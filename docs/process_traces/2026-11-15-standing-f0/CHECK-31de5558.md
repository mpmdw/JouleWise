# STANDING-F0 run 6 (item 346, launched by item 377): Check

Magistrate 31de5558 (headless, Opus 5.5), 2026-11-16 20:17-20:30 PST. Launch record: `MAGISTRATE-LAUNCH-ade002e9.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261117T021602Z` (not committed). Fence (align-r0 `3c1f7667…`, pid 43459) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no `desk_fence.json`; the watchdog moved FENCED -> LAUNCHING at 20:16:42. Receipt written 20:14:52 PST.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-31de5558/{check.sh,out.txt}`. The script is `check-d4b2584f/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

F0 standing notice: trigger (c) NO_STAGED after F0 run 5's close (13:33:56), released by item 376; the run completed, verdict `pass`, every judged line equal to the previous Part C (F0 run 5, item 373).

## Receipt (verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 f21bfddfe111c225a475ddb9a3d2867f593f335fe89b3b95c3c4c81dd2c40f4e
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json`): TV0h 34.127 °C, TV1h 34.127 °C (previous: 34.231 / 34.231). `r0_sha256` in the soak reference: `e6231a8f…769b` (the restored copy item 377 pointed the RL-89 check at; same value the check expects).

## smoke_part_c.json (evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false. `disposition` text unchanged from item 373.
- N_chunk 4096; T_dead 983.332 s (previous 979.440 s).

| line | this run (b2e01464d, F0 #6) | previous Part C (b2e01464d, F0 #5, item 373) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 196.48 s, limit 393.33 s, share of T_dead 0.200; pass. (Previous: 203.60 s of 391.78 s, 0.208.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples, all os_level 0, Nominal, fresh stamps (ages −0.003 to −0.019 s).
- `step_d`: pass; G0 wait 199.79 s; over reference 0.356 °C (fast = slow); slope −0.183 °C/min. (Previous: 212.08 s; 0.339 °C; −0.180.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted` text unchanged ("OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98").
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,723 (143.0 s after first token); last-512 clock ratio 0.909; token-rate ratio last-512 0.977; decode OS-level share {0: 0.419, 1: 0.006, 2: 0.575}. (Previous: token 1,496; 0.905; 0.974; {0: 0.363, 1: 0.006, 2: 0.632}.) Printed only: the clock ratio is inside the predicted band; the token-rate ratio is 0.003 below its predicted floor, as in F0 runs 1-5. The first off-nominal token moved 227 tokens later than run 5 and is still before 2,048. No verdict reads any of these.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags as item 373.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,142 rows compared; 2 unequal rows outside gate windows, 0 inside). (Previous: 1,151; 4 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 18:16:02 .. 20:14:52 PST; `log show` rc 0; 41,999 lines saved as `$OUT/maintenance-log.txt`. Non-`dasd` lines per 10 min (process: lines); `dasd` 2,252-3,794 per 10 min (max 3,794 at 20:00), higher than run 5's 552-1,994:

```
18:40 backupd 6 | mobileassetd 173
18:50 backupd 30 | mobileassetd 1
19:00 backupd 15 | mobileassetd 69
19:10 backupd 6 | softwareupdated 8
19:40 backupd 6
19:50 backupd 30 | mobileassetd 122
20:00 backupd 15 | mobileassetd 221
20:10 backupd 6 | mobileassetd 1 | softwareupdated 8
```

No XProtect lines; no `mobileassetd` burst of the 1,000-line class (max 221 at 20:00); `softwareupdated` 8 lines twice. Higher `dasd` volume is printed only; no judged line moved.

## Restore and host after close

Receipt `restore` rc 0. After close: no desk fence; 0 align-r0 labels; plist ProcessType Interactive; powermode 0; Network Time Off; `ntp_adjtime` rc 0, frequency word 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; night.lock no holder; AC connected, not charging, InstantAmperage 0. Free disk 241 GiB (`df -g`) after the item 376 offload.

## Next

Mon 16 Nov has its three F0 t0s (05:32:36, 11:34:43, 18:16:05); rule 5 allows at most three F0 t0s in one local calendar day, so no further F0 today. The next F0 t0 is allowed from Tue 00:00:00 (and at least 22:16:05, 14,400 s after this t0), but item 367 comes first. Next: item 367 (`dev-04-s01`) from Tue 00:00:00 under its own gates (close interval 1,200 s after this close, 20:34:52, already passed by then); item 367 expires 24 h after its issue, at Tue 05:38:05 PST. No disk eviction is needed (241 GiB free).
