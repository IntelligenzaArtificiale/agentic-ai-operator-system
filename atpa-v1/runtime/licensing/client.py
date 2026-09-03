"""Signed, device-bound license leases stored with Windows DPAPI."""

from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import urllib.error
import urllib.request
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


PRODUCT = "Agentic AI Operator System"
DEFAULT_API = "https://www.alessandrociciarelli.it/ai-os/api.php"
PINNED_PUBLIC_KEY = "ukYNPjeMZt_cXv6nm1X99y_z3qVGmCbF2GRm-k_D7yw"
ENTROPY = b"AIOS-LICENSE-STATE-V1"


class LicenseError(RuntimeError):
    """A safe, user-facing license denial."""


class _Blob(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_char))]


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _protect(value: bytes) -> bytes:
    source = ctypes.create_string_buffer(value)
    entropy = ctypes.create_string_buffer(ENTROPY)
    source_blob = _Blob(len(value), ctypes.cast(source, ctypes.POINTER(ctypes.c_char)))
    entropy_blob = _Blob(len(ENTROPY), ctypes.cast(entropy, ctypes.POINTER(ctypes.c_char)))
    output = _Blob()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(source_blob), PRODUCT, ctypes.byref(entropy_blob), None, None, 0, ctypes.byref(output)
    ):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        ctypes.windll.kernel32.LocalFree(output.data)


def _unprotect(value: bytes) -> bytes:
    source = ctypes.create_string_buffer(value)
    entropy = ctypes.create_string_buffer(ENTROPY)
    source_blob = _Blob(len(value), ctypes.cast(source, ctypes.POINTER(ctypes.c_char)))
    entropy_blob = _Blob(len(ENTROPY), ctypes.cast(entropy, ctypes.POINTER(ctypes.c_char)))
    output = _Blob()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(source_blob), None, ctypes.byref(entropy_blob), None, None, 0, ctypes.byref(output)
    ):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        ctypes.windll.kernel32.LocalFree(output.data)


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class LicenseClient:
    def __init__(self, state_dir: Path | None = None, api_url: str | None = None, version: str = "2.5.1"):
        root = state_dir or Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Intelligenza Artificiale Italia" / "Agentic AI Operator System"
        self.state_dir = Path(root)
        self.state_path = self.state_dir / "license.dat"
        self.install_path = self.state_dir / "install-id"
        self.device_path = self.state_dir / "device-id"
        self._device_id_cache: str | None = None
        self.api_url = api_url or os.environ.get("AIOS_LICENSE_API", DEFAULT_API)
        self.version = version
        self.public_key = PINNED_PUBLIC_KEY

    def status(self, refresh: bool = True) -> dict:
        try:
            state = self._load()
            if refresh and datetime.now(timezone.utc) >= _utc(self._lease(state)["refresh_after"]):
                try:
                    state = self._refresh(state)
                except (OSError, urllib.error.URLError):
                    pass
            lease = self._lease(state)
            now = datetime.now(timezone.utc)
            if now + timedelta(minutes=5) < _utc(state.get("last_clock", "1970-01-01T00:00:00Z")):
                raise LicenseError("Orologio di sistema non valido. Collegati a Internet e riprova.")
            if now >= _utc(lease["valid_until"]):
                raise LicenseError("Licenza scaduta o verifica online necessaria.")
            state["last_clock"] = now.isoformat().replace("+00:00", "Z")
            self._save(state)
            return {"active": True, "valid_until": lease["valid_until"], "license_id": lease["license_id"]}
        except LicenseError as error:
            return {"active": False, "message": str(error)}
        except Exception:
            return {"active": False, "message": "Attivazione richiesta."}

    def require(self) -> None:
        result = self.status()
        if not result["active"]:
            raise LicenseError(result["message"] + " Apri 'Attiva Agentic AI Operator System' dal menu Start.")

    def activate(self, license_key: str) -> dict:
        response = self._post({
            "action": "activate", "license_key": license_key, "device_id": self.device_id(),
            "device_name": platform.node() or "Windows device", "client_version": self.version,
        })
        if response.get("signing_public_key") != self.public_key:
            raise LicenseError("Identità del server licenze non valida.")
        state = {
            "activation_token": response["activation_token"], "lease": response["lease"],
            "signature": response["signature"],
            "last_clock": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        self._lease(state)
        self._save(state)
        return self.status(refresh=False)

    def deactivate(self) -> None:
        state = self._load()
        try:
            self._post({"action": "deactivate", "activation_token": state["activation_token"], "device_id": self.device_id()})
        finally:
            self.state_path.unlink(missing_ok=True)

    def device_id(self) -> str:
        if self._device_id_cache is not None:
            return self._device_id_cache
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if self.device_path.exists():
            stored = self.device_path.read_text(encoding="ascii").strip().lower()
            if len(stored) == 64 and all(character in "0123456789abcdef" for character in stored):
                self._device_id_cache = stored
                return stored
        if not self.install_path.exists():
            self.install_path.write_text(str(uuid.uuid4()), encoding="ascii")
        install_id = self.install_path.read_text(encoding="ascii").strip()
        machine_guid = self._machine_guid()
        device_id = hashlib.sha256(f"{PRODUCT}|{machine_guid}|{install_id}".encode()).hexdigest()
        try:
            with self.device_path.open("x", encoding="ascii") as file:
                file.write(device_id)
        except FileExistsError:
            persisted = self.device_path.read_text(encoding="ascii").strip().lower()
            if len(persisted) == 64 and all(character in "0123456789abcdef" for character in persisted):
                device_id = persisted
        self._device_id_cache = device_id
        return device_id

    @staticmethod
    def _machine_guid() -> str:
        try:
            import winreg

            access = winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, access) as key:
                value, _kind = winreg.QueryValueEx(key, "MachineGuid")
            if str(value).strip():
                return str(value).strip()
        except (ImportError, OSError):
            pass
        return platform.node() or "unknown-windows-device"

    def _refresh(self, state: dict) -> dict:
        response = self._post({"action": "validate", "activation_token": state["activation_token"], "device_id": self.device_id()})
        state.update({"lease": response["lease"], "signature": response["signature"]})
        self._lease(state)
        self._save(state)
        return state

    def _lease(self, state: dict) -> dict:
        payload = _b64url_decode(state["lease"])
        try:
            Ed25519PublicKey.from_public_bytes(_b64url_decode(self.public_key)).verify(_b64url_decode(state["signature"]), payload)
        except (InvalidSignature, ValueError, KeyError) as error:
            raise LicenseError("Licenza locale non autentica.") from error
        lease = json.loads(payload)
        if lease.get("product") != PRODUCT or lease.get("device_hash") != self.device_id() or lease.get("status") != "active":
            raise LicenseError("Licenza non valida per questo dispositivo.")
        return lease

    def _post(self, body: dict) -> dict:
        request = urllib.request.Request(self.api_url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": f"AIOS/{self.version}"})
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            try:
                message = json.load(error).get("error", "Licenza non valida.")
            except Exception:
                message = "Servizio licenze non disponibile."
            raise LicenseError(message) from error
        if not result.get("ok"):
            raise LicenseError(result.get("error", "Licenza non valida."))
        return result

    def _load(self) -> dict:
        if not self.state_path.exists():
            raise LicenseError("Attivazione richiesta.")
        return json.loads(_unprotect(self.state_path.read_bytes()))

    def _save(self, state: dict) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_name(f"license-{os.getpid()}-{uuid.uuid4().hex}.tmp")
        temporary.write_bytes(_protect(json.dumps(state, separators=(",", ":")).encode()))
        os.replace(temporary, self.state_path)
