# PR #709 cold review (Fable 5.2) and dispositions

Reviewer: Fable 5.2 (high), cold, 2026-11-10 20:02 PST. Head reviewed: `0b1333562` on base `60d3225ee`. Verdict: **ADMIT-WITH-FIXES**.

## Verified by the reviewer
- `git diff a1a5029fb HEAD -- docs/paper/paper1` is empty (tree `27d1e96df` on both sides). The annotated tag `paper1/blind-draft-2026-10-27` (object `8c7096c45`) peels to `a1a5029fb`, the lane tip.
- `docs/analysis/b5/RESULTS.md` is blob `5432cc227` at `0b0658a20` and HEAD (sha256 `fb5f81e8…6f55`).
- 19 files and 14 commits. No lane commit touches a path outside `docs/paper/paper1/`. Both merges reproduce exactly under `git merge-tree`, with no hand edits.
- `build_fill_index.py` reproduces `fill_index.md` byte-identically (`236 215 219 174`). `build_figures.py` regenerates all five SVGs with no diff.
- RL-3 is not breached: landing is RL-3 condition 1, the file is marked internal in CANONICAL, and no B5 headline value appears under `docs/paper/paper1/`.
- Local tests: `test_d165_rationale_census` (10), plus `test_paper_successor_migration`, `test_paper_first_use_ledger`, `test_claims_lint` and `test_paper_comparison_placements` (72). All OK.

## Findings and dispositions
| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F1 | MED | CANONICAL said PAPER-OUTLINE lines were marked; they are not | Fixed (`233d999e7`): narrowed to PAPER-PLAN-v2, naming PAPER-OUTLINE lines 29, 75 and 164 as not yet marked |
| F2 | MED | A squash or rebase merge would drop `a1a5029fb` from main's ancestry | The lead merges with a merge commit (`gh pr merge --merge`), then checks `merge-base --is-ancestor a1a5029fb origin/main` |
| F3 | LOW | PAPER-PLAN-v2 notes read as Block 5 joining the tripwire manuscript | Fixed: "reported in Paper 1 (item 256 E1; RL-1, RL-8), not as a section of this manuscript" |
| F4 | LOW | TALK-OUTLINE gloss of RL-3 omitted the licence-constraint check | Fixed: "(all three conditions of RL-3, including the check against the ten licence constraints)" |
| F5 | LOW | "milestones and roles do not govern Paper 1" is in no ruling | Fixed: "Its milestones do not govern Paper 1; Paper 1's seats, builders and reviewers are set by RL-24" |
| F6 | LOW | RL rows had no pointer to the log | Fixed: the Decisions row now points at the RL log (item 257) |
| F7 | LOW | The tag ruleset did not cover `paper1/**` | Fixed by the lead: ruleset 26996548 now includes `refs/tags/paper1/**` |
| F8 | INFO | Gate ledger pending; CI not yet observed | This record; CI on the final head |
| F9 | INFO | The Build row could read as Paper 1's build | Fixed: "(renders `draft-v1.md` by default; not yet Paper 1's build)" |
| F10 | INFO | Trailing whitespace inside the tagged tree | No change: fixing it would break the zero-diff |

Notes routed to the research lead: the repo is public, so "internal" is a label, not access control; a site rebuild would carry item 232's numbers; RESULTS.md's §6 and §8 gate list is stale; RL-1 item 3 vs item 256 E1 on the tripwire manuscript's exclusion; item 257's time stamp.
