# Sol implementation report — fix round 11

Date: 2026-09-04. Starting and current committed HEAD: `b2800c6124c8baa754028e337ec314b7167810cd` on `feat/2026-09-03-magistrate-watchdog`; all round-11 changes are intentionally uncommitted. Authority: findings F1 and F2 with evidence in `28-delta-reaudit-round-10.md:111-113`. No install, canonical-checkout mutation, default-custody access, agent/session launch, production signal, email, or quiet-machine work occurred.

## Clause map

| Clause from trace 28 | Production/documentation site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| F1 — the reaper must survive both the documented job-control group-leader shape and a non-leader child shape, then proceed through the ladder | `docs/process/MAGISTRATE_WATCHDOG.md:157-163,183-248` | `tests/test_magistrate_watchdog.py:1425-1490` executes the exact heredoc bytes twice, forces the second child to be a process-group leader, and requires both receipts to contain the TERM/KILL snapshots and `verdict == "pass"` | Replace the conditional at `docs/process/MAGISTRATE_WATCHDOG.md:158-163` with unconditional `os.setsid()`; the group-leader subprocess exits 1 with `PermissionError: [Errno 1] Operation not permitted`. The mutation was executed and killed below. |
| F1 — the receipt must say which detachment path ran | `docs/process/MAGISTRATE_WATCHDOG.md:235-248` | `tests/test_magistrate_watchdog.py:1479-1490` distinguishes `new_session` from `already_process_group_leader` and pins the observed initial process group | Delete or swap either receipt label; the corresponding exact-value assertion fails. |
| F2 — step 0 binds the canonical checkout to the two-parent merge commit at `main` HEAD | `docs/process/MAGISTRATE_WATCHDOG.md:92-100` | `tests/test_magistrate_watchdog.py:1540-1555,1576-1609` pins the three merge-identity commands, creates an actual two-parent merge on `main`, and executes the extracted zsh block | Remove the branch, ref, or two-parent assertion; the exact-command assertion fails. |
| F2 — every one of the five working-tree files must hash identically to `git show "$merge_sha:$path"` | `docs/process/MAGISTRATE_WATCHDOG.md:100-113` | `tests/test_magistrate_watchdog.py:1547-1555,1577-1621` pins the comparison commands, requires two digest/path lines for each file, mutates one pinned working-tree file, and requires the exact block to fail | Compare to packet exhibits or omit the per-file equality test; the exact-command assertion fails or the in-test pinned-file mutation survives. |

## RED — tests before the runbook cure

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.ContractTests.test_documented_reaper_executes_for_both_process_group_shapes tests.test_magistrate_watchdog.ContractTests.test_documented_merge_commit_digest_gate_compares_all_five_files
```

Tail, exit 1:

```text
ERROR: test_documented_merge_commit_digest_gate_compares_all_five_files
StopIteration
FAIL: test_documented_reaper_executes_for_both_process_group_shapes
AssertionError: False is not true : the executable reaper must inspect its process group before detaching
Ran 2 tests in 0.004s
FAILED (failures=1, errors=1)
```

## RED mutation — unconditional setsid

The final test and runbook were copied under a fresh temporary directory; only that copy's conditional detachment block was replaced by unconditional `os.setsid()`. Command shape:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$mutation_dir:$repo" python3 -m unittest tests.test_magistrate_watchdog.ContractTests.test_documented_reaper_executes_for_both_process_group_shapes
```

Stable tail, expected test exit 1 while the enclosing mutation check exited 0:

```text
FAIL: test_documented_reaper_executes_for_both_process_group_shapes
AssertionError: 0 != 1 : Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
PermissionError: [Errno 1] Operation not permitted
Ran 1 test in 0.216s
FAILED (failures=1)
F1 unconditional-setsid mutation killed (test exit 1)
```

F2 carries its own executed counterfactual at `tests/test_magistrate_watchdog.py:1613-1621`: after the exact five-file comparison passes, one pinned checkout file is changed and the same block must exit nonzero.

## GREEN — focused red pair

```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.723s

OK
```

## GREEN — preflight-authorized module tails

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog`:

```text
...............................................................
----------------------------------------------------------------------
Ran 63 tests in 2.045s

OK
```

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_magistrate_watchdog`:

```text
........
----------------------------------------------------------------------
Ran 8 tests in 5.138s

OK
```

Only the two preflight-authorized modules were run. D-172 is compliant vacuously: `git diff -- scripts/magistrate_watchdog.py` is empty, so there is no changed production-script line requiring a subprocess-level test and RED mutation. The F1 documentation path nevertheless has both forms of evidence.
