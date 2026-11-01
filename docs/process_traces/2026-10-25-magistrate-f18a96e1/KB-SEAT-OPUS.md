claude-opus-5-5

# Known-bytes stream test: the reading rule (design seat, Opus)

**Status: finished.** Blind design seat. Tree: JouleWise `6731d524907a9c9f77eb51a5380410a705ffc657`
(integrate/2026-10-24-416, the registered BYTES pass-1 tree). Read-only for JouleWise. No blinded or claim
data were opened. The only measured numbers used are non-claim check-session H records: the H export in this
repository at `8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b:bytes-h-desk-20261022/export/` and the H worked
numbers in `docs/process_traces/2026-10-22-forward/BAT-RULING.md` §9. The arithmetic is in
`known-bytes-rule/worked_example.py` next to this file (run: `python3 worked_example.py`).

**Summary.** A stream arm on its own cannot answer the question. A memory-bound reduction keeps the GPU busy
whether or not the memory controller is on the GPU rail, so the rail rises either way. The rule therefore
contrasts energy per byte when bytes come from DRAM with energy per byte when they come from cache. It uses the
same probe with no code change: one stream payload and two cache-resident payloads. The cache arms also remove
the per-dispatch overhead. The classes use only two thresholds: 0, and a per-byte level derived from the
registration's 1 J per-run attribution limit. A caveat prints beside a boundary's claim lines unless that
boundary's response is resolved and positive. The probe needs one small change: it must record its own idle
spans and the stack fields.

Where I disagree with the brief, the reason is given at that point. In short:
- (i) The test cannot tell the memory controller apart from GPU cores waiting on memory. It measures
  memory-traffic energy that appears in the rail.
- (ii) The class that sets the caveat is read on the **rails** boundary, because the claim lines use rails. The
  GPU rail gets its own class, which fills the §1 slot.
- (iii) A control arm is required, and it needs two cache sizes, not one.

---

## 1. Reported quantities

### 1.1 Measurement layout

**Arms.** All arms use the unchanged kernel of `scripts/bytes_stream_test.py`, which repeats
`mx.sum(data); mx.eval` on a `uint8` payload.

| Arm | Payload per dispatch | What it isolates |
|---|---|---|
| S (stream) | B bytes, far above cache (§4) | bytes from DRAM, plus GPU and dispatch work |
| C1 (cache, small) | Bc1 bytes, cache-resident | GPU and dispatch work with no DRAM traffic |
| C2 (cache, large) | Bc2 = 4 × Bc1, cache-resident | same as C1; the pair separates per-byte from per-dispatch energy |

**Order.** Six probe invocations, two per arm, in a palindrome: **S, C1, C2, C2, C1, S**. Each arm's two
invocations are symmetric about the session midpoint. Any drift that is linear in time therefore enters every
arm's sum at the same midpoint value. This is the null-quad (ABBA) reasoning of registration §5, applied to arms.

**Per invocation `i`** (from its receipt, after the §5 change):
- `start_ns`, `end_ns`: the streamed span, on CLOCK_MONOTONIC_RAW. T_i = (end_ns − start_ns) / 10⁹.
- `bytes_per_read`, `repeats` = N_i: the dispatch count.
- `idle_pre` and `idle_post`: two idle spans, each **57.6 s**. That is the registered pass-1 idle length,
  `sampling.idle_seconds` in every BYTES run config (e.g.
  `configs/campaigns/bytes_v1/qwen3-8b/01_decode_absolute/bytes-qwen3-8b-abs-r03.json:41`). The spans are
  stamped after allocation and fill and before the stream, and again after the stream, inside the same process
  with the payload still resident.

### 1.2 Boundaries and how each is integrated

| Boundary | Source and method |
|---|---|
| rails | CPU + GPU + ANE powermetrics energy (`cpu_power,gpu_power,ane_power`, 10 Hz: `power_hz: 10.0` in the same configs). Mapped and integrated over each span exactly as pass-1 rails are, under the session's operative timing bound (`joulewise/b6/calibration.py`; registration §7 table row 1). |
| GPU rail | The `gpu_power` series alone, by the same method. |
| DC input | KM003C meter energy plus the battery term E_b over the same span (registration §7, "Battery term"), through `km003c_parse.clock_fit` and `integrate`. |
| rest | DC input minus rails, formed per span before any averaging (§7). |

### 1.3 Arithmetic

All energies are in J. Bytes are converted to GB with 1 GB = 10⁹ bytes (`docs/contracts/bytes_tables.md`).

1. **Idle power**, per invocation and boundary β: P_idle,i = (P_pre + P_post) / 2. Each term is the mean power
   over its stamped idle span.
2. **Excess energy:** X_i = E_β[start_ns, end_ns) − P_idle,i × T_i.
3. **Per-dispatch excess for arm a:** x_a = Σ_i X_i / Σ_i N_i, summing over the arm's two invocations.
4. **Cache arms fit a line** x = α + γ_c × Bc:
   - γ_c = (x_C2 − x_C1) / (Bc2 − Bc1): energy per cache-sourced byte, in J/GB;
   - α = x_C1 − γ_c × Bc1: per-dispatch energy that does not depend on payload size (dispatch, launch, CPU).
5. **DRAM-sourced energy per byte:** γ_d = (x_S − α) / B.
6. **Reported quantity, per boundary:** Δ_β = γ_d − γ_c, in J/GB. This is the extra energy on boundary β per
   logical byte when the byte comes from DRAM instead of cache, with the kernel and dispatch work held fixed.

**Printed as description** (no class is read from these):
- the raw stream-arm figures the gate asked for, X_S / (Σ N_S × B), on rails, GPU rail, DC input and rest;
- the rails share f = Δ_rails / Δ_DC;
- the GPU-rail excess power contrast ΔP_GPU = X_S,GPU / T_S − X_C2,GPU / T_C2, with bound b/T for each term.

**Why the two-size control is needed (disagreement with a single control arm).** A single cache arm with the
same total bytes has B / Bc times more dispatches per byte. Its per-dispatch overhead would bias Δ downward by
about α / Bc. With the numbers in §6 that is about 0.17 J/GB on rails, larger than the effect being measured.
Two cache sizes measure α directly. Adding them costs no code: they are two more probe calls with a different
`--bytes`.

**What Δ can and cannot say (disagreement with "includes the memory controller").** When the GPU waits on DRAM
it spends more seconds per byte, at some power. Δ_GPU > 0 therefore shows that memory traffic costs energy on
the GPU rail. It cannot show whether that energy is the memory controller, the fabric, or GPU cores stalled on
memory. The BYTES claim lines need the mechanism-neutral answer: does the boundary they measure respond to bytes
read from memory? So that is what the class reads.

ΔP_GPU gives a one-sided hint about the mechanism. A GPU rail that draws *more* power streaming from DRAM than
streaming from cache at full activity is consistent with controller or fabric energy on that rail. A rail that
draws less says nothing either way. It is printed as description only.

### 1.4 Uncertainty bound

Per invocation and boundary, b_i is the sum (`math.fsum`) of the terms below. This is the registration's
convention for systematic terms: B is a sum (§7 step 4), not a quadrature.

| Term | rails / GPU rail | DC input | rest | Source |
|---|---|---|---|---|
| Edge placement at start_ns and end_ns | the rails anchor-shift bound, computed by the pass-1 function under the session's operative timing bound; plus the joint-edge interpolation bound, which is 0 for interval-support traces | u + v as in §7: u = (P_start + P_end) × (r_max + Δt), with Δt = 20 ms at 50 SPS (`km003c_parse.STEP_MS`); v from the battery polls in [edge, edge + τ) | rails term + DC term | registration §7 table and "Meter edge term u"; this is the "about 1 J per run" attribution limit (§12; `joulewise/tolerances.py` comment). H: rails anchor bound 0.28 to 0.63 J per run (median by model, H export `bound_E_clock_anchor_shift_bound_j`); u 6.0 to 8.5 J (BAT-RULING §9) |
| Baseline | T_i × (\|P_pre − P_post\| / 2 + 2 × se_idle) | same | same | half-difference: bounds any monotone drift of the baseline across the span. se_idle = √(v_pre + v_post) / 2, where v is the harvest's own `idle_variance_of_mean_w2` estimator for each span. The factor 2 is the two-standard-error convention the registration already uses (§9 coverage floor) |
| Meter resolution and sample interval | inside the anchor-shift bound | inside u (Δt) | — | §7 adds no separate resolution term at either boundary. Over spans of 400 to 600 s the per-sample quantisation averages out, and the edges are what u bounds |
| Dropped meter samples | — | none allowed: a gap inside a span makes that boundary unavailable for the invocation (`bytes.meter_gap` rule, §7) | as DC | §7 |

**Propagation through the arithmetic** (linear and worst-case, like B):
- δx_a = Σ b_i / Σ N_i
- δγ_c = (δx_C1 + δx_C2) / (Bc2 − Bc1)
- δα = δx_C1 + δγ_c × Bc1
- **δΔ = (δx_S + δα + |α|) / B + δγ_c**

The |α| / B term is the **dispatch-transfer term**. The fitted α comes from cache-sized dispatches. A 4 GiB
dispatch may carry different per-dispatch overhead (its reduction workspace and the number of passes scale
with size). The whole of α is therefore charged as a possible error. No factor is invented for this, and in §6
the term is the largest single part of the rails bound.

**Bias that is printed, not bounded.** Logical bytes are not DRAM bytes. The receipt counts logical `uint8`
reads (`scripts/bytes_stream_test.py:39–40`). If a fraction φ of the S arm's reads hit in cache, the measured
Δ = (1 − φ) × Δ_true. For a cyclic sequential scan of B larger than the cache, φ ≤ K / B, with K the cache knee
from §4. K / B is printed beside Δ, and the "excludes" test in §2 divides by (1 − K / B).

**Printed precision.** Each Δ, f and ΔP_GPU prints its half-width to 2 significant figures, and the estimate to
the same decimal place. This is registration §14's rule for H2 coefficients: a 2-significant-figure half-width
is at least 10 units of its last digit, so rounding moves a value by at most 5% of its half-width. JSON keeps
full precision. **Classes are decided on the full-precision values.**

**Agreement bar, if an independent recompute is made** (none is required). Agreement means every class matches
exactly and every Δ matches within **1% of its own δΔ**.
- In §6 the smallest half-width is 5.4 × 10⁻⁴ J/GB, so the bar is 5.4 × 10⁻⁶ J/GB.
- 10⁶ × float noise on Δ: 10⁶ × 2.2 × 10⁻¹⁶ × (83.8 W × 1200 s) / 396,417 GB = 5.6 × 10⁻¹¹ J/GB.
- The bar therefore sits between the two, as §12 requires.

---

## 2. Outcome classes and the caveat rule

For a boundary β, define the interval I_β = [Δ_β − δΔ_β, Δ_β + δΔ_β] and let φ = K / B.

**Validity of the contrast.** The test is valid when Δ_DC − δΔ_DC > 0: sourcing bytes from DRAM costs more
energy at the machine input than sourcing them from cache. If this fails, the control did not separate DRAM
traffic from GPU work. Every class below is then **UNDETERMINED (contrast not resolved)**. DC input encloses
rails and rest, so any real response on either boundary shows on DC.

**Stack check (§5).** If any probe-applicable stack field differs from the registered pass-1 stack, every class
is **UNDETERMINED (stack differs in: <fields>)**. The test then says nothing about pass-1's stack. Δ is still
printed.

**Classes**, read on rails (which sets the rails caveat), on the GPU rail (which fills the §1 slot), and on rest:

| Class | Condition | Meaning |
|---|---|---|
| INCLUDES (rails, GPU rail) or RESPONDS (rest) | Δ_β − δΔ_β > 0 | memory-traffic energy is resolved on β |
| EXCLUDES (rails, GPU rail) or ABSENT (rest) | (Δ_β + δΔ_β) / (1 − φ) ≤ ε₀ | any memory-traffic energy on β is below the per-run attribution limit, for every registered model |
| UNDETERMINED | otherwise | neither of the above is resolved |

**ε₀ = 1 J / (512 × b_max) = 4.9009 × 10⁻⁵ J/GB.**
- 1 J is the registration's per-run attribution limit (§12: "about 1 J per run"; `joulewise/tolerances.py`).
- 512 × b_max is the most bytes any registered decode phase reads: 512 × 39,852,331,520 bytes
  (Llama-70B, §4 table) = 20,404.4 GB.
- Below ε₀, memory-traffic energy on that boundary changes no run of any model by more than the instrument can
  attribute to a run.
- The bound must also be small enough for EXCLUDES to be reachable at all. In §6 it is not (δΔ_rails is
  5.4 × 10⁻⁴ J/GB, about 11 × ε₀). A Δ near 0 would then print UNDETERMINED, which is the honest reading. I give
  no smaller threshold, because none derives from the registration.

**"As registered."** §1 registers that the chip's share of memory-read energy appears in rails and the memory
chips' share in rest. So rails "responds as registered" when its class is INCLUDES, and rest when its class is
RESPONDS. DC input always responds when the test is valid, and its claim lines get no caveat: attribution
between boundaries cannot change an enclosing boundary.

**Caveat rule.** Exactly one line prints beside each of the rails and rest claim lines whenever that boundary's
class is not the registered one. Nothing prints when it is. The exact wording, with values filled from the
test record:

- rails, EXCLUDES:
  > Known-bytes stream test: rails energy per DRAM-sourced byte exceeded cache-sourced by Δ = {Δ} ± {δΔ} J/GB, below the 1 J-per-run attribution level ({ε₀} J/GB); memory-read energy appears only in rest, so rails lines here describe compute energy, not memory traffic.
- rails, UNDETERMINED:
  > Known-bytes stream test: the rails response to DRAM-sourced bytes is not resolved (Δ = {Δ} ± {δΔ} J/GB; {reason}); whether rails lines include memory-traffic energy is not established.
- rest, ABSENT:
  > Known-bytes stream test: rest energy per DRAM-sourced byte exceeded cache-sourced by Δ = {Δ} ± {δΔ} J/GB, below the 1 J-per-run attribution level ({ε₀} J/GB); memory-chip energy is not seen in rest at this test's resolution.
- rest, UNDETERMINED: the same as the rails line, with "rest" and "memory-chip energy".
- **Test not run before stage-1 unblinding:** beside the rails and rest lines:
  > Known-bytes stream test: not measured; the boundary attribution of memory-read energy (§1) is not established.

`{reason}` is one of: `contrast not resolved`, `stack differs in: <fields>`,
`interval spans 0 and the attribution level`.

**The §1 slot** (`⟦MAC: known-bytes stream test outcome⟧`) is filled with:
- the GPU-rail class, the rails class and the rest class;
- Δ ± δΔ for rails, GPU rail, DC input and rest;
- f, ΔP_GPU, K / B, the stack-check result and the receipt digests;
- and the sentence: "The test identifies memory-traffic energy on a rail, not whether it is the memory
  controller, the fabric or the GPU waiting on memory."

---

## 3. Control

**A control is required.** It is the two cache-resident arms C1 and C2 of §1. They use the same probe, kernel,
dispatch loop and process structure as S, and only the payload size changes. Two sizes are needed because one
size cannot separate per-byte cache energy from per-dispatch overhead (§1.3).

I considered a "compute without memory traffic" arm, such as an ALU loop. I rejected it: it changes the kernel,
so its GPU work per byte is not the stream kernel's. The cache arms keep the kernel exactly the same.

**What the control does not remove.** GPU clock (DVFS) state may differ between a DRAM-bound and a cache-bound
kernel. That difference is part of what Δ measures (it is energy spent because the bytes come from DRAM) and is
not a confound for the mechanism-neutral question. Thermal state is shared across arms by the palindromic
order. The OS thermal level over each span is printed, as pass-1 prints it.

---

## 4. Choosing B, Bc and N

**Cache size.** The repository does not record the M3 Max cache size. The only mention is "expert ≫ SLC" in
`docs/process_traces/2026-09-15-interactive-b0ae8462/20-rq-exploration-fable.md:53`. **Measure first** with a
timing-only knee scan:
- Run the existing probe with no power capture, at `--bytes 2^k` for k = 20 … 35 (1 MiB … 32 GiB).
- Choose repeats so each call lasts about 2 s, and run 3 calls per size.
- Throughput = bytes_read / duration_s from each receipt.
- The DRAM plateau is the throughput at 32 GiB, with spread taken as the range of its three calls.
- **K** = the smallest scanned size whose throughput lies within that plateau range.

The scan reads no energy, so it is not BYTES data. It takes about 2 minutes, outside the planned hour.

**Cache payloads.** Bc2 = K / 4 and Bc1 = Bc2 / 4.
- Bc2 = K / 4 keeps the payload, the reduction workspace and other resident lines clear of the knee.
- Bc1 = Bc2 / 4 makes Bc2 − Bc1 as large as possible, which sets δγ_c, while keeping both sizes on the plateau.
- If a cache arm still leaks to DRAM, γ_c rises and Δ shrinks. The error goes toward UNDETERMINED, never toward
  INCLUDES.

**Stream payload.**
- B = max(4 GiB, the smallest power of two ≥ 64 × K) bytes.
- 4 GiB = 4,294,967,296 bytes is inside the fit set's range of bytes per pass. It sits beside Qwen3-8B-4bit's
  b = 4,597,412,096 (§4 table), so the test reads DRAM in the regime the fit lines are drawn through.
- 64 × K caps the printed cache-hit bias φ = K / B at 1/64 (1.6%), which cannot move a class at the size of Δ in
  §6. It leaves 128 GB machine memory far from the limit.

**Repeats N.** Plan the hour as:
- 12 idle spans × 57.6 s = 691.2 s;
- about 60 s for six allocations, fills and process exits (**measure first** in the knee scan);
- leaving about 2,850 s of streaming: S 2 × 600 s, C1 2 × 400 s, C2 2 × 400 s = 2,800 s.

Per invocation, N_a = floor(T_a / t_disp,a), with t_disp,a = duration_s / repeats measured at that exact payload
in the knee scan. No bandwidth is guessed, as the probe's README asks.

S is longest because δx_S is divided by B only once, while the cache arms set δγ_c through the small difference
Bc2 − Bc1 (§1.4). With the §6 numbers, N_S = 46,149 per invocation at 4 GiB and 331.6 GB/s, and N_C1 and N_C2
are about 6.85 × 10⁶ and 4.79 × 10⁶ per invocation (assumed 50 µs dispatch, 1 TB/s cache throughput).

**Is the bound small against the quantity?** S moves 396,417 GB above an idle rails draw of 0.05 W, for an
excess of 37,676 J on rails. In §6, δΔ_rails / Δ_rails is 0.8% and δΔ_DC / Δ_DC is 1.0%. The largest terms are:
- |α| / B (3.3 × 10⁻⁴ J/GB on rails);
- δγ_c, which is set by the baseline term over the cache arms.

---

## 5. The C4 stack gap

The governed stack has eleven fields (`joulewise/identity_pins.py:64–76`). The registered pass-1 values are in
`configs/b6/registration/identity_pins.json` (`stack_identity`) and `configs/bytes/identity_pins.json`
(`runtime_versions`). Five model-specific fields do not apply to a probe that loads no model.

**Smallest change: one `stack` object in the probe receipt.** Ten lines in `scripts/bytes_stream_test.py`, no new
module:

| Receipt field | Value source (same function pass-1 uses) | Compared to registered |
|---|---|---|
| `os_version` | `platform.platform()` (pass-1: `joulewise/bundle.py:1106` → `identity_pins.py:360`) | `stack_identity.os_version` (`macOS-26.6.2-arm64-arm-64bit-Mach-O`) |
| `hardware_unit.machine` | `platform.machine()` (`bundle.py:1107`) | `hardware_unit.machine` (`arm64`) |
| `hardware_unit.device` | the chain extension's `hardware_target.id`, passed as `--hardware-id` (pass-1: config `hardware_target.id`) | `hardware_unit.device` (`macbook_m3_max`) |
| `runtime_version` | `{"name": "mlx", "version": mx.__version__}` | `runtime_version.version` (`0.31.2`) |
| `kernel_library` | the same source as pass-1 `prepare.kernel_library`, else `"unavailable"` | `kernel_library` (`unavailable`) |
| `packages`, `python` | `importlib.metadata.version` over `joulewise.flags.collect.RUNTIME_PACKAGES` and `platform.python_version()`, i.e. what `runtime_versions` returns | `configs/bytes/identity_pins.json` `/runtime_versions` (mlx 0.31.2, mlx-metal 0.31.2, …, python 3.13.1) |
| `git_commit` | `git rev-parse HEAD` of the non-claim checkout | printed, not compared (the checkout differs by design) |
| `model_artifact_sha256`, `quantization`, `tokenizer_identity`, `sampler_output_policy`, `batching_concurrency_policy` | `"not_applicable"` | not compared |

The other two governed fields come from the concurrent capture, not the probe. They are taken at harvest from
the capture's own record, as pass-1's are:
- `telemetry_backend`: `powermetrics`;
- `measurement_boundary_label.rails`: the samplers `cpu_power, gpu_power, ane_power`.

**Same change, idle stamps.** Add `--idle-s` (57.6) and record `idle_pre_start_ns`, `idle_pre_end_ns`,
`idle_post_start_ns` and `idle_post_end_ns` on the same CLOCK_MONOTONIC_RAW. The probe sleeps through each span
after `mx.synchronize()`. Without these stamps the idle baseline cannot be computed from the receipt and traces
alone: the pre-start interval holds the 4 GiB fill, which is not idle.

The receipt `schema_version` becomes `joulewise.bytes_stream.v2`. The harvest compares the applicable fields
exactly and prints the differing field names into the stack check of §2.

---

## 6. Worked example

**Illustration only. This is not a prediction.** Inputs come from H's non-claim records where a record exists.
Values marked *assumed* have no record and stand in for what the test measures. `worked_example.py` reproduces
every number below.

**Inputs from records:**
- **S-arm rails power:** 31.45 W, the Qwen3-8B-4bit median rails decode power in H (223.22 J / 7.098 s, H export
  `phase_decode_j`, `dur_decode_s`). Its b (4.6 GB) is next to B.
- **S throughput:** 331.6 GB/s = b × 512 / T for 8B-4bit (manifest b; H decode T). It is inside the pilot's
  209 to 344 GB/s dense range (`docs/design/bytes_pilot/SUMMARY.md:39`).
- **S-arm rest power:** 52.39 W = 577.210005 J / 11.017813 s (Qwen3.5-122B check-r01, BAT-RULING §9).
- **Idle power:**
  - rails 0.051 W, se 0.011 W (8B-4bit H medians of `idle_power_w` and √`idle_variance_of_mean_w2`);
  - DC 2.386 W = (6101.072862 − 5967.417892) J / 56.018813 s (70B check-r01, BAT-RULING §9).
- **Edges:**
  - rails anchor-shift bound 0.5388 J per invocation (8B-4bit H median);
  - u = 2 × 83.84 W × (0.017762 + 0.020) s = 6.33 J (r_max from H, §7);
  - v = 0, since 84 W is below the 140 W adapter.

**Assumed:**
- DC idle se 0.05 W;
- drift half-difference 0.002 W on rails and 0.05 W on DC;
- dispatch fixed time 50 µs;
- cache throughput 1 TB/s;
- excess power during the cache arms: 28.0 W rails, 25.0 W rest;
- knee K = 64 MiB, so Bc1 = 8 MiB, Bc2 = 32 MiB and B = 4 GiB.

**Carried through §1:**

| | rails | DC input | rest |
|---|---|---|---|
| α (mJ per dispatch) | 1.4000 | 2.6500 | 1.2500 |
| γ_c (J/GB) | 0.02800 | 0.05300 | 0.02500 |
| γ_d (J/GB) | 0.09472 | 0.24594 | 0.15123 |
| **Δ ± δΔ (J/GB)** | **0.06672 ± 0.00054** | **0.1929 ± 0.0020** | **0.1262 ± 0.0019** |
| part of δΔ that is \|α\|/B | 3.3 × 10⁻⁴ | 6.2 × 10⁻⁴ | 2.9 × 10⁻⁴ |

**Carried through §2:**
- **Validity:** Δ_DC − δΔ_DC = 0.1909 > 0, so the contrast is resolved.
- **Stack:** assumed identical, so the check is clear.
- **rails:** 0.06617 > 0, so the class is INCLUDES, the registered outcome. No caveat prints.
- **rest:** 0.1243 > 0, so the class is RESPONDS, the registered outcome. No caveat prints.
- **GPU rail:** not separable in these inputs. H exports rails totals only. In the test the GPU series is read
  directly, and its class fills the §1 slot.
- **Description:** f = 0.35 (the rails share of memory-traffic energy); K / B = 0.0156.

**For contrast:** had Δ_rails come out at 0.0003 ± 0.00054 J/GB, the interval [−0.00024, 0.00084] would span 0,
and its upper end, 0.00084 / (1 − 0.0156) = 0.00085, is far above ε₀ = 0.000049. The rails class would be
UNDETERMINED, and the rails lines would carry:

> Known-bytes stream test: the rails response to DRAM-sourced bytes is not resolved (Δ = 0.00030 ± 0.00054 J/GB; interval spans 0 and the attribution level); whether rails lines include memory-traffic energy is not established.

---

## 7. Decisions I made

None of these changes which data count or any printed claim number. Each adds or words the one printed line, so
I mark none NEEDS_RULING.

1. **Contrast, not stream alone.** The reported quantity is the DRAM-minus-cache energy per byte Δ, with two
   cache sizes to remove dispatch overhead. Stream-only per-byte energies print as description.
2. **The class reads memory-traffic energy, not "the memory controller".** The probe cannot separate the
   controller, the fabric and GPU wait. ΔP_GPU prints as a one-sided description.
3. **The rails class sets the rails caveat; the GPU-rail class fills the §1 slot.** The claim lines use rails
   (CPU + GPU + ANE).
4. **DC input gets no caveat.** Its Δ decides whether the test is valid.
5. **Two thresholds only: 0 and ε₀ = 1 J / (512 × b_max).** The 1 J attribution limit and the largest manifest b
   are registered values. No effect-size threshold was invented.
6. **Idle-subtracted basis, with a local pre/post baseline per invocation** of the registered 57.6 s each, and a
   baseline term of half-difference plus 2 se. The 2 is the registration's own two-standard-error convention (§9).
7. **Worst-case linear propagation, including the whole |α| / B** as the dispatch-transfer term. This follows the
   registration's summed B.
8. **Palindromic order S C1 C2 C2 C1 S, and the hour split 1,200 / 800 / 800 s.** The split is a planning choice;
   N follows from measured dispatch times.
9. **B = max(4 GiB, the next power of two ≥ 64K); Bc2 = K / 4; Bc1 = Bc2 / 4; K from a timing-only knee scan.**
   The 4 GiB matches the fit-set bytes. The factors are planning choices whose effects are printed (K / B) or
   push the outcome toward UNDETERMINED.
10. **A stack difference in any applicable governed field makes every class UNDETERMINED,** with the field names
    printed. It is not merely a note.
11. **If the test has not run before stage-1 unblinding, a "not measured" line prints** beside the rails and rest
    lines. The texts do not say what prints in that case. This keeps §19's "carries that outcome" true without
    adding a gate.
12. **Precision:** §14's H2 rule (half-width to 2 significant figures). The agreement bar for an optional
    independent recompute is 1% of δΔ.
