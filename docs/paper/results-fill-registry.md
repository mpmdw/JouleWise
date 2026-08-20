# Results fill registry

This is the binding crosswalk for result rendering. It inventories the generic
markers in `docs/paper/draft-v1.md` by site and the exact fill-key vocabulary in
`docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md` by distinct
token. It does not authorize a value. A renderer must stop when the named
artifact, field, branch predicate, or authentication condition is absent.
Numeric characters in this document occur only inside binding identifiers,
model names, source locators, and the required census; no measured result or
demonstration value appears.

No historical result is a supplier for this registry. Under D-117, claim
authority can arise only from prospective alpha, beta, and gamma evidence;
D-122 adds a prospectively frozen prompt-processing contrast to gamma; and
D-123 adds reported phase-energy mean cells to alpha and beta, conditional on
the required no-semantics-change check.

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

Every row cites one or more of these defining sources:

- `DRAFT` — `docs/paper/draft-v1.md`, especially Sections 6 and 7 and the
  bracket markers enumerated below.
- `TPL` — `docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md`,
  Fill key and the guarded Section 6 and Section 7 variants. This is the
  binding token vocabulary.
- `LINT` —
  `docs/process_traces/2026-08-07-plan-factory/lint_results_prose_template.py`,
  which enforces branch selection, global token licensing, and `STOP_FILL`.
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

Campaign shorthand used below is semantic, not a claim that final artifact
identifiers already exist:

- `alpha`: prospective Qwen2.5-1.5B floor window; prompt-processing and
  token-generation absolute and comparative cells; D-123 reported means.
- `beta`: prospective Qwen2.5-7B floor window; the same four floor-cell roles;
  D-123 reported means.
- `gamma`: prospective Qwen2.5 model-size contrast window; token-generation
  contrast plus the D-122 prompt-processing contrast arm.
- `characterization`: the separately governed Window C characterization
  campaign, not any historical window called C.

## Exact template-token registry

There is one row for every distinct bracket token recognized by the template
census. Repeated occurrences of a token share this row and therefore the same
source value.

### Alpha and beta floor-cell values

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[F_1p5B_prompt_abs_J]` | Prospective aggregate floor artifact, alpha prompt cell `floor_abs_j` | alpha / prompt absolute component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier freezes with the alpha pack and post-collection pinset | TPL, DF, MINT, PLAN |
| `[F_1p5B_prompt_cmp_J]` | Same cell, `floor_cmp_j` | alpha / prompt comparative component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_1p5B_prompt_operative_J]` | `max(F_1p5B_prompt_abs_J, F_1p5B_prompt_cmp_J)`; verify against the same cell's `floor_gate_j` | alpha / prompt aggregate cell | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL, DF, MINT |
| `[F_1p5B_decode_abs_J]` | Prospective aggregate floor artifact, alpha decode cell `floor_abs_j` | alpha / decode absolute component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_1p5B_decode_cmp_J]` | Same cell, `floor_cmp_j` | alpha / decode comparative component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_1p5B_decode_operative_J]` | `max(F_1p5B_decode_abs_J, F_1p5B_decode_cmp_J)`; verify against `floor_gate_j` | alpha / decode aggregate cell | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL, DF, MINT |
| `[F_7B_prompt_abs_J]` | Prospective aggregate floor artifact, beta prompt cell `floor_abs_j` | beta / prompt absolute component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_7B_prompt_cmp_J]` | Same cell, `floor_cmp_j` | beta / prompt comparative component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_7B_prompt_operative_J]` | `max(F_7B_prompt_abs_J, F_7B_prompt_cmp_J)`; verify against `floor_gate_j` | beta / prompt aggregate cell | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL, DF, MINT |
| `[F_7B_decode_abs_J]` | Prospective aggregate floor artifact, beta decode cell `floor_abs_j` | beta / decode absolute component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_7B_decode_cmp_J]` | Same cell, `floor_cmp_j` | beta / decode comparative component | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact cell identifier pending | TPL, DF, MINT, PLAN |
| `[F_7B_decode_operative_J]` | `max(F_7B_decode_abs_J, F_7B_decode_cmp_J)`; verify against `floor_gate_j` | beta / decode aggregate cell | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL, DF, MINT |

### Floor-cell branch text and diagnostics

For each row below, the cell selector must first validate both component
records exactly as the template requires. Generic absence or nullness is never
converted into a nonterminal no-exact-floor state.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERMINAL_REFUSAL_REASON_1p5B_prompt]` | Conservative rendering of terminal codes from alpha prompt extraction `cells[].refusal_reasons`, plus governing verdict failures | alpha / prompt cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL on unknown code or malformed metadata | TPL, LINT, FX, WV, AUTH |
| `[TERMINAL_REFUSAL_REASON_1p5B_decode]` | Same source class for alpha decode | alpha / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL on invalid selector input | TPL, LINT, FX, WV, AUTH |
| `[TERMINAL_REFUSAL_REASON_7B_prompt]` | Same source class for beta prompt | beta / prompt cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL on invalid selector input | TPL, LINT, FX, WV, AUTH |
| `[TERMINAL_REFUSAL_REASON_7B_decode]` | Same source class for beta decode | beta / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; STOP_FILL on invalid selector input | TPL, LINT, FX, WV, AUTH |
| `[NO_EXACT_FLOOR_REASON_1p5B_prompt]` | Renderer-normalized explanation from alpha prompt component reports when the permitted exact-floor-unavailable state is proven | alpha / prompt cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[NO_EXACT_FLOOR_REASON_1p5B_decode]` | Same normalization for alpha decode | alpha / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[NO_EXACT_FLOOR_REASON_7B_prompt]` | Same normalization for beta prompt | beta / prompt cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[NO_EXACT_FLOOR_REASON_7B_decode]` | Same normalization for beta decode | beta / decode cell | DERIVE | KEY_FROZEN / VALUE_UNISSUED; all unmatched absences STOP_FILL | TPL, LINT, FX |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_prompt]` | Fixed-order renderer over available alpha prompt `floor_abs_j`, `floor_cmp_j`, and `point_floor_diagnostics` | alpha / prompt cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED; emit the template's no-diagnostic sentence if all are absent | TPL, DF, LINT |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_1p5B_decode]` | Same renderer for alpha decode | alpha / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_prompt]` | Same renderer for beta prompt | beta / prompt cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[AVAILABLE_DIAGNOSTIC_CLAUSE_7B_decode]` | Same renderer for beta decode | beta / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_1p5B_prompt]` | Component-specific renderer over alpha prompt `point_floor_diagnostics` entries; `published_claim_floor` must be false | alpha / prompt cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_1p5B_decode]` | Same renderer for alpha decode | alpha / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_7B_prompt]` | Same renderer for beta prompt | beta / prompt cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[POINT_DIAGNOSTIC_CLAUSE_7B_decode]` | Same renderer for beta decode | beta / decode cell | DERIVE | RENDERER_FROZEN / VALUE_UNISSUED | TPL, DF, LINT |
| `[REFUSAL_REASON_1p5B_floor_window]` | Alpha whole-window verdict `status` with conservative rendering of `idle_admission_core.conditions` and `member_failures` | alpha / whole window | MEASURED | KEY_FROZEN / VERDICT_UNISSUED; never synthesize a passing value from extraction | TPL, WV, AUTH |
| `[REFUSAL_REASON_7B_floor_window]` | Beta whole-window verdict, same fields | beta / whole window | MEASURED | KEY_FROZEN / VERDICT_UNISSUED | TPL, WV, AUTH |

### D-123 reported phase-energy cells

D-123 freezes the procedure and requires reader-facing phase-energy means from
alpha and beta. The current repository defines floor-cell `mean_j` internally,
but it does not define a reported-mean result schema, its admitted member basis,
its fully composed mean interval fields, or its runtime-observed per-token
companion fields. Substituting the absolute floor component's internal mean
would silently choose a basis and is forbidden.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[E_1p5B_prompt_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN; resolve by landing the alpha reported-mean schema and exact member basis | TPL, AUTH, FX |
| `[E_1p5B_prompt_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | alpha / prompt reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN; resolve in the D-123 extractor contract | TPL, AUTH |
| `[E_1p5B_prompt_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | alpha / prompt reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN; resolve in the D-123 extractor contract | TPL, AUTH |
| `[E_1p5B_prompt_J_per_token]` | UNKNOWN — runtime-observed prompt-token companion field not yet defined | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN; bind the denominator provenance in the D-123 output schema | TPL, AUTH |
| `[N_bundles_1p5B_prompt]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |
| `[E_1p5B_decode_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; resolve by landing the alpha reported-mean schema and basis | TPL, AUTH, FX |
| `[E_1p5B_decode_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | alpha / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_1p5B_decode_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | alpha / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_1p5B_decode_J_per_token]` | UNKNOWN — runtime-observed output-token companion field not yet defined | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; denominator provenance must be authenticated | TPL, AUTH |
| `[N_bundles_1p5B_decode]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |
| `[E_7B_prompt_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN; resolve by landing the beta reported-mean schema and basis | TPL, AUTH, FX |
| `[E_7B_prompt_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | beta / prompt reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_7B_prompt_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | beta / prompt reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_7B_prompt_J_per_token]` | UNKNOWN — runtime-observed prompt-token companion field not yet defined | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN; denominator provenance must be authenticated | TPL, AUTH |
| `[N_bundles_7B_prompt]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |
| `[E_7B_decode_J_per_request]` | UNKNOWN — D-123 reported-mean artifact field not yet defined | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; resolve by landing the beta reported-mean schema and basis | TPL, AUTH, FX |
| `[E_7B_decode_lower_J]` | UNKNOWN — fully composed lower endpoint not yet defined | beta / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_7B_decode_upper_J]` | UNKNOWN — fully composed upper endpoint not yet defined | beta / decode reported-mean interval | STOP_FILL | SUPPLIER_UNKNOWN | TPL, AUTH |
| `[E_7B_decode_J_per_token]` | UNKNOWN — runtime-observed output-token companion field not yet defined | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; denominator provenance must be authenticated | TPL, AUTH |
| `[N_bundles_7B_decode]` | UNKNOWN — admitted independent-bundle count for the D-123 mean basis not yet defined | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN; do not substitute a floor-component count | TPL, AUTH, FX |

### Gamma token-generation contrast

These rows name the token-generation contrast because that is the landed
template vocabulary. D-122 additionally requires a prompt-processing contrast;
the missing prompt token family is recorded under discrepancies rather than
invented here.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[E_decode_contrast_signed_J_per_request]` | Prospective claim-verdict artifact `contrasts[decode].estimator.estimate`; orientation must remain condition B minus condition A | gamma / decode contrast | MEASURED | KEY_FROZEN / VALUE_UNISSUED; exact contrast identifier freezes with the D-122-compliant gamma pack | TPL, CV, AUTH |
| `[E_decode_contrast_lower_J]` | `contrasts[decode].deterministic_bounds.decision_interval.lower` | gamma / decode contrast | MEASURED | KEY_FROZEN / VALUE_UNISSUED | TPL, CV |
| `[E_decode_contrast_upper_J]` | `contrasts[decode].deterministic_bounds.decision_interval.upper` | gamma / decode contrast | MEASURED | KEY_FROZEN / VALUE_UNISSUED | TPL, CV |
| `[M_decode_contrast_abs_J_per_request]` | `abs(E_decode_contrast_signed_J_per_request)` | gamma / decode contrast | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL |
| `[F_claim_decode_armwise_max_J]` | `max(F_1p5B_decode_operative_J, F_7B_decode_operative_J)`; verify against the claim artifact's armwise floor gate | gamma consumer of alpha and beta decode floors | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED | TPL, DF, CV, MINT |
| `[B_decode_claim_J]` | UNKNOWN binding. Candidate field is `contrasts[decode].deterministic_bounds.total`, but no named authority equates that entire field with the template's claim-side `E_clock_anchor_shift_bound_j` magnitude | gamma / decode claim interval | STOP_FILL | SUPPLIER_UNKNOWN; resolve by naming the exact claim-side-bound output field in the gamma claim artifact | TPL, CV, DF |
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

The prose template fixes the semantic names and branch structure, but no
repository file in the authority set defines a characterization result schema
or the output field paths below. All numeric and outcome fills therefore stop.
The resolving unit must define one issued characterization verdict/report with
row identifiers, units, acceptance criteria, diagnostic presence flags, and
the fields named here before collection results are rendered.

| Exact token | Intended producing field | Campaign / row | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[S_C_linearity_request_J_per_token]` | UNKNOWN — fitted gross-request slope | characterization / linearity | STOP_FILL | SUPPLIER_UNKNOWN; define in characterization report schema | TPL, DRAFT |
| `[S_C_linearity_decode_J_per_token]` | UNKNOWN — fitted token-generation slope | characterization / linearity | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[R_C_linearity_limit_J]` | UNKNOWN — frozen residual acceptance criterion carried into the issued report | characterization / linearity | STOP_FILL | SUPPLIER_UNKNOWN; criterion must be pre-registered, not outcome-selected | TPL, DRAFT |
| `[D_C_null_max_abs_J]` | UNKNOWN — largest authenticated absolute null ABBA difference | characterization / null response | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[R_C_micro_min_x_floor]` | UNKNOWN — lower authenticated effect-to-floor diagnostic bound | characterization / empirical floor | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[R_C_micro_max_x_floor]` | UNKNOWN — upper authenticated effect-to-floor diagnostic bound | characterization / empirical floor | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[D_C_additivity_J]` | UNKNOWN — registered phase-sum minus enclosing-request diagnostic | characterization / phase attribution | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[S_C_prompt_invariance_J_per_token]` | UNKNOWN — fitted prompt-processing slope against later output length | characterization / phase attribution | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[B_C_prompt_invariance_J_per_token]` | UNKNOWN — frozen prompt-invariance acceptance band | characterization / phase attribution | STOP_FILL | SUPPLIER_UNKNOWN; band must be pre-registered | TPL, DRAFT |
| `[D_C_reference_excursion_J]` | UNKNOWN — authenticated start/midpoint/end excursion | characterization / drift and settling | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[T_C_recovery_s]` | UNKNOWN — authenticated recovery-time result | characterization / drift and settling | STOP_FILL | SUPPLIER_UNKNOWN | TPL, DRAFT |
| `[N_C_eligible_sessions]` | UNKNOWN — eligible-session count under the registered identity/freshness rule | characterization / between sessions | STOP_FILL | SUPPLIER_UNKNOWN; a refused window contributes nothing | TPL, DRAFT |
| `[PLAIN_LANGUAGE_RESULT_linearity]` | UNKNOWN row-outcome enum, rendered through the template's closed phrase set | characterization / linearity | STOP_FILL | SUPPLIER_UNKNOWN; define row outcome and evidence predicate | TPL, LINT |
| `[PLAIN_LANGUAGE_RESULT_null]` | UNKNOWN row-outcome enum, rendered through the closed phrase set | characterization / null response | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[PLAIN_LANGUAGE_RESULT_floor]` | UNKNOWN row-outcome enum, rendered through the closed phrase set | characterization / empirical floor | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[PLAIN_LANGUAGE_RESULT_phase]` | UNKNOWN row-outcome enum, rendered through the closed phrase set | characterization / phase attribution | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[PLAIN_LANGUAGE_RESULT_drift]` | UNKNOWN row-outcome enum, rendered through the closed phrase set | characterization / drift and settling | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[PLAIN_LANGUAGE_RESULT_between_sessions]` | UNKNOWN row-outcome enum, rendered through the closed phrase set | characterization / between sessions | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[REFUSAL_REASON_window_C]` | Characterization whole-window verdict `status`, `idle_admission_core.conditions`, and `member_failures`, once an exact verdict basis is issued | characterization / whole window | MEASURED | KEY_FROZEN / VERDICT_UNISSUED | TPL, WV, AUTH |
| `[D_C_linearity_diagnostic_J_per_token]` | UNKNOWN refused-window diagnostic field | characterization / linearity diagnostic | STOP_FILL | SUPPLIER_UNKNOWN; define diagnostic presence and value field | TPL, LINT |
| `[D_C_null_diagnostic_J]` | UNKNOWN refused-window diagnostic field | characterization / null diagnostic | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[D_C_micro_diagnostic_x_floor]` | UNKNOWN refused-window diagnostic field | characterization / empirical-floor diagnostic | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[D_C_phase_diagnostic_J]` | UNKNOWN refused-window diagnostic field | characterization / phase diagnostic | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |
| `[D_C_drift_diagnostic_J]` | UNKNOWN refused-window diagnostic field | characterization / drift diagnostic | STOP_FILL | SUPPLIER_UNKNOWN | TPL, LINT |

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

| Draft site | Exact marker | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| Section 4 operative-floor hold, line 113 | `[RESULT PENDING CORRECTED ARTIFACTS]` | Four cell decompositions from all `F_*_abs_J`, `F_*_cmp_J`, and `F_*_operative_J` tokens | alpha and beta / all phase floor cells | DERIVE | DRAFT_GENERIC; replace only through guarded template output | DRAFT, TPL, DF |
| Section 6 linearity row, line 159 | `[PENDING WINDOW C]` | `PLAIN_LANGUAGE_RESULT_linearity` plus licensed linearity diagnostics | characterization / linearity | DERIVE | DRAFT_GENERIC; supplier unknown | DRAFT, TPL |
| Section 6 null row, line 160 | `[PENDING WINDOW C]` | `PLAIN_LANGUAGE_RESULT_null` plus licensed null diagnostic | characterization / null response | DERIVE | DRAFT_GENERIC; supplier unknown | DRAFT, TPL |
| Section 6 empirical-floor row, line 161 | `[PENDING WINDOW C]` | `PLAIN_LANGUAGE_RESULT_floor` plus licensed floor diagnostics | characterization / empirical floor | DERIVE | DRAFT_GENERIC; supplier unknown | DRAFT, TPL |
| Section 6 phase-attribution row, line 162 | `[PENDING WINDOW C]` | `PLAIN_LANGUAGE_RESULT_phase` plus licensed additivity/invariance diagnostics | characterization / phase attribution | DERIVE | DRAFT_GENERIC; supplier unknown | DRAFT, TPL |
| Section 6 drift row, line 163 | `[PENDING WINDOW C]` | `PLAIN_LANGUAGE_RESULT_drift` plus licensed excursion/recovery diagnostics | characterization / drift and settling | DERIVE | DRAFT_GENERIC; supplier unknown | DRAFT, TPL |
| Section 6 between-session row, line 164 | `[PENDING WINDOW C]` | `PLAIN_LANGUAGE_RESULT_between_sessions` and `N_C_eligible_sessions` when licensed | characterization / between sessions | DERIVE | DRAFT_GENERIC; supplier unknown | DRAFT, TPL |
| Section 7 branch hold, line 190 | `[RESULT PENDING CORRECTED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into this draft.]` | Exactly one guarded Section 7 template variant | alpha, beta, gamma | DERIVE | DRAFT_GENERIC; no value is a supplier | DRAFT, TPL, LINT |
| Table 1 prompt/1.5B gross cell, line 196 | `[PENDING]` | `E_1p5B_prompt_J_per_request` with lower and upper interval endpoints | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 prompt/1.5B per-token cell, line 196 | `[PENDING]` | `E_1p5B_prompt_J_per_token` | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 prompt/1.5B floor cell, line 196 | `[PENDING]` | `F_1p5B_prompt_operative_J` plus cell label branch | alpha / prompt floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| Table 1 prompt/1.5B count cell, line 196 | `[PENDING]` | `N_bundles_1p5B_prompt` | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 prompt/7B gross cell, line 197 | `[PENDING]` | `E_7B_prompt_J_per_request` with lower and upper interval endpoints | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 prompt/7B per-token cell, line 197 | `[PENDING]` | `E_7B_prompt_J_per_token` | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 prompt/7B floor cell, line 197 | `[PENDING]` | `F_7B_prompt_operative_J` plus cell label branch | beta / prompt floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| Table 1 prompt/7B count cell, line 197 | `[PENDING]` | `N_bundles_7B_prompt` | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 decode/1.5B gross cell, line 198 | `[PENDING]` | `E_1p5B_decode_J_per_request` with lower and upper interval endpoints | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 decode/1.5B per-token cell, line 198 | `[PENDING]` | `E_1p5B_decode_J_per_token` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 decode/1.5B floor cell, line 198 | `[PENDING]` | `F_1p5B_decode_operative_J` plus cell label branch | alpha / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| Table 1 decode/1.5B count cell, line 198 | `[PENDING]` | `N_bundles_1p5B_decode` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 decode/7B gross cell, line 199 | `[PENDING]` | `E_7B_decode_J_per_request` with lower and upper interval endpoints | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 decode/7B per-token cell, line 199 | `[PENDING]` | `E_7B_decode_J_per_token` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 1 decode/7B floor cell, line 199 | `[PENDING]` | `F_7B_decode_operative_J` plus cell label branch | beta / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| Table 1 decode/7B count cell, line 199 | `[PENDING]` | `N_bundles_7B_decode` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| Table 2 decode point estimate, line 205 | `[PENDING]` | `E_decode_contrast_signed_J_per_request` | gamma / decode contrast | MEASURED | VALUE_UNISSUED | DRAFT, TPL, CV |
| Table 2 decode interval, line 205 | `[PENDING, PENDING]` | `E_decode_contrast_lower_J`, `E_decode_contrast_upper_J` | gamma / decode contrast | MEASURED | VALUE_UNISSUED; one bracket marker contains two semantic fills | DRAFT, TPL, CV |
| Table 2 decode floor, line 205 | `[PENDING]` | `F_claim_decode_armwise_max_J` | gamma consuming alpha/beta decode floors | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| Table 2 decode clearance, line 205 | `[PENDING]` | `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; branch must be explicit | gamma / decode contrast | DERIVE | DRAFT/TEMPLATE SHAPE MISMATCH; draft has one unconditional cell | DRAFT, TPL |
| Table 2 decode claim-side bound, line 205 | `[PENDING]` | `B_decode_claim_J` | gamma / decode contrast | STOP_FILL | SUPPLIER_UNKNOWN | DRAFT, TPL, DF, CV |
| Table 2 decode floor-gate outcome, line 205 | `[PENDING]` | No exact template token; derive only from authenticated magnitude and claim floor, consistent with claim verdict | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; renderer contract must add a binding without renaming existing tokens | DRAFT, TPL, CV |
| Table 2 decode direction-gate outcome, line 205 | `[PENDING]` | No exact template token; derive only from the fully composed interval and registered direction | gamma / decode contrast | STOP_FILL | TOKEN_MISSING | DRAFT, TPL, CV |
| Table 2 decode verdict, line 205 | `[PENDING]` | No exact template token; candidate source `contrasts[decode].claim_evaluation.outcome` | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; bind a professor-facing conservative rendering | DRAFT, TPL, CV, AUTH |
| Table 2 prompt floor, line 206 | `[PENDING]` | No prompt claim-floor token exists; D-122 now requires a prompt contrast rather than floors-only prose | gamma consuming alpha/beta prompt floors | STOP_FILL | SUPERSEDED_DRAFT / TOKEN_FAMILY_MISSING | DRAFT, TPL, AUTH |
| Artifact locators, line 264 | `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | UNKNOWN release-manifest fields for repository commit, archive locator, and published digest manifest | release / artifact availability | STOP_FILL | SUPPLIER_UNKNOWN; resolve only after the release checklist issues the locators | DRAFT, AUTH |

## Authority discrepancies and non-token gaps

These are recorded rather than repaired because `docs/paper/draft-v1.md` is
read-only and the template vocabulary is binding.

| Gap | Conflict | Required resolution | Sources |
|---|---|---|---|
| Gamma prompt-processing contrast | The draft calls it unregistered and the template contains decode-only contrast tokens; D-122 requires the prospectively frozen prompt arm in gamma | The lead-owned draft/template edit train must add a guarded prompt token family, exact gamma contrast-row identifier, claim-bound field, floor/direction outcomes, and refusal branches before rendering | DRAFT, TPL, AUTH |
| D-123 reported means | D-123 authorizes mean cells, while no current extraction/report schema fixes their member basis or output field names | Land and audit the reported-mean schema in the alpha/beta packs and extraction output; prove floor outputs remain byte-identical; then replace `SUPPLIER_UNKNOWN` statuses | AUTH, FX, PLAN |
| Generic draft table outcomes | Draft Table 2 has generic cells for gate outcomes and verdict, but the template has no exact tokens for them | Add binding tokens or a machine renderer contract in the lead-owned template train; do not infer strings from variant headings | DRAFT, TPL, CV |
| Characterization outputs | The template names values and rows but no authoritative result schema defines their fields | Freeze the characterization analysis/report schema before collection and map every named token to an issued field | DRAFT, TPL |
| Global work-selection checkpoint | `RUN_STATE.md` currently gates ordinary agent-lane selection, while this branch was explicitly created and directly assigned for the paper scaffold | Lead should confirm this direct delegated branch is intentionally outside ordinary queue selection before merge review | `RUN_STATE.md`, direct task brief |

## Census and reconciliation

Census command shape: scan every non-newline bracket pair in the draft and
retain markers beginning with `PENDING`, `RESULT PENDING`, or `REPOSITORY AND
ARCHIVE LOCATORS PENDING`; scan the template with
`\[([A-Z][A-Za-z0-9_*.-]*)\]`; sort for the distinct vocabulary while retaining
the unsorted stream for occurrence counts. Markdown citations such as `[1]`
are excluded by construction.

- Draft: 34 bracket-marker sites, representing 35 semantic fill slots because
  the interval marker `[PENDING, PENDING]` contains two endpoints.
- Template: 436 token occurrences and 91 distinct exact tokens.
- Registry: 91 exact template-token rows plus 34 draft-site rows, for 125 fill
  rows. The separate discrepancy table contains no additional fill token and
  is excluded from that total.
- Reconciliation: all 91 template tokens occur literally in the exact-token
  tables; all 34 draft marker sites occur once in the draft-site table. The
  site-to-token gaps are explained in the discrepancy table rather than
  silently supplied.

## Lead double-checks before renderer implementation

- Confirm the final alpha/beta cell and artifact identifiers after their packs
  and post-collection pinsets land; this registry currently binds semantic
  roles plus stable output fields, not invented identifiers.
- Rule the exact D-123 reported-mean member basis and output schema; none of the
  twenty mean/interval/companion/count tokens is fillable yet.
- Name the gamma claim-side-bound field. Do not assume that the complete
  deterministic-bound total is identical to the template's clock-anchor
  claim-side term.
- Update the lead-owned draft/template train for D-122 prompt contrast and the
  missing Table 2 outcome tokens.
- Freeze a characterization result schema before using any Section 6 token.
- Keep D-119 conservative wording attached to every rendered figure, table,
  and caption; a stronger claim must name its evidence in the same sentence.
