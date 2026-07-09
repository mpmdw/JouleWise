# Instruction tuning behavior suite spec

Status: draft. Scope: inference-time behavior suites around instruction style,
chat-template delivery, output-format constraints, and base-vs-instruct
comparisons.

## Non-goal

This spec is not about training energy. If a later campaign compares
fine-tuned or instruction-tuned checkpoints, it must pin model, adapter, and
training-manifest provenance, but it must not claim training-process
efficiency without a separate train-time capture contract.

## Purpose

The suite substrate can compare how instruction-shaped prompts affect measured
inference energy and behavior under fixed evidence rules. This is valuable
only if it stays disciplined:

- same boundary and hardware
- explicit tokenizer/template identity
- exact prompt/output shape where possible
- strict validation
- floor gates
- behavior annotations separated from energy measurement
- no intelligence-per-joule or leaderboard claims

## Candidate profiles

### `instruction_style_ladder_v1`

Same semantic task, same target shape, varied instruction style:

- bare task
- role/audience framing
- explicit constraints
- strict response contract

Use `difficulty.axis: instruction_style` with quarantine language. Initial
categories can draw from existing `jw.chat`, `jw.summ`, `jw.json`, and
`jw.reason` generators.

Primary question: under fixed shape, do instruction styles change request
energy, emitted-token behavior, stop reasons, or malformed/format-valid rates?

Forbidden upgrade: "more instruction following costs X energy" as a general
model claim.

### `chat_template_bridge_v1`

Raw-completion versus chat-template delivery for instruction-tuned models.

This is the highest-value bridge for instruction-tuning work, but it requires
an explicit adapter/spec change. Current affine delivery is raw-completion, and
there is no generic chat-template path in the suite substrate.

Required pins before implementation:

- template source and hash
- whether BOS/EOS/template special tokens are injected
- token budget accounting after templating
- prompt-token hash domain
- whether raw and templated variants can be exact-shape matched

Forbidden upgrade: AP-6 ids-native/no-BOS sentinel results generalize to
text-path chat-template prompts.

### `format_following_ladder_v1`

JSON/schema/output-format tasks with increasing constraint strictness.

Behavior annotations may include deterministic JSON parse validity,
schema-validity, required-key coverage, and malformed status. Correctness must
remain quarantined unless a new analysis-plan row adopts the deterministic
scorer.

Primary risk: terse invalid/refusal outputs can look energy-cheap under
natural EOS. Stop reason and emitted-token distributions must be headline
quality checks.

### `reasoning_mode_ladder_v1`

Direct-answer, short-visible-explanation, and constrained-format variants at
fixed shape, plus a natural-EOS pilot.

Primary question: how much of an observed energy difference is realized output
length, stop policy, or phase timing rather than "reasoning" as a capability?

Prompts must not request hidden chain-of-thought, private scratchpads, or
internal reasoning transcripts. Any visible explanation is ordinary model
output and must be treated as response text, not privileged reasoning evidence.

Forbidden upgrade: "thinking is more energy efficient" or "reasoning costs X"
without model-specific, prompt-specific caveats and token controls.

### `base_instruct_pair_v1`

Named base and instruction-tuned checkpoint pairs under the same boundary and
as much shared provenance as possible.

Required pins:

- model artifact hashes
- adapter/LoRA hashes where applicable
- tokenizer file manifest
- template policy
- prompt source and BOS handling
- exact output policy

Claim shape: observed inference behavior and energy for named stacks. Do not
claim the tuning process caused the difference unless the pair is controlled
well enough and the analysis plan says so.

## Measurement outcomes

Primary outcomes:

- gross request energy
- idle-subtracted request energy
- suite/block/level gross energies
- emitted tokens
- stop reason
- TTFT
- throughput
- item status counts
- prompt/response hashes and response text
- phase descriptors where identifiable

Behavior annotations:

- JSON parse/schema validity
- exact affine scoring where applicable
- malformed/capped/runtime-failed rates
- refusal/short-output deterministic flags
- natural-EOS output-length distributions

Annotations must remain separate from bundle validity unless the manifest
contract or analysis plan explicitly promotes them.

## Analysis-plan needs

Before L2 claims, add AP rows for:

- instruction-style common-shape comparison
- chat-template bridge comparison
- format-following validity/energy comparison
- base-vs-instruct named-stack comparison

Each AP row must define metric, window class, unit of analysis, floor gate,
inclusion/exclusion, order covariates, denominator provenance, claim ceiling,
and forbidden stronger claim.

## Acceptance criteria

- Uses the existing suite manifest mechanism.
- No bespoke marker/window plumbing.
- Generated manifests and sidecars are deterministic and byte-identical.
- Tokenizer/template identity is explicit and hashable.
- Text-path expected-vs-realized hash guard is in place before scale.
- Chat-template variants do not run until template/BOS/token-budget semantics
  are contract-pinned.
- First-run evidence remains L0/L1 until `n >= 5`, floor gates, strict
  validation, and AP rows are satisfied.

## Rationale

Instruction-tuned behavior is tempting because it sounds close to model
quality. JouleWise should keep the question narrower and more valuable:
given named inference stacks and controlled prompt delivery, what energy and
runtime behavior is actually observed? That keeps the work in the project's
measurement lane while still producing useful evidence.

Rejected alternatives:

- Train-time energy accounting in this suite. Rejected because the harness is
  currently an inference measurement instrument.
- Judge-scored pass/fail or pass@k. Rejected because it drifts into benchmark
  leaderboard territory and needs a separate evaluation policy.
- Chat-template comparison without template hashes and BOS handling. Rejected
  because prompt identity would be ambiguous.

## Revisit triggers

- A chat-template delivery path is designed.
- A specific base/instruct pair is selected.
- A deterministic scorer graduates from sidecar annotation to analysis-plan
  endpoint.
- Training-energy capture becomes an explicit project scope.
