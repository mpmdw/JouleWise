# STANDING-F0 run 4 (item 346, launched by item 364): Check

Magistrate abc54ff5 (headless, Opus 5.5), 2026-11-16 07:35-07:45 PST. Launch record: `MAGISTRATE-LAUNCH-d59960c1.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T133233Z` (not committed). Fence (align-r0 `03d7298f…`, pid 84557) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no `desk_fence.json`.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-abc54ff5/{check.sh,out.txt}`. The script is `check-c93b67ee/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

F0 standing notice: trigger (c) NO_STAGED after the dev-03 pilot's close (05:10:07 PST); the run completed, verdict `pass`, every line equal to the previous Part C (F0 run 3, item 359).

## Receipt (item 325's script 1, verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 1346b0bf4ab60e160d57334781017477077763b54d7bef002a252a4efb40424c
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json` `sensors_c`): TV0h 34.202 °C, TV1h 34.202 °C (previous: 34.077 / 34.077).

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 979.723 s (previous 982.195 s).

| line | this run (b2e01464d, F0 #4) | previous Part C (b2e01464d, F0 #3, item 359) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 198.47 s, limit 391.89 s, share of T_dead 0.203; pass. (Previous: 203.63 s of 392.88 s, 0.207.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.003 to −0.019 s).
- `step_d`: pass; G0 wait 205.92 s; over reference 0.298 °C (fast = slow); slope −0.185 °C/min. (Previous: 212.11 s; 0.263 °C; −0.185.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted`: "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,461 (121.0 s after first token); last-512 clock ratio 0.905; token-rate ratio last-512 0.976; decode OS-level share {0: 0.354, 1: 0.015, 2: 0.632}. (Previous: token 1,604; 0.919; 0.976.) Printed only: the clock ratio is inside the predicted band; the token-rate ratio is 0.004 below its predicted floor, as in F0 runs 1-3. No verdict reads either.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,146 rows compared; 4 unequal rows outside gate windows, 0 inside). (Previous: 1,146; 2 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 05:32:33 .. 07:31:37 PST; `log show` rc 0; 28,730 lines saved as `$OUT/maintenance-log.txt`. Per 10 min (process: lines):

```
05:30 dasd 909
05:40 backupd 6 | dasd 1530
05:50 backupd 24 | dasd 1573 | mobileassetd 3
06:00 backupd 9 | dasd 1555
06:10 backupd 6 | dasd 1854 | mobileassetd 3 | softwareupdated 8
06:20 dasd 1351 | mobileassetd 69
06:30 dasd 1438
06:40 backupd 6 | dasd 1639 | mobileassetd 3
06:50 backupd 24 | dasd 1559
07:00 backupd 9 | dasd 1646
07:10 backupd 6 | dasd 1841 | mobileassetd 3 | softwareupdated 8
07:20 dasd 1535 | mobileassetd 3
07:30 dasd 37
```

No `mobileassetd` burst, no XProtect, no `softwareupdated` burst in this window.

## Host lines after the close

`no desk fence`; align-r0 labels loaded 0; plist ProcessType Interactive; powermode 0; Network Time Off; `ntp_adjtime` rc 0, frequency word 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; `night.lock` no holder; battery ExternalConnected Yes, IsCharging No, InstantAmperage 0. Restore lines (receipt steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes`) all rc 0. Free disk 67 GiB at 07:38.

## Timing

- Close used for the close interval: the dev-03 pilot's campaign receipt, 05:10:07 PST (epoch 1794834608 rounded up); LAST_CLOSE_KIND campaign, GAP 300 s.
- Previous F0 / Part C t0: F0 run 3, 21:18:47 PST Sun (epoch 1794806327).
- This t0: 05:32:36 PST (epoch 1794835956); runner span 05:32:45-07:31:37 PST (receipt `ended` epoch 1794843097.11; 7,131 s); DEADLINE 09:32:36 PST.
- 00:00 did not fall inside the span.
