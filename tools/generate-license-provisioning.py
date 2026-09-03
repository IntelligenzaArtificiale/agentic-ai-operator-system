"""Generate ignored server secrets and print only the public verification key."""

from __future__ import annotations

import base64
from pathlib import Path
import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


root = Path(__file__).parents[1]
target = root / "license-server" / "private" / "provisioning.php"
if target.exists():
    raise SystemExit("Provisioning already exists; refusing to rotate the production signing key.")
private = Ed25519PrivateKey.generate()
seed = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
secret = seed + public
pepper = secrets.token_bytes(32)
target.write_text(
    "<?php\ndeclare(strict_types=1);\nreturn [\n"
    f"    'license_pepper' => '{base64.b64encode(pepper).decode()}',\n"
    f"    'signing_secret_key' => '{base64.b64encode(secret).decode()}',\n"
    "];\n",
    encoding="utf-8",
)
print(base64.urlsafe_b64encode(public).decode().rstrip("="))
