# Research-lead bundle after Part C (2026-11-13/14), for RL-149
Prepared by the laptop lead. Everything here is read-only material; nothing is merged or armed. Ed's standing decisions this evening are in A0.

## A0. Ed's decisions on record (do not re-ask)
- RUN_STATE 314: option (c) (keep K, reword). 
- /Volumes/JW-EXT/scratch/cadence-decisions/ED-DECISIONS-1113.md: stay Automatic + ~12-leg High Power arm in calibration; measurement_mode with XProtect + Wi-Fi ON (applied 23:47, see C4); no ambient logger (home 72-78 °F; use start Tf08).
- Ed approved the throughput plan's top three cadence changes and the principle "design next blocks before the current ones finish; blocks quick and modular" (memory). Ed wants the instrument validated for S as hard as possible (NOT a registration change promoting S).
- Ed: use more Mythos seats for design/risk; you remain the research lead whose rulings are on record.

## A. Part C (RUN_STATE 316) — your close §8 asks you to rule on the table
- Desk table: /Volumes/JW-EXT/scratch/partc-desk/DESK-TABLE.md (+ diagnosis.json, desk.json, CSVs). Headline: the start_state_failed verdict is an evaluator lookup bug (`align_r1_part_c.py::_journal` reads only kind=="sample"; the Part C journal is kind=="reading"); fixed, start state passes; only admitted_turns 2 of 3 fails. Predictions table. P7: OS state stops refreshing 15-20 s after the last token (earlier "Heavy" = stale stamp). TV1h≠TV0h: 0 rows in gate windows, 2 rows in D_bank decode outside gates. G0 replay 3-9 s earlier than recorded (timestamp race hypothesis).
- RL-148 step 1 yield extended (step1_yield_with_partc.csv) and step 2 (step2_start_state.csv).
- For you: the S row's three constants (state definition, clock clause, guard) per RL-148 §1/§3; whether step 3 opens now; G_turn / U1 timeout line / typical-case bar per RL-148 §2; the row-7 fix.

## B. S design (RL-148 follow-ups)
- Desk steps 0 + 6 (truncated bundles; row builder, branch align/2026-11-13-s-rows fdff00b82): /Volumes/JW-EXT/scratch/v4-s-rows/REPORT.md — six open questions (edge uncertainty: all boundaries vs cut ends, quadrature vs linear, edge_j; T3 clock-window start; T1 carry-in stamp age; leg-max reference; rl145_prints fallback; Sol family build).
- Desk step 4 simulation: /Volumes/JW-EXT/scratch/desk-step4-s-oc/REPORT.md (+ tables.md): idea 1 holds ≤ .031-.036; whole-turn S leaks .224 at −50 %/+15 %; idea 5 companion; K threshold rises with heat.
- Desk steps 1 + 5: /Volumes/JW-EXT/scratch/desk-steps-1-5/REPORT.md (pilot-7 length ratio 1.374).
- Ed's steelman of heat-modelled whole-turn S: Sol /Volumes/JW-EXT/scratch/steelman-s/MEMO-sol.md + MEMO-sol-delta.md; Mythos MEMO-mythos.md + MEMO-mythos-delta.md; onset-from-start-state desk /Volumes/JW-EXT/scratch/desk-onset-predict/REPORT.md. Both seats: register S_w (work+start-state heat model, fitted on conditionless data, frozen pre-W1) beside the rows; a label-free rule on holdout data picks the primary; rows default.
- Extra analyses Ed asked for: heat-as-signal (MEMO-mythos-heat.md) and unused data (MEMO-mythos-unused.md) — candidate frozen exploratory prints, positive controls (scripted hidden work, CPU burn), memory-pressure logging.

## C. Calibration campaign + cadence (Ed approved the direction)
- Measured throughput: /Volumes/JW-EXT/scratch/throughput-plan/REPORT.md (MBP measured 19 % of 6 days; leg 19.3 min fast G0 / 29-33 min heatsink-bound; Part C G0 209 s on TV1h = fast column).
- Cadence designs: Opus builder (branch ops/2026-11-13-cadence-queue b0ddd73a9 + 637ff6b5d; design doc docs/process/cadence_queue_design.md on that branch) vs Sol (/Volumes/JW-EXT/scratch/cadence-sol/MEMO-sol.md); 4 differences listed in the builder's doc §11. Rulings it needs: RL-119/122 standing authorization over a finite queue; RL-143 item 1 counted pilot; RL-127 term 6; RL-128 term 2/3; the doc's §12 questions.
- OS limits: /Volumes/JW-EXT/scratch/mythos-os-limits/REPORT.md; MBP inspection /Volumes/JW-EXT/scratch/mbp-inspect/REPORT.md: the 11:45-13:15 blackout has no cause now (dasd batch moved to ~02:08; XProtect standard scan 02:08-02:25) -> propose moving the blackout to ~02:00-02:35 (ruling 8 / RL-72 E2); prefill and decode kernels at ~84-85 % of measured ceilings (no engine change before W1).
- C4 measurement_mode applied on the MBP (verify OK; Spotlight agents disabled, effective next restart; battlimit unset).
- Needed from you: the campaign ruling (legs, bands by history, the HP arm, length-only control pairs, scripted hidden-work / CPU-burn positive controls, block definition, inclusion/stop rules, interim look, freeze, energy-read rule, rehearsal-energy disclosure), the standing authorization, the blackout move, and the block-design pipeline (BLOCK-QUEUE ledger on the cadence branch).

## D. Blinding: latent desk leak (REAL, nothing leaked)
- Audit: /Volumes/JW-EXT/scratch/desk-leak-audit/VERDICT.md. Guard built: branch align/2026-11-13-v4-desk-seal 1756c73c8 (allowlist; withheld + sha256; released() needs series_complete + receipt; harvest-off triage route also sealed). Re-sign needed (three bound files + new module + two RL-145 files already unbound on base).
- Questions: (a) W1 scope (builder recommends withholding W1 sabotage GPU/outcomes too); (b) T scores after calibration_complete vs B0 (builder: release only); (c) pooled figures as built + add the desk to the pre-C1 seal list; confirm the three beyond-brief calls (benign DC sealed in C/T; R22-3 balance sealed in C/T; flag codes kept).

## E. Disclosures
- The Part C desk analyst's exploratory dump displayed one idle_baseline power_w_mean of the conditionless D_bank rehearsal member (unused; in no output).
- Mythos seats ran read-only and blind; one Sol seat's sandbox had no per-file deny list (blinding by instruction).
