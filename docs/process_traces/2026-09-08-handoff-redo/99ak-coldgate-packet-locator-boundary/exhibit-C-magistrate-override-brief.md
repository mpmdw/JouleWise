WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","tests/test_calibration_ledger_custody.py","tests/test_calibration_bracketing.py","docs/contracts/calibration_ledger_append.md"]

# Seat brief — ICLOUD-CUSTODY-LOCATOR-01 part 4: the override is READ/REPLAY-ONLY; issuing paths never consult it (gpt-6-astra, medium)

HEAD = 20cd559f (fix round 1). The delta re-audit (trace 99u) found two more minting sites where a non-empty
`JOULEWISE_BACKUP_ROOTS` can bind relocated bytes to an original locator; a consult (trace 99ae, absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ae-consult-sf4-astra-report.md) proposed a
31-file entry-point guard. MAGISTRATE RULING (D-161 proportionality; the hazard is an honest-operator footgun):
REJECT the entry-point guard programme. Adopt instead: the override is honoured ONLY inside the bounded pure path
probe's absent-shortcut and inside explicitly read/replay resolution helpers; EVERY issuing/minting/finalizing/
rederiving path resolves custody locators WITHOUT the override (original locator only, after the bounded probe).
Consequences: a false evidence record is impossible by construction (issuing never sees mapped roots); an issuing
run on a stalled mount gets the bounded probe's ABSENT outcome → the existing fail-closed refusal; the round-1
`custody_locator_override_mint_forbidden` guards become defence in depth and stay.

Do: (1) enumerate every function in the two modules that reads the override (grep `JOULEWISE_BACKUP_ROOTS`,
`_custody_probe_paths`, the lexical root replacement); classify each caller as read/replay or issuing using the
consult's entry-point table (trace 99ae §F1 and the issuance census in 99u); (2) make the resolution helper take an
explicit `mode` (`read_replay` | `issuing`), default `issuing` = NO mapping, and pass `read_replay` only from the
validators/replay/readers; `artifact_hashes` and every mint-side helper use `issuing`; (3) regressions: with a
non-empty override pointing at a scratch root that CONTAINS a planted candidate, (a) a read/replay entry finds it at
the mapped root, (b) `artifact_hashes` and each issuing helper hash/resolve the ORIGINAL locator (mapped root never
touched: count probes/opens on it = 0) and, if the original is absent, yield the absent outcome exactly as before;
(c) the round-1 refusal guards still fire where they exist; (4) the two delta sites (`_CaptureLedgerLifecycle.begin`,
`rederive_artifact`) are OUT of scope: state in the report which helper they call and that under this ruling those
calls resolve the original locator (verify by reading scripts/validate_powermetrics_fiducial.py, read-only; if they
call a helper you cannot make issuing-mode from within scope, return NEEDS_SCOPE naming the exact function).
Dated addendum to docs/contracts/calibration_ledger_append.md stating the read/replay-only rule. Acceptance = the
four modules (`tests.test_calibration_ledger_custody tests.test_calibration_bracketing tests.test_calibration_ledger
tests.test_authentication_io`) to a log with rc. Never the real iCloud path; never the repository-wide suite; no
`git commit`; header < 8192 bytes; genre implementation verdict keys.
