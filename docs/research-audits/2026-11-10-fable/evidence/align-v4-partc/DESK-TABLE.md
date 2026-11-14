# Part C desk table (RUN_STATE 316; RL-145 close section 8, item 315 "After")

Built Fri Nov 13 23:48 PST 2026 (`date`) on the Air by a desk analyst for the lead. It goes to the research lead with item 314's answer (Ed chose (c)). It reads the journals of Part C OUT `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-partc-smoke-20261114T052520Z` (smoke commit `f006b7aa6`), copied read-only to `in/`. The MBP was only listed (`ls -R`) and read (`rsync`, `cat`). Nothing on it was modified or run.

Files beside this one:
- `diagnosis.json`: task 2.
- `desk.json`, `gates.csv`, `turns_row6.csv` and `tv_trigger.csv`: task 3.
- `step1_yield_partc.csv` and `step1_yield_with_partc.csv`: task 4. The original `desk-steps-1-5/step1_yield.csv` is untouched; its sha256 is still `250640e2…`.
- `step2_start_state.csv` and `step2.json`: task 5.
- `in_SHA256SUMS.txt`: the input hashes.
- `scripts/`: the scripts that wrote all of the above.

Code reused read-only:
- The build worktree `/Volumes/JW-EXT/jw-wt/mythos-keep-s` at `f006b7aa6` (clean): `thermal_gates.py` (sha256 `c72937bd…`), `rl145_prints.py`, `r1_runtime.t_decline`, `thermal_desk.thermal_exclusions`, and the Part C evaluator `scripts/align_r1_part_c.py` (sha256 `6ca41186…`).
- The B1 slot desk tool `scripts/align_r1_slot_gate_desk.py` at `04059c26e` (blob `1de627ad…`), via `git show`, executed in memory.
- `desk-steps-1-5/scripts/step1_yield.py`: `bad_pm`/`analyse` executed from its source text, unchanged.

## 1. Diagnosis of the null start-state samples: a sampler LOOKUP BUG (the wrong journal kind and schema), not stamp age and not absent data

**Cause.** `scripts/align_r1_part_c.py::_journal` keeps only rows with `kind == "sample"`, sorted by a top-level `monotonic_ns`.
- The Sidecar journal that Part C writes (`joulewise.align_thermal.v1`) has no such rows. Its readings are `kind: "reading"`, with the stamps nested in `started` and `finished` and the status in `values.status`.
- D_bank's journal holds `reading` 1,157, `align_thermal_gate` 4, `session_start` 1, `session_end` 1, and `sample` 0. The evaluator's own `_journal()`, run unchanged on the copied bundle, returns **0 rows** (X_G also returns 0).
- So `by_ns.get(exit_sample_ns)` is `None` for every release, and the first-reading search finds nothing. All four samples become `release_status`/`first_reading_after_start` = None, which prints `os_level` null, `pm_state` null and `ok` false.
- `reasons` is empty because the function adds a reason only when no G0 is released.

**What the code was meant to do.** The gate module itself (`thermal_gates.sample_rows`), the B1 desk (`project_journal`) and `thermal_desk.normalize_journal` all project `reading` rows to `sample` rows (`monotonic_ns = started.monotonic_ns`) before matching. `rl145_prints.bundle_prints` uses `normalize_journal`, which is why `printed_not_judged` shows the start states correctly. The evaluator's `_journal` skips that projection.

**Fix (row 7 change, for the builder).** `_journal` should return `thermal_gates.sample_rows(rows)` (or `normalize_journal`). Its unit tests evidently use legacy `kind: "sample"` fixtures.

**Evidence: the same lookup on the normalised rows.** Every `exit_sample_ns` matches exactly one row.

| sample (evaluator label) | time of the sample | level | state | `pm_observed_ns` age at the row stamp (s) | age at the status read (s) | 2 s rule | evaluator's own lookup |
|---|---|---|---|---|---|---|---|
| G0 release | exit sample `2623593335185291`, 110.582 s after G0 entry (gate end 0.193 s later) | 0 | Nominal | −0.0187 | +0.0001 | fresh, ok | no row (0 `sample` rows) |
| G1 release (turn 1) | exit sample `2623750328132541`, 99.690 s after G1 entry (gate end 0.130 s later) | 0 | Nominal | −0.0141 | +0.0001 | fresh, ok | no row |
| first reading after turn 0 start | 0.581 s after the start | 0 | Nominal | −0.0034 | n/a | fresh, ok | no row |
| first reading after turn 1 start | 0.868 s after the start | 0 | Nominal | −0.0035 | n/a | fresh, ok | no row |

- **Neighbouring rows.** The two rows before and after each release sample are all level 0 and Nominal. Their stamp ages run from −0.003 to −0.019 s, and TV0h equals TV1h on each.
- **Stamp age.** A negative age means the sidecar reads the status about 15 ms after the SMC read bracket starts (`thermal.py` tick). B1's RL-138 item 6 documents this.
- **Not a stamp-age effect.** No sample is anywhere near 2 s old.
- **Not absent data.**
  - The journal has `os_level` on all 1,157 rows.
  - `pm_state` is null on 429 rows: the 422 idle-baseline rows before the first state at 422.0 s (G0 entry at 422.4 s), and the 7 rows after the state stream ended.
  - The 41 rows with stamps older than 2 s all lie 16.7 to 56.7 s after turn 1's last token (section 4).
- **Re-run with a working lookup.** The evaluator's own `d_bank_start_state`, re-run on facts built from the normalised rows, returns **pass**: all four samples level 0 and Nominal, with or without the 2 s rule. X_G's 24 samples (G0, 11 G1 releases, 12 turn starts) also pass, under the 2 s rule too.
- **The verdict that would have printed.** With the bug fixed, the verdict would have been `other_failure` (mechanics: `admitted_turns` 2 < 3 only), not `start_state_failed`.

## 2. Desk table

### 2a. Step-D: addendum section 8 prints

**G0's duration and the clause last out**
- G0 recorded **209.02 s**: released, slope −0.159 °C/min, TV0h 35.020 against reference 34.745, so 0.275 °C over. TV1h is identical.
- **Clause last out, from the journal: `slope_slow`** (TV1h's 60 s slope). Its last failure was 195.77 s after entry; the bands last failed at 77.77 s, and the status clause never failed.
- At entry: TV0h 84.26 °C, slope +2.26 °C/min.
- **Caveat: a journal replay does not reproduce the recorded exit.** Using B1 `validate`, the unmodified `_wait` replayed on the journal releases at 206.0 s, against 208.77 s recorded (exit sample). Releasing needs 10 consecutive good samples. The live gate needed 13 after the last slope failure the journal shows, so it reset its count at least once on a sample the journal shows as good.
  - The same happens on D_bank's G0 (replay 102.0 s against 110.78 s, 19 samples after the last failure) and X_G's G0 (86.0 s against 90.64 s, 15 samples).
  - G1s replay correctly. X_G G1 turn 3 differs by one row, a benign batching effect: two rows arrived in one loop, and the exit sample is the later one.
  - **Likely mechanism (not established from the journal).** In `thermal_gates._wait`, `now` is stamped before `self.rows` takes the sidecar lock, and `tick()` holds that lock across the SMC read and the status read.
    - When the gate's `now` lands inside a tick, the new row comes back with `pm_observed_ns > now`. The G0 status clause's `0 <= now - pm_ns` then fails, and `consecutive` resets.
    - This applies to G0 only, because G1 and H have no status clause.
    - It is consistent with the release phases: gate end − exit sample is 0.19 to 0.25 s, with about 20 ms of loop drift per iteration over the 10 samples back to the reset sample.
    - It lengthened the three G0s by about 3, 9 and 5 s. It does not touch any verdict here.

**P4 rows.** These come from Part C step-D's `r1_classification.json`.

| key | class | eligible | clamped | resolving | baseline °C | idle mode fraction | idle distinct | max 1-s change °C | rise °C | half rise °C | half rise − max change °C | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TV0h | die | True | False | True | 34.660 | 0.0033 | 300 | 20.160 | 49.608 | 24.804 | 4.644 | model-free die step response |
| TV1h | die | True | False | True | 34.660 | 0.0033 | 300 | 20.160 | 49.608 | 24.804 | 4.644 | model-free die step response |
| TVh0 | record-only | False | False | False | 34.660 | 0.0267 | 293 | 25.0 | 49.608 | 24.804 | **−0.196** | D1(b): one-second change exceeds half the step rise; recorded only |

- TV0h's alias group is `['TV0h', 'TV1h']`.
- `night_confirmation`: ok, rule RL-145, basis `alias_group_of_fast_key`, s_fast TV0h, s_slow TV1h, reasons [].
- For the record, the classifier's own fields: `s_slow` is `Tf0B` (11-13: `TaRF`), and `selected_key_aliases` is {TV0h: [TV1h], Tf0B: []}.
- TVh0 fails D1(b) by 0.196 °C (11-13 failed it by 0.297 °C). It is not clamped this time: idle mode fraction 0.027.

**P2 row.** Definitions are p2p3.py's, on the episode clock. Clock rows come from `extract_gpu_clock` (section 6).
- Prefill: 98.88 s, 19,458 tokens. Decode: 340.42 s, 12.03 tok/s.
- First-10-s median clock: 1,380.0 MHz (88 rows). Last-512 clock: 1,135.1 MHz.
- **Last-512 clock ratio: 0.823.**
- Last-512 token-rate ratio: 0.983 by p2's definition, 0.973 by `rl145_prints`'.
- Registered t_decline: 99.18 s from the turn start (0.30 s from the first token, "declined"; the base-ramp artefact).
- OS levels in decode: {0: 127, 1: 23, 2: 190}. PM states: {Nominal 127, Moderate 23, Heavy 190}.
- What fires: OS/pm and the clock clause (0.823 < 0.90).
- 256-block ratios: 0.980, 1.000 ×6, then 0.926, 0.939, 0.943, 0.902, 0.871, 0.856, 0.842, 0.826, 0.819.

**P6 values**

Base and registered scan:
- Base: 88 rows, median 1,380.0 MHz, threshold 1,338.6 MHz.
- Registered scan rows: 0.300 s (token 3) at 1,337.8 MHz, then 0.413 s (token 5) at 1,262.0 MHz.
- Registered `t_decline`: 99.177 s from the turn start (declined).

After-base scan:
- The first row after the base ends at 10.066 s.
- Rows 149.01 s (token 1,805) at 1,321.5 MHz and 149.12 s (1,807) at 1,289.0 MHz.
- After-base t_decline: **149.01 s from the first token, 247.89 s from the turn start**. 88 of 88 rows were under threshold in the next 10 s.
- The first 256-block under 0.97 is block 7 (tokens 1,792 to 2,047), ratio 0.926.

Marks (seconds from the first token, with the token):
- TV0h ≥ 93.0 °C: 115.8 s (token 1,404; 93.02).
- Level 1: 127.8 s (token 1,549; Moderate).
- Level 2: 150.8 s (token 1,826; Heavy).
- Order: TV0h ≥ 93 → level 1 → decline (149.0) → level 2.

N_chunk:
- Formula, print only (r_decode 12.031 tok/s): registered 512; after-base counted from the turn start 1,536; after-base counted from the first token 1,024.
- Configured: 4,096 (row 2, "candidate, not adopted").

**P7 time.** Times are from the last token. The in-run journal runs to 84.35 s; there is a gap from 84.35 to 133.03 s; the recovery journal runs from 133.03 to 601.03 s.
- At the last token: level 2, Heavy, fresh (−0.015 s).
- **Level 0 for 5 readings: 56.36 s.**
- **Level 0 and Nominal for 5 readings: not reached.** With the 2 s rule: also not reached.
- The last fresh state was **Heavy at 20.36 s** (age 1.82 s).
- From 21.36 to 77.36 s, `pm_state` stays "Heavy" on a stale stamp (age rising linearly to 58.8 s). From 78.35 s it is null.
- The recovery journal (469 rows) records no status.
- The first sample within 1.0 °C of the G0 release (35.02 °C) is at 144.04 s, on the recovery journal with no status. P3's five-sample band starts at the same point: 144.04 s.

### 2b. Every gate: replay, clause last out, and the release sample under the 2 s rule

| member | gate | turn | outcome | recorded s | journal replay s | clause last out (journal) | last fail s: band_fast / band_slow / slope_slow / status | entry TV0h | release TV0h (ref) | slope at release | release sample: level / state / stamp age s / 2 s rule |
|---|---|---|---|---|---|---|---|---|---|---|---|
| step_D | G0 | 0 | released | 209.02 | 206.0 (differs) | slope_slow | 77.77 / 77.77 / 195.77 / - | 84.26 | 35.020 (34.745) | -0.159 | 0 / Nominal / -0.0184 / ok |
| D_bank | G0 | 0 | released | 110.78 | 102.0 (differs) | slope_slow | - / - / 91.58 / - | 35.51 | 34.615 (34.745) | -0.148 | 0 / Nominal / -0.0187 / ok |
| D_bank | G1 | 1 | released | 99.82 | 100.0 | band_fast (tie band_slow) | 94.71 / 94.71 / - / - | 85.91 | 35.565 (34.615) | -6.596 | 0 / Nominal / -0.0141 / ok |
| X_G | G0 | 0 | released | 90.64 | 86.0 (differs) | slope_slow | - / - / 75.44 / - | 35.25 | 34.707 (34.745) | -0.129 | 0 / Nominal / -0.0198 / ok |
| X_G | G1 | 1 | released | 56.99 | 57.0 | band_fast (tie) | 51.25 / 51.25 | 48.95 | 35.625 (34.707) | -16.925 | 0 / Nominal / -0.0115 / ok |
| X_G | G1 | 2 | released | 34.62 | 34.0 | band_fast (tie) | 28.78 / 28.78 | 42.26 | 35.609 | -0.286 | 0 / Nominal / -0.0103 / ok |
| X_G | G1 | 3 | released | 60.20 | 60.0 (one row; batching) | band_fast (tie) | 54.17 / 54.17 | 47.98 | 35.613 | -13.175 | 0 / Nominal / -0.0168 / ok |
| X_G | G1 | 4 | released | 36.74 | 37.0 | band_fast (tie) | 31.48 / 31.48 | 42.14 | 35.637 | -0.545 | 0 / Nominal / -0.0197 / ok |
| X_G | G1 | 5 | released | 44.92 | 45.0 | band_fast (tie) | 39.90 / 39.90 | 42.95 | 35.634 | -3.741 | 0 / Nominal / -0.0130 / ok |
| X_G | G1 | 6 | released | 50.06 | 50.0 | band_fast (tie) | 44.58 / 44.58 | 43.07 | 35.627 | -7.278 | 0 / Nominal / -0.0107 / ok |
| X_G | G1 | 7 | released | 32.72 | 33.0 | band_fast (tie) | 27.26 / 27.26 | 37.73 | 35.635 | -0.180 | 0 / Nominal / -0.0179 / ok |
| X_G | G1 | 8 | released | 58.32 | 59.0 | band_fast (tie) | 53.02 / 53.02 | 47.47 | 35.629 | -11.675 | 0 / Nominal / -0.0127 / ok |
| X_G | G1 | 9 | released | 40.93 | 41.0 | band_fast (tie) | 35.14 / 35.14 | 42.05 | 35.655 | -1.294 | 0 / Nominal / -0.0151 / ok |
| X_G | G1 | 10 | released | 34.73 | 34.0 | band_fast (tie) | 28.98 / 28.98 | 37.95 | 35.631 | -0.246 | 0 / Nominal / -0.0115 / ok |
| X_G | G1 | 11 | released | 34.82 | 35.0 | band_fast (tie) | 29.44 / 29.44 | 37.94 | 35.638 | -0.303 | 0 / Nominal / -0.0139 / ok |

D_bank gates + holds = 110.78 + 99.82 = **210.59 s** (0.214 × T_dead 983.10; limit 393.24 s). There is no H record, as N_chunk 4,096 implies.

### 2c. Close section 7 row 6 prints, D_bank and X_G (2 s stamp rule applied)

**(i) The W1 desk's per-turn flags and exclusion reasons**
- `os_nominal` and `pm_nominal` follow the `thermal_desk` rule, over turn start to turn end plus tool calls.
- They are computed on the 1 Hz journal's `os_level` and `pm_state`, not on native powermetrics rows, so the desk's `pm_nominal` could differ only for sub-second excursions.
- **D_bank:**
  - Turn 0: os_nominal True, pm_nominal True.
  - Turn 1: **False / False**.
  - `thermal_exclusions` gives **['thermal.os_level_nonzero', 'thermal.powermetrics_non_nominal']**, so the member is excluded (X1, X3) under the registered rule. Under RL-148 section 2's (c) text, X1 and X3 no longer exclude a D member; they are printed only.
  - Member flags were not read (`align_episode.json` was not copied).
- **X_G:** all 12 turns True / True. Exclusion reasons: none.

**(ii) Section 2 prints.** See 2d.

**(iii) Per-turn prefill, decode and continuous load**

| member | turn | prefill tokens | prefill s | decode tokens | decode s | continuous load s (prefill + decode) | decode bin | stop |
|---|---|---|---|---|---|---|---|---|
| D_bank | 0 | 10,021 | 48.58 | 103 | 8.21 | 56.79 | <=1024 | stop |
| D_bank | 1 | 11,211 | 60.59 | 4,096 | 341.62 | 402.21 | >2048 | requested_tokens_emitted |
| X_G | 0 | 7,102 | 6.04 | 1,339 | 18.06 | 24.10 | 1025-2048 | stop |
| X_G | 1-11 | 27 to 2,230 | 0.37 to 3.11 | 229 to 658 | 3.7 to 10.0 | 4.2 to 12.9 | <=1024 | stop |

The residual binned by continuous load needs `residual_j` (energy), so it is **not printed**: blind.

**(iv) The TV1h ≠ TV0h trigger.** See 2e.

**(v) Token times from the token events (`events.jsonl`; no deadman, so `align_runtime_events.jsonl` does not exist)**

| member/turn | base clock MHz | clock ratio by 256-block | last-512 clock ratio | last-512 token-rate ratio | first off (level/state; s after first token; token) | level 1 / level 2 (token) | decode OS level counts |
|---|---|---|---|---|---|---|---|
| D_bank 0 | 1,315.3 | 0.994 (partial) | n/a (<512) | n/a | none | none | {0: 9} |
| D_bank 1 | 1,380.0 | 1.000 ×8, 0.997, 0.985, 0.955, 0.931, 0.911, 0.896, 0.877, 0.874 | **0.8752** | **0.9732** | **1/Moderate; 102.28 s (162.87 s after the turn start; not in prefill); token 1,234**; TV0h 89.15 | 1,234 / 1,523 | {0: 102, 1: 24, 2: 216} |
| X_G 0 | 1,380.0 | 0.9997 to 0.9999 | 0.9998 | 0.9915 | none | none | {0: 18} |
| X_G 2 | 1,380.0 | 0.9998 | 0.9998 | 0.9976 | none | none | {0: 10} |
| X_G 7 | 1,380.0 | 0.9998 | 0.9998 | 0.9964 | none | none | {0: 10} |
| X_G other turns | 1,380.0 | 0.998 to 0.9999 | n/a (<512 tokens) | n/a | none | none | all level 0 |
| step-D 0 (for reference) | 1,380.0 | as P2 | 0.8225 | 0.9731 | 1/Moderate; 127.77 s; token 1,549 | 1,549 / 1,826 | {0: 127, 1: 23, 2: 190} |

**Cross-check against the evaluator.** On the evaluator's own uniform-token estimate, these clock rows reproduce `printed_not_judged` for D_bank turn 1. The last-512 ratio is 0.8751257 (printed 0.8751257385725489), and the block ratios agree to 3 decimals. So the clock extraction and the clock mapping (journal-vs-turns offset within 0.7 µs) match `native_pm_samples`.

The evaluator's first_off (Moderate at token 1,223) came from native PM rows at about 8.6 Hz with uniformly spread tokens. The 1 Hz journal plus real stamps gives token 1,234.

### 2d. Close section 2: replacement evidence (the gated D_bank run)

**At every G1 release sample.**
- D_bank had one G1, before turn 1. At its release sample: **level 0, Nominal, stamp age −0.014 s (fresh)**, TV0h = TV1h = 35.565 °C. That is 0.950 °C over the episode reference 34.615.
- For completeness, the G0 release sample: level 0, Nominal, age −0.019 s.
- There was no G1 after turn 1: the episode ended at turn 1 (see section 5).

**Per turn: from the last token to the first of five consecutive readings at level 0 and Nominal on a fresh stamp (≤ 2 s), and TV0h at that reading.**
- **Turn 0** (103 decode tokens after a 48.6 s, 10,021-token prefill):
  - 0.79 s; TV0h **82.25 °C**.
  - The OS never left level 0 or Nominal, with the die at 82 to 86 °C (G1 entry TV0h 85.91 °C).
- **Turn 1** (4,096 tokens, the hot one): **not reached within the journal** (63.7 s after the last token).
  - Level 0 first comes back at 53.67 s.
  - The last fresh state is Heavy at 15.67 s (age 1.93 s). From 16.66 to 56.67 s the journal carries "Heavy" on a stale stamp (age up to 42.9 s), then null.
  - The next fresh observation is X_G's G0 entry, 531.56 s after the last token: level 0, Nominal, TV0h 34.98 °C.
- **The state is unobserved after a long turn.** In every member (step-D at 20.4 s, D_bank at 15.7 s, X_G's last turn at 14.9 s) the powermetrics state stops refreshing 15 to 20 s after the last token, and its stamp then ages linearly.
  - This confirms the Opus seat's caveat: the "Heavy" P7 saw at 69 s and 135 s on 11-12 and 11-13 was a stale stamp.
  - Under the 2 s rule, the question "is the OS back at Nominal once the die is back in band?" **cannot be answered from these journals.** At the last fresh reading after a 4,096-token turn the state is still Heavy. The first fresh reading after it, 8 to 17 minutes later, is Nominal.

### 2e. The TV1h ≠ TV0h trigger (close section 5)

**As fixed ("any journal row inside a gate window"): NOT fired.** All 15 gate windows (entry to end) of step-D, D_bank and X_G have 0 rows with TV1h ≠ TV0h. Step-D, X_G, the step-D recovery journal and the soak (1,800 rows) have 0 in total.

**Two rows outside any gate window** (D_bank), where TV1h ≠ TV0h at the raw bytes:

| member | seq | where | TV0h | TV1h (hex) |
|---|---|---|---|---|
| D_bank | 588 | turn 0 decode, 2.00 s after the first token (token 24); 6.30 s before G1 entry, so inside G1's 60 s look-back but outside the gate window. G1 has no slope clause. | 84.7495 | **85.0000** (`0000aa42`) |
| D_bank | 760 | turn 1 decode, 3.28 s after the first token (token 39) | 89.8877 | **90.0000** (`0000b442`) |

- Both rows sit on a steep rise: the readings before them are 81.26 and 85.70 °C, the readings after 85.06 and 90.13 °C, and the two keys are equal again on both neighbours.
- On both rows TV1h reads an exact multiple of 5 °C.
- So the alias is not byte-identical on every row of a gated member. The DEVIATIONS draft says "identical in every field of the three D steps on record", which still holds for Part C's step-D: 0 of 1,552 rows. For the research lead.

## 3. RL-148 step 1: yield rows for Part C

- Same script logic (`analyse`, unchanged).
- Wall clock; a reading's time is `finished.wall_ns`.
- (d) and (e) start windows at first token + 10 s; (d20) and (e20) at + 20 s.
- Part C's gated runs now have clock rows, so (c) to (e) are computed for them.

| run | turn | prefill s | prefill tok | decode tok | gap last L0 → first >0 (s) | base MHz | (a) first OS level >0 | (b) first PM state not Nominal | (c) after-base scan (record only) | (d) trailing-10 s < 0.97 base, from t0+10 | (d20) | (e) < 0.97 top state (1,380), from t0+10 | (e20) | D_bank slot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| step-D | 0 | 98.88 | 19,458 | 4,096 | 0.997 | 1380.0 | 127.8 s; tok 1549; TV0h 93.3; D′ 1550; **0.378** | same as (a) | 149.0 s; tok 1805; TV0h 97.7; D′ 1806; **0.441** | 10.1 s; tok 121; D′ 122; **0.030** (window artefact) | 152.6 s; tok 1848; TV0h 97.9; D′ 1849; **0.451** | 10.1 s; **0.030** (artefact) | 152.6 s; D′ 1849; **0.451** | |
| D_bank | 0 | 48.58 | 10,021 | 103 | no reading above 0 | 1312.8 | none (D′=D=103, share 1) | none | none | none | none | none | none | a_os D′=103/103 |
| D_bank | 1 | 60.59 | 11,211 | 4,096 | 0.998 | 1380.0 | **102.3 s; tok 1234; TV0h 89.2; D′ 1235; 0.302** | same as (a) | 208.2 s; tok 2507; TV0h 89.0; D′ 2508; **0.612** | 216.5 s; tok 2606; TV0h 89.0; D′ 2607; **0.637** | same as (d) | same as (d) | same as (d) | a_os D′=1235/4096 |
| X_G | 0-11 | 0.37-6.04 | 27-7,102 | 229-1,339 | no reading above 0 | 1380.0 | none (share 1) on every turn | none | none | none | none | none | none | |

**The D_bank slot.**
- In `step1_yield_with_partc.csv`, the 11-13 D_bank rows' `D_bank_Dprime_slot` now reads "Part C turn 0: a_os D′=103/103 (share 1.0)" and "Part C turn 1: a_os D′=1235/4096 (share 0.3015)". The Part C rows carry their own (a) D′.
- The prefill does not cut (`prefill_cut` = no on every Part C turn).
- (a) and (b) fire on the same reading again.
- The gap of 0.997 to 0.998 s is the 1 s journal cadence.
- On D_bank turn 1, (a)/(b) come 106 to 114 s before any clock cut, and that clock cut is the first one: (c) 208.2 s, (d)/(d20)/(e)/(e20) 216.5 s. The clock declines only after level 2 has persisted for about 80 s.

## 4. RL-148 step 2: start state after a hot turn

**Every turn after the first (0-based index ≥ 1): the first reading after the turn's start, and the clocks from the previous turn's last token.**

| member | turn | previous turn (decode tok; left level 0?; max TV0h) | G1 before the turn s | first reading: s after start; level / state; stamp age s; 2 s rule | last token → level 0 s | last token → Nominal (fresh) s | → five L0+Nominal+fresh s (TV0h there) |
|---|---|---|---|---|---|---|---|
| D_bank | 1 | 0 (103; no; 85.91) | 99.82 | 0.868; 0 / Nominal; −0.0035; ok | 0.79 | 0.79 | 0.79 (82.25) |
| X_G | 1 | 0 (1,339; no; 53.67) | 56.99 | 0.255; 0 / Nominal; −0.0045; ok | 0.29 | 0.29 | 0.29 (53.07) |
| X_G | 2 | 1 (371; no; 42.65) | 34.62 | 0.157; 0 / Nominal; −0.0041; ok | 0.82 | 0.82 | 0.82 (42.65) |
| X_G | 3 | 2 (658; no; 48.75) | 60.20 | 0.969; 0 / Nominal; −0.0043; ok | 0.21 | 0.21 | 0.21 (48.19) |
| X_G | 4 | 3 (314; no; 42.49) | 36.74 | 0.742; 0 / Nominal; −0.0047; ok | 0.52 | 0.52 | 0.52 (42.49) |
| X_G | 5 | 4 (477; no; 45.08) | 44.92 | 0.963; 0 / Nominal; −0.0055; ok | 0.94 | 0.94 | 0.94 (43.36) |
| X_G | 6 | 5 (495; no; 47.35) | 50.06 | 0.509; 0 / Nominal; −0.0045; ok | 0.63 | 0.63 | 0.63 (47.35) |
| X_G | 7 | 6 (235; no; 42.00) | 32.72 | 0.540; 0 / Nominal; −0.0038; ok | 0.30 | 0.30 | 0.30 (42.00) |
| X_G | 8 | 7 (623; no; 47.73) | 58.32 | 0.686; 0 / Nominal; −0.0041; ok | 0.13 | 0.13 | 0.13 (47.73) |
| X_G | 9 | 8 (315; no; 42.96) | 40.93 | 0.198; 0 / Nominal; −0.0035; ok | 0.18 | 0.18 | 0.18 (42.37) |
| X_G | 10 | 9 (229; no; 42.38) | 34.73 | 0.233; 0 / Nominal; −0.0041; ok | 0.03 | 0.03 | 0.03 (37.95) |
| X_G | 11 | 10 (264; no; 43.33) | 34.82 | 0.617; 0 / Nominal; −0.0040; ok | 0.48 | 0.48 | 0.48 (42.22) |

**The turn after a turn that left level 0: none exists in Part C.**
- D_bank's only hot turn (turn 1, 4,096 tokens) was its last. It was cut at the 4,096-token turn cap inside an unclosed reasoning span (flags `turn_token_budget_reached:1`, `unclosed_reasoning_span`, `reasoning_censored_at_token_limit`).
- With no tool call, `workload.py` ends the episode (`if not result.tool_calls: break`). No G1 or turn 2 followed.
- What the journals give after each long turn, from the last token:

| leg | journal after last token s | → level 0 s | → Nominal fresh | last fresh state (s; age) | stale-stamp span s (value) | next journal: first fresh state |
|---|---|---|---|---|---|---|
| step-D (4,096) | 84.35 (+ recovery 133 to 601, no status) | 56.36 | not observed | Heavy (20.36; 1.82) | 21.36 to 77.36 ("Heavy", age to 58.8) | D_bank: 0 / Nominal at 1,029.0 s (its G0 entry) |
| D_bank turn 1 (4,096) | 63.66 | 53.67 | not observed | Heavy (15.67; 1.93) | 16.66 to 56.67 ("Heavy", age to 42.9) | X_G: 0 / Nominal at 531.6 s (its G0 entry; journal starts at 116.6 s with level 0, state unobserved) |
| X_G turn 11 (231) | 58.88 | 0.88 | 0.88 | Nominal (14.89) | 14.89 to 51.89 ("Nominal", stale) | n/a |

**Step-2 result.**
- Every turn that followed a turn which stayed at level 0 started at level 0 and Nominal on a fresh stamp (12 of 12, first reading 0.16 to 0.97 s after the start).
- That includes D_bank turn 1, which followed a prefill-heavy turn that took the die to 85.9 °C without leaving the reference state.
- **No turn in Part C followed a turn that left level 0.** After the two 4,096-token legs, level 0 returned at 53.7 s and 56.4 s. Nominal on a fresh stamp was never observed within the journal: the state stream stops refreshing 15 to 20 s after the last token, while it still reads Heavy.

## 5. Against the close section 8 predictions (and addendum section 6's printed ones)

| # | prediction (fixed before the run) | observed | holds? |
|---|---|---|---|
| 1 | Step-D's G0 releases on the slope clause in 100 to 220 s | 209.02 s; clause last out `slope_slow` (last failing 195.8 s) | **yes** |
| 2 | D_bank turn 1 leaves level 0 before token 2,048, and the desk's rule excludes the member | left at token 1,234 (level 1/Moderate, 102.3 s after the first token); level 2 at token 1,523; `thermal_exclusions` = os_level_nonzero + powermetrics_non_nominal | **yes** |
| 3 | The G1 after turn 1 takes more than 120 s | **No G1 after turn 1**: the episode ended at turn 1 (cut at 4,096 tokens in reasoning, no tool call). The G1 before turn 1 took 99.82 s, after a turn that stayed at level 0 | **not observable** |
| 4 | The run fails its mechanics: gates above 398.3 s, or the deadman before a third turn ends | Mechanics failed, but **on neither named ground**: gates + holds 210.59 s (limit 0.40 × 983.10 = 393.24 s; the close assumed T_dead 995.79), no deadman (episode 670 s of 983 s). The failure is `admitted_turns` 2 < 3, from the episode ending | **failure yes, mechanism no** |
| 5 | X_G passes | 12 turns, no X7, no G1 timeout; all 12 release samples level 0 / Nominal / fresh | **yes** |
| 6 | No prediction on the state at each G1 release sample | D_bank's one G1: level 0, Nominal, stamp age −0.014 s (fresh) | observation |
| A6 | Addendum section 6, printed: level 2 before token 2,048 | token 1,523 | **yes** |
| A6 | last-512 clock ratio 0.83 to 0.93 | 0.8752 (real stamps); 0.8751 (evaluator, uniform estimate) | **yes** |
| A6 | token-rate ratio ≥ 0.98 | **0.9732** (real stamps; the evaluator printed null) | **no** |
| A8 | Addendum section 8 (for the Part A smoke): the replay predicted the G0 at 212 s | Part C's step-D G0: 209.02 s | close |

## 6. Method notes, deviations and blinding

**Clock rows (task 1).**
- `extract_gpu_clock.py` hard-codes the 11-12 and 11-13 night paths and its segment list, so it cannot run byte-unchanged on this OUT. `scripts/extract_gpu_clock_partc.py` keeps its three per-row extraction lines byte-identical and changes only the input loop.
- It ran **on the Air**. The input is the same file the original reads, `rich_telemetry.jsonl` (the raw plist was not needed), streamed with `ssh mbp-ts cat … |` into the extractor, so that file was never stored on the Air.
- The output is `in/gpu_clock.jsonl`: per row only `timestamp_s`, `elapsed_ns` and the dvfm (freq, used_ns) pairs, for step-D, D_bank and X_G. As in P2, each row is parsed whole in memory and no other field is emitted.
- The clock rows reproduce the evaluator's own printed ratios (section 2c(v)).

**Copied** (hashes verified against the MBP, 17 of 17, mode 444): `events.jsonl`, `align_turns.jsonl`, `align_thermal.jsonl` and `align_window_reference.json` of step-D, D_bank and X_G (predecessor: `events.jsonl` and `align_turns.jsonl`); the step-D recovery journal; `r1_classification.json`; the soak's `align_thermal.jsonl` and `soak_reference.json` (sha256 `decfc428…`, equal to the receipt's); `runner_receipt.json`.
- `align_runtime_events.jsonl` and `align_failure.json` do not exist in this OUT: no deadman.
- **Not copied or opened:** `smoke_part_c.json`, `smoke.json`, `runtime_result.json`, `align_episode.json`, `load_journal.json`, `summary_metrics.json`, `power_trace.csv`, `rich_telemetry*` (beyond the streamed dvfm extraction), raw plists, `hazards/meter`, `meter_*`, transcripts, `soak_row.json`, `inventory_journal.jsonl`.

**Fields read.**
- `align_turns.jsonl`: stamps, clock-mapping offset, `prefill_tokens`, `prompt_tokens`, flags, stop conditions, and the **length** of `output_token_ids`. No id was printed or decoded.
- `runner_receipt.json`: only its key names were listed.

**Disclosure.** While mapping `events.jsonl`, one exploratory dump printed the D_bank `stage_completed idle_baseline` metadata, including its `power_w_mean` value (an idle-baseline stage mean). It was not used, is in no desk file, and is not repeated here.

**Definitions.**
- Stamp age is taken at the sample's row stamp (B1's convention). Negative ages are about 10 to 20 ms: the status is read just after the SMC bracket.
- "Five consecutive" means adjacent journal rows no more than 2 s apart.
- `os_nominal`/`pm_nominal` come from the 1 Hz journal.
- The D_bank exclusion uses `thermal_exclusions` on those turn observations, without member flags.
