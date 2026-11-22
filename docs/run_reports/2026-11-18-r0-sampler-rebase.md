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

## Delta audit round 3 and spec v3

Round 3 reviewed `687170eb2adcecbbbacc037f8a3c40407c35ad2c`, whose hosted CI passed all 21 jobs. It verified one HIGH and one MED. The HIGH triggered the Tier 2 return-to-spec rule. Spec v3 was frozen at `452ccdf88dd952ccdaa84b9691adcc9b1b48a5cb` before patching. The new regressions produced three expected failures on the reviewed code. [Reviewed-head CI](https://github.com/mpmdw/JouleWise/actions/runs/44342344950) · [Pipeline §3](https://github.com/mpmdw/JouleWise/blob/211ff5033/docs/process/PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence)

| Verified finding | Repair in `889c172384dec7c65a32670479b9f56bec9f914d` | Regression | Final |
| --- | --- | --- | --- |
| HIGH, a required census root could disappear between preflight and enumeration and the shared scanner would return a clear census. | Declared R0 roots carry their required policy into the shared scanner. A missing root refuses at the enumeration itself, even if restored before the caller can recheck it. Ordinary child paths keep the shared scanner's reconciliation policy. | `test_cli_refuses_when_required_background_census_root_cannot_be_enumerated` | PASS |
| MED, a process observed between overlapping window endpoints could be omitted from one window. | For a contender whose birth is established inside the interval, count the largest observed cumulative CPU as a lower bound over the full window. Earlier births and below-threshold lower bounds remain outside this flag. | `test_window_flags_proven_cpu_from_worker_seen_only_at_an_interior_snapshot` | PASS |

Both auditor probes passed with the repaired expectations. The exit-2 CLI reproduction and overlap regression passed 20 consecutive synthetic runs. Exact-candidate CI and the two-family spec-v3 review are tracked in draft PR #824. Issue #834 remains with the CI owner. [CI-owner issue #834](https://github.com/mpmdw/JouleWise/issues/834)

## Lead-directed census repair after round 4

Round 4 reviewed `caea9b23285d2d3fbadecaa316b78fc45b748e1c`. The lead directed one repair for the recurring filesystem failure class and retained the frozen sampler spec. Repair `e923cd3aa59a19e83365cd86ba3e6f34c7efc8c3` routes census filesystem operations through `census_fs`. The helper consumes directory listings inside its error boundary and raises `Refused` with the failed path and errno. R0 establishes optional absence from a successful parent listing. A listed entry that disappears while it is being inspected refuses. The shared census retains its optional absence and reconciliation policy for other callers.

Both CLI modes return 2 on refusal. Inventory writes its requested file after final sampler verification. Check mode works in a private sibling directory and publishes at the requested path only after verification. On refusal it retains private diagnostics. The SMC redo remains independent. Its reported command records the path used for capture, and its published artifact location follows the completed directory.

| Audit reproduction or requirement | Regression | Result on `e923cd3aa` |
| --- | --- | --- |
| `readlink` returns EIO or ENOENT during census root resolution. | `test_full_r0_refuses_every_census_filesystem_call_fault`, configured symlink with a low-level `readlink` fault | PASS |
| A listed `chain.started` or active-campaigns entry disappears before its read. | `test_full_r0_refuses_every_census_filesystem_call_fault`, injected ENOENT on reads of both record kinds | PASS |
| Inventory census aborts on a filesystem error and exits 2 without publishing. | `test_full_r0_refuses_every_census_filesystem_call_fault`, inventory mode, and `test_inventory_refuses_census_failure_at_eof` | PASS |
| A raw filesystem call bypasses the common helper. | `test_census_filesystem_calls_are_confined_to_the_helper`, verified by injecting a raw `readlink` into a function called by the census | PASS |

The quiet controls passed in both modes. Injecting EIO, ENOENT and EACCES at each observed helper call passed 198 check-mode cases and 99 inventory cases. The synthetic audit replays separately verified exit 2 with no publication for unreadable roots, disappearing chain and registry entries, and the inventory CLI. The original sampler dispositions and frozen test commits remain in force. Exact-candidate CI and two-family review are tracked on PR #824. NEEDS_SPEC has no entries.

## Lead-directed census repair after round 5

Round 5 reviewed `610507f5e13c526c83c92c6f758f1a3d76c3d9b5` and verified two HIGH findings. Regression commit `6a029d5c0` produced seven failing synthetic cases on that implementation. Repair `639ab359040c236d96aff5de5cf721b5b6c46f67` addresses both findings.

Each strict census resolves a configured root once at scan time with `realpath(strict=True)`. Opening the resolved path with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW` verifies that it is a directory and holds the object for enumeration. Within that tree, directory opens, marker reads and metadata lookups use their held parent descriptors. The filesystem helper closes the descriptors and retains path and errno on failure. A configured alias removed or repointed before the scan is observed at resolution. Replacing the filesystem path after the root is opened leaves the scan on the held directory.

Complete listings index entries by case-folded name and preserve their recorded spelling for subsequent opens. Duplicate folded names refuse. Strict custody and LaunchAgent lookups use this index. Other shared-census callers retain their existing traversal and reconciliation policy.

| Verified finding | Regression | Result on `639ab3590` |
| --- | --- | --- |
| HIGH, a configured root changed between preflight and the census. | `test_background_census_resolves_configured_alias_at_scan_time`, `test_background_census_refuses_symlink_substituted_before_root_open`, `test_background_census_keeps_open_root_when_its_path_is_replaced` | PASS |
| HIGH, matching exact stored case skipped a live owner under `Night`. | `test_background_census_matches_folded_names_and_refuses_collisions` covers `Night`, `CHAIN.STARTED`, `Active-Campaigns` and a colliding pair. | PASS |

The round 4 fault matrix now injects errors at the descriptor-relative filesystem operations. Both CLI modes still return 2 without publication on census refusal. The background receipt test runs the strict scanner against an empty synthetic custody root so it verifies the resolved root supplied by the scanner. The frozen sampler spec remains in force. Exact-candidate CI and the requested two-family delta reviews are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Lead-directed R0 repair after round 6

Round 6 reviewed `a1be3f7bfa01aa826a10aca0facc5f37aac22ae8`. Regression commit `f413276af` produced six failing synthetic cases on that implementation. Repair `8b4c877f759a67a4837943cdde81284470a67088` addresses both verified findings.

The issued W1 presign pin and PR #734 head both resolved to `b2e01464d6d4fbf2901ff4d4154df9455104a12a`. Git object checks matched all ten frozen R1 blob IDs at that pin to the W1 source census. `joulewise/night_gate.py` is outside that ten-path set. Its issued W1 blob is `cf9acc2f4a3acf493495b1a8edb59812e9f98dba` and its R0 lane blob is `452da0de9363555dff3cf6f0f65b327b45e354fa`. The repair changes only R0 host code. It supplies R0's `pgrep -i` query with explicit Claude and Codex desktop bundle paths, then applies the shared process-identity filter. [W1 source census](https://github.com/mpmdw/JouleWise/blob/2acbb013567e2d97232497791419f61264dbf831/docs/run_reports/2026-11-18-w1-integration-evidence.md#seventeen-path-census)

For a contender present at opening and absent at close, R0 now subtracts the opening CPU counter from the largest observed counter before exit and judges that lower bound over the full window. If both that evidence and previous-window evidence exceed the limit, the flag uses the observed delta once. A contender whose birth is proven inside the window still uses a zero opening counter.

| Verified finding | Regression | Result on `8b4c877f` |
| --- | --- | --- |
| HIGH, the inherited case-sensitive query missed the Claude desktop executable. | `test_r0_cli_refuses_desktop_agents_in_its_own_census` covers both desktop apps, the CLI, startup and background discovery, and an incidental app path in an unrelated process's arguments. | PASS |
| MED, a worker present at baseline opening could exceed the limit and exit without a flag. | `test_r0_baseline_flags_cpu_delta_of_worker_that_exits_mid_window`, `test_exit_delta_replaces_previous_interval_evidence_for_same_worker` | PASS |

Both auditor probes passed three synthetic replays. Claude and Codex each refused with exit 2 and no publication. The exiting-worker baseline passed with one R0-L3 flag at 0.06 CPU-s/s, as did the still-running control. The R0 lane delta leaves all ten frozen R1 paths, `night_gate.py` and the code pin registry byte-identical to its base. Exact-candidate CI and two-family review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Lead-directed R0 repair after round 7

Round 7 reviewed `caff40650a34ef1b51e748ad4dbee7e087850df5`. Regression commit `1d699ed4d` produced six assertion failures and one input error on those bytes. Repair `8bb807fd6c1156c16864f3054092b517a1883774` addresses all three verified findings.

R0 runs the full case-insensitive agent query and identity filter at baseline opening, baseline close, subsequent admission boundaries and the existing background cycles. Polling during an admitted operation keeps its throttle. The CLI repeats the query after preparing its staged report or serializing its inventory, immediately before making the result visible at the requested path. An agent hit yields exit 2 and withholds publication. The desktop regression also verifies that overlapping queries do not match the literal pattern in each other's arguments.

CPU judgement retains the highest counter observed for each PID and start identity. The high counter survives later low samples and rolled windows. A lower opening sample therefore cannot charge past CPU to a fresh interval. Raw regressions remain available in the receipt. The existing fallback carries a previous over-limit observation when the window has no stronger direct observation. Inventory drains the sampler after an input error and surfaces any census refusal before propagating the input failure.

| Verified finding | Regression | Result on `8bb807fd6` |
| --- | --- | --- |
| HIGH, an agent appearing during the baseline could survive admission and publication. | `test_r0_rechecks_agents_at_baseline_close_later_admission_and_publication`, `test_inventory_rechecks_agents_after_serializing_before_publication` | PASS |
| MED, a zeroed closing counter could hide an earlier 0.06 CPU-s/s lower bound. | `test_r0_baseline_flags_cpu_delta_of_worker_that_exits_mid_window`, `test_lower_opening_counter_cannot_recount_cpu_in_a_later_window` | PASS |
| MED, an inventory input error could mask a latched census refusal. | `test_inventory_census_refusal_takes_precedence_over_input_read_error` injects EIO during the required root read, with and without an inventory read error. | PASS |

All three auditor probes passed synthetic replays. The late agent refused before the first host check, the zeroed counter retained one contention flag, and the simultaneous inventory and census EIO returned exit 2 with the census path and errno and no output. Exact-candidate CI and the requested two-family delta reviews are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Frozen differential against admitted R0-L3

The 341-case acceptance module was copied byte for byte in test-first commit `548336c79`. Its SHA-256 is `e113501601e3cae09b1fc1a131dcf8ef55361493ae7a353135a5c5c83c7438b3`. The unmodified module reproduced 96 failures on `60390d55d` against admitted tree `9c40e4e5d`. It reported 67 missed or late refusals, six missing worker flags, 22 flagged passes, and one additional args-only zombie case. The three clean controls passed both lanes.

Each admission and publication check now runs the full custody, LaunchAgent, agent and process census. The guard applies the admitted CPU interval decision to caller samples and maintains its separate background windows. Each sequence retains its own previous over-limit evidence. Shared process history preserves the highest CPU counter and the contaminant matches for a PID and start identity. A worker with lost arguments therefore retains its first observed classification. A reused PID with a different start identity begins a new history.

The runner drains completed windows before the terminal verdict. Any guard contention flag blocks publication in both check and inventory modes. The check CLI retains the private refused receipt. The forecast and SMC still carry their independent diagnostics.

| Differential requirement | Result |
| --- | --- |
| Match admitted refusal decisions at the same boundaries | PASS, 0 missed or late refusals |
| Retain admitted CPU evidence | PASS, all six previously missing 30–60 s intervals were recorded |
| Withhold publication on any guard flag | PASS, all 80 flagged scenarios returned exit 2 and left the requested path absent |
| Track the args-only zombie after its arguments disappear | PASS, the 0–30 s flag was recorded |

The frozen comparison reports **341 scenarios and 0 failures**, with zero invalid oracle controls. The oracle was staged from pinned local Git objects and both lanes ran on synthetic inputs. Exact-candidate CI and the two-family delta review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 1 after the frozen differential

The blocking audit reviewed `1d77b3194` and verified two HIGH findings and one MED. Regression commit `74ba84158` reproduced seven failing synthetic subcases. Repair `e79e6f231fe4fc52178582378f34846bbe149d70` covers all three findings.

Publication now checks the age of the last background sample on both sides of its final census. A fresh caller probe does not renew background coverage. The same agent identity and measurement-chain decisions apply to each observed process table, including the table paired with the midpoint CPU sample. Caller and daemon windows keep their own endpoints and use observations from both sequences as intermediate evidence.

| Verified finding | Regression | Result on `e79e6f231` |
| --- | --- | --- |
| HIGH, staging delayed publication until background coverage was stale. | `test_publication_refuses_stale_background_samples` exercises a delayed publication, an agent entirely inside the gap, and a final probe that crosses the freshness bound. | PASS |
| HIGH, an agent observed during the baseline could leave before the next dedicated census. | `test_baseline_snapshot_refuses_agent_or_chain_that_leaves_before_admission` covers the CLI agent, desktop agent, measurement chain and benign argument control. | PASS |
| MED, daemon windows lost a worker seen only by a caller admission. | `test_background_window_keeps_contender_seen_only_at_caller_admission` covers the caller-only worker and the daemon-visible control. | PASS |

The six auditor replay cases passed, including the quiet control and the caller-only 15–45 s flag. The existing baseline-close regression introduces its agent after the closing sample so it exercises the dedicated admission census. The frozen module still matches the supplied SHA-256 and reports 341 scenarios, zero failures and zero invalid oracle controls. The earlier audit reports record findings on earlier candidate heads. Their existing custody, exit status, agent and CPU regressions remain in the focused suite and the frozen comparison. No additional MED or LOW follow-ups remain. Exact-candidate CI and two-family review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 2 after the frozen differential

Round 2 reviewed `835235b2f54ca7359315a4c085de43677d0e4f65`. Regression commit `dd299ca0c` produced six failing subcases on those bytes. Repair `27854ed1659c34a600dea3b2c5631fdf89e05263` covers both findings.

R0 refuses case-insensitive agent identities directly from the captured row in the cumulative CPU table, the process arguments table and the dedicated agent query. The cumulative CPU table is judged before the arguments query. The existing identity filter handles incidental argument mentions such as a desktop app path passed to `echo`.

For a worker missing from a window endpoint, R0 keeps CPU growth measured between its observations. A whole-second start near or before the opening does not erase that growth. R0 uses a zero baseline when the observed start floor proves the worker was born within the window. Otherwise it uses the first observed counter and retains the highest measured increase. A worker seen at the close and a worker that exited before it both use this evidence.

| Verified finding | Regression | Result on `27854ed16` |
| --- | --- | --- |
| HIGH, an agent listed at the midpoint could exit before the arguments query and escape admission. | `test_midpoint_accounting_refuses_agent_that_exits_before_args_read`, `test_args_and_pgrep_agent_sightings_do_not_query_process_identity` | PASS |
| MED, the whole-second start floor hid the observed CPU growth of an exiting worker. | `test_exited_worker_retains_measured_growth_across_fractional_window_open`, `test_worker_still_present_at_close_retains_growth_after_missing_open_sample` | PASS |

Both auditor probes passed all four synthetic replay cases. The accounting sightings halted the check before an arguments query or host work. Both worker start-time variants recorded the 15–45 s flag at 0.06 CPU-s/s and withheld output. The frozen suite remains byte-identical at `e113501601e3cae09b1fc1a131dcf8ef55361493ae7a353135a5c5c83c7438b3`. It passed all 341 scenarios with zero failures and zero invalid oracle controls. Exact-candidate CI and the two-family review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 3 after the frozen differential

Round 3 reviewed `7891f898e920cdd0c4bc19ba191aeac88f9b92f0`. Regression commit `c0f607e47` produced 31 failing synthetic subcases. Commit `2429f7a10` added a failing check for distinct observations timestamped on the window edges. Repair `ddf8a4558ae0296cdf1dd79109d4024044f1c13e` covers both classes of finding.

Every captured process row goes through the same census rule set. The case-insensitive agent and measurement-chain matchers refuse from the first sighting in the CPU accounting table, either use of the process arguments table, or the dedicated agent query. An incidental name in a non-agent argument retains the admitted identity filter. The generated matrix hides each process from every other read and checks that the first sighting refuses before another command or identity lookup.

CPU-rate evidence uses the observations in each window's overlap with a process lifetime, including observations on either edge. For an identity absent at the opening, the whole-second start range can supply a zero counter when it overlaps the window. An older start uses its first observed counter. The highest value observed in the overlap establishes measured growth. That evidence survives an exit before the closing sample. Windows with overlapping observations can each retain their own lower bound.

| Verified finding | Regression | Result on `ddf8a4558` |
| --- | --- | --- |
| HIGH, a background CPU table identified an active measurement chain that exited before the arguments query. | `test_background_cpu_table_refuses_measurement_chain_before_args_read`, `test_every_census_name_refuses_from_any_process_table_without_confirmation` | PASS |
| MED, a whole-second start bound excluded the only observation of an exited worker from a 30 s window. | `test_single_sighting_of_exited_worker_counts_at_either_side_of_birth_tick`, `test_distinct_cpu_observations_on_window_edges_are_retained`, `test_exited_worker_retains_measured_growth_across_fractional_window_open` | PASS |

All 44 generated sightings and six auditor replays passed on synthetic inputs. The two worker start variants each recorded the 0–30 s flag at 0.06 CPU-s/s and withheld publication. The 50 publication and CPU interval tests passed. The byte-identical frozen differential passed all 341 scenarios with zero failures and zero invalid oracle controls. Exact-candidate CI and the two-family review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Frozen differential v2

The November 19 resume found a clean worktree at the existing test-first commit `5b038d8e7401c1f4eddb8bb2c3147fc8bddafd0d`, one commit ahead of draft PR #824 at `fb320ce683c6ae929f17eee7da3b86d8ed2928e5`. The v2 suite SHA-256 is `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca`. The copy matches the supplied file byte for byte. The supplied baseline recorded 906 failures on `fb320ce68`.

Repair `33138f71a55d87199329ccba164ef29195ed1466` normalizes each captured process name through one function. It strips enclosing parentheses, takes the basename, case-folds and recognizes process names shortened to Darwin's 16-byte command limit. Agents and measurement chains refuse on the captured sighting. A CPU contender named in an arguments read can use that identity's accounting history, including when it exits before a later query.

The rate uses the largest supported intersection of a window and a process lifetime. The opening read's beginning and the whole-second start floor bound one end. The closing read's completion and the first observed absence after the last accounting sighting bound the other. Counter growth uses centisecond arithmetic and a strict integer comparison to 0.05 CPU-s/s. Exact ties stay quiet. Earlier flags continue to block publication, and subsequent windows are judged on their own evidence.

| Regression family | Cases | Failures before repair | Failures on `33138f71a` |
| --- | ---: | ---: | ---: |
| Preserved differential against admitted R0-L3 | 341 | 0 | 0 |
| Name normalization by class and read | 1,673 | 525 | 0 |
| Lifetime overlap and the strict threshold | 1,080 | 381 | 0 |
| Total | 3,094 | 906 | 0 |

Focused verification passed 115 tests and all 11 publication audit tests. The contention module passed 46 synthetic tests with three live cases skipped. The prior candidate's shard 5 failed `test_every_refusal_site_is_listed_with_its_exact_count` on the refusal allowlist for `measurement_liveness.py`. The previous result and the new exact-candidate CI are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 1 after frozen differential v2

The November 19 resume found a clean worktree and draft PR #824 at `53aba150b8ddbf235d547880609b2048a5a48c7d`. The current audit verified that R0 missed `corespotlightd` at 0.06 CPU-s/s and published. The earlier audit reports cover the repaired census, sampler and window findings exercised by the existing suites.

| Verified finding | Test-first commit | Repair | Regression result |
| --- | --- | --- | --- |
| HIGH, the normalized prefix matcher dropped the admitted substring matches in CPU command names and arguments. | `a0a310e01` | `9690e9e30c2d75aadbc6a7ece6849ec59a8e951e` | PASS, `test_contaminant_substrings_keep_admitted_cpu_flags` |

The CPU census retains the normalized match and the admitted case-insensitive substring search on the original command or arguments. The original arguments preserve path components that basename normalization removes. The regression covers every admitted contaminant pattern in both fields, the exact `corespotlightd` report, and the threshold and neutral-process controls. All 19 above-threshold cases failed before the repair and passed afterward. Both controls published. The auditor replay recorded the 0–30 s flag on admitted R0-L3 and on the repaired R0, which exited 2 without publishing.

Frozen v2 remains byte-identical and passed all 3,094 scenarios with zero failures. The 115 focused tests, 12 publication audit tests, and 46 synthetic contention tests passed. Three live contention cases were skipped. The current report has no additional MED or LOW findings. Exact-candidate CI and the two-family delta review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Frozen differential v3

The freeze commit `4a0dabe4d` copied the supplied suite byte for byte. Its SHA-256 is `afd360c29d390f7d39400e1363a25add5c13ace71bca55c80d11ec0ceb4e5009`. The supplied baseline at `08a2a1d991ce327fe2060ab0d61fdbcc62b91373` lost admitted R0-L3 flags in 3,816 cases. The November 19 resume retained the freeze commit and the partial timestamp changes.

Repair `411e60e1c489bee3d7d46bc5da745979f3785321` gives the admitted endpoint comparison the same paired-read timestamps and midpoint spacing as R0-L3. Foreground admissions choose the newest eligible opening on that time base and use the shared contention calculation with its prior-interval evidence for exits and regressed counters. R0 retains the accounting brackets and intermediate readings for v2's additional lifetime evidence. Check and inventory modes drain the sampler and evaluate the terminal admission even when an earlier flag already bars publication. Commit `c9cecb3f1` places the optional host tick read before the process sample clock starts.

The fixed resident replay saw 1.52 CPU-seconds over the admitted 30.2-second interval. R0 recorded that flag, exited 2 and withheld publication. The earlier `corespotlightd` replay also retained its admitted flag and withheld publication.

| Frozen regression family | Cases | Baseline failures | Candidate failures |
| --- | ---: | ---: | ---: |
| Preserved v2 cases | 3,094 | 0 | 0 |
| Rate denominator and time base | 4,219 | 3,605 | 0 |
| Endpoint and worker histories | 368 | 210 | 0 |
| Fixed audit replays | 2 | 1 | 0 |
| Total | 7,683 | 3,816 | 0 |

All 116 focused tests and 12 publication audit tests passed. They include `test_args_ps_time_is_included_in_the_admitted_midpoint`, `test_host_probe_time_precedes_the_admitted_cpu_sample`, the guard's exit and regression cases, and both terminal-admission checks with an earlier flag. The previous candidate's shard 5 repeated `test_every_refusal_site_is_listed_with_its_exact_count`. Exact-candidate CI and the two-family delta review are tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 1 after frozen differential v3

The audit reviewed `9fd1181cdfc1c8a379de2f513d3cc33f4b61cffd`. The new caller-gap regression in `c929cfc78` reproduced a false pass with 0.5 s and 2.0 s arguments-read delays. Draft PR #694 judged the same accounting window at 0.0503333 CPU-s/s. Repair `6258f14e80f24319a74c1d446966e78789f3f17d` restores that result.

| Finding | Regression | Result |
| --- | --- | --- |
| HIGH, arguments latency diluted a background contention flag. | `test_background_resident_rate_excludes_arguments_read_latency`, `test_args_ps_time_only_extends_the_admitted_midpoint` | PASS |

The background guard uses the accounting-read midpoints for window selection, endpoint rates, and resident lower bounds. Foreground admissions use the paired-read midpoint and the admitted R0-L3 endpoint decision. Arguments rows can still identify workers and bound the lifetime of a worker that exits. Both auditor replay variants flagged the 30–60 s window, exited 2, and withheld publication. The exact-threshold control published.

Frozen v3 remains byte-identical and passed 7,683 cases. The separately executed v2 archive matched SHA-256 `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca` and passed 3,094 cases. All 116 focused tests, 13 publication audit tests, and the foreground midpoint check passed. Exact-candidate CI is tracked on draft PR #824.

## Resolved audit checklist for PR #824

The lead superseded the v2 checksum requirement at `tests/align/test_r0_vs_l3_differential.py`. The next audit uses frozen v3 at that path and runs the archived v2 suite separately against the same candidate commit.

| Audit input | Byte source | Required SHA-256 | Required passes |
| --- | --- | --- | ---: |
| Frozen v3 | `tests/align/test_r0_vs_l3_differential.py` at the candidate | `afd360c29d390f7d39400e1363a25add5c13ace71bca55c80d11ec0ceb4e5009` | 7,683 |
| Archived v2 | `tests/align/test_r0_vs_l3_differential.py` at `5b038d8e7401c1f4eddb8bb2c3147fc8bddafd0d` | `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca` | 3,094 |

Record both digests and completed case counts against the exact PR head in the draft evidence. A digest mismatch, incomplete run, or failed case blocks the audit. The v2-at-that-path finding in the previous audit is superseded. NEEDS_SPEC has no entries.

## Audit round 2 after frozen differential v3

The audit reviewed `9ed986bec8258ced5e8e2c32527dc3d9a7b94e15`. Both verified findings reproduced on that head from the auditor's scripts before any change.

| Finding | Regression | Result |
| --- | --- | --- |
| HIGH, a forced disk admission returned clear after the sampler had latched a census `EIO`. | `test_audit2_forced_disk_admission_refuses_eio_latched_during_its_own_census`, `test_sampler_failure_at_any_foreground_probe_admits_nothing_afterwards`, `test_every_verdict_refuses_a_failure_latched_at_any_of_its_probes`, `test_throttled_check_refuses_a_latched_failure_before_the_sampler_stops`, `test_finish_refuses_a_failure_latched_after_its_windows_were_judged`, `test_refusal_without_a_message_still_latches` | PASS |
| MED, an exited worker's 1.80 CPU-seconds were dropped when its PID had an earlier holder. | `test_audit2_exited_worker_is_flagged_when_its_pid_had_an_earlier_holder`, `test_later_holder_of_a_pid_cannot_stretch_an_exited_workers_lifetime`, `test_later_holder_bounds_the_lifetime_after_an_earlier_wall_step`, `test_arguments_only_pid_sighting_reads_the_same_as_an_argument_change`, `test_arguments_sighting_before_the_first_accounting_row_names_the_process`, `test_sighting_without_another_holder_on_record_stays_with_the_pid`, `test_earlier_holders_name_does_not_follow_the_pid_to_a_later_process`, `test_later_process_is_cleared_only_by_a_start_second_after_the_sighting`, `test_later_workers_name_does_not_reach_back_to_an_earlier_process`, `test_printed_start_proves_a_later_birth_only_beyond_any_clock_shift`, `test_history_is_kept_per_identity_across_pid_reuse` | PASS |

Repair `b6174ef716ee3305247d1a701875e0c13f5786f4` gives every clear verdict one last step. An admission read the sampler's stored failure once, before its own census probes, so a failure stored during those probes waited for the next call. `check`, `verify_publication` and `finish` now re-read the stored failure immediately before they return clear. The 15-second throttle also reads it directly instead of relying on the sampler's stop flag. The sweep moves the auditor's fault to each of the 30 probes that the six forced admissions after the baseline make. On the audited head all 30 admitted the checkpoint in progress, and the ten inside a unit's own admission went on to start host or disk work. On the repair each refuses that checkpoint, starts no further work and exits 2 without publishing. An admission does not wait for a census still in flight; `finish` drains that case as before.

Repair `13a12d9475c3771d7201efcc09b461e272708894` stops treating the arguments table's PID as a process. That table prints no start time. The guard had withheld an arguments sighting from an accounting row whenever the PID's remembered history belonged to a different start, which discarded the worker's name after reuse. Counter and classification history is now kept per PID and start. A sighting that precedes an identity's first accounting row counts for it. A later holder of the PID bounds the earlier lifetime at the end of the holder's printed start second, so it cannot dilute the rate through the arguments table. In the mirrored replay a worker with 0.60 CPU-seconds over 11 seconds is flagged at 0.0545 CPU-s/s; the audited head spread it over 25 seconds and published.

An independent executing review of those two commits found no path that returns clear with a failure stored. It found gaps in the PID join and one in the foreground latch, repaired in `20f59b6f432a207963d8cb7d75508482aa083667`.

- The later-holder bound was dated against the window opening, so a wall step of more than one second earlier in the window switched it off. It is now dated on the clock of the worker's own last row.
- A sighting was withheld from any row whose start proved a later birth. With no other holder of the PID on record, the audited head kept the sighting and flagged, and `13a12d947` published. The sighting now stays with the row unless accounting has another holder on record and the start proves a later birth.
- The proof used a fixed one-second band, which named ordinary later processes. The start second must now clear the sighting by the clock shift measured since the nearest earlier accounting read.
- Once a later holder bounded its lifetime, an earlier ordinary process could cross the limit on the strength of the later worker's name alone. Arguments reads now record when they began. The bound applies when the earlier process is named by its own rows or by a sighting from inside the bounded lifetime. Otherwise its lifetime stays as long as the PID was listed, as on the audited head, so the bound only adds evidence.
- A foreground refusal whose exception had an empty message stored an empty failure, and the next admission was clear. The latch now stores the exception type.

The review's differential fuzz was rerun against `20f59b6f4`: 8,000 histories with one to three holders of a PID, wall steps, zombies and slow reads, each run with and without the other holders. In none of the 16,000 runs did the audited head refuse and the candidate publish. The candidate refused 102 runs that the audited head published. In 62 it flags the named worker. In 40 it names an ordinary process born in the second a named holder exited, the one-second limit described below.

Three limits remain and are stated here. The first is a limit of the frozen arguments query, which the lead ruled stays as issued.

- A later holder that only an arguments table lists, and no accounting read, cannot be told from the earlier process changing its arguments. `ps -Ao pid=,pcpu=,args=` prints no start time, and a process can change its arguments while keeping its PID and start. The two histories give byte-identical tables and R0 gives them the same verdict. The earlier lifetime extends to the first confirmed absence, as frozen v2's long-exit overlap cases require for a listed PID. With the worker's only row at the 15-second baseline midpoint, 0.60 CPU-seconds over 25 seconds is below the limit and both runs publish with no flag. When accounting lists the later holder with another start, the 11-second bound applies and R0 flags the window and exits 2.
- `lstart` has one-second resolution. A holder's start second bounds the earlier lifetime only at its end. A later process whose start second contains a sighting keeps the sighted name; the audited head published that case, and the candidate refuses it.
- After a forward wall step of more than one second, a worker first listed after the step with a single row is charged from its first counter. The audited head behaves the same; this round does not change it.

Both auditor replays pass on the candidate. The census replay refuses at the disk unit's admission in the `before` and `during` cases with only host work started. The process replay flags the same three windows for the fresh and the reused PID and exits 2.

Frozen v3 remains byte-identical at SHA-256 `afd360c29d390f7d39400e1363a25add5c13ace71bca55c80d11ec0ceb4e5009` and passed 7,683 cases. The archived v2 suite at SHA-256 `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca` passed 3,094 cases. Both ran against `20f59b6f432a207963d8cb7d75508482aa083667` and again against the pushed head `4607492a5abf312ad62e57705b2d99bac1c225e1`. All 132 focused tests of that head passed with one native-capture case skipped, and the paired regression added after the ruling passes. Of the 17 new ones, 15 fail on the audited head. The two that pass there are controls: an unrelated later process is not named, and a sighting with no other holder on record is judged as on that head. `test_every_refusal_site_is_listed_with_its_exact_count` still fails for `measurement_liveness.py` with the same 18 differences as on the audited head; this round changes neither that module nor the allowlist. Exact-candidate CI on `4607492a5` passed 20 jobs, including the 16 regressions of that head in shard 8 and frozen v3 at 7,683 cases in shard 12. Shard 5 repeated the allowlist failure. RL-180 §2(c) grants this PR no CI waiver, so that failure still blocks.

The builder raised one NEEDS_SPEC entry: whether a later holder of a PID that only the arguments table lists must end the earlier process's lifetime. The lead resolved it. A PID sighting in the arguments table alone does not end the earlier worker's lifetime. R0 uses the largest overlap the observations support, bounded by the first confirmed absence or by accounting evidence of a later holder with a different `lstart`, and keeps the earlier worker's observed CPU in either case. A latched census failure still refuses admission immediately. The frozen query and both suites stay as issued. The paired regression above records the ruling. NEEDS_SPEC has no entries.

## Audit round 3 after frozen differential v3 and the lead's architecture ruling

The audit reviewed `9c01174a6cb39d8f1444ff5b239a64fce7f6686b`. It found the same class as round 2: a fault reached while a foreground admission's own probes ran still let disk work start, and the final verdict then withheld the run. The lead ruled that patching this race case by case does not converge.

- R0's only authority is its final verdict over the complete sample series. A stall, a window over the limit, a census fault or contention latched at any time from the first admission to the end of the run gives exit 2 and withheld publication.
- Foreground admission is advisory. As its last act before returning clear, it re-reads the latch, the age of the newest sample and the windows completed during its own probes. The residual race is accepted and documented in the module docstring.
- Window and interval arithmetic uses the monotonic clock. A window in which the wall clock moves more than 0.5 s against the monotonic clock is flagged.
- Hosted CI must be green, including the `measurement_liveness.py` refusal allowlist on shard 5.

| Finding | Regression | Result |
| --- | --- | --- |
| HIGH, forced disk admission returned clear with the newest sample 50.1 s old, or with a completed 60 s window queued. | `test_audit3_admission_refuses_a_stale_sample_or_long_window_reached_during_its_probes`, `test_throttled_tick_does_not_skip_a_stale_sample_or_a_completed_window` | PASS |
| MED, a 2 s forward wall step hid an exited worker's 1.80 CPU-seconds; R0 published with no flag. | `test_audit3_forward_wall_step_flags_the_window_and_withholds`, `test_wall_clock_divergence_flags_a_window_only_above_half_a_second` | PASS |

Repair `53526d42aaaaca4bb585f613bcb4c09b706dff6b` gives admission one closing step, `QuietGuard._close_admission`. It judges any windows completed while the admission's probes ran, so a long window refuses and a busy window keeps its flag. It then requires the newest sample to be at most 50 s old, measured at that moment, and re-reads the latch. The 15-second tick throttle skips only when the same three facts are clear. In the auditor's replay, `stale_during` and `long_during` now refuse at the disk admission with only host work started. `boundary` ends its admission with the newest sample exactly 50.0 s old, which is within the limit, so disk work starts; the final verdict withholds the run at 63.0 s. All five cases exit 2 without publishing, which the regression asserts.

Windows, intervals and rates were already computed on the monotonic clock. The same repair records, for each judged window, how far the wall clock moved against the monotonic clock across the window's accounting reads. Above 0.5 s the window gets a flag of kind `wall_clock`, which withholds publication like contention. Darwin's printed process start (`lstart`) is the only evidence of a birth time and remains a wall label converted with the offset measured at the read that listed it; frozen v2's overlap family depends on that conversion. No unflagged window now relies on a conversion across a wall step. In the auditor's replay the 2 s step flags the 0–30 s sampler window and the 0–40 s admission window, and the run exits 2 without publishing. The stable-clock control still flags the worker. Steps of ±0.49 s publish and steps of ±0.51 s are withheld.

A first draft also treated absence from a window's opening read as proof of a birth inside the window. It contradicted `test_window_flags_proven_cpu_from_worker_seen_only_at_an_interior_snapshot`, where a process whose printed start precedes the window is missed by the opening read and its CPU may predate the window. That change was withdrawn; the clock flag alone meets the ruling.

Three earlier tests asserted behaviour the ruling removes. Two controls stepped the wall clock by 5 s and expected publication; they now expect the clock flag and still assert that no process is flagged. `test_stalled_sampler_refuses` expected a throttled tick to skip a 51 s old sample; the tick now refuses.

The unit-test helper's guard now has a wall clock that moves with its fake monotonic clock; it had read the real wall clock. Tests that set their own wall clock replace the guard's `wall_clock_ns` instead of patching `time.time_ns`.

The refusal allowlist covers every census site in `measurement_liveness.py`. Twelve new sites and five changed ones, whose guard changed or whose count rose, are reviewed: fifteen as NUMBER_INTEGRITY and two as INTERNAL. The stale signal-0 entry under `_inspect_pending` moved with its code to `_pending_group_gone`. `python -m tests.hazards.refusal_census` reports no differences, and `tests.hazards.test_refusal_allowlist` passes.

The audit-2 replays still pass: the census fault refuses at the disk admission, and fresh and reused PIDs flag the same three windows. Allowlist review `7cbab59168a39b085daf98e1aa6de3647bca1645`. Frozen v3 is byte-identical at SHA-256 `afd360c29d390f7d39400e1363a25add5c13ace71bca55c80d11ec0ceb4e5009` and passed 7,683 cases against `7cbab59168a39b085daf98e1aa6de3647bca1645`. The archived v2 suite at SHA-256 `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca` passed 3,094 cases. Both local runs widened only the outer per-lane watchdog, from 900 s or 240 s to 7,200 s, after hashing the unchanged suite file, as the round 3 audit did. All 137 focused tests passed with one native-capture case skipped, along with 155 runner, contention and liveness tests. All 4 new tests fail on `9c01174a6`. Exact-candidate CI is tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 4 after frozen differential v3 and the self-contained final verdict

The audit reviewed `c069985cb80331638f45157450b7c1cce25eb6a0`. Frozen v3 passed 7,683 cases, all 6,903 injected census faults refused, and every prior reproduction passed. The one finding applied the round 3 ruling incompletely. The daemon's last sample was at 61.0 s and the run ended at 75.5 s. The only window ending at the run-end read was the publication census's admission window, opened at the 30.0 s admission sample. That window was 45.5 s long, so 1.80 CPU-seconds between 71.5 and 75.5 s gave 0.040 CPU-s/s, and R0 published. The lead ruled that the final verdict be self-contained:

- Its only input is the sample series, from the first daemon sample to the last read at run end. It uses no admission timestamp or opening.
- On the monotonic clock it judges every window the rule defines over that series, including the window ending at the final read and, for fixed-length windows, the last full-length window ending there. Any window over the limit flags and means exit 2.
- Admission stays advisory and is never an input to the verdict.

| Finding | Regression | Result |
| --- | --- | --- |
| HIGH, contention in the last 30 s before the run-end read fell outside every window the verdict judged; R0 published. | `test_audit4_terminal_contention_is_judged_from_the_series_final_read`, `test_a_burst_at_every_five_second_offset_flags_through_the_verdict`, `test_full_length_window_uses_the_oldest_sample_inside_it` | PASS |

Repair `bf3aa3b1bbc3b2905e4389e3c1db897b0368452b` makes the read that each publication census takes at run end a sample of the series. Before, it was an admission-only snapshot. The verdict then judges every sliding window over the series, including the window ending at that final read. The sliding rule opens a window at the newest sample at least 30 s earlier, so its windows run from 30 s to about 45 s. A final read off the daemon's grid can therefore end a 44 s window. The verdict also judges the window of exactly 30 s that ends at the final read. Counters exist only at samples, so that window's opening carries the counters of the oldest sample inside it, which bounds its CPU from below. Its rates use the full 30 s. It is reported from that sample to the final read, so every reported endpoint is a sample midpoint, as frozen v3's endpoint family requires. A first build reported the synthetic start instead, and that family stopped with `reported endpoint 100.4 is not a sampled midpoint`. When a sample sits exactly 30 s before the final read, the two windows coincide and only one is judged. The publication census's admission window remains for parity with the admitted L3 guard, which frozen v3 compares window by window. It can add a flag and never supplies an opening to the verdict.

In audit 4's replay, the quiet control publishes. The `normal`, `extra_admission` and `next_tick` cases flag the series window ending at the final read (45.5–75.5 s and 45.5–76.5 s) and exit 2; `normal` published before. The audit's companion replay with regular ticks and a final read at 79 s now flags 45–79 s at 0.0529 CPU-s/s and the full-length window, reported from its 60 s opening sample to 79 s, at 0.06 CPU-s/s; its quiet control publishes.

The sweep places a 1.80 CPU-second burst over 4 s at every 5 s offset across the run under two schedules. One is the audit's, with the daemon 0.5 s late each cadence and the final read at 75.5 s. The other is the regular cadence with an off-grid final read at 74 s. All 30 placements, 15 per schedule from 0 to 70 s, exit 2 without publishing. Each placement is flagged by a series window that contains the whole burst, not only by an admission window. Both quiet controls publish. On `c069985cb`, the placements at 60, 65 and 70 s published under both schedules. The exact-threshold test fixes the full-length window as the 30 s from 44 s to 74 s, reported from its 45 s opening sample: 1.50 CPU-seconds stays quiet and 1.52 flags at 1.52/30 CPU-s/s. All three new tests fail on `c069985cb`.

One limit remains, and it was accepted when MAX_WINDOW_S was set. If the daemon misses ticks without exceeding the 50 s stall limit, a window can be up to 50 s long, and the series cannot place a burst inside it more finely than its samples.

The audit-2 and audit-3 replays are unchanged. Frozen v3 is byte-identical at SHA-256 `afd360c29d390f7d39400e1363a25add5c13ace71bca55c80d11ec0ceb4e5009` and passed 7,683 cases against `bf3aa3b1bbc3b2905e4389e3c1db897b0368452b`. The archived v2 suite at SHA-256 `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca` passed 3,094 cases. Both local runs widened only the outer per-lane watchdog after hashing the unchanged suite file. All 140 focused tests passed with one native-capture case skipped, including the census fault matrix, along with 155 runner, contention and liveness tests. Exact-candidate CI is tracked on draft PR #824. NEEDS_SPEC has no entries.

## Audit round 5 after frozen differential v3 and the exact check at every sample

The audit reviewed `671bd3f1dad08588bdf63a2ee28ba8b954377b6f`. Frozen v3 passed 7,683 cases and all 6,903 injected census faults withheld publication. The one finding: the daemon read 0.00 CPU-seconds for a worker at 45.5 s and 1.52 at 61.0 s. That pair proves at least 0.0507 CPU-s/s within 30 s. A run ending at 61.0 s flagged it and exited 2. The same run extended with quiet samples through 107.5 s published `pass`. The exact 30 s window was judged only at the final read, and the 30–45 s sliding windows dilute an interior burst. The lead ruled (E1):

- The verdict flags contention if any interval the series can prove holds at least the limit times 30 s of CPU within 30 s. For every pair of samples i < j with t_j − t_i ≤ 30 s, it flags if (cpu_j − cpu_i) / 30 ≥ limit. The existing rule windows stay. Equivalently, the exact 30 s check runs at every sample end.
- The verdict is monotone: adding samples can never remove a flag already provable from earlier samples.

| Finding | Regression | Result |
| --- | --- | --- |
| HIGH, appending quiet samples after an interior burst turned a flagged run into a published pass. | `test_audit5_quiet_samples_appended_after_an_interior_burst_keep_its_flag`, `test_appending_quiet_samples_never_removes_a_verdict_flag`, `test_exact_check_flags_at_least_the_limit_within_any_30_s` | PASS |

Repair `97c170d1fed5d862f8038261befd28a4a82f104c` runs the exact check at every sample, as that sample first ends a window. The check compares the sample with each earlier sample at most 30 s before it. A contaminant identity listed by both samples is flagged when its counter grew by at least 1.50 CPU-seconds (the 0.05 limit times 30 s), and its rate is charged over 30 s. Ties flag, as E1 specifies. The earlier counter must be the process's own reading: a counter that regressed below an earlier peak, such as a zombie's zero, is not used as the earlier end of a pair. Each sample is judged once and a flag is never withdrawn, so adding samples cannot remove one. Pruning keeps every sample within 30 s of a future end. The per-sample check replaces round 4's single full-length window at the final read, which it covers. The sliding rule windows stay with their strict comparison. At each sample the rule window is judged before its exact pairs, so a rule window keeps its own flag in the receipt when a pair has the same endpoints; frozen v1 checks that audited windows stay in the terminal report. Exact-check flags carry `kind: "exact_30s"` and are receipted under `exact_windows`.

In audit 5's replay, every run with 1.50, 1.52 or 1.60 CPU-seconds exits 2 without publishing, short and extended alike. The 45.5–61.0 s pair is flagged in both, and the short run's verdict flags are a subset of the extended run's. Both quiet controls publish. Under the ruling's tie rule, `short_150`, which published on `671bd3f1d`, now flags.

The generated sweep crosses burst position (start, interior, end) with burst size (1.49, 1.50, 1.51 and 1.80 CPU-seconds over 4 s) and three daemon schedules: on the 15 s grid, 0.5 s late each cadence, and alternating ±0.4 s around the grid. Each short run ends on a daemon tick, so its samples are a subset of the runs extended by one and three quiet ticks. Across all 108 runs, every short run's verdict flags are a subset of each extended run's, and no withheld run becomes a pass. Every burst of at least 1.50 CPU-seconds is flagged by a series window that contains it. Every 1.49 CPU-second burst publishes with no flag. On `671bd3f1d`, the audit-5 regression failed in 6 subtests, the sweep in 12, and the tie test failed.

Earlier tests that list the sliding rule flags now filter on `kind`, because the exact check adds stricter flags. Two quiet controls at exactly 1.50 CPU-seconds within 30 s moved one TIME quantum below the limit, to 1.49, since E1 flags the tie. Round 4's full-length window test became the tie test.

The audit-2, audit-3 and audit-4 replays are unchanged. Frozen v3 is byte-identical at SHA-256 `afd360c29d390f7d39400e1363a25add5c13ace71bca55c80d11ec0ceb4e5009` and passed 7,683 cases against `97c170d1fed5d862f8038261befd28a4a82f104c`. The archived v2 suite at SHA-256 `0752ccc152ec4c93b710337be6d9ff6e5de7f50c6997ff6db3d046391d91fcca` passed 3,094 cases. Both local runs widened only the outer per-lane watchdog after hashing the unchanged suite file. All 142 focused tests passed with one native-capture case skipped, including the census fault matrix, along with 155 runner, contention and liveness tests. Exact-candidate CI is tracked on draft PR #824. NEEDS_SPEC has no entries.
