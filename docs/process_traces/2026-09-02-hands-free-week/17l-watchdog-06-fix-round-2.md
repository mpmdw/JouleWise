# Magistrate watchdog — Sol fix round 2

Date: 2026-09-03 PDT  
Base/HEAD at intake: `b93f5ffb`  
Branch: `feat/2026-09-03-magistrate-watchdog`  
Install/session/commit actions: none.

## Finding → cure → test

| Finding | Cure | Biting test / evidence |
|---|---|---|
| F1 blocker — matching `notice.ack` could survive a child exit | The resident consumes the acknowledgement before polling the child and before the child-exit return. The cleared queue is persisted before exit classification. | `test_notice_ack_is_consumed_before_child_exit` pins empty in-memory and persisted `notice_pending` plus absent `notice.ack`. |
| F2 blocker — synchronous GitHub probing could spend 20 seconds before plan enforcement | The launchd decision records its probe result. The resident resolves clock and plan enforcement before consulting that cache; a single daemon thread refreshes it at most every five minutes and never overlaps another refresh. Local `STOP` remains a synchronous local-file check. | `test_sleeping_remote_probe_cannot_delay_plan_term_or_kill` holds an injected probe in `sleep(30)` while TERM and KILL both execute in less than 10 seconds total. |
| F3 — contract refuter read file-15 row 6 as narrower than the code | Kept `refs/heads/ops/stop*`, per the magistrate's adopted ruling on execution-refuter N2. The operator guide now names that source, and the landing report carries a dated amendment. | `test_stop_glob_catches_shortened_magistrate_branch_name`; documentation and clause-map inspection. |
| F4 — bench instructions were not runnable | Added exact temp-custody `t0=now+10m` dry-run commands and expected decisions; an exact no-TTY replay citing file 02; and the lead-controlled first-tree adoption sequence naming the Terminal-hosted interactive twin, `claude daemon`, spares, and before/after census. | Documentation inspection. The implementation seat did not execute an install, launchd action, twin stand-down, or session start. |
| F5 — resident omitted clock uncertainty | The resident now calls the shared `clock_uncertain` detector before plan arithmetic. Detection irreversibly requests a conservative drain for that activation; TERM/KILL elapsed time is monotonic, and a later launch resets the completed drain flag. | `test_clock_uncertain_resident_drains_with_monotonic_deadlines` pins `CLOCK_UNCERTAIN`, request, monotonic TERM, and monotonic KILL. |
| F6 nit — atomic temporary names absent from write inventory | Documented `.<target>.<pid>.<uuid>.tmp`, including the crash-orphan case. | Documentation inspection against `Storage.atomic_bytes`. |

No other nits are listed in `05-refuter-contract.md`.

## Focused verification

Preflight command, before edits:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog
```

Exit 0 tail:

```text
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.075s

OK
```

Final replay used the same command. Exit 0 tail:

```text
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.075s

OK
```

Compilation command used an external cache so it wrote no repository bytecode:

```sh
compile_cache="$(mktemp -d "${TMPDIR:-/tmp}/watchdog-fix2-pycompile.XXXXXX")"
PYTHONPYCACHEPREFIX="$compile_cache" python3 -m py_compile scripts/magistrate_watchdog.py
```

Exit 0, no diagnostic. The final executed cache root was `/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T//watchdog-fix2-final-pycompile.fkhkSW`.

Per the runner's preflight rule, no other test module and no discovery suite ran. One development replay initially exposed an old injected fixture that advanced wall time by nine minutes while holding monotonic time fixed; with resident clock checking now live, that correctly entered `CLOCK_UNCERTAIN`. The fixture was corrected to advance both clocks equally, then the final replay above passed.

## Mutation probes

The three execution-refuter mutations were rerun against separate restorations of the final watchdog and focused test under `/private/tmp/watchdog-fix2-final-mutations.dZR6WE-*`. Every mutated replay used `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog` and exited 1 as required.

| Mutation | Failing test name(s) |
|---|---|
| Ignore failed remote positive control | `test_stop_branch_present_absent_and_positive_control_failure` |
| Flip the belt's closed start boundary to open | `test_fixed_belt_is_half_open` |
| Delete the plan `_write_request` step | `test_cooperative_exit_after_request_never_signals`; `test_ignored_request_gets_term_then_kill_and_census` |

## Scope and residual gates

Only runner-authorized paths were modified. No commit was created, no package was installed, and no Claude or Codex session was started. The no-TTY transcript in file 02 is cited rather than rerun, and the new adoption procedure is an owed lead-controlled bench because it intentionally stands down the live twin. Final installed-launchd, twin-census, and delta re-audit authority remains with the lead.
