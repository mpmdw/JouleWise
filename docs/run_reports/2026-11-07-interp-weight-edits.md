# Reversible weight edits — desk implementation, 2026-11-07

## Intake and authority

User task `weight-edits`, branch `interp/2026-11-07-weight-edits` (already
checked out at intake), starting head `3edb715df`. The initial worktree was
clean. This is synthetic desk work for the interp × energy design study,
not an experiment, registration, model-edit reproduction, or energy result.

Read the study and relevant companion checks, especially Stage 0 and the
LOCKIN-SWAP/PRBS cautions; ran Mission M0 intake against the generated stop-card
and lane pointers, queue/do-not-do list, workspace state, project authority
map, orchestration guidance, and D-009. No active stop card was present.
The user's direct bounded task selects this desk lane ahead of the historical
queue. Per the user's stronger instructions, no coordination state/kernel task
was changed and no full suite was run. No subagents or external consults were
used. No network, downloads, real measurement data, sealed directories,
analysis pipeline, quiet-machine collection, or running analysis jobs were
accessed. Absolute paths mentioned in repository prose were not followed.

## Changes

- Added `joulewise/interp_energy/` with a backend-lazy `weight_edits.py`.
- Added `SparseDelta`, `RankOneUpdate`, `AblationMask`, `MagnitudePruning`,
  `SignFlip`, and `Scale`. Each applies to a flat parameter mapping and reverts
  using saved bytes, checking full raw-byte SHA-256 of affected parameters.
  Sparse deltas support flat indices and coordinate vectors. Rank-one updates
  use `u` of length rows and `v` of length columns as `u[:, None] * v[None, :]`.
  This implements the update primitive, not ROME/MEMIT fitting.
- Sparse/rank-one/scale arithmetic uses at least float32 (retaining float64
  parameters' precision), then casts back to the stored dtype. A tiny fp16
  delta test guards against rounding the delta before adding it to the weight.
- Ablation covers exact-shape boolean masks and unions of row, column, neuron,
  or contiguous head-group selections along an explicit axis. No model packing
  or head orientation is inferred. Pruning selects `floor(fraction * size)`
  entries, resolving equal magnitudes by flat offset; existing zeros count.
- Added `WeightSwap`: compares states bitwise during setup, retains sparse
  NumPy backups, switches only changed elements, preserves NumPy array/mapping
  identity, and records immutable start/completion monotonic-nanosecond events
  plus state, sequence, and logical changed-byte count. Same-state requests
  also receive events. SHA-256 scans occur at setup/explicit `verify()`, never
  in the switch path.
- MLX uses resident, pre-evaluated base/edited tensors and changes only the
  affected leaves in the same mapping/model. A `bind(changed_parameters)`
  callback connects that mapping to the model. Evaluation/synchronization
  brackets binding. No tensor expressions are built per MLX switch.
- Preparation validates the full edit before writes. Binding failures roll
  back bytes/state; edits reject outside value changes before reversion.
  Switches reject rebinding/layout changes on patched parameters, and explicit
  verification audits all names/layouts/bytes. Broken injected completion
  clocks roll back the requested switch. Inputs require exclusive ownership;
  NumPy active arrays must be writable/C-contiguous, floating point, and not
  aliased. Quantized integer codes are deliberately rejected.
- Added NumPy, dependency-free import, and gated native MLX unittest modules
  under `tests/interp_energy/`, using only tiny synthetic arrays/layers.

## Minimal usage

```python
from dataclasses import asdict
import numpy as np
from joulewise.interp_energy.weight_edits import SparseDelta, WeightSwap

base = {"layer.down_proj": np.arange(24, dtype=np.float32).reshape(4, 6)}
edited = {name: array.copy() for name, array in base.items()}
edit = SparseDelta({"layer.down_proj": (([0, 3], [1, 4]), [.125, -.25])})
edit.apply(edited)

swap = WeightSwap(base, edited)  # setup and full hashes outside timed replay
for state in ("base", "edited", "edited", "base"):  # caller owns schedule
    event = swap.switch(state)
    event_row = asdict(event)  # caller persists this with its replay record
    # Run/evaluate the caller's fixed-token work under the selected state.
swap.revert()
swap.verify()  # full audit outside the timed switch path
edit.revert()  # also verifies bit-identical restoration of edited's source
```

For MLX, flatten names to match the model and pass a binding callback, e.g.
`bind=lambda changed: model.update(tree_unflatten(list(changed.items())))`.
Use an uncompiled forward and submit/evaluate its results before switching.
Synchronizing cannot discover an inference result that remains unevaluated.

## Verification

Tests ran one module at a time, in seconds total, with no background workers.
`python3` is Python 3.14.6 with NumPy; `python3.13` is Python 3.13.18 with
neither NumPy nor MLX. No packages were installed.

| Command | Final result |
| --- | --- |
| `python3 -B -m unittest tests.interp_energy.test_weight_edits` | 45 passed, about 0.02 s |
| `python3.13 -B -m unittest tests.interp_energy.test_weight_edits_import` | 1 passed, about 0.14 s; optional imports blocked |
| `python3.13 -B -m unittest tests.interp_energy.test_weight_edits` | 45 skipped, optional NumPy absent |
| `python3 -B -m unittest tests.interp_energy.test_weight_edits_mlx` | 8 skipped, MLX absent |
| `python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx` | 8 skipped, MLX absent |
| `python3.13 -B -m compileall -q joulewise/interp_energy tests/interp_energy` | passed |
| `git diff --cached --check` | passed before commit |

The first NumPy run found empty-array memoryview hashing and NaN sign handling
issues. Both were fixed and covered: empty hashes use the empty byte string;
sign flipping uses negation rather than multiplication. Subsequent review
added metadata-conflict, clock rollback, read-only alternative, endian/scalar,
and low-precision rounding checks. Full-suite execution was intentionally
omitted under the user's blinded-job safety rule.

## Limits, uncertainty, and exact lead handoff

**PROVISIONAL MLX support:** no native MLX code ran in this sandbox. The native
suite covers every edit family on fp16/bf16/fp32, bf16 raw-byte hashes and
restoration, a real tiny uncompiled `mlx.nn.Linear` bound to `WeightSwap`,
repeated resident swaps, signed-zero/NaN payload differences, and ordering of
sync/bind/completion events. Its API assumptions and device behavior still
need native execution. Python 3.11 numerical execution was also unavailable;
3.13 numerical tests skipped because NumPy is absent here.

NumPy's O(changed bytes) claim concerns writes per prepared switch; setup and
verification scan full tensors. MLX switches resident references in the same
model, **not the same MLX array object or a guaranteed partial device-buffer
write**. Two resident full tensors are held per changed parameter. Sparse index
preparation has temporary memory costs; dense edits may store an index per
weight. Native setup/latency/memory performance was not benchmarked. No-op
identical states do not establish the study's distinct-physical-buffer A/A′
control. No recompilation/reload in a real model, cache correctness, swap
latency symmetry, buffer identity, or energy sensitivity is claimed.

Next: on a Metal-capable **desk** session, with NumPy and MLX already installed,
run these modules individually under the lead's Python 3.13 environment:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_import
python3.13 -B -m unittest tests.interp_energy.test_weight_edits
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx
```

Repeat the NumPy/import checks with the Python 3.11 CI environment. Then review
the actual model leaf-binding and uncompiled forward integration with tiny
synthetic configurations. The lead still owns noise-PSD, teacher-forced/cache,
A/A′ buffer controls, model-download approval, native latency/residency gates,
and all later measurement authority. There are no unresolved naming or science
rulings introduced by this toolkit; the native behavior above remains unverified.

## Local delivery

The implementation/tests and this report are committed locally on the requested
branch; no push or merge. The commit message is
`Add reversible synthetic weight edits and resident weight swaps`.
Only the two new packages and this report are in the change. Coordination files
and existing project code are unchanged.
