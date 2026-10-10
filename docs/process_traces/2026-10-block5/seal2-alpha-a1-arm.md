# Block 5, second seal, ALPHA attempt 1: arm record

Magistrate activation 1aed44f9 (Opus 5.5, headless), 2026-10-09. Structure only: paths, hashes, codes and
counts. Procedure: sections 5 and 6 of `docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`
with the eight differences of the RUN_STATE top block of 2026-10-09 15:45. What preceded this arm (the
erratum, the second seal, the second clone, the rehearsal): `alpha-a3-consult.md`, `corpus18-erratum/`,
`second-clone.md`.

## Desk checks (brief 5.1), all passed (15:41 PDT)

- The four desk helpers hash to the digests the brief lists.
- Agent check: `foreign_agents` empty, `own_seats_still_running` empty. No agent application and no
  browser open.
- Clone clean; `git diff --name-only` against the claim head lists the three seal documents and the
  ledger pin.
- Ledger: `blocking` empty, no open session; pinned sequence 422.
- Clock frequency check: `passes: true` (bound 4.69 ms against the 5.0 ms limit).
- Free disk 204 GiB (91 needed). Build 25G83.
- Battery: adapter connected, not charging.
- Reference model and interpreter: generator rc=0, equal to the sealed pins (nine names).
- The Mac has not been restarted (boot time 2026-09-18); `mediaanalysisd`, `photoanalysisd` and
  `corespotlightd` are running. No daemon restart, Wi-Fi toggle or login in the last hour, so no settle
  is owed.
- `/private/tmp` is not small (5,222,549 entries), so the midnight rule applies: the chain is expected to
  end about six hours after t0, at about 22:15 local, before the 00:00 job.

## The plan

| Item | Value |
|---|---|
| Plan id | `v5-b5-alpha-a1-20261009T2312Z` |
| Pack, attempt | ALPHA (`d117_floor_qwen3-1p7b_v5`), attempt 1 of the second seal; G10 control not requested (`false`: the first seal's attempt 1 left a `night/g10.json`, result `DISCHARGED`) |
| Members | 125 (corpus stage `alpha-bound-collection`: 18; the rendered chain carries `--max-failures 18` twice, the stage and its retry) |
| t0 | epoch 1791587520 (2026-10-09 16:12 PDT) |
| `window_max_s` | 110220 |
| Custody root | `/Users/edr/night-custody/v5-b5-alpha-a1-20261009T2312Z` |
| Runs parent | `/Users/edr/night-b5/v5-b5-alpha-a1-20261009T2312Z` |
| Staging | `/Users/edr/night-plan-staging/v5-b5-alpha-a1-20261009T2312Z` |
| Measurement clone | `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` |
| Clone head | `39665b8cb8ce841b1345c9b39b10022e0f92dfa4` (the seal commit `be6525e5a` plus the carried pin) |
| `night_plan.json` sha256 | `1bba17e6cf32ed05d342aebbeeac31d822bfe034f5c00204509c00b3021e1019` |
| `plan-inputs.json` sha256 | `7c94422a3288077e8a1c0ecec6eef83762f649e0deebf945b38fe9f0aae2ffd4` |
| `chain.zsh` sha256 | `3fcb56c8df9dc9e6a5d8026cef80982a7360413615d3a56b7aee99cb4730bb6f` |
| `window.env` sha256 | `edcf77c49fad9d05389b0c03410a885f3d6ca6d8a9ea9f81fc89ebd3abaca5bc` |
| `identity-epoch.json` sha256 | `b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607` |
| `t1-bindings.json` sha256 | `8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98` |
| `inputs-summary.json` sha256 | `c649aa1cbdebc955423f322c7555c532cdf554bab8198021a88550db03a10bae` |
| `plan-record.json` sha256 | `5ca1413ea5287c8b1b5f30873f4087309638d3e74498991ba339d0c116b5bbdf` |
| `chain-check.json` sha256 | `6515ce7257e30d7f14fcfdcd7dfbcbdfa6e903a960e6c441a1b9375748000615` |
| `schedule.json` sha256 | `cad34620c55ea7f7dfe214be6474f1f3434b7a03d96adf8b42768548aeff74b6` |
| `install.out` sha256 | `b104b60a66e99685d6072a90c2ca4018e78e09cad0262b0250f3f19ccb8567f2` |

Checks of brief 5.3: plan writer `STAGED` (rc=0), no difference from the default thresholds, no pack
digest error; `chain.zsh` parses and matches its sidecar; chain check rc=0; preflight ok; schedule
written; desk seal check against the new claim head `c27485347`: `no flag`, rc=0.

## Notice and install

- Arm notice: Gmail message id `1a122d5041ccf218`, sent about 15:42 PDT to the owner's notice address; it
  promises that a NO received by 15:57 PDT is acted on. It carries the superseded attempt 3's outcome,
  what changed under the second seal, the rehearsal's result, and the request not to restart the Mac
  until the result email. No NO at the search after sending. The watchdog had no pending notice at this
  point (the morning's yield notice was acknowledged after Gmail message `1a120c4169df6206`).
- Agent check before the install: two empty lists. Install rc=0 at about 15:42 PDT. Loaded labels:
  `com.joulewise.night`, `com.joulewise.night.deadman`. The night job's arguments are the new clone's
  interpreter, `scripts/run_night.py run --plan <the plan>`; its process type is `Interactive`; its
  calendar is month 10, day 9, 16:12.
- Dead-man job calendar: hour 23, minute 54 (27,720 s after t0, after the chain's expected end).
- Clone clean after the install, head unchanged.

## Next action

Read from the disk by brief section 3. Until t0 − 180 s each activation is case 1 (search once for Ed's
NO; a NO is the withdrawal of brief 5.6). After the window ends: brief section 4 for this plan id (the
harvest is variant A: the pin test prints `HARVEST_PINNED` for the desk root at `224a264c5`), then:

1. Read the harvest's `derived/neg8-corpus-physics.json` structure with a program that prints counts only
   (`members_bound`, `members_kept`, the number under `beyond_cap`, the number dropped, `problems`), as
   the rehearsal record in `second-clone.md` did, and write it into the window record: it is the first
   claim window through the cap rule.
2. Tally the contention journal (intervals over the limit, by process name; integers and names only).
3. `claim_usable` true: ALPHA is done; arm BETA attempt 1 (91 GiB free needed; the midnight rule of the
   RUN_STATE block). Otherwise the brief's table by window reason; the first seal's three attempts do
   not count toward the same-cause rule.
4. If Ed has restarted the Mac by then (`sysctl -n kern.boottime`), do the RUN_STATE block's item 6
   before the next arm.
