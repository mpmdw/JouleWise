# Toggle-model desk implementation — 2026-11-07

Branch: `interp/2026-11-07-toggle-model` (already selected and clean at intake).
Base: `3c8ce8a5a`, the integrated wave-1 desk tools. Local commit subject:
`Add function-preserving affine toggle-model desk tools` (this report is part
of that commit; its resulting hash is in the final handoff).

## Authority and intake

Selected task: Ed's direct ideas 5–6/ENTROPY-DIAL/H4 brief, **[AGENT] DESK**.
Read the two specified design-study documents first, then targeted Mission M0
intake, AGENTS/CLAUDE conventions, source map, orchestration and relevant
decision-log clauses (optional dependencies D-009, gross basis D-067;
stop-card authority D-050). `ACTIVE_STOP_CARD` and global work-selection gates
were NONE. Inspected Current Project Status, restart/next-work lanes, Known
Workspace State, queue intake/current queue and Do-Not-Do-Yet guidance.

The direct brief overrides ordinary queue/kernel edits and full-suite rules.
No coordination files, kernel tasks or advisor-facing status were changed.
No delegation or external consult was used. No network, model downloads,
collectors, live measurements, sealed paths/data or Block-5 analysis pipeline
were used. The running analysis job was not inspected or disturbed. Absolute
paths appearing in source documents were treated as text only.

## Delivered files

- `joulewise/interp_energy/toggle_model.py`: affine 4/8-bit uint32 packing;
  owned float16/float32 metadata snapshots; integer code/scale/bias
  reparameterization; full/masked sign complement; whole-input-group
  permutation with compensating inputs; exact host dequantized-byte gate;
  lazy native materialization/snapshot and native dequantized-pair validator.
- Same module: stride-resolved exact storage descriptors (2–128 bytes),
  separate code/scale/bias counts, randomized ABBA/BAAB schedule using the
  existing rail scheduler, and signed conditional J/proxy-transition estimates
  reusing the lock-in HAC/moving-block bootstrap intervals.
- `joulewise/interp_energy/__init__.py`: lazy public module namespace.
- `joulewise/interp_energy/README.md`: API/discovery and handoff pointer.
- `tests/interp_energy/test_toggle_model.py`: 16 tiny synthetic tests covering
  exact dequantization, scale/offset/sign families, permutation/input inverse,
  byte order, rejection cases, descriptors, estimator recovery, signed/null
  effects, bootstrap endpoints, drift/crossing windows and 80-trial synthetic
  HAC coverage/recovery.
- `tests/interp_energy/test_toggle_model_mlx.py`: two import-gated native tests
  for MLX packing/dequantization, supplied quantized snapshots and exact
  output preservation through the existing rail backend. Only tiny synthetic
  64×256 weights; no model files.
- `docs/research-audits/2026-11-07/toggle-model-run-plan.md`: API examples,
  exactness/identification limits, one proposed 180-minute KM003C-arbitrated
  window, prospective gates, statistics/reading rules and native commands.
- This dated report. No wave-1 algorithms or capture implementations replaced.

## Findings and limits

1. The algebraic complement is not universally bit exact after metadata
   rounding. A synthetic fp16 s=0.1,b=0.03 counterexample is tested and rejected.
   Accepted host transforms have exact reference dequantized bytes. The host
   contract is float64 affine arithmetic followed by one metadata-dtype round;
   native arithmetic is a separate gate.
2. Full complement flips packed Hamming weight while preserving every packed
   XOR distance. A transition-slope denominator of zero is rejected. Mixed
   group polarities change selected strides: an early end-to-end test used
   stride 64 with a period-64 mask and correctly found no contrast. It was
   corrected to the nonzero stride-32 descriptor, not by weakening the check.
3. Group permutation preserves the real affine map after the returned input
   gather/inverse weight mapping. Floating reductions may change native
   outputs; host tests use small exact dyadic tensors, with distinct input
   groups and a non-self-inverse permutation. Native dequantization and exact
   native outputs are mandatory before using any candidate in H4.
4. The fitted coefficient is conditional on storage counts and a supplied
   common dispatch rate. It is not an observed physical bus coefficient and
   its CIs do not include calibration, rate uncertainty, systematic bounds or
   model error. Metadata/input/ALU changes, DBI and compression remain possible
   explanations. Nothing here validates a predictor of surgical edits.
5. The proposed window stays behind the study's block-P non-null gate. DC is
   the arbiter; “DC moves, rail flat” remains admissible. Native residency,
   timing, clock matching, noise cadence and metrology remain unverified.

## Verification

All commands were local, single-process unittest modules, sequentially.
Numerical commands used the existing Python **3.14.6 / NumPy 2.2.6** with
`PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`; no packages were
installed. Python 3.13 lacks NumPy in this clone. `-B` was used for tests.

| Command (environment prefix above omitted) | Result |
|---|---|
| `python3 -B -m unittest tests.interp_energy.test_toggle_model -v` | 16 passed; final rerun also passed after review fixes. |
| `python3 -B -m unittest tests.interp_energy.test_lockin` | 12 passed. |
| `python3 -B -m unittest tests.interp_energy.test_operand_stats` | 6 passed. |
| `python3 -B -m unittest tests.interp_energy.test_rail_data_dependence` | 11 passed; synthetic dry/plan paths only. |
| `python3 -B -m unittest tests.interp_energy.test_integration` | 4 passed, including bare `-S` package import without numerical dependencies. |
| `python3.13 -B -m unittest tests.interp_energy.test_toggle_model -v` | 16 skipped (NumPy absent), importability only. |
| `python3.13 -B -m unittest tests.interp_energy.test_toggle_model_mlx -v` | 2 skipped (optional dependencies unavailable), no native execution. |
| `python3.13 -B -m unittest tests.interp_energy.test_operand_stats` (baseline) | 6 skipped (NumPy absent). |
| `python3.13 -m compileall -q joulewise/interp_energy tests/interp_energy` | Passed. |
| `git diff --check` | Passed. |

**49 distinct numerical tests passed.** Targeted execution stayed far below
the ~20-minute cap. Full/quick/sharded repository suites were deliberately not
run under the direct machine-load instruction. No MLX/Metal result is claimed;
Python 3.11/3.13 numerical compatibility needs the lead's installed NumPy/CI.

## Next exact steps / open gates

On an authorized Metal-capable non-measurement machine, the lead should run,
one module at a time, without downloads:

```sh
python3.13 -B -m unittest tests.interp_energy.test_toggle_model_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

Also run `tests.interp_energy.test_toggle_model` on CI Python 3.11/3.13 with
NumPy. Do not infer numerical/native validation from skips. If native factoring
breaks exact equality, reject the candidate or adjust its synthetic fixture
prospectively; do not relax to allclose and call outputs identical.

Before a future collection, supply a thin prepared-ring driver reusing the
existing rail `cycle`, capture hooks and event stamps. The stock fill-label
runner does not yet accept these prepared encoding pairs. The delivered task
is an encoding/estimator desk library and run plan, not a new acquisition CLI.
That driver, the PSD/cadence pilot, block-P gate, prospective registration and
lead review are later work; no quiet-Mac window has been requested or started.
The run plan lists the timing/rate/residency and claim gates explicitly.

No blocking question for this desk implementation. The uncertainty is native
arithmetic and physical attribution; both are preserved as open gates. Commit
locally only; no push, merge, deployment or publication is authorized here.
