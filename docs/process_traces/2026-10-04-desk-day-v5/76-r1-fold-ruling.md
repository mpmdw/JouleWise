# Lead ruling 76: fold the isolated rehearsal `r1` into the non-claim G2-b shakedown `s1` (prospective erratum to D-176 decision 4)

2026-10-05, desk-day seat 2 (Opus 5.5, orchestrator). Inputs: blind consult brief [75](75-r1-fold-consult-brief.md);
answers `~/night-archive/desk-day-v5/opus-r1fold.md` (Opus 5.5) and `~/night-archive/desk-day-v5/sol-r1fold-sol.md`
(Sol 6.1 xhigh). Both recommend folding. This ruling is PROSPECTIVE and binds only through the sealed block-4
registration: the cold Fable judge and the independent Opus refuter of that seal rule on it, and Ed may veto
(D-176 was adopted "Ed may veto"). Until that seal, D-176 decision 4 stands.

## Why

`r1` was drafted as a non-inference night on a dedicated rehearsal pack. Lane B's first round
(`~/night-archive/desk-day-v5/sol-b4b.md`) showed that making it armable needs a new arm-readiness profile
(`joulewise/arm_readiness.py:4488`, `:4576`), an isolated ledger genesis pin
(`joulewise/arm_readiness_evidence_t0.py:1572`) and a separate un-inventoried clone, all of which exist only to make
`r1` possible. Both consult seats found no defect class that only `r1` can catch and that protects a claim number:
its exclusive coverage is the T0_REHEARSAL branch itself. On the gates that do protect a number (agent load in
captured power, clock steps, operator activity, wrong pack/ARM/boot, evidence loss) `s1` is the stronger test,
because it runs the real workload under real sampler and GPU load. `s1` is non-claim, isolated, one-use, and has a
tooling-recovery allowance, so a pack-path failure on it costs a window, not a number.

## Decisions

1. **The D-176 decision-4 night is `s1`.** Purpose stays `G2B_SHAKEDOWN`, `claim_eligible=false`, real frozen GAMMA
   pack, one A/B/B/A block (#474). No rehearsal pack, rehearsal profile, rehearsal ledger genesis or un-inventoried
   rehearsal clone is built. Lane B's rehearsal pack generator and chain are dropped; its observation producers
   (process custody, lifecycle stages, HID, lineage, bundle assembly) are kept and run on `s1`.
2. **Live gates on `s1`:** G1, G2, G3, G4, G5, G8, G9, evaluated by the existing evaluators in
   `joulewise/t0_rehearsal.py` on `s1`'s own evidence. **G10**: Ed's physical privileged-anchor control
   (`scripts/ed_session/capture_t0_anchor_positive_control.py`, recipe 46) before `s1`'s T-0 (before `a1`'s if
   convenient), outside every armed/capture span, plus the software ±1 ns falsifiers.
3. **G6 and G7 retire as live gates** (no rehearsal authority or rehearsal roots exist to be presented or to
   overlap). The merged G7 unit regression ("a fully valid rehearsal receipt refused by class") stays. The
   evaluator records G6/G7 as `NOT_APPLICABLE` with basis `retired_by_ruling_76`, never PASS. Dissent (Sol): keep
   G6/G7 as desk controls with `g7-control` amended to accept the non-claim template; not adopted because without
   rehearsal authority there is nothing for them to catch, and amending `g7-control` would need a template that
   never exists in production.
4. **G1 re-ruled (code agrees with the zero-agent fence):** each governed process carries a registered expected
   outcome. The agent census passes on `pgrep` exit exactly 1 with empty stdout (A161 / D-127 fence); every other
   governed process passes on exit 0. fd 0 at `/dev/null`, no timeout, `sequence_completed` stay. Exhaustive
   exec-descendant prompt/EOF tracing is not required: with fd 0 at `/dev/null` a prompting descendant gets EOF and
   shows up as an abnormal exit or an incomplete chain, which G1/G9 and the `s1` verdict already catch.
5. **Two verdicts on `s1`.** (a) The structural G2-b verdict (registration §7, unchanged). (b) The qualification
   verdict (decision 2's gates). Evidence producers only OBSERVE: a producer fault makes the qualification verdict
   REFUSED or FAIL; it never aborts the chain and never turns the G2-b verdict into RECOVER. A qualification FAIL
   with a G2-b PASS goes to the lead: an R3-cured producer is re-run on the same bytes where possible; a gate that
   genuinely failed live (agent present, clock not bounded, HID activity) is END STATE for the block.
6. **No-science RECOVER does not spend `s2`.** A RECOVER whose named pack-path or launch tooling cause fired after
   `chain.started` but before the first science member's sampler started holds no science bytes (D-078 has nothing
   to pool or top up). It is preserved, cured through R3, and re-armed as a fresh `s1` attempt (new plan id,
   authorization and T-0) without consuming the one `s2` allowance. Same refusal code twice in a row → consult.
7. **`a1` stays** (arm-only, must expire `readiness_record_expired`, no launch), directly before `s1`. **Q110's third
   receipt bundle** comes from a second arm-only control `a2` with the same recipe and its own fresh T-0, run after
   `a1`'s expiry check and before `s1`'s T-0; `a2` also must expire with no launch. (A NULL `s1` attempt's ARM
   receipt may substitute if one occurs.)
8. **Kernel edges (installed only after seal):** A160 closes on `s1`'s qualification harvest PASS; Q3 drops its
   NIGHT-PACK-REHEARSAL-01 hard-start; A161 closes SUPERSEDED by this ruling; D-176 decision 4 gains a dated
   erratum pointing here.
9. **Courier blindness (lane C F2):** for every non-`CAMPAIGN_TRANSACTION` purpose the durable record pushed by
   `scripts/run_night.py` excludes raw chain stdout/stderr logs (they carry per-member durations); those stay in
   restricted local custody. Public outputs stay structural.

## Lead rulings carried from the lane reports

- L10-A (lane C F1): `--output-dir` is the staging custody root (`joulewise/analysis_manifest_v3.py:4072`); recipe
  `docs/process/v5-l10-rehearsal-phase.md` §L10-A corrected with a dated note.
- G10 resync vector (lane D F1): the arm step's reviewed ON vector (`scripts/capture_t0_step.py::_arm_reference`),
  imported; anchor poll to >5 ms within a bounded deadline (default 120 s, max 300 s); OFF in `finally`.
- Terminal refresh coverage (draft §14 question 3): the post-`s1` desk refresh moves only the ledger pin and
  re-authors readiness/freeze records; executables, generated pack configs and chain sources do not change (the
  packs pin the acceptance cutoff, not the live ledger head: Fable N4 on #477). H′ = H + those records is covered
  by `s1`'s qualification, proven by an exact changed-path map before any later arm.
- Sizing (lane A F1): approved as a source-bound allowance adapter. GAMMA member estimates at the issued length come
  from block-3 archives (diagnostic reading, permitted after block 3 by its registration §10) and the committed
  pack configs; each allowance cites `{path, sha256, pointer}`. No `s1` byte is used for sizing.

## Addendum A (2026-10-05 02:35, same seat): G9 on `s1`, sizing roster and the clock design check

- **G9 stages on `s1`** (fold seat F1). `s1`'s night chain stops at physical-ahead and must not emit launch
  completion, so the backups and close-out happen in the governed post-STOP desk step, after the quiet window and
  before any later arm. `claim_backup` and `bound_backup` are two verified copies of the `s1` custody and runs
  roots, to two distinct destinations named in the `s1` plan, made through the existing backup path
  (`scripts/run_campaign.py::backup_runs`) with a SHA-256 census verified at each destination. `close_out` is the
  runsheet's Phase G post-run assertion record plus the identity of the window's OFF receipt. `restore` is the
  observed network-time-OFF state and stand-down. `launch`, `capability_consumption` and `capture` come from the
  night itself. No G9 stage may be satisfied by an in-chain step that the G2-b chain forbids.
- **Sizing roster** (sizing seat F2). The plan writer sizes exactly the stages the rendered one-block G2-b chain
  runs. It must not size full-GAMMA stages that `s1` never dispatches (`gamma-reference-arm-boundary`,
  `gamma-reference-prefill-midpoint`).
- **Sizing allowances** (sizing seat F3). The labelled custody, control and backup allocations and the
  auxiliary-model proxy are approved as design allowances. Their bytes are committed under
  `configs/campaigns/v5_qualification_25g83/` so that every allowance cites a repository path and digest.
- **Clock design check** (sizing seat F1). The worst-case product h + rho*T_stream (ladder-maximum anchor half-width,
  maximum drift rate, a 613-second envelope that also counts the separate cooldown sampler) is 8.5 ms. It stacks
  three worst cases, so it is reported as a diagnostic, not a gate. The design check uses observed effective
  clock-anchor bounds from comparable streams on this machine, models and OS build: the block-3 SELECT re-harvest
  holds 50 anchor records, all `bounded`, largest 4.02 ms. The margin to 5 ms is thin and is disclosed to the cold
  gate. The binding admission is unchanged: every obligated `s1` member must be `bounded` at harvest, and the
  majority trigger (at least five recorded anchors, more than half not bounded) ends the block.
