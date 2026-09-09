```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented findings 2–6; all five named acceptance modules passed; no commit made.",
  "workspace": {
    "base_requested": "4d72e524",
    "base_mode": "exact",
    "head_start": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "head_end": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "upstream_end": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "tests/test_arm_readiness.py",
    "tests/test_launch_window.py"
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
      "cmd": "python3 -m unittest tests.test_arm_readiness.PackNightConsumerTests tests.test_launch_window",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_night_gate tests.test_arm_readiness tests.test_launch_window tests.test_arm_readiness_schemas tests.test_docs_freshness > /tmp/d176-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 225 tests in 448.401s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 225 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 /tmp/d176_verify_pins.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: 166 definition/constant pins; named symbols and eight repaired assertion rows verified"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS: 166 definition/constant pins"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Review finding 1 remains deliberately unchanged: the frozen census prevents the intended T0_REHEARSAL deployment.",
      "needs": "Lead-controlled cold-gate ruling before the first pack-bound night."
    }
  ]
}
```

## Change

- **2:** Pinned all eight requested assertion rows; added UUID4 and missing-record/digest/copied-field assertions.
- **3:** Repaired stale coordinates and verified 166 definition/constant pins, including moved tests.
- **4:** Recorded `4d72e524` as the integration commit editing the contract.
- **5:** Consumer imports the shared rehearsal prefix; regression changes that constant and checks both sites.
- **6:** Missing pack roots produce identical missing-code/details. Gate uses §6’s bare root-refusal details; regressions assert gate/consumer equality.

## Verification notes

The preliminary Python 3.14 run was interrupted during an expensive existing mint fixture. The complete acceptance run subsequently passed under the review’s Python 3.13 venv. No discovery or sharding was invoked.

## Residual risk

Finding 1 remains for the cold gate. Both root-predicate loops were verified unchanged apart from refusal text. Next step: lead final diff review and cold-gate adjudication before live authorization.