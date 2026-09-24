# 20 — A281 escalation consult, Opus 5.5 blind seat (brief 18b), head d2f9a273

Transcribed by the magistrate from the subagent's final report. Scratch artefacts: `/tmp/opus18b/spec.py` (reference decision layer), `patterns.py`, `enum.py` (every reachable input run through the reference and the current `decide`, with `ratio_interval` monkeypatched to return prescribed p-values and intervals).

## Q1 Diagnosis

The magistrate's diagnosis is right but incomplete. (1) **The rule is incomplete, not only scattered.** Packet C, M9 and ruling 08 each define when L\* exists, and none defines the rest: which reason applies when it does not, what status a pooled level gets, or what "monotone" means with unresolved levels. So fix seats made up the missing branches; the fallback at `energy_per_correct.py:241-245` is made-up rule text. Packet C also has two tests for "below 1": its terms paragraph says "interval wholly below 1", while §3 says "Holm rejects and p_below < p_above". The code requires both, and nobody decided that. (2) **Tests check single points in a small, finite input space.** There are only 676 reachable decision inputs. At d2f9a273, 123 of them yield an L\* where packet C says non-monotone (e.g. 88818 → 5; 88188 → 4); 91 return a wrong or false `boundary_in_merged_group` (e.g. `123|45` statuses `11`); every pooled constituent row is labelled "not estimable" (932 level-rows). (3) **The mutation gate gave false assurance:** 236/236 killed shows the tests pin down the code as written, not that it matches the specification. (4) **Validation happens where the value is used, not where inputs enter** (19 `.get(` / `setdefault` / `=None` sites); class (iv) needs a structural cure. Also, 14 clauses in one fix seat is how fix rounds introduce new partial edges.

## Q2 Decision specification

Group status: `8B cheaper` (E8), `1.7B cheaper` (E1), `not resolved` (NR), `not estimable` (NE, reason `sparse_after_merges` or `ceiling_violation`). Level status: the group status if alone, else `pooled` with `pooled_in`. Pattern: `crossover`, `reverse_order`, `non_monotone`, `all_1.7B`, `all_8B`, `one_signed_1.7B`, `one_signed_8B`, `none_resolved`, `none_estimable`. L\* absent reasons: `boundary_group_pooled`, `reverse_order_not_registered`, `non_monotone`, `no_8B_cheaper_group`, `no_1.7B_cheaper_group`, `none_resolved`, `none_estimable`.

```
merge(c8, c17):                        # correct counts per level; nothing else
  groups = {1},{2},{3},{4},{5}; sparse(g) = min(Σc8[g], Σc17[g]) < 3
  if sparse{4} or sparse{5}: join(5,4); if sparse(group(5)): join(group(5),3)
  if sparse{1} or sparse{2}: join(1,2); if sparse(group(1)): join(group(1), group(3))
  NE = {g : sparse(g)}                 # e.g. {3} alone, 345, 123, 12345
holm(p over tested groups, m=5 fixed): sort ascending; reject while p ≤ α/(5−rank); stop at first failure
status(g): NE if g∈NE; else if not rejected or p_below==p_above: NR
           else E8 if p_below<p_above and hi<1; E1 if p_above<p_below and lo>1
           else NR + flag interval_disagrees
classify(groups in level order):
  seq = statuses of E8/E1 groups in level order; changes = #adjacent differences
  seq empty          → none_estimable if all NE else none_resolved
  changes == 0       → all_X if every group resolved else one_signed_X
  changes ≥ 2        → non_monotone
  seq[0] == E8       → reverse_order
  else (E1…E1 E8…E8) → crossover: boundary = first E8 group, licensing = last E1 group,
                       gap_levels = levels strictly between (NR/NE)
                       L* = boundary's level if single, else None, reason boundary_group_pooled
                       (crossover_group still reported)
```

Rulings the table settles: monotone is over resolved groups only; NR/NE are gaps, reported as `gap_levels` and named in the claim sentence. **Ruling 08 is too strict on the licensing side:** the licensing condition is existential (some lower region is 1.7B-cheaper), and a pooled 1–2 group proves that, while the boundary claim rests on Level 3's own unmerged test; so `12|3|4|5` with `1888` gives L\* = 3 with licensing group 1–2. 08 is right on the boundary side. Reverse crossovers are a pattern, not a registered L\*. A sparse Level 3 alone has no merge target in packet C and stays NE (needs registration text).

| Partition | Group statuses | Level statuses | Pattern | L\* / reason |
|---|---|---|---|---|
| 1\|2\|3\|4\|5 | 1n888 | 1n888 | crossover | 3 (gap 2) |
| 1\|2\|3\|4\|5 | 88111 | 88111 | reverse_order | none / reverse_order_not_registered |
| 1\|2\|3\|4\|5 | 81888 | 81888 | non_monotone | none (current code: 3) |
| 1\|2\|3\|4\|5 | 18188 | 18188 | non_monotone | none (current code: 2) |
| 1\|2\|3\|4\|5 | 1nn8n | 1nn8n | crossover | 4 (gap 2–3) |
| 1\|2\|3\|4\|5 | n1n8n | n1n8n | crossover | 4, licensing 2 |
| 1\|2\|3\|4\|5 | 11188 | 11188 | crossover | 4 |
| 1\|2\|3\|4\|5 | 11111 | 11111 | all_1.7B | none / no_8B_cheaper_group |
| 1\|2\|3\|4\|5 | 111n1 | 111n1 | one_signed_1.7B | none |
| 1\|2\|3\|4\|5 | n8888 | n8888 | one_signed_8B | none / no_1.7B_cheaper_group |
| 1\|2\|3\|4\|5 | nnnnn | nnnnn | none_resolved | none |
| 1\|2\|3\|4\|5 | 11x88 | 11x88 | crossover | 4, licensing 2, gap 3 (NE) |
| 1\|2\|3\|4\|5 | 1n8n1 | 1n8n1 | non_monotone | none |
| 1\|2\|3\|45 | 1118 | 111pp | crossover | none / boundary_group_pooled; group 4–5 |
| 1\|2\|3\|45 | 1111 | 111pp | all_1.7B | none (current code: false boundary_in_merged_group) |
| 12\|3\|4\|5 | 1888 | pp888 | crossover | 3, licensing 1–2 (08 says undefined) |
| 12\|3\|45 | 1n8 | ppnpp | crossover | none / boundary_group_pooled |
| 1\|2\|345 | 11x | 11ppp | one_signed_1.7B | none |
| 12345 | x | ppppp | none_estimable | none |

## Q3 Acceptance shape

Sound, with conditions: split `decide` into pure layers (`merge` → per-group `ratio_interval` → `holm` → `status` → `classify`) so enumeration needs no bootstrap; the enumeration proves code = reference, not reference = intent, so the cold Fable gate rules on the worked-pattern table; the implementer may ship the gated reference as `classify`, compared exhaustively with a second, table-driven encoding written in the brief. Sizes measured: merge 4^10 = 1,048,576 capped-count inputs → 9 partitions, 18 (partition, NE-set) pairs, 6.8 s; status 18 cases; holm ≈ 12^5 ≈ 250k grid inputs around each cutoff; classify 676 × 2 (family); composition 676 via `unittest.mock.patch` on `ratio_interval`.

## Q4 Silent defaults

A frozen `Registration` dataclass built only through `Registration.from_mapping(d)`, refusing unknown and missing keys, no defaults; its digest bound into roster, reducer output and decision output; `pack`, `requeue_overrun`, `reduce`, `decide` take it as required first argument and check type and digest. `reduce` also takes the roster and checks completeness (every roster item appears exactly once as a row or a terminal refusal). Fields: identity (`schema`, `mode ∈ {pilot, registered}`, `arm`, `arm_to_family` so the family is derived, `role_to_model_id`); levels and decision (`levels = [1..5]`, `merge_order` as data, `min_correct = 3`, `alpha`, `holm_m = 5`, `n_boot`, `seed`); `floor_j`, `anchor_j`; `cap_tokens` per arm, `cap_bound_fraction = 0.20`; sizing (`block_size` per arm, `n_per_level`, `min_blocks_per_cell = 5`, `min_envelopes_per_cell = 5`); timing with coherence checks (`offset_s + interior_s ≤ envelope_s`, `interior_s − guard_s > 0`, `pitch_s ≥ envelope_s`); physical ceiling (`s_per_token_upper` per model and arm, `prefill_s`, `ceiling_s`; `cap × s/token_upper + prefill ≤ ceiling_s ≤ capacity`; single-problem worst case DERIVED and asserted ≥ the failed prediction); retry stages distinct (`initial`, `whole_block`, `single_problem`, `single_retry`, `ceiling_violation`); `max_drift_lever_slots` (null only in pilot mode), declared sensitivities, scorer id, item-set digest. Two structural tests: `inspect.signature` shows no public parameter default except presentational ones; an AST scan finds no `.get(`, `setdefault` or `None` default on input records.

## Q5

(a) Per replicate, drawn block d, model m: share s = drawn items' generated tokens ÷ block's generated tokens (even split at zero tokens); allocated energy e = g·s; bound u = k·(floor + anchor)·s with k the number of measured windows composing the block for that model. U_m = Σ u. Low bound R(E₈ − U₈, E₁.₇ + U₁.₇), high R(E₈ + U₈, E₁.₇ − U₁.₇); point bounds use s = 1. Exact because allocation is linear; Sol's plain per-draw window count under-bounds draws where s > 1.
(b) Refuse at pack time when any level's gap exceeds `max_drift_lever_slots` (refusal costs no capture). Register the threshold now as a formula: `max_gap = budget_j / (δ_upper · blocks_per_cell)`, with δ_upper from the pilot. `requeue_overrun` recomputes the gap; the claim uses the executed roster's gap.
(c) The group containing a ceiling-violation item becomes `not estimable (ceiling_violation)`; the family continues; Holm m stays 5; pairwise exclusion only as a labelled selection-confounded sensitivity. Pairwise exclusion as primary is exactly the selection M12 forbids; imputing "incorrect" fails because energy and outcome are both censored. The output flags that the registered `s_per_token_upper` was false for that arm. The reducer passes `terminal_refusals` through as typed records instead of the pairing `ValueError`.

## Q6 Scope

Split: **A281a** packer + reducer + `Registration` (+ cell interface with `terminal_refusals` and `parent_block_id`); remaining defects are mechanical and Q4 kills them as a class; on the arming critical path. **A281b** estimator: (1) put the Q2 table and pseudocode into the AP-5M registration text and have the cold Fable instance rule on the worked patterns (rules before data, so before the first scored night); (2) implement against the Q3 enumeration and Q5a/Q5c. The estimator runs at the desk over immutable rows (M11), so its code can land after the first capture; its rule cannot. One lane means a third mixed round.
