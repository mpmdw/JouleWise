```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the bounded round-7 diagnostic prose scan, its three counterfactual command-line regressions, and the fill-checklist closure statement.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-R7F-DX-PROSE-SCAN-01"
  },
  "pathspec": [
    "docs/paper/round7/fill-checklist.md",
    "docs/process_traces/2026-09-04-fanout/R7F-DX-PROSE-SCAN-01/01-sol-report.md",
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_paper_round7_artifacts.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
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
          "Ran 48 tests in 1.388s",
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
          "Ran 3 tests in 0.272s",
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
    }
  ],
  "flags": []
}
```

## Change

The round-7 fence now searches only the diagnostic-value prose region opened
by the registry's mandatory standing sentence and ended by the next Markdown
heading. Within that region, a registered rendered value produces
`MISMATCH prose DX-nnn` unless its own fill marker is immediately before it.
The existing marker-value checks and placement census remain unchanged.

The scan assigns an overlapping character span to the longest registered
rendering. This is necessary because the population value `15` (registry row
DX-020) is also a component of the longer control rendering in registry row
DX-023; a correctly marked DX-023 value must not be misclassified as bare
DX-020 prose.

The three required command-line regressions construct a complete marked
diagnostic region, then prove the following counterfactuals: the unmarked
phrase `refused 49 of 59 pulses` inside the region exits 2 and names
`MISMATCH prose DX-013`; the same phrase after the next heading exits 0; and
the same in-region value with `[FILL:DX-013]` immediately before it exits 0.
Removing the new prose-check integration call makes the first regression exit
0, so the refusal is not supplied by the pre-existing placement census.

The fill checklist's deferral sentence now states the installed boundary and
failure form. No hardware, external operator action, dependency installation,
or ruling remains for this kernel row.

Magistrate-owned close-out remains intentionally unedited: mark
`R7F-DX-PROSE-SCAN-01` closed in the state kernel and regenerate its queue and
run-state projections after accepting this diff. No decision-log or frozen
paper-skeleton change is indicated by the row's acceptance criteria.

| Finding | Decision | Executed or governing evidence |
| --- | --- | --- |
| A global scan would confuse unrelated numbers with registered values. | Start at the mandatory diagnostic standing sentence and stop before the next line beginning with `#`. | Magistrate ruling §A2; V2 outside-region regression. |
| A short registered value can occur inside another row's longer registered rendering. | The longest registered rendering owns a containing character span. | Initial focused run exposed DX-020 `15` inside the correctly marked DX-023 control rendering; V1 and V2 pass after the ownership rule. |
| The current skeleton has no diagnostic placements. | Preserve the zero-placement baseline and its exact successful tail. | V3. |
| The row has no hardware or pending dependencies. | Close the desk-completable implementation without a ruling request. | Kernel `dependencies: []`, lane `agent`, and the acceptance evidence. |

## Verification notes

The repository-wide test suite was not run, as required by the preflight
rule. V1 intentionally points `R7F_CORPUS_ROOT` at an absent scratch path, so
the focused module skips its unrelated retained-corpus replay and executes all
desk-local fence tests. The retained-corpus replay did execute during the
first focused development run; that run completed all 48 tests and failed
only the two newly added passing cases because DX-020's short value was first
misclassified inside DX-023. That finding produced the longest-rendering span
rule recorded above. The final focused module and all three acceptance-shaped
regressions pass.
