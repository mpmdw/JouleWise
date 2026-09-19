SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/night_gate_fixtures/bind_supervision.py","tests/test_run_night.py"]
BASE_HEAD: 6ec5b460a4ec13dbecd1368c77a5ab666da49e86
BASELINE_MANIFEST: .codex-bridge/baselines/argv-fix-f0b608b7.json
BASELINE_DIGEST: sha256:f4ff3dbada41c8b5abc90b499e1b8dd8c3fc9c0db95143622e60439bc7d2974a
LEASE_ID: lease-985d4a62762d486dbf09b7654180d836

# Seat brief — lane TEST-LARGE-FRAME-ARGV-PORTABILITY-01: test-only argv portability fix for `test_large_frame_is_incremental_and_still_bounded`

Cwd is the linked worktree `/Users/edr/code/JouleWise-wt-argv-f0b608b7`, branch `fix/2026-09-18-large-frame-argv-portability` at `6ec5b460` (origin/main). Do NOT commit (the lead commits by pathspec). Never touch `/Users/edr/code/JouleWise` (canonical root), any other worktree, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, or `/Users/edr/night-custody`. No network. No `sudo`, no `powermetrics`. Scratch only under `/tmp`. Never run the canonical `python3 -m unittest discover`; run only the modules named below. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and pass `-B` on every Python run.

## Defect (root cause already established; record `docs/process_traces/2026-09-18-activation-d8ca3a36/19-rootcause-ci-large-frame-astra.md`, read it first)

`tests/night_gate_fixtures/bind_supervision.py` is the real-exec fault bench that the bind-supervision regressions in `tests/test_run_night.py` (class `BindSupervisionProcessTests`) drive. In the `large_frame` scenario, `Bench.dispatch` (line ~157) sets `value['load_avg_diagnostic']['raw'] = 'x' * 200000` in the PARENT and then passes the whole spec as ONE argv string to the worker (`json.dumps(spec)` in the launcher lambda, lines ~172–175). Measured: that argument is 200,884 bytes including its NUL. Linux caps each single argv string at 131,072 bytes (32 pages of 4 KiB; `execve(2)` MAX_ARG_STRLEN) and fails the exec with `E2BIG`; macOS does not have that per-string cap, so the test passes locally and fails on every hosted `ubuntu-latest` run of job `test (3.13, 5)` with `'REFUSED' != 'GO'` (the driver latches the launch `OSError` as `night_probe_error`, `tests/test_run_night.py:4607`; two identical hosted failures on main `b55909e3`). The production driver is NOT affected: `scripts/run_night.py` passes only interval, PID and job identifiers to sample workers (the uncapped production `--request` payload is a different lane, BIND-REQUEST-PAYLOAD-CAP-01). This is a test-only portability defect.

## Fix (the shape record 19 F4 prescribed and its V6 scratch already proved; `/tmp/jw_rootcause_d422e85a.py` may still be there for reference — read-only)

1. In `tests/night_gate_fixtures/bind_supervision.py`, stop expanding the 200,000-character string in the parent. Carry small metadata instead (for example `spec['large_frame_bytes'] = 200000` with `raw` left at its normal short value) and expand it INSIDE `worker()` after the spec is parsed and before the frame is built (`payload = frame(spec['id'], spec['value'])`), so the worker still publishes the identical ~200,761-byte frame and the parent still sees `max_buffer > 200000`, `max_reads <= 4`, `max_bytes <= 65536` and `verdict == 'GO'`.
2. Make the bench RECORD the largest single argv string it launches: compute `max(len(os.fsencode(arg)) + 1 for arg in argv)` when the launcher builds the argv and store it in the per-task row (for example `max_arg_bytes`), and surface it in the per-task result rows that `Bench.run` returns (the same rows that already carry `max_buffer`, `max_reads`, `max_bytes`; see lines ~177, ~388, ~454). Every scenario's rows carry it, not only `large_frame`.
3. In `tests/test_run_night.py`, add ONE defect-shaped regression in `BindSupervisionProcessTests` (place it next to `test_large_frame_is_incremental_and_still_bounded`, whose existing assertions you must leave byte-identical): assert that for the `large_frame` scenario EVERY launched task's `max_arg_bytes` is below `131072` (name the Linux `MAX_ARG_STRLEN` constant in a comment with the `execve(2)` reference). This assertion MUST FAIL on the unmodified fixture (200,884 > 131,072) and PASS after your change; that is the counterfactual for this lane, and you must show both runs (see verification 3 and 4).
4. Do not change `scripts/run_night.py`, `joulewise/`, or any other test. Do not change frame size, fake-clock behaviour, the 4-read/64 KiB budgets, or any deadline. Do not add per-platform skips or `sys.platform` branches: the fix is to keep every argv string small everywhere.

## Verification you must run and paste (exact commands and tails)

1. `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests 2>&1 | tail -4` (whole class green).
2. `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night 2>&1 | tail -4` (whole module green; if it exceeds 15 minutes, report the class run and say so).
3. Counterfactual, old fixture: `git stash push -- tests/night_gate_fixtures/bind_supervision.py` (keep your new test in place), run your new test alone, paste the failing assertion with the measured byte count, then `git stash pop`. If stash is unavailable in the sandbox, copy the original fixture from `git show HEAD:tests/night_gate_fixtures/bind_supervision.py` to `/tmp` and run the new test with a `PYTHONPATH` shim only if that is clean; otherwise report the exact obstacle.
4. Counterfactual, Linux limit emulated on this Mac: run your new fixture under the same E2BIG emulation record 19 used (patch `subprocess.Popen._execute_child` in a `/tmp` scratch to raise `OSError(errno.E2BIG)` when any argv string exceeds 131,072 bytes) and show the `large_frame` scenario reaches `GO`. Paste the largest argv byte count you observed for each worker kind.
5. `git status --short` (only the two in-scope paths may appear) and `git diff --stat`.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre implementation` (`verdict.implementation` in {implemented, partial, no_change}; `verdict.acceptance` in {ready, pending_verification, needs_ruling}); JSON header under 8000 bytes; all pasted output in the markdown body, not the header. Name the counterfactual input, the production call site you checked in `scripts/run_night.py` (cite the lines you read), the byte counts before and after, and anything in the fixture you found that could still exceed 131,072 bytes in another scenario. If a blocking decision arises, stop with NEEDS_RULING (question, options, recommendation, blocked work) after finishing the independent work.
