```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Retired N1's JSON-spelling gate and replaced it with the adopted serialization-invariance evidence-binding regression.",
  "workspace": {
    "base_requested": "27c257509decd798cb28f5de30890ff949be1858",
    "base_mode": "exact",
    "head_start": "27c257509decd798cb28f5de30890ff949be1858",
    "head_end": "27c257509decd798cb28f5de30890ff949be1858",
    "upstream_end": "27c257509decd798cb28f5de30890ff949be1858",
    "branch": "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/09-sol-rescope-report.md",
    "scripts/validate_gate_packet.py",
    "tests/test_validate_gate_packet.py"
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
      "cmd": "python3 -m unittest tests.test_validate_gate_packet.ValidateGatePacketTests.test_handoff_binding_is_invariant_to_semantically_equivalent_json_encodings",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.003s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_validate_gate_packet",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 35 tests in 2.750s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 35 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "coldgate_cf_dir=$(mktemp -d /private/tmp/coldgate-rescope.XXXXXX); mkdir -p \"$coldgate_cf_dir/scripts\" \"$coldgate_cf_dir/tests\"; cp scripts/validate_gate_packet.py \"$coldgate_cf_dir/scripts/validate_gate_packet.py\"; cp tests/test_validate_gate_packet.py \"$coldgate_cf_dir/tests/test_validate_gate_packet.py\"; touch \"$coldgate_cf_dir/tests/__init__.py\"; perl -0pi -e 's/acknowledgement = transport\\(request_bytes\\)/acknowledgement = transport(request_bytes + b\" \")/' \"$coldgate_cf_dir/scripts/validate_gate_packet.py\"; (cd \"$coldgate_cf_dir\" && ! python3 -m unittest tests.test_validate_gate_packet.ValidateGatePacketTests.test_handoff_binding_is_invariant_to_semantically_equivalent_json_encodings)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "- REFUSE",
          "+ PASS",
          "Ran 1 test in 0.004s",
          "FAILED (failures=3)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AssertionError: 'REFUSE' != 'PASS'[\\s\\S]*Ran 1 test in [0-9.]+s[\\s\\S]*FAILED \\(failures=3\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && git rev-parse HEAD && git rev-parse @{upstream} && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M scripts/validate_gate_packet.py",
          " M tests/test_validate_gate_packet.py",
          "?? docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/09-sol-rescope-report.md",
          "27c257509decd798cb28f5de30890ff949be1858",
          "27c257509decd798cb28f5de30890ff949be1858",
          "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scripts/validate_gate_packet.py[\\s\\S]*tests/test_validate_gate_packet.py[\\s\\S]*09-sol-rescope-report.md[\\s\\S]*27c257509decd798cb28f5de30890ff949be1858[\\s\\S]*27c257509decd798cb28f5de30890ff949be1858[\\s\\S]*feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No concrete real-judge launcher was selected or live-verified; the adopted operational fence remains in force.",
      "needs": "Keep the fence until Ed ratifies the registry amendment and lead-owned concrete-launcher verification passes."
    }
  ]
}
```

## Change

| Adopted ruling clause | File:line |
|---|---|
| Deterministic JSON is only a reproducibility/diffability convention; equivalent whitespace and Unicode escaping are not safety conditions. | `scripts/validate_gate_packet.py:44`; `scripts/validate_gate_packet.py:601`; `tests/test_validate_gate_packet.py:283`; `tests/test_validate_gate_packet.py:285`; `tests/test_validate_gate_packet.py:400` |
| Construct request sources solely from the immutable validated snapshot. | `scripts/validate_gate_packet.py:617`; `tests/test_validate_gate_packet.py:358` |
| Deliver exactly once. | `scripts/validate_gate_packet.py:724`; `tests/test_validate_gate_packet.py:310`; `tests/test_validate_gate_packet.py:333` |
| Bind the digest of the exact emitted bytes. | `scripts/validate_gate_packet.py:724`; `scripts/validate_gate_packet.py:740`; `tests/test_validate_gate_packet.py:334`; `tests/test_validate_gate_packet.py:350` |
| Bind exactly one judge request/session identity. | `scripts/validate_gate_packet.py:757`; `tests/test_validate_gate_packet.py:313`; `tests/test_validate_gate_packet.py:345` |
| Retire N1 and replace its exact-spelling assertion with the one named metamorphic acceptance test. | `tests/test_validate_gate_packet.py:279` |
| Keep the operational fence pending Ed ratification and lead-owned live verification. | `scripts/validate_gate_packet.py:49` |

The former reconstructed canonical-byte and terminal-newline assertions were removed; no retired spelling-enforcement mechanism remains.

## Verification notes

The acceptance test was also run against a disposable exact-byte corruption counterfactual. All three encoding subcases failed because the acknowledged digest no longer matched the bytes the runner hashed, establishing that the replacement test is red on an evidence-binding break while remaining green for harmless serialization changes.

## Residual risk

The real launcher remains intentionally unselected and unverified, so the ruling's operational fence still applies.
