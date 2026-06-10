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
| Calendar honored | required | pending | each deliverable dated against `docs/milestones.md` actuals | `docs/milestones.md` |

## Definition Of Done (project level)

- A new user ran one local benchmark from the README alone (5.0 evidence).
- A new developer could add a backend from the guide alone (5.1 evidence).
- Final figures regenerate from published, hash-verified data (5.3
  evidence).
- Every quantitative claim in report and slides traces to bundles (4.3 +
  5.5 evidence).
- All five phase exit checklists are green or carry explicit, dated
  descope notes per the R-012 ladder.
