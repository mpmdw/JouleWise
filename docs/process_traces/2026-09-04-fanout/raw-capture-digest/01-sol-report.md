```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Exact raw-file checking is implemented and the focused tests pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-raw-capture-digest"
  },
  "pathspec": [
    "joulewise/bundle.py",
    "joulewise/reduce.py",
    "tests/fixtures/d117_v2_production/strict_seed_bundle/metadata.json",
    "tests/test_bundle.py",
    "tests/test_reduce.py",
    "docs/process_traces/2026-09-04-fanout/raw-capture-digest/01-sol-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_bundle tests.test_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 209 tests in 437.293s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 209 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_p2038_production_path.P2038ProductionPathTests.test_retained_v2_production_fixture_is_a_refusal_arm",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 1 test in 2.253s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_salvage_dangler",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 24 tests in 1.939s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 24 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
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
      "kind": "lint",
      "cmd": "python3 -c 'import re; from pathlib import Path; p=Path(\"docs/process_traces/2026-09-04-fanout/raw-capture-digest/01-sol-report.md\"); t=p.read_text(); labels=re.findall(r\"^(C[0-9]+|V[0-9]+|R[0-9]+)\\. \", t, re.M); rows=re.findall(r\"^\\| (C[0-9]+|V[0-9]+|R[0-9]+) \\|.*\\| ([^|]+) \\|$\", t, re.M); assert labels == [label for label, _ in rows], (labels, rows); assert all(result.strip() != \"FAIL\" for _, result in rows); print(f\"FIRST_USE_SENTENCES={len(labels)} TABLE_ROWS={len(rows)} FAIL=0\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FIRST_USE_SENTENCES=13 TABLE_ROWS=13 FAIL=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^FIRST_USE_SENTENCES=13 TABLE_ROWS=13 FAIL=0$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "All repository tests were intentionally not run because the issued preflight rule forbade that command; the focused writer, reducer, retained-current-fixture, and restored aborted-run-fixture checks passed.",
      "needs": ""
    }
  ]
}
```

## Change

C1. A run bundle is one directory containing the records for one execution, and a raw capture is an unprocessed file written by an instrument or runtime during that execution.

C2. When the writer closes `metadata.json`, the bundle's descriptive record, it now writes `raw_sha256`, a map from every raw-capture path to a Secure Hash Algorithm 256-bit (SHA-256) fingerprint that identifies the file's exact bytes.

C3. The reducer, the program that turns captured records into reported measurements, recomputes those fingerprints before it parses any raw capture.

C4. The check uses an exact census, meaning that the recorded paths must include every raw file and no path that is absent from the directory.

C5. A changed byte, an unreadable file, a malformed map, or a path-set difference produces a structured refusal: a failed result carrying `raw_capture_digest_mismatch`; a missing required map carries `raw_capture_digest_missing`.

C6. A current-format bundle must contain the map, while an earlier-format bundle without the map remains readable; the format is identified by the exact reducer version stored in a finalized summary, and a bundle still being assembled uses the selected reducer version.

C7. The counterfactual regression, a test intended to fail if the safeguard is removed, changes one byte of `raw/powermetrics.plist` and requires the named mismatch refusal.

| Finding | Executed evidence | Decision |
|---|---|---|
| Writer coverage | Independent fingerprints for two distinct raw files | Record the complete map as a writer-owned metadata field |
| Parser ordering | A changed mock raw file that no existing parser consumes still refuses | Check fingerprints before reduction logic |
| Compatibility | Stored earlier version remains readable without a map; current unfinished bundle refuses without one | Use exact stored versions, without numeric range inference |
| Retained current fixture | Its three raw files match the newly recorded fingerprints | Add the authenticated map to that fixture |

## Verification notes

V1. The first focused run failed because the initial compatibility rule used the requested reducer version instead of the version stored in an already finalized bundle; its stable tail was `FAILED (failures=4, errors=30)`.

V2. The corrected rule reads the stored version first, which preserves earlier evidence even when it is re-reduced by current code, and the final focused run passed.

V3. A separate fixture representing an aborted run has a deliberately closed metadata shape, meaning that only its listed fields are admissible; a temporary map addition made its own tests fail, so that addition was restored byte-for-byte and its focused module then passed.

V4. All repository tests were not run because the issued preflight rule explicitly prohibited that command.

V5. The first mechanical check command over-escaped its matching expressions, and the next check searched its own command text for a failure marker; the corrected check found thirteen labeled sentences, thirteen corresponding table rows, and no failed first-use disposition.

### First-use sentence check

R1. The first-use sentence check asks whether each technical term is defined in plain language when it is first named; the table covers every changed report sentence mechanically identified by its label.

| Sentence | Terms first appearing there | Result |
|---|---|---|
| C1 | run bundle; raw capture | Defined in the sentence |
| C2 | metadata; raw_sha256 map; SHA-256 fingerprint | Defined in the sentence |
| C3 | reducer | Defined in the sentence |
| C4 | exact census | Defined in the sentence |
| C5 | structured refusal; named refusal fields | Defined or shown as literal output |
| C6 | current-format bundle; earlier-format bundle; finalized summary | Defined by direct contrast and operation |
| C7 | counterfactual regression | Defined in the sentence |
| V1 | requested version; stored version | Built in C6 |
| V2 | re-reduced | Built from the reducer action in C3 |
| V3 | closed metadata shape | Defined in the sentence |
| V4 | all repository tests | Plain language |
| V5 | matching expression; first-use disposition | Defined by the stated comparison and R1 |
| R1 | first-use sentence check | Defined in the sentence |
