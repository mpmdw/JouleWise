# BYTES known-bytes stream test: the reading rule (DRAFT, matched geometry)

**Status.** Matched-geometry revision pending cold review and the lead's admission.
The preceding design was admitted 2026-10-30 at `559197821`; this revision replaces that design
prospectively and must be admitted before the test runs. Source: the lead's matched-geometry rulings,
`kb-knee-council/build/RULE-REVISION.md` Part B and its `NOTES.md` (writer seat 2026-10-30),
against the admitted draft at `79de7be49`.

**Prior-design history.** The preceding revision was installed 2026-10-28 in magistrate activation
39206674. Originally drafted 2026-10-25 in activation f18a96e1 from two blind design seats
(`docs/process_traces/2026-10-25-magistrate-f18a96e1/KB-SEAT-SOL.md` and `KB-SEAT-OPUS.md`, brief `KB-BRIEF.md`).
Reconciler: Opus 5.5, JouleWise-data `claude/kb-revise-opus` at `0609bcc0caf941fd68c36fccea323f34c3951730`,
`kb-revise/CHANGES.md`. Cold reports: Fable 5.1, `claude/kb-cold-fable` at
`39398e572ea0943edc77f0981d82e3be32311a32`, and Opus 5.5, `claude/kb-cold-opus-gteliv` at
`ecd46c1124000dbfbc51b475068661ceefb62a1f`, both `kb-cold/REPORT.md` in JouleWise-data, both
ADMIT-WITH-CORRECTIONS. These are independent executing reviews by models that did not write the draft.
The lead has adopted CHANGES.md option (a) for Fable 1: the disclosure, ε_flip and per-arm GPU frequency and
residency remain; neither a new kernel nor a leverage model is adopted. **Admitted 2026-10-30 by the lead (magistrate activation 4e748ac1) at `559197821`**, after nine reader rounds. The last blind delta reviews (Sol 6, Opus 5) found no defect beyond those fixed in round 9. The lead re-ran Opus 5's `p8_major_cli.py` and `p8_grid.py` at `559197821`: every shape that printed a smaller bound now ends UNDETERMINED with its reason and no interval, and the worked output is bit-identical to round 8. That admission applied to the preceding design.

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

The test streams a known number of bytes through the GPU and asks whether each boundary's energy rises with
**memory traffic**. A stream on its own cannot answer that: reading bytes keeps the GPU busy, so the GPU
rail rises whether or not the memory controller is on it. The test therefore compares two ways of doing the same
GPU work, rotating addresses intended to read DRAM and repeating addresses intended to read on-chip cache (§1).
The difference is **memory-traffic energy** per logical byte. It can include address translation and DRAM row
locality as well as byte source: the memory controller, the on-chip fabric, the GPU's time stalled waiting on
memory, and the GPU clock state (DVFS, dynamic voltage and frequency scaling). The timing check resolves an
address-reuse contrast; it does not isolate energy per DRAM-sourced byte.

Both design seats agreed on the limit, and it is adopted: a positive difference on the GPU rail shows that memory
traffic costs energy on that rail. It cannot say whether the energy is the memory controller, the fabric, or GPU
cores stalled waiting on memory. On rest it cannot separate the memory chips from power-conversion loss and fan
energy that rise with the rails' own rise. No outcome of this test establishes "the GPU rail does not include the
memory controller". The classes below are worded accordingly.

*Expected outcome on rails.* In the matched diagnostic (§5), a 32 MiB dispatch whose bytes come from DRAM took
52.4 µs longer than the same dispatch re-reading bytes already in cache: 308.6 against 256.2 µs. That is about
1.6 ps more per byte (52.4 µs / 33,554,432 B). The GPU draws power above idle while it waits. So rails RESOLVED (§4)
is close to guaranteed by stall time alone, and carries little information about the memory controller. The same
holds for rest through conversion loss (§4, "What responds as registered means").

## 1. The probe, its arms and its payload size

**Terms.** The probe is `scripts/bytes_stream_test.py`. It reduces `uint8` arrays with MLX (Apple's array library)
by `mx.sum(view); mx.eval(...)`. One such reduction, sent to the GPU and waited for, is a **dispatch**.
- The **ring** is one `uint8` array of W bytes, allocated as shape (Q, b) and filled before measurement.
- A **view** is one row, `ring[i]`: b contiguous bytes starting at byte i·b. MLX's slice shares the ring's memory and
  copies nothing.
- A **sweep** is Q consecutive dispatches that read views 0, 1, …, Q−1 in that order.
- The **receipt** is the JSON record of one probe call. It counts **logical bytes** (b × dispatches), not a hardware
  DRAM byte count.

**The two arms.** Both arms run the identical Python loop over a list of Q view references. The k-th dispatch reduces
`views[k mod Q]`, and every call allocates the same ring.

| Arm | List of Q references | Intended byte source |
|---|---|---|
| R (rotate) | the Q distinct views 0, …, Q−1 | DRAM: each view is next read a whole ring later |
| C (repeat) | Q references to view 0 | cache: the same b bytes are re-read every dispatch |

The two arms have the same payload size b, dtype, shape (b,), expression and launch geometry, the same allocation, and
the same Python indexing. Only address reuse differs.

*Why the matched design is chosen.* The admitted design compared a 4 GiB stream with cache arms of 4–16 MiB. Under
MLX 0.31.2 those payloads run different GPU launches (G below). The cache line fitted in one launch was subtracted
from a stream measured in the other, and nothing in §3 bounded the difference. Fable's alternative was a
row reduction with a fixed row length, so that every payload size shares one per-row geometry. It changes the kernel
expression for every arm, needs its own scan to choose the row length, and still compares arms of different sizes.
The matched design changes only which addresses are read: the expression stays `mx.sum` over a contiguous view.
And because R and C have equal size, the per-dispatch fixed cost cancels exactly (§3) rather than being estimated
and carried across sizes. Fable's fixed-row kernel is not adopted.

**Launch geometry: an explicit, source-pinned input.** A **threadgroup** is the GPU's unit of parallel work. The
reduction's **launch geometry** is the number of threadgroups it uses. In MLX v0.31.2,
`mlx/backend/metal/reduce.cpp`, function `all_reduce_dispatch`, the contiguous all-reduce branches on
`in.nbytes() <= (1 << 26)`:
- at and below that size it uses 32 × REDUCE_N_READS = 128 first-pass threadgroups and a 32-thread second pass (the
  **small launch**);
- above it, 4,096 threadgroups and a 1,024-thread second pass (the **large launch**).

So **G = 2^26 bytes**. G is valid only for the build it was read from: `packages.mlx` = `packages.mlx-metal` =
`runtime_version.version` = 0.31.2. A row view `ring[i]` of a row-contiguous (Q, b) array is itself contiguous
(pinned `mlx/backend/common/slicing.cpp`), so it takes this all-reduce path with `in.nbytes()` = b.

**Geometry check.** It runs on every receipt, of the check and of the hour. It passes only when all of these hold:
- the receipt's `view_nbytes` equals b;
- `ring_shape` = [W/b, b] and `dtype` = `uint8`;
- `launch_side` = `small`, which requires b ≤ G;
- the receipt's MLX versions equal the build G was read from.

Since R and C have identical b, any check that passes puts both arms on the same side of G. The check fails if they
were not. A failure names the field.

**Ring size W, and the bound on R's cached fraction.** R is meant to read DRAM, but some of its bytes might still be
in cache. Let K_c be the largest number of bytes any on-chip cache between the GPU and DRAM can hold.
- *Cyclic-sweep bound (holds for any replacement policy).* Take any byte x read in sweep k. If that read is a cache
  hit, x stayed resident from its read in sweep k−1 to its read in sweep k. That interval contains the first
  dispatch of sweep k. At that instant at most K_c bytes are resident. So at most K_c of the W bytes in a sweep hit,
  and R's cached fraction is φ ≤ K_c / W over whole sweeps. More generally, for N dispatches,
  φ ≤ K_c ⌈N/Q⌉ / (N b).
- *Capacity premise.* The admitted design covered caches of K ≤ 512 MiB only: it refused whenever 64K > s_max, with
  s_max = 32 GiB, its largest scanned allocation. This revision keeps that same envelope as a stated premise,
  **K_c ≤ K_cap = W/64**. It also keeps the admitted 1/64 cached-fraction cap, now applied to the working set:
  **W = 64 × 512 MiB = 2^35 bytes (32 GiB)**, so φ_U = K_cap/W = 1/64 for whole sweeps. The admitted scan already
  allocates 2^35 bytes. The premise is not tested by this rule. §3 ("Bias") and `NOTES.md` say what it supports and
  what a breach does.
- *Allocation.* Allocate as `mx.ones((Q, b), dtype=mx.uint8)` with Q = W/b. Both axes stay below 2^31 for every b on
  the ladder (Q ≤ 2^16 and b ≤ 2^26), so the per-axis allocation limit fixed at `79de7be49` is not reached.
- *Payload content.* `mx.ones` is constant data, which minimises DRAM-bus toggle energy. Relative to real model
  weights, this biases Δ toward zero. It weakens the NOT RESOLVED upper limit and BELOW ATTRIBUTION LEVEL as
  statements about decode traffic; the test measures this constant payload.

**Residency check (replaces the knee scan).** It runs before the measured hour, with no energy capture and with
`--idle-s 0 --settle-s 0`.

R1. **Ladder.** The rungs are b_k = G / 2^k for k = 0, 1, …, 7, that is 64 MiB down to 512 KiB, run top-down.
- *Top rung.* G is the largest payload of the small launch. The ladder stays in one launch, so the chosen b has a
  geometry known before any measurement.
- *Bottom rung.* 2^19 = 128 first-pass threadgroups × 1,024 threads × 4 bytes read per thread (REDUCE_N_READS) is the
  smallest payload that fills the small launch's first pass (Sol round 2, from the same pinned source). Below it,
  threads are idle and the precision argument of R4 only worsens.

R2. **Per rung.**
- Reshape the one ring to (W/b_k, b_k). This is a view of the same memory, so the ring is allocated once for the
  whole check. Build and evaluate the Q views, then `mx.synchronize()`.
- For mode C, then mode R: run one warm dispatch, then one **pilot** call of one sweep (Q dispatches), whose
  per-dispatch time is t_pilot. Then run three calls of N = Q × max(1, floor(T_chk / (Q × t_pilot))) dispatches, with
  T_chk = 2 s.
- *Why whole sweeps.* They make φ ≤ K_c/W exact.
- *Why 2 s and three calls.* These are the admitted scan's planning choices, carried over unchanged; they set the
  observed spread propagated below.

R3. **Timing per mode, unchanged from the admitted step 1.**
- d_j = (end_ns − start_ns)/(10⁹ N_j), and t is the mean of the three d_j.
- r is the larger of the reported clock resolution and the measured tick; u = 10⁻⁹ s; q_j = 2(r + u)/N_j. On the
  recorded Mac, r = 42 ns, so q_j = 86 ns/N_j.
- δt = max_j |d_j − t| + mean_j q_j.
- Each receipt records the admitted clock fields. A missing clock prerequisite prints its reason, with no 1 ns
  fallback.

R4. **Residency contrast.** At rung b_k, let D = t_R − t_C and δD = δt_R + δt_C.
- The contrast is **resolved** when D > δD.
- *Derivation.* The two modes differ only in address reuse, so a C dispatch faster than an R dispatch by more than
  both observed envelopes together resolves a repeat-versus-rotate timing contrast. Cache residency can cause it,
  but address translation and DRAM row locality can also contribute (§3, "False residency"). At 64 MiB, repeat
  is not resolved as faster than rotate: the diagnostic gives 705.550 versus 663.892 µs; the four rehearsals give
  C/R means 462.2/466.5, 455.3/518.7, 450.8/468.1 and 498.3/469.5 µs, all with D ≤ δD (§5). Translation reuse
  alone is therefore not shown to produce the 32 MiB contrast.
- No threshold, multiplier or band is added. This is an observed-spread bound, not a confidence statement, and not
  a hardware residency counter.
- The ladder stops at the first resolved rung, and **b = that rung's b_k**.
- *Why top-down.* §3's half-width is dominated by its baseline row, which per dispatch is t × (baseline power
  bound). Per byte it scales as (t_R + t_C)/b. With t = t₀ + b × (per-byte time), the fixed time t₀ is spread over
  more bytes as b grows, so the largest resolved b gives the smallest δΔ.
- Print every measured rung: t, δt, all calls, D, δD, and the verdict. Rungs below the chosen b are not run.

R5. **Cost** (planning, not a threshold). A rung costs per mode one pilot sweep plus three calls with counts set
by R2's pilot, not a guaranteed 2 s duration. One sweep lasts Q × t ≈ (W/b) × t.
- If pilot and timing-call rates agree, the archived fixed time t₀ ≈ 205 µs gives about 16 s per rung from
  64 MiB to 4 MiB (about 32 s for two rungs).
- 2 MiB takes about 27 s, 1 MiB about 54 s and 512 KiB about 108 s, because there one sweep exceeds 2 s.
- If all eight rungs run, the total is about 270 s, plus one ring allocation and fill (planned at the admitted
  "about 10 s").
- Measured on this Mac, timing calls last about 1 s because the slow pilots set smaller counts; the first two
  rungs together took 18–19 s in the rehearsals. These measured costs do not change the planning counts or ladder.

R6. **Refusal.** The residency check fails, and **the measured hour does not run**, in any of four cases. Each
prints its specific reason, and every class is UNDETERMINED with that reason:
- the ring of W bytes cannot be allocated: `allocation failed (34359738368 B ring)`;
- a clock prerequisite is missing: `clock prerequisite missing (<field>)`;
- any check receipt fails the geometry check: `geometry check failed (<field>)`;
- no rung is resolved: `residency not resolved`.

In every case, the slot records the check's receipts, every rung's comparison, and the reason. Preserve the one
check's calls; do not repeat, extend or retry it into acceptance. Observed-spread intervals do not guarantee against
a false residency or a false refusal under timing noise. §3 ("Bias") explains how an R-only stall can resolve
the check and produce a RESOLVED memory-traffic class even without a byte-source difference.

A `residency resolved` result must carry no reason. Its b must equal the first resolved rung exactly, with
Q = W/b; every check receipt must pass the geometry check. An inconsistent success is a reasoned check-status fault:
keep records and calls, set every class UNDETERMINED and print no interval.

The check reads no energy and is not BYTES data.

**Order.** Four probe calls in a palindrome, **R, C, C, R**, all with the same planned length. Each arm's two stream
midpoints then have the same mean time, so a drift linear in time puts both arms at the same mean state (§5 checks
these mean times). With the planned 10 s allocation/fill/warm-up all before pre-idle (§2's order), that common
time is about 6.5 s beyond the session midpoint; this shared offset does not change the cancellation. This is
the reasoning of the registration's null quads (A, B, B,
A, reg. §5) applied to arms.

**Repeats and the hour.** Each call's dispatches are N = Q × floor(T_call / (Q × t_a)): whole sweeps. Here t_a is the
arm's t at b from the residency check (t_R for R, t_C for C), and T_call = 759.2 s is the planned stream length.
Logical bytes per call are N × b.
- *Planned hour:* eight idle spans of 57.6 s (460.8 s); twelve settle gaps of 3 s (36 s; §2); about 10 s per call of
  allocation, fill, view building, warm-up and exit (40 s); and four streams of 759.2 s (3,036.8 s). Total
  3,573.6 s, the admitted hour.
- *Why 759.2 s.* It keeps the admitted hour. The stream length is (3,573.6 − 4 × 134.2) / 4, where 134.2 s is one
  call's fixed overhead (115.2 idle + 9 settle + 10 allocation).
- *Why equal lengths.* The baseline row per dispatch does not depend on T_call; the edge rows per dispatch scale
  as t_a/T_a. For a fixed total stream time, the sum t_R/T_R + t_C/T_C is smallest at T_R/T_C = √(t_R/t_C). At the
  diagnostic's ratio t_R/t_C = 1.2045, equal lengths are within 0.22% of that optimum on this one row, so equal
  lengths are used.

These are planning choices, not thresholds; the arithmetic uses the actual stamped spans.

## 2. The receipt change (before the test)

The receipt gains schema `joulewise.bytes_stream.v3` with:

1. **Order inside a call, idle spans and settle gaps.**
   - *Sequence.* Allocate and fill the ring and `mx.synchronize()`. Build and evaluate the Q views and the arm's
     list of Q references (§1), then synchronize. Run one warm reduction and synchronize, so the first measured
     dispatch is not a kernel compile. Then: sleep one settle gap before stamping `idle_pre_start_ns`; sleep the
     pre-idle span (`--idle-s 57.6`); sleep the settle gap (`--settle-s 3`); stream from `start_ns` to `end_ns`;
     sleep the settle gap; sleep the post-idle span with the ring still resident; exit.
   - *Stamps.* `idle_pre_start_ns`, `idle_pre_end_ns`, `idle_post_start_ns` and `idle_post_end_ns` are taken on
     CLOCK_MONOTONIC_RAW, the clock of `start_ns` and `end_ns`. Without them the baseline cannot be computed from the
     receipt and traces alone: the time before `start_ns` holds the fill, which is not idle.
   - *57.6 s* is `sampling.idle_seconds` of every pass-1 BYTES run config. It exceeds the three 10 s bandwidths the
     idle-variance estimator requires (§3).
   - *Settle gap 3 s, derived.* An idle span next to the stream would take in energy that a boundary reports late or
     smears across the edge. The longest such delay is the battery's: τ = 2 × T_SMC + Δt_p (reg. §7). The system
     controller publishes battery current once a second (T_SMC = 1.0 s), and Δt_p is the longest interval between
     meter polls. On H, τ = 2.302 s. It exceeds one rails sample interval (100 ms at the registered 10 Hz) and the
     meter's r_max + Δt (38 ms on H, §3). 3 s is the next whole second above τ. The same delay applies after
     fill/warm-up, hence the extra gap before pre-idle.
   - *If τ exceeds 3 s.* If the test's own τ exceeds 3 s, each idle mean is taken over its stamped span minus its
     first τ − 3 s. Energy inside the gaps enters no quantity.
   - *Clock fields.* Every receipt, including measured arms and residency-check calls, records:
     - `clock` = `CLOCK_MONOTONIC_RAW`;
     - `clock_resolution_s` from `time.clock_getres(time.CLOCK_MONOTONIC_RAW)`;
     - on macOS, `clock_tick_num_ns`/`clock_tick_den` from `mach_timebase_info`, with `clock_tick_source`;
     - `clock_ns_conversion` and `clock_ns_conversion_source`, which are `unknown` unless a source establishes the
       convention (the observed steps alone do not);
     - the derived `clock_duration_bound_ns` = 2(max(resolution_ns, tick_ns) + 1), retaining both raw inputs.

     On non-macOS the timebase fields are null and marked not applicable; getres supplies r. Missing clock
     prerequisites retain the receipt and print the check's reason, with no 1 ns fallback.
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
   (`measured rails boundary differs`); DC is unaffected. If the recorded rail set on either
   side lacks `gpu_power`, GPU is also UNDETERMINED: its integral has no measured source
   (`gpu_power missing from recorded rail set`). `kernel_library` is recorded as prepare metadata (the actual
   running kernel versions are the two MLX packages). `telemetry_backend` discloses the
   capture metadata; the governed boundary integrations above still have to be supplied. They do not independently
   veto a class. `mlx-lm` loads/generates model text; `transformers` and `tokenizers` supply model/token processing;
   `safetensors` reads model weights; `numpy` supplies host arrays. None is used by this uint8 MLX reduction.
   Python patch level changes the host interpreter metadata, not the selected MLX/Metal kernel; dispatch work is
   measured and removed by the cache arms. Each of these differences is printed as a disclosure and changes no
   class. `git_commit` and the five not-applicable model fields have the non-comparison roles in the table.

3. **Ring and geometry object.**
   - `arm`: `R`, `C` or `check-R`/`check-C` with the rung index.
   - `ring_bytes` = W, `ring_shape` = [Q, b], `dtype` = `uint8`, `view_nbytes`.
   - `view_order`: `rotate` (k mod Q) or `repeat` (always 0).
   - `sweeps` = N/Q (an integer).
   - `geometry_branch_bytes` = G, with `geometry_source` =
     `mlx v0.31.2 mlx/backend/metal/reduce.cpp all_reduce_dispatch: in.nbytes() <= (1 << 26)`.
   - `launch_side` (`small` when view_nbytes ≤ G, else `large`).
   - `logical_bytes` = N × b.

   Receipt integer counts must satisfy exactly `bytes_read = bytes_per_read * repeats`, with `bytes_per_read` = b
   and `repeats` = N; a violation is a missing prerequisite naming the field. The residency-check calls use this
   same schema with zero idle and settle.

Validate stack, ring and capture containers leaf by leaf. An absent or invalid disclosure-only leaf prints
`not recorded (<reason naming the leaf>)` and changes no class; valid siblings, including the rail set, remain
available. Missing physical leaves charge the same classes as their physical differences. A missing ring/geometry
leaf fails the geometry check, naming the leaf.

**Ordering and sign checks.**
- Each receipt must satisfy `idle_pre_start_ns <= idle_pre_end_ns <= start_ns < end_ns <= idle_post_start_ns <= idle_post_end_ns`.
- Native rails/GPU rows require `start_ns < end_ns` and `row[i].start_ns >= row[i-1].end_ns` (consecutive, disjoint
  intervals). Native rows and meter stamps must respect their recorded time order.
- A violation, including a zero stamp that breaks order, makes the affected interval prerequisite missing, with the
  row named and retained as evidence. Never drop it and recompute a bound.
- Rails, GPU and adapter-meter `power_w`, and `energy_j.rails`, must be non-negative. Battery power and its stream
  integral remain signed; zero is valid.
- Battery edge energy `battery_edge_j` is the non-negative bound v_edge = (T/n) × Σ |P_b| (registration §7). A
  negative or non-finite value is a missing prerequisite, never a smaller bound.

**Capture and harvest.** One continuous `powermetrics` capture and one continuous meter stream cover all four calls,
with one meter clock fit for the test. They run from the test's own non-claim checkout with the chain extension
(reg. §19). The one new piece of harvest code integrates rails, the GPU series, DC input and the battery term over
the receipt's stamped spans rather than over a run's own phases. It calls the pass-1 integrators unchanged.

## 3. The reported quantity and its bound

**Residency-check prerequisite and scope.** Use b, W and Q only after the §1 residency check has resolved a rung and
every receipt has passed the geometry check. The check's intervals come from clock quantization and three observed
calls per mode. They are not confidence intervals on future timing noise and do not prove cache residency. If the
check fails, preserve and print its calls, clock metadata, every rung's comparison and the specific reason. The
measured hour does not run, every class is UNDETERMINED with that reason, and quantities requiring b print
`not defined (<reason>)`. The check changes no collected BYTES number and adds no energy-uncertainty term to the
propagation below. Its timings enter only κ ("Bias").

**Boundaries.** There are four: rails (CPU + GPU + ANE), the GPU rail alone (the `gpu_power` series of the same
capture), DC input, and rest. Each is integrated over a stamped span exactly as pass 1 integrates it (reg. §7):
- **rails and the GPU rail:** by **native interval support**. The trace is a sum of constant-power intervals, so a
  span edge inside one interval needs no interpolation. The integration runs under the test session's **operative
  timing bound**: the measured bound on how far a laptop timestamp can sit from the trace's time base, evaluated as
  pass 1 evaluates it (`joulewise/b6/calibration.py`).
- **DC input:** by the meter integrator (`km003c_parse.clock_fit` and `integrate`) plus the battery term E_b
  (reg. §7, "Battery term").
- **rest:** DC − rails per span, before any averaging.

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
3. Excess per dispatch of arm a ∈ {R, C}: x_a = Σ X_i / Σ N_i over the arm's two calls; per call, x_a,i = X_i / N_i.
4. **Reported quantity: Δ_β = (x_R − x_C) / b**, in J/GB. This is the extra energy on β per logical byte when a
   b-byte dispatch reads addresses not re-read since the previous sweep, rather than re-reading the same b bytes.
   Shape, dtype, expression and launch geometry are identical. A resolved check establishes a repeat-versus-rotate
   timing contrast. Δ is memory-traffic energy per logical byte, including translation and row-locality effects;
   it is not an isolated energy per byte read from DRAM rather than cache.
   - *Why α cancels.* Write x_a = α + b × e_a, where α is the per-dispatch fixed energy (launch, synchronization,
     CPU work) and e_a the energy per byte. Both arms run the same dispatch at the same b with the same Python path,
     so α is the same in both and x_R − x_C = b(e_R − e_C) exactly. Any fixed energy that does depend on address
     reuse (for example a stall at dispatch end) is part of the measurand.

**Bound, per call.** b_i (the bound for call i, not the payload b) is the sum, not in quadrature, of the
rows (edges, counter gaps, baseline) for call i. The sum follows reg. §7 step 4, which sums its systematic terms.
The baseline term, se_idle, the Newey–West estimator and its per-stream application, and the DC combination
se_DC = se_meter + se_battery are as follows. Rest sums the rails and DC rows.

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

**Repeatability.** Each arm adds rep_a = |x_a,1 − x_a,2| × max(N_1, N_2) / (N_1 + N_2). It is exactly
the shift of x_a caused by a transient confined to one call. It does not bound an excursion present equally in
both calls of an arm.

**Propagation** (worst case, linear):
- δx_a = Σ b_i / Σ N_i + rep_a, for a ∈ {R, C};
- **δΔ_β = (δx_R + δx_C) / b.**

No α, |α|/B or cross-size term remains.

**What the bound does not cover.**
- *Address-reuse effects that are not cache residency.* R also walks Q times more pages than C, so it also takes
  more address-translation misses and fewer DRAM row-buffer hits. Their energy is part of reading new addresses
  from memory, and Δ includes it, as §0 includes stall time and clock state. It is not separable from the
  controller or the fabric.
- *The timing model behind κ* (below): a dispatch's time as a fixed part plus a sum of per-byte times by source.
  This is the model the admitted step 4 used. Overlapped stalls and unequal cache throughput across arms (GPU
  clock state) can depart from it, and κ is then not guaranteed. In particular, κ is not conservative when an
  R-only fixed time, such as address translation, dominates the timing contrast.
- *Per-call fixed energy.* Unlike per-dispatch α, a clock ramp at stream start after idle does not divide out
  because N_R ≠ N_C. Assuming the same 10 J ramp in both calls gives
  E_ramp(1/N_R − 1/N_C)/b ≈ 2 × 10⁻⁵ J/GB on §5's counts: about 0.065 δΔ_rails and 0.4 ε₀. R's first sweep
  is another possible per-call term: its 32 MiB rehearsal pilots took 506–518 µs per dispatch versus about
  311 µs steady. If that penalty returns after the hour's 60.6 s idle/settle, an R-only 0.2 s × 30 W ≈ 6 J
  per call gives about 7 × 10⁻⁵ J/GB, about 0.23 δΔ_rails and 1.5 ε₀. These are separate estimates with
  different assumptions, not measured hour energies. An equal penalty in both R calls is invisible to rep_R.
- *An excursion present equally in both calls of one arm,* as before.
- *The capacity premise K_c ≤ W/64* (§1), which this rule does not test.

**Bias, printed beside Δ: the contrast fraction ρ and its correction κ.**
- *Fractions.* Let φ be R's cached fraction and λ the fraction of C's bytes that leak to DRAM. If the per-byte
  energies are e_d (DRAM) and e_c (cache), and there is no additional arm-only fixed time/energy, then
  e_R = (1 − φ) e_d + φ e_c and e_C = λ e_d + (1 − λ) e_c. Hence, under this source-mixture model,
  **Δ measured = ρ × (e_d − e_c)**, with ρ = 1 − φ − λ.
- *Bounding ρ from the check's timing.* By the same mixture, t_R − t_C = ρ × Θ, where Θ = b(1/v_d − 1/v_c) and v_d,
  v_c are the DRAM and cache throughputs. Θ ≤ b/v_d. R's time includes its DRAM-sourced bytes, t_R ≥ (1 − φ) b/v_d,
  so Θ ≤ t_R / (1 − φ). Therefore
  ρ ≥ (1 − φ)(t_R − t_C)/t_R ≥ **ρ_L = (1 − φ_U)(D − δD)/(t_R + δt_R)**, with D, δD, t_R and δt_R from the chosen
  rung and φ_U = K_cap/W = 1/64.
  - *Why this direction.* Every substitution moves toward a smaller ρ: the lower contrast endpoint, the upper R time,
    the largest φ. ρ_L is positive exactly when the rung is resolved.
- *Correction.* **κ = 1/ρ_L** multiplies |Δ| wherever the admitted text used 1/(1 − φ): in §4 row 3 and in the NOT
  RESOLVED upper limit.
- *Direction of the bias.* Both leakages pull Δ toward zero, never toward "resolved". This covers cache leakage only;
  see "Repeatability" and the paragraph above for errors of either sign.
- *False residency.* Both arms can read DRAM and still differ in address reuse. An R-only fixed stall, such as
  translation, can resolve the timing check and add R-only energy, producing RESOLVED when Δ − δΔ > 0.
  For example, a 26 µs R-only stall at 30 W gives about 0.02325 J/GB at 32 MiB even without a source contrast.
  In that case the shared-fixed-time mixture model fails: true source contrast ρ can approach zero while ρ_L
  remains positive, so κ is not conservative. RESOLVED identifies memory-traffic energy including translation,
  not DRAM-source energy alone. No intercept-free residency signature is adopted in this revision.
- *If the capacity premise fails.* Then φ may exceed 1/64, κ is understated, and only rows 3 and the upper limit
  are affected.

**Printed precision.** Every Δ, δΔ and description quantity with a half-width prints its half-width to 2 significant
figures and the estimate to the same decimal place (reg. §14's H2 rule: a 2-significant-figure half-width is at least
10 units of its last digit, so rounding moves a value by at most 5% of it). b, W, Q, N and byte counts print
exactly; φ_U prints as its exact fraction; ρ_L and κ print to 4 significant figures. Classes are decided on
full-precision values.

**Agreement bar** for an independent recompute, if one is made:
- every class identical;
- b, W, Q, φ_U and every count identical;
- every Δ and δΔ within one bar, 1% of the smallest printed δΔ among the boundaries;
- κ within 10⁻⁶ relative (it comes from the check's receipts by closed form): float noise is amplified by about
  t_R/(D − δD) ≈ 21, so 10⁶ × noise ≈ 10⁻⁸; half a unit at 4 significant figures is at least 5 × 10⁻⁵
  relative. The 10⁻⁶ bar lies between those scales;
- any other printed quantity within half a unit in its last printed decimal (reg. §12).

The bar must exceed 10⁶ × float noise. Float noise is the propagation above applied to a relative error of
2.2 × 10⁻¹⁶ (binary64's machine epsilon) on every gross energy, as reg. §12 uses it. Worked example (§5):
3.2 × 10⁻¹⁰ ≤ 3.1 × 10⁻⁶ J/GB.

## 4. Validity, classes and the printed lines

**Validity.** The contrast is valid only when Δ_DC − δΔ_DC > 0. DC input encloses rails and rest, so a real
memory-traffic cost must show there; if it does not, the control failed to separate DRAM traffic from GPU work.

**Stack check.** Record and print the full comparison in every case, including all disclosure-only differences
and pending fields. Differences in OS build, hardware unit/device, or MLX/MLX-Metal runtime versions set
UNDETERMINED; §2 gives their physical paths. A different `measurement_boundary_label.rails`
is a different measured rails boundary: rails and rest are UNDETERMINED with that reason,
while DC is unaffected. If either recorded rail set lacks `gpu_power`, GPU is
UNDETERMINED (`gpu_power missing from recorded rail set`): a GPU integral then has no measured source.
Other differences change no class. Invalid disclosure-only leaves are printed as `not recorded (<reason>)`
leaf by leaf, without discarding valid physical siblings or charging a class.
The receipt keeps `differences`, `physical_differences` and `disclosure_differences`; harvest completes the
capture comparison and prints it even for an otherwise undetermined result.
In addition, a difference in the MLX build fails the geometry check (§1), so the hour does not run.

**Classes.** Read separately on rails, on the GPU rail and on rest, with I = [Δ − δΔ, Δ + δΔ] and κ from §3. The rows
are tested **in order** and the first that holds is the class, so exactly one holds:

| Order | Class | Condition | Meaning |
|---|---|---|---|
| 1 | UNDETERMINED | residency check failed (any §1 R6 reason); geometry check failed on an hour receipt; physically relevant stack differs; a required call, integral, bound, gap source, battery reading or native-support prerequisite is missing; validity fails; or Δ + δΔ < 0 on this boundary | the test cannot be read on this boundary; a wholly negative contrast is a failed control, not an immaterial one |
| 2 | RESOLVED | Δ − δΔ > 0 | memory-traffic energy, including translation and row-locality effects, is resolved on this boundary |
| 3 | BELOW ATTRIBUTION LEVEL | κ × max(\|Δ − δΔ\|, \|Δ + δΔ\|) ≤ ε₀ | under the stated model and constant payload, the interval spans 0 and every contrast-fraction-corrected value is below the registered per-run attribution limit; transfer to real decode traffic is limited (§1), and this does **not** say the controller is off this rail |
| 4 | NOT RESOLVED | otherwise | neither is shown |

Row 3 bounds both ends because a large negative value inside I would move runs as much as a large positive one.

**ε₀ = 1 J / (512 × b_max) = 4.9009 × 10⁻⁵ J/GB.** 1 J is the registration's per-run attribution scale (reg. §12,
"about 1 J per run"; the class is named for what it shows at that scale). 512 × b_max is the most bytes any
registered decode phase reads: 512 decode passes (reg. §3) × 39,852,331,520 bytes per pass (b_max, Llama-3.3-70B, the
largest b of the reg. §4 table) = 20,404.4 GB. Using the largest b gives the smallest, strictest ε₀. This is the Opus
seat's threshold; Sol argued no threshold can show exclusion, which is why the class is named for what it shows
(immaterial at the instrument's resolution), not "excludes". With the rehearsed κ = 17.6–23.7 (§5),
row 3 is reachable only when κ × (|Δ| + δΔ) ≤ ε₀. At §5's illustrative δΔ_rails, a zero true Δ_rails gives
κ × δΔ_rails ≈ 0.0054–0.0073 J/GB, about 110–150 ε₀. With κ about 18–24, BELOW ATTRIBUTION LEVEL needs
δΔ_rails ≤ about 2.4 × 10⁻⁶ J/GB (2.0–2.7 × 10⁻⁶ across that range), even at Δ = 0. That is unreachable
on this hardware at the illustrated width of about 3 × 10⁻⁴ J/GB, so a null result reads NOT RESOLVED.

**What "responds as registered" means (reg. §19).** Reg. §1 expects the chip's share in rails and the memory chips' share in
rest. So rails responds as registered when its class is RESOLVED, and rest when its class is RESOLVED, in the
mechanism-neutral sense of §0: rest RESOLVED shows that rest rises with DRAM traffic, not that the memory chips'
share is in rest (conversion loss on the rails' own rise also shows there; on the §5 inputs, a 10% loss on Δ_rails
is about 0.0075 J/GB, about 2.8 δΔ_rest). DC input needs no caveat: moving energy between the inner boundaries cannot
change the enclosing one. The GPU-rail class prints nowhere beside claim lines (no claim line uses the GPU rail
alone); it fills the reg. §1 slot.

**Printed lines.** One line beside the rails claim lines and one beside the rest claim lines, whenever that
boundary's class is not RESOLVED. Values are filled from the test record; Δ is signed, rotate minus repeat:

- BELOW ATTRIBUTION LEVEL: `Known-bytes check: the {boundary} memory-traffic energy contrast is {Δ} ± {δΔ} J/GB (rotate minus repeat, {b}-byte matched dispatches), within the 1 J-per-run attribution level ({ε₀} J/GB) after the contrast-fraction correction ×{κ}; {boundary} lines here carry no resolvable memory-traffic energy under the stated model and constant payload.`
- NOT RESOLVED: `Known-bytes check: the {boundary} memory-traffic energy contrast is not resolved ({Δ} ± {δΔ} J/GB, contrast-fraction-corrected upper limit {κ(Δ+δΔ)} J/GB under the stated model and constant payload); whether {boundary} lines include memory-traffic energy is not established.`
- UNDETERMINED: `Known-bytes check: {boundary} memory-traffic attribution is undetermined ({reason}).` The reason is one of:
  `residency not resolved`, `geometry check failed (<field>)`, `allocation failed (<bytes> B ring)`,
  `clock prerequisite missing (<field>)`, `stack differs in: <physical fields>`, `battery reading missing in call <i>`,
  `idle variance not defined (<stream/support reason>)`, `contrast not resolved` (validity fails), or
  `contrast negative` (Δ + δΔ < 0).
- Test not run before stage-1 unblinding: beside the rails and rest lines, `Known-bytes check: not measured; the boundary attribution of memory-read energy (§1) is not established.`

When a boundary is RESOLVED, nothing prints beside its claim lines. Inside printed lines, "§1" is the registration's §1.

**The reg. §1 slot** is filled with:
- the three classes (rails, GPU rail, rest);
- Δ ± δΔ for rails, GPU rail, DC and rest;
- b, W, Q, G and its source pin, the chosen rung's D ± δD, φ_U, ρ_L and κ;
- the stack-check and geometry-check results, and the receipt digests;
- the sentence: "The test identifies memory-traffic energy on a boundary, not whether it is the memory controller,
  the fabric or the GPU waiting on memory; on rest it does not separate the memory chips from power conversion and
  fans."

At the rehearsed κ about 18–24, the slot's BELOW ATTRIBUTION LEVEL would need δΔ_rails ≤ about
2.4 × 10⁻⁶ J/GB even at Δ = 0, unreachable here; a null result reads NOT RESOLVED.

*Wording of reg. §1 on admission (proposed, changes no number).* Reg. §1's sentence "Whether the GPU rail includes the memory
controller is measured by the known-bytes stream test" claims more than the slot can show; it becomes "Whether
memory traffic costs energy on the GPU rail, on rails and on rest is measured by the known-bytes stream test".

**Description only** (no class reads these), printed in the test record:
- R's raw excess per logical byte, X_R / (Σ N_R × b), on each boundary;
- the rails share f = Δ_rails / Δ_DC, with δf = (δΔ_rails + |f| δΔ_DC) / |Δ_DC| when DC is valid. f is a ratio of
  two contrasts that carry the same ρ, so ρ cancels and f needs no κ;
- the GPU-rail excess-power contrast between R and C, X_R / T_R − X_C / T_C;
- per arm, each call's x_a,i and rep_a, and the hour's per-dispatch time T_i/N_i. Also the hour's contrast
  t_R,hour − t_C,hour beside the check's D, so that a reversal during the hour is visible. It changes no class:
  κ is fixed by the check, which is the registered evidence;
- per arm, the mean GPU active frequency and residency from the capture's `gpu_power` sampler;
- per span, the OS thermal level from the notify-bus journal `hazards/monitor/thermal.jsonl`, selected by the span's
  RAW stamps;
- the test's r_max, τ and operative timing bound, and the hour as run.

Every description with a zero denominator or missing prerequisite prints `not defined (<reason>)`, for example
`not defined (DC contrast not valid)` for f and δf, `not defined (residency not resolved)` for a quantity requiring
b, or `not defined (thermal journal missing)`. For Δ_rails = 0 and valid DC, f = 0 and δf = δΔ_rails/|Δ_DC| are
defined. A missing description never refuses a measurement or changes a class; the validity prerequisites above keep
their explicit role.

**Missing prerequisites.** Print the whole record, with each affected class UNDETERMINED and
`not defined (<reason>)`, beside every still-computable number.
- *What counts.* This includes a missing call, a missing stream integral, a missing r_max/edge bound, missing native
  support, or an unnamed gap power source or missing adapter rating.
- *Gap sources.* A gap's power sources must be named. Enforce this through the printed reason, never an exception
  that discards the record.
- *What is retained.* All inputs, per-call excesses, available bounds and central contrasts are retained when only
  their bound is undefined.
- *Native support.* Native-support failure makes that arm's x and δx undefined. Every propagated width requires
  both arms' uncertainties.
- *Scope by boundary.* A missing DC prerequisite prevents common DC validity. A rails-only prerequisite affects
  rails and rest, and a GPU-only prerequisite affects GPU.
- *Failed check.* With the residency check failed, every b-dependent quantity, including the share and the GPU
  arm-power contrast, is `not defined (<check reason>)`.
- *Display.* The NOT RESOLVED upper limit uses the same decimal place as its H2 interval. A zero half-width uses a
  fixed two-decimal display (`0.00`), since zero has no significant digit. If a half-width is undefined, the
  printed contrast contains only `not defined (<reason>)`; a computable central value stays in the numeric record.

**Executable reader (synthetic or harvested products).** The CLI shape is unchanged; its inputs change.
- `scripts/bytes_stream_test.py check CHECK.json` prints §1 R1–R6 from a JSON list of the residency-check receipts
  (pilots and calls, per rung and mode, in run order).
- `scripts/bytes_stream_test.py read INPUT.json` prints the full §3/§4 record. INPUT has `check` (the check
  command's result) and `records` (the four entries in stamped palindrome order R, C, C, R), each with `receipt`
  and `harvest`.

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

- The reader recomputes the geometry check on every receipt.
- This reader consumes the existing integrators' products. It does not claim to implement the external capture
  extension or validate a live Mac.
- The `knee_scan` code path is retired. The `stream`/`run_stage` code gains the ring, the views and the ordered
  reference lists; that is code work outside this text.

## 5. Worked example (illustration, not a prediction)

**Timing inputs: real.** These are the lead's matched diagnostic, run 1 (quiet Mac, MLX 0.31.2,
`diag-matched/run-1/SUMMARY.json`, script `diag_matched.py`). It used an 8 GiB ring, one pilot and three ~2 s calls
per mode, repeat calls then rotate calls; this rule specifies a 32 GiB ring (§1). Values below include the clock
term q_j = 86 ns/N_j, which the diagnostic's printed ± omitted. At 32 MiB, q is 11 ps for C and 22 ps for R.

| rung b | side of G | t_C (µs) | δt_C | t_R (µs) | δt_R | D = t_R − t_C | δD | verdict |
|---|---|---|---|---|---|---|---|---|
| 64 MiB (k = 0) | small | 705.550 | 95.749 | 663.892 | 2.404 | −41.658 | 98.153 | not resolved |
| 32 MiB (k = 1) | small | 256.236 | 1.845 | 308.646 | 0.086 | 52.410 | 1.931 | **resolved** |

The ladder stops at k = 1: **b = 32 MiB = 33,554,432 B**, W = 2^35 B, **Q = 1,024**, launch side small on both arms.
Then φ_U = 1/64 and ρ_L = (63/64)(52.410 − 1.931)/(308.646 + 0.086) = **0.16095**, so **κ = 6.213**.

(The diagnostic also ran 128 MiB, which is above G and not a rung: t_C = 870.3 ± 227.4 µs, t_R = 803.5 ± 70.4 µs,
not resolved. Run 2's receipts are not archived; its reported 32 MiB values, 257.40 ± 1.83 against 308.97 ± 0.04 µs,
also resolve, with ρ_L = 0.1583.)

**Production-order rehearsals (timing evidence, not hour energy).** The four archived
`kb-knee-council/build/rehearsal-{1,2,3,4}/CHECK.json` files use the specified 32 GiB ring and top-down ladder:

| rehearsal | 32 MiB t_C (µs) | C's three calls (µs) | κ |
|---|---|---|---|
| 1 | 285.1 | 273.8 → 286.2 → 295.2 | 21.43 |
| 2 | 283.0 | 273.8 → 287.5 → 287.6 | 17.64 |
| 3 | 286.0 | 274.0 → 290.1 → 294.0 | 23.67 |
| 4 | 284.0 | 273.0 → 287.7 → 291.4 | 19.18 |

Thus κ spans 17.6–23.7 and t_C 283.0–286.0 µs, against 256–257 µs in the bottom-up 8 GiB diagnostic.
C rises monotonically within each 32 MiB rung. At 64 MiB it rises from 414–422 µs on the first call to
468–610 µs on the third (small middle-to-last reversals occur in rehearsals 2 and 3); none of those rungs
resolves (§1 R4). The top-down ladder measures C after a DRAM-heavy rung, so its state can differ from the
hour's, which has 60.6 s idle/settle before each call. Opus reads this as weaker residency evidence in
production order; Fable reads it as GPU clock state on the cache-bound arm, since loss of residency would
not restart at about 274 µs each time. This rule does not choose between those readings. The hour's own
timing contrast is printed beside the check's, as §4 requires; κ remains fixed by the check.

**Hour.** One call = 10 + 9 + 115.2 + 759.2 = 893.4 s, and four calls make 3,573.6 s.
- *Midpoints.* Assuming the planned 10 s allocation/fill/warm-up all precedes pre-idle (§2), each arm's paired
  stream midpoints average 1,793.3 s, about 6.5 s beyond the session midpoint of 1,786.8 s. R uses calls 1
  and 4, C uses calls 2 and 3; the shared offset leaves linear-drift cancellation unaffected.
- *R per call.* One sweep takes 1,024 × 308.646 µs = 0.31605 s, so N_R = 1,024 × floor(759.2/0.31605) = 1,024 ×
  2,402 = **2,459,648** dispatches (82,532 GB logical).
- *C per call.* One sweep takes 0.26239 s, so N_C = 1,024 × 2,893 = **2,962,432** dispatches (99,403 GB logical).

**Energy inputs: the admitted §5's illustration, unchanged.** These are the H session values and assumptions:
- idle power: rails 0.051 W with se_idle 0.0078 W; DC 2.386 W with se_DC = 0.04243 W; half-differences 0.002 W
  (rails) and 0.05 W (DC);
- rails anchor-shift bound 0.5388 J per call; r_max = 17.76 ms; Δt = 20 ms; v = 0; no gaps; rep = 0.

The new assumptions, standing in for what the test measures:
- *C arm:* 28 W rails and 25 W rest above idle, the admitted cache-arm assumption.
- *R arm:* the admitted S-arm powers, rails 31.45 W and rest 52.39 W, that is 31.399 W rails and 50.055 W rest
  above idle.
- Both draw these powers for the whole dispatch time.

| | rails | DC input | rest |
|---|---|---|---|
| x_R (mJ per dispatch) | 9.69117 | 25.14043 | 15.44926 |
| x_C (mJ per dispatch) | 7.17460 | 13.58049 | 6.40589 |
| δx_R, δx_C (µJ) | 5.6252, 4.6701 | 44.1959, 35.9660 | 49.8212, 40.6361 |
| Δ ± δΔ (J/GB) | 0.07500 ± 0.00031 | 0.3445 ± 0.0024 | 0.2695 ± 0.0027 |

- *Validity:* 0.3445 − 0.0024 > 0. Stack assumed identical.
- *Rails:* RESOLVED, nothing prints. Rest: RESOLVED, nothing prints. GPU rail: not separable in these inputs.
- *Description:* f = 0.2177 ± 0.0024.
- *Agreement bar:* 3.1 × 10⁻⁶ J/GB (1% of 0.00031); 10⁶ × float noise is at most 3.2 × 10⁻¹⁰ J/GB (rest).
- *Full half-widths:* 0.000306823 (rails), 0.002389013 (DC) and 0.002695836 (rest) J/GB.

*Other outcomes, same inputs except as stated:*
- **Meter gap.** One missing 20 ms meter sample in the stream of call 2 (C), with P_max = 140 + 0 W, adds 2.8 J to
  that call's DC and rest b_i. Δ_DC = 0.3445 ± 0.0024 and Δ_rest = 0.2695 ± 0.0027; both stay RESOLVED, and the gap
  prints as a disclosure.
- **Small true Δ.** True Δ_rails = 0.00030 gives 0.00030 ± 0.00031, so I = [−0.0000068, 0.00061] spans 0.
  κ × (Δ + δΔ) > ε₀, so rails is NOT RESOLVED, upper limit 0.00377 J/GB at the interval's decimal place.
- **Transient.** A 5 W transient through the whole first R call gives Δ_rails = 0.098 ± 0.023: still RESOLVED, and
  the repeatability term carries the half-width from 0.00031 to 0.023.
- **No cache.** If both arms read DRAM and have no address-reuse energy difference, Δ is near zero and reads
  NOT RESOLVED if the check resolved by timing chance. But an R-only fixed stall, such as translation, can both
  resolve the check and add R-only energy: a 26 µs stall at 30 W can give rails RESOLVED at about
  0.02325 ± 0.00032 J/GB. That is memory-traffic energy including translation; κ's source-mixture model is
  not conservative when such an R-only fixed time dominates.
- **Check refusal.** If both archived rungs, and the six below them, had read like the 64 MiB rung, every class
  would be UNDETERMINED (`residency not resolved`) and the hour would not run.

## 6. Decisions

Made by the lead between the design seats:
- Contrast design (**superseded by the matched-geometry revision below**): Opus's unchanged kernel with several
  cache sizes and the |α|/B term, over Sol's single matched cache arm (no new kernel code).
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
- Fixed-cost non-constancy (**superseded by the matched-geometry revision below**): Fable's third cache size with
  its residual charged, not a new kernel; the unbounded remainder was stated and ε_flip printed.
- Arm repeatability: Opus's additive term, not an agreement check that would set every class UNDETERMINED.
- Meter gap (superseded by Round 3 R5): keep every call; bound each known missing duration by supplied power (§3).
- Agreement bar: one bar, 1% of the smallest printed δΔ, for every Δ and δΔ.
- Settle gap of 3 s around the stream and after fill/warm-up (§2), to keep delayed energy out of idle means.

Made in the matched-geometry revision (lead ruling after council rounds 1–2, writer seat 2026-10-30):
- Rotating-buffer arm R against a repeat arm C at one payload b, same shape, dtype, expression and launch; only
  address reuse differs. This was chosen over Fable's fixed-row kernel because it leaves the expression unchanged
  and α cancels exactly (§1).
- Residency rests on the matched repeat-versus-rotate contrast at b, using the admitted observed-spread construction.
  Neither timing-knee replacement is admitted. The knee scan is replaced by an eight-rung top-down ladder within the
  small launch (§1 R1–R6).
- G = 2^26 B is read from the pinned MLX source and bound to the build, and the geometry check runs on every receipt.
- W = 2^35 B carries the admitted 512 MiB cache envelope and the 1/64 cap to the working set by the cyclic-sweep
  bound.
- C1, C3, α, γ_c, r, ε_flip and |α|/B are deleted; Δ = (x_R − x_C)/b.
- κ = 1/ρ_L replaces 1/(1 − φ), because the residency contrast no longer licenses neglecting cache-arm leakage.
- Palindrome R, C, C, R with four 759.2 s streams keeps the 3,573.6 s hour.
