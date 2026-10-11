# Block 5, second seal, BETA attempt 3: window and harvest record

Magistrate activation 20773813 (Opus 5.5, headless), 2026-10-10, launched 15:02 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` with items 1 to 17 of the RUN_STATE top
blocks. The arm of this attempt is in `seal2-beta-a3-arm.md`.

## State found at launch

- Newest block-5 custody root: `/Users/edr/night-custody/v5-b5-beta-a3-20261010T2151Z`. `night/result.json`,
  `night/chain.started`, `night/chain.exited` and `night/courier.sent` exist; no driver process; no harvest
  archive; no stand-down request; both night jobs still loaded. Case 2 of brief section 3.
- No unread mail from the owner's notice address (searched at launch and after the arm notice). The open
  `directive` issues are the six that predate the hand-off. The watchdog handed over no pending notice.
- The courier's result email for the window: Gmail message id `1a127d5fafbf9ad9`.

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `CHAIN_STOPPED`, `stage_reached`
`chain:pre_calibration_capture_failed`, `refusal` null; fault reasons `yield_empty` and
`chain_stopped:pre_calibration_capture_failed`; the arm passed all six hazards; ten clean censuses; chain exit
code 11; one flag code emitted (`network_time.off_output`). Yield: 125 planned, 0 present; every stage `ZERO`.

The stage list has three entries: `beta-bracket-reservation` rc 0, `beta-pre-calibration` rc 1, `chain.stop`
rc 11. The driver started at 14:51:05 PDT, the chain at 14:54:52, the opening calibration capture ran from
14:55:54 to 14:59:31, and the chain stopped itself at 14:59:31.

**Why the chain stopped.** The opening calibration capture (a short run of a known workload that measures how
closely the power sampler's timestamps line up with the workload's) was recorded in the calibration ledger
with the disposition `systematic-invalid` (ledger rows 455 and 456). The capture script
(`scripts/validate_powermetrics_fiducial.py`, `_classify_capture`) gives that word to a capture whose own
status is `valid` but whose alignment bound is above the acceptance's screen, and returns 1 for any
disposition other than `valid`; the chain stops with exit 11 on a non-zero return. The writer then closed the
session itself (rows 457 and 458, `bracket-session-abort`), so no session was left open.

How often this happens. In the ledger's bracket sessions (the opening and closing captures of windows) there
are 14 finalized captures: 13 `valid` and this one. Of the 38 older imported captures, 2 were
`systematic-invalid`. (The arm notice for attempt 4 says "14 of 15"; the count is 13 of 14.)

Was the machine busy. One read-only seat (Sonnet 5.5) read the monitor's contention journal for this window
and for attempt 2's first five minutes, the unified log for 14:50 to 15:00, and the power log. In the 28
ten-second intervals from 14:54:52 to 14:59:37 no process exceeded the contention limit of 0.05 CPU-seconds
per second. The background was the same as in attempt 2's opening minutes, whose capture was valid: `launchd`
and `loginwindow` at about 0.03 each, and two bursts of the once-a-minute contacts cache job (`contactsd`,
about 0.1 combined) at 14:56:42 and 14:57:42. No display or wake event. It could not check per-core or thermal
effects, or bursts shorter than ten seconds. Its judgment: no competing activity found, consistent with chance.

The dead-man job's calendar was hour 23, minute 13; the job was removed before it fired.

## Closing steps (brief 4.2 to 4.4)

- 4.2: no open session (`open_sessions` empty; the writer's own abort is row 458). Nothing to do.
- 4.3: pin advanced, status `ADVANCED`, sequence 450 to 458, operator identity `magistrate-20261010T2203Z`.
  Clone commit `9bd5317340a5512928f96c60c607bc4bf38ce305`; its diff against the seal commit lists only
  `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A, RUN_STATE item 10)

- Pin test: `HARVEST_PINNED`; desk root at `0699abbb0881ce64b39c46ba07de568cc3848260` (the Step 2 pin of
  Addendum 3). A governed attempt (t0 epoch 1791669060).
- Archive `/Users/edr/night-archive/harvest-v5-b5-beta-a3-20261010T2151Z`; `harvest rc=6` within a few minutes.
- `verdict=NO_COLLECTION`, `claim_usable=false`, attempt 3, pack `d117_floor_qwen3-8b_v5`.
- `exclude_window_reasons`: `calibration.no_bracket`, `cell.below_minimum`, `neg8.bound_not_derived`,
  `roster.no_science_bundles`, `whole_window.verdict_absent`.
- `faults`: none. `harvest_checkout.head` equals the desk root's commit; `status_clean` true.
- Yield: planned 125, present 0, raw-valid 0, succeeded 0; stage journal 3 stages, 0 collection stages.
- `harvest.json` sha256 `a95540c91cec31d47b8dff62956c3020b1901801b9d111e2ec4155231c45e0c1`.

## END STATE count (brief section 6, rule 3)

Unchanged by this window (0 recorded): block total 520 recorded, 2 not bounded: continue.

## Departures from the brief's reading list

Before reading brief 4.1 this activation printed `night.log`, `night/result.json`, `night/chain.exited`,
`night/chain.exit-census.json`, `night/chain-stages.jsonl`, `night/launchd.night.err` and `.out`,
`night/courier.json`, and the two operator logs `window-chain.log` and `02-beta-pre-calibration.log`. The
last one holds the capture's receipt, which includes the capture's alignment bound in seconds (a calibration
quantity, not an energy, a power or a member's duration). The value is written into no record or email, and
the decision below uses only the disposition word. Later it read the ledger with a program that prints row
kinds, session names, slots and disposition words only.

## Decision

Verdict `NO_COLLECTION`: brief section 6 sends it to the stop's reason. The stop is a measured instrument
reading on one capture, not a code path that would lose the next window the same way (13 of 14 such captures
passed on this code), and no machine-state cause was found to remove. `cell.below_minimum` and
`neg8.bound_not_derived` are here only because no member ran; they are not the member losses that brief
section 6 and RUN_STATE item 17 send to a consult, and attempt 2's cause (an agent session at the keyboard)
was a different one. So: BETA attempt 4, unchanged. **If attempt 4's opening capture is again
`systematic-invalid`, that is the same cause twice: a two-seat consult (Sol 6.1 and Opus 5.5), not attempt 5
unchanged.** Arm record: `seal2-beta-a4-arm.md`.
