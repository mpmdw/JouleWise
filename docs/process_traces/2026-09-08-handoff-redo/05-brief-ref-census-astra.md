WRITE_SCOPE: []

# Refuter brief — WATCHDOG-CENSUS-01 + RESUME-DAEMON-01 landing, EXECUTION lens (gpt-6-astra, read-only)

You are an adversarial refuter. HEAD of this detached worktree is the seat landing (one commit on top of main
d8ad6c15). `git show --stat HEAD` and `git diff HEAD~1 HEAD` are your packet. The implementing seat's claims:
scoped handoff census (owned tree + lock owner only; night-time `production_census`/`agent_census` unchanged and
machine-wide), per-signal outcome labels (`already_gone` only if absent BEFORE the signal), daemon retirement
preflight in the installer, `handoff-inventory` classification of daemon/spare/bg-pty-host/resumed-twin
processes, watchdog refusal when the lock pid is dead AND a resumed twin exists, and documented operator commands
for lock reconciliation; 90 scoped tests pass.

Your lens is EXECUTION: does the code do what the tests claim, on THIS machine's real process shapes? Ground
truth process table (recorded by the lead at 00:48 PDT; you cannot run ps in the sandbox):
- 71607  `/Users/edr/.local/share/claude/versions/2.1.261 --resume /Users/edr/.claude/projects/-Users-edr-code-JouleWise/3c46c831-....jsonl --reply-on-resume --allowed-...` (the resumed twin; ppid = 71596 bg-pty-host)
- 71596  `.../ClaudeCode.app/Contents/MacOS/claude --bg-pty-host /tmp/cc-daemon-501/14ebf21c/pty/3c46c831.sock 162 47 -- /Users/edr/.local/share/claude/versions/2.1...`
- 71666  `/Users/edr/.local/bin/claude daemon run --origin transient --spawned-by {"label":"claude","cwd":"/Users/edr/code/JouleWise","pid":1536}`
- 71682  `claude bg-pty-host --bg-pty-host /tmp/cc-daemon-501/14ebf21c/spare/88735e15.pty.sock 200 50 -- /Users/edr/.local/share/claude/versions/2.1.263 --bg-spare ...`
- 71687  `claude bg-spare --bg-spare /tmp/cc-daemon-501/14ebf21c/spare/88735e15.claim.sock`
- 83953  `claude` (interactive magistrate, ppid 1282 = -zsh under Terminal) with children `node .../codex mcp-server ...`
- 84232  `/Users/edr/.local/bin/claude -p You are the top-level JouleWise magistrate, relaunched headless ...` (watchdog-owned resident, ppid 84229; lock owner)
- 48645  python `/var/folders/.../T/watchdog-c1-cli-audit-.../ladder/bin/claude -p You are the top-level JouleWise magistrate ...` (a LEAKED TEST STUB from 09-04; ppid 1)
Questions to break: (1) feed each of these command shapes to the new classifier functions in
`scripts/magistrate_watchdog.py` (write throwaway scripts under $TMPDIR, never in the repo) and report the
classification each gets; any misclassification (e.g. the leaked stub 48645 counted as a resumed twin, the
headless resident 84232 counted as a twin, or the interactive 83953 excluded) is a finding. (2) Extract the reaper
block from the doc exactly as the doc says (between the `watchdog_checkout=` line and the `   PY` terminator,
strip three spaces), `zsh -n` it, and run its Python with a FAKE process table if the code allows injection;
confirm the outcome labels for: alive-before-TERM-then-exits (expect term_exited or similar), absent-before-TERM
(expect already_gone), needs KILL. (3) Does the installer's daemon-retirement preflight actually detect the
daemon command shapes above, and does it refuse or merely warn? (4) Mutation probe: revert ONE core conjunct of
the scoped census (in a $TMPDIR copy) and confirm the named regression fails; do the same for the outcome-label
fix. (5) Anything that would make the NEXT real handoff on this machine fail or silently pass.
Run only the three scoped test modules (`python3 -m unittest tests.test_magistrate_watchdog
tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog`), never the repository-wide suite.
Report (genre review): `verdict` = {counts, findings} ONLY; envelope header < 8192 bytes; every finding with
file:line, severity (blocker/should-fix/nit), the exact command that demonstrates it, and evidence in the body.
