# Canonical map: the one current tool or document per job

Read this before building anything. If a job is listed here, use the named tool or
document. If you think it is wrong or stale, fix this file in the same PR that changes
the job. Superseded tools are deleted from `main`, not left beside the current one; old
files stay retrievable from the archive tag (see [docs/ARCHIVE.md](docs/ARCHIVE.md)).

Why this file exists: the fast independent recompute (`scripts/independent_recompute_b5.py`,
merged 2026-10-14) sat unused for three weeks while the slow pipeline was being optimized,
because nobody could see which tool was current. The 2026-11-06 prune
([run report](docs/run_reports/2026-11-06-repo-prune.md)) removed about 8,100 stale files so
that cannot happen again.

Last updated: 2026-11-10 (Paper rows: Paper 1 landed under `docs/paper/paper1/`, RL-1; earlier the same day, file-prune stack; CA-42 retirement held at the live ALIGN registration gate). The v4 line section remains as recorded on 2026-11-08; current lane state is in `RUN_STATE.md`.

## Project state

| Job | Canonical | Replaced |
|---|---|---|
| What is happening now, and what to do next | [`RUN_STATE.md`](RUN_STATE.md) (newest numbered item first; items from 150 on are current) | Dated `RESUME-*` files and session checkpoints under `docs/legacy/process_traces/` and `docs/process_traces/` (archived) |
| Machine-readable head pointer and Next activation rule | [`docs/process/CURRENT.json`](docs/process/CURRENT.json), generated from RUN_STATE's highest numbered item carrying a `pointer` block; [`docs/process/POINTER_RULE.md`](docs/process/POINTER_RULE.md) | Hand-maintained pointer JSON; `WINDOW_STATUS.md` and its publisher `scripts/window_status.sh` (superseded on `main`; retrieval in [docs/ARCHIVE.md](docs/ARCHIVE.md)) |
| Work queue | [`TASK_QUEUE.md`](TASK_QUEUE.md); its marker-fenced region is generated from `docs/process/state_kernel.json` by `scripts/gen_state.py` (`--check` in CI) | Hand-kept queue lists in session traces |
| Decisions and rulings | [`docs/decision_log.md`](docs/decision_log.md) (D-numbers), [`docs/council_log.md`](docs/council_log.md); research-design and paper-bound rulings (RL-numbers, the binding record per `RUN_STATE.md` item 257): `audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` | — |
| Owner unseal records (RL-53 W-8) | `joulewise/unseal_record.py`: strict schema, canonical digest and committed verdict-bound permission; records in `docs/unseals/` | Future unseals recorded only in prose; Block 5 predates the rule, BYTES keeps its commitment journal |
| Outcome display permission (opt-in) | `scripts/show_outcomes_guard.py check --block B --verdict V [--path P]`: hashes only the explicit verdict; refuses without a matching committed unseal | — |

## Measurement windows (ALIGN v4: R0, R1, W1, D1-D3)

The magistrate on the MacBook Pro owns running, re-running and arming windows
(`RUN_STATE.md` item 181). The laptop lead delivers reviewed kits onto the measurement lane.

| Job | Canonical | Replaced |
|---|---|---|
| Window design | `docs/align/council-2026-11-05/FINAL-DESIGN.md` with `FINAL-DESIGN-AMENDMENT-1.md` and `-2.md` | The council's round briefs and seat records (r1/r2 Opus, Sol, Fable), archived; v0-v3 pilot protocols |
| Measurement lane (kits, code, runbooks) | Branch `lane/2026-11-05-align-pilot10-benign`: `joulewise/align/**`, `configs/align/v4/**`, `docs/align/**` (v4 desk: `docs/align/v4_desk.md`, R0: `docs/align/r0_desk_runbook.md`) | ALIGN v0-v3 pilot kits (`scripts/align_pilot_kit.py`, `scripts/align_pilot_session.py`) for v4 work |
| R0 launch | `scripts/launch_align_r0.py` on `main` (hands R0 to a one-shot LaunchAgent via `scripts/run_align_r0_launchagent.sh`) | Running R0 from an agent tree |
| R0 runner (the checks themselves) | `scripts/align_r0_checks.py` + `joulewise/align/r0*.py` (`r0.py`, `r0_host.py`, `r0_mlx.py`, `r0_runner.py`, `r0_step.py`) on `lane/2026-11-05-align-pilot10-benign`. Not on `main` | — |
| External SSD qualification | `scripts/align_ssd_qualification.py` on `lane/2026-11-05-align-pilot10-benign` (merged there at `9f0125310`, PR #689); runbook `docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md` §6. Not on `main` | `lane/2026-11-06-ssd-always-attached` (never merged) |
| R1 rehearsal driver | `scripts/align_r1_rehearsal.py` + `joulewise/align/apple/r1_runtime.py` on the R1 integration line `lane/2026-11-06-v4-r1-integrated`. Not on `main`, and not yet on the measurement lane, which has only the earlier WP17 driver without `r1_runtime.py` | The WP17 driver on the measurement lane |
| v4 kit and sessions | `scripts/align_v4_kit.py`, `scripts/align_v4_session.py` on the R1 integration line (`lane/2026-11-06-v4-r1-integrated`); the WP17 versions are also on the measurement lane. Not on `main` | — |
| Window records | Record branches `records/<date>-align-*` and `docs/align/r0/<date>/` (cited from `RUN_STATE.md`) | — |
| Window state and outcome (read-only shadow) | `joulewise/window_state.py`; `python3 -m joulewise.window_state <custody_root> [--json]` reads structural markers only; synthetic coverage in `tests/test_window_state.py` | — |
| Owed host side effects (read-only shadow) | `joulewise/host_effects.py`; `python3 -m joulewise.host_effects --state-dir D [--json]` combines fixed-name records with caller-supplied live facts; synthetic coverage in `tests/test_host_effects.py` | — |
| Air results watcher (structure only) | `scripts/air/night_results_watch.py`; `--once` or `--loop` polls results refs without checkout or SSH; usage and launchd text in `scripts/air/README.md`; synthetic coverage in `tests/test_night_results_watch.py` | Lead's scratch zsh watcher, only after the current chain exits |
| Block-5 window harvest (collection finished) | `scripts/harvest_b5_window.py` + `joulewise/b5/**` | `scripts/harvest_g2a_window.py` (kept because `joulewise/v5_qualification.py` imports it); CA-42 arm/T-0 retirement (#668) is held by the live ALIGN v4 artifact/registration inventory; see `docs/run_reports/2026-11-10-file-prune-g3.md` |
| Exit-code vocabularies and classification (shadow only) | `joulewise/exit_contract.py`: immutable tables, fail-closed classifier and future plan-contract parser; no existing tool adopts it | — |

## ALIGN v4 window line (W1, C1-C14, T1-T3): agreements and records

The v4 arm stack, kit, series and PREQUAL live on the integration line `align/2026-11-08-v4-r11` @ `57c34f5ab`
(these paths are on that line or on the lane branches below, not on `main` yet; the line lands on `main` FIRST,
see MERGE-ORDER). The lanes were built separately by Sol and Opus and merged against an agreement report;
timing receipts is the exception and has a review record instead. Read the agreement before changing a lane.
Each lane's own branch and sha are given so the text can be checked there.

| Job | Canonical | Branch @ sha |
|---|---|---|
| W1 blockers (R14) | `docs/align/v4/W1-BLOCKERS-AGREEMENT.md` | `align/2026-11-08-w1-blockers-opus` @ `a589a1576` (the doc is also on the v4 line; the `-merged` branch `6d20e787a` lacks it) |
| D/C/T series (R15; frozen manifest, calibration windows C1-C8 with reserves C9-C14 per R22-2/R24, T1-T3) | `docs/align/v4/DCT-SERIES-AGREEMENT.md`; frozen bytes `configs/campaigns/align_v4/series/series_manifest.json` (sha256 `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`) | `align/2026-11-08-dct-series-merged` @ `25860dcaf` (agreement from `align/2026-11-08-dct-series-opus` @ `f9f9f7c4c`) |
| W1 smoke kit and PREQUAL `--w1-next w1` | `docs/align/v4/W1-SMOKE-AGREEMENT.md`, `docs/align/v4/W1-SMOKE.md` | `align/2026-11-08-w1-smoke-merged` @ `0ad6f29f3` |
| Harvest off the MBP (one pack per window, provisional arm eligibility, k+2 finality, R17) | `docs/align/v4/HARVEST-OFF-AGREEMENT.md`, `HARVEST-OFF-MERGED.md`, `HARVEST-OFF-MAGISTRATE-RUNBOOK.md` | `align/2026-11-08-harvest-off-fix` @ `d5dc1198c` |
| Between-window MBP -> Air offload (two verified copies before the MBP deletes) | `docs/ops/AIR-OFFLOAD.md` and its agreement `docs/ops/AIR-OFFLOAD-AGREEMENT.md`; tool `scripts/offload_window.py`. Consumes the harvest-off pack | `ops/2026-11-08-air-offload-merged` @ `b5af05e12` |
| Timing receipts (boundary markers only, no in-window computation; Ed 2026-11-08) | `docs/align/v4/TIMING-RECEIPTS-REVIEW-RECORD.md` (no agreement report: Sol build, Opus HOLD, Sol re-review) | `perf/2026-11-08-timing-receipts` @ `bcd4fd3c2`, review `perf/2026-11-08-timing-receipts-opus-review` @ `53740ab65`, re-review `perf/2026-11-08-timing-receipts-rereview` @ `9c4758dc9` |
| v4 release (stages a-c, comparator, pins) | `docs/analysis/v4/RELEASE-RUNBOOK-v4.md` | `align/2026-11-08-v4-release-tools` @ `8ba59ac55` |
| v4 analysis engine, merge order (the v4 line lands on `main` first and wins every arm-stack conflict) | `docs/analysis/v4/MERGE-ORDER.md` | `engine-r23j` @ `50f4958b6` |

Held, not canonical yet: the condition-waits lane (`align/2026-11-08-condition-waits-*`).

## Block-5 analysis

| Job | Canonical | Replaced |
|---|---|---|
| Registered plan | `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` (sealed, pinned in `configs/analysis/b5/seal_pins.json`) and `registration_block5.md` | — |
| Block-5 dry run (heavy, blinded) | `scripts/run_b5_analysis.py --mode blind-dry-run` over `joulewise/b5_analysis/**`, configs in `configs/analysis/b5/**` | Earlier per-step L9 drivers and `analysis_manifest_v2` (deleted; v3 is `joulewise/analysis_manifest_v3.py`) |
| Block-5 release (unblinding) | `scripts/release_b5.py` (DLE-1: verify the dry run's digests, run the recompute and the comparator; on `main` since PR #688). The release event itself follows the plan's release section and `RUN_STATE.md`. Deviations from the sealed plan: `docs/analysis/b5/DEVIATION-LOG.md` (DLE-3 is analysis version r3) | `run_b5_analysis.py --mode release`, a full second heavy run (now optional audit work). Care audit: `docs/run_reports/2026-11-06-b5-care-audit.md` |
| Production numbers for blocks 6+ | **`scripts/independent_recompute_b5.py`** (standard library only, minutes). DLE-2: it becomes the production program once its pending coverage additions land. **Block 6 (registration §17-R1 with §17-DLE2):** the printing program is RC-B6-1, `scripts/independent_recompute_b6.py` (on `analysis/2026-11-11-b6-path`; path and digest pinned at S-14), which loads `scripts/independent_recompute_b5.py` at SHA-256 `d49103e8…a2e4e0`; second side: the harvest and engine twins, a stdlib checker for counting, pairing and §10-§11, and the reducer cross-check; L9 audit not run (RL-99) | The heavy L9 pipeline as the production path |
| Comparator (recompute against the heavy pipeline) | `scripts/compare_b5_recompute.py` (bars in `configs/analysis/b5/recompute_bars.json`) | `tools/normalized_compare.py` and its R1 original under `docs/process_traces/2026-11-01-l9-speedup-r1/` (deleted in the prune) |
| D-188 equivalence gate (accepting a restructured heavy pipeline) | `tools/b5_equivalence/compare_b5_results.py` (result-equivalence comparator, `--mode blinded` by default). A different job from the comparator above | Byte-for-byte replays of the old pipeline |
| Seal and digest pins | `scripts/digest_pin_census.py` (censuses every SHA-256 literal in `tests/` and `configs/`, writes `configs/pins/registry.json`); checked in CI by `python3 scripts/repin.py --check` | One-off seal verification scripts in process traces; hand repins |
| Analysis commit identity and release checkout provenance | `tests/b5_analysis/test_analysis_commit_agreement.py`: frozen anchor/r4 ancestry and cited rebinds, record/runbook identity, remote-branch fence, and advisory `release_b5.py` checkout fields | — |

## Flash-Next (qwen4_exp) MLX port

| Job | Canonical | Replaced |
|---|---|---|
| Goal and status | Branch `port/qwen4-exp-mlx` (`docs/align/qwen4_exp_port/GOAL.md`) plus the `lane/*-qwen4exp-*` lanes. `docs/align/qwen4_exp_port/canonical.md` comes from `lane/2026-11-05-qwen4exp-canonical`; the newest lane carrying both is `lane/2026-11-06-qwen4exp-port-r2`. None of it is on `main` yet | Pinning a newer upstream `mlx-vlm` release to get the model |
| Model code | `joulewise/align/models/qwen4_exp.py` (loaded through the ALIGN `model_file` hook) + `scripts/align_convert_qwen4_exp.py`, on the qwen4exp lanes (`lane/2026-11-05-qwen4exp-canonical`, `lane/2026-11-06-qwen4exp-port-r2`), not on `port/qwen4-exp-mlx` itself | — |
| Upstream fixes | `docs/align/upstream_mlxvlm_d1/` (fact sheet, walkthrough, evidence) | — |

## CI and checks

| Job | Canonical | Replaced |
|---|---|---|
| Full suite | `python3 scripts/shard_tests.py --workers N --split` (N concurrent shards, e.g. 8). Plain `--workers` does **not** enforce the timing map's `exclusive_modules`: the two calibration modules share the pool with everything else, where CI gives each its own job. On the analysis or measurement Mac, leave the full suite to CI | `python3 -m unittest discover -s tests` (sequential, about 3.2 h) |
| Quick tier | `python3 scripts/quick_suite.py --tier quick --workers 4` (as CI runs it); `--tier touched --since <base>` adds modules related to a change | — |
| CI workflows | Three: `.github/workflows/ci.yml` (quick tier, fences, twelve ordinary `shard_tests.py` shards plus the two exclusive calibration jobs; docs-only ranges report success without running tests); `.github/workflows/gate-ledger.yml` + `scripts/check_gate_ledger.py` (**required** on `main`; validates the PR body's gate ledger); `.github/workflows/d117-production-proof.yml` (**dispatch-only**, `workflow_dispatch`, never runs on a PR) | — |
| Pins | `python3 scripts/repin.py --check` (all families); `--write registry` after deleting or adding pinned files | Hand repins |
| State kernel | `python3 scripts/gen_state.py --check` | — |
| Current pointer generation, byte check, phone display | `python3.13 -B scripts/gen_current.py` (`--check`, `--show`); lead integration into `scripts/gen_state.py` pending | Hand-maintained pointer JSON |
| Current pointer regression and repository drift gate | `python3.13 -B -m unittest tests.test_gen_current` (synthetic blocks/refusals and real generated-byte agreement) | — |

## Suite manifest producers

| Job | Canonical | Disposition |
|---|---|---|
| Mixed and sentinel suite manifests | `scripts/gen_jw_mixed.py` over `joulewise/gensuite/` | KEEP: current producer; tokenizer-manifest helpers have live test consumers |
| Authenticated scored-v6 import | `scripts/gen_gsm8k_scored.py` over `joulewise/benchmark_import.py` | KEEP: canonical producer; scored-lane retirement is deferred |

## Repository operations

| Job | Canonical | Replaced / retaining ref |
|---|---|---|
| Prune scope and dependency gates | `docs/ops/PRUNE-PLAN.md`; execution receipts and rollback log in `docs/ops/PRUNE-EXECUTION.md` and `docs/ops/PRUNE-ROLLBACK.tsv` | Branch retirement is already recorded; file retirement is a separate operation |
| Scientific pin inventory and future tag validation | `docs/ops/PIN-INVENTORY.md`, `docs/ops/TAG-PINNING.md` | Frozen B5 source and original digests remain authoritative for their registered checkout |
| Retrieve retired files | `docs/ARCHIVE.md`; per-file decisions in `docs/ops/FILE-PRUNE-G1.tsv` | `archive/process-traces-before-release-prune-2026-11-08` (`901d7580d`); earlier archive promise remains unchanged |
| Historical campaign retirement | `docs/ops/FILE-PRUNE-G2.tsv`; `configs/campaigns/p2_015_floors/README.md` explains retained live inputs | All nine D117 Qwen2.5 generations stay for the historical receipt/predecessor reader chain and registrations |
| CA-42 retirement gate | `docs/run_reports/2026-11-10-file-prune-g3.md`; all KEEP decisions in `docs/ops/FILE-PRUNE-G3.tsv` | The ALIGN owner must migrate the registered executed closure before the coupled #668 retirement; old-name shims alone do not satisfy it |

## Retired

| Retired material | Current replacement / verdict | Retaining ref |
|---|---|---|
| Superseded profiling logs and synthetic E2E reports listed as DELETE in `docs/ops/FILE-PRUNE-G1.tsv` | Current tools above; reader and authority records remain in the checkout | `archive/process-traces-before-release-prune-2026-11-08:<path>` |
| Historical P2-015 generated campaign, generator/spec/backup and six generator-only assertions | Current v5 packs; calibration plan, its digest sidecar and the live NEG8 test config remain. Historical manifest assertions use archived blobs | `archive/process-traces-before-release-prune-2026-11-08:configs/campaigns/p2_015_floors/` |
| `scripts/axi_sb_static_batch_spike.py` | Already retired: isolated AXI experiment, no current entry point (#654) | `archive/pre-prune-2026-11-06:scripts/axi_sb_static_batch_spike.py` |
| `scripts/axi_sc_spec_decode_spike.py` | Already retired: isolated AXI experiment, no current entry point (#654) | `archive/pre-prune-2026-11-06:scripts/axi_sc_spec_decode_spike.py` |
| `scripts/codex_usage_probe.py` | Already retired: one-shot diagnostic (#654) | `archive/pre-prune-2026-11-06:scripts/codex_usage_probe.py` |
| `scripts/measure_claude_cold_start.sh` | Already retired: one-shot timing diagnostic (#654) | `archive/pre-prune-2026-11-06:scripts/measure_claude_cold_start.sh` |
| `scripts/gen_affine_smoke.py` | Already retired: one-shot fixture generator (#654) | `archive/pre-prune-2026-11-06:scripts/gen_affine_smoke.py` |
| `scripts/spike_mlx_prompt_cache.py` | Retired: recorded Stage 3.0.1 verdict `replay_supported`; current size prediction is `python -m joulewise kv-size`. Historical evidence stays in `docs/phase_3/kv_feasibility.md`; no new native validation claimed | `archive/process-traces-before-release-prune-2026-11-08:scripts/spike_mlx_prompt_cache.py` |

The two retained G4 generator candidates are listed under suite manifest
producers above. All eight verdicts are recorded in `docs/ops/FILE-PRUNE-G4.tsv`.

## Paper

| Job | Canonical | Replaced |
|---|---|---|
| Paper 1 text (the mid-December capstone submission: E1, `RUN_STATE.md` item 256) | `docs/paper/paper1/paper1.md` with `docs/paper/paper1/fill_index.md` and `docs/paper/paper1/variants/` (research lead RL-1). Blind draft tagged `paper1/blind-draft-2026-10-27` (`a1a5029fb`); every later edit is a commit on top of that tag | `docs/paper/draft-v1.md` and `docs/paper/draft-v2-skeleton.md`: the frozen September methods drafts (`draft-v2-skeleton.md` is the D-174 methods fallback of 2026-09-05). Kept unchanged as the source of Paper 1's §3, Appendix B and Tier E; not to be edited as the paper |
| Paper 1 FILL index | `docs/paper/paper1/build_fill_index.py` (run from the repo root) regenerates `docs/paper/paper1/fill_index.md` | — |
| Block 5 released results (working record) | `docs/analysis/b5/RESULTS.md`, kept byte-identical. See [Errata to RESULTS.md](docs/analysis/b5/REDERIVATION.md#errata-to-resultsmd) (research lead RL-39). No number from it enters Paper 1, a slide, the site or a status page until research lead RL-3's gate passes; working records (`RUN_STATE.md`, audits, the deviation and decision logs, review records) may quote it, naming it (RL-27 (1)). Its §6 and §8 are historical as to gates (RL-27 (3)): gate 1 is closed by RL-2 (DLE-7), gate 2 by `RUN_STATE.md` item 256, gate 3 by RL-3 (DLE-6), gate 4 by RL-6 (e) (DLE-10); the DLE entries are in `docs/analysis/b5/DEVIATION-LOG.md` | — |
| Source register and evidence ledger for Paper 1's outlook and the talk (not a manuscript plan) | `docs/capstone/PAPER-PLAN-v2.md` and `docs/capstone/PAPER-OUTLINE.md`. Under `RUN_STATE.md` item 256 no tripwire manuscript is in production; both are superseded as manuscript plans and their Block 5 exclusion is historical, neither in force nor reversed (research lead RL-27 (4), which amends RL-1 item 3). Block 5 numbers are placed in Paper 1 only (RL-2), and on slides under RL-10; a later tripwire or v4 manuscript needs its own placement ruling. One header note on each file says this | Their use as the tripwire manuscript plan |
| Results fill | `docs/paper/results-fill-registry.md` | — |
| Build | `docs/paper/build/build_paper.py` (renders `draft-v1.md` by default; not yet Paper 1's build) | — |
| Reader's artifact guide | `docs/paper/artifact-guide.md` | — |

## Kept but undecided (do not build on these without asking)

- The public site and report pipeline (`scripts/build_site.py`, `scripts/pack_capsule.py`,
  `scripts/release_check.py`, `scripts/build_capstone.py`, `scripts/claims_lint.py`,
  `docs/site/`, `docs/report_src/`, `site_capsule/`). Last regenerated 2026-09-04. Kept as one
  unit because `docs/paper/artifact-guide.md` still tells readers to run `build_capstone.py`.
  Delete together if the site is no longer a deliverable.
  **Held (research lead RL-27 (2), 2026-11-10):** until RL-3's gate passes, no `build_site.py`,
  capsule or report build is published, and GitHub Pages is not enabled.
- The scored-roster modules (`joulewise/scored_*.py` and their tests): dead code, but retiring
  them means closing TASK_QUEUE rows A291-A296.
- `joulewise/load_transition_alignment.py` + `scripts/characterize_load_transition.py`: kept
  while TASK_QUEUE Q10/P2-046B is READY.
