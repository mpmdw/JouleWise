# 00 — Launch record, headless activation `d6888966` (2026-09-15 06:30:43 PDT)

Activation `d6888966-2cbd-4b48-9c10-016b810dfc3c`, watchdog attempt 33, claude
pid 55633 (supervisor 55630), spawned 06:30:43 PDT after activation `decae362`
exited at 06:24:07 PDT (about 8.5 minutes after its own launch). Heartbeat
written 06:30:56 (shell pid first; corrected 06:31:04 to
`{"pid":55633,…,"ts":1789479064}`). Launch email `1a0a54669089d7da` (new thread)
at ~06:33 PDT; `notice.ack` written after Gmail accepted it. `notice_pending`
was empty. No `standdown.request`, no `STOP`, remote stop `CLEAR`, no open
owner-authored `directive` issue (checked 06:31).

## Why the last two activations died (root cause, from the attempt streams)

The watchdog classed both `1acf2aee` (exit 06:06) and `decae362` (exit 06:24)
as `usage_exhausted`. Both classifications are wrong:

- `decae362`'s stream carries a `rate_limit_event` at 06:23 with
  `five_hour.utilization 0.29`, `status "allowed"`, reset 10:30 PDT. The window
  was not exhausted.
- Both `result` records read `"stop_reason":"end_turn"`,
  `"terminal_reason":"completed"`. Each session finished its bookkeeping, wrote
  that its background seats "will wake me on completion", and ended its turn.
  In headless `claude -p` the end of the turn is the end of the process, and
  the process kills its background tasks on exit: `decae362`'s stream shows the
  seat-D launch task `killed` at 06:23:49, eighteen seconds before the exit.
- `classify_exit` in `scripts/magistrate_watchdog.py` returns `usage_exhausted`
  for any non-zero exit whose output tail matches `USAGE_EXHAUSTED_PATTERNS`;
  the pattern `\brate_limit\b` matches the routine `rate_limit_event` telemetry
  lines that every stream carries. So a turn-end exit is reported as a usage
  exit and gets the 5-minute usage backoff. Lane to register (not this slice):
  WATCHDOG-EXIT-CLASS-TELEMETRY-01 — exclude `rate_limit_event` telemetry from
  the pattern scan, or key on the `result` record's `stop_reason`.

Consequence: the three Astra seats (A implementation, D docs, PACK-ROOT scout)
died twice, each within minutes of launch, and never landed an edit. Their
worktrees are CLEAN at `3d5b7623`.

Operating rule for this activation (a working practice, not a process-rule
change): never end the turn while a seat is running; hold with bounded
foreground waits and background waiters; and launch seats detached so they
survive an activation change regardless.

## State found

- Origin main `d6cff8ad` (decae362's record-00 addendum). Canonical
  `/Users/edr/code/JouleWise` fenced at `1d4045b4`, untouched (no git command run
  there). Bookkeeping worktree `/Users/edr/code/JouleWise-wt-bk-d6888966`,
  branch `bookkeeping/2026-09-15-activation-d6888966` from `origin/main`.
- NOTHING ARMED: `~/Library/LaunchAgents` holds only `com.joulewise.magistrate`.
  The refused night `d079-epoch-25g83-derivation-n1-20260915` was harvested and
  its agents uninstalled by `1acf2aee` (record 01 there); clone and night root
  retained.
- Machine at 06:31: 1-minute load 3.50 (5-min 3.63, 15-min 3.92); `fseventsd`
  pid 553 at 190 % CPU over 12 d 10 h uptime — the load-refusal cause remains
  live; its client needs sudo (Ed). No plan authored this activation.
- 35 orphaned `vllm serve /fake/model` fixture processes still present
  (FIXTURE-FAKE-VLLM-LEAK-01, decae362 record 00); left alone.
- Codex quota: 0 sessions in the current 5 h window. Claude 5-hour window at
  29 % (decae362's last telemetry).

## Actions this record

- 06:35:20–06:35:30 PDT: relaunched all three seats verbatim from the committed
  briefs (04 → scout, 07 → seat A, 08 → seat D) with the same flags decae362's
  manifests record (`CODEX_SERVICE_TIER=default`, `gpt-6-astra`; scout
  read-only xhigh 3600 s; seat A workspace-write xhigh 5400 s; seat D
  workspace-write high 3600 s), via `/tmp/magistrate-d6888966/launch-seats.py`
  (`subprocess.Popen(..., start_new_session=True)`, so each wrapper is its own
  session with parent pid 1). Wrapper pids 56084 (scout), 56331 (A), 56502 (D);
  all `RUNNING` with live `codex exec` children at 06:36. Outputs under
  `/tmp/magistrate-d6888966/` (`05-pack-root-scout-astra.md`,
  `09-seat-A-astra.md`, `10-seat-D-astra.md`, manifests beside them).
- Background waiters on each seat's `.status` file wake this session on
  completion; a successor activation harvests the same files from disk if this
  one is gone.

## Correction to decae362 record 00 addendum (dated addendum; that file is not edited)

The addendum "06:40 PDT — first relaunch ran read-only; relaunched again with
the write sandbox" carries estimated clock times that postdate the session's
actual exit (06:24:07). From the manifests and the attempt stream: read-only
relaunches 06:19:25 (scout), ~06:19–06:20 (A, D); seat D's read-only attempt
returned `blocked/partial` at 06:21:17 (manifest `finished_at 13:21:17Z`), not
06:33; seat A's read-only attempt was terminated ~06:22, not 06:37; the
workspace-write relaunches started 06:22:41 (A) and 06:22:48 (D), not
06:38–06:39. The substance of the addendum (read-only default; `-s
workspace-write` required for editing seats) stands.
