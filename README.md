# Agentic AI Operator System

Agentic AI Operator System is a local Windows platform for desktop automation,
process recording and reusable agentic procedures. The current installable
package uses **Windows MCP 0.8.5**, the licensed procedure runner and OpenSteps.
The older `src/winbridge` engine remains in this repository for development and
compatibility; it is not the engine installed by the current package.
That legacy engine uses a layered strategy:

1. Win32 controls for older MFC, VB6, VCL and classic WinForms applications. The
   automatic mode probes this first and keeps the fast path when it finds a useful
   tree.
2. Microsoft UI Automation for WPF, WinUI, Store, Qt and modern WinForms apps.
3. Native keyboard and mouse input as a compatibility fallback.
4. Vision/OCR fallback (planned) for owner-drawn canvases and remote desktops.

The legacy WinBridge server never accepts arbitrary shell commands. It returns stable window and
element references, checks that references are fresh, and requires the caller to
target a specific window before input is injected.

## Development

For the complete source archive, project map, backend setup and migration to
another PC, see [Development handoff](docs/DEVELOPMENT-HANDOFF.md).

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

Build the current package with `Build-SystemRelease.ps1 -Version 2.6.0`. On another Windows PC:

1. Extract `Agentic-AI-Operator-System-2.6.0-Windows-x64.zip`.
2. Double-click `INSTALLA.cmd` (administrator rights are not required).
3. Open `Attiva Agentic AI Operator System` on the Desktop yourself; the installer does not open activation windows.
4. Enter the key there, wait for `Licenza attiva`, close the window and confirm completion in chat. Never paste the key in chat.
5. After the status is verified, restart ChatGPT/Codex and open a new task.
6. Verify the `windows-mcp` and `procedure-runner` servers; use the bundled OpenSteps recorder from its Desktop shortcut.

An AI agent can install the archive autonomously after the user supplies its path
and explicitly requests installation. The archive-root `AGENTS.md` and
`GUIDA-UTENTE.md` define the non-interactive procedure. The installer backs
up the personal marketplace, installs `automazione-totale-procedure@personal`,
and registers the license-gated `windows-mcp` and `procedure-runner` entry points.
Installation success and license activation are separate checks.

Updates are discovered through `release-manifest.json`; downloads are accepted
only after their SHA-256 has been verified.

Version 2.6.0 gates Windows MCP tools, the deterministic procedure runner,
OpenSteps and the local dashboard behind a signed, device-bound license lease.
License keys are never requested in chat or stored locally in plaintext.

See [2.6.0 release notes](docs/releases/2.6.0.md) and the
[measured Windows MCP / Computer Use comparison](docs/benchmarks/2026-09-14-verdetto.md).

This system targets supported Windows 10 and Windows 11 releases. A universal
"100% of every application" guarantee is not technically possible: secure desktop,
UIPI integrity boundaries, DRM/protected surfaces, anti-cheat software and custom
renderers deliberately restrict inspection or input. Agentic AI Operator System reports these cases
instead of silently pretending an action succeeded.
