```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added a committed window mutant regression using the real prepare path.",
  "workspace": {
    "base_requested": "bd80d169",
    "base_mode": "exact",
    "head_start": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "head_end": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "upstream_end": "bd80d16905757ab03f7e166e42d93a0d6ac888bb",
    "branch": "test/2026-09-24-a295-window-mutant"
  },
  "pathspec": ["tests/test_night_kinds.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 19 tests in 85.401s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 19 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff bd80d169 --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests/test_night_kinds.py | 45 +++++++++++++++++++++++++++++++++++++--------", "1 file changed, 37 insertions(+), 8 deletions(-)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_night_kinds.py.*\\n 1 file changed"
      }
    }
  ],
  "flags": []
}
```

## Change

- **C1:** [test_committed_window_mutant_refused_by_real_prepare](/Users/edr/code/wt-a65fb4fa-a295/tests/test_night_kinds.py:397) commits the 8999-second row, updates the bare remote’s `main`, runs real `prepare`, and asserts the exact recorded `Refused` message.
- **C2:** The same test uses the fixture helper with the unmodified 9000-second row and confirms that `prepare` succeeds.
- **C3:** Removing the guard at [quiet_predicate_campaign.py:161](/Users/edr/code/wt-a65fb4fa-a295/joulewise/quiet_predicate_campaign.py:161) in a disposable clone made the test fail: `AssertionError: Refused not raised`. The production checkout was untouched.

## Verification notes

The required two-module suite passed. `git diff bd80d169 --stat` lists only the allowed test file.

The magistrate should double-check that the fixture commit is the head supplied to `prepare` and that the disposable-clone guard deletion is sufficient mutation evidence.