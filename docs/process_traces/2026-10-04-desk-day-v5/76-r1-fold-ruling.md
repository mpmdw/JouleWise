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

## Addendum C (2026-10-05 07:00, same seat): cold-pass findings on the integration code (PR #483)

Input: cold Fable final pass at 898c49a7, `~/night-archive/desk-day-v5/fable-int.md` (FAIL, B1 and B2 proved by
execution on the real producers).

1. **G1's registered outcomes are per argv, not one exception** (B2; corrects decision 4). The driver journals
   every governed process, including the T-0 author's own absence probes. Every `/usr/bin/pgrep` the driver or the
   author runs is an absence probe: the agent census, `pgrep -x caffeinate`, the browser and monitor censuses and
   the process-group census. Each passes G1 on exit exactly 1 with empty stdout, and its stdout must be captured
   by the journal (a `wait()` without captured output is a recording defect, not an empty answer). Every other
   governed process passes on exit 0. The registered table lives in code beside G1 and is tested against the
   real driver's journal.
2. **G9 checks the layout the night gate requires** (B1). The plan custody root and the ARM custody root are
   distinct and not nested. G9 compares the desk close-out's sources with both roots taken from the authenticated
   plan, and the backup copy set must equal exactly the set the close-out registers (both runs roots, the plan
   custody root, the ARM custody root and the night custody, whatever the code fixes), not a hand-written list.
3. **Public locators carry no timing** (M1). `replay-locators.json` keeps only paths and SHA-256 on the public side;
   the full rows with sizes and modification times go under the mode-0700 `withheld/` directory.
4. **The structural G2-b verdict does not depend on qualification artifacts** (M2). G10 custody replay belongs to the
   qualification verdict only; the G2-b harvest does not read it.
5. **The frequency gate applies to every pack that authors T-0** (M3), selected by the plan and registry profile,
   never by a pack directory name; ALPHA and BETA get it too.
6. **One composed desk test with no mock at the seams** before seal: the real journal into the real assembler into
   `evaluate_qualification`, and the real close-out output into G9, on a two-root fixture, covering G1, G3, G5, G8
   and G9.

## Addendum D (2026-10-05 10:15, desk-day seat 3): attempt history, the sealed prewindow script, G10 placement, ledger isolation, NULL recovery

Inputs: lane X6's open flags on PR #483 (`118-sol-b4-x6-report.md`: F5, P1, S1, T1) and the remaining items of the Opus
pre-mortem memo (`~/night-archive/ia-0a40/MEMO.md` 1.4, 1.6, 1.11 and 3.M).

1. **The attempt history of a block is a chain plus a census** (X6 F5). Sol's objection was that a per-attempt
   pointer cannot exclude an attempt that someone simply left out. Under D-161 the threat is an honest mistake or a
   hallucinated record, not a forger. So completeness is proven by two checks together:
   - Every `s1` attempt and the `s2` carries a required, create-once `previous_attempt` field in its authorization
     and plan. The field is either `none` (the block's first attempt only) or the path and SHA-256 of the
     immediately preceding attempt's `harvest.json`.
   - The harvester walks that chain back to `none`, authenticating each link. It then lists every attempt harvest
     of the block under the block's harvest archive root. The two sets must be equal: no fork, no orphan, no
     second `none`.

   The allowances are counted on the walked chain:
   - NULL re-arms are free;
   - at most one guard-attested admission abort re-arms (addendum B, item 4), and a second goes to the
     same-refusal-twice consult;
   - at most one `s2`, only after a named tooling RECOVER.

   Lane X7 (brief 120).
2. **`scripts/prewindow_check.sh` stays byte-identical to main** (X6 P1). The sealed Revision-6 registration pins
   it, and `scripts/issue_calibration_acceptance_generation.py` refuses a dwell whose script digest differs from
   that pin. The CPU-based census (addendum B, item 5) and the report-only load average at T-0 (memo A-F6) move into
   a T-0 dwell of the T-0 caller's own. That dwell has the same clean-dwell length and caps, and the T-0 evidence pins
   it. The night path keeps calling the sealed shell script. Consequence, stated for the seal: the night's
   pre-chain dwell judges contaminants by the sealed named-daemon list and vetoes on load average, while T-0
   judges every process by CPU. Both must pass, so the night path is the stricter one. Lane X8 (brief 121).
3. **G10 runs after `a2` and before `s1`'s T-0, scheduled by measured offset** (memo 1.4). Every T-0 arm reference
   resyncs when the sntp quorum's bound exceeds 0.5 s. Today the clock is about 1.15 s off, so `a1`'s preparation
   will resync. If G10 came first, its own preparation would do that resync, and G10's ON would then see almost
   nothing to correct.
   - G10 therefore runs after `a2`'s expiry check, on the same boot as the controls and `s1`, and before `s1`'s
     first T-0 boundary. This uses the original ruling 76 wording, "before `s1`'s T-0".
   - Its helper first measures the offset with the fixed R0 reference collector. It proceeds only when the
     quorum midpoint is at least 20 ms and the bound at most 0.400 s. At −3.17 ppm the offset grows by about
     11 ms an hour, so 20 ms accrues roughly two hours after `a1`'s resync.
   - If its preparation would resync anyway, it stops before its own ON. That outcome does not count as an
     attempt.
   - The one reviewed ON/OFF frequency redraw (addendum B, item 2) is now one per block, before whichever
     occurrence's R0 gate failed. A redraw made before G10 restarts the wait for the offset band.

   Lane X9 (brief 123). Recipe 46 is rewritten by the lead.
4. **Ledger isolation for the controls** (memo 1.6). G10's preparation, `a1` and `a2` each bind `CALIBRATION_LEDGER`
   to their own byte-exact copy of the production seed. Each copy sits outside all four ARM-context roots and
   stays unchanged until `s1`'s writer has run. Only `s1` reserves in the production ledger. Before every T-0, the
   operator recipe asserts that the production ledger's SHA-256 and the committed pin are unchanged. The memo
   checked this at API level: the controls' records re-authenticate against their copies, and production stays at
   the seed digest. No code change; registration §2 and §3.6 and the roots map carry it.
5. **NULL recovery restores the seed** (memo 1.11). A NULL `s1` attempt (no `chain.started`) leaves one open
   bracket session from its T-0 reservation. Recovery has three steps:
   - copy that attempt's ledger to custody;
   - prove that the dropped tail is exactly that one session-open row;
   - restore the seed bytes, with the pin unchanged.

   This is governed, not a copy-from-source retry: a tool does it and writes an authenticated restore record, which
   the next attempt's writer and harvester verify (lane X7). Because the pin and H do not change, `a1` and `a2` stay
   valid for the fresh attempt on the same boot. A reboot or a head change needs fresh controls, which are not
   occurrences and spend nothing. `s2` is written by the plan writer as `s1` plus the history pointer.
6. **Three watchdog tests are not a regression** (X6 T1). They failed serially only inside the Sol sandbox. The lead
   ran them outside the sandbox: 9 of 9 passed at bda1c180 and 3 of 3 at main.
7. **The magistrate watchdog makes no network call during a plan span** (memo 3.M). Its five-minute tick ran two
   HTTPS `git ls-remote` probes before checking for an active plan. Separate PR off main (lane WD, brief 122),
   because it protects every window, not only block 4.

## Addendum E (2026-10-05 10:50, desk-day seat 3): one dwell, the T-0 stage cap, and the stream bounds

Input: the sizing round-2 seat (brief 124, `~/night-archive/desk-day-v5/sol-sz2-r1.md`).

1. **Correction to addendum D, item 2: a pack night has one dwell, not two.** `scripts/run_night.py` runs the
   native six-step T-0 stage at t0, inside the window (`_capture_qualification_t0`, memo 1.9). The clean dwell is
   that stage's `prewindow-check` step. The night then binds that capture (`_admit_qualification_clean_dwell`); it
   never runs a second dwell. So for block 4:
   - the one dwell is T-0's: lane X8 makes it judge every process by CPU and record the load average without a
     veto;
   - the sealed Revision-6 `scripts/prewindow_check.sh` stays byte-identical and keeps serving derivation nights
     (`_admit_derivation_clean_dwell`);
   - the "both dwells must pass" sentence in registration §4 is withdrawn.
2. **The T-0 stage has its own cap, outside the chain's span.** Until now `T_pack_t0` was counted inside the
   programmed span, and the window added the 2700 s dwell cap again. That double-counts the stage and leaves the
   latest chain start (t0 + window − span, about t0 + 2706 s) earlier than the stage can finish when the dwell runs
   long.
   - **`T0_STAGE_CAP_S` = 3300 s**, the sizing seat's provisional value inside its band of 3180-3480 s. It is the
     2700 s dwell cap plus 600 s for the other five captures and the OFF margin.
   - `run_night.py` bounds the stage by this cap, not by 3600 s.
   - R0 to authoring then stays within G4's 3600 s ceiling: 3300 s for the stage plus the 120 s author allowance.
   - `T_pack_t0` inside the span returns to the post-stage author, verification and consuming start: 360 s.
   - `WINDOW_MAX_S = 60·ceil((NIGHT_PROGRAMMED_SPAN_S + T0_STAGE_CAP_S)/60)`, and the latest chain start is
     t0 + WINDOW_MAX_S − NIGHT_PROGRAMMED_SPAN_S, which is at least t0 + 3300 s.
   - The writer refuses a cap outside 3180-3480 s.
3. **Stream bounds.**
   - The cooldown runs on its own sampler: the main sampler stops at `joulewise/controller.py:1607` before cooldown
     begins. So the writer's stream-coverage check excludes it, and `T_stream_max` is 335 s. At today's −3.17 ppm the
     frequency gate gives 3.70 ms + 3.42 ppm × 335 s = 4.85 ms ≤ 5 ms; the largest |f| that passes is about 3.63 ppm.
   - Every anchor-bearing stream (science members, NEG-8 bound members, references, both brackets) must be at least
     60 s by allowance. Helper captures that carry no clock anchor (cooldown subwindows, the post-run sentinel) are
     exempt.

Lane X10 (brief 127) implements items 2-3. Record 44 is rewritten from the round-2 derivation.

## Addendum F (2026-10-05 12:30, desk-day seat 3): the second cold pass on PR #483

Input: the cold Fable pass at 6796b8e0 (`~/night-archive/desk-day-v5/fable-int2.md`, FAIL: B1-B3, M1, M2, L1). All
three blockers would refuse a good window after its launch was consumed, or spend Ed's G10 attempt for nothing. Each
has a cure that only makes the code agree with this ruling.

1. **Correction to addendum C, item 1: G1's registered outcomes come from the code's full roster, per exact argv.**
   Not every `pgrep` is an absence probe. The T-0 author's maintenance census
   (`pgrep -lf 'XProtect|mds_stores|...'`) lists resident daemons. It exits 0 on every real Mac, and the author
   accepts exit 0 or 1 because the CPU samples that follow decide.

   This is the second time G1's table has been wrong, and both times the cause was a hand-picked list. So the
   table is now derived from the code:
   - every governed argv the driver, the T-0 stage and the author can run;
   - with the outcomes its consuming code accepts.

   It is tested by running the real author probe roster through the real journal into G1. The R1 time-server
   query the author tolerates as a missing leg, and the driver's group-census polls, get the outcomes their
   consumers accept.
2. **G10 must reach the anchor check** (B2). The author replays the new sizing binding as it loads R0. G10's
   helper runs the real author on a copy of the inputs in its own custody, so the binding's path test refuses the
   copy before the anchor comparison.
   - The cure keeps the production author refusing on any defect, and keeps G10 running the real author
     unmodified.
   - The lane chooses the smaller of two designs, with evidence: (a) a provenance-bound copy, whose binding
     replay authenticates the original inputs path and digests; or (b) evaluating the anchor refusal before the
     binding replay, when both must pass for a PASS anyway.
   - G10's input capture also needs a staged custody of its own (`scripts/capture_t0_step.py:815-820`). The plan
     writer provides it, and recipe 46 names it.
3. **One plan id for the OFF receipt** (B3). The T-0 capture writes the network-time OFF receipt under the pack
   plan id (the frozen calibration identity), and the author reads it back the same way. The G2-b harvest and the
   desk close-out read it under the same pack plan id, never the attempt's night plan id.
4. **Allowances are judged against the nearest non-NULL predecessor** (M1). A NULL attempt spends nothing and
   changes no allowance:
   - after an `s1` tooling RECOVER and a NULL `s2`, the next attempt is the authorized `s2` again;
   - a fresh `s1` there is refused;
   - NULL `s2` records count toward nothing, and they open no new `s2`.
5. **A REFUSED harvest is superseded by its identical-bytes re-harvest** (M2). REFUSED is not a science outcome
   (registration §7). For an attempt whose original harvest is REFUSED, the history counts the newest
   `reharvest-N` verdict. The chain pointer keeps naming the original attempt record, so the chain stays stable,
   and the original is kept.
6. **Latest chain start includes the post-stage authoring** (L1). It is t0 + `T0_STAGE_CAP_S` + `T_pack_t0`, and
   the remaining chain span is the programmed span minus `T_pack_t0`. The window bound
   (t0 + `WINDOW_MAX_S`) is unchanged.
7. **The NULL restore's replay authenticates the pin bytes it recorded, not the live pin file** (L1), so a later
   pin advance cannot void the history replay of a restored attempt.
8. **The composed tests the first pass required are written now, with no mock at the seams.** They cover four
   seams:
   - the real journal into the real assembler into `evaluate_qualification`, for G1, G3, G5, G8 and G9;
   - the real author inside the real G10 helper, with the production sizing replay;
   - a G2-b harvest and a desk close-out with the night plan id different from the pack plan id;
   - the full author probe roster through the journal into G1.

Lanes X12a (items 3, 4, 5, 7 and the harvest-side composed test) and X12b (items 1, 2, 6 and the G1/G10 composed
tests), briefs 139 and 140.
