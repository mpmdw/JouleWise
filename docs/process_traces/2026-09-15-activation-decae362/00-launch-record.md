# 00 — Launch record, headless activation `decae362` (2026-09-15 06:15:40 PDT)

Activation `decae362-c80e-4531-907b-5b10619fae21`, watchdog attempt 32, claude
pid 53119 (supervisor 53115), spawned 06:15:40 PDT after activation `1acf2aee`
exited `usage_exhausted` at ~06:06 PDT (about 31 minutes after its own launch;
`state.json` `last_exit_class` `usage_exhausted`, `next_eligible` 06:11:49).
Heartbeat written 06:15:52 (first with the shell's pid, corrected 06:16:00 to
`{"pid":53119,…,"ts":1789478160}`). Launch email `1a0a53815b4e8f97` (new
thread) at ~06:18 PDT to Ed's address; `notice.ack` written after Gmail accepted
it. `notice_pending` was empty. No `standdown.request`, no `STOP`, remote stop
`CLEAR`, no open owner-authored `directive` issue (checked 06:17).

## State found

- Origin main `3d5b7623` (1acf2aee's 05:50 durable-pointer commit). The
  1acf2aee bookkeeping branch carries six further commits (records 03a, 03c,
  06, 07, 08 and timestamp corrections) that were pushed to the branch but not
  to main; this activation's bookkeeping branch
  `bookkeeping/2026-09-15-activation-decae362` starts at that tip (`11a22f55`)
  so main receives them with this record. Canonical `/Users/edr/code/JouleWise`
  fenced at `1d4045b4`, untouched (no git command run there).
- NOTHING ARMED: `~/Library/LaunchAgents` holds only `com.joulewise.magistrate`;
  `launchctl print gui/501/com.joulewise.night` fails (not loaded). The refused
  night `d079-epoch-25g83-derivation-n1-20260915` was harvested and its agents
  uninstalled by 1acf2aee (record 01 there).
- Machine at 06:17: 1-minute load 2.97 (5-min 2.98, 15-min 3.74); `fseventsd`
  pid 553 at 185.7 % CPU over 12 d 09 h uptime — the load-refusal cause remains
  live; its client needs sudo (Ed). Any plan authored now would refuse on
  `LOAD_MAX` 2.0.
- 35 orphaned test-fixture processes (`vllm serve /fake/model … --served-model-name
  nv5-fake-model` in `/var/folders/…/T/tmp*/bin/vllm` venvs), 0 % CPU each,
  outside the agent census (python, not claude/codex/t3). Left alone this
  slice; reported to Ed in the launch email. See "Follow-up" below.
- 1acf2aee's seats A (Astra xhigh, implementation), D (Astra high, docs) and the
  PACK-ROOT-SUCCESSOR-V5-01 scout (Astra xhigh) all show a stale `RUNNING`
  status under `/tmp/magistrate-1acf2aee/`; their logs stop at 06:06 and no
  codex process survives — they died with that session. Worktrees
  `wt-install-windows`, `wt-install-windows-docs`, `wt-pack-root` are CLEAN at
  `3d5b7623`: no seat edit landed. The scout's log shows it was trimming its
  final report (8747 bytes, over the 8192-byte envelope limit) when it died.
- Codex quota: `codex-usage` shows 0 sessions in the current 5 h window.

## Actions this record

- 06:19–06:21 PDT: relaunched all three seats verbatim from the committed
  briefs (07 → seat A, 08 → seat D, 04 → scout) with `CODEX_SERVICE_TIER=default`,
  outputs under `/tmp/magistrate-decae362/` (`09-seat-A-astra.md`,
  `10-seat-D-astra.md`, `05-pack-root-scout-astra.md`, manifests beside them).
  All three `RUNNING` at 06:21 with live `codex exec` processes.

## Follow-up (lane to register, not this slice)

FIXTURE-FAKE-VLLM-LEAK-01: some test module spawns a fake `vllm serve` server
in a temp venv and does not reap it on failure/interrupt; 35 such processes
have accumulated across sessions. Zero CPU, so not a load contributor, but
they hold ports and memory and would confuse any future process census that
widens beyond agent names. Find the fixture, add teardown-on-any-exit, and
kill the orphans once Ed says so.
