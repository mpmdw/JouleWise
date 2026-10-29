# L9-PATHTOKEN-FABLE-REV: second-family executing review of b13a510dc..49991c73a

Seat: Claude Fable (cloud, scheduled), replacing Sol under gate policy rule 3. Review branch
`review/2026-10-29-l9-pathtoken-fable-rev` at `49991c73a`. Synthetic fixtures only; no real block-5/6/BYTES data opened.
The committed transfer manifests on main were read for file names only. Evidence: `l9-pathtoken-fable-rev/probe_fable.py`,
`l9-pathtoken-fable-rev/probe_output.txt`.

## VERDICT: ACCEPT

The exemption is exact-match, per window, census-path-only, recomputed from disk at both ends, and empties on any mismatch.
Every probe I added fails closed. One release-mode consequence needs a ruling (F1); nothing blocks the dry run.

## Findings (ranked)

**F1 (low, needs ruling, not a defect of this change).** `dry_run.py:417` validates `release_difference.path` with the
full guard, and `dry_run.py:1334` validates the final record outside any `try`. If a number-like inventory file's bytes
differ between dry run and release, `release_difference()` names that path, the release record fails validation, and
`run()` raises `AnalysisRefusal('dry_run_record_invalid')` out of `scripts/run_b5_analysis.py:69` as an uncaught
traceback, with no `B5-RELEASE-RECORD.json` written. Fail-closed, but the step-11 `release_digest_differs_from_dry_run`
record is lost. The brief's P2 demands this (every other field keeps the guard), and the seat pinned it in a test and
listed it as OPEN ISSUES 1. Ruling: keep as is, or admit the same window inventory for `release_difference.path` only.

**F2 (note, precision).** "Authenticated by the index-pinned harvest digest" is exact for `outputs` names only.
`harvest.json` does not pin `sources/SHA256SUMS` (`archive.py:272` reads it with `expected=None`), so `sources/` and
`original/claim-runs/` names are pinned to the listing bytes step 0 read, re-pinned by the census row's digest at
validation (`dry_run.py:363-367`). That is sound for the guard's purpose: step 0 runs before any arithmetic, and
`RunState.path` (`dry_run.py:462-470`) confines every L9 write to restricted custody, so no analysis number can enter the
listing. The seat's DECISIONS 2 states this correctly.

**F3 (note).** Validating the public record needs the archives on disk: with `index=None` the tracked index is loaded,
and with absent archive roots no inventory is built, so the real record (68 such names per window) is refused as
`dry_run_record_invalid` off the laptop. Today the only non-test consumer is `run()` itself, so nothing breaks.

**F4 (not verified here).** The seat's claim that `test_G6_finalizer_main` fails order-dependently at base too. Outside the
requested two modules; the lead's laptop run covers it.

## Answers

**1. Can an analysis number reach a structure-only record or the run record through the exemption? No.**
Writer (`dry_run.py:493-505`): only `census_*` roles, only list values, only the `path` field, only on exact set
membership; `sha256`, `check`, extra keys, dict values, caller `raw`, and `attempt_/kept_/tripwire_` roles are scanned in
full. Validator (`dry_run.py:316-319, 371`): the inventory reaches `path()` only for `input_census` rows, keyed by the
row's own `window`; step output names and `release_difference` use the empty default. Probes (output file):
inventory name plus `/1.5`, `-1.5`, `1e5`, trailing slash, `./` prefix, upper case: all refused by both writer and
validator. Another window's name, an unlisted name, a `sources/attempts/<plan>/` history name: refused (seat tests, re-run).
Inventory from the wrong window's harvest digest: empty. Listing symlinked outside the archive at step 0:
`archive_path_invalid` before any census write; at validation, the digest mismatch empties the inventory and even the
legitimate record is refused. Paths L9 constructs (`ledger/live/...`, `sources/attempts/<plan>/...`, `original/claim-runs/<name>`)
come from constants, the index, or the listing, never from a result. History-only attempts carry no source names
(`archive.py:112-227` censuses only `harvest.json` and `derived/*`), so the real index's 8 non-analysed harvested
attempts add no number-like rows. The 68 float-like names per real window are all `sources/night-custody/results-clone/docs/process_traces/...`,
all listing entries, none an output name.

**2. Authenticated and identical at both ends? Yes, with F2's precision.** Write time: `window.harvest_record_sha256` and
the `sources/SHA256SUMS` digest from `archive.census()` (`dry_run.py:605-609`). Validation: `entry.harvest_record_sha256`
of the index entry that a `windows` row names by pack, plan and digest, and the record's own `sources/SHA256SUMS` row
(exactly one). Same helper, same roots. Probe: write-time and validation-time sets are equal (alpha 2368, beta 2370,
gamma 2370 names) and all 10 float-like census rows in the synthetic record are in their own window's set. Modified
`harvest.json` or listing: empty inventory, record refused (seat tests and probes).

**3. Do all other fields and roles keep the full guard? Yes.** `ReaderRecordGuardTests.test_T19` passes at the head,
including `census_gamma {'path':'sources/1e-100.json'}`; the seat's 7 writer refusal subcases pass; a step output named
like an inventory file is refused by the validator (probe).

**4. Regression tests: fail at base, pass at head? Yes.** At `b13a510dc` with the new module copied in: 3 failures, 10
errors, all 6 new tests, 55 existing pass. At `49991c73a`: Ran 61, OK (skipped=3). TMPDIR was outside the checkout
with no float-like token. `git diff --name-only b13a510dc 49991c73a`: the three WRITE_SCOPE files only.
