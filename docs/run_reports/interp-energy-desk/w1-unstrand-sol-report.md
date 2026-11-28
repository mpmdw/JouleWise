Implemented on `ops/2026-11-11-w1-unstrand`: delivered pre-chain refusal recovery and opt-in, locked `--restore-host` with a write-once record.

Changed only the helper, its test module, and the required report. Commits: `3a1b6ec89`, `9a9afd840`, `5a1aca68b`. Tree clean; nothing pushed.

Validation: all 27 new/updated tests and 36 closure/registration tests passed. The full unstrand module has one unchanged baseline follower timing failure and two native-process skips.

Lead cold review and remote native host checks remain. Exact commands, failure evidence, file changes, and next steps are in the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-unstrand/docs/run_reports/2026-11-11-w1-unstrand.md).