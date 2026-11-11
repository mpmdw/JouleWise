# R1 step_30b G0 timeout: Fable 5.2 research-design ruling

Seat: Fable 5.2 research design, 2026-11-10, blind to the parallel Sol seat
(`11-sol-findings.md` appeared in this directory while I worked; I did not open it).
Answers `01-brief-common.md`. Read only thermal, status and structural records.
No calibration value, workload result or power trace was read. No code, custody
or `M` file was changed, and no measurement was started.

Terms used below, each fixed here:

- **G0**: the start gate a member (one model run) must pass after its warmup and
  before its first turn (`thermal_gates.ThermalSession.wait('G0')`).
- **Tf08 / TV0h**: the two SMC temperature sensors the gate reads once a second.
  Tf08 is the "slow" key and TV0h the "fast" key chosen by R0.
- **Reference R**: the temperature pair the gate compares against.
- **Band δ**: how far above R a sample may be and still count as good
  (`delta_slow_c` for Tf08, `delta_fast_c` for TV0h).
- **Slope bar**: the gate also needs the Tf08 trend over the preceding 60 s to be
  within ±0.2 °C/min.
- **Release**: ten consecutive good samples. **Cap**: the longest the gate waits
  (`g0_cap_s`); reaching it is a timeout.
- **Soak**: R1's 30-minute idle segment before any model runs. Only the sensor
  reader runs in it: no model process, no power capture.
- **Own idle**: Tf08 during a member's own idle stage, before its warmup, with
  its model loaded and power capture running.
- **Excess**: Tf08 minus that member's own idle.

R1 names used below, as the runtime contract defines them:

- **step-30b, step-d**: one long turn each on the 30B model and on model D, used
  to read how the sensors respond to a load.
- **A-B-A legs**: three such turns in Automatic, High Power, Automatic power
  mode, to decide whether High Power is adopted.
- **Designed start states**: three D turns started on purpose at R, R + 2 and
  R + 4 °C, to measure how energy depends on start temperature (β_T).
- **Gated D runs and X-G**: four members run back to back as W1 will run them.
  The **duty bar** checks that their gate waits take at most 40 % of the
  member's time limit.
- **Precool** (`idle-until-soak`) and **`g0-release-soak`**: sensors-only waits
  for Tf08 to come within the band of R before a segment.
- **Slots S5 and S6**: the slow band from the registered formula, and the slow
  band the gates actually use. They differ only by a recorded tuning step.

## 1. Ruling

Adopt three changes together. Each is needed. On the 11-10 record every
combination of one or two of them is still unreleased at 600 s. The
combinations that keep the 600 s cap therefore time out on the record itself.
Those that take the 1,200 s cap fail to release within it in at least two of
the four tail models of section 3 (section 4.1).

| # | Change | Value | Now |
|---|---|---|---|
| 1 | Reference for every R1 gate after the first model member | **R_op**: the median of each gate key over the 60 s before warmup entry of the accepted `step-30b` member (the protocol's existing WP14(b) capture rule, `capture_reference`, coverage ≥ 0.9). On the 11-10 record: Tf08 26.571 °C, TV0h 34.106 °C | Mean of the last 1,200 s of the sensors-only soak: 25.489 / 34.011 °C |
| 2 | Slow band used by R1's gates | **δ_slow = max(1.5 °C, 3 × soak SD)** = 1.5 °C. Recorded as slot S6 = 1.5 with a tuning receipt from S5 = 1.0. S5's formula and the fast band (1.0 °C) do not change | max(1.0 °C, 3 × soak SD) = 1.0 °C |
| 3 | G0 cap for R1 model members | **1,200 s for every model member** (`g0_timeout_s`, the existing constant), which adds `step-30b`, the three A-B-A legs and `d-4bit`. For the legs and `d-4bit` the member deadman (the wall-time limit on the member, 1,580 s) is armed **after** the G0, as `step-30b` and step-d already do | 600 s for those five; 1,200 s already for step-d, X-G, the gated D runs and the designed start states. The legs and `d-4bit` arm their deadman at G0 entry |

Unchanged: the sensor keys, the slope bar, the ten-sample rule, the OS and
powermetrics status conditions, the warmup, the 300 s quiet after release, the
600 s cap of the sensors-only `g0-release-soak`, the 1,500 s precool caps, the
gated D runs' and X-G's deadman at G0 entry (that share is what the duty bar
measures), and every W1 rule. The soak stays: it still supplies the settling
check (|slope| ≤ 0.2 °C/min), the SD for the bands, and the "R minus soak"
print.

What the next R1 record should show if this ruling is right (a check, not a gate):
R_op − soak mean on Tf08 near +1.06 °C; `step-30b` G0 released between about
700 and 910 s; Tf08 at release about 1.5 °C above the member's own idle. No
release by 1,200 s means the tail model in section 3 is wrong and the record
should come back to this seat. A much earlier release is harmless and should
simply be noted.

## 2. What the 11-10 record shows

The diagnosis found one cause. The record holds two, and the second is the
larger.

**Cause A: the reference is taken at a different operating point (+1.06 °C).**

| State | Tf08 | Source |
|---|---|---|
| Soak, sensors only, last 1,200 s | mean 25.489, detrended SD 0.078, slope +0.004 °C/min | `soak_reference.json` |
| `step-30b` own idle, 60 s ending where pre-warmup activity begins | median 26.549, SD 0.079, slope over the last 180 s +0.019 °C/min | step `align_thermal.jsonl` |
| Same, by the WP14(b) rule (60 s ending at warmup entry) | median 26.571 | same |

The member's idle is flat and sits 1.06 °C above the soak (1.08 by the capture
rule). The old limit was 25.489 + 1.0 = 26.489 °C, which is 0.06 °C *below* the
member's own settled idle. No amount of waiting reaches it. Loading the model
is not the cause: that transient was +1.39 °C in the first 30 s of the idle
stage and under 0.1 °C after 150 s.

**Cause B: ten minutes after a 29 s warmup the machine is still 1.9 °C above its own idle.**

| Time after warmup end | Tf08 excess over own idle | TV0h excess | Tf08 60 s slope at end |
|---|---|---|---|
| peak | +32.4 | +20.2 | |
| 60–90 s | +11.15 | +1.02 | −7.6 °C/min |
| 270–300 s | +3.74 | +0.34 | −0.77 |
| 450–480 s | +2.47 | +0.23 | −0.29 |
| 570–600 s (cap) | +1.92 | +0.18 | −0.03 |

The slope bar was first met for ten consecutive samples 592 s into the gate, at
an excess of +1.86 °C. So even against the member's own idle with the
registered 1.0 °C band, the gate was 0.86 °C from releasing at the cap.

This is heat in the machine, not a quirk of Tf08. The step's full-inventory
journal has 224 temperature keys that rose at least 3 °C in the warmup. At
570–600 s their excess over their own pre-warmup idle has median +1.85 °C
(quartiles 1.74 and 1.97); 17 of the 224 are within +1.0 °C.

An older record agrees on the slow tail. R0 re-run `r0-v4-20261108T0550Z`
(settled idle 26.369 °C, fans at 0 rpm in idle) shows Tf08 +8.5 °C at 300 s and
+5.8 °C at 570–600 s after its 900 s load, still falling at −0.36 °C/min.

## 3. Parameter values and their derivations

**3.1 R_op (change 1).** A gate asks "has the heat from recent work gone?".
That is a difference from the temperature the machine holds when it is doing
nothing *in the same configuration*. A member idles with its model resident and
power capture writing; the soak has neither, and Tf08 reads 1.06 °C lower there.
The reference therefore has to be taken with the member's configuration live.
The first model member follows the 30-minute soak directly, so its pre-warmup
idle is the one point of the night that is both settled and at the right
operating point.

- Statistic and window: median over the 60 s before warmup entry, coverage
  ≥ 0.9. This is the registered W1 rule (protocol v4, WP14(b)), so R1 rehearses
  the rule W1 will use and no new statistic is introduced.
- Uncertainty of R_op: SD 0.079 °C at 1 Hz gives 1.2533 × 0.079 / √60 = 0.013 °C
  for the median if samples were independent. The four consecutive 60 s medians
  of the clean idle span 0.128 °C (26.492–26.620), which is the honest figure.
  The capture window also includes about 10 s of pre-warmup activity; the median
  moved by +0.022 °C (26.571 against 26.549). All three are small against a
  1.5 °C band.
- No fixed offset is written anywhere. Settled idle on Tf08 at one operating
  point differed between sessions by 0.6 °C (R0 re-runs on 11-07: 26.37, 26.39,
  26.97 °C), so the reference must be measured in the same night.
- R_op − soak mean is printed per key and not gated. There is one measurement of
  it (+1.06 °C), so there is no spread to size a tolerance from.

**3.2 δ_slow = 1.5 °C (change 2).** The registered text already names the
remedy for a timeout-driven failure: loosen δ_slow in 0.5 °C steps, never above
2.0 °C (protocol v4, chair ruling 14 and ruling 1(e); slot S6 with a tuning
receipt). That text was written for the D-series windows; it is applied here to
the R1 re-run, before the next attempt and not in place. The choice is which
step. Rule used: *the smallest step for which
1.25 × the predicted release time is within 1,200 s under every tail model that
fits the record.* The 1.25 factor and the 1,200 s are the registered headroom
and maximum (LEAD-RULINGS-2 R7-2: cap = 1.25 × longest wait, at most 1,200 s).

The record ends at 600 s, so release times beyond that are extrapolated. Four
two-exponential models were fitted to the tail from 60 s to 600 s after warmup
end. They differ in what the record cannot settle: where the tail levels off
and how slow its slow part is. Noise SD is 0.078 °C, so a fit with rmse near
that is as good as the data allow.

| Model | Fast / slow time constant | Level it tends to (vs own idle) | rmse °C | Slope bar met from |
|---|---|---|---|---|
| A: level free | 60 / 300 s | +0.93 | 0.076 | 587 s |
| B: level = own idle | 70 / 500 s | 0 | 0.076 | 656 s |
| C: level = own idle, slow part 956 s (the R0 0550Z tail) | 100 / 956 s | 0 | 0.137 | 503 s |
| D: level free, slow part 956 s | 70 / 956 s | −2.59 (not physical; kept as the adverse slope case) | 0.082 | 901 s |

Predicted release (band and slope bar both met, plus ten samples), seconds
after warmup end, against R_op:

| δ_slow | A | B | C | D | Range | 1.25 × longest | Within 1,200 s |
|---|---|---|---|---|---|---|---|
| 1.0 | 1,299 | 907 | 1,241 | 911 | 907–1,299 | 1,624 | **no** (A and C exceed 1,200 even without headroom) |
| **1.5** | 751 | 708 | 862 | 911 | 708–911 | 1,139 | **yes** |
| 2.0 | 597 | 666 | 608 | 911 | 597–911; observed 592 on the record | 1,139 | yes |

1.5 °C is the smallest step that passes. It is preferred over 2.0 °C for two
further reasons. At 2.0 °C the band stops doing anything on a warmup-only tail:
the band is met at 576 s and the slope bar is the last condition to be met
(observed release 592 s at +1.89 °C). And a night run
at 1.5 °C records each tail down to 1.5 °C, from which the 2.0 °C gate can be
replayed exactly; the reverse is not possible.

Sizing δ_slow from idle spread does not apply here. Three SD is 0.23 °C (soak
0.078, own idle 0.079, settled R0 idles 0.075–0.088 °C). Spread is already in
the registered formula and is not what failed.

**3.3 Cap 1,200 s for all model members (change 3).** Every model member has
the same warmup before its G0, so every one has the same tail. On the record
the slope bar alone took 592 s, which leaves a 600 s cap with 8 s of margin
before any band is considered. The need under 1.5 °C is 1.25 × 911 = 1,139 s;
1,200 s is the existing constant and the validator's maximum
(`G0_CAP_MAX_S`). `g0-release-soak` keeps 600 s: no warmup precedes it, and the
one sensors-only cooling record on disk (the head of the soak, starting at
28.4 °C) releases by replay at 151 s.

The A-B-A legs need the cap for the same reason. At 600 s each leg's own G0
would time out, the adoption decision would be inconclusive by construction,
and Ed's ruling that R1 includes the A-B-A would measure nothing. The legs'
deadman must move with the cap. Today it is armed at G0 entry (1,580 s), so a
G0 of 708–911 s would leave the turn only 669–872 s, and a deadman that fires
mid-decode is an incomplete member, which refuses the whole night
(`k_step`: an incomplete leg is inconclusive only when its G0 did not release).
Arming the deadman after the G0 uses the existing `rearm` path and keeps a long
wait from turning a clean inconclusive into a refusal. I did not read how long
the turn takes (a workload result), so I do not claim the turn would not have
fitted; the change removes the dependence.

## 4. Replay

Method. The production rule was re-implemented from
`thermal_gates.ThermalSession.wait`: a sample is good when TV0h ≤ R_fast + 1.0,
Tf08 ≤ R_slow + δ_slow, the ordinary-least-squares slope of Tf08 over the
preceding 60 s (at least 54 samples) is within ±0.2 °C/min and, where the
journal carries status, OS level is 0 and powermetrics reports Nominal. Ten
consecutive good samples release; otherwise timeout at the cap. The replay
reproduces the recorded outcome (first row). "Excess" is Tf08 minus the
member's own idle (26.549 °C for the R1 step).

**4.1 R1 `step-30b`, 2026-11-10 (the only record where G0 ran).** Recorded data
end 600 s into the gate.

| Candidate (reference, δ_slow, cap) | On the 600 s of record | Time to release | Excess at release |
|---|---|---|---|
| Soak mean, 1.0, 600 (as run) | timeout | none | +1.86 at 600 s |
| Soak mean, 1.0, 1,200 (longer cap only) | not released | never in models A–C (limit is below own idle); D 1,131 s | |
| Soak mean, 1.5, 1,200 | not released | A never; B 1,328; C 2,046; D 959 s | |
| Soak mean, 2.0, 1,200 (registered maximum band) | not released | A 1,886; B 949; C 1,321; D 911 s | +0.6 to +0.9 |
| Soak mean, 3.0, 600 | timeout | none | +1.86 at 600 s |
| R_op, 1.0, 600 (reference only) | timeout | none | +1.86 at 600 s |
| R_op, 1.0, 1,200 | not released | predicted 907–1,299 s | +1.0 |
| R_op, 1.5, 600 | timeout | none | +1.86 at 600 s |
| **R_op, 1.5, 1,200 (adopted)** | not released by 600 s | **predicted 708–911 s** | **+1.5** (D: +0.56) |
| R_op, 2.0, 600 | released | 592 s (8 s inside the cap) | +1.89 |
| R_op, 2.0, 1,200 | released | 592 s | +1.89 |

Under the adopted rule the member then idles 300 s before its prefill. The
predicted excess at prefill is +0.8 to +1.1 °C (models A–C), and TV0h is within
0.2 °C of its own idle.

**4.2 Records where G0 did not run but could have** (reference = that record's
own idle, last 60 s before load; no status source, so temperature and slope
only).

| Record | Own idle before load | Recovery on disk | Adopted rule (own idle, 1.5, 1,200) | 1.0 / 2.0 | Excess at the end of data |
|---|---|---|---|---|---|
| `r0-v4-20261108T0550Z` (900 s load) | 26.369, settled (slope +0.08 °C/min) | 600 s | not released by 600 s; predicted +1.5 at 1,600–1,900 s, so **timeout at 1,200 s** | predicted +1.0 at 1,900–2,300 s; +2.0 at 1,400–1,600 s; slope bar at about 1,170–1,230 s | +5.8 |
| `r0-v4-20261107T0810Z` (900 s load) | 34.75, **not settled** (slope −0.59 °C/min, fans running in idle) | 600 s | band met at 257 s with slope −0.89 °C/min; slope bar never met; no release | same | −1.91, still falling at −0.34 °C/min |
| `r0-v4-20261107T0720Z` | 34.41, not settled (−0.73 °C/min) | 288 s | band met at 257 s with slope −0.81; no release in 288 s | 1.0 not met | +0.9 at 270–280 s |
| `r0-v4-20261107T0631Z` | 34.62, not settled (−0.76 °C/min) | 78 s | no release (data end) | same | +8.0 |
| R1 soak head, 11-10 (sensors only, vs soak mean, 1.0) | | 1,800 s | released at 151 s | | +0.16 |
| `r0-v4-20261108T0115Z`, `…T0224Z` | 26.97 / 26.39, settled | none | cannot be replayed | | |
| `r0-v4-20261108T0140Z` | 30 s of idle at 33.9 | none | cannot be replayed | | |

The 0550Z row is the hot-start test: a machine 5.8 °C above its idle at 600 s
is refused by the adopted rule through its whole 1,200 s cap. The 0810Z row
shows what a per-member self-captured reference does when the idle before it
was still cooling: the band is met while the machine is falling at
−0.9 °C/min, and the machine ends 1.9 °C *below* that reference. Only the
slope bar stood between that start and a release.

**4.3 Roots with no thermal record to replay.** Pilots v7, v8 and v9 carry only
the OS thermal level at a 5 s cadence (4,629 / 4,619 / 4,645 readings; level 1
in 4 / 0 / 5 of them) and no SMC temperature, so the temperature conditions
cannot be replayed there. `r0-v4-20261106T1605Z`, `…T1705Z`, `…T2235Z`,
`…07T0132Z` and `…07T0149Z` have no SMC samples. `r1-20261108T085636Z` and
`r1-20261110T212531Z` never reached a model step.

## 5. Effect size in physical terms

**Cooling tail after release.** Under the adopted rule a warmup-only member is
released about 1.5 °C above its own idle with Tf08 falling at 0.1–0.2 °C/min.
Step members then idle 300 s and start prefill about 0.8–1.1 °C above idle.
Most of that is heat the member's own warmup put there: model A levels off at
+0.93 °C, and at 1,200 s models A–C still predict +0.6 to +1.1 °C. Every member
has the same warmup, so this part is shared by all members gated the same way.

**What residual heat costs in energy.** The cost is β_T × excess, where β_T is
the change in a member's energy per °C of start temperature. β_T has not been
measured; R1's three designed start states exist to measure it. Until then the
only estimate is from leakage physics, with assumed inputs that were not
measured on this machine: leakage is 5–20 % of active power, and leakage power
doubles every 10–30 °C (2.3–6.9 % per °C). The product is 0.12–1.4 % of member
energy per °C, or about 1–14 J per °C for each kJ a member uses.

- Against the roughly 1 J attribution limit: a 1.5 °C excess that one member had
  and its comparison did not would cost about 2–21 J per kJ. That is above the
  limit for any member larger than about 50–570 J. Start temperature is therefore
  not negligible, and the band cannot be called free.
- What this ruling adds over the registered 1.0 °C: 0.5 °C, or about 0.6–7 J per
  kJ, common to every member released by the same gate.
- What the reference change adds: nothing. It moves the zero to where the
  member's idle is. Under the old reference the allowance above the member's own
  idle was 1.0 − 1.06 = −0.06 °C.
- The registered check on this is U5: |β_T| (90 % bound) × δ_slow ≤ σ_pair
  (at least 2.97 J). It is now evaluated at 1.5 °C, so it is 1.5 times harder to
  pass than at 1.0 °C. That is the right direction: a looser band has to earn
  its place on R1's own β_T.

## 6. Why the other candidates are worse

- **Longer cap alone (soak reference, 1.0 °C, 1,200 s).** The limit, 26.489 °C,
  is below the member's own settled idle, 26.549 °C. Waiting longer cannot
  release.
- **Wider band on the soak reference.** At the registered maximum of 2.0 °C the
  limit is own idle + 0.94 °C and the predicted release is 911–1,886 s. Going
  wider would exceed the registered 2.0 °C maximum and would hide a 1.06 °C
  operating-point error inside a tolerance, where it would silently change if
  the capture load or the model changed.
- **Band from measured idle spread.** Three SD is 0.23 °C. Spread did not fail;
  the registered max(1.0 °C, 3 SD) already contains it.
- **Reference from each member's own pre-load idle.** Correct for the first
  member after the soak, which is what change 1 uses. Wrong as a general rule: a
  member that starts 300 s after a heavy load captures a reference that is still
  cooling (R0 0810Z: −0.59 °C/min, and at least 1.9 °C above where the machine
  ended). The band is then always met and the slope bar becomes the only gate.
  With the slow tail measured on R0 0550Z (time constant 743–956 s), a slope of
  0.2 °C/min corresponds to 2.5–3.2 °C above idle. That is the hot start this
  candidate lets through, against at most 1.5 °C for a fixed R_op.
  LEAD-RULINGS-2 R5-1 rejected per-member self-capture for the gated runs for
  the same reason.
- **A second 30-minute soak with the model and capture live.** Physically the
  same reference as change 1. It needs a new segment kind and 30 more minutes,
  and gives no better mean: the first member's idle already holds flat for
  180 s at that operating point.
- **Changing s_slow.** The registered selection rule forbids manual
  substitution (protocol v4, WP14(a)). It would not help either: the median of
  224 responding sensors shows the same +1.85 °C at the cap.
- **Reference change alone, or reference plus cap, at 1.0 °C.** Times out on
  the record at 600 s, and at 1,200 s releases in two of four models only
  (907–1,299 s).

## 7. Decisions I made

1. The three changes in section 1, with the values and derivations in section 3.
2. R_op comes from the **accepted** `step-30b` attempt. A `g0-release-soak`
   that runs before any `step-30b` is accepted (a redo) uses the soak mean,
   because nothing else exists yet. A capture that comes back `unobserved`
   (coverage below 0.9) leaves the existing behaviour: the member is incomplete
   and the night refuses.
3. One reference for everything after `step-30b`, including the sensors-only
   precools and `g0-release-soak`. In a sensors-only session Tf08 idles about
   1.06 °C lower, so those waits end about 1 °C earlier than a matched reference
   would end them. That is accepted: no measurement starts from a precool
   without passing its own member's G0 against R_op.
4. No new guard on the capture window. The 60 s before warmup entry contains
   about 10 s of pre-warmup activity, so a slope test on it would fail
   spuriously (+2.86 °C/min on the 11-10 record) while the median is unaffected
   (+0.022 °C). The soak's own settling check and the member's idle of at least
   300 s stand in for it.
5. `step-30b` does **not** join the R6-2 retry-then-inconclusive path. With the
   predicted release at 708–911 s against a 1,200 s cap, a timeout there would
   mean the model in section 3 is wrong, and stopping after one hour is the
   right response to that.
6. S5 keeps its registered formula and value (1.0 °C). The loosening is carried
   as S6 = 1.5 °C with a tuning receipt citing this ruling. Through the existing
   kit binding, W1's `delta_slow_c` then defaults to 1.5 °C. This ruling does not
   fix W1's value: the registered S6 step after R1 decides it from R1's measured
   β_T, U5 and gate waits.
7. U5 in R1 is evaluated with δ_slow = 1.5 °C, the band the gates actually used.
8. The slope bar, the ten-sample rule, the fast band and the sensor keys are
   left alone. Nothing on the record argues against them.
9. This is a code change in the R1 runtime, driver, contract and kit text, so
   the frozen root `M` at `20e9edbc4` cannot be re-armed as is. The re-arm goes
   through the ordinary build, review and pin path, not the zero-capture retry.
   Every bound that contains a model-member G0 cap is recomputed. `step-30b`
   takes step-d's bound: 3,663.9952 + 1,200 + 300 + 600 = 5,763.9952 s. Each
   A-B-A leg's G0 now sits outside its deadman, so its bound gains the 1,200 s
   cap: 4,328.9952 → 5,528.9952 s, to be confirmed by the builders against
   `segment_bounds` and `aba_leg_bound_s`. The plan's `window_max_s` follows
   from the recomputed night table.
10. The A-B-A legs and `d-4bit` arm their deadman after the G0 (section 3.3).
    A leg whose G0 still does not release stays inconclusive under R5-3, as now.

## 8. NEEDS_RULING

**NR-1. Which reference the gated D runs and X-G use.** This changes which
gated runs are judged and the W1 G0 cap and decode budget derived from them.

- The governing text says two things that the physics now sets against each
  other. R6-1's purpose: "the duty bar must reproduce W1's D-after-D G0". R5-1 /
  R6-1's mechanism: gate those runs against the R1 soak reference (after this
  ruling, R_op, which is equally cold).
- W1's own reference is the first sidecar member's pre-warmup idle, taken 300 s
  after earlier members. On the records here a machine is +3.7 °C (after a 29 s
  warmup) to +8.5 °C (after a 900 s load) above idle at 300 s. W1's reference
  will sit several °C above R_op.
- Against a cold reference plus 1.5 °C, the R0 0550Z tail predicts release
  1,600–1,900 s after a heavy load ends, which is beyond the 1,200 s cap and the
  member deadman. Against a warm W1-style reference the slope bar would bind
  instead, at about 1,170–1,230 s after the load ends. These come from one R0
  record with a synthetic load, so they are indications, not sizes.
- If the mechanism stands, expect R1's duty bar to come back inconclusive or
  failed and `g0_cap_w1` censored at 1,200 s, for a reason W1 would not share.
- My recommendation: use W1's own rule in the gated block. The first gated run
  captures at its pre-warmup idle and the later gated runs and X-G consume that
  reference; the capturing run is recorded but not judged, which answers R5-1's
  objection that a self-capturing run cannot fail. The adopted changes do not
  depend on this, and an R1 night can run before it is settled: unreleased gated
  runs are recorded as inconclusive, not as a night refusal, and their 1 Hz
  tails allow either reference to be replayed afterwards.

Nothing else needs a ruling.

## 9. Two consequences to expect, not changed here

- **Designed start states.** The gate is one-sided, so the R + 0 °C state will
  release near R_op + 1.5 °C. The three realized start temperatures will be
  about +1.5, +2 and +4 °C instead of 0, +2 and +4. The β_T fit already uses
  measured release temperatures, so it stays valid, but its spread about the
  mean falls from 8 °C² to 3.5 °C² and the standard error of β_T grows by
  √(8 / 3.5) = 1.5. At the registered 1.0 °C it would have been +1, +2, +4
  (4.67 °C², factor 1.3). Changing the offsets would change a printed R1 number
  and is not proposed.
- **Ambient drift over a long night.** R_op is fixed about an hour into a night
  that can run past 24 hours. Settled idle on Tf08 moved 0.6 °C between R0
  sessions on one day. A warmer room later makes gates slower or unreachable; a
  cooler one admits that much more heat. This was already true of the soak
  reference and of W1's single reference. The desk can print each member's own
  pre-warmup median minus R_op from the journals already written.

## 10. Reproducing the numbers

All figures come from these read-only files:
`/Users/edr/night-align/r1-20261111T014106Z/night/align-r1/soak_reference.json`,
`…/idle_soak/sensors/align_thermal.jsonl`,
`…/step_30b/runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl` and
`events.jsonl` (stage times only), `…/step_30b/inventory/inventory_journal.jsonl`,
`/Users/edr/night-align/r0-v4-*/smc/samples.jsonl`, and the pilots'
`custody/hazards/monitor/thermal.jsonl`.

- Own idle: median of Tf08 over the 60 s ending 10 s before the `warmup`
  stage start (where Tf08 first exceeds 27.0 °C). R_op: the same over the 60 s
  ending at the `warmup` stage start.
- Tail models: T(t) = level + a1·exp(−t/τ1) + a2·exp(−t/τ2), t from the
  `warmup` stage end, fitted by least squares to the 1 Hz samples from t = 60 s
  to the end of the gate; τ1 searched over 20–150 s and τ2 over 150–3,000 s,
  amplitudes non-negative; level free or fixed at own idle, τ2 free or fixed at
  956 s as tabulated.
- R0 0550Z slow time constant: log-linear fit of excess over 300–600 s (743 s)
  and 400–600 s (824 s); 956 s from 480–570 s.
- The replay and fit scripts were scratch files outside the repository
  (`/tmp/r1g0-fable/`) and are not part of this record; the method above is
  sufficient to recompute every number.
