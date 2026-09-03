"""Licensed entrypoint around the pinned Windows MCP implementation."""

from windows_mcp.__main__ import _build_mcp

from licensing.middleware import LicenseMiddleware, register_license_tools


server = _build_mcp()
register_license_tools(server)
server.add_middleware(LicenseMiddleware())

if __name__ == "__main__":
    server.run()
