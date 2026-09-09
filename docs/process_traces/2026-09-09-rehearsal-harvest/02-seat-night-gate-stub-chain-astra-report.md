```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented F1–F3; both defect regressions fail against baseline and all 135 scoped tests pass.",
  "workspace": {
    "base_requested": "83ab38ed",
    "base_mode": "informational",
    "head_start": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "head_end": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "upstream_end": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "branch": "fix/2026-09-09-night-gate-stub-chain"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "scripts/run_night.py",
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
      "cmd": "python3 -m unittest tests.test_night_gate tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 135 tests in 5.899s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 135 tests in .*s\\s+OK"
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
    }
  ],
  "flags": []
}
```

## Change

- **F1:** Stub receipts skip both chain reads and record `chain_sha256: null`, `expected_chain_sha256: null`, and `chain_stub: "built_in_stub_by_design"` in C5’s measured fields. Class table and basis rules remain unchanged. Real-class checks are byte-identical apart from indentation.
- **F2:** Added missing-file regressions proving valid `REHEARSAL_ONLY` receipts without either read, and diagnostic refusal when either file is missing.
- **F3:** Refused gate logs include reason and detail, normalized to one line and capped at 200 detail characters. Existing driver seams verify this and unchanged GO/rehearsal log forms.

## Verification notes

Before the gate cure, the new regression failed against `83ab38ed`:

```text
AssertionError: 'REHEARSAL_ONLY' != 'REFUSED'
Refusal reason: night_probe_error
Detail: FileNotFoundError: [Errno 2] No such file or directory: '/custody/chain.zsh'
Ran 1 test in 0.001s
FAILED (failures=1)
rc=1
```

The logging regression also failed with the baseline driver loaded in memory: actual output was only `night gate verdict=REFUSED`.

```text
Ran 1 test in 0.030s
FAILED (failures=1)
rc=1
```

An initial added test incorrectly expected driver rc 0 for rehearsal; corrected to existing `EXIT_REFUSED` behavior without changing production exit codes.

Final scoped log: `/tmp/night-gate-stub-scoped-tests.log`.

```text
Ran 135 tests in 5.899s

OK
rc=0
```

No commits or out-of-scope repository edits. Lead diff review is the next step; no live hardware validation was performed.