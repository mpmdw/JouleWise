```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the scoped ownership-forgery harness; it passes the legal corpus and exposes 109 pairwise and 105 sampled-triple seal escapes at 0fa4e6e3.",
  "workspace": {
    "base_requested": "0fa4e6e3",
    "base_mode": "exact",
    "head_start": "0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e",
    "head_end": "0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e",
    "upstream_end": null,
    "branch": "test/2026-09-24-a291-ownership-harness"
  },
  "pathspec": [
    "tests/test_scored_ownership_forgery.py",
    "tests/scored_ownership_oracle.py",
    "tests/scored_ownership_generator.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready",
    "pairwise_escapes": 109,
    "sampled_triple_escapes": 105,
    "checker_crashes": 0,
    "seal_crashes": 0
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_legal_corpus tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_regressions tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_checker_exception_is_failure",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LEGAL total_cases=48 rosters=1868 violations=0",
          "NAMED legal-contrast oracle=ACCEPT",
          "Ran 3 tests in 216.095s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rosters=1868 violations=0[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "A291_ESCAPE_LOG=/tmp/278ebc9e/a291own/escapes-pair.jsonl A291_INCONCLUSIVE_LOG=/tmp/278ebc9e/a291own/inconclusive-pair.jsonl python3 -B -m unittest -v tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_pairwise_seal_property > /tmp/278ebc9e/a291own/pair.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FORGER arity=2 ready=4800 inapplicable=1274 operator_errors=23 refresh_errors=239 escapes=109 checker_crashes=0 seal_crashes=0 runtime_s=12.917",
          "Ran 1 test in 12.918s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "escapes=[1-9][0-9]*[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "A291_ESCAPE_LOG=/tmp/278ebc9e/a291own/escapes-triple.jsonl A291_INCONCLUSIVE_LOG=/tmp/278ebc9e/a291own/inconclusive-triple.jsonl python3 -B -m unittest -v tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_sampled_triples_seal_property > /tmp/278ebc9e/a291own/triple.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FORGER arity=3 ready=8092 inapplicable=3799 operator_errors=139 refresh_errors=642 escapes=105 checker_crashes=0 seal_crashes=0 runtime_s=19.590",
          "Ran 1 test in 19.591s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "escapes=[1-9][0-9]*[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions > /tmp/278ebc9e/a291own/named-seal.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "NAMED_SEAL {\"AUD-1\": \"accepted\", \"B1\": \"accepted\", \"B2\": \"accepted\", \"legal-contrast\": \"accepted\", \"probe-D\": \"refused:inv_11\"}",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "AUD-1.*accepted[\\s\\S]*FAILED \\(failures=1\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The baseline seal accepts the documented AUD-1, B1 and B2 forgeries; this is the intended red result for the test seat.",
      "needs": "Lead-owned production repair and the next cold gate."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Malformed compositions that raised during operator application or derived-field refresh were recorded as inconclusive; the full repository suite was not run because the new seal assertions are deliberately red at this head.",
      "needs": ""
    }
  ]
}
```

## Change

Added an independent closed INV-11 oracle, eight composable ownership operators, and tests for the 1,868-roster legal corpus, named witnesses, checker-crash handling, and the finalizing seal. Only the three scoped test files are uncommitted.

## Verification notes

The pairwise escape counts by ordered operator pair are:

| Operators | Escapes |
|---|---:|
| `clone_block_new_id` → `terminalise_block` | 4 |
| `list_live_new_envelope` → `list_live_new_envelope` | 5 |
| `list_live_new_envelope` → `retarget_terminal` | 15 |
| `list_live_new_envelope` → `revive_voided` | 3 |
| `retarget_terminal` → `list_live_new_envelope` | 16 |
| `retarget_terminal` → `revive_voided` | 20 |
| `revive_voided` → `list_live_new_envelope` | 4 |
| `revive_voided` → `retarget_terminal` | 19 |
| `revive_voided` → `revive_voided` | 4 |
| `terminalise_block` → `clone_block_new_id` | 3 |
| `terminalise_block` → `retarget_terminal` | 16 |

Of the 109 pairwise escapes, 80 have two live owners and no terminal entry (B1/B2 class), seven have two live owners plus a terminal entry (AUD-1 class), and 22 have one live owner plus a terminal entry. Complete records include operator combination, seed, case, roster index, and per-item counts in [pairwise escapes](/tmp/278ebc9e/a291own/escapes-pair.jsonl) and [triple escapes](/tmp/278ebc9e/a291own/escapes-triple.jsonl).

## Residual risk

The 262 pairwise and 781 triple compositions that raised during operator application or derived-field refresh are recorded in [pairwise inconclusives](/tmp/278ebc9e/a291own/inconclusive-pair.jsonl) and [triple inconclusives](/tmp/278ebc9e/a291own/inconclusive-triple.jsonl); they did not reach the seal assertion.