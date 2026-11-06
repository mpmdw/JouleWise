# `tests/b5_analysis` speed report

Date: 2026-11-06 (UTC). All commands used only the repository's committed
synthetic fixtures. `JW_B5_SYNTHETIC_ONLY=1` was used for suite discovery runs;
no experiment-data path was opened.

## Slow-module census

The checked-in hosted timing census (`scripts/test_timings.json`) identifies the
largest modules as `test_sources_replay` (1,310.988 s),
`test_shared_physics_cache` (281.073 s), `test_bracket` (274.346 s),
`test_dry_run` (262.577 s), and `test_validator_context` (203.478 s). These are
module wall observations used as scheduling weights, not newly claimed hardware
measurements. The initial local pytest probe reached 89 passed tests before it
was stopped after 380.22 s; its completed-test durations found
`test_analysis_work_counts` at 68.97 s and the transfer-manifest test in
`test_analysed_windows_index` at 16.12 s.

## Changes

* `scripts/shard_tests.py` now accepts `--start-directory`. The existing
  deterministic, timing-weighted worker implementation can therefore execute
  this suite alone with
  `JW_B5_SYNTHETIC_ONLY=1 python3 scripts/shard_tests.py --workers 4 --start-directory tests/b5_analysis`.
  Every discovered module is still assigned exactly once; worker children
  receive the same start directory. This uses process isolation, so mutable
  module globals and temporary fixture trees are not shared across workers.
* `AnalysedWindowsIndexTests` now loads the immutable seal pins, tracked window
  index, and raw index JSON once in `setUpClass`, rather than repeating the
  identical parse/validation in every test method. Assertions and inputs are
  unchanged.
* `tests/test_shard_tests.py` proves subtree discovery is nonempty, contains a
  known B5 module, contains only `tests.b5_analysis.*`, and excludes the runner's
  own test module. Existing partition tests continue to prove full/disjoint
  coverage for discovered modules.

## Before and after

A bounded six-test sample was used because the checked-in census says the full
suite's slowest module alone takes about 21.8 minutes. Both runs were green and
used the same two modules and six tests (one synthetic-only skip):

| Measurement | Command/shape | Wall | User | Sys |
|---|---|---:|---:|---:|
| Before, serial | one `unittest` process: `test_analysis_work_counts` then `test_analysed_windows_index` | 88.012 s | 87.186 s | 0.650 s |
| After, isolated parallel | the same two module commands in two child processes | 74.541 s | 93.934 s | 0.945 s |

That bounded wall time fell by 13.471 s (15.3%). CPU time rose, as expected for
parallel execution. The cached-index module was then measured alone after the
change: 15.520 s wall (15.210 s user, 0.313 s sys), five tests with one
synthetic-only skip. The prior same-module observation in the paired parallel
run was 20.084 s and the initial pytest observation was 16.12 s; because these
are single observations under differing load, they demonstrate removal of
recomputation and output equivalence, not a stable percentage claim.

## Coverage and equivalence

`python3 -m unittest tests.test_shard_tests` passed 7/7, including the new
subtree-coverage assertion. `python3 -m unittest
tests.b5_analysis.test_analysis_work_counts
tests.b5_analysis.test_analysed_windows_index` passed all six selected tests
(one expected synthetic-only skip). The tests compare the same tracked bytes,
selection identities, hashes, work counters, reductions, and physics-refit
bounds; no analysis producer or happy-path output code changed.

The broader pytest probe was not green before these edits:
`CapabilityRecording.test_every_divergence_marks_the_scope_without_changing_the_read`
failed because the expected `capability read_text newline argument` marker was
absent. The run was then interrupted during a later CPU-heavy test, so it is
reported as a pre-existing baseline failure rather than a completed suite
timing. This speed patch does not change authentication recording behavior.
