```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Five cures verified; O4 remains unresolved because the replacement provenance path does not exist. All 49 focused tests pass; no additional delta regression found.",
  "workspace": {
    "base_requested": "37e5a429",
    "base_mode": "exact",
    "head_start": "b6d700e58c314c359be04be087d818d4771d76db",
    "head_end": "b6d700e58c314c359be04be087d818d4771d76db",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 0
    },
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "path": "docs/contracts/paper_comparison_placements.md",
        "line": 6,
        "summary": "O4 persists: the new scout-crosswalk provenance citation points to a nonexistent file.",
        "evidence": "ls docs/process_traces/2026-09-08-handoff-redo/75-scout-paper-crosswalk-astra-report.md returns exit 1: No such file or directory.",
        "requested_change": "Supply the cited authoritative report in the reviewable tree or replace the citation with a resolvable authoritative source."
      }
    ],
    "cure_checks": {
      "O1": "PASS: dated COMPLETE and NON-FILLABLE note; remaining incomplete/await matches concern historical retired rows.",
      "O2": "PASS: exactly 31 Applicability and 10 Missing evidence values match the test vocabulary. Both columns are mirrored into custody; all 66 placements agree across three tables. Independent TMPDIR-copy mutations of each column caused the agreement test to fail with the expected closed-vocabulary error.",
      "O3": "PASS: all four named S6 token families appear in each of the four model/phase X4 Site cells and the reading rules, consistent with S6's logical floor-slot contract.",
      "O4": "FAIL: replacement provenance path does not resolve.",
      "O5": "PASS: X1 retains an UNRESOLVED candidate-route grant; tests reject an adopted grant and accept an alternative candidate family.",
      "O6": "PASS: five matching FILL tokens each occur exactly once; appendix occurrences are escaped. All 228 retired rows are byte-identical to main; registry diff against main is 89 additions, zero deletions.",
      "regressions": "No additional regression found in the complete four-file delta; placement identities and unrelated table cells are preserved."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_comparison_placements tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 49 tests in 16.548s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 49 tests in .*\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "ls docs/process_traces/2026-09-08-handoff-redo/75-scout-paper-crosswalk-astra-report.md",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["ls: docs/process_traces/2026-09-08-handoff-redo/75-scout-paper-crosswalk-astra-report.md: No such file or directory"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "75-scout-paper-crosswalk-astra-report\\.md"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "grep -o '\\[FILL:[A-Z0-9-]*\\]' docs/paper/results-fill-registry.md | sort | uniq -c",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["   1 [FILL:DS-32]", "   1 [FILL:OB-01]", "   1 [FILL:OR-01]", "   1 [FILL:PE-01]", "   1 [FILL:PG-08]"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^\\s+1 \\[FILL:"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --numstat main -- docs/paper/results-fill-registry.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["89\t0\tdocs/paper/results-fill-registry.md"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^89\\s+0\\s+docs/paper/results-fill-registry\\.md"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": []
}
```

## Findings

**R1 — should_fix:** The replacement provenance citation at `docs/contracts/paper_comparison_placements.md:6–7` still cannot be resolved. Supply the authoritative report or correct the reference, then repeat the path check. No repository files were changed.

## Residual risk

Verification covered the requested delta, S6 contract comparison, temporary-copy counterfactuals, and focused suites. The full repository suite and live issuance were outside this read-only re-audit.