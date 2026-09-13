# 40 — Lead bench run of the install (record for the refuter and the ledger)

Worktree `wt-arm-census` at the round-2 tree (committed as `4cd8929886256f1e36556732a2598e598d04e1e3`), 09:03–09:14 PDT, interpreter `/Users/edr/code/JouleWise/.venv/bin/python3`, real probes (this session can list processes; the seats' sandbox cannot). Firefox was open on the machine during the run.

```
----------------------------------------------------------------------
Ran 75 tests in 390.163s

OK
--- G4 verbose
G3 kills M8 (unchecked output) and M9 (reordered or missing probe). ... ok
[…]
test_g4_real_ruled_census_pgrep_dialect (tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect)
G4 kills M10: a construct pgrep rejects or silently never matches. ... ok
----------------------------------------------------------------------
Ran 4 tests in 13.353s
OK
--- related modules
OK
--- decoys gone?
       0
[exited with code 0]
```

Full module: see the first block (all tests, real probes). G1–G4 verbose: all ok. Related modules (integration, registry, schemas): OK. Decoys absent after the run.
