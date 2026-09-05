```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Refuter blockers B2 and B3 are cured with discriminating regressions; B1 remains blocked solely on the out-of-scope tracked XS registry pin.",
  "workspace": {
    "base_requested": "6dd1f1def41853f3c41cfd6b0843eca0868e0ba4",
    "base_mode": "exact",
    "head_start": "6dd1f1def41853f3c41cfd6b0843eca0868e0ba4",
    "head_end": "6dd1f1def41853f3c41cfd6b0843eca0868e0ba4",
    "upstream_end": "04cd6e52e9d6ed2da369398bb448c5454f1917b3",
    "branch": "feat/2026-09-04-fan-R7F-EXIT3-SEMANTICS-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/03-sol-fix-round-1-report.md",
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_paper_round7_artifacts.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_disposition_table_drives_finalizer_and_help tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_present_raw_digest_drift_is_mismatch_in_producer_and_driver tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_missing_events_is_incomplete_in_producer_and_driver tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_present_events_digest_drift_is_mismatch_in_producer_and_driver tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_mixed_mismatch_then_unavailable_keeps_mismatch_and_exits_three tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_silent_producer_exit_three_names_source_and_no_output",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.245s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 36 tests in 3.625s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 36 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 51 tests in 3.740s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 scripts/check_paper_round7_artifacts.py --literals-only 2>&1 | rg 'MISMATCH digest XS|R7F LITERALS-ONLY COMPARED'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "MISMATCH digest XS: expected '8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b', observed '12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688'",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --help | sed -n '/Exit codes:/,$p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Exit codes:",
          "  0 when every requested comparison completes and agrees.",
          "  2 when a completed comparison, producer integrity check, or producer execution definitively disagrees.",
          "  3 when required input is unavailable and the requested replay cannot complete; earlier comparisons remain visible."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Exit codes:[\\s\\S]*  2 when a completed comparison[\\s\\S]*  3 when required input is unavailable"
      }
    },
    {
      "id": "V6",
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
      "text": "B1 requires repinning the tracked XS source identity in docs/paper/results-fill-registry.md, which is outside the exhaustive WRITE_SCOPE and was not modified.",
      "needs": "Resume with docs/paper/results-fill-registry.md added to WRITE_SCOPE, repin XS to sha256 12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688 with current provenance, then rerun V3 and V4."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The complete touched test module and tracked literals-only CLI remain red only at the stale XS pin.",
      "needs": "After the scoped registry repin, require the complete 51-test module and tracked CLI to pass."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/paper/results-fill-registry.md"
    ],
    "reason": "The registry authenticates the changed XS producer by SHA-256; its old pin necessarily disagrees with the authorized producer bytes.",
    "blocked_work": "Refuter blocker B1, tracked replay acceptance, and a green complete touched-module run cannot be completed.",
    "minimal_change": "At line 739, replace XS sha256 8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b with 12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688 and refresh its landed provenance metadata."
  }
}
```

## Change

Refuter finding-to-cure map:

| Finding | Cure | File:line |
| --- | --- | --- |
| B1 — stale tracked XS identity | Not writable in this scope. The exact required digest is recorded in `scope_expansion`; the fail-closed pin remains intact. | `docs/paper/results-fill-registry.md:739` |
| B2 — help regression compared a duplicated sentence to itself | Removed the duplicated numeral from the prose field and render help from `Disposition.exit_code`; the regression now pins the independent 0/2/3 codes, terminal tokens, and clauses. A `2 when` → `7 when` prose mutation can no longer remain green. | `scripts/check_paper_round7_artifacts.py:180`, `scripts/check_paper_round7_artifacts.py:1033`, `tests/test_paper_round7_artifacts.py:870` |
| B3a — existing wrong-digest raw capture lacked a regression | Added the named on-disk wrong-raw counterfactual and asserted producer exit 2 plus driver exit 2 and mismatch output. | `scripts/paper_excursion_decomposition.py:140`, `scripts/paper_excursion_decomposition.py:817`, `tests/test_paper_round7_artifacts.py:753` |
| B3b — absent `events.jsonl` lacked a regression | Added the named absent-events counterfactual and asserted producer exit 3 plus driver exit 3 and incomplete-replay output. | `scripts/paper_excursion_decomposition.py:177`, `scripts/paper_excursion_decomposition.py:814`, `tests/test_paper_round7_artifacts.py:817` |

No magistrate-owned state document was changed. No state-row text is proposed before B1 and its full-module verification close.

## Verification notes

The refuter-shaped tests and all focused non-corpus classes are green. The complete touched module has exactly two failures, both at the same stale XS digest precondition; the tracked literals-only CLI likewise reports one mismatch and exits 2. Per preflight, no repository-wide suite ran.

## Residual risk

Option A remains fail-closed but is not landable until the lead expands scope for the one-line registry repin (plus current provenance) and reruns V3/V4 green.
