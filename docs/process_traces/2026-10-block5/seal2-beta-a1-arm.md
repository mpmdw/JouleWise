# Block 5, second seal, BETA attempt 1: arm record

Magistrate activation e33d5695 (Opus 5.5, headless), launched 2026-10-09 23:11 PDT; the arm is on
2026-10-10. Structure only: paths, hashes, codes and counts. Procedure: section 5 of
`docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` with the eight differences of the
RUN_STATE top block of 2026-10-09 15:45. What preceded this arm: `seal2-alpha-a1-window.md` (ALPHA attempt 1
is claim-usable; the owner's session that held this arm; the settle).

## The settle and the midnight rule

The owner's interactive session (pid 25621) was last seen at 23:03:49 PDT and was gone at 23:11 PDT. The
display was put to sleep at 23:15 PDT. No plan was written before 00:11 PDT. At 00:11 PDT the HID idle time
read 5,626 s (last keyboard or trackpad event about 22:37:30 PDT), so nothing touched the Mac during the
60 minutes. The daily walk of `/private/tmp` at 00:00 PDT had passed; t0 is 00:42 PDT, inside the range
00:10 to 17:15.

## Desk checks (brief 5.1), all passed (00:11 PDT)

- The four desk helpers hash to the digests the brief lists.
- Agent check: `foreign_agents` empty, `own_seats_still_running` empty. The application line prints
  nothing. Firefox (pid 25671, open since 22:35:20 PDT on 2026-10-09) is still open; it does not hold an
  arm, E-2a=NO so it was not quit, and the arm notice says so.
- Clone clean at `ff0dbc7e5ace4e0bc6da14cafdf3b611caf39856`; `git diff --name-only` against the claim head
  lists the three seal documents and the ledger pin.
- Ledger: `blocking` empty, no open session; pinned sequence 432.
- Clock frequency check: `passes: true` (bound 4.69 ms against the 5.0 ms limit).
- Free disk 231 GiB (91 needed). Build 25G83.
- Battery: adapter connected, not charging, current 0 mA.
- Reference model and interpreter: generator rc=0, equal to the sealed pins (nine names).
- The Mac has not been restarted (boot time 2026-09-18); `mediaanalysisd`, `photoanalysisd` and
  `corespotlightd` are running.
- `/private/tmp`: 5,222,598 entries and 151 GiB at 23:16 PDT (before the 00:00 walk; not counted again).
- No unread mail from the owner's notice address; the open `directive` issues are the six that predate
  the hand-off; main unchanged at `1d4be995c`; no stand-down request.

## The plan

| Item | Value |
|---|---|
| Plan id | `v5-b5-beta-a1-20261010T0742Z` |
| Pack, attempt | BETA (`d117_floor_qwen3-8b_v5`), attempt 1; G10 control not requested (`false`: the first seal's attempt 1 left a `night/g10.json`) |
| Members | 125 (corpus stage `beta-bound-collection`: 18) |
| t0 | epoch 1791618120 (2026-10-10 00:42 PDT) |
| `window_max_s` | 112620 |
| Custody root | `/Users/edr/night-custody/v5-b5-beta-a1-20261010T0742Z` |
| Runs parent | `/Users/edr/night-b5/v5-b5-beta-a1-20261010T0742Z` |
| Staging | `/Users/edr/night-plan-staging/v5-b5-beta-a1-20261010T0742Z` |
| Measurement clone | `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` |
| Clone head | `ff0dbc7e5ace4e0bc6da14cafdf3b611caf39856` (the seal commit `be6525e5a` plus the pin at sequence 432) |
| `night_plan.json` sha256 | `3a0b51247a32c155f35bde2b682e791ce575048f947bb08f1a47779e08df74f3` |
| `plan-inputs.json` sha256 | `1be091fd6345fcba29bd1ba8ab1b289c6faa9e24ed2b103f08e0848f0ad889f4` (the plan record's `inputs_sha256` field reads `ac74b0550c67f234a3645eebdb5f5156014d8bd9705efe17cfd618afa2e2f126`) |
| `chain.zsh` sha256 | `5c068ac0ff4f1a41e1a91a63f5d92112b4650bcbd72caea954a0fdf27634fda4` |
| `window.env` sha256 | `3c2f74bc44ec2a41c51c112d87dd82f5b578c93ec9b1807700a6204ea26de641` |
| Pack sha256 | `6bfbecc731107238539ab76890b4fa32bd5937eb4ebe5bbe06c3f3ec79bc78dd` |
| `identity-epoch.json` sha256 | `b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607` |
| `t1-bindings.json` sha256 | `8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98` |
| `inputs-summary.json` sha256 | `a5a8ebca7ed1debc386a47e0c42446f3f964a3719dc39a029d570f4182a1277a` |
| `plan-record.json` sha256 | `8b6c8def07a44eb3d9afcd4aae042e4016cf7aa02ddddb2e843e66fe77ea4d4b` |
| `chain-check.json` sha256 | `615c3d529af337a66ff3711262f3adddb7b2d27fe69bad6e0cb6fca87b7033ce` |
| `schedule.json` sha256 | `6b8aded784d29f3f86fbbcf53590f2f83ef0ec1dfc028d3040bb4ebff6d6030e` |
| `install.out` sha256 | `0b87807c08f53d68d2d645e0779476e7b7fbd63abe36b81af42cf3bc5da8897b` |

Checks of brief 5.3: desk identity `WRITTEN`; plan writer `STAGED` (rc=0), no difference from the default
thresholds, no pack digest error; `chain.zsh` parses and matches its sidecar; chain check rc=0; preflight
ok; schedule written; desk seal check against the claim head `c27485347`: `no flag`, rc=0.

## Notice and install

- Arm notice: Gmail message id `1a124a818741e25d`, sent about 00:12 PDT to the owner's notice address; it
  promises that a NO received by 00:27 PDT is acted on. It carries ALPHA attempt 1's outcome (verdict
  `COLLECTED`, claim-usable, 125 of 125 raw-valid, no window-removing code), says that Firefox is open,
  and says why the arm came two hours after the harvest. No NO at the search after sending. The watchdog
  had no pending notice, so no acknowledgement file was written.
- Agent check before the install: two empty lists. Install rc=0 at about 00:12 PDT. Loaded labels:
  `com.joulewise.night`, `com.joulewise.night.deadman`. The night job's arguments are the clone's
  interpreter, `scripts/run_night.py run --plan <the plan>`; its process type is `Interactive`; its
  calendar is month 10, day 10, 00:42.
- Dead-man job calendar: hour 9, minute 4, which is 30,120 s after t0 (the erratum's figure for BETA,
  after the projected chain end of 21,328 s); a firing before the deadline stands down.
- Clone clean after the install, head unchanged.

## Next action

Read from the disk by brief section 3. Until t0 − 180 s each activation is case 1 (search once for Ed's
NO; a NO is the withdrawal of brief 5.6). After the window ends: brief section 4 for this plan id (close
an open session if any, advance the pin, uninstall, then the harvest, variant A: the pin test prints
`HARVEST_PINNED` for the desk root at `224a264c5`), then:

1. Read `derived/neg8-corpus-physics.json` with a program that prints counts only, and tally the
   contention journal with `/Users/edr/night-plan-staging/b5-bench/contention_tally.py`, as the ALPHA
   record did; note whether Firefox appears in the tally.
2. `claim_usable` true: BETA is done; before GAMMA's first arm do item 8 of the RUN_STATE block (compare
   16,560 s after t0 with GAMMA's rendered stage order; if it falls in the end triplet, shift t0 by a few
   minutes), then arm GAMMA attempt 1 (81 GiB free needed; the midnight rule; the settle if the owner was
   at the Mac). Otherwise the brief's table by window reason.
3. If Ed has restarted the Mac by then (`sysctl -n kern.boottime`), do the RUN_STATE block's item 6
   before the next arm.
