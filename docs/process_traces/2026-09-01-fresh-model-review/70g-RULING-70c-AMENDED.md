# 70g — RULING 70c AMENDED after cold-gate adjudication (70e cold Fable, 70f Opus)

Both adjudicators RATIFY §A (the stage-1 identity defect is real; cold Fable
shows it is worse than stated — cell keying fails before block ids are even
compared) and the stage-2 shape (candidate ii). Both independently refute the
ruling's bench premise (iv): `scripts/floor_mint_pinsets/schema_v2.json:333` is
the PINSET schema. Magistrate re-verification on `140ec4cc`: the sealed floor's
`cells[].comparative.blocks[]` carries `block_id`, positioned
`members[{position,bundle_id,bundle_sha256,config_sha256,metric_value_j}]` and
`delta_j` (`scripts/mint_floor_artifact.py:1450-1469`; `_CMP_KEYS` includes
`blocks`, `joulewise/detection_floor.py:1877-1889`), and
`cells[].provenance.comparative.bundle_ids` (`:1487`). Blind seat 70d risk 1
proposed binding by `comparative.blocks[].block_id`; the magistrate overrode it
on the misread — recorded against the magistrate in the council log.

70c stands except as amended below. Clause numbers refer to 70c.

## §A amendments (stage 1, lands on `feat/d165-dominance-closeout-core` before stage 2)

- **Clause 2 (amended):** sidecar blocks carry `block_id` (extraction-spec id)
  AND `members` — an object with exactly `A1, B1, B2, A2` → bundle id — AND
  `delta_j`. The adapter signature becomes
  `d165_replay_blocks_from_mint_inputs(block_ids, block_deltas_j, block_inputs, block_members)`;
  `block_members` is threaded from the authenticated extraction spec
  (`cell.blocks[].members`, `floor_mint_estimator.py:308-324`), never from
  `_CommonModeBlockInputs` (`floor_extraction.py:245-253`, untouched).
  `_raw_replay_block` (`dominance_closeout.py:320-332`) does NOT gain
  `members`: `replay_common_mode_dominance` re-replays from that projection;
  `members` is identity-only. Contract `:186-211` ("exactly the three values",
  "copies the six fields") and the block table `:148-156` are amended in the
  same commit; the worked sidecar digest at contract `:58` is re-pinned.
- **Clause 3 (replaced):** the close-out binds each sidecar block to the sealed
  floor cell's `comparative.blocks[]` by `block_id`, requiring exact positioned
  `members` equality (A1,B1,B2,A2 → bundle_id) and `delta_j` equality under
  `_close`; sidecar block count == floor `n_blocks`; no block id absent or
  duplicated on either side. Refusal name stays `floor_member_census_mismatch`.
  The union-of-sets formulation is withdrawn (position-blind; would admit an
  A1/B1 swap that flips the sign of `delta_j`). Contract `:228-235` (manifest
  `block_ids` census) is deleted and replaced by this paragraph.
- **Clause 4 (replaced):** no shared resolver — the finalizer's predicate
  (`analysis_manifest_v3.py:3312-3331`) consumes bundle-derived
  `expected_backend`/`expected_stack_sha` (`_floor_consumer_contexts`
  `:3185-3233`) that the close-out never has. Instead the finalizer RECORDS the
  resolved floor `cell_id` per arm as a new arm field `floor_cell_id`
  (`ARM_KEYS` `:230`), present iff the prospective manifest declares the
  sidecar attachment row (clause 7), so legacy finalized manifests validate
  byte-unchanged. Resolution is unique only for `exact_stack_only`
  (`:3332`); for a governed-transport or non-unique resolution the field is
  `null` and the close-out refuses with `floor_cell_unresolved` (distinct from
  `cell_not_common_mode`). The close-out re-checks the floor-side subset of the
  predicate against the sealed floor: `key.condition_family_id/sha` equal the
  arm's, `eligibility.claim_usable is True`, and
  `source_regime.stack_identity_sha256` equals the sha of the arm's
  `realized_stack_identity`. Pre-registered acceptance test: on the production
  fixture, that sha equals the finalizer's bundle-derived
  `expected_stack_sha` (if the two builders differ — `analysis_engine/inputs.py:2474`
  vs `build_stack_identity` — the session returns NEEDS_RULING with the two
  values; it does not paper over it).
- **Clause 5 (budgeted):** the minted mixed floor (`freeze_mixed_estimator_v2_pinset`,
  `tests/test_mint_floor_artifact_generalized.py:1451`) must satisfy
  `_authenticate_floor_dependencies` (`:3235-3331`) and `_floor_cell_map`'s
  exactly-four-cells (`dominance_closeout.py:1035`); the synthetic prospective
  manifest's selectors and transport groups are regenerated against the mixed
  pinset's cell ids. This is a fixture rebuild, not a swap; it is in scope.
- **Clause 6 (named):** `analysis_manifest_v3.calculate_manifest_id` (`:383`),
  a new import edge into `dominance_closeout.py` (the other two functions of
  that name, `analysis_manifest.py:222` and `analysis_engine/registry.py:491`,
  are not it).
- **Clause 12 (moved to stage 1, exact):** `comparative` admits exactly two key
  sets — `{independent, estimator}` with `estimator == "default"`, or
  `{independent, estimator, common_mode_replay}` with
  `estimator == "common_mode"`; `estimator` is required on every cell.
  `_COMPARATIVE_KEYS` (`dominance_closeout.py:68`) and contract rows
  `:110-151` are amended; schema version stays `.v1` (no production sidecar
  was ever emitted). Contract `:108` ("exactly the four floor cells") stays —
  cells remain exactly four; replay presence is per cell.
- **A2 limitation (contract text):** block `inputs` are trusted from the sole
  producer and replayed, not re-derived from bundles; the sidecar's physical
  correctness rests on clause 9 divergence + clause 14 byte identity (D-161:
  producer correctness, operator-only adversary).

## §B amendments (stage 2)

- **Clause 7 (mechanism):** `prospective_finalization_required_attachments()`
  (`:1206-1222`) gains an explicit optional-role argument; the registry
  constants `_REQUIRED_ATTACHMENT_SCHEMA_VERSIONS`/`_REQUIRED_ATTACHMENT_ROLES`
  are NOT widened (that would emit the row unconditionally). The v5
  generator's local literal (`generate_configs.py:121-140`, contrary to the
  `:2322-2326` comment) is replaced by the accessor call. The validator's
  `dominance_criterion` check is presence-only. `_FINALIZED_EVIDENCE_KEYS`
  (`:1134-1139`) admits four-or-five.
- **Clause 9 (placement):** `bind_v2_floor_artifact_evidence`
  (`floor_mint_estimator.py:588-602`) changes its return type to carry the
  per-cell recomputation record (four call sites incl.
  `tests:6530/7445` updated); the divergence check is per cell, and records
  accumulate keyed by cell id across the 4× bind loop.
- **Clause 11 (nits):** all three output paths are pre-checked before the
  first `_exclusive_write`; the CLI row's `events` assertion is updated so the
  third write is observed.

## Sequencing
Stage 1 (§A amended, clauses 1-6 + 12) is one Sol xhigh session with terra
xhigh execution refuter + Opus contract refuter, on a worktree stacked off
`feat/d165-dominance-closeout-core`; PR #254 is superseded by the stacked
branch. Stage 2 (clauses 7-11, 13, 14) starts only after stage 1's refuters
pass.
