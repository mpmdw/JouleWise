```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented six ordinary shards per interpreter and refreshed all 230 module timings; preserved existing coverage and recorded six-run measurements.",
  "workspace": {
    "base_requested": "f4d55d664a8df7937a52f807066b42ee01db6a12",
    "base_mode": "exact",
    "head_start": "f4d55d664a8df7937a52f807066b42ee01db6a12",
    "head_end": "f4d55d664a8df7937a52f807066b42ee01db6a12",
    "upstream_end": "ef05a0fc06ba8817ce24fbaa526f2f2415509b43",
    "branch": "chore/2026-09-15-ci-trim-2"
  },
  "pathspec": [
    ".github/workflows/ci.yml",
    "scripts/test_timings.json",
    "docs/process_traces/2026-09-15-interactive-b0ae8462/10-ci-trim-2-astra-plan.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\np=Path('docs/process_traces/2026-09-15-interactive-b0ae8462/10-ci-trim-2-astra-plan.md').read_text()\nfor name in ('yaml', 'partition', 'inline'):\n marker=f'<!-- CHECK:{name} -->\\n```sh\\n'\n command=p.split(marker,1)[1].split('\\n```',1)[0]\n subprocess.run(command,shell=True,check=True)\nprint('CHEAP VERIFICATION PASS; YAML, coverage, workflow dry execution; no test bodies run')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CHEAP VERIFICATION PASS; YAML, coverage, workflow dry execution; no test bodies run"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CHEAP VERIFICATION PASS"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
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
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Hosted CI has not run on this patch. Local suites were prohibited. Scope checker returned SCOPE_OK; no commits made.",
      "needs": "Lead reviews, commits/pushes through its authorized route, and verifies hosted results, test census and wall clock."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "gh could not connect; the installed GitHub connector supplied run/job logs. Branch-protection lookup returned 403. All existing job IDs and named steps remain.",
      "needs": "Lead checks current branch protection with sufficient read permission."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Another actor advanced origin/main during inspection. Worktree HEAD stayed exactly at BASE_HEAD; no unowned dirty paths appeared.",
      "needs": "Lead handles integration with newer main if required."
    }
  ]
}
```

## Change

Implemented **6×2 shards** and refreshed timings from six hosted runs. Both interpreters, exclusive jobs, existing splits, setup steps and coverage remain.

The latest three green code-changing push heads measured:

| Run | Wall min | Critical job | Start delay + execution min |
|---|---:|---|---:|
| 35051177531 | 24.67 | test (3.11, 2) | 0.07 + 24.60 |
| 35034962874 | 25.62 | test (3.11, 4) | 2.60 + 23.00 |
| 35006580578 | 53.33 | test (3.14, 2) | 32.37 + 20.97 |

The newest full-matrix pushes measured **39.82 / 32.57 / 32.05 minutes**. Queueing materially determines completion; one run ended on an 11-second wheel smoke after an 18-minute wait.

[Full measurements, arithmetic and replay commands](/Users/edr/code/JouleWise-wt-ci-trim/docs/process_traces/2026-09-15-interactive-b0ae8462/10-ci-trim-2-astra-plan.md) include every job and module.

New ordinary-shard estimate: **13.83 minutes**. Expected workflow execution with available runners: **19–20 minutes**, bounded by calibration exits. Eight shards would not lower that floor and would exceed observed 20-job occupancy. Queue delays remain additional.

Interpreter dedupe remains a proposal: approximately **95 runner-minutes saved**, but full Python 3.14 behavioral coverage would be lost. Calibration splitting remains deferred because it duplicates the shared witness sweep.

## Verification notes

Help, YAML parsing, partition coverage and workflow dry checks passed. Every split test ID remains assigned exactly once.

The brief’s changes detector was deliberately removed before merge. The actual installer module measures seconds, not ten minutes.

## Residual risk

Only hosted CI can establish actual speed, scheduling delays and absence of order/cache regressions. No full local suite or CI run was started.