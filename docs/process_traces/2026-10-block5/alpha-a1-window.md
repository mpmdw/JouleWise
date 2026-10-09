# Block 5, ALPHA attempt 1: window and harvest record

Magistrate activation d2ddcd8e (Opus 5.5, headless), 2026-10-08, launched 20:39 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`.

## State found at launch

- Newest and only block-5 custody root: `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z`.
  `night/result.json`, `night/chain.started`, `night/chain.exited` and `night/courier.sent` all exist; no
  driver process; no harvest archive; no `harvest-deferred` marker; no stand-down request. Both night jobs
  were still loaded. This is case 2 of brief section 3 (a window has ended and is not harvested).
- `B5-ARM-RELEASED: alpha beta gamma`. Ed's answers: E-2a=NO, E-2b=NO, E-3=NO, E-4=1800, E-6=NO.
- No unread mail from the owner's notice address. The open `directive` issues are the six that predate the
  hand-off (#405, #408, #416, #417, #421, #422); none is new.
- Watchdog `notice_pending` held one entry: id `transition-2602-hold_census`, kind `hold_census`, reason
  `production census non-empty inside plan span`, epoch 1791516883 (20:34:43 PDT). The watchdog's event log
  shows what the census found: the window's own courier (the short `claude -p` session the driver starts
  after the chain to email the result), pid 65389. Five minutes later the census was empty, the watchdog
  released the window as `collected_window` and started this activation. The hold is the expected
  behaviour, not a fault.

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `GO`, `stage_reached` `chain`, `refusal` null, fault reasons none
(`bound_derivation_failed` false, `post_bracket_failed` false). Driver yield status `PARTIAL`: 119 members
planned, 119 present, 114 succeeded. Every stage's status is `OK` (each at or above its `min_valid`).

| Stage | Planned | Succeeded | `min_valid` |
|---|---|---|---|
| `alpha-bound-collection` | 12 | 10 | 10 |
| `alpha-reference-start` | 3 | 3 | 2 |
| `alpha-science-absolute` | 10 | 10 | 8 |
| `alpha-science-abba-01-05` | 20 | 19 | 16 |
| `alpha-science-abba-06-10` | 20 | 20 | 16 |
| `alpha-reference-midpoint` | 1 | 1 | 0 |
| `alpha-science-prefill-p2048-absolute` | 10 | 9 | 8 |
| `alpha-science-prefill-p2048-abba-01-05` | 20 | 19 | 16 |
| `alpha-science-prefill-p2048-abba-06-10` | 20 | 20 | 16 |
| `alpha-reference-end` | 3 | 3 | 2 |

`night/g10.json` `result`: `DISCHARGED`. The dead-man job's calendar was hour 20, minute 29; it fired once
inside the window, which brief 4.1 expects.

## Closing steps (brief 4.2 to 4.4)

- 4.2: no open bracket session.
- 4.3: pin advanced, status `ADVANCED`, sequence 402 to 412, head digest
  `3d873d374c76115612c9907fc18cdd893c751eb55b06197f5bcccee7151ed03b`, operator identity
  `magistrate-20261009T0340Z`. Clone commit `a16db2d044c8d2cedd1f472169b879df31a22ff0`; its diff against
  the seal commit lists only `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A)

- Pin test: `HARVEST_PINNED`; desk root at `7e6158d669cbb6fb35761aee18abf363f07c5d36`.
- Archive `/Users/edr/night-archive/harvest-v5-b5-alpha-a1-20261008T2201Z`; started about 20:41 PDT,
  exited rc=0 at about 21:22 PDT.
- `harvest.json` sha256 `c15f85f21b4d6b8a82cefaf0176291deafb4d009efbea37093c5806bf6eadc91`.
- **verdict `COLLECTED`, `claim_usable` false, window reasons `cell.below_minimum` and
  `neg8.bound_not_derived`.** `faults` empty.
- `harvest_checkout`: head `7e6158d669cbb6fb35761aee18abf363f07c5d36` (equal to the desk root),
  `status_clean` true.
- Harvest yield: planned 119, present 119, raw-valid 119, succeeded 114. By roster stage (succeeded of
  planned): `01_phase_decode_absolute` 10/10, `02_phase_decode_abba_blocks_01_05` 19/20,
  `03_phase_decode_abba_blocks_06_10` 20/20, `04_phase_prefill_p2048_absolute` 9/10,
  `05_phase_prefill_p2048_abba_blocks_01_05` 19/20, `06_phase_prefill_p2048_abba_blocks_06_10` 20/20,
  `start_reference` 3/3, `midpoint_reference` 1/1, `end_reference` 3/3, `neg8_bound` 10/12.
- `derived/code-identity.json`: `comparison` `compared`, `window_input` empty, the only changed paths are
  the three seal documents. The window ran the sealed code.
- The claim runs root holds `whole-window-verdict.json` (existence tested, file not opened).
- END STATE count (brief section 6 rule 3): recorded 116, not bounded 1, result `continue`.

## Decision (brief section 6)

The window reasons are `cell.below_minimum` and `neg8.bound_not_derived`. The table's row for these codes
says: do not arm ALPHA again unchanged, and convene the consult of rule 1 at once, on the first occurrence
(two blind seats, Sol 6.1 at effort high and an Opus 5.5 agent, on structural evidence: the window reasons,
the member counts and the monitor's contention journal). ALPHA is not claim-usable, so BETA is not armed
either. Nothing is armed.

## Next action

The consult is convened by this activation. If this record is the newest file about ALPHA attempt 1, the
consult has not reported: the next activation reads the disk by brief section 3 (it finds case 4 with the
arm held by this decision), looks for `alpha-a1-consult.md` beside this file, and if it is absent convenes
the consult again from this record. No window is armed before the consult's decision is recorded.
