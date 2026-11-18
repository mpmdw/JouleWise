# C1 row 13 comparator and output mutations

18 November 2026 · Tier 2 · synthetic output evidence

Mission M0 found no active stop card. The named worktree was clean and detached at
`f1be75b21978da69fa20506640bcb76ec53f6df2`, equal to remote main. The remote
search found the historical release-tools line and the four named component
PRs. The lead has been asked for the accepted comparator successor, its run
index and the target ref. Item 437 remains a magistrate instruction. This
session follows the explicit row 13 synthetic assignment.

## Implemented and verified

| Finding | Implementation | Regression | Result |
|---|---|---|---|
| Common omissions and additions can satisfy a report-derived census | Compile both wire shapes from an external design card. Validate keyed lists, key multiplicity, positional intervals and required containers on each side. | Full and prefix common omission/addition, same-count substitution, duplicate identity, and swapped identities with planted unequal values. | PASS |
| The historical interpretation exemption skips value comparison | Require a rule for each logical leaf. Compare every occurrence, including the extra rendering. Reject unused rules and undeclared siblings. | Per-wire claim-text mutations, missing claim on both sides, wrong shared literal, extra recompute leaf. | PASS |
| Comparing equal states can miss a shared invalid prefix | Check the required literal and allowed tree shape before value comparisons. | Shared wrong marker, changed reasons, opened payload beside both marker shapes. | PASS |
| Presence, null and numeric representations can be confused | Check exact scalar types, required null and seal shape separately. Apply the bound only to finite values. | Null-to-zero, missing null and endpoint, malformed and alternate valid opaque values, strict JSON on both sides, exact rational component with unchanged float mirror, within-bar control. | PASS |
| An item-9 mutation can miss an alias or a variable row | Join the external leaf census with both validated raw pointer maps, enumerate each occurrence, and rerun the clean control after each mutation. | Full 27 left + 26 right leaves and prefix 30 left + 29 right leaves. All 112 leaf mutations produced their expected specific exit and family. | PASS |

The [synthetic execution index](2026-11-18-c1-comparator-synthetic-index.jsonl)
records 67 full and 75 prefix cases, including the leaf mutations, structural
adversaries and passing controls. Its run headers bind the input card, synthetic
bars, schema runner and comparator bytes. Public verdicts contain only the
verdict and exit code. Detailed diagnostics in the index use invented identities.

The frozen fixture and its two SHA-256-pinned public source files are copied
under `tests/v4_release/row13_fixture/` for offline replay. The fixture bytes
match the supplied file, SHA-256
`4bcabf8ae1de8086caa14a62b601e9a6b3bdcae2ce3b02dd38c98b3e06bc7a5d`.
Python 3.13.18 and 3.14.6 both reproduced the supplied diagnostics and passed
all seven focused tests. Python 3.14 also reproduced the indexed bytes generated
by Python 3.13. The canonical sharder discovered the new module and its
single-module run reported seven passes.

```sh
python3.13 -B tests/v4_release/row13_fixture/fixture.py
PYTHONPATH=tests:. python3.13 -B -m unittest v4_release.test_claim_output_mutations -v
PYTHONPATH=tests:. python3.13 -B -m v4_release.test_claim_output_mutations --evidence-index \
  | cmp docs/run_reports/2026-11-18-c1-comparator-synthetic-index.jsonl -
```

A filename-filtered repository-wide discovery attempt invoked the existing B5
package's `load_tests` hook, which disregards the filter. The two commands
entered unrelated archive tests. Their output supplies no comparator evidence.
Use the exact module invocation above for local replay. Full-suite CI belongs on
the lead's authorized draft PR.

## NEEDS_SPEC

- Integration owner supplies the approved target ref, exact write paths, the
  accepted or candidate comparator and its run index, and the exporter, release
  driver, bars, primary and independent recompute pins. Bind each actual wire
  schema and synthetic full/prefix pair there. The current code is an
  invented-schema comparator with no release invocation.
- Series, desk and evaluator owners supply the admitted manifest and both seed
  witnesses, the finality, held/retry and A9 mappings, the release event and
  withholding schemas, and the evaluator and companion receipts. The #836
  owner must supply a valid captured eligible/no-S fixture or identify the
  stable precondition that its captured control refused. These bindings precede
  the structural replay and production-family census.
- Opus routes the ledger's FOR-FABLE leaves, the narrow R2 §6.18 metadata AUC
  disposition and any missing exact rational or renderer operands. The
  synthetic rules establish comparator mechanics. Applying actual bars and
  preserving governed legacy dispositions depend on the named successor.

The next step is for the integration owner to identify the accepted successor
and provide one valid pinned full/prefix synthetic output pair. Bind one
family at a time against the ledger, then run the pinned producer-to-comparator
regression and return the coverage deltas to Opus. Row 13 acceptance and the
row 14 pre-C1 seal require the lead's decision.
