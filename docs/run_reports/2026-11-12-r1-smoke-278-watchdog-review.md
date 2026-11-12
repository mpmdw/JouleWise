# R1 smoke watchdogs off ITIMER_REAL (RUN_STATE 278): executing cold delta review

Reviewer: Claude Fable 5.2, independent executing seat (did not write the change; Opus built it). Written 2026-11-12 00:11 PST on the analysis Air. Blind: code, review text and wall-clock durations only; no v4, Block 6 or BYTES outcome and no energy or power value was read.

Target: `fix/2026-11-11-r1-smoke-278` @ `4365d9d6fa9c84129db94e6e691c61b5ee8d11aa`, parent `9c5ba057e`. RL-84 P-5 requires this delta review before the smoke because the change alters executed bytes of `joulewise/align/apple/r1_runtime.py` (condition 13).

## Verdict: ADMIT-WITH-FIXES

**The executed bytes are admitted as they stand. Nothing in this review blocks the fourth smoke.**

The one fix is test-only and touches no condition-13 file. The committed suite does not kill "the handler does not raise", which is one of the required mutants: no test drives the real `smoke_timeout` handler and checks that the run fails (F-1). Two related mutants also survive. I checked the behaviour itself by execution: at the head a fired watchdog fails the run with exit 3 and the wall-cap record, in and out of a deadman guard. Three witnesses that kill the survivors are in the appendix; they pass at the head.

The fix does what smoke 278 needed. The episode deadman is the only `ITIMER_REAL` owner, the real guard arms under both smoke watchdogs, and the night path is unchanged.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | Night path unaffected | **Pass.** With the smoke-guarded blocks, the new class and the new constant removed, the two ASTs differ in one statement, a pure read. A FakeWorld follow-up night and a non-smoke `rt.main` give byte-identical probe output at parent and head. |
| 2 | SIGUSR1 safety | **Pass, one item not executable here.** No other SIGUSR1/SIGUSR2/`pthread_kill`/`faulthandler` use in any tracked code. MLX is not installed on the Air, so its native library was not inspected (F-5). |
| 3 | Thread and signal semantics | **Pass.** Fires exactly once; interrupts blocking calls as SIGALRM did; no worse on native calls; re-arm, replace, disarm and stop behave; nothing is sent after `stop()`; the daemon thread does not hold the process or reach children. One narrow window at teardown (F-3). |
| 4 | Deadman coexistence | **Pass.** Both orders constructed through `rt.main`: deadman first reports `DeadmanExpired`, watchdog first reports the smoke wall cap. See F-2 for the workload's `except Exception`. |
| 5 | Fail-first | **Pass.** `SmokeTimerOwnerTests` on the parent runtime: 3 failures with "the smoke stole the deadman's timer", 4 errors for the missing class. Green at the head. The test uses the real `EpisodeDeadman.guard` on a `SystemClock`. |
| 6 | Mutants | **Partly.** 13 of 17 killed, 5 of the 7 required. "Handler not raising" survives (F-1). "Signal to the process" survives because the difference cannot be observed on this macOS. |
| 7 | Tests | **Pass.** Ten modules green and one all-skipped; `test_r1_runtime` fails the same 9 as the parent. |
| 8 | Post-smoke test branch | **Test-expectation change, not a regression.** One subcase fails as the author said. The branches also conflict textually. Rewrite below. |
| 9 | Binding | **Pass.** Engineering watchdog under RL-84 P-5. `budget.py`, `g0_timeout_s`, caps and the launch minimum are unchanged. No pin or plan_tree to regenerate. |

## Night path (check 1)

- **Static.** I parsed `r1_runtime.py` at parent and head, dropped every `if` whose test names `smoke_part` (keeping its `else`), dropped `class SmokeWatchdog` and the `SMOKE_WATCHDOG_SIGNAL` assignment, and compared the unparsed trees. The same six smoke guards are removed on both sides. One statement differs:
  `previous_alarm = signal.getsignal(signal.SIGALRM)` became `previous_smoke_signal = signal.getsignal(SMOKE_WATCHDOG_SIGNAL)`.
- **Why that one line is safe.** `signal.getsignal` reads Python's handler table and changes nothing. The value is used only inside `if args.smoke_part:` in the `finally`. On the night path the old line's result was never used either, so dropping the SIGALRM read loses nothing. `budget.py` is byte-identical.
- **The night driver never passes the flag.** `--smoke-part` and `--smoke-started` are built in one place, `scripts/align_r1_followup_kit.py:294`, inside `smoke()`. Only `r1_runtime.py`, its contract doc and two test files changed in this diff.
- **Executed, parent against head.** One script, run in each tree, output compared with `cmp`: identical.
  - A full follow-up night under `FakeWorld` (`align_r1_rehearsal.run`, synthetic): return code 0, the same 19 segment lines, 108 recorded argvs with the same SHA-256 after replacing the temp root, and no argv carries `--smoke-part` or `--smoke-started`. Thread list and SIGUSR1 disposition are the same before and after.
  - `rt.main` for `step-d` and `step-30b` with no smoke flag, with a real `EpisodeDeadman.guard` on a `SystemClock` inside `run()`: exit 0; the only thread is `MainThread` during and after the run; `signal.signal` is called for SIGTERM, SIGINT, SIGHUP (install and restore) and SIGALRM twice (the deadman's own arm and restore), never for SIGUSR1; `setitimer` is called twice, the deadman's 7 s and its 0. SIGUSR1 stays at `SIG_DFL` throughout.

## SIGUSR1 safety (check 2)

- `git grep` over every tracked file for `SIGUSR`, `USR1`, `USR2`, `pthread_kill`, `faulthandler`, `set_wakeup_fd`, `pthread_sigmask`, `sigwait`: outside old process-trace documents, the only hits are this change and its contract paragraph. The one existing `pthread_kill` in the runtime (`close_managed_session`) re-sends a held SIGTERM/SIGINT/SIGHUP, never SIGUSR1.
- Every `signal.signal` call in the runtime, the kit, the smoke runner, the launcher, `run_night.py`, `b5/driver.py`, `thermal`, `smc_enumeration`, and `km003c_monitor.py` installs handlers for SIGTERM, SIGINT, SIGHUP or SIGALRM only. The meter is a separate process and handles only those three termination signals. Nothing in the repo sends a signal other than TERM, KILL, STOP, CONT or the held termination signals.
- So nothing else can trigger the new handler, and the handler takes no signal another component needs. An outside `kill -USR1` during a smoke would now fail the smoke with the wall-cap message; before this change it would have killed the runtime outright (default action). On the night path it still kills it, as before.
- Children do not inherit the handler: `exec` resets a caught signal to default. A Python child started while the watchdog was armed reported SIGUSR1 at default, an empty signal mask and one thread.

## Thread and signal semantics (check 3)

All executed against the head's `SmokeWatchdog` on Python 3.13.18.

| Question | Result |
|---|---|
| Exactly once | One `set(0.05)`, watched for 2.5 s across the thread's 1 s wake cap: one handler call, `deadline` back to `None`. |
| Blocked in `time.sleep`, `Popen.wait`, `Event.wait`, `os.read` on a pipe | Interrupted 0.20 s after a 0.2 s `set` in each case. `pthread_kill` to the main thread returns the syscall with EINTR and Python runs the handler at once. |
| Native call that releases the GIL (about 1.9 s) | Handler runs when the call returns: 1.65 s, against 1.69 s for the old `ITIMER_REAL` on the same call. |
| Native call that holds the GIL (about 5.8 s) | Handler runs when the call returns: 6.3 s, against 5.9 s for the old itimer. One trial each; I did not repeat it to separate the 0.4 s from the call's own spread. |
| `set(0)` after `set(n)` | No fire. |
| `set(0)` then `set(n)` | Fires at `n`. |
| `set(5)` then `set(0.15)`; `set(0.1)` then `set(5)` | The later call replaces the deadline both ways. |
| After `stop()` | No send, thread joined and dead, `active` false. |
| Process exit with the watchdog armed and never stopped | Exits at once, return code 0. The thread is a daemon. |

Neither design can interrupt a long native call: Python runs a signal handler only when the main thread returns to the interpreter. The new one adds one step, since the watchdog thread needs the GIL to send, and a main thread busy in pure Python gives it up within the 5 ms switch interval. That is not worse in any way that matters for a 2,600 s or 3,000 s cap. The launcher's part caps remain the backstop for a native hang, as they were.

**`stop()` racing a fire.** 20,000 rounds with sub-millisecond deadlines and `main()`'s exact teardown order (`stop()`, then restore SIGUSR1 to `SIG_DFL`): 38 fired in the body, 63 raised inside `stop()` before it cleared `active`, none raised after `stop()` returned, and the process never died from a late signal under the restored default. The send happens under the same lock `stop()` takes, so once `stop()` holds it no further signal is sent. The 63 are finding F-3.

**Process-directed delivery (mutant M5).** With four extra idle threads, `os.kill(getpid(), SIGUSR1)` interrupted the main thread's sleep 40 times in 40, the same as `pthread_kill`. On this macOS the kernel picks the main thread. POSIX does not promise that, and the runtime has sampler threads, so `pthread_kill` is the right call; the difference is not observable in a test here.

## Deadman coexistence (check 4)

Three runs through `rt.main --r1-kind step-d --smoke-part B` with a fake `Segment` whose `run()` arms the post-G0 watchdog and then enters a real `EpisodeDeadman.guard` (`SystemClock`) around a 6 s sleep.

| Order | In the guard | Outcome |
|---|---|---|
| Deadman 0.4 s, watchdog 3 s | `ITIMER_REAL` 0.4 s, SIGALRM handler `expire`, SIGUSR1 handler `smoke_timeout` | Raised at 0.41 s. Exit 3, custody `failed`, error `DeadmanExpired`. Watchdog still armed with 2.59 s left, then stopped by `main`. |
| Watchdog 0.4 s, deadman 5 s | `ITIMER_REAL` 5.0 s, same handlers | Raised at 0.41 s. Exit 3, custody `failed`, error `RuntimeFailure: smoke part wall cap reached; partial smoke is not a pass`. The guard's `finally` cleared the itimer and restored SIGALRM. |
| Watchdog 0.4 s, deadman 5 s, caught by an `except Exception` shaped like `workload.py:660` | same | Recorded as `episode_error:RuntimeFailure:smoke part wall cap reached; ...`. No second fire. See F-2. |

After each run: `ITIMER_REAL` is (0, 0), SIGUSR1 is back at `SIG_DFL`, and only `MainThread` is alive.

In the real Part B the second and third rows cannot occur inside the episode. The deadman is re-armed after the quiet for `rearm_s`; the watchdog is set at G0 release to quiet + `rearm_s` + 600 + 120. The deadman's deadline is therefore 720 s ahead of the watchdog's, and any guard entered after it raises `DeadmanExpired` at once. The watchdog can only fire in the recovery and close that follow the episode, which no guard covers.

## Fail-first (check 5)

The head's `tests/align/test_r1_smoke_launcher.py` with the parent's `r1_runtime.py`, `SmokeTimerOwnerTests` only: 4 tests, 3 failures and 4 errors.

- `test_part_b_post_g0_turn_arms_the_real_episode_deadman`: FAIL, `the smoke stole the deadman's timer: ALIGN deadman cannot replace an active timer`. This is smoke 278's failure, reproduced.
- `test_pre_g0_guarded_call_runs_under_the_smoke_admission_watchdog`, parts A and B: FAIL, same message, exit 3.
- The other two tests error on the missing `SmokeWatchdog` and `SMOKE_WATCHDOG_SIGNAL`.

The guard is the real one: the test builds `EpisodeDeadman(SystemClock(), …)` and enters `deadman.guard()` with nothing patched in `budget.py`. At the head it reads the live itimer inside the guard (between 1,500 and 1,580 s) and checks the watchdog is still armed off the itimer.

## Mutants (check 6)

Each mutant was applied to a scratch worktree's `r1_runtime.py`, then `tests.align.test_r1_smoke_launcher` and `tests.align.test_r1_round3` were run.

| Mutant | Required | Result | Killed by |
|---|---|---|---|
| M1a post-G0 watchdog back on `ITIMER_REAL` | yes | Killed | `test_part_b_post_g0_turn_arms_the_real_episode_deadman`, the Part A stop test, round 3's installed-budget test |
| M1b admission watchdog back on `ITIMER_REAL` + SIGALRM | yes | Killed | `test_pre_g0_guarded_call_runs_under_the_smoke_admission_watchdog`, `test_runtime_pre_g0_watchdog_is_the_admission_budget` |
| M1c `SMOKE_WATCHDOG_SIGNAL = SIGALRM` (thread kept) | extra | **Survived** | none. The guard would swap out the handler, so a cap inside a guard would read as `DeadmanExpired` |
| M2 `set(0)` keeps the old deadline | yes | Killed | `test_watchdog_fires_once_on_the_main_thread_and_disarms_and_stops` |
| M3a `stop()` does nothing | yes | Killed | the same test, and the pre-G0 guarded-call test |
| M3b `stop()` leaves the thread and deadline | extra | Killed | the same two |
| M3c `main` never calls `stop()` | extra | Killed | the pre-G0 guarded-call test, the admission-budget test |
| M4 handler does not raise | yes | **Survived** | none (F-1) |
| M4b handler raises even after `stop()` | extra | **Survived** | none (F-1) |
| M5 signal sent with `os.kill(getpid(), …)` | yes | **Survived** | none; not observable here (see check 3) |
| M6 watchdog created on the non-smoke path | yes | Killed | `test_runs_without_a_step_d_smoke_part_start_no_watchdog_and_touch_no_timer` |
| M6b SIGUSR1 handler changed on the non-smoke path | extra | Killed | the same test |
| M7 Part A does not disarm after G0 | yes | Killed | `test_g0_released_after_1800_s_but_inside_budget_admits_and_stops_part_a` |
| M8 fires on every loop pass | extra | Killed | `test_watchdog_fires_once_…` |
| M9 never sends | extra | Killed | `test_watchdog_fires_once_…` |
| M10 SIGUSR1 handler not restored by `main` | extra | Killed | the pre-G0 guarded-call test |
| M11 Part B post-G0 budget never set | extra | Killed | the Part B deadman test, the Part A stop test, round 3 |

Does M5 matter? In behaviour, not on this host: process-directed delivery reached the main thread 40 times in 40 with four other threads alive. In principle it does, because POSIX lets the kernel pick any thread that has the signal unblocked, and a signal landing on another thread would not interrupt the main thread's blocking call (the handler would run only when that call returned). `pthread_kill` removes the dependence. I would not add a test for it.

## Tests (check 7)

One module at a time, `nice -n 10 python3.13 -B -m unittest`, at the head. Internal disk stayed at 29 GB free or more.

| Module | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 45 tests, OK |
| `tests.align.test_r1_followup` | 12 tests, OK |
| `tests.align.test_r1_round7_science` | 18 tests, OK |
| `tests.align.test_r1_round3` | 8 tests, OK |
| `tests.align.test_v4_registration` | 24 tests, OK |
| `tests.align.test_v4_executed_closure` | 6 tests, OK |
| `tests.align.test_v4_dynamic_closure` | 10 tests, OK |
| `tests.hazards.test_refusal_allowlist` | 24 tests, OK (1 skipped) |
| `tests.align.test_decode_budget` (decode budget and `EpisodeDeadman`) | 21 tests, OK (1 skipped) |
| `tests.align.test_thermal_gate` | 44 tests, OK |
| `tests.align.test_thermal_mlx` | 2 tests, both skipped (no MLX on the Air) |
| `tests.align.test_r1_runtime` | 33 tests, 7 failures and 2 errors: the same 9 tests as at the parent, with the same messages once paths, digests and timestamps are masked |

## Post-smoke test branch (check 8)

`ops/2026-11-11-r1-post-smoke-tests` @ `0ffcd22e7` branches from the same parent. I ran its `SmokeAdmissionScopeTests` against both runtimes.

- Parent runtime: 3 tests, OK.
- Head runtime: one failure, `test_runs_without_a_step_d_smoke_part_arm_no_itimer_or_alarm`, subcase `step-30b --smoke-part A`: `[] != [(ITIMER_REAL, 0)]`. The other two tests pass.

This is an expectation change. At the parent, `main`'s `finally` cleared the itimer whenever `--smoke-part` was given, even on a kind that never armed it; the test recorded that harmless clear. At the head the smoke never touches the itimer, so there is nothing to clear. The property the test exists for (a run that is not a step-D smoke arms nothing) is stronger now, not weaker.

**How to rewrite it.** Rename it (for example `..._arm_no_watchdog_timer_or_handler`) and, for all three argv cases alike:

- `timer.assert_not_called()` in place of the per-case timer list;
- patch `rt.SmokeWatchdog` (with `wraps=`) and assert it was not called;
- make the `signal.signal` recorder watch `rt.SMOKE_WATCHDOG_SIGNAL` as well as SIGALRM, and assert no callable handler was installed for either;
- assert `signal.getsignal(rt.SMOKE_WATCHDOG_SIGNAL)` and `threading.active_count()` are the same before and after.

I ran that rewrite against the head: 3 tests, OK. It overlaps the head's own `test_runs_without_a_step_d_smoke_part_start_no_watchdog_and_touch_no_timer`, so the simplest merge keeps the head's test, adds the handler and thread assertions to it, and drops the post-smoke one. `test_non_smoke_g0_return_ignores_the_admission_budget` and `test_launcher_caps_follow_the_constant` need no change.

The two branches also conflict textually in `tests/align/test_r1_smoke_launcher.py` (`git merge-tree` reports a content conflict: both add a class at the same place). Whoever lands second resolves it by keeping both classes.

## Binding (check 9)

- The watchdogs are engineering guards on the smoke only (RL-84 P-5). The ruled 1,200 s G0 cap (`g0_timeout_s`) is not read or changed by this diff.
- The WP8 property is intact: `budget.py` is unchanged, and the refusal to arm over an active timer is what the new tests exercise.
- Budgets and caps are unchanged: `SMOKE_ADMISSION_S` 3,000; post-G0 total 2,600; `r1_part_caps()` returns A 3,120 and B 5,720; `r1_minimum_seconds()` returns 9,510. `now + 11400` still clears the minimum.
- Condition 13 compares the working bytes of ten files with the executed commit at run time (`verify_r1_executed_sources`). No hash of `r1_runtime.py` is stored anywhere in the repo, so there is no pin or plan_tree to regenerate. `test_v4_registration`, `test_v4_executed_closure` and `test_v4_dynamic_closure` pass at the head. The smoke must run from a commit that contains `4365d9d6f`; this report's commit qualifies, since it adds one document.

## Findings

| # | Severity | Finding | Blocks the smoke |
|---|---|---|---|
| F-1 | Medium (tests only) | No committed test drives the real `smoke_timeout` handler, so "handler does not raise", "handler ignores `active`" and "watchdog signal is SIGALRM" all survive. | No |
| F-2 | Low (pre-existing, smoke only) | The wall cap raises `RuntimeFailure`, an `Exception`, once. Code that catches `Exception` can absorb it. | No |
| F-3 | Low (same class as the parent) | A cap that expires as `main` enters its `finally` can raise inside `stop()` and skip the teardown. | No |
| F-4 | Info | While armed, the watchdog thread wakes once a second. | No |
| F-5 | Info | MLX's native library could not be inspected for signal use on the Air. | No |

**F-1. The cap's effect is untested end to end.** The suite checks that the watchdog sends the signal (with a test-local handler) and that `main` installs and restores a handler, but never that `main`'s own handler raises. The behaviour is right at the head (check 4, rows 1 and 2). Fix, test-only: add the three witnesses in the appendix to `SmokeTimerOwnerTests`. Run in scratch, they pass at the head and fail under M4 (two of them), M4b (one) and M1c (one).

**F-2. The cap can be absorbed by `except Exception`.** `DeadmanExpired` is a `BaseException` for this reason; the smoke's `RuntimeFailure` is not, and the watchdog is one-shot. Inside the workload's episode `try` it would become an `episode_error:` flag, which still fails the member and carries the wall-cap text. Inside a tool call it would become a `tool_error` and the turn would go on. Neither is reachable in Part B, because the deadman's deadline is 720 s ahead of the watchdog's (check 4). The runtime's own journaling `except Exception` blocks (`r1_runtime.py:861`, `:1439`, `:1542`) are a few lines each. The parent's SIGALRM handler raised the same exception once, so this is not a regression, and the launcher's part cap is the backstop. Worth a follow-up only if the smoke outlives tonight: raise a `BaseException` subclass, or keep re-sending until `stop()`.

**F-3. Teardown window.** In the constructed race, 63 of 20,000 sub-millisecond deadlines raised inside `stop()` before it cleared `active`. In `main` that would propagate out of the `finally` before `segment.close()` and the terminal record. The window is a lock acquire and a few bytecodes, against a 2,600 s or 3,000 s cap, so the odds in a real smoke are negligible. The parent had the same window between entering the `finally` and `setitimer(0)`. A one-line hardening for later: have `main` set `watchdog.active = False` as the first statement of the `finally`, before `stop()`.

Related: if SIGUSR1's previous handler had been installed from C, `getsignal` returns `None` and the restore in the `finally` would raise `TypeError`. The parent had the same shape with SIGALRM. The read happens at the top of `main`, before the backend exists, and in every run so far it is `SIG_DFL`.

**F-4. One wake a second.** `_run` waits `min(left, 1.0)`, so the thread wakes about 3,000 times over a full admission budget. With the default `time.monotonic` the 1 s cap buys nothing; it only helps an injected fake clock. This runs in the measuring process, but only under `--smoke-part`, and the smoke's sensor table is an engineering check. No action for tonight.

**F-5. MLX not inspected.** Python 3.13 on the Air has no `mlx` or `mlx_lm`, so I could not list the native library's signal imports. Two things bound the risk. Until this change SIGUSR1 was at its default action in the runtime, which terminates the process, so anything that sent SIGUSR1 in-process would have killed the earlier R1 runs and smokes at this MLX pin. I know of no run that died that way, but I did not search the run logs for one. And if a library replaced the handler from C, the watchdog would go quiet rather than misfire, leaving the launcher's part caps (3,120 s and 5,720 s) in force.

## Appendix: witnesses for F-1

They use the same imports as `SmokeTimerOwnerTests`, plus `EpisodeDeadman` and `SystemClock` at module level. Total run time is under 1 s.

```python
class SmokeWallCapWitness(unittest.TestCase):   # or fold into SmokeTimerOwnerTests
    def run_main(self, run, admission=rt.SMOKE_ADMISSION_S):
        fake = SimpleNamespace(run=lambda: run(fake), close=lambda: [])
        with tempfile.TemporaryDirectory() as tmp, patch.object(rt, "read_soak_reference", return_value={}), \
                patch.object(rt, "Segment", return_value=fake), patch.object(rt, "SMOKE_ADMISSION_S", admission):
            code = rt.main(["--config", str(REPO / "configs/align/v4/r1_runtime.json"), "--r1-kind", "step-d",
                            "--output", str(Path(tmp) / "out"), "--smoke-part", "B",
                            "--smoke-started", str(time.monotonic())],
                           backend_factory=lambda _config: SimpleNamespace(close=lambda: None), stdout=io.StringIO())
            return code, json.loads((Path(tmp) / "out" / rt.CUSTODY_NAME).read_text())

    def test_admission_cap_fails_the_run_with_the_wall_cap_record(self):          # kills M4
        code, record = self.run_main(lambda fake: time.sleep(5), admission=0.2)
        self.assertEqual(code, rt.EXIT_FAILED)
        self.assertIn("smoke part wall cap reached", record["error"])

    def test_cap_inside_a_real_deadman_guard_is_reported_as_the_wall_cap(self):   # kills M1c (and M4)
        def run(fake):
            clock = SystemClock()
            fake.smoke_watchdog.set(0.2)
            with EpisodeDeadman(clock, clock.stamp(), 5).guard():
                time.sleep(5)
        code, record = self.run_main(run)
        self.assertEqual(code, rt.EXIT_FAILED)
        self.assertIn("RuntimeFailure: smoke part wall cap reached", record["error"])
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL), (0.0, 0.0))

    def test_a_late_signal_after_stop_is_ignored(self):                            # kills M4b
        def run(fake):
            fake.smoke_watchdog.stop()
            signal.raise_signal(rt.SMOKE_WATCHDOG_SIGNAL)
            return {"ok": True}
        code, record = self.run_main(run)
        self.assertEqual(code, 0, record)
```

## How this was run

- Worktrees `/Volumes/JW-EXT/jw-wt/rev-smoke278` (head), `-base` (parent) and `-mut` (mutants), all removed afterwards. `TMPDIR=/Volumes/JW-EXT/scratch/rev-smoke278/tmp`. The author's worktree was not touched.
- No code was changed, no host setting was changed, the MBP was not contacted, and `scripts/test_timings.json` was not rewritten.
- Probe scripts are in `/Volumes/JW-EXT/scratch/rev-smoke278/x/` (`astcmp.py`, `night.py`, `sem.py`, `race.py`, `procsig.py`, `coexist.py`, `mutants.py`, `scope_probe2.py`); they are scratch, not committed.
