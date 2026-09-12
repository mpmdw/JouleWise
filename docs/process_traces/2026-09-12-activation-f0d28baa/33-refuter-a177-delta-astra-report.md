```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One isolation-rule blocker: disconnecting the stressed adapter survives and allows the regression to pass without the bounded no-sleep cure.",
  "workspace": {
    "base_requested": "c85a171d",
    "base_mode": "exact",
    "head_start": "8a5d11690116671ee04643ead8f96a272bdd1ea5",
    "head_end": "8a5d11690116671ee04643ead8f96a272bdd1ea5",
    "upstream_end": "8a5d11690116671ee04643ead8f96a272bdd1ea5",
    "branch": "fix/2026-09-12-fixture-sentinel-controller"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "blocker",
        "path": "tests/test_controller.py",
        "line": 1652,
        "summary": "The regression does not protect its stress injection: deleting the adapter assignment passes, including with the no-sleep policy removed."
      }
    ],
    "same_signature": "No: the delta applies stress only inside the bounded-capture override.",
    "current_defect_shape": "Preserved: removing no-sleep alone produces TimeoutExpired, post_idle_unavailable, and both strict mismatches."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 74 tests in 51.756s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=no_sleep /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_delta_audit.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"fail","exit_code":1,"tail":["BOUNDED powermetrics_idle_post.plist count=58 scale=12.0 timeout=15.0","CAPTURE_EXCEPTION TimeoutExpired","Ran 1 test in 27.813s","FAILED (failures=1)"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=registry /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_delta_audit.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 18.540s","OK"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=registry A177_NO_SLEEP_CUT=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_delta_audit.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["BOUNDED powermetrics_idle_post.plist count=71 scale=1 timeout=15.325","Ran 1 test in 28.911s","OK"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short\ngit diff --exit-code\ngit diff --check c85a171d..HEAD\ngit rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["8a5d11690116671ee04643ead8f96a272bdd1ea5","8a5d11690116671ee04643ead8f96a272bdd1ea5"]},
      "expected": {"exit_code":0,"tail_regex":"8a5d11690116671ee04643ead8f96a272bdd1ea5"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Hosted Linux was not executed; the original CI-red attribution remains probable.",
      "needs": "Lead reruns PR #324 CI after adjudicating R1."
    }
  ]
}
```

## Findings

**R1 — blocker: essential stress clauses survive isolated cuts.** At [test_controller.py:1652](/Users/edr/code/JouleWise-wt-a177/tests/test_controller.py:1652), replacing `registry.adapter_type = StressedSentinelAdapter` with `pass` leaves the selected regression green. Removing `--no-sleep` as a subsequent counterfactual also leaves it green: **71 samples, scale 1, timeout 15.325 s; `Ran 1 test in 28.911s` / `OK`.** This demonstrates that the surviving wiring cut disables detection of report 19’s defect.

Lowering the floor and neutralizing the bounded environment patch also survive independently. These satisfy the brief’s explicit blocker criterion. Lead action: add coverage that fails when the effective bounded stress is disconnected or insufficient to exceed the unchanged capture timeout.

No should-fix or nit findings.

All cuts used the selected test `tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`, recompiled **in memory** by this [temporary harness](/private/tmp/a177_delta_audit.py). [Logs](/private/tmp/a177-delta-audit-results/) retain full results. Each row is a separate invocation; `FAILED` below means `FAILED (failures=1)`.

External scale was 1 except `env_override` (20), `outer_reset` (12), and the default-value check (unset).

| Cut ID / isolated change | Result |
|---|---|
| `control`: unchanged method | Ran 1 test in 13.900s; OK |
| `floor`: lower minimum 12 → 3.5 | Ran 1 test in 13.731s; OK — survived |
| `default`: fallback `"12"` → `"1"`, external unset | Ran 1 test in 21.494s; OK — redundant with floor |
| `env_override`: replace environment lookup with 12 | Ran 1 test in 14.938s; OK — survived |
| `stress_patch`: bounded `str(scale)` → `"1"` | Ran 1 test in 15.390s; OK — survived |
| `registry`: remove stressed adapter assignment | Ran 1 test in 18.540s; OK — survived |
| `outer_reset`: remove outer 1× reset | Ran 1 test in 18.737s; FAILED — admission timeout |
| `inheritance`: inherit production adapter directly | Ran 1 test in 11.054s; FAILED — admission refused |
| `forward`: replace bounded super-call with empty bytes | Ran 1 test in 14.482s; FAILED — unknown drift |
| `drift_message`: remove strict problems from assertion message | Ran 1 test in 13.898s; OK — survived |
| `strict_compute`: replace strict validation result with `[]` | Ran 1 test in 11.600s; OK — survived |
| `strict_expectation`: remove final strict-result assertion | Ran 1 test in 14.874s; OK — survived |
| `msg_status`: remove diagnostic field | Ran 1 test in 13.118s; OK |
| `msg_failure_reason`: remove diagnostic field | Ran 1 test in 13.544s; OK |
| `msg_failure_message`: remove diagnostic field | Ran 1 test in 13.974s; OK |
| `msg_idle_baseline`: remove diagnostic field | Ran 1 test in 14.087s; OK |
| `msg_measurement_quality`: remove diagnostic field | Ran 1 test in 14.336s; OK |
| `msg_environment_admission`: remove diagnostic field | Ran 1 test in 15.250s; OK |
| `msg_uncertainty_evidence`: remove diagnostic field | Ran 1 test in 13.206s; OK |
| `msg_telemetry`: remove diagnostic field | Ran 1 test in 17.104s; OK |

The diagnostic cuts survive successful executions; they do not independently remove report-19 detection. Likewise, the bounded-drift assertion still catches that defect when strict validation is neutralized. No expected status/count values were weakened by the delta.

**Defect shape at intact HEAD is preserved.** Removing only the shared bounded `--no-sleep` policy produced:

```text
BOUNDED powermetrics_idle_post.plist count=58 scale=12.0 timeout=15.0
CAPTURE_EXCEPTION TimeoutExpired
AssertionError: 'unknown' != 'bounded'
Ran 1 test in 27.813s
FAILED (failures=1)
```

The failing assertion is line 1677. Its message contains `{'reason': 'post_idle_unavailable', 'status': 'unknown'}` and both:

- `strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation`
- `strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation`

**Fast-host arithmetic:** admission requests 30 paced records at 50 ms, so baseline duration is at least 1.5 s and post count \(n\) is between 30 and 100. The fixture sleeps before every record, including the first. At 12×, required sleeping is \(0.6n\) seconds; production timeout is \(\max(15,\ 10+0.075n)\). Throughout that range, sleeping alone exceeds timeout—starting at **18 > 15 seconds**. Thus the intact 12× stress cannot finish inside timeout merely because the host is fast.

At a weakened 3.5× floor, 30 records require only **5.25 < 15 seconds**. My additional floor-plus-no-sleep counterfactual nevertheless timed out locally at 71 records: `Ran 1 test in 33.433s` / `FAILED (failures=1)`. The disconnected-registry counterfactual above demonstrated an actual cure-independent pass.

**CI diagnostics are now exposed.** Lines 1666–1667 include `"failure_reason": summary.failure_reason` and `"failure_message": summary.failure_message`. The outer-reset cut actually printed:

> `'failure_reason': <FailureReason.UNKNOWN_ERROR: 'unknown_error'>, 'failure_message': 'powermetrics admission stream did not complete the idle slice before timeout'`

This addresses the previous opaque assertion; no diagnostic should-fix found.

**Same-signature line — stress applied anywhere other than the bounded sentinel: NO.** `tests/test_controller.py:1645–1649` scopes stress to `_run_bounded_capture`; line 1653 resets surrounding execution to 1×. Observed stressed calls were exclusively `powermetrics_idle_post.plist`.

Requested suite, run once with the venv interpreter: **`Ran 74 tests in 51.756s` / `OK`.** No repository files changed; HEAD stayed pinned and the tree ended clean.

## Residual risk

Hosted Linux remains unverified. These were synthetic fixture tests, not live hardware validation. Temporary replay artifacts are outside the repository.