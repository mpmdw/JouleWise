# OSCTX-MVP-01 diagnostic harness

This is diagnostic evidence, not a claim-bearing campaign. The lead owns live execution. Use the pinned Python on the target Mac. `config.json` names the production D-117 source config and per-stage `runs_per_cell` values. `stage0U` is fixed at three I/SH blocks with two runs per cell. Rehearsal is one I/SH block with one run per cell, in the configured state (A by default).

Run the rehearsal in its own directory. It can be analyzed alone, but its cells are refused in any real-stage or session analysis. A real session pauses network time once before `stage0U` and restores it after final analysis, including on error or signal. The installed `scripts/joulewise-network-time.sudoers` rule must permit the exact fixed argv.

```sh
PY=/Users/edr/code/JouleWise/.venv/bin/python
REHEARSAL=/private/tmp/osctx-mvp-rehearsal
ROOT=/private/tmp/osctx-mvp-session
$PY scripts/diagnostics/osctx_mvp/runner.py --stage rehearsal --render-only "$REHEARSAL" --python "$PY"
$PY scripts/diagnostics/osctx_mvp/runner.py --session U --render-only "$ROOT" --python "$PY"
# Live execution is a separate, lead-owned operation:
# $PY scripts/diagnostics/osctx_mvp/runner.py --stage rehearsal --out "$REHEARSAL" --python "$PY"
# $PY scripts/diagnostics/osctx_mvp/analyze.py "$REHEARSAL"
# $PY scripts/diagnostics/osctx_mvp/runner.py --session U --out "$ROOT" --python "$PY"
```

The session performs `stage0U`, power analysis, the mechanical freeze, U1, conditional U2, S, and final root analysis. `freeze.json` is written before U1 and cannot be overwritten. The candidate grid is `(6 blocks, 1 run)`, `(6, 2)`, `(12, 1)`, `(12, 2)` ordered by estimated U-stage wall time. At 1.5 times the U-scale paired SD, the cheapest candidate with at least 0.80 EQUIVALENT power on all four primary tests and at most 180 minutes is selected. The D/I SD uses the SH/I proxy. If none qualifies, `(12, 1)` is frozen with `underpowered_by_prereg`. A 12-block freeze always runs U2; a 6-block freeze runs U2 only when U1 has an INCONCLUSIVE primary verdict. `session.json` records step outcomes and reasons.

Single stages remain available with `--stage NAME --render-only DIR` or `--stage NAME --out DIR`. A standalone live stage pauses and restores network time around the stage. `analyze.py power --stage0-summary DIR/summary.json` accepts a `stage0U` summary for a separate sizing inspection; the session itself writes `power.json` and `freeze.json`. Session sizing estimates cover U cells, the two B controls, and the I warm-up. `S` is the three-phase U–S–U display sandwich.

U1 starts with a discarded I warm-up cell, runs the Williams blocks, then the B controls. U cells require 600 seconds of HID idle. The S runner verifies display transitions, waits 120 seconds, and restores display-on state. The runner passes its ancestors as the census allowlist; add `--allow-pid PID` for other lead-owned processes. SH is a contemporary shell reference, not proof of the July policy.

Each cell records ancestry, QoS, census, source and materialized config hashes, child `ps` and ancestry, production bundle paths, three CPU probes of at least five seconds, and a 60-second settle. Each production child passes `--post-window-sampling-dwell-s 60`; the `done.json` marker is written last. A failed bundle or undeclared precheck invalidates the whole cell and reruns the same block order, at most twice. Three failures of one block abort the stage. Three distinct invalid cells in one arm stop the stage for council review. `summary.json` and `summary.md` report E, R, secondary power and uncertainty quantities, drift and edge bounds, census flags, hashes, discarded attempts, paired and widened intervals, and the exploratory S contrast. E is idle-subtracted J per 512 output tokens; R is inter-token throughput. The cell mean uses its production runs.
