This complete non-claim bundle was written by the real `python -m joulewise run`
path through `quiet_kit.collectors.model_run`, using the reference workload and
the stdlib Python interpreter. No bundle JSON was hand-authored or corrected.
The desk transform sets both hardware backends to `mock`, `idle_seconds` to
0.5, and `warmup_seconds` to 0.1; model files are never loaded.

Replay from the repository root (use a fresh destination):

```
TMPDIR="$PWD/.scratch-qk/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" /opt/homebrew/bin/python3.13 -m joulewise run tests/fixtures/quiet_kit/run_bundle/config.json --runs-dir .scratch-qk/fixture-replay
```

The integration tests in `tests.quiet_kit.test_model_cli` regenerate 20 N/S/S/N
runs, one R/A/B/B/A/R start block, and 20 N/L/L/N runs on each invocation, then
compute expectations directly from the CLI's JSON. The short-baseline desk
transform changes both arms to the same mock sampling duration; production
uses no transform and retains the ruled 50.0-second S baseline.
