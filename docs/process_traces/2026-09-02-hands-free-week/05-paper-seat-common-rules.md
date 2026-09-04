## Writing standard (Ed, 2026-08-19 — binding for ALL explainer, documentation, and methodology prose, in every project)

The cost of one flippantly-included term is real: on JouleWise, the single
word "converge," used without being built, cost five revision round-trips
and an entire standalone explainer page. Never again, anywhere.

- **The bar:** a reader should be able to REPLICATE the mechanism from the
  text alone — rebuild it, not follow the gist. A methodology section that
  cannot be replicated from is not done.
- **First-use test (run mechanically before delivering):** every term of
  art, criteria word, or verb doing technical work ("converge,"
  "admissible," "ruled out," "custody," "threshold"…) is either (a) built
  from physical reality before first use, (b) glossed in plain words AT
  first use, or (c) deleted. A term whose meaning arrives only in later
  text fails the draft.
- **Why-chain:** every mechanism gets its forcing problem, a concrete
  worked example with real numbers, and — for anything spatial or
  algorithmic — a diagram in which every visual element is named. An
  unexplained shape will be read as "a circle," and the reader is right.
- **No word does unpaid work.** If a later sentence would ever need to say
  a phrase "has been doing a lot of work," the explanation is out of
  order — restructure so the definition precedes the use.
- **Diff ritual:** after any revision cycle on an explainer doc, diff the
  original against the final and study what the reader's asks forced in;
  write the next first draft to survive that diff with zero asks.
- Writer-agent briefs for explainer work carry this section verbatim, and
  review passes check pedagogy (the first-use test) as its own dimension —
  factual-accuracy review does not catch these defects (proven: a
  70-claim fidelity pass caught none of the six asks).

## Common seat rules
- The audience is a professor (the advisor, a metrology expert) and an ICPE program-committee reviewer: plain language, every term defined at first use, physical explanations, NO internal shorthand (no registry IDs, kernel-row names, decision IDs, or seat names in reader-facing text).
- Every number in reader-facing text traces to a row in `docs/paper/results-fill-registry.md` or an issued artifact under `docs/paper/round7/`; you may not compute a new number at the desk. Unknown values stay as `[FILL:...]` markers with a registry row.
- Before delivering, run the first-use test MECHANICALLY on every sentence you added or changed (for each term of art: the line it is first used and the line it is built or glossed; the definition must precede) and paste the table under an "Executed evidence" heading in your report. Then run the shipped ledger test and every paper test (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'` and any test named in the paper's build notes) and paste the tail of the output.
- Do not end your turn mid-flight; commit your landing on the branch in your worktree (one or more commits with descriptive messages ending in "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"); do not push; do not touch any other worktree or the canonical checkout /Users/edr/code/JouleWise.
- Report file: write it to the path given in your launch message; keep your final JSON envelope under 8192 bytes (the report file carries the detail).
- If you need a path outside WRITE_SCOPE, stop and return NEEDS_SCOPE naming it; never widen scope yourself.
