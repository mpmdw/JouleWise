# Research strategy: the energy tripwire (Ed and the lead, 7-8 November 2026)

This records the strategy discussion of 7-8 November 2026. It is the "why" behind `docs/research/AGENDA.md`, which holds the "what next". Update both together.

## 0. Capstone milestones (Ed, 2026-11-08)
- **Nov 30: capstone talk.** Headline: the sabotage energy tripwire (v3 pilots, the instrument with known-bytes as validation, the squeeze framework, v4 in progress; v4 outcomes stay sealed).
- **Mid-December: capstone paper.** The sabotage-tripwire pilot study, with BYTES and known-bytes as the instrument-validation section. v4 results go in only if v4 passes its registered release by about Dec 10.
- **About six months of advisor-supervised research:** v4 → v5 (the squeeze) → NeurIPS 2027 (mid-May).
- The older BYTES-led "Paper 1" framing is superseded.

## 1. What result we are aiming for
| What is shown | Likely level |
|---|---|
| Today's pilots only | A workshop paper (AI-safety or trustworthy-ML workshops) |
| v4 at registration grade, non-adaptive agent | A strong workshop paper, a good arXiv preprint, a possible main-track paper at a smaller venue |
| **v4 plus an adaptive red team showing the squeeze holds** | **A credible main-track submission at a top ML or security venue, with real attention in the AI-control community.** This is the **MAIN GOAL** (Ed). |
| Plus an open, cheap benchmark | A datasets-and-benchmarks angle, and citations from reuse |

- **For an undergraduate first paper,** the preregistered, blinded design with an independent recompute and a public deviation log is unusually rigorous, and it is visible to reviewers, admissions and safety fellowships.
- **Limits on significance:**
  - datacenter batching makes per-episode attribution hard, so the result applies most directly to local and on-prem agents;
  - it needs a trusted meter on hardware the auditor controls;
  - one machine, two task pairs, mid-size open models.
- **The tripwire-directions study (PR #703)** estimates about 2/3 for a solid workshop paper and about 1/4 for main track if v4 clears W1 and the D windows. A measured limit is more likely than a clean win.
- **Target venue:** NeurIPS 2027 for the full squeeze (submission about mid-May 2027). An earlier v4 or limits paper if v4 lands cleanly. The security alternatives (CCS 2027 cycle 2, S&P 2028 cycle 1) are decided in March 2027.

## 2. The scientific claim: three layers of oversight
- **Transcript and CoT monitors** read **content**. They cannot see work that never reaches the log.
- **The energy meter** audits the **quantity of computation**:
  - It catches work actually done but missing from, or edited out of, the record: deleted or rewritten logs, unlogged side generation, tool subprocesses, and runtimes the auditor cannot trust or re-run.
  - It is blind to intent inside logged work: unfaithful or steganographic CoT, and latent reasoning within a fixed-compute forward pass. The weight-only physics effect is about 10⁻⁵ or less (interp study, PR #702).
- **Interpretability probes** see **internals**.

**The squeeze:**
- A monitoring-aware agent cannot satisfy both the monitor and the meter at once.
- Hiding work from the meter means logging plausible work, which the monitor reads.
- Hiding from the monitor means keeping work out of the log, which the meter sees.
- This puts the result in the field's growing worry: models that know they are monitored and alter logs or CoT.

**Design consequences (PR #703, lead):**
- **Authenticated runtime:** on a seeded local stack the auditor controls, a software rerun already catches stripped reasoning. Energy's necessary niche is runtime-external compute (side generation, tool subprocesses) and runtimes that cannot be trusted or re-run. Build the headline claim and the positive controls there.
- **Replay-referenced residuals:** judging each episode against a replay of its own log repeats to about 2 J, against 19-58 J for the regression residual. That is about 10-25× more sensitive, at the cost of extra Mac time.
- **Primary estimand:** the escape rate per sabotage attempt. Strict all-cells survival is descriptive only, because a zero-escape rule over 720 trials passes 0.07 % of the time at a true 1 % escape rate.

## 3. The plan: v4 as designed, v5 for the squeeze
- **v4 runs essentially as designed:** Qwen3.8-27B 8-bit, two SHADE task pairs, thermal gates, registration grade (m ≥ 39 per pair plus a held-out test cohort; Q4 and Q6 rulings, RUN_STATE 204). It adds only two things:
  - KM003C capture in every window;
  - full transcripts with reasoning, retained, sealed and unscored.
- v4 alone supports the solid paper (the energy tripwire against known hidden work).
- **v5 is the squeeze:** a monitor arm, an adaptive red team (attack families A0-A13), a capability gate, positive controls of runtime-external compute, and test windows. A design competition (Sol and Opus seats designing an add-on to v4 and a ground-up v5, judged by Sol and Opus) decides between:
  - reusing v4's frozen configuration (which saves about 7 calibration windows);
  - designing from scratch to escape v4's weak points (2-4-turn episodes at about 11.9 tok/s, the 8-bit budget failure, thermal-gating overhead, two task pairs).

  Results: `docs/align/squeeze/v5-design/` on `align/2026-11-08-v5design-*`.
- **v4 audits (7 November):** v4 as registered could not produce the squeeze paper. It had no monitor arm, no adversary and no meter capture; those are now v5 work or the two v4 additions. The pre-W1 registration blockers are on the v4 track (`docs/align/squeeze/v4-registration.md`).

## 4. Rulings from this discussion
- **Power path:** the KM003C sits between the wall brick and the MagSafe cable and measures all wall-to-machine power, ALIGN included. **Every measurement captures it, and every analysis analyses the DC-in channel** (Ed's standing rule; RUN_STATE 210).
- **D-139 A1 amended:** a scoped on-host red team is allowed. The agent under test is the adversary, sandboxed.
- **Monitor:** a frontier model via API, off-box, is primary; a local monitor is secondary. No monitor scores any v4 transcript before registration.
- **Models and review style:**
  - Sol 6.1 high/xhigh is a full partner. It is used liberally for seats, drafts, implementation and reviews.
  - Opus 5.5 is the Anthropic model for rulings and cross-family seats.
  - Sonnet 5.5 is on trial for big-work agents; Sonnet or Haiku for simple work.
  - Fable gives one final look at major checkpoints only.
  - Sol and Opus review each other's products, and every v4/v5 step ends in an agreement report that weights findings by cross-family agreement.

## 5. What else the tool enables (if the tripwire works)
Ranked candidates (PR #703; all novel, all rated incremental as written unless the squeeze lands):
1. the squeeze against a hider that deletes only the incriminating reasoning (H_blind against H_det);
2. where the tripwire stops working under batching (dense 27B against the 30B mixture of experts);
3. a map of hiding methods, their energy cost, and which detector sees each.

Also considered:
- sandbagging signatures;
- model substitution and inference-compute verification (compute governance);
- out-of-model agent activity (a sandbox tripwire);
- eval awareness;
- latent reasoning;
- an open "SHADE-Energy" benchmark.
