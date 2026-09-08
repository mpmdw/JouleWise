# CLAIM-NONISSUANCE-RECEIPT-01 — round-2 design specification

## Design verdict: NEEDS_RULING on the positive trigger

Bound revisions: worktree `f0a0201f`; locally present seam ref `a443f618`.
Fetch could not update the parent repository's `FETCH_HEAD`, so seam freshness
is unproved and every seam citation below names `a443f618` explicitly.

The round-1 catch of any post-manifest `AnalysisInputError` is withdrawn. It
would let malformed or forged evidence mint a paper-authorizing receipt, in
conflict with D-161's retained fail-closed rule for physics, evidence, and
pre-registration (`docs/decision_log.md:207`). Opus B1 is correct about that
defect but its two cure shapes still require an enumerated, non-integrity
production cause. None exists at this head:

- `AnalysisInputError` means invalid process input and no artifact
  (`joulewise/analysis_engine/inputs.py:231-232`); `analyze_claims` uses it for
  invalid manifest/floor/strict inputs
  (`joulewise/analysis_engine/__init__.py:1661-1665`). Those are evidence or
  pre-registration failures, so no member is eligible merely by assigning it a
  new `reason_code`.
- `not_estimable`, `not_resolvable`, and `unresolved` are already successful
  scientific outcomes in `claim_verdicts.v1`
  (`joulewise/analysis_engine/claims.py:22-30,326-375`). Reclassifying one as
  artifact non-issuance would violate the reviewed v1-preservation boundary.
- A crash, non-invocation, output conflict, failed write, invalid emitted v1,
  or unexpected exception proves no governed disposition and cannot issue.

Before implementation the magistrate must choose: (A) register a new pre-data,
producer-verifiable non-integrity stop and exact raise site; (B) make specified
evidence failures eligible by amending D-161; or (C) abandon the receipt and
keep bare absence `STOP_FILL`. Recommendation: **C unless a real A exists**. B
recreates the tampered-input path. A private exception without an independently
defined raise predicate is not a producer.

The remainder freezes the implementation contract conditional on A. The
magistrate need only supply `ELIGIBLE_CODE` and the one producer predicate; all
other design questions and Opus B2-B7 are closed here.

## Artifact and producer

The owner remains the production claim-gate close-out, implemented as
`joulewise.analysis_engine.nonissuance.close_out_claims`. Arm readiness cannot
attest post-collection close-out. Direct calls to `analyze_claims` remain pure
derivations and never mint this sibling artifact.

The close-out yields validated `claim_verdicts.v1` **or** validated
`claim_nonissuance_receipt.v1`, never both. It first admits every manifest,
floor, bundle, and strict-validator input through the existing path. Any
`AnalysisInputError`, `ClaimArtifactError`, I/O failure, unexpected exception,
or changed input returns rc 2/3 and writes neither. Only `ELIGIBLE_CODE`, raised
at its single ruled post-admission site, may enter the negative branch;
exception text is never parsed.

The receipt is strict UTF-8 canonical JSON plus one LF. Every object has exactly
the keys shown; arrays are order-significant, duplicate keys and non-finite
numbers refuse:

```json
{
  "campaign_manifest": {
    "file_sha256": "<64 lowercase hex>",
    "manifest_id": "<nonempty string>",
    "schema_version": "joulewise.analysis_manifest.v3.finalized"
  },
  "disposition": {
    "reason_code": "ELIGIBLE_CODE",
    "status": "not_issued"
  },
  "evaluation_basis": {
    "kind": "whole_window_evaluation_basis_sha256",
    "sha256": "<64 lowercase hex>"
  },
  "nonissuances": [
    {"contrast_id": "<finalized-manifest contrast_id>"}
  ],
  "producer": {
    "algorithm_version": "1",
    "closeout_contract_id": "claim_verdicts_or_nonissuance.v1",
    "implementation": "joulewise.analysis_engine"
  },
  "schema_version": "joulewise.claim_nonissuance_receipt.v1"
}
```

There is no self-asserted receipt ID and no nested `claim_verdicts.v1` schema
literal (Opus B6). The external identity is
`sha256(canonical_rendered_bytes)`, named only by the Git-anchored supply map.
`nonissuances` is nonempty, unique, and order-equal to
`finalized_manifest.contrasts[].contrast_id`; `ELIGIBLE_CODE` applies to the
whole close-out, never per caller-selected contrast. The basis path is now
confirmed: finalized-manifest construction writes
`evidence.whole_window_verdict.evaluation_basis_sha256`
(`joulewise/analysis_manifest_v3.py@a443f618:3814-3820,3939-3942`).

Under one same-directory lock, verdict and receipt destinations are distinct,
same-parent, outside inputs, and absent. After the eligible event, reopen and
revalidate all evidence; require unchanged manifest digest/ID/basis/contrast
census, floor, and strict-input census; validate and exclusively publish the
receipt. Conflict, lock loss, validation failure, or publication failure writes
nothing new. Receipt close-out may return rc 0 with distinct
`claim-nonissuance:` status; it is not a scientific verdict.

## Validator and custody-family subtype

`validate_claim_nonissuance_receipt(raw: bytes, *, frozen_manifest,
frozen_manifest_sha256) -> tuple[str, ...]` strict-parses, checks exact keys and
literals, validates the manifest, and joins digest/ID/basis/census. Its closed
codes are `claim_nonissuance_parse_invalid`,
`claim_nonissuance_schema_invalid`, `claim_nonissuance_producer_mismatch`,
`claim_nonissuance_manifest_mismatch`,
`claim_nonissuance_evaluation_basis_mismatch`,
`claim_nonissuance_contrast_census_mismatch`, and
`claim_nonissuance_reason_invalid`.

Keep the five public refs/results and `ClaimEvidenceRef == {role, runs_root}`.
Amend the claims family from one role tuple to a closed subtype table. Common
roles are `finalized_manifest`, `floor_artifact`; subtypes only add roles and
never remove a common role:

| Subtype selected by map `inputs` | Exact ordered role tuple |
|---|---|
| `issued` | `claim_verdicts`, `claim_side_bound`, `finalized_manifest`, `floor_artifact` |
| `not_issued` | `finalized_manifest`, `floor_artifact`, `claim_nonissuance_receipt` |

No `subtype` key is added to a public ref, map entry, inventory, or receipt. The
ordered map role tuple is the sole discriminator, preserving the exact map
entry keys (`paper_supply_custody.md`@`a443f618`:74-112). Inventory keys remain
`family,files,inventory_id,mode,schema_version`, each file row remains exactly
`authority,path,role,sha256`, and its row set must equal the **map-selected
subtype tuple plus `validator_receipt`**. This is the required amendment to the
currently fixed claims-family tuple and inventory rule (`:150-159,170-174`),
not an inventory- or receipt-authored discriminator (Opus B3).

For `not_issued`, replay the new validator and manifest/floor authentication.
The map-pinned floor remains mandatory though no v1 embeds it. Add the validator to
`_validator_source_census("claim_evidence")`. After replay, reopen inventory,
all three subtype inputs, and validator receipt through the same
`V2AuthenticationReadSession`. Only production mode with a registered governed
producer may set `issuance_authorized`; fixtures remain non-issuing. Missing or
unregistered production rows return `paper_custody_receipt_unissued`.

Measurement-time rows are produced by
`joulewise.paper_supply.register_claim_evidence_supply`, exposed as
`joulewise register-paper-supply --family claim_evidence`. It accepts paths but
**no digests**, replays validation, computes every digest, and emits one exact
row for lead review/commit. `close_out_claims` never edits the map; only the
later clean committed head authorizes consumption.

## Rendering and precedence

Gamma may render only from `VerifiedClaimEvidence` with
`issuance_authorized == true`. It joins each receipt contrast to the
map-pinned finalized manifest's `measurement_arm`; `decode` authorizes only
DS-32's byte-exact `not evaluated — required token-generation verdict absent`,
and the selected prefill contrast authorizes only PG-08's twin. No reason code,
number, gate result, path, or diagnostic is rendered.

The registered order at
`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:26`
is mandatory: evaluate authenticated before-comparison evidence first; if it
issues a stop, it wins and claim non-issuance is secondary. Only when no
before-comparison stop issues may this receipt select the DS-32/PG-08 absence
branch. There is no caller `precedence` input (Opus B5).

## Acceptance and counterfactuals

One end-to-end close-out test must prove: a ruled eligible event after complete
input admission publishes one canonical receipt and no v1; every invalid,
missing, forged, or changed manifest/floor/bundle instead publishes neither;
scientific null outcomes still publish only v1. A producer mutation changing
the eligible-event guard to `except AnalysisInputError` must turn this test red.

Extend the seam's auto-census test for **both claims subtypes** and every actual
read record (addenda 15/16; Opus B2):

1. raw mutation with map pins fixed -> exact
   `paper_custody_digest_mismatch`, mutated input role, zero rendered output;
2. full caller reseal of the validator receipt with its map pin fixed -> exact
   `paper_custody_digest_mismatch`, role `validator_receipt`, zero output;
3. replacement after replay and before reopen -> exact
   `paper_custody_input_changed`, replaced role, zero output.

Add a gamma test where authenticated before-comparison and claim-nonissuance
inputs coexist: the before-comparison sentence renders, receipt reason and
absence sentence do not. Signature/AST guards continue to ban public paths,
digests, bytes, mappings, receipts, subtype, and precedence parameters.

## Contract amendments and residual paper state

The implementation seat amends the claims ladder and v5 artifact flow to the
mutually exclusive close-out; the custody contract at `a443f618` lines 62,
74-112, 124-138, 150-159, 170-203, and 223-226 to the closed subtype/replay
rules above; and the `AnalysisInputError` comment to “no verdict artifact.” The
magistrate alone amends D-173; `docs/decision_log.md` stays outside the seat.

After code lands, **no production prose issues until the measurement-time
supply row is generated, reviewed, and committed**. Register these residuals:

- DS-32 (and PG-08) stays `STOP_FILL` for bare absence, every D-161 evidence
  failure, and any unregistered production role. Its earlier-stop branch still
  depends on `WHOLE-WINDOW-STOP-RECEIPT-01`.
- OR-01 stays `STOP_FILL` for claim non-issuance even after the fixed DS-32
  absence sentence becomes available: OR-01 requires an issued reason, while
  this design deliberately exposes no receipt code or total code-to-sentence
  map. Follow-on `CLAIM-NONISSUANCE-OR01-REASON-MAP-01` must register exact
  professor-facing bytes before any OR-01 consumer change (Opus B4).
- DS-28 through DS-31, DS-33, and PG-01 through PG-07 receive no numeric or gate
  authority from this receipt.

## Conditional implementation WRITE_SCOPE

After the positive trigger ruling and D-173 amendment, grant only:

```json
["joulewise/analysis_engine/nonissuance.py","joulewise/analysis_engine/__init__.py","joulewise/analysis_engine/inputs.py","joulewise/cli.py","joulewise/paper_custody.py","joulewise/paper_supply.py","joulewise/results_fill_gamma.py","configs/paper_supply/supply_map.json","docs/contracts/paper_supply_custody.md","docs/contracts/claims_ladder.md","docs/process/v5-artifact-flow.md","docs/paper/results-fill-registry.md","tests/test_claim_nonissuance.py","tests/test_analysis_integration.py","tests/test_paper_custody.py","tests/test_paper_supply.py","tests/test_results_fill_gamma.py"]
```

Real measured artifacts, production digest values, run/state reports, kernel
files, and `docs/decision_log.md` remain lead/measurement owned.
