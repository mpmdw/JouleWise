# 20 — Cold Fable gate ruling, A291-ESC2-02 (the METHOD and the round-3 plan, judged on the executed ownership harness)

Judge: Claude Fable 5.1, fresh non-interactive session, worktree `JouleWise-wt-coldgate-278ebc9e-r4` at `58a9d2c5`. Ruled 2026-09-24 ≈17:06–17:40 PDT. Nothing armed; no file other than this one written.

## 0. Disclosure, digests, validator

- **Auto-loaded before I acted:** `~/.claude/CLAUDE.md` (global rules), the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (truncated). None was requested; none is used below. I did not open CLAUDE.local.md, RUN_STATE, TASK_QUEUE, council logs, run reports, memory files, or any process-trace file outside the packet directory.
- **Charter digest:** expected (supplied outside the packet) `099de884…95d81`; observed `shasum -a 256 docs/process/coldgate_charter.md` = `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Method: `shasum -a 256` plus the validator.
- **Validator run 1** (charter sha ending `…95d82`, as instructed): `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2. **Run 2** (charter sha `…95d81`, packet sha `3ddca274…24d9c`): `result: PASS`, rc=0, all ten exhibit digests `expected == observed`, `exhibit_manifest_sha256 7b25389a…5168`.
- **Packet digest:** observed `3ddca2741388812ef43216704d729f9376c50eb9c9a3c5e0092faea2fa324d9c` = expected.
- **Harness exhibits = tree at `24ff94cb`:** `git archive 24ff94cb` under `/tmp/cg-r4-24ff94cb`; `shasum` of `tests/scored_ownership_{oracle,generator}.py` and `tests/test_scored_ownership_forgery.py` equal the three `ex-81-*` digests. `git diff --stat 0fa4e6e3 24ff94cb` = exactly those three files (+470 lines), so `24ff94cb` is `0fa4e6e3` plus the harness.

## 1. Read set and executed probes

Read: charter; `00-charge.md`; `09-convene-script.sh`; `ex-47`, `ex-81b`, `ex-71b` in full; `ex-48-20` §3–5 headings and K5; `ex-48-30` §4 Final texts R3b-0…R3b-5 and §5; `ex-02d` §0.4 glossary (lines 57–64) and INV-10/11/12 (lines 461–475); `git show 0fa4e6e3:joulewise/scored_packer.py` lines 70–115, 145–170, 218–275; `git show 0fa4e6e3:tests/test_scored_roster_checker.py` imports and `refresh_derived`. `ex-64b` was not needed: every one of its findings is re-litigated by `ex-71b`, and I rule the method, not R3 text.

Probes (all foreground, all in `/tmp/cg-r4-24ff94cb`, outputs under `/tmp/cg-r4-out/`):

| # | Probe | Result |
|---|---|---|
| P1 | `test_pairwise_seal_property` with escape + inconclusive logs | `ready=4800 inapplicable=1274 operator_errors=23 refresh_errors=239 escapes=109 checker_crashes=0 seal_crashes=0 runtime_s=11.97` — **reproduces ex-81b V2 exactly**. |
| P2 | Classify the 262 pairwise inconclusives | 239 = `refresh_error:KeyError` and **all 239 involve `drop_single`** (ready>0 in only 13 of its 15 pair slots, all others fully inconclusive). 23 = `operator_error:*:StopIteration` (`_block`'s `next()` on a dangling id). |
| P3 | Exhaustive triples (`TRIPLE_SAMPLE=512`) | wall 62.9 s; 258 escapes; 2,958 inconclusive of which 2,540 `refresh_error:KeyError`, **all 2,540 involve `drop_single`**; 418 `operator_error` (StopIteration). |
| P4 | Seal on the legal rosters of the four `CASES` (refresh, `sha256=None`, `_seal(finalize=True)`) | 99 rosters, **99 accepted**, 0 oracle violations. The harness itself never runs the seal on the legal corpus (`test_legal_corpus` calls only `ownership_violations`, ex-81 test:105–118). |
| P5 | Escape anatomy (pairwise) | oracle reason on every escaped item = `counts` (160 item rows); checker rows at `0fa4e6e3` include `INV-11` on only 17 of 109 escapes (the rest report INV-32/36/37/38 and never INV-11). Oracle-rejected mutants the seal refused: `inv_11` 4,496, `inv_52` 59, `inv_12` 2, `spread_minima` 1. Oracle-accepted and seal-accepted ready mutants: 110 (legal compositions such as void→revive). |
| P6 | `_seal` at `0fa4e6e3:251–275` | `_structure` runs in **both** modes before `_checked_derived`; `KeyError/TypeError/…/StopIteration` inside are translated to `PackingRefusal("inv_52")`. So `finalize=True` exercises the ownership rows for both modes, and an unrefreshed mutant can be submitted to `_seal` without crashing. |
| P7 | `refresh_derived` (`0fa4e6e3:tests/test_scored_roster_checker.py:145`) | imports only `tests.scored_roster_checker`; no packer import, so P cannot move it. |
| P8 | Existing scored tests at `0fa4e6e3` | 37+6+2+3+23 = **71** `def test_` (charge figure verified). |
| P9 | `0fa4e6e3:scored_packer.py:225–235` | per-item terminal test keyed on `t["block_id"] == b["block_id"]` (line 234) — the 4/4 diagnosis in ex-47 §Agreement 1 is verified. |

## 2. Packet hygiene

- (a) NIT. The charge's N1 phrase "legal corpus accepted" is ambiguous: at `24ff94cb` the corpus is accepted by the **oracle**, never by the seal (P4). ex-81b's wording ("the oracle accepts the legal corpus") is accurate; the charge's is not. Cured by the text in §3 N1.
- (b) NIT. ex-81b's evidence links point at `/tmp/278ebc9e/…` paths that a cold judge cannot read; I regenerated every number instead (P1, P3). No effect on any question.
- (c) The charge states the magistrate "takes no position on the method"; that is honest labelling. The lead's disposition is the plan text quoted in N1; I treat it as argument.
- No omitted contrary evidence found: the refuter that most damages the plan (ex-71b) is included in full.

## 3. Rulings N1–N6

### N1 (method) — AFFIRM the harness-as-gate method, with a different acceptance text. MATERIAL.

Deciding evidence: P1/P3 show the harness is a deterministic, reproducible RED at `0fa4e6e3` on the exact defect (AUD-1/B1/B2 accepted, 109/258 escapes); P9 verifies the diagnosed defect; two text rounds (R3, R3b) each failed under a refuter with the same signature (ex-71b: 7 of 9 not cured). Charter §9 requires explicit justification for another same-shape round: the justification is that this round is **not** the same shape. Rounds 1–2 (`bff27861`, `0fa4e6e3`) and texts R3/R3b patched predicates per forgery and pinned them by prose; R4 replaces the seal's predicate with the contract's closed form and replaces the prose pins with an executed property over 4,800 pairs and 512×99 triples. That is the redesign §9 asks for.

But the plan as quoted is unsound in three ways the exhibits prove, so I write a different acceptance text (Final text R4-1):
1. "Legal corpus accepted" must mean **accepted by `_seal(finalize=True)`**, else a seal that refuses everything passes the property (P4 shows the harness does not check this today).
2. The inconclusive classes (239/642, P2/P3) are one broken operator; they must be zero, not "recorded".
3. The disputed boundary-map (R3b-0 code table, D1/D4), the AST confinement list (R3b-2), and the mutation-kill prose (R3b-5(4)) are **not** needed to cure ownership and are where the last two rounds contradicted themselves. Ruling per item:

| R3b item | Disposition |
|---|---|
| R3b-0 contract INV-11 closed form (ex-48-20 K1 text) | **BINDING.** Magistrate applies to 02d:465–469 before P starts. |
| R3b-0 code-owner table (`SEAL_CODES`/`REPLAY_CODES`/…), D1, D4 | **DROPPED from R4.** Deferred to a separate lane; the R4 property tests refusal, not code. |
| R3b-1 `_ownership` view + `_conserve` (K3) + `_parent_facts` reads it + `:225–235` deleted | **BINDING** (Final text R4-2). |
| R3b-1 `_formation` per-model, `_provenance`/inv_37 split | **DROPPED as prose;** formation becomes harness-checked (R4-3 item 4); INV-37 untouched this round. |
| R3b-1/R3b-2 AST confinement lists | **DROPPED** except the two asserts in R4-2(c). |
| R3b-2 witnesses()/regressions in `test_scored_packer.py` | **DROPPED;** the harness's `_named_witnesses` (type-clean, ex-81 test:26–90) replaces them. D5 is moot. |
| R3b-3 checker closed INV-11 (K) | **BINDING**, harness-checked (R4-3 item 5): P5 shows the checker misses INV-11 on 92 of 109 escapes. |
| R3b-4 fuzz extension | **DROPPED;** the harness is the composed fuzz. Single-operator fuzz unchanged. |
| R3b-5 gate | **REPLACED** by R4-5. |

### N2 (the three ex-71b blockers) — D1 dropped this round; D2 and D3 converted to harness cases. MATERIAL each.

- **D1 (inv_51 two owners):** DROP from R4. It is a defect of the code-owner table, which R4 does not ship. It stays open in the deferred lane; it cannot block an ownership cure the harness decides without codes.
- **D2 (B1 cannot kill the superseded-holder clause):** CONVERT. The refuter's own witness (parent revived, its singles voided, counts (1,0), holder superseded) becomes named witness `B1-singles-voided`; the oracle must reject it with reason `superseded_live` and the seal must refuse it. That makes the m2 kill mechanical. Exact text R4-3 item 3.
- **D3 (cross-model parent reordering):** CONVERT. Not an INV-11 fact, so not an oracle clause and not a generator operator (the property would be inert on it). It becomes a named **seal** regression: swap two parents of different models at the same level in `roster["blocks"]`; `_seal(finalize=True)` must refuse `inv_10`. ex-71b V1 shows the checker already reports `inv_10` on it, so the test is decidable today and RED at `0fa4e6e3` ("both-seals-ACCEPT"). P implements formation however it likes. Exact text R4-3 item 4.

### N3 (the harness itself) — REJECT as the gate in its current form; AFFIRM once the seven additions below land. MATERIAL (one BLOCKER item: A1).

Checked against the contract and the executed runs:
- **Oracle clauses:** `ownership_violations` (ex-81 oracle:19–60) implements the closed form: listings counted over all envelopes and all blocks including superseded (l.28–32), counts ∈ {(1,0),(0,1)} (l.47), holder not superseded (l.51), no terminal item in the holder (l.53). Matches K1 and 02d:465–469(b). It imports neither packer nor checker (l.3–4, verified). NIT: `set(block['items'])` (l.31) collapses a duplicate item inside one block; that is an INV-10/52 shape, out of scope.
- **Operators present:** all five from ex-47 §5 (clone, terminalise, revive, retarget, flip) plus void, list-live-new-envelope, drop_single. **Missing** for the closed form's count clause: no operator produces (0,0) or (0,2) directly. Add `drop_terminal_entry` and `duplicate_terminal_entry`; add `copy_item_into_live_block` (an item duplicated into an existing live block of the same model, the non-clone (2,0) shape).
- **`drop_single` is broken (BLOCKER as a gate):** it deletes the block but leaves its placements and envelope listings, so every composition through it dies in `refresh_derived` with `KeyError` or in `_block` with `StopIteration` — 100 % of the 239 + 2,540 refresh errors and, by P2, the 23 + 418 operator errors (P2, P3). A gate that "records" these hides every forgery in that slice.
- **Triple sample:** 128 of 512 ordered triples. Exhaustive costs 62.9 s (P3) and found 258 escapes vs 105 in the sample. Rule: exhaustive.
- **Legal corpus through the seal:** absent (P4). Required.
- **Checker agreement:** the harness computes checker rows and discards them (ex-81 test:185). Required assertion in R4-3 item 5.
- **Two seal modes:** `finalize=True` suffices because `_structure` runs in both modes (P6); no change.

Additions are the exact text of Final text R4-3.

### N4 (seats and independence) — Write a different text. MATERIAL.

The harness author is not stated in the packet by name; ex-81b is a `claude-codex-report/v1`, so the author is a Codex-family seat (call it H). Rule: P is not H and not H's family; K is not P's family; K may be H or H's family. P reads, in this order and nothing else from the process tree: (1) 02d as amended (K1 closed form applied); (2) Final texts R4-1…R4-5 of this ruling; (3) `ex-81b-harness-report.md`, `tests/test_scored_ownership_forgery.py`, `tests/scored_ownership_generator.py` at the K-updated head — the acceptance test is not secret; (4) **not** `tests/scored_ownership_oracle.py` (P implements the predicate from the contract text; a copied oracle shares its bugs with the implementation) — enforced by an AST assert that `joulewise/scored_packer.py` imports nothing from `tests`. P runs the harness RED first, then GREEN. K lands R4-3 before P starts; P's worktree is cut from K's landed head.

### N5 (gate before merge and the stop rule) — Replace K5's items (1)–(6) with the harness; KEEP the forger seat (7) as amended by ex-71b D7. MATERIAL.

The harness is deterministic and now the primary gate (items 1–4 of R4-5). Mutation kills survive only as "the harness decides" runs (item 3). The forger seat stays because the harness's oracle and operators share one author's blind spots (D3 is the proof: a formation escape the oracle cannot see), and a 30-minute blind seat is cheap error control; its three outcomes take D7's definitions verbatim. Stop rule kept, shortened.

### N6 — Anything else.

- (i) MATERIAL. P5: the seal at `0fa4e6e3` already refuses 4,496 of the oracle-rejected pairwise mutants with `inv_11`; the 109 escapes are all `counts` violations (AUD-1/B1/B2 classes plus 22 one-live-plus-terminal). No escape is a `superseded_live` or `terminal_item_in_live_holder` case, so R4-2's predicate must be landed whole, not "the counts fix": those two clauses are exercised only by `B1-singles-voided` and `probe-D`.
- (ii) NIT. `refresh_derived` is test-side and checker-only (P7): acceptable as the harness's normaliser; record its digest in the P brief so a K change to it after P starts is visible.
- (iii) NIT. The escape log should also record the seal's refusal code histogram for oracle-rejected mutants (P5's `inv_52` 59 rows are mutants malformed for other reasons; a later drift of `inv_11`→`inv_52` would otherwise be invisible).
- (iv) NIT. `TRIPLE_SEED`/`TRIPLE_SAMPLE` become dead once triples are exhaustive; delete rather than leave a sampled path.

## 4. Final texts A291-R4 (paste verbatim into the P brief; K receives R4-3 and R4-5)

**R4-0 (magistrate, before K and P).** Replace 02d:465–469 (INV-11 predicate) by the closed form of `ex-48-20` K1: «for every (model, registered item): let LIVE be the list of (block, envelope) pairs over ALL blocks containing the item, superseded or not, whose block id is in that envelope's `blocks`; let TERM be the `terminal_refusals` entries naming (model, item). Exactly one holds: (a) (len(LIVE), len(TERM)) == (1, 0) and the one live block has `superseded == false` and none of its items has a `terminal_refusals` entry; (b) (len(LIVE), len(TERM)) == (0, 1).» Glossary 02d:57–64 pasted above it. No other 02d change this round.

**R4-1 (acceptance = the harness decides).** Round 3 is accepted when, at the integrated head, all of: (1) `python3 -B -m unittest tests.test_scored_ownership_forgery` is GREEN with the harness of R4-3 landed, meaning: zero seal escapes on exhaustive pairs and exhaustive triples; zero `operator_error`; zero `refresh_error`; every one of the 1,868 legal rosters accepted by `_seal(registration, roster, finalize=True)`; every named witness gets its listed outcome; (2) the five existing scored modules (71 tests at `0fa4e6e3`) GREEN; (3) R4-5 passes. Nothing else is an acceptance condition.

**R4-2 (P: `joulewise/scored_packer.py`).** (a) `def _ownership(registration, roster) -> dict` with keys exactly `blocks` (block_id → block), `live` ((model, item) → list of (block_id, envelope_index), every listing appended, none overwritten), `term` ((model, item) → list of entries, multiplicity kept), `placement` ((block_id, envelope_index) → placement dict); rebuilt on every call; no cache, no module-level container. (b) `def _conserve(registration, view)`: the R4-0 predicate, verbatim, over every (model in `registration.role_to_model_id.values()`, registered item), else `_need(False, "inv_11", "item conservation")`. Called from `_structure` immediately after the envelope loop that ends at `0fa4e6e3:192` and before any other row; lines `0fa4e6e3:225–235` deleted. (c) `_parent_facts(registration, roster, captured_window_keys=None)` keeps its signature; its first statement is `view = _ownership(registration, roster)`; an item's owner is `view["live"][(model, item)][0]` when that list has length 1, otherwise no index is recorded. Two AST asserts, in `tests/test_scored_packer.py`: the first statement of `_parent_facts` binds `_ownership(...)`; `_conserve` and `_parent_facts` contain no `Subscript` or `.get` `Call` whose base is `Name("roster")`. (d) Formation: P makes `_seal(finalize=True)` refuse `cross-model-reorder` (R4-3 item 4) with `inv_10`; the implementation is P's. (e) `joulewise/scored_packer.py` imports nothing from `tests` (AST assert). Nothing else in the module changes; INV-37 code unchanged.

**R4-3 (K: the harness, landed and GREEN-on-legal / RED-on-forgery at `0fa4e6e3` before P starts).**
1. `drop_single` also removes every placement of the block and every `blocks`/`voided_block_ids` listing of it; `composed_mutants` unchanged otherwise. `_seal_property` asserts `totals["operator_error"] == 0 and totals["refresh_error"] == 0` as hard failures (assertion before the escape assertion). Any mutant that still fails refresh is submitted to `_seal(reg, m, finalize=True)` and must raise `PackingRefusal`; acceptance or any other exception is a failure.
2. Triples exhaustive: `_combinations(3)` returns `list(product(OPERATORS, repeat=3))`; `TRIPLE_SAMPLE` and `TRIPLE_SEED` deleted. Budget: ≤ 5 min wall for pairs + triples (62.9 s measured at 8 operators; ≈ 2 min at 11).
3. New operators, appended to `OPERATORS`: `drop_terminal_entry` (remove one `terminal_refusals` entry chosen by `rng`); `duplicate_terminal_entry` (append a deepcopy of one entry); `copy_item_into_live_block` (choose a live block A and a live block B ≠ A of the same model; append one item of A to `B["items"]`). Each returns `False` when no candidate exists.
4. Named witnesses added to `_named_witnesses`: `B1-singles-voided` (from `base`: revive the superseded parent as in B1, then move every live listing of that parent's singles in the same envelope from `blocks` to `voided_block_ids`; oracle must reject with `reason == "superseded_live"`; seal outcome `refused:inv_11`); `cross-model-reorder` (from `base`: swap the positions in `roster["blocks"]` of two parents with different `model`, same `level`, no other change; oracle must ACCEPT; seal outcome `refused:inv_10`). `test_named_seal_regressions` asserts the exact outcome string per witness: `AUD-1`, `B1`, `B2`, `probe-D`, `B1-singles-voided` → `refused:inv_11`; `cross-model-reorder` → `refused:inv_10`; `legal-contrast` → `accepted`.
5. Checker agreement (K's R3b-3 lands here): `tests/scored_roster_checker.py` INV-11 replaced by the R4-0 predicate, `live` built over every listed block regardless of `superseded`. In `_seal_property`, for every oracle-rejected ready mutant whose checker rows do not contain `INV-52`, assert `"INV-11" in rows`; failures listed as `(ops, seed, case, roster, rows)`. In `test_named_regressions`, `AUD-1`, `B1`, `B2`, `probe-D`, `B1-singles-voided` report `INV-11`; `legal-contrast` and `cross-model-reorder` do not.
6. `test_legal_corpus_seal`: for every roster of `generate_case(seed, i)`, seeds 291013–291016, i 0–11 (1,868), after `refresh_derived`, `sha256 = None`, last event sha `""`: `_seal(case.reg, m, finalize=True)` returns; count asserted `== 1868`.
7. Escape and refusal logging: the `FORGER` line adds `refusal_codes={json histogram}` over oracle-rejected mutants; `A291_ESCAPE_LOG` records unchanged.
RED/GREEN contract at `0fa4e6e3`: items 4–6 GREEN except the named-seal outcomes and the escape assertions, which are RED; K's report states the RED set verbatim.

**R4-4 (seats and order).** Order: R4-0 → K lands R4-3 on `test/2026-09-24-a291-ownership-harness` (or its successor) → P's worktree is cut from K's landed head → P lands R4-2 → integrate → R4-5. Families: the harness author is Codex-family (ex-81b); P is neither that seat nor that family; K is not P's family. P's read set is exactly: amended 02d, this ruling's R4-0…R4-5, `ex-81b`, `tests/test_scored_ownership_forgery.py`, `tests/scored_ownership_generator.py`; P does not open `tests/scored_ownership_oracle.py` or `tests/scored_roster_checker.py`. P runs the harness before editing (expected: RED with escapes > 0) and after (expected: GREEN). `WRITE_SCOPE` for P: `joulewise/scored_packer.py`, `tests/test_scored_packer.py`. `WRITE_SCOPE` for K: the three `tests/scored_ownership_*`/`test_scored_ownership_forgery.py` files, `tests/scored_roster_checker.py`, `tests/test_scored_roster_checker.py`.

**R4-5 (gate before merge, in order).** (1) R4-1 in full at the integrated head. (2) `python3 -B -m unittest discover -s tests` GREEN. (3) Mutation kills, K-run, each = "run `test_pairwise_seal_property` and `test_named_seal_regressions` against the mutant; killed iff at least one fails": m1 count clause `in {(1,0),(0,1)}` → `len(LIVE) <= 1 and len(TERM) <= 1`; m2 superseded-holder clause removed; m3 terminal-item-in-holder clause removed; m4 `live` overwritten instead of appended; m5 superseded blocks skipped when building `live`. All five must be killed; no equivalence claim is accepted for m1–m5 because R4-3 items 3–4 supply their witnesses. (4) **Forger seat:** family neither P's nor K's, `WRITE_SCOPE: []`, 30 min wall, in `/tmp/forger-<activation>/` holding `git archive <integrated head>` with `tests/` removed, the amended 02d, the glossary and a runnable Python; told nothing of the named witnesses; charge "compose a roster with forged ownership or formation that `_seal(registration, roster, finalize=True)` accepts"; returns constructor code and seal results. The magistrate adjudicates each candidate with `tests/scored_ownership_oracle.py` and the amended checker. `ESCAPE` = a reproduced candidate `_seal(finalize=True)` accepts on which the oracle reports a violation or the checker reports `INV-10`, `INV-11` or `INV-12`. `COMPLETED_NO_ESCAPE` = the seat completed and every submitted candidate was adjudicated with no escape. Infrastructure failure, incomplete execution, timeout without a submitted candidate, or unadjudicable output = `INCONCLUSIVE`, never `COMPLETED_NO_ESCAPE`; one `INCONCLUSIVE` reruns once with a fresh seat, a second escalates. **Round 3 passes only when (1)–(3) pass and (4) is `COMPLETED_NO_ESCAPE`.** **Stop rule:** "An escape found by the forger, or by any harness run after P has declared GREEN, is a design defect of the ownership view: no seat patches it; the magistrate convenes a consult with the escape as its brief."

## 5. Severity summary and verdicts

BLOCKER: the seal accepts forged ownership at `0fa4e6e3` (109 pairwise, 258 exhaustive-triple escapes, AUD-1/B1/B2 accepted — reproduced P1/P3); merge stays blocked until R4-2 lands and R4-5 passes. BLOCKER (gate fitness, N3): `drop_single` leaves dangling references and is the source of 100 % of the 2,779 refresh errors and, by P2, the operator errors; cured by R4-3 item 1. MATERIAL: N1 (acceptance text: seal on the legal corpus; inconclusives must be zero; R3b items dropped/bound as tabled), N2 (D2, D3 converted; D1 dropped this round), N3 (operators, exhaustive triples, checker agreement, corpus-through-seal), N4 (P read set and family rule), N5 (harness replaces K5 (1)–(6); forger kept with D7 definitions), N6(i). NIT: hygiene (a), (b); N6(ii)–(iv); oracle `set(items)`.

Verdicts: **N1 AFFIRM** the method with different acceptance text; **N2** D1 DROP, D2 CONVERT, D3 CONVERT; **N3 REJECT** the harness as-is, AFFIRM with R4-3; **N4** different text (R4-4); **N5** different text (R4-5); **N6** findings as listed. No REFUSE. Disagreement with the lead's plan text: three points in N1 (seal on legal corpus, zero inconclusives, and that the boundary-map/AST/mutation prose is dropped rather than "settled first"). Everything else concurs with the charge's framing.
