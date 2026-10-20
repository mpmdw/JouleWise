# L9 ruling on Q-RENDERER, Q-LINEAGE, Q-EXACTSTACK, Q-CONSUMERID (lead, activation 4b350f47, 2026-10-20)

Inputs: packet JouleWise-data `packets/l9-questions-4b35` (726912f); two blind seats, both executing on synthetic
fixtures and tracked sealed config only: Opus 5.5 (`claude/l9-council-opus-tzdg1f` 1199d86,
`reports/l9-council-4b35/opus.md`) and Sol 6.1 xhigh (`codex/l9-council-sol` cf26555, `reports/l9-council-4b35/sol.md`).
Code: `lane/2026-10-13-l9-s10` d2c8460a3. No real-window value was read by either seat or by the lead.
Status: lead ruling, pending the cold Fable and cold Opus passes that claim-path rulings get; the build waits for them.

## Common

- A check that cannot make a number wrong (a record, receipt, lineage carrier or declaration that cannot be re-confirmed)
  becomes a limitation printed beside the result. A check whose failure means a wrong or inapplicable number (different
  stack, model, workload, phase or length; unreadable operand; failed numerical replay) still refuses.
- Limitations travel in the existing claim-verdict list `inputs.limitations` (`analysis_engine/artifact.py` 86-92, 1104;
  built in `analysis_engine/__init__.py` near 1922). No new flag module, schema or catalog (Sol proposed
  `joulewise/analysis_flags.py` plus a config; not adopted: the existing list carries strings to the verdict and the fill
  with no new path). The codes are not added to the sealed L6 window flag catalog.
- No registered arithmetic, threshold, exclusion or kept-unit count changes. Each ruling either removes a wrong refusal or
  keeps a refusal. Every comparison it adds is an identity or digest equality (exact, because bit-identity is the property).
- The four `CONDITIONAL_SEAMS` in `tests/b5_analysis/fixtures_s10.py` are replaced by production behaviour and deleted;
  `tests/fixtures/b5_analysis/s10/PROVENANCE.md` 159-162 is updated.
- Decided from code and sealed config before any real data was seen; committed before release.

## Q-RENDERER: step 11 ends at the validated fill input (seats split; lead's call)

`dry_run.step_11` (`joulewise/b5_analysis/dry_run.py` 1033-1063) runs the disclosures and `build_results_fill_input`, and
stops. Both `render.main` calls are removed. The step record carries the note
`results_rendering: "not_run_no_block5_template"`. `scripts/render_results_fills.py` is untouched; its stale 1p5B/7B row
names go to the paper lane's list.
Why (a), not Sol's (c): the renderer is the retired Window-A template (its rows are `RETIRED_FALLBACK (D-174)`); writing a
block-5 Results renderer decides which numbers print and how, which is paper-lane work that belongs after release, from the
validated fill input, under the Results cold gate that re-derives every printed value. Sol's point stands that the plan's
step 11 names validated Markdown; that is a process step, not arithmetic, and the orchestrator owns layout (CLAUDE.local
rule 8). The fill input is what the dry run must prove, and its builder already refuses through the registered
`results_fill_*_mismatch` codes. Sol's seat also correctly rejects the seam's "stop line accepted as rendered output".

## Q-LINEAGE: the aggregate carries a producer-lineage inventory (both seats)

- All components on one lineage: unchanged, one `provenance.launch_lineage`.
- Components on different lineages: the aggregate omits `launch_lineage` and carries `provenance.producer_launch_lineages`,
  one entry `{plan_id, launch_lineage}` per producer in `producer_calibration_plans` order, each the lineage the mint
  already authenticated for that producer. Never both shapes on one aggregate.
- The aggregate refusal `launch_lineage_conflict ... does not carry one authenticated lineage`
  (`scripts/mint_floor_artifact_generalized.py` near 3090, reached from 3455) is deleted. The per-producer call (3385-3388)
  stays a refusal: one producer is one window. The code stays in `dry_run_refusal_classes.json` (other sites raise it).
- Mixed marker-bearing and legacy provenance (near 3086) gives an entry with `launch_lineage: null` and the limitation
  `floor_producer_lineage_absent:<plan_id>`.
- Component rebuild (3665-3670) takes each producer's own entry. `_validate_v2_artifact_binding` checks the inventory equals
  the pinned components' carriers.
- `authenticate_floor_artifact_bytes` (`analysis_engine/inputs.py` 1089-1110) authenticates every entry; a failure becomes
  the limitation `floor_launch_lineage_unauthenticated:<plan_id|aggregate>` instead of a raise. A carrier-only discrepancy
  flags; a mismatch of a component's numerical content or source membership still refuses (Sol), since component bytes
  are digest-pinned and that is the number's binding.
Numbers: none change; an aggregate becomes issuable where an irrelevant equality blocked it.

## Q-EXACTSTACK: `exact_stack_only` means the stack is exact, served by the group's single source cell (both seats)

One shared predicate, defined in `joulewise/detection_floor.py` (Opus's placement; no new module), used by the finalizer
(`analysis_manifest_v3._authenticate_floor_dependencies`), the close-out (`dominance_closeout._contrast_floor_binding_error`)
and `analysis_engine/inputs.py` (`_floor_request_or_refusal` and the `resolve_floor` exact branch). A cell serves consumer
family F only when: its key family is F, or it is the sole `source_cell_ids` member of a transport group whose
`allowed_consumer_condition_families` admits F by id and sha256; backend, metric, window class, phase and length match;
`stack_identity_sha256` equals the consumer's; the cell is `claim_usable`; exactly one cell qualifies. Status `exact`;
`floor_cell_id` and `source_cell_ids` name the real source cell (no copy under another key); limitation
`floor_cell_from_floor_pack:<F>:<cell_id>`. Still refused: another stack, a group that does not admit F, zero or several
sources. v3's ban on cross-stack transport stays. The gate floor equals the source cell's `floor_gate_j` exactly (max of a
singleton; the mint asserts it at 3243; assert it again in the exact branch). The source cell id prints beside each
contrast floor.
Numbers: no value changes; today no GAMMA arm has a floor, after this each arm's registered floor resolves.

## Q-CONSUMERID: the sealed identity unit is the declaration (both seats; Sol's refinement adopted)

On the hazard route, for an `unprojected` pack with `freeze_receipt: null`, `_frozen_consumer_identity_set`
(`inputs.py` 4409-4608) reads the declared set from the sealed pack's one identity unit for the family, under the committed
pack tree that the lineage `pack_sha256` authenticates (pack digest, one unit per family, every file's sha256). A distinct
return value marks "hazard declaration unauthenticated", not the ARM empty set. If it cannot be authenticated,
`_floor_request_or_refusal` (4646-4648) records `consumer_identity_set_unauthenticated:<family>` as a limitation, skips the
subset test and continues to resolution, where the floor match on scientific and stack identity still binds.
`consumer_identity_undeclared` (4649-4650) refuses only when the arm's scientific identity (model, workload, phase, length,
stack) is not in the declared set; a difference only in fields that are not part of the scientific identity (Sol's
executed counterexample: a metadata tag) becomes the limitation `consumer_identity_recording_difference:<family>`. The ARM
route (projection `frozen`) is unchanged.
Numbers: values unchanged; the registered result prints where today every contrast floor refuses.

## Build (after the cold passes)

One Sol 6.1 xhigh round on top of `lane/2026-10-20-l9-silly-numbers` (or d2c8460a3 if that round is not merged yet), write
scope the union of the seats' file lists for the adopted options (Opus §Files per question, plus Sol's test files for
LINEAGE and CONSUMERID), with `configs/flags/number_rows.json` regenerated only if `tests/flags/test_number_coverage.py`
fails, and `tests/hazards/test_refusal_allowlist.py` run. Then the executing review, the J1-J6 and C5-C9 reruns on the Mac
with no conditional seams, and the cold Fable and Opus passes at L9's merge.
