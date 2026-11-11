**STOP: one real defect.** Commit `a85ee8ec6` moved bound calculation outside the refusal handler. Missing `g0_timeout_s` now causes exit 1 with a traceback and no result record. The other six failures are stale expectations.

Only the [run report](/Volumes/JW-EXT/jw-wt/sol-r1-kit-stale/docs/run_reports/2026-11-11-r1-kit-stale.md) changed, committed locally as `caabfc75e` on `ops/2026-11-11-r1-kit-stale`. Tests and all ten condition-13 files remain unchanged. Working tree clean; no push.

Both requested modules ran twice, sequentially:

- Round 7: 18 tests, 4 failures and 2 errors.
- Round 8: 21 tests, 6 failures, including five additional process-proof failures consistent with sandbox restrictions.

`nice` reported permission denied, so priority 10 was unverified. The lead must resolve the preflight refusal defect before test updates resume.