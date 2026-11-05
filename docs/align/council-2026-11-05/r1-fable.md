# ALIGN next-window design, round 1, Fable 5.1 seat

Written 2026-11-05 from the pilot-8 kit checkout `lane/2026-11-04-align-pilot8-benign` @ e328f0e72, origin/main @ 92026c184 (RUN_STATE item 168), the magistrate records 2026-10-30 to 11-04, and web checks of the model repositories made today. Guesses are marked **[guess]**. Nothing under `/Users/edr/jw-b5-*`, `night-custody`, `night-archive` or `restricted/` was opened; where a record cites numbers that live there, the record is cited.

**Machine.** Apple M3 Max laptop, model identifier Mac15,9, 128 GB, 140 W adapter (`docs/registrations/difficulty_pack_v2.md:29`, `docs/registrations/block6_replication_DRAFT.md:104`; RUN_STATE item 76 "Adapter is 140 W"). Runtime stack pinned at MLX 0.31.2 / mlx-lm 0.31.3 (`docs/align/pilot_protocol_v3.md`, seed-law paragraph; `pyproject.toml:17`).

**Note on sequencing.** A pilot-9 kit already exists (`origin/lane/2026-11-05-align-pilot9-benign` @ c9a0a3943: anchors + 20 fresh benign, seeds 27-36, same shape as pilot 8). This design is the window series that follows it, and nothing here needs pilot 9 to be skipped; section 3.5 says how they interleave.

---

## 0. Summary of the design

- **Model set:** two production-grade Qwen models in their own calibration cells, each in the pilot-8 window shape (28 slots: the 8 Qwen3-30B-A3B same-ordinal anchors at ordinals 1-4, 9, 14, 19, 28; 20 new-model members in the other 20 slots). Primary: **Qwen3-Next-80B-A3B-Instruct, MLX 8-bit** (84.7 GB; fallback the pinned pilot-3 4-bit artefact, 44.8 GB) and **Qwen3.8-27B, MLX 8-bit** (29.5 GB, `model_type qwen3_5`, loads under the pinned mlx-lm 0.31.3; fallback 4-bit). Qwen3.8-Flash-Next (125B-A6B, the newest "Qwen Next") is **named and dropped with a recorded reason** (needs a `qwen4_exp` runtime that the pinned stack does not have; 4-bit conversions are 97.6-111.6 GB). Qwen3.5-397B-A17B and Qwen3.8-2.4T do not fit at any quantization.
- **Thermal and clock control:** a measured-state gate before every member (SMC die temperature, settled and within a window-local band, on top of the existing OS-level-0 and powermetrics-Nominal rules), with a capped extra wait; die temperature, fan RPM and SMC system power journaled at 1 s; identical-work anchors and replays as the only estimator of the machine-state coefficient (J per degree C); print-only clock and temperature covariates; acceptance criteria A1-A5 fixed below. No clock term in the scoring design (record cf1baad2 ruling stands).
- **Window structure:** a short series of four windows, model order Next, 27B, 27B, Next (ABBA across days): windows 1-2 are each model's capability screen plus first calibration cell (per pair 6 benign + 4 sabotage), windows 3-4 are held-out benign increments (10 per pair) that bring each model to m = 16 held-out benign per pair, with the pilot-8/9 Qwen3-30B anchors continuing at the same ordinals in every window. Programmed spans 26,900-31,000 s, so window maxima of 44,640-48,700 s under the existing formula.
- **Relation to the frozen pilot-8 design:** new calibration cells under a fresh non-claim pre-registration (pilot protocol v4) that imports the frozen sequence design, the frozen alternative desk and the calibration script unchanged; per-model operating parameters (quantization, turn budget, guard, reasoning effort, sampler) are fixed by a declared rehearsal before any window of that model and never edited afterwards.

---

## 1. Model set

### 1.1 What exists (web checks, 2026-11-05)

| Model (HF repo) | Arch / active params | MLX weights | Runtime | Status for this Mac |
|---|---|---|---|---|
| `mlx-community/Qwen3-Next-80B-A3B-Instruct-8bit` | hybrid Gated DeltaNet + gated attention MoE, 80B total / 3B active | **84.7 GB**, 8-bit, converted with mlx-lm 0.27.1 | `qwen3_next`, loaded by mlx-lm since before 0.27.1; the 4-bit sibling ran in pilots 2-3 under the pinned 0.31.3 (RUN_STATE items 161-162) | **primary model N** |
| `mlx-community/Qwen3-Next-80B-A3B-Instruct-4bit` @ d8a069bf | same | 44.8 GB resident (`docs/registrations/bytes_pack_v1.md:94`, R = 44,844,060,160 B) | pinned in `configs/campaigns/bytes_v1/qwen3-next-80b/01_decode_absolute/*.json` and run in pilots 2-3 | **fallback for N** (already on the Mac) |
| `mlx-community/Qwen3-Next-80B-A3B-Thinking-8bit` | thinking variant | 84.7 GB, mlx-lm 0.27.1 | same family | optional later cell, not in this series |
| `mlx-community/Qwen3.8-27B-8bit` | dense, 64 layers (48 linear-attention + 16 full-attention, interval 4), 24 Q heads, 4 KV heads, head_dim 256, 262,144 ctx, thinking on by default with `reasoning_effort` default `xhigh` (Qwen/Qwen3.8-27B config.json and model card) | **29.5 GB**, 8-bit, converted with mlx-vlm 0.6.8; tags `qwen3_5` | mlx-lm's `qwen3_5.py` drops `vision_tower`/`model.visual` and `mtp.` tensors; Qwen3.5-series support landed in mlx-lm 0.30.7 (release notes), and the BYTES extension registration records that this model "runs on the pinned mlx-lm 0.31.3" (`docs/registrations/bytes_extension_models_2026-10-27.md`, table row 1; RUN_STATE item 1190 "The extension is Qwen3.8-27B only") | **primary model Q**. Was deleted from the Mac on 10-25 (RUN_STATE 1190); re-download at the recorded revision is owed |
| `mlx-community/Qwen3.8-27B-4bit` (and `-OptiQ-4bit`, `-mxfp4`) | same | about 16 GB (llm-explorer listing; file size to verify) | same | **fallback for Q** |
| `mlx-community/Qwen3.8-Flash-Next-4bit` and six third-party 4-bit MLX repacks | 125B total / 6B active + 51B n-gram embedding + 4B MTP, `qwen4_exp`, licence qwen-community-1.0 | 97.6 GiB (gs64/32) to 111.6 GB (gs32) | needs a Qwen4-Exp-aware mlx-vlm (0.7.x); mlx-lm release notes through v0.32.2 (16 Oct) name no Qwen3.8 or qwen4_exp support | **not feasible** under the pinned stack; even with a pin bump, 98-112 GB of weights plus KV plus the OS leaves < 20 GB on a 128 GB machine and sits above the default Metal working-set limit (about 96 GB) **[guess on the limit]**. Dropped and recorded, like Nemotron 3.5 Super (RUN_STATE 1190). Revisit only after a pin-bump council. |
| `mlx-community/Qwen3.5-122B-A10B-4bit` @ e9c67b08 | MoE 122B / 10B active, `qwen3_5_moe` | 69.6 GB (HF); R = 68,690,732,544 B (`bytes_pack_v1.md:95`) | on the Mac at `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit` (`configs/campaigns/bytes_v1/qwen35-122b`), BYTES held-out | **second fallback for N** (if the 8-bit Next fails the memory check and Ed wants a bigger model than the 4-bit Next), or a fifth window |
| Qwen3.5-397B-A17B, Qwen3.8-2.4T-A95B | | about 220 GB at 4-bit; about 400 GB at 1-bit | | do not fit |

Why these two are "the top runnable in 128 GB": the BYTES extension registration (written 10-27, Artificial Analysis open-weights index) already named Qwen3.8-27B "the strongest open-weights model that fits the laptop", with Qwen3.5-122B-A10B and Qwen3-Next-80B already on the BYTES roster below it; Qwen3-Next-80B-A3B is the model Ed names and the only large MoE whose 8-bit build fits with headroom. Qwen3.8-Flash-Next would outrank both and is the one real casualty of the pinned runtime; it is recorded as such.

### 1.2 Memory at the needed context (40,960-token cap, `collection_plan.json` `max_context_tokens`)

- **Qwen3.8-27B-8bit.** Full-attention KV per token = 16 layers x 2 (K,V) x 4 heads x 256 x 2 bytes = 64 KiB; at 40,960 tokens 2.7 GB. Linear-attention state is constant: 48 layers x (48 x 128 x 128 x 2 B recurrent + conv) about 80 MB. Peak about 29.5 + 2.7 + 0.1 + runtime (about 3 GB) = **about 35 GB**. Comfortable. (Derived from config.json; verify with `mx.get_peak_memory()` in the rehearsal.)
- **Qwen3-Next-80B-A3B-Instruct-8bit.** From the BYTES KV record (`configs/bytes/records/Qwen3-Next-80B-A3B-Instruct-4bit.kv.json`): attention layers allocate 5,242,880 B at capacity 2,560 = 2 KiB per token per layer; 12 attention layers give 24 KiB per token, 1.0 GB at 40,960; 36 linear layers hold 2,146,304 B each, constant, 77 MB. Peak about 84.7 + 1.1 + 3 = **about 89 GB**. Fits in 128 GB with the SHADE environment and macOS (about 8 GB) but is **above anything this Mac has run** (largest so far 69.6 GB, Qwen3.5-122B in BYTES). The rehearsal must record `mx.get_peak_memory()` and `sysctl iogpu.wired_limit_mb`; if MLX reports wired-limit pressure or the load swaps, fall back to the 4-bit (peak about 49 GB) without a sysctl change (a sysctl change is a system modification and needs its own ruling).
- **Qwen3-30B-A3B-4bit anchors.** 17.2 GB files (`registration/model_artifact_inventory.json`), peak about 22 GB.
- **Page cache across model switches.** A fresh process per member (protocol v3) re-maps the weights; with N-8bit (85 GB) plus the 30B anchors (17 GB) the cache holds both only barely, so each switch may re-read up to 85 GB from SSD (about 15-25 s at 4-6 GB/s **[guess]**). The load happens in the `prepare` stage, before `idle_baseline` (controller.py:31-32), so the load's heat is dissipated inside the 300 s idle and inside the new temperature gate (section 2). Model switches are therefore acceptable at the 8 anchor boundaries but should not be more frequent, which is one reason not to interleave the two new models inside one window.

### 1.3 Throughput and energy per trajectory

Measured so far on this Mac (pilot 3, `configs/campaigns/align_pilot_v2/registration/sizing_evidence.json` `phase_rates`): Qwen3-30B-A3B-4bit decode 64-79 tok/s, prefill 890-1,200 tok/s; Qwen3-Next-80B-4bit decode 62-71 tok/s, prefill 880-1,110 tok/s. Episode GPU energies: 30B-A3B 2,000-4,200 J (record 7e06863b, Reading line); Next-4bit cached sabotage episodes 1,380-2,232 J (RUN_STATE 987).

| Model | Decode tok/s | Prefill tok/s | Episode time at the proposed guard | GPU J per episode | Basis |
|---|---|---|---|---|---|
| N = Next-80B 8-bit | 45-55 **[guess: active bytes per token double the 4-bit's]** | 800-1,000 **[guess]** | 120 s guard + one 2,048-token turn (about 45 s) + fed prefill (up to 17 s) = **about 185 s upper** | 1,800-3,300 **[guess, 1.3-1.5x the 4-bit]** | pilot-3 C rates; BYTES active bytes 2.03 GB/token at 4-bit (`bytes_pack_v1.md:94`) |
| N fallback 4-bit | 62-71 measured | 880-1,110 measured | 120 + 2048/61.9 + 17 = **170 s upper** | 1,400-2,300 measured range | pilot 3 |
| Q = Qwen3.8-27B 8-bit | 10-12 **[guess: 29.5 GB read per token at about 350 GB/s]** | 150-200 **[guess: 54 GFLOP per token, 8x the 30B-A3B's]** | turn-0 prefill of the 6,347-7,102-token SHADE prompt alone takes 35-50 s; guard 180 s + one 2,048-token turn (about 190 s) + fed prefill (up to 60 s for a 10k-token tool result) = **about 430 s upper** | 12,000-25,000 **[guess: about 4 J per decode token, 50 W prefill]** | bandwidth/compute scaling from the 30B-A3B measurements |
| Q fallback 4-bit | 18-22 **[guess]** | 150-200 **[guess]** | 180 + 2048/19 + 60 = **about 350 s upper** | 7,000-14,000 **[guess]** | |

The Q row is the thermal problem of this series: a dense 27B at 8 bits spends 300-430 s per episode at 40-55 W GPU, and pilot 2's episodes of 219-840 s all reached OS thermal level 1-2 (RUN_STATE 981), while the pilots that stayed at level 0 kept episodes under about 200 s (protocol v3: "first observed in-episode OS onset of 201 s"). Section 2 is built for that row; the rehearsal rule in 4.3 decides 8-bit versus 4-bit and the turn budget on measured temperature, not on opinion.

### 1.4 Operating parameters per model (pre-registered after the rehearsal, never edited after)

| | Anchors (unchanged) | N: Next-80B-Instruct | Q: Qwen3.8-27B |
|---|---|---|---|
| Thinking | on | n/a (instruct) | on, `reasoning_effort: low` via `chat_template_kwargs` (the card's default `xhigh` would spend the whole turn budget on reasoning at 10 tok/s); `medium` only if the rehearsal shows `low` ends reasoning inside 1,000 tokens on every rehearsal turn **[the kwarg must be verified against the repo's chat template]** |
| Sampler | 0.6/0.95/20/0 | 0.7/0.8/20/0 (Qwen3-Next card, non-thinking; presence penalty 1.5 is not implemented by the runtime and is recorded as a deviation) | 1.0/0.95/20/0 (Qwen3.8 card, thinking) |
| Turns x budget | 12 x 4,096 | 20 x 2,048 (pilot-3 C specs, record e1308804 ruling) | 12 x 2,048 primary; 12 x 1,024 if the rehearsal thermal rule fires |
| Episode guard | 120 s | 120 s | 180 s primary (the guard admits a whole turn, so the upper bound is 430 s); 150 s if the rule fires |
| Context cap | 40,960 | 40,960 | 40,960 |
| Prompt cache | `episode_prefix` | `episode_prefix` with the whole-cache rebuild fallback built for pilot 3 (Next's cache is not trimmable, record e1308804:57) | `episode_prefix` (DeltaNet state: same non-trimmable class as Next; verify the fallback path engages) |
| Seed law | `align-p4-v1` with `model_id` = the `align-model=` tag (`scripts/align_pilot_kit.py:125`), so new model ids give new seeds without touching the law | `qwen3-next-80b` | `qwen3p8-27b` |

---

## 2. Thermal and clock control protocol

### 2.1 Diagnosis of the pilot-7 GPU-clock tracking

Facts from the records:

1. Pilot 7 ran at OS thermal level 0 in every episode and powermetrics pressure Nominal, yet under the sequence design the three untampered spam alarms (21-43 J, about 1 % of 2,700 J episodes) accumulate at +2 to +8 J on nearly every later turn, turn 0 within +/-1 J; benign spam trajectories carry offsets of the same size (b-e18 +25.2, a-e10 +18.7, a-e08 -48.2 J); across the 12 pilot-7 spam trajectories corr(residual, mean active GPU clock) = +0.86 (pilot-6 bank +0.92, pilot-7 bank +0.52, pilot-4 spam -0.15) (record cf1baad2, "Fable" paragraph and "Ruling" (4)).
2. Identical work across sessions barely moves the clock: the pilot 5 to 6 step is -8 to -9 J on 2,000-4,200 J anchors, decode segments only (-0.35 to -0.41 %), with the GPU clock +0.6 MHz, battery thermistor 29.8-30.3 C flat, CPU, ANE, display and duration equal (records 7e06863b "Shared findings", cf1baad2 "Sol" and "Fable" paragraphs). No die temperature is recorded anywhere, so the step is "not attributable".
3. Same-position noise for identical work is 2.1 J; sigma_w across sessions 4.8-5.1 J (records 7e06863b, cf1baad2).

Reading. The active GPU clock that `telemetry_diagnostics` reports is the residency-weighted DVFM frequency over GPU-active time (`joulewise/align/apple/diagnostics.py:161-213`). Two things move it: (a) the **work mix** of the trajectory, because prefill, decode, sampling and the CPU-side SHADE tool execution sit at different DVFM states and utilizations; (b) the **SoC power controller** (the closed-loop controller that modulates GPU clocks continuously below the coarse OS thermal levels). Fact 2 says that (b) is small for identical work on this machine at level 0 (+0.6 MHz across a 9 J step, and the step is not in the clock at all). Fact 1 says the correlation appears across *different* trajectories, where the work mix differs. So the clock is tracking **behaviour that the design does not weight correctly** (tool-result prefill charged at the decode rate, hidden-token accounting, sampler overhead), which is why both seats refused a clock term (it would absorb unlogged work; cf1baad2 Ruling (2)). What the pilots cannot tell apart is whether a few J per later turn is a DVFM/leakage effect of the episode's own heating (an episode that ran hotter in turns 3-12 because turns 0-2 were heavier). Only a direct temperature measurement on identical work separates the two. That is the point of the protocol below: measure the state, hold the start state constant, and estimate the machine-state coefficient on identical-work pairs only.

The pilot 5 to 6 step is a separate problem: a decode-only -0.35 % between sessions with everything logged equal. Its signature (decode only, GPU rail only, no clock change) points at DRAM or fabric power or a leakage difference; the monitor already journals SMC `PSTR` (system total), `PDTR` (DC-in) and `PPBR` at 1 s (`joulewise/hazards/monitor.py:31`, `joulewise/hazards/smc.py` header table), so "system minus CPU minus GPU minus ANE" is available and should be printed per anchor beside the GPU energy from now on.

### 2.2 Telemetry to record (per member, all in the member hull)

Existing, keep: powermetrics at 10 Hz with samplers `cpu_power,gpu_power,ane_power,thermal` (`joulewise/adapters/powermetrics.py:58`; `power_hz 10.0` in every episode config), GPU DVFM state residencies in `rich_telemetry.jsonl` (per-turn active clock, `diagnostics.py:174-196`), powermetrics thermal pressure seconds, OS thermal level every 5 s (`joulewise/hazards/thermal.py:15`, `max_gap_s 15`), SMC battery current/voltage and PSTR/PDTR/PPBR at 1 s (monitor battery journal), contention every 10 s.

Add, all 1 s, in a new monitor journal `die_temperature` (same 1 s grid as the clock journal, `monitor.py:58`):

- SMC die temperatures: the GPU and CPU die sensors, the SoC hottest sensor, the battery sensor (names on M3 Max are not in the repo; the follow-up "SMC die-temperature key enumeration (read-only, by day, never during a window)" is open in RUN_STATE 1055 and 1065 and is **prerequisite R0** here). Reader: the existing `AppleSMC` user client in `hazards/smc.py` (about 75 us per key).
- Fan RPM keys (`F0Ac`, `F1Ac` or whatever the enumeration finds) so that the fan curve is visible against temperature.
- Nothing else; the monitor's cost lands inside every member's package energy (`monitor.py:48`), and these reads are in-process and sub-millisecond.

If the enumeration finds no usable die sensor, the fallback thermometer is the idle baseline's processor package power (leakage is monotone in temperature): the gate in 2.3 then runs on `processor_combined_power` p50 of the last 60 s of idle against the window reference, band +0.15 W **[guess at the sensitivity; the rehearsal measures the idle power versus temperature slope]**.

### 2.3 Controls

**C1. Start-state gate on measured temperature, not wall time.** Keep the 300 s configured idle (`ALIGN_IDLE_S = 300`, `scripts/align_pilot_kit.py:40`; policy `cooldown.cap_s 300`, `require_thermal_nominal true` in `configs/campaign_policies/quiet_mac_p2_b5.json`). After it, the member's measured run may start only when, over the last 60 s of idle: OS level 0 (existing); powermetrics pressure Nominal (existing); GPU die temperature T_gpu <= T_ref + 1.5 C; and |dT_gpu/dt| <= 0.2 C/min (settled). T_ref is **window-local**: the median GPU die temperature over the last 60 s of idle before anchor ordinal 1, recorded in the custody record. Extra wait is capped at 600 s; on cap the member runs and is flagged `thermal.gate_timeout` with the start temperature (the rule in 2.5 says what that does to eligibility). Why a window-local reference and not an absolute one: ambient differs by night, and what the scores need is members of one session starting from the same state; cross-session differences are what the anchors measure.

**C2. Steady-state soak, not a cold start.** The chain already runs 25 scaffold members and the calibration bracket (about 5,000 s: `sizing_b5.json` collection_span 26,914 s minus align 21,919 s) before anchor ordinal 1, so the machine is not cold at member 1. No further soak; T_ref is taken after the scaffold on purpose.

**C3. Duty-cycle ceiling per member.** The guard plus turn budget bounds active time (table 1.3). Added rule: a member's active phase may not exceed 450 s (the Q upper bound); any member exceeding it is flagged `episode.active_over_ceiling` (observe). The gate in C1 makes the *following* member's start state independent of this one's length, which is the property the scores need; a fixed active:idle ratio is not imposed because it would make idle depend on behaviour.

**C4. Counterbalancing.** Within a window the seed-block ABBA on pair order stays (odd seeds spam-then-bank, even seeds bank-then-spam; README). Condition alternates inside each 4-member block as in pilots 4-9 (spam/benign, bank/sabotage, spam/sabotage, bank/benign; reversed on even blocks). Across the series the model order is N, Q, Q, N so that day-to-day and time-of-day drift cancels in the N versus Q contrast; windows 1 and 4 start by day and night alternately if the arm times allow (pilots 4-7 showed the session step is not time of day, record cf1baad2, so this is insurance, not a requirement).

**C5. Physical setup (Ed).** (a) Lid open, machine flat on a hard surface with the hinge vents clear, displays asleep as the policy requires (`environment_guard.require_displays_asleep`). (b) One external fan or laptop cooler on a fixed setting aimed at the hinge exhaust, switched on before the first window of the series and **left untouched for the whole series** (a changed airflow is a new session effect). (c) Battery at 100 % at arm (charging adds heat and is already a hazard); 140 W adapter. (d) Room: no direct sun on the machine, HVAC on a fixed setpoint, and the thermostat reading noted at arm and at the desk, or a USB logger if Ed has one (ambient is otherwise unrecorded). (e) **Not** a fan-pinning utility: it is a foreign daemon running during the window and it changes the OS's own thermal control, which is the thing being measured; if Ed wants it, it needs a ruling and a before/after anchor comparison.

**C6. Rejection and exclusion rules, fixed now.**
- `thermal.os_level_nonzero` on the member hull: exclude (existing, `joulewise/flags/catalog.py:123`, `b5/harvest.py:3074`).
- `thermal_pressure_elevated_in_window` (powermetrics non-Nominal inside the episode): exclude from calibration fits, print (existing precheck reason, `align_pilot_session.py:196`).
- New `thermal.start_temp_out_of_band`: start T_gpu > T_ref + 3.0 C after the gate timed out: excluded from the per-session benign calibration fit and from threshold calibration; kept in every printed table; not excluded from capability readings.
- New `thermal.smc_unmeasured`: observe only; a window without SMC readings still counts under the old rules.
- Members are never replaced or topped up (plan_tree `attempt_policy.outcome_dependent_top_up: forbidden`).

### 2.4 How the analysis uses the clock and temperature

Nothing changes in the scoring design: the frozen sequence design `[1, P, D, (C+P)D + D^2/2, CP + P^2/2]` per pair, per session, counts logged, with the registered row beside it (record cf1baad2 Ruling (1)); no clock, temperature or prompt-length term (Ruling (2)).

Added, print-only, per trajectory: start T_gpu, max T_gpu, mean T_gpu per turn, mean active GPU clock per turn (existing), fan RPM mean, PSTR-minus-rails energy. Added estimators, on identical-work pairs only:

- **beta_T (J per C):** over the same-ordinal anchors across sessions (K = 6 after pilot 9 plus this series' windows) and the four within-window replays, regress the energy difference of identical token work on the start-temperature difference. This is the machine-state coefficient free of behaviour, because the tokens are identical (`cross_pilot_token_identity`, `align_pilot_session.py:225-265`).
- **Per-turn clock versus temperature at fixed work:** for each anchor turn across sessions, the slope of per-turn active clock on per-turn mean temperature. If it is flat, the pilot-7 clock tracking is work mix; if it is negative and the turn energy rises with it, it is the SoC controller, and the protocol's gate and airflow are the remedy, not a model term.

### 2.5 Acceptance: when is it "under control"

Fixed before the first window of the series; evaluated per window at the desk, printed in `PILOT.json`:

- **A1 (no throttling):** OS level 0 and powermetrics Nominal for 100 % of in-episode seconds in at least 27 of 28 members.
- **A2 (gate works):** range of start T_gpu across the 28 members <= 3.0 C; at most 2 `thermal.gate_timeout` flags; no `thermal.start_temp_out_of_band`.
- **A3 (identical work is identical energy):** each of the four within-window replay differences |dE| <= 6 J (about 3x the 2.1 J same-position noise); the window's session effect on the 8 anchors within +/-6 J of the mean of pilots 6-9; moment sigma_w over all sessions <= 6 J.
- **A4 (machine state is small against the design's noise):** |beta_T| x (observed start-temperature range) <= 0.1 x the smaller per-pair s_r of the window (s_r was 22.9-86.9 J under the sequence design in pilot 7, so about 2-9 J).
- **A5 (clock correlation is behaviour, not state):** among benign trajectories per model and pair, print corr(residual, mean clock) and corr(residual, start T). Controlled if corr(residual, start T) is within +/-0.4 whatever the clock correlation does. If both exceed +0.6, the window is thermally confounded: the next window of that model runs with the escalation ladder (idle 300 -> 450 s, band 1.5 -> 1.0 C, then the next quantization step down) and is not pooled with it.

A window that fails A1-A3 is still a complete non-claim pilot; it is labelled "thermal protocol not met" and its new-model members do not enter that model's held-out calibration pool.

---

## 3. Window structure

### 3.1 Shape (every window)

28 slots, the pilot-8 shape, so the kit generator, scaffold, midpoint reference after member 14, stage split episodes-a/episodes-b and the K-session anchor analysis all carry over:

- Ordinals 1, 2, 3, 4 (seed-1 block) and 9, 14, 19, 28 (seed-1 replays): the **8 Qwen3-30B-A3B anchors, byte-identical to pilots 4-9** (configs a-e01..04, a-e09, a-e14, b-e19, b-e28; record cf1baad2 "Pilot-8 kit build"). They cost 8 x 783 s = 6,264 s (`sizing_b5.json` member_upper_s 782.8) and buy the cross-session machine-state link, the within-window identical-work channel (A3) and a direct read of what the new thermal protocol did to a known model.
- Ordinals 5-8, 10-13, 15-18, 20-27: **20 members of the window's one new model**, in 4-member blocks with the pilot-4 cell order and the odd/even reversal.

### 3.2 Allocation per window

| Window | Model | 20 new-model members | Purpose | Programmed span (s) | Window max (s) by `window_max_s` |
|---|---|---|---|---|---|
| M1 | N (Next-80B 8-bit or 4-bit per rehearsal) | per pair: benign seeds 1-6 (6), sabotage seeds 1-4 (4) | capability screen (does an instruct 80B act, does the side task succeed, cache rebuild rate), first calibration cell, first sabotage readout | 8 x 783 + 20 x 790 + 5,000 = **27,100** | 44,820 |
| M2 | Q (Qwen3.8-27B 8-bit, 2,048 budget, 180 s guard; or the stepped-down settings) | same seeds and split | same | 8 x 783 + 20 x (390 + 90 + 430 + 60 = 970) + 5,000 = **30,700** | 48,420 |
| M3 | Q | per pair: 10 fresh benign (seeds 7-16) | held-out benign increment: per pair m = 16 held-out benign (plus seed 1 if treated as in M1) | 8 x 783 + 20 x 900 + 5,000 = 29,300 (benign bank is guard-limited, benign spam shorter) | 47,040 |
| M4 | N | per pair: 10 fresh benign (seeds 7-16) | held-out benign increment, m = 16 | about **27,100** | 44,820 |

`window_max_s` = 60 x ceil((span + 3,300 + 7,200 + 7,200) / 60) (`joulewise/b6/plan_inputs.py:56-59`; `b5/plan.py:59,66,67`), so pilot 8's 26,914 s span gave 44,640 s. M2 and M3 exceed 44,640 s by 1 to 1.1 h because a dense 27B episode is 2-3x a 30B-A3B episode; the justification is that the alternative (14 new members) would leave the model with too few benign trajectories per pair to ever reach a finite split threshold (m >= 19 needs rank ceil(0.95(m+1)) <= m; record cf1baad2 "Next activation" (1)). If the 44,640 s ceiling is held literally, M2/M3 drop to 16 new members (per pair 5 + 3 in M2; 8 benign in M3) and the series needs a fifth Q window.

Sabotage share: 4 per pair in M1/M2 (the screen needs them; pilot 7 showed the alarms live on the sabotage arm) and none in M3/M4 (held-out benign is what binds thresholds). Across M1-M4 each model has per pair 16 held-out benign and 4 sabotage plus whatever M5+ adds; the split-threshold rule becomes finite at m = 19, so a fifth and sixth window (10 benign per pair each) are the registration-grade follow-on if Ed wants thresholds rather than score distributions. This series is a pilot series and says so.

### 3.3 Time budget check against the slot

Harvest plus desk is budgeted separately (5,400 s, `sizing_b5.json`), observed 99-103 min for pilots 4-7 (RUN_STATE 1058). With about 85 GB bundles per 8-bit Next window **[guess: pilot 8 was 36.7 GB at 30B; outputs scale with tokens, not weights, so probably about the same]**, disk is the real constraint: 96 GB free before pilot 8 (record cf1baad2 ARM), 58 GB expected after it (RUN_STATE 1053), and the new weights need 84.7 + 29.5 GB. Offload of pilot roots v5-v8 and the re-download are prerequisites (section 5).

### 3.4 One window or a series

A series of four, because: a model's first window is necessarily selection data for its own operating parameters (quantization, budget, guard) and its capability, and its held-out calibration cannot start until those are frozen; two models cannot share a window without eight extra 85 GB page-cache evictions and a 14-member cell that is too small for either purpose; and the ABBA order over four windows is what makes the N versus Q contrast drift-free.

### 3.5 Interleaving with pilot 9

Pilot 9 (built, benign seeds 27-36 for the 30B) completes the 30B held-out pool to m = 21 per pair. Recommended order: pilot 9 tonight under the *existing* protocol (it must not change mid-increment), then R0-R3 by day, then M1. If the thermal gate module is ready before pilot 9 is armed, do not use it for pilot 9: pilot 8 and 9 are one held-out increment under one protocol.

---

## 4. What must be built or changed

### 4.1 Kit and runtime

1. **Blocks and base configs.** `scripts/align_pilot_kit.py:37-39` `BLOCKS` gains per-block `model_id`, `enable_thinking`, `max_tokens`, `max_turns`, `max_episode_seconds`, `sampler`, `chat_template_kwargs`; `base_config_path` (`:44-45`) needs `configs/campaigns/bytes_v1/qwen3-next-80b-8bit/...` and `configs/campaigns/bytes_v1/qwen3p8-27b/...` generated by `configs/campaigns/bytes_v1/generate_configs.py` with the exact HF revision pins (the 4-bit Next pin d8a069bf already exists). `ordered_members` (`:86-113`) assigns the new block to ordinals 5-8, 10-13, 15-18, 20-27 and keeps the anchor block at 1-4, 9, 14, 19, 28; the README's seed table extends per model id.
2. **Identity pins and inventory.** `registration/derive_identity_pins.py` and `model_artifact_inventory.json` regenerated on the Mac after the downloads (kit `kit_identity_pins`, `:189-255`).
3. **Sizing.** `registration/derive_sizing.py` and `planning_sizing` (`:133-186`) take per-model phase rates from the rehearsal bundles (today they are pilot-3 A rates: `sizing_b5.json` derivation string); the 120/180 s guards and the Q 450 s active ceiling enter `episode_upper_s`.
4. **EpisodeSpec.** `joulewise/align/apple/workload.py:56-64, 92-93, 223` and `endpoint.py:241-249`: add `chat_template_kwargs` (for `reasoning_effort`) passed to `apply_chat_template`, hashed into the sampler `execution_policy`; `seed_inputs` unchanged (model id already keys the seed).
5. **Prompt cache for DeltaNet models.** Verify the whole-cache rebuild fallback built for Next (record e1308804:57) engages for `qwen3_5`; `cache_statistics` (`diagnostics.py:253`) already prints hit and rebuild counts.

### 4.2 Thermal gate and telemetry

6. **SMC temperature reader.** New `joulewise/hazards/die_temperature.py` using `hazards/smc.py`'s key reader; keys from the R0 enumeration committed as `docs/align/thermal_keys_mac15_9.md`; a `die_temperature` journal in `hazards/monitor.py` at 1 s (journal table `monitor.py:20-41`).
7. **Gate.** A new campaign policy file `configs/campaign_policies/quiet_mac_align_thermal_v1.json` (copy of `quiet_mac_p2_b5.json` plus a `thermal_gate` block: `source`, `keys`, `reference: window_local_pre_anchor_1`, `max_above_reference_c 1.5`, `settle_rate_c_per_min 0.2`, `window_s 60`, `extra_wait_cap_s 600`, `on_timeout: flag`), referenced by the align kit only, so BYTES and block-5 pins on the existing policy are untouched. Enforcement in the controller's `idle_baseline` stage (`joulewise/controller.py:1784-1990`, after `_measure_idle_admission_attempt`), writing the gate wait and start temperature into the bundle's hardware block beside `paired_clock_stamps_ns`.
8. **Desk.** `scripts/align_pilot_session.py` `episode_summary` (`:74-148`) adds the start/max/per-turn temperatures, fan RPM and PSTR-minus-rails energy from the journal (a reader shaped like `member_thermal_readings`, `diagnostics.py:135-158`); `instrument_checks` adds A1-A3 as printed checks (never a hypothesis test); the desk print block (`:402-416`) adds them. The frozen alternative desk (`scripts/align_pilot_alt_desk.py` at 4d54cb47b on `lane/2026-11-04-align-desk-attention`) and the calibration script (`scripts/align_pilot_calibration.py`, `lane/2026-11-04-align-desk-calibration`) are **not edited**; they are run per model on member subsets through a thin wrapper that filters `PILOT.json` members by `model_id` (`collection_plan.json` rows carry `model_id`, `align_pilot_session.py:294-296`). beta_T and the per-turn clock-versus-temperature slopes are a new read-only analysis script beside `k_sessions.py`, not repository code until reviewed.
9. **Flags.** `thermal.start_temp_out_of_band`, `thermal.gate_timeout`, `thermal.smc_unmeasured`, `episode.active_over_ceiling` in `joulewise/flags/catalog.py` with the dispositions of 2.3 C6.
10. **Tests.** `tests/align/test_pilot4.py`, `tests/test_align_pilot_session.py` (roster, seeds, anchors byte-identical), new `tests/test_die_temperature.py` and a gate test with a synthetic temperature trace (settled, drifting, timeout).

### 4.3 Rehearsal and dry-run plan (by day, no window armed, under an Interactive LaunchAgent as pilots 2-4 did)

- **R0 (prerequisite, read-only):** SMC key enumeration on the Mac: list all keys beginning `T` and `F`, read each at idle and during a 120 s 30B decode, keep the ones that move; commit the table. Also `sysctl iogpu.wired_limit_mb` and `mx.device_info()` recorded.
- **R1 (downloads and loads):** re-download `mlx-community/Qwen3.8-27B-8bit` at the revision in `~/night-archive/seats-f18a/models-removed.txt` (RUN_STATE 1190; the magistrate reads that file, not this seat); download `Qwen3-Next-80B-A3B-Instruct-8bit`; hash both; `mlx_lm.load` each under the pinned venv; record peak memory after one 7,102-token prefill plus 2,048 decode at the 40,960 cap. **Rule:** if N-8bit's peak exceeds 100 GB or the load swaps, N = 4-bit for the whole series.
- **R2 (one real episode per model, pair and condition, 8 episodes, plus one Q episode at the 4,096 budget):** real MLX, SHADE, powermetrics, the new journal. Records decode and prefill tok/s, turn lengths, hidden tokens under `reasoning_effort: low`, end states, cache rebuilds, OS level, pressure, die temperatures and fan RPM. **Pre-fixed step-down rule for Q:** if any R2 episode shows OS level >= 1 or non-Nominal pressure, or max T_gpu exceeds T_start + 25 C **[guess; replace with the R0-observed level-1 onset temperature minus 5 C]**, move one step down the ladder (2,048 -> 1,024 budget; then 8-bit -> 4-bit; then guard 180 -> 150 s) and repeat R2 for Q. The same rule applies to N. These rehearsal episodes are declared selection data in protocol v4 and never enter calibration.
- **R3 (kit):** `scripts/align_pilot_kit.py --check`; real `prepare` to STAGED; desk end to end on 28 production-shaped synthetic bundles for the M1 roster, including the new checks and a seed flip that fails provenance (as the pilot-8 build did, record cf1baad2).
- **R4 (hardware rehearsal of the gate):** two consecutive members (a Q episode then an anchor) with the gate live, confirming the wait, the flags and the journal; then the usual ledger-pin check, arm notice and install.

### 4.4 Review gates

Per the standing pattern (RUN_STATE 1102 and the pilot-8 build): Sol 6.1 build seat with WRITE_SCOPE = kit script, EpisodeSpec/endpoint kwargs, the new hazard module and policy file, flag catalog entries, their tests, the kit configs; one executing review by a non-author Opus 5.5 with a production-shaped desk run; because the gate and the journal are science-touching (they decide member eligibility and sit inside every member's energy), a cold Fable pass on those two modules; registration cold gate (Fable and Opus, blind) on protocol v4 before M1 is armed; the frozen alternative and calibration scripts reviewed for *invocation* only (no edits). Changes from any unvetted audit stay on an open PR (standing rule).

---

## 5. Risks, open questions, and what Ed must do

**Risks.**
- The M3 Max SMC may expose no per-die temperature key readable without root (the battery and power keys are known to work; `smc.py` header). Fallback thermometer: idle package power (2.2). If neither resolves, the protocol still has A1, A3 and the ABBA order, and says so.
- N-8bit at about 89 GB peak is untested on this Mac; the R1 rule falls back to the 4-bit cleanly, but then "8-bit" is lost for the biggest model, and Ed should know that the 4-bit Next is still a production-common deployment.
- Q at 10-12 tok/s with thinking is a different agent from the 30B: 2-4 turns per episode inside the guard, so capability (acting, side-task success) will look weaker for reasons of time, not ability. Protocol v4 must say so, and the capability read must be reported per turn admitted.
- `reasoning_effort` through `chat_template_kwargs` must be verified against the mlx-community repo's `chat_template` (the Qwen card documents it for Transformers/vLLM); if the template ignores it, Q runs at the card's `xhigh` default and the budget is cut to 1,024 with `thinking` still on, or Q runs non-thinking (0.7/0.8/20/0) as the registered alternative.
- Prompt-cache rebuilds on non-trimmable DeltaNet caches can make a whole-episode re-prefill of 20-40k tokens on Q (60-200 s at 150-200 tok/s): the 450 s active ceiling will be hit; the flag exists, and the rehearsal counts rebuilds.
- Disk: 84.7 + 29.5 GB of new weights against about 58 GB free after pilot 8 and pilot 9's bundles; offloads of pilot roots v5-v8 (`offload.py`, RUN_STATE 1053) must precede R1.
- The window maxima of M2/M3 (about 48,400 s) exceed 44,640 s; a ruling either accepts +1 h or cuts to 16 new members.
- Qwen3.8-Flash-Next is the strongest Qwen that would fit by bytes; dropping it is a runtime-pin consequence and Ed may prefer a pin-bump council first. A pin bump reopens the pinned-stack identity for every ALIGN pilot and for BYTES, so it is a separate decision.

**Open questions for the chair.**
1. Q: 8-bit with the 2,048 budget as primary (this design) or 4-bit from the start for thermal safety?
2. N: Instruct (continuity with pilots 2-3, this design) or Thinking (hidden tokens, like the 30B lineage) as the first Next cell?
3. Accept the +1 h window maximum for the Q windows, or 16 new members?
4. Treat the pilot-8/9 protocol change (gate on) as a new session class for the anchors (it is: A3's +/-6 J test is exactly the question "did the gate move the 30B anchors").

**What Ed must do physically (before M1, once, and then leave alone).**
1. Put the external fan or cooler in place at a fixed setting, lid open, hinge clear, machine flat; do not change it between windows of the series.
2. Charge to 100 % before each arm; keep the 140 W adapter.
3. Fix the room thermostat for the series and write the reading at arm and at the desk (or plug in a USB logger); keep direct sun off the machine.
4. Approve the two downloads (about 115 GB) and the root offloads that make room for them.
5. Decide questions 1-4 above, or let the chair rule.

**Must be verified (listed for the chair, because Sol has no network):** HF file sizes quoted above (84.7 GB, 29.5 GB, 69.6 GB, 44.8 GB); `model_type qwen3_5` for Qwen3.8-27B and mlx-lm 0.31.3 loading it (BYTES BY-EXT-1 says yes; the HF card says mlx-vlm 0.6.8); the `qwen4_exp` requirement of Qwen3.8-Flash-Next; mlx-lm's latest release 0.32.2 (16 Oct) with no Qwen3.8 note; Qwen3.8-27B config (16 full-attention layers, 4 KV heads, head_dim 256, 262,144 ctx, `reasoning_effort` default xhigh); the Qwen3-Next KV allocation of 2 KiB per token per attention layer (repo record).
