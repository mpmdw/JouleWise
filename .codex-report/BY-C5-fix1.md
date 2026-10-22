## PROGRESS

- Done (slice 1): finding 2 committed-fixed input/provenance, missing/malformed unavailable behavior, measured-unused disclosure; finding 7 exact measured_c assertion and imported WAIT constant.
- Verified: 18 bytes_gates tests and 6 plan_inputs tests pass. Real augmented H main exits 2, writes /tmp/byc5f1/C5.json; all 12 P values exactly equal the director's committed-fixed targets. Reviewer re-derivation agrees. Sealed diff is empty.
- Done (slice 2): finding 3 stops max()/mean arithmetic on a model without sizing observations; records model.observations_missing and unavailable model lines, pack disk/sizing/span/clock candidates. main repro covers all 21 qwen35-122b rows never-ran; exit 2 and file written. 19 bytes_gates tests pass.
- Done (slice 3): finding 1 implementation shares sizing_label/valid_disk_terms with the native encoding. PRECHECK reads registered P, headroom zero; smoke adds ceil(2*B*m/n) retained bytes, disclosed in its receipt. Missing P skips disk judgment with disk.budget_missing. Eight plan_inputs tests pass, including twelve shapes at exact synthetic P/smoke boundaries; real run_precheck boundary/missing test passes.
- Next: complete real-H twelve-pack updated-P planner/precheck evidence; findings 4/8 final report revisions and importer checks. Import-graph NULL is confirmed environmental: arm-debug-step3.log reports sysmond service not found / pgrep Cannot get process list in instrument group census; director rerun required.
- Done (slice 3, finding 6): DriverLane smoke metadata records native 3*m*q+headroom as required_free_bytes, with pack_required_free_bytes/pack_member_count separately labelled. Real DriverLane + smoke.prepare/reducer integration passes (1 test, 15.219 s, exit 0; smoke-metadata-step3-final.log).
- Open: director owns real replay, commits/push and PR #547 CI. No real session trees read. Slice 1 committed by director as 36b16f0d5; slice 2 committed as 1b70fa136; slice 3 edits uncommitted on local by-c5. HEAD movement was external, between slices. Intake disk available 44 GiB (>25 GiB gate).
- Verified (slice 2): real H C5-step2.json equals slice-1 C5.json exactly; sealed-step2.log confirms all 682 paths have empty diff against bda481d5a, including working tree.
- Evidence /tmp/byc5f1/: C5.json, H-C5.stdout, rederive.log, step1-tests.log, plan-inputs-tests.log, sealed.log. run.py gives each invocation a fresh TMPDIR and deletes it afterward.

## SUMMARY

Fix round in progress; not complete.
C5 now uses H's committed 4,046,531,103 B fixed-artifact allocation.
The measured 1,266,544,640 B partial-session allocation is labelled unused disclosure.
The committed source path, SHA-256 and JSON pointer are recorded in C5.
Missing or malformed committed fixed input makes all disk lines unavailable, never a measured fallback.
All twelve augmented-H P values match the director's exact byte targets.
Findings 3 and 7 are fixed; finding 1 implementation and synthetic boundary checks are in place. Finding 6 smoke metadata is fixed and tested. Final report/real-H planner/check evidence remain in progress.

## FIX LOG

| Finding | Disposition / evidence |
|---|---|
| 1 major | Implementation fixed in plan_inputs.sizing_label/valid_disk_terms/registered_disk_terms/member_count and precheck.thresholds_for/run_precheck. Tests: DiskBudgetTests twelve-shape boundaries and non-BYTES identity; PrecheckTests.test_bytes_disk_bar_and_missing_record_through_run_precheck. Real-H integrated evidence pending. Desk wait registered in hazard_refusals.json desk_wait_sites. |
| 2 major | Code fixed in bytes_gates.committed_fixed/calculate/main. GatesTests.test_committed_fixed_source_override_and_missing_never_fallback checks integer delta, provenance, invalid types, missing CLI input and no fallback. Real H targets agree; planner equality pending. |
| 3 minor | Fixed in bytes_gates.calculate: guard absent model observations, record model.observations_missing; mark dependent packs unavailable. StoppedSessionTests.test_model_never_ran_cli_writes_unavailable_dependent_packs runs main on all 21 qwen35-122b rows never-ran and checks exit 2, JSON output, five unavailable model lines, s6 dependent null candidates, unaffected packs and llama clock. Full module 19 tests passes. |
| 4 minor | Form unchanged as directed; final R6 text/sensitivity disclosure pending. |
| 5 nit | No change needed: maximum of two whole summed bases; reviewer rederive confirms stated deltas. |
| 6 nit | Fixed in DriverLane.prepare_session after real smoke reduction: native requirement and count replace full-pack values; pack_required_free_bytes and pack_member_count preserve derivation labels. ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard executes the real DriverLane smoke path and checks metadata/notes against native count, q and headroom; exit 0. |
| 7 nit | Fixed: ReplayTests.test_nine_plus_h_replay_and_integer_boundaries uses exact int/int equality; plan_inputs imports SESSION_WAIT_BUDGET_S from sealed plan, unchanged. |
| 8 nit | Partial report correction; full final report refresh pending. Scope grant acknowledged for native raw-byte producer. |
| BY-MERGE | No change needed in this lane; hand-forward recorded below. |

## PRECHECK END TO END

Synthetic terms B=1,000,001 B, WAIT=7,200 B, fixed=19 B imply P=2,014,421 B exactly. All twelve production pack trees pass at P and refuse at P-1 via thresholds_for and real disk.measure/judge; same boundaries hold at P+ceil(2*B*m/n) with smoke. The real run_precheck test covers WAIT/START with and without smoke and START plus disk.budget_missing at zero free bytes when P is absent. Driver remains responsible for its pre-existing missing-budget LaneMissing hold.

Smoke decision: retained member bytes remain before full-session arm. Add ceil(c*B*m/n), with c=2, m from compose.registered_smoke_keep and n from the same real native-stage count used by the arm. No WAIT/fixed term is added again. The receipt records formula, B, c, m, n and integer result. Non-BYTES disk defaults are byte-identical.

Reviewer probe command: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/probe-step3.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/precheck_probe.py /Users/edr/code/JouleWise-by-c5` (exit 0). It prints for each of s1–s6 p1, with and without smoke: `precheck bar 0 ... precheck at free=P: PASS | at free=P(committed fixed): PASS`. This is the missing-registration flag path: the repository has no registered pass P yet. It is not proof of registered real-H boundary values; those are still pending.

## P PER SUB-PACK (committed fixed)

Source: configs/campaigns/bytes_mac_check/registration/sizing_b5.json at /packs/bytes-mac-check/disk_derivation/fixed_retained_bytes.
Real H C5 input and exact rational allowances are preserved in /tmp/byc5f1/C5.json; stdout /tmp/byc5f1/H-C5.stdout.
Rates r_s=1,805,538.5168827055 B/s; r_w=1,285,759.0452694688 B/s.
WAIT=12,999,877,322 B; committed fixed=4,046,531,103 B; measured fixed unused=1,266,544,640 B.
c=2; measured c=0.8020750916018277 (disclosure).

| pack | stream basis | wall basis | B | P | planner equality |
|---|---:|---:|---:|---:|---|
| bytes-s1-p1 | 21883930645 | 21697490999 | 21883930645 | 73814147037 | pending updated-P run |
| bytes-s1-p2 | 21883930645 | 21697490999 | 21883930645 | 73814147037 | pending updated-P run |
| bytes-s2-p1 | 22841465166 | 22967763886 | 22967763886 | 75981813519 | pending updated-P run |
| bytes-s2-p2 | 22841465166 | 22967763886 | 22967763886 | 75981813519 | pending updated-P run |
| bytes-s3-p1 | 24053464961 | 24709054674 | 24709054674 | 79464395095 | pending updated-P run |
| bytes-s3-p2 | 24053464961 | 24709054674 | 24709054674 | 79464395095 | pending updated-P run |
| bytes-s4-p1 | 27547300445 | 26855538139 | 27547300445 | 85140886637 | pending updated-P run |
| bytes-s4-p2 | 27547300445 | 26855538139 | 27547300445 | 85140886637 | pending updated-P run |
| bytes-s5-p1 | 22901363715 | 21700998244 | 22901363715 | 75849013177 | pending updated-P run |
| bytes-s5-p2 | 22901363715 | 21700998244 | 22901363715 | 75849013177 | pending updated-P run |
| bytes-s6-p1 | 14585071383 | 16382541368 | 16382541368 | 62811368483 | pending updated-P run |
| bytes-s6-p2 | 14585071383 | 16382541368 | 16382541368 | 62811368483 | pending updated-P run |

Reviewer rederive command (exit 0):
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/rederive.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/rederive.py /Users/edr/code/JouleWise-by-c5 /tmp/byc5f1/MEASUREMENTS.raw.json /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv 4046531103`
Compare P_committed_fixed column; its P column deliberately uses measured-fixed as the old baseline.

## STOPPED-EARLY C5

Finding 3 synthetic main output: completeness:qwen35-122b:check: fail; completeness:qwen35-122b:soak: fail; contention/cpu_contention/calibration_T10/resolvability/clock:qwen35-122b: unavailable; disk:bytes-s6-p{1,2}: unavailable; sizing:bytes-s6-p{1,2}: unavailable; clock:llama-70b: pass. Exit 2, JSON written. All 21 qwen35-122b rows (5 checks + 12 soaks + 4 test-7 probes) never-ran. Both s6 packs have null programmed_span_s, T_stream_max_s, required_free_bytes and disk_derivation; all other packs remain available. Flag model.observations_missing names qwen35-122b.

Real H main exits 2 because completeness and thermal lines fail (thermal_level 1), not a program fault.

## TESTS RUN

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

- Remaining authorized fix-round work listed in PROGRESS; no completion claim. Slice 3 finding 6 integration passed in /tmp/byc5f1/smoke-metadata-step3-final.log (earlier attempts needed venv fixture setup).
- BY-MERGE: pass1 ancestors carry changes to sealed files relative to main (plan.py, driver.py, hazards/clock.py and others); resolve in BY-MERGE, never in this lane.
- Director re-runs real replay with updated fixed from C5; prior 0/10 evidence uses old fixed. Reviewer reports committed-fixed also 0/10; worker has not read real session trees.
- Draft PR #547, last supplied CI: 20 pass, gate-ledger fails at cf716ce00. No network/CI query attempted.

## NEEDS_RULING

none

Slice 3 sealed recheck: /tmp/byc5f1/sealed-step3.log, all 682 paths, exit 0, empty stdout.

Slice 3 finding 6 exact test command (standard synthetic environment/fresh TMPDIR): `/opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/smoke-metadata-step3-final.log -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard`: 1 test, 15.219 s, exit 0. No real arm/install executed; installer seam is fake.

Director commit handoff: proposed `BY-C5 fix1 slice 3: PRECHECK shares registered P and smoke retention; smoke metadata records native requirement`. Push would be to lane/2026-10-22-bytes-c5-gates only; worker performed no Git writes.
