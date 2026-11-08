Committed on `engine-r23e`: `b5bd465b044353c4758d79734d32cfe33ab1a542`. Working tree clean; not pushed.

- Re-derived X2 reaches screening, U checks, fits and calibration; W1 hand test gives K=10 and `excluded:X2`.
- Exact time conversion gives 954 ns; larger gaps remain uncovered and exclude members.
- C-sabotage member output is hash/status only, including token counts.

200 targeted synthetic tests passed, plus compileall and diff checks. Full suite deliberately unrun. One brief test-process overlap is disclosed; final reruns were sequential.

Updated `ENGINE-sol.md`. [Run report with files and test commands](docs/run_reports/2026-11-08-engine-r23e.md).

No open questions. Lead next step: regenerate freezes and run the independent synthetic rehearsal. No new MLX native test is needed; live hardware remains unvalidated.