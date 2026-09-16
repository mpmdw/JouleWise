```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed admission-query timeout flake; tests-only cure passes three concurrent copies and the worktree; canonical suite encountered an environment blocker.",
  "workspace": {
    "base_requested": "efdaed879e1d13d06de719f10a4b7b504601cdb4",
    "base_mode": "exact",
    "head_start": "efdaed879e1d13d06de719f10a4b7b504601cdb4",
    "head_end": "efdaed879e1d13d06de719f10a4b7b504601cdb4",
    "upstream_end": "efdaed879e1d13d06de719f10a4b7b504601cdb4",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "tests/test_night_agent_install.py",
    "tests/test_install_night_agent.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "fixed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B reproduce.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/diagnose",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 3.121s", "", "FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_agent_install",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/fixed1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 50 tests in 760.021s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 50 tests.*\\sOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_agent_install",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/fixed2",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 50 tests in 759.899s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 50 tests.*\\sOK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_agent_install",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/fixed3",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 50 tests in 751.090s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 50 tests.*\\sOK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_agent_install",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 50 tests in 760.126s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 50 tests.*\\sOK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 51 tests in 46.932s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests.*\\sOK"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -B -m unittest discover -s tests",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/fixed3",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/fixed3",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 2 tests in 1.588s", "", "FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git --no-optional-locks diff --check",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "Canonical suite was interrupted after two process-census subtest failures. Focused replay confirms pgrep exits 3 with 'sysmond service not found' and 'Cannot get process list'; the adjacent test passes. Full-repository verification remains incomplete.",
      "needs": "Lead should run the canonical suite in an environment with working process census before landing."
    }
  ]
}
```

## Causal chain

The fixture’s **0.75-second adapter timeout** expires on ordinary admission queries under load. The engine classifies that query as `UNKNOWN` and refuses while still `VALIDATED`, before `prepared.admit()`.

Captured natural retention failure: fixture PID **24010** wrote clock **1789498800.0**; transaction PID **68594** observed an ordinary `print` timeout after **0.757047 seconds**, with empty directives and the clock unchanged. [Captured evidence](/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/r6d-mut/natural-admission-timeout.json).

Three instrumented stress runs produced **9, 9, and 5 failures**, including retention admission timeouts. Controlled one-second query delays reproduced the two reported configurations’ exact `'VERIFIED' != 'VALIDATED'` assertion.

## Remediation

Cure hunks in the two authorized files:

- Adapter deadline **0.75 → 5 seconds**, intentional hangs **3 → 30 seconds**, outer transaction deadline **15 → 60 seconds**.
- Fixture subprocess groups are killed, their parent waited, and group disappearance verified.
- Retention cells receive immediate per-cell cleanup and an initial-clock assertion.
- Added slow-admission and delayed-grandchild-clock regressions, with atomic PID readiness publication.

Both regressions detect their counterfactuals: restoring 0.75 seconds fails admission; parent-only cleanup leaves the grandchild alive and fails its assertion.

V2–V5 ran concurrently against identical final test bytes. **No production edits or repository commits. No NEEDS_RULING for production changes.**

## Disproved alternatives

- **H1:** Roots and clocks were already unique; the fake hang was already a single process. Captured admission failures retained the initial clock.
- **H2:** The bootstrap clock directive executes after admission.
- **H3:** The trace and engine ordering show admission refusal before publication or bootstrap.

## Residual risk

Canonical verification remains incomplete because of the process-census environment failure in F1. Next step: lead diff review and canonical replay in the appropriate environment.