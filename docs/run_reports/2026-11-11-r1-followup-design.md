# R1 follow-up night: design (RL-64 round, Opus and Sol seats)

Date: 2026-11-11 (PST). This is the round ordered by research-lead ruling RL-64, under RL-59's rules. It has two seats,
which wrote independent plans:

- the Opus seat: this branch, first commit `4b1ff049f`, written before the Sol plan was read;
- the Sol seat: `docs/run_reports/2026-11-11-r1-followup-design-sol.md` on `design/2026-11-11-r1-followup-sol` @
  `71b65daed`.

This file is the **one plan**. Where the seats differed, the plan takes the position marked "plan". Every
disagreement, with both positions, is in section D, and the questions that need a ruling are in section E. The
research lead closes the round. Nothing here has been built or armed.

**Inputs.**

- RL-23, RL-26, RL-31, RL-32, RL-35, RL-58, RL-59, RL-61 and RL-64 (`origin/audit/2026-11-10-fable`).
- The RL-58 structural extract.
- The replay at `78e6b19ce`, carried onto this branch and extended (item 1).
- The copied R1 thermal journals, read only through the replay script or its stdlib projection: stamps, the two gate
  keys and the thermal status.
- Code: the W1 line `origin/align/2026-11-08-v4-r11` @ `b4a6c217f`, and the R1 build `da3187e6e`.

**Blinding.** Neither seat opened the ALIGN v4 protocol or the registration texts. The W1 roster facts used here
(ordinals, roles, config names, configured idle, window-reference role) come from the structural keys of
`configs/campaigns/align_v4/night_plan.template.json` and the member configs it names. No energy, power, token or
performance value was read or printed. Phase times come from the thermal journals' own stamps (warmup entry, G0
start and end). No decode or turn duration is stated.

---

## Headline

1. **The consume case works on R1's own record.** Gated against step-D's capture, every D G0 the journals hold
   releases inside 1,200 s:
   - at δ_slow 1.5 °C, between 716 and 889 s;
   - at δ_slow 1.0 °C, between 835 and 1,055 s.

   The two seats' independent replays agree on every shared row to 0.01 s.
2. **RL-64's margin premise is mistaken.** Both seats found this independently.
   - "0.88 to 1.45 °C inside the band at release" is the distance **at the 1,200 s cap**: the earlier replay
     report's "at cap" column.
   - At release, the legs and step-D sit only 0.02 to 0.46 °C inside the band at 1.5 °C, and 0.01 to 0.28 °C inside
     at 1.0 °C.
   - At 1.5 °C the band and the slope bar both bind. At 1.0 °C the band decides, and it costs 60 to 300 s per
     member.
3. **In W1, a G0 timeout does not run the member.** On both builds, `workload.py:440-500` ends an unreleased-G0
   member with zero generation (`episode.g0_unreleased:0`). Both seats found this. "A timeout runs flagged"
   therefore has to be defined, and it needs a seam outside `thermal_gates.py` (item 5).
4. **Thermometry needs a ruling before the night.** On step-30b's gate journal, the slow key Tf08 rose about 56 °C,
   and its cooling τ exceeds 97 s. Its D4/D5 return time, τ·ln ΔT, is therefore above 390 s, against a 300 s
   ceiling. The D step heats as much, and the kit refuses W1 without a passing D bar
   (`align_v4_kit.py:233-236`).

   This is the Opus finding. The Sol seat holds that no cause can be assigned from the copies. Both seats require the
   sanctioned full-inventory print before building (item 7, E1).

---

## Item 1. From the journals: the consume case and δ_slow = 1.0 °C

**What was run.** `scripts/align_r1_thermal_replay.py --scenarios` is extended on this branch. For every D member
it replays W1's G0 rule on the same recorded stream, from the same start instant. Four cases are run:

- against the member's own pre-warmup median;
- against step-D's captured median (the consume case of RL-59);
- each at δ_slow 1.5 and 1.0 °C.

δ_fast stays 1.0 °C and the cap 1,200 s. Each row prints:

- the release time;
- the slow and fast distance inside the band at the release sample;
- the slope at release;
- the release with the slope bar off ("band only") and with the band off ("slope only").

The self-check is unchanged and passes: all 13 recorded outcomes are reproduced, and R_op is recovered bit for bit.
There are 19 tests (`tests.test_align_r1_thermal_replay`), and all pass. The Sol seat's separate extension, on its
branch, stops each counterfactual at the recorded G0 end and adds `--consume-label`. Its numbers equal these. No row
here needs post-G0 samples.

**The consume reference.** The canonical step-D retry captured fast 34.307 °C and slow 28.586 °C. The first try
captured 34.323 and 28.591 °C. They differ by 0.016 °C, and the conclusions are identical with either.

**Gated members.** No heater ran during their G0, so these rows are exact counterfactuals. The replay is about 1 s
early.

| member | ref − own (slow) | own 1.5 | own 1.0 | consume 1.5 | consume 1.0 | inside band at release, consume 1.5 / 1.0 (°C) |
|---|---|---|---|---|---|---|
| A1 | +0.039 | 728 | 873 | 728 | 835 | 0.06 / 0.01 |
| B | +0.317 | 878 | 938 | 878 | 878 | 0.78 / 0.28 |
| A2 | +0.366 | 863 | 1,029 | 717 | 863 | 0.19 / 0.23 |
| step-D first try | −0.006 | 753 | 1,049 | 753 | 1,055 | 0.13 / 0.07 |
| step-D retry | 0 | 815 | 932 | 815 | 932 | 0.21 / 0.06 |

**Which condition decides.**

- At 1.5 °C, the band alone would release at 660 to 801 s and the slope bar alone at 578 to 723 s. The joint
  release, 716 to 878 s, comes after both.
- At 1.0 °C, the joint release is within 0 to 57 s of the band-only time in every gated row, and 112 to 360 s after
  the slope-only time.

**Planning turns.** The heater ran toward R_op + offset, so these rows are threshold tests on the recorded trace, not
counterfactuals.

| member | ref − own | own 1.5 | own 1.0 | consume 1.5 | consume 1.0 |
|---|---|---|---|---|---|
| +4 °C | +0.128 | 462 | 462 | 462 | 462 |
| +2 °C | −0.382 | 694 | 694 | 694 | 694 |
| +0 °C first try | +0.145 | 889 | 983 | 889 | 983 |
| +0 °C retry | +0.246 | 869 | 997 | 866 | 966 |

**Reading.**

- The worst consume-case gated wait is 878 s at 1.5 °C, 322 s inside the cap, and 1,055 s at 1.0 °C, 145 s inside.
- The journals cannot show a D member that follows a full D episode (RL-64). Nor can they show the follow-up's R_D,
  which will be captured after a 30B member rather than after a precool to the R_op band. The night's desk prints
  both.
- **For S6.** At 1.0 °C every member still releases, but by the band and near the cap. If the gated runs waited like
  these members, G0_cap_W1 = clamp(⌈1.25 × max wait⌉, 600, 1,200) would saturate at 1,200 (1.25 × 1,055 = 1,319);
  at 1.5 °C it would be about 1,098 s. Both seats: keep S6 at 1.5 for this arm (RL-32). The lead decides the
  smallest step from release times and cap headroom on the new record, not from the at-cap margin.

---

## Item 2. Order and the capture member

**The predecessor.** step-D follows **one ordinary 30B member**: a fresh, complete anchor-type episode with no thermal
policy (W1's anchors have none) and its normal member deadman and 1,800 s bound. It runs under the adopted series mode.

- *Plan:* the `model_30b` template that `r1_runtime.json` already binds, `align-pilot-v3-episodes-a-e01.json`.
- The Opus seat had proposed e04, W1's literal ordinal 4. This is minor, and listed as D1.

It is **not** step-30b, for three reasons:

- step-30b is a step member, with a 600 s recovery that W1 never has;
- RL-59 keeps it cold and unchanged;
- step-D must follow the A-B-A legs, because it runs under the adopted mode.

**The idle.** The inter-member idle is W1's schedule and nothing else: step-D's own configured `idle_baseline`,
300 s after its model load (`sampling.idle_seconds`; D = X-G = 300 s, `align_r1_rehearsal.py:1192`). R_D is the
median of the last 60 s of that idle.

**The capture pair.** The 30B member and step-D are **one admission unit** for the OS-batch guard. A batch wait
between them would insert exactly the cooling gap this design removes. A ruling 8 load redo repeats the whole pair,
and R_D comes only from the accepted pair. Likewise, each planning redo repeats its precool.

**Sequence.** M = 1,750 + 1.13544 × 1,580 + 120 = 3,663.995 s.

| # | segment | gate reference | mode | bound s |
|---|---|---|---|---|
| 0 | pre_calibration_bracket | — | Automatic | allowance (item 8) |
| 1 | idle_soak, 1,800 s (S5, S5_fast) | — | Automatic | 1,800 |
| 2 | step_30b: W1 capture R_op; G0; 300 s quiet; step; 600 s recovery; record-only classification | own (R_op) | Automatic | M + 2,100 = 5,763.995 |
| 3 | high_power_A1: W1 capture; G0; step | own | Automatic | M + 1,200 = 4,863.995 |
| 4 | high_power_B | own | High Power | 4,863.995 |
| 5 | high_power_A2 | own | Automatic | 4,863.995 |
| — | adoption → series mode set and read back; if inconclusive, run on in **provisional** Automatic, never frozen from that default | | | |
| 6 | capture_predecessor_30b (NEW kind), unmodified `model_30b` episode | none | series | 1,800 |
| 7 | step_D: no precool; D load, 300 s idle, **W1 capture R_D**; warmup; G0; 300 s quiet; step; 600 s recovery; full inventory | own (R_D) | series | 5,763.995 |
| 8 | cooldown_after_D: idle until S_slow ≤ R_D,slow + δ_slow, cap 1,500 s | sensors | series | 1,500 |
| 9 | planning +4: target R_D,slow + 4 | (150, R_D + 4) | series | M + 2,100 = 5,763.995 |
| 10 | precool to the R_D band, then planning +2 | (150, R_D + 2) | series | 1,500 + 5,763.995 |
| 11 | precool to the R_D band, then planning +0 (must dispatch D work before D_bank) | (150, R_D) | series | 1,500 + 5,763.995 |
| 12 | D_bank_benign_s1_gated_held (e08) | R_D consumed | series | 1,800 |
| 13 | D_spam_benign_s1_gated_held_a (e05) | R_D | series | 1,800 |
| 14 | D_spam_benign_s1_gated_held_b (e05), the replay pair with a | R_D | series | 1,800 |
| 15 | X_G_contrast (e06), after D_spam b | R_D | series | 1,800 |
| 16 | post_calibration_bracket, close, harvest; restore Automatic and read it back | | Automatic | allowance |

Segments 12 to 15 each follow the previous D turn with only the next member's 300 s configured idle (R6-1). There is
no precool between them.

**Removed from R1's table:**

- the three releases against the soak before the legs (RL-59);
- step-D's precool (RL-59);
- every precool-and-retry for a G0 (item 5);
- d-4bit, which is a later fallback with its own qualification, and whose source is null.

---

## Item 3. The A-B-A legs

**Each leg is a W1 capture member.** Its policy is `window_reference: {role: capture}` and no reference is installed,
so W1's own `capture_reference` takes the leg's last 60 s of idle before warmup. The G0 gates against that capture,
and the step deadman is re-armed after the G0. There is no soak release.

**The legs stay ahead of step-D.** step-D and every later D measurement run under the adopted mode. If the legs came
later, step-D's slots would be invalid whenever the verdict is "adopt". A1 follows step-30b's recovery. B and A2
follow a D leg.

**How the start states are shown comparable.** The desk prints, side by side for A1, B and A2:

- the mode and its readback;
- the own capture (both keys), with its coverage, slope and noise;
- the G0 outcome and wait;
- the release temperatures (both keys) and their excess over the capture;
- the release margins and the slow slope at release;
- the interval from release to prefill;
- the absolute differences A2 − A1.

The adoption arithmetic is unchanged (`align_r1_rehearsal.py:588`). A leg that started after a G0 timeout, overlapped
an agent, or was contaminated makes the adoption inconclusive, and it goes to the lead (RL-32 condition 7).

- *Plan:* in addition, the desk prints two checks as **disclosures, not acceptance bars**. (i) Cross-band: each leg's
  release sample lies inside every other leg's G0 band. (ii) Bracketing: B's own slow capture lies within
  [min(A1, A2) − 0.5 °C, max(A1, A2) + 0.5 °C], where 0.5 °C is the registered S6 step. A failure of either routes
  the adoption to the lead.
- At R1 the own slow captures were 28.546, 28.269 and 28.220 °C (spread 0.33 °C), and the fast captures were within
  0.03 °C of each other.
- Whether these become bars is D4.

---

## Item 4. Planning turns at R_D + 0, + 2, + 4

**What sets the state.** The warmup sets it, not the preheat. In every D member on the record:

- S_slow at the first G0 sample was 67.6 to 69.1 °C (the two seats read neighbouring samples);
- the warmup peak was 77.7 to 78.0 °C;
- warmup entry to G0 entry was about 104 s.

The preheat loop breaks on the first S_slow ≥ target − 0.5 °C, so it exits at once for every offset. R_D + 4 is
about 32.6 °C. **The preheat therefore reaches every state well inside its 900 s cap.** The designed state is then
reached on the way down. The heater's proportional duty, 0.5 + 0.5 × (target − S_slow) clamped to [0, 1], is zero
above target + 1 °C, and it holds S_slow near the target while W1's G0 decides. The binding cap is the G0's 1,200 s.

**On the record:**

- +4 released at 462 s and +2 at 694 s, both slope-decided and 1.4 to 2.3 °C inside the band;
- +0, in the consume case, released at 866 to 889 s at 1.5 °C and 966 to 983 s at 1.0 °C.

The follow-up's targets are 1.4 to 1.6 °C above R1's R_op + offset, so each band is met earlier on the way down, but
the heater's duty changes with the target. Expected: +4 < +2 < +0, all inside 1,200 s, with +0 at about 870 to
1,000 s. Only the new night shows the heater's trajectory natively.

**The night records** (Sol's list, adopted): preheat entry and end, the target and the threshold crossing, an
`r1.preheat_cap_reached` flag, the actual G0 release temperature, and the heater stop. The existing two-sided check,
|release − target| ≤ δ_slow with distinct release states (`align_r1_rehearsal.py:614-653`), still applies. Today that check raises a `Refusal` at the night's end. In the build it must become a
flagged, inconclusive U5, so that it cannot refuse the whole record (item 5, rule 1). It requires one shared R across
the three states, which holds here because all three consume R_D. A preheat-cap hit makes the planning and U5
evidence provisional until the lead rules.

---

## Item 5. "A timeout runs flagged": exact semantics

**What W1 does.** W1's `_wait` ends at the cap with outcome `timeout`, at min(300 s, cap) with `unobserved`, or with
`deadman`. It flags `thermal.start_gate_timeout` or `thermal.state_unobserved` and leaves `episode_reference = None`.
`workload.py:440-500` then ends the member with zero generation.

**The rule for the follow-up:**

1. **No G0 outcome refuses, aborts, retries or skips downstream.** There is one structural exception: if step-D's
   *capture* is unobserved (coverage < 0.9), W1's verifier refuses every consumer
   (`thermal.window_reference_unobserved`, `thermal_gates.py:256-258`). Planning, the gated block and X-G are then
   recorded as skipped with that code, and the night proceeds to the post bracket. Missing reference custody is a
   refusal, never permission to recapture. A step-D *G0* timeout is not the exception: R_D was captured before that
   G0 and stands.
2. **The run-after-timeout applies only to an observed `timeout`,** and only on step-30b, the legs, step-D and the
   planning turns. Those kinds dispatch their turn. W1's flags and the null episode reference are kept, and
   `r1.g0_timeout_run` is added. The timeout is never renamed "released" and never installed as a G1 or H reference.
   Steps keep the 300 s quiet, and steps and legs re-arm their deadman. Planning always stops the heater.
   `unobserved`, `deadman`, a collector fault or missing status keep W1's stop and their own fault semantics.
3. **Gated D runs and X-G** keep W1's behaviour exactly (*plan*; Sol disagrees, D3). The member ends with zero
   generation, and the next gated run records that it did not follow a D turn. Under the right reference, this is a
   finding about W1, answered by the registered fallback order that the lead applies (RL-59).
4. **No G0-only retry anywhere.** The R6-2 precool-and-retry is retired. Ruling 8 CPU-load redos remain, over complete
   recipes (item 8).
5. **A step-D timeout does not skip the gated block.** The flagged step-D turn gives *candidate* budgets (B_D, T_dead,
   N_chunk), and the gated block runs on them. A non-finite or zero budget, or an incomplete step, is a different
   failure, and no unbudgeted member runs.
6. **Recording.** Every flagged segment, gated runs included, enters `inconclusive_segments` with its reason. The kit
   already refuses on any entry (`align_v4_kit.py:183-239`), and that refusal is the "inadmissible without the lead's
   ruling" mechanism. An explicit `inadmissible_slots` map names, for each slot, the flag that bars it. The S6 = 1.5
   receipt is kept in every proposal, including an inconclusive one (RL-59 Q2).

**The flag, per slot, that makes it inadmissible without a ruling.** Universal bars apply to every slot-feeding
segment:

- the night is complete with chain exit 0 (the verdict word is not evidence);
- the accepted attempt is recorded;
- AC is present and the battery is not discharging (RL-35 condition 10);
- no agent-presence overlap (condition 11), with the summary codes `r1.battery_feed_invalid` and
  `r1.agent_feed_overlap`;
- the external-volume census passes;
- the mode readback is correct.

| slot / record | specific bar |
|---|---|
| S1–S4, S7, S8/N_chunk, S9/t_decline, B_D, I_D, T_dead, class, e_D | step-D carries `r1.g0_timeout_run`; or its turn is incomplete; or `tau_censored`, `recovery_censored` or an unobserved t_decline (a censored value is kept as a bound, never as a measurement) |
| S5, S5_fast | the soak is not accepted, has an unresolved slope, or has a coverage gap |
| S6 and its tuning inputs (G1/H medians) | any gated G0 timeout or hold suppression; the receipt is missing |
| ac_powermode | any leg carries `r1.g0_timeout_run`; or an inconclusive adoption; or a failed item 3 disclosure check (*plan*) |
| planning_temperature, U5 | any planning turn carries `r1.g0_timeout_run` or `r1.preheat_cap_reached`, or fails the two-sided check; or D_spam a or b has a G0 timeout (no σ_pair) |
| duty_bar, deadman_budget, l1, max_r1_tail_s, budget_fit_inputs, projected_mde | step-D budgets are only candidates; a gated G0 timeout is a duty-bar outcome that goes to the lead's fallback order |
| x_g, g0_cap_w1 | any gated or X-G timeout (counted at the cap for a conservative candidate): `r1.g0_cap_saturated` |
| thermometry.D / bar | step-D carries `r1.g0_timeout_run`; or the classifier sets a `reason`; or a null or aliased pick (item 7) |

---

## Item 6. Slots: what feeds each, and what the night must contain

There are 16 slot names: S1–S9, S5_fast, B_D, I_D, T_dead, N_chunk, t_decline and class. The W1 template lists 15
and must be brought to the driver's 16 in the build.

| slot / record | feeding segment | the night must contain |
|---|---|---|
| S1–S4 (fast and slow ΔT, t63, τ) | step_D | the turn, the 300 s quiet before prefill, the 600 s recovery |
| S5, S5_fast | idle_soak | an accepted soak: 3 × the detrended SD of the last 1,200 s, floor 1.0 °C |
| S6 | registered 1.5 °C | nothing new; the desk prints every release's distance inside the band |
| S7 (G_turn) | step_D recovery | the full 600 s recovery |
| S8 / N_chunk, S9 / t_decline, B_D, I_D, T_dead, class, e_D | step_D | one complete turn |
| ac_powermode | A1, B, A2 | three legs with turns |
| planning_temperature (β_T) | three planning turns | three released designed states |
| U5 (σ_pair) | D_spam a and b | both with admitted turns |
| duty_bar, deadman_budget, l1, max_r1_tail_s, budget_fit_inputs, projected_mde | the three gated D runs, plus step-D | each after a D turn with W1's idle; D_bank stays, so that D_spam a has a full-D predecessor |
| x_g, g0_cap_w1 | X-G, plus the gated G0 waits | X-G directly after D_spam b |
| thermometry.D, bar | step_D full-inventory journal | a journal that meets the classifier's sampling bar, and a pass (item 7) |
| thermometry.30B_record_only, R_op, 30B drain | step_30b | as now |
| W1 reference rehearsal (new record) | step-D capture, consumed by planning, the gated block and X-G | R_D verified by W1's verifier at every consumer; the desk prints each member's own pre-warmup median beside R_D and R_op (RL-32 item 8) |

**Cuts** (none feeds a slot):

- the soak releases;
- step-D's precool;
- all G0-only retries, which removes up to 4 × (1,500 + 5,764) s of retry ceiling;
- d-4bit.

The preheat cap is inert (item 4). It is left as it is.

---

## Item 7. The thermometry classifier's null pick on the 30B record

**Agreed by both seats, from code.**

- `classify_step` (`r1_runtime.py:280-323`) runs `smc_enumeration.rank(stage="r1")` on the **full-inventory
  journal**, not the gate journal.
- A null `s_fast` means no unclamped key anywhere was classed `die`. A null `s_slow` means none was classed
  `heatsink` (`select_keys`, `smc_enumeration.py:894-899`).
- `r1.sensor_pick_changed` is only a by-product. `any(ranked[role] != previous[role])` counts None ≠ TV0h as a
  change. *Plan:* flag a change only when both picks are non-null. This is a bound R1 runtime edit, under cold review.
- The sanctioned copies hold the two gate keys only. They do not include the inventory journal or its phase bounds.

**Opus seat, from the gate journal.** The classifier's arithmetic was applied to the two R0 keys over step-30b's
quiet, step and first 97 s of recovery. The phase edges were placed from the temperature trace.

| key | idle distinct values / mode fraction | ΔT | max 1 s change | τ | t_band = τ·ln ΔT |
|---|---|---|---|---|---|
| TV0h | 296 / 0.01 | 57.5 °C | 20.0 °C (< ΔT/2) | 39 s | 158 s: passes `die` |
| Tf08 | 237 / 0.01 | 55.8 °C | 2.6 °C | > 97 s (not crossed by the journal's end) | > 390 s: **fails `heatsink`** (ceiling 300 s) |

**What follows, in the Opus seat's reading.**

- **Tf08 fails D4/D5 on this step.** τ > 97 s does not depend on where the phase edges fall.
- **A generic limit.** At ΔT ≈ 56 °C, a slow key qualifies only if 60 s < τ ≤ 300 / ln 56 = 75 s. That other keys
  failed too is consistent with this, but not shown.
- **TV0h passes the die arithmetic.** Heat-ordering (D1(d)) cannot have nulled s_fast, because its reference key would
  itself be an unclamped die pick. The s_fast exclusion must therefore come from a gate that only the inventory
  journal can fail:
  - ≥ 99 % one-second cells per phase, or < 1 % read errors;
  - D6, two adjacent empty cells;
  - or a D1(b) jump enlarged by a gap.
- **A plausible mechanism for that gate.** The inventory is sampled by a Python ticker thread in the model's own
  process (`r1_runtime.py:1209-1228`, `:1716-1723`). That thread swallows errors and does not replace a late tick.

**Sol seat.** Running `rank` on the projected gate rows only shows that the input is incomplete ("classifier requires
idle, load and recovery"). No physical cause can be assigned from the supplied copies, and claims of a rise or
recovery cause would be guesses (D5).

**What the night needs for a verdict. Both seats agree on 1, 2 and 4.**

1. **Before building:** a sanctioned, temperature-only print of the 30B inventory and of
   `step_30b/inventory/r1_classification.json`. It needs:
   - the three phase bounds;
   - key, unit and quantum metadata;
   - per key: class and reason, ΔT, early rise, τ, t_band, noise, clamp, alias and heat-order diagnostics, and
     per-phase coverage, empty cells and read-error fraction.

   Then `classify_step` is re-run with unchanged thresholds. This takes minutes and settles both causes.
2. If the inventory sampler fails the bar, it is fixed in R1 runtime code, outside the gate module (condition 13
   permits this), with cold review.
3. *(Opus, E1.)* If Tf08's t_band failure is confirmed, the D bar fails under the registered classifier on any step
   that heats like this one. The kit also requires the W1 thermal-policy sensors to equal the D picks
   (`align_v4_kit.py:269`). That is a rule question for the lead **before** arming. The night cannot answer it.
4. The night needs one step-D turn with the quiet and the full 600 s recovery inside the inventory journal, and early
   enough recovery reads to resolve the fast crossing. A verdict is a genuine D pass with two independent, unaliased
   picks, or the lead's ruling on a failure. The 30B is record-only and neither passes nor fails D.

---

## Item 8. Length, deadline arithmetic, OS batch window

These are bounds from code, not measured predictions. Both seats got the same figures independently.

**Bounds.**

- No-redo phase subtotal (segments 1 to 15): **58,711.962 s (16.31 h)**.
- The largest admission unit is the capture pair, 1,800 + 5,763.995 = **7,563.995 s**. A precool plus planning unit
  is 7,263.995 s.
- One OS-batch encounter costs up to the unit bound plus the blackout: 7,563.995 + 5,400 = **12,963.995 s**.
  `wait_outside_os_batch` admits a whole unit (`align_r1_rehearsal.py:963-994`).
- Overhead allowance, to be enforced in the build or replaced by verified bounds: pre and post brackets 1,800 s each,
  close 900 s, harvest 4,500 s, for **9,000 s**.
- Window: the writer formula, 60 × ⌈(⌈span⌉ + 3,300 + 7,200 + 7,200) / 60⌉ (`joulewise/b5/plan.py:59-67`).

| redo allowance | floor (s) | span with overhead (s) | window_max_s |
|---|---|---|---|
| none, 2 encounters | 84,640 | 93,640 | **111,360 (30 h 56 min)** |
| 2 load redos for the night, each a whole unit; 2 encounters (*plan*, E2) | 99,768 | 108,768 | **126,480 (35 h 8 min)** |
| the inherited 2 redos per recipe (9 recipes, Q = 51,511.962 s); 4 encounters (Sol's conservative envelope) | 213,592 | 222,592 | **240,300 (66 h 45 min)** |

**Code to update in the build.**

- `night_worst_case_s` must expose the admission units, the redo quota and the encounter count. A test must assert
  that the arm's window equals it (RL-23 item 5).
- The W1 prequal constants (`w1_prequal.py:934`, `:997-1020`, `:1160`) must be updated from the new table.
- For comparison: R1 at `da3187e6e` gives 100,627 s with retries and one encounter, and the W1 line's stock table
  gives 96,427 s. Neither is this night's deadline. Do not arm on either.

**Expected wall time** (Opus estimate, not a bound). R1 itself ran from t0 20:53 PST to about 04:35, roughly 7.7 h.
That night had ten model members, seven 1,200 s timeouts, three soak releases, and no gated block. The follow-up has
thirteen model members, G0 waits of about 720 to 900 s, no releases and no retries. Expect about 9 to 11 h. The Sol
seat declines to estimate.

**OS batch window**, 11:45 to 13:15 America/Los_Angeles (DST-aware code, no fixed UTC mask):

- For the no-redo ceiling to end before it, t0 must be no later than 11:45 − 16.31 h = **19:26 PST**.
- A t0 between about 17:00 and 01:00 clears it in the expected case.
- The capture pair is admitted as one unit, so no blackout wait can fall between the 30B member and step-D.
- The deadline tests must include:
  - a t0 just before the capture pair would overlap 11:45;
  - a repeated pair;
  - planning redos;
  - a multi-day traversal.

---

## Item 9. The native smoke: what it must show

**Agreed core (Part A, ≤ 1,800 s, admission).** On the built head, on the measurement Mac, from a clean, agent-free
session, the smoke runs the chosen 30B member, then step-D through its load, 300 s idle, capture, warmup and G0. It
must show:

1. **Bytes and identity.** The digests of `thermal_gates.py`, `workload.py`, `r1_runtime.py`, the driver,
   `r1_runtime.json` and the phase-table module equal the built commit's, and `thermal_gates.py` equals the W1
   line's. The model weights match the inventory (RL-62). Nothing is fetched.
2. **The predecessor.** One complete 30B member, with its config digest unchanged and no thermal policy. No precool is
   inserted.
3. **The capture.** step-D's `align_window_reference.json` is `captured`, with 60 samples and coverage ≥ 0.9. It is
   taken **before** warmup and names step-D as the producer, not R_op or the soak. W1's `load_window_reference` with
   a consume policy, called at the desk, authenticates it without recapture. R_D is printed beside R_op.
4. **The gate.** The G0 against R_D releases inside 1,200 s at S6 = 1.5, with ten good samples and fresh Nominal
   status. The replay on the smoke journal prints the release time, the margins, and the band-only and slope-only
   times at 1.5 and 1.0 °C (censored at the recorded end).
5. **The hooks.** The re-arm is recorded. The capture member's G0 reference equals its own record, not overridden.
   `r1.g0_timeout_run` is absent. No outcome is altered.
6. **The host.** The KM003C DC-in capture is present (Ed's rule). AC present and the battery charged throughout. No
   agent, no external volume. Mode readback and restore are correct, and no heater, SMC worker or restore marker is
   orphaned.
7. **If admission does not fit in 1,800 s,** stop and report where it stopped. A partial smoke is not a pass, and it
   is never extended into the long block.

**Part B (*plan*: recommended, D7).** The same step-D runs on through its quiet, turn and 600 s recovery, about 20
more minutes, and `classify_step` runs on it. Part B must show the inventory journal meeting the sampling bar and the
classifier's picks, or its named reason. It is the only pre-night evidence on item 7. If s_slow is null for the t_band
reason, the night is not armed until the lead rules (E1). Sol limits the smoke to Part A.

**Synthetic tests before the smoke.** These run off the measurement Mac:

- an observed-timeout dispatch;
- the unobserved and fault stops;
- the consumer refusal on an unobserved capture;
- an unchanged W1 default;
- candidate-slot refusal;
- heater cleanup;
- budget edges;
- the grouped redo and deadline tests.

**Order before arming** (RL-59): replay; this round closed by the lead; build; synthetic tests; the native smoke;
cold review of the kit changes. If the cold review changes executed bytes, the affected smoke is repeated.

---

## Item 10. Condition 13: W1's thermal-gate module byte for byte; R1-only behaviour through hooks

**The module.** W1's `thermal_gates.py` (`c72937bd8bf7…918d`) differs from `da3187e6e`'s (`2d4917b7e499…da37`) only
by W1-side additions:

- the G0 timing-receipt span, which is a no-op with no writer bound;
- R10-2(a) `g0_cap_receipt` and R11 `contrast_fit` validation;
- refusal of an unobserved source record (D-14b-1);
- an unobserved limit of min(300, cap).

None of these is R1 behaviour. The night takes W1's bytes unchanged. Both seats agree. The Sol report carries the full
diff.

**The seam.** `ThermalRegistry(thermal_factory=...)` is W1's public seam. `ProductionBackend.run_member`
(`r1_runtime.py:1264`) builds W1's `ThermalSession` unchanged, then calls `hook(session)`.

| # | R1-only behaviour | segments | file and hook |
|---|---|---|---|
| 1 | G0 on its own cap outside the deadman; deadman re-armed after G0, quiet or preheat | step-30b, legs, step-D, planning | `r1_runtime.py` `Segment.reference_hook(reference, *, quiet_s=0, rearm_s=None, capture=False)`, which wraps `session.wait` for G0 and calls `rearm_deadman(deadman, s, origin)` (`:469`) |
| 2 | 300 s quiet after G0, including after an observed timeout | step-30b, step-D | the same wrapper |
| 3 | **run after an observed timeout** | step-30b, legs, step-D, planning | *plan* (Sol's design, D2): `workload.py` `EpisodeRuntimeAdapter(..., g0_timeout_hook=None)` is called at `:440-445` as `(session, g0_row) -> bool`. R1 supplies `allow_g0_timeout_run`, which is true only for `outcome == "timeout"`. The default `None` keeps W1's stop. This is a W1-bound edit with an inert default: it needs default-unchanged tests, closure binding and cold review, and it is made before signing |
| 4 | designed start state: reference (150, R_D,slow + offset), heater around W1's G0, preheat evidence | planning | `Segment.planning_hook(reference, target_slow_c, *, rearm_s)` (`:1494`); its base changes from R_op to R_D |
| 5 | **consume R_D across segment directories** (new) | planning base, gated runs, X-G | a hook before warmup: `session.reference, session.custody = load_window_reference(consume_policy, ctx)`. `consume_policy` names step-D's run id and its config SHA-256, and `ctx.bundle_path` sits in step-D's `runs/`. This is **W1's own verifier and W1's refusal codes**. The member policy keeps role `capture`, so `__init__` does not look for a sibling, and `capture_reference` returns early once a reference is set |
| 6 | capture of R_op, of each leg's own reference, and of R_D | step-30b, legs, step-D | **no hook**: W1-native role `capture`. The R1 label for R_op is applied when the runtime reads the record. `da3187e6e`'s capture tap inside the wait wrapper is removed |
| 7 | the new 30B predecessor | segment 6 | `Segment.k_capture_predecessor_30b()` → `run_member(config, hook=None)`, with the unchanged `model_30b` template |
| 8 | 1,200 s cap; S6 floor; S5 from the soak | all model members | policy data through W1's `validate_gate_policy`; `gate_policy`, `bands_c`, `g0_cap_s` (`:403-448`, `:1544`), ported from `da3187e6e` |
| 9 | inventory journal, classifier, heater, idle-until-band precools, recovery observation | runtime | `start_inventory`, `stop_inventory`, `thermometry` (`:1716-1758`), `ProcessHeater`, `k_idle_until_soak` (renamed to the R_D band), `observe_recovery`, all outside the gate module |
| 10 | mode set and restore; candidate versus admissible slots; redo and deadline units | driver | `_set_powermode`, `run`, `aba_adoption`, `night_worst_case_s`, and the contract and kit guard, updated together |
| 11 | phase table | pure module | the RL-61 move first (text unchanged, table-equality tests), then the follow-up schedule as a separate diff |
| 12 | own pre-warmup medians beside R_D and R_op; release margins | desk | *plan*: this replay script (no bound bytes). Sol proposes a runtime `own_reference_diagnostic` (D8) |

**Condition 13's test.** At signing, a check in `v4_registration.py`, for example
`verify_r1_executed_sources(root, slots, executed_commit)`, compares the five files with those at the executed
commit, and the slots file names that commit (RL-61). The regression changes each byte in turn, changes the named
commit, and drops the phase module. Both seats propose adding `workload.py` to the comparison: the run-after-timeout
seam lives there, and W1 already binds it.

**The build.** It starts from the W1 line, which has the newer `x_g_evidence` and the W1 gate code. It ports
`da3187e6e`'s R1 runtime and driver changes: the R_op capture, the S6 receipt reader, the all-model 1,200 s cap, and
the leg and d-4bit re-arm. It adds the RL-61 move and the changes above. The W1 line then takes those files. No stale
deadline, S6 TODO, soak consumer or G0-inconclusive skip is ported.

---

## D. Disagreements between the seats

| # | topic | Opus position | Sol position | in the plan |
|---|---|---|---|---|
| D1 | which 30B predecessor | W1's literal ordinal 4, `e04` (a new template key in `r1_runtime.json`) | the already-bound `model_30b` template, `e01` | Sol (no config change). Low stakes: same model, same idle, no thermal policy |
| D2 | the seam for run-after-timeout | originally an R1 hook setting `session.episode_reference` to the last sample, which leaves `workload.py` byte-identical. Safe for `per_turn: False` policies | a `g0_timeout_hook` callback in `workload.py` with an inert default. No fake episode reference: `ThermalSession.record()` persists `episode_reference` into the bundle (`thermal_gates.py:675-678`) | Sol. Opus concedes: a persisted pseudo-reference is a record a later reader would trust. Cost: a W1-bound edit before signing, with cold review |
| D3 | run-after-timeout for the gated D runs and X-G | no. W1-exact: zero generation. They exist to rehearse W1's D-after-D G0. Dispatching with a null episode reference makes every per-turn G1 an unreferenced wait to its 300 s cap, which W1 never does | yes. Dispatch the bounded workload inside the member's deadman, with native hold suppression disclosed, to preserve diagnostics | Opus. **Lead to rule** (E3) |
| D4 | A-B-A start-state comparability | a numeric cross-band check, plus bracketing within ± 0.5 °C (one S6 step) | print side by side; no new numeric threshold from a design seat; the lead judges | printed as disclosures that route to the lead, not as bars. **Lead to rule** whether they become bars (E4) |
| D5 | cause of the 30B null pick | Tf08's heatsink failure is established from the gate journal: τ > 97 s, t_band > 390 s against a 300 s ceiling. s_fast is narrowed to the inventory journal's sampling gates. The D bar will likely fail the same way | no cause can be assigned from copies that lack the inventory journal and the phase bounds. Anything else is a guess | both require the full-inventory print before building. Opus adds E1 |
| D6 | redo budget and deadline | first draft counted no load redos (window 78,876 s) | grouped recipes with the inherited 2 redos each, overhead caps, 4 encounters: 240,300 s. A smaller global allowance needs a ruling | Sol's construction adopted (units, encounter = unit + blackout, overhead, writer margin). Opus recommends **2 redos for the whole night**, 126,480 s. **Lead to rule** (E2) |
| D7 | smoke scope | Part A (30 min) plus Part B: the step and the classifier, about 20 min more. Part B is the only pre-night thermometry evidence | a strict 1,800 s admission smoke. Thermometry, the A-B-A and the full duty are out of scope | Part A is required; Part B is recommended. **Lead to rule** (E5) |
| D8 | where each member's own pre-warmup median is computed | at the desk, by this replay script; no bound bytes | in the runtime, `own_reference_diagnostic` | desk (RL-32 says "the desk prints"); runtime optional |
| D9 | expected wall time | about 9 to 11 h, scaled from R1's 7.7 h | gives bounds only; no duration prediction | both shown, labelled |

## E. Questions for the research lead

- **E1 (before arming).** Thermometry under the registered classifier. Order the sanctioned full-inventory print of
  the 30B step (item 7.1) now. If it confirms Tf08's t_band > 300 s, rule before the night on how R1's D bar is to be
  met. The kit requires a D pass and W1 sensors equal to the D picks, and the registered D4/D5 rule cannot pass a
  slow key with τ > 75 s at ΔT ≈ 56 °C. Without that ruling the night cannot produce admissible slots.
- **E2.** The load-redo allowance: none (111,360 s), 2 for the night (126,480 s, recommended), or the inherited
  2 per recipe (240,300 s). The 9,000 s overhead allowance must be enforced or verified in the build.
- **E3.** Run-after-timeout scope (D3): the step kinds only (plan), or the gated runs and X-G as well. Also confirm the
  `workload.py` callback (D2) as a W1-bound edit before signing.
- **E4.** Whether the A-B-A disclosure checks become acceptance bars.
- **E5.** Smoke scope: Part A only, or Part A plus Part B.
- **E6.** S6: stays 1.5 °C for the arm (RL-32). Note for the later decision that at 1.0 °C the band decides, at
  60 to 300 s per member, and that G0_cap_W1 could saturate.
- **E7.** Condition 13: add `workload.py` to the executed-source identity check.
