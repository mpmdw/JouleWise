```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all DG-071/DG-075 ruled-addendum corrections; 22 focused tests pass, both required mutants are killed, and the real-bundle replay matches every expected statistic.",
  "workspace": {
    "base_requested": "feat/2026-09-02-paper-d",
    "base_mode": "informational",
    "head_start": "b298ffe57820552ac42b2cca9c90868c388a99ac",
    "head_end": "b298ffe57820552ac42b2cca9c90868c388a99ac",
    "upstream_end": "a3dadaddda58dc0548a47cb4c333a3249c1ca41e",
    "branch": "feat/2026-09-02-paper-d"
  },
  "pathspec": [
    "scripts/issue_dg071_dg075_statistics.py",
    "tests/test_issue_dg071_dg075_statistics.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready",
    "counts": {
      "blocker": 0,
      "should_fix": 0,
      "nit": 0,
      "focused_tests": 22,
      "refusal_reasons": 16,
      "mutation_kills": 2
    },
    "closures": {
      "C1": "done",
      "C2": "done",
      "C3": "done",
      "C4": "done",
      "C5": "done",
      "C6": "done",
      "C7": "done"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/dg071-fix2.4uuQ8F PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 22 tests in 0.144s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 22 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": "<TMPDIR>/mutant-interval",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "FAIL: test_record_interval_not_positive_refusal_reaches_main",
          "Ran 22 tests in 0.149s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "test_record_interval_not_positive_refusal_reaches_main[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": "<TMPDIR>/mutant-rail",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "FAIL: test_record_rail_set_mismatch_refusal_reaches_main",
          "Ran 22 tests in 0.148s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "test_record_rail_set_mismatch_refusal_reaches_main[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "run scripts/issue_dg071_dg075_statistics.py twice with --repository-root /Users/edr/code/JouleWise-wt-paper-d and --out <TMPDIR>/replay-{a,b}/dg071-dg075-statistics.json; cmp both JSON and Markdown pairs; shasum -a 256 all four files",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DG-071 | 406 | 116.9720 | 120.9186 | 122.9227 | 5.9508",
          "DG-075 | 405 | 117.0321 | 120.9224 | 122.9270 | 5.8949",
          "counts 406 1218 ['ane_power', 'cpu_power', 'gpu_power']",
          "tiling 0.0000004 100"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tiling 0\\.0000004 100"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check -- scripts/issue_dg071_dg075_statistics.py tests/test_issue_dg071_dg075_statistics.py",
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

The producer now groups contiguous three-rail sampler records, uses exact `Decimal` arithmetic throughout, emits schema v2 string values, discloses the complete type-7 method, verifies DG-075 tiling, and reports the ruled population and tiling fields. All obsolete `R-167-1`, six-decimal, row-population, and “duplicate timestamps” language is gone.

The tests now use three-rail fixtures and bind every remaining refusal reason through `main`.

## Closure evidence

`TMPDIR` was:

```text
<scratchpad>/dg071-fix2.4uuQ8F
```

- C1: replay reported 406 sampler records, 1218 rail rows, and rails `ane_power`, `cpu_power`, `gpu_power`. Tests cover missing rails, differing sibling intervals, and interleaved timestamp groups.
- C2: every seconds statistic and millisecond rendering is a JSON string; real-bundle exact results matched the addendum. `SCHEMA_VERSION` is v2 and `MS_RENDER_QUANTUM = Decimal("0.0001")`.
- C3: JSON contains the structured `method` object; Markdown contains `## Method`, the exact type-7 formula, even-n median convention, exact-before-rendering IQR rule, round-half-even rule, float64 limitation sentence, and worked example.
- C4: replay reported `max_tiling_gap_s = "0.0000004"` and 100 nonzero boundaries. Tests separately exercise a 5 ms gap and an end/timestamp literal mismatch.
- C5: the focused command completed with `Ran 22 tests ... OK`; all 16 refusal names are mapped below.
- C6: `test_precision_regression_uses_exact_epoch_literals` asserts exact `120.9186` ms and independently computes float64 `120.9185` ms.
- C7: both replay pairs were byte-identical and matched all dictated values.

## Refusal-to-test mapping

| Refusal | Through-`main` test |
|---|---|
| `bundle_path_mismatch` | `test_bundle_path_mismatch_refusal_reaches_main` |
| `bundle_path_unavailable` | `test_bundle_path_unavailable_refusal_reaches_main` |
| `bundle_sha256_mismatch` | `test_bundle_sha256_mismatch_refusal_reaches_main` |
| `record_schema_mismatch` | `test_record_schema_mismatch_refusal_reaches_main` |
| `record_field_missing` | `test_record_field_missing_refusal_reaches_main` |
| `record_field_invalid` | `test_record_field_invalid_refusal_reaches_main` |
| `timestamps_non_monotone` | `test_timestamps_non_monotone_refusal_reaches_main` |
| `records_not_contiguous` | `test_records_not_contiguous_refusal_reaches_main` |
| `record_interval_not_positive` | `test_record_interval_not_positive_refusal_reaches_main` |
| `record_rail_set_mismatch` | `test_record_rail_set_mismatch_refusal_reaches_main` |
| `record_set_empty` | `test_record_set_empty_refusal_reaches_main` |
| `insufficient_unique_timestamps` | `test_insufficient_unique_timestamps_refusal_reaches_main` |
| `records_do_not_tile` | `test_records_do_not_tile_refusal_reaches_main` |
| `git_commit_unavailable` | `test_git_commit_unavailable_refusal_reaches_main` |
| `git_commit_invalid` | `test_git_commit_invalid_refusal_reaches_main` |
| `output_path_invalid` | `test_output_path_invalid_refusal_reaches_main` |

Mutation copies lived only under `TMPDIR`.

```text
record_interval_not_positive guard deleted:
............F.........
FAIL: test_record_interval_not_positive_refusal_reaches_main
Ran 22 tests in 0.149s
FAILED (failures=1)

record_rail_set_mismatch guard deleted:
.............F........
FAIL: test_record_rail_set_mismatch_refusal_reaches_main
Ran 22 tests in 0.148s
FAILED (failures=1)
```

## C7 replay

```text
198fe3b83e24eeeddf8ac10a84c9171234d3c74637c45bb86c162baae09f584f  replay-a/dg071-dg075-statistics.json
198fe3b83e24eeeddf8ac10a84c9171234d3c74637c45bb86c162baae09f584f  replay-b/dg071-dg075-statistics.json
03126994053aa676edc60061c18c3eb11c5d2bb056fef08afd165d3d51023f68  replay-a/dg071-dg075-statistics.md
03126994053aa676edc60061c18c3eb11c5d2bb056fef08afd165d3d51023f68  replay-b/dg071-dg075-statistics.md

| Registry row | Sample count | Q1 (ms) | Median (ms) | Q3 (ms) | IQR (ms) |
|---|---:|---:|---:|---:|---:|
| DG-071 | 406 | 116.9720 | 120.9186 | 122.9227 | 5.9508 |
| DG-075 | 405 | 117.0321 | 120.9224 | 122.9270 | 5.8949 |
```

## Diff stat

```text
 scripts/issue_dg071_dg075_statistics.py    | 464 ++++++++++++++++++++++-------
 tests/test_issue_dg071_dg075_statistics.py | 457 ++++++++++++++++++++++------
 2 files changed, 726 insertions(+), 195 deletions(-)
```

## Verification notes

Per the task restriction, the canonical discovery suite was not run. No files under `docs/` were written. The replay hashes are pre-landing hashes at HEAD `b298ffe`; the magistrate’s post-commit reissue will change the embedded `git_commit` and therefore the artifact hashes.