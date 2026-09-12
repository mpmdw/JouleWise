# Delta re-audit brief — GIT-FIXTURE-MAINTENANCE-SWEEP-01 fix round 1

SESSION_MODE: delegated
WRITE_SCOPE: []

You are a refuter re-auditing ONLY the fix-round delta. You may run tests
(temp dirs are allowed in this sandbox) but must not edit any tracked file;
the tree must end byte-identical (`git status --short` empty). Branch
`fix/2026-09-12-git-fixture-maintenance-sweep`; the landing is `68c4dd46`
(reviewed by refuter report 08); the fix round is HEAD: `git diff 68c4dd46..HEAD`.
Reports beside this brief in
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
08 (refuter, findings R1/R2), 15 (fix brief), 16 (fix report). Never touch
`/Users/edr/code/JouleWise` or `/Users/edr/JouleWise-measurement-20260913-derivation`
(fenced). `python3 -m unittest` only.

Fix rounds introduce defects. Check, in this order:
1. Isolation rule: for EVERY clause the delta adds or changes in the census
   (the constant-folding function at `tests/test_git_fixture_maintenance.py`
   ~:73 and its integration ~:123), cut it one term at a time IN MEMORY
   (monkeypatch, never edit the tree) and name one selected test per cut
   that fails; report `Ran N` and the result line per cut. A clause with no
   killing test is a should-fix (name the missing test).
2. Did the R2 deletion remove the ONLY census over the real `tests/` tree,
   or does `tests/test_git_fixture_maintenance.py` still assert
   `_git_init_violations(TESTS_ROOT) == {}` (quote the line)? If the real
   tree is now unscanned, blocker.
3. Folding safety: can the new folding produce a false POSITIVE on an
   existing `tests/` module (a non-git command that folds to something
   containing `init`)? Run the real census once and paste the violation
   dict (must be `{}`).
4. Fence: no pre-existing assertion changed (compare assertion ASTs of the
   retained tests between 68c4dd46 and HEAD, or diff them by eye and quote).
5. Run `python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene tests.test_identity_pins -q` once; paste the result line.

Report (claude-codex-report/v1, genre review): per-cut table for step 1;
findings tiered blocker / should-fix / nit; explicit "no blocker found" if
none. Under 8000 bytes.
