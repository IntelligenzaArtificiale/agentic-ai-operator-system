from __future__ import annotations

import base64
from pathlib import Path
import re

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from licensing.client import PINNED_PUBLIC_KEY


def test_local_provisioning_matches_pinned_client_identity():
    path = Path(__file__).parents[1] / "license-server" / "private" / "provisioning.php"
    if not path.exists():
        pytest.skip("production provisioning is intentionally not committed")
    content = path.read_text(encoding="utf-8")
    match = re.search(r"signing_secret_key' => '([^']+)'", content)
    assert match
    secret = base64.b64decode(match.group(1))
    public = Ed25519PrivateKey.from_private_bytes(secret[:32]).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    assert base64.urlsafe_b64encode(public).decode().rstrip("=") == PINNED_PUBLIC_KEY
