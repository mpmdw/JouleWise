# 00 — Launch record, headless activation `d7aba749` (2026-09-16 03:04:19 PDT)

Activation `d7aba749-0bfb-4bdd-8c94-576ba0c8cda2`, watchdog attempt 37, claude
pid 9937 (supervisor 9933), spawned 03:04:19 PDT by `com.joulewise.magistrate`
after activation `83d93f5a` armed the stub and exited cleanly at 02:56
(events.jsonl sequence 152 "clean activation exit"). `state.json` still labels
the last exit `usage_exhausted` (stale-field defect A197), so the watchdog
held in `BACKOFF_USAGE` (sequence 153) until 03:04 ("all launch predicates
clear", sequence 154); fixture-orphan census 0 rows.

Heartbeat written 03:04:31 (`{"pid":9937,…}`, first act). Pending notices
queued by the watchdog: none (`[]`). No `standdown.request`, no `STOP`,
remote stop `CLEAR`. Open owner-authored `directive` issues: none. No git
operation in the canonical root (`git worktree list` and `git status` only;
remote main read through `gh api`); this record was written from the linked
worktree `JouleWise-wt-bk-d7aba749`, added from `JouleWise-wt-hb-83d93f5a`
at main `a28726b0`.

## State at launch (clock-read 03:05 PDT)

- `rehearsal-20260916c` (REHEARSAL_STUB) IS ARMED: t0 03:25:00 PDT
  (1789554300), window 900 s, install close 03:15, resident REQUEST 03:17 /
  TERM 03:19 / KILL 03:20, courier deadline 03:45:00, dead-man 04:45. H
  `be221f6a`; clone `/Users/edr/JouleWise-measurement-rehearsal-20260916c`
  (fenced triple in `state.json`); custody root
  `/Users/edr/night-custody/rehearsal-20260916c`. `launchctl list` shows
  `com.joulewise.night`, `com.joulewise.night.deadman`, and
  `com.joulewise.magistrate`, all exit status 0.
- Notice thread `1a0a99fa2717d749`: two SENT messages only, no reply from Ed;
  the night stands.
- Census: Ed's interactive Claude session (pid 7066, `joulewise-95` /
  `3427f330`) alive with its Codex MCP child. Flagged to Ed in the launch
  email (a clean `REHEARSAL_ONLY` pass needs it closed before 03:17; a
  `night_refused_agent_present` hit is also an accepted harvest outcome).
  Not touched by this activation.

## Launch email: SENT

Gmail `send_message` accepted the launch email at 03:06 PDT (message
`1a0a9ae7c1584531`) to Ed's address; `notice.ack` written 03:06:27 with
this activation id.

## Work done

This activation does no night work: the successor's next exact action (harvest
after 03:45 and `courier.sent`) is unchanged from the 83d93f5a UPDATE in
`docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`. Slice
content: launch record (this file), RUN_STATE pointer line, DURABLE-STATE
UPDATE, one docs-only push to main, then a clean exit before the 03:17 request
so the t0 census is not polluted by this session. No Codex child was started
(the MCP server process is the harness's idle child, not a session).

## Exit

Recorded in the RUN_STATE pointer line and the DURABLE-STATE UPDATE at the
time of the exit; see the commit that carries this file.
