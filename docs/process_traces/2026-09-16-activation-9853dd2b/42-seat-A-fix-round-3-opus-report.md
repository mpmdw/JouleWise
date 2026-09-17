# Seat A fix round 3 — Opus 5 implementation seat (Codex quota exhausted), 2026-09-17 03:36–04:25 PDT

Brief: record 41. Verbatim report:

Seat A fix round 3 — COMPLETE, all 16 modules green. No git writes; all edits inside WRITE_SCOPE. No NEEDS_SCOPE, no NEEDS_RULING. One contract-text consequence you asked me to flag (item C below).

## Per failing test: root cause (file:line at f44652dc), fix, pinning test

**(1) tests.test_validate_powermetrics_fiducial.ContinuedEpochPreflightTests.test_invalid_acceptance_id_returns_named_cli_refusal_without_traceback (4 params), (2) test_powermetrics_fiducial.FrozenProtocolTests.test_acceptance_artifact_refusals_are_distinct_and_emit_no_output (3 err + 1 fail), (3) ...test_estimator_byte_drift_refuses_acceptance_as_stale — one root cause.**
Round 2 routed the writer's preflight snapshot through the bounded custody worker (`scripts/validate_powermetrics_fiducial.py:2010`, `custody_deadline=custody_deadline`), and `_bounded_custody_request` printed its diagnostics to `sys.stderr` unconditionally — `joulewise/calibration_ledger.py:2101` (`calibration_custody_complete`) and `:2080` (`calibration_custody_progress`). I captured the actual stderr: line 1 was `{"event": "calibration_custody_complete", "elapsed_s": …, "observations": 0}`, line 2 the refusal — hence `Extra data: line 2 column 1`.
Fix: the diagnostics stream is now a property of the allowance. `CustodyDeadline.__init__` takes `telemetry_stream`, defaulting to the sentinel `CUSTODY_TELEMETRY_STDERR` (resolved to `sys.stderr` at write time, so in-process capture still works); `next_operation()` propagates it; the two prints go through the new `_custody_telemetry()` helper, which writes nothing when the stream is `None`. The writer CLI constructs its allowance with `telemetry_stream=None`, because its stderr contract is exactly one JSON line. Reservation is untouched and keeps the stderr diagnostics its own tests pin (`tests/test_calibration_ledger_custody.py:713/937/997`). `scripts/reserve_calibration_window_bracket.py` is NOT modified.
Pinned by: the three tests above, unchanged.

**(4) test_powermetrics_fiducial.WriterLedgerIntegrationTests.test_main_preserves_symlinked_custody_spelling_used_by_reservation.**
Not a custody-locator bug. `scripts/validate_powermetrics_fiducial.py:1853` read `ledger_lifecycle.phase` unconditionally; the test patches `_CaptureLedgerLifecycle` with a stub (`StopAfterCustodyCapture`) that has neither `.phase` nor `.custody_deadline`, so the refusal path raised `AttributeError` instead of refusing.
Fix: the `emit_refusal` closure now reads `getattr(ledger_lifecycle, "phase", None) or "writer_preflight"` and `getattr(ledger_lifecycle, "custody_deadline", None) or custody_deadline`. Refusing must not depend on a lifecycle object being fully constructed. Pinned by that test.

**(5) test_powermetrics_fiducial.WriterLedgerIntegrationTests.test_writer_repairs_under_lease_and_uses_one_stable_claim.**
Round 2 added `self._validate_slot(ledger_snapshot=under_lease_snapshot)` at `scripts/validate_powermetrics_fiducial.py:1523-1524`, before the repair — giving `['validate','validate','repair','validate']` against the pinned `['validate','repair','validate']`.
Fix: removed that extra slot validation. The under-lease `load_calibration_ledger_snapshot(verify_custody=True, custody_deadline=…)` is KEPT (it is the under-lease custody authentication this lane exists for); only its return value is now discarded, with a comment saying why. Slot binding keeps its two pinned checks: before the lease, and after recovery in `_begin_once`. Pinned by that test, and the `under_lease` phase remains pinned by `tests/test_validate_powermetrics_fiducial_derivation_only.py:1016` (`_stall(1)`), which still passes.

## Two knock-on repairs my fix forced (both found by running, not guessed)

**(A) `tests/calibration_exits_fixtures/custody_hang.py:assert_workers_gone`** derived worker PIDs *only* from `calibration_custody_progress` lines on stderr and asserted the set was non-empty — so silencing writer diagnostics broke 3 tests in `test_validate_powermetrics_fiducial_derivation_only` (`_stall(0)`, `_stall(1)`, `test_final_artifact_timeout_preserves_existing_session`). I did NOT weaken it: the PID loop is kept, and a strictly stronger check was added. `CustodyFixture.run` records the child's process-group id (`start_new_session=True` ⇒ pgid == pid; every custody worker inherits the group), and `assert_workers_gone` now requires `os.killpg(pgid, 0)` to raise `ProcessLookupError` after the leader has exited and been reaped — a surviving group member can only be a leaked worker. This catches leaks that never emitted a progress line, which the old check could not.

**(B) `tests/test_authentication_io.py`** — the classified-reads allowlist keys on `file:function:LINE:call`, and my +20 lines in `calibration_ledger.py` shifted 8 entries. I rebased all 8 line numbers and verified each new line is the same call at the same function (`3225→3245 read_text`, `3329→3349`, `3660→3680`, `3605→3625`, `3277→3297`, `3291→3311` os.open, `4291→4311`, `4348→4368` os.fdopen). Comments untouched. This is the same maintenance round 2 already did.

**(C) CONTRACT TEXT — the sibling notice moved inside the single JSON line, as you authorised.** `emit_calibration_refusal` previously printed `calibration refusal document exists; writing …` and `…could not be written: …` as extra stderr lines (`joulewise/calibration_exits.py:667,675`), which contradicts the one-line pin whenever `JOULEWISE_CALIBRATION_REFUSAL_PATH` is set. They are now context fields on the single refusal line: `refusal_document`, `refusal_document_existing`, `refusal_document_error`. `tests/test_calibration_ledger_custody.py:878` (`assertIn(str(siblings[0]), completed.stderr)`) still passes, since the path is in the JSON. I updated `docs/contracts/calibration_ledger_append.md` with two new paragraphs stating (i) every refusing command writes exactly one JSON line to stderr and carries document-collision facts as fields, and (ii) which commands emit `calibration_custody_progress`/`calibration_custody_complete` (reservation yes, capture writer no, with `last_observation` in the refusal document as the writer's equivalent evidence).

Design note for the deadline consult (not actioned, outside my scope): the writer now has NO progress trace on a hang; its only in-flight evidence is `last_observation` in the refusal document. If the night wants writer-side progress, it needs a channel that is not stdout/stderr.

## Verification — 16 modules, ALL OK (final tree, sequential, `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest <m>`)

Seven named in the brief:
- tests.test_powermetrics_fiducial — Ran 75 tests in 63.407s — OK
- tests.test_validate_powermetrics_fiducial — Ran 12 tests in 7.477s — OK
- tests.test_validate_powermetrics_fiducial_derivation_only — Ran 20 tests in 83.698s — OK
- tests.test_calibration_ledger_custody — Ran 42 tests in 32.647s — OK
- tests.test_calibration_custody_worker — Ran 12 tests in 1.590s — OK
- tests.test_calibration_exits — Ran 48 tests in 496.066s — OK
- tests.test_authentication_io — Ran 22 tests in 0.994s — OK (+ `KILLED 3 renderer AST mutations`)

Nine adjacent modules I added on my own initiative, all OK:
- test_calibration_ledger 92/4.702s OK (skipped=1); test_custody_mode_inventory 7/34.981s OK; test_calibration_custody_store 7/0.227s OK; test_calibration_bracketing 92/0.522s OK (skipped=1); test_calibration_writer_crash_matrix 20/258.566s OK; test_night_plan_writer 8/0.008s OK; test_check_gate_ledger 31/1.638s OK; test_reissue_calibration_acceptance 6/0.053s OK; test_issue_calibration_acceptance_generation 114/62.745s OK

Full log: `/tmp/rh-core-verify.log`. Nothing still running.

Modules under `tests/` matching fiducial|calibration|custody|reserve|ledger|writer — RAN: the 16 above. NOT RUN (3): `tests/test_calibration_live_three_window.py`, `tests/test_paper_custody.py`, `tests/test_paper_first_use_ledger.py`. (`tests/verify_calibration_acceptance_corpus.py` is a helper, not a unittest module.)

`compileall`: `PYTHONPYCACHEPREFIX=/tmp/rh-core-pycache python3 -m compileall -q scripts joulewise` → **rc=0**. No `.pyc` anywhere in the tree (an empty, gitignored `scripts/__pycache__/` directory predates my session; it holds no bytecode).

## git status --short
```
 M docs/contracts/calibration_ledger_append.md
 M joulewise/calibration_exits.py
 M joulewise/calibration_ledger.py
 M scripts/validate_powermetrics_fiducial.py
 M tests/calibration_exits_fixtures/custody_hang.py
 M tests/test_authentication_io.py
```
## git diff --stat
```
 docs/contracts/calibration_ledger_append.md      | 15 +++++++++
 joulewise/calibration_exits.py                   | 14 ++++++---
 joulewise/calibration_ledger.py                  | 40 ++++++++++++++++++------
 scripts/validate_powermetrics_fiducial.py        | 28 ++++++++++++-----
 tests/calibration_exits_fixtures/custody_hang.py | 20 +++++++++++-
 tests/test_authentication_io.py                  | 16 +++++-----
 6 files changed, 102 insertions(+), 31 deletions(-)
```
Pathspec for your commit: exactly those six paths. `joulewise/calibration_custody_worker.py` and `scripts/reserve_calibration_window_bracket.py` were NOT touched; the custody-deadline architecture was not altered.
