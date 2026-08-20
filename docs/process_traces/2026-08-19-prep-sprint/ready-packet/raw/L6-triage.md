# RAW TRIAGE EXTRACT — L6-SEAM-READER-A

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L6-SEAM-READER-A`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 34/40 (evidence_universe_count=40)
- findings: 8; falsifiers: 5

## FINDINGS (verbatim)

### F1 [blocker] B1 — The T-0 evidence author's own inputs have no producer: no tool, no runbook step, no packet step
- file_line: `joulewise/arm_readiness_evidence_t0.py:42,132-139,506,556,601; docs/phase_2/window_runbook.md:812-827`
- failure_scenario (verbatim): The funded night reaches §5C's post-E-9 authoring step; author_arm_evidence_t0.py refuses evidence_author_t0_clock_attestation_missing (demonstrated live in probe P3) because nothing has created CUSTODY/PACK_ID/arm_readiness.t0.inputs/ — the author requires clock-attestation.json, arm-context.json, launch-manifest.json and six command captures (clock-prior-state, clock-disable, quiet-mac-prep, prewindow-check, ledger-readiness, ledger-reservation) as canonical JSON with boot-bound monotonic-ns fields no human can hand-produce; no repo tool writes joulewise.arm_readiness_t0_command_capture.v1 (grep: only the author itself references the schema), the runbook never names arm_readiness.t0.inputs, and the FINAL arm packet predates the author entirely. Night ends NO-GO — or worse, the operator hand-crafts nine JSON files at 2 a.m., the exact anti-pattern the readiness machinery exists to prevent.

### F2 [blocker] B2 — Committed freeze evidence is already past its 24 h monotonic horizon; every future window requires an undocumented full freeze-refresh lane
- file_line: `joulewise/arm_readiness.py:2943-2975,3712-3719; docs/phase_2/window_runbook.md:726-742,812-830`
- failure_scenario (verbatim): Live reading on the freeze boot session: now-monotonic 1,996,764 s > valid_until 1,986,799 s — all 11 generic PACK evidence receipts frozen 2026-08-13 are expired. generate_arm_receipt folds evidence expirations into the arm receipt's valid_until (min(...)), so any arm receipt issued now is expired at birth; verify/consume then refuse readiness_record_expired (arm_readiness.py:3952-3955). Cure = re-author 11 receipts + new freeze receipt + plan-tree re-pin + commit + review + fresh dry-run, same boot session as ARM and ≤24 h before it — a cycle no operative document names: §4 presents freeze as 'before quiet time' desk work, §5C's re-author rm covers only the two T-0 namespaces, and the reboot-fence paragraph says only 'generate new receipts'. Fails closed at every probe point, so no consumption unsoundness — but a required output (a valid GO arm receipt) currently has no producible path under the frozen packs + current runbook alone, and the refresh commits void the audit baseline per charter amendment 12.

### F3 [should_fix] S2 — D-117 two-stage mint freeze: the stage-1 desk pin artifact (floor_mint_pin_requirements.v2) has no committed instance and nothing fails closed on its absence
- file_line: `scripts/mint_floor_artifact_generalized.py:1391-1392; docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:368-403`
- failure_scenario (verbatim): DESIGN-MEMO §Two-stage mint freeze requires desk-time pins in a non-mintable pin_requirements.v2 artifact before collection; `git ls-files | grep pin_requirements` returns nothing, and the mint's only reference is a guard refusing it AS a pinset (mint_floor_artifact_generalized.py:1391-1392). A final pinset constructed entirely post hoc after the window would be mechanically indistinguishable from one honoring the two-stage freeze — the pre-registration value the ruling ordered is silently absent.

### F4 [should_fix] S3 — §12's postcollection backup receipts have no producer: backup_runs.sh emits no receipt and no hash
- file_line: `scripts/backup_runs.sh:38-42,58-67; docs/phase_2/window_runbook.md:1475-1481,1518-1526`
- failure_scenario (verbatim): Close-out requires 'each successful postcollection backup receipt path and SHA-256 … separately for the claim and bound roots'; backup_runs.sh writes only an unhashed one-line backup.log entry and §11 shows a single claim-root invocation. On the night the operator either cannot complete §12 as written or improvises an unhashed record; nothing downstream gates on backup, so a failed backup surfaces only in the human record.

### F5 [should_fix] S4 — The FINAL arm packet (the operator's night document, cited by the audit-baseline manifest) is stale against the baseline runbook
- file_line: `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md:480 (off-repo custody)`
- failure_scenario (verbatim): The packet's E-9a jumps from E-9 straight to `generate_arm_readiness.py arm` with no T-0 authoring step, never mentions arm_readiness.t0.inputs, and still says 'Expect a refusal tonight unless §0.6 has been resolved' — §0.6 is resolved by the T-0 author at this baseline. An operator following the packet verbatim arms without authored T-0 evidence and gets a wall of readiness refusals with no packet row explaining them.

### F6 [nit] N1 — window_duration_margins_receipt.v1 has no machine consumer; §11 ordering is unenforced
- file_line: `joulewise/window_duration_margins.py; scripts/record_window_duration_margins.py:19`
- failure_scenario (verbatim): Only scripts/record_window_duration_margins.py (writer) and tests reference the schema; extraction and mint proceed regardless. A tired operator who skips §11 loses the comparative-cell margin record with no mechanical signal — discovered only if a human audits the close-out record.

### F7 [nit] N2 — PRIVILEGE_INSTALLATION evidence kind has no producer anywhere in the repo
- file_line: `configs/arm_readiness/d117_row_registry_v1.json (privilege.* rows); joulewise/arm_readiness.py:2289-2303`
- failure_scenario (verbatim): Harmless while clock_route stays frozen at MANUAL (the four privilege.* rows evaluate NOT_APPLICABLE — confirmed in the P1 census); any future arm context using the clock-helper route makes four rows applicable with no production path, guaranteeing NO-GO with no tooling recourse. Record so the gap is chosen, not discovered.

### F8 [nit] N3 — The arm-time freeze-evidence replay skips the monotonic-horizon check; defense is one hop downstream
- file_line: `joulewise/arm_readiness.py:2955-2960 vs 3712-3719,3952-3955`
- failure_scenario (verbatim): _freeze_evidence_for_arm authenticates freeze evidence with expected_boot_session_id but no now_monotonic_ns, so FREEZE_AND_ARM rows can show PASS from horizon-expired evidence inside the arm receipt; the expiry is enforced only via the valid_until min-fold plus verify/consume. Any future direct consumer of row verdicts (none today) would read PASS rows from expired evidence.

## WORK ORDERS (verbatim)

- WO-L6-1 (cures B1, part of S4): build scripts/capture_t0_step.py (or equivalent) that wraps each §5C E-step command and writes its joulewise.arm_readiness_t0_command_capture.v1 JSON into arm_readiness.t0.inputs/ with the boot-bound monotonic fields, plus templates/authoring for clock-attestation.json, arm-context.json, launch-manifest.json; amend §5C to name the directory and the nine files as an explicit E-step

- WO-L6-2 (cures B2): add the governed freeze-refresh lane to §4/§5C — state plainly that PACK evidence is valid same-boot-session and 24 h from authoring, that ARM therefore requires the freeze lane re-run on the window day (re-author → re-freeze → commit → review → re-dry-run, in that order, before §5A), and reconcile with the charter's final-head invalidation (the refresh commit defines the head the T-0 GO binds)

- WO-L6-3 (cures S4): regenerate the arm packet from the baseline runbook after WO-L6-1/2 land; retire the 'expect a refusal unless §0.6' row

- WO-L6-4 (cures S2): commit stage-1 floor_mint_pin_requirements.v2 artifacts for alpha and beta (and the gamma consumer-pin requirements), or record a ruling that the packs' extraction specs + plan trees subsume stage 1 — either way make the mint or the close-out check their existence

- WO-L6-5 (cures S3): make backup_runs.sh emit a hashed per-root backup receipt (or amend §12 to match what the tool produces); optionally give the duration-margins receipt (N1) a consumer in the same close-out check

## ED-QUALIFICATION ROWS (verbatim)

- ED-QUAL-L6-1 (stable capability, any tap block): execute the T-0 authoring path live on the measurement Mac — once the B1 capture helper exists, run the six E-step captures + clock attestation + launch manifest into arm_readiness.t0.inputs/ and author_arm_evidence_t0.py end-to-end under real passwordless-sudo powermetrics (POWERMETRICS_PROBE) and real systemsetup state (CLOCK_PROBE), confirming all 15 receipts author and a same-boot `generate_arm_readiness.py arm` reaches row evaluation. This lens could only prove the refusal side (P3) from the sandbox; the PASS side of the arm-plane producer seam needs Ed's machine and sudo.

- ED-QUAL-L6-2 (stable capability, desk, no sudo but Ed's checkout): one full freeze-refresh rehearsal timed against the 24 h/same-boot coupling of B2 — re-author pack evidence, re-freeze, commit, dry-run, and measure the wall-clock of the lane so the window-day schedule in the WO2 runbook amendment is grounded in an observed duration, not an estimate.

## UNEXECUTED OBLIGATIONS (verbatim)

- Did not execute generate_arm_readiness.py freeze/dry-run/arm/consume as CLIs end-to-end (freeze mutates pack bytes; arm requires the B1 inputs that do not exist; tree had to stay byte-identical) — authentication internals were exercised by direct calls instead

- Did not run the collection-plane producers live (run_campaign, validate_powermetrics_fiducial, reserve_calibration_window_bracket) — no live measurement permitted; their seams verified by contract+code reading only, deep audit owned by seats L2/L3/L4

- Did not execute extraction→mint on a synthetic window (seat L10's sacrificial lifecycle owns this); mint consumption verified by import/code reading only

- Did not deep-trace the claims-index/claims-lint consumption seam beyond identifying producer and consumer files (post-paper plane, thinner risk)

- Did not resolve whether the t0.ledger_reservation predicate's expected_plan_sha256 (pack plan_tree sha) and the reservation's FROZEN_PLAN sha are the same identity — flagged to seat L2 (calibration acquisition) rather than guessed

- Could not read the FROZEN_PLAN/window.env instance (off-repo by design; none exists yet for the next window)

