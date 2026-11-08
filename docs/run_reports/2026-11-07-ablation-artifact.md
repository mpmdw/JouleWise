# ABLATION-ARTIFACT desk implementation, 2026-11-07

## Intake and authority

Task: ranked idea 12 in the interp × energy design study. Branch
`interp/2026-11-07-ablation-artifact` was already checked out at intake, at
integrated head `3c8ce8a5a`; the worktree was clean. It is the requested local
branch, so no additional branch was created.

Read the study's lead synthesis/ranked row and idea's companion checks, the
repository AGENTS/CLAUDE conventions, Mission M0, targeted restart/stop-card,
status/workspace and queue/do-not-do pointers, authority map, D-009, the wave-1
toolkit/README and relevant handoffs/contracts. No active stop card was found.
The user's explicit bounded task selects this [AGENT] research-preparation
lane ahead of historical queue work. No kernel task was registered and no
coordination state was edited, per the stronger task instruction.

Single-agent, offline desk work only. No network, downloads, real measurement
inputs, sealed directories, block-5 analysis pipeline, quiet-Mac collection,
process census, job signals or external integration were used. Absolute paths
appearing in repository prose remained text. Git used this clone normally;
no other workspace was inspected. No full suite, pytest or MLX execution ran.

## Implementation and changed files

1. `joulewise/interp_energy/weight_edits.py`: factored the existing ablation
   mask construction for reuse; added `AblationReplacement` on the same
   reversible edit lifecycle. Zero, calibration feature mean, explicit whole-row
   resampling, scalar constant and sham work on dense weight/saved-activation
   matrices. Preserves dtype/shape, unselected bytes and exact saved-byte
   reversion. Rejects invalid donor/index shapes, nonfinite calibration and
   post-cast overflow. Existing `WeightSwap` accepts prepared edited states.
2. `joulewise/interp_energy/ablation_artifact.py`: common runtime `where` for
   replacements/patch controls; row/feature transition descriptors using
   `operand_stats`; stdlib-only plan generator and tiny NumPy synthetic CLI.
   No new collector, model loader, measured-energy reducer or native grid runner.
3. `joulewise/interp_energy/__init__.py` and `README.md`: lazy namespace and
   API/design pointers. All public module imports still work without extras.
4. `tests/interp_energy/test_ablation_artifact.py`: synthetic semantics,
   saved-byte restoration, masks/heads, invalid-input atomicity, resident swaps,
   existing reference-model forced replay, dtype/encoding traversal checks,
   analytic IID toggles, counterexample, downstream patch and plan checks.
5. `tests/interp_energy/test_ablation_artifact_mlx.py`: three import-gated native
   tests, tiny synthetic arrays/Linear only, covering all styles/dtypes,
   patching and binding the existing swap to a real tiny module.
6. `docs/registrations/ablation_artifact_v0_draft.md`: derivation and later
   measurement design, direct/propagated split, instrument gates, DC/battery
   boundary, materiality/uncertainty rule and exact native handoff commands.
   **DRAFT NOT REGISTERED**, not authority to measure or reserve hardware.
7. This run report. No settled policy or advisor-visible project state changed.

## Prediction and synthetic output

For IID donor bits with probability p of a one, expected transition density is
`2p(1-p)`. Repeating a feature mean gives zero row-to-row transitions, exactly
like zero or a scalar constant; resampling has positive expected transitions
when donor bits vary. Feature/reduction transitions can distinguish mean from
zero. Thus the study's `zero <= mean < resample` is a conditional energy
hypothesis, not a universal theorem about stored-bit traversals. Tests include
a counterexample reversing mean-versus-resample feature-transition ordering,
and a repeated-donor case without a strict temporal inequality.

Both CLI paths were executed in subprocesses and their complete stdout parsed
as JSON; only bounded summaries were printed. No trace/data files were read or
created. Commands:

```sh
python3.13 -B -m joulewise.interp_energy.ablation_artifact --plan-only
python3 -B -m joulewise.interp_energy.ablation_artifact --synthetic
```

Default plan: 4 placeholder layers × 5 pair contrasts × 2 patch modes = 40
cells; 12 randomized ABBA/BAAB quads/cell = **1,920 members, 5.333 nominal work
hours** at 10 s/member. Uses the existing `lockin.make_schedule` specifications.
This excludes block P (planning 60–90 min), warmup, calibration, idle,
transitions and instrument checks. Actual execution must fix dispatch count,
not run to a style-dependent time target. Session/prompt blocking and exact
chips remain registration pins.

Seed 1212, float32 synthetic `[64,8]` activations and `[128,8]` calibration:

| Style | Row transition density | Within-row feature transition density | One-bit fraction | Restored bytes |
|---|---:|---:|---:|---|
| zero | 0 | 0 | 0 | exact |
| mean | 0 | 0.392857 | 0.515625 | exact |
| resample | 0.421193 | 0.431013 | 0.539917 | exact |
| constant (1) | 0 | 0 | 0.218750 | exact |
| sham | 0.427703 | 0.422852 | 0.548889 | exact |

These are **host storage descriptors, never energy or live hardware evidence**.
The constant arm is intentionally unranked relative to mean in the energy
prediction. The design uses the existing rail ladder as an instrument gate,
then per-layer prefill contrasts. Clean-residual patching separates the
operational direct-plus-intervention term from downstream effects; graph
matching alone does not remove hook switching energy.

## Verification

`python3` is Python 3.14.6 with NumPy; `python3.13` is Python 3.13.18 without
NumPy/MLX. No packages were installed. Every module invocation completed in
under one second of reported unittest time; aggregate testing was seconds,
well below the user's ~20 min limit. No full/sharded/quick suite was invoked.

| Command | Result |
|---|---|
| `python3 -B -m unittest tests.interp_energy.test_ablation_artifact` | 19 passed |
| `python3 -B -m unittest tests.interp_energy.test_weight_edits` | 45 passed |
| `python3 -B -m unittest tests.interp_energy.test_operand_stats` | 6 passed |
| `python3 -B -m unittest tests.interp_energy.test_integration` | 4 passed; includes dependency-free public imports |
| `python3.13 -B -m unittest tests.interp_energy.test_weight_edits_import` | 1 passed |
| `python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact` | 3 passed, 16 skipped (NumPy absent) |
| `python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact_mlx` | 3 skipped (MLX absent); no native execution |
| `python3.13 -B -m compileall -q joulewise/interp_energy tests/interp_energy` | passed |
| `git diff --check` | passed |

Execution caveat: during one verification rerun the new module yielded a
process handle after a 1 s tool wait. The next targeted module was launched
before its completion was collected. It subsequently returned all 19 tests
passing (0.708 s unittest time); overlap cannot be ruled out for that rerun.
No workers were requested and no running analysis job was inspected or touched.
This was a deviation from the requested strictly serial test-launch discipline.

## Open pins, uncertainty and next exact step

No energy was measured. Native MLX behavior is unverified; its import-gated
tests skipped here. In particular, a logical MLX copy does not certify distinct
physical A/A′ buffers, and lazy graph simplification, actual model hooks,
cache equivalence, resident bytes, equal dispatch/kernel paths and timing have
not been validated. Python 3.11 tests and Python 3.13 numerical tests with NumPy
also remain for the lead/CI environment.

The planner does not freeze a model, layer mapping, calibration/evaluation
split, sample count, exact masks/donor indices, dtype/kernel policy, dispatch
count, independent-session count, null SD, uncertainty bounds, multiplicity,
clock tolerances or claim-size materiality threshold. These are listed in the
design and returned by the planner. They do not block this desk deliverable;
they block measurement/registration. No science/naming ruling was invented.

Next: on a separate Metal-capable **desk** Mac with already-installed deps,
run these individually, waiting for each to finish:

```sh
python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact_mlx
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx
python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact
```

Then validate a tiny model's hook and clean-patch graph. Only the lead can
propose/seal a quiet-Mac block P and later grid; no window is requested here.
The materiality test compares a systematic-bound-widened style-contrast
interval with a tolerance set from the intended interp claim scale; lack of
significance alone never establishes that style is irrelevant.

## Local delivery

All eight changed files are committed together on the requested local branch,
with title `Add ablation styles and a desk energy-artifact plan`. The final
reply gives the commit ID. No push or merge; coordination files and immutable
evidence remain untouched.
