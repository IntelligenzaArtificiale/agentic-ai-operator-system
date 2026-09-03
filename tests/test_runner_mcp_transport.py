import asyncio
import json
from pathlib import Path

try:
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport
except ModuleNotFoundError:
    if __name__ == "__main__":
        raise
    import pytest
    pytest.skip("fastmcp is provided by the packaged Windows runtime", allow_module_level=True)


async def main():
    repo = Path(__file__).parents[1]
    server = repo / "atpa-v1" / "runtime" / "procedure-runner" / "server.py"
    procedure = repo / "atpa-v1" / "template" / "TEMPLATE-PROCEDURA"
    transport = StdioTransport(
        command=str(Path(__import__("sys").executable)),
        args=[str(server)],
        env={"AGENTIC_PROCEDURE_ROOT": str(procedure)},
    )
    async with Client(transport, timeout=60, init_timeout=60) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools}
        assert names == {"ValidatePlan", "ExecuteBlock", "PrepareRun", "ValidateRunCoverage", "LicenseStatus", "OpenLicenseActivation"}, names
        status = await client.call_tool("LicenseStatus", {})
        assert status.data["active"] is False
        result = await client.call_tool("ValidatePlan", {"plan_path": str(procedure / "execution-plan.json")}, raise_on_error=False)
        assert result.is_error
        assert "Attivazione richiesta" in result.content[0].text
    print("Procedure runner MCP transport test passed.")


if __name__ == "__main__":
    asyncio.run(main())
