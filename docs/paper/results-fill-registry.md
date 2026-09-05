# Results fill registry

Regenerated 2026-08-31 for the never-collected `_v4` to `_v5` transition.
The frozen source is `docs/paper/draft-v1.md`, SHA-256
`939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`,
672 lines. Its bytes are read-only. The current census is 34 literal
`[PENDING...]` sites carrying 36 semantic slots, 37 sites and 39 slots across
the complete result-marker family, and two `[[NEEDS-VALUE:...]]` sites.

This registry binds the `_v5` production pair selected by D-164:
`qwen3-1p7b` (`mlx-community/Qwen3-1.7B-4bit`) and `qwen3-8b`
(`mlx-community/Qwen3-8B-4bit`). The identifier spellings come from
`configs/model_panels/qwen3_4bit.json` and
`configs/campaigns/d117_contrast_v5/generate_configs.py`; no Qwen2.5 `_v4`
artifact may supply a prospective row. Retained calibration, excursion, and
anchor-correction rows in the diagnostic-era section remain historical,
non-claim-bearing evidence and are generation-independent.

The crosswalk does not authorize a value merely by naming it. A renderer stops
when an authenticated artifact, exact field, registered replay, branch
predicate, or identity pin is absent. `STOP_FILL` rows remain stopped unless a
named ruling and a built supplier both exist. D-165 replaces the old headline
predicate with the registered ratio R while preserving TERM A / TERM B only as
the coded cell-label diagnostic. D-166 replaces the synthetic decode prompt
with the hash-bound `real_prompts_v1` profile and leaves the prefill length
unresolved until the G2-a selection record issues.

## Rules and source index

Fill-rule vocabulary is closed:

- `MEASURED`: copy or conservatively render an authenticated issued artifact
  field. Never calculate a replacement from prose.
- `DERIVE`: compute only the formula or renderer rule named here from
  authenticated parents. Reject an independently supplied value.
- `STOP_FILL`: do not render a value. This includes an unknown supplier,
  absent required parent, failed predicate, malformed reason, or unissued
  governing verdict.

Freeze labels distinguish a frozen key or derivation from an issued value.
`KEY_FROZEN / VALUE_UNISSUED` means the vocabulary is fixed but no result may
be inserted. `SUPPLIER_UNKNOWN` identifies a missing field contract, not a
license to infer one.

Capture-method and estimator provenance are independent fill preconditions:

- **F2 — folded.** Capture-method era is an independent fill precondition:
  claim-bearing evidence must positively name a current claim-bearing anchor
  method. Re-registering or re-deriving a historical corpus does not turn it
  into a supplier. This strengthens, and does not replace, the verbatim
  D-117/D-122/D-123 rule above.
- **F5 — folded.** Every comparative `floor_cmp_j` supplier must authenticate
  the estimator selected by the prospectively fixed plan. Estimator identity
  is never accepted from a result or floor artifact, and a comparative value
  produced under another estimator is not interchangeable.

Every row cites one or more of these defining sources:

- `DRAFT` — `docs/paper/draft-v1.md`, especially Sections 6 and 7 and the
  bracket markers enumerated below.
- `TPL` — `docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md`,
  Fill key and the guarded Section 6 and Section 7 variants. This is the
  binding token vocabulary.
- `LINT` —
  `docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py`,
  which enforces branch selection, global token licensing, and `STOP_FILL`.
- `SPEC` — `configs/campaigns/metrology_v1/characterization_result_schema_v1.json`,
  the frozen characterization result specification, with its normative prose
  contract `docs/contracts/characterization_result_schema_v1.md`. Its
  `render_map.rows` object names the producing report field for every
  characterization token; `render_map.derived_value_rules` states the two
  derivations; `render_map.outcome_phrases` fixes the closed plain-language
  phrase set. The four limits it left open were ruled by D-152 on 2026-08-24.
- `DF` — `joulewise/detection_floor.py`, stable output fields emitted by
  `build_floor_cell`: `floor_abs_j`, `floor_cmp_j`, `floor_gate_j`,
  `eligibility`, and `point_floor_diagnostics`. Its validator fixes
  `floor_gate_j = max(floor_abs_j, floor_cmp_j)` when both components exist.
- `FX` — `joulewise/floor_extraction.py`, `CellReport.as_row` and
  `extract_cells`: extraction rows expose `refusal_reasons`, `floor`, admitted
  counts, diagnostics, and `all_cells_extractable`.
- `WV` — `scripts/run_campaign.py`, ordinary whole-window verdict row:
  `status`, `member_failures`, `idle_admission_core.conditions`, and the
  evaluation basis.
- `CV` — `joulewise/analysis_engine/__init__.py`, `_contrast_row`: claim-verdict
  fields under `contrasts[]`, including `estimator.estimate`,
  `deterministic_bounds.decision_interval`, `floor`, and `claim_evaluation`;
  `joulewise/analysis_engine/claims.py` defines the outcome semantics.
- `MINT` — `docs/phase_2/floor_mint_contract.md`, W3 component composition and
  the rule that a cell gate is the component maximum, never the sum.
- `AUTH` — `docs/decision_log.md`, D-119 and D-121 through D-124. D-119 requires
  conservative claim language; D-122 supersedes decode-only gamma; D-123 owns
  the reported-mean cells; D-124 owns the candidate contrast estimator and its
  transfer-assumption disclosure.
- `PLAN` —
  `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md`, which names
  alpha and beta as four-cell floor producers and gamma as the prospective
  contrast producer. Its decode-only gamma description is superseded by
  D-122.
- `V5GEN` — `configs/campaigns/d117_contrast_v5/generate_configs.py`, the
  authority for `_v5` pack, contrast, floor-artifact, cell, and family naming;
  its `dominance_criterion` is the frozen D-165 ratio/replay contract.
- `PANEL` — `configs/model_panels/qwen3_4bit.json`, which pins model IDs,
  revisions, tokenizer and chat-template SHA-256 values, thinking policy, and
  the rendering pinset.
- `WORKLOAD` — `configs/workloads/real_prompts_v1.json`, the ordered eight-prompt
  profile with prompt-set SHA-256
  `20debdb41eb4983339a160176dcf4e475153b5d6f16b1ef3ada39447e99f3474`.
- `G2A` — `scripts/select_g2a_prefill_length.py` and the hash-pinned
  `joulewise.g2a_prefill_selection.v1` output it will issue. D-166 as amended
  and its ratification at
  `docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md`
  own the four-rung rule and split refusal branch.
- `D165` — D-165 as cold-gate-amended, including R-5 completion in
  `docs/process_traces/2026-08-30-t28-v5-prep/REFUTER-ROUND-1-DISPOSITION.md`:
  independent-corner R is gated, comparative R_cm is the mandatory
  shared-energy-sign/local-corner diagnostic with the `< 2.0` withdrawal, and
  absolute R_cm is registered not applicable because the replay is
  comparative-only.

Campaign shorthand used below is semantic:

- `alpha`: prospective `qwen3-1p7b` floor window, artifact IDs
  `d117-qwen3-1p7b-decode-floor-v5` and
  `d117-qwen3-1p7b-prefill-p[PREFILL_LENGTH]-floor-v5`.
- `beta`: prospective `qwen3-8b` floor window, artifact IDs
  `d117-qwen3-8b-decode-floor-v5` and
  `d117-qwen3-8b-prefill-p[PREFILL_LENGTH]-floor-v5`.
- `gamma`: prospective pack
  `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`, with decode contrast
  `ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b` and prefill contrast
  `ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b`.
- `characterization`: the separately governed Window C characterization
  campaign, not any historical window called C.

`[PREFILL_LENGTH]` is a parameter placeholder, not a guessed value. It resolves
only to `collection_prefill_tokens` in the hash-pinned G2-a selection record,
and must equal `prefill_length` and `prompt_tokens` in the subsequently issued
`joulewise.prefill_prompt_pin.v2`. Every row containing it is
`UNRESOLVED-UNTIL-G2A`; textual substitution before that record and hash exist
is `STOP_FILL`.

## `_v5` identity and workload bindings

| Registry row | Binding | Frozen supplier | Status | Authority |
|---|---|---|---|---|
| V5-ID-001 | Small-model ID `qwen3-1p7b`, revision `3b1b1768f8f8cf8351c712464f906e86c2b8269e` | `configs/model_panels/qwen3_4bit.json` entry `qwen3-1p7b` | KEY_FROZEN | D-164, PANEL |
| V5-ID-002 | Large-model ID `qwen3-8b`, revision `545dc4251c05440727734bcd94334791f6ab0192` | `configs/model_panels/qwen3_4bit.json` entry `qwen3-8b` | KEY_FROZEN | D-164, PANEL |
| V5-WL-001 | Decode profile `real_prompts_v1`, eight ordered prompts, prompt-set SHA-256 `20debdb41eb4983339a160176dcf4e475153b5d6f16b1ef3ada39447e99f3474`; the two-model contrast uses prompt 0 in both arms and makes no prompt-population generality claim | Workload profile plus panel rendering pinset `qwen3-real-prompts-v1-thinking-off` | KEY_FROZEN | D-166, WORKLOAD, PANEL |
| V5-WL-002 | Shared `tokenizer.json` SHA-256 `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` | Both panel entries and the rendering pinset | KEY_FROZEN | D-164, D-166, PANEL |
| V5-WL-003 | Shared chat-template SHA-256 `87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5`; template applied; `enable_thinking=false` | Both panel entries and the rendering pinset | KEY_FROZEN | D-166, PANEL |
| V5-WL-004 | Greedy generation, forced 512 output tokens, one rendered prompt per member; gamma uses prompt 0 throughout while the same-model floor packs remain unchanged | `_v5` generator decode workload and D-166 R-1 | KEY_FROZEN | D-166, V5GEN |
| V5-G2A-001 | `[PREFILL_LENGTH]` = G2-a record `collection_prefill_tokens`; shortest clearing rung in 512/1024/2048/4096, otherwise 4096 | `scripts/select_g2a_prefill_length.py` output; exact output path and its SHA-256 are not yet issued | UNRESOLVED-UNTIL-G2A / STOP_FILL | D-166 as amended, G2A |
| V5-WL-005 | Prefill text, token IDs, repeat count, generation method, and selection authority | Post-selection `joulewise.prefill_prompt_pin.v2`, including `g2a_record_sha256` | UNRESOLVED-UNTIL-G2A / STOP_FILL | D-166 as amended, V5GEN, G2A |

## Exact template-token registry

There is one row for every distinct bracket token recognized by the template
census. Repeated occurrences of a token share this row and therefore the same
source value.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[PREFILL_LENGTH]` | Hash-pinned `joulewise.g2a_prefill_selection.v1` output from `scripts/select_g2a_prefill_length.py`, field `collection_prefill_tokens`; cross-check the post-selection prompt pin's `prefill_length` and `prompt_tokens` | all `_v5` prefill suppliers and identifiers | MEASURED | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; no path, hash, or rung may be guessed | G2A, V5GEN |

### Alpha and beta floor-cell values

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[F_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` | Aggregate floor artifact `d117-qwen3-1p7b-prefill-p[PREFILL_LENGTH]-floor-v5`, selected cell `floor_abs_j` | alpha / prefill-p[PREFILL_LENGTH] absolute component | MEASURED | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; exact cell ID comes only from the generated floor pack | DF, MINT, V5GEN, G2A |
| `[F_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` | Same selected cell, `floor_cmp_j`; estimator identity must match its frozen registration | alpha / prefill-p[PREFILL_LENGTH] comparative component | MEASURED | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, MINT, V5GEN, G2A |
| `[F_1p7B_prefill_p[PREFILL_LENGTH]_operative_J]` | `max(F_1p7B_prefill_p[PREFILL_LENGTH]_abs_J, F_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J)`; require exact equality with `floor_gate_j` | alpha / prefill-p[PREFILL_LENGTH] aggregate cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, MINT, V5GEN, G2A |
| `[F_1p7B_decode_abs_J]` | Aggregate floor artifact `d117-qwen3-1p7b-decode-floor-v5`, selected decode cell `floor_abs_j` | alpha / decode absolute component; `real_prompts_v1` | MEASURED | KEY_FROZEN / VALUE_UNISSUED; prompt, tokenizer, template, and thinking pins must match V5-WL-001 through V5-WL-004 | DF, MINT, V5GEN, PANEL, WORKLOAD |
| `[F_1p7B_decode_cmp_J]` | Same selected decode cell, `floor_cmp_j`; estimator identity must match its frozen registration | alpha / decode comparative component; `real_prompts_v1` | MEASURED | KEY_FROZEN / VALUE_UNISSUED | DF, MINT, V5GEN, PANEL, WORKLOAD |
| `[F_1p7B_decode_operative_J]` | `max(F_1p7B_decode_abs_J, F_1p7B_decode_cmp_J)`; require exact equality with `floor_gate_j` | alpha / decode aggregate cell | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, MINT, V5GEN |
| `[F_8B_prefill_p[PREFILL_LENGTH]_abs_J]` | Aggregate floor artifact `d117-qwen3-8b-prefill-p[PREFILL_LENGTH]-floor-v5`, selected cell `floor_abs_j` | beta / prefill-p[PREFILL_LENGTH] absolute component | MEASURED | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; exact cell ID comes only from the generated floor pack | DF, MINT, V5GEN, G2A |
| `[F_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` | Same selected cell, `floor_cmp_j`; estimator identity must match its frozen registration | beta / prefill-p[PREFILL_LENGTH] comparative component | MEASURED | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, MINT, V5GEN, G2A |
| `[F_8B_prefill_p[PREFILL_LENGTH]_operative_J]` | `max(F_8B_prefill_p[PREFILL_LENGTH]_abs_J, F_8B_prefill_p[PREFILL_LENGTH]_cmp_J)`; require exact equality with `floor_gate_j` | beta / prefill-p[PREFILL_LENGTH] aggregate cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, MINT, V5GEN, G2A |
| `[F_8B_decode_abs_J]` | Aggregate floor artifact `d117-qwen3-8b-decode-floor-v5`, selected decode cell `floor_abs_j` | beta / decode absolute component; `real_prompts_v1` | MEASURED | KEY_FROZEN / VALUE_UNISSUED; prompt, tokenizer, template, and thinking pins must match V5-WL-001 through V5-WL-004 | DF, MINT, V5GEN, PANEL, WORKLOAD |
| `[F_8B_decode_cmp_J]` | Same selected decode cell, `floor_cmp_j`; estimator identity must match its frozen registration | beta / decode comparative component; `real_prompts_v1` | MEASURED | KEY_FROZEN / VALUE_UNISSUED | DF, MINT, V5GEN, PANEL, WORKLOAD |
| `[F_8B_decode_operative_J]` | `max(F_8B_decode_abs_J, F_8B_decode_cmp_J)`; require exact equality with `floor_gate_j` | beta / decode aggregate cell | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, MINT, V5GEN |

### Cell-label terms and D-165 attribution-dominance ratios

D-165 reversed ruling item 34. TERM A and TERM B remain reproducible because
the coded predicate survives as the cell label, but `TERM B > TERM A` is not
the paper's headline falsifier. For component \(j\), the retained label terms
are:

```text
A_unguarded_abs = max(max_abs_residual_j, prediction_component_j)
A_guarded_abs   = guard_factor * A_unguarded_abs

A_unguarded_cmp = max(max_abs_delta_j, prediction_component_j)
A_guarded_cmp   = guard_factor * A_unguarded_cmp
```

TERM B is the exact linear corner maximum used by that same component's code
predicate. Preserve the emitted array order and use `math.fsum` for \(W\):

```text
absolute:    n = cells[].absolute.n
             r_i = cells[].absolute.residuals_j[i]
             w_i = cells[].absolute.admissible_half_widths_j[i]
             W = math.fsum(w_i)
             B_abs = max_i(abs(r_i) + w_i*(n-1)/n + (W-w_i)/n)

comparative: d_i = cells[].comparative.block_deltas_j[i]
             w_i = cells[].comparative.admissible_half_widths_j[i]
             B_cmp = max_i(abs(d_i) + w_i)
```

The headline ratio is instead
`R = corner_widened_unguarded_floor_j / point_unguarded_floor_j`, evaluated
separately for the absolute and comparative component of every cell. The point
denominator is re-derived from unconditional parents as
`max(max_abs_residual_j, prediction_component_j)` for absolute or
`max(max_abs_delta_j, prediction_component_j)` for comparative. The numerator
is the complete emitted `corner_widened_unguarded_floor_j`, not TERM B and not
the guarded or drift-widened published floor. The gate is `R >= 2.0`; exact
equality passes. A zero denominator refuses with
`dominance_ratio_zero_denominator`. Every registered component in every cell
must pass; mixed outcomes are printed per component and use null framing.

Comparative R_cm is mandatory per cell. Its supplier is the registered
`d165_shared_sign_local_corner_replay.v2` rule over authenticated custodied
block inputs. R_cm is a shared-energy-sign/local-corner sensitivity diagnostic,
with no proven conservatism for common-time motion. `R_cm < 2.0` withdraws the
dominance sentence even if independent-corner R passed. A uniform additive
energy offset cancels from absolute residuals; a common time shift need not.
Absolute R_cm is `not_applicable` because the registered replay is
comparative-only, not because absolute timing uncertainty vanishes.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` | Alpha prefill absolute parents; guarded point-only label term | alpha / prefill-p[PREFILL_LENGTH] absolute label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_abs_J]` | Alpha prefill absolute arrays; exact legacy corner label formula above | alpha / prefill-p[PREFILL_LENGTH] absolute label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[R_1p7B_prefill_p[PREFILL_LENGTH]_abs]` | `cells[].absolute.corner_widened_unguarded_floor_j / max(max_abs_residual_j, prediction_component_j)` | alpha / prefill-p[PREFILL_LENGTH] absolute R column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN, G2A |
| `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_abs]` | Literal `not_applicable`: the registered replay is comparative-only, not a claim that absolute timing uncertainty vanishes | alpha / prefill-p[PREFILL_LENGTH] absolute R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / REGISTERED_NOT_APPLICABLE | D165, V5GEN, G2A |
| `[TERM_A_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` | Alpha prefill comparative parents; guarded point-only label term | alpha / prefill-p[PREFILL_LENGTH] comparative label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[TERM_B_1p7B_prefill_p[PREFILL_LENGTH]_cmp_J]` | Alpha prefill comparative arrays; exact legacy corner label formula above | alpha / prefill-p[PREFILL_LENGTH] comparative label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[R_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | `cells[].comparative.corner_widened_unguarded_floor_j / max(max_abs_delta_j, prediction_component_j)` | alpha / prefill-p[PREFILL_LENGTH] comparative R column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN, G2A |
| `[R_cm_1p7B_prefill_p[PREFILL_LENGTH]_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the alpha prefill cell's authenticated custodied block inputs | alpha / prefill-p[PREFILL_LENGTH] comparative R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN, G2A |
| `[TERM_A_1p7B_decode_abs_J]` | Alpha decode absolute parents; guarded point-only label term | alpha / decode absolute label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[TERM_B_1p7B_decode_abs_J]` | Alpha decode absolute arrays; exact legacy corner label formula above | alpha / decode absolute label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[R_1p7B_decode_abs]` | `cells[].absolute.corner_widened_unguarded_floor_j / max(max_abs_residual_j, prediction_component_j)` | alpha / decode absolute R column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN |
| `[R_cm_1p7B_decode_abs]` | Literal `not_applicable`: the registered replay is comparative-only, not a claim that absolute timing uncertainty vanishes | alpha / decode absolute R_cm column | DERIVE | REGISTERED_NOT_APPLICABLE | D165, V5GEN |
| `[TERM_A_1p7B_decode_cmp_J]` | Alpha decode comparative parents; guarded point-only label term | alpha / decode comparative label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[TERM_B_1p7B_decode_cmp_J]` | Alpha decode comparative arrays; exact legacy corner label formula above | alpha / decode comparative label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[R_1p7B_decode_cmp]` | `cells[].comparative.corner_widened_unguarded_floor_j / max(max_abs_delta_j, prediction_component_j)` | alpha / decode comparative R column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN |
| `[R_cm_1p7B_decode_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the alpha decode cell's authenticated custodied block inputs | alpha / decode comparative R_cm column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN |
| `[TERM_A_8B_prefill_p[PREFILL_LENGTH]_abs_J]` | Beta prefill absolute parents; guarded point-only label term | beta / prefill-p[PREFILL_LENGTH] absolute label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[TERM_B_8B_prefill_p[PREFILL_LENGTH]_abs_J]` | Beta prefill absolute arrays; exact legacy corner label formula above | beta / prefill-p[PREFILL_LENGTH] absolute label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[R_8B_prefill_p[PREFILL_LENGTH]_abs]` | `cells[].absolute.corner_widened_unguarded_floor_j / max(max_abs_residual_j, prediction_component_j)` | beta / prefill-p[PREFILL_LENGTH] absolute R column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN, G2A |
| `[R_cm_8B_prefill_p[PREFILL_LENGTH]_abs]` | Literal `not_applicable`: the registered replay is comparative-only, not a claim that absolute timing uncertainty vanishes | beta / prefill-p[PREFILL_LENGTH] absolute R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / REGISTERED_NOT_APPLICABLE | D165, V5GEN, G2A |
| `[TERM_A_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` | Beta prefill comparative parents; guarded point-only label term | beta / prefill-p[PREFILL_LENGTH] comparative label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[TERM_B_8B_prefill_p[PREFILL_LENGTH]_cmp_J]` | Beta prefill comparative arrays; exact legacy corner label formula above | beta / prefill-p[PREFILL_LENGTH] comparative label | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DF, V5GEN, G2A |
| `[R_8B_prefill_p[PREFILL_LENGTH]_cmp]` | `cells[].comparative.corner_widened_unguarded_floor_j / max(max_abs_delta_j, prediction_component_j)` | beta / prefill-p[PREFILL_LENGTH] comparative R column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN, G2A |
| `[R_cm_8B_prefill_p[PREFILL_LENGTH]_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the beta prefill cell's authenticated custodied block inputs | beta / prefill-p[PREFILL_LENGTH] comparative R_cm column | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN, G2A |
| `[TERM_A_8B_decode_abs_J]` | Beta decode absolute parents; guarded point-only label term | beta / decode absolute label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[TERM_B_8B_decode_abs_J]` | Beta decode absolute arrays; exact legacy corner label formula above | beta / decode absolute label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[R_8B_decode_abs]` | `cells[].absolute.corner_widened_unguarded_floor_j / max(max_abs_residual_j, prediction_component_j)` | beta / decode absolute R column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN |
| `[R_cm_8B_decode_abs]` | Literal `not_applicable`: the registered replay is comparative-only, not a claim that absolute timing uncertainty vanishes | beta / decode absolute R_cm column | DERIVE | REGISTERED_NOT_APPLICABLE | D165, V5GEN |
| `[TERM_A_8B_decode_cmp_J]` | Beta decode comparative parents; guarded point-only label term | beta / decode comparative label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[TERM_B_8B_decode_cmp_J]` | Beta decode comparative arrays; exact legacy corner label formula above | beta / decode comparative label | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | DF, V5GEN |
| `[R_8B_decode_cmp]` | `cells[].comparative.corner_widened_unguarded_floor_j / max(max_abs_delta_j, prediction_component_j)` | beta / decode comparative R column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; `>= 2.0`, equality passes | D165, DF, V5GEN |
| `[R_cm_8B_decode_cmp]` | Registered replay `d165_shared_sign_local_corner_replay.v2` over the beta decode cell's authenticated custodied block inputs | beta / decode comparative R_cm column | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; mandatory; `< 2.0` withdraws dominance sentence | D165, V5GEN |

### Protocol-first title and contingent subtitle (D-165)

The protocol-first title fixed before collection is **JouleWise: Timing
Sensitivity of Phase-Energy Assignments on Apple Silicon**. It does not branch
on the result. “Attribution-limited” may appear only as a gate-contingent subtitle after
every independent-corner component in every cell has `R >= 2.0` and no mandatory
comparative R_cm is below 2.0. A missing/refused R or R_cm does not select the
subtitle. The methods sentence must disclose this branch rule; `R_cm < 2.0`
withdraws the dominance sentence and the subtitle.

### Floor-cell branch text and diagnostics

For each row below, the cell selector must first validate both component
records exactly as the template requires. Generic absence or nullness is never
converted into a nonterminal no-exact-floor state.

D-166's exhausted-ladder branch is also exact. The prefill arm is collected at
4096 when no rung clears the count-at-least-five gate. If the reducer emits
`not_resolvable_sample_count` with count below 3, print that reducer refusal as
itself. If the reducer resolves at count 3 or 4, print the separate
pre-registration refusal “below the pre-registered count floor of 5” and
disclose the reducer's resolvable result alongside it. Never relabel one branch
as the other, and keep the Holm family at two.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERMINAL_REFUSAL_REASON_1p7B_prefill_p[PREFILL_LENGTH]]` | Conservative rendering of terminal codes from alpha prefill-p[PREFILL_LENGTH] extraction `cells[].refusal_reasons`, plus governing verdict failures | alpha / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; STOP_FILL on unknown code or malformed metadata | TPL, LINT, FX, WV, AUTH |
| `[TERMINAL_REFUSAL_REASON_1p7B_decode]` | Same source class for alpha decode | alpha / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL on invalid selector input | TPL, LINT, FX, WV, AUTH |
| `[TERMINAL_REFUSAL_REASON_8B_prefill_p[PREFILL_LENGTH]]` | Same source class for beta prefill-p[PREFILL_LENGTH] | beta / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; STOP_FILL on invalid selector input | TPL, LINT, FX, WV, AUTH |
| `[TERMINAL_REFUSAL_REASON_8B_decode]` | Same source class for beta decode | beta / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL on invalid selector input | TPL, LINT, FX, WV, AUTH |
| `[NO_EXACT_FLOOR_REASON_1p7B_prefill_p[PREFILL_LENGTH]]` | Renderer-normalized explanation from alpha prefill-p[PREFILL_LENGTH] component reports when the permitted exact-floor-unavailable state is proven | alpha / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[NO_EXACT_FLOOR_REASON_1p7B_decode]` | Same normalization for alpha decode | alpha / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[NO_EXACT_FLOOR_REASON_8B_prefill_p[PREFILL_LENGTH]]` | Same normalization for beta prefill-p[PREFILL_LENGTH] | beta / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[NO_EXACT_FLOOR_REASON_8B_decode]` | Same normalization for beta decode | beta / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p7B_prefill_p[PREFILL_LENGTH]]` | Fixed-order renderer over available alpha prefill-p[PREFILL_LENGTH] `floor_abs_j`, `floor_cmp_j`, and `point_floor_diagnostics` | alpha / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED; emit the template's no-diagnostic sentence if all are absent | TPL, DF, LINT |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p7B_decode]` | Same renderer for alpha decode | alpha / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_8B_prefill_p[PREFILL_LENGTH]]` | Same renderer for beta prefill-p[PREFILL_LENGTH] | beta / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | TPL, DF, LINT |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_8B_decode]` | Same renderer for beta decode | beta / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_1p7B_prefill_p[PREFILL_LENGTH]]` | Component-specific renderer over alpha prefill-p[PREFILL_LENGTH] `point_floor_diagnostics` entries; `published_claim_floor` must be false | alpha / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_1p7B_decode]` | Same renderer for alpha decode | alpha / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_8B_prefill_p[PREFILL_LENGTH]]` | Same renderer for beta prefill-p[PREFILL_LENGTH] | beta / prefill-p[PREFILL_LENGTH] cell | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_8B_decode]` | Same renderer for beta decode | beta / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[REFUSAL_REASON_1p7B_floor_window]` | Alpha whole-window verdict `status` with conservative rendering of `idle_admission_core.conditions` and `member_failures` | alpha / whole window | MEASURED | KEY_FROZEN / VERDICT_UNISSUED; never synthesize a passing value from extraction | TPL, WV, AUTH |
| `[REFUSAL_REASON_8B_floor_window]` | Beta whole-window verdict, same fields | beta / whole window | MEASURED | KEY_FROZEN / VERDICT_UNISSUED | TPL, WV, AUTH |

#### Terminal-refusal known-code set (F1 fold)

The conservative renderer's closed known-code set for
`[TERMINAL_REFUSAL_REASON_1p7B_prefill_p[PREFILL_LENGTH]]`,
`[TERMINAL_REFUSAL_REASON_1p7B_decode]`,
`[TERMINAL_REFUSAL_REASON_8B_prefill_p[PREFILL_LENGTH]]`,
`[TERMINAL_REFUSAL_REASON_8B_decode]`,
`[REFUSAL_REASON_1p7B_floor_window]`, and
`[REFUSAL_REASON_8B_floor_window]` includes these exact codes:

| Exact code | Producing source lines | Consumer reason registries |
|---|---|---|
| `capture_pipeline_absent` | `joulewise/uncertainty_evidence.py:1312`, `:1318`, `:1321` | `joulewise/floor_extraction.py:190`; `joulewise/whole_window.py:199` |
| `capture_pipeline_superseded` | `joulewise/uncertainty_evidence.py:1324` | `joulewise/floor_extraction.py:191`; `joulewise/whole_window.py:200` |

`CLAIM_BEARING_ANCHOR_METHODS` is defined at
`joulewise/uncertainty_evidence.py:1299`; the producer returns no refusal only
for a method in that set. Unknown codes still require `STOP_FILL`; these two
codes are no longer unknown.

### D-123 reported phase-energy cells

D-123 freezes the procedure and requires reader-facing phase-energy means from
alpha and beta. The current repository defines floor-cell `mean_j` internally,
but it does not define a reported-mean result schema, its admitted member basis,
its fully composed mean interval fields, or its runtime-observed per-token
companion fields. Substituting the absolute floor component's internal mean
would silently choose a basis and is forbidden.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | alpha / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; resolve by landing the alpha reported-mean schema and exact member basis | TPL, AUTH, FX |
| `[E_1p7B_prefill_p[PREFILL_LENGTH]_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | alpha / prefill-p[PREFILL_LENGTH] reported-mean interval | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; resolve in the D-123 extractor contract | TPL, AUTH |
| `[E_1p7B_prefill_p[PREFILL_LENGTH]_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | alpha / prefill-p[PREFILL_LENGTH] reported-mean interval | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; resolve in the D-123 extractor contract | TPL, AUTH |
| `[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_token]` | UNKNOWN — runtime-observed prompt-token companion field not yet defined | alpha / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; bind the denominator provenance in the D-123 output schema | TPL, AUTH |
| `[N_bundles_1p7B_prefill_p[PREFILL_LENGTH]]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | alpha / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |
| `[E_1p7B_decode_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; resolve by landing the alpha reported-mean schema and basis | TPL, AUTH, FX |
| `[E_1p7B_decode_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | alpha / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_1p7B_decode_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | alpha / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_1p7B_decode_J_per_token]` | UNKNOWN — runtime-observed output-token companion field not yet defined | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; denominator provenance must be authenticated | TPL, AUTH |
| `[N_bundles_1p7B_decode]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |
| `[E_8B_prefill_p[PREFILL_LENGTH]_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | beta / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; resolve by landing the beta reported-mean schema and basis | TPL, AUTH, FX |
| `[E_8B_prefill_p[PREFILL_LENGTH]_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | beta / prefill-p[PREFILL_LENGTH] reported-mean interval | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_8B_prefill_p[PREFILL_LENGTH]_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | beta / prefill-p[PREFILL_LENGTH] reported-mean interval | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_8B_prefill_p[PREFILL_LENGTH]_J_per_token]` | UNKNOWN — runtime-observed prompt-token companion field not yet defined | beta / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; denominator provenance must be authenticated | TPL, AUTH |
| `[N_bundles_8B_prefill_p[PREFILL_LENGTH]]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | beta / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |
| `[E_8B_decode_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; resolve by landing the beta reported-mean schema and basis | TPL, AUTH, FX |
| `[E_8B_decode_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | beta / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_8B_decode_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | beta / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_8B_decode_J_per_token]` | UNKNOWN — runtime-observed output-token companion field not yet defined | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; denominator provenance must be authenticated | TPL, AUTH |
| `[N_bundles_8B_decode]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |

### Gamma `_v5` contrasts

The decode rows bind the known generator identifier
`ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b`. The `_v5` generator also emits a
prefill contrast, but its identifier contains `[PREFILL_LENGTH]`; the frozen
draft has no exact professor-facing prefill token family. PG placement rows
therefore remain `STOP_FILL` and `UNRESOLVED-UNTIL-G2A` rather than receiving
guessed token names.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[E_decode_contrast_signed_J_per_request]` | `_v5` claim-verdict artifact `contrasts[contrast_id=ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b].estimator.estimate`; orientation is condition B minus condition A | gamma / decode contrast over `real_prompts_v1` | MEASURED | KEY_FROZEN / VALUE_UNISSUED | CV, V5GEN, PANEL, WORKLOAD |
| `[E_decode_contrast_lower_J]` | Same contrast, `deterministic_bounds.decision_interval.lower` | gamma / decode contrast | MEASURED | KEY_FROZEN / VALUE_UNISSUED | CV, V5GEN |
| `[E_decode_contrast_upper_J]` | Same contrast, `deterministic_bounds.decision_interval.upper` | gamma / decode contrast | MEASURED | KEY_FROZEN / VALUE_UNISSUED | CV, V5GEN |
| `[M_decode_contrast_abs_J_per_request]` | `abs(E_decode_contrast_signed_J_per_request)` | gamma / decode contrast | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL |
| `[F_claim_decode_armwise_max_J]` | `max(F_1p7B_decode_operative_J, F_8B_decode_operative_J)`; verify against the claim artifact's armwise floor gate | gamma consumer of alpha and beta decode floors | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL, DF, CV, MINT |
| `[B_decode_claim_J]` | NO SUPPLIER EXISTS. Do not assume that `deterministic_bounds.total` is the template's separately registered claim-side term. The deliberate `_supplier_unknown("[B_decode_claim_J]")` guard in `scripts/render_results_fills.py` remains correct. | gamma / decode claim interval | STOP_FILL | SUPPLIER_UNKNOWN; ruling item 33 expressly preserves this stop | TPL, CV, DF |
| `[C_decode_floor_clearance_J]` | `M_decode_contrast_abs_J_per_request - F_claim_decode_armwise_max_J`, only after floor-gate passage | gamma / decode contrast | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL |
| `[S_decode_floor_shortfall_J]` | `F_claim_decode_armwise_max_J - M_decode_contrast_abs_J_per_request`, only on floor-gate refusal | gamma / decode contrast | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL |
| `[R_decode_effect_x_floor]` | `M_decode_contrast_abs_J_per_request / F_claim_decode_armwise_max_J` | gamma / decode contrast | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; denominator must be exact and nonzero | TPL |
| `[S_decode_joint_J]` | `F_claim_decode_armwise_max_J + B_decode_claim_J`; disclosure only, never an acceptance gate | gamma / decode contrast | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; blocked while claim-bound supplier is unknown | TPL, DF |
| `[CELL_NONPUBLICATION_SUMMARY]` | Fixed-order summary of decode cells that selected terminal or no-exact-floor branches, using already-rendered reasons | gamma Section 7 variant selector | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, LINT |

#### Swap-block tokens (no landed template counterpart)

The two rows below are keyed on the `CONDITIONAL-INSERT-TIGHTER-FLOOR` block in
`docs/paper/draft-v1.md`, not on `DRAFT-RESULTS_PROSE.md`. They were added under
the magistrate ruling on sweep finding B7, which removed superseded-era numeric
literals from that block and required every value in it to arrive through this
registry. Their absence from the landed template vocabulary is a real gap and is
recorded here rather than papered over: the template must gain matching tokens
before the block is applied, or the block's sentences must be rewritten to use
tokens the template already defines.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[F_decode_contrast_cmp_two_edge_J]` | Prospective aggregate floor artifact, gamma decode comparative cell `floor_cmp_j`, admissible only when that cell's `estimator` registration names `d124_two_shared_edge_common_mode.v1` | gamma / decode comparative component under the registered two-shared-edge estimator | MEASURED | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL if the estimator registration is absent, names a different estimator, or the cell refused with `common_mode_nonseparable_window_domain`. No historical or superseded-era replay is a supplier | DRAFT, DF, MINT, AUTH |
| `[F_decode_contrast_cmp_worst_case_J]` | UNKNOWN binding. The mint issues one comparative floor per cell under the estimator that cell selected; no named output field carries a same-cell worst-case counterpart as a diagnostic alongside a two-shared-edge issuance | gamma / decode comparative component under the worst-case composition, quoted for contrast only | STOP_FILL | SUPPLIER_UNKNOWN; resolve by naming a diagnostic output field that carries the worst-case composition for an already-issued two-shared-edge cell, or drop the comparison clause from the swap block | DRAFT, DF, MINT |

### Characterization campaign

The characterization tokens are now bound.
`configs/campaigns/metrology_v1/characterization_result_schema_v1.json` is the
frozen characterization result specification and
`docs/contracts/characterization_result_schema_v1.md` is its normative prose
contract. Between them they name one producing field, in an issued
characterization report, for every token in the table below. The 2026-08-22
finding that no repository file in the authority set defined a characterization
result schema or these output field paths is therefore retired.

Each field path below is copied verbatim from the specification's
`render_map.rows` object, which is the specification's own token-to-field map.
A path reads `rows.<row identifier>.<container>.<field>`. The issued report
carries one entry per public row under the six frozen row identifiers
`linearity`, `null`, `empirical_floor`, `phase_attribution`, `drift_settling`,
and `between_sessions`. Within a row entry, `observed_values` holds the values a
row publishes when its window passed, `diagnostics` holds the values a refused
window may still publish, `diagnostic_present` is the boolean that licenses the
diagnostic clause, and `row_outcome` holds the row's single outcome word.

Three plain-language tokens are spelled differently from the row they read:
`[PLAIN_LANGUAGE_RESULT_floor]` reads row `empirical_floor`,
`[PLAIN_LANGUAGE_RESULT_phase]` reads row `phase_attribution`, and
`[PLAIN_LANGUAGE_RESULT_drift]` reads row `drift_settling`. The specification
writes that crosswalk out in `render_map.rows` instead of leaving a renderer to
infer it, and the rows below cite it the same way.

No characterization report has been issued. Every fill in this section
therefore still stops. The rows are `KEY_FROZEN / VALUE_UNISSUED`: the
producing field name is fixed, and no value may be inserted. No row here moves
to a fillable state until an authenticated report exists.

Fail-closed carry-over is unchanged. A missing report, an unrecognized refusal
reason code, or a failed hash predicate is `STOP_FILL`. The specification's
`characterization_*` reason codes are a closed, non-overlapping set: a code
outside that set stops rendering until it is registered here, exactly as the
terminal-refusal rule above requires.

| Exact token | Producing field in the issued characterization report | Campaign / row | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[S_C_linearity_request_J_per_token]` | `rows.linearity.observed_values.request_slope_j_per_token`; fitted gross-request slope | characterization / linearity | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[S_C_linearity_decode_J_per_token]` | `rows.linearity.observed_values.decode_slope_j_per_token`; fitted token-generation slope | characterization / linearity | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[R_C_linearity_limit_J]` | `rows.linearity.observed_values.applied_residual_limit_j`; the binding residual limb, not one of the two limbs on its own | characterization / linearity | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; the derivation is PROPOSED below and awaits lead ratification | TPL, DRAFT, SPEC |
| `[D_C_null_max_abs_J]` | `rows.null.observed_values.max_abs_block_delta_j`; largest authenticated absolute ABBA block difference | characterization / null response | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[R_C_micro_min_x_floor]` | `rows.empirical_floor.observed_values.min_effect_to_floor_ratio` | characterization / empirical floor | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[R_C_micro_max_x_floor]` | `rows.empirical_floor.observed_values.max_effect_to_floor_ratio` | characterization / empirical floor | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[D_C_additivity_J]` | `rows.phase_attribution.observed_values.max_abs_additivity_residual_j`; registered phase-sum minus enclosing-request residual | characterization / phase attribution | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[S_C_prompt_invariance_J_per_token]` | `rows.phase_attribution.observed_values.prefill_slope_j_per_token`; fitted prompt-processing slope against later output length | characterization / phase attribution | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[B_C_prompt_invariance_J_per_token]` | `rows.phase_attribution.observed_values.applied_invariance_band_j_per_token`; the binding invariance limb | characterization / phase attribution | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; the derivation is PROPOSED below and awaits lead ratification | TPL, DRAFT, SPEC |
| `[D_C_reference_excursion_J]` | `rows.drift_settling.observed_values.max_heldout_excursion_j`; largest held-out reference-probe deviation | characterization / drift and settling | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[T_C_recovery_s]` | `rows.drift_settling.observed_values.max_recovery_s` | characterization / drift and settling | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued | TPL, DRAFT, SPEC |
| `[N_C_eligible_sessions]` | `rows.between_sessions.observed_values.eligible_session_count`, counted by the specification's `eligibility_predicate` | characterization / between sessions | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; a refused window contributes nothing | TPL, DRAFT, SPEC |
| `[PLAIN_LANGUAGE_RESULT_linearity]` | `rows.linearity.row_outcome`, rendered through `render_map.outcome_phrases` | characterization / linearity | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only through `render_map.outcome_phrases`, whose four phrases are the closed set; the pending-eligibility phrase is available to the between-sessions row alone | TPL, LINT, SPEC |
| `[PLAIN_LANGUAGE_RESULT_null]` | `rows.null.row_outcome`, rendered through `render_map.outcome_phrases` | characterization / null response | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only through `render_map.outcome_phrases`, whose four phrases are the closed set; the pending-eligibility phrase is available to the between-sessions row alone | TPL, LINT, SPEC |
| `[PLAIN_LANGUAGE_RESULT_floor]` | `rows.empirical_floor.row_outcome`, rendered through `render_map.outcome_phrases` | characterization / empirical floor | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only through `render_map.outcome_phrases`, whose four phrases are the closed set; the pending-eligibility phrase is available to the between-sessions row alone | TPL, LINT, SPEC |
| `[PLAIN_LANGUAGE_RESULT_phase]` | `rows.phase_attribution.row_outcome`, rendered through `render_map.outcome_phrases` | characterization / phase attribution | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only through `render_map.outcome_phrases`, whose four phrases are the closed set; the pending-eligibility phrase is available to the between-sessions row alone | TPL, LINT, SPEC |
| `[PLAIN_LANGUAGE_RESULT_drift]` | `rows.drift_settling.row_outcome`, rendered through `render_map.outcome_phrases` | characterization / drift and settling | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only through `render_map.outcome_phrases`, whose four phrases are the closed set; the pending-eligibility phrase is available to the between-sessions row alone | TPL, LINT, SPEC |
| `[PLAIN_LANGUAGE_RESULT_between_sessions]` | `rows.between_sessions.row_outcome`, rendered through `render_map.outcome_phrases` | characterization / between sessions | DERIVE | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only through `render_map.outcome_phrases`, whose four phrases are the closed set; the pending-eligibility phrase is available to the between-sessions row alone | TPL, LINT, SPEC |
| `[REFUSAL_REASON_window_C]` | Characterization whole-window verdict `status`, `idle_admission_core.conditions`, and `member_failures`, once an exact verdict basis is issued; the specification binds the same verdict at `render_map.selector_atoms.whole_window_verdict` | characterization / whole window | MEASURED | KEY_FROZEN / VERDICT_UNISSUED | TPL, WV, AUTH, SPEC |
| `[D_C_linearity_diagnostic_J_per_token]` | `rows.linearity.diagnostics.decode_slope_j_per_token`; a refused-window diagnostic | characterization / linearity diagnostic | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only when `rows.linearity.diagnostic_present` is true, and absence renders nothing | TPL, LINT, SPEC |
| `[D_C_null_diagnostic_J]` | `rows.null.diagnostics.max_abs_block_delta_j`; a refused-window diagnostic | characterization / null diagnostic | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only when `rows.null.diagnostic_present` is true, and absence renders nothing | TPL, LINT, SPEC |
| `[D_C_micro_diagnostic_x_floor]` | `rows.empirical_floor.diagnostics.effect_to_floor_ratio`; a refused-window diagnostic | characterization / empirical-floor diagnostic | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only when `rows.empirical_floor.diagnostic_present` is true, and absence renders nothing | TPL, LINT, SPEC |
| `[D_C_phase_diagnostic_J]` | `rows.phase_attribution.diagnostics.max_abs_additivity_residual_j`; a refused-window diagnostic | characterization / phase diagnostic | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only when `rows.phase_attribution.diagnostic_present` is true, and absence renders nothing | TPL, LINT, SPEC |
| `[D_C_drift_diagnostic_J]` | `rows.drift_settling.diagnostics.max_heldout_excursion_j`; a refused-window diagnostic | characterization / drift diagnostic | MEASURED | KEY_FROZEN / VALUE_UNISSUED; the producing field is named, no characterization report has been issued; renders only when `rows.drift_settling.diagnostic_present` is true, and absence renders nothing | TPL, LINT, SPEC |

#### The two limit tokens print a limit, not an observation (PROPOSED)

Two tokens in the table above print a *limit* — the value the row's observation
had to stay inside — rather than an observation of the instrument.
`[R_C_linearity_limit_J]` prints the residual limit of the workload-response
sentence; `[B_C_prompt_invariance_J_per_token]` prints the acceptance band of
the prompt-invariance sentence.

The ratified design gives each of those two properties **two limbs**, and the
row passes only if the observation stays inside both:

- a **resolution limb** — the limit set by what one admitted measurement can
  resolve. For linearity this is `H`, the largest half-width any single
  admitted bundle's authenticated energy interval carries for that metric
  (specification criteria C1.4 and C1.6). For prompt invariance it is `L_H`,
  the largest admitted prompt-processing energy half-width divided by the
  registered output-token span, the difference between the largest and smallest
  registered output-token counts (criterion C4.2a).
- a **claim-anchored limb** — the limit set by an independently issued floor
  for the matching cell, from a window frozen strictly earlier than the
  characterization freeze, never from the characterization window's own data.
  For linearity this is `F_operative` (criteria C1.5 and C1.7). For prompt
  invariance it is `L_F`, that same-cell prompt-processing floor divided by the
  same output-token span (criterion C4.2b).

Each template sentence has room for one number. The specification therefore
publishes the **binding** limb — the stricter of the two when both are
available, and the sole available limb otherwise — in one field per property,
and writes the rule into `render_map.derived_value_rules` so no renderer infers
it:

- `[R_C_linearity_limit_J]` takes `min(H, F_operative)`, published as
  `rows.linearity.observed_values.applied_residual_limit_j`.
- `[B_C_prompt_invariance_J_per_token]` takes `min(L_H, L_F)`, published as
  `rows.phase_attribution.observed_values.applied_invariance_band_j_per_token`.

Nothing is hidden by printing one limb. Both limbs stay separately reported per
criterion in `rows[].criteria[].limit_applied` of the same issued report.

Worked case, in symbols because this registry prints no numbers: when a
window's issued same-cell operative floor is smaller than that window's largest
admitted timing half-width, `F_operative` is the stricter limb and is what the
sentence prints, so the residual had to clear the tighter of the two tests. When
no same-cell floor was issued before the characterization freeze, criteria C1.5
and C1.7 return no conclusion under the reason code
`characterization_operative_floor_unavailable` — D-152 ruled that the
claim-anchored limb has no absolute fallback — the row itself returns no
conclusion, and the only limit the report can carry is the sole available limb,
`H`.

**Status: PROPOSED; the lead ratifies or replaces it.** This is the single
place where the specification had to choose what a one-limit template sentence
prints for a two-limb criterion. Until it is ratified, the two rows above carry
the derivation and no value, and no fill is authorized under either outcome.

#### The Variant-B prompt-invariance band (resolved)

`[B_C_prompt_invariance_J_per_token]` occurred in Section 6 Variant A only.
Variant B's phase-attribution sentence printed the observed prompt-processing
slope with no band beside it, so a Variant-B reader could not tell whether that
slope sat inside the registered limit or outside it. This revision adds the band
to the Variant-B present-branch sentence and to the linter's
`phase_attribution` row tuple, so both variants print slope and band together.
The specification publishes the band either way. The alternative on offer —
recording Variant B as slope-only by design — was rejected because it prints a
number the reader has no way to judge.

### Diagnostic-era value custody (Addendum 3 item 38)

Addendum 3 item 38 ruled that every diagnostic-era value in the draft is traced to an
actual artifact path or becomes a registered `[PENDING]` with the diagnostic-era label:
no number stands on seat prose. A sweep of all 101 diagnostic numeric value-sites in the
draft traced 98, left one (DG-097) narrowed to what its source supports, and converted 2.
The two conversions are the Section 6 resolvability example's width and spacing
descriptions. Reviewer synthesis C7 required a declared statistic; the round-7
resolvability projection then corrected the old mechanism: 328,522 retained
records tile with no meaningful gap, so spacing and width are the same
record-period distribution rather than quantities separated by sampler pauses.
The old 111.8–112.5 ms observation is the bottom of the cited bundle's width
distribution, not its range. PR #276 subsequently issued the ratified summary
family for both rows in `docs/paper/round7/dg071-dg075-statistics.md` (SHA-256
`041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b`) and
`docs/paper/round7/dg071-dg075-statistics.json` (SHA-256
`9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7`).

Path abbreviations below are exact:

- C = /Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json
- E = /Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/events.jsonl
- P = /Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/raw/powermetrics.plist
- R4 = docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json, array member member_id=20260722T145535-e941c821
- XS = configs/floor_mint/a10_extraction_spec.json
- A10 = /Users/edr/code/JouleWise/runs_window_a10_20260725/{member}/summary_metrics.json, where {member} is each exact XS cells[0..2].members[*].bundle_id
- S17 = configs/calibration/calibration_acceptance_d079_v2_n17_r3.json
- S19 = configs/calibration/calibration_acceptance_d079_v2_r2.json
- NR = docs/process_traces/2026-08-09-prefill-phase-proof/results.json
- R03E = /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/events.jsonl
- R03P = /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv
- AB = /Users/edr/code/JouleWise/runs_window_contrast_20260730/swdec-contrast-b{01..10}-{a1,a2,b1,b2}/summary_metrics.json
- ABC = /Users/edr/code/JouleWise/runs_window_contrast_20260730/swdec-contrast-b{01..10}-{a1,a2,b1,b2}/config.json
- DL = docs/decision_log.md, D-122 and its retained sizing record
- DF = joulewise/detection_floor.py, guarded point diagnostic and absolute_false_effect_floor/corner computation
- RF = scripts/check_paper_replay_fence.py
- PROJ = docs/paper/round7/prefill-resolvability-projection.md, especially Sections 4 and 11
- SYN = docs/process_traces/2026-08-28-reviewer-panel/04-SYNTHESIS.md, C7

#### Rows

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DG-001 — Abstract diagnostic scale, line 11 | about 1 J | A10/p2015-df-ph-prefill-abs-r01#energy_anchor_shift_envelopes[/phase_energy_j/prefill].max_abs_delta_j; descriptive about-one rendering | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-002 — Section 2 pre_spawn wall, line 69 | 1784757335.502742 | C#clock_anchor.clock_stamps.pre_spawn.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-003 — Section 2 pre_spawn mono-before, line 69 | 458736.4081875 | C#clock_anchor.clock_stamps.pre_spawn.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-004 — Section 2 pre_spawn mono-after, line 69 | 458736.408188666 | C#clock_anchor.clock_stamps.pre_spawn.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-005 — Section 2 pre_spawn R, line 69 | 0.0000010000000000000002 | max(C#...pre_spawn.wall_resolution_s, C#...pre_spawn.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-006 — Section 2 first_parse wall, line 70 | 1784757336.604396 | C#clock_anchor.clock_stamps.first_parse.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-007 — Section 2 first_parse mono-before, line 70 | 458737.509839458 | C#clock_anchor.clock_stamps.first_parse.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-008 — Section 2 first_parse mono-after, line 70 | 458737.509840291 | C#clock_anchor.clock_stamps.first_parse.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-009 — Section 2 first_parse R, line 70 | 0.0000010000000000000002 | max(C#...first_parse.wall_resolution_s, C#...first_parse.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-010 — Section 2 sampling_started wall, line 71 | 1784757337.0900722 | C#clock_anchor.clock_stamps.sampling_started.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-011 — Section 2 sampling_started mono-before, line 71 | 458737.995513416 | C#clock_anchor.clock_stamps.sampling_started.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-012 — Section 2 sampling_started mono-after, line 71 | 458737.995514666 | C#clock_anchor.clock_stamps.sampling_started.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-013 — Section 2 sampling_started R, line 71 | 0.0000010000000000000002 | max(C#...sampling_started.wall_resolution_s, C#...sampling_started.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-014 — Section 2 sampling_stopped wall, line 72 | 1784757533.877846 | C#clock_anchor.clock_stamps.sampling_stopped.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-015 — Section 2 sampling_stopped mono-before, line 72 | 458934.782846541 | C#clock_anchor.clock_stamps.sampling_stopped.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-016 — Section 2 sampling_stopped mono-after, line 72 | 458934.782848041 | C#clock_anchor.clock_stamps.sampling_stopped.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-017 — Section 2 sampling_stopped R, line 72 | 0.0000010000000000000002 | max(C#...sampling_stopped.wall_resolution_s, C#...sampling_stopped.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-018 — Section 2 post_parse wall, line 73 | 1784757533.8891652 | C#clock_anchor.clock_stamps.post_parse.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-019 — Section 2 post_parse mono-before, line 73 | 458934.794166 | C#clock_anchor.clock_stamps.post_parse.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-020 — Section 2 post_parse mono-after, line 73 | 458934.7941665 | C#clock_anchor.clock_stamps.post_parse.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-021 — Section 2 post_parse R, line 73 | 0.0000010000000000000002 | max(C#...post_parse.wall_resolution_s, C#...post_parse.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-022 — Section 2 wall resolution, line 75 | 1.0000000000000002×10^-6 s | C#clock_anchor.clock_stamps.*.wall_resolution_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-023 — Section 2 monotonic resolution, line 75 | 4.166666666666666×10^-8 s | C#clock_anchor.clock_stamps.*.monotonic_resolution_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-024 — Section 2 detected-pulse count, line 79 | 59 | R4#pulse_count with all_pulses_detected=true; RF replays P+E | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-025 — Section 2 rectangle count, line 79 | 122,859 | R4#projection_evaluated_cell_count; RF replays P+E | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-026 — Section 2 local anchor, line 79 | 0.0011349971959968978 s | R4#anchor_v3.effective_clock_anchor_bound_s; RF replays C+P | retained 20260722 capture / anchor | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-027 — Section 2 final capture bound, line 79 | 0.030067931757111657 s | R4#b_fiducial_v3_s; RF replays P+E+C | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-028 — Section 2 capture-bound arithmetic operand, line 79 | 0.030067931757111657 | same R4#b_fiducial_v3_s | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-029 — Section 2 anchor arithmetic operand, line 79 | 0.0011349971959968978 | same R4#anchor_v3.effective_clock_anchor_bound_s | retained 20260722 capture / anchor | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-030 — Section 2 residual subtraction, line 79 | 0.0289329345611147592 s | R4#b_fiducial_v3_s - R4#anchor_v3.effective_clock_anchor_bound_s, decimal rendering fixed by RF | retained 20260722 capture / pulse fit | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-031 — Section 2 maximal-pulse ordinal, line 79 | tenth | argmax over RF-replayed retained pulse endpoints from P+E+C; render index 9 as tenth | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-032 — Section 2 pulse-on plan offset, line 79 | 26.625 s | E#pulse_command_on occurrence 10.metadata.planned_on_offset_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-033 — Section 2 pulse-off plan offset, line 79 | 27.625 s | E#pulse_command_off occurrence 10.metadata.planned_off_offset_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-034 — Section 2 pulse-on epoch, line 79 | 1784757381.2856488 s | E#pulse_command_on occurrence 10.metadata.clock_stamp.epoch_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-035 — Section 2 pulse-off epoch, line 79 | 1784757382.293089 s | E#pulse_command_off occurrence 10.metadata.clock_stamp.epoch_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-036 — Section 2 onset lower, line 79 | 0.02544938965763524 s | RF replay P+E+C, pulse 10 retained onset residual lower endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-037 — Section 2 onset upper, line 79 | 0.02893293456111476 s | RF replay P+E+C, pulse 10 retained onset residual upper endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-038 — Section 2 offset lower, line 79 | -0.008607394549133255 s | RF replay P+E+C, pulse 10 retained offset residual lower endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-039 — Section 2 offset upper, line 79 | -0.005308621075866744 s | RF replay P+E+C, pulse 10 retained offset residual upper endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-040 — Section 2 best-fit onset, line 79 | +0.027 s | RF replay P+E+C pulse 10 best delta_on; round 3 decimals | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-041 — Section 2 best-fit offset, line 79 | -0.007 s | RF replay P+E+C pulse 10 best delta_off; round 3 decimals | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-042 — Section 2 pulse residual bound, line 79 | 0.02893293456111476 s | max absolute value of DG-036 through DG-039 | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-043 — Section 3 retained-cell count, line 103 | three | len(XS#cells[0..2]) | historical a10 / three absolute cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-044 — Section 3 prefill point floor, line 103 | 0.2888 | A10 prefill members + DF guarded point-only computation; round 4 decimals | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-045 — Section 3 decode point floor, line 103 | 0.4934 | A10 decode members + DF guarded point-only computation; round 4 decimals | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-046 — Section 3 short-prefill point floor, line 103 | 0.3113 J | A10 short-prefill members + DF guarded point-only computation; round 4 decimals | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-047 — Section 3 prefill corner floor, line 103 | 3.153 | A10 prefill members + DF corner_widened_guarded_floor_j; round 3 decimals | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-048 — Section 3 decode corner floor, line 103 | 2.922 | A10 decode members + DF corner_widened_guarded_floor_j; round 3 decimals | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-049 — Section 3 short-prefill corner floor, line 103 | 2.184 J | A10 short-prefill members + DF corner_widened_guarded_floor_j; round 3 decimals | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-050 — Section 3 prefill ratio, line 103 | 10.92 | unrounded DG-047 / unrounded DG-044; round 2 decimals | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-051 — Section 3 decode ratio, line 103 | 5.92 | unrounded DG-048 / unrounded DG-045; round 2 decimals | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-052 — Section 3 short-prefill ratio, line 103 | 7.02 | unrounded DG-049 / unrounded DG-046; round 2 decimals | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-053 — Section 3 timing minimum, line 105 | 25.6 ms | min A10 members#energy_anchor_shift_envelopes[*].anchor_bound_s = 0.025619527535021 at decode r03; ×1000, round 1 decimal | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-054 — Section 3 timing maximum, line 105 | 31.1 ms | max same 30 fields = 0.031073829369128 at prefill r01; ×1000, round 1 decimal | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-055 — Section 3 timing-member count, line 105 | n=30 | sum len(XS#cells[0..2].members) | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-056 — Section 3 repeated timing-member count, line 105 | not 30 independent timing draws | same XS member-count derivation as DG-055 | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-057 — Section 2 drift refusal screen, line 51 | 10.164835 ms | S17#decimal_derivation.ratified_operatives.maximum_budgetable_drift_s ×1000; round 6 decimals | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-058 — Section 2 bracket formula screen, line 51 | 9.724 ms | S17#decimal_derivation.ratified_operatives.bracket_screen_s ×1000 | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-059 — Section 2 named current screen, line 51 | 9.724 ms | same S17 bracket_screen_s | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-060 — Section 4 screen in seconds, line 161 | 0.009724 s | S17#decimal_derivation.ratified_operatives.bracket_screen_s | diagnostic calibration / n17 | MEASURED | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-061 — Section 4 screen reference, line 164 | 9.724-ms | S17#decimal_derivation.ratified_operatives.bracket_screen_s ×1000 | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-062 — Section 4 repeated screen, line 164 | 9.724 ms | same S17 bracket_screen_s ×1000 | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-063 — RETIRED (ruling item 58): Section 4 superseded 10.818 ms screen; the sentence was removed by item 32 and the value no longer appears in the draft | 10.818 ms (superseded; not in draft) | S19#decimal_derivation.ratified_operatives.bracket_screen_s ×1000 | diagnostic calibration / n19 superseded | DERIVE | RETIRED / SUPERSEDED_ISSUED_CONFIG; NON_CLAIM_BEARING | RETIRED |
| DG-064 — Section 4 superseded corpus count, line 164 | nineteen | S19#derivation_corpus.n | diagnostic calibration / n19 superseded | MEASURED | DIAGNOSTIC_ERA / SUPERSEDED_ISSUED_CONFIG; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-065 — Section 4 current corpus count, line 164 | seventeen | S17#derivation_corpus.n | diagnostic calibration / n17 | MEASURED | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-066 — Section 6 diagnostic population, line 247 | 50 | NR#stack_summaries[stack=1.5B].bundle_count | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-067 — Section 6 diagnostic failures, line 247 | 37 | NR#stack_summaries[stack=1.5B].resolvability.not_resolvable_sample_count | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-068 — Section 6 repeated population denominator, line 247 | 50 | same NR#bundle_count | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-069 — Section 6 diagnostic passes, line 247 | 13 | NR#stack_summaries[stack=1.5B].resolvability.identifiable | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-070 — Section 6 concrete prefill duration, line 256 | 0.121034145 s | NR#bundles[bundle=p2015-df-ph-decode-abs-r03].boundary.prefill_duration_s; verify R03E phase_end - phase_start; round 9 decimals | historical a10 / decode-abs-r03 prefill | DERIVE | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-071 — Section 6 sampling-record interval width, line 256 | n = 406; median 120.9186 ms; IQR 5.9508 ms | `docs/paper/round7/dg071-dg075-statistics.json#statistics.DG-071`, issued with `docs/paper/round7/dg071-dg075-statistics.md`; JSON SHA-256 `9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7`; Markdown SHA-256 `041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b`. Median with IQR of `interval_end_s - interval_start_s` over every retained record in R03P; render milliseconds to four decimals exactly as issued. | historical a10 diagnostic / resolvability example | ISSUED | RATIFIED-STATISTIC (magistrate 2026-08-31, `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`) / ISSUED_ARTIFACT (PR #276); DIAGNOSTIC_ERA; NON_CLAIM_BEARING | DRAFT, DF, PROJ, SYN |
| DG-072 — Section 6 two-overlap count, line 256 | two; 2 | NR#bundles[...r03].power.prefill_overlap_sample_count and NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[2] | historical a10 / r03 and population | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-073 — Section 6 three-sample threshold/count, line 256 | three; 3 | NR#bundles[...r03].resolvability.minimum_samples and NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[3] | historical a10 / r03 and population | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-074 — Section 6 rounded duration operand, line 256 | 0.121 | round NR r03 boundary.prefill_duration_s to 3 decimals | historical a10 / decode-abs-r03 prefill | DERIVE | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-075 — Section 6 record spacing, line 256 | n = 405; median 120.9224 ms; IQR 5.8949 ms | `docs/paper/round7/dg071-dg075-statistics.json#statistics.DG-075`, issued with `docs/paper/round7/dg071-dg075-statistics.md`; JSON SHA-256 `9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7`; Markdown SHA-256 `041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b`. Median with IQR of consecutive unique `timestamp_s` differences over R03P; render milliseconds to four decimals exactly as issued. The records tile with no sampler pause, so this is the DG-071 record-period distribution minus the first record, apart from the issued endpoint convention. | historical a10 diagnostic / resolvability example | ISSUED | RATIFIED-STATISTIC (magistrate 2026-08-31, `docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`) / ISSUED_ARTIFACT (PR #276); DIAGNOSTIC_ERA; NON_CLAIM_BEARING | DRAFT, DF, PROJ, SYN |
| DG-076 — Section 6 population with two overlaps, line 256 | 37 | NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[2] | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-077 — Section 6 population with three overlaps, line 256 | 13 | NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[3] | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-078 — Section 6 historical ABBA block count, line 268 | Ten | count AB block indices b01 through b10, each with a1,a2,b1,b2 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-079 — Section 6 historical prompt size, line 268 | 128-token | ABC#workload_profile.prompt_tokens for all 40 members | historical contrast / prefill | MEASURED | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-080 — Section 6 historical ABBA mean, line 268 | 5.809930 J | mean b01..b10 of (AB b1.prefill + b2.prefill - a1.prefill - a2.prefill)/2 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-081 — Section 6 projected prompt target, line 270 | 256 | DL#D-122 prospective prompt-processing target | prospective gamma / prefill sizing | MEASURED | DESIGN_FROZEN; PROJECTION_ONLY | DRAFT, AUTH |
| DG-082 — Section 6 historical denominator prompt, line 270 | 128 | ABC#workload_profile.prompt_tokens | historical contrast / prefill | MEASURED | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-083 — Section 6 repeated historical mean, line 270 | 5.809930 | same AB mean derivation as DG-080 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-084 — Section 6 projected effect, line 270 | 11.619860 J | (256/128) × unrounded DG-080 | prospective gamma / prefill sizing | DERIVE | DIAGNOSTIC_ERA INPUT / PROJECTION_ONLY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-085 — Section 6 approximate planning bar, line 272 | approximately 5 J | DL D-122 retained practical bar; copy only as approximate; exact components remain pending | prospective gamma / prefill sizing | MEASURED | ISSUED_APPROXIMATION; SIZING_ONLY | DRAFT, AUTH |
| DG-086 — Section 6 128-token clearance label, line 272 | 128-token | ABC#workload_profile.prompt_tokens | historical contrast / prefill | MEASURED | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-087 — Section 6 128-clearance estimate operand, line 272 | 5.809930 | same AB mean derivation as DG-080 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-088 — Section 6 128-clearance bar operand, line 272 | 5 | same DL approximate bar as DG-085 | prospective gamma / prefill sizing | MEASURED | ISSUED_APPROXIMATION; SIZING_ONLY | DRAFT, AUTH |
| DG-089 — Section 6 128-clearance result, line 272 | 0.809930 J | DG-087 - DG-088 | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-090 — Section 6 128 ratio, line 272 | 1.16 | unrounded DG-080 / 5; round 2 decimals | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-091 — Section 6 256-token clearance label, line 272 | 256-token | same DL D-122 target as DG-081 | prospective gamma / prefill sizing | MEASURED | DESIGN_FROZEN; PROJECTION_ONLY | DRAFT, AUTH |
| DG-092 — Section 6 256-clearance estimate operand, line 272 | 11.619860 | DG-084 | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-093 — Section 6 256-clearance bar operand, line 272 | 5 | same DL approximate bar as DG-085 | prospective gamma / prefill sizing | MEASURED | ISSUED_APPROXIMATION; SIZING_ONLY | DRAFT, AUTH |
| DG-094 — Section 6 256-clearance result, line 272 | 6.619860 J | DG-092 - DG-093 | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-095 — Section 6 256 ratio, line 272 | 2.32 | unrounded DG-084 / 5; round 2 decimals | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-096 — Section 6 selected prompt size, line 272 | 256 | same DL D-122 target as DG-081 | prospective gamma / prefill sizing | MEASURED | DESIGN_FROZEN; PROJECTION_ONLY | DRAFT, AUTH |
| DG-097 — Section 6 historical prompt ceiling, line 272 | 128 | max ABC#workload_profile.prompt_tokens; no 7B corpus above 128 tokens AMONG THE 40 CONTRAST CONFIGURATIONS named by ABC (narrowed by Addendum 4 item 43; the 40 configs cannot establish absence across all historical corpora, and no inventory is commissioned) | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-098 — Section 7 repeated retained-cell count, line 298 | three | len(XS#cells[0..2]) | historical a10 / three absolute cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-099 — Section 7 repeated prefill ratio, line 298 | 10.92 | same derivation as DG-050 | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-100 — Section 7 repeated decode ratio, line 298 | 5.92 | same derivation as DG-051 | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-101 — Section 7 repeated short-prefill ratio, line 298 | 7.02 | same derivation as DG-052 | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |

#### Appendix worked-continuation bindings (Addendum 5 item 50)

The 26 rows below enumerate every numeric value-site in the A.3.3 worked anchor
block at lines 549–557 and the A.3.6 worked example at line 650. The capture ID,
the A.3.3 section locator, and the word `binary64` are identifiers rather than
numeric value-sites and remain outside the value census. All 26 value-sites
trace to C or R4 through the exact field or arithmetic stated below; there is no
untraced gap in this continuation.

The replay fence covers Section 2 only. It does not parse or compare either
appendix site. A row marked `VALUE ALREADY REPLAY-FENCED VIA SECTION 2` states a
value that Section 2 already places under RF, but the appendix occurrence is
still bound only by this registry. Every other row is appendix-only and bound
only here. For RF to cover the appendix continuation too, it would have to add
unique, fail-closed extractors for the A.3.3 and A.3.6 anchors, re-derive and
compare all 26 direct and arithmetic values (including their stated rounding),
and increase its expected comparison census above 43; its tests would have to
pin that expanded census. No fence or test change is made by this registration.

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DG-102 — Appendix A.3.3 lower anchor endpoint, line 549 | 1784757336.5519202 s | R4#anchor_v3.anchor_lower_epoch_s | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-103 — Appendix A.3.3 upper anchor endpoint, line 549 | 1784757336.5532944 s | R4#anchor_v3.anchor_upper_epoch_s | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-104 — Appendix A.3.3 point anchor, line 549 | 1784757336.5526073 s | R4#anchor_v3.first_sample_end_point_epoch_s | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-105 — Appendix A.3.3 exact half-width term, line 551 | 0.0006869160344978743 | R4#anchor_v3.anchor_only_bound_s | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-106 — Appendix A.3.3 wall-minus-monotonic span, line 552 | 0.00044608116149902344 | R4#anchor_v3.wall_minus_monotonic_span_s | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-107 — Appendix A.3.3 maximum stamp resolution, line 553 | 0.0000010000000000000002 | R4#anchor_v3.stamp_resolution_s; same value RF re-derives from C#clock_anchor.clock_stamps in Section 2 | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / VALUE ALREADY REPLAY-FENCED VIA SECTION 2; APPENDIX OCCURRENCE REGISTRY_BOUND | DRAFT, AUTH |
| DG-108 — Appendix A.3.3 numeric padding, line 554 | 0.000001 | R4#anchor_v3.numeric_padding_s | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-109 — Appendix A.3.3 exact decimal four-term sum, line 555 | 0.0011349971959968977402 | Exact decimal addition of R4#anchor_v3.anchor_only_bound_s + R4#anchor_v3.wall_minus_monotonic_span_s + R4#anchor_v3.stamp_resolution_s + R4#anchor_v3.numeric_padding_s, preserving the four printed decimal lexemes | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-110 — Appendix A.3.3 outward-rounded sum, line 555 | 0.0011349971959968978 s | R4#anchor_v3.effective_clock_anchor_bound_s; same value RF re-derives in Section 2 | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / VALUE ALREADY REPLAY-FENCED VIA SECTION 2; APPENDIX OCCURRENCE REGISTRY_BOUND | DRAFT, AUTH |
| DG-111 — Appendix A.3.3 repeated anchor bound, line 557 | 0.0011349971959968978 s | R4#anchor_v3.effective_clock_anchor_bound_s; same value RF re-derives in Section 2 | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / VALUE ALREADY REPLAY-FENCED VIA SECTION 2; APPENDIX OCCURRENCE REGISTRY_BOUND | DRAFT, AUTH |
| DG-112 — Appendix A.3.3 anchor bound in milliseconds, line 557 | 1.135 ms | Round 1000 × R4#anchor_v3.effective_clock_anchor_bound_s to three decimal places | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-113 — Appendix A.3.3 printed-endpoint half-width divisor, line 557 | `/2` in `(*A_hi* − *A_lo*)/2` | Fixed divisor 2 in the binary64 half-width arithmetic over R4#anchor_v3.anchor_upper_epoch_s and R4#anchor_v3.anchor_lower_epoch_s | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-114 — Appendix A.3.3 printed-endpoint half-width, line 557 | 0.0006871223449707031 s | Binary64 `(R4#anchor_v3.anchor_upper_epoch_s - R4#anchor_v3.anchor_lower_epoch_s) / 2` | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-115 — Appendix A.3.3 printed-versus-exact half-width difference, line 557 | 0.0000002063105 s | Binary64 DG-114 minus R4#anchor_v3.anchor_only_bound_s, rounded to 13 decimal places | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-116 — Appendix A.3.3 epoch magnitude, line 557 | 1.78·10⁹ s | R4#anchor_v3.first_sample_end_point_epoch_s rendered in scientific notation to three significant digits | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-117 — Appendix A.3.3 binary64 spacing, line 557 | 2.4·10⁻⁷ s | At `A = R4#anchor_v3.first_sample_end_point_epoch_s`, derive the binary64 spacing as `2^(floor(log2(abs(A))) - 52)` and render to two significant digits | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-118 — Appendix A.3.3 fitted rate lower endpoint, line 557 | 1.0000022202281935 | R4#anchor_v3.rate_lower | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-119 — Appendix A.3.3 fitted rate upper endpoint, line 557 | 1.0000022646196323 | R4#anchor_v3.rate_upper | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-120 — Appendix A.3.3 fitted-rate midpoint summary, line 557 | about 2.2 ppm | `round(((((R4#anchor_v3.rate_lower + R4#anchor_v3.rate_upper) / 2) - 1) × 10^6), 1)` ppm | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-121 — Appendix A.3.3 rounded capture duration, line 557 | 197-second | Round C#clock_anchor.clock_stamps.sampling_stopped.epoch_s - C#clock_anchor.clock_stamps.sampling_started.epoch_s to the nearest whole second | retained 20260722 capture / anchor continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-122 — Appendix A.3.3 native rollover count, line 557 | 197 rollovers | R4#anchor_v3.native_rollover_count | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-123 — Appendix A.3.3 checked-record count, line 557 | 1665 records | R4#anchor_v3.records_checked | retained 20260722 capture / anchor continuation | MEASURED | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-124 — Appendix A.3.6 effective fiducial bound, line 650 | 0.030067931757111657 s | R4#b_fiducial_v3_s; same value RF re-derives in Section 2 | retained 20260722 capture / calibration-bound continuation | MEASURED | DIAGNOSTIC_ERA / VALUE ALREADY REPLAY-FENCED VIA SECTION 2; APPENDIX OCCURRENCE REGISTRY_BOUND | DRAFT, AUTH |
| DG-125 — Appendix A.3.6 anchor component, line 650 | 0.0011349971959968978 s | R4#anchor_v3.effective_clock_anchor_bound_s; same value RF re-derives in Section 2 | retained 20260722 capture / calibration-bound continuation | MEASURED | DIAGNOSTIC_ERA / VALUE ALREADY REPLAY-FENCED VIA SECTION 2; APPENDIX OCCURRENCE REGISTRY_BOUND | DRAFT, AUTH |
| DG-126 — Appendix A.3.6 printed-bound difference, line 650 | 0.0289329345611147592 s | Exact decimal R4#b_fiducial_v3_s - R4#anchor_v3.effective_clock_anchor_bound_s; same arithmetic RF checks in Section 2 | retained 20260722 capture / calibration-bound continuation | DERIVE | DIAGNOSTIC_ERA / VALUE ALREADY REPLAY-FENCED VIA SECTION 2; APPENDIX OCCURRENCE REGISTRY_BOUND | DRAFT, AUTH |
| DG-127 — Appendix A.3.6 difference in milliseconds, line 650 | 28.9 ms | Round 1000 × DG-126 to one decimal place | retained 20260722 capture / calibration-bound continuation | DERIVE | DIAGNOSTIC_ERA / APPENDIX_ONLY_REGISTRY_BOUND; NOT REPLAY_FENCED | DRAFT, AUTH |
| DG-128 — Appendix A.3.8 retained calibration corpus table, lines 1153–1169 | 17 b_fiducial_s bounds (table) | S17#derivation_corpus.members[].b_fiducial_s; `corpus_doubles_from_17_to_34` (`joulewise/calibration_bracketing.py:207`) regenerates both Section 2 constants and this table | diagnostic calibration / n17 | MEASURED | DIAGNOSTIC_ERA / n17 | DRAFT, AUTH |

#### Successor-draft desk analyses (round 7) — DX rows

These rows are a separate successor-draft namespace. They do not extend the
closed DG census of draft-v1 diagnostic sites, and they carry issued values
rather than `[PENDING...]` markers. `R7_FENCED` means digest- and field-checked
in CI by R7F, with byte-identical replay when the retained corpus is present.
It does not mean RF-fenced: RF remains the Section 2 replay fence and its
43-comparison census is unchanged.

Path abbreviations below are exact:

- XD = docs/paper/round7/excursion-decomposition.json, sha256 21618026dfc677165b2a1acd511ff0d3130bd3837fa344c9ca9fbac95d7e058b (33,765 B), schema joulewise-excursion-decomposition/v1
- XS = scripts/paper_excursion_decomposition.py, sha256 8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b (49b258d2, #240)
- F4 = docs/paper/figures/fig4_edge_excursions.svg, sha256 6ac9d5c7a84ac1bb8d3c0da036449f77e0e5d2d36564dfc33a1c2812912782cf
- AQ = docs/paper/round7/anchor-correction-quantified.json, sha256 c09077149c66411d1873838de5c21aa1b7c97d8df24ea66a163d679cb31f50fc (54,280 B)
- AS = scripts/paper_anchor_correction_quantified.py, sha256 e3e4355c8f388d5e60a4291f3aee4fbd4b4d45217f4156373d6e8dd398b9e693 (b36d1e85, #272)
- R7F = scripts/check_paper_round7_artifacts.py

AS was re-pinned in #272 from 41cbbf08 (0438566b, #242): its `main` now
returns exit 3 on `PopulationUnavailable` instead of raising; the AQ payload
bytes are unchanged (AQ sha256 above is the same).

Wherever a DX value is printed, the opening standing sentence is mandatory:
“The following are diagnostic-era instrument statistics — a desk
re-derivation (XS over XD; AS over AQ) over retained captures whose energy
values D-078 voids for claim use; they characterise the timing calibration of
the instrument and are not evidence for any `_v5` result.” The same prose must
say that the values were re-derived under the current claim-bearing v3 anchor,
`XD#anchor_method =
powermetrics_native_second_rate_aware_set_membership_v1`, and that re-deriving
a historical corpus under the current method does not make it a supplier for a
claim. It must retain draft-v2-skeleton line 1137 verbatim: one capture,
59/118 values, sample statistics with no coverage or independence claim. The
anchor-delta sentence must say that its numeric deltas cover the 12 captures
v3 derived, alongside the 3 refusals and the one control failure. Floor ratios
were not recomputed. “Repeatably” is prohibited for these numbers; print the
DX-012 and DX-013 counts instead. Any F4 caption uses D-119 wording.

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DX-001 — XD artifact identity; no draft site | 21618026dfc677165b2a1acd511ff0d3130bd3837fa344c9ca9fbac95d7e058b | sha256(XD), 33,765 bytes, `XD#schema = joulewise-excursion-decomposition/v1`; producer XS is separately pinned above; `R7F_RENDER=source_sha256_xd` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-002 — AQ artifact identity; no draft site | c09077149c66411d1873838de5c21aa1b7c97d8df24ea66a163d679cb31f50fc | sha256(AQ), 54,280 bytes; producer AS is separately pinned above; `AQ#worked_capture_gate.matches_exactly` must be true; `R7F_RENDER=source_sha256_aq` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-003 — F4 figure identity; no draft site | 6ac9d5c7a84ac1bb8d3c0da036449f77e0e5d2d36564dfc33a1c2812912782cf | sha256(F4), bound to parent DX-001 and `XD#replay_command`; full replay is `python3 scripts/paper_excursion_decomposition.py --corpus-root /Users/edr/code/JouleWise --out docs/paper/round7/excursion-decomposition.json --svg docs/paper/figures/fig4_edge_excursions.svg`. XD's own replay command omits `--svg`; no XD re-issue occurs in this round. `R7F_RENDER=source_sha256_f4` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, F4, R7F |
| DX-010 — successor-draft onset best-fit lag median | +13.0 ms | `XD#summary.onset_best_fit_lag.median_ms`, parent DX-001; render an explicit sign and one decimal followed by ` ms`; `R7F_RENDER=signed_1_ms` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-011 — successor-draft offset best-fit lag median | −5.5 ms | `XD#summary.offset_best_fit_lag.median_ms`, parent DX-001; render a Unicode minus and one decimal followed by ` ms`; `R7F_RENDER=signed_1_ms` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-012 — successor-draft positive-onset count | 59 of 59 | `XD#summary.onset_best_fit_lag.count_positive` of `XD#summary.onset_best_fit_lag.count`, parent DX-001; render both exact integers as `positive of count`; `R7F_RENDER=positive_count_of_count` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-013 — successor-draft negative-offset count | 49 of 59 | `XD#summary.offset_best_fit_lag.count_negative` of `XD#summary.offset_best_fit_lag.count`, parent DX-001; render both exact integers as `negative of count`; `R7F_RENDER=negative_count_of_count` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-014 — successor-draft onset median absolute deviation | 2.5 ms | `XD#summary.onset_best_fit_lag.median_absolute_deviation_ms`, parent DX-001; render one decimal followed by ` ms`; `R7F_RENDER=fixed_1_ms` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-015 — successor-draft offset median absolute deviation | 4.0 ms | `XD#summary.offset_best_fit_lag.median_absolute_deviation_ms`, parent DX-001; render one decimal followed by ` ms`; `R7F_RENDER=fixed_1_ms` | retained 20260722 capture / 59-pulse calibration | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-016 — successor-draft onset-bias share of the fiducial bound | 43.2 % | Derive 100 × `XD#summary.onset_best_fit_lag.median_ms` / `XD#bound_terms.b_fiducial_ms`, parent DX-001; round once to one decimal and append ` %`; `R7F_RENDER=ratio_percent_1` | retained 20260722 capture / 59-pulse calibration | DERIVE | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-017 — successor-draft worst-onset excess above the median | 14.0 ms | Derive `XD#summary.onset_best_fit_lag.max_ms` − `XD#summary.onset_best_fit_lag.median_ms`, parent DX-001; render one decimal followed by ` ms`; `R7F_RENDER=difference_1_ms` | retained 20260722 capture / 59-pulse calibration | DERIVE | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | XD, XS, R7F |
| DX-020 — successor-draft anchor-correction population | 15 | `AQ#summary.population_size`, parent DX-002; render as an exact integer; `R7F_RENDER=integer` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-021 — successor-draft v3 derived and refused counts | 12 derived / 3 refused (all anchor_unresolved) | `AQ#summary.v3_derived_count`, `AQ#summary.v3_refused_count`, and `AQ#summary.v3_refusals_by_token.anchor_unresolved`, parent DX-002; render exact counts and require every refusal token to be `anchor_unresolved`; `R7F_RENDER=derived_refused_counts` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-022 — successor-draft admissibility flips | 2 (both refused_by_v3) | `AQ#summary.admissibility_flip_count` and `AQ#summary.admissibility_flips`, parent DX-002; render the exact count and require every `flip_direction` to equal `refused_by_v3`; `R7F_RENDER=flip_count_refused_by_v3` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-023 — successor-draft v2 control reproduction | 14 of 15; failure 20260722T213749-563b9849 | `AQ#summary.control_v2_reproduces_stored_count` of `AQ#summary.population_size`, with `AQ#summary.control_v2_reproduction_failures`, parent DX-002; render exact integers and the sole exact failure ID; `R7F_RENDER=control_count` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-024 — successor-draft median absolute-bound delta | +0.154318 ms | `AQ#summary.delta_v3_vs_stored_absolute.median_ms`, parent DX-002; render an explicit sign and six decimals followed by ` ms`; `R7F_RENDER=signed_6_ms` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-025 — successor-draft maximum absolute-bound delta magnitude | 1.090519 ms | `AQ#summary.delta_v3_vs_stored_absolute.max_absolute_ms`, parent DX-002; render six decimals followed by ` ms`; `R7F_RENDER=fixed_6_ms` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-026 — successor-draft maximum relative delta magnitude | 4.05 % | `AQ#summary.delta_v3_vs_stored_relative.max_absolute_pct`, parent DX-002; round once to two decimals and append ` %`; `R7F_RENDER=fixed_2_percent` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
| DX-027 — successor-draft median relative delta | +0.61 % | `AQ#summary.delta_v3_vs_stored_relative.median_pct`, parent DX-002; the issued artifact names this field `median_pct` (not `median_abs_pct`); render an explicit sign and two decimals followed by ` %`; `R7F_RENDER=signed_2_percent` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |

### Renderer-only metatokens

These are present in the template's bracket census but are not independently
fillable scientific values.

| Exact token | Producing rule | Campaign / cell | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERMINAL_REFUSAL_REASON_*]` | Documentation wildcard for the four concrete terminal-reason tokens | alpha/beta cells | DERIVE | META_FROZEN; must not survive final rendering | TPL, LINT |
| `[NO_EXACT_FLOOR_REASON_*]` | Documentation wildcard for the four concrete no-exact-floor tokens | alpha/beta cells | DERIVE | META_FROZEN; must not survive final rendering | TPL, LINT |
| `[PLAIN_LANGUAGE_RESULT_*]` | Documentation wildcard for the six concrete characterization outcome tokens | characterization rows | DERIVE | META_FROZEN; must not survive final rendering | TPL, LINT |
| `[VALUE]` | Local pseudotoken in the diagnostic-renderer examples; replaced only by the exact authenticated component being iterated | alpha/beta cell renderer | DERIVE | META_FROZEN; surviving `[VALUE]` is STOP_FILL | TPL, LINT |
| `[PRESENT_DIAGNOSTIC_LIST]` | Fixed-order, punctuation-stable list of present characterization diagnostics | characterization / refused-window renderer | DERIVE | RENDERER_FROZEN; blocked until diagnostic fields exist | TPL, LINT |
| `[ABSENT_DIAGNOSTIC_ROW_LIST]` | Fixed-order list of characterization rows without authenticated diagnostics | characterization / refused-window renderer | DERIVE | RENDERER_FROZEN; blocked until presence predicates exist | TPL, LINT |

## Draft marker-site registry

The draft does not use the binding token vocabulary. Its repeated generic
markers are therefore inventoried by physical site, not collapsed by spelling.
Line references are locators only; the draft remains read-only in this task.
The six characterization rows DS-02 through DS-07 bind exact content anchors
whose former bracket markers are absent. The Section 5 rewrite at `ec11f3f`
replaced every `TODO-EVIDENCE` guard inside those rows with a frozen value, a
derivation rule, or an explicit statement that a value must be ratified before
the plan is frozen. Addendum 4 item 40 settled the three anchors that the round-2 restructure broke.
DS-02, DS-05 and DS-06 were never broken and still occur exactly once. DS-03 IS RE-ANCHORED: its
site survives in the main text — the round-2 rewrite renamed the row rather than removing it — and
the new locator was derived by searching for the renamed anchor. DS-04 and DS-07 are RETIRED with
superseded notes: they name sites that Addendum 1 item 12 demoted from characterization to Future
Work, so the round-2 rewrite removed them and there is nothing to re-anchor. No locator was guessed
at any point. Those sites remain
protocol-specification rows, not fillable result cells: results render through
the template's Section 6 variants, never by filling draft Table 1. Every line
number below was re-derived on 2026-08-24 by searching for the site's own
anchor text.

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DS-01 — Section 4 operative-floor hold, line 189 | `[RESULT PENDING ISSUED ARTIFACTS]` | Four cell decompositions from all `F_*_abs_J`, `F_*_cmp_J`, and `F_*_operative_J` tokens | alpha and beta / all phase floor cells | DERIVE | DRAFT_GENERIC; guarded template output only | DRAFT, TPL, DF |
| DS-02 — Section 3 characterization specification row, line 94 | `**Workload response:**` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_linearity` plus licensed linearity diagnostics, only after an authenticated characterization report is issued | characterization / linearity | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-03 — Section 3 characterization criteria row, line 95 | `**Identical-condition null:**` content anchor (RE-ANCHORED 2026-08-27, Addendum 4 item 40: the site survives in the main text at Section 3 line 95; the round-2 rewrite renamed the row from "Identical-condition null response" and the anchor was re-derived by search, not by offset); the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_null` plus licensed null diagnostics, only after an authenticated characterization report is issued | characterization / null response | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-04 — Section 5 characterization specification row, line 350 | `\| Deliberate small-difference challenge \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_floor` plus licensed floor diagnostics, only after an authenticated characterization report is issued | characterization / empirical floor | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |

**DS-04 RETIRED (Addendum 4 item 40).** The row immediately above is retained BYTE-FOR-BYTE as it stood before retirement, exactly as DS-08 was; retirement is recorded here, never by editing the retired row. This row bound a Section 5 characterization
site for the deliberate small-difference challenge. Addendum 1 item 12 demoted that criterion from characterization to Future
Work, and the round-2 rewrite removed the site accordingly, so the anchor no longer occurs in
the draft. The row is retired rather than re-anchored: no locator is ever guessed. Its bytes
are retained immediately above for provenance and must not be rendered.

| DS-05 — Section 3 characterization specification row, line 96 | `**Phase accounting:**` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_phase` plus licensed additivity/invariance diagnostics, only after an authenticated characterization report is issued | characterization / phase attribution | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-06 — Section 3 characterization specification row, line 97 | `**Drift and recovery:**` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_drift` plus licensed excursion/recovery diagnostics, only after an authenticated characterization report is issued | characterization / drift and settling | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-07 — Section 5 characterization specification row, line 353 | `\| Between-session stability \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_between_sessions` and `N_C_eligible_sessions`, only after an authenticated characterization report is issued | characterization / between sessions | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |

**DS-07 RETIRED (Addendum 4 item 40).** The row immediately above is retained BYTE-FOR-BYTE as it stood before retirement, exactly as DS-08 was; retirement is recorded here, never by editing the retired row. This row bound a Section 5 characterization
site for between-session stability. Addendum 1 item 12 demoted that criterion from characterization to Future
Work, and the round-2 rewrite removed the site accordingly, so the anchor no longer occurs in
the draft. The row is retired rather than re-anchored: no locator is ever guessed. Its bytes
are retained immediately above for provenance and must not be rendered.

| DS-08a — Section 6 results branch hold, line 274 | `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 6, and 7.]` | Exactly one guarded template result variant; template-internal section labels are not draft section locators | alpha, beta, gamma | DERIVE | DRAFT_GENERIC; no historical or diagnostic result is a supplier | DRAFT, TPL, LINT |

**DS-08 superseded by DS-08a (Addendum 3 item 35).** The round-2 restructure renumbered the
paper: instrument characterization moved from Section 5 to Section 3, and the resolution bound
from Section 3 to Section 4. The DS-08 marker's byte-frozen sentence named "Sections 3, 5, and 7",
which after renumbering pointed at collection — a section carrying no instrument diagnostic — and
omitted the sections that do. Addendum 3 item 35 authorises the successor marker DS-08a naming
**Sections 3, 6, and 7**: Section 3 carries the retained point-floor and corner-widened-floor
energies and the composed timing-bound range, Section 6 carries the prompt-sizing diagnostic, and
Section 7 carries the corner-to-point ratio. DS-08's original bytes are retained immediately below
for provenance; they are superseded and must not be rendered.

Retained superseded DS-08 bytes: `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural
placeholders; no energy value from superseded artifacts is carried into these tables, and none
appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3,
5, and 7.]`

| DS-09 — Table 2 prompt/1.5B gross cell, line 280, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request` with lower and upper interval endpoints | alpha / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-10 — Table 2 prompt/1.5B per-token cell, line 280, col 4 under `J per prompt token` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_token` | alpha / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-11 — Table 2 prompt/1.5B floor cell, line 280, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `F_1p7B_prefill_p[PREFILL_LENGTH]_operative_J` plus cell label branch | alpha / prefill-p[PREFILL_LENGTH] floor | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DRAFT, TPL, DF, G2A |
| DS-12 — Table 2 prompt/1.5B count cell, line 280, col 7 under `n` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `N_bundles_1p7B_prefill_p[PREFILL_LENGTH]` | alpha / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-13 — Table 2 prompt/7B gross cell, line 281, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `E_8B_prefill_p[PREFILL_LENGTH]_J_per_request` with lower and upper interval endpoints | beta / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-14 — Table 2 prompt/7B per-token cell, line 281, col 4 under `J per prompt token` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `E_8B_prefill_p[PREFILL_LENGTH]_J_per_token` | beta / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-15 — Table 2 prompt/7B floor cell, line 281, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `F_8B_prefill_p[PREFILL_LENGTH]_operative_J` plus cell label branch | beta / prefill-p[PREFILL_LENGTH] floor | DERIVE | UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED | DRAFT, TPL, DF, G2A |
| DS-16 — Table 2 prompt/7B count cell, line 281, col 7 under `n` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `N_bundles_8B_prefill_p[PREFILL_LENGTH]` | beta / prefill-p[PREFILL_LENGTH] reported mean | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-17 — Table 2 decode/1.5B gross cell, line 282, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `E_1p7B_decode_J_per_request` with lower and upper interval endpoints | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-18 — Table 2 decode/1.5B per-token cell, line 282, col 5 under `J per output token` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `E_1p7B_decode_J_per_token` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-19 — Table 2 decode/1.5B floor cell, line 282, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `F_1p7B_decode_operative_J` plus cell label branch | alpha / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-20 — Table 2 decode/1.5B count cell, line 282, col 7 under `n` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `N_bundles_1p7B_decode` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-21 — Table 2 decode/7B gross cell, line 283, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `E_8B_decode_J_per_request` with lower and upper interval endpoints | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-22 — Table 2 decode/7B per-token cell, line 283, col 5 under `J per output token` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `E_8B_decode_J_per_token` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-23 — Table 2 decode/7B floor cell, line 283, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `F_8B_decode_operative_J` plus cell label branch | beta / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-24 — Table 2 decode/7B count cell, line 283, col 7 under `n` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `N_bundles_8B_decode` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-25 — Table 3 decode point estimate, line 289, col 2 under `Point estimate` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `E_decode_contrast_signed_J_per_request` | gamma / decode contrast | MEASURED | VALUE_UNISSUED | DRAFT, TPL, CV |
| DS-26 — Table 3 decode interval, line 289, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `E_decode_contrast_lower_J`, `E_decode_contrast_upper_J` | gamma / decode contrast | MEASURED | VALUE_UNISSUED; one bracket marker contains two semantic fills | DRAFT, TPL, CV |
| DS-27 — Table 3 decode floor, line 289, col 4 under `Cell floor` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `F_claim_decode_armwise_max_J` | gamma consuming alpha/beta decode floors | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-28 — Table 3 planning-only sizing diagnostic F+B and signed clearance, line 289, col 5 | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; branch must be explicit; any separately issued F+B value is non-gating planning information, neither necessary nor sufficient for acceptance | gamma / decode contrast | DERIVE | DRAFT/TEMPLATE SHAPE MISMATCH; draft has one unconditional cell | DRAFT, TPL |
| DS-29 — Table 3 decode contrast claim-side bound, line 289, col 6 under `Claim-side bound` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `B_decode_claim_J` | gamma / decode contrast | STOP_FILL | SUPPLIER_UNKNOWN | DRAFT, TPL, DF, CV |
| DS-30 — Table 3 decode floor-gate outcome, line 289, col 7 under `Floor-gate outcome` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; derive only from authenticated magnitude and claim floor, consistent with claim verdict | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; renderer contract must add a binding without renaming existing tokens | DRAFT, TPL, CV |
| DS-31 — Table 3 decode direction-gate outcome, line 289, col 8 under `Direction-gate outcome` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; derive only from the fully composed interval and registered direction | gamma / decode contrast | STOP_FILL | TOKEN_MISSING | DRAFT, TPL, CV |
| DS-32 — Table 3 decode verdict, line 289, col 9 under `Verdict`, and A/B outcome paragraphs | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|`; repeated successor marker `[FILL:DS-32]` | Authenticated `contrasts[decode].claim_evaluation.outcome`; bind one professor-facing conservative rendering and repeat it without inferring it from any ratio disposition. On REFUSAL, retain the Table 3 slot: render the authenticated verdict if it issued; if this verdict's absence is the issued stop reason, render `not evaluated — required token-generation verdict absent`; if an earlier before-comparison stop prevented evaluation, render `not evaluated — stopped before comparison: <issued reason>` from the governing evidence | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; branch placements remain stopped until the authenticated rendering issues; the retained REFUSAL table cell must use the registered rendering rather than retain the marker | DRAFT, TPL, CV, AUTH |
| DS-33 — Table 3 prompt floor, line 290, col 4 under `Cell floor` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | `_v5` prefill contrast `ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b` needs a professor-facing claim-floor token; no such token exists | gamma consuming alpha/beta prefill-p[PREFILL_LENGTH] floors | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING | DRAFT, TPL, AUTH, V5GEN, G2A |
| DS-34 — Section 9 evidence/code-availability locator hold, line 348 | `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | UNKNOWN release-manifest fields for repository commit, archive locator, and published digest manifest | release / artifact availability | STOP_FILL | SUPPLIER_UNKNOWN; resolve only after the release checklist issues the locators | DRAFT, AUTH |
| PG-01 — Table 3 prompt point estimate, line 290, col 2 under `Point estimate` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future authenticated estimator for `_v5` contrast `ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b`; no exact professor-facing token exists | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH, V5GEN, G2A |
| PG-02 — Table 3 prompt interval, line 290, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future authenticated fully composed lower and upper endpoints for `_v5` contrast `ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b`; no exact professor-facing endpoint tokens exist | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING; one marker site contains two semantic slots | DRAFT, TPL, CV, AUTH, V5GEN, G2A |
| PG-04 — Table 3 planning-only sizing diagnostic F+B and signed clearance, line 290, col 5 | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future branch-explicit clearance or shortfall derivation for the selected `_v5` prefill contrast; no exact token exists; any separately issued F+B value is non-gating planning information, neither necessary nor sufficient for acceptance | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING; shape contract required | DRAFT, TPL, CV, V5GEN, G2A |
| PG-05 — Table 3 prompt contrast claim-side bound, line 290, col 6 under `Claim-side bound` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact professor-facing token and no named claim-side-bound field for the selected `_v5` prefill contrast | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / SUPPLIER_UNKNOWN | DRAFT, TPL, CV, AUTH, V5GEN, G2A |
| PG-06 — Table 3 prompt floor-gate outcome, line 290, col 7 under `Floor-gate outcome` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future conservative rendering consistent with the selected prefill magnitude, floor, and verdict; no exact token exists | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, V5GEN, G2A |
| PG-07 — Table 3 prompt direction-gate outcome, line 290, col 8 under `Direction-gate outcome` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | Future conservative rendering from the selected prefill contrast's fully composed interval and registered direction | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH, V5GEN, G2A |
| PG-08 — Table 3 prompt verdict, line 290, col 9 under `Verdict`, and A/B outcome paragraphs | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|`; repeated successor marker `[FILL:PG-08]` | Future authenticated claim-evaluation outcome for the selected `_v5` prefill contrast; bind one professor-facing conservative rendering and repeat it without inferring it from any ratio disposition. On REFUSAL, retain the Table 3 slot: render the authenticated verdict if it issued; if this verdict's absence is the issued stop reason, render `not evaluated — required prompt-processing verdict absent`; if an earlier before-comparison stop prevented evaluation, render `not evaluated — stopped before comparison: <issued reason>` from the governing evidence | gamma / prefill-p[PREFILL_LENGTH] contrast | STOP_FILL | UNRESOLVED-UNTIL-G2A / TOKEN_FAMILY_MISSING; branch placements remain stopped until the authenticated rendering issues; the retained REFUSAL table cell must use the registered rendering rather than retain the marker | DRAFT, TPL, CV, AUTH, V5GEN, G2A |

**PG-03 RETIRED (round-7 R-6 regeneration).** PG-02 now owns the one physical
`[PENDING, PENDING]` site and both of its semantic endpoints. Keeping a second
live row for that same site would violate the one-site/one-row census. No value,
supplier, or fill authority changed in this consolidation.

**DS-32/PG-08 successor-amendment provenance (2026-09-04).** These two rows
remain in the frozen-draft census because each owns its original Table 3 cell.
They were amended in place during paper-G fix round 2 to govern repeated A/B
placements in the successor skeleton, and amended again in fix round 4 to bind
the retained Table 3 cell's REFUSAL rendering. The table cells remain census
sites; only the repeated paragraph placements belong to the successor-slot
regime below. Neither amendment changes a supplier or authorizes a verdict to
be inferred from the ratio outcome.

### Successor-skeleton outcome-branch slots

These rows govern nonnumeric semantic placements added to
`draft-v2-skeleton.md`; they are outside the frozen-draft marker census above.
Each repeated marker shares one result across the Abstract, Section 7, and
Section 10. No row authorizes prose to be inferred at the desk.

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| OB-01 — Outcome-B failed-component list in the Abstract, Section 7, and Section 10 | `[FILL:OB-01]` | Authenticated `joulewise.d165_dominance_closeout.v1`: conservatively render every record with `passes` false from `independent_ratios[].{cell_id,component,passes}` and `comparative_common_mode_ratios[].{cell_id,component,passes}`; no professor-facing list renderer exists yet | alpha and beta / all required absolute, comparative, and comparative shared-energy-sign/local-corner components | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; TOKEN_MISSING; never render from an unauthenticated or incomplete close-out | DRAFT, D165 |
| TR-01 — Branch-independent transfer limitation in the Abstract, Section 7, and Section 10 | `Transfer of the pulse-derived timing allowance to inference was not tested.` | Fixed limitation sentence; no evidence lookup, late-window predicate, or outcome branch may alter it | pulse-to-inference transfer / all three outcome branches | LIMITATION | WITHDRAWN 2026-09-04 under provisional final ruling 17: all nine fill placements became the fixed sentence; the selector still retains one placement in each of its three selected outcome groups | DRAFT, AUTH |
| OR-01 — Refusal stop stage and issued reason in the Section-4 form and the Abstract, Section 7, and Section 10 Refusal paragraphs | `[FILL:OR-01]` | Before comparison: the authenticated window-admission outcome for the affected model or the authenticated claim-evaluation outcome for the affected token-generation (`DS-32`) or prompt-processing (`PG-08`) verdict. At close-out: authenticated `joulewise.d165_dominance_closeout.v1`. At every placement, render exactly one stage label (`before comparison` or `at close-out`) plus the reason issued by that governing evidence; name each affected model or verdict; include a Qwen-pair verdict only when its absence is the stop reason; never infer a reason from ratio disposition | fixed Qwen3 pair / two-stage refusal | STOP_FILL | SUPPLIERS_NAMED / VALUE_UNISSUED; TOKEN_MISSING; refuse on absent, unauthenticated, conflicting, or multi-stage-without-precedence inputs | DRAFT, AUTH, D165 |

## Authority discrepancies and non-token gaps

These are recorded rather than repaired because `docs/paper/draft-v1.md` is
read-only and the template vocabulary is binding.

| Gap | Conflict | Required resolution | Sources |
|---|---|---|---|
| Gamma prefill contrast | The frozen draft registers both contrast arms and the `_v5` generator names the selected prefill contrast, while the renderer/template remain decode-only | After G2-a resolves `[PREFILL_LENGTH]`, the lead-owned renderer/template train must add the guarded prefill token family for the point estimate, both interval endpoints, claim floor, branch-explicit clearance or shortfall, claim-side bound, floor and direction outcomes, verdict, and D-166's split refusal branch; DS-33, PG-01, PG-02, and PG-04 through PG-08 remain stopped | DRAFT, TPL, AUTH, V5GEN, G2A |
| D-123 reported means | D-123 authorizes mean cells, while no current extraction/report schema fixes their member basis or output field names | Land and audit the reported-mean schema in the alpha/beta packs and extraction output; prove floor outputs remain byte-identical; then replace `SUPPLIER_UNKNOWN` statuses | AUTH, FX, PLAN |
| Generic draft table outcomes | Draft Table 3 has generic cells for decode and prompt gate outcomes and verdicts, but the template has no exact tokens for them | Add binding tokens or a machine renderer contract in the lead-owned template train; do not infer strings from variant headings | DRAFT, TPL, CV |
| DG-071 / DG-075 issuance | RESOLVED by PR #276: the ratified record-period statistics issued in `docs/paper/round7/dg071-dg075-statistics.md` and `.json` with the SHA-256 pins recorded in both rows | Keep both values, sample counts, rendering rules, paths, and SHA-256 pins synchronized with the issued artifact; never recompute them from the prose | PROJ, SYN |
| Characterization outputs | RESOLVED 2026-08-24 as to the field contract: the frozen characterization result specification defines every named token's producing field, and this registry now binds each one. The draft's Section 5 still holds protocol-specification rows rather than claim-bearing result cells, which is by design | Issue an authenticated characterization report; until then every characterization row stays `KEY_FROZEN / VALUE_UNISSUED`. Ratify or replace the two-limb derivation recorded above | DRAFT, TPL, SPEC |

The folded capture-method-era and estimator-provenance preconditions authorize
no value.

## Census and reconciliation

Census command shape: scan every non-newline bracket pair in the frozen draft
and retain markers beginning with `PENDING`, `RESULT PENDING ISSUED ARTIFACTS`,
or `REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST`; count a comma
inside a result marker as a second semantic slot. Markdown citations and the
two explanatory `[[NEEDS-VALUE:...]]` notes are outside the result-marker
family and are counted separately.

- Frozen draft SHA-256:
  `939dfa23730a22d35e02154d7aa7904f396364d55c128e6715c72b849eaf39ab`;
  **34 literal `[PENDING...]` sites / 36 semantic slots**, **37 complete-family
  result-marker sites / 39 semantic slots**, and **2 `[[NEEDS-VALUE:...]]`
  notes**. These are measured against the current 672-line source, not
  carried forward.
- Registry exact-key rows: **126**. This is the prior 109-row key inventory
  regenerated one-for-one (66 model-bearing keys renamed and 43 retained) plus
  17 new keys: `[PREFILL_LENGTH]`, eight independent-corner R columns, four
  comparative R_cm columns, and four absolute R_cm not-applicable columns.
  The count includes the six explicitly labelled renderer metatokens.
- Registry live marker-site rows: **35**, exactly one for each complete-family
  draft site, carrying the same 37 semantic slots. PG-02 owns both slots at its
  interval site; PG-03 is retired. The `[PENDING...]` subset is therefore 32
  rows for 32 sites and 34 slots. No live site is duplicated and no site-to-row
  gap is silently supplied.
- The current renderer/template vocabulary still spells the pre-`_v5` model
  keys. It is not a fill supplier for renamed keys and must fail closed until a
  lead-owned regeneration binds the 126-row registry vocabulary. This scoped
  documentation change does not edit that implementation.

Measured marker-row command:

  ```sh
  grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*[[]PENDING' docs/paper/results-fill-registry.md
  ```

Result: **32 `[PENDING...]` rows**. Including DS-01, DS-08a, and DS-34 gives
the complete-family total of 35.

## Lead double-checks before renderer implementation

- Verify the G2-a selection output path and SHA-256, bind
  `[PREFILL_LENGTH]` to `collection_prefill_tokens`, and require the prompt-pin
  v2 cross-check before generating any prefill identifier.
- Rule the exact D-123 reported-mean member basis and output schema; none of the
  twenty mean/interval/companion/count tokens is fillable yet.
- Name the gamma claim-side-bound field. Do not assume that the complete
  deterministic-bound total is identical to the template's clock-anchor
  claim-side term.
- Regenerate the guarded prefill token family and the missing Table 3 outcome
  tokens only after G2-a; implement D-166's two distinct exhausted-ladder
  refusal renderings verbatim.
- Keep DG-071 and DG-075's issued median-with-IQR values bound to the exact
  Markdown and JSON paths and SHA-256 values quoted in their rows; any reissue
  must update both rows and their reader-facing placements together.
- The characterization result schema is frozen; what remains is an issued,
  authenticated characterization report. Ratify or replace the PROPOSED
  two-limb derivation for `[R_C_linearity_limit_J]` and
  `[B_C_prompt_invariance_J_per_token]` before either is rendered.
- Keep D-119 conservative wording attached to every rendered figure, table,
  and caption; a stronger claim must name its evidence in the same sentence.
