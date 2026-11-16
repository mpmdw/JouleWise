# STANDING-F0 run 5 (item 346, launched by item 371): Check

Magistrate d4b2584f (headless, Opus 5.5), 2026-11-16 13:35-13:50 PST. Launch record: `MAGISTRATE-LAUNCH-1292492b.md`.
OUT `/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T193440Z` (not committed). Fence (align-r0 `1a2b8e1a…`, pid 12276) gone before the Check: pid absent, no `com.joulewise.align-r0` label loaded, no `desk_fence.json`. Receipt written 13:33:56 PST.
Check script and full output in custody: `/Users/edr/night-custody/magistrate/standing-f0/check-d4b2584f/{check.sh,out.txt}`. The script is `check-abc54ff5/check.sh` with three substitutions only (TMPDIR, OUT, the r0-launches plist id); `diff` shows nothing else.

F0 standing notice: trigger (c) NO_STAGED after `dev-03-s02`'s close (11:16:18 PST); the run completed, verdict `pass`, every line equal to the previous Part C (F0 run 4, item 368).

## Receipt (item 325's script 1, verbatim output)

```
{"error": null, "fresh_soak": true, "parts": {"C": true}, "parts_requested": "C", "rc": 0}
[('deadline', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('soak_reference', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-part-C-volumes', 0), ('part-C', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
soak 0 a0109814542a7eae972fed7518d172b22b1918104b12fdb4690111464ce09ba2
part-C 0 None
RECEIPT OK
```

Soak bands (`soak/soak_reference.json`): TV0h 34.231 °C, TV1h 34.231 °C (previous: 34.202 / 34.202).

## smoke_part_c.json (script 2: evaluation, N_chunk, T_dead only)

- `verdict` **`pass`**, `pass` true, `slots_entered` false.
- `disposition` as printed: "Mechanics and start state hold. The no-hold TV1h design is adopted (RL-149 section 1.1); run at the commit of RL-149 step 3's PR, this is the Part C of the slot session's checklist (RL-149 section 5, items 11 and 12)."
- N_chunk 4096; T_dead 979.440 s (previous 979.723 s).

| line | this run (b2e01464d, F0 #5) | previous Part C (b2e01464d, F0 #4, item 368) |
|---|---|---|
| `d_bank_mechanics` | pass | pass |
| `d_bank_start_state` | pass | pass |
| `step_d` | pass | pass |
| `x_g` | pass (X_G ran) | pass (X_G ran) |

No line differs (rule 10: nothing goes to the research lead as a differing line).

- `d_bank_mechanics`:
  - `admitted_turns`: judged false, value 2, need 3, status `not_applicable: episode returned at turn 1`, stop `{own_stop: true, why: null}`. (Previous: same.)
  - `gate_time`: gates + holds 203.60 s, limit 391.78 s, share of T_dead 0.208; pass. (Previous: 198.47 s of 391.89 s, 0.203.)
  - `h_records`: pass (turn 0: 103 decode tokens; turn 1: 4,096; H on no turn).
  - `no_g1_timeout`: pass. `no_x7`: pass (x7 false).
- `d_bank_start_state`: pass; four samples (G0 release, G1 release turn 1, first reading after turn 0 and turn 1 start), all os_level 0, Nominal, fresh stamps (ages −0.004 to −0.019 s).
- `step_d`: pass; G0 wait 212.08 s; over reference 0.339 °C (fast = slow); slope −0.180 °C/min. (Previous: 205.92 s; 0.298 °C; −0.185.)
- `x_g`: pass; no G1 timeout, x7 false.
- `log`: "three-turn clause not evaluated: one D run".
- `printed_not_judged`:
  - `predicted`: "D_bank turn 1 (11,211 prefill tokens and a long decode): OS level 2 before token 2,048; last-512 clock ratio between 0.83 and 0.93; token rate ratio at or above 0.98. Printed beside the measurement; no verdict reads it."
  - turn 1 as measured: 11,211 prefill, 4,096 decode; first off-nominal (pm `Moderate`) at token 1,496 (124.1 s after first token); last-512 clock ratio 0.905; token-rate ratio last-512 0.974; decode OS-level share {0: 0.363, 1: 0.006, 2: 0.632}. (Previous: token 1,461; 0.905; 0.976.) Printed only: the clock ratio is inside the predicted band; the token-rate ratio is 0.006 below its predicted floor, as in F0 runs 1-4. No verdict reads either.
  - turn 0: 10,021 prefill, 103 decode, all Nominal.
  - desk verdict: member excluded, reason `thermal.powermetrics_non_nominal` (turn 1 not nominal); flags include `turn_token_budget_reached:1`, `ended_in_unclosed_reasoning`. (Previous: same.)
  - gate states: G1 release turn 1 Nominal, fresh; 5 consecutive readings; fresh-stamp bound 2.0 s.
  - `tv1h_trigger`: fires false (1,151 rows compared; 4 unequal rows outside gate windows, 0 inside). (Previous: 1,146; 4 outside, 0 inside.)

## Maintenance line (print only; gates nothing)

Window 11:34:40 .. 13:33:56 PST; `log show` rc 0; 30,013 lines saved as `$OUT/maintenance-log.txt`. Per 10 min (process: lines):

```
11:30 dasd 796
11:40 backupd 6 | dasd 1458
11:50 dasd 1682 | mobileassetd 122
12:00 backupd 9 | dasd 1674
12:10 backupd 30 | dasd 1910 | mobileassetd 3 | softwareupdated 8
12:20 dasd 1451
12:30 dasd 1522
12:40 backupd 6 | dasd 1353
12:50 backupd 30 | dasd 1966 | mobileassetd 9
13:00 backupd 9 | dasd 1733
13:10 backupd 6 | dasd 1994 | softwareupdated 8
13:20 dasd 1560 | mobileassetd 3
13:30 dasd 552
```

No XProtect lines; no `mobileassetd` burst of the 1,000-line class seen in `dev-03-s02` (max 122 at 11:50); `softwareupdated` 8 lines twice.

## Restore and host after close

Receipt `restore` rc 0 (`pmset -c powermode 0`, observed 0, no marker). After close: no desk fence; 0 align-r0 labels; plist ProcessType Interactive; powermode 0; Network Time Off; `ntp_adjtime` rc 0, frequency word 0, status 0x2081; no High Power marker; no stray monitor; no root powermetrics; night.lock no holder; AC connected, not charging, InstantAmperage 0. Free disk 60 GiB (`df -g`), down from 62 GiB before this run (each F0 OUT is about 2 GiB).

## Next

F0 spacing (rule 5): Mon 16 Nov has two F0 t0s (05:32:36, 11:34:43). A third is allowed at or after 15:34:43 (t0 + 14,400 s), inside rule 6's 02:35-22:40 launch window; rule 7 binds nothing today (`dev-04-s01`, item 367, cannot arm before Tue 00:00:00). This F0 close (13:33:56) leaves no staged item whose gate can hold within 2 h 30 min, so trigger (c) NO_STAGED holds for run 6 under item 346's complete eligibility check. Disk: the dev-04-s01 arm should expect to need an eviction (60 GiB now, about 58 GiB after a sixth F0).
