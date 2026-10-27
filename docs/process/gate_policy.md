# Gate policy (binding, Ed, 2026-10-27)

**Authority.** Ed, Claude Code session 015ASG1T, 2026-10-27. He answered "yes" to items 1, 3, 4, 5 and 6 of the
pipeline audit's decisions (`docs/process_traces/2026-10-27-pipeline-audit/`), having said: "cut the agent review
rounds then - especially those that havent produced any meaningful catches - but learn from where they did, and keep
a minimal second set of eyes where possible, maybe 6.1 sol xhigh fast for speed sake". Directive issue #589 carries it.

This policy was made before any block-5, block-6 or BYTES result was seen. It changes how code and rules are checked,
never what is computed. Where a registration's own text requires more (the block-5 seal's §10, block-6 §13 and §17,
BYTES §19), the registration wins until it is amended under its own rule. It supersedes the review-round parts of
`docs/orchestration.md` and the D-184 four-model council policy.

## What the October record showed

- **Real defects came from executing reviews of number-bearing code, and from running things.** Examples: the #416
  NEG-8 reference-span blocker (RUN_STATE item 69); a reference silently dropped on a read failure (FIX-416 rounds);
  the twin diverging on compressed input (#573); machine tests and real-shaped data.
- **Late rounds** mostly found defects in the previous round's fixes, but some were real HIGHs, so a hard round cap is
  unsafe.
- **Councils on process questions, reviews of docs and bookkeeping, and serial re-reviews** added time and little
  protection.

## The rule

1. **Docs, records, RUN_STATE, briefs, bookkeeping:** CI only.
2. **Tests, tooling, orchestration, and collection code that cannot change a number:** CI and the change's own
   regression test. One reviewer only if the author asks.
3. **Code that can change, select or exclude a claim number** (reduction, calibration, harvest/exclusions,
   estimators, analysis, blinding, the recompute), and the agent census, stand-down and arm checks:
   - CI, a regression test, and a counterfactual showing the test fails without the change.
   - Two executing reviews from different model families, **launched together**, each told to probe and mutate:
     Sol 6.1 at xhigh, fast (`service_tier = "priority"`), and Opus 5.5. (Fable 5.1 replaces either seat if it is
     unavailable.)
   - Together they count as both the independent review and any cold pass a ruling asks for.
4. **Fix rounds:** both reviewers check only the fix diff, until a round finds nothing above LOW. If the same defect
   class appears twice, the lead writes a structural rule; a third time, consult Ed.
5. **Rule changes and registration text:** one executing refuter (Sol 6.1 xhigh fast) plus a recorded lead line. A
   judge rules only when a registration requires one, or when the refuter's executed result contradicts the lead on
   a counting or exclusion rule.
6. **Councils:** only for a genuine science-design fork that changes what is measured or claimed. One seat per family,
   one round, and the lead or Ed decides. Process questions get no council. Ed can still ask for one.
7. **Unchanged:** the #416 three-family audit before a claim-bearing run; the agent census and physical-hazard
   refusals; file hashes and custody manifests; battery float (#421); blinding; the independent recompute and its
   agreement bars; CI.
8. **Release:** no cold gate beyond what the registration names (RUN_STATE item 37(ii), 2026-10-14).
9. **Pruning tally:** each session record ends with a table: gate, ran, caught_number, caught_session_refusal,
   evidence. A gate with no catch in three sessions is proposed to Ed for removal.
