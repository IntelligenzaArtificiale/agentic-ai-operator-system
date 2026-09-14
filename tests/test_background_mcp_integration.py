"""Run with the packaged Windows interpreter to exercise the actual adapter."""

from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "atpa-v1/runtime"))


def main():
    from background_processes import configure_background_processes
    from windows_mcp.powershell import PowerShellExecutor, utils
    from windows_mcp.tools import app

    configure_background_processes()
    configured = utils.subprocess
    configure_background_processes()
    assert utils.subprocess is configured
    assert app.subprocess is subprocess  # User application launches are not hidden.
    probe = ('Add-Type -Name ConsoleProbe -Namespace AIOS -MemberDefinition '
             "'[DllImport(\"kernel32.dll\")] public static extern IntPtr GetConsoleWindow();'; "
             '[AIOS.ConsoleProbe]::GetConsoleWindow().ToInt64()')
    for _ in range(5):
        output, code = PowerShellExecutor.execute_command(probe, timeout=10)
        assert code == 0 and output.strip() == "0", (output, code)
    try:
        utils.run_with_graceful_timeout(
            [sys.executable, "-c", "import time;time.sleep(20)"],
            timeout=0.2, grace_period=0.2, capture_output=True)
        raise AssertionError("Timeout was lost")
    except subprocess.TimeoutExpired:
        pass
    print("5 real MCP shells without console; timeout preserved; app launches unchanged.")


if __name__ == "__main__":
    main()
