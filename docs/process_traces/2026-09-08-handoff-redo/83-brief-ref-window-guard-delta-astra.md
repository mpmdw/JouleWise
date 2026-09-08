WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on WINDOW-STATUS-GUARD-CENSUS-01 (gpt-6-astra, read-only)
HEAD = fix-round commit; HEAD~1 = a37de2ec landing; HEAD~2 = main. Packet: `git diff HEAD~1 HEAD`
(scripts/window_status.sh, tests/test_window_status_guard.py). Claims: F1 a live `scripts/run_night.py` (any
interpreter, any chain path) and its children refuse; F2/F3 matching is by path component on the whole command
string, surviving spaces and interpreter options including `--`; F4 census rows are validated (PID/PPID columns) and
a garbage or empty census refuses before writing; five new regressions each failed against a37de2ec; sibling-test,
--dry-run, grep and codex-prompt exclusions still pass. Break it: (1) re-run the previous refuter's probe matrix
(trace docs/process_traces/2026-09-08-handoff-redo/76-ref-window-guard-astra-report.md; rebuild its injected
censuses from the description: real G2-a settle window with run_night + zsh chain + sleep; paths with spaces in
interpreter/script/chain; `python3 -- scripts/run_campaign.py`; `/usr/bin/env python3 …`; venv interpreter;
historical `window-chain` shell; garbage; empty; header-only) — every measurement shape refuses, every
non-measurement shape passes; (2) new false positives: a codex seat whose argv is `codex exec … "scripts/run_night.py
…"` (the prompt text contains the path component!), a `git grep run_night.py` process, an editor with the file open,
a `python3 -m unittest tests.test_run_night` process, a `less scripts/run_night.py` — none may refuse; if the
path-component rule matches the codex prompt text, that is a BLOCKER (the guard would refuse to publish status
whenever a seat mentions the driver); (3) F4: a census whose header is present but every row is malformed;
a census with only the guard's own `ps` row; (4) `bash -n`; run tests.test_window_status_guard; (5) mutation: drop
the run_night rule and the row validation separately, confirm the named regressions fail. Report (genre review):
`verdict` = {counts, findings}; header < 8192 bytes; findings with file:line, severity, exact demonstrating command.
