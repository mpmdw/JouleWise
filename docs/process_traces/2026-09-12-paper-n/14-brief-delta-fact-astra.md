# Delta re-audit brief — Paper-N fix round 1, FACT + METROLOGY + PIN lens

SESSION_MODE: delegated
WRITE_SCOPE: []

READ-ONLY refuter in a detached checkout of the fix-round-1 head (the runner names the commit; confirm
with `git log --oneline -1`). Base is origin/main `dbe6c675`. Diff: `git diff dbe6c675..HEAD --stat` and
`git diff dbe6c675..HEAD -- docs/paper/draft-v2-skeleton.md`. Run Python only as `python3 -B`; never run
`docs/paper/build/build_paper.py`; never edit.

Inputs: the fix contract `docs/process_traces/2026-09-12-paper-n/12-brief-fix-round-1.md` (the lead's
dispositions), the seat's report `13-fix-round-1-astra-report.md` in the same directory (its DONE /
NOT DONE table), the original fact lens `02-review-fact-astra-report.md` (F1–F10), and the pin census
`11-pin-census-opus.md`.

## Your lens: did the fix round change any fact, break any pin, or introduce a defect? (delta only)

1. Fact preservation. For every numeral in the main text and appendix that the diff touches or moves,
   confirm the literal is byte-identical before and after (table: literal → old line → new line → SAME /
   CHANGED). Any CHANGED literal is a blocker unless the contract's "rounded reading in front of the
   retained literal" shape applies; then check the rounded reading is arithmetically right.
2. New sentences (contract items A1/A2, C6, C7, D1, D2, E1, E4, E5, E6, F2/F3): for each, quote it and
   say whether it is supported by evidence already in the draft or its appendix, and whether any new
   digit entered the main text (a new digit is a blocker). E5's two candidate explanations must be
   presented as untested; E4's σ-floor statement must match A.3.5 and Table A3.
3. F1–F10 closure: for each of the ten original findings, quote the cured passage and give a verdict
   CURED / PARTIAL / NOT CURED / REGRESSED with a sentence of reason. A cure that introduces a new
   inaccuracy (e.g. the F1 member-domain text now disagreeing with `joulewise/floor_extraction.py`) is
   REGRESSED — read the named code lines.
4. Pins: run the paper checks the census §3 lists (all of them, exact commands) and
   `scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise`; paste every tail;
   compare the COMPARED / MISMATCHES census against the seat's before/after lines.
5. Moved paragraphs (B1, B3, C1, D2): confirm each HTML comment token moved with its paragraph
   byte-identical and that none of the 228 retired locators reappeared (`grep -c` the census's list).
6. Same-signature statement: does any defect in this diff have the same signature as a finding in
   02 or 04 (same class, another site)? Say yes/no and name it.

Report (claude-codex-report/v1, genre review; envelope < 8000 bytes): findings tiered blocker /
should-fix / nit, each with new-line quotes and a minimal cure; the F1–F10 closure table; the literal
table; the pasted tails; explicit "no blocker found" if none.
