# D3 Apple replication (internal, PROVISIONAL)

This harness repeats the [budget pilot](budget_pilot.md) on the M3 Max using
the [Apple lane](apple_path.md). It is unregistered. Its dry-run is synthetic;
the lead owns the first real session, control validation, and all measurement
authorization. The build session does not load weights, start powermetrics,
arm anything, or alter the paused-window state.

## Protocol and records

`python -m joulewise.align.budget.apple` reuses `budget.run.run_matrix`, its
calibration, paired no-hint answers, fixed reasoning monitor, scoring, and
`conditions.default_conditions()`. The eleven conditions are thinking on,
thinking off, concise, budget fractions 1.0/0.6/0.4/0.3, and their four
post-hoc deletion controls. Fractions, three calibration repetitions, and the
four-span deletion default are pilot design inputs, not precision claims.
Deletion shares the thinking-on capture and performs no new inference.
Both forced-generation calls, both prefills, and their gap belong to the
hinted Episode. Calibration, no-hint pairs, warmup, and monitor calls remain
separate; the headline inference energy excludes those costs.

The live path runs one model and one seed per invocation. Models are addressed
by repository ID and resolved exclusively from the local Hugging Face cache.
It requires a full commit SHA, tokenizer files, 4-bit dense-Qwen3 metadata,
and all indexed weight shards. No download is attempted. A `main` ref resolves
to its SHA; without a ref there must be exactly one snapshot or an explicit
`--revision`. These snapshots passed metadata/file-existence inspection during
the build (no weight loading or tensor validation):

| Repository | Cached revision |
|---|---|
| mlx-community/Qwen3-4B-4bit | 4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25 |
| mlx-community/Qwen3-8B-4bit | 545dc4251c05440727734bcd94334791f6ab0192 |
| mlx-community/Qwen3-14B-4bit | a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4 |

`BudgetMlxEndpoint` wraps the Apple lane's `MlxEndpoint` and existing MLX
runtime. Template options implement `enable_thinking`, assistant-prefix
continuation, and `add_generation_prompt=false`. A stream observer stops at
`</think>`, including when the delimiter crosses token segments. All actually
emitted tokens remain counted. The real runtime keeps its native tokenizer,
greedy sampler, phase events, and output token IDs. Reasoning counts use labelled
retokenization; delimiter boundaries need not reproduce original token splits.
Unclosed prefilled reasoning is censored reasoning with no answer, including
ceiling-hit calibration. Native faults become generation errors, not successful
empty replies. Nonzero temperature is refused: this path is greedy.

Energy comes through `BudgetAppleSampler`, a small wrapper of the Apple lane's
`ApplePowerSampler` and existing powermetrics adapter. Per-capture raw streams
remain under `captures/<unique-id>/raw/`. Traces retain native averaging
supports, anchor evidence, and the stop-derived epoch-to-monotonic mapping.
The wrapper puts that mapping into immutable trace notes in the checkpoint,
then installs it in each exported shared `Episode`, including after replay.
No new clock observation is used to reinterpret an old capture. The generic
checkpoint is an intermediate record; consume `result.json` or exported
Episode views, which have the measured mappings attached.

`apple_energy` explicitly sums gross CPU+GPU+ANE rails. It never adds a package
channel on top, substitutes wall energy, subtracts idle, or counts paired and
deletion captures as extra independent energy observations. An unresolved native
anchor, missing rail, or unbracketed trace has no energy estimate. Native
quantization is unknown in the adapter: the summary retains J but leaves its
complete uncertainty blank. The existing reducer carries the approximately
1 J attribution limit documented in RUN_STATE and D-078; extra clock, averaging,
and edge terms can only widen it. A blank bound is unknown, never zero or proof
of a sub-joule distinction. Do not treat ~1 J as a new acceptance threshold or
claim that this exploratory harness implements a calibrated claim interval.
When finite component bounds exist, the shared reducer applies the minimum
per rail and adds their bounds. That conservative sum is not a new instrument
calibration.

Exports are `result.json` and its content-addressed trace sidecar, summary JSON
and Markdown, and hinted/paired/calibration Episode views. Metadata records
the resolved model revision/path, runtime/artifact identity, benchmark config,
monitor transport, exact condition order, source implementation digest, and
provisional/synthetic labels. Shared Episodes also carry D3 hardware and scope
labels. `preflight/<unique-id>.json` preserves warm calls separately. The export
also preserves the frozen item bytes under `rosters/<sha256>.json`; per-call
native phase/token events and token IDs remain in the recorded usage provenance.
Resume uses the same checkpoint only with an identical experiment fingerprint; changed
settings, order, pins, code, roster, monitor transport, or measurement ID start
a different fingerprint. Other-run checkpoint entries stay preserved and flagged.

## Commands

Offline rehearsal, using all three model labels and authored items:

```sh
JW_WT=/ABS/WORKTREE-BEING-EXECUTED
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$JW_WT/.scratch-D3-BUILD/tmp-dry" \
  PYTHONPATH="$JW_WT" /opt/homebrew/bin/python3.13 -P -m joulewise.align.budget.apple \
  --dry-run --benchmark "$JW_WT/configs/examples/mock_local.json" \
  --count 2 --seed 0 --output "$JW_WT/.scratch-D3-BUILD/dry"
```

Create that TMPDIR first. Rehearsal uses scripted endpoints, a simulated clock,
and production-shaped 10 Hz three-rail interval samples injected at the native
telemetry boundary. It runs the real matrix, Apple representation adapter,
mapping attachment, reducer, checkpoint, and export. It does not simulate MLX
kernel behavior, privilege checks, native clock anchoring, or actual sensor
resolution. Native-shaped mocked streams additionally test the MLX endpoint
and live orchestration seam without importing or invoking native MLX inference.

For a separately authorized quiet session, prepare a frozen `ItemBatch` JSON
using the pilot's pinned MMLU source and stratified roster. Use precisely the
same roster, hint assignments, and fixed monitor as the NVIDIA comparison.
The harness reads this local roster; it performs no dataset fetch. A live
configuration has this shape (paths relative to that config file):

```json
{
  "roster": "frozen-roster.json",
  "controls_verified": false,
  "monitor": {
    "base_url": "http://REMOTE-MONITOR:8000",
    "model": "openai/gpt-oss-20b",
    "backend": "vllm",
    "runtime_revision": "REPLACE-WITH-FROZEN-WEIGHTS-AND-RUNTIME-PIN",
    "timeout_s": 120,
    "options": {"chat_template_kwargs": {"enable_thinking": false}}
  },
  "settings": {
    "max_tokens": 1536,
    "answer_max_tokens": 128,
    "calibration_repetitions": 3,
    "temperature": 0.0,
    "measurement_id": "REPLACE-WITH-SESSION-HARDWARE-SENSOR-IDENTITY"
  }
}
```

Token ceilings and monitor timeout above are operator design parameters; verify
that answers and verdicts fit before collection. Keep the monitor on a separate
unmeasured machine; do not load a second monitor model on the Mac. Supply the
actual monitor pin rather than the placeholder. A fixed monitor's remote
calls occur outside sampled generation brackets. This harness does not manage
that server or verify remote weight bytes.

The lead's live command, only after the normal machine/hazard and authorization
checks, is:

```sh
JW_WT=/ABS/WORKTREE-BEING-EXECUTED
PYTHONPATH="$JW_WT" /Users/edr/code/JouleWise/.venv/bin/python -P -m joulewise.align.budget.apple --live \
  --benchmark "$JW_WT/configs/examples/mac_mlx_local.json" --config /ABS/d3-live.json \
  --model mlx-community/Qwen3-4B-4bit \
  --revision 4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25 \
  --seed 0 --output /ABS/d3-block1-4b-seed0
```

`-P` (Python 3.11+) removes the current directory from `sys.path`, so the
JouleWise package comes from the explicit `PYTHONPATH` worktree. The live
interpreter must have the pyproject `mac` extra; the Apple lane's real H2 run
used Python 3.13.1, mlx 0.31.2, mlx_lm 0.31.3, and transformers 5.12.1 in the
venv above. Prepare metadata records the versions actually loaded. The offline
rehearsal imports no MLX and stays on python3.13.

Native per-token events are retained in every `ChatResult`. At about 800
reasoning tokens, the measured footprint was about 2.19 MB per item per file:
200 items × 2.19 MB is about 0.44 GB per file, or about 0.9 GB including traces,
per model-and-seed invocation. Before each invocation, the operator checks
`df -g /Users/edr` and keeps free disk above 40 GiB.

The base benchmark must select MLX/powermetrics and the intended sampling
cadence. Its optional tokenizer/template pins must belong to the selected model.
Each invocation loads one cached model, warms outside sampled brackets, exercises
on/off and four answer-prefix shapes (natural close, mid-line cut, newline cut,
zero cap), runs its matrix, and cleans up the runtime. API success alone does
not establish correct controls. Before marking `controls_verified=true`, inspect
the warm outputs through the real stack, decode the recorded `prompt_token_ids`
of the preflight continuations, and compare them with the NVIDIA serving stack's
rendering of the same prefixes; otherwise every trial stays flagged. On
transformers 5.12.1 the continuation prefix rendered as `...\n</think>\n\n`,
and real Qwen3-4B emitted a stray `</think>` on three of four preflight shapes.
Size `answer_max_tokens` from the preflight and the pilot's first continuations:
in the 2026-10-22 PR #555 review run on real Qwen3-4B, a cap-16 cut and forced
close led to a re-explanation that did not reach `ANSWER:` within 32
continuation tokens.
The sampler retains the Apple lane's post-window support dwell. This entry point
does not perform the controller's idle/hazard admission or authorize a window;
`hazard.unjudged:battery,ac,thermal,contention` remains in its traces.

## Run order and comparisons

Before seeing answers, freeze the roster, generation seeds, condition order,
ceiling settings, monitor, and session schedule. Optional `condition_order` in
the live config must be a permutation of all eleven default names. Execution
is model → item → calibration → non-deletion conditions in that order → deletion
conditions. Each physical condition executes its hinted request then its no-hint
pair, followed by the monitor. Deletion always comes last to reuse thinking-on
and its matched budget cuts. The default uses the order printed above.

Rotate the externally scheduled model order across blocks, for example
4B/8B/14B then 8B/14B/4B then 14B/4B/8B. Preselect condition permutations across
blocks; save them and use separate output/checkpoint directories per model/seed.
Greedy seeds name paired runs and deletion randomization; changing the seed
does not create independent stochastic MLX generations. Plan independent
measurement repetitions separately. Never treat sensor polls as replicates.

It can compare within-Mac monitorability, accuracy, reasoning length, and gross
rail work across budget settings and model sizes. With matched roster/hints and
the same monitor, it can test whether qualitative budget/monitorability patterns
repeat across platforms. It cannot isolate hardware efficiency: MLX 4-bit
weights, tokenizer/template implementation, greedy decoding, runtime, unified
memory, and sensor boundary can differ from the NVIDIA pilot. Mac CPU+GPU+ANE
rails and NVIDIA device energy have different scopes and exclude different
system costs. Absolute J, tokens/J, or a cross-platform cheapest-model ranking
are not interchangeable. Small effects near the attribution limit cannot settle
a ranking. There is no registered D3 power analysis or claim protocol here.

## What would kill it

Stop the session for unsupported controls or answer continuation, repeated
censored calibration/answers, unresolved hint-use labels, missing/truncated
monitor verdicts, absent cached shards/pins, or an inability to keep the monitor
and other workloads off the measured Mac. Retain failures and denominators;
do not silently rerun until an attractive answer appears. Missing privileges,
unresolved native anchors, missing/bracketing-invalid rails, battery/AC/thermal
or contention hazards, memory pressure, or effects comparable to unknown
attribution uncertainty also defeat an energy conclusion. The operator needs
independent live evidence to discharge these conditions. A successful dry-run
does not discharge any hardware gate.
