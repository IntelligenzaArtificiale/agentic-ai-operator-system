---
name: windows-desktop-control
description: Control the local Windows desktop and applications using CursorTouch Windows-MCP. Use whenever the user asks to open, inspect, click, type in, configure, verify, or close a Windows application.
---

# Windows desktop control

Use the native `windows-mcp` MCP tools for the entire desktop workflow. Do not switch to Browser, Chrome, Computer Use, shell UI automation, or ad-hoc mouse scripts unless Windows-MCP returns a clear unsupported-operation error and the user authorizes a fallback.

## Mandatory visual loop

1. Call `Screenshot` first for fast visual context. Use `Snapshot` when element ids, UIA details, scrollable regions, or browser DOM are needed.
2. Launch or switch applications with `App`, then call `Wait` only for the shortest necessary render delay.
3. Prefer element labels/ids from `Snapshot`; otherwise use screenshot coordinates and account for any image downscaling ratio reported by the tool.
4. After every state-changing `Click`, `Type`, `Shortcut`, or multi-action, call `Screenshot` or `Snapshot` again.
5. Compare the visible post-action state with the requested state. A successful tool response alone is not proof of success.
6. Retry at most twice after obtaining fresh state. If verification remains ambiguous, report that honestly and leave the application open unless the user explicitly requested otherwise.
7. Close an application only after all requested settings have been visibly confirmed.

For speed, use `Screenshot` instead of the heavier `Snapshot` when pixels are sufficient, batch independent form edits with `MultiEdit`, and avoid repeated full UI-tree extraction.
