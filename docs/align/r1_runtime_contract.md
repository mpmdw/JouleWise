# ALIGN v4 R1 runtime contract (WP15 seam)

The R1 driver (`scripts/align_r1_rehearsal.py`) does no model, SMC or gate work itself. For each segment it runs the WP15 runtime argv once:

    <runtime...> --r1-kind KIND --output DIR [--duration-s N] [--soak-reference FILE]

It then reads one JSON object from stdout. A non-zero exit, a result that is not JSON, or a missing field refuses R1 (exit 3). The Automatic power mode is still restored.

The runtime argv is the list `inputs.WP15.runtime_entrypoint` in `configs/campaigns/align_v4/registration/inputs.json` (Fable cold pass LOW-3):

    ["scripts/align_r1_runtime.py", "--config", "configs/align/v4/r1_runtime.json"]

Element 0 is a repo-relative Python script; the chain passes `--runtime-entrypoint <inputs.json>` and the driver runs it with its own interpreter (`$PY -B`, the pinned venv), followed by the remaining elements verbatim. `ALIGN_R1_RUNTIME`, if set, overrides the list with one operator-pinned executable path (never shell text); this is the only place the override is defined.

The field table lives in `joulewise/align/apple/r1_runtime_contract.py` (`KIND_FIELDS`, `QUIET_FIELDS`, `NEEDS_SOAK_REFERENCE`). The driver checks every result against it at the seam. This document is the prose form of that table, and a test keeps the two in step.

## Arguments

- `--output DIR` is always the canonical segment directory, `<R1 output>/<segment name>`. When the driver rejects an attempt (ruling 8 load, or soak slope), it renames that directory to `<segment name>.rejectedN` (N = 1, 2) before the next attempt starts. The accepted attempt therefore always ran in, and owns, the canonical directory. The runtime must write only inside `DIR` and use paths relative to it.
- `--soak-reference FILE` is passed to every invocation after the accepted idle soak. The file is `<R1 output>/soak_reference.json`, schema `joulewise.align.r1_soak_reference.v1`, and holds:
  - `sensors_c`: per sensor key, the mean over the last 1,200 s of the accepted soak. This is the reference R.
  - `detrended`: the slope, SD and mean per key.
  - the source attempt.

  Every release, the post-D cooldown, the designed planning-turn start states and the A-B-A legs measure against this R. The kinds marked "R" below refuse without it.
- `--duration-s N` is given for fixed-length idle segments only.
- The kinds that run D under the R1 slots (`x-g`, the gated D runs) read the accepted step-d result, `<R1 output>/step_D_prefill_10k_decode_4096/runtime_result.json`, for T_dead, B_D, N_chunk and G_turn. They refuse without it. Reading a sibling is the runtime's only access outside `DIR`.

## Signals and custody (Fable cold pass MEDIUM-1)

- On its first TERM/INT/HUP the driver sends TERM to the running runtime, waits at most 20 s (inside run_night's 30 s), and only then sends KILL. Later signals are ignored so the wait and the Automatic restore complete.
- On TERM the runtime must stop work and, within 20 s: let an open controller bundle salvage and finalize (that stops powermetrics and closes the bundle's SMC sidecar), close its own SMC sessions, heater and journals, write its terminal record and exit 128 + signal. The WP15 runtime forces its own exit after 15 s.
- The terminal record is `DIR/runtime_custody.json` (`status`: `complete`, `refused`, `failed` or `aborted`, the signal, and the SHA-256 of every other file in `DIR`). It is written last on every exit path. After an abort `DIR` is incomplete: it holds the salvaged bundle and journals, and the custody record says so. Nothing is printed on stdout unless the segment completed.
- The runtime refuses (exit 2) when `DIR` already exists, an input is PENDING (R0 sensor keys, the kit's R0 reasoning effort, WP18's X-G turn count, the D-4bit source) or `--soak-reference` is missing or unreadable; it exits 3 when the segment ran but cannot supply its fields.

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
| `cpu_busy_t_s` | list of finite numbers, same length | The time of each `cpu_busy_cores` sample in seconds on the segment's own clock (nondecreasing). |
| `census` | non-empty list | Process census: the full process table at least at segment start and end. |

The journal must cover the segment (executing review MEDIUM-1). With W the wall seconds the driver measured around the invocation, R1 refuses unless there are at least 0.9·W − 5 samples and no two consecutive sample times are more than 5 s apart. Without that, one sample could stand for an 1,800 s soak and the 60 s-sustained rule would be vacuous.

`LoadJournal` in the contract module is the reference implementation of these fields. It uses `ps -A -o pid=,ppid=,pcpu=,comm=` and excludes the runtime's PID tree. A redo of a heavy segment starts only after a `g0-release-soak` release, never straight after the contaminated attempt.

## Fields per kind

| kind | R | fields |
|---|---|---|
| `calibration-pre` | | none beyond a JSON object |
| `calibration-post` | | none |
| `idle` | | none (cooldown after the 30B; not quiet) |
| `idle_soak` | | quiet fields, plus `sensor_series_c`: `{sensor key: [per-second °C, ≥ 1,200 values]}`. Contract key for the `idle` kind of the `idle_soak` segment; the soak is redone unless `abs(slope) <= 0.2` °C/min over the last 20 min. |
| `step-30b` | | quiet fields; `battery_drain_pct_per_h` (ruling 4(b)) |
| `step-d` | | quiet fields; `slots` (S1-S9, B_D, I_D, T_dead, N_chunk, t_decline: finite numbers; `class`: `heavy` or `light`); `e_D_j_per_token` (> 0); `battery_drain_pct_per_h` |
| `idle-until-soak` | R | `recovery_curve`: non-empty list of `[t_s, S_slow °C]`. Idle until S_slow is within δ of R, or 1,500 s (ruling 1(c)). |
| `x-g` | | none |
| `d-spam-benign-s1-a`, `d-spam-benign-s1-b`, `d-bank-benign-s1` | | `energy_j`; `admitted_turns` (int ≥ 0); `x7` (bool); `deadman.T_dead_s` (the deadman the run armed at G0 entry; it must equal the `step-d` `slots.T_dead`, or R1 refuses at that run); `deadman.phases_s.{G0,G1,H,decode,prefill,tool,tail}` (finite seconds) (ruling 1(a), 1(d)); `battery_drain_pct_per_h` |
| `d-planning-turn-r-plus-0c`, `d-planning-turn-r-plus-2c`, `d-planning-turn-r-plus-4c` | R | quiet fields; `reference_c` (R, identical across the three); `g0_release_c` (the S_slow **measured** at release); `delta_slow_c` (the gate band, identical across the three, > 0); `energy_j`. The driver refuses a release outside R + offset ± δ_slow and fits β_T on the measured release temperatures (ruling 6). |
| `d-4bit` | | none (optional) |
| `g0-release-soak` | R | `released`: true if S_slow came within δ of R before the G0 cap (600 s), false on timeout |
| `high-power-aba-a1`, `high-power-aba-b`, `high-power-aba-a2` | R | quiet fields; `t_decline_s`: positive seconds, or null for no decline (infinite) |
| `harvest` | | `charge_resume_soc_pct`: the SoC (%) at the first observed charge resume during R1, or null if charging never resumed (ruling 4(b)) |

`battery_drain_pct_per_h` is the OLS drain rate in %/h (positive = discharging) over the segment's non-charging `pmset -g batt` samples, or null when the segment charged throughout. The driver records both ruling 4(b) outputs in `r1_slots.battery`: the drain under D (mean of step-d and the three gated runs) and under the 30B (step-30b), and the charge-resume SoC.

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
- **Duty bar and L1 (ruling 1(d), lead ruling L1; executing review MEDIUM-2).** On the R1 record the driver computes L1 T_dead = min((1750 − I_D)/1.13544, (1800 − I_D − max_tail − 10)/1.13544) from the step-d `I_D` and the largest gated-run tail, prints it (`R1 L1: {...}` on stdout) and stores it as `l1` in r1_slots with the member fit I_D + 1.13544·T_dead + tail + 10 for the armed and the effective T_dead. The 40 % G0 + G1 + H share is judged against min(armed T_dead, L1), the value W1 will arm.
- **Ruling 20 (external volumes).** The driver takes a volume census (`/sbin/mount` plus `diskutil info -plist`, through `joulewise/align/apple/external_volume.py` pinned to status `off`) at t0, before every runtime invocation and before it writes r1_slots, and refuses R1 if any external volume is mounted. It records every census in `r1_result.json` and r1_slots (`external_volumes`) and takes a last, recorded-only census in the terminal record.
- **Ruling 7.** Each ALIGN episode bundle records `hardware.ac_powermode = {value, source, observed_at: "episode_start"}`.
  - The value is read through `EpisodeRuntimeAdapter.powermode_reader`. `ThermalRegistry(powermode_reader=...)` binds it, and a real run defaults to a read-only `pmset -g custom`.
  - The v4 desk compares every member's recorded value with the frozen series value, using `validate_powermode_members`. Any mismatch, or an unobserved value, sets the `ac_powermode_members` check false, so `instrument_ok` is false.

## Host-level power-mode admission (executing review HIGH-3)

`run_night` refuses every plan class (`night_refused_ac_powermode`) unless the AC-profile `powermode` read from `pmset -g custom` equals the plan's optional `ac_powermode` (0 or 2; absent means 0). If `$MEASUREMENT_ROOT/.align-r1-high-power` exists, it first runs the narrow `sudo -n /usr/bin/pmset -c powermode 0`, removes the marker only after that succeeds, and reads the mode again. A failed read is retried once. The v4 session `install` (W1/D arm) applies the same admission against the kit's frozen series value and writes `staging/v4-arm-NNN.json` with the observed value, the exact pmset text and the ruling 20 volume census, admitted or not.

## Re-runs

A re-run into an existing `<NIGHT_DIR>/align-r1` refuses (exit 3) without a traceback and never overwrites an earlier `r1_result.json`; if the directory holds none (a SIGKILLed run), the refusal is written there.

## The WP15 runtime (`joulewise/align/apple/r1_runtime.py`)

The runtime adds orchestration only; every measurement uses an existing production path:

- **Model segments** (`step-30b`, `step-d`, the planning turns, the A-B-A legs, `x-g`, the gated D runs, `d-4bit`) run `run_benchmark` with a `ThermalRegistry`: the ALIGN episode adapter, `MlxEndpoint` on mlx_lm, `ThermalSession` (SMC sidecar, G0/G1/H, the powermetrics status tap), the episode deadman, the powermetrics telemetry adapter, the bundle custody writer and the ruling 7 powermode record. Members are built from the generated kit configs named in `configs/align/v4/r1_runtime.json`, tagged `align-v4-r1`/`non-claim` without launch lineage. Bundles land in `DIR/runs/`.
- **Step tests** (10k fed prefill + 4,096 seeded decode) are one-turn episodes of a deterministic long-prefill task (`StepTask`), gated by a G0 against the soak R with no G1 or holds so the decode is continuous.
- **Sensor segments** (`idle`, `idle-until-soak`, `g0-release-soak`) run a `ThermalSession` alone in `DIR/<label>/align_thermal.jsonl`; `g0-release-soak` starts powermetrics for the PM state, pre-rolls 65 s for the slope window and calls the production `wait('G0')` with R as its reference.
- **Read-back** uses `read_episode_bundle`, `thermal_desk.read_bundle_record` (`energy_j` is its `turn_owned_j`), `thermal_desk.native_pm_samples` (the PM clock) and `attribute_episode` (decode energy).
- **Journals**: `contract.LoadJournal` once a second (the runtime's own PID tree excluded) and `pmset -g batt` every 30 s (`DIR/battery.jsonl`).

Field derivations and their stated approximations:

- `sensor_series_c`: the valid 1 Hz reads of the R0 gate keys in order; a failed read is dropped, never interpolated.
- `recovery_curve`: `[t_s, S_slow]` per read until |S_slow − R| ≤ δ_slow, or the cap.
- `deadman.phases_s`: G0/G1/H from the episode's `ThermalSession.record()` intervals; prefill (turn start to first token), decode (first token to turn end, holds removed) and tool time from the episode; tail = episode end past the G0-entry deadline.
- `slots` (step-d): S1/S2 = fast-key ΔT and t63; S3/S4 = slow-key ΔT and cooling τ (key names and the FD 2.6 class checks are in `slot_detail`); S5 = δ_slow = max(1.0 °C, 3 × soak SD); S6 = the δ_slow the R1 gates use (the S6 tuning is the lead's after the gated runs); S7 = G_turn = min(300 s, 3 × the recovery from the step peak to within δ of R, observed for up to 300 s after the step); S8 = N_chunk; S9 = t_decline (FD 2.6; when no decline occurs it is censored at the observed decode length and N_chunk = 2,048, A1 A3.1; no PM clock support refuses); I_D = member wall − (episode end − G0 entry); B_D = 1024 × ⌊((1800 − I_D)/1.13544 − prefill_s) × r_decode / 1024⌋, ≤ 40,960; T_dead = (1750 − I_D)/1.13544 (L1's first term; the kit applies the tail); class = D's protocol class (A1 A3.1), with the FD 2.5 rule recorded beside it.
- `e_D_j_per_token`: decode-segment energy over decode tokens of the step-d episode.
- Designed start states (planning kinds): a proportional MLX heater (`ProcessHeater`, a child process) preheats to R + offset and holds S_slow there during the production G0, whose reference is R + offset on S_slow (S_fast is not banded); it stops before the episode starts. `g0_release_c` is the G0 interval's measured release.
- `released`: the G0 outcome. `t_decline_s`: the step's t_decline, null when no decline occurred.
- `calibration-pre`/`-post` record the read-only host snapshot at the brackets; the meter calibration itself belongs to the R1 night plan's scaffold. `harvest` writes `DIR/harvest_manifest.json` (SHA-256 of every file under the R1 output) and aggregates the charge-resume events.
