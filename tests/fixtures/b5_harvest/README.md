# Block-5 harvest test fixtures (lane L5)

## `flag_catalog.json`

A TEST catalog in lane L4's `joulewise.flag_catalog.v1` format (L4's
`joulewise.flags.catalog.load_catalog` accepts it), not the sealed one. It
lists every code `joulewise/b5/harvest.py` emits (`CODES`) except
`records.malformed_flag`, which must stay unclassified so that a lost flag
line blocks the release event (L4's `NEVER_CLASSIFIED_CODES`).

- Codes that L4's draft catalog (`joulewise.flags.catalog.DRAFT_CODES`) names
  carry L4's family, klass, blinding and draft effect.
- The codes in `harvest.L5_ONLY_CODES` are not in L4's draft. Their effects
  here are drafted from gate-prune plan section 3.5:
  - `EXCLUDE_WINDOW`: `calibration.acceptance_mismatch`,
    `calibration.binding_failed`, `calibration.ledger_snapshot_refused`,
    `calibration.capture_battery_pair_failed`, `whole_window.not_passed`,
    `whole_window.verdict_absent`, `model.identity_inconsistent_in_window`,
    `roster.no_science_bundles`, `records.source_changed_during_harvest`,
    `g3.recompute_failed`;
  - `EXCLUDE_MEMBER`: `model.identity_underivable`, `member.unreadable`,
    `member.reduction_mismatch`, `member.anchor_recompute_mismatch`,
    `member.span_unknown`;
  - `DISCLOSE`: the other records, G3 and roster codes, and
    `battery.accumulator_activity` and `battery.accumulator_unavailable`.
  - The 17 `lineage.*` codes of lane L3's records audit
    (`joulewise.window_lineage.FINDING_CODES`) carry the block-5 draft
    catalog's classification (revision 3): `DISCLOSE`, except
    `lineage.plan_tree_digest_differs` (`PACK_IDENTITY`, `NUMBER`,
    `EXCLUDE_WINDOW`).

  Revision 3 of the block-5 draft catalog makes `whole_window.not_passed` and
  `g3.recompute_failed` `DISCLOSE` (registration 6.5); this fixture keeps the
  earlier draft effect, and the tests that need the registered one
  (`Neg8ScreenTests`) override it in their window's copy.

  L4 (draft) and L6 (sealed catalog) classify these; until then the sealed
  catalog leaves them `UNCLASSIFIED`, which blocks release, never collection.
- `rules.cell_unit_minimum` is the registered 8. The synthetic six-member test
  window lowers it to 1 in its own copy so the unit rule stays observable.

The sealed catalog is lane L6's
`configs/campaigns/v5_claim_25g83/flag_catalog.json`; the harvest only looks
effects up. `tests/test_harvest_b5_window.py` asserts that this fixture names
exactly the emitted codes, and, when `joulewise.flags` is importable, that it
agrees with L4's draft.

## `l1_monitor/`

Hazard-monitor journals (`joulewise.hazard_journal.v1`) written by lane L1's
own `joulewise.hazards.monitor.Monitor` under L1's `FakeMac` test harness:
420 simulated seconds with a -447 mA gauge publication, an fseventsd burst,
OS thermal level 1, a 6 ms wall-clock step and a disk drop under 10 GiB.
`expected.json` records L1's own member join (`monitor.member_findings`) for
named spans; the harvest's joins must give the same physics codes on the
same bytes. Regenerate from a tree that holds L1 with
`python3 -B tests/fixtures/b5_harvest/make_l1_monitor_journals.py`.

## Synthetic windows

The windows in the tests are built at run time from the committed
strict-valid seed bundle `tests/fixtures/d117_v2_production/strict_seed_bundle`
(clones with their own run ids and shifted, re-derived clock stamps), the
376-row acceptance-prefix ledger in `tests/fixtures/v5_qualification_harvest`,
journals written line for line in L1's format (pinned to `l1_monitor/` by
`L1JournalFormatTests`), an arm record in L1's `joulewise.hazard_arm.v1`
shape, and an executed inventory and plan in L2's shapes. The plan names a
registration copy whose section 6.9 carries the registered harvest-threshold
block (`RegisteredThresholdTests` pins that block to the design branch's text
when the branch is in the clone), and the pack's plan tree pins the committed
12-member NEG-8 settled corpus through a bound-derivation stage. The NEG-8
tests run the chain's own prune helper (`joulewise.b5.chain.PRUNE_HELPER`),
the core's `whole_window.mint_neg8_drift_bound_artifact` (only the members'
energy and strictness gates stubbed, as `tests/test_whole_window.py` does) and
the driver's `neg8_corpus_record` locator.
