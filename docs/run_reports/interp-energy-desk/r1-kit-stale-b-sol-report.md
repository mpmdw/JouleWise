Committed `5e9b9b480` on `ops/2026-11-11-r1-kit-stale-b`. Worktree clean; not pushed.

Applied the six cited expectation updates and corrected `FakeWorld` across the three authorized test files. Production, condition-13 files, coordination state, and the missing-timeout witness remain unchanged.

Ran `python3.13 -B -m unittest <module>` sequentially:

| Module under `tests.align` | Result |
|---|---|
| `test_r1_round7_science` | 18 pass |
| `test_r1_round8` | 16 pass; 5 baseline sandbox failures |
| `test_r1_rehearsal` | 77 pass |
| `test_r1_followup` | 12 pass |
| `test_r1_round3` | 8 pass |
| `test_r1_round4` | 10 pass |

Remaining failures show `sysmond service not found`, `pgrep: Cannot get process list`, or `PermissionError: [Errno 1] Operation not permitted: '/bin/ps'`. The lead must rerun round 8 outside this sandbox; its native result remains unverified.

The [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-r1-kit-stale-b/docs/run_reports/2026-11-11-r1-kit-stale-b.md) records each red→green change, exact failures, and the RL-59 read-scope caveat: surrounding prior-night narrative appeared in a documentation excerpt; no underlying measurement or custody files were opened.