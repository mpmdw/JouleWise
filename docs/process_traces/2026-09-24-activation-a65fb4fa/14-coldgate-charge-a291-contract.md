# 14 — Charge: cold gate A291-CONTRACT-01

## What this gate rules

The judge rules on 19 open choices and one confirmation. Together they decide the exact data contract and the invariant list for the rebuilt experiment scheduler (lane A291).

Assembled 2026-09-24 by the contract-drafting seat (Opus 5.5) for the magistrate of activation a65fb4fa. Nothing is armed.

Every pick below is ARGUMENT. That covers the drafting seat's, the lens's and the magistrate's. The ruled texts quoted are the authority. Where they conflict, the later text wins: addendum 45/21 §7 > ruling 45/10 > ruling 21/10 > rulings 08.

The magistrate adds the charter pin, the exhibit manifest, the judge's constraints and the ruling file name when convening.

## 1. Terms, in plain words (read this first)

### The experiment

- **The experiment.** Two language models, one with 8 billion parameters ("8B") and one with 1.7 billion ("1.7B"), answer the same set of MATH competition problems. The machine's power draw is recorded during fixed-length measurement windows. The claim compares energy per correct answer across the two models, at each of five difficulty levels (1–5).
- **Item.** One MATH problem, identified by an id string.
- **Level.** A difficulty level, 1 to 5.
- **Cell.** One (model, level) pair.
- **Envelope.** One fixed-length power-measurement window. During an envelope, exactly one model is loaded and runs a scheduled list of work.
  - Envelopes sit on a fixed time grid and are numbered 0, 1, 2, …; that number is the envelope's **index**.
  - **Capacity** is the usable seconds inside one envelope: its interior length minus a guard margin (`interior_s − guard_s`).
- **Idle slot.** An envelope in which a model is loaded but runs nothing. It exists only to balance the two models' positions in time. It is still a grid position.

### Blocks and scheduling

- **Block.** An ordered group of items that one model runs back-to-back inside one envelope.
  - The energy between the first and last item of a block is one measurement. Each such measurement is a **replicate**: one of several independent repeats that are pooled.
  - Both models use the same grouping of items into blocks, so their blocks pair up.
- **Parent block.** A block made by the initial schedule.
- **Single.** A one-item block cut from a parent after repeated overruns (see stages). A single is a *piece* of its parent, not a new replicate.
- **Registration.** The frozen, pre-registered parameter set. Its SHA-256 **digest** (a fingerprint of the exact bytes) is recorded as `registration_sha256`. Every registered value is either:
  - **CONSUMED**: the code demonstrably uses it; or
  - **CARRIED**: stored unused here and consumed by another named work lane, from a closed list ruled by an earlier gate.
- **Roster.** The JSON schedule document. It lists the blocks, the envelopes and the history of what happened, and carries its own digest `sha256`.
- **The three functions.**
  - `pack` builds the initial roster from the registration and the per-item time predictions.
  - `requeue_overrun` is called after an envelope in which work ran over. It records what happened and reschedules.
  - `reduce` turns the finished roster plus the measured energy windows into per-cell numbers.

### Time budgets

- **Prediction** (`predicted_s`). The forecast seconds for a block: the sum of its items' forecasts.
- **Derived worst case.** The longest one item can physically take: `cap_tokens × s_per_token_upper + prefill_s`. That is the token limit times the upper bound on seconds per token, plus prompt processing. It is computed from registered values.
- **Reservation** (`reserved_s`). The seconds a scheduled block books against an envelope's capacity.
- **Placement.** One scheduling of one block attempt into one envelope. It records the block id, the attempt number, the stage, the reservation and the envelope index.

### Stages, observations and culprits

- **Stages.** A block's retry stage moves along a ruled path:
  - `initial`: as first scheduled;
  - `whole_block`: the whole block re-run alone in a new envelope;
  - `single_problem`: the block split into singles;
  - `single_retry`: a single's one retry;
  - `ceiling_violation`: final; the item is recorded as a typed refusal.
- **Edge.** One allowed move between stages. **Reschedule** means moving work to a later envelope without changing its stage. **`unattributed_overrun`** is a typed final outcome for work that did not finish when nothing identifiable overran.
- **Closed edge list** (45/21 §7(G)). These nine edges, plus `pack` and `reduce`, are the eleven **paths**:
  - initial→whole_block, initial→reschedule, initial→unattributed_overrun;
  - whole_block→single_problem, whole_block→unattributed_overrun;
  - single_problem→single_retry, single_problem→reschedule;
  - single_retry→ceiling_violation, single_retry→reschedule.
- **Reporting envelope.** The envelope whose outcome a `requeue_overrun` call records.
- **Observation.** For each block in the reporting envelope, one status: `completed` with elapsed seconds, `cut_off` (stopped by the envelope's end) with elapsed seconds, or `not_started`.
- **Culprit.** A block whose elapsed time exceeded its prediction, or, for a single, its derived worst case.
- **Innocent.** A block that was cut off or never started because a culprit used its time.
- **`late`.** The flag on a block that completed but took longer than predicted.
- **Fixed envelope.** An envelope that already has an observation recorded. It may never change again.

### Records, digests and replay

- **Event.** One entry appended to the roster's `events` list per `requeue_overrun` call. It holds the reporting envelope, the observations, the decisions and the resulting roster digest.
- **Preimage.** The exact data a digest is computed over.
- **Replay.** Re-running `pack` and then every event from scratch to check that the roster was produced honestly.
- **Terminal refusal.** A typed record that an item ended in `ceiling_violation` or `unattributed_overrun`. The item is never silently dropped.

### Spread and drift

- **M8.** The spread rule for replicates. Each cell must have at least 5 parent blocks in at least 5 distinct envelopes, and no two parents of one cell may share an envelope.
- **Counted window.** The captured measurement of an item's final, valid attempt. Planned work that has not yet run is not counted.
- **`spread_exceeded`.** A cell-level flag meaning the executed spread fell below the minimum after capture. The numbers are reported, but the level is not resolved.
- **Drift lever.** For one level, the gap, in envelope slots, between the mean envelope position of the 8B's parents and that of the 1.7B's parents. Slow machine drift cancels out of the between-model comparison only when this gap is small.
- **`max_gap`.** The registered bound on the drift lever: `budget_j / (delta_upper_j_per_block_slot × ceil(items per level / block size))`. In words: the allowed energy bias divided by the per-slot drift rate times the number of blocks per cell.
- **Planned vs executed.** "Planned" values use the envelopes where work is scheduled. "Executed" values use the envelopes where counted windows were actually captured.

### Enforcement and review

- **Seal.** One function, `_seal`, that checks every ruled rule on the roster. It runs at every entry to and exit from `pack`, `requeue_overrun` and `reduce`.
- **Independent checker.** A separate module that checks rosters against the rules. It is written by a different seat from the ruling text, before the code exists, and it may not import the code.
- **Witness.** An executed test showing that a violation is caught on a given path. The three forms:
  - natural: a real input produces the violation;
  - entry injection: a bad roster is fed in;
  - exit injection: an internal step is patched to emit a bad roster.
- **Lanes.** A lane is one tracked work item.
  - **A291** is registration plus scheduler (this gate).
  - **A292** is the reducer: `reduce` itself.
  - **A293** is the estimator: the statistics that turn cell numbers into claims. Its statuses **NR** ("not resolved") and **NE** ("not estimable") mark levels where no claim is made.
  - The **runner lane** is the code that actually drives the machine.
  - **AP-5M** is the pre-registered analysis-plan text.
- **The stopped draft `c0998fdb`.** A git commit holding an earlier implementation. It was stopped because it carried registered fields it never used. It is cited as `c:<file>:<line>`.
- **Record types in this directory.**
  - **02b** is the proposed contract. Every row it tags `PENDING-GATE(OP-nn)` is decided here.
  - **09** is a contract review by Sol 6.0 (another model).
  - **13** is the magistrate's synthesis.
- **Classes of choice.** An **R-class** choice is representation only. An **S-class** choice adds to, weakens or reinterprets a ruling. S-class choices come to this gate.

### Section labels of the governing text

The addendum ruling 45/21 §7 has labelled paragraphs:

| Label | Subject |
|---|---|
| (W) | whole-block stage |
| (T) | split trigger |
| (N) | single stages |
| (E) | empty envelopes and placement |
| (S) | seal contents |
| (R) | replay |
| (G) | gate criterion |
| (X) | spread wording |
| (P) | precedence |

### Source keys

All sources are under `docs/process_traces/`:

| Key | File |
|---|---|
| [08] | `2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md` |
| [21/10] | `…/21-coldgate-packet-a281/10-coldgate-fable-ruling.md` |
| [21/11] | `…/21-coldgate-packet-a281/11-opus-contract-refuter.md` |
| [45/10] | `…/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md` |
| [45/11] | `…/45-coldgate-packet-a281a-recut/11-opus-contract-refuter.md` |
| [45/21] | `…/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md` |
| [B26] | `…/45-coldgate-packet-a281a-recut/ex-26-a281a-fix2-seat-brief.md` |
| [19] | `2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md` |
| [09] | `2026-09-24-activation-a65fb4fa/09-a291-contract-sol-lens.md` |
| [13] | `2026-09-24-activation-a65fb4fa/13-a291-contract-synthesis-and-rulings.md` |

`«…»` marks a verbatim quote.

For each question, give AFFIRM (a stated pick), a different text, or a request for a new rule. Give exact text wherever you rule a cure.

---

## 2. Questions

### Q1 — Constants with no allowed home (OP-01)

**Question.** Four ruled constants have no ruled consumer on A291's code paths. What is their status in A291's sweep?
- The constants: `merge_order` (the order in which sparse levels are pooled), `min_correct` = 3, `holm_m` = 5 (the multiple-testing family size) and `cap_bound_fraction` = 0.20.
- The sweep: A291's acceptance test must show that every field and constant is either used or on a closed list of fields "carried for another lane". Those four are neither.

**Readings.**
- (a) Add them to the closed CARRIED list: the first three to A293, `cap_bound_fraction` to A292.
- (b) Constants defined outside A291's modules are exempt from A291's sweep.
- (c) Leave both texts as they are, so A291 cannot pass.

**Opus pick: (a).** The list is ruled "closed", so exempting anything by reading (b) is a seat reinterpretation.

**Sol pick (09 L5).** Same question, no disagreement: «Must `merge_order`, `min_correct`, `holm_m`, and `cap_bound_fraction` be added to CARRIED with named consumer lanes, or are constants outside A291’s modules exempt from this A291 sweep?»

**Magistrate.** Lists it as S class; no disposition stated.

**Texts.**
- «Constants: levels, merge_order, min_correct 3, holm_m 5, both spread minima 5, cap_bound_fraction 0.20, retry_stages» [45/10 §Q3]
- «Module constants pinned by `schema`; one test asserts equality to the AP-5M text.» [45/10 §Q3]
- «Closed CARRIED list (field → consumer lane). Anything else with no effect is a defect.» [45/10 §Q2]
- «Every registration field and every ruled constant is listed by the perturbation sweep as CONSUMED, with an executed boundary witness on every path in the closed path list, or as CARRIED in the closed list.» [45/21 §7(G)]

### Q2 — Type of the level keys (OP-03)

**Question.** The registration's `item_ids_by_level` maps level to item list. JSON object keys are always strings, but a Python caller can pass integer keys, which silently become strings when hashed or saved. Must the keys be the strings "1".."5", with integer keys refused?

**Readings.**
- (a) Strings only; refuse integers.
- (b) Accept either form and normalise to strings.
- (c) Use a list of five lists in level order instead of a map.

**Opus pick: (a).** A single accepted form means one in-memory shape per digest. Two shapes with the same digest is exactly the kind of silent difference that stopped the last draft.

**Sol pick (09 L4).** «**AGREE, subject to ruling.** String JSON keys make serialization stable, but refusing integer in-memory keys narrows accepted input.»

**Magistrate.** S class; no disposition.

**Texts.**
- «Register `item_ids_by_level`; derive `item_set_sha256`, `n_per_level`» [45/10 §Q3]
- «Opus S7 (`pack` requires the registered level set)» [08 Adopted fixes]

### Q3 — Equal level sizes; short last block (OP-05)

**Question.** The ruled derived field `n_per_level` and the drift bound's "blocks per cell" are single numbers.
- Must every level register the same number of items?
- If items per level is not a multiple of the block size, may the last block of a level be shorter?

**Readings.**
- (a) Equal counts are required, and a short last block is allowed. It counts as a block.
- (b) Counts may differ, with a per-level `n` and a per-level bound.
- (c) Equal counts, and the count must also be a multiple of the block size.

**Opus pick: (a).** The ruled derivation yields one number. The stopped draft sliced the list with a possible short tail (`c:scored_packer.py:234`).

**Sol pick (09 L4).** «**AGREE.** Equal level lengths fit the singular `n_per_level`; a short final block still counts, but both are acceptance choices to write explicitly.»

**Magistrate.** S class; no disposition.

**Texts.**
- «Formula at `scored_registration.py:169-170` becomes the definition; the field is removed.» [45/10 §Q3]. That formula is `max_gap` in §1.
- «Each cell is spread over at least 5 blocks in at least 5 distinct envelopes.» [19 §1 M8]

### Q4 — How items are grouped into blocks, and block ids (OP-06)

**Question.** The rule "both models use the same grouping" does not say *which* grouping, or how blocks are named. Should the contract fix one?

**Readings.**
- (a) Adopt the stopped draft's rule:
  - consecutive slices of `block_size[arm]` items, in registered order;
  - parent ids `"{model}:{arm}:{level}:{k}"`, with `k` the slice number;
  - single ids `"{parent}:single:{j}"` (`c:scored_packer.py:234, 243, 330`).
- (b) Leave the grouping to the implementer. The checker only tests that the two models' groupings are equal.
- (c) Some other grouping rule, for example balancing predicted time across blocks.

**Opus pick: (a).** Without it, the independent checker and the implementer choose separately. Replay also needs `pack` to be deterministic.

**Sol pick (09 L4).** «**AGREE as a proposed new contract.** Consecutive slicing and ID syntax make replay deterministic but are not implied by paired membership.»

**Magistrate.** «Slicing rule and block_id syntax move to a separate representation contract (§2), which is OP-06 and goes to the gate.» [13]

**Texts.**
- «Block membership is identical across the two models, and block size is set per arm, not per model.» [19 §1 M8]
- «`reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]`» [45/21 §7(R)]

### Q5 — The whole-block retry that does not finish (OP-14)

**Question.** A whole-block retry always runs alone in its envelope. The texts disagree on three reports.
- Reported `cut_off` with elapsed at or below its prediction: (W) sends it to `unattributed_overrun`, because there is no culprit; (T) sends it to the split.
- Reported `not_started`: which edge applies, and what elapsed value is recorded?
- Reported `completed`: what happens?

**Readings.**
- (a) Rule by outcome:
  - `cut_off` at any elapsed goes to split (whole_block→single_problem);
  - `not_started` goes to `unattributed_overrun` (whole_block→unattributed_overrun), with nothing recorded as elapsed;
  - `completed` keeps its window and is `late` when elapsed exceeds its prediction.
- (b) (W) governs: a within-prediction `cut_off` is `unattributed_overrun`.
- (c) (T) governs everything: `not_started` also splits.

**Opus pick: (a).**
- The addendum's own reasoning says no innocence test applies to the lone retry.
- The whole_block→unattributed_overrun edge would otherwise be unreachable.
- `not_started` has no elapsed time to record, and (T) requires one.

**Sol pick (09 L4/L5).** «**AGREE provisionally.** `cut_off` splits under (T); `not_started` follows (W)’s no-culprit terminal route. The within-prediction cut-off still conflicts with (W), so this cannot be final without a judge.» Sol's question: «For a whole-block retry reported `cut_off` at or below prediction, and for `not_started`, which edge wins—`whole_block→single_problem` or `whole_block→unattributed_overrun`—and what elapsed value, if any, is recorded?»

**Magistrate.** S class. Rows for the completed outcome follow the ruling.

**Texts.**
- «`requeue_overrun` at the initial and whole-block stages takes, for every block in the reporting envelope, an observation» [45/21 §7(W)]
- «If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun`» [45/21 §7(W)]
- «A whole-block retry advances to the split stage when its attempt did not complete within its envelope; its observed elapsed is recorded.» [45/21 §7(T)]
- «The whole-block retry runs alone (ruling 10 §Q3 row 5), so non-completion within its reservation is the split trigger and no innocence test applies.» [45/21 A5]

### Q6 — A single that completes but exceeds its worst case (OP-15)

**Question.** A single finished inside its envelope but took longer than its derived worst case. Does it advance to the next stage, and is its completed measurement kept or discarded?

**Readings.**
- (a) It advances. The completed window is voided and never counted, and the event counts as a culprit event for its envelope-mates.
- (b) It keeps its window (counted) and is flagged, with no advance.
- (c) It keeps its window and also re-runs. The judge should note that this leaves two measurements of one item.

**Opus pick: (a).**
- (N) says any single whose elapsed exceeds its worst case advances.
- Exceeding a registered physical bound makes that measurement untrustworthy.
- (Record 02 stated an incoherent mix of (a) and (b). This corrects it.)

**Sol pick (09 L4).** «**DISAGREE.** A completed single above worst case advances under (N); its prior attempt cannot simultaneously be a kept counted window and a voided retry window. Rule which evidence is retained.»

**Magistrate.** S class; no disposition.

**Texts.**
- «A single whose elapsed exceeds its derived worst case advances (`single_problem` → `single_retry` → `ceiling_violation`).» [45/21 §7(N)]
- «The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).» [08 F2(c)]

### Q7 — A single-stage envelope with no culprit (OP-16)

**Question.** In an envelope of singles, some singles did not finish, yet none exceeded its worst case. Singles are booked at their worst case, so this cannot happen with correct timing: it is an instrumentation fault. The edge list has no single→`unattributed_overrun` edge. What happens?

**Readings.**
- (a) Reschedule all of them. Only the aggregate bound (N) limits repetition.
- (b) A typed `unattributed_overrun` for each unfinished single. This adds edges single_problem→unattributed_overrun and single_retry→unattributed_overrun.
- (c) The seal refuses: the call raises, and the night's remaining work for those items is stranded.

**Opus pick: (b).**
- (N) says each innocent reschedule is caused by a culprit event. The magistrate has accepted a per-reschedule check of that, which excludes (a).
- (W) already treats the same fault as a typed final state.
- (c) strands items.
- (Record 02 originally picked (a). This is revised because of that accepted check.)

**Sol pick (09 L4).** «**DISAGREE.** An accepted innocent reschedule without a culprit violates (N)’s causal bound immediately; waiting for the aggregate limit does not cure it. Seek an explicit fault outcome/edge.»

**Magistrate.** Accepted the causal check: «check (a) each innocent reschedule is linked to a culprit event in the same envelope; (b) each item has at most two culprit events; then (c) the aggregate bound.» [13]. The outcome is S class.

**Texts.**
- «Each innocent reschedule is caused by one culprit event in its envelope and each item has at most two culprit events, so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it.» [45/21 §7(N)]
- «`unattributed_overrun` is unreachable under correct instrumentation (Σ elapsed ≤ Σ predicted ≤ capacity); it is a fault signal the runner lane must surface, not a retry path.» [45/21 §8 N1]

### Q8 — Where an innocent initial-stage block goes, and how often (OP-17)

**Question.** At the initial stage, an innocent block is "rescheduled at its current stage". No text says into which envelope, or bounds how many times.

**Readings.**
- (a) Use the single-stage rule. The block goes to the first later envelope that satisfies M8 and capacity (see Q9 for which envelopes qualify), else a fresh one. It keeps its reservation. Beyond "each reschedule is caused by a culprit in its envelope" there is no separate bound.
- (b) Always a fresh envelope, alone.
- (c) Adopt the refuter's per-item bound, «innocent reschedules ≤ 2 × (block_size − 1)».

**Opus pick: (a).** It is one rule for both stages, and it keeps M8. Under (a), (X)'s «a rescheduled parent the seal cannot place» is unreachable, because a fresh envelope always exists.

**Sol pick (09 L4).** «**AGREE provisionally.** Apply later eligible placement to initial-stage innocents, but its lack of a bound and its effect on (X) need a ruling.»

**Magistrate.** S class; no disposition.

**Texts.**
- «An uncompleted or not-started non-culprit is rescheduled at its current stage without advancing, provided the envelope holds a culprit.» [45/21 §7(W)]
- «Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one.» [45/21 §7(N)]
- (X) «for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)» [45/21 §7(X)]
- «ACCEPT R5 and both NITs (MATERIAL)» [45/21 A6]. The accepted refuter NIT reads: «rule where an innocent rescheduled parent goes (the seal refuses it if it shares an envelope with another parent of the cell). NIT: "at most two guilty events per item; innocent reschedules ≤ 2 × (block_size − 1)".» [45/11 Step 2]

### Q9 — Which envelopes may receive moved work (OP-18)

**Question.** When work is rescheduled, or a single advances to its retry, which existing envelopes may take it?

**Readings.**
- (a) An envelope qualifies only if all of these hold:
  - its index is above the reporting envelope;
  - it is not fixed;
  - it is not an idle slot;
  - it does not hold a whole-block retry;
  - it has the same model;
  - it keeps M8-by-parent and capacity.
  
  Advancing singles use the same first-qualifying-else-fresh rule.
- (b) Only (E)'s literal limits (index above the reporter; never a fixed envelope). Idle slots and retry envelopes may be filled.
- (c) Moved work always goes to a fresh envelope.

**Opus pick: (a).**
- Filling an idle slot destroys the "loaded and idle" capture the ruling defines.
- Filling a whole-block retry's envelope breaks "alone".
- (N) states no placement for *advancing* singles; one rule avoids a silent choice.

**Sol pick (09 L4).** «**AGREE.** Keep observed envelopes fixed, idle captures idle, and whole-block retries alone; the eligible-target rule should be stated explicitly.»

**Magistrate.** «"Alone" applies only to the whole-block-retry placement.» [13]. The target rule is S class.

**Texts.**
- «An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.» [45/21 §7(E)]
- «The whole-block retry is scheduled alone in a fresh envelope» [45/21 §7(W)]
- «An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster.» [08 F1]

### Q10 — Must overruns be reported in time order? (OP-19)

**Question.** `requeue_overrun` is called only for envelopes that overran. An envelope that ran cleanly records nothing and so is never "fixed". Suppose envelope 7 is reported after envelope 9 has already run cleanly. Work could then be placed into envelope 9, which has already run. Must reports come in strictly increasing envelope order, with every envelope at or below the highest reported index treated as already run?

**Readings.**
- (a) Yes: strictly increasing report order, and placement only above the highest index reported so far.
- (b) No: only (E)'s literal limits apply.

**Opus pick: (a).** Otherwise the defect (E) exists to prevent, new work placed into a capture that already ran, stays reachable.

**Sol pick (09 L4).** «**DISAGREE.** Enforce fixed observed envelopes and placement above each reporting envelope; strict event-index order adds a refusal absent from (E).»

**Magistrate.** S class; no disposition.

**Texts.**
- «An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's.» [45/21 §7(E)]
- «A retry must preserve each item and its parent block, record observations and stage transitions, and never place work into a capture that has already run.» (the lane row A291 in `TASK_QUEUE.md`; magistrate text, not a ruling)

### Q11 — Initial reservation and attempt numbering (OP-22)

**Question.**
- What does an initial block reserve against capacity?
- How are attempts numbered? The reducer keys measurement windows by (block id, attempt).

**Readings (reservation).**
- (a) Its prediction (the sum of its items' forecasts), as the stopped draft packed (`c:scored_packer.py:133`). A rescheduled block keeps its previous reservation.
- (b) The sum of its items' derived worst cases.

**Readings (attempts).**
- (a) Attempt 0 at the initial placement, plus 1 per later placement. Singles continue the parent's count (`c:scored_packer.py:315, 333, 364`).
- (b) Some other key, for example the placement's position in the roster.

**Opus pick: (a) and (a).** Reservation (b) books every block at its worst case, which under long reasoning outputs is several times the prediction, and wastes most envelopes. The attempt rule is the stopped draft's and works with the window key.

**Sol pick (09 L4).** «**AGREE provisionally.** Initial `reserved_s = predicted_s` matches stopped packing but is an unruled acceptance rule.»

**Magistrate.** «INV-21 (initial `reserved_s`) and INV-36 (attempt increments) become proposed contract, S class, for the gate (OP-22).» [13]

**Texts.**
- «capacity by `reserved_s`» [45/21 §7(S)]
- «The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged.» [45/21 §7(W)]
- «Each single is packed at `reserved_s = predicted_s = the item's derived worst case`.» [45/21 §7(T)]

### Q12 — Drift over the bound after capture (OP-23)

**Question.** At `pack`, a registered roster whose drift lever exceeds `max_gap` is refused. After measurements have started, retries can push the executed lever over `max_gap`. What then?

**Readings.**
- (a) Record `drift_exceeded` for that level. The estimator (A293) reports the level NR(`drift_exceeded`). Nothing refuses.
- (b) The seal refuses the roster.
- (c) Refuse only the retry call that pushes the lever over.

**Opus pick: (a).**
- Refusing after capture discards measured data and strands items.
- It mirrors the ruled after-capture treatment of spread shortfall (report, do not resolve).

**Sol pick (09 L4).** «**DISAGREE.** Keep the ruled counted-attempt position; distinguish a planning estimate from executed drift. Post-capture flag versus refusal needs a ruling from these authorities.» The position part is accepted by the magistrate. The consequence is the question here.

**Magistrate.** «drift position uses the envelope of the COUNTED attempt, per the ruled text. The pack-time lever is a separate "planned" computation. Refusal versus flag after capture goes to the gate.» [13]

**Texts.**
- «A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured.» [45/10 §Q4]
- «register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows. `requeue_overrun` recomputes `drift_lever_slots`.» [21/10 §Q2 D5b]
- «drift by parent» [45/21 §7(S)]
- See Q18 for the refuter text R11.

### Q13 — When the executed spread is final (OP-24)

**Question.** The spread minima after capture count only parents all of whose items have counted windows. At what point is `spread_exceeded` decided?

**Readings.**
- (a) Once, at the entry of `reduce`, from the finished roster plus the set of captured window keys.
- (b) At every retry, on what has been captured so far.
- (c) Never in A291; only in the reducer lane.

**Opus pick: (a).** This revises record 02, which counted pending work, as the lens showed wrongly. Only at `reduce` is the evidence complete.

**Sol pick (09 L4).** «**DISAGREE.** A pending block is not a counted window. Count fully evidenced parents and distinct capture envelopes at the appropriate completed stage.»

**Magistrate.** «Distinguish PLANNED minima (checked at pack and requeue) from EXECUTED minima (checked at reduce entry on counted evidence). The executed `spread_exceeded` is determined at reduce entry.» [13]

**Texts.**
- «A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them,» [45/10 §Q4]
- «Before capture the same shortfall is a packing refusal.» [45/10 §Q4]

### Q14 — Idle slots and time balance (OP-26)

**Question.** The ordering goal is that each level's two models sit at the same mean envelope position. Two things are unruled:
- when idle slots are inserted, and for which model;
- whether exact balance is a hard rule or a goal.

**Readings.**
- (a) Keep the stopped draft's rule: one idle slot is added only when both models have an odd envelope count, and it is given to the second model (`c:scored_packer.py:65-66, 111-114`). Balance is a search goal. The checkable rule is the recorded gap, bounded by `max_gap` in registered mode.
- (b) Exact equal means are required.
- (c) A different idle rule: an idle slot wherever one model lacks a paired position.

**Opus pick: (a).** 08 F1 itself records a residual gap and defers the tolerance, so exact equality is not what was ruled. The idle rule is deterministic.

**Sol pick (09 L4).** «**AGREE provisionally.** The stopped insertion rule is deterministic, but the particular idle-worker model and balance policy are not ruled.»

**Magistrate.** S class; no disposition.

**Texts.** From [08 F1]:
- «the packer's ordering invariant is **equal mean envelope index per cell across the two models**»
- «The palindrome is kept only if the balance search wants it; it is no longer a requirement.»
- «The claim tolerance on it is registered in AP-5M after the sizing pilot measures drift, not fixed here.»

### Q15 — May an invariant be declared "not applicable" on a path? (OP-28)

**Question.** Every invariant row needs an executed violating witness on every one of the eleven paths. Some pairs cannot occur naturally: for example, a single's parent link on `pack`, before any single exists. May such a pair be marked `n/a`?

**Readings.**
- (a) No `n/a`. Use entry or exit injection where a natural witness is impossible.
- (b) `n/a` is allowed with a reason reviewed by the contract lens, as the ruled text allows for field cells.

**Opus pick: (a).** This revises record 02, which picked (b). With injection, every pair in the proposed matrix is reachable. Keep (b) only as a gate-level exception.

**Sol pick (09 L4).** «**DISAGREE.** (G) literally asks for an executed violating witness for every magistrate row on every closed path. An `n/a` escape requires amendment; use entry/exit injection where feasible.»

**Magistrate.** «every magistrate row needs an executed violating witness on every closed path, using entry or exit injection where it cannot be reached naturally. Any `n/a` is an exception for the gate (OP-28).» [13]

**Texts.**
- «Every magistrate invariant row has an executed violating witness on every path.» [45/21 §7(G)]
- «A 'no effect' cell needs a contract-lens-reviewed reason.» [45/21 §7(G)]

### Q16 — Who owns the witnesses at `reduce` (OP-29)

**Question.** A291's path list includes `reduce`, and the seal and replay must run at `reduce`'s entry. But `reduce` is built in lane A292, which starts only after A291 is gated. How does A291 meet its `reduce` column?

**Readings.**
- (a) A291 ships a public `verify_executed_roster(registration, roster, predicted_decode_s)`, which runs the seal plus replay. A291's `reduce` witnesses run against it. A292's `reduce` must call it first, and A292's gate re-runs the same witnesses at the real `reduce`.
- (b) A291 builds a minimal `reduce` entry itself.
- (c) A291's `reduce` column stays open until A292.

**Opus pick: (a).** It keeps lane order, and it makes A292 inherit a mandatory gate row.

**Sol pick (09 L4).** «**DISAGREE.** A helper may be useful, but its test cannot substitute for an executed witness at the actual `reduce` entry named in (S)/(G).»

**Magistrate.** S class; no disposition.

**Texts.**
- «`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`.» [45/21 §7(S)]
- «Closed path list: `pack`; `requeue_overrun` on each edge» [45/21 §7(G)]
- «Every CARRIED row is a mandatory CONSUMED row in its consumer lane's gate.» [45/21 §7(G)]

### Q17 — Per-arm values for arms not run (OP-30)

**Question.** Several registered maps hold one value per inference setting ("arm", for example thinking on or off): `cap_tokens`, `block_size`, `s_per_token_upper`, `prefill_s` and `ceiling_s`. Only the selected arm's values affect this run. The others are used only by the registration's own coherence check, which the gate text says does not count as use.

**Readings.**
- (a) Restrict these maps to the selected arm.
- (b) Add the unselected-arm entries to CARRIED, with a named consumer.
- (c) Keep them as they are. By (G) they are then a defect.

**Opus pick: (a).** It removes values that have no consumer.

**Sol pick (09 L4).** «**AGREE with the selected-arm restriction as a proposal.** Otherwise unselected-arm entries need a new ruled CARRIED home; registration validation alone cannot establish consumption.»

**Magistrate.** S class; no disposition.

**Texts.** «A validation-only witness, one whose refusal comes from the field's own range, type or coherence check before the field meets roster content, does not count.» [45/21 §7(G)]

### Q18 — Does refuter R11 bind? (OP-34)

**Question.** The rule "drift over the bound after capture makes the level not resolved" comes from two places: a paired refuter's text (R11) and a later implementation brief that adopted it. No cold ruling adopted it. Does it bind A291 and A293? This interacts with Q12.

**Readings.**
- (a) It binds, through the magistrate's adoption in the brief.
- (b) It binds only if this gate adopts it.
- (c) It does not bind.

**Opus pick: (a), confirmed here.** Q12's pick (a) needs it as the estimator-side mapping.

**Sol pick (09 L4).** «**DISAGREE that R11 binds from the listed authorities alone.** The refuter asked for an after-capture status; obtain or cite the adopting ruling before using `drift_exceeded` as acceptance.»

**Magistrate.** S class; no disposition.

**Texts.**
- «If the executed roster's gap exceeds max for a level, that level's status is NR(`drift_exceeded`) pending a balanced recapture.» [21/11 R11]
- «If a retry pushes a level's gap above max_drift_lever_slots in registered mode, set that level's `drift_exceeded: true` in the roster (refuter R11; the estimator lane maps it to not resolved (`drift_exceeded`)).» [B26 G3]
- «**D5b drift refusal: AFFIRM**, amend units» [21/10 §Q2]

### Q19 — May a cut-off report zero elapsed seconds? (OP-35; lens finding F14)

**Question.** An observation of `completed` or `cut_off` carries "elapsed seconds". Is zero allowed?

**Readings.**
- (a) Elapsed must be greater than zero. A block cut off before it used any time must be reported `not_started`.
- (b) Zero is allowed.

**Opus pick: (a).**
- A zero-second `cut_off` cannot be told apart from `not_started`.
- It would dodge Q5's rule that `not_started` records no elapsed time.

**Sol pick (09 F14).** No pick: «decide whether an immediate cut-off can be zero.»

**Magistrate.** «whether a zero elapsed time is allowed for a cut-off goes to the gate.» [13]

**Texts.**
- «an observation: `completed` with elapsed seconds, `cut_off` with elapsed seconds, or `not_started`» [45/21 §7(W)]
- «At the single stages the observation per single is `completed`, `cut_off` or `not_started`, with elapsed where applicable.» [45/21 §7(N)]

### Q20 — Confirm as representation: the digest chain

**Question.** Confirm the magistrate's encoding of the ruled "resulting sha256" and root replay as representation only, adding nothing and weakening nothing. Or amend it.

The encoding in plain words:
- The roster's digest is computed over the roster *minus* three fields: its own `sha256`, `registered_sha256` (the digest of the original packed roster), and each event's `sha256`.
- Each event's `sha256` then equals the resulting roster's digest without circularity, because event digests are outside what is hashed.
- A freshly packed roster sets `registered_sha256` equal to its own digest. Every later roster keeps the original's value.
- `reduce` checks `registered_sha256` against a fresh `pack` for every roster, with no exception for the original.
- The old `parent_sha256` field is dropped; the event list is the chain.

**Magistrate's text (verbatim).**
- «Preimage rule: the roster digest is `canonical_json_sha256` of the roster with the top-level `sha256`, the top-level `registered_sha256`, and every event's `sha256` removed.»
- «`event.sha256` equals the resulting roster's top-level `sha256` computed by that rule. It is the ruled "resulting sha256" and is not circular.»
- «`registered_sha256`: a root roster (no events) carries `registered_sha256 == sha256`. Every descendant carries the root's `sha256`. `reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]` uniformly, with NO root exception (lens F10 satisfied). Excluding it from the preimage weakens nothing, because it is itself verified against a re-pack.»

All from [13].

**Opus pick.** Confirm.
- `registered_sha256` and the event digests are each independently verified, by re-pack and by replay respectively.
- Leaving them out of the hashed data removes no check.
- At `requeue_overrun`'s entry, where no re-pack is possible, the prediction digest still binds the per-item predictions.

**Sol (09 F09/F10).** Asked for exactly this:
- «establish a non-circular digest encoding under which `event.sha256` equals the resulting roster digest»
- «either make `reduce` reject roots and remove the root R witness, or obtain a cold-gate exception defining root reduction.»

**Texts.** «The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`). `reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]`, replays every event from the root, and refuses unless the final digest matches its input roster.» [45/21 §7(R)]

---

## 3. What the ruling unlocks

Record 02b carries every question above as a `PENDING-GATE(OP-nn)` row or clause, written in the Opus or magistrate form. The checker seat is briefed from 02b as amended by this ruling. The checker must be committed before implementation starts, outside the implementer's write scope (45/21 §7(G)).
