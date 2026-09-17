# Final delta re-audit over 3c685b6e..52274fc3 — Opus 5, read-only, 2026-09-17 05:35–06:19 PDT

Verbatim report:

DELTA RE-AUDIT `3c685b6e..52274fc3` (NIGHT-RESERVE-HANG-01, read-only Opus, `/tmp/reaudit-final` copy; canonical, night-custody, LaunchAgents, launchctl, network untouched)

## VERDICT: MERGEABLE-WITH-FIXES
No blocker condition holds. Findings below are ranked; every claim was executed.

## Kill re-application (all in the /tmp copy, restored between each)
| Mutation | Killed by | Observed |
|---|---|---|
| remove `probe_custody` guard (`calibration_ledger.py:5318`) | `test_calibration_ledger_custody` | `FAILED (failures=4)` — `CalibrationLedgerError not raised` ×3 (callers `_read_contained_nofollow`, `_governed_raw_nofollow`, `_custody_reasons`) + `Assign(...paths...) is not an instance of ast.If` |
| drop chain marker export (`calibration_derivation_only.zsh:80`) | `test_run_night` | `{'unset'} != {'45'}` |
| drop driver pop (`run_night.py:469`) | `test_run_night` | `'JOULEWISE_NIGHT_CUSTODY_BUDGET_S' unexpectedly found` |
| headroom gate → `if False` (`night_agent_install.py:811`) | `test_run_night` | `Refused not raised` at `custody_elapsed_s=20.02` |
| remove `observations>0` gate (`:843`) | `test_run_night` | `Refused not raised` (regex `observations`) |
| restore extra under-lease slot validation (`validate_powermetrics_fiducial.py:1517`) | `test_powermetrics_fiducial` | `['validate','validate','repair','validate'] != ['validate','repair','validate']` |
| writer telemetry back to stderr (`:1868`) | `test_validate_powermetrics_fiducial` | `FAILED (errors=4)` — `JSONDecodeError: Extra data: line 2 column 1` |
| `PROBE_CODE_PATHS` back to 3 paths | `test_install_night_agent` | `FAILED (failures=15)`, `'install_span_closed' not found in 'probe receipt code_digests mismatch'` |
| restore old rerun path `refusal.json` | `test_run_night` | `FAILED (failures=4)`, incl. `[] != [PosixPath('.../night/refusal.json')]` |

**SURVIVOR:** `run_night.py:2240` `record["code_digests"] = bindings["code_digests"]` → `value["code_digests"]` leaves `test_run_night` (126 OK) **and** `test_install_night_agent` (60 OK) green. See F2.

## Findings
**F1 SHOULD-FIX — the marker refusal is misattributed to corrupt custody.** `calibration_ledger.py:2866` wraps it as `primary evidence is unreadable`, and `calibration_exits.py:215` renders `LEDGER_CUSTODY_INVALID` as `receipt-bound evidence bytes are absent or hash-invalid`. Executed: `JOULEWISE_NIGHT_CUSTODY_BUDGET_S=120 python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only.WriterCustodyDeadlineTests.test_writer_preflight_stall_refuses_without_starting_slot` →
`CalibrationLedgerError: .../20260101T000001-aaaaaaaa: primary evidence is unreadable: calibration_ledger_custody_invalid: receipt-bound evidence bytes are absent or hash-invalid (caller='_read_contained_nofollow', ..., reason='custody_read_unbounded_under_night_budget')`.
A desk operator reads "your evidence is corrupt". The context never names the variable. Scope is desk-only — the three unbounded `probe_custody` routes are `_inspect_historical_candidate` (`:2850`), `_reauthenticate_historical_import_plan` (`:3877`), `resume_finalize_bracket_session` (`:5790`), none chain-reachable — so not a blocker. Fix: add `"unset": NIGHT_CUSTODY_BUDGET_ENV` to the guard's context (`:5318`).

**F2 SHOULD-FIX — the receipt's superset publication is uncovered.** Publishing the reservation's 3-entry echo instead of the installer's 5-entry binding survives both modules, yet in production `validate_probe_receipt`'s `for field, value in expected.items()` (`night_agent_install.py:848`) would refuse **every** real install with `probe receipt code_digests mismatch`. Fail-closed but arm-blocking, and no test exercises `_probe_worker` → `validate_probe_receipt`. Related: no test runs the capture writer CLI with the marker inherited (`custody_hang.py` and the derivation-only module both scrub env to PATH). I ran it — patched `_fresh_env` to export `JOULEWISE_NIGHT_CUSTODY_BUDGET_S=120`: `Ran 20 tests ... OK`. Fix: one install-path test that consumes a worker-written receipt; one writer test with the marker exported.

**F3 SHOULD-FIX — no success-path custody timing on the night.** `telemetry_stream=None` silences `calibration_custody_progress`/`_complete` for the writer; `grep custody_elapsed` finds no other success-path recorder. The refusal path is fine (`CustodyDeadline.context()` `:1970-1975` carries `last_observation` + `elapsed_s`, set independently of telemetry at `:2163`). What is lost is the healthy-night T series — the quantity the new headroom gate is sized against. Fix: carry `custody_elapsed_s`/`observations` in the writer's success receipt on stdout (single JSON object, no stderr-contract break).

**F4 NIT — worst-case abort is N×budget, unstated.** `calibration_session_status` (`:5452`) calls `_custody_state` once per declared slot with no deadline → a fresh ambient budget each. `SLOT_COUNT` default 12 (chain `:85`) ⇒ up to 12×120 s = 1440 s, plus the abort's own call ≈ 1560 s ≈ 26 min. Against `COURIER_DEADLINE_S=300` + `DEADMAN_GRACE_S=3600` (`run_night.py:64,67,1062`): 1560 s < 3900 s, so the dead-man does **not** fire and the courier still delivers. Improvement over unbounded; state the 12×120 s worst case in the runbook.

**F5 NIT — subset echo has no floor.** `run_night.py:2219-2224` accepts any non-empty subset; the reservation computes exactly three (`reserve_calibration_window_bracket.py:350-357`). A silently shrunk echo still passes. Fix: `set(echoed) >= {those three}`.

**F6 NIT — `custody_elapsed_s` is not purely the corpus pass.** `elapsed_s` = `time.monotonic()-started` since deadline construction (`:1967`, `:1932`), so it includes ledger read/parse. Conservative for the gate; the runbook says the probe reports "that pass, and only that pass" — add a clause.

## Traced, no finding
- **(b)** `metadata_only=True` site is genuine: `assert_custody_directory` (`calibration_custody_worker.py:58-69`) makes only `os.lstat`/`os.stat` calls; no governed bytes.
- **(d) the gate will NOT refuse every real arm.** Measured on this machine with the production reader: `read_authentication_input`+sha256 over 1.195 GB → **0.57 s, 2.09 GB/s** ⇒ 3.33 GB ≈ **1.6 s** warm; cold local SSD adds <1 s. Limit is T ≤ 20 s (120/(4×1.5)) ⇒ ~10× margin for a *materialized* corpus. Unmeasured term: per-open FileProvider latency for 190 files across 38 iCloud locators — at 100 ms/open that alone is 19 s. Recommend the lead record the first real probe's `custody_elapsed_s` in the arm record and treat >10 s as the trigger to land CUSTODY-PASS-MEMO-01 before arming. An evicted corpus refusing the install is correct fail-closed behaviour.
- **(e)** refusal-side evidence intact (see F3 for what is not).
- **(f)** fewer echoed digests pass by design; installer recomputes all five and compares field-by-field.
- **(g)** rerun stem is clean: `_write_refusal_bytes` (`:236-245`) yields `rerun.refusal-01.json`; `_refusal_paths` (`:248-251`) globs only `refusal.json`/`refusal-NN.json`/`calibration-refusal*`; both call sites return `EXIT_REFUSED` before any courier call (`:1282-1285`, `:1638-1641`); courier prompt names the exception.
- **(h)** nothing measurement/instrument/claim/census-bearing changed. Chain re-pin verified: `shasum -a 256` = `4f1ede1e19af550cd153c86860eb4bd3cb1efc2c5f4a6c30fbb5cdcc45721e37`, matching both runsheet occurrences. `night_calibration_refused` is a real emitted reason (`night_gate.py:87`, `run_night.py:519-521`) — registry parity only.
- **Marker is inert inside the writer.** Instrumented `_ambient_custody_deadline` to log every construction, ran the whole derivation-only writer module with the marker exported: **zero** ambient deadlines built — every writer custody entry threads its own. Timing 112 s (no marker) vs 117 s (marker): no measurable cost.

## Suites (pristine head, `/tmp/reaudit-final` byte-identical to the worktree by `diff -r`)
`test_calibration_ledger_custody` 50 OK · `test_calibration_custody_worker` 12 OK · `test_run_night` 126 OK · `test_arm_retry` 27 OK · `test_authentication_io` 22 OK · `test_validate_powermetrics_fiducial` 12 OK · `test_validate_powermetrics_fiducial_derivation_only` 20 OK · `test_powermetrics_fiducial` 75 OK · `test_install_night_agent` 60 OK · `test_night_agent_install` 57 OK · `zsh -n scripts/night_chains/calibration_derivation_only.zsh` rc 0.

Blocker checklist: night cannot hang unattended (real-CLI barrier regression, base-failing, refuses in <5 s with ledger+pin bytes unchanged); no append-after-expiry path touched; refusal still reaches the courier; install cannot admit without a valid receipt (both gates kill-verified); a real arm can pass (arithmetic above); no unauthorised semantics change.
