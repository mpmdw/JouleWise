# Magistrate synthesis — S3 claim-side bound (interactive magistrate, 2026-09-08 ~12:50 PDT)

Inputs: cold Fable ruling (10) and Opus contract-lens refutation (11) on packet sha 9b5eec35… at e241e0b7. Both rule
A+B (the scalar IS the estimator's complete deterministic-bound total B, `PairedEstimate.deterministic_bound_total`,
estimators.py ~:160/:422–447 = protocol :351–364; components must travel with it) and C for display until the
clause-to-test map lands. Where they differ the synthesis takes the stricter or better-evidenced text:

1. QUANTITY: B, copied (never recomputed) from `claim_verdicts.json contrasts[].deterministic_bounds.total`, with
   the per-kind `{name, bound}` list copied from `deterministic_bounds.terms` (judge 1/4, Opus 1).
2. NAME AND TYPE (Opus 1/5 governs; the judge's "propagation channel" reading is recorded as dissent): the sidecar
   field is `deterministic_widening_total` with `unit` (`J` or `J/token`), `estimator_id` and `ratio_estimand`; the
   S6 rendering token `claim_side_bound_j` keeps its S6 meaning (the non-gating clock-anchor planning term inside
   F+B). DS-29 binds explicitly to `deterministic_widening_total` and the registry note at :1128–1130 is resolved
   by that binding, not by overloading the token. A per-token quantity under a `_j` suffix is a BLOCKER (Opus 5).
3. JOIN (judge 3 governs; Opus missed it): `finalized_manifest.contrasts[].source_cell_ids` does not exist in the v3
   contrast schema (analysis_manifest_v3.py ~:1072–1085); the scaffold's :51 is re-pointed to
   `claim_verdicts contrasts[].floor.resolutions[].source_cell_ids` (ordered concatenation in resolution order, no
   dedup/sort, every resolution status ∈ {exact, transported}); plus Opus 3's injectivity check (two contrasts may
   not register identical ordered lists). No manifest schema change.
4. TOLERANCE (judge 4 governs, stricter): EXACT equality against the verdicts' JSON numerals byte-for-byte; the
   scaffold's isclose becomes diagnostic only; reject bool (Opus 4). Schema id bumps to `joulewise.claim_side_bound.v2`
   (Opus 4) because keys change; never issued under v1.
5. DOUBLE-WIDENING (both): `decision_interval` is copied from verdicts, never CI ± B recomputed; the sidecar's
   `metrology_aware_CI95` binds to `contrast["estimator"]["metrology_aware_CI95"]` INSIDE the S3 contract (Opus 2);
   the anchor term must be present in the term list (judge 5).
6. MUTATION SET = union of judge 6 (7 cases) and Opus 6 (a–h): anchor-only substitution; dropped kind; sum-for-mean;
   double-widen (decision fed as CI95; 2B); precedence flip; permuted/deduped/refused-resolution cells; 1e-13 drift;
   edited interval with matching scalar; ratio estimand into a `_j` cell; sign flip.
7. SCOPE: S3 producer (copy-only) + v2 validator + re-pointed join + exact-equality gate + `claim-evidence.v1`
   registration only after the producer exists + renderer projection DS-26/28/29 from gate-authenticated verdicts;
   replace the fixture that invents the missing manifest key (tests/test_paper_custody.py ~:888). X6/X7 and the S6
   claim-side display stay PROPOSED_STOP_FILL until the kills are green and S6 disambiguates the token from F+B.
   Decision-log entry D-178 records this ruling. Implementation seat: Astra high on the paper integration head
   after PR #301 merges (shares paper_custody.py with S2).
