# 01f — Fix round 5 landed at `ccce8a61`; lead bench verification (magistrate b0ae8462, 2026-09-15 21:05 PDT)

Committed by pathspec on `feat/2026-09-15-install-windows-transactional` → `ccce8a61` (pushed). Lead diff read of all
four files: F1 cell asserts exit 3, the verbatim diagnostic, stdout empty, zero fake-launchctl calls, sidecar bytes and
mtime unchanged, directory mtime unchanged, no `<custody_root>/night` created; F3 production hunks are exactly the ruled
shape (constructor capture, handler-install recapture, handler-side `SIG_BLOCK`, `entry_mask` restored in `_unwind` and
`uninstall`); F2 prose matches lt-31's text in the runbook refusal table, §1.3 paragraph, the retained and
failed-restoration rows, §1.4, and NIGHT_HANDBACK (one nit: the sidecar sentence is now stated four times in the runbook;
accepted for pedagogy over concision).

Bench (rule 1, run by the lead in `wt-iw-txn` at `ccce8a61`, `nice -n 5`, seats running concurrently):
```
python3 -B -m unittest tests.test_night_agent_install.TransactionTests.test_retained_prior_refuses_without_writes tests.test_night_agent_install
Ran 38 tests in 268.268s — OK
python3 -B -m unittest tests.test_install_night_agent
Ran 47 tests in 28.013s — OK
```
Seat report 01e: RED/GREEN on the F3 reversion (1 failure RED, OK GREEN), both modules OK, early-refusal probe PASS
(retained-prior refusal before handler installation: rc 3, no AttributeError, entry mask preserved), `SCOPE_OK`.
