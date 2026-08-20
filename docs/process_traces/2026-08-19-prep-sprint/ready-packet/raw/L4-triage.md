# RAW TRIAGE EXTRACT — L4-quantitative-claim-pipeline

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L4-quantitative-claim-pipeline`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 24/27 (evidence_universe_count=27)
- findings: 4; falsifiers: 4

## FINDINGS (verbatim)

### F1 [blocker] Margin recorder cannot read the re-specced frozen floor-pack extraction specs — ALPHA/BETA close-out halts deterministically at runbook section 11
- file_line: `joulewise/window_duration_margins.py:897 (session) + :394 (spec read); cause joulewise/authentication_io.py:179,214; missing authorization mirror of scripts/mint_floor_artifact_generalized.py:1758-1759,3683`
- failure_scenario (verbatim): A funded quiet window collects ALPHA cleanly; the operator runs the exact runbook section-11 command; the recorder opens its V2AuthenticationReadSession and reads the pack-pinned spec, which since the D-133 cl.4 re-spec carries estimator_registration in all comparative cells; the session's reserved-vocabulary rule refuses (executed: REFUSE authoritative_input_invalid, exit 2, no receipt); 'REFUSE stops close-out without writing a receipt' — backup/extraction never run under the mandated order, the window cannot be called claim-bearing, and the standing constraint 'collection close-out gates on the WO-COLLECTION-MARGIN-01 receipt' is unsatisfiable on every attempt. Only the mint authorizes governed-spec vocabulary (allow_governed_extraction_spec); the recorder never does. The committed census tests (tests/test_window_duration_margins.py:213,514) model 'real floor pack cell shapes' WITHOUT the estimator vocabulary, so the suite is green while the real seam is broken — the charter's producer-gap type specimen.

### F2 [should_fix] GAMMA contrast both-gates consumption route is unbuilt: prospective manifest refused by the loader, sole frozen-v3 builder hard-pinned to the splitwise campaign
- file_line: `joulewise/analysis_manifest_v3.py:34,48,441-447 (ROOT_ORDER_SHA256 splitwise pin, swdec-contrast run-id grammar, 40 entries) vs configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1 (80 rows, d117c15v7-* ids); joulewise/analysis_engine/inputs.py:554-569`
- failure_scenario (verbatim): After a funded GAMMA window, no committed code can produce the frozen v3 analysis manifest the engine requires: load_manifest refuses joulewise.analysis_manifest.v3.prospective (correctly), build_analysis_manifest_v3 refuses the GAMMA order manifest (wrong pinned sha, wrong run-id grammar, 40 vs 80 entries), and zero production code references the d117c15v7 grammar. The funded p256 contrast — the reason the packs re-specced to the 1.869502 J floor — cannot mechanically reach evaluate_claim's both-gates logic; the between-window re-run decision for GAMMA cannot be made on claim outcomes inside the span. Fails closed (no wrong consumption possible), but the missing builder must be registered and its pre-registration binding (prospective contrast census mechanically bound into the built manifest) designed before the GAMMA window.

### F3 [should_fix] Margin-receipt consumption never mechanically binds to the FROZEN pack: a repinned truncated pack yields a plausible PASS and the receipt validator accepts a truncated sha-repaired receipt
- file_line: `joulewise/window_duration_margins.py:988 (validator proves internal consistency only); docs/phase_2/window_runbook.md:1449-1473,1536 (close-out records path+SHA, no pack-binding cross-check)`
- failure_scenario (verbatim): Executed F3-B/F3-C: a pack root whose spec, plan_tree, and sidecar are consistently re-pinned after dropping a comparative cell produces a PASS receipt over the truncated census, and a post-hoc truncated receipt with recomputed cell_inventory_sha256 passes validate_window_duration_margins_receipt. Both leave fingerprints (pack_tree_sha256/registry_source_sha256 differ from the frozen pack), but no close-out step compares them to the frozen pack's committed plan_tree.sha256 — a tired operator pointing --pack-root at a stale draft copy (the registered F-C/F-F CUSTODY_ROOT-ambiguity family makes this realistic) gets a plausible PASS bound to the wrong census, and close-out proceeds.

### F4 [nit] validate_floor_artifact's recomputation tolerance accepts a one-ULP-understated floor; tamper-evidence rides on byte custody, not numeric revalidation
- file_line: `joulewise/detection_floor.py:2021 (_close, min(~1e-12 relative, 1e-6)); enforcing layers scripts/mint_floor_artifact_generalized.py:2484-2490 (exact Decimal) and joulewise/analysis_engine/artifact.py:943 (file_sha256 binding)`
- failure_scenario (verbatim): Executed: a one-ULP downward perturbation of the committed mint1 artifact's comparative floor passes validate_floor_artifact with zero errors. Not exploitable end-to-end today because the mint's postcollection/binding equalities are exact-Decimal (refused all my floor-value ULP attacks) and every claim-side consumption re-authenticates artifact bytes against a bound sha256 — but nobody should ever cite validate_floor_artifact alone as tamper-proofing, and any future consumption path that skips the sha binding would inherit a ~1.9e-12 J silent understatement window.

## WORK ORDERS (verbatim)

- WO-L4-1 (BLOCKER cure): teach joulewise/window_duration_margins.py to authorize governed-spec vocabulary for exactly the one plan-tree-pinned extraction-spec path before its authenticated read (mirror the mint's _allow_governed_extraction_spec single-path pattern; GAMMA analysis-manifest path must NOT be authorized), plus a committed census regression that reads the REAL frozen spec bytes from configs/floor_mint/ (read-only) so the synthetic-fixture/real-vocabulary seam can never silently diverge again; fix the misleadingly named test_census_discovers_all_three_real_floor_pack_cell_shapes to carry estimator/estimator_registration/calibration_basis fields. Full C-028 gauntlet; re-run the three_night_freeze_manifest 'D-133 item (1)' checklist row against frozen bytes, since its assertion was evidently never executed against them.

- WO-L4-2: register and author the D-117 GAMMA frozen-v3 analysis-manifest production path — either generalize build_analysis_manifest_v3 over a pack-declared order/grammar or add a D-117-pinned builder — with the prospective manifest's contrast census (contrast IDs, members, config pins, metric) mechanically bound into the built manifest so pre-registration integrity is enforced by code, not operator discipline; sequence before the GAMMA window or as an explicitly registered post-window dependency with the re-run-decision implication stated.

- WO-L4-3: add one mechanical close-out check to runbook section 11/12: the reported margin receipt's pack_tree_sha256 must equal the frozen pack's committed plan_tree.sha256 sidecar value (and record that comparison in the section-12 close-out fields); optionally have the recorder CLI print the plan-tree sha it bound so the check is a single diff.

- WO-L4-4 (record-only): document that validate_floor_artifact numeric revalidation is defense-in-depth behind byte custody (one-ULP understatements pass _close); any new floor-artifact consumption path must bind file_sha256 like analysis_engine/artifact.py:943 or use the mint's exact-Decimal equality.

## ED-QUALIFICATION ROWS (verbatim)

- ED-QUAL-L4-1 (network capability, not hardware/sudo — emitted so it is not silently skipped): execute scripts/replay_d117_decisive.sh at the audited head in any tap block with network — anonymous release download, digest gate, governed hydration, census byte-compare, then the single decisive no-skip mint test (~3h35m on the M3 Max). Stable evidence; closes the two skipped decisive tests and the full-fixture leg of the mint's exact-equality proof.

## UNEXECUTED OBLIGATIONS (verbatim)

- Full canonical suite (python3 -m unittest discover -s tests) on BOTH interpreters at the baseline head — I executed 13 focused in-scope modules on python3.13 and 2 on python3.11; repo CI green at ac3fe1d corroborates the rest but is not my execution.

- The decisive full-fixture production proof (scripts/replay_d117_decisive.sh; test_coordinated_report_and_pin_change_refuses_against_floor_evidence and the split-partition test, the 2 skips in my mint suite run) — requires network download of the custody-store release asset and ~3h35m; not executable in this no-network sandbox.

- Deep line-audit of joulewise/reduce.py (3983 lines) and joulewise/whole_window.py (5348 lines) beyond interface depth — covered by their full test modules (123/15/56 OK), by the margin recorder's live reuse of reducer internals, and by the verdict-writer/basis-reader seam check I did execute; the numeric interior was not line-read.

- End-to-end synthetic collected-window rehearsal through reduce -> verdict -> mint -> claim consumption — seat 10's charter (SACRIFICIAL FULL LIFECYCLE); not duplicated here. Note seat 10 must expect my finding 1 to fire if its rehearsal includes the section-11 margin step on a registration-bearing spec.

- MET-VERDICT-ADJ-01 adjudication status of the whole-window verdict machinery — historical gate, not re-adjudicated by this seat.

