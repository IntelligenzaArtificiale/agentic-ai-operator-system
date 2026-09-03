from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from licensing.client import LicenseClient, PRODUCT


def b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


class FakeServer:
    def __init__(self, client: LicenseClient):
        self.client = client
        self.private = Ed25519PrivateKey.generate()
        self.token = "T" * 43
        self.denied = False

    def lease(self, seconds: int = 3600) -> dict:
        now = datetime.now(timezone.utc)
        payload = json.dumps({
            "schema_version": 1, "product": PRODUCT, "license_id": "license-1",
            "activation_id": "activation-1", "device_hash": self.client.device_id(),
            "status": "active", "issued_at": now.isoformat(),
            "refresh_after": (now + timedelta(minutes=5)).isoformat(),
            "valid_until": (now + timedelta(seconds=seconds)).isoformat(),
        }, separators=(",", ":")).encode()
        public = self.private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return {"lease": b64(payload), "signature": b64(self.private.sign(payload)), "signing_public_key": b64(public)}

    def post(self, body: dict) -> dict:
        if self.denied:
            from licensing.client import LicenseError
            raise LicenseError("Licenza revocata.")
        if body["action"] == "activate":
            return {"ok": True, "activation_token": self.token} | self.lease()
        if body["action"] == "validate":
            lease = self.lease()
            lease.pop("signing_public_key")
            return {"ok": True} | lease
        return {"ok": True}


def test_activation_is_dpapi_protected_and_valid(tmp_path: Path):
    client = LicenseClient(tmp_path)
    fake = FakeServer(client)
    client.public_key = fake.lease()["signing_public_key"]
    client._post = fake.post
    result = client.activate("AIOS-EXAMPLE")
    assert result["active"] is True
    raw = client.state_path.read_bytes()
    assert fake.token.encode() not in raw
    assert b"activation_token" not in raw


def test_device_identity_is_cached_and_persisted(tmp_path: Path, monkeypatch):
    client = LicenseClient(tmp_path)
    values = iter(["machine-guid-a", "machine-guid-b"])
    monkeypatch.setattr(client, "_machine_guid", lambda: next(values))
    first = client.device_id()
    assert client.device_id() == first

    reloaded = LicenseClient(tmp_path)
    monkeypatch.setattr(reloaded, "_machine_guid", lambda: "different-machine-guid")
    assert reloaded.device_id() == first
    assert reloaded.device_path.read_text(encoding="ascii") == first


def test_tampered_lease_is_rejected(tmp_path: Path):
    client = LicenseClient(tmp_path)
    fake = FakeServer(client)
    client.public_key = fake.lease()["signing_public_key"]
    client._post = fake.post
    client.activate("AIOS-EXAMPLE")
    state = client._load()
    state["lease"] = state["lease"][:-2] + "AA"
    client._save(state)
    assert client.status(refresh=False)["active"] is False


def test_unpinned_server_identity_is_rejected(tmp_path: Path):
    from licensing.client import LicenseError

    client = LicenseClient(tmp_path)
    fake = FakeServer(client)
    client._post = fake.post
    try:
        client.activate("AIOS-EXAMPLE")
        raise AssertionError("untrusted signing key accepted")
    except LicenseError as error:
        assert "Identità" in str(error)


def test_expired_offline_lease_fails_closed(tmp_path: Path):
    client = LicenseClient(tmp_path)
    fake = FakeServer(client)
    client.public_key = fake.lease()["signing_public_key"]
    response = {"activation_token": fake.token} | fake.lease(seconds=-1)
    client._save({**response, "last_clock": "1970-01-01T00:00:00Z"})
    assert client.status(refresh=False)["active"] is False


def test_revocation_is_seen_at_refresh(tmp_path: Path):
    client = LicenseClient(tmp_path)
    fake = FakeServer(client)
    client.public_key = fake.lease()["signing_public_key"]
    client._post = fake.post
    client.activate("AIOS-EXAMPLE")
    state = client._load()
    lease = fake.lease()
    payload = json.loads(base64.urlsafe_b64decode(lease["lease"] + "=="))
    payload["refresh_after"] = "2000-01-01T00:00:00+00:00"
    encoded = json.dumps(payload, separators=(",", ":")).encode()
    state["lease"] = b64(encoded)
    state["signature"] = b64(fake.private.sign(encoded))
    client._save(state)
    fake.denied = True
    assert client.status()["active"] is False
