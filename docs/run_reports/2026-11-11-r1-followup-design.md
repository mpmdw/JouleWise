# R1 follow-up night: design (RL-64 round, Opus and Sol seats)

Date: 2026-11-11 (PST). This is the round ordered by research-lead ruling RL-64, under RL-59's rules. It has two
seats. The Opus seat wrote this file and the Sol seat wrote `docs/run_reports/2026-11-11-r1-followup-design-sol.md`
on `design/2026-11-11-r1-followup-sol`. This file is the one plan. The disagreements, with both positions, are in
section D. The research lead closes the round. Nothing here has been built or armed.

**Inputs.** RL-23, RL-26, RL-31, RL-32, RL-35, RL-58, RL-59, RL-61 and RL-64 (`origin/audit/2026-11-10-fable`); the
RL-58 structural extract; the replay at `78e6b19ce`, carried onto this branch and extended (see item 1); the copied R1
thermal journals, which were read only through the replay script or the stdlib projection it uses (stamps, the two
gate keys and the thermal status). The code read is the W1 line `origin/align/2026-11-08-v4-r11` @ `b4a6c217f` and
the R1 build `da3187e6e`.

**Blinding.** I did not open the ALIGN v4 protocol or registration texts. The W1 roster facts used below (ordinals,
roles, config file names, configured idle, window-reference role) come from
`configs/campaigns/align_v4/night_plan.template.json` and the member configs it names, and I read only those
structural keys. No energy, power, token or performance value was read or printed. The member-phase timings below
are taken from the thermal journals' own stamps (warmup entry, G0 start and end). No decode or turn duration is
stated anywhere in this file.

---

## Headline

1. **Every D member releases in the consume case, at both bands.** Gated against step-D's capture, all nine D G0s
   the journals hold release inside 1,200 s: at δ_slow 1.5 °C between 716 and 889 s, and at 1.0 °C between 835 and
   1,055 s. The night's reference rule works on R1's own record.
2. **RL-64 read the wrong column.** "0.88 to 1.45 °C inside the band at release" is the distance at the 1,200 s cap
   (the replay report's "at cap: slow − own edge" column). At release the legs and step-D sit only 0.02 to 0.46 °C
   inside the band at 1.5 °C, and 0.01 to 0.28 °C inside at 1.0 °C. The band is not slack. At 1.5 °C the band and
   the slope bar both bind. At 1.0 °C the band decides alone. Releasing at 1.0 °C would cost 60 to 300 s per member.
   If W1's gated runs waited as long, its G0-cap formula would saturate at 1,200 s (1.25 × 1,055 s = 1,319 s). This bears on the S6 decision that
   RL-64 reserves.
3. **In W1, a G0 timeout does not "run" the member.** At `workload.py:440-498` (W1 bytes) an unreleased G0 ends the
   member with zero generation, flagged `episode.g0_unreleased:0`. So "a timeout runs flagged" has to be defined per
   segment kind (item 5). The step kinds need an R1-only hook to run their turn. The gated block keeps W1's
   behaviour exactly.
4. **The thermometry bar will very probably fail on the D step under the registered classifier. Nothing in the
   night fixes that.** On step-30b's gate journal, Tf08 rose by about 56 °C and its cooling τ exceeds 97 s, so its
   D4/D5 release time τ·ln(ΔT) exceeds 390 s, against a 300 s ceiling. The D step heats as much. The kit refuses W1
   without a passing D bar (`align_v4_kit.py:233-236`), so this needs the research lead's ruling **before** the night
   is armed (item 7, ruling request Q1).

---

## Item 1. From the journals: the consume case, and δ_slow = 1.0 °C

**What was run.** `scripts/align_r1_thermal_replay.py --scenarios` is extended on this branch. For every D member it
replays W1's G0 rule on the same recorded stream, from the same start instant. It runs against two references: the
member's own pre-warmup median, and step-D's captured pre-warmup median (the consume case, RL-59). It does each at
δ_slow 1.5 and 1.0 °C. δ_fast stays 1.0 °C and the cap 1,200 s. Each row prints:

- the release time;
- the distance inside the slow and fast bands at the release sample;
- the slope at release;
- the release with the slope bar off (band only) and with the band off (slope bar only).

The self-check is unchanged and passes: all 13 recorded outcomes are reproduced, and R_op is recovered bit for bit.
New tests are in `tests.test_align_r1_thermal_replay.ScenarioTests` (19 tests, OK). The run took 157 s on the Air.

**Consume reference.** There are two step-D captures:

- step_D (retry), the canonical attempt: fast 34.307 °C, slow 28.586 °C;
- step_D (first try): fast 34.323 °C, slow 28.591 °C.

They differ by 0.016 °C, and every result below is the same with either one.

**Gated members** (no heater during G0, so these are exact counterfactuals). Waits are in seconds; the replay runs
about 1 s early.

| member | ref − own (slow) | own 1.5 | own 1.0 | consume 1.5 | consume 1.0 | inside band at release, consume 1.5 / 1.0 (°C) |
|---|---|---|---|---|---|---|
| A1 | +0.039 | 728 | 873 | 728 | 835 | 0.06 / 0.01 |
| B | +0.317 | 878 | 938 | 878 | 878 | 0.78 / 0.28 |
| A2 | +0.366 | 863 | 1,029 | 717 | 863 | 0.19 / 0.23 |
| step-D first try | −0.006 | 753 | 1,049 | 753 | 1,055 | 0.13 / 0.07 |
| step-D retry | 0 | 815 | 932 | 815 | 932 | 0.21 / 0.06 |

**Which condition decides.** At 1.5 °C the band alone would release at 660 to 801 s and the slope bar alone at 578
to 723 s. The joint release, 716 to 878 s, comes after both, so both bind. At 1.0 °C the joint release is within 0
to 57 s of the band-only time in every gated row, and 112 to 360 s after the slope-only time. The band decides.

**Planning turns** (the heater ran during G0, toward R_op + offset; the rows say only whether the recorded stream
meets the alternative rule):

| member | ref − own | own 1.5 | own 1.0 | consume 1.5 | consume 1.0 |
|---|---|---|---|---|---|
| +4 °C | +0.128 | 462 | 462 | 462 | 462 |
| +2 °C | −0.382 | 694 | 694 | 694 | 694 |
| +0 °C first try | +0.145 | 889 | 983 | 889 | 983 |
| +0 °C retry | +0.246 | 869 | 997 | 866 | 966 |

**Reading.**

- RL-64's inference holds in its conclusion: against a D-captured reference, every D member releases. It does not
  hold in its reason. The members are not deep inside the band at release. They reach it about when the slope
  flattens.
- The worst consume-case wait of a gated member is 878 s at 1.5 °C (322 s to the cap) and 1,055 s at 1.0 °C (145 s
  to the cap).
- The follow-up's R_D will be captured after a 30B anchor, not after a precool to the R_op band as in R1 (item 2).
  It can come out warmer or cooler than 28.59 °C. The journals cannot show which, and nor can they show a D member
  that follows a full D episode, as RL-64 says. The night's desk prints both.
- **For S6** (RL-64's note): at 1.0 °C every member still releases, but by the band and close to the cap. If the gated
  runs waited like these members, W1's G0_cap_W1 = clamp(⌈1.25 × max wait⌉, 600, 1,200) would saturate. At 1.5 °C it
  would be about 1,098 s. "Released at
  1.0 °C" is true but thin. The S6 decision should be taken on release time and cap headroom, not on the at-cap
  margin.

---

## Item 2. Order and the capture member

**The predecessor.** step-D follows **one W1 30B anchor member**, configuration `align-pilot-v3-episodes-a-e04.json`
(W1's ordinal 4, the member that precedes ordinal 5 in the plan template). It runs unmodified and has no thermal
policy, as W1's anchors have none. It runs under the adopted series mode.

**Inter-member idle.** The idle between the anchor and step-D is the W1 schedule: nothing but step-D's own configured
`idle_baseline` (300 s, `sampling.idle_seconds` of e05, after the model load). R_D is the median of the last 60 s of
that idle, which is WP14(b)'s mechanics.

**Why not step-30b.** step-30b is a step member, not an anchor, and it ends in a 600 s recovery observation that W1
never has. It must also stay cold and first (RL-59: unchanged). And step-D must follow the A-B-A legs, because it
runs under the adopted mode. A new 30B member between A2 and step-D is the only order that satisfies all three.

**Exact sequence.** Bounds are the code's ruling 8 bounds, with M = 1,750 + 1.13544 × 1,580 + 120 = 3,663.995 s.

| # | segment | kind | reference used by its G0 | mode | bound s |
|---|---|---|---|---|---|
| 0 | pre_calibration_bracket | calibration-pre | — | Automatic | (unbounded) |
| 1 | idle_soak | idle 1,800 s | — | Automatic | 1,800 |
| 2 | step_30b | step-30b (W1 capture: R_op) | own capture | Automatic | 5,763.995 |
| 3 | high_power_A1 | aba leg (W1 capture) | own capture | Automatic | 4,863.995 |
| 4 | high_power_B | aba leg (W1 capture) | own capture | High Power | 4,863.995 |
| 5 | high_power_A2 | aba leg (W1 capture) | own capture | Automatic | 4,863.995 |
| — | A-B-A verdict → series mode set | | | | |
| 6 | anchor_30b (NEW) | W1 anchor e04, unmodified | none (no policy) | series | 1,800 |
| 7 | step_D_prefill_10k_decode_4096 | step-d (W1 capture: **R_D**) | own capture = R_D | series | 5,763.995 |
| 8 | cooldown_after_D | idle-until-band of R_D (1,500 s cap) | sensors only | series | 1,500 |
| 9 | planning_turn_R_plus_4C | designed state, R_D + 4 | (150, R_D,slow + 4) | series | 5,763.995 |
| 10 | planning_turn_R_plus_2C.precool | idle-until-band of R_D | sensors only | series | 1,500 |
| 11 | planning_turn_R_plus_2C | designed state, R_D + 2 | (150, R_D,slow + 2) | series | 5,763.995 |
| 12 | planning_turn_R_plus_0C.precool | idle-until-band of R_D | sensors only | series | 1,500 |
| 13 | planning_turn_R_plus_0C | designed state, R_D + 0 | (150, R_D,slow) | series | 5,763.995 |
| 14 | D_bank_benign_s1_gated_held | gated D (W1 e08), follows the +0 turn | R_D (consumed) | series | 1,800 |
| 15 | D_spam_benign_s1_gated_held_a | gated D (W1 e05) | R_D | series | 1,800 |
| 16 | D_spam_benign_s1_gated_held_b | gated D (W1 e05) | R_D | series | 1,800 |
| 17 | X_G_contrast | X-G (W1 e06), follows D_spam b | R_D | series | 1,800 |
| 18 | post_calibration_bracket, harvest | | | restore Automatic | (unbounded) |

**Removed from R1's table:**

- the three releases against the soak before the legs (RL-59);
- step-D's precool to the R_op band (RL-59);
- every R6-2 precool-and-retry (item 5);
- d-4bit, whose source is null.

**What changes from R1.** R_op is captured by step-30b with W1's native capture role, and it gates nothing after it.
The precools and the post-D cooldown release against R_D's band, not the soak's or R_op's. The gated runs, X-G and
the planning base consume R_D, and step-D gates against R_D, which is its own capture.

---

## Item 3. The A-B-A legs

**Each leg is a W1 capture member.** Its policy is `window_reference: {role: capture}` with no hook-installed
reference, so W1's `capture_reference` takes the leg's own last 60 s of idle before warmup, and the leg's G0 gates
against that capture. The leg keeps R1's re-armed deadman (item 10). There is no release against the soak.

**Start states shown comparable, at the desk.** These checks are run at the desk, not as gates. Three records per leg
are printed: its own reference (fast, slow), its G0 release sample (fast, slow), and the slope at release. They come
from `align_window_reference.json` and the G0 row. The rule:

- **(i) Settled.** All three G0s released against their own capture. A leg that ran after a timeout (item 5) makes
  the adoption inadmissible without a ruling.
- **(ii) Cross-band consistency.** Each leg's release sample lies inside every other leg's G0 band (δ_fast 1.0 °C,
  δ_slow = S6). Equivalently, any leg would have released against any other leg's reference. At R1 the three own
  slow references were 28.546, 28.269 and 28.220 °C (spread 0.33 °C) and the fast ones lay within 0.03 °C, so this
  holds with room on the record we have.
- **(iii) Bracketing.** B's own slow reference lies within [min(A1, A2) − 0.5 °C, max(A1, A2) + 0.5 °C], so that a
  monotone drift is bracketed. The 0.5 °C is the registered S6 step: a difference smaller than one tuning step
  cannot be told apart.

If (ii) or (iii) fails, the adoption is reported as "start states not comparable", left inconclusive, and goes to the
lead (RL-32 condition 7). The decline times are still recorded.

**The legs stay ahead of step-D.** Step-D and every later D measurement run under the adopted mode (RL-59, R5-5).
Putting the legs after step-D would invalidate step-D's slots whenever the verdict is "adopt". A1 follows step-30b's
600 s recovery. B and A2 follow a D leg.

---

## Item 4. Planning turns at R_D + 0, + 2, + 4

**The preheat never sets the state; the warmup does.** In all nine D members on the record, S_slow at G0 entry was
67.6 to 68.6 °C, and the warmup peak was 77.7 to 78.0 °C, against idles near 28.5 °C. The G0 starts about 104 s after
warmup entry. `planning_hook`'s preheat loop (`r1_runtime.py` at `da3187e6e`, around line 1558) breaks as soon as
S_slow ≥ target − 0.5 °C, so it exits at its first check for every offset: R_D + 4 is about 32.6 °C, far below 68 °C.

**How the designed state is actually reached.** It is reached on the way down. The heater's proportional hold,
duty = 0.5 + 0.5 × (target − S_slow), clamped to [0, 1], is zero above target + 1 °C. It holds S_slow near the target
while W1's G0 (band target + δ_slow, and the slope bar) decides. **The binding cap is the G0's 1,200 s, not the 900 s
preheat cap.**

**Does each state release inside its cap?** Yes, on the record:

- +4 released at 462 s and +2 at 694 s. Both were slope-decided, 1.4 to 2.3 °C inside their bands.
- +0, in the consume case, releases at 866 to 889 s (1.5 °C) and 966 to 983 s (1.0 °C).

The follow-up's targets are R_D + offset, about 1.4 to 1.6 °C above R1's R_op + offset, so the cooldown meets each
target band earlier. The +0 target equals D's own idle level, and the heater holds at the band centre. Expected
release order is +4 < +2 < +0, all inside 1,200 s, with +0 the slowest at about 870 to 1,000 s.

**One caution.** At +0 the heater is active near D's natural idle. It cannot hold S_slow above the band, since its
duty is zero above target + 1 °C, but it does flatten the approach, which helps the slope bar. The β_T rows therefore
carry the release temperature actually reached, as R1 already records (`g0_release_c`).

---

## Item 5. "A timeout runs flagged": exact semantics

**What W1 does** (W1 bytes): `thermal_gates.py` `_wait` returns outcome `timeout` at the cap, or `unobserved` at
min(300 s, cap), or `deadman`. It raises `thermal.start_gate_timeout` or `thermal.state_unobserved`. `workload.py`
:440-498 then ends the member **with zero generation** (`episode.g0_unreleased:0`), and the window continues.

**The follow-up's rule** (generalising RL-23 item 2):

1. **No G0 outcome refuses, aborts or skips anything downstream.** There is one structural exception. If step-D's
   *capture* is unobserved (coverage < 0.9), W1's verifier refuses every consumer
   (`thermal.window_reference_unobserved`, `thermal_gates.py:256-258`). Planning, gated and X-G are then recorded
   skipped with that W1 code, and the night continues to the post bracket and harvest. A step-D **G0** timeout is
   not that exception: R_D was captured before the G0 and stands.
2. **No retries.** R6-2's precool-and-retry is retired. W1 has none, and a retry would recapture R_D or turn the
   segment into a second, different start state.
3. **After a timeout, by kind:**
   - **Gated D runs and X-G: exactly W1.** The member ends with zero generation, the wait is the cap, and the
     member is flagged. The next gated run then does not follow a D turn, and R6-1's schedule reason is recorded.
     This is W1's own D-after-D outcome and is evidence about W1, not noise.
   - **step-30b, A-B-A legs, step-D, planning turns: run-after-timeout (R1-only hook, item 10).** The turn runs from
     the temperature reached, the step quiet still applies, and the segment adds `r1.ran_after_g0_timeout` to W1's
     timeout flag. Every field it produces carries `start_state: "unreleased"`. step-30b stays record-only under
     RL-23 item 2.
4. **Recording.** Every flagged segment enters `inconclusive_segments` with the reason
   `"G0 <outcome> at <wait> s: ran flagged (RL-59)"`. Gated runs and X-G are recorded as `"G0 timeout: W1 finding
   (RL-59)"`. The kit already refuses on any entry (`align_v4_kit.py:194-205`), so the kit's refusal is the
   mechanism for "inadmissible without the lead's ruling". Admission is the lead's signed ruling, cited in the slots
   record.

**The flag, per slot, that makes it inadmissible without a ruling:**

| slot / record | inadmissible if |
|---|---|
| S1–S4, S7, S8/N_chunk, S9/t_decline, B_D, I_D, T_dead, class, e_D (step-D) | step-D carries `r1.ran_after_g0_timeout` or `thermal.state_unobserved`; or its turn is incomplete (`episode.deadman:*`, `episode.decode_budget:*`) |
| S5, S5_fast | soak not accepted on attempt 0, or a soak redo |
| S6 (stays 1.5, RL-32) and its tuning input (gated G1/H medians) | any gated run has a timeout flag (its G1/H waits are absent), or step-D slots inadmissible |
| ac_powermode | any leg has `r1.ran_after_g0_timeout`, or start states fail (ii) or (iii) of item 3 |
| planning_temperature, U5 | any planning turn has `r1.ran_after_g0_timeout`; either replay-pair run (D_spam a or b) has a G0 timeout (no turns, so no σ_pair) |
| duty_bar, deadman_budget, l1, max_r1_tail_s, budget_fit_inputs, projected_mde | step-D slots inadmissible (the budgets come from them); a gated-run G0 timeout is a duty-bar outcome under the correct reference, and the lead applies the registered fallback order (RL-59) |
| x_g, g0_cap_w1 | X-G or any gated G0 timeout (G0_cap_W1 saturates at 1,200 s): `r1.g0_cap_saturated` |
| thermometry.D / bar | step-D has `r1.ran_after_g0_timeout`; or the classifier's `reason` is set; or a null pick (item 7) |
| thermometry.30B_record_only | record only, never a slot |
| any slot-feeding segment | battery not AC and not charged (RL-35 condition 10); an agent-presence overlap (condition 11); an external-volume census FAIL |

---

## Item 6. Slots: what feeds each, and what the night must contain

| slot / record | feeding segment | the night must contain |
|---|---|---|
| S1–S4 (fast and slow ΔT, t63, τ) | step_D | the step turn, with the 300 s quiet before prefill and the 600 s recovery |
| S5, S5_fast | idle_soak | an accepted 1,800 s soak (3 × detrended SD, 1.0 °C floor) |
| S6 | registered 1.5 °C (RL-32) | nothing new; the desk prints every release's distance inside the band (RL-64) |
| S7 (G_turn = min(300, 3 × recovery)) | step_D recovery | the 600 s recovery observation |
| S8 / N_chunk, S9 / t_decline, B_D, I_D, T_dead, class, e_D | step_D | one complete step turn |
| ac_powermode, slots_ac_powermode | A1, B, A2 | three legs with turns and comparable starts (item 3) |
| planning_temperature (β_T) | three planning turns | three released designed states |
| U5 (σ_pair) | D_spam a and b (the replay pair) | both with admitted turns |
| deadman_budget, duty_bar, l1, max_r1_tail_s, budget_fit_inputs, projected_mde | D_bank, D_spam a, D_spam b (and step-D slots) | the three gated runs, each following a D turn with W1's idle |
| x_g, g0_cap_w1 | X_G_contrast, plus gated G0 waits | X-G right after D_spam b |
| thermometry.D, bar | step_D full-inventory journal | an inventory journal meeting the classifier's sampling bar, plus a passing classification (item 7) |
| thermometry.30B_record_only, R_op, 30B drain | step_30b | step-30b (unchanged) |
| battery, g0_waits, census | all | as now |
| **W1 reference rehearsal (new record)** | step_D capture → planning, gated, X-G | R_D verified by W1's verifier at every consumer; desk prints each member's own pre-warmup median beside R_D and R_op |

**Cuts proposed** (none feeds a slot):

- the three releases against the soak (RL-59);
- step-D's precool (RL-59);
- all R6-2 retries (item 5; saves up to 4 × (1,500 + 5,764) s of ceiling);
- d-4bit (source null);
- the planning preheat cap. It is inert (item 4). It is left in the code, but the bound could drop by 900 s per state
  if the lead wants a shorter ceiling. I do not recommend changing a bound for 45 min of ceiling.

---

## Item 7. The thermometry classifier's null pick on the 30B record

**What the code says.**

- `classify_step` (`r1_runtime.py:280-320`) calls `smc_enumeration.rank(stage="r1")` on the **full-inventory
  journal** (`<segment>/inventory/inventory_journal.jsonl`). That is not the gate journal.
- A null `s_fast` means **no key in the whole inventory** was classed `die` (and unclamped). A null `s_slow` means
  no key was classed `heatsink` (`select_keys`, `smc_enumeration.py:894-899`).
- `r1.sensor_pick_changed` is a by-product: `changed = ranked[role] != previous[role]` counts None ≠ TV0h as a
  change. It says nothing beyond the null pick. Proposed fix: flag a change only when both picks are non-null; a
  null pick has its own reason. This is a bound R1 runtime edit and goes with the build, under cold review.
- The reasons field held only "null pick", so `classify_step`'s own coverage refusals (`quiet_not_observed`,
  recovery not observed) did not fire.

**What the gate journal shows**, for the two R0 keys over step-30b's quiet, step and first 97 s of recovery. This uses
the classifier's own arithmetic. Phase edges were placed from the temperature trace, so it is indicative only.

| key | idle distinct values (300 s) | idle mode fraction | rise ΔT | max 1 s change (load) | τ | t_band = τ·ln ΔT | D4/D5 |
|---|---|---|---|---|---|---|---|
| TV0h | 296 | 0.01 | 57.5 °C | 20.0 °C (< ΔT/2 = 28.8) | 39 s | 158 s ≤ 300 | passes as `die` |
| Tf08 | 237 | 0.01 | 55.8 °C | 2.6 °C | > 97 s (not crossed by journal end) | > 390 s > 300 | **fails `heatsink`** |

**Cause of the null s_slow: established.** It is the registered releasability rule meeting the step's heat:

- With ΔT near 56 °C, a slow key qualifies only if 60 s < τ ≤ 300 / ln(56) = 75 s, a 15 s window.
- Tf08's τ exceeds 97 s.
- No slow key will qualify on a step that heats this much. R0's picks were made under R0's calibration load, not this
  step.

**Cause of the null s_fast: not established, but narrowed.** TV0h passes the die arithmetic on the gate journal.
Heat-ordering (D1(d)) cannot null s_fast, since its reference key would itself be a die pick. So the exclusion must
come from a quality gate that only the inventory journal can fail:

- ≥ 99 % one-second cells per phase;
- < 1 % read errors;
- no two adjacent empty cells (D6);
- or a D1(b) jump inflated by a gap.

The inventory journal is sampled by a Python ticker thread in the model's own process (`ticker`, `r1_runtime.py`
around line 1209). That thread swallows its errors, and a late tick is not replaced: `due += 1.0` only bunches the next reads, so a slow
read leaves empty one-second cells. The 2-key gate
sidecar in the same process held 1 Hz, but a full-inventory read is many times longer.

**What the night needs for a verdict.**

1. **Before arming: a sanctioned desk print of `step_30b/inventory/r1_classification.json`.** Temperatures and
   classifier fields only: for every key, its class and reason; ΔT, τ, t_band, noise; per-phase coverage, maximum
   empty cells and read-error fraction; plus `heat_ordering_reference` and the exclusion count. It takes minutes, and
   it confirms or refutes both causes.
2. **If the inventory sampler is the s_fast cause,** fix it in the R1 runtime before the night: it is R1 code outside
   the thermal-gate module, so condition 13 permits it, under cold review. The smoke (item 9) must then show the
   journal meeting the bar.
3. **The s_slow cause is a rule question, not a night question.** Under the registered classifier, D's step
   classification will null-pick s_slow with high probability. The D bar then fails, the kit refuses
   (`align_v4_kit.py:233-236`), and the kit also requires the W1 thermal-policy sensors to equal the D picks
   (`:269`). **The research lead must rule before the night is armed** (Q1). The night alone cannot produce a
   passing D bar.
4. The night itself needs one step-D turn (released, or run-after-timeout and flagged), the 300 s quiet and the 600 s
   recovery inside the inventory journal, as now.

---

## Item 8. Length, deadline arithmetic, OS batch window

**Ceiling** (`night_worst_case_s` construction, sequence of item 2):

- **No redo: 58,711.962 s (16.31 h).** That is 1,800 + 5,763.995 + 3 × 4,863.995 + 1,800 + 5,763.995 + 1,500 +
  3 × 5,763.995 + 2 × 1,500 + 4 × 1,800.
- **One batch encounter** (the largest bound plus the blackout: 5,763.995 + 5,400 = 11,163.995 s): 69,875.957 s
  (19.41 h).
- **Retry floor.** With no R6-2 retries, `r6_2_retry_max_s` is 0, so the floor is 69,875.957 s.
- **Window.** By RL-23's construction (floor + 9,000 s), `window_max_s` = 78,875.957 s (21.91 h).
- **Compared with R1 at `da3187e6e`:** no-redo 60,406.962 s, retry floor 100,626.938 s.
- **Rule.** A test asserts that the constant equals `night_worst_case_s` (RL-23 item 5). The arm derives the plan's
  window from it.

**Expected wall time.** R1 itself ran from t0 20:53 PST to chain exit before 04:40 PST, about 7.7 h. That night had
ten model members, seven 1,200 s timeouts and three soak releases, and it skipped the gated block. The follow-up has
thirteen model members, G0 waits of about 720 to 900 s instead of 1,200 s, no releases and no retries. I expect
about 9 to 11 h. The magistrate's alarm sits at the window ceiling plus grace, as usual.

**OS batch window.** It runs 11:45 to 13:15 local (`OS_BATCH_WINDOW_LOCAL`). To keep even the no-redo ceiling clear
of it, t0 must be no later than 11:45 − 16.31 h = **19:26 PST**. Any t0 between about 17:00 and 01:00 clears it in the
expected case. `wait_outside_os_batch` covers the worst case either way, at up to 11,164 s per encounter.

---

## Item 9. The native smoke: what it must show

**Plan.** The smoke is a two-segment R1 plan on the built follow-up commit, on the measurement Mac: `anchor_30b`
(W1 e04), then `step_D`. It runs in two parts:

- **Part A**, the gate, about 30 min: the anchor, then step-D's load, idle, capture, warmup and G0.
- **Part B**, the step, about 20 min more: the same step-D continues through its quiet, turn and 600 s recovery, and
  `classify_step` runs.

I recommend running both: Part B is the only pre-night evidence on item 7. If only 30 min are allowed, Part A alone
meets RL-59's text.

**It must show:**

1. **Bytes.** The SHA-256 of `thermal_gates.py`, `workload.py`, `r1_runtime.py`, the driver, `r1_runtime.json` and
   the phase-table module equal the follow-up commit's. `thermal_gates.py` and `workload.py` must equal the W1
   line's, which is condition 13 checked at the source. The digests go in the smoke record.
2. **Anchor.** The anchor runs the W1 e04 config with its digest unchanged, has no thermal policy, ends cleanly, and
   its AC powermode reads back as the requested mode.
3. **Capture.** step-D writes `align_window_reference.json` with status `captured`, 60 samples and coverage ≥ 0.9.
   A desk call of W1's `load_window_reference` with a consume policy pointed at it returns the same values
   (consumer path dry run). R_D is printed beside R_op from the last night, as a diagnostic.
4. **Gate.** step-D's G0 against its own capture releases inside 1,200 s. The replay script, run on the smoke's
   journal, prints the release time, the distance inside the band at release, and the band-only and slope-only
   times, at both 1.5 and 1.0 °C. If it does not release, stop, and the case goes to the lead.
5. **Hooks.** The re-arm event is recorded, and the quiet is 300 s. On the capture member the G0 row's `reference`
   equals the captured record, with `source_member` its own run id, and no hook overrode it.
   `r1.ran_after_g0_timeout` is absent.
6. **Thermometry (Part B).** The inventory journal meets the classifier's bar in every phase, and `classify_step`
   returns picks or a named reason. A null s_slow for the t_band reason confirms item 7's prediction and goes to the
   lead before the night is armed.
7. **Host.** The KM003C DC-in capture is present (Ed's rule). AC present and charged throughout. No agent presence,
   no external volume, and the batch guard inert.
8. **Not native, in synthetic tests before the smoke:** the run-after-timeout hook, the consumer hook's refusal
   path, and the skip-on-unobserved-capture path.

---

## Item 10. Condition 13: W1's thermal-gate module byte for byte; every R1-only behaviour through a hook

**The module.** `joulewise/align/apple/thermal_gates.py` at W1 `b4a6c217f` (blob SHA-256 prefix `c72937bd8bf7`)
differs from `da3187e6e`'s copy (`2d4917b7e499`) only by additions on the W1 side:

- the G0 timing receipt span (no-op unless a writer is bound);
- the R10-2(a) `g0_cap_receipt` and R11 `contrast_fit` policy validation;
- refusal of an unobserved source record (D-14b-1);
- the unobserved limit, min(300 s, cap).

R1 needs nothing inside the module. It takes W1's bytes as they are. The same holds for `workload.py`: W1's
`8730691f4774` against R1's `de9d52cc392b`, a docstring only.

**The hook seam.** `ThermalRegistry(thermal_factory=...)` is W1's public seam. R1's `ProductionBackend.run_member`
factory constructs W1's `ThermalSession` unchanged, then calls `hook(session)`. Every R1-only behaviour is an
instance-level hook installed there, or lies outside the gate module altogether.

| # | R1-only behaviour | segments | mechanism |
|---|---|---|---|
| 1 | G0 on its own cap, outside the member deadman; deadman re-armed after G0 (and after quiet or preheat) | step-30b, legs, step-D, planning | hook: wraps `session.wait` for G0, pops `deadman`, calls W1's `wait`, then `rearm_deadman` (`reference_hook(rearm_s=)`) |
| 2 | 300 s step quiet before prefill | step-30b, step-D | same wrapper (`quiet_s`); after **any** G0 outcome when 3 applies |
| 3 | run-after-timeout (NEW) | step-30b, legs, step-D, planning | same wrapper: if W1's G0 row is `timeout`/`unobserved`, set `session.episode_reference = row["release"]` (the last sample) so the workload's `g0_unreleased` stop does not fire, and append `r1.ran_after_g0_timeout` to `session.flags`. Safe because these policies have `per_turn: False`, so no G1/H reads `episode_reference`. |
| 4 | designed start state | planning | hook: `session.reference = (150, R_D,slow + offset)` before warmup, plus the heater around W1's G0 (`planning_hook`); base changes from R_op to R_D |
| 5 | consume R_D across segment directories (NEW) | planning base, gated, X-G | hook before warmup: `session.reference, session.custody = load_window_reference(consume_policy, ctx)`, where `consume_policy` names step-D's run id and its config SHA-256, and `ctx.bundle_path` is placed in step-D's `runs/` directory. This is **W1's own verifier**, with W1's refusal codes. The member's policy keeps role `capture`, so `ThermalSession.__init__` does not look for a sibling, and `capture_reference` returns early because a reference is set. |
| 6 | capture (R_op, own leg references, R_D) | step-30b, legs, step-D | **none.** W1-native role `capture`. The R1 label `r1_step_30b_pre_warmup` is applied by the R1 runtime when it reads the record, not inside the session. `da3187e6e`'s capture tap inside the wait wrapper is removed. |
| 7 | 1,200 s G0 cap for model members | all model members | policy data (`g0_cap_s`), validated by W1's `validate_gate_policy` |
| 8 | δ bands (S6 floor, soak SD) | all | policy data |
| 9 | full-inventory journal, classifier, heater | step-30b, step-D, planning | R1 runtime code outside the gate module (`InventoryJournal`, `ticker`, `ProcessHeater`) |
| 10 | desk prints (own medians beside R_D and R_op; release margins) | desk | this replay script, not runtime |

**Condition 13's test.** At signing, the R1 driver, the R1 runtime, `thermal_gates.py`, `r1_runtime.json` and the
phase-table module on the W1 line equal the files at the commit that ran this night, and the slots file names that
commit (RL-61). I propose adding `workload.py` to that comparison. The run-after-timeout hook depends on its
`g0_unreleased` stop, and W1 already binds it.

**The build.** It starts from the W1 line, which has the newer `x_g_evidence` and W1-side gate code. It takes
`da3187e6e`'s R1-runtime and driver changes (R_op capture, S6 receipt reader, the 1,200 s cap for every model kind,
the A-B-A and d-4bit re-arm), the RL-61 phase-table move and the changes above. The W1 line then takes those files,
so that they are identical.

---

## D. Disagreements between the seats

(Filled in after the Sol seat's plan was read; see below.)

## E. Ruling requests for the research lead

(See below.)
