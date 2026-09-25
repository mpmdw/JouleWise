# 30/21 — Cold Fable addendum ruling, A292-REDUCER-DESIGN-01-ADD

Judge: Claude Fable 5.1, fresh session, 2026-09-25 05:26–≈05:45 PDT, worktree HEAD `eb409ec9`. Read-only except this file. No background work, no subagents, no tests run (every probe was a read).

## 0. Custody

- **Validator.** Run 1, charter sha `…95d82` (the deliberate typo): `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2, charter sha `…95d81`: `PASS`, rc 0; all four exhibits matched the manifest (`coldgate-validator-receipt/v2`). Independent `shasum -a 256`: charter `099de884…5d81`, charge `a6f28e26…bfcf5f`. Expected = observed on both.
- **Auto-loaded before I chose anything:** `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, the harness memory index (truncated). None was used. I read the packet, the charter, the ruling lines ex-30's header cites (45/10, 45/21, 15/10, 15/21, 89, 07d, kernel:3832/3861), and the code: `scored_packer.py`, `scored_registration.py`, `mlx_runtime.py`, `test_scored_packer.py:270-345`, `test_scored_packer_fuzz.py:120-175`, `scored_roster_checker.py:1-8`, `scored_case_generator.py:99-119`.
- **Charter §9.** No fix-round history in the packet; no presumption either way.

## E1 — The refuter's findings, ruled one by one

Verdict vocabulary: AFFIRM (the refuter's corrected text stands), DIFFERENT TEXT (mine replaces it), REJECT, or INSTALLED (ex-20 already contains the correction; the refuter was arguing against ex-30's §P, which it never saw amended).

**B1 — missing live window. DIFFERENT TEXT; the refuse policy stands; tier MATERIAL, not BLOCKER.**
Facts, all verified: the three witnesses omit a live key and assert a flag (`test_scored_packer.py:298-302` adds the voided attempt and drops the live one, then `assertTrue(spread_exceeded)`; `:337-340` removes live single `('large:decode:1:0:single:0', 2)` and asserts lever 1.6; `test_scored_packer_fuzz.py:130-132` samples 75 % of all placements). Q16 (15/10:47; 89:375) orders every `reduce`-column witness re-run at the real entry; INV-26 and INV-45 are form (b) at `R`, PROVISIONAL (89:560,572). Recapture is not producible until K25 is ratified (07d:810, 1324-1325), so the refuter is right that "cure is recapture" was false as P-S7 wrote it (ex-20 never said it; only its plain summary implies refusal is survivable).
Merits, as the charge asks. The typed outcome is not "already implied by the A291 surface". `executed_status` accepting a partial key set is API generality, not a science outcome: K24's list of causes that drop a problem is closed (`ceiling_violation`, `unattributed_overrun`, `night_exhausted`, `below_floor`; 07d:196), step 12's NR list is closed (07d:286), and 45/21:58's "for any reason" is glossed by a closed parenthetical of roster events. A `window_missing` item would therefore be dropped from `n` with no ruled NR reason, and spread does not catch it when the cell still has five fully counted parents (six parents, one lost window). That is a silent drop. Refusal counts nothing, so no counted number can be wrong, and the refusal names the key, so nothing is silent. **Refuse wins the charge's test.** It is an amendment of Q16 as applied to witnesses whose input omits a live key, and I label it so. It is not a conversion of a verdict into its opposite (charter §9): the A291 surface, its tests and their PROVISIONAL label are unchanged; only the form of their re-run at `reduce` changes, and Q16 is a gating rule, not a science rule.
Ruled text (replaces ex-20 S7 and ex-30 P-S7):
> **S7 (v1.1).** `reduce` refuses `missing_live_window` when any live placement key `(block_id, attempt)` lacks a window; the refusal detail names the key. `reduce` passes `executed_status` exactly the set of live keys, so within `reduce` the captured set always equals the live set and `spread_exceeded` can arise only from terminals. This AMENDS 15/10 Q16 for the three A291 witnesses whose `captured_window_keys` omit a live key (`test_checker_executed_voided_attempt_counterexample`, `test_executed_partly_counted_parent_position`, the fuzz `_keys` sampler): they stay as A291 tests of `executed_status`, unchanged; their re-run at the real entry takes this form: (i) `test_a291_partial_keys_refuse_at_reduce`, parameterised over the first two witnesses' key sets, asserts `ReductionRefusal` with code `missing_live_window`; (ii) INV-26 and INV-45 form-(b) rows are re-witnessed at `reduce` by `test_spread_four_vs_five_parents_by_terminal_degradation`, `test_spread_four_vs_five_envelopes` and `test_partial_parent_position_and_null_lever`, whose fixtures reach four parents or a partly counted parent only through terminal events, with every live key captured; (iii) the fuzz sampler's analogue is the differential test's variant B. Until K25 is ratified a refused night is lost whole; no recapture roster can be produced; the refusal is the disclosure.

**B2 — `stop_reason`. INSTALLED with one addition.** Verified: `"stop"` is not a literal in `mlx_runtime.py`; :338 is output-policy metadata, not an emit site; emit sites are :568 (`runtime_failed`), :590 (`malformed`), :611 (= `stop_condition` from :896-899: `requested_tokens_emitted` | mlx_lm's `finish_reason` | `stream_exhausted`), :624 (`length`). Ex-20 S3 already closed the set to `{"stop","length"}`, struck the runtime-failure clause, and gave K3's rule. Addition: the refusal gets its own code so a runtime-failed row is distinguishable from a type error. Ruled text:
> **S3 (v1.1).** `STOP_REASONS = {"stop": False, "length": True}` (value = cap class; K3, 07d:262-263). Any other value refuses `row_stop_reason_unknown`. `row_cap_disagreement` unless `STOP_REASONS[stop_reason] == (generated_tokens >= cap_tokens[arm])`. Mapping mlx_lm finish reasons onto `{stop, length}` and never emitting a scored row for a runtime failure are obligations of the score-row producer (scorer lane), recorded as a CARRIED non-field row; a runtime-failed item therefore surfaces as `row_missing` (no row) or `row_stop_reason_unknown` (raw row), never as a counted outcome. Any counted outcome for runtime failures goes to HEADLINE-AP5M-AMENDMENT-01.
No conflict between refuter and ex-20 on substance.

**M1 — terminal `gross_j`. DIFFERENT TEXT; MATERIAL.** K17 is ruled verbatim: "recorded on the terminal refusal as `gross_j`" (45/10:79; 07d:746; kernel:3832). Ex-20 S6 dropped it from the terminal record. Only `ceiling_violation` is under K17 and it is always a one-item single (`scored_packer.py:444-449`), so a per-record `gross_j` cannot double count there; `unattributed_overrun` records are per item under one key (:448-449) and must not carry energy. Ruled text:
> Output `terminal_refusals`: one record per roster terminal record, in roster order, = the roster's 7 keys plus `window_key` ([block_id, attempt]) and `gross_j`. For `ceiling_violation`, `gross_j` is the accepted window's value or `null` when absent (S8). For `unattributed_overrun`, `gross_j` is always `null`; its energy is held once in `uncounted_windows` under its key. A window whose key's observation is `not_started` refuses `window_unstarted`; a window for a `cut_off`/`completed` terminal key is optional.

**M2 — in-force digest. INSTALLED for the definition; DIFFERENT TEXT for the reason; REJECT for rows; NIT.** Verified: each event stores its resulting digest (`scored_packer.py:309`), replay checks each (:485), and placements only go above the reporter (:334), so in-force is readable from the sealed roster. Ex-20 S1 already defined `in_force(ix)`. Its phrase "the only reducer-checkable evidence of FT-9" overclaims: anyone holding the sealed roster can stamp after the fact. Ruled wording: *"The in-force stamp is a consistency binding of a window to the plan in force for its envelope; it is stampable at capture, which the final digest is not. FT-9 stays a runner-lane obligation with no reducer witness."* Rows keep the FINAL digest (ex-20 S1): the scorer runs over the finished roster, and a final stamp catches a scorer run on a stale roster, which an in-force stamp recomputed from the same roster would not.

**M3 — K24 paired drop. AFFIRM with additions; MATERIAL.** Verified: "contributes to neither model's energy nor correct count nor n for that cell" (07d:196) and "dropped from both models" (07d:269-270). Items are shared per level across models (`item_ids_by_level`, `scored_registration.py:136`), so the reducer can pair on `(level, item_id)`. The flip example is right arithmetic (2/10 false, 2/9 true). Every seat, ex-30 and ex-20 missed it; ex-20 D3.1's "denominator is counted rows" is wrong. Energy caveat the refuter did not state: block energy is per window, so an unpaired item inside an unsplit counted block cannot be subtracted; that part of K24 is the estimator's, on parents. Ruled text:
> An item is **paired** iff both models have a counted attempt for it. Cell `n`, `n_correct`, `n_capped`, `n_malformed`, `prompt_tokens`, `generated_tokens`, `retry_stage_counts` and `cap_bound` range over paired items; `n_counted` (this model's counted rows) is kept beside them; `k24_dropped` lists each counted-but-unpaired item as `{item_id, partner_outcome}` with the partner's terminal type. `gross_j` stays the fsum of the model's counted windows; parents carry `unpaired_item_ids`, and the energy side of K24 is CARRIED to A293 with that list. Items carry `paired B?` (null for terminals).

**M4 — per-window anchor bound. AFFIRM; MATERIAL.** Verified 07d:640: the anchor is "window w's reducer field `energy_bound_terms_j.E_clock_anchor_shift_bound_j`; a counted window without a bounded value is refused (`anchor_energy_envelope_unrecorded`)". It needs no registration key. Ex-20's window schema omits it and its D2 answer is amended: **A292 v1 is not claim-bearing without this field**; with it, v1 is pilot-complete and a registered claim still needs `below_floor` (schema v2). Text is in E2.

**M5 — oracle independence. INSTALLED.** Ex-20 D4: "stdlib only, imports nothing from `joulewise`", may use `tests.scored_roster_checker`. Matches 45/10:32 and the checker header. Added: the enforcing test is named in E2.

**M6 — differential degeneracy. INSTALLED.** Ex-20's variant A / variant B is the refuter's text. Kept.

**M7 — row completeness. INSTALLED.** Ex-20 has `row_missing`, `row_duplicate`, `row_unknown`, `row_unstarted`, and superseded rows pass every check. Ex-20's names stay.

**M8 — mutation sweeps. DIFFERENT TEXT; NIT.** No test file in `tests/` carries a sweep; sweeps are a gate criterion (45/21:56), and ex-20 lists them in the merge gate. Text: *"The implementation PR's gate ledger records the operand-collapse, `>`↔`>=` boundary and guard-deletion sweeps over `joulewise/scored_reduce.py` with zero survivors; the mutants that must die include: `>=`→`>` in `capped`; `>`→`>=` in `cap_bound`; `sr.CAP_BOUND_FRACTION`→literal; dropping the pairing filter; summing a window per item; dropping the `missing_live_window`, `row_tokens_over_cap`, anchor and `internal_disagreement` guards."* Not a unittest.

**M9 — tokens over cap. INSTALLED** (ex-20 S9 refuses `row_tokens_over_cap`). Concur with the refuter's reasons (`scored_registration.py:99-102,153-154`).

**N1 — patch site. DIFFERENT TEXT; MATERIAL (gate-criterion conformance).** 45/21:56 rules "constants are patched at their module attribute", the defining module's. Under `from … import CAP_BOUND_FRACTION`, patching `scored_registration` does not reach the reducer, so ex-20's witness (patch on `scored_reduce`) is not the ruled CONSUMED form. Text: *"`scored_reduce.py` does `import joulewise.scored_registration as sr` and reads `sr.CAP_BOUND_FRACTION` at call time; no `from`-import of the name and no `0.2`/`0.20` literal (AST scan). The witness uses `patch.object(sr, "CAP_BOUND_FRACTION", 0.25)` and 3/10 flips to false."*

**N2 — INSTALLED** (ex-20 already says "every code literal"). **N3 — AFFIRM** (cite :568,590,611(:895-900),624). **N4 — INSTALLED.** **N5 — AFFIRM** (counts are in items). **N6 — AFFIRM**, recorded as a known limit. **`floor_j` still in `REGISTRATION_KEYS`** (`scored_registration.py:28`; removed by 07d:841): verified, CARRIED to A293 per 45/10:41; NIT, routed to the AP-5M amendment with `floor_gate_j`.

**Found by this gate, missed by the charge.**
- **Naming hazard (MATERIAL as a text defect).** `registration.cap` is the envelope capacity in seconds (`scored_registration.py:79`; used at `scored_packer.py:219`), not the token cap. Ex-20's text `cap = registration.cap_tokens[registration.arm]` invites the harness or oracle to read `.cap`. E2 names it `cap_tokens_arm` and forbids the bare name.
- **Live keys are always `completed`.** Every non-`keep` decision moves the block to `voided_block_ids` (`scored_packer.py:441-443`); `keep` requires `completed` (:431). So `window_unstarted`/`row_unstarted` can only fire on voided or terminal keys; E2 states it so the harness does not chase a live `not_started` fixture.

**Where ex-20 and the refuter conflict, and who prevails.** B1: both keep refuse; the refuter's labelling and three-witness accounting prevail over ex-20's one-witness note. B2: no substantive conflict; the separate code is added. M1: the refuter prevails (ruled K17 text). M2: ex-20 prevails on rows; the refuter on wording. M3, M4, N1: the refuter prevails. Ex-20 stands everywhere else, and the refuter's BLOCKER tier is not sustained: neither B1 nor B2 leaves the design inexecutable once these texts are installed.

## E2 — A292 reducer rulings v1.1 (final texts)

Supersedes ex-20 D4 in full. Wire conventions: `S` nonempty str; `H` 64 lowercase hex; `I` int ≥ 0 with `type(v) is int`; `N` finite number, `type(v) in (int, float)`; `B` bool; `?` nullable, never omitted; exact key sets; no unknown keys, defaults or coercion. `in_force(k)` = `sha256` of the last event with `envelope_index < k`, else `roster["registered_sha256"]`. `cap_tokens_arm = registration.to_mapping()["cap_tokens"][arm]` with `arm = registration.to_mapping()["arm"]`; the name `cap` is never used for it (`registration.cap` is capacity seconds).

```text
ENTRY
reduce(registration, roster, predicted_decode_s, score_rows, capture_windows) -> dict
Five positional parameters, no defaults. First statement (AST-asserted):
verify_executed_roster(registration, roster, predicted_decode_s). PackingRefusal from it or
from executed_status propagates unchanged. Pure: no argument mutated. Module joulewise/scored_reduce.py.
import joulewise.scored_registration as sr; sr.CAP_BOUND_FRACTION read at call time; no from-import
of the name; no 0.2/0.20 literal in the module.
STOP_REASONS = {"stop": False, "length": True}

SCORE ROW  schema "joulewise.scored_row.v1"  (exact 12 keys)
schema; registration_sha256 H (== registration.digest); roster_sha256 H (== roster["sha256"], FINAL);
scorer_id S (== registration scorer_id); block_id S; attempt I; item_id S; prompt_tokens I;
generated_tokens I; stop_reason S; extracted_answer S?; scorer_match B.
Coherence: scorer_match => extracted_answer is not null. Key (block_id, attempt) must be a roster
placement and item_id in that block's items.

CAPTURE WINDOW  schema "joulewise.scored_window.v1"  (exact 8 keys)
schema; registration_sha256 H (== registration.digest); roster_sha256 H (== in_force(envelope_index));
block_id S; attempt I; envelope_index I (== placement.envelope_index); gross_j N > 0;
bundle_sha256 H (carried, not verified); energy_bound_terms_j: object with exactly one key
E_clock_anchor_shift_bound_j: N >= 0, or null (null allowed only on a non-live key).

CLASSIFICATION of a placement key (precedence)
live     : block_id in envelopes[envelope_index]["blocks"]   (always observation status "completed")
terminal : (block_id, attempt) equals a terminal_refusals entry's (block_id, attempt)
voided   : otherwise
observation(key) = entry of envelopes[envelope_index]["observations"] with that block_id.

REFUSAL CLASS  class ReductionRefusal(ValueError) with .code and .detail; REDUCTION_CODES exactly:
reduce_input                     score_rows or capture_windows is not a list
window_keys                      window key set != schema
window_domain                    type/domain/schema literal failure (gross_j <= 0, nonfinite, bool,
                                 anchor object shape or negative/nonfinite anchor)
window_unknown                   key is not a placement (idle_slot keys are never placements)
window_binding                   registration_sha256 or roster_sha256 (in-force) mismatch
window_duplicate                 repeated (block_id, attempt)
window_envelope                  envelope_index != placement.envelope_index
window_unstarted                 observation(key).status == "not_started"
anchor_energy_envelope_unrecorded a live key's window has anchor null (K11, 07d:640)
missing_live_window              a live placement has no window (detail names the key)
row_keys                         row key set != schema
row_domain                       type/domain failure or coherence failure
row_stop_reason_unknown          stop_reason not in STOP_REASONS
row_scorer                       scorer_id mismatch
row_unknown                      key not a placement, or item_id not in that block
row_binding                      registration_sha256 or roster_sha256 (final) mismatch
row_duplicate                    repeated (block_id, attempt, item_id)
row_unstarted                    observation(key).status == "not_started"
row_missing                      a live placement lacks a row for one of its items
row_tokens_over_cap              generated_tokens > cap_tokens_arm
row_cap_disagreement             STOP_REASONS[stop_reason] != (generated_tokens >= cap_tokens_arm)
internal_disagreement            reducer's own spread counts disagree with executed_status
A test asserts REDUCTION_CODES is disjoint from every code literal in scored_packer.py and
scored_registration.py. Terminal types are record fields, never codes.

CHECK ORDER (first failure wins; within a phase, input list order)
1 verifier  2 reduce_input  3 windows: keys, domain, unknown, binding, duplicate, envelope, unstarted
4 rows (ALL rows, superseded included): keys, domain, stop_reason_unknown, scorer, unknown, binding,
duplicate, unstarted, tokens_over_cap, cap_disagreement  5 completeness: missing_live_window,
anchor_energy_envelope_unrecorded, row_missing  6 executed_status(registration, roster,
predicted_decode_s, frozenset(live keys))  7 internal_disagreement.

COMPLETENESS
live key     : window REQUIRED with non-null anchor; one row per item REQUIRED
voided key   : window optional -> uncounted_windows reason "voided"; rows optional -> superseded_rows
terminal key : window optional -> uncounted_windows reason "terminal"; rows optional -> superseded_rows
not_started  : window forbidden (window_unstarted); rows forbidden (row_unstarted); such keys are
               never live
Only live windows enter gross_j, positions and counts; energy is fsum'd once per counted window
(placement order), never once per item.

CAP (sealed AP-5M v4 only; nothing selects semantics)
capped    = generated_tokens >= cap_tokens_arm     (cap-1 false; cap true; cap+1 refuses)
malformed = extracted_answer is None
correct   = scorer_match and not capped            (K3)
paired(item) = both models have a counted attempt for (level, item_id)   (K24, 07d:196)
cell.cap_bound = null if n == 0 else (n_capped / n) > sr.CAP_BOUND_FRACTION, over paired items,
division form only. Boundaries: 1/5, 2/10, 3/15 false; 2/5, 3/10, 4/15 true; the K24 flip
2/10 false -> partner terminal -> 2/9 true is a named witness; patch.object(sr,
"CAP_BOUND_FRACTION", 0.25) flips 3/10 false (CONSUMED witness).
attempt_divergence(item) = counted correct != derived correct of any superseded row of the same
(model, item_id); false when none exists.

EXECUTED STATUS
executed_status output copied verbatim: spread_exceeded {ten cells}, executed_drift_lever_slots
{"1".."5": N?}, drift_exceeded {"1".."5": B}. Spread per CELL, drift per LEVEL. Reducer recomputes
per cell fully_counted_parents and distinct_envelopes and refuses internal_disagreement unless
spread_exceeded[cell] == (fully_counted_parents < 5 or distinct_envelopes < 5) for all ten.
Parent position = item-weighted mean of counted windows' envelope indices; partly counted parents
contribute; lever null when either model has zero fully counted parents; drift false when lever
or max_gap null; equality does not exceed. No level status, no NE/NR; precedence is A293's.

OUTPUT  schema "joulewise.scored_reduction.v1"; exact keys:
schema; registration_sha256; roster_sha256 (final); registered_sha256; scorer_id; mode; claim_ready;
items; parents; cells; levels; counted_windows; uncounted_windows; terminal_refusals;
superseded_rows; executed_status; sha256.
items (model in role order, level, registered item order): model, level, item_id, parent_block_id
  (root parent), outcome "counted"|"ceiling_violation"|"unattributed_overrun", block_id, attempt,
  envelope_index I?, retry_stage S? (counted placement stage), late B?, prompt_tokens I?,
  generated_tokens I?, stop_reason S?, capped B?, malformed B?, scorer_match B?, correct B?,
  extracted_answer S?, attempt_divergence B?, paired B?. Terminal items: block_id/attempt only; energy
  is looked up in uncounted_windows by key, never copied.
parents (roster["blocks"] root order): parent_block_id, model, level, n_items, counted_item_ids,
  unpaired_item_ids, window_keys [[block_id, attempt]...], g_j N, k I, fully_counted B, position N?.
cells ("{model_id}:{level}", ten keys): model, level, n_items, n_counted, n, n_correct, n_capped,
  n_malformed, prompt_tokens, generated_tokens (paired sums), gross_j (all counted windows),
  k24_dropped [{item_id, partner_outcome}], uncounted {ceiling_violation I, unattributed_overrun I}
  (in items), retry_stage_counts {stage: I over paired items}, cap_bound B?, spread_exceeded B,
  fully_counted_parents I, distinct_envelopes I.
levels "1".."5": executed_drift_lever_slots N?, drift_exceeded B, max_gap N?.
counted_windows: accepted live windows (all 8 keys) + item_ids, placement order.
uncounted_windows: other accepted windows + reason "voided"|"terminal", input order.
terminal_refusals: per M1 text (roster 7 keys + window_key + gross_j).
superseded_rows: non-live rows verbatim, input order.
sha256: SHA-256 of canonical JSON (sort_keys, no spaces, allow_nan=False) of all other keys.
All numbers finite. No key parsed from block_id or cell-key strings. Schema v1 is pilot-complete;
a registered-mode claim needs v2 (floor_gate_j + below_floor via HEADLINE-AP5M-AMENDMENT-01).
```

**Harness seat.** `WRITE_SCOPE: ["tests/test_scored_reduce.py", "tests/scored_reduce_checker.py"]`. Oracle `check_reduction(registration_mapping, roster, predicted_decode_s, score_rows, capture_windows, candidate) -> list[dict(code, detail)]`, stdlib only, imports no `joulewise` module (AST-enforced), may import `tests.scored_roster_checker` (its `check_executed` supplies `spread_exceeded`); recomputes items, pairing, parents, cells, ledgers and the refusal outcome. Committed RED before implementation; each test fails individually (reducer imported inside a helper). Test names, one per ruled clause: `test_ast_first_statement_is_verifier`, `test_signature_five_positional`, `test_packing_refusal_passes_through` (inv_39, inv_38, inv_01, unreported_envelope), `test_reduce_input_not_list`, `test_window_keys`, `test_window_domain_zero_negative_nonfinite_bool_anchor`, `test_window_unknown_and_idle_slot`, `test_window_binding_in_force_stale_and_final_stamp_refused`, `test_window_duplicate`, `test_window_envelope_mismatch`, `test_window_unstarted_only_on_nonlive_keys`, `test_anchor_unrecorded_live_refuses_nonlive_null_ok`, `test_missing_live_window_names_key`, `test_a291_partial_keys_refuse_at_reduce` (B1 (i)), `test_row_keys`, `test_row_domain_and_coherence`, `test_row_stop_reason_unknown_incl_runtime_failed`, `test_row_scorer_id`, `test_row_unknown_item_not_in_block`, `test_row_binding_final_digest`, `test_row_duplicate`, `test_row_unstarted`, `test_row_missing`, `test_row_tokens_over_cap`, `test_row_cap_disagreement_both_directions`, `test_cap_boundary_cap_minus_one_and_cap`, `test_capped_never_correct`, `test_cap_bound_boundaries_1_5_2_10_3_15_and_null`, `test_cap_bound_k24_pairing_flip_2_10_to_2_9`, `test_k24_dropped_listed_and_parents_unpaired_ids`, `test_cap_bound_fraction_consumed_by_patch_on_sr`, `test_no_cap_literal_and_no_from_import`, `test_codes_disjoint_from_packer_and_registration`, `test_oracle_imports_no_joulewise`, `test_voided_window_ledgered_not_summed` (FT-11), `test_ceiling_terminal_gross_j_on_record_or_null`, `test_unattributed_multi_item_energy_once_gross_j_null` (defect 1, M1), `test_superseded_rows_checked_and_passed_through`, `test_attempt_divergence`, `test_whole_block_retry_window_counts_all_items`, `test_block_energy_summed_once_per_window`, `test_retry_stage_on_items_and_cells` (INV-13), `test_late_disclosed`, `test_spread_four_vs_five_parents_by_terminal_degradation`, `test_spread_four_vs_five_envelopes`, `test_partial_parent_position_and_null_lever` (terminal fixture), `test_drift_equal_vs_above_max_gap`, `test_pilot_max_gap_null`, `test_unattributed_count_per_cell_in_items` (FT-5), `test_internal_disagreement_exit_injection`, `test_output_exact_keys_and_sha256`, `test_forged_single_prediction_refused_record_code` (S12), `test_every_a291_provisional_R_witness_at_real_reduce` (parameterised over every 89 §5.3 row whose F column names `R`; form per FT-4, with B1's substitution for partial-key inputs), `test_differential_oracle_200_nights` (for `seed` in a fixed set, ≥ 200 `generate_case` nights; variant A = all live windows with anchors plus seeded voided/terminal windows, must succeed and equal the oracle minus `sha256`; variant B = one seeded live window dropped, must refuse `missing_live_window` in both).

**Implementation seat.** `WRITE_SCOPE: ["joulewise/scored_reduce.py"]`, starting at the committed harness head; may run `python3 -B -m unittest tests.test_scored_reduce` and read failure output; instructed not to read the two harness files (known limit N6: tracebacks print oracle lines); any needed change elsewhere returns `NEEDS_SCOPE`/`NEEDS_RULING`. Gate before merge: the focused modules green; the M8 sweep ledger with zero survivors; a cold gate.

## Findings, tiered (severity independent of verdict)

- **MATERIAL — S7 was an unlabelled amendment of Q16 and mis-stated the cure** (B1). Cured by the S7 v1.1 text. Not BLOCKER: the policy survives on the merits.
- **MATERIAL — K24 pairing missed by every seat and by ex-20** (M3). Cell counts and `cap_bound` now range over paired items.
- **MATERIAL — per-window anchor bound omitted** (M4). Schema v1 is not claim-bearing without it.
- **MATERIAL — K17 `gross_j` removed from the terminal record** (M1). Restored for `ceiling_violation`.
- **MATERIAL — CONSUMED witness not in the ruled patch-at-defining-module form** (N1).
- **MATERIAL — `cap` naming hazard** (`registration.cap` is seconds). Cured by `cap_tokens_arm`.
- **NIT** — M2 wording; M8 sweep list; N3 citation; N5 unit; N6 limit; `floor_j` superseded but still registered; ex-30 P-S7 "cure is recapture" false until K25.
- **Packet hygiene:** adequate. The charge presented both arguments neutrally; the refuter never saw ex-20, so seven of its findings were already installed there, which the charge's framing ("2 BLOCKERs") did not disclose. NIT.
- No BLOCKER. With E2 installed the design is executable without further choice.

## Plain summary for Ed

A lost energy capture still refuses the whole night; that is now written as a deliberate change to one earlier test rule, and the night cannot be re-run until the retry amendment lands. The reducer must drop a problem from both models' counts when either model failed it, which changes the cap-bound label; every reviewer had missed that. Each energy window must carry its clock-anchor bound, or the night is not claim-grade. A falsified-bound retry keeps its measured joules on its own record. Nothing else in the earlier ruling changes.
