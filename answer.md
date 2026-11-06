# ALIGN v4 WP5: b6 baseline repair, part 1

Branch: `lane/2026-11-05-align-v4-wp5-b6`, based on
`c8ef6b2f6ee02ac1db97c98a1c538615af4b20f2`.

Part 1 is implemented. The b6 baseline remains open: three lead-owned review
rows are missing, and the five full-round cold-pass cases need completion
outside this run's test-time budget.

## Changes and commits

- `649af40ea`: applied the supplied `b6-end-date-fixture.patch` exactly to
  `tests/b6/round_support.py`. Both synthetic registration builders now use
  `FIXTURE_END_T0_BEFORE` (UTC import time plus 365 days). Production registrations
  and their stopping dates are untouched.
- The same commit appends one row to `configs/b6/executing_reviews.json`, for
  `1bf706fcffa8494e0d4e50a39e541bb45b2a2df1`. Existing rows are unchanged. No rows
  were added for the three commits listed below, and no review-coverage test
  boundary was changed.
- Handoff/report commit: recorded in the final delivery message and Git history.

## Review evidence

The local refs `origin/codex/2026-10-28-by-therm-lines`,
`origin/codex/2026-10-28-by-therm-lines-rev-sol`, and
`origin/codex/2026-10-28-by-therm-lines-rev-sol-2` already contain
`ee4ce93fc7a1e4d77bc54d2085337b122448c334`; no network or fetch was used.
That commit records the Sol 6.1 xhigh and Opus 5.5 executing reviews of
`de35f6403..defd9f9a3` for `7d67cbd5bed1d1b00a7d9719053ae0b6f11ba861`.
The new row copies their reviewer, covered-range, and paper fields verbatim.

Direct byte comparisons of `joulewise/b5/harvest.py` at `1bf706fcf`,
`7d67cbd5b`, and reviewed tip `defd9f9a3` all matched:

- Size: 470,098 bytes.
- Git blob: `1ddcb2cd0b2dda04aa20d27f6465367d8640def0`.
- SHA-256: `2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744`.

The historical record cites
`/Users/edr/night-archive/seats-caa9ff66/p2therm-rev/sol-REPORT.md` and
`/Users/edr/night-archive/seats-caa9ff66/p2therm-rev/opus-REPORT.md`.
These paths were treated only as text. The record exists in Git; the papers'
current filesystem existence and contents were not independently checked because
the blind boundary forbids accessing that archive. The lead retains that check.

## Verification

All five unittest modules are run sequentially using this exact prefix:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5/tmp python3.13 -B -m unittest
```

| Module | Tests completed | Passed | Failed | Skipped | Elapsed |
| --- | ---: | ---: | ---: | ---: | ---: |
| `tests.b6.test_loop_round_desk` | 6 | 6 | 0 | 0 | 256.150 s |
| `tests.b6.test_desk_resume_finalize` | 6 | 6 | 0 | 0 | 351.911 s |
| `tests.b6.test_capture_screen_reachability` | 9 | 9 | 0 | 0 | 322.260 s |
| `tests.b6.test_cold_pass_fixes` | 9 of 14 | 9 | 0 | 0 | 181.185 s (bounded wrapper) |
| `tests.b6.test_audit_record_fixes` | 8 | 7 | 1 | 0 | 81.089 s |

The four completed modules report unittest elapsed times; cold-pass reports its
wrapper's monotonic duration. Across all five modules: **38 completed tests,
37 passes, 1 failure, 0 skips; 1 interrupted test and 4 not started.**
Recorded active durations sum to 1,192.595 s (19 min 52.595 s), excluding small
interpreter startup overhead on the first four commands. Logs are under
`/private/tmp/jwsol/v4-wp5/tmp/test_*.log`; the timeout command, return code, and
duration are in `test_cold_pass_fixes_budget.json` there.

The audit failure is
`AuditRecordTests.test_review_rows_are_append_only_and_load_in_the_code_check`
at line 121. The uncovered history is exactly `0ba413d40`, `b29c25c59`, and
`dc2204dba`; `1bf706fcf` is no longer missing. This is an open gate, not a passing
baseline. The test was preserved. The final cold-pass module uses `-v` and a
180-second subprocess timeout. Nine `ColdPassTests` passed. The wrapper then
sent SIGINT to its own test process group at the cap; the child returned -2
and the wrapper returned 124. `FullRoundTests.test_completed_full_alpha` was
interrupted, and these four tests did not start:

- `FullRoundTests.test_exit4_and_acceptance_unavailable_reharvest_into_new_archive`
- `FullRoundTests.test_gamma_lost_midpoint_counts_and_overrides_b5_claim`
- `FullRoundTests.test_lost_start_reference_without_spare_counts`
- `FullRoundTests.test_physical_and_opening_no_bound_stops_rotate`

The lead must run all five full-round cases (the interrupted case is not a pass):

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5/tmp python3.13 -B -m unittest tests.b6.test_cold_pass_fixes.FullRoundTests
```

Timing limitation: capture-screen reachability reports 322.260 s in unittest but
5,106.91 s of command wall time. A tool wait also returned after 4,892.39 s.
The cause of this host/tool delay was not established. The first two commands
reported 256.67 s and 353.09 s wall time. The requested roughly 20-minute total
wall-time limit therefore cannot be certified; active unittest durations are
reported separately and cold-pass was capped at the residual active-time
budget. No claim is made that the host was continuously executing
tests during the unexplained interval.

Additional checks:

- Direct byte-equality / SHA-256 checks and append-only / unique-row assertions
  passed. The fixture file's Git blob is
  `8577b7e997e530b9b7cb54f75b38cc0785841351`, matching the supplied patch.
- Syntax check: `env PYTHONPYCACHEPREFIX=/private/tmp/jwsol/v4-wp5/tmp/pycache python3.13 -m compileall -q joulewise tests`
  passed (exit 0).
- Final diff whitespace and file-scope checks passed before the report commit.
  No test rerun is required for the report-only commit.

The full suite is intentionally not run, per the standing machine-load rule.
No block-5 analysis pipeline, real measurement inputs, network access, live
hardware capture, or native MLX tests are part of this work. WP5's requested
modules use synthetic inputs; their results are not hardware validation.

## TODO: lead-owned executing reviews and rows

These are outstanding requirements, not review approvals. First check the archive
from an authorized lead session for existing papers. If absent, commission
independent Opus executing reviews labeled **retroactive**, disposition findings,
then let the lead append the rows. All hunk coordinates below refer to each
original commit's parent-to-commit diff in `joulewise/adapters/mlx_runtime.py`.

- [ ] **`dc2204dba1e0512e17ff264be4f2498b04d0cbb0` (pilot 3):** review all seven
  hunks: `-213,6 +213,7`, `-763,6 +764,10`, `-786,8 +791,13`,
  `-798,6 +808,7`, `-807,6 +818,8`, `-826,7 +839,8`, and
  `-973,6 +987,7`. They add `_GenerationRecord.prefill_tokens`, opt-in `_generate`
  stream/cache/setup/reconciliation arguments, measured setup reconciliation,
  event metadata, cached/fed-token accounting, stream options, and the returned
  prefill count. Check unchanged legacy execution and measurement boundaries;
  inspect callers in `joulewise/align/apple/endpoint.py`,
  `joulewise/align/apple/prompt_cache.py`, and
  `joulewise/align/apple/workload.py`, with
  `tests/align/test_pilot3_cache.py` and `tests/align/test_apple_endpoint.py`.
- [ ] **`b29c25c59ad57787faae4e939578dea01c5682a6` (pilot 4):** review all five
  hunks: `-768,6 +768,8`, `-798,6 +800,14`, `-836,7 +846,8`,
  `-1061,7 +1072,7`, and `-1078,6 +1089,15`. They add `_generate` sampler policy
  and per-turn seed arguments, validate/seed MLX RNG, preserve the legacy sampler
  branch, and extend `_sampler_for_generation` with categorical constructor
  arguments/provenance. Check reproducibility and the unchanged legacy branch;
  inspect callers/policy in `joulewise/align/apple/endpoint.py`,
  `joulewise/align/apple/sampling.py`, and
  `joulewise/align/apple/workload.py`, with `tests/align/test_pilot4.py` and
  `tests/align/test_pilot3_cache.py`.
- [ ] **`0ba413d40fbadeac03d619cda7c030a11eb24394` (#657):** review all four
  hunks: `-768,6 +768,7`, `-830,6 +831,7`, `-850,6 +852,10`, and
  `-998,7 +1004,7`. They add the `_generate.prefill_prompt` hook, capture
  `fed_prompt_tokens` before the hook changes the prompt, call the hook inside
  measured prefill, and return the saved count. Inspect checkpoint callers and
  state handling in `joulewise/align/apple/endpoint.py`,
  `joulewise/align/apple/prompt_cache.py`, and
  `joulewise/align/apple/workload.py`, with
  `tests/align/test_cache_checkpoint.py` and
  `tests/align/test_cache_checkpoint_native.py`. Coordinate with WP3's pinned-core
  ruling and implementation; the lead must cite its actual Opus paper and verify
  the final integrated boundary behavior. Native checkpoint validation belongs
  to the lead outside this sandbox:
  `JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_cache_checkpoint_native`.

To extract the exact review inputs without measurement data:

```sh
git diff dc2204dba^ dc2204dba -- joulewise/adapters/mlx_runtime.py
git diff b29c25c59^ b29c25c59 -- joulewise/adapters/mlx_runtime.py
git diff 0ba413d40^ 0ba413d40 -- joulewise/adapters/mlx_runtime.py
```

No new Ed ruling is requested by this repair. The remaining archive checks,
executing-review papers, dispositions, and appended rows belong to the lead.
The coordination-state files named in the brief were not edited or regenerated.
After the five full-round cases and the three executing-review TODOs are
complete, the lead should append the real review rows and rerun
`tests.b6.test_audit_record_fixes` with the same synthetic-only environment.
