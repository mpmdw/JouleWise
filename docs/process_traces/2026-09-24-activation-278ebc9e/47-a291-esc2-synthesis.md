# 47 — Synthesis of the A291 escalation-2 consult (magistrate, Opus 5.5)

Four blind seats answered brief 41: Opus 42 (with probes in 42-a291-esc2-opus-probes/), Fable 43, Sol 45 and Astra 46. This synthesis binds nothing; a cold Fable gate rules on packet 48.

Terms:
- **Seal:** `_seal` in `joulewise/scored_packer.py`, which must refuse any roster that violates the contract before derived arithmetic.
- **Checker:** the independently written test oracle `tests/scored_roster_checker.py`.
- **Ownership:** which block holds each registered (model, item). An item is either live in exactly one placement, or terminal (refused).
- **AUD-1:** the delta re-audit's forgery. A block copied under a new id is listed live, while terminal entries for all its items name the original block. `_structure` and both seal modes accept it; the checker reports INV-11; replay later refuses with `inv_38`.

## Agreement (4/4)

1. Final text 3 quotes the contract's INV-11 wording faithfully. The immediate defect is the implementation at `scored_packer.py:225-235`: a per-item terminal test keyed on the refusal's `block_id` instead of the contract's "a terminal block is one all of whose items are terminal" (02d:62).
2. The structural cause is that ownership is reconstructed several times, in different coordinates, by different predicates (`_structure`, `_live_index`/`_parent_facts`, replay). Each patch closes one reading while another stays open.
3. The cure is **(b): one ownership view, built once and validated**. INV-10/11/12/17/52 are evaluated on it before arithmetic, and `_parent_facts` derives positions from the same view. It contains **(a)**, the literal contract predicate, as its acceptance condition.
4. **Reject (c)** (the checker as a production dependency): the oracle would lose its independence. Reject **(d)** (a production differential) as the primary cure.
5. **Fuzz:** the ten-operator, single-edit fuzz cannot express the forgery, and its oracle sits behind replay (`inv_38` masks seal misses). Required changes:
   - composed operators (clone-block-new-id, terminalise all items of a block, revive voided, retarget a terminal entry, flip superseded);
   - a **seal-level oracle** (the seal accepts while the checker's seal-owned rows object ⇒ fail);
   - the AUD-2 fix (checker crashes must fail the run);
   - AUD-1 as a fixed regression.
6. The checker stays test-only, and P and K stay in different model families.

## Divergence

- **Contract amendment to INV-11.**
  - Opus says the contract's INV-11 is **not closed**. Its probes B1/B2 revive a superseded parent as a live listing, so an item gets two live owners, and both the seal and the checker miss it (they report INV-32/36/38, never INV-11). Opus proposes a closed form: for each (model, item), (live listings over ALL blocks, terminal entries) ∈ {(1,0), (0,1)}, and the one live holder is not superseded and has no terminal item. It found 0 violations on 1,868 legal rosters.
  - Fable proposes (e1): INV-11 (a) gains "and no `terminal_refusals` entry names the item".
  - Sol and Astra say text 3 and the checker are correct as they stand and need no AUD-1 repair. They did not probe B1/B2.
- **Seal-coverage / phase map.** Opus wants a table assigning every F:a and Chk:yes row either to a seal clause or to replay with a reason, pinned by an AST test. The seal today has no inv_22/23/25/27/36/37/41/50 code, and Astra's literal cure pushes 278 composed forgeries onto INV-37. Fable wants a data-only `SEAL_ROWS`/`REPLAY_ROWS` map shared by both modules. Astra wants an invariant-to-boundary matrix in a new `docs/contracts/scored_ownership.md`. Sol wants the ownership table to expose counts and terminal status.
- **Module shape.** Astra wants a new `joulewise/scored_ownership.py`; the other seats keep the view inside `scored_packer.py`.
- **Order.** Opus has step 0 (magistrate text plus a text-only cold gate), then K first, then P parallel after step 0. Fable has Gate 0, then P ∥ K. Astra has a contract seat, then K first, then P after K's tests are pinned. Sol does not specify.
- **Final gate.** Fable wants a fresh forger seat that sees only the contract and has 30 minutes to forge ownership past `_seal`. Round 3 passes only if the forger fails; otherwise `_structure` is rewritten wholesale as table-driven. Opus wants a fresh delta refuter told "forge two live owners with three composed edits". Astra wants mutation kills (all→any, refusal-id matching restored, duplicate overwrite, weakened multiplicity, each ownership guard removed). Opus also has a stop rule: an escape on a row the table owns is a table-design defect, to be escalated, not patched.

## Proposed rulings (the magistrate's; the judge may amend any)

- **E-1 (contract).** Amend 02d INV-11 to Opus's closed form, which subsumes Fable's (e1). Bench-check both of the following against the probes:
  - the closed form refuses AUD-1, B1, B2 and Fable's probe-D;
  - it accepts the legal corpus (0 violations on 1,868) and the legal contrast (one item terminal, the other's single live, parent superseded).
  Every brief pastes the 02d:57-64 glossary above any text that uses it.
- **E-2 (coverage).** A data-only row→boundary map (`SEAL_ROWS`, `REPLAY_ROWS`, `EXECUTED_ROWS`) is added as a contract addendum table. Every F:a/Chk:yes row is either a seal clause or replay-owned with a written reason. An AST test pins the mapping. The seal-level oracle reads the map.
- **E-3 (implementation).** The ownership view lives in `joulewise/scored_packer.py` as `_ownership(registration, roster)`, built once. Raw `blocks`/`terminal_refusals` subscripts are confined to `_ownership` and the type rows (AST rule). `_parent_facts` reads the view.
- **E-4 (seats and order).** Gate 0 (this ruling plus a paired refuter), then K (Opus; checker closed INV-11, composed generator, seal-level oracle, AUD-2, the regressions AUD-1/B1/B2/probe-D/legal contrast; RED at `0fa4e6e3`), in parallel with P (Sol; the E-3 view and E-2 seal clauses; blind to K). Then integrate.
- **E-5 (gate before merge).**
  - All scored modules green.
  - The exhaustive two-operator run and the sampled three-operator run show zero seal-accepts on seal-owned rows and zero closed-ownership breaches.
  - Astra's mutation kills are executed.
  - Then a **fresh forger seat** (Fable's design).
  - Stop rule: an escape on a table-owned row is escalated, never patched.
