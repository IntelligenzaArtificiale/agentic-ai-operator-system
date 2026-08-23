from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP, Image

from . import __version__
from .controller import AutomationController


SERVER_INSTRUCTIONS = (
    "For every task that operates the local Windows desktop or a native Windows "
    "application, use WinBridge first and keep using it for the whole workflow. "
    "Prefer semantic UIA/Win32 inspection and set_control_value. For custom-rendered "
    "interfaces, call capture_window, reason from its pixels, then use "
    "click_and_capture and visually inspect the returned image. A successful click "
    "is not proof that the requested state changed. Do not switch to Computer Use or "
    "shell-driven UI automation unless WinBridge returns an explicit unsupported "
    "operation or repeated error. Minimize round trips: inspect once, reuse HWNDs, "
    "and type complete text in one call. For desktop notes, always use "
    "create_desktop_note instead of typing into Notepad or using Save dialogs. "
    "Never start winbridge.exe manually through a shell. If native WinBridge tools "
    "are absent, stop immediately and tell the user to restart Codex and open a new "
    "task. Do not switch to Chrome, Browser, or Computer Use unless the user explicitly "
    "authorizes it after WinBridge reports an unsupported operation."
)

mcp = FastMCP("winbridge", instructions=SERVER_INSTRUCTIONS)
controller = AutomationController()


@mcp.tool()
def health_check() -> dict:
    """Return immediately when the native WinBridge MCP connection is healthy."""
    return {"ok": True, "version": __version__}


@mcp.tool()
def launch_app(executable: str, arguments: list[str] | None = None) -> dict:
    """Launch a Windows executable directly, never through a shell."""
    return {"pid": controller.launch(executable, arguments)}


@mcp.tool()
def activate_app(target: str) -> str:
    """Activate an executable, document, shortcut, or shell AppsFolder ID through Windows ShellExecute."""
    controller.shell_launch(target)
    return "ok"


@mcp.tool()
def open_url_in_default_browser(url: str) -> str:
    """Open an HTTP(S) URL in the Windows default browser."""
    controller.open_uri(url)
    return "ok"


@mcp.tool()
def list_windows(title_contains: str = "", include_untitled: bool = False) -> list[dict]:
    """List visible app windows; omit untitled system surfaces by default."""
    return [window.dict() for window in controller.list_windows(title_contains, include_untitled)]


@mcp.tool()
def create_desktop_note(filename: str, text: str, open_in_notepad: bool = True) -> dict:
    """Atomically create a UTF-8 text note on the real Windows Desktop, optionally opening it."""
    return controller.create_desktop_note(filename, text, open_in_notepad)


@mcp.tool()
def inspect_window(
    hwnd: int,
    backend: Literal["auto", "uia", "win32"] = "auto",
    max_depth: int = 8,
    max_elements: int = 500,
    max_name_chars: int = 500,
) -> dict:
    """Inspect a window while truncating large control text to keep responses fast."""
    return controller.inspect(hwnd, backend, max_depth, max_elements, max_name_chars)


@mcp.tool()
def focus_window(hwnd: int) -> str:
    """Restore and focus one validated window."""
    controller.focus(hwnd)
    return "ok"


@mcp.tool()
def click_window(hwnd: int, x: int, y: int, button: Literal["left", "right"] = "left") -> str:
    """Click window-relative coordinates after validating target and bounds."""
    controller.click(hwnd, x, y, button)
    return "ok"


@mcp.tool()
def capture_window(hwnd: int) -> Image:
    """Capture the visible window as PNG. Image pixels map 1:1 to click_window coordinates."""
    return Image(data=controller.capture_window(hwnd), format="png")


@mcp.tool()
def click_and_capture(
    hwnd: int,
    x: int,
    y: int,
    button: Literal["left", "right"] = "left",
    settle_ms: int = 500,
) -> Image:
    """Click window-relative pixels and return the rendered result for mandatory visual verification."""
    return Image(data=controller.click_and_capture(hwnd, x, y, button, settle_ms), format="png")


@mcp.tool()
def type_text(hwnd: int, text: str, interval_ms: int = 0) -> str:
    """Focus a validated window and type literal text into the current control."""
    controller.type_text(hwnd, text, interval_ms)
    return "ok"


@mcp.tool()
def press_keys(hwnd: int, keys: str) -> str:
    """Send a key chord to a validated window (^s, ^l, {ENTER}, etc.)."""
    controller.press_keys(hwnd, keys)
    return "ok"


@mcp.tool()
def set_control_value(
    hwnd: int,
    value: str,
    backend: Literal["uia", "win32"] = "uia",
    automation_id: str | None = None,
    title: str | None = None,
    control_type: str | None = None,
) -> str:
    """Set a field directly using a semantic UIA or Win32 selector."""
    controller.set_control_value(
        hwnd,
        value,
        backend=backend,
        automation_id=automation_id,
        title=title,
        control_type=control_type,
    )
    return "ok"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
