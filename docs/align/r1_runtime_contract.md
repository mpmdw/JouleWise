# ALIGN v4 R1 runtime contract (WP15 seam)

The R1 driver (`scripts/align_r1_rehearsal.py`) does no model, SMC or gate work itself. For each segment it runs the WP15 runtime argv once:

    <runtime...> --r1-kind KIND --output DIR [--duration-s N] [--soak-reference FILE]

It then reads one JSON object from stdout. A non-zero exit, a result that is not JSON, or a missing field refuses R1 (exit 3). The Automatic power mode is still restored.

The field table lives in `joulewise/align/apple/r1_runtime_contract.py` (`KIND_FIELDS`, `QUIET_FIELDS`, `NEEDS_SOAK_REFERENCE`). The driver checks every result against it at the seam. This document is the prose form of that table, and a test keeps the two in step.

## Arguments

- `--output DIR` is always the canonical segment directory, `<R1 output>/<segment name>`. When the driver rejects an attempt (ruling 8 load, or soak slope), it renames that directory to `<segment name>.rejectedN` (N = 1, 2) before the next attempt starts. The accepted attempt therefore always ran in, and owns, the canonical directory. The runtime must write only inside `DIR` and use paths relative to it.
- `--soak-reference FILE` is passed to every invocation after the accepted idle soak. The file is `<R1 output>/soak_reference.json`, schema `joulewise.align.r1_soak_reference.v1`, and holds:
  - `sensors_c`: per sensor key, the mean over the last 1,200 s of the accepted soak. This is the reference R.
  - `detrended`: the slope, SD and mean per key.
  - the source attempt.

  Every release, the post-D cooldown, the designed planning-turn start states and the A-B-A legs measure against this R. The kinds marked "R" below refuse without it.
- `--duration-s N` is given for fixed-length idle segments only.

## Fields every quiet segment returns (council ruling 8)

The quiet segments are:
- the idle soak;
- the 30B and D step tests;
- the three planning-turn states;
- the three A-B-A legs.

Each returns:

| field | type | meaning |
|---|---|---|
| `cpu_busy_cores` | list of finite numbers, 1 per second | Background CPU load in cores: summed %CPU / 100 of every process outside the measured runtime's own process tree. The driver redoes the segment when the load is > 0.5 core for 60 consecutive seconds. |
| `census` | non-empty list | Process census: the full process table at least at segment start and end. |

`LoadJournal` in the contract module is the reference implementation of both fields. It uses `ps -A -o pid=,ppid=,pcpu=,comm=` and excludes the runtime's PID tree. A redo of a heavy segment starts only after a `g0-release-soak` release, never straight after the contaminated attempt.

## Fields per kind

| kind | R | fields |
|---|---|---|
| `calibration-pre` | | none beyond a JSON object |
| `calibration-post` | | none |
| `idle` | | none (cooldown after the 30B; not quiet) |
| `idle_soak` | | quiet fields, plus `sensor_series_c`: `{sensor key: [per-second °C, ≥ 1,200 values]}`. Contract key for the `idle` kind of the `idle_soak` segment; the soak is redone unless `abs(slope) <= 0.2` °C/min over the last 20 min. |
| `step-30b` | | quiet fields |
| `step-d` | | quiet fields; `slots` (S1-S9, B_D, I_D, T_dead, N_chunk, t_decline: finite numbers; `class`: `heavy` or `light`); `e_D_j_per_token` (> 0) |
| `idle-until-soak` | R | `recovery_curve`: non-empty list of `[t_s, S_slow °C]`. Idle until S_slow is within δ of R, or 1,500 s (ruling 1(c)). |
| `x-g` | | none |
| `d-spam-benign-s1-a`, `d-spam-benign-s1-b`, `d-bank-benign-s1` | | `energy_j`; `admitted_turns` (int ≥ 0); `x7` (bool); `deadman.T_dead_s` (the deadman the run armed at G0 entry; it must equal the `step-d` `slots.T_dead`, or R1 refuses at that run); `deadman.phases_s.{G0,G1,H,decode,prefill,tool,tail}` (finite seconds) (ruling 1(a), 1(d)) |
| `d-planning-turn-r-plus-0c`, `d-planning-turn-r-plus-2c`, `d-planning-turn-r-plus-4c` | R | quiet fields; `reference_c` (R, identical across the three); `g0_release_c` (the S_slow **measured** at release); `delta_slow_c` (the gate band, identical across the three, > 0); `energy_j`. The driver refuses a release outside R + offset ± δ_slow and fits β_T on the measured release temperatures (ruling 6). |
| `d-4bit` | | none (optional) |
| `g0-release-soak` | R | `released`: true if S_slow came within δ of R before the G0 cap (600 s), false on timeout |
| `high-power-aba-a1`, `high-power-aba-b`, `high-power-aba-a2` | R | quiet fields; `t_decline_s`: positive seconds, or null for no decline (infinite) |
| `harvest` | | none (authenticated harvest; recorded verbatim) |

## How the driver uses the fields

- **U5 (ruling 6 with lead ruling L2, c = 1.0).** Inputs:
  - σ_pair = max(|E_a − E_b|, 2.97 J), where E_a and E_b are the `energy_j` of the two spam/benign replay runs;
  - δ_slow is the planning-turn `delta_slow_c`.

  The verdict:
  - PASS if |β_T|₉₀·δ_slow ≤ σ_pair;
  - FAIL if |β_T|·δ_slow > σ_pair;
  - INCONCLUSIVE otherwise.
- **A-B-A (ruling 16).** The sequence for each leg:
  1. The driver sets the mode with the narrow sudo rule and reads it back.
  2. It waits outside 11:45-13:15 local (ruling 8).
  3. It runs `g0-release-soak`, then the leg.

  A leg is redone, after another release, on sustained load. If any accepted leg's release timed out (`released: false`), adoption is INCONCLUSIVE and the series stays Automatic.
- **Ruling 7.** Each ALIGN episode bundle records `hardware.ac_powermode = {value, source, observed_at: "episode_start"}`.
  - The value is read through `EpisodeRuntimeAdapter.powermode_reader`. `ThermalRegistry(powermode_reader=...)` binds it, and a real run defaults to a read-only `pmset -g custom`.
  - The v4 desk compares every member's recorded value with the frozen series value, using `validate_powermode_members`. Any mismatch, or an unobserved value, sets the `ac_powermode_members` check false, so `instrument_ok` is false.

## Not yet implemented in the runtime

`LoadJournal` and the bundle powermode record are implemented. Every other field above needs the WP15 R1 runtime executable, which does not yet exist. That runtime must drive the episode adapter, the SMC sidecar and `ThermalSession`, which this contract does not touch:
- `sensor_series_c` and `recovery_curve`: SMC sidecar rows;
- `deadman.phases_s`: the G0, G1 and H intervals from `ThermalSession.record()`, plus decode, prefill and tool time from the episode, plus the post-deadline tail;
- `released`: the G0 wait outcome;
- `t_decline_s`;
- `energy_j`: the episode attribution;
- `e_D_j_per_token`: the step-D decode energy divided by decode tokens.

The R1 chain refuses (exit 3) until every field is present.
