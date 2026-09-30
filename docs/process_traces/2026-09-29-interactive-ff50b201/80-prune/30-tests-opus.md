PRUNE-TESTS-OPUS

# Test-suite prune sweep (Opus 5.5 testing-stack investigator, session ff50b201, 2026-09-29)

Read-only. Only the rubric (`00-rubric.md`) was read in this directory. Investigated on a detached worktree at `origin/main` 32ff9013 (`/Users/edr/code/JouleWise-wt-prune-tests-ff50b201`). Every local run used `python3 -B` with a refusal shim (fake `sudo`/`powermetrics`/`systemsetup` first on PATH plus a `sitecustomize` that refuses any Python-started argv naming them). The shim's refusal log stayed empty for every run. No real sampler, sudo or systemsetup was started.

The rubric is applied to tests. The question for each test is which number it protects: joules per request, calibration, the detection floor, a printed paper value, or the custody of any of these.

## 0. Measured facts (all executed unless marked ESTIMATE)

| Fact | Value | How measured |
|---|---|---|
| Test modules | 269 (`tests/**/test_*.py`) | unittest discovery |
| Tests loaded | 7,540 executions, 7,403 unique ids | `unittest.TestLoader().discover('tests')`, walked |
| Duplicate executions | **137**: `LaunchConsumptionV2Tests` (32 tests) runs 3× because `test_cli_run` and `test_detection_floor` import the class at module level; `PairAuthenticationTests` (9 tests) is imported by other modules the same way | duplicate `test.id()` count |
| Test code vs production code | tests 267,624 Python lines (incl. 6,347 helper lines) vs production 214,442 (`joulewise/` 139,859 + `scripts/` 74,167). Tests are 1.25× production. The S1 integration branch (unmerged) adds 9,288 more test lines against about 1,830 non-test lines | `wc -l` at 32ff9013 and `git diff --stat` |
| Growth | test lines 45,782 (07-15), 77,759 (08-01), 133,324 (08-15), 185,303 (09-01), 229,600 (09-15), 267,624 (09-29): 5.8× in 2.5 months. Production grew 4.1× over the same period | `git cat-file` over dated main commits |
| Non-code fixtures | `tests/` is 28 MB, of which `tests/fixtures` is 16 MB; 254 non-Python files | `du`, `find` |
| Hosted CI, latest completed main run (36382310251, 09-28) | 23 jobs, **462 runner-minutes**, about 61 min wall. Ordinary shards were badly unbalanced: 11.7 / 15.1 / 15.9 / 16.4 / 28.8 / 29.5 / 39.4 / 39.8 / 44.6 / 51.7 / 55.4 / **56.8 min** | `gh run view --json jobs` |
| Sum of module seconds per interpreter (hosted) | about 13,090 s on 3.11 and 12,260 s on 3.13 in ordinary and exclusive jobs, plus calibration-exits (763 s on 3.13) | parsed `MODULE PASS … seconds=` lines from the run log |
| **Concentration** | the **top 25 modules = 89.5 %** of hosted module-seconds. **Four `test_scored_*` modules = 6,371 s = about 43 %** (`test_scored_reduce` 2,523, `test_scored_packer_stress` 2,304, `test_scored_ownership_forgery` 1,401, `test_scored_packer_fuzz` 143) | same log; max over the two interpreters |
| Timing map | `scripts/test_timings.json` was last re-measured 2026-09-15 (CI-TRIM-02): 230 modules, and **37 current modules are unmapped**, including every `test_scored_*` module. Unmapped modules get the 21.8 s mean weight, so the 2,500 s scored modules were packed as if they took 22 s. **That is the shard imbalance above** | file read vs discovery |
| Skips (hosted Linux, 3.13) | 159 per interpreter (grouped in §3). The owner's figure of 109 is the Mac count, not re-measured here | CI log `skipped '…'` lines |
| Assertions | 27,892 assert calls; **407 (1.5 %)** are mock-interaction asserts (`assert_called*`, `call_count`, `mock_calls`) in 78 modules | grep |
| Structurally identical test bodies | **169 of 7,294 test functions (2.3 %)**: the AST is identical once literals and names are erased (`test_cli_run` 13, `test_scored_packer` 11, `test_check_gate_ledger` 10 …). This is a lower bound on near-duplicates | AST hash per test body |
| Tests that open a doc/`.md` and assert a substring or regex | **about 156** (heuristic; includes paper-wording lints that are legitimately number-adjacent) | AST + regex scan |
| sha256 literals pinned in tests | **305 literals in 60 modules**. 129 of the 1,746 commits that touched tests changed a 64-hex literal. 259 pin lines were replaced in 55 commits. One module (`test_d117_floor_qwen25_1p5b_plan`) alone has had 81 pin lines replaced, and 21 of its 28 commits changed a digest | `git log -G`, `git log -p` |
| Sleep-based timing | 121 `sleep(` sites, nearly all inside fake child processes. Only **3** follow the pattern "sleep, then assert something is absent", and those can pass falsely on a slow host (`test_arm_readiness_evidence_author.py:926,945`; `test_calibration_exits.py:3261`) | grep |
| `d117-production-proof.yml` | `workflow_dispatch` only. Last run 2026-08-16 (failure, then cancelled). Its own header says the matrix "is not runnable at current main" | `gh run list`, file header |

## 1. Module table (the 25 slowest by hosted seconds, then a seeded random 25 of the remaining 244; seed 20260929)

"Tests" is the unittest-loaded count by defining module. "CI s" is the hosted module seconds from run 36382310251 (max of 3.11 and 3.13). "Local" is this Mac under load average 9–12 during the spot runs.

**The 25 slowest (1,846 tests; 89.5 % of hosted seconds)**

| # | Module | Tests | CI s | Local s | Verdict | Deciding reason |
|---|---|---|---|---|---|---|
| 1 | test_scored_reduce | 64 | 2,523 | 1,188 | **THIN** | This is the A292 headline reducer, and it has produced no number yet. The named boundary tests kill the required mutants in 5 s (M4, M5 in §2). `test_differential_oracle_200_nights` alone is 1,119 of 1,188 s locally (94 %); every other test is under 12 s. Move the 200-night differential to nightly or a paths-filtered job; keep the R-witness sweep (2.5 s) per push |
| 2 | test_scored_packer_stress | 2 | 2,304 | 962 | **THIN** | It holds the only unique catch in the sample: M2, caught at seed 291013 case 1 in **4 s**. The other 299 sequences × 2 seeds add time, not catches. Keep 1–2 cases per push and run the full corpus nightly |
| 3 | test_scored_ownership_forgery | 10 | 1,401 | 597 | **THIN** | 4 corpus/property tests take 594 of 597 s locally. The named seal regression (0.2 s) killed M1. The corpus only "caught" M2 through a pinned total roster count (1868 ≠ 1907), not through the ownership predicate. Keep the 6 named tests per push |
| 4 | test_calibration_writer_crash_matrix | 20 | 954 | – | KEEP (one interpreter) | Calibration-ledger custody under SIGKILL at every stage protects calibration. Filesystem behaviour does not differ between 3.11 and 3.13 |
| 5 | test_reduce | 132 | 675 | – (97 s for 178 light tests incl. 3 other modules) | **KEEP** | J-per-request integration, clock anchor, stale-calibration refusal. The D-078 time-anchor defect is exactly this class. M6 in §2 |
| 6 | test_p2038_production_path | 8 | 635 | – | **KEEP** | The real PowermetricsTelemetryAdapter child process, then the real parser, controller, reducer and strict validator, run on committed plists. This is the only end-to-end J path in CI |
| 7 | test_night_agent_install | 82 | 588 | 681 | **THIN** | 8 `*_product` fault×state matrices take 619 of 681 s locally, driven by 5 s fake-launchctl timeouts. They test launchd plumbing, not a number. Collapse them to one cell per outcome class (OK / FAILED / UNKNOWN) |
| 8 | test_validate_powermetrics_fiducial_derivation_only | 27 | 529 | 201 | KEEP, thin time | This is fiducial (calibration) derivation custody. 6 live-capture tests take 175 of 201 s at real-time scale; lower `--time-scale-for-test` |
| 9 | test_receipt_histsem | 73 | 497 | – | **KEEP** | Historical receipt semantics for published receipts. The `fences` job also runs `verify_receipt_histsem.py --require-published` |
| 10 | test_run_campaign | 261 | 345 | – | KEEP | The campaign runner writes the bundles that every number comes from. Imported by 3 modules as a fixture home |
| 11 | test_whole_window_selection | 57 | 297 | – | **KEEP** | The whole-window claim barrier (which window rows may feed a claim) |
| 12 | test_evidence_night | 166 | 250 | – | THIN (est. −20 %) | Night-prepare composition. Mostly orchestration; it guards arming, not arithmetic |
| 13 | test_launch_window | 38 | 242 | – | THIN (est. −20 %) | Launch ceremony plumbing. 29 mock-interaction asserts |
| 14 | test_issue_calibration_acceptance_generation | 156 | 220 | – | KEEP | The calibration acceptance regime (which calibration captures are admissible). CI time grew from 78 s (09-15 map) to 220 s |
| 15 | test_battery_float | 18 | 146 | – | **KEEP** | Battery-float confound: on battery, the wall/rail power differs, which changes J |
| 16 | test_scored_packer_fuzz | 6 | 143 | 53 | **THIN → nightly** | 0 of 3 packer mutants caught (M1, M2, M3 in §2) |
| 17 | test_run_night | 237 | 107 | – | KEEP core, THIN | The night driver. 88 mock-interaction asserts, all on courier/killpg behaviour. CI time grew from 7 s to 107 s since 09-15 |
| 18 | test_powermetrics_fiducial | 75 | 104 | – | **KEEP** | Fiducial calibration (the powermetrics-to-meter relation) |
| 19 | test_collector_analysis_manifest_id | 16 | 102 | – | KEEP | A collected bundle binds to the one finalized v3 manifest, so it cannot be re-labelled into another analysis |
| 20 | test_analysis_integration | 116 | 94 | – | **KEEP** | The final claim artifact, derived end to end |
| 21 | test_uncertainty_evidence | 58 | 89 | – | **KEEP** | Uncertainty and half-width evidence (the error bar printed beside J). CI time grew from 0.9 s to 89 s since 09-15 |
| 22 | test_custody_mode_inventory | 7 | 85 | – | KEEP (lint) | An AST census of custody replay-vs-issuing call sites against an allowlist. It is cheap in tests but carries allowlist upkeep |
| 23 | test_controller | 74 | 79 | – | KEEP | Request/phase timing marks, which set the integration windows |
| 24 | test_arm_readiness_evidence_t0 | 78 | 71 | – | THIN (est. −15 %) | T0 process census and decoys. It guards quiet-machine admission (contamination), but the decoy pattern-by-pattern coverage is heavy. Keep one positive and one negative decoy per pattern class |
| 25 | test_install_night_agent | 65 | 67 | – | THIN | Installer pin policy. It overlaps #7, which imports this module's fixture. CI time grew from 8.5 s to 67 s since 09-15 |

**Seeded random 25 of the other 244 modules (464 tests; 120 CI s in total)**. Classified by two read-only sub-agents from docstrings, test names and 3–5 bodies per module. I spot-verified their load-bearing claims (e.g. `test_render_results_fills.py:151` overwrites `RENDERER.REGISTRY_ROWS`; `test_preflight` targets `docs/process_traces/2026-08-28-live-smoke/preflight.sh`; nothing in `joulewise/`, `scripts/` or `.github/` calls `axi_sb_static_batch_spike.py` or `axi_sc_spec_decode_spike.py`).

| Module | Tests | CI s | Verdict | Deciding reason |
|---|---|---|---|---|
| test_2k_amplification | 13 | 0.1 | DELETE | NVIDIA "Slice 2K" edge layer. No hardware contact and no NVIDIA number. About 4 of its tests duplicate `test_node_worker` |
| test_analysis_manifest_v3 | 19 | 1.0 | KEEP | The frozen decode contrast manifest (arms, blocks, Holm family) |
| test_arm_readiness_evidence_author | 24 | 53.5 | THIN −3 | It pins another module's exact test count (23 run / 3 skipped), freezes an import list, and mirrors an import-time assertion. Also contains 2 of the 3 "sleep 1 s, then assert absent" tests |
| test_audit_amplification | 8 | 5.5 | KEEP | The raw plist re-derives `power_trace.csv` exactly. An edited trace would integrate into the wrong J |
| test_axi_analysis_manifest | 23 | 0.2 | THIN −10 | The AP-SPEC v2 group has only fixture manifests. Keep the attempt-ledger tests (first eligible attempt is used, no retry-until-good) |
| test_axi_sb_spike | 18 | 0.0 | DELETE | A closed July feasibility spike (`feasibility_not_energy`). Only tests call it |
| test_bridge | 62 | 24.0 | THIN −15 / move | Agent-bridge tooling; no number. Has 5 doc-drift prose tests and about 10 near-duplicate session-close variants |
| test_calibration_ledger | 95 | 4.0 | THIN −20 (cold check) | The D-079 bootstrap-import cluster is completed history, and one test is permanently skipped (`/private/tmp/d079-*`). Keep reservation, finalization and bracket |
| test_capture_pipeline_era | 10 | 2.4 | KEEP | Superseded-clock bundles must never reach claims (D-078) |
| test_d117_floor_qwen3_v5_generate | 13 | 14.8 | KEEP | The current v5 floor packs, prompt pin and prefill length |
| test_dominance_closeout | 3 | 2.1 | THIN −2 | One test patches a set and then asserts that two sets differ, which is a tautology. Fold the survivor into `test_d165_dominance_closeout` |
| test_environment_admission | 2 | 0.6 | KEEP | Thermal-pressure refusal. Throttling changes J |
| test_measurement_liveness | 18 | 0.0 | KEEP | No measuring while another chain is live, because concurrent load inflates power |
| test_mint_floor_artifact | 40 | 1.1 | THIN −5 (cold check) | The detection-floor mint core is load-bearing. The A10/Window-C era pins are retired |
| test_paper_rendering | 6 | 1.6 | KEEP, −1 | Custody-issued values only. Drop the "feature still absent" tripwire |
| test_paper_reported_energy | 26 | 0.8 | KEEP | The reported J mean and half-width formulas (stratified, mean of ratios) |
| test_paper_successor_migration | 10 | 0.6 | THIN −7 | Prose regexes and paragraph sha pins for a one-time round-7 migration |
| test_preflight | 9 | 0.2 | DELETE | Tests a one-off runsheet under `docs/process_traces/` |
| test_render_results_fills | 29 | 0.9 | DELETE (port 3; cold check) | Runs against a frozen pre-v5 vocabulary that production never uses, and includes a self-hash tautology |
| test_run_night_probe_worker_cadence | 1 | 0.2 | KEEP / merge | The only test of the failed-cadence receipt |
| test_s0_blocked_enumeration | 1 | 3.5 | THIN | Retired S0/CRASH taxonomy plus an exact skip-count ratchet. Keep "no expectedFailure" |
| test_scored_registration | 3 | 0.0 | KEEP | Compact and behavioural |
| test_sealed_bundle_compatibility | 4 | 0.9 | DELETE | WO-003 July gate with no callers. Its core is also covered in `test_corpus_strict_validation` |
| test_window_status_guard | 11 | 1.0 | KEEP | No git or network traffic during a live window, since that traffic would add energy to the measurement |
| test_write_derivation_night_inputs | 16 | 0.6 | KEEP, −2 | Calibration identity epoch and T1 bindings |

**Extrapolation (ESTIMATE).**
- Random sample: about 73 tests DELETE and about 65 THIN out of 464, so about 25–30 % of the long tail by count. The sub-agents lean toward cutting, so I discount to **15–25 % of the ~5,550 tests outside the top 25, i.e. about 800–1,400 tests and about 20,000–40,000 lines**.
- By time, the long tail is cheap: the 244 modules together cost only about 1,470 hosted s. **Test-count pruning buys maintenance, not wall-clock; wall-clock lives almost entirely in the top 25.**
- Uncertainty: 25 modules out of 244, so the 95 % interval on the proportion is roughly ±10 points.

## 2. Mutation spot-checks (scratch `git archive` exports under the session scratchpad; production files mutated there only)

Each mutant is one edit to production code in a `git archive HEAD` copy, with `docs/` copied in because some tests read process docs. Baseline M0 is the unmutated copy, and it was green for every set used. "Caught" means at least one test went red.

| Id | Mutation (production file) | Fast named tests | Slow corpus/property tests | Reading |
|---|---|---|---|---|
| M1 | `scored_packer._conserve`: drop `not …["superseded"]` (a superseded live block counts as owning its items) | `test_scored_packer` + `_registration` + `_roster_checker` (68 tests, 15 s): **survived**. `test_scored_ownership_forgery.test_named_seal_regressions` (0.2 s): **caught** (`refused:inv_11` ≠ `refused:stale_derived`, case B1-singles-voided) | fuzz (55 s): survived. stress (951 s, both tests): **survived** | A named regression is enough; the corpus is not needed |
| M2 | `scored_packer._eligible`: capacity `>` → `>=` | 68 fast tests: **survived**. Fuzz: **survived** | **stress caught it at seed 291013 case 1 in 4.2 s** (checker INV-23 disagreement). Forgery `test_legal_corpus` caught it after 226 s, and only through its pinned total (`1868 != 1907`), not through a violation | The one genuinely unique catch in the sample. It needs 1 case, not 600 sequences |
| M3 | `scored_packer._eligible`: delete the same-level different-parent skip | **caught** by `ScoredPackerTests.setUpClass` (`inv_24 parent spread`) | not run | Named tests suffice |
| M4 | `scored_reduce`: `cap_bound` `>` → `>=` (a required mutant in the module's own M8 ledger) | `-k cap` (8 tests, 5 s): **caught** by 5 | not needed | The 200-night differential is not needed for this required mutant |
| M5 | `scored_reduce._derived`: `capped` `>=` → `>` (also a required mutant) | `-k cap`: **caught** by 5 | not needed | Same |
| M6 | `reduce._integrate` (interval-average branch): drop the left-edge clip `max(start_s, …)`, so energy before the window start is counted | `test_reduce` without its 3 declared heavy tests, plus `test_aggregate`, `test_phase_share`, `test_audit_amplification` (178 tests, 97 s): **caught by 10**, including `test_powermetrics_interval_partial_edges_use_overlap_not_trapezoids`, `test_frozen_050_dispatch_reproduces_recorded_gross` and `test_051_golden_summary` | not needed | Confirms the KEEP core for J per request is live and sharp. The 3 heavy `test_reduce` tests (477 CI s) were not needed for this class. They cover the clock-anchor / cadence-boundary class, which is a different class (D-078) and should stay |

Side finding: `test_reduce.test_d138_reduce_source_bytes_remain_at_issued_pin` pins the *source bytes* of `reduce.py`, so any edit at all turns it red. That is intentional custody for the issued D-138 calibration. It is listed so nobody mistakes it for an arithmetic check.

## 3. Outdated: skips (hosted Linux 3.13, 159 per interpreter), grouped

| Group | Count | Reason text | Verdict |
|---|---|---|---|
| Retired site/capsule lane (D-136) | **73** | `site-lane test (site workflow; set JOULEWISE_SITE_CONTENT_TESTS=1)` in `test_pack_capsule` (43) and `test_build_site_parsers` (30). `site.yml` is dispatch-only | **DELETE** (or move under `site_capsule/`). They never run in any gate |
| Darwin-only | 18 + 5 | `requires Darwin fchflags/st_flags` (`test_reauthor_clean`); native QoS; `kern.bootsessionuuid`; POSIX_SPAWN_START_SUSPENDED; macOS census | KEEP. They run on the Mac, so this is correct behaviour |
| Optional libraries absent on CI | 9 + 2 + 2 + 1 + 1 | matplotlib (`test_report`), markdown-it-py, jsonschema, tokenizers | KEEP, or install the extras in one CI job |
| Retained corpora absent (runs/, window corpora, harvest archives, D-079 `/private/tmp` inputs, MATH source, tokenizer mirrors) | about 22 | e.g. `the 2026-09-22 harvest archives are not on this machine`, `lead-reviewed D-079 import inputs are unavailable` (a `/private/tmp` path that no longer exists anywhere, so it is permanently skipped) | THIN: keep the corpus-gated replay tests that fence printed paper values (`test_paper_replay_fence`, `test_paper_round7_artifacts`); delete the permanently unsatisfiable ones (the D-079 `/private/tmp` inputs) |
| Waiting on work that is not coming soon | 3 + 2 + 1 + 1 + 1 | `U2 successor engine pending` (`test_calibration_live_three_window` ×3); `STRUCTURAL-BLOCKED: … _v2 family …` / `… _v5 fixture omits …`; `successor member not minted yet; shape check is vacuous`; `split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION` / `full-fixture proof runs in d117-production-proof` (that workflow has been dead since 08-16) | THIN: delete or convert to tracked TODOs. A skipped test protects nothing |
| Filesystem-specific | 1 | `temporary filesystem is case-sensitive` | KEEP |

## 4. Ranked THIN/DELETE list (top 20), ranked by (cost saved) × (confidence it protects no number)

"CI s" is hosted seconds saved per interpreter per full run. Every row is an ESTIMATE unless marked measured.

| Rank | Item | Tests affected | CI s saved per interpreter | Protects a number? | Confidence it protects none | Cold Fable check? |
|---|---|---|---|---|---|---|
| 1 | **Move the scored corpus/property sweeps off the per-push path**: stress beyond its first 1–2 cases; forgery `legal_corpus`, `legal_corpus_seal`, `triple_seal_property`, `pairwise_seal_property`; fuzz (6); scored_reduce `differential_oracle_200_nights` (94 % of that module). Run them nightly, or only when `joulewise/scored_*` or `tests/*scored*` change | about 12 tests moved, 0 deleted | **≈ 5,800** (ESTIMATE from measured 2,523 + 2,304 + 1,401 + 143, less about 500 kept) | No: the A291/A292 lane has issued nothing | High. M1, M3, M4 and M5 were caught by named tests; M2 was caught in 4 s by case 1 | No (no published claim path). Tell the A291 lane owner |
| 2 | **Refresh `scripts/test_timings.json`** (37 modules unmapped since 09-15), or let unmapped modules inherit their last hosted time | 0 | 0 seconds, but ordinary shard wall-clock falls from 57 min toward the calibration-exit floor (about 13–19 min) once #1 lands | No | Certain (scheduling hint only) | No |
| 3 | **Main pushes run only 3.13**; the 3.11 floor moves to a weekly cron | 0 | ≈ 13,900 runner-s per main push (a whole interpreter) | No. Production nights are 3.13 and local work is 3.14 | High | No |
| 4 | `test_night_agent_install` `*_product` matrices collapsed to one cell per outcome class | 0 tests, many cells | ≈ 450 (8 tests = 619 of 681 s locally) | No (launchd plumbing) | High | No |
| 5 | Exclusive calibration jobs (`calibration_exits`, `writer_crash_matrix`) on 3.13 only | 0 | ≈ 1,700 per main push | Yes (calibration custody), but not interpreter-dependent | High that 3.11 adds nothing | No |
| 6 | **Delete the site/capsule tests** (`test_pack_capsule` 43, `test_build_site_parsers` 30, `test_build_capstone` 2). 73 of them are permanently skipped; the lane was retired (D-136) | 75 | ≈ 0 (2,540 lines) | No | Very high | No |
| 7 | **Stop the 137 duplicate executions**: move `LaunchConsumptionV2Tests` and `PairAuthenticationTests` fixture methods into helpers, or import the module rather than the class | 137 runs | small (ESTIMATE < 60) | No (pure duplicate) | Certain | No |
| 8 | Delete closed spikes and retired-script tests: `test_axi_sb_spike` 18, `test_axi_sc_spike` 20, `test_preflight` 9, `test_sealed_bundle_compatibility` 4, `test_render_results_fills` 29 (port 3 arithmetic tests first) | about 77 | ≈ 3 | No. Only tests call them | High | Yes for `render_results_fills` (paper-fill renderer) |
| 9 | Move the agent/orchestration tooling tests (`test_bridge`, `test_claude_bridge_mcp`, `test_codex_app_bridge`, `test_codex_bridge_observer`, `test_magistrate_watchdog*`, `test_install_magistrate_watchdog`, `test_check_gate_ledger`, `test_validate_gate_packet`, `test_coldgate_*`; 11 modules, 320 tests) to a non-blocking tooling job, and cut about 15 prose/near-duplicate tests in `test_bridge` | 320 moved, about 15 cut | ≈ 55 | No (process hygiene only) | Very high | No |
| 10 | Lower `--time-scale-for-test` in the 6 live-capture tests of `test_validate_powermetrics_fiducial_derivation_only` | 0 | ≈ 300 (ESTIMATE; they take 175 of 201 s locally) | Yes, but only time changes | Medium (timing-sensitive custody) | No |
| 11 | Retire the permanently dead skips: `U2 successor engine pending` ×3, `STRUCTURAL-BLOCKED` ×2, `successor member not minted yet`, D-079 `/private/tmp` inputs, `d117-production-proof` partition skips (that workflow has been dead since 08-16) | about 10 | 0 | No, because a skipped test protects nothing | High | Yes for the D-117 proof pair (it once discharged D-130) |
| 12 | Delete test-only process-doc prose checks: `test_coldgate_charter_v3` 3, `test_midcampaign_cure_generation_docs` 2, `test_paper_successor_migration` prose 7, the bridge doc-drift 5, exact-count ratchets (`test_s0_blocked_enumeration`, the 23/3 pin in `test_arm_readiness_evidence_author`). **Keep** the paper number-wording lints (`test_paper_terms_lint`, `test_claims_lint`, `test_paper_replay_fence`) | about 25 | ≈ 10 | No | High | No |
| 13 | Pare the D-117 Qwen2.5 v1–v3 plan tests (`test_d117_floor_qwen25_1p5b_plan` 20, `_7b_plan` 20, `test_d117_decode_contrast_plan` 25) to one frozen-digest check per pack. That family is superseded by the v5 Qwen3 packs. It has the highest repin churn in the suite: 21 of 28 commits changed a digest, and 81 pin lines were replaced in one module | about 50 | ≈ 55 | Possibly. The 7B Qwen2.5 floors are listed "evidence-bearing" in CLAIMS_STATUS | Medium | **Yes** |
| 14 | NVIDIA node lane: delete `test_2k_amplification` (it duplicates `test_node_worker`); keep the rest of the lane as parked (Ed's heterogeneous-hardware horizon) | 13 | ≈ 0 | No NVIDIA number exists | High | No |
| 15 | `test_axi_analysis_manifest` AP-SPEC v2 group (~10) and `test_analysis_manifest_v2` (5): these are fixture-only manifests | about 15 | ≈ 0 | No current number | Medium-high | No |
| 16 | `test_calibration_ledger` D-079 bootstrap/historical-import cluster (~20) plus the always-skipped D-079 test | about 20 | ≈ 2 | Calibration history: rows imported once and already in the ledger. Reader-side import-marker tests stay | Medium | **Yes** |
| 17 | `test_mint_floor_artifact` A10/Window-C era pins (~5) | about 5 | ≈ 0 | Retired floors (D-110) | Medium | **Yes** |
| 18 | Tautologies and self-restating tests: the `render_results_fills` self-hash, the `test_dominance_closeout` set-difference test, the `test_paper_reported_energy` literal `(14.5+49.5)/2 == 32`, and `test_paper_rendering`'s deferred-feature tripwire | about 5 | 0 | No | Very high | No |
| 19 | Rewrite the three "sleep, then assert absent" tests (`test_arm_readiness_evidence_author.py:926,945`, `test_calibration_exits.py:3261`) as wait-for-condition checks with a bound. On a slow host they pass falsely, so this is a fix, not a cut | 3 | ≈ 2 | Custody-adjacent | n/a | No |
| 20 | **S1 branch, not yet on main**: `tests/bfgs_fixtures.py` (370 lines) switches production refusal functions off for listed test IDs, with two closed ID lists (first form 40, then 35 after commit cdfb27ce withdrew five; second form 6, ruled to 11), and every grant is ruled by the lead or a cold gate. The cheaper equivalent is one fixture builder that emits genuine, digest-bound battery evidence, so no switch and no ID list is needed. What is lost is a per-ID audit trail of which tests bypass the gate. `tests/sampler_launch_fence.py` (319 lines) is a sound, cheap guard; keep it | future: every S1 round | 0 today; saves future rulings | The switch touches claim-path refusals (`floor_extraction`, `analysis_engine/inputs`, `whole_window`) | Medium | **Yes** |

**Totals (ESTIMATE).** Items 1–20 remove or move about **700–800 tests** (about 350 deleted, about 330 moved to non-blocking or nightly jobs, 137 duplicate executions removed). They cut **≈ 6,600 hosted s per interpreter per run** (about 47 % of module-seconds, nearly all from #1, #4, #10). With #3 and #5, a main push drops from **462 runner-min to about 125**, and the critical path from **about 61 min to about 20 min**. Broader long-tail pruning (§1 extrapolation, 800–1,400 tests) adds maintenance savings but almost no wall-clock.

## 5. Load-bearing KEEP list (tests that guard a number or its custody)

These guard a number or its custody. Keep them whole. The ones marked (thin time) keep every assertion and only need to run faster.

- **Joules per request (arithmetic and capture)**
  - `test_reduce`: trapezoid and interval-overlap integration, clock anchor across cadence boundaries, and the D-078 regression goldens. Mutation M6 caught by 10 tests.
  - `test_p2038_production_path`: the real adapter, parser, controller, reducer and strict validator, end to end.
  - `test_powermetrics` and `test_adapters_powermetrics`: the parser.
  - `test_audit_amplification`: raw plist to trace, re-derived exactly.
  - `test_aggregate`, `test_phase_share`, `test_controller`: phase windows.
  - `test_capture_pipeline_era`: superseded clock method barred from claims.
  - `test_load_transition_alignment`.
  - `test_idle_admission` and `test_idle_dependence`: idle subtraction.
  - `test_environment_admission`: thermal pressure.
  - `test_measurement_liveness` and `test_window_status_guard`: no concurrent load.
  - `test_battery_float`, `_consumers`, `_sweep`: battery confound.
  - `test_quiet_admission`, `test_quiet_guard`, `test_quiet_guard_process`: background contamination. The 2026-07-17 screensaver contamination of 43/50 is the precedent.
- **Calibration**
  - `test_calibration_ledger` core: reservation, finalization, bracket and derivation sessions.
  - `test_calibration_bracketing`, `test_calibration_exits`, `test_calibration_writer_crash_matrix` (one interpreter).
  - `test_powermetrics_fiducial`, `test_validate_powermetrics_fiducial`, `test_validate_powermetrics_fiducial_derivation_only` (thin time).
  - `test_issue_calibration_acceptance_generation`, `test_write_derivation_night_inputs`, `test_epoch_continuation`.
- **Detection floor**
  - `test_detection_floor`, `test_floor_extraction`, `test_floor_mint_estimator`.
  - `test_mint_floor_artifact` core and `test_mint_floor_artifact_generalized` core.
  - `test_uncertainty_evidence` and `test_uncertainty_p2029`: the half-width.
  - `test_claim_side_bound`.
  - `test_d117_floor_qwen3_v5_generate` and `test_d117_contrast_v5_pack`: the current packs.
  - `test_single_count_discipline_*`.
- **Claim consumption and analysis**
  - `test_analysis_integration`, `test_analysis_engine`, `test_analysis_claims`, `test_analysis_finalizer`, `test_analysis_inputs`.
  - `test_analysis_manifest_v3`, `test_analysis_ratio*`, `test_analysis_multiplicity`, `test_dependence_sensitivity`.
  - `test_whole_window` and `test_whole_window_selection`.
  - `test_collector_analysis_manifest_id`, `test_check_window_provenance`.
  - `test_bundle`, `test_bundle_read`, `test_schemas`: strict validation.
- **Printed paper values and their custody**
  - `test_receipt_histsem`, plus the `fences` job step `verify_receipt_histsem.py --require-published`.
  - `test_paper_replay_fence`: each fenced draft value is stated once, the draft's own arithmetic is right, and it is corpus-replayable.
  - `test_paper_round7_artifacts`: figure/DX values.
  - `test_paper_custody`, `test_paper_reported_energy`, `test_paper_comparison_placements`.
  - `test_paper_terms_lint` and `test_claims_lint`: number wording.
- **Mechanism kept, noted as cheap and sound**: `sampler_launch_fence` (S1 branch). It refuses any real `sudo`/`powermetrics` start inside tests, and a whole-module run had in fact launched real captures (record d528efb2 item 124).

**Named gap, not a cut.** RUN_STATE (09-28) records "241 printed results numbers no checker compares". The fences above cover only the fenced subset. If test effort is to be re-spent anywhere, it belongs on a checker for those printed values, not on more gate machinery.

## 6. Proposed hosted-CI trim

What happens today (run 36382310251): 23 jobs and 462 runner-min on a main push, and about 61 min wall. PRs run 3.13 only, so about 14 jobs and 231 runner-min, with the same about 57 min critical path. The critical path is `test_scored_reduce` alone (2,523 s), placed on a shard as if it were a 22 s module.

Proposed, in order of payoff. The first two need no test change.

1. **Refresh the timing map** (37 unmapped modules), or make an unmapped module inherit its last hosted time. This rebalances the shards immediately.
2. **Scored sweeps go to a `paths:`-filtered job** (runs when `joulewise/scored_*`, `tests/*scored*` or `tests/scored_*` change), plus a nightly cron. The per-push suite keeps the named scored tests and stress case 1–2. This is item 1 in §4.
3. **Main pushes run 3.13 only.** A weekly `schedule:` job runs the full 3.11 matrix. The exclusive calibration jobs run on 3.13 only.
4. **Tooling tests move to a non-blocking `tooling` job** (item 9 in §4).
5. **Delete** the always-skipped site-lane tests (item 6). They never run in `ci.yml` at all, so this changes no CI minutes, only clutter. Remove `d117-production-proof.yml`, or leave it explicitly parked: it has been unrunnable since 08-16 and was last triggered 2026-08-16 (cold check, because it once discharged D-130).
6. Keep `fences`, `quick`, `build`, `installed-wheel` and `gate-ledger` as they are; together they cost about 5 runner-min.

**Expected result (ESTIMATE).**
- Ordinary module-seconds per interpreter drop from about 13,100 to about 5,400: minus 6,371 scored plus about 500 kept, minus about 450 installer, minus 954 crash matrix counted separately, minus about 300 fiducial time scale.
- Six shards then take about 15 min each. The calibration-exit job (about 13 min) becomes the floor.
- A main push goes from 462 to about 125 runner-min. PRs go from about 231 to about 125. Critical path goes from about 61 min to about 20 min.
- Four shards would also fit, at about 23 min each, if queue pressure matters more than wall-clock.
- None of this removes a test that guards a number. Everything guarded still runs on every push, except the scored lane's corpus sweeps, which have guarded no issued number yet.

## 7. Plain summary for the owner (10 lines)

1. The suite runs 7,540 tests in 269 modules. The test code (268k lines) is now larger than the code it tests (214k), and it grew 5.8× since mid-July.
2. The slowness is not spread out. Four modules for the not-yet-used "scored" headline machinery take about 43 % of CI time. The top 25 modules take about 90 %.
3. Those four scored modules run huge random corpora. In mutation tests, small named tests caught 4 of 5 injected bugs, and the fifth was caught by the first stress case in 4 seconds, not by the other 599 sequences.
4. CI shards take 12 to 57 minutes, unevenly, because the timing file is two weeks stale and treats the 42-minute scored module as a 22-second one.
5. Main-branch CI also runs everything twice (Python 3.11 and 3.13), though the measurements run on 3.13. That is about 230 runner-minutes per push that protects no number.
6. The outdated tests: 73 site-lane tests that are always skipped (the lane is retired), July feasibility spikes, a retired results renderer tested against a frozen vocabulary, a test of a one-off runsheet, and about 10 skips waiting on work that is not coming.
7. The silly tests are few: a handful of tautologies, exact-count ratchets, about 25 process-doc wording checks, 137 tests that run twice by accident, and 3 "sleep then assert" checks that can pass falsely.
8. The core is sound. When I broke the joule integration in the reducer, 10 tests went red within 97 s. Keep every test on J per request, calibration, the detection floor and printed paper values (§5).
9. Doing items 1–7 of §4 plus the CI changes (estimates): a main push drops from about 462 to about 125 runner-minutes and from about 61 to about 20 minutes, and no number-guarding test is lost.
10. Four cuts touch a claim path and need a cold Fable check first: the Qwen2.5 D-117 plan tests, the D-079 ledger bootstrap tests, the retired mint pins with the results renderer, and the S1 branch's test-only gate switch with its ID lists (replace it with one honest fixture).
