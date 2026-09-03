"""Dedicated activation UI: the model never receives the license key."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from client import LicenseClient, LicenseError


class ActivationWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Attiva Agentic AI Operator System")
        self.geometry("540x320")
        self.resizable(False, False)
        self.client = LicenseClient()
        self.key = tk.StringVar()
        self.status_text = tk.StringVar()
        frame = ttk.Frame(self, padding=28)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Agentic AI Operator System", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Inserisci la chiave ricevuta. Non verrà mostrata a ChatGPT né salvata in chiaro.", wraplength=470).pack(anchor="w", pady=(8, 22))
        ttk.Entry(frame, textvariable=self.key, show="•", font=("Consolas", 12)).pack(fill="x")
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=16)
        ttk.Button(buttons, text="Attiva", command=self.activate).pack(side="left")
        ttk.Button(buttons, text="Verifica stato", command=self.refresh).pack(side="left", padx=8)
        ttk.Button(buttons, text="Disattiva dispositivo", command=self.deactivate).pack(side="right")
        ttk.Label(frame, textvariable=self.status_text, wraplength=470).pack(anchor="w", pady=10)
        self.refresh()

    def activate(self) -> None:
        value = self.key.get().strip()
        if not value:
            messagebox.showwarning("Chiave mancante", "Inserisci una chiave di licenza.")
            return
        try:
            result = self.client.activate(value)
            self.key.set("")
            self.status_text.set(f"Licenza attiva fino al {result['valid_until']}.")
            messagebox.showinfo("Attivazione completata", "Il sistema è ora attivo. Riavvia ChatGPT/Codex.")
        except (LicenseError, OSError) as error:
            self.status_text.set(str(error))

    def refresh(self) -> None:
        result = self.client.status()
        self.status_text.set(f"Licenza attiva fino al {result['valid_until']}." if result["active"] else result["message"])

    def deactivate(self) -> None:
        if not messagebox.askyesno("Conferma", "Disattivare questa licenza sul dispositivo?"):
            return
        try:
            self.client.deactivate()
            self.refresh()
        except (LicenseError, OSError) as error:
            self.status_text.set(str(error))


if __name__ == "__main__":
    ActivationWindow().mainloop()
