# Refuter brief — GIT-FIXTURE-MAINTENANCE-SWEEP-01 landing (execution lens)

SESSION_MODE: delegated
WRITE_SCOPE: []

You are a READ-ONLY refuter (sandbox read-only; you may run tests, you may
not edit). Branch `fix/2026-09-12-git-fixture-maintenance-sweep` in this
worktree, one commit over origin/main `ace4cc3c`: `git diff ace4cc3c..HEAD`.
The seat's report is at
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/06-seat-gitfix-astra-report.md`
and its brief at `05-brief-git-fixture-maintenance-sweep.md` beside it. Never
touch `/Users/edr/code/JouleWise` or
`/Users/edr/JouleWise-measurement-20260913-derivation` (fenced).

Kernel row acceptance: "an enumeration test fails if a tests/ module creates
a git fixture repository without the four-key tuple, so the class cannot
regrow; every touched module green 3× at the bench". Fences: fixture hygiene
only, no product code, no change to any test's ASSERTIONS; the two
calibration-exits maintenance-ON sites are excluded by name.

Try to BREAK the landing. Specifically:
1. Fence check: does the diff change any assertion in `tests/test_identity_pins.py`
   or elsewhere? Quote any line that does.
2. Guard soundness: write (under /tmp, never in the tree) three synthetic
   modules that create a git repo WITHOUT the tuple in forms the report
   claims to catch (argv list, shell string, f-string) and one that routes
   through the shared helper; run the guard's census function against them
   (import it, or run the guard with a monkeypatched scan root) and report
   which are caught. Also try one evasion the census would plausibly miss
   (e.g. `cmd = ["git"] + ["init"]`, or `subprocess.run(" ".join(parts))`)
   and say whether it slips through; that is a should-fix, not a blocker,
   unless such a form already exists in `tests/`.
3. Double-guard: `tests/test_git_fixture_maintenance.py` ALREADY had an
   enumeration guard on the baseline (per the report). Is the new
   `tests/test_git_fixture_hygiene.py` a second home for the same rule? If
   both assert the same invariant, name which one should be the ONE home
   and what the other should drop (should-fix).
4. Runtime: time the new guard module once (`time python3 -m unittest
   tests.test_git_fixture_hygiene`); a scan >30 s is a should-fix.
5. Rerun `python3 -m unittest tests.test_identity_pins tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q` once; paste the result line.

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit, each with the reproducing command or the quoted
line; explicit "no blocker found" if none. Under 8000 bytes.
