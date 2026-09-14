# Review brief — merged methods/diagnostic article, FACT + METROLOGY lens

SESSION_MODE: delegated
WRITE_SCOPE: []

You are a READ-ONLY reviewer (do not edit any file; run tests with `python3 -m unittest`, never pytest). This
worktree is a detached checkout of origin/main `dbe6c675`. The article under review is
`docs/paper/draft-v2-skeleton.md` (main text §1–§8, appendix A; ~19k words). Its evidence registry is
`docs/paper/results-fill-registry.md` (rows DX-… and DG-…, each pointing at a custody artifact); its scope
freeze is decision D-174 and its later rulings D-177/D-178/D-179 in `docs/decision_log.md`; the sections
that presume the unperformed comparison live in `docs/paper/protocol/prospective-comparison-protocol.md`.
Pinning tests you may run for orientation: `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest
tests.test_paper_replay_fence tests.test_paper_round7_artifacts tests.test_paper_first_use_ledger`.

Audience of the article: an undergraduate capstone advisor who is an energy-measurement metrologist
(JouleSort lineage) and a student research venue. The article claims ONLY: a phase-energy allocation method,
its sensitivity calculation over a registered timing domain, one historical pulse-calibration re-analysis,
and record-support counts in two historical model stacks. It must not read as a model comparison, a
dominance result, or a physical phase-energy bound.

## Your lens: is every sentence supported, consistent, and metrologically defensible?

1. Number trace. For EVERY numeral in the abstract, §4, §5 and §8 (counts such as 59/49/37/50/13/33/17,
   durations such as 0.2815 s / 0.1365 s / 120.9 ms / 0.030067931757111657 s, bundle counts 10/40/50),
   name the registry row that supplies it and the artifact the row cites, and state whether the article's
   wording matches the row's stated scope (population, model, window). Present as a table: numeral →
   section:line → registry row → MATCH / MISMATCH / NO ROW. Read the rows; do not assume.
2. Claim ceiling. Quote every sentence that a metrologist could read as stronger than the evidence:
   unconditional bounds, "validated", "guarantees", transfer of the pulse allowance to inference, any
   comparative statement between the 1.5B and 7B stacks that could be read as an energy comparison, any
   "current-method re-analysis" wording that implies the historical capture was re-collected. For each,
   quote the sentence, say what a careful reader would take it to claim, and propose the minimal rewording.
3. Internal consistency. Cross-check abstract ↔ §4 ↔ §5 ↔ §8 for any number, definition or verdict word
   that differs (e.g. "identifiable" vs "resolvable", record-support minimum, phase definitions). Cross-check
   §2/§3 formulas against Appendix A.3 (same symbols, same limits). Report each discrepancy with both
   locations quoted.
4. Method replicability (metrology bar). Could a reader rebuild the calibration and the sensitivity
   calculation from §2–§3 plus A.3 alone? Name every step where a constant, rule, or selection criterion is
   used but not stated (e.g. how onsets/offsets are fitted, the timing-domain edges, the three-record rule's
   origin). Each gap: quote where the text needs it, say what is missing.
5. Anything in §6 Related work or §9 References that mis-states a cited work as far as you can tell from the
   text itself (id/title/year mismatches) — note only; a separate seat verifies sources of record.

Do NOT propose new experiments or scope growth; the scope is frozen (D-174). Do not restyle prose.

Report (claude-codex-report/v1, genre review; JSON envelope under 8000 bytes, then the body): findings
tiered blocker / should-fix / nit, each with section:line quote and a proposed minimal cure; the number-trace
table in full; an explicit "no blocker found" if none. Write the report to the path the runner gives you
(outside this worktree).
