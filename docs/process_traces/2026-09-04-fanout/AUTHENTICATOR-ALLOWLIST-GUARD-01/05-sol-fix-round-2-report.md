```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: round-1 re-audit explicitly repeats the opt-in-registration bypass, so the last-fix-round rule forbids another implementation attempt.",
  "workspace": {
    "base_requested": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "base_mode": "exact",
    "head_start": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "head_end": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "upstream_end": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/05-sol-fix-round-2-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/04-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\np = Path('docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/04-delta-reaudit-round-1.md')\ns = p.read_text()\nassert '\"same_signature\": \"YES:' in s\nassert 'NOT CURED: registration remains opt-in' in s\nassert 'undecorated future_authenticator executes' in s\nprint('same_signature=YES')\nprint('finding=NOT CURED: registration remains opt-in')\nprint('counterfactual=undecorated authenticator executes and allowlist accepts its path')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "same_signature=YES",
          "finding=NOT CURED: registration remains opt-in",
          "counterfactual=undecorated authenticator executes and allowlist accepts its path"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^same_signature=YES\\nfinding=NOT CURED: registration remains opt-in\\ncounterfactual=undecorated authenticator executes and allowlist accepts its path$"
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The repeated signature is registration remains opt-in: another authenticator can execute without entering R1_AUTHENTICATOR_REGISTRY, after which its differently named path passes allowlist validation.",
      "needs": "Define the authoritative authenticator boundary and approve the dispatcher-owned structural cure before implementation resumes."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Python cannot infer that an arbitrary newly added callable is semantically an authenticator; the contract must define authenticator status through an unavoidable invocation boundary or adopt a path-namespace invariant.",
      "needs": "Lead must choose the contract semantics described under Options considered."
    }
  ]
}
```

## Change

No production or test change was attempted. The re-audit declares `same_signature: YES` and reproduces the original bypass: registration remains optional, an undecorated authenticator executes, and its path is accepted (`04-delta-reaudit-round-1.md:24-33,148-154`). The prompt makes that condition a mandatory `NEEDS_RULING` stop.

| Finding | Cure | File:line |
|---|---|---|
| F1, repeated blocker: `_r1_authenticator` binds only implementations that opt into the decorator. | **Not attempted by order.** Replace the decorator-as-authority model with one dispatcher-owned authenticator table and make that dispatcher the only contract-recognized invocation boundary. | `joulewise/arm_readiness.py:577-621` |
| F1 counterfactual: an undecorated future authenticator can run while its allowlisted path is accepted. | After ruling, add the exact regression first: a new authenticator must be invokable only through the dispatcher with a mandatory registered `path_class`; direct implementation consumption must be rejected by the consumer-census assertion. | `tests/test_arm_readiness_schemas.py:576-602` |
| Current consumers do not establish a closed boundary. | Route the internal confirmation calls and public family-publication entry through the dispatcher; retain the public API only as a thin dispatcher facade if compatibility is required. | `joulewise/arm_readiness.py:4774-4776,11639-11645,11693-11699,11772-11774,12020-12027` |

Question: What makes a callable an authenticator for D-151 clause 7, such that a future direct callable is structurally impossible or inadmissible?

Options considered:

1. Adopt a registry-backed dispatcher as the sole authoritative authentication boundary, keep implementations private, and add a consumer-census regression that forbids direct implementation calls. This makes registration and `path_class` mandatory for every contract-recognized authenticator.
2. Reject the entire authenticator-capable path namespace except explicitly ruled grandfathered non-authenticator paths. This closes novel filenames but departs from the acceptance requirement to derive the forbidden set from authenticator roles/classes.
3. Retain decorator registration plus more tests. This repeats the rejected signature and is prohibited for round three.

Recommendation: adopt option 1. It turns “authenticator” from an inferred property of arbitrary Python callables into a closed, dispatcher-owned capability, while preserving registry-derived allowlist refusal. Before landing, audit the external scheduler consumer at `joulewise/scheduler_gates.py:866-873`; if its source or its focused tests require edits, expand scope prospectively.

Blocked work: production cure, the named undecorated-authenticator counterfactual, and focused module verification await the ruling (and any resulting scope expansion).

## Verification notes

No test module was run because this stopped before production/test edits and the only landed path is this report. This follows the instruction to run only modules the landing touches.

## Residual risk

Until the ruling and structural cure land, D-151 clause 7 remains unenforced for an authenticator consumed outside the optional decorator registry.
