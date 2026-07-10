# Phase 4 Exit Checklist

Companion plan: `docs/phase_4/phase_4_plan.md`.

## Evidence Matrix

| Item | Kind | Status | Required Evidence | Where Recorded |
|---|---|---|---|---|
| 4.0 protocol ratification | required | pending | observed-variance note; D-014 status updated before first figures | `docs/phase_4/protocol_ratification.md` + decision log |
| 4.1 aggregation | required | pending | aggregate tests; dataset rows + exclusions reconcile exactly with bundles on disk | test suite + `analysis/` |
| Exclusion log discipline | required | pending | every excluded bundle has a reason; zero silent exclusions (reconciliation proves it) | `analysis/exclusions.md` |
| 4.2 figure pipeline | required | pending | all registry figures regenerate via one documented command; render tests pass | `scripts/make_figures.py` + `figures/` |
| F1-F8 coverage | required | pending | each research question Q1-Q3 has its registry figures rendered from real data (or descoped with R-012 note) | figure registry table |
| 4.3 claims index | required | pending | 100% of quantitative claims have rows; 3 spot-checks traced claim->figure->script->bundles | `docs/phase_4/claims_index.md` |
| 4.4 results draft | required | pending | findings for Q1/Q2/Q3; limitations cover boundary table, co-residency, exercised fallbacks, network conditions | `docs/phase_4/results_draft.md` |
| 4.5 sensitivity audit | required | pending | per-headline-claim effect-vs-CI table; thermal-order audit; clock-bound audit | sensitivity appendix in results draft |
| 4.6 related-work draft | required (ungated; may close early) | complete (2026-07-09 reconciliation; drafted 2026-07-06 via c31ffac — docs/phase_4/related_work_draft.md, 11 sources, citations independently verified; reconciled per DOC-009/REV-8) | sourced background draft; every design choice mirroring/departing from prior art cited; citations resolvable | `docs/phase_4/related_work_draft.md` |
| Repro check | required | pending | clean checkout + runs corpus => dataset + figures regenerate, performed once end-to-end and logged | run report |

## Phase 5 Readiness Gate

Phase 5 may start when the matrix above is green and the dataset is frozen
(no further hardware sessions planned). Figures and claims must not change
during Phase 5 except through the full pipeline (edit script -> regenerate
-> update claims index), so presentation work builds on stable ground.
