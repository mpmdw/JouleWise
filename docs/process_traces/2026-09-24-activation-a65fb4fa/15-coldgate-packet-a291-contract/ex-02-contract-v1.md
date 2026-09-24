# 02 — A291 (HEADLINE-PACKER-RECUT-01): invariant matrix, roster data contract, checker interface, open points

Drafted 2026-09-24 by the contract-drafting seat (Opus 5.5) for the magistrate of activation a65fb4fa. DRAFT: the magistrate reviews and owns it. Nothing here is a ruling. Where this file and a ruling differ, the ruling wins, in this order: 45/21 §7 > 45/10 > 21/10 > 08.

**Sources.** Every path is relative to `docs/process_traces/2026-09-23-activation-d8cc9c0a/`:
- [08] `08-a281-round1-synthesis-and-rulings.md`
- [21/10] `21-coldgate-packet-a281/10-coldgate-fable-ruling.md`; [21/11] its paired refuter `11-opus-contract-refuter.md`
- [45/10] `45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md`; [45/11] its paired refuter
- [45/21] `45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md`
- [19] `../2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` §1: the M8 base rule, which the rulings amend.

Text inside «…» is quoted verbatim. `c:<file>:<line>` means that file at commit `c0998fdb`. "Registered" = a key in the Registration mapping. "Derived" = computed from registered values, with the seal re-deriving it and requiring equality. "Recorded" = observed or produced by an event and stored in the roster.

**Path codes** for the closed path list of §7(G): `P` = `pack`. `E1` initial→whole_block, `E2` initial→reschedule, `E3` initial→unattributed_overrun, `E4` whole_block→single_problem, `E5` whole_block→unattributed_overrun, `E6` single_problem→single_retry, `E7` single_problem→reschedule, `E8` single_retry→ceiling_violation, `E9` single_retry→reschedule (`E1`–`E9` are all `requeue_overrun`). `R` = `reduce`. `ALL` = all eleven. A path marked "n/a" needs the contract-lens-reviewed reason given in the row (OP-28).

---

## 1. Invariant matrix (magistrate rows)

Each row gives: the ruled text; the predicate over the §2 data, with registration `g`, roster `r` and predictions `p`; and the paths needing a violating witness. The definitions `cap`, `worst(m)`, `bpc`, `max_gap`, `canon_sha` and `pos` are in §2.0.

### A. Identity and digests

**INV-01 registration binding.** «Identity fields (`schema`, `registration_id`, `plan_id`) are CONSUMED: their witness is that a roster sealed under the old digest is refused by every consumer under the new registration.» [45/10 §Q2]
Predicate: `r.registration_sha256 == canon_sha(g)`. Paths: ALL.

**INV-02 roster self-digest.** «Opus S4 (digest chain and bound parameters)» [08 Adopted fixes]. The addendum adds: «PF shows the requeue entry trusts any well-formed roster» [45/21 A4]. So this row is necessary but not sufficient; INV-38 and INV-39 supply the rest.
Predicate: `r.sha256 == canon_sha(r minus "sha256")`. Paths: ALL.

**INV-03 no copies.** «no roster copies of registered values» [45/21 §7(S)]; «no copies (roster carries only `registration_sha256`)» [45/10 §Q2(1)].
Predicate:
- the set of top-level roster keys equals the §2.3 set exactly;
- no key at any level of `r` is a Registration key name;
- no key is one of the c0998fdb copy keys `models`, `arm`, `block_size`, `interior_s`, `guard_s`, `cap_tokens_by_arm`, `envelope_s`, `offset_s`, `pitch_s`, `capacity_s`, `levels` (c:scored_packer.py:149-152, 262-265).

Paths: ALL.

**INV-04 derived identity fields.** «Register `item_ids_by_level`; derive `item_set_sha256`, `n_per_level`» and «`item_set_sha256 := canonical_json_sha256([ids in level order])` is a derived roster field.» [45/10 §Q3]
Predicate: `r.item_set_sha256 == canon_sha(ITEM_SET_FORM(g))` (form per OP-04), and `r.n_per_level == n(g)` (OP-05). Paths: ALL.

**INV-05 claim readiness.** «`mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.» [21/10 §Q2 D4]
Predicate: `r.claim_ready == (g.mode == "registered")`. Paths: ALL. See OP-10.

### B. Registration coherence and prediction binding

**INV-06 worst-case ordering.** «registration keeps the inequality derived worst case ≤ `ceiling_s` ≤ capacity» [45/10 §Q2 table]; «the worst-case seconds input is derived in Registration (`cap × s_per_token_upper + prefill`)» [21/10 §Q4].
Predicate: for every model id `m` and every arm `a` in `g.arm_to_family`, `worst(m,a) ≤ g.ceiling_s[m][a] ≤ cap`.
Paths: P, R. The requeue edges are n/a: the registration is fixed across calls, and INV-01 refuses a swapped registration first.

**INV-07 prediction domain.** «`pack` refuses any item above its derived worst case (P4)»; «Extra predictions are refused, not ignored (Sol 34 (d)).» [45/10 §Q3]
Predicate:
- `set(p) == set(g.role_to_model_id.values())`;
- for every `m`, `set(p[m])` equals the set of registered items;
- every value is a finite float with `0 < p[m][i] ≤ worst(m)`.

On the roster form, the same bound holds for every `predicted_item_s` entry of every initial block.
Paths: P (argument form); `E1`–`E9` and R (roster form).

**INV-08 prediction digest.** «Add registration field `predictions_sha256` (pilot-nullable, required in registered mode)»; «refuses when `canonical_json_sha256(predicted_decode_s restricted to the registered items)` ≠ `predictions_sha256`» [45/10 §Q3].
Predicate:
- `g.mode == "registered"` implies `g.predictions_sha256` is not null;
- if it is not null, `canon_sha(PRED_FORM(r)) == g.predictions_sha256`, where `PRED_FORM(r)` = `{m: {i: s}}` rebuilt from the `predicted_item_s` of the initial blocks (OP-08).

At `pack`, the same comparison runs against `p`.
Paths: ALL.

### C. Items, blocks and parents

**INV-09 level set and item identity.** «Opus S7 (`pack` requires the registered level set)» [08]; «`pack(registration, predicted_decode_s)` takes no items argument» [45/10 §Q3].
Predicate:
- `set(g.item_ids_by_level) == LEVELS`;
- every item id is a non-empty `str`;
- no item id repeats within or across levels;
- every block's `level` is in `LEVELS`, and every item in the block belongs to `g.item_ids_by_level[level]`.

Paths: ALL.

**INV-10 paired block membership.** «Block membership is identical across the two models, and block size is set per arm, not per model.» [19 §1 M8]
Predicate: for each level, the ordered list of item tuples of the parent blocks is identical for both models, and equals `BLOCKS(g, level)`. `BLOCKS` slices the registered order into consecutive pieces of `g.block_size[g.arm]` (c:scored_packer.py:234; OP-06). Parent `block_id` = `f"{model}:{arm}:{level}:{k}"` (c:scored_packer.py:243). Paths: ALL.

**INV-11 item conservation.** «item conservation (per model, every registered item is in exactly one block that is neither superseded nor terminal, and that block is in exactly one envelope, or is in exactly one terminal refusal and no envelope)» [45/21 §7(S)].
Predicate: for every model and every registered item `i`, exactly one of these holds:
- (a) exactly one block `b` contains `i`, with `b.superseded == false`, `b` not terminal (OP-25), and `b.block_id` in the `blocks` list of exactly one envelope;
- (b) `i` is in exactly one `terminal_refusals` entry, and every block containing `i` is absent from the `blocks` list of every envelope.

Paths: ALL.

**INV-12 parent identity of pieces.** «Pairing survives a split: singles carry `parent_block_id`, and the estimator pairs on the parent (Opus B2).» [08 F2(a)]; «A parent block is a block scheduled by the initial packing; single-problem blocks made from it under M12 are pieces of that parent, not new replicates.» [45/10 §Q4]
Predicate:
- `parent_block_id is None` if and only if `b.retry_stage ∈ {initial, whole_block}` (the block keeps its id through the whole-block retry, c:scored_packer.py:314-316);
- a single has exactly one item, and its parent exists, has the same model and level, contains that item, and is `superseded`;
- the singles of one parent partition the parent's items;
- a single's id is `f"{parent}:single:{k}"` (c:scored_packer.py:330).

Paths: `E4`, `E6`–`E9`, R. P and `E1`–`E3` are n/a because no single can exist before a split.

**INV-13 stage field.** «`retry_stage` is on every item row and flows into cells (Opus S6).» [08 F2(b)]
Predicate: every block has `retry_stage ∈ RETRY_STAGES`. Paths: ALL.

### D. Envelopes and placement

**INV-14 envelope model homogeneity.** «envelope model homogeneity» [45/21 §7(S)]; «every envelope's blocks share the envelope's model» [45/10 §Q2(1)].
Predicate: for every envelope `e`, every id in `e.blocks ∪ e.voided_block_ids` names a block with `model == e.model`, and `e.model` is one of the two model ids. Paths: ALL.

**INV-15 empty-envelope legality.** «An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope.» [45/21 §7(E)]
Predicate: `e.blocks == []` implies `e.kind == "idle_slot" or e.voided_block_ids != []`. Paths: ALL.

**INV-16 idle slots.** «An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster.» [08 F1]
Predicate:
- `e.kind ∈ {"loaded", "idle_slot"}`;
- `idle_slot` implies `blocks == []`, `voided_block_ids == []` and `observations is None`, and the slot never gains work later.

Paths: ALL.

**INV-17 grid.** «on a fixed-pitch grid in which idle slots are grid positions» [08 F1].
Predicate: envelope indices are distinct integers ≥ 0 that increase strictly in list order. Contiguity is OP-27. Paths: ALL.

**INV-18 fixed once observed; monotone placement.** «An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.» [45/21 §7(E)]
Predicate, on a transition `before → after` (§3), where the call's event reports envelope `k`:
- every envelope with `observations` not null in `before` is identical in `after`;
- every block id added to any envelope's `blocks` by the call sits at an index greater than `k`.

On a single roster: for every event `j`, each block placed by event `j` sits above that event's reporting envelope. This needs the event's placement record (OP-12).
Paths: `E1`, `E2`, `E4`, `E6`, `E7`, `E9`, R. The terminal-only edges `E3`, `E5` and `E8` need a witness only for the "fixed" half.

**INV-19 no reuse after split.** «The split stage never reuses the whole-block retry's envelope.» [45/21 §7(E)]
Predicate: no single of parent `B` sits in the envelope that holds `B`'s whole-block retry, either in `blocks` or in `voided_block_ids`. Paths: `E4`, `E6`, `E7`, `E9`, R.

### E. Capacity and reservations

**INV-20 capacity.** «capacity by `reserved_s`» [45/21 §7(S)]; «capacity per envelope» [45/10 §Q2(1)].
Predicate: for every envelope, `Σ reserved_s ≤ cap` over the blocks placed there. "Placed" means `blocks ∪ voided_block_ids` (OP-21). Paths: ALL.

**INV-21 initial reservation.** This row carries over c0998fdb behaviour; the reservation of initial blocks is unruled (OP-22). For an initial parent: `predicted_s == Σ predicted_item_s` (c:scored_packer.py:239-240), and `reserved_s == predicted_s`. Paths: ALL.

**INV-22 whole-block retry.** «The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged.» [45/21 §7(W)]
Predicate, for every block with `retry_stage == "whole_block"`:
- `reserved_s == min(len(items) × worst(m), cap)`;
- `predicted_s` equals the value it had as an initial block;
- the envelope holding it (active or voided) holds no other block id;
- that envelope's index is above every index present before the event that created the retry.

Paths: `E1`, R.

**INV-23 single reservation.** «Each single is packed at `reserved_s = predicted_s = the item's derived worst case`.» [45/21 §7(T)]; M12 amendment: «never by the prediction that already failed» [08].
Predicate: every single has `reserved_s == predicted_s == worst(m)`. Paths: `E4`, `E6`, `E7`, `E9`, R.

### F. Spread (M8 by parent) and minima

**INV-24 M8 by parent.** «No two parent blocks of one cell share an envelope at any stage, initial or retry.» [45/10 §Q4]
Predicate: for every envelope and every level, the parents (a parent block itself, or the `parent_block_id` of a single) of the placed blocks with that level are pairwise equal. The model is already homogeneous by INV-14.
Non-violation witness, which the checker must accept: «Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity.» [45/10 §Q4]
Paths: ALL.

**INV-25 pack-time minima.** «The five-block and five-envelope minima count parent blocks and the distinct envelopes holding their executed windows; a split never adds to either count.» and «Before capture the same shortfall is a packing refusal.» [45/10 §Q4]
Predicate, on a root roster (`events == []`): every cell `(m, level)` has at least `MIN_PARENT_BLOCKS` (5) parents in at least `MIN_ENVELOPES` (5) distinct envelopes. Paths: P, R (root roster).

**INV-26 post-capture spread status.** «A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them,» with the cause amended by (X) to «for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)» [45/10 §Q4; 45/21 §7(X)].
Predicate:
- for every cell, `spread_exceeded(m, level) == (live_parents < 5 or env_count < 5)`, where `live_parents` = parents none of whose items is in a terminal refusal, and `env_count` = distinct envelopes holding their active blocks (OP-24);
- after capture the call never raises for this.

Paths: `E1`–`E9`, R.

### G. Drift (parent unit)

**INV-27 drift lever.** «The drift lever of a level is the absolute difference, in envelope slots, between the mean position of its 8B parents and the mean position of its 1.7B parents. A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing.» [45/10 §Q4]; «One function, the §Q4 parent-unit definition, on both paths.» [45/10 §Q5 N2]; «`requeue_overrun` recomputes `drift_lever_slots`.» [21/10 §Q2 D5b]
Predicate: `r.drift_lever_slots[level] == |mean_P8(pos) − mean_P17(pos)|`, where `pos(parent)` is defined in §2.0. The value is null when either model has no positioned parent at that level (OP-23). Paths: ALL.

**INV-28 drift threshold.** «register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows.» [21/10 §Q2 D5b]; «Formula at `scored_registration.py:169-170` becomes the definition; the field is removed.» [45/10 §Q3]
Predicate:
- registered mode at `pack` refuses if any `drift_lever_slots[level] > max_gap(g)` (c:scored_packer.py:258-261);
- after any event, `r.drift_exceeded[level] == (gap is None or gap > max_gap(g))` (c:scored_packer.py:369-377);
- in pilot mode every flag is false and nothing refuses.

Refuse-versus-flag after capture is OP-23. Paths: ALL.

### H. Observations and transitions

**INV-29 observation record.** «`requeue_overrun` at the initial and whole-block stages takes, for every block in the reporting envelope, an observation: `completed` with elapsed seconds, `cut_off` with elapsed seconds, or `not_started`; the envelope records every observation.» [45/21 §7(W)]; «At the single stages the observation per single is `completed`, `cut_off` or `not_started`, with elapsed where applicable.» [45/21 §7(N)]
Predicate: for each event, the observations cover the reporting envelope's pre-call `blocks` exactly: one observation per block, no extra and no missing. Each observation has:
- `status ∈ {completed, cut_off, not_started}`;
- `elapsed_s` a finite float > 0 if and only if the status is not `not_started`, and null otherwise.

The reporting envelope's `observations` equals the event's `observations`.
Paths: `E1`–`E9`, R.

**INV-30 culprit and late (initial and whole-block stages).** «A completed block keeps its window; if its elapsed exceeds its `predicted_s` it is marked `late: true` and is a culprit. An uncompleted block whose elapsed exceeds its `predicted_s` is a culprit and advances one stage.» [45/21 §7(W)]
Predicate, per observation `o` on a block `b` at stage `initial`:
- `completed` means `b` stays in the envelope's `blocks`, and `b.late == (o.elapsed_s > b.predicted_s)`;
- `cut_off` with `elapsed_s > predicted_s` means `b` is advanced to `whole_block` (INV-22);
- culprit(envelope) = at least one observation has `elapsed_s > predicted_s`.

The whole-block stage is OP-14.
Paths: `E1`, `E2`, `E3`, R.

**INV-31 innocents and unattributed overrun.** «An uncompleted or not-started non-culprit is rescheduled at its current stage without advancing, provided the envelope holds a culprit. If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun` (a `terminal_refusals` entry; its cell is unresolved until a registered recapture); the call never raises for innocence.» [45/21 §7(W)]
Predicate:
- when the envelope holds a culprit, every uncompleted non-culprit keeps `retry_stage`, is voided in `k`, and is active at an index above `k`;
- when it holds none, every uncompleted block is voided in `k`, is in no envelope's `blocks`, and each of its items has one `terminal_refusals` entry of type `unattributed_overrun` (OP-25);
- the call returns a sealed roster and does not raise.

Paths: `E2`, `E3`, `E5`, R.

**INV-32 split trigger.** «A whole-block retry advances to the split stage when its attempt did not complete within its envelope; its observed elapsed is recorded.» [45/21 §7(T)]
Predicate: a whole-block retry observed `cut_off` becomes `superseded == true`. Its singles (INV-12, INV-23) are created, and no innocence test applies (A5: «no innocence test applies»). `not_started` is OP-14. Paths: `E4`, R.

**INV-33 single-stage advance.** «A single whose elapsed exceeds its derived worst case advances (`single_problem` → `single_retry` → `ceiling_violation`).» [45/21 §7(N)]
Predicate:
- a single with `elapsed_s > worst(m)` at `single_problem` moves to `single_retry` and is placed as INV-34 requires;
- at `single_retry` it moves to `ceiling_violation`: it is voided, removed from every `blocks` list, and gets one `terminal_refusals` entry of type `ceiling_violation`.

A completed single above its worst case is OP-15. Paths: `E6`, `E8`, R.

**INV-34 single reschedule placement.** «Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one.» [45/21 §7(N)]
Predicate: the target envelope is the lowest-index envelope `e` with `e.index > k` that is eligible and non-fixed (OP-18), that keeps INV-14, INV-20 and INV-24 after insertion, and that is not an `idle_slot`. If none exists, the target is a new envelope appended at the end. Paths: `E6`, `E7`, `E9`, R.

**INV-35 innocent-reschedule bound.** «Each innocent reschedule is caused by one culprit event in its envelope and each item has at most two culprit events, so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it.» [45/21 §7(N)]
Predicate: `count(single-stage reschedules in events) ≤ 2 × count(single blocks)` (OP-16, OP-20). Paths: `E7`, `E9`, R.

**INV-36 stage legality.** «stage legality (each block's `retry_stage` history follows the closed edge list in (G))» [45/21 §7(S)]. The closed edge list reads «initial→whole_block, initial→reschedule, initial→unattributed_overrun, whole_block→single_problem, whole_block→unattributed_overrun, single_problem→single_retry, single_problem→reschedule, single_retry→ceiling_violation, single_retry→reschedule» [45/21 §7(G)].
Predicate:
- every decision recorded in `events` is one of these edges, applied to the block's stage at that moment;
- `whole_block→single_problem` acts on the parent, and its singles start at `single_problem`;
- a root roster has every block at `initial` and `attempt == 0`;
- `attempt` rises by exactly 1 per placement (c:scored_packer.py:315, 364).

Paths: ALL, where P is witnessed by a root roster carrying a non-initial block.

**INV-37 typed terminals.** «The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).» [08 F2(c)]; «The reducer passes `terminal_refusals` through typed» [21/10 §Q2 D5c].
Predicate:
- every entry has `type ∈ {"ceiling_violation", "unattributed_overrun"}` and the §2.6 keys;
- `(model, item_id)` is unique;
- the entry's block exists, contains the item, and is in no envelope's `blocks`.

Paths: `E3`, `E5`, `E8`, R.

### I. Replay and structure

**INV-38 event log.** «The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`).» [45/21 §7(R)]
Predicate:
- on a transition: `after.events[:-1] == before.events` and `len(after.events) == len(before.events) + 1`, with `after.events[-1].sha256` per OP-12;
- `after.registered_sha256 == (before.registered_sha256 or before.sha256)`;
- on a single roster: `events == []` if and only if `registered_sha256 is None`.

Paths: `E1`–`E9`, R.

**INV-39 root replay (seal/reduce only; not the checker).** «`reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]`, replays every event from the root, and refuses unless the final digest matches its input roster.» [45/21 §7(R)]
Predicate: replay equality. The checker cannot evaluate it without `pack` (§3). Paths: R, plus the witness "a forged roster with a recomputed digest is refused" (45/21 PF).

**INV-40 seal placement (structural AST test; not a checker predicate).** «`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`.» [45/21 §7(S)]; «`_seal(registration, roster)` is the ONLY caller of `_digest`» [45/10 §Q2(1)].
The witness is an AST test plus one guard-deletion mutant per seal call site.

### Out of A291 scope (consumer lane owns the predicate)

| Ruled invariant | Source | Consumer |
|---|---|---|
| Crossover L\*, the three-way status rule, licensing, reverse order, the gap sentences, NE(`ceiling_violation`), sparse levels, Holm, the per-replicate bootstrap bound | 08 Crossover; 21/10 Q1, D5a; 21/11 R3–R7 | A293 estimator |
| NE precedes `spread_exceeded`; a level with `spread_exceeded` and no NE is NR (`spread_exceeded`) | 45/21 §7(P) | A293 |
| Drift exceedance maps to NR(`drift_exceeded`) | 21/11 R11, adopted by brief 26 G3 | A293 |
| Idle slot never enters a numerator (M7) | 08 F1 | A292 reducer |
| Terminal window accepted, recorded as `gross_j`, never summed | 45/10 §Q5 F3 | A292 |
| Cap derived from `generated_tokens ≥ cap_tokens`; `stop_reason` required; windows keyed `(block_id, attempt)`; row/refusal completeness; rows and windows carry `scorer_id` and both digests | 21/11 R9; 45/10 §Q3 last row | A292 |
| Paired drop-retried sensitivity analysis, labelled selection-confounded | 08 F2(d) | A293 / AP-5M lane |
| Kill timeout = `ceiling_s`; capture timing; sizing-receipt digest comparison | 45/10 §Q2 CARRIED table; 45/21 §7(G) | runner lane / arm gate |

---

## 2. Data contract

### 2.0 Definitions

- `cap := interior_s − guard_s` (c:scored_registration.py:129; c:scored_packer.py:219).
- `worst(m) := cap_tokens[arm] × s_per_token_upper[m][arm] + prefill_s[m][arm]`, per item, for the selected arm (c:scored_registration.py:157; the same expression appears at c:scored_packer.py:309-311, 322-324 and 353-355). `worst(m,a)` is the same with arm `a`. For a block, the worst case is `len(items) × worst(m)` (c:scored_packer.py:309-311).
- `n(g) := len(item_ids_by_level[L])`, which must be common to all levels (OP-05).
- `bpc := ceil(n(g) / block_size[arm])` (c:scored_registration.py:169).
- `max_gap(g) := budget_j / (delta_upper_j_per_block_slot × bpc)` (c:scored_registration.py:170). It is undefined, and no drift check runs, when either input is null (pilot mode).
- `canon_sha(v) := sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()`. c0998fdb has no function by this name; it inlines this form at c:scored_registration.py:96+179 and c:scored_packer.py:27-32. `ensure_ascii` keeps its default (True). See OP-07.
- `pos(parent)` = the mean, over the parent's items that are not terminal, of the `index` of the envelope whose `blocks` currently holds that item's active block. Voided placements and idle slots contribute nothing, and neither do terminal items (OP-23). A parent with no such item has no position.
- `mean_Pm` = the unweighted mean of `pos` over model `m`'s positioned parents at the level.
- `LEVELS = [1,2,3,4,5]`; `RETRY_STAGES = ["initial","whole_block","single_problem","single_retry","ceiling_violation"]` (c:scored_registration.py:26); `MIN_PARENT_BLOCKS = MIN_ENVELOPES = 5`.

### 2.1 Registration mapping (exact key set; 29 keys)

| Key | Type / domain | Status | Source |
|---|---|---|---|
| `schema` | `"joulewise.scored_registration.v2"` (OP-33) | registered | c:scored_registration.py:101 (v1); 45/10 §Q3 row 1 |
| `mode` | `"pilot"` \| `"registered"` | registered | c:…:104-105 |
| `registration_id`, `plan_id` | non-empty str | registered | c:…:99-100 |
| `sizing_receipt_sha256` | sha256 hex; null only in pilot | registered | c:…:106-110 |
| `arm` | non-empty str, a key of `arm_to_family` | registered | c:…:133 |
| `arm_to_family` | non-empty `{str: non-empty str}` | registered | c:…:132-137 |
| `role_to_model_id` | exactly `{"8B": str, "1.7B": str}`, values distinct | registered | c:…:138-143 |
| `alpha` | number, 0 < α ≤ 1 | registered | c:…:123-125 |
| `n_boot` | int ≥ 1 | registered | c:…:121 |
| `seed` | int ≥ 0 | registered | c:…:121-122 |
| `floor_j`, `anchor_j` | number ≥ 0 | registered | c:…:123 |
| `cap_tokens`, `block_size` | `{arm: int ≥ 1}`, keys = arms of `arm_to_family` | registered | c:…:144-148 |
| `item_ids_by_level` | `{"1".."5": [non-empty str, …]}`, globally distinct, equal lengths (OP-03, OP-05) | registered, NEW | 45/10 §Q3 row 2 |
| `envelope_s`, `interior_s`, `pitch_s` | number > 0; `pitch_s ≥ envelope_s` | registered | c:…:123-131 |
| `offset_s`, `guard_s` | number ≥ 0; `offset_s + interior_s ≤ envelope_s` | registered | c:…:123-128 |
| `s_per_token_upper`, `ceiling_s` | `{model_id: {arm: number > 0}}` | registered | c:…:149-154 |
| `prefill_s` | `{model_id: {arm: number ≥ 0}}` | registered | c:…:149-154 |
| `delta_upper_j_per_block_slot` | number > 0; null only in pilot | registered | c:…:160-166 |
| `budget_j` | number ≥ 0; null only in pilot | registered | c:…:160-166 |
| `declared_sensitivities` | non-empty list of non-empty str | registered | c:…:173-176 |
| `scorer_id` | non-empty str | registered | c:…:99-100 |
| `predictions_sha256` | sha256 hex; null only in pilot | registered, NEW | 45/10 §Q3 row 7 |

Removed from the c0998fdb `_FIELDS` (c:scored_registration.py:15-25):
- `levels`, `merge_order`, `min_correct`, `holm_m`, `cap_bound_fraction`, `retry_stages`, `min_blocks_per_cell`, `min_envelopes_per_cell` become module constants (45/10 §Q3 row 1; OP-02);
- `n_per_level` and `item_set_sha256` become derived roster fields (row 2);
- `max_drift_lever_slots` becomes the `max_gap` definition (row 3).

`registration_sha256 := canon_sha(mapping)`, taken over the entire mapping, CARRIED fields included (c:scored_registration.py:96, 179).

### 2.2 `predicted_decode_s` (the argument to `pack` and `reduce`)

`{model_id: {item_id: float}}` with exactly the two model ids and exactly the registered items for each (INV-07). Each float satisfies `0 < v ≤ worst(m)`.

### 2.3 Roster top level (exact key set)

| Key | Type | Status | Source |
|---|---|---|---|
| `schema` | `"joulewise.scored_roster.v3"` (OP-33) | recorded constant | c:scored_packer.py:262 (v2) |
| `registration_sha256` | sha256 hex | recorded | 45/10 §Q2(1) |
| `claim_ready` | bool | derived | 21/10 D4 (OP-10) |
| `item_set_sha256` | sha256 hex | derived | 45/10 §Q3 |
| `n_per_level` | int | derived | 45/10 §Q3 |
| `blocks` | list[Block] | recorded | c:…:243-246 |
| `envelopes` | list[Envelope], in index order | recorded | c:…:110-117 |
| `terminal_refusals` | list[TerminalRefusal] | recorded | c:…:269, 360-362 |
| `events` | list[Event] | recorded, NEW | 45/21 §7(R) |
| `drift_lever_slots` | `{"1".."5": float \| null}` | derived | 08 F1; 45/10 §Q4 |
| `drift_exceeded` | `{"1".."5": bool}` | derived | c:…:267, 369-377 (OP-23) |
| `spread_exceeded` | `{model_id: {"1".."5": bool}}` | derived, PROPOSED | 45/10 §Q4 / (X) (OP-24) |
| `registered_sha256` | sha256 hex \| null (null if and only if `events == []`) | recorded | c:…:268, 291-292; 45/21 §7(R) |
| `sha256` | sha256 hex = `canon_sha(roster − "sha256")` | recorded | c:…:27-32 |

Dropped from c0998fdb `ROSTER_KEYS` (c:scored_packer.py:149-152):
- `models`, `arm`, `block_size`, `interior_s`, `guard_s`, `cap_tokens_by_arm`, `envelope_s`, `offset_s`, `pitch_s`, `capacity_s`, `levels` (INV-03);
- `parent_sha256`, which is superseded by `events` (OP-13).

### 2.4 Block

| Key | Type | Status | Source |
|---|---|---|---|
| `block_id` | str. Parent: `"{model}:{arm}:{level}:{k}"`; single: `"{parent}:single:{j}"` | recorded | c:…:243, 330 |
| `model` | model id | recorded | c:…:243 |
| `level` | int in LEVELS | recorded | c:…:244 |
| `items` | list[str] (singles: length 1) | recorded | c:…:244, 330 |
| `predicted_item_s` | list[float], aligned with `items` | recorded from `p` | c:…:245, 332 |
| `predicted_s` | float. Initial: Σ `predicted_item_s`; whole_block: unchanged; single: `worst(m)` | derived | c:…:240; 45/21 (W), (T) |
| `reserved_s` | float (INV-21 to INV-23) | derived, NEW | 45/21 (W), (T); §8 M5 |
| `attempt`, `origin_attempt` | int ≥ 0 | recorded | c:…:245, 333 |
| `retry_stage` | str in RETRY_STAGES | recorded | 08 F2(b) |
| `parent_block_id` | str \| null | recorded | 08 F2(a) |
| `superseded` | bool | recorded | c:…:246, 320 |
| `late` | bool | recorded, NEW | 45/21 (W); §8 M5 |

Dropped: `arm` (a copy; OP-10) and `ceiling_violation` (derivable from `retry_stage`; OP-25).

### 2.5 Envelope

| Key | Type | Status | Source |
|---|---|---|---|
| `index` | int ≥ 0 | recorded | c:…:114-117 |
| `model` | model id | recorded | c:…:114-117 |
| `kind` | `"loaded"` \| `"idle_slot"` | recorded | 08 F1; c:…:114 |
| `blocks` | list[str], active block ids | recorded | c:…:117 |
| `voided_block_ids` | list[str] | recorded | c:…:249, 303 |
| `observations` | list[Observation] \| null (null until observed) | recorded, NEW | 45/21 (W); §8 M5 |

Dropped: `predicted_s` and `retry_tail` (both derivable; OP-21).

**Observation**:
- `block_id`: str.
- `status`: `"completed"` \| `"cut_off"` \| `"not_started"`.
- `elapsed_s`: float > 0, or null if and only if `not_started`.
- Proposed `decision`: `"keep"` \| `"advance"` \| `"reschedule"` \| `"split"` \| `"unattributed_overrun"` \| `"ceiling_violation"` (OP-11).

Sources: 45/21 (W), (N).

### 2.6 Event and TerminalRefusal

**Event** (45/21 §7(R)):
- `block_id` (OP-12);
- `observations`: list[Observation], equal to the reporting envelope's `observations`;
- `sha256` (OP-12);
- proposed `envelope_index`: int.

**TerminalRefusal** (c:scored_packer.py:157, 360-362):
- `type`: `"ceiling_violation"` \| `"unattributed_overrun"` (the new type comes from 45/21 (W));
- `block_id`, `parent_block_id`, `item_id`, `model`, `level`;
- proposed `attempt`, for A292's F3 window join (OP-25).

`arm` is dropped.

### 2.7 Digest chain

1. `registration_sha256 = canon_sha(registration mapping)`.
2. Root roster: `pack(g, p)` yields `events == []` and `registered_sha256 == null`, with `sha256 = canon_sha(root − sha256)`. The output is deterministic (45/21 PA).
3. Each `requeue_overrun` appends one event and sets `registered_sha256 = input.registered_sha256 or input.sha256`. `event.sha256` follows OP-12, and `sha256` covers the whole roster, events included.
4. `predictions_sha256` binds `p`; `item_set_sha256` binds the item set; both are defined in §2.0 and §2.1.

---

## 3. Checker interface

Module name, proposed: `tests/support/scored_roster_checker.py`. It sits outside the implementer's WRITE_SCOPE (45/21 §7(G)). A different seat commits it before implementation starts.

```python
@dataclass(frozen=True)
class Violation:
    inv: str       # "INV-11"
    where: str     # e.g. "envelopes[12].blocks[0]"
    detail: str

def check_roster(registration: Mapping, roster: Mapping,
                 predicted_decode_s: Mapping | None) -> list[Violation]: ...
def check_transition(registration: Mapping, before: Mapping, after: Mapping,
                     predicted_decode_s: Mapping | None) -> list[Violation]: ...
```

- **Pure functions.** Neither function raises on bad data. Each returns every violation, sorted by `(inv, where)`. The registration arrives as a plain mapping (§2.1), never a `Registration` object. The checker re-derives `cap`, `worst`, `bpc`, `max_gap` and `canon_sha` itself.
- **What `check_roster` covers.** INV-01–17, INV-19–35 and INV-37, on a single roster. From INV-38 it checks only the single-roster clause. INV-18 is covered only through the per-event placement record (OP-12).
- **What `check_transition` covers.** INV-18 (fixedness and monotone placement), INV-38 (append-only, one event per call, `registered_sha256` chaining), and the edge legality and decision re-derivation of INV-30 to INV-36 for the single new event, by comparing `before` with `after`.
- **Imports.** Stdlib only: `dataclasses`, `hashlib`, `json`, `math`, `typing`, `collections`. It never imports `joulewise.scored_packer`, `joulewise.scored_registration` or `joulewise.scored_reduce`, and it imports nothing else from `joulewise`.
- **No shared canonical-JSON helper.** Main carries three `canonical_json_sha256` functions, and none of them fits:
  - `joulewise/identity_pins.py:210` uses `ensure_ascii=False` and imports `joulewise.provenance` and `joulewise.schemas`;
  - `joulewise/benchmark_import_math.py:47` lacks `allow_nan=False` and imports `joulewise.benchmark_import`;
  - `joulewise/dominance_closeout.py:491` imports the analysis engine.

  Each differs from c0998fdb's form or pulls in project modules, so the checker carries its own `canon_sha` (§2.0). A test outside the checker, which may import both, asserts byte-equality between the packer's and the checker's digests on the fixtures.
- **Replay (R).** The checker cannot call `pack`: §7(G) bars it from importing the packer. Full root equality and event replay (INV-39) are therefore the job of the seal at `reduce` entry and of `reduce` itself (45/21 §7(R)). The checker verifies structure and chaining through INV-38, and checks each event's recorded decisions against the ruled rules (INV-30 to INV-36).
- **Stress harness.** The test module, which may import both, runs `pack`, then seeded random observations, then `requeue_overrun`, repeatedly. It calls `check_roster` on every roster and `check_transition` on every call. The criterion is zero violations (45/10 §Q2 gate text).
- **Validating the checker first.** Before any packer exists, the checker's own tests supply one hand-built violating roster per INV. These can double as the entry-injection witnesses (OP-28).

---

## 4. Open points (texts silent or ambiguous)

Each point gives the question, the candidate readings, my recommended pick with its reason, and the texts that bear on it.

**Inconsistencies found in the rulings**

- **OP-01. Constants with no CARRIED home.** §7(G) says every ruled constant must be CONSUMED or in the closed CARRIED list. That list names only fields (45/10 §Q2 table, plus the three timing fields). `merge_order`, `min_correct`, `holm_m` and `cap_bound_fraction` cannot be consumed by registration and packer code.
  - Readings: (a) the constants live in their consumer modules (A293, A292) and fall outside A291's sweep; (b) a cold-gate addendum adds them to CARRIED.
  - Pick: (b). The CARRIED list is ruled "closed", and (a) is a seat reading of a closed list. This is **internally inconsistent**.
- **OP-10. `claim_ready` versus "roster carries only `registration_sha256`".** 21/10 D4 rules a roster flag that is a function of `mode`. The later text, 45/10 §Q2(1), bars copies. Block `arm` and c0998fdb's `capacity_s` raise the same question.
  - Pick: keep `claim_ready` as a derived flag, checked by INV-05, because it is explicitly ruled and consumers must refuse on it. Drop block `arm` and `capacity_s`. **Ambiguity between rulings**: the magistrate should confirm.
- **OP-14. Whole-block stage: (W) versus (T).** (W) says it applies «at the initial and whole-block stages», with a culprit test and `unattributed_overrun` when there is no culprit. (T) and A5 say a whole-block retry splits on non-completion and «no innocence test applies». The edge list has `whole_block→unattributed_overrun` but no `whole_block→reschedule`.
  - Pick: for a whole-block retry, `cut_off` (any elapsed) takes E4; `not_started` takes E5 (no culprit and no elapsed, a fault signal per 45/21 N1); `completed` keeps its window, with `late` per (W). **Internally inconsistent**, so it needs a ruling.

**Registration and derivation**

- **OP-02. Constants: removed or asserted?** Should the constants stay as Registration fields asserted equal, as c0998fdb does (c:scored_registration.py:111-120), or be removed? Pick: remove them. 45/10 §Q3 row 1 says «Module constants pinned by `schema`», and 44 Q3 reads «a field that may hold only one value carries no information».
- **OP-03. JSON key type for level-keyed maps.** Keys are JSON strings. c0998fdb used int keys in memory (c:scored_packer.py:221, 266-267), and `Registration.__getattr__` returns `json.loads` output with str keys (c:scored_registration.py:73). Pick: str keys `"1".."5"` everywhere, and refuse int keys, so that the JSON round-trip is the identity.
- **OP-04. The `item_set_sha256` preimage.** «[ids in level order]» could be a flat list or a list of lists. A flat list loses the level boundaries if lengths ever differ. Pick: `[[ids of level 1], …, [ids of level 5]]`, each level in its registered order.
- **OP-05. `n_per_level` and short blocks.** Should unequal level lengths be refused? Is a short last block allowed? Pick: refuse unequal lengths, because `bpc` and `n_per_level` are single numbers (c:scored_registration.py:169). Allow a short last block, as c0998fdb's slicing does (c:scored_packer.py:234); the paired membership of INV-10 is unaffected. Note that `bpc` counts it as a block.
- **OP-06. Block formation rule.** This is unruled; it carries over c0998fdb's consecutive slicing in registered order and its `block_id` formats. Pick: keep it and state it in the brief, so that the checker and the packer do not choose independently.
- **OP-07. Canonical form and numeric types.** Canonical JSON writes `5` and `5.0` differently, and c0998fdb stores `float(value)` (c:scored_packer.py:42). An int prediction would therefore hash differently from its roster form. Pick: predictions must be `float`, and ints are refused. The digest uses the §2.0 form.
- **OP-08. How the seal checks `predictions_sha256`.** `_seal(registration, roster)` has no predictions argument. Pick: rebuild `{m: {i: s}}` from the initial blocks' `predicted_item_s`. In pilot mode with a null field, skip the check; with a non-null field, enforce it.
- **OP-09. "Restricted to the registered items" versus "extra predictions refused".** With extras refused, the restriction does nothing. Pick: refuse extras, both extra model keys and extra items, and hash the full mapping. The outer keys are model ids, not roles.
- **OP-30. Per-arm entries for unselected arms.** Entries such as `cap_tokens[a]` and `block_size[a]` for `a ≠ arm` are carried without effect. `worst(m,a)` for those arms is consumed only by the registration's coherence check, which is validation-only under §7(G). Pick: restrict the per-arm maps to the selected arm, or get these entries ruled CARRIED.

**Roster representation**

- **OP-11. Where `late`, stage history and decisions live.** Pick: `late` goes on the Block, because (W) says «it is marked». Stage history is derived from `events`. Each observation carries the `decision` that was taken, so the seal and the checker can re-derive and compare it (45/21 A1: «observations are recorded so the seal and checker re-derive the decision»).
- **OP-12. Event semantics.** Which `block_id` does an event name when an envelope holds zero or several culprits? And `sha256` cannot cover the event that contains it.
  - Pick: `block_id` = the first block in the reporting envelope's pre-call `blocks` order, plus `envelope_index` and a `placements` list (`block_id`, then `index`).
  - `event.sha256` = the digest of the resulting roster with that event's `sha256` set to null and the top-level `sha256` removed.
- **OP-13. Root `registered_sha256`; `parent_sha256`.** Pick: the root carries null (c:scored_packer.py:268), and `reduce` on a root roster compares the root's own `sha256` with `pack(...)`. Drop `parent_sha256`, which is redundant with `events`.
- **OP-21. Capacity basis.** Does capacity count active blocks only, or active and voided? Pick: every block placed there, active and voided. A fixed envelope cannot change, so this also keeps the reservation that was in force when the envelope ran. Drop the envelope `predicted_s` and `retry_tail` (derivable).
- **OP-24. `spread_exceeded`.** The texts say «The cell carries» it; §8 M5 does not list it as a roster key. The rulings also leave open what a «counted window» means before capture, and how to count envelopes when «a split never adds».
  - Pick: a derived roster map checked by the seal, with A292 copying it into cells. A pending (not yet run) active block counts as a future counted window.
  - `env_count` = the number of live parents that hold at least one active block in an envelope. M8-by-parent makes the parents' envelope sets disjoint, so this equals `min(live_parents, distinct envelopes)` and never grows with a split.
- **OP-25. Terminal representation.** Pick: one `terminal_refusals` entry per item, including for a multi-item `unattributed_overrun` block. A block is "terminal" when all of its items are in refusals. Add `attempt` for A292's window join.
- **OP-26. Idle-slot model and insertion.** c0998fdb inserts one idle slot only when both models have an odd envelope count, and assigns it `models[1]` (c:scored_packer.py:65-66, 111-114). 08 F1 speaks of «its model worker», which implies the slot belongs to a model that lacks a position. Pick: keep c0998fdb's rule and state it, pending a magistrate ruling. Treat balance as an objective, not a hard equality: 08 F1 records the residual gap.
- **OP-27. Index contiguity.** Pick: indices are `0..N−1`, equal to list position. "Grid position" implies every index is a capture, and the placement text assumes appended envelopes take the next index.
- **OP-33. Schema strings.** Pick: `joulewise.scored_registration.v2` and `joulewise.scored_roster.v3`.

**Transitions**

- **OP-15. A completed single above its worst case.** Does it advance and re-run, or keep its window? Is it `late`? Is it a culprit for its mates? Pick: it keeps its window, is marked `late`, and advances. Exceeding the derived bound is a physical falsification (21/11 R6), so it takes E6 or E8, and its window is voided. It counts as a culprit. Magistrate ruling needed.
- **OP-16. A single-stage envelope with no culprit.** There is no single→unattributed edge. Pick: reschedule every uncompleted single, and let the INV-35 bound refuse at the seal. Note that a refusal there raises; 45/21 N1 already treats this as instrumentation failure.
- **OP-17. Initial-stage innocent reschedule.** Neither the placement nor a bound is ruled; the 45/11 NIT's «≤ 2 × (block_size − 1)» was not adopted. Pick: apply (N)'s placement rule with M8-by-parent and `reserved_s = predicted_s`. Leave it unbounded beyond "one culprit per event", and flag it for the cold gate. (X)'s «a rescheduled parent the seal cannot place» is unreachable under this pick, because a fresh envelope always exists.
- **OP-18. Eligible placement targets.** Pick: never an `idle_slot` (INV-16); never the envelope of a whole-block retry, which is «alone»; pack-time envelopes and single tails above `k` are allowed if not fixed.
- **OP-19. Reporting order.** Must events report non-decreasing envelope indices, with every envelope at or below the latest reported index treated as run? Otherwise a late report could place work into an envelope that has already run without an overrun, since no observation was recorded on it. Pick: yes. Events must have strictly increasing `envelope_index`, and placement must be above the maximum reported index. Needs a ruling: it strengthens (E).
- **OP-20. "Number of singles" in (N).** Pick: the total number of single blocks ever created in the roster, across models, counted at the time of the seal.
- **OP-22. Initial `reserved_s`.** This is unruled. Pick: `reserved_s = predicted_s`, as c0998fdb packs initial blocks by prediction (c:scored_packer.py:133). A reschedule keeps its `reserved_s`.
- **OP-23. Drift details.**
  - Items still pending use their scheduled envelope's index.
  - Terminal items contribute nothing, and a parent with no position is excluded.
  - A level with no positioned parent for a model gives `null`, and then `drift_exceeded` is true (c:scored_packer.py:375-376).
  - Comparing a recorded value with its re-derivation uses `math.isclose(rel_tol=1e-9)`, but the threshold test uses the checker's own value.
  - After capture: flag, never refuse (brief 26 G3, adopting 21/11 R11). Pilot: no flags.
  - The "seal checks drift by parent" text does not say refuse or flag, so the magistrate should confirm.
- **OP-31. Plausibility of observations.** Should the checker enforce sequential execution within an envelope (completed*, at most one cut_off, then not_started*), and `elapsed_s ≤ cap` for a cut-off? Pick: enforce both as checker warnings, not INV rows, because this is unruled.

**Gate mechanics and lanes**

- **OP-28. "Every path" for invariant rows.** Some (INV, path) pairs are unreachable, for example single-parent identity on P. Entry injection makes all nine edges the same witness, which is vacuous.
  - Pick: each applicable path needs an exit witness, in which an internal helper is patched to emit the violation on that edge and the seal refuses. Add one entry-injection witness per INV at requeue entry and at reduce entry.
  - Unreachable cells are "n/a" with a reason reviewed by the contract lens, mirroring the rule for fields.
- **OP-29. Ownership of `reduce`.** `reduce` is in A291's path list, yet the reducer is lane A292. Pick: A291 ships a public `verify_executed_roster(registration, roster, predicted_decode_s)` that performs the seal plus replay. A291's R-path witnesses run against it, and A292's `reduce` must call it first. A292's gate carries this.
- **OP-32. Checker location and registration checks.** Pick: `tests/support/`. The checker also re-checks INV-06 on the registration mapping.
- **OP-34. Refuter-only cures.** 21/11 R11 and R13 bind only through brief 26. R13 is superseded by (N); R11 still stands as the source for `drift_exceeded`. Confirm R11.

---

## 5. Field-row seed (for the seat's witness rows)

CONSUMED: the seat must give an executed boundary witness on every applicable path. CARRIED: the closed list of 45/10 §Q2 plus the §7(G) additions.

| Field / constant | Proposed status | Consumer or where it is consumed |
|---|---|---|
| `schema`, `registration_id`, `plan_id` | CONSUMED (identity) | INV-01 digest refusal (45/10 §Q2) |
| `mode` | CONSUMED | INV-05, INV-08 nullability, INV-28 drift refusal |
| `sizing_receipt_sha256` | CARRIED | scored-night arm gate (runner lane) |
| `arm` | CONSUMED | block ids, `worst`, `bpc` (INV-10, INV-22, INV-23) |
| `arm_to_family` | CARRIED | A293 estimator (family) |
| `role_to_model_id` | CONSUMED | model set (INV-07, INV-10, INV-14) |
| `alpha`, `n_boot`, `seed`, `floor_j`, `anchor_j`, `declared_sensitivities` | CARRIED | A293 estimator |
| `cap_tokens` | CONSUMED (selected arm only; OP-30) | `worst` (INV-07, INV-22, INV-23, INV-33) |
| `block_size` | CONSUMED | INV-10, `bpc` (INV-28) |
| `item_ids_by_level` | CONSUMED | INV-04, INV-09 to INV-11 |
| `interior_s`, `guard_s` | CONSUMED | `cap` (INV-20, INV-22) |
| `envelope_s`, `offset_s`, `pitch_s` | CARRIED | runner lane (45/21 §7(G)) |
| `s_per_token_upper`, `prefill_s` | CONSUMED | `worst` |
| `ceiling_s` | CARRIED | runner lane kill timeout; INV-06 is validation-only |
| `delta_upper_j_per_block_slot`, `budget_j` | CONSUMED (registered mode) | `max_gap` (INV-28) |
| `scorer_id` | CARRIED | A292 reducer and runner |
| `predictions_sha256` | CONSUMED | INV-08 |
| Constant `LEVELS` | CONSUMED | INV-09 |
| Constant `RETRY_STAGES` (and the edge list) | CONSUMED | INV-13, INV-36 |
| Constant `MIN_PARENT_BLOCKS` = 5 | CONSUMED | INV-25, INV-26 |
| Constant `MIN_ENVELOPES` = 5 | CONSUMED | INV-25, INV-26 |
| Constants `MERGE_ORDER`, `MIN_CORRECT` = 3, `HOLM_M` = 5 | no ruled home in A291 | OP-01 (A293) |
| Constant `CAP_BOUND_FRACTION` = 0.20 | no ruled home in A291 | OP-01 (A292) |
| Factor `2` in the (N) bound | candidate constant | INV-35 (the magistrate decides whether "ruled constant" covers it) |
