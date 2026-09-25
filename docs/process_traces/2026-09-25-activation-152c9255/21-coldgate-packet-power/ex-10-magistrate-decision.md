# 18/10 — Magistrate decision on HEADLINE-POWER-01 (O-18/E4, Ed-delegated), subject to the Fable final pass

Decided 2026-09-25 07:05 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Inputs: question [00](00-question.md), the Opus ruling [01](01-ruling-opus.md) and the Astra ruling [02](02-ruling-astra.md). Both were blind.

## Where the two rulings agree

- Keep all five levels as separate Holm hypotheses (m = 5), keep Δ_L as the primary, and do not merge, drop or pool levels for confirmation. The binding AP:10 item 7 and v5 §6 forbid it.
- Raise n_acc well above 128. At n = 128 the per-level power at Δ_L = 0.3 is 0.20–0.37, which is not defensible.
- A larger n_acc adds **zero quiet windows**. The energy design (envelopes and null windows) is unchanged; only daytime accuracy-run hours grow.
- Freeze the exact counts and the ID-list SHA-256 at registration, before any test outcome exists.

## Where they differ

- Opus: a **census** of every eligible level-L problem outside the pilot and calibration draws, expected 368/720/911/953/1,022.
- Astra: n_acc[L] = min(600, available), with ≥ 128 required.

For L1 the two coincide (368 < 600). For L3–L5 the census adds 311–422 problems per level.

## Decision

**The census (Opus), with Astra's floor.**
> `n_acc_rule: "census_v1"`: for each level L, the test draw is every problem of the AP §1 eligible pool at level L that is not in the pilot draw or `calibration_draw`, listed by the importer at registration. The exact counts and the ID-list SHA-256 are registration fields, and `subject_strata[]` are the pool's stratum sizes. n_acc[L] ≥ 128 is required for every L, else registration refuses. All five levels remain in the Holm family (m = 5).

**Reason.** Power at the hardest levels is exactly where the headline is weakest: a cell near p = 0.05 contributes SD(ln p̂) ≈ 0.39 at n = 128. Every added problem there buys power at no quiet-window cost. The 600 cap saves compute hours, which are off the critical path. Ed's objective is the most defensible paper, and the tiebreak in "decisions serve the better paper" favours power.

## Not adopted here, and routed to the Fable final pass

- **Opus's df rule** ν = min(ν̂_Welch, ν_proj,L) changes the just-ruled amendment A-JC-1 v1.1 (13/30/21 §A). A magistrate decision cannot amend a cold-gate text, so the Fable final pass rules whether to adopt it as an addendum.
- **Astra's point** that a validated finite-population variance amendment could change the picture: 128 of about 800 problems at the old n means FPC ≈ 0.92, while a census at about 90 % of the pool means FPC ≈ 0.3. That is a real effect on V_acc under the ruled population, "the level-L eligible pool". The Fable final pass rules whether A-JC-1's V_acc takes the FPC. It is prospective, before any data.

## Smallest effect of interest and null wording (P3)

The registration states Δ_L = 0.3 (log units, about a 35 % change in relative efficiency) as the smallest effect of interest, with the per-level power table. A level that is not significant is reported as "not detected at this power", with its interval. It is never reported as "no effect".
