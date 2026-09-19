SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Refuter (read-only, CONTRACT lens) — lane QUIET-PREDICATE-EVIDENCE-01 (kernel 232) sampling harness, head `d066d271` vs base `7faaf2d0`

Cwd is a detached read-only worktree at `d066d271`. Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch. No network, no `sudo`, no `powermetrics`, no live `collect`. A measurement night is armed on this machine for 00:00 PDT: finish well inside your timeout and start no long-running process. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and `-B`; `pytest` is absent on the canonical 3.14 interpreter, use `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence`. Never run the canonical `python3 -m unittest discover`.

## What you are refuting

`git diff 7faaf2d0 d066d271` adds `scripts/sample_quiet_predicate_evidence.py` (1071 lines) and `tests/test_sample_quiet_predicate_evidence.py` (537 lines, 31 tests). It is the desk harness that lane 232 stage A uses to sample the quiet predicate (the night gate's "is the machine quiet" check) beside `powermetrics`, generate calibrated synthetic CPU load, and summarize evidence rows. The contract it must satisfy is the seat brief `docs/process_traces/2026-09-18-activation-d8ca3a36/11-brief-seat-harness-quiet-predicate-evidence.md` (deliverables D1–D8 and Rules) and the design consult `.../06-consult-lane-232-astra.md` §6 (harness spec), §3 (load generator), §5 (observer). The seat's own report is `.../13-seat-harness-astra.md`; do not trust it, check it.

## Contract lens — answer each with evidence (file:line you read, commands you ran)

C1. Deliverable coverage: for each of D1–D8 in brief 11, state MET / PARTIAL / MISSING with the function or CLI flag that implements it. A silently dropped or renamed deliverable is should_fix; a deliverable the report claims but the code lacks is blocker.
C2. "Imports, never copies" (brief 11 Rules): the module docstring claims it imports the actual smoke round (`run_night.py:2603-2712`), the framed transport (`quiet_admission.py:231-278`) and the adapter's rate-aware anchor (`powermetrics.py:1775-1785, 2009-2025`). Verify every cited line range against the code at `d066d271`; name each production symbol imported and any production logic re-implemented instead of imported. Re-implemented gate logic is blocker (the harness would then measure something other than the gate).
C3. Authority boundary: the harness must never be admission authority and must never write a cutoff into any plan or code. Grep for any path writing under `docs/`, `joulewise/`, `scripts/` other than its `--out`/`--log` targets, and any import of the harness from production. Any such coupling is blocker.
C4. Schema v1 row (D6): list the fields the code actually emits versus the brief's field list; a missing field or a unit mismatch (seconds vs ms, joules vs watts) is should_fix. Confirm `observer: true`-style labelling and PROVISIONAL labelling of outputs exist where the brief requires them.
C5. Alignment claims (D2): the docstring says no arrival-time or linear fallback is silently substituted and unresolved evidence stays null with the production reason. Find the code path and state whether a null bound carries a reason string in every failure branch.
C6. Census-clean condition (record 14 decision 3): the harness must record whether the round ran with an agent session alive (census result) in every row, so contaminated rounds cannot pass as clean. Confirm the row carries it and that `summarize` groups or labels by it.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; all evidence in the markdown body. Severity vocabulary: blocker / should_fix / nit. For every finding give the counterfactual input and the production call site or CLI invocation that shows it. If you find nothing, say so with the commands that would have found it.
