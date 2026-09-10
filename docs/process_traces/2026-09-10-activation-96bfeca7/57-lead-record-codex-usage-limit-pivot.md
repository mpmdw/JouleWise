# 57 — Codex usage limit reached at ~08:41 PDT 2026-09-10; implementation pivots to Opus agents until 2026-09-15 00:52 PDT

Every Codex seat launched from 08:38 onward failed with `ERROR: You've hit your usage limit ... try again at Sep 15th, 2026 12:52 AM`:
S2 (`51`, NEEDS_SCOPE then the resume died), S3 (`52`, `52b`), S5 (`54`, partial: tool + chain skeleton + tests, committed WIP on
`feat/2026-09-10-epoch-s5-chain-watch`), S6 (`53`, partial: contracts + D-102 addendum draft + pre-registration file, committed WIP on
`feat/2026-09-10-epoch-s6-docs-prereg`). Seat logs carry the error verbatim. Twenty Astra seats ran today before the limit (scouts 02a/02b/04/09,
refuters 18/23/27/29, root causes 19/38, implementation 08/44/33, design 41, kernel 44, and the four S-seats).

Pivot (magistrate): the four implementation seats relaunch as Opus agents (Claude family) in the same worktrees under the same briefs (47–50 as
amended) and the same WRITE_SCOPE, which the runner no longer enforces — the lead reviews every diff against its footprint at the gate. Gate
shape unchanged (execution + contract refuters, delta re-audits, cold gate before issuance), but cross-model diversity is reduced to the Claude
family for implementation and review until Codex returns on 09-15; the design stage already had three families (Astra 41, Fable 42, Opus 43b)
and the mechanism ruling had an Opus pairing. Recorded as a limitation, not waived. The calendar in addendum 11 (corpus nights from 09-12) now
depends on Opus throughput and the Claude weekly bucket (resets 16:00 PDT today).
