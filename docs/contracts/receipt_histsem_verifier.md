# Receipt Historical-Semantics Verifier Contract

This document is the one normative home for `RECEIPT-HISTSEM-01`. Its
authority is the [final D-144 co-design ruling](../process_traces/2026-08-20-go-session/rh-ruling.md),
including its normative annexes, and the
[cold delta verdict](../process_traces/2026-08-20-go-session/rh-cold-verdict.md).
For gate-eligibility semantics on an absent-at-HEAD pinset, the adopted
rule-11 consult
(../process_traces/2026-08-20-go-session/t19-envelopes/rh-consult.md)
SUPERSEDES the ruling's original refusal wording; the ruling text is
preserved as custody.

## Governed identity and activation

The governed pinset is a closed, ordered, code-enumerated chain of versioned
artifacts:

1. `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`
2. `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json`

A pack is a histsem pack exactly when its immutable repository identity — the
pair `(pack_id, pack_path)` — is a member of the committed union. Receipt counts,
receipt filenames, evidence-ID prefixes, and other scanned pack contents do
not decide whether the gate engages. Consequently, adding, removing, or
renaming an unreferenced receipt cannot disengage verification for a governed
pack.

An unenumerated pinset-like file governs nothing. A duplicate `(pack_id,
pack_path)` anywhere across present members refuses `histsem_pinset_invalid`.
Each present member retains schema `joulewise.receipt_histsem_pinset.v1`; the
chain contract does not mutate that artifact schema.

The in-library gate runs before custody output in both entry points:

- `generate_arm_receipt` verifies the governed pack being armed.
- `generate_freeze_receipt` verifies the governed predecessor when operating
  in predecessor mode.

The pinset carries each pack's explicit historical and current digests,
historical commit, post-authoring delta, freeze binding, plan bindings, and
complete legacy-receipt inventory. Its bytes are SHA-256-pinned by
`tests/test_receipt_histsem.py`. There is no update, regenerate, repair, or
auto-reseal lane; a new governed value requires an explicit versioned change.

Eligibility loops over the enumerated chain using successful `git ls-tree HEAD
-- <member>` presence checks followed by `git show HEAD:<member>` reads. After
canonical validation and union/duplicate closure, membership of `(pack_id,
pack_path)` engages the gate and a membership miss returns normally. An
unambiguous result that an enumerated member does not exist in `HEAD` skips
that member; if all are absent, the library returns to ordinary readiness.
This preserves the rule-11-settled absence-of-governance answer and is not a
`histsem_pinset_absent` refusal. In that state the library must not inspect
receipt schemas, names, counts, or inventories. Any other failure to obtain a
HEAD member refuses, and any invalid present member refuses. The HEAD reads
prevent worktree deletion or mutation from disengaging a pack whose HEAD row
exists, and the gate verifies against those same HEAD-anchored rows. Committed
mutation/deletion remains owned by byte pins and changed-set controls.

## Coordinates and checks

The verifier has two coordinates, and they are not interchangeable.

| Coordinate | Governed checks |
|---|---|
| `HISTORICAL` (`head_commit`) | Pure-Git `ls-tree` plus `cat-file blob` recomputation under the existing `PACK_DIGEST_DOMAIN` framing; K5 comparison with `historical_pack_sha256`; receipt `head_commit`/`pack_sha256`; the pre-authoring invariant; ancestry to `HEAD`, with the lane-specific `origin/main` rule below. |
| `HEAD` | K12 comparison of the committed current pack tree with `current_pack_sha256`; receipt-to-sidecar-to-freeze-to-plan binding; mandatory `facts[].source_sha256` binding; exact pinned receipt inventory; predecessor binding. |

K7 compares `head_commit` to `HEAD`: there must be zero deletions, additions
must be confined to the four custody directories encoded in the library, and
modifications must be drawn only from the closed freeze-retarget set encoded
there. K5 and K12 are the load-bearing historical and current byte checks. K7
is layered delta-shape hardening and the bootstrap check used when a new
pinset row is minted; it is not the sole byte-integrity check.

The differential self-test over every governed pack mechanically requires
`historical_pack_tree_sha256(..., "HEAD")` to equal
`committed_pack_tree_sha256(...)`. This pins the framing without relying on a
prose reimplementation.

## Invocation lanes

There are two invocation lanes:

1. **CI-hard verification.** Run
   `python3 scripts/verify_receipt_histsem.py --repository-root . --require-published`
   in the full-history `test` job. The historical commit must be an ancestor
   of both `HEAD` and `origin/main`. The verifier must not be installed in a
   shallow checkout job.
2. **Pre-arm library verification.** The arm and predecessor-freeze entry
   points invoke the same verifier before writing custody artifacts. Ancestry
   to `HEAD` is hard; a historical commit not yet published to `origin/main`
   is advisory so a newly minted local family can cross the pre-arm gate.

Neither lane fetches, unshallows, repairs, or otherwise mutates Git history.
Missing or incomplete local history is a refusal that must be resolved by
supplying a governed full-history checkout outside the verifier.

## Refusal vocabulary

Historical-semantics refusals use the closed `histsem_*` vocabulary, disjoint
from `READINESS_REASON_CODES`:

| Code | Meaning |
|---|---|
| `histsem_binding_mismatch` | A current receipt, sidecar, freeze, plan, fact source, or predecessor binding differs. |
| `histsem_commit_off_lineage` | The historical commit is not an ancestor of `HEAD`. |
| `histsem_commit_unpublished` | The historical commit is not an ancestor of `origin/main`; hard in CI and advisory pre-arm. |
| `histsem_commit_unresolvable` | A well-formed historical commit cannot be resolved in a non-shallow local history. |
| `histsem_git_unavailable` | A required bounded local Git operation cannot be executed. |
| `histsem_historical_digest_mismatch` | Pure-Git historical recomputation differs from the governed historical digest or receipt coordinate. |
| `histsem_historical_tree_anomalous` | The historical tree contains malformed or inadmissible entries. |
| `histsem_historical_tree_not_pre_authoring` | The historical coordinate already contains custody artifacts. |
| `histsem_history_unavailable` | A required historical tree, blob, or delta cannot be read. |
| `histsem_history_shallow` | The checkout does not contain full history. |
| `histsem_pack_absent_at_commit` | The governed pack is absent at its historical coordinate. |
| `histsem_pinset_absent` | The worktree pinset is missing for a pack whose HEAD row engages the gate. An unambiguous absent-at-HEAD path returns to ordinary readiness instead (see Governed identity and activation). |
| `histsem_pinset_invalid` | The pinset is unreadable, noncanonical, malformed, or internally inconsistent. |
| `histsem_pinset_mismatch` | Current committed pack or receipt bytes differ from the governed pins. |
| `histsem_post_authoring_delta_unexpected` | The observed historical-to-HEAD delta violates or differs from the governed envelope. |
| `histsem_receipt_head_malformed` | A receipt's historical commit or pack digest coordinate is malformed. |

Both library boundaries catch `HistoricalSemanticsError` and return the
governed reason code; no bare exception may escape and no coincidental
downstream `readiness_*` refusal substitutes for a required histsem refusal.

## Archival location rule

The verifier is location-agnostic by design. It never compares a freeze
receipt's `pack_identity.pack_root` with the verifier's current working
directory or checkout root. The `_v3` family replays only at its separately
ruled pre-install coordinate in
`/Users/edr/JouleWise-measurement-20260818`; a refusal caused by replaying it
elsewhere is a location refusal, not evidence of pack corruption, and this
verifier does not add a `pack_root` equality check.

## `_v4` transaction sequencing

This verifier and its refusal vocabulary land before the `_v4` re-freeze.
After all three `freeze-0004` artifacts exist, and before Ed's exact-byte step
6, the `_v4` pinset rows are minted and checked against the transaction's
confirmation table. The successor pinset path is the pack-and-ordinal-exact 112th entry
in the whole-repository changed-set allowlist. Retrofitting the rows after the
transaction would recreate the missing-expected-value defect; a later family
gets its own exact entry, never a glob.

The successor class is digest-conditional on Ed's single step-6 confirmation
table. The table schema, custody rule, and acyclic two-consumer digest graph
have exactly one home in
[`d117_step6_confirmation_table.md`](d117_step6_confirmation_table.md). This
contract owns only the successor section's semantic replay; it does not
restate or fork the confirmation schema. The confirmation table is an
authenticator and therefore may never enter any allowlist.

## Truth boundary

This is DETECTABILITY, not integrity — the verifier does not stop a
history-rewriting in-process actor (that residual is a REGISTERED LIMITATION
under D-139 A1, which is why it is recorded rather than a gap); it raises
forgery cost from a 6-file commit to a history rewrite that breaks merge-base
ancestry against `origin/main` and contradicts the hand-published S5 digest
table. The paper must state this detectability boundary in those words and
must not claim that the mechanism establishes integrity against that actor.
