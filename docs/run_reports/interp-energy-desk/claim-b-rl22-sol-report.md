Applied all four RL-22 fixes and the equivalence-power correction on `claim-b-rl22`.

- `41228e3e2` — implementation, regressions, and text corrections
- `93399139d` — handoff report

Changed the packet builder, two test modules, protocol, DEVIATIONS, agreement, Opus report, and [handoff report](docs/align/v4/CLAIM-CONTRACT-B-rl22-report.md).

Verification: failing-first regression confirmed; **190 tests passed across 14 targeted unittest modules**. Focused compileall and diff checks passed. Full suite omitted as instructed; no MLX code changed.

Working tree is clean; nothing pushed. No unresolved implementation questions. Commit absence was tested by mocking. Next: required Fable/research-lead delta review before merge.