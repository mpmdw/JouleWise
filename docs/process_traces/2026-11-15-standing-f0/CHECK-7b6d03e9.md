# STANDING-F0 run 1 (item 346, launched by item 351): Check

Magistrate 7b6d03e9 (headless, Opus 5.5), 2026-11-15 15:19-15:22 PST. Launch record: `MAGISTRATE-LAUNCH-a187f945.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261115T211611Z` (not committed). Fence (align-r0 `3e6f684d…`) gone before the Check; watchdog FENCED -> LAUNCHING at 15:18:37.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-7b6d03e9/{check.sh,out.txt}`.

F0 standing notice: trigger (c) NO_STAGED after the `dev-02-s02` close (12:42:45 PST); the run completed, verdict `pass`, every line equal to the previous Part C (item 328).

## Receipt (item 325's script 1, verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 4751d79104e150146df18166d118eb48eaddabe143e0551af02a69429a2f8c78
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json` `sensors_c`): TV0h 34.160 °C, TV1h 34.160 °C (previous: 34.189 / 34.189).

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 975.292 s (previous 981.044 s).

| line | this run (b2e01464d, F0 #1) | previous Part C (c3f4bacd8, item 328) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}` (RL-149 §1.5). (Previous: same.)
  - `gate_time`: gates + holds 200.50 s, limit 390.12 s, share of T_dead 0.206; pass. (Previous: 202.71 s of 392.42 s, 0.207.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.003 to −0.015 s).
- `step_d`: pass; G0 wait 208.10 s; over reference 0.288 °C (fast = slow); slope −0.182 °C/min. (Previous: 199.96 s; 0.352 °C; −0.184.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted`: "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,689 (140.1 s after first token); last-512 clock ratio 0.933; token-rate ratio last-512 0.978; decode OS-level share {0: 0.411, 1: 0.006, 2: 0.584}. (Previous: token 1,761; 0.930; 0.976.) Printed only: the clock ratio sits 0.003 above the predicted band and the token-rate ratio 0.002 below its predicted floor, as in the previous run (0.976); no verdict reads either.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,145 rows compared; 3 unequal rows outside gate windows, 0 inside). (Previous: 1,149; 1 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 13:16:11 .. 15:15:11 PST; `log show` rc 0; 46,783 lines saved as `$OUT/maintenance-log.txt`. Per 10 min (process: lines):

```
13:10 dasd 721
13:20 backupd 1 | dasd 1718 | mobileassetd 5168
13:30 dasd 1605 | mobileassetd 6
13:40 backupd 6 | dasd 1642 | mobileassetd 3
13:50 dasd 1263
14:00 backupd 9 | dasd 3044 | mobileassetd 407
14:10 backupd 6 | dasd 2033 | mobileassetd 303
14:20 dasd 1707 | mobileassetd 182 | softwareupdated 8
14:30 backupd 2 | dasd 1499 | mobileassetd 1
14:40 backupd 6 | dasd 1724 | mobileassetd 405
14:50 backupd 21 | dasd 1661 | mobileassetd 3
15:00 backupd 27 | dasd 1961
15:10 backupd 6 | dasd 1188 | softwareupdated 8
```

For the desk: the 13:20 bucket carries 5,168 `mobileassetd` lines (soak period, right after launch). No XProtect lines in the window.

## Timing

- Close used for the close interval: `dev-02-s02` campaign receipt, mtime 12:42:46 PST (epoch 1794775366); LAST_CLOSE_KIND campaign, GAP 300 s.
- Previous F0 / Part C t0: item 325's run, 21:23:25 PST 11-14 (epoch 1794720205).
- This t0: 13:16:14 PST (epoch 1794777374); runner span 13:16:26-15:15:11 PST (7,125 s); DEADLINE 17:16:14 PST.
- 00:00 did not fall inside the span.

## Restore lines (15:19:31-15:19:34 PST)

- Runner close steps: `restore` 0, `stop-volumes` 0, `stop-meter` 0, `stop-agents` 0, `close-volumes` 0; every feed proven stopped and hash-checked.
- No `desk_fence.json`; `com.joulewise.align-r0` labels loaded: 0; plist ProcessType `Interactive`.
- powermode 0; Network Time Off; kernel frequency word (`ntp_adjtime`) freq 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; `night.lock` no holder; battery ExternalConnected Yes, IsCharging No, InstantAmperage 0.

No restore line failed: no "restore unproven" stop.

## Next under item 346

Rule 5: the next F0 t0 is at or after 17:16:14 PST (this t0 + 14,400 s); rule 6: launch at or before 22:40:00 PST; this is the first of at most three F0 t0s on Sun 15 Nov. A later activation launches it only if a trigger holds then and no staged item outranks it (rule 3). This activation launches nothing (it is before 17:16:14).

## Disposition

A diagnostic: nothing adopted, no slots, nothing from OUT committed. The verdict decides nothing here; the lead reads it under RL-164 §3. The magistrate reports; it decides nothing.
