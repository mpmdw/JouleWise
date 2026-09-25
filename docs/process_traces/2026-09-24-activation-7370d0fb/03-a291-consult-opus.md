```json
{
  "schema": "claude-codex-report/v1",
  "genre": "triage",
  "status": "findings",
  "completion": "complete",
  "summary": "The signature is real and structural. Every derived population (live placement, non-terminal parent, positioned parent) is only well defined under INV-11/INV-12, but the packer computes derived values before, or instead of, establishing those invariants. The oracle's derived code is a transcription of the packer's (30 of 34 lines match after renaming), so one misreading lands in both. Plan: enforce the presupposition rows in the seal before any derived computation, check the digest first, build one per-parent fact record with two named nested populations, delete the trust cache (affordable: under 50 ms per call at real night sizes), add a mutation-fuzz differential test, and seed-drive the generator.",
  "workspace": {
    "base_requested": "20cd29de",
    "base_mode": "exact",
    "head_start": "20cd29de",
    "head_end": "20cd29de",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "q1_signature": "STRUCTURAL",
    "C1": "ADOPT WITH CHANGES (presupposition rows only; row ids and codes shared, never code)",
    "C2": "ADOPT WITH CHANGES (one fact record, two named nested populations; a literal single population re-installs lens-37 B1)",
    "C3": "ADOPT (delete the cache; finalize may stay callable because sealing no longer confers trust)",
    "C4": "ADOPT WITH CHANGES (plus a mutation-fuzz differential test: legal-only generators cannot see this class)",
    "new_cures": ["seal checks the digest before derived", "_live refuses duplicates (inv_11)", "arithmetic backstop at the seal boundary, asserted never to fire", "checker derived values re-derived item-centrically by a separate seat"]
  },
  "verification": [
    {"id": "P-Q3", "kind": "probe", "cmd": "python3 -B /tmp/7370d0fb/probe/q3_cost.py", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["n=11 size=2 events=15 cached 0.045s nocache 0.347s max 43.5ms", "n=64 size=2 events=131 cached 2.871s nocache 174.557s max 2807.3ms"]}, "expected": {"exit_code": 0, "tail_regex": "nocache"}},
    {"id": "P-Q4", "kind": "probe", "cmd": "python3 -B /tmp/7370d0fb/probe/q4_defects.py", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["P1 requeue_overrun: ZeroDivisionError (cache empty)", "P2 requeue_overrun ACCEPTED forged roster", "P2 _live picks envelope 12 ... live in [0, 12]", "P3 requeue w/o cache refused: inv_39"]}, "expected": {"exit_code": 0, "tail_regex": "ZeroDivisionError"}},
    {"id": "P-S2", "kind": "probe", "cmd": "inline: run_case(i) for i<40 under both seeds", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["cases with identical (edge counts, calls) across the two seeds: 38/40"]}, "expected": {"exit_code": 0, "tail_regex": "identical"}}
  ],
  "flags": [
    "The brief names joulewise/scored_roster_checker.py; the checker is actually at tests/scored_roster_checker.py.",
    "Records 37, 44, 45, 46 and 50 are untracked and missing from this worktree. Record 50 was read read-only from the canonical checkout; nothing was imported or executed from there."
  ]
}
```

# 03 — A291 design consult (Opus seat, blind)

All probes live under `/tmp/7370d0fb/probe/` and ran at `20cd29de`. Line numbers refer to that commit.

## Q1 — Is the signature real? Yes, and it is structural.

**Root cause.** Each derived quantity is defined over a population of placements or parents: "live placement", "non-terminal parent" (RD-5, 02d:63), "parent with a planned position" (RD-4, 02d:354), "counted parent" (§4.1). Those populations are well defined, and nest inside one another (every gate parent also has a position), **only when INV-11 and INV-12 hold**. INV-11 says each (model, item) has exactly one live-or-terminal owner (02d:465-469); INV-12 says the singles of a split parent partition its items.

Nothing in the design states that dependency, and every layer breaks it in its own way:

- **The seal computes derived values before legality is established.** `_seal` calls `_derived` at `scored_packer.py:204`. That runs before the digest check (`:224-228`) and before replay (`requeue_overrun:332` precedes `:334`). The cache at `:333` can skip replay altogether.
- **`_structure` never checks INV-11.** See `:113-191`.
- **`_live` resolves ambiguity silently.** The dict comprehension at `:72-74` keeps whichever placement comes last.
- **The contract installs two populations per lever and leaves their relation implicit.** The gate is "zero non-terminal/counted parents"; the positions include partly terminal or partly counted parents (02d:774, X-5, "installs both texts literally").
- **The oracle is not independent at the derived layer.** After renaming variables, 30 of the packer's 34 `_derived` lines appear verbatim in the checker's `_derived` (`scored_roster_checker.py:247-280`). The only differences are inlining. The same was true at birth: `b8962fd0` and `ef1c5e48` share the identical wrong `len(indices) == len(items)` population.

So a misreading in one is a misreading in both (instance a). On legal histories the populations coincide, so no legal-only stress run can tell them apart (instance e, measured below). Instances (b), (c) and (d) are the same missing presupposition, reached by three routes: a voided placement read as live, a gate/position mismatch, and a cache hit.

**Probe P1 (S1).** Level-1 `large` blocks were moved from live to voided, the roster was not resealed, and `_TRUSTED_OUTPUTS` was empty:
```
P1 _derived: ZeroDivisionError: division by zero
P1 requeue_overrun: ZeroDivisionError: division by zero
P1 checker: [('INV-02','inv_02'), ('INV-11','inv_11'), ...]
```
This goes further than record 50. S1 needs neither the cache nor a reseal: the digest check never gets a chance, because `_derived` crashes first.

**Probe P2/P3 (B1 and `_live`).** One block was made live in envelope 0 and in a new envelope 12, then sealed through the private `_seal(finalize=True)`:
```
P2 _seal(finalize) accepted forged roster; cache size 1
P2 _live picks envelope 12 for large:decode:1:0 live in [0, 12]
P2 requeue_overrun ACCEPTED forged roster, events 1
P2 checker: ['INV-11', 'INV-36']
P2 verify_executed_roster refused: inv_39
P3 requeue w/o cache refused: inv_39
```
Severity context: the claim path cannot be fooled today. `verify_executed_roster` (`:411-413`) never consults the cache. B1 corrupts night planning, not evidence. It is still worth curing, because a corrupted plan wastes a night.

## Q2 — The four candidates

**C1 (one invariant table): ADOPT WITH CHANGES.**
- The §5 table already exists (02d §5.3), and so does the checker's row map (`scored_roster_checker.py:26-70`).
- Making the seal evaluate every §5 row would create a *third* implementation of the transition rules (INV-30 to INV-38). The packer's proof of legality is replay, and it should stay replay.
- Narrow C1 to the **presupposition set**: the static rows that the derived code and `_live` rely on. These are INV-03 (already present at `:149`), INV-11, INV-12, INV-17 (present at `:145`) and INV-52.
- The seal evaluates this set before `_derived`.
- **How the oracle stays independent:** share only row ids and code strings, never code. Add a test that the set of codes `scored_packer` can raise is a subset of the §5 codes and of the checker's `ROWS` keys. It compares strings only; neither module imports the other.

**C2 (one population per derived quantity): ADOPT WITH CHANGES. As worded it is wrong.**
- The ruled text deliberately uses two populations per lever: the gate (FT-10 with RD-5, fully non-terminal; §4.1, fully counted) and the positions (RD-4, any live item; §4.1, partly counted).
- A single population is exactly the original defect, lens-37 B1.
- Cure: one fact builder per parent, `_parent_facts(registration, roster, counted=None)`. It returns, for each parent, `(n_items, n_terminal, indices)` and is the only loop over `roster["blocks"]`.
- Populations become named predicates over that record:
  - `gate = n_terminal == 0` (planned) or `len(indices) == n_items` (executed);
  - `positioned = bool(indices)`.
- One `_lever(facts)` returns `None` iff the gate count is 0. It raises a typed `inv_11` refusal if any gate record lacks full `indices`, so gate ⊆ positioned is checked, not assumed.
- Both `_derived` (`:77-110`) and `executed_status` (`:425-452`, today a second copy) call it.
- The magistrate should put this population table into the brief as a dated contract addendum. It restates X-5; it does not reopen it.

**C3 (no trusted-output cache): ADOPT; delete the cache.** The costs are in Q3.
- Once the cache is gone, sealing confers no trust. `_seal(..., finalize=True)` can then stay callable with its contract-literal signature (INV-40, FT-8's "sole caller of `_digest`"). A resealed forgery simply fails at the next entry, as P3 shows.
- Line 333 becomes `if not _REPLAYING.get(): _replay_roster(...)`.
- A secondary win: every requeue call in tests and production now takes the same path. The eight-entry eviction today makes replay coverage depend on call order.

**C4 (seed-driven generator): ADOPT WITH CHANGES.**
- Measured: 38 of 40 cases give identical `(edge counts, calls)` under the two seeds. Size, cap and mode come from `i` (`test_scored_packer_stress.py:70-72, 82`).
- The seed should choose size, n, cap, pred, mode, the cut-off position, and boundary `elapsed_s` values (exactly `Bound`, and `Bound` + ε). Assert that at least 60% of cases differ between the seeds.
- **This alone cannot catch the signature**, because legal histories satisfy INV-11. It needs a partner: the mutation-fuzz differential test (plan step 7).

## Q3 — What dropping the cache costs (measured)

The probe times `requeue_overrun` at every report, once as-is and once with `_TRUSTED_OUTPUTS.clear()` before each call:
```
n= 11 size=2 cap=8.0 mode=0 events= 15 envs= 15 placements=  69 | cached total=0.045s max=3.6ms | nocache total=0.347s max=43.5ms ratio=7.8x
n=  6 size=1 cap=4.0 mode=0 events= 15 envs= 15 placements=  67 | cached total=0.041s max=3.3ms | nocache total=0.323s max=40.8ms ratio=7.8x
n= 64 size=4 cap=8.0 mode=0 events= 67 envs= 67 placements= 172 | cached total=0.730s max=13.5ms | nocache total=23.362s max=729.1ms ratio=32.0x
n= 64 size=2 cap=4.0 mode=0 events=131 envs=131 placements= 328 | cached total=2.871s max=27.0ms | nocache total=174.557s max=2807.3ms ratio=60.8x
```
(Mode 5 rows are within 3% of mode 0 and are omitted.)

- **Real nights:** the headline plan is "64 per level ≈ 11 envelopes" (`09-headline-packet-b-scored-night.md:113`). That is inside the first row's regime: at most about 45 ms per requeue. **Affordable.**
- **Growth:** the cost is O(E²) per night. It reaches 2.8 s per call only at 131 events, a fixture with a tiny cap that no planned night approaches. If a future registration plans more than about 60 envelopes, the extra CPU work between envelopes needs a look (it is a quiet-machine concern). That is NOT EXECUTED here; the orchestration timing was not examined.
- **Test suite:** the stress run adds roughly 0.3 s × 600 registrations, about 3 minutes, to a 183 s suite (record 50, V1). That is an estimate from the first row, not a measured suite run.

## Q4 — Cures the candidates miss

1. **Seal order.** Today the order is identity → structure → derived → digest (`:196-228`). It should be identity → **digest match (verify mode)** → structure + presupposition rows → derived → `stale_derived`. A tampered but unresealed roster then refuses `inv_02` instead of crashing (P1).
2. **`_live` must refuse.** Replace it with `_live_index`, which raises `PackingRefusal("inv_11")` when a block id is in two envelopes' `blocks`. A last-wins dict is how instances (b) and (d) arise.
3. **One exception boundary: yes, but only as a backstop.**
   - Add `ArithmeticError` to the tuple at `:208`, mapped to `inv_52` with detail `internal:<type>`.
   - Tests assert this detail **never** appears on either the legal corpus or the mutation corpus.
   - Otherwise the backstop would dress genuine packer bugs up as "malformed input". Totality should come from steps 1–2, not from catching exceptions.
4. **Should `_seal(finalize=True)` stay callable?** Yes, once the cache is gone (C3). A private capability token would be anti-operator engineering of the kind D-161 prunes.
5. **The checker needs re-derivation, not patching.**
   - A separate seat (the checker role) rewrites the checker's `_derived` and `check_executed` in an **item-centric** form, without reading `joulewise/scored_packer.py`. For each (model, item) it finds the INV-11 owner, then groups by the parent id parsed from the block id.
   - A normalized-similarity gate goes into the lens: rename variables, count shared lines, and require few. The probe method is in Q1 (30 of 34 lines today).

## Q5 — The fix-round-2 plan

**Roles.**
- **Packer seat P (one Sol seat, one round):** steps 1–6 and the packer-side regressions.
- **Checker seat K (separate author, different model family preferred):** step 7's differential harness and the item-centric re-derivation (Q4.5). K may run in parallel. P's regressions assert typed codes on named inputs and do not depend on K.
- If only one seat is funded: P goes first, K is queued, and the loss of oracle independence is recorded as a residual.

Every regression names its counterfactual input and the production call site it drives. Forgeries are resealed on the **test side**, using the checker's own `canon`/`preimage` (`scored_roster_checker.py:94-113`), never the packer's `_seal`.

1. **`_live_index` (`scored_packer.py:72`).** It refuses duplicates with `inv_11`.
   - *R1:* the P2 roster (block live in envelopes 0 and 12), resealed test-side, through `requeue_overrun` (entry `_seal`, `:332`) → `inv_11`, raised **before** replay: assert the code is `inv_11`, not `inv_39`.
   - Same roster through `verify_executed_roster` (`:412`) → `inv_11`.
2. **Presupposition rows in `_structure`, before `_derived`:** INV-11 predicates (a)/(b) exactly as at 02d:467-469, and the INV-12 partition.
   - *R2:* the P1 roster (level-1 large blocks moved from live to voided, no terminal refusals), resealed test-side, through `requeue_overrun` → `inv_11`.
   - Also a split parent whose single was deleted → `inv_12`.
3. **Reorder `_seal` (`:194-229`)** as in Q4.1.
   - *R3:* the P1 roster **not** resealed, through `requeue_overrun` → `inv_02` (today: ZeroDivisionError).
4. **`_parent_facts` + `_lever`**, with `_derived` and `executed_status` rewritten on top of them (C2).
   - *R4a:* the lens-37 R2 value `6.199999999999999` and the omitted-window value `1.5999999999999996` are unchanged, compared against hand arithmetic, not only against the checker.
   - *R4b:* exit injection. Patch `_parent_facts` to return one gate record with empty `indices`; `_derived` via `requeue_overrun` raises `PackingRefusal`, never `ZeroDivisionError`.
   - *R4c:* AST test. Only `_parent_facts` iterates `roster["blocks"]` for positions, and `executed_status` contains no division.
5. **Delete `_TRUSTED_OUTPUTS`** and change `:333` (C3).
   - *R5a:* record 50's first forgery (in-place `late` flip, `sha256=None`, reseal through `_seal(finalize=True)`), through `requeue_overrun` → `inv_39` or `inv_38`. This forgery passes the presupposition rows, so only replay catches it.
   - *R5b:* grep/AST test that `scored_packer` holds no module-level container of rosters or digests.
6. **Backstop (Q4.3)**, with the stress run asserting zero `internal:` refusals and zero refusals of legal rosters.
7. **Tests (K):**
   - (i) **Seed-driven generator (C4)** with the per-seed variation assertion.
   - (ii) **Mutation-fuzz differential test.** Take legal rosters from (i). Apply at least 8 seeded operators: live→voided, duplicate a live placement, drop or add a terminal refusal, delete a single, flip `superseded`, move a placement's `envelope_index`, flip `late`. Submit each variant twice, resealed and not resealed.
     - Property: `requeue_overrun(M)` either returns or raises `PackingRefusal`, and never raises anything else.
     - If `check_roster(M)` is non-empty, it must raise. "Packer accepts ⇒ checker accepts."
     - Every operator reports at least one refusal, so no operator is silently a no-op.

## Q6 — Risks, and what catches each

- **The seal's INV-11 is a third implementation.** If it is stricter than the contract, it refuses legal rosters. *Caught by* the step-6 assertion: the no-cache stress run seals every legal roster at every call and must see zero refusals.
- **Population drift inside the fact record** (for example, the gate written as "placed" rather than "non-terminal"). This re-creates lens-37 B1. *Caught by* R4a's hand-arithmetic values on a partly terminal parent, and by R4b.
- **The backstop masks bugs.** *Caught by* the never-fires assertion over both corpora.
- **The oracle converges again**, if K reads the packer or P reads the checker's internals. *Caught by* the normalized-similarity gate in the lens, and by briefs that give each seat only the other module's interface.
- **Weak fuzz.** Operators may produce only trivially refused inputs, so the property holds vacuously. *Caught by* the per-operator refusal-code census, which must include `inv_11`, `inv_12`, `inv_38`/`inv_39` and `inv_02`.
- **Replay cost at larger nights** (the O(E²) numbers in Q3). Not a correctness risk. Record it as a residual: re-measure before any registration plans more than about 60 envelopes.
