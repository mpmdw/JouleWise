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
at `6f81504db0c50ced6ef488d13afab0bf2662ec5b`. These were the two digest
edits in the original provider commit.

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

## PR #968 fix-1

Mythos returned MERGE for the original provider patch and identified
gaps in the recorder and CLI. The lead ruled that `public` is the
single look report root. Ledger validation, stage-2 preflight, the
recorder, and freeze-2 authority use the same route check.

- F1. The recorder checks the full stage-2 execution row in the fetched
  main history before opening a report, then verifies the exact commit
  named in the report. The `row --output --write` regressions exercise
  `docs/public`, the reserved route, and a working-tree row with no
  matching execution commit. Each refuses with zero report opens and
  byte-identical ledger contents. A valid synthetic report records `run`.
- F3. The provider refuses if either `execution_host` or `custody_root`
  is missing, with zero Git report lookups.
- F4. `authorize-freeze2` prints the provider's route and row refusals
  after its fixed prefix on stderr. A malformed report regression
  checks the generic refusal and empty stdout.

The interim draft manifest pins these source digests for the fix-1
changes on [PR #968](https://github.com/mpmdw/JouleWise/pull/968).

| Path | SHA-256 |
| --- | --- |
| `joulewise/cadence_looks/manifest.py` | `41b8aa0cc1662c21619b4a9c303b4581b431855f7b03a18b34bc7dbd56ab9873` |
| `scripts/cadence_look_manifest.py` | `111efda69101cbecd941cd633af070a45d97dc884a016358fd947ba941e0b555` |
| `scripts/cadence_look_run.py` | `206a51d99f280d2ead8569d872da17df38629903254c8b29ba695cc1a20ad172` |

The interim ledger row records the new manifest digest
`9e2b1a07875029399377fbf640543ca319eefdf611d194f24820a525d7ddc66e`.
The pin command reported zero changes. Five new tests exercise the
provider, recorder, and stage-2 preflight. Existing stage-2 fixtures
now publish under `public`.

The six provider modules passed 133 tests under `taskpolicy -c utility`
with at most two workers and NumPy available. The run covered
`test_freeze2_authority`, `test_interim_release`, `test_look_layout`,
`test_merge_audit_c3a0dd9f8`, `test_round6_guards`, and `test_time_fields`.
Two audit classes initially failed setup because the sparse checkout
omitted their generated corpus. The complete audit module passed after
restoring the fixtures. Four additional stage-2 tests passed from
`test_look_run.Stage2Custody` and `test_look_run.CommittedLedger`.
Hosted CI covers the nested `test_look_manifest` run.

## Handoff

PR #795 merged to `align/2026-11-14-look-manifest`, which is still the head
of [PR #793](https://github.com/mpmdw/JouleWise/pull/793). The lead opened
[PR #968](https://github.com/mpmdw/JouleWise/pull/968) as a stacked draft
against that branch.

The independent [PR #835](https://github.com/mpmdw/JouleWise/pull/835)
drafts still point at the original provider commit. Re-bind after
review using the new provider commit, `public` in the synthetic
fixtures, and a replay observer that permits the fixed `LOOKS.json`
history query.
