# P06 — registry and template changes the frozen schema now requires

Written by the schema implementer for the owner of the results-fill registry
and the template train. **Nothing in `docs/paper/results-fill-registry.md`,
`docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md`, or
`lint_results_prose_template.py` was edited by this branch.** This file is the
precise change list, not a patch.

Sources: `docs/contracts/characterization_result_schema_v1.md` (normative, no
values) and `configs/campaigns/metrology_v1/characterization_result_schema_v1.json`
(the frozen specification, which carries every producing field path). Both
landed on branch `paper/p06-schema-v1`.

## 0. What did NOT change, so nobody re-audits it needlessly

- **No new bracket token.** The ruling folded the timing-attribution property
  into `phase_attribution` as conjunctive subtests C4.3–C4.7, precisely so no
  token family, no template amendment, and no lint change would be needed for
  it. The 91-distinct-token census is unaffected by the schema itself.
- **No public row added, renamed, or split.** The six row identifiers stay
  `linearity, null, empirical_floor, phase_attribution, drift_settling,
  between_sessions`, exactly as `lint_results_prose_template.py:777-788`
  binds them.
- **Template lint still passes** unchanged on this branch (verified:
  `results prose template lint: PASS`).
- **`build_capstone.py --profile rpt001 --check` still reports no drift**
  (verified before and after the draft edit).

## 1. Registry — characterization campaign token table (`results-fill-registry.md:249-276`)

Every row in that table currently reads `STOP_FILL` / `SUPPLIER_UNKNOWN`
because "no repository file in the authority set defines a characterization
result schema or the output field paths below." That sentence is now false:
the schema exists and names a producing field for every token. The table's
lead-in paragraph and every row below need updating.

The producing field paths are authoritative in the specification's
`render_map.rows` object. Reproduced here for convenience:

| Exact token | Producing field in the issued report | Proposed fill rule |
|---|---|---|
| `[S_C_linearity_request_J_per_token]` | `rows.linearity.observed_values.request_slope_j_per_token` | MEASURED |
| `[S_C_linearity_decode_J_per_token]` | `rows.linearity.observed_values.decode_slope_j_per_token` | MEASURED |
| `[R_C_linearity_limit_J]` | `rows.linearity.observed_values.applied_residual_limit_j` | DERIVE — see §2 below; this is the *binding* limit, not one limb |
| `[D_C_null_max_abs_J]` | `rows.null.observed_values.max_abs_block_delta_j` | MEASURED |
| `[R_C_micro_min_x_floor]` | `rows.empirical_floor.observed_values.min_effect_to_floor_ratio` | MEASURED |
| `[R_C_micro_max_x_floor]` | `rows.empirical_floor.observed_values.max_effect_to_floor_ratio` | MEASURED |
| `[D_C_additivity_J]` | `rows.phase_attribution.observed_values.max_abs_additivity_residual_j` | MEASURED |
| `[S_C_prompt_invariance_J_per_token]` | `rows.phase_attribution.observed_values.prefill_slope_j_per_token` | MEASURED |
| `[B_C_prompt_invariance_J_per_token]` | `rows.phase_attribution.observed_values.applied_invariance_band_j_per_token` | DERIVE — see §2 below |
| `[D_C_reference_excursion_J]` | `rows.drift_settling.observed_values.max_heldout_excursion_j` | MEASURED |
| `[T_C_recovery_s]` | `rows.drift_settling.observed_values.max_recovery_s` | MEASURED |
| `[N_C_eligible_sessions]` | `rows.between_sessions.observed_values.eligible_session_count` | MEASURED |
| `[D_C_linearity_diagnostic_J_per_token]` | `rows.linearity.diagnostics.decode_slope_j_per_token` | MEASURED, gated on `rows.linearity.diagnostic_present` |
| `[D_C_null_diagnostic_J]` | `rows.null.diagnostics.max_abs_block_delta_j` | MEASURED, gated on `rows.null.diagnostic_present` |
| `[D_C_micro_diagnostic_x_floor]` | `rows.empirical_floor.diagnostics.effect_to_floor_ratio` | MEASURED, gated on `rows.empirical_floor.diagnostic_present` |
| `[D_C_phase_diagnostic_J]` | `rows.phase_attribution.diagnostics.max_abs_additivity_residual_j` | MEASURED, gated on `rows.phase_attribution.diagnostic_present` |
| `[D_C_drift_diagnostic_J]` | `rows.drift_settling.diagnostics.max_heldout_excursion_j` | MEASURED, gated on `rows.drift_settling.diagnostic_present` |
| `[PLAIN_LANGUAGE_RESULT_linearity]` | `rows.linearity.row_outcome` | DERIVE through `render_map.outcome_phrases` |
| `[PLAIN_LANGUAGE_RESULT_null]` | `rows.null.row_outcome` | DERIVE through `render_map.outcome_phrases` |
| `[PLAIN_LANGUAGE_RESULT_floor]` | `rows.empirical_floor.row_outcome` | DERIVE through `render_map.outcome_phrases` |
| `[PLAIN_LANGUAGE_RESULT_phase]` | `rows.phase_attribution.row_outcome` | DERIVE through `render_map.outcome_phrases` |
| `[PLAIN_LANGUAGE_RESULT_drift]` | `rows.drift_settling.row_outcome` | DERIVE through `render_map.outcome_phrases` |
| `[PLAIN_LANGUAGE_RESULT_between_sessions]` | `rows.between_sessions.row_outcome` | DERIVE through `render_map.outcome_phrases` |

**Token-name crosswalk to watch.** Three plain-language tokens are spelled
differently from their row identifiers: `_floor` ↔ `empirical_floor`,
`_phase` ↔ `phase_attribution`, `_drift` ↔ `drift_settling`. The
specification writes the crosswalk out explicitly in `render_map.rows` rather
than leaving it to be inferred; the registry rows should cite it the same way.

**Freeze status.** These rows move from `SUPPLIER_UNKNOWN` to
`KEY_FROZEN / VALUE_UNISSUED`: the field contract now exists, but no
characterization report has been issued, so every fill still stops. Do not
move any row to a fillable state.

**Fail-closed carry-over, unchanged.** A missing report, an unknown refusal
class, or a failed hash predicate remains `STOP_FILL`. The specification's
`characterization_*` reason codes are closed and disjoint; an unrecognized
code stops rendering until registered, matching
`results-fill-registry.md:153-171`.

## 2. Two tokens are *limits*, not observations, and need a DERIVE rule

The template prints one residual limit and one invariance band, but the
ratified design gives each of those properties **two** limbs — a resolution
limb and a claim-anchored limb — and the row passes only if both hold.

The specification therefore defines the printed value as the **binding**
limb: the stricter of the two when both are available, and the sole available
limb otherwise. The rule is written out in the specification's
`render_map.derived_value_rules`, so the renderer never infers it.

- `[R_C_linearity_limit_J]` ← `min(H, F_operative)` for the metric the
  sentence is about, published as `applied_residual_limit_j`.
- `[B_C_prompt_invariance_J_per_token]` ← `min(L_H, L_F)`, published as
  `applied_invariance_band_j_per_token`.

Both limbs are separately reported per criterion in the issued report
(`rows[].criteria[].limit_applied`), so nothing is hidden by printing the
binding one. **This DERIVE rule is a decision the registry owner should
ratify or replace**; it is the one place where the schema had to choose what a
single-limit template sentence prints for a two-limb criterion.

## 3. `[B_C_prompt_invariance_J_per_token]` renders in Variant A only

Verified on this checkout: the token occurs at `DRAFT-RESULTS_PROSE.md:2460`
(Variant A) but is **absent from the Variant-B `phase_attribution` row tuple**
at `lint_results_prose_template.py:784-785`, which lists only
`D_C_additivity_J` and `S_C_prompt_invariance_J_per_token`. Consequently a
Variant-B render prints the observed prompt-invariance slope with no band to
compare it against.

Two coherent resolutions; the template-train owner picks one:

1. Add `B_C_prompt_invariance_J_per_token` to the Variant-B
   `phase_attribution` present-branch and to the lint row tuple, so both
   variants print slope-and-band together.
2. Record it deliberately as Variant-A-only, and add a registry note that the
   Variant-B phase sentence is slope-only by design.

The schema supports either; it publishes the band regardless.

## 4. Draft-site rows DS-02 … DS-07 (`results-fill-registry.md:304-309`)

Those six rows describe the §5 specification rows as `\| Property \|` content
anchors "with `TODO-EVIDENCE` guards", fill rule `STOP_FILL`, freeze status
"`SUPPLIER_UNKNOWN`; specification row is not a fillable result cell."

After the §5 rewrite on this branch:

- **The `TODO-EVIDENCE` guards are gone.** All twelve occurrences in §5 were
  replaced by frozen values, derivation rules, or an explicit statement that a
  value must be ratified before the plan is frozen. The six content anchors
  themselves (`| Workload response |`, `| Identical-condition null response |`,
  `| Deliberate small-difference challenge |`, `| Phase accounting |`,
  `| Drift and recovery |`, `| Between-session stability |`) are **unchanged
  and still occur exactly once each** — mechanically verified.
- **The `SUPPLIER_UNKNOWN` justification no longer holds**; update to
  `KEY_FROZEN / VALUE_UNISSUED` with the schema as the named supplier.
- **The "specification row is not a fillable result cell" ruling still holds**
  and should stay. Table 1 is the specification; the *results* still render
  through the template's §6 variants, not by filling Table 1.
- **No new bracket-marker site was created in §5**, so the 35-site / 37-slot
  draft census is unchanged. Please re-run the census to confirm — my §5 text
  contains square brackets only inside LaTeX math (`\([0.0227, 0.0336]\)`,
  `\([\bar E_{128},\ldots]\)`), the same shape §3 already carries.

## 5. Line-number drift in the registry's draft-site locators

The §5 rewrite lengthened `docs/paper/draft-v1.md` by 32 lines. Every registry
locator citing a line number **at or after old line 329** is now stale. Known
affected rows (locators only; the registry says these are locators, not
bindings):

| Registry row | Cited line | Live line on `origin/main` | Live line on this branch |
|---|---|---|---|
| DS-02 … DS-07 | 321–326 | 335–340 | 346–351 |
| DS-08 | 358 | 372 | 403 |
| DS-09 … DS-12 | 364 | 378 | 409 |
| DS-13 and later Table 2/3 rows | 365+ | 379+ | +31 from the live number |

DS-01 (Section 3) is **not** affected; it precedes §5, and the registry's own
line references for §3 and §4 are likewise unaffected. Two separate drifts are
in play: the registry's cited numbers were already stale on `origin/main`
before this branch, and §5's rewrite then added a further 32 lines to the file
(571 → 603) of which 31 fall after the Table 1 block. Re-derive the locators
rather than applying a single offset.

## 6. Analysis registry — AP-C1 … AP-C7 rows

The ruling's work order calls for AP rows. The specification is already
shaped to fill `docs/contracts/analysis_plans.md:17-36`, so the rows are
transcription rather than design. One row per public characterization row
plus one family row:

| AP row | Content source in the specification |
|---|---|
| AP-C0 (family) | `characterization_family`: `family_id` `characterization-metrology-v1`, `claim_role` `exploratory`, `multiplicity_rule` (explicitly exploratory, no confirmatory inference; Holm at `m = 2` over the inferential subfamily), `alpha`, `inferential_subfamily` `["C2.3", "C4.2a", "C4.2b"]` with the note that C4.2a/b are two limbs of one property so the denominator counts properties |
| AP-C1 | `rows[linearity]` — 7 criteria |
| AP-C2 | `rows[null]` — 4 criteria plus `c2_floor_mode` as the frozen conditional branch |
| AP-C3 | `rows[empirical_floor]` — 5 criteria plus `registered_targets` and `registered_directions` |
| AP-C4 | `rows[phase_attribution]` — 9 criteria (C4.1a/b closure, C4.2a/b invariance, C4.3–C4.7 attribution) |
| AP-C5 | `rows[drift_settling]` — 3 criteria |
| AP-C6 | `rows[between_sessions]` — 6 criteria plus `eligibility_predicate` |

Per-criterion, the specification already supplies `quantity`, `units`,
`estimator`, `sample_unit`, `minimum_n`, `decision_rule`, `limit` or
`derivation_rule`, `limit_basis`, `limit_basis_source`, `evidence_binding`,
`failure_outcome`, `reason_code_on_failure`, `consequence_if_contradicted`,
and `claim_ceiling`. The two AP fields it does **not** supply are
`Order/blocking/covariates` and `Linked manifests/bundle hashes`; the first
comes from each campaign's order manifest, the second is filled
post-execution.

**Four criteria cannot freeze yet.** `ed_input_ledger` in the specification
names them, each blocking only its own criterion:

| Item | Blocks | Ledger text |
|---|---|---|
| `sizing_tolerance_ratio` | C3.4 | no basis exists |
| `tau_float` | C4.1a | pinned code value or Ed ruling; the 1e-9 J proposal is not ruled and is not frozen |
| `heldout_reference_probe_count` | C5.1, C5.2 | window budget; proposed ≥ 3 |
| `r1_r2_fallback_absolute_limits` | C1.5, C1.7, C2.3, C2.4 | needed only if no matching floor is issued at freeze time; the design's single largest dependency |

## 7. Consequential draft edits that were out of scope for this branch

Flagged, not made. Each is in a section this branch was fenced out of.

**(a) DS-08's hold sentence (`draft-v1.md`, Section 6).** It promises that no
energy value from superseded artifacts "appears anywhere in this paper except
the explicitly labelled instrument diagnostics of Sections 3 and 7." The new
§5 worked substitutions were written to keep that promise true: they restate
only energy values the paper already carries in §3 and §7 (the 0.0 J
reintegration discrepancy, the 0.5094 J excursion against 0.652/0.658 J
allowances) and otherwise use timing and power values, which the sentence does
not cover and which §5 already contained. **If the magistrate wants §5 to
carry the retained point-floor energies as well** — the 0.2888 / 0.4934 /
0.3113 J point floors against 3.153 / 2.922 / 2.184 J corner-widened floors,
which would make the dominance worked example numeric rather than
counterfactual — then DS-08's sentence must be amended to name Sections 3, 5,
and 7. I judged the fence the stronger constraint and used the falsification
probe (envelope widths forced to zero flips the condition) as the dominance
worked example instead.

**(b) Section 7's attribution paragraph.** It quotes 25.6–31.1 ms as a corpus
range. §5's new C4.3 subtest exists because that composed bound is mostly one
shared session constant — on the retained run whose bound is 31.07 ms, 24.879
ms is the session's shared calibration term and only 6.195 ms is that run's
own. §5 now says so explicitly and names §3 and §7 as the sites that quote the
composed range. A cross-reference from §7 back to §5 would close the loop, but
§7 was out of scope.

**(c) Nothing in the conditional-insert block was touched.** All six
`REPLACE EXACT` anchors were mechanically re-verified after the §5 rewrite and
each still occurs exactly once in the body outside the block.

## 8. Campaign-side prerequisites the schema depends on but does not create

- `configs/campaigns/metrology_v1/micro_delta/` remains
  `freeze_status: "draft_pending_slope"` with only the `k0064` placeholder.
  Criterion C3.1 formalizes that dependency: the row cannot evaluate until an
  issued linearity slope supplier exists with a strictly earlier freeze
  ordinal.
- The held-out `reference_role` field C5.1 requires (`allowance_constructing`
  vs `held_out`, frozen at pack generation) does not yet exist in
  `configs/campaigns/window_references/`. It is a plan field, not a harness
  change.
- The `metrology_v1` freeze-namespace gap and the "Window C" naming collision
  are separately registered work and are untouched here.
