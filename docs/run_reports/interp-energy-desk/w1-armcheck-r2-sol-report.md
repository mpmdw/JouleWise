Committed on `ops/2026-11-11-w1-armcheck-r2`; clean tree, no push.

Updated the arm helper, PREQUAL harness, their tests, and report. Added both dwell stamps, state/evidence classification, timeout rollback coverage, and explicit synthetic adapters.

- Passed: 24 watchdog tests, focused PREQUAL witness, 36 closure/registration tests, five dependent modules.
- Outstanding: full PREQUAL and remaining checks. One dependent test failed with `488 != 440`; pre-existence is unproven.
- Finding: the unchanged watchdog can probe remote Git before t0−180; probes are suppressed inside the span.

Commits: `9efe1d635`, `96f5a1f44`, `3be01f98f`, `dca880f05`.

[Round-2 report: files, commands, evidence, and native handoff](/Volumes/JW-EXT/jw-wt/sol-w1-armcheck-r2/docs/run_reports/2026-11-11-w1-armcheck.md:278). Native qualification and cold review remain lead-owned.