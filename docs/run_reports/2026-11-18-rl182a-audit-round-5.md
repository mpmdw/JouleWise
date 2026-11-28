# PR #813 audit round 5 repair, 2026-11-18

[AGENT], Tier 2. Audited head `07ebee6c8`. W1 base `b2e01464d`.
[RL-182a check 1](https://github.com/mpmdw/JouleWise/blob/45b2d57/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19946)

The audit replay reproduced both annotated-assignment mutations. They
performed prompt hashing between the stamps on the first turn or a
genuine cache hit while preserving the one-tick gap.

The static check locates the event timestamp expressions and walks
the adapter AST for their store nodes. It checks each pair using indices
in the full enclosing body, so an intervening node of any statement type
breaks adjacency. Annotated writes are discovered and checked. The check
also rejects a changed pair count, including a split into two individually
adjacent pairs, and confines the unpaired prefill event to the empty stream.

Cached and uncached first yields now share the same consecutive clock
reads. The old uncached path had a separate read for the decode-start
marker. Decode start now uses prefill end's timestamp on all first yields.
The Pilot-10 source pin matches outside the first-yield boundary. The
endpoint clamp regression injects its earlier stamp through the synthetic
runtime clock instead of the superseded event helper.

The one-tick test covers the cold cached turn, a second turn that reuses
five cached tokens and feeds only the single new token, an uncached turn
and a suite item. An extra read restricted to the cache hit fails the
runtime test. Both round 5 hashing mutations and every earlier mutation
fail the static check. A separate executable replay confirmed hashing on
the intended first-turn input or the single new cache-hit token, with a
one-tick gap in either case.

All 139 focused tests passed. Scorer and registration files match the audited head byte for byte.
The accepted synthetic S/Q comparison passes with Q words enabled and
disabled. Neither state file appears in the PR diff.

The updated runtime SHA-256 is
`578455fa7b9ffb5582ef6c09ab5428d3078f3b1aea058409d39187de160a9336`.
The native runtime is a registered acquisition path. Its new commit
requires independent executing-review coverage, as does `07ebee6c8`.
CI and final-head readback are tracked on draft PR #813.
