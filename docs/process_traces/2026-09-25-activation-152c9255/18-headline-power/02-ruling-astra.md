```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend 600 accuracy problems per level, capped by available eligible IDs; retain five hypotheses and budget 20 capture days. Blind-read compliance was compromised by a search exclusion error.",
  "workspace": {
    "base_requested": "6d0ae9b0",
    "base_mode": "exact",
    "head_start": "6d0ae9b0bfb5887a2397e15d3af67ab095f554bb",
    "head_end": "6d0ae9b0bfb5887a2397e15d3af67ab095f554bb",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Strict blind-read admissibility is compromised"},
      {"id": "F2", "severity": "should_fix", "title": "Power depends strongly on joint outcomes and finite-pool sampling"},
      {"id": "F3", "severity": "should_fix", "title": "The minimum quiet-window schedule has no two-week contingency"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 -u /tmp/152c9255/pw-astra/finite.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["FINITE_GRID_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "FINITE_GRID_COMPLETE"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 /tmp/152c9255/pw-astra/audit.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NUMERICAL_AUDIT_PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "NUMERICAL_AUDIT_PASS"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "An ineffective initial rg exclusion exposed prohibited September 25 and council-related snippets. They were not used as supporting evidence, but strict blind-read compliance cannot be certified.",
      "needs": "Magistrate must determine admissibility; a fresh restricted seat is required if strict blindness is indispensable."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Synthetic desk simulations are complete. Actual stratum counts, joint correctness patterns, timing, minted floor, anchor bounds and the complete A-JC-1 acceptance battery remain unverified.",
      "needs": "Install and validate the adopted registration before test outcomes or quiet capture."
    }
  ]
}
```

## Findings

**F1 — BLOCKER, process.** The initial search exclusion failed and exposed prohibited snippets. I cannot certify this as an uncontaminated blind ruling. No repository files changed; no other models, inference, or measurement operations were invoked.

**F2 — MATERIAL, statistics.** The independent-outcome power estimates broadly reproduce. The cited comonotonic estimates do not reproduce under the specified joint-outcome construction. Moreover, sampling without replacement from a finite pool changes power substantially when the estimator retains its uncorrected bootstrap variance.

**F3 — MATERIAL, schedule.** The baseline requires **70 quiet windows**, before additional prerequisites or contingencies. Fourteen days works only at five successful windows every day.

Citation abbreviations below expand to these repository paths:

- **AP** = `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md`
- **JC** = `docs/process_traces/2026-09-25-activation-152c9255/13-coldgate-packet-jc/30-addendum/21-coldgate-fable-jc-addendum-ruling.md`
- **SM** = `docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md`

### P1. Sample size and primary question

**Recommend a target of 600 distinct accuracy problems per level, capped automatically by the eligible IDs remaining after the disjoint pilot and calibration draws. Retain all five level hypotheses.**

This is a prospective allocation rule. Freeze its five resulting integers before any test outcomes. The cited **4,040 total** does not establish that every level can supply 600—or 800—problems; the manifest must establish that. Calibration reserves **10 per level**, and the pilot uses **16 overall**. Increasing beyond 200 requires an explicit AP amendment. Sources: `AP:21`, `AP:29`, `JC:75`, `JC:85`.

My rationale:

- 600 provides strong sensitivity for the assumed easy and middle profiles, including when Holm stepdown provides little assistance.
- A near-census does not guarantee useful sensitivity for a sparse denominator under the unchanged A-JC-1 gate.
- Dropping the hardest level because of low accuracy would narrow the scientific question. Keep it and report its limitations.
- Pooling levels or replacing Δ with per-model C trends changes the primary question. Keep those displays descriptive rather than switching primaries to obtain significance.

**Desk simulation.** I used the actual joint bootstrap, implemented through mathematically equivalent multinomial resampling of four-cell outcome patterns within strata—not a delta-method substitute. The estimator, Welch df, missing-level handling, denominator guard, Holm procedure, floor and decision interval follow `JC:67`, `JC:69`, `JC:71`, `JC:73`.

All following generator inputs are **ASSUMED**, not measured:

| Illustrative level | Correctness probabilities: 8B-hi, 8B-lo, 1.7B-hi, 1.7B-lo |
|---|---|
| L1 | .85, .80, .70, .65 |
| L2 | .75, .65, .55, .45 |
| L3 | .65, .55, .50, .40 |
| L4 | .45, .35, .30, .20 |
| L5 | .30, .20, .15, .05 |

Additional **assumptions**: two equally sized subject strata; independent levels; Gaussian paired-envelope SD 0.03; floor 0.0124; anchor bound zero; valid energy capture. “Comonotonic” uses one shared difficulty ordering across all four cells. These are sensitivity scenarios, not measured MATH-level forecasts.

Simulation settings: seed **2026092506**, **2,000 bootstrap replicates** per fitted level, **2,000 families** for n=600 and **1,000 families** for the other finite-pool rows. Finite scenarios draw without replacement from an **assumed 800-ID pool per level with exact cell margins**. The estimator still applies **no finite-population correction**, as required by `JC:69`. IID scenarios instead draw independent problems.

**Power table.** Percentages are simulated admission probabilities. Every alternative row sets the same true Δ at all five levels. “Any” means at least one supported direction; “All” means all five. They are different family-power objectives.

| Sampling scenario | n | Δ | L1 | L2 | L3 | L4 | L5 | Any | All |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Finite, independent cells](/tmp/152c9255/pw-astra/finite-n200-com0.txt:6) | 200 | .30 | 87.9 | 50.5 | 34.7 | 11.2 | 0.2 | 95.2 | 0.1 |
| [Finite, independent cells](/tmp/152c9255/pw-astra/finite-n400-com0.txt:6) | 400 | .30 | 100 | 93.3 | 81.1 | 32.5 | 3.2 | 100 | 2.5 |
| [Finite, independent cells](/tmp/152c9255/pw-astra/finite-n600-com0.txt:6) | **600** | **.30** | **100** | **100** | **99.7** | **59.2** | **6.1** | **100** | **5.7** |
| [Finite, independent cells](/tmp/152c9255/pw-astra/finite-n600-com0.txt:8) | 600 | .50 | 100 | 100 | 100 | 100 | 66.8 | 100 | 66.8 |
| [Finite, comonotonic](/tmp/152c9255/pw-astra/finite-n600-com1.txt:6) | 600 | .30 | 100 | 100 | 100 | 100 | 38.4 | 100 | 38.4 |
| [Finite, comonotonic](/tmp/152c9255/pw-astra/finite-n600-com1.txt:8) | 600 | .50 | 100 | 100 | 100 | 100 | 99.5 | 100 | 99.5 |
| [IID, independent cells](/tmp/152c9255/pw-astra/n600-com0-p0.txt:6) | 600 | .30 | 100 | 97.5 | 92.6 | 52.9 | 18.4 | 100 | 13.8 |
| [Finite census, independent cells](/tmp/152c9255/pw-astra/finite-n800-com0.txt:6) | 800 | .30 | 100 | 100 | 100 | 100 | 0 | 100 | 0 |
| [Finite census, independent cells](/tmp/152c9255/pw-astra/finite-n800-com0.txt:8) | 800 | .50 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

The census rows are mathematical sensitivities, **not promises that 800 test IDs remain after reservations**. Rounded 100% entries are Monte Carlo estimates.

At n=600, simulated null-family admission was **0/2,000** for finite/independent, **2/2,000** for finite/comonotonic, **99/2,000** for IID/independent and **107/2,000** for IID/comonotonic. Their one-sided 95% Clopper–Pearson upper bounds are respectively **0.00150, 0.00314, 0.05823 and 0.06253**. Numerical audit: [audit.json](/tmp/152c9255/pw-astra/audit.json).

Without relying on Holm stepdown, the n=600 IID/independent probabilities of clearing the stricter **p<.01** threshold at Δ=.30 are **99.9%, 95.5%, 87.3%, 38.9%, 6.8%**. Thus “100% chance of finding something” must not become “the study is adequately powered at every level.” [Simulation](/tmp/152c9255/pw-astra/n600-com0-p0.txt:6).

The **80% MDEs**, rounded upward to the tested **0.1 grid**, under that same conservative p<.01 criterion are:

- IID/independent: **(.2, .3, .3, .5, .8)**.
- Finite/independent: **(.2, .3, .3, .4, .7)**.

**Verification of the earlier paragraph.** With its assumed mid tuple `(.55,.65,.40,.50)`, my IID independent-cell average powers at Δ=.30 are **.212 and .373** at n=128 and 200. For fully comonotonic outcomes they are **.922 and .990**, not the cited .37 and .63 (`JC:18`, `JC:19`). The exact first-order comonotonic variance coefficient is **0.779720/n**, giving SD **.07805** at n=128. The joint pattern matters enormously. [128 simulation](/tmp/152c9255/pw-astra/n128-com1-p1.txt:6), [200 simulation](/tmp/152c9255/pw-astra/n200-com1-p1.txt:6).

**Registration text:**
```text
Amend AP §2 and A-JC-1 §A(vii)'s n restriction.
n_target = 600
available[L] = eligible_ids[L] minus pilot_ids minus calibration_ids
n_acc[L] = min(600, count(available[L]))
require n_acc[L] >= 128 for every L
Freeze the five integer n_acc values and selected IDs before test outcomes.
Retain levels [1,2,3,4,5], Holm m=5, alpha=0.05; missing p-values=1.
No outcome-dependent top-up, level removal, merging, or primary replacement.
Recompute projected_power with the actual n, population and subject counts.
```

### P2. Compute hours, quiet windows, and feasibility

I found no applicable measured throughput establishing the proposed schedule. **49 tok/s appears as a planning rate**, explicitly not a campaign measurement, in `docs/process_traces/2026-08-28-workload-consult/01-sol-seat.md:287`. The cited smoke produced **no timings** and failed before model loading: `SM:3`, `SM:11`.

For budgeting, **ASSUME** two rungs, **1,024 and 4,096 thinking tokens**, rates **49 tok/s for 8B and 120 tok/s for 1.7B**, and **25% additional runtime overhead**. Use the draft’s **256-token answer allowance** (`AP:29`). The proposed pair must pass the existing feasibility-only selection rule.

At 600 per level:

| Accuracy execution | Decode hours, derived | Including assumed 25% overhead |
|---|---:|---:|
| Successful nesting | 110.4 | **138.0** |
| Separate-budget fallback | 134.9 | **168.6** |

Nesting requires `4096 + 2×256` generated tokens per model/problem at these assumed caps; separate execution requires `1024 + 4096 + 2×256`. Nesting and its fallback are specified at `AP:37`, `AP:39`. These estimates exclude additional rungs and are ceilings only with respect to the assumed emitted-token caps—not verified wall-clock bounds. [Arithmetic](/tmp/152c9255/pw-astra/timing.txt:6).

**Increasing n_acc adds zero quiet windows if the energy design remains fixed.** For the proposed costed energy design, use **50 distinct energy IDs per level**, **s=1**, five paired subsets, and ten blocks per envelope, subject to pilot precision and capture validation.

- Claims: **5 levels × 5 pairs × 2 models = 50 windows**.
- Calibration: **2 mints × 5 pairs × 2 models = 20 windows**.
- Total: **70 windows**. Sources: `JC:65`, `JC:67`, `JC:88`.

Propose a **5,400-second window class** for budgeting: 70 windows reserve **105 quiet hours**. Under the throughput assumptions, the 8B high-budget null envelope needs **59.2 decode minutes**, or **74.0 minutes** including the assumed overhead. This class still requires the mandated shakedown (`AP:31`, `JC:89`).

At five windows/day, the baseline takes **14 days exactly**; at four/day, **18 calendar days**. I would budget **20 capture days at four windows/day**, providing ten contingency slots. This excludes prerequisite acceptance work. A calibration escalation to k=10 adds **20 windows**, taking the baseline to **90** (`JC:82`).

**Registration text:**
```text
Costed ladder=[1024,4096]; answer_allowance=256; no extra rung is budgeted.
Proposed energy design: s=1, unique_energy_ids_per_level=50,
k_planned_pairs=5, n_reg=10, window_seconds=5400.
Freeze this design only after its precision and strict-capture checks pass.
Baseline quiet windows=70; planning allocation=80 slots over 20 capture days.
Planning accuracy hours=138 nested, 169 separate; both are ASSUMED estimates.
If calibration requires k_cal=10, replace the baseline with 90 windows.
Contingency slots do not override replay-nondeterminism or recapture rules.
```

### P3. Smallest effect and interpretation of nonsignificance

**Propose |Δ|=.30 as the smallest effect of scientific interest.** This is a scientific value judgment, not a sourced empirical threshold. It means multiplying the relative-efficiency ratio by **1.3499 or 0.7408**: approximately **35% higher or 26% lower**, not simply “a 30% change.”

Keep .30 even when a difficult level has low power. Do not increase that level’s importance threshold merely to make its power look satisfactory. The .50 rows are sensitivity analyses.

A nonsignificant level says **“not resolved”**, accompanied by its interval and prospective power. It does not establish no budget effect. Avoid observed/post-hoc power calculated from the estimated effect.

A significant sign also does not establish an effect exceeding .30. For practical-size statements, propose simultaneous **99% per-level intervals**, using Bonferroni across the five levels, with the same anchor widening. Validate their coverage before using equivalence wording.

**Registration text:**
```text
SESOI_abs_log_ratio=0.30.
Primary direction admission remains A-JC-1 v1.1.
Supplemental interval I_L = Delta_hat_L ± (t[0.995,nu_L]*SE_L + B_ln_L).
After interval-coverage validation:
  I_L wholly within [-0.30,+0.30] -> "effects of this size excluded";
  I_L wholly above +0.30 or below -0.30 -> "material effect supported";
  otherwise -> no practical-equivalence or material-size conclusion.
A failed direction gate is "not resolved", never "no effect".
Publish prospective power, denominator counts and intervals; no observed power.
```

### P4. What would show this recommendation wrong?

The recommendation should change **before test outcomes** if:

1. **Actual joint outcomes differ materially from these assumptions.** Marginal p alone cannot establish power. Even perfect positive dependence can greatly cancel error in this contrast.
2. **The actual roster or stratum composition defeats the projection.** A 600 target is not a guarantee of 600 available IDs. Near-census variance and subject allocation must be represented.
3. **Energy uncertainty or metrology dominates.** The simulations assume paired SD .03, floor .0124 and zero anchor bound. Larger values can invalidate their power.
4. **Measured throughput or capture duration defeats the schedule.** The existing smoke cannot settle that.
5. **A validated finite-population variance amendment is adopted.** That could make a census substantially more attractive. It would be a prospective estimator amendment, not permission to silently remove V_acc under today’s rule.

The disjoint **16-problem overall pilot** (`AP:29`) is too small to establish precise joint-outcome distributions for all five levels. Do not advertise pilot-certified power from those few observations.

**Registration text:**
```text
Before freeze, run A-JC-1 §A(vii)'s complete G1-G4 acceptance battery
with actual n/strata and both IID and without-replacement sensitivities.
Use >=2000 families/generator and >=2000 bootstrap replicates/simulation;
production bootstrap replicates=20000; proposed seed=2026092506.
Require null-family admission <=0.06, CP95_upper<=0.075,
and mean(SE)/SD(Delta_hat)>=0.90, as in JC:75.
Repeat with minted floor and recorded anchor bounds.
Treat projected power below 0.80 at Delta=.30 for any L1-L3
as failure of this recommendation's planning rationale: replan before tests.
L4-L5 carry explicit low-power disclosures; never delete them retrospectively.
```

## Residual risk

These simulations validate only their stated synthetic conditions. They do not complete the Student-t stress case, actual-pilot generators, production implementation checks, carryover/replay gates, or hardware validation. The scratch artifacts use Python drivers and a compiled numerical kernel. Nothing is armed.

**Where the other seat may disagree**

- Whether the extra compute for a near-census is worth more than the 600 target.
- Whether a strictly bounded fortnight justifies prospectively narrowing the scientific question.
- Whether finite-population variance should be amended before choosing n.
- Whether .30 is the appropriate scientific importance threshold.

**For Ed**

- Aim for 600 problems per level, using all remaining eligible IDs when fewer are available.
- Keep all five levels; difficult levels may remain unresolved.
- Budget about 138 accuracy hours, or 169 without nesting, under explicit assumptions.
- Seventy quiet windows is the minimum; plan 20 capture days with contingency.
- The earlier power paragraph needs correction, and this seat’s accidental read-boundary breach needs magistrate adjudication.