# BYTES known-bytes stream test: the reading rule (DRAFT, revised)

**Status.** Reconciled revision awaiting the lead's admission, installed 2026-10-28 in magistrate activation
39206674. Originally drafted 2026-10-25 in activation f18a96e1 from two blind design seats
(`docs/process_traces/2026-10-25-magistrate-f18a96e1/KB-SEAT-SOL.md` and `KB-SEAT-OPUS.md`, brief `KB-BRIEF.md`).
Reconciler: Opus 5.5, JouleWise-data `claude/kb-revise-opus` at `0609bcc0caf941fd68c36fccea323f34c3951730`,
`kb-revise/CHANGES.md`. Cold reports: Fable 5.1, `claude/kb-cold-fable` at
`39398e572ea0943edc77f0981d82e3be32311a32`, and Opus 5.5, `claude/kb-cold-opus-gteliv` at
`ecd46c1124000dbfbc51b475068661ceefb62a1f`, both `kb-cold/REPORT.md` in JouleWise-data, both
ADMIT-WITH-CORRECTIONS. These are independent executing reviews by models that did not write the draft.
The lead has adopted CHANGES.md option (a) for Fable 1: the disclosure, ε_flip and per-arm GPU frequency and
residency remain; neither a new kernel nor a leverage model is adopted. Admission of this revision is still pending.

It answers registration-gate finding 4 (Opus, `docs/process_traces/2026-10-24-magistrate-7209d1b0/REGGATE-OPUS.md`):
before the test runs, say which quantity is reported and which outcome prints a caveat. "The registration" below
is `docs/registrations/bytes_pack_v1.md` at the registered pass-1 tree `6731d5249` (the BYTES pre-registration:
it fixes the questions, runs and arithmetic of a study of decode energy per token against bytes read per token,
before any energy is measured). "reg. §n" is a section of the registration; "§n" alone is a section of this text. The rule binds once the lead admits
this revision, and it must bind **before the test runs**. The test itself runs after pass-1 collection (the first
of two collection passes) and before stage-1 unblinding (the first release of the hidden factors that scale every
energy until the fit-set predictions are committed; reg. §11, reg. §19, P0 ruling 9). Nothing here changes a collected
number, an exclusion or an estimator: the outcome only adds lines beside the claim lines (the registration's
printed result lines) and fills the reg. §1 slot (a marked placeholder in reg. §1 for this outcome).

## 0. The question, and what this test cannot answer

The registration measures energy at three **boundaries** (reg. §1): **rails** (CPU + GPU + neural-engine energy that
macOS `powermetrics` reports for the processor chip), **DC input** (the energy entering the whole laptop: a KM003C
USB-C meter on the charging cable, plus the energy the battery supplies when the laptop draws more than the
adapter delivers) and **rest** (DC input minus rails: memory chips, power conversion losses, SSD, fans).
`powermetrics` reports no memory (DRAM) channel. So when a model reads its weights from memory, part of that energy
may show in rails (if the circuits that move bytes are on a reported rail) and part only in rest (the memory chips
themselves). Reg. §1 registers the expectation: the chip's share appears in rails, the memory chips' share in rest.

The test streams a known number of bytes through the GPU and asks whether each boundary's energy rises **because
the bytes came from DRAM**. A stream on its own cannot answer that: reading bytes keeps the GPU busy, so the GPU
rail rises whether or not the memory controller is on it. The test therefore compares two ways of doing the same
GPU work, one whose bytes come from DRAM and one whose bytes come from on-chip cache (§1). The difference is
**memory-traffic energy**: the extra energy per byte when the byte comes from DRAM. It includes everything that
changes with the byte's source: the memory controller, the on-chip fabric, the GPU's time stalled waiting on
memory, and the GPU clock state (DVFS, dynamic voltage and frequency scaling) a DRAM-bound kernel runs at.

Both design seats agreed on the limit, and it is adopted: a positive difference on the GPU rail shows that memory
traffic costs energy on that rail. It cannot say whether the energy is the memory controller, the fabric, or GPU
cores stalled waiting on memory. On rest it cannot separate the memory chips from power-conversion loss and fan
energy that rise with the rails' own rise. No outcome of this test establishes "the GPU rail does not include the
memory controller". The classes below are worded accordingly.

*Expected outcome on rails.* A byte from DRAM holds the GPU about 3 ps (1 / 331.6 GB/s, the H throughput of §5)
against about 1 ps from cache (1 / 1 TB/s, assumed in §5), and the GPU draws power above idle while it waits. So
rails RESOLVED (§4) is close to guaranteed by stall time alone, and carries little information about the
controller. The same holds for rest through conversion loss (§4, "What responds as registered means").

## 1. The probe, its arms and sizes

The probe is `scripts/bytes_stream_test.py` (at the pass-1 tree `6731d5249`; usage in
`configs/campaigns/bytes_mac_check/README.md` there, "Known-bytes companion probe"). It allocates a `uint8` payload
of `--bytes` bytes with MLX (Apple's array library) and repeats `mx.sum(data); mx.eval(...)` `--repeats` times.
Each repeat is one **dispatch**: one reduction sent to the GPU and waited for. The probe writes a **receipt** (a
JSON record of the call) that counts **logical bytes** (payload bytes × repeats), not a hardware DRAM byte count.

Four arms use this same kernel unchanged; only the payload size differs. The **cache knee** K is the payload size
at and above which the reduction's bytes come from DRAM rather than from on-chip cache; it is measured first,
below.

| Arm | Payload per dispatch | Where the bytes come from |
|---|---|---|
| S (stream) | B, far above K | DRAM |
| C1 (cache, small) | Bc1 = K / 16 | cache |
| C3 (cache, middle) | Bc3 = K / 8 | cache |
| C2 (cache, large) | Bc2 = K / 4 | cache |

*Why several cache sizes (Opus seat, adopted over a single cache arm).* Each dispatch costs some energy that does
not depend on its size (launch, synchronization, CPU work). A cache arm moving the same total bytes in smaller
payloads makes many more dispatches, so its per-byte energy would carry more of that fixed cost. With two sizes
(C1, C2) the fixed cost per dispatch, α, and the per-byte cache cost, γ_c, are both solved for (§3). The third size
(C3, Fable cold pass) tests the assumption that the fixed cost is the same at every cache size: its departure from
the C1–C2 line is charged to the bound (§3). Sol's alternative, one kernel with an address-period parameter that
holds dispatch structure fixed, would need new kernel code; the multi-size design needs none, so it is chosen, and
§3 says what it leaves unbounded.

**Order.** Eight probe calls in a palindrome, **S, C1, C3, C2, C2, C3, C1, S**, the two calls of each arm with the
same planned length. Each arm's two stream midpoints then have the same mean time, so a drift linear in
time puts every arm at the same mean state (§5 checks these mean times). The extra settle before pre-idle
shifts that common time 1.5 s beyond the session midpoint; this shared offset does not change the cancellation. This is
the reasoning of the registration's null quads (A, B, B, A, reg. §5) applied to arms.

**Cache knee K: measure first.** The repository records no cache size for this M3 Max. Before the measured hour,
with no energy capture and with `--idle-s 0 --settle-s 0` (§2; otherwise the idle spans would add about two hours): run the probe at `--bytes 2^k` for k = 14 to 35 (16 KiB to 32 GiB), three calls per size, repeats chosen so
each call lasts about 2 s (planning choices: they set the observed timing spread, propagated below). If a
size cannot be allocated as one buffer, the scan stops at the largest size that can, s_max (32 GiB if all can).
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

The scan reads no energy and is not BYTES data.

**Sizes.**
- *Bc2 = K / 4.* The scan directly requires separated marginal evidence on C1→C3 and C3→C2, and K's
  definition makes the pair ending at K/2 above threshold. Under the stated cache/DRAM timing model,
  these observations support using K/4 clear of the transition. They are timing evidence, not a hardware
  cache-residency counter or proof against unobserved timing excursions. Bc1=K/16 and Bc3=K/8 retain
  their existing roles and sizes.
- *Bc1 = Bc2 / 4, Bc3 = Bc2 / 2.* δγ_c falls as Bc2 − Bc1 grows (§3); dividing Bc2 by 4 gives 3/4 of the largest
  possible difference while keeping a power of two (Bc3) between the two ends for the linearity check. A planning
  choice; its effect is the printed δΔ.
- *B = max(4 GiB, the smallest power of two ≥ 64 K).* 4 GiB sits beside Qwen3-8B-4bit's bytes per pass
  (4,597,412,096, reg. §4 table), inside the fit set's range (the fit set is the three models the registration's
  rival lines are drawn through, reg. §2). The factor 64 caps the cached fraction of S's reads at φ = K / B ≤ 1/64
  (§3, "Bias"). φ enters every class decision either as the exact correction 1 / (1 − φ) or by pulling Δ toward
  zero, so no class depends on its size; 64 is a planning choice that keeps the correction at most 1.6% and B
  within a 32 GiB scan for any K up to 512 MiB.

**Repeats.** Each call's repeats N = floor(T_call / t_dispatch), with t_dispatch = duration / repeats measured at
that exact payload in the knee scan and T_call the call's planned stream length. Planned split of the hour: sixteen
idle spans of 57.6 s (921.6 s), twenty-four settle gaps of 3 s (72 s; §2), about 10 s per call of allocation, fill,
warm-up and exit (80 s; measured in the scan), S 2 × 500 s, C1, C3 and C2 2 × 250 s each (2,500 s): 3,573.6 s.
These are planning choices, not thresholds; the arithmetic uses the actual stamped spans.

## 2. The receipt change (one small code change, before the test)

The receipt gains schema `joulewise.bytes_stream.v2` with:

1. **Order inside a call, idle spans and settle gaps.** Allocate and fill the payload, `mx.synchronize()`, run one
   warm reduction and synchronize (so the first measured dispatch is not a kernel compile), then: sleep one
   settle gap before stamping `idle_pre_start_ns`, sleep the pre-idle span (`--idle-s 57.6`), sleep the settle gap (`--settle-s 3`), stream from `start_ns` to `end_ns`,
   sleep the settle gap, sleep the post-idle span with the payload still resident, exit. Stamp
   `idle_pre_start_ns`, `idle_pre_end_ns`, `idle_post_start_ns`, `idle_post_end_ns` on CLOCK_MONOTONIC_RAW, the
   clock of `start_ns` and `end_ns`. Without these, the baseline cannot be computed from the receipt and traces
   alone (the time before `start_ns` holds the fill, which is not idle).
   - *57.6 s* is `sampling.idle_seconds` of every pass-1 BYTES run config, and it exceeds the three 10 s
     bandwidths the idle-variance estimator requires (§3).
   - *Settle gap 3 s,* derived: an idle span next to the stream would take in energy that a boundary reports
     late or smears across the edge. The longest such delay is the battery's, τ = 2 × T_SMC + Δt_p (reg. §7: the
     system controller publishes battery current once a second, T_SMC = 1.0 s, and Δt_p is the longest interval
     between meter polls), 2.302 s on H; it exceeds one rails sample interval (100 ms at the registered 10 Hz)
     and the meter's r_max + Δt (38 ms on H, §3). 3 s is the next whole second above τ. The same delay applies after fill/warm-up, hence the extra gap before pre-idle. If the test's own τ
     exceeds 3 s, each idle mean is taken over its stamped span minus its first τ − 3 s. Energy inside the gaps enters
     no quantity.
   Every receipt, including measured arms, records `clock` = `CLOCK_MONOTONIC_RAW`,
   `clock_resolution_s` from `time.clock_getres(time.CLOCK_MONOTONIC_RAW)`, and on macOS
   `clock_tick_num_ns`/`clock_tick_den` from `mach_timebase_info`, with `clock_tick_source`.
   `clock_ns_conversion` and `clock_ns_conversion_source` are `unknown` unless a source
   establishes the convention; the observed steps alone do not. The derived
   `clock_duration_bound_ns` = 2(max(resolution_ns, tick_ns) + 1) retains both raw inputs.
   On non-macOS the timebase fields are null and marked not applicable; getres supplies r.
   Missing clock prerequisites retain the receipt and print the scan reason, with no 1 ns fallback.
2. **Stack object** (the governed runtime identity, so a change of OS or library between pass 1 and the test is
   visible). The sources and comparisons are listed below (§4, "Stack check"); the device source is explicit
   because this standalone probe has no telemetry device metadata:

   | Receipt field | Source | Compared with (registered pass-1 stack) |
   |---|---|---|
   | `os_version` | `platform.platform()` | `stack_identity.os_version`, string equality |
   | `hardware_unit.machine`, `hardware_unit.device` | `platform.machine()`; explicit `--device` from `hardware_target.id` (pass 1 takes `device` from telemetry device metadata; its `config_id` comes from `hardware_target.id`) | `stack_identity.hardware_unit.machine`, `.device` |
   | `runtime_version` | `{"name": "mlx", "version": mx.__version__}` | `stack_identity.runtime_version.name` and `.version` |
   | `kernel_library` | as pass-1 prepare records it, else `"unavailable"` | `stack_identity.kernel_library`, string equality (`"unavailable"` on both sides is equal) |
   | `python`, `packages` | `joulewise.flags.collect.runtime_versions` (Python and all seven packages) | `configs/bytes/identity_pins.json` `runtime_versions`, every key |
   | `git_commit` | the non-claim checkout | printed, not compared (the checkout differs by design) |
   | `model_artifact_sha256`, `quantization`, `tokenizer_identity`, `sampler_output_policy`, `batching_concurrency_policy` | `"not_applicable"` (no model is loaded) | not compared |

   `telemetry_backend` and `measurement_boundary_label.rails` come from the concurrent capture's record at harvest
   (the step that collects traces and computes per-run fields after a session), as in pass 1, and are compared
   with `stack_identity.telemetry_backend` and `.measurement_boundary_label.rails`. The reference is the embedded projection read at `6731d5249` from all 19 `units`
   entries of `configs/b6/registration/identity_pins.json`, which agree on these fields (`macOS-26.6.2-arm64-arm-64bit-Mach-O`, `arm64`, `macbook_m3_max`, mlx 0.31.2, `unavailable`,
   `powermetrics`, `cpu_power, gpu_power, ane_power`). Source sha256:
   `95d07401bb5d7c7e44e9dc27984bc3da4fb04642ec7cf80bf3c6ecadaf2efc6e`.
   The embedded Python/package projection comes from `configs/bytes/identity_pins.json` at the same commit,
   sha256 `0760eded0603782b5367ad56721faf96417b9ea87bb698dc520835f34e03b2b2`.
   The receipt records these provenance values and the running checkout's full projected comparison with them,
   including missing/unreadable files and divergent units. Checkout divergence never raises or changes a class.

   **Physical scope of a difference.** The OS build can change the driver, scheduling and power states; the
   hardware unit/device changes the cache, memory path and rails; `runtime_version.name/version`, `packages.mlx`
   and `packages.mlx-metal` select the reduction kernel and its execution. These differences
   prevent transfer and set UNDETERMINED. A difference in `measurement_boundary_label.rails`
   changes the physical set of measured rails: rails and rest are UNDETERMINED
   (`measured rails boundary differs`); DC is unaffected. `kernel_library` is recorded as prepare metadata (the actual
   running kernel versions are the two MLX packages). `telemetry_backend` discloses the
   capture metadata; the governed boundary integrations above still have to be supplied. They do not independently
   veto a class. `mlx-lm` loads/generates model text; `transformers` and `tokenizers` supply model/token processing;
   `safetensors` reads model weights; `numpy` supplies host arrays. None is used by this uint8 MLX reduction.
   Python patch level changes the host interpreter metadata, not the selected MLX/Metal kernel; dispatch work is
   measured and removed by the cache arms. Each of these differences is printed as a disclosure and changes no
   class. `git_commit` and the five not-applicable model fields have the non-comparison roles in the table.

**Capture and harvest.** One continuous `powermetrics` capture and one continuous meter stream cover all eight
calls, with one meter clock fit for the test, from the test's own non-claim checkout with the chain extension (reg. §19).
Integrating rails, the GPU series, DC input and the battery term over the receipt's stamped spans, rather than over
a run's own phases, is the one new piece of harvest code; it calls the pass-1 integrators unchanged.

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
  For battery polls use lag_count = floor(10 s / median positive native inter-poll interval); record the interval,
  lag count, sample count and equal support durations. Count and disclose duplicated stamps;
  retain every poll, and do not make variance undefined solely because a stamp is duplicated. The approximately 1 Hz SMC updates are already repeated in the native
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

## 4. Validity, classes and the printed lines

**Validity.** The contrast is valid only when Δ_DC − δΔ_DC > 0. DC input encloses rails and rest, so a real
memory-traffic cost must show there; if it does not, the control failed to separate DRAM traffic from GPU work.

**Stack check.** Record and print the full comparison in every case, including all disclosure-only differences
and pending fields. Differences in OS build, hardware unit/device, or MLX/MLX-Metal runtime versions set
UNDETERMINED; §2 gives their physical paths. A different `measurement_boundary_label.rails`
is a different measured rails boundary: rails and rest are UNDETERMINED with that reason,
while DC is unaffected. Other differences change no class.
The receipt keeps `differences`, `physical_differences` and `disclosure_differences`; harvest completes the
capture comparison and prints it even for an otherwise undetermined result.

**Classes**, read separately on rails, on the GPU rail and on rest, with I = [Δ − δΔ, Δ + δΔ], φ = K / B and ε₀
defined below. The rows are tested **in order** and the first that holds is the class, so exactly one holds:

| Order | Class | Condition | Meaning |
|---|---|---|---|
| 1 | UNDETERMINED | knee not found; physically relevant stack differs; a required call, integral, bound, gap source, battery reading or native-support prerequisite missing; validity fails; or Δ + δΔ < 0 on this boundary | the test cannot be read on this boundary; a wholly negative contrast is a failed control, not an immaterial one |
| 2 | RESOLVED | Δ − δΔ > 0 | memory-traffic energy is resolved on this boundary |
| 3 | BELOW ATTRIBUTION LEVEL | max(\|Δ − δΔ\|, \|Δ + δΔ\|) / (1 − φ) ≤ ε₀ | the interval spans 0 and every value in it, corrected for cache bias, is too small to move any registered model's run by the instrument's per-run attribution limit; this does **not** say the controller is off this rail |
| 4 | NOT RESOLVED | otherwise | neither is shown |

Row 3 bounds both ends because a large negative value inside I would move runs as much as a large positive one.

**ε₀ = 1 J / (512 × b_max) = 4.9009 × 10⁻⁵ J/GB.** 1 J is the registration's per-run attribution scale (reg. §12,
"about 1 J per run"; the class is named for what it shows at that scale). 512 × b_max is the most bytes any
registered decode phase reads: 512 decode passes (reg. §3) × 39,852,331,520 bytes per pass (b_max, Llama-3.3-70B, the
largest b of the reg. §4 table) = 20,404.4 GB. Using the largest b gives the smallest, strictest ε₀. This is the Opus
seat's threshold; Sol argued no threshold can show exclusion, which is why the class is named for what it shows
(immaterial at the instrument's resolution), not "excludes". It may be unreachable at the test's resolution
(worked example: δΔ_rails is about 12 ε₀); then a near-zero Δ reads NOT RESOLVED, which is the honest reading.

**What "responds as registered" means (reg. §19).** Reg. §1 expects the chip's share in rails and the memory chips' share in
rest. So rails responds as registered when its class is RESOLVED, and rest when its class is RESOLVED, in the
mechanism-neutral sense of §0: rest RESOLVED shows that rest rises with DRAM traffic, not that the memory chips'
share is in rest (conversion loss on the rails' own rise also shows there; on the §5 inputs, a 10% loss on Δ_rails
is about 0.0067 J/GB, about 3 δΔ_rest). DC input needs no caveat: moving energy between the inner boundaries cannot
change the enclosing one. The GPU-rail class prints nowhere beside claim lines (no claim line uses the GPU rail
alone); it fills the reg. §1 slot.

**Printed lines.** One line beside the rails claim lines and one beside the rest claim lines, whenever that
boundary's class is not RESOLVED (values filled from the test record; Δ is signed, DRAM minus cache):

- BELOW ATTRIBUTION LEVEL: `Known-bytes check: {boundary} energy per DRAM-sourced byte differed from cache-sourced by {Δ} ± {δΔ} J/GB (DRAM minus cache), within the 1 J-per-run attribution level ({ε₀} J/GB); {boundary} lines here carry no resolvable memory-traffic energy.`
- NOT RESOLVED: `Known-bytes check: the {boundary} response to DRAM-sourced bytes is not resolved ({Δ} ± {δΔ} J/GB, cache-bias-corrected upper limit {(Δ+δΔ)/(1−φ)} J/GB); whether {boundary} lines include memory-traffic energy is not established.`
- UNDETERMINED: `Known-bytes check: {boundary} memory-traffic attribution is undetermined ({reason}).` with reason one of `knee not found`, `stack differs in: <physical fields>`, `battery reading missing in call <i>`,
  `idle variance not defined (<stream/support reason>)`, `contrast not resolved` (validity fails), `contrast negative` (Δ + δΔ < 0).
- Test not run before stage-1 unblinding: beside the rails and rest lines, `Known-bytes check: not measured; the boundary attribution of memory-read energy (§1) is not established.`

When a boundary is RESOLVED, nothing prints beside its claim lines. Inside printed lines, "§1" is the
registration's §1.

**The reg. §1 slot** is filled with the three classes (rails, GPU rail, rest), Δ ± δΔ for rails, GPU rail, DC and rest,
K and φ = K / B, the stack-check result, the receipt digests, and the sentence: "The test identifies memory-traffic
energy on a boundary, not whether it is the memory controller, the fabric or the GPU waiting on memory; on rest it
does not separate the memory chips from power conversion and fans."

*Wording of reg. §1 on admission (proposed, changes no number).* Reg. §1's sentence "Whether the GPU rail includes the memory
controller is measured by the known-bytes stream test" claims more than the slot can show; it becomes "Whether
memory traffic costs energy on the GPU rail, on rails and on rest is measured by the known-bytes stream test".

**Description only** (no class reads them), printed in the test record:
- the stream arm's raw excess per logical byte, X_S / (Σ N_S × B), on each boundary;
- the rails share f = Δ_rails / Δ_DC, with δf = (δΔ_rails + |f| δΔ_DC) / |Δ_DC| when DC is valid;
- the GPU-rail excess-power contrast between S and C2, X_S / T_S − X_C2 / T_C2;
- per boundary, the residual r and ε_flip = δΔ (Bc2 − Bc1) / (1 − Bc1 / B), the fixed-cost difference between C1
  and C2 dispatches that would move Δ by its own half-width, also as a fraction of α;
- per arm, each call's x_a,i and rep_a; the mean GPU active frequency and residency from the capture's
  `gpu_power` sampler; per span, the OS thermal level from the notify-bus journal
  `hazards/monitor/thermal.jsonl`, selected by the span's RAW stamps;
- the test's r_max, τ and operative timing bound, and the hour as run.

Every description with a zero denominator or missing prerequisite prints `not defined (<reason>)`, e.g.
`not defined (alpha is zero)` for ε_flip/α, `not defined (DC contrast not valid)` for f and δf,
`not defined (knee not found)` for a quantity requiring K, or `not defined (thermal journal missing)`.
For Δ_rails = 0 and valid DC, f = 0 and δf = δΔ_rails/|Δ_DC| are defined. A missing description never
refuses a measurement or changes a class; the validity prerequisites above retain their explicit role.

**Missing prerequisites.** Print the whole record, with each affected class UNDETERMINED
and `not defined (<reason>)`, beside every still-computable number. This includes a missing
call, missing stream integral, missing r_max/edge bound, missing native support or unnamed
gap power source/missing adapter rating. A gap's power sources must be named; enforce this
through the printed reason, never an exception that discards the record. Retain all inputs,
per-call excesses, available bounds and central contrasts when only their bound is undefined.
A missing DC prerequisite prevents common DC validity; a rails-only prerequisite affects
rails/rest, and a GPU-only prerequisite affects GPU. With no K, every K-dependent quantity,
including share and GPU arm-power contrast, is `not defined (knee not found)`.
The NOT RESOLVED upper limit uses the same decimal place as its H2 interval. A zero
half-width uses a fixed two-decimal display (`0.00`), since zero has no significant digit.

**Executable reader (synthetic or harvested products).** `/opt/homebrew/bin/python3.13 scripts/bytes_stream_test.py scan SCAN.json`
prints §1 from a JSON list of the 66 probe receipts (or the completed doubling prefix).
`/opt/homebrew/bin/python3.13 scripts/bytes_stream_test.py read INPUT.json` prints the full §3/§4 record, including the stack comparison
in every outcome and H2-formatted claim lines. INPUT has `scan` (the scan command's result) and `records`
(the eight entries in stamped palindrome order), each with `receipt` and `harvest`.
The harvest contract is explicit: `energy_j` holds pass-1 stream integrals `rails`, `gpu`, `meter`, `battery`;
`idle.pre`/`idle.post` hold native `rails`/`gpu` interval rows (`start_ns`, `end_ns`, `power_w`)
and native `meter`/`battery` polls (`stamp_ns`, `power_w`), in RAW time. Supply the untrimmed native rows;
the reader clips intervals, selects polls in the half-open idle spans and applies §2's τ trim.
`anchor_shift_j`, `operative_timing_bound_s`, `r_max_s`, `tau_s`, `meter_edge_w` (two edge powers),
and `battery_edge_j` (the two edge v terms) come from the governed integrators, not from this reader.
`capture_stack` completes the comparison. `battery_samples` supplies the call's native discharge-power polls;
`adapter_max_w`, `adapter_source`, `battery_source`, and `meter_gaps` (rows with `span` stream/pre/post and
integer `missing_samples`) supply the R5 disclosures. Optional description inputs are `gpu_state`,
`thermal_spans` joined from the named journal by RAW spans, and `hour_as_run_s` measured from session endpoints.
Absent description inputs print the reasoned `not defined` convention. Native variance estimates and their
cadences/supports, all receipts, systematic bounds and gap sources remain in the record. Full precision numeric
fields support recomputation; `printed` carries the §14 rounded intervals and §4 claim-side sentences.
This reader consumes the existing integrators' products; it does not claim to implement the external capture
extension or validate a live Mac. The tests run the real probe with production-shaped fake arrays through it.

## 5. Worked example (illustration, not a prediction)

From JouleWise-data `claude/kb-revise-opus` at `0609bcc0caf941fd68c36fccea323f34c3951730`,
`kb-revise/kb_worked_example.py` (output `kb-revise/kb_worked_example.out`). Inputs from H, the non-claim check
session of 2026-10-21/22 (records at JouleWise-data `8db1b40d6`, `bytes-h-desk-20261022/export/`, and
`docs/process_traces/2026-10-22-forward/BAT-RULING.md` §9), where a record exists:
- S-arm rails power 31.45 W (Qwen3-8B-4bit median rails decode power, 223.22 J / 7.098 s) and DRAM throughput
  331.6 GB/s (its b × 512 / T);
- S-arm rest power 52.39 W (Qwen3.5-122B check-r01 rest over decode, 577.210005 J / 11.017813 s);
- idle power: rails 0.051 W with variance of the mean 1.2037 × 10⁻⁴ W² per span (8B-4bit medians), so
  se_idle = 0.0078 W; DC 2.386 W ((6101.072862 − 5967.417892) J / 56.018813 s, 70B check-r01);
- rails anchor-shift bound 0.5388 J per call (8B-4bit median); r_max = 17.76 ms; Δt = 20 ms; v = 0 (84 W is below
  the 140 W adapter).

Assumed, standing in for what the test measures: meter idle standard error 0.05 W and battery idle standard
error 0.01 W per span, each from its own stream estimator. Thus se_meter = 0.05/√2 = 0.03536 W,
se_battery = 0.01/√2 = 0.007071 W, se_DC = 0.04243 W; no covariance or alignment is assumed;
half-differences |P_pre − P_post| / 2 of 0.002 W (rails) and 0.05 W (DC); fixed time 50 µs per dispatch; cache
throughput 1 TB/s; 28 W (rails) and 25 W (rest) above idle during cache arms; a true cache capacity of 64 MiB; no
transient and no fixed-cost change between sizes, so rep_a = 0 and r = 0. The baseline example has no meter
gaps; the gap counterexample below uses the H adapter rating, 140 W, and measured battery maximum 0 W.

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

The measurement Mac was measured by the lead on 2026-10-28: timebase 125/3 ns,
`time.clock_getres(time.CLOCK_MONOTONIC_RAW)` = 4.2e-8 s, smallest positive deltas
41, 42, 83, 84 and 125 ns. These do not establish the integer conversion convention.
The worked scan agreement bar is 4.5e-7 GB/s = 1% of the smallest printed uncertainty
(0.000045 GB/s); the independent rational check finds 10⁶ × binary64 noise below it.
Clock changes affect the scan only: K and all energy-example counts and numbers below remain unchanged.

*Hour.* 3,573.6 s = 921.6 idle + 72 settle + 80 allocation/exit + 2,500 stream. Every arm's paired stream
midpoints average 1,788.3 s, 1.5 s beyond the session midpoint 1,786.8 s (the additional pre-idle gap). N per call: S 38,457 (330,343 GB over
both calls), C1 4,613,030, C3 4,281,657, C2 3,743,791.

| | rails | DC input | rest |
|---|---|---|---|
| α (mJ per dispatch) | 1.4000 | 2.6500 | 1.2500 |
| γ_c (J/GB) | 0.02800 | 0.05300 | 0.02500 |
| γ_d (J/GB) | 0.09472 | 0.24594 | 0.15123 |
| r (µJ) | 0.000 | 0.000 | 0.000 |
| Δ ± δΔ (J/GB) | 0.06672 ± 0.00057 | 0.1929 ± 0.0025 | 0.1262 ± 0.0024 |
| ε_flip (µJ; share of α) | 7.20; 0.51% | 31.79; 1.20% | 30.78; 2.46% |

Validity: 0.1929 − 0.0025 > 0. Stack assumed identical. Rails: 0.06672 − 0.00057 > 0, RESOLVED, nothing prints.
Rest: RESOLVED, nothing prints. GPU rail: not separable in these inputs (H exports rails totals only). Description:
f = 0.3458 ± 0.0075. Agreement bar 5.7 × 10⁻⁶ J/GB (1% of 0.00057); 10⁶ × float noise 2.5 × 10⁻¹⁰ J/GB.

The full revised half-widths are 0.000571796 (rails), 0.002524213 (DC) and 0.002444084 (rest) J/GB.
The original `0609bcc0c` script predates this round: reproduce the revision by replacing its assumed
`V_IDLE_DC = 0.05**2` with `(0.05 + 0.01)**2`, its two settle gaps per call with three, and adding the
extra gap before each pre-idle in the timeline. The source ratios, energy means and counts do not change.
The synthetic arithmetic tests in `tests/test_bytes_stream_test.py` also recompute these publication digits.

*Other outcomes, same inputs except as stated:*
- One missing 20 ms meter sample in the stream of call 4 (C2): P_max = 140 + 0 = 140 W (H adapter rating
  above; assumed battery poll maximum zero), so add 2.8 J to that call's DC/rest b_i. The resulting Δ_DC
  is 0.1929 ± 0.0026 and Δ_rest is 0.1262 ± 0.0025 J/GB; both remain valid/RESOLVED. Their ε_flip are
  32.17 µJ (1.21% of α) and 31.16 µJ (2.49%). Rails, counts, energy point estimates and the agreement bar
  are unchanged. A pre-idle gap in that call would instead add 2.8 × T_i/(2 × 57.6) J, by the baseline weight.
  The gap and its power sources print as disclosures, not an UNDETERMINED reason.
- True Δ_rails = 0.00030: the rule gives 0.00030 ± 0.00057, I = [−0.00027, 0.00087], spanning 0;
  0.00087 / (1 − 1/64) = 0.00089 > ε₀ = 0.000049, so rails is NOT RESOLVED, upper limit 0.00089 J/GB.
- The same world with a 5 W transient through the whole first S call (Opus cold pass): Δ_rails = 0.0079 ± 0.0081,
  NOT RESOLVED. Without the repeatability term the half-width would be 0.00057 and rails would read RESOLVED.
- True Δ_rails = 0, C2 dispatches 1% (14 µJ) cheaper in fixed cost than C1, C3 halfway (Fable cold pass):
  r = −2.33 µJ, Δ_rails = 0.00111 ± 0.00076, RESOLVED. This is the case §3 does not bound; ε_flip (7.20 µJ) shows
  that a fixed-cost difference of half a percent of α is enough.
- Hand-set intervals: 2.5 × 10⁻⁵ ± 1.0 × 10⁻⁵ is RESOLVED only (row 2 precedes row 3); −0.0100 ± 0.0020 is
  UNDETERMINED (`contrast negative`); 1.0 × 10⁻⁵ ± 2.0 × 10⁻⁵ is BELOW ATTRIBUTION LEVEL.

## 6. Decisions

Made by the lead between the design seats:
- Contrast design: Opus's unchanged kernel with several cache sizes and the |α|/B term, over Sol's single matched
  cache arm (no new kernel code).
- Classes: Opus's two thresholds (0 and ε₀), with the lower class renamed from "EXCLUDES" to "BELOW ATTRIBUTION
  LEVEL" and NOT RESOLVED printing its upper limit, per Sol's point that non-detection cannot show exclusion.
- Idle: 57.6 s spans per call (the registered pass-1 idle length), not Sol's 300 s, because the baseline is per
  call and the palindrome cancels linear drift across calls.
- Sol's extra meter terms (label offset over Δt + poll round trip, digital resolution of one encoded unit) are not
  added: reg. §7 bounds the edges with u and adds no resolution term, and this test inherits reg. §7 rather than widening it.
- Sol's warm-up point is adopted: the v1 probe at `6731d5249` builds its first reduction inside the measured span;
  v2 warms first (§2).
- The "not measured" line (the Opus seat's decision 11) is adopted.

Made in the revision, where the cold passes offered a choice (reasons in `kb-revise/CHANGES.md`):
- Fixed-cost non-constancy: Fable's third cache size with its residual charged, not a new kernel; the unbounded
  remainder is stated (§3) and ε_flip printed.
- Arm repeatability: Opus's additive term, not an agreement check that would set every class UNDETERMINED.
- Meter gap (superseded by Round 3 R5): keep every call; bound each known missing duration by supplied power (§3).
- Agreement bar: one bar, 1% of the smallest printed δΔ, for every Δ and δΔ.
- Settle gap of 3 s around the stream and after fill/warm-up (§2), to keep delayed energy out of idle means.
