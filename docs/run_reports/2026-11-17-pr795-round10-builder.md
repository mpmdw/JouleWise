# PR #795 Builder E round 10, 2026-11-17

Direct user priority on `align/2026-11-14-fit-interim` from `a33b37a00`.
Mission M0 selected the agent lane. No stop card was active and the worktree was
clean at intake. One writer worked from the Astra design and window-schedule
final reports in the audit scratch directories. The local checks use in-memory
synthetic inputs, mocked file boundaries and derived manifest fixtures. Hosted
checks and the PR-body readback are recorded on PR #795.

| Finding | Repair and regression |
|---|---|
| WS 1 | Derive the receipt date in Los Angeles and require roster agreement. `test_receipt_epoch_overrules_the_roster_date_at_the_la_boundary` covers the two audit labels, a UTC-boundary label and the subsecond local-midnight boundary. `test_level_r_rejects_false_or_impossible_date_before_folding` checks the direct input route. `test_span_ledger_rejects_impossible_dates` checks impossible calendar dates in roster resolution. |
| Design 4 | Freeze the onset coefficients and scatter for every held-out day, with null recording a dropped onset. `test_frozen_fold_onsets_reproduce_the_reference_day_jackknife` replays the 11.64 J GPU jackknife SE from canonical Freeze 2 and the reference leg. Substituting full-fit onset gives 18.28 J. |
| Design 7 | Add the paired `realized_onset` synthetic world. `test_realized_onset_world_keeps_predictors_but_changes_responses` checks the drawn-onset overlap for the planted response and the held-out error comparison on the same design. |
| Design throughput 1 | `test_dependent_full_design_refuses_before_opening_responses` reproduces the audit's collinear fan and temperature readings after ordinary stage-1 checks clear. `test_dependent_fold_refuses_before_opening_responses` isolates rank loss to one held-out day. Both tests guard the response-open boundary. |
| Design throughput 2 | `test_channels_share_onset_fits_and_factorizations` checks 11 onset fits and 22 rank factorizations over the main and marked-spans fits, with channel-specific residuals and covariance. `test_cli_reuses_the_blind_design_for_fit_and_freeze` checks that the CLI reuses the completed preflight through both outputs. |

The audit regressions reproduced on the old implementation. The synthetic world
regression failed at scenario selection because that world was absent. The focused
fit, predict, roster, schema, manifest and mocked CLI suite ran 147 tests with one
optional skip. Manifest pins, generated-view freshness and `git diff --check`
passed. All 144
existing mutation selectors resolve and compile after updating their source
anchors. A direct byte comparison of the seven existing worlds at seed `20261114`
matched the old stage-1 and fit outputs, including keyed residuals and prefix bias.

Hosted shard 9 caught the synthetic generator's expanded usage docstring because
the host-command inventory fingerprints the original isolated-Python usage text.
The follow-up restores that text and retains the comparison command here and in
CLI help. The host-command inventory regression passes on the follow-up.

## Held-out hot error

`python3 -I scripts/cadence_look_synth.py --compare-hot --seed 20261114` compares
both worlds with the same synthetic inputs, random draws and frozen predictors.
Each world fits its own response coefficients. All five days are counted.

| World | Channel | Max absolute day error | Per-leg RMS | Pooled signed error |
|---|---|---:|---:|---:|
| Expected onset | GPU rail | 0.515% | 0.720% | +0.070% |
| Drawn onset | GPU rail | 0.791% | 1.111% | +0.328% |
| Expected onset | DC-in | 0.173% | 0.484% | −0.018% |
| Drawn onset | DC-in | 0.457% | 0.713% | +0.178% |

## RL-175 follow-up

The clean resumed head was `0b93be9f7`, with the same tip locally and on origin.
The research lead ruled on the audit branch at `b26c0d0e7`.

| Ruling | Implementation and regression |
|---|---|
| B.3, design 1 | The public fit carries only aggregate diagnostics and the restricted SHA-256. A committed run writes the custody-only artifact with owner-only permissions before public outputs. `test_public_outputs_block_astras_keyed_residual_reconstruction` runs the audit's calculation on stage 1, the public fit and Freeze 2. The previous code reconstructs 53 of 53 synthetic totals for each channel within 1%. The split reconstructs zero. `test_single_fit_leg_day_is_restricted_without_a_pooled_backdoor` checks that a sparse day cannot be recovered by subtracting the released days from the pool. |
| B.3, release boundaries | `test_assemble_refuses_keyed_residuals_and_sparse_day_lines`, `test_ledger_records_restricted_digest_from_public_output`, `test_restricted_destination_keeps_existing_bytes_and_owner_only_mode` and `test_restricted_comparison_prints_only_the_maximum_difference` cover the public schema, digest handoff, file mode and comparator. |
| B.4, design 8 | `test_prefix_bias_centres_both_statistics_on_equal_day_means` reproduces the 12/1/1 allocation. Both the estimate and its 90% t interval use the mean of day means. The registered scaling and null rules still apply. |

The twin check uses a source-only scratch copy of the retained independent v5.2
twin under `sol62-E-look/rl175-twin`, with builder-authored changes for the new
disclosure, equal-day weights and frozen fold fields. The comparison uses only
generated in-memory fixtures and publishes only aggregate comparison evidence.
All nine cases agreed, including the sparse-day fixture. The comparator's
maximum absolute difference was `1.2232188439237346e-10`. The sparse fixture's
prefix interval differed by under `1e-9` absolute, which the comparison uses
alongside `1e-8` relative for near-zero interval endpoints. The focused suite
ran 155 tests with one optional skip. This builder-authored compatibility check
leaves the fresh lead review gate open.

## NEEDS_RULING

- **Design 5, load redo.** Which runner and desk change will move both sustained
  load decisions to monotonic elapsed time? I recommend one coordinated change
  with independent runner and hand-desk tests for 56 samples over 60.5 s and
  60 samples over 58.41 s. The calls are in `scripts/cadence_legs_runner.py:299`
  and `:715`, with the sample-count rule in `scripts/align_r1_rehearsal.py:813`
  and `:852`. Astra points to the independent hand reader's `hand_table.py:28`.
  Those paths are outside the PR diff.


## 2026-11-18 resumed RL-175 verification

### Intake and write scope (before edits)

The first branch-history read after fetching the requested refs found only
`d3fb89dfd` after `0b93be9f7`. The PR body already describes all four owed repairs;
code inspection confirms them. The worktree was clean and no stop card was active.
The environment initially checked out an unrelated `work` branch; no conclusions
or write authority were taken from that branch's diff. It was switched to the
requested head before this inventory or any edit.

The requested `git diff --name-only origin/main...HEAD` enumerated **3578**
paths against main `2a0434037f08ed32b2cd755f52085ad1c707f3f0` (merge base
`d842f697f37a95a439dbb89927185b4b6e4fb1ea`). Its newline-terminated path inventory
has SHA-256 `8e007e1d207b2d04c9c9c19fe6405c69e1e9da629d5c51a9005530d70cde9d43`. That wide comparison includes earlier stacked work.
The actual PR base is `9a7defbb9ff04d7a5c182c874edd924618afce27`; its **43** paths
are listed below. This session deliberately uses that narrower set for writes.
The final write set is `tests/cadence/test_look_run.py`,
`joulewise/cadence_looks/fit_interim.py`, its draft manifest
`docs/process/cadence/looks/lm-interim-01.json`, the manifest digest in
`docs/process/cadence/looks/LOOKS.json`, and this existing PR run report.
No RUN_STATE or TASK_QUEUE edit is needed or made.

```text
.github/workflows/ci.yml
RUN_STATE.md
TASK_QUEUE.md
docs/process/cadence/looks/LOOKS.json
docs/process/cadence/looks/evidence/2026-11-15-q11-drift-10k-REPORT.md
docs/process/cadence/looks/lm-interim-01.coefficients.schema.json
docs/process/cadence/looks/lm-interim-01.json
docs/process/cadence/looks/lm-interim-01.output.schema.json
docs/process/cadence/looks/lm-interim-01.stage1.schema.json
docs/process/cadence/looks/look_manifest.schema.json
docs/process/cadence_look_fit_interface.md
docs/process/cadence_look_manifest.md
docs/run_reports/2026-11-15-pr795-round7-builder.md
docs/run_reports/2026-11-16-pr795-round8-builder.md
docs/run_reports/2026-11-16-pr795-round8-invocations.jsonl
docs/run_reports/2026-11-16-pr795-round9-builder.md
docs/run_reports/2026-11-16-pr795-round9-invocations.jsonl
docs/run_reports/2026-11-17-pr795-round10-builder.md
joulewise/cadence_looks/fit_interim.py
joulewise/cadence_looks/inclusion_34.py
joulewise/cadence_looks/manifest.py
joulewise/cadence_looks/schema_check.py
joulewise/cadence_looks/step3_roster.py
joulewise/cadence_looks/time_fields.py
scripts/cadence_look_manifest.py
scripts/cadence_look_run.py
scripts/cadence_look_synth.py
tests/cadence/look_fixtures.py
tests/cadence/look_minirepo.py
tests/cadence/mutants_fit_interim.py
tests/cadence/schema_lite.py
tests/cadence/test_fit_interim.py
tests/cadence/test_inclusion_34.py
tests/cadence/test_look_manifest.py
tests/cadence/test_look_run.py
tests/cadence/test_predict.py
tests/cadence/test_round6_diagnostics.py
tests/cadence/test_round6_guards.py
tests/cadence/test_round7_admission.py
tests/cadence/test_schema_check.py
tests/cadence/test_step3_roster.py
tests/cadence/test_time_fields.py
tests/host_command_sites.json
```

### Already on the incoming head

- `d3fb89dfd`: B.3 separates leg-keyed residuals and days with fewer than three
  fit legs into a custody-only file, writes it owner-only before public artifacts,
  publishes its digest, and hands that digest to the ledger. Public pooled lines
  exclude withheld days to prevent subtraction from revealing a sparse day.
- `d3fb89dfd`: B.4 uses the mean of standardized day means for both the estimate
  and `mean ± t(0.95,D-1)*SD(day means)/sqrt(D)`. Length-specific scaling, null
  cases and the ruled constants remain unchanged.
- `67623ba03` (before `0b93be9f7`): Freeze 2 contains each fold's onset coefficients
  and scatter, with null for a dropped onset; held-out prediction uses those
  parameters. Dates come from the receipt epoch in Los Angeles, checked against
  the roster. Full and required fold designs are selected and checked for rank
  before outcome loaders, with shared preflight for fit and Freeze 2.

Authority fetched: `audit/2026-11-10-fable` at
`27cc1338b31558fd90331eefdbabb73e86a9c2a3`, RL-175 B.2/B.3/B.4 in
`docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
No substantive discrepancy with the brief was found. The fold-parameter obligation
is explicitly in B.2, alongside the receipt-date obligation; B.3/B.4 set the
release classes and the prefix-bias estimand.

### Added end-to-end evidence

`RL175Cli` generates the `noisy` world, writes production-shaped custody (GPU
traces, meter streams, receipts, bundles, journals and roster), and runs both real
CLI entry points as isolated subprocesses. A temporary mini repository uses real
pin checks, a committed manifest, a committed stage-1 hash/roster/verdict ledger,
and the real fit and Freeze 2 writer. No fit, loader or publication boundary is
mocked. Inputs and outputs in this test are entirely synthetic. The committed
path is intentional: draft runs only emit restricted bytes when explicitly asked.

| New test | Before: `0b93be9f7` source | After: `d3fb89dfd` source |
|---|---|---|
| `test_public_attack_fails_but_custody_recovers_truth_with_noise_bound` | FAIL: public outputs recover 106 channel/leg totals (53 per channel), expected zero | PASS: zero recovered; custody artifact exists, mode 0600, SHA matches; synthetic GPU planted means recovered within derived noise bound |
| `test_unequal_day_bias_estimate_and_interval_from_cli_responses` | FAIL: first estimate -0.021803074540231653 versus equal-day -0.018585574141867966 (difference 0.0032175003983636874) | PASS: both channels, all three lengths, estimate and interval agree with independently aggregated day means |

The red control overlays only historical pinned production/manifest/schema files
in the temporary mini repository, re-pins that copy and runs the same new tests.
Both CLI stages complete successfully; failures reach the intended assertions,
with two failures and no errors. The working branch is never rolled back.

The truth-recovery bar is derived beside its assertion: the generator adds one
independent segment error of SD `seg_sd_j` per segment and one common leg-power
error of SD `leg_power_sd_w`. Thus total variance is
`n_segments*seg_sd_j² + duration²*leg_power_sd_w²`; the assertion uses six times
its square root (two-sided Gaussian tail <2e-9 per leg). GPU piecewise-constant
integration preserves that plant. The attack's 1% tolerance is prescribed by
RL-175, separately from this noise bar. The bias formula check allows accumulated
binary64 rounding, derived beside its assertions; it uses no exact float equality.
The existing 12/1/1 allocation and sparse-day unit regressions remain in place.

### Decisions I made

- Treat the four owed production repairs as complete after verifying the incoming
  source, rather than duplicating them. Add missing subprocess evidence.
- Repair the reproducible baseline singular-Hessian exception using the existing
  failed-convergence result, as described below. This installs no new threshold.
- Exercise a committed synthetic ledger so the residual custody write happens
  through the production publication path.
- Use all five generator days with their unequal surviving pair counts for the
  CLI bias check; retain the existing direct 12/1/1 test as a separate regression.
- Read only generated synthetic responses and restricted outputs; no campaign,
  real meter, power, energy, slot data or external scratch twin is opened.
- Run only focused modules and modules importing the changed test helper;
  `JW_B5_SYNTHETIC_ONLY=1` is set on every run. CI owns whole-suite execution.
- Leave the historical Design 5 load-redo question outside this bounded task.
  No ruling is needed for these test/report-only changes.

### Verification results

The stable final run used Python 3.12 and CI-pinned NumPy 2.2.6 in an
isolated temporary virtual environment: **333 tests PASS, 0 failures, 0 errors,
0 skips, 869.640 s**. Every test invocation used `JW_B5_SYNTHETIC_ONLY=1`.

| Module | Tests | Result |
|---|---:|---|
| `tests.cadence.test_fit_interim` | 84 | PASS |
| `tests.cadence.test_predict` | 16 | PASS |
| `tests.cadence.test_look_run` | 71 | PASS |
| `tests.cadence.test_time_fields` | 44 | PASS |
| `tests.cadence.test_round7_admission` | 10 | PASS |
| `tests.cadence.test_round6_guards` | 12 | PASS |
| `tests.cadence.test_round6_diagnostics` | 9 | PASS |
| `tests.cadence.test_look_manifest` | 87 | PASS |

`test_look_manifest.FreezeCommit` is intentionally omitted because it recursively
runs a broader suite; the user reserves the whole suite for CI. All other tests
in these eight modules ran. The five changed paths are all within the actual
43-file PR inventory above. Final manifest validation: draft, zero placeholders;
dry pin: zero changes; `git diff --check`: PASS. The production source and pin
files did not change during this stable run. No CI, fresh cold-review, merge or
real-data validation is claimed by these local results.

The initial unmodified-source baseline on NumPy 2.3.5 ran 168 tests with one
error, the singular-Hessian convergence regression repaired below. A separate
single-test check reproduced that error with CI-pinned NumPy 2.2.6 before repair.
The two new B.3/B.4 tests first passed on `d3fb89dfd`; their historical-source
control ran two tests with exactly two intended failures and no setup errors.
The singular-onset CLI test first failed, then it and the existing convergence
test passed together after repair (2 tests).

An intermediate importer run (`test_time_fields`, `test_round7_admission`,
54 tests) overlapped the source/pin update and finished with three stale-pin
failures in `TraceClausesThroughTheCli`. That run is invalidated, not claimed as
a source failure or a pass. The final run below begins after all production and
pin edits, on a stable source tree, and supersedes it.

NEEDS_RULING for this task: none. Existing nonsingular fits keep their arithmetic;
the singular case now follows the already-ruled non-convergence path. Only the
fit-code pin and corresponding draft-manifest ledger digest change; no estimator
constant, data-selection rule or coefficient format changes.

### Baseline defect repaired within the allowed fit module

The untouched incoming fit failed
`tests.cadence.test_fit_interim.RL166b.test_b5_convergence_test` with
`numpy.linalg.LinAlgError: Singular matrix` on both environment NumPy 2.3.5 and
CI-pinned NumPy 2.2.6. A rounded eigenvalue of a singular negative Hessian can be
positive; the subsequent linear solve must still be allowed to fail convergence.
`convergence_test` now catches only that solve's `LinAlgError` and returns its
existing `passes=False`, unavailable-decrement result. All thresholds stand.

Added `AstraPreResponse.test_singular_onset_keeps_rank_refusal_before_responses`:
generate `noisy`, seed 3, make the fan reading 100 times temperature (dependent
onset predictors), and run the real stage-1 CLI. **Before:** exit 2 with
`FAILED LinAlgError`; the new test fails expecting the successful stage-1 output.
**After:** stage 1 completes with onset not estimable; stage 2 refuses the
rank-deficient design before opening a sentinel response file, as proved by an
open audit hook. The original convergence regression also passes. The noisy
custody test above supplies the corresponding successful-fit truth control with
its explicitly derived six-sigma bar.

The draft manifest was re-pinned using the real `pin --write` command. Exactly
the fit source digest and the manifest digest in LOOKS.json change. No committed
campaign manifest or ledger row is replaced.


### Focused reproduction

Use CI's pinned `numpy==2.2.6` in an isolated environment. Every test invocation
carries `JW_B5_SYNTHETIC_ONLY=1`; set `OPENBLAS_NUM_THREADS=1`,
`OMP_NUM_THREADS=1` and `PYTHONDONTWRITEBYTECODE=1` as well. The final run selects
all cases in the eight modules in the results table except
`test_look_manifest.FreezeCommit`, whose recursive suite would widen this task's
test scope. No whole-suite or fresh cold-review pass is claimed.

The three new CLI regressions alone can be reproduced with:

```bash
JW_B5_SYNTHETIC_ONLY=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest -v \
  tests.cadence.test_look_run.RL175Cli \
  tests.cadence.test_look_run.AstraPreResponse.test_singular_onset_keeps_rank_refusal_before_responses
```

For the historical B.3/B.4 control, temporarily wrap
`tests.cadence.look_minirepo.mini_repo` before loading `RL175Cli`: after calling
the original helper, overlay each already-present non-test file in
`git diff --name-only 0b93be9f7 d3fb89dfd` with its `git show 0b93be9f7:PATH`
bytes, run that copy's real `cadence_look_manifest.py pin --write`, then commit
that copy with `look_minirepo.git_commit`. Load and run the same two test methods.
The valid red-control condition is `testsRun == 2`, two failures and zero errors;
a setup/pin refusal is not a valid control. This is the executed procedure, not
a reversal of the working branch.

Final fit source SHA-256:
`228bdffc7f38043a9155c9f473b128d0f72700ef85b7c00db8bd638d097d8303`.
Draft manifest SHA-256:
`fc8d3efb375328d5efba4cf6eedbba0451ae936b736b6c790501a722b0c7aaad`.
