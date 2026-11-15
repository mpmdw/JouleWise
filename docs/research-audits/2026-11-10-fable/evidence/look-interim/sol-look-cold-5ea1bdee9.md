# Seat: sol, interim look cold

```text
Sat Nov 14 23:08:28 PST 2026
```

**Verdict: REFUSE current head `5ea1bdee9` for a real interim look.**

[Full report with every ruling trace, file:line references, runnable reproductions and fixes](/Volumes/JW-EXT/scratch/sol-look-cold/REPORT.md).

Nine findings:

1. **High:** Inclusion decodes energy values before discarding them.
2. **High:** Inclusion opens type-T bundles; a legacy field also overrides the ruled type selector.
3. **Medium:** The output guard aborts on valid relative residuals ≥100%.
4. **High, CI:** Both numerical test modules fail collection without NumPy; ordinary CI never installs it.
5. **Medium:** Manifest, schema and assembler still admit the hp-01 table removed by RL-167.
6. **Medium, science gate:** Q11’s statistic-identity condition remains unverified; use the ruled 0.04 fallback pending disposition.
7. **Medium:** Validator accepts altered required sentences and an incomplete never-read list.
8. **Low:** One-day input causes an unhandled empty-fold error.
9. **Medium:** An unpinned meter-parser dependency can change results without changing emitted code hashes.

Verification: 185 focused tests **OK, one skipped**; all seven generator scenarios completed. The pinned step-3 hash matches. Wrong-hash stage 2 opens no custody, but actual Git commitment remains a procedural gate.

The broader cadence suite ran 340 tests with 13 launch-fixture errors under this environment’s `/bin/ps` restriction. Both worktrees remain clean; no commit or push occurred.