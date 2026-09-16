# 00 — Launch record, headless activation `736e2aed` (2026-09-16 02:29:14 PDT)

Activation `736e2aed-7274-43f4-a782-de0c7976a6ad`, watchdog attempt 35, claude
pid 5361 (supervisor 5353), spawned 02:29:14 PDT by `com.joulewise.magistrate`
after activation `08ca8197` exited cleanly at 02:18 (events.jsonl sequence 144,
"clean activation exit"; `state.json` again labels the last exit
`usage_exhausted`, the stale-field defect A197). The watchdog held in
`BACKOFF_USAGE` until 02:29 ("all launch predicates clear"); the fixture-orphan
census at spawn was 0 rows.

Heartbeat written 02:29:25 (shell pid 5477 first, corrected to `{"pid":5361,…}`
by the resident refresh loop). Pending notices queued by the watchdog: none.
No `standdown.request`, no `STOP`, remote stop `CLEAR`, no open owner-authored
`directive` issue (checked 02:30). NOTHING ARMED. No git operation in the
canonical root (read-only `git status`/`log`/`worktree list` only).

## Launch email: NOT SENT (transport down)

The claude.ai Gmail connector loads **unauthenticated** in this process (the
MCP server reports "requires authentication"; no `send_message` tool is
exposed). The intended launch email is preserved verbatim at
`/Users/edr/night-custody/magistrate/intended-launch-email-736e2aed-0232.txt`;
`notice.ack` is NOT written (Gmail never accepted anything). The interactive
session `b0ae8462` (joulewise-2e, Ed present) reported at ~02:30 that this is a
claude.ai-side outage, not a stale session: Ed's own reconnect in the
connector settings returns `not_found_error "Server not found"` (request id
`req_011Cf6t8mYgEBLHarG6c4aBi`, ~02:30 PDT). Its instruction: do not loop on
re-plans against the outage and do not exit for another relaunch; hold
resident pending either Ed's ruling on a GitHub-issue notice transport while
Gmail is down, or an instruction to re-plan; if neither arrives, re-plan when
the connector returns.

This activation's reply (~02:31): holding; asked that the ruling be written by
Ed as a `directive` issue (author `mpmdw`) rather than relayed, because the
launch fence forbids arming outside the documented email-then-arm procedure
and relayed remarks are recorded only "as relayed"; noted that the 03:00 t0 is
lapsed in practice (install close 02:50, no notice out), so any arm under
either transport is a re-plan with a new t0 and a new handback commit H.

## State found (02:29–02:32 PDT)

- Main was `77d7f0e8` at launch and moved to `62495a0b` by 02:32 (the
  interactive session's research prospectus + horizon plan, v1). The
  canonical root carries an untracked `docs/process/research_prospectus_2026-09-16.md`
  (the peer's in-progress work; left untouched).
- REHEARSAL_STUB `rehearsal-20260916` staged, not published, exactly as record
  10 of activation `08ca8197` left it: clone
  `/Users/edr/JouleWise-measurement-rehearsal-20260916b` HEAD =
  `cf249594529cfecf068ca56e6ac8e8d97b78bc77` (H, verified 02:32); staged plan
  `/Users/edr/night-plan-staging/rehearsal-20260916/night_plan.json` sha256
  `dff929bc09039f72e0edc9f450d357657ec04847bb5b3a872d75b88069d42489` (verified
  02:32); t0 1789552800 (03:00 PDT); custody root
  `/Users/edr/night-custody/rehearsal-20260916` (empty); attempt 1 aborted
  `arm_transport`. The older clone `…-rehearsal-20260916` (at 1f721fbf, the
  first cut) still exists.
- `launchctl list`: `com.joulewise.magistrate` only. Zero discoverable plans.
- Interactive session pid 841 alive with its Codex MCP child (idle-exempt for
  a stub census); the Claude desktop app was launched at ~02:29 (Ed
  reconnecting the connector). Load 3.30 / 3.29 / 2.90 at 02:30.
- Bookkeeping worktree `/Users/edr/code/JouleWise-wt-lanes-08ca8197` reused
  on a new branch `chore/2026-09-16-lanes-736e2aed` from `origin/main`
  `62495a0b`; no seat, test matrix or new worktree launched.
- `enforce_admins` reported OFF by the predecessor (direct pushes work;
  `gate-ledger` still required for PR merges).

## Resident hold

A background poll (60 s) refreshes the heartbeat and watches
`standdown.request`, `STOP` and the owner-authored `directive` issue list;
the peer's next cross-session message is the other wake source. Nothing that
moves night state runs until a verifiable Ed ruling or a re-plan instruction
arrives.

## Exit (02:35 PDT, clock-read)

The peer's second message (~02:32) reported Ed had repaired the connector from
the Claude desktop app ("~02:36" in its text; the peer's estimate, ahead of
this machine's clock) and asked for a probe; no Gmail tool exists in this
process, so the probe result was FAIL by construction. Peer GO at ~02:33 to
exit for a relaunch. Poll loop stopped, no Codex children, heartbeat current,
no `standdown.request`/`STOP`, zero directive issues. Timestamps in the first
two pointer lines and in this record were first written from estimates that
ran ahead of the clock and are corrected here from the commit times
(f9e32343 at 02:32:41, 6eb0edc4 at 02:34:06).
