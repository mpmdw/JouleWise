# Delta re-audit brief — Paper-N fix round 1, PEDAGOGY + STRUCTURE lens (Opus, read-only)

Work in `/Users/edr/code/JouleWise-wt-paper-n-ref` after the lead checks out the fix-round-1 head there
(confirm with `git log --oneline -1`; it must not be dbe6c675). Do not edit any file except the single
report you write at
`/Users/edr/code/JouleWise-wt-paper-n/docs/process_traces/2026-09-12-paper-n/16-delta-pedagogy-opus.md`.

Inputs: your original review `04-review-pedagogy-opus.md`, the fix contract `12-brief-fix-round-1.md`,
the seat report `13-fix-round-1-astra-report.md`, the blind advisor read `06-blind-fable-advisor-read.md`
(Asks 1–12), and the diff `git diff dbe6c675..HEAD -- docs/paper/draft-v2-skeleton.md`.

Apply the writing standard mechanically (first-use test; replicable from the text; every diagram
element named; no word does unpaid work).

Deliverables, one Markdown report:
1. Closure table for B-1..B-3, S-1..S-14, N-1..N-7, RO-1..RO-9, F-1..F-4 and Asks 1–12: CURED /
   PARTIAL / NOT CURED / REGRESSED, each with the new line quoted.
2. Re-run the first-use test on every MOVED or NEW paragraph only (§1 compressed block, §3 additions,
   §2 reordered numeric-rules paragraph, A.4/A.3.9 additions, §5 additions, new abstract): list any
   term now used before it is built, with both lines.
3. Read the new §1 and the new abstract as a whole: does the reading order now hold (problem → method
   → what was measured → what was found → what is not claimed)? Quote the first sentence that breaks it,
   if any. Abstract word count.
4. New defects introduced by the round (a moved paragraph that now dangles, a cross-reference to a
   renumbered figure that was missed, a gloss duplicated in two places): tiered blocker / should-fix /
   nit with minimal cures.
5. Same-signature statement: does any new defect repeat a class from 04? Name it.
End with "no blocker found" if none.
