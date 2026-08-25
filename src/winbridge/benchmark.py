from __future__ import annotations

import argparse
import json
import statistics
import time

from .controller import AutomationController


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Agentic AI Operator System discovery and inspection")
    parser.add_argument("--title", default="", help="substring of a visible window title")
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    controller = AutomationController()
    windows = controller.list_windows(args.title)
    if not windows:
        raise SystemExit("No matching visible windows")
    window = windows[0]
    rows = []
    for backend in ("win32", "uia", "auto"):
        samples = []
        last = None
        for _ in range(args.runs):
            started = time.perf_counter()
            last = controller.inspect(window.hwnd, backend=backend)
            samples.append((time.perf_counter() - started) * 1000)
        rows.append({
            "backend": backend,
            "elements": len(last["elements"]),
            "median_ms": round(statistics.median(samples), 2),
            "samples_ms": [round(sample, 2) for sample in samples],
        })
    print(json.dumps({"window": window.dict(), "results": rows}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

