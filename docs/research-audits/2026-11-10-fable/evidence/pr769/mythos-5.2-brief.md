# Cold audit: Block 6 release record, PR #769 (Mythos 5.2, read-only)

You are an independent cold auditor for JouleWise, a blind energy-measurement study. Merging PR #769 to `main` IS the
release event: it unblinds Block 6. Your job: decide whether the record is correct and complete and whether every
precondition is truly met, so the merge may proceed. Audit adversarially; trust nothing you are told, verify from files.
Nobody gives you a prior verdict on purpose.

## BLINDING — absolute (violating this ruins the study)
Do NOT open, cat, head, grep, or otherwise read the CONTENT of: any `restricted.json`; any `stdout` or `stderr` file;
anything under `/Volumes/JW-EXT/b6-custody/` (the $ROOT custody tree); any `analysis-tmp`. You MAY `shasum -a 256` those
files (digest checks are part of the release check) and `ls` directories. You MAY read `public.json`, `structure.json`,
`record.json`, `process.json`, `child-argv.json`, `time`, and the top-level JSON files in `/Volumes/JW-EXT/b6-custody-run/`
other than those excluded. If you are unsure whether a file is outcome-bearing, do not read it; note it instead.

## Read-only
Do not edit, commit, push, comment on GitHub, or run the analysis programs. Write ONLY your report.

## Material
- The record under audit: worktree `/Volumes/JW-EXT/jw-wt/b6-release-record` (branch docs/2026-11-13-b6-release-record,
  head 2d8a8ee7b): `docs/registrations/block6_release_record.md` and `.json`. Rendered by
  `/Volumes/JW-EXT/jw-wt/b6-real-run/scripts/b6_release_record.py` from `/Volumes/JW-EXT/b6-custody-run/release-record-draft.json`
  against main 76a6eba99. `gh pr view 769 --repo mpmdw/JouleWise` and `gh pr diff 769` are fine.
- The registration: `docs/registrations/block6_replication_DRAFT.md` in that worktree (§12.3, §17 entries incl. §17-R13).
- The governing ruling RL-134 and the runbook: `/Volumes/JW-EXT/scratch/fable-b6-post-pin-runbook.md` (steps 0-12, and
  "## 3. RL-134" sections 1-18). Step 12's "What" row lists everything the record must tie.
- Records of the r2 gate/dry/release-check: `/Volumes/JW-EXT/scratch/rl142-r2-records.md` (§F-§G), event logs
  `/Volumes/JW-EXT/scratch/b6-gate-r2.events`, `b6-dry-r2.events`, `b6-release-check-r2.events`, `b6-*-r2*.out`, `b6-*-probe.out`,
  launch scripts `b6-*-r2-launch.zsh`, `b6-release-check-r2.zsh`.
- Run directory: `/Volumes/JW-EXT/b6-custody-run/` (attempts.jsonl, b5-probe-r2.json, mapping*.json, run-inputs-*.json,
  verify-receipt-release.json, gate-r2/, dry-r2/ — note r1 dirs `dry/`, `gate/`, `gate-2/` are superseded attempts).
- RUN_STATE.md on origin/main (items 309, 310) for Ed's OK and the RL-6 (d) tier call. Git history is fair game.

## Questions
1. Does the record tie every item step 12 requires (registration SHA-256 at the named main commit; catalog; nine
   harvest_sha256; S-14 commit/tag/24 hashes; MSHA, receipt digests, D_block, D_gate, B5SHA; restricted+public output
   digests of gate and dry run; Python/zstd versions; attempts ledger; eleven conditions with evidence; "L9 audit: not
   run"; signing statement)? Recompute every digest you can (shasum on the actual files / `git show <commit>:<path> | shasum`).
2. Is the registration hash still valid against current origin/main (has anything touched block6_replication_DRAFT.md
   after 76a6eba99)? Would merging now leave the record true?
3. Are the r2 gate, dry run, probe/term-7 check and release check really PASS per RL-134's own definitions (exit codes,
   stop flags, attempts ledger completeness incl. r1 attempts, budgets)? Any condition asserted without evidence?
4. Anything in RL-134 sections 1-18 that should have happened before release and did not?
5. Anything else that would make you refuse the merge.

## Output
Write `/Volumes/JW-EXT/scratch/mythos-audit-769/REPORT.md`: verdict first (ADMIT / ADMIT WITH FIXES / REFUSE), then
numbered findings, each with severity (blocking / should-fix / note), the evidence (file:line or command + output),
and what would fix it. Then a list of what you verified and how, and a list of what you could not verify. Add a final
line confirming you opened no blinded content.
