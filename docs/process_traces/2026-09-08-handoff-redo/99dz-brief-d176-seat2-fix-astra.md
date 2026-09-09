WRITE_SCOPE: ["joulewise/night_gate.py","scripts/run_night.py","joulewise/t0_rehearsal.py","scripts/rehearse_t0_unattended.py","joulewise/arm_readiness.py","tests/test_night_gate.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_rehearse_t0_unattended.py","tests/test_arm_readiness_schemas.py","tests/test_magistrate_watchdog.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 2 — fix round (gpt-6-astra, HIGH, genre implementation)
Head 4b25d29f on feat/2026-09-08-d176-seat2-producer. The Astra execution delta (/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dy-delta-d176-seat2-astra-report.md)
is clean. Cure the Opus contract refutation at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99dx-ref-d176-seat2-opus-contract-review.md
findings 1–8 with these RULINGS (verify every line by reading the code):
1 (BLOCKER) contract §6 purpose table ~:495–500: rewrite rows 3–4 to the installed SIBLING_CHILD rule (a compliant
  rehearsal custody_root IS a child of night_custody_parent named by the prefixed ARM window id; equality, deeper
  nesting, another basename refuse; DISJOINT roles refuse any containment) and pin the S4 row (§9 :816) to the tests
  that bite each of the four table rows.
2 (BLOCKER, RULED) the night GATE is the authority for C1–C5: the fence lifts for ANY valid v3 plan carrying a
  `pack_night` object (no caller argument), and the gate EVALUATES C1 and C2 itself from the plan and the custody
  records (paths/bytes the driver passes), never copying driver-supplied ConditionRows. Amend §10 S2 only if the
  wording still needs it after the code matches it. Regressions: a watchdog/replay caller parsing a valid v3 pack
  plan no longer gets night_refused_class_unbuilt; a driver that passes a forged PASS row cannot make the gate PASS.
3 add one test pinning the SHIPPED configs/production_custody_inventory.json's four deployments (deleting one fails).
4 §9 rows B1/B5/S2/S3/S4/S6/N1: replace NOT PINNED/PARTIAL with the biting tests (the §10.3 appendix rows already
  name tests for S3/S6/N1 — move them up); every row's counterfactual must be one the named test actually asserts.
5 refusal attribution: the TRANSACTION_PACK refusal receipt's `refusal.reason` carries the TRUE cause code (courier
  unavailable, dead-man overrun, chain digest mismatch, chain already started…); `launch_go_receipt_invalid` is used
  ONLY for GO authentication/binding/validity failures per §3; regression per cause.
6 (RULED) only `measurement_root` must be wholly outside night_custody_parent; the other ARM-context roots
  (claim_runs_root, quarantine_root, both backup destinations, waiver_path) are checked by the DISJOINT predicate
  against every census role EXCEPT night_custody_parent — they may live under the rehearsal's own custody dir. Amend
  §6 :492–493 and scripts/run_night.py ~:1370–1374; regression: a rehearsal keeping runs/quarantine under its own
  custody dir passes; one under production custody refuses.
7 import readiness.ARM_CONTEXT_KEYS instead of re-hardcoding the four non-path keys (run_night.py ~:1352–1354).
8 restore §6's "and disjoint from production roots" + the ledger gloss "(the retained transaction event log)"; §3 :249
  "both flags" → the eight flags of §5; §7.1 records this seat's scope expansion (inventory json, rehearse script,
  its test, night_plan_writer test; test_arm_readiness_schemas shared with seat 3 for the resolver tests only); a v2
  plan carrying receipt_class TRANSACTION_PACK is a ruled refusal (night_plan_malformed) — add a watchdog test
  asserting that code rather than a crash (tests/test_magistrate_watchdog.py, additive).
Acceptance (rc-gated to a log): tests.test_night_gate tests.test_run_night tests.test_t0_rehearsal
tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas tests.test_night_plan_writer
tests.test_install_night_agent tests.test_magistrate_watchdog tests.test_docs_freshness; git diff --check; no commit;
header < 8192 bytes; report per finding with file:line and counterfactual.
