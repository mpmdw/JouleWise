# Delta re-audit brief — A177 fix round 1 (CI-red cure), execution lens

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter re-auditing ONLY the fix-round delta `git diff c85a171d..HEAD` (HEAD
`8a5d1169`, branch `fix/2026-09-12-fixture-sentinel-controller`, PR #324).
You may run tests (temp dirs allowed) but must not edit tracked files; the
tree must end clean. Reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
30 (fix brief with the CI failure text), 31 (fix report: root cause
"probable", cure = stress scoped to the bounded sentinel, 12× floor), 10
and 24 (the landing's refuters). Never touch `/Users/edr/code/JouleWise`
(read-only use of its `.venv/bin/python3` is allowed) or
`/Users/edr/JouleWise-measurement-20260913-derivation`. `python3 -m unittest` only.

Fix rounds introduce defects. Check:
1. Isolation rule: for every clause the delta adds or changes (the local
   adapter subclass that scopes stress, the 12× floor arithmetic, the
   reason-carrying assertion, any changed expectation), cut it one term at a
   time IN MEMORY and name one selected test that fails; `Ran N` + result per
   cut. A surviving cut on a clause that decides whether the regression can
   detect report 19's defect is a blocker.
2. Defect shape preserved: with the tree read-only, re-derive from the diff
   whether removing the bounded `--no-sleep` policy would still fail the
   regression (which assertion, with which reason) — the seat's V8 says
   TimeoutExpired / post_idle_unavailable / both strict mismatches. If the
   12× bounded stress could pass WITHOUT the cure on a fast host (i.e. the
   bounded capture finishes inside the 15 s timeout even while sleeping),
   show the arithmetic; a cure-independent pass is a blocker.
3. CI-red hypothesis: the seat could not run Linux. State what evidence in
   the delta would let the NEXT CI run explain itself if it fails again
   (the reason string in the assertion) — quote it; if the assertion still
   hides the reason, should-fix.
4. Same-signature statement: the landing's defect class was "host-timing
   fixture: stress applied to the wrong capture". Does the delta apply
   stress anywhere other than the bounded sentinel? yes/no with file:line.
5. Run `python3 -B -m unittest tests.test_controller -q` once with the venv
   interpreter and paste the result line.

Report (claude-codex-report/v1, genre review): per-cut table; findings
tiered blocker / should-fix / nit; explicit "no blocker found" if none; the
same-signature line. Under 8000 bytes.
