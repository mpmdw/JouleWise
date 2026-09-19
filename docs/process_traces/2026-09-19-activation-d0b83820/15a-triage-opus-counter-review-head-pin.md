# Record 15a — lead triage of Opus counter-review 15 (head-pin test repair at `ff788ef7`) and fix round 1 at the bench (2026-09-19 08:4x PDT)

| # | Severity | Disposition |
|---|---|---|
| F1 | should_fix | ACCEPTED, fixed at the bench (bench-vs-session threshold: a five-line copy loop): `generation_repository()` now copies each FLOORS generator from the working tree over the clone's committed copy, so an uncommitted generator edit is graded (record 15's executed counterfactual: uncommitted `PLAN_ID` mutation passed blind, committed failed). Module `tests.test_d117_floor_qwen3_v5_generate` + `tests.test_campaign_generator_core`: 20 tests OK, 12.9 s. |
| N1 | nit | ACCEPTED, fixed at the bench: the generator-core head fixture is bound and asserted to have been called with the head path, so a future edit that routes around `sha256_file` for that path fails loudly. |
| N2 | nit | Queue data: the r6 path re-read duplicates the default acceptance file today and will stop describing the live anchor at r7 — the test already names r6 explicitly, which is the intent (the r6 cutoff literals belong to r6); revisit when r7 issues. |
| N3–N6 | nit | Queue data (fixture keyed to labels; clone inside the output root; digest self-check in three modules; hardcoded `head.json`): none changes what the tests prove; folded into the lane note for GENERATOR-HEAD-FILE-BYTE-PIN-01's implementation round, which will touch these tests again. |

Post-review commit: one (fix round 1). Delta re-audit of it: seat 19 (fresh Astra, read-only, detached worktree at the new head) with F1/N1 negative oracles, the five modules, and the quick tier. Row 10 (fresh-eyes on the post-review commit) is covered by that seat plus the lead's read of the 15-line diff.
