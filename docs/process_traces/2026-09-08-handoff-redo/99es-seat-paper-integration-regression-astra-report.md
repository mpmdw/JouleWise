```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added one regression with two DS-09-derived malformed-history refusal subcases; all 69 tests pass.",
  "workspace": {
    "base_requested": "21331ac9",
    "base_mode": "exact",
    "head_start": "21331ac971580f5e07cad372888ff3d61cc28500",
    "head_end": "21331ac971580f5e07cad372888ff3d61cc28500",
    "upstream_end": "21331ac971580f5e07cad372888ff3d61cc28500",
    "branch": "int/2026-09-08-paper-s2-s3-s7"
  },
  "pathspec": ["tests/test_paper_round7_artifacts.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "JOULEWISE_BACKUP_ROOTS= R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 69 tests in 623.704s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Added one regression using the real DS-09 row. Both counterfactuals executed against the unchanged checker raised `RegistryError`:

- Replace the dated marker with `RETIRED_FALLBACK (undated)`.
- Append a second dated note as an eighth column.

Both require the “exactly one dated retirement note” diagnostic. No commit was made.

## Verification notes

An optional process-status inspection was sandbox-blocked. The named module subsequently completed successfully.