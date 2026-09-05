```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Option A and all four requested regressions are implemented and focused-green; the lead-owned XS registry digest must be repinned before the tracked CLI can accept the changed producer.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "9717c8ace4fe746f048bc6ac64e9337f06aba42e",
    "head_end": "9717c8ace4fe746f048bc6ac64e9337f06aba42e",
    "upstream_end": "9717c8ace4fe746f048bc6ac64e9337f06aba42e",
    "branch": "feat/2026-09-04-fan-R7F-EXIT3-SEMANTICS-01"
  },
  "pathspec": [
    "scripts/check_paper_round7_artifacts.py",
    "scripts/paper_excursion_decomposition.py",
    "tests/test_paper_round7_artifacts.py",
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/02-sol-resume-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 34 tests in 18.862s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 34 tests in [0-9.]+s\\n\\nOK"
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
          "----------------------------------------------------------------------",
          "Ran 34 tests in 22.568s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 34 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_mixed_mismatch_then_unavailable_keeps_mismatch_and_exits_three tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_present_events_digest_drift_is_mismatch_in_producer_and_driver tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_disposition_table_drives_finalizer_and_help tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_silent_producer_exit_three_names_source_and_no_output",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 4 tests in 1.666s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile scripts/check_paper_round7_artifacts.py scripts/paper_excursion_decomposition.py tests/test_paper_round7_artifacts.py",
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
        "tail_regex": "Exit codes:[\\s\\S]*earlier comparisons remain visible\\."
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
      "text": "The changed excursion producer now hashes to 12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688, while docs/paper/results-fill-registry.md still pins 8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b; that authority path is outside WRITE_SCOPE and was preserved.",
      "needs": "Expand scope to docs/paper/results-fill-registry.md or have the lead repin the XS digest and landed provenance metadata, then run the full focused test module."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide suite and retained-corpus replay were not run, as directed; the complete test_paper_round7_artifacts module was also not run against the stale tracked XS pin.",
      "needs": "After the registry repin, run python3 -m unittest -q tests.test_paper_round7_artifacts; keep the repository-wide suite omitted under this task's preflight rule."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/paper/results-fill-registry.md"
    ],
    "reason": "The registry authenticates XS by SHA-256, so the authorized producer change necessarily invalidates its lead-owned pin.",
    "blocked_work": "Tracked-registry consistency and the full focused-module pass cannot complete until XS is repinned.",
    "minimal_change": "Replace the XS digest with 12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688 and update its landed commit/PR metadata when known."
  }
}
```

## Change

Implemented ruled option A. Replay now returns completed comparisons plus an optional typed stop record, so an anchor-summary exit 3 preserves earlier XD/F4 mismatches while `R7F REPLAY INCOMPLETE` remains the final disposition and process exit 3. A closed disposition enum/table drives exit codes, terminal tokens, the finalizer, and the generated help paragraph. Silent producer exit 3 reports its producer source and `detail=no output`.

The excursion producer now classifies missing primary inputs as exit 3 and present-byte digest disagreement as exit 2, for both `events.jsonl` and located raw powermetrics candidates. Regressions cover mixed failure, mutated events bytes through producer and driver, disposition consistency, and silent producer output. Scratch registries bind copied producer bytes without weakening the tracked-registry pin test.

## Verification notes

The first 34-test run found two scratch-fixture failures because temporary registries retained the historical XS digest; rebinding those scratch fixtures to the copied producer bytes made the identical focused command pass 34/34. The tracked registry was intentionally not changed. No repository-wide suite was run.

## Residual risk

Until the XS registry pin is updated, an ordinary tracked-registry CLI invocation stops at the always-on digest half with exit 2 before exercising replay. This is fail-closed, but option A cannot be accepted end to end against tracked authority in the current scoped diff.
