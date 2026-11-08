# Timing receipts: Opus cross-family cold review

2026-11-08. Reviewer: Claude Opus 5.5 (cross-family; Sol 6.1 built the change).
Target: `origin/perf/2026-11-08-timing-receipts` @ `5fc873136` (base `8d0dabc73`).
Integration target: `origin/align/2026-11-08-v4-r11` @ `1a2574b49`. W1 integration item 6 (RUN_STATE 228).
Line numbers refer to `5fc873136` unless marked `1a2574b49`. Rules: `origin/main:docs/perf/SPEED-TOOLBOX.md` §"Timing receipts: markers only". Reader and spec:
`origin/fix-timing` @ `dc684b308` (`joulewise/align/window_timing.py`, `docs/perf/TIMING-RECEIPTS.md`).

Only synthetic data was used: fake clocks and temporary directories. No measurement, custody or restricted
record was read. All runs used `python3.13 -B` with a realpath'd scratch `TMPDIR` and
`GIT_CONFIG_GLOBAL=/dev/null`.

## Verdict: **HOLD**

The marker mechanics are sound. Inside a measured member there is no fsync, flush, open, thread or process,
and there are no sample-rate markers. Two placements break existing record contracts, though, and the branch
fails three existing CI gates, both on its own and when merged into the v4 head. All of these fixes are
small. Re-review only the deltas.

## Findings

### HIGH-1: every ALIGN member bundle now fails `validate_bundle`, so the harvest marks every W1 member strict-invalid

- **`joulewise/bundle.py:1040-1044`.** `_append_timing_boundary` writes markers straight into the
  held-open `events.jsonl` stream.
  - The controller buffers every ordinary event in memory and writes them only at the reduce stage, in
    timestamp order (`joulewise/controller.py:3923-3940`).
  - So the G0 markers land at lines 1-2, ahead of the buffered `run_started` and with later timestamps.
- **`joulewise/bundle.py:1233`.** The `bundle_finalize` span's end marker is appended after `run_finalized`.
- **`joulewise/bundle_read.py:2958-2966` (D-025 structural check).** This check now fails for every ALIGN
  bundle, with two problems:
  - `events.jsonl timestamps are not non-decreasing`
  - `events.jsonl last event is 'timing_boundary', expected 'run_finalized'`
- **The harvest's `strict_problems` uses this check.** See `joulewise/b5/harvest.py:2199-2204` and `:2254-2256`.
  - `strict_valid` therefore becomes False for every member.
  - `member.strict_validation_failed` is emitted for each one (`:4126`).
  - Each member drops out of the valid-bundle set (`:4468-4469`).
  - The ALIGN desk runs this harvest through `scripts/harvest_b6_session.py`
    (`scripts/align_pilot_session.py:311`).
- **The order is deterministic in production, not only under the fake clock.** With `SystemClock` the G0
  marker's wall stamp is later than `run_started` but is written first. The finalize end marker always
  follows `run_finalized`.
- **The fake clock adds one more inversion.** `clock_stamp` rounds the epoch to integer nanoseconds, so an
  equal-time marker can sort before the event it follows (`joulewise/timing_receipts.py:31-36`).
- **Evidence.** This was a cross-tree run of the full W1 synthetic (20 bundles), validated with
  `joulewise.cli.validate_bundle`:
  - At `1a2574b49` the structural problem list is `[]` for 20 of 20 bundles.
  - At the merge it is those 2 problems for 20 of 20.
  - Strict problems are otherwise identical. The pre-existing synthetic-only uncertainty-evidence problems
    are unchanged.
- **Why the branch's tests missed it.** No W1 synthetic test calls the bundle validator. The branch's own
  capture-equality test strips the marker lines before comparing.
- **Witness.** `tests/align/test_timing_receipts_opus_witnesses.py::MemberBundleWitnesses`. It fails on the
  branch and on the merge, and passes on `1a2574b49`.
- **Fix, either of:**
  - (a) Emit bundle markers as `RuntimeEvent`s through the controller's buffer, so the stable sort places
    them. Close the finalize span before `run_finalized`; summary persistence can be bracketed by the
    night driver's `night_result` span.
  - (b) An explicit validator rule that skips `event_type == "timing_boundary"` rows in the order and
    last-event checks. This changes `bundle_read.py`, which is registered, so it needs registration.

  Option (a) keeps the validator frozen and is preferred.

### HIGH-2: the driver writes into the child chain's stage journal, creating it before any chain runs and leaking markers into desk records

- **The parent never had this file open.** `chain-stages.jsonl` belongs to the generated chain shell
  (`joulewise/b5/chain.py:943`, `>> "$STAGE_JOURNAL"`).
  - `_timing_journal` opens it with `open("a")` before admission: `scripts/run_night.py:2543-2563`, entered
    at `:4519` and in `arm_only` at `:2575`.
  - On every pre-chain refusal, and in every arm-only custody, the driver now creates a file that did not
    previously exist. This breaks SPEED-TOOLBOX's "Create no new files". The implementation note's phrase
    "the existing night/chain-stages.jsonl" is wrong for the pre-chain case.
- **Downstream semantics change.**
  - **Harvest stage journal.** `joulewise/b5/harvest.py:7450-7465` returns `None` "when the chain wrote no
    journal"; it now returns `[]`.
  - **Collection presence.** `collection_presence` (`:7466-7478`) flips from True to False and emits
    `chain.stopped_before_collection`. This changes `collected` (`:7905`).
  - **Yield record.** `derived/yield.json.stage_journal` (`:7496-7498`) changes from `null` to
    `{"stages": 0}`.
  - **Missing-record defect.** `joulewise/session_structure.py:34-36` lists `night/chain-stages.jsonl` as a
    required record. The `record_class_missing` defect it raised for a chain that never ran is now hidden.
- **The happy path changes too.** `session_structure.check` turns every journal row into a public `stages`
  entry (`:135`, `:283-287`), so each driver marker appears there as a null stage. The v4 registration binds
  this module (`joulewise/align/apple/v4_registration.py:240` on the branch, `:252` at `1a2574b49`).
- **Witness.** `tests/align/test_timing_receipts_opus_witnesses.py::StageJournalWitnesses`. Both cases fail
  on the branch and on the merge.
- **Fix.** Write driver markers only to a journal the driver itself already has open before admission.
  - `censuses.jsonl` is appended just before (`run_night.py:4513`); audit its readers first.
  - Alternatively, hold pre-chain markers in memory and append them once the chain journal exists.
  - Also filter `kind == "timing_boundary"` in `session_structure` and in the harvest's
    `stage_journal`/`collection_presence`.

  Any path that still creates a file needs a lead deviation ruling against the markers-only rule.

### HIGH-3: the branch fails existing CI gates, on its own head and on the v4 merge

These were run on `5fc873136` and on the scratch merge `e370e8c25`.

- **`tests.align.test_v4_executed_closure`.** `joulewise/timing_receipts.py` is a new import of
  `bundle`, `controller`, `hazards/arm`, `b5/driver`, `thermal_gates`, `run_night` and the watchdog, but it
  is missing from `EXECUTED_CLOSURE` (`joulewise/align/apple/v4_registration.py:54` on the branch, `:64` at `1a2574b49`).
- **`tests.align.test_v4_dynamic_closure`.** The same module is absent from
  `docs/align/v4/dynamic_closure_trace.json`.
- **`tests.test_run_night` reason-code lint.** The literal call sites `@timing_receipts.timed("finalize",
  "night_result")` (`run_night.py:2108`) and `producer="night_driver"` (`:2553`) trip
  `test_driver_reason_codes_are_registered_and_are_not_literal_call_sites`. That test passes on
  `1a2574b49`.

The failing tests are themselves the witnesses. Fixing them changes the registered closure, so this is a
re-registration (STRICT tier), which the implementation note already anticipates.

### MEDIUM-1: the byte-identity proof does not compare against the pre-change code and fails on a real Mac

- **It never compares against the old code.** `tests/align/test_timing_receipts.py:357` patches
  `Writer.emit` within the same source tree. The "markers off" run therefore already includes the held-open
  stream, the extra `clock.stamp()` and the changed synthetic battery seams.
- **It fails every time on this host.**
  - Without `JW_WP22_FULL` it failed 2 of 2 runs.
  - With `JW_WP22_FULL=1` it failed 3 of 3, on the branch and on the merge.
  - The cause is `metadata.json` `process_rss_bytes` (real RSS in the cleanup memory snapshots). Sol's
    sandbox evidently did not report RSS.
- **What I ran instead.** A cross-tree comparison of the full W1 synthetic, `1a2574b49` (plus only the same
  synthetic battery seam) against the merge.
  - It ignores marker lines and normalizes only RSS, source provenance (`git_commit`, `diff_sha256`,
    `tracked`, `claim_eligible`, `reason_codes`) and worktree paths.
  - The result is identical file sets and no semantic differences, apart from traceback line numbers in one
    `controller.log`.
  - So the capture bytes are unchanged apart from the markers and their placement (HIGH-1).
- **Fix.** Seam or normalize RSS, and compare against the base tree's output rather than a patched emit.

### MEDIUM-2: completeness is shown only for invented spans; the real synthetic window still has 814.7 s unattributed

- **Reader run on real producer output.** I ran the pinned reader (`read_window`) over the full W1 synthetic:
  20 bundles plus the projected and refined marker spans.

  | Source set | Wall | Unattributed |
  |---|---|---|
  | Merge, bundles only | 12,376.1 s | 898.1 s |
  | Merge, bundles plus marker spans | 12,376.1 s | 814.7 s |
  | Base `1a2574b49` | 12,376.1 s | 898.1 s |

- **Where the remaining time sits.** All of it is inside member envelopes, under `measured_run`.
  - The 600 s G0 timeout in `e08` stays unattributed. The reader gives bundle stages priority 20, above the
    priority 15 of `--span` records.
  - The synthetic has zero inter-member gaps and no driver, so it cannot test turnaround at all.
- **The 647 s / zero-unattributed test is hand-built.** Its spans are constructed in the test
  (`test_complete_nested_turnaround_parses_in_pinned_reader`); they do not come from the producers.
- **Uninstrumented turnaround.**
  - The whole v4 arm: `scripts/align_v4_session.py:380-511` at `1a2574b49`, including `arm_checks`, the 3 s meter probe,
    the packet rebuild, the W1 disk gate and the installer hand-off. Its `quiet_dwell` record holds only
    monotonic `start_ns` and a wall `now_s`.
  - R16 cool-down. It exists on `origin/align/2026-11-08-condition-waits-impl` (not merged), inside the
    hazard arm's dwell (joint start state).
  - Chain settles and launch barriers.
  - Harvest, desk, backup and push, which are off the MBP under R17.
- **Answer to check 2: no.**

### LOW

- **LOW-1. The dwell start marker falls inside the recorded dwell.** In `joulewise/hazards/arm.py:280` the
  span opens after `dwell_started`, `_boot()` and the first clock sample (`:277-279`). It causes one write
  and flush, and a later page writeback, inside the quiet dwell. It does not fsync. Move it above `:277`.
  The OFF-settle sleep marker (`run_night.py`, `_admit_network_time_off`) behaves the same way, but that
  interval is turnaround.
- **LOW-2. Watchdog per-transition overhead and a schema extension.** `_hold_boundaries`
  (`scripts/magistrate_watchdog.py:1793`) builds a `Writer` on every `transition()` call, which costs a few
  clock reads per tick. Reason-only boundaries do an open/write/close without fsync (`:1848`).
  `terminal_release` gains a `paired_stamp` field (`:2150-2161`); no reader is strict about it.
- **LOW-3. Member markers are buffered in memory until the reduce-stage flush.** A crashed member loses its
  G0 start, against the spec's "persist the start before the operation". This is disclosed and is the right
  trade-off for measurement safety.
  - The held-open stream also replaces per-event open/append/close with write and flush, which happens only
    at reduce.
  - On failure paths it relies on `__del__` (`bundle.py:957`) to close the stream.
- **LOW-4. A flaky test unrelated to receipts.**
  `tests.test_b5_driver_p3.DeadManMeterTests.test_the_reaper_reads_the_named_journal` failed once under
  concurrent load and passed on two reruns on both trees.

## Check 1: measurement safety (writers instrumented)

- **Audit-hook run.** I ran the full W1 synthetic at the merge under a Python audit hook and an `os.fsync`
  wrapper. Each was attributed only from `Writer.emit`/`_emit` frames.
  - 68 marker emissions in total, about 4 per member: G0 start/end and `bundle_finalize` start/end.
  - Zero `open`, `os.*`, `subprocess`, `_thread` or `socket` audit events.
  - Zero fsync calls.
  - Mean 21 µs per emit under concurrent load.
- **Member markers stay in the stream buffer** until the existing reduce-stage event flush, so no syscall
  happens inside a measured member segment.
- **No marker is emitted at sample rate.** No loop is instrumented, and the per-turn G1/H receipts are reused.
- **Driver markers** come to roughly 15-25 per window. Each is one write and flush (no fsync) on the
  turnaround path, all before the chain or after it returns.
- **The watchdog** shares the transition append, and reason-only changes are not fsynced.
- **Capture bytes:** unchanged apart from the markers, by cross-tree comparison. See MEDIUM-1 for method and
  HIGH-1 for placement.

## Check 3: integration with `origin/align/2026-11-08-v4-r11` @ `1a2574b49`

The merge into a scratch worktree is clean (`e370e8c25`). Results there:

| Suite | Result |
|---|---|
| `JW_WP22_FULL=1 tests.align.test_v4_w1_synthetic` | 22 tests, OK (1 expected failure) |
| `tests.align.test_timing_receipts` | 13 of 14 pass; the capture-equality test fails (MEDIUM-1) |
| `JW_WP22_FULL=1 tests.align.test_timing_receipts` | same; capture-equality fails |
| `test_bundle`, `test_bundle_read` | 156, OK |
| `test_magistrate_watchdog`, `_span`, `_b6`, `_yield`, `_cli` | 218, OK |
| `test_thermal_gate`, `hazards.test_arm` | 69, OK |
| `test_controller`, `test_axi_controller_events`, `test_controller_battery_float`, `test_controller_hazard_flags` | 152, OK |
| `test_v4_next_arm_packet`, `test_v4_cadence`, `test_v4_w1_blockers`, `test_v4_kit` | 190, OK |
| `test_b5_driver`, `_p2`, `_p3` | 124; one flake (LOW-4) |
| `tests.test_run_night` | 318; 1 failure (HIGH-3 lint) |
| `test_v4_executed_closure`, `test_v4_dynamic_closure`, `test_v4_registration` | 36; 2 failures (HIGH-3) |

- **The v4 head's new arm features are untouched by this change.** It neither touches nor instruments the
  arm-rebuilt packet or the probe-before-dwell rule (`align_v4_session.arm_checks`).
- **Conflict with R16.** A trial merge of `condition-waits-impl` onto the receipts merge adds one conflict,
  in `joulewise/hazards/arm.py` (the dwell call). The other conflicts in that trial already occur against
  the v4 head alone.
- **Labelling after R16 lands.** The `hazard_clean_dwell` span would cover R16's joint cool-down, labelled
  `dwell` rather than `idle/cooldown`.

### Receipt-bound files touched

- **In `EXECUTED_CLOSURE`, and so in the receipt artifact set:**
  - `joulewise/bundle.py`
  - `joulewise/controller.py`
  - `joulewise/hazards/arm.py`
  - `joulewise/b5/driver.py`
  - `scripts/magistrate_watchdog.py`
- **In `_NAMED_ARTIFACTS`:**
  - `joulewise/align/apple/thermal_gates.py`
  - `scripts/run_night.py`
  - `scripts/align_v4_w1_synthetic.py`
- **In `STRICT_SCRIPTS`:**
  - `scripts/run_night.py`
  - `scripts/magistrate_watchdog.py`
- **New, and missing from the closure (HIGH-3):** `joulewise/timing_receipts.py`.
- **Not receipt-bound:**
  - The tests: `tests/align/test_timing_receipts.py` and `tests/test_magistrate_watchdog.py`.
  - The three docs and run reports.

## Check 4: observer cost

- **No measurable cost.** No marker path adds a thread, timer, poll or sampler, so there are no wake-ups.
- **CPU** is about 10-21 µs per marker, for tens of markers per window, all at phase boundaries.
- **Inside members,** markers cost no I/O until reduce.
- **Unlike R16.** The R16 sampler failure mode was a periodic observer running into the start state; nothing
  here runs periodically.
- **Remaining start-state contact** is one write and flush at the dwell start and at the OFF-settle start
  (LOW-1). Moving the dwell start marker above `dwell_started` removes the in-dwell one.

## Re-review scope after fixes

1. The HIGH-1 placement fix, including the witness and `validate_bundle` on all 20 synthetic bundles.
2. The HIGH-2 journal choice, plus filters in `session_structure` and the harvest.
3. The closure, the trace and the lint (HIGH-3).
4. A deterministic cross-tree capture comparison (MEDIUM-1).

Then integrate after R16 lands, re-place the dwell or cool-down spans, and register.
