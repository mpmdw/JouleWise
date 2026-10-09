# Block 5, ALPHA attempt 2: arm record

Magistrate activation d2ddcd8e (Opus 5.5, headless), 2026-10-08. Structure only: paths, hashes, codes and
counts. Procedure: sections 5 and 6 of `docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`.
Why this attempt exists and why it is armed unchanged: `alpha-a1-window.md` and `alpha-a1-consult.md`.

## Desk checks (brief 5.1), all passed (about 21:43 PDT)

- The four desk helpers hash to the digests the brief lists.
- Agent check: `foreign_agents` empty, `own_seats_still_running` empty. No agent application and no
  browser open. The two consult worktrees were removed first.
- Clone clean; `git diff --name-only` against H_claim lists the three seal documents and the ledger pin.
- Ledger: `blocking` empty, no open session; pinned sequence 412.
- Clock frequency check: `passes: true` (bound 4.69 ms against the 5.0 ms limit).
- Free disk 190 GiB (88 needed). Build 25G83.
- Battery: adapter connected, not charging.
- Reference model and interpreter: generator rc=0, equal to the sealed pins (nine names).
- Machine state the consult looked at, unchanged from attempt 1: `com.apple.mediaanalysisd` (pid 98055)
  and `com.apple.photoanalysisd` (pid 81746) are loaded and running, both listed as disabled; the
  bootout of each was refused with error 150 (System Integrity Protection).

## The plan

| Item | Value |
|---|---|
| Plan id | `v5-b5-alpha-a2-20261009T0515Z` |
| Pack, attempt | ALPHA (`d117_floor_qwen3-1p7b_v5`), 2; G10 control not requested (`false`: attempt 1 left a `night/g10.json`, result `DISCHARGED`) |
| t0 | epoch 1791522900 (2026-10-08 22:15 PDT) |
| `window_max_s` | 102180 |
| Custody root | `/Users/edr/night-custody/v5-b5-alpha-a2-20261009T0515Z` |
| Runs parent | `/Users/edr/night-b5/v5-b5-alpha-a2-20261009T0515Z` |
| Staging | `/Users/edr/night-plan-staging/v5-b5-alpha-a2-20261009T0515Z` |
| Clone head | `a16db2d044c8d2cedd1f472169b879df31a22ff0` (the seal commit plus the pin advance after attempt 1) |
| `night_plan.json` sha256 | `037b1ef3f6c586c357680e2e22f0c50591e0f21b7fe0ffad3c4a6c7389981744` |
| `plan-inputs.json` sha256 | `23877b2b535bc4927a2cacb7e1043ed66eab93327a74eaf3d1aa15418e292869` |
| `chain.zsh` sha256 | `9b1a7994cf32c930b4048a4d6355caca4f731d1a3d0fa16163adff515f0070ee` |
| `window.env` sha256 | `3bd605807af545bf109760e5a0fa3feca6775b9c51697e70693f54dc41bf0a7c` |
| Thresholds sha256 | `d2e031ccb36f187a7b5a7fb7f794f194d05b98ff2c792f7186b71f52fc924eff` |
| `identity-epoch.json` sha256 | `b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607` |
| `t1-bindings.json` sha256 | `8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98` |
| `plan-record.json` sha256 | `a78ceff236439555a3192fe83dc3827f44128eb620785098b3e3348958296496` |
| `chain-check.json` sha256 | `f43ea7d3470468245d0b402df825c98cec1add2356a85eac4e470417f56fa365` |
| `schedule.json` sha256 | `322cbf4a49dd5b2c2dfafd2090b28dccb27a8cf987d0e5a5dad0ec2603ed116a` |
| `install.out` sha256 | `99143cf595a9c7b3c43c12a9aacdb2e074bbdacef1950a472eff1c3a041d955b` |

Checks of brief 5.3: plan writer `STAGED` (rc=0), no difference from the default thresholds, no pack
digest error; `chain.zsh` parses and matches its sidecar; chain check rc=0; preflight ok; schedule
written; desk seal check `no flag`, rc=0.

## Notice and install

- Arm notice: Gmail message id `1a11efaa8e47a0f4`, sent about 21:45 PDT to the owner's notice address; it
  promises that a NO received by 22:00 PDT is acted on. It carries attempt 1's outcome, the family count,
  the refused bootout and two questions that do not hold this window: `RESTART-OK` or `RESTART-NO` (may
  the Mac be restarted between windows so that the two existing disables take effect), and `SPOTLIGHT-OK`
  or `SPOTLIGHT-NO` (may `com.apple.corespotlightd` be disabled). No NO at the search after sending.
- An earlier email of this activation, Gmail message id `1a11ee6b6b3ef228` (about 21:23 PDT), reported
  attempt 1's harvest outcome and carried the watchdog's pending notice `transition-2602-hold_census`;
  `notice.ack` was written after Gmail accepted it.
- Agent check before the install: two empty lists. Install rc=0 at about 21:45 PDT (install span closes
  at epoch 1791522600). Loaded labels: `com.joulewise.night`, `com.joulewise.night.deadman`. The night
  job's arguments are the clone's interpreter, `scripts/run_night.py run --plan <the plan>`.
- Dead-man job calendar: hour 3, minute 43.
- Clone clean after the install, head unchanged.

## Next action

Read from the disk by brief section 3. Until t0 − 180 s each activation is case 1 (search once for Ed's
NO; a NO is the withdrawal of brief 5.6). After the window ends: brief section 4 for this plan id, then:

1. Tally the window's contention journal (intervals over the limit, by process name; integers and names
   only) and write it beside the attempt, as the cold ruling asks.
2. If the harvest again gives `cell.below_minimum` or a `neg8` code, this is the same cause family twice:
   registration 7.3 sends it to a consult (Sol 6.1 and Opus 5.5), not to a third arm. The consult starts
   from `alpha-a1-consult/RULING.md`; the ruling's family-count program may be run once on the new
   archive (change only the `ARCHIVE` path).
3. Read Ed's answers to the two questions. `RESTART-OK`: before any restart, one consult seat checks what
   a restart does to the block's preconditions (network time setting, ledger, automatic login, the
   magistrate's launchd job); restart only with no night job loaded; afterwards the check is that
   `launchctl print gui/501/com.apple.mediaanalysisd` and `…photoanalysisd` both fail with "Could not find
   service". `SPOTLIGHT-OK`: `launchctl disable gui/501/com.apple.corespotlightd`, effective at the same
   restart. Whatever state results is checked before every remaining arm and named in each arm notice.
