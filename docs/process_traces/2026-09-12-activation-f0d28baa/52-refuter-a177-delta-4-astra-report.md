```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two mechanism cuts survive; production-floor and cure-removal counterfactuals fail as predicted; controller suite passes.",
  "workspace": {
    "base_requested": "74a547cd",
    "base_mode": "exact",
    "head_start": "572dcb58a7f885a4cbe6f871146a268877a962bd",
    "head_end": "572dcb58a7f885a4cbe6f871146a268877a962bd",
    "upstream_end": "572dcb58a7f885a4cbe6f871146a268877a962bd",
    "branch": "fix/2026-09-12-fixture-sentinel-controller"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "R1", "severity": "should_fix", "path": "tests/test_controller.py", "line": 1651, "summary": "Recording a different config with power_hz=40 survives; the config witness is not bound to the observed sampling interval."},
      {"id": "R2", "severity": "should_fix", "path": "tests/test_controller.py", "line": 1691, "summary": "Replacing the production timeout call with zero survives; the new observation mechanism can be removed without failing the regression."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 74 tests in 72.933s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONPATH=/private/tmp/a177-g50-audit:$PWD A177_CUT=timeout_zero /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_g50.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 19.603s", "OK"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONPATH=/private/tmp/a177-g50-audit:$PWD A177_CUT=production60 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_g50.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 20.200s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**No blocker found.**

**R1 — should-fix:** The config-recording mechanism accepts a substituted config with `sampling.power_hz=40.0`, although capture ran at 20 Hz. The test’s argv check validates the separately recorded interval, not the config consumed by `_capture_timeout_s`. In this run the production floor masks the altered timeout input: `33.6 > 15.0` still passes.

**R2 — should-fix:** Replacing the timeout-producing call with `0.0` passes: `32.400000000000006 > 0.0`. This cuts the new mechanism producing the observation; it leaves the comparison unchanged. Classification follows the brief’s explicit mechanism boundary. The huge constant **does not survive**: `45.0 > 1e100` fails as predicted.

No nit found. No terminal-oracle deletion or weakening is reported.

**Same-signature: YES — the delta adds mechanism clauses without a killer for the demonstrated substitutions.**

All cuts compiled source in memory and selected only `test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`. Replay V2 with the corresponding `A177_CUT`; [driver](/private/tmp/a177-g50-audit/a177_g50.py) and individual logs remain in that temporary directory.

| Cut ID | Mechanism cut | Ran/result | Exit |
|---|---|---|---|
| `config_none` | Recorded config → `None` | Ran 1 test in 15.052s; FAILED (errors=1), `AttributeError` on `.sampling` | 1 |
| `config_other` | Recorded config → replaced config, 40 Hz | Ran 1 test in 19.259s; **OK** | 0 |
| `timeout_zero` | Timeout call → `0.0` | Ran 1 test in 19.603s; **OK** | 0 |
| `timeout_huge` | Timeout call → `1e100` | Ran 1 test in 16.256s; FAILED (failures=1), inequality | 1 |
| `production60` | Production timeout floor 15 → 60 | Ran 1 test in 20.200s; FAILED (failures=1), inequality only | 1 |
| `cure` | Remove bounded `--no-sleep` append | Ran 1 test in 29.806s; FAILED (failures=1), first strict validation | 1 |

For `production60`, diagnostic instrumentation wraps the original inequality assertion in a unittest subtest, recording its failure and continuing through the unchanged remainder. Both strict validations returned `[]`; drift remained bounded. Exact excerpts:

```text
STRICT []
INEQUALITY 36.6 > 60.0
STRICT []
REMAINDER COMPLETED: every other assertion passed
AssertionError: 36.6 not greater than 60.0 : this bounded capture must time out if --no-sleep is removed
Ran 1 test in 20.200s
FAILED (failures=1)
```

The cure cut reproduces report 19:

```text
CAPTURE_EXCEPTION TimeoutExpired
DRIFT {'reason': 'post_idle_unavailable', 'status': 'unknown'}
STRICT ['strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation', 'strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation']
Ran 1 test in 29.806s
FAILED (failures=1)
```

Mirror check:

```sh
sed -n '1625,1770p' tests/test_controller.py | rg -n '15\.0|1\.5 \+ 10'
```

No output; exit 1 (no matches).

The committed assertion is:

```python
self.assertIsInstance(registry.adapter, RetryAdmissionPowermetricsAdapter)
```

Instance wiring is confirmed by the registry assigning `self.adapter = self.adapter_type(...)` and returning `self.adapter, None`; the regression sets `adapter_type = StressedSentinelAdapter`. The assertion checks its type, while that wiring establishes it is the returned execution instance.

The venv controller suite ran **once**:

```text
Ran 74 tests in 72.933s
OK
```

Final `git status --short` was empty. No repository files changed. Next step: lead adjudication of R1/R2 under ruling 50 Q1.

## Residual risk

Synthetic fixture evidence only. Hosted CI, full repository discovery, and live hardware validation were outside this audit.