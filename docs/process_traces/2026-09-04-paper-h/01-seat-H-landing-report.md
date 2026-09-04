# REPORT-H — Paper seat H: dissolve the Section 1 glossary

Date: 2026-09-04. Branch: `feat/2026-09-04-paper-h`. Exact starting
HEAD: `a6e9edde082f460fbe335d2eac8021f77258b8e6`. The worktree started clean.
No commit was requested or made.

## Planning audit

1. **Goal:** replace the glossary-first opening with prose in which the
   physical boundary problem forces each needed name at its first use.
2. **Prior state inspected:** the active stop-card/status/workspace sections,
   current queue and do-not-do-yet list, Mission M0, orchestration and bridge
   contracts, the skeleton and fill registry, both paper tests, and the E/F/G
   terminal reviews. No stop card was active.
3. **Inherited assumptions:** the three Abstract outcome groups are frozen;
   every fill marker and all issued numbers must survive; no result may be
   inferred from an unresolved registry row.
4. **Progress:** closes the only nonblocking pedagogy residual in the paper-G
   terminal review, `PAPER-H-INTRO-GLOSSARY-01`.
5. **Acceptance evidence:** exact-base check; unchanged Abstract digest;
   unchanged fill-marker count; `FAILS: 0`; both authorized test modules green.
6. **Captured commands/artifacts:** final test tails below and this report.
7. **Nonblocking failure policy:** an undefined term is repaired or deleted;
   an unavailable result stays `STOP_FILL`. No measurement was attempted.
8. **Excluded work:** no Abstract wording, outcome branching, registry status,
   result value, test code, queue/state file, or Git history was changed.

## Change

The former one-paragraph glossary is gone. Section 1 now proceeds from the
thing the machine reports to the question the paper asks:

1. `powermetrics` emits one start-to-end average.
2. Prompt processing and token generation meet at a runtime-recorded phase
   edge.
3. One sampling record can straddle that edge. Moving the edge reallocates a
   slice of integrated energy while the request total remains unchanged.
4. Time-stamped GPU pulses and a rate-aware clock mapping constrain the allowed
   movement; the inserted-gap check is introduced only when the pulse-to-model
   transfer problem appears.
5. Configuration cell, component, point/moved bounds, independent/shared
   ratios, authentication, evaluation, the cutoff at 2, and the model decision
   rule appear only as their calculations become necessary.

Glossary-only labels with no later job were deleted: `physical ambiguity`,
`uninterrupted collection`, `edge behavior`, `largest spurious difference`,
`uncertainty range`, `short-input diagnostic records`, `overlapping power
samples`, and `internal processor-power fields`. The later `power sample` use
now defines the object in place. The ledger re-homes `members`, `R_cm`, and
`missing / malformed`, inventories `phase edge` and `power sample`, and records
266 terms with `FAILS: 0`.

The Abstract block SHA-256 is unchanged at
`a52064fd715629bc73c1e87aa0534c2dfd455293d01e5c3f44aa20322fc3a9b7`.
The skeleton contains 140 `[FILL:...]` markers before and after this work.
`results-fill-registry.md` was inspected but required no edit: this mission
changed no supplier, fill rule, or freeze status.

## Verification

The first ledger replay after the prose move correctly went red on stale homes
and exact gloss contracts; those findings were repaired before the final runs.
Per the preflight restriction, no other test module or full suite was run.

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
..........
----------------------------------------------------------------------
Ran 10 tests in 1.725s

OK
```

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint
...
----------------------------------------------------------------------
Ran 3 tests in 1.397s

OK
```

## SCOUT — next five highest-value paper asks

The E and F terminal reviews closed their paper-content defects, and G left
only the glossary residual completed here. The remaining high-value asks are
therefore the registry's stopped result producers, especially those that feed
G's three outcome branches.

1. **Issue the prefill identity.** V5-G2A-001 and V5-WL-005 wait on the
   authenticated `scripts/select_g2a_prefill_length.py` output with its exact
   path and SHA-256, followed by the G2-a-bound
   `joulewise.prefill_prompt_pin.v2` record.
2. **Build the D-123 reported-mean supplier.** DS-09 through DS-24 wait on
   issued alpha/beta artifacts carrying each phase mean and full interval,
   authenticated observed-token denominator, and admitted independent-bundle
   count.
3. **Issue the gamma claim-evaluation fields and professor-facing renderings.**
   DS-29 through DS-33 and PG-01 through PG-08 wait on an authenticated gamma
   claim-evaluation artifact that names the claim-side bound, estimate,
   composed endpoints, magnitude outcome, direction outcome, and verdict for
   decode and the G2-a-selected prefill arm.
4. **Issue the dominance close-out.** OB-01 and the close-out limb of OR-01
   wait on a complete authenticated `joulewise.d165_dominance_closeout.v1`
   artifact plus a conservative renderer for every failed component or issued
   stop reason.
5. **Run and issue the transfer check.** TR-01 waits on accepted
   `TRANSFER-FIDUCIAL-01` evidence containing the largest inserted-gap edge
   residual, an explicit supported/not-supported result field, and its
   professor-facing rendering.

## Residual risk

The two authorized tests prove ledger placement and the standing terminology
lint contract; they do not substitute for the lead's final full-paper read.
All scientific result slots above remain stopped until their named artifacts
issue.
