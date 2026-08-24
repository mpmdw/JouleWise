# MAGISTRATE RULING — P06 characterization result schema (D-144 co-design)

Shape executed in full: two blind seats (Opus / gpt-5.6-terra xhigh, both
citation-verified by their directors), one debate round, one counter-round.
The counter-round ACCEPTED all six contested items; convergence is total.
This ruling RATIFIES the converged design as `characterization_result_spec.v1`.

## Ratified design (normative summary; the seat files 01-04 are the record)

1. SIX public rows (linearity, null, empirical_floor, phase_attribution,
   drift_settling, between_sessions) with INTERNAL SUBTESTS; no public row
   added. Attribution is realized as conjunctive C4.3-C4.7 subtests
   (term decomposition; bracket-bound-in-issued-band; quarter-window
   eligibility rate = 0; cadence/sample fidelity; dominance realized via the
   committed predicate) — zero new tokens, zero new numbers, and a C4.7
   contradiction precommits that the fresh window's floors do NOT carry the
   attribution-limited label.
2. OUTCOME ARCHITECTURE, four orthogonal layers: row_outcome {supported,
   indeterminate, contradicted, pending_eligibility (C6-only)} mapping
   totally onto the template's four closed phrases; publication_class
   {RESULT, PUBLISHABLE_REFUSAL, DIAGNOSTIC_ONLY, PROTOCOL_INCOMPLETE};
   closed failure_class; closed characterization_* reason codes disjoint
   from readiness_*/histsem_*. protocol_incomplete is UNREACHABLE in an
   issued report post-freeze — the writer refuses issuance instead.
3. DUAL LIMIT LIMBS on C1 and C4-invariance: resolution limb (R_max <= H,
   always available, resolution-qualified ceiling enforced via
   claim_ceiling/exact_forbidden_upgrade) AND claim-anchored limb
   (R_max <= F_operative from a prior-issued same-cell floor); an
   unavailable limb renders indeterminate with
   characterization_operative_floor_unavailable — never silently dropped.
4. C2: c2_floor_mode frozen prospectively — issued_floor_comparator primary
   (disjoint hash sets required); heldout_train_test (10 blocks: 5 train /
   5 test) as the pre-registered conditional branch iff no issued floor at
   freeze. Rationale: g(5)=1.5 vs issued n=10 at g=1.
5. C3: k_r integer rounding AWAY from the gate boundary; both directions;
   the 1x slot registered with expectation:none; mis-sizing guard
   (predicted vs realized delta; breach -> indeterminate with
   characterization_effect_sizing_missed, never contradicted).
6. C4 closure: SIGNED split criteria (max D_i <= tau_float overcount;
   |D_i| <= gap duration x max gap power undercount), per the template's
   registered gap treatment.
7. C5: recovery via the COOLDOWN-EXIT first-pass time t_j (observable today
   at controller.py:2534/:2567/:2971), criterion max t_j <= 180 s, with the
   cross-mechanism sentence (180 is the settle convention; the cooldown's
   own cap is 300) and the workload-disturbance-only claim ceiling; drift
   containment on held-out reference probes excluded from the allowance.
8. C6: predicate-defined eligibility (never enumerated) with
   sessions_excluded[]; the symmetric 1.25x corridor labeled
   limit_basis=derived (a generalization of the directional ruled
   sentinel, never presented as ruled); the change-check import.
9. FREEZE HOME: the two-artifact form (contract prose carrying NO numbers +
   frozen spec JSON) bound by a successor frozen plan (executable today),
   PLUS the two report-writer ordering gates
   (characterization_criteria_not_prior;
   characterization_limit_supplier_not_prior) — the mechanism that would
   have refused the 2026-07-25 same-day criterion change. Upgrade to an
   arm-readiness receipt kind is strictly-later hardening.
10. Multiplicity: family registered exploratory (no confirmatory inference)
    + Holm m=2 over the two inferential members; ANTI-SELECTION rule (a
    contradicted row under a PASSED window never licenses re-collection;
    successor windows predecessor-link and both publish).
11. Failed-row publication form: seat B's §4 form adopted verbatim as the
    contract's normative form (failure_class + custody block + mandatory
    Interpretation-limit paragraph).
12. §5 worked examples fill NOW from retired diagnostics, explicitly
    labeled non-claim-bearing (house precedent at draft :78 and :426).

## ED-INPUT LEDGER (blocks the respective freezes, nothing else)
- sizing_tolerance_ratio (C3 mis-sizing guard) — no basis exists.
- tau_float (C4 overcount) — pinned code value or Ed ruling; A's 1e-9 J is
  NOT ruled and is not frozen.
- Held-out reference probe count (C5) — window budget; proposed >= 3.
- R1/R2 fallback ABSOLUTE limits iff no alpha/beta floor is issued at
  freeze time (the design's single largest dependency).

## Implementation work order (next)
Author: docs/contracts/characterization_result_schema_v1.md (no numbers),
configs/campaigns/metrology_v1/characterization_result_schema_v1.json
(numbers + derivation rules + token bindings), and the draft-v1.md §5
rewrite (spec Table 1 completed + worked examples + glossary). Registry:
AP-C1..C7 rows; token supplier updates. The metrology_v1 freeze-namespace
gap and the Window-C naming collision are separate registered work.
