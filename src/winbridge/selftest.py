from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

from pywinauto import Desktop
from pywinauto.keyboard import send_keys
import win32clipboard

from .controller import AutomationController


def wait_until(callable_, timeout: float, description: str):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = callable_()
            if value:
                return value
        except Exception as exc:
            last = exc
        time.sleep(0.25)
    suffix = f"; last error: {last}" if last else ""
    raise TimeoutError(f"Timed out waiting for {description}{suffix}")


def desktop_path() -> Path:
    # FOLDERID_Desktop through the known-folder API supports localized and moved desktops.
    folder_id = ctypes.c_byte * 16
    desktop_guid = folder_id(0x3A, 0xCC, 0xBF, 0xB4, 0x2C, 0xDB, 0x4C, 0x42, 0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41)
    path_ptr = ctypes.c_wchar_p()
    result = ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(desktop_guid), 0, None, ctypes.byref(path_ptr))
    if result != 0:
        raise OSError(result, "SHGetKnownFolderPath(FOLDERID_Desktop) failed")
    try:
        return Path(path_ptr.value)
    finally:
        ctypes.windll.ole32.CoTaskMemFree(path_ptr)


def clipboard_text() -> str | None:
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
            return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except Exception:
        return None
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
    return None


def set_clipboard_text(value: str | None) -> None:
    for _ in range(10):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            if value is not None:
                win32clipboard.SetClipboardText(value, win32clipboard.CF_UNICODETEXT)
            return
        except Exception:
            time.sleep(0.05)
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass


def read_weather_from_browser(controller: AutomationController, timeout: float) -> tuple[str, int]:
    before = {window.hwnd for window in controller.list_windows()}
    controller.open_uri("https://wttr.in/?format=3")

    def browser_candidates():
        windows = controller.list_windows()
        fresh = [item for item in windows if item.hwnd not in before]
        likely = [item for item in windows if any(token in item.class_name for token in ("Chrome_WidgetWin", "Mozilla", "ApplicationFrame"))]
        return fresh or likely

    candidates = wait_until(browser_candidates, timeout, "default browser window")
    browser = wait_until(
        lambda: next((item for item in controller.list_windows() if "wttr.in" in item.title.casefold()), None),
        timeout,
        "weather browser tab",
    )

    clipboard_backup = clipboard_text()

    def page_text():
        root = Desktop(backend="uia").window(handle=browser.hwnd).wrapper_object()
        chunks = []
        for element in root.descendants(depth=12):
            text = (element.window_text() or "").strip()
            if text and text not in chunks:
                chunks.append(text)
        joined = "\n".join(chunks)
        # wttr.in format=3 is normally: "Location: condition +18°C".
        weather_lines = [line for line in chunks if re.search(r"(?:°[CF]|[+-]\d+°)", line)]
        if weather_lines:
            return weather_lines[-1], joined

        # Chromium may hide page content from UIA unless renderer accessibility is
        # enabled. Copying the active plain-text page is the cross-browser fallback.
        controller.press_keys(browser.hwnd, "^a^c")
        time.sleep(0.15)
        copied = ""
        try:
            win32clipboard.OpenClipboard()
            copied = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except Exception:
            pass
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
        copied_lines = [line.strip() for line in copied.splitlines() if line.strip()]
        matches = [line for line in copied_lines if re.search(r"(?:°[CF]|[+-]\d+°)", line)]
        return (matches[-1] if matches else "", joined + "\n" + copied)

    weather, diagnostic = wait_until(lambda: (value if (value := page_text())[0] else None), timeout, "weather text")
    set_clipboard_text(clipboard_backup)
    return weather.strip(), browser.hwnd


def write_note(controller: AutomationController, weather: str, timeout: float) -> Path:
    before = {window.hwnd for window in controller.list_windows()}
    controller.launch("notepad.exe")
    note = wait_until(
        lambda: next((window for window in controller.list_windows() if window.hwnd not in before and window.class_name == "Notepad"), None),
        timeout,
        "new Notepad window",
    )
    body = f"Meteo rilevato il {datetime.now():%d/%m/%Y alle %H:%M}\r\n{weather}\r\n"
    note_spec = Desktop(backend="uia").window(handle=note.hwnd)
    editor = note_spec.child_window(control_type="Document").wrapper_object()
    editor.set_focus()
    clipboard_backup = clipboard_text()
    set_clipboard_text(body)
    send_keys("^a^v", pause=0.03)
    set_clipboard_text(clipboard_backup)
    dialogs_before = {window.hwnd for window in controller.list_windows() if window.class_name == "#32770"}
    send_keys("^s", pause=0.03)

    save_dialog = wait_until(
        lambda: next(
            (
                w
                for w in Desktop(backend="win32").windows()
                if w.handle not in dialogs_before and w.class_name() == "#32770" and w.is_visible()
            ),
            None,
        ),
        timeout,
        "Save As dialog",
    )
    output = desktop_path() / f"Meteo_WinBridge_{datetime.now():%Y%m%d_%H%M%S}.txt"
    save_spec = Desktop(backend="win32").window(handle=save_dialog.handle)
    filename = save_spec.child_window(class_name="Edit", control_id=1001).wrapper_object()
    filename.set_edit_text(str(output))
    save_button = save_spec.child_window(class_name="Button", control_id=1).wrapper_object()
    save_button.click_input()
    wait_until(output.exists, timeout, "saved weather note")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="WinBridge browser-to-Notepad end-to-end test")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    controller = AutomationController()
    weather, browser_hwnd = read_weather_from_browser(controller, args.timeout)
    output = write_note(controller, weather, args.timeout)
    result = {
        "ok": True,
        "weather": weather,
        "browser_hwnd": browser_hwnd,
        "output": str(output),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
    }
    print(json.dumps(result, ensure_ascii=True, indent=2) if args.json else f"PASS: {output}\n{weather}")


if __name__ == "__main__":
    main()
