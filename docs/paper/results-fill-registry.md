# Results fill registry

Revised 2026-08-22 against `docs/paper/draft-v1.md` at commit `3f931d5`
(551 lines; the draft was verified unchanged through current HEAD `73764f0`).
This revision supersedes the `0e35990` authoring. Re-bind custody is
`docs/process_traces/2026-08-22-t20/registry-rebind-r2.md` (all seventeen
PROPOSED bindings ratified by the lead 2026-08-22); the
prior audit is
`docs/process_traces/2026-08-19-prep-sprint/paper-staging/registry-audit.md`.

Revised again 2026-08-24 against `docs/paper/draft-v1.md` at commit `a591a91`
(602 lines). This revision binds every characterization token to the frozen
characterization result specification landed at `ec11f3f`, and re-derives every
draft-site line locator by searching for that site's own anchor text. The
locators carried by the 2026-08-22 revision were already stale before the
Section 5 rewrite and the rewrite moved them again, so no single offset would
have repaired them. The change list this revision implements is
`docs/process_traces/2026-08-24-p06-codesign/06-registry-template-changes-needed.md`.

Locators re-derived again 2026-08-25 against `docs/paper/draft-v1.md` at 818
lines. Two Section 2 pointer comments were added to the draft on that date, both
above every draft site listed below, so all forty-two line locators moved down by
two lines. Each new number was re-derived the same way as the 2026-08-24
revision — by searching the draft for that site's own anchor text — rather than
by applying the offset blind, and every one of the forty-two was confirmed to sit
on its stated line. That pass changed nothing else: no marker string, supplier,
fill rule, freeze status, or census figure was touched, and the draft's rendered
prose and bracket-marker count were unchanged.

DS-08 marker re-bind, 2026-08-25. The magistrate ruled that Section 5 may carry
the retained point-floor and corner-widened-floor energies as labelled instrument
diagnostics, which requires DS-08's hold sentence to name the section it now
exempts. The exact-marker cell below therefore reads "Sections 3, 5, and 7" where
it read "Sections 3 and 7", byte-identical to the amended sentence at its draft
site; DS-08's supplier, campaign/cell, fill rule (`DERIVE`), freeze status, and
sources are unchanged, and no other row is affected. The Section 5 and Section 6
edits behind it are in-place text changes that added no lines to the draft, so
every line locator below still resolves — re-confirmed by anchor-text search over
all forty-two after the edit. The bracket-marker census is unaffected: the draft
still carries the same thirty-five `PENDING`-family marker sites, with DS-08's
site changing its text rather than the set gaining or losing a site.

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

### Attribution-dominance test terms (T26 ruling item 26)

The primary research question compares, per claim-bearing cell, a point-only
repeatability term (TERM A) against a timing-widened term (TERM B). TERM B as the
published GATE is already registered above as the operative floor. TERM A is NOT
emitted unconditionally: `joulewise/detection_floor.py` attaches the
`point_floor_diagnostic` container only when the dominance predicate is already true,
and the validator FORBIDS it when the predicate is false. A cell where the claim FAILS
therefore carries no emitted TERM A, so the falsifier cannot be read off an artifact
and TERM A is derived at the desk.

**The derivation, per component record** (`cells[].absolute` or `cells[].comparative`):

    A_unguarded = max( max_abs_residual_j (absolute) | max_abs_delta_j (comparative),
                       prediction_component_j )
    A_guarded   = guard_factor * A_unguarded

**Self-consistency proof (executed, two blind seats).** A Sol xhigh seat and a blind
Fable seat independently derived the identity and independently reproduced every
emitted `point_floor_diagnostic` available in the repository byte-for-value, and both
confirmed that container presence matches the recomputed predicate. Custody:
`docs/process_traces/2026-08-27-t26/term-a-derivation/`. The two seats agree on the
identity and on both open questions below.

**Two questions remain NEEDS-RULING and gate every row in this table:**

1. **Aggregation.** Nothing in code or contract combines the absolute and comparative
   point terms into one per-cell TERM A. Candidates: the component maximum, by analogy
   to `floor_gate_j = max(floor_abs_j, floor_cmp_j)`; per-component comparison with no
   aggregation, which is what the code's own predicate does; or selection of the
   component matching the claim's use. A sum has contrary evidence and is not a candidate.
2. **Which quantity is TERM B for the comparison.** The code's predicate compares an
   exact linear corner maximum that is never emitted; the emitted
   `corner_widened_guarded_floor_j` is greater than or equal to it. The drift-widened
   `floor_gate_j` adds a whole-window drift allowance, which is not a timing term, so
   comparing it against TERM A would test a different proposition and it is reported
   only as the gate.

Until both are ruled, every row below is `STOP_FILL`.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERM_A_1p5B_prompt_J]` | Desk derivation over the alpha prompt cell's unconditional component fields `max_abs_residual_j`, `max_abs_delta_j`, `prediction_component_j`, `guard_factor` | alpha / prompt dominance TERM A | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; aggregation NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_B_1p5B_prompt_J]` | Same cell; NEEDS-RULING between `corner_widened_guarded_floor_j` and the exact derived predicate comparand | alpha / prompt dominance TERM B | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; TERM B semantics NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_A_1p5B_decode_J]` | Same derivation over the alpha decode cell | alpha / decode dominance TERM A | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; aggregation NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_B_1p5B_decode_J]` | Same cell; same TERM B alternatives | alpha / decode dominance TERM B | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; TERM B semantics NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_A_7B_prompt_J]` | Same derivation over the beta prompt cell | beta / prompt dominance TERM A | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; aggregation NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_B_7B_prompt_J]` | Same cell; same TERM B alternatives | beta / prompt dominance TERM B | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; TERM B semantics NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_A_7B_decode_J]` | Same derivation over the beta decode cell | beta / decode dominance TERM A | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; aggregation NEEDS-RULING | TPL, DF, MINT, PLAN |
| `[TERM_B_7B_decode_J]` | Same cell; same TERM B alternatives | beta / decode dominance TERM B | STOP_FILL | PROPOSED_KEY / VALUE_UNISSUED; TERM B semantics NEEDS-RULING | TPL, DF, MINT, PLAN |

`PROPOSED_KEY` marks a token whose name is not yet frozen because the quantity it
names is still under ruling. It is not a licence to render.

### Held title pair (T26 ruling item 28)

Neither title is typeset before `_v4` issues. The draft carries a neutral placeholder
H1 and both candidates as non-rendering comments. The choice is made by the outcome of
the attribution-dominance test, not by preference.

| Slot | Condition of use | Title |
|---|---|---|
| PRIMARY | `_v4` reproduces attribution dominance | Held in the draft's non-rendering title block; built around attribution-limited resolution of phase energy, and readable without prior exposure to either term. |
| NULL-OUTCOME | `_v4` does not reproduce dominance | Held in the same block; the protocol-first framing, under which the capstone is a calibration that corrected its own clock-model error followed by a prospective null. |

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

#### Terminal-refusal known-code set (F1 fold)

The conservative renderer's closed known-code set for
`[TERMINAL_REFUSAL_REASON_1p5B_prompt]`,
`[TERMINAL_REFUSAL_REASON_1p5B_decode]`,
`[TERMINAL_REFUSAL_REASON_7B_prompt]`,
`[TERMINAL_REFUSAL_REASON_7B_decode]`,
`[REFUSAL_REASON_1p5B_floor_window]`, and
`[REFUSAL_REASON_7B_floor_window]` includes these exact codes:

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
| `[B_decode_claim_J]` | Semantics RULED, binding NOT YET FLIPPED. T26 ruling Addendum 2 item 25 rules that the column means the contrast's WHOLE deterministic bound, `contrasts[decode].deterministic_bounds.total` — the quantity that expands the decision interval (`joulewise/analysis_engine/artifact.py:667`); `E_clock_anchor_shift_bound_j` is one named term inside `deterministic_bounds.terms[]` and is NOT this column. The row STAYS `STOP_FILL`, and the reason is a genuine conflict the magistrate must resolve, not a bookkeeping lag. `scripts/render_results_fills.py:977` contains a DELIBERATE guard — `_supplier_unknown("[B_decode_claim_J]")` — whose own comment reads: "Every A/B predicate requires the claim-side bound. The registry explicitly forbids binding the tempting deterministic total." That guard was built to forbid precisely the binding item 25 now rules correct. (`SUPPLIER_UNKNOWN_ROWS` is parsed from this registry's own Fill-rule column, so flipping the row here alone makes the guard's membership assertion fail and two renderer tests error.) Reconciling the ruling with that guard is a code change the paper director does not own. | gamma / decode claim interval | STOP_FILL | SUPPLIER_UNKNOWN pending the coupled renderer change; semantics resolved 2026-08-27 | TPL, CV, DF |
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
the plan is frozen; the six content anchors themselves are unchanged and each
still occurs exactly once, mechanically verified. Those sites remain
protocol-specification rows, not fillable result cells: results render through
the template's Section 6 variants, never by filling draft Table 1. Every line
number below was re-derived on 2026-08-24 by searching for the site's own
anchor text.

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DS-01 — Section 3 operative-floor hold, line 265 | `[RESULT PENDING ISSUED ARTIFACTS]` | Four cell decompositions from all `F_*_abs_J`, `F_*_cmp_J`, and `F_*_operative_J` tokens | alpha and beta / all phase floor cells | DERIVE | DRAFT_GENERIC; guarded template output only | DRAFT, TPL, DF |
| DS-02 — Section 5 characterization specification row, line 348 | `\| Workload response \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_linearity` plus licensed linearity diagnostics, only after an authenticated characterization report is issued | characterization / linearity | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-03 — Section 5 characterization specification row, line 349 | `\| Identical-condition null response \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_null` plus licensed null diagnostics, only after an authenticated characterization report is issued | characterization / null response | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-04 — Section 5 characterization specification row, line 350 | `\| Deliberate small-difference challenge \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_floor` plus licensed floor diagnostics, only after an authenticated characterization report is issued | characterization / empirical floor | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-05 — Section 5 characterization specification row, line 351 | `\| Phase accounting \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_phase` plus licensed additivity/invariance diagnostics, only after an authenticated characterization report is issued | characterization / phase attribution | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-06 — Section 5 characterization specification row, line 352 | `\| Drift and recovery \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_drift` plus licensed excursion/recovery diagnostics, only after an authenticated characterization report is issued | characterization / drift and settling | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-07 — Section 5 characterization specification row, line 353 | `\| Between-session stability \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_between_sessions` and `N_C_eligible_sessions`, only after an authenticated characterization report is issued | characterization / between sessions | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-08 — Section 6 results branch hold, line 405 | `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 5, and 7.]` | Exactly one guarded template result variant; template-internal section labels are not draft section locators | alpha, beta, gamma | DERIVE | DRAFT_GENERIC; no historical or diagnostic result is a supplier | DRAFT, TPL, LINT |
| DS-09 — Table 2 prompt/1.5B gross cell, line 411, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `E_1p5B_prompt_J_per_request` with lower and upper interval endpoints | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-10 — Table 2 prompt/1.5B per-token cell, line 411, col 4 under `J per prompt token` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `E_1p5B_prompt_J_per_token` | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-11 — Table 2 prompt/1.5B floor cell, line 411, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `F_1p5B_prompt_operative_J` plus cell label branch | alpha / prompt floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-12 — Table 2 prompt/1.5B count cell, line 411, col 7 under `n` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `N_bundles_1p5B_prompt` | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-13 — Table 2 prompt/7B gross cell, line 412, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `E_7B_prompt_J_per_request` with lower and upper interval endpoints | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-14 — Table 2 prompt/7B per-token cell, line 412, col 4 under `J per prompt token` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `E_7B_prompt_J_per_token` | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-15 — Table 2 prompt/7B floor cell, line 412, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `F_7B_prompt_operative_J` plus cell label branch | beta / prompt floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-16 — Table 2 prompt/7B count cell, line 412, col 7 under `n` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `N_bundles_7B_prompt` | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-17 — Table 2 decode/1.5B gross cell, line 413, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `E_1p5B_decode_J_per_request` with lower and upper interval endpoints | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-18 — Table 2 decode/1.5B per-token cell, line 413, col 5 under `J per output token` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `E_1p5B_decode_J_per_token` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-19 — Table 2 decode/1.5B floor cell, line 413, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `F_1p5B_decode_operative_J` plus cell label branch | alpha / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-20 — Table 2 decode/1.5B count cell, line 413, col 7 under `n` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `N_bundles_1p5B_decode` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-21 — Table 2 decode/7B gross cell, line 414, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `E_7B_decode_J_per_request` with lower and upper interval endpoints | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-22 — Table 2 decode/7B per-token cell, line 414, col 5 under `J per output token` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `E_7B_decode_J_per_token` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-23 — Table 2 decode/7B floor cell, line 414, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `F_7B_decode_operative_J` plus cell label branch | beta / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-24 — Table 2 decode/7B count cell, line 414, col 7 under `n` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `N_bundles_7B_decode` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-25 — Table 3 decode point estimate, line 420, col 2 under `Point estimate` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `E_decode_contrast_signed_J_per_request` | gamma / decode contrast | MEASURED | VALUE_UNISSUED | DRAFT, TPL, CV |
| DS-26 — Table 3 decode interval, line 420, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `E_decode_contrast_lower_J`, `E_decode_contrast_upper_J` | gamma / decode contrast | MEASURED | VALUE_UNISSUED; one bracket marker contains two semantic fills | DRAFT, TPL, CV |
| DS-27 — Table 3 decode floor, line 420, col 4 under `Cell floor` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `F_claim_decode_armwise_max_J` | gamma consuming alpha/beta decode floors | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-28 — Table 3 decode clearance, line 420, col 5 under `Clearance (point − floor)` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; branch must be explicit | gamma / decode contrast | DERIVE | DRAFT/TEMPLATE SHAPE MISMATCH; draft has one unconditional cell | DRAFT, TPL |
| DS-29 — Table 3 decode contrast deterministic bound, col 6 under `Comparison's own deterministic bound (deterministic_bounds.total)` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `B_decode_claim_J` | gamma / decode contrast | STOP_FILL | SUPPLIER_UNKNOWN | DRAFT, TPL, DF, CV |
| DS-30 — Table 3 decode floor-gate outcome, line 420, col 7 under `Floor-gate outcome` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; derive only from authenticated magnitude and claim floor, consistent with claim verdict | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; renderer contract must add a binding without renaming existing tokens | DRAFT, TPL, CV |
| DS-31 — Table 3 decode direction-gate outcome, line 420, col 8 under `Direction-gate outcome` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; derive only from the fully composed interval and registered direction | gamma / decode contrast | STOP_FILL | TOKEN_MISSING | DRAFT, TPL, CV |
| DS-32 — Table 3 decode verdict, line 420, col 9 under `Verdict` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; candidate source `contrasts[decode].claim_evaluation.outcome` | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; bind a professor-facing conservative rendering | DRAFT, TPL, CV, AUTH |
| DS-33 — Table 3 prompt floor, line 421, col 4 under `Cell floor` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No prompt claim-floor token exists; the draft arm is live and the template family is missing | gamma consuming alpha/beta prompt floors | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, AUTH |
| DS-34 — Section 9 evidence/code-availability locator hold, line 503 | `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | UNKNOWN release-manifest fields for repository commit, archive locator, and published digest manifest | release / artifact availability | STOP_FILL | SUPPLIER_UNKNOWN; resolve only after the release checklist issues the locators | DRAFT, AUTH |
| PG-01 — Table 3 prompt point estimate, line 421, col 2 under `Point estimate` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated prompt-contrast estimator field | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-02 — Table 3 prompt interval lower endpoint, line 421, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated fully composed lower endpoint | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-03 — Table 3 prompt interval upper endpoint, line 421, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated fully composed upper endpoint | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-04 — Table 3 prompt clearance, line 421, col 5 under `Clearance (point − floor)` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future branch-explicit clearance or shortfall derivation | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING; shape contract required | DRAFT, TPL, CV |
| PG-05 — Table 3 prompt contrast deterministic bound, col 6 under `Comparison's own deterministic bound (deterministic_bounds.total)` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token and no named claim-side-bound output field | gamma / prompt contrast | STOP_FILL | SUPPLIER_UNKNOWN | DRAFT, TPL, CV, AUTH |
| PG-06 — Table 3 prompt floor-gate outcome, line 421, col 7 under `Floor-gate outcome` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future conservative rendering consistent with authenticated magnitude, floor, and verdict | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV |
| PG-07 — Table 3 prompt direction-gate outcome, line 421, col 8 under `Direction-gate outcome` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future conservative rendering from the fully composed interval and registered direction | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-08 — Table 3 prompt verdict, line 421, col 9 under `Verdict` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt rendering token; future authenticated claim-evaluation outcome | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |

## Authority discrepancies and non-token gaps

These are recorded rather than repaired because `docs/paper/draft-v1.md` is
read-only and the template vocabulary is binding.

| Gap | Conflict | Required resolution | Sources |
|---|---|---|---|
| Gamma prompt-processing contrast | The current draft registers both contrast arms, while the template remains decode-only | The lead-owned template train must add the guarded prompt token family and exact identifiers for the point estimate, interval endpoints, claim floor, branch-explicit clearance or shortfall, claim-side bound, floor and direction outcomes, verdict, and refusal branches before rendering; DS-33 and PG-01 through PG-08 state this one-sided gap | DRAFT, TPL, AUTH |
| D-123 reported means | D-123 authorizes mean cells, while no current extraction/report schema fixes their member basis or output field names | Land and audit the reported-mean schema in the alpha/beta packs and extraction output; prove floor outputs remain byte-identical; then replace `SUPPLIER_UNKNOWN` statuses | AUTH, FX, PLAN |
| Generic draft table outcomes | Draft Table 3 has generic cells for decode and prompt gate outcomes and verdicts, but the template has no exact tokens for them | Add binding tokens or a machine renderer contract in the lead-owned template train; do not infer strings from variant headings | DRAFT, TPL, CV |
| Characterization outputs | RESOLVED 2026-08-24 as to the field contract: the frozen characterization result specification defines every named token's producing field, and this registry now binds each one. The draft's Section 5 still holds protocol-specification rows rather than claim-bearing result cells, which is by design | Issue an authenticated characterization report; until then every characterization row stays `KEY_FROZEN / VALUE_UNISSUED`. Ratify or replace the two-limb derivation recorded above | DRAFT, TPL, SPEC |

The folded capture-method-era and estimator-provenance preconditions authorize
no value.

## Census and reconciliation

Census command shape: scan every non-newline bracket pair in the draft and
retain markers beginning with `PENDING`, `RESULT PENDING ISSUED ARTIFACTS`,
or `REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST`; scan the
template with `\[([A-Z][A-Za-z0-9_*.-]*)\]`; sort for the distinct vocabulary
while retaining the unsorted stream for occurrence counts. Markdown citations
such as `[1]` are excluded by construction.

- Draft: 35 bracket-marker sites, representing 37 semantic fill slots because
  the two interval markers `[PENDING, PENDING]` each contain two endpoints.
  Re-counted 2026-08-24 after the Section 5 rewrite: unchanged. The rewritten
  Section 5 carries square brackets only inside LaTeX math, which the census
  command's marker prefixes exclude.
- Template: 437 token occurrences and 91 distinct exact tokens. The count
  rose by one on 2026-08-24: `[B_C_prompt_invariance_J_per_token]` was added
  to the Section 6 Variant B phase-attribution sentence, which is an added
  occurrence of an already-registered token, so the distinct vocabulary is
  unchanged.
- Registry: 91 exact template-token rows plus 42 draft-site rows, for 133
  census rows. The two swap-block-only rows are separately registered, have no
  landed template counterpart, and are excluded from the template-key census.
  The discrepancy table contains no additional fill token.
- Reconciliation: all 91 template tokens occur literally in the exact-token
  tables. Six draft-site rows, DS-02 through DS-07, bind content anchors whose
  former markers are absent. The remaining 36 marker-bound rows cover all 35
  bracket-marker sites: PG-02 and PG-03 share one interval marker, while DS-26
  carries two semantic fills in one row. Together those rows cover all 37
  semantic fill slots without silently supplying a site-to-token gap.

## Lead double-checks before renderer implementation

- Confirm the final alpha/beta cell and artifact identifiers after their packs
  and post-collection pinsets land; this registry currently binds semantic
  roles plus stable output fields, not invented identifiers.
- Rule the exact D-123 reported-mean member basis and output schema; none of the
  twenty mean/interval/companion/count tokens is fillable yet.
- Name the gamma claim-side-bound field. Do not assume that the complete
  deterministic-bound total is identical to the template's clock-anchor
  claim-side term.
- For D-122, add the guarded prompt token family to the template train; the
  draft arm is live. Add the missing Table 3 outcome tokens.
- The characterization result schema is frozen; what remains is an issued,
  authenticated characterization report. Ratify or replace the PROPOSED
  two-limb derivation for `[R_C_linearity_limit_J]` and
  `[B_C_prompt_invariance_J_per_token]` before either is rendered.
- Keep D-119 conservative wording attached to every rendered figure, table,
  and caption; a stronger claim must name its evidence in the same sentence.
