# P2-042 frozen analysis-manifest emitter — 2026-07-10

## Scope and authority

Implemented queue row P2-042 on `impl/p2042`, without committing. Scope was
the deterministic manifest emitter, its shared validator/registry model, and
the two minimal compatibility shims explicitly required by
`docs/specs/c027/analysis_engine_trio.md`: config discovery excludes the new
sidecar and `claims_lint` can lint the analysis registry. No P2-037 consumer,
claim verdict, bundle analysis, campaign execution, or hardware work landed.

Authority order used: `docs/specs/c027/ADJUDICATION.md` analysis-trio rulings,
then the P2-042 component of `analysis_engine_trio.md`, then the task prompt.
AP-2 uses four estimand-local six-contrast families per model and only gross
request, idle-subtracted request, gross prefill, and gross decode. No B14
reason code was added or changed.

## Baseline and workspace

- Start: `impl/p2042...origin/main`, clean.
- Baseline: `python3 -m unittest discover -s tests` -> `Ran 879 tests in
  31.425s`, `OK (skipped=11)`.
- During the run the shared `origin/main` reference advanced by 16 commits to
  the P2-040 integration head. This worktree was not rebased or merged because
  the user assigned a no-commit/pathspec handoff. Incoming changes overlap
  `scripts/claims_lint.py`, `tests/test_claims_lint.py`, `RUN_STATE.md`, and
  `TASK_QUEUE.md`; the lead must preserve both sides during integration.

## Per-unit status

| Unit | Status | Result |
|---|---|---|
| Registry/AP freeze | complete | Added reviewable `slice_2m_ap2.v1.json`; raw registry bytes and the exact AP-2 section bytes are SHA-256 linked; registry/AP family, role, and Holm method must agree. |
| Manifest model + validator | complete | Added canonical `am-<sha256>` identity, exact-key validation, source/config/order hash checks, semantic entry/cell/block IDs, sentinel linkage, full family/contrast enumeration, and fail-closed mutations. |
| Generator emission | complete | Writes `order_manifest.json`, then builds/self-validates and atomically replaces `analysis_manifest.json`; both paths print only after both writes succeed. No time, host, Git, absolute-path, or nondeterministic field is emitted. |
| Minimal compatibility | complete | `run_campaign.discover_configs` ignores both manifest sidecars; `claims_lint --mode analysis-registry` checks the template against AP-2. No campaign verdict semantics were added. |
| Verification | complete | One/two-model shape, exact 24-ID hand-built expectation, linkage/uniqueness, double-run and reversed invocation bytes, semantic IDs, source tamper, and mutation negatives pass. |

## Files

Added:

- `configs/analysis_registry/slice_2m_ap2.v1.json`
- `joulewise/analysis_manifest.py`
- `tests/test_analysis_manifest.py`

Modified:

- `scripts/generate_matrix.py`
- `scripts/run_campaign.py`
- `scripts/claims_lint.py`
- `tests/test_generate_matrix.py`
- `tests/test_run_campaign.py`
- `tests/test_claims_lint.py`
- `RUN_STATE.md`
- `TASK_QUEUE.md`

## New tests

`tests/test_analysis_manifest.py`:

- `test_one_and_two_model_shape_and_entry_identity`
- `test_exact_one_model_contrast_enumeration_matches_hand_built_cross_product`
- `test_sentinel_and_family_linkage_invariants`
- `test_analysis_manifest_bytes_are_identical_across_double_run_and_reverse_invocation`
- `test_semantic_block_ids_do_not_follow_mutable_numeric_block_index`
- `test_validation_rejects_dropped_cell_id_mutation`
- `test_validation_rejects_duplicated_contrast_id_across_families_mutation`
- `test_validation_rejects_cross_block_end_sentinel_mutation`
- `test_validation_rejects_removed_contrast_with_frozen_m`
- `test_validation_rejects_non_frozen_status_and_ap_snapshot_mutations`
- `test_validation_rejects_tampered_config_and_order_hash`

Other coverage:

- `test_discover_configs_excludes_order_and_analysis_manifest_sidecars`
- renamed/extended live lint gate:
  `test_real_analysis_plans_and_registries_lint_clean`
- existing generator determinism/config tests now include or exclude the new
  sidecar as appropriate.

## Verification

Focused:

```text
Ran 25 tests in 2.241s
OK

Ran 77 tests in 10.195s
OK

Ran 11 tests in 0.966s
OK
```

Repository lint:

```text
python3 scripts/claims_lint.py --mode analysis-registry --json
errors=0 warnings=0
```

Final canonical suite tail:

```text
----------------------------------------------------------------------
Ran 891 tests in 33.592s

OK (skipped=11)
```

`git diff --check` passed. No fake-NVIDIA load flake occurred.

## Deviations and contradictions

The trio body predates adjudication in the nested `floor_selector` example:
it uses window aliases (`gross_request`, `idle_subtracted_request`,
`gross_phase`) plus ad hoc `combine`/`transport` strings. The adjudication says
the implemented `joulewise.detection_floor_artifact.v1` schema/resolver is
authoritative with no aliases. The emitter therefore freezes P2-039 vocabulary:
`request|phase`, `floor_gate_j`, semantic condition-family IDs, and
`same_stack_componentwise_worst_case.v1`. This is an intentional adjudication-
over-spec deviation; the top-level and contrast object shapes remain as
specified.

Read-only inspection of `origin/impl/p2039` found the implemented artifact
schema and transport refusal rule, but not the typed `resolve_floor` public
surface promised by the P2-039 spec/adjudication wording. P2-042 does not need
or emulate that consumer. The lead should adjudicate that mismatch before
P2-037 integration rather than adding aliases here.

## Double-check list and handoff

- [x] No timestamps, randomness, host identity, absolute paths, or Git state in
  the emitted manifest.
- [x] Byte-identical rerun and reversed model invocation order.
- [x] Semantic block IDs unchanged when a second model changes numeric order.
- [x] Four six-contrast families per model; 24 confirmatory contrasts/model.
- [x] Every generated config represented once; both sentinels represented and
  linked per block.
- [x] Dropped `cell_id` and duplicated cross-family `contrast_id` fail after
  manifest identity is recomputed.
- [x] No P2-037 consumer or campaign-verdict behavior added.
- [x] No commit, push, campaign, or hardware measurement performed.

Next exact step: lead reviews the diff against the now-advanced P2-040 main,
resolves overlapping pathspecs without dropping either side, reruns the focused
tests and canonical suite at the integrated head, then commits by pathspec.
