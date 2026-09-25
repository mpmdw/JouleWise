```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Choose a matched dimensionless floor for the registered log contrast; the current J floor and single-model registration cannot support it.",
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
        "id": "F1",
        "severity": "blocker",
        "text": "The proposed log-ratio hypothesis has no matched floor; a J or J/correct floor cannot be compared with it directly."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "text": "A cross-model log contrast needs both model artifacts and a joint null, while the proposed registration binds one calibration model."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "The required graded null windows have no demonstrated ten-block, 600-second scored workload fit."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B -c 'import math; print(\"illustrative_C\",400/6); print(\"energy_plus4_log\",math.log(404/400)); print(\"correct_minus1_log\",math.log(6/5)); print(\"correct_plus1_log\",math.log(6/7)); print(\"g5\",math.sqrt(9/4)); print(\"signflip_min_k5\",2**(1-5))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["g5 1.5", "signflip_min_k5 0.0625"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "signflip_min_k5 0\\.0625"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No measured MATH energy or correctness magnitudes were established by the cited desk smoke; the numerical example is assumed.",
      "needs": "Use scored pilot measurements to size and validate the calibration before freezing claims."
    }
  ]
}
```

## Findings

- **F1 — BLOCKER.** The proposed confirmatory statistic is a difference of **log ratios**, while the draft also asks it to clear a J/correct difference floor. Those are different quantities. The draft itself leaves that mapping open (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:63-67`). CG-4(f) expressly permits a registered dimensionless alternative with a matched floor (`docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:9`).

- **F2 — BLOCKER.** The proposed registration has one `calibration_model_artifact_sha256` and currently refuses a contrast joining different model artifacts. A calibration of either model alone is not a null for the complete four-cell contrast (`docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:53,69`).

- **F3 — MATERIAL.** Ten ABBA blocks per graded envelope remain a physical feasibility question. The scored draft requires a quiet shakedown, and the cited calibration-night desk smoke produced no model timing or energy measurements (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:31`; `docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md:1-3,15-34`).

## Residual risk

This is a design judgment, not a measured floor or a power result. The earlier desk simulation exercised the old production claim path with block-scale floors; it does not establish operating characteristics for the proposed log-contrast gate (`docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:7-9,40-48,63-71`).

## J1 — Choice and derivation — BLOCKER

**Choose (c): a dimensionless, matched floor for the registered log change in relative J/correct.** For each level \(L\), freeze two budgets \(l,h\), and retain the draft’s statistic
\[
\theta_L=\{\log C_{8,h}-\log C_{1.7,h}\}-\{\log C_{8,l}-\log C_{1.7,l}\},
\qquad C_{m,b}=e_{m,b}/p_{m,b}.
\]
Here \(e\) is directly measured mean gross J/attempt on the quiet subsample and \(p\) is correctness on at least 128 frozen problems. A zero denominator makes the statistic undefined. This preserves the proposed one-hypothesis-per-level interpretation and its split-sample numerator and denominator (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:31,45-49,55-67`).

For each \((L,m,b)\) among the **four** cells in \(\theta_L\), collect \(k_{\rm cal}\ge5\) independent, same-epoch graded null envelopes, with **exactly \(n_{\rm cal}=10\) ABBA blocks per envelope**. A and B are aliases of the *same* model artifact, budget, prompt, frozen problem IDs, scorer and seed. Run the same off-quiet accuracy and directly measured quiet-energy estimator as the science cell. For envelope \(r\), compute its A and B mean J/attempt, \(e^A_{m,b,r},e^B_{m,b,r}\), and accuracies \(p^A_{m,b,r},p^B_{m,b,r}\), then
\[
d_{m,b,r}=\log(e^B_{m,b,r}/p^B_{m,b,r})
          -\log(e^A_{m,b,r}/p^A_{m,b,r}).
\]
Pair the four model/budget envelopes prospectively into quartet \(r\), with order balanced, and form
\[
z_r=d_{8,h,r}-d_{1.7,h,r}-d_{8,l,r}+d_{1.7,l,r}.
\]
Exclude and list any envelope lacking ten complete blocks; a quartet with an excluded member is excluded. Refuse if any required energy or accuracy is nonpositive, the epoch or trace binding fails, or fewer than five quartets remain. Set \(\bar z=\sum_r z_r/k_{\rm cal}\), \(s_z^2=\sum_r(z_r-\bar z)^2/(k_{\rm cal}-1)\), and
\[
F_{\log}=g(k_{\rm cal})
 \left(|\bar z|+t_{0.975,k_{\rm cal}-1}s_z/\sqrt{k_{\rm cal}}\right),
\quad
g(k)=\max\{1,\sqrt{9/(k-1)}\}.
\]
This is CG-1’s estimate-scale formula applied to the **matched composite null**, in dimensionless log units; its guard is implemented as shown in `joulewise/detection_floor.py:118-122,846-854`, and CG-1 requires distinct calibration and claim envelopes with \(k_{\rm cal}\ge5\) (`docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3`). Pin all four model/budget calibration sources, quartet identities, estimator, \(F_{\log}\), and a prospectively chosen dimensionless admission margin \(M_L\ge F_{\log}\). Admit only after the registered Holm test, the metrology and separately anchor-widened decision intervals agree on a sign, and \(|\hat\theta_L|>M_L\). A claim *beyond* \(M_L\) needs a separately implemented shifted-null magnitude test; the current ruling defers that path (`docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:69,81`). Keep floor and claim-side bound as separate checks, as D-083’s later addendum requires (`docs/decision_log.md:11291-11303`).

For scale only, the question’s **assumed**, unmeasured 400 J and 6/10 example gives 66.7 J/correct. **Assumed** +4 J changes log energy by 0.010; **assumed** one fewer correct changes log J/correct by 0.182. Those describe sensitivity of a ten-answer ratio, not an observed MATH null, and the planned accuracy denominator has at least 128 problems (`docs/process_traces/2026-09-25-activation-152c9255/10-jcorrect-floor-council/00-question.md:13`; `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:31`). At the minimum five calibration quartets, \(g(5)=1.5\); the floor and five-level Holm gate reduce power. The old simulation found 84% missed effects even at its **assumed** 5σ setting, but it used another estimator and must not be quoted as this gate’s power (`docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:40-48,65`). A single-model or fixed-token J floor risks being **too small** for this composite; treating independent ten-answer count swings as matched-null noise risks a **too large** floor. Changing the primary outcome to J, option (b), would answer a different scientific question and requires the cold amendment named in WR-9 (`docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:81`).

**Executable text:** “Freeze \(\theta_L\), \(M_L\), the four graded alias cells and their quartet pairing before test outcomes. Mint \(F_{\log}\) only from at least five independent complete ten-block quartets by the formula above. Refuse a missing, unmatched or stale source; never convert the existing J artifact into this floor.”

## J2 — Seeds and correctness — MATERIAL

**“Same model, same seed” is the correct null for the plan’s stated, seed-conditional result**, provided the pilot proves repeatable token IDs and bytes. The plan freezes one seed, the same problems and trace-matched quiet reruns; it explicitly refuses a headline when even separately generated traces cannot reproduce (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:35-47`). Under that contract, the two aliases’ correctness indicators should match. Their zero *within-null* correctness difference is real conditioning, not a measurement failure. Correctness uncertainty across the frozen problem draw belongs in the paired problem bootstrap and interval, whose split-sample details still require validation (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:57-61`).

Varying A and B seeds independently would calibrate a different experiment: independent stochastic generations. It could make the floor too large for these paired fixed-seed captures. Conversely, using this conditional floor while claiming performance averaged over random seeds could make the full claim gate too permissive; that broader target needs a new seed schedule in **both** science and null capture. Any observed correctness disagreement between same-seed aliases is a trace/scoring defect to investigate, not a count to absorb silently into \(F_{\log}\).

**Executable text:** “Bind both null aliases to the science problem IDs and pinned seed. Compare complete output bytes and scored outcomes before floor minting; refuse discordant repeats. Label admitted claims conditional on that seed and frozen problem set. A seed-marginal claim requires a separately registered multi-seed design and new calibration.”

## J3 — Cross-model floor — BLOCKER

Use **something else: the joint quartet floor \(F_{\log}\) from J1**. An 8B-only floor ignores 1.7B measurement noise; a 1.7B-only floor ignores 8B noise. Their maximum is not generally a bound on the difference of both errors, and a pooled scalar discards their scale and possible within-quartet covariance. The statistic itself contains four signed cell terms, so its null must contain the same four terms. This follows directly from the proposed \(\log R_L(h)-\log R_L(l)\) formula (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:57,65`). The registration’s single calibration-model hash cannot authenticate that joint source; WR-3 currently refuses mixed-model contrasts for precisely this unresolved rule (`docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:53,69`).

**Executable text:** “Replace the single calibration-model binding for this contrast with four keyed bindings \((8B,h),(8B,l),(1.7B,h),(1.7B,l)\), each carrying its artifact SHA-256, plus one pinned joint-quartet floor artifact. Authenticate and recompute the four sources and composite \(F_{\log}\); refuse if any key, model hash, epoch or quartet member differs.”

## J4 — Scheduling — MATERIAL

The 25G83 acceptance ruling schedules **two** 12-slot windows at least six hours apart, with a third only if retained count is short. Its order then places G2-a and the COUNCIL-407-01 calibration night after successor issuance (`docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md:71,80-81`). That calibration night has **twelve 600-second envelopes**, alternating models, for its context and meter questions—not scored MATH null blocks (`docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:18,24`). WR-10 separately requires at least **five** 25G83 fixed-token floor windows before the existing J floor can be minted (`docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md:83`).

My executable schedule adds **20 graded null quiet windows for the first level**: five quartets × four distinct model/budget cells, one cell per window, ten ABBA blocks per window. For all five levels with no verified packing reuse, that is **100 added windows**. These are *additional* to acceptance, the twelve-envelope calibration night, the fixed-token floor windows and claim capture. The counts are a proposed roster, **conditional on a desk shakedown proving the ten-block graded workload fits**; no cited timing result proves that fit (`docs/process_traces/2026-09-24-activation-278ebc9e/57-calnight-desk-smoke/README.md:15-34`). If it fails, report a scheduling blocker and redesign the registered window shape before capture; do not shorten a ten-block envelope after seeing outcomes. A first claim-bearing number also needs its own qualifying science envelopes, which CG-1 requires at \(k\ge5\) (`docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3`).

**Executable text:** “After accepted 25G83 authority and the existing floor windows, pass a scored ten-ABBA-block shakedown. Then reserve five balanced four-window graded-null quartets per level; mint and pin their joint floor before freezing that level’s claim registration. Start claim capture only after its applicable floor is authenticated.”

## J5 — What would falsify this choice — MATERIAL

Three results would overturn it. First, same-seed alias traces or scores disagree: the **pilot and every calibration replay** detect that, and J2’s conditional null no longer matches capture. Second, the joint floor admits too many zero-effect claims, or its interval misses generating values under plausible heavy tails, drift, shared timing and sparse accuracy: the **pre-claim desk simulation and held-out graded null replay** detect that. The prior simulations explicitly show why old within-night intervals and floors cannot be presumed calibrated for a new gate (`docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md:13-17,40-48,63-67`; `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/03-ap5m-v5-open-questions.md:9-11`). Third, ten blocks cannot fit or the scored quiet traces fail their byte-match ceiling: the **shakedown and capture validator** detect that before a headline is issued (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:31,45-53`). Excess false admission means a floor or interval is too small; persistent null over-refusal and failed power targets mean the gate is too large or badly matched.

**Executable text:** “Before first claim use, simulate the full five-level Holm decision with matched split-sample data under declared null and effect generators; report familywise false admission, interval coverage, power and refusal with finite-sample uncertainty. Replay disjoint graded null quartets and enforce trace, epoch and ten-block checks. Reopen the design if the preregistered error or power criteria fail.”

## where I expect the other seats to be wrong

A one-model floor cannot represent a four-cell log contrast.  
Dividing the existing J floor by a correct count has neither the right unit rule nor the right workload.  
A one-answer swing among ten **independently sampled** answers is not same-seed null noise for the planned paired 128-problem result.  
The old desk simulation’s 84% miss rate is evidence against the old gate, not a measured power estimate for this one.

## Plain summary for Ed

Use a noise floor measured on scored math runs and expressed in the same scale as the proposed comparison.  
That comparison uses both models at two thinking budgets, so its floor needs evidence from all four settings.  
The plan’s fixed seed makes repeat accuracy deterministic; uncertainty across math problems still belongs in the confidence interval.  
This choice adds a proposed 20 quiet calibration windows for the first difficulty level, subject to proving they fit.  
No claim should be frozen until that fit, the joint floor and the new claim rule pass validation.