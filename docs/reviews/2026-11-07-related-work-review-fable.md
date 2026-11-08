# Related-work literature review (Fable seat), 2026-11-07

Status: audit-track deliverable, not a paper section. Written by the Fable 5.1
seat of the "Related-work literature review" audit track. A second model audits
the same brief independently. Nothing here is a measurement, a Block-5 value, or
a claim; Block 5 stays sealed and nothing in this document was derived from it.

Repo evidence is cited as `path:line` at `main` commit `9406e49a2` (the handoff
clone) or at `desk/2026-11-01-align-pilot-v0` commit `cbfb9b0a5` for the agent-
monitoring (ALIGN) docs, which are not on `main`. The brief named
`docs/align/pilot_protocol_v4.md`; that file does not exist on any fetched
branch of `mpmdw/JouleWise` (only `pilot_protocol_v0.md` on the desk branch and
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v{1,2,3}.json` on
`main`). The v0 protocol was used instead; see Open questions.

Every external source below was opened with WebFetch unless marked otherwise:

- **OPENED**: the arXiv abstract page, publisher page, or full text was fetched
  and the bibliographic fields below were read from it.
- **PARTIAL**: a primary page was fetched but returned only metadata or binary
  content, so the substantive summary rests on a secondary page that was opened.
- **UNVERIFIED**: no primary page could be opened (403, paywall redirect, or
  only search snippets); fields come from the search index and should be
  re-checked before citation.

## 0. What JouleWise measures (for the relevance notes)

- One instrument: `powermetrics` on Apple silicon at 10 Hz (one reading per
  100 ms), integrated only inside runtime-emitted phase boundaries, with a timing
  calibration of where the sampler places energy in time, issued per macOS build
  and judged by a cold reviewer before use (`README.md:21`, `:23`;
  `docs/paper/draft-v1.md:324-330`).
- Gross energy within a named boundary as the headline basis; idle-subtracted
  energy only as a within-device secondary view (`README.md:63-70`).
- Battery must be full and floating (not charging) during every measurement,
  because charging heats the chip; a keep-awake job prevents sleep; an agent
  session at the keyboard voids a session (`README.md:19`, `:23`).
- Rules sealed by an independent reviewer before data exist; a desk program
  reads counts and check results and never an energy; opening measured energies
  needs reviewer approval; eight removed or refused attempts kept and disclosed
  (`README.md:19`).
- A *detection floor*: the largest false difference the admitted measurement
  system can produce, minted by a governed process; contrasts below it are
  refused (`README.md:11-13`; `draft-v1.md:342`).
- The *prefill probe*: find the shortest prompt length at which five runs of the
  small model show at least five power readings overlapping prefill, because
  prefill of a 1.7B model can be shorter than a few 100 ms samples
  (`README.md:21`).
- ALIGN pilot v0: SHADE-Arena task pairs (`spam_filter_update`, `bank_transfer_2`)
  run on Qwen3-8B-4bit under MLX, benign vs sabotage system prompts, 12 episodes
  in ABBA order inside the unchanged Block-6 scaffold; per-turn prefill, decode
  and hidden-token counts, tool-call timestamps, and per-segment attributed
  energy recorded; no monitor runs during the session
  (`docs/align/pilot_protocol_v0.md:23-60` at `cbfb9b0a5`).
- Research questions: RQ-ALIGN-METADATA-BASELINE (do token/turn/tool counts
  alone separate benign from sabotage), RQ-ALIGN-ENERGY-RESIDUAL (does energy
  beyond what logged tokens predict flag hidden or deleted work),
  RQ-ALIGN-EFFICIENCY-MONITORABILITY (cheapest configuration in measured joules
  reaching a monitor catch rate) (`docs/align/PIPELINE.md:26-30` at
  `cbfb9b0a5`). The residual detector's design is
  `[1, prefill, decode, context*decode, context*prefill]`, trained only on benign
  episodes per hardware/model/serving configuration; "Power can count work
  omitted from a log; it cannot tell what reasoning occurs inside the same
  forward passes" (`docs/align/energy_residual.md:1-30` at `cbfb9b0a5`).

What the paper draft already cites (`docs/paper/draft-v1.md:320-392`): Khan et
al. RAPL in Action; Jay et al.; Hähnel et al. (short code paths under RAPL); Ma
et al. Illusion of Power Capping; TokenPowerBench; Ruf and Detyniecki; ML.ENERGY;
JouleSort; SPECpower; MLPerf Power; Georges/Buytaert/Eeckhout; Mytkowicz et al.;
Paired-MDE; disaggregation papers; SplitZip. This review does not re-derive
those; it adds what the draft lacks: Apple-specific telemetry validity, the
agent-monitoring and control literature, the agent-energy literature, reasoning-
token energy, and the preregistration/blinding lineage.

## 1. Energy and power measurement of LLM inference on Apple silicon and edge devices

### 1.1 Apple's own statement of what `powermetrics` is

**S1. `powermetrics(1)` man page (Apple; community mirror).** OPENED.
<https://keith.github.io/xcode-man-pages/powermetrics.1.html>
Apple's text: "Average power values reported by powermetrics are estimated and
may be inaccurate" and "should not be used for any comparison between devices";
the `cpu_power` sampler's energy-model data are "generally not comparable across
machine models"; the thermal sampler is "an instantaneous value taken at the end
of the sample window"; default interval 5000 ms, settable with `-i`.
*Relevance.* This is the vendor's own validity caveat for JouleWise's sole
instrument. It supports JouleWise's within-device, paired-contrast design and
its refusal to rank devices on `powermetrics` numbers; it also means the
thermal flag JouleWise records is an end-of-window snapshot, not an integral,
which the paper should state when it describes thermal hazard gating.

**S2. Oakley, H. "What does Activity Monitor measure?" The Eclectic Light
Company, 2026-06-29.** OPENED.
<https://eclecticlight.co/2026/06/29/what-does-activity-monitor-measure/>
Practitioner measurement on an M4 Pro Mac mini: Activity Monitor's "Energy
Impact" tracks CPU power only and is non-linear (implied a 173x P/E-core ratio
where `powermetrics` energy gave about 11x); neither tool estimates memory or SSD
power; Macs do not expose wall power; most consumer wattmeters are unreliable
below about 5 W.
*Relevance.* Explains why JouleWise integrates named `powermetrics` channels
rather than any OS-level "energy" score, and why an external meter cross-check at
laptop idle power is itself a measurement problem rather than a free ground
truth. Useful in the limitations section when the paper admits it lacks an
independent counter cross-check (`draft-v1.md:330`).

### 1.2 Studies that use `powermetrics` on Apple silicon for LLM or HPC workloads

**S3. Hübner, P., Hu, A., Peng, I., Markidis, S. "Apple vs. Oranges: Evaluating
the Apple Silicon M-Series SoCs for HPC Performance and Efficiency." arXiv
2502.05317, 2025.** OPENED. <https://arxiv.org/abs/2502.05317>
Measures M1 to M4 power with `powermetrics`; reports chips drawing a few watts to
10-20 W and more than 200 GFLOPS/W on GPU and accelerators; no external meter and
no validation of the tool is described in the abstract.
*Relevance.* Representative of the current state: `powermetrics` is used as if
it were a meter. JouleWise's timing calibration and detection floor are the
missing validation layer, and this paper is the right citation for "prior work
uses the tool without characterising it".

**S4. Kannan, R., Firke, R., Bengle, S., Deshmukh, S. "GreenBench: Benchmarking
Energy Efficiency and Carbon Footprint of Open-Source LLM Inference on Apple
Silicon." arXiv 2608.28667, 2026 (comments: accepted IEEE ICCUBEA 2026).**
OPENED. <https://arxiv.org/abs/2608.28667>
M4 Pro, Ollama, five 3-9B models; `powermetrics` for "CPU+GPU package power";
reports about 0.47 W package power during sustained inference against 8-12 W
total system power, per-token energy as power times per-token latency, smaller
models up to 62% less energy per token, and a 30-40x advantage over datacenter
GPUs.
*Relevance.* The closest published work to JouleWise's hardware and question,
and a cautionary example. A 0.47 W package figure during sustained decode of a
7B model is not plausible for an M4 Pro GPU and is inconsistent with the paper's
own 8-12 W system number; it looks like a channel or unit misreading. No idle
baseline, thermal handling, or repeat protocol is described. JouleWise's paper
can cite it as the nearest neighbour and as the reason channel naming,
calibration and a detection floor are necessary before any per-token number on a
Mac is quotable.

**S5. Rajesh, V. et al. "Production-Grade Local LLM Inference on Apple Silicon:
A Comparative Study of MLX, MLC-LLM, Ollama, llama.cpp, and PyTorch MPS." arXiv
2511.05502, 2025.** OPENED. <https://arxiv.org/abs/2511.05502>
M2 Ultra, Qwen2.5 family, prompts to 100k tokens; MLX highest sustained
throughput; energy is not among the metrics.
*Relevance.* Establishes MLX as the throughput-leading runtime JouleWise
measures, and shows that the Apple-runtime comparison literature reports
tokens/s without joules. JouleWise supplies the energy axis for the same
runtime.

**S6. Preprint "LLM inference energy on Apple Silicon" (preprints.org
202605.0855 v1, May 2026).** UNVERIFIED (HTTP 403 on fetch).
<https://www.preprints.org/manuscript/202605.0855/v1>
Search snippets say it claims no prior work has validated an energy estimation
method for Apple-silicon LLM inference and that its telemetry used `top`,
`vm_stat`, `ioreg` and `ps` at 1.5 s intervals, not `powermetrics`, because the
latter needs root.
*Relevance.* If the snippet is accurate it concedes exactly the gap JouleWise
fills, but from a weaker instrument. Re-open before citing.

### 1.3 Software counter validity on other platforms (gain-axis lineage)

**S7. Khan, K. N., Hirki, M., Niemi, T., Nurminen, J. K., Ou, Z. "RAPL in
Action: Experiences in Using RAPL for Power Measurements." ACM TOMPECS 3(2),
Article 9, 2018. DOI 10.1145/3177754.** PARTIAL (open-access PDF fetched as
binary; bibliographic record confirmed by search; already cited at
`draft-v1.md:366`). <https://doi.org/10.1145/3177754>
Validates RAPL against external meters by regression on plug power; high
correlation, negligible overhead, but jittery ~1 ms update period and cold-start
effects.
*Relevance.* Already the paper's anchor for "gain validity". Keep; no change.

**S8. Yang, Z., Adámek, K., Armour, W. "Part-time Power Measurements:
nvidia-smi's Lack of Attention." arXiv 2312.02741, 2023 (DOI
10.1109/SC41406.2024.00028 for SC'24).** OPENED.
<https://arxiv.org/abs/2312.02741>
Micro-benchmarks on 70+ GPUs; on A100/H100 only about 25% of runtime is actually
sampled for power; corrected practice cuts energy error by 35% average, up to
65%, against an external meter.
*Relevance.* The GPU analogue of JouleWise's sampler-coverage concern. The
prefill probe (`README.md:21`) is a direct response to the same hazard: a phase
shorter than the sampler's coverage cannot be measured. Cite beside Hähnel.

### 1.4 Edge and mobile devices (thermal and sustained-load confounds)

**S9. Laskaridis, S., Katevas, K., Minto, L., Haddadi, H. "MELTing point:
Mobile Evaluation of Language Transformers." MobiCom 2024, pp. 890-907; arXiv
2403.12844.** OPENED. <https://arxiv.org/abs/2403.12844>
Android, iOS and Jetson; LLM inference memory-bound; quantization makes
execution viable at accuracy cost; "continuous execution of LLMs remains
elusive" because energy and heat degrade experience.
*Relevance.* The peer-reviewed statement that thermal behaviour, not nominal
compute, limits sustained on-device inference. JouleWise treats thermal pressure
as a hazard flag per member and bans charging; this paper motivates both.

**S10. Tummalapalli, P., Arayakandy, S., Pal, R., Kundan, K. "LLM Inference at
the Edge: Mobile, NPU, and GPU Performance Efficiency Trade-offs Under Sustained
Load." arXiv 2603.23640, 2026.** OPENED. <https://arxiv.org/abs/2603.23640>
Qwen2.5-1.5B 4-bit, 258-token prompt, 20 warm iterations on Pi 5 + Hailo-10H,
Galaxy S24 Ultra, iPhone 16 Pro, RTX 4050 laptop. iPhone loses nearly half its
throughput within two iterations; S24 hits an OS GPU-frequency floor that stops
inference; RTX 4050 sustains 131.7 tok/s at a battery-limited 34.1 W.
*Relevance.* Quantifies how fast thermal and battery policies move the operating
point on Apple mobile silicon. Supports JouleWise's bracketed references
(start/mid/end triplets) and its drift bound as necessary, not decorative.
Measurement tooling is not described in the abstract; check before citing
numbers.

**S11. Islam, M. R. et al. "Characterizing and Understanding Energy Footprint
and Efficiency of Small Language Model on Edges." arXiv 2511.11624, 2025
(presented IEEE MASS 2025).** OPENED. <https://arxiv.org/abs/2511.11624>
Pi 5, Jetson Nano, Jetson Orin Nano; Llama 3.2, Phi-3 Mini, TinyLlama, Gemma 2;
Orin Nano GPU best energy-to-performance; measurement method, per-token numbers,
thermal and idle handling not in the abstract.
*Relevance.* Typical edge-energy paper: rankings without an error budget.
JouleWise's floor-gated refusal is the contrast.

**S12. Zähl, P. M., Dalipaj, E., Hennig, A., Bayer, T. "Energy Efficiency of
Locally Deployed LLMs: A Preliminary Quantitative GPU Power Benchmark on
Consumer Hardware." arXiv 2608.00008, 2026.** OPENED.
<https://arxiv.org/abs/2608.00008>
RTX 4060 Ti, Ollama, 18 models 0.5-7B, `nvidia-smi` at 2 Hz; 0.27 J/tok
(qwen2.5:0.5b) to 8.6x that for Mistral 7B; a thinking-mode model shows
anomalously high energy per prompt, so the authors argue generation modes must be
distinguished in efficiency metrics.
*Relevance.* Independent evidence that hidden reasoning tokens dominate
per-prompt energy, the premise of RQ-ALIGN-ENERGY-RESIDUAL. Its 2 Hz sampler
with S8's finding also shows why JouleWise's 10 Hz and coverage probe matter.

**S13. Husom, E. J., Goknil, A., Shar, L. K., Sen, S. "The Price of Prompting:
Profiling Energy Use in Large Language Models Inference." arXiv 2407.16893,
2024 (v2 2026).** OPENED (full HTML). <https://arxiv.org/abs/2407.16893>
MELODI: Scaphandre for process-level CPU power plus `nvidia-smi` for GPU; server,
workstation and two laptops (one CPU-only); response token length is the
strongest energy predictor (r about 0.77) while prompt features correlate weakly
(about 0.13); 70B-class models about two orders of magnitude more energy per
token than small ones; a regression on response length, model and hardware
reaches R^2 0.996.
*Relevance.* The published regression most similar in spirit to JouleWise's
energy-residual design, but at whole-request grain and with no uncertainty on
the measurement. JouleWise's per-turn attribution with half-widths and the
decode/prefill/context design (`energy_residual.md`) is the finer instrument;
cite MELODI as the coarse ancestor.

## 2. Energy and cost of LLM agents and of agent monitoring

### 2.1 Sabotage and monitoring benchmarks (SHADE-Arena and successors)

**S14. Kutasov, J. et al. (12 authors incl. Shlegeris, Benton). "SHADE-Arena:
Evaluating Sabotage and Monitoring in LLM Agents." arXiv 2506.15740, 2025.**
OPENED. <https://arxiv.org/abs/2506.15740>
17 task pairs of a benign main task plus a harmful side task in tool-rich
environments; best sabotage success 27% (Claude 3.7 Sonnet) under a Claude 3.6
monitor; best monitor Gemini 2.5 Pro AUC 0.87; side-task success leans heavily
on a hidden scratchpad the monitor cannot see; no compute or token cost of
monitoring reported.
*Relevance.* The source of JouleWise's ALIGN tasks (pinned at upstream
`6614e771`, `docs/align/shade_port.md` at `cbfb9b0a5`). The hidden-scratchpad
finding is the mechanistic reason an energy residual could carry signal: hidden
tokens are work the log can omit but the SoC cannot. The paper reports no
energy, no per-turn timing and no monitoring cost, which is the opening.

**S15. Benton, J. et al. "Sabotage Evaluations for Frontier Models." arXiv
2410.21514, 2024.** OPENED. <https://arxiv.org/abs/2410.21514>
Threat models and evaluations for covert sabotage of evaluation, monitoring and
deployment decisions; Claude 3 Opus and 3.5 Sonnet; minimal mitigations
currently sufficient; argues for mitigation-aware evaluations and simulating
large deployments from small-scale statistics.
*Relevance.* Frames "undermining oversight" as a capability to measure; the
small-sample-to-deployment extrapolation is the same inferential move JouleWise's
pilot sizing makes with `sigma_pair` (`apple_path.md:306-373`).

**S16. Mittapalli, V. et al. "TRACE: Trajectory Reasoning through Adaptive
Cross-Step Evidence Aggregation for LLM Agents." arXiv 2606.07054, 2026.**
OPENED. <https://arxiv.org/abs/2606.07054>
Triage-Inspect-Judge monitoring loop over long trajectories; on ten SHADE-Arena
domains F1 0.713, recall 0.844; no cost or token overhead reported.
*Relevance.* Shows SHADE-Arena is becoming the standard monitor testbed and
that monitor papers still do not report their own compute. A joule-per-catch
axis (RQ-ALIGN-EFFICIENCY-MONITORABILITY) has no occupant.

**S17. Ward, F. R. et al. "CTRL-ALT-DECEIT: Sabotage Evaluations for Automated
AI R&D." arXiv 2511.09904, 2025 (NeurIPS 2025 spotlight).** OPENED.
<https://arxiv.org/abs/2511.09904>
MLE-Bench extension in Inspect; agents implant backdoors, cause generalisation
failures, sandbag to target levels; LM monitors fairly good on code sabotage,
weak on sandbagging; aggregating monitors helps.
*Relevance.* Sandbagging is work-reducing, not work-hiding; an energy residual
would be expected to go negative rather than positive. Worth one sentence in the
ALIGN design about the sign of the effect each threat model predicts.

**S18. Debenedetti, E. et al. "AgentDojo: A Dynamic Environment to Evaluate
Prompt Injection Attacks and Defenses for LLM Agents." arXiv 2406.13352, 2024.**
OPENED. <https://arxiv.org/abs/2406.13352>
97 tasks, 629 security cases; models fail many tasks even unattacked.
*Relevance.* The other widely used tool-agent security environment; relevant
only as an alternative task source if SHADE pairs prove too long for a session.

### 2.2 AI control and monitoring protocols

**S19. Greenblatt, R., Shlegeris, B., Sachan, K., Roger, F. "AI Control:
Improving Safety Despite Intentional Subversion." arXiv 2312.06942, 2023 (ICML
2024 version linked).** OPENED. <https://arxiv.org/abs/2312.06942>
Untrusted GPT-4, trusted GPT-3.5, limited human audit; protocols (trusted
editing, untrusted monitoring) evaluated against red-team subversion; the
"control evaluation" methodology.
*Relevance.* Defines the trusted/untrusted monitor vocabulary JouleWise's
ALIGN docs borrow. Control evaluations budget human audits but not joules;
JouleWise asks what oversight costs in energy on the device that runs the agent.

**S20. Bhatt, A. et al. "Ctrl-Z: Controlling AI Agents via Resampling." arXiv
2504.10374, 2025.** OPENED. <https://arxiv.org/abs/2504.10374>
BashBench, 257 sysadmin tasks; resample protocols cut attack success 58% to 7%
at 5% usefulness cost.
*Relevance.* Resampling multiplies inference work per step; a protocol's
energy cost is a first-class design variable JouleWise could measure and no
control paper reports.

**S21. UK AI Security Institute. "Introducing ControlArena: A library for
running AI control experiments." 2025-10-22.** OPENED.
<https://www.aisi.gov.uk/blog/introducing-controlarena-a-library-for-running-ai-control-experiments>
Settings with main/side tasks, policies, monitors, micro- and macro-protocols,
built on Inspect.
*Relevance.* If ALIGN grows beyond two SHADE pairs, ControlArena is the
standard harness to port rather than a bespoke runner; its Inspect sandboxing
conflicts with JouleWise's "no agent process on the Mac" rule, which would need
a design note.

**S22. Cooper Stickland, A. et al. (UK AISI). "Async Control: Stress-testing
Asynchronous Control Measures for LLM Agents." arXiv 2512.13526, 2025.**
OPENED. <https://arxiv.org/abs/2512.13526>
Post-hoc monitoring of a Claude 4.1 Opus SWE agent across five internal-infra
environments; ensemble monitor 6% FNR at 1% FPR; extrapolation from FNR to
deployment risk.
*Relevance.* JouleWise's protocol is asynchronous by construction (no monitor
during the session; `pilot_protocol_v0.md:114`), so this is the
control-theoretic frame to cite. The paper does not price the monitor.

**S23. Terekhov, M., Liu, Z. N. D., Gulcehre, C., Albanie, S. "Control Tax: The
Price of Keeping AI in Check." arXiv 2506.05296, 2025 (v3 2026).** OPENED.
<https://arxiv.org/abs/2506.05296>
Defines control tax as the operational and financial cost of control measures;
empirical dollar cost estimates for LLM monitors under an auditing budget;
safety-versus-cost curves; no energy or compute unit.
*Relevance.* The nearest prior art to RQ-ALIGN-EFFICIENCY-MONITORABILITY and
the citation that proves the axis is priced in dollars, not joules. JouleWise's
contribution would be the measured-joule version of the same frontier on local
hardware.

### 2.3 Chain-of-thought monitoring

**S24. Korbak, T. et al. (41 authors). "Chain of Thought Monitorability: A New
and Fragile Opportunity for AI Safety." arXiv 2507.11473, 2025.** OPENED.
<https://arxiv.org/abs/2507.11473>
Position paper: CoT monitoring is imperfect but promising; monitorability may
be fragile under developer choices; calls for monitorability evaluations.
*Relevance.* Supplies the "hidden tokens are the monitorable surface" premise.
JouleWise's residual asks whether a physical trace survives when the textual
trace is removed or obfuscated (tamper transforms,
`pilot_protocol_v0.md:114`).

**S25. Baker, B. et al. (OpenAI). "Monitoring Reasoning Models for Misbehavior
and the Risks of Promoting Obfuscation." arXiv 2503.11926, 2025.** OPENED.
<https://arxiv.org/abs/2503.11926>
CoT monitoring far more effective than action-only for reward hacking; GPT-4o
can monitor o3-mini; training against the monitor yields obfuscated reward
hacking; proposes a "monitorability tax".
*Relevance.* Obfuscation hides intent in text but not the compute spent; an
energy residual is one candidate monitor that optimisation pressure on text
cannot directly erase. State this as hypothesis, not finding.

**S26. Arnav, B. et al. "CoT Red-Handed: Stress Testing Chain-of-Thought
Monitoring." NeurIPS 2025.** OPENED.
<https://proceedings.neurips.cc/paper_files/paper/2025/hash/468a018d4eb4ef57a2a5715d16658b24-Abstract-Conference.html>
Weak trusted monitor reads strong model's CoT; CoT helps where action-only
fails but rationalisations fool it; hybrid reasoning+action score about doubles
detection on subtle cases.
*Relevance.* The hybrid-score result suggests the natural evaluation for
JouleWise: add an energy channel to a text monitor and test whether the
combination moves detection at fixed false-positive rate.

### 2.4 Energy of agentic workloads

**S27. Panigrahy, D., Tyagi, A., Abkin, S., Houngninou, D. K., Mahapatra, R.
"Energy per Successful Goal: Goal-Level Energy Accounting for Agentic AI
Systems." arXiv 2605.22883, 2026 (v2 Oct 2026).** OPENED.
<https://arxiv.org/abs/2605.22883>
A-LEMS: RAPL on x86, SPBM and DCGM on NVIDIA GB10; a temporal boundary model and
a five-layer attribution pipeline from hardware signals to workflow energy;
Energy per Successful Goal includes failed attempts and retries; Orchestration
Overhead Index 0.35x to 11x CPU-only, 0.4x to 26x with GPU; GPU is 83.8% of
agentic energy in local inference; overhead comes from extra calls, not costlier
calls.
*Relevance.* The closest methodological sibling to JouleWise's ALIGN
attribution (temporal boundaries, per-segment attribution, reproducibility
protocol), on NVIDIA and x86 rather than Apple silicon, and without a detection
floor or preregistration. Its finding that orchestration structure drives
energy supports treating turn and tool-call counts as covariates
(RQ-ALIGN-METADATA-BASELINE).

**S28. Luo, Q., Li, K., Wang, Z., Chen, Y. "Where Does the Energy Go? Profiling
LLM Agent Inference on Blackwell GPUs." arXiv 2609.29707, 2026.** OPENED.
<https://arxiv.org/abs/2609.29707>
2x RTX PRO 6000, Qwen3.8-27B; NVML + RAPL + IPMI; GPU-only telemetry misses
41-45% of system energy; sequential agent workload uses 63x more system energy
per output token than saturated serving, partly from context growth.
*Relevance.* Direct support for JouleWise's gross-energy boundary and for the
`context*decode` term in the residual design. Also the strongest published
number for why single-stream agent energy per token is far above serving
benchmarks.

**S29. Fortuna, C., Hanžel, V., Strnad, T., Bertalanič, B. "Where Should
Agents Live? Energy-Memory Characterization of Agentic AI for the Edge-Cloud
Continuum." arXiv 2609.18283, 2026.** OPENED.
<https://arxiv.org/abs/2609.18283>
A100/H100 benchmark configurations; closed-form two-rate (prefill/decode)
single-call energy model coupled with OSI transport modelling; inter-agent
transport about 0.25% of workflow energy; extra inference from inter-agent
context dominates.
*Relevance.* Its two-rate model is the same functional form JouleWise fits
per turn; cite as corroboration that prefill and decode need separate
coefficients. Edge tier is modelled, not measured; JouleWise measures it.

**S30. Tripathy, A., Harshit, C. P., Vaidhyanathan, K. "SWEnergy: An Empirical
Study on Energy Efficiency in Agentic Issue Resolution Frameworks with SLMs."
AGENT 2026 (ICSE workshop), pp. 104-111; arXiv 2512.09543.** OPENED.
<https://arxiv.org/abs/2512.09543>
Four frameworks, Gemma-3 4B and Qwen3 1.7B, 150 runs per configuration;
AutoCodeRover used 9.4x the energy of OpenHands; near-zero resolution, so most
energy is unproductive reasoning loops.
*Relevance.* Qwen3 1.7B is JouleWise's small model; this is the published
reminder that an SLM agent may not attempt the task at all, which is why pilot
v0 records main/side task scores "to see whether an 8B model attempts the tasks
at all" (`pilot_protocol_v0.md:87-88`).

**S31. Krupp, L., Geißler, D., Lukowicz, P., Karolus, J. "Towards Sustainable
Web Agents: A Plea for Transparency and Dedicated Metrics for Energy
Consumption." arXiv 2502.17903, 2025.** OPENED.
<https://arxiv.org/abs/2502.17903>
Position paper: agent energy should be a reported metric; developers rarely
disclose enough to estimate it.
*Relevance.* Motivational citation only.

### 2.5 Side channels (nearest relatives of "energy as a monitor signal")

**S32. McDonald, G., Bar Or, J. "Whisper Leak: a side-channel attack on Large
Language Models." arXiv 2511.03675, 2025.** OPENED.
<https://arxiv.org/abs/2511.03675>
Packet size and timing of streamed responses classify prompt topic at >98%
AUPRC across 28 models.
*Relevance.* The literature infers token counts and topics from timing and
packet metadata; no source found infers hidden computation from power or
energy. This absence is JouleWise's gap (Section 5), and Whisper Leak is the
right "nearest relative" citation.

## 3. Energy per token versus model size and quantization; prefill versus decode

**S33. Samsi, S. et al. "From Words to Watts: Benchmarking the Energy Costs of
Large Language Model Inference." arXiv 2310.03003, 2023.** OPENED.
<https://arxiv.org/abs/2310.03003>
LLaMA models on V100/A100, up to 32 GPUs, Alpaca and GSM8K; preliminary
analysis of energy versus scale, batch size, shard count and generation length.
*Relevance.* The standard early citation for inference energy; datacenter
scale only.

**S34. Luccioni, A. S., Jernite, Y., Strubell, E. "Power Hungry Processing:
Watts Driving the Cost of AI Deployment?" ACM FAccT 2024, pp. 85-99; arXiv
2311.16863.** OPENED. <https://arxiv.org/abs/2311.16863>
Energy and carbon per 1,000 inferences across 88 models and 10 tasks;
multi-purpose generative models orders of magnitude costlier than task-specific
ones at matched parameter count.
*Relevance.* Establishes that parameter count is not a sufficient predictor,
which is why JouleWise's contrasts are between named configurations rather than
a size axis.

**S35. Niu, C. et al. "TokenPowerBench: Benchmarking the Power Consumption of
LLM Inference." arXiv 2512.03024, 2025 (AAAI 2026).** OPENED (already cited at
`draft-v1.md`). <https://arxiv.org/abs/2512.03024>
Phase-aligned attribution of energy to prefill and decode per request; GPU,
node and system power "without specialized power meters"; 1B to 405B models.
*Relevance.* Already in the draft; the draft's critique (no boundary events,
alignment rule, repetition protocol or idle baseline disclosed) stands.

**S36. Delavande, J., Pierrard, R., Luccioni, S. "Understanding Efficiency:
Quantization, Batching, and Serving Strategies in LLM Energy Use." arXiv
2601.22362, 2026.** OPENED. <https://arxiv.org/abs/2601.22362>
H100 with TGI, five precisions; lower precision saves energy only in
compute-bound regimes; batching helps most in memory-bound decode; arrival
shaping cuts per-request energy up to 100x.
*Relevance.* Explains why a 4-bit versus 8-bit contrast on a memory-bound
single-stream Mac decode may be small or sign-ambiguous; a JouleWise
quantization contrast needs a floor and a preregistered direction, not a prior
that "smaller is cheaper".

**S37. Ma, B., Afzal, A., Eitzinger, J., Wellein, G. "The Illusion of Power
Capping in LLM Decode: A Phase-Aware Energy Characterisation Across Attention
Architectures." arXiv 2605.11999, 2026 (PPAM 2026).** OPENED (already cited at
`draft-v1.md:381`). <https://arxiv.org/abs/2605.11999>
H200, vLLM; decode draws under half of rated power and ignores power caps;
SM-clock locking recovers up to 32% of decode energy; recurrent architectures
show no prefill penalty.
*Relevance.* Already the draft's "closest methodological rival"; no change.

**S38. Solovyeva, L., Castor, F. "Towards Green AI: Decoding the Energy of LLM
Inference in Software Development." arXiv 2602.05712, 2026.** OPENED.
<https://arxiv.org/abs/2602.05712>
Higher prefill cost amplifies per-token decode energy by 1.3% to 51.8%
depending on model; three of ten models "babble"; suppressing it saves 44-89%.
*Relevance.* Independent evidence for the `context*decode` interaction term in
the residual design and for output-length control as the dominant lever.

**S39. Fernandez, J., Na, C., Tiwari, V., Bisk, Y., Luccioni, S., Strubell, E.
"Energy Considerations of Large Language Model Inference and Efficiency
Optimizations." ACL 2025 long, pp. 32556-32569; arXiv 2504.17674.** OPENED.
<https://arxiv.org/abs/2504.17674>
Optimisations cut energy up to 73%; effects highly sensitive to workload
geometry, stack and hardware; FLOP-based estimates substantially underestimate
real energy.
*Relevance.* The peer-reviewed warning against modelled energy; supports
JouleWise's measured-only stance and its refusal to extrapolate across hosts.

**S40. Chung, J.-W. et al. "The ML.ENERGY Benchmark: Toward Automated Inference
Energy Measurement and Optimization." arXiv 2505.06371, 2025 (NeurIPS 2025 D&B
spotlight).** OPENED (already cited). <https://arxiv.org/abs/2505.06371>
40 architectures, 6 tasks, public leaderboard; optimisation recommendations
save sometimes >40%.
*Relevance.* Datacenter GPU scope; no Apple silicon, no detection floor.

**S41. Patel, P. et al. "Splitwise: Efficient Generative LLM Inference Using
Phase Splitting." ISCA 2024, pp. 118-132; arXiv 2311.18677.** OPENED.
<https://arxiv.org/abs/2311.18677>
Prefill compute-bound, decode memory-bound with distinct power profiles; split
across machines for 1.4x throughput at 20% lower cost.
*Relevance.* The canonical phase-split characterisation; cite when defining
why JouleWise reports prefill and decode separately and why the prefill probe
exists.

**S42. Dauner, M., Socher, G. "Energy costs of communicating with AI." Frontiers
in Communication 10, 2025. DOI 10.3389/fcomm.2025.1572947.** OPENED (full
text). <https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1572947/full>
A100 80 GB, Perun framework, 14 models 7-72B on 1,000 MMLU items; reasoning
variants add about 543 thinking tokens per multiple-choice item versus 38
response tokens; reasoning modes 4-6x the emissions in free response; results
hardware-specific.
*Relevance.* The measured baseline for "hidden thinking dominates energy",
with Qwen and DeepSeek-R1 variants close to JouleWise's model family. Note this
Dauner is not the Dauner cited at `draft-v1.md:326` for counter-update
behaviour; check the bibliography for a name collision.

**S43. Jin, Y., Wei, G.-Y., Brooks, D. "The Energy Cost of Reasoning: Analyzing
Energy Usage in LLMs with Test-time Compute." arXiv 2505.14733, 2025.** OPENED.
<https://arxiv.org/abs/2505.14733>
Test-time compute beats model scaling on accuracy per energy, mostly on complex
reasoning; interaction with output length; match compute to query complexity.
*Relevance.* Frames RQ-ALIGN-EFFICIENCY-MONITORABILITY's "inference-time
budget" axis in energy terms; hardware and tool not in the abstract.

**S44. Wilhelm, P., Wittkopp, T., Kao, O. "Beyond Test-Time Compute Strategies:
Advocating Energy-per-Token in LLM Inference." EuroMLSys 2025; arXiv
2603.20224.** OPENED. <https://arxiv.org/abs/2603.20224>
Argues for energy-per-token beside accuracy; nonlinear energy curves from
input/output token dynamics; energy-aware routing.
*Relevance.* Metric-advocacy paper; JouleWise's per-phase token denominators
are the concrete form.

**S45. Oviedo, F. et al. (Microsoft). "Energy Use of AI Inference, Efficiency
Pathways, and Test-Time Scaling." arXiv 2509.20241, 2025; Joule 2026,
102430.** OPENED. <https://arxiv.org/abs/2509.20241>
Bottom-up model (not measurement): median 0.31 Wh per frontier query on H100
nodes; 15x longer test-time-scaling queries raise it about 13x to 3.91 Wh.
*Relevance.* Modelled, so it is the kind of estimate S39 warns about; cite
only to position JouleWise as measured and on-device.

**S46. Elsworth, C. et al. (Google). "Measuring the environmental impact of
delivering AI at Google Scale." arXiv 2508.15734, 2025.** OPENED.
<https://arxiv.org/abs/2508.15734>
Boundary includes accelerator, host CPU/DRAM, idle provisioned capacity and
datacenter overhead; median Gemini Apps text prompt 0.24 Wh.
*Relevance.* The clearest industrial statement that boundary choice moves the
number by more than 2x; supports JouleWise's gross-energy headline and named
boundary (`README.md:63`).

**S47. Jegham, N., Abdelatti, M., Koh, C. Y., Elmoubarki, L., Hendawi, A. "How
Hungry is AI? Benchmarking Energy, Water, and Carbon Footprint of LLM
Inference." arXiv 2505.09598, 2025 (v6 Nov 2025).** OPENED.
<https://arxiv.org/abs/2505.09598>
Estimated (API latency plus inferred hardware and multipliers), 30 models;
most energy-intensive exceed 29 Wh per long prompt.
*Relevance.* Estimate-based; cite as contrast only.

**S48. Argerich, M. F., Patiño-Martínez, M. "Measuring and Improving the Energy
Efficiency of Large Language Models Inference." IEEE Access 12, pp.
80194-80207, 2024. DOI 10.1109/ACCESS.2024.3409745.** UNVERIFIED (DOAJ and
UPM portal returned 403 or a loading stub). <https://doi.org/10.1109/ACCESS.2024.3409745>
Search record: profiles inference energy and tunes batch size and quantization.
*Relevance.* Possibly relevant to the quantization contrast; re-open.

## 4. Measurement methodology, preregistration and blinding

**S49. Nosek, B. A., Ebersole, C. R., DeHaven, A. C., Mellor, D. T. "The
preregistration revolution." PNAS 115(11), pp. 2600-2606, 2018. DOI
10.1073/pnas.1708274114.** OPENED (PMC full text).
<https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500>
Prediction versus postdiction; preregistration on preexisting data is only
pure if no one has observed the data; deviations are acceptable if transparent;
tools include staged preregistration, blinding the dataset, decision trees and
SOPs.
*Relevance.* The canonical citation for JouleWise's "rules sealed before data
exist" and for its public deviation log (amendment under a second seal,
`README.md:19`). Its "indirect exposure" warning is exactly why the desk program
never reads an energy.

**S50. Hofman, J. M., Chatzimparmpas, A., Sharma, A., Watts, D. J., Hullman, J.
"Pre-registration for Predictive Modeling." arXiv 2311.18807, 2023.** OPENED.
<https://arxiv.org/abs/2311.18807>
Adapts preregistration to predictive modelling with a lightweight template and
a qualitative study of ML researchers.
*Relevance.* Shows the ML preregistration literature targets model-evaluation
degrees of freedom; systems-measurement preregistration (what to measure, which
checks remove a session, how to analyse) is not its subject. JouleWise is an
instance in that unoccupied space.

**S51. Søgaard, A., Hershcovich, D., de Lhoneux, M. "A Two-Sided Discussion of
Preregistration of NLP Research." 2023 (arXiv 2302.10086).** UNVERIFIED (not
opened; search record only). <https://arxiv.org/abs/2302.10086>
Pros and cons of preregistration in NLP; must allow reclassification as
exploratory.
*Relevance.* Supports JouleWise's explicit exploratory/claim split ("pilot
tests no hypothesis").

**S52. Khiani, R. "Blinding the AI Co-Scientist: Mechanical Pre-Commitment for
AI-Assisted Empirical Research." Poster, NeurIPS 2026 Workshop on AI-Native
Academia.** OPENED. <https://neurips.cc/virtual/2026/166242>
Hash-frozen registration with dated append-only amendments; structural
blindness (estimator package has no loader for real data); two-seat review (the
component that produced an artifact cannot certify it); a finance deployment
where the admission gate refused the headline analysis twice; closing rule that
claim checks run from the reader's vantage.
*Relevance.* The nearest published description of JouleWise's own governance
pattern (sealed rules, desk program blind to energies, independent reviewer,
refusals kept and disclosed) and the only one framed for AI-assisted research.
Cite as the mechanical-precommitment neighbour; the paper should state how
JouleWise's instance differs (physical measurement, detection floor, cold
reviewer per macOS build). See Open questions on provenance.

**S53. MacCoun, R., Perlmutter, S. "Blind analysis: Hide results to seek the
truth." Nature 526, pp. 187-189, 2015.** PARTIAL (Nature redirected to a
login wall; summary from Berkeley News coverage, opened).
<https://www.nature.com/articles/526187a>;
<https://news.berkeley.edu/2015/10/08/blind-analysis-could-reduce-bias-in-social-science-research/>
Argues biology, psychology and social science adopt particle-physics blind
analysis; techniques: hide or shift data values by a hidden amount until the
analysis is debugged; randomise group labels.
*Relevance.* The general-audience anchor for "analysis code written and
reviewed before the measured energies are opened" (`README.md:19`).

**S54. Klein, J. R., Roodman, A. "Blind Analysis in Nuclear and Particle
Physics." Annual Review of Nuclear and Particle Science 55, pp. 141-163, 2005.
DOI 10.1146/annurev.nucl.55.090704.151521.** PARTIAL (PDF fetched; text layer
not extractable in this environment; metadata confirmed).
<https://www.gwern.net/doc/statistics/bias/2005-klein.pdf>
Hidden signal box, hidden offset, hidden answer, prescription method.
*Relevance.* The discipline-of-origin review; JouleWise's "nobody has looked at
a measured energy yet" is a hidden-signal-box design.

**S55. Hoefler, T., Belli, R. "Scientific Benchmarking of Parallel Computing
Systems: Twelve Ways to Tell the Masses when Reporting Performance Results."
SC15, ACM. DOI 10.1145/2807591.2807644.** OPENED (abstract record).
<https://evaluate.inf.usi.ch/node/366>
120-paper survey: often unclear whether improvements are in the noise; twelve
reporting rules and a benchmarking library.
*Relevance.* Complements Georges et al. and Mytkowicz already cited; cite for
"report whether the difference clears the noise", which is what the detection
floor operationalises.

**S56. Mytkowicz, T., Diwan, A., Hauswirth, M., Sweeney, P. F. "Producing Wrong
Data Without Doing Anything Obviously Wrong!" ASPLOS 2009.** Already cited at
`draft-v1.md:392`; not re-opened. No change.

## 5. Gaps JouleWise fills (and the sources that bound each claim)

1. **Validated, phase-resolved `powermetrics` energy on Apple silicon.** Apple
   calls the numbers estimates (S1); the two Apple-silicon energy papers found
   (S3, S4) use the tool without any timing calibration, repeat protocol, idle
   baseline, thermal gating or external cross-check, and S4's headline package
   power appears internally inconsistent. No source characterises where the
   sampler places energy in time. JouleWise's timing calibration per macOS
   build, cold-reviewed, is unoccupied ground. Claim boundary: JouleWise still
   lacks an independent counter cross-check (S37 has one; `draft-v1.md:330`),
   and the vendor caveat forbids cross-device ranking.

2. **Sampler coverage as a gate (the prefill probe).** The GPU literature shows
   under-sampled phases produce wrong energy (S8); the consumer-GPU and edge
   papers sample at 2 Hz or do not say (S10-S12). No source sets a minimum
   workload length from measured sampler overlap before measuring a phase.

3. **Battery and thermal state as admission criteria.** S9 and S10 show thermal
   and battery policy move the operating point within seconds on Apple mobile
   silicon; no LLM-energy paper found makes battery-floating, no-charging and a
   thermal flag per member a precondition with refusal. JouleWise does
   (`README.md:23`).

4. **Energy as an agent-monitoring signal.** The monitoring literature measures
   text (S14, S16, S17, S24-S26) and prices oversight in dollars (S23) or
   usefulness (S19, S20, S22); the agent-energy literature measures joules on
   NVIDIA/x86 with no monitoring question (S27-S30); the side-channel
   literature infers token counts from timing and packets, not power (S32). No
   source found asks whether energy beyond what logged tokens predict flags
   hidden or deleted work, or reports a joule-per-catch frontier. Both
   RQ-ALIGN-ENERGY-RESIDUAL and RQ-ALIGN-EFFICIENCY-MONITORABILITY are
   unoccupied. Claim boundary: the ALIGN pilot is a non-claim instrument check
   (`pilot_protocol_v0.md:3-5`), and S25's obfuscation result implies any
   energy-based monitor is also a target for optimisation pressure once known.

5. **Per-turn, per-tool energy attribution on a laptop SoC with uncertainty.**
   S27 attributes per workflow layer on servers; S13 regresses whole requests;
   S28 shows non-GPU energy is 41-45% of agent energy, which on an SoC is
   inseparable and therefore argues for JouleWise's gross boundary. No source
   attributes energy per turn on Apple silicon with half-widths and a tiling
   check (I3, `pilot_protocol_v0.md:72`).

6. **Preregistration and blinding applied to systems measurement.** The ML
   preregistration work targets predictive modelling (S50, S51); blind analysis
   is a physics practice (S53, S54); mechanical precommitment is described for
   AI-assisted econometrics (S52). No LLM-energy paper found seals its removal
   rules before data, keeps and discloses refused sessions, or blinds its desk
   program to outcomes. JouleWise's Block-5 procedure (`README.md:19`) is a
   concrete systems-measurement instance; S52 is the paper to cite as the
   nearest pattern and to differentiate from.

7. **Reasoning-token energy on-device.** S42, S43 and S12 show hidden thinking
   dominates per-answer energy on A100 or a consumer GPU; none measures it on
   Apple silicon or ties it to the chat template's hidden-token accounting
   (`apple_path.md:91-109`). The open choice "Qwen3 thinking on or off"
   (`pilot_protocol_v0.md:137`) is therefore also a literature gap.

## 6. Suggested placement in the paper

- `draft-v1.md` §8 "From counter gain to counter time": add S1 (vendor caveat)
  and S8 (sampler coverage) beside Hähnel.
- §8 "LLM energy measurement": add S4 as nearest Apple-silicon neighbour with
  the channel-consistency caveat; add S36 and S38 for the quantization and
  context-interaction priors; add S46 for boundary choice.
- New §8 paragraph for Paper 2 (agent monitoring): S14, S19, S23, S25, S26,
  S27, S28, S32, in that order, ending on the gap in item 4 above.
- §8 "Benchmark and metrology lineage": add S49, S52, S53/S54, S55.
- Bibliography hygiene: two different "Dauner" citations now exist (S42 vs the
  counter-update paper at `draft-v1.md:326` [23]); confirm [23]'s full record.

## 7. Could not open / verify

- S6 preprints.org 202605.0855 (403).
- S48 Argerich and Patiño-Martínez (DOAJ 403; UPM portal loading stub).
- S51 Søgaard et al. (not attempted beyond search).
- S53 Nature full text (login redirect); S54 PDF text layer (no poppler/pypdf
  on this host).
- Hoefler and Belli's own site (TLS certificate mismatch); record taken from the
  USI evaluate database instead.
- `docs/align/pilot_protocol_v4.md`: not present on any fetched branch.

## 8. Open questions

1. Where is `pilot_protocol_v4.md`? If it exists only on the measurement Mac or
   an unpushed branch, this review used v0 (`cbfb9b0a5`) and should be
   re-checked against v4's task list and budgets.
2. S52 (Khiani, NeurIPS 2026 workshop) describes hash-frozen registration,
   structural blindness and two-seat review that match JouleWise's practice
   closely. Is it independent prior art, or is there any connection to this
   project? The answer decides whether it is cited as neighbour or as source.
3. S4's 0.47 W package figure: worth one controlled check on the analysis Air
   (not the measurement Mac) of what `powermetrics` reports as "package" versus
   `gpu_power` under MLX decode, so the paper's critique is grounded rather than
   inferred.
4. For RQ-ALIGN-ENERGY-RESIDUAL, S17's sandbagging threat predicts a negative
   residual; the design doc frames hidden work as positive residual. Should the
   preregistered test be two-sided?
5. Should the ALIGN runner adopt ControlArena (S21) settings for a later block,
   given its Inspect sandbox conflicts with the "no agent process on the Mac"
   rule?
