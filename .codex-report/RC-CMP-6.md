# RC-CMP-6: producer-derived input gate for the block-5 recompute comparator

**Status: DONE.** Seat RC-CMP-6, cloud, synthetic only. Brief:
`docs/process_traces/2026-10-28-recompute-meter-fit/FIX-BRIEF-3.md` (main `03ea4a6ef`). Base: lane tip `7fede8c76`.
Code head: `534159c4d` (this report's commit follows it). Interpreter `/usr/bin/python3.13`, `TMPDIR=/tmp/rccmp-tmp`.
No real block-5, block-6 or BYTES data was opened or searched. L9's producers and the sealed configs were read
from `origin/main` (the lane's copies of the sealed configs are byte-identical). No L9 code was copied into the
comparator, and the comparator imports nothing from `joulewise`.

## SUMMARY

The comparator now gates its step-11 inputs before anything reads them:

- **G1** reads the bytes once, in the producer's own format.
- **G2** reads an identity field only on the object that owns it.
- **G3** routes only by ids that the sealed v5 configs register, looked up literally.

Every round-3 witness that exited 0 at `7fede8c7` now refuses with a named code. Every consult control that L9's
writer produces is accepted. The registered comparative cell spelling `d117-df-cmp-abba-ph-*` now binds; it used to
fail with `key_unresolved`. The comparator no longer parses ids for their parts: `cell_phase`, `cell_model`,
`floor_kind`, `reported_key`, `pack_of_cell` and `tag` are removed.

Two more over-refusals of real producer output are fixed by narrow named rules (see DECISIONS):

- the integer `campaigns/*/attempt`;
- the adapter's default `characterization/verdict: null`.

The base test fixture now has the producers' shape: 24-key fill rows and `_item` disclosure lines across all nine
record sections. Suite: `Ran 282 tests in 177.456s OK (skipped=18)`. At `7fede8c7` it was 235 OK.

## G1-G6

| item | what changed (scripts/compare_b5_recompute.py unless named) | evidence after | counterfactual |
|---|---|---|---|
| G1 canonical load | A step-11 output is read with `strict_loads`. The loader refuses a repeated member (`l9_output_duplicate_key:<fill\|disclosure>`) and a NaN or Infinity token (`l9_output_nonfinite:…`). It also refuses bytes that differ from `canonical(parse)` plus the writer's tail, newline for the fill and none for the disclosure (`l9_output_not_canonical:…`). Writer flags: `sort_keys`, `(",",":")`, `ensure_ascii=False`, `allow_nan=False`, from `render_results_fill_input` and `canonical_json_bytes`. Every other input refuses a repeated member: other L9 outputs, the custody record, the recompute output, harvest meter records, the bars and the registry. | `test_input_gate.CanonicalLoadTests` (B3, B4, B5, B6, C2 pretty-printed, C3 unsorted, C4 `1E0`, missing newline, `.` escape, disclosure plus newline, duplicates in the other inputs). Consult prototype at the new head prints `refused=l9_output_duplicate_key:fill` (B3, B4), `l9_output_nonfinite:fill` (B5, B6) and `l9_output_not_canonical:fill` (C2-C4). | At `7fede8c7` B3, B5 and C2-C4 exit 0 (consult `probes.out`, re-run here byte-identical; Sol `duplicate_json_estimate_bad_first exit 0`, `duplicate_json_nan_discarded exit 0`, re-run here). In-test: `strict_loads` patched to the `7fede8c7` reader turns each case back to exit 0. |
| G2 owner-only identity | `IDENTITY_OWNERS` is a table of owning-container patterns per identity field, taken from `adapt_claim_verdicts` rows, `loo/rows`, the `_item` line containers, `removed_unit`/`stored_member_reason`, `loo_magnitude` rows, sensitivity rows and their `block_lines/*/record` copies. `IDENTITY_ATTRIBUTES` is a table of attribute exceptions; it holds one entry, a band's `pack`. `gate()` refuses an identity field in any other position, a non-string identity, or an owner that repeats an enclosing owner's field, with `identity_field_misplaced:<label>:<path>`. `leaves()` puts only owned identity fields into the binding context, so a nested scalar no longer merges over its parent's. | `OwnerIdentityTests`: B1 (Opus F1/Q3c), B2 (Sol 1), C1, shadowing, five misplaced positions, A6, and leaves-context unit tests. At the new head the prototype prints `refused=identity_field_misplaced:fill:gamma/contrasts/*/floor/contrast_id` for B1 and `…disclosure:contrasts/*/estimator/contrast_id` for B2. | At `7fede8c7` B1, B2 and C1 exit 0 (consult; Opus `Q3c … exit=0`; Sol `nested_estimator_contrast_id_redirects… exit 0`; all re-run here). In-test: switching the gate off with the `7fede8c7` context and identity rule gives exit 0 again. |
| G3 literal routing | `Registry` is built from the sealed configs' own fields, with each file pinned by sha256 (`REGISTRY_PINS`). Sources: `extraction_spec.json` ×2 (`cells[*].cell_id`, `kind`, `target_precheck_path`, condition family, workload prompt tokens for p42; `reported_energy_cells[*].cell_id`, joined to its extraction cells by member set), `analysis_manifest_v3.json` (`contrast_id`, phase, `floor_selector.condition_family_ids` in [A, B] order) and `consumer_family_declaration.json` (aggregate floor cell ids of arms A and B per phase). A routing id that is unregistered, or registered for another window, refuses with `routing_id_unregistered:<where>`. This applies in `gate()` for step 11 and in every family function for L9's other inputs: extraction cells, aggregate cells, ratio rows, verdict and sensitivity contrasts, projection cells and sensitivity cells. `binding()`, `arm` conditions, `contrast_floor_part`, p42 selection and the recompute-side window filters all read the table. A resolution's source id that the registry does not list prints no cell, so its `routing_id` row disagrees. | `RegisteredIdTests` (B7 Sol 3, suffix spellings including the lane's old `-comparative`, A7/A8 both registered spellings bound, window mismatch, unregistered pack, family inputs, unregistered source id). `RegistryTests`: the table's content; a spec edit changes the table, and the pin refuses the edited copy (`routing_registry_digest_differs`); no parsing helper or substring test remains in the script. | At `7fede8c7` B7 exits 0, and its typo'd id is labelled `routing_id` (consult B7; Sol `bad_raw_floor_cell_id_prefix exit 0`, `RAW_ID_COVERAGE routing_id`; re-run here). A8 was refused with `key_unresolved` (consult A8). With the gate off the literal lookup still leaves B7 unbound (`key_unresolved`), so there is no parse-based route left to switch back on. |
| G4 fixtures | `test_comparator.l9_files()`: verdict rows carry the producer's contrast keys with a v3 floor (arm gates and resolutions). Fill rows come from an adapter mirror (`fill_row`) with all 24 keys. The fill top level is complete (campaigns as `build_results_fill_input` writes them, gamma, characterization). The disclosure record has all 9 sections, with `_item` lines for floor_composition (registered ids), kept_units, primary_contrast, contrast_interval, decision_floor, magnitude, loo, the sensitivity block lines with `record`, dominance_ratio/branch, window structure lines and fixed sentences. The custody writer writes step-11 bytes canonically. Existing tests whose counts changed because the shape now prints more were moved to equivalent faults (DECISIONS 5). | `ProducerShapeTests`; every comparator test runs on this fixture; the meter fixture already had producer-shaped machine lines. | n/a |
| G5 exemptions | The rules the reviews named are now enumerated leaf names: `(.*/)?(positions/\*\|attempt)`, `(conditions\|metric\|equivalence)(/.*)?`, identity and text at any depth, and Sol's `point_floor_diagnostics\|single_count_discipline(/.*)?`. Also enumerated: `variance_contributions`, `neg8_allowance/values_j` (one level, `_j` names), `campaigns`, `characterization`, `finalized_manifest`, `floor_artifact` and the fixed sentences. A string spelling a number is numeric-class outside the text and identity rules (Opus F3). The restricted output adds `coverage.named_exemptions`, each named rule with the leaves it took. | `ExemptionTests` (Q5a, Q5b, Sol diagnostics subtree, no `(.*/)?` left, the census listing) and `NumericWordTests` (Q1b, Q1d, Q1e, text/identity spellings). Opus probe at the new head: Q1b and Q1e exit 2; Q1d listed. | At `7fede8c7` Q1b, Q1e, Q5a, Q5b and Sol's `named_broad_subtree=*` exit 0 (Opus `probe_structural.out`, re-run identical; Sol re-run). In-test: `numeric_word` patched off turns Q1e back to exit 0. |
| G6 witnesses | All round-1 and round-2 probe tests still run, on the producer shape. Round 3: Opus F1-F5 and Q1-Q6 and Sol 1-3, together with the consult's A1-A8, B1-B7, C1-C4 and D, are tests in `test_input_gate.py`. Opus F4: `test_structural_rules.guard_faults` adds three checks: no `while` in a family function, no `c.add` outside `Comparison`, and no family call from a helper. | `test_the_extended_guard_catches_opus_f4_and_sol_while_mutants` flags all four of Opus's appended shapes. At the new head, Opus's own probe reports `failures=1` for each. | At `7fede8c7`, Opus's `while_loop`, `helper_add` and `helper_calls_family` shapes gave `failures=0` (re-run identical). |

Verification commands:

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
  gives `Ran 282 tests in 177.456s OK (skipped=18)`.
- Probe scripts, extracted from the three review branches into throwaway worktrees at `7fede8c76` and at `534159c4d`:
  - The consult's `prototype_gate.py` and Opus's `probe_structural.py` re-run at `7fede8c76` byte-identical to their
    committed `.out` files, apart from timings.
  - Sol's `probes.py` main needs a Mac-local `.codex-bridge` baseline and `/private/tmp`. I ran its attack sections
    in-process with only TMPDIR redirected.
  - At the fixed head every witness prints a refusal. Opus's script stops at Q3c and Sol's at its next assertion,
    because each expects the old exit 0 or a `coverage` key that a refusal does not write. The cases after those
    stops are the tests named above.

## FILES CHANGED

- `scripts/compare_b5_recompute.py`: loaders, `Registry`, `gate`, owner-only `leaves`, registry `binding`,
  family-function lookups, enumerated `COVERAGE`, numeric words, `named_exemptions`, `routing_registry_sha256` in the
  restricted output.
- `tests/independent_recompute/test_comparator.py`: producer-shaped fixture, canonical writer, `RULES = cmp.COVERAGE`,
  three tests moved to equivalent faults.
- `tests/independent_recompute/test_review_fixes.py`, `test_structural_rules.py`: adapted to the producer shape and
  to the earlier refusals; the AST guard is extended.
- `tests/independent_recompute/test_input_gate.py` (new).
- `.codex-report/RC-CMP-6.md`.

## DECISIONS I MADE

1. **Aggregate floor cell ids come from `consumer_family_declaration.json`.** The brief lists only the extraction
   specs and the manifest, but `d117-<model>-<phase>-floor-v5` (the aggregate, ratio and sensitivity floor cells and
   the resolution sources) is in neither. The declaration sits in the same sealed contrast campaign, and its plan tree
   binds it by the same sha256 I pin. Without it, those ids could only be parsed, which G3 forbids.
2. **Reported cell to recompute cell id is a join, not a spelling rule.** A reported cell's recompute id is the
   condition family of the extraction cells whose members it contains. It is unique in both specs.
3. **A p42 cell is defined from the spec: target phase prefill and a 42-token workload.** The old rule was
   `"p42" in id`.
4. **Only ids that route are refused at the gate.** A printed `condition_family_id` and a printed `source_cell_ids`
   entry are compared attributes (RC-CMP-5 S2). An unregistered one makes its `routing_id` row disagree rather than
   refusing at load.
5. **Test changes kept each test's intent.**
   - The RC-CMP-5 nonfinite tests now expect the earlier `l9_output_nonfinite:fill` refusal, not
     `step11_nonfinite_value`.
   - Three tests that unregistered ids now refuse at the gate assert that refusal: `ctr-unknown`, the L9-only extra
     contrast, and Sol's `d117-qwen3-1p7b-decode` condition probe is unchanged.
   - The planted floor-gate fault moved to L9's aggregate cell, because the recompute cell also feeds the
     resolutions.
   - The stdout test uses a run energy, because D is now printed in step 11.
   - Fixture helpers keep the producer copies in step (`set_estimate`; `v3_floor` updates `decision_floor` and
     `minted_j`).
6. **Opus F3 (numbers written as strings) is in scope.** G6 asks every round-3 witness to refuse. The text and the
   enumerated identity rules still take numeric spellings, because block numbers, short pins and ids can be digits.
   Every other rule refuses them.
7. **Two producer over-refusals are fixed by enumerated named rules.** `fill:campaigns/(alpha|beta)/attempt` is now
   identity-number, and `fill:characterization/verdict` is a named null. `7fede8c7` refused both on any real fill.
   No bar changed.

## OPEN ISSUES

1. **Two numeric subtrees are still broad.** They are `load_correlated_*/values/.*` and `(arm_hazards|battery_phase)/measurements/.*`.
   No review named them. `ExemptionTests` pins their count at 2, and `named_exemptions` lists every leaf they take,
   so the full-size census can enumerate them.
2. **The full-size synthetic comparison at the new head has not been run.** It is the readiness gate (consult
   item 8). In its restricted output, `coverage.unmapped`, `coverage.unbound`, `coverage.nonfinite` and
   `absent_sources` should be empty and `named_exemptions` should be reviewed.
3. **Two id parses remain, outside G3's list.** `loo_key` and `block_key` still parse leave-one-out block ids. The
   dominance-ratio `R`/`R_cm` label is still read from the line's text (RC-CMP-5 open issue 2). Both are compared
   through union `routing_id` rows.
4. **Opus Q6 / consult A5 is unchanged.** A refused v3 arm gate printed as null on both sides still refuses with
   `row_disagrees`. That needs a ruling, not a gate change.
5. **Some witnesses are out of the AST guard's reach.** A helper that silently drops one side (Sol's
   `selected_runs → {}`) cannot be caught by the AST guard. The projection-p42 row is still compared only when L9
   lists refused cells (Sol answer 2; other p42 rows remain). Completeness of the fill (Opus Q2d/Q2e) belongs to L9's
   fill validator.
6. **No L9-side census tests were added.** The consult's owner-table and exemption census tests in `tests/b5_analysis`
   are outside WRITE_SCOPE.

## NEEDS_RULING

None blocking. The ruling on open issue 4 is still the lead's.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| comparator suite | yes | no | no | 282 OK |
| round-3 witnesses as tests | yes | yes (B1, B2, B3, B5, B7, Q1b, Q1e, Q5a/b exit 0 at `7fede8c7`) | no | `test_input_gate.py` and the re-runs above |
| producer-shaped fixture | yes | no | yes (two producer over-refusals: campaign attempt, characterization verdict) | DECISIONS 7 |
