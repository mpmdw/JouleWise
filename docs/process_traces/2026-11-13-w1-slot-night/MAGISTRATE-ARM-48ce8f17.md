# Slot-producing R1 follow-up night: arm by magistrate 48ce8f17 (2026-11-13)

Headless magistrate 48ce8f17 (Opus 5.5) did item 306's activation 2. The procedure was `docs/process_traces/2026-11-12-air-offline-handoff/arm-item-draft.md`, with item 306's substitutions and `__NIGHT_SHA__` = `a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe`. Part A was launched by item 307 (magistrate c962500e). Every time below comes from `date`.

## Part A check: PASS

- OUT `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-followup-smoke-20261113T134059Z`. The runner closed at 06:36 PST. The fence is gone, and no `com.joulewise.align-r0*` label is loaded. The launch plist's `ProcessType` is `Interactive`.
- Receipt `{"error": null, "fresh_soak": true, "parts": {"A": true, "B": false}, "parts_requested": "A", "rc": 0}`.
  - All 20 steps returned rc 0, and `close-volumes` ran once.
  - Every feed is `proven_stopped`, and every feed file's sha256 matches. The script printed `RECEIPT ASSERTS OK`.
- Soak rc 0. `soak_reference.json` sha256 `52bfbb5a5888256c3392b8c99b3cc18ba0727a6e55852c431af3ce507f660fd1`.
- G0, step D (`smoke_part_a.json` sha256 `4a2624ed…1e67`): **released**.
  - `duration_s` 113.18 against the 1,200 s cap; `admission_s` 1,190.4; `rearmed` true.
  - Reference, the step-D member's own 60 s capture: TV0h 34.696 °C, TVh0 34.696 °C.
  - Release: TV0h 35.365 °C (+0.669), TVh0 35.000 °C (+0.304). Both bands are +1.0 °C.
  - Slope at release 0.0 °C/min, against the ±0.2 °C/min bar.
  - At entry: TV0h 84.34, TVh0 84.34, Tf08 69.61 °C; entry slope +2.31 °C/min.
  - The G0 record names only TV0h / TVh0. Neither return-to-lead condition of item 306 applies: no other key is named, and there was no timeout.

## Finding: TVh0 is TV0h floored to 5 °C steps while the die cools (reported, not decided)

Source: the step-D member's `outputs/align_thermal.jsonl` (sha256 `32d6b2a0…110c`), 642 one-second readings. Raw SMC bytes are in each reading.

- In 312 of the 642 readings, TVh0 equals TV0h bit for bit. This holds at rest below 35 °C and under load: 505–520 s, 83–85 °C, equal.
- In the other readings TVh0 takes only the values 35, 40, 45, 50, 55, 60 and 85 °C, raw `0000xx42`, so whole numbers. In the cool-down after step D, TVh0 = 5 × ⌊TV0h / 5⌋:
  - TV0h 63.79 → TVh0 60;
  - 58.78 → 55;
  - 53.44 → 50;
  - …;
  - 41.26 → 40;
  - 36.95 → 35;
  - 35.37 → 35.
- **Consequence for G0.** While TV0h is between 35 and 40 °C, TVh0 is flat at 35.0, so a slope read on TVh0 is exactly 0. G0's slope clause is read on TVh0 (RL-122 item 2). In this window it was met by the rounding and not by the die settling:
  - TV0h fell from 35.501 °C (615 s) to 35.412 °C (625 s), about −0.53 °C/min;
  - at release, 635 s, TV0h was 35.37 °C and still falling;
  - the registered bar is ±0.2 °C/min.
  The 11-12 smoke on Th0C (item 296) released at −0.147 °C/min after 837 s.
- **How this sits with RL-122.** RL-122 says "TV0h and TVh0 are two die-class channels, not two independent thermometers … TVh0 reads lower, by up to 5.5 °C, only while the die cools, so the registered alias rule does not join them". It also says G0 "can release while TV0h is still coming down". That consequence was accepted, so I armed on the checklist. What the ruling does not state is the mechanism found here: a 5 °C staircase, where the earlier reading was a lag. That mechanism may bear on the alias rule, and so on the pick (Tf48 was the runner-up), and on RL-122's return times (TVh0 69.6 s, τ 17.4 s).
- **For the research lead, before slots are entered or W1 is signed.** TV0h is journaled on every sample of every sidecar member. So the desk can print each night gate's release with TV0h's own slope as a labelled alternative beside the registered result.
- Ed was told in the arm notice.

## Checklist (item 306 activation 2)

- [x] Config is one token: `git diff --word-diff=porcelain 99622e96c HEAD` gives exactly `-"Th0C",` / `+"TVh0",`. The hash `24bad206a999441f74d82615df61f45d6dc334abd6516150d1ea6a07272f0bb1` is the one check (b) pins.
- [x] The nine other condition-13 paths hash as item 306's table says, from `$M` at the night sha. No diff against `99622e96c` under `joulewise/align/apple/` or in the two scripts. `verify_r1_executed_sources` returns `a6a09e6d7…`.
- [x] Cold review: `docs/run_reports/2026-11-13-pr752-review.md` (Fable, ADMIT-WITH-FIXES), with the fixes in `5e3c9cccc`. The pick is TVh0, per item 306's ruling under the RL-122 amendment.
- [x] Part A passed at `a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe`: G0 113.18 s; release TV0h 35.365 °C, TVh0 35.000 °C (reference 34.696 / 34.696).
- [x] 60-key check (a) and D-7 passed (below). There is no `r1.prepare_packet_absent_at_arm` flag.
- [x] Dry check `RebindPairDryCheck` passed (item 307).
- [x] `PlanningReleaseTests` passed (item 307). Ruled met by RL-124 item 7.
- [x] The dispositions are in item 306 and are carried unchanged.

## Arm checks

1. Only `com.joulewise.magistrate` is loaded. There is no night plist, no desk fence, no High Power marker and no `$M/.align-r1-high-power`.
   - No powermetrics, km003c or hazard process, no BYTES job, no R12 process.
   - The only claude/codex processes are this session (pid 94242) and its codex MCP adapter.
2. `night.lock` holds `{"pid": 90544, "role": "r1-smoke-close"}`. The pid is dead, `lsof` shows no holder, and the mode is `edr -rw-------`. Left as found.
3. Power and host:
   - AC power, 100%, charged; ioreg `ExternalConnected` Yes, `IsCharging` No, `InstantAmperage` 0.
   - powermode 0, and both pmset sudo rules are present. No external disk. 85 GiB free.
4. **Network time and the frequency word.** Network time was already Off, but the kernel frequency word read `raw_word` 396784 (+6.05 ppm), left from the 11-12 night's restore to ON (item 301). I applied item 251's remedy:
   - `systemsetup -setusingnetworktime off` (already off);
   - root `zero.py`: before freq 396784, after 0;
   - `raw_word` re-read as 0;
   - a 120 s wall-vs-raw rate of **+0.008 ppm** (0.04 ms over 5,764 s).
5. `$M` was clean at `99622e96c`, apart from the 11-12 packet (sha256 `8d63766d…eab9`). It was fetched and detached to the night sha, and HEAD was verified.
   - Ancestors: `99622e96c`, `8c6440d28`, `bb6394f2b` and `683dfe654`.
   - mlx 0.31.2, mlx_lm 0.31.3, transformers 5.12.1.
6. (a) `RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 24bad206a999441f74d82615df61f45d6dc334abd6516150d1ea6a07272f0bb1`
7. (b) `RL-89 RULING OK b2369b6c78d91b75299e10ff7249f1e8cae7304b48cf022e20b2c6a6f69f2884 TV0h TVh0 24bad206a999441f74d82615df61f45d6dc334abd6516150d1ea6a07272f0bb1`. The ruling is `research_lead_ruling` RL-122, `authorizes_night` true.
8. (c) The wrapper is in the commit. `sudo -n -l /bin/kill` returned rc 0, and the argv-shape check returned rc 0.

## D-7 packet

- The old packet `8d63766d…eab9` was deleted. `prepare` (`--sensor-ruling …rl122/sensor_ruling_rl122.json --smoke-table …rl122/smoke_part_b.rl122.json`) returned rc 0 in 19.5 s.
- Weight roots, in seconds: 30B 6.9, 1.5B 0.4, 27B 11.8.
- **PACKET_SHA256 `80d2023cff9cb219e282f20c730ac2de541f156f096c05c06141ecec97e6946e`**. The script printed `PACKET OK`, with `s_slow == "TVh0"`.
- `$M` porcelain shows exactly `?? .align-r1-prepare.json`.

## Plan

- Custody `S=/Users/edr/night-align/r1fu-20261113T144743Z`.
- Plan `align-r1-20261113T1508Z`, plan sha256 `0b00236960e4abbcedf36415cf2a218baec9000783a548616f08e0bec3952873`. `arm.json` sha256 `e2449bacf9a09259168928b3eed1488beb6b03f65f070f79d542b95ef62839b6` (copy beside this file).
- t0 1794582480 = **Fri 13 Nov 07:08:00 PST** (15:08Z). That is now + 20 min, rounded up, and ≤ T0MAX 1794626760 (19:26 PST today). The install cutoff is 07:03:00 PST.
- `window_max_s` 126,480 (RL-72 E2).
  - **Latest end** = t0 + W + 300 = 1794709260 = **Sat 14 Nov 18:21 PST**.
  - **Dead-man** 1794712860 = **Sat 14 Nov 19:21 PST**.
  - Soft "likely redo" mark: T0 + 70,000 s = Sat 14 Nov 02:35 PST.
- Batch-window crossings inside the span: 2, at Fri 13 Nov 11:45 and Sat 14 Nov 11:45 PST. The budget is two; the driver waits each one out.
- `D-7 ARM RECORD OK 80d2023c…946e`. The only `arm.json` flag is `disk.allocation_unsized; shared headroom and live disk floor remain`.
- `PLAN OK align-r1-20261113T1508Z 1794582480 126480`: `receipt_class` HAZARD_PACK; `repo_head` = `measurement_head` = night sha; no `ac_powermode` key.
- Render: preflight ok, and every plist is `ProcessType` Interactive:
  - night `baf4a90c…6133`, calendar 11/13 07:08;
  - dead-man `edf55027…0498`, 19:21;
  - probe `8f4270fe…3c19a3f`.
- **Arm notice** to Ed via Gmail, message `1a1d5618b8f3d6a1`, sent at 06:48 PST, before the install. `notice.ack` is written. Gmail worked in this session, so item 305's #349 issue route was not needed.

## Install

- Before the install, at 06:49 PST:
  - no unread mail from Ed;
  - no `standdown.request`;
  - directives unchanged (standing issues only);
  - the KM003C enumerated on USB (`POWER-Z KM003C`).
- `arm_align_r1.py install`: **rc 0** at 06:49:43 PST (epoch 1794581383). That is before the install cutoff, 07:03:00 PST.
  - `com.joulewise.night` and `com.joulewise.night.deadman` are loaded, together with `com.joulewise.magistrate`.
  - The rendered plist hashes are as above.
- `D-7 packet unchanged since prepare`.
- Next: this commit, then `pmset displaysleepnow`, then exit. No Codex child was started, and the session's codex MCP adapter ends with it.
