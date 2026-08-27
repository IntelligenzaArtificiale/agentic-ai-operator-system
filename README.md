# Agentic AI Operator System

Agentic AI Operator System is a local Windows platform for desktop automation,
process recording and reusable agentic procedures. Its automation engine retains
the internal `winbridge` identifier for compatibility.
It uses a layered strategy instead of assuming that every application exposes the
same accessibility model:

1. Win32 controls for older MFC, VB6, VCL and classic WinForms applications. The
   automatic mode probes this first and keeps the fast path when it finds a useful
   tree.
2. Microsoft UI Automation for WPF, WinUI, Store, Qt and modern WinForms apps.
3. Native keyboard and mouse input as a compatibility fallback.
4. Vision/OCR fallback (planned) for owner-drawn canvases and remote desktops.

The server never accepts arbitrary shell commands. It returns stable window and
element references, checks that references are fresh, and requires the caller to
target a specific window before input is injected.

## Development

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\pytest
.venv\Scripts\winbridge-benchmark
```

Run the MCP server over stdio:

```powershell
.venv\Scripts\winbridge
```

## Installable Windows package

Build the portable package with `build_release.ps1`. On another Windows PC:

1. Extract `Agentic-AI-Operator-System-2.3.0-Windows-x64.zip`.
2. Double-click `INSTALLA.cmd` (administrator rights are not required).
3. Restart the ChatGPT desktop app or Codex.
4. Type `/mcp` to verify that the global Windows automation server is connected.
5. Open the bundled OpenSteps recorder from the Desktop shortcut.

An AI agent can install the archive autonomously after the user supplies its path
and explicitly requests installation. The archive-root `AGENTS.md` and
`INSTALL_FOR_CHATGPT.md` define the non-interactive procedure. The installer backs
up the personal marketplace, installs `winbridge@personal`, and registers its
bundled executable as the global `winbridge` MCP server. `DISINSTALLA.cmd` removes the per-user
installation.

Updates are discovered through `release-manifest.json`; downloads are accepted
only after their SHA-256 has been verified.

This system targets supported Windows 10 and Windows 11 releases. A universal
"100% of every application" guarantee is not technically possible: secure desktop,
UIPI integrity boundaries, DRM/protected surfaces, anti-cheat software and custom
renderers deliberately restrict inspection or input. Agentic AI Operator System reports these cases
instead of silently pretending an action succeeded.
