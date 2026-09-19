# Launch record — headless activation 28ff4b28-0cc9-4401-a00a-7fac2d3be279 (2026-09-18 20:10:58 PDT)

Watchdog attempt 50, claude pid 36807 (supervisor 36803), model Fable 5.1 (`--model fable --effort high`), binary 2.1.277. Previous activation f0b608b7 (attempt 49, launched 19:50:55) exited at 20:04:04 with exit class `usage_exhausted` (events 205–207: clean activation exit → IDLE → BACKOFF_USAGE; relaunched when "all launch predicates clear"). The armed-plan fence starts at t0 − 8 min (23:52), so relaunches before it are by design.

## Durable sources read (in order)

1. heartbeat written 20:11:10 with the bash pid, corrected 20:11:24 to the claude pid (`{"pid":36807,"activation_id":"28ff4b28-…","ts":1789787484}`); no `standdown.request`, no `STOP`.
2. `state.json`: ACTIVE, `notice_pending: []`, `remote_stop CLEAR`, `last_exit_class usage_exhausted`, fenced checkouts = the canonical root and the triple (`d079-epoch-25g83-derivation-n1-20260919`, `/Users/edr/JouleWise-measurement-20260919-derivation`, `d595aa9f`).
3. `RUN_STATE.md` top block: the canonical checkout sits at `422cdebb` (stale, untouched); origin/main is `6ec5b460` (arm record 21, read from the linked worktree `JouleWise-wt-mag-d8ca3a36`); the f0b608b7 and d8ca3a36 checkpoint memories; `AGENTS.md`; f0b608b7's launch record 00 and briefs 02/04.
4. `gh issue list --label directive --author mpmdw --state open` → `[]`.
5. Measurement clone HEAD `d595aa9f` (read from `.git/HEAD`, no git command); `com.joulewise.night` and `com.joulewise.night.deadman` loaded; plan directory intact under `~/night-custody/d079-epoch-25g83-derivation-n1-20260919/`.

## Launch email

Gmail accepted `1a0b7a711e8ef27f` at 20:13 PDT to `claude.ai.copper531@passmail.net` cc `claude2.glaring610@passmail.net` (why launched; no pending notices; the night stays armed; desk work only; exit before 23:40). `notice.ack` written with this activation id after acceptance.

## Inherited from f0b608b7 (killed mid-slice)

- Bookkeeping branch `bookkeeping/2026-09-18-activation-f0b608b7` was one commit ahead of origin (`3ce0390e`, brief 02); pushed 20:14. The argv seat manifest (record 03) was untracked there; it is filed by this activation together with f0b608b7's brief 04 (kernel registrations) and the kernel seat's manifest/observer rows.
- Argv-fix seat (Astra high, invocation `argv-fix-f0b608b7`, lease `lease-985d4a62…`, status file still `RUNNING`): died with the activation after writing the complete diff in `JouleWise-wt-argv-f0b608b7` (only the two in-scope paths dirty). Its log shows it had run `test_blocked_journal_never_blocks_deadline_or_grants_go` alone and hit the 8 s external watchdog under the load of two seats plus the magistrate; that test passes at the bench (record 03). The seat produced no report.
- Kernel registration seat (Astra high, invocation `kernel-reg-f0b608b7-2`, lease `lease-93e3197d…`; first launch refused because the report path was inside the worktree): killed while still reading; `JouleWise-wt-kernel-f0b608b7` is clean at `3ce0390e`. To be relaunched from brief 04.

## Boundary

REQUEST 23:52:00 PDT (1789800720), TERM 23:54, KILL 23:55, t0 00:00:00 09-19. This activation ends its loop and exits before 23:40 PDT. No `[QUIET-MAC]` work; no git operation in the canonical root; the measurement clone, plan and LaunchAgents are not touched.

## Slice plan

1. TEST-LARGE-FRAME-ARGV-PORTABILITY-01: bench-verify the seat's diff (record 03), commit it on `fix/2026-09-18-large-frame-argv-portability`, contract refuter (Astra) + execution refuter (Opus) on detached worktrees at the fix head, PR under the twelve-row ledger; hosted CI on the PR is the Linux execution of the counterfactual.
2. Relaunch the kernel registration seat from brief 04 with a fresh lease.
3. Records, RUN_STATE pointer, memory checkpoint; exit before 23:40.
