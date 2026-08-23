# WinBridge agent installation contract

When the user explicitly asks you to install this ZIP/package, perform the following
steps. The user's request to install is the authorization for these local changes.

1. Confirm the host is Windows x64 and the archive was supplied by the user.
2. Extract the complete archive to a temporary directory. Do not execute files
   directly inside the ZIP and do not upload any package content.
3. Read `INSTALL_FOR_CHATGPT.md` in full.
4. Run `Install-WinBridge.ps1 -NonInteractive` from the extracted package root.
5. Read the generated `INSTALL_RESULT.json` and require `ok: true`,
   `plugin_installed: true`, `mcp_configured: true`, and
   `persistent_background_service: false`.
6. Verify `%USERPROFILE%\plugins\winbridge\app\winbridge.exe` exists.
7. Tell the user that ChatGPT/Codex must be fully restarted to load the new MCP
   server. Do not attempt to automate or restart the ChatGPT desktop app UI.
8. After restart, create a new task. An already-open task retains its old native
   tool inventory and cannot acquire WinBridge retroactively.
9. In the new task, use `/mcp` to verify the global `winbridge` server and verify that
   `$windows-desktop-control` is available. For every Windows desktop action,
   use WinBridge. Do not use Chrome, Browser or Computer Use unless WinBridge
   reports an unsupported operation and the user then authorizes that fallback.
   For Desktop notes, use `create_desktop_note` once instead of typing into
   Notepad or operating its Save dialog.
10. If WinBridge tools are absent, stop. Never launch `winbridge.exe` manually through
    PowerShell or another shell as a substitute for the native MCP connection.

Never disable Windows security, bypass SmartScreen, request credentials, or alter
unrelated plugin or marketplace entries.
