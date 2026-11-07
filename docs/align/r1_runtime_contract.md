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

  Every release, the post-D cooldown, the gated-run precools, X-G, the gated D runs, the designed planning-turn start states and the A-B-A legs measure against this R. The kinds marked "R" below refuse without it. No R1 model member keeps a self-captured reference: each installs R (or its designed start state) through a session hook before warmup, so the gate policy's `capture` role never fires (LEAD-RULINGS-2 R5-1).
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
| `step-30b` | | quiet fields; `battery_drain_pct_per_h` (ruling 4(b)); `thermometry.status`, `thermometry.classification_sha256` (the full-inventory classification, for the record only) |
| `step-d` | | quiet fields; `slots` (S1-S9, B_D, I_D, T_dead, N_chunk, t_decline: finite numbers; `class`: `heavy` or `light`); `e_D_j_per_token` (> 0); `battery_drain_pct_per_h`; `thermometry.status` (`pass` only with both a die and a heatsink pick), `thermometry.classification_sha256` (protocol v4 :243-251, LEAD-RULINGS-2 R5-5) |
| `idle-until-soak` | R | `recovery_curve`: non-empty list of `[t_s, S_slow °C]`; `released` (bool). Idle until S_slow is in the G0 band of R (S_slow ≤ R + δ_slow, one-sided: a host already cooler than the soak has cooled), or the cap: 1,500 s (ruling 1(c)). The driver uses it as the post-D cooldown (X-G's precool) and as each gated D run's precool (LEAD-RULINGS-2 R5-1). |
| `x-g` | R | `reference_c` (the soak R it gated against); `reference_source` = `r1_soak_reference` (R5-1) |
| `d-spam-benign-s1-a`, `d-spam-benign-s1-b`, `d-bank-benign-s1` | R | `energy_j`; `admitted_turns` (int ≥ 0); `x7` (bool); `deadman.T_dead_s` (the deadman the run armed at G0 entry; it must equal the `step-d` `slots.T_dead`, or R1 refuses at that run); `deadman.phases_s.{G0,G1,H,decode,prefill,tool,tail}` (finite seconds) (ruling 1(a), 1(d)); `battery_drain_pct_per_h`; `reference_c` and `reference_source` = `r1_soak_reference` (the run gates against the soak R, as W1 members consume member 5's R; R5-1); `gate_waits_s.{G0,G1,H}` (per-gate waits, s; R5-7's S6 TODO input) |
| `d-planning-turn-r-plus-0c`, `d-planning-turn-r-plus-2c`, `d-planning-turn-r-plus-4c` | R | quiet fields; `reference_c` (R, identical across the three); `g0_release_c` (the S_slow **measured** at release); `delta_slow_c` (the gate band, identical across the three, > 0); `energy_j`. The driver refuses a release outside R + offset ± δ_slow and fits β_T on the measured release temperatures (ruling 6). A G0 that did not release is not a designed start state: the runtime fails the segment (exit 3) instead of reporting its last sample as a release (round-4 executing review HIGH-1). |
| `d-4bit` | | none (optional) |
| `g0-release-soak` | R | `released`: true if S_slow came within δ of R before the G0 cap (600 s), false on timeout |
| `high-power-aba-a1`, `high-power-aba-b`, `high-power-aba-a2` | R | quiet fields; `g0_released` (bool: the leg's own G0 released); `t_decline_s`: positive seconds, or null for no decline (infinite) when `g0_released` is true. A leg whose own G0 did not release has no turn: the runtime exits 0 with `g0_released: false`, `t_decline_s: null` and `leg_status: inconclusive` (LEAD-RULINGS-2 R5-3); the driver never reads that null as "no decline". |
| `harvest` | | `charge_resume_soc_pct`: the SoC (%) at the first observed charge resume during R1, or null if charging never resumed (ruling 4(b)) |

`battery_drain_pct_per_h` is the OLS drain rate in %/h (positive = discharging) over the segment's non-charging `pmset -g batt` samples, or null when the segment charged throughout. The driver records both ruling 4(b) outputs in `r1_slots.battery`: the drain under D (mean of step-d and the three gated runs) and under the 30B (step-30b), and the charge-resume SoC.

## How the driver uses the fields

- **U5 (ruling 6 with lead ruling L2, c = 1.0).** Inputs:
  - σ_pair = max(|E_a − E_b|, 2.97 J), where E_a and E_b are the `energy_j` of the two spam/benign replay runs;
  - δ_slow is the planning-turn `delta_slow_c`.
  - a replay run that admitted no turn (its G0 did not release, so `energy_j` is 0) makes |E_a − E_b| meaningless; U5 is then INCONCLUSIVE with `sigma_pair_valid: false` and the reason (round-4 executing review HIGH-2).

  The verdict:
  - PASS if |β_T|₉₀·δ_slow ≤ σ_pair;
  - FAIL if |β_T|·δ_slow > σ_pair;
  - INCONCLUSIVE otherwise.
- **Order (LEAD-RULINGS-2).** calibration-pre, idle soak, 30B step, 600 s cooldown, the A-B-A legs, then **under the adopted series mode** (High Power if A-B-A adopts, else Automatic; protocol v4 :243-251, R5-5): step-d, the post-D cooldown, X-G, three times (precool, gated D run) (R5-1), the designed start states **warmest first** (R + 4, R + 2, R + 0 °C: after D_bank the host is warm and the heater is clamped at duty 0, so the highest target needs the least natural cooling and each later state inherits the earlier ones' cooling time; R5-2), the optional 4-bit, then Automatic is restored before calibration-post and the harvest. Each A-B-A leg must record its leg mode, and each model member after the decision the series mode, as an observed integer (ruling 7; an unobserved value refuses R1); `r1_slots.slots_ac_powermode` records it and the kit requires it to equal `ac_powermode`.
- **Thermometry bar (protocol v4 :243-251, R5-5).** Around both planning-turn steps (30B and D) the runtime journals every inventoried `T*`/`F*` key at 1 Hz (`DIR/inventory/inventory_journal.jsonl`) from before the member through a fixed 600 s recovery; the step member idles 300 s after its G0 release, so the last 300 s before prefill are quiet. The WP14(a) classifier (`smc_enumeration.rank`, stage `r1`) runs on idle = the 300 s before prefill dispatch, load = prefill dispatch to the last decode, recovery = 600 s. The D classification fills `r1_slots.thermometry` (`bar`: pass only with both picks; `r1.sensor_pick_changed` when a pick differs from R0's); the 30B one is recorded only. The kit refuses W1 unless the bar passed, unless W1's gate keys (`R1.thermal_policy.sensors`) are in the D classification's die and heatsink lists, and, when R1 changed (or did not report) R0's picks, unless the lead recorded `thermometry.lead_verification`. For changed picks the runtime also computes `thermometry.s7_for_r1_picks` from the inventory journal (reference = the quiet-window median, band max(1.0 °C, 3 SD), S7 = min(300 s, 3 × peak-to-band recovery)) for that verification. S1-S4 stay the R0 keys' step response (R5-7).
- **Batch-window bounds (ruling 8).** A quiet segment is admitted only if its bound ends before 11:45 or starts after 13:15: 1,800 s, plus the 600 s recovery for the 30B and D steps and the 900 s preheat cap for the designed start states, plus 600 s when a release precedes it.
- **Gated runs (R5-1).** Each gated D run is preceded by `idle-until-soak` (cap 1,500 s) into `<name>.precool`, and X-G by the post-D cooldown. A precool that did not reach the G0 band makes that run INCONCLUSIVE (recorded, never a refusal): its duty-bar row has verdict `inconclusive`, the duty bar's overall verdict is `fail` if any judged run fails, else `inconclusive` if any run is inconclusive, else `pass` (`pass` is true only for `pass`, so the kit needs a recorded lead fallback otherwise), and a replay-pair run that is inconclusive makes U5 INCONCLUSIVE with `sigma_pair_valid: false`.
- **S6 (R5-7).** S6 = δ_slow (S5) until the FD 2.6 tuning. `r1_slots.s6_tuning` records the TODO with the gated runs' median G1 and hold waits (`gate_waits_s`), the input the lead tunes S6 on.
- **A-B-A (ruling 16).** The sequence for each leg:
  1. The driver sets the mode with the narrow sudo rule and reads it back.
  2. It waits outside 11:45-13:15 local (ruling 8).
  3. It runs `g0-release-soak`, then the leg.

  A leg is redone, after another release, on sustained load. If any accepted leg's release timed out (`released: false`), or a leg's own G0 did not release (`g0_released: false`, R5-3), adoption is INCONCLUSIVE, the series stays Automatic and R1 continues; the ruling 16 rule is then `not_evaluated` when a leg has no t_decline.
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
- **Step tests** (10k fed prefill + 4,096 seeded decode) are one-turn episodes of a deterministic long-prefill task (`StepTask`), gated by a G0 against the soak R with no G1 or holds so the decode is continuous. For `step-30b` and `step-d` the G0 runs on its own 600 s cap, a released G0 is followed by 300 s of quiet, and only then is the step deadman armed, for the decode (`token_budget.deadline_origin` = `R1_after_G0_release_and_quiet`).
- **Designed start states** keep the preheat (900 s) and G0 (600 s) caps of their own; the deadman is armed after them, for the decode only (`deadline_origin` = `R1_after_preheat_and_G0`; LEAD-RULINGS-2 R5-2).
- **Sensor segments** (`idle`, `idle-until-soak`, `g0-release-soak`) run a `ThermalSession` alone in `DIR/<label>/align_thermal.jsonl`; `g0-release-soak` starts powermetrics for the PM state, pre-rolls 65 s for the slope window and calls the production `wait('G0')` with R as its reference.
- **Read-back** uses `read_episode_bundle`, `thermal_desk.read_bundle_record` (`energy_j` is its `turn_owned_j`), `thermal_desk.native_pm_samples` (the PM clock) and `attribute_episode` (decode energy).
- **Completeness** (round-4 executing review HIGH-1, Fable cold pass HIGH-1): a step (`step-30b`, `step-d`, `d-4bit`), planning-turn or A-B-A member must be exactly one turn, `succeeded`, with none of `episode.deadman:`, `episode.decode_budget:`, `episode.g0_unreleased:`, `episode.time_guard:`, `episode.context_limit:`, `episode_error:`, `endpoint_error:`, `thermal.start_gate_timeout`, `thermal.gate_timeout:`, `thermal.hold_timeout:`, `thermal.state_unobserved`, `thermal.collector_failed`, `thermal.custody_invalid` or `thermal.status_source_missing` (`r1_runtime.INCOMPLETE_MEMBER_FLAGS`); otherwise the runtime exits 3 and R1 refuses. A malformed or refused tool-call flag does not cut the decode and does not count. The gated D runs and X-G are exempt: their truncation is the duty-bar evidence.
- **Journals**: `contract.LoadJournal` once a second (the runtime's own PID tree excluded) and `pmset -g batt` every 30 s (`DIR/battery.jsonl`).

Field derivations and their stated approximations:

- `sensor_series_c`: the valid 1 Hz reads of the R0 gate keys in order; a failed read is dropped, never interpolated.
- `recovery_curve`: `[t_s, S_slow]` per read until |S_slow − R| ≤ δ_slow, or the cap.
- `deadman.phases_s`: G0/G1/H from the episode's `ThermalSession.record()` intervals; prefill (turn start to first token), decode (first token to turn end, holds removed) and tool time from the episode; tail = episode end past the G0-entry deadline.
- `slots` (step-d): S1/S2 = fast-key ΔT and t63; S3/S4 = slow-key ΔT and cooling τ (key names and the FD 2.6 class checks are in `slot_detail`); S5 = δ_slow = max(1.0 °C, 3 × soak SD); S6 = the δ_slow the R1 gates use (TODO: the FD 2.6 S6 tuning, tied to the gated runs' median G1 wait, R5-7); S7 = G_turn = min(300 s, 3 × the recovery from the step peak to within δ of R, observed for a fixed 600 s after the last decode); S8 = N_chunk; S9 = t_decline (FD 2.6; when no decline occurs it is censored at the observed decode length and N_chunk = 2,048, A1 A3.1; no PM clock support refuses); I_D = member wall − (episode end − G0 entry); B_D = 1024 × ⌊((1800 − I_D)/1.13544 − prefill_s) × r_decode / 1024⌋, ≤ 40,960; T_dead = (1750 − I_D)/1.13544 (L1's first term; the kit applies the tail); class = D's protocol class (A1 A3.1), with the FD 2.5 rule recorded beside it.
- `e_D_j_per_token`: decode-segment energy over decode tokens of the step-d episode.
- Designed start states (planning kinds): a proportional MLX heater (`ProcessHeater`, a child process) preheats to R + offset and holds S_slow there during the production G0, whose reference is R + offset on S_slow (S_fast is not banded); it stops before the episode starts. `g0_release_c` is the G0 interval's measured release.
- `released`: the G0 outcome. `t_decline_s`: the step's t_decline, null when no decline occurred.
- `calibration-pre`/`-post` record the read-only host snapshot at the brackets; the meter calibration itself belongs to the R1 night plan's scaffold. `harvest` writes `DIR/harvest_manifest.json` (SHA-256 of every file under the R1 output) and aggregates the charge-resume events.
