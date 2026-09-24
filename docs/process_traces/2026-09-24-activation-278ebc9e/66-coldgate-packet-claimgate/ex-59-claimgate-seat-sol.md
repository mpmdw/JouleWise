```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a same-scale minimum-effect gate and a two-component equivalence rule; the present one-night design cannot establish that the instrument is unchanged.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "4b7f5a0498b8ab324f6674e1274192ee691f7dfd",
    "head_end": "4b7f5a0498b8ab324f6674e1274192ee691f7dfd",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "should_fix", "text": "The directional floor predicts a future block while the tested estimate is a mean; a claim exceeding a meaningful amount needs a same-scale minimum-effect test."},
      {"id": "F2", "severity": "should_fix", "text": "The proposed equivalence-night rule has poor coverage for separate night shocks and admits most fourfold variance increases."},
      {"id": "F3", "severity": "should_fix", "text": "AP-5M's log-ratio contrast has no general conversion to a joules-per-correct-answer difference for its floor check."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 /tmp/278ebc9e/cg-sol/sim_review.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["NIGHT 80 80 shared_local PASS/mean/var at 0,2,5,x4= [(0.82, 1.0, 0.82), (0.067, 0.067, 0.813), (0.0, 0.0, 0.82), (0.0, 1.0, 0.0)]"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^NIGHT 80 80 shared_local "}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {"id": "R1", "kind": "verification_gap", "level": "nonblocking", "text": "The new simulation is a small synthetic design check, not calibration of a production gate or a physical margin.", "needs": "Validate boundary error, interval coverage, and power with more trials and an authenticated multi-night design before adoption."}
  ]
}
```

# Sol 6.0

## Findings

**F1 — Directional claim.** Define the claim in one physical unit: \(\theta=E[B-A]\) for paired blocks, or a registered additive J/correct contrast for AP-5M. Freeze a sign \(s\), a practically meaningful minimum \(\tau>0\), and an applicable estimate-scale floor \(F_{\rm est}\) before outcomes. Admit “\(s\theta>\tau\)” only when all of these hold:

1. A dependence-preserving, anchor-widened lower confidence bound for \(s\theta\) exceeds \(\tau\).
2. The corresponding test of \(H_0:s\theta\leq\tau\) passes Holm at family \(\alpha=0.05\); AP-5M keeps all **five** level IDs in \(m=5\), including missing results. Use its registered two-sided convention.
3. The point estimate separately satisfies \(s\hat\theta>F_{\rm est}\), and the existing evidence, interval, and eligibility conditions pass.

The bound must resample whole independent nights when the claim generalizes across nights, and preserve paired problem IDs and energy parent/envelope clusters for AP-5M. Add the recorded deterministic anchor envelope once on the claim side. Captures within one night do not estimate a separate night shock; a one-night result needs either an externally validated night-shock bound or wording confined to that night. The current paired estimator treats block scatter as its standard error, while its floor includes a future-block prediction term; these are different scales. `joulewise/analysis_engine/estimators.py:450-489`; `joulewise/detection_floor.py:871-881`; `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:63-67`. Holm retains missing family members. `joulewise/analysis_engine/multiplicity.py:49-77`.

Size \(\tau\) from the scientific claim, in its own units. About **1 J** is an attribution-scale phase example, and roughly **5 J** was historical planning scale for phase contrasts; neither is a universal AP-5M J/correct threshold. \(F_{\rm est}\) must come from an accepted calibration for that estimate class and epoch. Preserve the strict point check required by O-21, but do not use a future-block \(F\) as though it were a mean-scale minimum-effect confidence bound, and do not introduce an \(F+B\) gate. `docs/decision_log.md:4757-4771`; `docs/decision_log.md:4803-4814`; `docs/decision_log.md:11268-11303`; `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:13-15`.

**F2 — Equivalence.** For an ordinary equivalence claim, freeze a physically tolerable margin \(M\) in the *same units as its estimand*. Require \(M>F_{\rm est}\), then admit only if the dependence-preserving, anchor-widened TOST interval lies strictly inside \((-M,M)\), with the TOST p-value adjusted over its registered family. A diagnostic \(4\sigma\) margin is not a physical registration. The current code already requires a margin above \(F\), two intervals inside it, and adjusted rejection. `joulewise/analysis_engine/claims.py:346-368`; `joulewise/analysis_engine/estimators.py:251-279`; `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:7-9`.

For an **“instrument unchanged” night**, require *both* mean equivalence and spread equivalence. Register a seconds-scale mean tolerance tied to the permitted effect on the accepted floor, plus a maximum acceptable variance ratio tied to permitted floor inflation. My desk candidate tests a mean tolerance of \(2\sigma\) and a variance ratio strictly within \([1/2,2]\); those are simulation proxies, **not proposed physical constants**. Construct intervals from independent old and new nights, resampling whole nights. If local capture scatter also matters to the floor, check its variance component separately. A point variance-ratio screen with bound 20 cannot support “unchanged”: the existing proposal passes 88.2–93.0% of fourfold variance increases, and its one-night mean interval covers only 33.5–63.3% under separate shocks. `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md:19-30`; `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim.py:187-224`.

**Operating characteristics.** I ran `python3 /tmp/278ebc9e/cg-sol/sim_review.py` (seed 184600/184601). It copies the four desk generating models, including heavy-tailed errors, centered drift, and shared-plus-local shocks, from `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim.py:43-65`. These rates are exploratory Monte Carlo results.

| Rule and design | No-effect or no-change admission | At \(2\sigma\) | At \(5\sigma\) | Fourfold variance admission |
|---|---:|---:|---:|---:|
| Direction: 10 independent nights × 10 blocks, five Holm contrasts, \(\tau=F=1\sigma\), width \(w=0.5\sigma\) | 0/1,500 per model at \(0\) and \(1\sigma\) | 0.213–0.467 power | 1.000 power | — |
| Same, \(w=1\sigma\) | 0/1,500 per model | 0.005–0.009 power | 0.999–1.000 power | — |
| Same, \(w=2\sigma\) | 0/1,500 per model | 0 power | 0.999–1.000 power | — |
| Night mean TOST **and** bootstrap variance-ratio interval, 17 old/12 new *independent nights*, 12 captures/night | 0–0.020 pass | 0 pass at a \(2\sigma\) shift | 0 pass | 0 |
| Same, 80 old/80 new independent nights | 0.787–0.847 pass | 0.027–0.067 pass at a \(2\sigma\) shift | 0 pass | 0 |

Each directional cell used 300 trials and five contrasts. Each night cell used 150 trials and 200 whole-night bootstrap replicates. At a \(2\sigma\) shift, equivalence admission is a **false admission at the chosen margin boundary**, not power; the 0.067 observed rate and small trial count require further calibration. The near-zero no-change pass rate at 17/12 is decisive for practical use: that strict “unchanged” rule would stall almost every genuinely unchanged night. Eighty independent nights improve passage but impose a substantial collection cost. The existing one-night corpus has 17 old and 12 proposed new *captures*, rather than those numbers of independent nights. `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md:5-15`; `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim.py:202-215`.

Keep the **physical floor and provenance conditions separate**: applicable calibrated \(F\), strict \(|\hat\theta|>F\), window validity, anchor accounting, epoch identity, and custody cannot be supplied by a small p-value. D-083 explicitly keeps floor, intervals, multiplicity, and eligibility as distinct checks. `docs/decision_log.md:11291-11303`; `joulewise/analysis_engine/claims.py:288-323`; `joulewise/analysis_engine/claims.py:388-420`.

**F3 — AP-5M’s missing estimand decision.** Its proposed hypothesis is a *change in log ratios* across budgets, while O-21 asks for a J/correct difference exceeding \(F\). There is no general conversion: ratios can change while the additive J/correct difference stays fixed. For example, \(10/20\) becomes \(20/30\); the ratio changes, while both additive gaps are \(-10\) J/correct. Register the additive contrast as the primary minimum-effect estimand, or give the log-ratio claim its own defensible dimensionless physical margin and matched floor rule. Resolve this **before data**; the v5 draft explicitly leaves the mapping open and has no adopted claim gate. `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:3`; `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:57-67`.

Implementation costs are a versioned estimate-scale floor artifact, cluster-aware interval and test code, registered margins and variance components, and simulation calibration. Existing historical claims and bytes should retain their original rule version; a new rule must govern only prospective registrations. The paper comparison remains unperformed and AP-5M v5 remains a proposal. `docs/decision_log.md:11275-11283`; `docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/01-current-gate.md:22-24`; `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:119`.

## Residual risk

This proposal is wrong if a prespecified, higher-precision simulation or held-out calibration shows boundary false admission above its allocated \(\alpha\), materially deficient interval coverage under night shocks, or unusable power at physically important effects. My night simulation checks variance of *night means* under the desk model’s combined fourfold change; a local-only spread change and real capture loss still need separate tests. The question also conflates an operational decision to continue collecting with the scientific assertion “instrument unchanged.” A one-night screen may support the former with explicit limits; it cannot, on these data, establish the latter.