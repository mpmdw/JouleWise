```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented SF-1 and N1/N2; 193 requested tests passed and all 42 mutation cuts were killed.",
  "workspace": {
    "base_requested": "6d838a10",
    "base_mode": "exact",
    "head_start": "6d838a102fa867338e91c398b8adf44cbfb09603",
    "head_end": "6d838a102fa867338e91c398b8adf44cbfb09603",
    "upstream_end": "6d838a102fa867338e91c398b8adf44cbfb09603",
    "branch": "feat/2026-09-10-epoch-continuation"
  },
  "pathspec": [
    "joulewise/calibration_epoch_continuation.py",
    "scripts/issue_epoch_continuation.py",
    "docs/contracts/epoch_continuation.md",
    "tests/test_epoch_continuation.py",
    "tests/fixtures/epoch_continuation/mutation_cuts.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_continuation tests.test_calibration_bracketing tests.test_validate_powermetrics_fiducial_derivation_only tests.test_docs_freshness tests.test_mint_policy_resolver_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 193 tests in 110.980s", "", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 193 tests in [0-9.]+s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "PYTHONPYCACHEPREFIX=/tmp/s10-round4-pycache python3 -m compileall -q joulewise scripts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["cuts=42 killed=42 survivors=0 source_sha256_restored=true"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "cuts=42 killed=42 survivors=0 source_sha256_restored=true"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
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

Added the shared [all-valid envelope check](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/calibration_epoch_continuation.py:76). Authentication and preparation now prevent unresolved rows from converting FAIL to PASS. Preparation refuses with rc 3, names unresolved slots, requests a written ruling through the desk, and writes nothing.

Retained statistics remain unchanged. Honest unresolved rows inside the envelope still prepare and authenticate; `m` excludes them. Every slot now requires exactly the documented keys, with `slots.keys` for extra or missing keys.

The [mutation table](/Users/edr/code/JouleWise-wt-s10-continuation/tests/fixtures/epoch_continuation/mutation_cuts.py:34) preserves C01–C24 and adds:

| Cuts | Single killing test |
|---|---|
| C25 | Hidden finalized-row forgery; independent N1 cut |
| C26 | Exact keys on every slot; N2 |
| C27 | Nine-row unresolved level forgery |
| C28 | Nine-row unresolved range forgery |
| C29, C31, C32, C41 | Prepare refuses unresolved level exceedance |
| C30, C33, C40, C42 | Prepare refuses unresolved range exceedance |
| C34–C35 | Unresolved row at envelope equality passes |
| C36–C37 | Envelope has no minimum count |
| C38–C39 | Combined unresolved extrema exceed range |

Changes are ready for lead review; HEAD and upstream remain unchanged.

## Verification notes

Full-suite discovery remains lead-owned under the inherited brief 168 fence. Compilation cache was redirected to `/tmp` to preserve write scope. All evidence is synthetic; no live measurement ran.