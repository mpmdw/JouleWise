```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: replace the open-world authenticator registry with positive, independently authenticated allowlist provenance.",
  "workspace": {
    "base_requested": "38bbd1be210d42ae76b4dcd94d89982b2c5c1dff",
    "base_mode": "exact",
    "head_start": "38bbd1be210d42ae76b4dcd94d89982b2c5c1dff",
    "head_end": "38bbd1be210d42ae76b4dcd94d89982b2c5c1dff",
    "upstream_end": "38bbd1be210d42ae76b4dcd94d89982b2c5c1dff",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/06-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "landability": "NOT LANDABLE",
    "recommendation": "DIFFERENT MECHANISM",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "joulewise/arm_readiness.py:572-621,1728-1755,1812-1818,11639-11699; tests/test_arm_readiness_schemas.py:532-602",
        "text": "The landing tries to close an open semantic class with an opt-in registry; no authority boundary makes every present or future authenticator enter that registry."
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
          "38bbd1be210d42ae76b4dcd94d89982b2c5c1dff",
          "38bbd1be210d42ae76b4dcd94d89982b2c5c1dff",
          "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^38bbd1be210d42ae76b4dcd94d89982b2c5c1dff\\n38bbd1be210d42ae76b4dcd94d89982b2c5c1dff\\nfeat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check \"$(git merge-base origin/main HEAD)\"..HEAD",
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
      "cmd": "python3 -c 'import json,pathlib; s=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/06-consult-sol-structural.md\").read_text(encoding=\"utf-8\"); raw=s[8:s.index(chr(10)+chr(96)*3+chr(10),8)]; json.loads(raw); assert len(raw.encode(\"utf-8\")) <= 8192; print(\"report envelope: valid JSON, UTF-8, <=8192 bytes\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report envelope: valid JSON, UTF-8, <=8192 bytes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report envelope: valid JSON, UTF-8, <=8192 bytes$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Two same-signature rounds exhausted the decorator/registry design; a magistrate ruling is required before implementation resumes.",
      "needs": "Adopt the Q4 row and commission the D-151 V-1(vii) positive-provenance mechanism instead of another registry fix."
    }
  ]
}
```

## Findings

### F1 — blocker — Q1: structural cause

The repeated signature is a closure error, not a missing call site: `R1_AUTHENTICATOR_REGISTRY` is an initially empty mutable dictionary populated only when code elects to use `_r1_authenticator` (`joulewise/arm_readiness.py:572-621`), while the allowlist check can see only those elected records (`joulewise/arm_readiness.py:1728-1755,1812-1818`). The two current functions opt in (`joulewise/arm_readiness.py:11639-11699`), and the novel-name regression also opts in before asserting refusal (`tests/test_arm_readiness_schemas.py:576-602`), so the test assumes the universal registration edge it claims to prove; the implementation/declaration coupling test likewise quantifies only over already-registered entries (`tests/test_arm_readiness_schemas.py:532-574`). Python has no structural fact from which to infer that an arbitrary new callable is semantically an authenticator, and no dispatcher owns all authentication, so moving names into records and then wrapping those records cannot close the open world.

### Q2: threat model

This is a real EVIDENCE and PRE-REGISTRATION fence, not an operator-adversary guard to remove: the allowlist decides which post-derivation repository changes are subtracted, and admitting an authenticator can let subject and alleged authenticator move together (`docs/contracts/d117_step6_confirmation_table.md:76-93`). D-161 keeps fail-closed behavior for evidence and pre-registration (`docs/decision_log.md:207,10394-10398`); the trusted-operator exclusion means machinery need not resist a deliberate co-edit, but it does not license an accidental allowlist classification that destroys independence. What should be removed is this semantic-discovery mechanism, not D-151 clause 7.

### Q3: class-ending cure

Use a different mechanism: make allowlist membership positive and proof-carrying, derived at the pre-registration boundary from the closed set of governed artifact outputs and their independent authentication/replay records, and authenticate that derived manifest outside the subtraction set. Validation then compares the literal allowlist to that derived, digest-bound set and refuses every unexplained extra path by default; it never asks whether a filename or callable “looks like” an authenticator. This is D-151's already-recorded V-1(vii) route (`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md:92-96,114-115`), and it ends the opt-in class because omission from a deny-registry no longer grants admission. The one proving test adds `configs/arm_readiness/future-confirmation-token.json` only to the candidate allowlist—without naming or registering any authenticator—and must observe refusal for an extra path absent from the independently authenticated derived manifest; disabling the exact-set comparison must make that test fail.

### Q4: magistrate ruling row, verbatim

“AUTHENTICATOR-ALLOWLIST-GUARD-01 is NOT LANDABLE: two rounds establish that an opt-in authenticator registry cannot close an open semantic class. The row is re-scoped to D-151's V-1(vii) mechanism: allowlist membership is derived positively from independently authenticated governed-artifact provenance, and any unexplained extra path refuses without classifying it by name or callable. Remove the decorator/registry landing; D-151 clause 7 remains a fail-closed evidence and pre-registration fence under D-161. Acceptance is one novel-name extra-entry regression that refuses without registering or naming the future authenticator, plus its exact-set-comparison mutation kill.”

## Residual risk

No executable claim required a test run: the conclusion follows from the complete mission trace, the production reference census, and the landing diff. The positive-provenance design still requires a fresh bounded specification of the manifest's authority root and transaction timing before implementation; this consult does not authorize those out-of-scope changes.
