```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented and verified the hash-pinned DG-071/DG-075 statistics producer and focused refusal tests.",
  "workspace": {
    "base_requested": "a63d45bdfb0f6076b183495590b014725d33c8a8",
    "base_mode": "exact",
    "head_start": "a63d45bdfb0f6076b183495590b014725d33c8a8",
    "head_end": "a63d45bdfb0f6076b183495590b014725d33c8a8",
    "upstream_end": null,
    "branch": "feat/2026-09-02-paper-d"
  },
  "pathspec": [
    "scripts/issue_dg071_dg075_statistics.py",
    "tests/test_issue_dg071_dg075_statistics.py"
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
      "cmd": "TMPDIR=<scratchpad>/paper-seat-d /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".......", "Ran 7 tests in 0.031s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 7 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "TMPDIR=<scratchpad>/paper-seat-d /Users/edr/code/JouleWise/.venv/bin/python scripts/issue_dg071_dg075_statistics.py --out <scratchpad>/paper-seat-d/dg071-dg075-statistics.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DG-071 median_ms=120.918512 iqr_ms=5.975008", "DG-075 median_ms=120.922327 iqr_ms=5.894899"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DG-071 median_ms=120\\.918512 iqr_ms=5\\.975008\\nDG-075 median_ms=120\\.922327 iqr_ms=5\\.894899"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "shasum -a 256 scripts/issue_dg071_dg075_statistics.py <scratchpad>/paper-seat-d/dg071-dg075-statistics.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["script 048d8bb20fcdea9ecd61d4c1bce8c76882c540dc5c7e80391a4f075f5e231ce2", "artifact bdd5ec88ac8ddce6fae6373ecf35f422227473de1da9af54d6ddb2616e93bc1a"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "048d8bb2.*\\nbdd5ec88.*"
      }
    }
  ],
  "flags": []
}
```

## Change

Implemented the ratified definitions:

> “DG-071 (record interval width): median with IQR of `interval_end_s − interval_start_s` over every retained record of the cited `p2015-df-ph-decode-abs-r03` bundle, with the exact file path and SHA-256 recorded by the fill's ratification artifact.”

> “DG-075 (record spacing): median with IQR of differences between consecutive unique `timestamp_s` values over the same bundle.”

Real issuance:

- DG-071: median `0.12091851234436035 s`; IQR `0.005975008010864258 s` — rendered `120.918512 ms`, `5.975008 ms`.
- DG-075: median `0.12092232704162598 s`; IQR `0.005894899368286133 s` — rendered `120.922327 ms`, `5.894899 ms`.
- Counts: 1,218 records; 406 distinct timestamps; 812 duplicates dropped; 405 spacing differences.
- Artifact SHA-256: `bdd5ec88ac8ddce6fae6373ecf35f422227473de1da9af54d6ddb2616e93bc1a`.

## Verification notes

The first test pass exposed an invalid strict shifted-zip; corrected before the real run. Final tail: `Ran 7 tests in 0.031s` / `OK`.

No `NEEDS_RULING`; R-167-1 resolves all conventions.