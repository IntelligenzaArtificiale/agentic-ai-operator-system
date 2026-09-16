# Compiled procedure runtime

## 2.6.0 — operational dashboard and clean reinstall (2026-09-16)

- [x] Review local runtime, dashboard, installer and ownership of installed files.
- [x] Replace dashboard presentation with accessible process-first navigation and truthful metrics.
- [x] Refresh local data without repeated shell launches; protect every dashboard route.
- [x] Regression-test empty, populated, malformed and unlicensed states and responsive layout.
- [x] Build, commit and publish a verified Windows release.
- [x] Remove only AIOS installations, integrations and user-requested procedure data on this device.
- [x] Verify clean state and document preserved shared dependencies and reinstall instructions.

Scope: no new unattended scheduler or production actions. Preserve source repository,
ChatGPT/Codex, browsers, accounts and unrelated plugins. Local reset happens last.

Verified: 74 Python tests, separate packaged MCP integrations, PowerShell telemetry,
browser QA at five widths and a full 2.6.0 install before the reset. Release CI
succeeded and the published archive SHA-256 matches its manifest. The license
server acknowledged device deactivation before identity removal. AIOS plugin,
both MCP registrations, runtime and old local data were removed; procedure data
and legacy folders were recycled, not irreversibly erased. Source and shared
Python remain. Restart the host app before installing from the latest release;
activate via the Desktop shortcut, then configure company DNA and a new process.

## Central licensing 2.5.0

- [x] Define the threat model, safe enforcement boundary and lease protocol.
- [x] Build the authenticated PHP administration panel and license API.
- [x] Hash license keys and device tokens; sign device-bound leases.
- [x] Build the DPAPI-protected Windows client and activation window.
- [x] Gate Windows MCP, procedure runner, OpenSteps and dashboard launchers.
- [x] Add migration and activation flow for upgrades from older versions.
- [x] Update all operational skills without exposing keys to model context.
- [x] Test activation, expiry, revocation, device limits, offline leases and tampering.
- [ ] Deploy the PHP service and verify denial of private server files.
- [ ] Install locally, commit, push and publish release 2.5.0.

## Contextual experience memory 2.4.0

- [x] Build a mandatory preflight manifest from the concrete procedure steps.
- [x] Bind incidents and preventive lessons to stable step identifiers.
- [x] Load reusable software, business and interaction-pattern experience by context.
- [x] Keep new shared lessons as candidates until repeated verified evidence promotes them.
- [x] Prevent successful completion when required steps are missing or silently skipped.
- [x] Preserve existing rich-text content through explicit insertion contracts.
- [x] Surface shared-memory totals in the dashboard.
- [x] Validate runtime, MCP transport, dashboard, installer and release package.
- [x] Install locally and publish version 2.4.0 to the canonical repository.

## Onboarding and company DNA 2.3.0

- [x] Add concise start command with the recommended usage sequence.
- [x] Add guided company-profile command with verified public research.
- [x] Store a reusable, provenance-aware company profile.
- [x] Show company identity and setup state in the local dashboard.
- [x] Migrate existing installations without overwriting their profile.
- [x] Validate skills, dashboard, installer, package and local installation.
- [x] Commit, push and publish release 2.3.0.

## Acceptance criteria

- [x] Every procedure includes a compiled execution plan.
- [x] Steps distinguish deterministic execution, AI reasoning and side effects.
- [x] Deterministic blocks run locally without intermediate screenshots.
- [x] Fast coordinates require matching environment guards.
- [x] Guard failures return control to the AI without unsafe continuation.
- [x] Promotion requires repeated clean runs.
- [x] Telemetry separates action, wait, observation, verification and recovery.
- [x] Installer registers the local procedure runner and migrates old procedures.
- [x] Dashboard exposes compiled-plan state and AI intervention metrics.
- [x] Tests, installation, commit and release complete successfully.

## Current

- Completed: procedure-runner and execution-plan schema.
- Completed: skill lifecycle, telemetry, migration, dashboard and runner transport tests.
- Completed: release build, tests, end-to-end installation, commit, push and GitHub release 2.2.0.
