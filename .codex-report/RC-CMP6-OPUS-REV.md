VERDICT: REJECT

# RC-CMP6-OPUS-REV: delta review of RC-CMP-6 (7fede8c7..1134bbf58)

This is one of two parallel blocking delta reviews (gate policy rule 3). Branch: `review/2026-10-29-rc-cmp6-opus-rev`,
cut from `1134bbf58`. I used synthetic fixtures only; no real block-5, block-6 or BYTES data was opened or searched for.
Interpreter: `/usr/bin/python3.13`, with `TMPDIR=/tmp/rcopus_tmp`.

**Why REJECT.** The input gate (G1-G3) holds: every earlier witness refuses, and I found no exit 0 with a wrong
printed *number*. But Amendment 1's G7 was not implemented. RC-CMP-4's first cause still fails a sound producer-shaped
window (finding 1). That makes the comparator unusable on the real window, so the brief's acceptance is not met.
The fix scope is G7 alone. Finding 2 should ride the same round.

## Suite

`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 282 tests in 153.875s` / `OK (skipped=18)` / exit 0 (`rc-cmp6-opus-rev/suite.out`).

## Findings, ranked

1. **BLOCKING: G7 is absent.** The key universe of `run_phase_energy_j` is still built from the two outputs.
   - `scripts/compare_b5_recompute.py:582-612`: `compare_runs` pairs `rereduced_names(custody)` with
     `selected_runs(members)`. The second one takes any member whose `selected` is true, or which has no `selected`
     field at all.
   - The code has no role table, no `compared_in:<family>` listing, and no G7 test. `.codex-report/RC-CMP-6.md`
     never mentions G7. It cites the brief at `03ea4a6ef`; Amendment 1 (`8fbe1b397`) landed a minute before
     milestone 1.
   - Executed (`probe_cmp6.out`):
     - **G7.1**: RC-CMP-4 cause 1 on the producer shape. The recompute marks `neg8-refcorpus-r01`
       (`role: reference`) selected, as `independent_recompute_b5.py:2814` does, and L9 re-reduces science runs
       only. Result: `exit=1 fails={'routing_id': 1, 'run_phase_energy_j': 3}`, and `compared_in exclusions listed:
       False`.
     - **G7.2**: the converse. A science run that both sides omit (no rereduced file, `selected: False`) is
       compared nowhere: `exit=0`, `run_phase_energy_j counts: {'fail': 0, 'pass': 0}`. This is the
       universe-from-output defect that G7 names.
   - Fix: take the per-window science and reference member sets from a registered table. Apply the same set to
     both sides, so a registered science run that either side lacks is DISAGREE. Also list each excluded member as
     `compared_in:neg8_allowance|reference_counts|corpus_counts`.

2. **MEDIUM (pre-existing, not a regression): a wrong categorical word can pass with exit 0.** The cause is the line
   word, a value read from the checked document, which routes the leaf's path.
   - `step()` (`:232-235`) builds the path component from the item's own `line` value.
   - Two broad string/boolean subtrees remain: `block_lines/(superseded_history|attempt_count|attempt_history|g10|harvest_once|reharvest_account)/.*`
     (`:1546`) and `disclosure:window_lines/.*` (`:1512`).
   - Relabelling a compared line into one of them moves its words out from under the comparison.
   - Executed:
     - control: `dominance_branch` printed `branch: "A"` refuses (`value_differs`);
     - the same line with `line: "harvest_once"` gives `exit=0 fails={}`;
     - so does `dominance_sentence_licensed: True` under `harvest_once`.
   - Across all relabels of the fixture's lines, 58 exit 0. None of them carries a number, because the `uncovered:`
     rules deny numbers and numeric spellings.
   - The same rule is present at `7fede8c7` (`:1294` there).
   - Fix (either works):
     - enumerate those subtrees' leaf names, as G5 did for the others;
     - or admit a line word only in the section L9 writes it to, with its producer key set.

3. **LOW: some id parses and text reads remain (RC-CMP-6 open issue 3).**
   - `loo_key` (`:746-749`) parses the omitted block id: `loo_key('b03-b07') = 'b07'`.
   - The `R`/`R_cm` label is read from `text` (`:1617`). A mislabel refuses (`no_row` on every ratio leaf), and I
     found no exit 0 through it.
   - The ratio-table label reads `numerator_field.startswith("common_mode")` (`:688`). A mislabel there yields a
     DISAGREE against the recompute, not an exit 0.
   - None of these yields a wrong printed number. They should still move onto registered block ids (the verdict's
     `planned_block_ids`) when G7 lands.

4. **LOW: the earlier probe scripts no longer run to completion at the new head.**
   - Opus `probe_structural.py` stops at Q3c (`KeyError: 'coverage'` after the refusal). Sol `probes.py` sections
     stop at the first refusal, and its duplicate witnesses assume non-canonical spacing.
   - I re-ran Sol's duplicates with the canonical spelling (finding 4's commands are in `run_sol_duplicates.py`).
   - Q4-Q6 and the Sol cases after each stop are verified only through `test_input_gate.py`, which passes.

## Answers

1. **Earlier witnesses: yes, every one refuses.**
   - The consult's B1-B7 and C1-C4 refuse with the named codes:
     - `identity_field_misplaced:fill:gamma/contrasts/*/floor/contrast_id`;
     - `…disclosure:contrasts/*/estimator/contrast_id`;
     - `l9_output_duplicate_key:fill`, `l9_output_nonfinite:fill`, `l9_output_not_canonical:fill`;
     - `routing_id_unregistered:disclosure:floors/*/cell_id`.

     Source: `consult_prototype_at_1134bbf58.out`, lines "comparator alone". The prototype's own gate now mismatches
     on the new fixture's `block_lines/*/record`; that is expected.
   - Opus Q1b, Q1e and Q3c refuse. Q1d is listed, and the AST mutants give `failures=1` each.
   - Sol: `duplicate_json_estimate_bad_first`, `bad_last` and `nan_discarded` all exit 2. The nested
     `contrast_id`, `bad_raw_floor_cell_id` and `_prefix`, and the `named_broad_subtree` diagnostics refuse.
   - Rounds 1-2 are covered by the passing suite.
   - **Consult controls:**
     - A1-A4, A7 and A8 pass with exit 0; A8 is the registered `cmp-abba` spelling.
     - A5 still refuses `row_disagrees`. That is a ruling (RC-CMP-6 open issue 4) and still unmade.
     - A6 refuses only for want of a meter record, as the consult expected.
   - Still exit 0, and none of them a wrong printed number:
     - Opus Q2d/Q2e and Sol `projection_p42_omitted` (completeness; open issue 5);
     - Sol's AST mutants `one_sided_while` and `helper_drops_all_selected_runs` (open issue 5).

2. **Exit 0 with a wrong printed number: none found. A wrong printed categorical word: yes (finding 2).**
   - **Value-derived routes:** the line word (finding 2), plus the low-risk parses in finding 3. Identity routing
     itself is owner-only: `leaves()` at `:1566-1572` admits only `owns()` fields, and the gate refuses misplaced or
     shadowing ids (`:509-539`).
   - **Identity off its owner:** refused.
   - **Id table:** built only from the four pinned sealed files (`:363-367`, `:416-424`).
   - **Canonical-bytes check:**
     - It applies to the two step-11 outputs. A different writer's bytes refuse unless they equal canonical bytes.
     - Other L9 inputs are not canonical-checked, but each of their values must AGREE with the recompute before a
       printed leaf can bind to it, so another writer there yields DISAGREE, not exit 0.

3. **G7: no.**
   - Families take their universe from the outputs, not from a role table (finding 1), and no `compared_in` listing
     exists.
   - In the NEG-8 families, a reference member dropped on one side does still DISAGREE through the counts:
     - `NEG8.1` (start 1 vs 2) gives `fails={'count': 1}`;
     - `NEG8.2` (deciding 11 vs 12) gives `fails={'count': 1}`;
     - the control `NEG8.0` passes with exit 0.

     This works because the NEG-8 lines compare counts and means. The members themselves are not compared, and
     there is no registered member list.

4. **Over-refusal: only cause 2 is fixed.**
   - **cmp-abba:** fixed. A8 and the base fixture bind the registered spelling with exit 0.
   - **NEG-8 reference rows:** NOT fixed (G7.1, exit 1). Every real window has NEG-8 references, so RC-CMP-4's
     window would still fail.
   - Other likely refusals of a sound real window:
     - A5: a refused arm gate printed null on both sides (needs the ruling).
     - `IDENTITY_OWNERS` is hand-listed from fixtures. Any real line that carries an identity field in a position
       the table omits refuses `identity_field_misplaced`. Only the full-size synthetic run (RC-CMP-6 open issue 2)
       can show this.
     - Sol's `CLEAN_MODEL_ALIAS` gives `Qwen3-1.7B-4bit` → `rho: 16, routing_id: 4` if the producer spells the
       model in full in machine lines.

   Re-run RC-CMP-4's full-size synthetic window after the G7 fix, before any acceptance.

## Evidence files (`.codex-report/rc-cmp6-opus-rev/`)

- `probe_cmp6.py` and `probe_cmp6.out`: G7, the relabel sweep, the text label, the loo parse and NEG-8.
- `consult_prototype_at_1134bbf58.out`, `opus_rev3_probe_at_1134bbf58.out` and `sol_rev3_probes_at_1134bbf58.out`:
  the earlier probes, copied verbatim. For the Sol run, only the hard-coded `/private/tmp/jwrc3-tmp` was redirected,
  and its duplicate witnesses were re-spelled canonically (`run_sol_*.py`).
- `suite.out`.
