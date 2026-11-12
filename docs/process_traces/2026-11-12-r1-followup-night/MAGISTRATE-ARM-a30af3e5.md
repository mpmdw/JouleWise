# R1 follow-up night: arm by magistrate a30af3e5 (2026-11-12)

Headless magistrate a30af3e5 (Opus 5.5), interim lead under RUN_STATE items 289, 291, 292 and 295. Arm procedure: `docs/process_traces/2026-11-12-air-offline-handoff/arm-item-draft.md` with `__NIGHT_SHA__` = `99622e96cf83d578672747a90db1d8128a57eae9` and `__SMOKE_ITEM__` = RUN_STATE 296. Every time below comes from `date`.

## Smoke 2 (item 294) check: PASS

- OUT `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-followup-smoke-20261112T210906Z`. The run closed at 14:24 PST, and the fence is gone.
- Receipt `{"error": null, "fresh_soak": true, "parts": {"A": true, "B": false}, "parts_requested": "A", "rc": 0}`.
  - All 20 steps returned rc 0, and `close-volumes` ran once.
  - Every feed is `proven_stopped`, and every feed file's sha256 matches. The script printed `RECEIPT ASSERTS OK`, check rc 0.
- Soak: rc 0. `soak_reference.json` sha256 `c0d2f44054ed4d09f22c9ef00dd88bf71277c9b470ec01aed6d9838e51c56ff5`. Over the last 1,200 s, detrended:

  | Sensor | Mean | sd | Slope | State |
  |---|---|---|---|---|
  | TV0h | 34.056 °C | 0.0072 °C | −0.0010 °C/min | settled |
  | Th0C | 26.070 °C | 0.037 °C | −0.0089 °C/min | settled |

  The idle soak's busiest moment used 2.20 cores, and the longest gap between samples was 1.04 s.
- G0 (step D, `part-a/step_D_prefill_10k_decode_4096/smoke_part_a.json`): **released**, `duration_s` 837.331 (bar 1,200), `admission_s` 1,910.7, `rearmed` true.
  - At entry: TV0h 84.18, Th0C 65.78, Tf08 70.02 °C; slope −7.81 °C/min.
  - Reference: the step-D window's own capture (`align-v4-r1-step-d`, 60 s): fast 34.664, slow 32.635 °C.
  - Release: fast 34.429, slow 30.174 °C. Release minus reference: fast −0.24 °C, slow −2.46 °C. Both are under the +1.0 °C bands.
  - Slope at release: −0.147 °C/min, against the 0.2 °C/min bar.
  - Both temperatures were inside their bands with margin, so the slope condition was presumably the one that decided the release, as in item 286. The release record does not name the deciding condition, so this is an inference.
  - Tf08 is recorded at entry only.
- Launch plist `ProcessType` `Interactive`. No `com.joulewise.align-r0*` label is loaded. `night.lock` was left as found (pid 11787, dead, `r1-smoke-close`).

## #741 CI re-run 43257905641 (attempt 2)

Read with `cmpjobs.sh 741`. Failing shards 2, 3, 5, 6, 8, 10, 11 and 12 show `new=0` against `base.ids` (with RL-97's three ids). Shard 4 and all other jobs are green.

## Arm checks (all passed)

1. Only `com.joulewise.magistrate` was loaded. There was no night plist, no fence, no High Power marker and no `$M/.align-r1-high-power`.
   - No powermetrics, km003c or hazard process was running, and no BYTES job.
   - The only claude/codex processes were this session and its codex MCP adapter.
2. `night.lock`: pid 11787 dead, no `lsof` holder, `edr -rw-------`. Left as found.
3. Power and host:
   - AC power, 100%, charged; ioreg `ExternalConnected` Yes, `IsCharging` No, `InstantAmperage` 0.
   - powermode 0, and both pmset sudo rules are present. No external disk.
   - `Network Time: Off`; kernel `raw_word` 0. Free disk 97 GiB.
4. `$M` was clean at `bb6394f2b`, with no old packet. It was fetched and detached to `99622e96c`, and HEAD was verified.
   - `bb6394f2b` and `683dfe654` are ancestors. mlx 0.31.2, mlx_lm 0.31.3, transformers 5.12.1.
   - `verify_r1_executed_sources` returned `99622e96c…`.
5. The two RL-89 lines:
   - (a) `RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad`
   - (b) `RL-89 RULING OK 1fdd980c91ceca6ee3907191b499f0108ca84b8709648a638bd49808a298eba3 TV0h Th0C 95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad`
6. Item (c): the wrapper is in the commit. `sudo -n -l /bin/kill` returned rc 0, and the argv-shape check returned rc 0.

## D-7 packet

- There was no old packet. `prepare` returned rc 0 in 17.79 s real time.
- Weight roots, in seconds: 30B 6.3, 1.5B 0.4, 27B 10.8.
- **PACKET_SHA256 `8d63766da71bcc85ade0a60672758793fe8b3c3a490dad405c948a85f232eab9`**. The script printed `PACKET OK`.
- `$M` porcelain shows exactly `?? .align-r1-prepare.json`.

## Plan

- Custody `S=/Users/edr/night-align/r1fu-20261112T223055Z`.
- Plan `align-r1-20261112T2251Z`, plan sha256 `4877bdb9eec5ae09bbaa20d2044aa8db458a9530cd4efa6c5910d1948a70b8d4`. `arm.json` sha256 `52dbce43b99de50d8f011f7505fb4091e5526e36c9e4714f69cf37a36d839c0c` (copy beside this file).
- t0 1794523860 = **Thu 12 Nov 14:51:00 PST** (22:51:00Z). That is now + 20 min, rounded up, and ≤ T0MAX 1794540360. It is earlier than 19:26, which Fable F6 prefers.
- `window_max_s` 126,480 (RL-72 E2). Latest end = t0 + W + 300 = 1794650640 = **Sat 14 Nov 02:04 PST**. The dead-man fires at 03:04 PST Sat (1794654240).
- The batch window is crossed once, at 1794599100 (Fri 13 Nov 11:45 PST), inside the span. The driver waits it out.
- `D-7 ARM RECORD OK 8d63766d…eab9`. The only `arm.json` flag is `disk.allocation_unsized; shared headroom and live disk floor remain`. `r1.prepare_packet_absent_at_arm` is not among the flags.
- `PLAN OK align-r1-20261112T2251Z 1794523860 126480`.
  - `receipt_class` HAZARD_PACK.
  - `repo_head` = `measurement_head` = night sha.
  - No `ac_powermode` key.
- Render: preflight ok. Every plist is `ProcessType` Interactive. Night calendar 11/12 14:51; dead-man 03:04.
- The arm notice went to Ed via Gmail (message `1a1d1e2fd06047f0`) at about 14:31 PST, before the install. `notice.ack` was written.
  - **Correction:** the notice's "expected end without a redo, about 14:20 PST Fri" was a rough figure of mine.
  - The draft's soft "likely redo" mark is T0 + 70,000 s = Fri 13 Nov 10:18 PST, plus up to 5,400 s for the 11:45 batch-window wait.
  - The bounds that matter are the latest end and the dead-man time above.

## Install

- Before the install: no unread mail from Ed, no `standdown.request`, and the KM003C enumerated on USB ("POWER-Z KM003C").
- `arm_align_r1.py install`: **rc 0** at 14:32:48 PST (epoch 1794522768). That is before the install cutoff, 14:46:00 PST (1794523560).
  - `com.joulewise.night` and `com.joulewise.night.deadman` are loaded, together with `com.joulewise.magistrate`.
  - The rendered plists are all `ProcessType` Interactive: night `53bd01a9…a7a9`, deadman `d942cf7e…4acc`, probe `af219756…f6d5`.
- `D-7 packet unchanged since prepare`.
- Next: `pmset displaysleepnow`, this commit, then exit. No Codex child was started, and the session's codex MCP adapter ends with it.
