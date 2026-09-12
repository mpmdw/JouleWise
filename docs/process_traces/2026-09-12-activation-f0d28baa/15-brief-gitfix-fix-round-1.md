# Fix-round brief — GIT-FIXTURE-MAINTENANCE-SWEEP-01, round 1 (refuter 08 R1 + R2)

WRITE_SCOPE: ["tests/test_git_fixture_maintenance.py","tests/test_git_fixture_hygiene.py"]

You are a fix-round seat in the linked worktree you were started in (branch
`fix/2026-09-12-git-fixture-maintenance-sweep`, HEAD `68c4dd46`, one commit
over origin/main `ace4cc3c`). Read the refuter report
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/08-refuter-gitfix-astra-report.md`
(findings R1, R2) and the seat report `06-seat-gitfix-astra-report.md`
beside it. Fixture hygiene only; no product code; no change to any
pre-existing test assertion (kernel fence). Never run git commands that move
HEAD, never push, never touch `/Users/edr/code/JouleWise` or
`/Users/edr/JouleWise-measurement-20260913-derivation` (fenced). Use
`python3 -m unittest` (no pytest on this host). Do NOT edit
`tests/test_identity_pins.py` or any other module.

## R2 first (structure): ONE census home
`tests/test_git_fixture_maintenance.py:269` and
`tests/test_git_fixture_hygiene.py:26` both assert
`_git_init_violations(TESTS_ROOT) == {}`; the maintenance module already
asserted it at baseline (line 172). Keep the maintenance module as the ONE
repository-census home. Remove the duplicate `test_repository_census` from
the hygiene module; keep the hygiene module's adversarial scanner tests
(synthetic-source cases) — they test the scanner, not the repository.
If, after the removal, the hygiene module's remaining tests would be better
placed inside the maintenance module (one file for one mechanism), say so in
the report but do NOT move them this round.

## R1 (scanner gap): constant string concatenation
`cmd = ['git', 'in' + 'it']; subprocess.run(cmd)` escapes the census. Extend
the scanner's constant resolution to fold `BinOp(Add)` over string constants
(and constant-only tuples/lists joined the same way) so the case is caught,
and add it as a NEGATIVE case in the hygiene module's synthetic tests.
Counterfactual (defect-shaped): run the new negative case against the
scanner with the folding disabled (temporarily, in-memory or by a flag you
remove afterwards — the tree must end with no such flag) → the test must
FAIL; then enabled → PASS. Paste both result lines. Do not widen the scanner
to execute any scanned source.

## Verify
`python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q`
three consecutive times; paste the three result lines. Time the hygiene
module once (must stay under 30 s). `git diff --check`. Do NOT commit;
report `git status --short` and `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
R2 disposition with the deleted test name; R1 change (file:line) and the
counterfactual evidence; 3× results; any NEEDS_SCOPE/NEEDS_RULING. Under
8000 bytes.
