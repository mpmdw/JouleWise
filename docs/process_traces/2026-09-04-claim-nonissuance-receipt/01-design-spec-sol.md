# CLAIM-NONISSUANCE-RECEIPT-01 — Sol design specification

## Decision

The **analysis engine's production claim-gate close-out** produces the artifact.
Arm readiness is pre-collection authority and cannot attest that post-collection
claim evaluation reached terminal non-issuance (`joulewise/arm_readiness.py:1-5`). A bare
missing `claim_verdicts` file, a process crash, an uninvoked command, or a caller
statement remains no evidence and therefore `STOP_FILL`/structured refusal.

Source mismatch: the prompt's `joulewise/claims.py` does not exist; the owner is
`joulewise/analysis_engine/claims.py`.

The close-out has two mutually exclusive results: existing
`joulewise.claim_verdicts.v1`, or one `joulewise.claim_nonissuance_receipt.v1`
covering the finalized manifest's ordered contrast census.

This is a sibling negative artifact, never v2, a v1 field, or a scientific
verdict. Scientific negative/null outcomes
(`not_estimable`, `not_resolvable`, `unresolved`) continue to issue inside v1;
the evaluator already owns those outcomes (`joulewise/analysis_engine/claims.py:22-30,326-375`).

## Exact wire

Strict UTF-8 JSON (no duplicate keys or non-finite numbers), with these exact
keys and types:

```json
{
  "schema_version": "joulewise.claim_nonissuance_receipt.v1",
  "claim_nonissuance_receipt_id": "cnr-<64 lowercase hex>",
  "producer": {
    "implementation": "joulewise.analysis_engine",
    "algorithm_version": "1",
    "closeout_contract_id": "claim_verdicts_or_nonissuance.v1"
  },
  "campaign_manifest": {
    "schema_version": "joulewise.analysis_manifest.v3.finalized",
    "manifest_id": "<nonempty string>",
    "file_sha256": "<64 lowercase hex>"
  },
  "evaluation_basis": {
    "kind": "whole_window_evaluation_basis_sha256",
    "sha256": "<64 lowercase hex>"
  },
  "claim_verdicts": {
    "schema_version": "joulewise.claim_verdicts.v1",
    "status": "not_issued"
  },
  "nonissuances": [
    {
      "contrast_id": "<exact finalized-manifest contrast_id>",
      "reason_code": "analysis_inputs_refused"
    }
  ]
}
```

`nonissuances` is nonempty, unique by `contrast_id`, and order-equal to
`finalized_manifest.contrasts[].contrast_id`; any census/order/reason difference
refuses. V1 deliberately has one reason:
`analysis_inputs_refused` means the manifest was admitted but the claim engine's
typed invalid-process-input boundary prevented any v1 artifact from being
finalized. No exception text, path, timestamp, phase label, caller digest, or
free-text explanation enters the receipt. More granular causes wait for a
structured `AnalysisInputError.reason_code` contract and schema amendment;
parsing today's messages is forbidden.

Authentication fields are the finalized-manifest ID/file digest, the
whole-window evaluation-basis digest copied from
`manifest.evidence.whole_window_verdict.evaluation_basis_sha256`, and the exact
contrast census. The receipt does not self-authorize: its rendered-byte digest,
custody-inventory membership, producer receipt, clean-Git supply-map binding,
and fresh validator replay independently authorize consumption under addendum
16 (`docs/process_traces/2026-09-04-paper-i/16-magistrate-rulings-addendum-5.md:5-8`).

Content addressing uses
`"cnr-" + sha256(canonical_json(receipt without claim_nonissuance_receipt_id))`.
Canonical JSON is UTF-8, sorted keys, compact separators, `ensure_ascii=False`,
`allow_nan=False`. Disk is that canonical object including the ID plus LF. The
supply map pins `sha256(rendered_bytes)`, not the `cnr-` body hash.

## Producer and trigger

Add `close_out_claims(...)` beside `analyze_claims` in
`joulewise/analysis_engine/__init__.py`. The exact production call site is
`joulewise/cli.py:_cmd_analyze_claims`: replace the call currently at
`joulewise/cli.py:2009-2019`; direct library calls to `analyze_claims` remain
pure derivations and cannot mint receipts.

The CLI adds required `--nonissuance-output`; both targets must be distinct,
same-parent, outside inputs, and absent under one directory lock:

1. Fully validate a **finalized v3** manifest; retain raw SHA-256, ID, ordered
   contrast IDs, and basis digest. Any other manifest cannot issue a receipt.
2. Run `analyze_claims(..., output_path=None)`. On return, finalize/validate and
   exclusively publish v1; no receipt is written.
3. Catch only post-step-1 `AnalysisInputError`; reopen/revalidate the manifest,
   require digest/ID/basis/census unchanged, then exclusively publish the
   validated receipt. This is the sole trigger.
4. `ClaimArtifactError`, unexpected exceptions, output/lock failures, manifest
   changes, pre-step-1 failures, or existing targets publish nothing. Existing
   receipt plus verdict is an append-only conflict, never a preference rule.

A published receipt is a successful **close-out** (rc 0 and distinct
`claim-nonissuance:` status), not a successful verdict. Publication failure
preserves rc 2/3. This narrows the current `AnalysisInputError` statement of
"no artifact" (`joulewise/analysis_engine/inputs.py:231-232`) without changing
`analyze_claims`' rule that invalid inputs raise while scientific negative/null
outcomes are returned (`joulewise/analysis_engine/__init__.py:1661-1665`).

## Validator and refusal codes

New owner: `joulewise/analysis_engine/nonissuance.py`. Public replay function:
`validate_claim_nonissuance_receipt(raw: bytes, *, frozen_manifest,
frozen_manifest_sha256) -> tuple[str, ...]`. It strict-parses exact bytes,
recomputes the ID, checks static producer/disposition values, independently
validates the finalized manifest, then enforces all manifest/basis/census joins.
It returns only this closed namespace:

- `claim_nonissuance_parse_invalid`
- `claim_nonissuance_schema_invalid`
- `claim_nonissuance_identity_mismatch`
- `claim_nonissuance_producer_mismatch`
- `claim_nonissuance_manifest_mismatch`
- `claim_nonissuance_evaluation_basis_mismatch`
- `claim_nonissuance_contrast_census_mismatch`
- `claim_nonissuance_reason_invalid`

## `claim_evidence` custody-family read

Do not add a sixth paper family or a sixth verified output. Extend the existing
`ClaimEvidenceRef -> VerifiedClaimEvidence` family with two closed input
variants:

- `issued`: current ordered roles `claim_verdicts`, `claim_side_bound`,
  `finalized_manifest`, `floor_artifact`;
- `not_issued`: ordered roles `claim_nonissuance_receipt`,
  `finalized_manifest`.

`ClaimEvidenceRef` stays exactly `{role, runs_root}`. The Git-anchored map selects
the variant; callers pass no discriminator, binding, receipt, or value. Inventory
and generic custody-validator receipt remain mandatory. Both role sets,
duplicates, or neither refuse as `paper_custody_evidence_ambiguous` or
`paper_custody_receipt_unissued`.

For `not_issued`, `open_paper_input` uses a fresh
`V2AuthenticationReadSession`, replays against the independently map-pinned
manifest, checks the custody receipt, reopens every file, and returns the frozen
`VerifiedClaimEvidence` with `disposition == "not_issued"`. Its validator-source
census includes the new validator. This preserves ruling 15's five-family/five-
type boundary and addendum 16's role-only caller boundary.

The gamma supplier joins each receipt row to the authenticated manifest's
`measurement_arm`, not a receipt/caller phase. Only `decode` authorizes DS-32's
byte-exact `not evaluated — required token-generation verdict absent`; only the
selected prefill row authorizes PG-08's prompt-processing twin
(`docs/paper/results-fill-registry.md:885,894`). All
numeric/gate fields remain unissued, not literal `STOP_FILL` fill values, and no
receipt reason code is rendered. A missing file without this verified branch
still yields structured refusal.

## ONE acceptance test

`tests/test_paper_custody.py::test_claim_nonissuance_is_producer_owned_and_custody_bound`
is one end-to-end test with two arms:

1. Control: a valid finalized-v3 fixture reaches the close-out trigger through
   a real missing-floor `AnalysisInputError`; assert one receipt, no v1, clean
   validator replay, exact manifest/basis/contrast bindings, a verified
   `not_issued` claim-family value, and only the exact DS-32/PG-08 absence text.
2. Counterfactual: alter/re-content-address the receipt and write a
   caller-authored inventory/validator receipt while leaving the clean-Git map
   unchanged. `open_paper_input` must raise exact
   `paper_custody_digest_mismatch`, return zero rendered values, and never reach
   a caller-selected path. This is the required proof; schema self-consistency
   alone is not acceptance.

## Deliberately not decided

- No actual prefill length, live contrast ID, receipt bytes/digest, production
  supply-map row, or custody locator: all come from the finalized `_v5` manifest.
- No verdict, direction, floor, bound, estimate, claim level, or paper branch.
- No cause-specific public reason beyond `analysis_inputs_refused`; no exception
  text mapping.
- No whole-window-stop receipt, arm-readiness change, claim-verdict v2, or
  relaxation of v1.
- No claim that non-invocation, crash, deletion, or an output-write failure is
  authenticated non-issuance.

## Conflicts and required amendments

1. **Decision gate.** Ruling 15 closes claims to v1 + sidecar and five types
   (`docs/process_traces/2026-09-04-paper-i/15-magistrate-ruling-custody-seam.md:5-8`). The variant changes that wire while preserving the counts. Amend D-173
   before implementation. At this base D-173 and its contract are absent;
   in-flight head `2e3349e1` installs them provisionally.
2. **Claims ladder.** Current engine-linked authority is exclusively
   `claim_verdicts.v1` (`docs/contracts/claims_ladder.md:21-30`). Add the negative
   receipt as a negative dialect authorizing only registered absence prose,
   never a claim level.
3. **Artifact flow.** L10-C currently treats every absent verdict as failure and
   the claim gate names only a v1 output (`docs/process/v5-artifact-flow.md:21-24`).
   Amend it to the mutually exclusive close-out and distinguish governed
   non-issuance from bare absence.
4. **In-flight custody contract.** At `2e3349e1`, claims have one fixed issued
   census (`docs/contracts/paper_supply_custody.md:62,150-159,223-226`). Amend
   that census to the two variants above; preserve role-only ingress and
   independent map authority.
5. **Producer API comment.** `AnalysisInputError` currently promises no artifact
   (`joulewise/analysis_engine/inputs.py:231-232`); qualify it as no verdict and
   point to the production close-out's governed negative artifact.

No conflict exists with addendum 07's v1 preservation
(`docs/process_traces/2026-09-04-paper-i/07-magistrate-rulings-addendum.md:3-7`):
the receipt is not a verdict and never enters v1. The DS-32/PG-08 registry rows
already require governed issued absence, so their text is preserved. Process
note: addendum 07 says the mission is queued, but neither `TASK_QUEUE.md` nor
`docs/process/state_kernel.json` contains its row at this head; the direct
WRITE_SCOPE prompt authorizes this design only, not implementation.

## Implementation-seat WRITE_SCOPE

Prerequisite: lead lands the D-173 amendment/ruling first. Then grant exactly:

```json
[
  "joulewise/analysis_engine/nonissuance.py",
  "joulewise/analysis_engine/__init__.py",
  "joulewise/analysis_engine/inputs.py",
  "joulewise/cli.py",
  "joulewise/paper_custody.py",
  "joulewise/results_fill_gamma.py",
  "configs/paper_supply/supply_map.json",
  "docs/contracts/paper_supply_custody.md",
  "docs/contracts/claims_ladder.md",
  "docs/process/v5-artifact-flow.md",
  "docs/paper/results-fill-registry.md",
  "tests/test_claim_nonissuance.py",
  "tests/test_analysis_integration.py",
  "tests/test_paper_custody.py",
  "tests/test_results_fill_gamma.py"
]
```

`docs/decision_log.md`, state/kernel files, run reports, real custody, measured
artifacts, and any live production supply-map values remain lead/measurement
owned and are intentionally outside that seat.
