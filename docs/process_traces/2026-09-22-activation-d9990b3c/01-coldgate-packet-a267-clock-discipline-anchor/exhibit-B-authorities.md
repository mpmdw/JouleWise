# Exhibit B — controlling authorities at main `9b6b3f0e` (verbatim `git show` extracts; the magistrate wrote only the headings)

### B1 — `docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md` lines 1,200 (git show 9b6b3f0e:docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md | sed -n '1,200p')

```
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
```

### B2 — `docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md` lines 66,72 (git show 9b6b3f0e:docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md | sed -n '66,72p')

```
      },
      {
        "id": "D5",
        "ruling": "Retain and strengthen refusal gates.",
        "spec": "Keep wall_minus_monotonic_span_exceeded at >5 ms. Add affine_clock_fit_empty, affine_clock_residual_exceeded, clock_rate_limit_exceeded, clock_fit_span_insufficient, native_rollover_anomalous, rate_aware_native_set_empty, admissible_interval_empty, and effective_clock_anchor_bound_exceeded. Recommend an independent 5 ms ceiling on the resulting effective anchor bound as well as the existing 5 ms offset-span gate."
      },
      {
```

### B3 — `docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md` lines 90,96 (git show 9b6b3f0e:docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md | sed -n '90,96p')

```
      },
      {
        "id": "I4",
        "bar": "Prospective claim-bearing captures require authenticated network-time-OFF admission. ON or unknown cannot be normalized away by the affine fit; historical unknown-state material may be used only for validation diagnostics."
      },
      {
        "id": "I5",
```

### B4 — `docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md` lines 286,294 (git show 9b6b3f0e:docs/process_traces/2026-08-18-anchor-v3-science-review/02-design-consult.md | sed -n '286,294p')

```
Historical outputs should be sibling derivation records, never patched evidence. The archive/current validation artifacts remain `validation_only`; they do not retroactively make original invalid evidence claim-bearing.

## Residual risk

Even exact feasible-set arithmetic depends on the affine-with-bounded-departure model. A nearly linear network-time slew below both the 5 ms span limit and the residual threshold can look like oscillator rate. Prospective network-time-OFF provenance is therefore essential; the fit must not be treated as a substitute for that environmental control.```

### B5 — `docs/decision_log.md` lines 4747,4815 (git show 9b6b3f0e:docs/decision_log.md | sed -n '4747,4815p')

```
11. **Attribution-limited detection floors — Ed-RATIFIED amendment
   (2026-07-25).** The first collection under the merged SCREEN+BUDGET
   rules (windows a9, a10; both whole-window verdicts PASSED
   [2026-08-24 caveat, readiness-sitting B-45/L11-SF3: the verdict
   artifacts themselves were not retained — the retained extraction
   refuses `whole_window_neg8_verdict_missing` — so PASSED here rests
   on recorded close-out prose pending a recovered or re-derived
   verdict artifact]) could not
   produce a floor: all three of a10's phase-absolute cells refuse
   `admissible_set_uncertainty_dominates_point_floor`. **Finding: the
   instrument is ATTRIBUTION-limited, not NOISE-limited.** Repeatability
   is 0.29-0.49 J on ~50 J points (and a settled reference pair three
   hours apart agreed to 0.007 J [2026-08-24, B-47/L11-N2: unreproduced
   — no retained ref pair matches this figure; best candidate
   0.0013-0.0019 J gross at ~3.7 h]), but each member carries a
   clock-anchor-shift envelope of ~0.7-1.0 J: a +/-31 ms window shift
   across a phase boundary where power swings ~33 W mis-attributes ~1 J
   between prefill and decode. The composed bound is additive and
   measured — fiducial 24.9 ms (80-87%) [2026-08-24, B-47/L11-N2: the
   24.9 ms reproduces; the 80-87% fraction does not — retained members
   span 80-97%] plus bundle-local 3.3-6.1 ms
   plus edge span. Because repeatability will always beat attribution
   here, the refusal is STRUCTURALLY PERMANENT: no future phase corpus
   can pass it and there is nothing to re-collect around.

   **Alternatives measured and eliminated** (authenticated replay,
   2026-07-25): (a) the calibration-bracket gap is NOT the cause — every
   cell refuses under both its minted and its post-bracket bound (delta
   +0.167 ms); (b) instrument tightening cannot rescue it — extraction
   would require a 10x (decode) to 32x (prefill) bound reduction, and
   each cell's bundle-local term ALONE (3.3-6.1 ms) already exceeds the
   entire required bound (0.99-2.9 ms), so even a perfect fiducial
   calibration would still refuse; (c) coarser granularity does not
   rescue it — request-level cells replayed on a10 and a8 have smaller
   envelopes (1.5-1.9 J) but still dominate and still refuse; (d) an
   ABBA common-mode estimator gives a real 3x gain (a5 decode 6.46 J ->
   2.13 J) but remains above that cell's 0.60 J point floor. The
   labelled path below is therefore not the preferred option among
   several — it is the only remaining path to any detection floor at
   all, at any granularity, on this instrument.

   **Ruling (Ed-ratified).** D-054 registers the detection floor as a
   practical prediction bound on FALSE OBSERVED EFFECTS, not as a
   repeatability statistic; a false observed effect may arise from
   scatter OR from anchor mis-attribution, and the corner-widened
   maximum is exactly the largest false effect this instrument can
   produce. `admissible_set_uncertainty_dominates_point_floor` therefore
   becomes a LABELLED CLAIM PATH rather than a hard refusal: extraction
   publishes the widened floor with a `floor_source` field naming the
   dominant term (here `E_clock_anchor_shift_bound_j`) and retains the
   point floor separately as the repeatability diagnostic. The gate
   keeps its real function — preventing a repeatability-only number from
   publishing as if it were the whole story — while no longer conflating
   "unsound corpus" with "instrument-limited floor". a10 is sound.

   **Binding condition — SINGLE-COUNT DISCIPLINE (Ed: "the cost seems
   sensible as long as it's noted").** The floor gate now contains the
   anchor term, and each claim's decision interval separately consumes
   the member's `E_clock_anchor_shift_bound_j`. These are different
   objects (calibration false-effect bound vs claim-side measurement
   uncertainty) and both are legitimate, but the consequence is that the
   effective clearable effect is FLOOR + CLAIM-SIDE BOUND (~5 J for
   phase contrasts), not the floor alone. Every artifact publishing an
   attribution-limited floor must state this explicitly so that neither
   term is later removed as an apparent double count. Science must be
   sized to the ~5 J bar; Splitwise-class effects (tens of percent of
   tens of joules) clear it with margin.

   **Not authorised by this amendment:** any instrument-tightening
```

### B6 — `docs/decision_log.md` lines 171 (git show 9b6b3f0e:docs/decision_log.md | sed -n '171p')

```
| D-127 | AUTONOMOUS WINDOW LOOP authorized (Ed directive, in-thread 2026-08-08, during the 40h window): partially REVERSES D-114's descope — the scoped network-time toggle (QUIET-GUARD sudoers slice: exactly the two fixed systemsetup network-time commands, exact binary path + exact argv, no wildcards) plus an autonomous experiment-loop harness (post-window supervisor step relaunches a fresh headless claude session with launch-then-verify-then-retry liveness proof + an independent launchd fallback timer; agent fully EXITS during capture — zero-agent rule for the capture itself is UNCHANGED) are chartered for build. D-115's conditions bind the privileged install path (fresh sudo -k auth, authenticated staged content, interpreter isolation) and Ed personally executes the one sudo install command — the privileged step never passes through the agent. Security-critical: full D-118/D-121 gauntlet + pre-decision design consult; built OFF the night-critical path and INSTALLED only at a deliberate Ed-present moment (the PRIVILEGED sudo path only, per §3; a user-level LaunchAgent needs no Ed presence — D-169 stage-1 ruling) | ratified by D-128 (build authorized; install gated; initially chartered by Ed, in-thread; transcribed by the magistrate) |
```

### B7 — `docs/decision_log.md` lines 8528,8562 (git show 9b6b3f0e:docs/decision_log.md | sed -n '8528,8562p')

```

**Date:** 2026-08-08 (Ed, in-thread during the 40h window). **Status:**
RATIFIED by D-128 (build authorized; install gated; initially CHARTERED).

1. **What Ed authorized.** Claude Code drives the full experiment loop
   across multi-day unattended stretches: harvest → mint → judge →
   build/freeze next pack → toggle network time off → launch the
   supervisor → EXIT for the capture; the window's final step relaunches
   a fresh headless session. Ed's involvement reduces to optionally
   remote, or zero once the toggle lands.
2. **Zero-agent during capture is UNCHANGED.** The agent fully exits for
   the ~3h capture; this charter removes the human toggle and the
   relaunch gap, not the contamination fence. (The dormant-app
   characterization number becomes moot for this design — full exit,
   not residency.)
3. **Scoped toggle.** Sudoers rule for exactly the two fixed
   systemsetup network-time commands (exact path, exact argv, no
   wildcards). Honest risk register: worst-case abuse is TIME
   MANIPULATION, which for this project is a measurement-integrity
   vector (clock anchors, drift screens) — detectable by the existing
   custody/drift chain; not a general-privilege surface. D-115's
   install conditions bind (sudo -k fresh auth; authenticated staged
   content; interpreter isolation); Ed personally runs the single sudo
   install command after the artifacts clear their gauntlet.
4. **Relaunch harness (Ed's design point, corrected for process
   lifecycle).** No pre-existing process to check — each cycle launches
   fresh. Shape: preflight (binary, auth, disk state) → launch →
   liveness proof (the fresh session's first scripted action writes a
   heartbeat/claim file; launcher stands down only on proof) → bounded
   retries with backoff → independent launchd fallback timer as the
   second wake layer. Never one mechanism.
5. **Process.** Security-critical: pre-decision design consult, full
   D-118 gauntlet, D-121 terminal review; own branch/worktree, OFF the
   night-critical path (trust/recovery merges outrank it); D-114's
   remaining descopes (t3-resident, T3-CHAR-PAIR, WO-T3-VIS, SEC5A
```
