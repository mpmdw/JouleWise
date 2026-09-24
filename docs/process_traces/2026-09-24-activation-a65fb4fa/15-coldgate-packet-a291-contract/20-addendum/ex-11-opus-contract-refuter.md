# 11 — Paired Opus contract refuter, A291-CONTRACT-01

Seat: Claude Opus 5.5, fresh session, 2026-09-24. Lens: CONTRACT. Target: the ruling's exact cure texts (Q1–Q20), as checker and implementer must build them. Read: `00-charge.md`, `10-coldgate-fable-ruling.md`, 45/21 §7, 45/10, 02b §§1–2. Code: `git archive c0998fdb` at `/tmp/ref-a291-c0998fdb`. Probe (executed): `/tmp/ref-a291-c0998fdb/probe/ruled_text_sim.py`. It applies the ruled decision rules literally to hand-built observations.

A **culprit** is a block whose elapsed time exceeds its own bound: `predicted_s` at the initial and whole-block stages ((W)), the derived worst case for singles ((N)).

## Findings

### R1 — BLOCKER. Culprits are stage-local in Q7 and Q8, but Q9 lets one envelope hold blocks of different stages

Ruled texts:
- Q7: *"If the envelope holds no culprit (no single advanced), every uncompleted or not-started single becomes the typed terminal state `unattributed_overrun`"*.
- Q8: *"The seal refuses an initial-stage `reschedule` decision in an event holding no initial-stage culprit."*
- Q9: eligibility excludes idle slots, whole-block envelopes and other models. It does not exclude envelopes holding blocks of another stage.

Standing text (W): a non-culprit is rescheduled *"provided the envelope holds a culprit"*. That text does not restrict the culprit's stage.

Reachable roster (model 8B, capacity 50 s, worst case 30 s):
1. Envelope 7 is reported. Parent A (level 1) is a culprit and advances to `whole_block`, alone in fresh envelope 40.
2. Innocent parent B (level 2, predicted 4 s) must be rescheduled. Every later pack envelope holds a level-2 parent of 8B, so M8 forbids them all. B goes to fresh envelope 41.
3. Envelope 40 reports A `cut_off` and A splits. Envelope 41 is eligible: its index is above 40, it is loaded, it has the same model, it holds no other level-1 parent, and 4 + 30 ≤ 50. So `A:single:0` lands in 41. Envelope 41 now holds an initial-stage block and a single.

Executed outcomes:
- **Case 1.** B completes late at 25 s, so B is a culprit. `A:single:0` is then cut off at 25 s, below its 30 s worst case. Result: `unattributed_overrun`, a terminal refusal. Another block's ordinary forecast miss loses the item and leaves its cell unresolved: a fault signal manufactured under correct instrumentation (contrary to 45/21 N1).
- **Case 2.** The single runs to 45 s, above its 30 s worst case, and advances. B (predicted 10 s) is cut off at 5 s and is innocent. (W) says reschedule, because the envelope holds a culprit. Q8's seal refuses that reschedule. The call raises, which contradicts Q7's "the call never raises".

Probe: `'8B:on:1:0:single:0': 'unattributed_overrun'`; `'SEAL REFUSES (Q8 …) -> call raises'`.

Replacement:
- Q7, replace the parenthetical with: *"(no observation in the envelope, at any stage, is a culprit)"*.
- Q8, replace the seal sentence with: *"The seal refuses any `reschedule` decision, at any stage, in an event whose observations contain no culprit at any stage. An observation is a culprit when its elapsed exceeds its block's bound: `predicted_s` for `initial` and `whole_block`, `worst` for singles. This includes a completed-late `keep`."*
- INV-35(a), add: *"… or an initial-stage `keep` with `late: true`, or an initial-stage `advance`"*.

### R2 — MATERIAL. The (N) numeric bound is false, and the seal would raise on a legitimate roster

Standing text (N), not amended: *"…so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it."* The arithmetic assumes each culprit event reschedules at most one block. One event can reschedule every other block in the envelope.

Counter-example (executed): capacity 120 s, worst case 30 s. One parent of four items splits into singles A, B, C and D, which share envelopes (45/10 D5 allows siblings to share).

| Envelope | Culprit | Reschedules | Cumulative |
|---|---|---|---|
| E1 | A | 3 | 3 |
| E2 | A | 3 | 6 |
| E3 | B | 2 | 8 |
| E4 | B | 2 | 10 |

The bound is 2 × 4 = 8, and E4 exceeds it. Each item has at most two culprit events: A and B have two each; C and D have none. The seal refuses and the call raises. C and D, which never overran, are stranded. This contradicts Q7's "never raises". 02b §5 also left factor 2's status as a "ruled constant" undecided.

Replacement for the (N) last sentence: *"Each innocent reschedule decision sits in an event holding a culprit (R1 definition); each single item has at most two single-stage culprit events and each parent at most one initial-stage culprit event; the seal refuses a roster violating either. The count of reschedule decisions in one event is at most (blocks in the reporting envelope − 1), so the total is finite; no separate numeric cap applies and factor 2 is not a constant."*

### R3 — MATERIAL. Two placement choices are undecided: where split singles go, and the order within one event

Ruled text (Q9): *"Reschedules and advancing singles (`single_problem`→`single_retry`) take the lowest eligible index, else a new envelope appended at `len(envelopes)`."*

- **Split singles.** The singles created by a split (whole_block→single_problem) are not named in that sentence. The stopped draft appends them to fresh tail envelopes (`c:scored_packer.py:273-284`). A seat must choose between lowest-eligible and fresh.
- **Order within an event.** One event can create several placements. "Lowest eligible" depends on the order in which they are placed. At capacity 90 s in the R2 roster, two of three placements fit E2 and the third goes fresh. The checker re-derives targets and the replay re-derives digests, so this order must be ruled.
- **Execution order inside an envelope**, which decides who is cut off, is also unstated.

Replacement: *"Reschedules, the singles created by a split, and advancing singles each take the lowest eligible index, else a new envelope appended at `len(envelopes)`. Within one event, placements are made in the order of the reporting envelope's `blocks` list, and a split's singles in ascending `j`. Each placement updates eligibility for the next. An envelope's `blocks` list is its execution order, and every placement appends to it."*

### R4 — MATERIAL. Q15 (no `n/a` cells) meets cells that Q12, Q13 and Q16 made "record, never refuse" or "pack only"

Q15: *"No invariant row/path cell may be `n/a`."* On the other side:
- Q12: *"never refuses on it"*.
- Q13: *"minima are a refusal only at `pack` (root roster)"*.
- Q16: the `reduce` column is provisional.

Consider INV-25 (planned minima) or INV-28 (drift at pack) on edge `single_problem→reschedule`. By ruling, nothing refuses there. No roster can then be a "violating witness that is caught", and the gate is unpassable unless a seat invents a meaning.

Q13's "(root roster)" is also ambiguous. It can be read as "only inside `pack`", or as "any roster with no events, at any entry".

Replacement, appended to Q15: *"Where the ruled consequence on a path is a recorded value, not a refusal, the violating witness drives that path into the violating state and asserts the recorded value (for example `planned_spread_shortfall`, `drift_lever_slots` > `max_gap`). A mutant that suppresses the record must be killed. A rule that refuses only root rosters is witnessed on every other path by a root roster in violation, fed to that path's entry and refused there."*

### R5 — MATERIAL. The consequence of `unattributed_overrun` is left out of (P) as Q12 extends it

- (W): *"its cell is unresolved until a registered recapture"*.
- Q12 extends (P) only with `ceiling_violation`, `spread_exceeded` and `drift_exceeded`.

Counter-example: a cell has 8 parents, and one item ends in `unattributed_overrun` (now reachable at the single stages too, Q7). Seven parents are fully counted and 7 ≥ 5, so `spread_exceeded` stays false. No ruled estimator status makes the level NR. A293 would resolve a level that (W) says is unresolved.

Replacement, appended to Q12's precedence sentence: *"A level any of whose cells holds an `unattributed_overrun` refusal is NR(`unattributed_overrun`) unless NE(`ceiling_violation`) applies; NR reasons accumulate."*

### R6 — MATERIAL. Q4(iii) names `roster.models`, but (S) forbids roster copies of registered values

Ruled text (Q4(iii)): *"The model order everywhere (`roster.models`, idle assignment, tie-breaks)…"*

The conflict:
- The roster key set in 02b §2.3 has no `models` key.
- `role_to_model_id` is registered, and (S)/INV-03 says *"no roster copies of registered values"*.
- The stopped draft did carry `roster["models"]` (`c:scored_packer.py:200`).

A checker built on 02b flags the key; an implementer following Q4 adds it.

Replacement: *"(iii) The model order everywhere (iteration, idle assignment, tie-breaks) is by role, derived from `registration.role_to_model_id`: the `"8B"`-role model first, the `"1.7B"`-role model second. The roster carries no `models` key."*

### R7 — MATERIAL. Key names and types conflict under 02b's exact roster key set

- Q12 writes *"`planned_drift_lever_slots[level]`"*. Q14 and 02b §2.3 write `drift_lever_slots` for the same planned value.
- Q13 adds *"`planned_spread_shortfall[cell]: true`"* with no key format for a (model, level) pair, no type, and no rule for "absent vs false".

The checker enforces an exact key set, so it and the implementer will diverge.

Replacement:
- Q12: *"records `drift_lever_slots[level]` (the PLANNED lever, 02b §2.3)"*.
- Q13: *"`planned_spread_shortfall` is a roster key: an object with one key per cell, `"{model_id}:{level}"`, value bool, recomputed at every seal exit; `pack` refuses when any value is true."*

### R8 — MATERIAL. Replay is not stated to re-derive decisions

Q20: *"Replay recomputes the roster after each event…"* The text does not say whether replay re-runs the decision rules or applies each event's recorded `decision` and placements.

If replay applies recorded decisions, a forged decision passes `reduce` with consistent digests. Example: an item recorded `keep` although its elapsed exceeds `worst`, so the window is counted. Applying recorded results would also need `_digest` outside `_seal`, which contradicts Q20's own sentence.

Replacement: *"Replay calls `requeue_overrun(registration, roster_{k−1}, events[k].envelope_index, observations_k)`, with each observation stripped of `decision`, and asserts that the re-derived decisions and placements equal the recorded ones and that `events[k].sha256` equals the re-derived value."*

### R9 — MATERIAL. Runner sequencing leaves envelope r+1 open to a capture that has already started

Q9/Q10 make envelope `r+1` eligible for work placed by the report of envelope `r`. The grid has a fixed pitch (08 F1), so the runner may start `r+1` before `requeue_overrun(r)` returns. New work would then land in a capture already running, the defect 45/21 A2 exists to prevent. Neither the texts nor the CARRIED list assigns this.

Replacement: add a CARRIED row, *"runner lane: envelope `r+1` does not start until `requeue_overrun` for `r` has returned and its roster is loaded; otherwise the runner reports `r+1` `not_started` in full"*.

### R10 — NIT. The executed lever is undefined when a model has no counted parent at a level

Q12 computes the executed lever as a mean of positions. With zero counted parents for one model, that mean does not exist.

Replacement: *"the executed lever is null, and `drift_exceeded` is not set; that cell is already `spread_exceeded` (0 < 5) under (X)."*

### R11 — NIT. Q6's "the roster's voided attempts" names no field

Replacement: *"its placement's `block_id` moves to that envelope's `voided_block_ids`; the voided window key is (`block_id`, that placement's `attempt`)."*

### R12 — NIT (optional physics guard, not ruled)

A sequential envelope cannot run longer than its interior. Suggested addition: *"the seal refuses an event whose Σ `elapsed_s` exceeds `interior_s` (`invalid_elapsed`)."*

## AGREE

- AGREE, checked sound: Q1, Q2 (`from_mapping` is the only constructor, `c:scored_registration.py:65, 89`), Q3, Q5, Q11, Q14, Q17, Q18, Q19.
- AGREE with the cure named: Q4 (R6), Q6 (R11), Q7 and Q8 (R1, R2), Q9 (R3), Q10 (R9), Q12, Q13 and Q15 (R4, R5, R7), Q16 (R4), Q20 (R8).
