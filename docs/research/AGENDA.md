# JouleWise research agenda (living document)

Started 2026-11-07 by the laptop lead from Ed's decisions. Update it in place; keep each entry's source link.

## ★ MAIN GOAL (Ed, 2026-11-07)
**ALIGN v4 plus an adaptive red team showing the monitor+energy squeeze holds**, aimed at a main-track submission at a top ML or security venue.
- **The squeeze:** energy and transcript monitors are blind in opposite places. Hiding compute from the meter forces logging plausible work, which the monitor reads. Avoiding the monitor forces unlogged work, which the meter sees.
- **All spare effort goes to** auditing v4 and maximizing the chance of this result. Other lanes get spare capacity only.
- **Work in flight on it** (started 2026-11-07 about 21:00 PST):
  - **Sol, detached** (pushes on completion when the audit is clean): `align/2026-11-07-squeeze-prereg` (preregistration addendum draft), `align/2026-11-07-squeeze-analysis` (joint detection curves, adaptive-adversary simulator, power analysis), `align/2026-11-07-adversary-kit` (meter-aware adversary variants and a positive-control compute injector), `align/2026-11-07-reviewer2` (hostile-reviewer audit). Status files: `/private/tmp/jwsol/squeeze/<name>/pushed`.
  - **Claude workflow `v4-squeeze-readiness`** (Fable + Opus seats; each track pushes itself): `align/2026-11-07-v4-v4-registration` (closing the pre-W1 registration blockers, plus the blind gate checklist), `align/2026-11-07-v4-squeeze-design`, `align/2026-11-07-v4-reviewer2`.
  - Also `research/2026-11-07-tripwire-directions` (part 5: what the tool enables if it works).
- **Critical path:** R0-L3 merge (#699/#700) → R0 → R1 (RUN_STATE 202) → R10 procedure → W1 kit (`lane/2026-11-07-w1-kit-r10`) → close the pre-W1 registration blockers → the blind registration gate → W1 → D windows (Q4) → registration-grade calibration (Q6) → adaptive red team and positive controls, preregistered before data.

## Ed's direction (2026-11-07)
- **ALIGN claim:** "sabotage leaves an energy signature" (protocol v4). More windows and 30B positive-control nights are approved. Registration grade was ruled under Q6 (RUN_STATE 204).
- **Paper 1** is led by BYTES and known-bytes (what a laptop's own counters can and cannot resolve). It is accepted, though Ed finds it less exciting than ALIGN. BYTES stage 1 is due 12 Nov.
- **Main interest: interpretability.** The intersection of surgical weight edits with power *and* performance, with the caveat that power is a hard signal to pull out of a busy machine's noise. A design study is in progress; see "Interp × energy" below.
- **Open source:** contribute anything germane (`docs/research-audits/2026-11-07/oss-contributions.md`, PR #696). Ed writes every upstream post. Agents ping Ed before running upstream code.

## Measurement-Mac experiments (ranked, `docs/research-audits/2026-11-07/methodology-vs-literature.md`, PR #698)
| Status | # | Experiment | Cost | Note |
|---|---|---|---|---|
| **Next** | 1 | Two-channel physical audit of hidden tokens: energy plus trusted time as two detectors of stripped reasoning tokens, with an attack grid | 0 Mac-nights (analysis) | Register before the held-out pool is unblinded. A two-knob mixed attack must be registered too. |
| **Next** | 2 | Agent energy at the machine boundary (DC-input decomposition of local agent episodes), plus the BYTES riders | 0 extra (desk) | Register before BYTES stage 1 (12 Nov). KM003C on D windows needs a ruling. |
| Banked | 3 | Instrument night: the `powermetrics` transfer function against the meter, and IOReport counters (where the missing watts go) | 1-1.5 | No weights needed. Can run by day on a quiet machine. macOS 27 may block IOReport. |
| Banked | 4 | SSD-tier conditional memory: Flash-Next PLE resident, paged or uncached | 1-1.5 | Needs a resident arm, a concurrent pread arm and a page-cache purge. Runs after Flash-Next live validation. |
| Banked | 5-9 | Oversight tax in joules; DVFS power modes by phase; rail share by phase + bits arm; thermal sensitivity atlas; context term across attention regimes | see doc | Partly anticipated in the literature (novelty checks in the doc). |
| Dropped | 10 | Speculative/MTP decoding energy | — | Headline refuted by Dutta et al. 2602.09113. |

## ALIGN / SHADE-Arena (critical path)
R0 → R1 (RUN_STATE 202) → W1 under ruling R10 (RUN_STATE 203) → D windows (Q4: 3 windows of 59,520 s) → registration-grade calibration (Q6). Pre-W1 blockers are in `docs/research-audits/2026-11-07/w1-prearm-gate.md`.

## Interp × energy (Ed's main interest)
Design study: `docs/research-audits/2026-11-07/interp-weight-edit-energy.md` (draft PR #702; 18 ideas, 36 adversarial checks).
- **Ed's reference** exists as a blog post, not a paper: MIT CSAIL, "Sparks of Weight-Space Programming" (2026-11-02). Astra edited 0.016 % of Qwen3.5-0.8B's weights; MATH-500 went from 7.9 % to 48.1 %, and answers hitting the cap fell from 93 % to 33 %. The post has no energy data. An independent rerun found thinking-off already scores 45.8 %.
- **Physics:** for surgical edits, almost all the energy effect comes through **behaviour** (tokens generated; about 12-15× fewer tokens per correct answer in the Astra case). The fixed-token, weight-only effect is predicted at ≤ 3e-5 of energy, likely ≤ 1e-6. Separating it from zero would need about 95,000 replay pairs, so the deliverable is an **upper bound**.
- **Noise:** background processes are not the limit (0.2 % of the known-bytes half-width). The limits are the tiny surgical effect itself, and the chance that the powermetrics rails are *modelled*, not measured. Any small-effect claim must be checked against the KM003C DC meter.
- **Best first experiment: ASTRA-2CH** (one measurement-Mac window after desk prep).
  - Measure energy on the free-running edited and base models.
  - Replay the same tokens through both weight sets to bound the weight-only effect.
  - Run a synthetic data-dependence test of the rails.
  - Needs Ed's OK to download Qwen3.5-0.8B and the edit, plus a forced-token decode loop. Queued **behind** Mac experiments 1-2, BYTES stage 1, the ALIGN windows and the Paper 1 freeze.
- **Refuted ideas:** ROUTER-EDIT (the repo's question bank already predicts a null) and DVFS-COUPLE (the GPU clock is pinned on the fan-cooled Mac).

## Other audits (2026-11-07, PR #695)
W1 pre-arm gate · W1 budget fallback · Block 6 design (REG §17 amendments before the B5 unseal) · B5 release-to-paper · literature · research program · proportionality.
