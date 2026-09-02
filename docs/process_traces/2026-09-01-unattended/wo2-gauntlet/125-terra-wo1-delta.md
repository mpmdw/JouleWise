```json
{
  "schema": "claude-codex-report/v1",
  "adapter": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Exact commit 0ecaf55a matches all 18 ruled cures; focused suite passes and all four requested final-module mutants are killed.",
  "workspace": {
    "base_requested": "0ecaf55a",
    "base_mode": "exact",
    "head_start": "88c222324bcb0686c0e2b2bd45f536bba49d9a79",
    "head_end": "88c222324bcb0686c0e2b2bd45f536bba49d9a79",
    "upstream_end": "88c222324bcb0686c0e2b2bd45f536bba49d9a79",
    "branch": "feat/2026-09-01-night-gate"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGE-READY",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngdelta_audit python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 40 tests in 0.004s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 40 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngdelta_audit python3 -m unittest -v tests.test_night_gate",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngdelta_audit",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 40 tests in 0.007s", "FAILED (failures=17, errors=3)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=17, errors=3\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_night_gate",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngmut_a",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 40 tests in 0.005s", "FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_night_gate",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngmut_b",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 40 tests in 0.005s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_night_gate",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngmut_c",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 40 tests in 0.004s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_night_gate",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/ngmut_d",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 40 tests in 0.005s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The live load command was denied by the restricted environment, so its real output could not be replayed.",
      "needs": "Optional unrestricted bench rerun of sysctl -n vm.loadavg."
    }
  ]
}
```

Verdict: **MERGE-READY**.

| Item | Cure matches? | Pre-fix new-test result | Note |
|---|---|---|---|
| B2 | Yes | FAIL, 2 methods / 5 subcases | GNU form accepted; malformed forms name the correct check. |
| B3 | Yes | FAIL | Parent raises `AssertionError`; fixed code returns malformed refusal. |
| F1 | Yes | ERROR | Parent reaches a refusal with null payload for malformed load output. |
| F2 | Yes | ERROR | Parent treats malformed thermal prefix as absent. |
| S1 | Yes | ERROR + FAIL | Class refusal and bidirectional receipt invariant are both red on parent. |
| S2 | Yes | PASS, expected | Literal pin tests an unchanged production constant. |
| S3 | Yes | PASS, expected | Literal pin tests an unchanged digest constant. |
| S4 | Yes | FAIL | Parent registry lacks the new class refusal code. |
| S5 | Yes | N/A, inspection | Parent still defines `RESULT_SCHEMA`; fixed module does not. |
| S6 | Yes | FAIL | Parent rejects list-form probe argv. |
| S7 | Yes | FAIL | Parent detail is not exactly `ac_power`. |
| N1 | Yes | N/A, inspection | Parent has the three aliases; fixed module removes them. |
| N2 | Yes | N/A, inspection | Parent has dead `refusal_valid`; fixed module removes it. |
| N3 | Yes | FAIL | Future-authored plan reaches GO on parent. |
| N4 | Yes | PASS, expected | Fixture-only coverage expansion; serialization already behaved correctly. |
| N5 | Yes | FAIL | Parent turns monotonic failure into window expiry via zero. |
| N6 | Yes | FAIL | Parent rejects valid reordered rows. |
| F3 | Yes | FAIL | Parent retains all 586 census lines. |

## Findings

None.

## Unmapped hunks

- `tests/test_night_gate.py`: only the behavior-neutral reorder of `hashlib` and `inspect` imports. Every other code or test hunk maps to a ruled item.

## B2 twin check

For valid chain-file paths, the gate and driver have the same acceptance set:

| Sidecar input | Gate | Driver |
|---|---|---|
| Uppercase digest | reject | reject |
| Tab separator | accept | accept |
| CRLF line ending | accept | accept |
| Trailing spaces | accept | accept |
| BOM before digest | reject | reject |
| GNU form with basename containing spaces | reject (three tokens) | reject (three tokens) |

Both accept bare lowercase hex even when the basename contains spaces. A malformed chain path ending in `/` would produce different basename comparisons, but the driver rejects it earlier as not a file.

## S1

A `TRANSACTION_PACK` plan with an agent present returns `night_refused_agent_present`, not the class refusal: census precedes chain validation and the class check. That matches R-3’s census-first safety rule; R-4/R-10 make the transaction class unavailable only after those preconditions. The suite tests the `ORDER` entries individually, but has no direct combined transaction-plus-agent test.

## Mutants

All killed:

- Bare-hex-only parser: 2 failures.
- Boundary changed to reject `LOAD_MAX`: 1 failure.
- Removed `REFUSED ⇒ refusal` invariant: 1 failure.
- Removed census 20-line cap: 1 failure.

## Commands

- Focused final suite: 40 passed.
- New suite against `0ecaf55a^` through the isolated import shim: 17 failures, 3 errors.
- Purity grep found no matches.
- `pmset -g therm` exited 0 with no `CPU_Speed_Limit` line, which the parser accepts. `sysctl -n vm.loadavg` was blocked with “Operation not permitted”; the parser’s `\d+` groups syntactically accept two-digit loads such as `{ 12.34 … }` before applying the load threshold.

## Residual risk

Live load-output replay remains an environment-only gap; no repository files were modified.