# ALIGN v4 WP5b: b6 review rows

The three review papers and rows are committed. **Five-module verification is
incomplete**: 19 tests passed, 1 was interrupted at the time cap, and 23 did not
start; no assertion failures were reported.

## Changes and commits

Continued `lane/2026-11-05-align-v4-wp5-b6` from `4344a1174`.
Implementation commit: `3bf81ba5312482c9bd64aa14937ad065175ee8a1`
(`docs(b6): record three retroactive ALIGN runtime reviews`).
The final report-only commit follows it on this branch; its hash is in the
final delivery message and Git history. Nothing was pushed.

Files changed in WP5b:

- `configs/b6/executing_reviews.json`: appended exactly three retroactive rows
  from the papers' section 5, preserving all 53 prior rows and the schema.
  Each cites the committed paper and its SHA-256 in `covered`.
- `docs/align/reviews/2026-11-05-retro-executing-review-dc2204dba.md`
- `docs/align/reviews/2026-11-05-retro-executing-review-b29c25c59.md`
- `docs/align/reviews/2026-11-05-retro-executing-review-0ba413d40.md`
  (all three copied byte for byte from the supplied `/private/tmp` papers).
- `tests/b6/test_audit_record_fixes.py`: retained text-only historical archive
  citations and added repository-paper existence, containment and digest
  validation. Append-only, uniqueness and HEAD history coverage checks remain.
- `answer.md` and
  `docs/run_reports/2026-11-05-align-v4-wp5b-b6-review-rows.md`: handoff evidence.

`git merge-base --is-ancestor 0ba413d40 HEAD` passed. The commit is in this
branch through integration `c8ef6b2f6` / the #657 merge. The first two papers
are ADMIT. `0ba413d40` is **ADMIT_WITH_FIXES, admitted for limit None/0 only**:
F2 must be fixed and E4 rerun before any limit > 0 cell. Recording a row does
not enforce that runtime condition.

## Verification

The two attempted modules used this exact prefix, sequentially in the table's
order:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v <module>
```

| Module | Passed | Failed | Skipped | Interrupted | Not started | Result / elapsed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `tests.b6.test_audit_record_fixes` | 8 | 0 | 0 | 0 | 0 | exit 0; wrapper 76.413 s; unittest 75.842 s |
| `tests.b6.test_cold_pass_fixes` | 11 | 0 | 0 | 1 | 2 | exit -2; budget timeout; wrapper 1114.800 s; no final unittest timer |
| `tests.b6.test_loop_round_desk` | 0 | 0 | 0 | 0 | 6 | not started; not run |
| `tests.b6.test_desk_resume_finalize` | 0 | 0 | 0 | 0 | 6 | not started; not run |
| `tests.b6.test_capture_screen_reachability` | 0 | 0 | 0 | 0 | 9 | not started; not run |

Totals: 19 passed, 0 failed, 0 skipped, 1 interrupted, 23 not started.
Sequential wrapper wall time: **1191.213 s**. The 1,190 s cap interrupted its own test process group. A partially completed test or subtest is not counted as passed. The five-module acceptance is incomplete.

Additional checks passed: `git diff --check`; all three source/copy byte and
SHA-256 comparisons; append-only/schema/unique-commit checks; and:

```sh
env PYTHONPYCACHEPREFIX=/private/tmp/jwsol/v4-wp5b/tmp/pycache python3.13 -m compileall -q joulewise tests
```

## Limits, risks and next step

The full five-module acceptance is still open because the standing test-time
cap was reached. The gamma test was interrupted;
these two cold-pass tests never started:

- `FullRoundTests.test_lost_start_reference_without_spare_counts`
- `FullRoundTests.test_physical_and_opening_no_bound_stops_rotate`

The interrupted case was
`FullRoundTests.test_gamma_lost_midpoint_counts_and_overrides_b5_claim`.
The other three modules have 21 tests not started. Earlier part-1 results are
historical evidence and are not counted as fresh WP5b passes.

Next exact step: the lead reviews the implementation commit, then runs the
four incomplete/unrun modules sequentially in a sufficiently long authorized
test window before claiming the WP5 acceptance gate is green:

```sh
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_cold_pass_fixes
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_loop_round_desk
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_desk_resume_finalize
env JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp/jwsol/v4-wp5b/tmp python3.13 -B -m unittest -v tests.b6.test_capture_screen_reachability
```

The full suite was forbidden by the machine-load rule. No native MLX test was
attempted or counted as a skip. The papers' native results are supplied review
evidence, not independently reproduced here. The lead's WP3/WP6 native gate
includes:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
```

The lead must retain limit None/0 or close F2 before any positive-limit cell.
Optional hardening findings remain documented in the papers. The WP14 commit
`a17ed96c8` is not locally available, so copies were checked against the supplied
source files, not that commit. The original archive citations were treated only
as text. The copied 0ba paper retains its author's process note about an
upstream archive listing; any disposition of that note remains lead-owned.
No new Ed ruling is requested for these record changes.

No network, real measurement inputs, block-5 pipeline, or live capture was
used. The four protected coordination files were unchanged. The part-1 dated
report is unchanged; the earlier detailed `answer.md` remains available via
`git show 4344a1174:answer.md`.
