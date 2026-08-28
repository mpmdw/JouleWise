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

The optional verifier/CLI pinset-path selector may select one member of this
same code-enumerated chain for a focused check; it is not an override lane. A
path outside the enumeration refuses `histsem_pinset_invalid`, even when its
bytes are an exact copy of an enumerated member.

The in-library gate runs before custody output in both entry points:

- `generate_arm_receipt` verifies the governed pack being armed.
- `generate_freeze_receipt` verifies the governed predecessor when operating
  in predecessor mode.

The pinset carries each pack's explicit historical and current digests,
historical commit, post-authoring delta, freeze binding, plan bindings, and
complete legacy-receipt inventory. Its bytes are SHA-256-pinned by
`tests/test_receipt_histsem.py`. D-161 permits one reviewed refresh lane for
the two **current-coordinate** fields only:
`scripts/refresh_receipt_histsem_pinset.py --refresh-row PACK_ID` re-derives
`current_pack_sha256` with `committed_pack_tree_sha256` and
`post_authoring_delta` with `_histsem_delta`, using the same code paths as the
verifier. It requires a clean pack directory, requires the row's historical
commit to be published on `origin/main`, and requires current `HEAD` to be
reachable from a remote-tracking ref. It also reproduces the historical tree
and digest before constructing a candidate, then requires that candidate to
pass the ordinary pack verifier before and after the canonical write; a
post-write refusal restores the original bytes.

The same lane's composable `--refresh-tool-sidecars` mode owns the exact GNU
sidecar rendering and the ruled set `build_family_marker.py`,
`verify_family_marker.py`, `build_v4_histsem_pinset.py`, and
`verify_receipt_histsem.py`. It refuses `histsem_binding_mismatch` if a governed
tool or its `.sha256` path is dirty and refuses `histsem_commit_unpublished` if
current `HEAD` is not reachable from a remote-tracking ref. After those checks,
it hashes each tool's committed `HEAD:scripts/<name>` blob (the clean-path check
makes those bytes equal to the worktree tool), diffs the old and regenerated
sidecar bytes, and writes only changed sidecars. It never writes a tool. The
family-marker sidecar test imports this lane's tuple and renderer: that test is
the staleness tripwire, and this mode is the reviewed regenerator.

The refresh script's own committed sidecar uses the same exported renderer but
is deliberately outside the CLI-owned tuple. A self-rewriting authenticator is
incompatible with the required dirty-tool and dirty-sidecar refusals inside one
reviewed change: the tool is dirty before its first commit, and its newly
written sidecar is dirty until a second commit. Its separate exact-byte
family-marker assertion therefore keeps it current in the same reviewed change
without weakening the CLI's fail-closed rule.

The lane refuses rather than changing `historical_pack_sha256`, `head_commit`,
`freeze_receipt`, `plan_sha256`, `plan_tree_sha256`, `pack_id`, `pack_path`,
`published_anchor`, `receipt_count`, or `receipts`. Dirty pack bytes,
unpublished coordinates, a noncanonical or absent pinset/row, a historical
digest mismatch, a historical tree that is not pre-authoring, an out-of-envelope
delta, or any current freeze/plan/receipt/predecessor binding mismatch is a
refusal with the verifier's closed `histsem_*` vocabulary; there is no override
flag and no partial write. `PINSET_SHA256` in
`tests/test_receipt_histsem.py` remains the exact-byte authenticator that the
reviewed refresh PR moves (optionally through `--write-test-pin`) alongside the
reviewable row diff. Historical-coordinate values remain immutable: changing
one still requires an explicit versioned governed change, and no refresh,
repair, or auto-reseal lane exists for them.

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

## Adopted A93 ruling: the frozen-receipt constant is not authority

**Adopted 2026-08-26.** This section is normative. A pack generator is the
plan-pinned Python program that creates or checks a campaign pack. The
authentication path is the code that selects that program's command, runs the
check, and returns PASS or REFUSE. That path MUST NOT read the presence, syntax,
value, extraction status, or recorded relation of
`CURRENT_FROZEN_RECEIPT_SHA256` when it selects the command or decides the
verdict.

The adopted choice is that `CURRENT_FROZEN_RECEIPT_SHA256` is **not refreshed
per generation; the authentication path stops depending on it**. Refreshing is
impossible, not merely undesirable. A successor generator is emitted before
the successor's own freeze receipt exists, so the SHA-256 value needed for the
constant does not yet exist. Editing the generator after that receipt is minted
would change the already-frozen pack bytes. The rejected refresh-per-generation
alternative is therefore circular: it requires the receipt digest before the
receipt can be made, then requires a pack-byte edit after the receipt has fixed
those bytes. It would also contradict D-153's new-family rule, under which each
later family receives new versioned custody artifacts rather than retargeting
an already-frozen family.

The constant is frozen compatibility metadata: an old, pack-owned value kept
because changing it would change frozen bytes. A total diagnostic extractor
parses it without raising and records
`authentication_dependency: false`. Nothing consults that diagnostic. The
extractor records `constant_extraction_status` as follows:

- `absent`: no top-level assignment exists;
- `readable`: exactly one literal lowercase SHA-256 exists;
- `duplicated`: more than one top-level assignment exists;
- `non_literal`: the one value is computed or otherwise cannot be read by
  `ast.literal_eval`;
- `malformed`: the declaration has no assigned value, or its literal is not a
  lowercase SHA-256; and
- `source_unreadable`: the bytes cannot be decoded as UTF-8 Python or parsed as
  Python syntax.

The recorded `relation` is `unreadable` for the last four failure statuses. For
`absent` it is `absent`. For `readable` it is `no_current_receipt` when the plan
names no current freeze receipt, `matches_current` when the value equals that
receipt's digest, `names_predecessor` only when it equals the predecessor
receipt's digest, and `unrelated` otherwise. These values are observations,
not verdict inputs.

Preserve capability is classified separately from constant extraction. A
preserve mechanism is generator behavior that can accept already-frozen bytes
instead of rebuilding them; for example, a branch controlled by
`preserve_current_frozen_bytes`. A generator that declares
`--preserve-current-frozen-bytes` with `argparse.BooleanOptionalAction` has an
explicit two-way selection, so authentication invokes
`--no-preserve-current-frozen-bytes`. A generator with a preserve mechanism but
without that explicit flag refuses because a bare invocation would leave the
choice implicit. Every flagless generator is denied by default. It can reach a
bare `--check` only when the SHA-256 of its exact bytes is a member of the
library's closed allowlist of reviewed ordinal-1 historical generators, after
which syntax inspection must also find no preserve mechanism. Allowlist
membership admits the blob to those later checks; it does not prove
regeneration, admit a rewrite with the same claimed behavior, or override the
preserve-mechanism refusal. The constant does not alter any of these decisions.

The ruling is pinned by
`tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_frozen_receipt_constant_variants_do_not_change_the_authentication_verdict`.
That regression holds one generator behavior and authentication context fixed,
varies the constant through absent, current, predecessor, unrelated, computed,
duplicated, and malformed forms, and requires an identical authentication
verdict with only diagnostic differences.

## Coordinates and checks

The verifier has two coordinates, and they are not interchangeable.
A **custody coordinate** is the current committed pack state being protected:
one Git commit identifies the tree and one pack digest identifies the exact
pack bytes in that tree. In this gate, `HEAD` and `current_pack_sha256` identify
that current custody state.

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

For every authenticated `PACK_AUTHENTICATION` item, the verifier also parses
the bound source and requires its `head_commit` and `pack_sha256` to equal the
receipt's values. A derivation coordinate is that exact Git commit plus pack
digest; for example, the receipt's `head_commit` identifies the committed tree
and its `pack_sha256` identifies the pack bytes inside that tree. The verifier
materializes the derivation coordinate from local Git in a temporary checkout
and executes the plan-pinned generator through `python -I -B`. Regeneration
means that the generator rebuilds and checks its declared outputs from pinned
inputs; the verifier selects it with `--no-preserve-current-frozen-bytes` when
the explicit flag exists. A flagless generator runs bare only when its exact
SHA-256 is in the closed reviewed historical allowlist and the independent
syntax scan finds no preserve mechanism.

A **tautology** is a comparison that cannot independently detect the change
under review because both sides come from the same already-changed bytes. For a
concrete echo, suppose a committed `plan_tree.json` is mutated. A preserve-mode
`--check` reads that mutated `plan_tree.json` as its saved output, re-emits the
same bytes as its candidate, and compares the candidate with the same mutated
file; both sides match, so the mutation is accepted. Regeneration instead
rebuilds `plan_tree.json` from `calibration_plan.json` and the pinned external
artifacts without using the committed `plan_tree.json` as its output source.
The rebuilt candidate then differs from the mutated committed file, so
`--check` notices the mutation.

A U11-projected derivation coordinate is a post-generation pack state produced
by the identity-pin projection procedure; concretely, that procedure rewrites
`plan_tree.json`, `plan_tree.sha256`, and `producer_contract.json` and adds a
projection receipt plus its sidecar. Its projection anchor is the earlier
reviewed Git commit named by that receipt, where the pre-projection pack still
exists. The evidence author regenerates the pack at that anchor, then performs
a replay, meaning it applies the projection receipt's recorded write set and
compares every resulting byte with the U11-projected coordinate. A bare check
at the post-projection coordinate is not equivalent. The temporary checkout is
removed after verification, including after refusal. Temporary-workspace
allocation and cleanup failures yield `histsem_history_unavailable`. Failure to
execute the bounded local Git clone that materializes the workspace yields
`histsem_git_unavailable`; if the clone succeeds but the named commit cannot be
checked out, the coordinate yields `histsem_commit_unresolvable`. The generator
is never imported into the verifier process, and neither receipt nor pinset
schema gains a field.

Normative honest limit: `pack_generator_check_status: PASS` proves that the
plan-pinned generator regenerated the authenticated historical pack coordinate
(composed with the receipted projection replay when that coordinate is
U11-projected); it does not prove that current HEAD pack bytes were regenerated,
and a preserve-mode echo—a check that accepts already-frozen bytes without
rebuilding them—cannot establish or renew this claim.

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
| `histsem_history_unavailable` | A required historical tree, blob, or delta cannot be read, or the temporary historical workspace cannot be created or cleaned up. |
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
