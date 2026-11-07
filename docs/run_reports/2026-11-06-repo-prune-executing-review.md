# Executing review of the hard repo prune (PR #690), 2026-11-06

Reviewer: Claude (Opus 5.5), not the prune's author, with one local Sol 6.1 xhigh run as a
second critic. Reviewed head `71dea4e09c5d1e0c85af5a41fad687cef4bbff64` against base
`origin/main` `eeea6d5cfac225bfa3609a9ca443eca66918ca2a`. Fresh worktrees under `jw-wt/`:
`prune-review` (PR head), `prune-review-base` (main), `prune-review-p10` (the measurement lane
`lane/2026-11-05-align-pilot10-benign` at `84848dc68` with all 8,085 PR-removed paths that
exist there deleted), `prune-review-sol` (Sol). Every local command ran under `nice -n 19`
(and `taskpolicy -b` for the long ones), because a real-data analysis is running on this Air.

## Verdict

**One LIVE removal found and fixed on the branch. No other LIVE removal found.** The measurement
kit flow, the b5 analysis entry points and CANONICAL.md all check out, with two small wording
fixes to CANONICAL.md. CI on the original head `71dea4e0` passed every job except `gate-ledger`,
which was still PENDING by design.

## 1. Defect fixed: two suite-manifest sidecars that kept code reads by a runtime-built path

Removed by the PR: `configs/suite_manifests/jw_mixed_v1_qwen25_15b_annotations.json` and
`configs/suite_manifests/jw_sentinel_v1_qwen25_15b_annotations.json`. The manifests next to
them (`jw_mixed_v1_qwen25_15b.json`, `jw_sentinel_v1_qwen25_15b.json`) are kept.

- `scripts/run_campaign.py:2471` (`inferred_prompt_sidecar_path`) builds
  `manifest_path.with_name(f"{manifest_path.stem}_annotations.json")`. The path is never written
  out in full, so the inventory's path-string scan missed it.
- `scripts/run_campaign.py:2757-2774` (`check_prompt_hashes_for_config_bundle`, called from
  `evaluate_member` at `:2919`) checks prompt hashes against that sidecar when it exists.
  Without it, the code falls through to the token-evidence policy. Sol ran the extracted helpers
  on the real kept mixed manifest (48 text items): after the prune the result is
  `missing_evidence`, which becomes `prompt_token_evidence_missing` (`:402`). Before the prune
  it was a hash check against 48 rows.
- 54 kept `configs/campaigns/p2_015_floors/**` configs, which the inventory itself classed LIVE,
  name `jw_sentinel_v1_qwen25_15b.json`. Their member evaluation therefore takes a different
  branch without the sidecar: a full hash check before, the token-policy path
  (`not_applicable`) after. `tests/test_suite.py:45` pins the mixed manifest's bytes.
- **Fix (commit on this branch):** restored both files byte for byte from `main` (91 KB). Re-ran
  `python3 scripts/repin.py --write registry`. Their registry rows came back identical to
  `main`, checked by a JSON comparison of both entries. Net removal is now 8,109 files. The run
  report's section 3 records this.
- After the fix: `tests.test_suite`, `tests.test_docs_freshness` and
  `tests.test_audit_cli_examples` passed (69 tests). `gen_state --check` rc 0.

## 2. The 62 riskiest removals (all code, configs and tests), each shown unreferenced

Method: (a) I searched every kept non-Markdown file except `configs/campaigns/**` and
`tests/fixtures/**` for every one of the 8,111 removed full paths (`rg -F -f`). The only hits in
code are docstrings, comments, or constant evidence strings that are compared but never
opened: `joulewise/detection_floor.py:140`, `joulewise/clock_reference.py:5-7`,
`tests/test_d117_decode_contrast_plan.py:2178`, `tests/test_d117_contrast_v5_pack.py:1224`,
`tests/test_battery_float_sweep.py:103`, `scripts/check_paper_replay_fence.py:32`,
`scripts/bench_replay_start_drift.py:369`, `tests/test_git_fixture_maintenance.py:32`. Other
hits are JSON `evidence_reference` and `published_anchor` text fields in `configs/floor_mint`,
`configs/arm_readiness` and `configs/model_panels`. I found no code that opens those fields.
(b) I searched for each removed file's basename and module stem in `joulewise`, `scripts`,
`tests`, `tools`, `.github` and `configs`, leaving out the regenerated registry and the timing
hints. (c) I listed every `glob`, `rglob`, `iterdir`, `listdir` and `walk` call and every
f-string or `Path /` construction under `docs/` or `configs/`, and checked each one that could
reach a directory that lost files. (d) I traced imports from each removed test, to see whether
a kept test imports it and what kept code it exercised.

| Removed | Result |
|---|---|
| `configs/suite_manifests/jw_{mixed,sentinel}_v1_qwen25_15b_annotations.json` | **LIVE, restored** (section 1) |
| `configs/campaigns/exploratory_2026_07_17/**` (12 files) | No kept reader. The only basename hits are `order_manifest.json` in other packs. No pack id, glob or f-string reaches `exploratory_*`. |
| `configs/campaigns/p2_015_smoke/production_shakedown/*` (2) | Same as above. `test_p2038_production_path` is a different, kept module. |
| `configs/characterization/char-t3appup-r0{1,2,3}.json` | The directory is gone. The only `characterization/` strings are `fill:characterization/*` leaf names in `compare_b5_recompute.py:3609` and its tests, which are not paths. |
| `configs/examples/mac_mlx_mock_telemetry.json` | `tests/test_audit_cli_examples.py:52` globs `configs/examples/*.json` with no expected count, and it passes. The `test_schemas` pin row was dropped by the PR. |
| `joulewise/analysis_manifest_v2.py` | Superseded by `joulewise/analysis_engine/registry.py:566,723`, which kept the v2 *validator*. `hazard_refusals.json:340-342` names that kept function, not the module. |
| `joulewise/{coldgate_receipt,phase_share,workload_sizing,workloads}.py` | No import, `import_module` or `runpy` use. The basename hits are the English word "workloads" and `configs/workloads/`. |
| 13 scripts (`admit_model_panel_entry`, `analyze_phase_share`, `axi_s{b,c}_*_spike`, `check_sealed_bundle_compatibility`, `codex_usage_probe`, `derive_estate_anchors`, `ed_session/{build_rehearsal_env,rail-probe,sampler-checklist}.sh`, `gen_affine_smoke`, `measure_claude_cold_start.sh`, `quiet_window_clock.sh`) | Not in `hazard_refusals.json` `not_scanned`, CI, or RUN_STATE items 150-186. Every one is named in `configs/campaigns/v5_claim_25g83/sealed_inventory.json`. That inventory is checked against git history at H_claim (`tests/test_b5_seal_landing.py` docstring, points 1-3), not against the working tree, so deleting the files on `main` does not affect it. |
| 24 tests | No kept test imports any of them. The two kept-test mentions are comments (`test_arm_readiness_lifecycle.py:937`). None has a BLOCKED skip or `expectedFailure`, so `test_s0_blocked_enumeration` counts are unchanged. `scripts/test_timings.json` lists them as scheduling hints only, not in `exclusive_modules` or `split_modules`. |

**Coverage given up (by the PR's design, not a defect):** the removed tests also exercised kept
scripts on the retiring CA-42 arm/T-0 route: `scripts/launch_window.py`,
`scripts/capture_t0_step.py`, `scripts/generate_arm_readiness.py`,
`scripts/check_v5_arm_abort.py`, `scripts/quiet_mac_prep.sh`, `scripts/run_night.py`
(partially), `scripts/ed_session/capture_t0_anchor_positive_control.py` and
`scripts/harvest_g2a_window.py`. RUN_STATE items 150-186 cite none of these scripts. They stay
on `main` only because `hazard_refusals.json` or an import pins them, and PR #668 retires them.
Until #668 lands they have less test coverage. Do not use them for ALIGN v4 work.

## 3. Measurement kit flow (ALIGN v4)

ALIGN v4 code is not on `main`. It lives on `lane/2026-11-05-align-pilot10-benign`, the
measurement checkout `84848dc68`. Only the R0 launcher is on `main`. Checks:

- **PR head:** `scripts/launch_align_r0.py --help` and each of `launch`, `handoff`, `clear`,
  `preflight` and `run` `--help`: all rc 0. The launcher uses only the standard library. It
  reads `<--repo>/scripts/align_r0_checks.py` and the sibling
  `run_align_r0_launchagent.sh`, and both exist.
- **Lane tree with the prune applied** (8,085 removed paths deleted): rc 0 for `--help` of
  `align_v4_kit`, `align_v4_session` (`prepare`, `install`, `desk`), `align_r1_rehearsal`,
  `align_r0_checks`, `align_v4_thermal_desk`, `align_v4_verify_d_pins`,
  `build_v4_histsem_pinset`, `align_smc_enumerate`, `bytes_mac_kit`, `align_pilot_kit` and
  `align_pilot_session`, and for `python -m` on `joulewise.align`, `.r0_runner`,
  `.apple.pilot`, `.power.preflight`, `.analysis.metadata_baseline`,
  `.analysis.budget_pilot`, `.moe.stage_a`, `.budget` and `.budget.apple`.
  `align_cache_checkpoint_native.py` needs `PYTHONPATH=.` (this was already so before the
  prune) and then gives rc 0.
- **Dry kit build:** `align_v4_kit.py --output-root <scratch>` on the pruned lane tree gives
  rc 0 and 29 files, **byte-identical** (`diff -r`) to the same build on the unpruned lane
  tree.
- **Static:** among the lane's 2,991 changed files, removed paths appear only in
  `configs/pins/registry.json` (regenerate it on merge, as the run report says) and as `paper`
  text fields in `configs/b6/executing_reviews.json` rows 316-352. The lane's
  `joulewise/b6/code_check.py` never reads `paper`. The lane test
  `tests/b6/test_audit_record_fixes.py` checks only rows appended after `9bdcf6c95`, and those
  rows point at `docs/align/reviews/`. All 28 repo paths named in the lane's `tests/align`
  exist after the prune, apart from f-string templates and one summary-string mention of
  `FINAL-DESIGN.md` (which is on `main` and not on the lane, so this is not a prune effect).
- RUN_STATE items 150-186: no cited path, full or partial, is among the removed paths.
  `docs/align/council-2026-11-05/FINAL-DESIGN*.md` are kept and do not cite the removed round
  files. No kept non-history Markdown file links a removed path except `RUN_STATE.md` (58 links
  in old items, left as they are by rule).
- Not run: the full `tests/align` package on the pruned lane tree. It did not finish within
  15 minutes niced, so I stopped it. A 13-module subset of the path-reading align tests was
  still running when this report was written. CI runs `tests/align` on the lane.

## 4. Block-5 analysis, recompute, comparator

- `scripts/independent_recompute_b5.py --help` and `scripts/compare_b5_recompute.py --help`:
  rc 0. `scripts/run_b5_analysis.py --help` gives rc 2 (`step 0 - tooling_refusal`) on the PR
  head **and the same on `main`** (worktree `prune-review-base`). This is a local
  environment refusal, not a prune effect.
- 22 fast modules (each under about 15 s in `test_timings.json`) on the synthetic fixtures,
  across `tests.independent_recompute.*` (rehearsals, examples, meter, hygiene,
  comparator_meter, reconcile, structural_rules, review_fixes, input_gate, comparator),
  `tests.b5_analysis.*` (joined_probes, step4_exit_classes, reported_cell, neg8_predicate,
  frozen_files, fill_adapter, neg8_parity, release_equality, archive, chain_fixture, windows)
  and `tests.test_b5_seal_landing`: 351 tests. The only failures were 9 failures and 5 errors
  in `test_fill_adapter` and `test_release_equality` (`results_fill_path_refused`,
  `custody_path_invalid`). **The same 14 failures occur on `main`** in the same environment, so
  they are local custody-path refusals, not prune effects. On GitHub CI both modules pass on
  the PR head.
- `configs/analysis/b5/seal_pins.json`: every file key under `pins` exists. The `sealed`
  digests are checked from git history, not the working tree.
- `tools/b5_equivalence/compare_b5_results.py` reads only `configs/analysis/b5/`, which
  the PR does not touch.

## 5. CANONICAL.md

Every path that it says is on `main` exists on the PR head. The off-main destinations
(`joulewise/align/**`, `configs/align/v4/**`, the v4 desk and R0 runbooks, the R1 and v4 kit
scripts, the qwen4_exp port docs and code) are labelled with their branches. The claims I
checked hold: `joulewise/v5_qualification.py:20` imports `scripts.harvest_g2a_window`;
`run_b5_analysis.py` takes `--mode blind-dry-run|release`; `joulewise/analysis_manifest_v3.py`
exists; RUN_STATE item 181 gives windows to the magistrate; item 184 keeps the launcher on
`main` and the kit on the lane. Fixed on the branch:

- "full suite on every PR" changed to say that docs-only ranges report success without
  running tests (`.github/workflows/ci.yml:18-20`).
- The care-audit citation now says the report is on `lane/2026-11-06-b5-care-audit`, not
  `main`.

## 6. Findings left as they are (non-blocking, with reasons)

1. **State-kernel acceptance evidence cites removed traces** (Sol). Counting only
   `acceptance.evidence`, Sol found 111 unique removed paths cited by 68 non-shelved tasks.
   My wider count over each whole task record gives 92 non-shelved tasks (71 queued,
   13 blocked, 5 partial, 3 active), for example `BFGS-S0-FOLLOWUPS-01` and
   `BATTERY-FLOAT-GATE-01`. These are free-text citations. The structured `pointer.path` fields have zero matches, so
   `gen_state --check` passes. Nearly all of these are tasks on the retired CA-42/v5 night
   route. Rejected as a prune blocker: `docs/ARCHIVE.md` gives the `git show
   archive/pre-prune-2026-11-06:<path>` fallback. Recommended follow-up (a queue decision):
   shelve the CA-42-route tasks together with #668, rather than restoring the traces.
2. **The registry regeneration also adds two rows that `main` lacked:**
   `configs/analysis/b5/equivalence_open_indices.json` and
   `tests/b5_analysis/fixtures/equivalence/s10_remint.py`, both from the D-188 merge. This
   corrects drift that `--check` tolerated; it is not a regression. CI's
   `repin.py --check` covers it.
3. **`scripts/test_timings.json`** still names 23 removed modules. These are scheduling
   hints only. Left alone, as the run report says, to avoid conflicts with the ci-timings
   lanes.

## 7. Sol second critic

One run: `codex exec -m gpt-6.1-sol`, xhigh, workspace-write, in `jw-wt/prune-review-sol`.
The prompt is at `jw-wt/prune-review-sol.prompt.txt`, the events at
`jw-wt/prune-review-sol.events.jsonl`, and its report at
`jw-wt/prune-review-sol/SOL-PRUNE-CRITIC.md` (outside the repo). It found the sidecar defect
independently (section 1) and the kernel-citation item (section 6.1). It also flagged the
CANONICAL CI wording (fixed) and the branch-only destinations (already labelled).

**Blinding audit:** I grepped the events file with `/usr/bin/grep -E 'jw-b5-|night-custody|night-archive|restricted/'`
and got 31 matching lines. Of these, 24 are commands, and every one is a deny-filter string in
Sol's own path filters. The rest are repo text quoted in tool output (RUN_STATE paragraphs that
mention custody paths). No command opened, listed or hashed a path on disk outside the
repository: **AUDIT CLEAN** for disk paths. Sol reported one in-repo exception itself. An early
`rg` over shell-expanded tracked filenames printed a `from __future__` line from a tracked test
file whose name contains "outcome". No content from it was used, and later scans filtered names
before opening files.

## 8. CI

The original head `71dea4e0` passed: changes, fences, build, quick, installed-wheel,
`test (3.13, 1-12)`, `calibration-exits-exclusive`, and
`calibration-writer-crash-matrix-exclusive (1, 2)`. `gate-ledger` failed because its rows were
PENDING. The PR conversation records the result on the fixed head.
