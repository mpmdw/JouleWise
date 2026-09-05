```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Retire N1's exact JSON-spelling gate while retaining the immutable-source, emitted-byte digest, and judge-identity evidence fence.",
  "workspace": {
    "base_requested": "c6bba192e3872e48740caa6804b6386370e56bda",
    "base_mode": "exact",
    "head_start": "c6bba192e3872e48740caa6804b6386370e56bda",
    "head_end": "c6bba192e3872e48740caa6804b6386370e56bda",
    "upstream_end": "c6bba192e3872e48740caa6804b6386370e56bda",
    "branch": "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/08-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "N1",
        "severity": "should_fix",
        "location": "tests/test_validate_gate_packet.py:301",
        "text": "The exact canonical-request byte assertion mistakes a serializer spelling convention for an evidence invariant, creating an open-ended sequence of fixture-dependent counterexamples.",
        "recommendation": "Retire the byte-spelling gate, retain deterministic JSON as a maintainability convention, and test that evidence bindings are invariant across semantically equivalent serializations."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git rev-parse @{upstream} && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "c6bba192e3872e48740caa6804b6386370e56bda",
          "c6bba192e3872e48740caa6804b6386370e56bda",
          "feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c6bba192e3872e48740caa6804b6386370e56bda[\\s\\S]*feat/2026-09-04-fan-COLDGATE-HANDOFF-01"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "test -z \"$(git diff --no-index --check /dev/null docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/08-consult-sol-structural.md 2>&1)\"",
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
      "cmd": "python3 -c 'import json,pathlib; s=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/COLDGATE-HANDOFF-01/08-consult-sol-structural.md\").read_text(); a=len(\"```json\\n\"); b=s.index(\"\\n```\",a); raw=s[a:b]; o=json.loads(raw); assert len(raw.encode()) <= 8192 and o[\"schema\"] == \"claude-codex-report/v1\" and o[\"genre\"] == \"review\"; print(\"envelope valid\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "envelope valid"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^envelope valid$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No concrete real-judge launcher has been ratified or live-verified.",
      "needs": "Keep only that operational fence until Ed ratification and lead-owned concrete-launcher verification complete."
    }
  ]
}
```

## Findings

Q1 — N1 (should_fix). The repeated signature is a quantifier and abstraction error: the ruling's evidence claim was converted into a requirement for one exact JSON spelling, while the regression exercises only one concrete, ASCII-only request. Production centralizes four incidental spelling choices in `_canonical_json` (`scripts/validate_gate_packet.py:600`), but the test parses those bytes and recreates them with another `json.dumps` call (`tests/test_validate_gate_packet.py:300`, `tests/test_validate_gate_packet.py:301`); it can therefore discriminate only serializer dimensions activated by its fixture. Round 1 exposed spacing (`05-delta-reaudit-round-1.md:156`), and round 2 exposed Unicode escaping at the same assertion (`07-delta-reaudit-round-2.md:169`, `07-delta-reaudit-round-2.md:171`). Adding one fixture per newly discovered spelling choice never closes that open set.

Q2 — THREAT MODEL. The immutable-snapshot source, exact emitted-byte digest acknowledgement, and judge identity are real evidence fences: `_judge_request` uses only snapshot bytes (`scripts/validate_gate_packet.py:615`), `run_gate_handoff` hashes the actual emitted bytes and compares the transport observation (`scripts/validate_gate_packet.py:722`, `scripts/validate_gate_packet.py:738`), and the regression verifies decoded source hashes (`tests/test_validate_gate_packet.py:333`). Compact versus spaced JSON and raw UTF-8 versus `\\u` escapes preserve the same JSON values, base64-decoded evidence, and acknowledged emitted-byte digest; no pre-committed request digest or physics quantity depends on either spelling. Under D-161, exact spelling is therefore an operator-only/maintainability concern and must be downgraded, not enforced fail-closed; this does not weaken the genuine delivery fence.

Q3 — CURE. Re-scope “canonical JSON” to a deterministic implementation convention for reproducibility and diffability, RETIRE N1 as an acceptance finding, and define the safety contract over semantic request fields plus the digest of whatever exact bytes were actually emitted. The one proving regression is `test_handoff_binding_is_invariant_to_semantically_equivalent_json_encodings`: with a valid non-ASCII source name, inject compact/raw-UTF-8, spaced, and ASCII-escaped encoders as subcases and require each to make exactly one transport call, PASS only when the returned digest equals SHA-256 of the captured bytes, bind exactly one judge identity, and decode packet/charter/exhibits to the immutable snapshot and validator-receipt hashes. That test fails on a source reread, byte corruption, false acknowledgement, identity loss, or second delivery, but deliberately stays green for harmless JSON spelling changes.

Q4 — VERBATIM RULING ROW. `| COLDGATE-HANDOFF-01 | Option A's evidence fence is adopted: construct the request solely from the immutable validated snapshot, deliver once, and bind the exact emitted-byte digest plus one judge request/session identity. “Canonical JSON” is downgraded to a deterministic maintainability convention; whitespace and Unicode-escape spelling are not safety conditions, and N1 is RETIRED. Replace N1 with one metamorphic serialization-independence test that proves source-byte equality, emitted-byte digest acknowledgement, identity binding, and exactly one transport call across semantically equivalent JSON encodings. Keep the operational fence only until Ed ratifies the registry amendment and the concrete launcher passes lead-owned live verification. |`

## Residual risk

This consult does not establish interoperability with a real launcher: the fake and subprocess adapters prove the mechanism, but launcher selection, Ed's registry ratification, and lead-owned live verification remain outside this review and are the only reasons to retain the operational fence.
