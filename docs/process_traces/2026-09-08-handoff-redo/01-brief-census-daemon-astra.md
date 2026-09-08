WRITE_SCOPE: ["scripts/magistrate_watchdog.py","scripts/install_magistrate_watchdog.sh","docs/process/MAGISTRATE_WATCHDOG.md","tests/test_magistrate_watchdog.py","tests/test_magistrate_watchdog_cli.py","tests/test_install_magistrate_watchdog.py"]

# Seat brief — WATCHDOG-CENSUS-01 + RESUME-DAEMON-01 (implementation, gpt-6-astra)

## 1. Mission
Cure two defects in the magistrate relaunch watchdog's install handoff so the next handoff receipt can read
`verdict: pass` on this shared machine and the reaped interactive session is NOT auto-resumed behind the
watchdog's back. Both defects are recorded in TASK_QUEUE.md (do not edit that file; quote it):

- WATCHDOG-CENSUS-01: the handoff reaper's receipt (`~/night-custody/magistrate/handoff-1788689322.json` and
  `.verify.log`) reads `verdict: fail` with `survivors: []` because `production_census()` in
  `scripts/magistrate_watchdog.py` counts EVERY `claude` process on the machine (Ed's other sessions, e.g. the
  pid 1536 lineage), so the handoff can never pass on a shared machine. Also every owned PID was labelled
  `already_gone` although they were alive at TERM time — the reaper (the zsh/python block in
  `docs/process/MAGISTRATE_WATCHDOG.md` §Install handoff step 5) labels outcomes from the post-cooperative
  snapshot instead of the per-signal snapshot.
- RESUME-DAEMON-01: after the reaper killed the interactive tree (pid 4453) at 03:18 on 2026-09-06, the Claude
  Code background-job daemon (`claude daemon run --origin transient`, pid 71666, with a `claude bg-spare` /
  `bg-pty-host` pair) resumed the same session (`claude --resume <session>.jsonl --reply-on-resume`, pid 71607)
  five minutes later, outside the watchdog's lock; the lock still names dead pid 4453 as ACTIVE.

## 2. Required cure shape (design is yours within these fences; disagree explicitly if you see a better one)
a. Handoff verdict census scoped to the RECORDED OWNED TREE plus the lock owner — never to "any claude on the
   machine". The night-time safety census (`agent_census` — never start a [QUIET-MAC] measurement while an agent
   session is active) keeps its current machine-wide semantics; if you find the two cannot be separated cleanly,
   return NEEDS_RULING with the conflict stated, do not weaken the safety census.
b. Per-PID outcome labels derived from the per-signal snapshot taken immediately before each signal
   (`already_gone` only if absent BEFORE the signal; `term_exited` / `kill_exited` otherwise), and the
   receipt must still require every recorded (pid, start_time) pair absent.
c. Daemon retirement as an explicit, verifiable handoff step: step 1 (or a new step) must enumerate and stop the
   Claude Code background-job daemon and its spare (`claude daemon stop --any` exists in this binary:
   `claude daemon --help` shows `stop` with `--any` for a transient daemon and `--keep-workers`), verify no
   `claude daemon run|bg-spare|bg-pty-host` process remains, and the inventory helper (`handoff-inventory`)
   must classify daemon/spare/resumed-twin processes so a resumed twin is either owned (and reaped) or the
   handoff refuses. The relaunch side: a lock naming a dead pid must be reconcilable per the existing
   MAGISTRATE_WATCHDOG.md step 4 rule (remove only after confirming the owner is not live) — make the doc say
   exactly what the operator runs, and if the watchdog itself can detect "lock pid dead AND a resumed twin
   exists", refuse to launch with a named refusal rather than launching a second magistrate.
d. Every behaviour change gets a defect-shaped regression test that FAILS on the current code and passes after
   (name the counterfactual input in the test docstring: e.g. an unrelated `claude` process present in the
   process table; a pid alive at TERM time; a daemon process in the table).

## 3. Evidence to read first (read-only, outside the worktree)
- `~/night-custody/magistrate/handoff-1788689322.json`, `handoff-1788689322.json.verify.log`, `events.jsonl`,
  `state.json`, `magistrate.lock`, `launchd.out`, `launchd.err`.
- Live process table: `ps -axo pid,ppid,lstart,command | grep -E "claude|codex"` (this machine NOW has the
  resumed twin pid 71607, daemon 71666, bg-pty-host 71682, bg-spare 71687, plus the current interactive
  magistrate pid 83953 under zsh 1282 and its codex mcp-server children). Use it as ground truth for the
  command shapes your classifier must recognise; do NOT signal or kill anything.
- `docs/process/MAGISTRATE_WATCHDOG.md` (whole file; you own it in scope), `scripts/magistrate_watchdog.py`,
  `scripts/install_magistrate_watchdog.sh`, and the three test modules in scope.

## 4. Constraints
- WRITE_SCOPE is exhaustive (header line). Need another path → return NEEDS_SCOPE naming it, with reason.
- Do NOT run the repository-wide unittest suite. Acceptance = the three scoped modules:
  `python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog`
  (run to a log, report the exact rc). Edit first, verify after.
- Do not `git commit` (the worktree cannot; the lead commits). Do not touch `~/night-custody` or any process.
- The reaper block in the doc is executed by extracting the text between the `watchdog_checkout=` line and the
  `   PY` terminator and stripping the three-space indent; keep that extraction contract intact and `zsh -n` /
  `python3 -c compile()` your edited block.
- Keep the JSON envelope header under 8192 bytes; evidence goes in the markdown body.

## 5. Report (genre implementation)
Envelope `verdict.implementation` in {implemented, partial, no_change}; `verdict.acceptance` in
{ready, pending_verification, needs_ruling}. Body: files changed with the counterfactual each regression kills,
the acceptance log tail with rc, open questions, and any explicit design disagreement with §2.
