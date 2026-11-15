# R7-2 refusal fix: cold delta review of `scripts/align_r1_rehearsal.py`, `433bcd6a6..de10a3829`

Cold reviewer (Fable 5.2), 2026-11-11, on the Air. Code only: no Block 6, BYTES held-out or v4 outcome data was opened.
This review was killed once by a terminal restart at 16:50 PST and resumed; nothing from the first run was pushed.

## Verdict: ADMIT

The condition-13 bytes at `de10a3829` are right and need no change. A runtime config without `g0_timeout_s` is a recorded
refusal again (exit 3, `r1_result.json` written, nothing else touched), and a night with the field behaves as it did before
the fix. One finding is worth acting on, in tests only: no test notices if the teardown span check or the work deadline is
silently disabled on a night that ran (F1). It does not block, because the code is correct today and the fix does not touch
the driver.

Presign has moved to `566720484` since; none of the later commits touch the driver.

## What changed

| Commit | Content | Driver bytes |
|---|---|---|
| `0aa014307` | Moves `night_worst_case_s(args.runtime)` and the `_R1_WORK_DEADLINE` assignment from the top of `run()` to inside the handled region, after the output directory is created and before the prepare packet. `span_cap` starts as `None`; the teardown check becomes `span_cap is not None and chain_wall_s > span_cap`. | behaviour |
| `95a189b9c`, `577963b78` | Test expectations (admitted by Opus) and docs. | none |
| `de10a3829` | Comments and docstrings in the driver, plus contract text. | comments only |

## Checks

| # | Check | Result | Evidence |
|---|---|---|---|
| 0 | `de10a3829` changes no code | PASS (from the killed run, not redone) | Docstring-stripped `ast.dump` identical between `577963b78` and `de10a3829`. New comments match RL-59 and RL-72 E2, with one omission (F2). |
| 1 | Missing field: exit 3, refused record, no power-mode, Automatic, runtime or prepare work | PASS | Witness red at `433bcd6a6` (the `Refusal` escapes `run()` at line 1612), green at `de10a3829`. Probe below. |
| 2 | With the field: same commands, same records, same deadline and span, same teardown | PASS | Base driver and head driver under identical fixtures give identical output. Probe below. |
| 3 | No other early config read outside the handler | PASS | AST walk of `run()`: nothing before the `try` at line 1648 uses `args.runtime`. See below. |
| 4 | Mutants | 2 killed, 2 survive | F1. |
| 5 | Required modules at `de10a3829` | PASS | All six OK. |

### Check 1: the missing-field path

The witness asserts exit 3, the error text, no registration, no runtime call and no High Power command. It does not look at
Automatic, the sudo listing, the prepare packet or the condition-13 verification, so I probed those directly with the fake
command boundary (`FakeWorld`), at `de10a3829`:

| Case | Exit | Record | Commands issued |
|---|---|---|---|
| No `g0_timeout_s`, synthetic | 3 | `refused`, names `g0_timeout_s`, 0 phases, 0 power-mode records, `restore_skipped` (lock never held) | 3, all the terminal volume census (`mount`, `diskutil`) |
| No `step.deadman_s`, synthetic | 3 | `refused`, names `step.deadman_s` | same 3 |
| No `g0_timeout_s`, production path (`synthetic=False`) | 3 | `refused`; no `prepare_packet` key | same 3; `require_prepare_packet`, `executed_commit` and `verify_r1_executed_sources` never called |
| No `g0_timeout_s`, output directory already exists | 3 | refusal written into the existing directory | same 3 |

No `pmset` query, no `sudo -l`, no Automatic or High Power command and no runtime call in any of them. `_R1_WORK_DEADLINE`
is `None` afterwards. At the base driver every one of these cases raises out of `run()` with no record.

The refusal now lands earlier than the contract requires: before the host night lock and the t0 volume check, not only
before power-mode and runtime work.

### Check 2: a night with the field

Comparing `433bcd6a6` against `de10a3829` directly is confounded, because `95a189b9c` changed the shared fixture (`FakeWorld`
now reports 1,200 s for the G0 cap). So I ran the base driver inside the head tree, which leaves the driver as the only
difference. A full synthetic night, both drivers:

- Command sequence: 108 calls, identical (sha256 `123c67a368213057…`).
- `r1_result.json` and `r1_slots.json`: identical after dropping wall-clock fields (`close_s`, `chain_wall_s`, `started_ns`,
  `ended_ns`, `wall_s`, `required_samples`, `registration_sha256`, `host_state_dir`).
- `span_cap`: 108,768 s in both.
- `_R1_WORK_DEADLINE`: armed before the first command in both, one value all night, equal to start + 108,768 − 900 s to
  within 0.01 s, and `None` after teardown.
- Teardown on a normal night that overruns: with the span bound patched to 1 µs, both drivers end `aborted` with
  "RL-72 E2: close/span overhead cap exceeded", exit 4, and no `r1_slots.json`. The `None` tolerance does not weaken the
  check when the bound was read.

`span_cap` can only be `None` at teardown when `mkdir` or the bound read itself failed. Both come before the lock, the
guard and every runtime call, so `None` always means the night did not run.

Two ordering differences exist and neither matters. The config is now read after the signal handlers are installed and
after `mkdir`, where it used to be read before both. And with an existing output directory plus a bad config, the run now
refuses on the directory without reading the config.

### Check 3: early reads

Before the `try`, `run()` calls only `time.monotonic`, path resolution, `VolumeWatch(...)`, `HostLock(...)`,
`PowerModeGuard(...)`, `host_marker_path()`, `host_state_dir()` and `signal.signal`. None reads the runtime config; the
constructors do no I/O. `host_state_dir()` can raise outside the handler, but `main()` calls it first and turns that into
exit 3 (unchanged). `main()` reads `--runtime-entrypoint` inside its own handler (exit 3, stderr only, unchanged). Inside
the handled region, every `args.runtime` read comes after the moved lines.

## Mutants

Applied in a scratch worktree at `de10a3829`; the worktree was restored after each.

| Mutant | Change | Result |
|---|---|---|
| M1 | Move the bound read and deadline back above the `try` | **Killed** by the witness (error: `Refusal` escapes). |
| M2 | Skip `_write_result` when `span_cap` is `None` | **Killed** by the witness (no `r1_result.json`). |
| M3 | The night runs but `span_cap` stays `None` (the bound goes to another local; the deadline is still armed) | **Survives.** All 22 `test_r1_*` modules and `test_v4_registration` give the same result as at head. |
| M4 | `_R1_WORK_DEADLINE` is never armed | **Survives**, same sweep. |

M3 is not an equivalent mutant: under the probe's overrunning night it ends `complete`, exit 0, with `r1_slots.json`
written, where head ends `aborted`, exit 4. M4 is detected by the probe too (the deadline is `None` at the first command).

## Tests at `de10a3829`

Native on the Air, `nice -n 10 python3.13 -B`, one module at a time, TMPDIR on JW-EXT.

| Module | Result |
|---|---|
| `tests.align.test_r1_rehearsal` | 77 OK |
| `tests.align.test_r1_followup` | 12 OK |
| `tests.align.test_r1_round4` | 10 OK |
| `tests.align.test_v4_registration` (condition 13) | 24 OK |
| `tests.align.test_v4_executed_closure` | 6 OK |
| `tests.align.test_v4_dynamic_closure` | 10 OK |
| `tests.align.test_r1_round7_science` (holds the witness) | 18 OK |
| `tests.align.test_r1_round8` | 21 OK |

## Findings

**F1 (MEDIUM, tests only; no driver change).** Nothing in the suite exercises "RL-72 E2: close/span overhead cap exceeded"
or the work deadline: no test mentions `chain_wall_s`, `close_s`, `span_cap` or `_R1_WORK_DEADLINE`. That gap dates from
`a85ee8ec6`, but this fix makes it matter more, because the check is now conditional on `span_cap` and a later edit could
leave it `None` on a real night without any test turning red (M3). Suggested witnesses, both a few lines against
`FakeWorld`: patch `night_worst_case_s` to a tiny span and assert `aborted`, exit 4, no `r1_slots.json`; and assert
`_R1_WORK_DEADLINE` is set at the first runtime call and `None` after `run()`.

**F2 (LOW, comment).** The rewritten R7-2 comment at the G0 constants lists step-d, the gated D runs, X-G, step-30b, the
A-B-A legs and d-4bit as arming the 1,200 s timeout. It drops the designed start states (the planning turns), which the
old comment named and which do arm it (`test_gate_policies_carry_the_timeout_only_for_its_kinds` asserts 1,200 s for
`d-planning-turn-r-plus-0c`). The contract text has it right. These are condition-13 bytes, so leave it for the next
change that already rebinds the file.

**F3 (LOW, pre-existing, unchanged by this delta).** A refused run whose teardown takes over 900 s is recorded as
`aborted` with the E2 error, overwriting the refusal reason, while the exit code stays 3. Shown with a missing-field
refusal and a 1,000 s terminal census. Any refusal path does this since `a85ee8ec6`.

**F4 (INFO, outside the required set).** Four other R1 modules are red at `de10a3829`: `test_r1_round6_exec_review` (1),
`test_r1_round6_lows` (2), `test_r1_round6_power` (2) and `test_r1_runtime` (9), 14 tests in all. They are not caused by
this delta: the failing sets are identical under M3 and M4, and identical in the base logs the killed run left for these
four modules at `433bcd6a6`. They look like more stale expectations of the kind `95a189b9c` refreshed (phase order,
worst-case table, G0 inconclusive handling). I did not diagnose them.

**F5 (INFO).** `test_v4_registration` passes with a mutated driver in the working tree, so it is not a guard against
uncommitted driver edits. The run-time condition-13 check (`verify_r1_executed_sources`) is what compares working bytes
to the commit.

## Housekeeping

Probe, mutant script and logs: `/Volumes/JW-EXT/scratch/r72-review/probe` and `logs3` (scratch, not committed). All
`r72-review*` worktrees are removed. `scripts/test_timings.json` was not touched.
