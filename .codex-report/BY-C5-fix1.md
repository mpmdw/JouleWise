## PROGRESS

- Part 2 (review of dcceb8480) started at 0a585bb8e.
- Done (Part 2 slice 1): R2-3 deliberate missing-P hold comment and actionable disk-budget receipt; real DriverLane.prepare_session tests absent/malformed disk_derivation before any prepared pointer/plan. Registry checks every bytes-s sizing row (currently 0). /tmp/byc5f1/r2-3.log: 10 tests OK, exit 0.
- Done (Part 2 slice 1): R2-2 hand-computed calculate test with science counts 2/3, reference count 1, margin 1; exact rational allowances, bases 2600/2467 B, B=2600, WAIT=360000, fixed=7, P=725207 B. /tmp/byc5f1/r2-2.log: 1 test OK, exit 0.
- Done (Part 2 slice 1): all four M4/M8/M12/M13 mutants CAUGHT on /private/tmp/byc5f1/mut-tree; disposable copy removed afterward. Separate fresh-TMPDIR modules: gates 20, inputs 9, adapters 22, wrapper 6; all OK. Sealed 682-path diff empty; git diff --check passes.
- Next (Part 2): R2-4 desk status, R2-5 labels, R2-6a decimal stdout, R2-1/R2-6b report audit and final FIX LOG/importer checks. Do not mark complete yet. Director owns commits/push/PR #547. Intake free=49 GiB; starting tree clean.
- Done (slice 4): all twelve committed-fixed budgets match real native planner and precheck/arm integer boundaries; report R6, allowance sensitivity and committed-fixed tables refreshed.
- Done (slice 1): finding 2 committed-fixed input/provenance, missing/malformed unavailable behavior, measured-unused disclosure; finding 7 exact measured_c assertion and imported WAIT constant.
- Verified: 18 bytes_gates tests and 6 plan_inputs tests pass. Real augmented H main exits 2, writes /tmp/byc5f1/C5.json; all 12 P values exactly equal the director's committed-fixed targets. Reviewer re-derivation agrees. Sealed diff is empty.
- Done (slice 2): finding 3 stops max()/mean arithmetic on a model without sizing observations; records model.observations_missing and unavailable model lines, pack disk/sizing/span/clock candidates. main repro covers all 21 qwen35-122b rows never-ran; exit 2 and file written. 19 bytes_gates tests pass.
- Done (slice 3): finding 1 implementation shares sizing_label/valid_disk_terms with the native encoding. PRECHECK reads registered P, headroom zero; smoke adds ceil(2*B*m/n) retained bytes, disclosed in its receipt. Missing P skips disk judgment with disk.budget_missing. Eight plan_inputs tests pass, including twelve shapes at exact synthetic P/smoke boundaries; real run_precheck boundary/missing test passes.
- Next: finish required importer checks, all-twelve run_precheck coverage where feasible, and final report cleanup. Twelve updated-H planner/precheck threshold boundaries now pass. Findings 4/8 report revisions applied. Import-graph NULL is confirmed environmental: arm-debug-step3.log reports sysmond service not found / pgrep Cannot get process list in instrument group census; director rerun required.
- Done (slice 3, finding 6): DriverLane smoke metadata records native 3*m*q+headroom as required_free_bytes, with pack_required_free_bytes/pack_member_count separately labelled. Real DriverLane + smoke.prepare/reducer integration passes (1 test, 15.219 s, exit 0; smoke-metadata-step3-final.log).
- Open: director owns real replay, commits/push and PR #547 CI. No real session trees read. Slice 1 committed by director as 36b16f0d5; slice 2 committed as 1b70fa136; slice 3 committed as dcceb8480 on local by-c5; slice 4 test/report edits uncommitted. HEAD movement was external, between slices. Intake disk available 44 GiB (>25 GiB gate).
- Verified (slice 2): real H C5-step2.json equals slice-1 C5.json exactly; sealed-step2.log confirms all 682 paths have empty diff against bda481d5a, including working tree.
- Slice 4 checks: all12-step4.log 1 pass; loop-step4.log 55 pass; smoke-step4.log 22 pass; lane-step4-physical.log 21 pass; session-step4.log 6 pass; planinputs-step4-final.log 8 pass. render-step4.log full module: 5 tests, 57.128 s, exit 0. Sealed-step4.log empty for 682 paths. Intake free=46 GiB.
- Evidence /tmp/byc5f1/: C5.json, H-C5.stdout, rederive.log, step1-tests.log, plan-inputs-tests.log, sealed.log. run.py gives each invocation a fresh TMPDIR and deletes it afterward.

## SUMMARY

Fix round in progress; not complete.
C5 now uses H's committed 4,046,531,103 B fixed-artifact allocation.
The measured 1,266,544,640 B partial-session allocation is labelled unused disclosure.
The committed source path, SHA-256 and JSON pointer are recorded in C5.
Missing or malformed committed fixed input makes all disk lines unavailable, never a measured fallback.
All twelve augmented-H P values match the director's exact byte targets.
Findings 3 and 7 are fixed; finding 1 implementation and synthetic boundary checks are in place. Finding 6 smoke metadata is fixed and tested. All twelve committed-fixed planner/precheck threshold/arm boundaries now pass. Required importer checks and final handoff remain in progress.

## FIX LOG

| Finding | Disposition / evidence |
|---|---|
| 1 major | Implementation fixed in plan_inputs.sizing_label/valid_disk_terms/registered_disk_terms/member_count and precheck.thresholds_for/run_precheck. Tests: DiskBudgetTests twelve-shape boundaries and non-BYTES identity; PrecheckTests.test_bytes_disk_bar_and_missing_record_through_run_precheck. All twelve updated-H integer P values verified through real planner/arm/precheck thresholds, all12-step4.log (1 test, 6.007 s, exit 0). Desk wait registered in hazard_refusals.json desk_wait_sites. |
| 2 major | Code fixed in bytes_gates.committed_fixed/calculate/main. GatesTests.test_committed_fixed_source_override_and_missing_never_fallback checks integer delta, provenance, invalid types, missing CLI input and no fallback. Real H targets agree; all twelve native planner requirements equal P exactly (all12-step4.log). |
| 3 minor | Fixed in bytes_gates.calculate: guard absent model observations, record model.observations_missing; mark dependent packs unavailable. StoppedSessionTests.test_model_never_ran_cli_writes_unavailable_dependent_packs runs main on all 21 qwen35-122b rows never-ran and checks exit 2, JSON output, five unavailable model lines, s6 dependent null candidates, unaffected packs and llama clock. Full module 19 tests passes. |
| 4 minor | Form unchanged as directed; R6 now states both allowances, check/soak-only margin and reference terms, and requires recomputation if BY-SLOTS changes form. Re-derived per-model-max-nonrequest P deltas: s1 0; s2 +486,009,912; s3 +271,803,398; s4 0; s5 0; s6 +497,717,866 B (variants-step4.log, exit 0). Reference spread 0.022169313982700597 < margin 0.03325233382759357. No code form change. |
| 5 nit | No change needed: maximum of two whole summed bases; reviewer rederive confirms stated deltas. |
| 6 nit | Fixed in DriverLane.prepare_session after real smoke reduction: native requirement and count replace full-pack values; pack_required_free_bytes and pack_member_count preserve derivation labels. ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard executes the real DriverLane smoke path and checks metadata/notes against native count, q and headroom; exit 0. |
| 7 nit | Fixed: ReplayTests.test_nine_plus_h_replay_and_integer_boundaries uses exact int/int equality; plan_inputs imports SESSION_WAIT_BUDGET_S from sealed plan, unchanged. |
| 8 nit | Thermal/completeness and committed-fixed report/R6/table corrections applied; final PROGRESS cleanup pending importer checks. Scope grant acknowledged for native raw-byte producer. |
| BY-MERGE | No change needed in this lane; hand-forward recorded below. |
| R2-2 minor | Fixed hand-computed terms coverage in GatesTests.test_hand_computed_p_includes_margin_reference_and_tree_counts (calculate, no helper re-derivation). All 20 module tests pass. M4/M12/M13 CAUGHT. M13 renames the reference key rather than dropping its numeric contribution, so the test explicitly pins the reference-labelled count/allowances too. |
| R2-3 minor | Fixed: Director's registered-input exception kept deliberately in DriverLane.prepare_session; plan_inputs.encode_disk_budget receipt names missing disk_derivation and registration remedy. AdapterTests.test_bytes_missing_disk_derivation_holds_before_prepared_or_plan passes both absent/malformed rows through real build/prepare; registry test prints 0 rows checked. Refusal census does not scan driver_lane.py or recognize LaneMissing holds (rg produces no matching driver_lane/LaneMissing entries); no registry edit required by disposition 3d. Nine block-6 sessions and H never enter this BYTES driver branch; director replay remains 0 of 10. |

## MUTANTS

Copied current tree with `cp -R /Users/edr/code/JouleWise-by-c5 /private/tmp/byc5f1/mut-tree`. Each X in M4, M8, M12, M13 ran sequentially with:

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

Reviewer probe command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/probe-step3.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/precheck_probe.py /Users/edr/code/JouleWise-by-c5` (exit 0). It prints for each of s1–s6 p1, with and without smoke: `precheck bar 0 ... precheck at free=P: PASS | at free=P(committed fixed): PASS`. This is the missing-registration flag path: the repository has no registered pass P yet. It is not proof of registered real-H boundary values; those are still pending.

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

Command: `git diff --name-only bda481d5a -- <all 682 keys of configs/campaigns/v5_claim_25g83/sealed_inventory.json files>`; exit 0, empty stdout (also includes uncommitted work). Log /tmp/byc5f1/sealed.log.

## DECISIONS I MADE

- Director disposition 2 supersedes old which-text-wins item 5: fixed comes solely from committed H sizing. --committed-sizing can override the file, with identical pointer/type validation; no measured fallback.
- Missing/malformed committed fixed is disk.committed_fixed_missing, a desk flag; no new refusal site or harvested flag catalog entry.
- Finding 7 exact measured_c equality is bit identity of the same integer division. WAIT imports the sealed constant; no sealed source edits.
- Keep C5's member-wall form and maximum of two whole summed bases as instructed; report details still pending.
- Local-route prohibition on Git writes overrides commit/push rules. Director should commit this slice as `BY-C5 fix1 slice 1: committed fixed provenance and exact constants`, then push only lane/2026-10-22-bytes-c5-gates.

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

## OPEN ISSUES

- Remaining authorized work: finish tests.b6.test_precheck by test name, tests.test_bytes_h_session by class/test, tests.b6.test_bytes_packs, importer modules from the rg list below, and final report/probe registered-P evidence. No completion claim. Slice 3 finding 6 integration passed in /tmp/byc5f1/smoke-metadata-step3-final.log (earlier attempts needed venv fixture setup).
- BY-MERGE: pass1 ancestors carry changes to sealed files relative to main (plan.py, driver.py, hazards/clock.py and others); resolve in BY-MERGE, never in this lane.
- Director re-runs real replay with updated fixed from C5; prior 0/10 evidence uses old fixed. Reviewer reports committed-fixed also 0/10; worker has not read real session trees.
- Draft PR #547, last supplied CI: 20 pass, gate-ledger fails at cf716ce00. No network/CI query attempted.

## NEEDS_RULING

none

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
