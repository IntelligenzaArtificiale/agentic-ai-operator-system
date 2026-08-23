from __future__ import annotations

import argparse
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def inspect(executable: str) -> None:
    parameters = StdioServerParameters(command=executable, args=[])
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            initialization = await session.initialize()
            print(f"instructions={initialization.instructions}")
            tools = await session.list_tools()
            print(f"tool_count={len(tools.tools)}")
            print("\n".join(tool.name for tool in tools.tools))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("executable")
    args = parser.parse_args()
    asyncio.run(inspect(args.executable))
