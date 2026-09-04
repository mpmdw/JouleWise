# Paper-I seat consult — Opus seat, CONTRACT lens (2026-09-04)

Base `9cab7f6e`, read-only except this file; every citation opened this session.
R1–R3 answer the scout's rows (`01-supplier-gap-scout.md:13,14,16`).

## R1 — D-123 reported-mean supplier

**(a) Already fixed.**
1. D-123 cl.1 (`decision_log.md:7988-7995`): means pre-register in the
   alpha/beta packs, **same 50 members, zero added collection**, conditional on the
   pack gate proving every floor computation **byte-identical**.
2. Table 2 caption (`draft-v1.md:276`): gross cell = estimate **plus
   composed endpoints**; per-token cell = value whose **runtime-observed
   denominator is fixed by the issuing schema**; **`n` counts admitted independent
   run bundles, not power records**.
3. `registry:862-877` freezes twenty names:
   `E_{1p7B,8B}_{prefill_p[PREFILL_LENGTH],decode}_J_per_request`, `_J_per_token`,
   `N_bundles_*`. DS-09/13/17/21 are one cell each: mean + both endpoints.
4. Denominator vocabulary exists and fails closed (`reduce.py:3735-3757`,
   `:399-414` D-058); and `floor.mean_j` (`floor_extraction.py:1350`) is no
   substitute — on a comparative cell members are block *differences* (`:2653-2717`)
   and `n_admitted` (`:1298,:2799`) counts blocks, both contradicting (2).

**(b) Minimal schema.** `joulewise.reported_phase_energy.v1`, closed keys:

```
cells[]: cell_id, arm_id, phase, model_id, mean_j_per_request,
  member_basis:{basis_kind:"independent_bundle", bundle_ids[],
                n_admitted_bundles:int, source_cell_id, member_sha256[]},
  interval:{lower_j, upper_j, composition_rule:"<registered id>", terms[]},
  per_token:{value_j|null, denominator_kind:"prompt_tokens"|"output_tokens",
    observed_token_count|null,
    denominator_source:"runtime_observed"|"server_usage", refusal_reason|null},
  provenance:{floor_artifact_sha256, pack_id, config_sha256[], byte_identity_receipt_sha256}
refusal:{scope:"artifact", reasons[]}   # whole-artifact, never per-cell
```

**Forbidden:** computing a mean from `bundle_ids`; deriving `n` rather than reading
`n_admitted_bundles` (mismatch refuses); computing
`per_token.value_j` as `mean_j_per_request / observed_token_count`; substituting
`workload_profile.output_tokens` (`reduce.py:362`) or any `config_fallback` count;
reading `floor.mean_j`, `floor.n`, `n_admitted`; composing an endpoint as
`mean ± anchor_shift_bound_j` (`floor_extraction.py:1247`); printing `0`/`—` for an
absent measurement. A `denominator_source` outside
`{runtime_observed, server_usage}` nulls `value_j`, stopping that cell only.

**(c) Rendering rule.** Gross cell prints `<mean_j_per_request> (<lower_j>,
<upper_j>)` from ONE record; per-token prints `<per_token.value_j>`; `n` prints
`<n_admitted_bundles>`. Stops use the frozen `STOP_FILL
{"label","reason","registry_row"}` shape (`render_results_fills.py:130-160`).

**(d) Fixture + one test.** 50-member alpha/beta prefill+decode summaries with
runtime-observed counts, plus a byte-copy of the detection-floor fixture. Test: four cells /
twenty values emitted deterministically **and** a before/after sha256 over every
detection-floor artifact proving zero changed bytes (D-123 cl.1);
a `stream_chunk_fallback` source or perturbed `n` refuses the artifact.

**(e) Waits.** All values; prefill cells also wait on G2-a for `[PREFILL_LENGTH]`.
`composition_rule` must name a *registered* rule — if none exists
at build time the field refuses rather than inventing one.

## R2 — gamma claim-evaluation renderer

**(a) Already fixed.**
1. **The claim-side bound enters no gate and is not the deterministic total.**
   `draft-v1.md:196`: the decision interval is the metrology interval widened by
   `deterministic_bounds.total`, which "is not the claim-side bound";
   `:200`: `B_claim` enters only the sizing disclosure `F+B`, "not an acceptance threshold"
   (enforced at `artifact-guide.md:141`, `render_results_fills.py:575,977`), so
   `B_decode_claim_J`/PG-05 may **not** alias `deterministic_bounds.total`.
2. Table 3 caption (`draft-v1.md:285`): interval = fully composed endpoints; floor = larger arm-specific exact-cell floor;
   sizing = `C=F+B`, signed clearance `|estimate|-C`; floor gate passes only when
   `|estimate|>F`; direction gate only when both endpoints are positive.
3. `_contrast_row` (`analysis_engine/__init__.py:1567-1644`) emits
   `contrast_id`, `estimator`, `deterministic_bounds.{terms,total,decision_interval}`,
   `floor` (`aggregation:"max_never_sum"`, `arm_gates[].floor_gate_j` `:487-501`), `claim_evaluation`. VERDICT vocabulary is closed at five — `not_estimable | not_resolvable | unresolved | equivalent |
   direction_supported` — with `direction ∈ {positive,negative,null}`,
   `claim_ready_for_l2_l3`, `claim_level_ceiling ∈ {L1,L2}` (`claims.py:326-410`).
4. **Refusal renderings are registered verbatim**, not re-authorable here:
   `not evaluated — required token-generation verdict absent` /
   `not evaluated — stopped before comparison: <issued reason>` (DS-32, `registry:876`);
   `... required prompt-processing verdict absent` (PG-08, `:887`). Both bind the
   retained Refusal cell to that rendering, not the marker.

**(b) Minimal schema.** ONE new field per contrast in `_contrast_row`, a
**sibling** of `deterministic_bounds`:

```
claim_side_bound:{value_j: float|null, bound_id:"<registered sizing-bound id>",
                  reason_codes[]}
```

`value_j=null` keeps DS-29/PG-05 and sizing cells DS-28/PG-04 at STOP_FILL while
every other Table-3 column renders.

**Forbidden:** reading `deterministic_bounds.total` or `terms[].*` for DS-29/PG-05;
summing `arm_gates[].floor_gate_j` (`max_never_sum`, `__init__.py:489`); computing a
gate outcome when `claim_evaluation.outcome` is absent, or one contradicting it;
inferring DS-32/PG-08 from any D-165 ratio disposition (`registry:876,887`);
matching a contrast by prefix/substring/index instead of exact `contrast_id`;
computing `C=F+B` with a component unissued; defaulting `[PREFILL_LENGTH]` when the
G2-a pin is absent.

**(c) Token family.** Decode names mirrored one-for-one, nothing renamed
(`registry:880-887`, all `TOKEN_FAMILY_MISSING`), with
`P=prefill_p[PREFILL_LENGTH]`: `E_P_contrast_signed_J_per_request`,
`E_P_contrast_{lower,upper}_J`, `F_claim_P_armwise_max_J`, `C_P_floor_clearance_J` /
`S_P_floor_shortfall_J`, `B_P_claim_J`. Gate cells (DS-30/31, PG-06/07) carry no
token by design: a fixed two-word outcome from issued `outcome`/`reason_codes` plus
`floor`/interval. Verdict cells render one phrase per outcome, byte-identical across
all six placements.

**(d) Fixture + one test.** Two synthetic `claim_verdicts.v1` contrasts (decode and
`ctr-d117-prefill-p[PREFILL_LENGTH]-qwen3-1p7b-vs-qwen3-8b`,
`collection_prefill_tokens=2048`) plus four floor cells; six cases:
supported, floor-refused, direction-refused, null bound, missing verdict, bad id. Test:
byte-exact outputs for every row including both Refusal strings, STOP_FILL for every
absent/duplicate/inconsistent parent, no surviving `[PENDING]`, `[FILL:*]`, `[VALUE]`.

**(e) Waits.** All numerics; the prefill arm also waits on G2-a for
`[PREFILL_LENGTH]` and the selected `contrast_id`. `bound_id` waits on a registered
sizing-bound definition; if the campaign issues none, DS-29/PG-05 stay STOP_FILL.

## R3 — transfer-result renderer

**(a) Already fixed.** TR-01 (`registry:920`) binds the rendering to *whether the
largest fitted inserted-gap edge residual supported applying the session's
pulse-derived timing bound to inference*, and "no branch selection may remove this
placement". Candidate producer (branch
`feat/2026-09-04-transfer-fiducial-v5`, `d67ee56c`, **UNREVIEWED, not a descendant
of this base**) emits `joulewise.transfer_fiducial_capture.v1`
(`transfer_fiducial.py:1449-1495`): `diagnostic:true`,
`claim_bearing:false`, `b_pulse_s`, `residual_transfer_s`, `excess_s`, `reasons[]`,
`estimator_revision`, `estimator_source_sha256`, and
`verdict ∈ {supported, exceeds_bound, inconclusive}` (`:1441-1447`). Rule and worked
example are pinned: `residual_transfer_s = max(edge_radius_s)`, supported iff
`residual_transfer_s <= b_pulse_s`, `0.022 <= 0.030067931757111657` s
(`transfer-fiducial/worked-example.json`, `check_transfer_fiducial_prose.py:57-80`).

**(b) Minimal schema.** No new fields; read exactly the nine names above.
**Forbidden:** recomputing `residual_transfer_s <= b_pulse_s` (read `verdict`);
putting `residual_median_s_diagnostic_only`/`_p95_` (`:1477-1482`) into prose (they
are diagnostic-only); rendering when `claim_bearing != false` or `diagnostic !=
true`; minting a floor or entering a claim path; suppressing the slot on any branch.

**(c) Token and rule.** One token `TR_01_transfer_result`, one sentence copied
byte-identically to all nine slots. `supported`: "The largest inserted-gap edge
residual was `<residual_transfer_s>` s, within the session's pulse-derived bound of
`<b_pulse_s>` s, so the bound transfers to inference; diagnostic, not a claim." `exceeds_bound` gives both magnitudes plus `excess_s` and denies the bound; `inconclusive` names issued `reasons[]` and asserts
neither.

**(d) Fixture + one test.** The branch's protocol-arithmetic worked example
(non-measurement) plus `exceeds_bound` and `inconclusive` records. Test:
each fixture yields one byte-identical sentence in all nine slots; absent/invalid
identity, unrecognized `verdict`/`reasons`, `claim_bearing=true`, or
`estimator_source_sha256` mismatch stops all nine.

**(e) Waits, and the disposition this seat cannot make.** The value waits on the
post-campaign capture (after final G3). **A magistrate/cold-gate adjudication of the
unreviewed sibling branch must precede any consumer on main**: it also touches
`claims.py`, `floor_extraction.py`, `whole_window.py`, `mint_floor_artifact.py`, so
its blast radius is not confined to the diagnostic. Build the renderer in its own
module against the field names above only.
