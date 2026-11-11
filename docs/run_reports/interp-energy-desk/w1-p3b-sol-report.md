Stopped under condition (a). Exactly three missing argv vectors were confirmed, but:

- The dynamic inventory also contains unrelated `run_night` → `_run_night` changes.
- Qualification cleanup reaches the network-time getter. Source tracing and a synthetic cleanup reproduction confirm this, so condition (b) cannot pass unchanged.

`python3.13 -B -m unittest tests.test_v5_block4_x12b`: **11 tests, 201.861s, two failures**. No green run or mutant proof was claimed.

Only the [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-w1-p3b/docs/run_reports/2026-11-11-w1-p3-qualification.md) changed, committed as `8b7ffb7ab`. Worktree clean; nothing pushed.

**NEEDS_RULING:** Should the brief authorize the separate inventory repair and revise the getter classification, or remain blocked? I recommend revising the brief; the reachable getter cannot honestly receive the proposed exception.