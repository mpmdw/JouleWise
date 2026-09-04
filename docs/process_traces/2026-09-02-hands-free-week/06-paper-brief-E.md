# Paper seat E — write §6 "Printed negative result" as reader-facing prose

Worktree: /Users/edr/code/JouleWise-wt-paper-e (branch feat/2026-09-02-paper-e-negative, from main 33290b8b).
WRITE_SCOPE: [docs/paper/draft-v2-skeleton.md, docs/paper/results-fill-registry.md, docs/paper/figures/, docs/paper/figures-plan.md, docs/paper/round7/, docs/paper/fill-rehearsal/, tests/]

## Forcing problem
The paper (`docs/paper/draft-v2-skeleton.md`) has exactly one research question that is already answered from data on disk: 37 of 50 short-prefill phases in the retained diagnostic window overlapped only two sampler records (fewer than the three the resolvability rule requires) and are therefore "not resolvable". Its section, "Printed negative result: short prompt processing has too few overlapping records" (`:917-940`), is still a build note — zero reader-facing sentences. Every input exists: registry rows DG-067..DG-077 (`docs/paper/results-fill-registry.md:639-649`; DG-067/068/069/072/073/076/077 are MEASURED, DG-070/074 are DERIVE) and the DG-071/DG-075 statistics issued by PR #276 (`docs/paper/round7/dg071-dg075-statistics.md` + `.json`; values of record: DG-071 sampling-record interval width n = 406, median 120.9186 ms, IQR 5.9508 ms; DG-075 record spacing n = 405, median 120.9224 ms, IQR 5.8949 ms — verify these against the artifact and quote the artifact's path and SHA-256).

## Deliverables
1. Replace `:917-940` with prose that a professor can replicate from: what a sampler record is (build it from the 100 ms-class powermetrics cadence already built in §1 `:87-91`), what "overlap" means for a phase and a record (a named diagram: the phase's start and end edges on the time axis, the tiled records, the overlap count — every element labelled, SVG under `docs/paper/figures/`, registered in `figures-plan.md`), why fewer than three overlapping records makes the phase energy unresolvable (the forcing problem, with the worked example from DG-070/DG-074: a 0.121 s prefill phase against ~121 ms records), the population result (37 of 50 two-overlap, 13 three-overlap), and what the reader should conclude and NOT conclude (diagnostic-era data, non-claim-bearing; the demonstration's G2-a-selected prefill length is the response). Keep the frame the skeleton's build note prescribes; if the note prescribes something you cannot back from the registry, say so in the report instead of inventing.
2. Flip registry rows DG-071 and DG-075 from STOP_FILL to ISSUED, citing the artifact path and SHA-256, and update the fill-checklist sentences that reference them (grep the registry and `fill-rehearsal/` for DG-071/DG-075).
3. Add ledger entries for every new term (IQR, record support, overlap count, ...) to the first-use ledger (`:1551-1790`) so the shipped ledger test stays green and honest.
4. Re-pin the round-7 artifact fence (R7F) if your edits change any fenced artifact: find the fence's documented procedure (`grep -rn R7F docs/paper tests scripts`) and follow it exactly; if the fence does not cover your files, say so.
5. Report: `<report path>` with the diff summary, the first-use table, the test tail, and any registry contradictions you found.

Effort: xhigh. Read `docs/paper/round7/built-terms-lexicon.md` before writing so you reuse the paper's built vocabulary instead of coining new terms.
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
