```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Choose (c), preserving the registered log efficiency contrast with a conservative matched floor from both models; reject fresh correctness noise as an instrument-floor requirement for the fixed-seed design.",
  "workspace": {
    "base_requested": "dcf8832a",
    "base_mode": "exact",
    "head_start": "dcf8832a06843ea4f62505aca0b9a0f3ecd03328",
    "head_end": "dcf8832a06843ea4f62505aca0b9a0f3ecd03328",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "A6-1",
        "severity": "blocker",
        "text": "The floor must match the exact estimand and both models. Neither a scalar model identity nor the existing fixed-token joule floor supplies the proposed four-cell efficiency contrast."
      },
      {
        "id": "A6-2",
        "severity": "should_fix",
        "text": "The question conflates fixed-seed replay noise, problem-sampling uncertainty, and fresh-seed correctness variability."
      },
      {
        "id": "A6-3",
        "severity": "should_fix",
        "text": "Existing desk evidence establishes neither scored energy magnitudes nor power and capture feasibility for this proposed floor."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "dcf8832a06843ea4f62505aca0b9a0f3ecd03328"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "dcf8832a06843ea4f62505aca0b9a0f3ecd03328"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The review is complete; the proposed dimensionless floor composition, registration structure, and conditional inference scope require council adoption before implementation or capture.",
      "needs": "Adjudicate the executable texts below; do not treat them as an installed rule."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Only read-only inspection and arithmetic were performed. No hardware, model, workload, or capture was run; no repository files changed.",
      "needs": "Validate the chosen estimator and capture design prospectively."
    }
  ]
}
```

## Findings

### J1 — Choose (c): preserve the scientific contrast and derive its floor

**A6-1 — BLOCKER.** I choose **(c)**, retaining the proposed budget interaction
\[
\theta_L=\log R_L(b_h)-\log R_L(b_l).
\]
This answers whether changing the thinking budget changes the models’ **relative** energy efficiency. An additive difference between their J/correct values answers a different question; changing units alone cannot reconcile them. The draft explicitly leaves this interpretation open. Sources: `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:57`, `:65`; its `03-open-questions.md:8`.

My choice is a **conservative derived resolution margin**, not a claim that taking logarithms eliminates uncertainty. It requires matched energy calibration but no independently fluctuating correct count in every null block. Option (c) expressly requires a derivation and has no existing producer by fiat. Source: `docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:81`.

**Exact proposed derivation.** For each level, index the four contributing cells by
\(c=(8,h),(8,l),(1.7,h),(1.7,l)\), with coefficients \(a_c=(+1,-1,-1,+1)\).

1. Before calibration, register for each cell:
   - Model, runtime, epoch, budget, scorer, seed, workload and capture identities.
   - A constant \(q_c\): attempts in each measured arm member.
   - A positive lower applicability limit \(\ell_c\), in **J/attempt**, selected by a prospective pilot rule. It is not the subsequently observed science mean.
   - Five calibration envelopes, each containing exactly ten valid same-configuration ABBA null blocks. Calibration and claim envelope identities must be disjoint.
2. For block \(i\), envelope \(e\), record four **gross joule** values and compute
   \[
   d_{cei}=(J_{B1}+J_{B2}-J_{A1}-J_{A2})/2,\qquad
   u_{ce}=\frac1{10}\sum_{i=1}^{10}d_{cei}.
   \]
   A and B use identical problem IDs, prompt, budget, seed and scored trace. Alternate ABBA/BAAB starts by frozen assignment, retaining the B-minus-A sign.
3. With \(k_{\rm cal}=5\), calculate sample mean \(\bar u_c\), sample SD \(s_c\), and
   \[
   f_c^J=g(5)\left(|\bar u_c|+
     t_{0.975,4}\frac{s_c}{\sqrt5}\right),\quad
   g(5)=1.5,\quad f_c=f_c^J/q_c.
   \]
   An envelope missing any of its ten blocks is excluded and listed. Fewer than five retained envelopes gives `not_resolvable`; no favorable-outcome top-up.
4. Define \(r_c=f_c/\ell_c\). If any \(r_c\ge1\), do not issue a finite matched log floor. Otherwise issue
   \[
   \boxed{F_{\theta,L}=\sum_c-\log(1-r_c)}.
   \]
   Evaluate it only when every science energy mean \(\hat e_c\ge\ell_c\), with matching calibration applicability. Keep all four accuracy denominators positive.
5. Apply the floor strictly: \(|\hat\theta_L|>F_{\theta,L}\). The Holm test and metrology/decision intervals must concern **this same \(\theta_L\)**. Timing bounds enter the claim interval once, not these null point-energy floors.

Steps 2–3 use the existing ABBA algebra and ruled estimate-floor formula: `joulewise/detection_floor.py:1449`, `:846`, `:121`; `docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3`. The balanced start rule is at `docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:36`. Step 4 is **my proposed new derivation**, requiring adoption.

Its justification is exact algebra: for \(e\ge\ell>f\) and \(|\delta|\le f\),
\[
|\log(e+\delta)-\log e|\le-\log(1-f/\ell).
\]
Sum this inequality over the four coefficients. It is conservative, and uses no small-error approximation or independence assumption. **The algebra does not turn the underlying operational \(f_c\) into a guaranteed error bound.** Its operating characteristics still require validation.

For fixed correctness fractions,
\[
\theta_L=\sum_c a_c(\log e_c-\log p_c).
\]
The \(\log p_c\) terms cancel when comparing a measurement with its same-trace null replay. Thus correctness affects the science estimate and its statistical uncertainty; it need not create artificial noise in this instrument margin. The actual estimator uses accuracy from the larger cohort, not each energy block’s correct count. Source: `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:57`.

**Power and magnitudes — A6-3, MATERIAL.** At \(k_{\rm cal}=5\), the SD term alone is \(1.86250s_c\). Under the explicitly **assumed** independent, equal-variance ten-block model, that is \(0.58897\sigma_{\rm block}\); the absolute-mean term adds more. Night-shared variation does not receive the ten-block reduction. Increasing science \(k\) does not shrink a previously frozen calibration floor.

For **assumed** \(f_c/\ell_c=0.01\) in all four cells, the derived floor is \(0.04020\) log units; for **assumed** 0.10, it is \(0.42144\). Consequently, conservative composition can hide moderate interactions. These are arithmetic illustrations, not measured performance.

The old simulations show why block floors must not gate means, but do **not** establish power here: they used twelve hypotheses, different sample sizes and the old production path. Their reported refusal rates were 1.000 at \(2\sigma\) and 0.840 at \(5\sigma\). Sources: `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:9`, `:17`, `:42`, `:65`. The registration only mandates science \(k_{\rm planned}\ge5\); a definite achieved-power number is unavailable. Source: the wiring ruling above, `:69`.

I found no applicable measured MATH energy/correctness pair in the permitted evidence searched. The suggested smoke explicitly contains **no energy measurements** and failed before loading a model. Source: `docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md:3`, `:11`. With the question’s **assumed** 400 J and six correct, changing correctness to five gives **+20%**, and to seven gives **−14.29%**; ±17% is a linear approximation.

**Executable text:** Adopt `matched_log_floor.v1` using steps 1–5; register the exact four-cell \(\theta_L\), five-hypothesis family, applicability limits and calibration identities before science outcomes. Add a dimensionless unit and versioned composite-floor validator. Refuse missing components, invalid domains or unverified workload transfer. Preserve J/correct, accuracy and J/attempt as reported components. Do not freeze until the full decision rule passes the J5 validation.

### J2 — A null is conditional on the experiment actually registered

**A6-2 — MATERIAL.** Same model, same problems, same seed and same configuration **is the appropriate repeatability null for the currently proposed study**, provided byte identity is demonstrated. Zero replay correctness variance is then expected, not evidence that the floor is understated.

The plan explicitly requires one pinned seed and byte-identical quiet reruns; it scopes accuracy to the frozen problem set. Sources: `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:19`, `:37`, `:43`, `:47`.

Three uncertainties must remain distinct:

- **Instrument/replay variation:** repeated energy measurement of the registered work.
- **Problem-selection uncertainty:** addressed by the registered paired problem/subsample analysis when making the corresponding sampling inference.
- **Fresh-seed generation uncertainty:** relevant only to a study whose target averages over independently drawn decoding seeds.

The current draft calls for jointly resampling problem IDs and respecting energy clusters; it does not license treating the same cohort’s accuracy as a newly observed denominator in every envelope. Source: that draft, `:61`. Reusing one \(p_c\) across ten envelopes does not create ten independent accuracy measurements.

If the desired claim is “expected energy per success over future random generations,” the current one-seed design is inadequate. Independent registered seeds must then appear in **both calibration and science**, with their pairing/covariance preserved. Varying seeds only in calibration would usually inflate the floor for this conditional study, hiding effects; ignoring seed variation while claiming fresh-generation performance would understate uncertainty.

**Executable text:** Freeze `inference_scope = fixed_problem_set_and_seed`; null A/B members share identical seed, item IDs and expected token bytes. Score each logical accuracy attempt once. Refuse affected headline cells under the registered trace-mismatch rule; do not repair mismatches by choosing new seeds. Any seed-averaged claim requires a prospective design amendment, a seed sampling unit and matching science/calibration replication.

### J3 — Both models supply the floor; a larger-model shortcut is unjustified

**A6-1 — BLOCKER.** Use **both model-specific calibrations**, and both budgets for the interaction. Neither parameter count nor higher joules proves which model has larger **relative** energy error. Taking the larger raw-J floor and using it for both is not a justified dimensional conversion.

For a two-cell contrast, my composition uses two terms; for the budget interaction, four. I choose the conservative sum in J1 because it does not assume that errors from different windows cancel. It errs toward missed effects.

With verified independence and an appropriate linearized estimator, stochastic **variances** would add. A pooled raw-J SD mixes different scales; a maximum does not generally bound the combined error; signed averaging of calibration biases may cancel opposing biases without physical warrant. A future tighter rule should use the actual contrast covariance and validate its transfer, not silently substitute pooling.

This caution is particularly relevant because the existing packer enforces model-homogeneous envelopes and interleaves models across envelopes. Sources: `joulewise/scored_packer.py:218`, `:375`. Common-mode transfer must be named and evidenced, with identical covariance treatment on calibration and science; Ed’s ratification retains those conditions. Sources: `docs/decision_log.md:8332`, `:8459`. Later disclosure also rejects treating common-time cancellation as proven conservatism: `docs/decision_log.md:11311`.

The current scalar `calibration_model_artifact_sha256` cannot honestly identify a composite source. The existing ruling expressly refuses cross-model contrasts pending this decision. Source: `docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:69`.

**Executable text:** Keep `calibration_model_artifact_sha256` mandatory on **each component calibration binding**. Add a versioned composite reference containing the four cell bindings, source artifact hashes, lower limits, derivation ID and recomputed dimensionless floor. Each component’s model hash must equal its corresponding science cell’s hash. No single representative model, fallback maximum, pooled raw-J estimate or presumed cross-window cancellation is permitted.

### J4 — Keep the first science nights; count matched calibration separately

**A6-3 — MATERIAL.** Do not call three different activities “the calibration”:

1. W1/W2 derive the timing acceptance.
2. The COUNCIL-407 calibration night measures context-position energy/power relationships.
3. The proposed null windows calibrate the matched claim floor.

The ordered acceptance path is W1, W2 at least six hours later, count-only W3 if needed, derivation and issuance, then G2-a and the calibration night. Source: `docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md:71`, `:81`.

The COUNCIL-407 night has twelve 600-second envelopes, six per model, but runs fixed-token, greedy, thinking-off context rungs and sustained prefill. It supplies neither ten matched scored null blocks per target cell nor a free replacement for this floor. Source: `docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:18`.

**Window arithmetic for my proposal:**

- Two models × five levels × two budgets = **20 calibration cells**.
- Five retained envelopes per cell = **100 cell-envelope allocations**, each with ten null blocks.
- With one cell per physical envelope, this adds **100 accepted null envelopes** before the first complete five-level claim family.
- Sharing an envelope among several cells could reduce the physical count; the absolute model-homogeneous lower bound is **ten envelopes**, five per model. Achieving ten requires all required per-cell blocks to fit, which has not been demonstrated.
- For just one level’s four-cell contrast, the corresponding separated count is **20 envelopes**.

These are **proposed design counts**, not measured feasibility or a requirement to collect 100 regardless of evidence. A prospectively demonstrated transfer rule can reduce the number of distinct calibration classes. “All cells use the same model” is insufficient proof. Conversely, if ten scored ABBA blocks cannot fit the registered envelope, the design fails feasibility; silently splitting them across windows changes the floor’s sampling unit.

Thus I cannot honestly promise “one extra night.” The smoke did not establish even its own timing budget. Source: `docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md:32`. The five-per-model minimum is a lower bound, not a booking estimate.

The first science nights need not wait for this claim floor. The ruled order already places the MATH feasibility pilot after G2-a and the context calibration night. Source: the COUNCIL-407 ruling, `:54`. Claim-bearing MATH capture must wait for the selected floor’s issuance and registration freeze; calibration envelopes cannot later become claim envelopes. Source: the wiring ruling, `:67`, `:83`.

**Executable text:** Preserve W1/W2 → issuance → G2-a → COUNCIL-407 calibration night. Complete the MATH feasibility pilot, then freeze the matched-null roster and floor applicability classes. Book 100 cell-envelope allocations for the full family, reducing physical windows only through a prospective capacity/transfer proof. Publish the actual physical-window count before arming. Mint and pin the composite floor, freeze the science registration, then collect disjoint claim envelopes; do not delay unrelated descriptive science for this floor.

### J5 — What would falsify my choice, and where to detect it

**BLOCKER if observed:**

- **The scientific target requires fresh-seed performance.** My conditional floor then answers too narrow a question. Detect this at adoption of the estimand and claim wording, before registration; redesign both science and null sampling.
- **The fixed-token calibration does not transfer to scored traces.** Duration, power shape, forced-close behavior or model loading may change the error distribution. Detect this in matched-null qualification before floor issuance. Current P2-015 observations contain joules, not correctness, and its extractor excludes `cap_hit` members; carrying that rule into deliberately forced-close scored runs could select the calibration population incorrectly. Sources: `joulewise/detection_floor.py:2106`; `joulewise/floor_extraction.py:2699`; the AP draft, `:41`.
- **The complete gate has excessive false admission.** Detect with a frozen desk simulation before use, covering correlated envelopes/nights, heavy tails, differential model drift, energy–correctness association, sparse denominators and the actual five-test family. Simulate the full split-sample estimator; do not replace it by independent binomial denominators per block.
- **The calibration floor is small only because biases cancel within a same-model null.** Stable, model-dependent absolute energy bias can cancel from every same-model ABBA contrast and remain in a cross-model contrast. No choice among 8B/max/pool fixes this identifiability problem. Detect through an independently specified model/load-dependent instrument check, and scope any surviving claim to the measured rail/allocation estimand. The existing doctrine explicitly disclaims arbitrary physical-energy and future-error coverage: `docs/decision_log.md:11270`.

**MATERIAL:**

- **The floor hides the scientifically meaningful effect.** Detect in prospective power simulation at the actual planned \(k\), with a meaningful effect size selected before test outcomes. More science envelopes cannot overcome a frozen floor above that effect. First investigate conservative composition, applicability limits and calibration uncertainty; do not change the floor after seeing the result.
- **Any science cell falls below its registered \(\ell_c\), has zero accuracy, or violates trace matching.** Detect during reduction; withhold the affected contrast and retain its place in the five-hypothesis family.
- **Five envelopes mostly reproduce one night’s disturbance.** Detect in the declared dependence model and date/session structure, not by treating fifty blocks as fifty independent replicates. The earlier simulations explicitly expose night-shared undercoverage: `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:15`, `:65`.

My proposal intentionally errs high through conservative composition and lower applicability limits. It can still err low through wrong workload transfer, unrepresented dependence or undetectable differential bias. A large-looking floor is not a soundness certificate. Floor and interval gates remain separate; their conjunction is not \(F+B\). Source: `docs/decision_log.md:11291`.

**Executable text:** Before freeze, commit the exact estimator, floor derivation, simulation generators, seeds and full-gate results at the planned \(k\), \(k_{\rm cal}=5\), \(n_{\rm reg}=10\), Holm \(m=5\). Report familywise false admission, coverage, power, refusal and floor-only failures separately, with Monte Carlo uncertainty. Reject the design if false-admission calibration fails or power cannot resolve the prospectively named meaningful effect; do not rescue it by post-outcome threshold changes. At reduction, enforce all applicability, identity, positive-denominator and independence requirements mechanically.

## Residual risk

This derivation is review advice, not installed or empirically validated. The nonlinear mapping is algebraically conservative for its stated perturbation domain; coverage of that domain by the underlying calibration floor remains an empirical/statistical assumption. No live scored magnitudes or feasible window roster were established.

## where I expect the other seats to be wrong

- Requiring fresh seeds merely because decoding uses a stochastic sampler.
- Treating ten energy-block outcomes as the plan’s accuracy denominator.
- Assuming the larger model, or the maximum raw-J floor, covers a cross-model contrast.
- Selling logarithms as either a cure for sparse correctness or a zero-new-calibration shortcut.
- Counting the context calibration night as already satisfying the scored-null design.

## Plain summary for Ed

Keep the question about how thinking budget changes relative energy efficiency.
Repeating identical answers measures instrument noise; drawing new answers measures something else.
Both models need relevant calibration, and the floor must match the exact comparison.
The available smoke supplies no measured energy numbers or credible extra-night estimate.
My proposed floor is conservative and may hide real effects, so test its power before collecting the claim data.
Nothing was changed or run on the measurement machine.