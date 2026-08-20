# RAW TRIAGE EXTRACT — L2-CALIBRATION-ACQUISITION

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L2-CALIBRATION-ACQUISITION`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **READY**
- coverage: 15/16 (evidence_universe_count=16)
- findings: 4; falsifiers: 4

## FINDINGS (verbatim)

### F1 [should_fix] detect_pulses region projection has no work budget — non-termination on degenerate traces while holding the writer lease
- file_line: `joulewise/powermetrics_fiducial.py:554 (_accepted_region_projection; FIT_HALF_RANGE_S=0.75 at :70, REGION_COVERAGE_RESOLUTION_S=0.0001 at :73); reached from scripts/validate_powermetrics_fiducial.py:1509`
- failure_scenario (verbatim): Quiet-window pre-calibration hits clock_anchor_unresolved (a recorded real production condition — runbook SS10/SS13.1) and the capture's loss surface is flat enough that the 1.5 s x 1.5 s rectangle bisected to 0.1 ms cells (~2.25e8 cells/pulse x 59 pulses) never prunes: the writer computes for hours holding the writer lease, the chain has no watchdog, the operator is forbidden to touch the machine (SS5C), and the funded window burns with no governed exit ever emitted; a consumed one-launch arm capability is lost with it. Witnessed 3x >600 s on this host with the repo's own crash-matrix fixture (SIGABRT stack captured inside _pulse_loss_cell_lower_bound) while a near-identical run finished in 10.7 s — unbounded, data-dependent cost on a refusal path. Consumption soundness is NOT affected (evidence already forced invalid; SIGKILL leaves a fail-closed pending/claimed state — proven by passing witness tests). Also blocks tests.test_calibration_writer_crash_matrix from completing on this audit host (its 600 s subprocess ceiling aborts).

### F2 [should_fix] readiness/session-status crash with an unregistered raw traceback when the ledger parent directory is missing
- file_line: `joulewise/calibration_ledger.py:2885 (resolve_ledger_lease_identity parent .resolve(strict=True)) via writer_lease_is_live, uncaught in scripts/recover_calibration_ledger.py:412/:321 (only CalibrationLedgerError is caught)`
- failure_scenario (verbatim): Operator runs the SS5-amendment E-8 readiness command (or session-status) with $CALIBRATION_LEDGER mis-pointed at a path whose parent does not exist (typo, unmounted volume, fresh clone before any ledger exists): FileNotFoundError traceback, exit 1, no registered refusal code, no SS10 row — an unmapped failure that ends the night by SS5C rule 4 instead of a correctable governed refusal. Executed witness: E-8 before E-9 in a fresh scratch checkout crashes exactly this way, while E-9 then succeeds because the lease mkdirs the parent. Bounded: the frozen plan pins CALIBRATION_LEDGER to /Users/edr/code/JouleWise/runs/... which exists, so the documented night is unaffected; inspect handles the same state cleanly (genesis inspection).

### F3 [nit] Runbook needs_pin_commit bullet is unscoped vs the by-design PHYSICAL_AHEAD pre-slot relation
- file_line: `docs/phase_2/window_runbook.md:421-423 vs joulewise/calibration_ledger.py:4949`
- failure_scenario (verbatim): SS5 amendment says 'Treat needs_pin_commit: true as desk work that ends a 2 a.m. attempt', but the pre-slot readiness (diagnostic and enforcing) reports needs_pin_commit=true whenever ready, because PHYSICAL_AHEAD is the REQUIRED mid-bracket relation (pin deliberately stays at the pre-reservation head until post finalization). A tired operator reading the bullet mechanically at pre-slot aborts every legitimate resume. The adjacent bullet (phase-appropriate pin relation) is correct; the needs_pin_commit bullet should be scoped to pre-reserve/terminal.

### F4 [nit] Idempotent re-reservation returns status:reserved without re-printing calibration_pre_reserve_authorized
- file_line: `scripts/reserve_calibration_window_bracket.py:172-201 (event printed only on ready readiness; fall-through resume path appends idempotently)`
- failure_scenario (verbatim): SS5C requires both the authorized event and status:reserved; after an accidental double-run of E-9 the second invocation (readiness blocked by the now-open session, session-status found, idempotent completed-op return) prints status:reserved with no authorized event — an operator matching the runbook's required markers sees a discrepancy on a harmless governed resume. Executed: rerun was byte-identical, exit 0. Runbook already forbids re-reservation on restart; document the resume output shape.

## WORK ORDERS (verbatim)

- WO-L2-1 (for L2-1): add a rigorous work budget to _accepted_region_projection (cell-count or wall bound); on exhaustion fail closed with a new detection reason (e.g. detection_nonconvergent -> status invalid, never a bound), and/or skip full-resolution projection entirely when clock anchor is unresolved (the artifact is already forced invalid — full-resolution region evidence buys nothing). Regression: replay the degenerate crash-matrix trace; the crash-matrix module then completes on any host.

- WO-L2-2 (for L2-2): wrap the readiness/session-status/validate-slot dispatch in recover_calibration_ledger.py (and/or resolve_ledger_lease_identity) to convert missing-parent OSError into the registered physical_ledger_unreadable/unsafe_lock_inode refusal envelope so every diagnostic surface fails closed with a SS10 row.

- WO-L2-3 (nit): scope the runbook SS5-amendment needs_pin_commit bullet to pre-reserve/terminal phases (pre-slot's ready state is physical_ahead by design).

- WO-L2-4 (nit): document the reservation CLI's idempotent-resume output shape (status:reserved without a re-printed authorized event) in SS6.

## ED-QUALIFICATION ROWS (verbatim)

- EDQ-L2-1 (stable capability): execute tests.test_calibration_writer_crash_matrix to completion on the quiet bench at the audit-baseline head and record pass + wall time. On the audited host it cannot complete (finding L2-1); CI exclusive-job green at the baseline head corroborates but a bench execution closes the row with local evidence.

- EDQ-L2-2 (stable capability; runbook-mandated non-delegable): the SS5C lead live verification on the exact reviewed measurement checkout — frozen plan's literal readiness-validator command plus the complete under-lease synthetic rehearsal (real reservation CLI --execute + production writer lifecycle through BOTH slots against a synthetic root), requiring the D-134 dry-run receipt PASS/NOT_APPLICABLE with the reviewed HEAD + committed-pack digest. This audit replayed the equivalent in scratch; the runbook requires it on the production checkout with the frozen plan, which no sandboxed seat can perform.

## UNEXECUTED OBLIGATIONS (verbatim)

- Full tests.test_calibration_writer_crash_matrix module on THIS host (16 tests; 6 executed locally, all governed-exit/lease/capability classes PASS): completion is blocked by finding L2-1's degenerate-cost case exceeding the harness's 600 s subprocess ceiling. Corroboration: CI runs it as a dedicated exclusive job (ci.yml:115) and PR #149 — the baseline head — merged green.

- Two documented suite skips requiring lead-reviewed D-079 import fixtures at /private/tmp (absent here): test_production_path_authenticates_real_76_receipt_import_prefix, test_d079_issued_artifact_mode_is_deterministic_and_write_explicit.

- calibration_ledger.py historical-import/bootstrap block (~lines 2205-2727) and snapshot/parse internals read behaviorally (their tests green), not line-by-line.

- joulewise/calibration_bracketing.py evaluation half (evaluate_calibration_bracket, calibration_bracket_for_bundles) — L4 quantitative-pipeline seat's scope; only the acceptance-authentication half audited here.

- Real-time-scale live writer run and sudo powermetrics behavior — hardware; ED rows / seat L3.

