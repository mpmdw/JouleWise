# 11 — Cold Opus contract refuter on ruling 10 (A291-FIX2-01), Final texts 1–8

Refuter: Claude Opus 5.5, cold, 2026-09-24. Read: 00, 10, ex-02d, ex-31, and the code at `20cd29de`. Probes ran in a `git archive 20cd29de` copy under `/tmp/refuter-7370d0fb` (probe.py, probe2.py, sim.py; removed after use), cache cleared per call.

## 0. Executed evidence

- **X1** (probe.py, R1). The ruling's R1 recipe was run as written, and the new envelope's `blocks` was set to `[id]`. `_structure` passes; at 20cd29de the seal then refuses `stale_derived`, and the checker reports INV-11. Under B5's order, INV-11 (step 3) comes before stale (step 6), so R1 → `inv_11` holds. Variant: the copied placement is added but `blocks` is left empty. That gives `inv_03` "placement ownership", not `inv_11`.
- **X2** (probe.py, R2b as ruled). Split roster: production route, 11 events, singles `large:decode:1:0:single:{0,1}`. Two variants were run:
  - Delete a live single from `blocks`, `placements` and the envelope lists, then reseal: the seal refuses **`inv_18`** "event placement target", because deleting from `placements` shifts the `Event.placements` indices. The checker reports only INV-52.
  - Delete it from `roster.blocks` only: the seal refuses **`inv_52`**, from a KeyError at :154.
  - Neither variant can reach `inv_12`. Both refusals come from `_structure` rows that run before the INV-11/12 rows B5 appends. Even with a perfect cleanup, the orphaned item fails INV-11 before INV-12 is checked.
- **X3** (probe.py). Set `superseded` to false on the split parent, then reseal. The checker reports **INV-12 and no INV-11**, which is the §5 predicate reading 02d:468. `_structure` passes, so under B5's order the seal would refuse `inv_12`. Under the ruled text of 45/21 §7(S) ("exactly one block that is neither superseded nor terminal"), the same mutant is an INV-11 violation.
- **X4** (probe.py, R2/R3). E1 resealed: `_structure` passes and the checker reports INV-11, so under B5 this gives `inv_11`. E1 unresealed gives `stale_derived` today and `inv_02` under B5 step 2. Both are as ruled.
- **X5** (probe2.py, R4a). The ruled route, extended with single 0 completed at `1.01 × worst`, produces E6 then E8. Result: one `ceiling_violation`, `check_roster == []`, `drift_lever_slots["1"] == 1.5999999999999996`, and `planned_spread_shortfall["large:1"]` is true.
  - The hand literal is `abs(sum([13,2,4,6,8])/5 - sum([1,3,5,7,9])/5)`.
  - The "fully non-terminal" counterfactual gives **0.0**.
  - So R4a is feasible and discriminating.
- **X6** (read). `class PackingRefusal(ValueError)` is at :17. `_live_index`, `_parent_facts` and `_lever` do not exist at 20cd29de; grep over `joulewise/` and `tests/` finds none. `executed_status` at :418-455 does its own division at :442 and :452, and no try boundary covers it.
- **X7** (read). `tests/test_scored_packer.py` (P's scope) imports from K's files: `run_case` (stress, :11), `r2_four_envelope_roster` (checker tests, :10), `check_*` (checker, :8). Its E1–E11 gate witnesses read fixed modes at a fixed seed (:19, :30-40), e.g. `edge_counts[7]['E7']`, `[6]['E9']`.
- **X8** (sim.py, E3 normalisation, keywords kept). Checker `_derived` (33 lines) against packer functions it is not a transcription of: 12/33 = **0.36** against six of them (about 200 lines); 2/33 = 0.06 against `_seal` and `_observations` (54 lines). The ratio tracks the size of the packer set, not copying.
- **X9** (python). Checker `digest(r)` equals `sp._digest(r)` on a root roster and on a mutated roster, so the `reseal` helper is sound.

## 1. Findings

**F1 — BLOCKER — R2b cannot pass as written (Final text 6).** X2: every deletion variant is refused by an earlier `_structure` row (`inv_18` or `inv_52`). Even a clean deletion fails INV-11 first, because B5 step 3 orders INV-11 before INV-12. The only INV-12-only mutant found is X3. Replacement for R2b: «R2b: on the production-built split roster of R4a, set the split parent's `superseded` to `false`, `reseal` → `requeue_overrun(reg, r, pending, all-keep)` raises `inv_12`, and `check_roster` reports INV-12 and not INV-11. Counterfactual: a seal without INV-12 passes this roster. Call site: `requeue_overrun` entry `_seal` step 3.»

**F2 — MATERIAL — INV-11 has two readings; Final text 3 pins the weaker one without saying so.** The 02d:468 predicate counts only blocks that satisfy all three conditions. The 45/21 §7(S) ruled text, which comes first under §0.1 precedence, requires exactly one non-superseded, non-terminal block, and then requires that block to be live. The two readings agree on every legal roster. They disagree on X3 (inv_11 versus inv_12). P and K will each have to choose, and F1's replacement depends on the choice. Neither reading is unsafe: under the predicate reading, X3 is still refused (inv_12), and a stray voided non-superseded block is refused by the B3 relation rule.
Replacement, added to Final text 3: «INV-11(a) is evaluated as 02d:468 literally: count the blocks that contain the item AND have `superseded == false` AND are not terminal AND have their id in exactly one envelope's `blocks`; (a) holds iff that count is 1. Checker and packer use this reading. The 45/21 §7(S) difference (a non-superseded, non-terminal block not in any envelope) is refused by INV-12 or by the A291-POP-1 relation rule; it is recorded as a residual for the magistrate, not decided by a seat.»

**F3 — MATERIAL — B6 and Final text 2 disagree on the clauses, and one reading silently rewrites codes.** B6 says `_checked_derived` wraps `_derived` in "the two except clauses". Final text 2 lists three. Because `PackingRefusal` is a `ValueError` (X6), the two-clause reading turns the B3 relation refusal `inv_11` into `inv_52 "malformed roster"`.
Replacement for Final text 2, second sentence: «`_checked_derived` has exactly three handlers, in this order: `except PackingRefusal: raise`; `except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError) as exc: raise PackingRefusal("inv_52", "malformed roster") from exc`; `except ArithmeticError as exc: raise PackingRefusal("inv_52", f"internal:{type(exc).__name__}") from exc`. `_seal`'s try block uses the first two handlers in the same order.»

**F4 — MATERIAL — the executed arithmetic sits outside the boundary (the E6 pattern again).** Final text 2 protects `_derived` only. But R4c bans `Div` in `executed_status`, so the executed lever must divide inside `_lever`, which `executed_status` then calls directly. That path has no ArithmeticError backstop and no fuzz property (fuzz (a) covers only `requeue_overrun`).
Replacement, added to Final text 2: «`_checked_derived(registration, roster, captured_window_keys=None)` is the sole caller of `_parent_facts` and `_lever` as well as `_derived`. `executed_status` obtains every executed value through it with its `captured_window_keys`. Fuzz property (a) extends to `executed_status(reg, M, p, keys)` on every final (fully reported) mutant, with `keys` = seeded 75 % of live window keys: it returns or raises `PackingRefusal`, nothing else.»

**F5 — MATERIAL — `_parent_facts` and `_lever` are named by R4b, R4c and B4 but never specified; the record lacks the fields the refusal detail needs.** A291-POP-1's record is `(n_items, n_terminal, indices)`, yet the relation refusal's detail string interpolates `{parent_id}`, and grouping needs model and level. R4b's patch "returning one record `(2, 0, [])`" has no defined call shape (X6: the functions do not exist).
Replacement, a new Final text 2a: «`_parent_facts(registration, roster, captured_window_keys=None) -> list[dict]` returns one dict per parent in `roster["blocks"]` order, with keys exactly `parent_id, model, level, n_items, n_terminal, indices` as defined in A291-POP-1. With `captured_window_keys is None`, an item's index is recorded iff its owner has a live placement. Otherwise it is recorded iff that placement's `(block_id, attempt)` is in the keys.
`_lever(registration, facts, *, executed)` returns `(cell_flags, lever)`, where `cell_flags` is the planned shortfall or the executed `spread_exceeded`. It applies the gate of A291-POP-1 for the mode, and the relation check before any division.
R4b patches `sp._parent_facts` to return `[dict(parent_id="p", model=<8B id>, level=1, n_items=2, n_terminal=0, indices=[])]`.»

**F6 — MATERIAL — R4c can pass vacuously.** Final text 4 names `_live_index`, but the function is `_live` (X6). If P keeps `_live`, R4c's "no Name `_live_index`" is true of every function, and the check never fires. The Subscript test is also evaded by `bs = roster["blocks"]; for b in bs:`.
Replacement for R4c: «Rename `_live` to `_live_index` (Final text 4 applies to it). AST test: `_live_index` and `_live` are referenced only inside `_parent_facts`. `_derived`, `_lever`, `executed_status`, `_seal`, `_checked_derived` contain no Subscript or `.get` call with constant `"blocks"`, `"placements"` or `"terminal_refusals"` anywhere (not only in loop iterables), and no `Div` outside `_lever`. `_parent_facts` is the only function other than `_structure`, `_replay_roster`, `pack`, `requeue_overrun`, `_eligible`, `_place` and `_new_envelope` that reads `"placements"`.»

**F7 — MATERIAL — fuzz property (c) is vacuous; (e) is undefined on final rosters.**
- Each operator is also submitted unresealed, and those submissions are always refused `inv_02`. So "every operator refused ≥ 1" passes for an operator the seal never catches.
- `requeue_overrun` on a fully reported roster refuses `report_order` after seal and replay. Under (e) that is a spurious "finding", and it also breaks B6's "legal corpus raised zero refusals".
- Operator (5)'s extent is unstated (X2 shows the variants refuse different codes).
- (e) does not say whether a finding fails the test.
Replacement:
- «(c) for every operator, at least one RESEALED submission is refused with a code other than `inv_02`.»
- «Mutation bases are the intermediate rosters that have a pending loaded envelope; `requeue_overrun` gets that envelope with all-keep observations (`completed`, `elapsed_s = 0.01`). Final rosters go to `verify_executed_roster` instead.»
- «Operator (5) removes one single from `blocks` only.»
- «(e) is a hard test failure listing (operator, seed, code), except for codes `inv_38`, `inv_39` and `report_order`.»
- «(9) picks `k < len(events) - 1` when `len(events) ≥ 2`, and is skipped otherwise.»

**F8 — MATERIAL — P's gate witnesses depend on files K rewrites (B9, Final text 8).** X7: P's E1–E11 tests read `run_case(mode, Random(291013))` per mode. K "switches the stress module to the new generator", and B8's variation rule only guarantees E1–E11 "in aggregate". Integration can silently break or re-point the thirteen gating witnesses. `r2_four_envelope_roster` (in K's file) feeds P's R2 test.
Replacement, added to B9: «K keeps `run_case(i, rng, check=True)`, `r2_four_envelope_roster()` and the checker's `digest`, `check_roster`, `check_transition` and `check_executed` importable, with unchanged signatures and return shapes. At `random.Random(291013)`, `run_case(i, …)` for i in 0..7 yields the edge counts `tests/test_scored_packer.py:30-40` asserts; the new generator is a separate entry `generate_case(seed, i)`. Alternatively P rewrites :30-40 to assert aggregate coverage over modes 0..7. The brief picks ONE: the magistrate picks the first.»

**F9 — MATERIAL — the B4 similarity threshold is not a stable measure.** X8: unrelated code scores 0.36 or 0.06 depending only on the size of the packer set, so the check can fail an independent checker or pass a copy. Keyword handling and set-versus-multiset counting are also unstated.
Replacement for the B4 method: «Keywords kept; each checker line counted once per occurrence. The lens also computes a control: the same checker function against an unrelated packer function set of equal normalised line count (`_structure` truncated). PASS iff ratio ≤ max(0.30, control + 0.15). Report both numbers.»

**F10 — NIT — R1 wording.** X1: "holding only a copy of placement 0" does not say that `blocks` gets the id; without it, R1 refuses `inv_03`. Replace with «a new envelope `dict(index=n, model=<block's model>, kind="loaded", blocks=[placement0.block_id], voided_block_ids=[], observations=None)` plus a copy of placement 0 with `envelope_index=n` appended to `placements`».

**F11 — NIT — R5b misses AnnAssign, `lru_cache`/`cache` decorators and mutable defaults.** Replace with «no module-level Assign/AnnAssign binding a mutable container other than `_REPLAYING`; no `lru_cache`/`cache` decorator; no mutable-literal default; `_TRUSTED_OUTPUTS` absent».

**F12 — NIT — INV-10's extent in Final text 3 is open.** Write «INV-10 as :135 (unique `block_id`, model in the registration, level in LEVELS); full formation stays with replay (`inv_39`) and the checker».

**F13 — NIT — A291-POP-1 cites X-5 for the executed position population; X-5 rules only cell keys.** Cite «45/10 §Q4 (§4.1)».

**F14 — NIT — the "five scored modules" (B9) are unnamed.** Name them: «`tests/test_scored_{registration,packer,roster_checker,packer_fuzz,packer_stress}.py`».

## 2. Signature recurrence check

Routes left open: F4 (executed arithmetic outside the boundary), F5 (seat-invented grouping), F6 (the AST guard checks a name that does not exist), F2 (packer and checker read INV-11 differently). With F2–F6 applied, every population is read only through `_parent_facts`, behind INV-11/12 and the relation check.

## 3. Agreement

- **AGREE as written:** Final text 1 (A291-POP-1). I checked every row against 02d §0.4 RD-5, §3.4, §4.1, FT-7 and FT-10, and the gate ⇒ full-indices rule. X5 confirms it on the production route. The only defect is the F13 citation.
- **AGREE as written:** Final text 5; B2's residual; B7.
- **AGREE with additions:**
  - Text 2 (F3, F4);
  - Text 3 (F2, F12);
  - Text 4 (F6: the rename);
  - Text 6: R1 (F10), R2, R3, R4a and R5a hold as written; R2b is replaced (F1); R4b is pinned (F5); R4c is replaced (F6); R5b is strengthened (F11); the reseal helper is sound (X9);
  - Text 7 (F7);
  - Text 8 (F8, F9, F14).
- B5 order affirmed (X4).

BLOCKER F1; MATERIAL F2–F9; NIT F10–F14.
