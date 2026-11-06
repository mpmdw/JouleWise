# Calibration-candidate refit optimization

## Scope and baseline

This change is confined to synthetic analysis and repository tests; it did not read
or attempt to locate experiment data.  The recorded step-3b profile attributes
**1,097 of 1,272 worker-seconds (86.24%)** to 12 calibration-candidate refits:
three pack evaluations, each serially refitting four candidates
(`docs/run_reports/2026-11-06-b5-under-90.md:97-100`).

## Implementation

* `joulewise/calibration_bracketing.py:1675-1720` is the cited in-place rebind of
  the frozen estimator.  Within an analysis run it keys a successful candidate
  physics result by the SHA-256 digests of the authenticated evidence,
  powermetrics, and event bytes.  It does not memoize outside an analysis run,
  after a deadline firing, without a worker observer, on an exception, or for a
  non-`float` result.  Thus a hit returns the exact binary64 value produced by
  the original frozen refit rather than recomputing or approximating it.
* `joulewise/b5_analysis/bracket.py:303-356` prefetches independent valid ledger
  candidates through the existing ordered member pool only on an L4 miss.  The
  frozen evaluator still authenticates and evaluates candidates in its original
  serial order; only clean float memo entries return from workers.  Prefetch
  rows, census, physics, deadline accounting, and store entries are discarded,
  and any prefetch failure falls back to the original path.
* `joulewise/analysis_member_pool.py:120-125` adds the content-addressed memo to
  the existing worker memo shipment.  For three synthetic candidates, the
  regression observes one `member_map` submission containing exactly three
  ordered calls; repeated identical authenticated inputs execute the mocked
  refit once rather than twice.

The frozen-file exception is itself cited at
`tests/b5_analysis/test_frozen_files.py:18-23`, binding the evolved file back to
the accepted analysis commit rather than silently relaxing the freeze.

## Equivalence and refusal proof

`tests/b5_analysis/test_candidate_physics_memo.py` uses synthetic bytes only.
It proves (1) no run means two calls still produce two refits; (2) a run keys
separate authenticated byte triples separately; (3) a cold value and its memo
hit have identical `struct.pack(">d", value)` bytes and the underlying refit runs
once; (4) deadline firings, exceptions, and absent observers are never retained;
and (5) only successful, zero-firing float worker results merge.  The focused
module passes 6 tests, covering the happy-path bytes and existing refusal
behavior without real experiment data.

## Result

The hot path now performs at most one clean refit per distinct authenticated
three-file byte identity per analysis run, and independent candidate misses are
submitted together to the existing worker pool.  This removes identical
candidate refits while retaining the original evaluator as the sole consumer
and preserves result bytes exactly.  No post-change wall-time claim is made:
the checkout contains no real experiment data, and the task forbids accessing
it; the measured baseline above is the existing synthetic profile.
