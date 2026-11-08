# Latency synthesis and v4-lean proposal (four independent Sol audits)

Synthesis of two whole-pipeline latency audits and two window-efficiency audits. Proposal only; nothing here is registered, measured or authorised. No restricted path, sealed outcome or Block-5 value was read.

**Source key** (all on `origin/perf/2026-11-08-<name>`): **L1** `docs/perf/LATENCY-AUDIT-sol1.md` (rows M01-M27 measurement, A/E analysis and engineering, "rankN" = Ranked fixes). **L2** `docs/perf/LATENCY-AUDIT-sol2.md` (inventory rows, "F1-F9" = Ranked fixes). **W1** `docs/perf/WINDOW-EFFICIENCY-sol1.md` (§2 budget, §3 overhead table, §4 A, §5 B, §6 R1 questions). **W2** `docs/perf/WINDOW-EFFICIENCY-sol2.md` (same layout). **RS** `RUN_STATE.md` item N on main. **STRAT** `docs/research/research-strategy.md`. **AF** `docs/align/squeeze/AGREEMENT-FINAL.md` @ `4526de7d5`. "My check" means I recomputed it (script in the scratchpad; formulas inline).

## 0. Bottom line

- All four seats agree there is **no evidence a valid D window can drop from hours to 1-5 h by software**. The protected decode alone is 10,240 tok / 11.9 tok/s = 860.5 s per member (bandwidth ceiling 14 tok/s gives 731 s; RS 203 R10-1), i.e. 48% of the 1,800 s member allowance, and the 300 s configured idle is another 17% (my check). Ed's rule is met for the *process* steps (desk, CI, hash/custody, kit, analysis), not for the decode.
- **"22 episodes in 16.5 h" is a reservation, not a runtime.** Programmed D span is 40,527 s = 11.26 h (4 x 782.8175 + 18 x 1,800 + 4,995, rounded up; W1 §2.2, W2 §2.1; my check). The remaining 5.28 h to the 59,520 s ceiling (RS 204 Q4) is allowances (T0 3,300, member waits 7,200, pauses 7,200) that cost nothing if unused. Real rate if windows finish near programmed span: 22/11.26 = 1.95 members/h (1.42 fresh/h) versus 1.33 (0.97 fresh) per reserved hour.
- **Biggest wins are scheduling and placement, not physics**: (1) arm on actual close, not on the ceiling; (2) desk off the MBP and out of the arm-gating path; (3) a count-only adaptive stop for calibration windows. Together they take the v4 Mac bill from about 8.5 days (reservation basis) to about 5.9-6.1 days (programmed basis), if windows really finish near programmed span (unmeasured; R1 gives the first timeline).
- Hardest unresolved item is not a speedup but a roster ruling: 3 vs 6 test windows (about 35 h).

## 1. Agreement table (class: A engineering, B registered design/arm rule, C reject)

| # | Proposed speedup | Seats | Agreement | Estimated saving and source | Class |
|---|---|---|---|---|---|
| 1 | Run desk/review/analysis on the Air while the next window measures | L1 rank2; L2 F1; W1 §4; W2 §4; RS 213 | 4/4 agree on placement. L1 also wants the desk itself shrunk (30-45 min); L2 says compute is unchanged and only leaves the MBP | Desk measured 98-103 min (pilots 10/4, L1 M23); L2 counts 100 min to 0 MBP-min. L1: 5.3-7.3 h/wk at 6 desks/wk (6 x (98-45)/60 and 6 x (103-30)/60, my check). At the cadence below (about 13 windows/wk) about 21.7 MBP-h/wk freed (my check) | A (placement); gating rule is #2 |
| 2 | Only a mechanical terminal triage gates the next arm; desk output is non-gating | RS 213 (4 MBP steps); L2 F1 ("never arm across an unresolved gate that depends on the desk"); W2 §4 | Implied by all, spelled out by L2 only | Same 100 min/window, on the MBP critical path. Risk below | **B** |
| 3 | Windows end at authenticated terminal completion; 59,520/58,260 s are ceilings | L2 "v4 W1/D chains"; W1 §4; W2 §4; L1 M17 | 4/4 agree | 59,520 - 40,527 = 18,993 s (5.28 h) per window of *reservation*, zero compute (my check). Whether the kit already returns early is unverified (W1 §4: "may already") | A in code, B in registration wording |
| 4 | Terminal-event wake of the magistrate (300 s poll to 0-30 s) | L2 F9 only | Single seat | 0.225 MBP-h/wk at 6 windows/wk (L2 F9, uniform-phase assumption) | A (MBP) |
| 5 | Finalize/hash/custody: bounded parallel hashing, incremental manifests, one compress+copy, destination re-read kept | L1 rank5, M22, M24; L2 F3 | Agree on method. Baselines differ and are all unmeasured: L1 45 to 18 min; L2 30 to 10 min (target 2-5 min finalize) | L1 2.7 h/wk, L2 2.0 MBP-h/wk, both scenario-only. Volumes: 18.71 GB/copy W1, 26.45 GB/copy D (L1 M24); two copies 37.4-52.9 GB (L2; my check), transfer floor 0.6-3.5 min | A |
| 6 | CI: land timing lane, split BYTES `test_bytes_analysis` into independent campaigns | L1 rank1, E01-E02; L2 F2 | 4/4-consistent numbers | 9,121.794 s (152.0 min) to 5,741.949 s (95.7 min) to 3,379.853 s (56.3 min) slowest shard; floor 35,409.86/12 = 49.2 min (L2 static table; my check). L1 target 55-65 min, 7.3-8.1 CI-h/wk; L2 9.39 + 6.56 CI-h/wk | A |
| 7 | Fixture/simulation profiling (MoE 1,376.959 s, run_night 108.804 s, coverage_map 2,787.918 s) | L1 rank9, E03-E05; L2 F5 | **Disagree on additivity**: L1 banks 0 beyond #6; L2 hypothesises 20-30% less ordinary work (3.3-4.9 score) | L1: MoE 22.95 to 6-12 min critical path; L2: 49.18 min x 20-30% | A |
| 8 | Phase receipts / timing-only worksheet from R1 and every window, before promising any target | L1 §R1 headline, M09; L2 F8; W1 §6; W2 §7 | 4/4 | 0 credited; prerequisite for #13, #14 and every "unknown" in §3 | A |
| 9 | Content-addressed kit regeneration; one review packet per candidate, reviews concurrent | L1 rank4, rank6, E08, E10; L2 F6 | Agree; both low-confidence | L1 45 to 21 min packet overhead (2.0 h/wk), kit 10 to 1 min; L2 0.7 h/wk | A |
| 10 | BYTES stage-1 export in isolated read workers, ordered publication | L1 rank7, A08; L2 "BYTES stage 1" | L1 targets 2.5 to 1.25 h; L2 "no defensible target" | L1 1.25 h/wk | A |
| 11 | Analysis/release dedupe under D-188 | L1 A01-A07; L2 F7 | Agree: precedent 37 h to 1 h 40 min is already banked; remainder small | L2 100 to 80-90 min/run | A (low) |
| 12 | R0 scoped retry / reuse of unchanged checks | L1 rank3; L2 F4 | **Disagree on size**: L1 3.5 to 1.25 h per retry, 4.5 h/wk; L2 15-20 min/event, 0.5-0.66 h/wk, zero if SMC-first and R0-L3 already prevent it | Bring-up only; L1 itself calls it operational acceptance, needs lead receipt | A (low); moot once R0 passes |
| 13 | Shorter per-member configured idle (300 s) | L1 "design/physics" 2; L2 "Per-member idle"; W1 §3; W2 §3 | All four: design-bound, no evidence for or against, nobody proposes it now | 300 to 120 s on 22 members: 3,960 s; 300 to 60 s: 5,280 s (13.0% of span); L1 quotes 54 min on the 18 W1 members (my check). Net is smaller if G0 grows | **B** (conditional) |
| 14 | Scaffold thinning: reuse corpus/derived bound, fewer references | W1 §3, W2 §2.3, §3; L2 (historical 6+45+12+7 min) | W1/W2 agree: decomposition of the 4,995 s is unknown, no ablation exists | Historical chain: 70 min of which corpus 45 min (L2 "Opening/closing calibration", RS item 29, not interchangeable with v4) | **B** (conditional) |
| 15 | Drop the 4 unchanged 30B anchors, or replace anchors + 2 sentinels with 4 D sentinels | W1 §3/§5; W2 §3 | W1 and W2 both keep for lean | 3,131 s (7.7% of span) if dropped; replacement saves 1,931 s at 1,200 s members but costs 469 s at 1,800 s (W2 §3; my check) | C |
| 16 | Move or remove the 8 W1 contrast members | W1 §3; W2 §6 | Agree: separate window costs more | Removal saves 8,000 s once (2.2 h, 29.7% of W1 span); separate window +1.888 h (W1 §3) or +8,126 s (W2 §6) | C |
| 17 | Count-only adaptive stop for calibration windows (min 6, cap 8) instead of a fixed number | W1 §4 (fixed 8, cap 8); W2 §4 (7, "count-only reserve" 8th); AF R13 | Seats differ 7 vs 8; adaptive rule is my synthesis of both | Expected 6.87 windows vs 8: about 1.1 windows, about 13 h at an 11.76 h cycle, under an assumed 10% iid member exclusion (my check, §3) | **B** |
| 18 | Test-cohort shape: 3 default two-pair windows vs 6 one-pair windows with 6 fit-support members each | W2 §4 vs W1 §4 | **Disagree** | Difference 3 windows = 35.3 h at 11.76 h (my check) | **B** (ruling) |
| 19 | v4-max: ungated, resident model, 1,200 s member, new estimand | W1 §5; W2 §5; L1 gen. | Agree it is a *new* experiment needing fresh F/C/T and native qualification. **Disagree on bill**: W1 186.9 h vs lean 195.1 h (-4.2%); W2 135.5 h vs 128.3 h (+5.6%) | Net about zero either way; dev/qualification windows eat the gain | C for v4 (v5 question) |
| 20 | Drop or shorten G0/G1/H holds; resident model across members | W1 §3; W2 §3; L1 M19-M20 | Agree: no evidence; sum of G0/G1/H is unknown until R1; S6 tuning (median <= 90 s, delta_slow <= 2 C) is the authorised route | Unknown | C (S6 tuning stays A) |
| 21 | Overlap offload/hash/compress with the next window on the MBP | L1 "design" 4; L2 "Overlap"; W1 §3 | Agree not admissible. L2 permits only a non-measuring host verifying an already-closed copy | Unknown | C (remote verify only) |
| 22 | SSD qualification shortcuts (3 blocks; 30 s gaps) | L1 M27, "design" 3; L2 SSD rows | Agree 3 blocks is invalid (zero residual df). L1 floats 30 s gaps: 5.83 h | 24,600 s = 6.833 h = 0.58 window cycles; 30 s gaps would save 120 x 30 = 3,600 s, giving 5.83 h (my check; L1 "design" 3) | C |
| 23 | OS batch blackout (11:45-13:15) handling | L2 (code finding), W2 §2.4; L1 M16, W1 §2.4 treat it as 5,400 s | **Disagree**; I verified W2 against `wait_outside_os_batch` (R1 script @ `e901eb2a4`, lines 980-996): a segment waits to 13:15 whenever [t, t+bound] overlaps 11:45, so wait <= bound + 5,400 s (11,164 s for step-D), not 5,400 s | R1 bound 67,371 s = 18.71 h (not 61,607 s = 17.11 h) for one encounter (my check) | B (ruling) |
| 24 | Cooler / power-mode / stand changes to cool faster | L1 "design" 1; L2 "Thermal"; W1 §3 | Agree: R1 decides use for the whole series (>= 25% rule), never toggled | Unknown | C |

## 2. Classification notes

- **A (no effect on what is measured):** 1, 3 (code side), 4-12. Land any time; none may run on the MBP during a window (magistrate activity is contention, RS 213). Item 8 is first because it is free and everything conditional depends on it.
- **B (decide before W1 registration):** 2, 3 (wording), 13, 14, 17, 18, 23. Reason: each changes window structure, member counts, dwell lengths, or an arm/admissibility rule that the prereg will freeze.
- **C reasons:** 15 loses the only cross-window drift control with measured history (pilot 6 anchors shifted -0.41%, 3.5-14.7 J, no temperature recorded; W1 §3) and saves no net time at 1,800 s members. 16 costs more than it saves. 19 and 20 change the estimand (reference-state energy to continuous serving) and need a new calibration. 21 and 24 perturb the measured power/thermal state. 22 loses residual df. None of the C items is a latency bug in Ed's sense: each is a physics or design requirement.

## 3. v4-lean proposal

v4-lean = both window seats' "A" (W1 §4, W2 §4): same 22-member frame (4 anchors, 2 D sentinels, 14 fresh benign, 2 fresh sabotage; 16 fresh), same estimand, same gates, plus the following (B) decisions.

### Recommended B items

| ID | Change | Saving | Validity cost and evidence |
|---|---|---|---|
| **B1** | Registration text: windows end on terminal completion; 59,520 s is a ceiling; next arm on committed record + quiet start state (RS 213). Stop sizing the calendar on ceilings | Calendar: cycle falls from 17.03-17.28 h (ceiling + 0.5-0.75 h turnaround) to 11.76-12.01 h; windows/day 1.41-1.39 to 2.04-2.00; members/day 31.0-30.5 to 44.9-44.0 (fresh 22.5-22.2 to 32.7-32.0) (my check). Bill, 7 C + 3 T + W1 + R1: about 203.8 h (8.5 d) on ceilings vs 146.2 h (6.1 d) on programmed span (0.75 h turnaround; my check) | **None to the measured trajectory.** Risk is only that real windows run longer than programmed (waits, G0 censoring, blackout pause). Evidence either way: **none** until R1 records exist |
| **B2** | Arm-gating set = mechanical triage only (about 5 min): meter samples and clock coverage (RS 212 R11-3), battery/charge state, power-mode restored, token identity and eligible-member count, record committed. Desk, review, analysis, kit run asynchronously on the Air. Keep desk-gating for the first window after W1 and after any code/config change | About 100 min per window leave the MBP path (L1 M23 measured 98-103 min); 12.4% of a 13.4 h cycle (my check) | A systematic fault found by the desk after the next window has started loses that window (11.3-16.5 h). Evidence the fault class is real: pilot 10 lost 3 members to 21-31 W charging and 1 to thermal level 1 (W1 §3); R0 re-runs 8-10 were refused on contention bursts, RS 205/206/208. Triage covers the charging and meter cases; it does not cover desk-only findings (e.g. wrong grading), accepted risk |
| **B3** | Calibration windows: stop on counts only (eligible benign >= 39 per pair, and the sabotage target if adopted), minimum 6 windows, hard cap 8, fixed before W1; at cap return "insufficient calibration" (AF R13; registration grade m >= 39 per pair plus held-out test, RS 204 Q6, STRAT §3) | AF's illustration (10% iid exclusion, >= 39 benign and >= 6 sabotage per pair): 6/7/8 windows complete with probability .0416/.7115/.9253; I reproduced these. Benign-only, both pairs: .147/.984/1.000. Adaptive expected windows 6.87 (6 x .147 + 7 x .837 + 8 x .016) vs fixed 8: about 1.1 windows, about 13 h | None to blinding (counts only, no alarm read). Costs interleaving flexibility between calibration and test windows. The 10% exclusion rate is AF's assumption; **no measured yield exists** |

### Conditional B items (decide before W1 registration; default is keep)

| ID | Change | Saving if it passes | Validity cost and evidence |
|---|---|---|---|
| B4 | D-member idle 300 s to 120 s (anchors stay 300 s) | 22 x 180 = 3,960 s: span 10.16 h; cycle 10.66-10.91 h; 2.25-2.20 windows/day; 49.5-48.4 members/day (my check). Net less if G0 absorbs the time | Stops controlling predecessor-heat recovery and idle-baseline admission. Evidence that 300 s helps or hurts: **none** (W1 §3, W2 §3: no 60/120/300 comparison; pilot idle stage ran 389-393 s). Evidence G0 is separately needed: R0 post-load settledness took 840-1,040 s (W1 §3) |
| B5 | Reuse the derived drift bound/corpus across back-to-back windows | Up to about 2,700 s (45 min corpus, historical chain, L2): span 10.51 h; with B4 9.41 h, 2.42-2.36 windows/day, 53.3-52.0 members/day | Stops re-deriving the drift bound per window; needs stability across setups and time. Evidence: **none** (W1 §3: no ablation of 18 candidates, stop-after-12, or 3/1/3 references; 4,995 s is an aggregate with no stage split, W2 §2.3) |

Decision rule: take B4/B5 only if the R1 offline replays (W1 §6 rows 5, 10; W2 §7 rows 3, 8) show unchanged baseline reference medians over 60/120/180/300 s sub-windows and a stage timeline that shows the saving is real, **and** the paired check in §5 D5 passes. Otherwise v4-lean stays at B1-B3.

### Resulting numbers (22 members, 16 fresh per window; my check)

| Case | Window | Cycle (0.5-0.75 h turnaround) | Windows/day | Members/day (fresh/day) |
|---|---|---|---|---|
| Today's basis: ceiling 59,520 s | 16.53 h | 17.03-17.28 h | 1.41-1.39 | 31.0-30.5 (22.5-22.2); RS 213 quotes 1.35-1.4 |
| v4-lean B1-B3, programmed span | 11.26 h | 11.76-12.01 h | 2.04-2.00 | 44.9-44.0 (32.7-32.0) |
| Same, blackout hard-avoided 1.5 h/day (22.5/cycle) | 11.26 h | same | 1.91-1.87 | 42.1-41.2 (30.6-30.0) |
| + B4 | 10.16 h | 10.66-10.91 h | 2.25-2.20 | 49.5-48.4 (36.0-35.2) |
| + B4 + B5 | 9.41 h | 9.91-10.16 h | 2.42-2.36 | 53.3-52.0 (38.8-37.8) |

Series bill (R1 at 17.11 h plus 0.5/0.75 h, W1 at 26,927 s, D windows at 40,527 s; my check): 7 C + 3 T = 143.2-146.2 h (5.97-6.09 d); with B3 expected 6.87 C: about 141.6 h at 0.5 h turnaround (5.9 d); WE1's 8 C + 6 T plan = 190.2-194.2 h (7.9-8.1 d); 6 C + 3 T is 131.4-134.2 h. WE1's own figure 195.1 h charges W1 at its 12.4 h maximum. These exclude R1 calibration brackets/harvest, retries and any redo (W1 §4, `C_R`). RS 213's "11-13 days" corresponds to ceiling-basis windows (W1 §4: 268.98 h = 11.2 d for 14 D windows at 59,520 s).

## 4. Ranked (A) engineering backlog

Ranking key: Mac-critical-path time first, then candidate turnaround, then recurring CI cost. "MBP" owner = the magistrate executes or validates it, only in gaps between windows; the Air desk writes all code.

| Rank | Item (table #) | Owner | Why here | First deliverable |
|---|---|---|---|---|
| 1 | Desk off the MBP, stage-parallel, with synthetic full-chain equivalence (#1) | Air desk (build, run); MBP only pushes the committed record | Largest recurring MBP time: 98-103 min/window; L1 precedent 903 s to 401 s on synthetic chain with exact output equality | Stage timings first (L1 rank2), then bounded workers consuming in roster order |
| 2 | R1/window timing worksheet and phase receipts (#8) | Air desk analyses; MBP exports records after close, no live instrumentation | Free, and it settles #3, #13, #14, #23 and the C_R term | Disjoint wall ledger per member (W2 §7 row 1; W1 §6) |
| 3 | Finalize/hash/push with bounded parallel hashing, incremental manifests (#5) | Air desk builds, MBP magistrate benchmarks 1/2/4/8 workers on closed files | On the MBP critical path; unmeasured baseline 5-20 min | Synthetic corruption/interruption tests, then timing at first real close |
| 4 | CI timing lane plus BYTES campaign split (#6, #7) | Air desk (cloud CI) | 152.0 to 56.3 min slowest shard. Matters whenever a frozen-code change gates an arm: one CI cycle (2.53 h) exceeds the whole 0.5-0.75 h turnaround | Land timing lane, then split 60 campaigns with all aggregate assertions kept |
| 5 | Event wake + immutable pre-arm packet built off-MBP, static checks precomputed (#4, #9) | MBP magistrate (wake, dwell, fresh checks); Air builds packets | RS 176/177: 95 min calendar from activation to launch; poll delay up to 300 s | Terminal-event trigger with the 300 s watchdog kept as fallback |
| 6 | Kit cache and concurrent review packet (#9) | Air desk | Minutes per candidate, low confidence | Cache by complete input digests, `--check` still regenerates |
| 7 | BYTES export read workers (#10) | Air desk (not the MBP; see §5 D9) | 1-4 h of serial exports | Profile restore/auth first; shared key stores forbid blind pooling |
| 8 | Fixture profiling: MoE, run_night, coverage_map (#7) | Air desk | Runner cost, not candidate wall | Profile after #4 |
| 9 | Analysis/release dedupe (#11), R0 scoped resume (#12) | Air desk | Small or moot | Only if re-run 11 fails or a release is due |

## 5. Disagreements not resolved, and what would settle them

- **D1. Expected R1 wall.** L1 M09 gives 4-8 h as an *investigation target*; L2 and both W seats see no evidence below the bound (15.61 h no-redo; 17.11 h with one wait, both reproduced). Settle: R1 phase timeline (#8). Do not shrink the reservation.
- **D2. Blackout cost.** 5,400 s (L1, W1) versus up to bound + 5,400 s (W2). I confirmed W2 from the R1 script, so R1's printed 61,607 s is not a bound. Open: do W1/D windows use the same segment-level wait or member-level admission, and must D windows avoid the blackout at all (RS 213 "respect" versus R0-L3 "record, not avoid")? Settle: `os_batch_wait_s` in R1 records plus a lead ruling. Member-level admission costs at most the 90 min blackout plus one member bound per day (about 2 h/day), segment-level can cost 3.1 h per encounter (11,164 s).
- **D3. Calibration count, 7 vs 8.** W2 7 (49/pair, 42 after a whole-window loss, 3 more losses allowed); W1 8 (39 after loss plus 20% attrition). AF's .7115 vs .9253 favours 8 only because of the >= 6 sabotage target; benign alone is .984 at 7. B3 makes this adaptive. Settle: exclusion rate in the first two calibration windows.
- **D4. Test shape, 3 vs 6 windows (B, #18).** Driven by whether R14's LOTO/full-fit asymmetry is cured by fit-support members (W1: 6 per window, so 4 honest tests left) or by a different score law. Needs a lead/statistics ruling (AF A06 owner), not a measurement. Cost of the choice: 35.3 h.
- **D5. Does 300 s idle (and G0/G1/H) reduce noise?** No seat has evidence. Reference scales: same-position repeat noise about 2 J, pair-difference SD 2.97 J, regression residual SD 19-58 J (W1 §3, W2 §3), so gates may not touch most of the misfit. Settle: after R1, a paired 30B check, idle 300 vs 120 s, 8 pairs (pair SD 2.97 J gives SE of about 1.05 J, which resolves a 2-3 J shift; my check), reading G0 wait length and baseline R as well. Costs about 2-4 h of MBP time, repaid in about 3 windows if B4 passes.
- **D6. Scaffold decomposition.** 4,995 s is one aggregate (W2 §2.3, SE `sizing_evidence`). Settle: chain-journal stage start/end in R1/W1 (R1 may not run every W1 stage, W2 §7 row 8).
- **D7. Finalize/custody baseline.** L1 45 min, L2 30 min, both assumed. Settle: timestamps at the first real close.
- **D8. R0 retry savings (#12).** 4.5 h/wk (L1) vs 0.5-0.66 h/wk (L2). Settle: whether re-run 11 passes (RS 211).
- **D9. Where BYTES stage 1 runs.** RS 213 puts it in the 30-45 min gaps; L1 A08/A09 estimates 1-4 h exports plus one to a few hours of run. It cannot fit a gap on the MBP. Recommend the Air for everything except the one-time read of archives; needs Ed/lead confirmation. Likewise the 6.83 h SSD qualification costs 0.58 window cycles (my check) and needs Ed present; payback depends on the unmeasured offload time (#5).
- **D10. Does the kit idle to the ceiling?** If any code path sleeps to the 59,520 s deadline, B1 is also an A fix. Settle: R1 `chain` journal end vs ceiling.

## Appendix: arithmetic I redid

`ceil(3131.27 + 18 x 1800 + 4995) = 40527`; W1 `ceil(3131.27 + 4 x 1150 + 4 x 850 + 6 x 1800 + 4995) = 26927`; R1 `M = 1750 + 1.13544 x 1580 + 120 = 3663.9952`, no-redo sum 56,206.96 s, +5,400 = 61,606.96, +4 x (1500 + 5763.9952) = 29,055.98 retries, step-D scheduler worst case 5,763.9952 + 5,400 = 11,163.995 (10:30 to 13:15 = 9,900 s); SSD `5 x 600 + 60 x 120 + 60 x 120 + 120 x 60 = 24,600`; probabilities from `P(Bin(7W, .9) >= 39) x P(Bin(W, .9) >= 6)` squared over two pairs, matching AF's .04157/.71149/.92526; one slight mismatch: CI method + remainder = 9,121.802 s vs module median 9,121.794 s (medians are not additive; L1 E02).
