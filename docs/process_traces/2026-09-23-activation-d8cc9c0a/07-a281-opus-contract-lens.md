# 07 — A281 contract lens, round 1 (Opus 5.5 subagent, read-only) on e63fb541

Transcribed by the magistrate from the subagent's final report (brief 03). The probes lived in `/tmp/a281lens/p1.py`–`p4.py`.

**Verdict: FAIL. 2 blockers, 7 should-fix, 5 nits.** The named acceptance command passes (`Ran 15 tests in 0.332s OK`).

## Clause map

| Clause | Where | Status | Evidence |
|---|---|---|---|
| P1 pure, deterministic roster | `scored_packer.py:105-140` | MET | test line 22 |
| P1 identical block membership across models, size per arm | `:123-135` | MET | same slices for both models |
| P1 capacity = interior − guard | `:89`, `:129` | MET | operand-collapse test |
| P1/M8 no two blocks of a cell per envelope; ≥5 blocks in ≥5 envelopes | `:87-93`, `:124-125` | MET | one block per level per envelope by construction |
| P1 palindrome "so drift cancels" | `:58-75` | PARTIAL | labels symmetric, loaded slots unbalanced (S1) |
| P1 Williams rows | `:43-55`, `:86` | MET | |
| P1 roster sha256 | `:25-30` | PARTIAL | S4 |
| P2/M12 requeue then split, never dropped | `:143-180` | PARTIAL | pairing breaks after split (B2); unbounded loop (S5) |
| P3 reducer gross only (M7) | `scored_reduce.py:30-92` | MET | idle padding changes J/correct by 0 J |
| P3 malformed/truncated incorrect | `:66` | MET | |
| M2 every capped attempt incorrect | `:48`, `:66-67` | PARTIAL | trusts `outcome` (S6) |
| M3 cap-bound > 20 % | `:89-91` | MET | |
| M10 J/token descriptive | `:87` | MET | see N3 |
| P4/M9 paired, block-aware, widened bootstrap | `energy_per_correct.py:48-109` | MET | |
| M9 two Holm families of m = 5 | `:121-198` | PARTIAL | nothing labels or checks family (S2) |
| M9 L\* only on Holm-significant directions | `:193-197` | CONTRADICTED | B1 |
| P5 merge order, correct counts only | `:136-156` | MET | see N2 |
| P5 "not resolved" never "no difference" | `:175`, `:192` | MET | |
| Packet C "not estimable" | none | MISSING | S3 |
| M5 pilot never chooses reported levels | `decide:130` yes; `pack:115` no | PARTIAL | S7 |
| M11 pure desk-side reducer | whole module | MET | |
| P6 tests | three modules | PARTIAL | crossover test encodes wrong direction (B1); palindrome test checks labels only (N4) |

## Blockers

**B1. Crossover rule contradicts packet C and M9.** Packet C (`10-…md:53-54`): L\* is "the lowest level whose R_L interval lies wholly below 1, provided some lower level's interval lies wholly above 1". Code (`energy_per_correct.py:193-197`) takes the first adjacent resolved, differing pair in either direction. Probe: pattern 88111 → crossover 3 (packet C: none); pattern 1n888 → crossover None (packet C: 3). `tests/test_energy_per_correct.py:50-67` asserts crossover 3 for the reverse pattern, locking in the error.

**B2. A split block makes the paired estimator refuse the whole level.** Keys are `(level, sorted members)` (`:13`); `:62-63` requires identical keys. After a second overrun the 8B copy exists only as singles while the 1.7B copy is whole: `ValueError paired models must have identical block membership`, and `decide` propagates it, aborting the family. Fix: singles carry `parent_block_id`; the estimator sums singles' gross joules into the parent for pairing, and counts one floor/anchor bound per single window.

## Should-fix

- **S1. Palindrome balances labels, not each cell's measured blocks.** Empty slots are filled last, so drift does not cancel per level. Mean envelope index: F1 example 8B 5.0 vs 1.7B 4.2; n64 bs13 8B 8 s/item: 8B 6.0 vs 1.7B 5.0, per level 8B 4.4–6.0; 8B 12 s/item (no empty slot) per level 7.4–8.8 vs 8.0. Invariant should be equal mean index per cell across models; assert it or register a tolerance; report the residual as a covariate.
- **S2. `decide` family misuse is easy:** no arm/family argument; mixed arms accepted (a thinking-on 8B vs thinking-off 1.7B yields a crossover); missing bootstrap options default floor/anchor to 0 (silently unwidened, against M9); a ready `ratio` dict is accepted unchecked. Fix: `decide(levels, *, arm, family ∈ {primary, secondary}, floor_j, anchor_j)` with validation and `can_carry_headline = family == "primary"`.
- **S3. "Not estimable" missing:** sparse groups give `ratio None` → "not resolved", conflating inconclusive with not computable.
- **S4. Digest chain incomplete:** `requeue_overrun` overwrites `sha256` (original digest not kept; add `parent_sha256`/`registered_sha256`); per-arm cap, envelope length, offset and pitch are not bound; the empty slot has no kind label.
- **S5. Single-problem overrun has no terminal state:** requeues indefinitely (attempt 6, 18 envelopes after four more overruns). Flag `ceiling_violation` after one single-problem retry.
- **S6. Reducer does not enforce M2 and drops retry provenance:** a row `truncated: True, stop_reason: length, outcome: correct` counts correct and not capped (4 capped rows → correct 1, cap_hit 0.25, true 1.0). Refuse capped/outcome disagreement; carry `retry_stage` into cells.
- **S7. `pack` accepts any subset of levels** (`pack levels {3}` → [3]); under M5 / D-062 it should require the registered level set, as `decide` does.

## Nits

- N1 `holm_significant=True` can coexist with "not resolved" (`:187-189`); rename or make consistent.
- N2 when only Level 4 is sparse the code merges 5 into 4; defensible, but the registration text must say so (and for Level 2).
- N3 the bootstrap splits block energy across items by tokens (`:91-95`), J/token inside inference; AP-5M should exempt it from M10 by name.
- N4 `test_scored_packer.py:25-26` checks label symmetry only.
- N5 `:92-93` a zero-token block contributes full gross energy whatever items were drawn.

## F1 recommendation

Capture YES, full 600 s, model loaded and idle, labelled `idle_slot`, out of every numerator. But capture is not sufficient: with the slot at index 9 the 1.7B's measured blocks average index 4.2 vs 5.0. With 5 + 5 loaded envelopes on 10 slots, positions sum to 45 and cannot split evenly; on an 11-slot grid with a captured idle slot, exact balance exists for an empty slot at any odd index (e.g. empty at 9: 8B {0,2,6,7,8}, 1.7B {1,3,4,5,10}, both sum 23), but not as a palindrome. Adopt: packer objective = equal mean index per cell across models on a fixed-pitch grid; idle slots captured; test or registered tolerance.

## F2 recommendation

ACCEPT append-only tails with four conditions: fix B2 (pair on parent); `retry_stage` on every row through the reducer; terminal single-problem state (S5); label the drop-retried sensitivity as selection-confounded (it removes exactly the long items), never a peer headline. Reject paired retry as default (doubles cost); pre-register a trigger instead (e.g. retried attempts > 10 % of a headline cell → next night re-measures the other model's copies adjacently). On single-problem packing: M12 requires only re-queueing as single problems, never dropping; pack singles several per envelope, each with its own item edges, by cap-bounded worst case (cap × s/token_upper + prefill), not the failed p95 prediction. Amend M12 wording to "single-problem blocks, packed by worst-case duration".
