# MoE Stage A: routing beyond counts

Status: offline Stage A is implemented. Execution evidence and optional-model
coverage are recorded in .codex-report/align-moe.md. Synthetic validation is not
hardware evidence.
No real model download, rented GPU, or live power collection is part of this lane.

Stage A asks whether aggregate router statistics separate benign and sabotage
episodes beyond logged token, turn, and tool-call counts. A negative Stage A
result is the pipeline's stop condition for the routing direction. Stage B,
which asks whether routing is visible in electrical power, requires hardware.
Power can count hidden work; it cannot identify reasoning inside one forward pass.

## Model topology

The published [Qwen/Qwen3-30B-A3B config](https://huggingface.co/Qwen/Qwen3-30B-A3B/blob/d47d535f78ec44bd57128f8e8aeba17eeb0285ea/config.json),
checked 2026-10-22, declares `model_type=qwen3_moe`,
`num_hidden_layers=48`, `num_experts=128`, `num_experts_per_tok=8`,
`decoder_sparse_step=1`, and `mlp_only_layers=[]`.
The recorder must discover actual sparse blocks and read their gate topology;
these published values are not constants imposed on other models.

## Backend capture paths

HF transformers permits forward hooks on each Qwen3-MoE, Qwen2-MoE, or Mixtral
sparse block's gate. The shared `RouterLog` orders rows by processed token,
then by actual MoE layer, and tags each row prefill or decode. A generation's
last sampled token need not have been forwarded through the model yet; captured
forwarded-token counts therefore need not equal server completion counts.

[vLLM v0.21.0 routing replay](https://docs.vllm.ai/en/v0.21.0/training/routed_experts_replay/)
documents `--enable-return-routed-experts` (offline:
`enable_return_routed_experts=True`). It exposes request-level
`prompt_routed_experts` and per-completion `routed_experts` arrays in
token/layer/top-k order. An adapter would join each request to its episode/turn,
append prompt and generation rows with their phase labels, and validate topology
and counts. Prefix-cache sentinel IDs, missing/preempted capture, and speculative
token trimming need flags. Pin the serving version and verify capture coverage;
older versions may need instrumentation at the fused router's selected IDs.

llama.cpp's [MoE graph construction](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-graph.cpp)
has the selected-expert tensor produced by top-k routing. A C++ graph evaluation
callback (`cb_eval`), or a small backend patch if fusion hides that tensor, would
copy actual selected IDs to host and join microbatch token positions, sequence
IDs, and layer IDs to requests. Its ordinary completion API does not supply
a shared `RouterLog`. Capture requires backend synchronization and correct
treatment of cached prompts and speculative forwards. Do not infer routes from
model text or expert load totals.

## Analysis contract

Entropy is normalized by log(number of experts). Load imbalance is the mean
per-layer population coefficient of variation. Reuse measures expert-set overlap
between adjacent selected tokens; reuse distance excludes each expert's first
selection. Phase filtering must happen before sequence statistics are calculated.

Permutation inference preserves label counts within each task group. Exact
enumeration applies through 100,000 arrangements; larger spaces require Monte
Carlo error below 0.005 at p=0.05, a tenth of that conventional significance level.
Routing, metadata, and combined classifiers must share held-out task groups.


## Capture API and coverage

Construction attaches the hooks. Use eager inference on one sequence at a time:

```python
from dataclasses import replace
from joulewise.align.moe.hooks import RouterRecorder

with RouterRecorder(model) as recorder:
    with recorder.phase("prefill"):
        output = model(input_ids=prompt, use_cache=True)
    with recorder.phase("decode"):
        model(input_ids=next_token, past_key_values=output.past_key_values)
    episode = replace(episode, router_log=recorder.log,
                      flags=episode.flags + tuple(recorder.flags))
```

A snapshot never changes when later forwards are recorded. reset() starts another
episode without reattaching hooks; close() removes this recorder's hooks.
Inference without an override uses sequence length and the KV cache: a fresh
one-token prompt is prefill, and a cached one-token forward is decode. Override
cached one-token tool-response prefill and multi-token speculative decode
explicitly. Batched episodes, incomplete layers, unsupported topology, training
mode, padding omission, and inference ambiguity are flags. An uncached multi-token
forward after recorded work adds `uncached_reforward`: uncached generate repeats
the growing prefix, and the log preserves that actual processed work rather than
pretending those rows are newly generated tokens. A cached multi-token tool-result
prefill does not trigger this flag. Incomplete forwards
are not presented as complete token rows. Propagate recorder.flags to
Episode.flags: RouterLog itself has no flags field.

Gate hooks synchronize selected IDs to the host. This instrumentation changes
runtime and potentially energy; Stage A establishes statistical feasibility.
Do not use its overhead as Stage B evidence. Compiled/fused/distributed HF
execution needs separate capture-coverage validation.

## Statistics and inference details

- usage_entropy: average of layer entropies, rather than entropy of pooled
  expert IDs; normalization is log(num_experts). One expert has entropy zero.
- load_imbalance: population standard deviation of expert counts divided by
  their mean, including zero-count experts, then averaged over layers.
- reuse_fraction: mean set intersection / top_k over adjacent tokens and layers.
- mean_reuse_distance: each recurrent selection contributes its token-index
  distance from the previous use at that layer; first uses are excluded.
- episode_stats: twelve keys, <phase>_<metric>, with phases prefill, decode, both.
  None and both select all rows. Filtering precedes adjacency and distance
  calculations; distances count positions in the filtered sequence.
- Empty phases and undefined distances are NaN. routing_flags describes malformed
  log topology or selections. Stage A retains every episode in the aligned feature
  report, but excludes non-finite values separately for each routing test before
  permutation, effects and bootstrap. Each test flags the excluded episode IDs
  and count, and any retained group with only one condition. Undefined report
  fields print as JSON null.

RouterLog contains no turn/sequence boundary offsets. Sequence statistics use its
flat token order, including across turn/phase boundaries for the both view.
The explicit phase filter is a different sequence, so decode reuse distances do
not count intervening prefill rows.

The two-sided permutation statistic is sabotage mean minus benign mean. The
number of arrangements is the product of binomial group sizes. Exact p is the
fraction of all arrangements at least as extreme as observed. Monte Carlo p is
(extreme+1)/(draws+1); draws are at least floor(.05*.95/.005^2)+1 = 1901, since
sqrt(.05*.95/1901) < .005. An explicit smaller budget is raised to that minimum.
Binary-rational integer sums handle equality exactly without a floating tie
tolerance. Groups with only one condition cannot exchange labels and are flagged.

Holm correction always covers all twelve planned metrics; missing phases cannot
shrink the correction family. Effects include raw differences and pooled-SD
standardized differences. Whole task groups are sampled with replacement for
percentile intervals. Bootstrap count and confidence are parameters; the default
confidence is the conventional 95%. Undefined replicates are counted and flagged.
With only 12 to 17 task groups, the reviewer's independent-noise controls measured
zero-effect coverage of 0.913 and 0.906 across statistic-world cells (120 worlds
each), about 0.91 rather than 0.95. These effect percentile intervals retain that
small-cluster limitation; permutation p-values supply the corresponding tests.

## Routing versus metadata comparison

analyze_stage_a uses Episode.task_pair for both permutation groups and
leave-one-task-group-out classifier folds. The counts baseline uses logged
prefill tokens, visible decode tokens (decode_tokens minus hidden_tokens),
logged turns, and logged tool calls. It never uses the condition or side-task
success as a feature.

Routing uses all twelve statistics. Combined uses routing plus the same count
features. All three use a standardized nearest-centroid classifier with means,
population scales, imputation, and centroids fitted on training groups only.
Constant columns have zero weight. There is no hyperparameter fitting or
label-informed feature selection. Local Mann-Whitney AUC awards half credit to
ties; the spine has no metadata_baseline module/AUC to reuse.

The deliverable reports each held-out AUC and the combined-minus-metadata AUC
gain with a paired group-bootstrap interval that refits metadata and combined
classifiers in every replicate. All copies of each original task group are held
out together: duplicate bootstrap copies never cross a training/test boundary.
The main `auc_gain_interval` is this refitted percentile interval; its method and
valid replicate count are returned explicitly. Its calibration is tested against
the two lane nulls and the reviewer's null A and counts-only null B.

The individual `auc_intervals` and the separately labelled
`auc_gain_fixed_prediction_interval` resample fixed original predictions. They
are descriptive, conditional on fitted folds, and do not support a claim that
routing adds separation. A within-group label permutation would test the joint
null that neither feature set separates; it would not answer the gain question
when counts already separate. Refitting the group bootstrap targets the gain
under both kinds of null. A positive raw routing test alone does not establish
added separation. No automatic hardware authorization is embedded in the report.

Read shared Episode JSONL and print the analysis:

```sh
python3 -m joulewise.align.moe.stage_a episodes.jsonl --n-bootstrap 2000 --seed 0
```

The bootstrap budget is chosen by the analyst; it is not a hidden agreement bar.
The CLI streams JSONL through the shared record decoder, reduces each episode
to scalar features, and releases its router log before advancing. Library callers
can pass any iterable to `analyze_stage_a`; retaining a list of Episodes in the
caller still retains those logs. `episode_stats` validates once per aggregate
call, while each standalone metric call validates independently. The shared
eager `read_episodes` contract is unchanged.

## Generative synthetic controls

TopicWorld defaults to six-turn episodes with five tool calls, varying prompt
and decode counts, four sparse layers, 32 experts, top-4. Set layers=48,
num_experts=128, top_k=8 to exercise the verified full topology. Timings are an
explicit configurable serving scenario, with no power trace or hardware claim.

Every expert has equal main-topic affinity. A side topic has affinity one on
a layer-specific top_k-expert subset and zero elsewhere. A stated fraction f of
sabotage decode tokens switches topics; prefill is unchanged. Main-topic tokens
sample top_k distinct experts uniformly. Counts stay matched within task pairs.

For E experts and k selections, the asymptotic decode load CV is
f sqrt(E/k-1), and expected reuse is k/E + f^2(1-k/E). Entropy follows the
mixture probabilities: f/k+(1-f)/E on core experts and (1-f)/E elsewhere.
Finite-token CV-squared also has a marginal-count variance term. A balanced-exposure
control checks entropy and load against the exact mixture law. The random world
checks the expected reuse effect using its grouped-bootstrap interval.

The matched zero-shift control uses common random numbers, producing identical
paired router logs when f=0. A second control uses independent routing noise
under f=0. Both pass through real episode_stats, permutation tests, held-out
classification, and grouped bootstrap. Tiny real model tests construct 2-layer,
8-expert, top-2, hidden-size-32 HF models locally and generate two prompts. They
skip explicitly when torch/transformers or Qwen3-MoE support is unavailable.

Implementation and test execution status, with exact commands and observed
numbers, is tracked in .codex-report/align-moe.md.


The classifier comparison is specific to this fixed learner and these four
metadata features. It does not establish conditional independence from every
possible function of counts. Perfect synthetic separation can give a degenerate
bootstrap AUC interval; that is a property of the finite control world, not
uncertainty about real-model generalization. The optional tiny-model generation
length guarantees recurrent expert selections by the pigeonhole principle
before asserting that reuse distance is finite.
