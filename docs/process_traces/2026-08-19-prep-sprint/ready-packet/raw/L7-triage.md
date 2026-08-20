# RAW TRIAGE EXTRACT — L7-SEAM-READER-B-EXECUTION

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L7-SEAM-READER-B-EXECUTION`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 21/25 (evidence_universe_count=25)
- findings: 3; falsifiers: 7

## FINDINGS (verbatim)

### F1 [should_fix] Frozen PACK-namespace evidence is consumed at arm/verify/consume without its declared monotonic horizon being checked — and all 33 frozen receipts' horizons have ALREADY lapsed
- file_line: `joulewise/arm_readiness.py:2957 (also arm at 3628 and verify/consume at 3801 vs freeze-time enforcement at 3021-3027)`
- failure_scenario (verbatim): Council declares READY; Ed arms tonight on the un-rebooted machine. _freeze_evidence_for_arm re-authenticates the 33 pack evidence receipts by bytes + boot session only (now_monotonic_ns never passed), so the arm proceeds even though every receipt's valid_until_monotonic_ns lapsed ~2.8h before my probe (verified live: now=1.997e15 ns > valid_until=1.9868e15 ns on the same boot, 33/33 across the three packs). A later reviewer reading the receipt bytes finds attestations consumed past their own declared validity — the readiness chain is impeachable post-hoc, the exact 'output that neither traces cleanly nor fails closed' the charter hunts. Either the horizon must be enforced on the arm path (which then mandates a pre-arm re-author + re-freeze ceremony, since the current evidence is void) or PACK-namespace valid_until must be authoritatively documented as freeze-time-only semantics before any arm consumes these bytes.

### F2 [should_fix] Mandatory pre-arm sequence is undocumented: the runbook's E-step tool does not exist at the frozen measurement-checkout head, and advancing the checkout stales the recorded §5C dry-run receipt
- file_line: `docs/phase_2/window_runbook.md:805-838 (author_arm_evidence_t0.py E-step) vs `git ls-tree 49dcc49 scripts` (tool absent at the frozen head); RUN_STATE.md:31-33`
- failure_scenario (verbatim): The measurement checkout /Users/edr/JouleWise-measurement-20260813 sits at 49dcc49, where scripts/author_arm_evidence_t0.py (the mandated T-0 E-step, merged in #149) does not exist and the arm generator still carries the launch-blocking 15-row ARM_ONLY gap. Arming there refuses. Arming at the current reviewed head requires advancing the checkout — which by the runbook's own staleness rule (and test test_dry_run_becomes_stale_after_later_head) voids dry-run-0001 (head-bound to the 49dcc49-era head; pack digests drifted 6246b6...->f4c02c8a... because #149 edited all three packs' generate_configs.py). No standing doc (RUN_STATE T7, ed-qualification-session.md, 70h plan) states the required sequence: advance checkout to final reviewed main -> lead re-runs the §5C dry-run to a fresh PASS receipt -> then E-steps. A tired operator following RUN_STATE's 'NO REBOOT preserves the frozen evidence' hits an unexplained refusal chain at night, or improvises.

### F3 [nit] `joulewise reduce` writes its re-reduction artifact into the invoker's CWD by default
- file_line: `joulewise/cli.py:1873-1875`
- failure_scenario (verbatim): Observed live: reducing a TMPDIR bundle from the repo root dropped example-mock-local.summary_metrics.rereduced.0.5.2.json into the checkout. An operator reducing from the measurement checkout would dirty it — and a dirty measurement tree is itself an arm refusal. The guard against writing inside the bundle exists; a default outside the current directory (or a required --output) would remove the pollution path.

## WORK ORDERS (verbatim)

- WO-L7-1 (pre-arm, needs magistrate ruling): resolve the PACK-evidence horizon asymmetry — either pass now_monotonic_ns in _freeze_evidence_for_arm (then schedule the mandatory re-author + re-freeze ceremony before ALPHA arm, since all 33 receipts are lapsed) or document PACK-namespace valid_until as freeze-time-only semantics in the runbook §5C and the receipt schema notes, with an explicit disposition recorded for the lapsed 08-13/14 receipts

- WO-L7-2 (pre-arm, doc + checklist): add the explicit sequence to RUN_STATE/ed-qualification-session/runbook §5C entry gate: (1) advance the measurement checkout to the final reviewed merged main (clean, exact match), (2) verify boot session unchanged (DA90818C...), (3) lead personally re-runs the §5C dry-run at that head and requires a fresh PASS receipt binding the new head + new pack digest, (4) only then the E-steps; correct RUN_STATE's 'NO REBOOT preserves the frozen evidence' to name the dry-run staleness and the #149 pack-byte drift

## ED-QUALIFICATION ROWS (verbatim)

- ED-L7-1: prewindow_check.sh --wait to READY plus quiet_mac_prep.sh on the freed quiet machine (stable capability; my execution proves the gate correctly BLOCKS while any agent fleet runs, so READY can only be demonstrated in an Ed/quiet block)

- ED-L7-2: fresh §5C lead dry-run PASS at the final reviewed head on the measurement checkout — executes the real reservation CLI --execute and the production ledger-writer lifecycle through both slots under lease (the recorded dry-run-0001 is head-stale after any checkout advance; a new PASS receipt binding the final head/digest is required desk evidence before arm)

- ED-L7-3: live sudo powermetrics fiducial calibration seam (validate_powermetrics_fiducial --allow-live producing instrument_evidence.json consumed by the chain's §5B jq screen) — unexercisable without sudo + quiet machine; covered by the charter's sampler checklist but named here because it is the one producer->consumer edge in the §6 chain I could not execute or observe in any test

## UNEXECUTED OBLIGATIONS (verbatim)

- Live capture path: validate_powermetrics_fiducial --allow-live, MLX member collection, --arm-quiet-mode display arming (no sudo / no live measurement in this sandbox) — ED rows

- tests.test_calibration_exits (2,036 s) and tests.test_calibration_writer_crash_matrix (5,317 s) — CI-exclusive modules not re-run in this seat's budget; last known green on the #149 merge CI

- The decisive full-fixture mint proof (replay_d117_decisive.sh / test_coordinated_report_and_pin_change_refuses_against_floor_evidence) — requires a GitHub release download; no network. Skip marker observed and documented in batch B

- Whole-window verdict and extract_detection_floors CLIs against a real collected corpus (runs/ corpora are off-repo); exercised only through their test fixtures

- reserve_calibration_window_bracket.py --execute against the production ledger (exercised only inside the dry-run generator and tests)

- quiet_mac_prep.sh (mutates display state)

- a9/a10 retained characterization basis — seat 11's scope, excluded from my universe count

