# PR #764 cold check (research lead, Fable 5.2)

Checked 2026-11-13 16:54 PST (`date`). Head `6c26c8751dbd83451a4ac2839e02fec63b6770e5`, branch
`docs/2026-11-13-b6-r2-records`, read as `git diff origin/main...HEAD` in `/Volumes/JW-EXT/jw-wt/b6-r2-records`
(no fetch, so `origin/main` is the local ref). Read only; no test run; no run-directory file opened.

**Verdict: ADMIT.** No fixes.

The diff is 2 files, 17 insertions, 1 deletion.

## 1. §17-R13 (`docs/registrations/block6_replication_DRAFT.md`)

- The 15 added lines equal RL-142 §4 (`fable-rl142-dry-hold.md`) byte for byte (`cmp`), with the one
  `<r2 sha256>` replaced by `4a9f594471652581737b6cd02bd2922592f2e7cf9d575a164adb10162a5211ea`.
- Placement: line 1533, directly after §17-S16 (line 1532), as the last entry of §17. Same list format as its
  neighbours (`- 2026-11-13, §17-… **Kind.**`, two-space continuation). No line removed. The file ends in a newline.
- Cosmetic only: the digest line runs past the wrap width. That follows from the verbatim rule; leave it.

## 2. Addendum (`docs/registrations/block6_freeze_by_commit_addendum.md`)

- New `b6/analysis-r2` row equals the records file §D1 template string for string, with the three values filled.
- The `b6/analysis` row keeps its text and gains exactly the §D1 revision clause in the Status cell.
- Values checked with `git rev-parse` in `/Volumes/JW-EXT/jw-wt/rl129-s14-merge`: tag object
  `e11a600328e45d067c732c039c309c4a024f85f9`, commit `6e6d1b18a9dffbba675c3abd28db2e4c6a484fde`, tree
  `726501c9d0a421abcc341f0e0cfe7140cb811300`. All three match the row.

## 3. "No other printed value changes, shown by a names-only comparison of the two dry runs"

Supported. `rl142-cmp-b.json` (sha256 `8b805e8e…e6eb`): mode b, `dry` against `dry-r2`, verdict PASS, exit 0,
176 differing paths, 0 unowned, no extra files, `inputs_rerun` false; `comparer_sha256` in the file and the file on
disk are both `eb82b6e25a9dc9a3cffcb4d2e859a19c2f2151a42ce3b4a98f2ea188887e02c1`.

I read the 176 path names myself rather than relying on the verdict:

- Every differing quantity path (84: between-session 16, flagged-inclusive 16, side-by-side 24, comparison table
  28) is under `lines/whole_machine/` for ALPHA `qwen3-1p7b` or BETA `qwen3-8b`, decode or `prefill-p2048`. The
  fields are `n`, `mean`, `sd`, `block5_included`, `block5`, `block5_label`, `delta` and three `session_deltas`
  per quantity. That is the list the line gives. No GAMMA path and no path outside the four quantities differs.
- The other 92 paths are not quantity values: the comparison's own verdict and tallies (failures 0 to 7 removed,
  side_by_side passed/failed/pass, `option_c` pass, `comparison_stopped`, exit code and status), the
  `option_c_disagrees` flag and the flag counts that follow from it (public `flag_count`, 9 session
  `restricted_flag_count`, stdout `flags`), `block5_included` for ALPHA and BETA, the program digest and commit,
  output digests, and run bookkeeping (times, argv, paths, three hash-only process files).

The path names agree with the lead's counts where names can show it: 8 failure entries removed, 9 sessions with a
changed `restricted_flag_count`, the flag removed once in each of restricted and structure, side_by_side tallies
and term-7 `side_by_side/passed` changed, `block5_included` changed for ALPHA and BETA only. The numeric deltas
themselves (−9, +4/−4, 8→0, 20→22) are the lead's reading; the result file holds names only and I did not open the
run directories.

## Note (no action for this PR)

The line's "Changed outputs" sentence lists the four quantities' values. The flag, failure and tally changes are
the removal of the disagreement the line's first sentence reports, so the line is accurate as written and stays
verbatim. If a reader later asks why `flag_count` differs between the two dry runs, the answer is in
`rl142-cmp-b.json` rules R-OCD, R-OCD-N, R-FL and R-CT.
