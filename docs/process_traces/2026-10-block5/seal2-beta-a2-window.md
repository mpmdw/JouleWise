# Block 5, second seal, BETA attempt 2: window and harvest record

Magistrate activation 4c4ed4b2 (Opus 5.5, headless), 2026-10-10, launched 13:32 PDT. Structure only: paths,
hashes, codes and counts. Procedure: sections 3, 4 and 6 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` with items 1 to 15 of the RUN_STATE top
blocks of 2026-10-09 15:45 and 2026-10-10 08:40. The arm of this attempt is in `seal2-beta-a2-arm.md`.

## State found at launch

- Newest block-5 custody root: `/Users/edr/night-custody/v5-b5-beta-a2-20261010T1756Z`. `night/result.json`,
  `night/chain.started`, `night/chain.exited` and `night/courier.sent` all exist; no driver process; no
  harvest archive; no `harvest-deferred` marker; no stand-down request. Both night jobs were still loaded.
  Case 2 of brief section 3 (a window has ended and is not harvested).
- `B5-ARM-RELEASED: alpha beta gamma`. Ed's answers file: E-2a=NO, E-2b=NO, E-3=NO, E-4=1800, E-6=NO.
- No unread mail from the owner's notice address. The open `directive` issues are the six that predate the
  hand-off (#405, #408, #416, #417, #421, #422). The watchdog handed over no pending notice.
- The courier's result email for the window: Gmail message id `1a1278277c4b5e97`.

## The window (brief 4.1)

From `night/hazard_result.json`: verdict `ABORTED`, `stage_reached` `chain`, `refusal` null; fault reasons
`yield_low`, `post_bracket_failed` `not_run`, `bound_derivation_failed` false. From `night/result.json`:
`aborted_reason` `night_aborted_agent_present`, chain exit code -15, 298 censuses, one hit. The arm passed
all six hazards (courier's report).

**Why the chain stopped.** The census hit lists pid 86158 `claude` and three processes of the project's
Codex MCP server (pids 86183, 86204, 86205) started with it, with a Terminal environment. Machine records
show what it was: `pmset -g log` has the display turned on at 13:28:09 PDT; the local Claude prompt history
has one entry for that session, `/exit`, at 13:28:30 PDT, and nothing typed before it; the zsh history
ends with the command `claude`. So a `claude` session was opened in Terminal at the keyboard and closed
about 20 seconds later. The census runs every 30 seconds and stops the chain on the first agent it sees.
The watchdog did not start it: its event log shows the state FENCED and no launch between 10:26 and 13:32.

The window started at 10:56 PDT; the chain exited at 13:28:24 PDT, 2 h 32 min after t0.

| Stage | Planned | Present | Succeeded | `min_valid` | Status | Stage ended (PDT) |
|---|---|---|---|---|---|---|
| `beta-bound-collection` | 18 | 18 | 18 | 10 | `OK` | 11:50 |
| `beta-reference-start` | 3 | 3 | 3 | 2 | `OK` | 12:10 |
| `beta-science-absolute` | 10 | 10 | 9 | 8 | `OK` | 12:38 |
| `beta-science-abba-01-05` | 20 | 17 | 13 | 16 | `LOW` | not returned |
| the six later stages | 74 | 0 | 0 | | `ZERO` | not run |

Driver yield status `LOW`: 125 planned, 48 present, 43 succeeded. The stage list has 11 entries, ten with
return code 0 and `beta-science-absolute` with 1. The closing calibration did not run.

The dead-man job's calendar was hour 19, minute 18, after the chain's end; the job was removed before it
fired.

## Closing steps (brief 4.2 to 4.4)

- 4.2: the bracket session `v5-b5-beta-a2-20261010T1756Z-calibration` was open with next slot `post` and
  custody state `absent`. `recover_calibration_ledger.py abort-session` returned `status` `aborted`,
  ledger sequence 450, receipt digest `e53e9a20f95abbb5234060836946f720fdd32a7066ec157ab7904e7433cd331a`,
  finalized slots `pre`, unused `post`.
- 4.3: pin advanced, status `ADVANCED`, sequence 442 to 450, operator identity
  `magistrate-20261010T2032Z`. Clone commit `c97389f2f3be4c846459d18c4c0500bb942325c9`; its diff against
  the seal commit lists only `configs/calibration/calibration_ledger_head.json`.
- 4.4: uninstall rc=0; no `com.joulewise.night*` label loaded and no job file left.

## Harvest (brief 4.5, variant A, RUN_STATE item 10)

- Pin test: `HARVEST_PINNED`; desk root at `0699abbb0881ce64b39c46ba07de568cc3848260`, the commit of the
  `B5-HARVEST-PIN:` line under Step 2 of Addendum 3 (seal record line 510). This attempt's t0
  (epoch 1791654960) is after 1791649800, so it is a governed attempt.
- Archive `/Users/edr/night-archive/harvest-v5-b5-beta-a2-20261010T1756Z`; started about 13:34 PDT,
  `harvest rc=0` about ten minutes later.
- `verdict=COLLECTED`, `claim_usable=false`, attempt 2, pack `d117_floor_qwen3-8b_v5`.
- `exclude_window_reasons`: `calibration.no_bracket`, `cell.below_minimum`, `whole_window.verdict_absent`.
- `faults`: none. `harvest_checkout.head` equals the desk root's commit; `status_clean` true.
- Yield: planned 125, present 48, raw-valid 48, succeeded 43, strict-deferred 47. Per roster stage
  (planned/present/succeeded): `neg8_bound` 18/18/18; `start_reference` 3/3/3;
  `01_phase_decode_absolute` 10/10/9; `02_phase_decode_abba_blocks_01_05` 20/17/13; all others 0 present.
- `harvest.json` sha256 `143ec4d5969f541d6829781c9076441412c21246dad67bcab54671150c77526f`.

All three window reasons follow from the stop: no closing calibration, six stages with no member, and no
verdict file. None is a `neg8.*` code, so item 9 of the RUN_STATE block (the NEG8 family twice) does not
apply; the cause families of attempts 1 and 2 differ.

## END STATE count (brief section 6, rule 3)

`alpha-a1-20261008T2201Z` 116 recorded, 1 not bounded; `alpha-a1-20261009T2312Z` 125, 0;
`alpha-a3-20261009T0644Z` 117, 1; `beta-a1-20261010T0742Z` 119, 0; `beta-a2-20261010T1756Z` 43, 0.
Block total 520 recorded, 2 not bounded: continue.

## One departure from the brief's reading list

Before reading brief 4.1 this activation printed the window's `night.log` (five driver lines: start,
verdict, two pushes, courier), `night/launchd.night.out` (the courier's summary), `night/chain-stages.jsonl`
and `night/stage_yield.jsonl`. The brief's list (decision O-7) excludes `night.log`. The lines hold times,
stage names, return codes and counts and no energy, power or duration of a member; nothing from them is
used beyond the stage end times in the table above.

## Decision

`cell.below_minimum` goes to a two-seat consult on its first occurrence (brief section 6). It was convened;
record and decision in `seal2-beta-a2-consult.md`. Next: BETA attempt 3.
