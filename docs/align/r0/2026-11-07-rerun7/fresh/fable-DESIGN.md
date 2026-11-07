# Fresh design: choosing and qualifying ALIGN's thermal-control sensors on Mac15,9

Seat: Fable 5.1, blind, 2026-11-07. Scratch: `/Users/edr/night-archive/r0-smc-cov/fresh/fable/`.
Read: the brief; worktree `/Users/edr/code/jw-wt/r0-smc-cov` (tip 3c0b71b24); FINAL-DESIGN §1.0 (V8), §2.2,
§2.4, §2.6, §2.8 and Amendment 1 on `origin/lane/2026-11-05-align-window-council`; `docs/align/r0_step_test_ruling.md`,
`smc_temperature.md`, `thermal_gates.md`, `r0_desk_runbook.md`; the real capture
`/Users/edr/night-align/r0-v4-20261107T0810Z/smc/{r0.json,samples.jsonl}` (1,800 rows, 403 keys).
Every number below was computed by scripts in the scratch directory (`load_capture.py`, `sweep1.py`, `sweep2.py`,
`sweep3.py`, `slopes.py`, the patched classifier `smc_enumeration_fable.py`, replay logs `replay_patched*.txt`).
Nothing outside the scratch directory was written.

## 0. Bottom line

1. **What the gate needs** (from `thermal_gates.py` and §2.6): two keys that read a real component temperature
   every second *while the GPU is idle* (that is when G0/G1/H evaluate), rise by at least 3 °C under a full step,
   are quiet enough that the 1 °C band and the 0.2 °C/min slope test mean something, respond monotonically to
   heat on the die-to-chassis path, and can re-enter a 1 °C band within the 300 s turn cap. One should carry the
   die's state (fast), the other the stored heat beyond the die (slow). Those seven properties, not "t63 ≤ 5 s"
   and "30 s < τ ≤ 300 s", are the rule.
2. **Tg\* keys are not usable gate sensors.** They read a bit-identical sub-zero value (0.000, −0.500, −2.750,
   −8.750, −9.000) on 95 % of idle samples and 97 % of recovery samples, and real temperatures only while the GPU
   is active. The current "die" class is exactly these 32 keys (16 pass the ΔT bar). At a gate the GPU is idle,
   so `S_fast ≤ R_fast + δ` is satisfied by the placeholder and the fast band controls nothing. Two observable
   rules remove them and 46 other non-temperatures (§2).
3. **The idle baseline was not settled.** The 300 s idle followed a 12-minute 30B model load; at its end the
   die-path keys were still cooling at −0.5 to −0.9 °C/min, 3-4× G0's own 0.2 °C/min settle bar. The whole-idle
   median overstated the baseline by 1.1 °C (TCMb) to 2.2 °C (TCHP), inflated the "noise" floor 10-80× (TaRT's
   1.137 °C is a cooling trend; its settled noise is 0.042 °C), and shifted τ by 10-15 %. Fix: baseline and noise
   from the last 60 s of idle (the same window the live reference R uses), a per-key `baseline_unsettled` flag,
   the SMC step moved to the front of R0, and an adaptive idle extension (§3).
4. **Classes by cooling τ, picks by what the gate needs.** fast: τ ≤ 60 s, pick the largest ΔT; slow:
   60 s < τ ≤ 300 s, pick the longest band hold time τ·ln(ΔT/δ) that is still ≤ 300 s. Replayed through the real
   `rank` path on this capture: **fast 93, slow 28, record-only 282; s_fast = Tf18 (ΔT 45.7 °C, τ 24.7 s,
   noise 0.062 °C), s_slow = TaLP (ΔT 20.5 °C, τ 86 s, noise 0.020 °C)**. The picks do not move for any class
   boundary between 30 and 75 s or any noise bar between 0.1 and 0.5 °C (§4). Both picks carry the
   `baseline_unsettled` flag from this capture, so they are proposals for R1, not qualified sensors.
5. **The receipt** re-checks the picks against a capture-wide coverage block built with a 100 ms grid
   tolerance on a single grid. The sampler re-anchors its grid at every phase start and after every late read,
   so 98 % of sample midpoints are more than 100 ms off any fixed grid and the stored block reports 0.02 for
   every key. It should read the classifier's own per-phase coverage (1 s cells), the read-error fraction, the
   valid-sample total and the maximum interval between consecutive valid readings (§5).

Three choices change which sensors count and are marked NEEDS_RULING in §7. Everything else I decided and listed.

## 1. What s_fast and s_slow have to do at window time

From `joulewise/align/apple/thermal_gates.py` (`ThermalSession.wait`, `slow_slope`, `_window_coverage`,
`capture_reference`), `thermal.py` (`Sidecar`, `Coverage`), `thermal_desk.py` (`member_record`, `acceptance`),
and FINAL-DESIGN §2.4 and §2.6:

| Use | Code / text | What it demands of the key |
|---|---|---|
| Sidecar reads `(s_fast, s_slow, *fan_keys)` at 1 Hz from adapter `prepare` to teardown | `thermal.Sidecar.tick`, `Coverage` | Readable every second without root; `valid_value` is only −40..150 °C, so plausibility is the classifier's job |
| Reference R = medians over the 60 s before warmup entry of the first sidecar member | `capture_reference` (`'anchor': 'warmup_entry', 'window_s': 60`) | A real value at idle; R0's baseline should be built the same way (last 60 s of idle) |
| δ_k = max(1.0 °C, 3·SD_k), SD_k over R1's 30-min idle soak | §2.6 "Bands" | If SD_k > 0.33 °C the key widens its own band; a 1 °C band is the registered floor |
| G0 releases on 10 consecutive samples with S_fast ≤ R_fast + δ_fast, S_slow ≤ R_slow + δ_slow, |OLS slope of S_slow over 60 s| ≤ 0.2 °C/min, OS level 0, PM Nominal; cap 600 s → `thermal.start_gate_timeout`, X2 | `wait`, lines 426-460 | The gate evaluates **while the GPU idles** (between warmup and episode). A key that reads a placeholder when the GPU is idle passes the band trivially. The slope test needs SE(slope) well under 0.2 °C/min |
| G1/H release on 5 consecutive samples within δ of that episode's G0 release values; cap `turn_cap_s` ≤ 300 (`validate_gate_policy`), timeout stops the episode (X2) | `wait`, `validate_gate_policy` | After a turn the key must come back within δ of its start value inside 300 s, or every turn times out |
| Unobserved: window coverage < 0.9 → X4 | `_window_coverage` | ≥ 90 % of seconds with a valid reading; gaps ≤ 2 s (U1(c)) |
| U2: range of G0-release S_slow across a model's members ≤ 3.0 °C | §2.4 | S_slow must resolve state at the 1 °C scale: ΔT under a full step well above 3 °C, else the 3 °C range is the whole dynamic range and U2 is vacuous |
| U5 heavy: β_T (J/°C) × observed G0-release range | §2.4 | Precision ∝ ΔT_key / noise_key |

So the requirements, each with where it comes from:

- **R1 continuous.** Every valid reading is a component temperature whether or not the GPU is active (G0/G1/H
  evaluate with the GPU idle).
- **R2 resolving.** ΔT under the R0 step ≥ 3.0 °C = 3 × δ_min (δ_k ≥ 1.0 °C; U2's 3 °C range). Same bar for
  both classes.
- **R3 quiet.** Settled idle noise σ ≤ 0.22 °C. Derivation: the slope test is OLS over 60 samples at 1 Hz;
  Σ(t−t̄)² = 60·(60²−1)/12 = 17,995 s², so SE(slope) = 60·σ/√17,995 = 0.447·σ °C/min. Requiring SE ≤ 0.1 °C/min
  (half the 0.2 bar, so a true slope of 0.4 is rejected at 2 SE) gives σ ≤ 0.224 °C. This also keeps
  3σ ≤ 0.67 < 1.0 °C, so δ_k stays at its registered floor.
- **R4 monotone.** The early response (50-60 s rise) is positive and above 3× the noise floor. A key that dips
  when the fans spin up (the TD\* keys, −0.8 to −1.2 °C at 50-60 s, then +4 to +13 °C) reads airflow, not stored
  heat; its band would open and close with fan state.
- **R5 releasable.** t_band = τ·ln(ΔT/δ_min) ≤ 300 s: the time a first-order sensor needs after a full step to
  re-enter a 1 °C band must fit the turn cap (`turn_cap_s ≤ 300`). ΔT here is the R0 matmul step, an upper bound
  on a planning turn, so this is conservative.
- **R6 two time scales.** fast: τ ≤ 60 s (one slope window: after 60 s such a key has shed ≥ 63 % of its own
  transient, so a 60 s slope on it would read the shared chassis drift, which is why §2.6 puts the slope test on
  S_slow only). slow: 60 s < τ ≤ 300 s (300 s = the turn cap; the G0 cap 600 s = 2τ gives 86 % recovery).
  τ is the cooling time constant from the recovery phase (first 1/e crossing relative to the first recovery
  reading, as the code does now); heating t63 stays as a recorded diagnostic.

## 2. Rejecting placeholders: observable rules and their replay

Signatures in this capture (`sweep1.py`, `sweep2.py`; 375 degC keys, 28 F\* keys):

- Tg2I idle: `[(0.1, -2.75), (1.2, -2.75), (2.2, -2.75), (3.1, 53.41), (4.3, 53.38), (5.3, -2.75), ...]`; 14 of
  300 idle samples are real temperatures (the GPU finishing the 30B unload); load first samples
  `(0.0, -2.75), (1.1, 48.43), (2.1, 53.31), ...`; recovery `(0.0, 85.49), (1.0, 85.50), (2.1, -2.75), ...`.
  All 32 Tg\* keys: idle mode fraction 0.95, recovery mode fraction 0.97, two parked samples inside the 900 s
  load. TCMb reads exactly Tg2I's value under load (53.307, 56.068, ..., 85.477) and 79.68 two seconds into
  recovery when Tg2I parks: TCMb is a max-of-die composite and stays continuous.
- TV1m/TVm0 clamp at exactly 40.000 on 63 % of idle samples (112 distinct values otherwise); TVh0 at 35.000 on 57 %.
- TVH3 = 1.72 × TCMb − 38 (R² 0.98) and reaches 137.0 °C under load; TV2S/TVM2/TVH2 read −37 to −10 °C;
  Tf00/Tf10/Tf20/Tf30/Tf40 read −0.2..0.2 °C. None is a component temperature.

Rules (all on the idle series unless stated), with derivations:

- **P1 constant.** Fewer than 3 distinct idle values → record-only. (Existing rule; kept.)
- **P2 parked / clamped.** With ≥ 10 distinct idle values, one exact value holds ≥ 40 % of idle samples →
  record-only. Derivation: a continuous reading with quantum q and noise σ ≥ q puts at most q/(σ√2π) ≈ 0.40 of
  its samples on any one quantum; a series with ≥ 10 distinct values has q ≪ σ, so one value holding 40 % is a
  parked or clamped output, not noise. Coarse-quantum keys with < 10 distinct values (TB1T: 5 values, 0.40 at
  29.6) are exempt and fall to R2 on ΔT.
- **P3 envelope.** Any valid reading over the whole capture outside [10, 125] °C → record-only. 10 °C is
  Apple's operating-ambient floor for this product class (no passive component on a running laptop is colder
  than the room; the coolest varying key here reads 26.7 °C, Ts1P); 125 °C is the standard absolute-maximum
  junction rating for silicon (the composite max-die key TCMb peaked at 85.5 °C; the hottest plausible key,
  TCMz, at 112 °C).

Replay over all 403 keys (`replay_patched_v2.txt`, removal ledger; the rules run in this order after the unit
and coverage checks):

| Rule | Removes | Keys |
|---|---|---|
| unit ≠ degC | 28 | all F\* |
| P1 constant | 95 | TG0C, TG0H, TH1a/b, TR0Z, TVMD, Ta08..Ta0P (8), Tf01/02/05/06/0C..., Tp1g..Tp3j (49), Tz11..Tz1j (9) |
| P2 parked | 35 | the 32 Tg\* keys; TV1m, TVm0, TVh0 |
| P3 envelope | 14 | TV2S, TV3S, TVH2, TVH3 (46..137 °C), TVHO, TVM2, TVM3, TVMO, TVSO, Tf00, Tf10, Tf20, Tf30, Tf40 |

P2 alone removes every current "die" candidate; P3 removes TVH3, which the current classifier lists first among
its 141 "heatsink" candidates (τ 32 s, ΔT 62 °C). Tg2I should still be **recorded** by the sidecar as a diagnostic
("GPU die while active"), but never gated.

## 3. Idle baseline: settle criterion, this capture's cooling curves, cost

**Criterion.** A key's baseline is valid when the OLS slope of its last 60 s of idle satisfies
|slope| ≤ 0.2 °C/min + 2·SE, SE = 0.447·σ_resid (σ_resid = SD about that line). Derivation: 0.2 °C/min is the
bar G0 applies to S_slow before an episode may start (§2.6), so R0's baseline is held to the window's own
definition of "settled"; the 2·SE term makes the test self-scaling so a quiet key is judged sharply
(TaLP: SE 0.009) and a noisy key is not failed by its own noise. A residual slope of 0.2 °C/min biases a 60 s
median by ≤ 0.1 °C, a tenth of δ_min.

**Baseline and noise.** Baseline = median of the last 60 s of idle (identical in form to the live reference R);
noise = SD of residuals about the OLS line over that window (a cooling trend no longer counts as noise).

**This capture** (`slopes.py`, `sweep3.py`):

```
TCMb idle     60 s-window slopes degC/min:  -8.33  -2.98  -1.36  -0.28  -0.63
TCMb recovery 60 s-window slopes degC/min: -21.43  -4.24  -1.54  -0.73  -0.85  -0.57  -0.47  -0.71  -0.30  -0.40
Tf2B idle     ...  -9.61  -3.23  -1.23  -0.71  -0.76      recovery ... -0.53  -0.51  -0.34
TCHP idle     ... -11.03  -4.31  -2.05  -0.92  -0.55      recovery ... -0.45  -0.35  -0.30
TaLT idle     ...  -1.46  -1.15  -0.52   0.12  -0.21      recovery ... -0.36  -0.33  -0.33
```

- At the end of the 300 s idle, 198 of 235 continuous plausible keys fail the criterion; of the 121 keys my
  classifier finds eligible, 114 are unsettled. Only the skin keys TaRT/TaLT/TaLW/TaRW (slopes −0.13 to −0.21)
  and a few noisy Tp\* keys pass.
- Whole-idle median minus last-60 s median: TCMb +1.10 °C, TCHP +2.18 °C, TaRT +0.28 °C. Noise floor, whole-idle
  pstdev vs settled residual: TaRT 1.137 vs 0.042; TCMb 3.243 vs 0.084; TCHP 4.817 vs 0.040. τ with the two
  baselines: TCMb 26.8 → 28.9 s, TCHP 66.1 → 77.2 s, TaLP 75.1 → 86.2 s, TaRT 123.1 → 129.0 s (10-15 %).
- Fitting |slope| = s₀·e^(−t/τ_c) over the recovery windows after 120 s gives a slope-decay τ_c of 345 s (TCMb),
  347 s (Tf2B), 461 s (TRD0), 215 s (TCHP); the skin keys sit at −0.33 °C/min with no visible decay over
  600 s (chassis cooling, τ ≫ 600 s). Extrapolated time to reach 0.2 °C/min: after the 12-min model load,
  450 s (TCMb), 595 s (Tf2B), 685 s (TRD0), 363 s (TCHP) from idle start; after the 900 s matmul, 813, 754,
  861, 655 s from recovery start.
- Even at the end of the 600 s recovery every die-path key sits 1.7-2.0 °C **below** its idle baseline: the idle
  baseline itself was that far above the machine's settled state.

**Proposal and cost.**

1. Move the SMC step to the front of R0, before `load` (the runbook order is
   `host,disk,load,template,generated,memory,smc,ladder,long-decode`; `smc` directly follows the 30B memory
   check). Cost: 0 s; the machine is otherwise idle before R0 begins.
2. Adaptive idle: minimum 300 s, then extend until the criterion holds for every key that is continuous and
   plausible so far (P1-P3 on the idle data) and has σ_resid ≤ 0.22 °C, for 60 consecutive seconds; cap 1,200 s.
   Cap derivation: from the measured slope-decay τ_c ≈ 345 s and 0.4 °C/min at 570 s of recovery, 0.2 °C/min is
   reached at ~810 s; a start three times hotter adds 345·ln 3 ≈ 380 s, so 1,200 s covers a step as heavy as the
   900 s matmul. Cost: 0 s extra when SMC runs first after ≥ 15 min of machine idle; +150 to +400 s after a
   12-minute model load (from the extrapolations above); +900 s worst case. At the cap the capture proceeds and
   every key carries `baseline_unsettled` with its slope; the receipt prints the flag count. Per the doctrine
   ("physics refuses; everything else is a flag") an unsettled baseline flags, it does not refuse.
3. Keep load 900 s (≥ 8τ for every slow candidate; TaLP peaks at 300 s and is flat after) and recovery 600 s
   (the 1/e crossing of a τ ≤ 300 s key falls inside it with 2× margin).

## 4. Classes and picks, replayed through `rank`

**Rule text the code could implement** (patched copy: `smc_enumeration_fable.py`, `RULE_FABLE`, `rank`,
`select_keys`; all phases ≥ 99 % coverage at one reading per 1 s cell and < 1 % read errors, unchanged):

```
unit == degC; P1 constant; P2 parked (>=10 distinct, one value >= 40%); P3 envelope [10, 125] degC.
baseline = median(last 60 s of idle); noise = SD about the OLS line over that window;
settled = |slope| <= 0.2 + 2*0.447*noise degC/min (flag, not refusal).
floor = max(0.05, quantum, noise). rise = median(last 10% of load) - baseline; rise60 = median(50-60 s) - baseline.
tau = first crossing of baseline + (first recovery value - baseline)/e, minus the first recovery stamp.
selectable: rise >= 3.0; noise <= 0.22; rise60 > 3*floor; tau resolved; t_band = tau*ln(rise/1.0) <= 300.
class: fast if tau <= 60; slow if 60 < tau <= 300; else record-only (chassis).
s_fast = fast key with the largest rise; s_slow = slow key with the largest t_band. Lexical ties.
```

Every constant's derivation is in §1-§3: 3.0 °C = 3·δ_min; 0.22 °C from SE(slope) ≤ 0.1 °C/min; 60 s = one
slope window; 300 s = `turn_cap_s` ceiling; 1.0 °C = δ_min; 0.2 °C/min = G0's bar; 10/125 °C and 40 % in §2.

**Replay** (`replay_patched_v2.txt`; `thermal` imported from the worktree, checked by `__file__`):

```
CURRENT rank:  die 16  heatsink 141  record-only 246  picks Tg2I TaRT  status pass
PATCHED  rank: fast 93  slow 28      record-only 282  picks Tf18 TaLP  status pass  (114 of 121 eligible flagged baseline_unsettled)
```

Removal ledger for the 403 keys: 28 non-degC, 95 constant, 35 parked, 14 envelope, 67 noise > 0.22 °C,
22 rise < 3 °C, 16 non-monotone (all TD\*: 50-60 s rise −0.75 to −1.19 °C, then +3 to +13 °C), 5 band re-entry
> 300 s (TVFm 406 s, TVS2 365, TVS1 349, TVS0 329, TVFh 328), 93 fast, 28 slow. Sum 403.

Fast class, top of the ranking (rise, τ, t63, noise, baseline slope):

```
Tf18  45.68  24.7  18.9  0.062  -0.64   <- s_fast
Tf2B  45.63  24.4  18.3  0.070  -0.76
Tf1B  45.36  25.4  19.2  0.067  -0.69
Tf24=Tf2D=Tf2E 45.27 24.6 18.5 0.043 (byte-identical series)
TCDX  43.04  25.9  20.3  0.111  -0.60
TCMb  36.15  28.9  25.2  0.084  -0.63   (max-of-die composite; equals Tg under load)
```

Slow class by t_band (rise, rise60, τ, noise, t_band):

```
TaLP  20.54  11.33   86.2  0.020  261   <- s_slow
TMVR  17.07   7.06   90.5  0.041  257
TCHP  24.82  12.77   77.2  0.040  248
TaRF  22.37  13.28   79.5  0.021  247
TPD2  23.92  13.25   77.4  0.220  246
...
TfA0  30.42  19.85   63.0  0.201  215   (largest rise in class; τ on the boundary, noise at the bar)
TaRT   4.37   0.34  129.0  0.042  190   (longest τ in class; 1/5 of TaLP's resolution)
TaLT   3.93   0.74  116.4  0.041  159
```

Sensitivity (same file): the fast/slow boundary at 30, 45, 60 or 75 s gives Tf18/TaLP under the recommended
rule; at 90 s TMVR, at 120 s TaRT (only one slow key left). The noise bar at 0.1, 0.15, 0.22, 0.33 or 0.5 °C
gives Tf18/TaLP. The alternative slow-pick criteria are boundary-sensitive: largest rise gives TVV0 (30 s),
TfA0 (45, 60 s), TCHP (75 s), TMVR (90 s); longest τ gives TaRT throughout.

Why t_band rather than longest τ for the slow pick: at a G1 gate the question is "has the stored heat gone",
and the time a key keeps the gate closed after a step is τ·ln(ΔT/δ), not τ. TaRT (τ 129 s, ΔT 4.4 °C) re-enters
the 1 °C band 71 s *before* TaLP (τ 86 s, ΔT 20.5 °C) does, and its 4.4 °C full-step range makes U2's 3 °C
criterion nearly vacuous and U5's β_T fit five times less precise (ΔT/noise 104 vs 1,027). The 300 s cap keeps the
pick releasable. The fast pick stays largest ΔT (§2.6 text): the die key's job is resolution, and all fast keys
re-enter the band in 93-192 s.

What the new rules do to the current classifier's candidates (set comparison against `current_rank.pkl`): all
16 Tg\* "die" keys are removed by P2. Of the 141 "heatsink" keys, 68 become fast (their τ against a last-60 s
baseline is ≤ 60 s), 28 stay selectable as slow, 41 are removed by the settled-noise bar (Tp\*, TPD\*, TRD\*
with σ 0.22-7.7 °C), TVh0 by P2, TVH3 by P3, and TVS1/TVS2 by R5. The 16 TD\* keys removed by R4 and the 25 keys
that join the fast class from record-only (TCMb, TCDX, Tf18, Tf2B and their siblings) were record-only before.
The current classifier's "die" boundary t63 ≤ 5 s has no continuous member on this Mac: the fastest
continuous keys have t63 18-20 s and τ 24-26 s, because the SoC package, not the junction, sets the response
to a sustained matmul.

## 5. The receipt

`r0_host.smc_enumeration` (lines 484-491) requires, for each pick, `payload["coverage"]["per_key"][key]` with
`expected_samples ≥ 600` and `valid/expected > 0.99`. That block is built by the capture script with
`thermal.Coverage`'s default 100 ms tolerance on one grid anchored at the first sample of the whole capture.
Measured on this capture with the worktree's `Coverage` class:

```
tolerance 100 ms: all_keys expected=1800 valid=36   frac=0.020  (every key)
tolerance 250 ms: all_keys expected=1800 valid=300  frac=0.167
tolerance 500 ms: all_keys expected=1801 valid=1631 frac=0.906
abs offset of sample midpoints from a fixed grid: median 399 ms, p90 484 ms; fraction > 100 ms = 0.980
actual max interval between consecutive valid readings (all five test keys): 1,271 ms; read bracket median 86 ms, p95 139 ms
```

The sampler (`collect`) starts a new grid at each phase origin (phase starts at +0.117, +0.443, +0.614 s from the
capture origin) and re-anchors `due` after any late read, so no single capture-wide grid exists; the 100 ms
tolerance then fails 98 % of readings, and even a 500 ms tolerance on one grid loses 9 %. The per-phase coverage
inside `rank` (fixed in 3c0b71b24 to one reading per 1 s cell, grid per phase) reports 1.000 in every phase for
every pick. The receipt therefore refuses picks the classifier has already shown readable.

Read instead, for each of the two picks, from `classification["ranking"]`:

1. `phase_coverage[p] ≥ 0.99` for idle, load and recovery (1 s cells, per-phase grid; already required for
   eligibility, so the receipt asserts the invariant);
2. `phase_read_error_fraction[p] < 0.01`;
3. valid readings summed over the three phases ≥ 600 (the "10 min" of §2.6; here 1,800);
4. the maximum interval between consecutive valid stamps of the key ≤ 2 s (U1(c)'s window bar, and what the
   gate's `_window_coverage` can tolerate; here 1.271 s). Compute it from the samples, as
   `Coverage.report` does for `max_interval_ns`;
5. the `baseline_unsettled` flag and slope for each pick, printed, not refused.

Drop the `payload["coverage"]` re-check, or recompute it per phase with `tolerance_ns = NS // 2`. Keep
`period_ns == 1_000_000_000`, the SHA-256 check and the distinct-keys check.

## 6. What to verify in the next R0 run

1. SMC runs first; the idle extension used is printed; `baseline_unsettled` is false for both picks and for
   ≥ the top five of each class. If the cap (1,200 s) is reached, print the residual slopes.
2. With a settled baseline, τ of Tf18 and TaLP move by < 10 % from 24.7 s and 86 s (the bias measured in §3);
   rise of TaLP rises from 20.5 °C toward its true value (the baseline was ~1.5 °C high).
3. The picks reproduce or flip only within the measured spread: Tf18/Tf2B/Tf1B/Tf24 differ by 0.4 °C in rise;
   TaLP/TMVR/TCHP/TaRF differ by 14 s in t_band. A flip inside those spreads is expected; R1's planning-turn step
   makes the final pick.
4. Tg2I (recorded, not gated) parks at exactly −2.750 within two samples of GPU idle; TCMb equals the Tg maximum
   under load and stays continuous. This confirms the placeholder reading and the composite.
5. P2/P3 remove the same 49 keys; TD\* keys fail R4 again (airflow dip); TVFm/TVS\* fail R5.
6. The receipt passes on the classifier's per-phase fields; the capture-wide block, if still emitted, is
   diagnostic.
7. In R1: under the real planning turn, Tf18 re-enters the 1 °C band in about 25·ln(ΔT_turn) s and TaLP in about
   86·ln(ΔT_turn) s; both must be ≤ G_turn. Record the 30-min soak SD of both (expected 0.06 and 0.02 °C, so
   δ = 1.0 °C for both).

## 7. Decisions and rulings

**NEEDS_RULING (changes which sensors count):**

1. Tg\* keys are non-selectable (P2). This removes the current s_fast (Tg2I) and the only class with
   t63 ≤ 5 s; s_fast becomes a continuous die-path key (Tf18, t63 19 s). The §2.6 "die class" as written has no
   member on this Mac.
2. Fast class by cooling τ ≤ 60 s instead of heating t63 ≤ 5 s; slow class 60 < τ ≤ 300 s instead of
   30 < τ ≤ 300 s with t63 > 5 s.
3. Slow pick by largest τ·ln(ΔT/δ) ≤ 300 s instead of §2.6's longest τ: TaLP instead of TaRT. §4 gives the
   numbers for both and for largest-ΔT (TfA0).

**Decisions I made (the governing texts determine them):**

- Baseline = median of the last 60 s of idle, matching `capture_reference`'s 60 s window; noise = detrended SD
  over that window; an unsettled baseline is a flag with its slope, never a refusal.
- Rise bar 3.0 °C for both classes (3·δ_min); noise bar 0.22 °C for both (slope SE); monotone early response
  (existing `rise60 > 3·floor`) extended to both classes; band re-entry ≤ 300 s from `turn_cap_s`.
- P1-P3 as written; P2 and P3 are new; the unit check precedes them so F\* keys are "not a temperature unit".
- The SMC step moves before `load` in R0; adaptive idle 300-1,200 s; load 900 s and recovery 600 s unchanged.
- t63 (50-60 s) is kept as a recorded diagnostic and for R4; it no longer classifies.
- Tg2I and the fan keys F0Ac/F1Ac are recorded by the sidecar as diagnostics.
- The receipt reads the classifier's per-phase coverage, read errors, valid-sample total and maximum interval;
  the capture-wide 100 ms block is dropped or made per-phase at NS // 2.
- Both picks from this capture are PROVISIONAL: 114 of 121 eligible keys carry `baseline_unsettled`.

**Kept from the current classifier, and why:** per-phase ≥ 99 % coverage at one reading per 1 s cell and
< 1 % read errors (3c0b71b24's derivation stands); the constant-series rule; model-free crossings with no
exponential fit; the 300 s ceiling on τ; the 900/600 s load and recovery; the two-key structure (a die-path key
and a stored-heat key answer different questions at the gate: Tf18 is back in band ~95 s after a full step,
TaLP ~260 s; the slow key is what holds the gate while the heatsink sheds heat).

## Appendix: commands

```
# all run from /Users/edr/night-archive/r0-smc-cov/fresh/fable with
PY=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python
$PY -B -P -I load_capture.py          # capture.pkl; read bracket/interval stats; 0 read errors
$PY -B -P -I sweep1.py                # per-key placeholder signatures (sweep1.json)
$PY -B -P -I sweep2.py                # mode-fraction and envelope distributions
$PY -B -P -I sweep3.py                # response table, detrended noise, settle times (sweep3.json)
$PY -B -P -I slopes.py                # 60 s-window slopes through idle and recovery, slope-decay tau
PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov $PY -B -P -c '...'   # current rank (current_rank.pkl); Coverage tolerance test
PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov $PY -B -P - < replay  # patched rank, sensitivities (replay_patched_v2.txt)
```
