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
