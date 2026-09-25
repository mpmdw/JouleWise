ROLE: DELTA re-audit (read-only review) for JouleWise lane A291, fix round 1 after stage I1. Independent reviewer; you did not write this code. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-a291rev, detached at 20cd29de. The fix round is `git diff 01badd6a 20cd29de`, and stage I1 is `git diff b8962fd0 ef1c5e48`. Read-only in the repository; scratch only under /tmp. Fences: never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise.
Records (read-only) at /Users/edr/code/wt-a65fb4fa-bk/docs/process_traces/2026-09-24-activation-a65fb4fa/: 45 fix brief (F1-F4), 46 fix report, 37/43/44 checker lens, fix and delta, 36 I1 report. Contract: 02d and 31 in the worktree's copy of that directory.

1. TASKS (execute; do not just read):
   D1. F1-F4: FIXED / PARTLY / NOT FIXED / FIX INTRODUCED A NEW DEFECT, with executed evidence. Recompute the lens-37 R2 planned lever (6.2) and a partly counted parent's executed lever by hand, and via both the packer and the checker.
   D2. New defects anywhere in the fix diff, especially: `_live` now keys on the placement's own envelope (can two placements of one block both be live? can a block have none while not terminal?); the planned-null rule (`first_count and second_count` uses non-terminal counts while `pos` may be empty or non-empty independently; can this divide by zero, or give a lever from partial positions where 02d says null?); and spread counting.
   D3. The seal's "trusted outputs" cache (`_TRUSTED_OUTPUTS`, used at requeue entry to skip the full replay for rosters this process just produced): can a caller get a roster past requeue entry that the ruled seal-plus-replay would refuse? Try mutating a returned roster in place and re-submitting; try two registrations; try the deque's eviction.
   D4. Stress diversity: the two seeds give near-identical edge counts. Find why and state what a diverse generator needs.
   D5. Same-signature statement: does any finding repeat the class "a derived quantity misreads which placements or parents count"? YES or NO.
   Named tests only: tests.test_scored_registration tests.test_scored_packer tests.test_scored_packer_stress tests.test_scored_roster_checker.

2. ACCEPTANCE. Review genre; severity BLOCKER / SHOULD-FIX / NIT with file:line and executed evidence. Body under about 300 lines; JSON header under 8 KB. End your turn only when D1-D5 are answered.
