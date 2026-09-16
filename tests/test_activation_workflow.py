from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys
import threading
from unittest.mock import Mock
from queue import Queue
from types import SimpleNamespace

import pytest

from licensing.activation_ui import ActivationWindow, perform, status_message
from licensing.client import LicenseClient, LicenseError
from licensing.locking import mutex
from test_licensing_client import FakeServer


def activated_client(tmp_path):
    client = LicenseClient(tmp_path)
    server = FakeServer(client)
    client.public_key = server.lease()["signing_public_key"]
    client._post = server.post
    return client, server


def test_activation_writes_once_and_verifies_persisted_state(tmp_path, monkeypatch):
    client, _ = activated_client(tmp_path)
    save = Mock(wraps=client._save)
    monkeypatch.setattr(client, "_save", save)
    assert client.activate("TEST")["active"]
    assert save.call_count == 1
    assert client.status(False)["active"]


def test_write_failure_does_not_report_activation_success(tmp_path, monkeypatch):
    client, _ = activated_client(tmp_path)
    monkeypatch.setattr(client, "_save", Mock(side_effect=PermissionError("TEST")))
    result = perform(client, "activate", "SECRET-TEST-KEY")
    assert result["active"] is False
    assert "Verifica stato" in result["message"]
    assert "SECRET" not in str(result)


def test_expired_activation_not_persisted(tmp_path):
    client, server = activated_client(tmp_path)
    client._post = lambda _: {"activation_token": server.token, **server.lease(-1)}
    with pytest.raises(LicenseError, match="scaduta"):
        client.activate("TEST")
    assert not client.state_path.exists()


def test_failed_deactivation_preserves_state_for_retry(tmp_path, monkeypatch):
    client, _ = activated_client(tmp_path)
    client.activate("TEST")
    saved = client.state_path.read_bytes()
    monkeypatch.setattr(client, "_post", Mock(side_effect=OSError("offline")))
    with pytest.raises(OSError):
        client.deactivate()
    assert client.state_path.read_bytes() == saved


def test_confirmed_deactivation_removes_local_lease(tmp_path):
    client, _ = activated_client(tmp_path)
    client.activate("TEST")
    client.deactivate()
    assert not client.state_path.exists()


def test_inactive_response_never_becomes_success_message():
    client = Mock()
    client.activate.return_value = {"active": False, "message": "Non verificata"}
    assert status_message(perform(client, "activate", "TEST")) == "Non verificata"
    text = status_message({"active": True, "valid_until": "2099-01-01"})
    assert "2099" not in text  # Offline lease is not the subscription expiration.
    assert "Licenza attiva" in text


def test_concurrent_device_initialization_has_one_identity(tmp_path):
    barrier = threading.Barrier(8)

    def identify(_):
        client = LicenseClient(tmp_path)
        barrier.wait(timeout=5)
        return client.device_id()

    with ThreadPoolExecutor(max_workers=8) as pool:
        identities = list(pool.map(identify, range(8)))
    assert len(set(identities)) == 1
    assert len(identities[0]) == 64


def test_concurrent_status_checks_keep_valid_state(tmp_path):
    client, _ = activated_client(tmp_path)
    client.activate("TEST")

    def check(_):
        reader = LicenseClient(tmp_path)
        reader.public_key = client.public_key
        return reader.status(False)["active"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert all(pool.map(check, range(24)))
    assert client.status(False)["active"]
    assert not list(tmp_path.glob("license-*.tmp"))


def test_mutex_excludes_another_process_and_releases(tmp_path):
    code = ("from licensing.locking import mutex; import sys\n"
            "with mutex('activation-ui', sys.argv[1]) as acquired: print(acquired)")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1] / "atpa-v1/runtime"))

    def child():
        return subprocess.check_output([sys.executable, "-c", code, str(tmp_path)],
                                       env=env, text=True, timeout=10).strip()

    with mutex("activation-ui", tmp_path) as acquired:
        assert acquired
        assert child() == "False"
    assert child() == "True"


def test_busy_ui_does_not_start_a_second_operation():
    view = Mock(busy=True)
    ActivationWindow._start(view, "activate", "TEST")
    view.status_text.set.assert_not_called()
    ActivationWindow.activate(view)
    view.key.get.assert_not_called()


def test_ui_background_job_and_poll_confirm_only_verified_state():
    client = Mock()
    client.activate.return_value = {"active": True, "valid_until": "2099-01-01"}
    view = SimpleNamespace(busy=False, client=client, results=Queue(),
                           status_text=Mock(), controls=[Mock(), Mock()],
                           key=Mock(), after=Mock(), _poll=Mock())
    ActivationWindow._start(view, "activate", "TEST")
    ActivationWindow._start(view, "activate", "TEST")
    result = view.results.get(timeout=3)
    view.results.put(result)
    assert view.busy
    ActivationWindow._poll(view)
    client.activate.assert_called_once_with("TEST")
    assert not view.busy
    view.key.set.assert_called_once_with("")
    assert "Licenza attiva" in view.status_text.set.call_args.args[0]
    assert "2099" not in view.status_text.set.call_args.args[0]


def test_status_distinguishes_local_io_failure(tmp_path, monkeypatch):
    client = LicenseClient(tmp_path)
    monkeypatch.setattr(client, "_load", Mock(side_effect=PermissionError("TEST")))
    result = client.status(False)
    assert result["active"] is False
    assert result["code"] == "local_state_unavailable"


def test_persisted_state_must_be_verified_before_success(tmp_path, monkeypatch):
    client, _ = activated_client(tmp_path)
    monkeypatch.setattr(client, "_load", Mock(side_effect=LicenseError("Non autentica")))
    result = perform(client, "activate", "TEST")
    assert result["active"] is False


def test_install_and_dashboard_do_not_auto_open_activation():
    root = Path(__file__).parents[1] / "atpa-v1"
    installer = (root / "Install-System.ps1").read_text(encoding="utf-8-sig")
    dashboard = (root / "runtime/Update-Dashboard.ps1").read_text(encoding="utf-8-sig")
    launcher = (root / "runtime/licensing/launcher.py").read_text(encoding="utf-8")
    assert "Start-Process -FilePath $runnerPython" not in installer
    assert "activation_ui.py" not in dashboard
    assert "activation_ui.py" not in launcher
    assert "Attiva Agentic AI Operator System.lnk" in installer
