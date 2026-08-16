```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the adopted F3 and NDF1 designs; nine focused suites pass, but one out-of-scope lifecycle test requires migration after the mandated public-symbol deletion.",
  "workspace": {
    "base_requested": "impl/wo-launch-binding",
    "base_mode": "exact",
    "head_start": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "head_end": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "upstream_end": "0f886d38cc1d87f5168e0775942d239bc0036c33",
    "branch": "impl/wo-launch-binding"
  },
  "pathspec": [
    "docs/decision_log.md",
    "joulewise/arm_readiness.py",
    "scripts/launch_window.py",
    "scripts/run_campaign.py",
    "tests/test_arm_readiness.py",
    "tests/test_launch_window.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [
    ".consult-f3-report.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 20 tests in 0.160s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 20 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 14 tests in 0.032s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 14 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_bundle",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 74 tests in 6.412s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 74 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_launch_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 31 tests in 0.239s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_analysis_engine",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 12 tests in 0.053s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_analysis_integration",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 92 tests in 32.462s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 92 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_extraction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 124 tests in 1.770s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 124 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 15 tests in 0.025s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 15 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 242 tests in 143.885s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 242 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V10",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "ImportError: cannot import name 'consume_launch_capability' from 'joulewise.arm_readiness'",
          "Ran 1 test in 0.000s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests .*\\n\\nOK"
      }
    },
    {
      "id": "V11",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport inspect\nimport joulewise.arm_readiness as readiness\nassert not hasattr(readiness, 'consume_launch_capability')\nassert '_consume_launch_capability' not in readiness.__all__\nsignature = inspect.signature(readiness._consume_launch_capability)\nassert all(parameter.default is inspect.Parameter.empty for parameter in signature.parameters.values())\nassert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in signature.parameters.values())\nprint('PUBLIC_NAME_ABSENT=1 PRIVATE_EXPORT_ABSENT=1 REQUIRED_KEYWORD_CONTEXT=1')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PUBLIC_NAME_ABSENT=1 PRIVATE_EXPORT_ABSENT=1 REQUIRED_KEYWORD_CONTEXT=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PUBLIC_NAME_ABSENT=1 PRIVATE_EXPORT_ABSENT=1 REQUIRED_KEYWORD_CONTEXT=1"
      }
    },
    {
      "id": "V12",
      "kind": "build",
      "cmd": "python3 -m py_compile joulewise/arm_readiness.py scripts/launch_window.py scripts/run_campaign.py tests/test_arm_readiness.py tests/test_launch_window.py tests/test_run_campaign.py",
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
      "id": "V13",
      "kind": "lint",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "tests/test_arm_readiness_lifecycle.py imports and invokes the public consume_launch_capability symbol that the adopted design requires to be absent, so that module no longer collects.",
      "needs": "Expand WRITE_SCOPE to tests/test_arm_readiness_lifecycle.py so its obsolete direct-wrapper checks can be migrated without restoring the forbidden symbol."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The pre-edit canonical discovery run was manually interrupted in the unrelated calibration crash matrix after an unusually long execution; post-edit canonical discovery is independently blocked by F1.",
      "needs": "After granting F1 scope and migrating the stale test, rerun python3 -m unittest discover -s tests."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A hostile same-interpreter or same-UID actor can deliberately invoke the private consumer with forged-but-complete valid context; the enforced property is atomic single use, not caller identity.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_arm_readiness_lifecycle.py"
    ],
    "reason": "The mandatory removal of consume_launch_capability makes this legacy module's import and four direct-call expectations invalid.",
    "blocked_work": "Restore canonical test discovery and migrate lifecycle regressions to the supported launcher/private complete-context contract.",
    "minimal_change": "Remove the deleted import and direct-wrapper signature assertions; retain lifecycle coverage through scripts/launch_window.py and the complete-context single-use path."
  }
}
```

## Change

Implemented the adopted F3 API boundary and NDF1 AXI release gate. The consumer now requires complete keyword-only context, independently reauthenticates it before publication, and documents the no-clobber primary as the sole enforcement. Marker-bearing AXI dispatch now refuses with the registered `launch_lineage_axi_unsupported` code before any child or runs-directory side effect. Everything remains uncommitted.

## Verification notes

All nine requested focused suites passed. `NEEDS_SCOPE`: the canonical suite cannot collect until `tests/test_arm_readiness_lifecycle.py` is authorized and migrated; it was not modified.

## Residual risk

The private API prevents accidental incomplete invocation but cannot authenticate hostile same-interpreter/same-UID callers. The decision log records this limitation and the exact Phase-2 AXI release mechanism.