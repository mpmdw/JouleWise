# ALIGN v4 condition-based waits: Opus build

Independent Opus 5.5 build of the condition-waits design, under Ed's paired-build rule (RUN_STATE 220, 221 rule 6). A Sol seat builds the same task on `align/2026-11-08-condition-waits-sol`. I did not read it before committing this file.

- **Base:** `align/2026-11-08-v4-r11` @ `05b6d04cb` (protocol `docs/align/pilot_protocol_v4.md` and the kit).
- **Also read:** RUN_STATE items 203-221 on `main` @ `b58a2b2ca`; the latency synthesis (`perf/2026-11-08-latency-synthesis`, D5); the finalize/pre-arm review (`perf/2026-11-08-opus-review-finalize-prearm`, §3); `WINDOW-EFFICIENCY-sol1` §3; LEAD-RULINGS-2 Round 7; `docs/perf/SPEED-TOOLBOX.md` on `main` @ `fd4547e07` (batching).
- **Blinding:** no energy, residual, score or alarm value was read. From committed records I used only timing fields, thermal fields (SMC keys, fans, cooling constants) and state fields (display, contention, battery).
- **Paths:** I opened no restricted path, night-custody or night-archive directory, and no `/Users/edr/jw-b5-*` or `/Users/edr/night-*` path.

**What this delivers:**
- this design;
- `scripts/align_v4_start_state.py`, a stdlib replay and analysis tool that reports timing and predicate outcomes only;
- `tests/align/test_align_v4_start_state.py`, 18 synthetic tests that pass.

The tool is not an arm gate and changes no measured path.

## 0. Bottom line

1. **The between-window "quiet start state" is not defined anywhere today.** It is a triage check whose evidence is a free-text basis string in the off-MBP packet (`joulewise/align/apple/v4_cadence.py:29-31`, `source=PACKET`). The 15-25 min cool-down is a magistrate estimate (RS 213), not a criterion. Replacing elapsed time with a registered start-state band is both faster and more valid. That change is **P1**, my headline proposal.
2. **Most within-window waits are already condition-based**, with floors and caps:
   - G0, G1 and H (thermal gates);
   - the between-member power cooldown gate;
   - the hazard-arm contention dwell;
   - the hazard idle-admission retry.

   The fixed timers that remain are:
   - the 300 s configured idle per member;
   - the 60 s chain settles;
   - the 5 s warmup settle;
   - the post-calibration 20 s countdown;
   - the magistrate's fixed display/quiet dwell between windows.
3. **I do not recommend condition-ending the 300 s member idle for v4** (D5). For D-after-D members the physics says the time would only move into G0, which sits inside the deadman budget, so the net saving is about zero. The downside (G0 timeouts, X2 exclusions, less turn opportunity under ruling 1(f)) is real. The idle is also a registered escalation lever (idle 300 to 450 s). Instead, I propose recording a print-only shadow predicate, computed off-MBP from the sidecar journals that already cover the idle. That gives v5 the evidence that D5 lacks.
4. **Expected saving: about 20 min per window (range about -2 to +30 min)**, out of a 30-45 min turnaround target. The main mechanisms:
   - **P1:** cool-down overlaps finalize and offload, then a 5 min stability interval;
   - **P2:** the separate display dwell goes;
   - the triage packet is built during the stability interval.

   That is about 2.5-3 % of an about 12 h cycle, or about 3.5-4 MBP-hours over the 11-window series (W1 + 7 C + 3 T). The negative end is not a validity loss. It is the case where today's guessed 15 min would have under-cooled against the registered band.

## 1. Inventory of every wait in the v4 W1/D loop

"Fixed" means it ends on elapsed time. "Condition" means it ends on a measured predicate. "Both" means a condition with a fixed floor or cap. Line numbers are on the base unless marked `main`.

### 1a. Between windows (MBP critical path, RS 213 B2)

| # | Wait | Where | Kind | Signal and threshold | Confound controlled | Evidence its length matters |
|---|---|---|---|---|---|---|
| B-1 | Finalize, hash, commit and push the record | magistrate; `run_night` terminal inventories; harvest | not a wait (work), about 5-20 min, unmeasured (synthesis D7) | none | custody | n/a. It is the overlap opportunity for B-2 |
| B-2 | **Cool-down to the quiet start state** | RS 213 step 2; protocol v4 `:776-791`; `v4_cadence.py:29-31` (`quiet_start_state`, PACKET, free-text basis) | **Fixed by judgment** (about 15-25 min), with **no registered signal** | none registered | carry-over heat into the opening scaffold: pre-calibration, the 18-run NEG-8 corpus and bound derivation, start references, and in W1 the four ungated 30B anchors. All of these start from the window-start state (`plan_tree.json` stage graph ordinals 1-6) | Physics only. After a 900 s full load, fans stop about 180 s after load end. Every key then cools on one shared mode, τ about 430-510 s, and no key reaches G0's 0.2 °C/min until 840-1,040 s after the load (LEAD-RULINGS-2 Round 7, R0 re-run 7). **No committed record times a between-window cool-down.** The 15-25 min figure is an estimate |
| B-3 | Battery top-up | `v4_registration.py:388-425` (`battery_arm`, `TOPUP_WINDOW_S` = 1,800 s) | **Condition**: fresh AC, SoC ≥ 99 %, not charging, \|InstantAmperage\| ≤ 200 mA, plus a completed top-up ≤ 30 min before arm | ioreg / `pmset -g batt` | battery assist and charging power inside members | Pilot 10 lost three members to battery charging (W1 §3). This is a state field; no energy was read |
| B-4 | Next-arm triage | `v4_cadence.py:22-74`; `align_v4_session.py:244-315` | not a wait (checks). Arm-computed checks take seconds; the packet is built off-MBP | 14 frozen checks | a broken next window | "Fits in 5 min" is a target (protocol `:813-815`) |
| B-5 | **Display/quiet dwell** | RS 213 step 4; RS 206 ("≥ 5 min before the first census-checked segment"); R0 launcher `DISPLAY_SLEEP_DWELL_S = 300` (`main:scripts/launch_align_r0.py:35`). No W1/D code: the magistrate does it by hand | **Fixed** (300 s) | after `pmset displaysleepnow` | display-on WindowServer/ControlCenter bursts, and the burst of the display-off transition itself | RS 206: with the display off, WindowServer and ControlCenter stay below 0.02 CPU-s/s. The off-transition gave one burst (corespotlightd 0.174, duetexpertd 0.130), then corespotlightd every about 5 min. **No evidence that 300 s rather than a clean-run condition is needed** |
| B-6 | Magistrate exit and t0 margin | watchdog fence; arm install | fixed margin, set by the magistrate | agent census must be empty at t0 | agent activity as contention | Doctrine (`hazards/arm.py:6-8`) |
| B-7 | Terminal-event wake | `perf/2026-11-08-eng-prearm` (watchdog `StartInterval` 300 s) | poll, up to 300 s | marker file | n/a | review §3: about 2-2.5 min mean. Already in flight; not counted again here |

### 1b. In-window, before the chain (HAZARD_PACK driver and hazard arm)

| # | Wait | Where | Kind | Signal and threshold | Confound | Evidence |
|---|---|---|---|---|---|---|
| A-1 | Cadence probe | `hazards/arm.py:260-266` | fixed measurement, about 40 s | powermetrics cadence | instrument hazard | n/a (it measures) |
| A-2 | **Arm dwell** | `hazards/arm.py:24-26, 273-290`; `hazards/contention.py:106-118` (`clean_s` 180, `cap_s` 2,700, `interval_s` 30, `cpu_limit_s_per_s` 0.05); `Dwell` `:562-606` | **Both**: ends at a 180 s run of clean 30 s intervals, cap 2,700 s; a dirty interval resets the run; at the cap, measured contention refuses | max outside process at or below 0.05 CPU-s/s per interval | background contention at GO | Gate-prune 2 A1 cut the clean run from 600 s to 180 s. **The v4 registration has not copied hazard thresholds yet** (none in the kit). It must, before W1 (see §4) |
| A-3 | Network-time-OFF 600 s settle | `run_night.py:3577-3600` | fixed | n/a | n/a | **Not on the HAZARD_PACK path.** The arm runs OFF as an action with no settle (`hazards/arm.py:14-16`). Listed so nobody counts it |
| A-4 | Monitor ready | `b5/driver.py:126-129` | condition, up to 3 × 20 s | journal row | n/a | negligible |

### 1c. In-chain (`joulewise/b5/chain.py`)

| # | Wait | Where | Kind | Signal | Confound | Evidence |
|---|---|---|---|---|---|---|
| C-1 | Settle before the pre slot and before each of the 6 collection stages (7 × 60 s = 420 s per window) | `b5/chain.py:100-105` (`SETTLE_S = 60`) | **Fixed** | none | residual decode activity before a stage's first member | Block-5 timing ruling 2026-10-06: "the machine is at idle within about 15 s of a decode ending, and each first member measures its own idle baseline", which cut it from 180 s to 60 s |
| C-2 | Operator countdown | `b5/chain.py:150-157` (0 s on the pre slot and on collection stages; 20 s on the post slot); `run_campaign.py:1069-1072` | **Fixed** | none | operator presence (unattended windows: none) | 20 s per window, negligible |
| C-3 | Post-chain monitor hold | `b5/driver.py:137` (5 s) | fixed | n/a | battery join coverage | negligible |
| C-4 | G10 clock-step control | `b5/driver.py:112` (300 + 900 + 300 s) | fixed, only if the plan asks | n/a | clock | The v4 kit does not request it (no `g10` in `scripts/align_v4_kit.py`) |

### 1d. Per member (controller and campaign runner)

| # | Wait | Where | Kind | Signal and threshold | Confound | Evidence its length matters |
|---|---|---|---|---|---|---|
| M-1 | Between-member cooldown gate | `run_campaign.py:5071-5110, 5338-5345`; `controller.py:3958-`; policy `configs/campaign_policies/quiet_mac_p2_b5.json` `cooldown` (line 6) | **Both**: package power back to the reference idle mean × (1 + 1.0) over a sustained 5 s window, 80 % coverage, thermal nominal; cap 300 s. With no anchor, a self-referenced two-window flatness test (≥ 30 s, 10 %) | powermetrics package power | the predecessor's power tail | Already a condition |
| M-2 | `settle_s` before idle | `controller.py:3773-3778` | fixed if set | environment `settle_s` | n/a | Not set for v4 members |
| M-3 | **Configured idle baseline, 300 s** (anchors, contrast and D); 57.6 s for corpus and reference members | stage configs `sampling.idle_seconds` (for example `episodes-a/align-v4-episodes-a-e05.json:49`); `scripts/align_pilot_kit.py:41`; `adapters/powermetrics.py:1464-1466` (count = ceil(idle/interval), 3,000 samples at 10 Hz); `controller.py:1784-` | **Fixed**, plus admission (policy `idle_admission_extension`: cpu_busy p95 ≤ 0.5, processor power p95 ≤ 1.0 W, ≥ 30 samples; one retry). The HAZARD idle-wait retries until a 1,500 s cap within a 7,200 s session budget (`b6/idle_wait.py:9-10`) | powermetrics | (i) idle-power baseline and admission; (ii) predecessor-heat recovery before warmup; (iii) the window reference R = medians of the last 60 s of idle in the capture member (protocol `:257-259`); (iv) the KM003C DC-in baseline span (`b5/harvest.py:2040`); (v) anchor comparability with pilots 4-10 (anchor config bytes are pinned) | **None either way** (synthesis D5; W1 §3). 30B pilots observed 389-393 s for a configured 300 s. It is a registered escalation lever (protocol `:500`, idle 300 to 450 s) |
| M-4 | Warmup settle | `sampling.warmup_seconds` 5.0 | fixed | n/a | first-call effects | no evidence; 5 s |
| M-5 | **G0** | protocol `:359-413`; `thermal_gates.py:503-590` | **Both**: 10 consecutive 1 Hz samples with S_fast ≤ R + δ_fast and S_slow ≤ R + δ_slow, \|60 s OLS slope\| ≤ 0.2 °C/min, OS level 0, PM Nominal within 2 s. Cap 600 s; W1's cap is R1-derived in [600, 1,200] s; R10-2(a) G0* for D; contrast caps per R11 | SMC TV0h/Tf08 | start heat and slope at episode start | R0 re-run 7: 840-1,040 s to 0.2 °C/min after a 900 s load. That is why R7-2 raised R1's cap to 1,200 s. Already a condition |
| M-6 | **G1** before turns k ≥ 1 | protocol `:414-416` | **Both**: 5 consecutive samples within bands of the episode's E; cap G_turn = min(300 s, 3 × R1 p95 recovery) | SMC | heat added by earlier turns | R0 replay: G1-like release at 279 s, near the cap. S6 tuning (δ_slow in 0.5 °C steps to ≤ 2.0 °C, median G1 ≤ 90 s) is the registered lever |
| M-7 | **H holds** | protocol `:417-420` | **Both**: G1's reference and cap at N_chunk | SMC | clock decline inside long decode | already a condition |
| M-8 | Gate fallback on unobserved | protocol `:421-423`; `thermal_gates.py:29` (`G0_UNOBSERVED_LIMIT_S` 300) | **Fixed** timed wait, then X4 | failed-read fraction > 10 % | no invented temperature | rare; keep |
| M-9 | Post-window sampling dwell | `align/apple/sampler.py:26`; policy `post_window_sampling_dwell_s` 1.0 | fixed, 1 s | n/a | sampler tail | negligible |

R1-only waits (`r1_runtime.py:73` cooldown cap 1,500 s and `:1613-1636` `k_idle_until_soak`; precools; designed start states; the R1 batch blackout `wait_outside_os_batch`) are out of scope. The R1 lane is frozen while armed (RS 216). They matter here only as evidence: `k_idle_until_soak` is already the condition-based cool-down that P1 generalizes (S_slow ≤ R_soak + δ_slow, one-sided, cap 1,500 s), and it records a `recovery_curve`.

## 2. Condition-based replacements

The principle is **start-state equivalence, not elapsed time**. Each proposal reuses a predicate the protocol already trusts (G0's bands and slope, the idle-admission power bar, the R02 battery predicate, the hazard-arm clean run) rather than inventing a new one.

### P1. Start-state equivalence (SSE) gate replaces the fixed cool-down (B-2), and runs concurrently with finalize (B-1)

| Element | Proposal |
|---|---|
| **Reference** | R1's 30-min idle soak medians (`r1_soak_reference.json`; `scripts/align_v4_thermal_desk.r1_soak_c`) and the S5 bands δ_fast/slow = max(1.0 °C, 3 × idle SD). This is the reference R1's own `idle-until-soak` cool-down uses |
| **Signals** (1 Hz, the existing SMC sidecar reader) | `s_fast` TV0h and `s_slow` Tf08 (the R0 re-run 11 picks, re-classified by R1); fans F0Ac/F1Ac; OS thermal-pressure level and PM state; battery `is_charging` and InstantAmperage. Package power (powermetrics CPU+GPU+ANE) at the idle-admission cadence. Print-only: one chassis key with τ > 300 s as the ambient proxy (chair 19) |
| **Band (all must hold on every sample)** | (a) **level**: S_fast ≤ R_soak,fast + δ_fast and S_slow ≤ R_soak,slow + δ_slow. One-sided: cooler than the soak counts as cooled (R5-1). (b) **settled**: \|OLS slope of S_slow over the last 300 s\| ≤ 0.1 °C/min, with ≥ 90 % coverage. With the shared τ of about 470 s, this bounds the residual to about 0.8 °C above the asymptote, tighter than G0's 0.2 °C/min over 60 s, which is right for a window start. (c) **fans**: each ≤ the R1-soak fan median + 100 rpm. Not "= 0": R0 re-run 7's partial journal shows non-zero idle-phase fan medians, so the soak value is the reference. (d) **status**: OS level 0, PM Nominal. (e) **battery**: not charging and \|InstantAmperage\| ≤ 200 mA (R02), so the heat of a top-up has to settle inside the band. (f) **power**: package-power p95 over the stability interval ≤ 1.0 W, the registered idle-admission bar |
| **Stability interval** | S = 300 s of continuous in-band samples (no gap > 2 s). It must lie **wholly after** the end of finalize, push and offload (`record_committed`) and after charging stops. A failing sample resets it |
| **Floor** | 600 s after authenticated terminal completion (B1). This covers fans-off (about 180 s) plus the stability interval. It costs nothing in practice, because finalize alone usually exceeds it |
| **Ceiling** | The later of terminal + 2,700 s and quiet start + 1,200 s. 2,700 s is about 5.7 τ at 470 s, so a residual of e^-5.7 ≈ 0.3 %. It is also the hazard dwell's own cap. The second term keeps a slow finalize from eating the cooling budget |
| **Signal timing** | The clock starts at terminal completion. `pmset displaysleepnow` runs at the same moment (this subsumes P2). The sampler runs during finalize: it is monitoring only, and finalize's heat is captured because S must start after it |
| **Outcomes** | `released`: arm. `ceiling_level`: everything except level held for the whole last S, and the slow offset above the band is ≤ 3 °C, which reads as ambient or the chassis rather than carry-over. **Arm with a DISCLOSE flag** `start_state.ceiling_level` and record the offset. `hold_level_offset`: offset > 3 °C (U2's G0-range bar). Do not arm; mail Ed and the lead. This is a room-temperature control failure (chair 19 thermostat); one re-check after 30 min. `ceiling_unsettled`: slope, fans, power or status failing at the ceiling, meaning something is heating. Run the existing contention diagnosis; one more SSE attempt; a second failure escalates (RS 221 rule 5: no blind re-run). `unobserved`: > 10 % failed SMC reads. Do not arm; this is a tooling fault for the lead, because every gated member would end X4 anyway |
| **Window counting** | An SSE flag never removes, replaces or re-orders a window, and a flagged window counts toward B3's 8. There is no outcome-dependent selection |
| **How the estimand is protected** | (1) Nothing read is an outcome. The predicates use the channels the registered gates already use. (2) The start state becomes a registered band instead of an unrecorded elapsed-time proxy. That tightens window-to-window comparability for the scaffold, the corpus-derived drift bound and the W1 anchors, which is what R14's exchangeability needs (B3's simulations showed window-level drift is the FPR risk). (3) In-window gates are unchanged: idle admission, G0 relative to the in-window R, G1/H, the arm dwell. (4) The SSE record (`schema joulewise.align_v4.start_state.v1`: trace digest, release time, offset, last failing predicate) is bound into the triage. The desk prints release time and offset as **print-only window covariates**; they enter no registered model unless pre-registered |
| **Implementation** | **Now:** a magistrate-side tool built on `scripts/align_v4_start_state.py`'s predicate, running before arm. No armed code changes. **Later (engineering):** the same predicate inside the launchd job before the hazard arm, so that the magistrate agent can exit at once instead of idling, and adding heat, through the cool-down. That later step is armed code. It needs guard replay and a native smoke (RS 221 rules 2-3). Because it never refuses except on `hold_level_offset` or `unobserved`, its false-refusal exposure is limited to those two |

### P2. The display/quiet dwell (B-5) becomes the arm's own quiet criterion

| Element | Proposal |
|---|---|
| Signal | The hazard arm's contention dwell: 30 s intervals, every outside process ≤ 0.05 CPU-s/s |
| Band and stability | 180 s run of clean intervals (`contention.py` `clean_s`) |
| Floor | the 180 s clean run itself |
| Ceiling | 2,700 s (`cap_s`) |
| Failure | Unchanged: measured contention at the cap refuses (NULL window); missing evidence is UNMEASURED and the arm goes on |
| What changes | The magistrate's separate fixed 300 s dwell is dropped. The display is put to sleep at the **start** of P1, so the off-transition burst (RS 206) falls inside the cool-down, at least S + arming time ≥ 5 min before t0. The arm dwell then judges quiet on the guard's own criterion |
| Estimand protection | The registered contention guard is unchanged and is the authority. Display state stays recorded and required asleep by the campaign environment guard (`require_displays_asleep`) per member |
| Precondition | The v4 registration must copy the hazard thresholds (`clean_s` 180, `cap_s` 2,700, `interval_s` 30, limit 0.05) from the contract. They are absent from the kit today, and the W1 HAZARD_PACK plan needs them in any case (`b5/plan.py:555-558`) |

### P3. Member idle (M-3): keep 300 s for v4; add a print-only shadow predicate (D5 evidence)

A condition-ended idle would be: floor 120 s; then end when G0's own predicate (bands relative to the window R, 60 s slope ≤ 0.2 °C/min, OS 0, PM Nominal) has held 10 consecutive samples; ceiling 300 s, so never longer than today. On failure the idle runs to 300 s exactly as today. It would exclude the anchors (pinned bytes), the R-capture member (R is not yet known there), both sentinels (matched predecessors, CHAIR 1(g)) and the contrast members (pilot-7 identity).

I recommend **not adopting it for v4**, for four reasons:
1. **Net saving ≈ 0 where it matters.** For D-after-D, the power cooldown gate (≤ 300 s) plus 300 s idle is ≤ 600 s, against 840-1,040 s to reach the slope criterion after a heavy load (Round 7). The predicate would rarely hold within 300 s. Any idle it did cut would reappear as G0 wait, inside T_dead and therefore against turn opportunity (R10-1, ruling 1(f)).
2. **Yield risk.** A shorter idle with a fixed G0 cap raises the probability of G0 timeouts, which are X2 exclusions.
3. **It changes four other things.** Idle doubles as the idle-admission sample (p95 statistics over fewer samples change the false-refusal rate), the KM003C baseline span and I_D. It is also a registered escalation lever (300 to 450 s), and that step loses its meaning if idle is variable.
4. **Scope.** Only 1-2 D members per window follow a light predecessor (after a reference stage). Upper bound about 3-7 min per D window.

**What to build instead (pure engineering, no control effect):** `align_v4_start_state.py idle-shadow` computes, from each member's own sidecar journal (the 1 Hz sidecar already covers idle), when G0's predicate would first have held during idle. Run it off-MBP on R1's gated runs and on W1. If the lead wants a decision before the calibration series, it can be made **before C1** on these timing fields alone, all-or-nothing for C1-C8 and the test windows. W1 is development data, so a pre-C1 switch does not break calibration exchangeability. My default is to defer to v5.

### P4. Chain settles (C-1): not recommended for v4

A power condition could replace the 60 s settle: floor 15 s; end when package power ≤ the idle bar for 15 s; ceiling 60 s. The saving would be ≤ 6 × 45 s ≈ 4.5 min per window, keeping the pre-slot settle before the fiducial calibration.

It is not worth it. `SETTLE_S` is a block-5 registered constant shared by every HAZARD_PACK window, and `chain.py` is a shell-rendering module under the refusal census. The value does not justify touching pinned shared code. Revisit only if the window timing worksheet shows settles are not idle.

### P5. Battery top-up time-stamped by the SSE tool (B-3): engineering

The SSE sampler already watches `is_charging`, SoC and current. It records `topup_completed_at` as the first sample after charging with `is_charging` false and SoC ≥ 99 %, and passes it with its source to `--topup-completed-at` and `--topup-source`. The R02 predicate and the 30 min window are unchanged. This removes a manual and possibly sequential step, and P1's battery predicate keeps charging heat out of the start state.

### Batching and overlap (SPEED-TOOLBOX lever 4, coordinator note)

- **Finalize, harvest and compressed offload:** these overlap the cool-down under P1 at no cost to the start state. P1's stability interval starts only after they end, so their heat is judged by the same band.
  - The toolbox puts the harvest at about 88-109 min per window. While that stays on the MBP, the whole cool-down hides inside it.
  - Moving the harvest off the MBP (toolbox lever 2) is then the larger saving, and P1 makes the cool-down after it short.
- **Batched unmeasured inference** (screens, attack-policy development, ladder selection): **n/a during the cool-down.** It adds heat, so the SSE predicates would not release, and it would cost its own duration plus extra cooling.
  - It may run in a between-window gap **before** the SSE clock starts, as MBP busy time that lengthens that turnaround. It is worth doing only for work that must run on the MBP; otherwise use the Air or the x86 desktop.
  - Measured members stay batch-1, whatever the placement.
- **Model warm-up: n/a.** Every measured member uses a fresh process with its own warmup. A warm-up before the window does not carry into later processes (W1 §3).
- **Kit regeneration, desk, reviews and the triage packet:** off the MBP (RS 213), built while S runs.

## 3. Evidence plan

### 3a. What committed records already show (timing, thermal and state fields only)

| Source | Fact | Bears on |
|---|---|---|
| LEAD-RULINGS-2 Round 7 physics input (R0 re-run 7 SMC journal) | After a 900 s full load: fans stop about 180 s after load end; one shared cooling mode, τ about 430-510 s; no key at 0.2 °C/min until 840-1,040 s; G1-like release at 279 s; aliased keys (TCMb = TVD0; Tf24/Tf2D/Tf2E) | P1 floor, slope bar and ceiling; P3 net-zero argument |
| R0 classifier (protocol `:236-239`, R0-L2) | The slow class requires 60 < τ ≤ 300 s and a band hold τ·ln(rise/1 °C) ≤ 300 s after the 900 s step; Tf08 was picked (re-run 11). Its numeric τ is **not committed** (the reports stay on the Mac; NOTE.md) | P1 stability S = 300 s |
| R0 re-run 11 NOTE | Display dwell 300 s with no wake; the SMC capture was uncontended (0 redos, 0 flagged intervals) with the display off | P2 |
| RS 206 | With the display off, WindowServer and ControlCenter stay < 0.02 CPU-s/s. The off-transition gave a single burst (corespotlightd 0.174, duetexpertd 0.130), then corespotlightd bursts about every 5 min | P2: the clean-run criterion, not 300 s, is what matters |
| RS 205 | Known schedule of contention sources (trustkit about xx:31, softwareupdated, the /tmp cleaner, XProtect, daily maintenance) | the P1 `ceiling_unsettled` diagnosis |
| W1 §3 (P3 lines 17-19) | 30B pilots' observed idle stage 389-393 s for a configured 300 s | M-3 overhead |
| Pilot 10 (W1 §3) | Members lost to battery charging and one to thermal level 1 | P1 battery predicate; B-3 |
| R0 re-run 7 committed report (`report.json`, fan F0Ac row) | Idle-phase coverage only 12 %; non-zero idle fan median | P1 fans are judged against the R1 soak, not 0 rpm |
| **Missing** | Any timed between-window cool-down; finalize duration (D7); D-member idle versus G0 timing | the native run below and R1 |

### 3b. Free evidence from R1 (no extra MBP time)

- **Post-D cooldown curve:** R1's `cooldown_after_D` (`idle-until-soak`) records `recovery_curve` and `released`. That is time-to-(soak + δ_slow) after a full D episode, which is P1's level predicate.
- **Soak reference and bands:** the 30-min soak gives R_soak and δ.
- **Idle shadow:** the gated runs' sidecar journals give P3's shadow timing.

Run `align_v4_start_state.py` off-MBP on copies of these journals. It reports timing and predicate outcomes only.

### 3c. Native characterization run CW-1 (≤ 2 h, magistrate, in a gap; labelled non-registrable)

Run it after R1, so that R1's soak and δ exist. Preconditions:
- display asleep, AC power, Spotlight paused as for R0;
- no agent session alive except the sampler;
- not inside 11:45-13:15 or a listed schedule minute (or record it).

| Step | Duration | What it does | Records |
|---|---|---|---|
| 1. Soak | 15 min | idle, sampler only | confirms the soak reference on the day; ambient offset |
| 2. Heavy load | 25 min | one D 8-bit decode with the R0 long-decode harness (no scoring) | end-of-member heat |
| 3. Light tail | 8 min | three 1.5B reference-corpus runs (the window's end-reference workload) | the window's actual end state |
| 4. Simulated finalize | 10 min | sha256 over a 20 GB synthetic tree plus a zstd copy | finalize and offload heat, I/O |
| 5. Cool-down observation | 40 min | `pmset displaysleepnow` at the start; sampler only; SMC 1 Hz, fans, OS/PM, battery, powermetrics package power | P1 release time; first-pass time per predicate; the `--grid` sensitivity (slope 0.1 and 0.2 °C/min × S 120, 300 and 600 s); top-up time if SoC < 99 %; the display-off burst against a replayed 180 s clean run |
| 6. Spare | ≤ 20 min | repeat step 5's arm-dwell replay if a scheduled job interfered | |

Each proposal is settled as follows:
- **P1** is adopted with the defaults if CW-1 and R1's post-D curve both release before the ceiling, and if the grid shows S = 300 s within 2 min of S = 120 s (otherwise take the shorter S the grid supports).
- **The guard replay** (RS 221 rule 2) runs the tool on R0 re-run 11's idle phase, R1's soak and CW-1's soak, and reports the rate of `hold_level_offset` and `unobserved` on idle traces. The required bound is 0 on idle traces.
- **P2** is confirmed if the replayed arm dwell reaches READY within ≤ 10 min of display sleep.
- **P3** is decided from R1 and W1 shadow timing alone.

### 3d. Expected saving per window

Turnaround today follows RS 213, sequentially: F + C + T + D. Proposed: max(F, C_band) + S, with T built during S and D removed.
- F: finalize, push and offload, about 5-20 min, unmeasured.
- C: cool-down, about 15-25 min.
- T: triage, ≤ 5 min.
- D: display dwell, 5 min.
- C_band: time to the band after terminal completion, unknown. R0 physics suggests about 5-20 min, because the window ends on light stages.
- S: stability interval, 5 min.

| Proposal | Saving per window | Range | Basis |
|---|---|---|---|
| P1 SSE concurrent with finalize | about 15 min | -2 to +25 min | central F = 10, C = 20, C_band = 12: 30 → 17 min. Worst: F = 5, C = 15, C_band = 25 (+2 min, a validity gain, not a loss). Best: F = 20, C = 25, C_band ≤ 15 |
| P2 display dwell dropped | 5 min | 0-5 min | fixed 300 s removed; the arm dwell existed already |
| Triage built during S | 0-5 min | | T overlapped |
| P5 top-up stamp | 0-5 min | | only when a top-up was sequential |
| **Total (P1 + P2 + overlap)** | **about 20 min** | **about -2 to +30 min** | of a 30-45 min target turnaround; about 2.5-3 % of an 11.8-12 h cycle; about 3.5-4 MBP-hours over W1 + 7 C + 3 T |
| P3 member idle | 0 for W1 | 0-7 min per D window, only if adopted before C1 | physics argument above |
| P4 settles | 0 (not recommended) | ≤ 4.5 min | |
| Terminal wake (already in review) | 2-2.5 min mean | 0-5 min | not counted above |

These are planning ranges from code and committed timing fields. Per the toolbox's measure-first rule, none counts as a saving until CW-1 and the first real turnaround give a before-and-after. Track the result in the per-window phase-timing worksheet.

## 4. Registered-design changes versus pure engineering

v4 is not registered yet, so the registered items go into the registration text before W1, not into the deviation log (as R12 did).

| Item | Class | Why |
|---|---|---|
| P1 SSE definition: signals, band, S, floor, ceiling, outcomes, window-counting rule, print-only covariates | **Registered design** | It defines the gating `quiet_start_state` triage check and the window start state. The triage evidence source changes from a free-text PACKET basis to an SSE record digest (`v4_cadence.py:29-31`, protocol `:791`). The frozen list keeps the same 14 ids; no check becomes non-gating |
| P2 drop the separate display dwell; copy the hazard thresholds into the v4 registration | **Registered design** (the thresholds) plus a procedure change | The thresholds are registration inputs (`b5/plan.py`). Dropping a magistrate step is procedure |
| P3 shadow predicate | **Engineering** | Off-MBP, print-only, no control effect |
| P3 condition-ended idle (if ever adopted) | **Registered design**, decided before C1 on timing fields only, or in v5 | It changes a registered member parameter and the escalation ladder's meaning |
| P4 settles | Registered (block-5 constant); not recommended | |
| P5 top-up stamp | **Engineering** | R02 predicate and window unchanged |
| SSE tool on the magistrate side; triage built during S; display sleep at the start of the cool-down | **Engineering** | No measured path is touched |
| SSE inside the launchd job (later) | **Engineering, armed code** | Needs guard replay, a native smoke, an executing review, and paired Sol/Opus builds (RS 220-221) |
| G0/G1/H, idle admission, cooldown gate, arm dwell | **Unchanged** | Already condition-based; their registered levers (S6 tuning, R10-2(a), R7-2) stand |

Nothing here touches blinding, custody digests, the GPU residual estimand, batch-1 measured episodes, the full-desk gate after W1 or after a code change, or the paired-build rule.

## 5. Notes for the agreement step

- `tests.hazards.test_refusal_allowlist` already fails on the base `05b6d04cb`, before this change (checked with the change stashed). The new script is not on the HAZARD import path.
- The SSE tool and its tests are stdlib-only. They read journals given on the command line and write JSON to stdout.
