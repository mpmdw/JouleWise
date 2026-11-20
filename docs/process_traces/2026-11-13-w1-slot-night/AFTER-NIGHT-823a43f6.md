# Slot-producing R1 follow-up night: after the night, magistrate 823a43f6 (2026-11-13)

Headless magistrate 823a43f6 (Opus 5.5) launched at 17:05:59 PST, after `chain.exited` (17:04:41 PST, exit 0). It ran item 306's "After the night" with `S=/Users/edr/night-align/r1fu-20261113T144743Z` and `PKT_SHA=80d2023c…946e`. There were no pending notices and no unread mail from Ed. The open directives are only the standing ones. Every time below comes from `date` or from the records.

**Result in one line.** The night COMPLETED, but it produced no slots. Two dispositions send it to the research lead. First, TVh0 failed admissibility on D (clause D1(b), the 5 °C staircase). Second, the duty bar failed: the D_bank run admitted only 2 turns, its gates plus holds took 0.62 × T_dead, and the deadman stopped it (X7). Under disposition 3, no slots are entered, W1 does not sign, and no further night is armed. Nothing is armed now.

## Result, packet, restore

- `r1_result.json` (sha256 `8df1bdd1…8fed`): `status complete`, `error None`. Chain `exit_code` 0. `chain_wall_s` 35,194 s (07:08 to 16:55 PST, then the close). `executed_commit` `a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe`.
- **D-7 step 3:** `prepare_packet.sha256` = `80d2023cff9cb219e282f20c730ac2de541f156f096c05c06141ecec97e6946e`, equal to the arm record's PKT_SHA: **True**.
- Hazard result verdict GO. The results were pushed to `refs/heads/night-results/align-r1-20261113T1508Z` (last commit `61f88049a`).
- Runbook §4:
  1. `arm_align_r1.py uninstall --custody-root "$S"` rc 0. Only `com.joulewise.magistrate` is loaded, and no `com.joulewise.night*` plist is on disk.
  2. `pmset -g custom`: powermode 0 on AC and battery.
  3. No `powermetrics`, `km003c_monitor` or `hazard_monitor` process.
  4. The KM003C capture is present: `hazards/meter/stream-001.jsonl`, 106.6 MB, 35,515 s elapsed, 177,576 polls, 0 bad, 0 USB errors, stopped by signal 15 at the close.
- **Network time and the frequency word.** The driver restored network time ON at 17:04:47 (item 301's behaviour). At 17:07:38 I ran `systemsetup -setusingnetworktime off` and read back Off. Root `zero.py`: before, offset 149 and freq −188706 (−2.88 ppm); after, 0 and 0. Then a 120 s wall-vs-raw rate of **+0.012 ppm** (0.07 ms over 5,764 s).
- Canonical root fast-forwarded to `a5c698e51` after the uninstall, with no night label or plist present.

## Dispositions (item 306), applied by number

1. **Thermometry: FAILED; goes to the research lead.** `thermometry.D.night_confirmation.ok` is false (RL-78), with flag `r1.sensor_inadmissible`. The reason given is "s_slow: TVh0 is not admissible on D (rise/noise/return-time/R0/quality)". The clause, from `step_D_prefill_10k_decode_4096/inventory/r1_classification.json`: TVh0 is class `record-only`, `eligible` false, `clamped` true, with reason **"D1(b): one-second change exceeds half the step rise; recorded only"**. Its `max_one_second_change` is 25.0 °C, and half its observed rise is 49.41 / 2 = 24.70 °C. TVh0's `idle_distinct_values` is 175, against 299 for TV0h, and its `idle_mode_fraction` is 0.418, against 0.003. This is the 5 °C staircase that the arm record (48ce8f17) reported; a 25 °C jump is one step from 60 to 85. TV0h stays `die` and eligible.
   - Also printed (record only): the 30B member's thermometry has `status pass`, flag `r1.sensor_pick_changed`, and picks `s_slow` Th06. The D thermometry's `registered_picks` field reads `{s_fast TV0h, s_slow TaRF}`.
   - Because of the refusal, `align_r1_followup_kit.py desk` (night bytes, read-only) stops with `Refused: RL-78: picked sensors inadmissible on night D; research lead ruling required`.
2. **Duty bar passes: NO.** `duty_bar.verdict fail`, with T_dead 995.79 s, so the bar is 0.40 × T_dead = 398.32 s.
3. **Duty bar fails: APPLIES.** No slots are entered, W1 does not sign, and no further night is armed. It goes to the research lead, and the lead brings the journal table. The rest of the night is kept as diagnostics. The magistrate commits nothing from `r1_slots.json`. Per judged gated run:

   | run | admitted turns | G0 s | G1 s | H s | gates + holds s | / T_dead | X7 | bar |
   |---|---|---|---|---|---|---|---|---|
   | D_bank_benign_s1_gated_held | **2** | 12.2 | 72.3 | **536.5** | **621.06** | **0.624** | **yes** (`episode.deadman`) | fail |
   | D_spam_benign_s1_gated_held_a | 3 | 16.3 | 146.7 (89.6 + 57.1) | 0 | 163.05 | 0.164 | no | pass |
   | D_spam_benign_s1_gated_held_b | 3 | 15.2 | 135.4 (82.5 + 53.0) | 0 | 150.64 | 0.151 | no | pass |

   - In D_bank, turn 1's decode (3,175 tokens over the episode) was held six times on H: 87.7, 105.2, 106.2, 108.4 and 111.9 s, each released, and then the deadman ended the sixth hold after 17.1 s. Every G0, G1 and H on the pair released within its cap, and no G1 or H timed out. The failure is the total hold time inside one long decode, not a stuck gate. D_bank followed `planning_turn_R_plus_0C`.
   - X-G (`X_G_contrast`, not a duty-bar row) was measured: 12 admitted turns, G0 9.2 s, G1 total 430.0 s over 11 turns (27.6 to 54.9 s each), H 0, no X7.
   - `g0_cap_w1` is 600 s, the floor (max D or X-G G0 16.3 s × 1.25).
4. **Planning turns: the 3(a) pattern holds for all three.** This is from `scripts/align_w1_3a_desk.py` at `215e048ed`, run read-only (print beside this file; the lead's own run is the record). For every planning segment: OS level 0; Nominal yes; preceding idle-until-soak `released: true`; no stale pm; G0 interval 1,200 s, with 227 to 266 samples at or above the threshold in its last 300 s (desk column `n>=thr`). The table below gives TVh0's peak over the last 300 s against band edge − 0.3 °C.

   | segment | target °C | band edge °C | TVh0 last-300 s peak °C | margin °C | class |
   |---|---|---|---|---|---|
   | R+0 | 34.853 | 35.853 | 40.000 | +4.447 | planning-release-3a |
   | R+2 | 36.853 | 37.853 | 45.000 | +7.447 | planning-release-3a |
   | R+4 | 38.853 | 39.853 | 45.000 | +5.447 | planning-release-3a |
   | R+4 (`rejected1`, superseded by the load redo) | 38.853 | 39.853 | 45.000 | +5.447 | planning-release-3a |

   - **Caution:** these TVh0 peaks are staircase values (40, 45). The real die temperature is 5 × ⌊TV0h/5⌋ or more, so the margins are lower bounds. U5 and the planning temperature print `inconclusive`. Whether the lead writes `r1_planning_release.json` is the lead's call. With disposition 3 in force, no slots follow from it.
5. **S6.** The median G1 wait over the gated D runs is 72.30 s (5 waits), at most 90 s, so this disposition is not triggered. The H median is 105.73 s (6 waits, all in D_bank). `s6_tuning.status` is `new_sensor_default`.
6. **A-B-A: `not_adopted`, as expected.** The reason is "t_decline(B) < 1.25 × max(A1, A2)", with t_decline A1 100.78 s, A2 100.93 s and B 100.90 s. All 12 start-state cross-band bars pass (smallest margin +0.003 °C, A2 against A1, fast). B's slow capture is bracketed (`slow_capture_bracket` true). Every leg's G0 released (114.2, 116.3 and 114.2 s).
7. **Host.** Network time is OFF again and the frequency word is 0 (above). AC powermode is 0. `ac_powermode` is 0 in every slot record.
8. **Other failure shapes.** These also go to the research lead: X7 in D_bank (above) and the failed admissibility clause (disposition 1). There was no G0 timeout outside the planning turns.

## RL-90: every G0

Release minus reference is in °C. The reference is the step-D 60 s capture (34.853 °C on both keys) for the D, X-G and step-D members, and each member's own capture for 30B and A-B-A. Tf08's reference is the mean Tf08 over the same span from the source member's journal. Tf08 at release is the last journal reading at or before `exit_sample_ns`. "Last clause" is derived from the journal. If both keys sat in band for more than 1.5 s before release, the slope clause decided; otherwise the band did. The script is `after-night-823a43f6/g0_table.py`, and its output is `g0_table.jsonl`.

| member | outcome | s | TV0h | TVh0 | Tf08 | slope °C/min | last clause | Tf08 at member start − ref |
|---|---|---|---|---|---|---|---|---|
| step_30b | released | 107.9 | +0.778 | +0.778 | +7.762 | −0.055 | slope (band held 34 s) | −0.506 |
| step_D | released | 118.2 | +0.601 | +0.147 | +4.668 | 0.000 | slope (band held 40 s) | +27.05 |
| high_power_A1 | released | 114.2 | +0.928 | +0.597 | +8.649 | 0.000 | slope (10 s) | +3.498 |
| high_power_B | released | 114.2 | +0.674 | +0.279 | +5.795 | 0.000 | slope (34 s) | +13.09 |
| high_power_A2 | released | 116.3 | +0.673 | +0.273 | +5.728 | 0.000 | slope (35 s) | +11.66 |
| D_bank | released | 12.2 | +0.521 | +0.147 | not extracted | +0.198 | not extracted | not extracted |
| D_spam_a | released | 16.3 | +0.683 | +0.147 | +5.511 | +0.146 | slope (10 s) | +17.66 |
| D_spam_b | released | 15.2 | +0.551 | +0.147 | +3.959 | +0.211 | slope (14 s) | +14.89 |
| X_G_contrast | released | 9.2 | +0.261 | +0.147 | +0.787 | +0.149 | both in band at entry | +15.24 |
| planning R+0, R+2, R+4, R+4 rejected1 | timeout | 1,200.0 each | — | — | — | — | (disposition 4) | — |

- RL-64: every release is inside its +1.0 °C band on both keys. The largest TV0h value is +0.928 (A1), and every TVh0 value is +0.778 or lower.
- Most slope values at release are 0.000, and the D-member TVh0 deltas are all +0.147, which is 35.000 − 34.853. That is the staircase: TVh0 is pinned at 35.0. D_spam_b released at +0.211 °C/min, outside ±0.2. This needs the research lead's attention, together with disposition 1; the arm record's finding covers how the slope clause reads TVh0.
- Tf08 at member start sits 3.5 to 27 °C above the step-D reference (RL-78 record key).
- Why D_bank's row has gaps: its gate events are in `outputs/align_runtime_events.jsonl`, not the bundle `events.jsonl` that the script reads. Its G0 numbers above come from that file by hand.

## RL-91 and flags

- `capture_reaps`: absent from every member's `metadata.json` (14 members), so no powermetrics reap was recorded. Ticker statistic (ticks less than 0.5 s apart): **not computed by this activation**; it is left to the lead's desk.
- `r1.g0_timeout_run`: 4 G0 timeouts, all on planning turns (R+0, R+2, R+4, and R+4 `rejected1`).
- `inconclusive_segments`: 4. Three planning segments carry `r1.g0_timeout_run`, and `thermometry.D` carries `r1.thermometry_failed: research lead ruling required`.
- Other `inadmissible_slots` flags: `r1.candidate_budget_or_duty_fallback` on budget_fit_inputs, deadman_budget, duty_bar, l1, max_r1_tail_s and projected_mde. U5 carries `r1.u5_inconclusive`. `load_redos_used` is 1.
- Not read or printed: `r1_slots.json` and the energy fields.

## Mail

Ed was mailed after this commit (Gmail; the message id is in RUN_STATE item 310). No Codex child was started.
