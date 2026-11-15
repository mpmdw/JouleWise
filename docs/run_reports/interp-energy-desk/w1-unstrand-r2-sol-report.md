Applied U-1–U-4 on `ops/2026-11-11-w1-unstrand-r2`: numbered retry records capped at 20, absent-job retry coverage, driver-matching success checks, and distinct ownership refusal.

Changed only the script, its tests, and the [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-w1-unstrand-r2/docs/run_reports/2026-11-11-w1-unstrand.md:233).

Local commits: `145860528` tests, `1f9306450` fix, `556ce3e5e` report. Working tree clean; nothing pushed.

- Nine review-focused tests passed.
- Changed module: 54 passed, one unchanged follower failure, two native-process skips.
- All 36 closure/registration tests passed.
- Syntax and diff checks passed.

Next: lead review and remote native retry/ownership checks. No implementation questions remain.

Intake caveat: an overly broad audit read exposed unrelated Block 5 discussion. No custody files were opened; the report records this error.