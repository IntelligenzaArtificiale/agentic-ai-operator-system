from __future__ import annotations

import ctypes
import os
import subprocess
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any, Literal

from pywinauto import Desktop
from pywinauto.keyboard import send_keys
from pywinauto.controls.hwndwrapper import HwndWrapper
from mss import MSS
from mss.tools import to_png
from win32com.shell import shell, shellcon

from .models import ElementRef, WindowRef


user32 = ctypes.WinDLL("user32", use_last_error=True)
IsWindow = user32.IsWindow
IsWindow.argtypes = [wintypes.HWND]
IsWindow.restype = wintypes.BOOL
SetForegroundWindow = user32.SetForegroundWindow
SetForegroundWindow.argtypes = [wintypes.HWND]
SetForegroundWindow.restype = wintypes.BOOL

ULONG_PTR = wintypes.WPARAM
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
INPUT_KEYBOARD = 1


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = [("type", wintypes.DWORD), ("value", INPUT_UNION)]


SendInput = user32.SendInput
SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
SendInput.restype = wintypes.UINT


class StaleReferenceError(RuntimeError):
    pass


class AutomationController:
    """Hybrid Win32/UIA controller with explicit, validated targets."""

    def __init__(self) -> None:
        if ctypes.sizeof(ctypes.c_void_p) not in (4, 8):
            raise RuntimeError("Unsupported Windows architecture")

    @staticmethod
    def _validate_hwnd(hwnd: int) -> None:
        if not hwnd or not IsWindow(hwnd):
            raise StaleReferenceError(f"Window handle {hwnd!r} is no longer valid")

    def list_windows(self, title_contains: str = "", include_untitled: bool = False) -> list[WindowRef]:
        needle = title_contains.casefold().strip()
        found: list[WindowRef] = []
        for wrapper in Desktop(backend="win32").windows(visible_only=True):
            title = wrapper.window_text() or ""
            if not include_untitled and not title.strip():
                continue
            if needle and needle not in title.casefold():
                continue
            try:
                pid = wrapper.process_id()
                class_name = wrapper.class_name()
            except Exception:
                continue
            found.append(WindowRef(wrapper.handle, pid, title, class_name))
        return sorted(found, key=lambda w: (w.title.casefold(), w.hwnd))

    def launch(self, executable: str, arguments: list[str] | None = None) -> int:
        """Launch one executable without invoking cmd.exe or a shell."""
        candidate = executable.strip().strip('"')
        if not candidate or any(char in candidate for char in "\r\n\0"):
            raise ValueError("Invalid executable")
        if Path(candidate).suffix and Path(candidate).suffix.casefold() != ".exe":
            raise ValueError("Only Windows executable (.exe) targets are accepted")
        executable_path = Path(candidate)
        working_directory = str(executable_path.parent) if executable_path.is_absolute() else None
        process = subprocess.Popen([candidate, *(arguments or [])], shell=False, cwd=working_directory)
        return process.pid

    @staticmethod
    def shell_launch(target: str) -> None:
        """Activate an app through the Windows registered shell, as Start Menu does."""
        candidate = target.strip().strip('"')
        if not candidate or any(char in candidate for char in "\r\n\0"):
            raise ValueError("Invalid application target")
        os.startfile(candidate)  # type: ignore[attr-defined]

    @staticmethod
    def open_uri(uri: str) -> None:
        """Open an HTTP(S) URL with the user's registered default browser."""
        if not uri.casefold().startswith(("https://", "http://")):
            raise ValueError("Only HTTP(S) URIs are accepted")
        os.startfile(uri)  # type: ignore[attr-defined]

    def inspect(
        self,
        hwnd: int,
        backend: Literal["auto", "uia", "win32"] = "auto",
        max_depth: int = 8,
        max_elements: int = 500,
        max_name_chars: int = 500,
    ) -> dict[str, Any]:
        self._validate_hwnd(hwnd)
        if not 32 <= max_name_chars <= 4000:
            raise ValueError("max_name_chars must be between 32 and 4000")
        # Legacy Win32 enumeration is typically tens of milliseconds while UIA can
        # take a second on the same app. Probe Win32 first and only pay the UIA cost
        # when the classic tree is effectively empty/custom-drawn.
        backends = ("win32", "uia") if backend == "auto" else (backend,)
        attempts: list[dict[str, Any]] = []
        best: tuple[str, list[ElementRef]] | None = None
        for candidate in backends:
            started = time.perf_counter()
            try:
                root = Desktop(backend=candidate).window(handle=hwnd).wrapper_object()
                descendants = root.descendants(depth=max_depth)[:max_elements]
                elements = [self._element_ref(item, candidate, hwnd, i, max_name_chars) for i, item in enumerate(descendants)]
                elapsed = (time.perf_counter() - started) * 1000
                attempts.append({"backend": candidate, "count": len(elements), "elapsed_ms": round(elapsed, 2)})
                if best is None or len(elements) > len(best[1]):
                    best = (candidate, elements)
                if backend == "auto" and candidate == "win32" and len(elements) >= 3:
                    attempts[-1]["selected_fast_path"] = True
                    break
            except Exception as exc:
                attempts.append({"backend": candidate, "error": f"{type(exc).__name__}: {exc}"})
        if best is None:
            return {"backend": None, "elements": [], "attempts": attempts}
        return {"backend": best[0], "elements": [e.dict() for e in best[1]], "attempts": attempts}

    @staticmethod
    def _element_ref(item: Any, backend: str, hwnd: int, ordinal: int, max_name_chars: int = 500) -> ElementRef:
        info = item.element_info
        rect = item.rectangle()
        runtime = getattr(info, "runtime_id", None)
        runtime_id = ".".join(map(str, runtime)) if runtime else f"ordinal:{ordinal}"
        name = item.window_text() or ""
        if len(name) > max_name_chars:
            name = name[:max_name_chars] + f"… [truncated {len(name) - max_name_chars} chars]"
        return ElementRef(
            hwnd=hwnd,
            runtime_id=runtime_id,
            backend=backend,
            name=name,
            control_type=getattr(info, "control_type", "") or item.friendly_class_name(),
            automation_id=getattr(info, "automation_id", "") or "",
            left=rect.left,
            top=rect.top,
            right=rect.right,
            bottom=rect.bottom,
        )

    def focus(self, hwnd: int) -> None:
        self._validate_hwnd(hwnd)
        wrapper = HwndWrapper(hwnd)
        if wrapper.is_minimized():
            wrapper.restore()
        wrapper.set_focus()
        if not SetForegroundWindow(hwnd):
            # set_focus can succeed even when Windows declines the foreground hint.
            if user32.GetForegroundWindow() != hwnd:
                raise RuntimeError("Windows refused to foreground the target window")

    def click(self, hwnd: int, x: int, y: int, button: Literal["left", "right"] = "left") -> None:
        self._validate_hwnd(hwnd)
        wrapper = HwndWrapper(hwnd)
        rect = wrapper.rectangle()
        if not (0 <= x < rect.width() and 0 <= y < rect.height()):
            raise ValueError(f"Coordinates ({x}, {y}) are outside the target window")
        wrapper.click_input(button=button, coords=(x, y), absolute=False)

    def capture_window(self, hwnd: int) -> bytes:
        """Return the visible window pixels as PNG with window-relative origin (0, 0)."""
        self.focus(hwnd)
        rect = HwndWrapper(hwnd).rectangle()
        if rect.width() <= 0 or rect.height() <= 0:
            raise RuntimeError("The target window has no visible capture area")
        region = {
            "left": rect.left,
            "top": rect.top,
            "width": rect.width(),
            "height": rect.height(),
        }
        with MSS() as grabber:
            shot = grabber.grab(region)
            return to_png(shot.rgb, shot.size)

    def click_and_capture(
        self,
        hwnd: int,
        x: int,
        y: int,
        button: Literal["left", "right"] = "left",
        settle_ms: int = 500,
    ) -> bytes:
        """Perform one bounded click, wait for rendering, then capture the resulting state."""
        if not 0 <= settle_ms <= 5000:
            raise ValueError("settle_ms must be between 0 and 5000")
        self.click(hwnd, x, y, button)
        time.sleep(settle_ms / 1000)
        return self.capture_window(hwnd)

    def type_text(self, hwnd: int, text: str, interval_ms: int = 0) -> None:
        self.focus(hwnd)
        # KEYEVENTF_UNICODE sends literal UTF-16 input. Unlike type_keys, characters
        # such as ^, %, + and braces are never interpreted as shortcut syntax.
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        chunks = normalized.split("\n")
        for chunk_index, chunk in enumerate(chunks):
            raw = chunk.encode("utf-16-le", "surrogatepass")
            units = [int.from_bytes(raw[offset : offset + 2], "little") for offset in range(0, len(raw), 2)]
            for start in range(0, len(units), 64):
                batch = units[start : start + 64]
                events = (INPUT * (len(batch) * 2))()
                for index, unit in enumerate(batch):
                    events[index * 2] = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(0, unit, KEYEVENTF_UNICODE, 0, 0))
                    events[index * 2 + 1] = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(0, unit, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0))
                sent = SendInput(len(events), events, ctypes.sizeof(INPUT))
                if sent != len(events):
                    raise RuntimeError("Windows rejected Unicode input (possible UIPI integrity boundary)")
                time.sleep(max(interval_ms / 1000, 0.001))
            if chunk_index < len(chunks) - 1:
                send_keys("{ENTER}", pause=0)

    @staticmethod
    def _windows_text(text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")

    def create_desktop_note(self, filename: str, text: str, open_in_notepad: bool = True) -> dict[str, Any]:
        """Create a complete Desktop note atomically and optionally open it in Notepad."""
        clean = filename.strip()
        if not clean or clean in {".", ".."} or Path(clean).name != clean or any(c in clean for c in '<>:"/\\|?*'):
            raise ValueError("filename must be a plain Windows file name")
        if not clean.casefold().endswith(".txt"):
            clean += ".txt"
        desktop = Path(shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOPDIRECTORY, 0, 0))
        target = desktop / clean
        temporary = desktop / f".{clean}.{os.getpid()}.tmp"
        temporary.write_text(self._windows_text(text), encoding="utf-8-sig", newline="")
        os.replace(temporary, target)
        pid = None
        if open_in_notepad:
            pid = subprocess.Popen(["notepad.exe", str(target)], shell=False).pid
        return {"path": str(target), "bytes": target.stat().st_size, "pid": pid}

    def press_keys(self, hwnd: int, keys: str) -> None:
        """Send a pywinauto key chord such as ^s, ^l or {ENTER}."""
        self.focus(hwnd)
        if not keys or len(keys) > 100:
            raise ValueError("Invalid key sequence")
        send_keys(keys, pause=0.01)

    def set_control_value(
        self,
        hwnd: int,
        value: str,
        *,
        backend: Literal["uia", "win32"] = "uia",
        automation_id: str | None = None,
        title: str | None = None,
        control_type: str | None = None,
    ) -> None:
        self._validate_hwnd(hwnd)
        if not automation_id and not title:
            raise ValueError("automation_id or title is required")
        root = Desktop(backend=backend).window(handle=hwnd)
        target = root.child_window(
            auto_id=automation_id,
            title=title,
            control_type=control_type,
        ).wrapper_object()
        target.set_focus()
        if hasattr(target, "set_edit_text"):
            target.set_edit_text(value)
        else:
            target.type_keys("^a{BACKSPACE}" + value, with_spaces=True, set_foreground=False)
