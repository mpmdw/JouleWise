```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed authorized D-177 reconciliation; custody mirror scope and the missing adopted paragraph block completion.",
  "workspace": {
    "base_requested": "main ac092ccd",
    "base_mode": "exact",
    "head_start": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "head_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-paper-S7-reconciliation"
  },
  "pathspec": [
    "docs/paper/protocol/prospective-comparison-protocol.md",
    "docs/contracts/paper_comparison_placements.md",
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/successor-migration-inventory.md",
    "docs/paper/round7/fill-checklist.md",
    "docs/decision_log.md",
    "tests/test_paper_comparison_placements.py",
    "tests/test_paper_successor_migration.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_comparison_placements tests.test_paper_successor_migration tests.test_paper_round7_artifacts tests.test_d165_rationale_census tests.test_gen_state tests.test_docs_freshness > /private/tmp/paper-s7-recon-acceptance.log 2>&1\ncheck_rc=$?\nprintf 'EXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-s7-recon-acceptance.log\ntail -65 /private/tmp/paper-s7-recon-acceptance.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 178 tests in 658.286s",
          "FAILED (failures=217, errors=3)",
          "EXIT_CODE=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_successor_migration tests.test_d165_rationale_census tests.test_gen_state tests.test_docs_freshness > /private/tmp/paper-s7-recon-independent-final.log 2>&1\ncheck_rc=$?\nprintf 'EXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-s7-recon-independent-final.log\ntail -15 /private/tmp/paper-s7-recon-independent-final.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 93 tests in 13.395s",
          "OK",
          "EXIT_CODE=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_successor_migration.PaperSuccessorMigrationTests.test_assembled_first_uses_use_read_only_ledger tests.test_paper_successor_migration.PaperSuccessorMigrationTests.test_characterization_reconciliation_preserves_protected_text > /private/tmp/paper-s7-recon-first-use.log 2>&1\ncheck_rc=$?\nprintf 'EXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-s7-recon-first-use.log\ncat /private/tmp/paper-s7-recon-first-use.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.244s",
          "OK",
          "EXIT_CODE=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the six X13-X16 Applicability cells in docs/contracts/paper_supply_custody.md must mirror the reconciled tables. This out-of-scope file was not modified; exact agreement and closed safety checks remain enforced.",
      "needs": "Expand WRITE_SCOPE to docs/contracts/paper_supply_custody.md."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: which exact Opus disposition paragraph is adopted? Supplied file 11 contains only a parenthetical summary. Options: supply the paragraph, or authorize wording drafted from that summary. Recommendation: supply the exact adopted text. Item 4 remains unimplemented; both protected passages remain verbatim.",
      "needs": "Provide the exact adopted paragraph or authorize drafting from the summary."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced concurrently; working HEAD remains exactly the requested ac092ccd base. No commit, rebase or merge was performed.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/contracts/paper_supply_custody.md"
    ],
    "reason": "S1 requires exact agreement among placements, registry and custody; Applicability is a shared comparison column.",
    "blocked_work": "Green three-table agreement and complete acceptance.",
    "minimal_change": "Copy the six reconciled X13-X16 Applicability cells from the placements contract into the custody proposal table; change no family, role, grant, adoption or live binding."
  }
}
```

## Change

Installed the ruled omissions, narrowed precondition, phase-attribution limitation, migration guidance, and dated D-177 entry. Updated six S1 safety-text pins while preserving exact three-table equality.

**Before:** “Instrument characterization asks four physical questions before any campaign result may rely on the instrument.”

**After:** “Instrument characterization asks four physical questions before relying on per-token conversion (the fitted joules per output token), an issued floor (a published resolution guard for assigned-energy differences), or a phase-specific claim (a statement about energy assigned to prompt processing or token generation).”

The protected methods, minimum-count/withdrawal, and Variant-0 paragraphs remain verbatim.

## Verification notes

All acceptance failures arise from the untouched custody mirror’s six stale cells; other acceptance modules, including retained-corpus replay, passed. [Acceptance log](/private/tmp/paper-s7-recon-acceptance.log).

A D-165 line-pin regression was corrected by preserving the inventory’s line count. Every added prose sentence also received a [manual first-use review](/private/tmp/paper-s7-recon-first-use-audit.md), supplementing the automated ledger check.

## Residual risk

Item 4 remains blocked: §6 Variant 0 is confirmed in `rendered-refusal.md`, but the supplied Opus file contains only a summary of the adopted paragraph.

Next lead step: expand scope for the six custody cells and supply the exact paragraph—or authorize drafting from its summary—then resume insertion and acceptance.