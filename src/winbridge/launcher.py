from __future__ import annotations

import sys


def main() -> None:
    if "--configure-mcp" in sys.argv:
        from winbridge.configure import configure_mcp, print_json

        def option(name: str) -> str | None:
            try:
                return sys.argv[sys.argv.index(name) + 1]
            except (ValueError, IndexError):
                return None

        executable = option("--executable") or sys.executable
        print_json(configure_mcp(executable, option("--codex-home")))
    elif "--diagnose" in sys.argv:
        from winbridge.configure import diagnose, print_json

        try:
            home = sys.argv[sys.argv.index("--codex-home") + 1]
        except (ValueError, IndexError):
            home = None
        print_json(diagnose(home))
    elif "--selftest" in sys.argv:
        from winbridge.selftest import main as selftest_main

        sys.argv.remove("--selftest")
        selftest_main()
    else:
        from winbridge.server import main as server_main

        server_main()


if __name__ == "__main__":
    main()
