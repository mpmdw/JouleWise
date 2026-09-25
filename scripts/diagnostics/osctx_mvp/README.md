# OSCTX-MVP-01 diagnostic harness

This is a diagnostic of macOS launch context. Its results are not claim-bearing.
The lead runs all live cells. Use the JouleWise Python environment on the target Mac.

```sh
PY=/Users/edr/code/JouleWise/.venv/bin/python
ROOT=/private/tmp/osctx-mvp-01
$PY scripts/diagnostics/osctx_mvp/runner.py --render-only "$ROOT/render"
$PY scripts/diagnostics/osctx_mvp/runner.py --out "$ROOT/attended" --state A
$PY scripts/diagnostics/osctx_mvp/runner.py --out "$ROOT/unattended" --state U
$PY scripts/diagnostics/osctx_mvp/runner.py --out "$ROOT/display-sleep" --state S
$PY scripts/diagnostics/osctx_mvp/analyze.py "$ROOT/attended"
```

For one combined summary, run all states into one `--out` directory, or copy
the three state cell directories into a common analysis directory and
concatenate their census JSONL files. `--render-only` writes plists and `command_sequence.json` without
starting anything. Inspect them before the lead runs a state. The default order,
segments, model, thresholds, and timeout are in `config.json`; `--config` selects
another JSON file. The runner uses its invoking Python interpreter unless
`--python` selects another. It writes `events.jsonl` and `census.jsonl` in the
run directory. Each cell writes `cell.json`, raw `powermetrics.plist`, and a
last-written `done.json`; failures also write `error.json`.

The unattended gate checks HID idle before every cell and records any pause.
Display sleep is requested before every S cell and restored after the state.
The analyzer derives the clock anchor with the production estimator and refuses
unresolved anchors. `summary.json` and `summary.md` include per-cell values,
paired directions, verdicts, and census flags. A missing state leaves its
decision pending. A cell failure remains visible in the summary.

The lead can probe a cell without a sampler using `cell.py --no-powermetrics`
and `--lm-repeats 1`; this still runs the configured workloads and writes a
done marker. It is only a workload smoke check; the analyzer requires raw
powermetrics data.
