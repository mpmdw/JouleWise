# Freeze-2 provider reserved-route check

The [PR #835 bind replay](https://github.com/mpmdw/JouleWise/blob/a76c0461c/docs/run_reports/2026-11-24-pr835-freeze2-bind.md#provider-blinding-blocker)
recorded an attempted Git read of a report under `invented/restricted`.
The observer stopped it before Git ran.

Provider commit `3319babb1159662ae75839c896b997562046e5f2` limits freeze-2
report reads to the repository-relative `public/` root used by the
existing provider acceptance tests. It checks path components against the
existing reserved-name list and authenticates a matching stage-1 row in
the fetched main commit's ledger history before any report lookup. After
reading the admitted report, it checks the exact execution commit named
in the report against the same binding. The refusal names the route.

The interim draft manifest re-pins `joulewise/cadence_looks/manifest.py`
from `48b2db84912948607b4b2f581886b359bc3b1e20c315d339d8d83b59b83517e6`
to `a8107f26d60848a914189441ff87dc5d5ecae8ac0ad834c3b65b0018aca5c09a`.
The interim draft's `LOOKS.json` row follows the new manifest digest
`91b7fee24cf99dcf97e83a18d27f3619fd8a45bce6c336592e7611ecf8ee46b9`.
The source was the reviewed [PR #795 merge](https://github.com/mpmdw/JouleWise/pull/795)
at `6f81504db0c50ced6ef488d13afab0bf2662ec5b`. These two digest edits are
the entire pin delta on the provider branch. Frozen suites and registered
outputs have no diff.

## Verification

- The new subprocess spy blocked six attempted report lookups on the old
  provider across the route and execution mismatch cases. On the fixed
  provider, all six returned provider refusals with zero Git subprocesses
  for those report routes. The positive fixture accepted an execution
  commit inheriting its stage-1 ledger row and refused a report naming
  the wrong execution commit.
- Ten focused tests passed in 21.914 seconds under `taskpolicy -c utility`
  with one worker. These covered the new route tests plus the existing
  naming, main port and fetch refusal tests. The manifest and ledger
  digests matched the updated files. `git diff --check` passed.
- The canonical whole suite is a hosted CI gate. Local verification used
  synthetic histories and the provider's pinned public source on the Air.

## Handoff

PR #795 merged to `align/2026-11-14-look-manifest`, which is still the head
of [PR #793](https://github.com/mpmdw/JouleWise/pull/793). The observed
`origin/main` at `8eb4c61709f96b5388eb36ad651cc036d77edba2` lacks the
provider. A narrow draft against main depends on the provider landing
there.

The independent [PR #835](https://github.com/mpmdw/JouleWise/pull/835)
drafts still point at the original provider commit. Their next bind
should use the new provider commit, the fixed public root in the
synthetic fixtures, and a replay observer that permits the fixed
`LOOKS.json` history query.
