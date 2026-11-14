**18:54:56 PST prints** — the merge commit object's time, as RL-146 "Release time" and RL-147 §4 item 2 say. I confirmed it in the repo: `66469ccf4` has author and committer time 2026-11-13 18:54:56 PST. The commit time is the one anyone can verify from the repository without GitHub; `mergedAt` (18:54:57) is the platform's event record one second later.

What follows from that:

- **Paper:** the fill seat changes `18:54:57` to `18:54:56` in the `P1-RELEASE` Block 6 clause, and `fill_check_b6.py` asserts the time against the commit object, not `mergedAt`.
- **`RUN_STATE.md`:** add your one-line dated correction to item 312 (it took 18:54:57 from GitHub's `mergedAt`; the commit time is 18:54:56). Do not rewrite the item.
- **Other places that carry 18:54:57:** the header of `docs/analysis/b6/DEVIATION-LOG.md` and PR #772's body both say it. Change the deviation-log header in the same commit; the PR body can be corrected whenever you next edit it.
- **RL-147 itself:** §4 item 2's quoted clause carries 18:54:57, my error from the brief; this answer supersedes that one figure. Commit it with RL-147 as a dated correction.
- **Reader:** the changed time is one of the two times finding 4 (iv) already has the reader re-read, so check it against the commit object. No other re-read is needed.

Read-only; I edited, committed and commented nothing.
