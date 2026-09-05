# One-name sweep — Sol fix round 2

Date: 2026-09-04  
Role: implementation seat  
Base: `94af46458aab6bb8597f2c4564f9b6d1e0d6975e` (exact)  
Outcome: `NEEDS_RULING` — no implementation attempted

## Early-return basis

The round-1 delta re-audit's only active finding is R2. It marks R2
`same_signature: true` and describes it as the same provenance-only replay
mismatch as the prior refuter: fresh generation records the current producer's
last-changing commit (`94af4645...`), while the issued artifacts record
`6b6deb2f...`. The fix-round brief explicitly forbids a third attempt when the
same signature repeats. This report therefore stops before changing the
producer, artifacts, registry, draft, or tests.

## NEEDS_RULING

**Question.** Should the lead execute a history-excluding rebuild/squash of the
surviving three-file terminology delta onto the current main-line tip and then
rerun the byte-exact replay at that resulting commit?

**Options considered.**

1. Rebuild or squash only the surviving terminology edits onto the current
   main-line tree, excluding the producer/artifact history that changed the
   producer's last-changing commit. The re-audit's detached-`origin/main`
   counterfactual already passes, so this preserves the settled provenance
   contract and makes the named counterfactual the landing regression.
2. Redesign the producer provenance field or weaken byte-exact replay. This
   changes settled contract semantics, would require a new ruling, and risks
   making committed artifacts self-referential or non-reproducible.
3. Preserve this branch's ancestry and edit the artifacts or producer again.
   This repeats the same signature: any producer edit changes the value returned
   by the last-changing-commit lookup, while merely refreshing artifacts cannot
   make the current producer history equal the issued provenance.

**Recommendation.** Choose option 1. It is the narrow structural cure proved by
the re-audit's `R2_ORIGIN_MAIN_COUNTERFACTUAL_MATCH`: land only the final-tree
terminology delta without carrying this branch's producer/artifact-changing
ancestry, then make byte equality from the resulting commit the acceptance
test.

**Blocked work.** R2 cannot be cured on this branch without violating the
brief's no-round-three rule. The lead owns the history-excluding landing ruling
and the final replay at the resulting commit.

## Finding → structural cure → file:line

| Finding | Structural cure (not applied) | Relevant file:line |
|---|---|---|
| R2 — repeated provenance-only replay mismatch | Rebuild/squash the surviving terminology-only delta onto main without the producer/artifact-changing ancestry; rerun byte-exact generation at the resulting commit and require both outputs to compare equal. | `scripts/issue_dg071_dg075_statistics.py:398` (`_git_commit`), `scripts/issue_dg071_dg075_statistics.py:593` (JSON emission), `scripts/issue_dg071_dg075_statistics.py:625` (Markdown emission), `docs/paper/round7/dg071-dg075-statistics.json:28`, `docs/paper/round7/dg071-dg075-statistics.md:12` |

## Verification

- Confirmed `HEAD` is exactly `94af46458aab6bb8597f2c4564f9b6d1e0d6975e`
  on `feat/2026-09-04-fan-one-name-sweep`.
- Inspected the round-1 re-audit and confirmed its sole active finding is marked
  `same_signature: true`; no `NOT CURED`, `REGRESSED`, or `NEW` finding remains
  that the brief permits this seat to implement.
- No test module was touched, so none was run under the brief's touched-modules-
  only preflight rule. The re-audit records the named detached-main
  counterfactual tail as `R2_ORIGIN_MAIN_COUNTERFACTUAL_MATCH`.
- Preserved the pre-existing untracked round-1 re-audit unchanged.
