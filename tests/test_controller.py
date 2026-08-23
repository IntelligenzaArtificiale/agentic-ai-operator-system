import pytest

from winbridge.controller import AutomationController, StaleReferenceError


def test_rejects_stale_window_handle():
    controller = AutomationController()
    with pytest.raises(StaleReferenceError):
        controller.inspect(0)


def test_lists_windows_with_required_identity_fields():
    windows = AutomationController().list_windows()
    assert windows
    assert all(item.hwnd > 0 and item.pid > 0 for item in windows)


def test_coordinate_bounds_are_checked_before_input():
    controller = AutomationController()
    window = controller.list_windows()[0]
    with pytest.raises(ValueError):
        controller.click(window.hwnd, -1, -1)


def test_windows_text_normalizes_newlines():
    assert AutomationController._windows_text("uno\ndue\rtre\r\nquattro") == "uno\r\ndue\r\ntre\r\nquattro"


@pytest.mark.parametrize("filename", ["", "..", "a/b", "a\\b", "*.txt"])
def test_desktop_note_rejects_unsafe_filename(filename):
    with pytest.raises(ValueError):
        AutomationController().create_desktop_note(filename, "test", open_in_notepad=False)


def test_inspect_rejects_unbounded_control_text():
    controller = AutomationController()
    window = controller.list_windows()[0]
    with pytest.raises(ValueError):
        controller.inspect(window.hwnd, max_name_chars=100_000)


def test_capture_returns_png_for_visible_window():
    controller = AutomationController()
    window = controller.list_windows()[0]
    data = controller.capture_window(window.hwnd)
    assert data.startswith(b"\x89PNG\r\n\x1a\n")


def test_click_and_capture_rejects_excessive_wait():
    controller = AutomationController()
    window = controller.list_windows()[0]
    with pytest.raises(ValueError):
        controller.click_and_capture(window.hwnd, 0, 0, settle_ms=5001)
