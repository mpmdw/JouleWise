# Quiet-machine calibration kit

This is non-claim calibration tooling. It reads no calibration ledger, head pin,
or block-5 session. All collection is lead-operated with agents absent. The kit's
desk tests use hardware seams.

```
/opt/homebrew/bin/python3.13 scripts/quiet_kit.py --plan
/opt/homebrew/bin/python3.13 scripts/quiet_kit.py --status
/opt/homebrew/bin/python3.13 scripts/quiet_kit.py --arm --model-python /Users/edr/code/JouleWise/.venv/bin/python
/opt/homebrew/bin/python3.13 scripts/quiet_kit.py --disarm
```

The director performs the live plumbing check (default M5, shortened, explicitly
not a measurement):

```
/opt/homebrew/bin/python3.13 scripts/quiet_kit.py --plumbing-check
```

It writes only beneath `threshold-validation/_plumbing/<stamp>/`, measures each
hazard once, shortens the dwell/sampler/clock probes, and never sleeps the display
or runs the wake command. Other tests can be selected with `--test`; unchanged
model runs may exhaust the 570-second plumbing deadline. Such a check retains
its partial captures and writes an incomplete analysis, never measurement output.
Raw instrument bytes keep their original format; the local kind marker and every
entry of the result's raw-file catalog identify them as plumbing-check bytes.

`--run` uses a lock, append-only numbered attempts, and an atomic result/summary
completion pair. Agents require ten continuously clean minutes before collection
and after a sighting. Failed physical preflights wait until the job deadline;
three consecutive failed non-sampler probes become flags. Thermal and battery
events inside a test flag overlapping segments; an agent interrupts the attempt.
The whole job permits at most three attempts per test, including the second pass.

The network-time OFF action is recorded once per job; this kit never turns it on.
The clock logger and no-sleep assertion are job-owned children. A crash preserves
earlier results and all raw bytes. SIGTERM/SIGINT stop owned test groups and record
teardown evidence; a restart allocates a new attempt. Prior child journals are
recovered only when both kernel birth identity and boot identity still match;
unverifiable leftovers end the job with a director-action record and wake-up.
The clock child also exits if its parent dies. `WAKE_DONE` is created before
the detached wake command, so even an uncertain wake launch is never repeated.

Reanalysis reads saved bytes and calls the same pure analysis functions:

```
/opt/homebrew/bin/python3.13 scripts/quiet_kit.py --reanalyze m4-contention-watts
```

M3 saves a frozen step-time clock snapshot and both step/end analyses; its final
analysis uses the longer job-wide series. Resumed jobs retain their own primary
clock logs, combine them with explicit per-job code and condition provenance,
and fit each continuous boot/gap segment separately. An agent retry allocates a
fresh analysis attempt while the job-wide logger continues. M3 distinguishes the longest observed
kit sampler stream from the waiting-proper stream that must come from the fault
rehearsal. No timing stop line or block-6 exclusion threshold is chosen here.

## Ruled schedules and analysis

M10 runs two 1,140-second palindromes: idle, CPU, idle, GPU, idle, mixed,
idle, mixed, idle, GPU, idle, CPU, idle. Idle segments last 60 seconds;
load segments last 120 seconds at full duty (mixed adds one full CPU core).
Analysis retains the segment fits and adds per-repeat level means and fits:
two segments per load level, all seven symmetric idle segments for the idle
level. A charger-supplied level mean requires every constituent segment to
have battery readings within 200 mA; the labelled second fit retains all levels.
Missing constituents make that level mean undefined, including in the analysis
that omits flagged segments.

M2b (`m2b-short-baseline`) follows M2. It runs five N/S/S/N quads with no
long waits. N preserves the reference config's 57.6-second nominal idle
setting; S changes only `sampling.idle_seconds` to 50.0, besides run_id/tags.
Both arms use the unchanged controller. The run table records the config
setting, child exit status, bundle refusal reason, and delivered idle duration
summed from the canonical raw idle plist records; retry captures are listed too.
Failed S runs remain in the table and make the test incomplete with
`short_baseline_refused_by_run_path`. They never enter a complete-quad estimate.
The plan includes both ruled tests; the default deadline remains twice its
total plus six hours.

Owned process groups receive SIGTERM, with a direct leader TERM if group
signalling lacks permission. The kit polls for absence and retries the leader
halfway through a minimum 10-second sampler, 30-second capture, or 60-second
model grace. KILL requires a fresh census proving all remaining members are
the kit user. A surviving root member blocks escalation and later tests;
`root_sampler_orphan` records its PID, argv, and group in the attempt,
journal, STATUS, and DONE before the wake-up. Plumbing prints the action and
exits nonzero. Unreadable UIDs also forbid KILL and require director action.

Display endpoints use CoreGraphics in the GUI session (main display,
asleep, active); unavailable reads carry a reason. IODisplayWrangler output
is retained only as a diagnostic. The deliberate display-sleep request precedes
the measurement's start observation.

## Desk verification

```
export TMPDIR="$PWD/.scratch-qk/tmp" PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR"
/opt/homebrew/bin/python3.13 -m unittest tests.quiet_kit
/opt/homebrew/bin/python3.13 -m unittest tests.test_battery_float_sweep tests.hazards.test_refusal_allowlist
```

Tests include independently computed uncertainty arithmetic, production plist,
KM003C byte encoding, CLI bundle summaries, ps and sntp formats, a synthetic
known-offset capture, the existing `controller_g2b/block3-pre` fixture, and both
runner-level and real-segment-executor hardware fakes. The bounded fake sudo and sampler children are registered in
`tests/fixture_signatures.json`; tests reap both processes, including on failure. The director must verify live launch context, sudoers, model execution,
SMC/thermal/display diagnostics, sampler cadence and ownership, meter presence and
edges, network-time OFF, and the detached wake path before unattended use.
