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

The mechanical fence is `verify_registration_ordering(repository, model)` in
`joulewise/paper_reported_energy.py`. It uses `git log --diff-filter=A
--no-renames HEAD -- <path>` to find the commit introducing that registration
owner (including its constants and `registration_sha256`) and the commit adding
`configs/campaigns/d117_floor_<model>_v5/extraction_spec.json`. The registration
commit must be a strict ancestor of the spec commit, checked with
`git merge-base --is-ancestor`; simultaneous addition refuses. Both the first
committed spec blob and the HEAD spec blob must contain
`reported_energy_registration.registration_sha256 == registration_sha256(model)`.
Missing, shallow or ambiguous addition history refuses; a later digest repair
cannot erase a spec that first existed with the wrong digest. This is a check
of committed Git ancestry, not author timestamps or a claim about untracked
files.
`paper_custody._register_reported_energy_gate` calls `_verify_gate_ordering`,
which requires a successful ordering result for both registered models before
inserting a gate. The custody dispatcher repeats this check against the current
repository before invoking a reported-energy gate, including one inserted
directly into the registry. Failed or absent ordering results refuse before the
gate body runs. The absent specification still blocks numbers;
this increment neither creates a frozen spec nor registers production issuance.

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
four-member arithmetic block means. The independence census is twenty units.
The CANONICAL computation is `m = statistics.fmean(energy)`, where `energy`
contains the ordered fifty member energies. Algebraic equivalence note only:
`m = 0.2 mean(r) + 0.8 mean(b)` in exact arithmetic; that expression is not the
canonical floating-point definition. Projection digests use the canonical
computed form, serialized as UTF-8 JSON with sorted keys, compact separators,
no newline and finite numbers; algebraically equivalent recomputations may
have different digests. Block means and kind averages also use
`statistics.fmean`; sample deviations use `statistics.stdev`, B uses
`math.fsum`, and endpoint evaluation is `m - h - B`, `m + h + B` in that order.

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

Compute `ΣE_i / ΣT_i` over the same fifty members. Decode requires only
`workload_observed.output_token_count` (normalized `output`) as its count
surface. Prompt surfaces may be absent or disagree without invalidating a
decode denominator. Prefill additionally requires the four bundle-reader
surfaces (`joulewise/bundle_read.py`, `count_surfaces`):

| Bundle field | Normalized token field |
|---|---|
| `workload_provenance.prompt.realized_token_count` | `prompt_realized` |
| `tokenize.end_metadata.prompt_tokens` | `tokenize_end` |
| `prefill.start_metadata.prompt_tokens` | `prefill_start` |
| `workload_observed.token_count-output_token_count` | `total - output` |

`_collapse_prompt_tokens` collapses these to one positive non-boolean int.
The two event surfaces are nonempty tuples (JSON arrays in fixture documents):
every element must be an integer, identical to every other element and equal
to both scalar surfaces. A previously collapsed scalar int is also accepted.
Any disagreement raises `paper_reported_energy_prompt_surfaces_disagree`;
absent, empty, ill-typed or nonpositive denominators raise
`paper_reported_energy_denominator_invalid`. For prefill, observed total and
output counts must be nonnegative non-boolean integers before subtraction.

Both phases require `source: runtime_observed` and valid, consistent
`tokenizer_sha256` / `output_policy_sha256` scope. Configured or fallback counts
and scope drift refuse the per-token value only, without changing the energy
mean or silently dropping a member. Mean of ratios is rejected.

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
value and the last caught typed refusal code in member order as `reason`.
Binding keys are
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
separate typed field is `reported_energy_projection: _FrozenObject | None`
on both `VerifiedReportedEnergyParents` and `FixtureReportedEnergyParents`.
The custody constructor initializes it in both branches; the future production
branch carries it from `_FamilyReplay.reported_energy_projection`. The renderer
consumes this field only after its existing exact-type/token/grant checks.
None raises `paper_reported_energy_projection_absent`, never `StopIteration`.
A non-None projection with missing or non-array `cells` raises
`paper_reported_energy_projection_mismatch` with empty `rendered_output`.
Private synthetic issuing controls exercise positive rendering; real fixture
capabilities remain non-issuing and cannot pass the public renderer's guard.

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

## Closed refusal vocabulary

`PaperReportedEnergyRefusal` carries `code` and empty `rendered_output`.
All energy-owner validation refusals use the following exhaustive vocabulary;
unknown codes and malformed input exceptions collapse to
`paper_reported_energy_request_invalid`. Denominator refusals are caught at the
per-token boundary and copied to its `reason`; other refusals abort the cell.
D-173 authentication refusals retain their separate custody vocabulary.

| Code | Condition |
|---|---|
| `paper_reported_energy_binding_mismatch` | Binding model or cell differs from the registered cell. |
| `paper_reported_energy_cell_census_invalid` | Reported or synthetic cells are not the three ordered registrations for one model. |
| `paper_reported_energy_cell_identity_invalid` | Cell ID is outside the closed model/phase/length identifiers. |
| `paper_reported_energy_cell_registration_mismatch` | Cell metric, count, reducer, phase or sibling differs from its registration. |
| `paper_reported_energy_denominator_invalid` | Count evidence is absent, ill-typed, empty, nonpositive, configured or fallback-sourced. |
| `paper_reported_energy_digest_invalid` | A required digest is not 64 lowercase hexadecimal characters. |
| `paper_reported_energy_floor_census_invalid` | The independent floor census does not have six cells. |
| `paper_reported_energy_floor_identity_mismatch` | Floor cell IDs do not match the registered model/phase. |
| `paper_reported_energy_floor_member_mismatch` | Ordered members or configuration pins differ from the floor census. |
| `paper_reported_energy_floor_stratum_mismatch` | Floor stratum kind, size, phase metric or block shape differs. |
| `paper_reported_energy_member_count_invalid` | The cell or normalized rows do not contain all fifty members. |
| `paper_reported_energy_member_duplicate` | A bundle ID repeats within the fixed universe. |
| `paper_reported_energy_member_identity_invalid` | A member has no nonempty string bundle ID. |
| `paper_reported_energy_member_order_invalid` | An ordinal is ill-typed or out of order. |
| `paper_reported_energy_model_invalid` | The model is outside the two registered Qwen3 models. |
| `paper_reported_energy_number_invalid` | Energy, floor or bound is nonfinite, boolean, ill-typed or negative. |
| `paper_reported_energy_ordering_history_invalid` | Git read fails, history is shallow/ambiguous/absent, or spec metadata cannot be read. |
| `paper_reported_energy_projection_absent` | The typed projection field is None after the renderer custody guard. |
| `paper_reported_energy_projection_mismatch` | The supplied projection differs from canonical recomputation, or a renderer projection has missing or non-array `cells`. |
| `paper_reported_energy_prompt_surfaces_disagree` | Prefill scalar counts or any tuple elements disagree. |
| `paper_reported_energy_ratio_estimand_invalid` | The sibling estimand differs from its exact registered object. |
| `paper_reported_energy_record_identity_mismatch` | Row order, member, model, phase or provenance pin differs. |
| `paper_reported_energy_record_invalid` | A member is not strictly valid or its repeat/ABBA unit is incorrect. |
| `paper_reported_energy_registration_digest_mismatch` | The spec registration digest differs from registration_sha256(model). |
| `paper_reported_energy_registration_invalid` | Registration metadata is malformed or changed, including prediction-term substitution. |
| `paper_reported_energy_registration_not_before_spec` | The registration addition is not a strict ancestor of the spec addition. |
| `paper_reported_energy_request_invalid` | Malformed input or arithmetic/serialization exception outside a more specific refusal. |
| `paper_reported_energy_schema_invalid` | An exact object has missing, extra or ill-typed keys, including the bound-kind census. |
| `paper_reported_energy_spec_binding_mismatch` | The synthetic binding digest differs from its frozen input spec. |
| `paper_reported_energy_spec_invalid` | The extraction-spec validator reports errors. |
| `paper_reported_energy_token_scope_mismatch` | Tokenizer or output-policy digest changes between members. |
