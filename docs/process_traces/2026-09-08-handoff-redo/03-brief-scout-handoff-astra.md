WRITE_SCOPE: []

# Scout brief — why will the NEXT magistrate watchdog handoff fail? (gpt-6-astra, fresh eyes)

You are a read-only peer auditor. The install handoff in `docs/process/MAGISTRATE_WATCHDOG.md` §Install handoff
was executed on 2026-09-06 (steps 0–5) and did not take: receipt `~/night-custody/magistrate/handoff-1788689322.json`
+ `.verify.log` read `verdict: fail`; the Claude Code bg-job daemon auto-resumed the reaped session; the watchdog
has sat in CLOCK_UNCERTAIN since 03:30 09-06 (`state.json`, `events.jsonl`) because the laptop lid was closed
(Maintenance Sleep every ~5 min; now cured, caffeinate holds it awake); lock names dead pid 4453. Three defects are
already being fixed by other seats (WATCHDOG-CENSUS-01, RESUME-DAEMON-01, T0-ACID-CLOCK-01 in TASK_QUEUE.md).

Your job: enumerate every OTHER reason the redo could fail or silently mis-succeed, ranked by likelihood × cost.
Read `scripts/magistrate_watchdog.py`, `scripts/install_magistrate_watchdog.sh`, the doc, the launchd plist it
renders, `~/night-custody/magistrate/*` (launchd.out/err too), `launchctl print gui/$(id -u)/com.joulewise.magistrate`,
`pmset -g`, and the live process table (`ps -axo pid,ppid,lstart,command | grep -E "claude|codex|python"`).
Specific questions: (1) does the watchdog recover from CLOCK_UNCERTAIN on its own once the clock is stable, and
what does `clock_sane_samples: 1` after 45 h imply about its tick cadence — is the launchd job even ticking
(`launchctl list` shows `-` pid, status 0)? (2) pid 48645 is a python `/var/folders/.../T/watchdog` alive 3 d 19 h —
what is it and does it collide? (3) is the first-night REHEARSAL_STUB path wired so a relaunched headless magistrate
does something observable? (4) anything in the state file (backoff, boot id, activation) that would make the first
post-handoff tick refuse. Do NOT modify files, signal processes, or touch `~/night-custody`.

Report (genre scout): envelope header < 8192 bytes; body = ranked findings with file:line evidence and the exact
command that demonstrates each, then the minimal cure for each.
