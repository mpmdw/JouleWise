# A292-REDUCER-DESIGN-01: Opus 5.5 seat answer

Base is `23289fc5`, which contains main `75d04e9e`. Every clause the scout quotes was checked against its source, and all match. I ran probes against the merged packer (scratch copies in `/tmp/152c9255/rd-opus/probe{1,2}.py`). The probes are named P1–P5 and cited below.

**Three things the scout's map leaves out, each binding on A292:**
1. **INV-13 was moved to A292.** «`retry_stage` is on every item row and flows into cells» (`docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md:13`). Contract v4.1 hands it to A292 at `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md:491`. Tier: **MATERIAL**.
2. **AP-5M v4 has reducer rules the merged code cannot carry yet.** The v4 plan itself, not v5, contains:
   - `below_floor`, which needs `floor_gate_j`;
   - the counted-attempt rule K24;
   - `night_exhausted`;
   - per-night levers.
   Sources: `docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:196,266,801,810`. `floor_gate_j` is not in `REGISTRATION_KEYS` (`joulewise/scored_registration.py:28`). K25 says `_seal` refuses `night_exhausted` until the code lane ratifies it (`07d…:810,1324-1325`). Tier: **MATERIAL**.
3. **The R6-1 gate rule is relevant to the reducer.** It would let a "reducer specification" record envelope index as a covariate. It is proposed and not yet ratified (`docs/process_traces/2026-09-24-activation-278ebc9e/112-coldgate-packet-a291-premerge/20-coldgate-fable-premerge-ruling.md:114`; `…/117-coldgate-packet-a291-finalpass/20-coldgate-fable-finalpass-ruling.md:63`).

---

## R1: Schemas and refusal vocabulary

**Tier: BLOCKER.** "Both digests" is ambiguous about *which* roster digest a row or window carries. There are three candidates:
- **The final `sha256`.** The runner cannot know it at capture time. If the runner stamps it afterwards, the binding proves nothing.
- **The root `registered_sha256`.** The runner can stamp it, but it is weak: every window in the night carries the same value.
- **The in-force digest**, meaning the digest of the roster the runner had loaded when it started that envelope. It can be stamped at capture time, and it is also the only evidence that runner obligation FT-9 was honoured (`docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:74`).

I rule the in-force digest. It is computable: events have strictly increasing `envelope_index` (`joulewise/scored_packer.py:227,395`), and each placement is created by an earlier event (`:257`).

**Tier: MATERIAL.**
- **Derive, don't copy.** Rows carry no `model`, `level`, `arm`, `retry_stage`, `parent_block_id` or cap flag. The stopped draft carried copies (`c0998fdb:joulewise/scored_reduce.py:16-18`). Every copy adds a way to disagree and adds nothing a key lookup does not already give.
- **INV-13 is met on the output side.** Each output item record carries `retry_stage`, taken from the counted placement's `stage` (`joulewise/scored_packer.py:322`), and each cell carries `retry_stage_counts`. This follows the derive-not-copy principle of 45/10 §Q1. The magistrate should confirm this reading of 08 F2(b).
- **Rows carry the raw scorer verdict `scorer_match`, never `correct`.** Correctness is derived under the v4 labelling. This keeps the cap rule in one function (see R3).

**Tier: MATERIAL. Refusals use a separate namespace, `ReductionRefusal`.** Two reasons:
- A291's `reduce`-column witnesses must see the same `PackingRefusal` codes when re-run at the real entry. That happens only if the verifier's refusal passes through unwrapped.
- Row and window defects are not roster invariants, so they must not borrow `inv_*` codes.

> **Executable text R1.**
> `joulewise/scored_reduce.py` exports `reduce(registration, roster, predicted_decode_s, score_rows, capture_windows) -> dict`: five positional parameters, no defaults, no `*args`/`**kwargs`. Its first statement is `verify_executed_roster(registration, roster, predicted_decode_s)` (AST-asserted). Any `PackingRefusal` it raises, or that `executed_status` raises, propagates unchanged.
>
> *Definitions.*
> - **Placement key:** `(p["block_id"], p["attempt"])` for `p` in `roster["placements"]`. Keys are unique (see the probes below).
> - **Live:** a key is live iff `p["block_id"] in roster["envelopes"][p["envelope_index"]]["blocks"]`.
> - **Observation of a key:** the entry of `envelopes[p.envelope_index]["observations"]` whose `block_id` equals `p.block_id`.
> - **`in_force(ix)`:** `roster["registered_sha256"]`, replaced in turn by `events[k]["sha256"]` for every `k` with `events[k]["envelope_index"] < ix`.
>
> *Score row.* `SCORE_ROW_SCHEMA = "joulewise.scored_row.v1"`. Exact key set:
> - `schema` (== the constant);
> - `registration_sha256` and `roster_sha256` (64 lower-case hex characters);
> - `scorer_id` (non-empty str);
> - `block_id` (str);
> - `attempt` (`type is int`, ≥ 0);
> - `item_id` (str);
> - `generated_tokens` (`type is int`, ≥ 0);
> - `stop_reason` (`"stop"` or `"length"`);
> - `extracted_answer` (str or None);
> - `scorer_match` (bool).
>
> Coherence rule: `scorer_match` is true ⇒ `extracted_answer is not None`.
>
> *Capture window.* `WINDOW_SCHEMA = "joulewise.scored_window.v1"`. Exact key set:
> - `schema`;
> - `registration_sha256` and `roster_sha256` (hex as above);
> - `block_id` (str);
> - `attempt` (int ≥ 0);
> - `envelope_index` (int);
> - `gross_j` (finite int or float > 0);
> - `bundle_sha256` (64 hex: the strict-valid raw bundle the J came from; carried to the output, not verified here).
>
> *Binding.* For both records:
> - `registration_sha256 == registration.digest`;
> - `roster_sha256 == in_force(placement.envelope_index)`.
>
> Rows only: `scorer_id == registration.scorer_id`.
>
> *Refusal class.* `class ReductionRefusal(ValueError)`, with `.code`. `REDUCTION_CODES` is exactly: `reduce_input`, `row_keys`, `row_domain`, `row_scorer`, `row_unknown`, `row_binding`, `row_duplicate`, `row_unstarted`, `row_missing`, `tokens_over_cap`, `cap_disagreement`, `window_keys`, `window_domain`, `window_unknown`, `window_binding`, `window_duplicate`, `window_envelope`, `window_unstarted`, `internal_disagreement`. A test asserts this set is disjoint from every code literal in `scored_packer.py` and `scored_registration.py`.
>
> *Check order* (the first failure wins):
> 1. The verifier.
> 2. `score_rows` and `capture_windows` are lists (`reduce_input`).
> 3. Each window, in list order: keys → domain → unknown (not a placement key) → binding → duplicate key → `envelope_index` ≠ the placement's (`window_envelope`) → observation `not_started` (`window_unstarted`).
> 4. Each row: keys → domain → scorer → unknown (key not a placement, or `item_id` not in that block's `items`) → binding → duplicate `(block_id, attempt, item_id)` → observation `not_started` (`row_unstarted`) → `generated_tokens > cap_tokens[arm]` (`tokens_over_cap`) → cap disagreement (R3).
> 5. Completeness (R2, `row_missing`).
> 6. `executed_status`.
> 7. The internal cross-check (R4).
>
> *Output.* `REDUCTION_SCHEMA = "joulewise.scored_reduction.v1"`. Keys:
> - `schema`, `registration_sha256`, `roster_sha256` (= `roster["sha256"]`), `registered_sha256`, `claim_ready`, `scorer_id`.
> - `items`: one record per (model in role order, item in registered level/item order). Keys: `model`, `level`, `item_id`, `parent_block_id` (the root parent), `outcome` ∈ {`counted`, `window_missing`, `ceiling_violation`, `unattributed_overrun`}, `block_id`, `attempt`, `envelope_index`, `retry_stage`, `generated_tokens`, `stop_reason`, `capped`, `malformed`, `scorer_match`, `correct`, `extracted_answer`, `terminal_gross_j`. Fields are null where they do not apply.
> - `parents`: one record per root parent, in `roster["blocks"]` order. Keys: `parent_block_id`, `model`, `level`, `n_items`, `counted_item_ids`, `windows` (each `[{block_id, attempt, envelope_index, gross_j, bundle_sha256, item_ids}]`), `g_j` (sum of the counted windows), `k` (count of counted windows), `fully_counted`.
> - `cells`: keyed `"{model_id}:{level}"`, the ten keys of FT-7. Keys: `n_items`, `n_counted`, `n_correct`, `n_capped`, `n_malformed`, `generated_tokens`, `gross_j`, `uncounted` (`{window_missing, ceiling_violation, unattributed_overrun}` counts), `retry_stage_counts`, `cap_bound`, `spread_exceeded`, `fully_counted_parents`, `distinct_envelopes`, `mean_envelope_index`.
> - `levels`: keyed `"1"`…`"5"`, each `{executed_drift_lever_slots, drift_exceeded, max_gap}`.
> - `uncounted_windows`: each `{block_id, attempt, envelope_index, gross_j, bundle_sha256, reason ∈ {voided, terminal}}`.
> - `superseded_rows`: rows whose key is not live, verbatim.
> - `sha256`: canonical-JSON SHA-256 of everything else.
>
> The reducer computes no ratios. Those belong to A293.

Probe results:
- **P1:** 57 placements, 57 unique keys.
- **P2:** the terminal's `(block_id, attempt)` equals the last *voided* placement (`large:…:single:0`, attempt 3, envelope 13). This matches `joulewise/scored_packer.py:449` and INV-37 at `89…:623`.

## R2: Window completeness

**Tier: MATERIAL.** I reject the draft's "all active windows required" rule (`c0998fdb:joulewise/scored_reduce.py:76-78`). Four parts of the ruled text assume that some live windows will be missing:
- `executed_status` takes the reducer-supplied `captured_window_keys` as an input (`joulewise/scored_packer.py:498-501`; `89…:379,387`). That input would do nothing if every live window were mandatory.
- `spread_exceeded` is cause-agnostic: «for any reason after capture» (`…/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:58`).
- FT-10 has a rule for "zero counted parents" (`…/20-addendum/21…:76`).

Refusing the whole reduction over one lost capture also throws away a night of good cells when the one cure, a recapture, already exists.

The asymmetry is deliberate:
- **Rows are re-derivable.** The scorer can be re-run over stored generations, so a missing row refuses.
- **Windows are physical evidence.** Energy that was never captured cannot be re-derived, so a missing window becomes a typed outcome.

**Tier: MATERIAL, and it belongs to another lane.** AP-5M v4's list of NR reasons omits `window_missing` (`07d…:196,284,286`). HEADLINE-AP5M-AMENDMENT-01 must add it. Otherwise a missing window would be the only silent drop.

| Attempt class (from the key's observation) | Window | Rows | Missing-window outcome |
|---|---|---|---|
| live (`keep`) | expected | **required** for every item (`row_missing`) | items get `window_missing`; not counted; no refusal |
| voided, `completed` (culprit single, INV Q6) | optional → `uncounted_windows` (`voided`) | optional → `superseded_rows` | nothing |
| voided, `cut_off` (advance, split, reschedule) | optional → `uncounted_windows` | optional | nothing |
| terminal `ceiling_violation` / `unattributed_overrun`, attempt started | optional → `terminal_gross_j` and `uncounted_windows` (`terminal`) | optional | `terminal_gross_j: null` |
| any key whose observation is `not_started` | **refused** (`window_unstarted`) | **refused** (`row_unstarted`) | n/a |
| `idle_slot` or non-placement key | **refused** (`window_unknown`) | **refused** (`row_unknown`) | n/a |

> **Executable text R2.**
> - For each registered (model, item): if it is in `terminal_refusals`, `outcome` = its `type`, and `terminal_gross_j` = the `gross_j` of the window keyed `(terminal.block_id, terminal.attempt)` if supplied, else null.
> - Otherwise let `p` be the live placement holding the item. `outcome = "counted"` iff a window for `p`'s key is supplied; otherwise `"window_missing"`.
> - Every item of every live placement has exactly one row, else `row_missing`.
> - Voided and terminal windows never enter `g_j`, `gross_j` or any position, by rule.
> - `executed_status` receives `counted_keys` = {the live keys with a supplied window}, never the full supplied set. This keeps future window exclusions consistent.
> - A missing `ceiling_violation` window never refuses. Its J is disclosure-only (K17, `07d…:746`).

P1 confirms that supplying voided keys leaves `executed_status` unchanged. P3 shows dropping one live key flips spread to true at the minimum of five parents (n=10, block size 2).

## R3: Cap policy

**Tier: BLOCKER, against parameterizing.** v5 cells are keyed (model, level, **budget**). v5 also has an answer allowance `A` and separates thinking-cap hits from answer-allowance hits (`52-ap5m-v5-draft/01-ap5m-draft-v5.md:10,41`). None of these exist in Registration v2 (`scored_registration.py:28`). A parameter today would be designed against unruled text (`v5:53`: «A291 contract v5 is OPEN»). That is exactly the silent hybrid the question forbids.

**Waiting for v5 also loses.** v5 keeps the scheduler safeguards (`v5:53`). Everything in A292 except the ~15-line labelling function therefore carries over, and v5 adoption waits on a contract that is not scheduled.

**Decision:** implement v4 now as the only semantics, with the labelling isolated in one function.

> **Executable text R3.**
> - `_label(registration, row)` is the single site of cap semantics:
>   - `cap = registration.cap_tokens[registration.arm]`;
>   - `capped = row["generated_tokens"] >= cap`;
>   - refuse `cap_disagreement` unless `(row["stop_reason"] == "length") == capped`;
>   - `malformed = row["extracted_answer"] is None`;
>   - `correct = row["scorer_match"] and not capped`.
> - `generated_tokens > cap` is refused (`tokens_over_cap`). Reason: the registered worst case `cap × s_per_token_upper + prefill` (`scored_registration.py:99-102`) assumes it cannot happen, so such a row falsifies a registered physical bound.
> - No argument, flag, environment variable or registration field selects the semantics. v5 is `REDUCTION_SCHEMA` v2 under a new registration schema, built in the contract-v5 lane.
> - **Cap-bound label.** `CAP_BOUND_FRACTION` is imported by name from `scored_registration`. `cap_bound = n_capped / n_counted > CAP_BOUND_FRACTION` over the cell's counted items, and `null` when `n_counted == 0`. Division is used, not multiplication: `k/n` rounds to the literal 0.2 exactly at equality.
> - **Mandatory CONSUMED witness** (15/10 Q1, `…/15-coldgate-packet-a291-contract/10-coldgate-fable-ruling.md:17`):
>   - cells with 2 capped of 10 give false, and 3 of 10 give true;
>   - patching `joulewise.scored_reduce.CAP_BOUND_FRACTION` to 0.25 flips the 3-of-10 cell;
>   - a source scan finds no `0.2` literal.
> - **v4 items not implemented in v1:** `below_floor`, K24 `attempt_divergence`, `night_exhausted`, recapture and per-night levers. v1 has no registered-mode claim path until they are ruled into Registration or the packer.

There is support for keeping equality as capped: the runtime already reports `emitted == cap` as `"length"` (`joulewise/adapters/mlx_runtime.py:622-624`).

**Tier: MATERIAL for the runner lane.** Runtime failures (`runtime_failed`, `malformed` at `mlx_runtime.py:568,590`) are not in the row's `stop_reason` vocabulary. They therefore refuse loudly, and the runner lane must rule on how they are typed.

## R4: How executed spread and drift are presented

**Tier: MATERIAL.**
- **Spread belongs to cells.** Spread is ruled per cell (45/10 §Q4 at `…/10-coldgate-fable-ruling.md:71`; FT-7 and FT-10), and the merged code computes it per cell (`scored_packer.py:152`). RD-6's "per-level" wording (`89…:788`) loses to the rulings, which rank higher in the authority chain.
- **Drift belongs to levels.** Mapping a spread-exceeded cell to its level's status is A293's job (AP-5M v4 glossary, `07d…:254`). A292 never emits a per-level spread flag.
- **Affirm X-5 as merged.** I recommend treating the merged return shape as ruled for A292 (`scored_packer.py:498-503`, checker `tests/scored_roster_checker.py:842-856`).
- **"Its numbers are reported"** needs the counts that sit behind each flag. The reducer computes those counts from its own parent records. It must then agree with the flag, which gives a free cross-check between two implementations.
- **R6-1:** record `mean_envelope_index` per cell. It is descriptive only, and it keeps option (ii) open without the reducer deciding anything.

> **Executable text R4.**
> - `status = executed_status(registration, roster, predicted_decode_s, frozenset(counted_keys))`.
> - `cells[c]["spread_exceeded"] = status["spread_exceeded"][c]`.
> - `levels[L]` = `{executed_drift_lever_slots: status[…][L], drift_exceeded: status[…][L], max_gap: registration.max_gap}`. In pilot mode or when the lever is null, `drift_exceeded` is false.
> - `fully_counted_parents` = the cell's parents with every item counted.
> - `distinct_envelopes` = distinct `envelope_index` values over those parents' counted windows.
> - `mean_envelope_index` = the mean, over the cell's parents with at least one counted window, of each parent's item-weighted mean envelope index. It is null if there are none.
> - The reducer refuses `internal_disagreement` unless `spread_exceeded == (fully_counted_parents < MIN_PARENT_BLOCKS or distinct_envelopes < MIN_ENVELOPES)` for all ten cells. The witness is exit injection: patch `executed_status` to flip one cell.
> - Precedence (NE > NR, both reasons recorded) is A293's. A292 emits the typed evidence only.

## R5: INV-12

**No dependency.**

**Evidence (P4):** I changed one single's `predicted_item_s` by 0.001 and resealed:
- `verify_executed_roster` refuses **`inv_38`**, because replay regenerates the single from the parent (`scored_packer.py:453,488`);
- the checker reports `INV-12` and `INV-38`.

On any roster that reaches the reducer's body, the checker's stricter clause and the seal agree. The difference is unreachable after replay. The one path it could move is the refusal code. If the reconciliation lane adds the clause to the seal's `inv_12`, then `_seal`, which runs before replay, would report `inv_12` first.

> **Executable text R5.**
> - The harness asserts `code in {"inv_12", "inv_38"}` for the forged-single witness, and nowhere else depends on INV-12.
> - The differential comparison with `check_executed` runs only on rosters that pass `verify_executed_roster`.
> - No A292 assertion compares checker-INV-12 output. This complies with `…/82-coldgate-packet-a291-r3method/30-addendum/21-coldgate-fable-r4-addendum-ruling.md:63`.

## R6: The stopped draft `c0998fdb`

**Use it only as an untrusted source of test cases. Reuse no code. Tier: MATERIAL.**

Reasons:
- It imports the obsolete `_verify_roster` (`c0998fdb:joulewise/scored_reduce.py:8`).
- It reads block fields that no longer exist: `arm`, `origin_attempt`, `ceiling_violation` (`:71-72,90`).
- It refuses terminal windows (`:54,71-74`), which is P6 and was ruled against as F3.
- It requires all active windows (`:77-78`).
- It keeps a second cap flag, `truncated` (`:104-106`).
- It reads stored `drift_exceeded` (`:125`).
- It reads `registration.cap_bound_fraction` (`:169`), an attribute that no longer exists.
- Its refusals are plain strings.

It also belongs to the lane stopped under the class-iv rule (`…/37-a281a-stop-and-consult-brief.md:5-11`). The kernel's acceptance text records that it is not accepted.

> **Executable text R6.** The harness seat may take *input shapes* from `c0998fdb` lines 60-75 (unmatched and duplicate windows), 85-97 (row does not match block), 100-112 (integer tokens; the cap boundary; capped-but-correct) and 113-116 and 143 (partition). It re-derives each expected outcome from R1–R3. No line of the draft is copied into `joulewise/`.

## R7: Delegation

**Tier: MATERIAL. An independent oracle is needed.** The claim-bearing risk is in aggregation, which the roster checker does not cover:
- counting a split parent's singles twice;
- letting a voided or terminal window leak into `g_j`;
- getting `k` wrong for the bootstrap's `k·(floor_j + anchor_j)·s` term (`…/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:68`);
- taking tokens from a superseded row.

Named tests check chosen points. Only an oracle compared over generated nights covers the combinations. The oracle is small, about 150 lines, because the roster is already verified.

> **Executable text R7.**
> **Harness seat.** `WRITE_SCOPE: ["tests/test_scored_reduce.py", "tests/scored_reduction_oracle.py"]`. Ruled text in R1–R6 only; the seat is never shown c0998fdb as code.
>
> The oracle is stdlib-only and imports nothing from `joulewise`. It computes `items`, `parents`, `cells` (except `spread_exceeded`) and `uncounted_windows` from `(registration mapping, roster, rows, windows)`.
>
> The test module imports the reducer inside a helper, so each test fails RED on its own. It holds:
> 1. The AST first-statement test and the signature test (five parameters, no defaults).
> 2. One named test per refusal code in R1, each asserting the class and `.code`.
> 3. One test per row of the R2 table.
> 4. The cap boundary (`cap−1` / `cap`, plus `stop_reason` disagreement both ways) and the `CAP_BOUND_FRACTION` witness from R3.
> 5. A binding witness per digest and per record type. This includes a row stamped with a stale in-force digest, and a roster sealed under a changed `scorer_id` registration (`inv_01`).
> 6. INV-13: `retry_stage` on every item record and `retry_stage_counts` in every cell.
> 7. Every A291 row marked `R` / PROVISIONAL (INV-26, INV-45, the entry-injected rows under §5.1, and every row with an R column in `89…` §5.3), re-run through `reduce` itself, not just `verify_executed_roster`. Codes are asserted exactly, except the INV-12 rule in R5.
> 8. The differential test: ≥ 200 finished nights from `tests.scored_case_generator.generate_case(seed, i)`. Each gets rows and windows generated with seeded drops of 0–25 % of live windows. The reducer's output minus `sha256` must equal the oracle's, and the cell flags must equal `check_executed`.
>
> The harness is committed RED before the implementation seat starts.
>
> **Implementation seat.** `WRITE_SCOPE: ["joulewise/scored_reduce.py"]`. It starts at the harness commit. Any required change to the tests, the oracle, the packer, the checker, the registration, the kernel or the AP-5M text returns `NEEDS_SCOPE` or `NEEDS_RULING`.
>
> **Gate.** Full claim-bearing review, the operand, boundary and guard-deletion mutation sweeps on `scored_reduce.py`, and a cold gate before merge.

---

## What would show this design wrong

- **A ruling that `roster_sha256` means the root digest.** In-force binding would then refuse legitimate rows stamped by a runner built to that reading. Resolve it before PR B designs its row stamps.
- **The runner lane cannot stamp in-force digests,** for example because scoring happens offline without the per-envelope roster. The fallback is root binding plus a separate FT-9 check.
- **A window is missing for a live placement in a night whose levels all resolve.** That means `window_missing` has become a silent selection effect. The proof would be a claim-bearing level with `uncounted.window_missing > 0` that is not NR.
- **Some legitimate item's `generated_tokens` exceeds the cap** under MLX (for example because a special token is counted). `tokens_over_cap` would then refuse real nights, and the rule needs a physical re-derivation.
- **The oracle and the reducer agree but both disagree with a hand-computed night.** That would mean they shared a misreading, and the oracle needs a third author.

## Where I expect disagreement

- The other seats may take the root digest as "the roster digest" (simpler to stamp), or may require `window_missing` to refuse.
- Some may parameterize the cap policy "for v5 readiness". I say that creates the hybrid.
- Some may treat the oracle as ceremony because the checker already exists.
- The INV-13 output-side reading, and adding `bundle_sha256`, go beyond the scout's scope. Both are my additions.
