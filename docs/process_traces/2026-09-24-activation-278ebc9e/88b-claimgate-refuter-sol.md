```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "CG-3 admits false equivalence at the registered margin; CG-2 conflicts with the current evaluator, and several implementation rules need tightening.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "4b7f5a0498b8ab324f6674e1274192ee691f7dfd",
    "head_end": "4b7f5a0498b8ab324f6674e1274192ee691f7dfd",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "summary": "CG-3 falsely passes equivalence at its location margin."},
      {"id": "F2", "severity": "blocker", "summary": "CG-2's permitted margins are refused by the current claims evaluator."},
      {"id": "F3", "severity": "blocker", "summary": "A second claim shape can be registered after seeing the same contrast's data."},
      {"id": "F4", "severity": "should_fix", "summary": "CG-3 can PASS a night whose every value exceeds the old level screen."},
      {"id": "F5", "severity": "should_fix", "summary": "CG-1 gives the wrong scaling for stochastic variance fields."},
      {"id": "F6", "severity": "should_fix", "summary": "CG-1's equal-envelope estimator need not estimate its stated block-population mean."},
      {"id": "F7", "severity": "should_fix", "summary": "CG-4 omits required floor and interval schema paths."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgref/probe.py 1000 500 2000 > /tmp/278ebc9e/cgref/probe.out",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["shared_local times16 _locpass=0.448 _spreadfail=0.962 _fail=0.968"]},
      "expected": {"exit_code": 0, "tail_regex": "shared_local times16 .*_fail=0\\.968"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgref/probe_m8.py 200 300 2000 > /tmp/278ebc9e/cgref/probe_m8.out",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["shared_local times16 _locpass=0.373 _spreadfail=0.887 _fail=0.927"]},
      "expected": {"exit_code": 0, "tail_regex": "shared_local times16 .*_fail=0\\.927"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/278ebc9e/cgref/joint_boundary.py > /tmp/278ebc9e/cgref/joint_boundary.out",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["shared_local fixed-old boundary location=0.212 spread_pass=1.000 joint_false_PASS=0.212"]},
      "expected": {"exit_code": 0, "tail_regex": "shared_local fixed-old boundary .*joint_false_PASS=0\\.212"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Simulation rates are conditional on the four specified generators and the stated envelope/window models; no live measurement was run.",
      "needs": ""
    }
  ]
}
```

## Findings

All four named CG-4 locations exist: `estimators.py`, `claims.py:361–363`, `epoch_equivalence_check.py:127,480–536`, and `analysis_plans.md:29`. The conflicts are in the rules those locations must implement and in additional code paths.

| ID | Severity | Finding and exact replacement text |
|---|---|---|
| F1 | **BLOCKER** | **CG-3 location test understates one-night uncertainty.** With the actual r7 old corpus fixed and a true shift exactly equal to its 8.613 ms margin, the *full location-plus-spread rule* falsely PASSed 17.0–22.4% across the four generators. The new night's shared window shift is absent from `s_new²/m`. Replace CG-3 location text with: **“Do not activate the prospective PASS rule until its location statistic accounts for a new night as one window-level draw against the ten old windows. Freeze the statistic, margin, and minimum m before capture; demonstrate ≤5% no-change false FAIL and ≤5% false PASS at the equivalence-margin boundary under every registered generator.”** |
| F2 | **BLOCKER** | **CG-2 conflicts with [claims.py](/Users/edr/code/wt-278ebc9e-cg-sol/joulewise/analysis_engine/claims.py:346).** CG-2 allows `Δ = F_est + B`; at equality, its strict decision-interval containment cannot pass. More broadly, the existing `margin <= floor` check refuses an effective margin `Δ − F_est` whenever `Δ ≤ 2F_est`. An executed example with `F_est=1`, `B=0.5`, `Δ=1.5`, and a narrow interval about zero returned `not_resolvable: equivalence_margin_not_above_floor`. Replace CG-2 implementation text with: **“Register Δ > F_est + B. The equivalence path uses Δ_eff = Δ − F_est for both its 90% decision interval and Holm-adjusted TOST. Refactor `claims.py:346–363` so the legacy `margin > floor` check is not reapplied to Δ_eff; validate the registered Δ and floor separately.”** |
| F3 | **BLOCKER** | **CG-2 permits selection after outcomes.** “A second shape on the same contrast is a new registration after the first is issued” does not require new observations. Replace that sentence with: **“One observed data set has one prospectively frozen confirmatory claim shape. A shape selected after any of those outcomes is exploratory on that data. A new confirmatory shape requires a newly frozen registration, independent subsequently collected observations, and multiplicity accounting for the selection opportunity.”** |
| F4 | **MATERIAL** | **CG-3 removes an existing level gate without proving an upstream gate covers it.** A constructed 12-value night with every value above r7’s 32.89849 ms level screen satisfies CG-3’s location test (`8.073 < 8.613 ms`) and spread test (`p=1.0`). Replace “Diagnostics printed, non-gating: count … above the level screen” with: **“A retained value above the operative level screen prevents PASS unless the verdict records an authenticated, earlier admission gate that already rejected such a value; otherwise report the level comparison as a gating check.”** This concerns [epoch_equivalence_check.py](/Users/edr/code/wt-278ebc9e-cg-sol/scripts/epoch_equivalence_check.py:509), whose current rule checks the level. |
| F5 | **MATERIAL** | **CG-1 says each stochastic “term” is divided by `√n_e`, but [StochasticVarianceTerm](/Users/edr/code/wt-278ebc9e-cg-sol/joulewise/analysis_engine/estimators.py:59) stores variances and covariance, not standard deviations.** Replace the aggregation sentence with: **“For independent block-level stochastic contributions within envelope e, divide each variance and covariance field by n_e; divide a standard deviation by √n_e only before squaring it. For contributions shared or correlated across blocks, propagate the registered covariance matrix of the envelope mean; refuse an unknown correlation structure.”** |
| F6 | **MATERIAL** | **CG-1 names a block-population estimand but takes an unweighted mean of envelope means.** Unequal `n_e` change the target: one envelope of 1 block at 10 and four envelopes of 10 blocks at 0 give an envelope mean of 2, versus a block mean of 10/41. Replace the estimand/replicate sentence with: **“The primary estimand is the equally weighted mean contrast over registered quiet-window envelopes; each envelope mean is one replicate. If the target is instead the block-population mean, pre-register equal block counts per envelope or a weighted estimator and its matching uncertainty rule.”** |
| F7 | **MATERIAL** | **CG-4’s named code sites do not cover the production path.** [inputs.py](/Users/edr/code/wt-278ebc9e-cg-sol/joulewise/analysis_engine/inputs.py:385) resolves floors, [registry.py](/Users/edr/code/wt-278ebc9e-cg-sol/joulewise/analysis_engine/registry.py:462) requires the v1 floor selector, [the engine](/Users/edr/code/wt-278ebc9e-cg-sol/joulewise/analysis_engine/__init__.py:1278) passes `active_floor_j`, and artifact validators carry fixed `ci95`/floor fields. Replace CG-4(c) with: **“Version the floor producer, authenticated resolution, registry selector, engine wiring, claim evaluator, and artifact validation together; carry floor class and the estimand’s actual unit throughout. Add distinct recorded 90% interval fields for equivalence while retaining historical 95% fields and v1 replay. Update the night verdict record, printed text, parser description, and historical version dispatch with the numerical rule.”** `floor_est_j` alone cannot name a J/correct floor accurately. |

## Simulation tables

The scratch [probe](/tmp/278ebc9e/cgref/probe.py) used production `estimate_paired_blocks`, `small_sample_guard_factor`, `holm_adjust`, `tost_p_value`, and Student-t helpers. Claim runs used six blocks per envelope, `k_cal=k`, registered positive direction, Holm family size five with four missing members, and `B=0.5σ`. CG-2 used a registered `Δ=3σ`; its 90% interval was assembled with the production Student-t helper because the proposed `confidence` parameter does not yet exist.

| Generator | k | CG-1 false admit, δ=0 | CG-1 power, 2σ | CG-1 power, 5σ | CG-2 PASS, δ=0 | CG-2 false PASS, δ=3σ / 5σ |
|---|---:|---:|---:|---:|---:|---:|
| Gaussian | 5 | 0.000 | 0.754 | 1.000 | 0.646 | 0 / 0 |
| Gaussian | 8 | 0.000 | 1.000 | 1.000 | 1.000 | 0 / 0 |
| Heavy t3 | 5 | 0.000 | 0.765 | 1.000 | 0.662 | 0 / 0 |
| Heavy t3 | 8 | 0.000 | 0.992 | 1.000 | 0.996 | 0 / 0 |
| Linear drift | 5 | 0.000 | 0.741 | 1.000 | 0.615 | 0 / 0 |
| Linear drift | 8 | 0.000 | 1.000 | 1.000 | 1.000 | 0 / 0 |
| Shared plus local | 5 | 0.000 | 0.524 | 1.000 | 0.310 | 0 / 0 |
| Shared plus local | 8 | 0.000 | 0.987 | 1.000 | 0.983 | 0 / 0 |

Each row has 1,000 trials. Thus CG-1’s observed δ=0 false admission is below 5% in every tested model. A separate 500-trial-per-cell width sweep also found zero δ=0 admissions at `w/σ = 1, 2`; at `w/σ=2`, 2σ power fell to 0.018–0.034.

For CG-3, r7 has **17 captures in 10 windows** with sizes `1,1,1,1,3,1,2,2,3,2`. The derived pooled within-window SD is **1.982 ms**, between-window SD **1.510 ms**, and observed old SD **2.461 ms**. The table uses simulated old corpora with that layout, one new window, and 2,000 permutations per verdict. Each m=12 cell has 500 trials; each m=8 cell has 300.

| Generator | No-change false FAIL, m=8 / 12 | Detection +3σ, m=12 | +5σ | ×4 variance | ×16 variance | False PASS at margin, fixed r7 old |
|---|---:|---:|---:|---:|---:|---:|
| Gaussian | 0.023 / 0.014 | 0.574 | 0.988 | 0.518 | 0.984 | **0.224** |
| Heavy t3 | 0.023 / 0.020 | 0.634 | 0.958 | 0.346 | 0.864 | **0.196** |
| Linear drift | 0.013 / 0.004 | 0.432 | 0.974 | 0.488 | 0.988 | **0.170** |
| Shared plus local | 0.010 / 0.008 | 0.758 | 1.000 | 0.358 | 0.968 | **0.212** |

The boundary column is the **joint CG-3 PASS** rate at a true shift of exactly `3.5 × s_old`, with the actual r7 corpus fixed: 500 trials per generator, 2,000 permutations each. No-change false FAIL meets the requested 5% ceiling in these runs, but the boundary false PASS does not.

## Probe tails

```text
shared_local 8 mean_F 0.974 d0=0.000 d2=0.987 d5=1.000 e0=0.983 e3=0.000 e5=0.000
shared_local null _locpass=0.994 _spreadfail=0.002 _fail=0.008
shared_local times16 _locpass=0.448 _spreadfail=0.962 _fail=0.968
shared_local fixed-old boundary location=0.212 spread_pass=1.000 joint_false_PASS=0.212
```

The repository remained clean; scripts and outputs are under `/tmp/278ebc9e/cgref/`.

## Residual risk

These are CPU simulations under the specified generators, not live hardware or custody validation. The simulated night’s between-window component was estimated from r7’s ten-window layout; other plausible dependence structures could change the reported rates.