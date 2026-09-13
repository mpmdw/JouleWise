# Paper-N magistrate terminal review (apex diff gate, rows 7/8/12)

Merge candidate: `feat/2026-09-12-paper-n`; code-final head e5c973ab (round 3 at 0fa5fa60, record-28 cures at 50a2d72a, replay cures at e5c973ab); this file and record 29 are committed on top and the PR body row 12 names the resulting head. Base
origin/main c53d4227 merged in at 0e071fa7.

## What I read at the bench (this session)

- The complete draft diff of round 1 (`git diff dbe6c675..482a0cc4`, 864 lines) in three passes; the
  round-2 draft diff (482a0cc4..e3285e67, 101 lines) and the checker/lexicon diffs; the round-3 bench
  edits I applied myself from the cold-gate ruling (e3285e67..0fa5fa60), site by site.
- Sections read in full at the base: abstract, §1, §2, §4 record support, §5, §8.
- Bench runs (venv Python 3.13.1, R7F_CORPUS_ROOT=/Users/edr/code/JouleWise): paper module set 179 OK at
  482a0cc4; 143 OK + 23 OK (fence tests incl. the frozen-v1 regression) at 0fa5fa60;
  `check_paper_replay_fence.py --corpus-root …` COMPARED 43 / MISMATCHES 0 at every head;
  `check_paper_round7_artifacts.py --repository-root . --corpus-root …` R7F PLACED 0/4, COMPARED 415 /
  MISMATCHES 0 at 482a0cc4 and at 0fa5fa60 (see below); `select_outcome_branches.py --check-rendered`
  METHODS_DIAGNOSTIC validated, abstract 245/250; `check_markdown.py` 0 hard defects; `build_paper.py`
  wrote `docs/paper/build/out/draft-v1.html` (11 top-level sections) at 482a0cc4 and 0fa5fa60;
  `gen_state.py --check` rc 0 after the bookkeeping edits.
- Full-suite replay on the code-final tree: record 29 — `scripts/shard_tests.py --workers 4 --split` at e5c973ab: WORKERS SUMMARY shards=4 modules=233 tests=6048 failures=0 errors=0 skipped=103 failed_shards=none result=PASS, REPLAY_RC=0 (a first replay at be87d551 had three pin failures my own bench edits caused — a pull-request literal in the README blurb and a shifted d165 allowlist line — cured at e5c973ab before the clean run).

## Design-level answers

1. **Is the article still honest, and more so?** Yes. Page one now says no sensitivity ratio is computed
   on measured inference data and that the raw captures are unreleased; the seven claim-ceiling
   qualifications of the fact lens are in; the one-directional lag and the σ floor are stated as
   limitations with untested explanations, no new number anywhere (the Opus refuter's numeral-token
   diff over both rounds: zero added).
2. **Did the cuts lose anything the paper needs?** One thing, caught by delta 2 and restored in round 3:
   the build of "false difference" and the floor's purpose clause. Every other deleted build was
   verified surviving by the cold judge (record 24 Q4). The introduction's campaign apparatus now lives
   in the protocol document, where it belongs.
3. **Did the pins hold?** Every registered literal byte-identical across three rounds (seat tables +
   Astra deltas 17/22 + my replay-fence runs); the 15 HTML comment tokens intact; both outcome-branch
   headline strings verbatim exactly once; 228 retired locators absent (round-7 checker). The one
   tooling regression of round 2 (the fence regex dropping the frozen-v1 prefix) was caught by Astra
   delta 22 and cured with a regression test that extracts the committed draft-v1.md.
4. **Why a cold gate and not round three?** The same defect class (a term used before it is built)
   recurred across two delegated rounds through a different door each time (moves, then deletions and
   reviewer-prescribed text). Rule 11's standing trigger names that as a structural problem; the gate
   agreed, ruled the eleven remaining cures small enough for the bench, and ratified a mechanical
   use-site rule that now sits in the first-use ledger header so the next delegated prose round is
   contracted against it.
5. **Overbuild / merge-ability prune:** the branch touches the article, its ledger and lexicon, one
   checker regex + one test, the trace records, and three bookkeeping files. Nothing to prune. Not
   done and recorded: retitle (Ed's call), promoting Appendix Figures A1/A2 into the main text (figure
   budget), any SVG change, the figures README "Table 4" residue (swept when figure sources next move).
6. **Same-signature at the final head:** record 28 (fresh-eyes final-head review): no blocker; every round-3 edit verbatim at its site, nothing else changed in the draft, zero new quantities (one token `4` from the figure's own "Table 4" label), first-use pass on the twelve edited sentences clean, same-signature NO. Its two cures (a pin on the corrected F7 wording in the fence test; record 27's quote block re-harvested at the final head) landed at 50a2d72a and I re-ran the fence module (11 OK).

Verdict: LANDABLE. Rows 1–10 RUN on this branch; row 11 = CI on the final head (gate-ledger check turns green once the PR body carries this ledger) plus the post-merge cross-unit review; row 12 = this review of the exact merge candidate. Merge under D-072 after CI; Ed may veto by comment.
