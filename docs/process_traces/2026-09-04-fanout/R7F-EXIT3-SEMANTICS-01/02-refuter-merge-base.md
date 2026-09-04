```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission delta is scope-clean and its focused claims pass, but it is not landable: the tracked XS pin is stale and two required counterfactual fences are non-discriminating or absent.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "descendant",
    "head_start": "6dd1f1def41853f3c41cfd6b0843eca0868e0ba4",
    "head_end": "6dd1f1def41853f3c41cfd6b0843eca0868e0ba4",
    "upstream_end": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "branch": "feat/2026-09-04-fan-R7F-EXIT3-SEMANTICS-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "location": "docs/paper/results-fill-registry.md:739; tests/test_paper_round7_artifacts.py:187",
        "text": "The changed XS producer is still authenticated by its old digest. The tracked CLI refuses the checkout before replay, and the touched test module has two failures. This is the implementation report's prior non-staleness blocker, re-tested and still open.",
        "counterfactual": "With XS at sha256 12d0293b... but the tracked pin at 8733ff03..., --literals-only exits 2 with MISMATCH digest XS; repinning to the landed bytes is required for the checker and module to pass."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "location": "scripts/check_paper_round7_artifacts.py:181; scripts/check_paper_round7_artifacts.py:1033; tests/test_paper_round7_artifacts.py:753",
        "text": "The disposition regression compares the help sentence only to itself. The numeric exit code is duplicated inside free-form help text, so runtime and recorded disposition can disagree while the claimed focused suite stays green; this misses the kernel acceptance condition.",
        "counterfactual": "In a temp copy, changing only the mismatch help prefix from '2 when' to '7 when' left all 34 claimed focused tests green although _finalize still returned 2."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "location": "scripts/paper_excursion_decomposition.py:140; scripts/paper_excursion_decomposition.py:177; tests/test_paper_round7_artifacts.py:697",
        "text": "Two producer disposition changes have no defect-shaped regression: an existing raw capture with the wrong digest must exit 2, and a missing events.jsonl must exit 3. The only producer test covers present events-byte drift.",
        "counterfactual": "In temp copies, routing wrong raw bytes back to ArtifactsUnavailable, or deleting the missing-events guard, each left all 34 claimed focused tests green."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "BASE=$(git merge-base origin/main HEAD); git diff --name-only $BASE..HEAD; for p in RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md; do git diff --quiet $BASE..HEAD -- $p || exit 1; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/check_paper_round7_artifacts.py",
          "scripts/paper_excursion_decomposition.py",
          "tests/test_paper_round7_artifacts.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_paper_round7_artifacts\\.py$"
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
          "Ran 34 tests in 3.979s",
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
          "Ran 4 tests in 0.232s",
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
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 49 tests in 4.187s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 49 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 scripts/check_paper_round7_artifacts.py --literals-only",
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
      "id": "V6",
      "kind": "other",
      "cmd": "cd /private/tmp/r7f-refuter-help-drift.IcwBTx && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 34 tests in 1.940s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "cd /private/tmp/r7f-refuter-raw.bwhPJp && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts.RefusalTests tests.test_paper_round7_artifacts.TypedArtifactCliTests tests.test_paper_round7_artifacts.InvocationTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 34 tests in 1.903s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check $(git merge-base origin/main HEAD)..HEAD",
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
  "flags": []
}
```

## Findings

### B1 — blocker — tracked XS identity is stale

The producer hashes to `12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688`, while the tracked registry still authenticates `8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b`. The complete touched module fails `test_registry_pinned_files_match` and the retained-corpus test at their digest precondition; the real literals-only CLI exits 2. The scope-clean implementation report already identified this blocker, and the refresh did not cure it.

### B2 — blocker — disposition/help counterfactual is false

`help_sentence` duplicates its own numeric code instead of `_exit_code_help` rendering `exit_code`. The test merely asks whether that same sentence appears in generated help. A one-line mutation from `"2 when"` to `"7 when"` survived the entire claimed 34-test set, so the required regression does not fail when the recorded disposition disagrees with runtime. Render the numeral from `row.exit_code` (or independently parse/compare it) and add a mutation-discriminating assertion.

### B3 — blocker — producer branches lack regressions

The new events-drift test is discriminating: routing its exception back to `ArtifactsUnavailable` failed as expected. No equivalent test reaches wrong-digest `raw/powermetrics.plist`, and no direct producer test reaches absent `events.jsonl`. Reverting either new branch left all 34 claimed tests green. Add direct producer-and-driver cases for those two counterfactual inputs.

The other changed behaviours did survive mutation checks: dropping completed XD/F4 comparisons made the mixed-failure test fail; changing finalizer returns made the table test fail; changing silent-exit detail made the silent-producer test fail; restoring the old preflight terminal token made the absent-corpus invocation fail.

Scope inspection passed: the mission delta contains only its two reports, two scripts, and one test module; `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta. No earlier refuter verdict is present in the mission directory.

## Residual risk

No repository-wide suite was run, per preflight. Retained-corpus replay remains blocked at the stale tracked XS pin, so replay equivalence after repinning is not established by this review.
