# 07 — Registration of TEST-PGREP-DIALECT-MULTILINE-01 (2026-09-16 ~00:45 PDT, activation `08ca8197`)

Requested by the interactive session `b0ae8462` (cross-session message) as a
P3 nit found while its Codex seats were running.

## Facts re-read by this activation (main at `4c843126`)

`tests/test_arm_readiness_evidence_t0.py:2690`
`test_g4_real_ruled_census_pgrep_dialect`; at `:2741-2746` the test runs the
real `/usr/bin/pgrep -lf <pattern>` and builds
`reported = {int(line.split(" ", 1)[0]) for line in lines}` over
`probe.stdout.splitlines()`. `pgrep -lf` prints each matched process's full
command line after its PID; a live process whose argv contains newlines (a
Codex seat launched with a multi-line brief that mentions the pattern) makes
the continuation lines start with non-PID text, and the comprehension raises
`ValueError: invalid literal for int() with base 10: 'WRITE_SCOPE:'` (the
interactive session's report; its record 23 was not yet on main at this
registration).

## What was registered

Kernel row `TEST-PGREP-DIALECT-MULTILINE-01`, rank 213,
`p3_hardening_candidates`, lane `agent`, `queued`. Kernel 186 → 187 rows;
`TASK_QUEUE.md` regenerated; `tests/test_gen_state.py` updated. Registration
only; no test changed.
