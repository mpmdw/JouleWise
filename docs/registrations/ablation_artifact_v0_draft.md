# ABLATION-ARTIFACT v0: energy of ablation styles (DRAFT)

**DRAFT, NOT REGISTERED; DESK ONLY.** This implements design-study idea 12's
software preparation. It authorizes no downloads, acquisition or Mac window.
All native behavior and energy predictions remain **PROVISIONAL**. Block 5 is
sealed, unrelated to this design, and supplies no inputs. No real measurement
data was read. No external literature was checked during this offline task.

Authority: the [ranked study](../research-audits/2026-11-07/interp-weight-edit-energy.md)
§3 row 12 and lead synthesis govern over its appendix. The
[companion checks](../research-audits/2026-11-07/interp-weight-edit-energy-checks.md)
§2 correct the ordering, cost and downstream confound. The
[measurement contract](../contracts/measurement_methodology.md),
[analysis-plan contract](../contracts/analysis_plans.md), and
[decision log](../decision_log.md) retain authority; this proposal changes no
settled policy. This desk work runs under the user's explicit task override;
coordination state stays lead-owned.

## 1. Question and scope

At identical dense work, does replacing an interp component's activations with
zero, a calibration mean, an unrelated donor activation, or a scalar constant
change energy enough to change an energy-based inference about that component?
An observed style difference would be an intervention artifact, not evidence
that one component's function intrinsically costs more joules.

Start with **4 layers' complete MLP down-projection input, batch-one prefill**,
not single heads or free generation. Provisional layer IDs 0, 3, 7, 11 in the
planner are placeholders for a reviewed model/config, not asserted model facts.
Per-head effects are expected below this instrument class's practical floor.
Decode is a secondary bound only after the compute-bound positive control.
No claim about surgical weight edits, model quality, or hardware energy follows
from the desk outputs.

## 2. Shared implementation and exact interventions

[`AblationReplacement`](../../joulewise/interp_energy/weight_edits.py) extends
the existing mask/axis-selection and reversible byte-restore lifecycle. It
accepts a dense matrix `[rows, features]`, whether weights or saved activations.
Selections default to empty, exactly as in `AblationMask`; pass an explicit
mask, rows, columns, neurons, or contiguous heads. True means replace. It does
not infer model orientation, head packing or layer names.

For activation input `X[T,F]`, freeze an independent calibration donor matrix
`D[S,F]` from a declared reference distribution before evaluation:

| Style | Prepared replacement `R[T,F]` | Meaning |
|---|---|---|
| zero | positive zero throughout | Dense zeroing; no work skipped |
| mean | repeat `mean(D, axis=0)` across T rows | Per-feature calibration mean; retains feature differences |
| resample | `D[indices]`, one donor index per row | Whole donor vectors, sampled with replacement; preserves within-vector feature covariance |
| constant | repeat a finite scalar `c` | Scalar-fill control; proposed `c=1`, freeze value before measurement |
| sham | clean `X` | Same replacement graph with its own clean operand |

Calibration means accumulate in at least float32 then cast once to target
storage; float64 targets retain float64 arithmetic. Nonfinite donors and
overflow after casting are refused. Donor indices are explicit, allow repeats,
and must be generated/pinned before the timed pass. The toolkit never draws
samples or loads models. Calibration split, source distribution, prompt and
position matching, sample count and donor-index hashes remain open pins. Each
evaluation tensor needs its own prepared operands; a sham from another prompt
is not an identity control.

For weights, rows are explicitly oriented parameter rows. Replacing a weight
row with a donor-weight row or its feature mean is supported, but **is a
different intervention from activation ablation**. Activation means cannot in
general be folded into weights. Keep these experiment families separate. Dense
storage, dtype and shapes stay fixed; quantized codes are out of scope.

Desk example (synthetic arrays only):

```python
import numpy as np
from joulewise.interp_energy.weight_edits import AblationReplacement
from joulewise.interp_energy.ablation_artifact import replace_activation

x = np.ones((4, 3), dtype=np.float32)
donors = np.array([[1, 2, 3], [3, 4, 5]], dtype=np.float32)
edit = AblationReplacement("x", "mean", calibration=donors, columns=[1])
state = {"x": x.copy()}
edit.apply(state)       # saved activation OR parameter mapping
edit.revert()          # full raw-byte restoration check
repl = edit.replacement_for(x)  # full unmasked tensor, prepare outside timing
mask = np.zeros_like(x, dtype=bool)
mask[:, 1] = True
y = replace_activation(x, mask, repl)  # same runtime where for every style
```

For resident weight contrasts reuse `WeightSwap` and model leaf binding. Never
apply/revert or hash inside measured work. For activation contrasts, prepare
all replacements, masks and calibration buffers beforehand, evaluate them and
keep them resident. Resampling's extra calibration pass, RNG, transfers and
setup must not appear only in that arm's measured span. Report setup cost
separately if the question includes total experiment cost.
Bind the calibration, mask, donor indices, scalar, shape/dtype and layer map
in an intervention manifest alongside replay's token and weight identities;
unchanged weight hashes alone do not identify an activation intervention.

## 3. Derivation: what ordering is actually predicted?

For storage bit b of feature j in IID donor rows, let `p[j,b]` be its probability
of being one. Then

`Pr(next bit != current bit) = p(1-p) + (1-p)p = 2p(1-p)`.

The expected normalized row transition density is the average of this quantity
over features and stored bits. It is positive if at least one bit varies.
Zero, a fixed feature mean, and a scalar constant each repeat exactly the same
row, so their **row-to-row transition density is zero**. Thus zero = mean <
resample is the expected row-proxy ordering for nondegenerate IID resampling;
constant also ties zero on this traversal. Finite sampling is not a proof of a
strict inequality: a repeated donor, constant calibration, correlated samples
or unchanged bits can give ties.

Within a row's feature/reduction traversal, +0 has no one bits and no internal
transitions. A mean vector can have both, while a scalar constant has one bits
but zero internal transitions. There is **no general mean-versus-resample
feature-transition ordering**. Float encodings, signs, exponent distributions,
rounding, partial masks and transitions into/out of edited regions matter. A
synthetic counterexample has calibration rows `[1,1,1,1]` and `[1,3,7,15]`:
the mean `[1,2,4,8]` changes bits across features; repeated draws of the first
donor do not. Hamming weight alone is also not transition activity.

The proposed *direct energy* ordering `E_zero <= E_mean < E_resample` therefore
requires a physical hypothesis: repeated means lower temporal switching,
zero may additionally lower reduction switching or operand-zero gating, and
data dependence survives the actual kernel/memory traversal. Neither Apple's
gating nor the traversal is established. Constant is a control without a
preregistered position relative to mean: its bit pattern and downstream output
matter. Software rails might be blind to all of these changes. Test the energy
ordering; do not encode it as a physical fact.

[`toggle_statistics`](../../joulewise/interp_energy/ablation_artifact.py) reuses
`operand_stats` for row and within-row counts, excluding feature transitions
across row boundaries. Tests cover float16/float32 and encoded bf16; the bf16
host encoding check is not native MLX validation. These statistics have no
coefficient converting them to watts, joules or physical bus transitions.

## 4. Separate direct and downstream terms

For each style s at layer l:

1. Run a clean uncompiled forward outside timing; cache the clean next-layer
   residual `Z_clean`, the clean hook activation, and fresh-cache identity.
2. In every timed arm compute `X_s = where(mask, R_s, X)` and the entire
   down-projection/residual `Z_s`, with identical dtype, shapes, kernels and
   dispatch count. **Materialize/submit the ablated projection before patching**
   so lazy evaluation cannot delete the very work under test. Match this
   submission/evaluation boundary in all arms.
3. Always execute `where(patch_mask, Z_clean, Z_s)`. The runtime patch mask is
   all true for the patched arm and all false for propagated. Both operands
   remain resident in both modes. Continue all downstream layers. Use fresh
   caches and identical input IDs/chunking for every member. No EOS stopping
   or sampled-token feedback.
4. Sham uses its clean activation through the same first `where`. A/A′ uses
   byte-identical **distinct buffers**, with the same placement/binding
   procedure. Numerically equal references alone do not certify this control.

For any two styles s,t define `C_patch = E_t,patch - E_s,patch` and
`C_total = E_t,prop - E_s,prop`. `C_total - C_patch` is the operational
downstream contribution. Verify downstream activations/logits are bit-identical
to the clean pass in patched arms. A patch mismatch invalidates this split.
Pair modes within independent session blocks to preserve covariance when
estimating this difference; do not subtract unrelated marginal error bars.

This is not transistor-level attribution. `C_patch` also includes operand-data
effects in the replacement/patch operations and the required materialization
boundary. Equal graph counts remove unequal hook work, not all hook switching.
Retain hook-only/null diagnostics and describe this as direct-plus-intervention
energy. If kernels, runtime, frequency, cache bytes or transfer counts differ,
report an execution-path contrast, not pure switching or component joules.

## 5. Later measurement gates and budget

**Gate 0, native desk validation:** run the native tests below on a separate
Metal-capable desk session with tiny synthetic arrays. Audit actual model hook
placement, graph equality, evaluation, distinct A/A′ storage, leaf binding,
resident allocation and patch correctness before proposing acquisition.

**Gate 1, authorized quiet Mac only:** reuse
`rail_data_dependence.Settings/make_plan/execute_plan` and its existing
powermetrics/KM003C hooks for block P, beginning with bf16 fixed-shape GEMM and
the existing decode-like weight-ring control. Include random, explicit zeros,
constant, sparse, sorted and A/A′ conditions. This is the existing ladder,
not a second collector. Its constant fill is a positive control; feature-mean
rows are separately prepared by this toolkit. Pin equal dispatch counts and
timing/frequency tolerances from independent timing/null work. If DC cannot
resolve extreme-fill contrasts within a relevant bound, bank the grid and
report the instrument bound. A flat rail alone does not establish physical
absence; a DC-only signal classifies rail blindness. No per-head escalation.

**Gate 2, banked per-layer grid:** the planner proposes four layers, five
pair contrasts (`zero/mean`, `mean/resample`, `zero/resample`,
`constant/resample`, `sham/sham_copy`), two patch modes, 12 randomized ABBA/BAAB
quads per cell. The same fixed token sets and donor-index choices recur in
all cells. Compare B minus A. A quad's estimator is `(B1+B2-A1-A2)/2` in ABBA
orientation; reverse labels for BAAB. Individual samples/members are not
independent replication units. Analyze quads with the existing lock-in tools,
with session clustering or block resampling for dependence. Freeze session
count, sample size and the multiplicity policy before viewing style contrasts.

This is **1,920 members, 5.33 nominal work hours** at 10 s/member, excluding
block P (planning 60–90 min), calibration, warmup, idle, transitions and capture
checks. Member seconds are budget estimates; execute a fixed dispatch count,
never run until a style-dependent time target. Start a smaller layer pilot if
independent null sizing cannot fit a lead-approved window. Do not infer
1/sqrt(time) improvements without PSD/null evidence; systematic bounds do not
average down. `power.plan_power` accepts the local independent-unit SD and
non-averaging bound; the historical study's SD is not transferred as a floor.

The generated cell order and per-cell `lockin.make_schedule` specifications
are desk proposals. A registration must also freeze session/prompt blocking,
pairing of patch modes and quads, exact chips, allocations, software versions,
calibration/evaluation hashes and dispatch counts. This module supplies no
native grid runner or measured-energy reducer.

## 6. Boundary, materiality and reading rule

Primary: gross energy at KM003C DC input **plus signed battery assist**
(discharge positive, charging negative). Missing assist evidence is not zero.
Use approved common-clock spans, integrate actual sample support and retain
edge/alignment uncertainty. Gross J/member and J/dispatch are primary;
duration and mean W aid interpretation. GPU/CPU/ANE rails, IOReport and rest
are secondary. Rest is not a DRAM meter. Log thermal state, frequency,
residency and cache size. Require thermal level 0 and predeclared timing/clock
matching for a pure operand-data interpretation. Do not shorten the calculation
to the finest power-sample interval or treat modelled rails as independent DC
evidence. Use the existing reducers and evidence contracts; no synthetic
descriptor is substituted for a measured quantity.

Before outcomes, name the smallest intended energy-interp claim scale `C` and
choose a materiality tolerance `epsilon` (proposal: `0.1 * abs(C)`, in J for
the exact fixed-work unit). A planner default is not a scientific threshold.
If C is unknown, provide a sensitivity curve over fixed tolerances and no
single "matters" verdict. Widen paired/session confidence intervals by the
applicable non-averaging systematic bound before any decision:

- Entire style-contrast interval inside `[-epsilon, epsilon]`: bounded below
  practical relevance for this workload/boundary, even if statistically nonzero.
- Entire interval above `epsilon` or below `-epsilon`: materially different
  energy for the stated claim scale.
- Otherwise: unresolved. A nonsignificant contrast is not equivalence.

For an energy-importance score `I_l,s = E_l,s - E_l,sham`, the change caused by
style is exactly `I_l,s - I_l,t = E_l,s - E_l,t`. Report patched and propagated
scores separately, with uncertainty and functional diagnostics from the same
frozen evaluation tokens. Check whether style-dependent intervals can exceed
the intended layer-ranking gap or reverse a ranking. Do not generalize one
layer's offset to every layer, claim independence from functional importance,
or call a below-floor result zero. Any actual efficacy/behavior study remains a
separate free-running channel using the existing behavior tools.

## 7. Reproduce desk outputs and pending native tests

Already-installed dependencies only; no model downloads or native collection:

```sh
python3.13 -B -m joulewise.interp_energy.ablation_artifact --plan-only
python3 -B -m joulewise.interp_energy.ablation_artifact --synthetic
python3 -B -m unittest tests.interp_energy.test_ablation_artifact
```

The lead must run these individually outside this sandbox, on a Metal-capable
**desk** Mac with NumPy/MLX already installed:

```sh
python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact_mlx
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx
python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact
```

The new native tests cover all styles/dtypes, clean-residual patching and
existing resident swaps bound to a tiny Linear. They do not validate a real
transformer hook, cache equivalence, graph invariance, latency or instruments.
Repeat numerical/import tests under the Python 3.11 CI environment. Native
grid execution and all acquisition remain lead-owned, pending these gates and
a sealed measurement/analysis plan.
