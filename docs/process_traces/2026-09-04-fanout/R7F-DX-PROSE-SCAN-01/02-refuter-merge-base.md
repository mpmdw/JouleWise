```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "LANDABLE: the refreshed merge-base delta is in scope, every claimed focused check passes, and the prose-refusal mutation is killed.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "aa15af731dbf71560985e58dc4a8fa65ce547593",
    "head_end": "aa15af731dbf71560985e58dc4a8fa65ce547593",
    "upstream_end": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "branch": "feat/2026-09-04-fan-R7F-DX-PROSE-SCAN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/R7F-DX-PROSE-SCAN-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/private/tmp/r7f-prose-scan-no-corpus python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 48 tests in 1.567s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 48 tests in [0-9.]+s[\\s\\S]*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_unmarked_rendered_literal_inside_dx_prose_region_is_refused tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_unmarked_rendered_literal_outside_dx_prose_region_passes tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_rendered_literal_with_own_marker_inside_dx_prose_region_passes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.278s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 scripts/check_paper_round7_artifacts.py --literals-only | tail -n 4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ok   figure offset mark 57",
          "ok   figure offset mark 58",
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F PLACED 0/16\\nR7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0$"
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-status \"$base\"..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M docs/paper/round7/fill-checklist.md",
          "A docs/process_traces/2026-09-04-fanout/R7F-DX-PROSE-SCAN-01/01-sol-report.md",
          "M scripts/check_paper_round7_artifacts.py",
          "M tests/test_paper_round7_artifacts.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fill-checklist.md[\\s\\S]*01-sol-report.md[\\s\\S]*check_paper_round7_artifacts.py[\\s\\S]*test_paper_round7_artifacts.py$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); for repo_file in RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md; do if git diff --quiet \"$base\"..HEAD -- \"$repo_file\"; then printf 'NO_DELTA %s\\n' \"$repo_file\"; else printf 'DELTA %s\\n' \"$repo_file\"; fi; done",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "NO_DELTA RUN_STATE.md",
          "NO_DELTA TASK_QUEUE.md",
          "NO_DELTA docs/process/state_kernel.json",
          "NO_DELTA docs/decision_log.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^(NO_DELTA .+\\n){3}NO_DELTA docs/decision_log.md$"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "(cd /private/tmp/r7f-refuter.KOIqUB/repo && R7F_CORPUS_ROOT=/private/tmp/r7f-prose-scan-no-corpus python3 -m unittest tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_unmarked_rendered_literal_inside_dx_prose_region_is_refused tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_unmarked_rendered_literal_outside_dx_prose_region_passes tests.test_paper_round7_artifacts.TypedArtifactCliTests.test_rendered_literal_with_own_marker_inside_dx_prose_region_passes)",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 0.343s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "Ran 3 tests in [0-9.]+s[\\s\\S]*FAILED \\(failures=1\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The focused module deliberately skipped its unrelated retained-corpus replay because R7F_CORPUS_ROOT named an absent scratch path; the changed desk-local prose path and CLI were executed.",
      "needs": ""
    }
  ]
}
```

## Findings

None.

## Evidence

The reviewed range was exactly `git diff $(git merge-base origin/main HEAD)..HEAD`, resolving to `b0ed6991c11f3a515ad293760c6dfc031adda8e1..aa15af731dbf71560985e58dc4a8fa65ce547593`. Its four paths exactly equal the implementer's declared scope. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` each show no delta.

All four checks claimed in `01-sol-report.md` pass when replayed. The focused module ran 48 tests with its one declared corpus skip; the three ruled CLI regressions ran separately; the literals-only smoke tail remained `R7F PLACED 0/16` and `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`; and the claimed clean-worktree `git diff --check` exited 0. A range-aware `git diff --check b0ed6991c..HEAD` also exited 0.

The behavioral counterfactual input is the in-region sentence `The retained calibration refused 49 of 59 pulses.` with no `[FILL:DX-013]` marker. In an isolated temp copy, deleting only the `check_prose_literals` integration call changed the checker from exit 2 to exit 0 on that input, so `test_unmarked_rendered_literal_inside_dx_prose_region_is_refused` failed `0 != 2`; the outside-region and correctly marked controls still passed. This kills the revert and proves the test invokes the mutated production CLI rather than a spoofed helper. Direct probes also confirmed the DX-020/DX-023 longest-rendering overlap does not false-fail a correctly marked DX-023 literal.

No previous `02-refuter-merge-base.md` or other refuter verdict was present in this mission directory. Therefore there was no previous-round non-staleness blocker to re-test; trusted mutable identifiers and occupied-root admission are not mechanisms in this delta. The false-counterfactual/spoofable-CLI class was nevertheless re-tested by V7 and is closed.

## Residual risk

The retained-corpus producer byte replay was not rerun; V1 intentionally reproduced the implementer's focused command and its declared single skip. The mission changes only the always-on skeleton prose scan, which V1, V2, V3, and V7 execute.
