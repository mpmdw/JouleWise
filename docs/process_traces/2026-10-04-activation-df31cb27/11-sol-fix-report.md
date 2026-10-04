```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Fix verified: 187 tests passed, one skipped, and b3w1 bracket replay passed; the required commit is blocked by the filesystem sandbox.",
  "workspace": {
    "base_requested": "a6c7f9cf",
    "base_mode": "exact",
    "head_start": "a6c7f9cf890428741c48233cd0047f70e7cb5f8f",
    "head_end": "a6c7f9cf890428741c48233cd0047f70e7cb5f8f",
    "upstream_end": "3b57e9c0b172aa1e7a44022e45dfd06e6da3fbc6",
    "branch": "fix/2026-10-04-g2a-b3w1-bracket-baseline"
  },
  "pathspec": [
    "scripts/harvest_g2a_window.py",
    "tests/test_harvest_g2a_window.py",
    "tests/fixtures/custody_read_replay_allowlist.json"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_harvest_g2a_window tests.test_calibration_bracketing tests.test_generate_g2a_probe_inputs tests.test_custody_mode_inventory",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 188 tests in 75.176s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 188 tests in [0-9.]+s[\\s\\S]*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/g2a-b3w1-replay-df31/replay.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["status=passed", "reason_codes=()"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "status=passed\\s+reason_codes=\\(\\)"
      }
    },
    {
      "id": "V3",
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
      "id": "V4",
      "kind": "other",
      "cmd": "git add scripts/harvest_g2a_window.py tests/test_harvest_g2a_window.py tests/fixtures/custody_read_replay_allowlist.json",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise-wt-86cb-rec/.git/worktrees/JouleWise-wt-df31-fix/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The linked Git metadata directory is outside the writable roots. Staging failed; no commit was created.",
      "needs": "Lead must stage the three pathspec files and commit them on the existing branch."
    }
  ]
}
```

## Change

Preserved seed and terminal-head custody authentication. Added the acceptance-cutoff bracket view, with unfiltered snapshot refusals retained as RECOVER causes.

Acceptance SHA uses the generator’s `_sha256_path`; SHA or ID mismatch now refuses with `bracket_acceptance_plan_mismatch`.

No out-of-scope tooling defect found. The prefix check at `joulewise/calibration_bracketing.py:2011` permits observations appended after the cutoff.

## Verification notes

The existing skip requires unavailable lead-reviewed D-079 import inputs.

**Commit SHA: none.** The sandbox blocked Git’s `index.lock` outside the writable roots. The lead’s remaining step is:

```sh
git add scripts/harvest_g2a_window.py tests/test_harvest_g2a_window.py tests/fixtures/custody_read_replay_allowlist.json
git commit -m "Fix G2-a harvest bracket acceptance baseline"
```