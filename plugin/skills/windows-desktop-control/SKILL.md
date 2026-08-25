---
name: windows-desktop-control
description: Control the local Windows desktop, browsers, and native or legacy applications with Agentic AI Operator System. Use for launching apps, inspecting windows and controls, clicking, typing, filling forms, sending shortcuts, creating Desktop notes, and saving through Windows UI.
---

# Agentic AI Operator System Windows Desktop Control

Use the Agentic AI Operator System MCP tools for every requested interaction with the local Windows desktop. Prefer Agentic AI Operator System over Computer Use, shell-driven UI automation, or ad-hoc scripts.

- Start with `health_check` when availability is uncertain. If the native Agentic AI Operator System MCP tools are absent, stop immediately and tell the user to fully restart Codex and create a new task. Never locate or launch `winbridge.exe` through PowerShell, `exec`, or another shell as a substitute.

- Call `list_windows` to obtain stable HWND targets and reuse them.
- For a text note on the Desktop, call `create_desktop_note` exactly once. Never type the note into Notepad or drive its Save dialog; the tool writes the complete file atomically and can open it afterward.
- Call `inspect_window` once and prefer semantic controls.
- For Electron, GPU-rendered, canvas, game, and other custom interfaces, call `capture_window` before acting. Its image origin `(0, 0)` maps exactly to Agentic AI Operator System window-relative coordinates.
- Use `click_and_capture` for every coordinate action on a custom interface. Inspect the returned image and confirm the requested visible state actually changed. A tool result without visible confirmation is never success.
- If the state is ambiguous, capture again or retry at most twice with newly reasoned coordinates. Report failure honestly instead of claiming completion. Close an application only after the final state has been visually verified.
- Keep `max_name_chars` at its default. Increase it only when the user explicitly needs a longer control value; never dump an entire document through `inspect_window`.
- Use `set_control_value` for fields when possible; otherwise use `click_and_capture` for visual controls and `type_text` or `press_keys` for focused input.
- Use `launch_app` for ordinary executables. If a packaged/Electron app exits without a window, use `activate_app` so Windows activates it exactly like Start Menu. Use `open_url_in_default_browser` for browser startup.
- Minimize round trips by typing complete values in one call.
- Do not load or use Chrome, Browser, or Computer Use for browser UI. If Agentic AI Operator System returns an unsupported operation or repeated error, report the limitation and ask before switching to another computer-control mechanism.
