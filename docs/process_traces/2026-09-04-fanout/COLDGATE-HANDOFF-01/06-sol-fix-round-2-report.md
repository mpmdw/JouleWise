```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "N1 is cured by a transport-boundary canonical-byte assertion that rejects the named spaced-JSON counterfactual.",
  "workspace": {
    "base_requested": "633a94fb42d8b061e2646f1f7857e0028743d899",
    "base_mode": "exact",
    "head_start": "633a94fb42d8b061e2646f1f7857e0028743d899",
    "head_end": "633a94fb42d8b061e2646f1f7857e0028743d899",
    "upstream_end": "633a94fb42d8b061e2646f1f7857e0028743d899",
    "branch": "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/06-sol-fix-round-2-report.md",
    "tests/test_validate_gate_packet.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/05-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "633a94fb42d8b061e2646f1f7857e0028743d899",
          "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "633a94fb42d8b061e2646f1f7857e0028743d899[\\s\\S]*feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
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
          "Ran 35 tests in 2.668s",
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
      "cmd": "cf_dir=$(mktemp -d /private/tmp/coldgate-n1.XXXXXX) && mkdir -p \"$cf_dir/scripts\" \"$cf_dir/tests\" && cp scripts/validate_gate_packet.py \"$cf_dir/scripts/validate_gate_packet.py\" && cp tests/test_validate_gate_packet.py \"$cf_dir/tests/test_validate_gate_packet.py\" && touch \"$cf_dir/tests/__init__.py\" && perl -0pi -e 's/separators=\\(\",\", \":\"\\)/separators=(\", \", \": \")/' \"$cf_dir/scripts/validate_gate_packet.py\" && (cd \"$cf_dir\" && ! python3 -m unittest tests.test_validate_gate_packet.ValidateGatePacketTests.test_runner_binds_transported_bytes_digest_and_judge_identity)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AssertionError: b'{\"schema\": \"coldgate-judge-request/v1\", \"sources\": [2094 chars]}}\\n' != b'{\"schema\":\"coldgate-judge-request/v1\",\"sources\":{\"c[2031 chars]}}\\n'",
          "Ran 1 test in 0.002s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AssertionError:[\\s\\S]*Ran 1 test in [0-9.]+s[\\s\\S]*FAILED \\(failures=1\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No concrete real-judge launcher was selected or live-run; the existing operational fence remains in force.",
      "needs": "Keep the fence until charter-v3/Ed ratification and lead-owned concrete-launcher verification complete."
    }
  ]
}
```

## Change

N1 → added an independently constructed compact, sorted, UTF-8 JSON byte expectation at the transport boundary and compared the exact delivered request against it → `tests/test_validate_gate_packet.py:301`. This pins both compact separators and the terminal newline without calling `_canonical_json`.

## Verification notes

The unmutated touched module passed all 35 tests. In a temporary copy, changing production separators from `(",", ":")` to `(", ", ": ")` made the strengthened runner-binding test fail at the exact-byte assertion, so the named counterfactual is now discriminated.

## Residual risk

No concrete real-judge launcher was exercised. The existing operational fence remains pending charter-v3/Ed ratification and lead-owned concrete-launcher verification.
