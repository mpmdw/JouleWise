# Wave 2 merge resolution — GIT-FIXTURE-MAINTENANCE-SWEEP-01

Date: 2026-09-04

Merge inputs:

- Mission HEAD: `e3050fd8511d2d3dd91f28cd8297f3b09afec242`
- Integration MERGE_HEAD: `ac7ca7f0e22e1806f0f085b81ca2988ba6780281`

## Hunk resolution

### `tests/test_issue_dg071_dg075_statistics.py` — producer-history fixture

Kept the integration side's complete reviewed
`test_producer_commit_on_axis_derived_history_pair` test, including its F2
history pair, unique timestamps, merge topology, unreachable-ref case,
add-only companion test, candidate-query assertions, values, and statuses.
The superseded mission-side history body was not duplicated.

Re-applied the mission's fixture-maintenance delta on top: retained the
`tests.git_fixture.init_git_fixture` import and changed only the integration
test's repository initialization from `git(checkout, "init", "--quiet")` to
`init_git_fixture(checkout, "--quiet")`. No assertions, expected values,
digests, statuses, registry rows, or `[FILL:...]` markers were changed.

Comparison with integration stage 3 shows exactly those two consistency edits:
the helper import and the initializer call replacement.

## Verification

Command:

```text
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_issue_dg071_dg075_statistics
```

Tail (exit 0):

```text
.............................
----------------------------------------------------------------------
Ran 29 tests in 1.871s

OK
```

Conflict-marker scan found zero markers. Both `git diff --check` and the scoped
command `git diff --check -- tests/test_issue_dg071_dg075_statistics.py`
exited 0, and
`python3 -m py_compile tests/test_issue_dg071_dg075_statistics.py` exited 0.

## Environment limitation

The resolved worktree bytes could not be staged because the managed sandbox
cannot create the linked-worktree index lock at
`/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fan-GIT-FIXTURE-MAINTENANCE-SWEEP-01/index.lock`.
Consequently Git still reports the test as `UU` even though its worktree file
contains no conflict markers. The magistrate must run
`git add -- tests/test_issue_dg071_dg075_statistics.py` (and add this report)
before committing the merge.
