```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Integrated D-176 seats 2+3; named acceptance passed: 514 tests, one existing skip.",
  "workspace": {
    "base_requested": "02ea7e05a71dea95e4c5f4094d30f15130f336dd",
    "base_mode": "exact",
    "head_start": "02ea7e05a71dea95e4c5f4094d30f15130f336dd",
    "head_end": "02ea7e05a71dea95e4c5f4094d30f15130f336dd",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "tests/test_arm_readiness.py",
    "tests/test_arm_readiness_lifecycle.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_launch_window.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_night_gate tests.test_run_night tests.test_t0_rehearsal tests.test_rehearse_t0_unattended tests.test_night_plan_writer tests.test_install_night_agent tests.test_magistrate_watchdog tests.test_arm_readiness_schemas tests.test_arm_readiness_lifecycle tests.test_launch_window tests.test_arm_readiness tests.test_d078_reason_registry tests.test_docs_freshness > /tmp/d176-acceptance-final.log 2>&1; rc=$?; tail -35 /tmp/d176-acceptance-final.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 514 tests in 608.440s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check > /tmp/d176-diff-check.log 2>&1; rc=$?; cat /tmp/d176-diff-check.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import subprocess; result = subprocess.run([\"git\", \"grep\", \"-n\", \"-E\", \"^(<<<<<<< |=======$|>>>>>>> )\", \"--\", \"*.py\", \"*.md\"], capture_output=True, text=True); assert result.returncode == 1, result.stdout + result.stderr; print(\"NO_CONFLICT_MARKERS\")' > /tmp/d176-marker-check.log 2>&1; rc=$?; cat /tmp/d176-marker-check.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["NO_CONFLICT_MARKERS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^NO_CONFLICT_MARKERS$"
      }
    }
  ],
  "flags": []
}
```

## Change

Preserved both seats’ contract rows and schema tests, ordered §10.2 before §10.3, and updated §7.1 and implementation pins. Installed the sixth-key pack binding, consumption digest check, rehearsal census predicate and named strict-custody refusal.

The integrated fixture at [tests/test_launch_window.py:2031](/Users/edr/code/JouleWise-wt-int-d176/tests/test_launch_window.py:2031) exercises:

1. Preparation → ARM → GO → eight-flag argv: `scripts/run_night.py:1108,1114,1176,1255`.
2. Launcher: `scripts/launch_window.py:263`.
3. Consumption → authenticated replay: `joulewise/arm_readiness.py:10227,10097`.

Preparation and GO digest mutations are covered at `tests/test_run_night.py:2047`; the deferred consumption mutation at `tests/test_arm_readiness.py:2448`; identical-tree root substitution and digest binding at `:2455`.

## Verification notes

Initial fixture incompatibilities were repaired. The existing skip concerns a synthetic repository lacking its family-publication marker.

The integrated fixture uses synthetic machine probes and ARM issuance/semantics; the separate real minted-ARM launch regression also passed. [Final acceptance log](/tmp/d176-acceptance-final.log).

No NEEDS_RULING or scope expansion. No commit made. Next: lead final diff review and full replay.