# OSCTX-MVP-01 diagnostic harness

This is diagnostic evidence, not a claim-bearing campaign. The lead owns live execution. Use the pinned Python on the target Mac. `config.json` names the production D-117 source config and the per-stage `runs_per_cell` values. Stage 0 is fixed at two runs per cell. Freeze the U counts and Williams block count (a multiple of six) after stage-0 sizing and before U1.

Render every stage to inspect its `command_sequence.json` and job plists:

```sh
PY=/Users/edr/code/JouleWise/.venv/bin/python
ROOT=/private/tmp/osctx-mvp-01
$PY scripts/diagnostics/osctx_mvp/runner.py --stage stage0 --render-only "$ROOT/stage0" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage U1 --render-only "$ROOT/U1" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage U2 --render-only "$ROOT/U2" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage S --render-only "$ROOT/S" --python "$PY"
```

Run and analyze stage 0, then publish the sizing table before U1:

```sh
$PY scripts/diagnostics/osctx_mvp/runner.py --stage stage0 --out "$ROOT/stage0" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/analyze.py "$ROOT/stage0"
$PY scripts/diagnostics/osctx_mvp/analyze.py power --stage0-summary "$ROOT/stage0/summary.json"
```

The power output covers D/I and SH/I, E and R, and paired SD multipliers 1, 1.5, and 2 over six and twelve blocks. Stage 0 contains I and SH only; the D/I table uses the SH/I paired spread as an explicitly labelled proxy. It also reports within-cell run SD and between-cell paired SD. Stage-0 observations are attended with agents active: drift may be an upper bound, while spread is not presumed conservative. The lead freezes stage sizes and U `runs_per_cell` before U1.

Then run U1 and analyze it. U2 requires an inconclusive U1 primary verdict and the U1 summary. S is the three-phase U–S–U display sandwich. Analyze each stage and finally the parent directory:

```sh
$PY scripts/diagnostics/osctx_mvp/runner.py --stage U1 --out "$ROOT/U1" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/analyze.py "$ROOT/U1"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage U2 --out "$ROOT/U2" --python "$PY" --u1-summary "$ROOT/U1/summary.json"
$PY scripts/diagnostics/osctx_mvp/analyze.py "$ROOT/U2"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage S --out "$ROOT/S" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/analyze.py "$ROOT/S"
$PY scripts/diagnostics/osctx_mvp/analyze.py "$ROOT"
```

U1 starts with a discarded I warm-up cell, runs the Williams blocks, then the B controls. U cells require 600 seconds of HID idle. The S runner verifies display transitions, waits 120 seconds, and restores display-on state. The runner passes its ancestors as the census allowlist; add `--allow-pid PID` for other lead-owned processes. SH is a contemporary shell reference, not proof of the July policy.

Each cell records ancestry, QoS, census, source and materialized config hashes, child `ps` and ancestry, production bundle paths, three CPU probes of at least five seconds, and a 60-second settle. Each production child passes `--post-window-sampling-dwell-s 60`; the `done.json` marker is written last. A failed bundle or undeclared precheck invalidates the whole cell and reruns the same block order, at most twice. Three failures of one block abort the stage. Three distinct invalid cells in one arm stop the stage for council review. `summary.json` and `summary.md` report E, R, secondary power and uncertainty quantities, drift and edge bounds, census flags, hashes, discarded attempts, paired and widened intervals, and the exploratory S contrast. E is idle-subtracted J per 512 output tokens; R is inter-token throughput. The cell mean uses its production runs.
