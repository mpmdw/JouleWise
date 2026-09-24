# 02b — A291 (HEADLINE-PACKER-RECUT-01): invariant matrix and roster contract, v2

Drafted 2026-09-24 by the contract-drafting seat (Opus 5.5) for the magistrate of activation a65fb4fa. This is a complete replacement for record 02.

It installs:
- every finding that record 13 (magistrate synthesis) accepts from record 09 (the Sol 6.0 high contract lens);
- every representation ruling in record 13.

Items record 13 sends to the cold gate are written in their proposed form and tagged `PENDING-GATE(OP-nn)`. The question behind each tag is in record 14 (the gate charge). When a ruling contradicts this file, the ruling wins, in this order: 45/21 §7 > 45/10 > 21/10 > 08. Records 13 and 09 are the next authority for representation.

## 0. Conventions

### Sources

Paths are relative to `docs/process_traces/2026-09-23-activation-d8cc9c0a/` unless stated otherwise.

| Key | File |
|---|---|
| [08] | `08-a281-round1-synthesis-and-rulings.md` |
| [21/10] | `21-coldgate-packet-a281/10-coldgate-fable-ruling.md` |
| [21/11] | `21-coldgate-packet-a281/11-opus-contract-refuter.md` |
| [45/10] | `45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md` |
| [45/21] | `45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md` |
| [B26] | `45-coldgate-packet-a281a-recut/ex-26-a281a-fix2-seat-brief.md` |
| [19] | `../2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` §1 |
| [13] | this directory, `13-a291-contract-synthesis-and-rulings.md` |

Other citation forms:
- `«…»` marks a verbatim quote.
- `c:<file>:<line>` means that file at commit `c0998fdb`.

### Tags

- **Ruled.** The row restates ruled text.
- **R[13].** A representation choice that record 13 has ruled.
- **R-seat.** A representation choice by this seat that record 13 has not ruled. The magistrate should confirm it.
- **PENDING-GATE(OP-nn).** An S-class item: a choice that adds to, weakens or reinterprets a ruling. The text here is the proposed disposition, and the gate may change it.

### Paths and witnesses (installs F11)

The eleven closed paths of 45/21 §7(G):

| Code | Path |
|---|---|
| `P` | `pack` |
| `E1` | `requeue_overrun`: initial→whole_block |
| `E2` | `requeue_overrun`: initial→reschedule |
| `E3` | `requeue_overrun`: initial→unattributed_overrun |
| `E4` | `requeue_overrun`: whole_block→single_problem |
| `E5` | `requeue_overrun`: whole_block→unattributed_overrun |
| `E6` | `requeue_overrun`: single_problem→single_retry |
| `E7` | `requeue_overrun`: single_problem→reschedule |
| `E8` | `requeue_overrun`: single_retry→ceiling_violation |
| `E9` | `requeue_overrun`: single_retry→reschedule |
| `R` | `reduce` |

**Every row below needs an executed violating witness on all eleven paths.** A witness can take one of three forms:
- **natural:** a real input takes the path and produces the violation;
- **entry injection:** a violating roster is fed to a call that would otherwise take that path, and the seal refuses it at entry;
- **exit injection:** an internal helper is patched so that the path emits the violation, and the seal refuses it at exit.

No row claims `n/a`. Any `n/a` the implementer later proposes is an exception for the gate (PENDING-GATE(OP-28)).

### Definitions (§2.0 of 02, carried forward)

- `cap := interior_s − guard_s` (c:scored_registration.py:129).
- `worst(m) := cap_tokens[arm] × s_per_token_upper[m][arm] + prefill_s[m][arm]` (c:scored_registration.py:157; c:scored_packer.py:309-311, 322-324, 353-355). This is per item, for the selected arm.
- `bpc := ceil(n / block_size[arm])` (c:scored_registration.py:169).
- `max_gap := budget_j / (delta_upper_j_per_block_slot × bpc)` (c:scored_registration.py:170). It is undefined in pilot mode when an input is null.
- `canon_sha(v) := sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()`, the inline form at c:scored_registration.py:96+179 and c:scored_packer.py:27-32. JSON numbers are hashed exactly as accepted: no float coercion (R[13] OP-07).
- `LEVELS = [1,2,3,4,5]`.
- `RETRY_STAGES = ["initial","whole_block","single_problem","single_retry","ceiling_violation"]` (c:scored_registration.py:26).
- `MIN_PARENT_BLOCKS = MIN_ENVELOPES = 5`.
- **Placement.** One scheduling of one block attempt into one envelope: the §2.5 record (R[13] F06).
- **Live placement.** For each block, its latest placement, provided the block's id is in that envelope's `blocks` list.
- **Planned position.** For a parent, the item-weighted mean of the envelope indices of the live placements holding its non-terminal items. It exists only while some item is non-terminal.
- **Executed position.** The same mean over counted attempts only (§3 `captured`). A pending placement is not a counted window (R[13] F07, F13).

---

## 1. Invariant matrix

### A. Identity and digests

**INV-01 registration binding** (ruled). «Identity fields (`schema`, `registration_id`, `plan_id`) are CONSUMED: their witness is that a roster sealed under the old digest is refused by every consumer under the new registration.» [45/10 §Q2]
Pred: `r.registration_sha256 == canon_sha(g)`.

**INV-02 roster self-digest** (ruled, with the preimage R[13]). «Opus S4 (digest chain and bound parameters)» [08 Adopted fixes]; «PF shows the requeue entry trusts any well-formed roster» [45/21 A4].
Pred: `r.sha256 == canon_sha(PRE(r))`. `PRE(r)` is `r` with three things removed: the top-level `sha256`, the top-level `registered_sha256`, and each `events[k].sha256` (§2.7).

**INV-03 no copies of registered values** (ruled; F01 installed). «no roster copies of registered values» [45/21 §7(S)]; «no copies (roster carries only `registration_sha256`)» [45/10 §Q2(1)].
Pred:
- Every record's key set equals its §2 key set exactly.
- No roster field holds a copy of a registered value. In particular, none of the c0998fdb copy keys appears: `models`, `arm`, `block_size`, `interior_s`, `guard_s`, `cap_tokens_by_arm`, `envelope_s`, `offset_s`, `pitch_s`, `capacity_s`, `levels` (c:scored_packer.py:149-152, 262-265), and no Block or TerminalRefusal carries `arm`.

Allowed:
- the roster's own `schema`;
- the ruled derived fields `claim_ready`, `item_set_sha256`, `n_per_level` and `drift_lever_slots`;
- the identity values `model` and `level` on records.

**INV-04 derived identity fields** (ruled; F02 installed). «Register `item_ids_by_level`; derive `item_set_sha256`, `n_per_level`» and «`item_set_sha256 := canonical_json_sha256([ids in level order])` is a derived roster field.» [45/10 §Q3]
Pred:
- `r.item_set_sha256 == canon_sha(FLAT(g))`. `FLAT` is one flat list: the ids of level "1" in registered order, then those of "2", and so on through "5".
- `r.n_per_level == n`. The common-length rule is PENDING-GATE(OP-05).

**INV-05 claim readiness** (ruled; F03 installed). «`mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.» [21/10 §Q2 D4]
Pred, as two clauses:
- (a) producer: `g.mode == "pilot"` implies `r.claim_ready == false`;
- (b) consumer: at the `requeue_overrun` and `reduce` entry, `g.mode != "pilot"` and `r.claim_ready == false` means refuse.

This is not a copy (R[13] OP-10).

### B. Registration coherence and prediction binding

**INV-06 worst-case ordering** (ruled). «registration keeps the inequality derived worst case ≤ `ceiling_s` ≤ capacity» [45/10 §Q2 table]; «the worst-case seconds input is derived in Registration (`cap × s_per_token_upper + prefill`)» [21/10 §Q4].
Pred: for every model `m` and every arm key `a` present in the per-arm maps, `worst(m,a) ≤ ceiling_s[m][a] ≤ cap`. Restricting the maps to the selected arm is PENDING-GATE(OP-30).

**INV-07 prediction domain** (ruled; OP-07 R[13]). «`pack` refuses any item above its derived worst case (P4)»; «Extra predictions are refused, not ignored (Sol 34 (d)).» [45/10 §Q3]
Pred:
- `set(p) ==` the two model ids;
- `set(p[m]) ==` the registered items;
- each value is a finite JSON number, not a bool, with `0 < v ≤ worst(m)`;
- in the roster form, the same bound applies to every `predicted_item_s` of every parent.

**INV-08 prediction digest** (ruled; OP-08 and OP-09 R[13]). «Add registration field `predictions_sha256` (pilot-nullable, required in registered mode)»; «refuses when `canonical_json_sha256(predicted_decode_s restricted to the registered items)` ≠ `predictions_sha256`» [45/10 §Q3]
Pred:
- `g.mode == "registered"` implies `g.predictions_sha256` is not null;
- when it is not null, `canon_sha(PRED(r)) == g.predictions_sha256`. `PRED(r) = {m: {i: v}}` is rebuilt from the parents' `items` and `predicted_item_s`, in the exact accepted representation. At `pack`, the check runs on `p` itself.

### C. Items, blocks and parents

**INV-09 level set and item identity** (ruled; F04 installed). «Opus S7 (`pack` requires the registered level set)» [08]; «`pack(registration, predicted_decode_s)` takes no items argument» [45/10 §Q3].
Pred:
- `set(g.item_ids_by_level) == {str(l) for l in LEVELS}`. Refusing int keys is PENDING-GATE(OP-03).
- Item ids are non-empty `str` and globally distinct.
- Each block's `level` is an int in `LEVELS`, and its items belong to `g.item_ids_by_level[str(level)]`.

**INV-10 paired membership** (ruled; F05 installed). «Block membership is identical across the two models, and block size is set per arm, not per model.» [19 §1 M8]
Pred:
- For each level, the parents of each model partition that level's registered items.
- The two models' partitions are equal as sets of item sets.
- The slicing rule and the parent `block_id` syntax are the §2.4 representation contract, PENDING-GATE(OP-06).

**INV-11 item conservation** (ruled). «item conservation (per model, every registered item is in exactly one block that is neither superseded nor terminal, and that block is in exactly one envelope, or is in exactly one terminal refusal and no envelope)» [45/21 §7(S)]
Pred: for every (model, registered item), exactly one of these holds:
- (a) exactly one block containing the item has `superseded == false`, is not terminal (§2.6), and has its id in the `blocks` list of exactly one envelope;
- (b) the item is in exactly one `terminal_refusals` entry, and no block containing it is in any envelope's `blocks`.

**INV-12 parent relationship** (ruled; F05 installed). «Pairing survives a split: singles carry `parent_block_id`, and the estimator pairs on the parent (Opus B2).» [08 F2(a)]; «A parent block is a block scheduled by the initial packing; single-problem blocks made from it under M12 are pieces of that parent, not new replicates.» [45/10 §Q4]
Pred:
- `parent_block_id is None` if and only if the block's first placement has stage `initial`.
- A single has exactly one item. Its parent exists, has the same model and level, contains that item, and is `superseded`.
- The singles of a parent partition the parent's items.
- The single id syntax is in §2.4, PENDING-GATE(OP-06).

**INV-13 — moved.** Per F12, the obligation that every item row carries `retry_stage` belongs to A292 (see the out-of-scope table). The block-stage vocabulary check is now part of INV-36.

### D. Envelopes and placement

**INV-14 envelope model homogeneity** (ruled). «envelope model homogeneity» [45/21 §7(S)]; «every envelope's blocks share the envelope's model» [45/10 §Q2(1)].
Pred: every placement in envelope `e` names a block with `model == e.model`, and `e.model` is one of the two model ids.

**INV-15 empty-envelope legality** (ruled). «An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope.» [45/21 §7(E)]
Pred: `e.blocks == []` implies `e.kind == "idle_slot"` or `e.voided_block_ids != []`.

**INV-16 idle slots** (ruled). «An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster.» [08 F1]
Pred:
- `kind ∈ {"loaded","idle_slot"}`.
- An `idle_slot` has `blocks == []`, `voided_block_ids == []` and `observations is None`.
- No placement ever targets an idle slot: PENDING-GATE(OP-18).

**INV-17 grid** (ruled; OP-27 R[13]). «on a fixed-pitch grid in which idle slots are grid positions» [08 F1]
Pred: `[e.index for e in envelopes] == list(range(len(envelopes)))`.

**INV-18 fixed once observed; placement above the reporter** (ruled). «An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.» [45/21 §7(E)]
Pred:
- (single roster) For every event `k`, every placement listed in `events[k].placements` has `envelope_index > events[k].envelope_index`.
- (single roster) No placement listed by a later event targets an envelope that an earlier-or-equal event reported.
- (transition) Every envelope with non-null `observations` in `before` is identical in `after`.

A strict reporting order is PENDING-GATE(OP-19).

**INV-19 no reuse after split** (ruled). «The split stage never reuses the whole-block retry's envelope.» [45/21 §7(E)]
Pred: no placement of a single of parent `B` has the `envelope_index` of `B`'s `whole_block` placement.

### E. Capacity and reservations

**INV-20 capacity** (ruled; F06 and OP-21 R[13]). «capacity by `reserved_s`» [45/21 §7(S)]; «capacity per envelope» [45/10 §Q2(1)].
Pred: for every envelope, `Σ placement.reserved_s ≤ cap` over all placements with that `envelope_index`, live and voided, each at its own `reserved_s`.

**INV-21 initial reservation** — PENDING-GATE(OP-22). Proposal: every `initial` placement has `reserved_s == block.predicted_s == Σ predicted_item_s` (c:scored_packer.py:133, 239-240). A reschedule placement keeps the `reserved_s` of that block's previous placement.

**INV-22 whole-block retry** (ruled; F06 installed). «The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged.» [45/21 §7(W)]
Pred: for each `whole_block` placement,
- `reserved_s == min(len(items) × worst(m), cap)`;
- the block's `predicted_s` equals `Σ predicted_item_s`;
- the placement is the only placement in its envelope;
- the envelope is fresh: its index is at or above the envelope count before the event that created it.

"Alone" constrains only this placement (R[13] F06).

**INV-23 single reservation** (ruled). «Each single is packed at `reserved_s = predicted_s = the item's derived worst case`.» [45/21 §7(T)]; «never by the prediction that already failed» [08].
Pred: every placement of a single has `reserved_s == worst(m)`, and every single has `predicted_s == worst(m)`.

### F. Spread: M8 by parent, and minima (F07 installed)

**INV-24 M8 by parent** (ruled). «No two parent blocks of one cell share an envelope at any stage, initial or retry.» [45/10 §Q4]
Pred: for every envelope and level, the parent ids of all placements there with that level are equal. A parent's id is its own `block_id`; a single's is its `parent_block_id`.
The checker must also ACCEPT this case: «Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity.» [45/10 §Q4]

**INV-25 planned minima** (ruled). «The five-block and five-envelope minima count parent blocks and the distinct envelopes holding their executed windows; a split never adds to either count.» and «Before capture the same shortfall is a packing refusal.» [45/10 §Q4]
Pred:
- At `pack`, for every cell, at least 5 parents occupy at least 5 distinct envelopes; otherwise `pack` refuses.
- At `requeue_overrun`, the counts are taken over parents, never pieces.
- A shortfall after the first event is not a refusal. It is decided on executed evidence by INV-26: (X) reads «for any reason after capture».

**INV-26 executed minima and `spread_exceeded`** (ruled; the timing is PENDING-GATE(OP-24)). «A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them,» [45/10 §Q4]; (X) «for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)» [45/21 §7(X)].
Pred, evaluated by `check_executed` (§3):
- a counted parent is one whose every item has a live placement `(block_id, attempt)` in `captured`;
- `spread_exceeded(cell) == (counted parents < 5 or distinct envelopes holding their counted placements < 5)`.

Proposal (record 13, F07): the value is final at reduce entry. It is not a roster key.

### G. Drift and balance, planned vs executed (F13 installed)

**INV-27 planned lever** (ruled). «The drift lever of a level is the absolute difference, in envelope slots, between the mean position of its 8B parents and the mean position of its 1.7B parents.» and «At pack time every item of a parent sits in one envelope, so its position is that envelope's index.» [45/10 §Q4]; «`requeue_overrun` recomputes `drift_lever_slots`.» [21/10 §Q2 D5b]; «One function, the §Q4 parent-unit definition, on both paths.» [45/10 §Q5 N2]
Pred:
- `r.drift_lever_slots[str(level)]` equals `|mean over 8B parents − mean over 1.7B parents|` of the planned positions.
- The value is null when a model has no positioned parent at that level.
- Recorded and re-derived values are compared with `math.isclose(rel_tol=1e-9)`.

**INV-28 pack-time drift refusal** (ruled). «register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows.» [21/10 §Q2 D5b]; «Formula at `scored_registration.py:169-170` becomes the definition; the field is removed.» [45/10 §Q3]
Pred: in registered mode, `pack` refuses if any planned lever is `> max_gap`. In pilot mode it records and never refuses.

**INV-45 executed lever** (ruled). «A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing.» [45/10 §Q4]
Pred: `check_executed` computes the lever from executed positions (captured placements only).
Consequence when it exceeds `max_gap` after capture: PENDING-GATE(OP-23). Proposal: record `drift_exceeded` for that level for A293 to map to NR(`drift_exceeded`), and never refuse. Whether 21/11 R11 binds is PENDING-GATE(OP-34).

**INV-41 per-cell balance** (ruled text; policy PENDING-GATE(OP-26); new from F15). «the packer's ordering invariant is **equal mean envelope index per cell across the two models**» and «The claim tolerance on it is registered in AP-5M after the sizing pilot measures drift, not fixed here.» [08 F1]
Proposal: equality is the packer's objective, not a checker predicate. The checkable invariant is INV-27 (recorded) plus INV-28 (bounded by `max_gap` in registered mode). Idle-slot insertion follows c0998fdb (c:scored_packer.py:65-66, 111-114).

### H. Observations and transitions

**INV-29 observation record** (ruled; the zero boundary is PENDING-GATE(OP-35)). «`requeue_overrun` at the initial and whole-block stages takes, for every block in the reporting envelope, an observation: `completed` with elapsed seconds, `cut_off` with elapsed seconds, or `not_started`; the envelope records every observation.» [45/21 §7(W)]; «At the single stages the observation per single is `completed`, `cut_off` or `not_started`, with elapsed where applicable.» [45/21 §7(N)]
Pred:
- For each event, `observations` covers the reporting envelope's pre-call `blocks` exactly: one per block.
- `status ∈ {completed, cut_off, not_started}`.
- `elapsed_s` is null if and only if the status is `not_started`; otherwise it is a finite JSON number, and `> 0` pending OP-35.
- `envelopes[event.envelope_index].observations == event.observations`.

**INV-30 initial-stage culprit and `late`** (ruled). «A completed block keeps its window; if its elapsed exceeds its `predicted_s` it is marked `late: true` and is a culprit. An uncompleted block whose elapsed exceeds its `predicted_s` is a culprit and advances one stage.» [45/21 §7(W)]
Pred, for an initial-stage block `b` with observation `o`:
- `completed` gives decision `keep`: `b` stays live, and `b.late == (o.elapsed_s > b.predicted_s)`.
- `cut_off` with `elapsed_s > predicted_s` gives decision `advance`, and a `whole_block` placement follows (INV-22).
- An observation is a culprit when its `elapsed_s` is greater than the block's `predicted_s`.

**INV-31 initial-stage innocents and unattributed overrun** (ruled). «An uncompleted or not-started non-culprit is rescheduled at its current stage without advancing, provided the envelope holds a culprit. If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun` (a `terminal_refusals` entry; its cell is unresolved until a registered recapture); the call never raises for innocence.» [45/21 §7(W)]
Pred:
- With a culprit present, each uncompleted non-culprit gets decision `reschedule`, keeps its stage, is voided in the reporting envelope, and gets a new placement. Its placement target is PENDING-GATE(OP-17).
- With no culprit, each uncompleted block gets decision `unattributed_overrun`, with one refusal per item.
- The call never raises.

**INV-32 whole-block non-completion** — PENDING-GATE(OP-14). (T): «A whole-block retry advances to the split stage when its attempt did not complete within its envelope; its observed elapsed is recorded.» [45/21 §7(T)]
Proposal:
- `cut_off`, at any elapsed, gives decision `split`: the block is `superseded`, and its singles are placed per INV-12 and INV-23 (edge E4).
- `not_started` gives decision `unattributed_overrun`, with one refusal per item (edge E5).

**INV-42 whole-block completed outcome** — PENDING-GATE(OP-14); new from F15. Proposal: `completed` gives decision `keep`, with `late == (elapsed_s > predicted_s)`. A late completion is a culprit, and it has no envelope-mates to affect.

**INV-33 single-stage advance** (ruled; the target is PENDING-GATE(OP-18)). «A single whose elapsed exceeds its derived worst case advances (`single_problem` → `single_retry` → `ceiling_violation`).» [45/21 §7(N)]
Pred:
- An uncompleted single with `elapsed_s > worst(m)` gets decision `advance`.
- From `single_problem`, a `single_retry` placement follows. Proposed target: the INV-34 rule.
- From `single_retry`, the decision is `ceiling_violation`: the single is voided, placed nowhere, and gets one typed refusal.

**INV-43 completed-single outcome** — PENDING-GATE(OP-15); new from F15. Proposal:
- A completed single with `elapsed_s ≤ worst(m)` gets decision `keep`, `late == false`, and no edge.
- A completed single with `elapsed_s > worst(m)` advances exactly as in INV-33. Its completed window is voided and never counted, and the event counts as a culprit event.

**INV-34 single reschedule placement** (ruled; eligible targets PENDING-GATE(OP-18)). «Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one.» [45/21 §7(N)]
Pred: the target is the lowest index above the reporting envelope whose envelope is eligible and keeps INV-14, INV-20 and INV-24. Otherwise it is a new envelope appended at the end.
Proposed eligibility: loaded, not fixed, and not holding a `whole_block` placement.

**INV-35 innocent-reschedule bound** (ruled; F08 installed; the no-culprit outcome is PENDING-GATE(OP-16)). «Each innocent reschedule is caused by one culprit event in its envelope and each item has at most two culprit events, so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it.» [45/21 §7(N)]
Pred:
- (a) Each single-stage `reschedule` decision sits in an event whose observations include at least one culprit decision (`advance`, `ceiling_violation`, or an OP-15 late advance).
- (b) Each single item has at most 2 culprit decisions across all events.
- (c) The count of single-stage `reschedule` decisions is at most `2 ×` the singles created so far (R[13] OP-20).

Proposal for an envelope with no culprit: the uncompleted singles get decision `unattributed_overrun` (a new edge; OP-16).

**INV-36 stage legality** (ruled; the attempt rule is PENDING-GATE(OP-22)). «stage legality (each block's `retry_stage` history follows the closed edge list in (G))» [45/21 §7(S)]; the list: «initial→whole_block, initial→reschedule, initial→unattributed_overrun, whole_block→single_problem, whole_block→unattributed_overrun, single_problem→single_retry, single_problem→reschedule, single_retry→ceiling_violation, single_retry→reschedule» [45/21 §7(G)].
Pred:
- Every recorded decision maps to a listed edge from the block's stage at that event. `keep` is not an edge. Edges proposed under OP-14, OP-15 and OP-16 are added only if ruled.
- Each block's `retry_stage` is in `RETRY_STAGES`, and equals its latest placement's `stage` (or `ceiling_violation`).
- A root roster has only `initial` placements.
- Proposal: `attempt` starts at 0 and rises by 1 per placement of that block. For singles, `attempt` continues from the parent's count (c:scored_packer.py:315, 333, 364).

**INV-37 typed terminals** (ruled; OP-25 R[13]). «The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).» [08 F2(c)]; «The reducer passes `terminal_refusals` through typed» [21/10 §Q2 D5c].
Pred:
- `type ∈ {"ceiling_violation","unattributed_overrun"}`.
- There is one entry per item, and `(model, item_id)` is unique.
- The entry's `block_id` and `attempt` name an existing voided placement of a block that contains the item.

### I. Replay and structure

**INV-38 event log and digest chain** (ruled; the digest rules are R[13]). «The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`).» [45/21 §7(R)]
Pred:
- (single) `events[-1].sha256 == r.sha256` when `events` is non-empty.
- (single) `events == []` implies `r.registered_sha256 == r.sha256`.
- (transition) `after.events[:-1] == before.events`, and `len(after.events) == len(before.events) + 1`.
- (transition) `after.events[-1].sha256 == after.sha256`.
- (transition) `after.registered_sha256 == before.registered_sha256`.

**INV-39 root replay** (ruled; F10 installed, no root exception). «`reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]`, replays every event from the root, and refuses unless the final digest matches its input roster.» [45/21 §7(R)]
Pred: the seal at the reduce entry checks replay equality for every roster, including a root. The checker cannot evaluate it (§3). Who owns the `R` witness is PENDING-GATE(OP-29).

**INV-40 seal placement** (ruled; F11 installed). «`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`.» [45/21 §7(S)]; «`_seal(registration, roster)` is the ONLY caller of `_digest`» [45/10 §Q2(1)].
Witness per path: delete that path's seal call, and a violating roster injected on that path is accepted. An AST test covers the "only caller" clause.

**INV-44 constant sweep** (ruled; homeless constants PENDING-GATE(OP-01); new from F15). «Module constants pinned by `schema`; one test asserts equality to the AP-5M text.» [45/10 §Q3]; «Constants are patched at their module attribute; a scan finds no literal duplicate.» [45/21 §7(G)]
Pred:
- Each constant in §5 equals its AP-5M value.
- Each constant is patched only at its module attribute.
- A scan finds no literal duplicate of any constant.
- Each constant is CONSUMED with witnesses, or CARRIED under a ruled home.

### Out of A291 scope (the consumer lane owns the predicate)

| Ruled invariant | Source | Consumer |
|---|---|---|
| Every item row carries `retry_stage` (was INV-13) | 08 F2(b) | A292 |
| Crossover L\*; status rule; licensing; reverse order; NE(`ceiling_violation`); Holm; per-replicate bootstrap bound | 08; 21/10 Q1, D5a | A293 |
| NE precedes `spread_exceeded`; NR(`spread_exceeded`); NR(`drift_exceeded`) mapping | 45/21 §7(P); B26 G3 | A293 |
| Idle slot never in a numerator (M7); terminal window kept as `gross_j`, never summed | 08 F1; 45/10 §Q5 F3 | A292 |
| Token-derived cap; `stop_reason`; windows keyed `(block_id, attempt)`; completeness; `scorer_id` and both digests on rows and windows | 21/11 R9; 45/10 §Q3 | A292 |
| Kill timeout = `ceiling_s`; capture timing; sizing-receipt comparison | 45/10 §Q2; 45/21 §7(G) | runner lane / arm gate |

---

## 2. Data contract

### 2.1 Registration mapping (29 keys; unchanged from 02 except where tagged)

| Key | Type / domain | Tag |
|---|---|---|
| `schema` | `"joulewise.scored_registration.v2"` | R[13] OP-33 |
| `mode` | `"pilot"` \| `"registered"` | carry-over (c:…:104) |
| `registration_id`, `plan_id`, `scorer_id` | non-empty str | carry-over (c:…:99) |
| `sizing_receipt_sha256` | sha256 hex; null only in pilot | carry-over (c:…:106-110) |
| `arm` | str, a key of `arm_to_family` | carry-over |
| `arm_to_family` | non-empty `{str: str}` | carry-over |
| `role_to_model_id` | exactly `{"8B": str, "1.7B": str}`, distinct values | carry-over |
| `alpha` | 0 < number ≤ 1 | carry-over |
| `n_boot` | int ≥ 1 | carry-over |
| `seed` | int ≥ 0 | carry-over |
| `floor_j`, `anchor_j` | number ≥ 0 | carry-over |
| `cap_tokens`, `block_size` | `{arm: int ≥ 1}` | key set PENDING-GATE(OP-30): proposal = `{g.arm}` only |
| `item_ids_by_level` | `{"1".."5": [str…]}`, globally distinct | 45/10 §Q3. Str keys: PENDING-GATE(OP-03). Equal lengths: PENDING-GATE(OP-05) |
| `envelope_s`, `interior_s`, `pitch_s` | number > 0, `pitch_s ≥ envelope_s` | carry-over |
| `offset_s`, `guard_s` | number ≥ 0, `offset_s + interior_s ≤ envelope_s` | carry-over |
| `s_per_token_upper`, `ceiling_s` | `{model_id: {arm: number > 0}}` | inner key set PENDING-GATE(OP-30) |
| `prefill_s` | `{model_id: {arm: number ≥ 0}}` | inner key set PENDING-GATE(OP-30) |
| `delta_upper_j_per_block_slot` | number > 0; null only in pilot | carry-over |
| `budget_j` | number ≥ 0; null only in pilot | carry-over |
| `declared_sensitivities` | non-empty list of str | carry-over |
| `predictions_sha256` | sha256 hex; null only in pilot | 45/10 §Q3 |

Removed from the registration (R[13] OP-02; 45/10 §Q3):
- `levels`, `merge_order`, `min_correct`, `holm_m`, `cap_bound_fraction`, `retry_stages`, `min_blocks_per_cell`, `min_envelopes_per_cell` become module constants;
- `n_per_level` and `item_set_sha256` become derived roster fields;
- `max_drift_lever_slots` becomes the `max_gap` definition.

`registration_sha256 = canon_sha(mapping)`, taken over the full mapping.

### 2.2 `predicted_decode_s`

`{model_id: {item_id: number}}`, exact per INV-07. It is hashed as accepted (R[13] OP-07, OP-09).

### 2.3 Roster top level (exact key set)

| Key | Type | Kind |
|---|---|---|
| `schema` | `"joulewise.scored_roster.v3"` | recorded constant (R[13] OP-33) |
| `registration_sha256` | sha256 hex | recorded |
| `claim_ready` | bool | derived (21/10 D4) |
| `item_set_sha256` | sha256 hex (flat preimage) | derived (45/10 §Q3; R[13] F02) |
| `n_per_level` | int | derived |
| `blocks` | list[Block] | recorded |
| `envelopes` | list[Envelope], index order | recorded |
| `placements` | list[Placement], append-only | recorded (R[13] F06) |
| `terminal_refusals` | list[TerminalRefusal] | recorded |
| `events` | list[Event], append-only | recorded (45/21 §7(R)) |
| `drift_lever_slots` | `{"1".."5": number \| null}`, PLANNED lever | derived (08 F1; 21/10 D5b) |
| `registered_sha256` | sha256 hex. Root: equals `sha256`. Descendants: the root's `sha256` | recorded (R[13]) |
| `sha256` | `canon_sha(PRE(r))` | recorded (R[13]) |

Dropped relative to 02:
- `drift_exceeded` and `spread_exceeded`. Both are executed-evidence values, computed at the reduce entry (INV-26, INV-45).
- `parent_sha256` (R[13]).

### 2.4 Block

| Key | Type | Kind |
|---|---|---|
| `block_id` | str | recorded. Syntax PENDING-GATE(OP-06), proposal: parent `"{model}:{arm}:{level}:{k}"`, where `k` is the slice index; single `"{parent}:single:{j}"` (c:scored_packer.py:243, 330) |
| `model` | model id | recorded |
| `level` | int in LEVELS | recorded |
| `items` | list[str], registered order. Singles have length 1 | recorded. Slicing PENDING-GATE(OP-06), proposal: consecutive slices of `block_size[arm]` in registered order, with a short last slice allowed (c:scored_packer.py:234; OP-05) |
| `predicted_item_s` | list[number], aligned with `items` | recorded from `p` |
| `predicted_s` | number. Parent: Σ `predicted_item_s`; single: `worst(m)` | derived |
| `attempt` | int = the attempt of the latest placement | derived. Rule PENDING-GATE(OP-22) |
| `retry_stage` | str in `RETRY_STAGES` | recorded (08 F2(b)) |
| `parent_block_id` | str \| null | recorded (08 F2(a)) |
| `superseded` | bool | recorded |
| `late` | bool | recorded (45/21 (W); R[13] OP-11) |

Dropped relative to 02: `arm`, `ceiling_violation`, `origin_attempt` (derivable from the first placement), and `reserved_s` (moved to Placement).

### 2.5 Envelope and Placement

**Envelope:**
- `index`: int.
- `model`: model id.
- `kind`: `"loaded"` \| `"idle_slot"`.
- `blocks`: list[str] of live ids.
- `voided_block_ids`: list[str].
- `observations`: list[Observation], or null until reported.

Consistency rule: `blocks ∪ voided_block_ids` equals the set of `block_id`s of the placements with this `envelope_index`, and the two lists are disjoint.

**Placement** (R[13] F06):
- `block_id`: str.
- `attempt`: int.
- `stage`: one of `initial`, `whole_block`, `single_problem`, `single_retry`.
- `reserved_s`: number.
- `envelope_index`: int.

`(block_id, envelope_index)` is unique. Placements created by `pack` are all listed before any event's placements.

**Observation** (45/21 (W), (N); R[13] OP-11):
- `block_id`: str.
- `status`: `"completed"` \| `"cut_off"` \| `"not_started"`.
- `elapsed_s`: number \| null (INV-29).
- `decision`: `"keep"` \| `"advance"` \| `"split"` \| `"reschedule"` \| `"unattributed_overrun"` \| `"ceiling_violation"`.

### 2.6 Event and TerminalRefusal

**Event:**
- `block_id`: str. R-seat pick: the first id in the reporting envelope's pre-call `blocks`.
- `envelope_index`: int.
- `observations`: list[Observation].
- `placements`: list[int], indices into the roster's `placements`, each created by this event (R-seat).
- `sha256`: the resulting roster's `sha256` (R[13]).

**TerminalRefusal** (R[13] OP-25):
- `type`;
- `block_id`;
- `attempt`: the attempt whose placement was voided;
- `parent_block_id`;
- `item_id`;
- `model`;
- `level`.

A block is **terminal** when every one of its items is in a refusal.

### 2.7 Digest chain (R[13]; the gate is asked to confirm it as representation, record 14 last question)

1. `registration_sha256 = canon_sha(registration mapping)`.
2. `PRE(r)` is `r` with three things removed: the top-level `sha256`, the top-level `registered_sha256`, and each `events[k].sha256`. Then `r.sha256 = canon_sha(PRE(r))`.
3. Root (`pack`): `events == []` and `registered_sha256 = sha256`.
4. Each `requeue_overrun` appends an event. It sets `event.sha256 = r'.sha256` (not circular, because event digests are outside `PRE`) and copies `registered_sha256` unchanged.
5. `reduce` asserts `registered_sha256 == pack(g, p)["sha256"]` uniformly, and replays the chain. Excluding `registered_sha256` from `PRE` weakens nothing, because the re-pack verifies it.

---

## 3. Checker interface

Module `tests/support/scored_roster_checker.py` (R[13] OP-32). It lies outside the implementer's WRITE_SCOPE, and a different seat commits it before implementation (45/21 §7(G)).

```python
@dataclass(frozen=True)
class Violation:
    inv: str; where: str; detail: str

def check_roster(registration: Mapping, roster: Mapping,
                 predicted_decode_s: Mapping | None) -> list[Violation]: ...
def check_transition(registration: Mapping, before: Mapping, after: Mapping,
                     predicted_decode_s: Mapping | None) -> list[Violation]: ...
def check_executed(registration: Mapping, roster: Mapping,
                   captured: Collection[tuple[str, int]]) -> dict: ...
```

**Behaviour:**
- The functions are pure and never raise.
- Violations are sorted by `(inv, where)`.
- The registration arrives as a plain mapping, and the checker re-derives every §0 definition itself.
- Rows tagged PENDING-GATE are implemented behind a table `PENDING = {"OP-nn": proposal}`. The table is switched to the ruled text before the checker commit.

**Coverage:**
- `check_roster` covers every INV except INV-18's transition half, INV-26, INV-45, INV-38's transition clauses, INV-39, INV-40 and INV-44.
- `check_transition` adds INV-18's fixedness and INV-38's transition clauses, and checks the new event's decisions against INV-30 through INV-36 and INV-42/43.
- `check_executed` returns, per cell, the counted parents, the executed envelopes and `spread_exceeded` (INV-26), and, per level, the executed lever (INV-45). It also returns violations for any `captured` key that is not a placement.

**Imports:** stdlib only. It never imports `joulewise.scored_packer`, `joulewise.scored_registration`, `joulewise.scored_reduce`, or anything else in `joulewise`.

No shared helper on main fits:
- `joulewise/identity_pins.py:210` uses `ensure_ascii=False` and project imports;
- `joulewise/benchmark_import_math.py:47` lacks `allow_nan=False`;
- `joulewise/dominance_closeout.py:491` imports the analysis engine.

The checker therefore carries `canon_sha` itself. A test outside the checker asserts that the packer and the checker produce byte-equal digests.

**Replay:** the checker cannot call `pack`. INV-39 belongs to the seal and to `reduce`. The checker verifies the chain structure through INV-38 and re-derives each event's decisions.

**Stress run:** seeded `pack` → random observations → `requeue_overrun` → … . `check_roster` runs on every roster, `check_transition` on every call, and `check_executed` on the final roster with a random `captured`. The expected result is zero violations.

**Checker output:** no plausibility warnings (R[13] OP-31).

---

## 4. Open-point register

**Ruled as representation by record 13:**

| OP | Ruling |
|---|---|
| OP-02 | Constants leave the registration. |
| OP-04 | Flat preimage. |
| OP-07 | Exact numeric representation. |
| OP-08 | PRED rebuilt from parents. |
| OP-09 | Hash the full map. |
| OP-10 | Not a conflict. |
| OP-11 | `late` on the block; decisions in observations. |
| OP-12, OP-13 | Digest-chain rules (§2.7). |
| OP-20 | Singles created so far. |
| OP-21 | Capacity over live and voided placements. |
| OP-25 | One refusal per item, plus `attempt`. |
| OP-27 | Contiguous indices. |
| OP-31 | No warnings. |
| OP-32 | `tests/support/`. |
| OP-33 | Schema strings. |

**Pending at the gate (record 14):** OP-01, OP-03, OP-05, OP-06, OP-14, OP-15, OP-16, OP-17, OP-18, OP-19, OP-22, OP-23, OP-24, OP-26, OP-28, OP-29, OP-30, OP-34, and OP-35 (F14's zero elapsed, numbered here). The gate is also asked to confirm the digest chain.

**Seat picks revised since 02:**
- **OP-15:** 02 said a completed single above its worst case both keeps and voids its window, which is incoherent (F14). v2 proposes voided and advancing.
- **OP-16:** 02 had "reschedule all". That contradicts the accepted F08(a), so v2 proposes a typed `unattributed_overrun`.
- **OP-23 and OP-24:** re-proposed on executed evidence (F07, F13).

**R-seat items for the magistrate to confirm:**
- the event's `block_id` pick;
- `Event.placements`;
- the `PENDING` switch table in the checker;
- the `check_executed` signature.

---

## 5. Field and constant seed

| Field / constant | Proposed status | Consumer |
|---|---|---|
| `schema`, `registration_id`, `plan_id` | CONSUMED (identity) | INV-01 |
| `mode` | CONSUMED | INV-05, INV-08, INV-28 |
| `sizing_receipt_sha256` | CARRIED | arm gate (runner lane) |
| `arm` | CONSUMED | `worst`, `bpc`, block ids |
| `arm_to_family` | CARRIED | A293 |
| `role_to_model_id` | CONSUMED | INV-07, INV-10, INV-14 |
| `alpha`, `n_boot`, `seed`, `floor_j`, `anchor_j`, `declared_sensitivities` | CARRIED | A293 |
| `cap_tokens`, `s_per_token_upper`, `prefill_s` | CONSUMED (selected arm; OP-30) | `worst`: INV-07, INV-22, INV-23, INV-33 |
| `block_size` | CONSUMED | INV-10 / OP-06, `bpc` |
| `item_ids_by_level` | CONSUMED | INV-04, INV-09 to INV-11 |
| `interior_s`, `guard_s` | CONSUMED | `cap`: INV-20, INV-22 |
| `envelope_s`, `offset_s`, `pitch_s` | CARRIED | runner lane (45/21 §7(G)) |
| `ceiling_s` | CARRIED | runner kill timeout; INV-06 is validation-only |
| `delta_upper_j_per_block_slot`, `budget_j` | CONSUMED (registered mode) | `max_gap`: INV-28 |
| `scorer_id` | CARRIED | A292 and the runner |
| `predictions_sha256` | CONSUMED | INV-08 |
| `LEVELS` | CONSUMED | INV-09 |
| `RETRY_STAGES` and the edge list | CONSUMED | INV-36 |
| `MIN_PARENT_BLOCKS` = 5, `MIN_ENVELOPES` = 5 | CONSUMED | INV-25, INV-26 |
| `MERGE_ORDER`, `MIN_CORRECT` = 3, `HOLM_M` = 5 | PENDING-GATE(OP-01), proposal: CARRIED → A293 | — |
| `CAP_BOUND_FRACTION` = 0.20 | PENDING-GATE(OP-01), proposal: CARRIED → A292 | — |
| Factor 2 of (N) | candidate constant (INV-35) | the magistrate decides whether it is a "ruled constant" |
