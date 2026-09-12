# Delta re-audit brief — A177 after the rule-11 consult (report 39 design), execution lens, fresh refuter

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter re-auditing the consult round: `git diff 0ff8ac04..HEAD` (HEAD `74a547cd`,
branch `fix/2026-09-12-fixture-sentinel-controller`, PR #324) and, because
the regression was reshaped, the WHOLE regression as it now stands
(`git diff ace4cc3c..HEAD -- tests/test_controller.py`). You may run tests
(temp dirs allowed) but must not edit tracked files; the tree must end
clean. Reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
39 (the consult's design + 33-cut table — do NOT trust it; re-derive), 37
and 33 (the two prior delta audits whose classes this round must not
repeat), 30/31 (CI-red round). Never touch `/Users/edr/code/JouleWise`
(read-only use of its `.venv/bin/python3` allowed) or
`/Users/edr/JouleWise-measurement-20260913-derivation`. `python3 -m unittest` only.

1. Enumerate the clauses of the final regression yourself (every guard,
   record, expectation, arithmetic term beyond the pre-existing happy-path
   assertions); cut each IN MEMORY; selected test; `Ran N` + result. Any
   surviving decision-bearing cut is a blocker. Include: wiring removed;
   wiring removed + cure removed; each arithmetic operand of the
   stressed-duration inequality; the timeout formula terms.
2. Killed cut: cure (bounded `--no-sleep`) removed → must FAIL with
   report 19's signature; paste the reason lines.
3. Same-signature statement (own line): classes seen so far — "stress on
   the wrong capture (CI-red)", "unprotected stress wiring", "unprotected
   validator delegation". Does the final regression contain any clause of
   those classes, or a new unprotected class? yes/no + which.
4. Overbuild: any assertion killed by exactly the same single cut as
   another and by nothing else → should-fix naming the one to drop. Any
   host-dependent pinned value → should-fix with the bound to use.
5. CI-safety: confirm continuous captures run at 1x (quote) and nothing in
   the test sleeps in its own critical path.
6. `python3 -B -m unittest tests.test_controller -q` (venv) once; paste the
   result line; `git status --short` empty.

Report (claude-codex-report/v1, genre review): per-cut table; findings
tiered blocker / should-fix / nit; explicit "no blocker found" if none; the
same-signature line. Under 8000 bytes.
