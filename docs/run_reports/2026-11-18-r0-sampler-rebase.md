# R0 background sampler rebase

Register 10 · Tier 2 · 2026-11-18

The candidate starts at the admitted R0-L3 lane, `9c40e4e5d9fa453cce3c70984e11fa382b7d4591`. It ports the seven-path delta between common ancestor `5f817856b33f65b269a44ea52811dbbed28d02a8` and draft head `d7b27961f809f3b2accba3a19194fb5a28cda7a9`. Both remote refs matched before branching. The lead cleared the detached checkout's divergence and directed a new branch from the verified target. [PR #694](https://github.com/mpmdw/JouleWise/pull/694) · [PR #699](https://github.com/mpmdw/JouleWise/pull/699)

## Sampler and runner

The caller waits for the initial 30-second baseline with a midpoint snapshot. During caller gaps, the daemon takes process snapshots and repeats the census. The next check evaluates the queued windows in order from the latest eligible opening snapshot. Each valid busy window keeps its own R0-L3 flag and interval bounds. An excessive interval, a stale sampler or a failed background census still latches a refusal. The flags already recorded before a refusal remain in the check receipt. The admitted guard's previous-interval exit and regressed-counter evidence also carries forward.

The advisory forecast and host aggregate disclosures feed the reports. The R0-L3 SMC redo, display census, and runner summaries matched the target's function ASTs. Both runner exit paths close the sampler, including an inventory exception. The changed paths are four implementation files, their three test files, and this report.

## Frozen tests and dispositions

Spec freeze `cb341a7936c55ce388c94c2f2a28d33ce7ba0651` recorded six failing tests (eight failing cases including subtests) against the target. The repair is `4e8b0ac816fdeacee7a6de4b543d95ceb0673ee0`. An in-memory restoration of the busy-window break failed both the queued excessive-interval and later-census regressions. Restoring fatal contention separately failed the later-census regression.

| Finding or contract case | Repair | Regression test | Final |
| --- | --- | --- | --- |
| Item 209 / PR #699 Opus MED, integration seam. Early busy window can suppress a later excessive interval or healthy census. | `4e8b0ac81` | `test_early_busy_window_cannot_mask_a_queued_excessive_interval`, `test_early_busy_window_allows_later_windows_and_their_censuses` | PASS |
| Runner receipt must retain the early flag when a later check refuses. | `4e8b0ac81` | `test_execute_reports_guard_flag_before_a_later_refusal` | PASS |
| Busy window must leave the sampler running and later census failures and stalls enforceable. | `4e8b0ac81` | `test_invalid_background_census_still_refuses_after_contention`, `test_stalled_sampler_still_refuses_after_contention` | PASS |
| Caller gap with a busy window, plus a quiet control. | `4e8b0ac81` | `test_caller_gap_retains_contention_and_quiet_control`, `test_300_second_caller_gap_daemon_thread_flags_60_second_contender` | PASS |

The prior PR #694 Fable review applied to its earlier head. Its repairs were replayed and rechecked here. [Prior review](https://github.com/mpmdw/JouleWise/pull/694#issuecomment-6709699992)

| Prior finding | Original repair | Rebase regression test | Final |
| --- | --- | --- | --- |
| MED-1, admission-boundary dilution | `0fd122410` | `test_burst_straddling_the_admission_end_is_judged_in_a_30_second_window` | PASS |
| MED-2 and LOW-3, interval and stall bounds | `0fd122410` | `test_window_longer_than_interval_plus_cadence_and_margin_refuses`, `test_stalled_sampler_refuses` | PASS |
| MED-3, background census evidence | `0fd122410` | `test_background_census_summary_is_receipted_per_cycle` | PASS |
| LOW-1, disclosure of between-snapshot activity | `4182378a1` | `test_host_aggregate_is_flagged_but_never_judged`, `test_report_counts_guard_windows_with_host_aggregate_above_limit` | PASS |
| LOW-2, inventory must close the daemon | `4182378a1` | `test_inventory_mode_closes_the_guard` on success and error | PASS |
| LOW-4, bounded forecast read | `0fd122410` | `test_softwareupdate_forecast_reads_only_a_bounded_tail`, `test_softwareupdate_scan_forecast_is_reported_and_never_refuses` | PASS |

## Verification and handoff

The focused suite covered `tests.align.test_r0_host`, `tests.align.test_r0_checks`, `tests.hazards.test_contention`, `tests.align.test_smc_classifier_v4`, `tests.align.test_smc_quiet` and `tests.hazards.test_smc_enumeration`. It passed 241 tests with four skips under synthetic inputs and host-command fakes. The harness rejected unexpected commands and signals. The inventory boundary test used a fake directory entry after local filesystem policy blocked creating its sentinel directory.

The draft PR carries the exact candidate SHA and the repository sharded CI run. The lead routes the Tier 2 delta to one executing reviewer from each family. Integration owner acceptance and lead acceptance remain pending. The integration owner determines where to carry the admitted bytes. Future first-native evidence follows RL-179 F-11 and the applicable pin-change requirements. NEEDS_SPEC has no entries.

## Delta audit round 1

Round 1 reviewed `cde215aff2def5b80b0f76bc26a5730279d8664c`. It verified one HIGH and one MED, both implementation bugs in consuming sampler state. The original frozen spec stays at `cb341a793`. The new regressions produced seven failing cases on the reviewed head and pass on repair `0ecd9c5121869b59d33ed7cc5501a31dfc86d162`.

| Verified finding | Repair | Regression | Final |
| --- | --- | --- | --- |
| HIGH, a late failed census could let the report pass or let the inventory publish. | Bounded sampler shutdown and final drain precede both success paths. A sampler still running at the join bound refuses. The final report records the refusal on the last check. | `test_execute_refuses_census_failure_during_final_check`, `test_execute_finishes_inflight_census_before_publishing`, `test_inventory_refuses_census_failure_at_eof` | PASS |
| MED, a failed census or stale sampler could discard a queued contention flag. | Drain completed windows in order before applying the later failure or freshness refusal. Publish each background snapshot with its census evidence. | `test_queued_contention_survives_census_failure_or_stall` | PASS |

Both threaded regressions passed 20 consecutive synthetic fixture runs. The existing sharded CI blocker in `tests/test_agent_identity.py` remains with the CI owner. The draft records hosted CI for the repaired candidate and requests the follow-up delta review. [CI-owner issue #834](https://github.com/mpmdw/JouleWise/issues/834)

## Delta audit round 2 and spec v2

Round 2 reviewed `71e6122a83090181e0de5806765ff9c57d62c28a`. It verified one HIGH and one MED, both implementation bugs. Both rounds had two HIGH-plus-MED findings, so round 2 exceeded the convergence limit of one. Spec v2 was frozen at `1b2582d4dbc7bca50c9fe1f1005ef61813eb9b9c` before the repair. It adds the audit reproductions and retains the admitted sampler timing, contention flags, and hard-refusal rules. The new cases produced six expected failures on the reviewed code. [Pipeline §3](https://github.com/mpmdw/JouleWise/blob/211ff5033/docs/process/PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence)

| Verified finding | Repair in `9fd95fbd0903fd65adb90ec699003195886a44af` | Regression | Final |
| --- | --- | --- | --- |
| HIGH, denied or incomplete LaunchAgents enumeration could clear the census. | Treat confirmed directory absence as empty. Require complete enumeration once the directory is observed and refuse on any error. The same census runs at startup and in the background. | `test_execute_refuses_when_background_launchagent_directory_is_unreadable`, `test_launchagent_enumeration_errors_after_presence_is_observed_refuse_at_admission` | PASS |
| MED, a failed host check could omit the final sampler refusal and queued contention. | Finalize the sampler for any admitted run and retain its evidence alongside the host error. | `test_execute_retains_sampler_refusal_and_contention_when_host_check_fails` | PASS |

The original synthetic probes also passed with the repaired expectations. Three threaded regressions passed 20 consecutive fixture runs. The earlier late-census and queued-contention repairs remain covered. Hosted CI and the spec-v2 reviews are tracked on draft PR #824. The shard 8 blocker remains with the CI owner. [CI-owner issue #834](https://github.com/mpmdw/JouleWise/issues/834)
