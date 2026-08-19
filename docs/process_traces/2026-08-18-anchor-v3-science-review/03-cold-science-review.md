# COLD SCIENCE REVIEW — rate-aware set-membership clock anchor (v3) and the calibration corpus consequences

*Cold Fable instance, no loop context, 2026-08-18 afternoon. Reviewed
read-only at fa7917b. All load-bearing anchors independently verified;
the estimator independently re-implemented (convex piecewise-linear
minimization over the rate in exact rational arithmetic, no shared code
with the production LP) and found to reproduce the published intervals at
1-ulp tightness. Verbatim rulings below; this file is the ONE home.*

## Q1 — Method soundness: SOUND. Ratified, with documentation conditions.

Independent verification on bundle 20260818T173136-bc9bff8e: rate window
[+7.2430695284, +7.2854172553] ppm and anchor interval reproduced to all
printed digits; composed bound 0.0019011137 s exact.

(a) Constant-rate absorption is CORRECT behavior (the disciplined
shakedown capture itself runs at +7.24 ppm — v2's rate=1 pin was the
falsified model). Sustained slew cannot understate the bound (drift
charged in full via the span term; gates refuse ≥~25 ppm sustained; the
±50 ppm projection REFUSES rather than clips — clipping is killed by
tests/test_uncertainty_evidence.py:642). Mid-capture rate changes refuse
at small magnitude (long-baseline stamp pairs constrain the rate to
~0.05 ppm width). The one genuine evasion window — a non-affine wall
excursion ≤~250 µs between stamps — is bounded by the residual gate
(~1% of typical b_fiducial) and structurally excluded by the
network-time-OFF admission. CONDITION: the method identity must state
containment is conditional on the model (affine wall + ≤250 µs native
departure) with network-time-OFF admission as the justification.

(b) The "double-charge" framing is WRONG in a dangerous direction: H
covers anchor placement; the span term covers within-capture wall-vs-
elapsed drift, load-bearing because detect_pulses maps the trace at
rate 1 from the anchor midpoint (powermetrics_fiducial.py:1249-1260,
composition :1043) while pulse commands carry wall-epoch stamps. Remove
either term and containment breaks. The only true overlap is the 250 µs
allowance widening H while real departures also inflate the span — a
priced ≤~0.5 ms conservatism. RULING: honest conservatism; RETIRE the
"double-charge" language. CONDITION: document that dropping the span term
is lawful only together with re-mapping the trace under the fitted rate
window, under a new method identity.

(c) The float64 span representation error (~0.24 µs ulp at epoch scale;
Fraction() exactifies an inexact value at uncertainty_evidence.py:1091;
NUMERIC_PADDING_S=1e-9 does not cover it) is the single inward-leaning
gap in an otherwise outward-exact chain. The "500× below the allowance"
comparator is the wrong term (the allowance lives in the native rows);
the honest comparator is the multi-ms bound, against which 0.5 µs is
immaterial. RULING: deferral RATIFIED for the validation artifact; it
must NOT survive into the frozen successor unpriced (raise
NUMERIC_PADDING_S to ≥1e-6 or add an explicit representation term at
issuance — the corpus regenerates anyway).

## Q2 — The two corpus refusals: CORRECT SCIENCE, not a method artifact.

Both members examined from manifest-authenticated raw bytes with the
reviewer's own machinery (sanity-checked against two surviving same-era
members, feasible with −875/−303 µs margin):

- 20260722T222332-901c5c13: stamp rectangles alone infeasible under any
  single rate — early pairs constrain the rate to [−1.1, +5.2] ppm,
  long-baseline pairs to [−16.04, −15.99] ppm (disjoint by ≥15 ppm);
  wall-minus-monotonic moved −3.18 ms mid-capture; minimal feasibility
  inflation independently computed = 5.612 µs (exact match to the
  implementation's figure).
- 20260723T183306-4ce692b4: early ≈ −9.2 ppm vs late ≈ −2.27 ppm;
  minimal inflation 1.873 µs (exact match).

41 of 43 bundles need exactly zero slack — the model fits normal captures
at sub-µs consistency. Custody corroborates the pre-discipline claim: the
earliest clock-pin record (pin-20260727T051946Z.txt, time.apple.com)
postdates both members. Active steering undermines the between-stamp
assumption for ANY method including v2 — which had accepted 901c5c13 as
the corpus MAXIMUM (4.53 ms anchor / 33.559 ms b_fiducial). The refusals
remove the corpus's most contaminated member; the max drops to 32.897 ms
(member 1acdbbc0) and screens TIGHTEN. Refusals stand; successor corpus
n=17 is correct. Pre-discipline survivors remain sound for containment
(steady slew is a genuine wall rate whose drift the span term charges).

## Q3 — Corpus deltas: honest correction; exclusions EXPECTED; successor regeneration is the right path.

v2's rate=1 assumption is measurably false by several ppm; its knife-edge
intersections placed midpoints with a rate-drift bias of order drift/2.
Removing a bias SHOULD produce new intervals excluding the old biased
points — 11/32 exclusions are the correction working. Mean B_anchor
+0.311 ms against 25-35 ms b_fiducial values is small; the corpus
survives 32/34 with the max DECREASING. The consult's R2 tolerance
exceedance was correctly routed here; THIS REVIEW CONSTITUTES THE
MANDATED METHODOLOGY REVIEW — record that adjudication in the acceptance
generation. One incomplete explanation to fix in the record: the
+4.72 ms b_fiducial outlier (20260818T045736) is NOT explained by the
anchor shift alone (+0.32 ms); the remainder is detector-refit
sensitivity under the shifted anchor (accepted regions jumping sample
quanta) — fail-closed and widening, not a blocker, but the acceptance
record needs the one-line mechanism note.

## Conditions attached to the successor acceptance generation

1. Detector-budget re-sweep under v3 BEFORE the freeze (validation bundle
   a7e8b412 went nonconvergent at exactly 165,000 cells under v3; 165k
   was swept under v2 anchors).
2. Price the float64 representation error at issuance (one constant), or
   a signed quantitative deferral in the acceptance record.
3. Document the span-term dependency in the method identity; retire the
   "double-charge" framing.
4. State the model condition; keep per-member network-time provenance
   fields in successor records (the validation artifact's
   unknown_in_artifact handling is the template).
5. Preserve the negative control permanently (b10cb348, span 6.40 ms,
   verified still refusing under v3); record the missing-raw archive
   member's permanent quarantine.
6. Atomic fan-out: everything derived from the old corpus max 33.559 ms
   (screens, budget constants, pack pins, T1 projections) re-derives
   inside the ONE atomic re-freeze (consult F3 / D-138); no partial
   adoption.
7. Publish the residual-margin distribution
   (min_l_infinity_residual_upper_bound_s across the corpus) in the
   acceptance record; the 250 µs / ±50 ppm constants stay frozen and may
   not widen after observed failures without a new method identity.

## Record corrections (overclaim/missing)

- "Double-charge" characterization: wrong, fix the words (Q1b).
- +4.72 ms outlier mechanism: incomplete, add the note (Q3).
- "500×-below-allowance" comparator: wrong term, right conclusion (Q1c).
- The ~11/~7 ppm cluster figures understate 901c5c13 (≥15 ppm by stamp
  pairs) — harmless.
- Everything else checked — quoted slacks, delta statistics, n=19→17
  accounting, corpus-max drop, 8/8+1 validation partition, code-head and
  digest bindings, no-bytes-altered — verified against primary evidence.
