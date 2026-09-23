# Feeder first-frame causality fix — report (seat, branch fix/2026-09-22-replay-feeder-first-frame-causality)

## The change (all in /Users/edr/code/JouleWise-wt-feeder-fix)

- `scripts/replay_powermetrics_frames.py:328` — `main()` takes `spawn_monotonic_s = time.monotonic()`
  as its FIRST statement, before argument parsing and before the digest pre-pass, and passes it to
  `run(args, spawn_monotonic_s)` (`:203`, defaulted for direct callers).
- `scripts/replay_powermetrics_frames.py:242` — frame *i* is due at
  `pacing_base + (cumulative elapsed_ns of frames 1..i)/1e9`, with `pacing_base = spawn`. Frame 1 is
  paced too (waits `elapsed_ns[0]` = 257.38 ms on envelope-01); later frames pace from spawn, not
  from the first write. `since_first_ns`/`first_write` are gone.
- `scripts/replay_powermetrics_frames.py:262` — under `--label-shift auto` the wall target for the
  shifted endpoint is still honoured; the LATER of the two constraints governs frame 1 and the
  cadence base is re-seated to it (`pacing_base = due - elapsed_ns[0]/1e9`). Without that re-seat a
  K-rounding wait of up to 1 s would leave frames 2..n already overdue and they would fire back to
  back, losing the archived cadence. Base never moves earlier than spawn, so the causality floor
  holds for every frame.
- `scripts/replay_powermetrics_frames.py:294-300` — sidecar gains `spawn_monotonic_s`,
  `first_write_delay_s` (observed), `first_frame_elapsed_s` (archived), and `first_write_late_s`
  = `max(0, first_write - first_due)`: a digest pre-pass slower than the first interval is recorded,
  never fatal. Module docstring and the WRITE_POLL_S note rewritten to the new pacing.
- Label shift, digests, source streaming, sidecar provenance and TERM/hold handling unchanged.

## Regression (tests/test_sample_quiet_predicate_evidence.py, BenchReplayRecorderSeamTests)

- `:1879 feed_watching_arrivals` — real feeder subprocess over the 3-frame fixture, polling the
  output every 2 ms and timing when each frame's terminating NUL becomes visible (the same event the
  collector's first-complete-frame poll waits on), on the parent's monotonic clock.
- `:1916 test_R7_no_frame_is_written_before_its_own_accumulation_has_elapsed` — frame 1 arrives no
  earlier than `elapsed[0] - 0.02`, frame 2 no earlier than `elapsed[0]+elapsed[1] - 0.02`, plus the
  four sidecar keys and `first_write_delay_s >= first_frame_elapsed_s` on the feeder's own clock.
- `:1957 test_R7_the_live_recorder_stamps_satisfy_the_deriver_causality` — the second assertion the
  brief asked for: a REAL `harness.ReplayRecorder` with `harness.Clock()` over the fixture
  (`start()` → 1 s → `finish()`), asserting
  `stamps['pre_spawn'].monotonic_before_s + elapsed_ns[0]/1e9 <= stamps['first_parse'].monotonic_after_s`.
  The existing machinery exposes `recorder.stamps`, so no new machinery was built.

## Kill tails (surgical: `due = time.monotonic()` for frame 1 — exactly the pre-fix pacing, sidecar keys kept)

```
FAIL: test_R7_no_frame_is_written_before_its_own_accumulation_has_elapsed
    self.assertGreaterEqual(arrivals[0] - spawn, elapsed[0] / 1e9 - 0.02)
AssertionError: 0.08094458299456164 not greater than or equal to 0.23738254100000003

FAIL: test_R7_the_live_recorder_stamps_satisfy_the_deriver_causality
    self.assertLessEqual(
        stamps["pre_spawn"].monotonic_before_s + elapsed[0] / 1e9,
        stamps["first_parse"].monotonic_after_s,
AssertionError: 343991.047691791 not less than or equal to 343991.007492666 : the deriver would call this stream clock_stamp_invalid

Ran 10 tests in 10.750s
FAILED (failures=2)
```
Restored (`grep -c KILL` = 0) → `Ran 10 tests in 10.846s / OK`.

## Exit tail

```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest \
  tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign
Ran 206 tests in 40.386s
OK
```

## git log --oneline origin/main..HEAD

```
6acad9e8 REPLAY-FEEDER-FIRST-FRAME-CAUSALITY-01: pace frame 1 from spawn, not from the digest pre-pass
```
Tree clean, nothing pushed, canonical untouched.

## Deviations
1. The `auto` cadence re-seat (`:262`) is beyond the literal dictate ("pace from spawn + elapsed[0]").
   Literal spawn-based pacing would have made every post-first frame instantly overdue whenever K's
   whole-second rounding delayed frame 1, collapsing the archived cadence. The floor the brief
   dictated still holds for every frame.
2. `first_write_late_s` is measured against frame 1's DUE instant (causality floor, or the `auto`
   wall target when later) rather than against `elapsed[0]` alone, so the deliberate `auto` wait does
   not read as lateness. A slow pre-pass still shows as > 0.
3. Four sidecar keys, not three (the brief's three plus `first_write_late_s`, which it also required).
4. No bench driver / smoke run, per the brief.

## NEEDS_RULING
None.
