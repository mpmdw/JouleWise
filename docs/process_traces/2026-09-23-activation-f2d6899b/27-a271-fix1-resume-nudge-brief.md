RESUME NUDGE for the A271 fix round 1 seat. Your previous session ended before it wrote its final report. Its partial work is uncommitted in /Users/edr/code/wt-f2d6899b-a271: run `git diff --stat` there. Keep that work. Do not commit.

WRITE_SCOPE: ["joulewise/night_gate.py", "joulewise/evidence_night.py", "joulewise/corecaptured_loop.py", "tests/test_corecaptured_loop.py", "tests/test_night_gate.py", "tests/test_evidence_night.py", "docs/process/NIGHT_HANDBACK.md"]

The full brief is /tmp/f2d6899b/a271-fix1-brief.md; read it again. It now carries one binding amendment. A cold Fable ruling (/Users/edr/code/wt-f2d6899b-docs/docs/process_traces/2026-09-23-activation-f2d6899b/16-coldgate-fable-ruling.md, sections Q2 and Q3) rules the arm-check behaviour when an earlier row failed. In that case the corecaptured row is READ-ONLY: record the count and remediation "not_licensed", and the verdict is fail when count > 2 (not "skipped"). Actuation runs only when item 0 (nothing loaded) and every earlier row passed. Its REQUIRED TESTS / ACTIONS 1-4 and Q3 conditions 1 and 3 (the three counterfactual check() tests: loaded night + 5 spawns → zero actuator commands; census failed + 5 spawns → zero commands; all pass + 5 spawns → exactly one off, one on, and the restart only on persistence) are required.

Do this, in order:
1. Walk every item of the brief and of the ruling's Q2/Q3 tests against the current diff. List each as DONE (file:line + test name) or MISSING.
2. Complete every MISSING item.
3. Run `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night.py tests/test_docs_freshness.py` and report the tail.
4. Show the boundary mutants (`> 2` → `>= 2` at t0, `<= 2` → `< 2` at arm, the post-toggle `>= 1` → `>= 2`) each failing a test, using scratch copies, never the worktree in place.
5. Write the final report, and keep the JSON envelope SHORT (under 6,000 bytes: summary, verification tails, flags). Put the details in the markdown sections after it. Include the proposed replacement text for docs/contracts/evidence_night_entry.md:175 per ruling 16 Q3 condition 2, for the other three stale texts (joulewise/arm_retry.py:31 comment, configs/campaigns/quiet_predicate_evidence_01/README.md:60), and a list of anything you could not finish.
Never run log, networksetup, sudo, launchctl or kill. Do not edit TASK_QUEUE, RUN_STATE, decision_log, state_kernel, council_log or skills.
