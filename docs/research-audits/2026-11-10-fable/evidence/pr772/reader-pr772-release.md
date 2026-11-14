# Reader report, PR #772 P1-RELEASE delta (final pass finding 4 (iv))

Reader: Sonnet 5.5 reader seat (separate from the fill seat), for the laptop lead
Time: Fri Nov 13 20:05 PST 2026 (from `date`)
Head: `c5e7fe38e`, worktree `/Volumes/JW-EXT/jw-wt/b6-paper-fills` (read only). Own checks by `git show`, `python3 json`, `gh pr view`; no fill-seat code.

Rows checked: 12. Agree: 12. Disagree: 0.

| Row | Source value | Printed | Result |
|---|---|---|---|
| Block 5 release time | SEAL_RECORD.md at `fd43dcdf4`, "### Recorded late (2026-11-13)": "Ed's unseal OK ... given on 2026-11-08 at 11:17 PST" (RUN_STATE item 231) | 8 November 2026 at 11:17 PST | agree |
| Block 5 output digest | same section: `c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc`; record appears once in the file | `c06ee7c8…` | agree |
| Date the seal-record clause was written | `fd43dcdf4` = merge of PR #773, committer 2026-11-13 19:56:24 PST; `gh` mergedAt 2026-11-14T03:56:24Z (= 19:56:24 PST on 13 Nov); the section itself says "written on 2026-11-13" | 13 November 2026 | agree |
| registration digest | release_record.md and .json `registration_sha256` `7243a2bc1e43207d756ba9eacc6c93622968edd73a6ebe0648afaba563324ead` | `7243a2bc…` | agree |
| catalog digest | `b5bce6c64bbc1d079ecf6fed02bf4c214b76a8f7d279d44eea5984e4a389a42b` | `b5bce6c6…` | agree |
| manifest digest | `b2901d51990812f6c2dadce1a763d90502d85b58a9d5b5b358d4cbb2ba9a9d6b` | `b2901d51…` | agree |
| restricted digest | `outputs_sha256.dry.restricted` `92e67c389bb71813d1e57b962e98eb6dcacf65d2bc3957332a36881c821c14bb` | `92e67c38…` | agree |
| public digest | `outputs_sha256.dry.public` `c2b5c4098f70dd3a5be19edb3016bf682588d5529f21c41abf05d125fe8107f8` | `c2b5c409…` | agree |
| harvest digests count | `harvest_sha256` in the .json has 9 entries (r1/r3/r4-alpha, r1/r2/r3-beta, r1/r2/r3-gamma archives); the .md Sessions table lists them | nine | agree |
| merge commit | `git log` / `gh`: PR #769 mergeCommit `66469ccf4d575e770b6a72de0d670105bbd95124` | `66469ccf4` | agree |
| release time | RUN_STATE.md item 312 (on main `fd43dcdf4`): "merged to `main` at 2026-11-13 18:54:57 PST (merge commit `66469ccf4d5...`" | 13 November 2026 at 18:54:57 PST | agree |
| commit-object time (not printed) | `git show -s --format=%cI 66469ccf4` = 2026-11-13T18:54:56-08:00 (author and committer the same) | not printed | agree with the manifest row |

Also read in the filled paragraph (paper1.md, "The primary block was released on 8 November 2026 at 11:17 PST ... replication block was released on 13 November 2026 at 18:54:57 PST ..."): every digest and date matches the rows above. The sentence "The record of that event was written into the seal record on 13 November 2026" is supported by the section's own header and by PR #773's merge date. `{{FILL: P1-RELEASE-BYTES ...}}` remains a placeholder, as ruled.

## The 18:54:56 vs 18:54:57 question
- GitHub `mergedAt` for PR #769: 2026-11-14T02:54:57Z = 18:54:57 PST (13 Nov).
- Merge commit `66469ccf4` object (committer and author): 18:54:56 PST, one second earlier than mergedAt.
- Printed: 18:54:57 PST, with "when its release record was merged into `main`". This agrees with GitHub's mergedAt and with RUN_STATE item 312, not with the commit object. The one-second difference is the commit being created before GitHub records the merge as complete; it does not change the date or the minute. If the paper wants the commit object's own time it would say 18:54:56; the printed event ("merged into main") is the GitHub event, so 18:54:57 is the defensible stamp. No disagreement.
- PR #773: commit 19:56:24 PST and mergedAt 03:56:24Z (19:56:24 PST) coincide. In UTC this merge falls on 14 November; the paper prints 13 November (PST, the same convention as everywhere else in the paper).

## Disagreements
None.

## Not checked
- The seal-record section's other digests (harvest records, section 4 tie table); only the released-output digest and the event time were in the delta.
- RUN_STATE item 231's own text (read only through the seal record's quote of it).

## Update (research lead ruling: release time is the merge commit object's time)
Checked at 20:07 PST on head `c5e7fe38e`. Commit object `66469ccf4` committer time is 2026-11-13T18:54:56-08:00. The paper at this head still prints 18:54:57 PST, so that row is: expected to change to 18:54:56; it is not yet agreeing with the commit object. Awaiting re-check of that one value on the new head. The other 11 rows are unaffected.

## Final re-check on head 35fc4e038 (Fri Nov 13 20:07 PST 2026, from `date`)
- Printed: "released on 13 November 2026 at 18:54:56 PST". Commit object `66469ccf4` committer time in PST: 2026-11-13 18:54:56. Agree.
- `git diff c5e7fe38e 35fc4e038 -- paper1.md`: one changed line (the P1-RELEASE paragraph); a word-level diff shows the only change is `18:54:57` -> `18:54:56`. No other P1-RELEASE text changed.
- `18:54:57` occurs 0 times in paper1.md.
- The delta manifest `fill_keys_b6_delta_release.tsv` now has 11 data rows (the RUN_STATE item 312 row is gone; the time row now reads the commit's committer time). The other 10 rows are as I checked them above and are unchanged in the manifest.
- Final count: 11 rows checked, 11 agree, 0 disagree.
