"""License-gated launcher for local UI applications and scripts."""

from __future__ import annotations

import subprocess
import sys

from client import LicenseClient, LicenseError


def main() -> int:
    try:
        LicenseClient().require()
    except LicenseError as error:
        subprocess.Popen([sys.executable, __file__.replace("launcher.py", "activation_ui.py")])
        ctypes_message(str(error))
        return 3
    if len(sys.argv) < 2:
        return 2
    subprocess.Popen(sys.argv[1:])
    return 0


def ctypes_message(message: str) -> None:
    import ctypes
    ctypes.windll.user32.MessageBoxW(None, message, "Licenza richiesta", 0x30)


if __name__ == "__main__":
    raise SystemExit(main())
