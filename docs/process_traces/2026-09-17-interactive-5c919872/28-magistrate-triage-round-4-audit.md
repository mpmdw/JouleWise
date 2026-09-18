# Magistrate triage of the round-4 delta re-audit (record 27) — NIGHT-GATE-QUIET-ADMISSION-01 head 13d53ce2, 2026-09-18 00:5x PDT

Audit result (Astra xhigh, own interpreter `/opt/homebrew/opt/python@3.14/bin/python3.14`): F1–F6 landed; 11 of 12 mutants killed by their named tests; every operation on the tick path and on the expiry-to-receipt path ACCEPTED under cold-gate ruling 71's bar; same-signature statement: "No: none found after tracing every operation"; six modules 344 OK; generator PASS; reason codes and every `E`-derived constant unchanged.

## R1 — the one finding (audit-labelled BLOCKER by the literal "named mutant survives" clause)

Mutant: restore the `launch_done` predicate inside `poll_cleanup` (the round-3 shape). Named test `test_pending_exec_returns_receipt_then_launcher_reaps_late_child` PASSES with the mutant. Cause, per the audit: round 4 bounds the WHOLE cleanup by the 1 s budget measured from expiry on the monotonic clock, so a restored predicate can no longer hold the return path — the predicate is redundant, not harmful. The mutant that carries the property ("budget only when `jobs` is empty") is KILLED (external watchdog, `launch_pending`), as are "omit late kill" and all F4/F5/F6 mutants.

Triage: **equivalent mutant under the ruled bar** — the surviving mutant does not reintroduce any wait of the pre-drawn class, and the audit itself records "no forbidden wait demonstrated" and "R1 concerns a redundant mutant, not an external-progress wait". The literal severity clause in the audit brief (record 26: "a named mutant survives") was the magistrate's wording; ruling 71 Q2's stop condition refers to a surviving BLOCKER under the bar, and no operation of the pre-drawn class remains. The lane does NOT stop; no fifth round is inferred or run. Recorded here so Ed and any later gate can see the call and its basis; if a reviewer disagrees, the remedy is a one-line removal of the redundant predicate, which changes no behaviour.

## G1 — environment sensitivity (nonblocking, registered as a follow-up)

Two of the audit's six-module runs hit the `journal_block` external watchdog (178 s and 174 s) when the inherited `PYTHONPYCACHEPREFIX` pointed under `/tmp`; unsetting it made the suite green. The lead's native runs (96 s and 81 s) never hit it. Follow-up lane to register: TEST-BIND-SUPERVISION-ENV-SENSITIVITY-01 (P3): the journal-block test must not depend on the bytecode-cache location; find the coupling (likely the FIFO/barrier fixture path or the worker's interpreter startup under a cold cache) and pin it.

## Decision

Proceed to the PR at 13d53ce2 under the twelve-row gate once the full replay on this head (record 25) is green and the magistrate's own reading of the production diff is complete.
