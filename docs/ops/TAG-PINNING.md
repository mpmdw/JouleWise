# Tag-based pinning for future blocks

Design only; implements [freeze-by-commit F1–F6](../process/freeze_by_commit.md).
Do not edit the frozen Block-5 driver, its registration, its tags or its refusal
semantics. Preserve main ancestry for existing reproductions. Introduce this
contract in a future driver/registration, then migrate main's integrity tests
under a reviewed post-release PR.

## Identity and authority

A registration binds `{block_id, role, commit, tree, ref, inputs, environment}`:

- `commit`: full Git commit SHA; `tree`: full tree object ID.
- `ref`: exact approved annotated tag, for example `refs/tags/pin/b6-analysis-r1`,
  or an exact protected block release branch. No namespace-wide “any pin tag”
  match. Collection, analysis and ledger-head identities are distinct roles.
- `inputs`: `{repo-relative path: SHA-256}` plus external artifact identities.
  Check Git blobs at the registered commit, not today's working tree. Treat
  external identities as metadata; do not fetch weights or open sealed data in
  an identity check.
- `environment`: Python minor/build, pyproject, resolved lock digest, OS/toolchain
  notes and hardware requirements. Preserve constraints-only limitations where
  the historical block did not record a fully resolved lock; do not fabricate one.

The hashed/reviewed registration's commit is the authority. A mutable tag or
branch name cannot replace it. Prefer annotated immutable release tags; configure
server rules to prohibit update/deletion, and retain them in a standalone bundle.
Signed tags can add signer authentication where keys are available. Neither a
local tag nor a local remote-tracking ref proves server protection. Record that
administrative evidence separately; the driver verifies object identity offline.

## Validator

For an ordinary immutable run, require:

1. Resolve the **exact** registered ref, peel it to a commit, verify annotated
   tag type when the contract requires a tag, and compare to registered commit
   and tree. Missing/ambiguous refs, moved tags, unavailable objects or malformed
   registrations refuse with stable field-only errors. No fallback to main.
2. Require clean tracked checkout and `HEAD == registered commit`. Verify input
   digests from that tree, environment record and the existing artifact/custody
   bindings. A ref's existence or ancestry alone never authenticates those bytes.
3. If the registration explicitly permits reviewed revisions on a protected
   block branch, require the anchor to be an ancestor of HEAD **and** HEAD to
   belong to that exact block release line **and** an authenticated ruling entry
   to name the precise new commit/tree and superseded identity. Every executed
   revision gets its own immutable `pin/<block>-analysis-r<k>` tag. Unlisted
   descendants, merges and cross-block commits refuse even if branch-contained.
4. Record registered and executed commit/tree, ref and peeled target, revision
   ruling, input digests and environment identities in the run receipt. Errors
   and blinded checks expose identities/field names only, never measured values.

The Git predicates for retention/line membership are explicitly separate:

```sh
# Exact immutable identity (compare output to the registered full SHA):
git rev-parse --verify 'refs/tags/pin/b6-analysis-r1^{commit}'
# Retention: this does not authorize execution of a different commit.
git merge-base --is-ancestor "$registered_commit" "$preserving_tag^{commit}"
# Optional revision-line topology, only alongside an exact ruling allowlist:
git merge-base --is-ancestor "$anchor_commit" "$executed_commit"
git merge-base --is-ancestor "$executed_commit" refs/remotes/origin/block6-release
```

A tag need not descend from main; deleting the old delivery branch must not
affect a valid immutable run. Protected branches are convenient delivery lines,
but their tips move. A previously registered run still binds its exact commit;
do not dynamically reinterpret it as “whatever the branch points at today.”
Never allow a tag on unrelated main history to authorize a block's execution.

## Guard test to implement with the future driver

Add `tests/test_block_git_pin_contract.py` with tiny synthetic Git repositories,
no measurements, network, model weights or optional MLX imports. Test the real
validator's public seam, not a mocked ancestry result:

| Fixture/action | Required outcome |
|---|---|
| Registered annotated tag on an orphan/off-main collection/analysis line; exact clean HEAD, matching tree/digests | Accept without `origin/main` |
| Delete its delivery branch and advance unrelated main; recover tag from a complete bundle in a repository with no alternates | Still accept; registered blob digests equal |
| Delete tag, shallow/missing required object, malformed ref or tag targets a blob/tree | Refuse with distinct stable identity errors |
| Move expected tag to a different commit, even one with identical file bytes; substitute an unregistered tag from the same namespace | Refuse; registered commit equality is mandatory |
| Correct tag but wrong HEAD, dirty tracked file, changed registered input, wrong tree/environment digest | Refuse |
| Branch-contained descendant with no ruling, cross-block merge, or forged local tracking ref without registered commit/ruling | Refuse |
| Explicit permitted revision, exact new commit/tree in authenticated ruling, correct block-line topology and new immutable revision tag | Accept and receipt names both identities |
| Prior registration replayed after branch advances | Same original commit remains authoritative |

Also add a regression proving the existing B5 validator/driver source and seal
digests are unchanged by introducing the new contract. Move main's historical
freeze tests to Git-blob checks only in the separate approved migration PR;
the reproducing B5 checkout retains its original tests. CI for the new test
must include full required tag history; missing history is a setup failure,
not a reason to skip a pin test or fetch opportunistically inside a validator.

No implementation or native validation is claimed here. This design needs no
MLX execution. Any eventual change that affects ALIGN's native runtime must be
validated by its lead on Metal-capable hardware, outside this sandbox.
