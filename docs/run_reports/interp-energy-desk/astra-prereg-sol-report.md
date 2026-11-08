Committed `8e6032c92` on `interp/2026-11-07-astra-prereg`. Working tree clean; nothing pushed.

Added:

- [Preregistration draft](/Users/edr/code/CapstoneProject/jw-wt/sol-astra-prereg/docs/registrations/astra_2ch_v0_draft.md)
- [Analysis-plan draft](/Users/edr/code/CapstoneProject/jw-wt/sol-astra-prereg/docs/analysis/astra_2ch/ANALYSIS-PLAN-v0-draft.md)
- [Handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-astra-prereg/docs/run_reports/2026-11-07-astra-prereg-draft.md)

Both drafts are explicitly **NOT REGISTERED**. They cover behaviour/replay/synthetic arms, estimands, study noise anchors, KM003C authority, exclusions, blinding, stopping, and equivalence versus upper-bound outcomes.

Verification: Python document/link/arithmetic checks passed; Git whitespace checks passed. No unittest suite or native MLX tests ran; no code changed. No network, downloads, measurement-data access, or coordination-state edits.

Next: lead review of the seven open slots. Downloads, edit provenance, Mac windows, and native validation remain unresolved. In particular, ±0.1% DC precision is unverified; the eventual deliverable may be a wider bound. Native checks must cover bf16 edits, forced-token identity, KV/recurrent resets, swaps, and meter/clock/battery handling.