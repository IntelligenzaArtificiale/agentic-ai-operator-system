"""Create the ignored one-time setup token without printing it."""

from pathlib import Path
import secrets


target = Path(__file__).parents[1] / "license-server" / "private" / "setup-token.txt"
if target.exists():
    raise SystemExit("Setup token already exists.")
target.write_text(secrets.token_urlsafe(32), encoding="ascii")
print(f"Created {target} (value intentionally hidden).")
