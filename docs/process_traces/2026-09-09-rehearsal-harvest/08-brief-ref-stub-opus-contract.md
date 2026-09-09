# Refuter brief — NIGHT-GATE-STUB-CHAIN-01 @ bb7090e2b8d4cfe30effbfb7e89cef802277d448, CONTRACT lens (Opus, read-only)

Worktree (read-only): /Users/edr/code/JouleWise-wt-ref-stub-astra (detached at bb7090e2b8d4cfe30effbfb7e89cef802277d448). Diff: `git diff 83ab38ed..bb7090e2b8d4cfe30effbfb7e89cef802277d448`.
Contract: docs/process_traces/2026-09-09-rehearsal-harvest/01-brief-night-gate-stub-chain-astra.md in
/Users/edr/code/JouleWise-wt-magistrate-1ef89702 (the seat report is 02-… beside it).
Governing texts on this head: the class table and validate_receipt basis rules in joulewise/night_gate.py (ruled condition matrix,
pinned by test_the_class_table_matches_the_ruled_condition_matrix), docs/process/NIGHT_HANDBACK.md standing rules, the D-175 /
D-176 entries in docs/decision_log.md that define what a REHEARSAL_STUB receipt may and may not carry, and the receipt schema
consumers (grep joulewise/ and scripts/ for "unattended_night_receipt").
Questions:
1. Does the cure stay inside the contract (F1 gate-side only, no class-table or basis change, F2 defect-shaped tests with the stated
   counterfactual, F3 log line) — quote any deviation.
2. Does recording `chain_sha256: null` and a new `chain_stub` key in C5.measured conflict with any ruled receipt semantics or any
   documented consumer expectation (a doc that says C5 "chain identity passed" or lists the measured keys)? The C5 detail string
   "window, plan freshness, measurement HEAD, and chain identity passed" is now also emitted for the stub where chain identity was
   NOT checked — is that a should-fix or a nit under the governing texts?
3. Is anything in this diff a process-rule or contract amendment that rule 11 reserves to the cold gate or Ed? If so, name it.
4. Test adequacy: do the new tests pin the behaviour the contract names (no chain read for the stub; unconditional read retained for
   DIAGNOSTIC_NO_PACK; one-line bounded refusal log; unchanged non-refused form)? Any assertion that would still pass if the cure were
   reverted?
Output: findings ranked blocker / should-fix / nit with exact quotes, governing text, proposed correction; then "Checks that PASSED";
then a one-paragraph verdict. Read-only, no design proposals.
