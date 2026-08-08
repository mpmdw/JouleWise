# Attestation-binding consult — response of record (2026-08-08)

Sol xhigh (fast tier), read-only. Charge: ESCALATION-ATTESTATION.md
beside this file (class at count 2: new_content_ids fixed, triggers
forged-acceptable).

**MAGISTRATE ADOPTION (Fable, 2026-08-08): ADOPTED IN FULL.** One
declared attestation-verification pass over an enrollment registry
(ACCEPTANCE_ATTESTATION_FIELDS keyed by schema leaf patterns; every
leaf VERIFIED-with-recomputation or NON_AUTHORITATIVE_ANNOTATION;
exact-set equality against the wire schemas; unenrolled fields fail
closed); the trigger set is RECOMPUTED as an exact set (both trigger
kinds recordable simultaneously; ordered-subset predicate retired);
field-by-field rulings per the tables incl. decision_ids gaining
D-125 (it owns the emitted arithmetic); two annotations
(issuance.reason, disposing_decision_id seam) excluded from the
VerifiedAcceptance decision object with a static consumer test;
parameterized forge-mutator regressions per verified field; the four
non-class rulings (fsync partial-order trace, named-violation
cardinality check, no /private/tmp skips — construct in-test, missing
runtime fields reach the runtime guard via .get-until-validated).
Must-not-change list binds; no successor issuance during rework.

---

Verdict: adopt one declared attestation-verification pass and fail closed on unenrolled schema fields. A third site-by-site patch is insufficient. The current trigger forgery must fail both standalone validation and parent-aware registry loading.

Layer notation:

- `S` — `_valid_acceptance_bound(child, parent=parent)`, using child plus authenticated parent bytes.
- `R` — `load_calibration_acceptance_registry`, with every registry artifact and parent available.
- `B→L` — build from an authenticated ledger/custody snapshot, followed by the same mandatory ledger-consistency residue before any runtime decision.
- `A` — non-authoritative annotation, excluded from the verified decision object.

## Field-by-field ruling: successor artifact

| Field path(s) | Ruling and exact authenticated comparison | Layer / standalone obligation |
|---|---|---|
| `schema_version` | Exact policy literal `joulewise.calibration_acceptance_bound.v3`. | `S` |
| `acceptance_id` | Exact `d079_calibration_acceptance_v3_s{ledger_cutoff.sequence}_{ledger_cutoff.head_digest[:16]}`. | `S` |
| `decision_ids` | Exact canonical decision set. It must include **D-125**, because D-125 owns the emitted lineage-envelope arithmetic; the current constant omits it. Recommended exact order: `D-102,D-109,D-117,D-125,D-126`. Each ID must resolve in the decision log in a build test. | `S`; decision-log resolution at build/test time. |
| `artifact_role`; `issuance.status`; `issuance.claim_eligible` | Exact coherent triple `issued / issued / true`. Actual issuance is true only when the bytes are present in the committed registry; a dry-run object is merely proposed issued bytes. | Shape/policy at `S`; truth at committed `R`. |
| `issuance.reason` | **A**. Current production code only checks nonempty text; no probe, arithmetic, freshness, basis, or claim decision consumes it. | Mark `NON_AUTHORITATIVE_ANNOTATION`; omit from the verified decision object. |
| `lineage.generation` | Parent generation + 1; genesis parent implies generation 2. Must also equal the registry entry generation. | `S` and `R`. |
| `lineage.root_acceptance_id` | Parent’s root ID if parent is v3, otherwise parent’s `acceptance_id`. | `S`; currently underbound. |
| `lineage.parent_acceptance_id` | Exact parent `acceptance_id`. | `S`, cross-checked at `R`. |
| `lineage.parent_artifact_sha256` | SHA-256 of exact parent file bytes, not canonicalized parsed JSON. | `R`; if `S` has only a parsed mapping, it can only check internal duplicated IDs and must report this rule deferred. |
| `lineage.parent_derivation_sha256` | Exact parent `derivation_sha256`. | `S` and `R`. |
| `lineage.parent_ledger_cutoff.{sequence,head_digest,ledger_schema}` | Exact parent artifact cutoff and registry parent cutoff. | `S` and `R`. |
| `trigger_judgment.judged_under_acceptance_id`; `.judged_under_artifact_sha256` | Exact parent ID and exact parent raw-byte SHA; also equal the corresponding lineage fields. | `S/R`. |
| `trigger_judgment.new_content_ids` | Preserve FIX-1 exactly: `set(new_content_ids) == child_basis_ids − parent_basis_ids == absorbed post-parent-cutoff basis IDs`, with a sorted, duplicate-free wire representation. Registry validation must retain its independent equality. | `S` and `R`. |
| `trigger_judgment.triggers` | Recompute the exact mathematical set described below. The JSON array is only canonical serialization; “nonempty ordered subset” is not sufficient. | `S`, transitively authenticated by `B→L`. |
| `trigger_judgment.result` | Exact `successor_required` iff the recomputed trigger set is nonempty. A successor artifact with no recomputed trigger fails. | `S`. |
| `ledger_cutoff.{sequence,head_digest,ledger_schema}` | Exact authenticated terminal snapshot head; `role` is the exact policy literal. | Truth at `B→L`. `S` must still require equality with `prior_observation_set.cutoff`, ID derivation, all recorded sequences ≤ cutoff, and parent cutoff < child cutoff. |
| `identity_epoch.{os_build,hardware_model,power_policy,sampling_interval_ms,estimator_revision,pulse_protocol_id}` | Exact parent identity epoch and exact observed identity passed to the builder. | `S` against parent; `B→L` against the authenticated observation/probe context. |
| `prospective_rederivation.calendar_expiry`; `.trigger_observation_rule`; `.triggers` | Exact policy constants. The mandatory-trigger array is an exact canonical set, not a permissive subset. | `S`. |
| `prospective_rederivation.protocol_sha256` | Recompute from the authenticated protocol-v3 file selected by `PROTOCOL_ID`. | `S` with repository source. |
| `prospective_rederivation.estimator_code_sha256.<four fixed paths>` | Exact key set `ESTIMATOR_CODE_PATHS`; compare each digest to current file bytes. | `S`. A new estimator path changes the schema leaf set and therefore requires enrollment. |
| `count_trigger.source_trigger_count` | Count exactly all content-distinct observations in the child prior set whose disposition is `valid` and whose catalogued epoch equals `identity_epoch`. Never derive it from corpus `n`. | `S`, with prior truth established by `B→L`. |
| `count_trigger.next_boundary` | `_next_count_boundary(parent_boundary, source_trigger_count, rule)` exactly. | `S/R`. |
| `count_trigger.rule`; `.universe_rule` | Exact supported policy literals, frozen per registry entry. | `S/R`. |
| `derivation_corpus.selection`; `.n` | Exact D-125 basis rule; `n == len(members) >= 19`. | `S`. |
| `derivation_corpus.members[*].content_id` | Recompute from the member’s manifest/evidence hash pair; exact member set is parent basis plus FIX-1 additions. | Local binding at `S`; source truth at `B→L`. |
| Member `attempt_id`, `finalization_sequence`, `receipt_digest`, `custody_locator`, `b_fiducial_s`, `manifest_sha256`, `instrument_evidence_sha256` | Exact equality to the corresponding prior-set representative attempt. Ledger fields compare to the exact receipt; custody hashes compare to actual governed bytes at build. | Mirroring at `S`; truth at `B→L`. Standalone minimum: valid shape, sorted/unique IDs, sequence ≤ cutoff, and exact member↔prior equality. |
| `prior_observation_set.cutoff` | Exact child cutoff triplet. | `S`; truth at `B→L`. |
| `content_identity_method` | Exact policy literal; independently recompute every row’s `content_id` from its attempt hash pair. | `S`. |
| `epoch_catalog.active_epoch` | Exact artifact `identity_epoch`. | `S`. |
| Other `epoch_catalog` entries | Each key must be exactly `epoch_{sha256(canonical_epoch)[:16]}`; values have exactly the six identity fields and are unique. Catalog membership must equal the distinct ledger epochs through cutoff. | Key/value consistency at `S`; complete membership and row association at `B→L`. |
| Observation `content_id`, `epoch_id`, `disposition` | Content ID recomputed from all aliases’ primary hashes; epoch and disposition compare exactly to grouped ledger observations. Disposition is decision-bearing for trigger count, systematic refusal, and basis selection. | Internal projections at `S`; truth at `B→L`. |
| `disposing_decision_id` | **A for the present schema seam.** Current code merely copies/regex-validates it; `_prior_set_matches_import_cutoff_prefix` excludes it, and no decision path consumes it. | Mark `NON_AUTHORITATIVE_ANNOTATION`. When the first D-126 disposition is consumed, reclassify it as verified against an authoritative decision-by-content-ID source in the same change. |
| `representative_attempt_id` | Exact first attempt in finalization-sequence order. | `S`. |
| Attempt `attempt_id`, `finalization_sequence`, `receipt_digest`, `observation_kind`, `custody_locator`, `exact_bound_lexeme_s`, `manifest_sha256`, `instrument_evidence_sha256` | Exact projection of the authenticated receipt. Aliases sharing a content ID must agree on classification, epoch, primary hashes, and exact bound. | Truth at `B→L`. Standalone owes schema, ordering, uniqueness, content-ID recomputation, alias coherence, and valid rows having a bound. |
| `noncontent_attempts[*].attempt_id`, `closure_sequence`, `receipt_digest`, `disposition`, `custody_locator` | Exact `_governed_noncontent_rows` projection from terminal no-content and governed-unused-slot receipts. | `B→L`. Standalone owes allowed dispositions, uniqueness, ordering, and cutoff bounds. |
| Entire `decimal_derivation` | Require exact mapping equality with `derive_successor_decimal_derivation(corpus.members, parent_operatives=actual_parent_operatives)`. This verifies every nested leaf: numeric semantics; quantile algorithm/precision/probabilities/rounding/pin; lineage-envelope rules, quantum and parent operatives; all source statistics and extremum IDs; presentation value and label; rounding metadata and values; and every ratified operative/rule/count. | `S`; actual parent operative equality also at `R`. |
| `derivation_sha256` | Canonical SHA-256 of every other artifact field. This is integrity only, never authority. | `S`, with exact equality to registry entry at `R`. |

The two annotations must be identified in the declared field registry, not merely by comments. Decision code should receive a `VerifiedAcceptance` view that excludes annotation fields. A static consumer test should reject raw reads of annotated paths outside serialization, validation, and presentation code; future consumption then necessarily requires reclassification.

## Trigger ruling

For parent `P` and child `C`:

```text
new_rows = C.prior_observations whose content_id is absent from P.prior_observations

range_trigger =
    any new row is valid,
        row epoch == P.identity_epoch,
        and representative exact_bound lies strictly outside
            [min(P.derivation_corpus), max(P.derivation_corpus)]

count_trigger =
    count(all content-distinct valid rows in C at P.identity_epoch)
        >= P's recorded next count boundary
```

The expected trigger set is exactly:

```text
[
  range trigger, if true,
  count-boundary trigger, if true,
]
```

in that canonical serialization order.

Both can be true simultaneously and both must then be recorded. Neither trigger dominates or suppresses the other. The current ordered-subset predicate is therefore wrong; an array remains acceptable only as the canonical encoding of an exact set.

Identity changes, protocol/code changes, and systematic-invalid observations are refusal outcomes before automatic successor issuance. They are not alternate `trigger_judgment.triggers` values for an issued successor.

## Registry-lineage fields

| Registry field | Exact verification |
|---|---|
| `schema_version`, `authority` | Exact policy constants. |
| `entries` membership/order | One consecutive generation chain, canonically generation-sorted, one root, no cycle, no fork, no duplicate ID or artifact path. |
| Entry `acceptance_id` | Exact artifact ID. |
| `artifact_path` | Safe repository-relative path naming an existing regular file; v3 filename exactly encodes artifact cutoff sequence and digest prefix. |
| `artifact_sha256` | SHA-256 of exact artifact bytes. |
| `derivation_sha256`, `artifact_schema`, `ledger_cutoff` | Exact artifact fields. |
| `generation` | Parent generation + 1 and exact artifact lineage generation. |
| `parent_acceptance_id`, `parent_artifact_sha256` | Exact parent entry and parent raw bytes; root uses null/null. |
| `count_boundary_rule` | Exact artifact rule; next boundary independently recomputed from the actual parent boundary and source trigger count. |
| `active` | Exactly one active entry and it is exactly the unique chain leaf. Both facts remain checked. |
| Committed authority | With `require_committed=True`, registry and every artifact byte sequence equal their Git `HEAD` bytes. |

## Validation shape and exact-set enrollment contract

Create one declarative registry such as `ACCEPTANCE_ATTESTATION_FIELDS`, keyed by normalized schema leaf patterns—e.g. `prior_observation_set.observations[*].attempts[*].receipt_digest`. Each entry must declare:

```text
classification: VERIFIED | NON_AUTHORITATIVE_ANNOTATION
source: POLICY | PARENT | REGISTRY_BYTES | LEDGER | CUSTODY | REPO_CODE
layer: S | R | B_TO_L
verifier_id
stable_failure_code
forge_mutator            # verified fields only
consumer_policy          # annotations only
```

Then:

1. `_valid_acceptance_bound` runs the same pass for all `S` rules and requires parent context for v3. It must not call a v3 artifact fully valid using only self-contained hashes.
2. Registry loading runs the `R` rules in generation order.
3. Building requires every non-annotation rule, including ledger/custody rules, to be verified.
4. Runtime claim paths accept only `VerifiedAcceptance`, produced after the ledger residue. A bare transport-authenticated registry mapping is not claim-authorizing.
5. Every violation has a stable code. Rejection alone is insufficient because overlapping invariants can mask deletion of a particular rule.

Exact-set test contract:

```text
schema_leaf_patterns(SUCCESSOR_WIRE_SCHEMA)
  ∪ schema_leaf_patterns(REGISTRY_WIRE_SCHEMA)
==
set(ACCEPTANCE_ATTESTATION_FIELDS)
```

Additionally:

- no duplicate enrollment;
- every field is exactly one of verified or annotation;
- every verified field has a callable verifier and forge mutator;
- every annotation has no verifier, is absent from `VerifiedAcceptance`, and has no decision consumer;
- a verification run over a maximally populated fixture must visit every concrete leaf exactly once;
- unknown runtime keys still fail schema validation;
- changing the wire schema without enrolling the new leaf fails the exact-set test.

## Regression contract

Permanent forged-trigger regression:

1. Build a real range-only successor with source trigger count below the parent boundary.
2. Replace `trigger_judgment.triggers` with count-boundary-only.
3. Recompute `derivation_sha256`, serialized artifact SHA, and registry artifact/derivation pins.
4. Require standalone failure with `trigger_judgment_mismatch`.
5. Require parent-aware registry refusal with the corresponding registry code.

Also retain truth-table cases for range-only, count-only, both, and neither.

For the whole class, parameterize over every `VERIFIED` field specification:

- Apply its same-type, schema-valid forgery.
- Recompute every attacker-controlled/self-authored digest and downstream pin.
- Do not mutate the authentic parent, ledger snapshot, custody bytes, repository code, or governing policy source.
- Assert the field’s named verifier code is emitted, even if another invariant also rejects.
- Ledger-derived forgeries must be tested through the ledger residue.
- Registry-authority forgeries use a temporary Git repository where committed-state behavior matters.

This combination means a new schema field cannot ship without enrollment, and an enrolled verified field cannot lack a discriminating forgery test.

## Four non-class rework rulings

1. **fsync ordering:** record an event trace, distinguishing regular-file and directory `fsync` using `fstat`. For each destination assert the partial order `staged-file fsync < os.replace < parent-directory fsync`. In the current two-file case, the filtered trace should establish both replace→directory-fsync relationships. Retain count assertions as deletion guards, but counts are not ordering evidence.

2. **Exactly one active:** the present condition is logically overlapped by “active IDs equal the unique leaf,” so no black-box boolean fixture can isolate it. Have the declared registry pass emit named violations and assert `registry_active_cardinality_invalid` is present for the two-active fixture, while retaining and separately asserting the active-leaf violation. Deleting the one-active rule then changes the exact violation set without weakening the leaf check.

3. **No `/private/tmp` custody dependencies:** remove both skip decorators. Use the tracked issuance disposition table as repo-relative input and construct the canonical receipt chain/pin inside the test’s temporary repository; the receipt-forgery and cadence tests do not require live custody files. Missing or hash-mismatched tracked input must fail, never skip. The tracked custody manifest alone is insufficient because its members point outside a fresh checkout.

4. **Missing runtime fields:** preserve the standalone rejection, then patch the authenticated loader boundary to return each malformed artifact and execute evaluation. Move the runtime operative extraction/guard before the first direct `["bracket_screen_s"]` access and use `.get` until validation completes. Parameterize missing screen, ceiling, cap, and preflight screen; each must return `invalid_acceptance_arithmetic`, with no allowance minted and no exception.

Also remove the trailing whitespace in `ROUND2-DELTA.md`; it is the remaining `git diff --check` failure.

## Must not change

- FIX-1’s exact equality at both standalone and registry layers.
- D-125 arithmetic: two-universe separation, lineage-monotone 95%/99% envelopes, `1e-18` half-even comparator quantization, strict `screen < ceiling`, unclamped `cap = ceiling − screen`, observed-maximum preflight screen, and n≥19.
- The issued D-079 artifact bytes or SHA-256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`.
- The genesis registry pin/cutoff or publication semantics. The fsync item is a test-strengthening requirement, not evidence that current publication order is wrong.
- No successor issuance during this rework.

Checks performed: exact HEAD `878ce9e`; governing D-125/D-126 and remand record inspected from Git history; schema, builder, loader, probe, runtime, and tests traced; focused suites `98/98 OK`; issued artifact hash unchanged; `git diff --check e5cf244..878ce9e` fails only on the recorded trailing whitespace; worktree status unchanged; no files edited. The optional Fable peer-consult tool was unavailable, so no peer result was consumed.