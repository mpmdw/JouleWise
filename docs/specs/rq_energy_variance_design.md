# RQ-ENERGY-VARIANCE Candidate Design Sketch

Status: candidate design sketch for `RQ-ENERGY-VARIANCE` (Ed, 2026-07-09).
This document is analysis-plan-only. Promotion to a claim-bearing campaign
requires a council round and a frozen analysis-registry entry before execution.

Registry boundary: ceiling `L2 within boundary`; forbidden upgrades are no
intelligence-per-joule claim and no correctness-causal claim under the C-004
quarantine. Correctness may appear only as a quarantined annotation with
stop-reason audit, never as the causal explanation for energy variance.

## Question

For one fixed hard prompt under one named sampler, what is the distribution of
request energy across sampled completions? Operationally: can the model "get
lucky" by emitting a shorter reasoning path, and how much request-energy risk
is in the tail rather than the mean?

This is not a model-quality question. The primary object is the same-boundary
distribution of gross and idle-subtracted request energy for a fixed
`model x backend x prompt x sampler` cell, with sampler parameters pinned and
the sampler seed recorded per bundle.

## Estimands

Let `P` be the fixed prompt, `S` the named sampler configuration
(`temperature`, `top_p`, any top-k/min-p/repetition settings, stop policy,
maximum-token policy, tokenizer/model/runtime identity), and `U_i` the recorded
sampler seed for sampled bundle `i`. Let `Y_i` be the realized emitted-token ID
path, `L_i = len(Y_i)`, and `E_i` the request energy for the measured boundary
and window class.

Primary distribution:

```text
F_E(e | P, S) = Pr(E <= e for repeated sampled requests with seed U recorded)
```

Report both `gross_energy_j` and `energy_request_j` when available. The claim
must name the boundary, for example `M3 Max / MLX / powermetrics SoC rails`.

Variance decomposition:

```text
Var(E) = E_path[Var(E | Y)] + Var_path(E[E | Y])
```

The first term is the replay-estimated residual for a fixed emitted-token path:
instrument repeatability, hardware drift, thermal state, controller residue,
and any remaining deterministic-runtime jitter. It is claim-bearing only above
the P2-015 floor for the same metric/window class. The second term is the
between-path component: the energy variation attached to different sampled
emitted-token paths. This is the closest operational version of "luck."

Length-facing companion decomposition:

```text
Var(E) = E_L[Var(E | L)] + Var_L(E[E | L])
```

This is easier to explain but weaker scientifically because equal length does
not imply equal decoded work. The report should show length as the primary
visible covariate, but the decomposition should be labeled exact-path replay
when it conditions on recorded token IDs. Any same-length content effect is a
threat to the length-only story and should be controlled with an AP-6-style
content sentinel, or reported as unresolved.

Tail metrics:

- `P90/P10 energy ratio`: ratio of the empirical 90th and 10th percentiles,
  with nonparametric order-statistic confidence intervals when `N` is large
  enough to make them informative.
- `energy-at-risk`: `P90(E) - median(E)` and optionally `P95(E) - median(E)`.
  Use absolute joules and percentage of median request energy. `P95` is
  exploratory unless `N` is large enough; at `N = 80`, the P95 estimate is too
  dependent on the top few observations for L2 wording.
- `path-length risk`: `P90(L) / P10(L)`, `P90(E | sampled) - E_replay(short
  quantile path)`, and a scatter or smooth of `E` versus emitted-token count.
  This is descriptive unless a predeclared model contrast is frozen.

Estimator choices:

- The empirical CDF is the primary distribution estimator. Do not fit a normal
  distribution to energy tails.
- Quantiles use type-7 or nearest-order statistics consistently, but confidence
  intervals should be nonparametric order-statistic intervals in the report.
  Approximate 95% order-statistic bands illustrate feasibility:
  `N = 50` gives P90 between roughly order 42 and 50, and P10 between order 2
  and 11; `N = 80` gives P90 between order 67 and 79, and P10 between order 4
  and 16; `N = 100` gives P90 between order 85 and 97, and P10 between order 6
  and 18. This is why `N = 30` is a pilot, not a tail-metric result.
- Variance components use ANOVA/method-of-moments on replay means when enough
  paths are replayed under a probability selection design. Claim-bearing
  decomposition requires either a random sample of Phase-A paths, or a
  decile-stratified random sample with explicit stratum weights and a declared
  target estimand. With only deterministic landmark paths, report a diagnostic
  range or approximation, not a population decomposition.

## Replay-Decomposition Protocol

### Phase A: sample paths once

Run `N` independent request bundles for the fixed prompt under the named
sampler. Requirements per bundle:

- sampler configuration pinned and verified;
- sampler seed recorded in bundle metadata and summary;
- emitted output token IDs recorded;
- runtime-observed emitted-token count and stop reason recorded;
- strict validation passed;
- manifest order recorded and interleaved with any replay/calibration blocks
  if the run is executed in multiple sessions.

Primary stop policy: natural EOS with an administrative safety cap.

Rationale: the scientific question is about the model's sampled request-energy
distribution, including early and late termination. A fixed output cap changes
the estimand by censoring long reasoning paths. If a safety cap is necessary,
cap-hit paths are right-censored tail observations; report cap-hit fraction,
stop-reason table, and tail metrics both including capped observed energy and
with cap-hit rows marked as censored. Do not call a capped distribution the
natural-EOS distribution.

If operational safety requires a hard fixed cap as the primary run, name the
estimand `capped sampled request-energy distribution at cap C`. That version
can still answer "energy-at-risk under this product policy" but not the full
natural reasoning-path question.

### Phase B: replay selected paths deterministically

Convert selected Phase-A emitted-token ID paths into deterministic ids-native
replay workloads. The replay script is the recorded output token IDs, not text
retokenized from the response. Replay each selected path `k` times with the
same prompt, runtime, model, and boundary, forcing the runtime to emit exactly
that token path or to execute an equivalent forced-token scoring/decode path.

Selection rule:

- Minimal diagnostic selection: shortest, median, and longest natural-EOS
  paths by emitted-token length, tie-broken by Phase-A manifest order. This is
  easy to explain and directly addresses the "lucky short path" intuition.
- Quantile diagnostic/approximation: select at least nine landmark paths:
  shortest, P10, P25, median, P75, P90, longest, plus two randomly selected
  interior paths from the frozen Phase-A order. Replay each `k = 6` times. This
  is useful for showing the length-facing shape of the energy curve, but it is
  not a minimal credible decomposition because deterministic quantile/extreme
  paths do not define a probability sample from the empirical path distribution.
- Minimal claim-bearing decomposition: replay a simple random sample of at
  least nine natural-EOS Phase-A paths, selected after freezing the Phase-A
  manifest and before inspecting replay energy. The target estimand is the
  variance decomposition over the empirical Phase-A natural-EOS path
  distribution, with equal path weights. Replay each selected path `k = 6`
  times.
- Fuller claim-bearing decomposition: stratify Phase-A paths by
  emitted-token-length decile, randomly select two paths per non-empty decile,
  and replay `k = 5` each. Declare stratum weights in advance as
  `W_d = M_d / M`, where `M_d` is the number of eligible Phase-A paths in decile
  `d` and `M` is the eligible Phase-A path count. The target estimand is the
  same empirical Phase-A natural-EOS path distribution, estimated with the
  predeclared decile weights. This supports a length-conditioned residual
  estimate and exposes same-length content spread.

Bias note: shortest/median/longest are order statistics selected because they
are extreme. Their replay means are valid for those realized paths, but they
do not by themselves estimate the average residual variance across the sampled
path distribution. Use random Phase-A path replay or decile-stratified random
replay with explicit weights for claim-bearing decomposition.

Combine Phase A and B:

1. Estimate `F_E` and tail metrics directly from Phase-A natural sampled
   request energies.
2. For each replayed path `j`, estimate `mu_j` and `sigma_j^2` from the `k`
   deterministic replays.
3. Floor-gate each path's replay residual scale using the P2-015 request-window
   floor for the same metric/window class. If replay residuals are below floor,
   report residual as `not resolvable` and bound the residual term by the
   floor rather than over-interpreting the point estimate.
4. Estimate the exact-path between component from replay means only under the
   declared probability selection design. For simple random path replay, use
   equal empirical-path weights. For decile-stratified random replay, use the
   predeclared `W_d = M_d / M` stratum weights. For the nine-landmark quantile
   design, report a quantile diagnostic/approximation, not a claim-bearing
   variance decomposition. For shortest/median/longest only, report a
   diagnostic contrast: `mu_longest - mu_shortest`, not a full variance
   decomposition.
5. Compare the Phase-A natural sampled `E_i ~ L_i` relationship to Phase-B
   replay means. A mismatch indicates thermal/order drift, runtime state, or
   forced-replay non-equivalence.

### Harness support today

Existing support:

- ids-native prompt delivery exists for AP-6-style workloads and records
  `prompt_source="token_ids"` with BOS-less delivery where required by D-046.
- Prompt token identity provenance is recorded per bundle under D-033.
- Capture hardening from the 2026-07-09 CP-5 resume records output token IDs:
  `tokens.jsonl.token_id` and `emitted_token_ids` matching emitted counts.
- Sampler pinning now fails closed when the adapter cannot verify the sampler
  pin, per the D-047 amendment.
- Stage 3.0.1 shows same-stack MLX replay feasibility for prompt-cache
  prefill/resume under greedy decode, with token identity matching in the
  tested replay spike.

Missing support and rough size:

- `G-RQVAR-SEED`: per-bundle sampler-seed recording for non-greedy sampled
  single-request runs and suite-like manifests. Rough size: small schema and
  adapter/controller change, plus strict validation.
- `G-RQVAR-FORCED-IDS`: forced-token replay mode in each runtime adapter. The
  runtime must either force logits through a provided output-token ID script or
  execute an equivalent scoring path with the same compute envelope. Rough
  size: medium for MLX, larger for runtimes without stable token-forcing APIs.
- `G-RQVAR-REPLAY-MANIFEST`: manifest/schema support for a replay workload
  whose identity is `prompt_token_ids + forced_output_token_ids + tokenizer`.
  Rough size: small to medium, mostly validation and provenance.
- `G-RQVAR-EQUIVALENCE-CHECK`: replay equivalence validator proving the replay
  consumed the exact forced IDs, same stop policy, and same prompt identity.
  Rough size: small once forced replay exists.
- `G-RQVAR-FLOOR-CONSUMER`: AP-specific mapping from P2-015 request floors to
  sampled and forced-replay request windows. Rough size: documentation and
  reducer/report wiring.

Important limitation: Stage 3.0.1 is evidence that replayable token identity
is feasible on the current MLX stack, not proof that sampled output paths can
already be forced as measured workloads. The forced-token replay mode is the
load-bearing missing instrument trick.

## Confounds And Threats

Thermal ordering:

- Interleave Phase A sampled runs and Phase B replay blocks where practical.
  If Phase B must run later, insert same-condition sentinels and use the
  Window-B-start floor revalidation logic. Preserve manifest order and cap-hit
  flags.
- Replay selected paths in randomized or balanced order, not shortest to
  longest, because monotone thermal drift can masquerade as path-length
  energy.

KV-cache and runtime state:

- Same prompt and same runtime process policy must be frozen. Fresh-process
  and resident-process modes are different workloads.
- Prompt-cache warmth, OS page cache, and MLX kernel caches are allowed only
  if the same state policy applies to Phase A and Phase B and is recorded.
- Do not use KV replay evidence to claim cross-machine portability; 3.0.1 was
  same-machine, same-venv evidence.

Path length versus path content:

- Longer paths usually cost more, but same length can still differ by token
  content, attention/cache behavior, or runtime kernels.
- Use an AP-6-style content sentinel as the control: fixed shape, ids-native,
  BOS-less where applicable, different token content. If the content sentinel
  clears the floor, the RQVAR report must not collapse all between-path energy
  into "length luck."

Stop-reason censoring:

- Natural EOS bundles and capped bundles are different evidence classes.
- Report stop reason counts, cap-hit fraction, emitted-token distribution, and
  whether tail metrics are natural-EOS, capped-policy, or censored summaries.
- A high cap-hit fraction means the upper tail is not estimable. Recommended
  rule: if cap hits exceed 5% at the chosen cap, P90 is suspect; if cap hits
  exceed 10%, P90/P10 and energy-at-risk cannot carry L2 natural-EOS wording.
  Increasing `N` at the same cap narrows sampling error but does not recover the
  censored upper tail. The remedy is to raise/redeclare the cap under the
  predeclared cap policy and rerun or augment compatibly, or to downgrade the
  claim to capped-policy/censored wording.

N sizing:

- Mean-energy uncertainty is cheap; distribution tails and variance components
  are not. Observed request-energy CV anchors in the AP contract are 0.3%
  flagship, 1.4% first real gross, and 7.4% contaminated idle-subtracted.
- Standard error of a Phase-A mean is `CV / sqrt(N)`: at `N = 80`, the three
  anchors give about 0.034%, 0.157%, and 0.827% of the mean. This is adequate
  for a mean, but it says little about P90/P10.
- Replay mean precision for one selected path is `CV / sqrt(k)`: at `k = 6`,
  the same anchors give about 0.12%, 0.57%, and 3.02%. A contaminated
  idle-subtracted residual can swamp a path difference unless the contrast is
  large and floor-clearing.
- Relative uncertainty of a normal-theory sample variance is approximately
  `sqrt(2 / (n - 1))`. That is 22.7% at `n = 40`, 16.0% at `n = 80`, and
  14.2% at `n = 100` before non-normal tails. Use those as optimism bounds,
  not guarantees.
- Minimal credible `N` for tail reporting is `N = 80`; `N = 50` is acceptable
  for pilot P90/P10 plots but not strong tail wording. `N = 100` is better if
  the lead wants a quantile figure to survive review.

## Draft Analysis-Plan Row

This is a draft row only. It must not be inserted into
`docs/contracts/analysis_plans.md` until a council round promotes the
candidate.

| Field | Draft value |
|---|---|
| Plan ID / RQ consumer | AP-RQVAR-DRAFT / `RQ-ENERGY-VARIANCE` sampled request-energy distribution. |
| family_id | `FAM-RQVAR-SAMPLED-ENERGY-DIST` for one frozen prompt/model/sampler campaign; fuller 3-prompt x 2-model execution either freezes six cell-specific families or one explicit six-cell family before execution. |
| claim_role | Candidate primary if promoted; until then exploratory/design-only. |
| selection_scope | One fixed hard prompt, one model, one runtime/backend/boundary, one named sampler config, recorded sampler seeds, natural-EOS policy with administrative cap, Phase-A sampled request energies, and Phase-B deterministic replay of frozen emitted-token ID paths. |
| multiplicity_rule | For a one-cell campaign, Holm across predeclared claim-bearing tail and decomposition contrasts: `P90/P10`, `P90 - median`, between-path variance component, and shortest-vs-longest replay contrast. Exploratory plots and unplanned thresholds carry no confirmatory inference. For multi-prompt/model sweeps, freeze the exact Holm denominator across all prompt/model cells or use BH at a declared q level for exploratory tail screening. |
| Metric + exact window class | `gross_energy_j` and `energy_request_j` on gross and idle-subtracted request windows; companion emitted-token length and stop reason. No item/phase energy claim unless a separate phase AP row is written. |
| Unit of analysis + dependence structure | Phase-A bundle is the sampled-path unit; Phase-B replay bundle is nested within selected emitted-token path. Uncertainty for the natural distribution is across sampled seeds; replay residual uncertainty is within path and must not be pooled as independent sampled paths. |
| Estimator/formula | Empirical CDF and quantiles for Phase A; nonparametric order-statistic quantile CIs; exact-path decomposition `Var(E)=E_path[Var(E|Y)] + Var_path(E[E|Y])` using replay means and within-path variances only under a declared random or decile-stratified random Phase-B path-selection design with explicit weights and target estimand; shortest/median/longest or nine-landmark quantile replay supports diagnostic contrasts/approximations, not full decomposition. |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only. Missing sampler seed, missing emitted-token IDs, unverified sampler pin, replay-token mismatch, or missing stop reason excludes a bundle from claim-bearing analysis. Quality-flag waivers must be named; cap-hit bundles are retained as censored observations and reported separately. |
| Order/blocking/covariates | Phase A sampled runs and Phase B replay blocks interleaved where practical; replay order balanced/randomized across selected path lengths; session/block, manifest order, cooldown cap hit, thermal state, and stop reason recorded. Length is the primary explanatory covariate; content-sentinel status is a required threat-control covariate when making length-luck language. |
| Floor gate | pending-P2-015: `max(floor_abs_j, floor_cmp_j)` for the same backend, metric, and request-window class; replay residual and replay contrasts must clear the relevant floor or be reported `not resolvable`/`unresolved` under the standing three-way rule. |
| MDE/n sizing + predeclared top-up rule | Minimal credible: Phase A `N = 80` sampled bundles plus Phase B `9 randomly selected paths x k = 6` replays for claim-bearing decomposition; the nine-landmark quantile replay is diagnostic/approximate unless separately randomized and weighted. Top up Phase A to `N = 100` only if P90/P10 CI is too wide for the planned figure. If cap hits exceed 5%, do not treat larger `N` as a cure; raise/redeclare the cap under the predeclared cap policy and rerun/augment compatibly, or downgrade to capped-policy/censored wording. Top up replay to `k = 10` for any selected path whose replay CI or floor status controls the headline. |
| Denominator provenance requirement | Runtime-observed emitted-token counts, emitted output token IDs, stop reason, output policy label, sampler config, and sampler seed per bundle. Config fallback cannot support token-normalized companion claims. |
| Holdout cells (L3 only) | not applicable; ceiling is L2 within boundary. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 within the named boundary and frozen sampler. Forbidden upgrades: no intelligence-per-joule; no correctness-causal claim; no model-family or architecture-wide variance law; no cross-boundary comparison without calibration. |
| Disqualifiers + not-resolvable conditions | P2-015 floor missing; seed not recorded; sampler pin unverified; forced replay not equivalent; cap-hit fraction too high for natural-tail estimation; below-floor residuals or contrasts; content sentinel shows same-length content effect but report attributes all variance to length; fewer than `N = 50` Phase-A sampled paths for tail metrics. |
| Linked manifests/bundle hashes | pending post-execution. |

Correctness annotation, if any, must be quarantined: report scorer/version,
malformed-as-incorrect policy if applicable, stop reasons, and response hashes,
but do not use correctness to explain energy variance except as exploratory
metadata outside the L2 claim.

## Feasibility

Assumptions:

- P2-015 request-window floors already exist for the metric/window class.
- Forced-token replay mode exists for the target runtime.
- Throughput uses the observed Tier-1 planning range from P2-015:
  30 to 75 strict-valid bundles/hour after ordinary cooldown.
- Add 10% replacement buffer for strict-validation failures, sampler refusals,
  cap-hit policy retries, or replay equivalence failures.

Minimal diagnostic, not full decomposition:

- Phase A: `N = 50` natural sampled bundles.
- Phase B: shortest/median/longest paths, `k = 10` each: 30 replay bundles.
- Total: 80 bundles, or 88 with 10% buffer.
- Runtime: 1.07 to 2.67 hours without buffer; 1.17 to 2.93 hours with buffer.
- Claim use: pilot distribution and path-extreme diagnostic only. P90/P10 CI is
  weak; variance decomposition is not claim-bearing.

Minimal credible one-cell version:

- Scope: one model, one hard prompt, one sampler config.
- Phase A: `N = 80` natural sampled bundles.
- Phase B: nine randomly selected natural-EOS Phase-A paths, `k = 6` each: 54
  replay bundles.
- Total: 134 bundles, or 148 with 10% buffer.
- Runtime: 1.79 to 4.47 hours without buffer; 1.97 to 4.93 hours with buffer.
- Claim use: candidate L2 within-boundary distribution and replay-based
  decomposition over the empirical Phase-A path distribution if floors,
  quantile CIs, cap-hit audit, and replay equivalence all pass. Deterministic
  nine-landmark quantile replay remains a diagnostic/approximation.

Stronger one-cell version:

- Phase A: `N = 100` natural sampled bundles.
- Phase B: decile-stratified random replay with two paths per non-empty length
  decile and predeclared `W_d = M_d / M` weights, `20 x k = 5`: 100 replay
  bundles when all deciles are populated.
- Total: 200 bundles, or 220 with 10% buffer.
- Runtime: 2.67 to 6.67 hours without buffer; 2.93 to 7.33 hours with buffer.
- Claim use: cleaner P90/P10 reporting, weighted stratified decomposition, and
  length/content residual diagnostics.

Fuller version:

- Scope: three hard prompts x two models x one sampler config each.
- Use the minimal credible one-cell design per cell: 134 bundles x 6 cells =
  804 bundles, or 885 with 10% buffer.
- Runtime: 10.72 to 26.80 hours without buffer; 11.80 to 29.50 hours with
  buffer.
- Claim use: six within-boundary cell results. Do not upgrade to a model-family
  law; this is still prompt/model-conditioned unless a later council freezes a
  broader generalization design.

Rejected alternatives:

- Fixed cap as primary estimand: useful for product policy, but it censors the
  long-reasoning tail and does not answer the natural "lucky short path"
  question.
- Replay only shortest/median/longest and call it a decomposition: too biased
  toward selected order statistics. Keep it as a diagnostic.
- Text replay from response strings: retokenization drift would defeat the
  identity guarantee. Replay must use recorded output token IDs.
- Fit a parametric distribution for tails: energy tails under sampling are
  exactly where non-normal behavior is plausible. Use empirical CDF and
  order-statistic CIs.
- Attribute between-path variance entirely to reasoning length: same-length
  token content can matter. The AP-6 content sentinel is the named control.
