# Block 5, second seal, ALPHA attempt 1: window and harvest record

Magistrate activation e37cd4d7 (Opus 5.5, headless), 2026-10-09, launched 22:06 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` with the eight differences of the
RUN_STATE top block of 2026-10-09 15:45. The arm of this attempt is in `seal2-alpha-a1-arm.md`.

## State found at launch

- Newest block-5 custody root: `/Users/edr/night-custody/v5-b5-alpha-a1-20261009T2312Z`. `night/result.json`,
  `night/chain.started`, `night/chain.exited` and `night/courier.sent` all exist; no driver process; no
  harvest archive; no `harvest-deferred` marker; no stand-down request. Both night jobs were still loaded.
  This is case 2 of brief section 3 (a window has ended and is not harvested).
- `B5-ARM-RELEASED: alpha beta gamma`. Ed's answers file: E-2a=NO, E-2b=NO, E-3=NO, E-4=1800, E-6=NO.
- Watchdog `notice_pending` was empty. No unread mail from the owner's notice address.
- The courier's result email for the window: Gmail message id `1a12432ad59ab69e`.
- The open `directive` issues are the six that predate the hand-off (#405, #408, #416, #417, #421, #422).

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `GO`, `stage_reached` `chain`, `refusal` null, chain exit code 0,
census clean (694 censuses, no hit). Fault reasons: none (`bound_derivation_failed` false,
`post_bracket_failed` false). Driver flag codes: `network_time.off_output`. G10 not requested. Monitor and
meter: one start each, no restart, no gap. The arm's verdict for each of the six hazards is `PASS`; from
the arm record `hazards/arm.json`: decision `GO`, no reason, nothing unmeasured.

Driver yield status `PARTIAL`: 125 members planned, 125 present, 123 succeeded.

| Stage | Planned | Succeeded | `min_valid` | Status |
|---|---|---|---|---|
| `alpha-bound-collection` | 18 | 18 | 10 | `OK` |
| `alpha-reference-start` | 3 | 3 | 2 | `OK` |
| `alpha-science-absolute` | 10 | 10 | 8 | `OK` |
| `alpha-science-abba-01-05` | 20 | 19 | 16 | `OK` |
| `alpha-science-abba-06-10` | 20 | 19 | 16 | `OK` |
| `alpha-reference-midpoint` | 1 | 1 | 0 | `OK` |
| `alpha-science-prefill-p2048-absolute` | 10 | 10 | 8 | `OK` |
| `alpha-science-prefill-p2048-abba-01-05` | 20 | 20 | 16 | `OK` |
| `alpha-science-prefill-p2048-abba-06-10` | 20 | 20 | 16 | `OK` |
| `alpha-reference-end` | 3 | 3 | 2 | `OK` |

The chain's stage list has 22 entries. Every one returned 0 except the two science stages that each lost
one member (rc 1). The corpus stage returned 0, its retry decision 0, the corpus record 0 and the bound
derivation 0; no retry and no spare stage ran. `neg8_corpus`: 18 listed, 18 kept. `yield_tripwire`: 125
attempts seen, no pre-bundle refusal flagged.

The window started at 16:12 PDT and the chain returned at about 22:02 PDT, 5 h 50 min after t0 (the arm
record expected about six hours). The dead-man job's calendar was hour 23, minute 54, which fell after the
chain's end; the job was removed before it fired.

## Closing steps (brief 4.2 to 4.4)

- 4.2: no open bracket session.
- 4.3: pin advanced, status `ADVANCED`, sequence 422 to 432, head digest
  `2abf5165abe237270f2c161b14798d06995efac3a1c87464ff5e83776eacfd3e`, operator identity
  `magistrate-20261010T0506Z`. Clone commit `ff0dbc7e5ace4e0bc6da14cafdf3b611caf39856`; its diff against
  the seal commit lists only `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A)

- Pin test: `HARVEST_PINNED`; desk root at `224a264c5faaae90cdf56118df37e773a932700b`.
- Archive `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261009T2312Z`; started about 22:08 PDT,
  exited rc=0 at about 22:53 PDT.
- `harvest.json` sha256 `baf397d620845bbd92e6efa69646daafa5c731d552e568e7a4be6b72ac797ab5`.
- **verdict `COLLECTED`, `claim_usable` true, no window reason.** `faults` empty.
- `harvest_checkout`: head `224a264c5faaae90cdf56118df37e773a932700b` (equal to the desk root),
  `status_clean` true.
- Harvest yield: planned 125, present 125, raw-valid 125, succeeded 123. By roster stage (succeeded of
  planned): `01_phase_decode_absolute` 10/10, `02_phase_decode_abba_blocks_01_05` 19/20,
  `03_phase_decode_abba_blocks_06_10` 19/20, `04_phase_prefill_p2048_absolute` 10/10,
  `05_phase_prefill_p2048_abba_blocks_01_05` 20/20, `06_phase_prefill_p2048_abba_blocks_06_10` 20/20,
  `start_reference` 3/3, `midpoint_reference` 1/1, `end_reference` 3/3, `neg8_bound` 18/18.
- `derived/code-identity.json`: `comparison` `compared`, `window_input` empty; the changed paths are the
  three seal documents and the ledger pin; `h_claim` `c27485347c9629b857df81665b5b1b8d10dcd36a`, executed
  head `39665b8cb8ce841b1345c9b39b10022e0f92dfa4`. The window ran the sealed code.
- The claim runs root holds `whole-window-verdict.json` (existence tested, file not opened).
- END STATE count (brief section 6 rule 3): first seal attempt 1 recorded 116, not bounded 1; first seal
  attempt 3 recorded 117, not bounded 1; this attempt recorded 125, not bounded 0; block total recorded
  358, not bounded 2, result `continue`.

## The corpus under the cap rule (first claim window through it)

`derived/neg8-corpus-physics.json`, read by a program that prints counts only: `members_collected` 18,
`members_bound` 18, `bound_derived_from` `collected_subset`, `members_kept` 12, 6 under `beyond_cap`, none
dropped, `minimum_n` 10, `clean_bound_validated` true, no problem listed. All 18 members were clean, so the
deciding bound comes from the first 12 in committed order, as the erratum says.

## Contention journal tally (names and integers only)

`hazards/monitor/contention.jsonl`: 2,081 ten-second intervals; 165 have an outside process above the
registered limit of 0.05 CPU-seconds per second. Intervals that contain each process (and those where it
is the only one): `mediaanalysisd` 84 (79), `corespotlightd` 36 (31), `mobileassetd` 13 (2),
`PerfPowerService` 11 (0), `runningboardd` 11 (0), `mds` 10 (0), `deleted` 10 (0), `cloudd` 8 (0),
`mds_stores` 6 (6), `duetexpertd` 5 (2), `accountsd` 5 (0), `ServiceExtension` 4 (3). `find` and
`fseventsd` do not appear: the window ended before the 00:00 walk of `/tmp`. The program is
`/Users/edr/night-plan-staging/b5-bench/contention_tally.py`; run on the first seal's attempt 3 it gives
that record's figures (173 of 1,913; `mediaanalysisd` 73 (72); `find` 31 (18)), which is the check that
it counts the right field.

Machine state at this activation: the Mac has not been restarted (boot time 2026-09-18);
`mediaanalysisd` (pid 98055), `photoanalysisd` (pid 81746) and `corespotlightd` (pid 711) are still
running; 192 GiB free.

## Decision (brief section 6)

`verdict=COLLECTED claim_usable=true`: ALPHA is done and is never armed again. Its analysed window is
`v5-b5-alpha-a1-20261009T2312Z`, the pack's first claim-usable attempt in arm order. The three attempts of
the first seal stay kept, disclosed and not analysed. The yield rule holds nothing: no stage is below its
`min_valid`, and the driver's shared-cause code is absent. No G10 record was written by this window.

Next is BETA attempt 1 (`d117_floor_qwen3-8b_v5`), which the `B5-ARM-RELEASED:` line names. The window
before it has its verdict file. `/private/tmp` is still not small, so the midnight rule of the RUN_STATE
block applies: BETA's t0 is set at or after 00:10 local on 2026-10-10, which means this activation runs
brief 5.2 at or after 23:40 PDT. Free disk is 192 GiB against the 91 needed.

## Next action

Read from the disk by brief section 3. If no `v5-b5-beta-a1-*` custody root exists, that is case 4: arm
BETA attempt 1 by brief section 5 with the RUN_STATE block's differences (t0 between 00:10 and 17:15
local). If one exists, the first case of section 3 that applies to it; its arm record is
`seal2-beta-a1-arm.md` beside this file.
