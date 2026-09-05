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
   program. Revisit only if a pilot shows target effects below ~3x the
   widened floor. The free lever is workload sizing — attribution error
   is approximately duration-independent while effects scale with
   workload, so longer prefill/decode raises effect-to-floor linearly at
   zero instrument cost (queue FLOOR-WORKLOAD-SIZING-01).
