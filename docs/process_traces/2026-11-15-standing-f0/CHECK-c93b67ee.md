# STANDING-F0 run 2 (item 346, launched by item 356): Check

Magistrate c93b67ee (headless, Opus 5.5), 2026-11-15 19:19-19:20 PST. Launch record: `MAGISTRATE-LAUNCH-428abccd.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T011723Z` (not committed). Fence (align-r0 `c472d6d6…`, pid 37008) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no `desk_fence.json`.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-c93b67ee/{check.sh,out.txt}`. The script is `check-7b6d03e9/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

F0 standing notice: trigger (c) NO_STAGED after F0 run 1's close (15:15:11 PST); the run completed, verdict `pass`, every line equal to the previous Part C (F0 run 1, item 352).

## Receipt (item 325's script 1, verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 39de408de9c93e0ffc0014dfa16ac35292a11d69150bcbf756cf029e70e1ccd0
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json` `sensors_c`): TV0h 34.072 °C, TV1h 34.072 °C (previous: 34.160 / 34.160).

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 980.578 s (previous 975.292 s).

| line | this run (b2e01464d, F0 #2) | previous Part C (b2e01464d, F0 #1, item 352) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 201.52 s, limit 392.23 s, share of T_dead 0.206; pass. (Previous: 200.50 s of 390.12 s, 0.206.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.004 to −0.018 s).
- `step_d`: pass; G0 wait 215.21 s; over reference 0.277 °C (fast = slow); slope −0.171 °C/min. (Previous: 208.10 s; 0.288 °C; −0.182.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted`: "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,713 (142.1 s after first token); last-512 clock ratio 0.915; token-rate ratio last-512 0.976; decode OS-level share {0: 0.416, 1: 0.006, 2: 0.578}. (Previous: token 1,689; 0.933; 0.978.) Printed only: the clock ratio is inside the predicted band this time (the two earlier runs sat 0.003 and 0.000 above it); the token-rate ratio is 0.004 below its predicted floor, as in both earlier runs. No verdict reads either.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,147 rows compared; 3 unequal rows outside gate windows, 0 inside). (Previous: 1,145; 3 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 17:17:23 .. 19:16:33 PST; `log show` rc 0; 29,776 lines saved as `$OUT/maintenance-log.txt`. Per 10 min (process: lines):

```
17:10 dasd 541
17:20 dasd 1310 | mds 25
17:30 dasd 1588 | mobileassetd 72
17:40 backupd 6 | dasd 1660
17:50 backupd 27 | dasd 1579
18:00 backupd 9 | dasd 1525
18:10 backupd 6 | dasd 1895 | mobileassetd 3 | softwareupdated 8
18:20 dasd 1575
18:30 dasd 1569 | mobileassetd 3
18:40 backupd 6 | dasd 1657 | mobileassetd 3
18:50 backupd 27 | dasd 1626
19:00 backupd 9 | dasd 1489
19:10 backupd 6 | dasd 1377 | softwareupdated 8
```

For the desk: no `mobileassetd` burst this time (run 1 had 5,168 lines in its first bucket); no XProtect lines in the window.

## Timing

- Close used for the close interval: F0 run 1's receipt, 15:15:11 PST (epoch 1794784512); LAST_CLOSE_KIND other, GAP 1,200 s.
- Previous F0 / Part C t0: F0 run 1, 13:16:14 PST (epoch 1794777374).
- This t0: 17:17:25 PST (epoch 1794791845); runner span 17:17:23-19:16:33 PST (receipt mtime epoch 1794798993; 7,148 s); DEADLINE 21:17:25 PST.
- 00:00 did not fall inside the span.

## Restore lines (19:19:38-19:19:40 PST)

- Runner close steps: `restore` 0, `stop-volumes` 0, `stop-meter` 0, `stop-agents` 0, `close-volumes` 0; every feed proven stopped and hash-checked.
- No `desk_fence.json`; `com.joulewise.align-r0` labels loaded: 0; plist ProcessType `Interactive`.
- powermode 0; Network Time Off; kernel frequency word (`ntp_adjtime`) freq 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; `night.lock` no holder; battery ExternalConnected Yes, IsCharging No, InstantAmperage 0.

No restore line failed: no "restore unproven" stop.

## Next under item 346

Rule 5: the next F0 t0 is at or after 21:17:25 PST (this t0 + 14,400 s); rule 6: at or before 22:40:00 PST; this would be the third and last F0 t0 on Sun 15 Nov. Rule 7: no staged counted span is due Sun 15 Nov (items 354 and 355 are due Mon 16 Nov from 00:00:00). See RUN_STATE 357 for this activation's decision.

## Disposition

A diagnostic: nothing adopted, no slots, nothing from OUT committed. The verdict decides nothing here; the lead reads it under RL-164 §3. The magistrate reports; it decides nothing.
