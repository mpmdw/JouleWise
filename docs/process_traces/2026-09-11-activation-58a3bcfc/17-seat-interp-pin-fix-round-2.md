```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "All six assigned findings fixed and verification passed; sandbox blocked staging, so commits remain outstanding.",
  "workspace": {
    "base_requested": "1c66b981",
    "base_mode": "exact",
    "head_start": "1c66b981d34cf813078967dc2cbbc64d56d95025",
    "head_end": "1c66b981d34cf813078967dc2cbbc64d56d95025",
    "upstream_end": "1c66b981d34cf813078967dc2cbbc64d56d95025",
    "branch": "fix/2026-09-11-night-interpreter-pin"
  },
  "pathspec": [
    "scripts/install_night_agent.sh",
    "scripts/run_night.py",
    "tests/test_install_night_agent.py",
    "tests/test_run_night.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_install_night_agent tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 106 tests in 14.414s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 106 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "python3 -m compileall -q scripts joulewise",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_night_agent.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "git add scripts/install_night_agent.sh scripts/run_night.py tests/test_install_night_agent.py tests/test_run_night.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-interp-pin/index.lock': Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "COMMIT_BLOCKED",
      "kind": "environment",
      "level": "blocking",
      "text": "Linked-worktree Git metadata is outside writable sandbox roots. Staging failed; no commits were created and nothing was pushed.",
      "needs": "Lead reviews and commits the six modified files on the current branch."
    }
  ]
}
```

## Change

- **F2 fixed:** recorded the 09-11 crash, dead-man refusal, harvest, item 5 MET/item 6 NOT MET, uninstall and retirement. Current sections say nothing is armed and point to record 13 without inventing pins.
- **F4 fixed:** uninstall ignores `--python` with the exact stderr notice; regression covers a missing interpreter.
- **F5 fixed:** both docs bound preflight coverage; JSON lists the driver and its five direct module-scope project imports.
- **F6 fixed:** glossed `--render-only` at first use.
- **F7 fixed:** explained `--python` before the arm block; added driver preflight to §Terms and the glossary table.
- **F8 fixed:** replaced “compatible” with absolute-path, minimum-version and successful-preflight requirements.

Commits: none; staging was blocked.

## Verification notes

All requested checks passed. Canonical-suite replay and final verification remain lead-owned. Next step: review the diff and commit code/tests and documentation separately.