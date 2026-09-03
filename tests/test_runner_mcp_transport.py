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
        assert names == {"ValidatePlan", "ExecuteBlock", "PrepareRun", "ValidateRunCoverage"}, names
        result = await client.call_tool("ValidatePlan", {"plan_path": str(procedure / "execution-plan.json")})
        payload = json.loads(result.content[0].text)
        assert payload["valid"] is True
        assert payload["status"] == "exploratory"
        result = await client.call_tool("PrepareRun", {"procedure_path": str(procedure)})
        payload = json.loads(result.content[0].text)
        assert payload["coverage_contract"]["required_step_ids"] == ["work", "verify"]
    print("Procedure runner MCP transport test passed.")


if __name__ == "__main__":
    asyncio.run(main())
