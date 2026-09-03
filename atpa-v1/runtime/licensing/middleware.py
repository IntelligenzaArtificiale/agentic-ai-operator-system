"""Reusable FastMCP license gate."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from .client import LicenseClient, LicenseError


ALLOWED_TOOLS = {"LicenseStatus", "OpenLicenseActivation"}


class LicenseMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next) -> Any:
        name = getattr(context.message, "name", "")
        if name not in ALLOWED_TOOLS:
            try:
                LicenseClient().require()
            except LicenseError as error:
                raise ToolError(str(error)) from error
        return await call_next(context)


def register_license_tools(mcp) -> None:
    @mcp.tool(name="LicenseStatus", description="Returns license status without exposing keys or tokens.")
    def license_status() -> dict:
        return LicenseClient().status()

    @mcp.tool(name="OpenLicenseActivation", description="Opens the dedicated local license window. No key is sent to chat.")
    def open_license_activation() -> str:
        script = Path(__file__).with_name("activation_ui.py")
        subprocess.Popen([sys.executable, str(script)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return "Finestra di attivazione aperta sul computer."
