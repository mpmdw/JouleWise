WRITE_SCOPE: []

# CONSULT (rule-11 same-signature escalation: "another missed call site") — where does the ONE entry-level guard for the custody-locator override belong on issuing paths? (gpt-6-astra, medium, read-only)

HEAD = 20cd559f on the ICLOUD-CUSTODY-LOCATOR-01 branch. Lane summary: custody-locator filesystem probes are now
bounded (pure path probe, 2 s, outside any lock) and `JOULEWISE_BACKUP_ROOTS` lexically replaces backup roots for
READ/REPLAY paths. Opus SF-4 found that a NON-EMPTY override on a MINTING path can hash bytes at the mapped root
while the receipt records the original locator (false evidence record). Fix round 1 guarded `artifact_hashes` and
some issuance paths with `custody_locator_override_mint_forbidden`. The delta re-audit (trace
docs/process_traces/2026-09-08-handoff-redo/99u-ref-icloud-locator-delta-astra-report.md; read it at the absolute
path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99u-ref-icloud-locator-delta-astra-report.md)
found two MORE sites: `scripts/validate_powermetrics_fiducial.py:1316` (`_CaptureLedgerLifecycle.begin()` writes
append-intent and a pending reservation before the refusal fires, so finalize/abandon then refuse and leave the
reservation pending) and `:1099` (`rederive_artifact()` hashes custody inputs and emits evidence unguarded). Two
rounds, same signature: per-site guards keep missing sites. Stop adding per-site guards.

Your charge (read-only): (1) enumerate EVERY process entry point that can mint, reserve, issue, rederive, or
finalize custody-bound evidence (scripts/*.py mains, joulewise/* public functions called by them; grep for the
ledger lifecycle, reservation, evidence emission, receipt writers); (2) propose the SINGLE structural guard: the
override is a read/replay affordance only — every issuing ENTRY POINT refuses at process/function entry when
`JOULEWISE_BACKUP_ROOTS` is set non-empty, BEFORE any lease, reservation, capture-state, hashing, or write (name the
exact function/line for each entry point, and whether a shared helper `refuse_if_custody_override_active()` can be
called from one place per script); show that read/replay paths (validators, replays, tests) keep the override;
(3) state the residual: any issuing path that cannot be reached through a guarded entry (e.g. library functions
imported by tests) and what to do (assert at the library level too, or document); (4) the regression shape: one
parametrized test per entry point that sets a non-empty override and asserts refusal with NOTHING written (diff the
custody tree before/after); (5) whether the per-site guards from round 1 should be REMOVED (redundant) or kept as
defence in depth. Output (genre review): `verdict` = {counts, findings}; header < 8192 bytes; body = the entry-point
table with file:line, the guard placement, and a seat brief verbatim under `## SEAT BRIEF` with a `WRITE_SCOPE:
[...]` line in exact JSON.
