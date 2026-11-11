# W1 reliability round 4 — local Sol seat `w1-reliability-4`

Branch: `ops/2026-11-10-w1-reliability-4`, created from `297629a0d`.
Applied the branch-1 cold review F-01–F-13 and F-01t. The review is copied
byte-for-byte to `2026-11-10-w1-reliability-fable-review.md` in this directory
(SHA-256 `3deea16af67ada3f814100ea0ae5261eb37126172f42433b51d2bf56cc399337`).
Branch-2 W findings are outside this assignment and remain open.

## Authority and boundaries

Lead rulings, verbatim:

> F-06 AUTHORIZED: km003c_monitor.py (bound) exits after N consecutive USB errors so the supervisor restarts it; the chain waits for a first valid meter batch before starting. Same scope as the I-01 ruling.

> F-09 AUTHORIZED: the next-arm release check accepts the dead-man's delivery receipt (bound code change), so a dead-man-delivered night does not block the next series arm.

> Confirmed as within the earlier rulings: the in-window meter gap stops the chain; the dead-man writes a REFUSED result.json when none exists.

> F-02 is the priority after F-01: a completed, restored, delivered night must be byte-stable under repeated dead-man fires (result.json sha unchanged, courier.sent never unlinked); restore the two weakened assertions in tests/test_run_night.py (F-03).

Mission M0: inspected root AGENTS/CLAUDE, the requested restart/workspace/queue
sections, playbook, orchestration and authority pointers. No active stop card;
the explicit brief selects this AGENT task. Preserved the clean starting tree.
No delegation or consult. No network, real measurement inputs, study analysis,
model downloads, sudo, installation, arm, or change to the long-running blinded
job. Git pushes in tests target **temporary local bare repositories only**.
No external data path cited by repository text was followed. No custody outcome
is disclosed. Hardware behavior remains **PROVISIONAL**.

The brief overrides ordinary coordination writes and the canonical full-suite
instruction: `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`
and `tests/test_gen_state.py` are unchanged; no kernel task was registered.

## Finding dispositions

| Finding | Change and witness |
|---|---|
| F-01 | Read `hazard_window.thresholds.clock`, copy its budget and override the span with the plan's `hazard_window.T_stream_max_s`. Missing budget keys refuse as `clock.frequency_plan_invalid`. |
| F-01t | `ProductionPathTests` runs the real prepare/install preflight on the real writer's plans with injected frequency reader and command runner. Its pre-arm clock is simulated because the chain replay deliberately stages a past t0 to avoid a real wait. Unit tests for budget errors use the actual hazard-window shape. |
| F-02 | Dead-man recovery never rewrites an existing `result.json` or unlinks `courier.sent`. A restored/delivered result with no power marker is a no-op. Recovery addenda are create-once artifacts and are published. Three daily fires preserve result SHA, sent-marker inode/mtime/bytes, directory entries and zero host/courier calls. A failed later courier also preserves both original records. A newly created recovery result includes its restoration record at creation. |
| F-03 | Early stand-down logs only to the custody log; launch-abandoned fires stand down. Restored both original assertions that the night directory is unchanged. Added an abandoned-launch witness. |
| F-04 | Hazard driver sets the runtime's unproven-termination record before post-chain work/result close. Unproven interrupt cleanup also propagates it. A driver test returns `proven=False` through the real hazard path and proves that mode 2, OFF and the owed marker remain; no courier launches. |
| F-05 | Passing words also require authenticated OFF. ON triggers OFF plus a second authenticated query. A passing nonzero word still needs no zero operation. |
| F-06 | Five consecutive USB errors terminate the monitor with exit 1 after cleanup; successful USB I/O resets the counter. USB cleanup errors retain the trailer. The meter supervisor also retries clean absent exits during re-enumeration. Chain claim waits for a fresh valid batch within the existing 20-second monitor-readiness timeout. No batch refuses before `chain.started`; absent-then-streaming recovery is tested. The existing 600-second in-window bound is unchanged. |
| F-07 | Unreadable secondary artifacts are omitted and named in `delivery_omissions.json`, the delivery receipt and custody log. Result-read failures still fail delivery. Real local Git transport verifies that result bytes arrive unchanged despite a secondary permission error. |
| F-08 | Escaped exceptions publish immediately after the fallback terminal result is written. The test checks that result/restoration exist when `_durable_record` is called. |
| F-09 | Next-arm release accepts an authenticated `courier_delivery` source when the original courier outcome is false. The receipt must match transport, plan, results ref, commit shape and exact result digest; existing `courier_sent`, chain-closure and watchdog latch requirements remain. Mutation tests reject missing/wrong receipts. |
| F-10 | Preflight records the installed helper's locator/SHA-256 before invoking it, or its read error if unavailable. Bound the C source in `v4_registration.ARTIFACTS` and added its null entry to the registration receipt **template**; no live registration or signature was minted. |
| F-11 | Network time ON requires this night's successful OFF action/receipt, or the dead-man's authenticated proof that no night job is installed. Rerun/abandoned paths suppress ON. Signal shielding covers host close and result persistence, then TERM can interrupt the courier. Pre-OFF refusal, zero-exit administrator denial, rerun and courier-TERM witnesses cover these changes. |
| F-12 | Delivery errors retain a bounded stderr tail. Successful program delivery removes `courier.filed`. Courier waiting returns immediately when the process has exited nonzero. |
| F-13 | Only the last complete batch payload per changed stream is decoded/validated; headers still establish streaming provenance. Current paired RAW/monotonic clocks prevent sleep from leaving every later sample in the future. The probe uses the observed subprocess boundary. Regenerated closure evidence includes the session import, actual forced-absent monitor child and actual shell courier importing the runner. |

Legacy kit/cadence unit witnesses that do not write a real night plan still
isolate the preflight. The production-writer replay no longer replaces it.

## Performance evidence and output preservation

Read `git show origin/main:docs/perf/SPEED-TOOLBOX.md` before the F-13 change.
A synthetic 500-batch backlog profile at `297629a0d` made 501 JSON decodes and
500 hex decodes; the corrected reader makes 2 JSON decodes and 1 hex decode.
A later comparison loaded the original module directly from that Git object
and compared canonical decision JSON on the same synthetic valid-batch,
USB-error and 601-second-silence sequence: byte-identical (`null`, `null`,
`{"outage_s":600.0,"silent_s":{"meter":601.0}}`).
The sleep projection and malformed-final-batch handling are the requested
reliability changes; equivalence is not claimed for those corrected cases.
No native timing/throughput saving is claimed. No batching, decision cache,
engine/estimator/threshold/seed change, or measured-episode change was made.

## Verification

Targeted checks only, one module at a time. Results and final test counts are
recorded below after verification. The first round-3 baseline was 14 passed.
During development, expected fixture assumptions were corrected: the old
frequency-plan shape, unconditional-ON expectations without an OFF action,
old dead-man result mutation, the replay's pre-arm clock, the synthetic
USB exception constructor, and the older header-only meter fixture. All final results supersede those intermediate
failures.

For each target below the command is
`JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest <target>` (Git-backed
runs also set `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`).

| Target | Result |
|---|---|
| `tests.test_w1_reliability` | 11 passed |
| `tests.test_w1_reliability_r2` | 18 passed |
| `tests.test_w1_reliability_r3` | 14 passed; also inherited by the round-4 module |
| `tests.test_w1_reliability_r4` | 42 passed on final confirmation |
| `tests.align.test_v4_series.ProductionPathTests` | 1 passed, replaying the writer/prepare/install/hazard path across the series |
| `tests.align.test_v4_next_arm_packet` | 46 passed |
| `tests.align.test_km003c.NightChainTests` | 2 passed after correcting the old header-only fixture |
| `tests.test_b5_driver_p3.MeterWindowTests` | 7 passed |
| `tests.external.test_km003c_monitor` | 12 passed, 1 live-device smoke skipped |
| `tests.align.test_v4_executed_closure` | 4 passed |
| `tests.align.test_v4_dynamic_closure` | 10 passed |

The selected legacy night/courier command below passed all 16 tests:

```sh
python3.13 -B -m unittest \
  tests.test_run_night.NightDriverTests.test_dead_man_restores_and_redelivers_when_courier_sent_exists \
  tests.test_run_night.NightDriverTests.test_dead_man_stands_down_immediately_after_t0_on_empty_night \
  tests.test_run_night.NightDriverTests.test_dead_man_stands_down_one_second_before_completion_epoch \
  tests.test_run_night.NightDriverTests.test_dead_man_absent_marker_at_completion_epoch_couriers \
  tests.test_run_night.NightDriverTests.test_dead_man_empty_start_marker_waits_until_completion_epoch \
  tests.test_run_night.NightDriverTests.test_dead_man_reaps_a_gone_group_then_censuses_and_couriers \
  tests.test_run_night.NightDriverTests.test_dead_man_refuses_a_proven_live_process_group \
  tests.test_run_night.NightDriverTests.test_dead_man_refuses_a_fresh_live_courier_lock \
  tests.test_run_night.NightDriverTests.test_courier_uses_one_launch_three_retries_and_every_backoff \
  tests.test_run_night.NightDriverTests.test_courier_wait_caps_sleep_at_the_dead_man_epoch \
  tests.test_run_night.NightDriverTests.test_run_path_courier_hands_off_at_the_dead_man_epoch \
  tests.test_run_night.CourierReapingTests
```

`JW_B5_SYNTHETIC_ONLY=1 python3.13 -B scripts/align_v4_dynamic_trace.py --out /private/tmp/w1-r4-dynamic-trace-final.json`
completed successfully: 416 targeted cases across nine successful scenario
suites, 186 executed paths, no unbound or non-STRICT paths. The tracer does
not inventory skip counts. Both `scripts/km003c_monitor.py` and
`scripts/run_night.py` appear in `child_process_paths`. Copied the generated
JSON into the bound trace only after all scenarios succeeded. The first
regeneration's one failed scenario was the header-only fixture described
above; it was not committed as successful evidence.

`python3.13 -m compileall -q joulewise tests`, AST parsing of every changed
Python file, and `git diff --check` passed. Synthetic before/after profiling
and byte comparison used `PYTHONPATH=. python3.13 -B /private/tmp/w1-r4-meter-profile.py`.
Cumulative test runtime including development reruns and both trace runs
was about 19 minutes, below the requested approximately 20-minute budget.
No full suite was run.


## STRICT re-registration inventory

Current-round STRICT-bound paths (membership checked against `ARTIFACTS`):

- `joulewise/align/apple/v4_registration.py`
- `joulewise/b5/driver.py`
- `scripts/align_v4_dynamic_trace.py`
- `scripts/align_v4_next_arm_packet.py`
- `scripts/align_v4_session.py`
- `scripts/km003c_monitor.py`
- `scripts/run_night.py`
- `docs/align/v4/dynamic_closure_trace.json` — regenerated, not hand-edited.

The complete reliability branch relative to `9abe6095f` additionally changes
STRICT-bound `joulewise/align/apple/powermode.py`, `scripts/b6_courier.sh` and
`scripts/zero_ntp_frequency.c` (newly bound here). These all require coverage
at re-registration. The receipt template is updated to reflect the added
source, but a fresh signed receipt and both registration gates remain lead-owned.

Other touched files: registration receipt template; the preserved review;
this report; `tests/test_w1_reliability_r4.py`; adjusted regression tests in
`tests/test_w1_reliability_r2.py`, `tests/test_w1_reliability_r3.py`,
`tests/test_run_night.py`, `tests/test_b5_driver_p3.py`, `tests/align/test_v4_kit.py`,
`tests/align/test_v4_next_arm_packet.py`, `tests/align/test_v4_series.py`.

## Native limits and next exact step

No native recovery, clock-setting, launchd delivery/authentication or MLX
validation is claimed. No new MLX path was introduced. The lead must run the
review's native checks 1–11 outside this sandbox, including the real-process
`tests.test_b5_driver.LaunchTests.test_chain_digest_mismatch_is_a_flag_and_the_chain_runs`,
helper provisioning/digests/sudo query rules, OFF/zero/read-back, real
re-enumeration with a 30-second unplug, the >600-second outage stop, launchd
local-to-Air delivery and failed-network recovery, and normal/refusal/TERM/
SIGKILL restoration with a second dead-man fire. Run final PREQUAL/W1 smoke
and regenerate/sign the STRICT registration before arming. Watchdog branch-2
alarm closure and the rendered-plan dry-run remain separate lead gates.

For F-09, the committed window exporter must include the digest-authenticated
`courier_delivery` source pointing to `night/courier.delivery.json` when the
original `courier.json` says false. The release check consumes committed bytes
only; it does not follow a live custody path. This must be exercised by the
lead's network-down/dead-man/native next-arm check.

Next exact step: review these commits on the lead's integration line, complete
the native checks and fresh STRICT registration, then decide whether to arm.
No remaining code ruling was needed within the explicit branch-1 brief.

## Local commits

- `cc946a5cd` — preserve the supplied Fable review verbatim.
- `454d78142` — F-01–F-13/F-01t implementation, regression tests and regenerated closure evidence.
- This report is the subsequent local documentation commit.

No push was performed. The final working tree is expected clean after committing
this report; coordination-state paths are byte-unchanged from `297629a0d`.
