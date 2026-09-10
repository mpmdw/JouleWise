```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added the three proposed deterministic clock-refusal tests unchanged; module acceptance and all three detail-string mutation checks passed.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "informational",
    "head_start": "4203ff599b0e7dfafda73ea7d10fb86ee2efbe71",
    "head_end": "4203ff599b0e7dfafda73ea7d10fb86ee2efbe71",
    "upstream_end": "afaeffefb38c050ff2e4a23fd32878180a723f23",
    "branch": "fix/2026-09-09-t0-clock-refusal-tests"
  },
  "pathspec": ["tests/test_arm_readiness_evidence_t0.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest tests.test_arm_readiness_evidence_t0 > /private/tmp/t0-clock-refusal-suite.log 2>&1\nrc=$?\nprintf '\\nRC=%s\\n' \"$rc\" >> /private/tmp/t0-clock-refusal-suite.log\ntail -n 8 /private/tmp/t0-clock-refusal-suite.log\nexit \"$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 71 tests in 467.510s",
          "OK (skipped=1)",
          "RC=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)[\\s\\S]*RC=0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 - <<'PY'\nimport inspect\nimport textwrap\nimport unittest\nfrom tests.test_arm_readiness_evidence_t0 import ArmReadinessEvidenceT0Tests as C\ncases = (\n    ('test_insufficient_positive_capture_history_refuses', 'clock-reference command capture fields are invalid or stale'),\n    ('test_r0_raw_anchor_ahead_of_author_raw_refuses', 'T-0 RAW anchor span is below 600000000000 ns'),\n    ('test_capture_finish_ahead_of_ordinary_now_refuses', 'clock-reference command capture is not a live T-0 artifact'),\n)\nfor name, detail in cases:\n    method = getattr(C, name)\n    namespace = dict(method.__globals__)\n    source = textwrap.dedent(inspect.getsource(method))\n    assert source.count(detail) == 1\n    exec(source.replace(detail, 'MUTATED REFUSAL DETAIL'), namespace)\n    Mutant = type('Mutant', (C,), {name: namespace[name]})\n    result = unittest.TestResult()\n    Mutant(name).run(result)\n    assert result.testsRun == 1 and len(result.failures) == 1 and not result.errors and not result.skipped, (result.errors, result.failures)\n    assert 'MUTATED REFUSAL DETAIL' in result.failures[0][1]\n    print(f'{name}: detail=\"MUTATED REFUSAL DETAIL\" -> FAIL (1 assertion failure, 0 errors); mutation check PASS')\nprint('RC=0')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "test_insufficient_positive_capture_history_refuses: detail=\"MUTATED REFUSAL DETAIL\" -> FAIL (1 assertion failure, 0 errors); mutation check PASS",
          "test_r0_raw_anchor_ahead_of_author_raw_refuses: detail=\"MUTATED REFUSAL DETAIL\" -> FAIL (1 assertion failure, 0 errors); mutation check PASS",
          "test_capture_finish_ahead_of_ordinary_now_refuses: detail=\"MUTATED REFUSAL DETAIL\" -> FAIL (1 assertion failure, 0 errors); mutation check PASS",
          "RC=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "mutation check PASS\\nRC=0"
      }
    },
    {
      "id": "V3",
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
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during verification; local HEAD remained unchanged and the branch is now behind by one commit.",
      "needs": "Lead accounts for the newer upstream during final integration."
    }
  ]
}
```

## Change

Added 37 lines, exactly matching the proposal; no helper adaptations or commits.

| Test | Production guard pinned |
|---|---|
| `test_insufficient_positive_capture_history_refuses` | `joulewise/arm_readiness_evidence_t0.py:552`: `value["started_monotonic_ns"] < 1`. At ordinary now 500 seconds, fixture start is −100,000,000,990 ns; exact refusal at line 556. |
| `test_r0_raw_anchor_ahead_of_author_raw_refuses` | `joulewise/arm_readiness_evidence_t0.py:1162`: `span < _MIN_IDLE_NS`. R0 at author RAW +1 produces span −1 ns; exact refusal at line 1163. |
| `test_capture_finish_ahead_of_ordinary_now_refuses` | `joulewise/arm_readiness_evidence_t0.py:559`: `value["finished_monotonic_ns"] > now`. Finish at ordinary now +1 triggers the exact refusal at line 562. |

Existing helper signatures, quoted:

```python
def _assert_clock_refusal(
    self, *, detail: str, mutate=None, probe=passing_probe,
    now_monotonic_ns: int = SYNTHETIC_MONOTONIC_NS,
    sample_anchor=None, kind: str = "CLOCK_ATTESTATION",
    reason_code: str = "evidence_author_t0_clock_attestation_underivable",
) -> None:

@staticmethod
def _replace_r0(
    inputs: Path, *, legs: Mapping[str, tuple[int, str]] | None = None,
    anchor_raw: int | None = None,
    anchor_realtime: int | None = None,
    anchor_skew: int = 1_000,
) -> None:
```

The biting assertion is `self.assertEqual(str(caught.exception), detail)` at test-module line 1194.

One-line mutation evidence:

```text
test_insufficient_positive_capture_history_refuses: detail="MUTATED REFUSAL DETAIL" -> FAIL (1 assertion failure, 0 errors); mutation check PASS
```

## Verification notes

Acceptance log: [t0-clock-refusal-suite.log](/private/tmp/t0-clock-refusal-suite.log). Verification used the requested module suite for this test-only change; repository-wide discovery was not run.

Next step: lead reviews and integrates the diff against the advanced upstream.