# BYTES known-bytes stream test: the reading rule (DRAFT)

**Status.** Draft, written 2026-10-25 by magistrate activation f18a96e1 (Opus 5.5, lead) from two blind design
seats (Sol 6.1 xhigh and Opus 5.5; reports `docs/process_traces/2026-10-25-magistrate-f18a96e1/KB-SEAT-SOL.md`
and `KB-SEAT-OPUS.md`, brief `KB-BRIEF.md`). It answers registration-gate finding 4 (Opus,
`docs/process_traces/2026-10-24-magistrate-7209d1b0/REGGATE-OPUS.md`): before the test runs, say which quantity
is reported and which outcome prints a caveat. It binds once a cold pass (Fable 5.1 and Opus 5.5, blind,
executing) admits it, and it must bind **before the test runs**. The test itself runs after pass-1 collection and
before stage-1 unblinding (`docs/registrations/bytes_pack_v1.md` §19, P0 ruling 9). Nothing here changes a
collected number, an exclusion or an estimator: the outcome only adds lines beside the claim lines and fills the
§1 slot.

## 0. The question, and what this test cannot answer

The registration measures energy at two boundaries (§1): **rails** (CPU + GPU + neural-engine energy from
`powermetrics`) and **DC input** (the KM003C meter on the charging cable plus battery assist); **rest** is DC
input minus rails. `powermetrics` reports no memory (DRAM) channel. So when a model reads its weights from
memory, part of that energy may show in rails (if the circuits that move bytes are on a reported rail) and part
only in rest (the memory chips themselves). §1 registers the expectation: the chip's share appears in rails, the
memory chips' share in rest.

The test streams a known number of bytes through the GPU and asks whether each boundary's energy rises **because
the bytes came from DRAM**. A stream on its own cannot answer that: reading bytes keeps the GPU busy, so the GPU
rail rises whether or not the memory controller is on it. The test therefore compares two ways of doing the same
GPU work, one whose bytes come from DRAM and one whose bytes come from on-chip cache (§2). The difference is
**memory-traffic energy**: the extra energy per byte when the byte comes from DRAM.

Both seats agreed on the limit, and it is adopted: a positive difference on the GPU rail shows that memory
traffic costs energy on that rail. It cannot say whether the energy is the memory controller, the on-chip fabric,
or GPU cores stalled waiting on memory. No outcome of this test establishes "the GPU rail does not include the
memory controller". The classes below are worded accordingly.

## 1. The probe and its arms

The probe is `scripts/bytes_stream_test.py`: it repeats `mx.sum(data); mx.eval(...)` on a `uint8` payload of
`--bytes` bytes, `--repeats` times. Each repeat is one **dispatch**. The receipt counts **logical bytes**
(payload bytes × repeats), not a hardware DRAM byte count.

Three arms use this same kernel unchanged, only the payload size differs:

| Arm | Payload per dispatch | Where the bytes come from |
|---|---|---|
| S (stream) | B, far above the cache knee K | DRAM |
| C1 (cache, small) | Bc1 = Bc2 / 4 | cache |
| C2 (cache, large) | Bc2 = K / 4 | cache |

*Why two cache sizes (Opus seat, adopted over the single cache arm).* Each dispatch costs some energy that does
not depend on its size (launch, synchronization, CPU work). A cache arm moving the same total bytes in smaller
payloads makes many more dispatches, so its per-byte energy would carry more of that fixed cost. With two sizes
the fixed cost per dispatch, α, and the per-byte cache cost, γ_c, are both solved for (§3). Sol's alternative, one
kernel with an address-period parameter that holds dispatch structure fixed, would need new kernel code; the
two-size design needs none, so it is chosen.

**Order.** Six probe calls in a palindrome, **S, C1, C2, C2, C1, S**. Each arm's two calls sit symmetrically
about the session midpoint, so a drift linear in time adds the same amount to every arm (the ABBA reasoning of
§5 of the registration).

**Cache knee K: measure first.** The repository records no cache size for this M3 Max. Before the measured hour,
with no energy capture: run the probe at `--bytes 2^k` for k = 20 to 35 (1 MiB to 32 GiB), three calls per size,
repeats chosen so each call lasts about 2 s. Throughput is bytes read / duration from each receipt. The DRAM
plateau is the throughput at 32 GiB, with spread equal to the range of its three calls. K is the smallest scanned
size whose throughput lies inside that range. The scan reads no energy and is not BYTES data.

**Sizes.** Bc2 = K / 4 and Bc1 = Bc2 / 4, so both cache arms stay clear of the knee. B = max(4 GiB, the smallest
power of two ≥ 64 K). 4 GiB sits beside Qwen3-8B-4bit's bytes per pass (4,597,412,096, §4 table), inside the fit
set's range. 64 K caps the cached fraction of S's reads at K / B ≤ 1/64 (§3, bias).

**Repeats.** Each call's repeats N = floor(T_arm / t_dispatch), with t_dispatch = duration / repeats measured at
that exact payload in the knee scan. Planned split of the hour: twelve idle spans of 57.6 s (691.2 s), about 60 s
of allocation and exits (measured in the scan), S 2 × 600 s, C1 2 × 400 s, C2 2 × 400 s. These are planning
choices, not thresholds; the arithmetic uses the actual stamped spans.

## 2. The receipt change (one small code change, before the test)

The receipt gains schema `joulewise.bytes_stream.v2` with:

1. **Idle spans.** `--idle-s 57.6` (57.6 s is `sampling.idle_seconds` of every pass-1 BYTES run config). After
   allocation, fill and `mx.synchronize()`, the probe sleeps 57.6 s, then streams, then sleeps 57.6 s with the
   payload still resident. It stamps `idle_pre_start_ns`, `idle_pre_end_ns`, `idle_post_start_ns`,
   `idle_post_end_ns` on CLOCK_MONOTONIC_RAW, the clock of `start_ns` and `end_ns`. Without these, the baseline
   cannot be computed from the receipt and traces alone (the time before `start_ns` holds the fill, which is not
   idle). Also warm the reduction once before `start_ns`, so the first measured dispatch is not a compile.
2. **Stack object.** From the same functions pass 1 uses: `os_version` (`platform.platform()`),
   `hardware_unit.machine` (`platform.machine()`), `hardware_unit.device` (passed in, from the checkout's
   `hardware_target.id`), `runtime_version` (MLX version), `kernel_library` (as pass-1 prepare records it, else
   `unavailable`), `python` and `packages` (what `joulewise.flags.collect.runtime_versions` returns), and the
   checkout's `git_commit` (printed, not compared). `model_artifact_sha256`, `quantization`, `tokenizer_identity`,
   `sampler_output_policy` and `batching_concurrency_policy` are `not_applicable`. `telemetry_backend` and the
   rails boundary label come from the concurrent capture's record at harvest, as in pass 1.

## 3. The reported quantity and its bound

**Boundaries.** rails (CPU + GPU + ANE), the GPU rail alone, DC input, and rest. Each is integrated over a stamped
span exactly as pass 1 integrates it: rails by native interval support under the session's operative timing bound
(registration §7); DC input by the meter integrator plus the battery term E_b (§7, "Battery term"); rest = DC − rails
per span, before any averaging. A meter gap inside a span makes DC and rest unavailable for that call (§7's
`bytes.meter_gap` rule).

**Arithmetic, per boundary β** (energies in J; 1 GB = 10⁹ bytes):

1. Idle power of call i: P_idle,i = (P_pre + P_post) / 2, each the mean power over its stamped idle span.
2. Excess energy of call i: X_i = E_β[start_ns, end_ns) − P_idle,i × T_i, with T_i the stamped span in seconds.
3. Excess per dispatch of arm a: x_a = Σ X_i / Σ N_i over the arm's two calls.
4. Cache line through C1 and C2: γ_c = (x_C2 − x_C1) / (Bc2 − Bc1) (J per cache-sourced byte) and
   α = x_C1 − γ_c × Bc1 (J per dispatch, independent of size).
5. DRAM-sourced energy per byte: γ_d = (x_S − α) / B.
6. **Reported quantity: Δ_β = γ_d − γ_c**, in J/GB: the extra energy on β per logical byte read from DRAM rather
   than cache, with the kernel and per-dispatch work held fixed.

**Bound, per call** (summed, not in quadrature, as the registration sums its systematic terms in §7 step 4):

| Term | rails and GPU rail | DC input | rest |
|---|---|---|---|
| Edges at start_ns and end_ns | the pass-1 anchor-shift bound under the session's operative timing bound (H: 0.28 to 0.63 J per run); interpolation term 0 for interval support | u + v of §7: u = (P_start + P_end)(r_max + Δt), Δt = 20 ms at 50 samples/s; v from battery polls in [edge, edge + τ) | rails + DC |
| Baseline | T_i × (\|P_pre − P_post\| / 2 + 2 se_idle), se_idle = √(v_pre + v_post) / 2 from the harvest's `idle_variance_of_mean_w2`; the half-difference bounds a monotone drift, the 2 is §9's two-standard-error convention | same | same |

**Propagation** (worst case, linear): δx_a = Σ b_i / Σ N_i; δγ_c = (δx_C1 + δx_C2) / (Bc2 − Bc1);
δα = δx_C1 + δγ_c × Bc1; **δΔ = (δx_S + δα + |α|) / B + δγ_c**. The |α| / B term charges the whole per-dispatch
cost as possible error, because a 4 GiB dispatch may carry a different fixed cost from a cache-sized one; no
factor is invented for it.

**Bias, printed beside Δ.** If a fraction φ of S's reads hit in cache, Δ measured = (1 − φ) Δ true. For a cyclic
scan of B above the cache, φ ≤ K / B, printed. A cache arm that leaks to DRAM raises γ_c and lowers Δ: errors run
toward "not resolved", never toward "resolved".

**Printed precision.** Δ prints its half-width to 2 significant figures and the estimate to the same decimal
place (§14's rule). Classes are decided on full-precision values.

**Agreement bar** for an independent recompute, if one is made: every class identical and each Δ within 1% of its
own δΔ. That bar sits between 10⁶ × float noise and 1% of the smallest printed half-width (worked example:
5.6 × 10⁻¹¹ ≤ 5.4 × 10⁻⁶ J/GB).

## 4. Validity, classes and the printed lines

**Validity.** The contrast is valid only when Δ_DC − δΔ_DC > 0. DC input encloses rails and rest, so a real
memory-traffic cost must show there; if it does not, the control failed to separate DRAM traffic from GPU work.
**Stack check.** If any compared stack field (§2 item 2) differs from the registered pass-1 stack
(`configs/b6/registration/identity_pins.json` `stack_identity`, `configs/bytes/identity_pins.json`
`runtime_versions`), the result does not transfer to pass 1. In either case every class is UNDETERMINED with the
reason, and Δ still prints.

**Classes**, read separately on rails, on the GPU rail and on rest, with I = [Δ − δΔ, Δ + δΔ] and φ = K / B:

| Class | Condition | Meaning |
|---|---|---|
| RESOLVED | Δ − δΔ > 0 | memory-traffic energy is resolved on this boundary |
| BELOW ATTRIBUTION LEVEL | (Δ + δΔ) / (1 − φ) ≤ ε₀ | any memory-traffic energy on this boundary is too small to move any registered model's run by the instrument's per-run attribution limit; this does **not** say the controller is off this rail |
| NOT RESOLVED | otherwise | neither is shown; the upper limit Δ + δΔ prints |

**ε₀ = 1 J / (512 × b_max) = 4.9009 × 10⁻⁵ J/GB.** 1 J is the registration's per-run attribution limit (§12);
512 × b_max is the most bytes any registered decode phase reads, 512 decode tokens × 39,852,331,520 bytes per
token (Llama-3.3-70B, §4 table) = 20,404.4 GB. This is Opus's threshold; Sol argued no threshold can show
exclusion, which is why the class is named for what it shows (immaterial at the instrument's resolution), not
"excludes". It may be unreachable at the test's resolution (worked example: δΔ_rails is about 11 ε₀); then a
near-zero Δ reads NOT RESOLVED, which is the honest reading.

**What "responds as registered" means (§19).** §1 expects the chip's share in rails and the memory chips' share in
rest. So rails responds as registered when its class is RESOLVED, and rest when its class is RESOLVED. DC input
needs no caveat: moving energy between the inner boundaries cannot change the enclosing one.

**Printed lines.** One line beside the rails claim lines and one beside the rest claim lines, whenever that
boundary's class is not RESOLVED (values filled from the test record):

- BELOW ATTRIBUTION LEVEL: `Known-bytes check: {boundary} energy per DRAM-sourced byte exceeded cache-sourced by {Δ} ± {δΔ} J/GB, below the 1 J-per-run attribution level ({ε₀} J/GB); {boundary} lines here carry no resolvable memory-traffic energy.`
- NOT RESOLVED: `Known-bytes check: the {boundary} response to DRAM-sourced bytes is not resolved ({Δ} ± {δΔ} J/GB, upper limit {Δ+δΔ} J/GB); whether {boundary} lines include memory-traffic energy is not established.`
- UNDETERMINED: `Known-bytes check: {boundary} memory-traffic attribution is undetermined ({reason}).` with reason `contrast not resolved` or `stack differs in: <fields>`.
- Test not run before stage-1 unblinding: beside the rails and rest lines, `Known-bytes check: not measured; the boundary attribution of memory-read energy (§1) is not established.`

When a boundary is RESOLVED, nothing prints beside its claim lines.

**The §1 slot** is filled with the three classes (rails, GPU rail, rest), Δ ± δΔ for rails, GPU rail, DC and rest,
K / B, the stack-check result, the receipt digests, and the sentence: "The test identifies memory-traffic energy on
a boundary, not whether it is the memory controller, the fabric or the GPU waiting on memory."

**Description only** (no class reads them): the stream arm's raw excess per logical byte on each boundary; the
rails share f = Δ_rails / Δ_DC; the GPU-rail excess-power contrast between S and C2.

## 5. Worked example (illustration, not a prediction)

From `kb_worked_example_opus.py` beside the seat reports (inputs from H's non-claim records where one exists,
otherwise marked assumed there: K = 64 MiB, so Bc1 = 8 MiB, Bc2 = 32 MiB, B = 4 GiB; cache throughput 1 TB/s; S at
331.6 GB/s for 1,200 s, 396,417 GB):

| | rails | DC input | rest |
|---|---|---|---|
| α (mJ per dispatch) | 1.4000 | 2.6500 | 1.2500 |
| γ_c (J/GB) | 0.02800 | 0.05300 | 0.02500 |
| γ_d (J/GB) | 0.09472 | 0.24594 | 0.15123 |
| Δ ± δΔ (J/GB) | 0.06672 ± 0.00054 | 0.1929 ± 0.0020 | 0.1262 ± 0.0019 |

Validity: 0.1929 − 0.0020 > 0. Rails: 0.06672 − 0.00054 > 0, RESOLVED, nothing prints. Rest: RESOLVED, nothing
prints. Had Δ_rails been 0.00030 ± 0.00054, I = [−0.00024, 0.00084] spans 0 and 0.00084 / (1 − 1/64) = 0.00085 >
ε₀ = 0.000049, so rails would be NOT RESOLVED and carry the second line.

## 6. Decisions the lead made between the seats

- Contrast design: Opus's unchanged kernel with two cache sizes and the |α|/B term, over Sol's single matched cache
  arm (no new kernel code).
- Classes: Opus's two thresholds (0 and ε₀), with the lower class renamed from "EXCLUDES" to "BELOW ATTRIBUTION
  LEVEL" and NOT RESOLVED printing its upper limit, per Sol's point that non-detection cannot show exclusion.
- Idle: 57.6 s spans per call (the registered pass-1 idle length), not Sol's 300 s, because the baseline is
  per call and the palindrome cancels linear drift across calls.
- Sol's extra meter terms (label offset over Δ + RTT, digital resolution of one encoded unit) are not added: §7
  bounds the edges with u and adds no resolution term, and this test inherits §7 rather than widening it.
- Sol's warm-up point is adopted (the probe now builds its first reduction inside the span).
- The "not measured" line (Opus decision 11) is adopted.
