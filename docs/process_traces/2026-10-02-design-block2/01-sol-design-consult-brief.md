# Sol 6.1 design consult (xhigh): which measurement block comes after Revision 6 block 1

You are a design consultant to the JouleWise orchestrator (Opus 5.5). This is ONE judgment round.
You have explicit license to disagree with the orchestrator's leaning below; say so plainly if you
do, and give the reason in physical or paper-value terms. You write nothing in the repository
(WRITE_SCOPE is empty); put your whole answer in your final message.

## State (verified 2026-10-02 19:00 PDT, main `b317866d`)

- The machine is one M3 Max (128 GB), macOS build 25G83, dedicated to measurement. Windows can run
  back to back at any hour; only physics waits between them (clean dwell, battery float, network
  time OFF settled 600 s on the same boot).
- The calibration acceptance for build 25G83 was just issued (PR #457, `6857428d`):
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, 24 members from two
  Revision 6 derivation windows (C1, C2). The claim hold H1 is lifted. Before this, every ordinary
  capture refused because the only acceptance bound the old build 25F84
  (`acceptance_artifact_epoch_mismatch`, record `docs/process_traces/2026-09-10-activation-96bfeca7/`
  T38j in `RUN_STATE.md`).
- The research plan is `docs/process/research_plan_2026-09-16.md`. Phase 0 (Paper B, the
  phase-energy capstone on the pinned Qwen3 1.7B/8B pair, `_v5`) runs: equivalence night (it
  failed into the Revision 6 derivation, now done) → **G2-a probe evening** (pick the prefill prompt
  length: the shortest of 512/1024/2048/4096 at which every one of at least five Qwen3-1.7B probe
  members shows at least five overlapping power records in the prefill phase; D-166 in
  `docs/decision_log.md`, amended by the 2026-08-30 cold gate) → desk day (rung pin, `_v5` pack
  generation, throwaway-clone re-proof) → G2-b shakedown → alpha/beta floors, gamma contrast. Two
  diagnostic arms (IOReport cross-check, generation-length-1 prefill isolation) were ruled in for
  the desk day. Queue rows: `V5-G2A-PREFILL-PROBE-01` (rank 2, queued), `V5-G2B-SHAKEDOWN-01`,
  `V5-TRANSACTION-01` in `docs/process/state_kernel.json`.
- The G2-a window was fully prepared once (runbook 68,
  `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`; chain
  generator `scripts/gen_g2_phase_d.py`; runsheet
  `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`) and was superseded only by
  the 25F84→25G83 epoch mismatch. `docs/phase_2/derivation_night_runbook.md` §6 item 1 says "A G2-a
  window becomes possible only after the D-138 transaction issues the successor acceptance", which
  has now happened.
- Owner priorities (memory): grade secured by Papers A+B first, then CV value per owner-hour; the
  owner's headline interest is prompt difficulty as an energy axis (Phase 2 `RQ-NEXT-EPCA-LEVELS`).
  Gates exist only to keep numbers defensible and to stop death loops.

## The orchestrator's leaning (disagree if you see better)

Block 2 = the G2-a prefill probe window: one `DIAGNOSTIC_NO_PACK` window, governed pulse-calibration
brackets before and after, four rungs × at least five Qwen3-1.7B members, Qwen3-8B probes recorded
and non-gating; output = the rung selection input, no claim. Reason: it is the first link of the
only chain that reaches Paper B's numbers, and every later Phase 0 window depends on its rung pin.
The two diagnostic arms (IOReport, generation-length-1) would come after, at the desk day.

## Questions

1. Is G2-a the highest paper-value-per-window next block? Name any block that dominates it and why
   (for example: should the generation-length-1 or IOReport arm ride inside the same window as
   additional non-gating members, given the window already loads both models?). Count windows.
2. What must the block's registration fix before data that D-166 and its 2026-08-30 amendment do not
   already fix? Consider: window count and the stop rule (what if a rung has fewer than five
   valid small-model members because of a member-level refusal: one more window, or select from
   what exists?), bracket acceptance against the new 25G83 acceptance (what makes a bracket fail and
   what happens then), network-time condition (register the physical state: OFF read or setter's
   OFF end state, plus the wall-minus-monotonic clock-step test; no exact-stdout match), what is and
   is not a claim, and what the window may never be used for.
3. Anything in the old runbook 68 design that is now wrong given the 09-29 process prune
   (`docs/process_prune_2026-09-29.md`, `docs/orchestration.md` "Cold gates, councils and round
   limits") or that would be cheaper as one setting than as enforcement code.
4. Risks that would waste a window (refusal causes), ranked, with the cheapest pre-arm check for each.

Read whatever you need. Cite file:line for every claim about code. Keep the answer under 1,500
words. First line of your final message: `CONSULT: AGREE|DISAGREE|AGREE-WITH-CHANGES`.

WRITE_SCOPE: []
