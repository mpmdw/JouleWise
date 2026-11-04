# Repo-trim mission: report (2026-10-30)

> **Status as of 2026-11-04 (committed copy).** This is the 2026-10-30 report, committed unchanged below this note so
> that every agent and machine can find it. It is the deletion list for Phase 2 of
> [`freeze_by_commit.md`](freeze_by_commit.md), kernel task `FREEZE-BY-COMMIT-01`. **That task is the first
> follow-up after the block-5 release.** Nothing in section 6 may be deleted until Phase 1 of `freeze_by_commit.md`
> has landed.
>
> Items closed since the report was written:
> - PR #605 merged (section 5.1; section 8 item 7).
> - Section 8 item 1 (`_is_sha256`): #617.
> - The MG-11/MG-12 coverage maps (item 7): #618.
> - `ci.yml`'s stale `site.yml` comment (item 14): #624.
> - Section 8 item 4 (tests writing into the real custody registry): #611 (CUSTODY-T1).
>
> Section 9's PR #605 instructions and worktree paths are historical. Line counts are as of 2026-10-30.


Lane: `lane/2026-10-30-repo-trim*`, worktree `/Users/edr/jw-trim` (plus a detached baseline worktree
`/Users/edr/jw-trim-base` at `origin/main`, used only for the before-change suite run). Not committed to any
main-bound PR.

## 1. Result in one paragraph

Almost nothing in this repository can be deleted under the mission's hard boundaries. The block-5 seal lists
every tracked file under `joulewise/` and `scripts/` as of `H_claim` (`tests/test_b5_seal_landing.py` proves
the inventory is exactly that set): 150 of 167 `joulewise/` files and 165 of 171 `scripts/` files. The six
unsealed code files outside `joulewise/b5_analysis/` are all used by the block-5 analysis. The test tree is held in
place by three further locks:
- `configs/pins/registry.json` records pins in 2,644 holder files: 2,319 pack configs, 74 test-side Python files,
  190 fixtures and 17 goldens. Rows in Python holders are keyed by line number, so any edit that moves a pinned line fails
  `repin.py --check`;
- pack arm-readiness evidence records test ids and skip counts of named test modules;
- the sealed registration cites some test allowlists.

Docs are cited by process traces. So the work splits into:
- one small, reviewable de-dupe PR (tests only);
- a precise inventory of what can go once the seal and pins are lifted, with evidence for each item.

Tracked tree, counted as newlines over all tracked blobs:
- at the start (`origin/main` `66f9b6be3`): **12,878 files, 4,426,339 lines**;
- at current main (`e46637f9d`, after PRs #604 and #606 landed): **12,919 files, 4,444,436 lines**;
- with PR #605 merged into current main (head `26dd1dfd9`): **12,918 files, 4,444,291 lines** (-1 file, -145 lines).

The NEEDS-ED list below
covers about 31,000 lines of retired arm-chain code (plus roughly 115,000 test lines that name it), about
40,000 lines of census data, and about 1,570 lines of re-implemented verification helpers. All of that is
behind the seal, the pins or the release path.

## 2. Method

- **Protected sets, computed first** (all under `/private/tmp/jwtrim/inv/`):
  - sealed paths: 682 from `sealed_inventory.json`, plus `seal_pins.json` and `identity_pins.json`;
  - pin holders (2,644) and pin targets (1,941) from `configs/pins/registry.json`;
  - files touched by the 45 open PRs (3,055 paths, from `git diff origin/main...origin/<head>` for every
    open head, including the BYTES measurement line `lane/2026-10-28-bytes-pass2-open`);
  - the block-5 analysis and collection paths, the coordination files, `.codex-report/`, and the records trees.
  - 40 tracked paths under `custody*`, `restricted`, `.scratch*`, `runs_claim` and `runs_bound` names were
    excluded from every search and never read.
- **Reachability.** An AST import graph covers `joulewise/`, `scripts/` and `tests/`. Its edges are module and
  function-level imports, `importlib` strings, `scripts/x.py` path literals, sys.path stems, and `-m`
  references in shell, zsh and launchd files. It is closed over 99 roots:
  - the CLI;
  - every CI workflow step (`ci.yml`, `gate-ledger.yml`);
  - `.mcp.json` and `.codex/config.toml`;
  - the launchd templates;
  - the block-5 analysis and collection entry points;
  - the night, watchdog and quiet-guard scripts;
  - the powermetrics fiducial and calibration issuers;
  - every script a runbook names (`docs/phase_2/*runbook*`, `docs/process/NIGHT_HANDBACK.md`,
    `MAGISTRATE_*`, guides, playbook, release checklist).

  Every `joulewise/` module is reachable. 46 `scripts/` files are not (section 6.1, item 3), and all 46 are sealed.
- **Reference census.** Every non-code tracked file was matched against the whole tree by path, basename and
  stem (`rg -F`, one pass per pattern class). For each candidate the referrers were classed as code, CI or
  infra, live docs, coordination files, and records.
- **Duplication census.** Three passes:
  - exact-AST function-body matches across all Python files: 118 groups, about 1,262 duplicated lines;
  - name-pattern counts of verification helpers;
  - pairwise line-overlap of test files: only one near-duplicate pair.
- **Test runs.** A parallel per-module runner used Python 3.13 with `TMPDIR=/private/tmp/jwtrim/tmp/<run>-w?`,
  `PYTHONDONTWRITEBYTECODE=1` and `JW_B5_SYNTHETIC_ONLY=1`, inside a `sandbox-exec` profile. The profile denies
  reads and writes of `/Users/edr/night-custody`, `/Users/edr/night-archive`, other `jw-b5-*` worktrees,
  `/Users/edr/code/JouleWise*`, any `/private/tmp/jw*` except `/private/tmp/jwtrim`, and any
  `restricted|runs_claim|runs_bound` path component outside `/private/tmp/jwtrim` (the synthetic fixtures the tests
  build under their own `TMPDIR` stay allowed).
  - Why: several tests hard-code real custody paths. `tests/test_rev6_custody_plan_id.py` reads
    `/Users/edr/night-custody/...` when present, and that directory exists on this laptop. Without the sandbox, a
    full local run would read custody data.
  - Recommendation for Ed: make those tests honour `JW_B5_SYNTHETIC_ONLY=1` (section 8, item 3).
  - After the lead's blinding check (section 8a), every local run also excludes 143 modules that contain a real-path
    literal. The whole-suite evidence for the PR is CI on Ubuntu, which runs all of them; the local runs are
    supplementary.

## 3. PRs opened

| PR | Scope | Tier | CI | Files / lines removed |
|---|---|---|---|---|
| #605 (draft) | De-dupe (tests only): delete the superseded, never-collected `docs/paper/fill-rehearsal/test_select_outcome_branches.py`; `tests/test_experiment.py` imports `fake_environment_run` from `tests/test_controller.py` instead of carrying an identical copy | light | green on the final head `26dd1dfd9` (main `e46637f9d` merged in): 20 pass, gate-ledger skipped as a draft | 1 file deleted, 1 edited; -146 / +1 lines |

There is no pure-deletion PR. Every deletion candidate that survived the checks turned out to be protected (section 4).

Verification for PR #605:
- **CI.** The whole suite on head `26dd1dfd9`, which has main `e46637f9d` merged in (ci run 41018691101): green.
  Since then main has gained only RUN_STATE commits.
- **Local, before versus after,** sandboxed, 143 custody-risk modules excluded.
  - Main `e46637f9d`: `modules=317 tests=6105 failed_modules=7`. PR head: `modules=317 tests=6105 failed_modules=7`.
  - The per-module results are identical. The seven failures are artifacts of the local environment and are the same
    on both trees:
    - the sandbox denying setuid `/bin/ps`;
    - the custody-registry write in section 8, item 4;
    - a bare `from test_mlx_runtime import` under `-m unittest`;
    - subprocess timeouts under concurrent load.
- **Behaviour-pinning tests** (`test_experiment` 39, `test_controller` 74, `test_select_outcome_branches` 5): OK before
  and after.
- **Gate ledger.** `scripts/check_gate_ledger.py` on the filled body (`PR605_BODY.md`) reports
  `light tier passes (5 rows, Impact statement answered)`.

## 4. Candidates examined and why each one stayed

These looked like DELETE until a check found a binding:

- `tests/goldens/config_schema.json`: no test reads it, but `docs/specs/axi/sa_burst_decode_contract.md:2176`
  makes it the hand-authored oracle for `print-config-schema | diff -u tests/goldens/config_schema.json -`. It
  still equals the current output. KEEP. Its twin `output_schema.json` is checked by `tests/test_schemas.py`, and
  the same automated check could be added for this one.
- The three `@unittest.skip("U2 successor engine pending")` tests in `tests/test_calibration_live_three_window.py`:
  the U2 engine was superseded by D-126 on 2026-08-08. But the module is run by `joulewise/arm_readiness_evidence.py`,
  and every pack's `arm_readiness.sources/three-window-regression.json` records `tests_run: 23, skipped: 3` and the
  test ids. Deleting the tests would change regenerated pack evidence. NEEDS-ED (goes with CA-42).
- The R-6 skip in `tests/test_arm_readiness_lifecycle.py` and the `_v2` skip in `tests/test_d117_decode_contrast_plan.py`:
  both modules' test ids are recorded in pack configs, and the second file is a pin holder. NEEDS-ED.
- Pruning-list (a) rows. The orchestrator's decision 7a cleared them for after the L9 merge.
  - MG-14, `tests/test_single_count_discipline_census.py`: imported by `tests/test_single_count_discipline_matrix.py:494`,
    which is a pin holder.
  - MG-15, the rationale census: `tests/fixtures/d165_rationale_allowlist.json` is cited by the sealed
    `registration_block5.md` and read by `tests/flags/test_flags_collect.py`.
  - MG-15, the custody-mode inventory: named in `docs/process/state_kernel.json`, and its allowlist is read by
    `joulewise/b5/harvest.py`.
  - All three are NEEDS-ED.
- `tests/replay_wi13_rev5.py` and `tests/verify_registered_calibration_snapshot.py`: neither is imported or
  collected, but they are calibration-issuance verification tools cited by the Revision-6 and D-138 records.
  NEEDS-ED.
- `configs/characterization/char-t3appup-r0{1,2,3}.json`: no code reads them, but they are the configs of banked
  T3 captures. ARCHIVE-NOTE.
- Root `df-ph-decode-floor-mint1.json` and `.single_count.txt`: stray-looking, but the JSON is a kind-P pin
  target (`floor_artifact`), read in place by `tests/test_detection_floor.py:2251,2419` and
  `tests/test_mint_floor_artifact.py:1512`, and cited by window `SHA256SUMS` and `harvest.json` records. NEEDS-ED.
- Fixture orphans: none. Every `tests/fixtures/*` entry is referenced by name, or loaded by a directory glob or an
  f-string (`envelope-{n:02d}.json`, `dwell/*.txt`).

## 5. DE-DUPE

### 5.1 Consolidated (PR #605)

- `docs/paper/fill-rehearsal/test_select_outcome_branches.py` (-79 lines) is the 2026-09-04 copy of
  `tests/test_select_outcome_branches.py`. It sits outside `tests/`, so CI never ran it, and today it errors.
  What covers it: `test_rendered_abstract_word_budget_accepts_250_and_rejects_251` survives under the same name,
  and `test_reader_facing_counts_exclude_html_comments` survives as `test_reader_facing_counts_exclude_comments`.
- `fake_environment_run` in `tests/test_experiment.py` (-67 lines) was identical as an AST to the one in
  `tests/test_controller.py`. It is now imported from there, as six other modules already do. The same tests run
  with the same results.
- Lines saved: 145 net.

### 5.2 Left for Ed (all inside sealed, pinned or evidence-bound files)

**Re-implemented verification helpers in sealed code** (name-pattern census, `joulewise/` and `scripts/`):

| Helper job | Definitions | Files | Lines |
|---|---:|---:|---:|
| SHA-256 of a file or bytes | 56 | 51 | 173 |
| finite-number guards | 47 | 37 | 251 |
| canonical JSON bytes | 31 | 26 | 168 |
| strict / duplicate-key JSON loaders | 26 | 18 | 391 |
| fsync / atomic write | 17 | 16 | 212 |
| SHA-256 string validators | 17 | 17 | 79 |
| repo-relative path guards | 13 | 12 | 160 |
| exact key-set checks | 11 | 9 | 137 |
| **Total** | **218** | | **~1,570** |

Notes on the table:
- The canonical-JSON variants are not equivalent. Some use `ensure_ascii=True`, for example
  `benchmark_import.py:161`, `hazards/base.py:222` and `quiet_guard.py:172`; most use `False`. Some allow NaN.
  Two modules that hash the same non-ASCII object would get different digests.
- Recommendation: after the block-5 release and recompute, add one `joulewise/strict_io.py` (canonical bytes,
  strict loader, digest helpers, fsync and atomic write, path guard), then move the modules over one at a time.
  Each move should come with byte-identical golden checks of every artifact the module writes. A variant whose
  bytes differ (the `ensure_ascii` and `allow_nan` cases) stays as a named variant, so no digest changes.

**Exact copy-pasted functions in sealed code** (the largest groups):
- `probe_backup_root`, `probe` and `backup_roots`: three copies each in `check_paper_replay_fence.py`,
  `paper_anchor_correction_quantified.py` and `paper_excursion_decomposition.py` (about 120 lines).
- `parse_campaign_lock`: `b5/harvest.py` and `run_campaign.py`.
- `_neg8_bracket_references` and `_neg8_reproduces`: `b5/harvest.py` and `whole_window.py`.
- `_forbidden_admitted_vocabulary_paths` and `walk`: `detection_floor.py` and `floor_extraction.py`.
- `_parse_finite_admission_int` and `_float`: three copies each.
- `_acknowledge_result_custody` and `_raise_task_failure`: `nvidia_smi.py` and `vllm_runtime.py`.
- Five helpers shared between the two AXI spike scripts.

**Parallel generations of the same tool** (sealed):

| Tool | Generations | Lines |
|---|---|---:|
| Floor mint (the generalized mint imports the original as its core, so this is layering rather than a copy) | `mint_floor_artifact.py`, `mint_floor_artifact_generalized.py` | 7,248 |
| Analysis manifest | `analysis_manifest.py` (frozen issued v1), `_v2`, `_v3` | 6,416 |
| Night harvesters | `harvest_window`, `harvest_g2a_window`, `harvest_v5_g2b_window`, `harvest_v5_qualification` (plus the live `harvest_b5_window` and `b5/harvest.py`) | 1,878 |
| Night and plan generators | `gen_derivation_night`, `gen_evidence_night`, `gen_g2_phase_d`, `generate_g2a_probe_inputs`, `write_derivation_night_inputs`, `write_v5_qualification_plan` | 4,482 |
| Acceptance issuers and replays | `issue_calibration_acceptance_generation`, `reissue_calibration_acceptance`, `promote_calibration_candidate`, `sim_acc_25g83_rev5`, `issue_epoch_continuation`, `issue_p8_pin_delta` | 5,383 |
| Agent bridge | `codex-bridge`, `codex-run` (CLAUDE.md: "the older hardened" protocol), `bridge`, `codex-app-bridge.mjs` | 3,267 |

**Mirrored tests that exist only because the code is duplicated.** Terminal-review trailer parsing is
implemented twice: `scripts/capture_t0_step.py::_verify_terminal_review` and
`joulewise/arm_readiness_evidence_t0.py::_derive_terminal_review`. Both test modules carry the same nine-vector
table. Both implementations belong to the retired arm chain (CA-42), so the right fix is deleting both, not
merging them.

**Overlapping tests:**
- `tests/hazards/test_import_graph.py` already checks that the flags package reaches no retired module, and that
  hazards import no flag code.
- `tests/flags/test_flags_import_graph.py` repeats those checks. Its fresh-interpreter lazy-core check is unique,
  so it is not a clean removal. Merge them into one when MG-22 is executed.

**Near-duplicate test files.** `tests/test_d117_floor_qwen25_1p5b_plan.py` and `..._7b_plan.py` match on 57%
of lines. They share `governed_*`, `commit_fixture`, `fake_report` and `checkout_inventory` with
`test_d117_decode_contrast_plan.py`. All three are pin holders, and their test ids are recorded in pack evidence.
Leave them until the Qwen2.5 packs are formally retired.

**Refusal-code tables doing overlapping jobs** (left for Ed):
- `configs/gates/hazard_refusals.json`;
- `configs/flags/number_rows.json` (28,989 lines) and `configs/gates/physics_rows.json` (7,605 lines). These are
  coverage maps of the 2026-10-06 gate-prune inventory. Both are pin holders, and `joulewise/hazards/battery.py`
  lazily reads the second.
- `joulewise/analysis_engine/reason_kinds.py`;
- `configs/analysis/b5/dry_run_refusal_classes.json`;
- `tests/hazards/refusal_census.py`;
- `tests/test_reason_code_partition.py`.

**Intentional redundancy, kept on purpose (ARCHIVE-NOTE):**
- `joulewise/twins/engine_twin.py` and `harvest_twin.py`, the blind twins, with `tests/twins/`.
- The independent block-5 recompute `scripts/independent_recompute_b5.py` and its comparator `scripts/compare_b5_recompute.py`, with `tests/independent_recompute/` (merged in PR #604 while this mission ran). The recompute must stay free of L9 imports.
- `scripts/check_campaign_generator_core_parity.py`.
- `tests/scored_*_oracle.py` and the checkers.
- The receipt oracles (`joulewise/receipt_oracle.py`).
- `tests/verify_*` replays.

## 6. NEEDS-ED (one-line recommendation each)

Timing labels follow `docs/process/pruning_list_2026-10-14.md`:
- **(a)** now;
- **(b)** after the block-5 release and the independent recompute agree;
- **(c)** before block 6.

### 6.1 Retired code behind the seal

1. **Retired arm and T-0 chain (CA-42), about 31,000 code lines.** Files: `arm_readiness.py` (13,126 lines),
   `arm_readiness_evidence*.py`, `t0_rehearsal.py`, `night_gate.py`, `v5_qualification.py`, `arm_retry.py`,
   `network_time_off.py`, `dwell.py`, `scheduler_gates.py`, `capture_t0_step.py`, `launch_window.py`,
   `author_arm_*`, `generate_arm_readiness.py`, `produce_t0_rehearsal_bundle.py`, `rehearse_t0_unattended.py`,
   `v5_s1_desk_closeout.py`, `check_v5_arm_abort.py`, `restore_v5_null_reservation.py`,
   `assemble_v5_battery_boundaries.py` and `scripts/ed_session/*`. About 99 test files name these modules. The
   pruning list estimates about 17,000 of these lines are removable once the helpers still in use move into
   `hazards/` and the shared modules.
   - **(b)** Delete after the release. First move the physical probe functions into `hazards/`, and drop the
     module-level `import arm_readiness` in `bundle.py`; the hazards import-graph test proves that import exists.
   - Then regenerate the pin registry and record the pack-evidence break in one dated note.
2. **Provisional NVIDIA and remote stack, never live (4,570 lines).** Files: `adapters/node_worker.py`,
   `node_client.py`, `ssh_transport.py`, `nvidia_smi.py`, `vllm_runtime.py`, and their tests.
   - Retire after the paper, or keep only if the align/GPU lanes (PRs #521 and #524) adopt them; check those
     lanes first.
3. **Unreachable sealed scripts** (no root reaches them). Recommendation for each:
   - **Retire after the seal lifts:** AXI one-shot spikes `axi_sb_static_batch_spike.py` and
     `axi_sc_spec_decode_spike.py` (3,015 lines with `spike_mlx_prompt_cache.py`). Their verdicts are recorded in
     `docs/specs/axi/s{b,c}_*_verdict.md`. Also `codex_usage_probe.py`, `measure_claude_cold_start.sh`,
     `gen_affine_smoke.py`, `gen_gsm8k_scored.py`, `gen_jw_mixed.py` and `scripts/ed_session/*.sh`.
   - **Ask the owning lane** (process tools reachable only from their own tests): `land_window_records.py`,
     `validate_gate_packet.py` and `derive_estate_anchors.py`.
   - **Keep:** `gen_math_scored.py` (DIFFICULTY may need it; ask its lane).
   - **Keep as record generators** (ARCHIVE-NOTE once the paper is final): `paper_prefill_resolvability_projection.py`,
     `paper_renumber_refs.py`, `paper_terms_lint.py`, `dependence_sensitivity.py`,
     `issue_dg071_dg075_statistics.py` and `paper/partial_record_enclosure.py`. They regenerate
     `docs/paper/round7/*`.
   - **Keep, calibration evidence chain:** `issue_epoch_continuation.py`, `issue_p8_pin_delta.py`,
     `verify_p8_replay.py`, `scripts/p8_evidence/*`, `sim_acc_25g83_rev5.py` and `replay_d117_decisive.sh`.
   - **Keep, on the block-5 test path:** `render_results_fills.py` (used by `tests/b5_analysis/test_s10_chain_defects.py`).
   - **Decide with the quiet-predicate lane:** `bench_replay_start_drift.py`, `bench_replay_systemsetup_stub.py`,
     `check_sealed_bundle_compatibility.py`, `corpus_compat_receipt.py`, `analyze_phase_share.py`,
     `characterize_load_transition.py`, `reauthor_clean.py`, `issue_g2a_prefill_prompt_pin.py` and
     `check_campaign_generator_core_parity.py`. All are test-only reachable.
4. **Floor mint "v1"** (`scripts/mint_floor_artifact.py`, 2,391 lines). This is **not** a dead generation:
   `mint_floor_artifact_generalized.py` loads it as its core (`_ORIGINAL_MINT_PATH`, line 103) and pins its
   interface (line 1732). It also renders the frozen v1 carriers
   (`tests/test_mint_floor_artifact.py::test_frozen_v1_carriers_keep_bytes...`).
   - KEEP. Merging the two files is a review-pinned estimator-interface change, so it is not worth doing before
     the paper.
5. **Analysis manifest v1 and v2** (`analysis_manifest.py` is frozen issued code, a kind-P `issued_code` pin;
   `analysis_manifest_v2.py`). Keep v1, since an issued artifact is pinned against it. Retire v2 if no stored
   manifest uses it **(b)**.

### 6.2 Pinned or cited data

6. **Root `df-ph-decode-floor-mint1.json` and `.single_count.txt`.** Move them to
   `docs/legacy/floor_artifacts/` and repoint the two tests and the registry row. The move changes a cited path in
   window records, so do it with a dated note, or leave the files where they are.
7. **Coverage maps MG-11 and MG-12** (`configs/gates/physics_rows.json` and `configs/flags/number_rows.json`,
   36,594 lines, both pin holders).
   - MG-11 is wrong that "runtime mentions it only in comments": `joulewise/hazards/battery.py:1040,1111-1129`
     builds `PROTECTS` lazily from `physics_rows.json`.
   - Delete both **(a)** with the battery edit, `tests/hazards/test_physics_coverage.py`,
     `tests/flags/test_number_coverage.py`, `tests/flags/number_rows_builder.py` and
     `test_flags_fx_regressions.py::test_number_rows_name_the_harvest_joins`, then run `repin.py --write registry`.
8. **The remaining pruning-list (a) rows, cleared by decision 7a but blocked here:**
   - MG-13: pin registry and `repin`.
   - MG-14: single-count census. Fold its import from the matrix test first.
   - MG-15: rationale census, cited by `registration_block5.md`; and the custody-mode inventory, named in the
     state kernel and read by `b5/harvest.py`.
   - MG-16: docs-freshness clause maps.
   - MG-17 and decision 6: state kernel, `TASK_QUEUE.md` and `gen_state.py`. These are coordination files, so
     execute them from the lead session.
   - MG-18: the CI step `verify_receipt_histsem.py`.
   - MG-20: paper supplier-pin census.
   - MG-21: `tests/test_b5_seal_landing.py`.
   - MG-22: reason-code partition and import fences.
   - MG-26: the proof-leg registry and custody census inside `tests/test_mint_floor_artifact_generalized.py`, a
     pin holder.
   - Recommendation: one lead-run PR per row, each with `repin.py --write registry` where a holder changes.
9. **`.github/workflows/d117-production-proof.yml`.** It is dispatch-only, and its header says it is not runnable
   at main because of a `STACK_IDENTITY_DOMAIN` AttributeError. The test file now imports that name from
   `joulewise.detection_floor`, so the header may be stale.
   - Either re-run it once by dispatch and update the header, or delete the workflow together with MG-26.
     Decide WO-PROOF-RUNNABILITY-REPAIR's fate either way.
10. **Retired-design docs cited only by process traces:** `docs/specs/suite_next/*` (6 files),
    `docs/campaign_packs/c5_*` (8), `docs/strategy/2026-08-0*` plans, `docs/specs/advisor_status_site_analysis.md`,
    `docs/specs/axi/sd_*` and `se_*` drafts, and `docs/process/instrument-readiness-audit-charter-DRAFT.md`
    (superseded by the non-DRAFT charter).
    - Optionally move them in one sweep to `docs/legacy/` with a redirect list. They are not evidence, but process
      traces link them.
11. **The site and RPT-001 lanes:**
    - `docs/site/**` (39 files, a stale 2026-09-04 snapshot), `docs/site_src`, `site_capsule/`, root
      `package.json`, and the sealed `build_site.py`, `pack_capsule.py` and `release_check.py`;
    - `docs/report_src/**`, `analysis/rpt001-v1`, `analysis/rpt001-v2` and `figures/rpt001-*`, with the sealed
      `build_capstone.py`, `make_figures.py` and `claims_lint.py`. The RPT-001 legacy L1 results are voided by
      D-078.
    - Recommendation: if Paper 1 does not use them, retire both lanes after the paper **(b)**. `docs/site/*.html`
      is also globbed by `tests/test_docs_freshness.py:48`.
12. **Skipped tests bound into pack evidence:**
    - `test_calibration_live_three_window.py`: three U2 skips;
    - `test_arm_readiness_lifecycle.py`: R-6;
    - `test_d117_decode_contrast_plan.py`: `_v2` freeze transition.
    - Delete them with CA-42, since they test retired code.
13. **One-off verification tools:**
    - `tests/replay_wi13_rev5.py` hard-codes `/Users/edr/night-custody/measurement/...-derivation-w2`;
    - `tests/verify_registered_calibration_snapshot.py`, `tests/verify_w1w2_disposition_sources.py` and
      `tests/verify_calibration_acceptance_corpus.py`.
    - They are cited by the Revision-6 and D-138 calibration records. Keep them until the calibration in force is
      superseded, then archive.
14. **Stale CI comment.** `ci.yml`'s last comment points to `.github/workflows/site.yml`, which no longer exists.
    Delete those three lines in the next full-tier CI PR.

## 7. ARCHIVE-NOTE (records and deliberate redundancy; kept)

- `docs/process_traces/` (8,081 files, 1.71M lines), `docs/legacy/` (311 files, 625K lines),
  `docs/run_reports/`, `docs/reviews/`, `docs/stream_logs/`, `docs/advisor_briefs/`, `docs/council_log.md`,
  `docs/decision_log.md` and `docs/project_status_history.md`.
- 108 tracked `*.log` files under `docs/process_traces/` match today's `.gitignore`. They were committed before the
  ignore rule existed, as verification logs, and are records.
- Historical campaign configs:
  - the nine Qwen2.5 packs `d117_{floor,contrast}_qwen25_*_v1..v3` (about 1,300 files), retired by D-167 but
    pinned (`pack_config_bytes`, 19,382 pins);
  - `p2_015_floors`, `metrology_v1`, `qwen25_7b_decode_floor_v1`, `splitwise_decode_v1`,
    `exploratory_2026_07_17` and `neg8_reference_corpus`.
- `configs/characterization/char-t3appup-r0{1,2,3}.json`: configs of banked T3 captures.
- `docs/paper/fill-rehearsal/**` except the deleted test copy, and `docs/paper/round7/**`: paper records, partly
  pinned.
- `analysis/rpt001-v{1,2}` and `figures/rpt001-v{1,2}`: v1 is pinned, v2 is read by sealed scripts.
- `env/bundle_pack_selection.md`: the REPRO-2 record, cited by the 2026-07-13 audit.
- `tests/goldens/config_schema.json`: the manual AXI-SA schema oracle (section 4).
- Intentional second implementations (section 5.2): the twins, the independent recompute and its comparator, the
  parity checker, the oracles and the replays.

## 8. Possible bugs in modern code (reported, not fixed)

1. **`joulewise/load_transition_alignment.py:104` `_is_sha256` accepts strings that are not digests.** It checks
   `len == 64`, `int(value, 16)` and `value == value.lower()`. Python's `int(..., 16)` accepts a `0x` prefix,
   surrounding whitespace and `_` separators.
   - Verified: `_is_sha256("0x" + "a"*62)` and `_is_sha256(" " + "a"*63)` both return `True`.
   - Severity: low. A hand-made record passes the shape check, and the later digest comparison would still fail.
     Every other validator in the tree uses a 64-character lowercase-hex test.
2. **Canonical JSON is not one function.** About 25 variants differ in `ensure_ascii` and `allow_nan`
   (section 5.2). This is not a confirmed bug, since no pair was found hashing the same object across modules. But
   it is a latent digest-mismatch hazard.
3. **Tests that read real custody data on a measurement-capable laptop.** `tests/test_rev6_custody_plan_id.py`
   (`REAL_CORPUS_ROOT = "/Users/edr/night-custody"`), `tests/verify_w1w2_disposition_sources.py`, and the
   `/Users/edr/code/JouleWise` readers in `test_floor_extraction`, `test_run_campaign` and
   `test_rpt001_report_slice` ignore `JW_B5_SYNTHETIC_ONLY=1`.
   - A full local run without a sandbox reads custody if the path exists. It exists on the analysis laptop.
4. **Two test modules write into the real custody registry. This is the most serious finding in this list.**
   `tests/test_axi_controller_events.py` (for example
   `test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`, `:346`) and `tests/test_axi_mock_spec.py`
   (for example `test_v2_campaign_writes_complete_immutable_ledger_and_pair_reports`, `:464`) run a campaign without
   setting `JOULEWISE_CUSTODY_PARENT`.
   - So `joulewise/measurement_liveness.py:118` `publish_campaign` calls `mkdir` on, and publishes into, the real
     `~/night-custody/active-campaigns`, because `custody_parent()` defaults to `~/night-custody` at
     `measurement_liveness.py:72`.
   - My sandboxed run caught it: four `PermissionError: ... '/Users/edr/night-custody/active-campaigns'` errors.
     Nothing was read or written there.
   - Without the sandbox, on this laptop or on the measurement Mac, these tests would publish fake active-campaign
     entries that the liveness census, the quiet guard and `run_campaign`'s stale-lock reclaim
     (`scripts/run_campaign.py:4699`) read.
   - Fix: set `JOULEWISE_CUSTODY_PARENT` to a temporary directory in both modules, as `test_run_campaign.py:101` and
     `test_run_campaign_hazard_flags.py:64` already do. Alternatively, make `custody_parent()` refuse the home default
     under unittest.
   - **Owner:** cloud seat CUSTODY-T1, on `lane/2026-10-30-custody-test-isolation`. It covers both modules, a
     whole-suite search and a decoy-HOME regression guard. The lead confirmed `~/night-custody/active-campaigns` holds
     nothing.
5. **`docs/site/fonts`.** `Fraunces-600.woff2` is byte-identical to `Fraunces-900.woff2`, and
   `IBMPlexSans-400.woff2` to `IBMPlexSans-600.woff2`, so the site's declared weights render the same. This is
   cosmetic, on the retired site.
6. **Stale headers and comments:** `d117-production-proof.yml`'s "not runnable" header (item 9) and `ci.yml`'s
   `site.yml` reference (item 14).
7. **`docs/paper/fill-rehearsal/test_select_outcome_branches.py` errored when run.** It is removed in PR #605.

## 8a. Blinding check (the lead asked on 2026-10-30)

None of `tests/test_rev6_custody_plan_id.py`, `tests/verify_w1w2_disposition_sources.py`, `test_floor_extraction`,
`test_run_campaign` or `test_rpt001_report_slice` ran in any local run. Per run:

1. **Full run, first attempt (task `bz51q8xrc`).** It never started: the output directory did not exist, so the shell
   failed before Python launched. No module ran.
2. **Full run, second attempt (task `b8iin0h97`)**, via `sandbox-exec` with the deny profile, 8 workers ordered
   longest-first. I stopped it on the lead's message.
   - Only queue positions 1–12 had started: 4 completed, 8 were killed.
   - The five modules and the four test modules that import `verify_w1w2_disposition_sources` sit at positions 14,
     26, 157, 192, 194, 199, 271 and 312. None of them started.
3. **Focused PR #605 run** (`tests.test_experiment`, `test_select_outcome_branches`, `test_paper_terms_lint`,
   `test_paper_successor_migration`), sandboxed. None of the five ran or were imported. Ran 70, OK.
4. **`python3.13 -m unittest test_select_outcome_branches`** inside `docs/paper/fill-rehearsal`, not sandboxed. That
   file only. Ran 2, 1 error.

Every later local run excludes 143 modules (138 before main gained PR #604's tests), listed in `/private/tmp/jwtrim/inv/exclude_modules.txt`: every test module
whose source, or an imported test helper, contains `/Users/edr`, `Path.home()`, `expanduser`, `night-custody` or
`night-archive`, plus quick_suite's `CANONICAL_PATH_MODULES`. CI on Ubuntu covers them, because the paths do not exist
there.

## 9. Permissions and blocks

- **Blocked: finishing PR #605's gate ledger.** The Claude Code auto-mode classifier denied `gh pr edit 605 --body-file ...`
  and `gh pr ready 605` ("Unrequested Commit in a Connected App"). The PR is still a draft, and its body still shows
  rows 2 and 3 as `NOT-RUN`.
  - The completed body (rows 2 and 3 = `RUN 26dd1dfd9a432fddac79475da8fd41d8aac41f19`, with the verification tails) is
    saved at `/Users/edr/jw-trim/PR605_BODY.md`.
  - To finish: `gh pr edit 605 --body-file /Users/edr/jw-trim/PR605_BODY.md && gh pr ready 605`. Then confirm the
    gate-ledger check goes green. If main has gained more than RUN_STATE commits by then, merge main into the branch
    first and re-run CI.

- Worktree creation (`/Users/edr/jw-trim`, `/Users/edr/jw-trim-base`), `git push` of lane branches and `gh pr
  create` all worked without a prompt.
- One local measurement command was refused by a built-in safety check: a `git archive | tar -xOf - | wc -l`
  pipeline, flagged as an unparseable rm-like risk. It deleted nothing. Line counting was redone with `git
  cat-file --batch` in `/private/tmp/jwtrim/inv/count.py`.
- Cleanup for Ed or the lead: remove `/Users/edr/jw-trim-base` and `/Users/edr/jw-trim` with
  `git worktree remove` once PR #605 is settled.
