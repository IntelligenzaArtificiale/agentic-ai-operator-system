# Licensing architecture

## Goal

Agentic AI Operator System must execute licensed capabilities only while a
server-issued device lease is valid. Activation happens in a dedicated local
window. License keys and activation tokens never enter model context, skill
files, telemetry or ordinary logs.

## Enforcement boundary

The trusted boundary is executable code, not a prompt:

1. the licensed Windows MCP entry point checks every tool call;
2. the procedure runner checks every tool call;
3. the OpenSteps and dashboard shortcuts use licensed launchers;
4. every operational skill checks status first and cannot obtain the key;
5. the updater installs the gated entry points before requesting activation.

The two licensing tools that remain available while locked only return a
redacted status or open the local activation window.

## Server model

The PHP service has separate administration and API entry points. License keys
are generated with a cryptographically secure random source and only their
keyed hashes and short display prefixes are stored. Device activation tokens
are also stored only as keyed hashes.

The server signs short-lived leases with Ed25519. The private signing key and
hash pepper stay in the server-only configuration. The package embeds only the
public verification key and rejects an activation endpoint with a different
identity. A lease binds:

- license identifier;
- opaque activation identifier;
- hashed device identifier;
- issue, refresh and expiry times;
- current license status and enabled product.

The server is authoritative for activation, expiry, suspension, revocation and
device limits. Online clients refresh periodically. During an outage they may
use only an unexpired signed lease; after that the system fails closed.

## `license.json`

The JSON document is server-side state, never a public download:

```json
{
  "schema_version": 1,
  "revision": 0,
  "licenses": {},
  "rate_limits": {},
  "audit": []
}
```

Each license contains customer contact data, a validation hash, display prefix
and an authenticated Sodium Secretbox ciphertext used only for explicit
administrator display. Plaintext keys are never persisted; legacy records need
one key regeneration. A license also contains status, expiry, device limit,
timestamps and a map of activated devices. Each
device contains its hashed identifier, label, token hash, activation and last
seen timestamps, client version and optional revocation timestamp. Writes are
serialized with a dedicated lock file and committed through an atomic rename.

The production data directory must be outside the web root when hosting allows
it. The bundled fallback includes an Apache deny rule, but deployment must also
verify that direct HTTP access to private files returns a denial.

## Local state

Windows stores the activation token and last signed lease in a DPAPI-protected
file scoped to the current Windows account. The stable device identifier is a
one-way hash of the Windows machine identifier and an installation identifier;
raw hardware identifiers are not sent or logged.

The client never trusts unsigned API fields. It verifies the Ed25519 signature,
product, device binding and lease times before allowing an operation.

## Expiry and revocation

- Active and online: refresh at a bounded interval.
- Temporarily offline: continue only until the signed lease expires.
- Expired, suspended, revoked or over device limit: deny tools and launchers.
- Reactivated or extended: the next successful refresh unlocks the system.

No licensing action changes unrelated Windows files, permissions or processes.
Procedure files remain owned, backupable and deletable by the customer. The
licensed system refuses to read, create, modify, display or execute them while
locked. Making customer files undeletable or irrecoverable is deliberately out
of scope because it is unsafe and cannot be guaranteed against a Windows
administrator.

## Known security boundary

Client-side licensing is resistance against ordinary sharing and accidental
use, not mathematically unbreakable DRM. A machine owner with administrator
rights can replace binaries or use unrelated automation tools. Enforcement is
therefore duplicated at every shipped executable boundary, signed server state
is required, secrets are excluded from model context, and bypass attempts are
made materially harder without harming the customer's computer or data.
