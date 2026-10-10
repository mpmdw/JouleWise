```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added the requested recovery regressions and restored the independent checkout-status assertion; both requested checks passed.",
  "workspace": {
    "base_requested": "067f4deabe45e5192553f26cf42a2ca087fb8704",
    "base_mode": "exact",
    "head_start": "067f4deabe45e5192553f26cf42a2ca087fb8704",
    "head_end": "067f4deabe45e5192553f26cf42a2ca087fb8704",
    "upstream_end": "067f4deabe45e5192553f26cf42a2ca087fb8704",
    "branch": "lane/2026-10-10-harvest-screen-sources"
  },
  "pathspec": [
    "tests/test_harvest_b5_sources.py",
    "tests/test_harvest_b5_window.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_sources",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_window.HarvestCheckoutTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": []
}
```

## Change

Added S1–S4, including independent hash mismatches and unreadable-file subcases for all three basis files. Expanded N1 to cover `None`, `{}`, `""`, `0`, and `"malformed"`. Added N4’s empty-loss assertion.

Restored the checkout test method exactly to `224a264c5faaae90cdf56118df37e773a932700b`. The round-2 `recovery_predates_erratum` edits remain unchanged. Production files are unchanged; all edits remain uncommitted.

V1 result:
```text
Ran 55 tests in 1.236s

OK
```

V2 result:
```text
Ran 4 tests in 21.824s

OK
```

`git diff --check` passed. Final `git status --short`:
```text
 M tests/test_harvest_b5_sources.py
 M tests/test_harvest_b5_window.py
```

## Verification notes

Used the authorized default-temp fallback because the sandbox write allowlist excludes the requested TMPDIR. Confirmed the default temporary directory is outside the working tree. Ran the requested checks sequentially; no discovery, sharding, or mutation runs were performed.