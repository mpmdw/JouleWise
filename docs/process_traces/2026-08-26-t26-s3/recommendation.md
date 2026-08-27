# Recommended implementation design

## A93 ruling: authentication stops depending on the constant

Do not refresh `CURRENT_FROZEN_RECEIPT_SHA256` in any existing or imminent
pack. Treat it as frozen compatibility metadata. Authentication must select an
explicit derivation mode from authenticated state, not from that constant.

Implementation functions/files:

1. `joulewise/arm_readiness_evidence.py::_recorded_generator_check`: accept an
   explicit invocation mode. For generators that expose the BooleanOptional
   flag, invoke `--check --no-preserve-current-frozen-bytes`; never rely on its
   default.
2. `joulewise/arm_readiness_evidence.py::_recorded_projected_pack_authentication`:
   apply the same explicit no-preserve rule to the anchored generator before
   the existing projection replay.
3. `joulewise/arm_readiness_evidence.py::_derive_pack_authentication`: AST-parse
   (never import/execute) the authenticated generator bytes and attach a named
   source check such as `frozen_receipt_constant_relation` with relation
   `matches_current|names_predecessor|absent|no_current_receipt` and
   `authentication_dependency: false`. Keep it in source `checks`, not in the
   exact six-key fact, so existing receipts remain valid.
4. `joulewise/arm_readiness.py` historical PACK_AUTH consumer described below:
   independently derive the same relation from current committed bytes and
   authenticated plan/freeze state during historical composition. A stale
   relation is observable but is not a refusal.
5. Tests: `tests/test_arm_readiness_evidence_packauth.py` and
   `tests/test_receipt_histsem.py`; no `configs/campaigns/` edits.

## A94 ruling: replay the recorded regeneration anchor

The existing receipt is stronger than the current echo path: it records an
exact pre-freeze `head_commit` and pack digest. Make that real derivation the
enforced meaning of `pack_generator_check_status=PASS`.

Implementation functions/files:

1. `joulewise/arm_readiness.py::_histsem_authenticate_legacy_item` and
   `verify_receipt_histsem_pack`: when the authenticated item kind is
   PACK_AUTHENTICATION, parse its bound source, require source/receipt
   `head_commit` and `pack_sha256` agreement, materialize that exact local-Git
   coordinate in a temporary tree, and run its pinned generator check.
2. Reuse `historical_pack_tree_sha256`, current K12 verification, exact
   receipt/source/freeze/plan bindings, and `_histsem_delta`; do not add a new
   pinset schema. Require the derivation coordinate to contain no current
   D-134 receipt. For legacy generators that lack the preserve option, AST
   must also prove no preserve branch/constant exists before a bare call is
   admitted. For modern anchors, require explicit no-preserve.
3. Retain `joulewise/arm_readiness_evidence.py::_recorded_projected_pack_authentication`
   for newly authored U11-projected packs. Its current composition is already
   the corresponding pre-projection derivation proof.
4. In `joulewise/arm_readiness.py:_authenticate_generic_evidence_item` and
   `_predicate_passes`, document/enforce that a current `echo_integrity` result
   cannot independently satisfy `pack_generator_check_status`. Do not change
   `_PREDICATE_CONTENT_REQUIREMENTS["desk.current_pack.v1"]`; old exact facts
   stay compatible because their historical source is now re-authenticated.
5. Tests: `tests/test_receipt_histsem.py`,
   `tests/test_arm_readiness_evidence_packauth.py`, and focused lifecycle cases
   in `tests/test_arm_readiness.py`. Schema fixtures in
   `tests/test_arm_readiness_schemas.py` should remain byte/shape unchanged.
   `scripts/build_v4_histsem_pinset.py` should need no semantic change; add a
   focused builder test only if the implementation exposes the derived mode in
   its returned diagnostics.

The materializer must use local Git only, run `python -I -B`, never import a
pack generator into the verifier, and clean its temporary tree. Missing/shallow
history is a governed refusal, consistent with the existing histsem contract.

## Defect-shaped regressions

1. **`test_preserve_authentication_refuses_canonical_committed_freeze_receipt_tamper_with_regenerated_sidecar`**
   — in a temporary committed tree, change a canonical field in the current
   freeze receipt and regenerate its GNU sidecar. Preserve/echo alone would
   otherwise replay the bytes. Full authentication must refuse on the
   plan-tree-to-receipt binding (`readiness_freeze_receipt_mismatch` or the
   existing precise equivalent). This mandatory mutation is already shown by
   `raw/mutations/freeze-receipt/`.
2. **`test_stale_current_frozen_receipt_constant_is_detected_but_not_an_authentication_dependency`**
   — construct a current frozen pack whose AST-derived constant names the
   predecessor receipt. Require relation `names_predecessor`, require
   `authentication_dependency == false`, and require success only through the
   authenticated historical/projected anchor. A code path that branches auth
   validity on the stale constant must fail the test.
3. **`test_ordinal1_recorded_derivation_anchor_replays_without_echo_capability`**
   — materialize each v1 source `head_commit`; assert no current freeze
   reference, no preserve mode/constant, generator rc=0, and recomputed pack
   digest equals the source/receipt coordinate.
4. **`test_preserve_echo_accepts_science_row_tamper_but_cannot_set_generator_pass`**
   — mutate and commit one science config. Assert raw preserve CLI rc=0, then
   assert the authentication classifier emits `echo_integrity` and refuses to
   use that result as regeneration evidence.
5. **`test_preserve_echo_accepts_plan_tree_semantic_tamper_but_histsem_composition_refuses`**
   — add a canonical plan-tree field and regenerate its sidecar. Assert raw
   preserve CLI rc=0; authenticated current K12/binding/delta must refuse.
6. **`test_recorded_anchor_replay_refuses_historical_science_mutation`**
   — change a generated science row at the derivation coordinate (or point the
   receipt at a commit containing that mutation). The no-preserve generator
   replay or K5 comparison must fail, proving independence from current echo.
7. **`test_recorded_anchor_replay_refuses_unresolvable_or_off_lineage_commit`**
   — mutate the source/receipt anchor to an absent or non-ancestor commit with
   correctly regenerated local sidecars. Require the existing
   `histsem_commit_unresolvable`/`histsem_commit_off_lineage` refusal.
8. **`test_projected_pack_authentication_uses_no_preserve_anchor_when_constant_is_stale`**
   — projected `_v4` fixture with a predecessor-naming constant. Assert the
   anchored generator command is explicit no-preserve, projection replay
   passes, and the stale diagnostic is present.
9. **`test_v4_prefreeze_authors_then_postfreeze_bare_refuses_without_invalidating_recorded_authentication`**
   — before receipt, author projected evidence successfully; after adding the
   plan-pinned freeze receipt, assert current bare CLI rc=1 while authenticated
   recorded-anchor reuse remains PASS. This pins the state transition A93
   actually exposes.
10. **`test_external_pinned_input_drift_is_checked_in_derivation_mode`** —
    mutate the pinned acceptance JSON at the derivation coordinate. Explicit
    no-preserve replay must refuse `pinned input drifted`; preserve echo may
    still return 0 but cannot authenticate.

## Expected test blast radius

Primary modules:

* `tests.test_arm_readiness_evidence_packauth`
* `tests.test_receipt_histsem`
* `tests.test_arm_readiness`
* `tests.test_arm_readiness_evidence`

Likely compatibility coverage because the three generator families are used as
fixtures:

* `tests.test_d117_floor_qwen25_1p5b_plan`
* `tests.test_d117_floor_qwen25_7b_plan`
* `tests.test_d117_decode_contrast_plan`
* `tests.test_d117_v3_family`

`tests.test_arm_readiness_schemas` and registry tests should remain unchanged
unless implementation accidentally changes the six-key fact/schema; such a
change is a design failure, not expected blast radius.

## `_v4` transaction effect

The `_v4` mint sequence is **not affected**. No pack generator, generated pack
byte, plan-tree schema, freeze-receipt schema, or runsheet order changes. §3.4
continues to author PACK_AUTH through the existing U11 projection anchor,
strengthened only by explicit no-preserve selection and a diagnostic source
check. §3.5 and §3.6 consume the same receipt schemas and bytes produced in the
ordinary transaction. The successor pinset then records the same historical
and current coordinates and makes the regeneration-anchor composition
available at pre-arm.

No re-mint is required. If implementation discovers that it cannot enforce the
recorded-anchor composition without changing pack or receipt schema bytes, it
must stop with a D-153 `lead_ruling`; this design does not presently require
that expansion.

