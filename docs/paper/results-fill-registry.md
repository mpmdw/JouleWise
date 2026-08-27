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
**HISTORICAL — superseded.** The thirty-five figure above describes the draft as it
stood on 2026-08-25 and is retained only as the record of that pass. It was carried
forward unchecked through round 2, which rewrote every section and changed the real
count. The binding census is the MEASURED one in the census section below: 34
bracket-marker sites and 36 semantic fill slots, with the recount command recorded
beside it. Do not cite the thirty-five figure as current.

Locators re-derived again 2026-08-27 against the current
`docs/paper/draft-v1.md` at 533 lines. Round 2 restructured and renumbered every
section, and round 3 restored Table 1's caption, inserted the Figure 2 and Figure
3 blocks, and added two `PENDING` markers, so the earlier locators were stale.
Each of the 141 existing line locators was checked by searching the current draft
for that row's own anchor text, never by applying an offset; 134 moved, and 138
were confirmed by re-reading the stated draft line. The DS-03
“Identical-condition null response,” DS-04 “Deliberate small-difference
challenge,” and DS-07 “Between-session stability” anchors no longer occur in
the draft, so their stale locators remain unchanged pending a ruling rather than
being guessed. Apart from the confirmed locator line and section numbers and
this note, this pass changed nothing else: no marker string, supplier, campaign
or cell, fill rule, freeze status, source list, or census figure was touched.

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

### Attribution-dominance test terms (T26 ruling item 34)

The primary research question replays the code's dominance predicate separately for
each claim-bearing cell's absolute and comparative components. There is no
component-to-cell aggregation for TERM A or TERM B. For component \(j\), TERM A is
the guarded point-only repeatability value:

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

The falsifier is verbatim code behavior: each component passes only when
`B_component > A_guarded_component`; equality fails. The emitted
`corner_widened_guarded_floor_j` is a different quantity: it is the published
component floor, includes the complete corner-maximized point formula, and is at
least TERM B. The cell's `floor_gate_j` is different again: it is the maximum of
the two component floors after each has received its whole-window drift allowance.
That drift allowance is not a timing term, so neither the published floor nor the
gate may replace TERM B in the dominance predicate.

TERM A remains a desk derivation because `point_floor_diagnostic` is conditional on
the predicate already being true. The Sol custody seat and blind Fable custody seat under
`docs/process_traces/2026-08-27-t26/term-a-derivation/` reproduced every emitted
diagnostic byte-for-value from the unconditional parents. The item-34 replay fence
must repeat that self-consistency check and independently derive TERM B for every
issued component. Until the authenticated four-cell artifact, its final pinset, and
the fence all pass, the rows remain `VALUE_UNISSUED` and rendering stops.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERM_A_1p5B_prompt_abs_J]` | Desk derivation over the alpha prompt cell's `cells[].absolute`: `guard_factor * max(max_abs_residual_j, prediction_component_j)` | alpha / prompt absolute dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_1p5B_prompt_abs_J]` | Same component; with `n = n`, `r_i = residuals_j[i]`, `w_i = admissible_half_widths_j[i]`, and `W = math.fsum(w_i)`, derive `max_i(abs(r_i) + w_i*(n-1)/n + (W-w_i)/n)` | alpha / prompt absolute dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_1p5B_prompt_cmp_J]` | Desk derivation over the alpha prompt cell's `cells[].comparative`: `guard_factor * max(max_abs_delta_j, prediction_component_j)` | alpha / prompt comparative dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_1p5B_prompt_cmp_J]` | Same component; derive `max_i(abs(block_deltas_j[i]) + admissible_half_widths_j[i])` with the two emitted arrays paired in their stored order | alpha / prompt comparative dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_1p5B_decode_abs_J]` | Desk derivation over the alpha decode cell's `cells[].absolute`: `guard_factor * max(max_abs_residual_j, prediction_component_j)` | alpha / decode absolute dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_1p5B_decode_abs_J]` | Same component; with `n = n`, `r_i = residuals_j[i]`, `w_i = admissible_half_widths_j[i]`, and `W = math.fsum(w_i)`, derive `max_i(abs(r_i) + w_i*(n-1)/n + (W-w_i)/n)` | alpha / decode absolute dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_1p5B_decode_cmp_J]` | Desk derivation over the alpha decode cell's `cells[].comparative`: `guard_factor * max(max_abs_delta_j, prediction_component_j)` | alpha / decode comparative dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_1p5B_decode_cmp_J]` | Same component; derive `max_i(abs(block_deltas_j[i]) + admissible_half_widths_j[i])` with the two emitted arrays paired in their stored order | alpha / decode comparative dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_7B_prompt_abs_J]` | Desk derivation over the beta prompt cell's `cells[].absolute`: `guard_factor * max(max_abs_residual_j, prediction_component_j)` | beta / prompt absolute dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_7B_prompt_abs_J]` | Same component; with `n = n`, `r_i = residuals_j[i]`, `w_i = admissible_half_widths_j[i]`, and `W = math.fsum(w_i)`, derive `max_i(abs(r_i) + w_i*(n-1)/n + (W-w_i)/n)` | beta / prompt absolute dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_7B_prompt_cmp_J]` | Desk derivation over the beta prompt cell's `cells[].comparative`: `guard_factor * max(max_abs_delta_j, prediction_component_j)` | beta / prompt comparative dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_7B_prompt_cmp_J]` | Same component; derive `max_i(abs(block_deltas_j[i]) + admissible_half_widths_j[i])` with the two emitted arrays paired in their stored order | beta / prompt comparative dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_7B_decode_abs_J]` | Desk derivation over the beta decode cell's `cells[].absolute`: `guard_factor * max(max_abs_residual_j, prediction_component_j)` | beta / decode absolute dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_7B_decode_abs_J]` | Same component; with `n = n`, `r_i = residuals_j[i]`, `w_i = admissible_half_widths_j[i]`, and `W = math.fsum(w_i)`, derive `max_i(abs(r_i) + w_i*(n-1)/n + (W-w_i)/n)` | beta / decode absolute dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |
| `[TERM_A_7B_decode_cmp_J]` | Desk derivation over the beta decode cell's `cells[].comparative`: `guard_factor * max(max_abs_delta_j, prediction_component_j)` | beta / decode comparative dominance TERM A | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; replay fence required; STOP_FILL on a missing, null, refused, unauthenticated, or method-mismatched parent | TPL, DF, MINT, PLAN |
| `[TERM_B_7B_decode_cmp_J]` | Same component; derive `max_i(abs(block_deltas_j[i]) + admissible_half_widths_j[i])` with the two emitted arrays paired in their stored order | beta / decode comparative dominance TERM B | DERIVE | DERIVATION_FROZEN / VALUE_UNISSUED; exact array order and replay fence required; STOP_FILL on any unavailable parent | TPL, DF, MINT, PLAN |

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
| `[B_decode_claim_J]` | NO SUPPLIER EXISTS. The registry's own rule governs and is unchanged: "Do not assume that the complete deterministic-bound total is identical to the template's clock-anchor claim-side term." T26 ruling Addendum 2 item 25 briefly ruled otherwise and was WITHDRAWN on verification by Addendum 3 item 33: `scripts/render_results_fills.py:977` carries a deliberate guard, `_supplier_unknown("[B_decode_claim_J]")`, whose comment states that the registry explicitly forbids binding the tempting deterministic total, and that code was right. The column is the CLAIM-SIDE bound as this registry defines it; the supplier is built post-`_v4`, and the sizing sum renders only then. | gamma / decode claim interval | STOP_FILL | SUPPLIER_UNKNOWN; supplier to be built post-`_v4` | TPL, CV, DF |
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
draft traced 98, left one (DG-097) narrowed to what its source supports, and converted 2. The two conversions are the Section 6 resolvability
example's realized record spacing: the draft asserted about 112 ms, and no issued artifact
supplies it — the measured all-trace median spacing for that bundle is about 120.9 ms.
Both sites are now `[PENDING]` markers (rows DG-071 and DG-075) and the marker census rose
from 35 to 37 accordingly.

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

#### Rows

| Draft site | Exact marker or anchor | Intended supplier / binding token | Campaign / cell | Fill rule | Freeze status | Sources |
|---|---|---|---|---|---|---|
| DG-001 — Abstract diagnostic scale, line 11 | about 1 J | A10/p2015-df-ph-prefill-abs-r01#energy_anchor_shift_envelopes[/phase_energy_j/prefill].max_abs_delta_j; descriptive about-one rendering | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-002 — Section 2 pre_spawn wall, line 99 | 1784757335.502742 | C#clock_anchor.clock_stamps.pre_spawn.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-003 — Section 2 pre_spawn mono-before, line 99 | 458736.4081875 | C#clock_anchor.clock_stamps.pre_spawn.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-004 — Section 2 pre_spawn mono-after, line 99 | 458736.408188666 | C#clock_anchor.clock_stamps.pre_spawn.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-005 — Section 2 pre_spawn R, line 99 | 0.0000010000000000000002 | max(C#...pre_spawn.wall_resolution_s, C#...pre_spawn.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-006 — Section 2 first_parse wall, line 100 | 1784757336.604396 | C#clock_anchor.clock_stamps.first_parse.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-007 — Section 2 first_parse mono-before, line 100 | 458737.509839458 | C#clock_anchor.clock_stamps.first_parse.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-008 — Section 2 first_parse mono-after, line 100 | 458737.509840291 | C#clock_anchor.clock_stamps.first_parse.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-009 — Section 2 first_parse R, line 100 | 0.0000010000000000000002 | max(C#...first_parse.wall_resolution_s, C#...first_parse.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-010 — Section 2 sampling_started wall, line 101 | 1784757337.0900722 | C#clock_anchor.clock_stamps.sampling_started.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-011 — Section 2 sampling_started mono-before, line 101 | 458737.995513416 | C#clock_anchor.clock_stamps.sampling_started.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-012 — Section 2 sampling_started mono-after, line 101 | 458737.995514666 | C#clock_anchor.clock_stamps.sampling_started.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-013 — Section 2 sampling_started R, line 101 | 0.0000010000000000000002 | max(C#...sampling_started.wall_resolution_s, C#...sampling_started.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-014 — Section 2 sampling_stopped wall, line 102 | 1784757533.877846 | C#clock_anchor.clock_stamps.sampling_stopped.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-015 — Section 2 sampling_stopped mono-before, line 102 | 458934.782846541 | C#clock_anchor.clock_stamps.sampling_stopped.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-016 — Section 2 sampling_stopped mono-after, line 102 | 458934.782848041 | C#clock_anchor.clock_stamps.sampling_stopped.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-017 — Section 2 sampling_stopped R, line 102 | 0.0000010000000000000002 | max(C#...sampling_stopped.wall_resolution_s, C#...sampling_stopped.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-018 — Section 2 post_parse wall, line 103 | 1784757533.8891652 | C#clock_anchor.clock_stamps.post_parse.epoch_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-019 — Section 2 post_parse mono-before, line 103 | 458934.794166 | C#clock_anchor.clock_stamps.post_parse.monotonic_before_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-020 — Section 2 post_parse mono-after, line 103 | 458934.7941665 | C#clock_anchor.clock_stamps.post_parse.monotonic_after_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-021 — Section 2 post_parse R, line 103 | 0.0000010000000000000002 | max(C#...post_parse.wall_resolution_s, C#...post_parse.monotonic_resolution_s) | retained 20260722 capture / clock | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-022 — Section 2 wall resolution, line 105 | 1.0000000000000002×10^-6 s | C#clock_anchor.clock_stamps.*.wall_resolution_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-023 — Section 2 monotonic resolution, line 105 | 4.166666666666666×10^-8 s | C#clock_anchor.clock_stamps.*.monotonic_resolution_s | retained 20260722 capture / clock | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-024 — Section 2 detected-pulse count, line 109 | 59 | R4#pulse_count with all_pulses_detected=true; RF replays P+E | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-025 — Section 2 rectangle count, line 109 | 122,859 | R4#projection_evaluated_cell_count; RF replays P+E | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-026 — Section 2 local anchor, line 109 | 0.0011349971959968978 s | R4#anchor_v3.effective_clock_anchor_bound_s; RF replays C+P | retained 20260722 capture / anchor | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-027 — Section 2 final capture bound, line 109 | 0.030067931757111657 s | R4#b_fiducial_v3_s; RF replays P+E+C | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-028 — Section 2 capture-bound arithmetic operand, line 109 | 0.030067931757111657 | same R4#b_fiducial_v3_s | retained 20260722 capture / pulse fit | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-029 — Section 2 anchor arithmetic operand, line 109 | 0.0011349971959968978 | same R4#anchor_v3.effective_clock_anchor_bound_s | retained 20260722 capture / anchor | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-030 — Section 2 residual subtraction, line 109 | 0.0289329345611147592 s | R4#b_fiducial_v3_s - R4#anchor_v3.effective_clock_anchor_bound_s, decimal rendering fixed by RF | retained 20260722 capture / pulse fit | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-031 — Section 2 maximal-pulse ordinal, line 109 | tenth | argmax over RF-replayed retained pulse endpoints from P+E+C; render index 9 as tenth | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-032 — Section 2 pulse-on plan offset, line 109 | 26.625 s | E#pulse_command_on occurrence 10.metadata.planned_on_offset_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-033 — Section 2 pulse-off plan offset, line 109 | 27.625 s | E#pulse_command_off occurrence 10.metadata.planned_off_offset_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-034 — Section 2 pulse-on epoch, line 109 | 1784757381.2856488 s | E#pulse_command_on occurrence 10.metadata.clock_stamp.epoch_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-035 — Section 2 pulse-off epoch, line 109 | 1784757382.293089 s | E#pulse_command_off occurrence 10.metadata.clock_stamp.epoch_s | retained 20260722 capture / pulse 10 | MEASURED | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH |
| DG-036 — Section 2 onset lower, line 109 | 0.02544938965763524 s | RF replay P+E+C, pulse 10 retained onset residual lower endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-037 — Section 2 onset upper, line 109 | 0.02893293456111476 s | RF replay P+E+C, pulse 10 retained onset residual upper endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-038 — Section 2 offset lower, line 109 | -0.008607394549133255 s | RF replay P+E+C, pulse 10 retained offset residual lower endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-039 — Section 2 offset upper, line 109 | -0.005308621075866744 s | RF replay P+E+C, pulse 10 retained offset residual upper endpoint | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-040 — Section 2 best-fit onset, line 109 | +0.027 s | RF replay P+E+C pulse 10 best delta_on; round 3 decimals | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-041 — Section 2 best-fit offset, line 109 | -0.007 s | RF replay P+E+C pulse 10 best delta_off; round 3 decimals | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-042 — Section 2 pulse residual bound, line 109 | 0.02893293456111476 s | max absolute value of DG-036 through DG-039 | retained 20260722 capture / pulse 10 | DERIVE | DIAGNOSTIC_ERA / REPLAY_FENCED | DRAFT, AUTH, DF |
| DG-043 — Section 3 retained-cell count, line 133 | three | len(XS#cells[0..2]) | historical a10 / three absolute cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-044 — Section 3 prefill point floor, line 133 | 0.2888 | A10 prefill members + DF guarded point-only computation; round 4 decimals | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-045 — Section 3 decode point floor, line 133 | 0.4934 | A10 decode members + DF guarded point-only computation; round 4 decimals | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-046 — Section 3 short-prefill point floor, line 133 | 0.3113 J | A10 short-prefill members + DF guarded point-only computation; round 4 decimals | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-047 — Section 3 prefill corner floor, line 133 | 3.153 | A10 prefill members + DF corner_widened_guarded_floor_j; round 3 decimals | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-048 — Section 3 decode corner floor, line 133 | 2.922 | A10 decode members + DF corner_widened_guarded_floor_j; round 3 decimals | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-049 — Section 3 short-prefill corner floor, line 133 | 2.184 J | A10 short-prefill members + DF corner_widened_guarded_floor_j; round 3 decimals | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-050 — Section 3 prefill ratio, line 133 | 10.92 | unrounded DG-047 / unrounded DG-044; round 2 decimals | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-051 — Section 3 decode ratio, line 133 | 5.92 | unrounded DG-048 / unrounded DG-045; round 2 decimals | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-052 — Section 3 short-prefill ratio, line 133 | 7.02 | unrounded DG-049 / unrounded DG-046; round 2 decimals | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-053 — Section 3 timing minimum, line 135 | 25.6 ms | min A10 members#energy_anchor_shift_envelopes[*].anchor_bound_s = 0.025619527535021 at decode r03; ×1000, round 1 decimal | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-054 — Section 3 timing maximum, line 135 | 31.1 ms | max same 30 fields = 0.031073829369128 at prefill r01; ×1000, round 1 decimal | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-055 — Section 3 timing-member count, line 135 | n=30 | sum len(XS#cells[0..2].members) | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-056 — Section 3 repeated timing-member count, line 135 | not 30 independent timing draws | same XS member-count derivation as DG-055 | historical a10 / all three cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-057 — Section 2 drift refusal screen, line 75 | 10.164835 ms | S17#decimal_derivation.ratified_operatives.maximum_budgetable_drift_s ×1000; round 6 decimals | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-058 — Section 2 bracket formula screen, line 78 | 9.724 ms | S17#decimal_derivation.ratified_operatives.bracket_screen_s ×1000 | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-059 — Section 2 named current screen, line 81 | 9.724 ms | same S17 bracket_screen_s | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-060 — Section 4 screen in seconds, line 191 | 0.009724 s | S17#decimal_derivation.ratified_operatives.bracket_screen_s | diagnostic calibration / n17 | MEASURED | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-061 — Section 4 screen reference, line 194 | 9.724-ms | S17#decimal_derivation.ratified_operatives.bracket_screen_s ×1000 | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-062 — Section 4 repeated screen, line 194 | 9.724 ms | same S17 bracket_screen_s ×1000 | diagnostic calibration / n17 | DERIVE | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-063 — Section 4 superseded screen, line 194 | 10.818 ms | S19#decimal_derivation.ratified_operatives.bracket_screen_s ×1000 | diagnostic calibration / n19 superseded | DERIVE | DIAGNOSTIC_ERA / SUPERSEDED_ISSUED_CONFIG; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-064 — Section 4 superseded corpus count, line 194 | nineteen | S19#derivation_corpus.n | diagnostic calibration / n19 superseded | MEASURED | DIAGNOSTIC_ERA / SUPERSEDED_ISSUED_CONFIG; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-065 — Section 4 current corpus count, line 194 | seventeen | S17#derivation_corpus.n | diagnostic calibration / n17 | MEASURED | DIAGNOSTIC_ERA / ISSUED_CONFIG | DRAFT, AUTH |
| DG-066 — Section 6 diagnostic population, line 277 | 50 | NR#stack_summaries[stack=1.5B].bundle_count | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-067 — Section 6 diagnostic failures, line 277 | 37 | NR#stack_summaries[stack=1.5B].resolvability.not_resolvable_sample_count | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-068 — Section 6 repeated population denominator, line 277 | 50 | same NR#bundle_count | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-069 — Section 6 diagnostic passes, line 277 | 13 | NR#stack_summaries[stack=1.5B].resolvability.identifiable | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-070 — Section 6 concrete prefill duration, line 286 | 0.121034145 s | NR#bundles[bundle=p2015-df-ph-decode-abs-r03].boundary.prefill_duration_s; verify R03E phase_end - phase_start; round 9 decimals | historical a10 / decode-abs-r03 prefill | DERIVE | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-071 — Section 6 unsupported cadence, line 286 | [PENDING] (DIAGNOSTIC-ERA VALUE: realized record spacing for p2015-df-ph-decode-abs-r03) | UNKNOWN; no primary artifact field or declared statistic produces 112 ms; do not infer from R03P | historical a10 / decode-abs-r03 prefill cadence | STOP_FILL | SUPPLIER_UNKNOWN; DIAGNOSTIC_ERA marker | DRAFT, AUTH |
| DG-072 — Section 6 two-overlap count, line 286 | two; 2 | NR#bundles[...r03].power.prefill_overlap_sample_count and NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[2] | historical a10 / r03 and population | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-073 — Section 6 three-sample threshold/count, line 286 | three; 3 | NR#bundles[...r03].resolvability.minimum_samples and NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[3] | historical a10 / r03 and population | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-074 — Section 6 rounded duration operand, line 286 | 0.121 | round NR r03 boundary.prefill_duration_s to 3 decimals | historical a10 / decode-abs-r03 prefill | DERIVE | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-075 — Section 6 unsupported cadence operand, line 286 | [PENDING] (DIAGNOSTIC-ERA VALUE: realized record spacing in seconds for p2015-df-ph-decode-abs-r03) | UNKNOWN; no primary artifact field or declared statistic produces 0.112 s; do not infer from R03P | historical a10 / decode-abs-r03 prefill cadence | STOP_FILL | SUPPLIER_UNKNOWN; DIAGNOSTIC_ERA marker | DRAFT, AUTH |
| DG-076 — Section 6 population with two overlaps, line 286 | 37 | NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[2] | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-077 — Section 6 population with three overlaps, line 286 | 13 | NR#stack_summaries[stack=1.5B].prefill_overlap_sample_count[3] | historical a10 / short-prefill resolvability | MEASURED | DIAGNOSTIC_ERA / ISSUED_RESULT; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-078 — Section 6 historical ABBA block count, line 298 | Ten | count AB block indices b01 through b10, each with a1,a2,b1,b2 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-079 — Section 6 historical prompt size, line 298 | 128-token | ABC#workload_profile.prompt_tokens for all 40 members | historical contrast / prefill | MEASURED | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-080 — Section 6 historical ABBA mean, line 298 | 5.809930 J | mean b01..b10 of (AB b1.prefill + b2.prefill - a1.prefill - a2.prefill)/2 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-081 — Section 6 projected prompt target, line 300 | 256 | DL#D-122 prospective prompt-processing target | prospective gamma / prefill sizing | MEASURED | DESIGN_FROZEN; PROJECTION_ONLY | DRAFT, AUTH |
| DG-082 — Section 6 historical denominator prompt, line 300 | 128 | ABC#workload_profile.prompt_tokens | historical contrast / prefill | MEASURED | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-083 — Section 6 repeated historical mean, line 300 | 5.809930 | same AB mean derivation as DG-080 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-084 — Section 6 projected effect, line 300 | 11.619860 J | (256/128) × unrounded DG-080 | prospective gamma / prefill sizing | DERIVE | DIAGNOSTIC_ERA INPUT / PROJECTION_ONLY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-085 — Section 6 approximate planning bar, line 302 | approximately 5 J | DL D-122 retained practical bar; copy only as approximate; exact components remain pending | prospective gamma / prefill sizing | MEASURED | ISSUED_APPROXIMATION; SIZING_ONLY | DRAFT, AUTH |
| DG-086 — Section 6 128-token clearance label, line 302 | 128-token | ABC#workload_profile.prompt_tokens | historical contrast / prefill | MEASURED | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-087 — Section 6 128-clearance estimate operand, line 302 | 5.809930 | same AB mean derivation as DG-080 | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-088 — Section 6 128-clearance bar operand, line 302 | 5 | same DL approximate bar as DG-085 | prospective gamma / prefill sizing | MEASURED | ISSUED_APPROXIMATION; SIZING_ONLY | DRAFT, AUTH |
| DG-089 — Section 6 128-clearance result, line 302 | 0.809930 J | DG-087 - DG-088 | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-090 — Section 6 128 ratio, line 302 | 1.16 | unrounded DG-080 / 5; round 2 decimals | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-091 — Section 6 256-token clearance label, line 302 | 256-token | same DL D-122 target as DG-081 | prospective gamma / prefill sizing | MEASURED | DESIGN_FROZEN; PROJECTION_ONLY | DRAFT, AUTH |
| DG-092 — Section 6 256-clearance estimate operand, line 302 | 11.619860 | DG-084 | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-093 — Section 6 256-clearance bar operand, line 302 | 5 | same DL approximate bar as DG-085 | prospective gamma / prefill sizing | MEASURED | ISSUED_APPROXIMATION; SIZING_ONLY | DRAFT, AUTH |
| DG-094 — Section 6 256-clearance result, line 302 | 6.619860 J | DG-092 - DG-093 | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-095 — Section 6 256 ratio, line 302 | 2.32 | unrounded DG-084 / 5; round 2 decimals | prospective gamma / prefill sizing | DERIVE | PROJECTION_ARITHMETIC; SIZING_ONLY | DRAFT, AUTH |
| DG-096 — Section 6 selected prompt size, line 302 | 256 | same DL D-122 target as DG-081 | prospective gamma / prefill sizing | MEASURED | DESIGN_FROZEN; PROJECTION_ONLY | DRAFT, AUTH |
| DG-097 — Section 6 historical prompt ceiling, line 302 | 128 | max ABC#workload_profile.prompt_tokens; no 7B corpus above 128 tokens AMONG THE 40 CONTRAST CONFIGURATIONS named by ABC (narrowed by Addendum 4 item 43; the 40 configs cannot establish absence across all historical corpora, and no inventory is commissioned) | historical contrast / prefill | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; SIZING_ONLY | DRAFT, AUTH |
| DG-098 — Section 7 repeated retained-cell count, line 328 | three | len(XS#cells[0..2]) | historical a10 / three absolute cells | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH |
| DG-099 — Section 7 repeated prefill ratio, line 328 | 10.92 | same derivation as DG-050 | historical a10 / prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-100 — Section 7 repeated decode ratio, line 328 | 5.92 | same derivation as DG-051 | historical a10 / decode absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |
| DG-101 — Section 7 repeated short-prefill ratio, line 328 | 7.02 | same derivation as DG-052 | historical a10 / short-prefill absolute | DERIVE | DIAGNOSTIC_ERA / AUTHENTICATED_PRIMARY; NON_CLAIM_BEARING | DRAFT, AUTH, DF |

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
| DS-01 — Section 4 operative-floor hold, line 219 | `[RESULT PENDING ISSUED ARTIFACTS]` | Four cell decompositions from all `F_*_abs_J`, `F_*_cmp_J`, and `F_*_operative_J` tokens | alpha and beta / all phase floor cells | DERIVE | DRAFT_GENERIC; guarded template output only | DRAFT, TPL, DF |
| DS-02 — Section 3 characterization specification row, line 124 | `\| Workload response \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_linearity` plus licensed linearity diagnostics, only after an authenticated characterization report is issued | characterization / linearity | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-03 — Section 3 characterization criteria row, line 125 | `**Identical-condition null:**` content anchor (RE-ANCHORED 2026-08-27, Addendum 4 item 40: the site survives in the main text at Section 3 line 125; the round-2 rewrite renamed the row from "Identical-condition null response" and the anchor was re-derived by search, not by offset); the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_null` plus licensed null diagnostics, only after an authenticated characterization report is issued | characterization / null response | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-04 — Section 5 characterization specification row, line 350 | `\| Deliberate small-difference challenge \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_floor` plus licensed floor diagnostics, only after an authenticated characterization report is issued | characterization / empirical floor | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |

**DS-04 RETIRED (Addendum 4 item 40).** The row immediately above is retained BYTE-FOR-BYTE as it stood before retirement, exactly as DS-08 was; retirement is recorded here, never by editing the retired row. This row bound a Section 5 characterization
site for the deliberate small-difference challenge. Addendum 1 item 12 demoted that criterion from characterization to Future
Work, and the round-2 rewrite removed the site accordingly, so the anchor no longer occurs in
the draft. The row is retired rather than re-anchored: no locator is ever guessed. Its bytes
are retained immediately above for provenance and must not be rendered.

| DS-05 — Section 3 characterization specification row, line 126 | `\| Phase accounting \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_phase` plus licensed additivity/invariance diagnostics, only after an authenticated characterization report is issued | characterization / phase attribution | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-06 — Section 3 characterization specification row, line 127 | `\| Drift and recovery \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_drift` plus licensed excursion/recovery diagnostics, only after an authenticated characterization report is issued | characterization / drift and settling | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |
| DS-07 — Section 5 characterization specification row, line 353 | `\| Between-session stability \|` content anchor; the row's former `TODO-EVIDENCE` guards were replaced by the Section 5 rewrite | `PLAIN_LANGUAGE_RESULT_between_sessions` and `N_C_eligible_sessions`, only after an authenticated characterization report is issued | characterization / between sessions | STOP_FILL | KEY_FROZEN / VALUE_UNISSUED; the frozen characterization result specification is the named supplier, and the specification row itself remains not a fillable result cell | DRAFT, TPL, SPEC |

**DS-07 RETIRED (Addendum 4 item 40).** The row immediately above is retained BYTE-FOR-BYTE as it stood before retirement, exactly as DS-08 was; retirement is recorded here, never by editing the retired row. This row bound a Section 5 characterization
site for between-session stability. Addendum 1 item 12 demoted that criterion from characterization to Future
Work, and the round-2 rewrite removed the site accordingly, so the anchor no longer occurs in
the draft. The row is retired rather than re-anchored: no locator is ever guessed. Its bytes
are retained immediately above for provenance and must not be rendered.

| DS-08a — Section 6 results branch hold, line 304 | `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 6, and 7.]` | Exactly one guarded template result variant; template-internal section labels are not draft section locators | alpha, beta, gamma | DERIVE | DRAFT_GENERIC; no historical or diagnostic result is a supplier | DRAFT, TPL, LINT |

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

| DS-09 — Table 2 prompt/1.5B gross cell, line 310, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `E_1p5B_prompt_J_per_request` with lower and upper interval endpoints | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-10 — Table 2 prompt/1.5B per-token cell, line 310, col 4 under `J per prompt token` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `E_1p5B_prompt_J_per_token` | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-11 — Table 2 prompt/1.5B floor cell, line 310, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `F_1p5B_prompt_operative_J` plus cell label branch | alpha / prompt floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-12 — Table 2 prompt/1.5B count cell, line 310, col 7 under `n` | `[PENDING]`; row anchor `\| prompt processing \| 1.5B \|` | `N_bundles_1p5B_prompt` | alpha / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-13 — Table 2 prompt/7B gross cell, line 311, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `E_7B_prompt_J_per_request` with lower and upper interval endpoints | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-14 — Table 2 prompt/7B per-token cell, line 311, col 4 under `J per prompt token` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `E_7B_prompt_J_per_token` | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-15 — Table 2 prompt/7B floor cell, line 311, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `F_7B_prompt_operative_J` plus cell label branch | beta / prompt floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-16 — Table 2 prompt/7B count cell, line 311, col 7 under `n` | `[PENDING]`; row anchor `\| prompt processing \| 7B \|` | `N_bundles_7B_prompt` | beta / prompt reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-17 — Table 2 decode/1.5B gross cell, line 312, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `E_1p5B_decode_J_per_request` with lower and upper interval endpoints | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-18 — Table 2 decode/1.5B per-token cell, line 312, col 5 under `J per output token` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `E_1p5B_decode_J_per_token` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-19 — Table 2 decode/1.5B floor cell, line 312, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `F_1p5B_decode_operative_J` plus cell label branch | alpha / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-20 — Table 2 decode/1.5B count cell, line 312, col 7 under `n` | `[PENDING]`; row anchor `\| token generation \| 1.5B \|` | `N_bundles_1p5B_decode` | alpha / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-21 — Table 2 decode/7B gross cell, line 313, col 3 under `Gross J/request (lower, upper)` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `E_7B_decode_J_per_request` with lower and upper interval endpoints | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-22 — Table 2 decode/7B per-token cell, line 313, col 5 under `J per output token` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `E_7B_decode_J_per_token` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-23 — Table 2 decode/7B floor cell, line 313, col 6 under `Cell floor (labeled)` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `F_7B_decode_operative_J` plus cell label branch | beta / decode floor | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-24 — Table 2 decode/7B count cell, line 313, col 7 under `n` | `[PENDING]`; row anchor `\| token generation \| 7B \|` | `N_bundles_7B_decode` | beta / decode reported mean | STOP_FILL | SUPPLIER_UNKNOWN under D-123 | DRAFT, TPL, AUTH |
| DS-25 — Table 3 decode point estimate, line 319, col 2 under `Point estimate` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `E_decode_contrast_signed_J_per_request` | gamma / decode contrast | MEASURED | VALUE_UNISSUED | DRAFT, TPL, CV |
| DS-26 — Table 3 decode interval, line 319, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `E_decode_contrast_lower_J`, `E_decode_contrast_upper_J` | gamma / decode contrast | MEASURED | VALUE_UNISSUED; one bracket marker contains two semantic fills | DRAFT, TPL, CV |
| DS-27 — Table 3 decode floor, line 319, col 4 under `Cell floor` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `F_claim_decode_armwise_max_J` | gamma consuming alpha/beta decode floors | DERIVE | VALUE_UNISSUED | DRAFT, TPL, DF |
| DS-28 — Table 3 decode clearance, line 319, col 5 under `Clearance (point − floor)` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `C_decode_floor_clearance_J` on passage or negative of `S_decode_floor_shortfall_J` on refusal; branch must be explicit | gamma / decode contrast | DERIVE | DRAFT/TEMPLATE SHAPE MISMATCH; draft has one unconditional cell | DRAFT, TPL |
| DS-29 — Table 3 decode contrast claim-side bound, col 6 under `Claim-side bound` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | `B_decode_claim_J` | gamma / decode contrast | STOP_FILL | SUPPLIER_UNKNOWN | DRAFT, TPL, DF, CV |
| DS-30 — Table 3 decode floor-gate outcome, line 319, col 7 under `Floor-gate outcome` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; derive only from authenticated magnitude and claim floor, consistent with claim verdict | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; renderer contract must add a binding without renaming existing tokens | DRAFT, TPL, CV |
| DS-31 — Table 3 decode direction-gate outcome, line 319, col 8 under `Direction-gate outcome` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; derive only from the fully composed interval and registered direction | gamma / decode contrast | STOP_FILL | TOKEN_MISSING | DRAFT, TPL, CV |
| DS-32 — Table 3 decode verdict, line 319, col 9 under `Verdict` | `[PENDING]`; row anchor `\| token generation, 7B − 1.5B \|` | No exact template token; candidate source `contrasts[decode].claim_evaluation.outcome` | gamma / decode contrast | STOP_FILL | TOKEN_MISSING; bind a professor-facing conservative rendering | DRAFT, TPL, CV, AUTH |
| DS-33 — Table 3 prompt floor, line 320, col 4 under `Cell floor` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No prompt claim-floor token exists; the draft arm is live and the template family is missing | gamma consuming alpha/beta prompt floors | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, AUTH |
| DS-34 — Section 9 evidence/code-availability locator hold, line 378 | `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | UNKNOWN release-manifest fields for repository commit, archive locator, and published digest manifest | release / artifact availability | STOP_FILL | SUPPLIER_UNKNOWN; resolve only after the release checklist issues the locators | DRAFT, AUTH |
| PG-01 — Table 3 prompt point estimate, line 320, col 2 under `Point estimate` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated prompt-contrast estimator field | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-02 — Table 3 prompt interval lower endpoint, line 320, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated fully composed lower endpoint | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-03 — Table 3 prompt interval upper endpoint, line 320, col 3 under `Interval [lower, upper]` | `[PENDING, PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future authenticated fully composed upper endpoint | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-04 — Table 3 prompt clearance, line 320, col 5 under `Clearance (point − floor)` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future branch-explicit clearance or shortfall derivation | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING; shape contract required | DRAFT, TPL, CV |
| PG-05 — Table 3 prompt contrast claim-side bound, col 6 under `Claim-side bound` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token and no named claim-side-bound output field | gamma / prompt contrast | STOP_FILL | SUPPLIER_UNKNOWN | DRAFT, TPL, CV, AUTH |
| PG-06 — Table 3 prompt floor-gate outcome, line 320, col 7 under `Floor-gate outcome` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future conservative rendering consistent with authenticated magnitude, floor, and verdict | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV |
| PG-07 — Table 3 prompt direction-gate outcome, line 320, col 8 under `Direction-gate outcome` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt token; future conservative rendering from the fully composed interval and registered direction | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |
| PG-08 — Table 3 prompt verdict, line 320, col 9 under `Verdict` | `[PENDING]`; row anchor `\| prompt processing, 7B − 1.5B \|` | No exact prompt rendering token; future authenticated claim-evaluation outcome | gamma / prompt contrast | STOP_FILL | TOKEN_FAMILY_MISSING | DRAFT, TPL, CV, AUTH |

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

- Draft: **34 bracket-marker sites, representing 36 semantic fill slots**, because the two
  interval markers `[PENDING, PENDING]` each contain two endpoints. MEASURED 2026-08-27
  against the current draft, not carried forward.
  **The previously stated 35/37 figures were stale and are corrected here.** They were last
  re-counted on 2026-08-24, before the round-2 restructure rewrote every section; that
  restructure changed the count to 32 sites / 34 slots and no pass re-counted it, so the
  stale pair survived into round 3 and was briefly propagated as 37/39. Addendum 3 item 38
  then added two sites — the Section 6 resolvability example's realized record spacing,
  which no issued artifact supplies (the measured all-trace median spacing for that bundle
  is about 120.9 ms, not the 112 ms the draft asserted), became registered `PENDING`
  markers with the diagnostic-era label (rows DG-071 and DG-075). 32 + 2 = 34 sites,
  34 + 2 = 36 slots.
  Recount command: count matches of `\[PENDING[^\]]*\]` in `docs/paper/draft-v1.md`,
  scoring a match containing a comma as two slots. The rewritten
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
  tables. Draft-site rows DS-02, DS-05 and DS-06 bind content anchors whose former
  markers are absent; DS-03 was re-anchored and DS-04 and DS-07 retired under Addendum 4
  item 40.
  **Marker-bound row recount, MEASURED 2026-08-27 under Addendum 4 item 45** (nothing here
  is carried forward). Command:

  ```sh
  grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[PENDING' docs/paper/results-fill-registry.md
  ```

  Result: **35 marker-bound rows** (25 DS, 8 PG, 2 DG). These reconcile exactly with the
  measured draft census of 34 bracket-marker sites and 36 semantic fill slots: 35 rows less
  the one site that carries two rows (PG-02 and PG-03 share a single interval marker) gives
  34 sites; and 32 single-slot sites plus the 2 interval sites at two endpoints each gives
  36 slots. DS-26 carries two semantic fills in one row, which changes neither total. No
  site-to-token gap is silently supplied.

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
