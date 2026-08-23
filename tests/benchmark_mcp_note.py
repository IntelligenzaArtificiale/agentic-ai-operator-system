from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(executable: str) -> None:
    params = StdioServerParameters(command=executable, args=[])
    sample = "Meteo di prova: 24 °C — sereno\nPrima riga con accenti: città, perché\nTerza riga: nessun duplicato ✓"
    started = time.perf_counter()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            health = await session.call_tool("health_check", {})
            result = await session.call_tool(
                "create_desktop_note",
                {"filename": "WinBridge-0.6.0-MCP-Test.txt", "text": sample, "open_in_notepad": False},
            )
    elapsed = time.perf_counter() - started
    if result.isError:
        raise RuntimeError(result.content)
    payload = result.structuredContent or json.loads(result.content[0].text)
    payload = payload.get("result", payload)
    target = Path(payload["path"])
    actual = target.read_text(encoding="utf-8-sig")
    if actual.replace("\r\n", "\n") != sample:
        raise AssertionError("The MCP-created note does not match the requested text")
    target.unlink()
    print(json.dumps({"ok": not health.isError, "elapsed_seconds": round(elapsed, 3), "tool_count": len(tools.tools), "path": str(target)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("executable")
    asyncio.run(run(parser.parse_args().executable))
