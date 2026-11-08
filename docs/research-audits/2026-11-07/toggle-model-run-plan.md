# ENTROPY-DIAL / toggle model: H4 desk kit and proposed Mac window

Status: **PROVISIONAL; synthetic software evidence only.** This is a design
extension of ranked ideas 5–6 in [the study](interp-weight-edit-energy.md) and
the [checks](interp-weight-edit-energy-checks.md), not a registration, hardware
validation or authorization to collect. No sealed outcomes or real measurement
files were used. No model downloads are needed.

The study merges ENTROPY-DIAL into S1 and permits H4 only after block P gives
“both move” or “DC only.” That gate remains. A flat GPU rail cannot veto a DC
effect; a GPU-only effect cannot establish a DC switching claim. These tools
reuse `rail_data_dependence`, `operand_stats` and `lockin`; they do not add a
second collector, decode loop, power integrator or production runner.

## Encodings and exactness

`joulewise.interp_energy.toggle_model.AffineWeight` snapshots affine 4/8-bit
weights W[N,K], with little-code-first packed uint32 words and one floating
scale/bias per input group. NumPy/MLX imports are lazy. No operation follows
paths, reads data, selects a GPU or loads a model on import.

For each group, W = s*q + b. `affine_reencode` implements

```text
q' = m*q+c;  s' = s/m;  b' = b-c*s/m
```

Integer m/c may be scalar or group-shaped. Nonzero m, representable codes,
finite metadata and exact reference dequantized bytes are required. There is
no clipping or requantization. Examples: m=2,c=0 halves the scale for codes
with headroom; m=1,c=2 shifts codes and bias; m=-1,c=Q complements codes
(Q=15 or 255), negates scales and adds Q*s to the bias. Boolean group masks
allow partial complements. They are encoding choices, not weight edits.

**Floating arithmetic matters.** The study's algebraic complement identity
does not guarantee bit exactness for arbitrary floating metadata. The host
reference computes in float64 and rounds once to the float16/float32 metadata
dtype. Every transform compares the resulting bytes, including signed zeros,
and refuses a mismatch. A test with fp16 s=0.1,b=0.03 is a counterexample to
unconditional exactness. Do not claim all MLX weights are re-encodable.

`permute_groups(weight, order)` permutes whole input groups and their metadata.
New group j contains old group `order[j]`. Its returned `inputs(x)` gathers
the corresponding old input columns; `canonical_dequantized()` applies the
inverse column permutation. Thus x' @ W'.T = x @ W.T in exact arithmetic.
Use the returned mapping rather than guessing the inverse convention.

Permutation can change floating reduction order. Even identical native
dequantized weights do not prove identical `quantized_matmul` results: MLX can
factor group sums and affine bias terms differently. `verify_mlx_pair` checks
actual native dequantized bytes outside timed chips; the lead must ALSO check
native outputs for every prepared input/ring member. The tests demand exact
outputs on small dyadic fixtures. Arbitrary-input bit-identical logits remain
unverified. Exclude failing candidates from an identical-output experiment;
do not quietly substitute an allclose tolerance.

The returned MLX tuples work with the existing
`rail_data_dependence.MLXBackend.cycle((x, ring, "int4"))` at group size 64.
That runner is fixed at group size 64; other group sizes supported by the
encoding helper must not be passed to it. Bind/rebind resident operands, never
quantize, gather inputs, hash, convert to host or verify inside chips.

A tiny host-only example (existing NumPy required):

```python
import numpy as np
from joulewise.interp_energy import toggle_model as tm
q = np.arange(64*256).reshape(64, 256) % 4
w = tm.AffineWeight(tm.pack_codes(q), np.full((64, 4), .125, np.float16),
                    np.full((64, 4), -.5, np.float16))
offset_arm = tm.affine_reencode(w, offset=2)
scale_arm = tm.affine_reencode(w, multiplier=2)
sign_arm = tm.complement(w)
permuted = tm.permute_groups(w, [2, 0, 3, 1])
x = ((np.arange(256) % 3)-1).astype(np.float16)[None, :]
x_permuted = permuted.inputs(x)  # prepare outside any native timed span
assert permuted.canonical_dequantized().tobytes() == w.dequantize().tobytes()
```

## Descriptor and estimator contract

`storage_statistics` reports existing operand statistics and Hamming-distance
counts separately for packed codes, scales and biases. At byte stride d it
sums popcount(byte[i] XOR byte[i+d]) for all i<L-d in each C-order buffer.
Default d = {2,4,8,16,32,64,128} bytes. Row boundaries are included; buffer,
ring-member and dispatch boundaries are excluded. Each descriptor is one
buffer traversal. For a ring, sum each member's count before multiplying by
complete ring cycles per second. Do not multiply by ring size twice.

Full complement flips packed-code Hamming weight but preserves EVERY packed
XOR distance. It is a Hamming-weight control, not a transition slope arm.
Masked complement changes some strides: alternating 32-byte groups have
period 64, so their 64-byte distance is invariant. Group permutations retain
the code histogram but can alter ordering. Metadata descriptors, numerical
zero counts, activations and outputs must stay visible in the manifest.

For A/B descriptors T_A,T_B and common fixed dispatch rate r:

```text
delta_T_per_second = (T_B-T_A)*r
c = (mean_gross_power_B-mean_gross_power_A)/delta_T_per_second
units(c) = W / (proxy transitions/s) = J / proxy transition
```

`estimate_transition_cost` accepts interval-average gross powers and their
start/end windows in the existing `lockin.SyntheticTrace` container; that
container can hold supplied measurement arrays as well as simulations. Its
`baseline_w`, `effect_fraction` and simulation-component fields are not used
for inference. Actual input integration/alignment belongs to the existing
reducer and the lead. The reference must match commanded schedule windows.
`make_schedule` reuses the rail ladder's randomized ABBA/BAAB ordering.

Default inference reuses `lockin.estimate_abba`: equal observed coverage and
within-chip sampling centroids are required. For irregular/crossing meter
windows, use the preregistered `method="demodulate"`, which uses actual window
averages, a linear trend and fixed edge guards. Do not choose methods after
seeing their significance. Both paths reuse HAC or moving-block-bootstrap
intervals on chronological four-chip blocks. Negative exposure contrasts
reverse CI endpoints; negative coefficients and nulls are retained. Zero
exposure contrasts are rejected, not divided by an epsilon.

Intervals condition on supplied counts and r. They exclude meter calibration,
alignment error, systematic bounds, uncertain dispatch rates and model error.
Neither thousands of meter windows nor descriptor bits are independent
replicates. Dependence must decay across blocks for these asymptotic CIs.
No slope here is a measured physical joule per bus toggle: routing, DBI,
compression, dequantization and internal partial sums are unobserved. A
single-coefficient fit cannot identify their separate costs. Code/metadata
changes that covary remain an attribution limit, even at identical outputs.

Example, entirely synthetic and runnable with existing NumPy:

```python
from joulewise.interp_energy import lockin, toggle_model as tm
schedule = tm.make_schedule(64, chip_seconds=2, seed=714)
trace = lockin.simulate_trace(schedule, baseline_w=25, effect_fraction=.004/25,
                             noise=lockin.NoiseModel(white_sd_w=.001), seed=19)
result = tm.estimate_transition_cost(
    trace, transitions_a_per_dispatch=1e8, transitions_b_per_dispatch=3e8,
    dispatches_per_second=100, boundary="dc", hac_lags=3)
# Injected coefficient: .004 / ((3e8-1e8)*100) = 2e-13 J/proxy transition.
```

## One proposed quiet-Mac window

Owner: lead, on the fan-cooled MBP with KM003C inline. **No active agent, no
blinded analysis job on that machine, no concurrent experiments.** This desk
session must not stop or disturb the currently running job. Window selection
and any external capture require a later clean, lead-controlled session.

Before reserving it, native tests below must pass, the study's block-P gate
must be satisfied, and a nonrestricted PSD/cadence pilot must justify chip
duration and interval block lengths. Freeze a prospective manifest containing
runtime/version, seed, synthetic ring identities, input bytes, descriptors,
schedule, work count, guards, boundary and exclusion rules. No synthetic run
clears any metrology/registration/claim gate. Required independent review of a
future registration and claim remains lead-owned under `docs/orchestration.md`.

Planning envelope: **180 minutes maximum**, not a power calculation or promise
of detection. Three pair comparisons, 32 four-chip blocks per pair, nominal
10-second chips = 64 minutes active work. These are planning numbers to freeze
or resize before collection from the cadence/PSD pilot, never from outcomes.

| Time budget | Work and decision |
|---|---|
| 0–20 min | KM003C clock/cadence and existing rail capture checks, idle brackets, stable power source/battery state, fan/thermal settling. Preserve all raw samples. |
| 20–40 min | Materialize/warm all synthetic inputs and resident affine int4 rings; at least 1 GiB packed+metadata per arm via existing `weight_bytes`; evaluate every member, exact native dequantization and output checks. Calibrate one common integer number of whole ring cycles per slot. |
| 40–104 min | Three comparisons in a preseeded pair order: A/A′ byte-identical copies; full complement (HW control); predeclared group-permutation arm with nonzero 32-byte descriptor contrast. Each comparison has its own contiguous 32-block randomized ABBA/BAAB schedule using the existing rail ordering; no reload/recompile per chip. |
| 104–140 min | Guard/gap overhead, predeclared idle brackets and handling reserve. Fixed work, not “run until significant.” Stop if complete planned work cannot fit. |
| 140–180 min | Final idle bracket, collector completion checks and immutable custody. Any unused time remains unused, not extra outcome-dependent replication. |

Use fixed synthetic finite dyadic codes/metadata and identical activation
bytes where possible. Group permutation requires a compensating input gather
and therefore changes input order; prepare it outside chips and retain its
descriptor as an explicit confound. Prefer histogram-preserving group
permutations with common scales/biases across groups to hold metadata bytes
fixed. Choose their order before data using descriptor contrast, never energy.
Whole complement's stored scales/biases change and must be reported.

Proposed geometry is the existing GEMV shape M=1,N=K=4096, affine int4,
group size 64, fp16 metadata, and one fp16 all-ones input. Each matrix occupies
9 MiB including metadata by `rail_data_dependence.weight_bytes`; 114 matrices
give 1026 MiB per arm. Base, A′, complement and permutation resident together
need 4104 MiB of weight storage before allocator/host overhead. This is size
arithmetic, not a residency measurement. Use s=1/8,b=-1/4 in every group so
permutation leaves metadata and this input byte-identical.

Avoid nearly identical distances from permuting iid random codes. A proposed
synthetic contrast has 64 groups per row: group g has uniform code
`(g//16 + row_offset) % 4`, repeated across its 64 columns. Row offsets are
drawn from {0,1,2,3} with seed 714 in ring/member/row order. Permute groups with
`[g+16*v for g in range(16) for v in range(4)]`. The code histogram is fixed,
but 32-byte stride counts change substantially, before any energy is observed.
Retain per-member counts and verify the nonzero summed contrast when freezing
the manifest. These structured operands deliberately span descriptor space;
they are not representative trained weights, and potential compression is
still a validity/interpretation concern.

Ring size/setup/residency feasibility and actual runtime remain UNVERIFIED.
The current rail runner knows fill labels, not these prepared encoding pairs;
this plan is **not** an executable new capture CLI. The lead must supply a
thin prepared-ring driver using its existing cycle, clock stamps and
`capture_hooks.existing_capture` before a window. It must retain actual chip
spans, work counts, identities and an explicit completion/abort record. This
desk kit supplies encodings, schedule and estimator, not collection authority.

**Validity gates, prospectively frozen:** no native output/dequant mismatch;
identical dtype/shape, kernels, group size, resident bytes, dispatch count and
cache regime; thermal level zero; matched GPU frequency/residency; no faults,
paging or graph recompilation. Freeze timing-equivalence margin and treatment
of power-source drift from the pilot. The scalar estimator assumes common r;
unequal actual rates cannot be repaired by pretending r is common. Such runs
remain descriptive E/dispatch and timing contrasts; exclude their causal
coefficient or preregister a new model. Report exclusions/aborts, never drop
individual high-power samples. A/A′ bounds swap/setup artefacts separately.

**Reading rule:** DC is the primary arbiter. Report gross E, duration, work
count and contrast at DC, GPU and rails; construct rest as simultaneous
DC-minus-rails before fitting so covariance is retained. Do not subtract
independent CI endpoints. Report a conditional c at the predeclared primary
32-byte stride; the other strides are sensitivity descriptors, not seven
independent discoveries or a significance-driven stride search. Full
complement receives a power/HW contrast only. Keep systematic bounds separate
from statistical intervals and apply the owning claim gates before claiming
detection/equivalence. A wide DC interval is inconclusive, even if rails move.

If DC moves and rails are flat, report an instrument/boundary discrepancy;
do not label it “DRAM energy” by subtraction alone. If neither moves, report
the interval/bound on the conditional coefficient, not zero physical cost.
If timing changes, report structural/runtime coupling rather than isolated
switching. Do not fit a general predictor of surgical weight edits; they sit
near unchanged storage statistics. This one-window experiment is a local
platform/format/kernel calibration or bound, not a transfer claim.

## Verification handoff

Desk: run `python3 -B -m unittest tests.interp_energy.test_toggle_model -v`
with an existing NumPy installation. Bare Python skips numerical tests.

Lead, outside this sandbox on an authorized Metal-capable non-measurement
machine, one module per process, tiny synthetic operands only:

```sh
python3.13 -B -m unittest tests.interp_energy.test_toggle_model_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

First module checks packing/dequantization, snapshots of `mx.quantize` output,
all transforms and exact output equality through the existing rail backend.
The second is the wave-1 backend/fill regression. A skip is not native evidence.
The lead must also run the new desk module with NumPy on CI Python 3.11/3.13;
the sandbox's available NumPy interpreter is Python 3.14.
