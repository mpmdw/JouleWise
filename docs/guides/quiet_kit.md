# Quiet-machine calibration kit

The kit is one unattended program that takes the calibration measurements the block-6 design asks for before its
rules are written (`docs/design/block6_collection_draft.md` section 8, items M1 to M5, M9, M10, M13, M14 and M15;
`docs/design/next_block_threshold_proportion.md` section 4, tests 1, 2, 7, 8, 11, 13 and 15, and section 8.3). It runs
under launchd with no agent session alive and writes everything under
`/Users/edr/night-archive/threshold-validation/`. These are calibration measurements: no claim, no registration, no
seal. The kit reads no block-5 session and no calibration ledger; every path it touches passes one fence
(`joulewise/quiet_kit/paths.py` `fence`) that refuses the blinded roots.

## The command

All modes are one script, run with the stdlib interpreter:

```
/opt/homebrew/bin/python3.13 /Users/edr/code/JouleWise-wt-quiet-kit/scripts/quiet_kit.py --plan
/opt/homebrew/bin/python3.13 /Users/edr/code/JouleWise-wt-quiet-kit/scripts/quiet_kit.py --arm
/opt/homebrew/bin/python3.13 /Users/edr/code/JouleWise-wt-quiet-kit/scripts/quiet_kit.py --status
/opt/homebrew/bin/python3.13 /Users/edr/code/JouleWise-wt-quiet-kit/scripts/quiet_kit.py --disarm
```

- `--plan` prints the ordered schedule, each test's estimated minutes and their basis, what is already complete on
  disk, and the total estimated wall hours (11.3 h at this commit, hazard waits excluded). It writes nothing.
- `--arm` writes the launchd job `com.joulewise.quiet-kit` from `configs/launchd/com.joulewise.quiet-kit.plist.template`
  to `threshold-validation/launchd/`, lints it, boots out any loaded copy and bootstraps it in the GUI domain. The
  job runs at load (`RunAtLoad`), with `ProcessType` `Interactive` (the default launch context throttles powermetrics
  to about 248 ms records). The plist is not in `~/Library/LaunchAgents`, so a restart or logout ends the job and a
  later `--arm` resumes it. The repository the job runs is the checkout `--arm` was run from; every result records
  its commit and `git status`.
- The model, GPU-load and capture children run under `--model-python`, default
  `/Users/edr/code/JouleWise/.venv/bin/python` (MLX 0.31.2); the kit itself runs under the stdlib python.

Before arming: put the wake-up command in `threshold-validation/WAKE_CMD` if one is wanted, then end every agent
session. The job does nothing measurable until the agent census has been clean for 10 minutes in a row.

## What the job does

1. Starts a no-sleep assertion (`caffeinate -i -s -w <pid>`), runs the network-time OFF setter once (never ON),
   and starts the clock logger, which reads CLOCK_REALTIME and CLOCK_MONOTONIC_RAW every 10 s for the whole job.
2. Waits for 10 continuous minutes with no agent process (the census of `joulewise.hazards.arm.agent_census`).
3. For each test without a complete result, in order: a preflight, the test, its analysis.
4. After the schedule, one more pass over incomplete tests. Then it writes `DONE` and, once, runs `WAKE_CMD`
   (guarded by `WAKE_DONE`, created first).
5. A deadline (default twice the estimate plus 6 h, about 28.6 h) ends the job with `DONE` listing what is
   incomplete, then the wake-up, so a hazard that never clears still ends in a wake-up.

The preflight measures each physical hazard with the existing hazard modules and waits while it holds: an agent
alive, on battery or charging beyond 200 mA, thermal pressure above 0, an outside process above 0.05 CPU-s/s
(180 s clean dwell), too little free disk (the test's planned bytes plus 20 GiB), the sampler not delivering records
at a median of 150 ms or less, the clock stepping or drifting beyond budget. Each wait is a line in
`threshold-validation/journal.jsonl`. It records, and never refuses on, whether `mediaanalysisd` and `photoanalysisd`
run and their CPU time, the screen saver, the display state (CoreGraphics), keyboard or mouse input during the test,
and whether the wall meter is present. During a test a watcher re-censuses agents every 30 s and reads thermal level
and battery current every 10 s: an agent interrupts the attempt (retried after the hazard clears, at most three
attempts per test per job); thermal pressure or battery current flags the segments it overlaps, and the result is
reported both with and without them.

## Results

Each test has `threshold-validation/<test-id>/attempts/<n>/` (raw capture, logs, the preflight record) and, when
complete, `result.json` (each measured quantity with its unit and uncertainty, the flags, the conditions, the raw
files with their hashes, the code identity, the analysis function's name) and `summary.md` (one plain paragraph). A
test is complete only when its main quantities are defined (for example, five complete quads for M2); otherwise its
attempt is kept and the test is retried. A rerun skips complete tests. Attempts are never deleted or reused.
`--reanalyze <test-id>` recomputes a result from an attempt's raw files with the same pure analysis function.

| Order | Test | Question | About |
|---|---|---|---|
| 1 | `m4-contention-watts` | Watts per CPU-second of one busy core at 5, 20 and 100%, background and interactive; energy of phase-length bursts against what a 10 s accounting interval reports (note test 1, 2; council Q1) | 25 min |
| 2 | `m5-gpu-rail` | Graphics-rail level at idle and under a CPU-only load; watts a GPU contender adds that the CPU-time census misses (note 8.2 item 2) | 23 min |
| 3 | `m1-capture-stop-line` | Alignment-capture bounds on a quiet machine (10), under one busy core (4), in the throttled launch context (4); how often a quiet capture exceeds 36.46 ms; the range left for one stop line on the operative bound (note test 15) | 84 min |
| 4 | `m2-long-wait` | Phase energy after a 20-minute idle against the ordinary 85 s, 5 N L L N quads (note test 8) | 4.3 h |
| 5 | `m2b-short-baseline` | Phase energy with the idle baseline shortened to `idle_seconds` 50.0 (about 65 s), 5 N S S N quads (draft section 14) | 55 min |
| 6 | `m3-clock-rate` | Clock rate with network time off, fitted over at least 3 h of the job's clock log; the rate budget at the longest observed stream | logged throughout |
| 7 | `m9-time-server` | Scatter of one query-only `sntp` reading, two servers, 10 minutes (note test 11) | 15 min |
| 8 | `m14-meter-idle-power` | Whether the wall meter sees outside power directly, GPU and CPU steps (draft M14) | 28 min |
| 9 | `m13-meter-edges` | Wall-meter edge timing against pulse commands and the sampler (draft M13) | 18 min |
| 10 | `m10-rails-vs-wall` | Rails against the wall meter over steady loads in a palindrome, charger-supplied levels fitted (note test 13) | 43 min |
| 11 | `m15-drift-transfer` | Drift of the reference, the 1.7B and the 8B workloads between start and end blocks around a 90-minute soak (note test 7) | 2.1 h |

No test chooses a threshold. Limits that depend on the smallest printed floor are written as formulas of a
parameter `F_min_J`; nothing reads a block-5 number.

## Checks that are not measurements

`--plumbing-check [--test <id>]` runs the preflight once in record-only form (shortened dwell, sampler and clock
reads) and one test at a reduced time scale, into `threshold-validation/_plumbing/<stamp>/`, marked
`plumbing_check`. It never writes a real test directory, `DONE`, `STATUS` or `WAKE_DONE`, and does not sleep the
display. A capture test runs only its first capture, at full protocol length. Desk tests:
`python3.13 -m unittest discover -s tests/quiet_kit -t .` from the worktree, with a TMPDIR whose path holds neither
"claude" nor "codex".

## Known limits at this commit

- The model-run path (`python -m joulewise run` on the reference, 1.7B and 8B configs) is tested on real CLI bundles
  with mock backends only; its first real run is M2 in the first job.
- M10, M13 and M14 need the KM003C meter and the charger carrying the load; a level with battery current beyond
  200 mA is flagged and left out of the charger-supplied fit.
- The throttled launch context of M1 is approximated with `taskpolicy -c utility`; each such capture records its
  delivered sampler cadence and whether it exceeded 200 ms.
- Teardown sends SIGTERM to each owned process group (sudo relays it to a root powermetrics) and never SIGKILLs a
  group while a root member lives; a root member that survives ends the job with a director-action record.
