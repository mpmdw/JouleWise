# Record 03 — magistrate bench verification of the argv-fix seat diff (activation 28ff4b28, 20:15–20:22 PDT)

The seat (f0b608b7 brief 02) died before reporting; its diff (`/tmp/mag-28ff4b28/argv-seat.diff`, 4,635 bytes; two files, +23/−7) is the change committed as `e32ea56c` on `fix/2026-09-18-large-frame-argv-portability`. Everything below was executed this session in `JouleWise-wt-argv-f0b608b7` with `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B` (Python 3.14.7).

## Shape check against brief 02

1. Parent no longer expands: `Bench.dispatch` sets `spec['large_frame_bytes'] = 200000` for `large_frame` sample jobs; `worker()` expands `spec['value']['load_avg_diagnostic']['raw']` after parsing the spec and before the frame is built. ✔
2. Instrumentation: the launcher closure computes `max(len(os.fsencode(arg)) + 1 for arg in argv)` into the per-task row (`max_arg_bytes`), surfaced in both result-row builders (`Bench.run` and `launch_pending_case`). ✔
3. One regression `test_large_frame_keeps_each_worker_argument_below_linux_limit` placed after `test_large_frame_is_incremental_and_still_bounded`, whose four assertions are byte-identical (diff hunk context only). Comment names Linux `MAX_ARG_STRLEN` with the `execve(2)` reference. ✔
4. No production file, no platform skip, no timing/budget constant changed (diff is confined to the two test paths). ✔

## Executed evidence

- New test alone: `Ran 1 test in 0.631s — OK`.
- Whole class: `python3 -m unittest tests.test_run_night.BindSupervisionProcessTests` → `Ran 22 tests in 29.977s — OK` (includes `test_blocked_journal_never_blocks_deadline_or_grants_go`, which the seat's log shows timing out at its 8 s watchdog under seat load).
- Counterfactual A (old fixture, new test; `git stash push -- tests/night_gate_fixtures/bind_supervision.py` … `git stash pop`): `FAILED (errors=7)`, each `KeyError: 'max_arg_bytes'` — the old bench records nothing, so this only proves the instrumentation is new.
- Counterfactual B (new instrumentation, parent-side expansion restored by replacing the one `large_frame_bytes` line with the old `'x' * 200000` assignment, on a copy restored byte-identical afterwards): `AssertionError: 200885 not less than 131072` at `job_id='sample-4', kind='sample'` → `FAILED (failures=1)`. This is the defect-shaped failure (record 19 measured 200,884; the one-byte difference is not material).
- Largest argv string per worker kind with the new fixture (bench-side measurement): census 252, sample 917, static 1913, hard 2628/2648 bytes; receipt verdict `GO`.
- Linux E2BIG emulation (record 19's `/tmp/jw_rootcause_d422e85a.py` copied to `/tmp/mag-28ff4b28/e2big_emulation.py` with only the expected-verdict map changed so `limit` mode expects GO; it patches `subprocess.Popen._execute_child` to raise `OSError(E2BIG)` when any argv string exceeds 131,072 bytes): `verdict GO`, `refusal None`, elapsed 0.499 s, launches census 251 / sample 916 / static 1912 / hard 2627,2647 bytes (the scratch measures without the trailing NUL), `EXPECTED_OUTCOME_PASS`. Output kept at `/tmp/mag-28ff4b28/e2big_limit.out`.
- Whole module `tests.test_run_night`: running in the background at commit time; tail recorded in record 03a when it finishes.
- Diff restored byte-identical after both counterfactuals (`git diff | diff - /tmp/mag-28ff4b28/argv-seat.diff` empty).

## Disposition

Committed as `e32ea56c` by pathspec (the lead commits; the seat was told not to), pushed. Contract refuter (Astra high, read-only) and execution refuter (Opus) follow on detached worktrees at `e32ea56c`; the twelve-row ledger PR follows the refuters. Hosted CI `test (3.13, 5)` on the PR head remains the only Linux execution.
