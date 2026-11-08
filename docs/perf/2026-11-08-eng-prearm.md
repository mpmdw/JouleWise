# eng-prearm — static packet and terminal wake

Branch: `perf/2026-11-08-eng-prearm`, based on `origin/main` `c07b388e9`.
Implementation commit: `2f4cb41bd` (`perf: add immutable static pre-arm packets
and terminal watchdog wake`); this report follows in a documentation commit.
Authority: Ed's brief; latency synthesis `55029b860` §4 rank 5; the two latency
audits and two window-efficiency audits cited there; RUN_STATE 213–215.
Engineering only, synthetic inputs. **PROVISIONAL; no live arm/launchd or MLX
validation, and no production turnaround saving claimed.**

## Delivered

- `joulewise/prearm_packet.py`, `scripts/prearm_packet.py`: off-host execution
  of four original static validator commands; exact ordered stdout/stderr and
  exit codes; immutable exclusive publication; independently pinned recipe and
  packet digests. Verification executes no validators. It checks all declared
  input bytes, tree membership, executable status, plan/checkout pins and
  freshness. Expiry is bounded by the handoff, existing plan-age limit and
  receipt expiries. Mutation, failed validation, corruption, stale/future inputs,
  added files/directories, changed HEAD and traversal/symlinks refuse.
- `joulewise/terminal_wake.py`, `scripts/run_night.py`: atomic advisory marker
  after terminal reporting and durable courier outcome. Notification failure
  preserves the existing result and reporting exit code. Direct driver
  invocations without an explicit destination retain their previous behaviour.
- Night template and `joulewise/night_agent_install.py`: bind notification
  destination into the existing authenticated rendered-plist context.
- Magistrate template, installer and `scripts/magistrate_watchdog.py`:
  `WatchPaths` terminal wake, existing-file seed before bootstrap, normal
  watchdog gates, dedupe and at most 30 additional one-second retries for the
  writer-exit race. `StartInterval=300` and `RunAtLoad` remain. Advisory markers
  cannot release an open chain, bypass delivery/census/stop/clock/backoff gates,
  or start a continuous agent. A failed event acknowledgement retains a normal
  tick. This is a scheduling change, not new terminal-release authority.
- Synthetic tests, `scripts/bench_prearm_packet.py`, and
  [the interface/integration contract](../contracts/prearm_packet.md).

No estimand, threshold, registration, measurement runtime, raw evidence or
coordination state was changed. No network, model download, real study measurement
read, production pipeline, loaded job, hardware probe or full suite was run.

## Synthetic timing and equality

Reproduce with `python3.13 -B scripts/bench_prearm_packet.py --repetitions 7`.
Python 3.13.18; one process at a time, four deterministic CPU validators and
256 extra 4 KiB files (1 MiB). These are tiny synthetic checks, not measured kit
regeneration or the historical 95-minute activation-to-launch interval.

| Operation | Median | Range |
|---|---:|---:|
| Before: original four validators | 0.237025 s | 0.197586–0.279154 s |
| Off-host packet build, including both input snapshots | 0.516124 s | 0.441127–0.627175 s |
| After: host digest/identity/freshness verification | 0.134354 s | 0.117940–0.169561 s |
| Atomic marker publish + same-process read | 0.000808 s | 0.000635–0.001075 s |

Every baseline/packet result was exactly equal. Canonical ordered result digest:
`4e2dd7c9a335bd831d09f609a90631e12f33ed27f13fe03f4e45d4dab7f4b4bd`.
Static verification saved about 43% on this fixture. Build work moves off-host;
no claim about the production kit's speedup follows from this small fixture.
The marker timing excludes launchd scheduling, process exit and watchdog gates;
**it is not a measured wake latency**. The old poll phase contributes up to
300 s; its mean is 150 s only under a uniform completion-phase assumption.

## Verification

Failing-first evidence: `tests.test_terminal_wake` initially failed 7 cases
because the marker/API/WatchPaths did not exist; `tests.test_prearm_packet`
initially failed 9 cases because its implementation did not exist. The new
installer assertion separately failed on the absent watch-target seed before
the installer was changed.

Final commands use `python3.13 -B -m unittest`, one module at a time:

| Target | Result |
|---|---|
| `tests.test_prearm_packet` | 12 passed (6.63 s), including CLI pins and byte equality |
| `tests.test_terminal_wake` | 10 passed (0.19 s), including open-chain fencing and failure fallback |
| `tests.test_magistrate_watchdog.TerminalWindowReleaseTests` | 19 passed (0.10 s) |
| `tests.test_run_night.CourierDeliveryBoundaryTests` | 19 passed (15.75 s); fake transport, no email or push |
| `tests.test_night_agent_install.EvidenceRenderOnlyTests` | 15 passed (16.70 s final run); repository fixtures, no chain execution |
| `tests.test_night_agent_install.RenderedProcessTypeTests` | 2 passed (0.07 s final run) |
| `tests.test_install_magistrate_watchdog.InstallMagistrateWatchdogTests` (six methods below) | 6 passed (6.84 s); stub launchctl and shadow checkout |

The six installer methods were `test_rendered_plist_pins_canonical_checkout`,
`test_rendered_plist_pins_test_interpreter`,
`test_real_install_flow_seeds_lock_renders_plist_and_calls_launchctl`,
`test_failed_lock_seed_restores_exact_preexisting_plist_and_lock`,
`test_failed_bootstrap_restores_exact_preexisting_plist_and_absent_lock`, and
`test_failed_post_load_verification_restores_exact_preexisting_plist_and_absent_lock`.
Invoke them with the class prefix in the table using the same unittest command.

83 final targeted cases passed; repeated development runs also stayed well
under the 20-minute allowance. `python3.13 -B -m compileall -q joulewise tests
scripts/prearm_packet.py scripts/bench_prearm_packet.py
scripts/magistrate_watchdog.py scripts/run_night.py` and `git diff --check`
passed. The full suite is deliberately excluded under Ed's blinded-job rule.

## Integration decision and lead handoff

**NEEDS_RULING:** which ALIGN lane/head owns the production adapter and reviewed
recipe? Main at this task's base contains neither `scripts/align_v4_session.py`
nor `scripts/align_v4_kit.py`. The cited historical source is
`origin/lane/2026-11-06-v4-r1-integrated`; RUN_STATE 215 points registration
work to the newer `align/2026-11-08-v4-r11` lane. An asynchronous target question
was left with the lead during this run.

Options considered: import the entire older integration lane into main, or
deliver the shared tools here and connect the current owning lane separately.
Recommendation: the latter, with a recipe audited against that exact head.
**Blocked work:** replacing ALIGN's existing static checks with packet results.
No such check has been skipped. The packet facility is implemented and tested;
the production ALIGN adapter and production recipe remain unimplemented.
No lane patch is supplied because its correct target and dependency boundary
have not been settled. In particular, `night_gate.evaluate_static` contains
fresh time/window/checkout checks and must not be cached wholesale.

In a clean, lead-controlled MBP gap, after integrating the reviewed adapter:

1. Time the real original static checks versus packet verification on identical
   frozen inputs, compare their exact outputs, and record the complete inventory
   size and build/transfer/verify times. Mutate a synthetic copied input and
   exercise stale packet/receipt cases; each must refuse before arm side effects.
2. Retain fresh battery/thermal/disk/power-mode/volume, native runtime/model
   identity, boot/clock, notice/veto, single-use receipt, meter and quiet-dwell
   checks at their existing points. Native Metal/MLX qualifications remain
   lead-owned outside this sandbox; this change adds no MLX code or MLX tests.
3. Render/review/install the updated watchdog/night jobs through the normal
   procedures. New template/rendered digests require the ordinary pin/probe
   refresh; existing installed jobs are not changed by this branch.
4. With synthetic terminal records and stub jobs first, measure marker-to-tick
   and marker-to-activation separately. Test a driver still exiting, an active
   chain, live courier/agent, remote stop/backoff/uncertain clock, duplicate
   marker, absent marker and a suppressed/lost event. The lost-event case must
   recover through the unchanged 300 s tick. The nominal event target is
   0–30 s plus existing gate/probe latency, not a guarantee established here.
5. Only after those gates, benchmark a normal terminal-to-next-arm gap. Preserve
   cool-down and quiet dwell; do not credit fixture timing as hardware evidence.

The lead owns coordination updates and final arm/measurement authority. This
report is the handoff; RUN_STATE, TASK_QUEUE and the state kernel are untouched.
