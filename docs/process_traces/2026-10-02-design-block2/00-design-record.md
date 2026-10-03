# Block 2 design record (headless orchestrator seat, Opus 5.5, 2026-10-02)

Seat brief: `docs/process_traces/2026-10-02-interactive/design-block2-seat-brief.md`. State:
`~/night-archive/design-block2/`. Base: main `b317866d`. Branch `design/2026-10-02-block2`.

## 1. The choice: block 2 is the G2-a prefill resolvability probe

**What.** One `DIAGNOSTIC_NO_PACK` window (plus at most one recovery window): governed pre and
post pulse calibrations around eight probe stages (Qwen3-1.7B × 5 members and Qwen3-8B × 1 member
at each of 512, 1024, 2048 and 4096 prompt tokens). Output: the D-166 selection input, which fixes
`_v5`'s prefill length. Queue row `V5-G2A-PREFILL-PROBE-01` (rank 2, queued).

**Why this, now.** Research plan Phase 0 (`docs/process/research_plan_2026-09-16.md`) runs
equivalence night → G2-a → desk day → G2-b → alpha/beta floors → gamma contrast; Paper B (the
priority after the merged Paper A; memory "A+ first") is reached only through that chain, and
every later Phase 0 window depends on G2-a's rung pin. The equivalence night failed into the
Revision 6 derivation, which is now issued (PR #457), so the one blocker that superseded the
09-12 G2-a window (`acceptance_artifact_epoch_mismatch`, RUN_STATE T38j) is gone; the derivation
runbook §6 item 1 names exactly this moment ("A G2-a window becomes possible only after the D-138
transaction issues the successor acceptance"). D-167: diagnostic windows are at the lead's
discretion.

**Alternatives considered.** (a) The IOReport cross-check or the generation-length-1 arm first:
both are desk-day diagnostic arms that need the pinned rung (same prompts at the pinned rung), so
they cannot precede G2-a. (b) A generation-length-1 rider inside the G2-a window: rejected,
because the chain stops a stage on the first failure (`--max-failures 1`, `set -e`), so a rider's
failure would cost the core sweep (Sol's containment point). (c) Prompt-difficulty work (Ed's
headline interest, Phase 2 `RQ-NEXT-EPCA-LEVELS`): needs a scored leg and AP-5 policy; not
measurable before Paper B's chain. (d) Another calibration block: nothing calls for one; the
issued acceptance is fresh.

## 2. Consult (Sol 6.1 xhigh, one round, license to disagree)

Record: [11-sol-design-consult.md](11-sol-design-consult.md). First line `CONSULT:
AGREE-WITH-CHANGES`. Adopted: one window plus one contingent recovery window; register the
completeness rule explicitly (a rung needs 5 valid small members; first complete sweep supplies
selection; no pooling; second incomplete sweep goes to a consult); network time as the physical
state; the claim boundary; retire the September runbook's overnight cutoffs. Sol's
disagreement, accepted in full: runbook 68 is not reusable by changing dates; its four concrete
incompatibilities became lane rulings. Recorded, not decided here: Sol recommends one combined
later diagnostic window (matched d=512/d=1 requests with IOReport reads) instead of two separate
arms; that is the next design seat's call after the rung pin. Dissent recorded: none open.

## 3. Readiness scout (Sol 6.1 high)

Record: [12-sol-g2a-readiness-scout.md](12-sol-g2a-readiness-scout.md): 8 blocking, 5 non-blocking.
The new acceptance authenticates, its epoch passes, 24 members verify; the G2-a path does not
traverse today's driver/installer: stale ledger seed (B1), producer ignores ledger refusals (B2),
stale pre-calibration screen literal (B3), installer render/probe assume the derivation chain
(B4/B5), Revision 6 manifest, `SESSION_ID` and 7680 s span applied to G2-a (B6-B8), no typed
calibration refusal (N4), no G2-a harvester (N5).

## 4. Orchestrator rulings

1. **Admission scope.** Revision 6 bookkeeping applies only to Revision 6 windows; G2-a keeps the
   physical start conditions (OFF receipt and settle, clean dwell, gate) with its own programmed
   span literal. Reason: the manifest asserts facts about a prior Revision 6 session, which a G2-a
   window does not have; a null-prior manifest would pass syntax while asserting something false.
2. **Network time** (Ed, 2026-10-02). Registered as (a) the OFF state through the setter's OFF end
   state in either wording (E-NT1 recognition; no exact-stdout match) and (b) the estimator's
   within-capture clock-movement admission, binding per capture; the receipt-to-capture offset
   comparison is reported with a 0.015 s flag, not binding. Reason: this window's output is a
   count inside one capture; a step between captures cannot change a count, and a step inside a
   capture is what (b)'s binding part catches. Physical hazard, not proxy (memory "check the
   physics").
3. **Fable final pass F3 on #457** (issuer `--predecessor-acceptance` default): moot for this
   block, which issues no calibration. Any later calibration block names its predecessor
   explicitly in its registered recipe or fixes the default first; carried forward in RUN_STATE.
4. **#416 pre-arm triple audit.** Not triggered by this block: the amended directive places it
   before any claim-bearing run, and G2-a is diagnostic. It applies before the first
   claim-bearing `_v5` window, at the head containing this lane's capture-path changes.
5. **Gates for the code.** One lane, one PR, six-key ledger (Sol executing review, whole suite on
   the merged tree, CI green, Fable final pass because the lane touches the measurement path's
   admission and the pre-calibration screen, dispositions, Impact).
6. **Count per rung stays 5 small members** (the ratified minimum and the prepared producer
   setting). A sixth member would buffer only post-hoc invalidity, since a campaign-level failure
   stops the chain anyway; not worth changing a prepared input.

## 5. Work items

| Item | What | Status |
|---|---|---|
| Lane G2A-NIGHT-25G83-01 | brief [03](03-lane-g2a-integration-brief.md); branch `feat/2026-10-02-g2a-night-integration` | launched |
| Registration | `configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md` | drafted |
| Arm recipe | `docs/process_traces/2026-10-02-design-block2/40-g2a-arm-recipe.md` | after the lane |
| Seal | cold Fable gate + Opus refuter | after the lane merges (pins need H) |
| Handoff | RUN_STATE top block | last |
