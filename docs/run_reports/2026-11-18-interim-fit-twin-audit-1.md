# Independent interim-fit twin audit round 1 · 2026-11-18

The auditor blocked draft PR #816 at `ac5e4db87` with three verified high
findings, one verified medium finding, one verified low observation and one
refuted low finding. The twin's four changeable findings reproduced before
the patch and passed afterward at `5b9ebe7c6`.

## Findings and regressions

| Finding | Disposition and commit | Regression in `tests.test_cadence_interim_twin` | Result |
| --- | --- | --- | --- |
| HIGH, nested `result.bundle` | `5b9ebe7c6` validates the whole relative path below the named leg runtime. Traversal, absolute paths and symlink escapes refuse. | `test_span_override_and_runtime_bundle_containment` | PASS |
| HIGH, overlapping GPU Trace rows | `5b9ebe7c6` integrates every clipped row for both energy and coverage. Gap detection still tracks the rightmost covered edge. | `test_gpu_overlap_counts_every_row_in_trace_energy_and_coverage` | PASS |
| HIGH, false fold-drop verdict when the main onset is unavailable | `5b9ebe7c6` reports fold drops relative to the main delta column. An available main column still reports the individual missing folds. | `test_no_main_delta_is_not_reported_as_a_fold_drop` | PASS |
| MED, inventory path with `--span-dir` | `5b9ebe7c6` resolves logical span IDs through the selected directory map before checking hashes. Absolute paths already naming selected span inputs also work. | `test_inventory_uses_the_selected_span_for_logical_paths` | PASS |
| LOW, private numeric child stdout and unverified production launcher | The test parent captured the permitted numeric frame privately. Leave production capture, timeout, and malformed-frame verification with the parent integration lane. | `test_actual_child_argv_on_fully_bound_raw_bundle`, `test_isolated_child_private_capture_and_closed_failure` | PASS on synthetic child capture. Production parent follow-up. |
| LOW, alleged primary import or copied implementation | Refuted by the auditor. RL-183a authorizes the shared decoder. | Registered-decoder import audit in `test_actual_child_argv_on_fully_bound_raw_bundle` | PASS |

## Acceptance evidence

The actual isolated child passed the hand-derived raw fixture using the
registered decoder and initializer. The fixture combines a moved span with
logical inventory keys, nested `runs/cadence-leg` paths, overlapping GPU
intervals, and a one-cell onset model. Both fits and their folds compared,
including the marked-span projection. The parent produced `yes` on the
reference, `no` for the perturbation and `not_evaluable` for the missing and
changed inputs. All 24 focused tests passed with NumPy. The bare-Python
focused and documentation checks ran 107 tests with six NumPy-dependent
skips. Generated state and typed items agreed.

The tested `scripts/cadence_interim_twin.py` SHA-256 is
`504b2c11bef344d21e599745a1d627e73188e35f6dc25c996720b5d0d0848c49`.
It supersedes the pin in the earlier acceptance report. The builder used
synthetic fixtures and the audit's reported facts. The primary source and
the auditor's primary-importing probes were kept out of execution. The
audit's temporary raw fixture was no longer present for a comparison-only
rerun. The next gate is the fresh audit against generated primary fixtures
and the actual synthetic fit outputs. The parent integration owner still
owes the production launcher checks listed above.
