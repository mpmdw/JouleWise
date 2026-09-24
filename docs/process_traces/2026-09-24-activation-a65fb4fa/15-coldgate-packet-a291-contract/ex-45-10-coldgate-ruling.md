# 10 — Cold Fable gate ruling, A281A-RECUT-01

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-d8cc9c0a-r2` at `b28322ab`. Code judged at `c0998fdb`. Written 2026-09-23 22:00 PDT.

## 0. Disclosure, pins, method

Auto-loaded before I acted: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (pointers only). None used as evidence; no memory file, run state, queue, council log or trace outside the packet was opened.

Validator run 1 (charter sha ending `…5d82`, the deliberate typo): `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2, expected charter `099de884…5d81`, packet `8b5f8704…6fe1`: `PASS`, rc 0, ten exhibits, every observed digest equal to its manifest entry. Independent method: `shasum -a 256` on both files reproduced both expected values. Named suite in the `git archive c0998fdb` copy at `/tmp/coldgate-c0998fdb`: `Ran 13 tests … OK`.

Executed probes (`/tmp/coldgate-c0998fdb/probe_gate45.py`, `probe_gate45b.py`, registered-mode fixture from `tests/test_scored_registration.py`):
- P1 two disjoint item sets packed under one registration, both accepted (`item_set_sha256` has no consumer: grep of packer and reducer returns nothing).
- P2 `ceiling_s` 30→40 and `scorer_id` changed: roster identical with digest fields removed.
- P3 `min_blocks_per_cell=1, min_envelopes_per_cell=1` accepted (`scored_registration.py:121-122`).
- P4 `pack` accepted an item predicted at 40 s against a derived worst case of 30 s (`scored_packer.py:239-242` checks capacity only).
- P5a whole-block requeue with `failed_prediction_s=1e-9` accepted; the retry is re-appended with the failed prediction `predicted_s=10.0` (`:316`).
- P5b with capacity 90 s, two sibling singles of one parent share tail envelope 12 (`_append`, `:273-284`, has no cell check). P5c two parents' singles never shared a tail (call order only: `tail_start`, `:274`); the split left an EMPTY loaded tail envelope 13 in the roster.
- P6 the terminal `ceiling_violation` attempt's window is REFUSED by `reduce` (`scored_reduce.py:71-74`), so the caller must filter it out.
- P7 four consecutive innocent single-stage requeues (elapsed 1 s < worst 30 s) accepted; stage unchanged, attempt 6, 18 envelopes.

Exhibit 39's 5.47 vs 2.8 drift numbers and the 160/264 stress counts are the seats'; not reproduced here.

## Q1 — D1, D2: AFFIRM

D1 is verified, not merely argued: P1–P5 show four consumption-side gaps plus two fields with no consumer. D2: charter §9 makes the next spend after two same-signature rounds a consult or redesign. The consult ran (40, 44); A281a′ is a redesign (seal on every exit, derive-not-copy, matrix from ruling text), not a round three under brief 26. Conditions: (1) A281a′ runs under a NEW brief carrying §Q2–Q4 below verbatim; (2) its delta re-audit returns to a cold gate before merge (trigger 1 still applies: it fixes the same defect class); (3) A281c does not start until A281a′ is gated; (4) the AP-5M sentences in §Q4 land in the AP-5M text in the same PR as A281a′ or earlier, so registration and code do not diverge (21-10 Q4 condition). Stopping the lane entirely is rejected: nothing else is pending that the re-cut depends on.

## Q2 — D3 acceptance shape: AFFIRM with amendments; gate criterion AMENDED

Amendments (each MATERIAL):
- (1) Seal: `_seal(registration, roster)` is the ONLY caller of `_digest`; the AST test asserts that, and that every `return` statement in every public function of packer is `return _seal(...)`; `reduce` calls `_seal` first. Seal checks, on the executed roster: M8 by parent (§Q4 text), the five-parent and five-envelope minima, no copies (roster carries only `registration_sha256`), every envelope's blocks share the envelope's model, no empty loaded envelope (P5c), capacity per envelope, `predictions_sha256`, and drift by parent.
- (3) Matrix: the magistrate writes the invariant rows from 08, 21-10 and this ruling INTO the brief; the seat writes the field rows; the contract lens checks the invariant rows against the ruling text, not the code. Each witness is a boundary witness: the second value is the smallest change that crosses a ruled threshold (Opus 44 failure mode (c), slack fixtures). "Output changes" is judged with digest fields removed and with linked fields jointly re-derived.
- (4) The independent checker is a separate module that imports nothing from the packer.
- Mutation: the operand-collapse sweep is kept and a boundary sweep (`>`↔`>=`, `<`↔`<=`) and a guard-deletion sweep (each `if …: raise` removed) are added; 39 S6 shows the first sweep misses both. Counts are evidence for the sweeps, not acceptance for the seal.

Gate criterion, ruled text: *"Every registration field is listed by the perturbation sweep as CONSUMED with an executed boundary witness on every path it governs, or as CARRIED in the closed list below; `_seal` is the sole exit of pack and requeue and the entry of reduce; the seeded stress run against the independent checker reports zero violations; the operand, boundary and guard-deletion sweeps kill every mutant."*

Closed CARRIED list (field → consumer lane). Anything else with no effect is a defect.

| Field | Consumer |
|---|---|
| `alpha`, `n_boot`, `seed`, `floor_j`, `anchor_j`, `declared_sensitivities`, `arm_to_family` (family) | A281b estimator |
| `sizing_receipt_sha256` | scored-night arm gate (runner lane, ID assigned by the magistrate): compares the receipt file's digest; A281a′ sees only `predictions_sha256` (§Q3) |
| `ceiling_s` | runner lane, as the per-attempt kill timeout; registration keeps the inequality derived worst case ≤ `ceiling_s` ≤ capacity |
| `scorer_id` | A281c (row binding) and the runner (stamps rows) |

Identity fields (`schema`, `registration_id`, `plan_id`) are CONSUMED: their witness is that a roster sealed under the old digest is refused by every consumer under the new registration.

## Q3 — D4 field by field

| Item | Verdict | Ruled text or reason |
|---|---|---|
| Constants: levels, merge_order, min_correct 3, holm_m 5, both spread minima 5, cap_bound_fraction 0.20, retry_stages | AFFIRM | Module constants pinned by `schema`; one test asserts equality to the AP-5M text. P3 is the forcing case. |
| Register `item_ids_by_level`; derive `item_set_sha256`, `n_per_level` | AFFIRM | `pack(registration, predicted_decode_s)` takes no items argument; `item_set_sha256 := canonical_json_sha256([ids in level order])` is a derived roster field. |
| Derive `max_drift_lever_slots` | AFFIRM | Formula at `scored_registration.py:169-170` becomes the definition; the field is removed. |
| `ceiling_s` delete | AMEND | CARRIED, not deleted (table above). Reason: only the registration can assert kill timeout ≥ derived worst case; without it a runner may kill a legitimate long item and manufacture a false `ceiling_violation`, a physics/evidence failure. |
| Whole-block stage: observed `elapsed_s` vs roster `predicted_s` | AFFIRM, AMEND text | *"`requeue_overrun` at the whole-block stage takes the observed elapsed seconds of every block in the envelope that did not complete. A block whose elapsed exceeds its roster `predicted_s` advances to `whole_block`; a block cut off within its own `predicted_s` is rescheduled at its current stage without advancing (39 N6). If no block exceeded its prediction the call is refused (`innocent_requeue`). The whole-block retry is scheduled alone in a fresh envelope and packed at min(sum of its items' derived worst cases, capacity) (P5a: today it is packed by the failed prediction)."* |
| Split stage: per-item observed elapsed | AMEND | Per-item elapsed is NOT observable for items that never ran after a cut-off (`:318-327` forces the caller to invent positive numbers, a class-iv smell). Text: *"The split stage takes the block's observed elapsed seconds only, requires it to exceed the roster `predicted_s`, and packs every single at its derived worst case."* |
| `predicted_decode_s` bound; `predictions_sha256` | AFFIRM, AMEND mechanism | The pure module cannot open the sizing receipt. Add registration field `predictions_sha256` (pilot-nullable, required in registered mode); `pack` refuses any item above its derived worst case (P4) and refuses when `canonical_json_sha256(predicted_decode_s restricted to the registered items)` ≠ `predictions_sha256`. Extra predictions are refused, not ignored (Sol 34 (d)). |
| Rows carry `scorer_id` and both digests; reducer refuses mismatch | AFFIRM | A281c. Windows carry both digests too (39 S5). |

## Q4 — D5: AFFIRM the lead (Opus). D6: AFFIRM with one amendment

D5. M8's purpose is replicate independence, and the replicate is the parent block (08 F2(a) pairs on the parent; 21-10 affirmed). Siblings of one parent in one envelope reconstruct the parent's original single-envelope capture (P5b′); separating them buys no independence and costs an envelope per single. Sol 40's reading is the literal wording; the wording is what §Q4 text amends. Cross-parent sharing is today unreachable only by call order (P5c) and must be sealed.

D6. AFFIRM parent-unit M8b, `spread_exceeded`, parent-unit drift, and refusal of innocent requeues. AMEND: at the single stages an innocent mate re-queued by a guilty event is bounded by the guilty events (at most two per item), so P7's unbounded chain closes once `innocent_requeue` refusal exists; no separate cap is needed.

Exact AP-5M sentences:

*M8 on retry tails.* "M8 applies to parent blocks. A parent block is a block scheduled by the initial packing; single-problem blocks made from it under M12 are pieces of that parent, not new replicates. No two parent blocks of one cell share an envelope at any stage, initial or retry. Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity. The five-block and five-envelope minima count parent blocks and the distinct envelopes holding their executed windows; a split never adds to either count."

*spread_exceeded.* "A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them, because a parent lost an item to a terminal ceiling_violation after capture. The cell carries `spread_exceeded: true`, its numbers are reported, and its level is not resolved (`spread_exceeded`) until a registered recapture. Before capture the same shortfall is a packing refusal."

*Parent-unit drift lever.* "The drift lever of a level is the absolute difference, in envelope slots, between the mean position of its 8B parents and the mean position of its 1.7B parents. A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing. At pack time every item of a parent sits in one envelope, so its position is that envelope's index."

## Q5 — what both consults missed

- **MATERIAL F1.** Whole-block retry packed by the failed prediction (P5a, `:316`). Cure in §Q3 row 5.
- **MATERIAL F2.** Split stage demands per-item elapsed for items that never ran (`:318-327`). Cure in §Q3 row 6.
- **MATERIAL F3 (A281c).** The terminal attempt's executed window is refused, not excluded by rule (P6c), contradicting G4 "excluded by rule, never by caller choice". Text: *"A window for a terminal ceiling_violation attempt is accepted, recorded on the terminal refusal as `gross_j`, and never enters a cell sum."*
- **MATERIAL F4.** A split leaves an empty loaded tail envelope in the roster (P5c, envelope 13): a capture with no blocks that is not an `idle_slot` and will shift every later index. Cure: `_seal` refuses an empty loaded envelope; the split stage reuses the whole-block retry's envelope for its singles when they fit.
- **NIT N1.** `_append` merges additions into the last tail without checking model; safe today within one call, sealed by §Q2 (1).
- **NIT N2.** `pack` and `_executed_gaps` compute the lever by different units (bucket vs block, `:78-81` vs `:201-204`); they coincide only because the initial arrangement holds one block per cell per envelope. One function, the §Q4 parent-unit definition, on both paths.

## Findings tier summary

- **BLOCKER B1.** The four class-iv gaps at c0998fdb (P1, P3, P4, P5b) plus the two ignored fields (P2). Cure: A281a′ under §Q2–Q4.
- **MATERIAL M1–M4.** F1–F4 above. **MATERIAL M5.** `ceiling_s` deletion (D4) reversed to CARRIED. **MATERIAL M6.** `predictions_sha256` as a registration field, since the pure module cannot read the receipt.
- **NIT N1, N2** above. **NIT N3.** Exhibits 39 and 44 are magistrate transcriptions; their numeric claims are unreproduced here. Packet hygiene otherwise adequate: the contrary seat (Sol 40) is present on the D5 split and the lead's picks are labelled argument.

Disagreement with the lead's labelled disposition: `ceiling_s` (D4, keep as CARRIED); split-stage per-item elapsed (D4, block-level only); `predictions_sha256` mechanism (D4). All other picks concur.
