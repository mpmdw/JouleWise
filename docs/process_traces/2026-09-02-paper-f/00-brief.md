# Paper seat F — cure the 24 first-use defects, §1 scope paragraph and naming bridge, ledger test hardening

Worktree: /Users/edr/code/JouleWise-wt-paper-f (branch feat/2026-09-02-paper-f-firstuse, from main 33290b8b).
WRITE_SCOPE: [docs/paper/draft-v2-skeleton.md, docs/paper/round7/built-terms-lexicon.md, tests/]
DO NOT edit these regions of `draft-v2-skeleton.md` (other seats own them; line numbers as of main 33290b8b): Abstract `:23-80`, §6 "Printed negative result" `:917-940`, §7 "What the finding changes" `:998-1004`, §10 `:1222-1230`.

## Forcing problem
A fresh-reviewer audit ran the first-use test mechanically on the draft and found 24 defects that the shipped ledger test (`:1551-1790`, keyed on exact strings) cannot see because singular, possessive, and compound forms escape an exact-string match. The table of the 24 rows with a proposed cure for each is in the audit file
`/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-fresh-fable-audit/03-audit-paper-rq.md` §4.2 (read-only; that worktree is not yours). Re-verify each row against the current text before curing it — the audit was written at a slightly earlier head.

## Deliverables
1. Cure every row of the §4.2 table (use the proposed cure unless the text already changed; record each row's disposition: cured / already-fixed / disputed-with-reason). Excluding rows inside the regions above (those go to the owning seat: note them in your report).
2. §1 scope paragraph: name the machine (Apple M3 Max, 128 GB) and the runtime (MLX) once, early; add the naming bridge in one appositive — "resolution bound", the advisor's term "detection floor", and "cell floor" are related how (read `:112-114` and `:641-700` and say it exactly); adopt ONE symbol for the corner quantity (`U_edge` vs `U_corner`, `:115` vs `:486`) across the whole draft.
3. Extend the ledger test so a term's singular/plural, possessive, and hyphenated/compound forms count as uses (and would have caught these 24); keep it green on the cured draft; add a regression fixture that fails on the pre-cure text.
4. Update `built-terms-lexicon.md` for any term you built.
5. Report: `<report path>` with the 24-row disposition table, the first-use table for your added sentences, the test tail.

Effort: high.
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
