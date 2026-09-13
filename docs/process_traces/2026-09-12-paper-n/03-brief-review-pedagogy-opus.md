# Review brief — merged methods/diagnostic article, PEDAGOGY + STRUCTURE lens (Opus)

You are a READ-ONLY reviewer. Do not edit any file. Work in `/Users/edr/code/JouleWise-wt-paper-n-ref`
(detached checkout of origin/main dbe6c675). The article is `docs/paper/draft-v2-skeleton.md`
(main text §1–§8 plus Appendix A). Its audience: an undergraduate capstone advisor (energy-measurement
metrologist) and a student research venue; plain language; every term built at first use.

Apply this writing standard MECHANICALLY (it is binding on this project):

- The bar: a reader should be able to REPLICATE the mechanism from the text alone — rebuild it, not follow
  the gist.
- First-use test: every term of art, criteria word, or verb doing technical work ("resolvable",
  "identifiable", "record support", "held-average reconstruction", "registered timing domain", "shared-energy-sign",
  "local corner", "floor", "cell", "custody", "fence", "refusal", "moved-edge limit", "point-only value"…)
  is either (a) built from physical reality before first use, (b) glossed in plain words AT first use, or
  (c) should be deleted. A term whose meaning arrives only in later text FAILS.
- Why-chain: every mechanism gets its forcing problem, a concrete worked example with real numbers, and — for
  anything spatial or algorithmic — a diagram in which every visual element is named.
- No word does unpaid work: if a later sentence would ever need to say a phrase "has been doing a lot of
  work," the explanation is out of order.

## Deliverables (write them as ONE Markdown report to
`/Users/edr/code/JouleWise-wt-paper-n/docs/process_traces/2026-09-12-paper-n/04-review-pedagogy-opus.md`)

1. First-use ledger of the MAIN TEXT (§1–§8, abstract included): a table of every technical term — line of
   first use, line where it is defined/built, verdict PASS (defined at or before first use) / LATE (defined
   later; cite the line) / NEVER. Be exhaustive; ~40–80 rows is expected. Terms defined only in Appendix A
   count as LATE for main-text use.
2. Redundancy map: passages that restate the same fact in near-verbatim words (known example: the
   record-support sentences appear twice in §8 "Conclusion" and again in §4 "Record support in two historical
   model stacks"; abstract vs conclusion). For each, quote both locations and recommend which ONE survives
   and the exact replacement wording for the other.
3. Reading-order defects: places where a section relies on a mechanism explained later (cite both lines),
   and the minimal reorder or gloss that cures it.
4. Figure and equation check: for each figure reference (Figures 1–4, A.7 schematic) and each display
   equation in §2–§3, is every visual element / symbol named in the text before it is used? List failures.
5. Abstract: word count (cap 250) and whether a non-specialist can state, after reading it alone, (a) what
   was measured, (b) what was NOT claimed. Propose a tightened abstract ONLY if it currently exceeds the cap or
   fails (a)/(b); otherwise say "abstract passes".
6. Findings tiered blocker / should-fix / nit, each with a quoted passage and a proposed minimal cure
   (sentence-level, no restyling of passages that pass). Do not propose scope growth; scope is frozen
   (decision D-174). End with "no blocker found" if none.

Constraints: read the whole main text before writing; do not run the paper's tests (a sibling seat does);
do not propose new experiments.
