# Results-fill registry `_v5` regeneration — row change record

Date: 2026-08-31  
Scope: `docs/paper/results-fill-registry.md` and the row-synchronized
`docs/paper/round7/fill-checklist.md`  
Frozen input: `docs/paper/draft-v1.md`, SHA-256
`939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`

Replay the fail-closed row and draft census with
`01-verify-registry-v5.py` from the repository root using the project virtual
environment.

## Authorities

- **D-164:** `_v5` pair `qwen3-1p7b` / `qwen3-8b`; `_v4` never collected.
- **V5GEN:** `configs/campaigns/d117_contrast_v5/generate_configs.py`, binding
  pack, floor-artifact, contrast, cell-family, and D-165 replay names.
- **D-165:** decision-log body plus cold-gate ruling and R-5 completion in
  `docs/process_traces/2026-08-30-t28-v5-prep/REFUTER-ROUND-1-DISPOSITION.md`.
- **D-166A:** the amended D-166 index row and
  `docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md`.
- **PANEL / WORKLOAD:** `configs/model_panels/qwen3_4bit.json` and
  `configs/workloads/real_prompts_v1.json`.
- **R-6:** round-7 row regeneration ruling in
  `docs/process_traces/2026-08-27-t26/paper-round7-prep/04-MAGISTRATE-RULING.md`.
- **C7 / PROJ:** reviewer synthesis C7 and
  `docs/paper/round7/prefill-resolvability-projection.md` Sections 4 and 11.

## Added registry rows (25)

### Identity and workload binding rows (8)

| Added row | Binding | Authority |
|---|---|---|
| V5-ID-001 | `qwen3-1p7b` ID and revision | D-164, PANEL |
| V5-ID-002 | `qwen3-8b` ID and revision | D-164, PANEL |
| V5-WL-001 | `real_prompts_v1`, eight prompts, prompt-set hash | D-166A, WORKLOAD, PANEL |
| V5-WL-002 | tokenizer SHA-256 | D-164, D-166A, PANEL |
| V5-WL-003 | chat-template SHA-256, template applied, thinking off | D-166A, PANEL |
| V5-WL-004 | greedy decode, forced 512 | D-166A, V5GEN |
| V5-G2A-001 | `[PREFILL_LENGTH]` selection rule and hash-pinned record | D-166A, `scripts/select_g2a_prefill_length.py` |
| V5-WL-005 | prompt-pin v2 and G2-a hash cross-check | D-166A, V5GEN |

### Exact-key rows (17)

| Added exact key | Disposition | Authority |
|---|---|---|
| `[PREFILL_LENGTH]` | `collection_prefill_tokens`; unresolved until hash-pinned G2-a output | D-166A |
| `[R_1p7B_prefill_p[PREFILL_LENGTH]_abs]` | independent-corner absolute R | D-165, D-166A, V5GEN |
| `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_abs]` | absolute R_cm `not_applicable` | D-165 R-5, D-166A, V5GEN |
| `[R_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | independent-corner comparative R | D-165, D-166A, V5GEN |
| `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | mandatory comparative replay | D-165 R-5, D-166A, V5GEN |
| `[R_1p7B_decode_abs]` | independent-corner absolute R | D-165, V5GEN |
| `[R_cm_1p7B_decode_abs]` | absolute R_cm `not_applicable` | D-165 R-5, V5GEN |
| `[R_1p7B_decode_cmp]` | independent-corner comparative R | D-165, V5GEN |
| `[R_cm_1p7B_decode_cmp]` | mandatory comparative replay | D-165 R-5, V5GEN |
| `[R_8B_prefill_p[PREFILL_LENGTH]_abs]` | independent-corner absolute R | D-165, D-166A, V5GEN |
| `[R_cm_8B_prefill_p[PREFILL_LENGTH]_abs]` | absolute R_cm `not_applicable` | D-165 R-5, D-166A, V5GEN |
| `[R_8B_prefill_p[PREFILL_LENGTH]_cmp]` | independent-corner comparative R | D-165, D-166A, V5GEN |
| `[R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp]` | mandatory comparative replay | D-165 R-5, D-166A, V5GEN |
| `[R_8B_decode_abs]` | independent-corner absolute R | D-165, V5GEN |
| `[R_cm_8B_decode_abs]` | absolute R_cm `not_applicable` | D-165 R-5, V5GEN |
| `[R_8B_decode_cmp]` | independent-corner comparative R | D-165, V5GEN |
| `[R_cm_8B_decode_cmp]` | mandatory comparative replay | D-165 R-5, V5GEN |

All eight R rows use the complete corner-widened unguarded numerator and
unguarded point denominator. The threshold is inclusive at 2.0. All four
comparative R_cm rows are mandatory and `< 2.0` withdraws the dominance
sentence. All four absolute R_cm rows carry the registered cancellation reason.

## Renamed exact-key rows (66)

Every row below is a one-for-one rename; no old `_v4` key remains live. D-164
authorizes the model rename. D-166A and V5GEN additionally authorize every
`prompt` to `prefill_p[PREFILL_LENGTH]` rename and its unresolved status.

| Retired `_v4` key | Live `_v5` key |
|---|---|
| `[F_1p5B_prompt_abs_J]` | `[F_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| `[F_1p5B_prompt_cmp_J]` | `[F_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| `[F_1p5B_prompt_operative_J]` | `[F_1p7B_prefill_p[PREFILL_LENGTH]_operative_J]` |
| `[F_1p5B_decode_abs_J]` | `[F_1p7B_decode_abs_J]` |
| `[F_1p5B_decode_cmp_J]` | `[F_1p7B_decode_cmp_J]` |
| `[F_1p5B_decode_operative_J]` | `[F_1p7B_decode_operative_J]` |
| `[F_7B_prompt_abs_J]` | `[F_8B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| `[F_7B_prompt_cmp_J]` | `[F_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| `[F_7B_prompt_operative_J]` | `[F_8B_prefill_p[PREFILL_LENGTH]_operative_J]` |
| `[F_7B_decode_abs_J]` | `[F_8B_decode_abs_J]` |
| `[F_7B_decode_cmp_J]` | `[F_8B_decode_cmp_J]` |
| `[F_7B_decode_operative_J]` | `[F_8B_decode_operative_J]` |
| `[TERM_A_1p5B_prompt_abs_J]` | `[TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| `[TERM_B_1p5B_prompt_abs_J]` | `[TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| `[TERM_A_1p5B_prompt_cmp_J]` | `[TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| `[TERM_B_1p5B_prompt_cmp_J]` | `[TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| `[TERM_A_1p5B_decode_abs_J]` | `[TERM_A_1p7B_decode_abs_J]` |
| `[TERM_B_1p5B_decode_abs_J]` | `[TERM_B_1p7B_decode_abs_J]` |
| `[TERM_A_1p5B_decode_cmp_J]` | `[TERM_A_1p7B_decode_cmp_J]` |
| `[TERM_B_1p5B_decode_cmp_J]` | `[TERM_B_1p7B_decode_cmp_J]` |
| `[TERM_A_7B_prompt_abs_J]` | `[TERM_A_8B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| `[TERM_B_7B_prompt_abs_J]` | `[TERM_B_8B_prefill_p[PREFILL_LENGTH]_abs_J]` |
| `[TERM_A_7B_prompt_cmp_J]` | `[TERM_A_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| `[TERM_B_7B_prompt_cmp_J]` | `[TERM_B_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` |
| `[TERM_A_7B_decode_abs_J]` | `[TERM_A_8B_decode_abs_J]` |
| `[TERM_B_7B_decode_abs_J]` | `[TERM_B_8B_decode_abs_J]` |
| `[TERM_A_7B_decode_cmp_J]` | `[TERM_A_8B_decode_cmp_J]` |
| `[TERM_B_7B_decode_cmp_J]` | `[TERM_B_8B_decode_cmp_J]` |
| `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` | `[TERMINAL_REFUSAL_REASON_1p7B_prefill_p[PREFILL_LENGTH]]` |
| `[TERMINAL_REFUSAL_REASON_1p5B_decode]` | `[TERMINAL_REFUSAL_REASON_1p7B_decode]` |
| `[TERMINAL_REFUSAL_REASON_7B_prompt]` | `[TERMINAL_REFUSAL_REASON_8B_prefill_p[PREFILL_LENGTH]]` |
| `[TERMINAL_REFUSAL_REASON_7B_decode]` | `[TERMINAL_REFUSAL_REASON_8B_decode]` |
| `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` | `[NO_EXACT_FLOOR_REASON_1p7B_prefill_p[PREFILL_LENGTH]]` |
| `[NO_EXACT_FLOOR_REASON_1p5B_decode]` | `[NO_EXACT_FLOOR_REASON_1p7B_decode]` |
| `[NO_EXACT_FLOOR_REASON_7B_prompt]` | `[NO_EXACT_FLOOR_REASON_8B_prefill_p[PREFILL_LENGTH]]` |
| `[NO_EXACT_FLOOR_REASON_7B_decode]` | `[NO_EXACT_FLOOR_REASON_8B_decode]` |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]` | `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p7B_prefill_p[PREFILL_LENGTH]]` |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]` | `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p7B_decode]` |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]` | `[AVAILABLE_DIAGNOSTIC_CLAUSE_8B_prefill_p[PREFILL_LENGTH]]` |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]` | `[AVAILABLE_DIAGNOSTIC_CLAUSE_8B_decode]` |
| `[POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]` | `[POINT_DIAGNOSTIC_CLAUSE_1p7B_prefill_p[PREFILL_LENGTH]]` |
| `[POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]` | `[POINT_DIAGNOSTIC_CLAUSE_1p7B_decode]` |
| `[POINT_DIAGNOSTIC_CLAUSE_7B_prompt]` | `[POINT_DIAGNOSTIC_CLAUSE_8B_prefill_p[PREFILL_LENGTH]]` |
| `[POINT_DIAGNOSTIC_CLAUSE_7B_decode]` | `[POINT_DIAGNOSTIC_CLAUSE_8B_decode]` |
| `[REFUSAL_REASON_1p5B_floor_window]` | `[REFUSAL_REASON_1p7B_floor_window]` |
| `[REFUSAL_REASON_7B_floor_window]` | `[REFUSAL_REASON_8B_floor_window]` |
| `[E_1p5B_prompt_J_per_request]` | `[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]` |
| `[E_1p5B_prompt_lower_J]` | `[E_1p7B_prefill_p[PREFILL_LENGTH]_lower_J]` |
| `[E_1p5B_prompt_upper_J]` | `[E_1p7B_prefill_p[PREFILL_LENGTH]_upper_J]` |
| `[E_1p5B_prompt_J_per_token]` | `[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_token]` |
| `[N_bundles_1p5B_prompt]` | `[N_bundles_1p7B_prefill_p[PREFILL_LENGTH]]` |
| `[E_1p5B_decode_J_per_request]` | `[E_1p7B_decode_J_per_request]` |
| `[E_1p5B_decode_lower_J]` | `[E_1p7B_decode_lower_J]` |
| `[E_1p5B_decode_upper_J]` | `[E_1p7B_decode_upper_J]` |
| `[E_1p5B_decode_J_per_token]` | `[E_1p7B_decode_J_per_token]` |
| `[N_bundles_1p5B_decode]` | `[N_bundles_1p7B_decode]` |
| `[E_7B_prompt_J_per_request]` | `[E_8B_prefill_p[PREFILL_LENGTH]_J_per_request]` |
| `[E_7B_prompt_lower_J]` | `[E_8B_prefill_p[PREFILL_LENGTH]_lower_J]` |
| `[E_7B_prompt_upper_J]` | `[E_8B_prefill_p[PREFILL_LENGTH]_upper_J]` |
| `[E_7B_prompt_J_per_token]` | `[E_8B_prefill_p[PREFILL_LENGTH]_J_per_token]` |
| `[N_bundles_7B_prompt]` | `[N_bundles_8B_prefill_p[PREFILL_LENGTH]]` |
| `[E_7B_decode_J_per_request]` | `[E_8B_decode_J_per_request]` |
| `[E_7B_decode_lower_J]` | `[E_8B_decode_lower_J]` |
| `[E_7B_decode_upper_J]` | `[E_8B_decode_upper_J]` |
| `[E_7B_decode_J_per_token]` | `[E_8B_decode_J_per_token]` |
| `[N_bundles_7B_decode]` | `[N_bundles_8B_decode]` |

## Retired row (1)

| Retired row | Reason | Authority |
|---|---|---|
| PG-03 | Duplicate live row for PG-02's one physical `[PENDING, PENDING]` interval site. PG-02 now owns both lower and upper semantic slots; no supplier or stop changed. | R-6 plus the runner's exact one-row-per-site census requirement |

## Amended, rebound, or status-only rows

These are neither additions nor renames but are recorded so the semantic delta
is reviewable.

| Rows | Change | Authority |
|---|---|---|
| TERM A / TERM B, all 16 live rows | Retained as cell-label diagnostics; removed as headline predicate | D-165 |
| DS-09 through DS-16 | Rebound frozen physical prompt-table anchors to selected Qwen3 prefill suppliers; all placeholder-dependent rows are `UNRESOLVED-UNTIL-G2A` | D-164, D-166A, V5GEN |
| DS-17 through DS-24 | Rebound frozen physical decode-table anchors to Qwen3 and `real_prompts_v1` | D-164, D-166A, PANEL, WORKLOAD, V5GEN |
| DS-33; PG-01, PG-02, PG-04 through PG-08 | Rebound to generator contrast `ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b`; retained `STOP_FILL` because professor-facing tokens are unbuilt | D-164, D-166A, V5GEN, R-6 |
| DG-071 | Proposed median-with-IQR width statistic; corrected former low-band-as-range claim | C7, PROJ, R-6 |
| DG-075 | Proposed median-with-IQR spacing statistic; removed contradicted sampler-pause mechanism | C7, PROJ, R-6 |
| `[B_decode_claim_J]` and DS-29 | Explicitly preserved `STOP_FILL`; deterministic total remains forbidden as a substitute | ruling item 33 |
| Protocol title/subtitle contract | Fixed protocol-first title; subtitle/dominance sentence gated on all R and comparative R_cm dispositions | D-165 |
| Prefill refusal rendering | Split reducer `<3` refusal from resolvable count 3–4 pre-registration refusal | D-166A |
| All 37 live placement rows in the checklist | Regenerated into the same batch/fence structure; PG-02 placed once with two slots | R-6 |

## Census

- Added: **25 rows** = 8 identity/workload bindings + 17 exact keys.
- Renamed: **66 exact-key rows**.
- Retired: **1 live placement row** (PG-03 duplicate).
- Unresolved: **41 exact-key rows** contain `[PREFILL_LENGTH]`; **59 registry
  table rows total** carry `UNRESOLVED-UNTIL-G2A` when binding and placement
  rows are included.
- Exact-key inventory: **126** = prior 109 regenerated one-for-one + 17 added.
- Frozen draft: **34 literal pending sites / 36 slots**; **37 complete-family
  sites / 39 slots**; **2 `[[NEEDS-VALUE:...]]` notes**.
- Live registry placement rows: **37 / 37 sites**, with PG-02 and DS-26 each
  carrying two semantic slots.

## Outstanding rulings and implementation gates

No ruling blocks this registry regeneration. Future fill remains gated on:

1. G2-a record and prompt-pin v2 issuance;
2. renderer/template regeneration for the `_v5` keys and R/R_cm ledger;
3. D-123 reported-mean and claim-side-bound suppliers;
4. ratification plus issued artifacts for DG-071 and DG-075; and
5. release and characterization writers.

None of these gates changes a `STOP_FILL` row in this change set.
