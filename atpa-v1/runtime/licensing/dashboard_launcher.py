"""Desktop dashboard shortcut. Runs the existing lifecycle with no console window."""
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import messagebox

try:
    from .client import LicenseClient
    from .locking import mutex
except ImportError:
    from client import LicenseClient
    from locking import mutex


def launch():
    script = Path(__file__).resolve().parent.parent / "Update-Dashboard.ps1"
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script), "-Open"],
        creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, timeout=150,
    ).returncode


def main():
    with mutex("dashboard-launch", LicenseClient().state_dir) as acquired:
        if not acquired:
            return
        try:
            failed = launch() != 0
        except (OSError, subprocess.TimeoutExpired):
            failed = True
        if failed:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dashboard AIOS", "Dashboard non disponibile. Verifica la licenza con l’icona di attivazione. Se è attiva, usa Visualizza procedure nella chat per la diagnosi.")
            root.destroy()


if __name__ == "__main__":
    main()
