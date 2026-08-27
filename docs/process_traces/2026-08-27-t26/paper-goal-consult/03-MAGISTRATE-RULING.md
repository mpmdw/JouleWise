# Magistrate ruling — the paper's goal (T26, 2026-08-27)

Two seats (Sol xhigh, Opus 5), blind to each other, answered the same
prompt and the same reweighting addendum. Their texts are custodied
verbatim beside this file. This ruling is the ONE home for the paper's
organizing goal for the `paper/t26-sprint` work; Ed is the final authority
and may reverse any item below by a word.

## Where the seats agreed without contact (adopted as settled)

1. **The science is the attribution finding, not the model comparison.**
   Both seats independently picked the same goal: phase-edge placement,
   not run-to-run scatter, sets the smallest defensible phase-energy
   comparison on this instrument, and that limit is measured inside the
   same window it is used in. The Qwen 1.5B/7B contrast is a demonstration
   that stresses the floor, not the paper's destination. It survives a
   refused contrast; a claim-first paper does not.
2. **Custody and Appendix A are over-weighted.** Both seats: cut §4 +
   Appendix A by roughly 60%; keep the refusal-log paragraph and the
   scientific reproduction path (raw trace → anchor → pulse bound →
   verdict); move repository-governance mechanics (generated-state
   checks, receipt links, path conventions, workflow) to an artifact
   guide in the repo with a one-paragraph pointer.
3. **Length.** 30k words hides the best idea. Target 12–16k main-text
   words; reproduction material outside that count.
4. **Contributions 6 → 3:** (i) the in-window pulse-train calibration
   with the corrected clock model; (ii) the cell-specific resolution
   bound and the attribution-dominance finding; (iii) the demonstrated
   decision behaviour — two gates, printed refusals, the resolvability
   rule.
5. **The pulse-to-inference (load-regime) transfer assumption is
   limitation #1** in §7, stated first and plainly: the bound is
   characterized under the calibration regime and transported to mixed
   inference load; nothing in `_v4` tests the transfer. The cheapest
   closing measurement — a workload-shaped transfer calibration (Sol) /
   mixed-load pulse variant (Opus) — is Future Work #1, NOT a `_v4`
   change (the pack is frozen; changing it is a new family generation).
6. **Related work engages peers, not neighbours:** Khan et al. (RAPL in
   Action) and Jay et al. own the gain axis; JouleWise opens the time
   axis and must say so first, not defensively. Dauner et al. is the
   strongest corroboration; "The Illusion of Power Capping" is the closest
   methodological rival (phase-aware, repeated, independent cross-check
   — which we lack). Add Georges/Buytaert/Eeckhout and Mytkowicz et al.
   to the metrology lineage. Every citation the seats flagged [VERIFY]
   is verified against the bibliography audit before it is typeset.

## Where they differed, and the ruling

7. **Naming the floor.** Sol: "detection floor" sounds universal and
   probabilistic; prefer "resolution bound". Opus: register is fine.
   RULING: "detection floor" stays as the ARTIFACT and registry term
   (it is bound into D-078 cl.11, the floor artifacts, and the labels
   they publish under; renaming an artifact vocabulary mid-transaction is
   not a paper edit). In PROSE, the paper builds the quantity first and
   names it at first use as "the cell's resolution bound — the artifact
   calls it the detection floor", then uses "resolution bound" in
   narrative and "detection floor" when referring to the published
   artifact. Scope and the transfer assumption are restated where the
   number is used, not once.
8. **The primary research question.** Sol: the registry has no RQ that
   asks the attribution-dominance question (RQ-METHOD-FLOOR is a
   methodology row); register one. Opus: RQ-METHOD-FLOOR is the
   headline. RULING: Sol is right on the registry's own terms — a
   methodology row cannot be the paper's falsifiable claim. Register:
   **RQ-ATTRIBUTION-DOMINANCE** — "Under the corrected clock model, does
   phase-boundary attribution rather than run-to-run scatter dominate the
   resolution bound for prefill and decode on the named M3 Max / MLX /
   powermetrics configuration?" Falsifier (Sol turn 2 §1, adopted
   verbatim in substance): for each claim-bearing phase cell, the
   point-only repeatability floor and the timing-widened floor are
   produced independently; the claim holds where the timing term
   exceeds the repeatability term and falls where it does not; a
   one-phase failure narrows the claim to the other phase; a total
   failure turns the paper into "a calibration that corrected its own
   clock-model error, followed by a prospective null" — still a
   defensible capstone, with the Qwen contrast promoted to the principal
   demonstration. Registration follows the registry's own promotion
   rules and is Ed-reversible.
9. **How many RQs the capstone carries.** RULING: ONE primary
   (RQ-ATTRIBUTION-DOMINANCE), ONE demonstration contrast (C5-1.1 in its
   permitted pairwise form: fixed 7B vs fixed 1.5B — never an
   active-parameter scaling law), ONE printed negative result
   (RQ-SHORT-PREFILL-RESOLVABILITY: short prompt-processing phases are
   not resolvable at this sampler cadence, with the rule that decides
   it). Every further RQ needs its own cell floor (floors do not
   transport) and therefore a measurement night the sprint does not
   have.
10. **The null row is the floor's own falsification test** (Opus audit
    C). RULING: adopted — §3 says in one sentence that the
    identical-condition null block passing at the corner-widened floor
    is the test of the floor itself; its number is reported first in §6.
11. **The headline numbers rest on retired runs** (Opus audit B).
    RULING: until `_v4` issues fresh floors, every 25 July number in
    the draft is labelled as diagnostic-era evidence of the phenomenon,
    not a current instrument property; the phase-accounting row is
    named as the repair. The results-fill registry gains a row for the
    dominance test's two floor terms per cell — the paper director
    verifies that both terms are ISSUED by the frozen `_v4` pack's
    existing outputs (DS-08 option B built both terms in prose, so they
    should be) and reports NEEDS-RULING if either is not derivable at the
    desk. No pack change.
12. **Between-session stability and micro-delta rows** (Opus audit D):
    RULING: demote to Future Work rather than print "pending".
13. **Over-disclosure** (Opus audit E): TOCTOU, operator trust, retired
    bundle counts compress to one paragraph.

## What this does NOT change

- The frozen `_v4` pack, its rows, and the transaction runbook.
- D-078 cl.11 (attribution-limited, labelled floors) — the ruling
  restates its scope; it does not reinterpret it.
- The paper-first priority stack (P1 capstone, P2 ICPE, P3 modularity).

## Orders to the paper director (round 2 onward)

Shortest path, merged from both seats, in this order: (1) retitle;
rewrite abstract and §1 around the single finding, contributions 6→3;
(2) §7 opens with load-regime transfer; (3) §3 gains the null-row
falsification sentence and the first-use construction of "resolution
bound / detection floor"; (4) §2 compresses to the physical failure, the
named diagram, the algorithm, one numeric reconstruction; (5) §5
collapses to the criteria table + the most probative outcomes, with
between-session and micro-delta moved to Future Work; (6) §4 + Appendix
A cut ~60%, governance mechanics moved to the repo artifact guide; (7)
§8 rewritten to engage Khan/Jay, Dauner, Illusion-of-Power-Capping as
peers and add the metrology lineage; (8) the short-prefill negative
result printed as a named result; (9) results-fill registry gains the
dominance-test rows and the register-the-RQ delta is drafted for the
registry. Round 1's mechanical pedagogy/fidelity fixes stand where they
touch retained text; do not polish text slated for the cut.

## Addendum (2026-08-27) — the blind Fable seat, and what it changes

Ed asked why no blind Fable instance sat at the table; the magistrate
had substituted itself, which is not blind. A fresh Fable seat
(`04-fable-seat.md`) then ran on the identical prompt, blind to both
seats and to this ruling. It picked the SAME goal (instrument-first,
attribution finding; contrast demoted; negative result embedded) and
independently proposed registering the same missing RQ — so items 1–6
and 8 above now rest on three model families converging blind. It also
found things the other seats missed. Rulings:

14. **Holm / p-value text has no source.** The pipeline produces
    deterministic intervals and two gates; no test statistic is defined
    anywhere. RULING: the paper director VERIFIES against the code that
    no p-value or Holm computation exists; if confirmed, delete the
    multiplicity text and state "two deterministic gates, two registered
    contrasts; no multiplicity correction is applicable" — and check the
    analysis plan (AP) documents for the same orphan.
15. **`[B_decode_claim_J]` is STOP_FILL / SUPPLIER_UNKNOWN** (Sol also
    flagged missing suppliers). RULING: resolve the supplier at the desk
    if one exists in the reduction outputs; otherwise DELETE the sizing
    sum from the results table rather than print a placeholder that can
    never fill. Director reports which.
16. **Inserted-gap fiducial arm** (a commanded ~500 ms sleep between
    prefill end and decode start on ~10 real-workload runs, edges fitted
    with the existing pulse estimator, residual compared to the
    pulse-derived bound) is the cheapest closure of the transfer
    assumption — better-shaped than the generic "workload-shaped
    calibration" of item 5. RULING: it does NOT enter `_v4` (frozen pack;
    any non-config change is a new family generation). It is named as
    Future Work #1 in concrete form and registered as a queued row
    (TRANSFER-FIDUCIAL-01) for the first post-campaign diagnostic
    window; the paper says plainly that `_v4` leaves transfer untested.
17. **p256 prompt contrast vs D-117's decode-only default.** RULING:
    director verifies whether Ed's option was exercised (decision log /
    freeze manifest); the paper states which, in one sentence, where the
    contrast is introduced.
18. **Citations to add:** Hähnel et al. 2012 (RAPL for short code paths —
    the closest ancestor to edge placement) and Hackenberg et al. 2013
    (sampling-cadence bias), both [VERIFY] against real bibliographic
    records before typesetting; nothing is cited on a seat's memory.
19. **RQ count — dissent recorded.** The Fable seat would carry three
    (RQ-METHOD-FLOOR, C5-1.3, C5-1.1-pairwise). RULING stands at item 9
    (one primary + one demonstration + one printed negative result):
    C5-1.3 asks about power asymmetry, not resolution — the seat's own
    words — and a third carried RQ costs a floor the sprint does not
    have. C5-1.3 is named in Future Work as the first characterisation
    the calibrated boundary makes decidable.
20. **Label regime — dissent recorded.** The seat would drop the
    attribution-limited label rule and report the ratio. RULING: the
    label regime is D-078 cl.11 and is not a paper edit; the PAPER
    reports the ratio as the number and the label as its one-line
    consequence, so a reader never needs the rule to use the result.
21. **"Detection floor" gloss** — the seat's first-use gloss is adopted
    verbatim alongside item 7: "the largest false difference this
    measurement system can manufacture."
22. **§5 before §3** (characterise, then compose). RULING: adopted — it
    is the why-chain in section order; the director reports if it
    creates more forward references than it removes.
23. **Length.** The seat says 8–10k; the others 12–16k. RULING: 12k
    main-text HARD ceiling, 10k the target; the round-2 PR reports the
    count.

## Addendum 2 (2026-08-27) — round-1 verification returns; corrections and decisions

Round 1 (PR #202, merged) verified six items against code and record.
Two of this ruling's premises were WRONG and are corrected here:

24. **Item 14 is WITHDRAWN.** Holm / p-values are implemented
    (`analysis_engine/multiplicity.py`, `two_sided_student_t_p_value`,
    `tost_p_value`) and ratified by D-139 A2. The paper keeps them. A
    REAL conflict was found instead: `analysis_manifest_v3.py:476`
    freezes m=1 while D-139 A2 rules m=2. This is potentially
    claim-bearing for the `_v4` transaction; a three-seat blind consult
    (Sol xhigh, Opus, Fable) is running and the ruling follows as
    Addendum 3. Until then the paper text states m=2 per D-139 A2 and
    footnotes nothing.
25. **Item 15 is WITHDRAWN.** `[B_decode_claim_J]` has suppliers.
    RULING on which: the column means the contrast's whole deterministic
    bound, `deterministic_bounds.total` (`artifact.py:667`) — that is the
    "comparison's own uncertainty bound" the sizing sum adds to the
    floor; `E_clock_anchor_shift_bound_j` is one term of it and is not
    the column. The column header names the quantity.
26. **Item 11 — TERM A/B.** TERM B (`cells[].floor_gate_j`) issues for
    all four claim-bearing cells; TERM A (point-only repeatability floor)
    is emitted only when the dominance predicate is already true
    (`detection_floor.py:3295`), so it cannot represent the negative
    outcome of the falsifier. RULING: (i) TERM A is DERIVED AT THE DESK
    from the emitted per-cell repeatability statistics, under a replay
    fence, and the derivation is PROVEN by reproducing the emitted
    diagnostic byte-for-value in every cell where the code does emit it
    (self-consistency proof; a Sol xhigh + blind Fable check each); (ii)
    TERM B for the dominance comparison is the CORNER-WIDENED floor — the
    quantity the code's own dominance predicate compares — derived the
    same way if not emitted; `floor_gate_j` (drift-widened) is reported
    separately as the gate; (iii) a post-`_v4` kernel row makes the TERM A
    emission unconditional. No pack change.
27. **RQ row:** register as `candidate` now; no PROJECT_STATUS slot is
    added during the sprint.
28. **Title:** two titles are drafted and held in the results-fill
    registry — the primary around attribution-limited resolution (used
    if `_v4` reproduces dominance) and S8's protocol-first title as the
    null-outcome title. Neither is typeset before `_v4` issues.
29. **The 25.6–31.1 ms range** is stated once, with its n and its
    diagnostic-era label (item 11), never as if 30 independent draws.
30. **37/50 retained prompt phases fail the resolvability rule.** That
    number IS the printed negative result of item 9 — reported as such,
    with the rule, not as a limitation.
31. **Round-2 writer brief carries the diff-ritual findings:** every
    worked example names its time/space origin; every contribution
    sentence cites the section that discharges it; every gloss added by
    a pass is fidelity-checked against code before it lands.

## Addendum 3 (2026-08-27, post round 2) — nine decisions

32. **Drift screen 9.724 ms vs 10.818 ms.** The frozen artifacts
    `n17_r3..r6` bind `bracket_screen_s = 0.009724`; D-125 rules
    0.010818; this is S9-05 on Ed's list. RULING for the paper: print the
    value the frozen artifacts bind (9.724 ms) wherever the number is
    used, ONCE, with a registered note that D-125's ruled value differs
    and the reconciliation is pending Ed's ruling; the §4 figure
    10.817749309 is replaced by the same reference. The paper never
    states two values for one screen.
33. **Item 25 is WITHDRAWN** (second withdrawal on verification). The
    renderer guard at `scripts/render_results_fills.py:977` and the
    registry's own fill rule deliberately forbid binding
    `deterministic_bounds.total` to `[B_decode_claim_J]`; the column is
    the CLAIM-SIDE bound as the registry defines it. It stays STOP_FILL
    with the rule text until a supplier is built post-`_v4`; the sizing
    sum renders only then. The column rename and DS-29/PG-05 anchors
    stand. The magistrate's lesson is recorded: two rulings this sprint
    contradicted code that was right; verification items stay mandatory
    on every numeric ruling.
34. **TERM A aggregation and TERM B semantics.** RULING: the paper's
    falsifier IS the code's dominance predicate, verbatim — per-component
    comparison as coded (`A_guarded = guard_factor × max(max_abs_residual_j
    | max_abs_delta_j, prediction_component_j)`; no invented aggregate),
    and TERM B is the exact corner maximum the predicate compares (derived
    at the desk under the replay fence). The emitted
    `corner_widened_guarded_floor_j` (≥ that maximum) is reported as the
    PUBLISHED floor and `floor_gate_j` (drift-added) as the GATE; the
    paper says in one sentence which quantity each of the three
    sentences tests. Registry rows are written to that.
35. **DS-08 marker.** A successor marker DS-08a is AUTHORIZED naming the
    renumbered sections; the old marker's bytes are retained with a
    superseded note in the registry.
36. **Holm m=2 replay.** Appendix A and the artifact guide say claim
    replay becomes executable when W-10 (D-157) lands; the paper's m=2
    stands.
37. **Hackenberg 2013.** Escalation trigger honoured. RULING: DROP the
    citation from the draft (it was a seat suggestion, marginal to the
    argument); keep Hähnel 2012 as characterised. No round three.
38. **Diagnostic values with no issued custody** (0.2888/0.4934/0.3113 J;
    25.6–31.1 ms). RULING: trace each to the actual July-25 artifact path
    in the results-fill registry; any value that cannot be traced becomes
    a registered `[PENDING]` with the diagnostic-era label. No number
    stands on seat prose.
39. **Replication bar.** Restore to the artifact guide the
    reference-repeatability construction and the 120 s projection
    deadline (as stated facts with their code anchors), restore Table 1,
    re-anchor Figures 2 and 3, refresh the registry's 42 line locators.
    Round 3 is this list plus a full pedagogy + fidelity pass over the
    NEW text (a cut this deep re-opens the first-use test everywhere).
