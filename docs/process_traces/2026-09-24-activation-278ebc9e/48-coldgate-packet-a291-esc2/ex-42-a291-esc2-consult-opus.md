# Opus 5.5 — blind consult, A291 escalation 2

## Q1. Root cause

**Text 3 does not mis-state INV-11. It does two other things wrong.** Its (a)/(b) wording repeats contract 02d:467-469 faithfully. But:

- It says "are not terminal" without writing out the definition, which lives only in the glossary at 02d:62 ("a terminal block is one all of whose items are terminal"). That left room for the implementer to substitute something else.
- It moves block formation out of the seal ("full formation stays with replay `inv_39` and the checker"). It then claims the two readings "differ only on rosters INV-10/INV-12/text 4 refuse anyway". That claim is false at the seal. `_structure` checks only block identity and non-emptiness (`scored_packer.py:167,169`), not INV-10 slice formation. The AUD-1 forged parent `…:1:999` is illegal under INV-10: the checker reports INV-10, and the seal cannot see it.

**The implementation drifts in both directions.** `scored_packer.py:234` replaces "block is terminal" with a per-item test that the terminal entry names *this* `block_id`. So it is looser than the contract on AUD-1 and stricter on partly-terminal live blocks (the audit's `part-terminal-live`: packer `inv_11`, checker not INV-11).

**The architecture is the main cause.** The contract spreads ownership over INV-10 (which blocks may exist), INV-11, INV-12, INV-36 (attempt history) and INV-37 (a terminal entry names a voided attempt). The seal re-states a hand-picked subset of these: `scored_packer.py` contains no `inv_22/23/25/27/36/37/41/50` code (grep). I measured the gap at the seal boundary itself. The script (`/tmp/278ebc9e/esc2-opus/seal_gap.py`) mutates, runs `refresh_derived`, runs `_seal(finalize=True)`, runs verify-mode `_seal`, then the checker, ignoring history rows:

| Mutants (4 fuzz cases) | Seal accepts, checker's static rows object | Rows missed |
|---|---|---|
| one operator: 1,177 | **33** | INV-37 ×20, INV-33/43 ×9, INV-22 ×5 |
| two operators composed: 14,018 | **237** | INV-37 179, INV-22 47, INV-33/43 29, **INV-11 16**, INV-10 16, INV-50 16, INV-23 11, INV-41 9, INV-25 5 |
| two operators + Astra's literal cure (patched in memory, `cure_a.py`) | **336** | INV-11/10/50 drop to 0, but INV-37 rises to **278** |

Astra's cure closes AUD-1. It also lets partly-terminal live blocks through, and the contract assigns those to INV-37, which the seal does not implement. **Patching one row pushes the forgeries onto the next row the seal doesn't have.**

**The contract's INV-11 is not a closed ownership rule.** It counts only holders that are neither superseded nor terminal, so a superseded block listed live is invisible to it. Probe `probe_b.py`: after a split, I revived the superseded parent `large:decode:1:0` as a live listing. B1 moves it from voided to live in envelope 0; B2 lists it in a new envelope 14.

- Item L1I0 then has two live owners: the parent and `…:single:0` in envelope 12.
- `_seal` accepts both forgeries.
- The checker reports B1 as INV-32/INV-38 and B2 as INV-36/INV-38, **never INV-11**.

The checker "agrees" with the packer here only because both implement the same leaky text.

**Why nobody saw it:** fuzz property (b) is judged at the public entry point (`test_scored_packer_fuzz.py:146-154,208-210`), after replay. Replay's `inv_38` hides every miss at the seal.

## Q2. Cures

| | What it costs | What it guarantees |
|---|---|---|
| **(a)** Literal contract predicate | About one line | Closes AUD-1 only. Measured +99 INV-37 leaks. Does not close B1/B2. Needed, but not enough. |
| **(b)** One ownership table | About 60 lines plus a contract amendment and a text-only cold gate | See below. Closes the ownership-forgery class by construction, whatever the operator composition. |
| **(c)** Checker as a production dependency | Runtime is no obstacle: `_static_checks` takes **1.6 ms** against `_seal`'s **2.1 ms** (measured on a 64-block, 33-event final roster) | Closes everything the checker sees. But the checker becomes the specification: shared bugs become undetectable, and B1/B2 prove the checker shares the contract's leak. It would also need splitting into static and replay rows. **Reject as the primary cure.** |
| **(d)** Differential guard in production | A second packer-authored recomputation | It is (b) done twice, by the same author. It is only worth having if truly independent, and then it is (c). Put the differential in the tests instead. |
| **(e)** Mine: (b) + contract amendment + oracle moved to the seal | See below | Every F:a row is either at the seal or explicitly given to replay; the seal is tested at its own boundary. |

**(b) in detail.** Build three indexes once:
- `live[(model,item)]` → list of (block, envelope) live listings, counting **every** block regardless of superseded status;
- `term[(model,item)]` → list of terminal entries;
- a block map.

Then evaluate every ownership rule on those indexes:
- INV-52 types first;
- INV-10 formation (parents equal the registered slices);
- **closed INV-11:** for each (model, item), (number of live listings, number of terminal entries) is (1, 0) or (0, 1), and the one live holder is not superseded and has no terminal item;
- INV-12;
- INV-37 (each terminal entry names a voided placement of that block and attempt);
- INV-17.

`_parent_facts` then reads the table instead of re-walking the roster. Executed probe (`closed_own.py`): the closed INV-11 rule found **0 violations on 1,868 legal rosters** (`generate_case`, seeds 291013–291016, i = 0–11). It rejects B1 and B2 (count (2, 0)) and AUD-1 (two live listings).

**(e) in detail.**
1. Amend 02d INV-11 to the closed form above.
2. Rule a seal-coverage table: every row marked F:a and Chk:yes gets either a named `_structure` clause or a written "replay-owned" reason. Today INV-22, 23, 33/43, 36, 37, 41 and 50 are missing without any reason.
3. An AST test pins the mapping from rows to clauses.
4. The checker stays a **test-only** oracle, applied at `_seal`, not at the entry points.

## Q3. The fuzz that would have caught AUD-1

**Why the ten-operator fuzz missed it:**
1. The oracle sits behind replay (see Q1).
2. Each mutant gets exactly one operator (`:175-176`).
3. The operator alphabet cannot express the forgery. No operator creates a block. None revives a voided listing. `op4` adds one terminal entry per item, not per block.
4. `reseal` never refreshes the derived fields (text 6). The AUD-1 witness needed `refresh_derived`, i.e. the forger's best effort.

**Proposed generator:**
- **Alphabet:** the ten existing operators, plus
  - `clone_block`: copy a block under a new id and list it live;
  - `terminalise_live`: add terminal entries for every item of a live block, naming that block;
  - `revive_voided`: move a voided listing back to live;
  - `retarget_terminal`: change a terminal entry's `block_id`.
- **Composition:** every ordered pair exhaustively (14,018 mutants in about 17 s over 4 cases); triples by seeded sampling.
- **After composing:** `refresh_derived`, then `_seal(finalize=True)`. Discard only mutants the seal refuses.
- **Oracle 1:** the sealed mutant also passes verify-mode `_seal`, **and** checker static rows are non-empty ⇒ **fail**.
- **Oracle 2, independent of the checker:** the closed ownership property from Q2(b). A breach ⇒ fail, even if the checker is silent. This is what catches B1/B2.
- On failure, print the operator combination, seed and rows.
- **AUD-2:** keep checker crashes as a dedicated marker or field, and add a test that injects a checker exception.

## Q4. Fix round 3 plan

0. **Magistrate text (no code).** Write the 02d INV-11 closed-form amendment and the seal-coverage table (each row: seal or replay). Cold-gate the text only: one Fable seat plus one refuter who is handed B1/B2/AUD-1.
1. **Seat K (checker and oracle), first.**
   `WRITE_SCOPE: [tests/scored_roster_checker.py, tests/test_scored_roster_checker.py, tests/test_scored_packer_fuzz.py, tests/scored_case_generator.py]`
   - Implement the amended INV-11 in the checker.
   - Build the Q3 generator and both oracles; fix AUD-2.
   - Add fixed regressions: AUD-1, B1, B2 and the partly-terminal contrast.
   - Must be RED at `0fa4e6e3` on all four fixtures and on at least one composed escape.
2. **Seat P (packer), parallel to K after step 0, blind to K's diff.**
   `WRITE_SCOPE: [joulewise/scored_packer.py, tests/test_scored_packer.py]`
   - Add one `_ownership(registration, roster)` table built once. `_structure`'s ownership rows and `_live_index` / `_parent_facts` all read it.
   - Add the seal clauses the coverage table assigns to the seal.
   - Add the AST row-coverage test.
   - No per-row predicate may re-walk `blocks` or `terminal_refusals`.
3. **Gate before merge:**
   1. K's two-operator exhaustive run and three-operator sampled run on P's head: **zero** seal-accepts-while-checker-objects and **zero** closed-ownership breaches.
   2. K's suite RED at `0fa4e6e3` and GREEN at P's head.
   3. Full five-module suite green, with the timing re-measured against the audit's A6 figures.
   4. A fresh delta refuter, told only "forge two live owners past `_seal` using three composed edits".

   **Stop rule:** an escape on a row the table owns is a table-design defect, to be escalated, not patched.

**Scratch files and deviation.** All probes are under `/tmp/278ebc9e/esc2-opus/` (`seal_gap.py`, `cure_a.py`, `probe_b.py`, `closed_own.py`); nothing was written in the repo. One deviation from the session rules: the harness automatically moved the long `closed_own.py` run to the background when it hit its timeout. I waited for it to finish in the foreground, and it exited 0.
