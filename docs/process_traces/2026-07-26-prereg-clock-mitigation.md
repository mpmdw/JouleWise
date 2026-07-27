# Pre-registration — clock-pin mitigation and window B/C failures (2026-07-26)

**Written BEFORE tonight's collection.** Its purpose is to fix the inference
rules in advance, so that tomorrow's session cannot read a lucky outcome as
causal confirmation. Nothing here changes a gate, a policy constant, or an
admission rule.

Author: lead (Opus 5, 1M context, effort high). Prompted by an adversarial
review that identified two live self-deception risks: compressing the window B
and window C failures into one causal story before the decisive check is run,
and letting tonight's window B outcome adjudicate that story.

---

## 1. The two failures

| | Window B | Window C |
|---|---|---|
| Members | 59/59 collected, zero failures | died at member 7/40, then at the bound mint |
| Failure | whole-window verdict `failed`, `instrument_calibration_mismatch` | per-member `clock_anchor_unresolved` |
| Number | pre fiducial 35.44 ms, post 23.85 ms, drift **11.58 ms** vs a 10.00 ms limit (16% over) | wall−monotonic spans **5.544 ms** and **7.769 ms** vs a 5.00 ms ceiling |
| Detectable | only at post-calibration, ~3h25 in | per-member, aborts in ~40 min |

Window C's diagnosis is **independently established**: directly observed slew
at rates (~+110 / −158 ppm) consistent with a clock adjuster, self-clearing
(the next member anchored at 0.305 ms). It does not depend on anything below.

## 2. Competing hypotheses for window B

- **H1 — common cause.** B's bracket drift and C's anchor failures share one
  mechanism: a wall clock adjusted underneath the measurement. Requires that an
  adjustment episode overlapped a *calibration* window while missing all 59
  members. **Prediction:** (wall − monotonic) drifts ≈11.6 ms end-to-end across
  B's 3.2 h (≈1 ppm secular), and/or a step or ramp overlaps a calibration.
- **H2 — separate causes.** B's fiducial drift lives in a non-wall-clock term of
  the fiducial (powermetrics anchor latency, thermal, overnight quiescence).
  **Prediction:** (wall − monotonic) is flat to ±1–2 ms across B while the
  fiducial still moved 35.44 → 23.85 ms. **Consequence: pinning the clock fixes
  C and does nothing for B.**
- **H3 — marginal noisy metric.** Bracket drift typically runs near the 10 ms
  limit anyway, and/or a single fiducial is repeatable only to ±3–4 ms, so
  11.58 ms is an ordinary draw. **Prediction:** prior *passing* windows show
  drifts of ~6–9 ms. **Consequence: B failed to bad luck; a re-run may pass for
  reasons unconnected to any fix, and the mitigation would take false credit.**

H1 was the lead's working story. H2 and H3 were raised in review; H3 had not
been considered at all.

## 3. What tonight CANNOT establish

**A window B pass tonight is WEAK evidence for H1.** B missed by 16% on a metric
whose noise floor is uncharacterized. Under H3 it may pass on redraw alone, and
under H2 it may pass for unrelated environmental reasons. Tonight's verdict is
therefore **not** admissible as confirmation that the clock mitigation fixed
window B, and must not be recorded as such.

**A green 5 ms anchor result tonight is not evidence of a quiet clock.** With
network time disabled, the wall and monotonic clocks derive from the same
oscillator, so the wall−monotonic predicate passes *by construction*. The gate
measures nothing while the clock is pinned. This is the intended effect of the
mitigation, not a side effect, and it must be stamped into the window's
provenance so no future reader treats those passes as an independent check.

**Regime change.** Windows a9 and a10 were collected WITH network time running.
Tonight's windows run in a different environmental regime. That difference is
protocol-relevant provenance and gets recorded, not smoothed over.

## 4. What DOES adjudicate H1 vs H2 vs H3

Desk checks on data already on disk, run BEFORE collection:

1. **Endpoint regression of (wall − monotonic)** across window B's members and
   both calibration bundles. Discriminates H1 from H2 per the predictions above.
   Note that per-member max-minus-min *spans* do NOT discriminate — corrective
   slew is approximately zero-sum, so spans cannot be integrated into bracket
   drift in either direction. The lead computed spans first; that check was
   uninformative and is recorded here as such.
2. **Fiducial composition.** If `b_fiducial_s` is composed purely of
   monotonic-clock terms, wall-clock slew cannot affect it and **H1 is dead on
   arrival** regardless of any other evidence.
3. **Historical bracket-drift distribution** across prior passing windows, plus
   shot-to-shot fiducial repeatability. Discriminates H3.

## 5. Decision rules, fixed in advance

- Window **C runs first** regardless of outcome above. Its mechanism is
  established, and its per-member gate shakes down the mitigation ~40 min in
  rather than 3h25 in.
- If check 2 shows the fiducial is monotonic-only, **or** check 1 shows
  (wall − monotonic) flat: **do not collect window B tonight.** Run window D.
  B returns to the bench for a real diagnosis.
- If check 3 shows passing windows routinely drift 6–9 ms: B's failure is
  probably H3. Re-running B is then a coin flip, not a fix, and D is the better
  use of the slot. Record that the drift metric's precision is unfit for the
  limit it enforces, and route that to Ed as a policy question — **not** by
  loosening the constant, which is forbidden.
- If checks 1–3 support H1: run C then B, and record that B's pass (if it comes)
  is *consistent with* H1 rather than confirmation of it. Confirmation comes
  from the endpoint regression on existing data, not from tonight's verdict.
- **Two consecutive same-signature member failures → stop the night**, write the
  handoff, fall back to desk work. No third attempt on the same signature.

## 5a. OUTCOME (appended after the checks ran, before collection)

**H1 KILLED. H3 KILLED. H2 CONFIRMED.** Window B and window C do not share a cause.

Fiducial decomposition (`joulewise/powermetrics_fiducial.py:884`,
`b = max pulse-edge residual + effective trace-anchor bound`):

| term | pre | post | Δ | share |
|---|---:|---:|---:|---:|
| pulse-edge onset residual | 33.2366 ms | 22.4335 ms | +10.8031 | **93.28%** |
| effective anchor bound | 2.1992 | 1.4209 | +0.7783 | 6.72% |
| wall-minus-monotonic term | 0.8469 | 1.0483 | **−0.2015** | opposite sign |

Large wall-clock adjustments DID occur inside window B (interval rates −160.69,
−109.63, +100.09 ppm; max step 40.09 ms; max rate 244.98 ppm) — but **neither
overlapped a calibration**. Pre-calibration: +0.844 ms over 197.97 s, +4.26 ppm,
no step > 0.028 ms. Post: +1.047 ms over 198.48 s, +5.28 ppm, no step > 0.035 ms.

H3 was falsified separately by the bracket population: the 7 prior passing
brackets drifted 0.167–2.901 ms (median 1.69), and `instrument_calibration_mismatch`
had **never fired** before window B. Lead independently confirmed both by grep and
by enumerating all 22 valid calibrations; B's pre (35.436 ms) is the corpus maximum.
The competing "21% of pairs exceed the gate" figure was computed over ADJACENT
CALIBRATIONS ACROSS THE WHOLE CORPUS, including cross-campaign pairs, which is the
wrong population — brackets are pre/post within one campaign. That figure is void.

**Decision taken: window C then window D tonight. Window B deferred.** Clock
controls apply to C only. B's dominant term is fiducial onset-residual
repeatability (thermal vs dispatch fraction UNKNOWN) and no mitigation for it
exists yet; re-collecting B tonight would test a hypothesis already killed.

### Note on the pre-registration itself

The §4 criterion was imperfectly specified. It asked whether the fiducial is
"monotonic-only" (binary) and whether the wall−monotonic series is "flat".
Neither held literally — the fiducial IS wall-sensitive, and the series was NOT
flat. Read literally, the §5 rule would not have fired. What actually decided it
was the FRACTIONAL attribution: the wall term contributed −0.20 ms against a
+11.58 ms failure. Recorded here rather than silently reinterpreted: a
pre-registered criterion should be stated as an attribution fraction, not a
binary, and future pre-registrations in this project should follow that form.

## 6. Open, not blocking

The identity of the clock adjuster is unproven (`clock_sync.status` is
`limited_without_admin` unconditionally, so `timed` is plausible but
unestablished). One admin-privileged `log stream` observation would settle it.
Cheap, worth closing this week, not required tonight — but until it is closed,
"network time sync" remains a hypothesis about the culprit, and a mitigation
that no-ops silently would be worse than none. Verify the disable took effect.
