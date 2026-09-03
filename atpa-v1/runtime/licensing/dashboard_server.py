"""Loopback-only dashboard server with a license check on every request."""

from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from client import LicenseClient


HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).resolve().parent.parent / "dashboard-live"


class LicensedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if not LicenseClient().status().get("active"):
            body = b"Agentic AI Operator System: licenza non attiva."
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'")
        super().end_headers()

    def log_message(self, _format: str, *args) -> None:
        return


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), LicensedHandler).serve_forever()
