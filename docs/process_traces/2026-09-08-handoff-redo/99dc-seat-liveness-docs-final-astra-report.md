```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Fixed exactly B1, B2, and A1; freshness tests passed; no commit.",
  "workspace": {
    "base_requested": "5cf1660f",
    "base_mode": "exact",
    "head_start": "5cf1660f378a0c0934216247d27ecf2519878305",
    "head_end": "5cf1660f378a0c0934216247d27ecf2519878305",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "docs/2026-09-08-window-liveness-docs"
  },
  "pathspec": ["docs/contracts/window_liveness.md"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness > /tmp/WINDOW-LIVENESS-DOCS-01-final-freshness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 0.905s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK\\s*$"}
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

Each requested edit, before → after:

| Finding/site | Before | After |
|---|---|---|
| B1 / C5 | “The census refuses any start object…” | “When neither exit check accepts an exit, the census refuses any start object…” |
| B2 / P1 | Status `:60–:92`; Git `:99–:106` | Status `:60–:94`; staging/change check `:101–:106`; commit/push `:107–:108` |
| B2 / C2 | JSON `run_night.py:105–106` | `:102–103` |
| B2 / C4 | Exclusive write/fsync `:119–129` | `:116–125` |
| B2 / C5 | Null assignment `:381` | `:382` |
| B2 / T7 | Local-only branch `:94–97` | `:96–99` |
| A1 / courier-delivery | Undefined at first use | Added “the program that emails the night's result” |
| A1 / collector | Undefined at first use | Added “the launchd-run measurement collection program” |
| A1 / watchdog | Undefined at first use | Added “the agent-monitoring LaunchAgent that evaluates arming ticks” |

All corrected pins were verified against code before editing. Only the authorized file changed; HEAD remains unchanged. Ready for lead review.