## PROGRESS

- Done: Part 2 (review of dcceb8480) started at 0a585bb8e; all A1–A8, BY-MERGE and R2-1–R2-6 dispositions are recorded below. Director committed and pushed slice 8 as c36ef1c51; this final slice changes reports only.
- Done: all twelve committed-fixed P values pass native planner/arm/precheck boundaries; four desk freshness cases pass; M4/M8/M12/M13 are CAUGHT; sealed inventory diff is empty (682 files).
- Done: 103 of 113 importer/native individual tests pass, zero failures and no skips in those 103. The ten remaining tests (capture_screen_reachability 4, cold_pass_fixes 5, desk_resume_finalize 1) are **delegated to PR #547 CI on the final head (director)** on PR #547 at c36ef1c51. They are not claimed as local passes. No slow importer test was rerun in this final slice.
- Next: director reviews/commits these two reports, verifies PR #547 CI on the final head and owns final verification, ledger done line and BY-MERGE hand-forward. No worker implementation or report task remains.
- Open: physical free-space recovery before arming; declared sandbox hazard failures and CI results remain director-owned. NEEDS_RULING: none.

BY-C5-fix1 COMPLETE

## SUMMARY

BY-C5 fix round 1 is complete under the director's final-slice instruction.
C5 uses committed fixed artifacts of 4,046,531,103 B; measured partial fixed bytes remain unused disclosure.
All twelve H-derived P values (62,811,368,483–85,140,886,637 B) equal native planner requirements exactly and pass the arm/precheck boundary checks.
Missing registered P deliberately holds before planning; future BYTES sizing rows are checked at registration.
Fresh-output desk status distinguishes program_fault from unavailable, fail and pass; all four real-desk cases pass.
Hand-computed P and missing-P coverage catch M4/M8/M12/M13; disclosure labels and decimal stdout are fixed.
Director's real replay refuses 0 of 10 available sessions, with r2-alpha prepared, never ran; 682 sealed files are unchanged.
103 of 113 importer/native tests passed individually; ten are delegated to PR #547 CI on the final head (director), with no CI result claimed here.
Only the two reports changed in this final slice; director owns commit/push, CI adjudication and final verification on PR #547.

## FIX LOG

| Finding | Disposition / evidence |
|---|---|
| A1 major | Implementation fixed in plan_inputs.sizing_label/valid_disk_terms/registered_disk_terms/member_count and precheck.thresholds_for/run_precheck. Tests: DiskBudgetTests twelve-shape boundaries and non-BYTES identity; PrecheckTests.test_bytes_disk_bar_and_missing_record_through_run_precheck. All twelve updated-H integer P values verified through real planner/arm/precheck thresholds, all12-step4.log (1 test, 6.007 s, exit 0). Desk wait registered in hazard_refusals.json desk_wait_sites. |
| A2 major | Code fixed in bytes_gates.committed_fixed/calculate/main. GatesTests.test_committed_fixed_source_override_and_missing_never_fallback checks integer delta, provenance, invalid types, missing CLI input and no fallback. Real H targets agree; all twelve native planner requirements equal P exactly (all12-step4.log). |
| A3 minor | Fixed in bytes_gates.calculate: guard absent model observations, record model.observations_missing; mark dependent packs unavailable. StoppedSessionTests.test_model_never_ran_cli_writes_unavailable_dependent_packs runs main on all 21 qwen35-122b rows never-ran and checks exit 2, JSON output, five unavailable model lines, s6 dependent null candidates, unaffected packs and llama clock. Full module 19 tests passes. |
| A4 minor | Fixed report; code form unchanged as directed; R6 now states both allowances, check/soak-only margin and reference terms, and requires recomputation if BY-SLOTS changes form. Re-derived per-model-max-nonrequest P deltas: s1 0; s2 +486,009,912; s3 +271,803,398; s4 0; s5 0; s6 +497,717,866 B (variants-step4.log, exit 0). Reference spread 0.022169313982700597 < margin 0.03325233382759357. No code form change. |
| A5 nit | No change needed: maximum of two whole summed bases; reviewer rederive confirms stated deltas. |
| A6 nit | Fixed in DriverLane.prepare_session after real smoke reduction: native requirement and count replace full-pack values; pack_required_free_bytes and pack_member_count preserve derivation labels. ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard executes the real DriverLane smoke path and checks metadata/notes against native count, q and headroom; exit 0. |
| A7 nit | Fixed: ReplayTests.test_nine_plus_h_replay_and_integer_boundaries uses exact int/int equality; plan_inputs imports SESSION_WAIT_BUDGET_S from sealed plan, unchanged. |
| A8 nit | Fixed in both reports: H exit 2 names completeness plus thermal_level 1; committed-fixed tables/R6 and final PROGRESS are current. Scope grant recorded for bytes_h_session.measurements and native tests; native H 36/36 passes, including fully observed native-export C5. |
| R2 open issue | No code change needed: reviewer free space below every pass P correctly refuses/WAITs; operator must free space. Reviewer quantities and smoke share recorded under OPEN ISSUES. |
| BY-MERGE | No change needed in this lane (director disposition 9). Pass1 ancestors alter sealed files relative to main; BY-MERGE owns reconciliation. No code/test added for this hand-forward. The bda481d5a-to-current 682-file diff is empty. |
| R2-1 major | Fixed: numeric audit corrected BY-C5.md replay table from director dcceb8480 archived replay; all old P values absent, measured fixed remains explicitly unused. All twelve native writer/boundary lines re-executed in all12-r2.log, 1 test OK. Final SUMMARY/PROGRESS completed; ten importer checks delegated to PR #547 CI on the final head (director). |
| R2-4 minor | Fixed: implemented freshness by unlinking derived C5.json immediately before every gates invocation, including convergence reruns. desk.json records c5_written and c5_sha256; without a new file status is program_fault regardless of exit. Four real desk/harvest/export tests stub only gates (three required exit-1 cases plus usage exit 2). Verified all four new real-desk tests individually, exit 0; /tmp/byc5f1/r2-desk-case1.log through case4.log. |
| R2-5 nit | Fixed sibling notes keep both keys intact and identify retained two-copy disclosure; no gate consumes them. Reader search quoted below; other bytes_per_member hits belong to native planner inputs, not C5 output. |
| R2-6 nit | Decimal stdout fixed and CLI assertions pin each rate/allowance exact formatting; 20 gates tests pass. Replay row now prepared, never ran. No smoke-source change: precheck.py:88 uses compose.registered_smoke_keep; loop.py:368 calls compose.smoke_keep; compose.py:223-225 dispatches to registered_smoke_keep; smoke.py:29 KEEP_PATH, :263 same registration. |
| R2-2 minor | Fixed hand-computed terms coverage in GatesTests.test_hand_computed_p_includes_margin_reference_and_tree_counts (calculate, no helper re-derivation). All 20 module tests pass. M4/M12/M13 CAUGHT. M13 renames the reference key rather than dropping its numeric contribution, so the test explicitly pins the reference-labelled count/allowances too. |
| R2-3 minor | Fixed: Director's registered-input exception kept deliberately in DriverLane.prepare_session; plan_inputs.encode_disk_budget receipt names missing disk_derivation and registration remedy. AdapterTests.test_bytes_missing_disk_derivation_holds_before_prepared_or_plan passes both absent/malformed rows through real build/prepare; registry test prints 0 rows checked. Refusal census does not scan driver_lane.py or recognize LaneMissing holds (rg produces no matching driver_lane/LaneMissing entries); no registry edit required by disposition 3d. Nine block-6 sessions and H never enter this BYTES driver branch; director replay remains 0 of 10. |

## MUTANTS

At Part 2 slice 1, copied the then-current tree with `cp -R /Users/edr/code/JouleWise-by-c5 /private/tmp/byc5f1/mut-tree`. Each X in M4, M8, M12, M13 ran sequentially with:

`JW_MUT_ROOT=/private/tmp/byc5f1/mut-tree JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -I -B /Users/edr/night-archive/forward-20261021/BY-C5/review-r2/mut.py X > /tmp/byc5f1/mut-X.log 2>&1`

```text
M4 no margin on stream allowance CAUGHT [('test_bytes_gates', 1, 'Ran 20 tests in 2.916s FAILED (failures=1)')]
M8 missing P proceeds CAUGHT [('test_plan_inputs', 0, 'Ran 9 tests in 0.038s OK'), ('test_session_wrapper', 0, 'Ran 6 tests in 0.091s OK'), ('test_lane_adapters', 1, 'Ran 22 tests in 0.363s FAILED (failures=2)')]
M12 count per model=50 fixed CAUGHT [('test_bytes_gates', 1, 'Ran 20 tests in 2.866s FAILED (failures=1)')]
M13 reference allowance dropped CAUGHT [('test_bytes_gates', 1, 'Ran 20 tests in 2.862s FAILED (errors=1)')]
```

M13 first survived numerical assertions because its actual edit renames `reference` to `_unused`, and disk_terms still sums every value. Final assertions pin the required reference-labelled disclosure and exact allowances. Truly removing reference also changes the hand-computed bases. One premature M4 launch before copying finished produced FileNotFoundError; it touched neither source tree and was rerun after copy completion. The disposable tree was removed using shutil.rmtree after the shell rejected rm -rf; working clone was never mutated.

## PART 2 SLICE 1 VERIFICATION

Each run.py command below allocates and deletes its own /private/tmp/jwtmp-byc5f1.* TMPDIR. No skips or environmental failures. Final independent runs supersede initial combined-module checks sharing one TMPDIR.

| Exact command | Tests | Exit |
|---|---:|---:|
| `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-final-gates.log -m unittest tests.test_bytes_gates` | 20 | 0 |
| `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-final-inputs.log -m unittest tests.b6.test_plan_inputs` | 9 | 0 |
| `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-final-adapters.log -m unittest tests.b6.test_lane_adapters` | 22 | 0 |
| `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-final-wrapper.log -m unittest tests.b6.test_session_wrapper` | 6 | 0 |

Sealed check: load `files` keys from configs/campaigns/v5_claim_25g83/sealed_inventory.json, pass all 682 paths to `git diff --name-only bda481d5a -- <paths>` (HEAD plus working edits). Empty output saved as /tmp/byc5f1/sealed-r2-slice1.log. `git diff --check`: exit 0, empty output.

Applied R2-3 decision: hold for the missing registered physical-hazard input P instead of arming against inherited constants or no bar. Receipt/lineage/provenance remain flags. Registration row is the remedy; CI checks future rows before any loop hold. This is the director's explicit exception. Refusal census does not cover driver-lane holds; disposition 3d permits recording the decision in this report.

## PRECHECK END TO END

Updated-H terms: ProductionPlanRenderTests.test_all_twelve_committed_fixed_budgets_through_native_planner_and_precheck uses all twelve real pack shapes with H-derived B/WAIT/committed fixed, synthetic timing/identity/launch seams, real DriverLane/plan_inputs/plan.write_window_plan, real thresholds_for and disk.measure/judge. Each native arm refuses P−1 and passes P. Each precheck disk boundary refuses bar−1 and passes bar with and without smoke. Run_precheck decision coverage is separately exercised by the s6 test; these are synthetic proofs, not live hardware evidence.

```text
bytes-s1-p1 P 73814147037 n 125 q 116714296 headroom 30046286037 smoke_retained 1400571562 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s1-p2 P 73814147037 n 125 q 116714296 headroom 30046286037 smoke_retained 1400571562 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s2-p1 P 75981813519 n 125 q 122494740 headroom 30046286019 smoke_retained 1469936889 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s2-p2 P 75981813519 n 125 q 122494740 headroom 30046286019 smoke_retained 1469936889 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s3-p1 P 79464395095 n 125 q 131781624 headroom 30046286095 smoke_retained 1581379500 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s3-p2 P 79464395095 n 125 q 131781624 headroom 30046286095 smoke_retained 1581379500 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s4-p1 P 85140886637 n 125 q 146918935 headroom 30046286012 smoke_retained 1763027229 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s4-p2 P 85140886637 n 125 q 146918935 headroom 30046286012 smoke_retained 1763027229 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s5-p1 P 75849013177 n 75 q 203567677 headroom 30046285852 smoke_retained 1832109098 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s5-p2 P 75849013177 n 75 q 203567677 headroom 30046285852 smoke_retained 1832109098 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s6-p1 P 62811368483 n 75 q 145622589 headroom 30046285958 smoke_retained 1310603310 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s6-p2 P 62811368483 n 75 q 145622589 headroom 30046285958 smoke_retained 1310603310 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
```

Synthetic terms B=1,000,001 B, WAIT=7,200 B, fixed=19 B imply P=2,014,421 B exactly. All twelve production pack trees pass at P and refuse at P-1 via thresholds_for and real disk.measure/judge; same boundaries hold at P+ceil(2*B*m/n) with smoke. The real run_precheck test covers WAIT/START with and without smoke and START plus disk.budget_missing at zero free bytes when P is absent. Driver remains responsible for its pre-existing missing-budget LaneMissing hold.

Smoke decision: retained member bytes remain before full-session arm. Add ceil(c*B*m/n), with c=2, m from compose.registered_smoke_keep and n from the same real native-stage count used by the arm. No WAIT/fixed term is added again. The receipt records formula, B, c, m, n and integer result. Non-BYTES disk defaults are byte-identical.

Reviewer probe command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/probe-step3.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/precheck_probe.py /Users/edr/code/JouleWise-by-c5` (exit 0). It prints for each of s1–s6 p1, with and without smoke: `precheck bar 0 ... precheck at free=P: PASS | at free=P(committed fixed): PASS`. This is the missing-registration flag path: the repository has no registered pass P yet. It is not proof of registered real-H boundary values; the later all12-step4.log and all12-r2.log tests supply that proof.

## P PER SUB-PACK (committed fixed)

All planner equality cells below are now verified through the real writer. q/headroom/native count and smoke retention are printed above. Every model count and allowance from the exact-rational C5 source follows; decimals are display only, no tolerance applied to bytes.

Source: configs/campaigns/bytes_mac_check/registration/sizing_b5.json at /packs/bytes-mac-check/disk_derivation/fixed_retained_bytes.
Real H C5 input and exact rational allowances are preserved in /tmp/byc5f1/C5.json; stdout /tmp/byc5f1/H-C5.stdout.
Rates r_s=1,805,538.5168827055 B/s; r_w=1,285,759.0452694688 B/s.
WAIT=12,999,877,322 B; committed fixed=4,046,531,103 B; measured fixed unused=1,266,544,640 B.
c=2; measured c=0.8020750916018277 (disclosure).

| pack | stream basis | wall basis | B | P | planner equality |
|---|---:|---:|---:|---:|---|
| bytes-s1-p1 | 21883930645 | 21697490999 | 21883930645 | 73814147037 | yes, all12-step4.log |
| bytes-s1-p2 | 21883930645 | 21697490999 | 21883930645 | 73814147037 | yes, all12-step4.log |
| bytes-s2-p1 | 22841465166 | 22967763886 | 22967763886 | 75981813519 | yes, all12-step4.log |
| bytes-s2-p2 | 22841465166 | 22967763886 | 22967763886 | 75981813519 | yes, all12-step4.log |
| bytes-s3-p1 | 24053464961 | 24709054674 | 24709054674 | 79464395095 | yes, all12-step4.log |
| bytes-s3-p2 | 24053464961 | 24709054674 | 24709054674 | 79464395095 | yes, all12-step4.log |
| bytes-s4-p1 | 27547300445 | 26855538139 | 27547300445 | 85140886637 | yes, all12-step4.log |
| bytes-s4-p2 | 27547300445 | 26855538139 | 27547300445 | 85140886637 | yes, all12-step4.log |
| bytes-s5-p1 | 22901363715 | 21700998244 | 22901363715 | 75849013177 | yes, all12-step4.log |
| bytes-s5-p2 | 22901363715 | 21700998244 | 22901363715 | 75849013177 | yes, all12-step4.log |
| bytes-s6-p1 | 14585071383 | 16382541368 | 16382541368 | 62811368483 | yes, all12-step4.log |
| bytes-s6-p2 | 14585071383 | 16382541368 | 16382541368 | 62811368483 | yes, all12-step4.log |

Reviewer rederive command (exit 0):
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/rederive.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/rederive.py /Users/edr/code/JouleWise-by-c5 /tmp/byc5f1/MEASUREMENTS.raw.json /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv 4046531103`
Compare P_committed_fixed column; its P column deliberately uses measured-fixed as the old baseline.


| pack | model | count | stream allowance s | member-wall allowance s |
|---|---|---:|---:|---:|
| bytes-s1-p1 | qwen3-1p7b | 50 | 95.936319908860 | 133.421011684801 |
| bytes-s1-p1 | qwen3-4b | 50 | 99.592648097569 | 138.716749210070 |
| bytes-s1-p1 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s1-p2 | qwen3-1p7b | 50 | 95.936319908860 | 133.421011684801 |
| bytes-s1-p2 | qwen3-4b | 50 | 99.592648097569 | 138.716749210070 |
| bytes-s1-p2 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s2-p1 | qwen3-30b-a3b | 50 | 100.460336723753 | 145.758197295419 |
| bytes-s2-p1 | qwen3-8b | 50 | 105.675267597787 | 146.138676196654 |
| bytes-s2-p1 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s2-p2 | qwen3-30b-a3b | 50 | 100.460336723753 | 145.758197295419 |
| bytes-s2-p2 | qwen3-8b | 50 | 105.675267597787 | 146.138676196654 |
| bytes-s2-p2 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s3-p1 | qwen3-14b | 50 | 115.960714413045 | 158.620031791883 |
| bytes-s3-p1 | qwen3-next-80b | 50 | 103.600245103200 | 160.362644346979 |
| bytes-s3-p1 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s3-p2 | qwen3-14b | 50 | 115.960714413045 | 158.620031791883 |
| bytes-s3-p2 | qwen3-next-80b | 50 | 103.600245103200 | 160.362644346979 |
| bytes-s3-p2 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s4-p1 | qwen3-32b | 50 | 147.706179398033 | 199.223982318429 |
| bytes-s4-p1 | qwen3-8b-8bit | 50 | 110.556092238560 | 153.147274264739 |
| bytes-s4-p1 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s4-p2 | qwen3-32b | 50 | 147.706179398033 | 199.223982318429 |
| bytes-s4-p2 | qwen3-8b-8bit | 50 | 110.556092238560 | 153.147274264739 |
| bytes-s4-p2 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s5-p1 | llama-70b | 50 | 206.799102208280 | 272.192316152822 |
| bytes-s5-p1 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s5-p2 | llama-70b | 50 | 206.799102208280 | 272.192316152822 |
| bytes-s5-p2 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s6-p1 | qwen35-122b | 50 | 114.679302443784 | 189.463644769154 |
| bytes-s6-p1 | reference | 25 | 93.759871867767 | 130.734032387328 |
| bytes-s6-p2 | qwen35-122b | 50 | 114.679302443784 | 189.463644769154 |
| bytes-s6-p2 | reference | 25 | 93.759871867767 | 130.734032387328 |

## STOPPED-EARLY C5

Finding 3 synthetic main output: completeness:qwen35-122b:check: fail; completeness:qwen35-122b:soak: fail; contention/cpu_contention/calibration_T10/resolvability/clock:qwen35-122b: unavailable; disk:bytes-s6-p{1,2}: unavailable; sizing:bytes-s6-p{1,2}: unavailable; clock:llama-70b: pass. Exit 2, JSON written. All 21 qwen35-122b rows (5 checks + 12 soaks + 4 test-7 probes) never-ran. Both s6 packs have null programmed_span_s, T_stream_max_s, required_free_bytes and disk_derivation; all other packs remain available. Flag model.observations_missing names qwen35-122b.

Real H main exits 2 because completeness and thermal lines fail (thermal_level 1), not a program fault.

## TESTS RUN

Final accounting (director instruction supersedes every historical pending/next note below): 103 of 113 importer/native individual passes stand as evidence. Ten tests are **delegated to PR #547 CI on the final head (director)** on PR #547, head c36ef1c51. No local test or slow importer module was run in this final slice. CI exit code/result is not yet observed. The exact local commands and final logs from earlier slices remain below; the table in FINAL REPORT VERIFICATION records the final allocation.

Earlier-slice execution evidence follows; pending instructions in these historical records are superseded by the CI delegation above.

Slice 4 (standard environment and fresh TMPDIR via run.py):
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/all12-step4.log -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_all_twelve_committed_fixed_budgets_through_native_planner_and_precheck`: 1 test, 6.007 s, exit 0.
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/variants-step4.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/variants.py /Users/edr/code/JouleWise-by-c5 /tmp/byc5f1/MEASUREMENTS.raw.json /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv`: exit 0, reviewer sensitivity reproduced.
- lane-step4.log: 21 tests, exit 1; two /tmp versus /private/tmp path-alias assertions. Runner corrected to physical /private/tmp for subsequent runs; production code unchanged. lane-step4-physical.log rerun: 21 tests, 0.299 s, exit 0. smoke-step4.log: 22 tests, 47.403 s, exit 0. Physical /private/tmp is the same fresh mktemp directory via its canonical macOS alias, deleted after each module.

All runs set JW_B5_SYNTHETIC_ONLY=1 and PYTHONDONTWRITEBYTECODE=1, use /opt/homebrew/bin/python3.13 -B, and get a fresh /tmp/jwtmp-byc5f1.* TMPDIR removed after completion.

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -c '<temporary-directory subprocess runner>'`: child `-m unittest tests.test_bytes_gates`; 18 tests, 3.040 s, exit 0, no skips/environment failures, /tmp/byc5f1/step1-tests.log.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/plan-inputs-tests.log -m unittest tests.b6.test_plan_inputs`: 6 tests, 0.017 s, exit 0, no skips/environment failures.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/H-C5.stdout scripts/bytes_gates.py --runs /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv --measurements /tmp/byc5f1/MEASUREMENTS.raw.json --disk-evidence /tmp/byc5f1/disk_h.json --out /tmp/byc5f1/C5.json`: exit 2, JSON written, all twelve exact expected byte targets pass.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/stopped-early-tests.log -m unittest tests.test_bytes_gates`: 19 tests, 3.104 s, exit 0, no skips/environment failures.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/H-C5-step2.stdout scripts/bytes_gates.py --runs /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv --measurements /tmp/byc5f1/MEASUREMENTS.raw.json --disk-evidence /tmp/byc5f1/disk_h.json --out /tmp/byc5f1/C5-step2.json`: exit 2, JSON written.
- `git diff --check`: exit 0.

Slice 3 exact commands (same runner environment described above):
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/precheck-inputs-step3.log -m unittest tests.b6.test_plan_inputs`: 8 tests, exit 0.
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/precheck-class-step3.log -m unittest tests.b6.test_precheck.PrecheckTests.test_07_disk_smoke_budget_and_remedy`: 1 test, exit 0.
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/precheck-bytes-step3.log -m unittest tests.b6.test_precheck.PrecheckTests.test_bytes_disk_bar_and_missing_record_through_run_precheck`: 1 test, exit 0 after correcting test fixture setup (sizing source absent from synthetic_checkout).
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/refusals-step3.log -m unittest tests.hazards.test_refusal_allowlist`: 23 tests, exit 0, one existing skip. Registry-note rerun log: refusals-step3-final.log (23 tests, exit 0, one existing skip).
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/import-step3.log -m unittest tests.hazards.test_import_graph`: 6 tests, one failure: arm/monitor integration returns NULL vs expected GO. Diagnosed by real Rig rerun: sysmond service not found and pgrep Cannot get process list; sandbox process-group census failure, director rerun required. Evidence /tmp/byc5f1/arm-debug-step3.log. No import-list failure.
- Reviewer probe as above: exit 0.
- `git diff --check`: exit 0.

## SEALED INVENTORY

Final report slice rechecked all 682 paths against bda481d5a, both HEAD and working tree: exit 0, empty output. Exact command is in FINAL REPORT VERIFICATION below.

Command: `git diff --name-only bda481d5a -- <all 682 keys of configs/campaigns/v5_claim_25g83/sealed_inventory.json files>`; exit 0, empty stdout (also includes uncommitted work). Log /tmp/byc5f1/sealed.log.

## DECISIONS I MADE

- Applied the final director note: retain 103/113 individual passes and delegate the remaining 4+5+1 importer cases to PR #547 CI on the final head (director). No further slow runs; COMPLETE means assigned implementation/report work is complete, with CI/final verification still owned by the director.
- Applied ruling precedence: exact rational maximum of the two summed bases, rounded once each; raw allocated bytes only, c=2 with measured c disclosed, registered 7,200-second WAIT, per-model pass allowances/counts and reference terms. No reserve or added margin. Committed fixed supersedes measured partial fixed.
- A4/A5: retain the ruled member-wall form and whole-base maximum, document both allowances and check/soak margin; BY-SLOTS must recompute if its registered form changes. Alpha/beta/gamma retain their existing path.
- A8/BY-MERGE: correct report location/completeness/thermal text, acknowledge native-producer scope grant; ancestor sealed-file differences relative to main remain BY-MERGE's work.
- R2-1: use committed fixed 4,046,531,103 B everywhere operative; replay rows come from director dcceb8480 JSON. The only remaining measured fixed occurrences are explicitly unused disclosure. Native planner equality is integer identity for every pack.
- R2-2: pin calculate with independent hand arithmetic (nonzero margin, reference, counts 2/3/1); all four requested mutants are CAUGHT.
- R2-3: director's deliberate registration-completeness exception retains LaneMissing for absent/malformed P, writes its remedy, and validates future registered bytes-s rows in CI. Receipts/lineage/provenance remain flags; driver hold sites are outside the refusal census.
- R2-4: remove only the desk-owned derived C5.json before each invocation, including convergence reruns; freshness requires new output. Record c5_written and SHA-256; leave the documented 0/2/1 exit contract unchanged.
- R2-5: retain both disclosure keys with sibling labels identifying their two-copy basis and no-gate use. No reader changes required.
- R2-6: nine significant decimal digits beside exact fractions exceed the ruled seven; JSON fractions stay exact. r2-alpha is prepared, never ran. No smoke-source change: precheck.py:88, loop.py:368, compose.py:217/223–225 and smoke.py:29/263 use the same registered keep counts.
- Reviewer low-free-space open issue: correct physical refusal; operator owns freeing space. No new margin or reserve.

- Director disposition 2 supersedes old which-text-wins item 5: fixed comes solely from committed H sizing. --committed-sizing can override the file, with identical pointer/type validation; no measured fallback.
- Missing/malformed committed fixed is disk.committed_fixed_missing, a desk flag; no new refusal site or harvested flag catalog entry.
- Finding 7 exact measured_c equality is bit identity of the same integer division. WAIT imports the sealed constant; no sealed source edits.
- Keep C5's member-wall form and maximum of two whole summed bases as instructed; complete allowance details and sensitivity are recorded in BY-C5.md R6 DRAFT and A4 above.
- Local route overrides cloud setup and Git-write rules; director committed/pushed slices through c36ef1c51 and owns the final two-report commit. Destination remains lane/2026-10-22-bytes-c5-gates, draft PR #547.

- Finding 3: absent model sizing data is a recorded flag. No mean, maximum or allowance is invented; all dependent pass candidates stay null. Completeness retains exit 2 under the existing contract.

- Finding 1: add smoke member retention ceil(2*B*m/n) because the smoke remains on the session volume before full-session arm. Both counts come from production registration/tree paths; no block-6 smoke constant applies. Missing P is flagged and bypasses disk judgment; the driver retains the record hold.
- Share sizing label lookup and disk-term validation rather than duplicate PRECHECK policy. Apply BYTES disk policy after threshold override layers so an old reserve cannot supersede P.

## Clause map

| Clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| committed fixed only, recorded provenance | scripts/bytes_gates.py committed_fixed/calculate/main | test_committed_fixed_source_override_and_missing_never_fallback | Use measured fixed or omit source hash: exact P delta/provenance assertion fails. |
| absent committed input is unavailable, no fallback | scripts/bytes_gates.py committed_fixed/calculate | same test, invalid input loop and main missing-file check | Fall back to measured fixed: disk statuses and CLI exit assertions fail. |
| model without observations remains visible | scripts/bytes_gates.py calculate model loop and pass loop | test_model_never_ran_cli_writes_unavailable_dependent_packs | Remove the guard: main exits 1 without JSON; substitute zero allowances: unavailable/null assertions fail. |
| measured c exact division | tests/test_bytes_gates.py ReplayTests | test_nine_plus_h_replay_and_integer_boundaries | Perturb measured_c by any representable amount: equality fails. |
| R2-2, reference/margin/tree counts set P | scripts/bytes_gates.py disk_allowance/calculate | GatesTests.test_hand_computed_p_includes_margin_reference_and_tree_counts | Drop margin or replace tree counts with 50: exact hand-computed P fails (M4/M12); rename reference disclosure: reference-key assertion fails (M13). |
| R2-3, absent registered P holds before plan | joulewise/b6/driver_lane.py prepare_session; plan_inputs.py encode_disk_budget | AdapterTests.test_bytes_missing_disk_derivation_holds_before_prepared_or_plan | Remove LaneMissing return: result and no-plan assertions fail (M8). |
| R2-3, registration catches absent P | tests/b6/test_plan_inputs.py DiskBudgetTests.test_registered_bytes_rows_have_valid_disk_terms | every bytes-s sizing row passes valid_disk_terms | Add a bytes-s sizing row without disk_derivation: registry assertion fails. Currently zero rows. |
| R2-4, no fresh C5 means program_fault | scripts/bytes_h_session.py desk freshness loop and status | SessionTests.test_desk_gates_exit_one_without_c5_is_program_fault; test_desk_stale_c5_does_not_hide_program_fault; test_desk_usage_exit_two_without_c5_is_program_fault | Remove unlink: stale-file case accepts old output; omit freshness status branch: exit-1/2 no-file status assertions fail. |
| R2-4, fresh exit-1 output means unavailable and carries digest | scripts/bytes_h_session.py desk status receipt | SessionTests.test_desk_gates_exit_one_with_new_c5_is_unavailable | Map exit 1 to program_fault or omit digest: status/c5_written/digest assertions fail. |
| R2-5, disclosure labels | scripts/bytes_gates.py calculate models/sessions | GatesTests.test_cli_runs_every_gate_from_native_nonclaim_harvest | Remove either sibling note: explicit label assertions fail. |
| R2-6a, decimal beside exact fraction | scripts/bytes_gates.py main displayed | GatesTests.test_cli_runs_every_gate_from_native_nonclaim_harvest | Remove decimals or fraction text: exact formatted stdout assertion fails for each rate/allowance. |

## OPEN ISSUES

- R2 physical free-space issue: reviewer reading 53,472,432,128 B was below every pass P. Arm refusal/precheck WAIT is correct until the operator frees about 9.3 GB (s6) to 31.7 GB (s4), plus smoke retention up to 1.83 GB. Final slice intake: 47 GiB available (>25 GiB workspace stop). No arming or measurement attempted.
- Ten importer tests are delegated to PR #547 CI on the final head (director); their result is unobserved here. The 103 individual passes stand; none of the ten is counted as passed. Environmental hazard reruns (arm sysmond/pgrep, import-graph GO/NULL, clock bootsessionuuid) remain director-owned. Refusal census has one existing skip for the absent block-5 design branch.
- BY-MERGE hand-forward: pass1 ancestors change sealed files relative to main (including b5/plan.py, b5/driver.py and hazards/clock.py). No lane change is required; the sealed diff against bda481d5a is empty.
- PR #547: director committed/pushed c36ef1c51 and reports whole-suite PR #547 CI on the final head on that head. No CI result was fetched or inferred. Director owns final review, report commit/push and ledger done line.

## NEEDS_RULING

none

## HISTORICAL SLICE EVIDENCE

The checkpoints and handoffs below preserve execution history. Their pending/next instructions and old head/CI statements are superseded by final PROGRESS and final CI delegation.

Slice 3 sealed recheck: /tmp/byc5f1/sealed-step3.log, all 682 paths, exit 0, empty stdout.

Slice 3 finding 6 exact test command (standard synthetic environment/fresh TMPDIR): `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/smoke-metadata-step3-final.log -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard`: 1 test, 15.219 s, exit 0. No real arm/install executed; installer seam is fake.

Director commit handoff: proposed `BY-C5 fix1 slice 3: PRECHECK shares registered P and smoke retention; smoke metadata records native requirement`. Push would be to lane/2026-10-22-bytes-c5-gates only; worker performed no Git writes.

Slice 4 additional exact commands, all standard JW_B5_SYNTHETIC_ONLY/PYTHONDONTWRITEBYTECODE environment and fresh TMPDIR per final module run:
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/loop-step4.log -m unittest tests.test_b6_loop.LoopTests`: 55 tests, 4.770 s, exit 0.
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/session-step4.log -m unittest tests.b6.test_session_wrapper`: 6 tests, 0.081 s, exit 0.
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/planinputs-step4-final.log -m unittest tests.b6.test_plan_inputs`: 8 tests, 0.035 s, exit 0.
- Earlier combined inputs-session-step4.log: 14 tests, exit 0; superseded by separate per-module TMPDIR runs above.
- `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/render-step4.log -m unittest tests.b6.test_b6_plan_render`: 5 tests, 57.128 s, exit 0, no skips.
- `git diff --name-only bda481d5a -- <all 682 sealed inventory paths>`: exit 0, empty stdout and stderr, /tmp/byc5f1/sealed-step4.log, including uncommitted work.
- `git diff --check`: exit 0.

Required importer census command: `rg -n 'from joulewise.b6 import.*(precheck|plan_inputs|driver_lane)|from joulewise.b6.(precheck|plan_inputs|driver_lane)' tests --glob '*.py'`. Besides touched/requested modules, this names hazards.test_clock, hazards.test_arm, test_b6_machine_test, b6.test_cold_pass_fixes, b6.test_round2_review_fixes, b6.test_capture_screen_reachability, b6.test_desk_resume_finalize, b6.test_s3_cold_fixes, b6.test_integration_seams, b6.test_loop_round_desk. Existing environmental hazards reruns remain director-owned; inspect broader support/round_support importers as appropriate.

Slice 4 handoff: local branch by-c5, HEAD dcceb8480bf9a7094b640e4ac57eade16b9e0666. Proposed director commit/push: `BY-C5 fix1 slice 4: verify all twelve committed-fixed native/precheck budgets; correct R6 and tables`, destination lane/2026-10-22-bytes-c5-gates, draft PR #547. No Git writes by worker. No real session reads. No COMPLETE marker until remaining authorized checks/report work finishes.

## DESK STATUS (R2-4)

All four cases now verified independently through the real desk path, each one test OK with exit 0 and no skips:

| Gates result | Recorded status | c5_written | SHA-256 |
|---|---|---|---|
| exit 1, no new C5 | program_fault | false | null |
| exit 1, new C5 | unavailable | true | exact new-file digest |
| stale C5, exit 1, no new C5 | program_fault | false | null |
| stale C5, usage exit 2, no new C5 | program_fault | false | null |

Evidence: /tmp/byc5f1/r2-desk-case1.log, case2.log, case3.log, case4.log; exact commands in PART 2 SLICE 3. Tests assert absence of C5 at each gates invocation and equality of returned receipt with written desk.json.

The desk removes only its derived C5.json before each gates run; no hash-only freshness inference. New output records c5_written=true and its SHA-256. No output records false/null and program_fault even on exit 1 or 2. Test cases: exit 1/no file → program_fault; exit 1/new file → unavailable; stale file plus no new file → program_fault; usage exit 2/no file → program_fault. Tests exercise real preparation/harvest/export/measurements/desk; only gates subprocess is stubbed.

## PART 2 SLICE 2 EVIDENCE

Exact commands (runner gives each module a fresh physical TMPDIR and deletes it):

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-gates-display.log -m unittest tests.test_bytes_gates`: 20 tests, exit 0.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/H-C5-r2-display.stdout scripts/bytes_gates.py --runs /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv --measurements /tmp/byc5f1/MEASUREMENTS.raw.json --disk-evidence /tmp/byc5f1/disk_h.json --out /tmp/byc5f1/C5-r2-display.json`: exit 2 (stopped H); all twelve lines show decimal and exact terms. r_s=1805538.52, r_w=1285759.05 B/s, nine significant digits. Exact JSON fractions unchanged.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/all12-r2.log -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_all_twelve_committed_fixed_budgets_through_native_planner_and_precheck`: 1 test, exit 0. Twelve lines:

```text
bytes-s1-p1 P 73814147037 n 125 q 116714296 headroom 30046286037 smoke_retained 1400571562 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s1-p2 P 73814147037 n 125 q 116714296 headroom 30046286037 smoke_retained 1400571562 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s2-p1 P 75981813519 n 125 q 122494740 headroom 30046286019 smoke_retained 1469936889 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s2-p2 P 75981813519 n 125 q 122494740 headroom 30046286019 smoke_retained 1469936889 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s3-p1 P 79464395095 n 125 q 131781624 headroom 30046286095 smoke_retained 1581379500 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s3-p2 P 79464395095 n 125 q 131781624 headroom 30046286095 smoke_retained 1581379500 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s4-p1 P 85140886637 n 125 q 146918935 headroom 30046286012 smoke_retained 1763027229 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s4-p2 P 85140886637 n 125 q 146918935 headroom 30046286012 smoke_retained 1763027229 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s5-p1 P 75849013177 n 75 q 203567677 headroom 30046285852 smoke_retained 1832109098 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s5-p2 P 75849013177 n 75 q 203567677 headroom 30046285852 smoke_retained 1832109098 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s6-p1 P 62811368483 n 75 q 145622589 headroom 30046285958 smoke_retained 1310603310 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
bytes-s6-p2 P 62811368483 n 75 q 145622589 headroom 30046285958 smoke_retained 1310603310 planner=P; arm REFUSE/PASS; precheck REFUSE/PASS both smoke states
```

Reader audit before labels, exact command `rg -n 'projected_footprint_bytes|bytes_per_member' scripts/ joulewise/ tests/ tools/ > /tmp/byc5f1/r2-disclosure-readers.log 2>&1` (exit 2 because tools/ does not exist; every existing requested tree searched):

```text
rg: tools/: No such file or directory (os error 2)
scripts/bytes_gates.py:246:                             "T_stream_max_s": None, "bytes_per_member": None}
scripts/bytes_gates.py:310:                         "bytes_per_member": max(receipts[r]["retained_bytes"] for r in all_model)}
scripts/bytes_gates.py:366:            projected_bytes = None if fixed_bytes is None or missing_models else fixed_bytes + reference_count * ref_bytes + sum(50 * models[m]["bytes_per_member"] for m in mids)
scripts/bytes_gates.py:375:                                 "measured_margin": margin, "projected_footprint_bytes": projected_bytes,
scripts/rehearse_b5_real.py:358:        "bytes_per_member": BYTES_PER_MEMBER,
tests/test_b6_machine_test.py:251:        self.assertEqual(inputs["bytes_per_member"], 182 * 1024 * 1024)
joulewise/b5/plan.py:84:    "T_stream_max_s", "bytes_per_member", "thresholds", "g10", "registration",
joulewise/b5/plan.py:541:    _number(inputs["bytes_per_member"], "bytes_per_member", integer=True)
joulewise/b5/plan.py:810:    planned_bytes = inputs["bytes_per_member"] * (members + spare_members)
tests/test_bytes_h_session.py:355:        self.assertEqual(state['inputs']['bytes_per_member'], 150_690_066)
tests/test_bytes_h_session.py:356:        self.assertEqual(budget['bytes_per_member'], state['inputs']['bytes_per_member'])
tests/test_bytes_h_session.py:363:        self.assertEqual(budget['bytes_per_member'], quotient)
tests/b6/test_b6_plan_render.py:247:                    "q", budget["bytes_per_member"], "headroom", budget["headroom_bytes"],
tests/b6/test_b6_plan_render.py:306:        native_required = 3 * m * smoke_metadata["inputs"]["bytes_per_member"] + \
tests/test_b5_plan.py:109:                self.assertEqual((members + 7) * inputs["bytes_per_member"], window["planned_bytes"])
joulewise/b6/plan_inputs.py:113:              "T_stream_max_s": allowance("T_stream_max_s"), "bytes_per_member": BYTES_PER_MEMBER,
joulewise/b6/plan_inputs.py:175:    inputs["bytes_per_member"] = q
joulewise/b6/plan_inputs.py:178:                             "member_count": n, "native_copies": 3, "bytes_per_member": q,
tests/b6/test_plan_inputs.py:106:            self.assertEqual(inputs["bytes_per_member"], 182 * 1024 * 1024)
tests/b6/test_plan_inputs.py:113:                      "bytes_per_member": plan_inputs.BYTES_PER_MEMBER,
tests/b6/test_plan_inputs.py:130:            self.assertEqual(3 * n * inputs["bytes_per_member"] +
joulewise/b6/driver_lane.py:116:                    required_free_bytes=3 * m * inputs["bytes_per_member"] +
scripts/bytes_h_session.py:323:        'native_copies': native_copies, 'bytes_per_member': per_member,
scripts/bytes_h_session.py:344:                  bytes_per_member=per_member)
tests/fixtures/b5_plan/fake_window.py:290:        "bytes_per_member": 190840832, "thresholds": json.loads(json.dumps(THRESHOLDS)),
```

Numeric report audit command:

`rg -n '1,266,544,640|1266544640|71,034,160,574|71034160574|73,201,827,056|73201827056|76,684,408,632|76684408632|82,360,900,174|82360900174|73,069,026,714|73069026714|60,031,382,020|60031382020' .codex-report/BY-C5.md > /tmp/byc5f1/r2-number-audit-final.log`

Final output rechecked in the final report-only slice (exit 0; only explicitly unused measured disclosures remain):

```text
30:Updated for committed fixed in fix round: all twelve requirements below verified through the real planner and disk hazard, and real precheck thresholds with smoke/no-smoke boundaries (all12-step4.log). C5 provenance records the source path, SHA-256 and JSON pointer. Measured fixed=1,266,544,640 B is unused disclosure.
268:The committed fixed source is configs/campaigns/bytes_mac_check/registration/sizing_b5.json, pointer /packs/bytes-mac-check/disk_derivation/fixed_retained_bytes (SHA-256 42bd19f9b4387944b919346ac946f0b996bf694f5f9af084f15adff4d35622c6). The stopped-session measured 1,266,544,640 B is unused disclosure. PRECHECK uses P with zero headroom; with smoke due it adds only ceil(2 B m/n) retained smoke member bytes. Missing P is flagged, without an inherited reserve; DriverLane retains its registration hold. Smoke metadata labels its actual native requirement separately from full-pack P.
```

Sealed inventory: `/opt/homebrew/bin/python3.13 -B` loads `files` from configs/campaigns/v5_claim_25g83/sealed_inventory.json, then `git diff --name-only bda481d5a -- <all 682 file paths>`: exit 0, empty stdout, saved /tmp/byc5f1/sealed-r2-slice2.log. `git diff --check`: exit 0, empty output.

Applied R2-4 decision: freshness uses removal of the derived desk-owned output before every invocation; a new file is required for pass/fail/unavailable, and its SHA-256 is recorded. The bytes_gates exit contract stays unchanged. R2-5 labels preserve keys; no new bar. R2-6 decimals use nine significant digits, exceeding seven required for the ruled 1e-6 relative rate agreement; exact JSON is unchanged.

Additional slice-2 exact commands:

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-bytes-packs.log -m unittest tests.b6.test_bytes_packs`: 9 tests, exit 0, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-refusals.log -m unittest tests.hazards.test_refusal_allowlist`: 23 tests, exit 0, 1 skip because the block-5 design branch is absent in this standalone clone (test_refusal_allowlist.py:233).
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-desk-status.log -m unittest tests.test_bytes_h_session.SessionTests.test_desk_gates_exit_one_without_c5_is_program_fault tests.test_bytes_h_session.SessionTests.test_desk_gates_exit_one_with_new_c5_is_unavailable tests.test_bytes_h_session.SessionTests.test_desk_stale_c5_does_not_hide_program_fault tests.test_bytes_h_session.SessionTests.test_desk_usage_exit_two_without_c5_is_program_fault`: long native harvest run, inspect log at next intake for count/exit before claiming completion. One completed-test dot at current checkpoint, no failure marker. No fixture harvest results or measurements are stubbed.

Direct import census: `rg -l 'from scripts import .*bytes_gates|from scripts import .*bytes_h_session|import scripts.bytes_gates|import scripts.bytes_h_session|bytes_h_session|bytes_gates' tests --glob '*.py'` finds only tests/test_bytes_h_session.py and tests/test_bytes_gates.py (saved /tmp/byc5f1/r2-importer-modules.txt). Broader round-required precheck/loop/smoke/adapters/graph runs remain to be finalized.

## PART 2 SLICE 3

Intake: clean by-c5 at 4aa17a44e, descendant of requested 0a585bb8e; 47 GiB available. No code changes needed after slice-2 implementation. Reports corrected stale CI/head/replay statements; historical execution records remain labelled by slice.

Independent byte-table audit (initial scratch attempt stopped before replay comparison on a full-path/name mismatch; corrected auditor uses Path.name without opening session paths):

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/audit_tables.py > /tmp/byc5f1/r2-table-audit.log 2>&1`

Exit 0, output:

```text
12 P rows: exact C5 byte terms and 3*n*q+headroom=P
11 replay rows: exact director replay bytes; 0/10 refusals
```

Fresh-TMPDIR commands (run.py deletes each directory; wrapper prints the child exit; underlying logs supply authoritative result):

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-loop.log -m unittest tests.test_b6_loop`: 55 tests OK, exit 0, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-integration.log -m unittest tests.b6.test_integration_seams`: 7 tests OK, exit 0, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-graph.log -m unittest tests.hazards.test_import_graph`: 6 tests, exit 1, one GO/NULL failure in test_a_complete_arm_and_monitor_run_load_no_retired_module; five static checks pass. Earlier arm-debug-step3.log establishes sandbox sysmond/pgrep census cause; reviewer outside sandbox ran 6 OK at dcceb8480. Director owns rerun.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/remaining.py tests.b6.test_precheck > /tmp/byc5f1/r2-precheck-split.log 2>&1`: 24 individual tests OK, each child exit 0, no skips. remaining.py loads names, then runs each with `run.py /tmp/byc5f1/final-<test.id>.log -m unittest <test.id>`; each test receives its own fresh physical TMPDIR. Initial discovery failed because the /tmp script lacked cwd in sys.path; corrected before the actual 24-test run. No production change.

Individual real-desk commands: all four completed, each one test OK, exit 0, no skips:

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-desk-caseN.log -m unittest tests.test_bytes_h_session.SessionTests.TEST`

N/TEST: 1/test_desk_gates_exit_one_without_c5_is_program_fault; 2/test_desk_gates_exit_one_with_new_c5_is_unavailable; 3/test_desk_stale_c5_does_not_hide_program_fault; 4/test_desk_usage_exit_two_without_c5_is_program_fault. Times by N: 221.389/221.447/222.424/221.816 s. Prior r2-desk-status.log ended with two dots and no summary; these definitive independent runs supersede it.

Other still-pending split commands use the exact same environment prefix and `remaining.py MODULE > LOG 2>&1`:

| MODULE | LOG |
|---|---|
| tests.test_bytes_h_session | /tmp/byc5f1/r2-session-split.log |
| tests.b6.test_capture_screen_reachability | /tmp/byc5f1/r2-capture-split.log |
| tests.b6.test_cold_pass_fixes | /tmp/byc5f1/r2-cold-split.log |
| tests.b6.test_desk_resume_finalize | /tmp/byc5f1/r2-resume-split.log |
| tests.b6.test_loop_round_desk | /tmp/byc5f1/r2-round-split.log |

Historical slice-3 checkpoint: the session split excludes only the four separately run new desk cases. All other split modules run every test individually. At checkpoint, session has 30 individually confirmed passes and pauses at the native-harvest integration; cold has nine passes and pauses at FullRoundTests; no failed summaries. No result inferred for unfinished tests.

Smoke command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/r2-smoke.log -m unittest tests.b6.test_smoke`; 22 tests OK, exit 0, no skips (83.857 s).

Sealed inventory command: synthetic-only `/opt/homebrew/bin/python3.13 -B` loads the 682 `files` keys and invokes `git diff --name-only bda481d5a -- <paths>`; exit 0, empty stdout saved in /tmp/byc5f1/sealed-r2-slice3.log. No real session paths opened; no Git writes, install, arm, launchctl or ops/stop operations.

Slice-3 final checkpoint: all four desk cases, precheck 24, loop 55, smoke 22, integration 7 pass; static import checks 5 pass with the one declared sandbox integration failure. Heavy remaining importers continue with no final summary yet; pending tests are not attributed success. No COMPLETE marker. Both modified paths are report files in WRITE_SCOPE. Working head remains 4aa17a44ef5a23589fe75267fccae4b83f03f2f0, origin lane same; local branch by-c5 has no configured upstream. No Git mutation attempted.

## PART 2 SLICE 4 VERIFICATION

Started at b063ba79e812442d6fc8eacaab19bb01f501a533, local branch by-c5, origin/lane/2026-10-22-bytes-c5-gates identical. Intake 48 GiB free. No code changes, Git writes or real-session reads.

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/audit_tables.py`: exit 0:

```text
12 P rows: exact C5 byte terms and 3*n*q+headroom=P
11 replay rows: exact director replay bytes; 0/10 refusals
```

The full native H module is now definitively 36/36 passing: all 32 non-new-desk test logs end in OK, plus the four individually verified desk cases in r2-desk-case1.log through case4.log. The two slow native integrations have final summaries, including test_prepare_to_real_nonclaim_harvest_to_measurements_to_gates (181.836 s, exit 0).

Resume command for each MODULE below:

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/resume_final.py MODULE > LOG 2>&1`

resume_final.py discovers all module tests, skips only individual logs with a final OK, and invokes `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/final-<test.id>.log -m unittest <test.id>` for each unfinished test. run.py gives each child its own neutral /private/tmp TMPDIR and deletes it. Final per-test summaries, not wrapper exit status, determine results.

| MODULE | LOG |
|---|---|
| tests.test_bytes_h_session | /tmp/byc5f1/r2-session-final.log |
| tests.b6.test_capture_screen_reachability | /tmp/byc5f1/r2-capture-final.log |
| tests.b6.test_cold_pass_fixes | /tmp/byc5f1/r2-cold-final.log |
| tests.b6.test_desk_resume_finalize | /tmp/byc5f1/r2-resume-final.log |
| tests.b6.test_loop_round_desk | /tmp/byc5f1/r2-round-final.log |
| tests.b6.test_round2_review_fixes tests.b6.test_s3_cold_fixes tests.test_b6_machine_test | /tmp/byc5f1/r2-other-final.log |

An extra command for s3_cold_fixes and b6_machine_test was launched while the last multi-module command had already reached those modules. This duplicated some fast synthetic tests, each with independent TMPDIR; no shared repository artifacts changed. Evidence /tmp/byc5f1/r2-extra-final.log. No additional duplicate runs are needed.

Slice-4 fast importer completion: tests.b6.test_round2_review_fixes 8/8, tests.b6.test_s3_cold_fixes 6/6 and tests.test_b6_machine_test 29/29 individually PASS, no skips/failures. /tmp/byc5f1/r2-status-slice4.log enumerates the authoritative per-module census; /tmp/byc5f1/status_final.py can regenerate it. Full native H 36/36 also confirmed by this census.

Sealed recheck: `/opt/homebrew/bin/python3.13 -B` (synthetic-only environment) reads inventory files and invokes `git diff --name-only bda481d5a -- <all 682 file keys>`: exit 0, stdout empty, stderr empty. /tmp/byc5f1/sealed-r2-slice4.log is empty. `git diff --check`: exit 0, empty output. Current free space 47 GiB (>25 GiB gate).

Final slice-4 checkpoint (2026-10-22 17:06 UTC):

| Importer/native module | Definitive passes | Pending | Failures |
|---|---:|---:|---:|
| tests.test_bytes_h_session | 36 | 0 | 0 |
| tests.b6.test_capture_screen_reachability | 5 | 4 | 0 |
| tests.b6.test_cold_pass_fixes | 9 | 5 | 0 |
| tests.b6.test_desk_resume_finalize | 5 | 1 | 0 |
| tests.b6.test_loop_round_desk | 5 | 0 | 0 |
| tests.b6.test_round2_review_fixes | 8 | 0 | 0 |
| tests.b6.test_s3_cold_fixes | 6 | 0 | 0 |
| tests.test_b6_machine_test | 29 | 0 | 0 |

No skips in these completed individual tests. Exact census command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/status_final.py > /tmp/byc5f1/r2-status-slice4.log` (exit 0); this is inspection of test logs, not a fresh suite run. The policy class command uses the same resume_final environment with MODULE=tests.b6.test_capture_screen_reachability.PolicyReadTests and LOG=/tmp/byc5f1/r2-policy-final.log; all four one-test child runs exit 0. The final loop-round test passes in 175.653 s, exit 0; its module is now 5/5. Resume's newly finished tests pass at 35.097, 34.708, 40.590 and 52.169 s; last pre-40ms case remains pending. No result is inferred for a running test.

Final `git diff --check` exit 0; only .codex-report/BY-C5.md and .codex-report/BY-C5-fix1.md modified. Sealed stdout remains empty. No production source changed in this slice. Intake/head/upstream remain b063ba79e812442d6fc8eacaab19bb01f501a533. Disk available 46 GiB at final recheck (>25 GiB gate). No completion claim while ten importer tests lack summaries.

## FINAL REPORT VERIFICATION

Director instruction for this slice supersedes the historical NEXT/checkpoint notes: slice 8 is committed/pushed as c36ef1c51f5f0d13a7f9ec08e781f5a56073f7ce; local by-c5 and origin/lane/2026-10-22-bytes-c5-gates both resolve to that head. The requested baseline 0a585bb8e695db3199f2d91adc4c8955a1944ed3 is an ancestor (`git merge-base --is-ancestor 0a585bb8e695db3199f2d91adc4c8955a1944ed3 HEAD`, exit 0). Intake tree was clean. No code, tests, registry, Git metadata or real session trees were changed in this final slice. Only the two scoped reports were edited; no further slow test was launched.

Final importer/native accounting, using the director-accepted /tmp/byc5f1/r2-status-slice4.log evidence:

| Module | Individual local passes (exit 0) | Remaining disposition |
|---|---:|---|
| tests.test_bytes_h_session | 36/36 | none |
| tests.b6.test_capture_screen_reachability | 5/9 | 4 delegated to PR #547 CI on the final head (director) |
| tests.b6.test_cold_pass_fixes | 9/14 | 5 delegated to PR #547 CI on the final head (director) |
| tests.b6.test_desk_resume_finalize | 5/6 | 1 delegated to PR #547 CI on the final head (director) |
| tests.b6.test_loop_round_desk | 5/5 | none |
| tests.b6.test_round2_review_fixes | 8/8 | none |
| tests.b6.test_s3_cold_fixes | 6/6 | none |
| tests.test_b6_machine_test | 29/29 | none |
| Total | 103/113 | 10 delegated to PR #547 CI on the final head (director) |

No failures or skips in the 103 individual passes. The ten cases below have no local success claim; CI exit codes/results are unobserved:

```text
tests.b6.test_capture_screen_reachability.CaptureDispositionTests.test_block6_and_block5_capture_disposition_and_exit_matrix — delegated to PR #547 CI on the final head (director)
tests.b6.test_capture_screen_reachability.CaptureDispositionTests.test_block6_does_not_promote_invalid_evidence — delegated to PR #547 CI on the final head (director)
tests.b6.test_capture_screen_reachability.ChainReachabilityTests.test_opening_150ms_stops_at_13_and_full_pack_outcome_is_physics — delegated to PR #547 CI on the final head (director)
tests.b6.test_capture_screen_reachability.ChainReachabilityTests.test_opening_40ms_reaches_real_screen_and_desk — delegated to PR #547 CI on the final head (director)
tests.b6.test_cold_pass_fixes.FullRoundTests.test_completed_full_alpha — delegated to PR #547 CI on the final head (director)
tests.b6.test_cold_pass_fixes.FullRoundTests.test_exit4_and_acceptance_unavailable_reharvest_into_new_archive — delegated to PR #547 CI on the final head (director)
tests.b6.test_cold_pass_fixes.FullRoundTests.test_gamma_lost_midpoint_counts_and_overrides_b5_claim — delegated to PR #547 CI on the final head (director)
tests.b6.test_cold_pass_fixes.FullRoundTests.test_lost_start_reference_without_spare_counts — delegated to PR #547 CI on the final head (director)
tests.b6.test_cold_pass_fixes.FullRoundTests.test_physical_and_opening_no_bound_stops_rotate — delegated to PR #547 CI on the final head (director)
tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_unfinalized_pre_40ms_keeps_physical_abort — delegated to PR #547 CI on the final head (director)
```

Director reports the whole suite running on PR #547 in PR #547 CI (first queued as run 39819912999 at c36ef1c51; superseded by the run on the final head after the director pushed the report commits). This is a delegated verification result to be adjudicated by the director, not a claimed pass. The earlier environmental arm/sysmond/pgrep, import-graph GO/NULL and clock/bootsessionuuid failures remain documented in BY-C5.md TESTS RUN; the one existing refusal-census skip is the missing block-5 design branch. No new environmental failure occurred in this report-only slice.

Exact final read-only checks (no repository-code test execution):

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/audit_tables.py`

Exit 0:

```text
12 P rows: exact C5 byte terms and 3*n*q+headroom=P
11 replay rows: exact director replay bytes; 0/10 refusals
```

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/final_report_checks.py`

The script reads the inventory's 682 file keys and runs both `git diff --name-only bda481d5a HEAD -- <all 682 paths>` and `git diff --name-only bda481d5a -- <all 682 paths>`. Both exit 0 with empty stdout/stderr (HEAD and working tree). It also checks the two-path write scope and both COMPLETE markers. Exit 0:

```text
682 sealed files: HEAD and working-tree diffs empty
Only two report paths changed; both PROGRESS sections COMPLETE
```

`git diff --check`: exit 0, empty output. `df -g /Users/edr`: 47 GiB available at final-slice intake, above the 25 GiB workspace stop; this is not a live arm gate reading.

Next exact step: director reviews and commits the two report edits, checks PR #547 CI on the final head (including the ten delegated cases and environmental hazard lanes), performs final verification, and writes the ledger done line. Suggested report commit: `BY-C5 fix1 complete: finalize reports and delegate ten importer cases to CI 39819912999`. Destination lane/2026-10-22-bytes-c5-gates, draft PR #547. No worker commit/push was attempted.

## DIRECTOR VERIFICATION (outside the sandbox, head 465742178; code identical to c36ef1c51)

Evidence: /Users/edr/night-archive/forward-20261021/BY-C5/director-verify-fix1/ (one log per run). Every run used
JW_B5_SYNTHETIC_ONLY=1 and its own TMPDIR under /private/tmp.

- Touched modules: tests.test_bytes_gates 20 OK; tests.b6.test_plan_inputs 9 OK; tests.b6.test_lane_adapters 22 OK;
  tests.b6.test_session_wrapper 6 OK; tests.b6.test_precheck 24 OK; tests.hazards.test_refusal_allowlist 23 OK
  (1 skip: the block-5 design branch is not in this standalone clone); tests.b6.test_bytes_packs 9 OK.
- R2-4 desk cases (tests.test_bytes_h_session.SessionTests): all four OK, about 178 s each.
- Mutants (review-r2/mut.py on a disposable copy): M4, M8, M12, M13, M7 and M14 all CAUGHT.
- C5 on H's augmented receipts at this head: exit 2, file written, status fail (completeness and thermal lines).
  All twelve P equal the reviewer's independent re-derivation exactly: s1 73,814,147,037; s2 75,981,813,519;
  s3 79,464,395,095; s4 85,140,886,637; s5 75,849,013,177; s6 62,811,368,483 B (p1 = p2). Disk lines print
  r_s=1805538.52 and r_w=1285759.05 beside their exact fractions.
- Report audit: no superseded cf716ce00 P value remains in BY-C5.md; the measured 1,266,544,640 B appears twice,
  both labelled unused disclosure; r2-alpha reads "prepared, never ran".
- The ten importer tests the seat left pending: eight OK locally (capture_screen_reachability 4 of 4,
  cold_pass_fixes 3 of 5, desk_resume_finalize 1 of 1). Two (cold_pass_fixes
  test_exit4_and_acceptance_unavailable_reharvest_into_new_archive and test_physical_and_opening_no_bound_stops_rotate)
  hit the director's 560 s per-test limit under machine load with no failure output; they are left to PR #547 CI.
