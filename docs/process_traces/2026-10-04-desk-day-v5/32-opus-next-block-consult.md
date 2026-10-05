# Opus 5.5 consult — next measurement block after the `_v5` desk day (2026-10-04)

Blind seat, one round, read-only. Short version: run **(a) in substance, compressed**: one registration holding `r1` (rehearsal), `a1` (the arm-and-expire, no launch) and `s1` (G2-b). They run in one quiet session at the **claim head**, with the claim analysis plan sealed before `s1` harvest is opened. Do not go straight to ALPHA.

## 1. Is the scout's critical path right?

The order is right. The weighting is not: several links protect a number only if they run at the **same code head** as the claim windows.

**Links that protect a number:**
- **Desk proof.** Pin → packs → freeze → clone re-proof. Every printed energy is attributed to a declared workload (prompt bytes, prefill length). Without the pin-bound packs, the workload identity is unproven.
- **G2-b plus L10-A** (Q3 `TASK_QUEUE.md:703`, A119 `:785`). These are the first real `_v5` bytes at the new prefill length to go through validate, reduce and the refusing finalizer, before any claim custody exists. G2-b launches the GAMMA contrast pack (`SHAKEDOWN-G2-RUNSHEET.md:271`), so both models run at the selected length.
- **Launch-realization recheck** (Q4 blocker, `TASK_QUEUE.md:704`; `scripts/launch_window.py:272–286`). It proves that the bytes launched are the bytes that were reviewed.
- **#421 battery** on every window, and **#416** before the first claim window. Both are Ed directives. I would not drop them.

**Procedure that should be merged, not dropped:**
- **`NIGHT-PACK-REHEARSAL-01` (A161, `:811`).** Its number-protecting content is G6 (rehearsal custody disjoint from the production ledger) and G7 (a rehearsal receipt cannot launch production). Both are code properties. Its other failure modes give a NULL night, not a wrong number.
  - It is still worth one short occurrence: D-176 decision 4 rules it (`docs/decision_log.md:11534–11538`), and it supplies one of the ≥3 real T-0 bundles `T0-LIVENESS-BOUND-EMPIRICAL-01` needs before ALPHA (Q110 `:712`). G2-a, being `DIAGNOSTIC_NO_PACK`, authors no arm T-0 receipts.
  - So `r1` should carry **no model inference**: arm → T0_REHEARSAL GO → stub chain → G7 control. It should be minutes long and sit in the same quiet session as `a1` and `s1`, not on a night of its own.
- **#416 triple audit.** Run it at the frozen claim head **while `r1`/`s1` are being prepared and run**, not afterwards in series. If G2-b forces a fix, re-audit only the diff.
- **Order fault in the scout.** It puts the launch-realization recheck and claim registration *after* G2-b (scout §4 table). That defeats G2-b, because anything landing between `s1` and ALPHA is code G2-b never ran. Land the recheck, the plan writers, the battery S3 choice and the floor generators **before** `s1`, so that G2-b proves THE claim head.

**Email Ed today** about the Ed-only links on the path: the privileged-anchor positive control (A161 "NEEDS-ED", `:811`) and the rehearsal-clone cut (E166, `:696`).

## 2. Next registered block

**Recommendation: (a) compressed.** One registration, occurrences `r1` → `a1` → `s1`, in one quiet session. An agent harvests `r1` between occurrences (the zero-agent rule binds only at T-0 and capture). `s1` arms only on `r1` = PASS.

What each option can reveal that the desk cannot:
- **(b) G2-b alone:** fails on two counts.
  - D-176 §4 says G2-a "discharges NO gate" (`decision_log.md:11534`), so (b) needs a re-ruling.
  - The liveness row needs three real T-0 bundles: rehearsal, ARM-ABORT and G2-b (`:11549`). Without `r1` there are two, so ALPHA blocks on a cold-gate re-rule of the 600 s bound anyway. A ~30-minute `r1` is cheaper than that ruling.
- **(c) Straight to ALPHA:** rejected for a science reason, not a procedural one.
  - Suppose ALPHA's first real-byte pass finds a defect in reduction or bracket binding at the new length. Then either the code changes mid-transaction, and ALPHA/BETA/GAMMA span two heads (GAMMA's contrast compares across those heads), or ALPHA is voided under D-078 no-retry (Q4 fence, `:704`).
  - G2-b costs one A/B/B/A block (four members: small, large, large, small; no after-midpoint stages, `scripts/gen_g2_phase_d.py:541–545`) and finds the same defect before claim custody opens. The code refuses (c) anyway: `CAMPAIGN_TRANSACTION` needs G2-b's custodied verdict (D-176 §2, `:11515–11518`).
- **What G2-b does *not* reveal:** the floor packs, never launched before ALPHA, whose generators were just re-bound to ladder-specific reported-cell identities. In the clone proof, assert those identities against the reducer output schema; register "floor-pack defect at first launch" as an ALPHA RECOVER cause.

## 3. What the registration must fix in advance

Follow the shape of block 3 (`registration_block3.md` §§2, 4, 7, 10).

- **Occurrences and allowance.**
  - `r1`, `a1`, `s1`, plus at most one recovery each (`r2`, `s2`).
  - `a1` arms once, never launches and expires completely before `s1`'s fresh T-0 (Q3 fence; runsheet "must never straddle… the later T-0 clean dwell").
- **Mechanical verdicts**, written by a harvest script in the style of `harvest_g2a_window.py`:
  - `r1`: **PASS** means G1–G10 all PASS from producer-emitted evidence. UNRULED or INCOMPLETE is FAIL (A161).
  - `s1`: **PASS** requires all of the following:
    - the chain exits with the registered one-block stop code;
    - exactly one complete A/B/B/A block;
    - both brackets pass;
    - `bracket-binding.json` is written before the verdict row;
    - the desk checker passes;
    - the scratch finalizer refuses with exactly `analysis_finalization_member_cover_mismatch`;
    - `floors/` is empty before and after;
    - the G2-b tree hash is unchanged.
  - **RECOVER**: the chain started and the occurrence is not PASS.
  - **NULL**: `chain.started` is absent.
  - **REFUSED**: a harvest tooling fault. It goes through the R3 fix route and is never a science outcome.
- **Stopping rules (copy from block 3 §7).**
  - A NULL re-arms under the standing rules.
  - The same refusal code twice in a row sends the next step to a Sol+Opus consult, not a third arm.
  - A RECOVER with no `powermetrics*.plist` captured counts as NULL.
  - After a RECOVER with capture: one recovery, only after the cause is named and removed. No pooling and no top-up (D-078).
- **END STATE.** If `s2` also ends RECOVER, or `s1` shows a systematic instrument cause registered now (for example the block-3 clock-anchor criterion: more than half of the anchored members not `bounded`):
  - the block stops and no third G2-b is armed;
  - the transaction does not open;
  - Ed is emailed;
  - the next step is a design record (consult + cold gate) on the named cause class.
  This is the death-loop stop.
- **Head freeze.** One reviewed head for `r1`/`s1`/ALPHA. A cure after `s1` reopens `s1` (as `s2`) and triggers a diff-scoped #416 re-audit, never a full one.
- **Blindness (missing from the scout).** `s1` produces real energies on the claim workload. Seal the claim analysis plan **before** the `s1` harvest. Until then the harvest emits structural verdicts only, with energy fields withheld, as in block 3 §10. Otherwise the ALPHA analysis can be tuned to the shakedown numbers.
- **Window length.**
  - Derive `window_max_s` by block 3's rule (programmed span from the component estimate + 2,700 s dwell cap, `registration_block3.md` §4), and check the longest member stream against the 5 ms clock-anchor bound: longer prefill means longer streams, and drift voids members.
- **Bindings.** Fix:
  - pin and pack sha256s;
  - acceptance `n24_25g83_r2`;
  - the step-6 record and `hC`, by argv only (D-176 §3);
  - the authorization record: `purpose`, `claim_eligible=false`, `permitted_blocks=1`.

## 4. Code that must land before the arm

1. **Unattended one-block stop. This is measurement code: Fable final pass.**
   - Today the G2-b chain asserts `test "$SCIENCE_RC" = 130` after a second-terminal SIGINT (`scripts/gen_g2_phase_d.py:531–539`).
   - `permitted_blocks` is validated only as metadata (`joulewise/night_gate.py:1008`, `joulewise/arm_readiness.py:10128–10131`). `scripts/run_campaign.py` has no block limit; its only stop flag is `--max-failures` (`:688`). Nothing at run time enforces "one block".
   - The fix is a controller-side `--max-blocks`, read from the plan and checked against `permitted_blocks`, that ends the stage after block 1 with a registered rc and a terminal log row; the chain then takes the post-bracket path. A driver-sent signal is racy and can leave a partial member.
2. **Plan writers.** Pack-night plan writers for `r1` and `s1` through `NightPlan.from_mapping` / `write_night_plan` (`joulewise/night_plan_writer.py:38,50`), binding the authorization sha256 and the step-6 record. This is launch-binding code: standard code gate. Add a Fable pass only if it changes the chain bytes that the science reads.
3. **Launch-realization recheck.** It lands **before `s1`** (see §1). Fable pass, because it guards which bytes the number came from.
4. **Harvest verdict scripts for `r1` and `s1`.** Fable pass: the PASS predicate decides admissibility.
5. **Battery S3 helper and preregistration pinning choice.** Settle it before the terminal desk freeze (scout §4).

## 5. Biggest risk in the next two weeks

**The corpus splits across heads or calibration states.** ALPHA, BETA and GAMMA run on different days, and GAMMA is a contrast against floors minted from ALPHA/BETA. Code fixes, a recalibration or an acceptance change landing between ALPHA and GAMMA would make the contrast compare unlike things. The current path invites this: a long gate chain where each fix restarts audits, which creates pressure to "just patch" mid-transaction.

What I would do:
- Freeze the claim head before `s1` (§1), and have the ALPHA registration fix one head, one acceptance (`n24_25g83_r2`) and one macOS build (25G83) for all three packs.
- Pre-commit the response to a mid-transaction defect: a cure touching the claim path supersedes the whole transaction; any other defect is disclosed and the transaction continues at the frozen head.
