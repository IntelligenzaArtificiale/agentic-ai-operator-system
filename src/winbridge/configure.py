from __future__ import annotations

import json
import os
import platform
import re
import shutil
from datetime import datetime
from pathlib import Path

from . import __version__
from .controller import AutomationController


def codex_home(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".codex"


def configure_mcp(executable: str, explicit_codex_home: str | None = None) -> dict:
    exe = Path(executable).resolve()
    if not exe.is_file() or exe.suffix.casefold() != ".exe":
        raise FileNotFoundError(f"Agentic AI Operator System executable not found: {exe}")
    home = codex_home(explicit_codex_home)
    home.mkdir(parents=True, exist_ok=True)
    config = home / "config.toml"
    original = config.read_text(encoding="utf-8") if config.exists() else ""
    backup = None
    if config.exists():
        backup = home / f"config.toml.winbridge-backup-{datetime.now():%Y%m%d%H%M%S}"
        shutil.copy2(config, backup)

    # Replace only Agentic AI Operator System's own table. Other MCP servers and Codex settings are
    # preserved byte-for-byte.
    pattern = re.compile(r"(?ms)^\[mcp_servers\.winbridge\][^\[]*(?=^\[|\Z)")
    cleaned = pattern.sub("", original).rstrip()
    escaped = str(exe).replace("\\", "\\\\").replace('"', '\\"')
    block = (
        "[mcp_servers.winbridge]\n"
        f'command = "{escaped}"\n'
        "enabled = true\n"
        "required = true\n"
        "startup_timeout_sec = 15\n"
        "tool_timeout_sec = 120\n"
        'default_tools_approval_mode = "approve"\n'
    )
    updated = f"{cleaned}\n\n{block}" if cleaned else block
    temporary = home / "config.toml.winbridge-new"
    temporary.write_text(updated, encoding="utf-8", newline="\n")
    os.replace(temporary, config)
    return {
        "ok": True,
        "config": str(config),
        "backup": str(backup) if backup else None,
        "command": str(exe),
        "restart_required": True,
    }


def diagnose(explicit_codex_home: str | None = None) -> dict:
    home = codex_home(explicit_codex_home)
    config = home / "config.toml"
    text = config.read_text(encoding="utf-8") if config.exists() else ""
    windows = AutomationController().list_windows()
    return {
        "ok": os.name == "nt" and bool(windows),
        "version": __version__,
        "windows": platform.platform(),
        "architecture": platform.machine(),
        "visible_windows": len(windows),
        "codex_home": str(home),
        "config_exists": config.exists(),
        "mcp_configured": "[mcp_servers.winbridge]" in text,
        "persistent_background_service": False,
    }


def print_json(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=True, indent=2))
