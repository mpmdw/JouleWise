# Block 5, ALPHA attempt 3: window and harvest record

Magistrate activation 1aed44f9 (Opus 5.5, headless), 2026-10-09, launched 05:10 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`. The arm of this attempt is in
`alpha-a3-arm.md`.

## State found at launch

- Newest block-5 custody root: `/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z`. `night/result.json`,
  `night/chain.started`, `night/chain.exited` and `night/courier.sent` all exist; no driver process; no
  harvest archive; no `harvest-deferred` marker; no stand-down request. Both night jobs were still loaded.
  This is case 2 of brief section 3 (a window has ended and is not harvested).
- `B5-ARM-RELEASED: alpha beta gamma`. Ed's answers file: E-2a=NO, E-2b=NO, E-3=NO, E-4=1800, E-6=NO.
- Watchdog `notice_pending` held one entry: kind `yield_alert`, code `yield.stage_low`, stage
  `alpha-bound-collection` (role corpus, ordinal 3), 9 of 12 planned members succeeded, 12 bundles present,
  minimum 10, stage rc 1, queued at epoch 1791531004 (00:30 PDT), file
  `night/yield_alert-3.json` sha256 `a738fbe22b1811e4ea1fdbb11d32fbaff8ba5762321a5e74f6723da529a5f24b`.
  It goes into this activation's email, and is acknowledged only after Gmail accepts that email.
- The courier's result email for the window: Gmail message id `1a1209173494156c`.
- The open `directive` issues are the six that predate the hand-off (#405, #408, #416, #417, #421, #422).

## Owner mail (one unread message, transcribed verbatim)

Gmail message `1a11f894e901dbbd`, 2026-10-09 00:20 PDT, a reply on the thread of the attempt-3 arm notice
(`1a11f4c8ca81d791`), which had asked `RESTART-OK` or `RESTART-NO` and `SPOTLIGHT-OK` or `SPOTLIGHT-NO`:

> yes if you can keep work going resisting mac ok
>
> and yes to spotlight

Read as: the Mac may be restarted between windows, on the condition that work keeps going afterwards
("resisting" is taken as "restarting"); and `com.apple.corespotlightd` may be disabled.

What was done with it:

- **Restart.** The condition cannot be met by an agent on this Mac. FileVault is on and there is no
  automatic login (`autoLoginUser` is not set), so after a restart the machine waits at the unlock screen
  for the owner's password, and the watchdog (a launchd job in the user's session, `RunAtLoad` true) starts
  again only after he logs in. This session has no passwordless `shutdown`, `reboot` or
  `fdesetup authrestart` (`sudo -n -l` lists only the `fseventsd` restart helper, the two network-time
  commands and `powermetrics`). No restart was attempted. A restart is the owner's act at the keyboard;
  whether the next arm waits for it is the consult's question (below).
- **Spotlight.** `launchctl disable gui/501/com.apple.corespotlightd` was refused by this session's
  permission check (reason given: account and standing-rule changes). It was not worked around. The
  command is logged in `/Users/edr/night-plan-staging/b5-bench/permission-blocks.log` and goes to the
  owner as one command he can run before he restarts.
- The consult seat the attempt-2 arm record proposed for the restart's side effects was not convened:
  every precondition a restart could disturb (clock frequency, battery, network-time setting, ledger,
  machine identity, agent processes) is measured directly by brief 5.1 and 5.3 before the next arm.

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `GO`, `stage_reached` `chain`, `refusal` null, chain exit code 0,
census clean. Fault reasons `yield_low` and `bound_derivation_failed` (`post_bracket_failed` false). Driver
flag codes: `network_time.off_output`, `yield.stage_low`. G10 not requested. Monitor and meter: one start
each, no restart, no gap, both proven stopped. From the arm record `hazards/arm.json`: decision `GO`, no
reason, nothing unmeasured.

Driver yield status `LOW`: 119 members planned, 119 present, 115 succeeded.

| Stage | Planned | Succeeded | `min_valid` | Status |
|---|---|---|---|---|
| `alpha-bound-collection` | 12 | 9 | 10 | `LOW` |
| `alpha-reference-start` | 3 | 2 | 2 | `OK` |
| `alpha-science-absolute` | 10 | 10 | 8 | `OK` |
| `alpha-science-abba-01-05` | 20 | 20 | 16 | `OK` |
| `alpha-science-abba-06-10` | 20 | 20 | 16 | `OK` |
| `alpha-reference-midpoint` | 1 | 1 | 0 | `OK` |
| `alpha-science-prefill-p2048-absolute` | 10 | 10 | 8 | `OK` |
| `alpha-science-prefill-p2048-abba-01-05` | 20 | 20 | 16 | `OK` |
| `alpha-science-prefill-p2048-abba-06-10` | 20 | 20 | 16 | `OK` |
| `alpha-reference-end` | 3 | 3 | 2 | `OK` |

The chain's stage list shows the corpus stage rc 1, its retry decision rc 0, the retry rc 1, the bound
derivation rc 2; the start reference rc 1, its spares decision rc 0, the spares rc 1. `neg8_corpus`: 12
listed, 9 kept. `yield_tripwire`: 131 attempts seen, no pre-bundle refusal flagged, so the driver's code
`stage.members_refused_pre_bundle_identical` is absent.

The window started at 23:44 PDT on 2026-10-08 and the chain returned at about 05:06 PDT on 2026-10-09. The
dead-man job's calendar was hour 5, minute 12, which fell after the chain's end.

## Closing steps (brief 4.2 to 4.4)

- 4.2: no open bracket session.
- 4.3: pin advanced, status `ADVANCED`, sequence 412 to 422, head digest
  `1ae51d38cec5ac271231011a56cfd6604749a9d748a2a99ad734ed751f33f717`, operator identity
  `magistrate-20261009T1211Z`. Clone commit `96e6d7a9a6b276f2e64135fb16b3eec2fb29f7c4`; its diff against
  the seal commit lists only `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A)

- Pin test: `HARVEST_PINNED`; desk root at `7e6158d669cbb6fb35761aee18abf363f07c5d36`.
- Archive `/Users/edr/night-archive/harvest-v5-b5-alpha-a3-20261009T0644Z`; started about 05:13 PDT, exited
  rc=0 before 05:33 PDT.
- `harvest.json` sha256 `e668781583da51efce7a7e7ef57fef8cbfab68b427acd40401dafc1529d4267e`.
- **verdict `COLLECTED`, `claim_usable` false, window reasons `neg8.bound_not_derived` and
  `neg8.screen_failed`.** `faults` empty. `cell.below_minimum` is absent.
- `harvest_checkout`: head `7e6158d669cbb6fb35761aee18abf363f07c5d36` (equal to the desk root),
  `status_clean` true.
- Harvest yield: planned 119, present 119, raw-valid 119, succeeded 115. By roster stage (succeeded of
  planned): `01_phase_decode_absolute` 10/10, `02_phase_decode_abba_blocks_01_05` 20/20,
  `03_phase_decode_abba_blocks_06_10` 20/20, `04_phase_prefill_p2048_absolute` 10/10,
  `05_phase_prefill_p2048_abba_blocks_01_05` 20/20, `06_phase_prefill_p2048_abba_blocks_06_10` 20/20,
  `start_reference` 2/3, `midpoint_reference` 1/1, `end_reference` 3/3, `neg8_bound` 9/12.
- `derived/code-identity.json`: `comparison` `compared`, `window_input` empty; the changed paths are the
  three seal documents and the ledger pin. The window ran the sealed code.
- The claim runs root holds `whole-window-verdict.json` (existence tested, file not opened).
- END STATE count (brief section 6 rule 3): attempt 1 recorded 116, not bounded 1; attempt 3 recorded 117,
  not bounded 1; block total recorded 233, not bounded 2, result `continue`.

## Contention journal tally (as the cold ruling of attempt 1 asks; names and integers only)

`hazards/monitor/contention.jsonl`: 1,913 ten-second intervals; 173 have an outside process above the
registered limit of 0.05 CPU-seconds per second. Intervals that contain each process (and those where it
is the only one): `mediaanalysisd` 73 (72), `find` 31 (18), `signpost_reporte` 17 (14), `fseventsd` 13 (0),
`mobileassetd` 12 (2), `PerfPowerService` 10 (1), `runningboardd` 9 (0), `mds` 8 (0), `corespotlightd` 8
(3), `airportd` 7 (5), `mds_stores` 7 (4), `deleted` 7 (0). The same program run on attempt 1's journal
gives the cold judge's figures (183 of 1,975; `mediaanalysisd` 77 (72); `corespotlightd` 51 (43);
`fseventsd` 14 (12)), which is the check that it counts the right field.

Machine state at this activation: `mediaanalysisd` (pid 98055) and `photoanalysisd` (pid 81746) still
running, both still listed as disabled; `corespotlightd` (pid 711) running; `fseventsd` (pid 69896) quiet
since its restart; uptime 20 days; adapter connected, battery not charging; 216 GiB free.

## Decision (brief section 6)

The window reasons are `neg8.bound_not_derived` and `neg8.screen_failed`. The table's row for these codes
says: do not arm ALPHA again unchanged, and convene the consult of rule 1 at once. Cause key of this
attempt (registration 7.3): the two `neg8` codes. Attempt 1's key also held `neg8.bound_not_derived`, so
two of ALPHA's two chains were lost through the 12-member corpus (10 kept with no margin, then 9 after the
one retry). ALPHA is not claim-usable, so BETA is not armed. Nothing is armed.

The yield rule: the `LOW` stage is the corpus, not a wholly lost science stage, and the driver's
shared-cause code is absent; the consult covers it.

## Next action

The consult is convened by this activation (Sol 6.1 at effort high through `codex-run-v3`, and an Opus 5.5
agent, both blind, read-only). Its papers are in `/Users/edr/night-archive/b5-consults/alpha-a3/`
(`BRIEF-body.md`, `sol-consult.md`, `opus-consult.md`) and are copied to `alpha-a3-consult/` beside this
file with the decision record `alpha-a3-consult.md`. If that record is absent, the consult has not been
decided: the next activation reads the disk by brief section 3 (case 4, with the arm held by this
decision), reads whichever seat answers exist in the archive directory, convenes again any seat whose
answer is missing, and decides. No window is armed before the decision is recorded. The email that
carries the watchdog's pending yield notice is sent with that decision; until Gmail accepts it,
`notice.ack` is not written and Ed's message `1a11f894e901dbbd` stays unread only if this record is not
yet pushed.
