# Harvest lane: the author's return (2026-10-07)

This is the report the author of the **harvest lane** handed back when the lane was finished, kept as the author
wrote it. The harvest lane is the branch `lane/2026-10-07-harvest-lane`: ten changes, one commit each, to the
harvest, the desk program that checks a finished measurement window and decides which measurements are kept. The
two reviews of the lane, `13-harvest-lane-executing-review.md` and `14-harvest-lane-cold-pass.md` beside this file,
refer to this report as "the author's return" and to its numbered notes ("author note 4", "the author's item 10").
The report is a record for a reviewer, not an explanation for a new reader; the first of those two files builds
the terms.

Source: row 2 (counting from 0) of the workflow journal `/Users/edr/.claude/projects/-Users-edr-code-JouleWise/e4fc0437-3e56-4860-a119-d14d766031f7/subagents/workflows/wf_38c5e204-c67/journal.jsonl`, the result of agent `a76a48ff0e0927f54`; SHA-256 of the journal file when this record was written: `b238a7b9e6ef51d8f287e875c9dca66bccc39f60e06771f63859876d06906c5c`.

---

# Harvest lane return: K-4 to K-7 and H-8 to H-13

All ten items are committed, one commit each, and pushed. Head `c10257418a9d7d2173bec306c0b1deb38e144343` on `lane/2026-10-07-harvest-lane`, equal to `origin`, worktree clean. Every module run on the final head passed, and the rehearsal harvest differs from the base only in ways an item explains.

## Per item

"Before" is the result of the new test on the source of the previous commit, tests unchanged.

| Item | Commit | Files | Tests | Counterfactual result |
|---|---|---|---|---|
| K-4 | `8b186fc9d` | `harvest.py`, `whole_window.py`, `tests/test_neg8_survivors.py`, `tests/test_harvest_b5_window.py` | `WriterEnergyPredicateParityTests` (2 tests); `HarvestSurvivorTests.test_a_succeeded_reference_with_no_energy_envelope_is_lost_and_the_survivors_decide`, `…test_an_unreadable_idle_subtracted_energy_or_midpoint_is_lost_the_same_way`, `…test_a_reference_carrying_a_member_validity_code_is_lost_not_the_window` | Input: end reference `b5t-neg8-end-3`, succeeded, strict-valid, no envelope. Base (helper supplied by a probe): no re-screen ran, `derived/neg8-screen.json` absent. Lane: lost as `energy_unreadable`; kept when survivors pass, `neg8.screen_failed` when they fail; its energy requested by neither pass. |
| K-5 | `aba9a2f32` | `harvest.py`, `tests/test_harvest_b5_window.py` | `PreHarvestCodeTests` (5 tests); `UnwrittenCoreFlagTests.test_a_flag_file_line_torn_inside_calibration_capt_is_disclosed_and_removes_nothing`; `…test_a_torn_flag_line_is_disclosed_or_excluded_by_what_it_still_shows` (rewritten) | Before: the line cut inside `calibration.capt` added `records.malformed_flag_exclusion_possible`. Lane: disclosed, exclusion reasons unchanged. A line cut inside `model.identity_m` still removes the window. |
| K-6 | `b12b41a06` | `harvest.py`, `tests/test_neg8_survivors.py` | `HarvestSurvivorTests.test_each_of_the_four_physics_codes_loses_a_reference_and_the_survivors_decide`, `…test_a_journal_gap_over_one_reference_loses_it_and_the_survivors_decide`, `…test_a_monitor_outage_over_all_three_references_of_one_endpoint_removes_the_window`, `…test_a_reference_with_unmeasured_clock_or_thermal_evidence_is_kept` | Before: no re-screen ran; the hidden-drift window and the outage window were both kept. Lane: reference lost; hidden-drift removed; outage removed with `references_insufficient`. `clock.unmeasured` on all seven references loses none. |
| K-7 | `d072b7952` | `harvest.py`, `scripts/harvest_b5_window.py`, `tests/test_harvest_b5_window.py` | `HarvestCheckoutTests` (4 tests); `CliTests.test_cli_prints_the_checkout_it_ran_from` | Before: `KeyError: 'harvest_checkout'`. Lane: both files hold the commit, clean state and three file digests. |
| H-8 | `2ed4358bd` | `harvest.py`, `tests/test_harvest_b5_window.py` | `IdentityReplayTests.test_a_driver_checkout_whose_code_differs_from_the_sealed_code_is_a_difference`, `…with_the_sealed_bytes_is_recorded_and_raises_no_flag`, `…test_a_driver_checkouts_own_status_is_replayed_in_the_scope_it_executes`, `…test_a_driver_checkout_that_cannot_be_compared_is_identity_unmeasured` | Before: no flag for a changed, missing or added code file. Lane: `code.executed_differs_from_sealed`; identical bytes stay a record. |
| H-9 | `36ccd798c` | `harvest.py`, `tests/test_harvest_b5_window.py`, `tests/flags/test_flags_collect.py` | `IdentityReplayTests.test_a_changed_window_input_after_the_seal_is_still_a_difference` (six new paths); `CheckoutIdentityTests.test_the_harvest_and_the_collector_class_paths_alike_but_for_the_harvests_positive_list`, `…test_on_every_tracked_path_the_harvests_window_inputs_contain_the_collectors` | Before: `hashlib.py`, `env/mac-measurement-lock.txt`, `pyproject.toml`, `.gitignore`, `.gitattributes`, `analysis/zz_new.py` raised no flag. Lane: each is a difference. |
| H-10 | `339a15d76` | `harvest.py`, `tests/test_harvest_b5_window.py` | `IdentityReplayTests.test_a_sealed_inventory_with_files_and_no_head_is_identity_unmeasured` | Before: no flag, and the arm's flag was superseded. Lane: `code.identity_unmeasured` (`sealed_inventory_head`); the arm's flag stands. |
| H-11 | `e75a31152` | `harvest.py`, `tests/test_harvest_b5_window.py` | `IdentityReplayTests.test_a_changed_path_that_is_not_utf8_is_listed_and_classed_not_a_fault` | Before: `HARVEST_FAULT`. Lane: `COLLECTED`; the `docs/` path is recorded, the `joulewise/` path is a difference. |
| H-12 | `71386deac` | `harvest.py`, `tests/test_harvest_b5_window.py`, `tests/flags/test_flags_collect.py` | `IdentityReplayTests.test_another_claim_packs_directory_is_record_only_for_a_window_of_a_different_pack`, `…test_a_commit_confined_to_another_claim_pack_is_recorded_not_a_difference`, `…test_the_claim_packs_are_the_sizing_files_three` | Before: the tests error on the missing constant and signature. The behavioural "before" is cold pass 5's executed C6, not re-run here. Lane: recorded; the window's own pack is still a difference. |
| H-13 | `c10257418` | `harvest.py`, `tests/test_harvest_b5_window.py` | `DocstringFactTests.test_the_reference_identity_docstring_states_the_catalogs_effect_of_underivable` | Before: fails (docstring said UNCLASSIFIED). Lane: states EXCLUDE_MEMBER. No executable line changed. |

## Modules run on the final head

Interpreter `/opt/homebrew/bin/python3.13 -B`, `TMPDIR=/private/tmp/w1007-harvest-lane/tmp`. No failure, so no load rerun was needed.

- **`tests.test_harvest_b5_window`**: 202 OK, 551 s.
- **Fourteen small modules**: 224 OK. `tests.test_b5_seal_landing`, `tests.hazards.test_refusal_allowlist`, `tests.flags.test_flags_{collect,exclusions,catalog,core,schema,identity_pins,import_graph,fx_regressions,review_regressions}`, `tests.test_d165_rationale_census`, `tests.test_digest_pin_census`, `tests.test_b5_chain_static_check`.
- **NEG-8 and whole-window modules**: 287 OK. `tests.test_neg8_survivors`, `tests.test_whole_window`, `tests.test_whole_window_selection`, `tests.test_hazard_neg8_mint_verdicts`, `tests.test_harvest_b5_p2harv`, `tests.test_harvest_b5_p3harv`, `tests.test_gate_prune_integration`.
- **Writer and consumers**: 488 OK, 2 skipped. `tests.test_floor_extraction`, `tests.test_mint_floor_artifact_generalized`, `tests.test_run_campaign`.

No process of the lane is left running.

## Base versus lane on the rehearsal window

Base `9395cecfb`, lane `c10257418`, same plan as the seal-landing lane's `run_ab.sh`. Both `COLLECTED`, `claim_usable` false, 13 members assessed. Flags 186 → 188. All 20 withheld files are identical, and so are `neg8-screen.json`, `neg8-allowance.json` and `neg8-bound.json`.

| Difference | Item |
|---|---|
| New `code.executed_differs_from_sealed`: the rehearsal's driver checkout lists untracked `scripts/rehearse_b5_real.py` | H-8 |
| New `code.identity_unmeasured`: the rehearsal's sealed inventory names no head | H-10 |
| `exclusions.json`: those two reasons and counts, plus `harvest_checkout` | H-8, H-10, K-7 |
| `harvest.json`: `harvest_checkout`, flag count, reasons | K-7 |
| `code-identity.json`: driver checkout status fields; `own_pack` and `changed_paths_in_other_claim_packs` | H-8, H-12 |

Paired flags differ only in `emitted`.

## Fence

`git diff --name-only 9395cecfb..HEAD` lists exactly: `joulewise/b5/harvest.py`, `joulewise/whole_window.py`, `scripts/harvest_b5_window.py`, `tests/flags/test_flags_collect.py`, `tests/test_harvest_b5_window.py`, `tests/test_neg8_survivors.py`. The four pinned estimator files, `scripts/prewindow_check.sh`, `scripts/run_campaign.py` and `joulewise/flags/collect.py` have the same git blob at base and head. No new flag code is emitted and no catalog effect changed.

## Not implemented inside the fence, and choices to rule on

1. **Claim-time replay of a K-4 row is unchanged.** The row validator still calls `_derived_neg8_decision` with the default `unreadable_energy="refuse"`, so a stored bracket with a no-energy entry does not replay at claim time. That is lane L9-NEG8 part (c); the keyword it needs is there. The allowance reader already accepts the survivor bracket of such a window (probed: no problem, counts 3/1/2).
2. **The predicate lives in `whole_window.py`, not a new module.** The L9-NEG8 design wants `joulewise/neg8_survivors.py`; a new file is outside the fence. `_neg8_writer_reference_energy` sits beside `_gross_fields` and can be moved.
3. **The gate ruling supersedes two lines of the L9-NEG8 design.** Its "an unmeasured reference is kept" and its test T-A3 are overridden by RF-5.
4. **K-4, `member.bytes_missing` on a never-run reference is not a new loss.** With no bundle directory the stored counts already lack it and it stays `bundle_absent`. Otherwise the two-absent case lost its `references_insufficient` disclosure. A present bundle with a missing file is a loss.
5. **K-5, a whole code keeps itself as its one candidate.** The narrowing applies to a prefix only.
6. **K-5, the set is slightly wider than what is written today.** `PRE_HARVEST_CODES` includes `window_lineage.FINDING_CODES` as ruled, though no pre-harvest program writes a lineage finding as a flag today. It also includes `collector.unmeasured`, which is in no catalog and so UNCLASSIFIED as a candidate. Its eight EXCLUDE_WINDOW members are the refuter's eight.
7. **H-8, the status replay is scoped.** A tracked edit counts only when the path is a window input; a changed doc or test in the driver checkout is recorded. The review's wording was any tracked edit. Widening is one line.
8. **H-9 and H-12 leave the arm collector as it was.** The two classifiers now differ in both directions; the rewritten parity test states the relation.
9. **Judge's finding 11 (corpus members with unmeasured physics) is not changed.** It was not ruled, and it would change a registered rule (§5.3). The four K-6 codes are deliberately outside `NEG8_PHYSICS_LOSS_CODES`.
10. **Observed, outside the items.** A reference whose stored summary reads by the writer's test but whose fresh reduction is precheck-ineligible still returns `provenance` in the harvest's authenticity pass. If a re-screen is needed the window is excluded; if none is needed the stored screen stands. This is by reading, not executed; it belongs to L9-NEG8.
11. **Fixture change.** The synthetic reference bundles now carry stored energies; with `{"status": "succeeded"}` alone every one was energy-unreadable by the writer's own test.

## SHA-256 of each changed non-test file at the head

- `joulewise/b5/harvest.py`: `f68e53d4e84292c182772a20edf2e3649c7470a7113ff87ebdec6f91208c9bc2`
- `joulewise/whole_window.py`: `ee107b1e5f7eab306192c78d43171de828c290158bd3dc6fb5e63c229a1c25a5`
- `scripts/harvest_b5_window.py`: `88ac1164e729691e4db249b77ebbd17072dbcd3f514499840a56f56576d66d45`

The lane's own harvest of the rehearsal recorded these same three digests in `harvest_checkout.files`.

## Paths

- Notes and A/B artifacts: `/Users/edr/night-archive/gate-prune/wave-1007b/harvest-lane/` (`NOTES.md`, `ab-compare.log`, `run_ab.sh`, `compare_ab.py`, test tails)
- Scratch, disposable: `/private/tmp/w1007-harvest-lane/` (A/B archives, test logs, counterfactual probes under `cf/`). The two snapshot worktrees I made were removed.
- Worktree: `/Users/edr/code/JouleWise-wt-harvest`
