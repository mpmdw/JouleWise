# Design consult: the magistrate relaunch watchdog (READ-ONLY seat; write ONLY your report file)

## Forcing problem
JouleWise's unattended night loop (D-127 / D-169; `scripts/run_night.py`, `scripts/install_night_agent.sh`, `docs/process/NIGHT_HANDBACK.md`, `docs/process/NIGHT_COURIER_PROMPT.md`, `scripts/night_gate.py`) refuses to run a measurement night if ANY agent session is alive at fire time (census `pgrep -lf "codex|claude|t3"`, reason `night_refused_agent_present`). The driving "magistrate" session (a Claude Code interactive session in Terminal.app, running a /loop over experiment planning, paper writing and review) is itself such a session. Ed is away for a week from 2026-09-02 and REQUIRES hands-free operation: nobody will start or stop anything at the machine. Ed ruled 2026-09-02: the magistrate MAY kill its own session and its codex children before a real measurement window; a relaunch agent is the way back. Default cadence (Ed's decision pending, default): stand-down 30 minutes before a window's t0; email Ed at stand-down and at relaunch. The night courier (a launchd-started headless `claude -p` run after the night) already exists and emails Ed + pushes a results branch; it is the ONLY relaunch path today and it chains nights with no wake source.

Read first: `docs/process_traces/2026-09-02-fresh-fable-audit/01-audit-night-loop.md` (in the worktree `/Users/edr/code/JouleWise-wt-decode-id`, branch fix/2026-09-02-decode-identity-set — NOT on main yet) sections 2, 3, 5 (B8, B10) and 6 item 3. Then the code files above and `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` (R-3, R-9) and `docs/decision_log.md` D-127, D-161, D-169.

## Constraints (hard)
- User-level launchd only (`~/Library/LaunchAgents`), no sudo, no new system daemons.
- Never launch while the night fence is active (02:45-03:30 and the 07:00 minute local) or while a night plan's [t0-30min, t0+window_max_s+courier slack] span is open; read `/Users/edr/night-custody/<plan>/night_plan.json`.
- Launch only when the agent census is EMPTY (same census the gate uses, so the design cannot race the gate).
- Bridge depth one hop: the relaunched magistrate is a top-level `claude` session; it may spawn codex children; it must not be spawned BY a codex session.
- Kill switch: a stop file Ed can create from a phone (via a pushed commit? via email? name the cheapest remote-actionable path; Ed can push to GitHub and send email, nothing else).
- Email Ed at each launch and each stand-down (Gmail MCP from inside the relaunched session, or the courier's route — say which and why).
- D-161: refusals whose only adversary is the trusted operator are over-engineering; fail-closed only for physics/evidence/pre-registration. Do not gold-plate.
- Rule 11: this is a process mechanism; it goes through a cold gate and Ed approves the install by email. Your report is design input, not a ruling.
- The relaunched session must resume the standing mandate from the repo alone (RUN_STATE.md pointer + the durable pause file), not from any scratchpad.

## Questions (answer each, numbered)
1. Topology: one calendar-driven launchd job that polls, vs a WatchPaths/StartInterval job, vs extending the existing courier baton. Recommend one with reasons; name the failure modes of the two you reject.
2. Exact state machine: inputs (plan json, census, fence clock, stop file, courier.sent, a `magistrate.pid`/lock), transitions, and every write it makes. Where does the magistrate's own stand-down live (a `ScheduleWakeup`-driven self-check inside the session that computes t0-30min from the plan and then exits, vs the watchdog SIGTERM-ing it)? Recommend.
3. The launch command: `claude -p` flags (model, --allowedTools, --permission-mode, output format, cwd = the dev checkout `/Users/edr/code/JouleWise`), the prompt text (≤ 25 lines) that resumes the loop from the repo, and how the /loop cadence survives a headless session (does `ScheduleWakeup` exist in `-p` mode? If unknown, say so and give the fallback: the watchdog re-launches on StartInterval whenever census is empty and no lock is held).
4. Usage-limit behaviour: when the Claude 5-hour window exhausts, the headless session errors out; design the backoff so relaunch attempts do not burn the machine or spam Ed (e.g. one email per state change, not per attempt).
5. Failure table: watchdog dies; session hangs forever; session exits mid-fix leaving a dirty worktree; two magistrates alive at once; clock skew; claude auto-update changes the binary path (the courier hit exactly this on 2026-09-02). For each: detection, containment, who hears about it.
6. Test plan runnable at the bench without a real night: dry-run mode, a fake plan with t0 in 10 minutes, a fake census hit, a stop file. Name the unit tests and the one end-to-end rehearsal.
7. Minimal file list to build (script names, plist label `com.joulewise.magistrate`, test file, doc section) and an estimate in Sol-hours.
8. Anything in the constraints you would push back on, with the reason.

## Output
Write ONE markdown report to the path given in your launch message. Be concrete: plist XML skeleton, the shell/python skeleton, the prompt text. No preamble. Cite file:line for every claim about existing code you make, and mark anything you did not execute as [not executed].
