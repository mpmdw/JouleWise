# PR #484 gates (magistrate watchdog: no network call during a plan span), desk-day v5 seat 3

- Finding: Opus pre-mortem memo §3.M. The watchdog tick (every 300 s) made two HTTPS `git ls-remote` calls before it checked for an active plan, so they ran during measured windows.
- Round 1, report [122-sol-watchdog-report-r1.md](122-sol-watchdog-report-r1.md): returned early from the whole tick during a span. The lead found this too broad: it also deferred supervisor recovery and A212's zero-capture refusal release.
- Round 2 (brief 128), report [128-sol-watchdog-report-r2.md](128-sol-watchdog-report-r2.md), at c53b9d39: only the probe is skipped (`NOT_PROBED`); everything else is as at baseline.
- Executing review [129-sol-wd-review.md](129-sol-wd-review.md): FAIL.
  - F1: the resident refresh ignored the installed-agent fence.
  - F2: a refresh in flight made its second call at span start.
- Round 3 (brief 130), report [130-sol-watchdog-report-r3.md](130-sol-watchdog-report-r3.md), at d68c0e28: F1 and F2 fixed, with regression tests that fail at c53b9d39.
- Delta review [131-sol-wd-delta-review.md](131-sol-wd-delta-review.md): FAIL.
  - F3: time was sampled before the guard's file reads.
  - F4: a torn installed plist turned ACTIVE into NETWORK_UNCERTAIN plus a notice.
- Round 4, lead, at 2f759c48: the reviewer's counterfactual edits, plus two regression tests that fail without the fix.
- Delta review [133-sol-wd-delta2-review.md](133-sol-wd-delta2-review.md): FAIL.
  - F3': the same race during installed-plist reads.
  - F5: the suppressed refresh renewed the cached timestamp.
- Round 5, lead, at 488ec8b7: F5 fixed with the reviewer's counterfactual edit, plus a regression test that fails without the fix. The reviewer's own F5 probes (`probe_error_cache_timestamp`, `probe_error_restart_cadence`) pass at the head.

Dispositions:
- F1, F2, F4, F5: FIXED.
- F3: fixed for the plan read (round 4).
- F3': REJECTED, with this reason. The span opens at t0 − 480 s, and no energy capture starts before the T-0 stage's 600 s clean dwell has passed. A probe admitted at the opening instant finishes within its 2 × 10 s timeouts, more than 17 minutes before any capture, so it cannot touch a measured member. The same defect class (sub-millisecond boundary races) came back a third time. Under the round-limit rule, the lead closes it here rather than spending a fourth round.

Whole suite, CI shard method, at 2f759c48 (main e7d13a17 merged). Round 5 changes one line of `scripts/magistrate_watchdog.py`; the watchdog and AXI modules were rerun at 488ec8b7 (176 tests OK).
- SHARD SUMMARY index=1/6 modules=1 tests=74 failures=0 errors=0 skipped=1 result=PASS
- SHARD SUMMARY index=2/6 modules=56 tests=1330 failures=0 errors=0 skipped=5 result=PASS
- SHARD SUMMARY index=3/6 modules=57 tests=1747 failures=8 errors=0 skipped=19 result=FAIL
- SHARD SUMMARY index=4/6 modules=57 tests=1752 failures=3 errors=0 skipped=7 result=FAIL
- SHARD SUMMARY index=5/6 modules=58 tests=1199 failures=4 errors=0 skipped=8 result=FAIL
- SHARD SUMMARY index=6/6 modules=57 tests=1550 failures=38 errors=0 skipped=3 result=FAIL
- Exclusives: calibration exits 48 OK; writer crash matrix 20 OK.

All 53 failures are local-environment failures already present on main:
- 52 are in the base list (`base-failures-8fa002f7.txt`);
- `test_installer_refuses_outside_a_listed_install_span` (stale live battery reading) fails in every main-based suite since #482 (suite-dp, dp2, dt, rg2, ct2).

Zero new failures. Hosted CI on the final head is the merged-tree whole-suite run. No cold Fable pass: the watchdog is orchestration code, not measurement, calibration or claim code.
