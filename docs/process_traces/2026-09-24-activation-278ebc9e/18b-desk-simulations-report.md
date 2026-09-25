```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Completed the scoped R-Q4(a) desk simulation and proposed an equivalence-night rule; files are uncommitted for the magistrate.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "21d045ad60aa926756e45c542cf6491dd143c472",
    "head_end": "21d045ad60aa926756e45c542cf6491dd143c472",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-sims"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results/metadata.json",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results/floor_claim_cells.csv",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results/floor_claim_cells.json",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results/equivalence_cells.csv",
    "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/results/equivalence_cells.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 sim.py --smoke",
      "cwd": "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "n=10 point-only median_F=2.571 sigma; SD(mean)=0.316 sigma",
          "w/sigma=0.50 P(R>=2)=0.000 median_F=3.767",
          "w/sigma=0.75 P(R>=2)=0.100 median_F=4.308",
          "w/sigma=1.00 P(R>=2)=0.412 median_F=5.007",
          "w/sigma=1.50 P(R>=2)=0.953 median_F=6.254",
          "w/sigma=2.00 P(R>=2)=1.000 median_F=7.537"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "w/sigma=2\\.00 P\\(R>=2\\)=1\\.000"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "time python3 sim.py --trials 30",
      "cwd": "docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "floor_claim_cells=144 trials=30",
          "equivalence_cells=768 trials=600",
          "results: floor_claim_cells.csv/.json equivalence_cells.csv/.json metadata.json",
          "python3 sim.py --trials 30  71.46s user 0.15s system 99% cpu 1:11.68 total"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "equivalence_cells=768 trials=600"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "?? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\?\\? docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 - <<'PY' ... CSV/JSON row, key, and selected false-alarm checks ... PY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "floor_claim_cells 144 CSV/JSON rows and keys OK",
          "equivalence_cells 768 CSV/JSON rows and keys OK",
          "selected maximum false alarm 0.013333333333333334"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "selected maximum false alarm 0\\.013333333333333334"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The synthetic equivalence replay calls the real numerical verdict but does not exercise ledger authentication or observed capture loss.",
      "needs": "Authenticate and register the eventual rule through M1 before night use."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The proposed rule detects only 7–12% of fourfold variance changes and its 90% interval undercovers under independent night shocks.",
      "needs": "Review this tradeoff at the later registration gate."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The worktree is intentionally uncommitted because this seat cannot write .git.",
      "needs": "Magistrate commits the process trace before claim-bearing use."
    }
  ]
}
```

## Change

The [simulation script](/Users/edr/code/wt-278ebc9e-sims/docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim.py) calls the production floor, ratio, estimator, Holm adjustment, claims admission, and equivalence-night numerical verdict. Fixed seeds produced 144 floor/claim cells and 768 equivalence cells. The [README](/Users/edr/code/wt-278ebc9e-sims/docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md) defines the models, rates, grid, and results.

The seed-278 dominance replay gives **0.000 / 0.100 / 0.412 / 0.953 / 1.000** across the five ruled width ratios, within Monte Carlo error of **0.00 / 0.11 / 0.41 / 0.94 / 1.00**. The twelve-component verdict was counted from shared trials.

| Rule and declared state | False admission | Missed effect or no-change false alarm | Coverage | Refusal |
|---|---:|---:|---:|---:|
| D-165, narrow w/σ=0.5 versus wide w/σ=2 *diagnostic proxies* | 0 joint passes at narrow width | 4.7–45.0% joint failures at wide width, by model | No ratio interval | 0 in simulated cells |
| Directional claim, δ=0 / 2σ / 5σ | 0 at δ=0 | 100% at 2σ; 84% at 5σ | 95% interval: 55.6–56.5%; expanded decision interval: 94.8–95.1%; guarded floor prediction: 99.9% | 100% at 0 and 2σ; 84% at 5σ |
| Diagnostic `tost_v1`, margin 4σ | 0 equivalence admissions at δ=5σ | 94.8% fail to admit equivalence at δ=0 | Same estimator intervals as above | 94.8% at δ=0 |
| Current equivalence rule, old n=17 and m=12 | 0.4% PASS after +5σ; 3.8% PASS after ×4 variance | 58.0% FAIL under no change | No interval | 0 at m=12; 100% at m=4 |
| Proposed rule, old n=17 and m=12 | 0.9% PASS after +5σ; **90.8% PASS after ×4 variance** | 0.5% FAIL under no change | 90% mean interval: 52.5% under no change | 0 at m=12; 100% below m=12 |

The [replacement proposal](/Users/edr/code/wt-278ebc9e-sims/docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md) sets **TOST margin 3.5σ, one-sided α=0.05, variance-ratio bound 20, old n≥17, and retained m=12**. Using the current 17-member corpus standard deviation gives a proposed margin of **0.008612996726931225 s**. Across the four models at old n=17/m=12, no-change false alarm was **0.2–1.3%**; detection of the named **+5σ shift** was **97.8–99.8%**. It remains **PROPOSED**, with registration and production installation reserved for M1.

## Verification notes

V1–V3 tails are in the envelope and the README. The full run took **1:11.68**; CSV and JSON row counts and keys matched. The canonical repository suite was not run for this scoped simulation-only trace.

## Residual risk

The variance-ratio bound needed to meet the simulated no-change target has little power against a fourfold variance increase. The ordinary TOST interval also undercovers when nights have separate shared shocks. **No NEEDS_RULING blocks this scoped desk deliverable**; those limitations require an explicit decision at the later registration gate. The magistrate must commit these untracked files before any claim-bearing use.