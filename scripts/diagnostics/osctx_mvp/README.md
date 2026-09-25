# OSCTX-MVP-01 diagnostic harness

This diagnostic is not claim-bearing. The lead runs every live smoke and cell.
Use `/Users/edr/code/JouleWise/.venv/bin/python` on the target Mac. The
registered seed, stage sizes, model, prompt, guards, and thresholds are in
`config.json`.

Render each stage before a live run:

```sh
PY=/Users/edr/code/JouleWise/.venv/bin/python
ROOT=/private/tmp/osctx-mvp-01
$PY scripts/diagnostics/osctx_mvp/runner.py --stage stage0 --render-only "$ROOT/stage0"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage U1 --render-only "$ROOT/U1"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage U2 --render-only "$ROOT/U2"
$PY scripts/diagnostics/osctx_mvp/runner.py --stage S --render-only "$ROOT/S"
```

The `command_sequence.json` in each stage names every block and command.
Live execution uses `--out` in place of `--render-only`. Start with stage0,
then analyze its directory and run
`$PY scripts/diagnostics/osctx_mvp/analyze.py power --stage0-summary "$ROOT/stage0/summary.json"`
before U1. The lead uses that table to decide
whether the registered stage sizes provide 80% equivalence power at 1.5× the
observed paired SD. If they do not, change the sizes before U1 capture; the
Williams stages must still contain all six orders once per six-block stage.

U1 starts with a discarded I warm-up cell, runs six Williams blocks, then
runs B twice. Analyze it before U2. U2 is permitted only if a primary U1
verdict is INCONCLUSIVE and requires `--u1-summary $ROOT/U1/summary.json`.
S runs last as a three-by-three U–S–U sandwich. The runner verifies each
display transition against both a display-state read and `pmset -g log`, then
waits 120 seconds. Every U cell is gated on 600 seconds of HID idle.
The runner passes its own ancestor PIDs as the census allowlist; repeat
`--allow-pid PID` for any additional lead-owned session process. SH is a
contemporary shell reference, not proof of the July process policy.

To reduce all stages together, run `analyze.py $ROOT`. It uses the production
powermetrics clock anchor and interval integrator. `summary.json` and
`summary.md` carry request-level energy, paired intervals, verdicts, census
flags, output hashes, discarded attempts, and exploratory S intervals.
Interrupted cells discard their whole block; a retry uses fresh directories
with the same arm order. Labels stay under `com.joulewise.dummy.osctx.`.

Cells write `cell.json`, `census.jsonl`, raw `powermetrics.plist`, and a
last-written `done.json`. `--no-powermetrics` is only for workload smoke; its
cell cannot enter the analyzer. No model or GPU verification is possible from
an offline fake-backend run.
