# Reported phase-energy projection — D-179

Authority: the magistrate synthesis of 2026-09-08, recorded as D-179.
This is a bounded schema/registration increment. Production issuance remains
unregistered. Synthetic arithmetic and fixture custody are non-issuing.

## Closed registration and ordering fence

Both `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py` and
`configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py` install executable
`projection_registration` and sibling `phase_ratio_estimand` objects on each
reported cell. `reported_energy_registration.registration_sha256` hashes the
ordered three-object registration manifest, using UTF-8 JSON with sorted keys,
compact separators, no newline and finite numbers. Registration schema:
`joulewise.paper_reported_energy_registration.v1`.

| Model | Registration SHA-256 (procedure metadata, not a production evidence pin) |
|---|---|
| qwen3-1p7b | d89011dbda01172c41ebaa200d2410b37419fc2ee626700945a811d51b136952 |
| qwen3-8b | 88e0f5c179a7ecccb1f048f209e25ed0f239772cc078cf650c50957beceab138 |

These digests must be recorded before the first frozen extraction specification
exists. The generators now register estimands; the absent specification still
blocks numbers. Before first issuance the lead must establish the registration
source/digest's prior existence and bind it to the frozen spec; a digest written
inside an already-created spec cannot establish this temporal ordering. This
increment neither creates a frozen spec nor claims that future ordering proof.

Every registration binds the full identifier
`d117-reported-mean-ph-{decode|prefill-p42|prefill-p512}-{qwen3-1p7b|qwen3-8b}`.
The closed values/keys are in `reported_energy_registration`; validation compares
the entire object, not a subset. All three registrations per model are required,
in that order. The floor `cells` projection and existing B8 `ratio_estimand`
remain unchanged. Numeric values remain null in registration.

## Membership, energy and uncertainty

Each reported cell has exactly fifty ordered `{ordinal,bundle_id,config_sha256}`
rows (ordinals 1–50). The first ten are absolute repeats. The remaining forty
are ten complete blocks ordered A1, B1, B2, A2. The independent floor-spec census
must match both the member order and configuration pins. Decode and prefill-p42
share a physical universe; prefill-p512 has its separately registered universe.
Any missing, duplicated, reordered, invalid or provenance-mismatched member
refuses the energy cell. No post-collection admission filter and no 49-member
mean are permitted. `n_bundles = expected_n = 50` is never a floor-component count.

The numerator is gross `phase_energy_j.decode` or `phase_energy_j.prefill`,
using the registered phase boundary and whole-window basis. It is neither
idle-subtracted request energy nor a floor component's internal mean.
Each member has weight 1/50. Let r be the ten repeat energies and b the ten
four-member arithmetic block means. The independence census is twenty units,
not fifty: `m = 0.2 mean(r) + 0.8 mean(b)`.

Use sample standard deviations (ddof 1),
`V = 0.2² s_r²/10 + 0.8² s_b²/10`, reference df 9 and
`t(0.975,9) = 2.262157162798205`; `h = t sqrt(V)`.
The pooled `s/sqrt(20)` formula is rejected. This model does not establish
physical independence across blocks; the protocol's dependence caveat persists.

The registered deterministic kinds for this gross-phase path are exactly
`E_clock_anchor_shift_bound_j`, `E_interpolation_joint_edge_bound_j` and
`E_whole_window_drift_allowance_j`. Idle-power drift for idle-subtracted request
energy is inapplicable to this numerator. Each member must have a finite,
nonnegative recorded value for every kind, including an explicit zero where
appropriate. Missing does not mean zero. Average each kind over all fifty
members, then sum those averages into B. Endpoints are `m ∓ (h+B)` without
clamping the lower endpoint. The upstream adapter must preserve the registered
whole-window allowance allocation; it may not substitute a newly derived bound.
`detection_floor.py:sqrt(1+1/n)` is explicitly excluded by name, both as an
interval method and as a deterministic term. The approximately 1-J D-078
attribution floor is labelled beside the cell and never composed into it.

## Runtime-observed per-token sibling

`phase_ratio_estimand` has exactly `cell_id`, `form`, `numerator`, `phase`,
`denominator`, `denominator_unit`, `tokenizer_scope`, `output_policy_scope`.
The values are respectively the exact cell ID, `ratio_of_totals`,
`gross_phase_energy_j`, its phase, `runtime_observed_output_tokens` for decode
or `runtime_observed_prompt_tokens` for prefill, `token`,
`same_identity_required`, `same_policy_required`.

Compute `ΣE_i / ΣT_i` over the same fifty members. Decode consumes observed
output; prefill consumes observed total minus observed output. Require agreement
with prompt realization, tokenize-end and prefill-start counts (all four
surfaces). Counts must be integers, excluding booleans, and the phase denominator
must be positive. Absent, zero, malformed, configured or fallback-sourced counts,
or tokenizer/output-policy scope drift, refuse the per-token value without
changing the energy mean or silently dropping a member. Mean of ratios is rejected.

## Separate closed result and twenty outputs

`joulewise.paper_reported_energy_projection.v1` has exact top-level keys
`schema_version`, `mode`, `cells`. This increment emits only
`mode: test_fixture_non_issuing`. Its closed cell schema is recomputed by
`_validate_projection`: `cell_id`, `model`, `phase`, `members`, `mean_j`,
`lower_j`, `upper_j`, `n_bundles`, `independence_units`, `interval`,
`phase_ratio_estimand`, `per_token`, `binding`, `attribution_floor_composed`.
`interval` records exactly `method`, `n_r`, `n_b`, `df`, `s_r`, `s_b`, `variance`,
`h_j`, `kind_averages_j`, `B_j`. `per_token` records `status`, `energy_sum_j`,
`observed_token_sum`, `j_per_token`, `reason`; refusal has null denominator and
value and reason `runtime_observed_denominator_invalid`. Binding keys are
`model`, `cell_id`, `extraction_spec_sha256`, `selection_sha256`,
`prompt_pin_sha256`, `whole_window_basis_sha256`, `attribution_floor_j`.
Extra fields, copied counts and stale arithmetic refuse recomputation.

For each of the four paper cells (two models × decode or G2-a selected prefill),
the five prospective outputs are `mean_j`, `lower_j`, `upper_j`,
`per_token.j_per_token`, `n_bundles`: twenty outputs total. The concrete prefill
registration must match G2-a's `[PREFILL_LENGTH]`; a different selected length
cannot be relabelled p512 and requires a prospective registration revision.
All X5 placements remain `RETIRED_FALLBACK` under D-174.

## Custody and remaining production work

D-173 `open_paper_input(ReportedEnergyParentsRef(role,runs_root))` is the only
evidence entry. The existing closed D-117 mint-consumption `extraction_report`
remains intact: no `reported_energy_cells` field is inserted into it. The
separate frozen payload key is `reported_energy_projection`; the renderer
consumes that key only after its existing exact-type/token/grant checks.

The fixture-only extension accepts `projection_input` inside the synthetic
extraction-spec marker; its exact keys are `spec` and `cells`, with each cell
holding `rows` and `binding`. `_project_cell` specifies exact normalized row,
unit, token and bound keys. This field is NOT valid in a production extraction
specification or mint report. Synthetic `strict_valid` and provenance pins are
controlled test inputs, never substitutes for strict bundle replay. All existing
fixture roles remain non-issuing and do not dispatch production gates.

The source census includes the complete new owner module and validators, bundle
reader, deterministic-bound owner and typed whole-window validator, alongside
both existing extraction validators. Receipt hashes change when these sources
change. Fixture receipts are re-pinned only as fixture metadata.

Still required before a production gate can register: bind actual clean-Git
selection/prompt-pin and frozen extraction-spec parents; replay the closed
mint report; replay the whole-window validator with authentic/admitted status
and exact governing row, model, basis and membership; read every strict bundle
and all its transitive files through the mapped authentication session; derive
normalized phase energies, per-kind bounds and four token surfaces from those
reads; establish the registration-before-spec ordering proof; reopen the exact
census; then mint a separate verified projection with cell-specific grants.
No public normalized-record, evidence-dict, path or digest bypass is provided.
The kernel's checked equality of supplied synthetic pins is not this production
replay. These are explicit provenance/issuance gaps, not unresolved mean,
interval, denominator, count or independence-unit semantics.
