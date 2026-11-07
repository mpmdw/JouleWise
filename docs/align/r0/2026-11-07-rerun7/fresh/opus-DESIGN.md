# Fresh design: choosing and qualifying ALIGN's thermal-control keys on the Mac15,9

Blind seat: Opus 5.5, 2026-11-07. I read only the brief, the worktree code and docs it named, the
council design (FINAL-DESIGN and AMENDMENT-1 on `origin/lane/2026-11-05-align-window-council`), and
the R0 re-run 7 capture. All scripts and outputs are in this directory. Interpreter: the
pilot2 venv, `-B -P`, `PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov`. Every run printed
`thermal module: /Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/thermal.py`.

## 0. Summary

- **What the keys must do.** Every gate (G0, G1, H) runs while the GPU is idle. So both keys
  must read a real temperature at GPU idle. S_fast has to show heat still sitting in the die.
  S_slow has to show stored heat that outlasts the die's own decay. It also has to support a
  60 s slope test at 0.2 °C/min and give U2/U5 a sensitive covariate.
- **Why the current picks fail.** On this Mac, no key that reads continuously at idle has
  t63 ≤ 5 s. Only the power-gated GPU keys (`Tg*`) reach that speed. They read a placeholder
  (for example −2.75 °C) in 286 of 300 idle seconds. `valid_value` accepts −40 to 150 °C, so
  at window time a `Tg*` pick reads −2.75 at every gate and is always "in band".
  - Replayed on the recovery leg, the current pair (Tg2I/TaRT) releases a G1 gate at 168 s.
    It releases on TaRT alone, while the die key and the heatsink key are both still more
    than 1 °C above the reference. They come back within 1 °C at 279 s and 272 s.
- **Proposal.** Replace the die/heatsink class windows with validity rules plus two rules
  that pick each key for its role:
  - S_fast = the valid key with the largest rise;
  - S_slow = the valid key holding the most stored heat, in band units, once S_fast's own
    excursion has decayed.

  Replay on the real capture (403 keys) gives 132 valid keys, **S_fast = Tf18** and
  **S_slow = TSXR**. The S_slow pick is stable within the cluster {TSXR, TSVR, TR1d, TCHP}
  for every late-time factor from 3 to 8.
- **Baseline.** The R0 idle was still cooling, at 0.6–1.0 °C/min, when the load began.
  - Settle rule: every clean key's |120 s slope| must be ≤ 0.2 °C/min before the load starts.
  - Measured settle time: about 930 s after heavy heat. Cost: +635 s to +900 s of R0 time
    over today's 300 s idle (cap 1,200 s).
  - Running the SMC step before the memory check may cost nothing (measure first).
- **Receipt.** It should read the classifier's own per-phase coverage of the picks, not the
  capture-wide block. That block, at its 100 ms tolerance on one grid, reports 0.02 for every
  key in this capture.

## 1. What S_fast and S_slow do at window time (Q1)

These facts come from `joulewise/align/apple/thermal_gates.py`:

- **Reference** (`capture_reference`, l.347-405): R = the median of S_fast and S_slow over
  the final 60 s of the first member's idle. It needs ≥ 90 % coverage, else
  `thermal.state_unobserved`.
- **G0** (`wait`, l.410-516, `required = 10`, `cap = 600`): releases after 10 consecutive
  samples that meet all of:
  - S_fast ≤ R_f + δ_f and S_slow ≤ R_s + δ_s;
  - |OLS slope of S_slow over 60 s| ≤ 0.2 °C/min (`slow_slope`, l.215);
  - OS thermal level 0 and powermetrics Nominal.
- **G1 and H**: release after 5 consecutive samples within δ of E, where E is the episode's
  G0 release values. Cap `turn_cap_s` (S7 = min(300 s, 3 × R1 p95 recovery)).
- **Unobserved**: trailing-60 s coverage < 90 % makes the gate a timed wait plus X4.
- **Validity** (`valid_value`, `thermal.py:44-46`): a T* reading is valid if −40 ≤ v ≤ 150.
- **Bands** (FINAL-DESIGN §2.6): δ_k = max(1.0 °C, 3 SD_k).
- **Acceptance** (§2.4): U2 requires the range of G0-release S_slow ≤ 3.0 °C. U5 for heavy
  cells uses β_T (J/°C on S_slow) × the release range. The labelled sensitivity adds G0
  release S_slow.

The fitness requirements follow from these:

| | Requirement | Source |
|---|---|---|
| F1 | Both keys read a real temperature in ≥ 99 % of seconds **while the GPU is idle**. Every gate and the reference sit in GPU-idle time. | gates; U1(c) |
| F2 | S_fast reflects the die's current heat: large rise, fast decay, so it holds a gate while the last turn's heat is still in the die. | G1 purpose (§1(c)) |
| F3 | S_slow carries stored heat that outlasts the die decay. Its rise must be large against δ, or U2 is met trivially and β_T is noise. Its noise must let the 60 s slope test resolve 0.2 °C/min. It must come back within the G1 cap. | G0 slope, U2, U5, S7 |
| F4 | Values must be measurements: no placeholders, clamps or computed values above the heat source. A placeholder reads "cold" and passes every band test. | gate logic |

**Replay of the gate on the recovery leg** (`gate_replay.py`). E = the idle reference,
δ = 1.0, 5 consecutive samples:

```
current picks Tg2I/TaRT, window R rule: {'Tg2I': -2.75, 'TaRT': 30.686} -> release after 168 s
Tg2I first recovery readings: [(0, 85.49), (1, 85.50), (2, -2.75), (3, -2.75), ...]
Tf18 alone 279 s; TSXR alone 272 s; pair 279 s
```

The current pair releases 111 s before the die and heatsink keys return.

## 2. Physical facts of this capture (all executed)

These shaped the rules.

1. **Modes**, measured as the cooling 1/e time relative to the last-60 s idle reference
   (`feat.py`, `tback.py`, `run_v5.py`):
   - `Tg*` GPU keys: τ ≈ 2 s, readable only under load.
   - Continuous die keys (Tf1x/Tf2x, TCMb, TCDX, Ts/Th/Te): τ 24–43 s.
   - Heatsink keys (TSXR, TSVR, TR1d, TCHP, TPMP, TRD*): τ 56–91 s.
   - TVS*/TD* keys: τ 113–183 s.
   - No clean key has τ in 44–55 s. The fastest continuous key has t63 = 21 s (Tf18 and
     others). **The design's "die: t63 ≤ 5 s" can only be met by the placeholder keys.**
2. **Fans** (`fans.py`): off at 169 s of idle; on at 73 s into load; off at 180 s after load
   end. With the fans off, all die keys cool on a common slow mode, τ = 427–510 s
   (`tailfit.py`, segment 1381–1800 s, rms 0.14–0.23 °C).
   - At fan-off, nearly every clean key is still 1.9–3.1 °C above its pre-load reference
     (`tback.txt`). So late recovery is limited by one chassis mode common to all keys.
3. **The idle baseline was not settled** (`slopes.py`, trailing 60 s OLS, °C/min):
   - at idle end: Tf18 −0.64, TCMb −0.63, TVS2 −0.82, TD23 −1.00, TaRT −0.13;
   - 600 s after load end, still: Tf18 −0.26, TCMb −0.41, TVS2 −0.35, TaRT −0.28.
4. **Core-local CPU keys (Tp*, TCMz) spike** by 13–30 °C in single idle seconds
   (`survey2.py`). These are short CPU bursts, including the tool's own 5 s census. A
   stored-heat mode cannot do this.
5. **Some keys are computed, not measured** (`virt.py`, `runs.py`):
   - TVH3 reads 137 °C under load, 20 °C above the GPU's own sensors (Tg max 104 °C). It
     recovers on a constant 2.0 °C/s ramp.
   - TVsa/TVss/TVh0 hold one value for 603 s, then step by 4–5 °C.
   - TV1m/TVm0 clamp at exactly 85.0.
6. **Sampling** (`run`, inline): sample offsets within each phase are 80–113 ms median and
   150 ms maximum. Reads last 86 ms median and 392 ms maximum. Intervals run from 0.85 s to
   1.298 s.

## 3. Rejecting placeholders (Q2)

**Rule P1, physical floor.** A T* reading below 10 °C is invalid. It counts as a failed read
in coverage, in `rank`, and at window time.
- Derivation: Apple's operating ambient minimum for this machine is 10 °C ("Operating
  temperature: 50° to 95° F (10° to 35° C)", MacBook Pro (16-inch, Nov 2023) Tech Specs,
  support.apple.com/en-us/117737, fetched today). A passively heated part of a running
  computer is never colder than its intake air.

**Rule P2, isolated recurring sentinel.** This is a floor-independent backstop for a
placeholder at or above 10 °C, and for clamps. A value v0 is a sentinel if both hold:
- the key enters v0 at least twice by a 1-sample jump of more than 3 °C;
- v0 is more than 3 °C from every other reading of that key in the capture.

Readings equal to a sentinel are invalid.
- Derivation of 3 °C = 3 × δ_floor: at idle, a stored-heat mode moves at most about
  ΔT_max × (P_background / P_load) / τ_min ≈ 45.7 × 0.1 / 24 ≈ 0.2 °C/s. A real
  temperature series also fills in the values between its extremes over time; a sentinel
  never does.
- "At least twice": one entry could be a single real excursion. Two exact returns to an
  isolated value is a written placeholder.

With P1 and P2, the existing 99 % per-phase coverage bar removes the key, because
placeholder seconds now count as failed reads.

**Replay over all 403 keys:**

- P1 removes 75 (`run_v5.py`, `survey.py`):
  - 32 `Tg*`: placeholder in 286/300 idle seconds, real only under load;
  - 43 keys that never read a temperature: constants 0, 1.0, 9.97, −2.7 and −10.5…−11.95
    (TH1a/b, TVMD, Ta08/09/0G/0H/0K/0L/0O/0P, Tf02/12/22/32/42, Tf0C/1C/3C/4C, Tf11,
    Tz11–Tz18, Tz1j); near-zero signed series Tf00/10/20/30/40; negative or mostly sub-10
    series TV2S, TV3S, TVH2, TVM2, TVM3, TVMO, TVHO, TVSO.
- P2 alone flags 34 (`sentinel2.py`): exactly the 32 `Tg*` (sentinels 0.0, −0.5, −2.75,
  −8.75, −9.0; nearest real value ≥ 3.2 °C away; up to 95.3 % of idle) plus TV1m/TVm0
  (clamp at 85.0).
- Combined, inside `rank_v5`: 75 by the floor plus 2 sentinel clamps.
- No key is removed whose values were all real and ≥ 10 °C, except the two clamped keys.

## 4. Idle baseline: settle rule and cost (Q3)

**Settle rule.** The idle phase runs for at least 300 s. It continues until every key that
passes P1, P2, coverage, the stale check and the spike rule (§5 V5) has |OLS slope over the
trailing 120 s| ≤ 0.2 °C/min. Cap 1,200 s. A key still above the bar at the cap is not
blocking; the per-key drift rule (V6) removes it for that capture.

Derivations:
- **0.2 °C/min.** Per-key drift validity (V6) needs |s| × τ ≤ δ. Gated keys have τ ≤ 300 s
  and δ ≥ 1.0 °C, so |s| ≤ 1.0/5 min = 0.2 °C/min guarantees V6 for every candidate. It is
  also G0's own release bar, so the R0 baseline is a state G0 would accept.
- **120 s window.** The OLS slope standard error at 1 Hz is 60σ/√(n(n²−1)/12) °C/min. That
  is 0.158σ at n = 120, and 0.447σ at n = 60.
  - For σ ≤ 0.149 °C (the slow-key ceiling in V8), 3 SE = 0.07 °C/min at 120 s. That
    resolves 0.2.
  - At 60 s, 3 SE = 0.20, which equals the bar and cannot resolve it.
- **Cap 1,200 s.** Measured settle time (`settle2.py`; per key: elapsed time + 510 s ×
  ln(|s|/0.2), with τ_passive = 510 s, the largest fitted fan-off τ):
  - after the 900 s GPU step: median 929 s, max 1,038 s;
  - after the memory check: median 935 s, p90 1,025 s; physical keys max 1,229 s
    (TD21, TD23, TDVx).

  1,200 s covers every key after the heaviest R0 load, with about 15 % margin for the
  427–510 s spread in τ.
- **Residual bias at the bar.** The ΔT and late excess of a slow key can still be biased by
  up to s × τ_passive = 0.2 × 8.5 = 1.7 °C. Within a cluster this bias is common-mode. V6
  stops it from deciding a class.

**Cost.**
- With today's order (SMC step after the memory check): +635 s expected (settle at about
  935 s vs today's 300 s idle), +900 s worst case (cap).
- **Decision I made:** run the SMC step before the memory check and any model load. Then the
  cost is 0–900 s, depending on the Mac's state beforehand. **Measure first:** the next R0
  logs the trailing slopes from idle start.

**R1 consequence.** The planned "10-min cooldown" between step tests is too short after
heavy heat. 600 s after the 900 s step, slopes were still 0.23–0.47 °C/min. R1 should use
the same settle rule between steps.

## 5. Selection rule (Q4)

Rule text, implementable in `rank`. Bracketed lines are derivations.

```
Per T* key, from the R0 (or R1) step capture:
V1  A reading is invalid if < 10 degC (P1) or equal to an isolated recurring sentinel (P2).
V2  Each phase: >= 99 % of 1 s cells valid (NS//2 cells), < 1 % failed reads.   [U1(c); unchanged]
V3  Idle has >= 3 distinct values.                                               [unchanged]
V4  sigma_k = SD of 1 s first differences / sqrt(2), over the last 240 s of idle and the
    last 300 s of recovery (drift-free); q_k = smallest step between distinct values;
    sigma_eff = sqrt(sigma^2 + q^2/12); delta_k = max(1.0, 3 sigma_eff).          [FINAL-DESIGN 2.6]
    R_k = median of the last 60 s of idle.                                       [window R rule]
    dT_k = median of the last 10 % of load - R_k. Require dT_k >= 3 delta_k.
    [A gate band of delta releases a first-order excursion after tau*ln(dT/delta).
     The key holds at least one tau only if dT/delta >= e; 3 rounds e up.]
V5  Quiet 1 s steps > 1.0 degC in <= 1 % of quiet seconds.
    [A step > delta_floor at idle is not stored heat (section 3). A spike second is a second
     with no stored-heat reading, so it counts against the same 99 % bar as a missing read.]
V6  tau_k = cooling 1/e crossing from the first recovery value, relative to R_k.
    Require |idle slope over 120 s| * tau_k <= delta_k.
    [If the baseline moves more than one band during tau, the crossing is not resolved
     at the gate's resolution.]
V7  dT_k <= dT of the fastest valid key + 3 delta_k.
    [With one heat source, the node nearest the source responds fastest and rises most.
     A slower key that rises more is not a measurement on that path.]
Picks:
S_fast = valid key with the largest dT_k (lexical tie).
t_late = 5 * tau(S_fast)          [e^-5 = 0.67 %: 0.31 degC of a 45.7 degC excursion, < delta_floor/3]
S_slow = among valid keys != S_fast with tau_k <= 300 s and sigma_eff <= 0.149 degC,
         the largest (median value over t_late +/- 5 s after load end - R_k) / delta_k.
         [300 s = G1 cap ceiling (S7).]
         [0.149: 3 x SE of the 60 s G0 slope (0.447 sigma) <= 0.2 degC/min.]
         [Score: the key that still shows the most bands of stored heat once the die has let go.
          That is S_slow's job, and it keeps U2's 3.0 degC range from being met trivially.]
Inconclusive if either pick is null or they are equal.
```

Heating t63 is dropped from selection: gates run on the cooling side, and heating is confounded
by fan onset (73 s) and the fan-regulated overshoot (die keys peak near 104 °C at 150–180 s,
then fall to about 86 °C). t63 stays as a diagnostic.

**Load step: unchanged** for R0 (900 s MLX matmul).
- 900 s charges a mode with τ ≤ 300 s to 95 % (the ruling's reason).
- It overcharges the chassis mode relative to a planning turn. That is conservative for
  the cap.
- R1 re-ranks on the real planning-turn step, as designed.

**Replay through the patched `rank` copy** (`rank_v5.py`, which reuses `thermal.Coverage`
with NS//2 cells; `run_v5.py`):

```
=== enforce_drift=True ===           (the proposal)
   132  VALID
    75  placeholder (< 10 degC) readings
    65  constant/stale idle
    41  quiet 1 s steps > 1 degC in > 1% of seconds (spiky)
    32  dT < 3 delta_k
    28  not a temperature unit
    27  idle drift over tau exceeds delta_k (baseline not settled)
     2  isolated recurring sentinel readings          (TV1m TVm0)
     1  dT exceeds the fastest key's dT (Tf2B) ...    (TVH3)
  S_fast Tf18  t_late 123.7 s  S_slow TSXR
  slow candidates (n=91): TSXR 5.16, TSVR 5.15, TR1d 5.09, TCHP 5.08, TSWR 4.90 ... die keys Tf1A/Tf1B 4.10
```

What each rule removes:
- V5, spiky (41): Te06 Te0Q Th06 Th0A Tp04 Tp05 Tp06 Tp0C Tp0D Tp0K Tp0L Tp0M Tp0R Tp0S
  Tp0T Tp0U Tp0V Tp0a Tp0b Tp0g Tp0h Tp0m Tp0n Tp0w Tp10 Tp16 Tp17 Tp18 Tp1E Tp1F Tp1G Tp1I
  Tp1J Tp1Q Tp1R Tp3O Tp3T Tp3W Ts06 Ts0T Ts0i. TCMz falls to V4 instead (σ 7.8 → δ 23).
- V6, drift (27): TD11 TD13 TD14 TD20 TD21 TD23 TD24 TDBP TDCR TDEC TDEL TDER TDTP TDVx TDeL
  TDeR TPD2 TPD4 TPD5 TPD6 TVFh TVFm TVS0 TVS1 TVS2 TaLP TaRF.
- TCMb and TCDX, flagged by reviewers as clean, are valid. They are in the die cluster and
  not picked.

Pick facts (`gate_replay.py`):
- **Tf18:** R 33.50, ΔT 45.68, τ 24.7 s, σ 0.058, δ 1.0, coverage 1.0/1.0/1.0, 0 failed
  reads, max interval 1.298 s.
- **TSXR:** R 34.26, ΔT 29.96, τ 68.2 s, σ_eff 0.027 (3 SE of the 60 s slope =
  0.036 °C/min), δ 1.0, late score 5.16, drift 0.85.

Sensitivity:
- **Late-time factor** (`sens.py`): 3τ → TSXR; 4τ → TSVR (tied with TSXR at 7.25); 5τ and
  6τ → TSXR; 8τ → TSVR. S_slow stays within one cluster.
- **Without V6:** S_slow = TVFm, a clamping computed key whose late excess is inflated by
  7.25 bands of baseline drift. V6 is load-bearing until R0 is settled.
- **The design's own S_slow rule** (longest τ ≤ 300 s, ΔT ≥ 3) inside the new valid set
  picks TaRT: τ 129 s, ΔT 4.37, late score 1.65. TaRT shows a third of TSXR's stored heat at
  gate time, and released the gate first in the replay.

## 6. The receipt (Q5)

The check is at `r0_host.py` l.481-489. It re-checks the picks against
`payload["coverage"]["per_key"]`, a capture-wide block computed at a 100 ms tolerance on one
grid. Three things are wrong with it:
- The block reports `sample_fraction 0.02` (36 of 1,800) for every key, including all
  candidates. Each phase restarts the grid, and jitter reaches 150 ms.
- It counts placeholder readings as valid.
- It is a second rule for the same quantity.

**It should read the classifier's own per-pick numbers:**
- `ranking[pick]["phase_coverage"][p] >= 0.99` and
  `phase_read_error_fraction[p] < 0.01` for p in idle, load and recovery. These already use
  NS//2 cells and, under V1, placeholder-aware validity.
- Total phase duration ≥ 600 s (the AMENDMENT-1 R0 bar: 10 min).
- Max interval between valid readings of each pick ≤ 2 s (the U1(c) gap bar).

`scripts/align_smc_enumerate.py` should then either recompute its `coverage` block per phase
with the same cells or label it diagnostic, so that only one coverage number exists.

## 7. Decisions I made (determined by the code, design or physics)

1. A 10 °C validity floor for T* in `thermal.valid_value`, applied in R0, R1 and window
   gates. P2 sentinel backstop.
2. Reference = the median of the last 60 s of idle, the same as the window's R. The
   whole-idle median is not used.
3. Noise from first differences (drift-free), quantum folded in. δ by the §2.6 formula.
4. Spike seconds count against the existing 99 % bar.
5. Per-key drift validity V6, and the R0 settle rule with a 1,200 s cap.
6. The ordering rule V7. It removes only TVH3, which reads 137 °C.
7. The SMC step runs first in R0. R1 settles between step tests.
8. The receipt reads the classifier's per-phase coverage.
9. Load step unchanged.

## 8. NEEDS_RULING (these change which sensors count)

- **N1. Replace the die/heatsink windows with role rules.** The windows are t63 ≤ 5 s for
  die and 30 < τ ≤ 300 s for heatsink. On this Mac the die window holds only placeholder
  keys. "Longest τ" favours insensitive keys (TaRT).
  - Proposed: S_fast = largest ΔT; S_slow = largest late excess in band units.
  - Fallback if the owner wants classes kept: a fast class τ ≤ 47 s and a slow class
    47 s < τ ≤ 300 s, with S_slow chosen by late excess. 47 s comes from
    t_fan_runon / ln(ΔT_max/δ) = 180.1 / ln 45.7. It falls in the measured 43–55 s gap and
    gives the same picks.
- **N2. Firmware-computed TV* keys.** They clamp, slew-limit, hold and step, or read above
  the heat source. Today they count if they pass every rule. Two of them (TV1m, TVm0) fall to
  P2 and one (TVH3) to V7.
  - TVFm would have won S_slow without V6.
  - In a settled R0, TVS0/1/2 (smooth, σ 0.012) may compete for S_slow.
  - My default: allowed if they pass. The owner may prefer to exclude keys that show any
    hold-then-step or clamp, as not measurements.

## 9. Verify in the next R0 run

1. SMC step first: log the trailing-120 s slopes from idle start and the time the settle
   rule is met. This gives the real cost.
2. `Tg*` still removed by both P1 and P2. The picks have 0 floor or sentinel hits in every
   phase.
3. Picks recur within the clusters: S_fast ∈ {Tf1x/Tf2x}; S_slow ∈ {TSXR, TSVR, TR1d, TCHP,
   TSWR, TS0P, TPMP}. If the settled baseline makes TVS*/TD* valid and one of them wins,
   inspect its raw trace before accepting it (N2).
4. V6 should remove nothing once the settle rule holds. If it still removes keys, the cap
   is too short.
5. Replay the G1 gate on the recovery leg with the new picks. Record fan-off time, excess at
   fan-off, and release time against the 300 s cap ceiling. This capture gives 279 s after a
   900 s full load.
6. The receipt passes on per-phase classifier coverage, with max interval ≤ 2 s.
7. For R1 and the window (not this brief's rules, but measured here): after a 900 s full load,
   no physical key reaches G0's 0.2 °C/min slope bar until about 840–1,040 s after load end.
   That is longer than G0's 600 s cap. R1 should measure the G0 wait in the real member cycle
   (model load + 300 s idle + warmup) before W1. Otherwise G0 timeouts may exceed U1(d).

## Files

All in `/Users/edr/night-archive/r0-smc-cov/fresh/opus/`:
- `rank_v5.py`: the patched rank.
- `run_v5.py`: the replay.
- `extract.py`, `feat.py`, `show.py`, `look.py`, `ts.py`, `fans.py`, `tailfit.py`,
  `slopes.py`, `survey.py`, `survey2.py`, `sentinel.py`, `sentinel2.py`, `tback.py`
  (output `tback.txt`), `settle.py`, `settle2.py`, `virt.py`, `runs.py`, `gate_replay.py`,
  `sens.py`, `replay_current.py`: the analyses.
- The current rank reproduced on this capture: s_fast Tg2I, s_slow TaRT; 16 die, 141
  heatsink, 246 record-only.
