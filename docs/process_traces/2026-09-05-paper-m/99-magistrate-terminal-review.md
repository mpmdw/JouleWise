# Paper-M magistrate terminal review (apex diff gate, rows 7/8/12)

Merge candidate: feat/2026-09-05-paper-m at 799b60ac (this file is committed on top; the review covers the tree at
799b60ac). Base: feat/2026-09-05-paper-l (PR #290), retargeted to main once that merges.

## What I read at the bench (this session)

- Full article structure and the changed regions after three fix rounds: abstract (246/250 words), §4
  "Record support in two historical model stacks", §8 conclusion, appendix A.6 caption and reproduction
  snippet. Both record-support arms are stated with model qualifiers (Qwen2.5-1.5B-Instruct-4bit 37/50 not
  resolvable, 13/50 identifiable; Qwen2.5-7B-Instruct-4bit 50/50 identifiable, 33 three-record / 17
  four-record) and the conclusion no longer reads as a blanket failure.
- Bench runs at this head: tests.test_paper_first_use_ledger 11 OK; tests.test_paper_terms_lint 16 OK;
  tests.test_select_outcome_branches 5 OK; tests.test_paper_replay_fence 10 OK;
  tests.test_partial_record_enclosure 14 OK; scripts/check_paper_replay_fence.py --corpus-root
  /Users/edr/code/JouleWise: COMPARED 43 / MISMATCHES 0; selector: METHODS_DIAGNOSTIC validated.

## Design-level answers

1. **Is the article honest about what ran?** Yes. Every campaign-presuming section moved to
   docs/paper/protocol/prospective-comparison-protocol.md (labelled prospective/unperformed, cited once);
   both refuters, the Opus counter-review and re-check, and two fresh astra deltas confirm no sentence reads
   as if the comparison campaign ran.
2. **Is the omitted 7B arm (Opus B2) cured without overclaiming?** Yes: both arms, counts recomputed by
   three independent reviewers against 2026-08-09-prefill-phase-proof/results.json, registry rows
   DG-135–144 with fingerprints, and the mechanism number (prefill medians 0.2815 s vs 0.1365 s against a
   120.9 ms record width) stated with "duration alone does not establish the overlap count".
3. **Magistrate error corrected on the record:** my brief labelled the failing arm "1.7B"; astra stopped and
   the artifact's Qwen2.5-1.5B identity governs (report 07).
4. **Pinned artifacts intact?** Round 3 hand-edited the enclosure SVG (title label) and broke the
   pinned-generator test; I restored the script's exact output and closed B4 by defining the label in the
   caption instead. The desk script scripts/paper/partial_record_enclosure.py is unchanged.
5. **Overbuild / merge-ability prune:** nothing to prune; the branch touches docs/paper, the paper tests,
   the replay-fence checker (--draft option) and trace files only. The remaining known nits (near-verbatim
   repetition of the record-support sentences between §4 and §8) are editorial and left for the advisor
   pass.

Verdict: LANDABLE after rows 9 and 11 (full replay on the integration tree; CI on the final head).
