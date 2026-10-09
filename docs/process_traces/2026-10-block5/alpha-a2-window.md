# Block 5, ALPHA attempt 2: window and harvest record

Magistrate activation 0705bcd5 (Opus 5.5, headless), 2026-10-08, launched 23:04 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`. The arm of this attempt is in
`alpha-a2-arm.md`.

## State found at launch

- Newest block-5 custody root: `/Users/edr/night-custody/v5-b5-alpha-a2-20261009T0515Z`. `night/result.json`
  and `night/courier.sent` exist; `night/chain.started` does not; no driver process; no harvest archive; no
  `harvest-deferred` marker; no stand-down request. Both night jobs were still loaded (the night job had run
  once and exited with code 3). This is case 2 of brief section 3 (a window has ended and is not harvested).
- The watchdog released the window as `null_window` at 23:04:54 PDT; `notice_pending` was empty.
- `B5-ARM-RELEASED: alpha beta gamma`. Ed's answers: E-2a=NO, E-2b=NO, E-3=NO, E-4=1800, E-6=NO.
- No unread mail from the owner's notice address, and no mail at all from it in the last two days: the two
  questions of the attempt-2 arm notice (`RESTART-OK` or `RESTART-NO`, `SPOTLIGHT-OK` or `SPOTLIGHT-NO`)
  are unanswered. The open `directive` issues are the six that predate the hand-off.

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `REFUSED`, `stage_reached` `arm`, refusal reason
`night_refused_hazard`, census clean, flag codes emitted by the driver: `network_time.off_output`. No chain
started, so there is no yield, no bracket session and no monitor journal (`hazards/monitor/` does not
exist; the journal tally the cold ruling of attempt 1 asks for has nothing to count).

From the arm record `hazards/arm.json` (`refused_at` `dwell`, decision `NULL`):

| Hazard module | Verdict | What it measured |
|---|---|---|
| battery | PASS | adapter connected (140 W), not charging, current 0 mA |
| clock | PASS | frequency check passes: bound 4.69 ms against the 5.0 ms limit |
| thermal | PASS | level 0 |
| disk | PASS | 204.5 GB free on the runs volume |
| instrument | PASS | 300 sampler frames, median interval 129.2 ms |
| contention | REFUSE | 89 intervals of 30 s in 2,700.9 s, 87 of them over the limit of 0.05 CPU-seconds per second, longest clean run 0 s; the last dirty interval names `fseventsd` (pid 11523) at 0.996 CPU-s/s |

The window started at 22:15:05 PDT and ended at 23:00:50 PDT: the arm waited its full 2,700 s for a clean
180 s and refused. The dead-man job's calendar was hour 3, minute 43; it never fired.

## Closing steps (brief 4.2 to 4.4)

- 4.2: skipped (an arm that refuses opens no session); `open_sessions` is empty.
- 4.3: pin advance status `NOT_NEEDED` (ledger and pin both at sequence 412, head digest
  `3d873d374c76115612c9907fc18cdd893c751eb55b06197f5bcccee7151ed03b`). Clone head unchanged,
  `a16db2d044c8d2cedd1f472169b879df31a22ff0`; its diff against the seal commit lists only
  `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A)

- Pin test: `HARVEST_PINNED`; desk root at `7e6158d669cbb6fb35761aee18abf363f07c5d36`.
- Archive `/Users/edr/night-archive/harvest-v5-b5-alpha-a2-20261009T0515Z`; harvest rc=0, under a minute.
- `harvest.json` sha256 `4564ea599b682c1e922dc090a42c01dd436f4c9e6bcb2c38e2271842ab4bd8a1`.
- **verdict `NULL`, `claim_usable` false, window reasons `window.null`.** `faults` empty; `yield` null.
- `harvest_checkout`: head equal to the desk root, `status_clean` true.
- END STATE count (brief section 6 rule 3): not rerun; this attempt started no chain and is not counted,
  so the block total stays at attempt 1's (recorded 116, not bounded 1, `continue`).

## Decision (brief section 6)

Row `verdict=NULL`: remove the refusing hazard, then arm ALPHA attempt 3.

- **Cause key** (registration 7.3). Attempt 2: the hazard module that refused, `contention`. Attempt 1:
  `cell.below_minimum`, which the registration counts as a family of its own, and `neg8.bound_not_derived`.
  The two keys differ, so rule 1 (same cause twice goes to a consult) does not apply, and the brief names
  the cure for this process.
- **The process.** `fseventsd` (the file-events daemon) pid 11523 was at 99.4 % of a core at launch. In
  attempt 1's journal it was over the limit in 14 of 1,975 intervals, so the loop began after that window
  or late in it.
- **The cure** (brief section 6, `[AH-6]`): see "Cure" below.

## Cure

- 23:05:52 PDT: `sudo -n /usr/local/sbin/joulewise-restart-fseventsd`, rc=0. launchd started a new
  `fseventsd`, pid 69896.
- Three minutes later (23:09:23): the new process had used 1.60 CPU-seconds in 3 min 29 s and read 0.0 %.
  The unified log's last ten minutes held five lines `spawned corecaptured` (23:00:36, 23:02:08, 23:03:39,
  23:05:10, 23:07:10): launchd was restarting the Wi-Fi log-capture daemon about every 91 seconds, which is
  what drove the loop on 2026-09-22. More than two lines, so by the brief Wi-Fi was switched off and on
  once: off 23:09:31, on 23:09:39, network back 23:09:46.
- Four minutes after the toggle (23:13:45): one `spawned corecaptured` line (23:11:42); `fseventsd` at
  1.81 CPU-seconds in 7 min 53 s (0.21 CPU-seconds in the 4 min 22 s since the earlier reading), 0.0 %. At
  23:14:40: 1.83 CPU-seconds, 0.1 %. No process other than this session and the log daemon during its own
  query was above the limit.
- `com.apple.mediaanalysisd` (pid 98055) and `com.apple.photoanalysisd` (pid 81746) are still running,
  unchanged since attempt 1; Ed has not answered the restart question.

## Next action

ALPHA attempt 3 is armed by this activation: `alpha-a3-arm.md`.
