# Consult (blind, one round): what is the next measurement block after the `_v5` desk day, and what must exist before it can be sealed?

You are one of two independent consult seats (the other is a different model; you will not see its answer). You have explicit license to disagree with anything below, including the framing. Read-only: write nothing in the repository; write only your answer file.

## Situation (2026-10-04)
- JouleWise measures LLM inference energy on a dedicated M3 Max MacBook (powermetrics + pulse calibration brackets, an append-only calibration ledger). Paper claims come from the `_v5` campaign: three packs, ALPHA = `d117_floor_qwen3-1p7b_v5`, BETA = `d117_floor_qwen3-8b_v5`, GAMMA = `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (`configs/arm_readiness/d117_row_registry_v2.json`).
- G2-a measurement block 3 (diagnostic prefill-resolvability probe) ended SELECT; the `_v5` prefill length is now a protocol parameter fixed by that record (not 512).
- Desk day in progress (gated PRs): #471 prompt-pin issuer bound to the block-3 harvest; floor generators taking the prefill length from the pin, re-bound to the acceptance in force `n24_25g83_r2`, with ladder-specific reported-cell identities; contrast generator made replayable under generic generator authentication and re-bound to the same acceptance; then pin issuance, pack generation, throwaway-clone freeze/arm-admission/receipt re-proof.
- A read-only scout mapped the path: `/Users/edr/night-archive/desk-day-v5/sol-scout.md` (read §§3-5 and "Plan"). Its critical path: desk proof → isolated pack-bound rehearsal (`NIGHT-PACK-REHEARSAL-01`, D-176 decision 4, purpose T0_REHEARSAL, G1-G10) → registered real-pack G2-b shakedown (`V5-G2B-SHAKEDOWN-01`, one non-claim A/B/B/A block) → L10-A + T0-liveness → launch-realization recheck + claim registration + directive #416 pre-arm triple audit → transaction authorization → ALPHA, BETA, GAMMA. It recommends one registration with occurrences `r1` (rehearsal) and `s1` (G2-b), and flags that `scripts/gen_g2_phase_d.py` has no unattended G2-b plan writer (its rendered G2-b stop expects a second-terminal SIGINT).
- Doctrine: Ed (owner) has ruled that every gate exists only to protect a number or stop a death loop; windows run back-to-back at the cadence the science needs; unattended windows with zero owner input are the goal; directive #421 (battery float) applies to every window; #416 applies before the first claim-bearing window. Rows: `TASK_QUEUE.md` (A161 NIGHT-PACK-REHEARSAL-01, A160 D169-STAGE3-01, Q3, Q4, A119 L10-A, E166 CLONE-READINESS-01), `docs/decision_log.md` D-162, D-171, D-176; `docs/process/v5-l10-rehearsal-phase.md`; `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`.
- Planning note: a floor window at the selected prefill length will be longer than at 512 (the prefill cells get longer prompts; decode is forced 512 tokens either way). A component estimate is being built.

## Questions
1. Is the scout's critical path right? Which links are genuinely needed to protect a number, and which are procedure that could be merged or dropped under Ed's "gates protect numbers" rule? Be specific (row ids, file:line).
2. What should the next REGISTERED measurement block be: (a) `r1`+`s1` as the scout proposes, (b) G2-b alone (if the rehearsal's purpose is already met by the G2-a block windows, which ran unattended through the same driver), (c) go straight to ALPHA as the first claim-bearing window with G2-b's checks folded in, or (d) something else? Argue from what each window can reveal that the desk cannot.
3. What must the registration fix in advance (stopping rules, recovery allowance, harvest verdicts, END STATE) so the block cannot become a death loop, following the G2-a block-3 registration's shape (`configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`)?
4. What code must land before the arm (the unattended G2-b stop; pack-night plan writer; anything else), and which of it is measurement code needing a Fable final pass?
5. Your single biggest risk to the science in the next two weeks, and what you would do about it.

Answer in at most 1,500 words, with file:line evidence for factual claims. Write your answer to the output path you are given. One session, foreground commands only; finish in this turn.

WRITE_SCOPE: []
