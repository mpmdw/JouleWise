# Paper-J — magistrate terminal review (apex Fable read)

Reviewed head: 00d8cdaa (fix round 1) plus the main merge that follows. Read in full: the prose diff of
docs/paper/draft-v2-skeleton.md against main, refuters 02-fact/02-pedagogy, the Opus counter-review 03,
the fix report 04, and the delta 05 (CLEAN, no same-signature survivor).

## Design-level questions

1. Does any cure change a claim, a number, or an outcome branch? No. The diff is vocabulary unification
   (phase edge → phase boundary; recorded-edge limit → point-only value; corner → moved-edge limit with
   the single artifact alias declared at first use), the clock-anchor bound folded into the pulse-derived
   limit at its first use, and the ledger rows following. Abstract digest, 140 fill markers, 24 outcome
   marker lines and the 266-row ledger are byte-identical (delta 05 V3).
2. Is anything now defined after its first use? No; the delta audited every cured sentence at the sentence
   unit and the first-use test runs clean.
3. Residual carried forward, NOT in this PR's scope: the ledger row "not_applicable / absolute R_cm: a
   uniform shared shift cancels when the absolute formula subtracts its cell mean" restates the physics the
   peer audits refuted (docs/process_traces/2026-09-04-peer-audit/02-claim-spine.md F2; consult 10 F2, 12 Q2).
   That sentence and its Section 4 source are paper-K's cure under the pending D-165 relabel ruling.
4. Overbuild / merge-ability: one fixture string in tests/test_paper_first_use_ledger.py followed the S2
   wording; nothing else outside docs/paper and the trace directory.

## Replay

Touched-module replay on the fix head (R7F_CORPUS_ROOT set): tests.test_paper_first_use_ledger 10 OK,
tests.test_paper_terms_lint 3 OK (delta 05 V1/V2 and bench, this session). Full-suite replay on the merged
head is recorded below when it lands.

Verdict: LANDABLE.
