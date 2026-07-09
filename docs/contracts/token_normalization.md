# Token Normalization And Stack Identity Contract

Status: binding for token-denominated metrics, cross-tokenizer comparison
language, and reader-facing stack-identity captions from 2026-07-09 onward.
It composes with `docs/contracts/claims_ladder.md` for claim levels and
`docs/contracts/capstone_scope.md` for single-unit limitation language.

Evidence inputs: `docs/reviews/2026-07-09-scientific-rigor-review.md` M3,
Appendix B finding 6, and Appendix D Part C rows "Stack confound" and
"J/token comparability"; `docs/decision_log.md` D-033, D-037, D-052, and
D-053; `docs/contracts/claims_ladder.md`;
`docs/contracts/capstone_scope.md`; and
`docs/contracts/run_bundle_layout.md`.

## Primary Metric

Request energy is the PRIMARY reader-facing energy metric.

Request energy means idle-subtracted joules per request under a named
measurement boundary. The boundary label is part of the metric identity, not
caption garnish.

Per-token metrics never replace request energy in a headline. They may appear
as companion metrics when their tokenizer scope and denominator provenance are
explicit.

A headline means the primary reader-facing figure or table and any
abstract-level claim, not only the title. In any reader-facing figure or
table containing token-normalized metrics, request energy must be co-displayed
with equal or greater salience.

## J/Token As Tokenizer-Scoped Companion Metrics

`J/token`, `J/output-token`, and `J/prompt-token` are companion metrics scoped
to a named tokenizer. They describe the measured stack and tokenizer that
produced the denominator; they are not tokenizer-blind work units.

Requirements:

- Per-token denominators must be runtime-observed token counts. This is the
  D-037 claims-ladder rider; use `docs/contracts/claims_ladder.md` Global
  Rules as the downgrade authority rather than restating it here.
- The tokenizer identity must be named wherever a per-token number appears:
  tokenizer name, revision, class, and vocabulary size where available, per
  the D-033 `metadata.workload_provenance` block.
- For per-token metrics, denominator provenance includes prompt-delivery
  regime and BOS handling: `prompt_source` and `bos_present` as recorded in
  `outputs/suite_items.jsonl` (D-046).
- When prompt token-ID hashes are cited, the single-prompt hash domain is
  `joulewise.prompt_token_ids.v1` (D-033). The suite rollup hash domain is
  `joulewise.suite_prompt_token_ids.v1` per
  `docs/contracts/run_bundle_layout.md`.
- `J/token` values from different tokenizers are NEVER an efficiency ranking
  by themselves.

## Cross-Tokenizer And Cross-Model-Family Comparisons

Any comparison across tokenizer families, or across model families with
different tokenizers, must do one of two things:

1. Carry companion denominators that are tokenizer-independent, such as
   `J/char`, `J/byte`, or semantic-matched pair denominators
   (FLORES-style same-content parallel items).
2. Avoid efficiency-ranking language entirely and remain descriptive.

Forbidden language:

| Forbidden language | Forbidden use | Allowed replacement |
|---|---|---|
| "more efficient per token" | Cross-tokenizer or cross-model-family ranking. | "lower `J/token` for [stack A] under tokenizer [name/revision/class/vocab size] than [stack B] under tokenizer [name/revision/class/vocab size], with request energy [direction/value] under [boundary]." |
| "better J/token" | Cross-family efficiency conclusion. | "different tokenizer-scoped `J/token` under [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size]; request energy is [direction/value] under [boundary]." |
| "cheaper tokens" | Treating tokens from different vocabularies as comparable work units. | "lower `J/char`, `J/byte`, or semantic-pair energy under the stated companion denominator." |
| Tokenizer-blind "energy per token" leaderboard language | Ranking stacks without naming tokenizer identity and request energy. | "tokenizer-scoped companion metrics for [stack A tokenizer name/revision/class/vocab size] and [stack B tokenizer name/revision/class/vocab size], reported beside request energy." |
| Treating token counts as comparable work units across vocabularies | Any inference that equal token counts imply equal semantic, byte, or character work across tokenizers. | "same-content item energy" or "`J/char`/`J/byte` companion denominator, with tokenizer-scoped `J/token` only as context." |

Within one tokenizer identity, per-token comparisons still obey the claims
ladder, analysis registry, floor, order, and boundary rules. This contract
only prevents token denominators from being promoted into tokenizer-blind
efficiency units.

## Stack-Identity Table

Every reader-facing result claim governed by
`docs/contracts/claims_ladder.md` must carry stack identity across all
claims-ladder-governed surfaces: reports, slides, README/status prose,
captions, tables, and figures. Any exported or reused rendering of a governed
figure must carry the same stack identity in the rendered artifact or
immediately adjacent text, at minimum by naming a stack-identity table it
resolves to.

The table below defines the minimum fields and the expected
bundle/provenance surface when it is already known.

| Field | What satisfies it | Bundle/provenance surface |
|---|---|---|
| Hardware unit | Concrete physical target or node label, hardware model, and unit identity when available. | `metadata.device`; composite/split node identity where applicable. |
| OS + version | Operating system name and version/build. | `metadata.environment` or device/environment capture fields. |
| Runtime + version | Runtime or serving stack name and version, for example MLX, vLLM, llama.cpp, mock, or adapter-specific runtime. | `metadata.runtime`; `metadata.environment.python_packages` for Python package versions such as `mlx`, `mlx-lm`, and `transformers`; `metadata.adapters.runtime` for additive adapter metadata. |
| Kernel/library where known | Kernel, attention implementation, library backend, graph/capture mode, or equivalent runtime kernel identity when exposed. | Runtime adapter metadata; `metadata.adapters.runtime.prepare_metadata` when captured. |
| Model artifact hash | Model artifact byte identity, not only a display name. For directories, the folded directory identity satisfies this field. | `metadata.runtime.model_artifact_identity`; model identity inside `metadata.workload_provenance` where recorded. |
| Quantization | Quantization format, precision, and runtime quantization label, or `none`/`unknown` if that is the recorded state. | `metadata.runtime`; model/config fields; `metadata.workload_provenance` model fields where recorded. |
| Tokenizer identity | Tokenizer name, revision, class, and vocabulary size where available; prompt source and BOS handling (`prompt_source`, `bos_present`) when per-token metrics are shown; token-ID hash domain and hash when the caption cites prompt-token identity. | `metadata.workload_provenance` (D-033); `outputs/suite_items.jsonl` item `prompt_source`, `bos_present`, and per-item token hashes; single-prompt domain `joulewise.prompt_token_ids.v1`; suite rollup domain `joulewise.suite_prompt_token_ids.v1`. |
| Sampler/output policy | Sampler settings, stop condition, runtime stop reason, and output cap/policy label. | `events.jsonl` `item_start` event metadata `output_policy`; `outputs/suite_items.jsonl` item `stop_reason`; `metadata.workload_provenance.output_policy`; suite `metadata.workload_provenance` sampler provenance per `docs/contracts/run_bundle_layout.md`. |
| Batching/concurrency policy | Always applicable: state explicit batch size/concurrency policy, `single-request sequential`, or `unavailable`. | Runtime adapter metadata, serving-stack configuration, run orchestration metadata, or explicit `unavailable` when not captured. |
| Measurement boundary label | Named boundary whose joules are reported, including rail/source semantics. | `metadata.telemetry`, `power_trace.csv` `source`/`rail`, rail-manifest metadata, and D-018 boundary label used under `docs/contracts/claims_ladder.md`. |
| Telemetry backend | Backend that produced the power trace, including version or command semantics where available. | `metadata.telemetry`; `metadata.device.powermetrics` for powermetrics sampler evidence; backend-native artifacts under `raw/`; telemetry logs. |

Every field in this table must appear on every governed surface as either a
concrete value or an explicit `unavailable`/`unknown`; silent omission of any
field is non-compliant.

## Caption-Compliance Rule

A figure or table caption is compliant when it carries the stack-identity
fields above and composes with both:

- the boundary-label rule in `docs/contracts/claims_ladder.md` Global Rules;
- the single-unit caption template in `docs/contracts/capstone_scope.md`
  "Single-Unit Limitation Language".

Do not duplicate those contracts' text here. Their rules remain the source of
truth for boundary labels and single-unit limitation wording.
