# Block-5 harvest test fixtures (lane L5)

`flag_catalog.json` is a TEST catalog, not the sealed one. It lists every code
`joulewise/b5/harvest.py` emits (`CODES`), with the emitter's family and klass,
and an effect drafted from the gate-prune plan section 3.5:

- `EXCLUDE_WINDOW`: pack, code and model identity mismatches; every
  `calibration.*` code; `neg8.bound_not_derived`; `whole_window.not_passed`
  and `whole_window.verdict_absent`; `clock.systematic`;
  `roster.no_science_bundles`; `records.source_changed_during_harvest`;
  `g3.recompute_failed`.
- `EXCLUDE_MEMBER`: member validity (`member.*`, `model.identity_underivable`,
  `roster.bundle_before_chain_start`) and physics in span (`battery.*` except
  the disclosed ones, `thermal.*`, `contention.*`, `clock.step_overlap`,
  `instrument.*`).
- `DISCLOSE`: everything else (records, diagnostics, G3 assertions other than
  F5-2, missing per-capture battery pairs, frequency changes).

The sealed catalog is lane L6's
`configs/campaigns/v5_claim_25g83/flag_catalog.json`; the harvest only looks
effects up. `tests/test_harvest_b5_window.py` asserts that this fixture names
exactly the emitted codes, so a new code cannot be added without a catalog row.

The synthetic windows in the tests are built at run time from the committed
strict-valid seed bundle `tests/fixtures/d117_v2_production/strict_seed_bundle`
(clones with their own run ids and shifted, re-derived clock stamps) and from
the 376-row acceptance-prefix ledger in `tests/fixtures/v5_qualification_harvest`.
