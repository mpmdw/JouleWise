# AXI-SC leg 1 — pinned mlx-lm speculative-decode/MTP feasibility verdict

- Date opened: 2026-07-17
- Runtime pin: `mlx-lm==0.31.3`, `mlx==0.31.2`
- Verdict: **`unsupported_for_joulewise`** (2026-07-17, lead-run live probes;
  external-draft: `event_observability`; native MTP: `native_mtp_generation`;
  evidence + SHA-256: `docs/process_traces/2026-07-17-axi-sc-live-probes/`).
  Filed per the Hailo idiom as a dated applicability finding: the Mac
  spec-decode energy leg is NOT minted on pinned mlx-lm 0.31.3. External
  draft is revisited only after a pinned-runtime upgrade exposes an exercised
  callback carrying per-round proposal counts, running aggregate acceptance,
  and exact decode-step emitted slices. Native MTP is revisited only after a
  pinned runtime retains the MTP weights and exposes an identifiable native
  generation path. DSpark/DFlash MLX implementations enter the registry as
  their own mechanism rows rather than reopening this pinned-runtime verdict.
- External-draft source finding: generation surface **`feasible_candidate`**;
  complete AXI-SA instrumentation surface **absent in the pinned API**
- Native-MTP source finding: **`unsupported_for_joulewise(native_mtp_generation)`**
- vLLM leg 2: **OUT OF SCOPE** here; it remains fixture-first,
  **PROVISIONAL**, and unable to support a live NVIDIA claim under D-070

This is an `[AGENT]` feasibility spike, not an energy measurement or a
claim-bearing campaign. It does not consume a `[QUIET-MAC]` window. External
draft models and native MTP are distinct mechanism families and are never
pooled.

## Binding classification

The binding AXI xhigh consult requires S-C to distinguish generation support
from claim-instrumentable support and to record missing proposal/acceptance
counters even when text generation works. The landed AXI-SA contract freezes
the required meanings: `tokens_proposed` is the number of actual candidate
positions submitted to target verification, `tokens_accepted` is the number
committed unchanged, and `acceptance_rate` is the ratio of their totals. One
request-scoped `decode_emission` event must describe each completed decode
step and its actual emitted burst.

The classification is therefore mechanical:

| Verdict code | Required evidence |
|---|---|
| `supported` | The requested target/mechanism executes; draft identity is complete for `draft_model` and null for `native_mtp`; and direct runtime evidence supplies actual `tokens_proposed`, actual `tokens_accepted`, their aggregate acceptance rate, and one request-scoped emission event per decode step with the exact N-token emitted slice. |
| `unsupported_for_joulewise(draft_model_generation)` | The pinned runtime is present, but the exact requested external target/draft pair does not execute through both model-call paths and complete generation. |
| `unsupported_for_joulewise(native_mtp_generation)` | The pinned runtime is present, but no native-MTP execution path is observed. Ordinary target-only generation is not MTP evidence. |
| `unsupported_for_joulewise(event_observability)` | Requested speculative generation executes, but any actual proposal counter, acceptance counter, aggregate rate, request lifecycle, or per-step emission boundary/count is unavailable. **Configured `num_draft_tokens`, model-call shapes, consecutive `from_draft` flags, or output grouping may not be substituted for direct proposal/emission evidence.** |
| `runtime_unavailable` | The pinned environment cannot be exercised: pin/source mismatch, missing or colliding artifacts, unavailable draft identity, MLX/Metal import failure, model-load/tokenizer failure, timeout, worker launch/protocol failure, or evidence/request mismatch. This is not a support verdict. |
| `PENDING-LIVE` | **Historical pre-live state, superseded by the 2026-07-17 closeout below.** It meant no lead-run Metal output had yet been attached; source inspection alone did not establish execution of a local target/draft pair. |

Generation without the required counters and event boundaries is thus
`unsupported_for_joulewise(event_observability)`, never `supported`.
Proposal/acceptance observability must be real runtime evidence and is never
inferred.

## Installed-source provenance

The reviewed installation is:

`/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/`

`mlx_lm/_version.py:3` records `0.31.3`; distribution metadata reports MLX
`0.31.2`. The live controller independently emits package versions and roots,
then verifies the source hashes before importing MLX.

| Installed source | SHA-256 |
|---|---|
| `mlx_lm/__init__.py` | `f9ffa88772d26e537a98aa39ab16488a7a0d13cc1fac5d665376132c94b49608` |
| `mlx_lm/_version.py` | `f0da9bc5c5c1bf21d576f7aa67b4eda887f1c7f0666746187b493e6831c4af6c` |
| `mlx_lm/generate.py` | `270778ad53eaca55a8533d82e6752660fe5d2605c4aa0879b48a50a91f69345f` |
| `mlx_lm/server.py` | `cdfcb4ac848636f9927851a0ec7a951584526530cb7832ba58049e4a9144db8b` |
| `mlx_lm/models/qwen3_5.py` | `f0daa30bba5cb521c8bdfa7093101a544c6a37bbba09bca582288219cb04ae3a` |

## Source-level answer

### A. External draft model: generation yes; full AXI-SA observability no

The pinned CLI exposes `--draft-model` and `--num-draft-tokens`
(`mlx_lm/generate.py:211-220`). The low-level
`speculative_generate_step(prompt, model, draft_model, ...)` accepts an
external model and configured draft count (`mlx_lm/generate.py:473-487`),
creates separate target and draft caches (`mlx_lm/generate.py:521-527`), and
requires a trimmable target cache (`mlx_lm/generate.py:529-533`). The public
`stream_generate` signature accepts `draft_model`
(`mlx_lm/generate.py:657-677`) and dispatches to the speculative generator when
that argument is non-null (`mlx_lm/generate.py:701-713`). The CLI separately
loads the requested draft and checks tokenizer vocabulary size
(`mlx_lm/generate.py:2056-2059`), then passes both `draft_model` and
`num_draft_tokens` to generation (`mlx_lm/generate.py:2072-2085`). This is a
real external-draft generation surface, subject to live execution of a
specific compatible pair.

Accepted-token observability is partially real. `GenerationResponse` defines
`from_draft` as whether the emitted token came from the draft model
(`mlx_lm/generate.py:269-296`); the internal accept loop yields each matching
draft token with `True`, then yields the target correction/bonus token with
`False` (`mlx_lm/generate.py:623-634`). `stream_generate` preserves that flag
on each public response (`mlx_lm/generate.py:716-753`). The harness therefore
records `tokens_accepted` from direct response flags, not text.

The rest of the AXI-SA surface is absent:

- The actual proposal count and acceptance-loop index remain local variables
  inside `speculative_generate_step` (`mlx_lm/generate.py:607-627`). The public
  response contains no actual proposed-count field (`mlx_lm/generate.py:269-296`).
  `num_draft_tokens` is a configured maximum; substituting it for actual
  proposals would violate AXI-SA.
- One verification iteration may commit several accepted tokens plus a target
  token (`mlx_lm/generate.py:612-634`), but the public generator flattens them
  into one response per token (`mlx_lm/generate.py:716-753`). It exposes no
  decode-step ordinal, step boundary, or N-token emission event. Grouping
  adjacent `from_draft` values would be inference.
- The convenience `generate` wrapper consumes responses into text only
  (`mlx_lm/generate.py:778-799`). The server discards even `from_draft`: its
  internal `Response` has no such field (`mlx_lm/server.py:225-233`), and the
  construction copies text/token/logprobs/finish state but not the draft flag
  (`mlx_lm/server.py:985-1004`). The server cannot restore the missing proposal
  counter or step boundary.

Consequently a successful external-draft live run can establish
`runtime_generation_supported:true`, a complete draft identity, emitted token
IDs, and direct accepted-token attribution. Under this pin it must still end
`unsupported_for_joulewise(event_observability)` because `tokens_proposed`,
`acceptance_rate`, and per-request decode-emission bursts are not directly
observable.

### B. Native MTP: no supported generation path

The public package exports `batch_generate`, `generate`, and
`stream_generate`, but no native-MTP entry point (`mlx_lm/__init__.py:10-19`).
Within `stream_generate`, the only accelerated branch is an external
`draft_model`; `draft_model is None` selects ordinary `generate_step`
(`mlx_lm/generate.py:657-713`). There is no native MTP/head kwarg, response
type, counter callback, or emission hook in the pinned generation module.

The Qwen3.5 implementation makes the negative result explicit. Its ordinary
text model returns one logits tensor (`mlx_lm/models/qwen3_5.py:278-298`), and
its sanitizer detects MTP weights and then removes every key containing
`mtp.` (`mlx_lm/models/qwen3_5.py:307-314`). The top-level model simply calls
that language model (`mlx_lm/models/qwen3_5.py:367-382`). A target config that
advertises `mtp_num_hidden_layers` is therefore only a candidate-artifact
fact; pinned mlx-lm discards the heads rather than executing native MTP.

The native-MTP probe keeps `draft_model_identity:null`, records the target
config's candidate fields separately, and refuses to count ordinary
target-only tokens as native-MTP generation. Its expected semantic result on
a live pinned runtime is
`unsupported_for_joulewise(native_mtp_generation)`.

## Probe design and fail-closed evidence contract

`scripts/axi_sc_spec_decode_spike.py` follows the hardened AXI-SB controller
shape from the start:

1. The standard-library controller emits JSONL only, pins both distribution
   versions and installed-source SHA-256 values, and validates model artifacts
   before starting a child.
2. Requested mode, target path, draft path or null, proposal cap, output cap,
   request ID, and prompt hash are copied into every lifecycle/capability row.
   The controller rechecks all of them. An internally coherent result for a
   substituted target, draft, or depth becomes
   `runtime_unavailable(evidence_verdict_mismatch)`.
3. External target and draft must resolve to distinct paths. The controller
   calculates the contract-domain folded SHA-256 over recognized draft weight
   files; the worker constructs the complete AXI-SA `draft_model_identity`
   from that digest, runtime pin, quantization, and runtime tokenizer. Native
   MTP requires that field to be null.
4. MLX import/load/generation occurs only in the captured child. Missing Metal,
   load failures, timeout, malformed output, stderr diagnostics, and protocol
   failure remain structured rows; the last line is always `probe_outcome`.
5. The child records target and draft model calls and one direct
   `generation_response` per public response. It dynamically checks for an
   explicit `speculative_decode_callback` parameter; bare `**kwargs` does not
   count. Only exercised callback payloads carrying actual proposal/accepted
   counts, running aggregate acceptance, and exact per-step emitted-token
   slices become `decode_emission` rows. Pinned mlx-lm 0.31.3 exposes no such
   parameter, so its live outcome remains unchanged. The controller
   cross-checks model-loaded, submitted, admitted, generation, terminal, and
   callback rows against the same request/model/depth identity and exact
   output token slice.
6. The controller suppresses the child's verdict and re-derives the result.
   A fabricated `supported`, a configured cap posing as `tokens_proposed`,
   grouped token responses posing as a decode step, duplicate/missing
   lifecycle rows, or terminal/output disagreement cannot upgrade the result.

`runtime_unavailable` is degradation evidence, not a support verdict. A final
semantic outcome always records `runtime_generation_supported` separately
from `claim_instrumentable`.

## Historical pre-live artifact snapshot (superseded)

The following initial inspection is retained for chronology. Its
missing-draft statement was superseded later on 2026-07-17 by the attached
lead-run evidence, which loaded and executed the named distinct pair:

- Present: `/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`
  (approximately 839 MiB, Qwen2 vocabulary 151,936). It can serve as the
  external-draft **target** for the small capability probe.
- Initially missing at the delegated inspection:
  `/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit`. This was the
  required smaller, tokenizer-compatible **draft**. **Superseded:** the lead
  subsequently made the artifact available and the attached live probe loaded
  it, exercised both model-call paths, and completed generation.
- Present: `/Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit`
  (approximately 65 GiB, Qwen3.5 vocabulary 248,320). Its config advertises
  one MTP hidden layer, so it is useful as a native-MTP candidate-surface
  check, but pinned mlx-lm strips the MTP weights. It is not tokenizer
  compatible with the Qwen2.5 artifact and is not a valid external-draft pair.

The initial conclusion that no distinct compatible pair was complete is
**superseded for the exact 1.5B-target/0.5B-draft pair** by the attached live
probe. The harness itself still performs no download; artifact acquisition and
any D-016 model decision remain lead/Ed-owned.

## Exact lead live commands

Run from this worktree. The absolute interpreter is intentional because this
delegated worktree has no `.venv` while the primary checkout contains the
pinned installation.

External-draft probe (historical missing-draft caveat superseded; this is the
command used for the attached live result and remains the exact rerun command):

```bash
/Users/edr/code/JouleWise/.venv/bin/python \
  scripts/axi_sc_spec_decode_spike.py \
  --mode draft_model \
  --target-model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --draft-model /Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --max-proposed-tokens 3 \
  --max-tokens 8 \
  --timeout-seconds 300 \
  > /tmp/axi-sc-mlx-draft.jsonl
```

Native-MTP candidate-surface probe:

```bash
/Users/edr/code/JouleWise/.venv/bin/python \
  scripts/axi_sc_spec_decode_spike.py \
  --mode native_mtp \
  --target-model /Users/edr/jw_models/mlx-community/Qwen3.5-122B-A10B-4bit \
  --max-proposed-tokens 1 \
  --max-tokens 8 \
  --timeout-seconds 300 \
  > /tmp/axi-sc-mlx-native-mtp.jsonl
```

Validate JSONL and print the final outcome for each file:

```bash
for evidence in /tmp/axi-sc-mlx-draft.jsonl /tmp/axi-sc-mlx-native-mtp.jsonl; do
  /Users/edr/code/JouleWise/.venv/bin/python -c \
    'import json,sys; rows=[json.loads(x) for x in sys.stdin if x.strip()]; assert rows and rows[-1]["event"]=="probe_outcome"; print(json.dumps(rows[-1],sort_keys=True))' \
    < "$evidence"
  shasum -a 256 "$evidence"
done
```

Historical lead-closeout checklist (**completed 2026-07-17**):

1. Attach or durably reference the exact JSONL outputs and their SHA-256
   values.
2. Confirm every row's requested mode, target, draft/null, proposal cap,
   output cap, request ID, and prompt hash agree with `probe_start`.
3. For external draft, verify distinct loaded target/draft paths, both model
   call counts positive, complete draft identity, generation/terminal output
   identity, direct `from_draft` acceptance flags, and the honest null/absent
   proposal/rate/emission fields.
4. Replace the historical `PENDING-LIVE` state only with the evidence-derived
   outcome. Do not
   reinterpret `runtime_unavailable` as unsupported or promote
   generation-only evidence to `supported`.
5. Keep the external-draft and native-MTP records separate. Feed any future
   native-MTP candidate selection into D-016 rather than selecting scope here.

## Dated closeout — 2026-07-17

The earlier `PENDING-LIVE`, missing-draft, and sandbox-only text above is
history retained with explicit supersession. The lead-run Metal artifacts and
their hashes are attached under
`docs/process_traces/2026-07-17-axi-sc-live-probes/`.

1. **Does the exact external target/draft pair execute? — Yes.**
   `axi-sc-mlx-draft.jsonl` records the requested Qwen2.5-1.5B target and
   Qwen2.5-0.5B draft, distinct loaded paths, positive target/draft call counts,
   complete draft identity, completed generation, and matching terminal token
   IDs/hash. Evidence SHA-256:
   `559731f48f035b86e6dc2545543f70c7af861705a3b443c52d8483eac0645f11`.
2. **Is external draft claim-instrumentable under pinned mlx-lm 0.31.3? —
   No.** Accepted tokens are directly observable through
   `GenerationResponse.from_draft`, but actual proposal counts, aggregate
   acceptance rate, and decode-step emission boundaries are absent. The
   evidence-derived outcome is
   `unsupported_for_joulewise(event_observability)`. Revisit this mechanism
   only when a newly pinned runtime exposes and exercises all three callback
   surfaces; configured caps or reconstructed groups do not trigger revisit.
3. **Does pinned mlx-lm 0.31.3 execute native MTP? — No.**
   `axi-sc-mtp.jsonl` records the pinned source identity and the absence of a
   native-MTP generation surface; the evidence-derived outcome is
   `unsupported_for_joulewise(native_mtp_generation)`. Evidence SHA-256:
   `f7ab880040ae5f17e58d97db5a2cbe9b492b1dd6b994c0e8b5a7a45d05b44eeb`.
   Revisit native MTP only when a newly pinned runtime retains MTP weights,
   executes an identifiable native path, and supplies the same AXI-SA counters
   and step boundaries.
4. **Is an AXI-SC Mac energy leg minted? — No.** Both mechanism questions are
   closed unsupported for this pin, so no support registry row or energy claim
   follows. DSpark/DFlash implementations, if evaluated, are separate
   mechanism rows with their own evidence rather than evidence against this
   closed result.
