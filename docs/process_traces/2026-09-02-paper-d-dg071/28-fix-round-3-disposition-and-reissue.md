# Fix round 3 (luna 251) — magistrate disposition and re-issue (2026-09-02)

Seat: luna xhigh, implementation, worktree `/Users/edr/code/JouleWise-wt-paper-d`
at `447a0f2b`, brief = the fix-round-3 brief summarised in file 26 (closure
shapes C1–C7); report custodied as `27-luna-251-fix-round-3.md` (envelope
3167 bytes, `clean`, C1–C7 all `done`). Landing committed by the magistrate as
`6d30c105` (`scripts/issue_dg071_dg075_statistics.py` +255/−94,
`tests/test_issue_dg071_dg075_statistics.py` +322) before any bench edit.

## Disposition

- **C1 golden full-payload test** — ACCEPTED. Twenty-four literal rail rows
  (eight records × cpu/gpu/ane), the fixture sha256 asserted against the
  literal from file 26, `build_payload` minus the two provenance keys
  compared for equality against a literal dict that carries every method
  string. The hand derivation is in the comment block as dictated.
- **C2 Markdown projection + stdout pin** — ACCEPTED. Header bullets, both
  tables (exact four-line blocks) and the two stdout lines are asserted
  through `main`.
- **C3 fixed-seed differential** — ACCEPTED. `_independent_reference` is a
  module-level function that imports nothing from the producer;
  `random.Random(20260902)`, 12 bundles of 2–8 records, seven-decimal
  literals, signed gaps drawn from {0, ±1e-7, ±3e-7, ±1e-6}; the numeric
  `statistics` subtree plus the two tiling fields are compared per bundle.
- **C4 prose glosses** — ACCEPTED. P1–P7 landed verbatim in the Markdown
  `## Method`, the JSON `method` keys (population, arithmetic, quantile,
  median, iqr with the last-place caveat, millisecond_rendering,
  float64_replication, tiling, dg075_dependence) and the docstring. One
  deviation, accepted: the docstring's tiling paragraph omits the
  bundle-specific "In this bundle {nonzero} of {n−1} boundaries…" clause,
  which is data-driven and belongs only where the payload is available.
  The magistrate read the re-issued Method section as a reader (first-use
  test): every term — literal, contiguous, sampler record, order statistic,
  type 7, round-half-even, values of record, tiling, tiling gap, endpoint
  convention — is built before or at its first use.
- **C5 prune** — ACCEPTED. `_ParsedRow.row_number` and
  `SamplerRecord.interval_start_literal` are gone; the float replication test
  now reads `interval_end_s`/`interval_start_s`.
- **C6 mutants** — luna reports all six killed. Replayed at the bench (below):
  all six die. The magistrate's first half-up replay died by `NameError`
  (the mutation replaced the usage but not the import — a replay error, not
  a semantic kill); redone with the import mutated too, it dies by three
  assertion failures. Recorded so nobody reads an `errors=11` line as a kill.
- **C7 replay** — luna's two runs are byte-identical to each other (JSON
  `820fd9f6…598c`, MD `0d0af50c…5fe4`) but differ from the bench pair below
  in exactly the `producer.git_commit` field: luna ran on the uncommitted
  tree, the bench re-issue is at `6d30c105`. Values of record and renderings
  UNCHANGED from file 18 (DG-071 n 406, 116.9720 / 120.9186 / 122.9227 /
  5.9508; DG-075 n 405, 117.0321 / 120.9224 / 122.9270 / 5.8949).
- **Nit (not fixed, not blocking):** the golden test binds `golden_sha256`
  and then repeats the literal in the assertion instead of using the name.
  Left for the delta re-audit to confirm or ignore; cosmetic.

Focused module at the bench after the landing: `Ran 25 tests`, OK.

## Same-signature statement (gate ledger item 5)

The two rounds that failed with the same signature (a reported field with no
value-pinning test — file 23) are now covered by the ruled shape, and the
bench replay of the four escalated mutants (half-up, dropped rail guard,
rendered-quartile IQR, tolerance-count) plus the two extra classes (dropped
`abs`, `>=` refusal) kills all six. Whether the signature recurs is for delta
re-audit 3 (a different model family, execution lens) to state, not this
file.

## Executed evidence

Mutant replay. Each `mut3-<name>` is a copy of the two module files with one
commit (`git init`), a single-site replacement applied (`assert count == 1`),
then `python3 -m unittest tests.test_issue_dg071_dg075_statistics` with
`TMPDIR=<scratchpad>/tmpbench3`; the unmutated copy is the baseline.

```
base    : Ran 25 tests  OK
iqr     : FAILED (failures=2)  test_differential_against_independent_reference, test_golden_bundle_pins_every_reported_field
gap     : FAILED (failures=2)  test_differential_against_independent_reference, test_golden_bundle_pins_every_reported_field
halfup  : FAILED (failures=3)  test_differential_against_independent_reference, test_golden_bundle_pins_every_reported_field, test_millisecond_rendering_ties_round_half_even_through_main
          (first attempt: errors=11 NameError — import not mutated; redone with
           `from decimal import …, ROUND_HALF_UP` added: the three failures above)
starts  : FAILED (failures=1)  test_record_rail_set_mismatch_refusal_reaches_main
noabs   : FAILED (failures=2)  test_differential_against_independent_reference, test_golden_bundle_pins_every_reported_field
ge      : FAILED (errors=3)    test_differential_against_independent_reference, test_golden_bundle_pins_every_reported_field, test_precision_regression_uses_exact_epoch_literals
          (errors, not failures: the producer refuses the at-tolerance 1e-6 boundary that the fixtures deliberately carry)
```

Re-issue at `6d30c105`, twice into `<scratchpad>/reissue-c` and `reissue-d`,
copied into `docs/paper/round7/`:

```
$ cd /Users/edr/code/JouleWise-wt-paper-d && shasum -a 256 docs/paper/round7/dg071-dg075-statistics.json docs/paper/round7/dg071-dg075-statistics.md
dda89609054742b66501ef3acfe822a20e3e7da5d5882349f5d5b255ed7b0caf  docs/paper/round7/dg071-dg075-statistics.json
a7bd11e5228716cd7242d3436ff2f7897e32869cf4d151220a1369141065f647  docs/paper/round7/dg071-dg075-statistics.md
$ grep -c 540125d5 docs/process_traces/2026-09-02-paper-d-dg071/27-luna-251-fix-round-3.md
0
```
