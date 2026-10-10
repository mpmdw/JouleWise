# Block 5, second seal, BETA attempt 2: arm record

Magistrate activation cbe4230e (Opus 5.5, headless), launched 2026-10-10 06:51 PDT; the arm is at 10:26 PDT.
Structure only: paths, hashes, codes and counts. Procedure: section 5 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` with the RUN_STATE top block of
2026-10-10 (items 9 to 15) and the eight differences of the block of 2026-10-09. What preceded this arm:
`seal2-beta-a1-window.md` (BETA attempt 1 is not claim-usable), `seal2-beta-a1-consult.md` (why), and
`sources-erratum/` (Erratum 2, its cold ruling, and the gate record of the third harvest pin).

This is the first attempt Erratum 2 governs: its t0, epoch 1791654960, is later than the admission time,
epoch 1791649800 (`ERRATUM-2-ADMITTED-AT: 2026-10-10T16:30:00Z` in Addendum 3 of the seal record). Both
steps of Addendum 3 were on main before the plan was written (main `2000762a7`): the erratum's digest
`b8510545…188a`, and the harvest pin `0699abbb0881ce64b39c46ba07de568cc3848260`. The desk root is checked out
at that pin and brief 4.5's test prints `HARVEST_PINNED`.

## Desk checks (brief 5.1), all passed (10:24 PDT)

- The four desk helpers hash to the digests the brief lists.
- Agent check: `foreign_agents` empty, `own_seats_still_running` empty. The application line prints
  nothing. Firefox (pid 25671, open since 22:35 PDT on 2026-10-09) is still open; it does not hold an arm,
  E-2a=NO so it was not quit, and the arm notice says so. It did not appear in the last window's
  contention tally.
- Clone clean at `86f4d0853292c8acbac0b218c5136970d1b20351` (the seal commit plus the pin at sequence 442);
  `git diff --name-only` against the claim head lists the three seal documents and the ledger pin.
- Ledger: `blocking` empty, no open session; pinned sequence 442.
- Clock frequency check: `passes: true` (bound 4.69 ms against the 5.0 ms limit).
- Free disk 219 GiB (91 needed). Build 25G83.
- Battery: adapter connected, not charging, current 0 mA.
- Reference model and interpreter: generator rc=0, equal to the sealed pins (nine names).
- No restart (boot time 2026-09-18), no daemon restart, no Wi-Fi toggle and no owner login since the last
  window: the last keyboard or trackpad event was 42,395 s before the check. So the 60-minute settle of
  RUN_STATE item 5 does not apply. This activation's own desk work (a test suite, two review seats) ended
  at about 10:23 PDT, 33 minutes before t0; the arm's own contention dwell measures what remains.
- `/private/tmp` holds 3,717,627 entries, so the midnight rule applies: t0 10:56 PDT is inside 00:10 to
  17:15, and the chain is expected to end at about 17:00 PDT, clear of 00:00 and of the 05:15 to 06:45
  scan hour.
- No unread mail from the owner's notice address; the open `directive` issues are the six that predate the
  hand-off; no stand-down request.

## The plan

| Item | Value |
|---|---|
| Plan id | `v5-b5-beta-a2-20261010T1756Z` |
| Pack, attempt | BETA (`d117_floor_qwen3-8b_v5`), attempt 2; G10 control not requested (`false`) |
| t0 | epoch 1791654960 (2026-10-10 10:56 PDT) |
| `window_max_s` | 112620 |
| Custody root | `/Users/edr/night-custody/v5-b5-beta-a2-20261010T1756Z` |
| Runs parent | `/Users/edr/night-b5/v5-b5-beta-a2-20261010T1756Z` |
| Staging | `/Users/edr/night-plan-staging/v5-b5-beta-a2-20261010T1756Z` |
| Measurement clone | `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` |
| Clone head | `86f4d0853292c8acbac0b218c5136970d1b20351` |
| `night_plan.json` sha256 | `e0b85a26b5644c59d45255e93d9317b38d2ea3712130b43b1ea5adfe38a28f06` |
| `plan-inputs.json` sha256 | `525020e6752958fffb8115b6ae9d1fad3ab2a0032146447af82d377795f6aa84` (the plan record's `inputs_sha256` field reads `209d2d49ef2cd6b52701b9077aa0b92534ee3a72a9b06dc4af203e344bcbcba1`) |
| `chain.zsh` sha256 | `985456a6268cc4169f1f34f664e3753c16521bda499c7a4adc5ee5c11bd73d96` |
| `window.env` sha256 | `e12df2ae2ccb1674e88ba15c42e362b659ac1e8180c3a952cc5b5530d6da3734` |
| `inputs-summary.json` sha256 | `e899f3ac7cbb30683d0aa5cb80255c6d4f5bb2dd275dc76594ecf912e2258f25` |
| `plan-record.json` sha256 | `0d1350c5f6d2d099c0b8995d9be830af520ecd760a434780f22b81842315fbc7` |
| `chain-check.json` sha256 | `615c3d529af337a66ff3711262f3adddb7b2d27fe69bad6e0cb6fca87b7033ce` |
| `schedule.json` sha256 | `9a963ab735855317430ba4455cb775c0b57c6aa0d0137bd27e7b8bd4697b222c` |
| `install.out` sha256 | `b14ae3dcb9410d6eb1312d58d33fbf5f7863ec0331488cfdcdf3020a9fb004c7` |

Checks of brief 5.3: desk identity `WRITTEN`; plan writer `STAGED` (rc=0), no difference from the default
thresholds, no pack digest error; `chain.zsh` parses and matches its sidecar; chain check rc=0; preflight
ok; schedule written; desk seal check against the claim head `c27485347`: `no flag`, rc=0.

## Notice and install

- Arm notice: Gmail message id `1a126da3f75861a3`, sent about 10:26 PDT to the owner's notice address; it
  promises that a NO received by 10:41 PDT is acted on. It carries BETA attempt 1's outcome (verdict
  `COLLECTED`, not claim-usable, 125 of 125 raw-valid, window-removing code `neg8.screen_failed`), why
  that window was removed, what Erratum 2 changes and that it is not applied backwards, the scan hour, and
  that Firefox is open. No NO at the search after sending.
- The watchdog's two pending notices of this activation's launch went out earlier in Gmail message
  `1a1261625fed1c07`, and the acknowledgement was written then.
- Agent check before the install: two empty lists. Install rc=0 at about 10:26 PDT. Loaded labels:
  `com.joulewise.night`, `com.joulewise.night.deadman`. The night job's arguments are the clone's
  interpreter, `scripts/run_night.py run --plan <the plan>`; its process type is `Interactive`; its
  calendar is month 10, day 10, 10:56.
- Dead-man job calendar: hour 19, minute 18 (30,120 s after t0, after the expected chain end).
- Clone clean after the install, head unchanged.

## Gates that ran in this activation, and what each caught that touches a number

- The harvest of BETA attempt 1 (pinned program): removed the window with `neg8.screen_failed`. The
  counts-only programs then showed the removal had no physical cause.
- The two-seat consult: both seats asked for the one count that located the cause.
- The fix seat's reading of the registration: caught that the first decision (fix, re-harvest attempt 1,
  go to GAMMA) would have applied a new rule to a completed window.
- The erratum's refuter: two blockers (the pin rules would have re-harvested attempt 1 under the new rule
  anyway; a rescued window would have been claim-usable with no drift allowance any consumer could read)
  and four rule-content corrections (the trigger was wider than the diagnosed state; schema-v1 manifests
  bypass authentication; the stand-in for the stored-bracket comparison named a check that does not exist).
- The cold judge: upheld them and wrote the rule; ruled the rule is not applied to attempt 1.
- The cold Fable pass and the independent executing review of the program: no blocker; five test gaps,
  one of which (the clean-bound requirement) would have let a later regression pass a screen on the wrong
  bound unnoticed.
- The whole suite: one real consequence (a call-site fence), the rest timing under load.
- Nothing to propose for deletion from this session.

## Next action

Read from the disk by brief section 3 with RUN_STATE items 9 to 15. Until t0 − 180 s each activation is
case 1 (search once for the owner's NO; a NO is the withdrawal of brief 5.6). After the window ends: brief
section 4 for this plan id. Before the harvest, confirm that the desk root is at
`0699abbb0881ce64b39c46ba07de568cc3848260` and that this is the `B5-HARVEST-PIN:` line of Addendum 3 step 2;
then harvest by variant A. Then:

1. Read `derived/neg8-screen.json` with `seal2-beta-a1-consult/screen_branch_count.py` (change the plan id
   in its path) and record `rescreen.evaluated`, the decision word, and whether `rescreen.reference_source`
   names `claim_campaign_manifests_authenticated`; if it does, this is the first harvest on the erratum's
   path and the window record says so. Tally the contention journal as before.
2. `claim_usable` true: BETA is done. Before GAMMA's first arm do item 8 of the RUN_STATE block of
   2026-10-09 (the dead-man job's 16,560 s against GAMMA's stage order), then arm GAMMA attempt 1 (81 GiB
   free; the midnight rule: t0 by 17:15 or from 00:10; prefer a chain that is not running from 05:15 to
   06:45; the settle if the owner was at the Mac).
3. `claim_usable` false with any `neg8.*` window reason: this is BETA's second removal in the NEG8 family,
   so a two-seat consult comes before attempt 3 (brief section 6 rule 1). Any other reason: the brief's
   table.
4. If Ed has restarted the Mac by then (`sysctl -n kern.boottime`), do item 6 of the RUN_STATE block of
   2026-10-09 before the next arm.
