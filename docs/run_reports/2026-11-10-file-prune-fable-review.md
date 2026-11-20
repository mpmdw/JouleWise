# PR #708 cold review (Fable 5.2): post-Block-5 file prune

Reviewed head `2df4fc6ec86a37d3a8449a6e365ff31acfe24fda` against `origin/main`
`281f690dc` (merge-base `bfe0f4c78`). Read-only: checkout and Git objects only,
`gh pr view 708` / `gh pr checks 708` for CI state. No push, no merge, no edit
other than this file. Scratch output and bytecode went to the session
scratchpad, not the checkout.

## Verdict: ADMIT-WITH-FIXES

The deletions themselves are sound. All 410 deleted blobs are byte-identical at
`archive/process-traces-before-release-prune-2026-11-08`, nothing ALIGN v4
binds was deleted or changed, no frozen B5 source or pin literal moved, and
only dedicated tests were removed.

It cannot merge as it stands, for reasons outside the deletion set:

- Two repository guards fail on the new `tests/test_prune_ops.py`
  (F1, F2). Both reproduce locally and match red CI jobs.
- CI shards 8 and 12 are also red and I could not reproduce either locally
  (F3). Their logs must be read before merge; I had no log access.
- Two retained documents on live lines still cite deleted files by bare path
  (F4, F5).

## Findings

| ID | Severity | Evidence | Fix |
|---|---|---|---|
| F1 | BLOCKER | `tests/test_shard_tests.py:154` `test_every_discovered_module_has_timing_or_documented_exemption` fails: `'tests.test_prune_ops'` has no weight in `scripts/test_timings.json` `seconds_by_module`, no `timing_exemptions` entry, and is outside the `untimed_module_allowance` prefixes. This module is in the quick tier and in ordinary shard 1; CI `quick` and `test (3.13, 1)` are red. | Add `"tests.test_prune_ops": 8.4` to `seconds_by_module` (after `tests.test_promote_calibration_candidate`; 8.4 s is the local run of its 13 tests). Rerun `tests.test_shard_tests`. |
| F2 | BLOCKER | `tests/test_git_fixture_maintenance.py:316` `test_every_test_module_routes_git_initialization_through_shared_helper` fails with `{'test_prune_ops.py': (24,)}`: `tests/test_prune_ops.py:24` runs `git init -b main` directly. This module is in ordinary shard 5; CI `test (3.13, 5)` is red. | In `tests/test_prune_ops.py` import `init_git_fixture` from `tests.git_fixture` and replace line 24 with `init_git_fixture(self.repo, "-b", "main")`. Rerun `tests.test_git_fixture_maintenance` and `tests.test_prune_ops`. |
| F3 | HIGH | CI `test (3.13, 8)` and `test (3.13, 12)` failed (`gh pr checks 708`, 18:17 PST, all jobs finished). Neither F1 nor F2 is in those shards under the CI packing recomputed from this checkout; that packing correctly predicted the shard 1 and shard 5 failures. I ran 33 of 44 shard-8 units and 34 of 43 shard-12 units locally; all pass. Not run: see "Not run" below. | Read the two job logs. If the failures are in the modules listed under "Not run", decide whether they come from this PR or are hosted flakes, and record which. Do not merge on a rerun alone without knowing the cause. |
| F4 | MED | `docs/run_reports/2026-11-06-b5-care-audit.md:6,57,174` cite the U90 "evidence folder" and `part5-head-stacks/detail.txt`, `cprofile-on-steps0-3b/report.txt` by folder-relative name. Those files are deleted in g1 and these citations were not rewritten. The care audit is the named authority (CARE) of `docs/analysis/b5/DEVIATION-LOG.md:17,23` and `docs/analysis/b5/LEAN-COVERAGE-AUDIT.md:24`. The g1 reader search matched full paths only. | Rewrite the three citations to `archive/process-traces-before-release-prune-2026-11-08:docs/run_reports/2026-11-06-b5-under-90/<file>`, as was done for the two parent reports. Both targets resolve at the tag. |
| F5 | MED | `origin/align/2026-11-08-v4-r11:docs/align/apple_path.md:340` cites `docs/legacy/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5952` as the reconstruction of the 0.0998 J/token design input. g1 deletes that file (`docs/ops/FILE-PRUNE-G1.tsv:2`). The cited line exists at the archive tag. The ALIGN doc is not on `main`, not in `v4_registration.ARTIFACTS`, and has no code reader, so this is a provenance citation only. | Either keep the file (restore from `origin/main`, flip the TSV row to KEEP, and correct the counts to 111 / 409 / 4,762), or leave it deleted and record in the g1 report that ALIGN must re-cite to the tag:path form at integration. This PR cannot edit the ALIGN line. |
| F6 | MED | `gate-ledger` is red: the PR body has no `## Gate ledger` section. It is a required check (`.github/workflows/gate-ledger.yml`). | Lead fills the ledger after the fixes. Row 3 must name the final head, and any `RUN <path>` pointer to this review resolves only if this file is committed at that head. |
| F7 | LOW | `CANONICAL.md:96` names `joulewise/gensuite.py`. It is a package directory, `joulewise/gensuite/`. | Correct the path. |
| F8 | LOW | `tests/archived_campaign.py:11-14` raises a bare `CalledProcessError` when the archive tag is absent (source zip, tagless clone) and passes no `timeout`. Two tests now hard-depend on it. CI shard 2, which holds both tag readers, is green, so hosted checkouts do have the tag. | Raise an assertion that names the tag and `git fetch --tags`. Optional: pin the three blob ids so a moved tag cannot change the oracle. |
| F9 | LOW | `docs/phase_2/window_runbook.md:183-184`: the stage-list example block now holds `archive/...:` object paths, which are not valid stage-list lines. | Use a current v5 directory as the example and cite the archived pair in prose. |
| F10 | LOW | Net bytes go up: 4.79 MB deleted, 15.96 MB added. `docs/ops/BRANCH-NAME-CONSUMERS.tsv` (7.4 MB), `PIN-UNRESOLVED.tsv` (3.9 MB) and `PIN-COMMITS.tsv` (3.3 MB) are regenerable by `scripts/ops/prune_refresh.py`. | Lead's call: keep these three on main, or keep them only on the ops branch / at a tag and cite them. |
| F11 | LOW | `docs/run_reports/2026-11-10-file-prune-g3.md:51` describes the unlanded g3 prototype as preserved at `/private/tmp/jwsol-file-prune/g3-unlanded.patch`. That path does not survive a reboot. | If the prototype matters, push it to a branch and cite that; otherwise say it is scratch. |
| F12 | LOW | `scripts/test_timings.json`: `tests.test_mlx_runtime` went 0.038 to 0.219 after a test was removed (a local with-import observation replacing a hosted median). Scheduling hint only; nothing asserts it. | Optional: restore 0.038. |

### Notes for the lanes that merge later (no action in this PR)

- ALIGN `docs/align/v4/dynamic_closure_trace.json` (a bound strict artifact)
  lists `scripts/spike_mlx_prompt_cache.py` under `by_event.opened`. That
  bucket is evidence only; `executed` does not contain it and no ALIGN test
  compares the trace to a regeneration. The committed bytes stay valid.
  Regenerating the trace after this prune would drop that entry and change a
  bound artifact, so regenerate only with a planned re-registration.
- Both live lanes modify `configs/pins/registry.json`,
  `scripts/test_timings.json` and `tests/test_floor_extraction.py`; BYTES also
  modifies `CANONICAL.md`. A scratch three-way merge of
  `tests/test_floor_extraction.py` is clean on both lanes and keeps the
  archive reader. `CANONICAL.md` conflicts with BYTES (one hunk). The registry
  needs `repin.py --write registry` at each integration.
- `repin.py --check` prints its existing sealed-inventory note with 80 paths;
  19 sealed-inventory files are now absent from the tree (18 on main, plus the
  spike). B5 collection is finished, so this is a note, not a finding.

## What I verified, and how

**1. Nothing live is deleted**

Verified in full (all 410 paths):

- Every deleted blob equals the blob at
  `archive/process-traces-before-release-prune-2026-11-08:<path>` (0 mismatches).
- The DELETE rows of `FILE-PRUNE-G1/G2/G4.tsv` equal the actual deleted set
  exactly (112 + 297 + 1). All 410 retaining refs resolve.
- Full-path search of the PR head for all 410 paths (2,551 hits). Every hit is
  one of: the inventories; historical harvest manifests and SHA256SUMS that
  describe archived window copies, not the checkout; `docs/ops` census
  snapshots; archive-qualified citations; the commit-scoped registry target;
  `sealed_inventory.json`.
- Token search (`p2_015_floors`, `b5-under-90`, `b5-robust`,
  `SYNTHESIS-IMPACT-FIRST`, `spike_mlx_prompt_cache`) over `joulewise/`,
  `scripts/`, `tests/`, `configs/`, `.github/`: the only code readers left are
  the retained `calibration_plan.json` and the retained NEG8 start config.
- Zero hits in `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAIMS_STATUS.md`,
  `docs/decision_log.md`, `configs/gates/hazard_refusals.json`,
  `docs/paper/artifact-guide.md`, `.github/workflows/`.
- Directory walkers over `configs/campaigns` and `scripts/`: none depends on
  the removed pack contents.
- ALIGN v4 (`9abe6095f`): every path-like string constant in
  `joulewise/align/apple/v4_registration.py` was intersected with the deleted
  and modified sets. Intersection is empty, no constant is a parent directory
  of a deleted path, and all 178 bound paths that exist on main are present
  and byte-identical at the PR head.
- CA-42 (g3): all 30 inventory paths and the plan's module and script list are
  present and byte-identical to main. `scripts/ed_session/` and
  `scripts/author_arm_*` are unchanged.
- BYTES stage 1 (`912cf8c3a`) and ALIGN: branch-only lines mentioning a
  deleted path were listed against main. The only live ones are F5 and the
  trace note above.

Sampled or reasoned, not exhaustive:

- Computed loaders. I searched for glob and walk patterns and for path
  assembly from parts; I did not trace every dynamic path in the codebase.
- B6, x86 and port lanes were not in the brief and were not searched.

**2. Pins and frozen science**

- `git diff origin/main...HEAD` is empty for `joulewise/`, `.github/`,
  `scripts/run_campaign.py`, `configs/analysis/`, `configs/gates/`,
  `configs/campaigns/v5_claim_25g83/`, `RUN_STATE.md`, `TASK_QUEUE.md`,
  `CLAIMS_STATUS.md`, `docs/decision_log.md`.
- No hex literal changed in any retained non-registry source file.
- Registry, compared per holder as a multiset of (family, target) so line
  shifts drop out: no retained holder lost a binding. All 344 removed kind-P
  rows sit in deleted holders (23,594 to 23,250). Five kind-B `source_digest`
  rows were gained that main's registry had not yet indexed. No working-tree
  target is missing.
- `calibration_plan.json` still hashes to its sidecar value `e529a062...`.
- Tags: local `archive/process-traces-before-release-prune-2026-11-08`
  (`efd15e06` peeling to `901d7580d`) and `b5/analysis-r1-9bfix-ref`
  (`57bd0af6` peeling to `e7eb872d`) match
  `docs/ops/execution-2026-11-08/TAG-LS-REMOTE-PROOF.tsv`.
- All 25 concrete archive citations in the head resolve with `git cat-file -e`
  (three more are patterns). The five `archive/pre-prune-2026-11-06:` script
  paths resolve.

**3. CANONICAL.md and the archive guide**

Read both diffs. Path tokens were checked against the checkout: the archive
guide and the new pack README have none missing; CANONICAL's new rows are
right except F7. The `kv-size` verb exists. The Retired table matches the
inventories, and the first-prune section of `docs/ARCHIVE.md` is intact.

**4. Deleted tests**

AST comparison of each edited test module against main:

- `tests/test_modularity.py`: six `CampaignSpecificationTests` methods and the
  `run_campaign` helper removed; both `ClosedSetRegistryTests` unchanged. The
  archived generator is stdlib-only, so no retained code lost coverage.
- `tests/test_mlx_runtime.py`: one method removed
  (`test_spike_report_rejects_equal_truncated_decodes`); 61 others unchanged.
  `joulewise/kv_size.py` keeps `tests.test_kv_size`.
- `tests/test_floor_extraction.py`, `tests/test_d117_floor_qwen25_1p5b_plan.py`,
  `tests/b5_analysis/test_result_equivalence.py`: one method changed each, at
  the read site only.

## Commands and results

Python 3.13, `-B`, one module at a time, `TMPDIR` and `PYTHONPYCACHEPREFIX` in
the scratchpad. Modules whose source names paths under `/Users/edr` outside
the checkout were not run. 98 whole modules and 3 single tests ran, in about
14 minutes of test wall time.

| Command | Result |
|---|---|
| `python3 -B -m compileall -q joulewise scripts tests` | rc 0 |
| `python3 -B scripts/repin.py --check` | PASS, 16 families current |
| `tests.b5_analysis.test_frozen_files` | 4 OK |
| `tests.test_b5_seal_landing` | 9 OK |
| `tests.test_docs_freshness` | 31 OK |
| `tests.test_modularity` | 2 OK |
| `tests.test_mlx_runtime` | 42 OK |
| `tests.test_prune_ops` | 13 OK (8.4 s) |
| **`tests.test_shard_tests`** | **FAILED, 1 of 8 (F1)** |
| **`tests.test_git_fixture_maintenance`** | **FAILED, 1 of 6 (F2)** |
| `tests.hazards.test_refusal_allowlist` | 23 OK, 1 skip |
| `tests.test_floor_extraction...test_specs_match_pinned_order_manifests_and_membership_shape` | 1 OK |
| `tests.test_d117_floor_qwen25_1p5b_plan` | OK (whole module) |
| `tests.b5_analysis.test_result_equivalence` | OK, 2 skips |
| `tests.test_mint_floor_artifact` | 42 OK |
| `tests.test_repin`, `tests.test_digest_pin_census`, `tests.test_gen_state`, `tests.test_shard_split`, `tests.test_ci_docs_only`, `tests.test_kv_size` | all OK |
| `tests.test_d165_rationale_census`, `tests.test_battery_float_consumers`, `tests.test_single_count_discipline_census`, `tests.test_custody_isolation_guard`, `tests.test_git_fixture_hygiene`, `tests.test_s0_blocked_enumeration` | all OK |
| `tests.flags.test_flags_collect`, `tests.test_arm_readiness_evidence`, `tests.test_v5_block4_x1`, `tests.test_v5_block4_x2`, `tests.test_v5_qualification_plan`, `tests.test_quiet_guard`, `tests.test_window_env_allowlist`, `tests.test_bytes_campaign_split` | all OK |
| The other whole modules run from CI shards 5, 8 and 12 (see F3), including `tests.test_arm_readiness_evidence_t0` (214 s), `tests.test_controller`, `tests.test_neg8_corpus_cap`, `tests.hazards.test_monitor`, `tests.hazards.test_import_graph` | all OK |

CI at 18:17 PST (`gh pr checks 708`, all jobs finished): `fences`, `build`,
`installed-wheel`, `changes`, both exclusive jobs and shards 2, 3, 4, 6, 7, 9,
10, 11 pass; `quick`, `gate-ledger` and shards 1, 5, 8, 12 fail. Shard 2 holds
both archive-tag readers and the tag-bound equivalence test, so its pass
confirms the tags are present on hosted checkouts. `fences` covers
`gen_state.py --check`, `repin.py --check`, docs freshness and
`verify_receipt_histsem.py --require-published` on the PR merge ref.

### Not run (candidates for the unexplained shard 8 and 12 failures)

- Shard 8: `tests.test_validate_powermetrics_fiducial_p2_vpf`,
  `tests.test_evidence_night`, `tests.test_validate_powermetrics_fiducial_hazard`,
  `tests.test_battery_float`, `tests.independent_recompute.test_sol_delta_review_704`,
  `tests.b5_analysis.test_deadline_observer`, `tests.b5_analysis.test_row_selection_context`,
  `tests.test_quiet_predicate_campaign` (one test run, OK),
  and, because they name out-of-checkout paths, `tests.test_d117_contrast_v5_pack`,
  `tests.test_rev6_custody_plan_id`, `tests.test_paper_round7_artifacts`.
- Shard 12: `tests.b5_analysis.test_bracket`, `tests.b5_analysis.test_dry_run`,
  `tests.test_harvest_b5_trigger_scope`, `tests.test_harvest_b5_p2harv`,
  `tests.test_p2_ctl_calibration`, `tests.b5_analysis.test_vdl_core`,
  `tests.test_analysis_engine_evidence_roots`, and, for out-of-checkout paths,
  `tests.test_agent_identity`, `tests.test_magistrate_watchdog_b6`.

None of these names a deleted path, and a static scan found no repo-wide
walker in them that the added files would trip. That is a reason to suspect
hosted flakiness, not evidence of it.
