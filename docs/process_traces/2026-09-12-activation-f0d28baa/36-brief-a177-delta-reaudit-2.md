# Delta re-audit brief — A177 fix round 2 (round-1 delta audit 33 R1 cure)

SESSION_MODE: delegated
WRITE_SCOPE: []

Refuter re-auditing ONLY the round-2 delta `git diff 8a5d1169..HEAD` (HEAD
`0ff8ac04`, branch `fix/2026-09-12-fixture-sentinel-controller`, PR #324).
You may run tests (temp dirs allowed) but must not edit tracked files; the
tree must end clean. Reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
33 (your round-1 delta audit: R1 and the cut table), 34 (round-2 brief), 35
(round-2 report: per-cut table, all R1 cuts now fail). Never touch
`/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3` is
allowed) or `/Users/edr/JouleWise-measurement-20260913-derivation`.
`python3 -m unittest` only.

1. Independently re-run the isolation procedure over the FINAL regression
   (enumerate the clauses yourself from the diff — do not trust report 35's
   list): every clause that decides whether the regression can detect
   report 19's defect gets one in-memory cut and one selected test; `Ran N`
   + result per cut. Include the combined cut (wiring removed AND
   `--no-sleep` removed) — it must FAIL. Any surviving decision-bearing
   cut is a blocker.
2. Same-signature statement (own line): round 1's class was "stress on the
   wrong capture (CI-red)"; round 2's was "unprotected stress wiring". Does
   the round-2 delta introduce either class again, or a third? yes/no +
   which.
3. Overbuild check (row 8): the regression grew by ~77 lines. Name any
   assertion that is redundant with another (two assertions that the same
   single cut kills and nothing else does) — should-fix with the one to
   drop; name any assertion that pins an incidental value (an exact count
   or wall time that will drift on another host) — should-fix with the
   bound to use instead.
4. Defect shape: re-run the killed cut (bounded `--no-sleep` removed, in
   memory) → must FAIL with report 19's signature; paste the reason lines.
5. Run `python3 -B -m unittest tests.test_controller -q` once with the venv
   interpreter; paste the result line. Confirm `git status --short` empty.

Report (claude-codex-report/v1, genre review): per-cut table; findings
tiered blocker / should-fix / nit; explicit "no blocker found" if none; the
same-signature line. Under 8000 bytes.
