# 70c — RULING: D165-SIDECAR-EMIT-01 design + stage-1 identity correction

Magistrate ruling over four consult seats (Sol xhigh 70, terra xhigh 71,
Opus 5 contract lens 70b, blind Fable 70d) on the stage-2 mint of the
`joulewise.d165_dominance_replay.v1` sidecar, plus a bench verification of
the one finding two seats converged on independently. Tree:
`feat/d165-dominance-closeout-core` @ `140ec4cc` (PR #254, unmerged).

## A. Stage-1 defect (blocker on PR #254): the block-identity model is unsatisfiable in production

Claim (Opus R1 from the admitted-vs-prospective angle; blind Fable risk 1
from the namespace angle): `_manifest_block_membership_error`
(`joulewise/dominance_closeout.py:1246-1287`) looks up sidecar cells by the
manifest's `contrasts[].cell_a_id/cell_b_id` and requires each sidecar
cell's block-id set to EQUAL `contrasts[].block_ids`.

Bench verification (magistrate, 2026-09-01):
- Floor-mint blocks: `configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json:414`
  `d117-df-cmp-abba-ph-decode-qwen25-7b-b01` … (detection-floor campaign).
- Contrast blocks: `configs/campaigns/d117_contrast_v5/generate_configs.py:1191`
  `block_id()` → `d117-decode-contrast-bNN`; the frozen v3 manifest carries
  `d117-decode-contrast-b01` at `analysis_manifest_v3.json:154`.
- Manifest cell ids are finalizer-derived: `analysis_manifest_v3.py:3120`
  `cell_id = f"cell-{measurement_arm}-{arm_label.lower()}"`; floor cells are
  bound to arms by selector (`:3312-3331`: backend, metric, window_class,
  condition_family_id + sha, transport group, stack sha, `claim_usable`),
  never by id.
- The floor artifact v2 records per-cell `members[]` (bundle ids;
  `scripts/floor_mint_pinsets/schema_v2.json:333`), not block ids; block ids
  exist only in the extraction spec inside the pinset.

Therefore a physically correct sidecar — blocks from the floor spec, cells
from the floor — lands in `manifest_block_membership_mismatch` → the
neither-branch, for every production pack, forever. The stage-1 suite is
green only because `tests/test_d165_dominance_closeout.py:41-68` builds its
toy floor from the manifest's own `CELL_IDS` and `block_ids`. Contract line
`docs/contracts/d165_dominance_closeout.md:151` ("The finalized manifest's
comparative block identity") is wrong. Refuters 40b passed this; the miss is
recorded against those lenses in the council log.

RULED (stage-1 correction, lands on the PR #254 branch before stage 2):
1. Sidecar `cells[].cell_id` is the FLOOR artifact's comparative cell id.
2. Every sidecar block gains `members`: an object with exactly the keys
   `A1, B1, B2, A2` → bundle id. `block_id` stays, defined as the extraction
   spec's block id (informational; unique within the cell).
3. Close-out binding replaces the manifest-block census: for each floor
   comparative cell present in the sidecar, the union of its blocks' member
   bundle ids must equal the sealed floor cell's `comparative.members[].bundle_id`
   set, every block's four members distinct, no bundle in two blocks. Refusal
   name: `floor_member_census_mismatch` (replaces
   `manifest_block_membership_mismatch`).
4. Contrast → floor cell resolution at close-out reuses the finalizer's own
   selector: extract the predicate at `analysis_manifest_v3.py:3312-3331`
   into one public function (`resolve_arm_floor_cells(manifest, floor)` or
   equivalent) called by BOTH the finalizer and `dominance_closeout`; no
   second implementation of the selector may exist (AST census).
5. The end-to-end row of the stage-1 suite uses a MINTED floor (the
   `freeze_mixed_estimator_v2_pinset` fixture path), not the hand-built one;
   the hand-built fixture may remain for unit rows only.
6. `_attach_replay_sidecar` (test injection at `:129-146`) is DELETED;
   fixtures finalize through `finalize_prospective_analysis_manifest_v3` with
   the sidecar path, and `validate_d165_closeout` gains
   `manifest_id == calculate_manifest_id(manifest)` (Sol F1, Opus (b),
   Fable Q2 — three seats, one finding).

## B. Stage-2 design

Convergence across all four seats: candidate (ii) — the finalized manifest
seals the sidecar as an identity-only attachment `evidence.dominance_replay_sidecar`
= {path, sha256, schema_version, sidecar_id}; (i) is impossible (closed
sidecar schema, mint runs before finalization, digest cycle); (iii) is
unread by any consumer. Sealing bytes without reading `cells[]` keeps the
D-168 outcome-blind fence (`analysis_manifest_v3.py:3624`).

RULED:
7. Pre-registration (split: terra/Opus "declare a fifth required row" vs
   Sol/Fable "optional role, `required_attachments` is inside frozen
   semantics"): BOTH halves are right and compose. The finalized validator
   admits `evidence` with four keys or four-plus-`dominance_replay_sidecar`;
   the prospective validator admits a fifth `required_attachments` row ONLY
   when every contrast's `floor_estimator_registration` carries
   `dominance_criterion`; finalization REQUIRES the sidecar iff the
   prospective manifest declares the row. Legacy four-row packs are
   byte-unchanged and still validate. The v5 generator declares the row in
   `prospective_finalization_required_attachments()` now, before v5 freezes;
   `dominance_criterion_registration()` bytes stay `1c0a4a11`.
8. Capture: `_ComparativeRecomputation` (`floor_mint_estimator.py:72`) and
   `V2CellRecomputation` (`:314`) carry the block inputs, block ids, member
   ids, bracket and bound out of `recompute_comparative_estimate` (`:465`).
   `floor_extraction.py`, `detection_floor.py`, `scripts/mint_floor_artifact.py`
   (signature-pinned) are NOT touched; the pins at `floor_mint_estimator.py:80-109`
   and `tests/test_detection_floor.py:1136-1145` are the confinement proof.
9. Emission happens ONCE, in `_mint_multi_cell_floor_artifact_active` after
   the bind pass (`mint_floor_artifact_generalized.py:4022`), never inside
   `recompute_comparative_estimate` (which runs twice per cell: gate `:2441`,
   bind `floor_mint_estimator.py:660`). The adapter records from both
   recomputations must be byte-equal or the mint refuses
   (`d165_replay_recomputation_divergence`).
10. Sole assembler: public `dominance_closeout.build_d165_replay_sidecar(...)`
    wrapping `d165_replay_blocks_from_mint_inputs`; absolute records via
    `_build_independent_record`; the builder self-validates. AST census test:
    the literal `"joulewise.d165_dominance_replay.v1"` and any dict literal
    carrying the block-record key set appear only in `dominance_closeout.py`;
    references to the adapter/builder outside it only in
    `floor_mint_estimator.py` and `mint_floor_artifact_generalized.py`.
11. Write: `write_outputs_exclusive` (`scripts/mint_floor_artifact.py:1963`)
    is NOT in `_CORE_SIGNATURES` but IS in a signature-pinned module; the
    third output is written from `mint_floor_artifact_generalized.py` with
    `output_core._exclusive_write` and rollback of floor + statement on
    failure, so `mint_floor_artifact.py` stays untouched. CLI: `--d165-replay-out`,
    required for any v2 mint whose spec has at least one common-mode
    comparative cell, refused otherwise.
12. Default-path cells (blind Fable risk 3): the sidecar carries
    `comparative.common_mode_replay` only for cells computed by the registered
    common-mode estimator; other cells carry `comparative.estimator: "default"`
    and no replay. The close-out refuses a D-165 verdict for any contrast
    whose resolved floor cell lacks a replay (`cell_not_common_mode`). The
    mixed fixture therefore remains mintable.
13. `sidecar_id = f"{floor.artifact_id}::d165-replay"`. No lineage field.
14. Byte identity: (a) TEST-ONLY first commit pins the sha256 of the floor
    file written by `test_common_mode_full_cli_path_writes_bound_exact_artifact`
    on the pre-change tree; (b) the emission commit keeps it green and adds
    the with/without-`--d165-replay-out` byte-equality test; (c) existing
    `SYNTHETIC_COMPONENT_SHA256S` untouched.

## C. Gate shape
Sol xhigh implements under the WRITE_SCOPE in the brief (union of the four
proposals minus the forbidden files). Refuters: terra xhigh (execution +
mutation over the census, the divergence refusal and the member-census
binding) and Opus 5 (contract lens over clauses 1-14). Because §A amends a
design that refuters 40b passed, a cold Fable instance + Opus refuter
adjudicate THIS RULING concurrently; a dissent stops the implementation.
