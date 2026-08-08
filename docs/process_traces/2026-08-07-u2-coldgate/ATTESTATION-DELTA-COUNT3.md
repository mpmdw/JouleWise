# Verdict: FAIL

**SAME-SIGNATURE QUESTION: YES.** An enrollment-level instance survives. This is **count 3** for “lineage/judgment attestation validated as well-formed, not as true” and therefore triggers the cold gate.

## Severity-tiered findings

### Critical — ledger-absent epoch attestation is accepted

The consult requires `epoch_catalog` membership to equal the distinct ledger epochs through cutoff ([ATTESTATION-CONSULT.md:68](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/docs/process_traces/2026-08-07-u2-coldgate/ATTESTATION-CONSULT.md:68)).

The implementation instead:

- Validates each catalog entry’s self-derived key against that same entry ([calibration_bracketing.py:1997](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1997)).
- Verifies that every ledger row resolves to one catalog entry, but never rejects unreferenced catalog entries ([calibration_bracketing.py:3593](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:3593)).

Executed failing scenario:

1. Built the authentic successor fixture.
2. Added a ledger-absent epoch with a correctly derived `epoch_4e3bf9a5f4fcd821` key.
3. Recomputed `derivation_sha256`, serialized artifact SHA, and registry artifact/derivation pins.
4. Standalone validation returned valid with no violations.
5. Full parent-aware registry loading accepted the forged active successor.
6. Ledger-residue verification produced `VerifiedAcceptance` with no violations.

This is plainly a false wire attestation accepted as true.

### High — enrollment is auto-generated and not verbatim to the ruled table

`ACCEPTANCE_ATTESTATION_FIELDS` is generated automatically from the same leaf sets used by `schema_leaf_patterns`; all verified entries receive one verifier that always returns `True` ([calibration_acceptance_attestation.py:247](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_acceptance_attestation.py:247), [calibration_acceptance_attestation.py:348](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_acceptance_attestation.py:348), [calibration_acceptance_attestation.py:395](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_acceptance_attestation.py:395)).

An in-memory schema-change probe showed that adding `future_authority_leaf` to the schema set automatically enrolled it as `VERIFIED / POLICY / S`, its verifier returned true, and schema/enrollment equality still passed. Therefore the claimed exact-set test does **not** force a new wire field through explicit classification and verifier design.

Several existing metadata rows also disagree with the consult:

| Field | Ruled authority/layer | Enrolled |
|---|---|---|
| `trigger_judgment.judged_under_*` | Parent, `S/R` | `POLICY`, `S` |
| `trigger_judgment.new_content_ids` | Parent/ledger, `S/R` | `POLICY`, `S` |
| Count source/boundary | Prior truth and parent boundary, including `R/B→L` obligations | `POLICY`, `S` |
| Parent operative decimal leaves | `S`, with equality also at `R` | `LEDGER,PARENT`, `S/B_TO_L` |
| `derivation_sha256` | `S`, exact registry equality at `R` | `POLICY`, `S` |

The generic routing responsible is at [calibration_acceptance_attestation.py:370](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_acceptance_attestation.py:370).

### High — 133-field forge coverage does not satisfy the regression contract

The loops do enumerate exactly 118 successor and 15 registry verified patterns, but:

- Three mutators are not same-type: `calendar_expiry`, genesis `parent_acceptance_id`, and genesis `parent_artifact_sha256` change from `null` to string ([calibration_acceptance_attestation.py:312](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_acceptance_attestation.py:312)).
- The 118-field successor loop recomputes only `derivation_sha256`; it does not serialize and update the artifact SHA and registry pins ([test_calibration_acceptance_successor.py:528](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:528)).
- It mutates the first existing scalar occurrence only, so it never tests false collection membership such as the surviving extra-epoch forgery.

The dedicated forged-trigger test does perform the required downstream re-pinning, but that does not repair the whole-class harness.

### Medium — static annotation-consumer guard is incomplete

`VerifiedAcceptance` correctly removes both annotations, and no current decision consumer was found. However, the static regression scans only two functions and checks for an AST variable named `issuance`, rather than forbidding a `"reason"` path read. A future `artifact["issuance"]["reason"]` access could pass the test ([test_calibration_acceptance_successor.py:443](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:443)).

## Per-charge disposition

| Charge | Result | Evidence |
|---|---|---|
| 1. Enrollment conformance | **FAIL** | Counts are correct: 120 successor patterns = 118 verified + 2 annotations; 15 registry; 133 verified total. Dynamic fixtures match. Decimal expansion is exactly 39 leaves; spot-checks matched derivation output (`0.995`, parent screen `0.010818`, maximum content ID, preflight `0.033558756679900`, cap `0.002463687165770351`). But source/layer metadata, explicit enrollment, and static-consumer contracts fail. |
| 2. Trigger math | **PASS** | Exact range/count recomputation, canonical order, both-recorded behavior, and exact result are implemented at [calibration_bracketing.py:1762](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1762). Identity/protocol/systematic cases refuse before issuance. The five-step forged-trigger regression rehashes all named pins and asserts `trigger_judgment_mismatch` at standalone and registry layers. |
| 3. Forge coverage | **FAIL** | Exact iteration counts and real ledger/temp-Git cases exist, but three forgeries change type, successor coverage omits full registry re-pinning, and collection-membership forgeries are absent. |
| 4. Class hunt | **FAIL — count 3** | Executed extra epoch-catalog forgery passes standalone, full registry, enrollment, and ledger-residue verification. |
| 5. Non-class closures | **PASS** | Fsync test proves staged-file-fsync `<` replace `<` destination-directory-fsync for both paths; named active-cardinality is asserted; relevant U2 test files contain no skip markers; tracked disposition/custody inputs are hash-pinned and absence fails; four missing operative fields reach evaluation and refuse `invalid_acceptance_arithmetic`. Repository-wide unrelated skips remain, including incoming-main tests, but the two consult-targeted skips are gone. |
| 6. Must-not-change | **PASS** | FIX-1 exact equality remains at standalone and independent registry layers. `derive_successor_decimal_derivation`, `_acceptance_arithmetic_valid`, and `_next_count_boundary` are byte-identical from `878ce9e` through final head. Issued SHA is `316113960c…8985`; registry remains one active genesis entry at cutoff 76; no v3 artifact exists. |
| Bench five-ID + integration | **PASS** | Exact IDs are `D-102,D-109,D-117,D-125,D-126`, all five index rows exist, and the new regression passes. Merge `a68682d` has only two overlapping paths, no conflict markers, and zero combined-resolution patch bytes; no conflict damage found. |

Checks performed: focused `110/110 OK`; canonical `2837 OK (skipped=90)`; 135-pattern/39-decimal census; full-rehash extra-epoch acceptance probe; same-type mutator audit; scoped skip grep; issued/config hashes; D-125 function byte comparison; `git diff --check`; merge-tree/combined-diff audit; final worktree clean. No files edited.