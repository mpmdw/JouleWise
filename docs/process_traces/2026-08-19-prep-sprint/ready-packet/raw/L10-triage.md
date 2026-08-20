# RAW TRIAGE EXTRACT — L10-SACRIFICIAL-FULL-LIFECYCLE

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L10-SACRIFICIAL-FULL-LIFECYCLE`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 15/18 (evidence_universe_count=18)
- findings: 5; falsifiers: 13

## FINDINGS (verbatim)

### F1 [blocker] Frozen packs' claim-consumption edge is unbuilt: analyze-claims refuses the packs' v3.prospective manifests, the U7-designed prospective builder/validator do not exist, and the final-v3 wire is hard-pinned to splitwise
- file_line: `joulewise/analysis_engine/inputs.py:556-568; joulewise/analysis_manifest_v3.py:613,630-663; configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:2`
- failure_scenario (verbatim): The funded gamma window collects clean, the verdict passes, alpha/beta floors mint into the aggregate — and the contrast claim cannot be consumed: analyze-claims refuses 'unsupported analysis manifest schema_version: joulewise.analysis_manifest.v3.prospective' (executed); validate_analysis_manifest_v3 hard-requires design_id splitwise_decode_cross_model_abba_v1, the splitwise generator path/plan sha, exactly two stages and n=10, so no hand-authored final D-117 manifest can validate either; grep finds zero implementations of the U7-specified build_prospective_analysis_manifest_v3 / validate_prospective_analysis_manifest_v3 and no postcollection-attachment finalizer; no TASK_QUEUE row tracks this edge. The window is spent and its REQUIRED OUTPUT cannot trace through a claim consumer without landing new code post-hoc, colliding with L1 same-session custody discipline.

### F2 [should_fix] Runbook §11 extraction command as frozen refuses at argparse: --evaluation-basis-sha256 without the co-required --consumption-semantics-id
- file_line: `docs/phase_2/window_runbook.md:1485-1491 vs scripts/extract_detection_floors.py:100-106`
- failure_scenario (verbatim): At close-out the operator pastes the literal §11 command; it exits 2 with '--evaluation-basis-sha256 and --consumption-semantics-id are required together' (executed). A tired operator must improvise the exact semantics id (d078_minted_envelopes_v1) at 4 a.m. — precisely the hand-improvisation the runbook forbids elsewhere — or close-out stalls.

### F3 [should_fix] Runbook §11 margins-recorder identity mismatch: --pack-identity "$WINDOW_ID" (window_a9_YYYYMMDD convention per §4) can never satisfy the recorder's plan-derived window_id requirement
- file_line: `docs/phase_2/window_runbook.md:1456-1461 (with §4 window.env WINDOW_ID convention at line 186) vs joulewise/window_duration_margins.py:374-379`
- failure_scenario (verbatim): First §11 command on the night: the recorder REFUSEs {reason: pack_identity_invalid} for any identity other than the pack plan-tree's window_id (executed with both the runbook-style id and the pack dirname; only plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1 advances). REFUSE stops close-out by §11's own rule; the operator must reverse-engineer identity semantics mid-night.

### F4 [should_fix] L1 same-custody-session limitation structurally conflicts with the three-window design's cross-session floor consumption; FLOOR-BIND-01 is READY but unclosed
- file_line: `TASK_QUEUE.md:477 (L1 fence); docs/phase_2/window_runbook.md:61-66`
- failure_scenario (verbatim): Even with the manifest edge built, the gamma analysis must consume alpha/beta floor artifacts extracted and minted in EARLIER custody sessions; L1 ('claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction') renders that consumption non-claim-bearing until FLOOR-BIND-01 lands or a prospective ruling licenses an L1-compatible cross-window procedure. No such ruling or closure is scheduled before the windows.

### F5 [nit] backup_runs.sh counts campaign_manifests/ as a bundle in operator-facing output (reported 5 bundles for a 4-member window)
- file_line: `scripts/backup_runs.sh:25-36`
- failure_scenario (verbatim): §12 requires member counts by distinct bundle ID; an operator cross-checking the backup line (5) against the member count (4) sees a discrepancy and burns close-out time chasing a phantom bundle. Cosmetic; the copy itself was complete and correct (executed).

## WORK ORDERS (verbatim)

- WO-1 (closes blocker F1): implement and land the D-117 analysis-manifest consumption edge before any window is spent — build_prospective_analysis_manifest_v3 / validate_prospective_analysis_manifest_v3 per the U7 spec (docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md §'Prospective analysis-manifest repair'), plus the postcollection-attachment finalizer (passed verdict sha, evaluation-basis sha, bracket-binding sha, terminal ledger head, aggregate floor-artifact sha) producing a manifest analyze-claims accepts, generalizing the final-v3 wire beyond its splitwise pins without changing splitwise bytes; add refusal regressions for missing/stale attachments

- WO-2 (closes F2+F3): repair runbook §11 — add --consumption-semantics-id d078_minted_envelopes_v1 to the extraction command, and replace --pack-identity "$WINDOW_ID" with the pack's plan-derived window_id literal (plan-d117-…-v1) per pack, or define WINDOW_ID as that literal for D-134 nights in §4

- WO-3 (closes F4): close FLOOR-BIND-01 before gamma claim consumption, or obtain a prospective magistrate ruling licensing an L1-compatible cross-window floor-consumption procedure (recorded before the plan freeze, not improvised after collection)

- WO-4 (nit F5): make backup_runs.sh exclude campaign_manifests/ from its bundle count or reword the operator-facing line

## ED-QUALIFICATION ROWS (verbatim)

- ED-L10-1 (stable capability, any tap block, no live measurement): one desk replay of the complete post-collection chain against a RETAINED real window corpus (a9/a10 custody, Ed-held off-repo) — whole-window verdict (expect passed), duration-margins recorder, backup, governed extraction with the matching spec and basis sha — pasting every command and exit code. This supplies the CLI-level PASSED-basis positive proof that no sandboxed desk rehearsal can produce, because a passing basis requires real calibration-bracket, NEG-8 corpus, and reference-triplet evidence that only a live sudo/powermetrics window can mint.

## UNEXECUTED OBLIGATIONS (verbatim)

- §9 D-100 salvage-dangler verdict dispatch (--consumption-semantics-id salvage_dangler_exclusion_v1 with membership binding + salvage closure) — not exercised at the CLI (no synthetic salvage closure); covered only by suite evidence

- §10 --record-supersession quarantine/supersession flow — not exercised at the CLI

- v2 multi-cell aggregate mint route (--v2-input-manifest + schema_v2 pinset), the route the gamma consumption depends on — not exercised at the CLI; covered by tests/test_mint_floor_artifact_generalized.py (passed)

- Waiver path: --waivers producing a 'flagged' verdict and extraction refusing the flagged basis — not exercised

- CLI-level PASSED-basis end-to-end (verdict passed → margins PASS → extraction admitted → mint minted) — impossible from the desk without a real window corpus; see ED-QUALIFICATION row

