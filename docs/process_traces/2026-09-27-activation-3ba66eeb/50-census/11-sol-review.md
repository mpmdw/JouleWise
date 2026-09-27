```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Test-only change preserves the decoy and pgrep-error checks, but skipping an unavailable unrelated hit weakens the recorded-service assertion.",
  "workspace": {
    "base_requested": "97082508",
    "base_mode": "exact",
    "head_start": "0c0af6422b399c947e77fb65d47210c754fb50d1",
    "head_end": "0c0af6422b399c947e77fb65d47210c754fb50d1",
    "upstream_end": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "tests/test_arm_readiness_evidence_t0.py",
        "line": 2792,
        "text": "If a reported non-decoy process exits before ps reads it, continue skips both text assertions. A hit containing a recorded Apple-service basename would have failed the old assertion against pgrep's captured output but can now pass."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --name-status 97082508 0c0af642",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["M\ttests/test_arm_readiness_evidence_t0.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "M\\s+tests/test_arm_readiness_evidence_t0.py"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 1.197s", "OK (skipped=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/usr/bin/pgrep -f '[r]un_campaign'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": ["sysmon request failed with error: sysmond service not found", "pgrep: Cannot get process list"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^[0-9]+$"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/bin/ps -ww -o command= -p 1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 127,
        "tail": ["zsh:1: operation not permitted: /bin/ps"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".+"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 97082508 0c0af642",
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
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The focused test skipped both cases because sandboxed pgrep cannot obtain the process list; ps is also denied. No live pgrep-to-ps behavior was validated.",
      "needs": "Replay the focused test in a process-table-capable Mac session."
    }
  ]
}
```

## Findings

**F1 — SHOULD-FIX.** The `continue` at [line 2792](/Users/edr/code/JouleWise-wt-census-rev-3ba66eeb/tests/test_arm_readiness_evidence_t0.py:2792) can hide a recorded-service basename in an unrelated hit that exits between `pgrep` and `ps`. The negative decoys cannot take that branch, so their checks remain fail-closed. Positive decoy membership, narrowed alternatives, Python-only regex constructs that miss a positive decoy, and `pgrep` errors also retain their failure paths. The per-hit basename assertion is nonetheless weaker than the old check of captured `pgrep -lf` output.

Only the test changed. The production `-lf` commands in `arm_readiness_evidence_t0.py` and `night_gate.py` remain untouched.

## Residual risk

`ps -ww -o command=` does **not** print byte-identical match text: Apple’s `ps` source escapes newlines and tabs, while `pgrep -f` matches its joined argument list. The current patterns’ literal matches do not appear sensitive to that escaping, and `-ww` removes display-width truncation. A process becoming a zombie or a PID being reused before the `ps` read can still turn an otherwise valid hit into a spurious test failure. These behaviors need a live Mac replay; the sandbox result was a skip, not a passing live census. [Apple `pgrep` source](https://github.com/apple-oss-distributions/adv_cmds/blob/main/pkill/pkill.c), [Apple `ps` source](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c).

REVIEW: FAIL