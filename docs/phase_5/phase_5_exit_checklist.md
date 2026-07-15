# Phase 5 Exit Checklist

Companion plan: `docs/phase_5/phase_5_plan.md`. This is also the project's
final checklist: green here means submission-ready.

## Evidence Matrix

| Item | Kind | Status | Required Evidence | Where Recorded |
|---|---|---|---|---|
| 5.0 README quickstart | required | pending | literal fresh-clone execution transcript; CI mock step mirrors it | run report + CI |
| 5.1 extension guide | required | pending | shipped `file_replay` tutorial adapter + tests; guide matches code section-by-section | `docs/extending.md` + test suite |
| 5.2 sample bundles | required | pending | mock + real bundles in `examples/runs/` (or release-asset fallback); CI validates them | repo + CI |
| 5.3 dataset freeze | required | pending | `v1.0-data` tag; SHA-256 manifest; regeneration-from-tag log | tag + `scripts/` + run report |
| 5.4 colloquium deck | required | pending | deck in repo; rehearsal timing; claim IDs in speaker notes | `docs/phase_5/colloquium/` |
| 5.5 final report | required | pending | report source; claims-index final-pass note with zero untraceable claims | repo + run report |
| 5.6 final repo pass | required | pending | LICENSE decided; final handoff `RUN_STATE.md`; CI green; clean status | repo |
| 5.7 publication release chain | required | partial — fixture/component smoke wired; private-corpus release and Ed-manual deploy pending | clean-clone `release_check.py --dry-run` passes in CI; controlled corpus regeneration and pack evidence retained; Ed records the manual drift review, site regeneration, and deploy | `docs/publication_release_checklist.md` + CI + release run report |
| Calendar honored | required | pending | each deliverable dated against `docs/milestones.md` actuals | `docs/milestones.md` |

## Definition Of Done (project level)

- A new user ran one local benchmark from the README alone (5.0 evidence).
- A new developer could add a backend from the guide alone (5.1 evidence).
- Final figures regenerate from published, hash-verified data (5.3
  evidence).
  Superseded (2026-07-15, WO-017; D-043): full figure re-derivation is controlled/internal by default; an externally re-reducible evidence handoff is optional and requires an affirmative privacy ruling; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4.
- Every quantitative claim in report and slides traces to bundles (4.3 +
  5.5 evidence).
- The ordered publication checklist has a green clean-clone component smoke,
  controlled/private-corpus regeneration evidence, and Ed's manual site
  regeneration/deploy record (5.7 evidence).
- All five phase exit checklists are green or carry explicit, dated
  descope notes per the R-012 ladder.
