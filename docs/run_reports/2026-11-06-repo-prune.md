# Hard repo prune, 2026-11-06

Branch `lane/2026-11-06-repo-prune`, base `main` at `eeea6d5cfac225bfa3609a9ca443eca66918ca2a`
(RUN_STATE 186). The current tool for each job is now in [CANONICAL.md](../../CANONICAL.md).
How to get removed files back: [docs/ARCHIVE.md](../ARCHIVE.md).

**Why.** The fast independent recompute (`scripts/independent_recompute_b5.py`, merged
2026-10-14) sat unused for three weeks while the slow pipeline was being optimized. Nobody
could see which tool was current. Ed asked for a hard prune so that stale files cannot hide
current ones.

**History is kept.** Tag `archive/pre-prune-2026-11-06` (annotated) and branch
`archive/pre-prune-2026-11-06` both point at the base commit. Both are pushed.

## 1. Counts

| | Files | MB (10^6 bytes) |
|---|---:|---:|
| Before (`eeea6d5c`) | 13,031 | 376.0 |
| After (this branch; includes the 3 new docs) | 4,923 | 186.4 |
| Removed | 8,111 | 189.6 |

Per area (the "after" columns exclude the three new documents):

| Area | Files before | Files after | Removed | MB before | MB after |
|---|---:|---:|---:|---:|---:|
| `docs/process_traces` | 8,105 | 649 | 7,456 | 157.0 | 54.5 |
| `docs/legacy` | 311 | 5 | 306 | 83.1 | 1.1 |
| `tests/fixtures` | 468 | 468 | 0 | 60.7 | 60.7 |
| `tests` (other) | 580 | 556 | 24 | 18.9 | 18.4 |
| `configs/campaigns` | 2,432 | 2,418 | 14 | 15.7 | 15.6 |
| `joulewise` | 172 | 167 | 5 | 8.3 | 8.3 |
| `docs` (other) | 193 | 129 | 64 | 7.2 | 6.1 |
| `docs/paper` | 93 | 93 | 0 | 5.7 | 5.7 |
| `configs` (other) | 79 | 73 | 6 | 5.4 | 5.3 |
| `scripts` | 177 | 164 | 13 | 5.1 | 4.9 |
| root and other (`.codex-report/`, `analysis/`, `site_capsule/`, root files) | 114 | 114 | 0 | 3.5 | 3.5 |
| `docs/site` | 39 | 39 | 0 | 1.6 | 1.6 |
| `docs/run_reports` | 109 | 10 | 99 | 1.4 | 0.1 |
| `docs/reviews` | 76 | 6 | 70 | 1.3 | 0.4 |
| `docs/stream_logs` | 47 | 1 | 46 | 0.4 | 0.0 |
| `docs/align` | 11 | 3 | 8 | 0.3 | 0.1 |
| `docs/report_src` | 19 | 19 | 0 | 0.1 | 0.1 |
| `tools`, `.github` | 6 | 6 | 0 | 0.1 | 0.1 |

Removed by class: HISTORY 8,027, DEAD 60 (including 7 companion tests), SUPERSEDED 24.

## 2. Method

Five inventories classified every tracked path. Each one used a reference scan by Claude,
an adversarial Sol 6.1 xhigh pass, and a verification pass against `eeea6d5c` that applied
all removals together and ran the path-reading checks. The checks were `gen_state --check`,
`repin --check`, `test_docs_freshness`, `verify_receipt_histsem --require-published`, and the
test modules that read paths. The five areas were process traces and legacy docs, configs,
scripts, the `joulewise` package, and docs and tests. Classes:

- LIVE: kept.
- UNSURE: kept, with the reason recorded.
- HISTORY, DEAD, SUPERSEDED: removed.

Under the blinding rule, files whose names suggest sealed outcome content were classified by
name only and never opened.

The final lists are in `jw-wt/prune-work/*-final.tsv`, outside the repo: 12,913 classified
rows. The 118 tracked paths that are in no inventory were kept: root files, `.codex-report/`,
`analysis/`, `site_capsule/`, `env/`.

Main moved only in `RUN_STATE.md` (items 184-186) between the inventory base `088b95cd` and
this base. Those items cite no removed path.

## 3. Changes beyond `git rm`

- `tests/test_modularity.py`: dropped the two `ClosedSetRegistryTests` cases that imported the
  removed `joulewise/analysis_manifest_v2.py`. The detection-floor registry tests and the
  p2_015 campaign generator tests stay.
- `tests/test_schemas.py`: dropped the `PINNED_CONFIG_SHA256` row for the removed
  `configs/examples/mac_mlx_mock_telemetry.json`.
- `scripts/quick_suite.py` and `tests/test_quick_suite.py`: dropped
  `tests.test_admit_model_panel_entry` from the A211 deny-list. **The inventory missed this
  one.** `test_a211_single_module_replay_cannot_bypass_guard` replays every listed module and
  failed with "module not discovered" once that test was gone. Found by the local check and
  fixed here.
- `joulewise/clock_reference.py`: the docstring now cites the retired
  `scripts/quiet_window_clock.sh` through the archive tag. No code change.
- `configs/pins/registry.json`: regenerated with `python3 scripts/repin.py --write registry`.
  Fifteen pinning files were gone. Before the rewrite they produced only notes, and `--check`
  passed.
- 97 Markdown links in 10 kept documents pointed at removed files. They now point at
  `https://github.com/mpmdw/JouleWise/blob/archive/pre-prune-2026-11-06/<path>`. The documents:
  `TASK_QUEUE.md` (outside its generated region), `docs/contracts/{night_quiet_admission,
  pack_night_go_receipt, paper_comparison_placements, receipt_histsem_verifier,
  window_liveness}.md`, `docs/process/{NIGHT_HANDBACK, research_plan_2026-09-16,
  v5-l10-rehearsal-phase}.md` and `docs/research_question_bank.md`. No test or code reads
  the old link targets.
- Not rewritten:
  - Links inside kept trace and legacy files. Live code reads those files by path, so their
    bytes stay as they are.
  - `RUN_STATE.md` (left untouched).
  - About 550 plain-text path citations in kept docs, which are history. `docs/ARCHIVE.md`
    explains how to resolve them.
- Executing review (`docs/run_reports/2026-11-06-repo-prune-executing-review.md`) restored
  `configs/suite_manifests/jw_{mixed,sentinel}_v1_qwen25_15b_annotations.json` and re-ran
  `repin.py --write registry` (their rows return byte-identical to `main`).
  `scripts/run_campaign.py:2471` builds `<manifest stem>_annotations.json` at run time and
  uses it for the prompt-hash check of every config that names the kept manifests (54 kept
  `p2_015_floors` configs name the sentinel manifest). Net removal is 8,109 files.
- `scripts/test_timings.json` still lists 23 removed test modules under `seconds_by_module`.
  Those entries are scheduling hints only; the CI shard planner ignores modules it does not
  discover. They were left alone to avoid a conflict with the `ci-timings` lanes.

## 4. Rescued items (would have broken something if removed)

The inventories moved 547 paths from a removal class back to LIVE or UNSURE:

| Area | Rescued | Typical reason |
|---|---:|---|
| traces/legacy | 151 | `state_kernel.json` pointer targets (`gen_state --check` fails if missing); ruling authority cited by `decision_log.md` or by registered plans on open lanes; current magistrate runbook citations |
| configs | 223 | digest-bound by LIVE v5 reference configs (`p2_015_floors/calibration_plan.json`); D-096 frozen metrology plans; read and sha-pinned by LIVE tests |
| scripts | 74 | listed in `configs/gates/hazard_refusals.json` `scan.not_scanned` (test fails if absent); imported by LIVE tests or by kept modules |
| package | 7 | `arm_readiness.py` imported by `whole_window.py`; `scheduler_gates.py` ast-parsed by `test_family_marker.py` |
| docs/tests | 92 | `gen_state` pointer targets; inputs to the site build; paper provenance comments |

Kept at execution time (69 more paths), because removing them would leave a kept tool broken:

- **Report and site pipeline (65 paths):** `docs/report_src/**`, `docs/site/**`, the RPT
  tests and `docs/JouleWise_Hardening_Proposal.md`. `scripts/build_capstone.py` was rescued
  because `docs/paper/artifact-guide.md:168` tells readers to run it, and it reads
  `docs/report_src/`. `release_check.py` reads `docs/site/build_manifest.json`. The whole
  pipeline is one UNSURE unit pending Ed (is the public site still a deliverable?).
- **`joulewise/scored_{packer,reduce,registration}.py`:** dead code, but retiring it means
  closing TASK_QUEUE A291-A296 and state-kernel rows. That is a queue decision, not a prune.
- **`joulewise/load_transition_alignment.py`:** imported by the rescued
  `scripts/characterize_load_transition.py` (TASK_QUEUE Q10/P2-046B is READY).

## 5. Traps the inventory found (one or two per area)

1. **Traces.** `docs/process/state_kernel.json` holds pointer targets inside
   `docs/process_traces/` and `docs/reviews/`, and `scripts/gen_state.py:138-139` fails CI
   when one is missing. Some traces are also the cited authority for decision-log rulings
   (D-181/182/184) or for registered plans that live only on open ALIGN lanes, such as
   `docs/registrations/bytes_pack_v1.md`. Those lanes are not on `main` yet.
2. **Configs.** Superseded campaign packs are still bound by digest. For example, 54 LIVE
   block-5 v5 reference configs carry `calibration-plan-sha256=` of
   `p2_015_floors/calibration_plan.json`. 1,734 superseded Qwen2.5 and D-117 pack configs stay
   because tests regenerate or pin them byte for byte. Plain deletion breaks CI, so they need
   a coupled retirement.
3. **Scripts.** `configs/gates/hazard_refusals.json` `scan.not_scanned` names retired
   scripts, such as `launch_window.py` and `capture_t0_step.py`, and
   `tests/hazards/test_refusal_allowlist.py` fails if one does not exist. Also,
   `tests/test_d117_decode_contrast_plan.py` copies `scripts/generate_arm_readiness.py` with
   `shutil.copy2`, and `joulewise/v5_qualification.py` imports `scripts/harvest_g2a_window.py`
   at module top. All of these retire only as units, through PR #668.
4. **Package.** Removing any `joulewise` module changes `analysis_verified_store.code_digest`.
   That means a cache miss on the next block-5 run, and a new `executed_inventory` in the
   observational `b5/driver.py` record. Neither one refuses. The running analysis on the Air
   uses its own checkout and is unaffected.
5. **Docs and tests.** Several "dead-looking" docs are read by tests as text:
   - `NIGHT_HANDBACK.md` and `evidence_night_entry.md` are read by `test_evidence_night` and
     `test_night_gate`.
   - `receipt_histsem_verifier.md` is read by `test_receipt_histsem`.
   - `docs/phase_2/alpha_arm_readiness.md` is read by `test_arm_readiness_registry`.

   The site build needs non-regenerable inputs (`docs/advisor_briefs/2026-07-17-window-a-brief.html`
   and the fonts). Plus the miss in section 3: the A211 deny-list in `quick_suite.py`.

## 6. Conflicts with open lanes

Checked: every `origin/lane/2026-11-06-*` and `lane/2026-11-07-*` lane (50 at check time)
plus `lane/2026-11-05-align-pilot10-benign`, using `git diff --name-only origin/main...<lane>`.

**Removed files that an open lane modifies (modify/delete conflict):**

| File | Lanes | Resolution |
|---|---|---|
| `tests/test_harvest_v5_qualification.py` | `lane/2026-11-06-ci-timings-main`, `lane/2026-11-06-sol-ci-flaky-timings` | Take the deletion. The test covers the retired CA-42 qualification chain, and PR #668 deletes it too. |

**Edited files that open lanes also modify:**

| File | Lanes |
|---|---|
| `configs/pins/registry.json` | pilot10-benign and 22 lanes based on it |
| `TASK_QUEUE.md` | 28 lanes |
| `tests/test_schemas.py` | pilot10-benign and 22 lanes based on it |
| `docs/process/NIGHT_HANDBACK.md` | `lane/2026-11-06-v4-r1-round4-fixes` |

Text conflicts are listed in the PR description from a `git merge-tree` dry run. If
`registry.json` conflicts, resolve it by re-running `python3 scripts/repin.py --write registry`
on the merged tree. Do not hand-merge it.

Earlier prune PRs overlap this one: #650 (plan), #654 (Stage 1) and #668 (Stage 2, the CA-42
route). This prune already removes #654's five scripts and #668's test files. #668's code
changes, such as renaming `arm_readiness.py`, still apply after it.

## 7. Checks run (on the Air, niced, while a real-data analysis was running)

- `python3 -m compileall -q joulewise scripts`: rc 0.
- Imported every module under `joulewise/`: 167 modules, 166 OK. The exception is
  `joulewise.__main__`, which runs the CLI parser on import and exits 2 with no arguments.
- `python3 scripts/gen_state.py --check`: rc 0.
- `python3 scripts/repin.py --check`: PASS, 16 families, before the registry rewrite.
- `unittest tests.test_modularity tests.test_docs_freshness tests.test_quick_suite
  tests.test_paper_comparison_placements tests.test_gen_state`: 119 tests. One failure was
  the deny-list issue in section 3. After the fix, `tests.test_quick_suite` is OK (15).
- The full suite was not run locally. CI runs it on the PR.

## 8. Next prune candidates (kept here, removable with a decision)

- The report and site pipeline (section 4). Ed's call.
- `joulewise/scored_*` and their 12 tests, with TASK_QUEUE A291-A296. Queue decision.
- The CA-42 arm/T-0 route and its coupled configs and tests. PR #668.
- 1,734 superseded D-117 pack configs. Coupled retirement with their regeneration tests.
- `.codex-report/` (Codex seat reports at the repo root). Not inventoried.
