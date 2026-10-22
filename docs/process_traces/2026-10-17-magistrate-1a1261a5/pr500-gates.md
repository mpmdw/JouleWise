# PR #500 gates (watchdog reads block-6 night plans)

Lead: magistrate activation 1a1261a5 (Opus 5.5), 2026-10-17.

## Commits

| Commit | Author | What |
|---|---|---|
| 42ebf400c | lead (e761d241) | Port the lane's validator hunk: accept the two optional block-6 bindings |
| 5f4620d71 | lead (e761d241) | Port the lane's three refusal-allowlist rows (review r1 BLOCKER-1) |
| ddef54e5d, fa0cb735c | Sol 6.1 xhigh (Codex Cloud) | Installed night plists feed `load_plans`, so a running magistrate gets REQUEST/TERM/KILL for a block-6 plan the custody scan cannot see (review r1 MAJOR-1) |
| ed665952e | lead | Test: mocked Storage lists an empty LaunchAgents directory (CI quick failure) |
| 8d3fbdc94 | lead | Test: the fence names each (plan id, plan path) once (CI shards failed on the doubled string) |
| 6d014015b | lead | Any content fault in an installed plist holds and drains (review r2 MINOR-1) |
| 374509f83 | lead | Refusal rows for the widened catch; watchdog doc decision order (r2 NIT-2, NIT-3) |
| 8498a7802 | lead | Test: drop a subtest that exercised nothing (r2 NIT-4) |

## Row 1: independent executing review

- Round 1 on 42ebf400c: `pr500-review-r1.md` (Opus 5.5, not an author), REQUEST-CHANGES.
- Round 2 on ed665952e, 8d3fbdc94 and the delta 374509f83: `pr500-review-r2.md` (Opus 5.5, not an author of any reviewed commit). Final verdict APPROVE-WITH-NITS once CI is green. It ran MAJOR-1's scenario on a real block-6 plan layout (REQUEST at t0-180 s, TERM at t0-90 s, KILL at t0-60 s, Python 3.13 and 3.14), replayed 392 readable v2/v5 plans on disk (11,762 decisions identical to main), and read the real LaunchAgents directory read-only (no plans, no errors; the magistrate and machine-test plists are not read).

## Row 2: whole suite on the merged tree

CI runs the whole suite in 12 shards on GitHub's merge of this head into main (Ed 2026-10-16: seats run touched modules, CI runs the suite). Evidence is the final head's CI run, row 3.

## Row 4

No measurement, calibration or claim code: the watchdog only decides when the magistrate session may run and when it must stop.

## Row 5: dispositions

| Finding | Disposition |
|---|---|
| r1 BLOCKER-1 (allowlist rows) | Fixed, 5f4620d71 |
| r1 MAJOR-1 (no stand-down for an installed-only block-6 plan) | Fixed, ddef54e5d; verified by r2 |
| r2 BLOCKER-1 (CI red, doubled fence string) | Fixed, 8d3fbdc94 |
| r2 MINOR-1 (malformed `<date>` or deep nesting escaped `load_plans`) | Fixed, 6d014015b; r2 delta: the new test fails on 8d3fbdc94 and passes on the head |
| r2 NIT-1 (if t0 is unknown, the fallback drain TERMs at 540 s and KILLs at 600 s) | Deferred to the block-6 watchdog follow-up lane, named in RUN_STATE. It needs a plist that names an unreadable plan and no readable sibling, which the installer cannot write |
| r2 NIT-2 (record the intended changes) | Fixed: the PR body and the watchdog doc say that a torn plist drains a running session and that a STOP during an installed plan's window reports the span's state |
| r2 NIT-3 (stale doc; `installed_agent_fence` used only by tests) | Fixed, 374509f83: the doc is rewritten; the function is kept as a labelled test helper |
| r2 NIT-4 (deep-XML subtest exercised nothing) | Fixed, 8498a7802 |
