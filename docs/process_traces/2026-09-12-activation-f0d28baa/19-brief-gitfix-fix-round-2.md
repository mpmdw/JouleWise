# Fix-round brief — GIT-FIXTURE-MAINTENANCE-SWEEP-01, round 2 (delta re-audit 18 R3: overbuilt folder, 13 untested clauses)

WRITE_SCOPE: ["tests/test_git_fixture_maintenance.py","tests/test_git_fixture_hygiene.py"]

Fix-round seat in the linked worktree you were started in (branch
`fix/2026-09-12-git-fixture-maintenance-sweep`, HEAD `59873a5c`). Read the
delta re-audit `../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/18-refuter-gitfix-delta-astra-report.md`
in full (its per-cut table names 13 surviving cuts and the missing tests).
Fixture hygiene only; no product code; no change to any pre-existing test
assertion. Never move HEAD, never push, never touch `/Users/edr/code/JouleWise`
or `/Users/edr/JouleWise-measurement-20260913-derivation` (fenced).
`python3 -m unittest` only. Do not edit any other module.

## Direction: PRUNE first, then test what remains (not: test everything that exists)

The magistrate's overbuild judgement: the constant folder at
`tests/test_git_fixture_maintenance.py` ~:73 carries list/tuple folding and
type-preservation clauses that the audit shows no scanner test needs, because
the pre-existing recursive fallback already detects list/tuple command
fragments (that is WHY cuts C04-C07, C23, C26-C29 survive). Remove every
clause that is behaviourally redundant with the fallback; keep the folder at
the minimum that catches the R1 form (`'in' + 'it'`, nested string Add) and
whatever else a REAL evasion needs. Also remove the redundant integration
`Add` guard if C18 shows it is dead (or make it live and tested). For every
clause you KEEP, there must be exactly one selected test that fails when that
clause is cut. Run the audit's isolation procedure yourself over the final
folder (in-memory mutation, never edit the tree for it): one cut per clause,
`Ran N` and result per cut, all killed. Paste the table. Clause count before
→ after.

## Verify
`python3 -m unittest tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene -q`
three consecutive times; paste the three result lines. Real census must be
`{}` (paste). `git diff --check`. Do NOT commit; report `git status --short`
and `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Clauses removed (quote), clauses kept + their killing tests, the per-cut
table, 3× results, any NEEDS_SCOPE/NEEDS_RULING. Under 8000 bytes.
