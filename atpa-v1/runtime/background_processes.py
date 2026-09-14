"""Hide only Windows MCP's internal shell/cleanup processes, not user apps."""

import os
import subprocess


def hidden_options(options):
    result = dict(options)
    if os.name == "nt":
        result["creationflags"] = result.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
        startup = result.get("startupinfo")
        startup = startup.copy() if startup is not None else subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        result["startupinfo"] = startup
    return result


class _BackgroundSubprocess:
    """Module-local proxy; never monkeypatch the shared subprocess module."""

    def __getattr__(self, name):
        return getattr(subprocess, name)

    def Popen(self, *args, **kwargs):
        return subprocess.Popen(*args, **hidden_options(kwargs))

    def run(self, *args, **kwargs):
        return subprocess.run(*args, **hidden_options(kwargs))


def configure_background_processes():
    # Compatibility adapter for pinned Windows MCP 0.8.5, including taskkill
    # in its timeout handler. App.launch_executable keeps normal visibility.
    from windows_mcp.powershell import utils

    if not isinstance(utils.subprocess, _BackgroundSubprocess):
        utils.subprocess = _BackgroundSubprocess()
