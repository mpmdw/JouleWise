```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented scoped handoff census, accurate signal outcomes, daemon retirement gates, and dead-lock resumed-twin refusal; all 90 scoped tests pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "head_end": "d8ad6c15d48a41ad9e562ce9845bf8fb874826bb",
    "upstream_end": null,
    "branch": "feat/2026-09-08-watchdog-census-daemon"
  },
  "pathspec": [
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "scripts/install_magistrate_watchdog.sh",
    "scripts/magistrate_watchdog.py",
    "tests/test_install_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog_cli.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog > /private/tmp/watchdog-census-01-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 90 tests in 19.340s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "zsh -n -o NO_BG_NICE /private/tmp/watchdog-census-01-reaper.zsh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "python3 -c 'from pathlib import Path; compile(Path(\"/private/tmp/watchdog-census-01-reaper.py\").read_text(), \"documented-reaper\", \"exec\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/watchdog-census-01-counterfactuals.py > /private/tmp/watchdog-census-01-counterfactuals.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COUNTERFACTUAL_REPLAY_OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "COUNTERFACTUAL_REPLAY_OK"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "zsh -n scripts/install_magistrate_watchdog.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox denied live ps. Classifier evidence came from the saved receipt and supplied command shapes. Custody now records PID 84232 rather than the brief's stale lock owner.",
      "needs": "Lead must inspect fresh processes and perform the authorized live handoff verification."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Existing locks lack Claude session IDs, so any interactive --resume with --reply-on-resume is conservatively treated as a potential resumed twin.",
      "needs": "Explicitly resolve or adopt such candidates before handoff."
    }
  ]
}
```

## Change

The queue records:

> “`verdict: fail` with `survivors: []` because `production_census()` counts every `claude` process on the machine”

and:

> “resumed the same session (`claude --resume`, pid 71607) five minutes later, outside the watchdog's lock.”

Implemented the following, with regressions in the three scoped modules:

| Change | Counterfactual covered |
|---|---|
| Separate handoff census | Unrelated Claude remains; owned or lock pairs survive, disappear, or undergo PID reuse. |
| Reaper outcomes and receipt | Owner lives before TERM, exits during the wait, races a signal, requires KILL, or remains defunct. |
| Inventory and CLI classification | Nonorphan daemon/spare/host or detached resumed twin appears; adoption requires its exact start token. |
| Installer retirement preflight | Live daemon machinery remains before installation writes. |
| Dead-lock protection and documented reconciliation | Resumed twin survives repeated ticks or a plan hold; operator encounters a live or dead lock owner. |

Night-time `production_census()` and `agent_census` remain machine-wide. The documentation retains the reaper extraction contract and supplies explicit retirement and reconciliation commands.

No design disagreement with §2. No open implementation questions.

## Verification notes

The initial run exposed an existing regex-count assertion; it was updated to cover both installer checks while retaining its mutation test. Final acceptance: **90 tests, rc 0**, recorded in [the acceptance log](/private/tmp/watchdog-census-01-acceptance.log).

An isolated replay against the starting commit reproduced all four original failures. The repository-wide suite was not run.

## Residual risk

No live processes or custody files were modified, and nothing was installed or committed. Fresh process inspection was sandbox-blocked. The next step is lead diff review followed by the authorized live retirement and handoff verification.