```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt an exact set-membership affine-rate anchor, not statistical regression; preserve all fail-closed gates and partition the nine-bundle set because one member must remain refused by the 5 ms span rule.",
  "workspace": {
    "base_requested": "/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN",
    "base_mode": "exact",
    "head_start": "311d80167b87e21af9b3cfd4addabe2af78e78a6",
    "head_end": "311d80167b87e21af9b3cfd4addabe2af78e78a6",
    "upstream_end": "fdcfe15d631750914c40615560e4b0cb7f09d3d9",
    "branch": "integration/phase2-transaction"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "adopt_with_validation_partition_ruling",
    "method_identity": {
      "evidence_schema": "p2-038.3",
      "anchor_method": "powermetrics_native_second_rate_aware_set_membership_v1",
      "rederivation_schema": "joulewise.clock_anchor_rederivation.v1",
      "acceptance_generation": "new D-079 generation, recommended d079_calibration_acceptance_v3_n19_r1; never re-key r2 in place"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The nine-bundle all-resolve requirement conflicts with the retained 5 ms refusal",
        "detail": "The diagnosis inventories four archive native_intersection_empty members, one raw-bearing wall_minus_monotonic_span_exceeded member, and four current native_intersection_empty members. Only eight are rate-quantization resolution candidates; the ninth must remain a negative control unless the 5 ms rule is explicitly overturned."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Residual-based regression cannot support a containment claim",
        "detail": "OLS, Huber, Theil-Sen, residual standard errors, and confidence intervals may understate the anchor. The authoritative estimator should project an exact feasible set of affine rates, quantized native intervals, and causal ClockStamp constraints."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The method change is a full D-138 reissue event",
        "detail": "All four governed estimator inputs should change or be reviewed as changed. New bounds are science-facing, so the D-138 pure-pin PROCEED shortcut is inapplicable; a new acceptance generation, cold review, and atomic dependent-pin re-freeze are required."
      }
    ],
    "d_items": [
      {
        "id": "D1",
        "ruling": "Fit one affine wall-versus-monotonic relation per capture as a deterministic feasible set, not as a point regression.",
        "spec": "Let q_0=0 and q_i=sum(elapsed_ns[1..i])/1e9 exactly; N_i is the exact whole-second native endpoint label. Variables are first endpoint A, centered intercept alpha, and rate beta. Every record contributes N_i <= A + beta*q_i <= N_i+1, conservatively closing the native upper endpoint. Every ClockStamp contributes its wall-resolution and bracketed-monotonic rectangle. Causal pre_spawn/first_parse inequalities are included in the same feasible polytope. The authoritative anchor interval [A_lo,A_hi] is the exact projection of that polytope; midpoint is diagnostic only."
      },
      {
        "id": "D2",
        "ruling": "Use exact rational/decimal interval arithmetic with outward binary64 projection.",
        "spec": "Preserve elapsed_ns as integers; represent stored binary64 ClockStamp values through as_integer_ratio or Decimal.from_float; solve linear extrema without float regression. Round A_lo downward and A_hi upward. Record beta_lo, beta_hi, anchor interval, and arithmetic padding."
      },
      {
        "id": "D3",
        "ruling": "Use a fixed model-departure gate rather than an observed-residual-derived uncertainty.",
        "spec": "Set MAX_AFFINE_CLOCK_RESIDUAL_S=0.000250 provisionally. Compute the minimum L-infinity residual r_star for diagnostics, refuse if r_star exceeds 250 us, and construct the authoritative feasible set using the full 250 us allowance. Allow relative endpoint departure up to 2*250 us in native transport. Do not shrink uncertainty to r_star."
      },
      {
        "id": "D4",
        "ruling": "Carry rate uncertainty through the interval before computing the scalar bound.",
        "spec": "Project beta to [beta_lo,beta_hi]. Equivalently, with beta_mid and delta_beta=max(beta_mid-beta_lo,beta_hi-beta_mid), record i contributes [N_i-beta_mid*q_i-delta_beta*q_i, N_i+1-beta_mid*q_i+delta_beta*q_i]. Intersect jointly, not record-by-record with independently selected rates. Let H=(A_hi-A_lo)/2. effective_clock_anchor_bound_s=outward_up(H + wall_minus_monotonic_span_s + max_stamp_resolution_s + numeric_padding_s). The existing detector composition remains b_fiducial=max_edge_fit_bound+effective_clock_anchor_bound_s."
      },
      {
        "id": "D5",
        "ruling": "Retain and strengthen refusal gates.",
        "spec": "Keep wall_minus_monotonic_span_exceeded at >5 ms. Add affine_clock_fit_empty, affine_clock_residual_exceeded, clock_rate_limit_exceeded, clock_fit_span_insufficient, native_rollover_anomalous, rate_aware_native_set_empty, admissible_interval_empty, and effective_clock_anchor_bound_exceeded. Recommend an independent 5 ms ceiling on the resulting effective anchor bound as well as the existing 5 ms offset-span gate."
      },
      {
        "id": "D6",
        "ruling": "Prospective evidence and rederivations receive fresh identities.",
        "spec": "Never alter manifest.json, instrument_evidence.json, ledger receipts, or previously issued acceptance bytes. A rederivation record binds source content ID and SHA-256 values for raw, events, manifest, and original evidence; original method/status/digest; new method/schema and all four estimator digests; derived interval/bound/refusal; network-time provenance; role validation_only or prospective; and its own canonical digest."
      }
    ],
    "i_items": [
      {
        "id": "I1",
        "bar": "Exact arithmetic unit tests prove outward containment at every conversion and reject NaN, infinity, nonintegral native labels, nonpositive elapsed_ns, and unordered ClockStamps."
      },
      {
        "id": "I2",
        "bar": "Require at least five named ClockStamps, at least two native rollovers, a rate-fit baseline >=60 s, and controller-stamp coverage spanning the raw q range. A fit touching a configured rate boundary refuses rather than being clipped."
      },
      {
        "id": "I3",
        "bar": "Use a provisional physical rate domain of 1 +/- 50 ppm. The unconstrained feasible beta projection must lie wholly inside it; partial overlap is a refusal. Recalibration of 50 ppm or 250 us requires a new ruled method identity."
      },
      {
        "id": "I4",
        "bar": "Prospective claim-bearing captures require authenticated network-time-OFF admission. ON or unknown cannot be normalized away by the affine fit; historical unknown-state material may be used only for validation diagnostics."
      },
      {
        "id": "I5",
        "bar": "No rollover deletion, phase unwrapping repair, trimming, winsorization, or best-subset fit. Every complete native record participates."
      }
    ],
    "r_items": [
      {
        "id": "R1",
        "bar": "Hash-freeze the nine-bundle validation inventory. Eight native_intersection_empty members must become bounded with approximately 1-2 ms native/rate contribution plus existing span/resolution terms. The wall_minus_monotonic_span_exceeded member must remain refused; the missing-raw archive member is not in the executable set."
      },
      {
        "id": "R2",
        "bar": "On all 34 currently resolvable corpus members, require zero new refusals; point shift <=1 ms; and effective bound delta within +/-0.25 ms. Any loosening >0.25 ms or any tighter interval that fails to contain the old admissible point triggers explicit methodology review rather than automatic acceptance."
      },
      {
        "id": "R3",
        "bar": "Kill tests independently exercise >5 ms offset span, >250 us affine residual, empty rate set, rate outside +/-50 ppm, insufficient span, native backward step, impossible forward rollover, zero rollovers, causal-set empty, first-parse lag >0.25 s, and effective bound >5 ms."
      },
      {
        "id": "R4",
        "bar": "Mutation tests prove that deleting one record, using midpoint native timestamps, deriving uncertainty from observed residuals, rounding inward, or clipping beta changes a passing test to failure."
      },
      {
        "id": "R5",
        "bar": "Historical rederivation leaves every source byte unchanged and emits fresh validation-only records. Claim consumers reject old-method/new-method substitution and reject copied rederivation fields without authenticated source hashes."
      },
      {
        "id": "R6",
        "bar": "D-138 stale-pin tests must fail after the estimator diff and pass only after the new D-079 issuance and complete successor-family re-freeze."
      }
    ],
    "d138_fanout": {
      "governed_estimator_files": [
        "joulewise/uncertainty_evidence.py",
        "joulewise/powermetrics_fiducial.py",
        "joulewise/adapters/powermetrics.py",
        "joulewise/reduce.py"
      ],
      "reason": "core feasible-set derivation; raw-backed dispatch and stored-record authentication; preservation of exact elapsed/native inputs; reducer method dispatch and independent raw anchor reconstruction",
      "reissue": "new D-079 acceptance generation plus calibration registry/default, three successor pack trees and acceptance-owner pins, two floor-mint extraction specs, T1 anchor_method_version projections, and exact/stale-pin regressions inside one atomic re-freeze"
    },
    "explicit_disagreements": [
      "I disagree with fitting native-second midpoints by ordinary or robust regression: it produces an estimate, not a containment set.",
      "I disagree that all nine raw-bearing failures may resolve while wall_minus_monotonic_span_exceeded remains binding. The executable acceptance partition is eight positive resolutions plus one preserved negative refusal.",
      "I disagree with treating this as a pure code-digest reissue. Changed anchor and b_fiducial values are science-facing and require a new acceptance generation."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "sed -n '1,260p' /private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/sol-anchor-diagnosis.md && nl -ba joulewise/uncertainty_evidence.py | sed -n '286,445p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "derive_powermetrics_anchor_v2 begins at line 292",
          "native intersection is lines 376-389; 5 ms span refusal is lines 366-374; bound composition is lines 413-438"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bound composition"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "sed -n '9894,10020p' docs/decision_log.md && sed -n '1070,1260p' joulewise/powermetrics_fiducial.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "D-138 pins four estimator files and forbids fixture re-keying",
          "raw-backed rederivation currently dispatches derive_powermetrics_anchor_v2"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rederivation"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## integration/phase2-transaction...origin/main [behind 2]",
          "no modified paths"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "behind 2"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The nine-bundle all-resolve bar contradicts the mandatory 5 ms wall-minus-monotonic refusal.",
      "needs": "Adopt the recommended eight-positive/one-negative partition, or explicitly overturn the 5 ms rule."
    },
    {
      "id": "FLAG2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The proposed 250 us residual and +/-50 ppm rate limits are prospective calibration constants, not facts yet established on the corpus.",
      "needs": "Freeze them before replay, publish all observed margins, and do not widen them after seeing failures without a new method identity."
    },
    {
      "id": "FLAG3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The inspected transaction head is two commits behind origin/main; all cited code anchors resolve at the requested head.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Validation-set contradiction

The diagnosis and code anchors check out. The current resolver fixes rate at exactly 1, intersects `[N_i-q_i, N_i+1-q_i]`, and refuses an empty result. But the diagnosed archive set is four `native_intersection_empty`, one raw-bearing `wall_minus_monotonic_span_exceeded`, and one missing-raw member. With today’s four native failures, the executable rate-aware set contains eight positive candidates and one mandatory negative control.

Resolving the span-exceeded member would silently repeal the very gate the request says to preserve. My recommendation is therefore R1’s eight-pass/one-refuse partition.

### F2 — Estimator ruling

The right successor is set-membership estimation, not regression in the statistical sense.

For raw record \(i\):

\[
q_0=0,\qquad
q_i=\sum_{k=1}^{i}\frac{\mathrm{elapsed\_ns}_k}{10^9}
\]

and its quantized label supplies:

\[
N_i \le A+\beta q_i \le N_i+1.
\]

Here \(A\) is the first record’s endpoint and \(\beta\) is wall seconds per monotonic second. All records remain active; no rollover is discarded.

The five ClockStamps constrain a centered affine relation

\[
W(m)=\alpha+\beta(m-m_0)
\]

through their wall-resolution and bracketed-monotonic rectangles. The causal pre-spawn/first-parse constraints belong in this same polytope. Exact minimization and maximization of \(A\) produce \([A_{\min},A_{\max}]\). There is no probability statement.

The fixed 250 µs departure allowance is deliberately used in full, even when observed residuals are smaller. This prevents an unusually tidy capture from manufacturing a smaller uncertainty. If the smallest feasible residual exceeds 250 µs, the capture refuses.

The scalar containment bound is:

\[
B_{\text{anchor}}
=\operatorname{up}\left(
\frac{A_{\max}-A_{\min}}{2}
+S_{\text{wall-mono}}
+R_{\text{stamp}}
+R_{\text{numeric}}
\right).
\]

Rate uncertainty is already inside the projected anchor interval; it must not be replaced by a slope standard error. The existing `b_fiducial` addition remains unchanged.

### F3 — Identity and reissue

All four D-138 files participate:

- `uncertainty_evidence.py`: feasible-set math and refusal details.
- `adapters/powermetrics.py`: retain integer `elapsed_ns` and exact native seconds instead of prematurely projecting both to floats.
- `powermetrics_fiducial.py`: method-aware raw rederivation and stored-record authentication.
- `reduce.py`: new-method dispatch and independent raw reconstruction.

Because rederived anchor and `b_fiducial` values can change, this is not D-138’s “only code pins differ” case. It requires a new acceptance generation and cold science review, followed by the complete atomic successor-family re-freeze.

Historical outputs should be sibling derivation records, never patched evidence. The archive/current validation artifacts remain `validation_only`; they do not retroactively make original invalid evidence claim-bearing.

## Residual risk

Even exact feasible-set arithmetic depends on the affine-with-bounded-departure model. A nearly linear network-time slew below both the 5 ms span limit and the residual threshold can look like oscillator rate. Prospective network-time-OFF provenance is therefore essential; the fit must not be treated as a substitute for that environmental control.