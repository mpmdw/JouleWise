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

## Pending specification

M10's collection order needs a lead ruling: the brief says ABBA twice but names
three load levels (CPU, GPU, GPU+CPU). Its analysis and generic collectors exist;
the runner records `needs_ruling` instead of choosing an order. The plan's current
9.662-hour subtotal excludes M10, and the default deadline uses that subtotal.
The two proposed orders are CPU/GPU/mixed/mixed/GPU/CPU twice, or two pairwise ABBA
blocks (CPU/GPU and GPU/mixed), twice. The choice changes collection time and the
observations entering the fit.

Draft §13.2 also requires a short-baseline M2 arm without specifying its setting or
order. This kit implements the brief's exact five N/L/L/N quads; the short arm
needs a specification and is flagged in M2 results. Source configs are copied with only run_id/tags changed.
The nominal `idle_seconds=57.6` setting is preserved; delivered sampler cadence,
not that nominal setting alone, determines the actual baseline duration.

## Desk verification

```
export TMPDIR="$PWD/.scratch-qk/tmp" PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR"
/opt/homebrew/bin/python3.13 -m unittest discover -s tests/quiet_kit -t .
```

Tests include independently computed uncertainty arithmetic, production plist,
KM003C byte encoding, CLI bundle summaries, ps and sntp formats, a synthetic
known-offset capture, the existing `controller_g2b/block3-pre` fixture, and both
runner-level and real-segment-executor hardware fakes. They start no fixture
processes. The director must verify live launch context, sudoers, model execution,
SMC/thermal/display diagnostics, sampler cadence and ownership, meter presence and
edges, network-time OFF, and the detached wake path before unattended use.
