"""Single-instance, non-blocking activation window; keys never enter chat."""

from __future__ import annotations

from queue import Empty, Queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from .client import LicenseClient, LicenseError
    from .locking import mutex
except ImportError:
    from client import LicenseClient, LicenseError
    from locking import mutex


def status_message(result: dict) -> str:
    if result.get("active") is True:
        return ("Licenza attiva su questo dispositivo. Verifica locale completata.\n"
                "Puoi chiudere questa finestra e comunicarlo in chat. "
                "Dopo la prima installazione riavvia ChatGPT/Codex.")
    return result.get("message") or "Licenza non attiva. Premi Verifica stato prima di riprovare."


def perform(client, operation: str, key: str = "") -> dict:
    """No Tk calls on the worker. Never infer success from server acceptance alone."""
    try:
        if operation == "activate":
            return client.activate(key)
        if operation == "deactivate":
            client.deactivate()
        return client.status()
    except LicenseError as error:
        return {"active": False, "message": str(error)}
    except Exception:
        return {"active": False, "message": (
            "Operazione non confermata. Controlla la connessione e premi Verifica stato: "
            "la richiesta potrebbe essere già stata ricevuta. Non riavviare l'installazione.")}


class ActivationWindow(tk.Tk):
    def __init__(self, client=None) -> None:
        super().__init__()
        self.title("Attiva Agentic AI Operator System")
        self.geometry("600x390")
        self.resizable(False, False)
        self.client = client or LicenseClient()
        self.busy = False
        self.results = Queue()
        self.key = tk.StringVar()
        self.status_text = tk.StringVar()
        frame = ttk.Frame(self, padding=28)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Agentic AI Operator System", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Inserisci qui la chiave ricevuta. Non incollarla in chat.\n"
                  "Attendi la conferma in questa finestra prima di chiuderla.", wraplength=540).pack(anchor="w", pady=(8, 20))
        self.entry = ttk.Entry(frame, textvariable=self.key, show="•", font=("Consolas", 12))
        self.entry.pack(fill="x")
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=16)
        self.controls = [self.entry]
        for label, callback in (("Attiva", self.activate), ("Verifica stato", self.refresh),
                                ("Disattiva dispositivo", self.deactivate)):
            button = ttk.Button(row, text=label, command=callback)
            button.pack(side="left", padx=(0, 8))
            self.controls.append(button)
        ttk.Label(frame, textvariable=self.status_text, wraplength=540).pack(anchor="w", pady=10)
        self.close_button = ttk.Button(frame, text="Chiudi", command=self.close)
        self.close_button.pack(side="bottom", anchor="e")
        self.controls.append(self.close_button)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()

    def _start(self, operation, key="") -> None:
        if self.busy:
            return
        self.busy = True
        self.status_text.set("Verifica in corso… Attendi, senza aprire altre finestre.")
        for widget in self.controls:
            widget.configure(state="disabled")

        def worker():
            self.results.put(perform(self.client, operation, key))

        threading.Thread(target=worker, daemon=True).start()
        self.after(100, self._poll)

    def _poll(self) -> None:
        try:
            result = self.results.get_nowait()
        except Empty:
            self.after(100, self._poll)
            return
        self.busy = False
        for widget in self.controls:
            widget.configure(state="normal")
        if result.get("active") is True:
            self.key.set("")
        self.status_text.set(status_message(result))

    def activate(self) -> None:
        if self.busy:
            return
        value = self.key.get().strip()
        if not value:
            self.status_text.set("Inserisci una chiave di licenza.")
            return
        self._start("activate", value)

    def refresh(self) -> None:
        self._start("status")

    def deactivate(self) -> None:
        if not self.busy and messagebox.askyesno("Conferma", "Disattivare questa licenza sul dispositivo?"):
            self._start("deactivate")

    def close(self) -> None:
        if not self.busy:
            self.destroy()


def main() -> int:
    client = LicenseClient()
    with mutex("activation-ui", client.state_dir) as acquired:
        if acquired:
            ActivationWindow(client).mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
