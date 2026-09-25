# 20 — Cold Fable gate ruling, A291-ESC2-01 (structural cure after the same-signature recurrence)

Judge: Claude Fable 5.1, fresh session, no loop context. Worktree `JouleWise-wt-coldgate-278ebc9e-esc2`, HEAD `34bef63b`. Foreground only; no subagents; nothing armed; no tracked file touched other than this one.

## 0. Disclosure, charter digest, validator

**Auto-loaded by the harness, not requested:** the global `~/.claude/CLAUDE.md`, this worktree's `CLAUDE.md`, and a truncated copy of the memory index (`MEMORY.md`, index lines only). I opened no memory file, no RUN_STATE/TASK_QUEUE/council/run-report file, and nothing in `docs/process_traces` outside the packet directory. None of the auto-loaded text was used as evidence.

**Charter digest.** Expected (supplied independently of the packet): `099de884…95d81`. Observed: `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` by `shasum -a 256 docs/process/coldgate_charter.md`. Packet expected `1cf13c95…f094`, observed `1cf13c955c8fb32ca807bced3a5e337eb4e083bb81619325a8b3e09fbbf11094` by `shasum -a 256`. Match on both.

**Validator.** Run 1 with the deliberate typo sha `…95d82`: `scripts/validate_gate_packet.py` returned `"result":"REFUSE","reason":"charter_trusted_observed_mismatch"`, rc=2. Run 2 with `…95d81`: `"result":"PASS"`, rc=0, all 12 exhibits `expected_sha256 == observed_sha256`, `exhibit_manifest_sha256 78c294a7…`. I judged only after run 2 passed.

**Code evidence.** `git archive 0fa4e6e3` (`0fa4e6e3bdb55e1cf4129cd4b027a4c00b54f97e`) extracted to `/tmp/coldgate-esc2-278ebc9e/`; all probes ran there with `PYTHONPATH=.`. Never sudo/launchctl/powermetrics/systemsetup; never the discovery suite.

## 1. Read set and executed probes

Read in full: charter; charge; ex-41, ex-42 (+ four probe files), ex-43, ex-45, ex-46, ex-47; ex-14; ex-02d lines 50-72 (glossary), 398-419 (§5.1-5.3 legend), 440-500 (INV-06..17), 599-670 (INV-36..52, §6), 242-262 (§2.8, §2.9), 367-374 (§3.6); ex-39b lines 1-40, 171-192, 461-512. Code at 0fa4e6e3: `joulewise/scored_packer.py:60-100, 160-300`; `tests/scored_roster_checker.py:255-275, 560-600, 641-643, 780-790`; `tests/test_scored_packer_fuzz.py:24, 42-125, 140-215`.

Executed, all against the archive:

| Probe | Result |
|---|---|
| Opus `probe_b.py` (B1 revive voided superseded parent; B2 list it in a new envelope) | **Reproduced.** Both: `_structure`/`_seal(finalize)`/`_seal` ACCEPT; two live owners of L1I0 (`large:decode:1:0` and `…:single:0`); checker B1 `['INV-32','INV-38']`, B2 `['INV-36','INV-38']`, never INV-11. |
| Opus `closed_own.py` over the legal corpus | **Reproduced**: 1,868 rosters, 0 violations (3 min 42 s). NOTE: this probe implements only the count rule and the superseded-holder rule; it does **not** implement the third clause of Opus's closed form ("the live holder has no terminal item"). See K6(i). |
| Opus `seal_gap.py 2` (14,018 two-operator mutants, seal accepts while checker static rows object) | **Reproduced exactly**: 237 escapes; rows missed INV-37 179, INV-22 47, INV-33/43 29, INV-50 16, INV-11 16, INV-10 16, INV-23 11, INV-41 9, INV-25 5. |
| Opus `cure_a.py 2` (Astra's literal predicate patched in memory) | **Reproduced exactly**: 336 escapes; INV-11/10/50 → 0; INV-37 → 278. The +99 are every composition containing `op4_add_terminal` (one terminal entry for one item of a live block). |
| My `judge_probe.py`: five named witnesses × three candidate INV-11 texts, plus a 420-roster legal subset (seed 291013, i = 0..11) evaluated under the **full three-clause** closed form, Fable's (e1), and the literal text | Table below. |

| Witness (built from `_split_route()` roster, refreshed with `refresh_derived`) | Seal at 0fa4e6e3 | Checker at 0fa4e6e3 | literal 02d:467-469 | Fable (e1) | Closed form (3 clauses) |
|---|---|---|---|---|---|
| AUD-1 (clone live 2-item parent under new id, list live, terminalise all items naming the original) | ACCEPT | INV-10, **INV-11**, 22, 29, 31, 34, 36, 37, 38, 41, 50 | violation | violation | violation (count 2,1) |
| probe-D (one terminal entry for item 0 of a live 2-item parent) | REFUSE `inv_11` (the block-id test is stricter here) | INV-52 only (my terminal entry is not type-clean for the checker; irrelevant to the predicate) | **ok — the contract as written accepts it** | violation | violation (count 1,1; holder-has-terminal-item) |
| B1 | ACCEPT | INV-32, INV-38 | **ok** | **ok** | violation (count 2,0) |
| B2 | ACCEPT | INV-36, INV-38 | **ok** | **ok** | violation (count 2,0) |
| Legal contrast (single 1 voided + terminal; single 0 the one live owner; parent superseded, unlisted) | ACCEPT | INV-32, 37, 38 (history rows from my hand-made terminal; ownership shape legal) | ok | ok | ok |
| Legal subset, 420 rosters | — | — | 0 | 0 | 0 |

Two facts decide most of what follows. (1) The contract's INV-11 as written is open: B1/B2 satisfy it and put two live owners on one item. (2) Fable's (e1) closes probe-D but not B1/B2; only the closed form closes all four and still accepts the legal corpus and the legal contrast.

## 2. Packet hygiene

No cherry-picking found. The synthesis quotes every seat's divergence; Sol and Astra are correctly recorded as not having probed B1/B2. Two defects, neither blocking a ruling: (a) only Opus's probe files are in the packet; Fable's probes A-D and Astra's `two_live.py`/`cure_probe.py` are cited but not exhibited, so I reproduced probe-D and AUD-1 myself (above); (b) the synthesis's E-1 evidence line "0 violations on 1,868" is reported for the full closed form but was measured on two of its three clauses (K6(i)). Charter §9: two consecutive same-signature failures make the next spend a consult or redesign, not round three. The plan before me **is** a redesign (one ownership view, a contract amendment, a seal-level oracle), and the consult has been held; licensing round 3 is therefore justified on its face. That is the only presumption I apply.

## 3. Rulings K1-K6

### K1 (E-1) — AFFIRM the closed form; REJECT (e1) as sufficient; text below. Severity of the underlying defect: BLOCKER (unchanged from ex-39b AUD-1); of the contract hole: MATERIAL.

Deciding evidence: `probe_b.py` (B1/B2 sealed with two live owners; literal predicate "ok"); `judge_probe.py` ((e1) "ok" on B1/B2; closed form violation on AUD-1/B1/B2/probe-D, ok on the legal contrast and 420 legal rosters); `closed_own.py` (0/1,868 on the count and superseded clauses). Opus's B1/B2 claim stands. The synthesis is right that the closed form subsumes (e1), and I make that binding: no seat may implement (e1) alone.

**Amendment text (replaces 02d:467-469; 02d:466 ruled text and 02d:62 glossary unchanged):**

> - Predicate (closed form, A291-R3). For each model in `role_to_model_id` and each registered item, define LIVE(model, item) = the list of `(block_id, envelope index)` pairs such that a block with that `model` contains the item and its `block_id` is in that envelope's `blocks` — every block counts, whether or not it is `superseded` or terminal; TERM(model, item) = the `terminal_refusals` entries whose `model` and `item_id` match. INV-11 holds iff for every (model, item): `(len(LIVE), len(TERM))` is `(1, 0)` or `(0, 1)`; and when `len(LIVE) == 1`, the listed block has `superseded == false` and none of its items is a terminal item. Any other state is refused `inv_11`.
> - The v4 clauses (a)/(b) are implied by this predicate and are retained as history only; where a text cites "INV-11 (a)/(b)" it now means this predicate. The 45/21 §7(S) parse residual noted in Final texts v4 item 3 is closed by this amendment.

### K2 (E-2) — Write a different text: the map's home is a 02d addendum table; REJECT a new `docs/contracts/scored_ownership.md`. MATERIAL.

Reason: the contract is the one authority (charter §7); a second contract file splits it and creates the conflict-of-authority case that forces REFUSE at later gates. Astra's matrix content is right; its home is wrong. Data form: the map exists as three frozensets of row ids exactly as headed in 02d ("INV-11", "INV-33/43"). The checker may not import `joulewise` (02d:637), so the map is carried twice and pinned equal: `SEAL_ROWS/REPLAY_ROWS/EXECUTED_ROWS` in `joulewise/scored_packer.py` (P) and an identical literal in `tests/test_scored_packer_fuzz.py` (K), with one integration test asserting equality. The checker itself carries no map.

**Rows the seal must own (mandatory; the magistrate's Gate 0 text assigns every remaining F:a/Chk:yes row with a written reason):** INV-01, 02, 03, 04, 05, 06, 07, 08, 51 (registration/identity, present today); INV-09; **INV-10 including full §3.1 formation (parents are exactly the registered slices)** — today `_structure` checks only identity/non-emptiness (`scored_packer.py:167,169`) and 16 INV-10 escapes reach the seal (`seal_gap 2`); **INV-11 closed form**; INV-12; INV-14, 15, 16, 17, 18 (placement targets), 20, 21, 24; **INV-37 structural clause** — `(model, item_id)` unique (02d:254) and each entry's `(block_id, attempt)` names a **voided** placement of a block containing the item (02d:608) — see K6(ii); INV-52; plus the codes `report_order`, `inv_29`, `invalid_elapsed`, `invalid_observation_order`, `culprit_limit`, `inv_35c`, `reschedule_without_culprit` already in `_structure`. **Replay-owned with the reason "needs the reconstructed event history":** INV-30, 31, 32, 33/43, 35 (decision-linkage clauses), 36 (stage history), 38, 39, 46, 47, 48. INV-22, 23, 25, 41, 50 leaked in `seal_gap 2` and have no owner today; the Gate 0 text must assign each one (seal or replay) with a reason — leaving any row unassigned fails Gate 0. EXECUTED_ROWS = INV-26, 45, 49 (F:b).

**AST pin (K writes it in `tests/test_scored_packer_fuzz.py`; P must satisfy it):** walk `ast.parse(inspect.getsource(sp))`; collect every string constant that is the second positional argument of a `Call` to `Name("_need")` inside `_structure`, `_ownership`, `_live_index`, `_seal`, `_predictions`; map codes to rows by 02d §5.2 (`inv_xx` → `INV-xx`, ruled codes by the table in the same test); assert the resulting row set ⊇ `SEAL_ROWS` and ∩ `REPLAY_ROWS` = ∅; assert `sp.SEAL_ROWS == FUZZ_SEAL_ROWS` and likewise for the other two.

### K3 (E-3) — AFFIRM: `_ownership(registration, roster)` inside `joulewise/scored_packer.py`; REJECT a new module. MATERIAL.

A new `joulewise/scored_ownership.py` (Astra) adds an import boundary and rewrites R4c's confinement for no independence gain: P authors both files. Astra's lossless requirements are adopted as text. **Rule:** `_ownership` is called once inside `_structure`, immediately after the per-block and per-envelope type rows (`:165-192` at 0fa4e6e3) and before any ownership row; it returns a plain dict with keys exactly `blocks` (id → block), `live` ((model, item) → list of (block_id, envelope index), every listing kept, no overwrite), `term` ((model, item) → list of entries, multiplicity kept), `listing` (block_id → count of envelopes listing it); it is rebuilt on every call and never cached or accepted from a caller. INV-10 formation, INV-11 (closed), INV-12, INV-37 structural clause are evaluated on it, in that order, before `_checked_derived`. `_parent_facts` takes an item's owner as `live[(model, item)][0]` when `len == 1` and records no index otherwise; it no longer walks `blocks` for a single. Lines `:225-235` are deleted. **AST confinement (R4c gains (vi)):** a `Subscript` or `.get` `Call` whose constant is `"blocks"`, `"placements"`, `"terminal_refusals"` or `"envelopes"` appears only in `_ownership`, `_live_index`, the type rows of `_structure` (statements before the `_ownership` call — K pins by asserting the call is the first statement after the envelope loop), `_replay_roster`, `pack`, `_place`, `_new_envelope`, `requeue_overrun`; `_parent_facts` contains none of them.

### K4 (E-4) — AFFIRM with two amendments. MATERIAL.

Seats and families as synthesized: Gate 0 (magistrate text + paired refuter of a different family, given B1/B2/AUD-1/probe-D), then **K = Opus 5.5** and **P = Sol 6.0**, blind to each other's diffs, in parallel after Gate 0; integrate; then the E-5 gate. Astra's "K first, P after K's tests are pinned" is rejected: it costs P's blindness to K for no gain, because RED-at-`0fa4e6e3` is checkable after the fact. Scopes: K `[tests/scored_roster_checker.py, tests/test_scored_roster_checker.py, tests/test_scored_packer_fuzz.py, tests/scored_case_generator.py]`; P `[joulewise/scored_packer.py, tests/test_scored_packer.py]`. Sol's "checker unchanged" is rejected: the checker's `:585-590` must move to the closed form or it keeps missing B1/B2. Amendment 1: RED-at-base is per target — the K fuzz/regressions must be RED at `0fa4e6e3` on AUD-1, B1, B2 (seal accepts) and on the checker's own INV-11 row for B1/B2/probe-D (checker silent), while probe-D at the seal is already `inv_11` there (executed) and is not a RED requirement. Amendment 2: the K oracle property is refusal, not code equality: `check_roster(M) ∩ SEAL_ROWS ≠ ∅ ⇒ _seal(reg, M) raises PackingRefusal`; code equality is asserted only in the five named regressions. **Final texts v4 items superseded:** item 3 in full (replaced by A291-R3 text 3 below); item 6 R4c gains (vi) and R1-R5b otherwise stand; item 7 properties (b)-(e) stand and gain (g)/(h) below; items 1, 2, 2a, 4, 5, 8 stand unchanged.

### K5 (E-5) — AFFIRM, with the stop rule and forger seat as exact text. MATERIAL.

Gate before merge, in order: (1) five scored modules green at the integrated head, `python3 -B -m unittest discover -s tests` green; (2) K's exhaustive two-operator and sampled three-operator runs (alphabet = the ten operators + `clone_block`, `terminalise_live`, `revive_voided`, `retarget_terminal`, `flip_superseded`) on the integrated head: zero mutants where the seal accepts and the checker reports a `SEAL_ROWS` row; zero closed-ownership breaches accepted by the seal; zero refusals on the legal corpus; zero `internal:`; (3) the full three-clause closed form evaluated by the checker over the full `generate_case` corpus (seeds 291013-291016, i 0-11): zero violations (K6(i)); (4) Astra's mutation kills executed and each reported killed: `all→any` in the terminal-block test, refusal-`block_id` matching restored, dictionary overwrite in `live`, `(1,0)/(0,1)` weakened to `≤`, and removal of each of the three closed-form clauses; (5) similarity screen per Final texts v4 item 8 unchanged; (6) A6 timing re-measured; (7) **forger seat**: a fresh seat of a family that is neither P's nor K's, `WRITE_SCOPE: []`, in a worktree at the integrated head, given only the amended 02d, the glossary, and `joulewise/scored_packer.py`, told nothing of AUD-1/B1/B2/probe-D, 30 minutes wall: "compose a roster with forged ownership that `_seal(finalize=True)` and `_seal` both accept". Success = any accepted roster on which the checker reports a `SEAL_ROWS` row or the closed form is breached. **Round 3 passes iff the forger fails.** **Stop rule (binding text):** "If the forger, the fuzz, or the re-audit produces an escape on a row in `SEAL_ROWS`, that is a table-design defect: no seat patches the row; the magistrate convenes a consult with the escape as its brief. If the escape is on a `REPLAY_ROWS` row that a single roster could have refused, the row moves to `SEAL_ROWS` by a ruled amendment, not by a seat."

### K6 — Dropped or mis-stated items. Findings tiered.

(i) **MATERIAL — the closed form's third clause was never bench-checked by Opus.** `closed_own.py:13-18` tests counts and `superseded` only. The synthesis (ex-47:27, :39) reports "0 violations on 1,868" for the closed form as stated with three clauses. My 420-roster subset shows 0 violations under all three clauses, so the clause is legal-safe on that evidence; the E-5 gate step (3) makes the full-corpus check mandatory before merge.

(ii) **MATERIAL — Astra's literal cure really does push forgeries onto INV-37, and the seal must therefore own INV-37's structural clause.** Executed: 179 → 278 INV-37 escapes at arity 2, every added escape a composition with `op4_add_terminal`, i.e. one terminal entry for one item of a still-live block (the probe-D shape). The closed form's third clause turns that shape into `inv_11` at the seal. It does **not** cover `retarget_terminal`: an item with `(0, 1)` whose single entry names a block/attempt that is not a voided placement of a block containing it passes the closed form and is INV-37 only. Hence INV-37's structural clause (02d:254, :608) is `SEAL_ROWS`, not replay (K2). INV-37's history clause ("effects differ from replay", checker `:774`, and append-only `:810`) stays replay-owned.

(iii) **MATERIAL — the checker's own INV-11 row is part of the defect.** `tests/scored_roster_checker.py:585` filters holders by `not b['superseded']` and so is blind to B1/B2 exactly as the contract is. Any plan that "pins the existing checker" (Astra step 2, Sol step 2) ships the hole into the oracle. K rewrites `:581-590` to the closed form.

(iv) **NIT — `_live_index` double-listing refusal is redundant after `_ownership`** (`listing[bid] > 1` is a count failure); keep it as Final texts v4 item 4 requires, but the AST pin must tolerate two `inv_11` sites.

(v) **NIT — packet completeness:** Fable's probes A-D and Astra's scripts are cited, not exhibited; future packets should exhibit every probe a seat's claim rests on.

(vi) **NIT — brief ex-41:5 says round 1's forgery was "two live placements for one block"; ex-39b:486 shows that route closed (`duplicate FINALIZE inv_11`).** Consistent with the record; no effect.

Disagreements with the lead's labeled disposition, stated explicitly: E-2's home (addendum table in 02d, not a new contract file, and the map is carried in packer + fuzz, not "shared by both modules"); E-4's RED-at-base wording; E-5's gate gains steps (3), (4) as mandatory and the exact stop-rule text; K6(ii) adds INV-37-structural to the seal's mandatory rows. Everything else in ex-47's proposed rulings is affirmed.

## 4. Final texts A291-R3 (paste verbatim into the K and P briefs)

**Glossary (02d:57-64, verbatim, above every text that uses it):**

> - **Parent.** A block created by `pack`; its `parent_block_id` is null.
> - **Single.** A one-item block created by a split. Its `parent_block_id` is its parent's id.
> - **Cell.** A pair (model id, level).
> - **Placement.** One scheduling of one block attempt into one envelope (§2.6).
> - **Live placement.** A placement is live when its `block_id` is in its envelope's `blocks` list. **Voided** means the id is in that envelope's `voided_block_ids` list.
> - **Terminal item.** An item with a `terminal_refusals` entry. A **terminal block** is one all of whose items are terminal.
> - **Non-terminal parent.** «A "non-terminal parent" is a parent none of whose items has a terminal refusal. A parent "occupies" the envelopes of its and its singles' LIVE placements only; voided placements do not count.» [RD-5]
> - **Reported envelope.** An envelope whose `observations` is not null. **Root roster:** «A root roster is one with `events == []`.» [FT-4]

**R3-0 (contract, magistrate, Gate 0).** 02d INV-11 predicate replaced by the K1 amendment text verbatim. 02d gains §5.4 "Boundary map (A291-R3)": a table with one row per F:a/F:b/F:c row id and a column `owner ∈ {seal, replay, executed}` and a column `reason`; the mandatory `seal` rows are those K2 lists; no row is blank. `SEAL_ROWS`, `REPLAY_ROWS`, `EXECUTED_ROWS` are the three sets of row ids read off that column.

**R3-1 (P: `_ownership`).** In `joulewise/scored_packer.py`, `def _ownership(registration, roster) -> dict` with keys exactly `blocks`, `live`, `term`, `listing` as K3 defines; called exactly once, as the first statement of `_structure` after the envelope loop that ends at 0fa4e6e3 `:192`; never cached; no module-level container (R5b). Rows evaluated on it, in order, each with `_need`: INV-10 formation — for each model and level the parents' item lists equal the §3.1 slices, else `inv_10` "formation"; INV-11 closed form — for every (model, item) `(len(live.get(k, [])), len(term.get(k, [])))` in `{(1, 0), (0, 1)}` and, when `(1, 0)`, holder `superseded == False` and no holder item in `term`, else `inv_11` "item conservation"; INV-12 both clauses (unchanged text 3 wording); INV-37 structural — `(model, item_id)` unique over `terminal_refusals` and each entry's `(block_id, attempt)` equals the `(block_id, attempt)` of a placement whose `block_id` is in its envelope's `voided_block_ids` and whose block contains `item_id`, else `inv_37` "terminal provenance". Lines `:225-235` deleted. `_parent_facts` takes the owner from `live` as K3 states. Module constants `SEAL_ROWS`, `REPLAY_ROWS`, `EXECUTED_ROWS` as frozensets of row-id strings copied from §5.4.

**R3-2 (P: AST and regressions in `tests/test_scored_packer.py`).** R4c(vi): the K3 confinement, on `inspect.getsource(sp)`. Regressions, each building its roster exactly as `judge_probe.py`/`probe_b.py` do from `_split_route()` and `refresh_derived`, resealed with `sha256 = None` and last event sha `""`: AUD-1 → `_structure` raises `inv_11`, `_detail` == "item conservation"; B1 → `inv_11`; B2 → `inv_11`; probe-D → `inv_11`; legal contrast → `_structure` returns, `_seal(finalize=True)` returns. R2b's expected code stays `inv_12` (its roster has no terminal entry and one live owner per item; P asserts this in the test).

**R3-3 (K: checker).** `tests/scored_roster_checker.py:581-590` replaced by the closed form: `live` built over every listed block regardless of `superseded`; report `INV-11` with detail `item ownership {m}:{item}` when the counts are not `(1,0)/(0,1)`, or the single live holder is superseded, or any of its items is in `terms`. `:641-643` INV-37 rows unchanged. K's `tests/test_scored_roster_checker.py` gains B1, B2, probe-D (checker reports `INV-11`, RED at `0fa4e6e3`) and the legal contrast (no `INV-11`).

**R3-4 (K: fuzz, `tests/test_scored_packer_fuzz.py` + `tests/scored_case_generator.py`).** Alphabet = the ten operators of v4 item 7 plus `clone_block`, `terminalise_live`, `revive_voided` (as `ex-42-probe-seal_gap.py:11-31`), `retarget_terminal` (change one entry's `block_id` or `attempt` to another block/attempt of the same model), `flip_superseded_live` (set a live parent's `superseded` true / a listed superseded parent's false). Composition: every ordered pair exhaustively over the four `CASES`; triples by seeded sample of 2,000. After composing: `refresh_derived`, `sha256 = None`, last event sha `""`, then `sp._seal(reg, m, finalize=True)` and `sp._seal(reg, m)`. Property (g), seal-level oracle: for every mutant the seal accepts, `{v.inv_id for v in check_roster(g, m, p)} ∩ SEAL_ROWS == set()`; else hard failure listing (ops, seed, i, k, rows). Property (h), closed-ownership oracle independent of the checker: the K1 predicate, implemented in the fuzz module, holds on every seal-accepted mutant. AUD-2: `:184` stores `('checker-crash', name)` in a dedicated `checker_error` field; `test_a` asserts the field is `None` on every row; one test injects a checker exception and asserts `test_a` fails. `FUZZ_SEAL_ROWS/REPLAY_ROWS/EXECUTED_ROWS` literals equal `sp.*` (one test). The K2 AST pin. Properties (a)-(f) of v4 item 7 stand; (b) keeps the public entry points as an additional, weaker check.

**R3-5 (gate and stop rule).** K5 verbatim.

## 5. Severity summary

BLOCKER: the seal accepts forged ownership at `0fa4e6e3` (AUD-1, B1, B2 executed) — merge stays blocked until R3-1/R3-3 land and K5 passes. MATERIAL: K1 (contract hole; (e1) insufficient), K2 (map home; unassigned rows INV-22/23/25/41/50), K3 (module/AST), K4 (RED-per-target; refusal-not-code oracle), K5 (steps 3-4; stop rule text), K6(i)-(iii). NIT: K6(iv)-(vi).

Verdicts: K1 AFFIRM (text amended as above); K2 AFFIRM-with-different-text; K3 AFFIRM; K4 AFFIRM with two amendments; K5 AFFIRM with exact text; K6 findings as listed. No REFUSE.
