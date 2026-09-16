"""Real HTTP checks on an isolated random port; no production licensing state."""
import json
from pathlib import Path
import threading
import urllib.error
import urllib.request

import pytest

from licensing import dashboard_server as dashboard


@pytest.fixture
def server(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "ROOT", tmp_path)
    (tmp_path / "index.html").write_text("dashboard fixture", encoding="utf-8")
    (tmp_path / "settings.json").write_text(json.dumps({"procedure_root":str(tmp_path / "data")}), encoding="utf-8")
    state = {"active":False}
    monkeypatch.setattr(dashboard.LicenseClient, "status", lambda self: state)
    http = dashboard.ThreadingHTTPServer(("127.0.0.1", 0), dashboard.LicensedHandler)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    yield f"http://127.0.0.1:{http.server_port}", state, tmp_path
    http.shutdown()
    http.server_close()
    worker.join(timeout=3)


@pytest.mark.parametrize("method", ["GET", "HEAD"])
@pytest.mark.parametrize("route", ["/", "/index.html", "/api/data", "/settings.json"])
def test_all_routes_deny_without_license(server, method, route):
    base, _, _ = server
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(urllib.request.Request(base+route, method=method), timeout=3)
    assert error.value.code == 403
    assert error.value.headers["Cache-Control"] == "no-store"


def test_active_allows_live_catalog_but_not_private_files(server):
    base, state, root = server
    state["active"] = True
    with urllib.request.urlopen(base+"/api/data", timeout=3) as response:
        assert json.load(response)["procedures"] == []
        assert response.headers["X-AIOS-Dashboard"] == "1"
    for route in ["/settings.json", "/data.js", "/../settings.json", "/%2e%2e/settings.json", "/data/"]:
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(base+route, timeout=3)
        assert error.value.code == 404
    with urllib.request.urlopen(base, timeout=3) as response:
        assert response.read() == b"dashboard fixture"
    state["active"] = False
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(base+"/api/data", timeout=3)
    assert error.value.code == 403


def test_foreign_host_is_rejected(server):
    base, state, _ = server
    state["active"] = True
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(urllib.request.Request(base, headers={"Host":"external.example"}), timeout=3)
    assert error.value.code == 403


def test_missing_settings_reports_unavailable(server):
    base, state, root = server
    state["active"] = True
    (root / "settings.json").unlink()
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(base+"/api/data", timeout=3)
    assert error.value.code == 503
