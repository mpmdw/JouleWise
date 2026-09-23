WRITE_SCOPE: []
ROLE: DELTA RE-AUDIT refuter (execution lens) for the A271 fix round. Branch feat/2026-09-23-a271-corecaptured, worktree /Users/edr/code/wt-f2d6899b-a271, delta `git diff f81e34ec..1b8c6410`. Fix rounds introduce defects. Audit only what this delta changed or could break. The governing texts are cold ruling 16 Q2/Q3 (/Users/edr/code/wt-f2d6899b-docs/docs/process_traces/2026-09-23-activation-f2d6899b/16-coldgate-fable-ruling.md) and the refuter reports 11 and 13 in the same directory.

Hunt:
(1) The arm-check licensing gate. Show, through check(), that NO actuator command (networksetup, sudo) can run when item 0 failed or ANY earlier row failed, including a row that fails by exception, a row that is "skipped", and the fake_launchctl rehearsal path. Show that a read-only count above two fails the check.
(2) Timeouts. Every actuator command has a bounded timeout. A TimeoutExpired or other exception on OFF, the 8 s wait or ON still reaches exactly one ON attempt and refuses. There is never a second OFF, never a second restart, and never a restart without a completed cycle.
(3) Window anchoring at both t0 and arm. The window is [clock-before-read − 600, clock-after-read]. Check equal timestamps, DST and timezone offsets, and a clock that moves backwards.
(4) Post-toggle threshold >= 1. Check the boundary with a spawn stamped exactly at toggle completion.
(5) The parser's blank-line tolerance. Can it hide a real non-empty malformed line?
(6) The regenerated policy blocks in NIGHT_HANDBACK.md and the runbook are byte-identical to arm_retry.render_policy(). The contract text at docs/contracts/evidence_night_entry.md (the "three machine moves" sentence and item 7) is true against the code.
(7) Mutation probes: collapse each new guard (the licensing predicate, the timeouts, the threshold, the anchor) to its operands, and report survivors.

Run tests/test_corecaptured_loop.py, tests/test_night_gate.py, tests/test_evidence_night.py and tests/test_arm_retry.py.

You are a READ-ONLY refuter. Do not edit tracked files, do not commit, and do not call Claude or any other agent. Scratch files go only under /tmp/f2d6899b-scratch-a271delta/. Run tests with `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider ...`. Mutate only scratch copies. Never run log, networksetup, sudo, launchctl or kill. Report BLOCKER / SHOULD-FIX / NIT with file:line, a counterexample and executed evidence (or NOT EXECUTED). Say "no blocker found" if there is none. Keep the JSON envelope under 6,000 bytes.
