# 10 — Cold Fable gate ruling: A291-FIX2-01 (fix-round-2 plan for the scored-night packer)

Judge: Claude Fable 5.1, cold session, worktree at `7d902b49`. Evidence: `git show 20cd29de:<path>` and probes in a `git archive 20cd29de` copy under `/tmp/coldgate-7370d0fb` (sim2.py, dig.py, cost.py, repro.py; removed after use). Ruled 2026-09-24.

## 0. Disclosure, charter check, read set

- Auto-loaded: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, the memory index `MEMORY.md` (pointers only). I opened no memory file, CLAUDE.local.md, RUN_STATE, TASK_QUEUE, council log, run report, or trace outside the packet directory.
- Charter digest. Expected (supplied independently of the packet): `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Observed (`shasum -a 256`): identical. Method: validator run 1 with the deliberate typo `…5d82` → `REFUSE`, `charter_trusted_observed_mismatch`, rc=2; run 2 with `…5d81` → `PASS`, rc=0, eight exhibits matching the manifest. Packet digest expected `8e99b258…99bb`, observed identical.
- Read: charter, charge, ex-01/02/02d/03/06/31/37/50; packer, checker and both test files at `20cd29de`.

## 1. Executed evidence (all at 20cd29de)

- E1 (repro.py) S1: level-1 large blocks moved live→voided, no terminal refusals, unresealed, `requeue_overrun` → raw `ZeroDivisionError`; checker INV-02, INV-11. Confirms ex-50 S1, ex-03 P1.
- E2 (repro.py) B1: one block live in envelope 0 and a new envelope 11, `_seal(finalize=True)` accepts, `_live` picks 11, `requeue_overrun` ACCEPTS (events 1); checker INV-11/INV-36; cache cleared, same call refuses `inv_39`. Confirms ex-50 B1, ex-03 P2/P3.
- E3 (sim2.py; every identifier → `N`, numbers → `#`, strings kept, blanks/comments dropped): packer `_derived` 34 lines vs checker `_derived` 33, 29 shared (0.88); `executed_status` vs `check_executed` 27/48 (0.56); `_structure` vs `_static_checks` 20/139 (0.14, the independent baseline). The magistrate's bench claim is re-verified: `scored_packer.py:77-110` and `scored_roster_checker.py:247-279` are one function, including the unguarded `sum(a)/len(a)` at :109 and :278. The checker test helper `refresh_derived` (`tests/test_scored_roster_checker.py:139-175`) is a third copy.
- E4 (cost.py) cache cleared before every call, fixture n=11/bs=2/cap=8: 12 events, max 32.8 ms per requeue, 218 ms total; n=10/bs=2/cap=6: max 24.0 ms. Same magnitude as Sol (47 ms max, 377 ms over 15 events) and Opus (43.5 ms).
- E5 (dig.py) `_digest` on `events=[1]` raises `AttributeError`; NaN → `ValueError`; a set → `TypeError`. The seal's conversion tuple at :208 lacks `AttributeError`.
- E6 (read) `_live` is called only at :79 and :421; `_derived` also runs outside any boundary at :307 (`pack` exit) and :385 (`requeue_overrun` exit).

## 2. Rulings B1–B10

**B1 AFFIRM, structural.** E1, E2, E3. Every derived population is well defined only under INV-11/INV-12 (02d:465-476), and nothing establishes them before arithmetic: `_seal` :203-205 runs `_derived` before the digest test; `_structure` :113-191 has no INV-11; `_live` :72-74 is last-wins; :333 skips replay on a cache the caller can fill. Correction to ex-06 §2 item 1: add a fifth route — the oracle's `_derived` and the fixture `refresh_derived` are transcriptions, so the tests cannot see the misreading (E3).

**B2 AFFIRM deletion; residual affirmed with pinned numbers.** E4 re-measures the cost. The "64 per level ≈ 11 envelopes" night size is cited from a document outside the packet (ex-03 Q3); I do not rely on it. Residual text: «Replay at requeue entry costs O(E²) per night. Measured at 20cd29de: ≤ 47 ms per call at 15 events; 729 ms at 67; 2.8 s at 131 (ex-03 Q3; judge E4 concurs at 12 events). Before any registration whose `pack` root holds more than 60 loaded envelopes, re-measure the per-call requeue cost on that registration and record it in the arm record.» Line :333 becomes `if not _REPLAYING.get(): _replay_roster(registration, roster)`.

**B3 Write a different text (MATERIAL).** Rows checked against 02d:354-359 (RD-4, FT-7, FT-10), :382-386 (§4.1, FT-10), :63 (RD-5), 31 X-5. Defects: the executed-spread row omits the five-envelope clause that §4.1 and :447 carry; the planned-spread "every problem is live" clause is the code's phrasing (:102), not RD-5's. Ruled addendum (dated 2026-09-24; restates RD-4, RD-5, FT-7, FT-10, §4.1, X-5; reopens none):

```
ADDENDUM A291-POP-1 (2026-09-24). Per parent P of cell (model, level) the fact
record is (n_items, n_terminal, indices): n_items = len(P.items);
n_terminal = number of P's items with a terminal refusal; indices = envelope
index of the LIVE placement owning each non-terminal item (owner = P if not
superseded, else the single whose items == [item]), in item order (X-4).
Planned lever: gate population = parents with n_terminal == 0 (RD-5, FT-10);
position population = parents with indices non-empty (RD-4); position =
sum(indices)/len(indices); per-model mean over position parents in
roster.blocks order; lever = |mean_8B - mean_1.7B|; null iff either model's
gate population is empty.
Planned spread shortfall[cell] = (gate count < MIN_PARENT_BLOCKS) or
(len(set of indices of all gate parents) < MIN_ENVELOPES) (FT-7, RD-5).
Executed lever (counted = the owner's live placement (block_id, attempt) is in
captured_window_keys; indices built from counted items only): gate =
len(indices) == n_items (§4.1 counted parent, FT-10); position population =
indices non-empty (45/10 §Q4, X-5); lever and null rule as above.
Executed spread_exceeded[cell] = (gate count < MIN_PARENT_BLOCKS) or
(len(set of indices of all gate parents) < MIN_ENVELOPES) (45/10 §Q4).
Relation rule: for the planned lever every gate parent must have
len(indices) == n_items (INV-11 makes this so); `_lever` checks it before any
division and refuses PackingRefusal("inv_11", f"gate parent without full live
positions {parent_id}"). For the executed lever the relation holds by
definition of the gate; no check.
```
The plan's weaker "gate ⊆ positioned" is replaced by "gate ⇒ full indices": the spread's occupied set needs every index and INV-11 guarantees it. Code `inv_11` affirmed (an INV-11(a) failure).

**B4 AFFIRM Opus (D1), with exact terms.** E3. Seat K: Claude family (Opus 5.5), never the Sol/GPT family while P is Sol. K's brief may show: 02d §0.4, §1.2, §3.4, §4, §5, §6, §10; ex-31; addendum A291-POP-1; lens-37 B1/B2/M1 as defect shapes; the packer's public names and signatures only (`pack`, `requeue_overrun`, `verify_executed_roster`, `executed_status`, `PackingRefusal(code, detail)`, module constants); K's own files. Not shown: `joulewise/scored_packer.py`, `tests/test_scored_packer.py`, ex-02, ex-03, ex-06. K must also rewrite `refresh_derived` item-centrically or replace it with literal hand values (E3). Similarity check, applied by the delta re-audit with the script pasted: pairs (packer `_parent_facts`+`_lever`+`_derived` concatenated vs checker `_derived`; `executed_status` vs `check_executed`; `_parent_facts` vs `refresh_derived`); normalise as E3; count checker lines present verbatim in the packer set. Threshold: ratio ≤ 0.30 of the checker function's lines (today 0.88 and 0.56; the independent pair scores 0.14). Additionally the checker's outer loop is over (model, item), the packer's over parents.

**B5 Write a different text (MATERIAL).** Order affirmed in substance, but the digest step must sit inside the conversion boundary and the tuple must gain `AttributeError` (E5), or a roster with `events=[1]` crashes before `inv_02`. Ruled `_seal` order: (1) identity rows as :196-201; (2) inside `try`, verify mode only: `digest = _digest(roster)`, then `inv_02` "input unsealed"/"digest mismatch" and the INV-38 rows :224-228; (3) `_structure` as today plus, at its end, INV-11 (a)/(b) exactly as 02d:467-469 including "exactly one terminal entry", and INV-12 both clauses (02d:473-476); (4) `_checked_derived` (B6); (5) `except PackingRefusal: raise`; `except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError) as exc: raise PackingRefusal("inv_52", "malformed roster") from exc`; (6) `stale_derived`; (7) root-only `spread_minima`, `inv_28`; (8) finalize: compute `digest` now, write fields as :216-221, no cache append. Precondition row set: {INV-03, INV-10, INV-11, INV-12, INV-17, INV-52}; INV-10 (:135, unique ids, model membership) is relied on by the single lookup and was missing (NIT). Not stricter than the contract: each is a §5 "F: a" row refused at entry, and INV-11/12 are the contract predicates verbatim.

**B6 AFFIRM with exact text.** `except ArithmeticError as exc: raise PackingRefusal("inv_52", f"internal:{type(exc).__name__}") from exc`, after the malformed clause. MATERIAL addition: E6 shows `_derived` runs outside `_seal` at :307 and :385, so the plan's boundary does not cover R4b. Rule: one helper `_checked_derived(registration, roster)` wraps `_derived` in the two except clauses and is the only caller of `_derived`; `_seal`, `pack` exit and `requeue_overrun` exit call it. Never-fires assertion: «In the fuzz module, collect every `PackingRefusal` raised over the legal corpus and the mutation corpus; assert no `detail` starts with `internal:`; assert the legal corpus raised zero refusals.»

**B7 AFFIRM.** With the cache gone (E2: replay refuses `inv_39` on the resealed forgery), sealing confers no trust; INV-40 (02d:624) and FT-8 name the call. Keep :216 `inv_02` "output already sealed".

**B8 Write different texts (MATERIAL).** Gaps: R2b names no call site; R4a's fixture is hand-built and checked through private `sp._derived` (`tests/test_scored_packer.py:258`), and a hand-built roster fails replay at every production entry once the cache is gone; R4c/R5b are not mechanical. Ruled:
- Test-side reseal helper (P and K each own a copy; `digest` from the checker): `def reseal(r): d = digest(r); r["sha256"] = d; (r["events"][-1].__setitem__("sha256", d) if r["events"] else r.__setitem__("registered_sha256", d)); return r`.
- R1: from `pack` on `fixture(n=10, block_size=2, cap=6.0)`, append a NEW loaded envelope of the block's model holding only a copy of placement 0, `reseal` → `requeue_overrun(reg, r, pending, all-keep)` raises `inv_11`; same `r` → `verify_executed_roster` raises `inv_11`.
- R2: E1's roster, `reseal` → `requeue_overrun` raises `inv_11`. R2b: a production-built roster with a split parent; delete one single from `blocks` and its placements, `reseal` → `requeue_overrun` raises `inv_12`. R3: E1's roster unresealed → `inv_02`.
- R4a: build by production `pack`+`requeue_overrun` a history in which one single of a split parent is terminal while a sibling is live (the route of `test_executed_partly_counted_parent_position`, extended to `ceiling_violation`); assert `roster["drift_lever_slots"]["1"]` equals a literal computed by hand from that roster's live envelope indices with the partly-terminal parent INCLUDED, and that cell's `planned_spread_shortfall` is `true`. Keep the 6.199999999999999 and 1.5999999999999996 checks as secondary. Counterfactual: a gate/position written "fully non-terminal" (lens-37 B1) changes the literal.
- R4b: `unittest.mock.patch.object(sp, "_parent_facts", …)` returning one record `(2, 0, [])` → `requeue_overrun` raises `PackingRefusal` code `inv_11`, never `ZeroDivisionError`.
- R4c: AST test: `_derived`, `_lever`, `executed_status`, `_seal` contain no `For`/comprehension whose iterable is a Subscript with constant `"blocks"` or `"placements"` and no Name `_live_index`; `executed_status` contains no `Div`. R5a as the plan. R5b: no module-level `Assign` whose value is a `Call` to `deque`/`dict`/`list`/`set` or a `Dict`/`List`/`Set` literal, except `_REPLAYING`; the string `_TRUSTED_OUTPUTS` absent.
- Variation: signature(seed, i) = (edge-count tuple, calls, final envelope count, event count, single count, terminal count); for seeds 291013 and 291014 the signature differs for ≥ 60 % of case indices; each seed still covers E1–E11 in aggregate.
- Fuzz operators, exactly ten, seeded, each submitted resealed and unresealed: (1) live→voided; (2) duplicate a live placement in a new envelope; (3) drop a terminal refusal; (4) add a terminal refusal; (5) delete a single; (6) flip `superseded`; (7) move a placement's `envelope_index`; (8) flip `late`; (9) alter one `events[k].sha256`; (10) increment a placement's `attempt`. Properties: (a) `requeue_overrun` returns or raises `PackingRefusal`, nothing else; (b) `check_roster(M) != []` ⇒ refusal; (c) every operator refused ≥ 1; (d) census includes `inv_11`, `inv_12`, `inv_38`, `inv_39`, `inv_02`; (e) NEW: `check_roster(M) == []` and a refusal with a code outside {`inv_38`, `inv_39`} is recorded as a finding for the magistrate (seal stricter than the contract, or checker weaker); (f) B6's never-fires assertion.

**B9 Write a different text (BLOCKER for implementability).** Scope collision: the plan gives K the seed-driven generator but only P may write `tests/test_scored_packer_stress.py`. Ruled: K's WRITE_SCOPE = `tests/scored_roster_checker.py`, `tests/test_scored_roster_checker.py`, `tests/scored_case_generator.py` (new), `tests/test_scored_packer_fuzz.py`, `tests/test_scored_packer_stress.py` (switch to the new generator, add the variation assertion). P's WRITE_SCOPE = `joulewise/scored_packer.py`, `tests/test_scored_packer.py`; P's step-6 assertions move to K's fuzz module. P and K run in parallel from `20cd29de` in separate linked worktrees. K's fuzz must be RED at `20cd29de` (it targets E1/E2); K's report pastes which properties fail there and K must not weaken it. Integration by the magistrate: cherry-pick K onto P's head (disjoint files), run the five scored modules; a P/K disagreement is decided by the magistrate citing the contract line under executed evidence; one the contract does not settle is a cold-gate question, never a seat's choice.

**B10 Misses.** (1) `_derived` exit sites outside the boundary, E6 [MATERIAL, B6]; (2) `AttributeError` from `_digest`, E5 [MATERIAL, B5]; (3) third copy `refresh_derived` [MATERIAL, B4]; (4) executed-spread five-envelope clause dropped [MATERIAL, B3]; (5) scope collision [BLOCKER, B9]; (6) R4a not driven through a production entry [MATERIAL, B8]; (7) no "checker accepts, packer refuses" property, so an over-strict seal passes every listed test but the legal corpus [MATERIAL, B8(e)]; (8) INV-10 absent from the precondition set [NIT]; (9) night-size claim rests on an off-packet document [NIT, hygiene].

## 3. Packet hygiene and tiering

Complete and neutrally assembled; both consults and the delta reproduce under my probes. One defect: ex-03's cost argument cites `09-headline-packet-b-scored-night.md:113`, outside the packet (NIT; B2 ruled without it). No REFUSE. Tiers: BLOCKER B9; MATERIAL B3, B4, B5, B6, B8; NIT INV-10, off-packet citation, ex-06 root-cause wording.

## Final texts (paste verbatim into the P and K briefs)

1. Addendum A291-POP-1 (B3 block, verbatim).
2. `_seal` order B5 steps 1–8; conversion clauses `except PackingRefusal: raise` / `except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError) as exc: raise PackingRefusal("inv_52", "malformed roster") from exc` / `except ArithmeticError as exc: raise PackingRefusal("inv_52", f"internal:{type(exc).__name__}") from exc`, in `_checked_derived`, the sole caller of `_derived`, used by `_seal`, `pack` exit, `requeue_overrun` exit.
3. Precondition rows in `_structure`: INV-03, INV-10, INV-11 (a)/(b) verbatim 02d:467-469, INV-12 both clauses 02d:473-476, INV-17, INV-52.
4. `_live_index` refuses a block id in two envelopes' `blocks` with `PackingRefusal("inv_11", f"duplicate live placement {block_id}")`.
5. Delete `_TRUSTED_OUTPUTS`; :333 → `if not _REPLAYING.get(): _replay_roster(registration, roster)`; :222 removed; B2 residual text in the round report.
6. Regressions R1, R2, R2b, R3, R4a, R4b, R4c, R5a, R5b and the `reseal` helper exactly as B8.
7. K: item-centric `_derived`, `check_executed`, `refresh_derived`; `tests/scored_case_generator.py`; fuzz with the ten operators and properties (a)–(f); variation signature and 60 % rule; RED at 20cd29de recorded.
8. WRITE_SCOPEs and sequencing as B9; similarity check as B4 (ratio ≤ 0.30, item-centric outer loop) in the delta re-audit brief.
