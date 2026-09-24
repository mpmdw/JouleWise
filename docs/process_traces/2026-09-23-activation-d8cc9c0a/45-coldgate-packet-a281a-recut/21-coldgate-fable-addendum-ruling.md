# 21 — Cold Fable addendum ruling, A281A-RECUT-01 (refuter objections to cure text)

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-d8cc9c0a-r3` at `95e6e880`. Code judged at `c0998fdb`. Written 2026-09-23 ~22:25 PDT.

## 0. Disclosure, pins, method

Auto-loaded: `~/.claude/CLAUDE.md`, worktree `CLAUDE.md`, memory index `MEMORY.md` (pointers only); none used; nothing outside this packet directory opened. `ex-21-10` (digest `b8a66c41…50e2d`) read only for its NE sentence (A6).

Validator run 1 (charter `…5d82`, deliberate typo): `REFUSE`, `charter_trusted_observed_mismatch`, rc 2. Run 2, expected charter `099de884…5d81`, packet `51bd0f4f…4355`: `PASS`, rc 0, three exhibits, all digests equal to the manifest. Method: `shasum -a 256` reproduced both values. Named suite in the `git archive c0998fdb` copy `/tmp/coldgate-r3-c0998fdb`: `Ran 13 tests … OK`.

Executed probes (`/tmp/coldgate-r3-c0998fdb/probe_addendum.py`, registered fixture: capacity 50 s, worst 30 s/item, block size 2):
- PA `pack` twice → equal `sha256` (deterministic, `random.Random(0)`, `scored_packer.py:67`).
- PC whole-block requeue of `1.7B:on:1:0` then split: envelope 11 is `loaded`, `blocks []`, `voided_block_ids ['1.7B:on:1:0']`; singles in 12, 13. Probe (c) CONFIRMED: the "empty" envelope is the retry's own already-run capture. Retry keeps `predicted_s` 4.0 (`:316`).
- PD min(Σworst 60, capacity 50) = 50 = maximum observable elapsed → `elapsed > predicted_s` unsatisfiable. CONFIRMED.
- PF roster with a foreign item id and `predicted_s` 1001, digest recomputed: accepted by `requeue_overrun` (`_verify_roster` `:165-192` checks digest and keys only). Probe (b) CONFIRMED.
- PG `:351` refuses `elapsed <= 0`; `:340-346` leave an unlisted mate in the already-run envelope. R4 verified by code reading only; my executed mate probe was invalid (siblings in separate envelopes) and is NOT relied on.

## A1 — whole-block row: REJECT the ruling's text, ACCEPT the refuter's cure, AMENDED (BLOCKER stands)

Deciding exhibit: the ruled words "that did not complete" plus the innocence refusal. Refuter's example (A predicted 20 completes at 35; B predicted 25 cut at 15) gives input {B: 15}, refusal, and B's items with no legal state. Amendment: observations are recorded so the seal and checker re-derive the decision; completed-late blocks are marked without a state change. Text §7 (W).

## A2 — empty envelopes and placement: ACCEPT the refuter, strike F4's reuse clause (BLOCKER stands)

PC is decisive: "no empty loaded envelope" would refuse every post-split roster, and reuse would put new work into a capture that has run (envelope 11), falsifying positions and the drift lever. Placement is ruled as index monotonicity (`_append` `:282` complies; the seal enforces). Text §7 (E).

## A3 — gate criterion: ACCEPT R1, AMENDED with definitions (MATERIAL)

`envelope_s`, `offset_s`, `pitch_s` reach only coherence checks (`scored_registration.py:123-130`) and roster copies (`scored_packer.py:264-265`) → CARRIED to the runner lane. §7 (G) defines "validation-only" and the path list so the seat chooses neither.

## A4 — checker authorship, seal contents, replay: ACCEPT R2 and R3 (MATERIAL)

PF shows the requeue entry trusts any well-formed roster; PA shows replay is feasible. Text §7 (S, R).

## A5 — reservation vs prediction, split trigger, not_started: ACCEPT (MATERIAL)

PD is decisive for `reserved_s`. The whole-block retry runs alone (ruling 10 §Q3 row 5), so non-completion within its reservation is the split trigger and no innocence test applies. Text §7 (W, T, N).

## A6 — precedence and wording: ACCEPT R5 and both NITs (MATERIAL)

Ex-21-10 line 23 makes a group NE(`ceiling_violation`) on any terminal item; `spread_exceeded` makes the level NR. Missing evidence precedes replication shortfall. Text §7 (X, P).

## 7. Final texts (paste verbatim into the A281a′ brief; supersede ruling 10 §Q2 seal list, §Q3 rows 5–6, §Q4 `spread_exceeded`, §Q5 F4)

**(W) Whole-block stage.** "`requeue_overrun` at the initial and whole-block stages takes, for every block in the reporting envelope, an observation: `completed` with elapsed seconds, `cut_off` with elapsed seconds, or `not_started`; the envelope records every observation. A completed block keeps its window; if its elapsed exceeds its `predicted_s` it is marked `late: true` and is a culprit. An uncompleted block whose elapsed exceeds its `predicted_s` is a culprit and advances one stage. An uncompleted or not-started non-culprit is rescheduled at its current stage without advancing, provided the envelope holds a culprit. If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun` (a `terminal_refusals` entry; its cell is unresolved until a registered recapture); the call never raises for innocence. The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged."

**(T) Split trigger.** "A whole-block retry advances to the split stage when its attempt did not complete within its envelope; its observed elapsed is recorded. Each single is packed at `reserved_s = predicted_s = the item's derived worst case`."

**(N) Single stages.** "At the single stages the observation per single is `completed`, `cut_off` or `not_started`, with elapsed where applicable. A single whose elapsed exceeds its derived worst case advances (`single_problem` → `single_retry` → `ceiling_violation`). Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one. Each innocent reschedule is caused by one culprit event in its envelope and each item has at most two culprit events, so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it."

**(E) Empty envelopes and placement.** "An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope. An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's. The split stage never reuses the whole-block retry's envelope."

**(S) Seal contents.** "`_seal(registration, roster)` runs on the input at the entry of `requeue_overrun` and `reduce` and at every public exit of `pack` and `requeue_overrun`. It checks: M8 by parent (ruling 10 §Q4); five-parent and five-envelope minima; no roster copies of registered values; envelope model homogeneity; (E); capacity by `reserved_s`; `predictions_sha256`; drift by parent; item conservation (per model, every registered item is in exactly one block that is neither superseded nor terminal, and that block is in exactly one envelope, or is in exactly one terminal refusal and no envelope); stage legality (each block's `retry_stage` history follows the closed edge list in (G)); the bound in (N)."

**(R) Replay.** "The roster carries an append-only `events` list, one entry per `requeue_overrun` call (block id, observations, resulting `sha256`). `reduce` asserts `registered_sha256 == pack(registration, predicted_decode_s)["sha256"]`, replays every event from the root, and refuses unless the final digest matches its input roster."

**(G) Gate criterion.** "Every registration field and every ruled constant is listed by the perturbation sweep as CONSUMED, with an executed boundary witness on every path in the closed path list, or as CARRIED in the closed list. A validation-only witness, one whose refusal comes from the field's own range, type or coherence check before the field meets roster content, does not count. Constants are patched at their module attribute; a scan finds no literal duplicate. Every magistrate invariant row has an executed violating witness on every path. Closed path list: `pack`; `requeue_overrun` on each edge initial→whole_block, initial→reschedule, initial→unattributed_overrun, whole_block→single_problem, whole_block→unattributed_overrun, single_problem→single_retry, single_problem→reschedule, single_retry→ceiling_violation, single_retry→reschedule; `reduce`. A 'no effect' cell needs a contract-lens-reviewed reason. `_seal` is the sole exit of pack and requeue and the entry of requeue and reduce; the seeded stress run against the independent checker reports zero violations; the operand, boundary and guard-deletion sweeps kill every mutant. The checker is written by a different seat from the ruling text, committed before implementation starts, outside the implementer's WRITE_SCOPE. Every CARRIED row is a mandatory CONSUMED row in its consumer lane's gate." CARRIED additions: `envelope_s`, `offset_s`, `pitch_s` → runner lane.

**(X) spread_exceeded, cause-agnostic.** Replace "because a parent lost an item to a terminal ceiling_violation after capture" with "for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)".

**(P) Precedence.** "When a level carries both NE(`ceiling_violation`) for a group and `spread_exceeded`, NE(`ceiling_violation`) takes precedence in the A281b total table and `spread_exceeded: true` is recorded alongside; a level with `spread_exceeded` and no NE is NR(`spread_exceeded`)."

## 8. Tiers and disagreements

- **BLOCKER B1** (A1) and **B2** (A2): ruling 10's sentences must not reach the A281a′ brief; cured above.
- **MATERIAL M1** R1 (A3), **M2** R2+R3 (A4), **M3** `reserved_s` and `not_started` (A5), **M4** precedence (A6), **M5** `late`, `reserved_s`, observations and `events` are new roster keys; the brief adds them to the key sets and the matrix.
- **NIT N1** `unattributed_overrun` is unreachable under correct instrumentation (Σ elapsed ≤ Σ predicted ≤ capacity); it is a fault signal the runner lane must surface, not a retry path.

Disagreement with the lead: none (the charge took no position). Ruling 10 (predecessor instance): A1 and A2 reversed as above; every other ruling 10 text stands. Packet hygiene: adequate; the refuter's probes reproduced and its quotations of ruling 10 match the sealed file.
