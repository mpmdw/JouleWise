```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Recognize versioned Claude interactive children in both handoff inventory and installer adoption while excluding background hosts and headless sessions.",
  "workspace": {
    "base_requested": "46d925c2",
    "base_mode": "exact",
    "head_start": "46d925c2baf310fb5a69042a6246bb194d271405",
    "head_end": "46d925c2baf310fb5a69042a6246bb194d271405",
    "upstream_end": null,
    "branch": "feat/2026-09-05-watchdog-host-ident"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "scripts/install_magistrate_watchdog.sh",
    "tests/test_magistrate_watchdog.py",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process_traces/2026-09-05-watchdog-host-ident/01-seat-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 11.669s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 63 tests in 2.210s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 63 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.ClaudeHostIdentificationTests.test_bench_versioned_child_is_interactive_parent_is_not",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: False is not true",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.000s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 11.639s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 66 tests in 2.012s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 66 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_magistrate_watchdog.sh",
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
      "id": "V7",
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
    }
  ],
  "flags": []
}
```

## Change

Both executable recognizers now accept `claude/versions/X.Y.Z` followed by whitespace or end of command. The watchdog's existing exclusions remain intact. The installer previously lacked role exclusions; it now excludes daemon, bg-pty-host, --bg-pty-host, bg-spare, and --bg-spare before selecting the oldest interactive ancestor, while preserving its existing headless rejection. No other matching census probe exists in these two files. Install handoff step 3 uses the exact requested wording.

The regression fixtures preserve the bench command strings supplied in the task, including their ellipsis placeholders. They verify the child is selected, its parent is excluded, plain Claude commands retain their behavior, versioned -p/--print sessions are rejected, and trailing path/version lookalikes do not match. Separate in-memory regex reverts in each implementation make the bench assertion fail. The installer tests execute its real embedded adoption block against mocked process rows and stop before the version probe.

## Verification notes

V1–V2 are sequential preflight results; V4–V5 are sequential post-change results. V3 is the intentional red test before the implementation change: the original recognizer rejected the bench child. Replay V3 against the final source passes; its recorded expected failure belongs to the pre-fix state. V5 includes both in-memory mutation checks.

Only the two permitted test modules were run, plus the isolated regression from the watchdog module. No discovery suite or agent executable was launched. Existing tests use temporary custody/plist fixtures and launchctl stubs; the real ~/night-custody, ~/Library/LaunchAgents, and launchctl were not touched. Python bytecode writes were disabled. The branch has no configured upstream; no fetch, commit, push, or merge was performed. The initial worktree was clean, and changes remain within WRITE_SCOPE. Lead-owned state, queue, and report paths outside the allowlist were preserved.

## Residual risk

This is fixture verification, not live handoff evidence. The next exact step is lead diff review followed by the authorized handoff-inventory check from the background-hosted magistrate in the canonical checkout; the live installation and final verification remain lead-owned.

