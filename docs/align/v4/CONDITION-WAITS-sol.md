# Condition-based waits — independent Sol design

2026-11-08. **Proposal; not registered, implemented, or hardware-qualified.**
Baseline: `05b6d04cb` (`origin/align/2026-11-08-v4-r11`). This is the Sol
build required by RUN_STATE item 220. An independent Opus build, agreement
report and lead ruling must precede adoption. I did not read a peer's
condition-waits design. The earlier latency synthesis and the explicitly
cited Opus engineering review are context, not that independent build.

**Recommendation:** specify and qualify a joint, measured between-window
start-state release; stop adding discretionary time after its conditions
hold. Keep the 300 s member idle, G0/G1/H, stage settles, calibration and
sampling tails for v4. Most named thermal waits already release on a
condition. Changing their caps does not save their unused allowance.

The plausible recurring gain is **minutes per window**, conditional on
observations, with **zero saving established today**. The observed long
thermal tail makes an unconditional “five-minute cooldown” unjustified.
The potentially larger 54 min/D-window idle saving remains a new design
question, already deferred by the lead, not an engineering optimization.

## Scope, authority and evidence boundaries

Only repository code, designs and committed timing/thermal/context records
were used. No real measurement directory, restricted directory, model
payload, Block-5 analysis or network service was opened or run. Absolute
record locations in prose were treated as text. No live characterization
was performed; the running analysis job was left alone.

Local file:line citations below refer to the baseline unless qualified.
Historical records are Git objects, not instructions to open their original
paths. Source abbreviations:

| ID | Immutable source / location | What it supports |
|---|---|---|
| AUTH | `b58a2b2ca` (local `origin/main` snapshot), `RUN_STATE.md`, items 209, 213–220 | R0 display floor; cadence; retained idle/gates; paired builds. Item 217 and the baseline fix calibration at **8** windows, superseding the synthesis's adaptive count stop. |
| SYN | `55029b860`, `docs/perf/2026-11-08-latency-synthesis.md`, §§1, 3 B4, 5 D5 | No idle/gate ablation; scenario arithmetic; proposed eight-pair 30B study takes 2–4 h. |
| REV | `f551a6749`, `docs/perf/2026-11-08-opus-review-finalize-prearm.md`, §§2a, 3 | 15–25 min cooldown is an operational estimate; quiet dwell dominates; a static packet cannot certify fresh host physics. |
| P8 | `b58a2b2ca`, `docs/process_traces/2026-11-05-magistrate-c110a6c9/RECORD.md:29` | Pilot 8 thermal level 1 at four samples, starting 223 s into the member; does not identify a sufficient idle duration. |
| P9 | same commit, `docs/process_traces/2026-11-05-magistrate-f775edaf/RECORD.md:13` | Pilot 9 reports no thermal flag, but contention/idle flags remain. |
| P10 | same commit, `docs/process_traces/2026-11-05-magistrate-3efb8793/RECORD.md:18` | Three charging exclusions (21.5–30.5 W at about 95% SoC), then a thermal-level-1 exclusion at line 19. A float arm snapshot is insufficient for the whole window. |
| R08 | `origin/records/2026-11-07-align-r0-v4-rerun8`, `docs/align/r0/2026-11-07-rerun8/NOTE.md:9` | 30.1 s interval, frauddefensed 0.092 CPU-s/s against 0.05. |
| R09 | `origin/records/2026-11-07-align-r0-v4-rerun9`, `docs/align/r0/2026-11-07-rerun9/NOTE.md:9` | WindowServer 0.0838 and ControlCenter 0.0570 over 30.7 s; display on; transient. |
| R10 | `origin/records/2026-11-07-align-r0-v4-rerun10`, `docs/align/r0/2026-11-07-rerun10/NOTE.md:8` | Display stayed off; routined still exceeded 0.05 at 0.0521 over 35.9 s (line 12). |
| R11 | `d8bc5baa1`, `docs/align/r0/2026-11-08-rerun11/NOTE.md:26` | Fast TV0h (TV1h alias), slow Tf08; **PROVISIONAL**. Line 34 records the 300 s display dwell; lines 7 and 40–41 say detailed SMC/report bytes remain off-repo. |
| TAIL | `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:319` | Recorded physics input: after 900 s load, G0 slope reached only after 840–1,040 s; G1-like release 279 s; fans stopped about 180 s; late common cooling tau about 430–510 s. This is a cited observation, not a new reanalysis. |

D-077 (`docs/decision_log.md:4085`) controls environment admission and
cooldown provenance. Its default sustained 30 s / 10% rule is **not** the
currently selected ALIGN campaign sidecar: the actual B5-derived policy has
5 s / 100% recovery tolerance. Do not silently replace one with the other.
The thermal protocol and LEAD-RULINGS-2 own the more specific ALIGN G0/G1/H
rules. R0-L3's relaxed *engineering-check* contention handling is not a
license to weaken claim-window admission.

## 1. Inventory: what actually waits

FIXED means elapsed time or a fixed observation count; CONDITION means
state-dependent release with a cap; BOTH means a minimum observation/stability
window plus state. All caps below are deadlines, not time to spend. Values
that remain R1 slots are not filled from guesses. Scope includes inherited
scaffold waits, not just the ALIGN episode runner; subprocess polling and
TERM/KILL grace periods are implementation bounds, not experimental dwells.

| Wait / location (file:line) | Class and actual release rule | Confound or purpose; duration evidence |
|---|---|---|
| Between-window cooldown: `docs/align/pilot_protocol_v4.md:777`; `joulewise/align/apple/v4_cadence.py:29` | **CONDITION, incompletely specified**: machine returns to quiet start state, then triage/dwell. The 15–25 min in REV is an estimate, not a registered fixed timer in this checkout. The triage entry is a packet status, not an SMC evaluator. | Thermal history, fans, idle power and contention. TAIL supports a long physical tail; no per-window time-to-full-band distribution exists here. |
| Terminal release, finalize, next-arm triage: protocol v4 `:763`, `:776`; `scripts/align_v4_session.py:244`, `:293`; `v4_cadence.py:23` | **CONDITION**: authenticated terminal result, chain/courier closure and empty censuses; committed record; **all 14** triage entries, full desk after W1 or a code/config change. No fixed “night” wait. | Prevents concurrent agent/hash/I/O load, stale evidence and carrying unresolved faults forward. REV's event wake removes polling latency only; no physics saving. |
| Installation lead and scheduled t0: `scripts/bytes_h_session.py:39`, `:318`; `joulewise/b6/driver_lane.py:185` | **FIXED scheduling constraint**: default lead 420 s, minimum 300 s; t0 rounded up to a minute. Not 300 s of measured quiet. | Installation/stand-down safety. Preparation can occur earlier, but this does not certify recovery. Do not double-count the lead as an additional cooldown if they overlap. |
| R0 display prep: **AUTH** `scripts/launch_align_r0.py:35`, `:195` | **FIXED 300 s**, after requesting display sleep. Request failure is recorded; sleeping 300 s alone does not prove display off. AUTH item 209 explicitly makes a production R0 dwell below 300 s inadmissible. This launcher is absent from the baseline checkout. | Display compositing and the sleep-transition burst. R09 versus R10 supports sleeping the display, not the exact five minutes. R11 used five minutes; no shorter comparison. |
| R1 display floor: AUTH item 206, next step (2), and item 209 | **BOTH, operational instruction**: display asleep at least 5 min before first census-checked segment; plus R1's native gates. Not a blanket replacement for the arm guard. | Same display confound. No measured justification for 300 versus 180 s; retain until explicitly superseded. |
| Native HAZARD arm dwell: `joulewise/hazards/arm.py:267`; `joulewise/hazards/contention.py:10`, `:107`, `:638` | **BOTH**: 30 s direct cumulative-CPU intervals, no outside process >0.05 CPU-s/s; READY after 180 s clean, cap normally 2,700 s. Registered aggregate limit, if present, is conjunctive. Dirty/failed intervals reset; the documented counter-regression-only unknown neither adds nor resets clean time. Final clock, battery, thermal and agent reads follow. | Background contention and clock observation. Already early-exits. R08–R10 prove bursts occur; none proves longer dwell predicts fewer future bursts. Keep the guard's actual unknown semantics. |
| B6 precheck dwell: `joulewise/b6/precheck.py:38`, `:595` | **BOTH**: same 180 s clean criterion, but default cap **600 s**; clock series minimum 60 s; ordinary retry recommendation 300 s (clock path 600 s). These defaults can be overridden by bound registration. It is a diagnostic/pre-session route, not a second mandatory ALIGN dwell by name alone. | Cheap readiness screen. Do not add precheck + native-arm durations without establishing both actually execute. A precheck does not replace fresh GO reads. |
| Legacy clean dwell: `joulewise/prewindow.py:30`, `:113`; `scripts/run_night.py:3919` | **BOTH**: 600 s continuous clean with 30 s checks, cap 2,700 s. Qualification explicitly binds the native receipt rather than repeating the ten minutes. This is a different lane from HAZARD's 180 s. | Environment recovery. Historical/default policy, not evidence that ALIGN needs 600 s; not an extra 600 s to subtract from the current HAZARD path. |
| Fresh physical pre-arm checks: `scripts/align_v4_session.py:259`, `:274`; protocol v4 `:601`; `joulewise/hazards/arm.py:221`, `:292` | **CONDITION**: frozen series AC power mode; no external/network/FUSE volume; AC, not charging, ≥99%, absolute current ≤200 mA, UpdateTime age 0–180 s; completed-top-up source/time ≤30 min old and OBC-off attestation. At native GO, battery/thermal/clock/census are re-read. No elapsed timer can make a failed check pass. | Battery flow, mode, filesystem load and contention. P10 demonstrates charging later in a window despite a start check. Top-up completion is distinct from observation freshness. |
| Chain stage settles and countdowns: `joulewise/b5/chain.py:100`, `:154`, `:940`, `:1157`, `:1201`, `:1252` | **FIXED**: 60 s before pre-calibration and collection stages, including final references/spares when dispatched; pre/collection countdown 0, closing-calibration countdown **20 s**. Number of settles depends on rendered stages, not “11” for every future plan. | Transition/background settling and operator departure. Code cites the prior 180→60 s ruling and about 15 s recovery to idle; this is not proof of full SMC recovery. Keep calibration/scaffold timing. |
| Controller environment pre-idle settle: `joulewise/controller.py:175`, `:3716`, `:3773` | **FIXED 2 s** where environment capture installs `settle_s`; then baseline observation. | Probe/transient settling. No ablation; small cost. Not the chain's 60 s settle. |
| ALIGN member idle: example config `configs/campaigns/align_v4/stages/episodes-a/align-v4-episodes-a-e05.json:49`; protocol v4 `:84`; `scripts/align_v4_kit.py:315` | **FIXED observation target**: configured 300 s, fresh process per member. PM capture counts are `ceil(idle_seconds / interval_s)`, not a precise 300 s wall sleep (`joulewise/adapters/powermetrics.py:1464`). Protocol v3 `:17` records **389–393 s observed** with idle 300; no D transfer assumed. | Baseline/admission and some predecessor cooling; member 5's last 60 s supplies window R. SYN D5: no 60/120/300 ablation, no evidence either way about residual benefit. |
| Idle-admission wait/retry: `joulewise/controller.py:2044`; `joulewise/b6/idle_wait.py:10`; `configs/campaign_policies/quiet_mac_p2_b5.json:28` | **BOTH**: complete baseline attempt plus admission criterion; HAZARD repeats observations within effective per-member cap min(1,500 s, remaining 7,200 s session budget), not an extra fixed sleep. Configured retry backoff is ignored there. GPU idle suspect criterion, CPU power p95 ≤1 W, and evidence coverage remain; busy-fraction-only >0.5 is specifically flag/admit on HAZARD, not another hard wait (`controller.py:2114`). | Contention/idle-power contamination. Failed attempts retained; cap/budget ends in member abort/skip flag, not an invented passing baseline. R08–R10 show why a fixed delay cannot guarantee admission. |
| Legacy admission retry: `joulewise/controller.py:1953`; B3 policy `configs/campaign_policies/quiet_mac_p2_g2a_b3.json` | **FIXED + CONDITION**, only outside the HAZARD waiting path: one retry, optional policy backoff; B3's 300 s backoff is historical. | Avoids immediately repeating a contaminated baseline. Not a 300 s penalty on every current ALIGN member. |
| Campaign cooldown before members: `scripts/run_campaign.py:11100`; `joulewise/controller.py:3959`; selected sidecar `configs/campaign_policies/quiet_mac_p2_b5.json:6` (bound by ALIGN plan tree `:48`) | **BOTH**, already adaptive: duration-weighted power ≤ reference ×2, Nominal, ≥80% coverage of complete **5 s** window, 5 s captures, cap 300 s; no absolute ceiling configured. First physical member exempt. Fallback tries eligible baseline/anchor; no-reference self-comparison instead uses **two ≥30 s windows**, ≤10% difference (`run_campaign.py:5073`, `:5305`). | Gross thermal/power recovery, not the precise SMC start state. Eligibility/provenance and cap flags remain. D-077's general 30 s/10% text must not be reported as this selected 5 s/100% policy. |
| Warmup and settling: `joulewise/controller.py:2444`; example member config `:51`, `:61` | **FIXED work + 5 s** post-warmup settle, normally one neutral benign warmup; G0 follows. | Kernel/cache warm state and RNG/cache equivalence; not just cooling. WP19 identity requirements apply. No evidence that deleting this preserves trajectories. |
| G0: protocol v4 `:356`, `:359`, `:362`, `:373`, `:388`; `joulewise/align/apple/thermal_gates.py:527` | **BOTH**, already adaptive: ten consecutive 1 Hz samples, fast/slow ≤ fixed R + δ; δ=max(1°C,3×idle SD), slow trailing-60 s slope within ±0.2°C/min, OS level 0, PM Nominal age ≤2 s. Normal cap 600 s; R1 selected roles 1,200 s; W1 derived clamp and contrast cap / signed D G0* receipt rules below. | Start-state thermal equivalence. TAIL justifies observing slow recovery; no direct D residual-equivalence evidence. Timeout is not release: current v4 ends before turn 1, X2 (or X4/X7), no episode reference. Older generic documentation saying “proceeds” is not the current v4 member behavior. |
| G1: protocol v4 `:414`; `thermal_gates.py:529`, `:562` | **BOTH**: before turns k≥1, five consecutive samples in one-sided fast/slow bands relative to **that episode's G0 release E**, never a moving per-turn reference. Cap G_turn=min(300 s,3×R1 p95 recovery). | Within-episode heat accumulation. TAIL's G1-like 279 s illustrates a real wait near the cap. Timeout X2 stops before next chat; no shortened timer proposed. |
| H: protocol v4 `:417`; `thermal_gates.py:299`, `:503` | **BOTH**: heavy D pauses at fixed N_chunk, except final token/cap; drain/synchronize native lookahead as owned work first, then G1's five-sample E-band/cap. N_chunk is R1-derived. | Decode heating/DVFM. Drain must precede the unowned hold boundary. No evidence permits fewer holds or speculative dispatch. |
| Unobserved gate / deadman: protocol v4 `:421`; `thermal_gates.py:547`, `:580`; `docs/align/thermal_gates.md:115` | **FIXED fallback + deadlines**: >10% missing/failed slots in 60 s latches X4; G0 waits min(300 s, armed G0 cap), G1/H their cap; deadman can stop earlier. Missing status source/collector fails outright. Unreleased G0 ends member; G1/H actual timeout/deadman stops. | Prevents missing evidence masquerading as cool state. Gates consume the deadline anchored at G0 entry. These waits are excluded trajectories, not useful recovery opportunities. |
| Sampling readiness, closing tail and post-idle sentinel: `joulewise/adapters/powermetrics.py:60`, `:1021`, `:1464`; `joulewise/controller.py:2528`, `:2615` | **CONDITION + FIXED observation**: readiness/whole-second rollover each bounded by 15 s; ≥1 s configured post-window sampling dwell, then bounded native-record drain; post-idle sentinel requests max(3 sampling periods, min(5 s, observed baseline duration)), with at least three records. It is not another 300 s baseline. | Clock alignment, interval coverage and drift evidence. A tail outside measured runtime can still be essential to its validity. Do not delete it as idle “waste”. |
| Agent-interruption hold: `joulewise/b6/agent_pause.py:11`, `:77`, `:197`; `scripts/run_campaign.py:11078` | **BOTH**: future members pause; resume on clean census ≥600 s since last sighting; cumulative pause limit 7,200 s; marker polled every 5 s with stale-driver handling. | Agent contention; overlapping units remain excluded. Zero cost if no intrusion. Shortening changes recovery/exclusion rules, not ordinary cadence. |

### R1/R0 characterization waits, not recurring D-window overhead

| Location | Class / release and purpose | Evidence / disposition |
|---|---|---|
| R0 SMC step: `docs/align/r0_desk_runbook.md:36`; `joulewise/align/apple/smc_enumeration.py:261` | **BOTH** idle floor 300 s, ceiling 1,200 s, ten consecutive trailing-60 s slope passes (±0.2°C/min) for eligible low-noise keys; fixed load **900 s**, fixed recovery **600 s**. At idle cap proceeds with baseline flags; empty qualifying-key case is explicitly indeterminate, not “settled”. | Already condition-based. `joulewise/align/r0_host.py:32` cites median settle ~930 s/max 1,038 s. Load/recovery are observation design, not dispensable cooling. |
| R1 soak: `scripts/align_r1_rehearsal.py:518`, `:920`; runtime contract `:65` | **FIXED + CONDITION**: 1,800 s soak, last **1,200 seconds** ≥0.9 Hz valid observations, slope ≤0.2°C/min; unstable soak redone. Supplies R/noise/bands. | Long observation estimates slow drift and noise. Do not substitute ten G0 samples for twenty minutes of evidence. |
| R1 step quiet/recovery: `joulewise/align/apple/r1_runtime.py:1463`; `scripts/align_r1_rehearsal.py:104`; protocol v4 `:243` | **FIXED** 300 s quiet **after G0** before step prefill, fixed 600 s post-load inventory recovery. A-B-A uses 65 s G0 pre-roll and its own condition release. | Needed to characterize response/aliases and match classifier definitions. Separate post-30B 600 s cooldown was already removed (R6-6); no new saving to claim. |
| R1 post-D/calibration precools: `r1_runtime.py:1613`; runtime contract `:68`; `scripts/align_r1_rehearsal.py:524` | **CONDITION**: first valid S_slow≤soak R+δ_slow, cap 1,500 s; no multi-sample stability required by this helper. Post-D precool also serves the first designed state; later states and timeout retries get their own. Non-release recorded, not itself refusal; no valid samples fails. | Already faster than a mandatory 25 min. Subsequent G0 supplies the stronger start check. Strengthening this helper adds a design change; do not pretend its current test is the proposed joint check. |
| R1 designed-state preheat: `r1_runtime.py:1494`, `:1518` | **CONDITION + ceiling**: heater until target−margin or 900 s, then controlled target R+4/+2/+0°C and ordinary G0; heater stops before episode, deadman rearmed afterwards. | Deliberately varies initial temperature to qualify U5. Cannot replace it with cooling to one state. |
| R1 gated D / X-G sequence: `docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-2.md:168`; `r1_runtime.py:1842` | **FIXED member idle + CONDITION G0**: only W1's own 300 s idle between matched predecessors, no extra cool-to-band. | Additional cooldown would make R1 understate W1's G0 duty. Never insert the between-window proposal between these members. |
| R1 OS batch avoidance: `scripts/align_r1_rehearsal.py:980` | **Schedule CONDITION**: segment must end before 11:45 or start after 13:15 Pacific; otherwise sleep to 13:15. Delay can be **segment bound+5,400 s**, not just 5,400 s (11,164 s for step-D). | Controls known contention; SYN D2 / AUTH 214–216 correct stale bounds. Live quietness is not evidence to waive this rule. D-window blackout policy remains lead-owned. |
| R1 retry/redo releases: runtime contract `:90`; `scripts/align_r1_rehearsal.py:66`, `:168` | **CONDITION + bounded repetition**: G0-timeout calibration state precools then retries once; heavy quiet-segment redo uses G0-style release (65 s pre-roll, 600 s cap), with ruled retry counts and guards. | Preserve rejected first attempts; ceilings include retries. No “keep trying until success” optimization. |

The G0 cap details matter: ordinary W1 cap is
`clamp(ceil(1.25*max counted R1 gated D/X-G waits),600,1200)` with censored
waits counted at the full R1 cap. A signed R10-2(a) receipt can instead size
D's G0* below 600 from the decode/hold budget; contrast always has its
R11 evidence-bound available-span cap, potentially zero. These are not
minimum wait lengths. Keep role-specific caps, X2/X4/X7 outcomes, and all
first outcomes (`pilot_protocol_v4.md:362–412`).

## 2. Proposed releases

### P1 — joint between-window state, before the next native GO

This replaces an informal amount of cooling with an auditable admission
policy. It **does not** replace any member baseline or G0. Since the
start-state definition is currently incomplete, this is a **registration
decision**, even if called an engineering cooldown.

Freeze a clean reference vector **Q** linked to the qualified R1 evidence,
under the adopted series mode, unchanged physical setup and display off.
Q is distinct from **R**, which W1 must still capture from member 5, and from
episode **E**. Use the last 1,200 s of a stable reference soak for temperatures;
fan/power channels must also have a qualified contemporaneous reference.
R1's initial soak precedes the power-mode A-B-A: if High Power is adopted or
R1 changes sensor picks, that initial soak cannot automatically supply Q in
the final mode/keys. A prospectively approved reference capture in the native
diagnostic below can fill this gap before registration; otherwise Q stays
unavailable. Do not infer missing channels from SMC capture duration or
choose a convenient previous window. Bind the baseline, sensor identities,
mode/setup, channel units, noise statistics and policy digest.

The following are **proposed constants/formulas**, not measured optimal
values or filled R1 slots:

| Component | Signal and proposed band | Stability / floor / ceiling | Failure outcome |
|---|---|---|---|
| Temperature | R1-final fast/slow SMC picks. R11 TV0h/Tf08 are bootstrap candidates only; TV1h is not an independent fast sensor. Each temperature within **Q±δ**, δ equal to its frozen R1 band (initial max(1°C,3×idle residual SD), subject to ruled S6 qualification). Slow 60 s OLS slope within ±0.2°C/min. | Full **180 s** jointly good interval; temperature/slope evaluated at 1 Hz. Minimum **300 s since last disruptive work ends**; whole attempt cap **1,800 s**. | No band/slope/freshness proof: no release. At cap, `not_ready`, retain trace and return to magistrate; never arm merely because ceiling expired. |
| Fans | Every qualified fan RPM key in Q±max(100 RPM,3×reference SD); if reference fan is stopped, require stopped, not “almost stopped”. Record fan key/decoder, not any arbitrary F* value. | Same 180 s interval and shared 300/1,800 s floor/cap. | Missing/unreadable fan cannot be dropped from the AND condition. Unsupported channel means proposal unqualified. |
| Idle package/rail power | Fixed powermetrics processor-combined rail definition and decoder, distinct from KM003C DC-in. Every trailing-30 s duration-weighted mean within Q_P±max(0.25 W,0.10×Q_P,3×reference SD); Q_P must be finite/positive. | All such means for the same 180 s interval in band; same floor/cap. Characterize observer cost separately. | Missing channel or ambiguous scope: no release. Do not import an energy/residual-derived “good idle” threshold. |
| Pressure/display/contention | OS level 0, fresh PM Nominal; display asleep and screensaver disengaged; existing native contention evaluator READY, including any registered aggregate condition; no agent/driver from prior window. | Existing guard's **180 s / 30 s** clean criterion, not a snapshot. Keep its 2,700 s cap and clock tests. Joint release needs both this guard and P1; P1 timeout may stop earlier. | Dirty/unknown handled by existing guard; sensor/display failures invalidate the joint evidence. Existing refusal semantics stay; no waiver on nominal temperature. |
| Battery/setup | Existing fresh AC/float, top-up and OBC predicates, frozen power mode, volume/setup and meter requirements. | Initial and final reads; battery is not certified by 180 samples of old ioreg UpdateTime. Completed top-up must still be within 30 min at actual arm. | Wait for float or obtain fresh top-up evidence within authorized procedure; then rerun affected physics checks. Expiry, charging or unplugging prevents GO. |

“Jointly good” means measured time, not sample count multiplied by one
second. Require ≥99% one-second-cell coverage, no gap >2 s, no stale sample
older than 2 s at a release evaluation, and bracketed monotonic stamps.
For package power, cover the complete averaging interval. A missing interval
cannot be credited as quiet; record the exact last-failure time and reason.
Use the existing contention evaluator's special unknown handling unchanged,
but do not claim that unmeasured time belongs to the full joint interval.

The two-sided Q bands are intentional: “colder than R” is sufficient for the
existing one-sided G0 intervention but is not by itself equivalent to the
same initial condition. This is a stricter new between-window definition;
**do not change G0/G1 to two-sided bands**. If an ambient change makes Q
unreachable, stop for a new setup/cohort decision rather than slide Q along
with successive windows. Record ambient proxy, elapsed time and predecessor
class even when they do not gate; the two sensors cannot prove all latent
thermal modes equivalent.

Execute slow/static triage, custody traffic and cadence probes before the
final stability interval. Start the 300 s floor at the last disruptive
operation, including top-up/load/hash/probe work or a display transition;
reset after new disruption. Cheap final battery/mode/census reads remain
inside the native GO path. Keep their cost in the characterization. If they
break the bands/quietness, re-establish the interval. Do not certify this
live state on the Air or reuse a previous arm's PASS. The baseline currently
accepts `quiet_start_state` through a packet entry; adoption needs a native
receipt/evaluator, bound to this attempt and checked again at GO, rather
than a new boolean asserted by that packet.

**Estimand protection:** elapsed cooling time does not enter model work or
the primary residual. Release uses pre-work state alone, before task/score
access, under one frozen rule for every window role. Keep process isolation,
sampler, warmup, order, member R capture, gates, ownership boundaries,
exclusions, F/C/T allocation and the fixed-eight calibration rule unchanged.
Record every failed/censored readiness attempt and the start clock/time of
day. This protects the proposed state equivalence; it does **not** prove
equivalence of unobserved state or residual distributions. Apply the chosen
policy to the whole new cohort and calibrate under it, rather than pool
old/new start protocols on a successful spot check.

### P2 — display/quiet dwell ends on its own measured criterion

For v4's HAZARD path, use the existing 180 s clean guard exactly as written,
with its 30 s intervals, final clock/battery/thermal/census reads and
2,700 s cap. No new 180 s sleep after READY. Do not import legacy 600 s or
precheck's 600 s cap into that path. This part is already implemented and
has no new physics saving.

Where a 300 s display floor is imposed, propose one shared interval:
display must be observed asleep throughout, at least **300 s since the
last sleep transition**, native guard READY, and P1 jointly satisfied.
Release at their maximum, not their sum. Hard cap 1,800 s for P1/display
readiness and the existing guard cap; a wake restarts the display floor,
and unknown display state refuses. Finite attempt deadline is never reset
by repeated wakes. Keep R0's production 300 s rule until a lead ruling
explicitly permits overlap; reducing it to 180 s is **not** proposed here.

Overlap only observation-only work between windows, after heavy preparation
is finished. If current components cannot share a continuous stamped trace,
keep sequential checks; proximity of two PASS files is not continuity.
Display sleep can itself cause a CPU burst (AUTH item 206), so the clean
suffix starts after that disturbance. A warm/cool sensor or an idle HID
timer cannot substitute for the guard's process measurements.

### P3 — member idle: a concrete future candidate, retained at 300 s in v4

A candidate for later qualification is: after process/telemetry preparation,
release baseline at the earliest time ≥**120 s** with a complete final-60 s
baseline, the P1 physical bands and 180 s quiet requirement if not already
continuously observed, and passing existing idle-admission evidence. Cap
at the existing attempt/member/session deadlines, at most the current
1,500 s effective admission cap; failure follows today's abort/flag path.
The actual minimum would therefore often be ≥180 s. **A 120 s target is not
a 120 s promise.** The PM sample count/coverage/admission contract would
need a new explicit definition; it cannot be truncated to whatever samples
happen to exist at the first temperature crossing.

This changes a measured baseline, member-5 R, predecessor trajectory,
available deadman time and the estimand's conditioning. R1's matched D-after-D
schedule and sizing would have to be rerun; shortened idle can just become
longer G0, while G0 then consumes more of T_dead. Preserve workload/RNG/cache
identity and score held-out data under fresh calibration. SYN D5's eight-pair
check is 2–4 h and would require outcome/energy evaluation in a separately
authorized lane. The ≤2 h physics run below cannot establish this scientific
equivalence. **Recommendation remains the lead's AUTH 214: keep 300 s for
v4, defer the paired shortening study to v5 development.**

### P4 — gates/holds and other fixed waits

Keep G0/G1/H and all role-specific caps. Use only the already ruled S6
joint G1/H tuning (median target ≤90 s each, δ_slow increments 0.5°C up to
2°C, U5 and duty qualification); filling an authorized R1 slot is not a
new exemption. Do not shorten stability counts, bypass slope/pressure,
move E, change N_chunk, or suppress holds to obtain a faster run.

Keep R1 soak/step observation windows, 60 s scaffold settles, 20 s closing
countdown, 2 s pre-idle settle, warmup/5 s settle, post-idle sentinel and
≥1 s sampling tail. No shorter stage-settle policy is proposed: a fresh
180 s joint stability observation cannot fit inside a 60 s settle, and
reusing earlier observations across a busy stage would not prove continuity.
Deleting 30 s of a settle is only a gross arithmetic opportunity below,
not a qualified replacement. R1 precools already early-exit and need no
replacement. Agent-resume and OS-batch holds stay as ruled; no ordinary-window
saving is credited.

## 3. What existing records can establish, without outcome access

The permitted unit is an explicitly named committed timing/thermal field,
not an archive search. Use `git show <commit>:<allowlisted path>`; never
follow a record locator, symlink or configuration's absolute data path.
Allowlist stamps, phase bounds, temperatures/aliases, RPM, pressure,
display transitions, idle power **in watts**, read coverage, gate outcomes
and durations. Exclude integrated joules, energy contrasts, residuals,
scores, alarms, transcripts and all Block-5 data. No free-form recursive
JSON export. Package power is used only to judge pre-work state, never to
select a favorable residual or outcome.

| Existing source | What is available now / honest limit |
|---|---|
| Pilot 8–10 committed native `arm_decision.json` stamps | Measured **whole arm elapsed** is 276.580233, 306.510938 and 276.620115 s, respectively. Derived only as `(ended.monotonic_ns−started.monotonic_ns)/1e9`; wall time is not used. Native arm overhead is already around 4.6–5.1 min, so another notional ten-minute dwell cannot be “saved” from it. These records point to arm details that are not co-located here: no attribution of the 96–127 s beyond a nominal 180 s to particular probes is justified. |
| P8–P10 thermal/charging/context fields | Heat/charging/contention are real; display-off alone and an initial float snapshot do not prevent them later. They are not an idle-duration experiment. Pilots differ in seeds, conditions and implementation history; no residual values were used for this proposal. |
| TAIL / R0 adaptive-idle comments | Establish plausible **slow** settling and a useful horizon for a new observation. The 840–1,040 s slope timing is not time to the **joint** temperature/fan/power/display band. Do not fit an exponential from these few summarized numbers. |
| R08–R10 NOTES / R11 NOTE | Establish distinct contention bursts and the new picks. R11's SMC check wall time 1,896.3 s (NOTE line 12) includes capture/startup: subtracting 900+600 and calling the remainder “cooldown” is invalid. R11's detailed SMC journal is only digest-pinned off-repo, so a new TV0h/Tf08 time-to-band curve cannot be computed within this task. |
| R1 contract fields, when a permitted committed export exists | `idle-until-soak.recovery_curve`, `released`, R/δ/cap; `g0_wait_s`, `g0_outcome`, `g0_timeout_s`; `gate_waits_s`; `deadman.phases_s`; inventory phase bounds, sensor series and fan keys. These suffice for a disjoint duration ledger and some temperature-only replay. The contract defines fields; this checkout supplies no native R1 result, and their existence is not a measured finding. |

Pilot stamp source pins (all paths begin
`docs/process_traces/night-results/align-pilot-<id>/arm_decision.json`):

| Pilot | id | Record commit | Fields / lines |
|---|---|---|---|
| 8 | `20261105T015948125148Z` | `1832b78fbd38` | ended `:24`; started `:36` |
| 9 | `20261105T102850144782Z` | `1e5942d1db56` | ended `:24`; started `:36` |
| 10 | `20261105T231016638759Z` | `bc50b8106221` | ended `:24`; started `:36` |

For a future allowed thermal export, define t=0 at **actual load end**, not
nominal step duration. Compute first qualifying trailing band at floors
300 s and stability intervals 60/120/**180 s** as descriptive sensitivity
only; the bold choice is the proposal. Compute slope on actual sample
times. Report the first joint pass, later re-exits, time spent outside each
band, last failure and coverage. A trace ending before readiness is
**right-censored**, never a success at its last sample or at the ceiling.
If fans/power were not captured, report temperature-only timing as such.
Do not reconstruct them from temperature or DC energy.

Stratify by preceding load/mode/ambient and display transition. Keep failed
attempts and their elapsed time in the cadence bill. Do not combine
pre-arm, member idle, G0 and hold durations twice: sum disjoint intervals
on one monotonic clock. Release in a replay is a counterfactual timestamp,
not evidence about the workload that would have followed it.

## 4. One native characterization, maximum two hours

**Owner: measurement-Mac magistrate, in a declared gap, with no analysis or
measurement job competing and every agent stood down.** This document does
not launch or schedule it. In particular it is not run beside the current
eight-worker analysis. Existing sealed data are not inputs. No model weights
or downloads: use a deterministic tiny synthetic MLX GPU kernel with bounded
allocation (≤256 MiB), or an equivalently reviewed native synthetic step.
Synthetic heat is an apparatus probe, never D-model or residual validation.

Freeze the test plan and proposed Q-band formulas before collecting. Use
the series power mode, charger, support/cooler state and display configuration
already chosen for v4. A hardware/SMC decoder failure aborts; no CPU fallback
is presented as native MLX evidence. Log 1 Hz fast/slow, qualified fan RPM,
OS/PM status, defined idle package power, clock stamps, read errors, display
events, observer CPU and existing guard intervals. Store only this new
diagnostic record. The collector must be bounded; its own tree is excluded
only in the existing manner and its CPU cost is disclosed, not excused.

| Wall budget | Action and question |
|---|---|
| 0–5 min | Native preflight, stable source/units, no other jobs, fixed setup and trace writer. No inventory/hash/model work inside the final quiet suffix. |
| 5–25 min | 1,200 s idle reference. Require the soak slope/noise/coverage bar; unstable or missing reference ends the experiment inconclusive rather than extending beyond two hours. Compare to R1-linked Q if already available; this capture may supply Q only under a prospective reference-capture ruling, never silently replace an existing Q. |
| 25–40 min | Fixed 900 s synthetic GPU pulse, matching R0's observation scale. One predeclared workload size/duty, no search for a favorable heat response. |
| 40–70 min | Recovery observed for **1,800 s**, even if the shadow P1/P2 release occurs early. Record first band/stability pass, whether it exits again, fan lag and comparison at 900/1,500/1,800 s. Shadow release does not stop logging. |
| 70–85 min | Same 900 s pulse. For the display-transition case, a local bounded runner may create one predeclared wake/sleep during the synthetic-load phase, ending with display sleep at recovery entry; label this different display history. No person or agent remains active. |
| 85–115 min | Second 1,800 s recovery. Replay fixed display floor versus joint release, existing guard and final physical-read cost. If display state is unavailable, no display-overlap qualification. |
| 115–120 min | Stop collectors, cleanup/census and small diagnostic manifest. No production model, campaign arm or real-data desk. Hard stop at 120 min including cleanup. |

P1/P2 pass the **engineering characterization** only if both traces have
valid reference/channels, candidate releases satisfy every bound and remain
in the frozen bands through the remaining observed recovery, final reads
do not disturb readiness, and observer CPU fits the existing 0.5%-of-one-core
monitor budget. Report each release and net measured saving, not just a
mean. A release close to the horizon provides little post-release evidence;
mark it inconclusive. A thermal reset does not predict future scheduled
background activity; keep in-window monitoring.

This settles whether the proposed signal, timing and shared-dwell mechanism
works on these native synthetic recoveries, and can refute overly permissive
bands. Two recoveries cannot establish a tail quantile, universal 30 min
recovery, D-load equivalence, or residual noninferiority. If existing allowed
D/R1 thermal fields cannot bridge that load-transfer gap before registration,
**retain the incumbent wait policy for W1 and its cohort**; the engineering
result alone is not a scientific go. P3 (member idle) and P4's optional stage
shortening remain deferred. Do not squeeze SYN D5's 2–4 h eight-pair study
into this ≤2 h budget or claim it has been completed.

Before implementation, synthetic tests should cover early/cap-equality,
bad/gapped/stale samples, aliases, band re-exit, counter reset, fan/power
absence, clock discontinuity, display wake, expired top-up, final-read
disturbance and cancellation/cleanup. Lead native checks must then cover
real SMC/PM units and freshness, native display observation, fan lag,
observer overhead, and MLX hold drain/resume and token/cache identity if
that path is touched. No native/MLX check is claimed from this sandbox.

## 5. Saving ranges and registration disposition

Use **net** first-capture timing; manual cooling may already overlap display
dwell, charge recovery and t0 lead. These are conditional planning ranges,
not independent quantities to add:

| Proposal | Per-window saving / cost | What may be credited now |
|---|---|---|
| P1 joint start-state release | If already physically ready by the 300 s floor: versus 900–1,500 s discretionary cooldown, **10–20 min**. If the TAIL slope first qualifies at 840–1,040 s and needs another 180 s stability, release cannot precede **1,020–1,220 s**: versus that same allowance, **−5.3 to +8.0 min**. Other predicates may take longer or fail at 1,800 s. | **0 measured**. The hot calculation is a lower-bound scenario for release, not a distribution of new-pick cooldowns. It shows why “expected 10–20 min” is unwarranted. |
| P2 overlap display floor and quiet dwell | Serial 300+180 s becomes max(300,180)=300 s when both are otherwise ready: **0–3 min**. If thermal recovery already contains both, **0**. Existing guard early exit alone saves **0 new seconds**. | **0 measured**; registration/continuity qualification needed. Do not add 3 min to P1 if the old cooldown already included this dwell. |
| Fresh battery wait / repeat polling | Correct float predicate can avoid an unnecessary *additional* fixed retry delay, but actual top-up and float time are unknown; no battery-time saving range established. | **0**. A charge/top-up outside this document's readiness cap can dominate turnaround. |
| P3 idle 300→120 s, hypothetical later design | Gross **54 min** for 18 D members in a D window; **42 min** for 14 thermal members in W1; four anchors kept at 300. Changing all 22 would gross 66 min but is not this proposal. Net can be **zero or negative** if G0 expands/timeouts increase; observed idle inflation is not a guaranteed reclaimable 90 s/member. | **0 for v4**. New admission definition, matched R1 schedule and F/C/T qualification required. |
| P4 G0/G1/H early release / S6 tuning | Already condition-based. Tuning could save sum(old waits−new waits), unmeasured; unused ceiling has **zero** recurring cost. | **0 quantified**; keep qualified gates. |
| Hypothetical stage settle 60→30 s | At most **30 s per actually executed settle**, before any added guard/hold cost; no condition-based replacement is qualified here. | **0; defer**. Do not multiply a historical “11” by 30 for the current plan without rendering/counting its stages. |

Until native evidence exists, capacity planning should retain the current
30–45 min turnaround estimate from REV. Report potential improvement as
**0–8 min on the hot-tail illustration, with possible slowdown**, and
**10–20 min only for an already-cool case**. These are scenarios; a numerical
expectation cannot be estimated from the available summaries. Shared dwell
has a separate 0–3 min ceiling only where it was actually serial. Repeat
readiness failures, extra probes or top-up can erase the gain.

| Item | Pure engineering versus registered design | Required disposition before W1 |
|---|---|---|
| Timing-only exports, disjoint duration ledger, showing actual READY, removal of a proven redundant post-READY sleep with unchanged evidence | Engineering, if admitted instants, observation duration, failures and bytes that govern admission remain equivalent. No new skip or stale receipt. | Ordinary implementation review, focused synthetic checks; native gap timing. Preserve all R12 triage entries. |
| P1 new Q/bands/floor/stability/ceiling/missing-data rules and host receipt | **Registered start-state/admission design**; adding fans/power or two-sided temperature checks also changes the admitted population. | Independent builds/agreement and lead/cold registration ruling; native qualification, exact source/digests and failure policy. Bind one policy/cohort before W1. No pending numeric channel/reference may authorize an arm. |
| P2 overlap across previously sequential display/guard/cooldown or reuse of observations | **Registered temporal/admission design** unless exact unchanged-predicate timing equivalence is demonstrated. Shortening R0's 300 s violates AUTH 209 without a ruling. | Choose explicitly in W1 arm route; new continuity receipt and native characterization. Existing READY behavior by itself needs no amendment. |
| P3 shortened/adaptive baseline; stage settles/countdowns/tails; changed gate samples/bands/caps or N_chunk | **Registered measurement/design change**. Existing authorized S6/R1 slot filling is distinct from a new policy. | Keep current values for v4. Any reopening needs prospective ruling, matched R1 and fresh calibration/testing; never retrofit earlier records. |
| Top-up/charge hold, OBC, ambient/cooler/power mode, OS batch and agent-resume policy | **Physical setup / design / owner authority**, not an elapsed-time optimization. | Preserve existing rules; missing charge-hold evidence and blackout ruling are not discharged by P1. |

The W1 registration must name the chosen wait policy, Q source and sensor
classification digests, exact channel/band definitions, floor/stability/caps,
clock/coverage rules, every failure outcome, point of final evaluation,
observer implementation, all permitted overlap, and the unchanged member-R/E
rules. Record start time/ambient/predecessor diagnostics so cadence and
time-of-day shifts remain visible. Freeze once; no window-by-window threshold
adaptation based on success or outcomes.

**Next exact step:** compare this Sol build with the independent Opus build
under item 220; lead rules whether P1/P2 qualification is worth one ≤2 h
native gap before registration. If approved, the magistrate executes that
diagnostic after all competing work clears and returns a timing/thermal-only
receipt. If adequate load-transfer evidence or a bound channel/reference is
missing, register the current waits and defer replacements. Nothing in this
document authorizes changing or arming a live window.
