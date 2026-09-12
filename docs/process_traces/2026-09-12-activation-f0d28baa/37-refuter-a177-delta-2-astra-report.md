```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Stress-wiring cuts now fail, but real strict-validator delegation remains unprotected; one redundant drift assertion also found.",
  "workspace": {
    "base_requested": "8a5d1169",
    "base_mode": "exact",
    "head_start": "0ff8ac046a1a370d08bb94b2140653942c41d2a1",
    "head_end": "0ff8ac046a1a370d08bb94b2140653942c41d2a1",
    "upstream_end": "0ff8ac046a1a370d08bb94b2140653942c41d2a1",
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
        "line": 1710,
        "summary": "Replacing either real-validator delegation with a canned empty result survives; replacing both passes with zero real-validator calls.",
        "related_line": 1829
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "path": "tests/test_controller.py",
        "line": 1830,
        "summary": "The final helper invocation repeats the bounded-status assertion on the same previously checked drift snapshot."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 74 tests in 58.464s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=combined /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_r2_refuter.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"fail","exit_code":1,"tail":["Ran 1 test in 26.382s","FAILED (failures=1)"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=no_sleep /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_r2_refuter.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"fail","exit_code":1,"tail":["CAPTURE_EXCEPTION TimeoutExpired","Ran 1 test in 29.333s","FAILED (failures=1)"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_EXTRA=strict_wrap_both /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_r2_extra.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 17.885s","OK","REAL_VALIDATOR_CALLS 0"]},
      "expected": {"exit_code":1,"tail_regex":"FAILED"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short\ngit diff --exit-code\ngit diff --check 8a5d1169..HEAD\ngit rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["0ff8ac046a1a370d08bb94b2140653942c41d2a1","0ff8ac046a1a370d08bb94b2140653942c41d2a1"]},
      "expected": {"exit_code":0,"tail_regex":"0ff8ac046a1a370d08bb94b2140653942c41d2a1"}
    }
  ],
  "flags": []
}
```

## Findings

**R1 — blocker: real strict-validation wiring is unprotected.** At lines 1710 and 1829, independently replacing `wraps=validate_bundle` with `return_value=[]` survives. Replacing both also survives, with **zero calls reaching the real validator**. `assert_called_once_with` verifies the outer mock; the negative probes exercise the helper using separate mocks.

The previously listed R1 cuts are killed, but these newly introduced delegation clauses fail the requested isolation rule. Add a negative strict-result case through each actual validation boundary so disconnecting delegation fails. This is a coverage blocker; the intact timeout counterfactual still fails correctly.

**R2 — should-fix: duplicate bounded-drift assertion.** The final helper call repeats line 1707 against the same `drift` dictionary checked before reduction. One isolated input mutation, changing only that dictionary’s status to `unknown`, kills the first check. Suppressing only that first assertion lets every intervening check complete and kills the final identical check:

- First check: `Ran 1 test in 17.894s`; `FAILED (failures=1)`.
- First suppressed, final check retained: `Ran 1 test in 21.902s`; `FAILED (failures=1)`.

Drop the final repeated bounded-status assertion; retain post-reduction strict validation. A direct `self.assertEqual(validate_bundle(bundle_path, strict=True), [])` can replace the final helper/mock block.

**No incidental host-value pin found.** Capture count `1` describes the fixture lifecycle. Post-sample count remains dynamically derived. The timeout equality pins the production formula, `max(15.0, nominal_s * 1.5 + 10.0)`, rather than observed wall time. No replacement bound is needed. No nit findings.

**Same-signature: YES, a third class—unprotected strict-validation wiring; NO recurrence of “stress on the wrong capture (CI-red)” or “unprotected stress wiring.”**

Clauses were enumerated from the final code before reading report 35. Every row below ran the selected `HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` once, with source mutations applied in memory.

[Main harness](/private/tmp/a177_r2_refuter.py), [additional delegation cuts](/private/tmp/a177_r2_extra.py), [duplicate-check probe](/private/tmp/a177_r2_overbuild.py), [logs](/private/tmp/a177-r2-refuter-logs/).

Replay main rows using V3’s command with the named `A177_CUT`; † rows use V4 with `A177_EXTRA`. External scale was `1`, except `override` and `stress_override` (`20`), and `outer_reset` (`12`). `timeout_bypass` is the harness alias for the timeout-read-to-zero cut.

`F1` means `FAILED (failures=1)`; `F2` means `FAILED (failures=2)`.

| Cut / clause removed or weakened | Observed result | Catch |
|---|---|---|
| control | Ran 1 test, 17.305s; OK | Baseline |
| default: 12 → 1 | Ran 1 test, 14.861s; F1 | Stress policy |
| floor: 12 → 3.5 | Ran 1 test, 13.343s; F2 | Policy, effective floor |
| override: environment operand → 12 | Ran 1 test, 16.026s; F1 | Higher-scale policy |
| scale_call → 1 | Ran 1 test, 14.584s; F1 | Effective floor |
| stress_patch → 1 | Ran 1 test, 14.150s; F1 | Effective floor |
| stress_override → 12 | Ran 1 test, 15.753s; F1 | Effective override |
| registry assignment removed | Ran 1 test, 14.301s; F1 | Missing capture record |
| combined: registry + no-sleep removed | Ran 1 test, 26.382s; F1 | Missing capture record |
| outer_reset removed | Ran 1 test, 19.006s; F1 | Admission timeout |
| inheritance → production adapter | Ran 1 test, 6.778s; F1 | Admission refused |
| forward → empty bytes | Ran 1 test, 12.472s; F1 | Unknown drift |
| command_forward bypasses fixture policy | Ran 1 test, 31.085s; F1 | Timeout, unknown drift |
| command_record removed | Ran 1 test, 15.131s; F1 | Missing bounded command |
| command_kind → continuous | Ran 1 test, 13.837s; F1 | Missing bounded command |
| record_count → count + 1 | Ran 1 test, 14.870s; F1 | Timeout/count consistency |
| record_interval → doubled | Ran 1 test, 15.415s; F1 | Timeout/interval consistency |
| record_scale → 1 | Ran 1 test, 14.900s; F1 | Effective floor |
| record_timeout → 999 | Ran 1 test, 15.457s; F1 | Production timeout formula |
| timeout_bypass: timeout read → 0 | Ran 1 test, 16.825s; F1 | Production timeout formula |
| strict_compute → [] | Ran 1 test, 14.965s; F1 | Mock called zero times |
| strict_flag → false | Ran 1 test, 15.354s; F1 | Exact call arguments |
| strict_expectation removed | Ran 1 test, 15.612s; F1 | Negative probe |
| drift_message omits strict result | Ran 1 test, 17.505s; F1 | Missing strict diagnostic |
| continuous_filter → [] | Ran 1 test, 15.155s; F1 | Continuous-command presence |
| bounded_filter → [] | Ran 1 test, 15.678s; F1 | Bounded-command presence |
| no_sleep removed | Ran 1 test, 29.333s; F1 | Report 19 signature |
| continuous_no_sleep added | Ran 1 test, 0.772s; F1 | Fixture rejects continuous flag |
| capture_record removed † | Ran 1 test, 18.352s; F1 | Missing stress record |
| command_return → [] † | Ran 1 test, 0.471s; F1 | Failed summary |
| strict_wrap_first → canned [] † | Ran 1 test, 17.943s; **OK** | Survives; one real call |
| strict_wrap_last → canned [] † | Ran 1 test, 19.987s; **OK** | Survives; one real call |
| strict_wrap_both → canned [] † | Ran 1 test, 17.885s; **OK** | Survives; zero real calls |

The required combined stress cut completed at **85 samples, scale 1, timeout 16.375 seconds**, then failed with `0 != 1 : bounded stress was not exercised`.

Removing bounded `--no-sleep` alone produced these reason lines:

```text
CAPTURE powermetrics_idle_post.plist count=66 scale=12.0 timeout=15.0
CAPTURE_EXCEPTION TimeoutExpired
AssertionError: 'unknown' != 'bounded'
{'reason': 'post_idle_unavailable', 'status': 'unknown'}
strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation
strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation
Ran 1 test in 29.333s
FAILED (failures=1)
```

The requested venv controller suite ran **once**: `Ran 74 tests in 58.464s` / `OK`. Final `git status --short` was empty; HEAD stayed unchanged. No repository files were modified.

## Residual risk

Hosted CI and full repository discovery were not run. Evidence is from synthetic fixture tests, not live hardware validation.