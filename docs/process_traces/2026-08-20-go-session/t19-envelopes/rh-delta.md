```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NO-GO: receipt-set eligibility is cured, but a committed-pinset lookup failure still silently skips the governed histsem gate.",
  "workspace": {
    "base_requested": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "base_mode": "exact",
    "head_start": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "head_end": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "upstream_end": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "branch": "impl/receipt-histsem"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/contracts/receipt_histsem_verifier.md",
    "joulewise/arm_readiness.py",
    "tests/test_receipt_histsem.py"
  ],
  "verdict": {
    "outcome": "NO-GO",
    "findings": [
      {
        "id": "H1",
        "severity": "should_fix",
        "title": "Committed pinset lookup failures silently disengage the governed gate",
        "location": "joulewise/arm_readiness.py:3444",
        "detail": "For a pack covered by the committed pinset, a nonzero `git show HEAD:<pinset>` result returns from `_gate_receipt_histsem` rather than producing a `histsem_*` refusal. Executed probes produced `HEAD_PINSET_FAILURE_GATE_SKIPPED` and, after making an isolated clone's Git object store unreadable, `OBJECT_STORE_FAILURE_GATE_SKIPPED`. A committed pinset deletion and a committed removal of the pack row also produced gate skips; arm then reached `readiness_schema_invalid` instead of the claimed `histsem_pinset_absent` refusal. Committed malformed pinsets correctly refuse as `histsem_pinset_invalid`."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_receipt_histsem -v > /tmp/receipt-histsem-round1-reaudit-unittest.txt 2>&1; test_exit=$?; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 11 tests in 87.385s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 /tmp/receipt_histsem_round1_probe.py . current > /tmp/receipt-histsem-round1-reaudit-probe-current.txt 2>&1; test_exit=$?; cat /tmp/receipt-histsem-round1-reaudit-probe-current.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "TWELFTH_OK",
          "PREDECESSOR_FREEZE_BOUNDARY_OK",
          "WORKTREE_histsem_pinset_absent_OK",
          "WORKTREE_histsem_pinset_invalid_OK",
          "HEAD_PINSET_FAILURE_GATE_SKIPPED",
          "OBJECT_STORE_FAILURE_GATE_SKIPPED",
          "COMMITTED_PINSET_ABSENCE_GATE_SKIPPED",
          "COMMITTED_PINSET_ABSENCE_ARM_REACHED_readiness_schema_invalid",
          "COMMITTED_ROW_ABSENCE_GATE_SKIPPED",
          "COMMITTED_PINSET_MALFORMATION_OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COMMITTED_PINSET_ABSENCE_REFUSED_histsem_"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 /tmp/receipt_histsem_contract_probe.py . > /tmp/receipt-histsem-round1-reaudit-contract-probe.txt 2>&1; test_exit=$?; cat /tmp/receipt-histsem-round1-reaudit-contract-probe.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CONTRACT_D16_PROBE_OK vocabulary=16"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONTRACT_D16_PROBE_OK vocabulary=16"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/verify_receipt_histsem.py --repository-root . --require-published > /tmp/receipt-histsem-round1-reaudit-cli.txt 2>&1; test_exit=$?; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "\"receipt_count\": 99,",
          "\"status\": \"PASS\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"receipt_count\": 99,.*\"status\": \"PASS\""
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --quiet HEAD -- configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "pinset SHA-256 d81515505d677c2ca045238e721c87eae8f38439a89a5377e58fa9064eaf2f21 equals HEAD",
          "all four r6-pinned source SHA-256 values equal HEAD"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "unchanged"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "python3 -c 'import json; from pathlib import Path; from unittest import mock; import joulewise.arm_readiness as r; root=Path(\".\").resolve(); governed={x[\"pack_path\"] for x in json.loads((root/\"configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json\").read_bytes())[\"packs\"]}; packs=[p for p in root.glob(\"configs/campaigns/*\") if p.is_dir() and p.relative_to(root).as_posix() not in governed]; assert len(packs)==8; with mock.patch.object(r,\"verify_receipt_histsem_pack\",side_effect=AssertionError(\"called\")): [r._gate_receipt_histsem(p) for p in packs]; print(\"NONLEGACY_GATE_UNCHANGED\",len(packs))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "NONLEGACY_GATE_UNCHANGED 8"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "NONLEGACY_GATE_UNCHANGED 8"
      }
    }
  ],
  "flags": []
}
```

## Findings

### H1 — should_fix: committed-pinset lookup failure skips eligibility

At [arm_readiness.py:3444](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtNEXT/joulewise/arm_readiness.py:3444), any unsuccessful `git show HEAD:<pinset>` is treated as pre-governance and returns normally. This is a counterexample to the required fail-closed refusal path for a governed pack when its committed pinset cannot be resolved.

The twelfth valid-but-unreferenced receipt cure is clean: direct verification, library gate, arm boundary, and predecessor-freeze boundary all returned `histsem_pinset_mismatch`. Working-tree pinset absence and malformation also correctly returned `histsem_pinset_absent` and `histsem_pinset_invalid`.

H2 is clean. The D16 probe verified exact 16-code vocabulary parity, pinset-anchored eligibility wording, both coordinates and lanes, archival rule, sequencing, and the detectability wording. No extra normative requirement was found. K5/K7/K12 refusal fixtures and the nine-pack differential self-test passed in V1; the pinset and all four r6-pinned files are byte-identical to `HEAD`; eight non-legacy packs did not invoke the verifier.