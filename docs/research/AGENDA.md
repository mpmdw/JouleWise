# JouleWise research agenda (living document)

Started 2026-11-07 by the laptop lead from Ed's decisions. Update it in place; keep each entry's source link.

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
Design study: `docs/research-audits/2026-11-07/interp-weight-edit-energy.md`. It covers how surgical weight edits change power and performance, whether that signal can be pulled out of machine noise, and a staged pilot. Until it lands, this section points to it.

## Other audits (2026-11-07, PR #695)
W1 pre-arm gate · W1 budget fallback · Block 6 design (REG §17 amendments before the B5 unseal) · B5 release-to-paper · literature · research program · proportionality.
