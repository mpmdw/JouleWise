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

## Addendum B (2026-10-05 04:55, same seat): clock, idle admission and the pre-mortem rulings

Inputs: the Opus pre-mortem memo (`~/night-archive/ia-0a40/MEMO.md`, lane ia-0a40, run from the interactive session
at Ed's request) and the blind consult in brief 90, with both answers beside it (`90-opus-clock-idle.md`,
`90-sol-clock-idle.md`).

**What each clock guard protects.** The per-member effective bound (at most 5 ms, pinned estimator) decides where an
energy trace sits against the wall-stamped phase edges; it is the guard that protects the joules. At 40 W, 5 ms is
0.2 J per edge, below the roughly 1 J attribution limit. The T-0 anchor check protects provenance: it shows that
nothing reset the clock between R0 and authoring. With network time OFF the anchor drifts steadily at the kernel's
stored frequency correction (−3.17 ppm today, read-only `ntp_adjtime(modes=0)`), so a fixed 5 ms check refuses any
T-0 span longer than about 1579 s even when nothing happened.

1. **Idle 75 s** (memo 1.8). All `_v5` science, NEG-8 bound and reference configs move from `idle_seconds` 30 to 75,
   the value block 3 ran with (all 50 anchors bounded, largest 4.02 ms). At 30 s every stream is shorter than the
   60-second clock-fit minimum and returns `unknown`. The packs are regenerated and re-pinned through a gated PR.
2. **Frequency gate** (memo 1.1). After G10's OFF and at every R0, read the kernel frequency word `f`. Arm only if
   `H_max + 0.10 ms + (|f| + 0.25 ppm) · T_stream_max ≤ 5 ms`, where `H_max` = 3.60 ms (largest observed half-width)
   and `T_stream_max` is the longest continuous sampler stream of the regenerated packs, including one admission
   retry and the guards (record 44 is recomputed after regeneration). The gate is this inequality, not a fixed ppm
   number; the Opus seat's 5 ppm (for a 250 s stream) and the Sol seat's 3.5 ppm (for 320 s) are two evaluations of
   it. If the draw after G10 fails, one reviewed network-time ON/OFF redraw is allowed before `a1`; a second failure
   goes to the lead and nothing arms.
3. **T-0 anchor check in residual form** (memo 1.1, 1.21). The author, ARM, G4 replay and the G10 helper all use
   `|Δanchor − f_R0 · span| ≤ 5 ms`, plus: the kernel frequency word read at authoring equals `f_R0`, and
   `|f_R0|` passes the gate above. Any intervention by `timed` rewrites the frequency word, so the equality test
   catches slews as well as steps at any accrued offset, including right after G10. The fixed form
   `5 ms + RATE_CAP · span` (Sol seat) is not adopted: just after G10 the accrued offset is small, and at 12.5 ppm
   and 3600 s the fixed form would pass a stray resync of up to about 45 ms. Dissent recorded. G10's discharge is
   unaffected: before G10 the accrued offset since the last sync is hundreds of milliseconds.
4. **Backoff stays 0 s; one admission abort re-arms** (memo 1.14). Admission thresholds are unchanged. Exactly one
   guard-attested idle-admission abort per block, with no other RECOVER cause present, re-arms a fresh complete
   `s1` (new plan id, authorization and T-0) without END STATE and without spending `s2`. The aborted attempt's bytes
   are kept and never pooled with the fresh attempt (D-078). A second abort follows the same-refusal-twice consult
   rule. Dissent (Sol seat): allow this only when no science energy window has started yet. Not adopted: `s1` is
   non-claim and the fresh attempt collects a complete new block, so nothing is pooled or topped up. Retry as a new
   sampler stream, which would make a real backoff affordable, is deferred to block 5 (with the v3.1 identity).
5. **Census** (memo 1.15), recorded as the WO-CENSUS-SEMANTICS cure: the ARM maintenance census keeps its `pgrep`
   probe for custody and judges by CPU: it fails only on a probe error or a matching process above 5.0% CPU, the
   constant shared with `scripts/prewindow_check.sh`. A resident daemon idling at 0–0.3% is not a contaminant.
6. **Revision-5 attachment** (memo 1.16): an authenticated G2-b pre-slot route, selected when the runs root holds the
   launch lineage file, taking session and plan from that lineage and confirming through session status that the
   attached directory is that session's finalized pre slot. Measurement code; cold final pass.
7. **Detokenizer** (memo 3.1): mlx-lm's detokenizer is built once in `prepare()`, outside every measured window, and
   handed out as reset copies. This shortens prefill windows by 55–65 ms of CPU-only work. It must land before the
   seal, so that `s1` qualifies the code that collects claims; the registration carries a prospective note, and the
   claim registration states it again.
8. **G10 owner** (memo 1.5, C1): stays Ed-owned, as the registration says. Ed's 2026-10-05 email asking to make it
   agent-run could not be recorded by the headless seats (the safety classifier blocked it), so it is not applied.
