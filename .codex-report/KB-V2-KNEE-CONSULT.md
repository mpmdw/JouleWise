# KB-V2 knee consult

2026-10-28. Design consult; the lead retains admission and implementation authority.
Base: `a7a20c19751730f49dae445d44d9ac363ee41e08`, draft PR #593.
Delivery branch: `codex/2026-10-28-kb-v2-knee-consult`, cut directly from that base.
Only this report and `.codex-report/kb-knee-consult/` were written in the repository.
Production code, registration, measurements and lead bookkeeping are unchanged.

## Recommendation

Use exact reciprocal intervals; choose the cache reference by its largest exact lower endpoint;
require resolved timing evidence across the two actual cache-arm increments C1→C3 and C3→C2.
Keep K after the last above-threshold pair, including isolated late pairs: do not discard inconvenient
late evidence to recover a smaller K. Bound each dispatch's clock contribution by
`q_j = 2 (max(clock_getres, measured tick) + 1 ns) / N_j`.

This removes the artificial nonpositive symmetric-endpoint refusal without weakening the
positive-duration prerequisite. It also connects the evidence to the arms that will consume the hour.
The number of required arm increments is derived from the existing three cache arms, not fitted
to the simulated false-positive rate. The recommendation was specified before the completed sweep;
no noise multiplier, percentage tolerance, confidence cutoff or retry count was fitted.

In 2,000 trials per noise/world cell, this rule refused 0, 0, 0, 7 and 26 true-knee scans
at 0, 0.05, 0.2, 0.5 and 1% noise, respectively. It accepted no DRAM-only scans in these cells.
Every accepted true-knee scan returned 64 MiB. These are synthetic observations, not coverage guarantees.

## Reproduction and experimental design

The five requested reviewer scripts were fetched from JouleWise-data commit
`3b92244b4c41d2a5cc56dc999340aa65d81a091b`, branch `claude/kb-v2-delta-opus`.
Verbatim copies are under `kb-knee-consult/reviewer/`; their complete stdout is
`kb-knee-consult/reviewer-replays.txt`. They import the real pinned `scripts.bytes_stream_test.knee_scan`.

- **F1 reproduced exactly.** `knee_noise_diag.py`: 123/400 refusals (30.75%, printed 0.307).
  The first failing reference is the 256 KiB pair: m_C = 1279.2 GB/s, δm_C = 4833.4 GB/s,
  D = 102.5 ns, δD = 81.0 ns. The top DRAM pair remains resolved.
  `scan_cases.py` gives refusal fractions 25.00%, 28.75%, 27.50%, 30.25% at its four noise levels.
- **F2 reproduced exactly.** `tick_quant.py`: 72/200 noiseless DRAM-only scans accept a false knee (36%).
  All 200 worked-example scans return 64 MiB. Its physical tick is now supported by the lead's
  2026-10-28 Mac measurement: timebase 125/3 ns, getres 42 ns, observed steps 41, 42, 83, 84, 125 ns.
  This consult did not remeasure the Mac.
- **F3 reproduced exactly.** `dram_noise.py`: 6/200, 7/200, 6/200 false knees
  at 0.05%, 0.2%, 1% noise. `knee_fix_check.py` reproduces its reference-selection improvement and
  its increased DRAM-only acceptance. Its original 200-trial cells are supplemented below.

`experiment.py` uses those scripts' `worked5` and `dram_only` models, the same 22 sizes
(16 KiB through 32 GiB), three calls per size, N = floor(2 / nominal dispatch time), and
independent Gaussian multiplicative **whole-call** duration noise. It does not model independent
noise on each dispatch: averaging thousands of dispatches would describe a different experiment.
The worked model uses 50 µs fixed dispatch cost, 1 TB/s cache, a 198.8 GB/s straddling pair,
and 331.6 GB/s DRAM, as in `scan_cases.py`.

Each call starts at an independently uniform phase of a 125/3 ns physical tick, at a random integer
tick epoch. Both physical endpoints are floored to ticks. The main sweep converts those tick values
to integer ns by truncation; a second sweep converts them to nearest integer ns. Large epochs use
integer arithmetic, so subtraction does not invent cancellation at ~10¹² ns. The Gaussian noise
and phase draws are identical across candidates within a trial. Seeds are
`20261028 + 10 * noise_level_index + world_index`; indices and all outcomes are in the JSON files.
Every candidate has 2,000 trials in every requested cell, under each conversion: 120,000 scan
executions per sweep, 240,000 total. The current rule is the actual function; the F1/F2 variants
are checked single-anchor edits to its source compiled in memory. The own candidate reuses the
real grouping, spread and D calculation, then replaces the reference/threshold/acceptance logic.

## Candidates and measured rates

F1 selects the largest **symmetric** lower endpoint m−δm. F2 adds the reviewer's conservative
`2 * clock_getres / N` term: 84 ns/N on this Mac. Under this experiment's common tick quantizer,
the sharper duration bound is tick + 1 ns = 42⅔ ns, which is below 84 ns, so F2 is conservative
here even with integer conversion. The recommendation uses the more generally explicit
86 ns/N derivation below. The difference is from endpoint accounting, not a noise fit.

“Adjacent anywhere” requires at least one adjacent above-threshold pair of pairs anywhere in the
scan, retaining the original K calculation. “Adjacent at frontier” additionally requires that
the last above-threshold pair's predecessor be above; this prevents a low-size run from
licensing an isolated late pair. The recommendation instead checks the actual proposed cache arms.

Each entry is **true-knee refusal % / DRAM-only false-knee %**; denominator 2,000 for each rate.
A 0.05 percentage-point step is one trial. Raw integer counts and refusal reasons are in
`results-floor.json`.

| Rule | 0% | 0.05% | 0.2% | 0.5% | 1% |
|---|---:|---:|---:|---:|---:|
| Current | 0.00 / 33.10 | 29.85 / 4.10 | 30.55 / 3.80 | 29.45 / 2.75 | 32.50 / 1.75 |
| F1 | 0.00 / 55.80 | 0.00 / 13.10 | 0.00 / 7.55 | 0.25 / 6.10 | 1.25 / 3.30 |
| F1 + F2 | 0.00 / 0.00 | 0.00 / 13.05 | 0.00 / 7.55 | 0.25 / 6.10 | 1.25 / 3.30 |
| F1 + F2 + adjacent anywhere | 0.00 / 0.00 | 0.00 / 0.10 | 0.00 / 0.05 | 0.25 / 0.05 | 1.25 / 0.00 |
| F1 + F2 + adjacent at frontier | 0.00 / 0.00 | 0.00 / 0.10 | 0.00 / 0.05 | 0.35 / 0.05 | 1.35 / 0.00 |
| Exact intervals + cache-arm evidence (recommended) | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.35 / 0.00 | 1.30 / 0.00 |

The second conversion sweep (`results-nearest.json`) has identical rates in every nonzero-noise
cell and every corrected noiseless cell. Only the uncorrected noiseless DRAM-only rates change:
current 33.40% (668/2000), F1 55.95% (1119/2000), versus 33.10% and 55.80% above.
Thus neither integer conversion convention saves the 1 ns assumption.

Refusal alone understates the loss of outcome. Among true-knee trials, F1, F1+F2 and
“adjacent anywhere” also accept **two wrong Ks** at 0.5% (both 512 MiB), and **two** at 1%
(256 and 512 MiB). Current accepts one wrong K at 1% (256 MiB). “Adjacent at frontier” and
the recommendation accept none. For the recommendation's 7 refusals at 0.5%, 5 have 64K>s_max
and 2 lack cache-arm evidence; at 1%, these counts are 24 and 2. Genuine late ambiguous evidence
can still consume the test's outcome; this rule does not suppress it.

For independent Bernoulli trials the sampling SE of a reported proportion is
sqrt[p(1−p)/2000], at most 1/(2 sqrt(2000)) = 1.12 percentage points. Candidate comparisons are
paired, so this is a descriptive single-rate SE, not a significance test between candidates.
Zero observed false knees does not establish a zero population rate. No confidence level or
acceptance threshold is inferred from these trials. The zero-false-knee advantage over the
adjacency variants is only a few trials here; the arm-location rationale, rather than statistical
proof of superiority from those few events, is the reason for preferring it.

## Derivations and limits

**Clock.** Integer nanoseconds specify an output unit, not a physical tick. For tick r_t and
integer conversion unit u = 1 ns, a truncated physical endpoint can be displaced by less than
r_t; subsequent truncation to integer ns adds less than u. Nearest-integer conversion adds at
most u/2 instead, but does not make the physical clock round to the nearest tick. The observed
41/42 ns increments do not identify the rounding convention. Use the conservative truncation/
unknown-conversion rule: r = max(reported clock_getres, measured tick), per-endpoint absolute
error at most r+u, hence duration error at most 2(r+u), hence q_j = 2(r+u)/N_j. On the supplied
Mac values r = 42 ns and q_j = 86 ns/N_j. The two is the number of stamped endpoints; the added
1 ns is the integer conversion unit. Neither is an empirical noise multiplier.

A single fixed floor quantizer has same-signed endpoint errors, allowing the tighter duration
bound r_t+u; an ideal round-to-nearest physical tick allows r_t before integer conversion.
Neither should be silently assumed from the return type. I recommend the conservative bound
because the given measurement establishes the tick but not all conversion internals. Record
getres, exact timebase numerator/denominator, clock identity and conversion convention/source in
every receipt; “unknown” conversion retains the conservative rule. The synthetic floor and
nearest mappings are both tested. Clock quantization is tiny compared with nonzero whole-call
noise, explaining why F2 fixes the zero-noise failure but barely moves the other columns.

**Reference.** With A>0 and D>δD, the exact interval of A/D is
[L,U] = [A/(D+δD), A/(D−δD)]. Both endpoints are positive. The old symmetric bar uses the larger
upward excursion on the downward side too. Its “lower endpoint” can therefore become negative
even though the actual reciprocal cannot. F1 avoids selecting the worst such rectangle;
exact endpoints remove that artificial geometry. Select the defined pair maximizing L,
with smaller size breaking an exact tie. Do not select a largest point estimate or globally
inflate uncertainty until selected small pairs stop winning.

**Threshold and comparison.** For H(x,y) = 1/[(63/64)/x + (1/64)/y], monotonicity gives
T_L=H(L_D,L_C), T_U=H(U_D,U_C). A pair is above precisely when L_pair>T_U. Equivalently,
with m=A/D and T=H(m_D,m_C), margin=m−T and bar=(m−L_pair)+(T_U−T), require margin>bar.
This is exact one-sided interval propagation; no symmetric lower-reference positivity test or
Taylor expansion is needed. Dependence from reusing the chosen pair makes a rectangular bound
conservative conditional on the input intervals; it does not require independent references.

**Which evidence.** Form K from all above pairs, then inspect the two existing arm increments:
(K/16→K/8) and (K/8→K/4). Both must be defined and above by the same comparison. Together with
the last above pair ending at K/2 (implied by K's definition), this requires three consecutive
above pairs near the proposed arms. “Three” is a consequence of the existing arm geometry and
K definition, not an additional tuned run length. A successful pair at unrelated sizes is not
adequate evidence for C1, C3 and C2. Undefined pairs and isolated late pairs are printed; no
filter silently erases them. If the arm evidence is missing, do not shrink K or retry the scan.

**Noise realism: unknown.** The pinned rule §5 labels the cache throughput and fixed dispatch
time as assumptions; `.codex-report/KB-V2.md` Round 3 labels its noise sweeps synthetic. The
reviewer scripts likewise synthesize them. No live three-call, ~2 s-per-call scan receipt series
establishing an M3 Max per-call duration distribution was found in the targeted repository
evidence. Model decode timings, power uncertainty and the new clock measurement do not establish
this probe's whole-call noise. I cannot label 0.05%, 0.2%, 0.5% or 1% realistic. Dispatch/scheduler
correlation, frequency changes and size-dependent fixed costs remain outside this IID Gaussian
model. The scan uses observed spread, not a confidence interval on future excursions; a smooth
size-dependent timing effect can imitate cache evidence. A false knee can spend the 3,573.6 s
hour and will often yield DC validity UNDETERMINED, but that outcome is not mathematically
guaranteed. Neither kind of scan error changes a collected BYTES value.

## Worked example and numerical agreement

Every candidate returns K=67,108,864 bytes (64 MiB) in all 2,000 noiseless true-knee trials
under each conversion. The own rule also passed 400 separately seeded noiseless phase trials
per conversion in `verify.py`. Thus B=4 GiB, C1=4 MiB, C3=8 MiB, C2=16 MiB, φ=1/64 remain.
The reviewer model rounds DRAM throughput to 331.6 GB/s, giving T≈335.0997 GB/s; the draft's
335.12 uses the slightly different H-derived throughput. This does not change K.

For the recorded floor-conversion worked example (seed 8), the 16→32 MiB pair has
m=1000.0000348308483 GB/s, interval [999.9996495246795,1000.0004201373141] GB/s.
T=335.09969869370707 GB/s, interval [335.09965410765943,335.0997432797666] GB/s.
The comparison margin is 664.9003361371414 GB/s and its one-sided bar is
0.00042989222833251953 GB/s. The threshold's larger endpoint excursion is
0.000044586059509277344 GB/s. H2 displays those uncertainties as 0.00043 and
0.000045 GB/s; the margin is overwhelmingly separated.

`verify.py` independently recomputes the mean/spread, reciprocal endpoints, reference,
threshold, margin and bar from the integer receipt fields with rational arithmetic.
For these printed comparison quantities the largest binary64 discrepancy is
2.8793189825782005e−13 GB/s. This is a direct measurement of float noise against exact rational
values, not an equality test on rounded decimals. The agreement bar is derived as 1% of the
smallest printed uncertainty: 0.01 × 0.000045 = 4.5e−7 GB/s, and
1e6 × float noise = 2.8793189825782006e−7 < 4.5e−7 GB/s. All checked discrepancies are inside
that bar. This arithmetic bar is for the specified worked comparison, not a universal
absolute tolerance for every ill-conditioned small-size reciprocal. Categorical K, class and
integer-count identities are checked as identities; no floating quantity is tested by exact
equality and no agreement epsilon enters scan acceptance.

## Exact text for the builder

The pinned file's §3 is **“The reported quantity and its bound”**, not a knee-scan section.
The complete replacement below preserves that section's energy arithmetic and inserts only
the knee conditionality paragraph. The scan itself is in §1. Because the clock and reciprocal
changes also touch steps 1–2, replace all six numbered scan steps with the following block;
steps 3–5 are included explicitly. These are proposals for the lead, not installed changes.

### §1: replacement numbered knee-scan steps 1–6

1. Per size s and call j, let d_j(s) = (end_ns − start_ns) / (10⁹ N_j), and let t(s) be the mean of
   the three d_j. Every receipt records CLOCK_MONOTONIC_RAW's reported `clock_getres` in seconds,
   the measured physical tick as an exact numerator/denominator in ns with its source,
   and the integer-nanosecond conversion convention/source (`truncation`, `nearest`, or `unknown`).
   An integer-nanosecond return type does not imply a 1 ns physical tick or rounding to the nearest tick.
   Let r be the larger of the reported resolution and measured tick, in seconds, and u = 10⁻⁹ s.
   Use q_j = 2(r + u)/N_j seconds per dispatch: each endpoint can be displaced by at most one physical
   tick plus one integer conversion unit, and a duration has two endpoints. This conservative truncation/
   unknown-conversion bound also covers nearest-integer conversion. On the recorded Mac values,
   r = max(42 ns,125/3 ns) = 42 ns, so q_j = 86 ns/N_j. Use
   δt(s) = max_j |d_j − t(s)| + mean_j q_j. The first term envelopes the observed three-call spread
   about its mean; the second bounds the mean's stamp error. This is an observed-spread bound,
   not a confidence claim about unobserved timing excursions. Print t, δt, clock metadata and all three calls.
2. Per adjacent pair (s/2,s), write D = t(s) − t(s/2), δD = δt(s) + δt(s/2), A = s − s/2.
   If D ≤ δD, the marginal throughput is `not defined (dispatch-time difference not separated from zero)`;
   this pair never counts as above threshold. Otherwise m(s) = A/D and its exact propagated interval is
   L(s) = A/(D + δD), U(s) = A/(D − δD). Derivation: A/D decreases with positive D, whose endpoints are
   D−δD and D+δD. Print m, L, U and their endpoint excursions, without replacing the asymmetric interval
   by a symmetric lower endpoint. The fixed dispatch time cancels; whole-call throughput does not cancel it.
3. The DRAM reference is the top pair's m_D with interval [L_D,U_D] (16→32 GiB if s_max=32 GiB).
   The cache reference is the defined pair with largest L(s), carrying that pair's m_C and [L_C,U_C];
   break an exact tie by smaller pair size. Print both reference sizes and intervals. If the top pair is
   undefined, no threshold is defined and the knee is not found. For every defined pair D>δD ensures
   positive exact reciprocal endpoints; do not refuse because a symmetric approximation's lower endpoint
   would be nonpositive. Undefined pairs cannot supply either reference.
4. Threshold, derived: a pair whose added bytes come from cache in fraction c takes
   (1−c)/m_D + c/m_C seconds per byte. The stream-size rule caps its cached fraction at 1/64, so let
   H(x,y)=1/[(63/64)/x+(1/64)/y], T=H(m_D,m_C). Since H increases in both positive arguments, its propagated
   interval is [T_L,T_U]=[H(L_D,L_C),H(U_D,U_C)]. A defined pair counts as above threshold only when
   L(s)>T_U. Equivalently print margin=m(s)−T and bar=[m(s)−L(s)]+[T_U−T], and require margin>bar.
   This bar is derived from the receipts' observed spread and clock quantities through exact endpoints;
   no numerical epsilon, noise multiplier or percentage band is added. Print every comparison.
5. First form the candidate K as the smallest scanned pair size with no above-threshold pair at that
   size or higher. Use all above pairs, including isolated late pairs; an undefined pair never counts as above.
   Then require both actual proposed cache-arm increments (K/16→K/8) and (K/8→K/4) to be scanned,
   defined and above threshold by step 4. These are the C1→C3 and C3→C2 increments of the existing arms,
   so their number and locations follow from the arm geometry. Missing evidence is not repaired by
   discarding a late pair, shrinking K or repeating the scan. Print the candidate K and each arm check.
   Observed-spread intervals do not guarantee against a false knee or a false refusal under timing noise.
   A false knee can spend the measured hour on DRAM-reading “cache” arms; DC validity will often then
   read UNDETERMINED, but is not guaranteed to catch every timing misclassification.
6. Refusal: the knee is not found if the top reference/clock prerequisite is unavailable, no pair is above,
   no candidate K exists, either cache-arm increment fails step 5, or 64K>s_max. Print the candidate and
   the specific reason. The measured hour then does not run; every class is UNDETERMINED (`knee not found`),
   and the slot records the scan and reason. Preserve the one scan's calls; do not retry it into acceptance.

### §1: replacement first Sizes bullet

- *Bc2 = K / 4.* The scan directly requires separated marginal evidence on C1→C3 and C3→C2, and K's
  definition makes the pair ending at K/2 above threshold. Under the stated cache/DRAM timing model,
  these observations support using K/4 clear of the transition. They are timing evidence, not a hardware
  cache-residency counter or proof against unobserved timing excursions. Bc1=K/16 and Bc3=K/8 retain
  their existing roles and sizes.

### §2: receipt addition

Add to every v2 receipt, including measured-arm receipts: `clock_resolution_s` from
`time.clock_getres(time.CLOCK_MONOTONIC_RAW)`; `clock_tick_num_ns`, `clock_tick_den` and
`clock_tick_source` from the machine's measured timebase; `clock_ns_conversion` and its source;
and the derived `clock_duration_bound_ns = 2 * (max(resolution_ns,tick_ns) + 1)`.
Retain the raw resolution/timebase values, so the derived field is independently recomputable.
For the supplied Mac these are 4.2e−8 s, 125, 3, the lead's dated timebase measurement,
truncation/unknown unless its conversion source is established, and 86 ns. Do not insert
synthetic tick metadata into a receipt presented as a live measurement. A missing clock
prerequisite is printed with the scan, not a fabricated 1 ns fallback.

### §3: complete replacement

## 3. The reported quantity and its bound

**Knee-scan prerequisite and scope.** Use K, B and the three cache sizes only after the §1 scan
has passed its exact-interval comparisons and both C1→C3 and C3→C2 timing-evidence checks.
The scan's intervals are derived from clock quantization and three observed calls; they are not
confidence intervals on future timing noise and do not prove cache residency. If the knee is not
found, preserve and print its calls, clock metadata, comparisons, candidate K and specific reason;
the measured hour does not run, the classes are UNDETERMINED (`knee not found`), and quantities
requiring K print `not defined (knee not found)`. A false positive can spend the hour with cache
arms reading DRAM; DC validity may then be UNDETERMINED, but this is a downstream check, not a
logical guarantee that every false knee will be caught. This scan prerequisite changes no
collected BYTES number and adds no energy-uncertainty term to the propagation below.

**Boundaries.** rails (CPU + GPU + ANE), the GPU rail alone (the `gpu_power` series of the same capture), DC input,
and rest. Each is integrated over a stamped span exactly as pass 1 integrates it (reg. §7):
- rails and the GPU rail by **native interval support** (the trace is a sum of constant-power intervals, so a
  span edge inside one interval needs no interpolation) under the test session's **operative timing bound** (the
  measured bound on how far a laptop timestamp can sit from the trace's time base, evaluated as pass 1 evaluates
  it, `joulewise/b6/calibration.py`);
- DC input by the meter integrator (`km003c_parse.clock_fit` and `integrate`) plus the battery term E_b (reg. §7,
  "Battery term");
- rest = DC − rails per span, before any averaging.

**Meter gap.** An exact device-counter gap of n samples gives a missing duration n × Δt, with Δt = 20 ms
(50 samples/s). Charge n × Δt × P_max to that call's DC systematic bound, where P_max is the adapter's rated
maximum (nameplate/specification source recorded) plus the maximum measured positive battery discharge power
in that call (record the battery poll source and maximum). Derivation: the missing energy is no greater than
missing time times maximum supplied power. This is the adopted measured-maximum bound; it does not claim an
unmeasured battery peak cannot exceed that maximum. Keep every call, DC and rest valid, and disclose each gap.
For a gap in a baseline, charge its missing-energy bound divided by that idle span's length, times T_i/2,
because that span mean has weight 1/2 in P_idle; for a stream gap the coefficient is 1. Sum these contributions
in b_i (rest inherits DC). No 50 Hz battery alignment is introduced. A span with no battery poll carrying both
readings still makes DC and rest unavailable for the whole test (`battery reading missing in call i`);
without that prerequisite the supply/baseline and DC validity cannot be evaluated. Rails/GPU Δ still print.

**Arithmetic, per boundary β** (energies in J; 1 GB = 10⁹ bytes):

1. Idle power of call i: P_idle,i = (P_pre + P_post) / 2, each the mean power over its stamped idle span.
2. Excess energy of call i: X_i = E_β[start_ns, end_ns) − P_idle,i × T_i, with T_i the stamped span in seconds.
3. Excess per dispatch of arm a: x_a = Σ X_i / Σ N_i over the arm's two calls; per call, x_a,i = X_i / N_i.
4. Cache line through C1 and C2: γ_c = (x_C2 − x_C1) / (Bc2 − Bc1) (J per cache-sourced byte) and
   α = x_C1 − γ_c × Bc1 (J per dispatch, independent of size).
5. Residual of the middle size: r = x_C3 − (α + γ_c × Bc3). It is zero when the fixed cost is the same at all three
   cache sizes and the per-byte cost is linear.
6. DRAM-sourced energy per byte: γ_d = (x_S − α) / B.
7. **Reported quantity: Δ_β = γ_d − γ_c**, in J/GB: the extra energy on β per logical byte read from DRAM rather
   than cache, with the kernel and per-dispatch work held fixed.

**Bound, per call.** b_i is the sum (not in quadrature, as the registration sums its systematic terms in reg. §7 step 4)
of the rows below for call i:

| Term | rails and GPU rail | DC input | rest |
|---|---|---|---|
| Edges at start_ns and end_ns | the call's rails **anchor-shift bound** (the energy that moving both span edges by the operative timing bound could add, computed by the pass-1 function on the call's span; H: 0.28 to 0.63 J per run, both edges together); the GPU rail uses the rails bound, which is never smaller because GPU power never exceeds rails power; interpolation term 0 for interval support | u + v of reg. §7: u = (P_start + P_end)(r_max + Δt), with r_max the largest excess latency of the test's meter clock fit and Δt = 20 ms at 50 samples/s; v = v_start + v_end, the battery energy of the polls received in [edge, edge + τ) | rails row + DC row |
| Counter gaps | 0 | sum of the gap contributions derived above | DC row |
| Baseline | T_i × (\|P_pre − P_post\| / 2 + 2 se_idle) | same, with the DC spans' values | rails row + DC row |

- *Baseline term.* The half-difference bounds a baseline drift that is monotone across the call; the 2 is reg. §9's
  two-standard-error convention. se_idle = √(v_pre + v_post) / 2 is the standard error of the mean of two
  independent span means, where v_pre and v_post are each span's variance of the mean from
  `joulewise.idle_dependence.estimate_newey_west_bartlett` (method
  `duration_weighted_newey_west_bartlett_10s_iid_floor_v2`, the estimator behind pass-1's
  `idle_variance_of_mean_w2`: the larger of the IID variance and a Newey–West estimate with a 10 s Bartlett
  bandwidth). Apply it separately to rails and GPU samples (10 Hz, 100 lags), meter samples (50 Hz,
  500 lags), and battery discharge-power polls at their own observed cadence (about 5 Hz, about 50 lags),
  using rails/GPU native interval durations clipped to the idle span. Meter/battery means retain the pass-1
  integrator's arithmetic sample support in [span_start, span_end): give each of its n retained samples equal
  duration span_length/n in the estimator, so its weighted mean equals the integrated mean. Thus do not interpolate, hold a battery poll onto meter stamps, or construct a joint series.
  For battery polls use lag_count = floor(10 s / median native inter-poll interval); record the interval,
  lag count, sample count and equal support durations. The approximately 1 Hz SMC updates are already repeated in the native
  battery polls and enter this estimator's serial dependence, not a resampled stream. Each stream needs the
  estimator's own sample/cadence support (including at least three bandwidths); if unavailable, print the
  missing prerequisite and do not claim DC validity. This rule registers the estimator for meter and battery
  separately; neither inherits it by analogy.
- *DC combination, derived without alignment.* For each stream h, se_h = √(v_h,pre + v_h,post)/2. Then
  Var(mean_meter + mean_battery) = se_meter² + se_battery² + 2 Cov ≤ (se_meter + se_battery)² by
  |Cov| ≤ se_meter se_battery. Thus se_DC = se_meter + se_battery (the correlation +1 bound), with no
  covariance estimate. Use this in the DC baseline row; retain the summed stream means for P_pre/P_post.
- *Rest* sums the rails and DC rows, so it needs no variance of its own.

**Repeatability.** Every row above is systematic; none responds to the two calls of an arm disagreeing, so energy
present in one stream span and absent from its idle spans (a background process, a thermal step, a clock-state
excursion) would go unbounded and could push a class toward RESOLVED. Each arm therefore adds
rep_a = |x_a,1 − x_a,2| × max(N_1, N_2) / (N_1 + N_2). Derivation: a transient E confined to call 1 moves x_a by
E / (N_1 + N_2) and moves x_a,1 − x_a,2 by E / N_1, so rep_a is exactly the shift it causes (with the larger N for
either call). It costs no measurement. It does not bound an excursion present equally in both calls of an arm.

**Propagation** (worst case, linear):
- δx_a = Σ b_i / Σ N_i + rep_a;
- δγ_c = (δx_C1 + δx_C2 + |r|) / (Bc2 − Bc1);
- δα = δx_C1 + |r| + δγ_c × Bc1;
- **δΔ = (δx_S + δα + |α|) / B + δγ_c.**

The |α| / B term charges the whole per-dispatch cost as possible error, because a 4 GiB dispatch may carry a
different fixed cost from a cache-sized one; no factor is invented for it. Treating α and γ_c as independent is
conservative (by about 0.2% on the unrevised draft's example inputs, Opus cold pass). The |r| terms charge a fixed cost that differs
between the cache sizes, as far as C3 shows it.

**What the bound does not cover.** A fixed cost ε per dispatch that differs between C1 and C2 moves Δ by
ε (1 − Bc1/B) / (Bc2 − Bc1), about 340 times the leverage of the same ε between S and a cache arm (Fable cold
pass). The C3 residual charges only the part of such a difference that is not linear in payload size; a part
linear in size is indistinguishable from per-byte cache energy. On the §5 inputs, C2 dispatches 1% cheaper in
fixed cost than C1 in a world with no memory-traffic energy on rails still reads RESOLVED (§5). Its sign is not
controlled. Two descriptions make it visible (§4): ε_flip, the fixed-cost difference that would move Δ by its own
half-width, and each arm's mean GPU active frequency and residency. Removing it needs a kernel that holds dispatch
structure fixed (Sol's design), which is new code.

**Bias, printed beside Δ.** If a fraction φ of S's reads hit in cache, Δ measured = (1 − φ) Δ true. For a cyclic
scan of B above the cache, φ ≤ K / B, printed. A cache arm that leaks to DRAM raises γ_c and lowers Δ. Both cache
effects run toward "not resolved", never toward "resolved"; this sentence covers cache leakage only (see the
paragraph above and "Repeatability" for errors of either sign).

**Printed precision.** Every Δ, δΔ and description quantity with a half-width prints its half-width to 2
significant figures and the estimate to the same decimal place (reg. §14's H2 rule: a 2-significant-figure half-width is
at least 10 units of its last digit, so rounding moves a value by at most 5% of it). K, B, the cache sizes, N and
byte counts print exactly; φ prints as its exact fraction. Classes are decided on full-precision values.

**Agreement bar** for an independent recompute, if one is made: every class identical; K, B, φ and every count
identical; every Δ and δΔ within one bar, 1% of the smallest printed δΔ among the boundaries; any other printed
quantity within half a unit in its last printed decimal (reg. §12). The bar must exceed 10⁶ × float noise, where float
noise is the propagation above applied to a relative error of 2.2 × 10⁻¹⁶ (binary64's machine epsilon) on every
gross energy, as reg. §12 uses it (worked example: 2.5 × 10⁻¹⁰ ≤ 5.7 × 10⁻⁶ J/GB).


### §5: replacement Knee paragraph

*Knee.* With the stated cache/DRAM timing model, the exact-interval scan and both cache-arm
increment checks give K=64 MiB, B=4 GiB, Bc1=4 MiB, Bc3=8 MiB, Bc2=16 MiB and φ=1/64.
Clock bars use the receipts' recorded resolution and timebase, not the integer output unit.
For the supplied 42 ns resolution and 125/3 ns tick, the conservative duration contribution is
86 ns divided by repeats. In the independently recomputed quantized worked example, the
16→32 MiB margin is about 664.90034 GB/s against a derived one-sided bar of 0.00043 GB/s;
the threshold half-width is 0.000045 GB/s. The reviewer model's rounded DRAM reference
331.6 GB/s gives T≈335.0997 GB/s. Random-phase tick quantization preserves K in the noiseless
worked example. A noiseless DRAM-only model supplies no cache-arm evidence with the corrected
clock bar. Neither statement guarantees an outcome under unobserved per-call timing noise.

## Verification, files and handoff

Environment: Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1` throughout
synthetic imports/execution. No MLX/Metal, energy capture, quiet-Mac work, unblinding, production
implementation, merge or admission was performed. Existing focused tests:
`python3.13 -B -m unittest -v tests.test_bytes_stream_test tests.test_bytes_mac_kit`:
**33 tests, OK** (`focused-tests.log`). The first attempt in the read-only sandbox had six
temporary-directory errors; rerunning with ordinary temporary-file write access passed all 33.
There was no automatic-approval rejection. A full suite was not needed for report-only and
consult-script changes; the focused checks establish the pinned function's baseline.

Reproduction from repository root:

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B .codex-report/kb-knee-consult/experiment.py --trials 2000 --replay-reviewer
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B .codex-report/kb-knee-consult/experiment.py --trials 2000 --rounding nearest
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B .codex-report/kb-knee-consult/verify.py
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B .codex-report/kb-knee-consult/write_report.py
```

Scripts fail if the pinned source-edit anchors change. Evidence includes the two raw result
JSONs, two stdout sweep logs, reviewer replay log and rational-verification JSON. The original
reviewer scripts were checked byte-identical against their fetched Git blobs. Both result files
contain all 60 candidate/noise/world cells, each with 2,000 outcomes. `git diff --check` passes; the branch diff is confined
to the report and consult directory. The requested branch is committed and pushed for lead review.
The final delivery message identifies the pushed commit; it is not a self-referential report field.

Next exact step: the lead rules on the recommendation, then gives a builder authority to install
the stated registration/receipt/scan changes and appropriate focused regression checks. The
unknown live noise distribution and residual false-refusal risk remain explicit; there is no
request for a new measurement campaign or permission expansion in this consult.
