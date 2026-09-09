WRITE_SCOPE: ["joulewise/calibration_ledger.py","tests/test_calibration_ledger.py","tests/test_calibration_ledger_custody.py"]

# Seat brief — ICLOUD-CUSTODY-LOCATOR-01 (gpt-6-astra, medium)
Opus review trace docs/process_traces/2026-09-08-handoff-redo/47-ref-icloud-opus-contract-review.md C8 (static
finding): `joulewise/calibration_ledger.py` ~4650-4658 `_custody_state()` calls `path.exists()`/`is_dir()` on tracked
fixture `custody_locator` values that point under the iCloud path
`/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/...` with no time budget; an unresponsive
iCloud mount blocks forever with zero CPU (seen twice on 2026-09-08 in the paper producers, cured there by
ICLOUD-BACKUP-PROBE-01, main c9e2981c: a 2 s daemon-thread budget + `JOULEWISE_BACKUP_ROOTS` override — read that
helper in scripts/paper_excursion_decomposition.py as the reference shape). Do: (1) find every filesystem probe of a
`custody_locator` (grep) and bound each with the same budget semantics — a timed-out probe must yield exactly the
state an ABSENT locator yields today (verify from the code what that state is and say so; never a new state that
changes a ledger verdict); (2) honour `JOULEWISE_BACKUP_ROOTS` (empty = treat backup-rooted locators as absent
without probing) where a locator lies under a default backup root; (3) regressions: blocked probe returns within
budget with the absent-equivalent state; override empty → no probe; existing custody tests unchanged; (4) name
which tests/fixtures reference the iCloud path (`grep -rn CloudDocs tests/fixtures | head`) and confirm none of
them are touched. Acceptance = the touched test modules to a log with rc (name them). Never touch the real iCloud
path; never the repository-wide suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys.
NEEDS_SCOPE if the probe lives elsewhere.
