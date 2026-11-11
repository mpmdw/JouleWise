Committed `61ab3c1df` on `design/2026-11-11-slow-sensor-rule-sol`. Clean worktree; not pushed.

[Sol design report](/Volumes/JW-EXT/jw-wt/sol-slowsensor-sol/docs/run_reports/2026-11-11-slow-sensor-rule-design-sol.md) covers all options, deviation text, smoke criteria and quantified replays. Four files added: report, replay script, manifest and tests.

Validation: 24 targeted tests passed; all 13 recorded gate outcomes reproduced; W1 gate bytes unchanged.

Key warning: Tf08’s replayed G0 waits alone exceed the most generous duty allowance if they recur. Native D evidence remains necessary.

The report discloses unintended exposure to unrelated Block 5 audit prose.

**Open questions for the research lead:** exposure acceptability, slow-role policy, and record-only collection.