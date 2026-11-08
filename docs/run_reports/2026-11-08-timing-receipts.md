# Timing receipts implementation handoff — 2026-11-08

Branch: `perf/2026-11-08-timing-receipts`, based on
`origin/align/2026-11-08-v4-r11`. No push, network, model download, live
measurement, Block 5 analysis, restricted-directory access or external
filesystem inspection. Shared Git object reads were used for repository
code only. The named branch was already checked out and clean at intake.

The user task superseded the generated queue for this bounded [AGENT] work.
M0/stop-card/workspace intake found no active stop card. Coordination state
is deliberately untouched as instructed: no edits to `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, or `tests/test_gen_state.py`;
no kernel registration. No agents or external review services were launched.
The follow-on Opus review belongs to the lead.

## Local commits

- `3c9c47a4e` — `Add boundary-only timing receipts to existing capture journals`
  (implementation, tests and implementation note).
- This handoff is a separate report-only commit, titled
  `Record timing receipt verification and remaining integration gates`.

Both commits are local on the named branch; no push or registration.

## Result and limits

Boundary-only records now cover existing driver arm/dwell/settle, member G0,
bundle/result finalize, reporting/publication/copy/commit/push and watchdog
hold/release paths. Emission uses existing journals and no added fsync in a
measured member. Native G1/H receipts are reused rather than duplicated;
deferred H resume semantics are unchanged. The current reader is tested
through the proposal's offline timed-record projection, not claimed to
ingest marker JSONL natively. Details and clock/missingness limits:
`docs/perf/TIMING-RECEIPTS-IMPL.md`.

The synthetic driver now supplies its existing battery clock/runner seams;
otherwise real battery stamps prevented a meaningful whole-file byte proof.
Comparison is at the same source tree with markers disabled/enabled, including
raw event-byte equality after removing only the new marker lines. No claim
that registered source-attestation hashes stay unchanged.

**Not ready to claim a COMPLETE native W1/D turnaround ledger or to register.**
The R16 cool-down evaluator is absent from this base and the inspected
`origin/main` ALIGN code. A clarification was sent while independent work
continued. External/manual harvest, backup and push do not acquire markers
automatically from a driver hand-off. R0/R1-only and capability-launcher
insertion points are outside this patch's W1/D implementation. Reused
qualification dwell has no source wall stamps; only its existing monotonic
stamps/boot identity are copied. No missing interval is filled from a
configured wait, commit timestamp or guessed phase.

## Registration changed-file receipt

Every path in this change (lead must include the relevant transitive capture
dependencies in registration; no generated receipt/kit was rewritten here):

- `joulewise/timing_receipts.py`
- `joulewise/align/apple/thermal_gates.py`
- `joulewise/b5/driver.py`
- `joulewise/bundle.py`
- `joulewise/controller.py`
- `joulewise/hazards/arm.py`
- `scripts/align_v4_w1_synthetic.py`
- `scripts/magistrate_watchdog.py`
- `scripts/run_night.py`
- `tests/align/test_timing_receipts.py`
- `tests/test_magistrate_watchdog.py`
- `docs/perf/TIMING-RECEIPTS-IMPL.md`
- `docs/run_reports/2026-11-08-timing-receipts.md`

## Verification

Targeted unittest modules only, serially; no full-suite discovery. Python 3.13,
`-B` throughout. Later Git-using checks also set
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`.

Completed preliminary checks:

- `python3.13 -B -m unittest tests.align.test_v4_w1_synthetic.KitBridgeTests`
  — 4 passed before implementation (3.810 s); 4 passed after initial hooks
  (4.004 s).
- `python3.13 -B -m unittest tests.align.test_timing_receipts`
  — 10 passed (13.956 s) before the additional publication/OFF tests.
- `JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic`
  — 20 tests, OK, one pre-existing expected failure (137.274 s).
- `python3.13 -B -m unittest tests.test_magistrate_watchdog.BackoffAndEventTests`
  — 11 passed (0.123 s).
- `python3.13 -B -m unittest tests.test_run_night.Ruling76DriverTests`
  — 5 passed (2.593 s).

Additional/final focused checks:

- `JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_timing_receipts`
  — 12 passed (70.821 s), including byte comparison over the complete
  fault-injected W1 capture. One subsequent watchdog-reboot case was added;
  `python3.13 -B -m unittest tests.align.test_timing_receipts` then passed
  all 13 tests (23.446 s).
- `python3.13 -B -m unittest tests.test_bundle.RunBundleWriterTests`
  — 35 passed (35.384 s), including unchanged non-ALIGN event/finalize contracts.
- `python3.13 -B -m unittest tests.align.test_thermal_gate.GateTests tests.align.test_thermal_gate.HoldTests`
  — 31 passed (18.924 s), including deferred resume and exact token/hold behavior.
- `python3.13 -B -m unittest tests.test_magistrate_watchdog.TerminalWindowReleaseTests`
  — 22 passed (0.199 s), synthetic custody only.
- `python3.13 -B -m unittest tests.test_run_night.Ruling76DriverTests`
  — final 5 passed (1.271 s), after the journal/arm-only integration.
- Final `python3.13 -B -m unittest tests.align.test_timing_receipts`
  — all 14 passed (30.395 s), after adding the existing-worker context
  isolation regression. Only receipt identity crosses into that worker;
  unrelated observation contexts retain their original behavior.
- Final `JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic`
  — 20 tests, OK, one pre-existing expected failure (117.831 s).
- AST syntax parse of all 11 changed Python files — passed; no native imports
  or bytecode artifacts required. `git diff --check` — passed.

The reader integration requires code object `dc684b308` in the local Git
object store, also in CI. It is not fetched at test time or made a hidden
opt-in. The named object was available and the integration check passed here.
Recorded unittest runtimes, including exploratory failures and final reruns,
total approximately 9.9 minutes, serially, below the requested 20-minute cap.

An initial receipt-test run correctly exposed an invalid synthetic 10-second
G0 cap and a sandbox process-census limitation; the test now uses the existing
600-second registered cap and a synthetic cadence seam. The unmodified
existing positive-arm test was also attempted:
`python3.13 -B -m unittest tests.hazards.test_arm.ArmTests.test_quiet_float_mac_arms_go_in_the_registered_order`
— failed (2.695 s): `pgrep` cannot access the process table because the sandbox
has no `sysmond` service. This is not a native pass. The initial capture-byte
comparison also failed on real-clock battery fields; the synthetic seam fix
above resolves that source of nondeterminism.

Software-only overhead observation: 2,000 encoded markers into an open
`StringIO`, final source 20,165,875 ns total (~10.1 microseconds/marker),
1,363,783 bytes; earlier runs were ~11.4 and ~19.3 microseconds/marker.
No flush/fsync in either run.
No native disk/capture-overhead or throughput improvement is claimed.

## NEEDS_RULING / next exact step

Question: which code/ref owns the R16 evaluator, and which existing Python
owner will record manual desk harvest/offload/push boundaries?

Options considered: (1) silently treat the older R1 `idle-until-soak` as R16;
(2) add shell marker subprocesses or a new timing sidecar; (3) integrate at
the actual owners once supplied, using their existing open journals.
Recommendation: (3), preserving the user's markers-only rule. Blocked work:
actual R16 cooling receipts, external turnaround completeness, final native
verification and registration. Independent implementation/tests are preserved
for the promised Opus review.

Outside this sandbox, the lead must rerun the positive hazard-arm/cadence and
process-group checks, the full W1 synthetic regression at the final integrated
head, and the existing native MLX/thermal tests under the normal quiet-machine
protocol. MLX was not run here. No fixture result is live hardware validation.
The existing tiny native array command is
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`;
no weights are needed. The existing positive hazard-arm/cadence test also
needs a host where its own process group can be enumerated.
