import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

from background_processes import _BackgroundSubprocess, hidden_options


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows process flags")
ROOT = Path(__file__).parents[1]


def test_hidden_options_preserve_flags_and_do_not_mutate_startupinfo():
    startup = subprocess.STARTUPINFO()
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP, "startupinfo": startup}
    result = hidden_options(options)
    assert result["creationflags"] & subprocess.CREATE_NO_WINDOW
    assert result["creationflags"] & subprocess.CREATE_NEW_PROCESS_GROUP
    assert result["startupinfo"].dwFlags & subprocess.STARTF_USESHOWWINDOW
    assert startup.dwFlags == 0


def test_proxy_is_scoped_and_preserves_errors(monkeypatch):
    original = Mock(return_value="result")
    monkeypatch.setattr(subprocess, "run", original)
    proxy = _BackgroundSubprocess()
    assert proxy.run(["example.exe"], check=True) == "result"
    assert subprocess.run is original
    assert original.call_args.kwargs["creationflags"] & subprocess.CREATE_NO_WINDOW
    assert original.call_args.kwargs["check"] is True
    assert proxy.TimeoutExpired is subprocess.TimeoutExpired


def test_real_internal_child_has_no_console():
    result = _BackgroundSubprocess().run(
        [sys.executable, "-c", "import ctypes; print(ctypes.windll.kernel32.GetConsoleWindow())"],
        capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout.strip() == "0"


def ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def run_helper(code, arguments=(), timeout=30):
    script = ROOT / "atpa-v1/runtime/Invoke-BackgroundCommand.ps1"
    args = ",".join(ps_quote(a) for a in ("-c", code, *arguments))
    command = (f". {ps_quote(script)}; Invoke-AiosBackgroundCommand "
               f"-FilePath {ps_quote(sys.executable)} -Arguments @({args}) "
               f"-TimeoutSeconds {timeout} | ConvertTo-Json -Compress")
    return subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                          capture_output=True, text=True, timeout=15,
                          creationflags=subprocess.CREATE_NO_WINDOW)


def test_powershell_helper_hides_console_and_roundtrips_arguments():
    args = ('path with spaces', 'a"b', 'C:\\trailing\\', '', 'apostrophe\'s')
    result = run_helper("import ctypes,json,sys; print(json.dumps([ctypes.windll.kernel32.GetConsoleWindow(),sys.argv[1:]]))", args)
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["ExitCode"] == 0
    assert json.loads(output["Output"]) == [0, list(args)]


def test_powershell_helper_preserves_exit_code_and_stderr():
    result = run_helper("import sys;print('failure',file=sys.stderr);sys.exit(7)")
    output = json.loads(result.stdout)
    assert output["ExitCode"] == 7
    assert "failure" in output["Error"]


def test_powershell_helper_timeout():
    result = run_helper("import time;time.sleep(10)", timeout=1)
    assert result.returncode != 0
    assert "Timeout" in result.stderr
