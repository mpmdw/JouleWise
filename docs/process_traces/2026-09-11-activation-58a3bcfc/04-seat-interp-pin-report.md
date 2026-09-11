```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented interpreter pinning, import preflight, regressions, and docs; all requested checks pass, but sandbox permissions prevent committing.",
  "workspace": {
    "base_requested": "1dddcfea",
    "base_mode": "exact",
    "head_start": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "head_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "upstream_end": "1dddcfea573d85ee8facebc2b50dac412cb3b69f",
    "branch": "fix/2026-09-11-night-interpreter-pin"
  },
  "pathspec": [
    "configs/launchd/com.joulewise.night.plist.template",
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
      "cmd": "python3 -m unittest tests.test_install_night_agent tests.test_run_night -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 105 tests in 14.345s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 105 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "build",
      "cmd": "python3 -m compileall -q scripts joulewise",
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
      "id": "V3",
      "kind": "smoke",
      "cmd": "scripts/install_night_agent.sh --render-only /tmp/interp-pin-render --plan /private/tmp/interp-pin-fixture-31pn32dg/night_plan.json --hour 2 --minute 56 --python \"$(command -v python3)\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"preflight\": \"ok\", \"python\": \"/opt/homebrew/opt/python@3.14/bin/python3.14\", \"version\": \"3.14.7\", \"modules\": [\"joulewise.arm_readiness\", \"joulewise.arm_readiness_evidence_t0\", \"joulewise.t0_rehearsal\", \"joulewise.night_gate\", \"joulewise.measurement_liveness\"]}",
          "validated pins: repo_head=1dddcfea573d85ee8facebc2b50dac412cb3b69f measurement_root=/Users/edr/code/JouleWise-wt-interp-pin measurement_head=1dddcfea573d85ee8facebc2b50dac412cb3b69f"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"preflight\": \"ok\"[\\s\\S]*validated pins:"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import json, plistlib; from pathlib import Path; [print(p.name + \": \" + json.dumps(plistlib.loads(p.read_bytes())[\"ProgramArguments\"])) for p in sorted(Path(\"/tmp/interp-pin-render\").glob(\"*.plist\"))]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "com.joulewise.night.deadman.plist: [\"/opt/homebrew/bin/python3\", \"/Users/edr/code/JouleWise-wt-interp-pin/scripts/run_night.py\", \"dead-man\", \"--plan\", \"/private/tmp/interp-pin-fixture-31pn32dg/night_plan.json\", \"--courier-bin\", \"/Users/edr/.local/share/claude/versions/2.1.268\"]",
          "com.joulewise.night.plist: [\"/opt/homebrew/bin/python3\", \"/Users/edr/code/JouleWise-wt-interp-pin/scripts/run_night.py\", \"run\", \"--plan\", \"/private/tmp/interp-pin-fixture-31pn32dg/night_plan.json\", \"--courier-bin\", \"/Users/edr/.local/share/claude/versions/2.1.268\"]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ProgramArguments|/opt/homebrew/bin/python3"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "env -i PATH=/usr/bin:/bin /usr/bin/env python3 --version",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Python 3.9.6"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Python 3\\.9\\.6"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "/bin/zsh -n scripts/install_night_agent.sh && git diff --check",
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
      "kind": "other",
      "cmd": "git add configs/launchd/com.joulewise.night.plist.template scripts/install_night_agent.sh scripts/run_night.py tests/test_install_night_agent.py tests/test_run_night.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-interp-pin/index.lock': Operation not permitted"
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
      "text": "Git staging cannot write the linked worktree metadata outside the writable sandbox. No commits were created; all seven files remain unstaged. No bypass was attempted.",
      "needs": "Lead must stage and commit the implementation/tests and documentation on this branch."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical suite and final acceptance review remain lead-owned, as instructed. No night was armed and no live launchctl invocation occurred.",
      "needs": "Lead performs final diff review and the sharded canonical replay."
    }
  ]
}
```

## Change

The installer validates one absolute interpreter, runs import preflight in the job’s minimal environment, and renders that interpreter into both plists. Uninstall works without a venv or driver modules. The chain interpreter remains unchanged.

Hoisted lazy dependencies: `arm_readiness`, `arm_readiness_evidence_t0`, and `t0_rehearsal`. Template bytes otherwise remain identical.

## Verification notes

Commits: **none**, because staging was denied by filesystem permissions. No scope expansion or contract ruling is required.

The rendered interpreter and preflight’s reported executable resolve to the same file. Next: lead commits the changes, reviews the diff, and runs the sharded replay.