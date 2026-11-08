Committed locally on `perf/2026-11-08-fix-wake`:

- `2944e1fbd` — terminal-wake fixes and tests
- `5f851edb9` — handoff report

| Finding | Result |
|---|---|
| W-M1 | Marker waits for confirmed driver exit; witness passes. |
| W-L1 | Retries coalesce before one ordinary tick. |
| W-L2 | Installed custody-root mismatch refuses loudly. |
| W-L3 | No-courier/dead-man polling fallback documented and tested. |
| T-L1 | Temporary paths resolve correctly through symlinked TMPDIR. |

Validation: **461 passed, 3 skipped**; compile and diff checks passed. The mutation test correctly failed. Total recorded test runtime was about 7.7 minutes.

Changed wake/installer code, seven test modules, terminal-wake documentation and the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-fix-wake/docs/run_reports/2026-11-08-fix-wake.md), which lists exact commands and the initial test-overlap deviation.

Native launchd checks and three process-census tests remain. The orphan census was blocked by sandbox `ps` permissions. Pre-arm remains parked; 300 s fallback remains; no window was armed. Worktree clean; nothing pushed.