# STANDING-F0 run 8 (item 346, launched by the cb24533b pre-launch record, commit `d65f60d8b`): Check

Magistrate c6a5728a (headless, Opus 5.5), 2026-11-17 12:28-12:40 PST. Launch record: `MAGISTRATE-LAUNCH-cb24533b.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261117T182510Z` (not committed). t0 10:25:13 PST (epoch 1794939913); receipt written 12:24:12 PST (epoch 1794947052; span 7,139 s); no 00:00 crossing. Fence (align-r0 `cc900ce2…`, pid 3920) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no desk fence. This activation was spawned at 12:28:22, 250 s after the receipt, so no agent was alive during the run; no agent-pause flag.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-c6a5728a/{check.sh,out.txt}`. The script is `check-cb24533b/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

F0 standing notice: trigger (c) NO_STAGED after F0 run 7's close (08:22:25); the run completed, verdict `pass`, every judged line equal to the previous Part C (F0 run 7, `CHECK-cb24533b.md`).

## Receipt (verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 632a8d08269e1dac3b9032edc626d085597e293237956d8b129251d07339e709
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json`, window 1,200 s, settled): TV0h 34.166 °C, TV1h 34.166 °C (previous: 34.224 / 34.224). `r0_sha256` in the soak reference: `e6231a8f…769b` (same as runs 6 and 7).

## smoke_part_c.json (evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false. `disposition` text unchanged.
- N_chunk 4096; T_dead 977.063 s (previous 976.995 s).

| line | this run (b2e01464d, F0 #8) | previous Part C (b2e01464d, F0 #7) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 199.49 s, limit 390.83 s, share of T_dead 0.204; pass. (Previous: 200.35 s of 390.80 s, 0.205.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples, all os_level 0, Nominal, fresh stamps (ages −0.004 to −0.019 s).
- `step_d`: pass; G0 wait 215.24 s; over reference 0.324 °C (fast = slow); slope −0.167 °C/min. (Previous: 195.48 s; 0.369 °C; −0.178.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted` text unchanged ("OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98").
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,579 (130.9 s after first token); last-512 clock ratio **0.912**; token-rate ratio last-512 0.976; decode OS-level share {0: 0.384, 1: 0.006, 2: 0.610}. (Previous, run 7: token 1,122 at 92.9 s; 0.811; 0.969; {0: 0.271, 1: 0.058, 2: 0.671}.)
  - Per-256-token clock-ratio blocks of turn 1: 1.000 through block 8 (to token 2,304), then 0.995, 0.984, 0.966, 0.946, 0.934, 0.918, 0.905 (last block 3,840-4,096). The last-512 ratio is back inside the predicted 0.83-0.93 band (runs 1-6: 0.905 to 0.933; run 7, the 06:23 start: 0.811). So run 7's low reading did not repeat at a 10:25 start; one more morning start would say whether it is the hour. Token-rate ratio 0.004 below its 0.98 floor, as runs 1-6. Printed for the research lead's reading of the F0 series, not routed as a differing line.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); 13 flags (listed in custody `out.txt`).
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,145 rows compared; 3 unequal rows outside gate windows, 0 inside). (Previous: 1,144; 3 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 10:25:10 .. 12:24:12 PST; `log show` rc 0; 45,290 lines saved as `$OUT/maintenance-log.txt`. Non-`dasd` lines per 10 min (process: lines); `dasd` 1,307-1,847 per 10 min (492 and 737 in the partial first and last buckets):

```
10:30 backupd 33 | mobileassetd 3
10:40 backupd 6 | mobileassetd 3
10:50 backupd 30
11:00 XProtect 50 | XProtectPluginService 562 | backupd 15 | mobileassetd 2041 | softwareupdated 2579
11:10 backupd 6 | mobileassetd 10 | softwareupdated 35
11:40 backupd 6
11:50 backupd 30 | mobileassetd 125
12:00 backupd 12 | mobileassetd 68
12:10 backupd 6 | mobileassetd 3 | softwareupdated 8
```

The 11:00 bucket is one burst at 11:08:46-11:09:42: `softwareupdated`'s background scan (`com.apple.SoftwareUpdate.Activity`, ramp Background, then a `MacUpdateBrain` asset query to `mobileassetd`) and an XProtect plugin pass at 11:09:35. It is the same class and the same 12-hour phase as the 23:08 burst in F0 run 2 (`CHECK-29e66c4b.md`: XProtect 50 | XProtectPluginService 562 | mobileassetd 2041 | softwareupdated 3027). It falls inside `capture_predecessor_30b` (11:00:32-11:09:42), before step D (11:09:43-11:44:22), D_bank (11:44:22-12:04:05) and X_G (12:04:30-12:24:10). The OS build is unchanged (`sw_vers` 25G83 at 12:32).

## Restore and host after close

Receipt `restore` rc 0. After close: no desk fence; 0 align-r0 labels; plist ProcessType Interactive; powermode 0; Network Time Off; `ntp_adjtime` rc 0, frequency word 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; AC connected, not charging, InstantAmperage 0. Free disk 273 GiB (`df -g`).

## Next

Two F0 t0s on Tue 17 Nov (06:23:32, 10:25:13). Rule 5: the next F0 t0 is allowed from 14:25:13 (t0 + 14,400 s), the third and last today. `dev-05-s01` and `dev-05-s02` are issued as items 393/394 but cannot arm before Wed 00:00:00, more than 2 h 30 min after this close, so F0 run 9 runs under trigger (c) NO_STAGED; rule 7 is not bound (no counted span is due Tue).
