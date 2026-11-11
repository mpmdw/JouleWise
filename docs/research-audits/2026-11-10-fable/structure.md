# JouleWise structure audit (Fable 5.2, 2026-11-10)

Auditor: Fable 5.2, independent seat. Read-only audit of `main` @ `bfe0f4c78` (worktree `jw-wt/fable-audit`),
written 2026-11-10 17:20 PST. No code was changed. The only file written is this one.

Method: `git ls-files` censuses, an AST import graph over all 934 tracked Python files (module-level and
function-level imports separated), string-reference censuses per script, and read-only `git` object probes of
`origin/align/2026-11-08-v4-r11` @ `9abe6095f` (the ALIGN v4 line; `57c34f5ab`, the sha CANONICAL names, is an
ancestor, 6 commits behind). Three fence test modules were run (`tests.b5_analysis.test_frozen_files`,
`tests.flags.test_flags_import_graph`, `tests.hazards.test_import_graph`: 13 tests, OK) and
`scripts/gen_state.py --check` (clean). No measurement, model or analysis pipeline was run. Nothing outside the
worktree was read.

Marks: **[V]** verified by a probe in this audit; **[I]** inferred from what was read. The in-flight second prune
(`docs/process_traces/**`, `docs/legacy/**`, `docs/reviews/**`, dated `docs/run_reports/*`,
`configs/campaigns/d117_*_v1..v3`, `configs/campaigns/p2_015_floors/**`, the CA-42 arm/T-0 chain, spike scripts) is
treated as already gone; it appears below only where something live still depends on it.

---

## 1. Verdict

The code on `main` is internally consistent at import time (zero module-level import cycles, the independence
fences hold, the three fence tests pass), but the structure does not tell a reader which tool is current, and the
file prunes alone will not fix that. Four things matter most. (1) The live work is not on `main`: the ALIGN v4
line branched on 2026-10-27, never took the 2026-11-06 prune, and holds 15,789 files; landing it adds 3,187 files
to `main`, including 83 `.codex-report` files, 35 process traces, 42 dated run reports and 129 superseded pilot
configs, the same categories the prunes remove. (2) The v4 registration binds the working-tree bytes of 317 paths,
178 of which are legacy files on `main` today, including `scripts/launch_window.py`, `scripts/capture_t0_step.py`
and 21 of the 23 files that `main`'s own fence test calls retired; every bound path is strict, so deleting or
editing one in a checkout that arms a window means re-registration. The in-flight CA-42 chain prune collides with
this. (3) The reason the bound set is so large is one structural defect: function-local imports join 91 modules
(173K lines, including 23 scripts) into a single strongly connected component, so the static closure of any
measurement entry point is 149 files and 203K lines. (4) Three documents claim to be the authority for "what is
current" and they disagree: `docs/process/state_kernel.json` (declared sole authority, CI-enforced, last updated
2026-09-25, no ALIGN task), `RUN_STATE.md` (the real one, 9,659 lines, about 5,000 of them superseded August
checkpoints) and `CANONICAL.md` (accurate for what it lists, but silent on the whole measurement spine). The
deliberate duplicates (independent recompute, comparator, release check, equivalence comparator, arithmetic twins)
are genuinely independent and should be left alone. The recommended path is: fix the maps and the merge order now
with docs-only and additive changes, delete only unbound files while R1/W1 run, adopt the already-approved
freeze-by-commit model for v4 so `main` stops being the frozen copy, and defer every move or split of bound code
until the v4 series is collected.

---

## 2. Structure map

### 2.1 Size by area (`main` @ `bfe0f4c78`, tracked files) [V]

| Area | Files | Lines | MB | Notes |
|---|---:|---:|---:|---|
| `joulewise/` (top level) | 97 | 131,130 | 5.5 | flat; 13 modules over 2,500 lines |
| `joulewise/b5/` | 6 | 13,982 | 0.8 | block-5 collection (HAZARD_PACK path) |
| `joulewise/analysis_engine/` | 12 | 14,987 | 0.6 | generic claims engine |
| `joulewise/b5_analysis/` | 19 | 9,385 | 0.5 | block-5 heavy analysis |
| `joulewise/adapters/` | 13 | 9,879 | 0.4 | mlx, powermetrics, mock, never-live NVIDIA/SSH stack |
| `joulewise/hazards/`, `flags/` | 18 | 9,042 | 0.4 | fenced by import-graph tests |
| `joulewise/gensuite`, `external`, `twins` | 7 | 3,308 | 0.1 | twins are test-only by design |
| `scripts/` | 168 | ~109,000 | 5.1 | 143 Python, 10 shell/zsh, 4 `.mjs`, 9 `p8_evidence` records |
| `tools/` | 1 | 2,145 | 0.1 | D-188 equivalence comparator |
| `tests/` (modules + helpers) | 586 | ~380,000 | 18.6 | 494 test modules, 353 of them flat at top level (308K lines) |
| `tests/fixtures/` | 470 | — | 60.7 | `b5_analysis` 39.9 MB, `d117_v2_production` 12.1 MB |
| `configs/campaigns/` | 2,418 | 376,680 | 15.6 | 1,629 go in the in-flight prune |
| `configs/` (rest) | 75 | 80,677 | 5.4 | `pins/registry.json` alone is 2.9 MB |
| `docs/process_traces/` | 651 | 862,416 | 54.5 | in-flight prune |
| `docs/` (rest) | 467 | ~226,000 | 17.9 | `paper/` 93, `run_reports/` 141, `site/` 39, `contracts/` 33 |
| Root and other | 120 | 25,457 | 3.7 | `RUN_STATE.md` 1.38 MB, `TASK_QUEUE.md` 1.29 MB, `.codex-report/` 58 files |
| **Total** | **5,128** | | **191.6** | about 2,430 files leave with the in-flight prune [I: my reading of its stated list] |

First-party non-test Python is about 301K lines; test modules are about 365K lines.

### 2.2 Dependency diagram (counts are file-to-module import edges) [V]

```
 tests ── 1,885 ──► joulewise        tests ── 320 ──► scripts        scripts ── 12 ──► tests (7 scripts)

 scripts (143 py) ── 298 ──► joulewise (top, 97 modules)
     │                          ▲   │
     │                          │   └── 27 function-local imports back UP into scripts (12 library modules)
     ├── 54 ──► b5_analysis ── 42 ──► top        b5_analysis ── 10 (lazy) ──► scripts
     ├── 16 ──► analysis_engine ── 29 ──► top    analysis_engine ── 5 (lazy) ──► b5_analysis   (generic → block-specific)
     ├── 10 ──► b5 ── 21 ──► top, 5 ► hazards, 2 ► flags        b5 ── 1 (lazy) ──► scripts.run_campaign
     ├── 12 ──► adapters ── 48 ──► top
     ├──  9 ──► hazards ── 6 ──► top             [fence: may not reach the RETIRED list]
     ├──  7 ──► flags ── 3 ──► top               [fence]
     └── 76 script-to-script imports

 Independent by design, 0 first-party imports each, fenced by tests:
   scripts/independent_recompute_b5.py   scripts/compare_b5_recompute.py   scripts/release_b5.py
   tools/b5_equivalence/compare_b5_results.py   joulewise/twins/{engine_twin,harvest_twin}.py

 Cycles: module-level imports 0.  With function-local imports: one component of 91 files (68 library + 23 scripts,
 173,044 lines), one of 9 (b5_analysis dry-run group + 2 mint scripts), two of 2.
```

Static import closure of each entry point (all imports / module-level only) [V]:

| Entry point | All imports | Module-level only |
|---|---|---|
| `scripts/run_night.py` (the LaunchAgent target) | 149 files, 202,845 lines | 29 files |
| `scripts/run_campaign.py` | 149 files | 66 files |
| `scripts/harvest_b5_window.py` | 150 files | 2 files |
| `scripts/run_b5_analysis.py` | 175 files, 219,761 lines | 8 files |
| `joulewise/cli.py` (`python -m joulewise`) | 149 files | 44 files |
| `scripts/independent_recompute_b5.py`, `compare_b5_recompute.py`, `release_b5.py`, `tools/b5_equivalence/compare_b5_results.py`, `scripts/launch_align_r0.py` | 1 file each | 1 file each |

### 2.3 Entry points actually wired [V]

| Wiring | Entry points |
|---|---|
| LaunchAgent templates (`configs/launchd/*.plist.template`) | `scripts/run_night.py` (night and night-probe), `scripts/magistrate_watchdog.py` |
| Night chains (`scripts/night_chains/*.zsh`) | `gen_g2_phase_d.py`, `gen_derivation_night.py`, `recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py`, `validate_powermetrics_fiducial.py` |
| Installers | `install_night_agent.sh` → `run_night.py`; `setup_quiet_guard.sh` → `quiet_guard_privileged.py` |
| CI `ci.yml` | `quick_suite.py`, `shard_tests.py`, `gen_state.py --check`, `repin.py --check`, `verify_receipt_histsem.py`, `ci_docs_only.sh`, `python -m joulewise {validate-config, run, validate-bundle, reduce, determinism-gate}`, `tests.test_docs_freshness`, wheel build |
| CI other | `gate-ledger.yml` → `check_gate_ledger.py`; `d117-production-proof.yml` (dispatch only) → `hydrate_d117_fixture.py`; `nightly-optin.yml` (cron) → four `tests.test_scored_*` modules, one recompute class, one v4-line module |
| CANONICAL rows that exist on `main` | `harvest_b5_window.py`, `run_b5_analysis.py`, `release_b5.py`, `independent_recompute_b5.py`, `compare_b5_recompute.py`, `tools/b5_equivalence/compare_b5_results.py`, `digest_pin_census.py`, `repin.py`, `gen_state.py`, `shard_tests.py`, `quick_suite.py`, `check_gate_ledger.py`, `launch_align_r0.py` + `run_align_r0_launchagent.sh`, `docs/paper/build/build_paper.py` |
| No importer from library or scripts, no CI/launch/CANONICAL reference | 57 scripts, 24,912 lines (section 5 sorts them) |

Library modules that no script and no CLI path reaches [V]: `scored_packer.py`, `scored_reduce.py`,
`scored_registration.py`, `scheduler_gates.py` (1,078 lines, tests only), `arm_census.py`,
`analysis_engine/reason_kinds.py` (tests only), `b5_analysis/sensitivity_parallel.py` (2-line alias),
`twins/*` (by design), `evidence_night.py` (1,970 lines; reached only as `python -m joulewise.evidence_night`).
`adapters/{ssh_transport,vllm_runtime}.py` are reached through `importlib` in `adapters/__init__.py:64-202`, and
`node_worker.py` by filename from `node_client.py:39`; they are not dead.

---

## 3. Findings

Severity is about structural risk to the stated goals (prune safely, keep v4 untouched, make the current tool
obvious), not about code correctness.

### S-01 HIGH: the v4 line never took the prune; landing it re-adds 3,187 files

- Evidence [V]: merge base of `main` and `origin/align/2026-11-08-v4-r11` is `d842f697f` (2026-10-27). Tree sizes:
  merge base 12,602, `main` 5,128, v4 line 15,789. Against the merge base the v4 line has 3,187 additions,
  112 modifications and no deletions. Additions by category: `configs/campaigns/bytes*` 2,119,
  `tests/` 331 (259 modules in `tests/align` + `tests/b6`, 81,860 lines), `docs/` 215 (42 dated run reports,
  35 process traces), `joulewise/` 141 (97 in `joulewise/align`, 38,563 lines), `.codex-report/` 83,
  `scripts/` 64, `configs/campaigns/align_pilot_v0..v3` 129, `configs/campaigns/align_v4` 38.
- Evidence [V]: `main` deleted 8,086 files since the merge base; only two of them were modified on the v4 line
  (`tests/test_launch_window.py`, `tests/test_launch_window_realization_recheck.py`), so a merge keeps the prune
  except for those two modify/delete conflicts. 28 files are modified on both sides, among them `ci.yml`,
  `configs/pins/registry.json`, `scripts/test_timings.json`, `joulewise/whole_window.py`, `joulewise/b5/harvest.py`,
  `joulewise/cli.py`, `scripts/magistrate_watchdog.py`, `RUN_STATE.md`, `TASK_QUEUE.md`.
- Evidence [V]: none of the in-flight prune's docs/config targets is modified on the v4 line (0 of the 112), and
  none is in the v4 bound-path list. The collision is confined to the CA-42 chain (S-02).
- Impact: after the landing `main` is back above 8,000 files (about 5,900 if the in-flight prune lands first), with
  new process traces, run reports and `.codex-report` files. Anyone working in a v4-line checkout today still
  sees all 8,084 pruned files, which is the condition that hid the fast recompute.
- Recommendation: plan a post-landing prune PR now, scoped to v4-line additions that are not in the registration's
  bound list (the 83 + 35 + 42 + 129 files above are not bound; checked against `ARTIFACTS` at `9abe6095f`).
  Do not touch the v4 line itself while R1/W1 run. Resolve the two modify/delete conflicts in favour of deletion
  only if the CA-42 chain is really gone on the landing side (see S-02).
- Confidence: high on the counts; medium on the post-landing total, which depends on merge order.

### S-02 HIGH: the v4 registration freezes 178 legacy `main` files in place, including the CA-42 chain

- Evidence [V] (`joulewise/align/apple/v4_registration.py` @ `9abe6095f`): `ARTIFACTS` = `_NAMED_ARTIFACTS` (54) +
  `EXECUTED_CLOSURE` (263) = 317 paths. `AMENDMENT_ALLOWLIST = ()`, so `is_strict()` is true for every path.
  `validate_receipt()` (lines 472-520) checks each path twice: the bytes at the receipt's commit, and the bytes of
  the current working tree; a missing file raises `registration_receipt missing committed artifact`, a changed one
  raises `digest drift ... (strict tier: re-register)`.
- Evidence [V]: 178 of the 317 paths exist on `main` today: 75 top-level `joulewise` modules, 51 scripts, all of
  `hazards/` and `flags/`, 10 of `analysis_engine/`, 10 adapters, 5 of `b5/`, three launchd templates, both night
  chains. `STRICT_SCRIPTS` names `scripts/launch_window.py`, `scripts/run_night.py`, `scripts/run_campaign.py`,
  `scripts/magistrate_watchdog.py`; `EXECUTED_CLOSURE` names `scripts/capture_t0_step.py`.
- Evidence [V]: on `main`, `scripts/run_night.py:3893` imports `scripts.capture_t0_step`, and lines 667 and 2620
  read and launch `scripts/launch_window.py`. Removing the CA-42 chain therefore also edits `run_night.py`, a
  strict path.
- Evidence [V]: of the 23 files in `RETIRED` (`tests/hazards/test_import_graph.py:29-41`, 29,065 lines), 21 are
  bound; only `scripts/generate_arm_readiness.py` and `scripts/assemble_v5_battery_boundaries.py` are not.
- Evidence [V]: `configs/campaigns/align_v4/registration/registration_receipt.json` is not valid JSON at
  `9abe6095f` (empty). [I] So the binding takes effect when W1 is registered; I did not and may not inspect the
  measurement checkout.
- Impact: any checkout that arms a v4 window must hold all 317 paths byte-identical to the registered commit. If
  the CA-42 prune (or any refactor of a bound file) reaches that checkout before the W1/D/C/T series is collected,
  the arm refuses until v4 is re-registered. This also re-creates the freeze-in-place model that
  `docs/process/freeze_by_commit.md` (adopted 2026-10-30) was written to end.
- Recommendation: (a) keep the CA-42 chain deletion on `main` only, and make it a rule that v4 windows are armed
  from a worktree at the registered commit, never from `main`; tag that commit (`align-v4/collection`), which is
  freeze-by-commit F1/F2 applied to v4. (b) Before merging the CA-42 prune, list its files against `ARTIFACTS`
  and state in the PR that the arming checkout is not rebased onto it. (c) At the next registration epoch, shrink
  the bound set by fixing S-03 first.
- Confidence: high on the mechanism and counts; medium on operational impact, which depends on how the magistrate
  checks out code.

### S-03 HIGH: one 91-file import component makes every entry point depend on almost everything

- Evidence [V]: with function-local imports included, 68 library modules and 23 scripts form one strongly
  connected component (173,044 lines). Module-level imports alone have no cycle. The closure table in 2.2 follows
  from it: `run_night.py`, `run_campaign.py`, `cli.py` and `magistrate_watchdog.py` all close over the same 149
  files.
- Evidence [V]: the component is held together by 27 library-to-script imports from 12 library modules, for
  example `joulewise/b5/harvest.py` → `scripts.run_campaign`, `joulewise/v5_qualification.py` →
  `scripts.harvest_g2a_window` (module level) and five more scripts, `joulewise/arm_readiness.py` →
  `scripts.reserve_calibration_window_bracket` and `scripts.validate_powermetrics_fiducial`,
  `joulewise/b5_analysis/dry_run.py` → eight scripts, `joulewise/night_gate.py` →
  `scripts.write_v5_qualification_plan`.
- Impact: (1) the v4 "executed closure" is a static walk, so it inherits the whole component (S-02). (2) Retired
  code cannot be deleted without editing live strict files. (3) The wheel CI builds (`pyproject.toml` packages
  `joulewise*` only) cannot run any of those 27 paths; `ci.yml`'s installed-wheel job asserts they fail closed.
  (4) "Which tool is current" cannot be answered from the import graph.
- Recommendation: after the v4 series, cut the 27 upward edges first (move the imported functions into the
  library, leave the scripts as thin argument parsers). That alone should break the component. Until then, add a
  ratchet test that fails on any new library-to-script or script-to-test import (allowlist = today's 27 + 12).
- Confidence: high.

### S-04 HIGH: three "what is current" authorities, and the declared one is stale

- Evidence [V]: `AGENT_PLAN.md` ("Single Source Of Truth Map", last commit 2026-09-04), `AGENTS.md` (Intake step 3)
  and `CLAUDE.md` (last paragraph) send every agent to Mission M0 and `docs/process/state_kernel.json`, "the sole
  editable authority for live work selection". The kernel says `"updated": "2026-09-25"`, holds 283 tasks
  (192 queued, 51 blocked, 7 active) and contains no task that mentions ALIGN; its seven active tasks are
  September work (`D166-PROMPT0-01`, `EVIDENCE-NIGHT-ENTRY-01`, `HEADLINE-REDUCER-SEALED-01`, ...). `ci.yml` runs
  `gen_state.py --check` on every PR, so CI enforces agreement with a list nobody works from.
- Evidence [V]: `CANONICAL.md` says the real pointer is `RUN_STATE.md`, newest numbered item first. `RUN_STATE.md`
  is 9,659 lines and 1.38 MB; lines 4,567 to about 8,780 are checkpoints T0 to T19 from August, most titled
  "superseded ... kept as record". The generated kernel region sits at lines 8838-8869. One line near the top
  (`B5-ARM-RELEASED: beta gamma`) is described as machine-read.
- Evidence [V]: `README.md` (274 lines) opens with "Now (2026-10-12)", never mentions `CANONICAL.md`, ALIGN or the
  recompute. `WINDOW_STATUS.md` was last changed 2026-08-24, `PROJECT_STATUS.md` 2026-09-04, `CLAIMS_STATUS.md`
  2026-09-12. `AGENTS.md` (Handoff) still requires "a dated report under `docs/run_reports/`", a directory the
  in-flight prune removes.
- Impact: a fresh agent that follows the repo's own instructions lands on September work. This is the same failure
  class as the hidden recompute, at the document level.
- Recommendation: make `CANONICAL.md` the single entry and say so in `README.md`, `AGENTS.md`, `CLAUDE.md` and
  `AGENT_PLAN.md` (replace the old truth map with a pointer). Either retire the kernel's authority wording and
  keep `gen_state.py --check` only as a drift check for the generated regions, or refresh the kernel; do not leave
  it declared authoritative and stale. Move `RUN_STATE.md` lines 4,567-8,780 to the archive tag (keep the
  generated region and the machine-read line). Delete or regenerate the three stale status files.
- Confidence: high.

### S-05 MED: `CANONICAL.md` is accurate where it speaks and silent on the measurement spine

See section 4 for the row-by-row result.

### S-06 MED: layer boundaries are stated in docstrings but not held

- Evidence [V]: `joulewise/b5_analysis/__init__.py` says "Desk-only block-5 analysis readers; never imported by
  collection code." The collection closure (`scripts/run_campaign.py`) contains eight `b5_analysis` modules, via
  `joulewise/whole_window.py:1572,1669` → `analysis_verified_store.py:1146` → `b5_analysis.bracket`. The fence
  (`tests/b5_analysis/test_frozen_files.py`, `test_collection_does_not_import_analysis`) checks direct imports of
  two files only, so it passes.
- Evidence [V]: `scripts/run_campaign.py`, the collection driver, imports `joulewise.analysis_engine.{claims,
  inputs, ratio, registry}`, `analysis_manifest` and `analysis_manifest_v3` at module level.
- Evidence [V]: the generic engine imports the block-specific package: `analysis_engine/inputs.py:111-119, 334,
  363-367, 3646` and `analysis_manifest_v3.py:3652, 4545` import `joulewise.b5_analysis.*`.
- Evidence [V]: `joulewise/arm_readiness.py` (13,189 lines) is on the RETIRED list yet is imported by
  `analysis_engine/inputs.py`, `bundle.py`, `cli.py`, `controller.py`, `detection_floor.py` and `b5/plan.py`
  (17 library importers, 24 scripts).
- Evidence [V]: seven scripts import test fixtures (`b5_e2e_synthetic.py`, `benchmark_b5_pack_parallel.py`,
  `benchmark_b5_speed_plan.py`, `check_campaign_generator_core_parity.py`, `issue_p8_pin_delta.py`,
  `verify_p8_replay.py`).
- Impact: measurement, analysis, registration and ops code cannot be reviewed, frozen or deleted separately. The
  blinding argument "collection cannot see analysis" rests on a fence weaker than its docstring.
- Recommendation: extend the collection fence to the transitive closure with an explicit allowlist of today's
  eight modules, then ratchet. Treat `arm_readiness.py` as live until its six non-retired importers are cut.
- Confidence: high on the edges; I did not judge whether any edge leaks outcome data (it is a structure finding).

### S-07 MED: god modules and scripts used as library

- Evidence [V]: 13 files over 4,000 lines hold 87,752 lines, about 29% of first-party non-test Python:
  `arm_readiness.py` 13,189; `scripts/run_campaign.py` 11,588; `whole_window.py` 9,456; `b5/harvest.py` 8,395;
  `calibration_ledger.py` 6,894; `analysis_engine/inputs.py` 5,421; `scripts/run_night.py` 5,242;
  `scripts/mint_floor_artifact_generalized.py` 4,883; `detection_floor.py` 4,825; `analysis_manifest_v3.py` 4,767;
  `controller.py` 4,668; `scripts/compare_b5_recompute.py` 4,421 (single file on purpose); `reduce.py` 4,003.
- Evidence [V]: `scripts/` has no `__init__.py` and is imported as a namespace package: 320 edges from tests,
  76 script-to-script, 27 from the library. `run_campaign.py` is imported by 17 library/script files and
  referenced by 61 test files; `run_night.py` by 22 and 38.
- Evidence [V]: `joulewise/` has 97 modules at top level with no grouping; the names carry the era
  (`arm_readiness_evidence_t0`, `v5_qualification`, `quiet_predicate_campaign`, `paper_reported_energy_issuer`).
- Impact: the two largest drivers are scripts that everything imports, which is why they sit in every closure.
- Recommendation: no splits while v4 runs (10 of the 13 are bound, 4 are modified on the v4 line). Afterwards:
  `run_campaign.py` and `run_night.py` become library packages with thin script wrappers.
- Confidence: high.

### S-08 MED: several generations of the same job are kept side by side

Deliberate duplication, verified independent, **not defects** [V]:

| Program | First-party imports | Fence |
|---|---|---|
| `scripts/independent_recompute_b5.py` (3,255 lines) | none; stdlib only; no `importlib`, no subprocess into first-party code | `tests/independent_recompute/test_comparator.py:807` |
| `scripts/compare_b5_recompute.py` (4,421) | none | same regex fence |
| `scripts/release_b5.py` (529) | none (runs the two above as subprocesses) | `tests/independent_recompute/test_release_b5.py:510` |
| `tools/b5_equivalence/compare_b5_results.py` (2,145) | none | separate job (D-188) |
| `joulewise/twins/engine_twin.py`, `harvest_twin.py` | none | imported only by `tests/twins/` |

The Sol/Opus twin v4 analysis engines are not on `main` (branch `engine-r23j`) and were not audited. One note:
the regex fences catch `import`/`from` lines only; an AST fence that also refuses `importlib` and `sys.path`
edits would be stronger and costs a few lines.

Generations that are not for independence [V]:

- Harvest: `harvest_window.py`, `harvest_g2a_window.py`, `harvest_v5_g2b_window.py`,
  `harvest_v5_qualification.py`, `harvest_b5_window.py` (CANONICAL names only the last; the v4 line adds a sixth).
- Floor mint: `mint_floor_artifact.py` (2,393) is loaded by path from
  `mint_floor_artifact_generalized.py:1767`.
- Analysis manifest: `analysis_manifest.py` (v1, 1,453) beside `analysis_manifest_v3.py` (4,767); v1 is still
  imported by `run_campaign.py` and three other files.
- Drivers: `python -m joulewise run` → `run_campaign.py` → `run_night.py` → `joulewise/b5/driver.py` ("the
  HAZARD_PACK branch of `run_night.py`"); each wraps the previous one.
- Config generators: `configs/campaigns/d117_contrast_v5/generate_configs.py` and
  `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py` are 3,806 lines each and differ in one line (21);
  the two v5 floor generators are 3,452 lines each and differ in 260 diff lines. The v5 packs are sealed bytes.
- Config generations: nine `configs/calibration/calibration_acceptance_d079_v2*.json`;
  `neg8_reference_corpus` and `_v5`; `window_references` and `_v5`; `d117_row_registry_v1/v2`.
- Impact: this is what `freeze_by_commit.md` describes; it is the direct cost of freezing on `main`.
- Recommendation: section 6, stage 3.
- Confidence: high.

### S-09 MED: hashing and canonical-JSON helpers are re-implemented dozens of times

- Evidence [V] (library, scripts, tools; tests excluded): 36 module-level canonical-JSON functions with 30 distinct
  bodies; 79 definitions of SHA-256 helpers under 14 names (`_sha256` 19 definitions and 6 bodies); `_is_sha256`
  10 definitions and 8 bodies; `_require_exact_keys` 10 and 10. `joulewise/validation.py` ("shared validation
  primitives with no internal dependencies") is 28 lines.
- Impact: every digest in the custody chain depends on which canonicalisation the writer and the verifier each
  picked. Some copies are deliberate (the independent programs); most are not.
- Recommendation: after v4, one canonical implementation in `joulewise/validation.py` with a test that pins its
  bytes on a corpus; replace copies only in unbound, unfrozen files, by cited rebind elsewhere. Do not touch the
  independent programs.
- Confidence: high on counts; I did not diff the 30 bodies for behavioural differences.

### S-10 MED: `docs/process_traces` is a data store that live code and tests read

Live dependencies on in-flight prune targets (census: 15 code files, 38 test modules, 29 config files cite a path
that exists today and is on the prune list). Read-versus-cite was checked for these [V]:

| Reader | What it reads |
|---|---|
| `tests/b5_analysis/test_frozen_files.py:14,99` | `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md` (parsed for every seal pin) |
| `tests/b5_analysis/test_analysed_windows_index.py:21` | `docs/process_traces/2026-10-27-l9-restart/b5-transfer/` (four manifests, 26.8 MB) |
| `scripts/promote_calibration_candidate.py:22,37` | two candidate acceptance JSON files under `docs/process_traces/` |
| `scripts/land_window_records.py:52` | writes into `docs/process_traces/rev6-windows/` |
| `scripts/issue_g2a_prefill_prompt_pin.py:63` | `docs/process_traces/2026-10-03-design-block3/windows` |
| `scripts/build_site.py:26` | `docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json` |
| `scripts/write_b5_identity_pins.py:139-140` | `configs/campaigns/d117_{floor,contrast}_qwen25_*_v1/plan_tree.json` |
| `tests/test_docs_freshness.py:135-158` | walks `docs/process_traces` |
| `configs/floor_mint/d117_qwen25_*_extraction_spec.json` (6 files) | name `order_manifest.json` in the d117 v1-v3 packs |
| `configs/analysis/b5/analysed_windows.json` | 25 citations of `docs/process_traces/2026-10-block5/*.md` (cite) |
| `joulewise/night_gate.py:134-161` | 13 ruling paths in a `records` table (surfaced in receipts; cite) |
| `configs/pins/registry.json` | 13,484 of 27,160 pin rows sit in files the prune removes; some `targets` point into `docs/process_traces` |
| `CANONICAL.md`, `docs/ARCHIVE.md` | link `docs/run_reports/2026-11-06-repo-prune.md` and `2026-11-06-b5-care-audit.md` |

- Impact: a docs prune is a code change. The seal record and the transfer manifests are registered evidence, not
  process notes.
- Recommendation: move evidence that tests or tools read to `records/` (or `tests/fixtures/`) in the same PR that
  prunes the traces, and state the new path in the test. The remaining 30-odd test modules in the census need
  the same read-or-cite check by the prune builders.
- Confidence: high for the rows above; the full census is a string match and was not classified file by file.

### S-11 MED: test organisation mirrors the history, not the structure

- Evidence [V]: 494 test modules, 353 flat in `tests/` (308,170 lines). 104 test files (133,703 lines) name a
  module on the RETIRED list. Test names in `tests/independent_recompute/` follow review rounds
  (`test_rc_cmp7` ... `test_rc_cmp11`, `test_sol_delta2_review_704_sol1`).
- Evidence [V]: `scripts/test_timings.json` has 690 timed modules; 478 exist on `main`, 212 belong to other lanes
  (deliberate: "a key superset of every open lane's map"), 16 `main` modules are untimed and covered by
  exemptions. Hosted serial time for `main`'s modules is 17,831 s (4.95 h); the ten slowest are 36% of it
  (`tests.b5_analysis.test_sources_replay` 1,311 s, `test_controller_g2b_attachment` 875 s, the two exclusive
  calibration modules 820 s and 700 s). Across all lanes the map totals 12.06 h and `tests.test_bytes_analysis`
  alone is 9,122 s.
- Evidence [V]: `nightly-optin.yml` gives four jobs with a 240-minute ceiling each to `tests.test_scored_*`.
  CANONICAL calls the scored-roster modules "dead code".
- Evidence [V]: fixtures are 60.7 MB; `tests/fixtures/b5_analysis` is 39.9 MB (about 1.4 MB per archive, 27
  archives); four fake powermetrics helpers exist (`tests/fixtures/fake_powermetrics_process.py`,
  `tests/fixtures/p2038_v3_production/`, `tests/b5_analysis/support_s10/`, `tests/fixtures/hazards/instrument/`),
  all different.
- Impact: nobody can tell which tests guard live code. The timing map is a shared merge-conflict point (modified
  on both sides of the v4 landing).
- Recommendation: decide the scored unit one way (keep and say so in CANONICAL, or delete code, tests and the four
  nightly rows together). After v4, move tests into directories that mirror the packages; delete tests with the
  retired route in the same PR.
- Confidence: high.

### S-12 MED: four freeze mechanisms, none of which lists what is frozen

- Evidence [V]: (1) block-5 freeze: `tests/b5_analysis/test_frozen_files.py` computes the frozen set from
  `sealed_inventory.json` (682 paths at head `c27485347`; on `main` today 603 match, 61 differ, 18 are missing,
  which is allowed because only a subset is enforced), `seal_pins.json` pin4, `EVOLVED_ON_MAIN` (bytes read from
  commit `b13a510dc`) and `REBOUND_WORKING_TREE` (the cited-rebind map; one entry). (2) Pin registry:
  27,160 SHA-256 literals in `tests/` and `configs/`, 23,594 of kind P, checked by `repin.py --check`; Python
  holders are keyed by line number (`TRIM_REPORT.md` section 1). (3) Import-graph fences for `hazards/` and
  `flags/`. (4) v4 `ARTIFACTS` (S-02).
- Evidence [V]: `docs/process/freeze_by_commit.md` (adopted 2026-10-30) sets Phase 1 "right after the block-5
  release"; CANONICAL does not mention it, and no `b5/collection` tag check exists in the tests.
- Impact: the answer to "may I edit this file" requires running a test or reading four mechanisms. The cited-rebind
  rule is implemented well for block 5 but exists in one test file only.
- Recommendation: a generated `FROZEN.md` (path, mechanism, registered commit, rebind citations), produced by a
  small read-only script and checked like `gen_state`. Then execute freeze-by-commit Phase 1 and apply the same
  model to v4.
- Confidence: high.

### S-13 LOW: "window", "session", "block"

- Evidence [V]: `docs/glossary_measurement_terms.md` (2026-10-12) found "window" used for thirteen things and
  ruled that prose says "session" while code keeps "window". `CANONICAL.md` (2026-11-08) and the v4 line use
  "window" in prose again ("Measurement windows", W1, "window design"). "Block" is not in the glossary and has at
  least two code meanings: a registration block ("block 5", `b5`, 165 filenames) and an ABBA block inside a
  contrast (`01_decode_contrast_blocks_01_05`). In library and script identifiers: `window` 8,078 occurrences,
  `session` 5,050, `block` 4,416, `night` 2,889, `attempt` 2,207.
- Recommendation: add "block" (both senses) and the v4 terms (R0/R1/W1/D/C/T) to the glossary; no renames in code.
- Confidence: high on the counts; the judgement is mine.

### S-14 LOW: code and evidence outside their directories; branch sprawl

- Evidence [V]: 21 `generate_configs.py` files and `_shared.py` under `configs/campaigns/` (40.5K lines before the
  in-flight prune; about 15K after); Python in `docs/` (`docs/handoff/2026-11-07-account-retirement/tools/`,
  `docs/paper/build`, `docs/paper/figures`); `.codex-report/` (58 files, 12 Python) is process traces under
  another name and is read by `tests/independent_recompute/test_input_gate.py` and `test_rc_cmp7.py`;
  `df-ph-decode-floor-mint1.json` (58 KB) sits at the repo root and is read by `tests/test_detection_floor.py`;
  `analysis/`, `figures/`, `site_capsule/`, `package.json` belong to the undecided site unit.
- Evidence [V]: the repository has 1,758 branches (370 `lane/*`, 225 `feat/*`, 160 `align/*`, 148 `fix/*`,
  136 `impl/*`, 97 `night-results/*`). CANONICAL identifies live work by branch name and sha in 20 rows.
- Recommendation: after the landing, CANONICAL should name paths on `main`, not branches; archive-tag and delete
  merged lanes.
- Confidence: high.

### S-15 LOW: dangling pointers

- `scripts/independent_recompute_b5.py:88` names `scripts/restore_run_to_scratch.py` as the restore tool; it is not
  on `main` [V].
- `CANONICAL.md` says "CI workflows: Three"; there are four (`nightly-optin.yml`) [V].
- `joulewise/b5_analysis/resume.py:39` and `tests/independent_recompute/test_release_trace_20261107.py:1` cite dated
  run reports the in-flight prune removes [V].

---

## 4. `CANONICAL.md` gaps

Row check [V]: every non-template path that CANONICAL presents as being on `main` exists. Every path that is absent
is marked "not on `main`" or sits in the "Replaced" column, with these exceptions:

| Item | Issue |
|---|---|
| "CI workflows: Three" | four exist; `nightly-optin.yml` is missing |
| `docs/run_reports/2026-11-06-repo-prune.md`, `docs/run_reports/2026-11-06-b5-care-audit.md` | linked as live; both are dated run reports on the in-flight prune list |
| `scripts/harvest_g2a_window.py` "kept only because `joulewise/v5_qualification.py` imports it" | true, and `v5_qualification.py` is itself on the RETIRED list and is v4-bound; the row should say so |
| CA-42 route "retiring in PR #668" | does not say that both scripts are in the v4 strict set (S-02) |
| Scored-roster modules "dead code" | contradicted by four nightly CI jobs |
| "Work queue ... generated from `state_kernel.json`" | does not say the kernel is stale and is not where live work is selected (S-04) |
| Twenty rows identify the tool by branch and sha | correct today; unreadable once the line lands |

Live tools and documents with no row [V: zero occurrences of each name in CANONICAL]:

| Job | Tool on `main` |
|---|---|
| Unattended session entry (LaunchAgent target) | `scripts/run_night.py`, `scripts/install_night_agent.sh`, `configs/launchd/*.template` |
| Campaign driver | `scripts/run_campaign.py` |
| Supervision | `scripts/magistrate_watchdog.py`, `scripts/install_magistrate_watchdog.sh` |
| Wall-side meter (standing rule: every measurement captures it) | `scripts/km003c_monitor.py`, `joulewise/external/km003c_{usb,parse}.py` |
| In-window hazards and flags | `scripts/hazard_monitor.py`, `scripts/collect_window_flags.py`, `joulewise/hazards/**`, `joulewise/flags/**` |
| Pre-window machine state | `scripts/prewindow_check.sh`, `scripts/quiet_mac_prep.sh`, `python -m joulewise doctor` |
| Calibration (fiducial, ledger, bracket, acceptance) | `validate_powermetrics_fiducial.py`, `recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py`, `issue_calibration_acceptance_generation.py`, `scripts/night_chains/*.zsh` |
| Block-5 desk tools | `write_b5_window_plan.py`, `check_b5_chain.py`, `size_b5_window.py`, `b5_window_calibration_verdict.py`, `advance_b5_ledger_pin.py`, `b5_phase_report.py` |
| Floors, disclosures, reported energy, results fill | `mint_floor_artifact_generalized.py`, `extract_detection_floors.py`, `produce_b5_disclosures.py`, `issue_reported_energy.py`, `build_results_fill_input.py`, `render_results_fills.py` |
| Single-run CLI | `python -m joulewise` (13 subcommands) |
| Independent twins | `joulewise/twins/**` |
| Freeze rules | `docs/process/freeze_by_commit.md`, `tests/b5_analysis/test_frozen_files.py`, `configs/analysis/b5/seal_pins.json` (pins are listed; the freeze model is not) |
| Terms | `docs/glossary_measurement_terms.md` |
| Contracts | `docs/contracts/**` (33 files; which are binding is not stated anywhere) |
| Opt-in nightly | `.github/workflows/nightly-optin.yml` |
| Fixture hydration | `scripts/hydrate_d117_fixture.py` (used by a workflow) |

Authoritative versus informational documents, as far as the tree shows [I]:

- Authoritative (read by code or tests, or sealed): `configs/campaigns/v5_claim_25g83/{registration_block5,
  analysis_plan_block5}.md`, `docs/analysis/b5/DEVIATION-LOG.md`, `docs/decision_log.md`, `docs/council_log.md`,
  `docs/align/council-2026-11-05/FINAL-DESIGN*.md`, `docs/contracts/bridge_protocol.md`,
  `docs/phase_2/window_runbook.md` (bytes pinned by the seal, per the glossary), `docs/registrations/*`,
  `docs/process/state_kernel.json` (mechanically, by CI).
- Operational: `RUN_STATE.md` top items, `docs/analysis/b5/RELEASE-RUNBOOK-lean.md`, `docs/process/MAGISTRATE_*`,
  `NIGHT_*`, `R0_HEADLESS_LAUNCH.md`, `docs/guides/instrument-guide.md`.
- Informational or historical: `docs/phase_1..5/*plan*`, `docs/specs/**`, `docs/capstone/**`, `docs/research/**`,
  `docs/strategy/**`, `docs/perf/**`, `docs/handoff/**`, `docs/paper/draft-v1-review-round*.md`,
  `docs/process/TRIM_REPORT.md`, `docs/process/pruning_list_2026-10-14.md`, `docs/process_prune_2026-09-29.md`,
  `PROJECT_STATUS.md`, `CLAIMS_STATUS.md`, `WINDOW_STATUS.md`, `AGENT_PLAN.md`.

Nothing in the tree marks a document as one or the other. A one-line status header per document (or a column in
CANONICAL) would be enough.

---

## 5. Next prune candidates (beyond the in-flight list)

Evidence columns: **code** = importers or string references from `joulewise/`, `scripts/`, `tools/`, `.github/`,
`configs/launchd`, night chains; **v4** = in the v4 bound list / modified on the v4 line. "Tests" are the tests
that go with the file. All rows [V] unless marked.

### Tier A: no live reader, not bound, not modified on the v4 line. Safe while R1/W1 run.

| # | Candidate | Size | Code readers | Tests and docs that go with it |
|---|---|---|---|---|
| A1 | P8 one-shot issuance: `scripts/issue_p8_pin_delta.py`, `scripts/verify_p8_replay.py`, `scripts/p8_evidence/` | 422 lines + 9 records | none (both import a test helper) | 1 test importer |
| A2 | Rev-5/Rev-6 calibration desk one-shots: `promote_calibration_candidate.py`, `land_window_records.py`, `sim_acc_25g83_rev5.py`, `issue_dg071_dg075_statistics.py`, `calibration_ledger_bootstrap.py`, `calibration_ledger_backfill.py` | 2,216 lines | none | 6 test modules; `docs/calibration/acc_25g83_rev5_simulation.md`. The first two lose their inputs/destination with the in-flight prune (S-10) |
| A3 | `scripts/reauthor_clean.py` (cleanup for the T-0 re-author namespaces; belongs with the CA-42 chain) | 2,389 lines | none | 1 test reference |
| A4 | WO-003/WO-005 receipts: `corpus_compat_receipt.py`, `reconcile_retained_powermetrics.py`, `floor_reconciliation_receipt.py` | 553 lines | only each other | 2 test references |
| A5 | `scripts/validate_gate_packet.py`, `scripts/replay_d117_decisive.sh`, `scripts/bench_replay_systemsetup_stub.py` | 893 lines | none | 2 test references; `.gitignore` entry `.decisive-replay/` |
| A6 | `configs/campaigns/metrology_v1/` | 209 files | a name in a list at `scripts/check_window_provenance.py:76` | `tests/test_microdelta_generate_configs.py` |
| A7 | `configs/campaigns/qwen25_7b_decode_floor_v1/` | 59 files | a name in a list at `check_window_provenance.py:75` | 4 test modules, three of which test the d117 v1-v3 packs already leaving |
| A8 | `configs/floor_mint/d117_qwen25_{1p5b,7b}{,_v2,_v3}_extraction_spec.json` | 6 files (most of the 1,989 `floor_artifact` pin rows) | none | 7 test modules; they point into the d117 v1-v3 packs |
| A9 | Root: `df-ph-decode-floor-mint1.json`, `df-ph-decode-floor-mint1.single_count.txt` | 2 files | none | `tests/test_detection_floor.py` reads it: move to `tests/fixtures/` rather than delete |
| A10 | `RUN_STATE.md` lines 4,567 to about 8,780 (superseded checkpoints T0-T19) | about 4,200 lines | none; keep the generated region (8838-8869) and the machine-read line | `tests/test_gen_state.py`, `tests/test_docs_freshness.py` to be checked first [I] |
| A11 | Stale root status: `WINDOW_STATUS.md` + `scripts/window_status.sh`, `CLAIMS_STATUS.md` | 3 files | `window_status.sh` only | kernel mentions `window_status`; `CLAIMS_STATUS.md` has no code or test reader |
| A12 | Superseded prune and plan notes: `docs/process/pruning_list_2026-10-14.md`, `docs/process_prune_2026-09-29.md`, `docs/planning_reflection_protocol.md` ("compatibility pointer"), `docs/phase_3/`, `docs/phase_5/` (last touched July) | about 10 files | none | check `tests/test_docs_freshness.py` path lists first [I] |
| A13 | `docs/handoff/**` (two dated handoffs with five tool scripts) | 7 files | none | dated process records by another name |
| A14 | `joulewise/scheduler_gates.py` | 1,078 lines | none | `tests/test_scheduler_gates.py`, one use in `tests/test_family_marker.py`; listed in `TRIM_REPORT.md` |
| A15 | `joulewise/b5_analysis/sensitivity_parallel.py` | 2-line alias | none | `tests/b5_analysis/test_sensitivity_parallel.py` |

### Tier B: one decision each, then delete as a unit

| # | Unit | Size | Why it needs a decision |
|---|---|---|---|
| B1 | Site and report pipeline (CANONICAL "kept but undecided"): `build_site.py`, `pack_capsule.py`, `release_check.py`, `build_capstone.py`, `claims_lint.py`, `make_figures.py`, `docs/site/`, `docs/site_src/`, `docs/report_src/`, `site_capsule/`, `analysis/`, `figures/`, `package.json`, `package-lock.json`, `PROJECT_STATUS.md` | 6,705 script lines + about 95 files | no importer, not bound, not in CI; last regenerated 2026-09-04; `docs/paper/artifact-guide.md` still tells readers to run `build_capstone.py`; `docs/site/run_state.html` is a stale copy of `RUN_STATE.md` |
| B2 | Scored roster: `joulewise/scored_{packer,reduce,registration}.py`, 7 test modules + 5 helpers, four `nightly-optin` rows | 973 library lines | CANONICAL says dead; DIFFICULTY is on the research list (`docs/registrations/difficulty_pack_v2.md`); `benchmark_import*.py`, `gen_gsm8k_scored.py`, `gen_math_scored.py` and `gensuite` belong to the same decision |
| B3 | `.codex-report/` | 58 files now, 141 after the landing | two test modules and one bar-set JSON reference it; move what they read to fixtures, delete the rest |
| B4 | Paper round-7 one-offs: `paper_prefill_resolvability_projection.py`, `paper_excursion_decomposition.py`, `paper_anchor_correction_quantified.py`, `check_paper_round7_artifacts.py`, `docs/paper/round7/` (one 2.4 MB JSON), `docs/paper/draft-v1-review-round*.md`, `docs/paper/fill-rehearsal/` | 3,892 script lines + about 55 files | depends on whether the BYTES-led Paper 1 keeps the round-7 material |
| B5 | Quiet guard "inactive Commit-1 installation": `joulewise/quiet_guard.py`, `scripts/quiet_guard.py`, `quiet_guard_privileged.py`, `setup_quiet_guard.sh` | 1,604 lines | not bound; `quiet_guard_process.py` is used by `arm_census.py`; the v4 launcher mentions QuietGuard, so confirm on the v4 line first [I] |
| B6 | P2-046 load transition: `joulewise/load_transition_alignment.py`, `scripts/characterize_load_transition.py`, `configs/calibration/p2_046_load_transition` | 895 lines | CANONICAL keeps it while TASK_QUEUE Q10/P2-046B is READY |

### Tier C: after the v4 series is collected (bound or modified on the v4 line)

| # | Unit | Size | Blocker |
|---|---|---|---|
| C1 | The RETIRED TRANSACTION_PACK route (`tests/hazards/test_import_graph.py:29-41`) and its tests | 23 files, 29,065 lines; 104 test files, 133,703 lines | 21 of 23 are v4-bound; six live modules import `arm_readiness.py` |
| C2 | `scripts/bench_replay_start_drift.py`, `scripts/write_b5_identity_pins.py` | 1,573 lines | modified on the v4 line (modify/delete conflict) |
| C3 | Older harvest generations (`harvest_window.py`, `harvest_g2a_window.py`, `harvest_v5_g2b_window.py`, `harvest_v5_qualification.py`), `mint_floor_artifact.py` v1, `analysis_manifest.py` v1, `joulewise/report.py` | about 6,000 lines | bound, and imported by live drivers |
| C4 | v4-line additions outside the bound list: 83 `.codex-report`, 35 process traces, 42 dated run reports, `configs/campaigns/align_pilot_v0..v3` (129) | 289 files | only exist after the landing; `scripts/align_pilot_kit.py` and `align_pilot_session.py` are strict and stay |
| C5 | Never-live NVIDIA/remote stack (`adapters/node_worker.py`, `node_client.py`, `nvidia_smi.py`, `vllm_runtime.py`, `ssh_transport.py`) | 4,570 lines | partly bound; an x86 platform is planned, so this is a keep-or-replace decision, not a prune |

---

## 6. Target structure and staged path

### 6.1 Target (end state, after the v4 series)

```
joulewise/
  core/         schemas, interfaces, validation (one canonical JSON + digest), clock, provenance, suite,
                bundle, bundle_read            # data formats and readers; old-format readers stay here (F5)
  instruments/  adapters/*, external/*, powermetrics_fiducial, kernel_clock, sampler_teardown
  measure/      controller, environment*, idle/quiet admission, prewindow, calibration_* (collection side),
                hazards/, flags/, campaign driver (from scripts/run_campaign.py), night driver (from run_night.py)
  analysis/     analysis_engine/*, reduce, detection_floor*, floor_*, whole_window, uncertainty_evidence
  blocks/b5/    b5/* (collection) and b5_analysis/* (analysis), kept apart by a transitive fence
  align/        the v4 line as it lands (unchanged)
  ops/          night_agent_install, magistrate support, agent_identity
  twins/        unchanged
scripts/        argument parsing only; one subdirectory per job: measure/ analysis/ ops/ ci/ paper/
tools/independent/   recompute, comparator, release check, equivalence comparator (stdlib only, AST-fenced)
configs/        registered/<block>/...   live/...   pins/
records/        evidence that tests or tools read (seal record, transfer manifests, window records)
docs/           contracts/ registrations/ analysis/ align/ + decision_log, council_log, glossary  (authoritative)
                research/ paper/ capstone/                                                      (informational)
tests/          mirrors joulewise/ and scripts/
CANONICAL.md    one row per job, paths on main only; FROZEN.md generated
```

Rules the layout encodes: imports go downward only (`core` ← `instruments` ← `measure`; `core` ← `analysis`;
`blocks/*` and `align` on top); nothing in `joulewise/` imports `scripts/`; nothing outside `tests/` imports
`tests/`; frozen code lives at a tag, and `main` keeps only readers of old data.

### 6.2 Staged path

**Stage 0: now. Docs and additive files only; no bound path, no file the v4 line modifies.**

1. `CANONICAL.md`: add the rows of section 4, fix the workflow count, replace the two run-report links, add a
   "Frozen and registered code" section that names the four mechanisms and the v4 bound list, and state the
   arming rule (S-02 a).
2. `README.md`, `AGENTS.md`, `CLAUDE.md`, `AGENT_PLAN.md`: first line points to `CANONICAL.md`; remove the
   run-reports requirement; mark the old truth map superseded. Decide the kernel's status (S-04).
3. Glossary: add "block" and the v4 terms.
4. Write down the merge order in one place: v4 line lands first (as `MERGE-ORDER.md` says), the CA-42 chain
   deletion lands after and never enters the arming checkout, the post-landing prune C4 follows.
5. For the in-flight prune builders: the read-versus-cite list in S-10.

**Stage 1: now. Deletions of unbound, v4-unmodified files (Tier A), one PR per row group.**
Each PR: delete code, its tests and its pins together; `repin.py --write registry`; update CANONICAL in the same
PR. No protected number is repinned, because no surviving file's bytes change; only registry rows for deleted
files disappear. Avoid `ci.yml` and keep `scripts/test_timings.json` a key superset (stale keys are harmless and
avoid a conflict with the v4 line).

**Stage 2: at the v4 landing.**
1. Tag the registered commit; arm only from a worktree at that tag.
2. Merge the v4 line; resolve the two test modify/delete conflicts.
3. Post-landing prune C4. CANONICAL rows switch from branch names to paths.
4. Add two ratchet tests (new files, so no conflict): no new library-to-script import beyond today's 27; no new
   script-to-test import beyond today's 12; collection closure may not grow beyond today's eight `b5_analysis`
   modules.
5. Generate `FROZEN.md`.

**Stage 3: after the v4 series is collected and block 5 is released.**
1. Freeze-by-commit Phase 1 as already approved (tags `b5/collection`, `b5/analysis`, and the v4 tag; freeze tests
   compare the tag's tree, not `main`'s bytes; line-number pins become behavioural or go).
2. Delete Tier C1-C3 and decide C5. Fixes to still-frozen components follow the existing cited-rebind pattern
   (`REBOUND_WORKING_TREE` in `test_frozen_files.py`); no protected number is repinned from changed bytes: either
   the bytes stay and the pin stays, or the change is a ruled rebind recorded in `DEVIATION-LOG.md`.
3. Cut the 27 upward imports: move the imported functions into the library, leave the scripts as wrappers. Verify
   with the closure table of 2.2 (target: `harvest_b5_window.py` and the analysis entry no longer close over the
   night driver).

**Stage 4: re-layout.**
Move modules into the 6.1 packages one layer at a time, with re-export shims for one release, tests moved in the
same PR, and the ratchet allowlists driven to zero. Split the god modules only after their layer is in place.
Consolidate the canonical-JSON and digest helpers last, outside the independent programs.

### 6.3 What should not change

- The independent recompute, the comparator, the release check, the equivalence comparator and the twins stay
  separate and stdlib-only.
- The v4 line, its registration files and the 317 bound paths in any arming checkout.
- Blinding and custody rules; the block-5 seal pins; the cited-rebind discipline.

---

## 7. Limits of this audit

- The v4 line was read through `git` objects only (file lists, one module, import lines). Its internal structure
  (97 files, 38.5K lines in `joulewise/align`) was not audited.
- The import graph is static. It sees `importlib.import_module("literal")` and path-based loads only where the
  argument is a string literal; subprocess launches by path are covered by the string census, not the graph.
- The S-10 census is a string match; only the listed rows were opened and classified.
- The exact file list of the in-flight prune was not available to me; where I count its effect I use the
  description given in the brief.
- No full test suite, no measurement, no model, no analysis run. Three fence modules and `gen_state.py --check`
  only.
