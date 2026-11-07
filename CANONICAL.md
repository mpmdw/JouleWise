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

Last updated: 2026-11-06 (lane/2026-11-06-repo-prune, base `eeea6d5c`).

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
| R0 launch | `scripts/launch_align_r0.py` (hands R0 to a one-shot LaunchAgent via `scripts/run_align_r0_launchagent.sh`) | Running R0 from an agent tree |
| R1 rehearsal / v4 sessions | `scripts/align_r1_rehearsal.py`, `scripts/align_v4_kit.py`, `scripts/align_v4_session.py` on the measurement lane | — |
| Window records | Record branches `records/<date>-align-*` and `docs/align/r0/<date>/` (cited from `RUN_STATE.md`) | — |
| Block-5 window collection (finished) | `scripts/harvest_b5_window.py` + `joulewise/b5/**` | `scripts/harvest_g2a_window.py` (kept only because `joulewise/v5_qualification.py` imports it); the CA-42 arm/T-0 route (`scripts/launch_window.py`, `scripts/capture_t0_step.py`, retiring in PR #668) |

## Block-5 analysis

| Job | Canonical | Replaced |
|---|---|---|
| Registered plan | `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` (sealed, pinned in `configs/analysis/b5/seal_pins.json`) and `registration_block5.md` | — |
| **Production numbers** | **`scripts/independent_recompute_b5.py`** (standard library only, minutes) **+ `scripts/compare_b5_recompute.py`** (agreement with the heavy pipeline; bars in `configs/analysis/b5/recompute_bars.json`) | The heavy L9 pipeline as the production path. Per the care audit (`docs/run_reports/2026-11-06-b5-care-audit.md` on branch `lane/2026-11-06-b5-care-audit`, not on `main` yet): DLE-1, the release is "verify dry-run digests + recompute + comparator" instead of a second heavy run; DLE-2, the recompute is the production program for blocks 6+ |
| Audit run (heavy) | `scripts/run_b5_analysis.py` (`--mode blind-dry-run`, then `--mode release`) over `joulewise/b5_analysis/**`, configs in `configs/analysis/b5/**` | Earlier per-step L9 drivers and `analysis_manifest_v2` (deleted; v3 is `joulewise/analysis_manifest_v3.py`) |
| Accepting a restructured heavy pipeline | `tools/b5_equivalence/compare_b5_results.py` (D-188 result-equivalence comparator, `--mode blinded` by default) | Byte-for-byte replays of the old pipeline |
| Release (unblinding) | DLE-1 path above; the release event itself follows the plan's release section and `RUN_STATE.md` | A full second heavy re-run (now optional audit work) |

## Flash-Next (qwen4_exp) MLX port

| Job | Canonical | Replaced |
|---|---|---|
| Goal and status | `docs/align/qwen4_exp_port/GOAL.md` (branch `port/qwen4-exp-mlx`) and `docs/align/qwen4_exp_port/canonical.md` (from `lane/2026-11-05-qwen4exp-canonical`; newest lane carrying both: `lane/2026-11-06-qwen4exp-port-r2`). Not on `main` yet | Pinning a newer upstream `mlx-vlm` release to get the model |
| Model code | `joulewise/align/models/qwen4_exp.py` (loaded through the ALIGN `model_file` hook) + `scripts/align_convert_qwen4_exp.py` | — |
| Upstream fixes | `docs/align/upstream_mlxvlm_d1/` (fact sheet, walkthrough, evidence) | — |

## CI and checks

| Job | Canonical | Replaced |
|---|---|---|
| Test suite | `.github/workflows/ci.yml` (full suite on every PR that changes code; docs-only ranges report success without running tests); locally `python3 scripts/quick_suite.py` for the quick tier | Running the full suite on the analysis or measurement Mac |
| Gate ledger | `.github/workflows/gate-ledger.yml` + `scripts/check_gate_ledger.py` | — |
| Pins | `python3 scripts/repin.py --check` (all families); `--write registry` after deleting or adding pinned files | Hand repins |
| State kernel | `python3 scripts/gen_state.py --check` | — |

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
