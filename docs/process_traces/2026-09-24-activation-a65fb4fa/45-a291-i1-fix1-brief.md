ROLE: implementation seat, A291 fix round 1 after stage I1. Execution seat and design peer; the magistrate reviews. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: ["joulewise/scored_packer.py", "tests/test_scored_packer.py", "tests/test_scored_packer_stress.py"]

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-a291, branch feat/2026-09-24-a291-packer-recut at 01badd6a. It carries your I1 implementation (ef1c5e48) and the independent checker's fix round 1 (01badd6a, cherry-picked from b8fae7b3). That fix cured two checker defects an independent Opus lens found, one of which you also found (the voided first placement in check_executed). You may not edit the checker. Do not commit. Fences: never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise.
Records (read-only) are at /Users/edr/code/wt-a65fb4fa-bk/docs/process_traces/2026-09-24-activation-a65fb4fa/: 37 (checker lens: B1 planned lever, B2 live placement, M1 executed lever), 43 (checker fix report), 44 (checker delta). Contract: 02d and 31 in your worktree's copy of the same directory.

1. FINDING (magistrate, executed). With the fixed checker, `python3 -B -m unittest tests.test_scored_packer_stress` fails at case 6, call 13: INV-27 "stale planned drift", then INV-38 digest mismatches. Cause: `_derived` (joulewise/scored_packer.py about :97) gives a parent a planned position only when EVERY item has a live placement (`len(indices) == len(parent["items"])`), which drops partly terminal split parents. This is the same misreading as checker B1.

2. CLAUSES.
   F1. Planned position per 02d as installed from RD-4 (record 25) and 31 X-4: the item-weighted mean of the envelope indices of the LIVE, non-terminal placements holding a parent's items (for a split parent, its live singles). A parent with no such placement has no position. The spread shortfall count stays separate and follows RD-5: a non-terminal parent is one none of whose items is terminal, and it occupies its and its singles' LIVE placements only. Keep the float evaluation order of 31 X-4.
   F2. Audit `executed_status` against the checker lens M1 and fixed-checker semantics: the executed lever positions a parent with ANY counted window (45/10 §Q4, 31 X-5), spread requires every item counted, and the live placement is the latest non-voided one. Fix it if it differs; say so if it already matches.
   F3. Regressions: the lens-37 R2 roster (planned lever 6.2 by 02d arithmetic; show it), a partly counted parent's executed lever, and your earlier `test_checker_executed_voided_attempt_counterexample`, now asserting agreement with the fixed checker.
   F4. Stress: keep seed 291013, and add a second seed, both at least 300 registrations. Zero checker violations. Report the edge-hit table for both seeds.

3. ACCEPTANCE: `python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_packer_stress tests.test_scored_roster_checker tests.test_git_fixture_maintenance` passes. NEVER `unittest discover`. `git status --porcelain` shows only WRITE_SCOPE paths. End your turn only after acceptance has run; if you find another checker disagreement, report it with a counter-example and do not work around it.

4. EVIDENCE DEMANDED (markdown body): F1–F4 mapped to file:line and tests; both edge-hit tables; the test command and its result tail; "what the magistrate should double-check". Implementation-genre verdict keys only; JSON header under 8 KB.
