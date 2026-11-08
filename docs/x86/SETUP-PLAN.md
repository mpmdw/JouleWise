# x86 / RTX 3050 second measurement platform: setup plan

Status: plan, 2026-11-08. Context: `docs/research/research-strategy.md` (every measurement captures an external wall meter; KM003C on the Mac) and `docs/research/AGENDA.md`. Rig: desktop x86 PC, NVIDIA RTX 3050 (8 GB), Linux, llama.cpp on CUDA, loaned for months.

Source discipline: every URL below was opened. Where a page did not state a number, that is said, not filled in. Prices are listing prices seen on the day, not quotes.

## 0. Bottom line

- **Budget meter:** Athom pre-flashed Tasmota US plug, listed 12.88 USD sale (18.40 regular), 16 A, vendor claims 0.2 % active-power error. Log by HTTP polling. Vendor figure unverified; calibrate it (section 1.3).
- **Better meter:** Yokogawa WT310E (single-phase digital power meter). Listed 0.1 % of reading + 0.05 % of range, USB standard, built-in integrator. Cost is high: RS UK lists WT310E-Q-C1 at 2,230 GBP ex VAT; Transcat lists a used unit at 3,495 USD. Try to borrow one, or use it only as a one-off calibration reference for the cheap plug.
- **Plan:** run the cheap plug as the always-on logger, and cross-calibrate it once against the WT310E (or a borrowed lab meter) over a few load steps. That turns an unverified vendor claim into a measured gain/offset.
- **Per-episode energy must be computed by integrating logged power at >= 1 Hz.** Plug energy counters are too coarse (Wh scale; 1 Wh = 3,600 J).

## 1. AC wall meter options

Requirement: >= 1 Hz logging to a computer, local (no cloud) access.

| Option | Price (seen) | Rate | Stated accuracy | Local access | Fit for per-episode joules |
|---|---|---|---|---|---|
| Athom Tasmota US plug, no relay, HLW8032 ([US](https://ru.athom.tech/blank-1/no-relay-power-monitoring-us-plug-for-tasmota)) | 12.88 USD sale / 18.40 regular | Not documented on page; Tasmota publishes on `TelePeriod`, minimum 10 s ([Tasmota commands](https://tasmota.github.io/docs/Commands/)); poll `Status 10` over HTTP instead (successor of `Status 8`) | Vendor: active power "about 0.2 %", current and voltage 0.5 % | MQTT, HTTP, Web UI; open firmware | Good if polled at 1 Hz and calibrated. Actual refresh of the reading is unconfirmed, test it. |
| Shelly Plug US Gen4 ([Shelly docs](https://www.shelly.com/blogs/documentation/shelly-plug-us-gen4)) | about 25-30 USD per a [review](https://news.lavx.hu/article/shelly-gen4-plug-review-the-smart-outlet-that-does-everything-right-almost) | Not stated. Gen2+ API exposes `apower` (W) and `aenergy.total` (Wh) ([Switch component](https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Switch)) | Not stated on any page I could open | Local scripting, MQTT, UDP listed in search summaries of the product docs (the page I opened was truncated); local RPC per the API docs | Plausible; no accuracy number, so treat like the Athom: calibrate. I could not open its spec table. |
| Shelly Plug S Gen3 (EU/230 V; [KB](https://kb.shelly.cloud/knowledge-base/shelly-plug-s-mtr-gen3)) | about 17-23 EUR (retailer listings) | n/a | Not stated by Shelly | MQTT, scripting | Mentioned only because Ed is probably on 120 V; 230 V parts are the wrong product. |
| PZEM-004T v3 (Peacefair module; [components101](https://components101.com/modules/pzem-004t-energy-meter-module-pinout-datasheet)) | not checked | Update rate not stated | Page gives none (other sources claim 0.5 %, not opened) | TTL UART | **Not recommended**: bare module, voltage sensing is wired directly to mains. Safety and enclosure burden for a loaned rig. |
| Yokogawa WT310E ([Meilhaus spec](https://meilhaus.de/en/wt310.htm), [RS UK](https://uk.rs-online.com/web/p/power-meters/0662927)) | 2,230 GBP ex VAT (RS UK, option C1); used 3,495 USD ([Transcat](https://www.transcat.com/yokogawa-wt310e-used-for-sale-digital-power-meter)) | Data update 100 ms to 20 s, selectable (Meilhaus) | 0.1 % reading + 0.05 % range, 50/60 Hz | USB standard; GP-IB or RS232 selectable; Ethernet/Modbus TCP optional | Best. Built-in integrator gives Wh directly, 10 Hz updates, so sub-kJ episodes are resolvable. |

Notes on what I could not verify: RS-Online and Transcat pages returned 403 on re-fetch; the prices above come from search-result listings and the Meilhaus page (which has no price). Shelly pages were rate-limited or truncated, so no Shelly accuracy figure is claimed. TP-Link Kasa KP115/EP25 plugs are supported by [python-kasa](https://pypi.org/project/python-kasa) per search, but I could not open the page and newer firmware reportedly needs cloud credentials, so they are excluded.

### 1.1 Recommendation

- Budget pick: Athom Tasmota US plug (about 13-18 USD). Open firmware, plain HTTP, no cloud. Buy two, so one can be a spare and one a drift cross-check.
- Better pick: Yokogawa WT310E, ideally borrowed. If a purchase is needed, quote the exact option set (USB only is enough).

### 1.2 Where accuracy is uncertain

- All plug accuracy numbers are vendor claims or absent. Cheap metering chips are usually best near their mid-range; this box idles around tens of watts (section 4), so check low-load behaviour specifically. One forum user reported a Tasmota Sonoff S31 showing nothing below about 10 W in Home Assistant (forum anecdote seen in a search summary; not opened, so unverified).
- Desktop loads are switching-supply loads with high crest factor and low power factor; a cheap plug may misreport reactive/distorted loads. Test with the real rig, not a resistive heater.
- Energy totals inside plugs can reset on power loss (reviewer report, not opened). Do not use them.

### 1.3 Practical use for per-episode joules

1. Poll power at 1 Hz or faster from a separate logger (not the measured box if avoidable), NTP-synced timestamps.
2. Integrate with trapezoids over the episode window; subtract a baseline measured in a quiet idle window just before and after each episode block.
3. Resolution check: a 60 s episode at about 150 W is about 9 kJ. A 1 % meter error is about 90 J; the plug counter step of 1 Wh = 3,600 J is useless at this scale.
4. Calibration: one day with plug and reference meter in series (plug into the WT310E output side), at 4-5 load levels (idle, CPU-only, GPU-only, both). Fit gain and offset, record them in the run manifest.

## 2. Linux setup checklist (quiet measurement box)

1. **Distro:** Ubuntu LTS (current LTS, Server or minimal desktop). Reason: NVIDIA's CUDA guide documents the network-repo install for Ubuntu ([CUDA install guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)). Pin kernel and driver after the first good qualification; no unattended upgrades afterwards.
2. **Driver and CUDA:** add NVIDIA `cuda-keyring`, `apt update` separately, then `apt install cuda-toolkit`. Per the guide, from CUDA 13.4 the toolkit package no longer installs a driver; install the driver separately (`nvidia-open` or `cuda-drivers`; the guide does not choose between them, so pick one and record it). Add the CUDA `bin` dir to `PATH`. Record `nvidia-smi` and `nvcc --version` in the manifest.
3. **NVML access:** user needs access to `/dev/nvidia*` (video/render group per distro defaults). Query with `nvidia-smi --query-gpu=power.draw,power.draw.instant,clocks.sm,clocks.mem,temperature.gpu,pstate --format=csv -lms 100`. Per nvidia-smi docs, average power draw (1 s) is supported on Ampere except GA100 or newer, and instantaneous draw is "the last measured power draw for the entire board" ([nvidia-smi docs](https://docs.nvidia.com/deploy/nvidia-smi/index.html)). Log both.
4. **Persistence:** `nvidia-smi -pm 1` is not boot-persistent and is Linux-only per the docs; use the persistence daemon, which the installer does not enable at boot ([persistence daemon](https://docs.nvidia.com/deploy/driver-persistence/persistence-daemon.html)). Enable `nvidia-persistenced` via the sample systemd script.
5. **RAPL / powercap (CPU package energy, complements the wall meter):** counters live under `/sys/class/powercap/intel-rapl:*/energy_uj` ([kernel docs](https://www.kernel.org/doc/html/latest/power/powercap/powercap.html)); they are cumulative energy in microjoules with a `max_energy_range_uj` wrap range, so handle wraparound. Since CVE-2020-8694 they are root-only; make them readable by a group via a udev rule (0440, group-owned) ([CodeCarbon guide](https://docs.codecarbon.io/latest/how-to/enable-rapl/)). On AMD, check `/sys/class/powercap` exists at all; if not, skip RAPL and rely on the wall meter.
6. **Quiet system:** disable and mask what wakes periodically: `apt-daily*.timer`, `apt-daily-upgrade.timer`, `fstrim.timer` (run manually between blocks), `man-db.timer`, `motd-news.timer`, `snapd`, `unattended-upgrades`, `cups`, `avahi-daemon`, `ModemManager`, `bluetooth`, `packagekit`, `fwupd-refresh.timer`. Check with `systemctl list-timers --all` and `top` before each block. Console only; no desktop session, no screen blanking games. Disable Wi-Fi power-save noise by using Ethernet. Keep the plug logger and the harness on a different machine or a lightweight pinned core.
7. **CPU frequency:** `cpupower frequency-set -g performance`, and fix a max frequency below boost if thermal drift appears; or disable turbo (`intel_pstate/no_turbo`, or `cpufreq/boost` for AMD). Decide once, record in manifest, hold it for all blocks. Pin the harness to specific cores (`taskset`).
8. **GPU clocks:** `sudo nvidia-smi -lgc <min,max>` locks GPU clocks (supported on Volta+, root); `-rgc` resets. Choose a clock at which the 3050 does not hit its power or thermal cap, so the clocks do not wander during a run. `-lmc` locks memory clocks (also needs root; check it is accepted on this card). `-pl` power limit is documented only "from Kepler family" supported devices; check Min/Max reported. Locked clocks vs default boost is a design choice: lock for stability, and say so in the manifest.
9. **Thermals:** fan curve fixed or default but identical every block; warm-up run before measured episodes; ambient temperature logged (cheap USB sensor); a thermal gate analogous to the Mac ones.
10. **BIOS:** disable C-states only if it helps idle stability (and record the idle power change); disable onboard audio/Bluetooth/Wi-Fi if unused; set a fixed fan profile; keep ErP/EuP and similar power-saving options at one fixed setting. Keep the same BIOS profile for the loan period.
11. **llama.cpp build (CUDA):** per [build.md](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/build.md): `cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=<cc>` then `cmake --build build --config Release`. Get `<cc>` from `nvidia-smi --query-gpu=compute_cap --format=csv` (the 3050 is Ampere, expected 8.6, so `86`; verify on the card). Leave `GGML_NATIVE` on for a single-machine build. `GGML_CUDA_FORCE_MMQ` (custom quantized kernels instead of FP16 cuBLAS) and `GGML_CUDA_FORCE_CUBLAS` change the compute path and therefore the energy; pick one explicitly and keep it fixed, do not leave to defaults across versions. Pin the llama.cpp commit hash; the harness port (Sol job) should log build flags in the manifest. `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1` must stay unset (spilling to system RAM invalidates the run). Flash attention and KV-cache quantization (`GGML_CUDA_FA_QUANTS`) are also fixed per prereg.

## 3. Models: 8B-class, 4-bit GGUF, 8 GB VRAM

VRAM budget: RTX 3050 8 GB has 8 GB GDDR6 on a 128-bit bus and 130 W board power ([NVIDIA](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3050/)). Leave about 0.5-1 GB for CUDA context and compute buffers, and run headless so the display does not take VRAM.

| Model | Q4 GGUF size | Notes |
|---|---|---|
| Qwen3-8B ([bartowski GGUF](https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF)) | Q4_K_M 5.03 GB, Q4_K_S 4.80 GB, IQ4_XS 4.56 GB, Q5_K_M 5.85 GB | Card says it excels at tool calling and complex agent tasks in thinking and non-thinking modes; 32,768 native context, 131,072 with YaRN; thinking on by default, hard switch `enable_thinking=False` ([model card](https://huggingface.co/Qwen/Qwen3-8B)). Best first candidate. |
| Llama 3.1 8B Instruct ([bartowski GGUF](https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF)) | Q4_K_M 4.92 GB, Q4_K_S 4.69 GB, IQ4_XS 4.45 GB, Q5_K_M 5.73 GB | 128k context, "multiple tool use formats" ([model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)); custom license with attribution terms. |
| Granite 4.0-H-Tiny ([model card](https://huggingface.co/ibm-granite/granite-4.0-h-tiny)) | not checked (about 7B total, 1B active MoE, BF16 weights) | BFCL v3 57.65, Apache 2.0, 128K context. Hybrid arch: confirm llama.cpp CUDA support and find a GGUF before counting on it. Active-parameter count differs, so energy per token differs: interesting contrast case. |

KV-cache check (my arithmetic from the public architecture, verify against `config.json`): Qwen3-8B has 36 layers; with 8 KV heads of dim 128 and fp16 cache that is about 144 KiB per token, so 16k tokens is about 2.3 GB and 32k about 4.5 GB. On Q4_K_M weights (5.03 GB) plus 8k-16k context this fits in 8 GB; 32k does not once compute buffers are added. Llama 3.1 8B (32 layers) is about 128 KiB per token. Quantizing KV to q8_0 halves it, but changes numerics/energy: fix it per prereg.

Suitability as SHADE-Arena agents: both candidates are plausible for tool use and multi-turn, but 8B local models will score far below the frontier agents SHADE-Arena was built for; treat this rig as an energy-per-episode platform with a weaker agent, not a replicate of v4 results (which use Qwen3.8-27B 8-bit per the strategy doc). Check tool-call success rate on a pilot before committing: llama.cpp must be run with the model's own chat template for tool calls (`--jinja`; flag spelling to be confirmed against the pinned build).

## 4. Measurement caveats for this rig

- **Wall vs DC:** the wall meter sees PSU losses plus every other component. The Mac KM003C measures DC-in; this rig cannot be compared like for like. Report wall AC energy as the primary quantity here, and never mix it numerically with Mac DC-in joules without stating it. Optionally add per-rail components: GPU via NVML, CPU via RAPL, residual = everything else.
- **PSU efficiency varies with load:** the 80 PLUS table (115 V) requires 80-87 % at 20 % load for Standard-to-Gold, 90-92 % at 50 % load for Platinum-Titanium ([Wikipedia 80 Plus](https://en.wikipedia.org/wiki/80_Plus)), and "80 Plus does not set efficiency targets for very low load"; the article says a 520 W supply could be 70 % or less efficient at 60 W, a typical desktop idle. So a PSU converting 40 W vs 200 W DC will have different efficiency, and the wall-minus-idle difference does not equal DC energy. Identify the PSU model and rating; record which curve applies; a 550 W-class supply (NVIDIA lists 550 W system power for the 3050) is oversized for this load, which pushes the box into the low-efficiency region.
- **Idle power:** measure it carefully. A desktop idles at tens of watts, and the episode's increment may be a modest fraction of it. Log idle baselines before and after every block and treat drift as a quality gate. Disable unused devices (section 2.10). Idle depends on GPU state (P-state, persistence mode, locked clocks), so changing those changes the baseline.
- **NVML power resolution on consumer GPUs:** NVIDIA documents +/-5 W; an independent study of 70+ GPUs found proportional error of about +/-5 %, a stable per-GPU gain and offset, and warns the default average power can be a 1 s window on Ampere/Ada, smoothed and lagging ([Yang et al., arXiv 2312.02741](https://arxiv.org/html/2312.02741v3)). Consumer Ampere cards in that study had the averaging window equal to the update interval, so no samples are missed, but readings lag. For a 130 W-class card, +/-5 % is about +/-6.5 W. Use NVML as a component trace (shape, attribution), and the wall meter as the energy of record. Use `power.draw.instant` plus the average, align traces to GPU activity, and do not use NVML total energy until checked against the wall meter. The paper does not discuss the NVML energy counter.
- **Meter sampling vs workload:** agent episodes alternate GPU bursts (prefill, decode) with CPU/idle gaps (tool execution, network). 1 Hz sampling is adequate for energy (integral) but not for attributing phases; use NVML and timestamps for phases.
- **Chain of timing:** wall meter, NVML, harness, and RAPL use different clocks. Sync with NTP/chrony, log a start and end marker pulse (a short GPU burst at known times) to align traces.
- **Repeats:** the same-workload noise (fans, temperature, DVFS) is larger than on the Mac; use the paper's practice of repeated runs with randomised delays and discard thermal transients ([arXiv 2312.02741](https://arxiv.org/html/2312.02741v3)).

## 5. Order of work

1. Order two Athom plugs; line up a WT310E loan (university lab, supplier rental).
2. Install Ubuntu, driver, CUDA, persistence daemon, quiet-box services (sections 2.1-2.6). Capture an idle trace on both meters for 30 min.
3. Calibrate plug vs reference at 4-5 load steps (1.3.4).
4. Build llama.cpp with fixed flags, qualify Qwen3-8B Q4_K_M with a 20-episode pilot; record tokens/s, wall W, NVML W, RAPL W.
5. Freeze: kernel, driver, CUDA, llama.cpp hash, clocks, BIOS, fan profile, meter calibration; write them into the run manifest before any registered block.
