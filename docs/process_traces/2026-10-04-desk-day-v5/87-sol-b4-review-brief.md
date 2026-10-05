# Executing review (Sol 6.1 xhigh, non-author): block-4 qualification code at 3697fef2

Worktree: /Users/edr/code/JouleWise-wt-dd5-b4rev, detached at 3697fef2 (branch feat/2026-10-05-v5-qualification-code = origin/main c88565c4 + the block-4 code). Diff: `git diff c88565c4 3697fef2`. Scratch /tmp/dd5-b4rev/ only. You are an independent reviewer with an EXECUTING lens; you did not write this code.

Spec: `docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md` (ruling 76 and addendum A) and the registration draft on branch `origin/design/2026-10-04-v5-qualification-block` (`git show origin/design/2026-10-04-v5-qualification-block:configs/campaigns/v5_qualification_25g83/registration_block4_draft.md`). An earlier pre-mortem's findings (`/Users/edr/night-archive/ia-0a40/sol/sol-harv.out.md`, `sol-arm.out.md`) were addressed in round 3; re-run their repros (`/tmp/ia-sol-harvest-1005/`, `/tmp/ia-sol-armlaunch/`) against this head.

Hunt for defects that would (a) let a bad window be admitted or a non-claim byte be promoted, (b) refuse or RECOVER a good window, (c) leak a measured value (energy, power, per-member duration) into a public output, or (d) make a producer fault abort the chain. Check every ruling-76 decision has code that bites (mutate the guard, watch a test fail). Pay special attention to: the G1 registered outcomes; G6/G7 never PASS; the qualification-vs-structural verdict separation; `recover_no_science` ordering proof; the courier log exclusion; the arm-only path never reaching GO or the launcher; the desk close-out backup verification; the writer's sizing roster and clock check; the T-0 load-average change (report-only only on the T-0 path; other callers unchanged).

Run `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-b4rev/pc tests/test_v5_*.py tests/test_harvest_v5_*.py tests/test_t0_rehearsal.py tests/test_t0_anchor_positive_control.py tests/test_prewindow_check.py tests/test_capture_t0_step.py tests/test_install_night_agent.py` (TMPDIR=/tmp/dd5-b4rev).

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and execution evidence.

WRITE_SCOPE: []
No background processes. Finish in this turn.
