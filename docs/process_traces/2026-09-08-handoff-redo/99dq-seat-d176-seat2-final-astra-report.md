```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Seat-2 census, locator and GO producer rulings installed; focused acceptance passes; consumption-point proof awaits seat-3 integration.",
  "workspace": {
    "base_requested": "8eae74926595507380b20b89880d8e6e462f9516",
    "base_mode": "exact",
    "head_start": "8eae74926595507380b20b89880d8e6e462f9516",
    "head_end": "8eae74926595507380b20b89880d8e6e462f9516",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat2-producer"
  },
  "pathspec": [
    "configs/production_custody_inventory.json",
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "joulewise/t0_rehearsal.py",
    "scripts/rehearse_t0_unattended.py",
    "scripts/run_night.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_install_night_agent.py",
    "tests/test_night_gate.py",
    "tests/test_night_plan_writer.py",
    "tests/test_rehearse_t0_unattended.py",
    "tests/test_run_night.py",
    "tests/test_t0_rehearsal.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_gate tests.test_install_night_agent tests.test_run_night tests.test_t0_rehearsal tests.test_night_plan_writer tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas tests.test_docs_freshness > /tmp/d176-seat2-acceptance.log 2>&1\nrc=$?\ntail -14 /tmp/d176-seat2-acceptance.log\nexit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 239 tests in 13.461s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check > /tmp/d176-seat2-diff-check.log 2>&1\nrc=$?\ncat /tmp/d176-seat2-diff-check.log\nexit $rc",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 /tmp/d176-seat2-scope-check.py > /tmp/d176-seat2-scope-check.log 2>&1\nrc=$?\ncat /tmp/d176-seat2-scope-check.log\nexit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: scope, restricted ARM/schema-test edits, unchanged receipt validator/start-marker guard, and clause-map line pins"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS: scope,.*line pins$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests > /tmp/d176-seat2-canonical.log 2>&1\nrc=$?\ntail -24 /tmp/d176-seat2-canonical.log\nexit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK(?: \\(skipped=\\d+\\))?$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the third pack_root digest mutation, at consumption, cannot be proved against this checkout's pre-seat-3 consumer. Preparation and GO mutations pass.",
      "needs": "Provide the integrated seat-3 head for a resumed consumption regression, or designate seat 3's regression as the shared-clause evidence. Recommend seat 3 evidence plus lead replay at the integrated head; combined acceptance remains blocked."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Supplemental canonical suite was interrupted on handback (exit 130); it is not a passing full-suite result. The requested eight-module acceptance completed successfully.",
      "needs": "Lead runs the canonical suite on the integrated candidate."
    }
  ]
}
```

## Change

Installed the governing §10.3 text and producer changes. No commit created. The complete start-marker and atomic-replace guard remain unchanged.

The full symbol-level map is in [contract §9](/Users/edr/code/JouleWise-wt-d176-seat2/docs/contracts/pack_night_go_receipt.md:833).

| Item | Production site | Regression | Counterfactual |
|---|---|---|---|
| 1–2 | `arm_readiness.py:248`; inventory JSON | `test_arm_readiness_schemas.py:1694,1710,1719` | Literal/incomplete census, omitted deployment, or environment override shrinks coverage |
| 3, producer/G6 | `t0_rehearsal.py:749`; `run_night.py:1342` | `test_run_night.py:2040`; `test_rehearse_t0_unattended.py:51` | Nested, equal-to-parent, wrong-name, symlinked or overlapping roots pass |
| 4 | `rehearse_t0_unattended.py:118` | `test_rehearse_t0_unattended.py:19,34` | Stale census produces false PASS; inventory differs from HEAD |
| 5 | `run_night.py:1128,1151,1377` | `test_run_night.py:1940,2016`; `test_night_plan_writer.py:101` | Changed pack root/digest passes preparation or GO; consumption proof remains pending |
| 6 | `run_night.py:1218,1240` | `test_run_night.py:1922,1969` | Selected ARM, higher receipt, same-boot consumption or NO_GO permits GO |
| 7 | `run_night.py:1321` | `test_run_night.py:1982` | Missing, symlinked, second or substituted manifest is accepted |
| 8 | `run_night.py:1377,1456,1473` | `test_run_night.py:1864,2005` | GO precedes ARM, appears on refusal, lacks census lineage, inherits stdin, or omits any launcher flag |
| 8, evidence | `run_night.py:1278` | `test_run_night.py:2024` | Omitted/extra receipts or changed capture bytes enter GO |
| 9 | `run_night.py:1101,1151,1321` | `test_run_night.py:1957,1982` | Missing inputs or digest disagreements silently fall back |

## Verification notes

`tests.test_rehearse_t0_unattended` was absent and was added within scope; no requested modules were dropped.

All evidence is fixture-based. The supplemental canonical run was interrupted, so full-suite verification remains incomplete. The new inventory intentionally requires lead landing before HEAD authentication succeeds.

## Residual risk

**NEEDS_RULING:** Should seat 3 supply the consumption-point regression, or should this seat resume on the integrated head? Recommend seat 3 supplies it and the lead replays it after integration. That third-point proof and combined acceptance remain blocked.