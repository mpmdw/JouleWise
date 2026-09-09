```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Replaced authenticated-read timeout workers with pure path probes; requested tests and unchanged authentication sentinel pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "ec181aaa8a3ddea681d0f2ce3f5a7466feff1627",
    "head_end": "ec181aaa8a3ddea681d0f2ce3f5a7466feff1627",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [
    "joulewise/calibration_ledger.py",
    "joulewise/calibration_bracketing.py",
    "tests/test_calibration_ledger_custody.py",
    "tests/test_calibration_bracketing.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -m unittest tests.test_calibration_ledger tests.test_calibration_ledger_custody tests.test_calibration_bracketing tests.test_authentication_io > /private/tmp/icloud-custody-locator-part3-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 155 tests in 8.726s",
          "OK (skipped=2)",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "cmd": "git diff --exit-code -- joulewise/authentication_io.py tests/test_authentication_io.py",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Accepted post-probe mount race remains: authenticated reads are synchronous and unbounded. Timed-out probe workers cannot retain authentication locks.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Parts 1–2 shifted line-number-pinned writer I/O sites. Relocating three custody helpers restored the sentinel's original positions without editing authentication code or tests.",
      "needs": ""
    }
  ]
}
```

## Change

Removed worker execution of inspection/absence callbacks, copied authentication context, and the nested-worker context flag. Workers now perform only `Path.exists()` and `is_dir()`; authenticated reads run on the caller.

Probe sites cover artifact hashes, observation custody checks, directory validation, contained/governed reads, custody state, and calibration candidates. Timeout and probe exceptions preserve each entry point’s absent outcome. Empty backup overrides skip probing.

Counterfactual regressions verify blocked path probes return within budget without authentication, successful reads retain caller/session identity, and subsequent authentication proceeds while a timed-out worker remains blocked.

## Verification notes

The initial regression incorrectly nested authentication sessions; corrected before acceptance. The sentinel’s line-position drift was also resolved.

[Acceptance log](/private/tmp/icloud-custody-locator-part3-tests.log) includes `rc=0`. No real iCloud access, repository-wide suite, commits, or out-of-scope repository edits.

## Residual risk

A mount can stall between a successful probe and the unchanged authenticated read. The accepted roughly two-second post-probe race remains; read duration is unbounded. Lead review is the next step.