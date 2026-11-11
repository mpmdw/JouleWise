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

Last updated: 2026-11-08 (v4 line section added; the rest as of 2026-11-06, lane/2026-11-06-repo-prune, merged with `main` at `a07134b8`; entries checked against the triage of `sol/burn-canon`).

## Project state

| Job | Canonical | Replaced |
|---|---|---|
| What is happening now, and what to do next | [`RUN_STATE.md`](RUN_STATE.md) (newest numbered item first; items from 150 on are current) | Dated `RESUME-*` files and session checkpoints under `docs/legacy/process_traces/` and `docs/process_traces/` (archived) |
| Work queue | [`TASK_QUEUE.md`](TASK_QUEUE.md); its marker-fenced region is generated from `docs/process/state_kernel.json` by `scripts/gen_state.py` (`--check` in CI) | Hand-kept queue lists in session traces |
| Decisions and rulings | [`docs/decision_log.md`](docs/decision_log.md) (D-numbers), [`docs/council_log.md`](docs/council_log.md) | — |

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
| Block-5 window harvest (collection finished) | `scripts/harvest_b5_window.py` + `joulewise/b5/**` | `scripts/harvest_g2a_window.py` (kept because `joulewise/v5_qualification.py` imports it); CA-42 arm/T-0 retirement (#668) is held by the live ALIGN v4 artifact/registration inventory; see `docs/run_reports/2026-11-10-file-prune-g3.md` |

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
| Production numbers for blocks 6+ | **`scripts/independent_recompute_b5.py`** (standard library only, minutes). DLE-2: it becomes the production program once its pending coverage additions land | The heavy L9 pipeline as the production path |
| Comparator (recompute against the heavy pipeline) | `scripts/compare_b5_recompute.py` (bars in `configs/analysis/b5/recompute_bars.json`) | `tools/normalized_compare.py` and its R1 original under `docs/process_traces/2026-11-01-l9-speedup-r1/` (deleted in the prune) |
| D-188 equivalence gate (accepting a restructured heavy pipeline) | `tools/b5_equivalence/compare_b5_results.py` (result-equivalence comparator, `--mode blinded` by default). A different job from the comparator above | Byte-for-byte replays of the old pipeline |
| Seal and digest pins | `scripts/digest_pin_census.py` (censuses every SHA-256 literal in `tests/` and `configs/`, writes `configs/pins/registry.json`); checked in CI by `python3 scripts/repin.py --check` | One-off seal verification scripts in process traces; hand repins |

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
| Superseded profiling logs, synthetic E2E reports and legacy portfolio synthesis listed in `docs/ops/FILE-PRUNE-G1.tsv` | Current tools above; reader and authority records remain in the checkout | `archive/process-traces-before-release-prune-2026-11-08:<path>` |
| Historical P2-015 generated campaign, generator/spec/backup and six generator-only assertions | Current v5 packs; calibration plan, its digest sidecar and the live NEG8 test config remain. Historical manifest assertions use archived blobs | `archive/process-traces-before-release-prune-2026-11-08:configs/campaigns/p2_015_floors/` |

## Paper

| Job | Canonical | Replaced |
|---|---|---|
| Paper text | `docs/paper/draft-v1.md` (current full draft) with `docs/paper/draft-v2-skeleton.md` (next revision) | — |
| Results fill | `docs/paper/results-fill-registry.md` | — |
| Build | `docs/paper/build/build_paper.py` | — |
| Reader's artifact guide | `docs/paper/artifact-guide.md` | — |

## Kept but undecided (do not build on these without asking)

- The public site and report pipeline (`scripts/build_site.py`, `scripts/pack_capsule.py`,
  `scripts/release_check.py`, `scripts/build_capstone.py`, `scripts/claims_lint.py`,
  `docs/site/`, `docs/report_src/`, `site_capsule/`). Last regenerated 2026-09-04. Kept as one
  unit because `docs/paper/artifact-guide.md` still tells readers to run `build_capstone.py`.
  Delete together if the site is no longer a deliverable.
- The scored-roster modules (`joulewise/scored_*.py` and their tests): dead code, but retiring
  them means closing TASK_QUEUE rows A291-A296.
- `joulewise/load_transition_alignment.py` + `scripts/characterize_load_transition.py`: kept
  while TASK_QUEUE Q10/P2-046B is READY.
