# Gate policy, 2026-10-27: executed checks first, one second set of eyes

**Status: DRAFT, not adopted. Held for the pipeline audit (Ed, 2026-10-27: "we can wait before that's decided its full audit").** Ed's words, in Claude Code session 015ASG1T: "cut the agent review rounds then -
especially those that havent produced any meaningful catches - but learn from where they did, and keep a minimal
second set of eyes where possible, maybe 6.1 sol xhigh fast for speed sake." Earlier the same day: "the only real rule
is good science at a speedy cadence".

This replaces the review-round parts of `docs/orchestration.md` (cold gates, councils, delta passes, the D-184
four-family councils) and the three-family requirement of directive #416. It does **not** change what protects the
numbers: registrations fixed before data, blinding, file hashes, the independent recompute and its agreement bars,
physical-hazard refusals, and CI. Gates written into a registration's own text (block-5 seal errata, block-6 §13 and
§17, BYTES §19) stay as written until amended by that registration's own rule; the lead drafts those amendments
(pipeline audit, 2026-10-27).

## What the October record shows

Agent reviews caught real defects in one pattern: **the first adversarial review that executed the code, on code
that computes or selects claim numbers.** Examples:
- The #416 audit found the NEG-8 reference span was the whole stage, 6.5-6.9 times the request, so the drift
  allowance B was too small. Fable and Opus found it; the third auditor missed it. RUN_STATE item 69.
- A cold delta pass found a reference dropped silently on a read failure (FIX-416 rounds, item 69).
- A cold delta pass on #573 found the independent twin silently diverging on compressed input (185 and 243 fields).
  Item 68's record.
- The PR #500 executing review found a watchdog stand-down gap (MAJOR-1). Item 41.

What did not pay: later rounds on the same change mostly found defects in the previous round's fixes. The #416 work
took seven rounds of cold passes over about two days. Councils and judges on process questions, reviews of
docs/records/bookkeeping, and second and third reviewers of the same diff from other families also added little.
Several real defects were found by **running things**, not by review: machine tests (stale sidecar, agent-presence
flag, three desk defects), the real s1 session (missing sidecars), and real-shaped data (step 9b's deadline). The
pipeline audit's evidence ledger will replace these examples with counts; adjust the tiers below if it disagrees.

## The rule

| Change | Executed checks (always) | Second set of eyes |
|---|---|---|
| Docs, records, RUN_STATE, briefs, bookkeeping | CI | none |
| Tests only, tooling, orchestration, collection code that cannot change a number | CI, plus the change's own regression test | none, unless the author asks |
| Code that can change, select or exclude a claim number (reduction, calibration, harvest/exclusions, estimators, analysis, blinding, the recompute) | CI, the regression test, and a counterfactual showing the test fails without the fix | **one** adversarial executing review by a different model family from the author: Sol 6.1 at xhigh, fast (`service_tier = "priority"`). It runs the tests and its own counterfactuals; findings come back with evidence |
| Registration text, amendments, rulings that change what counts | the re-derivation or replay the text cites | **one** blind executing refuter (Sol 6.1 xhigh, fast), where the registration's own rule asks for a refuter or gate |
| Before a pack's release | the independent recompute agrees within its registered bars; the release rerun matches the dry run | none beyond the above |

**Rounds.** One review. The author fixes. If any finding was a blocker, the same reviewer checks **only the fix
diff**, once. Anything still disputed goes to the lead, then to Ed if it is a science question. There is no third
round and no new reviewer on the same diff.

**When Sol is unavailable** (quota, outage), use one Opus or Fable executing review instead, from a session that did
not write the code. Never wait on a reviewer: record the gap and proceed only for the non-claim tiers.

**Councils.** Only for a genuine science-design fork: two defensible designs that change what is measured or
claimed. One seat per family, one round, and the lead or Ed decides. Process questions get no council.

**What stays exactly as it is:** the agent census and physical-hazard refusals, file hashes and custody manifests,
the battery-float rule (#421), blinding, the independent recompute, and CI.
