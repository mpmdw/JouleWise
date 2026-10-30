STATUS: DONE

# RC-CMP-10: fix round inside the RC-CMP-9 design (FS1-FS4, Opus F1-F2, Fable F1-F4, literal pins)

Seat RC-CMP-10, branch `lane/2026-10-27-recompute-comparator`, from `f9f86869e`. Synthetic data only: no real
block-5, block-6 or BYTES data was opened or searched for. The tracked window index
(`configs/analysis/b5/analysed_windows.json`) was read only by the comparator's loader to check that it parses
(11 attempts; field types only). `python3.13`, `TMPDIR=/tmp/claude-0/rccmpten_tmp` (outside the checkout, no
float-like token). The script still imports no repository code (`test_no_l9_import`; `itertools` added to the
stdlib allowance). Producers were read as text from `origin/main` (now merged); the tests import producers only to
build fixtures (`producer_fixtures.py`, `detection_floor.TRANSPORT_RULE_ID`).

Reviews read: `review/2026-10-30-rc-cmp9-opus-rev` (`RC-CMP9-OPUS-REV.md`, `probe_cmp9.py`, `drop.out`) and
`review/2026-10-30-rc-cmp9-fable-rev` (`RC-CMP9-FABLE-REV.md`, `probes.py`, `probes_extra.py`, `sweep.py`,
`classify.py`).

## SUMMARY

- **Merge.** `origin/main` (b547253a9) merged into the lane as `ab4029f7b`, no conflicts, nothing resolved by hand.
  Suite at the merge: 362 tests OK (18 skipped).
- **FS1.** Each resolution's `transport_rule_id` is compared with its arm's registered transport group
  `group_rule_id` (`same_stack_componentwise_worst_case.v1` = `detection_floor.TRANSPORT_RULE_ID`). The selector's
  `exact_stack_only.v1` is printed in no L9 output (the engine's floor and v3 floor key sets carry no
  `transport_rule_id`; pinned), so there is no selector-level row to keep.
- **FS2.** `P42_EXIT` and the invented `p42_expected_unresolvable` are gone (a test asserts the word is not in the
  script). The p42 code must be one of the kernel's closed refusal codes (`REPORTED_REFUSAL_CODES`, copied from
  `paper_reported_energy.PAPER_REPORTED_ENERGY_REFUSAL_CODES` and pinned) and equal in every L9 copy: the
  projection's refused cell, the sensitivity record, its disclosure copy and its block line. The recompute derives
  no refusal reason, so there is nothing to re-derive. The fixtures' code now comes from the issuer itself:
  `producer_fixtures.p42_refusal_code()` runs `tests/b5_analysis/fixtures_s8`'s pack through the issuer (T12's path)
  and gets `paper_reported_energy_record_invalid`.
- **FS3.** `Comparison.word` and `Comparison.atom` implement the rule. A word derived from the sign of, or a threshold
  on, a compared number is compared exactly only when every test it reads lies outside the number's family bar from
  the threshold on both sides, or when the decided tests fix the word whatever the undecided ones are. Otherwise the
  row records `within_bar_undetermined` and the tests inside their bar (restricted output only), and it is AGREE only
  if every number it reads agrees within its bar. The rule is applied uniformly to:
  - the contrast `outcome`, `direction`, `holm_reject`, `ceiling` and `claim_ready`;
  - each leave-one-out row's `outcome`, `floor_status` and influence triggers (`estimate_sign`, `floor_status`,
    `adjusted_rejection`, `outcome`, `estimate_magnitude`);
  - `below_screen_bound/below`, the sensitivity windows' `widened`, the sensitivity rows' `equals_primary` and
    `not_below_primary`, the sensitivity contrast's `outcome`, `outcome_equals_primary` and its primary `outcome`;
  - `cross_window/agree`, the `loo_magnitude` row selection, the D-165 `branch` and `dominance_sentence_licensed`,
    and `machine_member/plausible`.
  The full-size case (decode loo b10: L9 +3.55e-15, recompute -1.78e-15, `["estimate_sign"]` against `[]`) passes;
  the same flip outside the bar DISAGREEs.
- **FS4.** The comparator reads the window index L9's run read (`--window-index`, default the tracked
  `analysed_windows.json`). The bytes must have the digest the dry-run record carries (`window_index_sha256`),
  otherwise it refuses `window_index_digest_differs`. The history lines become table entries keyed on the index:
  - `attempt_count` per (pack, deciding or superseded group);
  - `attempt_history` per attempt;
  - `g10` per attempt (expected when the index requests G10, conditional otherwise);
  - `superseded_history` when any attempt is superseded;
  - `reharvest_account` per pack (conditional).
  Their leaves are bound to rows against the index (`compare_history`): `count`, `causes/*` (null allowed),
  `superseded`, `verdict`, `cause_key` (null allowed) and `redraw_cycles`. A null `triggers` is a named exemption
  (no calibration bracket; the same rule as `erratum3_triggers/values`). No producer history leaf is unmapped.
- **OPUS F1.** L9's leave-one-out row count (`loo/l9_rows`) and `loo_counts/count` are bound to the kept n whenever
  the engine prints rows (`loo_status(n) == complete`: 1 ≤ n, at most `LOO_REQUIRED_MAX` registered blocks), and
  `loo_block_kept` requires L9's rows from n ≥ 1. The recompute's own row count stays from `LOO_MIN` = 3 (the
  recompute is unchanged).
- **OPUS F2.** These keys are now required:
  - `bundle_blocks/included_bundle_ids`;
  - each registered block's `_BLOCK_KEYS`;
  - `randomization_check/{status,reason,n_blocks,exact_two_sided_p,rejects}`;
  - `estimator/repeat_point_CI95/{lower,upper}` and every `estimator/variance_contributions/*` item's
    `_VARIANCE_CONTRIBUTION_KEYS` (a `*` step in `absent_keys`).
  They are required in the verdict and in the disclosure's `primary_contrast` estimator copy.
- **FABLE F1.** Conditional families build value rows under the table's own `condition_holds` (`holds()`, over the
  same documents). When both sides refuse, only status words are compared:
  - floors: `floor_computed`;
  - magnitude ratio: `computable`;
  - reported cells: status `refused` and code `paper_reported_energy_kept_units_below_minimum`, against the
    recompute's `below_minimum`.
  This also closes RC-CMP-9 OPEN ISSUE 1 (a refused non-p42 cell) and the not-computable half of OPEN ISSUE 2: the
  assist contrast builds only the value rows its status word prints.
- **FABLE F2.** These verdict words are now bound:
  - the verdict's `sampling/kept_n`, against the recompute's n;
  - its `sampling/removed_block_ids`, by position against the registered blocks the recompute leaves out (the
    fill's copy now binds to these rows);
  - each registered block's `included`, against the recompute's kept set.
- **FABLE F3.** Pinned: `build_results_fill_input.py` passes `finalized_manifest_raw=manifest_raw` and
  `floor_artifact_raw=floor_raw`, and the adapter's `extended = any(...)` precondition.
- **FABLE F4.** The fill's `finalized_manifest/{file_sha256,manifest_id}` are bound to the finalized manifest that
  L9's custody lists (`finalized/<id>.finalized.json`: its listed digest and its `manifest_id`). That manifest's
  `lineage.prospective_manifest_sha256` must equal `REGISTRY_PINS[MANIFEST]`. P8 exits 2.
  `Custody.step_ok` is deleted.
- **New rule (pins).** Every word or code the comparator expects L9 to print is pinned in `test_rc_cmp10.py`
  `LiteralPinTests` (10 tests) to the producer line or sealed config that prints it (list below).
- **Suite:** `Ran 393 tests`, `OK (skipped=18)`, exit 0 (31 new in `test_rc_cmp10.py`).

## Per-item table

Counterfactuals: "in place" means a test in `test_rc_cmp10.py` (or the updated older test) switches this round's
check off and shows the f9f86869e outcome. The probe outcomes at f9f86869e are the reviewers' published outputs and
the lead's full-size run (RUN_STATE item 124).

| Item | Evidence at this head | At f9f86869e |
|---|---|---|
| Merge | `ab4029f7b`, a merge commit; suite 362 OK at the merge | — |
| FS1 | `TransportRuleTests`: the engine's word AGREEs; a resolution printing `exact_stack_only.v1` DISAGREEs; `LiteralPinTests.test_transport_rule_is_the_group_rule` | Full-size: 4 rows DISAGREE. In place (the selector's word as the reference): 4 `transport_rule_id` rows DISAGREE |
| FS2 | `P42CodeTests`: the producer's code passes, and every copy binds `outcome_word`. The invented word in every copy: non-zero. A member code differing in one copy (projection, record or block line): non-zero. A member code identical everywhere: passes (NEEDS_RULING 1). `test_p42_and_refusal_codes` | Full-size: 2 rows DISAGREE. In place (the invented reference): the invented fixture passes and the producer's code refuses |
| FS3 | `WithinBarTests`: the full-size b10 flip inside the bar exits 0 (row `within_bar_undetermined`, AGREE), and L9 printing `[]` there also exits 0. The sign decided (+1.0 both sides) with a missing trigger: DISAGREE. A flip with disagreeing numbers: non-zero. `below_screen_bound` at the bound: passes, away from it: DISAGREE. `holm_reject` at alpha: undetermined, beyond it: compared. Relation words: undetermined unwidened, a decided difference still compared | Full-size: 3 rows DISAGREE. In place (`plain_exact`, no undetermined trigger): non-zero |
| FS4 | `HistoryTests`: the producer's own history lines (`disclosures._history_lines` over a 6-attempt index: superseded and no-archive attempts, cause keys, G10 requested and printed, a calibration bracket) exit 0, with `causes/*`, `cause_key`, `verdict`, `count` and `redraw_cycles` bound and a null `triggers` named. 12 drop and change cases are non-zero, among them a dropped line, a changed cause, count, verdict, superseded word or redraw count, and an attempt the index lacks. Index digest mismatch: `window_index_digest_differs`. Re-harvest accounts follow `harvest_once` | Full-size: `attempt_count/causes/*`, `attempt_history/cause_key` and `attempt_history/triggers` unmapped. In place (without the history rules): `refused=step11_unmapped_fill` |
| OPUS F1 | `LeaveOneOutTests.test_rows_dropped_refuse`: at a kept n of 1 and 2, widened and unwidened, each "rows dropped" case is non-zero (`loo/l9_rows` (0, n), `loo_counts/count` against n). `probe_cmp9.py n2` at this head: sound exit 2, rows dropped with count 0 exit 2, rows dropped with count 2 exit 1, on both windows | Opus `cmp9_n2.out`: rows dropped with count 0 exit 0. In place (rows from `LOO_MIN`, the old `loo_counts` reference): exit 0 |
| OPUS F2 | `NestedKeyTests.test_each_nested_key_dropped_refuses`: 15 drops (`included_bundle_ids`, a block's `bundle_a_id`, `bundle_b_id`, `reason_codes` and `included`, each `randomization_check` key, `repeat_point_CI95` lower, a variance-contribution key, and the disclosure copy's `repeat_point_CI95` and contribution key): all non-zero | Opus `drop.out` exit 0. In place (the RC-CMP-9 key sets): each exits 0 |
| FABLE F1 | `ConditionalFamilyTests`: P1, P3, P4 and X5, widened and unwidened (that is, P1/P3/P4 and X1/X3/X4/X5), exit 0. Each one-sided case (P2.a/b, P3.a/b, P4.a/b) is non-zero. The refused cell's status words are compared. Fable's `probes_extra.py` at this head: P1 0, P2.a 2, P2.b 2, P3 0, P3.a 1, P3.b 2, P4 0, P4.a 1, P4.b 2, X1 0, X3 0, X4 0, X5 0 | Fable `probes.out`/`probes_extra.out`: P1 2, P3 2, P4 1, X1/X3/X5 2, X4 1. In place (`holds` always true): P3 and P4 refuse |
| FABLE F2 | `test_fable_p6_p7_verdict_sampling_words`: P6.a, P6.b and P7.a are non-zero. Fable's probes at this head: P6.a 2, P6.b 2, P7.a 1 | Fable: P6.a, P6.b and P7.a exit 0. In place (without the three rows, the f9f86869e rules): exit 0 |
| FABLE F3 | `LiteralPinTests.test_extended_fill_precondition` | unpinned |
| FABLE F4 | `FinalizedManifestTests`: P8 non-zero; a lineage naming another prospective manifest: non-zero; `step_ok` absent. Fable P8 at this head: exit 2 | Fable P8 exit 0. In place (the IDENTITY rule, no row): exit 0 |
| Pins | `LiteralPinTests` (10 tests) | — |
| RC-CMP-6..9 | All older tests pass (after the updates listed under FILES CHANGED). Probes at this head: see below | — |

Probes at this head (outputs in the session scratchpad; reruns of the reviewers' scripts unchanged except the
repository path):
- `probe_cmp8.py confirm`: 0 exit-0 cases, on both windows.
- `probe_cmp8.py joint2`: all 10 cases non-zero.
- `probe_cmp8.py loo`: only the control exits 0.
- `probe_cmp8.py relabel`: `identity relabels tried: 4087; exit 0: 0`.
- `probe_cmp9.py n2`: as above.
- `probe_cmp9.py extra`: as at RC-CMP-9, except that dropping the `attempt_count` line now also fails the history
  row. Only the declared `machine_absent` and `flag_count` drops and the equal-valued R/R_cm text swap exit 0.
- `probe_cmp9.py absent`: exit 0.
- `probe_cmp7.py all`: A0 control 0. A4, A5, C5 and K10 exit 0, as declared at RC-CMP-9. The relabel sweep tried
  15189 relabels, 6 exit 0, all `machine_absent` relabelled into `catalog_path` or `lost_midpoint`. The words probe
  gave 295 exit-0 mutations, the same count and declared classes as RC-CMP-9 (text, label, restricted, identity,
  harvest words, reason codes).
- Fable `probes.py` (P0 to P13): as in the table. P5.a/b exit 2, P9.a 2, P9.b 0 (declared `LOAD_LINE`), P10.a/b 2,
  P11.a 1, P11.b 1, P12.a/b 2, and P13 exits 0 on both windows.
- Fable `sweep.py`: `deletions tried: 5035; exits: {1: 1673, 2: 2719, 0: 643}` (735 exit 0 at f9f86869e).
- Fable `classify.py` on that sweep: **0 UNDECLARED**.
  - `attempt_count causes`: 0 (was 3).
  - The verdict's `sampling/removed_block_ids` members: 0 (was 2).
  - Fill identity pins: 0 (was 2).
  - The 40 verdict-internal exit-0 deletions are all list members whose values are declared exemptions:
    `included_bundle_ids/N`, `reason_codes/N` and whole `variance_contributions/N` items. Their keys are now
    required.

**Class sweep (output-derived existence).** New table entries and their key sources:
- `fill_identity`: a constant path.
- The history entries: the window index, a registered source bound by digest to L9's record.
- Per-block locators: `registry.blocks`.

New row constructors:
- `blocks/<id>/included`: `pairs` over `registry.blocks`.
- `sampling_removed_block_ids`: positions against the registered blocks.
- `history/*`: the table's entries; rows are keyed by the concrete position the entry resolved to.
- `fill/finalized_manifest/*`: constant keys.
- `projection/refused/<cid>/code`: registered cells.
- `loo_magnitude`: the existing union, with undetermined blocks put on both sides.

Two new conditions read L9's own line (`history_printed`: `g10` without a G10 request, `reharvest_account`). They
only switch an expectation on, and the lines carry no compared claim (NEEDS_RULING 3). No new existence depends on
the recompute's output. `test_structural_rules` (family functions iterate only through `pairs` or constants)
passes.

## The pinned-literal list (new rule)

Each literal below is a word or code the comparator compares against something L9 prints. Each is pinned by a test
to its producer line, unless marked otherwise.

| Literal(s) in the script | Producer / source | Pin |
|---|---|---|
| `transport_rules` (from the manifest's `group_rule_id`) | `detection_floor.TRANSPORT_RULE_ID`; `inputs.py` `transport_rule_id=TRANSPORT_RULE_ID`; `analysis_engine/__init__.py` resolution row | `test_transport_rule_is_the_group_rule` |
| `REPORTED_REFUSAL_CODES` | `paper_reported_energy.PAPER_REPORTED_ENERGY_REFUSAL_CODES` | `test_p42_and_refusal_codes` |
| `BELOW_MINIMUM_CODE` | `paper_reported_energy.estimate_reported_cell` raise | same |
| `P42_REFUSED_STATUS` `"refused"` | `sensitivity.py` refused row | same |
| `P42_UNRESOLVABLE`, `REPORTED_BELOW_MINIMUM` (recompute side) | `independent_recompute_b5.py` | same |
| outcome words (`decide_outcome`, `threshold_free`) | `analysis_engine/claims.py` `CLAIM_OUTCOMES` | `test_outcome_direction_ceiling_words` |
| `"positive"`/`"negative"` (`sign_word`) | `claims.py` direction | same |
| `READY_CEILINGS`, `"L1"`/`"L2"` (`ceiling_of`) | `artifact.py` ceiling sets | same |
| `V3_AGGREGATION` `"max_never_sum"` | `artifact.py` | same |
| `registry.alpha` | sealed manifest `families[*].multiplicity.alpha` (read, not typed) | same |
| `loo_status` words `"complete"`/`"not_run"` | `analysis_engine/__init__.py` | `test_leave_one_out_words` |
| `FLOOR_STATUS_WORDS` | `_loo_family` floor_status | same |
| `INFLUENCE_TRIGGERS`, `MAGNITUDE_SHARE` | `analysis_engine/sensitivity.py influence_triggers` | same |
| arm ids `"A"`/`"B"` | `arm_by_condition` in `analysis_engine/__init__.py` | same |
| `"agrees"`, `"controller_stamps"` (recompute words) | `independent_recompute_b5.py` | same |
| `DOMINANCE_THRESHOLD`, `DOMINANCE_BRANCHES`, ratio status `"complete"` | `dominance_closeout.py` | `test_closeout_and_disclosure_words` |
| `RATIO_TEXT` (`R`/`R_cm`), `NUMERATOR_FIELDS` | `disclosures._closeout_lines`; `run_d165_closeout_from_custody.py` | same |
| `"computed"` (cell status), `paired_status` words | `disclosures._cell_values`, `_paired_values` | same |
| `SCREEN_BOUND_S`, cross-window agree test, `SHORT_MODELS`, `PACKS` | `disclosures.py` | same |
| `labelled(..., "sensitivity")` | `sensitivity.py` `"label": "sensitivity"` | same |
| `KIND_ORDER` | `paper_reported_energy.BOUND_KINDS` | same |
| every `LINE_KEYS` line word; `CELL_WORDS`, `CONTRAST_WORDS`, `BLOCK_WORDS`, `WINDOW_LINES`, `TRIPWIRES` | `disclosures.py` `_item` words | `test_line_words` |
| `HISTORY_KEYS`, `HARVESTED_HISTORY_KEYS`, `DECIDING_SEAL`, `NO_ARCHIVE`, `WINDOW_INDEX_SCHEMA` | `disclosures._history_lines`; `archive.open_attempt_record`; `windows.py` | `test_history_words_and_keys` |
| `FINALIZED_MANIFEST`, `FINALIZED_MANIFEST_KEYS`, lineage key | `analysis_manifest_v3.py`; `artifact._INPUT_ARTIFACT_KEYS`; `results_fill_adapter.py` | `test_finalized_manifest_words` |
| `ENGINE_KEYS` new sets (`bundle_blocks`, `block`, `randomization`, `variance_contribution`) | `artifact.py` | `test_new_engine_key_sets` |
| RC-CMP-9 key sets, tripwires, battery codes, trigger keys, fixed sentences | as pinned by RC-CMP-9 | `ProducerPinTests` (unchanged) |

Unpinned literals, with the reason each needs no pin:
- `"extractable"` in `p42_word`: a comparator-internal word that never matches a registered word, so it can only
  DISAGREE. It is never compared with an L9-printed word.
- `"/unregistered_numerator"`: an internal key suffix that can only DISAGREE.
- `REFERENCE_INPUTS` keys: sealed plan-tree input ids, read through the digest-pinned registry. An unknown id raises
  `routing_registry_invalid`.
- `"none"` (direction): the comparator's spelling of a null direction on both sides. Its raw value is kept.

## FILES CHANGED

- `scripts/compare_b5_recompute.py`:
  - FS1: `Registry.transport_rules`; `compare_arms`.
  - FS2: `REPORTED_REFUSAL_CODES`, `P42_REFUSED_STATUS`, `P42_UNRESOLVABLE`, `refused_code`, `code_of`,
    `projection_refused`; the p42 branch of `compare_sensitivity`.
  - FS3: `Comparison.word`, `Comparison.atom` and `Comparison.bar`; the test helpers (`outcome_atoms`,
    `decide_outcome`, `trigger_atoms`, `undetermined_triggers`, `relation_words`, `branch_tests`,
    `magnitude_tests`, `agree_margin`, `sensitivity_tests_numbers`, ...); `INFLUENCE_TRIGGERS`, `MAGNITUDE_SHARE`,
    `FLOOR_STATUS_WORDS`, `DOMINANCE_THRESHOLD`, `DOMINANCE_BRANCHES`; `Registry.alpha`.
  - FS4: `WINDOW_INDEX`, `load_window_index`, `indexed`, `history`; `Custody(..., window_index)`; `--window-index`;
    the history table entries (`history_line` kind, entry `expect`); `history_printed` condition;
    `compare_history`; coverage rules; `POSITIONS` (`block_line`, `cause`); history words in `BLOCK_WORDS`;
    `g10` identity pattern (`[a-z_0-9]+`).
  - Opus F1: `loo_rows_expected`; `l9_rows`, `loo_counts` and the `loo_block_kept` condition.
  - Opus F2: `ESTIMATOR_NESTED`; the new `ENGINE_KEYS`; `*` in `absent_keys`; per-block locators.
  - Fable F1: `holds`, `window_floors`; `compare_floors`, magnitude ratio, assist contrast and refused reported
    cells; `Registry.reported_id`; `REPORTED_BELOW_MINIMUM`, `BELOW_MINIMUM_CODE`; the aggregate primary allowance
    from the window's NEG-8 allowance; the `SF primary/allowance_j` rule binds the record's own row.
  - Fable F2: the `kept_n`, `sampling_removed_block_ids` and `blocks/<id>/included` rows; `registered_kept`,
    `printed_included`.
  - Fable F4: `FINALIZED_MANIFEST`, `compare_fill_identity`, the `fill_identity` entry; `step_ok` deleted.
  - Module docstring.
- `tests/independent_recompute/test_rc_cmp10.py` (new, 31 tests).
- `tests/independent_recompute/producer_fixtures.py` (new): history lines via `disclosures._history_lines`; the p42
  code via the issuer.
- `tests/independent_recompute/window_index/synthetic.json` (new): the base fixture's window index.
- `tests/independent_recompute/test_comparator.py`:
  - `cmp.WINDOW_INDEX` points at the fixture index, and the record carries its digest.
  - History lines and the p42 code come from the producers; the resolutions print `TRANSPORT_RULE_ID`.
  - A finalized manifest is in custody, with the fill's digest of it.
  - NEG-8 drift allowance 1.0, equal to the floors' allowance, as in the recompute, where the floor allowance is
    the window's.
  - Updated assertions:
    - `test_planted_contrast`: the moved D also disagrees in one relation-word row;
    - `test_planted_kept_units`: 9 included rows, with the counterfactual lenient on them;
    - `test_planted_p42_status`: the projection code row;
    - `test_no_l9_import`: `itertools`.
- `test_rc_cmp7.py`: the same NEG-8 allowance (1.0).
- `test_rc_cmp8.py`:
  - The p42 code comes from the producer.
  - Relation-word flips are expected to pass where the base row is `within_bar_undetermined` (FS3; at least 10
    cases stay decided and fail). Partial-copy flips still fail.
  - `widened` flip: widened window only (FS3).
- `test_rc_cmp9.py`:
  - `indexed_registry()` for the table tests: counts (+`history_line` 9, `fill_identity` 1); `attempt_count` is
    now per group; the line-word sets.
  - Conditional items: g10 and reharvest not expected on the base.
  - Generic deletion: covers `history_line` and `fill_identity`, and deletes nested locators first.
  - The joint-drop and identity-relabel counterfactuals also switch off this round's rows.
- `.codex-report/RC-CMP-10.md` (this report).

## DECISIONS I MADE

1. **Fable F4 binds through L9's custody, not by literal equality.** The fill names the step-8 *finalized*
   manifest. Its bytes differ from the sealed prospective `analysis_manifest_v3.json`, so
   `file_sha256 == REGISTRY_PINS[MANIFEST]` would refuse every real or full-size run. The chain is:
   - the fill's digest equals the custody-listed digest of `finalized/<id>.finalized.json`;
   - that manifest's `lineage.prospective_manifest_sha256` equals `REGISTRY_PINS[MANIFEST]`.
   P8 still exits non-zero. NEEDS_RULING 4.
2. **The window index is the one L9's run read.** The default is the tracked file. A synthetic window's run reads its
   own index, so the full-size rerun must pass `--window-index <that index>`. Its digest must equal the record's
   `window_index_sha256`, and any other index refuses. Tests point the module default at the fixture index.
3. **FS3 composite words.** A test whose numbers are missing on one side counts as decided: the word is compared, and
   it disagrees through its missing numbers. A word with any test inside its bar is AGREE only if all of its
   numbers (and per-side thresholds) agree.
   - The bound-independent numbers of the sensitivity outcome (estimate, metrology interval, p) are read from the
     primary contrast on both sides, as `sensitivity.py` guarantees.
   - L9's sensitivity decision interval is its metrology interval widened by the sensitivity D. The engine prints
     no other.
4. **Relation words with unchanged values are undetermined (FS3 as briefed).** `equals_primary` /
   `not_below_primary` read sensitivity minus primary against 0, so an unchanged value is always inside its bar.
   Unwidened, those words are therefore no longer compared; their numbers are. A decided difference (widened) is
   still compared. `widened` is undetermined when b_sens = b_op.
5. **The aggregate floor's primary allowance comes from the window's NEG-8 allowance.** This is the value L9 reads
   from the extraction report whether or not the floor is computed, and the recompute's floor copies it. Without
   that, P3/X3 could not pass.
6. **FS2 extraction report.** It prints `refusal_reasons` in the floor-extraction vocabulary and no
   paper-reported-energy code, so it is not one of the code copies.
7. **Loo influence trigger rows.** The positional rows are keyed by L9's printed positions only. A trigger the
   recompute raises and L9 omits is DISAGREE in the whole-list row, which compares both lists without their
   undetermined triggers.
8. **`step_ok` is deleted** rather than given a caller: no check needs it.

## OPEN ISSUES

1. **The lead's full-size rerun.** The command must add `--window-index <the synthetic index the dry run read>`
   (the `JoinedHarness` fixture's `window-index.json`). Two assumptions are untested off the laptop:
   - the dry-run record lists `finalized/<manifest_id>.finalized.json` (step 8's output);
   - that manifest's `lineage.prospective_manifest_sha256` equals the sealed pin. The harness uses identical
     sealed packs, so I expect it to.
   If either fails, the run refuses or DISAGREEs on `fill/finalized_manifest/*`. Those two rows are the only place
   to look.
2. **Kept n of 1 or 2 over-refuses on the recompute's side** (Opus F1 left it so): the engine's rows are required,
   and the recompute prints none below `LOO_MIN`. This is the safe side; NEEDS_RULING 2.
3. **The refused dominance ratio's value rows** (RC-CMP-8 S3.b, half of RC-CMP-9 OPEN ISSUE 2) still over-refuse.
   There is no registered mapping from the recompute's refused ratio to the closeout's refusal word.
4. **Suite time** is about 600 s (was about 480 s at the merge).
5. Carried and declared, unchanged:
   - `machine_absent` / `flag_count` (NEEDS_RULING RC-CMP-9 4);
   - the machine lines and G7 (RC-CMP-9 NEEDS_RULING 2);
   - `LOAD_LINE`;
   - list-member deletions of declared value exemptions (`included_bundle_ids/N`, `reason_codes/N`,
     `variance_contributions/N`).

## NEEDS_RULING

1. **The p42 code has no re-derivation.** The recompute derives no refusal reason, so any closed-set code printed
   identically in every copy passes. The stricter reading would be to pin `paper_reported_energy_record_invalid`,
   but which code the p42 cell gets depends on the kernel's validation order.
2. **Whether the recompute should compute leave-one-out rows at a kept n of 1 or 2** (RC-CMP-9 NEEDS_RULING 5,
   unchanged; Ed's).
3. **Two history lines are conditional on L9's own line.** These are `g10` without an index G10 request (printed
   from the archive's `g10.*` flag codes) and `reharvest_account` (from the steps' re-harvest accounts). Neither
   source is registered. A drop of either line exits 0 unless `harvest_once` says a window was harvested twice;
   that case is bound by `history/reharvest_accounts_printed`. Neither line carries a compared claim.
4. **Fable F4's literal reading.** The brief said to bind the fill's `file_sha256` to `REGISTRY_PINS[MANIFEST]`.
   I bound it through the finalized manifest's lineage instead (DECISIONS 1), because the literal reading would
   refuse every run.
5. **FS3 applied to relation words removes their comparison whenever a value is unchanged** (DECISIONS 4). If Ed
   prefers exact equality to count as decided for by-construction equalities, that is a one-line change in
   `relation_words`.

## VERIFICATION

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
at this head: `Ran 393 tests in 629.507s`, `OK (skipped=18)`, exit 0 (362 at the merge + 31 in `test_rc_cmp10.py`).
