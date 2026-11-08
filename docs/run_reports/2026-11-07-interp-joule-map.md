# JOULE-MAP desk implementation and handoff

2026-11-07. **PROVISIONAL — synthetic evidence only.** Branch
`interp/2026-11-07-joule-map` already existed at intake, clean, based on
`3c8ce8a5a` (integrated wave 1). Implementation commit: **`200152c1b`**, *Add
desk JOULE-MAP component interventions and energy attribution*. This report is
the subsequent documentation commit; both remain local, with no push.

## Scope and authority

Executed the user's ranked-idea-9 brief as an isolated desk task. Read the local
design study and targeted JOULE-MAP checks, repo AGENTS/CLAUDE guidance, Mission
M0, generated stop-card/queue pointers, and targeted dependency/boundary policy.
No stop card/global selection gate was active. The user's explicit task selected
this work; no kernel task was registered. Their binding restrictions supersede
normal full-suite and coordination closeout requirements.

No network, model downloads, real measurement inputs, Block 5 pipeline,
collectors, power measurements, process/job inspection, or full-suite execution.
The running blinded analysis job was not controlled. Absolute data paths in
source documents were treated as text. No prohibited external or real
`restricted/` paths were accessed. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, and `tests/test_gen_state.py` were not edited.
No delegation, external consult, integration installation or publication.

## Delivered

- `joulewise/interp_energy/component_intervention.py`: explicit array-output
  gate for full, retained-compute/clamped and removed-compute arms. Both latter
  arms return the same resident tape; retained outputs are evaluated before
  discard, defeating MLX lazy elimination. Replays reset/validate tape cursors.
  A lazy `mlx.nn.Module` wrapper keeps original parameters registered/resident.
- `joulewise/interp_energy/joule_map.py`: randomized six-member palindromes;
  fixed-work/weight/policy/tape identity checks; common-time interpolation with
  actual timestamps; gross and above-idle raw/control/corrected J/token; matched
  circular block-bootstrap pointwise CIs; conservative systematic sensitivity
  intervals; covariance-preserving additivity audits and prospective budgets.
  Context and physical boundaries stay separate. Negative marginals are kept.
- `scripts/interp_energy/joule_map.py`: stdlib-only plan, seven-target synthetic
  demo and named-JSON reduction. No collection/execution path, recursive
  discovery or nested path dereference. Invalid JSON/identities fail closed.
- `tests/interp_energy/test_joule_map.py`: 12 synthetic analysis/CLI tests.
- `tests/interp_energy/test_component_intervention.py`: 3 NumPy tests, including
  real wave-1 forced replay/fresh growing KV caches, output clamps, dispatch
  counts and reversible dense weight zeroing. Dense zeroing retains computation.
- `tests/interp_energy/test_joule_map_mlx.py`: four import-gated native tests,
  using only a tiny randomly initialized two-layer Llama (attention, MLP,
  embedding, head). Native execution remains **unverified**.
- `joulewise/interp_energy/__init__.py` and `README.md`: lazy namespaces and
  usage/native handoff pointers.
- `docs/design/interp_joule_map.md`: estimands, correction, platform novelty,
  CLEAR/HYMELL citations, architecture gates, uncertainty and banked run plan.
- This run report: coordination handoff, deliberately outside lead-owned state.

The new tools reuse forced decode, parameter identity/edit/revert and power
planning from wave 1. Behavior projection stays in `behaviour_channel`; there
is no second generation loop, edit engine, energy-count model or collector.

## Method and synthetic result

Raw F−S credits changes in downstream operands and idle duration to the removed
target. C−S holds downstream output values fixed. The reported correction is
`(F−S)−(F−C)=C−S`, with each energy divided by the identical decode count. It
prices retained computation under a declared replacement trajectory and
instrumented schedule. Reference-output tapes are primary; zero tapes are a
sensitivity test. F−C remains a control shift, not a pure semantic behavior
effect. Free-running count/context accounting and the exact later crossover
decomposition are documented separately.

The seeded demo (`--demo --seed 0`, 2000 bootstrap replicates) produced these
**invented** above-idle marginal energies on `synthetic_dc`, all in J/token:

| Target | Synthetic truth | Estimate | Pointwise 95% bootstrap CI |
|---|---:|---:|---:|
| embedding | 0.001 | 0.0010027 | [0.0008712, 0.0011257] |
| layer0 attention | 0.020 | 0.0199031 | [0.0197465, 0.0200706] |
| layer0 MLP | 0.040 | 0.0398519 | [0.0397102, 0.0400153] |
| layer1 attention | 0.018 | 0.0180901 | [0.0178981, 0.0182829] |
| layer1 MLP | 0.038 | 0.0380615 | [0.0378954, 0.0382157] |
| LM head | 0.015 | 0.0149824 | [0.0147985, 0.0151606] |
| layer0 joint | 0.055 | 0.0549617 | [0.0548162, 0.0550997] |

The joint audit deliberately violates additivity: true sum(parts)−joint=0.005;
estimate 0.0047932, bootstrap CI [0.0044832, 0.0050861], sensitivity interval
[0.0027432, 0.0068261]. It fails the declared ±0.002 budget. This is a fixture
demonstration, not evidence of actual hardware non-additivity or coverage.
The standalone JSON was written only to `/private/tmp/joule-map-synthetic-demo.json`;
it is regenerable and not a measurement artifact.

## Verification

Tests ran as separate modules, one process at a time. No dependencies installed.
`python3` is the existing Python 3.14/NumPy installation; Python 3.13 lacks NumPy.
Final relevant commands used `PYTHONNOUSERSITE=1` and `-s`; NumPy commands also
used `OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1`.

| Command (after environment prefix) | Result |
|---|---|
| `python3.13 -B -s -m unittest tests.interp_energy.test_joule_map -v` | 12 passed; final run 3.06 s |
| `python3 -B -s -m unittest tests.interp_energy.test_joule_map -v` | 12 passed; 3.83 s |
| `python3 -B -s -m unittest tests.interp_energy.test_component_intervention -v` | 3 passed; 0.12 s |
| `python3.13 -B -m unittest tests.interp_energy.test_component_intervention -v` | 3 skipped: no NumPy |
| `python3 -B -s -m unittest tests.interp_energy.test_integration -v` | 4 passed; 0.43 s |
| `python3.13 -B -s -m unittest tests.interp_energy.test_integration -v` | 1 passed, 3 skipped: no NumPy |
| `python3.13 -B -S -m unittest tests.interp_energy.test_joule_map_mlx -v` | 4 skipped; bare import gate only, no MLX/Metal execution |
| `python3.13 -B -s -m compileall -q joulewise/interp_energy tests/interp_energy scripts/interp_energy` | Passed, including final native-test syntax |
| `python3.13 -B -s scripts/interp_energy/joule_map.py --plan-only` | Passed; 12 six-member units per two-hour single-target budget, illustrative assumptions |
| `python3.13 -B -s scripts/interp_energy/joule_map.py --demo --seed 0` | Passed; synthetic estimates above |
| `git diff --cached --check` | Passed before implementation commit |

Tests cover exact linear-drift removal with unequal durations, behavior-control
correction, 6 J of idle-duration credit, null/negative marginals, non-shrinking
systematics, strongly correlated paired additivity, independent-unit Monte
Carlo coverage (80 seeded populations, broad tolerance), stratification and
malformed-input refusals. CLI tests run with `-S` to exclude optional backends.
Total targeted test runtime, including development reruns, was under one minute,
far below the requested ~20-minute ceiling. Full/canonical/quick suites were
intentionally not run under the user's explicit blinded-job restriction.
Python 3.11 was unavailable and remains a CI compatibility check.

## Remaining uncertainty and next exact step

1. On an authorized Metal-capable **non-measurement** Mac, outside this sandbox,
   with dependencies already available, run:
   `python3.13 -B -m unittest tests.interp_energy.test_joule_map_mlx -v`.
   Four skips here establish no native correctness. MLX/`mlx-lm` API compatibility,
   actual parameter registration, native cache/logit parity and execution of
   discarded results still need that test. Known Llama slot-name variants are
   handled in the bounded native test, not by production model discovery.
2. Complete an architecture-specific cache-position adapter before all-layer
   attention mapping. A shared mask derived from cache[0] can break when its
   attention update is skipped. The new native attention test uses the last
   layer. MoE indices/mixing replay, shared hybrid state, tied-head behavior,
   tuple-returning modules and compiled graphs are not certified.
3. Native tape residency, paging avoidance, finiteness and call-order parity
   must be checked before proposing collection. Natural head tapes can occupy
   ~1 GiB at 4096 calls and 128k bf16 logits; footprint is a real design gate.
4. These are instrumented conditional marginals. Clamp/materialization overhead,
   nonlinear/schedule-correlated drift, frequency shifts and sampling anchors
   need fresh nulls and prospective bounds. Caller-supplied digests/bounds are
   assertions, not authenticated evidence. The map is not a claim-bundle issuer.
5. CIs are pointwise approximate percentiles. Block length one assumes independent
   units. Select correlation length, sample size, multiplicity and additivity
   budget from an independent pilot before freezing a confirmatory analysis.
6. CLEAR/HYMELL descriptions were inherited from the provided audit; no fresh
   literature verification was performed under the no-network rule. Broader
   Apple/pruning overlap still needs review before any novelty claim.

After native parity/adapters, the lead may allocate a small, separately authorized
agent-free pilot. The full illustrative 8-target ×3-context ×12-unit grid costs
48 member-hours before overhead. No window was scheduled, and no hardware
claim or immediate Mac action is implied by this handoff.
