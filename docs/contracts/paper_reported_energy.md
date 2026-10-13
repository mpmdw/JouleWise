# Reported phase-energy projection — D-179

Authority: the magistrate synthesis of 2026-09-08, recorded as D-179.
It began as a bounded schema and registration increment with synthetic,
non-issuing arithmetic. Lane L9 (2026-10-13) added the block-5 amendment for
kept units and the production issuer; both are described under "Kept units" and
"Custody and the production issuer" below. Everything above those sections is
the full-universe contract, which is unchanged and still holds whenever all
twenty units of a cell are kept.

## Closed registration and ordering fence

Both `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py` and
`configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py` install executable
`projection_registration` and sibling `phase_ratio_estimand` objects on each
reported cell. `reported_energy_registration.registration_sha256` hashes the
ordered three-object registration manifest, using UTF-8 JSON with sorted keys,
compact separators, no newline and finite numbers. Registration schema:
`joulewise.paper_reported_energy_registration.v1`.

Prospective extension (2026-10-04 floor-seat ruling F1): the ordered roles are
`decode`, `prefill-p42`, and exactly one `prefill-p<L>`, where L is a D-166
ladder rung (512, 1024, 2048, 4096). `registration_manifest(model, L)` and
`registration_sha256(model, L)` select that manifest; the omitted L remains
512 for historical callers. The p512 objects, bytes and digests are unchanged.
The generator supplies L only after authenticating its prompt pin. The census
derives L from the pack's long-prefill condition-family workload declarations
(absolute and both comparative bindings must agree); a minimal spec may declare
`reported_energy_registration.prefill_prompt_tokens` instead. If both forms
are present they must agree. Undeclared historical specs retain L=512. Reported
cell names cannot supply length authority. Both floor identities and the reported
identity must use the declared L; a mixed family or a longer prompt labelled
`p512` refuses.

| Model | Registration SHA-256 (procedure metadata, not a production evidence pin) |
|---|---|
| qwen3-1p7b | d89011dbda01172c41ebaa200d2410b37419fc2ee626700945a811d51b136952 |
| qwen3-8b | 88e0f5c179a7ecccb1f048f209e25ed0f239772cc078cf650c50957beceab138 |

Prospective ladder-specific manifests (procedure metadata only):

| Model | L | Registration SHA-256 |
|---|---:|---|
| qwen3-1p7b | 1024 | f0066cda9197d50fc3a039ea3e728b37789cdccfb835881705d66defbcf2b883 |
| qwen3-8b | 1024 | 23e7d130b2fa9978452ebdb6ddaae195a22e6b480991d2233b92308e09fe4fda |
| qwen3-1p7b | 2048 | 5560857668f053c99d0369161d4735015f4678a160b7a8423c7a7f357a50f5ea |
| qwen3-8b | 2048 | 04657a74de839a48ebf6bf55fe66f299fdd2e6401353c76d87d4d6ae843dae79 |
| qwen3-1p7b | 4096 | 00563c28347edbad9ca97d10e8af584a91f81f2351a2353ee2a9833d10e550ec |
| qwen3-8b | 4096 | b1ed97fb33f88c79fb22825a1e49dbf35f1f8491ebc00b214c0ecda031f49147 |

The mechanical fence is `verify_registration_ordering(repository, model)` in
`joulewise/paper_reported_energy.py`. It uses `git log --diff-filter=A
--no-renames HEAD -- <path>` to find the commit introducing that registration
owner (including its constants and `registration_sha256`) and the commit adding
`configs/campaigns/d117_floor_<model>_v5/extraction_spec.json`. The registration
commit must be a strict ancestor of the spec commit, checked with
`git merge-base --is-ancestor`; simultaneous addition refuses. Both the first
committed spec blob and the HEAD spec blob must contain
`reported_energy_registration.registration_sha256 == registration_sha256(model, L)`
with the same declared L. For L=512 the original owner-addition fence is
unchanged. For a longer rung the registration commit is the first committed
addition of `PREFILL_LADDER_PROMPT_TOKENS = (512, 1024, 2048, 4096)` in that
owner (`git log --reverse -S <declaration>`); this prospective commit must
strictly predate the spec. The original p512 owner commit cannot authorize a
later ladder registration. Both models' ordering checks recognize their own
ladder-specific manifest digest.
Missing, shallow or ambiguous addition history refuses; a later digest repair
cannot erase a spec that first existed with the wrong digest. This is a check
of committed Git ancestry, not author timestamps or a claim about untracked
files.
`paper_custody._register_reported_energy_gate` calls `_verify_gate_ordering`,
which requires a successful ordering result for both registered models before
inserting a gate. The custody dispatcher repeats this check against the current
repository before invoking a reported-energy gate, including one inserted
directly into the registry. Failed or absent ordering results refuse before the
gate body runs. The gate `reported-energy.v1` is registered statically (see
"Custody and the production issuer"); the ordering check still runs before it
on every dispatch.

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
share a physical universe; prefill-p<L> has its separately registered universe.
Any missing, duplicated, reordered, invalid or provenance-mismatched member
refuses the energy cell. No post-collection admission filter and no 49-member
mean are permitted. `n_bundles = expected_n = 50` is never a floor-component count.
Block 5 amends exactly one thing in this paragraph: a unit that the harvest's
exclusion function removed is left out by the rule of "Kept units" below
(registration section 10 item 4). The registered universe stays fifty ordered
members, and nothing else may leave a member out.

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

## Kept units: the block-5 amendment (lane L9)

**Forcing problem.** A reported cell has ten repeats (one member each) and ten
quads (four members each, run A1, B1, B2, A2). Its fifty members therefore weigh
the repeats 0.2 and the quad members 0.8. After a block-5 window, the harvest's
exclusion function may remove a member; a removed repeat member removes that
repeat, and a removed quad member removes its whole quad. A plain mean over the
members that are left would then move weight between the two kinds of unit, by
an amount that depends on which units happened to be lost. The registered
estimator holds the weights at 0.2 and 0.8 whatever was kept.

**Terms.** A *unit* is a repeat or a quad. A *kept unit* is a unit none of whose
members the exclusion function removed; `derived/exclusions.json` of the window's
harvest archive is the only source of that fact. n_r and n_b are the numbers of
kept repeats and kept quads. r is the list of the kept repeats' phase energies;
b is the list of the kept quads' means, each the `statistics.fmean` of that
quad's four member energies.

**Arithmetic** (`estimate_reported_cell` in `joulewise/paper_reported_energy.py`;
analysis plan section 4):

1. Mean. When n_r = n_b = 10: `statistics.fmean` of the fifty energies in
   ordinal order, the canonical value above. Otherwise
   `m = 0.2 * fmean(r) + 0.8 * fmean(b)`. The branch is on the cell's own
   counts, not on whether the window lost a unit elsewhere.
2. Variance. `V = 0.2 ** 2 * s_r ** 2 / n_r + 0.8 ** 2 * s_b ** 2 / n_b`, with
   s_r and s_b the sample standard deviations (`statistics.stdev`) of r and b.
   The code keeps the expressions `0.2 ** 2` and `0.8 ** 2`, which differ from
   0.04 and 0.64 in the last binary digit, so that a full-count cell's bytes do
   not move.
3. Half-width. `h = T975[min(n_r, n_b) - 1] * sqrt(V)`. The degrees of freedom
   come from the smaller stratum, which is the conservative choice. `T975` holds
   nine frozen two-sided 95% Student-t quantiles; no quantile function runs at
   issue time:

   | Degrees of freedom | Literal |
   |---:|---|
   | 9 | 2.262157162798205 |
   | 8 | 2.306004135204166 |
   | 7 | 2.364624251592785 |
   | 6 | 2.44691185114497 |
   | 5 | 2.5705818356363155 |
   | 4 | 2.7764451051977943 |
   | 3 | 3.1824463052837095 |
   | 2 | 4.302652729749464 |
   | 1 | 12.706204736174705 |

   A reported cell has at least five kept units in each stratum, so it uses 4 to
   9 degrees of freedom; 1 to 3 are reached only by the two labelled
   below-minimum sensitivity lines (`minimum=None`).
4. Timing bounds. For each of the three kinds, the stratified average is
   0.2 times the mean over the kept repeats plus 0.8 times the mean over the
   members of the kept quads; at n_r = n_b = 10 it is the fifty-member mean. B
   is the `math.fsum` of the three averages. A kind that is missing on a kept
   member refuses the cell; it is never taken as zero.
5. Endpoints. `lower = m - h - B`, `upper = m + h + B`, in that order, not
   clamped.
6. Per token. 0.2 times (sum of energies over sum of tokens, kept repeats) plus
   0.8 times (the same ratio over the members of the kept quads): a ratio of
   totals inside each stratum, never a mean of per-member ratios. At
   n_r = n_b = 10 it is the fifty-member ratio of totals above. A bad
   denominator on any kept member refuses the per-token value only; the mean is
   still issued.
7. Attribution floor. The largest `E_clock_anchor_shift_bound_j` over the kept
   members, recorded with the member that attains it (the first in ordinal order
   on a tie) and the smallest value. It says how far phase-edge timing alone
   could move one member's phase energy. Its stratified average is already
   inside B; the largest value is printed beside the cell and never added:
   `attribution_floor_composed` is false in every record. A binding whose
   `attribution_floor_j` differs from that largest value refuses
   `paper_reported_energy_binding_mismatch`.

**Worked example (synthetic).** Repeats 10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8,
10.1, 10.0, 9.6 J; quad means 10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3,
10.1, 9.9 J; kind averages 0.010, 0.000 and 0.050 J, so B = 0.060 J.

| Kept | n_r, n_b | m (J) | s_r, s_b (J) | V | Degrees of freedom | h (J) | Interval (J) |
|---|---|---|---|---|---:|---|---|
| all | 10, 10 | 10.16 | 0.2, 0.182574 | 0.00229333 | 9 | 0.108332 | 9.991668 to 10.328332 |
| repeat 6 removed | 9, 10 | 10.153333 | 0.180278, 0.182574 | 0.00227778 | 8 | 0.110057 | 9.983277 to 10.323390 |
| repeat 6 and quads 5 and 9 removed | 9, 8 | 10.133333 | 0.180278, 0.166905 | 0.00237302 | 7 | 0.115189 | 9.958144 to 10.308523 |

In the last row a plain mean over the 41 kept members would give 10.129268 J,
because it weights the strata 9/41 and 32/41; and the larger stratum's 8 degrees
of freedom would give h = 0.112334 J. Neither is the registered value.

**The record.** With kept units a cell's record has the keys of the closed
schema below with the actual values (`n_bundles = n_r + 4 n_b`,
`independence_units = n_r + n_b`, `interval.n_r`, `interval.n_b`, `interval.df`;
`interval.method` keeps its registered string, whose "t9" names the full-count
case; `members` stays the registered fifty), and in addition `kept_units` and
`removed_units` (each a list of `{stratum, unit_id, ordinals}`),
`exclusions_sha256` (the SHA-256 of the file bytes of `derived/exclusions.json`),
`attribution_floor {value_j, attained_by, minimum_j}`, and each stratum's energy
and token sums inside `per_token`. The record of a cell computed without kept
units (`kept=None`) has none of these keys and its bytes are unchanged.

**Row census.** The rows given to the kernel are exactly the members of the kept
units, in ordinal order. A row of a removed unit, a missing row of a kept unit,
a duplicate, or a quad with other than four rows refuses
`paper_reported_energy_member_count_invalid`; this is what keeps a quad mean a
mean of four. Fewer than five kept units in a stratum refuses
`paper_reported_energy_kept_units_below_minimum`.

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
`schema_version`, `mode`, `cells` in `mode: test_fixture_non_issuing`. (The
production record of the issuer adds top-level keys; see "Custody and the
production issuer".) Its closed cell schema is recomputed by
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

## Custody and the production issuer

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

**The production issuer** (`joulewise/paper_reported_energy_issuer.py`;
`scripts/issue_reported_energy.py --window-index PATH --pack alpha|beta
--output PATH`). It takes no runs root, spec, bound or digest from the caller.
In this order it: selects the pack's analysed window from the window index;
opens the window's harvest archive; requires the repository's
`extraction_spec.json` and the pack's two `prefill_pin` files to equal the
archive's copies; loads the kept units; evaluates the window's calibration
bracket; builds the window's archive context from the archived verdict row; and
projects the three cells, each in its own refusal scope, so that a refusing
cell (the p42 cell, by registration) leaves the others issued.

Where each quantity of a row comes from:

| Quantity | Source |
|---|---|
| phase energy and the first bound kind | the member's summary as reduced again in memory under the window's operative bound (the calibration bracket's `b_fiducial_s`), which is what the consumption session serves; never the summary stored in the bundle, which was reduced under the pre-capture bound alone |
| the interpolation bound and the drift allowance | `deterministic_bounds` in `joulewise/analysis_engine/inputs.py`; the allowance is the one the harvest's `derived/neg8-allowance.json` names, read once per pack and halved per member there |
| tokens | the four prompt-count surfaces and the observed output count, as mapped above |
| model | the bundle's realized scientific identity, never the cell ID, so a bundle of the other model at this cell's ordinal refuses `paper_reported_energy_record_identity_mismatch` |
| the binding's three digests | the SHA-256 of the pack's `prefill_pin/selection.json` and `prefill_pin/prefill_prompt_pin.json`, and the verdict row's `evaluation_basis.sha256` |

A kept member whose consumption provenance lacks the operative bound, or carries
one that is not the window bracket's, stops the window
(`operative_bound_not_the_window_bracket`). A kept member of a target cell that
fails strict validation or its phase precheck stops the window
(`member_code_on_kept_unit`): the exclusion function kept it, so the two
programs disagree. A missing drift allowance refuses the cell with
`paper_reported_energy_whole_window_allowance_unrecorded`, which is the D-179
spelling of the analysis plan's `whole_window_drift_allowance_unrecorded`; the
record carries the plan's spelling beside it as `plan_code`.

The production record has `mode: production` and the top-level keys
`schema_version`, `mode`, `window {pack, plan_id, attempt, harvest_pin}`,
`exclusions_sha256`, `sensitivity_label`, `b_override_s`, `cells` and
`refused_cells [{cell_id, code, plan_code, target}]`. It holds no path, time or
host name, so two runs on the same bytes give the same file. The script writes
it once, as sorted compact JSON with a final newline, and exits 0 only when no
target cell is refused; its one line of standard output holds structure only
(cell IDs, n_r, n_b, per-token status, refusal codes, the file's SHA-256).
`b_override_s` is accepted for the sensitivity pass and refused
(`b_override_s_unsupported`) until that pass supplies a reduction at another
bound.

**The custody gate** `reported-energy.v1` is registered statically in
`paper_custody._ISSUANCE_GATES`. It replays `validate_extraction_spec`, the
registered-spec census and `validate_d117_mint_consumption_report`; identifies
the pack as the one whose sealed `extraction_spec.json` equals the supplied
bytes; runs the issuer again through the tracked window index, outside the
custody read session; requires the `g2a_selection` and `prompt_pin` inputs to
hash to the projection's binding digests and the `whole_window_basis` input to
be the JSON object whose `sha256` is the binding's whole-window basis digest;
and grants `cell` for each selected subject that issued. The two production
supply roles select the decode and prefill-p2048 cells of their model, never
p42.

Not exercised until the lane's integration stage: a full production
`open_paper_input` of these roles on a GAMMA-shaped synthetic custody, and the
sensitivity reduction at another bound. No public normalized-record,
evidence-dict, path or digest bypass is provided.

## Closed refusal vocabulary

`PaperReportedEnergyRefusal` carries `code` and empty `rendered_output`.
All energy-owner validation refusals use the following exhaustive vocabulary;
unknown codes and malformed input exceptions collapse to
`paper_reported_energy_request_invalid`. Denominator refusals are caught at the
per-token boundary and copied to its `reason`; other refusals abort the cell.
D-173 authentication refusals retain their separate custody vocabulary.

| Code | Condition |
|---|---|
| `paper_reported_energy_binding_mismatch` | Binding model or cell differs from the registered cell, or, with kept units, its attribution floor differs from the largest first-kind bound of the kept members. |
| `paper_reported_energy_cell_census_invalid` | Reported or synthetic cells are not the three ordered registrations for one model. |
| `paper_reported_energy_cell_identity_invalid` | Cell ID is outside the closed model/phase/length identifiers. |
| `paper_reported_energy_cell_registration_mismatch` | Cell metric, count, reducer, phase or sibling differs from its registration. |
| `paper_reported_energy_denominator_invalid` | Count evidence is absent, ill-typed, empty, nonpositive, configured or fallback-sourced. |
| `paper_reported_energy_digest_invalid` | A required digest is not 64 lowercase hexadecimal characters. |
| `paper_reported_energy_floor_census_invalid` | The independent floor census does not have six cells. |
| `paper_reported_energy_floor_identity_mismatch` | Floor cell IDs do not match the registered model/phase. |
| `paper_reported_energy_floor_member_mismatch` | Ordered members or configuration pins differ from the floor census. |
| `paper_reported_energy_floor_stratum_mismatch` | Floor stratum kind, size, phase metric or block shape differs. |
| `paper_reported_energy_kept_units_below_minimum` | A stratum has fewer than five kept units (fewer than two when the labelled sensitivity form asks for no minimum). |
| `paper_reported_energy_whole_window_allowance_unrecorded` | The window has no authenticated gross drift allowance (no archive context, or an allowance record that names none). |
| `paper_reported_energy_member_count_invalid` | The cell or normalized rows do not contain all fifty members, or, with kept units, the rows are not exactly the members of the kept units. |
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
