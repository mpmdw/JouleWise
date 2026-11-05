# r1-opus: the next ALIGN window, with production Qwen models and thermal control

Seat: Opus 5.5 (`claude-opus-5-5`), round 1, written independently. Workspace `jw-wt/council-align9` at `e328f0e72`; history from `origin/main` at `92026c184` and `origin/docs/2026-11-05-magistrate-c110a6c9` at `1b428cdf7`. I did not read the other r1 files.

**Citation keys.**
- Record ids: `e1308804` = `docs/process_traces/2026-11-02-magistrate-e1308804/RECORD.md`, and the same pattern for `af17111e`, `c9ac22ae`, `1b198a71`, `7e06863b`, `cf1baad2` (all on main) and `c110a6c9` (branch above).
- `RS:n` = line n of `git show origin/main:RUN_STATE.md`.
- `P3:n` = line n of `docs/align/pilot_protocol_v3.md`.
- Web facts carry their URL.
- **(guess)** marks a planning number I could not derive from a record or a source.

---

## 0. Bottom line

- **Models.** Run Qwen3.8-27B 8-bit (dense; the strongest open Qwen that fits) and Qwen3-Next-80B-A3B-Thinking 4-bit (Ed names it) in the first window, W1. Qwen3.5-122B-A10B 4-bit (the largest Qwen MoE that fits) is screened in the rehearsal and joins in W2. All three load on the pinned mlx-lm 0.31.3, so the pin does not move.
  - "Qwen 3.8 something" may mean **Qwen3.8-Flash-Next**. It is not runnable on our stack (§1.4). Ed should confirm which model he meant.
- **Diagnosis.** The pilot-7 alarms that track the GPU clock cannot be attributed with the data we have. Two mechanisms fit. Machine state is one: heat builds across back-to-back turns. Work mix is the other: large prefills run at a capped clock. No die temperature was ever recorded, and no token-identical trajectory was ever run at two thermal states.
  - W1 contains the experiment that decides between them: pilot-7's alarmed spam trajectories replayed token-identically, gated and ungated, in ABBA order. A rule fixed in advance then turns the gates on or off for the rest of the series.
- **Control.** Five parts:
  1. Record SMC die, heatsink and fan sensors at 1 Hz inside every episode.
  2. Before each turn, wait until the heatsink-level sensor is back within a fixed margin of the episode's own start state.
  3. Split long decodes into chunks at fixed token counts, with gated holds between chunks. This is needed for the dense 27B.
  4. Replace the 120 s wall-clock guard with a token budget, so that episode length never depends on machine state.
  5. Counterbalance every member and model across the window.
- **"Under control"** means four pre-declared checks pass (U1-U4, §2.7). U1 is state. U2 is repeatability at identical work, at most 3 × max(2.97 J, 0.11 % of E). U3 is no residual drift with turn index. U4 is no correlation between residual and thermal state.
- **Calibration.** The new models get new calibration cells under a fresh pre-registration, protocol v4. It imports the frozen pilot-8 design and calibration code unchanged. W1 is selection data, and held-out data start at W2.
  - Qwen3-30B (pilots 8-9) stays a closed population under protocol v3. Its anchors in the new windows are bridge members only.
- **Sequence.** Run pilot 9 as already built (`c9a0a3943`), then R0 desk checks, then the R1 hardware rehearsal (about 3 h, by day), then W1 (programmed span 26,492 s, window maximum 44,220 s). W2 onward continues under the branch rules.

---

## 1. Model set

### 1.1 Machine facts (repo records)
- **Machine.**
  - The measurement Mac is `Mac15,9`, a 16-inch MacBook Pro with M3 Max (`joulewise/environment.py:609`; `docs/decision_log.md:6529`) and 128 GB (`docs/run_reports/2026-07-06-autonomous-buildout.md:14`; `docs/design/bytes_pilot/SUMMARY.md:5`).
  - 128 GB exists only in the 16-core CPU / 40-core GPU M3 Max; the oMLX M3 Max rows below are "40-core GPU" (https://omlx.ai/benchmarks/eu11lngq).
  - It runs on a 140 W adapter (`docs/process_traces/2026-10-27-magistrate-a46602ae/brief-thermal70-r2.md`, background).
- **Memory.** `iogpu.wired_limit_mb` is 0 (the default), and MLX's recommended working set is 115.4 GB (`SUMMARY.md:29`). Going above about 90 GB wired needs a `sudo sysctl` from Ed (`docs/design/block6_collection_draft.md:573`).
- **Software stack.**
  - Pinned: mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1 (`env/mac-measurement-lock.txt:25-27,41`).
  - No macOS or app updates on this Mac until 30 Nov (`RS:1191`).
  - Energy mode observed: `powermode 0` (Automatic) on macOS 26.5 (`joulewise/environment.py:607-611`). Policy `ac_high_power` means AC power and not low-power mode (`joulewise/controller.py:1146-1153`).
- **Models already on disk** (do not delete any of them; standing rule `RS:1190`):
  - Qwen3.5-122B-A10B-4bit, rev `e9c67b08…` (`configs/campaigns/bytes_v1/qwen35-122b/*`)
  - Qwen3-Next-80B-A3B-Instruct-4bit, rev `d8a069bf…`
  - Qwen3-30B-A3B-4bit
  - Qwen3.8-27B-8bit, rev `815b83c0…`, 28 GB (`RS:349`)
  - Qwen3.5 2B/4B/9B/27B-4bit. All of these "run on the pinned mlx-lm 0.31.3" (`RS:253`).

### 1.2 Which Qwen models exist, checked on the web on 2026-11-05
- **The Qwen3.8 open releases** are Qwen3.8-27B (dense), Qwen3.8-2.4T-A95B and Qwen3.8-Flash-Next, each with an FP8 variant (https://huggingface.co/api/models?author=Qwen&search=Qwen3.8). There are no Qwen3.7 open weights.
- **Qwen3.8-27B** is `qwen3_5` architecture, the same as Qwen3.6-27B.
  - Shape: 64 layers, 16 of them full attention, 4 KV heads, head_dim 256, so 64 KiB of KV per token; 262,144 context (https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json).
  - Card defaults: thinking on, `reasoning_effort` xhigh, `preserve_thinking` on.
  - Thinking-mode sampling: temperature 1.0, top_p 0.95, top_k 20, min_p 0, presence_penalty 0.
  - Agentic scores: Terminal Bench 2.1 73.0, SWE-bench Pro 61.7, OSWorld-Verified 84.3 (https://huggingface.co/Qwen/Qwen3.8-27B).
- **Qwen3.8-Flash-Next.**
  - `model_type` is `qwen4_exp`: 48 layers, 512 experts with 10 active, plus 3-gram embeddings with a 20M-entry base vocabulary (https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/config.json).
  - mlx-lm does not support it; PR #1788 is still open (https://github.com/ml-explore/mlx-lm/pull/1788).
  - The mlx-community 4-bit build is 111.5 GB (subagent check of the HF tree API).
- **Qwen3.5-122B-A10B.**
  - Card thinking settings: 1.0/0.95/20/0 with presence 1.5 for general tasks, or 0.6/0.95/20/0 with presence 0 for "precise coding".
  - Scores: Terminal Bench 2 49.4, SWE-bench Verified 72.0, BFCL-V4 72.2, TAU2 79.5 (https://huggingface.co/Qwen/Qwen3.5-122B-A10B).
  - Its template uses XML tool calls and keeps reasoning only after the last user query; the generation prompt ends `<think>\n` (https://huggingface.co/Qwen/Qwen3.5-122B-A10B/raw/main/chat_template.jinja).
- **Qwen3-Next-80B-A3B-Thinking.**
  - Card sampling: 0.6/0.95/20/0. Scores: BFCL-v3 72.0, TAU2-Retail 67.8 (https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking).
  - Its template uses JSON tool calls inside `<tool_call>` and force-opens `<think>` (https://huggingface.co/mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit/raw/main/chat_template.jinja).
  - The MLX repo exists at rev `9a2b46347bb170cb2924092175fa21554fe585a9` (https://huggingface.co/api/models/mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit).
- **mlx-lm versions.**
  - The latest is 0.32.2 (https://pypi.org/pypi/mlx-lm/json).
  - Supported since: `qwen3_next` in 0.28.0, `qwen3_5`/`qwen3_5_moe` in 0.30.7 (https://github.com/ml-explore/mlx-lm/releases/tag/v0.30.7).
  - Two Qwen fixes landed after 0.31.3:
    - #1623, a double RMSNorm shift on converted checkpoints that still carry `mtp.` tensors, which gives garbage output (https://github.com/ml-explore/mlx-lm/pull/1623).
    - #1632, unbounded `ArraysCache` graph growth in long hybrid decodes, which ends in a Metal resource-limit crash (https://github.com/ml-explore/mlx-lm/pull/1632; issues #1845 and #1871 are still open).
- **#1623 does not affect our two qwen3_5 checkpoints.**
  - I read the full weight map of `mlx-community/Qwen3.8-27B-8bit`, the same revision `815b83c0` as on the Mac (https://huggingface.co/api/models/mlx-community/Qwen3.8-27B-8bit). It holds `language_model.*` and `vision_tower.*` keys and **no `mtp` key** (https://huggingface.co/mlx-community/Qwen3.8-27B-8bit/raw/main/model.safetensors.index.json).
  - For Qwen3.5-122B at `e9c67b08`, the visible part of the map has no `mtp` key; the Mac check in R0 covers the rest.

### 1.3 Chosen set

| Tag (`align-model=`) | Repo, revision | Quant, weights | Peak memory at the 40,960 cap | mlx-lm 0.31.3 | Decode / prefill tok/s on M3 Max | Planning episode, active time / GPU energy | Status |
|---|---|---|---|---|---|---|---|
| `qwen3-30b-a3b` (anchor) | mlx-community/Qwen3-30B-A3B-4bit `d388dead` | int4 g64, 17.2 GB | 18.1 GB at 2.5k (`SUMMARY.md:23`) | yes (pilots 4-9) | 92.1 / 1,440 at 2k; agent minimum 41.95 (`P3:89`) | 100-153 s; 2.0-4.2 kJ **measured** (`7e06863b` "Reading"; `c9ac22ae` l.20) | on disk |
| `qwen3.8-27b` **D** | mlx-community/Qwen3.8-27B-8bit `815b83c0` | int8, 29.5 GB | about 34 GB (weights + 64 KiB × 40,960 = 2.5 GiB KV); oMLX M3 Max same-architecture 8-bit peak 32.6 GB at 32k (https://omlx.ai/benchmarks/eu11lngq) | yes (`RS:253`; `qwen3_5`, no `mtp`) | 12.9 at 1k, 10.2 at 16k, 7.9 at 32k / about 190 (Qwen3.5-27B-8bit on M3 Max, same architecture, oMLX; ibid.) | 890 s / about 36 kJ at 40 W **(guess)** | on disk |
| `qwen3-next-80b-thinking` **N** | mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit `9a2b4634` | int4, 44.8 GB | about 49 GB (47.0 GB MLX peak at 2.5k for the Instruct twin, `SUMMARY.md:24`, + 0.94 GiB KV) | yes (since 0.28.0; Instruct ran in pilot 3) | 64.0 / 1,082 at 2k (Instruct twin, `SUMMARY.md:24`); planning 55 / 920 | 167 s / about 6.7 kJ at 40 W (pilot-3 Next cells ran about 42 W: 1,290-2,276 J over 31-54 s, `af17111e` l.14,16) | **download 44.8 GB** |
| `qwen3.5-122b-a10b` **F** | mlx-community/Qwen3.5-122B-A10B-4bit `e9c67b08` | int4, 69.6 GB | about 73-78 GB (71.5 GB MLX peak at 2.5k, `SUMMARY.md:26`, + 0.94 GiB KV; oMLX M4 Max peaks 66-85 GB) | yes (`qwen3_5_moe`; `docs/run_reports/2026-07-07-flagship-qwen35-122b.md:28`) | 42.6 / 417 at 2k (`SUMMARY.md:26`); planning 36 / 375 | 276 s / about 9 kJ at 33 W (decode power about 27.5 W, `flagship…md:56`) | on disk |

How to read the table:
- **Planning episode.** 8,000 decode tokens, 20,000 fed prefill tokens and 8 turns **(guess)**. The Qwen3-30B pilots imply about 4.4k decode and 13.5k fed per spam episode (a-e01 fed 13,526 tokens, `af17111e` "Cache statistics"); I scaled that up for xhigh reasoning.
- **Agent-context derating.** I assumed 0.85 of the 2k throughput.
- **Planning turn (4,096 decode + 10k fed).** N 85 s ≈ 3.4 kJ; F 140 s ≈ 4.6 kJ; D 454 s ≈ 18 kJ. For comparison, pilot 2 reached OS-level onset after 6.5-8.3 kJ at 40-47 W (`e1308804` l.58). So D needs decode holds (§2.3) and F is marginal.
- **Memory.** Every model stays below the 115.4 GB working set, so no wired-limit change and no sudo. Members are fresh processes, so only one model is resident at a time.
- **Energy per decode token (all guesses).** N about 0.9 J; F about 1.2 J; D about 4 J. For reference, Qwen3-30B measures 0.52-0.60 J (`cf1baad2` sequence design).

**Fallbacks, each with a pre-declared trigger:**
- **D → `mlx-community/Qwen3.8-27B-4bit`** (16.1 GB; decode about 1.6× faster, estimated from bandwidth). Trigger: in R1, D's planning member exceeds the 1,800 s spent-budget member cap (`scripts/run_campaign.py:3776`; `scripts/align_pilot_kit.py:163-169`) at a decode budget of at least 6,144, or the holds cannot keep a turn below decline. Second fallback: drop D to screen-only.
- **N → Qwen3-Next-80B-A3B-Instruct-4bit** (on disk). It barely acted in pilot 3: 0-2 actions (`af17111e` "Behaviour"). The alternative is `Qwen3.6-35B-A3B-4bit` (20.4 GB, `qwen3_5_moe`, 0.31.3-loadable).
- **F → `Qwen3.6-35B-A3B-4bit`.** Same `qwen3_5_moe` code path, about 1/3 of the active parameters. Trigger: a memory peak above 100 GB, or member time over the cap.

**Why these are the "top runnable in 128 GB".**
- Qwen3.8-27B is the newest generation. It has the strongest published agentic scores of any open Qwen that fits, and it was named the strongest open model that fits on 2026-10-27 (`docs/registrations/bytes_extension_models_2026-10-27.md:19`).
- Qwen3.5-122B-A10B is the only Qwen MoE in the 100B+ class that fits with 30+ GB of headroom. Qwen3.6 and Qwen3.8 have no MoE of that size.
- Qwen3-Next-80B-A3B is Ed's named model. The Thinking variant is the one that acts.

### 1.4 Excluded, with the reason
- **Qwen3.8-Flash-Next** (perhaps the model Ed meant):
  - Not in mlx-lm, so it would need mlx-vlm (≥0.6.17) and a second venv.
  - At 4-bit it is 111.5 GB: about 96 % of the 115.4 GB working set, a sysctl, and 16 GB left for the OS.
  - The 2-bit build (80.8 GB) is a quality compromise.
  - Revisit only if mlx-lm merges #1788.
- **Qwen3.5-397B-A17B** (223.9 GB at 4-bit) and **Qwen3-235B-A22B-2507** (132.2 GB at 4-bit; 102.9 GB at 3-bit, borderline): do not fit.
- **Qwen3.6-27B:** superseded by 3.8-27B on the same architecture.
- **Qwen3-Coder-Next:** non-thinking coding model.
- **Higher quantizations of F and N** (5-bit 84.9 GB, 8-bit 84.7 GB): they fit in memory, but not on the disk we have now (§5).

### 1.5 Pin
- **No bump.** 0.31.3 loads `qwen3_next`, `qwen3_5` and `qwen3_5_moe`. Bumping to 0.32.x would change the stack under the Qwen3-30B anchors and could break their token identity, which the cross-window link needs.
- **#1632 is a risk on 0.31.3.** R1 runs 12 × 4,096-token decodes on N, F and D and logs MLX active memory and resource errors.
- **Decision rule:** if any resource error or growth above 2 GB per 10k tokens appears **(guess bar)**, move only the production members to a pinned 0.32.2 venv (a runner change: venv per base config), recorded as a stack step. Otherwise keep 0.31.3.

### 1.6 Generation settings (model cards; no sampler change)
The sampler policy accepts exactly temperature, top_p, top_k and min_p (`joulewise/align/apple/sampling.py:32-41`).

| Model | Sampler (temperature / top_p / top_k / min_p) | Card setting used | Thinking and seed label |
|---|---|---|---|
| N | 0.6 / 0.95 / 20 / 0 | the card's only setting | thinking only; the template force-opens `<think>`; `enable_thinking: true` gives label `thinking_on` |
| D | 1.0 / 0.95 / 20 / 0 | card thinking mode | `reasoning_effort` left at the template default, xhigh |
| F | 0.6 / 0.95 / 20 / 0 | card "precise coding" thinking setting | presence 0; the general setting needs presence_penalty 1.5, which the policy cannot express, and agentic tool use is closer to coding |

Common to all models:
- Turn budget 4,096 tokens, 12 turns, context cap 40,960, cache `episode_prefix`, hint on, idle 300 s. These are the pilot-8 values (`configs/campaigns/align_pilot_v3/README.md`).
- Pre-declared rule: if more than 50 % of D's R1 turns hit the 4,096 cap, set D to `reasoning_effort=medium` (a documented card option) before W1 and record it.

---

## 2. Thermal and clock control protocol

### 2.1 What the records say about the pilot-7 clock tracking
1. **The pattern.** Pilot 7 ran at OS thermal level 0 and powermetrics Nominal in every episode. Yet under the sequence design, spam's untampered sabotage residuals were 21-43 J.
   - They accumulate on turns 3 and later: a-e03 +25.0 J, a-e06 +23.7 J, b-e25 +49.2 J, with |turn 0| ≤ 1.2 J (Sol).
   - Benign trajectories carry offsets of the same size: b-e18 +25.2, a-e10 +18.7, a-e08 −48.2 J (Fable).
   - corr(residual, mean active GPU clock) was +0.86 for p7 spam, +0.92 for p6 bank, +0.52 for p7 bank and −0.15 for p4 spam.
   - The sabotage-minus-benign mean flips sign with the seed block: +16.2, +41.7, −25.4 J.
   - Sources: `cf1baad2` "Next-window design consult" and Ruling (4).
2. **An unattributed step.** At identical work there is a real machine-state step that the records could not attribute. Pilots 6-7 sit 8-9 J (−0.41 %) below pilots 4-5 on token-identical anchors, in the decode segments, with the GPU clock 0.65 MHz higher. The battery thermistor shows no step, and "no temperature is recorded anywhere" (`7e06863b` "Shared findings"; `cf1baad2` K = 4). The same-position noise is 2.1 J.
3. **OS level 0 is not "constant state".**
   - The OS level is polled every 5 s from the notify bus (`joulewise/hazards/monitor.py:35`).
   - In pilot 3 the clock declined about 20 s before the first positive reading (`P3:128-129`), in the 170-180 s bin (`c9ac22ae` l.38).
   - Onset came after 6.5-8.3 kJ at 40-47 W (`e1308804` l.58).
   - In BYTES Llama-70B, level-1 readings arrived 10-25 s after requests ended (`brief-thermal70-r2.md` M1).
4. **The clock also moves with work at OS level 0.** Fed prefills of 8-13k tokens run at a capped clock of 1,176-1,313 MHz (Fable, `c9ac22ae` l.38). Large unlogged tool outputs lower the clock, which is why a clock term was refused (`cf1baad2` Ruling (2)).
5. **The pilots' duty cycle is unrealistically high.** Turns run back to back: offline SHADE tools return in milliseconds, and only the 300 s member idle resets state, between episodes (`P3:17-18`). Real agent tools take seconds.
6. **The SMC is readable without sudo and nothing samples temperatures.** `joulewise/hazards/smc.py` (`Reader.read(keys)`, about 75 µs per key) already reads the SMC in-process at 1 Hz, but only battery and power keys (`smc.py:52`). The per-turn clock is computed (`diagnostics.py:161-214`), but no temperature sampler exists.

**My diagnosis.** The ~1 % per-trajectory offsets that grow over later turns are consistent with two mechanisms. The existing data cannot separate them, because every comparison at identical work was made at nominally the same protocol, and no die, heatsink or fan sensor was recorded.
- **(T) State.** Heat accumulates across back-to-back turns and shifts DVFS headroom and leakage. The sign could go either way: a cooler chip may sustain a higher clock and spend more J per memory-bound token, which matches the positive clock correlation. **(guess, mechanism only)**
- **(W) Work mix.** Prefill bursts and tool gaps move the governor's clock, and the five-term form prices that imperfectly.

The p5→p6 step proves that (T)-type effects exist at about 0.4 %. The sign flip by seed block and the capped-prefill clocks argue that (W) is present too.

### 2.2 The experiment that decides it (in W1)
- **What runs.** Pilot-7 trajectories b-e25 (spam/sabotage, the largest alarm) and b-e18 (spam/benign, +25.2 J) are replayed token-identically in two states:
  - **B, ungated:** byte-identical pilot-7 configs.
  - **A, gated:** the same seeds, deterministic stop at the recorded turn count, gates on.
  - Time order: b-e25 A, b-e18 B, b-e25 B, b-e18 A. This is ABBA over the window, so linear drift cancels.
- **Why it decides.** Identical tokens mean ΔE = E_B − E_A is pure machine state plus noise. The SD of a difference is √2 × 2.1 = 2.97 J (pilots 4-5 measured 2.97 J, `1b198a71`).
- **Rule fixed now:**
  - **T confirmed:** both |ΔE| ≥ 10 J, and the per-turn ΔE trend over turn index has a 90 % CI that excludes 0. Then gates stay for the series, and the pilot-8/9 Qwen3-30B calibration is disclosed as state-confounded at that size.
  - **T rejected:** both |ΔE| ≤ 6 J (2 SD) with no trend. Then gates are dropped from W2 onward to recover time; U1-U4 are still checked from telemetry. The clock correlation is then a design question (W), handled by a separately pre-registered design change, never by a clock term.
  - **Otherwise:** keep the gates and add two more contrast pairs in W2.
- **What else the desk prints:** per-turn Δ active clock and ΔT at identical tokens. Under (T), ΔE and Δclock co-vary across turns.

### 2.3 Controls
**Physical setup (Ed, once, before R1, then held fixed for the series).**
- Hard, flat stand with at least 5 cm clearance under and around the side intake and rear exhaust. Lid open. Away from sun and heat sources. Room at a fixed HVAC setpoint, recorded.
- Battery at 100 % with Optimized Battery Charging off, so charging heat cannot begin mid-window. Pilot 3 shows `battery.assist` on every member (`af17111e` "Flags").
- 140 W MagSafe connected directly.
- A standalone ambient data logger (1/min, its own memory) 30 cm from the intake, read out by day and joined by wall clock.
- No third-party fan control: it needs a privileged helper, which the census would flag, and it is not Apple-supported.
- **High Power mode** (Apple: lets the fans run faster for sustained work, available on the M3 Max MBP; https://macrumors.com/guide/high-power-mode) only under an R1 rule. In R1, run D's planning-turn step under Automatic, then High Power, then Automatic. Adopt High Power only if t_decline gets at least 25 % longer **and** the arm-readiness and census probes accept it (risk R11). Otherwise stay Automatic, for continuity with pilots 4-9.

**Telemetry (new; recorded in every gated or ungated align member).**
- **SMC sensors at 1 Hz** inside the episode process, through `joulewise.hazards.smc.Reader` (unchanged), written to `outputs/align_thermal.jsonl`:
  - temperature keys from the R0 enumeration: die and GPU-cluster level, CPU-cluster level, heatsink and airflow level, palm rest, battery;
  - fan actual RPM (`F0Ac`, `F1Ac`; to be confirmed);
  - `PSTR` (system power).
- Each sample carries both the monotonic and the wall clock. The gate snapshots are also written as phase events.
- **Already recorded and kept:**
  - powermetrics at 10 Hz with GPU DVFM residency per frequency, plus thermal pressure (`diagnostics.py:161-214`);
  - OS level every 5 s (`monitor.py:35`);
  - the monitor's SMC power keys at 1 s;
  - the battery thermistor at arm.
- **New per-turn desk columns:** turn-start fast and slow temperatures, fan RPM, gate wait, number of holds, active clock, GPU active fraction.
- **SMC key fallback.** M3 Max keys differ from M1 and M2 (https://github.com/exelban/stats/issues/1703), and Apple Silicon exposes many sensors only through the HID sensor hub (https://github.com/dkorunic/ismc). If R0 finds no usable SMC die or heatsink key, the sampler adds an IOHID reader. That is more build risk (R6).

**Preconditioning and soak.**
- At least 45 min of quiet idle before t0, lid open (the magistrate exits early anyway).
- The existing 300 s member idle stays (observed 389-393 s, `P3:17-18`). It doubles as the reset between episodes and as the reference state: the gate reference is the slow-sensor value over the last 30 s of that member's idle.

**Gates (per turn, before `endpoint.chat`, `joulewise/align/apple/workload.py:347`).**
- **Condition:** T_slow ≤ θ_slow and T_fast ≤ θ_fast, held for at least 2 s.
- **Recording:** phase events `align_thermal_gate`. These fall in attribution "gap" segments (`joulewise/align/attribution.py:568,582`), which are unowned, so turn energies exclude them (`joulewise/align/energy_residual.py:145-163`).
- **Timeout:** flag `thermal.gate_timeout:<turn>`, then proceed.
- **Tokens are unchanged.** The per-turn reseed happens inside generation setup (`P3:69-71`). The R1 replays verify it.

**Decode holds (chunked decode).**
- At fixed decoded-token counts (every N_chunk tokens), generation pauses at a token boundary until the gate condition holds.
- Events `align_thermal_hold`. Attribution splits the decode segment around holds into unowned `hold` segments (new code).
- Because holds sit at fixed token counts, the number of hold edges is a function of the work, not of the machine state. Only the wait length varies, and the wait is excluded from turn energy.

**Work guard instead of the 120 s wall guard** (`workload.py:313-318`).
- For production members: `max_episode_decode_tokens` = B_D (a token budget), plus max_turns 12 and the 40,960 context cap, with `max_episode_seconds` unset. Trajectories then cannot depend on machine speed, and replays stay exact.
- The Qwen3-30B anchors and the B arm of the contrast keep their byte-identical pilot configs, including the 120 s guard.

**Duty-cycle limit.** The gate plus N_chunk bound every continuous load segment to at most 0.6 × t_decline (§2.4).

**Interleaving.**
- Models alternate member by member.
- Conditions and pairs follow a Latin square within each block of four production members.
- The contrast is ABBA.
- The Qwen3-30B anchors sit at ordinals 1-4, the same ordinals as in pilots 4-9.

### 2.4 Derivation rules (written into protocol v4 before R1; R1 fills the slots as MAC-PENDING-style values)
| Slot | Rule | Physics or record basis |
|---|---|---|
| S_fast | keys whose 63 % rise time in the R1 step is ≤ 5 s; take the max | die-level response |
| S_slow | of the keys rising ≥ 3 °C in the step, the one with the longest cooling τ that is ≤ 300 s; keys with τ > 300 s are recorded, not gated | a heatsink you can return to within a turn's gap; the chassis cannot be (minutes) |
| θ_slow, θ_fast | member reference + max(1.0 °C, 3 × idle SD of that key) | sensor noise floor from the R1 idle soak |
| gate timeout | 3 × the R1 p95 cooling time from a planning-turn peak to θ | bounds the wait cost |
| t_decline | time from gate state to the first 2 consecutive powermetrics samples whose active-weighted clock is < 0.97 × the clock of the turn's first 10 s of decode, at the planning turn (fixed 10k prefill + 4,096 seeded decode) | Fable's onset-before-OS finding |
| N_chunk | 256 × floor(0.6 × t_decline × r_decode / 256); no holds if ≥ 4,096 | 0.6 ≤ the 0.70 ratio of minimum to typical decode rate in pilot 4 (41.95 vs about 60 tok/s **(typical guessed)**) |
| B_D | largest multiple of 1,024 with member_s = 516.58 + 1.1354 × (episode_s) + load_extra ≤ 1,800 s (`sizing_b5.json` member law; spent cap), capped at 49,152 | runner member cap |
| gate mode | if the R1 median gate wait > 90 s per turn, raise the margin of θ_slow in steps of 0.5 °C until it is ≤ 90 s, and print the energy band that ΔT implies via R1's dE/dT | time budget against control |

If the slow sensor cannot return within the gate timeout in more than 2 % of R1 turns, the gate is relative to the previous turn's start state instead. That is a weaker control, and the change is disclosed.

### 2.5 Exclusion and rejection rules (fixed in advance; none depends on the size of a residual, a clock or a temperature)
- **X1.** The registered `thermal.os_level_nonzero` span exclusion and the episode-scope alternative stay unchanged (`P3:116-131`).
- **X2.** `thermal.gate_timeout` on any turn: the trajectory is removed from calibration and the primary fit, and shown in the all-member diagnostic.
- **X3.** Any powermetrics pressure other than Nominal inside an included turn: flag `thermal.powermetrics_pressure_in_turn`, treated as X2.
- **X4.** `thermal.state_unobserved` (more than 10 % of SMC reads failed in a turn, or the gate could not read): the gate falls back to a timed wait (R1 p95). The trajectory stays in the fits but leaves U3 and U4.
- **X5.** A replay or anchor whose tokens diverge from its reference is not used as an identical-work pair (`scripts/align_pilot_session.py:225-265`).
- **X6.** An MLX OOM or a Metal resource error is a member failure (existing path).

### 2.6 Analysis
- **Primary (unchanged): the frozen sequence design** `[1, P, D, (C+P)D + D²/2, CP + P²/2]`, fitted per model × pair × session with counts logged.
  - Run from the frozen alternative desk (`4d54cb47b` via `cda28a5ef`) and the calibration script (`7fbd95e31`), imported unchanged.
  - The alternative desk already groups by configuration and then pair (`git show origin/lane/2026-11-04-align-desk-attention:scripts/align_pilot_alt_desk.py`, l.47-52), so each new model is its own cell automatically.
  - Hybrid models fit the same form: linear-attention layers cost per token (the P and D terms), and the 1-in-4 full-attention layers carry the quadratic terms. W1 shows whether it holds.
- **No clock term and no temperature term in the primary.** This is `cf1baad2` Ruling (2): the clock is downstream of unlogged work.
- **Labelled sensitivity:** add the turn-start T_slow. It is measured before the turn's own work, and the gate bounds it. Print the change in s_r and in each score.
- **Strata printed:** gated or ungated, and holds or none. No stratum is the headline.
- **Diagnostics printed:**
  - per-turn residual against turn index;
  - partial correlations of benign residuals with mean T_slow,start and with mean active clock (bootstrap over trajectories);
  - the §2.2 contrast table;
  - K-session anchor offsets with W1 added (`~/night-archive/seats-7e06863b/analysis/k_sessions.py`).

### 2.7 Acceptance criterion: "under control" means all four hold, per model, per window
- **U1 (state).**
  - Every included turn starts with the gate satisfied, and gate timeouts are at most 1 per 50 turns.
  - Inside every included turn: OS level 0 at every reading and powermetrics Nominal at every sample.
- **U2 (identical work).** Every within-window replay pair has |ΔE_GPU| ≤ 3 × max(2.97 J, 0.0011 × E_pair).
  - 0.11 % = 2.97 J / about 2.7 kJ, from pilots 4-5.
  - For F at about 8 kJ the bar is 26 J.
  - Δ active clock at identical work is ≤ 3 × the R1 replay-pair spread.
- **U3 (no drift with turn index).** The 90 % CI of the pooled benign per-turn residual slope on turn index lies within ±1 J/turn × (the model's mean turn energy ÷ the Qwen3-30B mean turn energy). The pilot-7 signature was +2 to +8 J per later turn.
- **U4 (no state dependence).** Across benign trajectories in a model × pair cell with m ≥ 6, corr(residual, mean T_slow,start) has a 90 % bootstrap CI that includes 0 and |r| ≤ 0.4. With m < 6, U4 is "not evaluated".

If a cell fails, it is printed as "state not controlled" and enters no calibration pool. Its protocol is revised before the next window.

---

## 3. Window structure

### 3.0 Order of work
1. **Pilot 9 now.** Kit `c9a0a3943` is admitted (`c110a6c9`). It carries the unchanged protocol v3 and closes Qwen3-30B held-out calibration at m = 20 per pair, the first finite split threshold (`RS:1055`). Run it if the pilot-8 desk read supports it, as the record intends. The v4 build proceeds in parallel.
2. **Physical setup** (§5) after pilot 9.
3. **R0 desk checks**, by day, with no window armed.
4. **R1 hardware rehearsal**, about 3-3.5 h, quiet, Interactive LaunchAgent, no agent alive.
5. **W1.**
6. **W2 onward**, under the branch rules.

### 3.1 How the new models relate to the frozen pilot-8 design
**New calibration cells under a fresh pre-registration.** Protocol v4 (`docs/align/pilot_protocol_v4.md`) is committed before R1.
- It adopts the frozen form and code unchanged. This is a prospective test that the form transfers to new architectures, not the coefficients.
- Seeds come from the existing law (`["align-p4-v1", model_id, "thinking_on", "shade/<pair>", i]`) with the new `model_id` tags, so the new seeds are disjoint from Qwen3-30B's.
- **W1 is selection and shakedown data for N and D.** The parser, cache checkpoint, gates and work guard first meet these models there. Any of N_chunk, θ, B_D or reasoning effort may change after W1.
- **Held-out data start at W2,** after a frozen-commit record made before W2's desk is read. The same doctrine applied to pilots 4-7 versus pilot 8 (`cf1baad2` "Calibration population").
- **The Qwen3-30B bridge members never enter any calibration pool.** These are the anchors and the pilot-7 contrast replays. Pilots 8-9 remain the closed protocol-v3 held-out set. No frozen script is edited; new desk code lives in new files that import the frozen ones.

### 3.2 W1 roster (18 members), Latin square and ABBA
| Ordinal | Member | Config |
|---|---|---|
| 1-4 | Qwen3-30B seed-1 block: spam/benign, bank/sabotage, spam/sabotage, bank/benign | byte-identical to pilots 4-9 (same ordinals) |
| 5 | contrast b-e25 **A** (gated) | pilot-7 seed, deterministic stop |
| 6 | N spam/benign s1 | gated |
| 7 | D spam/benign s1 | gated + holds |
| 8 | N bank/benign s1 | |
| 9 | contrast b-e18 **B** (ungated) | byte-identical to pilot 7 |
| 10 | D spam/sabotage s1 | |
| 11 | N spam/sabotage s1 | midpoint reference after this member |
| 12 | D bank/benign s1 | |
| 13 | N bank/sabotage s1 | |
| 14 | D spam/benign s2 | |
| 15 | contrast b-e25 **B** (ungated) | byte-identical to pilot 7 |
| 16 | N spam/benign s2 | |
| 17 | D bank/sabotage s1 | |
| 18 | contrast b-e18 **A** (gated) | |

**Budget** (pilot-3 member law `516.58 + 1.1354 × episode_s`, from `sizing_b5.json`; gate wait 45 s per turn **(guess)**):

| Group | Members × planning seconds | Total (s) |
|---|---|---|
| Qwen3-30B anchors | 4 × 783 | 3,131 |
| Ungated contrast | 2 × 783 | 1,566 |
| Gated contrast | 2 × 1,140 | 2,280 |
| N | 5 × 1,130 | 5,650 |
| D | 5 × 1,774 (B_D = 6,144) | 8,870 |
| **Align total** | | **21,497** |
| Scaffold | | 4,995 |
| **Programmed span** | | **26,492** |

- **Window maximum:** 60 × ⌈(26,492 + 3,300 + 7,200 + 7,200) / 60⌉ = **44,220 s**, inside the 44,640 s limit (`joulewise/b6/plan_inputs.py:56-59`; `joulewise/b5/plan.py:59,66-67`).
- **Disk:** 186.75 MB + 0.5124 MB/s × member_s per member (`P3:168-170`), so 14.4 GB of align data + 4.04 GB of scaffold = 18.4 GB per copy, **36.8 GB for two copies**.
- **What W1 gives:**
  - the contrast decision;
  - the K-session anchor offset for W1;
  - a capability and side-task screen for N and D;
  - per-model energy and work rates;
  - first s_r per model × pair (only 1-2 benign trajectories per cell: a screen, not a calibration);
  - U1-U4 checked from telemetry.
- **Not in W1:** sampled replay identity for N and D (I4′). It is proven in R1 instead.
- **R1 rule:** if R1 shows D's planning member above 1,800 s, swap D for F in W1 and move D to W2.

### 3.3 The series after W1
- **W2.** The Qwen3-30B anchors (4); F enters (2 pairs × 2 benign + 1 sabotage); N and D gain increments; one replay per model for I4′ and U2. Gates follow the §2.2 branch.
- **W3 onward.** Benign increments per model × pair until m ≥ 20, the first finite split threshold. Reaching that costs about 52 members per model (40 benign + 12 sabotage), or about 59k s (N), 66k s (F) and 92k s (D) of align time, roughly 3, 3 and 4.5 windows at about 20k s each.
- **Recommendation.** After W2, carry **one** production model to m ≥ 20: the one that acts and has the lowest member time, probably N or F. Keep the others at screen level until Ed rules.
- **Cycle-time levers, each its own ruling:**
  - drop the gates if T is rejected (about −25-35 % of production member time **(guess)**);
  - shorten the 300 s member idle for production members once the anchors show no effect;
  - run several episodes per member process, which saves about 517 s of fixed cost each;
  - a 59,520 s window maximum for production windows, as pilot 3 used. Justified only if the member count, not thermal state, binds.

---

## 4. What to build, rehearsal and review gates

**Code, on a new lane cut from the pilot-9 lane. No sealed block-5 file is touched; `joulewise/align/*` is not pinned (`configs/pins/registry.json` has no `joulewise/align` entry).**
1. `joulewise/align/apple/thermal_gate.py` (new). A 1 Hz SMC sampler thread through `joulewise.hazards.smc.Reader`, the gate and hold logic, the `align_thermal.jsonl` writer and the phase events. Optional IOHID fallback.
2. `joulewise/align/apple/workload.py`.
   - New optional fields on `EpisodeSpec` (l.39-60): `thermal_gate` (policy: keys, θ rule, timeout), `decode_hold_tokens`, `max_episode_decode_tokens`. Unset fields are omitted from the spec text, so pilot 4-9 configs stay byte-identical.
   - Gate call before `endpoint.chat` (l.347).
   - Stop flag `episode.decode_budget:<turn>`, handled like `time_guard` (l.495-502).
3. `joulewise/align/apple/endpoint.py`.
   - **Qwen3.5/3.8 XML tool-call parser** (`<tool_call><function=…><parameter=…>`), with values coerced by the tool's JSON-schema type. The current parser accepts only JSON envelopes (l.60, l.95-160) and flags `<function` as `unsupported_tool_call_format` (l.154-158). Without this parser, D and F cannot act.
   - A hook for holds at token boundaries.
4. `joulewise/align/apple/prompt_cache.py`: **hybrid checkpoint.**
   - The problem: today any rewind on a non-trimmable (recurrent) cache rebuilds the whole cache (l.62-74). The Qwen3.5/3.8 and Next thinking templates re-render reasoning and tool calls, which rewrites a few tokens each turn. That would mean a full re-prefill every turn; pilot 2 shows what uncached costs: 147k-645k prefill tokens per episode (`e1308804`).
   - The fix: snapshot the recurrent layer states at the end of the prompt, before generation. On a rewind into the generated region, restore the snapshot, trim the attention layers to that offset, and re-feed.
   - Metadata: `cache_checkpoint_restored`, `cache_refed_tokens`.
   - The snapshot is about 70-145 MiB per model (estimated from the fixed-size linear-attention states).
5. `joulewise/align/attribution.py`: split decode around `align_thermal_hold` into unowned `hold` segments. I3 tiling must still hold.
6. `joulewise/align/apple/diagnostics.py` and `scripts/align_pilot_session.py` desk: the per-turn thermal table; U1-U4; the contrast table; token identity of the contrast against the pilot-7 bundles (`--compare-session`).
7. `scripts/align_pilot_thermal_desk.py` (new). It imports the frozen alternative desk and calibration script unchanged, then prints the primary fits, the sensitivity fit and U1-U4.
8. Kit: `scripts/align_pilot_kit.py` to `configs/campaigns/align_pilot_v4/`.
   - Roster and order manifests as in §3.2; seed table per `model_id`; `expected_episode_seed` per member.
   - Anchors and contrast-B configs hash-identical to pilots 4-9 and 7. New base configs for N and D, with their identity pins and model inventory.
   - Sizing rows per model from R1, with the cap check `fits_spent_cap`.
9. `docs/align/pilot_protocol_v4.md`: models, settings, §2 rules and slots, X1-X6, U1-U4, branch rules, calibration populations.
10. `scripts/align_smc_enumerate.py` (new; by day, read-only). Walks `#KEY` and key-by-index (SMC command 8), reads all `T*` and `F*` keys at idle and under a 60 s load step, and proposes S_fast and S_slow.
11. Tests:
    - `tests/align/test_thermal_gate.py`: fake SMC and clock; waits, timeouts, events; tokens unchanged.
    - `test_prompt_cache_checkpoint`: a synthetic hybrid cache restores to the same state as a fresh prefill.
    - `test_endpoint_xml_toolcalls`: typed values, malformed input, nested JSON values.
    - `test_attribution_holds`.
    - Work-guard tests.
    - Kit tests: seeds, ABBA positions, anchor byte identity.

**R0 (desk; Mac by day; no window).** Each check has a bar.
- SMC enumeration.
- Download N (44.8 GB) after offloading the pilot-8 and pilot-9 roots.
- Full `mtp` key scan of F's index.
- Teacher-forced NLL on a fixed 2k-token SHADE prompt per model. Bar: ≤ 3.0 nats per token; the #1623 failure gave 17.46 against 1.68.
- Template round trip per model (assistant turn then tool turn): count of rewritten tokens.
- Greedy exactness, checkpoint path against a fresh prefill, over 4 turns per hybrid model: token-identical.
- `pmset -g custom` output under each energy mode, and a dry `prepare` that passes the census.

**R1 (hardware rehearsal, quiet, about 3-3.5 h).**
- 30 min idle soak.
- Planning-turn step and 10 min cooldown for Q30, N, F and D (D twice; also D under Automatic, then High Power, then Automatic if Ed opts in).
- One gated real episode per production model (spam/benign s1).
- Replays: N replayed gated against ungated (token identity, plus a small state contrast) and D replayed gated against gated (U2).
- Fill the §2.4 slots. The lead verifies the slots before the span and disk reservation are frozen, as `P3:199-214` requires.

**Dry run.** A production-shaped synthetic desk over all 18 W1 bundles must give `instrument_ok`. A bit flip in each class (anchor, contrast, N, D) must fail exactly that member. The pilot-8 bundles, re-attributed with the new code and no holds, must give byte-identical turn energies.

**Review gates.**
1. Sol 6.1 builds; the brief's WRITE_SCOPE lists the files above and their tests.
2. Opus 5.5 executing review (non-author) on the dry run.
3. Fable cold pass on the science-touching parts: the gate rules, hold attribution, parser typing and cache-checkpoint exactness.
4. CI on the lane PR.
5. R0 and R1 bars met, with the lead's verification of the slots.
6. Then arm. The pilot-8/9 desk freeze discipline applies: frozen commits are recorded before any window is read.

---

## 5. Risks, open questions, and what Ed must do

**Risks.**
- **R1. D is hot.** A planning turn is about 18 kJ against an onset budget of about 6.5-8.3 kJ, so holds are mandatory. If R1 shows they fail, fall back to 4-bit.
- **R2. Time.** Gates and holds make members long. W1 fits only 18 members, and calibrating one model takes about 3 more windows.
- **R3. Cache rewrites on hybrid models.** Without the checkpoint, F and D are infeasible. It is the critical build item.
- **R4. Tool-call parser.** Without the XML parser, D and F take no actions.
- **R5. mlx-lm 0.31.3 bug #1632.** Decision rule in §1.5.
- **R6. SMC keys on M3 Max.** Unknown; the IOHID fallback adds build time.
- **R7. Disk.**
  - Pilot 8 armed with 96 GB free (`cf1baad2` "ARM (ALIGN pilot 8)"); 82 GB was free at 00:41 on 11-05 (`c110a6c9`).
  - N needs 44.8 GB, and W1 needs 36.8 GB for two copies.
  - Offload the pilot-v7 and pilot-9 roots to iCloud first, during a desk and never during a window. Never delete a model that a registration names.
- **R8. Capability.** Next-Instruct acted 0-2 times in pilot 3. D at xhigh may hit the 4,096-token turn cap (rule in §1.6).
- **R9. Battery.** `battery.assist` appears on every member; heavier sustained load may mean more discharge and charging heat.
- **R10. Realism.** Gated energy is energy at a reference state, by convention. The paper must say so. The ungated contrast measures the gap, and gating is closer to real tool latency than the instant offline tools are.
- **R11. High Power mode and the probes.**
  - `arm_readiness_evidence_t0.py:1990` looks for `lowpowermode 0`, while macOS 26 reports `powermode`.
  - Arming has worked under Automatic, so the path the chain actually uses is not yet clear.
  - R0 must show the census and readiness probes passing under whichever mode is chosen.

**Open questions for the chair.**
1. Should gates run in W1 for the new models (my design), or should the new models run ungated until the contrast decides? The trade: about 25-35 % of member time against having controlled data from the first window.
2. Should W1 hold N and D (Ed's named models, my choice) or N and F (cheaper; D moves to W2)?
3. Is a separate R1 rehearsal (about 3.5 h of Mac time by day) worth it compared with putting the step tests into W1's first hour? I argue yes: the gate thresholds must be fixed before gated members run.
4. Should pilot 9 run first (my choice) or be skipped in favour of W1? Skipping would leave Qwen3-30B at held-out m = 10 per pair.

**Ed's physical and authority actions.**
1. Say which "Qwen 3.8" he means: 27B (runnable) or Flash-Next (not runnable on the pinned stack; §1.4).
2. Once, before R1: the stand, clearance, lid open, fixed room setpoint; battery at 100 % with Optimized Battery Charging off; an ambient logger.
3. Optional: allow High Power mode under the R1 rule (a System Settings toggle; it affects fan noise).
4. Approve the 44.8 GB N download and the iCloud offloads.
5. If R1 triggers the fallbacks: approve the D 4-bit download (16.1 GB). If #1632 forces it, approve a second pinned venv.

**Must-verify list (for the Sol seat, which has no network; I checked these on the web, and the Mac still has to confirm them).**
- N's revision `9a2b4634…`.
- No `mtp` keys in D's and F's local indexes.
- `qwen3_5_moe`, `qwen3_5` and `qwen3_next` load on 0.31.3.
- The XML tool format of D and F, and the JSON format of N.
- D's sampler and effort defaults.
- The SMC keys present.
- `pmset` output.
- The R1 rates against the planning numbers in §1.3.
