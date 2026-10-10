# Block 5, second seal, BETA attempt 2: consult and decision

Magistrate activation 4c4ed4b2 (Opus 5.5, headless), 2026-10-10. The window and harvest are in
`seal2-beta-a2-window.md`. Papers: `seal2-beta-a2-consult/` here (the brief, Sol's answer, the two count
programs and their outputs) and `/Users/edr/night-archive/b5-consults/beta-a2/` (those plus the launcher's
logs).

## The question

The stop itself needs no consult: an agent session was opened at the keyboard. But inside the 2 h 32 min
that ran, a structure-only tally (`loss_tally.py`: status word, admission word and start minute of each
member that did not succeed) shows four idle-admission aborts in 25 minutes, at 12:35, 12:52, 12:55 and
13:00 PDT, among 26 science members started; the fifth loss, at 13:27, is the member in flight at the stop.
Second-seal ALPHA attempt 1 lost 2 of 125 and BETA attempt 1 lost 3 of 125 outside its malware-scan hour.
A cluster like this, repeated, removes a window by `cell.below_minimum`. The seats were asked what was busy
then, whether it returns, and what attempt 3 should be.

## The two seats (13:49 to 14:00 PDT)

Both counted the contention journal the same way: 892 ten-second intervals, 210 of them between 12:30 and
13:05, and the same per-process table (`mediaanalysisd` 25 over-limit intervals inside the span and 23
outside, `spotlightknowled` 18 and 0, `corespotlightd` 15 and 20).

- **Sol 6.1**, effort high, through `codex-run-v3`, empty write scope, working directory the harvest
  lane's worktree at `0699abbb0`. Cause: indexing and media-analysis maintenance. Recurrence: established
  as recurring from `launchctl print`, but not when; its sandbox blocked the unified log. Recommendation
  (c): do not arm unchanged; a cold erratum that lets a member wait longer for a quiet idle baseline before
  its workload runs, thresholds unchanged, which needs a new seal and a new clone. The launcher exited
  rc=65 as on the earlier consults (header parse); the body is complete.
- **Opus 5.5** agent, read-only, with the unified log. Cause: the Mac's once-a-day background maintenance
  batch, which the system scheduler `dasd` releases at about 12:53 local. It names the tasks by time:
  dozens of daily activities from 12:53:29, a one-core Spotlight knowledge run 12:57:55 to 13:00:19, and
  a 1.9-core `mediaanalysisd` run 13:01:06 to 13:04:55. Of the 52 intervals in the window with at least
  one core of outside load, 44 lie between 12:53:29 and 13:04:49. The batch started within about a minute
  of 12:53 on each of 10-06 to 10-10. The 12:35 loss came before it, at the time of a smaller
  `corespotlightd` burst; that link is by timing only. Recommendation (b): arm unchanged, and keep chains
  out of 12:45 to 13:10 local; not (c), because the admission rule correctly refused baselines taken under
  one to two cores of outside load. It also names a second daily job of 3 to 4 minutes at no fixed time
  (`corespotlight.knowledge.journals.AB`), not yet run on 10-10.

## Decision: arm BETA attempt 3 unchanged this afternoon; add 12:45 to 13:10 local to the t0 preference

The seats agree on the cause and differ on the remedy. The difference comes from one fact Sol could not
read: whether the batch has a clock time. The lead checked it: `/usr/bin/log show` with the predicate
`process == "dasd" AND eventMessage CONTAINS "COMPLETED" AND eventMessage CONTAINS "com.apple.mlhostd.daily"`
prints one line a day, at 12:54:02 on 10-08, 12:53:49 on 10-09 and 12:53:29 on 10-10. With the time known
the hazard is avoided by the choice of t0, which changes nothing a window reads. Sol's remedy would
supersede the block: a new seal and clone, a restart at ALPHA, and the loss of ALPHA's claim-usable window.
It stays on record as the dissent, and as the first candidate if an attempt that avoids the batch is again
removed by `cell.below_minimum`: that would be the same cause twice (registration 7.3) and goes to a cold
gate with this proposal, not to a fourth unchanged arm.

Standing t0 preferences now, for a six-hour chain: not running at 00:00 (the `/tmp` walk, while
`/private/tmp` is large: 3.7 million entries, 113 GiB on 10-10), not between 05:15 and 06:45 (the scan
hour), not between 12:45 and 13:10 (the daily batch). That leaves a t0 from about 13:10 to 17:15 local,
about one chain a day, until the owner restart that disables the analysis daemons.

No cold judge was convened: the disagreement is about scheduling against a measured fact, not about a
threshold, an exclusion rule or anything registered.
