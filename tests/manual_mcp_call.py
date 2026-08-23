from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(tool: str, arguments: dict, image_path: Path | None) -> None:
    parameters = StdioServerParameters(command=sys.executable, args=["-m", "winbridge.server"])
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            summary: list[dict] = []
            for item in result.content:
                if item.type == "image":
                    if image_path is None:
                        raise RuntimeError("Image response requires --image")
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    image_path.write_bytes(base64.b64decode(item.data))
                    summary.append({"type": "image", "path": str(image_path), "mimeType": item.mimeType})
                else:
                    summary.append(item.model_dump())
            print(json.dumps({"isError": result.isError, "content": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool")
    parser.add_argument("arguments", nargs="?", default="{}")
    parser.add_argument("--image", type=Path)
    options = parser.parse_args()
    asyncio.run(run(options.tool, json.loads(options.arguments), options.image))
