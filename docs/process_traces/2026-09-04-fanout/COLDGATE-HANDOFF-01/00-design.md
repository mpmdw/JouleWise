# Sealed-byte cold-judge handoff: scoped design

Status: transport choice needs a magistrate ruling. The immutable snapshot
mechanism is implemented and testable without choosing or invoking a judge.

Authority: the `COLDGATE-HANDOFF-01` row in
`docs/process/state_kernel.json`, and question 2 plus the handoff regressions
in `docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md`. The
standing constraint in
`docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md` remains in force: a
validator PASS must not convene a cold judge until this handoff is complete.

## Forcing problem

The validator currently proves only what it read at validation time. A later
reader can see different bytes if a pathname is replaced or if another file
descriptor overwrites the same file. Keeping a file descriptor open does not
solve the second case. Rechecking a pathname immediately before launch also
does not solve it, because replacement can occur between the check and the
transport's read.

The safe boundary is therefore an immutable snapshot: ordinary Python
`bytes`, which cannot be changed after creation. The validator must calculate
each SHA-256 digest—a standard fingerprint of byte content—over that snapshot,
and the runner must construct the judge request from the same snapshot without
reading any source pathname again.

The remaining design question is how the actual judge transport represents and
acknowledges those bytes. The cited consult explicitly leaves that choice open.

## Options requiring a ruling

### Option A — canonical request bytes on standard input (recommended)

The runner creates one canonical UTF-8 JSON request. Packet, charter, and
exhibits are base64-encoded so every source byte has one reversible textual
representation. The runner sends those exact request bytes to a narrowly
specified launcher on standard input. The launcher returns a request or session
identity and the SHA-256 digest it observed for the request bytes. The runner
refuses unless that returned digest equals its own digest, then records both the
identity and digest in a runner receipt.

This is the smallest interface that makes the byte-to-request boundary
observable in a test. Its limitation is practical: the chosen judge launcher
must support an input channel whose exact bytes and returned identity can be
measured. No such launcher is yet named by authority.

### Option B — immutable attachment files

The runner writes snapshots into a newly created staging directory and asks the
judge transport to attach those files. This resembles current operator
practice, but ordinary files are not sealed storage. Permissions do not prevent
all same-user mutation, and pathname attachment can restore the very race this
row must remove. This option should be rejected unless the platform supplies a
genuinely sealed object and an independently observed attachment digest.

### Option C — provider-native attachment application programming interface

The runner uploads the snapshots as byte arrays through a provider interface
and records the provider's object and request identities. This can be sound if
the provider documents that the uploaded bytes are preserved and returns a
digest over them. It couples the contract to a provider and needs a separate
adapter for every judge surface. It is preferable only when the provider's
receipt is stronger than the standard-input acknowledgement in option A.

## Recommendation

Adopt option A as the transport-neutral contract, then rule the first concrete
launcher adapter separately. Require one call with the exact canonical request
bytes; an acknowledgement containing a nonempty request or session identity;
an independently observed request-byte SHA-256; refusal on missing, malformed,
or unequal acknowledgement fields; and a runner receipt binding the validator
receipt, request digest, source digests, and judge identity. The runner must
never serialize source pathnames beyond the basename and manifest-relative
names already permitted by the validator receipt.

Do not set `judge_handoff_bound` to true in the validator receipt. That receipt
describes validation only. The new runner receipt owns the later delivery claim.

## Worked example

Suppose the accepted snapshot contains packet bytes `P`, charter bytes `C`,
and one exhibit `E`.

1. The validator returns the immutable tuple `(P, C, E)` and a PASS receipt
   whose digests were calculated from that tuple.
2. A second process replaces all three pathnames and overwrites the original
   exhibit inode. The tuple is unchanged because it contains bytes, not open
   paths or deferred readers.
3. The runner base64-encodes `P`, `C`, and `E` into one canonical request byte
   string `R`, calculates `SHA-256(R)`, and passes `R` once to the launcher.
4. The launcher returns its observed `SHA-256(R)` and the judge request or
   session identity. A mismatch or absent identity yields refusal and no bound
   handoff receipt.
5. On equality, the runner receipt records the judge identity, `SHA-256(R)`,
   and the source digests. A test transport captures `R`, decodes it, and proves
   that the decoded `P`, `C`, and `E` have exactly the validator-receipt digests.

## Pending ratification text for the charter registry

The Ed-ratified registry is intentionally not edited in this branch. The
smallest proposed replacement for the final sentence of its “Minimal
validator” section is:

> A validator PASS records only that one invocation observed packet, charter,
> and exhibit bytes matching the supplied anchors. It is not launch
> authorization. The convening runner must construct the judge request from
> the same immutable in-process byte snapshots, bind the exact request bytes
> and the judge request or session identity in a runner receipt, and refuse
> before judge invocation when snapshot validation fails. No validator PASS
> may convene a cold judge until that runner contract and its concrete
> transport adapter are ratified and verified.

## Ruling requested

Choose the byte-to-request transport contract and concrete first launcher.
Recommendation: option A for the contract; require the magistrate to name the
launcher, its clean-environment proof, its exact input channel, and its
request/session identity source before implementation. Until that ruling, the
implemented snapshot boundary is safe to land, while operational judge
convening remains blocked.
