# Second Part C at c3f4bacd8 (RUN_STATE item 325): Check

Magistrate de565739 (headless, Opus 5.5), 2026-11-14 23:28-23:35 PST. Launch record: `MAGISTRATE-LAUNCH-b418e121.md`.
OUT `/Users/edr/code/jw-wt/partc-c3f4/.desk/r1-partc2-c3f4-20261115T052325Z` (not committed). Fence (pid 33365) gone before the Check.

## Receipt (script 1, verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 a3a64d7242851b5cdd2e294122ed34648c3e1d0a3305c932a8106ba959b2289f
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json` `sensors_c`): TV0h 34.189 °C, TV1h 34.189 °C.

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 981.044 s.

Lines, with the first Part C's result (item 322) beside each:

| line | this run (c3f4bacd8) | first Part C (f30a97d00, item 322) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs.

- `d_bank_mechanics` details:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}` (RL-149 §1.5). (First run: same.)
  - `gate_time`: gates + holds 202.71 s, limit 392.42 s, share of T_dead 0.207; pass. (First run: 201.67 s of 394.20 s, 0.205.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.004 to −0.016 s).
- `step_d`: G0 wait 199.96 s; over reference 0.352 °C (fast = slow); slope −0.184 °C/min. (First run: 207.91 s; 0.315 °C; −0.187.)
- `x_g`: no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted`: "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,761 (146.0 s after first token); last-512 clock ratio 0.930; token-rate ratio last-512 0.976; decode OS-level share {0: 0.428, 1: 0.006, 2: 0.566}. (First run: token 1,710; 0.935; 0.979.)
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,149 rows compared; 1 unequal row outside gate windows, 0 inside).

## Timing

- Close used for the 20-minute gate: dev-01-s03 `runner_receipt.json` mtime 21:01:48 PST.
- First Part C t0: 16:43:28 PST (epoch 1794703408).
- This t0 (launch): 21:23:25 PST (epoch 1794720205); runner span 21:23:41-23:22:33 PST (7,132 s). Deadline cap 01:30:00.
- 00:00 did not fall inside the span.

## Restore lines (23:28-23:30 PST)

- Runner close steps: `restore` 0, `stop-volumes` 0, `stop-meter` 0, `stop-agents` 0, `close-volumes` 0; every feed proven stopped and hash-checked.
- No `desk_fence.json`; `com.joulewise.align-r0` labels loaded: 0; plist ProcessType `Interactive`.
- powermode 0; Network Time Off; kernel frequency word (`ntp_adjtime`, modes 0) offset 0, freq 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics.

No restore line failed: no "restore unproven" stop; Sunday's 02:40 span is not held by this run.

## Disposition

A diagnostic: nothing adopted, no slots, nothing from OUT committed. The verdict decides nothing here: it goes to the research lead with the lead's desk table (item 325 "After"). This run's pass is the one RL-149 §5 item 12 reads (RL-156 §4.1, RL-164 §1); the two runs agree on every line. Quiet from here (RL-155a §1.2): nothing further runs tonight under item 325.
