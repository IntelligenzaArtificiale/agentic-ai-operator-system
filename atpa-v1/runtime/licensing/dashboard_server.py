"""Loopback-only dashboard server with a license check on every request."""

from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dashboard_data import collect

try:
    from .client import LicenseClient
except ImportError:
    from client import LicenseClient


HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).resolve().parent.parent / "dashboard-live"
ASSETS = {"/": "index.html", **{f"/{name}": name for name in
          ("index.html", "styles.css", "tokens.css", "workspace.css", "dashboard.js", "view.js", "detail.js")}}


class LicensedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def respond(self, code, body, content_type="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self) -> None:
        self.serve()

    def do_GET(self) -> None:
        self.serve()

    def serve(self):
        # Reject foreign Host headers (including DNS rebinding) before reading data.
        allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if self.headers.get("Host") not in allowed:
            self.respond(403, b'{"error":"Host non consentito"}')
            return
        try:
            active = LicenseClient().status().get("active")
        except Exception:
            active = False
        if not active:
            self.respond(403, b'{"error":"Licenza non attiva. Apri Attiva Agentic AI Operator System dal Desktop."}')
            return
        route = urlsplit(self.path).path
        if route == "/api/data":
            try:
                settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8-sig"))
                payload = collect(Path(settings["procedure_root"]), settings.get("system"))
                self.respond(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            except (OSError, ValueError, KeyError, TypeError):
                self.respond(503, b'{"error":"Catalogo non leggibile. Esegui visualizza-procedure per rigenerare la configurazione."}')
            return
        name = ASSETS.get(route)
        target = ROOT / name if name else None
        if not target or not target.is_file() or target.is_symlink():
            self.respond(404, b'{"error":"Risorsa non disponibile"}')
            return
        self.path = "/" + name
        handle = super().send_head()
        if handle:
            try:
                if self.command != "HEAD":
                    self.copyfile(handle, self.wfile)
            finally:
                handle.close()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("X-AIOS-Dashboard", "1")
        super().end_headers()

    def log_message(self, _format: str, *args) -> None:
        return


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), LicensedHandler).serve_forever()
