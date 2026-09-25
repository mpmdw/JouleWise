```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "C1–C6 are complete; idle parity witnesses match the base and final V1 passes.",
  "workspace": {
    "base_requested": "7647bb2e",
    "base_mode": "descendant",
    "head_start": "f170af7c98eec1dd8745e072a7022f9ab308f9dc",
    "head_end": "f170af7c98eec1dd8745e072a7022f9ab308f9dc",
    "upstream_end": "f170af7c98eec1dd8745e072a7022f9ab308f9dc",
    "branch": "feat/2026-09-24-a280-b0-kind-dispatch"
  },
  "pathspec": [
    "scripts/run_night.py",
    "tests/test_night_kinds.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_evidence_night tests.test_gen_evidence_night tests.test_night_gate tests.test_night_agent_install tests.test_run_night tests.test_zero_capture_facts tests.test_kind_dispatch_literals",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 603 tests in 1258.560s", "OK (skipped=9)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=9\\)"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check 2ea6a7ec",
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
      "kind": "smoke",
      "cmd": "sh /tmp/278ebc9e/b0fix1/v3.sh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["M3 pre-fix:", "OK", "M3 head mutant:", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_base_archive_byte_goldens tests.test_night_kinds.NightKindTests.test_refusal_parity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 28.981s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full repository discover suite was not run; the brief's exact V1 suite passed.",
      "needs": "Lead final verification before merge."
    }
  ]
}
```

## Change

The `f170af7c` draft was reviewed in full. It needed one cleanup parity regression and a guard for a non-object receipt; both are now uncommitted.

| Cure | Draft audit and final outcome | Witness |
|---|---|---|
| C1 | The draft removed plan-field kind inference and the `None → calibration` mapping, separated row-neutral reporting from dispatch, and pinned the shared artifact inventory. Reporting performs no kind read, so it needs no new diagnostic field in `result.json`; adding one would change idle bytes. I added the receipt shape guard in [run_night.py](/Users/edr/code/wt-7370d0fb-a280b0/scripts/run_night.py:1005) and the missing unreadable-wrapper cleanup test in [test_night_kinds.py](/Users/edr/code/wt-7370d0fb-a280b0/tests/test_night_kinds.py:319). | w1: all four results written, with `result.json` byte-identical to base under fixed clocks and paths. Cleanup: base/head both returned `None`, wrote the same refused outcome, and called refusal writing once. Sol F1: pre-fix inferred idle or calibration; final tree gives typed `ValueError` for missing identity and C5 conflict. |
| C2 | The draft restored the historical `candidate_state` check and placed wrapper/source binding after sealed-byte validation in [evidence_night.py](/Users/edr/code/wt-7370d0fb-a280b0/joulewise/evidence_night.py:636). No further change was needed. | w2: intact, archived clone, removed chain, and tampered chain were all `ACCEPTED` at base and final tree. |
| C3 | The draft validates `NightPlan` before reading `chain_path` in [evidence_night.py](/Users/edr/code/wt-7370d0fb-a280b0/joulewise/evidence_night.py:241). | F2: pre-fix `TypeError`; final `Refused sealed candidate failed plan`, matching the base refusal with a usable candidate interpreter. |
| C4 | The draft removed `chain.started` and asserts incomplete scanning in [test_night_kinds.py](/Users/edr/code/wt-7370d0fb-a280b0/tests/test_night_kinds.py:558). | M3: pre-fix mutant `OK`; final-tree mutant `FAILED (failures=1)` on `scan_complete`. |
| C5 | The draft moved alternate-template refusal after plan validation and receipt-class checking in [gen_evidence_night.py](/Users/edr/code/wt-7370d0fb-a280b0/scripts/gen_evidence_night.py:20). Its idle-row fallback is used only to preserve refusal ordering; it cannot dispatch an unmatched template. | Base/head both return `GenerationRefusal evidence requires v2 DIAGNOSTIC_NO_PACK` for wrong class and `PlanError plan must be an object` for a malformed plan. |
| C6 | The draft covered symbolic `KIND` literals in [test_kind_dispatch_literals.py](/Users/edr/code/wt-7370d0fb-a280b0/tests/test_kind_dispatch_literals.py:15), caught lazy-import failure in [zero_capture_facts.py](/Users/edr/code/wt-7370d0fb-a280b0/joulewise/zero_capture_facts.py:141), and removed repeated kind reads from durable reporting. No residual nit remains. | V1 and V3 passed. |

## Verification notes

The first V1 run had one eight-second watchdog timeout in `journal_block` while V3 was running concurrently. That test passed alone in 7.502 seconds; the exact V1 command then passed without competing test work. Changes remain uncommitted as directed.