# 10 — Cold Fable gate ruling, A281-DECISION-SPEC-01

Judge: Claude Fable 5.1, fresh session, worktree `JouleWise-wt-coldgate-d8cc9c0a` at `57996bca`. Code judged at `d2f9a273`. Written 2026-09-23 ~20:40 PDT.

## 0. Disclosure, pins, method

Auto-loaded into context before I acted: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md`. None was used as evidence. I read only the packet directory, the charter, and code via `git show d2f9a273:` and a `git archive d2f9a273` copy at `/tmp/coldgate-a281`.

Validator run 1 (deliberate typo sha …`5d82`): `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2 with expected charter sha `099de884…5d81` and packet sha `48209507…6710`: `PASS`, rc 0; twelve exhibits, every observed digest equal to its manifest entry. Independent check: `shasum -a 256` on both files reproduced both expected values. Suite in the archive copy: `Ran 30 tests … OK`.

Executed probe (`/tmp/coldgate-a281/probe_decide.py`): `ratio_interval` replaced by a stub returning prescribed p-values and intervals; `decide` run at d2f9a273. Results cited below as "probe".

## Q1 — decision specification: AMEND D2 (adopt, with rulings below)

**Diagnosis affirmed.** Probe at d2f9a273: `81888` → L\* 3; `18188` → L\* 2; `1n8n1` → L\* 3 (packet C §3 "Non-monotone: … no crossover claimed"; code `energy_per_correct.py:232-240` takes the lowest E8 row with any lower E1 row and never tests order). `12|3|4|5` with `1888` prints constituent levels `ee888`, i.e. `not estimable` for pooled constituents (`:209-212`). `1|2|3|45` with `1111`, and `1|2|345` with `11x`, both return `boundary_in_merged_group` with no E8 group (`:241-245`). The 676 / 123 / 91 counts in exhibit 20 are the seat's; I verified the classes, not the counts.

**Status rule (three-way conjunction): AFFIRM.** Packet C's terms paragraph ("interval wholly below 1") and §3 ("Holm rejects and p_below < p_above") plus M9 ("only on Holm-significant directions") are satisfied together only by the conjunction; a Holm rejection whose widened interval straddles 1 is NR with `interval_disagrees`. Code `:222-227` already implements this conjunction.

**Split 1, licensing: AFFIRM the lead (Opus).** Packet C §3 makes the merged cell the registered unit of test for its constituent levels ("a merged cell tests one hypothesis and m stays 5"); the constituents have no R of their own, so "either constituent's R" (Sol 19, ruling 08) is not a registered quantity. Sol's pooled-reversal argument is real arithmetic but applies identically to pooling problems within one level, so it is not a defect of merging. Cure text: *"A merged group may license L\* only as a region statement. When the licensing group is pooled, the crossover sentence reads: 'The cheaper model per correct answer changed from 1.7B on pooled Levels 1–2 to 8B at Level 3 on this set.' The output carries `licensing_group` (list of levels) and `licensing_pooled: true|false`. The boundary group must always be a single level."* Ruling 08's licensing clause is overturned; its boundary clause stands.

**Split 2, reverse order: AFFIRM the lead (Opus).** Pattern `reverse_order`, reason `reverse_order_not_registered`, no L\*, per-level results printed. NIT.

**Split 3, ceiling violation: AFFIRM the lead (Sol).** Cure text: *"When any item in the family carries a terminal `ceiling_violation`, its group is NE(`ceiling_violation`), every other group is classified and printed, and `crossover_level` is null with reason `ceiling_violation_unresolved` until a registered recapture resolves the item. Pairwise exclusion of the item appears only in the labelled selection-confounded sensitivity."* Reason: the violating item is by construction the longest; a gap there is the selection M12 forbids.

**Isolated sparse Level 3: AFFIRM** NE(`sparse_after_merges`); registration text for A282.

**Amendments to Opus 20's classify:** (a) `gap_levels` must list every NR/NE level in the family, not only those strictly between licensing and boundary; the claim sentence names them. (b) `reverse_order` is any resolved sequence matching `8+1+` with zero further changes; `88111` qualifies, `8n111` too.

### Authoritative worked-pattern table

Statuses per level 1→5: `8` 8B cheaper, `1` 1.7B cheaper, `n` not resolved, `e` not estimable, `p` pooled (with `pooled_in`). Brackets = merged group. "code" = probe at d2f9a273 where it differs.

| Partition / group statuses | Level statuses | Pattern | L\* or reason |
|---|---|---|---|
| 1\|2\|3\|4\|5 `1n888` | `1n888` | crossover | **3**, gap 2 |
| `88111` | `88111` | reverse_order | none, `reverse_order_not_registered` |
| `81888` | `81888` | non_monotone | none (code: 3) |
| `18188` | `18188` | non_monotone | none (code: 2) |
| `1n8n1` | `1n8n1` | non_monotone | none (code: 3) |
| `1nn8n` | `1nn8n` | crossover | **4**, gaps 2,3,5 |
| `n1n8n` | `n1n8n` | crossover | **4**, licensing 2, gaps 1,3,5 |
| `11188` | `11188` | crossover | **4** |
| `11n88` | `11n88` | crossover | **4**, gap 3 |
| `11111` | `11111` | all_1.7B | none, `no_8B_cheaper_group` |
| `88888` | `88888` | all_8B | none, `no_1.7B_cheaper_group` |
| `111n1` | `111n1` | one_signed_1.7B | none, `no_8B_cheaper_group` |
| `n8888` | `n8888` | one_signed_8B | none, `no_1.7B_cheaper_group` |
| `nnnnn` | `nnnnn` | none_resolved | none, `none_resolved` |
| 1\|2\|3\|4\|5, L3 sparse `11e88` | `11e88` | crossover | **4**, licensing 2, gap 3 (NE) |
| 1\|2\|3\|45 `1118` | `111pp` | crossover | none, `boundary_group_pooled`; crossover_group 4–5 |
| 1\|2\|3\|45 `1111` | `111pp` | all_1.7B | none, `no_8B_cheaper_group` (code: false `boundary_in_merged_group`) |
| 1\|2\|3\|45 `n1n8` | `n1npp` | crossover | none, `boundary_group_pooled` |
| 12\|3\|4\|5 `1888` | `pp888` | crossover | **3**, licensing 1–2 pooled (code: none; 08: undefined) |
| 12\|3\|45 `1n8` | `ppnpp` | crossover | none, `boundary_group_pooled` |
| 1\|2\|345 `11e` | `11eee` | one_signed_1.7B | none, `no_8B_cheaper_group` (code: false `boundary_in_merged_group`) |
| 123\|4\|5 `e18` (Sol) | `eee18` | crossover | **5**, licensing 4, gaps 1–3 (NE) |
| 1\|2\|345 `1n8` (Sol `1:1\|2:n\|[3–5]8`) | `1nppp` | crossover | none, `boundary_group_pooled` |
| 1\|2\|3\|45 `1n88` (Sol `1:1\|2:n\|3:8\|[4–5]8`) | `1n8pp` | crossover | **3**, gap 2 |
| 12345 `e` | `eeeee` | none_estimable | none, `none_estimable` |
| any partition, one group NE(`ceiling_violation`) | as above | as classified | none, `ceiling_violation_unresolved` |

## Q2 — D3, D4, D5: AFFIRM with amendments

**D3 acceptance shape: AFFIRM.** Amend: the reference encoding in the fix brief is generated from THIS table and the Q1 cure text, and is total over the 1,764-case superset (every `{1,8,n,e}` assignment on the nine partitions); the 676 reachable set is checked as a subset. Mutation counts are not acceptance evidence for `classify`. Holm tests must include exact-cutoff equality and stop-after-first-failure (already at d2f9a273, keep).

**D4 Registration: AFFIRM.** Verified silent defaults at d2f9a273: `scored_reduce.py:72` `row.get("retry_stage", "initial")`; `scored_packer.py:197` `worst_case_s_per_item=None`; `:200` `setdefault("registered_sha256", …)`; `decide` `:155` binds family to nothing. Field list: Opus 20 Q4 plus Sol 19's identity/scope items. Amend: `mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode. The AST scan is scoped to input-record access, not to internal dicts.

**D5a bootstrap bound: AFFIRM Opus's share-scaled bound.** Code `:99-100` fixes `error8/error17` once and reuses them at `:123` for every replicate (Sol 14 B1 confirmed by reading). Cure: per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`, with `k` the block's measured windows for that model and `s` the drawn-token share used at `:60-65`; point bounds keep `s = 1`.

**D5b drift refusal: AFFIRM**, amend units: register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows. `requeue_overrun` recomputes `drift_lever_slots`.

**D5c: AFFIRM** as Q1 split 3. The reducer passes `terminal_refusals` through typed, never the pairing `ValueError` (`:90-91` today).

## Q3 — D6 scope: AFFIRM

The consult has run; A281a round 2 carries a structural cure (Registration) and a narrowed clause set, so it is not a third same-shape round under charter §9. Conditions: (1) A281a's brief includes the cell interface (`terminal_refusals`, `parent_block_id`, `retry_stage` required) and the Registration schema verbatim; (2) no estimator implementation begins before this table is in the AP-5M text; (3) A281a's acceptance may not describe the headline decision as passing.

## Q4 — standing sub-rulings

**F1: AFFIRM.** Drift cancels in a per-level ratio only when each model's measured blocks share the mean envelope index; `idle_slot` captured, never a numerator. **F2: AFFIRM** with 08's conditions (a)–(d). **M12 amendment: AFFIRM**, MATERIAL condition: the worst-case seconds input is derived in Registration (`cap × s_per_token_upper + prefill`) and asserted ≥ the failed prediction, and the AP-5M text carries the amended M12 wording so registration and code do not diverge.

## Findings

- **BLOCKER B1.** Non-monotone and reverse patterns yield L\* at d2f9a273 (probe: `81888`, `18188`, `1n8n1`). Cure: Q1 table.
- **BLOCKER B2.** Split-block bootstrap bound is draw-invariant (`:99-100`, `:123`). Cure: D5a text.
- **MATERIAL M1.** False `boundary_in_merged_group` without an E8 group (`:241-245`); pooled constituents printed `not estimable` (`:209-212`). Cure: level status `pooled`, reasons per table.
- **MATERIAL M2.** Silent defaults (`scored_reduce.py:72`, `scored_packer.py:197,200`; family unbound `:155`). Cure: D4.
- **MATERIAL M3.** M12 amendment lacks the derived worst-case check (Q4).
- **NIT N1.** Exhibits 17 and 20 are magistrate transcriptions, not verbatim seat output; the counts 676/123/91 are unreproduced here. Packet hygiene otherwise adequate: contrary seat (Sol 19) present on every split.

Disagreement with the lead: none on the three picks; amendments to D2 (gap listing, reverse-order definition), D3 (superset enumeration), D4 (claim_ready flag), D5b (units).
