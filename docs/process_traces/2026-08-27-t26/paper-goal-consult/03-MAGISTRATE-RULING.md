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
