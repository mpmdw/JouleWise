```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Added the n=12 versus n=19 desk simulation; observed false-claim admission was zero in all eight cells.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "da1fa210ffe6628d63a0711c0cbf6a2d4b34f86f",
    "head_end": "da1fa210ffe6628d63a0711c0cbf6a2d4b34f86f",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-sims"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim_acc_n12.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README_acc_n12.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results_acc_n12/verdict.csv",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results_acc_n12/verdict.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim_acc_n12.py --trials 200 --screen-trials 10000",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["admission zero: YES"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "admission zero: YES"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --untracked-files=all",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "?? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README_acc_n12.md",
          "?? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results_acc_n12/verdict.csv",
          "?? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results_acc_n12/verdict.json",
          "?? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim_acc_n12.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "only four new files under 19-desk-simulations"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Zero admission is an observed result of 200 trials per cell, not a guarantee. The n=12 block-drift model refused 99.92% of later level checks.",
      "needs": "Lead review of the simulation and its yield implication."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The current production issuer still refuses n=12 and strict S=C; the simulation applies the ruled v4 changes to production numerical outputs. The production bracket projection was checked against issued r7, but no v4 artifact exists for end-to-end authentication.",
      "needs": "Re-run the issuer and bracket path after the rev 4 code and artifact are installed."
    }
  ]
}
```

## Change

Added [the simulation](/Users/edr/code/wt-278ebc9e-sims/docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim_acc_n12.py), [plain-language report](/Users/edr/code/wt-278ebc9e-sims/docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README_acc_n12.md), and saved CSV/JSON results. Existing trace-19 results were untouched.

## Verification notes

| Model | n=12 false admission | n=12 later refusal | n=19 false admission | n=19 later refusal |
|---|---:|---:|---:|---:|
| Gaussian | 0/200 | 7.78% | 0/200 | 5.68% |
| Heavy excursions | 0/200 | 4.45% | 0/200 | 3.07% |
| Serial AR(1) | 0/200 | 18.07% | 0/200 | 11.65% |
| Block drift | 0/200 | 99.92% | 0/200 | 12.73% |

**admission zero: YES.** `git status --short` shows only new files in the specified directory.

## Residual risk

The 7.7% versus 5.0% order-statistic reference assumes exchangeable observations. The serial and drift models depart from that assumption; the block-drift result is a substantial n=12 yield concern.