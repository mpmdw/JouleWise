SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Refuter brief — NIGHT-GATE-STUB-CHAIN-01 @ bb7090e2b8d4cfe30effbfb7e89cef802277d448 (branch fix/2026-09-09-night-gate-stub-chain), EXECUTION lens (gpt-6-astra, medium, genre review, read-only)

Diff under review: `git diff 83ab38ed..bb7090e2b8d4cfe30effbfb7e89cef802277d448` (joulewise/night_gate.py, scripts/run_night.py, tests/test_night_gate.py, tests/test_run_night.py).
Forcing defect: the live stub night rehearsal-20260909 produced receipt.json verdict REFUSED reason night_probe_error because
evaluate_night read plan.chain_path for every receipt class while the driver substitutes a built-in stub for REHEARSAL_STUB and the
stub arm never writes chain.zsh. Cure contract: docs/process_traces/2026-09-09-rehearsal-harvest/01-brief-night-gate-stub-chain-astra.md
(read it). Seat report: 02-seat-night-gate-stub-chain-astra-report.md in the same directory.

Try to BREAK the cure. Specifically:
1. Every non-stub class (DIAGNOSTIC_NO_PACK, TRANSACTION_PACK) must keep the unconditional chain + sidecar read and every sidecar
   defect check byte-for-byte: diff the else-branch against the pre-cure block with `git diff -w` and state whether any token changed.
2. Receipt validity: with the stub's C5 measured now carrying null values and a new key, does `validate_receipt` and the consumer
   path (scripts/run_night.py, any night-results/courier consumer that parses receipt.json — grep for readers of "measured") still
   accept it? Run the scoped modules and any consumer test module you find, to a log with rc.
3. Is there any OTHER place that assumes a REHEARSAL_STUB plan has a readable chain (install_night_agent.sh, night_plan_writer,
   preflight, scripts/run_night.py stub branch, docs/process/NIGHT_HANDBACK.md standing rules)? Name each with line numbers; a residual
   reader that would still refuse on a real stub arm is a BLOCKER.
4. The driver log change: confirm the non-refused line form is unchanged, the refused form is exactly one line, and that
   `_refusal_from_object` is defined before use in the module. Check the new driver tests actually exercise the modified line (not a
   mock of it).
5. Run the counterfactual yourself: check out the two new gate tests onto 83ab38ed's night_gate.py in a scratch copy (e.g. copy the
   file to /tmp and monkeypatch, or `git stash`-free: `git show 83ab38ed:joulewise/night_gate.py > /tmp/ng_base.py` and import it
   under a different name) and confirm the stub test FAILS with night_probe_error pre-cure and the diagnostic test PASSES pre-cure.
6. Pre-existing behaviour surfaced by the seat: the driver returns EXIT_REFUSED for a REHEARSAL_STUB night even with verdict
   REHEARSAL_ONLY (test_stub_without_chain_files_logs_rehearsal_only asserts it). Is that pinned by an existing test or ruling on
   this head? Report it as an observation with the evidence, do not judge it.
Do NOT edit any repository file. Report as claude-codex-report/v1, genre review, header < 8192 bytes; body = findings ranked
blocker / should-fix / nit with exact quotes, commands run and their tails, and the list of checks that passed.
