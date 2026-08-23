from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    executable = Path.home() / ".local" / "bin" / "windows-mcp.exe"
    parameters = StdioServerParameters(command=str(executable), args=["serve"])
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            required = {"Screenshot", "Snapshot", "Click", "Type", "App"}
            missing = sorted(required.difference(names))
            if missing:
                raise RuntimeError(f"Missing tools: {missing}")
            print(f"OK tools={len(names)} names={','.join(names)}")


if __name__ == "__main__":
    asyncio.run(main())
