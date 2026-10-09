# Block 5, ALPHA attempt 3: arm record

Magistrate activation 0705bcd5 (Opus 5.5, headless), 2026-10-08. Structure only: paths, hashes, codes and
counts. Procedure: sections 5 and 6 of `docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`.
Why this attempt exists, and the cure that preceded it: `alpha-a2-window.md`.

## Desk checks (brief 5.1), all passed (about 23:10 PDT)

- The four desk helpers hash to the digests the brief lists.
- Agent check: `foreign_agents` empty, `own_seats_still_running` empty. No agent application and no
  browser open. This activation started no seat.
- Clone clean; `git diff --name-only` against H_claim lists the three seal documents and the ledger pin.
- Ledger: `blocking` empty, no open session; pinned sequence 412.
- Clock frequency check: `passes: true` (bound 4.69 ms against the 5.0 ms limit).
- Free disk 189 GiB (88 needed). Build 25G83.
- Battery: adapter connected, not charging.
- Reference model and interpreter: generator rc=0, equal to the sealed pins (nine names).
- Machine state: `fseventsd` restarted and quiet (pid 69896, see `alpha-a2-window.md`);
  `com.apple.mediaanalysisd` (pid 98055) and `com.apple.photoanalysisd` (pid 81746) still running.

## The plan

| Item | Value |
|---|---|
| Plan id | `v5-b5-alpha-a3-20261009T0644Z` |
| Pack, attempt | ALPHA (`d117_floor_qwen3-1p7b_v5`), 3; G10 control not requested (`false`: attempt 1 left a `night/g10.json`, result `DISCHARGED`) |
| t0 | epoch 1791528240 (2026-10-08 23:44 PDT) |
| `window_max_s` | 102180 |
| Custody root | `/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z` |
| Runs parent | `/Users/edr/night-b5/v5-b5-alpha-a3-20261009T0644Z` |
| Staging | `/Users/edr/night-plan-staging/v5-b5-alpha-a3-20261009T0644Z` |
| Clone head | `a16db2d044c8d2cedd1f472169b879df31a22ff0` (unchanged since attempt 2) |
| `night_plan.json` sha256 | `e2c7d8f5715e2f7998ad170c95e332cfec8d5d5983b22edacbdada60b910cfc2` |
| `plan-inputs.json` sha256 | `26a18caeddfd2cb358300a09af25c094e8fe386ad1f5ae8ab867193c7c2e37b5` |
| `chain.zsh` sha256 | `9985788ffbc8b1db7dd2f71ced031d087815c28e01c6c783f2fd65954c136a12` |
| `window.env` sha256 | `61739a4ec5ebe3e09a917db312c753a940d8e7849a30d166d369590167444e8e` |
| `identity-epoch.json` sha256 | `b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607` |
| `t1-bindings.json` sha256 | `8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98` |
| `inputs-summary.json` sha256 | `6de8ad883e73850d4f49afd1bd3b3d832b99fe23fa0e7d2b86ad04dd84e07632` |
| `plan-record.json` sha256 | `1b24d160b02ed257bf1c129a9c2b5a8f2e11a595101f27f8268eff82bd299944` |
| `chain-check.json` sha256 | `f43ea7d3470468245d0b402df825c98cec1add2356a85eac4e470417f56fa365` |
| `schedule.json` sha256 | `5d962f04b35321b8e33acfa30013b6e55b9fdf538eed1f8a023d92cb180fa103` |
| `install.out` sha256 | `bfae2076a93b1ffc4a2e57d36a10ca306d38d7941828b0042c037c0f6c9c3d27` |

Checks of brief 5.3: plan writer `STAGED` (rc=0), no difference from the default thresholds, no pack
digest error; `chain.zsh` parses and matches its sidecar; chain check rc=0; preflight ok; schedule
written; desk seal check `no flag`, rc=0.

## Notice and install

- Arm notice: Gmail message id `1a11f4c8ca81d791`, sent about 23:14 PDT to the owner's notice address; it
  promises that a NO received by 23:29 PDT is acted on. It carries attempt 2's outcome (verdict `NULL`,
  not claim-usable, no chain, window reason `window.null`), the refusing hazard and its cure, and the two
  open questions again (`RESTART-OK` or `RESTART-NO`; `SPOTLIGHT-OK` or `SPOTLIGHT-NO`). No NO at the
  search after sending. The watchdog had no pending notice, so no `notice.ack` was written.
- Agent check before the install: two empty lists. Install rc=0 at about 23:14 PDT. Loaded labels:
  `com.joulewise.night`, `com.joulewise.night.deadman`. The night job's arguments are the clone's
  interpreter, `scripts/run_night.py run --plan <the plan>`; its calendar is month 10, day 8, 23:44.
- Dead-man job calendar: hour 5, minute 12.
- Clone clean after the install, head unchanged.

## Next action

Read from the disk by brief section 3. Until t0 − 180 s each activation is case 1 (search once for Ed's
NO; a NO is the withdrawal of brief 5.6). After the window ends: brief section 4 for this plan id, then:

1. If the arm refuses on contention again, this is the same refusing hazard on two consecutive attempts:
   registration 7.3 sends it to a consult (Sol 6.1 and Opus 5.5), not to a fourth arm. Its evidence starts
   from the two arm records and the `spawned corecaptured` counts in `alpha-a2-window.md`.
2. If a chain ran: tally the window's contention journal (intervals over the limit, by process name;
   integers and names only) and write it beside the attempt, as the cold ruling of attempt 1 asks. A
   harvest that again gives `cell.below_minimum` or a `neg8` code is not the same cause key as attempt 2,
   but the brief's table sends those codes to a consult on every occurrence; it starts from
   `alpha-a1-consult/RULING.md`.
3. Read Ed's answers to the two questions, as `alpha-a2-arm.md` item 3 describes.
