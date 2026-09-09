```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Installed all five D-177 ruling items; the complete acceptance suite and diff check pass.",
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
    "docs/paper/fill-rehearsal/rendered-refusal.md",
    "docs/decision_log.md",
    "tests/test_paper_comparison_placements.py",
    "tests/test_paper_successor_migration.py",
    "docs/contracts/paper_supply_custody.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_comparison_placements tests.test_paper_successor_migration tests.test_paper_round7_artifacts tests.test_d165_rationale_census tests.test_gen_state tests.test_docs_freshness > /private/tmp/paper-s7-recon-resumed-acceptance.log 2>&1\ncheck_rc=$?\nprintf 'EXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-s7-recon-resumed-acceptance.log\ntail -45 /private/tmp/paper-s7-recon-resumed-acceptance.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 179 tests in 645.607s",
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
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/paper-s7-recon-resumed-diff-check.log 2>&1\ncheck_rc=$?\nprintf 'EXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-s7-recon-resumed-diff-check.log\ncat /private/tmp/paper-s7-recon-resumed-diff-check.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EXIT_CODE=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^EXIT_CODE=0$"
      }
    }
  ],
  "flags": []
}
```

## Change

Installed the ruled omission, narrowed precondition, phase-attribution limitation, migration dispositions, and D-177 with both conditions. The adopted paragraph appears verbatim once at P.2’s close and once in §6 Variant 0. Protected passages remain unchanged.

Updated the six S1 safety-text pins and matching custody cells; exact three-table agreement remains enforced. No commit created.

**Before:** “Instrument characterization asks four physical questions before any campaign result may rely on the instrument.”

**After:** “Instrument characterization asks four physical questions before relying on per-token conversion (the fitted joules per output token), an issued floor (a published resolution guard for assigned-energy differences), or a phase-specific claim (a statement about energy assigned to prompt processing or token generation).”

## Verification notes

No additional gloss was needed: P.2 already constructs [identical-condition null containment](/Users/edr/code/JouleWise-wt-paper-S7recon/docs/paper/protocol/prospective-comparison-protocol.md:104) through its interval, mean, and maximum tests, and [phase accounting](/Users/edr/code/JouleWise-wt-paper-S7recon/docs/paper/protocol/prospective-comparison-protocol.md:149) through its signed residual and interpretation. The Variant-0 copy refers back to those methods.

The [sentence-level first-use review](/private/tmp/paper-s7-recon-resumed-first-use-audit.md) supplements the automated ledger and verbatim-paragraph checks. Custody inspection confirmed only the six authorized `Applicability` cells changed.