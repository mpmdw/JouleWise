WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on ICLOUD-CUSTODY-LOCATOR-01 (gpt-6-astra, read-only)
HEAD = fix-round commit; HEAD~1 = 42b0d235 part-3 landing (Astra execution refuter clean; Opus SF-1..SF-4). Packet:
`git diff HEAD~1 HEAD`. Claims: SF-1 timeout/exception probes emit a distinguishable stderr diagnostic
(`custody_locator_unreachable …`) with absent-equivalent decisions and receipt fields unchanged; SF-2 docstring;
SF-3 dated docs; SF-4 a NON-EMPTY `JOULEWISE_BACKUP_ROOTS` refuses issuance before hashing with
`custody_locator_override_mint_forbidden`, empty override unchanged; N-1 wrappers moved back adjacent to their
bodies with EXACTLY eight line-number entries refreshed in tests/test_authentication_io.py
`CLASSIFIED_NON_AUTHENTICATION_READS` (classified operations unchanged); N-2 `probe_custody` exported; N-4 constant
test replaced. Break it: (1) absent-equivalence must still hold: re-run the 16 comparisons (8 entry points × exists/
is_dir blocked) — serialized outcomes identical to genuine absence, and the diagnostic goes to stderr ONLY (no
receipt/log field changed: diff the structures); (2) SF-4: enumerate every minting/issuing path that calls
`artifact_hashes` or hashes custody bytes (grep callers incl. scripts/validate_powermetrics_fiducial.py) and confirm
each refuses under a non-empty override BEFORE any write; confirm read/replay paths still honour the override;
(3) the eight pin refreshes: `git diff HEAD~1 HEAD -- tests/test_authentication_io.py` must change only line
numbers of ledger entries (same operations, same count); verify each new line number points at the same operation
(`sed -n` the target lines); (4) `git diff HEAD~1 HEAD -- joulewise/authentication_io.py` empty; no worker touches
anything but exists/is_dir; (5) mutation: drop the SF-4 refusal and the SF-1 diagnostic separately in a $TMPDIR copy,
confirm the named regressions fail; (6) anything HEAD~1 had right that HEAD broke. Never touch the real iCloud path;
run only the four modules. Report (genre review): `verdict` = {counts, findings}; header < 8192 bytes.
