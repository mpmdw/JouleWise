# 09/20 — Cold Fable gate ruling, A292-REDUCER-DESIGN-01

Judge: Claude Fable 5.1, fresh session, 2026-09-25 05:19–≈05:50 PDT, worktree HEAD `307d2298`. Read-only except this file.

## 0. Custody

- **Validator.** Run 1 with charter sha `…95d82` (the deliberate typo): `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2 with `…95d81`: `PASS`, rc 0, all six exhibits matched their manifest digests (`coldgate-validator-receipt/v2`). Method: `scripts/validate_gate_packet.py` plus an independent `shasum -a 256` of the charter (`099de884…5d81`) and the charge (`99d9cbdd…5858`). Expected = observed on both.
- **Auto-loaded before I chose anything:** `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the harness-injected memory index. None was used for this ruling. I read only the packet, the charge's listed ruling lines, and the five named code files plus `tests/test_scored_packer.py:316-342` and `tests/scored_case_generator.py`.
- **Charter §9 pattern check.** This is a design consult, not a fix round; no same-signature failure history is in the packet. No presumption either way.

## D1 — Splits S1–S13

Deciding evidence is what I read, not the seats' paraphrase.

- **S1 — AMEND.** Windows carry the **in-force** digest (P-S1 affirmed for windows). Rows carry the **final** `roster["sha256"]`. Evidence: events are strictly index-ordered and every loaded envelope is reported (`scored_packer.py:226-227,494`), so `in_force(ix)` = `registered_sha256` replaced in turn by `events[k]["sha256"]` for every `k` with `events[k]["envelope_index"] < ix` is well defined and is the roster the runner must have held under FT-9 (15/21:74). A window stamped live with that digest is the only reducer-checkable evidence of FT-9. The scorer runs over the finished roster; an in-force stamp on a row would be recomputed from that same roster and evidences nothing, while a final stamp catches a scorer run on a stale roster. Runner-lane CARRIED row: each envelope's raw capture bundle records the loaded roster digest, and the window producer copies it.
- **S2 — AFFIRM P-S2** (derive, do not copy). Every copy would be derived from the same roster, so it is not an independent check; each copy is one more field to cross-check and refuse. K3's "parsed text is kept" (07d:544) is satisfied by `extracted_answer` on the row and item record.
- **S3 — AMEND P-S3.** Row `stop_reason` is the closed set `{"stop", "length"}`; any other value refuses `row_domain`. The rule `(stop_reason == "length") == capped` is K3 (07d:546-549). The runner's own vocabulary (`mlx_runtime.py:568,590,611,624`: `runtime_failed`, `malformed`, raw `stop_condition`, `length`) is mapped by the scorer lane, not enumerated by the reducer; a reducer constant "pinned against the runner's emit sites" is a cross-module AST coupling with no ruled basis. P-S3's last bullet ("runtime failures are scored outcomes of their placement") is a NEW science rule: it would count a runner fault as an incorrect answer in a cell's accuracy and energy. AP-5M v4 has no such outcome. Struck; a runtime-failed item refuses the reduction loudly (`row_domain`) until HEADLINE-AP5M-AMENDMENT-01 types it.
- **S4 — AFFIRM P-S4**, with one addition: superseded rows pass every row check (keys, domain, scorer, binding, duplicate, cap agreement) before pass-through; only counting is exempt. K24 "recorded and never used" (07d:196) is met by verbatim pass-through. See D2 for `attempt_divergence`.
- **S5 — AFFIRM P-S5.** `ReductionRefusal(ValueError)`; a subclass of `PackingRefusal` would let a re-run A291 witness asserting only the class pass on the wrong refusal.
- **S6 — AMEND P-S6.** One uncounted-window ledger (`uncounted_windows`, reason `voided` or `terminal`) instead of a separate `terminal_windows`; item records reference the key and never copy `gross_j`. Exact schema in D4.
- **S7 — AFFIRM P-S7** (missing live window refuses, `missing_live_window`). The partition rule is ruled (kernel:3832); `window_missing` is not a terminal type (89:417) and is absent from AP-5M's NR list (07d:286). 45/21:58's causes are all roster events, not lost captures. Consequence, stated so the harness does not miss it: under this rule `counted_keys` always equals the live placement set, so `spread_exceeded` can only arise from terminals; the packer's partial-parent witness (`tests/test_scored_packer.py:337` removes a live key) refuses at `reduce` and is replaced by a terminal-degradation fixture (S13).
- **S8 — AFFIRM P-S8.** 45/10:79 reads "is accepted", conditional. Generalised: a window for either terminal type is optional; if supplied it is bound, checked and ledgered; a `not_started` terminal may not have one (`window_unstarted`).
- **S9 — WRITE DIFFERENT TEXT: refuse `row_tokens_over_cap`.** The MLX runner stops at the requested budget (`mlx_runtime.py:622-624`), so `generated_tokens > cap_tokens[arm]` means the generation did not run under the registered cap. That is an evidence-integrity refusal of the same class as a digest mismatch, not a science rule; 07d:549's `≥` defines "capped", it does not license runs above the cap. The magistrate's diagnostic count would let a mis-configured runner's rows into cells.
- **S10 — AFFIRM P-S10** (`cap_bound: null` at zero counted rows).
- **S11 — AFFIRM P-S11** (no level status in A292). 45/21:60, 15/10:39, 07d:286 place precedence in the estimator. A292 emits per-cell counts of both terminal types so FT-5 (15/21:66) has its input.
- **S12 — AFFIRM P-S12** (assert a `PackingRefusal` is raised, record its code, never assert `inv_12`). My reading of `scored_packer.py:453,488` agrees with Opus's P4: replay regenerates singles, so a forged `predicted_item_s` fails `inv_38` today and would fail `inv_12` only if the reconcile lane adds the clause to the seal.
- **S13 — AFFIRM P-S13 with fixes.** Oracle path fixed as `tests/scored_reduce_checker.py`. The differential test cannot use "0–25 % seeded live-window drops" as its main body under S7 (every drop refuses); D4 gives the replacement.

## D2 — Single-seat defects, `internal_disagreement`, deferred list

- **Defect 1 (Astra, terminal energy repeated) — AFFIRM.** `scored_packer.py:448-449` writes one terminal record per item of the block under one `(block_id, attempt)`; an initial multi-item block that is `cut_off` with no culprit reaches `unattributed_overrun` (`:433-437`) and has a window. Cure per S6.
- **Defect 2 (Opus, INV-13) — AFFIRM on the output side.** 08:13 and 89:491 say item rows carry `retry_stage` and it flows into cells. Under S2 the input row does not carry it; the output item record carries the counted placement's `stage` and each cell carries `retry_stage_counts`. That satisfies "flows into cells", which is the invariant's purpose; a copy on the input row would only add a cross-check of a roster field against itself.
- **Defect 3 (K3 `stop_reason`) — AFFIRM**, enforced per S3.
- **Opus's `internal_disagreement` — AFFIRM.** It is a fail-closed consistency check between two implementations of the same ruled predicate (the reducer's parent counts and `executed_status`), not a science rule. Witness by exit injection (patch `executed_status` to flip one cell).
- **Deferred list — AMEND.** `attempt_divergence` (K24, 07d:196) was deferred as needing a registration key. It needs none: it is a per-item bool, true iff the counted row's derived `correct` differs from any superseded row's for the same `(model, item_id)`. It is ruled v4 disclosure text and costs ten lines; implement it now. `below_floor`, `night_exhausted`, per-night levers and recapture stay deferred (they need `floor_gate_j`, `max_envelopes_per_night` and K25, which the seal refuses, 07d:810,1324-1325). `mean_envelope_index` stays out (R6-1 is unratified, 117:63).
- **Must anything deferred be decided before A292 is claim-bearing?** Yes, one item. AP-5M v4 step "Floor gate" (07d:266) refuses any block window at or below `floor_gate_j`; a registered-mode claim computed without it is not an AP-5M v4 reduction. A292 v1 is complete for pilot mode and for the counted/terminal partition; the registered-mode claim path requires `floor_gate_j` + `below_floor` to land through HEADLINE-AP5M-AMENDMENT-01 as reduction schema v2. The output carries `schema` v1 so A293 can refuse to consume it for a registered claim. `night_exhausted` and recapture are packer-side and gate the registered arm, not this reducer.

## D3 — What all three seats and the synthesis missed

Every "Agreed by all three" item checked against its source; all hold (15/10:47; 45/10:59; kernel:3832; 15/21:78; `scored_packer.py:494`; 07d:549,553; `scored_registration.py:25`; 89:393-398; `scored_packer.py:152-157`; kernel:3861). Misses:

1. **The cap-bound denominator is settled by K24, and the synthesis cites the wrong line for it.** "More than 20 % capped attempts" (07d:251,553) names attempts; K24 (07d:196) makes only the counted attempt's values usable "in every computation", so the denominator is counted rows. Cite K24 in the harness docstring. NIT.
2. **Float equality at the boundary.** `k/n > 0.20` is safe only because IEEE division is correctly rounded, so `2/10`, `1/5`, `3/15` all equal the literal. `CAP_BOUND_FRACTION * n` is not safe. Rule the division form and witness `1/5`, `2/10`, `3/15` false and `2/5`, `3/10`, `4/15` true. NIT, but a mutant `>=` must die at all three.
3. **Runtime-failed items have no v4 outcome** (see S3). Every seat either refused silently by vocabulary (Astra, Opus) or admitted them (Sol); the synthesis made them scored outcomes. MATERIAL, routed to the AP-5M amendment.
4. **`late` is not disclosed.** A completed-late initial block is `keep` with `late: true` (`scored_packer.py:439`) and is counted; nothing surfaces it. Item records carry `late` (derived). NIT.
5. **Double replay.** `executed_status` calls `verify_executed_roster` again (`scored_packer.py:498`); the reducer replays twice. Cost only; do not "optimise" by bypassing. NIT.
6. **Whole-block retry windows.** A parent's `whole_block` attempt is the same `block_id` with `attempt+1` in a fresh envelope alone (15/10:25); its window is the counted one for every item. No seat named the fixture; the harness needs it. NIT.

## D4 — A292 reducer rulings (final texts)

Reference digests: registration `registration.digest`; final roster digest `roster["sha256"]`; in-force digest as defined in S1. Wire conventions: `S` nonempty str; `H` 64 lowercase hex; `I` int ≥ 0 with `type(v) is int`; `N` finite number, `type(v) in (int, float)`; `B` bool; `?` nullable, never omitted; exact key sets; no unknown keys, defaults or coercion.

```text
ENTRY
reduce(registration, roster, predicted_decode_s, score_rows, capture_windows) -> dict
Five positional parameters, no defaults. First statement (AST-asserted):
verify_executed_roster(registration, roster, predicted_decode_s).
PackingRefusal from it, or from executed_status, propagates unchanged.
Pure: no argument is mutated. Module: joulewise/scored_reduce.py.
CAP_BOUND_FRACTION is imported by name from joulewise.scored_registration;
no numeric literal 0.2/0.20 appears in scored_reduce.py.

SCORE ROW  schema "joulewise.scored_row.v1"
schema; registration_sha256 H (== registration.digest);
roster_sha256 H (== roster["sha256"], the FINAL digest);
scorer_id S (== registration.scorer_id); block_id S; attempt I; item_id S;
prompt_tokens I; generated_tokens I; stop_reason "stop"|"length";
extracted_answer S?; scorer_match B.  Coherence: scorer_match => extracted_answer is not null.
Key = (block_id, attempt) must be a roster placement; item_id must be in that block's items.

CAPTURE WINDOW  schema "joulewise.scored_window.v1"
schema; registration_sha256 H (== registration.digest);
roster_sha256 H (== in_force(placement.envelope_index));
block_id S; attempt I; envelope_index I (== placement.envelope_index);
gross_j N, > 0; bundle_sha256 H (carried to output, not verified here).
Key = (block_id, attempt) must be a roster placement.

CLASSIFICATION of a placement key (precedence):
live      : block_id in envelopes[envelope_index]["blocks"]
terminal  : (block_id, attempt) equals a terminal_refusals entry's (block_id, attempt)
voided    : otherwise
observation(key) = entry of envelopes[envelope_index]["observations"] with that block_id.

REFUSAL CLASS  class ReductionRefusal(ValueError) with .code; REDUCTION_CODES exactly:
reduce_input            score_rows or capture_windows is not a list
window_keys             window key set != schema
window_domain           type/domain/schema literal failure (incl. gross_j <= 0, nonfinite, bool)
window_unknown          key is not a placement (idle_slot keys are never placements)
window_binding          registration_sha256 or roster_sha256 mismatch (in-force)
window_duplicate        repeated (block_id, attempt)
window_envelope         envelope_index != placement.envelope_index
window_unstarted        observation(key).status == "not_started"
missing_live_window     a live placement has no window
row_keys                row key set != schema
row_domain              type/domain failure, incl. stop_reason not in {"stop","length"}, coherence
row_scorer              scorer_id != registration.scorer_id
row_unknown             key not a placement, or item_id not in that block
row_binding             registration_sha256 or roster_sha256 (final) mismatch
row_duplicate           repeated (block_id, attempt, item_id)
row_unstarted           observation(key).status == "not_started"
row_missing             a live placement lacks a row for one of its items
row_tokens_over_cap     generated_tokens > registration.cap_tokens[registration.arm]
row_cap_disagreement    (stop_reason == "length") != (generated_tokens >= cap_tokens[arm])
internal_disagreement   reducer's own spread counts disagree with executed_status
A test asserts REDUCTION_CODES is disjoint from every code literal in scored_packer.py
and scored_registration.py. Terminal types are record fields, never codes.

CHECK ORDER (first failure wins; within a phase, input list order)
1 verifier  2 reduce_input  3 windows: keys, domain, unknown, binding, duplicate, envelope,
unstarted  4 rows: keys, domain, scorer, unknown, binding, duplicate, unstarted,
tokens_over_cap, cap_disagreement (ALL rows, superseded included)  5 completeness:
missing_live_window then row_missing  6 executed_status(registration, roster,
predicted_decode_s, frozenset(live keys))  7 internal_disagreement.

COMPLETENESS
live key      : window REQUIRED; one row per item REQUIRED
voided key    : window optional -> uncounted_windows reason "voided"; rows optional -> superseded_rows
terminal key  : window optional -> uncounted_windows reason "terminal"; rows optional -> superseded_rows
not_started   : window forbidden (window_unstarted); rows forbidden (row_unstarted)
Only live windows enter g_j, gross_j, positions and counts. Block energy is summed once per
counted window (math.fsum, placement order), never once per item.

CAP (sealed AP-5M v4 only; no parameter, flag, env var or registration field selects semantics)
cap     = registration.cap_tokens[registration.arm]
capped  = generated_tokens >= cap            (cap-1 false, cap true, cap+1 refuses)
malformed = extracted_answer is None
correct = scorer_match and not capped         (K3: capped is never correct)
cell.cap_bound = null if n_counted == 0 else (n_capped / n_counted) > CAP_BOUND_FRACTION
Boundaries: 1/5, 2/10, 3/15 -> false; 2/5, 3/10, 4/15 -> true; patching
joulewise.scored_reduce.CAP_BOUND_FRACTION to 0.25 flips 3/10 to false (CONSUMED witness).
attempt_divergence(item) = counted correct != derived correct of any superseded row of the
same (model, item_id); false when no superseded row exists.

EXECUTED STATUS (merged shape affirmed as ruled for A292)
executed_status output copied verbatim: spread_exceeded {ten cells}, executed_drift_lever_slots
{"1".."5": N?}, drift_exceeded {"1".."5": B}. Spread is per CELL, drift per LEVEL (89:788 loses).
Reducer recomputes per cell: fully_counted_parents (every item has a counted window),
distinct_envelopes (over those parents' counted windows) and refuses internal_disagreement unless
spread_exceeded[cell] == (fully_counted_parents < 5 or distinct_envelopes < 5) for all ten cells.
Parent position = item-weighted mean of counted windows' envelope indices; partly counted parents
contribute; lever null when either model has zero fully counted parents; drift false when lever or
max_gap is null; equality to max_gap does not exceed. No level status, no NE/NR, no ratios beyond
cap_bound; precedence is A293's.

OUTPUT  schema "joulewise.scored_reduction.v1"; exact keys:
schema; registration_sha256; roster_sha256 (final); registered_sha256; scorer_id;
mode (registration.mode); claim_ready (roster); items; parents; cells; levels;
counted_windows; uncounted_windows; terminal_refusals; superseded_rows; executed_status; sha256.
items: one per (model in role order, level, registered item order):
  model, level, item_id, parent_block_id (root parent), outcome "counted"|"ceiling_violation"|
  "unattributed_overrun", block_id, attempt, envelope_index I? (counted only), retry_stage
  (counted placement stage; null for terminals), late B?, prompt_tokens I?, generated_tokens I?,
  stop_reason?, capped B?, malformed B?, scorer_match B?, correct B?, extracted_answer S?,
  attempt_divergence B?. Terminal items carry block_id/attempt only; their energy is looked up in
  uncounted_windows by key, never copied.
parents: one per root parent in roster["blocks"] order: parent_block_id, model, level, n_items,
  counted_item_ids, window_keys [[block_id, attempt]...], g_j N, k I, fully_counted B, position N?.
cells: keyed "{model_id}:{level}", ten keys: model, level, n_items, n_counted, n_correct, n_capped,
  n_malformed, prompt_tokens, generated_tokens, gross_j, uncounted {ceiling_violation I,
  unattributed_overrun I}, retry_stage_counts {stage: I over counted items}, cap_bound B?,
  spread_exceeded B, fully_counted_parents I, distinct_envelopes I.
levels: "1".."5": executed_drift_lever_slots N?, drift_exceeded B, max_gap N?.
counted_windows: accepted live windows + item_ids, placement order.
uncounted_windows: other accepted windows + reason "voided"|"terminal", input order.
terminal_refusals: roster["terminal_refusals"] verbatim. superseded_rows: non-live rows verbatim.
sha256: SHA-256 of canonical JSON (sort_keys, no spaces, allow_nan=False) of all other keys.
All numbers finite. No key parsed from block_id or cell-key strings.
```

**Harness seat.** `WRITE_SCOPE: ["tests/test_scored_reduce.py", "tests/scored_reduce_checker.py"]`. Oracle `check_reduction(registration_mapping, roster, predicted_decode_s, score_rows, capture_windows, candidate) -> list[dict(code, detail)]`, stdlib only, imports nothing from `joulewise`, recomputes items, parents, cells (except `spread_exceeded`, taken from `tests/scored_roster_checker.check_executed`), uncounted windows and refusal outcome. Committed RED before implementation; each test fails individually (reducer imported inside a helper). Test names, one per ruled clause:
`test_ast_first_statement_is_verifier`, `test_signature_five_positional`, `test_packing_refusal_passes_through` (inv_39 root, inv_38 event, inv_01 registration, unreported_envelope), `test_reduce_input_not_list`, `test_window_keys`, `test_window_domain_zero_negative_nonfinite_bool`, `test_window_unknown_and_idle_slot`, `test_window_binding_in_force_stale_and_final_stamp_refused`, `test_window_duplicate`, `test_window_envelope_mismatch`, `test_window_unstarted`, `test_missing_live_window`, `test_row_keys`, `test_row_domain_stop_reason_vocabulary_and_coherence`, `test_row_scorer_id`, `test_row_unknown_item_not_in_block`, `test_row_binding_final_digest`, `test_row_duplicate`, `test_row_unstarted`, `test_row_missing`, `test_row_tokens_over_cap`, `test_row_cap_disagreement_both_directions`, `test_cap_boundary_cap_minus_one_and_cap`, `test_capped_never_correct`, `test_cap_bound_boundaries_1_5_2_10_3_15_and_null`, `test_cap_bound_fraction_consumed_by_patch`, `test_no_cap_literal_in_source`, `test_codes_disjoint_from_packer`, `test_voided_window_ledgered_not_summed` (completed culprit single, FT-11), `test_terminal_ceiling_window_optional_ledgered_once`, `test_unattributed_multi_item_energy_once` (defect 1), `test_superseded_rows_checked_and_passed_through`, `test_attempt_divergence`, `test_whole_block_retry_window_counts_all_items`, `test_block_energy_summed_once_per_window`, `test_retry_stage_on_items_and_cells` (INV-13), `test_late_disclosed`, `test_spread_four_vs_five_parents_by_terminal_degradation`, `test_spread_four_vs_five_envelopes`, `test_partial_parent_position_and_null_lever` (terminal fixture, replaces packer:337), `test_drift_equal_vs_above_max_gap`, `test_pilot_max_gap_null`, `test_unattributed_count_per_cell` (FT-5 input), `test_internal_disagreement_exit_injection`, `test_output_exact_keys_and_sha256`, `test_forged_single_prediction_refused_record_code` (S12), `test_every_a291_provisional_R_witness_at_real_reduce` (parameterised over every R-column row of 89 §5.1/§5.3), `test_differential_oracle_200_nights`: for `seed` in a fixed set, ≥ 200 `generate_case` nights; per night, variant A = all live windows plus seeded voided/terminal windows, must succeed and equal the oracle minus `sha256`; variant B = one seeded live window dropped, must refuse `missing_live_window` in reducer and oracle.

**Implementation seat.** `WRITE_SCOPE: ["joulewise/scored_reduce.py"]`, starting at the committed harness head; may run `python3 -B -m unittest tests.test_scored_reduce` and read failure output; instructed not to read the two harness files; any needed change elsewhere returns `NEEDS_SCOPE`/`NEEDS_RULING`. Gate before merge: the three focused modules green, operand/boundary/guard-deletion mutation sweep on `scored_reduce.py` (mutants named in D3.2 and Astra R7 must die), and a cold gate.

## Findings (severity independent of verdict)

- **MATERIAL — P-S3 runtime-failure clause is a new science rule** (S3, D3.3). Struck; routed to HEADLINE-AP5M-AMENDMENT-01.
- **MATERIAL — `attempt_divergence` wrongly deferred** (D2). Implement in v1.
- **MATERIAL — registered-mode claim path needs `below_floor`** (D2). Schema v1 is pilot-complete; v2 after the amendment.
- **MATERIAL — S9 refusal instead of diagnostic count.** Rows above the registered cap are not evidence about the registered configuration.
- **NIT — packet hygiene.** The synthesis labels 07d:251 as the denominator source; K24 is. The scout's "OPEN code" harness proposal is superseded (all codes fixed above). Oracle file name now fixed.
- No BLOCKER. The design as amended is executable without further choice.

## Plain summary for Ed

The reducer is ruled: exact input and output shapes, twenty refusal codes, and the rule that a night with a lost energy capture is refused rather than partly counted. Energy for a multi-problem block is recorded once, never per problem. Tokens above the registered cap refuse the run. Runner faults inside an answer have no v4 outcome and must be typed in the analysis-plan amendment. A registered-mode claim also needs the floor gate from that amendment; pilot nights can be reduced now.
