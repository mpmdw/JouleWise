```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Independent fixes implemented; finding 5 needs a ruling because true driver refusal codes conflict with the frozen receipt validator.",
  "workspace": {
    "base_requested": "4b25d29f",
    "base_mode": "exact",
    "head_start": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "head_end": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat2-producer"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "joulewise/t0_rehearsal.py",
    "scripts/run_night.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_t0_rehearsal tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas tests.test_night_plan_writer tests.test_install_night_agent tests.test_magistrate_watchdog tests.test_docs_freshness > /tmp/d176-seat2-fix-acceptance.log 2>&1; result=$?; tail -n 14 /tmp/d176-seat2-fix-acceptance.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 329 tests in 21.214s", "", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/d176-seat2-fix-inspect.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS tracked diff within WRITE_SCOPE; HEAD unchanged"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS tracked diff within WRITE_SCOPE; HEAD unchanged"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest discover -s tests > /tmp/d176-seat2-fix-canonical.log 2>&1; result=$?; tail -n 14 /tmp/d176-seat2-fix-canonical.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: finding 5 requires true night_courier_unavailable, night_plan_overruns_deadman and night_chain_already_started causes in pack receipts; the contract freezes validate_receipt, which rejects all three driver codes. Cause assertions pass; three validator subcases fail. Validator and registries remain unchanged.",
      "needs": "Authorize a narrow validate_receipt exception accepting registered driver codes only for REFUSED TRANSACTION_PACK, preserving receipt keys and registry separation, or rule another representation."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was interrupted at the ruling boundary after the requested acceptance run isolated the blocker; no full-suite pass claimed.",
      "needs": "Rerun canonical discovery after the ruling and fix."
    }
  ]
}
```

## Change

| Finding | Change and counterfactual |
|---|---|
| 1 | Contract `docs/contracts/pack_night_go_receipt.md:503` installs SIBLING_CHILD rows. `tests/test_run_night.py:2135` covers all four rows, including accepted named child and refused equality, nesting, basename and production containment. |
| 2 | `joulewise/night_gate.py:867` authenticates C1 records and replays C2 ARM/evidence itself. Tests at `tests/test_night_gate.py:906` and `tests/test_run_night.py:1928` catch caller-dependent fencing and forged PASS authority. |
| 3 | `tests/test_arm_readiness_schemas.py:1694` pins the shipped inventory’s four deployment identities and paths. Removing any entry fails. |
| 4 | Contract rows at `docs/contracts/pack_night_go_receipt.md:814` onward name concrete assertions and matching counterfactuals. S3 explicitly records the unresolved validator conflict. |
| 5 | `scripts/run_night.py:1041` preserves the actual cause. Regression at `tests/test_run_night.py:1968` catches relabeling; three validator assertions remain blocked. |
| 6 | `joulewise/night_gate.py:830` applies the parent exclusion only to measurement. `tests/test_run_night.py:2135` accepts rehearsal-owned ARM paths and rejects production containment. |
| 7 | `joulewise/night_gate.py:842` uses readiness’s shared key sets; classification lives at `joulewise/arm_readiness.py:442`. Root regressions iterate those keys. |
| 8 | Contract wording and scope records updated at lines 249, 469 and 616. `tests/test_magistrate_watchdog.py:328` asserts v2 TRANSACTION_PACK yields `night_plan_malformed` and HOLD_UNSAFE without crashing. |

## Verification notes

The [acceptance log](/tmp/d176-seat2-fix-acceptance.log) contains only the three failing validator subcases described in F1. The validator, receipt keys, both reason registries and three chain-marker functions remain byte-unchanged. No commit was made.

**NEEDS_RULING:** May `validate_receipt` accept registered driver causes specifically for refused TRANSACTION_PACK receipts? I recommend that narrow exception. Keeping the validator frozen requires a different ruled representation; finding 5 and acceptance remain blocked until that decision.

## Residual risk

Evidence uses fixtures and mocked machine/ARM operations. Live hardware and integrated consumer verification remain lead-owned.