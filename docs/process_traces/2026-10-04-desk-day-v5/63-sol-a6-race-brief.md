# Fix seat: A6 (PR #475) breaks `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`

Worktree: /Users/edr/code/JouleWise-wt-dd5-a6 (branch feat/2026-10-04-launch-realization-recheck, head 8d9735f7 = round 6 + H1 test fix; main merged at baa9bb7b). Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

The whole suite at baa9bb7b fails, deterministically (lead reran it serially; it PASSES at main 1f49625f): `tests/test_arm_readiness_lifecycle.py::ArmReadinessLifecycleTests::test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses` (~841): eight threads call `launch_window.launch(args)` concurrently with `os.execve` and `_install_handoff` patched; the test asserts exactly one `execve` (exactly one consumer spends the launch capability; replays refuse). At the A6 head `execve.call_count` is 0.

Find out why (the new recheck, the PASS/claim/ACK barrier, the pending-record handshake, or the barrier-capability check), with file:line. Then:
- If the launch path now legitimately requires the driver's barrier/claim channel or the recheck inputs that the test does not provide, update the TEST so it supplies them faithfully (a driver-side stub that ACKs the claim; real recheck with matching projection or a stub that returns PASS) while keeping the property it guards: exactly one consumer reaches `execve`, every other consumer refuses with the replay/consumption refusal, and none reaches `execve` without the capability. Add an assertion that a recheck REFUSE in the winning thread yields zero `execve`.
- If instead the code broke the property (e.g. the capability is consumed but nothing launches, or more than one could launch), fix the CODE minimally and add a test.
Run: that test (5 times), `tests/test_arm_readiness_lifecycle.py`, `tests/test_launch_window.py`, `tests/test_launch_window_realization_recheck.py` with `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6race/pc` (TMPDIR=/tmp/dd5-a6race). Also grep the suite for other tests that call `launch_window.launch` or `main` directly in pack mode and run them; report any other failure. No background processes.

WRITE_SCOPE: ["tests/test_arm_readiness_lifecycle.py", "scripts/launch_window.py", "tests/test_launch_window.py", "tests/test_launch_window_realization_recheck.py", "tests/fixtures/**"]
Scratch: /tmp/dd5-a6race/ only. Never run sudo, launchctl or powermetrics. Finish in this turn.
