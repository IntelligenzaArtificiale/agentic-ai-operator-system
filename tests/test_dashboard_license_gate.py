from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request


def test_dashboard_denies_without_license():
    server = Path(__file__).parents[1] / "atpa-v1" / "runtime" / "licensing" / "dashboard_server.py"
    process = subprocess.Popen([sys.executable, str(server)])
    try:
        time.sleep(0.7)
        try:
            urllib.request.urlopen("http://127.0.0.1:8765/", timeout=5)
            raise AssertionError("dashboard accepted an unlicensed request")
        except urllib.error.HTTPError as error:
            assert error.code == 403
    finally:
        process.terminate()
        process.wait(timeout=5)
