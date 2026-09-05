## D-083: The additive effective-clearable-effect expression is a disclosure obligation, not an acceptance threshold

- Date: 2026-07-29
- Status: accepted (magistrate-adjudicated from primary text on a referred
  Sol-vs-Opus split; review finding B3 → NOT-A-DEFECT; no code change)
- Applies to: `joulewise/analysis_engine/claims.py`, every artifact or prose
  surface that publishes an attribution-limited floor
- Supersedes nothing; clarifies the enforcement semantics of D-078 clause 11

`effective_clearable_effect = floor_j + claim_side_bound_j` is a statement
the project owes its readers, **not** a gate a claim must clear. The
**two-gate structure** in `claims.py:324-363` — the floor gate containing the
anchor term, and each claim's decision interval separately consuming the
member's `E_clock_anchor_shift_bound_j` — is the **ratified design**.

Grounds (primary text read directly this session, not packet-trusted):

1. **D-078 clause 11's own words.** It introduces the additive expression as a
   *consequence* of the two-object design it has just ratified: "These are
   different objects … and both are legitimate, but the **consequence** is
   that the effective clearable effect is FLOOR + CLAIM-SIDE BOUND … Every
   artifact publishing an attribution-limited floor must **state this
   explicitly** so that neither term is later removed as an apparent double
   count." The operative verb is *state*. Science requires the disclosure;
   the code already enforces it (`claims.py:274-304`, exact-equality
   validation else `floor_artifact_invalid`).
2. **D-079 clause 5.** "The attribution-width floor is a diagnostic; the
   **operative floor is the claim gate**." The gate is the floor — not floor
   plus bound.
3. **The referral question — do the two citations address different objects?
   YES, explicitly.** D-082 clause 2 / contract rule 8 ("NEVER sum
   allowances") governs FLOOR-SIDE component composition (absolute vs
   comparative allowances *inside* the gate). D-078 clause 11's claim-side
   bound is consumed by the claim's decision interval — a different object,
   per clause 11's own words. The D-082 citation is therefore **orthogonal**
   to B3 and neither compels nor forbids the reading; the D-078-internal
   consequence/disclosure reading is decisive on its own and D-079 clause 5
   corroborates it.
4. **Consistency.** An additive *acceptance* gate would require its own
   ratification — it would sit in tension with D-082 clause 2's direction of
   travel as merged.

**Dissent preserved (Sol, xhigh review lens):** that the ratified text makes
the sum the operative bar ("not the floor alone"), worked through an executed
example (a claim of 8.63 J admitted against floor 3.59 plus a comparable
claim-side bound). The magistrate finds the ratified text does not support it:
that phrase is the same sentence's honest description of what a claim must in
practice clear across BOTH gates jointly, and does not convert the disclosure
into a single summed gate. `claims.py` was untouched by the mint series, so
the disposition carries no merge impact either way.

The practical phrasing already circulating in project notes — "effective bar
= floor + claim-side ≈ 5 J for phase contrasts" — **stays**, as the correct
description of what a claim must clear across both gates jointly. This entry
governs the *enforcement* semantics only.

Revisit when: someone proposes a single summed acceptance gate (which would
need its own ratification), or a floor artifact is published without the
clause-11 disclosure.
