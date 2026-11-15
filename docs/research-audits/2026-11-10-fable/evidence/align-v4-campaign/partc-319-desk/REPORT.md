# The first Part C at f30a97d00 (items 319/322): the lead's desk table and RL-156 §4.2 hand checks

Saved by the lead from the desk builder's hand-back on 11-14. Thermal values only. Full detail is in desk319.json, reeval.out and recorded_eval.json in this directory.

## Hand checks
1. **Blackout bound: HELD.**
   - Launch 16:43:46; soak 16:48:49-17:18:49; part C 17:18:50-18:42:26; close 18:42:40.
   - Soak start + 11,360 s = 19:58:09, before 02:00.
   - Launch + 12,180 s = 20:06:46, before 01:30.
2. **X_G's episode_flags is a list: TRUE.**
3. **Re-evaluation with #783's evaluator (561f4dd05):** verdict pass, all lines pass, "CHECK3: same verdict and lines". The full evaluation object differs in 0 fields.

## Desk table, summary
- **Step-D:** G0 207.91 s released, clause slope_slow. The release sample is level 0, Nominal and fresh.
- **Turn:** 19,458 + 4,096 tokens, 438.7 s. Level 1 at 230.8 s, level 2 at 253.8 s.
- **Gates:** all 15 released, with release samples at level 0, Nominal and fresh. The replay agrees on 13 of 15; two X_G G1 replays are one row off, with no verdict effect.
- **D_bank:**
  - G0 104.72 + G1 96.94 s = 0.205 × T_dead, against the 394.2 s limit.
  - Turn 1: 11,211 + 4,096 tokens; first off at 202.9 s (the evaluator says token 1,710); excluded for powermetrics_non_nominal.
- **X_G:** 12 turns, all level 0 and Nominal, no exclusion.
- **TV1h ≠ TV0h trigger:** not fired. There are 0 unequal rows inside gate windows; 3 outside, at D_bank seq 583, 584 and 752, where TV1h snapped to 85.0 or 90.0.
- **Soak:** reference sha 9442b655…45c5; TV0h = TV1h = 34.182 °C.

## FOR THE RESEARCH LEAD
- **No differing verdict line under RL-156 §4.2 item 3.** #783's evaluator reproduces the evaluation exactly.
- **Observations, for information only:**
  - (a) After a hot 4,096-token turn, the OS state stream stops refreshing 15-20 s after the turn end, still reading Heavy. A return to Nominal on a fresh stamp stays unobservable, as it was in 316.
  - (b) The alias pair snapped on 3 D_bank rows outside the gates; 2 of them are in G1's look-back.
  - (c) Two X_G G1 replays are one row off.
  - (d) D_bank turn 1's clock ratio (0.935) and token-rate ratio (0.979) printed just outside item 315's predicted ranges. They are printed, not judged.
- **Scope:** the P2/P6 clock prints and the N_chunk formula were not built (thermal-only brief).
