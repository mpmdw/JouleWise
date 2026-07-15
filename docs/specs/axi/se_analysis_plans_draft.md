# AXI S-E analysis-plan drafts

Status: **DRAFT — design only; no campaign authority**

Plan state: **PROVISIONAL pending P2-015 Window-A floors**

Owner: AXI-SE / S-E

Claim ceiling: L2 or lower for every plan in this file

This file closes the draft ownership gap for the architectural-axis analysis
plans required by D-070. It is not the frozen analysis registry and does not
authorize a live, hardware, or quiet-Mac run. Window A retains every
quiet-Mac slot. The rows below become executable only after their prerequisites
are satisfied, P2-015 has published the floor/error-budget evidence it actually
measures, each AP's independent pilot has supplied its own estimand-scale
variance/MDE evidence, and the resulting campaign-specific rows and contrast
IDs are frozen and hash-bound under D-053 and D-062.

Normative inputs are `docs/axi-handoff.md` §4 S-E and §6, D-053, D-054,
D-062, D-067, D-070, `docs/contracts/analysis_plans.md`, and the binding
xhigh consult at
`docs/process_traces/2026-07-15-axi-xhigh-consult/response.md` §§4-5.
AP-REASON-VARIANCE also inherits
`docs/specs/rq_energy_variance_design.md`. AP-SPEC completes the statistical
design over the S-A request/burst semantics and denominator front-freeze; it
does not redefine those semantics.

## 0. Provisional marker and shared rules

`PROVISIONAL-UNTIL-P2-015` is a literal floor/error-budget freeze marker.
P2-015 supplies only the backend x metric x window-class evidence it actually
measures: gross-request floors and same-condition single-request variance,
plus a gross-group floor only when that exact group design is an enumerated
P2-015 cell, with its complete error-budget row and window-evidence fields. It
does not measure a B>1 slope, a spec pair, a quant/quality joint gate, a
reasoning-tail component, a dense/MoE interaction, or a 2M dense/MoE pair.
Every AP-specific effect-size and confirmatory-n cell therefore carries the
stronger literal marker `PROVISIONAL-UNTIL-P2-015-AND-<PILOT-ID>`. It freezes
only after both P2-015 and that AP's named pilot below. A pilot is analyzed
before and separately from confirmatory data, is permanently labeled
pilot-not-confirmatory, and can never be pooled into the confirmatory result.
The replacement must be prospective, appear in the frozen registry before the
affected campaign, and be covered by the registry hash.

The following structural choices are already fixed and are not provisional
numbers: static batching only; the batch grid `B in {1,2,4,8,16}`; gross
energy as the headline basis; request-scoped evidence; separate external-draft
and native-MTP families; an L2 maximum; and no L3 route except the existing
Q4/AP-1 holdout machinery, which none of these drafts invokes.

Every plan inherits these rules:

1. Only strict-valid bundles enter claim-bearing analysis. Exclusions and
   quality-flag waivers are enumerated before unblinding; technically invalid
   runs may be replaced under a frozen replacement rule, but capacity,
   divergence, and unsupported outcomes are data, not invalid runs.
2. Gross energy inside the named boundary is primary. Idle-subtracted request
   energy may appear only as a clearly labeled within-device secondary view;
   it cannot rank devices or configurations. Phase energy is gross-only.
3. D-053's three-way disposition applies per contrast: a below-floor effect is
   `not resolvable`; a floor-clearing but non-directional interval is
   `unresolved`; equivalence wording requires its own predeclared equivalence
   gate. Failure to reject a difference is not equivalence.
4. Confirmatory `n` is frozen from the applicable independent AP pilot using a
   conservative upper variance bound and the predeclared effect/equivalence
   target. P2-015 request variance may be a plausibility cross-check only.
   Any outcome-dependent top-up permanently demotes the affected contrast to
   exploratory; the original fixed-`n` result is still reported. No pilot or
   grown estimate is pooled as retaining nominal confirmatory coverage.
5. Each frozen registry enumerates every `contrast_id`, role, model/cell set,
   estimator, family, adjustment rule, and exact multiplicity denominator.
   Unlisted contrasts are exploratory.
6. Runtime-observed committed-output counts and stop reasons are required for
   token-normalized companions. Configured token counts are QA evidence only.
   Request or group gross energy remains at least as salient as every ratio.
7. A fixture, mock, desk artifact, or runtime-support spike carries no live
   energy claim. Missing floors, missing observability, and unsupported
   runtime behavior yield structured outcomes rather than inferred zeros.
8. A scalar floor is necessary but insufficient. Every claim consumes the
   complete D-054 error-budget row for its backend x metric x window class,
   requires every contributing `window_evidence_precheck` to be eligible, and
   propagates `energy_variance_terms_j2` separately from deterministic
   `energy_bound_terms_j`. Applicable UNKNOWN terms retain their recorded
   consequence: if an UNKNOWN caps the claim below L2 or cadence, anchor,
   interpolation/aliasing, drift, or clock evidence makes the window
   ineligible, the L2 contrast is refused or `not resolvable` even when its
   scalar floor clears. Strict validation never substitutes for this gate.

### Shared estimand-scale floor transport

Let `mu` be the vector of gross-energy cell means entering an estimand
`theta=g(mu)`. An accepted same-design calibration supplies a covariance or
false-effect matrix `Sigma_F` in `J^2` on exactly that aggregate/window design,
plus deterministic bound vector `d` in J. With
`a = gradient(g)` evaluated at the prospectively frozen reference, transport
is

`F_theta = sqrt(a^T Sigma_F a)` and
`D_theta = sum_i(abs(a_i) * d_i)`.

The claim-facing null bound is `G_theta=F_theta+D_theta` on theta's units.
This additive union/triangle bound is conservative when stochastic and
deterministic errors align; taking their maximum is forbidden. For a linear
contrast `theta=c^T mu`, `a=c`. For a ratio `E/T`,
`a=(1/T,-E/T^2)` and the joint numerator/denominator covariance is required;
when T is exact and common, this reduces to `F_E/T`. A diagonal
`Sigma_F=diag(F_i^2)` is allowed only when the calibration proves the cell
errors independent; an unmeasured correlation is not zero.

Transport MUST refuse when metric/window semantics, aggregation weights,
duration range, cadence, drift regime, B, model/runtime state, or correlation
structure falls outside the calibration support, or when a nonlinear
denominator/variance gradient lacks calibrated inputs. Refusal requires a
dedicated same-design alias/calibration cell before claim-bearing execution.
There is no fallback transport that always accepts.

### Independent pilot registry

These sizes are pilot evidence budgets, not confirmatory n and not campaign
authority:

| Pilot ID | Fixed pilot-only design | What it freezes |
|---|---|---|
| `PILOT-BATCH-V1` | Three complete 16-request all-B blocks: 31 native group executions per block, 93 total. | Block covariance and within-B-cell pure-error variance for affine, lack-of-fit, breakpoint, normalized-energy, and latency estimands. |
| `PILOT-SPEC-DRAFT-V1` | Four paired blocks, each with eight frozen requests in both off and one exact external-draft arm: 64 bundles. | External-draft paired energy, denominator, identity/divergence, and latency variance. |
| `PILOT-SPEC-MTP-V1` | Four paired blocks, each with eight frozen requests in both off and one exact native-MTP arm: 64 bundles. | Native-MTP paired energy, denominator, identity/divergence, and latency variance. |
| `PILOT-QUANT-V1` | Four complete blocks over the 32-item `c5-1.12-quant-energy-v1` subset at exactly `L` S-D-frozen ladder levels, where `L in {2,3}`: `128L` bundles, hence 256 or 384 as frozen before the pilot. | Energy, denominator, power, duration, throughput, and influence precision; the separate S-D 256-item quality screen does not use these bundles. |
| `PILOT-REASON-REPLAY-V1` | Six distinct-seed natural source generations plus three forced-ID replays of each resulting frozen token sequence: 24 bundles. | Replay within-sequence variance, corrected across-sequence replay variance, component floors, and path/replay-count precision; source natural energy is descriptive only. |
| `PILOT-MOEBATCH-V1` | Three complete paired-model superblocks: 31 groups per model per superblock, 186 group executions. | Dense/MoE slope/DID, normalized-energy, routing-if-visible, and latency covariance. |
| `PILOT-MOE2M-V1` | Three paired dense/MoE pilot blocks per already-frozen target/profile cell: six bundles per cell. | Rider pair/profile, normalized-energy, power, duration, and latency covariance. |

Each pilot requires a separately authorized future campaign and is excluded
from every confirmatory contrast. If the exact `PILOT-MOE2M-V1` cells are not
already part of the source 2M plan, the rider's zero-extra-cost condition
fails rather than silently adding them.

## 1. AP-BATCH-DRAFT — static-batch affine stress test

### D-053 registry row

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | `AP-BATCH-DRAFT` / Mac leg of C5-2.2; a static-batch stress test of Q4's fixed-plus-marginal thesis. |
| `family_id` | `FAM-AXI-BATCH-MODEL-SELECTION` is one seven-hypothesis family: one affine slope, three fixed lack-of-fit departures, and three frozen breakpoint hinges. `FAM-AXI-BATCH-NORMALIZED` owns B-versus-B1 gross J/request and J/committed-token contrasts. `FAM-AXI-BATCH-LATENCY` owns eight separate two-sided difference hypotheses: TTFT-p95 and end-to-end-p95 at each of B=2,4,8,16 versus B=1. |
| `claim_role` | Affine slope and lack-of-fit: primary inside the one model-selection family. Frozen-candidate breakpoint: gate-kept secondary inside that same family and multiplicity budget. Normalized energy and latency: secondary. Memory-fit disposition: structured descriptive outcome. |
| `selection_scope` | One named target, telemetry boundary, backend/runtime version, model artifact and quantization, static native-batch path, workload shape, fixed output policy, and exactly 16 distinct equal-shape requests. Every block contains the fixed `B in {1,2,4,8,16}` grid through the 31-group construction below. No continuous batching, arrival trace, or scheduler search is in scope. |
| `multiplicity_rule` | One Holm denominator of exactly seven covers the complete `FAM-AXI-BATCH-MODEL-SELECTION`: one affine-slope hypothesis; the three lack-of-fit contrasts `d_1,d_2,d_3`; and one continuous-hinge coefficient for each frozen knot `K_BATCH={2,4,8}`. The single selection rule is: select `affine adequate` only when every simultaneous adjusted lack-of-fit interval lies inside its floor-clearing equivalence band; if any adjusted, floor-clearing `d_j` instead establishes lack of fit, open the three hinge candidates without resetting alpha and select one only when its hinge survives the same seven-hypothesis Holm denominator, it has the uniquely lowest leave-one-block-out RMSE, and its RMSE gap clears the pilot-frozen comparison bound; otherwise report `shape unresolved`/`breakpoint unresolved`. Any other knot is exploratory. Normalized contrasts have their own complete Holm denominator. The latency family has exactly eight two-sided difference hypotheses and one Holm denominator of eight. |
| Metric + exact window class | Primary: `gross_energy_j` for each unioned static batch-group request window and its block/B aggregate. Secondary: block/B gross J/request, ratio-of-totals gross J/committed token, type-7 p95 TTFT, and type-7 p95 end-to-end latency. Gross phase-window energy is a descriptive L1 audit unless a later registry enumerates a phase family. TTFT and end-to-end are separate endpoints. No overlapping group energy is divided among requests. |
| Unit of analysis + dependence structure | A native group is the captured energy unit; the complete 16-request block is the inferential unit. For each B, `16/B` groups partition the roster, so requests/groups inside a block are clustered inputs, not replicates. Confirmatory uncertainty is across complete blocks. |
| Estimand / estimator / formula | In block k and B, `Ebar_kB=(B/16)*sum_g(E_kBg)`, the equal-group mean over `16/B` groups. Fit `Ebar_kB = alpha_affine + block_effect + B*beta_batch + error`. `alpha_affine` is an estimated B=0 affine intercept, not measured idle or uniquely identified residency/runtime cost. For cell means ordered B=(1,2,4,8,16), freeze the pure-curvature basis `c_1=(-2,3,-1,0,0)`, `c_2=(0,-2,3,-1,0)`, and `c_3=(0,0,-2,3,-1)`, with `d_j=c_j^T mu`; each annihilates an affine E(B). Estimate pure error only from the replicated within-B cells after block adjustment: the residual SSE of the saturated block-plus-categorical-B model, with `4(K-1)` degrees of freedom for K complete blocks. Affine residuals never estimate pure error. Breakpoint candidate k uses the continuous hinge `h_k(B)=(B-k)_+`. Block/B J/request is `sum_g(E_kBg)/16`; J/committed token is `sum_g(E_kBg)/sum_g(T_kBg)` and is null when the token total is zero. Latency cells are type-7 p95 over the 16 request values; each hypothesis is a two-sided B-versus-B1 difference. |
| Effect-size target | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-BATCH-V1:** freeze minimum relevant `beta_batch`, the three `delta_LOF,j`, normalized-energy effects, breakpoint-selection RMSE gap, and separate TTFT/end-to-end minimum relevant differences from the pilot covariance and named workload policy. No target is selected from confirmatory AP-BATCH outcomes. |
| Inclusion/exclusion + quality-flag waiver rules | Include strict-valid native static batches whose configured and realized B agree, every admitted request has request-indexed terminal/output evidence, and the fixed output policy and realized shape pass. No Python loop over singleton calls qualifies. A waiver must be named in the frozen registry and cannot waive output identity, request lifecycle, group-window integrity, or floor evidence. |
| Order/blocking/covariates | Roster IDs are `r_0...r_15`. In block k, cyclically permute them as `pi_k(i)=r_((i+k) mod 16)`; at B, partition `pi_k` into consecutive disjoint chunks of size B. Thus each request appears exactly once at every B in every block: 16, 8, 4, 2, and 1 groups at B=1,2,4,8,16, respectively; 31 groups and 80 request placements per block. Rotate the five B-level order by `k mod 5` and rotate group order by `k mod (16/B)` (zero when one group) to form the Latin-square-style schedule. Draft confirmatory design is five such blocks (`n_blocks=5`, **PROVISIONAL-UNTIL-P2-015-AND-PILOT-BATCH-V1**): 155 groups and 400 placements. Session, manifest position, drift sentinel, cooldown-cap status, and realized B are recorded; no outcome-selected covariate is allowed. |
| Floor gate | **PROVISIONAL-UNTIL-P2-015:** accept a group calibration only if it covers every B's unioned window semantics, duration/cadence/drift range and supplies the joint `Sigma_F`; a scalar single-request floor alone refuses. With affine design contrast `c_beta`, use `F_beta=sqrt(c_beta^T Sigma_F c_beta)`, `D_beta=sum(abs(c_beta_i)*d_i)`, and the additive guard `G_beta=F_beta+D_beta`. Each lack-of-fit or breakpoint contrast `c_h` uses analogous `G_h=F_h+D_h`. J/request uses the linear `1/16` total-energy weights; J/token uses the shared ratio gradient and joint energy/token covariance. If any required covariance, bound, B, or nonlinear denominator support is absent, a dedicated 31-group same-design alias calibration is mandatory; otherwise this AP does not execute. |
| Error-budget + window-evidence claim gate | Every group window and reported phase window must pass its metric-specific `window_evidence_precheck`. Consume the complete D-054 row, including cadence, timestamp anchor, interpolation/aliasing, sensor/backend, and applicable drift/clock terms. Propagate stochastic and deterministic terms through the same `c_beta`, `c_h`, normalized, or phase contrast. Any applicable UNKNOWN that caps below L2 or any ineligible window refuses that claim even when `G_theta` clears. |
| MDE/n sizing + predeclared top-up rule | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-BATCH-V1:** the D-062 draft remains `n_blocks=5`, but final confirmatory blocks freeze only from the three complete nonconfirmatory pilot blocks using a conservative upper covariance bound for every family. Pilot blocks are excluded. If five is retained despite inadequate MDE, report `not resolvable`/L1. Technically invalid blocks alone may be replaced under the frozen rule. |
| Denominator provenance requirement | Group gross energy comes from the unioned native-group window. Block/B J/request divides the sum across the complete 16-request partition by exactly 16; it is unavailable for an incomplete partition. J/token is the ratio of total group gross joules to total runtime-observed committed tokens across that partition, null at zero tokens. Config counts, event counts, and a mean of group/request ratios are forbidden substitutes. |
| Holdout cells (L3 only) | Not applicable. This plan has no L3 route and no extrapolation beyond the frozen B grid. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 for one named stack, model, roster policy, and static-admission policy. Forbidden upgrades: no continuous-batching, request-coalescing, scheduler-optimum, offered-load, or general serving-efficiency claim; no architecture-wide scaling law; no interpretation of the affine intercept as measured idle or uniquely identified residency cost. |
| Disqualifiers + not-resolvable conditions | Missing batch support/observability, realized-B mismatch, looped singleton dispatch, incomplete request evidence, untransportable floor, unresolved latency difference, below-floor coefficient/deviation, or unresolved lack of fit causes the named downgrade. A structured B=16 memory failure prevents the frozen all-B primary fit; it is never silently dropped. |
| Linked manifests/bundle hashes | Pending. The frozen roster/order manifest, analysis-registry hash, calibration artifact/hash, runtime/model hashes, and strict-valid bundle hashes are required before a claim is drafted. |

### Frozen contrast rows

| Draft `contrast_id` | Role | Contrast and disposition |
|---|---|---|
| `BATCH-MODEL-AFFINE-SLOPE` | Primary/model-selection family | Estimate `beta_batch` from every block/B aggregate; report its one-family adjusted interval, pilot MDE, `G_beta`, and J/request added to the group. |
| `BATCH-MODEL-LOF-<j=1,2,3>` | Primary/model-selection family | The three exact `c_j` curvature contrasts above, each standardized only by saturated block-plus-categorical-B pure error. Any adjusted interval excluding zero and clearing `G_dj` declares lack of fit. Affirmative adequacy requires every simultaneous interval inside `+/-delta_LOF,j`, with `delta_LOF,j>G_dj`; otherwise adequacy is `not resolvable`/`unresolved`. |
| `BATCH-MODEL-BREAK-<k=2,4,8>` | Gate-kept secondary/same family | Exactly three continuous-hinge candidates, evaluated only after established lack of fit and charged within the exact seven-hypothesis Holm denominator. Apply the unique leave-one-block-out RMSE rule above; no unique floor-clearing winner means `breakpoint unresolved`. |
| `BATCH-JREQ-B<value>-VS-B1` | Secondary/normalized family | Difference in block total gross energy/16 between B and B=1 for each enumerated B. |
| `BATCH-JTOKEN-B<value>-VS-B1` | Secondary/normalized family | Difference between block ratio-of-totals gross J/committed token at B and B=1; zero-token cells are null and abort the contrast. |
| `BATCH-TTFT-P95-B<value>-VS-B1` | Secondary/latency family | Pre-registered two-sided difference test for type-7 p95 TTFT across the 16 requests, each B in {2,4,8,16} versus B=1. |
| `BATCH-E2E-P95-B<value>-VS-B1` | Secondary/latency family | Separate pre-registered two-sided difference test for type-7 p95 end-to-end latency, each B in {2,4,8,16} versus B=1. |
| `BATCH-MEMORY-B16` | Structured outcome | First failure records `observed_memory_failure` and triggers the reset protocol below. Record `memory_not_fit` only after the one permitted clean-state confirmation fails with the same memory-allocation reason while the B=1 health control succeeds. Otherwise record `capacity_unresolved`, `runtime_unsupported`, or `instrumentation_unobservable`. |

### Predeclared sensitivities

- Report categorical B-cell means and adjusted affine residuals without
  changing the primary affine specification.
- Run leave-one-block-out influence analysis because the draft block count is
  small. A randomization-respecting permutation check is allowed only if the
  final design has enough exchangeable blocks under D-053; it is omitted, not
  improvised, otherwise.
- Repeat the affine estimate with the predeclared drift/session covariate set
  and without it. A sign or claim-disposition change is reported.
- If B=16 has a structured capacity failure, a B<=8 fit may be shown only as a
  labeled descriptive sensitivity. It cannot inherit the all-B primary role
  or make the original plan appear successful.

### Abort and downgrade rules

Abort claim-bearing execution before measurement if the S-B Mac verdict is
not `supported`, request-scoped evidence is unavailable, or the floor route is
unfrozen. On the first B=16 memory failure: persist it and stop the model
process. Apply the pilot-frozen reset manifest: terminate every model/runtime
worker, reinitialize the runtime/device, clear only the named allocator/KV
cache state, complete the frozen cooldown, verify that no worker survives and
no new swap is present, and require available memory to return within the
pilot-frozen tolerance of the pre-block baseline. Then require a successful
B=1 health control before permitting exactly one B=16 confirmation attempt.
Any failed reset criterion prohibits the retry. The confirmation is
classification evidence, not a replacement or top-up. If reset/health fails,
the second attempt succeeds, or the failure reason differs, record
`capacity_unresolved`/`observed_memory_failure`, never `memory_not_fit`.
Retain lower-B evidence as descriptive and require a new prospective
restricted-range AP. Never choose a breakpoint after effects.

## 2. AP-SPEC-DRAFT — speculative decode / MTP completion

### D-053 registry row

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | `AP-SPEC-DRAFT` / C5-2.5 plus C-023-OUTPUT-IDENTITY. This completes statistical design over the S-A denominator, counter, request-output, and identity-report front-freeze. |
| `family_id` | External-draft families are `FAM-AXI-SPEC-DRAFT-ENERGY`, `FAM-AXI-SPEC-DRAFT-LATENCY`, and `FAM-AXI-SPEC-DRAFT-DIAGNOSTIC`; native-MTP uses the separate parallel `FAM-AXI-SPEC-MTP-*` IDs. A prospectively activated quality-matched route uses separate `FAM-AXI-SPEC-DRAFT-QUALITY` or `FAM-AXI-SPEC-MTP-QUALITY`. No family pools draft and MTP. |
| `claim_role` | Paired gross request energy: primary within each mode. Gross J/committed token and separate TTFT/end-to-end endpoints: secondary. Accepted-draft accounting: enabled-arm mechanism diagnostic only. |
| `selection_scope` | One frozen target model/artifact, tokenizer, runtime/backend/version, quantization, prompt/workload roster, target decoding policy, requested output policy, and either one exact external draft identity or one exact native-MTP/head configuration. Each enabled arm is paired with a speculation-off control that differs only in frozen speculation fields. |
| `multiplicity_rule` | Holm within each exact mode-specific family over its complete enumerated contrast set. Energy, latency, diagnostics, and optional quality have explicit denominators and never borrow alpha from one another; draft and MTP remain separate. Any cross-mode or pooled speculation effect is exploratory unless a later AP freezes it. |
| Metric + exact window class | Primary: paired `gross_energy_j` on gross request windows. Secondary: block ratio-of-totals gross J/runtime-observed committed token, type-7 p95 TTFT, and type-7 p95 end-to-end latency. Diagnostics: proposal/accepted totals, ratio-of-totals acceptance rate, and enabled-arm gross J/accepted token. Accepted-token ratios are undefined off and never serve as on/off efficiency denominators. |
| Unit of analysis + dependence structure | Exact on/off request pairs are nested in a counterbalanced complete roster block; the block is the inference unit. Requests receive equal weight within block. Decode emissions, tokens, and accepted tokens are denominator/mechanism evidence, not replicates. |
| Estimand / estimator / formula | For R frozen requests in block k, `DeltaE_k=(1/R)*sum_i(E_on,ki-E_off,ki)`. For arm a, `JT_ka=sum_i(E_a,ki)/sum_i(T_a,ki)`; the secondary contrast is `JT_k,on-JT_k,off`. TTFT and end-to-end cells are separate type-7 p95 values across R requests and contrast on minus off. Enabled-arm `acceptance=sum_i(A_i)/sum_i(P_i)` is null if total P is zero; `Jaccepted=sum_i(E_on,i)/sum_i(A_i)` is null if total A is zero. Block means/paired intervals are computed across blocks, never by pooling requests as independent. |
| Effect-size / equivalence targets | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-SPEC-DRAFT-V1** for external draft and **PROVISIONAL-UNTIL-P2-015-AND-PILOT-SPEC-MTP-V1** for native MTP: freeze separate gross-energy, J/committed-token, TTFT, and end-to-end effects. Any quality-equivalence margin is scientifically frozen before its pilot and is not selected from energy outcomes. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid S-A-version bundles only; proposal/acceptance rollups, request lifecycle, committed token IDs/hashes, stop reason, target identity, and output-identity report must agree. Pair states are `exact_token_match`, `text_match_token_divergent`, `output_divergent`, or `unassessable`. Only `exact_token_match` enters the clean matched-decoded-work primary. Other states remain in the disposition table and cannot be silently excluded to improve an effect. |
| Order/blocking/covariates | Counterbalanced paired on/off order within prompt/block; target/draft or MTP identity, session, manifest position, drift sentinel, and output-policy fields recorded. The frozen covariate set is limited to prespecified block/session drift terms. External draft and native MTP blocks are separate. |
| Floor gate | **PROVISIONAL-UNTIL-P2-015:** for paired energy `c=(1,-1)` on on/off cell means, use `F_DeltaE=sqrt(c^T Sigma_F c)`, the matching `D_DeltaE`, and additive `G_DeltaE=F_DeltaE+D_DeltaE`; `floor_cmp_j` is usable only when its calibration matches this pairing/state. For each arm's J/T ratio use gradient `(1/T,-E/T^2)` and the joint energy/token covariance, then sum its transported stochastic and deterministic guards across the arm difference. Exact common T reduces to the paired additive energy guard divided by T. If denominator covariance, state matching, or output-policy support is absent, refuse the ratio claim or run a dedicated paired calibration. Latency precision comes from the mode-specific pilot and timer evidence, not an energy floor. |
| Error-budget + window-evidence claim gate | Every on/off request window must have eligible `window_evidence_precheck.gross_request`; every reported phase uses its own eligible precheck. Consume all D-054 stochastic variance and deterministic bound terms through the paired/ratio gradients. Applicable UNKNOWN cadence, anchor, interpolation/aliasing, sensor, drift, or clock terms retain their claim cap; a cap below L2 or an ineligible window refuses that contrast independently of output identity. |
| MDE/n sizing + predeclared top-up rule | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-SPEC-DRAFT-V1** for external draft and **PROVISIONAL-UNTIL-P2-015-AND-PILOT-SPEC-MTP-V1** for native MTP: each freezes from its own conservative upper paired covariance. Pilot blocks are excluded. No bank `n>=5` wording fixes n. Technically invalid pairs may be replaced; divergence is an estimand/gate outcome. |
| Denominator provenance requirement | Committed tokens are summed from request-indexed observed outputs per arm/block. J/committed token is a block ratio of totals and null at zero total. Accepted and proposed totals use the S-A counters: acceptance is `sum(A)/sum(P)`, null at zero P; J/accepted is `sum(E_on)/sum(A)`, null at zero A and undefined off. Config caps and means of request/step ratios are forbidden. |
| Holdout cells (L3 only) | Not applicable. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 within the named stack and exact draft or MTP identity. Forbidden upgrades: no speculative-decoding efficiency claim without the output-equivalence/divergence report and accepted-token accounting; no pooling of native MTP with external draft-model results; no general runtime, model-family, or architecture claim. |
| Disqualifiers + not-resolvable conditions | Missing counters, unverified identity, unassessable output, absent/mismatched floor, below-floor paired effect, unresolved interval, zero accepted tokens for the diagnostic, or output divergence triggers the named disposition. Runtime generation without claim instrumentation is L0 support only. |
| Linked manifests/bundle hashes | Pending: S-A semantic/manifest version, frozen family/contrast registry, pairing manifest, floor artifact, target/draft/MTP hashes, output-identity reports, and bundle hashes. |

### Frozen contrast rows

| Draft `contrast_id` | Family | Role and gate |
|---|---|---|
| `SPEC-DRAFT-GROSS-REQUEST` | `FAM-AXI-SPEC-DRAFT-ENERGY` | Primary on-minus-off gross request energy; exact-token-match gate required. |
| `SPEC-DRAFT-GROSS-PER-COMMITTED` | `FAM-AXI-SPEC-DRAFT-ENERGY` | Secondary on-minus-off block ratio-of-totals gross J/committed token. |
| `SPEC-DRAFT-TTFT-P95` | `FAM-AXI-SPEC-DRAFT-LATENCY` | Secondary paired on-minus-off type-7 p95 TTFT. |
| `SPEC-DRAFT-E2E-P95` | `FAM-AXI-SPEC-DRAFT-LATENCY` | Secondary paired on-minus-off type-7 p95 end-to-end latency. |
| `SPEC-DRAFT-ACCEPTANCE-DIAG` | `FAM-AXI-SPEC-DRAFT-DIAGNOSTIC` | Enabled-arm ratio-of-totals acceptance and J/accepted with exact zero rules; no off accepted-token contrast. |
| `SPEC-MTP-GROSS-REQUEST` | `FAM-AXI-SPEC-MTP-ENERGY` | Primary on-minus-off gross request energy; exact-token-match gate required. |
| `SPEC-MTP-GROSS-PER-COMMITTED` | `FAM-AXI-SPEC-MTP-ENERGY` | Secondary on-minus-off block ratio-of-totals gross J/committed token. |
| `SPEC-MTP-TTFT-P95` | `FAM-AXI-SPEC-MTP-LATENCY` | Secondary paired on-minus-off type-7 p95 TTFT. |
| `SPEC-MTP-E2E-P95` | `FAM-AXI-SPEC-MTP-LATENCY` | Secondary paired on-minus-off type-7 p95 end-to-end latency. |
| `SPEC-MTP-ACCEPTANCE-DIAG` | `FAM-AXI-SPEC-MTP-DIAGNOSTIC` | Enabled-arm ratio-of-totals acceptance and J/accepted with exact zero rules; no off accepted-token contrast. |
| `SPEC-DRAFT-QUALITY-MATCHED` | `FAM-AXI-SPEC-DRAFT-QUALITY` | Optional adjusted paired quality interval wholly inside frozen `+/-Delta_Q`; wording is quality-matched, never exact-work matched. |
| `SPEC-MTP-QUALITY-MATCHED` | `FAM-AXI-SPEC-MTP-QUALITY` | Separate optional native-MTP quality-equivalence route under the same rule. |

### Predeclared sensitivities

- Report an all-attempted-pairs descriptive table by all four identity states;
  do not use post-hoc exact-match filtering without showing divergence rates.
- Run leave-one-block-out influence analysis and the prespecified with/without
  drift-term model. Use a within-block randomization check only when the final
  exchangeable-block count meets D-053.
- Report request energy against acceptance rate and proposal count as
  mechanism diagnostics without converting association to causation.
- Report committed-token ratio results with and without pairs whose stop
  reasons differ, while preserving the primary identity disposition.

### Abort and downgrade rules

Do not create a claim-bearing bundle until the S-A front-freeze and generic
registry/manifest version exist. If a runtime generates text but cannot expose
proposal/acceptance or request-output identity, record
`unsupported_for_joulewise(claim_observability)` and stop at L0. If exact
identity fails, the clean primary is unavailable; a prospectively frozen
quality-matched route may proceed with distinct wording, otherwise report the
divergence and energy observations at L1.

## 3. AP-QUANT-DRAFT — quantization ladder with quality equivalence

### D-053 registry row

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | `AP-QUANT-DRAFT` / C5-1.12 plus C-023-QUALITY-EQUIV-QUANT. |
| `family_id` | `FAM-AXI-QUANT-ENERGY`, `FAM-AXI-QUANT-QUALITY-EQUIV`, `FAM-AXI-QUANT-DECOMPOSITION` (power, duration, and throughput), `FAM-AXI-QUANT-NORMALIZED` (J/committed token), and descriptive `FAM-AXI-QUANT-DIAGNOSTIC` (output/stop divergence). |
| `claim_role` | Gross decode-energy contrasts: primary conditional on the separate S-D quality gate. Mean power, duration, throughput, and J/committed-token contrasts: secondary. Exact output/stop divergence: descriptive required diagnostic. |
| `selection_scope` | The S-D preferred `BF16/Q8_G64/Q4_G64` ladder or its prospectively frozen `BF16/Q4_G64` capability fallback (**PROVISIONAL-UNTIL-S-D-SCORECARD**) for the one scorecard model family, tokenizer, MLX runtime/recipe, target/boundary, `axi-sd-greedy-eos128-v1` output policy, 32-item energy subset, and 256-item quality screen. Artifact revisions, levels, hashes, and fallback status freeze before outputs or energy. Cross-stack and cross-boundary comparisons are outside this Mac-leg plan. |
| `multiplicity_rule` | The energy family contains exactly each frozen lower-precision level versus BF16: `m=2` for the three-level ladder or `m=1` for the pre-freeze fallback, with the S-D-frozen Bonferroni threshold `0.05/m`, no alpha recycling, and no outcome-selected level. The quality family uses the separate S-D 256-item gate and its frozen Bonferroni/bootstrap rule. Holm applies separately to the complete secondary decomposition and normalized families. The diagnostic family reports every frozen ladder state without directional inference. Unlisted all-pairs comparisons are exploratory. |
| Metric + exact window class | Primary: gross decode energy for the named request/decode window and boundary. Secondary: elapsed decode duration, mean gross decode power, committed-token throughput over decode duration, and gross decode J/runtime-observed committed output token. The frozen quality screen and exact output/stop divergence are reported beside energy. Other gross phase energy is descriptive only when resolvable and remains gross-only. |
| Unit of analysis + dependence structure | The 32 deterministic energy-subset items are paired across every quant level inside a complete block; block is the energy inference unit and items are nested inputs, not replicates. Energy items have equal fixed weight `w_i=1/32`. Quality equivalence is a separate once-per-level 256-item stratified S-D screen; it is neither pooled with nor re-estimated from energy blocks. |
| Estimand / estimator / formula | `E_kq=(1/32)*sum_i(E_kiq)` and `DeltaE_q=mean_k(E_kq-E_kref)`. Define aggregate decode duration `D_kq=(1/32)*sum_i(D_kiq)` and aggregate mean power `P_kq=E_kq/D_kq`, null at zero duration, so `E_kq=P_kq*D_kq`. Report the exact symmetric identity `Delta_E_power=(P_q-P_ref)*(D_q+D_ref)/2`, `Delta_E_time=(D_q-D_ref)*(P_q+P_ref)/2`, and `Delta_E_total=Delta_E_power+Delta_E_time`; it is descriptive, not causal. Block J/token is `sum_i(E_kiq)/sum_i(TOK_kiq)`, null at zero tokens. Throughput is `sum_i(TOK_kiq)/sum_i(D_kiq)`, null at zero duration; neither is a mean of item ratios. Quality passes only under the exact S-D gate: its Bonferroni/bootstrap overall lower bound exceeds `-0.02` and every stratum gap is at least `-0.05`. |
| Effect-size / equivalence targets | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-QUANT-V1 (plus S-D scorecard):** S-D freezes the quality margins, metric, scorer, 256-item population, stratification, missing-as-zero rule, and ladder before the pilot; the pilot freezes energy, power, duration, throughput, and normalized-effect MDEs from the 32-item energy subset. Nothing is selected from confirmatory energy outcomes. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid energy bundles with exact S-D artifact and 32-item manifest hashes, same tokenizer/runtime recipe/output policy, runtime-observed token/stop evidence, and a completed S-D quality disposition for every level. Exact output divergence on the 32-item subset is always reported. No waiver may excuse artifact/scorer drift, change the missing-as-zero quality rule, or drop an item/level after freeze. |
| Order/blocking/covariates | Counterbalance quant order within item/block; record session, manifest position, drift sentinel, cache/process state, realized tokens, and stop reason. The primary model uses the paired block design; only prespecified drift terms may be added. |
| Floor gate | **PROVISIONAL-UNTIL-P2-015:** for each q-minus-reference decode-energy contrast use its paired design vector `c_q`: `F_q=sqrt(c_q^T Sigma_F c_q)`, transported `D_q`, and additive `G_q=F_q+D_q`. J/token and throughput use their separate ratio gradients and sum the transported stochastic/deterministic guards from the joint numerator/denominator design at both q levels. Power/duration have their own pilot/timer/sensor precision gates and cannot inherit a joule floor. If quant state changes duration/cadence beyond calibration support, or denominator covariance is absent, transport refuses and a dedicated 32-item matched-quant calibration cell is required. |
| Error-budget + window-evidence claim gate | Every one of the 32 item/decode windows entering a block must pass its exact metric/window `window_evidence_precheck`; other phase companions require their own eligible windows. Consume the complete D-054 error budget and propagate stochastic/deterministic terms with `1/32` weights and the contrast/ratio gradients. Any applicable UNKNOWN that caps below L2, or any cadence/anchor/interpolation/drift/clock failure, refuses the affected contrast even if the S-D quality gate and scalar energy floor pass. |
| MDE/n sizing + predeclared top-up rule | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-QUANT-V1:** freeze confirmatory complete-block count from the four-block pilot's conservative 32-item energy/decomposition/throughput/denominator covariance. All pilot bundles are excluded. The 256-item quality gate is pre-frozen and completed separately; it is not a pilot-derived margin. If quality fails or energy is imprecise at frozen n, report the trade-off without efficiency wording. |
| Denominator provenance requirement | Gross decode energy is the equal-weight sum/mean over the complete frozen 32-item subset. J/token is block total gross decode J divided by block total runtime-observed committed tokens, null at zero; throughput reverses the observed-token/decode-duration totals and is null at zero duration. Means of item ratios and config counts are forbidden. Quality uses all 256 frozen screen items, four strata, and missing/invalid-as-zero exactly as S-D specifies; it cannot be replaced by the 32 energy items or successful-item filtering. |
| Holdout cells (L3 only) | Not applicable. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 for the named model family, ladder, stack, workload, and boundary. Forbidden upgrades (verbatim registry constraints): `no quantization efficiency claim without AP-level equivalence rule`; `no quantization efficiency claim without output divergence reporting`. Also no cross-stack, cross-boundary, or model-family-wide quant winner. |
| Disqualifiers + not-resolvable conditions | Quality-equivalence failure or imprecision, scorer/artifact drift, output-policy mismatch, floor-missing/below-floor energy, unbalanced pairing, or structured memory/runtime failure blocks efficiency wording. Energy savings with quality loss are a trade-off result, not efficiency. |
| Linked manifests/bundle hashes | Pending: S-D ladder/scorecard hashes, scorer and item manifest, frozen contrast registry, floor artifact, order manifest, and strict-valid bundle hashes. |

### Frozen contrast rows

| Draft `contrast_id` | Family / role | Contrast and gate |
|---|---|---|
| `QUANT-<q>-VS-REF-GROSS` | `FAM-AXI-QUANT-ENERGY` / primary | Paired equal-weight gross decode-energy contrast on the 32-item subset; claim-bearing only when the separate quality gate passes and divergence is reported. |
| `QUANT-<q>-VS-REF-QUALITY` | `FAM-AXI-QUANT-QUALITY-EQUIV` / primary gate | Separate 256-item S-D Bonferroni/bootstrap gate: overall lower bound `>-0.02` and every stratum gap `>=-0.05`; non-rejection is insufficient. |
| `QUANT-<q>-VS-REF-POWER` | `FAM-AXI-QUANT-DECOMPOSITION` / secondary | Paired aggregate mean decode-power contrast, reported with duration. |
| `QUANT-<q>-VS-REF-DURATION` | `FAM-AXI-QUANT-DECOMPOSITION` / secondary | Paired fixed-weight request-duration contrast, reported with power. |
| `QUANT-<q>-VS-REF-THROUGHPUT` | `FAM-AXI-QUANT-DECOMPOSITION` / secondary | Difference in block ratio-of-totals committed tokens/decode duration, with zero-duration rule. |
| `QUANT-<q>-VS-REF-PER-COMMITTED` | `FAM-AXI-QUANT-NORMALIZED` / secondary | Difference in block ratio-of-totals gross J/committed token, with zero rule above. |
| `QUANT-<q>-VS-REF-OUTPUT-DIVERGENCE` | `FAM-AXI-QUANT-DIAGNOSTIC` / descriptive | Complete exact-token/text/stop/quality divergence counts; no favorable-stratum directional inference. |

### Predeclared sensitivities

- Repeat the paired energy model with and without the frozen drift terms and
  perform leave-one-block/item-group-out influence analysis.
- Report exact-token-match and token-divergent energy-subset strata
  descriptively; the separate 256-item quality gate, not the more favorable
  energy stratum, controls efficiency wording.
- Reproduce the frozen S-D quality screen only as a code/hash audit; do not
  introduce an alternate scorer, margin, bootstrap convention, or subset.
- Show power and duration jointly so a lower-joule observation cannot be
  narrated as lower watts or shorter time without evidence.

### Abort and downgrade rules

Do not run a claim-bearing ladder until S-D freezes artifact and quality
identity. A missing or failed quality gate downgrades the result to a labeled
energy/quality trade-off. A quant artifact that does not fit or execute is a
structured capability outcome, not an excluded energy replicate. Do not add a
quant level, swap a reference, change a scorer, or enlarge n after outcomes.

## 4. AP-REASON-VARIANCE-DRAFT — sampled reasoning-path variance

### Prerequisites specific to this plan

This candidate cannot execute merely because a row exists. RQ-ENERGY-VARIANCE
must be promoted under the registry process, P2-015 request-window floors must
exist, and all of these harness gaps from
`docs/specs/rq_energy_variance_design.md` must close with strict validation:

- `G-RQVAR-SEED`: per-bundle non-greedy sampler seed recording;
- `G-RQVAR-FORCED-IDS`: exact forced-token replay on the selected
  runtime;
- `G-RQVAR-REPLAY-MANIFEST`: prompt plus forced-output-token identity;
- `G-RQVAR-EQUIVALENCE-CHECK`: only its exact forced-ID, prompt, state, and
  stop-policy replay-fidelity checks; no natural/forced compute-equivalence
  admission test remains; and
- `G-RQVAR-FLOOR-CONSUMER`: an AP-specific mapping from P2-015 request floors
  to natural-source and forced-replay request windows.

Forced replay is an intervention, not a compute-equivalent observation of
natural sampling conditional on the same output. The design therefore makes
no bridge assumption. An optional natural-versus-replay comparison may be
reported only as a labeled L1 diagnostic and cannot gate, validate, or upgrade
the replay decomposition.

### D-053 registry row

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | `AP-REASON-VARIANCE-DRAFT` / RQ-ENERGY-VARIANCE plus C5-W.2. |
| `family_id` | `FAM-AXI-REASON-REPLAY-DECOMP` contains exactly the two claim-bearing replay components. `FAM-AXI-REASON-DIAGNOSTIC` contains the natural-run variance/distribution, natural-versus-replay comparison, extreme-path, and length displays; every diagnostic is L1/descriptive. There is no bridge or natural-distribution inferential family. |
| `claim_role` | Candidate primary only after RQ promotion: the replay-intervention decomposition into within-fixed-token-sequence and across-token-sequence gross-energy variance. Direct natural-sampling run-to-run variance is a required L1 companion with no inferential claim. Until promotion and freeze, everything is design-only. |
| `selection_scope` | One fixed hard prompt, model artifact, runtime/backend/boundary, named stochastic sampler, process/cache-state policy, and natural-EOS policy with a frozen administrative safety cap. Phase A generates distinct seed-indexed natural token sequences. Phase B probability-samples or prospectively length-stratifies exact sequences from that source set and repeats each under the named forced-token replay intervention. |
| `multiplicity_rule` | One Holm denominator of exactly two covers the within-sequence and across-sequence replay-variance component claims. The natural-run and other diagnostic rows have no directional hypothesis, p-value, equivalence test, or multiplicity-based upgrade. A broader prompt/model screen requires a separately frozen family or remains exploratory. |
| Metric + exact window class | Primary: `J^2` components derived from gross request `gross_energy_j` under forced replay. Required L1 companion: direct natural-run gross request variance, empirical distribution, emitted-token length, stop reason, and cap-hit/censoring state. Idle-subtracted energy is only a labeled within-device descriptive sensitivity. No phase/item claim is owned here. |
| Unit of analysis + dependence structure | Each distinct-seed natural generation supplies one source token sequence and one natural-run energy observation. Selected sequence j has frozen selection weight `w_j`; its forced replays are nested within j. Replay repeats estimate energy variation given a fixed token sequence and are not additional natural sequences. Natural-run bundles are the descriptive companion units only. |
| Estimand / estimator / formula | The primary estimands are `V_within^replay=E_{Y~p_nat}[Var(E_replay|Y)]` and `V_between^replay=Var_{Y~p_nat}[E(E_replay|Y)]`, where Y is the naturally generated token-sequence distribution but E is always measured under the named replay intervention. For selected sequences j with weights `w_j`, replay means `m_j`, variances `s_j^2`, and repeats `k_j`, set `m_w=sum(w_j*m_j)`, `V_between_raw=sum(w_j*(m_j-m_w)^2)`, `C_mean=sum(w_j*(1-w_j)*s_j^2/k_j)`, and `V_between^replay=max(0,V_between_raw-C_mean)`. With calibrated same-design alias variance `a_j^2`, `V_within^replay=sum(w_j*max(0,s_j^2-a_j^2))`. The companion natural-run statistic is the direct sample variance `S_nat^2=sum_i(E_nat,i-Ebar_nat)^2/(N-1)`, reported only descriptively with its empirical distribution/censoring table and no inferential interval or claim. |
| Effect-size / component targets | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-REASON-REPLAY-V1:** freeze minimum relevant `J^2` effects for both replay components, administrative cap, cap-hit downgrade threshold, source-sequence count, selected-path count, and replay count from the 24 excluded pilot bundles. No effect target or MDE is assigned to the L1 natural companion. |
| Inclusion/exclusion + quality-flag waiver rules | Claim-bearing replay bundles require exact frozen output token IDs/counts, prompt/state/stop-policy identity, replay-manifest match, and strict-valid request evidence. Natural source bundles require verified sampler pin/seed, emitted token IDs/counts, stop reason, and strict-valid request evidence. Cap-hit natural paths remain in the descriptive censored table. Missing source seed/IDs or replay mismatch is reported and cannot be waived into replay fidelity or compute equivalence. |
| Order/blocking/covariates | Interleave natural source runs and replay blocks where practical. If replay occurs later, require same-condition sentinels and Window-B-start floor revalidation. Balance/randomize replay order across selected sequence lengths. Record session/block, manifest order, drift/thermal state, cooldown cap, stop reason, token length, source-sequence ID, and replay ordinal. Content-sentinel status gates only length-language diagnostics, not the replay-component identity. |
| Floor gate | **PROVISIONAL-UNTIL-P2-015:** `G-RQVAR-FLOOR-CONSUMER` must supply same-design replay `Sigma_F`, alias variances `a_j^2`, deterministic bounds, and nonlinear remainder support. For across-sequence variance let `H_w=diag(w)-w*w^T` and `a_V=2*H_w*mu`; use `F_between=sqrt(a_V^T Sigma_F a_V)` and `D_between=sum(abs(a_Vi)*d_i)`. For the nonnegative quadratic alias remainder Q, Markov's inequality gives `Pr[Q>trace(H_w*Sigma_F)/gamma]<=gamma`; therefore the guard uses the predeclared `(1-gamma)` upper-quantile bound `Q_between,1-gamma=trace(H_w*Sigma_F)/gamma`, never the trace expectation alone. Thus `G_between=F_between+D_between+Q_between,1-gamma`, with gamma frozen and charged to the same family error budget. For within-sequence variance use `a_W=gradient_e[sum_j(w_j*s_j^2)]`, `F_within=sqrt(a_W^T Sigma_F a_W)`, and `D_within=sum(abs(a_Wi)*d_i)` plus a separately calibrated `(1-gamma)` upper-quantile remainder `Q_within,1-gamma`; if only its expectation is identified, Markov's inequality requires expectation/gamma. Then `G_within=F_within+D_within+Q_within,1-gamma`, including alias-correction uncertainty. Missing covariance, deterministic bound, replay-state support, quadratic expectation/quantile support, or variance gradient forces a dedicated sampled/replay calibration cell. A J floor is never compared directly with a `J^2` component. |
| Error-budget + window-evidence claim gate | Every forced-replay request window entering a component must pass `window_evidence_precheck.gross_request`; consume all D-054 stochastic and deterministic terms in the component gradients and additive bounds. UNKNOWN cadence, anchor, interpolation/aliasing, sensor, drift, or clock consequences apply to the replay mode and can cap/refuse either component. Natural-source windows carry their own precheck/UNKNOWN disposition in the L1 companion table but cannot upgrade the replay claim. |
| MDE/n sizing + predeclared top-up rule | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-REASON-REPLAY-V1:** the source draft `N=80`, nine probability-selected sequences, and `k=6` replays remain provisional. Freeze N/path/k from the 24 excluded pilot bundles' conservative within-sequence, replay-mean, component-floor, and selection-weight precision evidence. Outcome-dependent extension permanently demotes the replay family; it never promotes the natural companion. |
| Denominator provenance requirement | Runtime-observed emitted-token counts and exact emitted output token IDs, stop reason, output-policy label, sampler config, and sampler seed per bundle. Config fallback cannot carry token-normalized companions. Replay denominators are nested within exact path identity. |
| Holdout cells (L3 only) | Not applicable; no L3 route. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 only for the replay-intervention components within the named boundary, prompt, model, sampler, path-selection rule, and forced-replay implementation. The natural-run companion is capped L1. Forbidden upgrade: **no wording may present the replay decomposition as natural-sampling conditional variance**. Also forbidden: intelligence-per-joule, correctness-causal, model-family/architecture-wide variance, cross-boundary uncalibrated, or length-only claims unsupported by content/state controls. |
| Disqualifiers + not-resolvable conditions | Missing floor/error-budget or any required G-RQVAR replay-fidelity prerequisite; unrecorded source seed; unverified sampler; replay token/prompt/state/stop mismatch; unsupported forced replay; high frozen-policy censoring that invalidates selection weights; below-floor `J^2` component; or inadequate component precision. The primary then is `not resolvable`/unsupported; direct natural-run variance may remain only the L1 descriptive companion. |
| Linked manifests/bundle hashes | Pending: promotion record, frozen sampler/prompt/state and replay manifests, path-selection seed/weights, floor/quantile artifacts, contrast registry, replay-fidelity reports, and bundle hashes. |

### Frozen contrast rows

| Draft `contrast_id` | Family / role | Contrast and gate |
|---|---|---|
| `REASON-REPLAY-BETWEEN-SEQUENCE` | `FAM-AXI-REASON-REPLAY-DECOMP` / candidate primary | Corrected `J^2` variation across naturally sourced token sequences, with energy measured only under forced replay and its own additive floor. |
| `REASON-REPLAY-WITHIN-SEQUENCE` | `FAM-AXI-REASON-REPLAY-DECOMP` / candidate primary | Alias-corrected weighted `J^2` replay variation given each fixed token sequence, with its own additive floor. |
| `REASON-NATURAL-RUN-VARIANCE-L1` | `FAM-AXI-REASON-DIAGNOSTIC` / required L1 | Direct natural-run sample variance and empirical/censoring table; no inferential interval, hypothesis, equivalence gate, or conditional-variance wording. |
| `REASON-NATURAL-VS-REPLAY-DIAG` | `FAM-AXI-REASON-DIAGNOSTIC` / optional L1 | Labeled source-natural versus replay-mean energy/latency display; it is not a compute-equivalence test and cannot gate or upgrade either component. |
| `REASON-EXTREME-PATH-DIAG` | `FAM-AXI-REASON-DIAGNOSTIC` / L1 | `m_longest-m_shortest` only if landmarks were prospectively included; never a natural decomposition. |
| `REASON-LENGTH-DIAG` | `FAM-AXI-REASON-DIAGNOSTIC` / L1 | Descriptive natural-run gross-J versus observed-token-length scatter and least-squares summary with fixed session/block labels; no inferential or causal claim. |

### Predeclared sensitivities

- Report the natural-run empirical CDF, sample variance, and frozen descriptive
  quantiles without a normal fit or inferential claim.
- Report natural-EOS, capped-observed, and censored summaries according to the
  frozen cap policy, never by deleting cap hits.
- Compare the primary probability-sampled decomposition with the
  prospectively named weighted stratified estimator; deterministic landmarks
  remain diagnostic.
- Run leave-one-selected-sequence-out influence analysis. Optionally show
  source-natural observations against replay means as an L1 intervention
  diagnostic; no amount of agreement creates a bridge.
- Use the AP-6-style equal-shape content sentinel as a threat-control
  sensitivity before using “length luck” language.

### Abort and downgrade rules

Abort before claim-bearing measurement if promotion, any harness gap, the
floor/error-budget mapping, pilot, or cap/path-selection design is missing. If
forced replay is unsupported or replay fidelity fails, do not estimate the
primary components; the direct natural-run result may remain only the L1
companion. If censoring exceeds the frozen tolerance, retain data and use
capped-policy/censored descriptive wording; do not repair selection weights
after outcomes. Never describe the replay components as natural-sampling
conditional variance. Do not raise the cap, add sequences/replays, or increase
N after outcomes.

## 5. AP-MOE-BATCH-DRAFT — dense/MoE by static-batch interaction

### D-053 registry row

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | `AP-MOE-BATCH-DRAFT` / MOE×BATCH candidate created by D-070. |
| `family_id` | `FAM-AXI-MOE-BATCH-OBSERVED` for gross-energy slope/DID interactions; `FAM-AXI-MOE-BATCH-NORMALIZED` for J/request and J/token interactions; `FAM-AXI-MOE-BATCH-LATENCY` for separate TTFT/end-to-end interactions; and conditional `FAM-AXI-MOE-BATCH-ROUTING` for the two exact routing summaries below. |
| `claim_role` | Observed dense/MoE-by-B interaction: primary. Routing-conditioned mechanism contrasts: secondary and conditional on observability. Memory-fit/unsupported outcomes: structured descriptive. |
| `selection_scope` | One S-D frozen dense/MoE pair, common family/tokenizer/runtime/quantization/output policy and matching rule, one target/boundary, and the exact AP-BATCH 16-request/31-group construction at each model. Corresponding dense/MoE groups contain identical request IDs. Matched-total fallback is a different labeled estimand/family, never a sensitivity substitution. |
| `multiplicity_rule` | Holm separately over every frozen observed-energy, normalized, latency, and—if admitted—routing contrast. Routing admission and its complete denominator freeze before execution; no counter observed after execution creates a family. Gross-energy slope and DID rows share the complete observed-interaction denominator. |
| Metric + exact window class | Primary: block/B aggregate gross group energy. Secondary: exact gross J/request and J/committed-token interactions plus type-7 p95 TTFT/end-to-end interactions. Gross phase energy is descriptive L1 unless separately enumerated. Conditional routing metrics are MoE-arm block/B mean per-request unique-expert count and expert-load CV. Group energy is never attributed to requests/experts. |
| Unit of analysis + dependence structure | A native group is the captured energy unit; the paired-model complete superblock is the inference unit. Each model has 31 corresponding groups and 80 request placements per superblock. Requests, groups, and expert events are nested, not replicates. |
| Estimand / estimator / formula | For model m use AP-BATCH `Ebar_kmB=(B/16)*sum_g(E_kmBg)`. Primary interaction is `beta_MoE-beta_dense`; B-specific DID is `[Ebar_MoE,B-Ebar_MoE,1]-[Ebar_dense,B-Ebar_dense,1]`. J/request uses `sum_g(E)/16`; J/token uses `sum_g(E)/sum_g(T)`, then the same model-by-B DID. Latency uses type-7 p95 over 16 requests per model/B and the same DID separately for TTFT and end-to-end. In the MoE arm only, `U_kB` is the equal-request mean distinct-expert count and `LCV_kB=sd_e(C_e)/mean_e(C_e)` over partition-total activations, null at zero mean. |
| Effect-size target | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-MOEBATCH-V1 (plus S-D/S-B):** freeze gross, normalized, separate latency, and conditional U/LCV interaction targets from the three excluded paired-model pilot superblocks. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid native static batches for both exact artifacts with complete request evidence, matched roster/output policy, verified model-selection scorecard, and realized B. Routing-family inclusion additionally requires auditable expert IDs/activation counts or weights tied to request/scheduler evidence and verified against runtime semantics. Missing routing evidence does not exclude the energy pair; it removes the mechanism family. |
| Order/blocking/covariates | Inherit AP-BATCH `r_0...r_15`, cyclic permutation, chunking, and Latin B/group order. Pair identical group partitions across models and counterbalance model order within each B; 62 group executions per superblock. Record session, position, drift sentinel, realized B, memory state, latency, and frozen model-size descriptors. No post-hoc active/total/KV regressors. |
| Floor gate | **PROVISIONAL-UNTIL-P2-015:** same-design paired-model group calibration must supply joint `Sigma_F` across model x B cells. For slope interaction vector `c_int`, use `F_int=sqrt(c_int^T Sigma_F c_int)`, its transported `D_int`, and additive `G_int=F_int+D_int`; every DID uses its exact `c_DID` and analogous additive guard. J/request uses linear total/16 weights; J/token uses the full two-model/two-B ratio gradient and summed stochastic/deterministic guards. Missing cross-model covariance, unsupported duration/B/state, or any nonlinear input forces refusal and a dedicated 62-group alias-calibration superblock. Latency/routing precision comes from the AP pilot, not a joule floor. |
| Error-budget + window-evidence claim gate | Every dense and MoE group/phase window must pass its metric-specific `window_evidence_precheck`; propagate all D-054 stochastic/deterministic terms through `c_int`, `c_DID`, and ratio gradients. An applicable UNKNOWN or ineligible window for either model caps/refuses the joint interaction. Routing additionally requires verified completeness of expert events; absence removes that family without imputing zero. |
| MDE/n sizing + predeclared top-up rule | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-MOEBATCH-V1:** draft confirmatory `n_blocks=5` freezes only from conservative paired covariance over the three excluded pilot superblocks (62 group executions each; 186 total). If inadequate, report `not resolvable`; never add superblocks after seeing interaction outcomes. |
| Denominator provenance requirement | Each model/B complete partition uses exactly 16 verified requests. J/request is total group gross J/16; J/token is total group J/total observed committed tokens, null at zero. S-D descriptors are selection evidence, not denominators. U and LCV require complete audited request/expert activation records; a mean of request energy ratios or partial routing logs is forbidden. |
| Holdout cells (L3 only) | Not applicable. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 for one named dense/MoE pair, stack, roster, and static policy. D-070 clause 4 forbidden upgrade, verbatim: **no MoE-serving-efficiency generalization from one pair**. Also forbidden: expert-activation-diversity or routing-mechanism claims without auditable expert evidence; continuous/offered-load/scheduler-optimum claims; active-parameter scaling laws. |
| Disqualifiers + not-resolvable conditions | Pair-selection/memory-gate failure, batch unsupported/unobservable, unmatched output policy/roster, missing group floor, below-floor interaction, latency-policy failure, or structured B failure yields the named downgrade. If either model cannot execute B=16, the all-B interaction is unavailable and B=16 is not silently discarded. |
| Linked manifests/bundle hashes | Pending: S-D pair scorecard/artifact hashes, S-B verdict, batch/routing schema versions, roster/order manifest, group-floor evidence, frozen contrast registry, and strict-valid bundle hashes. |

### Frozen contrast rows

| Draft `contrast_id` | Role | Contrast and observability branch |
|---|---|---|
| `MOEBATCH-SLOPE-INTERACTION` | `FAM-AXI-MOE-BATCH-OBSERVED` / primary | Difference between dense and MoE all-B affine slopes on gross group energy. |
| `MOEBATCH-DID-B<value>` | `FAM-AXI-MOE-BATCH-OBSERVED` / secondary | B-specific gross-energy DID against B=1 for each enumerated B. |
| `MOEBATCH-JREQ-DID-B<value>` | `FAM-AXI-MOE-BATCH-NORMALIZED` / secondary | DID in complete-partition total gross J/16. |
| `MOEBATCH-JTOKEN-DID-B<value>` | `FAM-AXI-MOE-BATCH-NORMALIZED` / secondary | DID in partition ratio-of-totals J/committed token with zero rule. |
| `MOEBATCH-TTFT-P95-DID-B<value>` | `FAM-AXI-MOE-BATCH-LATENCY` / secondary | Type-7 p95 TTFT model-by-B DID. |
| `MOEBATCH-E2E-P95-DID-B<value>` | `FAM-AXI-MOE-BATCH-LATENCY` / secondary | Separate type-7 p95 end-to-end model-by-B DID. |
| `MOEBATCH-ROUTING-U-B<value>-VS-B1` | `FAM-AXI-MOE-BATCH-ROUTING` / conditional secondary | MoE-arm B-versus-B1 difference in equal-request unique-expert count U. |
| `MOEBATCH-ROUTING-LCV-B<value>-VS-B1` | `FAM-AXI-MOE-BATCH-ROUTING` / conditional secondary | MoE-arm B-versus-B1 expert-load CV difference; null at zero activation mean and never per-expert joules. |
| `MOEBATCH-CAPACITY-B16` | Structured outcome | First per-model failure is `observed_memory_failure`. `memory_not_fit` requires the AP-BATCH clean reset, successful B=1 health control, and exactly one same-reason B=16 confirmation; otherwise `capacity_unresolved`. Asymmetric failure blocks the all-grid interaction. |

### Predeclared sensitivities

- Report cell means and a categorical model-by-B interaction beside the
  primary slope interaction; neither permits outcome-selected knots.
- Run leave-one-superblock-out influence analysis and the frozen with/without
  drift-term model.
- If routing evidence exists, report per-request routing distributions and
  load-balance summaries without treating requests or experts as energy
  replicates.
- A matched-total pair is not a sensitivity for a matched-active estimand. It
  requires a separately frozen family and explicit relabeling.
- A lower-B descriptive fit after structured B=16 failure is capacity-
  conditioned and cannot inherit the all-B primary role.

### Abort and downgrade rules

Do not execute until S-D freezes a permissible pair, S-B establishes true
native batch support, and the batch-group floor route is accepted. If routing
is not auditable, remove the routing family and retain only the observed
named-pair interaction. For either model's first B=16 failure, apply the exact
AP-BATCH stop/reset/clean-memory/B1-health/one-confirmation rule before using
`memory_not_fit`; reset failure, success on confirmation, or a changed reason
is `capacity_unresolved`. The confirmation is not an energy replicate. An
incomplete common grid requires a new prospective restricted-grid AP.

## 6. AP-5/MoE-2M-DRAFT rider — dense/MoE contrast inside 2M

This is a draft rider to AP-5 with its own multiplicity family. It does not
pool dense/MoE contrasts into AP-5's existing controlled-ladder family and it
does not alter AP-2's profile-contrast family.

### Zero-extra-cost activation condition

“Zero extra quiet-machine cost” is true only if the exact S-D dense/MoE pair
has passed every D-016 gate—including cross-primary-target availability and
8-GB fit/headroom—and that exact pair plus `PILOT-MOE2M-V1` are already in the
frozen cross-target 2M model/pilot set with the same profiles, blocks, and
repetitions. Under that condition the rider analyzes already-authorized 2M
bundles and adds no capture cell or repetition. If any condition is false, the
rider stays inactive: a model-set change or extra Mac bundle is additional
quiet-Mac work and needs a new owner, AP, queue/funding decision, and
prospective freeze. This document does not authorize that expansion.

### D-053 registry row

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | `AP-5/MOE-2M-DRAFT` rider / C5-1.1, C5-1.9, and the RQ-TWO-MODEL-ACTIVE-NONCLAIM guard. |
| `family_id` | `FAM-2M-DENSE-MOE-ENERGY`, `FAM-2M-DENSE-MOE-NORMALIZED`, `FAM-2M-DENSE-MOE-DECOMPOSITION` (power/duration), `FAM-2M-DENSE-MOE-LATENCY` (TTFT/end-to-end), and descriptive `FAM-2M-DENSE-MOE-DIAGNOSTIC` (output/stop/quality divergence), all separate from AP-5/AP-2 families. |
| `claim_role` | Secondary named-pair contrast inside an already frozen 2M campaign. Model-by-profile interaction is secondary only if enumerated prospectively. |
| `selection_scope` | The exact D-016-passing S-D dense/MoE pair already present in the frozen cross-target 2M matrix; the existing AP-2 profiles, targets, boundaries, runtime/quant recipes, prompts, output policies, and blocks. No substitute pair, added model, added profile, or added run. |
| `multiplicity_rule` | Holm separately across complete energy/profile-interaction, normalized, decomposition, and latency families. Every searched target/profile/endpoint is in the exact rider denominator; no alpha is borrowed from AP-2/AP-5 and no telemetry boundary is pooled. |
| Metric + exact window class | Primary: gross request energy by 2M profile. Secondary: ratio-of-totals gross J/committed token, request mean power/duration, and separate TTFT/end-to-end latency. Gross phase energy is descriptive L1 unless separately enumerated. Idle-subtracted request energy is labeled within-device secondary only. |
| Unit of analysis + dependence structure | Dense/MoE requests are paired by target, profile, frozen source-request weight, output policy, and block; complete block is the inference unit. Requests/profile cells/phase windows within block are nested, not independent replicates. |
| Estimand / estimator / formula | With frozen source weights `w_i`, block/target/profile energy gap is `DeltaE_k=sum_i(w_i*(E_MoE,ki-E_dense,ki))`. Arm J/token is `sum_i(w_i*E_mi)/sum_i(w_i*T_mi)`, null at zero; contrast is MoE minus dense. Power, duration, TTFT, and end-to-end use the same weighted paired difference as separate endpoints. A frozen model-by-profile interaction compares these `DeltaE` values and is not active-parameter scaling. |
| Effect-size target | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-MOE2M-V1 (plus S-D/D-016):** freeze named-pair gross, profile-interaction, normalized, power/duration, and separate latency effects from the three excluded paired pilot blocks per target/profile. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid source bundles only; exact D-016/S-D artifacts, same frozen runtime/quant/output policy, observed token counts/stop reasons, and source campaign pairing required. All output/quality differences are reported. No waiver can turn a non-D-016 pair or newly added capture into this rider. |
| Order/blocking/covariates | Inherit the source 2M counterbalanced order and drift sentinels; pair models within target/profile/block and record model order. Use only the source campaign's frozen session/block terms. |
| Floor gate | **PROVISIONAL-UNTIL-P2-015:** within each target/profile, paired model energy uses `c=(1,-1)`, `F_pair=sqrt(c^T Sigma_F c)`, transported `D_pair`, and additive `G_pair=F_pair+D_pair`; profile interactions use their full linear contrast vector and analogous additive guard. J/token uses the joint two-model ratio gradient/covariance and sums its stochastic/deterministic bounds. Phase energy uses only same-target eligible phase calibration. Target/boundary floors never transport across devices; missing model-state covariance or denominator support refuses and requires a dedicated paired calibration cell. |
| Error-budget + window-evidence claim gate | Every source request/phase window must pass its metric-specific precheck. Consume each target's complete D-054 error-budget row and propagate stochastic/deterministic terms through source weights and paired/interaction/ratio gradients. Applicable UNKNOWN terms retain target-specific caps; a cap below L2 or any ineligible contributing window refuses that target/profile contrast. |
| MDE/n sizing + predeclared top-up rule | **PROVISIONAL-UNTIL-P2-015-AND-PILOT-MOE2M-V1:** confirmatory source/rider blocks freeze from the three excluded paired pilot blocks per target/profile, not from generic P2-015 request variance. The rider adds zero repetitions beyond the already-frozen source plan. If the pilot is absent or n is inadequate, the rider is inactive/`not resolvable`; any extra run breaks zero-extra-cost and needs a new plan. |
| Denominator provenance requirement | Fixed source weights apply in both models. J/token is weighted total gross J divided by weighted total runtime-observed committed tokens per model/block, null at zero; means of ratios/config counts are forbidden. D-016/S-D active/total/KV/headroom values remain selection descriptors, not energy denominators. |
| Holdout cells (L3 only) | Not applicable. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 pairwise for the named models, profiles, targets, and boundaries. D-070 clause 4 forbidden upgrade, verbatim: **no MoE-serving-efficiency generalization from one pair**. Also forbidden: active-parameter scaling; model-family/architecture-wide efficiency; active+total+KV regression from this pair; cross-boundary winner without calibration. |
| Disqualifiers + not-resolvable conditions | Pair fails any D-016 gate; pair is absent from the frozen 2M matrix; extra capture would be required; artifact/runtime/output policy differs; profile pairing is incomplete; floor missing/below-floor; or output/stop/quality divergence defeats the frozen interpretation. The rider then stays inactive or reports the named downgrade. |
| Linked manifests/bundle hashes | Pending: D-016 closure and S-D scorecard, source AP-2/2M registry and campaign hashes, rider contrast registry, floor artifacts per target, and source bundle hashes. |

### Frozen contrast rows

| Draft `contrast_id` | Family / role | Contrast and gate |
|---|---|---|
| `MOE2M-<target>-<profile>-GROSS` | `FAM-2M-DENSE-MOE-ENERGY` / secondary | Paired fixed-weight MoE-minus-dense gross request energy. |
| `MOE2M-<target>-<profile>-PER-COMMITTED` | `FAM-2M-DENSE-MOE-NORMALIZED` / secondary | Difference in model block ratio-of-totals gross J/committed token. |
| `MOE2M-<target>-<profile>-POWER` | `FAM-2M-DENSE-MOE-DECOMPOSITION` / secondary | Paired fixed-weight request mean-power difference. |
| `MOE2M-<target>-<profile>-DURATION` | `FAM-2M-DENSE-MOE-DECOMPOSITION` / secondary | Separate paired request-duration difference. |
| `MOE2M-<target>-<profile>-TTFT` | `FAM-2M-DENSE-MOE-LATENCY` / secondary | Paired TTFT difference. |
| `MOE2M-<target>-<profile>-E2E` | `FAM-2M-DENSE-MOE-LATENCY` / secondary | Separate paired end-to-end difference. |
| `MOE2M-<target>-PROFILE-INTERACTION` | `FAM-2M-DENSE-MOE-ENERGY` / secondary | Named-pair gross-energy gap variation across existing profiles; no scaling law. |
| `MOE2M-<target>-<profile>-OUTPUT-DIVERGENCE` | `FAM-2M-DENSE-MOE-DIAGNOSTIC` / descriptive | Complete committed-token, stop-reason, score, and missing/malformed differences; no favorable-stratum inference. |
| `MOE2M-ACTIVE-SCALING-GUARD` | Negative guard | The two-model result cannot support active-parameter scaling, even if directionally consistent with that hypothesis. |

### Predeclared sensitivities

- Report each profile/target separately and the frozen with/without drift-term
  paired model; do not pool heterogeneous telemetry boundaries.
- Show gross request energy, committed-token companion, duration, power, and
  output/stop differences together so the named-pair result stays workload-
  conditioned.
- Run leave-one-block-out influence analysis using only the source blocks.
- A matched-total fallback or Mac-only pair is a different estimand and cannot
  enter as a sensitivity or preserve the zero-extra-cost label.

### Abort and downgrade rules

At registry freeze, evaluate the zero-extra-cost activation condition before
any 2M measurement. If it fails, leave the rider inactive and surface the
model/campaign choice to the lead; do not silently enlarge 2M. If it activates
but the `PILOT-MOE2M-V1`-frozen n or the target-specific P2-015/dedicated floor
route cannot resolve the pair, report the fixed-n result as `not resolvable`
rather than adding repetitions.

## 7. Bounded conversion to frozen plans

After P2-015—and only after all plan-specific prerequisites—the lead can
convert these drafts into `docs/contracts/analysis_plans.md` and registry rows
with a bounded edit:

1. Replace each floor marker with the cited P2-015/dedicated-calibration row,
   exact estimand-scale transport/refusal proof, complete D-054 error-budget,
   and window-precheck disposition. Replace each n/MDE marker only with its
   named excluded pilot's conservative covariance, target, final n, MDE
   arithmetic, and frozen replacement rule.
2. Enumerate every final `contrast_id`, role, family, candidate set, alpha or
   q rule, and exact multiplicity denominator; delete unused conditional rows
   rather than leaving latent choices.
3. Fill exact model/runtime/scorer/roster/path identities, order/block
   manifests, latency/quality/censoring policies, and structured-outcome
   schemas.
4. Bind the final rows, campaign manifests, calibration hash, and artifact
   hashes in the frozen registry before any claim-bearing campaign starts.
5. Confirm that no provisional marker remains, pilot bundles are excluded,
   and every forbidden upgrade and abort/downgrade rule survived conversion.

If P2-015 refuses floor/error-budget transport or the AP pilot makes its target
underpowered, the plan returns for prospective redesign. It does not run an
underpowered fixed design while promising resolution, silently consume an
unowned quiet-Mac slot, or acquire an L3 claim.
