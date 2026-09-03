from __future__ import annotations

import asyncio
from pathlib import Path
import sys

try:
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport
except ModuleNotFoundError:
    if __name__ == "__main__":
        raise
    import pytest
    pytest.skip("fastmcp is provided by the packaged Windows runtime", allow_module_level=True)


async def main() -> None:
    repo = Path(__file__).parents[1]
    server = repo / "atpa-v1" / "runtime" / "licensed-windows-mcp.py"
    transport = StdioTransport(command=sys.executable, args=[str(server)])
    async with Client(transport, timeout=60, init_timeout=60) as client:
        names = {tool.name for tool in await client.list_tools()}
        assert {"Screenshot", "Click", "Type", "LicenseStatus", "OpenLicenseActivation"} <= names
        status = await client.call_tool("LicenseStatus", {})
        assert status.data["active"] is False
        result = await client.call_tool("Screenshot", {}, raise_on_error=False)
        assert result.is_error
        assert "Attivazione richiesta" in result.content[0].text
    print("Licensed Windows MCP transport test passed.")


if __name__ == "__main__":
    asyncio.run(main())
