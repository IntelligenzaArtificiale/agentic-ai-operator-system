from __future__ import annotations

import asyncio
import base64
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    output = Path("artifacts/nvidia-initial.png")
    parameters = StdioServerParameters(command=sys.executable, args=["-m", "winbridge.server"])
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            launch = await session.call_tool(
                "activate_app",
                {"target": r"C:\Program Files\NVIDIA Corporation\NVIDIA Broadcast\NVIDIA Broadcast.exe"},
            )
            print(launch.content)
            await asyncio.sleep(6)
            result = await session.call_tool("list_windows", {"title_contains": "Broadcast", "include_untitled": True})
            windows = json.loads(result.content[0].text)
            print(json.dumps(windows, ensure_ascii=False, indent=2))
            if not windows:
                raise RuntimeError("NVIDIA Broadcast did not create a visible window")
            capture = await session.call_tool("capture_window", {"hwnd": windows[0]["hwnd"]})
            image = next(item for item in capture.content if item.type == "image")
            output.parent.mkdir(exist_ok=True)
            output.write_bytes(base64.b64decode(image.data))
            print(output.resolve())


if __name__ == "__main__":
    asyncio.run(main())
