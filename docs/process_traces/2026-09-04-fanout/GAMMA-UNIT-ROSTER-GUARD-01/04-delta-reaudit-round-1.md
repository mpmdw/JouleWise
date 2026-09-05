```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "disposition": "NOT CURED",
        "location": "joulewise/identity_pins.py:534-541,592-657; joulewise/arm_readiness.py:5623,5647-5650,5782-5786",
        "text": "The exact plan_id spoof is refused, but the external D-131 guard is still selected by mutable bytes inside the roster it polices. Renaming every A/... and B/... identity_unit_id to C/... and D/... makes gamma_namespace_present false, so both projection validation and the explicit arm-receipt roster check accept the malformed roster. This preserves the refuter's pack-is-its-own-oracle trust-boundary signature."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "disposition": "NEW",
        "location": "joulewise/identity_pins.py:573-584",
        "text": "The new generalized producer check enforces only same-within-arm and different-between-arms. Swapping the complete A and B producer-reference pairs is accepted, so A can reference the ruled 7B producer and B the ruled 1.5B producer, contrary to D-131 and the mission acceptance contract."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Fix round 1 blocks the literal plan_id exploit but preserves the same mutable-dispatch bypass and newly leaves A/B producer direction unenforced; NOT LANDABLE.",
  "workspace": {
    "base_requested": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "base_mode": "exact",
    "head_start": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "head_end": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "upstream_end": "ee940013abd1f1f3f78b44ba17ebf5346edb36d3",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gamma_unit_roster_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 0.473s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gamma_unit_roster_guard.GammaUnitRosterGuardTests.test_freeze_plan_id_spoof_cannot_disable_gamma_roster_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.104s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "audit_tmp=$(mktemp -d /private/tmp/jw-gamma-delta-reaudit.XXXXXX) && git archive HEAD | tar -x -C \"$audit_tmp\" && (cd \"$audit_tmp\" && perl -0pi -e 's/    if not gamma_namespace_present:\\n        return/    if True:  # counterfactual: disable the cure\\n        return/' joulewise/identity_pins.py && python3 -m unittest tests.test_gamma_unit_roster_guard.GammaUnitRosterGuardTests.test_freeze_plan_id_spoof_cannot_disable_gamma_roster_guard)",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.673s", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 -c 'import copy,json; from pathlib import Path; from joulewise import identity_pins as i; root=Path(\"configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3\"); tree=json.loads((root/\"plan_tree.json\").read_text()); p=tree[\"arm_attachments\"][\"identity_pin_projection\"]; r=json.loads((root/p[\"projection_receipt\"][\"path\"]).read_text()); q=copy.deepcopy(p); [(u.__setitem__(\"identity_unit_id\",u[\"identity_unit_id\"].replace(\"A/\",\"C/\").replace(\"B/\",\"D/\"))) for u in q[\"identity_units\"]]; i.validate_identity_pin_projection(q); qr=copy.deepcopy(r); [(u.__setitem__(\"identity_unit_id\",u[\"identity_unit_id\"].replace(\"A/\",\"C/\").replace(\"B/\",\"D/\"))) for u in qr[\"identity_units\"]]; i.validate_d131_gamma_identity_unit_roster(qr[\"identity_units\"],where=\"receipt.identity_units\"); s=copy.deepcopy(p); a=copy.deepcopy(s[\"identity_units\"][0][\"producer_plan_reference\"]); b=copy.deepcopy(s[\"identity_units\"][2][\"producer_plan_reference\"]); [(u.__setitem__(\"producer_plan_reference\",copy.deepcopy(b))) for u in s[\"identity_units\"][:2]]; [(u.__setitem__(\"producer_plan_reference\",copy.deepcopy(a))) for u in s[\"identity_units\"][2:]]; i.validate_identity_pin_projection(s); print(\"ACCEPTED: projection wholesale rename; arm receipt wholesale rename; A/B producer swap\"); raise SystemExit(1)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["ACCEPTED: projection wholesale rename; arm receipt wholesale rename; A/B producer swap"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "ordered D-131 gamma unit roster"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff-tree --no-commit-id --name-only -r HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py",
          "joulewise/arm_readiness.py",
          "joulewise/identity_pins.py",
          "tests/test_gamma_unit_roster_guard.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_gamma_unit_roster_guard\\.py$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The real MLX-backed freeze/arm path was not run because MLX is unavailable; the touched test module, production projection validator, and the exact production helper called on arm receipt units were exercised.",
      "needs": "Lead final verification may replay the malformed pack through the real MLX-backed path after the structural fix."
    }
  ]
}
```

## Findings

### F1 — blocker — NOT CURED

The named regression passes at HEAD: changing `plan.plan_id` and `window_identity.window_id` while dropping `B/prefill_p256` now refuses. Disabling the new namespace guard in an isolated copy makes that same test fail, so the regression bites.

The refuter's root finding nevertheless survives. `validate_d131_gamma_identity_unit_roster()` decides whether D-131 applies by inspecting the pack-controlled `identity_unit_id` values and returns at lines 540–541 if none use its A/B regex. The executed adversarial probe renamed the four IDs to `C/decode`, `C/prefill_p256`, `D/decode`, and `D/prefill_p256`; both `validate_identity_pin_projection()` and the arm receipt's explicit roster helper accepted. The selector moved from one mutable pack field to another, leaving the pack as its own applicability oracle.

Same-signature statement: **YES** — this is the same trust-boundary signature as refuter F1, not a new independent edge case. Another local dispatch-key patch should be escalated to a structural cure whose applicability comes from authority outside the roster under validation.

### F2 — blocker — NEW

The generalized check at lines 573–584 proves only that A's two references match, B's two references match, and A differs from B. It does not bind A to the smaller/1.5B producer and B to the larger/7B producer. The executed probe swapped both complete producer pairs; projection validation accepted. This contradicts D-131 clause 2 and the queue acceptance requiring the ruled producer references.

## Residual risk

MLX is unavailable in this environment, so the malformed pack was not driven through live model derivation. This does not weaken the two findings: both acceptance failures occur in the production validators before MLX, and the arm-side helper itself accepted the renamed receipt roster.
