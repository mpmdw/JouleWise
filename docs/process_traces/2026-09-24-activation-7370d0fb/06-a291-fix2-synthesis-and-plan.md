# 06 — A291 fix round 2: consult synthesis and proposed plan (magistrate, Opus 5.5)

Status: PROPOSED. A cold Fable gate rules on this plan (packet 07) before any code is written. The magistrate holds no ruling authority over contract text; every item marked CONTRACT below is a question for the gate.

## 1. Why this exists

A291 is the packer for scored nights. It decides which blocks of MATH problems go into which fixed-length power-capture windows ("envelopes"). It also re-plans ("requeues") when a block runs over its time budget. Delta re-audit 50 (a65fb4fa) found a BLOCKER in fix round 1 at `20cd29de` and a repeat of one defect class. That triggered the project's standing escalation rule: two rounds in a row failing with the same signature means the next spend is a design consult, not a third fix round. Two blind seats answered brief 01: Sol 6.0 high (report 02) and Opus 5.5 (report 03).

The signature: **a derived quantity misreads which placements or parents count.** A *placement* puts one block in one envelope. A placement is *live* when its block id is listed in that envelope's `blocks`. A *parent* is an original block; a *single* is a one-problem block split out of a parent after an overrun. The *planned lever* for a model at a level is the mean envelope index of that model's parents. The derived values compare it across the two models, so both models' problems sit at the same average position in the night.

## 2. What the seats agree on (bench-verified where marked)

1. **Root cause (both).** Each derived quantity reads a population, such as "live placements", "fully non-terminal parents" or "parents with a position". Those populations are consistent only when INV-11 (each model/problem pair has exactly one live-or-terminal owner) and INV-12 (a split parent's singles partition its problems) hold. Nothing establishes those invariants before the arithmetic runs:
   - `_seal` calls `_derived` before the digest check;
   - `_structure` never checks INV-11;
   - `_live` silently keeps the last of two live placements (`scored_packer.py:72-74`, bench-read);
   - the trusted-output cache (`_TRUSTED_OUTPUTS`) can skip replay altogether.
2. **Delete the trusted-output cache (C3, both ADOPT).** Measured cost without it, at the stress fixture's size (15 requeues): Sol 48 ms → 377 ms; Opus 45 ms → 347 ms. At 64 problems per level (the planned night, about 11 envelopes) the maximum is about 45 ms per requeue. The cost grows with the square of the event count (Opus: 2.8 s per call at 131 events, a fixture no planned night approaches). Recorded as a residual: re-measure before any registration plans more than about 60 envelopes.
3. **`_live` must refuse** a block that is live in two envelopes (typed `inv_11`), not pick one.
4. **One fact builder per parent, with named populations (C2 as amended by both).** A single population per lever is WRONG: it is exactly lens-37 B1. The ruled contract uses two populations per lever: a *gate* population (planned: fully non-terminal, RD-5; executed: fully counted, §4.1) and a *position* population (planned: any live problem, RD-4; executed: partly counted, §4.1, X-5). The cure is:
   - one builder yields per-parent facts `(n_items, n_terminal, indices)`;
   - the gate and position sets are named predicates over those facts;
   - the relation "gate ⊆ positioned" is checked, and a violation raises a typed refusal, before any division.
5. **An invariant table, narrowed (C1 as amended by both).** No shared executable table: a shared table would make the oracle agree with the packer's mistake. The packer and the checker share only row ids and code strings. A test asserts that every code the packer can raise is a §5 code and a key of the checker's `ROWS`, comparing strings only; neither module imports the other.
6. **A seed-driven stress generator (C4, both).** Each seed chooses sizes, counts, capacity, mode, cut-off positions and boundary durations (exactly at the bound, and the bound plus ε). Per-seed variation is asserted. Both seats note that legal histories always satisfy INV-11, so a legal-only stress run *cannot* detect this signature.

## 3. Where the seats differ, and the magistrate's proposal

- **D1. Is the checker still an independent oracle?** Sol: keep it; any change to what it treats as legal needs separate review. Opus: no. After renaming, 30 of the packer's 34 `_derived` lines appear verbatim in the checker. **Bench-verified by the magistrate:** `scored_packer.py:77-110` and `tests/scored_roster_checker.py:247-279` are the same code with renamed variables, including the same unguarded `sum(a)/len(a)`, so the checker would raise the same `ZeroDivisionError`. *Proposal:* adopt Opus.
  - A separate checker-role seat re-derives the checker's `_derived` and `check_executed` in an item-centric form: for each (model, problem), find the INV-11 owner, then group by parent.
  - That seat never reads `joulewise/scored_packer.py`.
  - The lens applies a normalised-similarity check to the rewritten code.
- **D2. Seal order (Opus only).** Today the seal runs identity → structure → derived → digest. *Proposal:*
  - new order: identity → digest match (verify mode) → structure plus the precondition rows → derived → `stale_derived`;
  - the precondition rows are INV-03, INV-11, INV-12, INV-17 and INV-52;
  - effect: a tampered roster that was not resealed refuses `inv_02` instead of crashing.
- **D3. Catch-all exception boundary.** Sol: one boundary that converts expected malformed-data exceptions. Opus: only a backstop; totality must come from the precondition checks. *Proposal (Opus):*
  - add `ArithmeticError` to the seal's conversion tuple, mapped to `inv_52` with detail `internal:<type>`;
  - tests assert that this detail NEVER appears on the legal corpus or on the mutation corpus.
- **D4. Mutation-fuzz differential test (Opus only).** *Proposal: adopt.* It is the only test that can reach the signature. It uses seeded operators, each submitted both resealed and not resealed:
  - live→voided;
  - duplicate a live placement;
  - drop or add a terminal refusal;
  - delete a single;
  - flip `superseded`;
  - move a placement's `envelope_index`;
  - flip `late`.

  The properties it checks:
  - `requeue_overrun` returns or raises `PackingRefusal`, never any other exception;
  - if the checker flags a roster, the packer refuses it;
  - every operator is refused at least once;
  - the refusal-code census includes `inv_11`, `inv_12`, `inv_38`/`inv_39` and `inv_02`.
- **D5. Should `_seal(finalize=True)` stay callable by callers?** Once the cache is gone, sealing confers no trust, and a resealed forgery fails replay at the next entry. *Proposal: keep it callable* (contract INV-40 and FT-8 name it). A private capability token would be protection against the operator, which D-161 prunes.
- **D6. The executed lever's position population (Sol F2).** The current production test at `tests/test_scored_packer.py:268` includes a partly counted parent's position; §4.1 defines "counted parent" using every problem. *Proposal:* the gate states the population table below as a dated addendum that restates X-5. It does not reopen X-5.

## 4. Proposed population table (CONTRACT — for the gate to rule)

| Quantity | Gate population (null if empty for either model) | Position population |
|---|---|---|
| planned lever (§1.2, §3.4) | parents with zero terminal problems (RD-5, FT-10) | parents with ≥ 1 live, non-terminal problem; position = mean live envelope index over those problems (RD-4) |
| planned spread shortfall | count = parents with zero terminal problems, vs `MIN_PARENT_BLOCKS`; occupied envelopes = distinct live envelope indices of those parents whose every problem is live, vs `MIN_ENVELOPES` (as the code at `20cd29de` computes it; the gate confirms or corrects) | — |
| executed lever (§4.1) | parents whose every problem is counted | parents with ≥ 1 counted problem; position = mean envelope index of counted problems (X-5) |
| executed spread | parents whose every problem is counted | — |

Rule proposed: every gate-population member must also be a position-population member. The builder checks this, and a violation refuses (`inv_11`) rather than dividing.

## 5. Proposed plan (two seats, one round each)

**Seat P, the packer role (Sol 6.0 high), in the A291 worktree on `feat/2026-09-24-a291-packer-recut` from `20cd29de`.** WRITE_SCOPE: `joulewise/scored_packer.py`, `tests/test_scored_packer.py`, `tests/test_scored_packer_stress.py`. Each regression below names the counterfactual input and the production call site it drives; forgeries are resealed on the test side using the checker's `canon`/`preimage`, never the packer's `_seal`.

1. `_live` → `_live_index`: refuses duplicate live placements with `inv_11`.
   - R1: a block live in envelopes 0 and 12, resealed test-side → `requeue_overrun` entry raises `inv_11` (not `inv_39`). The same roster → `verify_executed_roster` raises `inv_11`.
2. Precondition rows in `_structure`, run before `_derived`: INV-11 (a)/(b) exactly as 02d:467-469, and the INV-12 partition.
   - R2: level-1 large blocks moved from live to voided, no terminal refusals added, resealed test-side → `requeue_overrun` raises `inv_11`.
   - R2b: a split parent with one single deleted → `inv_12`.
3. Seal order as in D2.
   - R3: the R2 roster NOT resealed → `requeue_overrun` raises `inv_02` (today it raises `ZeroDivisionError`).
4. `_parent_facts` + `_lever` per §4; `_derived` and `executed_status` are rewritten on them.
   - R4a: lens-37 R2 value `6.199999999999999` and the omitted-window value `1.5999999999999996`, checked against hand arithmetic.
   - R4b: `_parent_facts` patched to yield a gate record with empty indices → `PackingRefusal`, never `ZeroDivisionError`.
   - R4c: AST test that only `_parent_facts` iterates `roster["blocks"]` for positions.
5. Delete `_TRUSTED_OUTPUTS`. Requeue entry always replays; `_REPLAYING` remains only as replay's own recursion guard.
   - R5a: record 50's in-place `late` flip, `sha256=None`, resealed through `_seal(finalize=True)` → `requeue_overrun` raises `inv_38`/`inv_39`.
   - R5b: AST test that the module holds no module-level container of rosters or digests.
6. Backstop per D3, with the stress run asserting zero `internal:` refusals and zero refusals of legal rosters.

**Seat K, the checker role (Opus 5.5 preferred, a different model family from P), in its own worktree from `20cd29de`.** WRITE_SCOPE: `tests/scored_roster_checker.py`, `tests/test_scored_roster_checker.py`, and new `tests/test_scored_packer_fuzz.py`.

7. Item-centric re-derivation of the checker's `_derived` and `check_executed` per §4. Seat K does not read `joulewise/scored_packer.py`; its brief gives it only the packer's public interface (02d §3, §6).
8. The seed-driven generator (C4) with the per-seed variation assertion (≥ 60% of cases differ between two seeds), and the mutation-fuzz differential test (D4).

**Integration.** Cherry-pick K onto P's head; run the four named modules plus the fuzz module. A disagreement between packer and checker is a finding for the magistrate, never something the seats resolve. Then a delta re-audit, then stages I2 and I3 as before, the cold delta gate and the cold Fable final pass.

## 6. Residual risks

- A precondition check stricter than the contract would refuse legal rosters. Caught by the no-cache stress run: every legal roster is sealed at every call, and zero refusals are expected.
- Population drift inside the fact record would re-create lens-37 B1. Caught by R4a on a partly terminal parent.
- The oracle converging again. Caught by the similarity check and by interface-only briefs.
- A weak fuzz (the property holds vacuously). Caught by the per-operator refusal census.
- The replay cost's quadratic growth, as in §2 item 2.
