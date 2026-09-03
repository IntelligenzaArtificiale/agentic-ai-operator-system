"""Small command-line gate for PowerShell launchers."""

from __future__ import annotations

import json

from client import LicenseClient


if __name__ == "__main__":
    result = LicenseClient().status()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["active"] else 3)
