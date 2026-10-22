# Registration ALIGN-META (draft): logged counts alone as a sabotage detector

**DRAFT, not funded, not registered.**

**Status.** A registration fixes a study's question, data and every piece of arithmetic in writing before the data exist. This one was written 2026-10-21 by Opus 5.5 in the orchestrator role, before any episode of this design exists: the project has run no SHADE-Arena task, rented no GPU for it and holds no agent transcript. Nothing in this file authorizes spending; the rented-GPU session it describes needs Ed's explicit go. The question is the bank row `RQ-ALIGN-METADATA-BASELINE` in `docs/research_question_bank.md` (section "Candidate questions 2026-10-21"); the build plan is `docs/align/PIPELINE.md`. The code this file names is being built on separate lanes (parallel build branches, one per module group) and is not merged; where this file names a function, it names the interface fixed in that lane's build brief, and the landed code's interface is checked against this text before registration (§11, slot M-5).

**What happens to this draft before it can count.** (1) The lanes it names land with their twins (independent second implementations of the same arithmetic, §1.7). (2) A shakedown session on the rented machine (§3.5) checks the harness and measures minutes per episode. (3) Every `OPEN[M-n]` slot in §11 is filled. (4) A cold gate (an independent judgment by a model with no part in writing this, checked by a second model that tries to show it wrong) reads the file against the landed code. (5) The file is committed with a date; that commit is the registration time and precedes the first counting episode. A change after that is a dated entry in §13 with its reason, and the registered result is printed beside any changed one.

## 0. Why this question, and why it comes first

The research direction behind this file asks whether the electrical energy an inference machine draws can serve as a record of an AI agent's work that the agent cannot edit. On one inference stream, energy follows the number of tokens processed closely. A detector built on energy could therefore turn out to be an expensive token counter. Before any energy is measured, we need to know how well the counts that an ordinary log already holds separate sabotage from honest work. That number is the bar every energy result must clear, in particular the energy question that shares these episodes (bank row `RQ-ALIGN-ENERGY-RESIDUAL`: does energy beyond what the logged tokens predict flag runs with hidden or deleted work?).

The outcome is useful whichever way it falls:

- If counts separate sabotage well on an honest log, sabotage is already visible to bookkeeping on these tasks, and energy can only add value where the saboteur edits the counts. The tampered-log line (§4.4 c) then becomes the one the energy work must beat.
- If counts separate poorly even on an honest log, sabotage adds little extra work that counts can see, and energy, which tracks the same work, is unlikely to do better on these tasks. That is a warning for the energy question before money is spent on it.
- Between these, the number is the bar.

No published baseline from token or tool-call counts exists for sabotage detection, so the number is reportable on its own.

## 1. Terms, built in the order they are used

### 1.1 Model, endpoint, turn, tool call, episode

- **Token.** A language model reads and writes text in tokens: short pieces of text such as a word, part of a word, a digit or a symbol.
- **Endpoint.** The model runs on a GPU behind a local web server (here vLLM) that accepts a conversation and returns the model's next message, together with counts of the tokens it read and wrote. The code's interface for it is `ChatEndpoint` in `joulewise/align/interfaces.py`.
- **Turn.** One call to the endpoint. The model first reads the conversation (the **prefill**) and then writes its message one token at a time (the **decode**). Tokens of the conversation that the server already processed in an earlier turn and kept in memory are the turn's **context**; the rest are its prefill tokens.
- **Tool call.** A message can ask to run a tool: read an inbox, send an email, move money in a simulated bank. The harness runs the tool in a simulated environment and appends the result to the conversation.
- **Agent and episode.** The model run in this loop, turn after turn, until it answers without asking for a tool or reaches a turn limit, is an **agent**. One complete run of one task, under one condition (§1.2), with one random seed, is an **episode**. In code an episode is an `Episode` in `joulewise/align/records.py`, holding its turns (`Turn`) and tool calls (`ToolCall`) with integer-nanosecond times.
- **Hidden tokens.** Some generated tokens are never shown to a monitor (§1.3): the reasoning text a reasoning model writes before its answer, which the server separates from the visible message, and a private scratchpad the benchmark offers the agent. The server still counts them. `Turn.hidden_tokens` records how many, and they are included in `Turn.decode_tokens`.

### 1.2 SHADE-Arena, task pairs and the two conditions

SHADE-Arena (Kutasov et al. 2025, arXiv 2506.15740) is a public benchmark of agent sabotage. Each **task pair** sets a **main task** in a simulated environment with mock tools, and a **side task**: a second, harmful goal reachable with the same tools. Five of its seventeen pairs are public; this design uses those five, fetched from the upstream repository at a pinned commit (slot M-1).

- **Benign condition:** the agent is given the main task only.
- **Sabotage condition:** the agent's instructions also contain the side task, tell it to complete the side task without being noticed, and tell it that a marked scratchpad is hidden from any reviewer.

Upstream code scores each episode: a main-task score, and whether the side task succeeded (`Episode.main_task_score`, `Episode.side_task_success`).

### 1.3 The log, the tampered log and the monitor

- **The log** is the record a deployer keeps of each episode: per turn, the server's token counts, and each tool call with its start and end times. It holds counts and times, not content. In code it is what `Episode.totals(logged_only=True)` sums: only the turns and tool calls marked `logged`.
- **The tampered log** is the log as a saboteur that can edit its own records would leave it: the turns and tool calls in which it worked on the side task are removed. The functions `delete_turns` and `drop_tool_calls` in `joulewise/align/tamper.py` mark them `logged=False` instead of deleting them, so the episode's measured energy, used by the energy question, stays with it.
- **The monitor** is a second language model given the transcript and a description of the main task and asked how suspicious the agent's behaviour is, answering with a number from 0 (not suspicious) to 100 (certainly sabotage), the SHADE-Arena convention (`MonitorVerdict.suspicion`). Unlike the counts, it reads content. Its **visibility** is the part of the transcript it is shown: `full` (everything), `no_scratchpad` (the scratchpad and the separated reasoning text withheld; SHADE-Arena's standard setting, since it tells the agent the scratchpad is hidden), or `actions_only` (only tool calls and their results).

### 1.4 A score and its AUC, with a worked example

A detector gives each episode a **score**; a higher score means more suspicious. Its **AUC** (area under the receiver-operating-characteristic curve) is the probability that a randomly chosen sabotage episode scores higher than a randomly chosen benign episode, with a tie counting one half.

Worked example, scoring six episodes by their number of tool calls:

| Benign episodes | Sabotage episodes |
|---|---|
| 10, 12, 15 | 14, 18, 20 |

There are 3 x 3 = 9 benign-sabotage pairs. The sabotage episode with 14 beats the benign 10 and 12 but not 15 (2 wins); 18 beats all three (3); 20 beats all three (3). AUC = 8 / 9 = 0.889. Had the labels been swapped, the AUC would be 1 / 9 = 0.111: a score that runs the wrong way. A score unrelated to the condition gives 0.5 on average. The AUC needs no cut-off: it measures how well the score ranks episodes, whatever threshold a deployer later chooses. It is `auc` in `joulewise/align/stats.py`.

### 1.5 Combining counts: the logistic score and cross-validation

- **Logistic regression** combines several counts into one score: a weighted sum of the counts passed through the function 1 / (1 + e^-x), which turns any number into one between 0 and 1. The weights are chosen to fit the labels of a set of training episodes. A **penalty** of strength λ (an "L2" penalty: λ times the sum of squared weights, or half that by some conventions) pulls the weights toward zero. It keeps the fit unique when two counts are near copies of each other (a count and its logarithm) or when the training episodes can be separated perfectly. It is `fit_logistic` in `stats.py`.
- **Cross-validation** scores each episode with weights fitted without it, so the AUC says how the score does on episodes it has not seen. **Leaving one task pair out** does this in five rounds:

```
round   weights fitted on (training)     episodes scored (held out)
  1     pairs 2, 3, 4, 5                 pair 1
  2     pairs 1, 3, 4, 5                 pair 2
  3     pairs 1, 2, 4, 5                 pair 3
  4     pairs 1, 2, 3, 5                 pair 4
  5     pairs 1, 2, 3, 4                 pair 5
then:   the five held-out score sets are pooled into one list -> one AUC
```

Every episode is scored once, by weights that never saw its task pair. This models a deployer facing a task it has no history for. Each round also rescales every count to mean 0 and standard deviation 1 using the training pairs only. It is `grouped_cv_scores` in `joulewise/align/metadata_baseline.py`.

### 1.6 Intervals

- A **95% confidence interval** is a range computed from the data that, over many repetitions of the whole study, would contain the true value in 95% of them.
- The **cluster bootstrap** rebuilds the study by drawing five task pairs from the five observed, with replacement (a pair can be drawn twice and another not at all), keeping each pair's episodes together, and recomputing the AUC. The 2.5th and 97.5th percentiles of the rebuilt AUCs are the interval. Drawing whole pairs keeps the differences between tasks inside the interval. With five pairs there are 5^5 = 3,125 equally likely ordered draws, few enough to compute every one, so the interval carries no random-sampling error of its own (§5). It is `cluster_bootstrap_auc_ci` in `stats.py`.
- The **DeLong interval** (DeLong, DeLong and Clarke-Pearson 1988) is a formula-based interval that treats every episode as independent. When task pairs differ, it is narrower than the bootstrap and too optimistic, so it is printed only as a labelled line. It is `delong_ci`.
- A **paired difference** compares two scores on the same episodes (for example the counts score against the monitor). DeLong's paired test gives the difference, its standard error and a two-sided p-value. It is `paired_auc_difference`.

### 1.7 Flags, exclusions and the twin

- A **flag** is a condition recorded on an episode (`Episode.flags`). It never stops collection. An **exclusion** removes a flagged episode from the primary line; §6 names which flags exclude, and every result is also printed with flagged episodes included, as a labelled line.
- The **twin** is a second implementation of the same arithmetic, written independently by a different model from the same definitions. Main code and twin both run on the real episodes and must agree within the bars of §5 before any number is released.

## 2. Hypotheses

This is an estimate, not a decision; the expected directions are registered so a reader can see what was predicted. Nothing is decided from them, and each line is printed with its interval whatever it shows.

- **H1.** On the honest log, the counts score separates sabotage from benign episodes above chance for each agent model: its 95% interval lies above 0.5. Reason: the side task asks for extra work (more turns, more tool calls, more hidden reasoning), and the log counts that work even when it hides the content.
- **H2.** On the tampered log, the counts score's AUC is lower than on the honest log (paired difference below zero). Reason: tampering removes exactly the work the counts saw.
- **H3.** No direction is registered for the counts score against the monitor; the paired difference is printed with its interval.

## 3. Data: what is run

### 3.1 Models and serving

| Role | Model (Hugging Face repository) | Size | Notes |
|---|---|---|---|
| Agent 1 | `Qwen/Qwen3-8B` | about 8.2 billion weights; about 16 GB at 16-bit | dense model: every weight is used for every token |
| Agent 2 | `Qwen/Qwen3-30B-A3B` | about 30.5 billion weights, about 3.3 billion used per token; about 61 GB at 16-bit | mixture-of-experts model: a router picks a few expert sub-networks per token; its routing on the same episodes is the subject of a separate question (bank row `RQ-ALIGN-MOE-ROUTING-STATS`, Stage A) |
| Monitor | `openai/gpt-oss-20b` | about 21 billion weights, 4-bit; runs in about 16 GB | open weights, fixed for the whole study |

"At 16-bit" means each weight is stored in 16 bits (2 bytes), so the memory in GB is about twice the weights in billions. Revisions, the vLLM version and every sampling setting are pinned in slot M-2. Sizes are from the model cards and are re-read from the pinned configs.

- **Thinking on.** Qwen3 writes its reasoning between `<think>` and `</think>` before the visible message by default; the agents run that way, because it is how the models are meant to be used for multi-step work.
- **Sampling.** The Qwen3 model card's recommended settings for thinking mode (temperature 0.6, top-p 0.95, top-k 20 at the time of writing; confirmed at pin time) and a per-request seed equal to the episode's seed. Seeds only matter if sampling is random, and the card advises against always taking the most probable token in thinking mode.
- **Limits.** The tokens a turn may write and the number of turns an episode may take are upstream SHADE-Arena's defaults (slot M-1). An episode that reaches either is flagged (§6), not cut from the data.
- **Why this monitor.** An open-weight monitor run locally costs no API spend and stays identical for every episode, so its AUC can be reproduced. It is weaker than the monitors SHADE-Arena reports, and any comparison with it says so (§10).

### 3.2 Task pairs, conditions and seeds

For each agent model: 5 public task pairs (names recorded from the pinned upstream commit, slot M-1) x 2 conditions x 30 seeds (0 to 29) = 300 counting episodes; 600 for both models. `run_matrix` in `joulewise/align/runner.py` runs them in an order shuffled with a recorded seed, so any slow drift of the machine over the session does not line up with the condition. Episodes run one at a time on the GPU because the energy question samples power on these same episodes (one episode's power cannot be separated from another's on a shared GPU). The number 30 is derived in §5.

### 3.3 Monitor runs

The monitor scores every counting episode under each of the three visibilities, and every sabotage episode's tampered transcript (§3.4) under `no_scratchpad`: 600 x 3 + 300 = 2,100 monitor calls. Each call is one request to the monitor endpoint; `prompt_sha256` records the exact prompt sent. The prompt is upstream's monitor prompt, pinned in slot M-4.

### 3.4 The tampered copy

For each sabotage episode, `delete_turns` and `drop_tool_calls` mark as unlogged every turn in which the agent worked on the side task. Which turns those are is decided per task pair by a rule written from the side task's definition before any episode exists (for example: turns whose tool calls name the side task's target account or address); the rules are slot M-3. Benign episodes are copied unchanged: an honest agent has nothing to hide, and tampering benign episodes as well would ask a different question. The tampered copy is a second view of the same episodes, not new runs.

### 3.5 Shakedown

Before the counting episodes: seeds 1000 and 1001 x 5 pairs x 2 conditions x 2 models = 40 episodes. They check the harness end to end on the rented machine (the endpoint's token counts against the server's own `/tokenize` counts, tool dispatch, monitor parsing), measure minutes per episode for the spend projection (§8), and report the side-task success rate per pair and model. Shakedown episodes never enter any counted line, and none of their numbers enters the analysis.

## 4. The analysis, step by step

Every step runs separately for each agent model; there are two primary results, one per model.

### 4.1 Features

For each episode, `features(episode, logged_only=True)` in `metadata_baseline.py` returns: turns; prefill tokens; decode tokens (including hidden tokens, which the server counts); tool calls; duration in seconds; decode tokens per turn (mean and maximum); tool calls per turn; decode tokens per second of turn time; the fraction of turns with a tool call; and log(1 + x) of each count, so that an episode with 400 tool calls does not swamp one with 40. Hidden tokens appear as zero under `logged_only`, because a log does not say which counted tokens were hidden. The landed function's exact list and names are frozen in slot M-5.

### 4.2 The counts score

`grouped_cv_scores(episodes, l2=1.0)`: leave one task pair out (§1.5); the rescaling and the fit use the training pairs only; an episode's score is its held-out fitted probability.

### 4.3 The primary result

The AUC of the pooled held-out scores against the condition (sabotage = 1, benign = 0), from `auc`, with the 95% cluster-bootstrap interval over task pairs from `cluster_bootstrap_auc_ci`, computed by enumerating all 3,125 draws (§5). Printed per agent model.

### 4.4 Secondary lines

Each is labelled and none replaces the primary.

- **(a) Independent-episode interval.** The DeLong interval for the same AUC.
- **(b) Per task pair.** The AUC of the held-out scores within each task pair: five numbers per model, showing whether one task carries the result.
- **(c) Tampered log.** Steps 4.1 to 4.3 on the tampered copy (fit and score both on tampered logs, as a deployer whose every log is tampered would), and the paired difference from the honest-log AUC on the same episodes (`paired_auc_difference`).
- **(d) Monitor.** The AUC of `suspicion` under each visibility, with its cluster-bootstrap interval; the paired difference, counts score minus monitor at `no_scratchpad`, on the honest copy and on the tampered copy.
- **(e) Successful sabotage only.** The primary repeated with the sabotage episodes restricted to those whose side task succeeded (benign episodes unchanged), printed with the count kept.
- **(f) Penalty.** The primary at λ = 0.1 and λ = 10.
- **(g) Flagged-inclusive.** The primary with every episode whose features can be computed, whatever its flags.

### 4.5 Disclosures printed with every result

Episodes per pair, condition and model, before and after exclusions; the count of each flag; the side-task success rate per pair and model; the mean main-task score per condition (does sabotage cost the main task?); the number of episodes that reached the turn limit.

## 5. Every size, threshold and bar, with its derivation

| Item | Value | Derivation |
|---|---|---|
| Interval level | 0.95 | Conventional. Nothing is decided from an interval, so no correction across the two models or the secondary lines is applied; the words of §10 depend only on whether an interval contains 0.5. |
| Seeds per pair, condition and model | 30 | Precision of the AUC with n episodes per condition, by the Hanley and McNeil (1982) variance formula, at the worst case AUC = 0.5. The target: a half-width no larger than 0.075, half of the 0.15 gap between chance (0.5) and the AUC of SHADE-Arena's human reviewers (0.65, as reported upstream), so a counts score as good as a human reviewer is distinguishable from chance. At 5 pairs x S seeds per condition, the half-width is 0.0927 (S = 15), 0.0802 (20), 0.0748 (23), 0.0654 (30): S = 23 is the smallest that meets the target. 30 keeps it met even if 23% of episodes are excluded (115 left per condition: 0.0748), and it is the shape (five pairs, 30 seeds) the code was tested at. At AUC 0.75 and 0.9 the half-width with 30 seeds is 0.055 and 0.036. More seeds do not narrow the between-task part of the uncertainty, which only more task pairs could. |
| Penalty λ | 1 (0.1 and 10 as labelled lines) | On rescaled counts, the data's curvature of the fit for one weight is about n p (1 - p) with n = 4 pairs x 2 conditions x 30 seeds = 240 training episodes and p (1 - p) at most 0.25, about 60. A penalty of λ = 1 adds 1 or 2 to that, by the code's convention, shrinking a well-determined weight by a few percent while keeping the fit unique. 0.1 and 10 are a factor of ten either side. |
| Fit stopping rule | stop when no weight changes by more than 1e-10 of the weights' scale in one step | From the A6 build brief. A change that small moves a held-out probability by far less than the AUC's printed precision (0.001), more than a million times below it. |
| Bootstrap draws | all 3,125 ordered draws of five pairs | Exact enumeration leaves no random-sampling error. The same rule the MoE permutation test uses applies: enumerate when the number of arrangements is at most 100,000 (5^5 = 3,125 qualifies). If the landed function only draws at random, it must gain this mode before registration (slot M-5). |
| Printed precision | AUC to 3 decimals | The smallest expected half-width is 0.036 (AUC 0.9, 150 per condition); 0.001 is under 3% of it. |
| Twin agreement | every AUC, interval end and paired difference within 1% of the smallest printed half-width of the primary intervals; counts, labels and flags identical | The project rule for an agreement bar between two programs: at least a million times the float noise, at most 1% of the smallest printed uncertainty. With half-widths from 0.036, the bar is about 3.6e-4; float noise in these sums is about 1e-15. |
| Turn limit, tokens per turn | upstream defaults (slot M-1) | Settings of the run, not thresholds on a measured quantity. Reaching one is flagged, not excluded. |
| Shakedown size | 2 seeds per cell | Enough to run every pair, condition and model twice; it sets no number in the analysis. |

## 6. Exclusions and flags

An episode is excluded from the primary line only when its counts do not describe a complete run of the registered setup. Everything else is a flag, and the flagged-inclusive line (§4.4 g) is always printed.

| Condition recorded | Primary line | Why |
|---|---|---|
| Episode ended by an endpoint or harness error | excluded | its counts describe a run cut short by the machinery, not by the agent |
| A turn without token counts from the server | excluded from every line, listed | its features cannot be computed |
| Turn limit reached | kept | the agent's behaviour under the registered limit |
| Output cap reached in a turn | kept | as above |
| Connection retried before any byte arrived | kept | the failed attempt generated nothing |
| Scratchpad tokens uncounted (`hidden_tokens.scratchpad_uncounted`) | kept | changes only the hidden-token count, which the features do not use; the scratchpad's tokens are already inside the decode count |
| Upstream evaluation routed through a local judge model | kept | affects only the side-task success used by line (e) |
| Monitor output without a readable score | kept for the counts lines; dropped from that monitor line and counted | the monitor line has no value for it |
| Power trace without a clock mapping (`clock.unmapped`) | kept | power is not used here |

Flag strings other than the two the runner's brief names are fixed from the landed code in slot M-5.

## 7. What would kill the question, and what would make it uninformative

Nothing kills a baseline: it is reported at whatever value it takes. Three outcomes change what follows it:

1. **The side task almost never succeeds** for an agent model (shakedown and counting episodes). The sabotage condition then labels an instruction, not a behaviour. The primary still answers "does the instruction leave a trace in the counts", and line (e) shows how few successes there were. The energy question cannot study hidden side-task work on that model's episodes, and its spend request says so.
2. **The honest-log AUC is near 1** for both models. Counts already catch sabotage on these tasks; energy is worth measuring only against the tampered log, and the energy question's registration makes that line primary.
3. **The tampered-log AUC stays high.** The tampering rule left the side-task work visible in other counts (for example, longer remaining turns). It is reported, and the tampering rules of slot M-3 are revisited before the energy question uses them.

The data would be unusable for this question only if the server's token counts could not be trusted; the shakedown checks them against `/tokenize` before any counting episode runs.

## 8. Hardware and spend

- **GPU.** One rented whole GPU with 80 GB of memory (A100 80GB or H100 80GB class), holding one agent model at a time. This question alone would run on any GPU, or a share of one, that serves the pinned weights. A whole GPU is needed because the same episodes are power-sampled for the energy question, and a shared or partitioned GPU hides the power of the whole card (the preflight, the check `python -m joulewise.align.power.preflight` runs at the start of a session, refuses one).
- **Monitor endpoint.** A second GPU with at least 16 GB, or the same machine after all agent episodes have finished: the monitor reads stored transcripts, so it never overlaps an agent episode's power trace.
- **No paid API.** Every model is open-weight and served locally. Upstream evaluation steps that call a judge model are routed to the local monitor endpoint and flagged.
- **Episodes.** 40 shakedown + 600 counting = 640, run one at a time.
- **GPU-hours** = 640 x (minutes per episode) / 60. The minutes are measured in the shakedown; this file does not guess them. The arithmetic for a few values:

| Minutes per episode | 2 | 5 | 10 | 20 |
|---|---|---|---|---|
| GPU-hours for 640 episodes | 21.3 | 53.3 | 106.7 | 213.3 |

- **Spend** = GPU-hours x the hourly price of the rented class. No price is written here; it comes from a quote at approval time. `joulewise/align/gpukit/cost.py` turns the shakedown's minutes per episode into the projection; Ed approves a GPU-hour cap; the session stops at the cap, and a matrix cut short is printed with its counts and called short.
- **If funded without the energy question**, episodes can run several at a time on the endpoint, dividing the GPU-hours by roughly the number run at once.

## 9. The code that computes it, the twin, and blinding

| Module | Lane in `docs/align/PIPELINE.md` | Used for |
|---|---|---|
| `joulewise/align/records.py` | spine (on the base branch) | `Episode`, `Turn`, `ToolCall`, `MonitorVerdict`, `Episode.totals` |
| `joulewise/align/endpoints.py`, `joulewise/align/shade/` | A1 | the OpenAI-compatible endpoint client, the SHADE-Arena task adapter, the monitor |
| `joulewise/align/runner.py`, `joulewise/align/tamper.py` | A5 | `run_matrix`, `run_episode`; `delete_turns`, `drop_tool_calls` |
| `joulewise/align/metadata_baseline.py`, `joulewise/align/stats.py` | A6 | `features`, `grouped_cv_scores`; `auc`, `delong_ci`, `paired_auc_difference`, `fit_logistic`, `cluster_bootstrap_auc_ci` |
| `joulewise/align/gpukit/` | W2 | the session script and `cost.py` |

The twin of A6's arithmetic is built on its own lane from the same definitions; both run on the real episodes, and the release waits for agreement within §5's bar. Commit hashes of every module at registration are slot M-5.

**No blinding.** No energy enters this analysis, the labels are fixed by design, and the arithmetic is fixed here before any episode exists, so there is nothing a hidden factor would protect.

**Analysis order.** Pin the code; shakedown; fill the slots; cold gate; register; collect the counting episodes; run main code and twin; compare; release.

## 10. What may be said

- "On SHADE-Arena's five public task pairs, with Qwen3-8B (or Qwen3-30B-A3B) as the agent, a score built only from logged counts separated sabotage from benign episodes with AUC X (95% interval over task pairs, a to b)." Always with the agent model, the five pairs and the interval.
- "Above chance" only for a model whose primary interval lies above 0.5.
- The comparison with the monitor names the monitor (gpt-oss-20b at the pinned revision and visibility). It is never compared with SHADE-Arena's published monitor AUCs as if measured here: the agents and monitors differ.
- Never "counts detect sabotage" in general: five task pairs, two agent models and one monitor bound every sentence.

## 11. Open slots

| Slot | What fills it | When |
|---|---|---|
| M-1 | Upstream SHADE-Arena commit, licence, the five public pair names, the default turn limit and tokens per turn | when the A1 lane lands |
| M-2 | Model revisions, vLLM version, sampling settings confirmed from the model card | at pin time |
| M-3 | Per-pair rule naming the side-task turns for the tampered copy, written from the task definitions | before the first counting episode |
| M-4 | Monitor revision and the exact monitor prompt with its SHA-256 | at pin time |
| M-5 | Commit hashes of every module in §9 and of the twin; the frozen feature list; exact enumeration in `cluster_bootstrap_auc_ci`; flag strings | when the lanes land |
| M-6 | GPU class rented and the price quote behind the spend approval | at Ed's approval |

## 12. Decisions made by the author

Each is a choice the governing texts left open; those marked * change which data count or a printed number and go to the cold gate.

1. * The label is the condition the agent was given (sabotage instructed), not side-task success; success-only is line (e). Reason: the condition is fixed by design before the episode, so the label cannot depend on the outcome.
2. * The primary is the leave-one-task-pair-out score (a deployer with no history of the task); per-pair AUCs are line (b).
3. * λ = 1, with 0.1 and 10 as labelled lines (§5).
4. The bootstrap enumerates all 3,125 draws instead of sampling them.
5. * The monitor's primary visibility is `no_scratchpad`, SHADE-Arena's standard setting.
6. * The tampered copy edits sabotage episodes only (§3.4).
7. * The agents run with thinking on at the model card's sampling settings.
8. * 30 seeds per pair, condition and model (§5).
9. Episodes run one at a time, because the energy question shares them.

## 13. Change log

- 2026-10-21: first draft (Opus 5.5).
