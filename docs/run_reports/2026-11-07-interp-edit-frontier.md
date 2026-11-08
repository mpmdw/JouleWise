# Edit-frontier desk handoff — 2026-11-07

Implemented on the already-selected requested branch
`interp/2026-11-07-edit-frontier`, based on `3c8ce8a5a` (integrated wave 1).
Implementation commit: **`6be2a3f53`**, “Add context-aware edit energy frontiers
and experiment plan.” This report is committed separately. Nothing was pushed.

## Intake, scope and safety

Read the study's lead synthesis/ranking/Stage 2 plan and companion checks for
EDIT-FRONTIER and energy/capability frontiers first, then relevant Mission M0,
RUN_STATE stop-card/status/workspace sections, queue/intake/do-not-do sections,
AGENTS/CLAUDE conventions, source-of-truth map, D-009 and D-067, wave-1 package,
behaviour-channel handoff, and ASTRA registration/analysis draft sections.
There was no active stop card; Git started clean. This is user-directed,
later-research **[AGENT] desk tooling**, not ordinary queue-draining or a
measurement task. No state-kernel task was registered. The explicit brief
overrides coordination-state updates: RUN_STATE, TASK_QUEUE, state_kernel and
test_gen_state are unchanged. No advisor-visible project state was promoted.

No network, model download, production analysis, collector, quiet-window work,
real measurement input, external home-directory data, or real restricted
directory was intentionally accessed. Absolute paths in source prose were
treated as text. No long-running analysis job was inspected or controlled.
Only tiny synthetic item records and temporary test JSON were exercised.
No subagents, external consults, plugins or new dependencies were used.

## Changes and scientific limits

| File | Change |
|---|---|
| `joulewise/interp_energy/edit_frontier.py` | Stdlib `Variant`, `analyze_variants`, `pareto_frontier`; reuses behaviour-channel energy and summaries |
| `scripts/interp_energy/edit_frontier.py` | Explicit-JSON CLI and entirely invented `--demo`; strict JSON/provenance checks |
| `joulewise/interp_energy/__init__.py` | Lazy module export |
| `joulewise/interp_energy/README.md` | API/CLI, assumptions and design-plan link |
| `tests/interp_energy/test_edit_frontier.py` | 16 synthetic accounting, inference, frontier, residual and validation tests |
| `tests/interp_energy/test_edit_frontier_cli.py` | 5 subprocess tests for JSON, demo, validation and input immutability |
| `docs/design/interp_energy_edit_frontier.md` | Estimands, Wu citation, schema example, variant/item/cost proposal, native handoff |
| This report | Verification, uncertainties and next step |

J/correct uses all supplied attempts' energy, including wrong/cap-hit answers.
The energy law includes prefill, decode and integrated context exposure,
`K=p*d+d*(d-1)/2`. Raw tokens are a diagnostic. Main frontiers minimize gross
J/answer or J/correct and maximize accuracy; ties survive. A synthetic test
demonstrates a token-frontier ranking reversed by the context cost.

One bootstrap draw resamples matched independent problem IDs across all
variants, keeping correctness/energy and observation/prediction covariance.
Reports contain marginal percentile CIs for coordinates and paired contrasts,
plus frontier inclusion frequencies. Frequencies are stability diagnostics,
not simultaneous frontier confidence bands or probabilities of superiority.
Zero-correct resamples are not discarded: affected ratio CIs and all inclusion
frequencies for that ratio frontier are withheld. Sparse and boundary
accuracies are flagged.

Optional supplied gross observations produce separate frontiers and paired
`observed delta - behaviour-law delta` residual CIs. Their provenance and
boundary validity remain caller assertions. Residuals do not identify switching.
The tool is not a measurement reader, calibration fitter, claim reducer or
implementation of the complete ASTRA draft. Coefficient, meter and systematic
uncertainty are excluded from these exploratory sampling CIs.

The proposal reuses ASTRA's controls and wave-1 tooling. It treats ThinkEdit
as length-raising, ASC-style compression as a runtime vector, and caps as
treatment settings. With explicit assumed lengths/speeds, core two-model
coverage is about 23.4–37.1 h including stated allowances; strengths extend it
to about 34.5–56.3 h. The core all-cap ceiling is approximately 62 h including
those allowances. These are arithmetic estimates, not observed Mac costs.

## Verification

Modules ran **one at a time**, using unittest, in seconds rather than the
20-minute budget. No full suite, sharding, pytest, native MLX execution, or
Block 5 pipeline ran. Final relevant results:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.interp_energy.test_edit_frontier` | 16 passed, 0.061 s on final run |
| `python3.13 -B -m unittest tests.interp_energy.test_edit_frontier_cli` | 5 passed, 2.232 s |
| `python3.13 -B -m unittest tests.interp_energy.test_behaviour_channel` | 25 passed, 2.135 s |
| `python3.13 -B -m unittest tests.interp_energy.test_behaviour_energy_cli` | 7 passed, 2.221 s |
| `python3.13 -B -m unittest tests.interp_energy.test_integration` | 4 run: import test passed, 3 NumPy-dependent tests skipped, 0.352 s |
| `PYTHONPYCACHEPREFIX=/private/tmp/jw-edit-frontier-pycache python3.13 -m compileall -q joulewise/interp_energy scripts/interp_energy tests/interp_energy` | Passed; caches outside tracked tree |
| `python3.13 -B scripts/interp_energy/edit_frontier.py --demo` | Default 2,000-draw smoke passed; strict JSON parsed; expected three-member J/answer frontier |
| `git diff --cached --check` | Passed before implementation commit |

Total across the five final unittest invocations: **54 passed, 3 skipped**.
The package import test runs with `-S` and confirms all public namespaces load
without NumPy, MLX, Torch or transformers. NumPy is unavailable in this Python
environment; skipped numerical integration is not verification of edit/replay.
An early new-test run failed two CI fixture assertions because fixture numeric
ordering differed from canonical textual problem-ID ordering. The fixtures
were aligned; final manual-ratio and existing-behaviour-channel CI comparisons
pass. The design doc's JSON example was also parsed and analyzed successfully,
including its expected unavailable sparse-ratio CI. Python 3.11 was not tested.
No native hardware result is claimed.

## Open questions and exact next step

No blocking desk question remains. Lead review should first confirm the
counting/input contract in the design doc, particularly the existing behaviour
API's **d** decode charges versus the ASTRA draft's **D−1** boundary, then freeze
matched calibration and evaluation inputs before any future use with real
observations. The new tool does not settle that pre-existing timing question.
Repeated seeds per problem require cluster inference and are rejected here;
do not encode seeds as independent problem IDs. The proposal therefore uses
one paired attempt per independent problem. Sparse baseline success counts
may prevent useful ratio intervals even at 100 items.

Wu's citation is carried from the supplied study/checks; the external source
was not independently fetched under the no-network rule. The context term is
the existing package approximation, not a claim to reproduce Wu's exact fit.
Native throughput, model support, released-diff import/hash validation, local
calibration, battery/meter support and all ASTRA open slots remain unverified.
No established policy was changed and no decision-log ruling was installed.

This component introduces no MLX code/tests. The lead must run the existing
tiny native tests **outside this sandbox**, on an authorized Metal-capable
non-measurement machine, one module per process, with no downloaded weights:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

Their importability gates remain intact; a skip is not Metal validation.
Live collection requires its separately authorized, clean lead-controlled
session. The desk smoke entry point is
`python3.13 -B scripts/interp_energy/edit_frontier.py --demo`.
