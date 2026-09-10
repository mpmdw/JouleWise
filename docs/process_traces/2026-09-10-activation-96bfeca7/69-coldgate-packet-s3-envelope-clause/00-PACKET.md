# Cold-gate packet 69 — seat S3's generation-row ceiling clause, and the masked-counterfactual harness rule (rule 11: two consecutive rounds, same signature)

Assembled 2026-09-10 ~09:40 PDT by the resident magistrate (activation 96bfeca7). Trigger: seat S3 (generation-keyed acceptance validation, branch
`feat/2026-09-10-epoch-s3-acceptance-validator`, HEAD 93799321) has had two consecutive rounds carrying the same defect signature — a check whose
naming counterfactual is masked by an upstream fence (refuter 65 F7 → delta 68 D2) — and round 1 introduced a clause no ruling states. The magistrate
does not run round three; it asks the cold gate to rule the clause and the harness rule.

## Q1 — the clause (Exhibit C, `_registered_generation_row_is_complete`, seat S3 branch)

Round 1 (curing refuter 65 F3, the third unchecked copy of the ceiling) added: `inherited_ceiling_s == maximum_budgetable_drift_s == prediction_99_two_draw_s`
(Decimal equality) AND strict `bracket_screen_s < maximum_budgetable_drift_s`, on EVERY registered generation row. Delta 68 (Exhibit A, D1/D2): the
`maximum_budgetable_drift_s == prediction_99_two_draw_s` half refuses a successor whose inherited (non-falling) ceiling sits ABOVE its own corpus Q99 —
exactly the lineage-monotone envelope D-125 cl.2 ratifies (Exhibit D: "neither screen nor ceiling may fall as more observations arrive"; the Q1Q13
consult's strictly ordered inherited pair) — and its naming test does not isolate it (mutation X2 survived: the row-vs-artifact prediction comparison
downstream already refuses the test's counterfactual). The strict `screen < ceiling` half is right and universal (D-126 cl.3: cap = ceiling − screen with
no clamp, cap > 0). Rule the exact relation the generation row must satisfy between `inherited_ceiling_s`, `maximum_budgetable_drift_s` and
`prediction_99_two_draw_s`, for (a) existing generations (import_only; today all three equal) and (b) a D-125 envelope successor (import_plus_live):
options — (i) `ceiling == drift` and `drift >= prediction` universally; (ii) equality only when `screen_rule == range_equals_screen`, `drift >= prediction`
under the envelope rule; (iii) other. Also rule whether `inherited_ceiling_s` should exist at all as a separate registered field (refuter 65 F3 called it a
third copy; delta 68 shows its only live bite is the envelope case) or whether the generation row should carry the PREDECESSOR's ceiling explicitly
(the value the envelope max is taken against) instead. Give the isolating counterfactual for whatever clause you rule (an input the clause refuses that
no other check refuses).

## Q2 — the harness rule (a proposed process mechanism; rule 11)

Delta 68 §7 proposes: any fence added upstream of an existing check obliges a re-cut of every counterfactual that reached the old check THROUGH it —
i.e. a fix round's delta re-audit re-runs the WHOLE mutation sweep and each counterfactual must be shown to reach its own clause (Ran N with a test
selected; the clause's deletion alone flips it). Rule whether this becomes a standing clause of the adversarial-review doctrine (the magistrate cannot
adopt it; Ed may veto) and its exact wording.

## Constraints

Historical artifacts (r2–r6, n19 genesis) must keep loading byte-identically; no successor data is registered; the cure is the smallest clause change.
Ruling file: `10-coldgate-fable-ruling.md` here — Q1 (the ruled relation, the code shape in one line, the isolating counterfactual), Q2 (adopt / amend /
refuse, exact wording), Executed probes (read-only `git show`/`grep`/`python3 -c`; no edits; refs are shared: the S3 branch is
`origin/feat/2026-09-10-epoch-s3-acceptance-validator`; never touch /Users/edr/night-custody or the rehearsal checkout).
