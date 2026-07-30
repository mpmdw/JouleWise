<!-- Origin: prepared 2026-07-30 for Ed's advisor meeting (Rivoire), from the
     magistrate session's banked facts and the same-day delegated related-work
     sweep (docs/run_reports/2026-07-30-sweep-*.md). Plain-language standing
     rule applies (professor-facing surface). Placed here rather than in
     docs/run_reports/ to match the existing docs/advisor_briefs/ convention. -->

# JouleWise — advisor brief, July 30

## The delta since our last meeting (~10 days)

Ten days ago we discovered a timing defect in how measurements were
anchored to the clock, and chose to invalidate every corpus collected to
that point rather than patch around it. Since then:

1. **Repaired the instrument** and added in-session calibration that
   *measures* the residual timing error (pulse-train fiducials before and
   after every measurement window) instead of assuming it.
2. **Characterized the instrument's true limits**: it is
   *attribution-limited* — the dominant error is assigning energy to the
   right instant, not measurement noise. That produced our core
   methodology: publish honest, labelled **detection floors** ("this
   instrument cannot see effects smaller than X joules") with every
   result.
3. **Collected the first fully clean sessions** in project history and
   minted the first floor artifact: the 1.5B model's decode floor,
   **7.38 J**, every gate green, acceptance thresholds frozen (and
   hash-sealed) eight days before the data existed.
4. **Validated a second instrument overnight**: a full calibration window
   for the 7B model — including two live contamination events (macOS's
   malware scanner, then a second, unidentified CPU excursion) that the
   admission gates caught and the protocol recovered from per its own
   written playbook. Floor: **14.0 J**. A null test (the model compared
   against itself) read **0.15 J with a block-to-block spread of
   ±2.6 J** — consistent with zero, and that spread is exactly where the
   14 J floor comes from.
5. **First cross-model measurements** (table below) and a literature
   sweep (full memo available): we found no published validation of
   Apple's powermetrics, and none of the LLM-energy work we surveyed —
   on any hardware — reports detection floors or in-window calibration.

## First numbers

| Decode, 512 tokens, 4-bit, M3 Max | Qwen2.5-1.5B | Qwen2.5-7B |
|---|---|---|
| Energy per member | 50.26 J (σ 0.21) | 192.39 J (σ 1.03) |
| Per token | ~0.098 J | ~0.376 J |
| Detection floor (comparative) | 7.38 J | 14.00 J |

Observed difference ≈ 142 J — more than 10× either floor. One honest
caveat we attach ourselves: these two measurements come from separate
sessions five days apart, and our floors bound error *within* a session,
not drift *between* sessions. So we call this a strong preliminary
observation, not a cleared claim. The claim-grade version — both models
interleaved in one session, drift-cancelling order, thresholds
pre-registered — is configured and validated; it runs this week and
should be in hand by our regular meeting. Note the ratio: ≈4.9× the
parameters (actual weight counts) costs 3.8× the energy, and decode ran
only 3.2× longer — the larger model also draws more power, not just
more time.

## Four decisions where your input steers the next five weeks

1. **Your acceptance bar.** For the capstone tier we're aiming at: how
   many claims, which figures, what reproducibility demonstration do you
   want to see? (This becomes the project's spec.)
2. **Scope of the write-up.** The distinctive contribution is the
   metrology (validated instrument + error budgets on consumer silicon —
   apparently unpublished as a combination). Frame the paper/report
   around the metrology with results as demonstration, or around the
   results with metrology as methods? Related: venue ambition —
   workshop (EuroMLSys/HotCarbon-class) vs. ICPE-class metrology track.
3. **Wall meter: yes or no?** Everything so far uses Apple's software
   counter, cross-checked internally but never against an external
   reference. Is external validation required for the tier you'd sign
   off on? (The requirements are scoped from the SPEC/RAPL-validation
   literature — the <75 W crest-factor trap, battery-neutralization,
   and a regression-based validation design; a concrete meter shortlist
   is about a day's work once you say yes.)
4. **Claim priorities for the remaining sessions.** Candidates ranked by
   measured feasibility: (a) the model-size contrast (running now);
   (b) speculative decoding on/off — identical weights, one flag, we
   found no published on-device measurement of its energy and the sign
   is genuinely open; (c) a quantization ladder (4/8/16-bit) — adjudicates
   a reported anomaly (4-bit worse than 8-bit) that no one error-barred;
   (d) MoE vs dense — the literature currently contains a sign
   contradiction our instrument could settle. Which two matter most to
   you?

## One sentence you can react to

"Attribution-limited detection floors for software-counter LLM energy
measurement, with in-window calibration and fail-closed custody,
demonstrated with phase-resolved results on consumer Apple Silicon."
