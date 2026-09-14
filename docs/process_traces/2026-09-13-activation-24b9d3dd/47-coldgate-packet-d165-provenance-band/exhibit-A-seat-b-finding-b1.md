# Exhibit A — seat B inventory report 02b (activation 96bfeca7), the B1 section verbatim (lines 322–400) and the inventory rows I23/I26

```
### B1 — D-165 zero-point identity band: proposed, requires ruling

**Priority:** the only demonstrated re-set candidate in this seat. **Low established likelihood of refusing a real G2-a number:** the demonstrated operands are approximately 20,000 J each. No live or fixture-level G2-a reproduction was run.

**Current guard:** `dominance_closeout.py:963` compares:

```python
math.isclose(zero_point, delta, rel_tol=1e-9, abs_tol=1e-12)
```

These are the same intended estimand but **different arithmetic paths**:

- Stored delta uses `(B1+B2−A1−A2)/2`, `detection_floor.py:1449`.
- Zero-shift replay uses weighted `math.fsum` of re-integrated member energies, `floor_extraction.py:2534`.
- D-124 already acknowledges real nonzero divergence and charges `abs(zero_point−delta)` into the shared bound. Its provenance guard is expressly **not load-bearing for soundness**: `docs/decision_log.md:8114–8138`.

**Demonstrated counterexample, sanity arithmetic only**

```text
A1=20000.1, B1=20000.3, B2=20000.0, A2=20000.2 J
sequential delta = 1.8189894035458565e-12 J
weighted fsum   = 0.0 J
current guard   = refuses
```

These binary64 operands are identical on both sides; the discrepancy is arithmetic, not telemetry noise.

**Proposed value**

Preserve the existing tolerance and add a member-scale arithmetic allowance:

```text
τ_new = max(
    1e-12 J,
    1e-9 × max(|zero_point|, |delta|),
    64u × S
)
u = 2^-53
S = max(1 J, member_envelope_integral_sum_j, |delta|, |zero_point|,
        every absolute onset/offset sweep value)
```

This uses the **existing D-124 member-integrand scale and `64u` allowance**, rather than inventing a measurement tolerance from 1 J. At the counterexample scale, the pad is `2.842192259322474e-10 J`: approximately `2.84e-10` of 1 J and `5.68e-11` of 5 J.

The proposed band must remain coupled to the existing **once-only outward charge of `|zero_point−delta|`**. Do not delete that term.

**Diff-shaped proposal; not applied**

```diff
--- a/joulewise/dominance_closeout.py
+++ b/joulewise/dominance_closeout.py
@@
-        if not math.isclose(zero_point, delta, rel_tol=1e-9, abs_tol=1e-12):
+        provenance_scale_j = max(
+            1.0,
+            float(block["member_envelope_integral_sum_j"]),
+            abs(delta),
+            abs(zero_point),
+            *(abs(value) for value in onset),
+            *(abs(value) for value in offset),
+        )
+        provenance_abs_tol_j = max(
+            1e-12,
+            64.0 * (math.ulp(1.0) / 2.0) * provenance_scale_j,
+        )
+        if not math.isclose(
+            zero_point, delta,
+            rel_tol=1e-9, abs_tol=provenance_abs_tol_j,
+        ):
             raise ValueError(_COMMON_MODE_ZERO_POINT_DIVERGENCE)
```

This does **not** complete the repair alone. Seat A owns the upstream duplicate at `floor_extraction.py:590`; leaving it unchanged would refuse the candidate before the D-165 replay consumer is reached. Prefer one shared predicate after lead approval.

**Defect-shaped regression**

1. Construct a block from the four stated member energies using the actual registered delta and zero-shift builder paths. Add another ordinary valid block so the point-floor denominator is nonzero. Supply valid windows, authenticated shared bound and complete sweeps.
2. **Admit counterfactual:** same member energies, differing only because of the two legitimate arithmetic paths. Assert old predicate refuses; proposed predicate admits; `|z−delta|` remains included in the shared width.
3. **Refuse counterfactual:** change the block delta by **1e-6 J**, leaving the authentic zero point and member-scale envelope unchanged. Assert the proposed provenance predicate still refuses. This is over three orders of magnitude beyond the illustrated new pad.

| I23 | dominance_closeout.py:963 | Zero-shift replay versus stored ABBA delta | τ(1e-9,1e-12) J | Arithmetic provenance | identity | J(τ) | **needs_ruling** | Different arithmetic paths; demonstrated false refusal at large member scale. B1 proposes re-set. |
| I26 | dominance_closeout.py:1109,1148,1357,2278 | Stored result/split versus fresh canonical result | Exact mappings | D-165 result replay | identity | J(0) for energy fields | keep | Calls the same production arithmetic; rejects stale or substituted results. |
```
