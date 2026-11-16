# STANDING-F0 run 3 (item 346, launched by item 358): Check

Magistrate 29e66c4b (headless, Opus 5.5), 2026-11-15 23:19-23:20 PST. Launch record: `MAGISTRATE-LAUNCH-c93b67ee.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T051844Z` (not committed). Fence (align-r0 `ce6a0154…`, pid 47873) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no `desk_fence.json`.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-29e66c4b/{check.sh,out.txt}`. The script is `check-c93b67ee/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

F0 standing notice: trigger (c) NO_STAGED after F0 run 2's close (19:16:33 PST); the run completed, verdict `pass`, every line equal to the previous Part C (F0 run 2, item 357).

## Receipt (item 325's script 1, verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 140a83f5b19d2dcc61394aee75321095442cdfcf1c832cb0a167548bbdb9b430
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json` `sensors_c`): TV0h 34.077 °C, TV1h 34.077 °C (previous: 34.072 / 34.072).

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 982.195 s (previous 980.578 s).

| line | this run (b2e01464d, F0 #3) | previous Part C (b2e01464d, F0 #2, item 357) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 203.63 s, limit 392.88 s, share of T_dead 0.207; pass. (Previous: 201.52 s of 392.23 s, 0.206.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.003 to −0.014 s).
- `step_d`: pass; G0 wait 212.11 s; over reference 0.263 °C (fast = slow); slope −0.185 °C/min. (Previous: 215.21 s; 0.277 °C; −0.171.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted`: "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,604 (133.1 s after first token); last-512 clock ratio 0.919; token-rate ratio last-512 0.976; decode OS-level share {0: 0.390, 1: 0.006, 2: 0.604}. (Previous: token 1,713; 0.915; 0.976.) Printed only: the clock ratio is inside the predicted band; the token-rate ratio is 0.004 below its predicted floor, as in F0 runs 1 and 2. No verdict reads either.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,146 rows compared; 2 unequal rows outside gate windows, 0 inside). (Previous: 1,147; 3 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 21:18:44 .. 23:17:51 PST; `log show` rc 0; 47,415 lines saved as `$OUT/maintenance-log.txt`. Per 10 min (process: lines):

```
21:10 dasd 40
21:20 dasd 1679 | mobileassetd 3
21:30 dasd 1741 | mobileassetd 3
21:40 backupd 6 | dasd 1448 | mobileassetd 4
21:50 backupd 24 | dasd 1501 | mobileassetd 1009
22:00 backupd 33 | dasd 1525 | mobileassetd 3
22:10 backupd 6 | dasd 1845 | softwareupdated 8
22:20 dasd 1489
22:30 dasd 1457
22:40 backupd 6 | dasd 1453
22:50 backupd 30 | dasd 1540 | mobileassetd 3
23:00 XProtect 50 | XProtectPluginService 562 | backupd 12 | dasd 1847 | mobileassetd 2041 | softwareupdated 3027
23:10 backupd 6 | dasd 1408 | mobileassetd 11 | softwareupdated 29
```

For the desk: this is the first F0 window that covers a predicted XProtect fast scan (23:08 on the current boot); it shows in the 23:00 bucket beside a `mobileassetd` burst (2,041 lines) and 3,027 `softwareupdated` lines. A second `mobileassetd` burst (1,009) sits at 21:50. The OS build is unchanged (`sw_vers -buildVersion` 25G83 at 23:20). Every Part C line still passed; which turns these overlap is the desk's to read from the journals.

## Timing

- Close used for the close interval: F0 run 2's receipt, 19:16:33 PST (epoch 1794798993); LAST_CLOSE_KIND other, GAP 1,200 s.
- Previous F0 / Part C t0: F0 run 2, 17:17:25 PST (epoch 1794791845).
- This t0: 21:18:47 PST (epoch 1794806327); runner span 21:18:44-23:17:51 PST (receipt mtime epoch 1794813471; 7,147 s); DEADLINE 01:18:47 PST Mon.
- 00:00 did not fall inside the span.

## Restore lines (Check)

All clean: no desk fence; 0 `com.joulewise.align-r0` labels loaded; plist ProcessType Interactive; powermode 0; Network Time Off; `ntp_adjtime` rc 0, frequency word 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; `night.lock` no holder; ExternalConnected Yes, IsCharging No, InstantAmperage 0. No restore-unproven stop.
