STATUS: DONE

# RC-CMP-7 seat report

bridge-report/v1 · scheduled seat RC-CMP-7 (lead: joulewise-28, block-5 lead) · branch
`lane/2026-10-27-recompute-comparator`, base `1134bbf58`, three milestone commits (`b3f871ed`, `7c667ffd`, and the
F3/report commit). Synthetic data only: no real block-5, block-6 or BYTES data was opened or searched for.

- Interpreter: `/usr/bin/python3.13`.
- `TMPDIR=/tmp/claude-0/rcseven`, which is outside the checkout and has no float-like token.
- Counterfactual worktree at `1134bbf58` under the same TMPDIR; removed afterwards.
- No import of `joulewise.b5_analysis` or `joulewise.external`. The producers on `origin/main` were read as data only:
  - `disclosures.py`, `sensitivity.py` and `kept_units.py`;
  - `dry_run.py` step 2;
  - `dominance_closeout.py`;
  - `run_d165_closeout_from_custody.py`.

## SUMMARY

- **G7 (FIX-BRIEF-3 Amendment 1) is implemented.**
  - `run_phase_energy_j` takes its key universe from L9's step-2 selection, applied identically to both sides. The
    selection is the run ids of the kept units in L9's kept-units record (`dry_run.kept_bundles`).
  - The roles come from the three sealed v5 plan trees, which are pinned by digest. They mark each member as science,
    a NEG-8 reference, a spare or a diagnostic member.
  - A member registered as a NEG-8 reference is excluded from the family and listed in the restricted output
    (`excluded_members`) with the reason `compared_in:reference_counts` or `compared_in:corpus_counts`.
  - Results:
    - RC-CMP-4's window (both causes, producer-shaped) gives exit 0 at the new head. At `1134bbf58` it gives exit 1
      with exactly RC-CMP-4's 162 failing run rows.
    - Opus G7.1 passes. Opus G7.2 now DISAGREEs.
    - A reference member dropped from a NEG-8 line still DISAGREEs.
- **F2 (Opus finding 2) is fixed.** A line word read from the document can no longer move compared leaves under an
  exemption.
  - The disclosure gate admits a line word only in the section its producer writes it to, and only with that word's
    producer keys.
  - Both broad subtrees are now enumerated leaf names.
  - Every printed claim word that the recompute re-derives is compared exactly.
  - Opus's relabel sweep gives 0 exits (58 at `1134bbf58`). Every wrong categorical word in its own line refuses.
- **F3 (Opus finding 3, also Fable F2) is fixed.**
  - Leave-one-out rows key only on the contrast's registered block ids (`analysis_manifest_v3` `block_ids`).
  - Ratio rows key on the registered numerator fields.
  - The `R`/`R_cm` text label of the comparative dominance line stays (OPEN ISSUES 3).
- **Fable delta review** (`review/2026-10-29-rc-cmp6-fable-rev` at `770db4aa`, fetched at start and again before
  this report):
  - Its only BLOCKING finding, F1 (G7 absent), is closed by G7. Its regressions P1a, P1c and P2b are tests here.
  - Its F2 (the loo id parse) is closed by F3.
  - Its F3 (LOW, step status never read) is not in this brief and is listed under OPEN ISSUES.
- **Verification.**
  - `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
    gives `Ran 303 tests in 171.744s` / `OK (skipped=18)`. It was 282 at `1134bbf58`; every earlier test still runs,
    and four were adjusted as listed under DECISIONS.
  - Opus's `probe_cmp6.py` at this head: every section runs except `loo_parse`, which calls the old one-argument
    `loo_key`. With that one call adapted to the new signature, it runs to completion. The output is quoted in the
    table.

## G7 / F2 / F3

Tests are in `tests/independent_recompute/test_rc_cmp7.py`.

### G7

- **Universe from registered roles, both sides identical.**
  - Evidence at head: `step_2_universe` and `compare_runs` use `c.pairs("run/", rereduced_names, universe, selected)`.
    L9 holds a key only when the run is in the universe and L9 re-reduced it. The recompute holds a key only when the
    member is selected.
  - Tests: `test_universe_run_either_side_lacks_disagrees` and `test_run_both_sides_hold_outside_the_universe_disagrees`.
  - At `1134bbf58`: the universe was the outputs' union.
- **RC-CMP-4's two causes on producer-shaped fixtures.** The `cmp-abba` floor lines are in the base fixture. 19 NEG-8
  references per window are selected; with NEG-8 lines on both sides.
  - Head: `exit=0 fails={}`. All 57 members are listed `compared_in:*` (`test_rc_cmp4_window_passes_and_lists_each_reference_member`).
  - At `1134bbf58`: `exit=1 fails={'routing_id': 54, 'run_phase_energy_j': 162}`. The 162 matches RC-CMP-4.
    Reproduced in the old worktree, and in place by the `old_key_set` mock.
- **Opus G7.1.**
  - Head: `exit=0 fails={}`, `compared_in exclusions listed: True`.
  - At `1134bbf58`: `exit=1 fails={'routing_id': 1, 'run_phase_energy_j': 3}`.
- **Opus G7.2** (a science run both sides omit).
  - Head: `exit=1 fails={'routing_id': 1, 'run_phase_energy_j': 3}`. The routing row is `missing_or_null` on both
    sides.
  - At `1134bbf58`: `exit=0`, `{'fail': 0, 'pass': 0}`. In place: with an output-derived universe, the run is
    compared nowhere.
- **Fable P1a, P1c, P2b.**
  - Head: P1a, the references selected, gives exit 0 and lists them. P1c, an L9 re-reduced reference, gives exit 1
    on its routing row (`test_reference_member_l9_rereduced_disagrees`). P2b, a reference dropped from a NEG-8 line,
    gives exit 2 with `count` `row_disagrees`.
  - At `1134bbf58`: P1a gave exit 1.
- **Reference dropped from a NEG-8 line still DISAGREEs** (`test_reference_member_dropped_from_a_neg8_line_still_disagrees`
  and `test_neg8_line_dropped_by_one_side_disagrees`).
  - Head: start 1 vs 2 gives `fails={'count': 1}`, `reference_counts/counts/start row_disagrees`. Deciding 11 vs 12
    gives `corpus_counts/deciding row_disagrees`. A whole line dropped gives a routing_id DISAGREE.
  - At `1134bbf58`: the same through the counts (Opus NEG8.1 and NEG8.2).
- **Restricted output lists each excluded member** with `{family, pack, run_id, role, selected, reason:
  compared_in:<family>}`.
  - Head: listed. At `1134bbf58`: absent.
- **Guards.**
  - A kept unit holding a registered reference or diagnostic member refuses `kept_units_member_not_science:<pack>`.
  - A missing kept-units record, or one built from other exclusions, is a DISAGREE on
    `run/<pack>/kept_units/exclusions_sha256` against the recompute's `inputs.<PACK>.exclusions_sha256`.
  - A selected diagnostic or unregistered member is a key, so it DISAGREEs.
  - These are new; none existed at `1134bbf58`.

### F2

- **Opus's relabel sweep** (`test_opus_relabel_sweep_never_exits_0`). Head: `relabel exit-0 count: 0`. At
  `1134bbf58`: 58.
- **Each compared categorical line relabelled into every exempt section and word.** The lines are `dominance_branch`,
  `dominance_ratio`, `sensitivity_reported`, `sensitivity_window` and `below_screen_bound`. The targets are the block
  history words, every window-line word, and the cells, floors, contrasts and fixed sentences sections.
  - Head: no exit 0 (`test_each_compared_line_relabelled_into_every_exempt_section_refuses`).
  - At `1134bbf58`: the `harvest_once` and `primary_contrast` cases gave exit 0 (probe).
- **A wrong categorical word in its own line** (`test_wrong_categorical_word_in_its_own_line_disagrees`). Head:
  exit 2, `value_differs` or `row_disagrees`, for each of:
  - branch A;
  - licensed True;
  - ratio status `refused`;
  - below True;
  - widened False;
  - p42 status `computed`;
  - p42 code changed.
  - At `1134bbf58`: licensed True and p42 status `computed` gave exit 0 (Opus probe). The in-place counterfactual
    restores the old `uncovered:` rules and gets exit 0 (`test_licensed_and_p42_words_were_exempt_at_1134bbf58`).
- **Probe "branch A under harvest_once", "licensed True under harvest_once", "status computed under
  primary_contrast".**
  - Head: `refused=line_key_unregistered:disclosure:block_lines/harvest_once/branch` (twice) and
    `refused=line_word_unregistered:disclosure:block_lines`.
  - At `1134bbf58`: all three gave exit 0.
- **No exemption takes a window-line or history subtree** (`test_no_exemption_takes_a_window_or_history_subtree`).
  - Head: enumerated. At `1134bbf58`: `block_lines/(…)/.*` and `window_lines/.*`.

### F3

- **Leave-one-out rows key only on the contrast's registered block id.**
  - Head: `TYPO-b03`, `b03`, `plan-gamma-b03` and the other contrast's `d117-prefill-p2048-contrast-b03` give
    exit ≠ 0. `d117-decode-contrast-b03` binds and gives exit 0.
  - At `1134bbf58`: the trailing-`bNN` parse routed all four to b03, giving exit 0 (in-place mock; Fable P3b and
    P3c).
- **Ratio rows key on the registered `numerator_field`.**
  - Head: an unregistered field gives exit 2, with a routing_id DISAGREE ≥ 2.
  - At `1134bbf58`: `startswith("common_mode")`.

## FILES CHANGED

- `scripts/compare_b5_recompute.py`:
  - The registry gains roles from the plan trees (`plan_roles`, `REFERENCE_INPUTS`, three new digest pins) and the
    registered contrast block ids.
  - New: `step_2_universe`, `reference_members`, `REFERENCE_FAMILIES`, `excluded_members` in the output.
  - New: `gate_lines` and `LINE_KEYS`.
  - New comparisons: the licensed boolean; ratio status; `widened`; sensitivity status, code, `equals_primary`,
    `not_below_primary` and `outcome_equals_primary`; `below`; the NEG-8 screen decision; member `plausible` and
    `battery_term_available`.
  - The broad coverage rules are replaced by enumerated ones (`HARVEST_WORDS`, `DESCRIPTIVE_STATUS`, `HAZARD`).
  - `loo_key` and `ratio_label` now read registered values.
- `tests/independent_recompute/test_comparator.py`: producer-shaped fixture additions. These are kept-units records
  per window, the recompute's `inputs.*.exclusions_sha256`, the closeout's `dominance_sentence_licensed`, and the
  ratio row's `status`. Two planted-fault expectations change: the moved branch now also moves the licensed word, and
  a moved p42 status also moves the printed status and code.
- `tests/independent_recompute/test_review_fixes.py`: two tests are adjusted (see DECISIONS).
- `tests/independent_recompute/test_input_gate.py`: two tests are adjusted (see DECISIONS).
- `tests/independent_recompute/test_rc_cmp7.py`: new, with 21 tests.
- `.codex-report/RC-CMP-7.md`: this report.

`git diff --name-only 1134bbf58` lists only WRITE_SCOPE paths.

## DECISIONS I MADE

1. **Universe source.** The science universe is L9's kept-units record (the run ids `kept_bundles` re-reduces), read
   as data. It is bound to the recompute through `exclusions_sha256`, and the sealed plan tree may not mark any of its
   runs as a reference.

   I did not require each kept run to be in the plan tree's `science/*`. The shared fixtures and Opus's probe use the
   synthetic id `run-a`, and the probe must run unchanged (see NEEDS_RULING 1).
2. **Which members are excluded.** Only NEG-8 roles (corpus; start, midpoint and end, spares included) leave the run
   family. Gamma's interior references (`diagnostic`) are compared in no family, so a selected one is a DISAGREE key.
3. **Unselected members with values.** A recompute member that is in the universe but unselected still contributes
   its values. The DISAGREE comes from the routing row, not the energies.
4. **Words compared.** I compared every claim word the recompute re-derives:
   - the licensed boolean, from the registered rule `licensed iff branch A` (`dominance_closeout`);
   - `below`, against `SCREEN_BOUND_S` copied from the producer;
   - `widened`, from the recompute's `b_sens != b_op`;
   - p42 status and code, against the registered exit's printed words `("refused", "p42_expected_unresolvable")`;
   - `equals_primary` and `not_below_primary`, re-derived from the recompute's primary and sensitivity values with
     L9's key sets;
   - `outcome_equals_primary`, NEG-8 `decision`, member `plausible` and `battery_term_available`;
   - ratio `status`, as `complete` when the recompute's ratio is finite.

   Two booleans that are true by construction (the producer refuses otherwise) are exempted by name:
   `mean_and_half_width_equal_primary` and `bound_independent_values_equal_primary`.

   Words the recompute does not re-derive are enumerated exemptions with a reason (`HARVEST_WORDS`): stored verdict,
   tripwires, attempt history, re-harvest, flag codes and hazard readings.
5. **Gate strength.** The line gate refuses:
   - an unregistered word for its section;
   - a key outside the word's producer set;
   - a keyed word whose line carries none of its keys (closes the keyless `sensitivity_boundary` relabels).

   It does not require every producer key, because several are conditional.
6. **Adjusted earlier tests** (behaviour is stronger, nothing was weakened):
   - `test_counterfactual_l9_keys_only`: its mock now keys on L9's first side only, because L9's side is now two maps.
   - `test_numeric_leaves_under_catch_alls_refuse_p12` and `test_numeric_string_under_a_word_rule_refuses_q1b_q1e`:
     these now refuse at the line gate first. The coverage-layer assertions are kept with the gate switched off. Q1b's
     counterfactual moved to an enumerated word leaf (`stored_status/status`), because no rule names `value_text_s`
     anymore.
   - `test_no_rule_takes_a_field_at_any_depth`: 1 broad numeric subtree instead of 2, because the hazard measurements
     are now enumerated.
7. **Probe adaptation.** Opus's `probe_cmp6.py` was run with one change: the `loo_parse` call to the new `loo_key`
   signature, plus a registered id. A copy of the original was used because its `ROOT` points at the review checkout.

## OPEN ISSUES

1. **The full-size synthetic window must be re-run at this head before acceptance.** It is the readiness gate. The
   real producer may print key or word variants that the line gate (`LINE_KEYS`) or the new comparisons do not
   foresee. The candidates are:
   - the conditional keys;
   - the `equals_primary` and `not_below_primary` derivations;
   - `exclusions_sha256` equality between L9's kept-units record and the recompute's hash.

   Each would over-refuse, not under-refuse.
2. **A window where both sides omit every NEG-8 line compares no reference member.** An obligation such as "a window
   with registered references must print NEG-8 lines" would fail Opus G7.1, which the brief requires to pass. I left
   this out.
3. **The comparative dominance line's `R`/`R_cm` label is still read from `text`.** The producer prints no other
   marker. A mislabel refuses (`no_row`), so this is not a small change.
4. **Words still exempt** because the recompute has no counterpart:
   - stored verdict status and conditions; tripwires; attempt-history verdicts; re-harvest accounts;
   - flag codes and hazard readings; `machine_member/removed`;
   - the fill's floor rule and resolution status words; `claim_ready_for_l2_l3`; `loo/status`;
   - descriptive-line status words (`DESCRIPTIVE_STATUS`).
5. **Fable F3 (LOW):** the record's step status is still never read (`Custody.step_ok` has no caller). It is outside
   this brief.
6. **Loo magnitude rows** key on the printed `block_number` digit string, which is the producer's numeric form (not an
   id parse). The load-correlated `values/.*` numeric subtree stays for the census, as in RC-CMP-6.

## NEEDS_RULING

1. **G7 universe.** No sealed source alone fixes the step-2 set, because it depends on each window's exclusions. I
   implemented it in `step_2_universe` from L9's kept-units record, bound by `exclusions_sha256` and checked against
   the plan tree's reference roles.

   Ruling wanted: should every kept run also be required to appear in the sealed plan tree's `science/*`? That is
   stronger, and safe on real windows, but it means moving the shared fixtures and Opus's probe off `run-a`.
2. **Reference obligation** (OPEN ISSUES 2). Should a window whose plan tree registers references be required to
   print its NEG-8 lines? That trades against Opus G7.1 as written.
