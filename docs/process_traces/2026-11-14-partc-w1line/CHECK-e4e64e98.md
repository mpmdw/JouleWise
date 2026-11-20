# Part C at the W1-line commit: magistrate check, activation e4e64e98

Magistrate e4e64e98 (headless, Opus 5.5), 2026-11-14 18:47-18:55 PST. Runs RUN_STATE item 319's "Check" on the run launched by f6c8a352. Reports; decides nothing.

- OUT `/Users/edr/code/jw-wt/partc-w1line/.desk/r1-partc-w1line-20261115T004253Z`; head `f30a97d00`; launcher rc 0 (custody `r1-partc-w1line-out-f6c8a352.txt`).
- Span: receipt `started` 1794703426.55 = 16:43:46 PST, `ended` 1794710560.36 = 18:42:40 PST (7,134 s). Pilot close used for the 20-minute gate: 1794702159 = 16:22:39 PST. 00:00 local did not fall inside the span. Fence gone; watchdog FENCED → LAUNCHING at 18:46:59.
- Blinding: only `runner_receipt.json`, `soak/soak_reference.json` and, through item 319's script verbatim, `part-c/smoke_part_c.json` (evaluation, N_chunk, T_dead) were opened. No energy, power, meter-stream, hazards, member or slot field was printed.

## Receipt (script 1: all asserts passed)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 9442b655233f39902314ef3edf778aa3d1509ae7ed0ae4379b9069cee71545c5
part-C 0 None
RECEIPT OK
```

Soak bands (`soak_reference.json` `sensors_c`): TV0h 34.182 °C, TV1h 34.182 °C (both settled; detrended sd 0.0091 °C, slope −0.0062 °C/min over 1,200 reads).

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 985.494 s.
- Lines:
  - `d_bank_mechanics` pass true:
    - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}` (RL-149 §1.5).
    - `gate_time`: gates + holds 201.67 s, limit 394.20 s, share of T_dead 0.205; pass.
    - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn, as expected).
    - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
  - `d_bank_start_state` pass true: four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.004 to −0.017 s).
  - `step_d` pass true: G0 wait 207.91 s; over reference 0.315 °C (fast = slow); slope −0.187 °C/min.
  - `x_g` pass true: no G1 timeout, x7 false (X_G ran).
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted` (item 315 close §8, carried in bytes): "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98."
  - turn 1 as measured: 11,211 prefill tokens, 4,096 decode tokens, first off-nominal (pm `Moderate`) at token 1,710; last-512 clock ratio 0.935; token rate ratio last-512 0.979; decode OS-level share {0: 0.416, 1: 0.006, 2: 0.578}.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 pm/os not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`.
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,147 rows compared; 3 unequal rows outside gate windows, 0 inside).

## Restore lines (18:47-18:49 PST)

- Runner close steps: `restore` 0 (`pmset -c powermode 0`, observed 0), `stop-volumes` 0, `stop-meter` 0, `stop-agents` 0, `close-volumes` 0.
- No `desk_fence.json`; `com.joulewise.align-r0` labels loaded: 0; plist ProcessType `Interactive`.
- powermode 0; Network Time Off; kernel frequency word 0 (measurement_mode PASS line); no High Power marker; no stray monitor; no root powermetrics.

No restore line failed, so no "restore unproven" stop. The verdict decides nothing here: it goes to the research lead with the lead's desk table (item 319 "After", including the RL-156 §4.2 hand checks against #783's evaluator).
