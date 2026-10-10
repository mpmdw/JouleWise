# Block 5, second seal, BETA attempt 1: window and harvest record

Magistrate activation cbe4230e (Opus 5.5, headless), 2026-10-10, launched 06:51 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` with the eight differences of the
RUN_STATE top block of 2026-10-09 15:45. The arm of this attempt is in `seal2-beta-a1-arm.md`.

## State found at launch

- Newest block-5 custody root: `/Users/edr/night-custody/v5-b5-beta-a1-20261010T0742Z`. `night/result.json`,
  `night/chain.started`, `night/chain.exited` and `night/courier.sent` all exist; no driver process; no
  harvest archive; no `harvest-deferred` marker; no stand-down request. Both night jobs were still loaded.
  This is case 2 of brief section 3 (a window has ended and is not harvested).
- `B5-ARM-RELEASED: alpha beta gamma`. Ed's answers file: E-2a=NO, E-2b=NO, E-3=NO, E-4=1800, E-6=NO.
- No unread mail from the owner's notice address. The open `directive` issues are the six that predate
  the hand-off (#405, #408, #416, #417, #421, #422).
- The courier's result email for the window: Gmail message id `1a12610eeb3e73ef`.
- The watchdog handed over two pending notices: the yield alert of stage
  `beta-science-prefill-p2048-abba-06-10` (file `night/yield_alert-12.json`, sha256
  `ea9dbc216ca65baa959b38776464ba567228aa19f040deec12ea573c0622f460`), and a hold of kind `hold_census`
  (id `transition-2663-hold_census`, 06:46:40 PDT, reason "production census non-empty inside plan
  span"). The hold began 95 s after the chain exited, while the courier session was alive, and cleared at
  06:51:40 PDT. Both went to the owner in one email, Gmail message id `1a1261625fed1c07`, and the
  acknowledgement file was written after Gmail accepted it.

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `GO`, `stage_reached` `chain`, `refusal` null, chain exit code 0,
census clean (718 censuses, no hit). Fault reasons: `yield_low` (`bound_derivation_failed` false,
`post_bracket_failed` false). Driver flag codes: `network_time.off_output`, `yield.stage_low`. G10 not
requested. Monitor and meter: no restart, no gap. The arm's decision is `GO` with no reason.

Driver yield status `LOW`: 125 members planned, 125 present, 117 succeeded.

| Stage | Planned | Succeeded | `min_valid` | Status | Stage ended (PDT) |
|---|---|---|---|---|---|
| `beta-bound-collection` | 18 | 18 | 10 | `OK` | 01:38 |
| `beta-reference-start` | 3 | 3 | 2 | `OK` | 01:59 |
| `beta-science-absolute` | 10 | 10 | 8 | `OK` | 02:24 |
| `beta-science-abba-01-05` | 20 | 19 | 16 | `OK` | 03:16 |
| `beta-science-abba-06-10` | 20 | 19 | 16 | `OK` | 04:06 |
| `beta-reference-midpoint` | 1 | 1 | 0 | `OK` | 04:09 |
| `beta-science-prefill-p2048-absolute` | 10 | 10 | 8 | `OK` | 04:35 |
| `beta-science-prefill-p2048-abba-01-05` | 20 | 20 | 16 | `OK` | 05:28 |
| `beta-science-prefill-p2048-abba-06-10` | 20 | 15 | 16 | `LOW` | 06:31 |
| `beta-reference-end` | 3 | 2 | 2 | `OK` | 06:45 |

The chain's stage list has 23 entries. Five returned 1: the three science stages that lost members,
`beta-reference-end`, and `beta-reference-end.spares` (the spare stage ran after the end reference lost a
member, and returned 1). Both calibration captures, the corpus stage, its retry decision, the corpus
record and the bound derivation returned 0. `neg8_corpus`: 18 listed, 18 kept. `yield_tripwire`: 125
attempts seen, no pre-bundle refusal flagged, so the driver's shared-cause code
`stage.members_refused_pre_bundle_identical` is absent.

The window started at 00:42 PDT and the chain exited at 06:45 PDT, 6 h 03 min after t0. The dead-man job's
calendar was hour 9, minute 4, after the chain's end; the job was removed before it fired.

## Closing steps (brief 4.2 to 4.4)

- 4.2: no open bracket session.
- 4.3: pin advanced, status `ADVANCED`, sequence 432 to 442, head digest
  `250904b494dc89d4aaad067f1abeabf09702f2175b11318ca175b4e6809200de`, operator identity
  `magistrate-20261010T1352Z`. Clone commit `86f4d0853292c8acbac0b218c5136970d1b20351`; its diff against
  the seal commit lists only `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A)

- Pin test: `HARVEST_PINNED`; desk root at `224a264c5faaae90cdf56118df37e773a932700b`.
- Archive `/Users/edr/night-archive/harvest-v5-b5-beta-a1-20261010T0742Z`; started about 06:53 PDT,
  exited rc=0 at about 07:22 PDT.
- `harvest.json` sha256 `f0d72323b67d075db29a5c136d087222284a6d4651d130549f9dbd5a82d6ec7d`.
- **verdict `COLLECTED`, `claim_usable` false, one window reason: `neg8.screen_failed`.** `faults` empty.
- `harvest_checkout`: head `224a264c5faaae90cdf56118df37e773a932700b` (equal to the desk root),
  `status_clean` true.
- Harvest yield: planned 125, present 125, raw-valid 125, succeeded 117. By roster stage (succeeded of
  planned): `01_phase_decode_absolute` 10/10, `02_phase_decode_abba_blocks_01_05` 19/20,
  `03_phase_decode_abba_blocks_06_10` 19/20, `04_phase_prefill_p2048_absolute` 10/10,
  `05_phase_prefill_p2048_abba_blocks_01_05` 20/20, `06_phase_prefill_p2048_abba_blocks_06_10` 15/20,
  `start_reference` 3/3, `midpoint_reference` 1/1, `end_reference` 2/3, `neg8_bound` 18/18.
- `derived/code-identity.json`: `comparison` `compared`, `window_input` empty; the changed paths are the
  three seal documents and the ledger pin; `h_claim` `c27485347c9629b857df81665b5b1b8d10dcd36a`, executed
  head `ff0dbc7e5ace4e0bc6da14cafdf3b611caf39856`. The window ran the sealed code.
- The claim runs root holds `whole-window-verdict.json` (existence tested, file not opened).
- END STATE count (brief section 6 rule 3): first seal attempt 1 recorded 116, not bounded 1; first seal
  attempt 3 recorded 117, not bounded 1; second seal ALPHA attempt 1 recorded 125, not bounded 0; this
  attempt recorded 119, not bounded 0; block total recorded 477, not bounded 2, result `continue`.

## The corpus under the cap rule

`derived/neg8-corpus-physics.json`, read by a program that prints counts only: `members_collected` 18,
`members_bound` 18, `bound_derived_from` `collected_subset`, 1 under `dropped`, `members_kept` 12, 5 under
`beyond_cap`, `minimum_n` 10, `clean_bound_validated` true, no problem listed. The bound was derived. So
`neg8.screen_failed` here does not follow from a missing bound, as it did on the first seal's attempt 3;
its cause is the consult's first question.

## Contention journal tally (names and integers only)

`hazards/monitor/contention.jsonl`, by `/Users/edr/night-plan-staging/b5-bench/contention_tally.py`: 2,152
ten-second intervals; 228 have an outside process above the registered limit of 0.05 CPU-seconds per
second. Intervals that contain each process (and those where it is the only one): `XProtectRemediat` 77
(61), `mediaanalysisd` 76 (72), `mobileassetd` 13 (2), `PerfPowerService` 12 (0), `runningboardd` 12 (0),
`corespotlightd` 11 (9), `cloudd` 11 (2), `mds` 11 (0), `trustd` 10 (0), `deleted` 8 (0), `duetexpertd` 8
(2), `syspolicyd` 8 (6), `triald` 7 (3), `mds_stores` 6 (4), `loginwindow` 5 (5). Firefox does not appear.

By the stage each interval ended in (over-limit intervals of all intervals): bound collection 33 of 315;
reference start 7 of 124; decode absolute 5 of 149; decode ABBA 01-05 9 of 310; decode ABBA 06-10 9 of
302; reference midpoint 1 of 19; prefill absolute 12 of 156; prefill ABBA 01-05 25 of 316; **prefill ABBA
06-10 114 of 379**; reference end 13 of 82. All 77 `XProtectRemediat` intervals lie between 05:40 and
06:00 PDT, inside the stage that came out `LOW`. In the reference-end stage the most frequent process is
`syspolicyd` (7 intervals).

Machine state at this activation: the Mac has not been restarted (boot time 2026-09-18); 219 GiB free.

## Decision (brief section 6)

`verdict=COLLECTED claim_usable=false` with the window reason `neg8.screen_failed`: the table's row for
that code says BETA is not armed again unchanged, and the consult of rule 1 (two blind seats: Sol 6.1 at
effort high, and an Opus 5.5 agent) is convened at once, on this first occurrence. Nothing is armed
meanwhile. The yield rule holds nothing by itself: the low stage kept 15 of 20, it was not wholly lost,
and the driver's shared-cause code is absent. This window has its verdict file, so the ledger rule does
not hold a later arm. No G10 record was written by this window.

## Next action

The consult is convened by this activation; its papers go to
`/Users/edr/night-archive/b5-consults/beta-a1/` and its record is `seal2-beta-a1-consult.md` beside this
file. If that record does not exist, or has no decision: convene or finish the consult from the brief
`/Users/edr/night-archive/b5-consults/beta-a1/BRIEF-body.md` (write it from this record if it is absent;
the model is `alpha-a3-consult/BRIEF-body.md`), then decide by brief section 6 rule 1. Arm nothing before
that record carries a decision.
