# 70b — Opus 5 contract-lens seat, D165-SIDECAR-EMIT-01 design consult (three-seat rule)

Seat: Opus 5 (Agent, read-only) over `feat/d165-dominance-closeout-core` @ `140ec4cc`; same brief as Sol 70 / terra 71. Verbatim final report follows.

## CONTRACT-LENS seat — `D165-SIDECAR-EMIT-01` design consult

All paths under `/Users/edr/code/JouleWise-wt-closeout`. I disagree with the brief's Q2 framing (candidate (ii) is not a candidate — it is already the written contract) and with an implicit assumption in Q6 (the mint call site is *not* in `floor_extraction.py`'s numeric path).

### Q1 — Call site, authentication, registration point
- Mint-side call: `joulewise/floor_mint_estimator.py:545` inside `recompute_comparative_estimate` (def `:465`). The extraction-side call is `joulewise/floor_extraction.py:2766` in `extract_comparative_cell`. `tests/test_detection_floor.py:1136-1145` pins that caller list to exactly those two `(file, owner)` pairs.
- Chain to CLI: `:545` ← `scripts/mint_floor_artifact_generalized.py:2441` (`_v2_gate_postcollection`) **and** `joulewise/floor_mint_estimator.py:660` (`bind_v2_floor_artifact_evidence`) → both converge in `_mint_multi_cell_floor_artifact_active` (`mint_floor_artifact_generalized.py:3889`, calls at `:3937` and `:3989`) ← `mint_multi_cell_floor_artifact` `:3843` ← `main` `:4067`, argparse `:4031`. **The estimate is recomputed twice per mint run** (gate + bind) — emission must not sit inside `recompute_comparative_estimate`.
- Authenticated: inputs yes (pinset sha, git tree state, `_authenticate_v2_inputs` `:3483`, `bind_v2_floor_artifact_evidence` `:3989`, revalidation `:4018`); **no receipt is issued**. `_artifact_sha256` (`:1844`) is in-memory only. The mint touches no manifest.
- Second-output registration point already exists: `write_outputs_exclusive(artifact, floor_path, statement_path)` (`mint_floor_artifact_generalized.py:4025` → `scripts/mint_floor_artifact.py:1963-1989`, O_EXCL via `_exclusive_write` `:1939`) already writes **two** files (floor + single-count statement). Crucially, `write_outputs_exclusive` is **absent from `_CORE_SIGNATURES`** (`mint_floor_artifact_generalized.py:141-194`), so a third output there breaks no pin; `mint_floor_artifact` **is** pinned (`:163-172`, with the standing note `:193-195`) and must not gain a parameter.

### Q2 — Hash binding: (ii), and it is already law
Candidate (ii) is the frozen stage-1 contract, not an open option: `docs/contracts/d165_dominance_closeout.md:215-234` mandates `evidence.dominance_replay_sidecar` with exactly `path|sha256|schema_version|sidecar_id`, and this branch already enforces it (`joulewise/dominance_closeout.py:1163-1202`, refusals `manifest_lacks_replay_sidecar` / `replay_sidecar_digest_mismatch` / `replay_sidecar_identity_mismatch`, contract `:376-381`). Candidate (i) **contradicts** the frozen sidecar schema — top-level keys are exactly `schema_version|sidecar_id|cells` (contract `:102-108`; `validate_d165_replay_sidecar` rejects extra keys, `:178-181`) — there is no `lineage` slot, and Q3 makes it physically impossible. Candidate (iii) adds a fourth file no consumer reads. Stage 1 additionally already expects the floor seal: `_manifest_floor_artifact_digest_error` (`dominance_closeout.py:1205-1226`) compares raw floor bytes to `evidence.aggregate_floor_artifact.sha256`.
Against the D-168 outcome-blind fence: sealing the sidecar is identity-only. `_authenticate_finalization_inputs`'s return (`analysis_manifest_v3.py:3624-3655`) records only path/sha256/schema_version/identity per role. A fifth entry of the same shape reads no ratio, no `passes`, no branch — **no fence violation**.

### Q3 — Ordering
Floor artifact is written **before** finalization: finalization *reads* it (`analysis_manifest_v3.py:3575-3578`, digest at `:3651`, param `aggregate_floor_artifact_path` `:3816`/`:3862`). The mint imports no manifest module. So the sidecar can never carry the finalized manifest's sha or `manifest_id`; lineage runs manifest → sidecar, one direction. But the sidecar's `block_id` values must equal the manifest's (contract `:151`, enforced set-equal at `dominance_closeout.py:1285`), and those IDs are frozen **prospectively** (`configs/campaigns/*/analysis_manifest_v3.json`, `contrasts[].block_ids` + `members[].block_id`) — so the mint reads block IDs from the *prospective* manifest, which is outcome-free and available at mint time.

### Q4 — Byte-identity proof
`install_synthetic_finalization_fixture` (`tests/test_analysis_finalizer.py:208`) is the wrong fixture: its floor is synthetic and never passes through the mint. Use the mint's own harness, `tests/test_mint_floor_artifact_generalized.py`, and assert **both**: (a) a literal digest pin — `hashlib.sha256(floor_path.read_bytes()).hexdigest() == "<pinned>"`, the same device as `tests/test_d165_dominance_closeout.py:1146-1149`; and (b) in one test, run the mint twice into two temp dirs with `--replay-sidecar-out` absent then present, `assertEqual(floor_a.read_bytes(), floor_b.read_bytes())` and `assertEqual(statement_a, statement_b)`. (a) survives fixture drift; (b) proves the *emission* is the neutral variable.

### Q5 — Adapter exclusivity
Extend the existing AST governed-caller census at `tests/test_detection_floor.py:1091-1145` (precedent also `tests/test_arm_readiness_evidence_author.py:157-160`): add `d165_replay_blocks_from_mint_inputs` to its `calls` dict and pin the expected owner list to exactly one emitter function; plus a string census asserting the literal `"joulewise.d165_dominance_replay.v1"` appears under `joulewise/` and `scripts/` only in `dominance_closeout.py` and the emitter. Failure it catches: a future renderer or repair script hand-builds a block dict with the schema string, bypassing `split_common_mode_block_width`, so `derived_split` drifts silently and only the replay recheck stands between it and a published claim.

### Q6 — Confinement
`joulewise/floor_extraction.py` need not be touched at all: `_CommonModeBlockInputs` records are already constructed in the *mint* module (`floor_mint_estimator.py:527-543`) and merely discarded by `_ComparativeRecomputation` (`:558-564`). The edit is to *widen the return record*, not the numeric path. Confinement proof: (1) `git diff --stat` shows no `floor_extraction.py`; (2) `tests/test_detection_floor.py:1136-1145` passes unchanged; (3) the Q4 golden.

### (a) Pre-registration — must the prospective manifest declare it? **Yes, conditionally.**
Contract text decides it. `evidence` is **not** in the semantic projection; `finalization_contract.required_attachments` **is** (`_prospective_semantics` `:1587-1595`, `_finalized_semantics` `:1677-1685`). So `required_attachments` is the only place in the frozen prospective bytes that can say "a fifth file is owed", and it is hash-sealed by `frozen_semantics_sha256`; `evidence` is derived at finalization and sealed by nothing pre-registered.

An auditor reading only the prospective manifest *can* see `contrasts[].floor_estimator_registration.dominance_criterion` (semantics-projected at `:1649`; generator `configs/campaigns/d117_contrast_v5/generate_configs.py:570-578`). But that registers a **criterion**, not a **deliverable**. With no declaration, a finalization that silently omits the sidecar is byte-indistinguishable from one that never owed it — the audit fails open, exactly what D-168's fail-closed posture forbids for pre-registration. "Finalization requires the sidecar iff the registration is present" is a *code* rule, not a manifest-checkable one, and code is not pre-registered.

Two hard corollaries the ruling does not name — **neither option avoids editing the finalizer**:
1. `_FINALIZED_EVIDENCE_KEYS` (`:1134-1139`) is enforced **exactly** at `:4029-4038`. I ran it: a fifth key yields `analysis_manifest_finalized_invalid: manifest.evidence: unrecognized key(s): dominance_replay_sidecar`, and the validator returns immediately.
2. `_build_finalized_manifest` builds `evidence` from `sorted(_REQUIRED_ATTACHMENT_ROLES)` (`:3751-3754`), and `validate_finalized_…` re-derives and demands `expected == value` (`:4095-4103`). A hand-added key fails that too.

So the finalizer must gain a `dominance_replay_sidecar_path` parameter either way. Given that, declaring the role costs almost nothing extra and buys the auditor the check.

**Do it conditionally, not globally.** `roles != _REQUIRED_ATTACHMENT_ROLES` (`:2755`) and `len(attachments) != 4` (`:2716`) are exact; flipping the global constant would retro-invalidate any pack frozen with four roles and change its `frozen_semantics_sha256` — and `finalize_…` refuses when finalized semantics ≠ frozen prospective semantics (`:3756-3761`). Introduce `_CONDITIONAL_ATTACHMENT_ROLES = {"dominance_replay_sidecar": REPLAY_SCHEMA_VERSION}`, admitted-and-required iff every contrast's `floor_estimator_registration` carries `dominance_criterion`; then `len` becomes 4-or-5 and the role comparison becomes `expected_roles_for(value)`. Cost today is zero: the four committed prospective manifests carry **no** `finalization_contract` at all (verified), and `configs/campaigns/d117_contrast_v5/` holds only `generate_configs.py` — v5's manifest is not yet generated or frozen. Amend `prospective_finalization_required_attachments()` in both `analysis_manifest_v3.py:1206-1222` and the v5 generator `:121-161` now, before v5 freezes; after freeze this becomes impossible without a re-freeze.

### (b) The test's injection — **inconsistent, and stage 1 does not catch it**
`tests/test_d165_dominance_closeout.py:129-145` mutates the manifest **after** `finalize_prospective_analysis_manifest_v3` returns: it overwrites `evidence.aggregate_floor_artifact.sha256` and adds `evidence.dominance_replay_sidecar`, without recomputing `manifest_id`. `calculate_manifest_id` (`analysis_manifest_v3.py:383-386`) hashes the canonical body minus `manifest_id`, so the injected bytes are no longer content-derived. Executed proof: `pre-inject id ok: True` / `post-inject id ok: False`. The authoritative validator would refuse twice — `:4131-4136` `analysis_manifest_finalized_invalid: finalized manifest identity is not content-derived`, and (reached first) `:4029-4038` on the unrecognized evidence key.

`validate_d165_closeout` does **not** catch it: `_source_precondition_errors` (`dominance_closeout.py:1309-1312`) only checks `manifest_id` is a nonempty string, and `dominance_closeout.py` never imports `analysis_manifest_v3` (no `validate_finalized_analysis_manifest_v3` call anywhere in the module).

**Consequence.** Every stage-1 green test on this branch runs against a finalized manifest that the production finalizer can neither emit nor accept. The `# injected pending D165-SIDECAR-EMIT-01` comment (`:138`) is honest about intent but understates the debt: stage 1 has no evidence that a *real* finalized manifest can carry this attachment, because none can today. Two consequences for stage 2: (i) the mint stream cannot land without the finalizer amendment — they are one contract change, not two streams; (ii) once the finalizer emits the fifth attachment, `_attach_replay_sidecar` must be **deleted**, not patched, and `_production_finalized_manifest()` must call the finalizer with the sidecar path — otherwise the injection permanently masks a real finalization defect. I would also add to `validate_d165_closeout` the one missing check the contract already implies (`:320` "identity"): `manifest_id == calculate_manifest_id(manifest)`, guarded by a local import to avoid the cycle.

### Q7 — Unnamed risks, ranked
**R1 (blocker). Block-ID set equality vs. admitted blocks.** `_manifest_block_membership_error` (`dominance_closeout.py:1273-1286`) demands the sidecar block set **equal** `contrasts[].block_ids`. The mint replays only *admitted* blocks (`floor_extraction.py:2789` `excluded_slots`; `floor_mint_estimator.py:527` iterates `spec_cell["blocks"]`). One excluded or replaced block → `manifest_block_membership_mismatch` → neither branch, permanently, with no diagnostic distinguishing "block excluded" from "forged sidecar". **R2. `block_id` does not exist in the mint's namespace** — `grep block_id joulewise/floor_mint_estimator.py` returns nothing; the mint holds bundle/run IDs. The mapping must be threaded in from the prospective manifest, a new mint input the ruling never budgets. **R3. Double emission** — `recompute_comparative_estimate` runs twice per mint (`mint_floor_artifact_generalized.py:2441` and `floor_mint_estimator.py:660`); an emission hook at the estimate would either write twice (O_EXCL failure) or write the gate-pass copy. **R4. Absolute cells have no `common_mode_replay`** but the contract requires four sidecar cells covering both absolute and comparative components (`:110-133`); the mint's absolute path never calls the common-mode estimator, so absolute records must be assembled from the floor artifact, not from a replay — a second, unsanctioned construction path unless it goes through `_build_independent_record`. **R5. Append-only namespace** — `_write_append_only` (`analysis_manifest_v3.py:3767-3776`) refuses a differing re-finalization, so any already-written finalized manifest can never gain the attachment; the v5 finalization must be first-run-correct.

### Recommended design (12 lines)
1. `_ComparativeRecomputation` gains `block_inputs` and `block_ids` (mint-module edit only; `floor_extraction.py` untouched).
2. `mint_multi_cell_floor_artifact` accepts `--prospective-manifest` (block-ID map, outcome-free) and `--replay-sidecar-out`.
3. New `joulewise/dominance_closeout.build_d165_replay_sidecar(...)` — the sole assembler, wrapping `d165_replay_blocks_from_mint_inputs`; absolute records via `_build_independent_record`.
4. Emit **once**, in `_mint_multi_cell_floor_artifact_active` after the bind pass — never inside `recompute_comparative_estimate`.
5. `write_outputs_exclusive` gains an optional third path with the same O_EXCL + rollback semantics (not signature-pinned).
6. R1: refuse at the mint if admitted ≠ prospective block set, with a named mint refusal, rather than deferring to `manifest_block_membership_mismatch`.
7. `analysis_manifest_v3`: `_CONDITIONAL_ATTACHMENT_ROLES`, conditional prospective role check, `_FINALIZED_EVIDENCE_KEYS` + `_build_finalized_manifest` fifth role, `_authenticate_finalization_inputs` fifth attachment (identity/digest only).
8. `scripts/finalize_analysis_manifest.py`: `--dominance-replay-sidecar`.
9. v5 generator: fifth row in `prospective_finalization_required_attachments()` — **before** v5 freezes.
10. Delete `_attach_replay_sidecar`; `_production_finalized_manifest()` finalizes with the real sidecar.
11. Add `manifest_id == calculate_manifest_id(manifest)` to `validate_d165_closeout`.
12. Tests: floor-bytes golden + before/after; extended AST caller census; conditional-role prospective/finalized matrix.

### Proposed WRITE_SCOPE
```json
[
  "joulewise/dominance_closeout.py",
  "joulewise/floor_mint_estimator.py",
  "joulewise/analysis_manifest_v3.py",
  "scripts/mint_floor_artifact.py",
  "scripts/mint_floor_artifact_generalized.py",
  "scripts/finalize_analysis_manifest.py",
  "configs/campaigns/d117_contrast_v5/generate_configs.py",
  "docs/contracts/d165_dominance_closeout.md",
  "tests/test_d165_dominance_closeout.py",
  "tests/test_mint_floor_artifact_generalized.py",
  "tests/test_analysis_finalizer.py",
  "tests/test_analysis_manifest_v3.py",
  "tests/test_detection_floor.py",
  "tests/test_d117_contrast_v5_pack.py"
]
```
Must **not** be touched: `joulewise/floor_extraction.py`, `joulewise/detection_floor.py`, `scripts/floor_mint_pinsets/*`, `_CORE_SIGNATURES` in `mint_floor_artifact_generalized.py:141-194`, `dominance_criterion_registration()` bytes (pinned `1c0a4a11…`, `tests/test_d165_dominance_closeout.py:1148`), and any `runs*/` corpus.
