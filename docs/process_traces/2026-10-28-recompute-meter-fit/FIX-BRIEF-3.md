BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "RC-CMP-6: producer-derived input gate in front of the block-5 recompute comparator",
 "OBJECTIVE": "Make the comparator's exit 0 mean that every printed step-11 number agrees, by gating its inputs on L9's own writer and L9's registered ids, as designed in the Fable consult; close the round-3 witnesses and the registered-spelling over-refusal together.",
 "AUTHORITY": [
   "RUN_STATE.md items 96, 97, 98, 99 (lead adopts the Fable consult under Ed's instruction to consult Fable instead of waiting)",
   "review/2026-10-29-rc-cmp-fable-consult .codex-report/RC-CMP-FABLE-CONSULT.md (6434f25b3): the design, invariants I1-I3, the prototype .codex-report/rc-cmp-fable-consult/prototype_gate.py and probes.out",
   "review/2026-10-29-rc-cmp-opus-rev-3 (5ce14b43e) and review/2026-10-29-rc-cmp-sol-rev-3 (038548089): the round-3 witnesses",
   "docs/process/gate_policy.md (binding)",
   "this brief"],
 "WRITE_SCOPE": [
   "scripts/compare_b5_recompute.py",
   "tests/independent_recompute/**",
   ".codex-report/RC-CMP-6.md"],
 "BASE_HEAD": "tip of lane/2026-10-27-recompute-comparator (7fede8c7 at writing)",
 "ACCEPTANCE": [
   "G1 canonical-bytes load: every L9 step-11 input (fill input, disclosure record) is refused unless its bytes equal the canonical serialisation of its own strict parse, using the producer's flags exactly (results_fill_adapter render_results_fill_input: sort_keys, separators (',',':'), ensure_ascii False, allow_nan False, trailing newline; calibration_ledger canonical_json_bytes: the same flags, no newline); the strict parse refuses duplicate object keys and nonfinite tokens; refusal codes l9_output_duplicate_key, l9_output_nonfinite, l9_output_not_canonical; the recompute output and meter records also load with duplicate keys refused",
   "G2 owner-only identity: an identity field (contrast_id, cell_id, pack, run_id, model, omitted_block_id and the others the consult's table lists) is admitted only on the object it names, by an explicit table of owning container patterns taken from the producers (results_fill_adapter adapt_claim_verdicts rows; disclosures _item lines and their containers); anywhere else refuses identity_field_misplaced; leaves() no longer merges nested scalar identities over a parent's",
   "G3 literal routing: every binding routes by ids taken literally from the sealed configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/extraction_spec.json (cells[*].cell_id, kind; reported_energy_cells[*].cell_id) and configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json (contrasts[*].contrast_id, floor_selector condition_family_ids in [A, B] order); no substring parsing of ids (remove cell_phase, cell_model and floor_kind parsing from routing); an id not in the registered set refuses routing_id_unregistered; the registered comparative spelling d117-df-cmp-abba-ph-decode-* resolves",
   "G4 fixtures: producer-shaped fill and disclosure fixtures (the full key sets the producers write, for example 24 keys per fill contrast row) replace the reduced ones wherever the gate would refuse them; every existing test still runs against producer shape",
   "G5 exemptions narrowed: the broad patterns the reviews named ((.*/)?(positions/\\*|attempt), (conditions|metric|equivalence)(/.*)?, identity at any depth) become enumerated leaf names; the list of named numeric exemptions is printed in the restricted output so the full-size run can census it",
   "G6 every witness of rounds 1-3 and every probe of the Fable consult (A-D) is a regression test; the round-3 witnesses fail at 7fede8c7 (counterfactual recorded) and refuse after; the consult's 8 controls are accepted; tests/independent_recompute passes; no file outside WRITE_SCOPE; no import of joulewise.b5_analysis or joulewise.external in the scripts (reading the sealed config files as data is allowed)"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .",
   "the round-3 reviews' probe files and the consult's probes print refusals at the fixed head"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# RC-CMP-6 brief

**Amendment 1 (lead, 2026-10-29 ~06:00 UTC; RUN_STATE item 101), G7.** RC-CMP-4 (`report/2026-10-28-rc-cmp-4`
`de637d4e`) ran the full-size synthetic window at `e5ccf720b`: L9 completed with every step ok and no value
disagrees, but the comparator refuses for two comparator-side reasons. One is the `cmp-abba` spelling, closed by
G3. The other is 162 `run_phase_energy_j` rows that are `missing_or_null` on L9's side: the recompute marks NEG-8
reference members (refcorpus, window-start, midpoint, window-end) as selected, but L9's step 2 re-reduces only
science runs. **G7:** each family's key universe comes from the registered role table, applied identically to both
sides, never from either side's output. For `run_phase_energy_j` that universe is the science runs L9's step 2
re-reduces. Reference members are compared through the NEG-8 families. A reference member that one side omits from
its NEG-8 computations is still DISAGREE there. The restricted output lists the members excluded from each family,
with the reason `compared_in:<family>`. Regression: RC-CMP-4's two causes, reproduced on producer-shaped fixtures,
refuse at `7fede8c7` and pass after; a reference member dropped from a NEG-8 line still DISAGREEs.

**Why.** Three review rounds found the same defect: the comparator decided where a printed number belongs from
something the checked document asserts about itself. The Fable consult (adopted, RUN_STATE item 99) closes it at the
input: one unique reading of the bytes, identity only where it belongs, routing only by registered ids. Its
prototype refused every round-3 witness and accepted every control. A full per-field type schema of the disclosure
record is deferred to after the block-5 release (consult section 2), because 70 conditional line kinds would
over-refuse sound windows.

**Rules.** Synthetic data only; never open real block-5/6/BYTES data. No bar widened; no change to the recompute's
arithmetic. Push only to lane/2026-10-27-recompute-comparator; no force push, no merge to main, no PR. Push the
report after each milestone. After this job the lead runs one delta round: Sol 6.1 xhigh fast and Opus, together.
If a fourth recurrence arrives through a value-derived route, the consult's fallback (a recompute-driven walk over
exact paths) is the next step, not another patch.

**Report.** .codex-report/RC-CMP-6.md: SUMMARY, the G1-G6 table with evidence and counterfactuals, FILES CHANGED,
DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
