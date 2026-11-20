# STANDING-F0 run 7 (item 346, launched by item 383): Check

Magistrate cb24533b (headless, Opus 5.5), 2026-11-17 08:33-08:50 PST. Launch record: `MAGISTRATE-LAUNCH-c3cdda76.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261117T142329Z` (not committed). t0 06:23:32 PST (epoch 1794925412); receipt written 08:22:25 PST (span 7,133 s); no 00:00 crossing. Fence (align-r0 `2f152123…`, pid 85027) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no `desk_fence.json`; the watchdog moved FENCED -> LAUNCHING at 08:23:06, 41 s after the receipt.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-cb24533b/{check.sh,out.txt}`. The script is `check-31de5558/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

Activation 6f72b71a (spawned 08:23:06, exited 08:23:47) believed it was inside run 7's span (it read the fence deadline 10:23:32, not the receipt) and exited with no action (custody `note-6f72b71a-spawn-in-span.txt`). The receipt was already written at 08:22:25, 41 s earlier, so no agent was alive during the run and run 7 carries no agent-pause flag from it.

F0 standing notice: trigger (c) NO_STAGED after `dev-04-s02`'s close (05:51:03); the run completed, verdict `pass`, every judged line equal to the previous Part C (F0 run 6, item 378).

## Receipt (verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 7349ee6568e2d00c3225565b06aa25b874e00261e74087d3e9a9ffc16b0d58f1
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json`, window 1,200 s): TV0h 34.224 °C, TV1h 34.224 °C (previous: 34.127 / 34.127). `r0_sha256` in the soak reference: `e6231a8f…769b` (same value as run 6).

## smoke_part_c.json (evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false. `disposition` text unchanged from item 378.
- N_chunk 4096; T_dead 976.995 s (previous 983.332 s).

| line | this run (b2e01464d, F0 #7) | previous Part C (b2e01464d, F0 #6, item 378) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 200.35 s, limit 390.80 s, share of T_dead 0.205; pass. (Previous: 196.48 s of 393.33 s, 0.200.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples, all os_level 0, Nominal, fresh stamps (ages −0.004 to −0.016 s).
- `step_d`: pass; G0 wait 195.48 s; over reference 0.369 °C (fast = slow); slope −0.178 °C/min. (Previous: 199.79 s; 0.356 °C; −0.183.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted` text unchanged ("OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98").
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,122 (92.9 s after first token); last-512 clock ratio **0.811**; token-rate ratio last-512 0.969; decode OS-level share {0: 0.271, 1: 0.058, 2: 0.671}. (Previous: token 1,723 at 143.0 s; 0.909; 0.977; {0: 0.419, 1: 0.006, 2: 0.575}.)
  - Printed only, no verdict reads it: **the last-512 clock ratio 0.811 is below the predicted 0.83-0.93 band**, the first F0 run below it (runs 1-6 printed 0.905 to 0.933 in their Checks; run 6 0.909, run 5 0.905). Per-256-token blocks of turn 1: 1.000 through token 1,792, then 0.989, 0.953, 0.912, 0.887, 0.855, 0.846, 0.823, 0.811, 0.812 (last block 3,840-4,096). Throttling began 601 tokens earlier than run 6 and went deeper; the token-rate ratio is 0.011 below its 0.98 floor (runs 1-6: about 0.003 below). Soak reference was 0.097 °C warmer than run 6. Two readings of one run do not say whether this is the hour (06:23 start, the first F0 morning start after a campaign close) or noise; it is recorded for the research lead's reading of the F0 series, not routed as a differing line.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags as item 378.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,144 rows compared; 3 unequal rows outside gate windows, 0 inside). (Previous: 1,142; 2 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 06:23:29 .. 08:22:25 PST; `log show` rc 0; 33,923 lines saved as `$OUT/maintenance-log.txt`. Non-`dasd` lines per 10 min (process: lines); `dasd` 1,403-3,230 per 10 min (max 3,230 at 08:00; 416 in the partial 08:20 bucket):

```
06:20 mobileassetd 3
06:40 backupd 6
06:50 backupd 27 | mobileassetd 6
07:00 backupd 12
07:10 backupd 6 | softwareupdated 8
07:40 backupd 6
07:50 backupd 30 | mobileassetd 193
08:00 backupd 12 | mobileassetd 218
08:10 backupd 6 | mobileassetd 175 | softwareupdated 8
```

No XProtect lines; no `mobileassetd` burst of the 1,000-line class (max 218 at 08:00, as run 6's 221); `softwareupdated` 8 lines twice.

## Restore and host after close

Receipt `restore` rc 0. After close: no desk fence; 0 align-r0 labels; plist ProcessType Interactive; powermode 0; Network Time Off; `ntp_adjtime` rc 0, frequency word 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; night.lock no holder; AC connected, not charging, InstantAmperage 0. Free disk 275 GiB (`df -g`).

## Next

One F0 t0 on Tue 17 Nov so far (06:23:32). Rule 5: the next F0 t0 is allowed from 10:23:32 (t0 + 14,400 s), at most two more today. No campaign item is staged (item 384: dev-05 is not issued; the dev-04 desks come first and are lead work handed to the MBP between spans), so F0 run 8 runs under trigger (c) NO_STAGED after this close, unless the lead stages an item first.
