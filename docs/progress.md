# Compiled procedure runtime

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
- [ ] Tests, installation, commit and release complete successfully.

## Current

- Completed: procedure-runner and execution-plan schema.
- Completed: skill lifecycle, telemetry, migration, dashboard and runner transport tests.
- Completed: release build, tests and end-to-end installation.
- In progress: commit, push and GitHub release publication.
