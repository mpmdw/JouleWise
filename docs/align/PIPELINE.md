# Alignment research pipeline (build plan, 2026-10-21)

Status: candidate research, built ahead of any measurement. Nothing here is
registered, funded or claimed. No rented GPU, hardware purchase or paid API
is used by anything in this package without Ed's explicit go.

## The question

Can the electrical energy an inference machine draws serve as a record of an
agent's work that the agent cannot edit? Logs, transcripts and monitors are
software the agent may be able to reach. The power draw is measured outside
it. Power cannot show what a single forward pass computes (a token costs about
the same work whatever it says), but it can count work: generated tokens a log
omits, tool calls a log omits, and the phase structure of a run (prefill,
decode, waiting on a tool). Long agentic runs (minutes, dozens of turns) may
carry enough extra work in a sabotage run for it to clear the measurement
floor, where a single query would not.

The limit every result states: power catches hidden tokens and unlogged tool
calls; it is blind to reasoning that fits inside one forward pass.

## Candidate questions (bank rows, not registry rows)

| ID | Question | Kill condition |
|---|---|---|
| RQ-ALIGN-METADATA-BASELINE | How well do token, turn and tool-call counts alone separate benign from sabotage agent runs? | none; a baseline is always reportable |
| RQ-ALIGN-ENERGY-RESIDUAL | Does energy beyond what the logged tokens predict flag runs with hidden or deleted work? | residual indistinguishable from noise at the measured floor |
| RQ-ALIGN-MOE-ROUTING-STATS | Do aggregate MoE routing statistics separate benign from sabotage (Stage A, from router logs), and are they visible in power (Stage B)? | Stage A shows no separation |
| RQ-ALIGN-EFFICIENCY-MONITORABILITY | What is the cheapest configuration, in measured joules, that reaches a given monitor catch rate across model sizes and inference-time budgets? | joule frontier identical to the token frontier across sizes |
| RQ-ALIGN-JOULE-DISTILL | Does joule-based trace selection differ from length-based selection? | provisionally killed: for a fixed teacher it reduces to length |

## Package layout

Everything lives under `joulewise/align/`, tests under `tests/align/`.

| Module | Lane | What it does |
|---|---|---|
| `records.py` | spine | The shared records: `Episode`, `Turn`, `ToolCall`, `PowerTrace`, `ClockMapping`, `MonitorVerdict`, `RouterLog`. The only thing that crosses lanes. |
| `shade/` | A1 | Runs SHADE-Arena task pairs against any OpenAI-compatible endpoint (vLLM, llama.cpp) and an off-box monitor; writes `Episode`s. Upstream code is fetched at a pinned commit, not vendored. |
| `power/nvml.py`, `power/preflight.py` | A2 | NVIDIA power and energy-counter sampling, the repetition protocol for sensors that average a slice of each period, and the rented-GPU preflight (whole GPU, power moves under load, clock-lock attempt recorded). |
| `power/ina3221.py`, `phase_detect.py` | A3 | Jetson INA3221 rail reader and a detector that finds tool-call and phase boundaries in a power trace. |
| `attribution.py` | A4 | Energy per turn, per phase, per tool call from a `PowerTrace` and the episode's timestamps, with the clock-offset uncertainty carried. |
| `runner.py` | A5 | Runs a matrix (task pairs x conditions x models x seeds) with sampling beside each episode; tamper simulation (delete turns, hide scratchpad) as a post-hoc transform. |
| `metadata_baseline.py` | A6 | Features from logged counts, a grouped cross-validated classifier, AUC with confidence intervals. |
| `energy_residual.py` | A7 | Fits energy against logged tokens and context on benign runs; scores the residual; computes detection power against hidden-work size and noise floor. |
| `moe/` | A8 | Router logging hooks (Qwen3-MoE family) and Stage A statistics: expert-usage entropy, reuse and locality, load imbalance, with a grouped permutation test. |
| `budget/` | A9 | The efficiency-monitorability pilot: thinking on/off, budget forcing at fractions of the median reasoning length, a "be concise" condition, the random-deletion control, a fixed local monitor, catch rate per configuration. |
| `frontier.py` | A10 | Joule and token Pareto frontiers across model sizes, and the Spearman gate that decides whether joule-based distillation is worth reopening. |

## Rules every lane follows

- The core is stdlib-only. Heavy dependencies (numpy, torch, transformers,
  pynvml, openai) are imported lazily inside the function that needs them,
  behind an extra; CI installs no extras, so every test that needs one skips
  with the reason, and the stdlib path is tested on its own.
- Every tolerance, threshold or test bar on a measured or derived quantity
  carries its derivation beside it (sensor resolution, sample interval, about
  1 J attribution limit on the M3 Max, or 1% of the smallest printed
  uncertainty). An agreement bar between two implementations sits between
  1e6 times float noise and 1% of the smallest printed uncertainty; where no
  uncertainty exists, 1e-6 relative.
- Conditions that are not physical hazards are recorded as `Episode.flags`,
  never refusals.
- Samplers expose plural `clock_mappings` after `stop()`. Foreign traces that
  cannot attach remain recoverable with their samples and mapping offers in
  `hardware.runner.unattached_traces`; non-finite samples are counted and flagged.
- Runner tokenizer diagnostics run after all samplers stop. Server-reported
  reasoning counts remain in `Turn.hidden_tokens`; tokenizer estimates of
  separated reasoning are labelled separately in episode hardware metadata.
- Monitor views exclude system messages and hide only closed scratchpad pairs.
  Task flags and per-call monitor diagnostics propagate into the episode.
- Synthetic test worlds are built so that the effect each rule is meant to
  catch is larger than the test's bar (a hidden-token count that clears the
  floor, a routing shift above the permutation noise), and so that its
  absence would be detected.
- Each number-producing analysis has a second, independent implementation
  written by a different model, and the two are compared on the same
  synthetic worlds.
