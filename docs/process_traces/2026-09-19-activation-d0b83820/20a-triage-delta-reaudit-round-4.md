# Record 20a — lead triage of delta re-audit round 4 (record 20) and fix round 5 contract (2026-09-19 09:0x PDT)

Record 20: S1–S7, N1–N3 all FIXED as ruled (executed against record 13's probes); no change outside the ten dispositions; eleven mutants killed; real-load AST unchanged; both same-signature statements none found. Two new findings:

| # | Severity | Disposition |
|---|---|---|
| R1 | should_fix | ACCEPT. The Markdown summary's three tables still label groups by state / repeat / census condition only, so the groups S5 correctly separated by `boot_id` / OS build render as indistinguishable rows. Same defect class as S5 in the human-readable surface. Fix: add `boot_id` (and `os_build` when present) columns to all three tables; regression asserts two boots render as two distinguishable rows. |
| R2 | nit | ACCEPT. The S1 regression injects a child that sleeps 60 s after reporting, so every passing module run spends the full 5 s production grace (module 5.3 s → 14 s). Fix: give `load()` a keyword `join_grace_s=5.0` (production default unchanged; the CLI does not expose it), and have the escalation regression pass a short grace (e.g. 0.2 s) while the one-second clean-exit regression keeps the production default. |

Fix round 5 = seat (Astra high, same WRITE_SCOPE, brief 21) → delta re-audit round 5 (fresh seat) → full sharded replay at the final head → PR.
