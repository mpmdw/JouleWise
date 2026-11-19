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

The six auditor replay cases passed, including the quiet control and the caller-only 15–45 s flag. The frozen module still matches the supplied SHA-256 and reports 341 scenarios, zero failures and zero invalid oracle controls. The earlier audit reports record findings on earlier candidate heads. Their existing custody, exit status, agent and CPU regressions remain in the focused suite and the frozen comparison. No additional MED or LOW follow-ups remain. Exact-candidate CI and two-family review are tracked on draft PR #824. NEEDS_SPEC has no entries.
