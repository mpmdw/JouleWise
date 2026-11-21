# Open-source contributions from JouleWise: a ranked shortlist

Date: 2026-11-05. Prepared by an Opus 5.5 research subagent for Ed. This document is research only: nothing was posted, filed, commented or opened upstream.

**Purpose.** Find the open-source contributions that best fit JouleWise's work and are worth the most to Ed, an undergraduate building a reputation in local LLMs and ML systems.

**Method.**
- Each candidate was checked against upstream `main` with `gh api` and GitHub search on 2026-11-05.
- Two parallel surveys (energy tooling; agent safety / transformers / llama.cpp) were spot-checked against source before being used here.
- JouleWise evidence is cited by branch and path.

**Excluded, handled elsewhere:**
- the mlx-vlm `qwen4_exp` ragged-batch QSA bug (D1);
- the `qwen4_exp` MLX port itself;
- the MLX `mx.fast.rope` batch-offset bug, already fixed in MLX #3494, #3795 and #3949.

## Ground rules that apply to every item

1. **Ed writes every word that a human reads upstream.** These projects forbid AI-written posts (issues, PR descriptions, replies): mlx-lm, llama.cpp and transformers. transformers also asks first-time contributors not to use code agents to create issues or PRs. Zeus closes "meat proxy" PRs and closed #274 for it. AI-written *code* is allowed in most of them, but only if it is disclosed and Ed can defend every line. This file therefore gives facts, evidence and first steps, and deliberately contains **no draft issue or PR text**.
2. **Custody.**
   - Do not publish any number from block 5 before its release (planned 8 Nov), from block 6, from BYTES held-out rows, or any ALIGN result about energy as a monitor signal before the paper.
   - Every item below can run on git-tracked fixtures, synthetic or tiny-config repros, or a fresh, unregistered desk capture.
   - Where an item needs measured energy, the custody check is listed under its prerequisites.
3. **Machines.** The M4 Air is the analysis box. The measurement Mac (Mac15,9, macOS 15.7.7) is reserved. Items that need it say so.
4. **New-contributor limits.** llama.cpp allows a new contributor at most one open PR, and no trivial fixes. Inspect AI auto-closes PRs from non-qualified contributors unless a maintainer has marked the issue `accepted`. Order the work accordingly.

## Ranked top 8

| # | Contribution | Where | Effort (Ed) | Why it ranks here |
|---|---|---|---|---|
| 1 | Pass past reasoning back to Qwen3.5/3.6/3.8 chat templates | ml-explore/mlx-lm (server) | 1–2 days | Unreported. It affects every multi-turn agent loop on the most popular local hybrid models. The fix is small and the test is crisp. |
| 2 | Accept transformers' `indexed_attention` layer type in llama.cpp's converter and mlx-vlm's loader | ggml-org/llama.cpp, Neywa-Labs/mlx-vlm | 1 day + 2 h | A real conversion bug: llama.cpp drops the sparse-attention setting without warning, and mlx-vlm refuses to load. Every fine-tuned Flash-Next checkpoint is affected. The patch and repro already exist. |
| 3 | Fix KM003C sample re-delivery being counted twice | okhsunrog/km003c-rs (+ protocol-research docs) | 3–4 h | Unique to Ed's instrument work, and backed by a recorded fixture. It earns a measurement-integrity reputation cheaply. |
| 4 | Validate SMC DC-in, system and battery power against a USB-C meter | vladkens/macmon PR #118, metaspartan/mactop | 3 h (+ desk capture if needed) | Timely: the PR is open with 0 comments, and the maintainers ask for an independent reference. The tools have about 2k stars. |
| 5 | Compare Apple Silicon IOReport energy against measured whole-machine energy; add M3 Max support | ml-energy/zeus-apple-silicon, ml-energy/zeus | 1–2 days | High value for a researcher's reputation with the ML.ENERGY group. The README itself flags its numbers as unvalidated. |
| 6 | **Flagship:** a meter-validated, rootless Apple Silicon power backend | mlco2/codecarbon | 1 day issue, then 2–3 weeks PR | Today CodeCarbon does not count the Mac GPU at all. The maintainers ask for exactly this, and it has the largest user reach of anything here. |
| 7 | `inspect-energy` hooks extension, plus `sample_id` in `ModelUsageData` | UKGovernmentBEIS/inspect_ai (+ Ed's own package) | 3–5 days | Gives visibility with UK AISI's eval/safety community. No energy extension exists, and listing one is a one-line PR. |
| 8 | Stable tie-break for the QSA indexer top-k, raised during the indexer rework | huggingface/transformers | 1–2 days | Timely: the maintainers said on 2026-11-03 that they "need to rethink the indexer completely". The real-weight parity work supplies the evidence. |

---

### 1. mlx-lm server: give past reasoning back to Qwen3.5/3.6/3.8 templates

**Pitch.** `mlx_lm.server` returns a model's thinking as `message.reasoning`. Clients send that message back with the next request; Inspect AI, for example, replays reasoning under the field name it arrived with. The server never maps it to `reasoning_content`, which is the only field these chat templates read.

- **Qwen3.8:** preserves thinking by default (`preserve_thinking` undefined means preserve).
- **Qwen3.5 / 3.6:** render thinking for every assistant turn inside the current tool chain. They read `reasoning_content` or a `</think>` in the content, but the server has already split reasoning out of the content.

So every earlier turn in an agent tool chain is re-rendered with an empty `<think>\n\n</think>`. That causes two problems:

1. **The model loses its own earlier reasoning,** which the template is built to keep, so the prompt drifts off-distribution.
2. **The prompt no longer extends the cache the server stored after generation.** Hybrid Gated DeltaNet caches cannot be trimmed, so every turn falls back to an older segment entry and re-prefills.

JouleWise measured this round trip byte for byte with the real templates:

| History sent back | Bytes of the previous prompt invalidated |
|---|---|
| Content only | 119 per tool-chain turn; 37 per user turn |
| Reasoning split into `reasoning_content` | 0 over six turns |

**The fix is small.** On incoming assistant messages, copy `reasoning` into `reasoning_content` when only the former is present, inside `process_message_content`. The regression test renders a two-turn tool chain through a Qwen3.5-style template and asserts that turn 2's prompt starts with turn 1's prompt plus its generation.

**Upstream state (verified):**
- **Not reported, not fixed.**
- `server.py` on main emits `choice[...]["reasoning"]` (around line 1527).
- `process_message_content` (around line 212) touches only `content` and `tool_calls.arguments`.
- A code search for `reasoning_content` in mlx-lm finds only the custom `chat_templates/deepseek_v32.py`.
- Related but different: #1841 (K2 reasoning history, closed), #1011 (Qwen3.5 multi-turn tools, closed).
- The server already stores the post-generation cache (`insert_cache(..., cache_type="assistant")`), so the fix turns a fallback into a hit.

**Contribution rules.** [CONTRIBUTING](https://github.com/ml-explore/mlx-lm/blob/main/CONTRIBUTING.md):
- AI code is allowed if disclosed; AI-written posts are strictly prohibited.
- The new test must fail on main.
- Run `uvx pre-commit run --all`.
- No CLA.

**First step.** Reproduce against mlx-lm main (any small Qwen3.5 checkpoint, e.g. Qwen3.5-0.8B):
1. Run two chat turns with a tool call through the OpenAI client, sending back `response.choices[0].message` as returned.
2. Log the rendered prompt and the cache hit length.
3. Open a short issue in Ed's own words, then the PR.

**What Ed must understand to defend it:**
- the server's segment cache (system/user/assistant entries in `LRUPromptCache`);
- why `ArraysCache` cannot be trimmed;
- the template's `last_query_index` / `preserve_thinking` logic;
- why mapping to an existing field name beats rewriting templates.

**Risks.**
- Clients that send both fields: prefer `reasoning_content` and do not overwrite it.
- Templates for other model families: the fix is harmless when a template ignores the field.

**Evidence:**
- Lane `lane/2026-11-05-align-xml-toolcalls` (JouleWise PR #659): `docs/run_reports/2026-11-05-align-reasoning-history.md` (the six-turn table) and `tests/align/test_xml_tool_calls.py::test_both_real_templates_replay_six_split_assistant_turns`.
- Template fixture `tests/align/fixtures/qwen38_chat_template.jinja`, lines 111–117.
- Qwen/Qwen3.5-35B-A3B and Qwen3.6-35B-A3B `chat_template.jinja` on the Hub, lines 90–101.

### 2. `indexed_attention`: llama.cpp converter (no warning) and mlx-vlm loader (refuses to load)

**Pitch.** transformers [#48974](https://github.com/huggingface/transformers/pull/48974) (merged 2026-09-22) deliberately remaps layer-type names when a config is loaded:

| Old name | New name |
|---|---|
| `full_attention` (in Qwen4-Exp) | `indexed_attention` |
| `deepseek_sparse_attention`, `qwen_sparse_attention` | `indexed_attention` |
| `mamba` | `linear_attention` |
| `attention` | `full_attention` |

`save_pretrained` then writes the new names. So every Flash-Next checkpoint that goes through transformers carries `indexed_attention`: Unsloth or PEFT fine-tunes, merges, re-shards and tiny test models. Two downstream consumers mishandle it:

- **llama.cpp converter (no warning).** `conversion/qwen4exp.py` (lines 84–90) writes `ratio if layer_types[i] == "full_attention" else 0`. A re-saved checkpoint therefore converts with compress ratio 0 on every main-model QSA layer, and only the MTP layer keeps its ratio. The sparse-attention setting is silently dropped.
- **mlx-vlm loader (refuses).** `mlx_vlm/models/qwen4_exp/config.py` raises `Unsupported Qwen4-Exp layer types: {'indexed_attention'}`. Once that is fixed, it also rejects transformers' default `output_gate_type=None`.

vLLM already accepts both names (#59756, closed 2026-10-04). mlx-lm PR #1788 matches only `full_attention`; that is part of the excluded port, so a review comment there is enough.

**Upstream state:** nobody has reported either consumer bug (searched both repos for `indexed_attention`).

**Contribution rules:**
- **llama.cpp:** AI-written issues, PRs and comments are prohibited, and undisclosed AI code can get an account banned. A bug fix needs a reproducible issue and a regression test that fails before the fix. A new contributor may have only one open PR. No CLA.
- **mlx-vlm:** black/clang-format hooks; no AI policy or CLA found.

**First steps:**
- **mlx-vlm (fastest, about 2 h):** open a PR with the ready patch `scripts/audit_mlxvlm/f1_indexed_attention_layer_type.patch` and a test built from `repro_f1_indexed_attention.py`. **Coordinate with whoever is filing D1**, so mlx-vlm sees one coherent contributor. Send P5 (`p5_padded_no_cache.patch`: a padded batch scored without a cache ignores the mask) separately.
- **llama.cpp:** file a reproducible issue: a tiny transformers-re-saved config, the converted GGUF's `attention.compress_ratios` all 0, and the expected values. Then a one-line PR with a converter test that accepts `indexed_attention` and the legacy names vLLM accepts.
- **Optional:** grep the other llama.cpp `conversion/*.py` and mlx-lm `models/*.py` for hard-coded `mamba` and `*_sparse_attention` comparisons against `layer_types`. The same remap affects DSA and Mamba-hybrid fine-tunes.

**Effort:** about 1 day for llama.cpp (issue, PR, test); 2 h for mlx-vlm.

**What Ed must understand:** the transformers config life cycle (`__post_init__` remap, then save); the GGUF `compress_ratios` key and what ratio 0 means at runtime. Confirm the latter before claiming silent dense attention: it may instead fail at load. Either outcome is a bug.

**Risks:** low. llama.cpp's new-contributor limits mean this should be Ed's first llama.cpp PR.

**Evidence:** `docs/align/qwen4_exp_port/audit_mlx_vlm_numerical.md` (findings F1 and P5, with validation numbers); the patches and repros in `scripts/audit_mlxvlm/`.

### 3. km003c-rs: sample re-delivery is integrated twice

**Pitch.** The most-used open KM003C library ([okhsunrog/km003c-rs](https://github.com/okhsunrog/km003c-rs): Rust, Python wheel `km003c`, GUIs) handles the 16-bit sequence wrap and rejects duplicate samples. `MeasurementAccumulator::push` in `km003c-lib/src/measurement.rs` (around lines 104–160) behaves as follows:

- After `MAX_CONSECUTIVE_REJECTED_SAMPLES = 8` rejects in a row, it sets `previous = None`. The intent is to survive a long stall.
- A re-delivery longer than 8 samples therefore restarts continuity *inside* the re-sent block.

Trace a 27-sample re-delivery at 1000 SPS, which JouleWise recorded:

1. Samples 74–81 are rejected.
2. Sample 82 is accepted with delta 0.
3. Samples 83–100 are integrated a second time: 18 intervals of energy and elapsed time.

So `elapsed_us` and energy are inflated, and `cumulative_discarded` reports 8, not 27. This was confirmed by reading the code; Ed must reproduce it with a failing `#[test]` before filing.

**The fix direction** is the one JouleWise uses: decide "long stall" vs "re-delivery" from host arrival time (more than about half a wrap, 32 s), not from a reject count.

**Follow-up:** a docs PR to [okhsunrog/km003c-protocol-research](https://github.com/okhsunrog/km003c-protocol-research). Its `adcqueue.md` does not mention re-delivery, and its dropped-sample snippet turns a backward step into about 65k "dropped" samples. Add the meter-clock-rate fit as well.

**Upstream state:** not reported.
- The maintainer responds in 2–3 days and tends to re-implement fixes himself, crediting the reporter (#62→#65).
- No CONTRIBUTING, no AI policy, no CLA.

**First step:** write the failing test against `MeasurementAccumulator` from the sequence numbers in `tests/fixtures/km003c/redelivery1000_slice.jsonl`, then file the issue.

**Effort:** 3–4 h (Rust test plus issue); about 1 day for a fix PR if wanted.

**What Ed must understand:** the AdcQueue sample layout; why a backward step through `wrapping_sub` looks like a huge forward step; the host-time disambiguation rule.

**Risks:** low visibility (25 stars). The value is credibility: it shows Ed's instrument has been audited down to the protocol.

**Evidence:**
- `joulewise/external/km003c_parse.py` (docstring: device time, re-delivery, clock fit);
- `tests/external/test_km003c_parse.py` (`test_recorded_re_delivery_is_dropped_and_counted`, `test_plain50_slice_unwraps_across_the_16_bit_wrap`, `test_stall_longer_than_half_a_wrap_uses_host_time`);
- `tests/fixtures/km003c/provenance.json` (desk and probe recordings, not claim data).

### 4. macmon / mactop: validate SMC DC-in, system and battery power against a meter

**Pitch.** [macmon PR #118](https://github.com/vladkens/macmon/pull/118) (opened 2026-11-02, 0 comments) adds:
- `dc_in_power` from SMC PDTR;
- `battery_power` from PPBR;
- display power;
- DRAM in `all_power`.

macmon's `agents.md` requires mappings to be verified "against an independent reference under separate component loads". Ed has exactly that reference: a KM003C on the DC input plus battery correction from B0AC×B0AV. JouleWise PR #565 already fitted a PDTR-on-meter slope.

**The contribution** is a short validation table posted on #118: slope, offset and lag of PDTR, PSTR and PPBR against the meter across idle, CPU-only, GPU-only and LLM-decode loads, with chip and macOS version stated. Reuse it as an issue on [mactop](https://github.com/metaspartan/mactop), which also reads PSTR/PDTR (its #94 showed 20 kW spikes).

**Upstream state.**
- Not done. macmon's owner often closes external *code* PRs and re-implements them (#77, #71, #40, #32), so a data comment is the right form.
- macOS 27 context: rootless IOReport "Energy Model" counters stop updating without a private entitlement (macmon README, "Power sources and macOS 27").
- This makes SMC power, which the PR adds, more important.

**First step.**
1. **Confirm custody of PR #565's sources.** The slope pools 12 sessions (`capture/verify-capture-C2/blind_slope.py`). If any is a block-5 or block-6 session, do not reuse it.
2. Otherwise, or as well, take a fresh unregistered desk capture: about 30 min on the measurement Mac while ALIGN is paused, with `scripts/km003c_monitor.py` plus SMC polling.
3. Post the table in Ed's own words.

**Effort:** about 3 h with existing data; plus a half-day desk session for a fresh capture.

**What Ed must understand:** what PDTR, PSTR and PPBR measure (adapter input vs system vs battery); why the meter needs the battery term; lag estimation.

**Risks:** low. SMC key meanings vary by chip, so do not generalize beyond Mac15,9 and the M4.

**Evidence:**
- `joulewise/external/km003c_parse.py` (battery term, rho);
- JouleWise PR #565 (merge `dbba9897c`, "Meter cross-check: PDTR-on-meter slope …");
- `scripts/km003c_monitor.py`;
- SMC enumeration on lane `lane/2026-11-05-align-smc-thermal`: `joulewise/hazards/smc_enumeration.py`, `docs/align/smc_temperature.md`.

### 5. Zeus / zeus-apple-silicon: validate on-chip energy against measured whole-machine energy; add M3 Max

**Pitch.** [zeus-apple-silicon](https://github.com/ml-energy/zeus-apple-silicon) reads IOReport "Energy Model" counters for CPU, GPU, ANE and DRAM, with no sudo. Its README says the values are "believed to be model-based estimates" and offers no validation. Its tested chips list M1 Max, M3 Pro, M4, M4 Pro and M5 Max, but **not the M3 Max**. It also has an explicit "adding a new chip" guide (dump_channels → check_compatibility → mock test).

Ed can contribute two things:
1. **An evidence issue.** For one LLM run, compare the IOReport rail energy over the prefill and decode windows against KM003C whole-machine energy (rho). Add a note on phase-boundary resolvability: Paper 1's diagnostic-era result is that boundary uncertainty during a steep power change can move about 1 J between phases.
2. **A small PR** adding the M3 Max channel dump and mock test case.

**Upstream state.**
- Not done. zeus-apple-silicon was last pushed 2026-04-02, and nothing mentions macOS 27.
- Zeus maintainers merge external PRs quickly; several merged the same day.
- They also closed #274 under their AI ("meat proxy") policy.
- A machine-level `zeus.device.machine` was endorsed in [#273](https://github.com/ml-energy/zeus/issues/273) but is still unbuilt. A USB-PD meter backend there is a later, higher-risk option.
- Contribution rules: open an issue first; tests; `scripts/lint.sh`; strict typing; Apache-2.0; no CLA.

**First step.** On the measurement Mac (macOS 15.7.7):
1. Run `dump_channels` and `check_compatibility`.
2. Wrap one fresh, unregistered decode run in `AppleEnergyMonitor` windows next to the meter.
3. Write a 10–15 line issue himself.

**Effort:** 1 day (issue) + 2–4 h (test PR).

**What Ed must understand:** IOReport delta counters vs powermetrics intervals; what rails exclude (display, SSD, fans, conversion losses); the rho computation; why short windows are not resolvable.

**Risks:** the Zeus maintainers strictly enforce the human-authorship rule. Keep it short and personal.

**Evidence:**
- `joulewise/external/km003c_parse.py` (rho, `integrate`);
- `joulewise/adapters/powermetrics.py`;
- `docs/paper/draft-v1.md` (abstract and section 1: the ~1 J boundary-attribution scale and the fewer-than-three-records resolvability rule).

### 6. FLAGSHIP: CodeCarbon, a meter-validated, rootless Apple Silicon power backend

**Pitch.** CodeCarbon (about 1.9k stars, cited in countless ML papers) is the default way researchers report training and inference energy. On Apple Silicon it is badly wrong, and its own docs say so:
- Its docs (`docs/explanation/methodology.md`) say "On Apple Silicon, `powermetrics` is effectively unreachable" and ask anyone who knows a sudo-less method to open an issue.
- Since commit 473351b2e (PR #1252), `cpu_load` mode wins whenever psutil is present.
- GPU tracking covers only NVIDIA and ROCm, so **the Mac GPU, which carries most LLM energy, is not counted.**
- The old powermetrics path takes a ~1 s CPU+GPU snapshot and multiplies it across the 15 s interval.
- Issue [#731](https://github.com/mlco2/codecarbon/issues/731) ("Sudoless power metrics on Apple Silicon") is open with an abandoned branch. [#1269](https://github.com/mlco2/codecarbon/issues/1269) (battery or whole-machine backend) has an unclaimed macOS part.

**The flagship has two stages:**
1. **Quantify the undercount.** For one LLM decode workload, compare CodeCarbon's default Mac estimate with KM003C whole-machine energy and with IOReport rails. Post the table on #731.
2. **Build the backend.** A rootless backend that reads IOReport rails (CPU/GPU/ANE/DRAM) where they still update, with stall detection for macOS 27. Add SMC system power (PSTR/PDTR) as the whole-machine number. Validate both against the meter.

Reuse an existing reader (the `zeus-apple-silicon` extra, or a small ctypes IOReport/SMC reader) to satisfy their "no reinvented helpers" rule.

**Why it is the flagship:**
- It turns JouleWise's core competence (measured truth vs instrument estimates) into a tool thousands of people run.
- It has documented demand from the maintainers.
- It produces a public validation table that will also seed the measured-energy dataset (see "Bigger flagship" below).
- A natural follow-on: once a validated reader exists, an `--energy` J/token column for `mlx_lm.benchmark` becomes a small, defensible mlx-lm PR. Today `benchmark.py` reports only `prompt_tps`, `generation_tps` and `peak_memory`, and no energy issue exists. Propose it by issue first.

**Contribution rules** ([AI_POLICY.md](https://github.com/mlco2/codecarbon/blob/master/AI_POLICY.md)):
- Pick an honest disclosure tier (vibecoded / AI-generated / AI-assisted / none).
- Test locally, reuse helpers, and be able to explain every line.
- No CLA. Release v3.3.2 shipped 2026-10-23, and external PRs merge in 1–7 days.

**Effort:** 1 day for the #731 data comment; 2–3 weeks for the backend, tests and docs.

**Prerequisites:**
- Understand IOReport, SMC and powermetrics, and the macOS 27 entitlement change (macmon README).
- Understand how CodeCarbon's `measure_power_secs` integration works.
- Use fresh, unregistered captures only.
- Machine time: the measurement Mac on macOS 15, plus ideally any macOS 27 Mac to confirm stall detection.

**Risks:**
- macOS 27 may remove more rootless counters.
- The maintainers may prefer a CLI subprocess (macmon) to a native reader. Ask in the #731 comment.
- Scope creep: keep #1269's battery path separate.

**Evidence:** the same as items 4 and 5, plus Paper 1's framing (`docs/paper/draft-v1.md`).

### 7. Inspect AI: an `inspect-energy` hooks extension

**Pitch.** Inspect has a Hooks API with `on_sample_start/end`, `on_before_model_generate` (which carries `sample_id`) and `on_model_usage`. It has no energy or carbon extension; the closest analogue is the "Inspect Costs Plugin".

**The contribution:** Ed's own package that records per-sample and per-generate Joules on Apple Silicon into a sidecar keyed by `sample_id`. It would use the validated reader from item 6, or server-reported telemetry.

Two small upstream pieces go with it:
- A one-line PR listing the package in `docs/extensions/extensions.yml`.
- A hand-written core issue asking for `sample_id` in `ModelUsageData`. It is missing today (`src/inspect_ai/hooks/_hooks.py`, lines 246–267), which blocks per-sample attribution of model calls.

This is the energy-meets-evals contribution, and it puts Ed in front of the UK AISI / ControlArena community without publishing any ALIGN result.

**Upstream state.**
- Issue [#6246](https://github.com/UKGovernmentBEIS/inspect_ai/issues/6246) (2026-11-02) proposes an mlx-lm provider recipe. Support it there rather than duplicating it, and mention item 1's reasoning caveat.
- Rules: issue-first; non-qualified contributors' PRs need an `accepted` issue or they are auto-closed. AI use is welcome with disclosure and a review-pass summary. No CLA.

**First step:** file the `sample_id` issue; while it is triaged (about 7 days), build the package.

**Effort:** 3–5 days for the package; about 0.5 day for the core PR once accepted.

**What Ed must understand:** the Inspect hooks life cycle and async model calls (overlapping samples make attribution ambiguous, so state the concurrency limits); measurement windows vs sampler cadence.

**Risks:**
- **Scooping or custody:** ship only the instrument, never energy-as-monitor results, until the ALIGN paper.
- The selling point is validity, so do not over-claim per-call precision.

**Evidence:**
- `joulewise/align/attribution.py`, `joulewise/align/phase_detect.py`, `joulewise/align/energy_residual.py`;
- ALIGN endpoint and token-budget design: lane `lane/2026-11-05-align-token-budget`, `docs/align/token_admission_budget.md`.

### 8. transformers `qwen4_exp`: a stable tie-break for the QSA indexer top-k

**Pitch.** The QSA indexer scores blocks with `relu(...)`, so blocks whose head dot-products are all negative score exactly 0. When fewer than K blocks score above zero, the K-th score is 0 and the selection among the tied zero-score blocks is implementation-defined:
- `torch.topk` on CPU picks neither the lowest nor the highest index (JouleWise probed this);
- `mx.argpartition` and mlx-vlm keep the higher indices.

So "the reference" is itself order-dependent. It is the only source of fp32 mismatch in mlx-vlm's single-request path, and in JouleWise's real-dim cross-check it appeared at 8 mask entries.

**Proposal.** A deterministic tie-break, such as (score descending, block index ascending), folded into the indexer rework. vasqu wrote on 2026-11-03 that they "need to rethink the indexer completely" (see open PRs #50169 and #49694).

**Upstream state.**
- No issue or PR about ties.
- The code is in `modeling_qwen4_exp.py`, lines 745–747; the modular file is the source of truth (lines 449–451).
- transformers asks first-time contributors not to use code agents for issues or PRs, discourages "theoretical bugs", and requires AI disclosure. No CLA.

**First step.**
1. Count exact-zero ties at the K-th score with real weights. `perf.md` requires the real-weight parity runs to log the tie rate: add that to the JouleWise PR #669 harness or the streamed gold pass if it is not there yet, then use the L2/L3 layers.
2. Build a tiny-config repro where CPU and MPS (or two torch versions) pick different blocks.
3. Then write the issue.

**Effort:** 1–2 days.

**What Ed must understand:** QSA block compression, `relu` scoring and why exact zeros are common; `torch.topk` stability guarantees.

**Risks:** maintainers may judge the rate negligible. Without real-weight numbers the issue reads as theoretical, so do not file it without them.

**Evidence:**
- Lane `lane/2026-11-05-qwen4exp-port-perf` (JouleWise PR #670): `docs/align/qwen4_exp_port/perf.md`, section 3 and open issue 1;
- `docs/align/qwen4_exp_port/audit_mlx_vlm_numerical.md`, finding P3;
- commit `a6a3364a3` (tie-aware comparisons).

---

## Quick wins this week

Ordered for this week's constraints: block-5 release on 8 Nov, the measurement Mac reserved, ALIGN paused.

1. **mlx-lm reasoning round trip (item 1).** Repro on the M4 Air with a small Qwen3.5 checkpoint, then the issue, then the PR. About 1–2 days.
2. **mlx-vlm `indexed_attention` (item 2).** The patch exists; about 2 h. Coordinate with the D1 thread. Then the llama.cpp converter issue and PR, about 1 day.
3. **km003c-rs re-delivery test and issue (item 3).** Fixtures already in git; about 3–4 h.
4. **macmon #118 validation comment (item 4).** Only if PR #565's sources pass the custody check. Otherwise schedule a 30-min desk capture for after the block-5 release.

Each of these needs only git-tracked fixtures, tiny configs or a small public model. None touches blinded data.

## Bigger flagship

**CodeCarbon's meter-validated, rootless Apple Silicon backend (item 6).** Zeus gets the validation issue as a side product (item 5), and the follow-ons are `inspect-energy` (item 7) and an `mlx_lm.benchmark --energy` proposal.

It is the one contribution that:
- puts JouleWise's distinctive skill (measured whole-machine truth vs on-chip estimates, timing-aware integration) into a tool with very broad reach;
- answers a request the maintainers wrote in their own docs;
- yields a public validation table that does not depend on any blinded data.

**Its research twin:** after the block-5 release and the BYTES subset release, a versioned **open dataset of measured Apple Silicon inference energy** (whole-machine DC input, rails, rho, phase-attributed prefill/decode), published with Paper 1 on Hugging Face Datasets or Zenodo with a DOI, following ML.ENERGY's run schema where possible.
- No leaderboard accepts this today. AI Energy Score requires an H100; ML.ENERGY is H100/B200 and run by its maintainers.
- Every public Apple Silicon J/token source found uses rail estimates or battery gauges: Anubis OSS, GreenBench (arXiv 2608.28667), john-rocky/apple-silicon-llm-bench. So the gap is real.
- Treat the dataset as a Paper-1 artifact, not as this week's work.

## Honorable mentions

- **ControlArena** ([UKGovernmentBEIS/control-arena](https://github.com/UKGovernmentBEIS/control-arena)): a docs page and example for running its `shade_arena` setting on local open-weight models (mlx-lm or vLLM through `openai-api/...`), with fixes in `settings/shade_arena/message_converter.py` for any real bugs. It merges external PRs within days, but the queue has been stalled since 10-26, and the setting depends on a stale SHADE fork. Running it needs a capable local model, so the measurement Mac. An energy-based *monitor* example belongs after the ALIGN paper. The official [jkutaso/SHADE-Arena](https://github.com/jkutaso/SHADE-Arena) is dormant: skip it.
- **mlx-lm `qwen3_coder` tool parser.** JouleWise's strict parser could supply template round-trip conformance tests (render → parse → equal) and a fix for #1907 (oneOf/anyOf without `type`). But this is the most crowded corner of mlx-lm: about 20 parser PRs, most closed unmerged, and #1992 / PR #1993 / #1996 are contested now. Its literal `"null"` → `None` behaviour comes from Qwen's own reference parser ("Handle null value for any type"), so it is a design choice, not a bug. Lower expected value than item 1.
- **Anubis OSS** ([uncsoft/anubis-oss](https://github.com/uncsoft/anubis-oss), 1,500+ Apple Silicon submissions): an issue showing that its "system_power" is SoC rails only (rho), and suggesting a label fix or an SMC column. About 2 h; maintainer uptake uncertain.
- **lm-evaluation-harness:** after v0.4.14 ships the `lm_eval.models` entry point (PR #4013), a tiny mlx-lm PR registering `mlxlm`. Low signal; requires a CLA.
- **llama.cpp Metal at long context (#30074):** a hand-written data comment with tok/s *and* J/token vs context depth, llama.cpp vs MLX, on the M3 Max. High interest, but it needs measurement-Mac time.
- **mlx-lm #1807** (hybrid server memory growth on Qwen3.8-27B): a data comment with JouleWise's config-derived recurrent-state payload (146.8 MiB per snapshot for Qwen3.8-27B).

## Checked and not recommended (already done, in progress, or too small)

| Candidate | Upstream state on 2026-11-05 | Verdict |
|---|---|---|
| mlx-lm Gated DeltaNet l2norm eps (callers used an effective eps of 1.28e-4, not 1e-6) | **Fixed** by [#1896](https://github.com/ml-explore/mlx-lm/pull/1896) (merged 2026-09-17, `normalize_qk`). | Done. The JouleWise finding applies only to the pinned 0.31.3 (`test_native_mlx_lm_normalization_is_not_hf`). |
| mlx-lm gated-delta masked steps: the Metal kernel writes y = 0, the ops path does not | **Known and accepted.** Upstream `tests/test_gated_delta.py::test_masked_generic_matches_ops_reference`: "Outputs at padded positions are unspecified (the kernel zeros them, the ops reference does not)". The state agrees. | Drop. JouleWise commit `28d153449` pins the same behaviour. |
| bf16 router top-k: mlx-lm ranks bf16 `softmax(precise=True)` outputs in `qwen3_next`, `qwen3_moe`, `qwen2_moe` and `olmoe`; HF ranks fp32 | No issue. **Measured too rare to matter:** audit P1 found 1.3 % of tokens at logit σ = 0.5 and 0 % at σ ≥ 1. Exact ties already present in the bf16 logits (about 14 % with 512 experts) dominate. A synthetic probe in this survey (bf16 Gaussian logits, E = 128..512) found ≤ 1e-4. | Drop; at most a remark in a related thread. |
| Hybrid prompt-cache checkpoint/restore (JouleWise PR #657) as an mlx-lm feature | **Exists, and the memory-lean variant was tried and closed.** The server already stores system/user/assistant segment copies in `LRUPromptCache`. [#1596](https://github.com/ml-explore/mlx-lm/pull/1596) (recurrent-only checkpoints inside LRU entries, essentially JouleWise's design) and [#1515](https://github.com/ml-explore/mlx-lm/pull/1515) were closed when the maintainer closed every PR from one contributor because there were too many to review. [#1395](https://github.com/ml-explore/mlx-lm/issues/1395) and [#1807](https://github.com/ml-explore/mlx-lm/issues/1807) remain open. | Not novel, and the maintainers are wary. The bitwise restore-equals-fresh gate (4/4 PASS, reported in the PR #657 review; `docs/run_reports/2026-11-05-align-cache-checkpoint-native.md` on the fix-657 lane) stays in-house evidence. |
| `ArraysCache` rollback for speculative decoding / MTP | **Crowded, in progress:** [#1486](https://github.com/ml-explore/mlx-lm/pull/1486), [#1821](https://github.com/ml-explore/mlx-lm/pull/1821) (maintainer zcbenz), [#990](https://github.com/ml-explore/mlx-lm/pull/990), [#1456](https://github.com/ml-explore/mlx-lm/pull/1456); issue [#1446](https://github.com/ml-explore/mlx-lm/issues/1446). | Drop. |
| MLX `scaled_dot_product_attention` at head_dim 256 (no fused prefill in 0.31.2; JouleWise splits rows) | **Fixed on MLX main.** `scaled_dot_product_attention.cpp` accepts D = 256 for the full kernel. | Workaround becomes obsolete at the stack upgrade. |
| mlx-vlm n-gram PLE table paged from disk (GOAL "offer PLE paging upstream") | **Done:** `mlx_vlm/models/qwen4_exp/ple_storage.py` (2026-08-26). | Update `GOAL.md`'s remaining-contribution line. |
| Gated DeltaNet padding semantics in transformers (HF zeroes inputs so the state decays; mlx-lm freezes it) | Harmless for left padding from a zero state. Maintainers already say right padding is unsupported for generation (#48256). | Drop. |
| `mx.fast.rope` inv_freq differs from HF's by 1 ulp (about 1e-3 rad at 40K) | No issue; `freqs=` already exists. | Too small. |
| Greedy vs speculative divergence ([#1423](https://github.com/ml-explore/mlx-lm/issues/1423), [#1470](https://github.com/ml-explore/mlx-lm/issues/1470)) | Already explained in-thread (GEMM vs GEMV schedules). | JouleWise's chunk-schedule finding agrees; nothing new to add. |
| A shared block-sparse attention Metal kernel for DSA models (from JouleWise's QSA prefill kernel) | mlx-lm merged gather-based sparse prefill for `glm_moe_dsa` and DeepSeek-V3.2 ([#1997](https://github.com/ml-explore/mlx-lm/pull/1997), [#2013](https://github.com/ml-explore/mlx-lm/pull/2013)). `mlx_lm/kernels/` accepts custom Metal kernels. | A plausible ML-systems stretch goal, but the gain over gather is unmeasured and the latent-MLA shapes differ from QSA's. Benchmark before proposing. Kernel: `joulewise/align/models/qwen4_exp_kernels.py` on lane `lane/2026-11-05-qwen4exp-port-perf`. |

## Verification notes

- **Upstream heads read:**
  - mlx-lm main (last push 2026-10-30; release v0.32.2);
  - MLX main (last push 2026-11-04; v0.32.4);
  - mlx-vlm `Neywa-Labs/mlx-vlm` main (2026-11-05);
  - transformers b55e0761; llama.cpp 10d4846a; inspect_ai 27f18ff7; vLLM 14d147a7.
- **Spot-checked directly** in addition to the survey reports:
  - km003c-rs `measurement.rs` reject/reset logic;
  - CodeCarbon's "effectively unreachable" doc line;
  - macmon README "Power sources and macOS 27";
  - the llama.cpp `conversion/qwen4exp.py` compress-ratio line;
  - the transformers `_LEGACY_LAYER_TYPE_REMAP` table and the `configuration_qwen4_exp.py` rewrite;
  - the existence of Inspect #6246 and ControlArena's `settings/shade_arena`.
- **Not executed:** the upstream `qwen3_coder` parser edge cases are from reading the source only. Running downloaded code was not permitted in this session.
- **Ed's footprint:** Ed's GitHub account (mpmdw) has no prior issues or PRs in any of these repositories, so he is a first-time contributor everywhere. Start with the small, crisp items so that later flagship PRs come from a known name.
