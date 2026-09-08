```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "87 tests and fallback validation pass; integration preserves all branch files, with two literal acceptance discrepancies.",
  "workspace": {
    "base_requested": "int/2026-09-08-paper-s1-s6-s7",
    "base_mode": "exact",
    "head_start": "b1217899216145ec239c6099c875b0ae28ce0a6a",
    "head_end": "b1217899216145ec239c6099c875b0ae28ce0a6a",
    "upstream_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 1},
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "path": "docs/paper/round7/fill-checklist.md",
        "line": 81,
        "summary": "Main's dated iCloud addendum survives only as a shortened, undated policy note.",
        "detail": "S7 replaced the 2026-09-08 ICLOUD-BACKUP-PROBE-01 addendum with Retained replay environment note. Core policy survives, but the date, task identity, and explicit is_dir/both-globs budget coverage do not. This replacement already exists at S7's head; it is not merge corruption.",
        "recommendation": "Restore the dated addendum and its precise budget coverage alongside S7's guidance, or explicitly waive literal preservation."
      },
      {
        "id": "R2",
        "severity": "nit",
        "path": "docs/contracts/paper_comparison_placements.md",
        "line": 56,
        "summary": "S1 and S6 agree numerically on D-168 but do not use identical census wording.",
        "detail": "S1 says All eight R_*; four comparative R_cm_*; four absolute R_cm_* N/A dispositions. S6 line 82 says exactly eight ordinary/independent ratios and four comparative R_cm values for comparative shared-energy-sign / local-corner components.",
        "recommendation": "Use a shared census sentence if identical wording remains an acceptance requirement."
      }
    ],
    "confirmed": [
      "S6 delta contains only the two described gloss edits; DS-33 matches the registry's historical unresolved prefill claim-floor slot.",
      "S1 delta adds only traces 75 and 90: 565 lines total; the provenance citation resolves.",
      "S1, S6 and S7 change mutually disjoint file sets, and every changed file matches its respective branch head at integration HEAD.",
      "S7 is based on current main; no conflict residue exists.",
      "All four floor-slot token-family names match exactly.",
      "Registry diff contains no deleted content lines; literal FILL tokens and retired rows remain unchanged.",
      "The literal grep '^-' command prints only the standard --- diff header, not a deleted registry line.",
      "Workspace remains clean and HEAD unchanged."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_comparison_contract tests.test_paper_comparison_placements tests.test_paper_successor_migration tests.test_docs_freshness tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 87 tests in 21.091s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 87 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"]},
      "expected": {"exit_code": 0, "tail_regex": "METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "grep -rn '^<<<<<<<\\|^=======$\\|^>>>>>>>' docs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff main -- docs/paper/results-fill-registry.md | grep '^-'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["--- a/docs/paper/results-fill-registry.md"]},
      "expected": {"exit_code": 0, "tail_regex": "^--- a/docs/paper/results-fill-registry\\.md$"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check main HEAD",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "docs/process_traces/2026-09-08-handoff-redo/90-scout-paper-briefs-astra-report.md:302: trailing whitespace.",
          "+**GENRE:** implementation  "
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Checkout is detached, but HEAD exactly matches the requested integration ref.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Extra diff-whitespace check flags six Markdown two-space line endings in added trace 90; these appear to be intentional hard breaks.",
      "needs": ""
    }
  ]
}
```

## Findings

1. **R1 — should_fix:** The iCloud policy remains, but its dated addendum and precise budget wording were shortened in S7. Restore them or waive literal preservation.
2. **R2 — nit:** D-168 census semantics agree; wording is not identical. Normalize it if byte-identical wording is required.

## Residual risk

Verification covered the requested desk checks, not live hardware or external-corpus replay. No files were modified.