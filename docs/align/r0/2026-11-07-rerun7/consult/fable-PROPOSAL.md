# Proposal: SMC classifier amendment for ALIGN R0/R1 on Mac15,9 (blind seat, Fable 5.1, 2026-11-07)

Scope: read-only consult. Inputs: the worktree `/Users/edr/code/jw-wt/r0-smc-cov`, FINAL-DESIGN §2.6/§2.8/V8
and Amendment 1 on `origin/lane/2026-11-05-align-window-council`, `docs/align/r0_step_test_ruling.md`,
`docs/align/smc_temperature.md`, and the real capture `/Users/edr/night-align/r0-v4-20261107T0810Z/smc/`
(1,800 rows, 403 keys, 1 Hz; idle 300 s, GPU load 900 s, recovery 600 s; idle began right after a 12-minute
30B memory check). Nothing else under `night-archive/r0-smc-cov/` was opened. Scratch files and commands are
listed in §8; every number below is from those runs.

## 0. Bottom line

1. The brief's facts check out: the worktree `rank` (NS//2 coverage) gives die 16 / heatsink 141 /
   record-only 246 and picks `s_fast=Tg2I`, `s_slow=TaRT` (§8, `run_rank.py`). All 16 die keys are `Tg*`
   placeholders (95 % of idle samples at an exact value of -2.75, -8.75, -9.0, -0.5 or 0.0; under load
   Tg2I equals TCMb's reading on 839 of 900 samples, so it is a copy of a die reading when the GPU is on and
   a constant when it is off). TaRT's "noise 1.14" is the full-idle SD of a cooling series; its detrended
   noise is 0.042 degC. The whole machine was still cooling at the end of idle (die keys -0.6 degC/min,
   chassis keys -0.5 to -1.0 degC/min), which biases every baseline-referenced number in the capture.
2. No real key on this Mac has t63 <= 5 s. The fastest clean temperatures have t63 18-20 s and cooling
   tau 24-27 s (`Tf18`, `Tf2B`, `Tf24/2D/2E`, `TCDX`); `TCMb` is 25 / 29 s. The design's die class is empty
   here by construction, which is what let the placeholders through.
3. Proposed rule (replayed through a patched copy of `rank`, §4): fast class tau <= 30 s; slow class
   90 s < tau <= 300 s with dT >= 3 degC; baseline and noise from the last 60 s of idle; two placeholder
   refusals (any reading <= 0 degC; a one-second change larger than half the step). On the real capture:
   die 20 / heatsink 25 / record-only 358; `s_fast = Tf18` (dT 45.7 degC, t63 18.9 s, tau 24.7 s,
   noise 0.062 degC). The slow pick is **not determined by this capture**: the slow-class tau values are
   biased by the unsettled idle and the design's "longest tau" rule lands on a 3.0 degC key (`TD14`) whose
   asymptote-free fit says tau is 500-670 s. Measure first (settled idle); the pick rule itself is a
   NEEDS_RULING (§6).
4. The receipt should stop reading the capture-wide 100 ms coverage block. On this capture only 2 % of
   stamps fall within 100 ms of a single grid; per phase on the phase's own grid, 100 % fall within 500 ms.

## 1. What s_fast and s_slow do at window time (Q1)

From `joulewise/align/apple/thermal_gates.py` and `thermal_desk.py` in the worktree:

| Use | Code | What the key must deliver |
|---|---|---|
| Reference R | `capture_reference` l.347-365: medians of both keys over the last 60 s before warmup of the first sidecar member; needs >= 90 % of 1 s slots | a value that is a *temperature* at idle (a power-gated constant makes R meaningless) |
| G0 release | `wait` l.410-463: 10 consecutive samples with `s_fast <= R_fast + delta_fast` and `s_slow <= R_slow + delta_slow`, plus OLS slope of s_slow over 60 s with abs <= 0.2 degC/min (`slow_slope` l.215-226), OS level 0, PM Nominal; cap 600 s, flag and proceed | s_slow noise small enough that the slope test is decidable (derived below); both keys read above R by less than delta only when the machine is back in the reference state |
| G1 / H release | same loop, 5 consecutive samples within `E + delta` where E is the G0 release value; cap `turn_cap_s` <= 300 s, timeout stops the episode | s_fast must shed its load excess within the cap (and, by S6, within a 90 s median); s_slow must change little over a G1 wait, or the gate measures the same transient twice |
| Bands | FINAL-DESIGN §2.6: `delta_k = max(1.0, 3 x SD_k)` from the R1 soak | SD_k <= 1/3 degC keeps the band at its 1.0 floor |
| Desk | `member_record` l.233-247: per-turn `slow_c`, `g0_slow_c`; `acceptance` l.572-576: U2 = range of `g0_slow_c` across members <= 3 degC; `state_sensitivity` l.451-475: U5 beta_T from `g0_slow_c` differences on identical pairs x release range | s_slow must be able to move more than 3 degC between member starts for U2 to be a test at all; a key whose full saturating-step dT is 3-4 degC makes U2 vacuous |

Derived requirements, each with its arithmetic:

- **Fast key tau.** G1 waits for the die excess to fall inside `delta_fast = 1.0 degC`. For a first-order
  decay from a step dT that takes `tau x ln(dT / 1.0)`. The S6 tuning rule names 90 s as the acceptable
  median wait; three time constants (e^-3 = 0.050, the usual "settled" point) in 90 s gives
  **tau <= 30 s**. On this Mac's clean die keys (tau 24-29 s, dT 36-46 degC) the saturating-step release
  time is 93-104 s (table in §4), so R1 should expect G1 medians at the S6 target even with the fastest
  real key; a decode turn heats less than the 900 s matmul, so the real number is shorter and R1 measures it.
- **Slow key tau lower bound.** A slow key should keep most of its state across one fast settling time
  (3 x 30 s = 90 s): tau >= 90 s loses at most 1/e of its excess in that time. **90 s < tau <= 300 s**;
  the 300 s upper bound is the design's (a key slower than the G1 cap can never release once exceeded).
  Keys with 30 s < tau <= 90 s are recorded as "intermediate" (149 keys here) and gated by neither role.
- **Slow key noise.** The G0 slope test uses OLS over 60 one-second samples: sum of (t - mean t)^2 =
  60 x (60^2 - 1)/12 = 17,995 s^2, so SD(slope) = SD / 134.1 per second = 0.447 x SD degC/min. For the
  0.2 degC/min test to be decidable at 3 sigma when the true slope is zero: 3 x 0.447 x SD <= 0.2,
  **SD <= 0.15 degC**. (TaRT's detrended SD is 0.042; the TVS keys 0.009-0.012; TD keys 0.016-0.08.)
- **Fast key noise.** 3 x SD <= delta floor 1.0 gives **SD <= 1/3 degC**; above that the band widens.
- **Slow key dT.** U2 compares `g0_slow_c` across members against a 3 degC range. A key whose
  saturating-step dT is 3 degC cannot exceed that range between two idles, so U2 would pass for the
  wrong reason. The design bar is dT >= 3 degC; I keep it in the class definition and raise the pick
  question in §6 because it changes which sensor counts.

## 2. Rejecting placeholders (Q2)

Observed on the 32 `Tg*` keys: 285 of 300 idle samples at one exact value (-2.75 for Tg2I), the rest at
50-53 degC; under load the value tracks TCMb; two samples after load ends the series is back at the
constant; largest one-second change 86-122 degC/s (Tg2I: -2.75 -> 48.4 in one second at load onset and
85.5 -> -2.75 two samples into recovery). Two observable rules separate this from a temperature, each
with a physical derivation, and a third is a flag.

**P1. Any valid reading <= 0 degC in any phase: not a temperature.** A passively cooled indoor laptop has
no part colder than the room air; 0 degC is the freezing point and the coldest real sensor in this capture
reads 25.8 degC at idle end (TVHC), 25 degC above the bar. Replay: removes **69 of 375 degC keys**: all
32 `Tg*`; the `TV2S/TV3S/TVH2/TVHO/TVM2/TVM3/TVMD/TVMO` virtual keys (values -37 to +23, deltas not
temperatures); the ten `Tf?0`/`Tf?2` offset keys (0 +/- 0.2, or constant -10.5 to -12.0); and 19 constant
zeros already caught by the stale rule (`TH1a/b`, `Ta08..Ta0P`, `Tz1*`). It removes no key that responds
with a positive dT.

**P2. Largest one-second change > 0.5 x the step rise dT: unresolvable at 1 Hz.** A first-order response
changes by `1 - exp(-1/tau)` of its step in one second; that exceeds one half only for tau < 1/ln 2 =
1.44 s, slower than nothing the 1 s sampler can classify. Replay (on keys with dT > 3 x floor): removes
**20 keys**: `TCMz` (alternates between two sources, 30.5 degC/s), the flickering `Tp0c/Tp0o/Tp1K/Tp3X/
Tp3P/Tp0W/Tp0i/Tp1S/Tp06/Tp0E/Tp0M/Tp1G` (16-30 degC/s, detrended SD 3-8 degC), the clamp jumpers
`TV0h/TV1h/TVh0/TVFh` (19-23 degC/s), and `TH0a/TH0b/TH0x` (dT 0.4-0.6 degC, harmless). The ratio for
every surviving key with dT >= 3 degC is <= 0.46 (clean die keys 0.13-0.15: Tf1B 6.4/45.4, TCMb 5.4/36.1).
P2 also catches the `Tg*` keys independently of P1 (ratios 0.97-1.43), so the pair is robust to a
placeholder value that happens to be positive on another machine.

**P3 (flag, not refusal). Floor clamp:** >= 50 % of idle samples at one exact value that is also the idle
minimum, with >= 3 distinct values present. `TV1m` and `TVm0` sit at exactly 40.0 for 63 % of idle (112
distinct values, residual SD 0.000) and would otherwise enter the fast class (dT 28.8, tau 28.4). A very
quiet real sensor (SD below a sixth of its quantum) could look the same, so this is a flag that excludes a
key from the picks only; here it changes no pick. Noted, not proposed as a refusal: `TVFm` shows a ceiling
clamp (18 load samples at exactly 85.00 = its maximum).

What the existing stale rule (fewer than 3 distinct idle values) does not catch and these do: `Tg*`
(14-15 distinct values because the GPU wakes a few times during idle), the clamps, and the sub-zero
virtual keys. I kept the stale rule on the whole idle as registered; applying it to the 60 s baseline
window would also reject slow quantized keys that legitimately move less than two quanta in a minute
(`TB1T`, `TG1B` here, with 2 distinct values).

## 3. The idle baseline (Q3)

**Defect in the current code.** `rank` takes the baseline as the median of the whole 300 s idle (l.328)
and noise as its SD (l.316). After the memory check the idle was a cooling curve: TCMb fell from 63.1 to
49.4 degC during idle, so its full-idle median (50.81) is 1.1 degC above its idle-end value (49.71); the
"noise" 3.24 is drift. For TaRT the full-idle SD is 1.14 against a detrended 0.042. For the slow keys the
bias flips the sign of the 50-60 s rise (TVS0/1/2, TD21/TD23: `rise60` -0.7 to -1.2 degC), so `t63` is
None and the current `heatsink` condition (`t63 is not None and t63 > 5`) drops the slowest keys, the ones
it exists to find. With the full-idle baseline and my classes nothing at all classifies (variant D in §4).

**B1. Baseline = median of the last 60 s of idle; noise = SD of the OLS residual over that window.** This
is the same statistic and window the sidecar uses for the window reference R (`capture_reference`), so
the classifier's baseline is "as settled as the window's reference" by construction. The quantum and the
`max(0.05, quantum, noise)` floor are unchanged.

**Settle criterion.** The remaining excess of a first-order cooling curve equals slope x tau. The G0
release criterion is abs(slope over 60 s) <= 0.2 degC/min; at the slowest gated tau of 300 s that is
0.2/60 x 300 = 1.0 degC = the band floor, which is why I propose the same number for the R0 baseline:
**a key whose last-60 s OLS slope exceeds 0.2 degC/min in magnitude gets the flag `idle_unsettled`**;
the picks prefer unflagged keys and a flagged pick is printed PROVISIONAL-UNSETTLED. In this capture 42 of
45 class members are flagged (die keys -0.6 to -0.8 degC/min; slow keys -0.5 to -1.0; only TaRT, TaLW
and TaRW are inside 0.2).

**Cost in seconds**, from this capture's cooling curves (asymptote-free exponential fits, diagnostic only;
`metrics.py` output in §8): the slow candidates TVS0/1/2 (idle tau 136-142 s, slope at idle end 0.68-0.82
degC/min) would have needed +170 to +200 s of idle to reach 0.2 degC/min; TD21/TD23/TDBP +215 to +249 s;
the TD1x/TD2x group (idle tau 350-540 s) +380 to +535 s, and those fits put them beyond the 300 s class
anyway. The die keys ride on the chassis, so their slope decays at the chassis rate: TCMb would need about
180 x ln(0.63/0.2) = 207 s. A fixed dwell derived from the class bound: initial excess after the 12-minute
load was 15.3 degC (TVS2 fit amplitude); to within 1.0 degC at tau = 300 s takes 300 x ln(15.3) = 819 s,
and 3 x 300 = 900 s settles any key in the class to 5 %. So: **either a 900 s pre-idle dwell after the last
model load (+15 min of R0), or run the SMC step first in R0, before the weights hash and the memory
check, at zero added time**, with the flag recording whether it worked. I propose the reorder plus the
flag, and no automatic idle extension (an extension loop would run to its cap on the tau > 300 s chassis
keys every time).

## 4. Classes and picks, replayed through `rank` (Q4)

Rule text the code could implement (replacing `RULE` and the class lines l.357-360 of `smc_enumeration.py`):

> Baseline and noise: median and OLS-residual SD of the last 60 s of idle. Reject keys with any reading
> <= 0 degC (P1), with fewer than 3 distinct idle values (stale), or whose largest one-second change
> exceeds half their step rise (P2). Fast class: dT > 3 x floor, t63 <= 30 s, cooling tau <= 30 s, noise
> <= 1/3 degC. Slow class: dT >= 3 degC, 90 s < tau <= 300 s, noise <= 0.15 degC; t63 is recorded but
> not required. Keys with 30 s < tau <= 90 s are intermediate, recorded only. A key whose last-60 s idle
> slope exceeds 0.2 degC/min is flagged idle_unsettled; picks prefer unflagged keys. s_fast = largest dT
> in the fast class; s_slow = (rule under NEEDS_RULING, §6) in the slow class; lexical tie-break.

Replay on the real capture (`rank_v2.py`, full output in `rank_v2_output.txt`; P1/P2/stale counts are
identical across variants: 69 / 20 / 70, plus 28 non-degC keys):

| Variant | die | heatsink | record-only | s_fast | s_slow | settled picks |
|---|---|---|---|---|---|---|
| worktree `rank` today (for reference) | 16 | 141 | 246 | Tg2I | TaRT | n/a |
| **A** proposed, longest-tau slow pick, settled preferred | 20 | 25 | 358 | **Tf18** | TaRT | fast no / slow yes |
| A' same, no settled preference | 20 | 25 | 358 | Tf18 | TD14 (dT 3.0) | no / no |
| B slow dT >= 6 degC (2 x the U2 range), longest tau | 20 | 15 | 368 | Tf18 | TDeR (dT 6.2, tau 168) | no / no |
| C slow pick = largest dT | 20 | 25 | 358 | Tf18 | TVFm (ceiling-clamped, flagged unsettled) | no / yes |
| D full-idle baseline (current code) with new classes | 0 | 0 | 403 | None | None | inconclusive |
| E fast tau <= 35 s | 76 | 25 | 302 | TVH3 (dT 64, tau 33) | TD14 | no / no |

Fast class under A, by dT (key, dT degC, t63 s, tau s, noise degC, estimated saturating-step release
`tau ln(dT/1)` s): Tf18 45.7 / 18.9 / 24.7 / 0.062 / 95; Tf2B 45.6 / 18.3 / 24.4 / 0.070 / 93;
Tf1B 45.4; Tf24 = Tf2D = Tf2E 45.3 (one sensor under three keys, 900/900 identical); Tf14 = Tf1D = Tf1E
45.2; Tf1A, Tf19 44.3; Tf28 43.8; Tf29 43.4; TCDX 43.0 / 20.3 / 25.9 / 0.111 / 98; Tf2A 42.7;
Ts0h 38.5; TCMb = TVD0 36.1 / 25.2 / 28.9 / 0.084 / 104; TV1m = TVm0 28.8 (P3 flag, excluded from picks).
Tf18 and Tf2B differ by 0.1 degC, below their noise; either is the same kind of sensor, and R1's
production step re-selects anyway (design). TVH3 (dT 64.1, tau 33.3, max reading 137 degC) is excluded by
tau <= 30; admitting it (E) lengthens the estimated release from 95 to 139 s.

Slow class under A, by dT (key, dT, tau, noise, last-60 slope): TVFm 22.5 / 130.5 / 0.040 / -2.7;
TMVR 17.1 / 90.5 / 0.041 / -0.52; TD23 = TDVx 12.8 / 133.9 / 0.031 / -1.0; TVS2 11.8 / 147.7 / 0.012 /
-0.82; TD21 11.7 / 145.1; TVS1 11.1 / 145.1 / 0.011; TDER 10.4; TDEL 10.1; TVS0 9.2 / 148.3 / 0.009 /
-0.68; TDBP 8.4 / 146.1; TDCR 6.7 / 153.1; TDEC 6.6; TDeR 6.2 / 168.2; TDeL 6.1; TaRW 5.1 / 94.8;
TD13 4.9 / 169.4; TDTP 4.5; TaRT 4.4 / 129.0 / 0.042 / -0.13 (settled); TaLT 3.9 / 116.4; TD20 3.9 /
182.2; TaLW 3.7; TD24 3.7 / 177.0; TD11 3.5 / 182.3; TD14 3.0 / 182.6.

Why the slow pick is not determined here: the model-free tau is a crossing of `baseline + peak/e`, and
the baseline is 0.5-2 degC too high for every unsettled key (the system cooled below its idle-end value
during recovery: TCMb 47.9 after 600 s recovery vs 49.7 at idle end). For a slow key with a small dT the
crossing then measures the continuing chassis cooling, not the key's response: TD14's crossing says 183 s,
its asymptote-free fits say 539 s (idle) and 665 s (recovery), i.e. beyond the 300 s class; TD11/TD20/TD24
375-499 s; TDCR/TDEC/TDeL/TDeR 298-310 s (at the edge). TVS0/1/2 fit at 136-182 s and TaRT/TaLT at
86-247 s (TaRT's two fits disagree because its amplitude is 4-5 degC). So the ordering among TaRT, TaLT,
TVS* and the TDxx keys under "longest tau" is not resolved by this capture, and a 0.3 degC baseline error
(10 % of the 3 degC bar) moves TD14 in or out of the class. **Measure first**: a settled idle (slopes
inside 0.2 degC/min), then the pick. My expectation from the fits: the TD1x/TD2x group leaves the class
(tau > 300 s), and the candidates are TVS0/1/2 (dT 9-12, noise 0.01) against TaRT/TaLT (dT 4-5, noise
0.04), with TD21/TD23/TDBP/TDCR possible.

## 5. The receipt (Q5)

`r0_host.smc_enumeration` l.484-491 reads `payload["coverage"]["per_key"][key]` and requires
`valid/expected > .99` and `expected >= 600`. That block is written by `scripts/align_smc_enumerate.py`
with `temperature.coverage(...)` at the class default tolerance of 100 ms, on one grid anchored at the
first sample of the whole capture. Measured on this capture: read duration 79-392 ms (p50 86, p95 139);
started stamps within each phase sit 0-200 ms late on the phase grid (idle histogram: 57 / 90 / 116 / 37
samples in the 0-50 / 50-100 / 100-150 / 150-200 ms bins), and `collect` re-anchors `due` at each
phase start (`origin = phase_start.monotonic_ns`), so the three phases sit on three different grids.
Result: capture-wide per-key coverage 36 / 1800 = 0.02 for every key; per phase on the phase grid 12 %,
29 %, 22 % at 100 ms and **100 % at 500 ms**; consecutive spacing 850-1298 ms, no gap over 1.3 s. The
classifier passed every key's coverage at NS//2 while the receipt refused the same keys from the other
block. Two definitions of one quantity is the defect.

What the receipt should read instead: the classifier's own row for each pick,
`classification["ranking"][key]["phase_coverage"][p] >= .99` and `["phase_read_error_fraction"][p] < .01`
for all three phases (these are the NS//2, phase-grid numbers `rank` already enforces for class
membership, so a classified key cannot fail them), plus the 10-minute bar as
`sum(end_s - start_s over phases) >= 600` from `payload["phases"]` (1,800 s here). Keep
`coverage["period_ns"] == 1_000_000_000`. The capture-wide block stays in r0.json as a diagnostic or is
recomputed per phase at NS//2 by the enumerate script; either way the receipt does not gate on it. The
sidecar at window time reads two to three keys in a few milliseconds, so its own 100 ms tolerance is
unaffected; this is an R0 enumeration (403-key read) artefact.

## 6. Decisions I made, and NEEDS_RULING

Decisions the code and design text determine, made here:
- Baseline window = last 60 s of idle, median; noise = OLS-residual SD over it (same window as R).
- Fast class tau <= 30 s and t63 <= 30 s (from the S6 90 s target as 3 tau); slow class 90 s < tau <= 300 s
  (3 x 30 s lower bound; design upper bound); keys between are recorded only.
- Noise bars 1/3 degC (fast; 3 SD <= delta floor) and 0.15 degC (slow; slope test at 3 sigma).
- P1 (<= 0 degC) and P2 (one-second change > half the step) are refusals; P3 (floor clamp) is a flag.
- `idle_unsettled` at 0.2 degC/min (the G0 criterion) is a flag; picks prefer unflagged keys.
- The receipt reads the classifier's per-phase coverage; the capture-wide block is diagnostic.
- R0 order: SMC enumeration before any model load, no automatic idle extension.
- `t63` is not required for the slow class (its absence means "slower than 60 s", which is the class).

NEEDS_RULING (changes which sensor is gated):
1. **Slow pick rule.** FINAL-DESIGN §2.6 says longest tau <= 300 s among dT >= 3 degC. On this Mac that
   rule selects at the 300 s edge, among the smallest-dT keys, where tau is least certain and U2 is least
   able to fail (§1). Options, with this capture's (unsettled) outcome: (a) design literal: TD14 (dT 3.0)
   or TaRT (dT 4.4) if unsettled keys are excluded; (b) longest tau with dT >= 6 degC (twice the U2 range,
   so a between-member excursion of 3 degC is reachable at half saturation): TDeR (dT 6.2, tau 168);
   (c) largest dT in (90, 300] s: TVFm, which carries a ceiling clamp and a -2.7 degC/min slope, so (c)
   needs the clamp flag to exclude from picks too, after which it would be TD23/TDVx (12.8) then TVS2
   (11.8, noise 0.012). My recommendation is (b) or (c) with clamp exclusion, decided after a settled R0.
2. **Fast class bound 30 s vs 35 s** (Tf18 vs TVH3): 30 s is my derivation; 35 s admits the hottest key at
   a 46 % longer estimated release. I recommend 30 s.
3. **R0 reorder** (SMC step first) is a protocol change to Amendment 1 §A5 step order.

## 7. What to verify in the next R0 run

1. Run the SMC step first (no model load before it). Check every eligible key's last-60 s slope is inside
   0.2 degC/min (no `idle_unsettled` flags on the class members). If any remain, record the dwell that
   would have cleared them (slope / 0.2 at the fitted tau) in the session record.
2. P1 removes exactly the 32 `Tg*` keys plus the virtual/offset keys listed in §2 and nothing with a
   positive dT; P2 removes `TCMz`, the twelve flickering `Tp*` keys and the clamp jumpers, and no key with
   a one-second ratio below 0.5 (the surviving maximum here is 0.46).
3. Fast class: Tf18/Tf2B/Tf24 family with tau 24-27 s and dT 43-46 degC; the pick's noise <= 1/3 degC.
   Record the saturating-step release estimate `tau ln(dT/1)` beside the pick; R1 compares it with the
   measured G1 waits.
4. Slow class with a settled baseline: do TD14/TD11/TD20/TD24 leave the class (tau > 300 s) as the fits
   predict? Which key is longest among dT >= 3 and among dT >= 6? Print both before the ruling in §6.1.
5. Receipt: `readability_bar_met` true for the two picks from the classifier rows; the capture-wide block
   left diagnostic. Re-run the receipt on this very capture after the change: it should pass for Tf18 and
   whichever slow key the rule selects (both have phase coverage 1.00 at NS//2).
6. The 60 s baseline window: confirm no slow key in the class has fewer than 3 distinct values over the
   whole idle on a settled machine (if quantized keys go stale when settled, the stale rule needs a
   quantum-aware form; `TB1T`/`TG1B` with quantum 0.1 are the ones to watch, both tau > 300 s).

## 8. Commands and files (scratch: `/Users/edr/night-archive/r0-smc-cov/consult/fable/`)

Interpreter: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P`
with `PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov`; `smc_enumeration.__file__` printed as the worktree path.

- `load_capture.py` -> `capture.pkl`: 1,800 rows, 403 keys; stored response in r0.json was
  inconclusive (0/0/403, capture-wide coverage 0.02 at 100 ms).
- `run_rank.py` -> `rank_baseline.json`: worktree `rank` on the capture: pass, Tg2I / TaRT, 16 / 141 / 246.
- `metrics.py` -> `metrics.json`, `metrics.tsv`: per-key idle mode/fraction/min, full and last-60 medians,
  full SD vs detrended SD vs first-difference SD, slopes, rise/t63/tau under both baselines, one-second
  jumps, recovery return-to-mode.
- Inline runs (outputs in this file): P1/P2/P3 replays; per-phase stamp offsets and `Coverage` at 100 ms
  vs 500 ms; idle and recovery exponential fits and 60 s window slopes; mirror checks (Tg2I == TCMb 839/900
  under load; Tf24 == Tf2D == Tf2E; TCMb == TVD0; TD23 == TDVx).
- `rank_v2.py` -> `rank_v2_proposed.json`, `rank_v2_output.txt`: the patched classifier and variants A-E.
