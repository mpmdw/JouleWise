```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Astra 6 recommends deliberate 25G83 recharacterization, longer-pulse validation, and a prospective amendment removing historical-comparator and calendar barriers while preserving physical and claim gates.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "a4f0d00e304bc4a36599e633486bdb0ea4ecb1f2",
    "head_end": "a4f0d00e304bc4a36599e633486bdb0ea4ecb1f2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "A1", "severity": "blocker", "title": "Acceptance must use the amended estimand and claim doctrine"},
      {"id": "A2", "severity": "should_fix", "title": "Several acceptance barriers test historical similarity rather than measurement fitness"},
      {"id": "A3", "severity": "should_fix", "title": "Recharacterize prospectively without making causal attribution a prerequisite"},
      {"id": "A4", "severity": "should_fix", "title": "Timing acceptance does not establish workload transfer or power accuracy"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B /tmp/278ebc9e/acc-astra6/verify.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "N2_HASHES_OK=48 FRAMES=10297 RAIL_PARITY_OK=12 VALID=7",
          "N2_MEDIAN_RANGE_S=0.244023..0.254255 MAX_INTERVAL_S=0.419063",
          "N2_B_MAX_S=0.133330958 B_RANGE_S=0.105080561",
          "UNCHANGED_IID_LEVEL_ONLY_PASS_17_12=0.586207",
          "MAX19_COVERS_POP95_CONFIDENCE=0.622646 MAX59=0.951505"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MAX19_COVERS_POP95_CONFIDENCE=0.622646 MAX59=0.951505"}
    }
  ],
  "flags": []
}
```

# Astra 6

## Findings

For compact, auditable citations, these file aliases apply below:

- **P** = `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
- **D** = `docs/decision_log.md`
- **F** = `joulewise/powermetrics_fiducial.py`
- **B** = `joulewise/calibration_bracketing.py`
- **C** = `docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md`
- **H** = `docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md`
- **R** = `docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md`
- **E** = `docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md`

### A1 — The question needs an estimand correction before acceptance

**Recommend C + deliberate B, with a bounded diagnostic from A only if useful.** Accept an instrument fit for explicitly defined measurements; do not require it to recreate 25F84. Do not turn an issued timing acceptance into a certificate of absolute energy accuracy.

The packet’s account of the approximately 1 J attribution limit and 5 J claim bar omits a decisive subsequent amendment. The September 4 rule says:

- The estimand is **energy assigned by interval-overlap allocation**.
- Its timing envelope is conditional on the held-average reconstruction.
- It does **not** bound arbitrary within-record physical energy allocation, establish inference transfer, or establish future-error coverage.
- `F+B` is a planning diagnostic, not an effective-clearable-effect guarantee. Actual gates remain separate; in the symmetric case their numerical conjunction is `|estimate| > max(F,h+B)`. [D:11268–11303]

That is binding scientific substance, not wording hygiene. The historical `33 W × 31 ms ≈ 1 J` remains an illustrative calculation; approximately 5 J is not a universal acceptance threshold. [D:4763–4769; D:4803–4814; D:11268–11303]

**Cadence physics.** The adapter supplies interval averages with actual `elapsed_ns` support, rather than pretending every record spans the requested 100 ms. Thus
\[
\widehat E(W)=\sum_i \bar P_i\,|I_i\cap W|.
\]
Coarsening the intervals does not inherently lose the energy assigned to complete cells. The principal vulnerabilities are allocation at cut cells, timing reconstruction, pulse identification, and any change in the sampler’s power estimates themselves. [joulewise/adapters/powermetrics.py:73–82,2009–2023; D:11270–11282]

For scale, using **illustrative 33 W boundary-cell averages**, two cut cells contain approximately:

| Delivered interval | Energy in two boundary cells | Fraction of a 330 J / 10 s segment | Fraction of a 19,800 J / 600 s segment |
|---|---:|---:|---:|
| 0.120 s | 7.92 J | 2.4% | 0.040% |
| 0.245 s | 16.17 J | 4.9% | 0.082% |

These are deliberately loose **allocation-ambiguity diagnostics**, assuming the reported cell energies themselves are accurate. They are neither measured errors nor additional terms authorized for composition into the repo’s bound. The amendment expressly distinguishes that diagnostic from the bound. [D:11270–11282]

Therefore 0.245 s can matter materially for a small difference between short segments; it is much less threatening to a large contrast accumulated over hundreds of seconds. “Long segment” alone does not guarantee a small *relative error on a contrast*: subtraction can leave a small difference.

The timing calculation is also not `B = cadence`:
\[
B=\max_{\text{pulse edges}}(|r_{\rm lower}|,|r_{\rm upper}|)+B_{\rm anchor},
\]
and the bracket later supplies
\[
B_{\rm operative}=\max(B_{\rm pre},B_{\rm post})+
                  \max(|B_{\rm pre}-B_{\rm post}|,S).
\]
Neither formula multiplies the old bound by 2.04. [F:1018–1043; B:2490–2495,2574–2585]

The retained second-night maximum, 0.133331 s, would contribute approximately **4.40 J at one 33 W step before additional terms**. That threatens small phase contrasts, not automatically all useful science. I independently reproduced that maximum, the 0.105081 s range, raw cadence, artifact hashes, and rail/frame parity from the archive. [H:59–73; verification V2]

### A2 — Keep physical gates; amend historical-comparator barriers

| Barrier | Recommendation | Reason |
|---|---|---|
| **Three distinct calendar days** | **Drop the calendar requirement. Keep three separately started, settled blocks with registered operating states and restart history.** | Midnight is not a physical reset. Different days can expose drift, but three dates do not establish independence. Explicit state coverage and subsequent brackets are more informative. Do not claim a one-day corpus characterizes all future days. The existing three-night arithmetic is a yield calculation. [P:91–114,143–147] |
| **Retained n ≥ 19** | **Keep for this first replacement campaign as a practical target, not a physical constant or a distribution-free coverage certificate.** | Cutting two observations saves little if all 36 slots still run. The permitted n=17 exception already shows 19 is not immutable. Dependence and tail shape matter more than 17 versus 19. [P:173–177,193–207] |
| **12 slots per day** | **Change “per day” to “per block”; retain 3×12 fixed attempts initially.** | This preserves existing batching and avoids unnecessary implementation churn. Neither 12 nor the midnight boundary has a physical status. Do not compress settling or replace invalid attempts opportunistically. [P:99–114,143–147,173–185] |
| **Pulse interiors, SNR, complete detection, edge support, feasible clock fit** | **Keep.** | They establish that the estimator has the evidence its model requires. An empty plateau interior is a real identification failure, not excessive caution. [P:165–171; F:751–765] |
| **Two members above the old 32.898 ms level stop successor issuance** | **Drop for the new characterization. Retain as a historical diagnostic.** | This asks a new instrument to remain inside the old corpus maximum, even when the new instrument is being deliberately characterized. Larger valid uncertainty should propagate into weaker claims. [P:188–190,250–259] |
| **New-corpus maximum as the first issue’s preflight screen** | **Keep initially as a conservative operating-envelope watchdog, not proof that an exceedance is a systematic physical defect.** | It detects movement outside the characterized envelope. Its false alarms must be disclosed, and an exceedance should trigger diagnosis rather than selective retries. [P:250–259; B:2513–2553] |
| **S, C, and refusal whenever S ≥ C** | **Keep a nonzero allowance and a drift ceiling; change to `C=max(S,Q99,predecessor C)` and permit `S=C`.** | Equality means zero additional budget above S, not invalid measurement. Never lower S to obtain passage. [P:232–248; B:2555–2579] |
| **Epoch equivalence shortcut** | **Drop from this critical path.** | A new characterized epoch need not be equivalent to the old one. The historical FAIL remains recorded. A future shortcut would need scientifically chosen margins and operating-characteristic validation. [P:421–455; C:36] |
| **Identity, custody, prospective membership, subsequent-use-only** | **Keep.** | These prevent mismatched instruments, evidence substitution, and a threshold judging its own training observations. [P:133–171,253–259] |

Two calculations expose why the amendments are warranted:

1. Under independent, identically distributed continuous observations, the probability all **12 new values** lie below the maximum of **17 old values** is exactly `17/(17+12)=0.5862`. The level condition alone therefore rejects an unchanged instrument **41.4%** of the time; the range condition can only reduce passage. This is my order-statistic calculation for the registered rule, not a simulation. [P:432–440]

2. A hypothetical perfectly stable new corpus has `range=SD=0`. Present rules give `S=0.010818` and `C=0.010164834757777545`, so it refuses. Better repeatability should not itself make acceptance impossible. My proposed `C≥S` construction removes that contradiction while preserving the entire allowance. [P:232–248]

The t prediction is model-based. Nineteen observations do not prove a 99% future-error guarantee. For example, even under IID sampling, their maximum covers the population’s 95th percentile with only `1−0.95^19=62.3%` confidence. The separate 59-pulse argument gives 95/95 coverage for its **calibration distribution**, subject to its assumptions; it does not turn 19 capture-level maxima into an unconditional future bound. [P:193–207; F:9–18]

Before issuance, simulate the actual proposed rules under skewed bounds, rare excursions, serial dependence and block drift, as well as a Gaussian reference. Report coverage and refusal rates. Do not call a Student-t output “99% coverage” outside its supported model. The existing council already requires that broader simulation discipline. [C:34–36]

### A3 — Executable path, failure tests, and calendar

**Desk steps, before capture**

1. Install one prospective amendment containing the table above, the claim boundary in A1, the fixed 36-slot schedule, exclusions, blindness, and stopping rule. Keep all valid members regardless of B.
2. Explicitly distinguish **historical prior-set evidence** from **new acceptance membership**. Otherwise the existing “valid same-epoch observation outside this registration refuses issuance” clause conflicts with the already populated ledger. Preserve the prior records and their hashes. [P:156–163,253–259]
3. Prepare a **2 s pulse protocol**, retaining 59 pulses, phase-varying gaps and the 0.25 s interior margins initially. Recompute duration limits, thermal expectations, chain budgets, identities and hashes. This is a new protocol, not a relabelled v3 capture. [R:54–62]
4. Exercise the pulse/clock code on synthetic phase offsets and the complete archived diagnostic set; run the acceptance-rule simulations. Authenticate the actual writer’s clock method. The r7 code reissue still identifies 25F84, and the v3.1 evidence-consumer clock path does not automatically replace the calibration estimator. [configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20–26,495–505; joulewise/uncertainty_evidence.py:935–948]
5. Prepare the G2-a bindings and calibration-night registration/payload concurrently at the desk. Neither is armable merely because this council recommends a route.

**Quiet window 1: prospective feasibility validation**

Ed supplies any missing narrow sudo authorization; the lead prepares the signed-off payload and exits before acquisition. No alternate OS boot or replacement binary is required for my path.

Run a fixed, registered pulse-validation block covering cold/settled and warmed operation with varied pulse phase. Require usable interiors, complete detection, feasible anchors and bounded residuals. Record every failure. A short command/sampler comparison may share this diagnostic window if registered, but **binary-versus-OS causal attribution is not an acceptance prerequisite**.

The geometry is decisive: with maximum interval width h, pulse length L and margin m, `L−2m ≥ (k+1)h` guarantees k complete interior cells under continuous coverage. At the verified approximately 0.419 s tail, a 1 s pulse with 0.25 s margins cannot guarantee even one; a 2 s pulse can guarantee two. Future interval tails must still be checked. [R:56–58; F:751–761; V2]

Longer plateaus do not automatically fix onset ramps or prove transfer. If complete detection or anchor feasibility still fails, stop the derivation spend and investigate that mechanism.

**Quiet windows 2–4: prospective corpus**

Run three separately settled 12-slot blocks, at any hour, without examining B values until all are terminal. Retain every valid registered observation; require n≥19. No outcome-driven top-ups. Review exclusions, state dependence and the complete distribution, then issue through the authenticated successor transaction. Governed estimator changes require the D-138 atomic re-freeze. [P:139–185,253–259; D:9184–9193]

**Quiet window 5: G2-a. Quiet window 6: calibration night.**

After issuance, regenerate and verify G2-a’s acceptance bindings, complete rehearsal and exact-plan arm checks. The binder actually derives the live calibration vector; an old artifact cannot simply be renamed. [scripts/generate_g2a_probe_inputs.py:638–674]

Preserve G2-a-first ordering. Prepare the meter night meanwhile: context-rung smoke, immutable meter import, alignment, battery-flow exclusions and reader-overhead controls. Ed handles the physical meter connection and any unavailable privilege. The meter is USB-C input after the charger, not a calibrated mains reference. [C:18–24,50–54]

**Already-seen data.** Use both September 19 nights, including invalid attempts, for mechanism diagnosis, estimator stress tests and disclosed retrospective sensitivity analyses. Use the idle pilots for cadence/clock/observer characterization. Count **none** toward this new prospective corpus; neither September 19 night counts under Ed’s ruling, and idle pilots are not 59-pulse captures. Reprocessing does not make already-seen data prospective. [E:9–14; P:156–185; docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/03-evidence-inventory.md:3–20]

**What would show this path wrong?**

- Longer pulses still fail identification: detected in feasibility validation, before 36 attempts.
- Apparently stable timing hides state dependence or rare large excursions: exposed by block diagnostics and prospective science-window brackets; the first failed bracket blocks that window’s claims.
- Timing uncertainty makes the target contrasts unresolved: actual floor and decision-interval gates refuse them. That is a sensitivity result, not justification to tighten the instrument indefinitely.
- The accepted pulse bound fails under inference: detected by an in-workload transfer check; physical timing claims must wait for that evidence.
- Statistical simulations show material undercoverage: revise the statistical claim/rule before use, rather than merely increasing a threshold until the corpus passes.

**Calendar, conditional on successful gates**

There is no honest unconditional arm date because implementation, review and payload readiness remain unfinished.

- **Capacity-only earliest G2-a: September 24**, if all desk work and five sequential windows—including intervening desk gates—fit that date. This uses the stated five-window ceiling; it is an extreme lower bound, not a credible promise.
- **Capacity-only earliest calibration night: September 25**, as the sixth window.
- **Practical fast schedule:** September 24 desk work plus feasibility; September 25 three corpus blocks plus G2-a; calibration late September 25 if a fifth window and its payload fit, otherwise September 26.

Three corpus blocks currently reserve about **7.5 hours**, excluding desk transitions; longer-pulse budgets must be checked. Any generator restriction tied to the next 07:00 needs a reviewed scheduling amendment rather than a quietness fiction. [P:99–114]

The end-of-November horizon does not justify accepting unsupported numbers. It does justify bounding this instrument work to days and letting propagated uncertainty determine which science is feasible.

### A4 — What this question misses

**Timing calibration, workload transfer, and power accuracy are different questions.** The source explicitly conditions fiducial interpretation on load-regime transfer; the project currently places an inference transfer fiducial after the campaign. I would move a bounded transfer check before any publication claim relying on physical phase-timing accuracy, or keep the paper’s claims explicitly at the conditional allocation estimand. [F:9–18; D:10766–10774; D:11270–11275]

Likewise, CPU+GPU+ANE rails and USB-C input measure different boundaries. Their disagreement cannot by itself identify rail error, memory energy, or meter error. The proposed simultaneous experiment is useful precisely if its boundary and battery controls remain explicit. [joulewise/adapters/powermetrics.py:57–58; C:22–24]

The fastest good-science question is therefore: **which registered segment contrasts remain informative under the measured 25G83 uncertainty and named energy boundary?** Matching the old cadence is only one possible means.

## Residual risk

This was a read-only review. I independently checked the second-night archive, source formulas and cited rules; I did not perform live validation, verify present arm readiness, or execute the proposed simulations. No repository files changed; scratch verification is under `/tmp/278ebc9e/acc-astra6/`. No other agent or model was called.