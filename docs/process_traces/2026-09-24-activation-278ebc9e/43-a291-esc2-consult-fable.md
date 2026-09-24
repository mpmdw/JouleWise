**Seat: Fable 5.1** (blind consult, read-only; probes under `/tmp/278ebc9e/esc2-fable/`, run with `PYTHONPATH=. python3 -B`)

## Q1. Root cause

**Architecture, with the brief as the trigger. Text 3 does not mis-state INV-11.** Text 3 paraphrases 02d:467-469 faithfully ("not terminal ... in exactly one envelope's blocks"). What it never does is gloss "terminal". The definition lives only in the glossary at `ex-02d-contract-v4.md:62` ("a terminal block is one all of whose items are terminal"), which text 3 does not cite. P met an unglossed term and re-derived it locally as "a terminal entry names this item AND this block id" (`joulewise/scored_packer.py:234`). That is the first-use failure Ed's writing standard names, and it is the fourth time this module transcribed the ownership vocabulary from English:

- `scored_packer.py:70` `_live_index`: "live" = listed in one envelope.
- `scored_packer.py:83-84` `_parent_facts`: "terminal" = `(model, item) in terminal_refusals`. This is the contract's definition.
- `scored_packer.py:225-235` `_structure` INV-11 row: "terminal" = entry naming item AND block id. A different definition of the same word, eleven lines below the right one.
- `tests/scored_roster_checker.py:577,585`: the contract definition again.

So the packer disagrees with itself before it disagrees with the checker. Every seal row rebuilds "live", "terminal" and "owner" from the raw lists with fresh comprehensions. Nothing in the module says what an owner is once. Both round-1 consults named exactly this (Sol Q1: "reconstructed separately by `_live`, `_derived`, `_structure`"; Opus Q1: populations "only well defined under INV-11/INV-12"), and round 2 answered by adding a third reconstruction rather than removing two. That is why the signature repeats: each patch is a new transcription, and each transcription is a new chance to misread a word.

**Two further structural facts, both executed:**

1. **Replay masks the seal at every public entry.** Probe A submits the AUD-1 forgery to all three entries:
```
seal(verify) ACCEPT                      checker ['INV-10','INV-11','INV-37','INV-38','INV-41','INV-50']
requeue_overrun        REFUSED inv_38    verify_executed_roster REFUSED inv_38    executed_status REFUSED inv_38
```
The seal is the only pre-replay ownership check, and no test observes it in isolation. The fuzz's property (b) ("checker non-empty ⇒ entry refused") is satisfied by inv_38, so AUD-1 was invisible to it by construction, not by operator choice.

2. **The contract's INV-11 (a) has its own hole.** Clause (a) at 02d:467 never says "and no terminal entry names the item". Probe D builds a rescheduled two-item parent, live at attempt 1, with one terminal entry for item 0 naming its voided attempt-0 placement:
```
checker ['INV-37','INV-38']          (no INV-11: contract-literal (a) holds)
packer _structure REFUSED inv_11     (its block-id test happens to be stricter here)
```
So even a perfectly literal implementation leaves packer and checker disagreeing on that roster, in the opposite direction. The ruled text 45/21 §7(S) means an exclusive-or; the predicate as written is not one. This is not text 3's residual (the 45/21 parse) and is not yet ruled.

## Q2. Cures

**(a) Literal contract predicate in the packer.** One line; the re-audit's `cure_probe.py` shows two_live → inv_11, 37 tests OK. Guarantees: closes AUD-1 only. Leaves two definitions of "terminal" in the module and the probe-D hole shared with the checker. A fifth transcription. Component of (b), not a cure.

**(b) One ownership table, every ownership row evaluated on it.** Probe C exec's a 20-line `_ownership(registration, roster)` into the module: one pass builds `listed` counts, `terminal_items`, and per (model, item) `live_once`, `terminal_names`, `any_listed`; the INV-11 row becomes a single `_need` over the table. Result:
```
CURE two_live.py inv_11: item conservation large:L1I0
probe_d: packer _structure ACCEPT, checker no INV-11   (now consistent with the contract as written)
packer tests OK 37
```
Guarantees: "live", "terminal block", "owner" are defined once; `_parent_facts` must be rewritten to take its owner from `live_once` so the lever and the seal cannot diverge; INV-10/12/17/52 read the same `listed`/holders. A misread becomes one reviewable function instead of five. Cost: ~40 lines plus `_parent_facts` refactor; R4c(iv) already confines `_live_index` to `_parent_facts`, so extend it to confine raw `terminal_refusals`/`blocks` subscripts to `_ownership` and the type rows. Recommended.

**(c) Checker as production dependency.** Kills the oracle: the checker cannot report a misread it now executes for the packer, and probe D shows the checker carries a misread of its own today. Reject.

**(d) Differential guard in production.** Doubles the ownership computation per seal (cheap next to replay) but turns any disagreement into a night-time refusal of a legal roster, and keeps two implementations to maintain forever. Reject in production; adopt as the fuzz oracle (Q3).

**(e) Mine.** (e1) Contract amendment: INV-11 (a) gains "and no `terminal_refusals` entry names the item"; checker :585 and `_ownership` implement it. (e2) A data-only row→phase map (`SEAL_ROWS`, `REPLAY_ROWS`, `EXECUTED_ROWS`, strings shared by both modules, no imports) so a seal-level oracle knows which checker rows the seal must answer for. (e3) Every brief pastes the glossary lines 02d:57-64 verbatim above any text that uses them, and the lens checks first-use, not just fidelity.

## Q3. Regression and fuzz design

**Why the ten operators missed it.** AUD-1 needs three coordinated edits: clone a block under a new id, list the clone live, and add terminals for all its items naming the old id. `op2` (`tests/test_scored_packer_fuzz.py:53`) duplicates under the same id, which `_live_index` refuses; `op4` (:78) adds one terminal for one item; each operator runs alone (:174). No composition reaches "every item terminal, block still live". And per Probe A the oracle at :156-161 would have accepted the row anyway.

**Design.**
1. **Oracle at the seal, phase-aware.** After test-side `refresh_derived` + `reseal`, call `sp._seal(reg, m)` directly. Property: `set(checker) ∩ SEAL_ROWS ≠ ∅ ⇒ _seal refuses` and `code ∈ {row.lower() for row in checker}`. Probe B over the existing 899 single-edit mutants finds 221 rows where the seal accepts what the checker flags, all INV-30/31/36 (replay-owned per 02d:622), which is why the phase map is a precondition, not a nicety.
2. **Composed ownership operators.** Family: clone-block-new-id, list-live(block, new envelope), void(block), terminal(item, naming block_id), flip-superseded, drop-single. Draw k ∈ {2,3} with replacement, seed-keyed; keep the mutant iff the checker reports a seal-owned row. Run on the same four cases.
3. **Property-based, table-first.** Generate the ownership table (per item one of: live-once, terminal, both, twice-live, neither), materialize a roster satisfying it, and assert `seal verdict == table legality`. This targets INV-11's meaning rather than edit paths.
4. **Named regressions:** AUD-1 verbatim (`two_live.py`) refused at `_seal` with inv_11; the probe-D roster refused with inv_11 after (e1); the legal contrast (one item terminal, the other's single live, parent superseded) accepted. Fix AUD-2 (:186 vs :206) so a checker crash fails the run.

## Q4. Fix round 3

- **Gate 0, magistrate only, before any seat:** rule (e1); amend text 3 to paste 02d:57-64 verbatim; rule the row→phase map as an addendum table. Check R2b's expected code survives (e1) (it should: R2b's roster has no terminal entry).
- **Seat P (Sol 6.0 high, or Opus 5.5), WRITE_SCOPE: `joulewise/scored_packer.py`, `tests/test_scored_packer.py`.** Build `_ownership`; INV-10/11/12 rows and `_parent_facts` consume it; delete :225-235; R4c gains "raw `terminal_refusals`/`blocks` subscripts only in `_ownership` and the type rows"; regressions from Q3.4. P never reads `tests/scored_roster_checker.py`.
- **Seat K (different model family from P), WRITE_SCOPE: `tests/scored_roster_checker.py`, `tests/test_scored_roster_checker.py`, `tests/test_scored_packer_fuzz.py`, `tests/scored_case_generator.py`.** Checker :585 gains (e1); fuzz gets the seal-level oracle, phase map, composed generator, AUD-2 fix. K never reads the packer.
- **Order:** Gate 0 → P ∥ K → integrate → gate.
- **Gate before merge:** all 71 + new tests green; AUD-1 and probe-D witnesses refused at `_seal` with inv_11; composed fuzz reports zero seal-accepts on seal-owned rows, zero legal-corpus refusals, zero `internal:`; similarity screen unchanged; then a **fresh forger seat** (read-only, sees only the contract) spends 30 minutes composing its own ownership forgery. Round 3 passes only if that seat fails to forge. If it succeeds with the signature "seal accepts forged ownership", stop patching rows and rewrite `_structure` wholesale as table-driven.
