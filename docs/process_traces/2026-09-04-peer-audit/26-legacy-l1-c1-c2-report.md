```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Landed the C1 RPT-001 void-disposition adjudication and C2 producer-owned artifact-manifest link with all permitted checks green.",
  "workspace": {
    "base_requested": "12c61893",
    "base_mode": "exact",
    "head_start": "12c61893b58e5c7feca36f33b8ae98d695fb35bb",
    "head_end": "12c61893b58e5c7feca36f33b8ae98d695fb35bb",
    "upstream_end": "12c61893b58e5c7feca36f33b8ae98d695fb35bb",
    "branch": "feat/2026-09-04-legacy-l1"
  },
  "pathspec": [
    "docs/specs/c027/ADJUDICATION.md",
    "scripts/build_capstone.py",
    "docs/report_src/generated/rpt001_vertical_slice.md",
    "tests/test_rpt001_report_slice.py",
    "docs/process_traces/2026-09-04-peer-audit/26-legacy-l1-c1-c2-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build_capstone.py --profile rpt001 --offline --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "build_capstone: check OK (no drift)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "build_capstone: check OK \\(no drift\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_build_capstone",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..",
          "----------------------------------------------------------------------",
          "Ran 2 tests in 0.000s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_rpt001_report_slice",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".........s..s......",
          "----------------------------------------------------------------------",
          "Ran 19 tests in 12.100s",
          "",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 19 tests in .*s\\n\\nOK \\(skipped=2\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_claims_index_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..............................",
          "----------------------------------------------------------------------",
          "Ran 30 tests in 8.163s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests in .*s\\n\\nOK"
      }
    }
  ],
  "flags": []
}
```

## Change

Added the single RPT-001 adjudication row required by C1, including the legal void values, the intentional exact-grandfather-row Markdown sanitization, and the unchanged mechanical `PROJECTION_DRIFT` invariant. Restored C2's manifest link in the page producer, refreshed the generated page to match, and changed the focused page assertion accordingly. C3 remains parked and untouched.

## Verification notes

Per the runner preflight, only the three named unittest modules were run, serially; the discovery suite was not run.
