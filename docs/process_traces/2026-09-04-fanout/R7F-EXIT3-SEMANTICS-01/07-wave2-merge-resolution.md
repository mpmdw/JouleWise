# R7F-EXIT3-SEMANTICS-01 wave-2 merge resolution

Date: 2026-09-04

Mission head: `7008fbf014bf0d8eccb7f3412b1e22e9b1636f17`

Integration head: `ac7ca7f0e22e1806f0f085b81ca2988ba6780281`

Conflicted path: `tests/test_paper_round7_artifacts.py`

## Hunk disposition

| Hunk | Integration content kept | Mission delta reapplied | Result |
| --- | --- | --- | --- |
| `InvocationTests.test_absent_corpus_exits_three_and_names_path` terminal-line assertion | Kept the integration side's reviewed path normalization: isolate the terminal line, remove its stable prefix, resolve the reported and expected paths, and compare the two `Path` values. | Reapplied the mission's exit-3 vocabulary and structure: the stable prefix is `R7F REPLAY INCOMPLETE: source=preflight; reason=required_input_unavailable; detail=` rather than `R7F CORPUS UNAVAILABLE: `. | Exit 3 remains pinned to incomplete replay semantics while the assertion retains integration's symlink-safe path comparison. |

All non-conflicting edits were preserved by the merge. A method-name census found 51 unique tests on the mission side, 49 on the integration side, and 55 in the resolved worktree file; neither parent has a test absent from the result. No registry row, digest, status, value, or `[FILL:...]` marker was edited during this resolution.

## Verification

Command:

```text
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts
```

Tail:

```text
----------------------------------------------------------------------
Ran 55 tests in 610.652s

OK
```

`git diff --check` exited 0 with no output. A conflict-marker scan of the conflicted file returned no matches.

## Index note

The resolved worktree bytes could not be staged in this sandbox because the worktree index is stored at `/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-fan-R7F-EXIT3-SEMANTICS-01/index`, outside the writable roots. `git add -- tests/test_paper_round7_artifacts.py` failed with `Operation not permitted`; the magistrate must run that exact command before committing the merge.
