# R1 follow-up night: after-the-night block and report (magistrate 80851129)

Headless magistrate 80851129 (Opus 5.5), 2026-11-12 from 22:08 PST. Procedure: the "After the night" block of `docs/process_traces/2026-11-12-air-offline-handoff/arm-item-draft.md`, with S=`/Users/edr/night-align/r1fu-20261112T223055Z` and PKT_SHA=`8d63766da71bcc85ade0a60672758793fe8b3c3a490dad405c948a85f232eab9` (arm trace `MAGISTRATE-ARM-a30af3e5.md`).

## Check lines (run by me)

- `r1_result.json`: `status complete error None`; `chain exit_code 0`; D-7 packet `8d63766d…eab9` == PKT_SHA: True. Executed commit `99622e96cf83d578672747a90db1d8128a57eae9`.
- `result.json`: chain_outcome COMPLETE, chain_exit_code 0, fault false, census_hits [], 865 censuses. Driver started 14:51:03, `chain.exited` 22:07:36, chain wall 25,622 s.
- Runbook §4: (1) `arm_align_r1.py uninstall --custody-root $S` rc 0; only `com.joulewise.magistrate` loaded, no night plist on disk. (2) `pmset -g custom`: powermode 0. (3) no `km003c_monitor.py`, `hazard_monitor.py` or root `powermetrics` alive. (4) KM003C capture present: `$S/hazards/meter/stream-001.jsonl`, 77,859,935 B, 129,712 lines, 25,942 s, bad 0, usb_errors 0, stopped by signal 15, supervision `proven_stopped true`.
- Network time: the driver's host restoration set it ON at 22:07:42 (`next_arm_owns_zeroing: true`). The draft says leave it OFF for W1, so I set it OFF at about 22:20 (`systemsetup -setusingnetworktime off`; read back Off). The kernel frequency word was not touched; the next arm zeroes it (item 251).
- No agent was alive on this Mac during the window (this activation spawned at 22:08:18, after `chain.exited`).

## Report (temperatures and structure only; R1 is a rehearsal)

Compiled read-only by a Sonnet investigation agent from the custody tree; scripts under `/tmp/jw-80851129/agent/` (not kept). `thermal_gates.py` and `r1_runtime.py` in the measurement checkout are byte-identical to `99622e96c` (sha256 `c72937bd…`, `472aff96…`). I re-checked by hand: the G0 rule in `joulewise/align/apple/thermal_gates.py` (night-custody tree) is a ONE-SIDED band (`sample <= reference + delta`) ANDed with `|slope| <= 0.2 °C/min`, os_level 0 and pm_state Nominal, for 10 consecutive samples; `r1_runtime.py:516` bars `0 <= t_band_s <= 300`; the step-D G0 record's reference is fast 34.9074 / slow 35.0184, duration 906.65 s.

### Dispositions under the arm draft

- **RL-89 margin: goes to the research lead.** The only failed thermometry clause on D is Th0C's return time (t_band_s 315.2 s against 300 s; tau 83.8 s, rise 43.0 °C; the files print only the generic five-family message, so this is a clause-by-clause evaluation). Step-D's G0 released (906.6 s), but two G0s on the pair timed out (planning R+4C, R+2C) and three G1s hit the 300 s turn cap (`thermal.gate_timeout` in D_spam a, D_spam b, X_G). The draft says the pick stands only if all released, so it does not stand here.
- **RL-72 E4 A-B-A: bars pass; High Power NOT adopted.** All 12 cross-band rows pass (smallest margin 0.398 °C, B slow vs A1); B's slow reference 32.523 lies inside [29.414, 33.303]. t_decline A1 98.665 / B 98.845 / A2 98.856 s against 1.25 × max(A1, A2) = 123.57 s: verdict `not_adopted`.
- **RL-91: wrapper in; 0 `capture_reaps` records** anywhere under $S, so no capture failed. Ticker: one sub-0.5 s gap in 2,413 ticks (step_30b, 0.04 %); 0 elsewhere; no member over 1 %.
- **Flags:** `r1.g0_timeout_run` 6 occurrences (2 members); `r1.g0_cap_saturated` does not exist in the files or the code; `inconclusive_segments` = {R+2C, R+4C: g0_timeout_run; thermometry.D: thermometry_failed}. Also `planning_temperature` inconclusive, `u5` inconclusive, `duty_bar` fail; `g0_cap_w1` = 740 s.
- **For the research lead, beyond the asked items:**
  1. Because the band is one-sided, six releases sit 2.0 to 5.3 °C BELOW the reference on Th0C (B, A2, D, D_bank, D_spam a/b, X_G); those gates waited on the slope clause, not on reaching the reference. Whether "at or below" is the intended start state is a ruling question.
  2. The step-D window reference is captured at warmup entry: inside its 60 s span Th0C falls 35.29 → 34.64 and then rises to 37.80 in the last 13 s (heater start), so the stored 35.018 median is not a settled value.
  3. D_bank failed by its member deadman (`episode.deadman`, T_dead 918.19 s: G0 591.4 + G1 269.9 + prefill 48.5 + decode 8.2 s).
  4. `align_window_reference.json` lists Tf08 under `record_keys` but stores no Tf08 value; the Tf08 references below are derived (median over the same span; the same derivation reproduces the stored fast/slow values exactly).
- **Lead's desk (item 7):** `align_r1_followup_kit.py desk --run-dir "$S/night/align-r1"` not run (the lead's). Nothing from `r1_slots.json` is committed.

The full tables follow.

---

All values from `/Users/edr/night-align/r1fu-20261112T223055Z/night/align-r1/` (called `$A`). Nothing modified. Scripts: `/tmp/jw-80851129/agent/*.py`.

## Headline

1. 12 G0s: 10 released (340-998 s), 2 timed out at 1,200 s (planning R+4C, R+2C). Waits: 30b 971.5, A1 650.3, B 850.1, A2 820.3, D 906.6, R+4C 1200.05 TO, R+2C 1200.05 TO, R+0C 997.7, D_bank 591.4, D_spam_a 466.9, D_spam_b 445.4, X_G 339.9. No other G0 exists.
2. The deciding condition is NOT recorded anywhere. The gate code makes band and slope an AND (band is one-sided: sample <= ref + 1.0), so 6 of 9 window-reference releases land 2.0-5.3 C below reference on Th0C (30b +0.95, A1 +0.57). Step members' references are not settled values.
3. Reconstructed last-to-clear: slope for A1/B/A2/D/D_bank/D_spam/X_G, band for step_30b. Both timeouts: Th0C kept crossing ref+1.0 (longest all-good streak 5 and 9 of 10 required).
4. Tf08: not stored in any window reference (null); derived step-D Tf08 ref 34.964 C. Tf08 at release 27.9-30.6 C for the step/high_power/D_bank/D_spam/X_G members, 35.4-39.6 C for the planning members; at G0 entry 33.7-70.8 C.
5. Thermometry D: files name only the generic 5-family message; by evaluation the only failing clause is return time, t_band_s 315.2 s > 300 s (tau 83.8, noise 0.0377, rise 43.0).
6. high_power: not_adopted, t_decline A1/B/A2 = 98.665/98.845/98.856 s vs threshold 123.57; start_state_bars pass, slow_capture_bracket true, smallest cross-band margin 0.398 C.
7. capture_reaps: 0 records anywhere. Ticker (load_journal cpu_busy ticks and SMC thermal ticks): 1 sub-0.5 s gap in 2413 (step_30b), 0 elsewhere; max fraction 0.04%.
8. `r1.g0_timeout_run` x6 (2 members x3 places); `r1.g0_cap_saturated` x0 (string does not exist in files or code); inconclusive_segments = {R+2C, R+4C: r1.g0_timeout_run; thermometry.D: r1.thermometry_failed}.

## 1. Every G0 (chronological, 12 rows; r1_result.g0_waits lists exactly these 12; capture_predecessor_30b has no G0)

Sources: G0 record = `<seg>/runs/<run>/events.jsonl` line `event_type=phase_end, phase=align_thermal_gate, message=G0`, field `metadata` (D_bank: same record in `outputs/align_runtime_events.jsonl`, because that member failed). Duration/outcome also in `<seg>/runtime_result.json` `g0_wait_s`, `g0_outcome`, and `r1_result.g0_waits[]`. `reference` = metadata.reference (the reference the gate actually used); `release` = metadata.release; slope = metadata.slope_c_per_min (OLS of Th0C over the preceding 60 s at the last loop pass; for a timeout it is the slope at the cap).

| segment | outcome | duration s | gate reference fast / slow (source) | release fast TV0h / slow Th0C | release - ref fast | release - ref slow | slope at release C/min | deciding condition recorded? |
|---|---|---|---|---|---|---|---|---|
| step_30b | released | 971.5 | 34.128 / 26.858 (own window ref) | 34.238 / 27.812 | +0.109 | +0.954 | -0.185 | null: no field |
| high_power_A1 | released | 650.3 | 34.429 / 29.914 (own window ref) | 34.482 / 30.488 | +0.053 | +0.574 | -0.173 | null: no field |
| high_power_B | released | 850.1 | 34.678 / 32.523 (own window ref) | 34.494 / 30.517 | -0.185 | -2.006 | -0.139 | null: no field |
| high_power_A2 | released | 820.3 | 34.706 / 32.803 (own window ref) | 34.484 / 30.337 | -0.222 | -2.466 | -0.114 | null: no field |
| step_D | released | 906.6 | 34.907 / 35.018 (own window ref) | 34.504 / 30.629 | -0.403 | -4.389 | -0.152 | null: no field |
| planning_R+4C | timeout | 1200.0 | 150.000 / 39.018 (designed R+k (fast=150 i.e. fast band off)) | 35.262 / 40.149 | -114.738 | +1.131 | -0.006 | null: no field |
| planning_R+2C | timeout | 1200.1 | 150.000 / 37.018 (designed R+k (fast=150 i.e. fast band off)) | 35.150 / 38.010 | -114.850 | +0.992 | +0.007 | null: no field |
| planning_R+0C | released | 997.7 | 150.000 / 35.018 (designed R+k (fast=150 i.e. fast band off)) | 34.978 / 35.951 | -115.022 | +0.932 | -0.100 | null: no field |
| D_bank | released | 591.4 | 34.907 / 35.018 (step-D window ref) | 34.461 / 30.143 | -0.447 | -4.876 | -0.085 | null: no field |
| D_spam_a | released | 466.9 | 34.907 / 35.018 (step-D window ref) | 34.465 / 30.134 | -0.442 | -4.884 | -0.051 | null: no field |
| D_spam_b | released | 445.4 | 34.907 / 35.018 (step-D window ref) | 34.442 / 30.005 | -0.466 | -5.014 | -0.107 | null: no field |
| X_G | released | 339.9 | 34.907 / 35.018 (step-D window ref) | 34.419 / 29.714 | -0.488 | -5.304 | -0.169 | null: no field |

**Which condition decided the release: not recorded.** None of events.jsonl G0 record, runtime_result.json, controller.log (2 lines per member: started/succeeded), r1_result.json carries a field for it; the G0 record has only outcome, reference, release, slope_c_per_min, entry_slope_c_per_min, entry_sensors, exit_sample_ns. From the gate code the run used (`/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/joulewise/align/apple/thermal_gates.py` `_wait`, lines ~563-590; byte-identical to `/Users/edr/code/jw-wt/r1-followup-smoke/.../thermal_gates.py`, sha256 c72937bd...918), G0 releases when 10 consecutive 1 Hz samples are ALL good, where good = (TV0h <= ref_fast + 1.0) AND (Th0C <= ref_slow + 1.0) AND (|60 s OLS slope of Th0C| <= 0.2 C/min) AND os_level == 0 AND pm_state == 'Nominal' (+ continuity/coverage >= 0.9). So (a) the band is ONE-SIDED (upper edge only; a sample far below reference is in band) and (b) band and slope are an AND, not an either/or; the brief's "band OR slope" does not match this code. This is why the B, A2, D, D_bank, D_spam and X_G releases sit 2.0 to 5.3 C below the reference on the slow sensor (30b and A1 released 0.95 and 0.57 C above it, inside the upper edge). Cap = 1,200 s (`g0_timeout_s`).

Reconstruction (mine, not recorded): replaying each member's `outputs/align_thermal.jsonl` over [start_ns, end_ns] with those rules (slope re-computed as OLS over the preceding 60 s; script `/tmp/jw-80851129/agent/binding.py`). `last band-bad` / `last slope-bad` = seconds into G0 of the last sample violating that condition; the later one is the condition that was last to clear.

| segment | first sample with band ok s | last band-violating sample s | last slope-violating sample s (abs slope > 0.2) | last-to-clear condition | frac samples band ok | frac slope ok |
|---|---|---|---|---|---|---|
| step_30b | 958.1 | 961.1 | 915.1 | band | 0.013 | 0.37 |
| high_power_A1 | 561.7 | 560.7 | 639.7 | slope | 0.137 | 0.015 |
| high_power_B | 388.1 | 387.1 | 839.1 | slope | 0.544 | 0.012 |
| high_power_A2 | 337.9 | 336.9 | 809.9 | slope | 0.589 | 0.012 |
| step_D | 247.4 | 246.4 | 896.4 | slope | 0.728 | 0.011 |
| planning_R+4C | 71.5 | 1199.5 | 1070.5 | band | 0.564 | 0.894 |
| planning_R+2C | 132.4 | 1195.4 | 180.4 | band | 0.559 | 0.849 |
| planning_R+0C | 215.4 | 987.4 | 262.4 | band | 0.504 | 0.736 |
| D_bank | 40.5 | 39.5 | 580.5 | slope | 0.932 | 0.019 |
| D_spam_a | 33.2 | 32.2 | 456.2 | slope | 0.929 | 0.021 |
| D_spam_b | 28.1 | 27.1 | 435.1 | slope | 0.937 | 0.025 |
| X_G | 0.2 | null | 329.2 | band never violated; slope | 1.0 | 0.032 |

Reading: step_D, high_power A1/B/A2, D_bank, D_spam a/b, X_G were band-ok from 0.2-562 s into the wait and waited on the slope clause until the slow sensor stopped falling faster than 0.2 C/min; step_30b cleared band last (Th0C first <= ref+1 at 958 s). The two timeouts (R+4C, R+2C) and the R+0C release are band-edge cases: Th0C hovered around ref_slow+1.0 (see 1c).

### 1b. Tf08 at release and the Tf08 reference

`align_window_reference.json` has `sensors.record_keys = ["Tf08"]` but NO Tf08 value (it stores only fast_c, slow_c and 60 [t, TV0h, Th0C] samples). Tf08 reference is therefore **null in the files**. Derived (mine): median of Tf08 over the same 60 s `span_ns` rows of the segment's own `outputs/align_thermal.jsonl` `values.sensors.Tf08`; the same derivation reproduces the stored fast_c/slow_c exactly for all five window references (check passed). Tf08 at release = journal row with `started.monotonic_ns == exit_sample_ns` (its TV0h and Th0C equal the recorded release values in all 12 cases; match = true).

| segment | Tf08 at release | Tf08 reference used (derived) | release - ref |
|---|---|---|---|
| step_30b | 27.863 | 26.742 (own window ref) | +1.121 |
| high_power_A1 | 30.416 | 29.832 (own window ref) | +0.584 |
| high_power_B | 30.394 | 32.303 (own window ref) | -1.909 |
| high_power_A2 | 30.279 | 32.783 (own window ref) | -2.504 |
| step_D | 30.633 | 34.964 (own window ref) | -4.332 |
| planning_R+4C | 39.591 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | +4.626 |
| planning_R+2C | 37.392 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | +2.428 |
| planning_R+0C | 35.406 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | +0.442 |
| D_bank | 30.091 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | -4.874 |
| D_spam_a | 30.056 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | -4.908 |
| D_spam_b | 29.914 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | -5.051 |
| X_G | 29.631 | 34.964 (step-D window ref (planning rows: designed start state has no Tf08 ref; shown vs step-D for comparison)) | -5.334 |

Tf08 has no band in the gate (the gate reads only TV0h and Th0C); the values above are record-only.

## 2. Tf08 at member start minus the step-D window reference, and band headroom at each release

Step-D window reference (`step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d/outputs/align_window_reference.json`): fast_c = 34.907400131225586, slow_c = 35.01839828491211, span_ns [2519566332418146, 2519626332418146], rule median over 60 s anchored at warmup_entry, coverage_fraction 1.0, Tf08 value: null (not stored). Derived Tf08 reference (median of journal Tf08 over that span) = **34.964375** C.

"Member start" = first `kind=reading` row of the member's `outputs/align_thermal.jsonl` (about 0.03 s after session_start, seconds after the member launched; before warmup). G0 entry = `metadata.entry_sensors.Tf08` (about 55-71 C for the step, high_power and planning members, 34-40 C for D_bank, D_spam and X_G).

| segment | Tf08 member start | start - 34.964 | Tf08 at G0 entry | entry - 34.964 | TV0h / Th0C at member start |
|---|---|---|---|---|---|
| step_30b | 26.985 | -7.979 | 55.359 | +20.395 | 33.866 / 27.194 |
| high_power_A1 | 34.296 | -0.668 | 69.148 | +34.184 | 34.391 / 34.128 |
| high_power_B | 43.299 | +8.334 | 70.197 | +35.233 | 35.819 / 42.766 |
| high_power_A2 | 45.434 | +10.470 | 69.148 | +34.184 | 35.840 / 45.518 |
| step_D | 64.118 | +29.154 | 70.760 | +35.796 | 56.780 / 61.286 |
| planning_R+4C | 34.468 | -0.496 | 69.696 | +34.732 | 34.938 / 34.644 |
| planning_R+2C | 35.970 | +1.006 | 70.202 | +35.237 | 35.014 / 36.467 |
| planning_R+0C | 35.862 | +0.897 | 69.599 | +34.635 | 35.007 / 36.440 |
| D_bank | 43.139 | +8.175 | 40.074 | +5.110 | 35.812 / 42.513 |
| D_spam_a | 42.730 | +7.766 | 40.097 | +5.132 | 35.606 / 43.116 |
| D_spam_b | 41.598 | +6.633 | 39.236 | +4.272 | 35.470 / 41.907 |
| X_G | 41.513 | +6.549 | 33.672 | -1.292 | 35.471 / 41.830 |

### 2b. Band headroom at each release

Two definitions, both from the recorded reference and release in table 1. (i) Symmetric, as asked: band - |release - ref| with band = 1.0 C (`bands_c.delta_fast_c/delta_slow_c` in runtime_result.json); negative = outside a two-sided band. (ii) One-sided, which is what the gate code and `aba_start_bars` (`scripts/align_r1_rehearsal.py` line 1471, `margin_c = reference + band - reading`) use: ref + 1.0 - release; negative = above the upper edge. For the planning rows fast ref is 150 (designed), so fast headroom is not meaningful (shown as n/a).

| segment | symmetric fast | symmetric slow | one-sided fast | one-sided slow | ok under gate rule (one-sided)? |
|---|---|---|---|---|---|
| step_30b | +0.891 | +0.046 | +0.891 | +0.046 | yes |
| high_power_A1 | +0.947 | +0.426 | +0.947 | +0.426 | yes |
| high_power_B | +0.815 | -1.006 | +1.185 | +3.006 | yes |
| high_power_A2 | +0.778 | -1.466 | +1.222 | +3.466 | yes |
| step_D | +0.597 | -3.389 | +1.403 | +5.389 | yes |
| planning_R+4C | n/a | -0.131 | n/a | -0.131 | NO (timeout, last sample) |
| planning_R+2C | n/a | +0.008 | n/a | +0.008 | yes |
| planning_R+0C | n/a | +0.068 | n/a | +0.068 | yes |
| D_bank | +0.553 | -3.876 | +1.447 | +5.876 | yes |
| D_spam_a | +0.558 | -3.884 | +1.442 | +5.884 | yes |
| D_spam_b | +0.534 | -4.014 | +1.466 | +6.014 | yes |
| X_G | +0.512 | -4.304 | +1.488 | +6.304 | yes |

### 2c. Release minus the step-D window reference for every segment (comparability; fast 34.9074, slow 35.0184)

| segment | TV0h - 34.907 | Th0C - 35.018 |
|---|---|---|
| step_30b | -0.670 | -7.207 |
| high_power_A1 | -0.426 | -4.530 |
| high_power_B | -0.414 | -4.502 |
| high_power_A2 | -0.424 | -4.681 |
| step_D | -0.403 | -4.389 |
| planning_R+4C | +0.355 | +5.131 |
| planning_R+2C | +0.243 | +2.992 |
| planning_R+0C | +0.071 | +0.932 |
| D_bank | -0.447 | -4.876 |
| D_spam_a | -0.442 | -4.884 |
| D_spam_b | -0.466 | -5.014 |
| X_G | -0.488 | -5.304 |

### 1c. Why the two planning timeouts timed out (reconstruction, `/tmp/jw-80851129/agent/g0diag.py`)

| segment | designed slow ref + 1.0 (upper edge) | Th0C at last sample | samples band-ok / all-good (of 1200) | longest all-good streak (needs 10) | Th0C min..max last 300 s | (os_level, pm_state) |
|---|---|---|---|---|---|---|
| planning_R+4C | 40.018 | 40.149 (0.131 above) | 677 / 639 | 5 | 39.518 .. 40.927 | (0, Nominal) x1200 |
| planning_R+2C | 38.018 | 38.010 (0.008 below) | 671 / 634 | 9 | 37.636 .. 38.516 | (0, Nominal) x1200 |
| planning_R+0C (released, 998 s) | 36.018 | 35.951 | 503 / 464 | 10 | 35.721 .. 36.399 | (0, Nominal) x998 |

Both timeouts: Th0C (the heater-held slow sensor) first got under the upper edge at 71.5 s (R+4C) and 132.4 s (R+2C), then kept crossing it; no 10-sample all-good streak formed in 1,200 s. Fast sensor was never the issue (ref 150). Power-management state was Nominal throughout. Recorded: `runtime_result.json` `g0_outcome=timeout`, `g0_release_c = null`, `episode_flags` include `thermal.start_gate_timeout` and `r1.g0_timeout_run`; heater `preheat`: R+4C `threshold_reached true`, `heater_stop_ns` 2523702701557104 (about 0.01 s after G0 end_ns 2523702690515437).

## 3. Thermometry, segment D (Th0C)

Files: `r1_result.json` `thermometry.D` and `thermometry.flags/bar`; `step_D_prefill_10k_decode_4096/inventory/r1_classification.json` (`classification.ranking[key=Th0C]`, `night_confirmation`); admissibility code `joulewise/align/apple/r1_runtime.py` `sensor_admissibility()` (lines ~500-520, night-custody tree).

What the files name (verbatim): `r1_result.thermometry.D.reasons` = `["s_slow: Th0C is not admissible on D (rise/noise/return-time/R0/quality)"]` (identical in `night_confirmation.reasons`, one string, nothing else; `classification.reason` is absent); `night_confirmation.ok = false`, `thermometry.bar = "fail"`, `thermometry.status = "fail"`, `thermometry.flags = ["r1.sensor_inadmissible"]`; `r1_result.inconclusive_segments["thermometry.D"] = "r1.thermometry_failed: research lead ruling required"`. **The files do not name a single failed clause**; the message lists all five clause families in one string. The Th0C ranking row says `class = "record-only"`, `eligible = false`, `reason = "not in a resolving/releasable D4/D5 role; recorded only"`.

Clause-by-clause evaluation (mine, applying the exact test in `sensor_admissibility` to the Th0C row of r1_classification.json; role s_slow, noise_max 0.15):

| clause in code | field in the Th0C row | value | bar | pass? |
|---|---|---|---|---|
| key in R0 keys | r1_result.thermometry.D.r0_sensors.s_slow | Th0C | = Th0C | yes |
| unit degC | unit | degC | degC | yes |
| not above junction / not clamped / not heat-ordering-excluded | above_junction, clamped, heat_ordering_excluded | false, false, false | false | yes |
| resolving (rise) | resolving, observed_rise | true, 43.036 C | true (rule: rise >= 3 C, > 3 noise floors) | yes |
| noise | noise (noise_floor 0.05) | 0.03768 C | <= 0.15 | yes |
| return time (band hold) | **t_band_s** | **315.218 s** | 0 <= t_band_s <= 300 | **NO (15.2 s over)** |
| tau | tau_s | 83.789 s | 0 <= tau_s <= 300 | yes |
| quality (phase coverage / read errors) | phase_coverage idle/load/recovery; phase_read_error_fraction | 1.0 each; 0.0 each | >= 0.99; < 0.01 | yes |
| alias of fast pick | alias_groups | Th0C aliases only Th0D; TV0h only TV1h | not in same group | yes |

t_band_s is tau x ln(rise / 1 C) = 83.7894 x ln(43.0356) = 315.218 s (reproduced). **Yes: the only failed clause is return time** (`t_band_s` 315.2 s against the 300 s bar), by this evaluation; the other four families pass with margin, and the files themselves do not say which clause failed. The fast pick TV0h passes (t_band_s 89.2, tau 22.8, noise 0.0105 vs 1/3). Context: the same classification ranks different keys (s_fast Tf1B, s_slow Tf38, `sensor_pick_changed: true` inside the classification file, `heat_ordering_wide_exclusion: true`); r1_result.thermometry.D reports `sensor_pick_changed: false`, `registered_picks {Tf1B, Tf38}` because RL-78 confirms the fixed smoke pair (TV0h, Th0C) without consulting the new rank. `thermometry.30B_record_only`: status "fail", reasons ["null pick: s_slow"], flags [] (record-only, not in inconclusive_segments).

## 4. r1_result `high_power`

(`r1_result.json` key `high_power`; per-leg values from `high_power_*/runtime_result.json`.)

- verdict: `"not_adopted"`; reason: `"t_decline(B) < 1.25 x max(A1, A2)"` (rule `high_power_adoption` in `scripts/align_r1_rehearsal.py`, gain 1.25).
- `t_decline_s`: A1 98.664529732, B 98.844763169, A2 98.855789088 (all `t_decline_status = declined`). Threshold 1.25 x max(A1, A2) = 123.570 s; B is 0.99989 x max(A1, A2).
- `g0_released` and `leg_g0_released`: A1 true, A2 true, B true (leg run order A1, B, A2).
- `start_state_bars.pass = true`; `slow_capture_bracket = true` (rule: min(A1,A2 slow ref) - 0.5 <= B slow ref <= max(A1,A2 slow ref) + 0.5; slow window refs A1 29.914, B 32.523, A2 32.803, so interval [29.414, 33.303] contains 32.523).
- `start_state_bars.cross_band` (12 rows, all pass). `margin_c` = other leg's window-reference + band(1.0) - this leg's G0 release, i.e. one-sided headroom to the upper edge (formula at `scripts/align_r1_rehearsal.py` line 1471; I verified A1-vs-B fast: 34.6784 + 1 - 34.4817 = 1.1967):

| leg | against | fast margin_c | slow margin_c |
|---|---|---|---|
| A1 | B | 1.1967 | 3.0349 |
| A1 | A2 | 1.2243 | 3.3145 |
| B | A1 | 0.9350 | 0.3976 |
| B | A2 | 1.2121 | 3.2859 |
| A2 | A1 | 0.9454 | 0.5773 |
| A2 | B | 1.1949 | 3.1859 |

Smallest margin: 0.3976 C (leg B slow vs A1). Per-leg operating references (runtime_result `operating_reference`): A1 34.429 / 29.914; B 34.678 / 32.523; A2 34.706 / 32.803 (fast / slow).

## 5. Powermetrics orphan wrapper (RL-91) and ticker

**capture_reaps**: `grep -rc capture_reap` over all of `/Users/edr/night-align/r1fu-20261112T223055Z` (all files, incl. every `metadata.json`, `*.jsonl`, `*.log`, `runtime_result.json`, `r1_result.json`): **0 records, null for every member.** Telemetry adapter was the reaping class (`joulewise/adapters/__init__.py` `resolve_telemetry` always imports `powermetrics_reap.ReapingPowermetricsTelemetryAdapter`; `logs/telemetry.log`: "resolved telemetry adapter 'powermetrics'"). In `joulewise/adapters/powermetrics_reap.py` `_reap_capture` the only writer of `device_metadata["capture_reaps"]`, it runs only when a capture fails or the probe fails, so an empty set means no powermetrics capture failed in any member (consistent: every member's `metadata.json adapters.telemetry` has no capture_reaps key; the only "reap" hit in metadata is `uncertainty_evidence.process_group_teardown.leader_reaped true`, a different record). Corroboration: the process `census` (start and end) in each of the 20 `runtime_result.json` lists no `powermetrics` process.

**Ticker**: no file named ticker/ticks exists. I used two 1 Hz journals and counted inter-tick gaps below 0.5 s. (A) `<seg>/load_journal.json` `cpu_busy_t_s` (cpu_busy_cores sampler; per segment, one member each). (B) `runs/*/outputs/align_thermal.jsonl` `kind=reading` rows, `started.monotonic_ns` (SMC sampler).

| segment | (A) ticks | (A) gaps < 0.5 s | (A) fraction | (B) ticks | (B) gaps < 0.5 s |
|---|---|---|---|---|---|
| step_30b | 2413 | 1 (0.357 s) | 0.00041 | 1925 | 0 |
| high_power_A1 | 1754 | 0 | 0 | 1701 | 0 |
| high_power_B | 1976 | 0 | 0 | 1915 | 0 |
| high_power_A2 | 1946 | 0 | 0 | 1886 | 0 |
| capture_predecessor_30b | 550 | 0 | 0 | n/a (no thermal journal) | n/a |
| step_D | 2766 | 0 | 0 | 2304 | 0 |
| planning_R+4C | 2367 | 0 | 0 | 2293 | 0 |
| planning_R+2C | 2372 | 0 | 0 | 2296 | 0 |
| planning_R+2C.precool | 116 | 0 | 0 | n/a | n/a |
| planning_R+0C | 2149 | 0 | 0 | 2080 | 0 |
| planning_R+0C.precool | 122 | 0 | 0 | n/a | n/a |
| D_bank | 1431 | 0 | 0 | 1414 | 0 |
| D_spam_a | 1337 | 0 | 0 | 1297 | 0 |
| D_spam_b | 1313 | 0 | 0 | 1274 | 0 |
| X_G | 1173 | 0 | 0 | 1138 | 0 |
| idle_soak | 1800 | 0 | 0 | n/a | n/a |
| harvest / cooldown_after_D / pre- and post_calibration_bracket | 3 / 1 / 0 / 0 | 0 | n/a (too few) | n/a | n/a |

No member exceeds 1% (maximum 0.041%, step_30b), so no time-weighted load statistics were required or computed. Median gap is 0.9994-1.0000 s everywhere; minimum gap in (A) other than step_30b is 0.552 s (step_D), maximum 1.537 s (step_30b).

## 6. Flag counts in r1_result.json (recursive search, `/tmp/jw-80851129/agent/flags.py`)

| string | occurrences | locations |
|---|---|---|
| `r1.g0_timeout_run` | 6 | `inconclusive_segments.planning_turn_R_plus_2C` (value); `inconclusive_segments.planning_turn_R_plus_4C` (value); `inadmissible_slots.U5[0]`; `inadmissible_slots.planning_temperature[0]`; `phases[9].result.episode_flags[7]` (planning_turn_R_plus_4C); `phases[11].result.episode_flags[7]` (planning_turn_R_plus_2C). Raw-text count also 6. |
| `r1.g0_cap_saturated` | **0** | not present anywhere in r1_result.json, in any run file, or in the night-custody Python source (`grep -rn`, `joulewise/` and `scripts/`). The nearest records: `g0_cap_w1.censored = []`, `g0_cap_w1.x_g_fallback = false`, `g0_cap_w1.value_s = 740` (clamp(ceil(1.25 x 591.379), 600, 1200) = 740; `max_g0_s` 591.379 from D_bank; waits D_bank 591.379, D_spam_a 466.905, D_spam_b 445.442, X_G 339.945). |
| `inconclusive_segments` | 1 key, 3 entries | `{"planning_turn_R_plus_2C": "r1.g0_timeout_run", "planning_turn_R_plus_4C": "r1.g0_timeout_run", "thermometry.D": "r1.thermometry_failed: research lead ruling required"}` |

Related (not asked): `thermal.start_gate_timeout` appears in the 2 planning-timeout members' episode_flags; `thermal.gate_timeout:1` (a G1, not G0, timeout at the 300 s turn cap) in D_spam_a, D_spam_b and X_G, and `episode.deadman:1` in D_bank (member_status "failed", failure_reason "unknown_error", stop_condition `episode.deadman`; deadman T_dead 918.19 s was exhausted: G0 591.4 + G1 269.9 + prefill 48.5 + decode 8.2 s). `planning_temperature.status = inconclusive`; `u5.verdict = inconclusive`; `duty_bar.verdict = fail`; `skipped_segments = {}`; no `g0_cap_saturated` is needed for any of them.

## Caveats

- The deciding-condition and timeout tables are my reconstructions from 1 Hz journals using the rules at `thermal_gates.py` ~563-590 (read from the night-custody tree, which equals the smoke worktree's file; I did not verify it equals executed commit 99622e96c byte for byte, only that `executed_inventory.json` lists the files). Slope was recomputed with a plain OLS over the preceding 60 s rows and may differ in the last digit from the gate's coverage-filtered slope; the gate's own recorded slope is the number in table 1.
- Tf08 reference values are derived (median over the window-reference span in the segment's own journal), because `align_window_reference.json` stores none. Planning-turn designed states have no Tf08 reference at all.
- Window references for step members are captured at warmup entry, before the heater loads; in step D the 60 s reference window's own sample list shows Th0C falling from 35.29 to 34.64 over the first 47 s then rising to 37.80 in the last 13 s (heater start), so the stored slow reference (35.018, a median) is not a settled value.
