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
