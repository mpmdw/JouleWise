```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Astra 6 recommends physically sized minimum-effect inference, a separate applicable floor, and distinguishing single-night clearance from evidence of instrument equivalence.",
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
      {"id":"F1","severity":"blocker","summary":"The existing directional gate does not establish an effect greater than a practical minimum."},
      {"id":"F2","severity":"blocker","summary":"One new night cannot establish unchanged between-night variability without additional assumptions or independent history."},
      {"id":"F3","severity":"should_fix","summary":"AP-5M needs a registered common-scale estimand and validation of its nonlinear estimator before adopting the gate."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"other",
      "cmd":"python3 -B /tmp/278ebc9e/cg-astra6/sim_astra.py claims","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["DONE claims"]},
      "expected":{"exit_code":0,"tail_regex":"DONE claims"}
    },
    {
      "id":"V2","kind":"other",
      "cmd":"python3 -B /tmp/278ebc9e/cg-astra6/sim_astra.py night","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["DONE night"]},
      "expected":{"exit_code":0,"tail_regex":"DONE night"}
    },
    {
      "id":"V3","kind":"inspection",
      "cmd":"git status --short --branch","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},
      "expected":{"exit_code":0,"tail_regex":"^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id":"R1","kind":"verification_gap","level":"nonblocking",
      "text":"Simulations validate stated synthetic designs, not live hardware, the full AP-5M ratio estimator, or an operational single-night replacement.",
      "needs":"Prospective estimator and physical-tolerance validation before adoption."
    }
  ]
}
```

# Astra 6

## Findings

**F1 — Adopt a minimum-effect test for the requested stronger claim; retain F separately.**

The current conjunction is a point estimate above F, intervals excluding zero, and adjusted rejection. It supports direction subject to that physical screen; it does **not** establish that the true magnitude exceeds F or another practical minimum. The production implementation and D-083 addendum agree on this distinction. (`joulewise/analysis_engine/claims.py:343`, `joulewise/analysis_engine/claims.py:369`, `docs/decision_log.md:11291`.)

My executable recommendation for paired energy differences:

1. Register the estimand \(\theta=E_{\text{independent nights}}[\text{mean paired }(B-A)]\), workload/window, weighting, practical minimum \(d>0\), and deterministic attribution bounds.
2. Form one contrast mean \(Y_k\) per independent night. Preserve pairing and balanced order within nights. Shared stochastic shocks belong in between-night uncertainty; captures within a night are not independent substitutes.
3. Construct a confidence interval by inverting an **exact night-level sign-flip location test**, then propagate the registered deterministic bounds without dividing common uncertainty by \(\sqrt n\).
4. Test the composite null \(|\theta|\le d\), apply Holm across the five frozen hypotheses, and require the supported sign to match any registered direction.
5. Independently require the applicable, current, same-estimand floor and strict \(|\hat\theta|>F\), plus existing evidence eligibility.

For an explicit implementation with common bound \(B\), define

\[
P_+(c)=2^{-K}\#\{S\subseteq\{1,\ldots,K\}:
\sum_{k\in S}(Y_k-c)\le0\},
\]

including the empty subset; \(P_-(c)\) reverses the inequality. Then

\[
p_D=\min\{1,\;2\min[P_+(d+B),P_-(-d-B)]\}.
\]

Apply Holm at family \(\alpha=.05,m=5\). Inverting the corresponding location tests gives the interval; at a Holm step with threshold \(a\), the relevant directional endpoint uses one-sided \(a/2\). Publish ordinary 95% intervals separately, clearly labelled. Do not pretend Holm rank-specific intervals are automatically simultaneous intervals.

This test is exact under independent nights with errors symmetric about their mean; heteroscedastic nights and arbitrary dependence among the five contrasts are allowed. The four supplied generators satisfy the required symmetry for their balanced night means. Their centered drift averages out; arbitrary drift does not and needs a registered bound or a different validated design. The generators explicitly contain night shocks and shared/local timing terms. (`docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/sim.py:52`.)

For unequal or coupled attribution bounds, compute the worst p-value over the admissible allocation set. Common/local timing information may narrow that set only where physically justified. Never assume independent timing errors merely to gain power.

**Physical sizing.** I propose **5 J as a candidate minimum for the historical phase-contrast example**, not a universal constant. Approximately 1 J of attribution movement and the historical ≈5 J planning bar motivate its scale; neither proves scientific utility for every workload. The later addendum explicitly makes F+B non-gating and limits the estimand to interval-overlap allocation. (`docs/decision_log.md:4763`, `docs/decision_log.md:4803`, `docs/decision_log.md:11268`.)

F remains a separate physical condition. It is neither an alpha threshold nor an extra interval half-width. The existing floor contains a future-block prediction term and an observed maximum; dividing that entire quantity by \(\sqrt n\) would be unjustified. Establish a mean-estimand floor prospectively, preserving systematic attribution limits and separately accounting for averaging of identified random components. Until then, retain the applicable accepted F. (`joulewise/detection_floor.py:871`, `docs/contracts/analysis_plans.md:29`.)

**Effect equivalence:** register a physical margin \(M\), with applicable \(F<M\). For the phase example, my candidate is **±5 J**. Use

\[
p_E=\max[P_+(-M+B),P_-(M-B)]
\]

and Holm on the five equivalence p-values. This is TOST: at unadjusted .05 it corresponds to a 90% interval wholly inside the margin, not an additional 95%-interval hurdle. Retain the separate physical admissibility checks. The current implementation additionally requires its supplied 95% intervals inside the margin; that is an extra conservatism to amend explicitly. (`joulewise/analysis_engine/claims.py:346`.)

Directional and equivalence claims must not become two independently searched families without registering that opportunity.

**Operating characteristics — proposed claim rule.**

Exact replay:

```sh
python3 -B /tmp/278ebc9e/cg-astra6/sim_astra.py claims
```

[Simulation source](/tmp/278ebc9e/cg-astra6/sim_astra.py), [claim results](/tmp/278ebc9e/cg-astra6/claims.json).

Design: 3,000 independent simulated families/model; five dependent contrasts; **10 independent nights × 10 captures/night**. Same supplied noise/shock generators. Illustrative physical conversion: \(\sigma=5\) J, \(d=M=5\) J, \(B=1\) J, \(F=4\) J. **F=4 J is a simulation assumption, not an accepted calibration.** Seeds 184610–184613.

| Model | Direction power, 2σ | Direction power, 5σ | Equivalence power, θ=0 | Worst-bias boundary directional FWER |
|---|---:|---:|---:|---:|
| Gaussian | .88960 | 1.00000 | .91393 | .01700 |
| Heavy t3 | .88860 | 1.00000 | .90747 | .01567 |
| Centered drift | .87967 | 1.00000 | .90520 | .01533 |
| Shared/local | .64780 | 1.00000 | .58347 | .01300 |

Power columns are per contrast. The last column is the probability of **any** false directional admission when all true effects equal \(d\), with an added common bias \(+B\).

Additional measured results:

- Directional false admission at θ=0: **0 observed** in every model.
- At θ=d without added bias, family false admission: **.00100/.00133/.00100/.00100**.
- False equivalence at θ=M: family rates **.00200/.00100/.00267/.00033**.
- False equivalence at 2σ and 5σ: **0 observed**.
- Expanded ordinary 95% interval coverage: **.99693/.99727/.99673/.99533**.
- Requiring \(F=8.5\sigma\) instead makes 5σ directional power **zero in all four models**.

These gains require a different sampling design and physical scale, not just a different inequality. Ten independent nights are not ten captures from one night. Zero events in 3,000 independent families gives an approximate 95% upper bound of .001, not proof of zero risk.

---

**F2 — Replace “instrument unchanged” with an explicit tolerance claim, and distinguish it from single-night clearance.**

The current numerical night check compares a new maximum and range against old screens. The proposed replacement’s own report records 88.2–93.0% admission after ×4 variance, and poor coverage under separate night shocks. Neither establishes broad absence of instrument change. (`scripts/epoch_equivalence_check.py:503`, `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md:19`.)

My proposed **epoch-equivalence** target includes:

- Difference in mean timing bound.
- Within-night capture variance \(W\).
- Variance of night means \(V\), which includes shared shocks.

A physically interpretable candidate is mean difference **within ±3 ms** and both variance ratios **strictly within (¼,4)**. These are proposed tolerances, not established instrument specifications.

Why this scale? At the historical 33 W boundary swing, 3 ms corresponds to about **0.10 J**, one tenth of the approximately 1 J attribution movement. The proposed old-corpus timing SD is 2.461 ms, corresponding to about 0.081 J at that sensitivity; doubling SD adds roughly 0.081 J. Thus the variance limit has an explicit candidate error-budget interpretation. This conversion must be redone for the actual window’s sensitivity and authenticated corpus; it is not universal. (`docs/decision_log.md:4763`, `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md:13`.)

An executable reference design:

- Freeze 64 independent nights per era, 12 retained captures/night.
- Mean TOST: \(D\pm t_{.95,63}\sqrt{V_{\rm old}/64+V_{\rm new}/64}\), wholly inside ±3 ms.
- For each variance ratio \(r\), construct \([r/q_{\rm hi},r/q_{\rm lo}]\); require the entire interval inside (¼,4).
- Calibrate pivot quantiles prospectively across the declared generator classes, including different old/new classes. My simulation used conservative empirical 4th/96th percentiles, with worst-case endpoints across classes.
- All three tests must pass. This intersection-union claim needs no three-way Bonferroni penalty: whenever equivalence is false, at least one required component null is true. Multiple epochs or repeated opportunities require their own registered multiplicity/sequential policy.
- Outside the validated model class, or without identifiable independent-night variation: **INCONCLUSIVE**, not “unchanged.”

This variance procedure is **model-calibrated**, not distribution-free. In particular, the t3 model defeats ordinary fourth-moment-based variance approximations.

Replay:

```sh
python3 -B /tmp/278ebc9e/cg-astra6/sim_astra.py night
```

[Night results](/tmp/278ebc9e/cg-astra6/night.json). Calibration: 6,000 epochs/model, seeds 184620–184623. Independent evaluation: 4,000 old/new pairs/model, seeds 184630–184633. Both eras use the supplied generators, including independently drawn night shocks.

Pivot intervals: \(V:\ [.619021,1.615559]\); \(W:\ [.583863,1.713606]\).

| Model | Equivalence power: unchanged PASS | False PASS: +2σ | False PASS: +5σ | False PASS: ×4 variance | False PASS: mean at margin |
|---|---:|---:|---:|---:|---:|
| Gaussian | .99975 | 0 | 0 | 0 | .04675 |
| Heavy t3 | .97500 | 0 | 0 | .00600 | .04225 |
| Centered drift | .99950 | 0 | 0 | 0 | .05025 |
| Shared/local | .99925 | 0 | 0 | 0 | .04800 |

Mean-interval coverage: **.90300/.91000/.90500/.90675**. Margin-boundary rates are consistent with nominal .05 at this Monte Carlo precision. At 2σ/5σ the nonadmission rate is 100%; nonadmission alone must not be relabelled proof of change.

**I do not recommend imposing this 128-night design before every ordinary measurement.** It demonstrates that a variance-sensitive equivalence rule can admit unchanged instruments, but exposes the cost of the broad claim. For an actual single new night, between-night variance equivalence is not identified by twelve captures. Report conditional session clearance under authenticated physical bounds, or inconclusive epoch equivalence; do not make blanket “unchanged” certification a gratuitous prerequisite for otherwise admissible science. Any cheaper historical-model route needs its assumptions and predictive coverage validated explicitly.

---

**F3 — Register the AP-5M scale, validate that estimator, and preserve historical meanings.**

AP-5M currently proposes a log ratio-of-ratios contrast while leaving the J/correct floor mapping open. Its clustered split-sample bootstrap is also unfinished. (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:61`, `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:65`.)

A concrete candidate resolves the sign mismatch. Write \(C_{m,b}\) for J/correct and register

\[
\theta_L=C_{8,H}-C_{1.7,H}\frac{C_{8,L}}{C_{1.7,L}}.
\]

For positive denominators, its sign equals the draft’s log ratio-of-ratios sign. It measures the high-budget J/correct departure from retaining the low-budget model ratio. Register this interpretation explicitly; it is not the ordinary between-model difference at one budget.

Apply the practical minimum and instrument floor on this same scale. Propagate all four cells’ energy allocation uncertainty through the formula. Preserve joint problem, parent-block, envelope, and night dependence. **The linear sign-flip simulations above do not validate this nonlinear ratio estimator.** A calibrated nested-bootstrap or other validated test is required; symmetry cannot be assumed for ratios.

Implementation requires a versioned estimator/test, cluster provenance, physical-bound propagation, matched floor metadata, admission semantics, and prospective registration. No production files were changed. No historical claim is automatically reclassified. Prospective amendments must preserve immutable old meanings and freeze rules before outcomes; outcome-driven top-ups remain prohibited. (`docs/decision_log.md:11280`, `docs/decision_log.md:3381`, `docs/contracts/analysis_plans.md:46`.)

The D-165 ratio census remains a separate registered paper falsifier; it is not evidence that this statistical interval covers physical common-time error. (`docs/decision_log.md:11313`.)

What would refute my recommendation:

- Independent validation exceeds .05 family false admission at practical-null boundaries, including mixed-null families and adverse permitted bias.
- Real residuals violate the independence/symmetry assumptions without a validated replacement.
- A scientifically worthwhile, physically resolvable effect has inadequate power at affordable registered sampling.
- The proposed timing-to-energy tolerances fail actual allocation replay.
- Plausible variance-shape changes defeat the model-calibrated epoch intervals.

The question misses that **“2σ” does not specify practical importance**. At the recorded 0.29–0.49 J repeatability, even 5σ is only 1.45–2.45 J, below a chosen 5 J minimum. Refusing that stronger minimum-effect claim is correct, not lack of sensitivity. Conversely, inflating a future-block floor until useful mean effects cannot pass is not justified by nominal rigor. (`docs/decision_log.md:4758`, `joulewise/detection_floor.py:879`.)

## Residual risk

These are synthetic design results, not hardware evidence or full AP-5M validation. The centered-drift generator does not test arbitrary order-confounded drift; the variance calibration covers a finite model class. The reference designs use more independent nights than the original harness, so their power gains cannot be credited solely to gate redesign.

The next step is to select the physical tolerances and estimand, then validate a feasible registered sampling design—including boundary and mixed-null cases—before implementation or claim-bearing data.