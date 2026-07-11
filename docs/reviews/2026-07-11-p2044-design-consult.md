# P2-044 idle-ESS design consultation + lead adjudication (2026-07-11)

> Pre-decision design consult (gpt-5.6-sol xhigh) per the design-consult-by-default
> doctrine; grounded in all six retained raw idle traces. LEAD ADJUDICATION of the
> five requested rulings: (1) independent_run covariance RATIFIED; (2) 10s
> powermetrics bandwidth APPROVED (methodology — flagged for Ed veto at the C-028
> bookkeeping D-030 amendment); (3) powermetrics-only scope + backend_policy_not_frozen
> APPROVED; (4) six legacy bundles re-reduced under 0.4.1 for analysis, originals
> retained as history, APPROVED; (5) fail-closed irregular cadence, no resampling in
> v1, APPROVED. Reducer version: 0.4.1 with 0.4.0 re-reduction rejection, per the
> consult's D-030 reasoning. This record + the freeze list in §4 constitute the
> P2-044 implementation contract once PR #54 lands.

## Recommendation

Adopt a single governed estimator: **Newey–West/Bartlett HAC variance for the idle-power mean, with a frozen 10 s physical bandwidth and an ESS capped at the raw count**. Do not select between block means and HAC after seeing a trace, and do not use block means in the governed result.

This fits the retained corpus better than block means: every trace has 300 samples, regular cadence, and roughly 36 s duration—enough for HAC—while a 10 s block-mean design would leave only three blocks and a very noisy variance estimate. It also plugs directly into P2-037’s already-built stochastic-term interface.

### Corpus evidence

All six configs request 30 s at 10 Hz, but the raw powermetrics records span 35.79–38.15 s, with median intervals 0.119–0.128 s—about 7.8–8.4 effective samples/s. Each trace contains exactly 300 interval-power observations.

Using the proposed kernel:

- \(H=10\) s.
- \(L=\lfloor H/\operatorname{median}(\Delta t)\rfloor\).
- Bartlett HAC variance, floored at the IID variance-of-mean so estimated ESS cannot exceed raw \(n\).
- No trimming or detrending.

| Retained raw idle trace | n | Span (s) | Median Δt (s) | lag-1 ρ | L | Governed ESS | Variance inflation vs current \(s^2/n\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| [local r1 raw idle](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r1/raw/powermetrics_idle.plist) | 300 | 36.010 | 0.1200 | 0.951 | 83 | 6.31 | 47.54× |
| [local r2 raw idle](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r2/raw/powermetrics_idle.plist) | 300 | 35.850 | 0.1198 | −0.014 | 83 | 300.00 | 1.00× |
| [local r3 raw idle](/Users/edr/code/JouleWise/runs/example-mac-mlx-local__r3/raw/powermetrics_idle.plist) | 300 | 38.148 | 0.1275 | 0.116 | 78 | 300.00 | 1.00× |
| [Qwen r1 raw idle](/Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r1/raw/powermetrics_idle.plist) | 300 | 35.805 | 0.1194 | −0.012 | 83 | 300.00 | 1.00× |
| [Qwen r2 raw idle](/Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r2/raw/powermetrics_idle.plist) | 300 | 35.794 | 0.1193 | 0.007 | 83 | 300.00 | 1.00× |
| [Qwen r3 raw idle](/Users/edr/code/JouleWise/runs/example-mac-mlx-qwen35-122b-512t__r3/raw/powermetrics_idle.plist) | 300 | 35.970 | 0.1199 | 0.713 | 83 | 33.10 | 9.06× |

The result is substantively important. For local r1, the current idle-energy variance term is approximately 0.428 J² and becomes 20.35 J²; for Qwen r3 it changes from 0.165 J² to 1.493 J². The other four retain the conservative IID floor. Those values use each bundle’s actual measured-window duration and the named raw traces above.

The 10 s bandwidth is justified by the historical traces: local r1 remains positively correlated at lag 50—about 6 s—but is approximately decorrelated by lag 75—about 9 s; Qwen r3’s dependence decays earlier. A 10 s taper covers the observed positive dependence without consuming nearly the entire 36 s trace.

## 1. Exact estimator

For idle totals \(x_0,\ldots,x_{n-1}\), using the same arithmetic rail-sum observations that produced the recorded idle mean:

\[
s^2=\frac{1}{n-1}\sum_t(x_t-\bar{x})^2,\qquad
v_{\mathrm{iid}}=\frac{s^2}{n}
\]

\[
\gamma_k=\frac{1}{n}\sum_{t=k}^{n-1}(x_t-\bar{x})(x_{t-k}-\bar{x})
\]

\[
v_{\mathrm{HAC}}=
\frac{1}{n}\left[
\gamma_0+
2\sum_{k=1}^{L}
\left(1-\frac{k}{L+1}\right)\gamma_k
\right]
\]

\[
v_{\mathrm{governed}}=\max(v_{\mathrm{iid}},v_{\mathrm{HAC}})
\]

\[
n_{\mathrm{eff}}=
\operatorname{clamp}\left(\frac{s^2}{v_{\mathrm{governed}}},1,n\right)
\]

For a constant trace, define variance as zero and ESS as \(n\). ESS is an audit descriptor only: **P2-037 must not use it as a Student-t sample size or degrees of freedom**. Its `n` and `df` remain semantic paired-block counts.

Freeze these eligibility rules:

- Powermetrics v1 only.
- At least two samples for arithmetic, but governed estimation requires `n >= 3 * (L + 1)`, giving at least three bandwidth spans.
- Cadence regularity requires `p95(interval)/p05(interval) <= 1.25`.
- Missing, corrupt, nonfinite, too-short, or irregular raw traces yield `not_estimable`; there is no fallback to raw \(s^2/n\).
- No outlier removal, detrending, adaptive lag selection, or estimator shopping.
- `math.fsum` is used throughout; stdlib-only D-009 is satisfied.

Newey–West is preferable to initial-sequence ESS here because it does not rely on the reversible-chain assumptions behind Geyer-style sequence estimators, and its cutoff is frozen in physical time rather than chosen from observed ACF sign changes.

## 2. Governed artifact and versioning

Keep this in `summary_metrics.json`; do not introduce a sibling artifact. The immutable raw idle trace is already the source artifact, and the reducer summary is the existing governed derivation and strict-reduction boundary.

Add this top-level object:

```json
"idle_mean_uncertainty": {
  "status": "estimated",
  "method": "newey_west_bartlett_10s_iid_floor_v1",
  "source_artifact": "raw/powermetrics_idle.plist",
  "source_sha256": "<64 lowercase hex>",
  "raw_sample_count": 300,
  "median_sample_interval_s": 0.1199250625,
  "cadence_p95_p05_ratio": 1.0581313969,
  "bandwidth_s": 10.0,
  "lag_count": 83,
  "sample_variance_w2": 0.379715,
  "iid_variance_of_mean_w2": 0.00126575,
  "hac_variance_of_mean_w2": 0.01147267,
  "governed_variance_of_mean_w2": 0.01147267,
  "effective_sample_size": 33.0982,
  "correlation_scope": "independent_run",
  "reason_codes": []
}
```

For non-estimable inputs, retain the same keys with numeric results and ESS set to `null`, plus one or more frozen reasons:

```text
raw_idle_trace_unavailable
raw_idle_trace_invalid
nonfinite_idle_power
insufficient_idle_samples
idle_trace_span_below_three_bandwidths
idle_cadence_irregular
idle_metadata_mismatch
backend_policy_not_frozen
```

The reducer must also rederive and compare the raw trace’s sample count, arithmetic mean, sample standard deviation, and duration against `metadata.idle_baseline`. A mismatch makes the governed variance unavailable and strict validation fail; metadata must not independently select the variance.

The existing term remains the consumer-facing scalar:

```json
"energy_variance_terms_j2": {
  "E_gross_repetition_j2": null,
  "E_idle_mean_j2": "<measured_duration_s^2 * governed_variance_of_mean_w2>"
}
```

Version ruling:

- `SUMMARY_SCHEMA_VERSION` remains `0.1`; this is additive and schema 0.2 remains reserved.
- `SUMMARY_REDUCER_VERSION` becomes **0.4.1**, not 0.5.0.
- This is not only an additive shape change: it changes the meaning and value of existing `E_idle_mean_j2`. Therefore current-era reducer 0.4.0 summaries must be rejected with “re-reduction required”; an absence-only `ADDED_SINCE_0_4_0` projection is insufficient.
- Frozen legacy summaries may keep their existing identity-based additive-absence handling, because all six retained legacy bundles preserve the raw idle artifacts needed for fresh correction.
- Reducer 0.5.0 would be disproportionate: no field is removed or renamed, unlike the 0.4.0 evidence-surface migration. D-030 specifically requires at least a patch bump for a governed output addition [and forbids reusing a frozen reducer version](/Users/edr/code/JouleWise-wt/p2041-vetted/docs/decision_log.md:1583).

`aggregate.py` should continue consuming each member’s corrected `E_idle_mean_j2`. Its existing member-average term remains observation-scale aggregate diagnostics; P2-037 must consume individual bundle terms, not the aggregate’s averaged term.

## 3. P2-037 propagation interface

The in-flight P2-037 estimator layer does not need redesign. Its current `StochasticVarianceTerm` already accepts exactly the required per-side variances and `independent_run` scope.

For an idle-subtracted request bundle, input assembly should:

1. Require reducer `0.4.1`.
2. Require `idle_mean_uncertainty.status == "estimated"`.
3. Require the exact method ID and `correlation_scope == "independent_run"`.
4. Read the nonnegative finite scalar from `energy_variance_terms_j2.E_idle_mean_j2`.
5. Optionally cross-check it against `measured_duration_s² × governed_variance_of_mean_w2`.
6. Construct:

```python
StochasticVarianceTerm(
    name="E_idle_mean_j2",
    variance_a=term_a,
    variance_b=term_b,
    covariance_ab=None,
    correlation_scope="independent_run",
)
```

Then the already-settled P2-037 calculation applies:

\[
v_i=v_{Ai}+v_{Bi}
\qquad
SE_{\mathrm{metrology}}^2=\frac{\sum_i v_i}{n_{\mathrm{blocks}}^2}
\]

This matches [analysis-engine B5](/Users/edr/code/JouleWise-wt/p2041-vetted/docs/specs/c027/analysis_engine_trio.md:693).

Interface boundaries:

- Gross request and gross phase estimators do not consume this term.
- `mean_of_request_ratios` divides each energy variance by the exact runtime token count squared.
- `ratio_of_totals` contributes `sum(v_Ei)/(sum(T_i)^2)` on each side.
- Missing or mismatched governed evidence yields `required_error_term_unknown`.
- `required_covariance_unknown` is reserved for a present variance whose correlation scope is missing or unacceptable.
- P2-037 never parses raw idle files and never recomputes ESS.
- The current explicit placeholder refusing the naïve term can be replaced locally in [inputs.py](/Users/edr/code/JouleWise-wt/p2037/joulewise/analysis_engine/inputs.py:650), without changing estimator APIs or the verdict artifact.

The `independent_run` label applies only to the residual within-capture stochastic term. Slow cross-run change remains the separately propagated deterministic drift bound under D-057.

## 4. Predeclaration freeze

Before any Window-A/P2-015 calibration effects are inspected, freeze:

- Exact method ID and formulas, including autocovariance denominator.
- Powermetrics 10 s bandwidth.
- Median-interval lag conversion.
- IID variance floor and ESS clamps.
- Minimum three-bandwidth trace rule.
- Cadence regularity threshold of 1.25.
- Rail definition: the same CPU+GPU+ANE arithmetic total used by the idle baseline.
- Arithmetic, not time-weighted, mean so the uncertainty matches the current point estimand.
- No trimming, detrending, stationarity “repair,” or adaptive bandwidth.
- Raw/metadata cross-check tolerance and failure behavior.
- Physical-backend applicability.
- `independent_run` covariance scope and the separation from deterministic drift.
- Reducer 0.4.1 and exact P2-037 required-method gate.
- The hand fixtures below.

Freeze these in a D-030 amendment plus the run-bundle and detection-floor contracts. The implementation/tests should land before calibration bundles are generated. A later method change must produce a new method ID and reducer version; historical outputs are never silently recomputed under a changed policy.

## 5. Hand-computable fixtures

### Closed-form IID-floor fixture

Samples `[0, 2, 0, 2]`, with kernel `L=3`:

- Mean = 1.
- \(s^2=4/3\).
- \(v_{\mathrm{iid}}=1/3\).
- Autocovariances: \(1,-3/4,1/2,-1/4\).
- Bartlett HAC variance-of-mean = \(1/16\).
- Governed variance = \(1/3\).
- ESS = 4.

This pins the “never claim ESS greater than raw n” floor.

### Highly correlated fixture

Samples `[0, 0, 0, 2, 2, 2]`, intervals 5 s, `H=10 s`, hence `L=2`:

- Mean = 1.
- \(s^2=6/5\).
- \(v_{\mathrm{iid}}=1/5\).
- \(\gamma_0=1,\gamma_1=1/2,\gamma_2=0\).
- HAC long-run variance = \(5/3\).
- Governed variance-of-mean = \(5/18\).
- ESS = \((6/5)/(5/18)=108/25=4.32\), not raw 6.
- With measured duration 3 s, `E_idle_mean_j2 = 9 × 5/18 = 5/2 J²`.

### Degenerate fixture

`[5, 5, 5, 5]`:

- All variance terms zero.
- ESS = 4.
- No division-by-zero or `NaN`.

### Eligibility fixture

A regular trace spanning less than three bandwidths:

- `status = not_estimable`.
- `E_idle_mean_j2 = null`.
- ESS = `null`.
- P2-037 returns `required_error_term_unknown`.
- It must not fall back to raw adjacent count.

### P2-037 propagation fixture

Two paired blocks; every A and B bundle carries `E_idle_mean_j2 = 5/2`:

- Each paired metrology variance = 5.
- Sum across two blocks = 10.
- \(SE_{\mathrm{metrology}}^2=10/2^2=5/2\).
- \(SE_{\mathrm{metrology}}=\sqrt{5/2}\).
- With paired differences `[1,1]`, `SE_repeat=0`, so `SE_total=sqrt(5/2)`.
- For ten exact output tokens per request, each mean-of-ratios variance becomes `(5/2)/100 = 1/40 (J/token)²`.

## 6. Lead/Ed rulings required

1. **Covariance policy:** ratify `independent_run` for the HAC residual after deterministic drift separation. Rejecting this requires a B5 amendment—probably a conservative unknown-covariance upper bound—and would materially change P2-037.

2. **Bandwidth freeze:** approve 10 s for powermetrics. The retained traces support it, but it becomes methodology, not an implementation tuning constant.

3. **Backend scope:** close P2-044 for powermetrics only. NVIDIA/other physical backends should emit `backend_policy_not_frozen` until a retained backend-specific idle trace supports its cadence and bandwidth. Mock remains non-physical and need not produce claim-bearing ESS.

4. **Legacy disposition:** re-reduce the six retained bundles under 0.4.1 for analysis use; retain their original summaries as historical evidence. Do not present their current stored summaries as corrected variance evidence.

5. **Cadence handling:** ratify fail-closed irregular-cadence behavior for v1. Resampling/interpolation would introduce another estimand and should not be improvised inside P2-044.

No files were changed. Verification consisted of direct stdlib parsing and calculation over all six named retained raw idle traces; no quiet-machine measurement or live hardware action was performed.