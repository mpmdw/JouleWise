# 18/00 — HEADLINE-POWER-01: sample size per level (Ed's O-18/E4), now that the claim gate carries the accuracy error

Assembled 2026-09-25 06:41 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Authority: Ed delegated O-18/E4 ("n per level") on 09-23. The magistrate decides toward best practice, with Opus 5.5 and Astra 6 each ruling and a Fable 5.1 final pass (directive #405, item 2). Nothing is armed.

## The problem, from the ground up

- **The headline.** For each MATH difficulty level L (1–5), the plan measures the energy per correct answer C = e/p for two models (Qwen3 8B and 1.7B, 4-bit, one Apple M3 Max) at two thinking budgets (low and high). It tests Δ_L = ln R_L(b_high) − ln R_L(b_low), where R_L = C_8B / C_1.7B: did the longer budget change the models' relative efficiency? The plan is the AP-5M v5 draft, `docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md`.
  - e is joules per attempt, measured on a quiet subsample.
  - p is the fraction correct over n_acc frozen problems, measured in accuracy runs outside quiet windows.
- **What changed today.** The cold gate found that the ruled claim gate ignored the sampling error of p. Its amendment A-JC-1 v1.1 (`docs/process_traces/2026-09-25-activation-152c9255/13-coldgate-packet-jc/30-addendum/21-coldgate-fable-jc-addendum-ruling.md` §A, with §1's power paragraph) adds it: SE² = s_d²/k + V_acc, where V_acc comes from a stratified joint bootstrap over problems and uses Welch df.
- **The consequence (the judge's numbers; verify them).** Per-level power at Δ_L = 0.3 is 0.20–0.37 at n_acc = 128 and 0.36–0.63 at 200. At a hard level with a cell near p = 0.05 it is about 0 at any feasible n, because that cell alone contributes SD(ln p̂) = √(0.95/(0.05·n)) = 0.39 at n = 128.
- **The limits.**
  - Problem pool: the eligible pool is 4,040 problems, about 800 per level (AP:21).
  - Time: accuracy runs need compute time but not quiet windows. For a rough number at 4k thinking tokens, the 8B runs at ≈49 tok/s, so ≈80 s per problem-attempt (assumed; verify from the repo if a measurement exists).
  - Holm: correction across the five levels (m = 5).
  - Ed's objective: an A+ capstone and the most impressive defensible paper. His standard: "preventing bad science, not progress on the paper when models agree".

## Questions

- **P1.** What n_acc per level? Consider the options:
  - raise n toward the pool (up to ~800);
  - fewer levels, or pooled levels;
  - a different primary (per-model C trends rather than the double-difference Δ_L);
  - a smallest effect of interest stated up front with its power;
  - dropping or merging the hardest level where p ≈ 0.05.
  Give the recommendation with its power table (per level and family-wise) from your own desk simulation, using the A-JC-1 v1.1 estimator.
- **P2.** What does your choice cost in accuracy-run hours and in quiet windows? Is it feasible within about 2 weeks at 4–5 quiet windows per day plus unrestricted daytime accuracy runs?
- **P3.** What should the registration state as the smallest effect of interest, and what does the paper say if a level is not significant (underpowered versus null)?
- **P4.** What would show your recommendation wrong?

Answer with executable text for the registration (numbers, not ranges), concerns tiered BLOCKER / MATERIAL / NIT, and a plain summary of at most 6 lines for Ed.
