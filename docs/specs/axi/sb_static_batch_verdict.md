# AXI-SB — pinned mlx-lm static-batch feasibility verdict

- Date opened: 2026-07-16
- Runtime pin: `mlx-lm==0.31.3`, `mlx==0.31.2`
- Verdict: **`supported`** (2026-07-16, lead-run live probes at B=2 and B=4;
  evidence: `docs/process_traces/2026-07-16-axi-sb-live-probes/`)
- Source-level feasibility: **`feasible_candidate`**
- Memory-fit range: fit at B=2 (peak 968,744,980 B) and B=4
  (peak 1,034,368,392 B) for Qwen2.5-1.5B-Instruct-4bit at 8 max tokens; no
  failing B tested; range not yet bounded above (separate from support
  semantics)
- Mac C5-2.2 registry leg: **minted 2026-07-16** (`docs/research_question_bank.md`
  C5-2.2 Mac leg; per D-070 mint-on-supported rule)

This is an agent-lane feasibility probe, not an energy measurement or a
claim-bearing campaign. It does not use or consume a `[QUIET-MAC]` window.
Continuous batching, coalescing, scheduler-optimum, and offered-load claims
remain out of scope under D-070.

## Installed-source provenance

The delegated worktree did not contain a `.venv` directory. The source review
therefore read the pinned repo venv in the primary checkout at
`/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/`.
`mlx_lm/_version.py:3` records `0.31.3`; distribution metadata reports MLX
`0.31.2`. The live probe independently emits both versions and package roots
and returns `runtime_unavailable(pin_mismatch)` before importing MLX if either
pin differs.

Reviewed-file SHA-256 identities:

| Installed source | SHA-256 |
|---|---|
| `.venv/lib/python3.13/site-packages/mlx_lm/__init__.py` | `f9ffa88772d26e537a98aa39ab16488a7a0d13cc1fac5d665376132c94b49608` |
| `.venv/lib/python3.13/site-packages/mlx_lm/generate.py` | `270778ad53eaca55a8533d82e6752660fe5d2605c4aa0879b48a50a91f69345f` |
| `.venv/lib/python3.13/site-packages/mlx_lm/models/cache.py` | `819ed95dcbf755652363cfdb15a639890447abb534a06dcefd52c7fff5055750` |
| `.venv/lib/python3.13/site-packages/mlx_lm/models/qwen2.py` | `30d38786f3c598bf58c1dafcdffbeac6f3c507442bde768944350c57222cf391` |
| `.venv/lib/python3.13/site-packages/mlx_lm/server.py` | `cdfcb4ac848636f9927851a0ec7a951584526530cb7832ba58049e4a9144db8b` |

## Questions to resolve

- Does the pinned implementation execute one genuine model batch with
  realized `B > 1`, rather than loop over singleton calls?
- Can every request be mapped to its own output token IDs and count, terminal
  stop reason, token/phase timestamps, and request-scoped lifecycle hooks?
- Which tested batch sizes fit the named model and machine? This answer is
  recorded separately and cannot upgrade or downgrade runtime support.

## Binding classification

The final live classification is mechanical:

| Verdict code | Required evidence |
|---|---|
| `supported` | One insertion of a roster with configured `B > 1`; realized B equal to configured B; distinct runtime UIDs for all requests; at least one observed model call whose leading dimension equals configured B; and every request has output token IDs/count, a stop reason, timestamps for all committed tokens plus a terminal timestamp, and request-scoped prefill/decode/lifecycle hooks. |
| `unsupported_for_joulewise(native_batch_execution)` | The runtime is present but the live path does not prove a true `B > 1` model call, including any Python loop over B singleton generations, or the pinned batch path fails during execution. |
| `unsupported_for_joulewise(event_observability)` | True batch execution occurs, but any request lacks identity, output token IDs/count, stop reason, timestamps, or the request-scoped hook surface required by the AXI-SA event model. |
| `runtime_unavailable` | The pinned environment cannot be exercised: pin mismatch, missing model artifact, MLX/Metal import failure, Metal unavailable, model-load failure, worker launch/protocol failure, or timeout. This is not a support verdict. |
| `PENDING-LIVE` | No attached live output yet. Source inspection alone cannot prove execution or memory fit. |

`scripts/axi_sb_static_batch_spike.py:classify_observation` implements these
rules. In particular, `insert_call_count == 1`, configured and realized B
equality, and an observed model-call
`batch_dimension == requested_batch_size > 1` are independent of per-request
observability. The classification function does not read the separate
`memory_fit_observation` event.

## Recorded source evidence

### True batch-generation surface

- `batch_generate` is a public top-level API: `mlx_lm/__init__.py:10` imports
  it and `mlx_lm/__init__.py:16` exports it. Its signature accepts a list of
  tokenized prompts and a scalar or per-prompt token cap
  (`mlx_lm/generate.py:1887`, `mlx_lm/generate.py:1890`,
  `mlx_lm/generate.py:1892`). It inserts the complete prompt roster in one
  call (`mlx_lm/generate.py:1930`), so the public convenience path is not a
  Python loop over singleton generation calls.
- Prompt processing constructs a two-dimensional batch, including right
  padding for unequal prompt lengths (`mlx_lm/generate.py:1142`,
  `mlx_lm/generate.py:1150`, `mlx_lm/generate.py:1155`), then calls the model
  with `tokens[:, :n_to_process]` (`mlx_lm/generate.py:1160`). Decode likewise
  calls the model once with `inputs[:, None]`
  (`mlx_lm/generate.py:1327`, `mlx_lm/generate.py:1332`). Those are the
  source-level predicates for genuine tensor execution at B, subject to the
  live model-call shape observation.
- The prompt processor merges per-sequence caches into a batch cache
  (`mlx_lm/generate.py:1034`, `mlx_lm/generate.py:1036`). The selected Qwen2
  model exposes ordinary layers (`mlx_lm/models/qwen2.py:219`), so the default
  cache factory produces one `KVCache` per layer
  (`mlx_lm/models/cache.py:31`, `mlx_lm/models/cache.py:34`,
  `mlx_lm/models/cache.py:40`). `KVCache.merge` delegates to
  `BatchKVCache.merge` (`mlx_lm/models/cache.py:396`,
  `mlx_lm/models/cache.py:398`), whose merged arrays have leading dimension B
  (`mlx_lm/models/cache.py:1089`, `mlx_lm/models/cache.py:1098`,
  `mlx_lm/models/cache.py:1104`). This makes the selected model a source-level
  batch candidate; live execution remains required.

### Per-request observability surface

- Each inserted sequence receives a stable numeric UID
  (`mlx_lm/generate.py:1649`, `mlx_lm/generate.py:1652`,
  `mlx_lm/generate.py:1655`). Prompt-progress responses carry that UID,
  processed/total progress, and end-of-prompt state
  (`mlx_lm/generate.py:1012`, `mlx_lm/generate.py:1014`,
  `mlx_lm/generate.py:1017`); `BatchGenerator.next()` returns those responses
  to the caller (`mlx_lm/generate.py:1847`, `mlx_lm/generate.py:1854`). The
  harness maps each UID to a predeclared JouleWise request ID and timestamps
  these returned hooks.
- Each decode response carries `uid`, token ID, and `finish_reason`
  (`mlx_lm/generate.py:1237`, `mlx_lm/generate.py:1239`,
  `mlx_lm/generate.py:1242`). `GenerationBatch.next()` produces one response
  for every active sequence (`mlx_lm/generate.py:1405`,
  `mlx_lm/generate.py:1419`, `mlx_lm/generate.py:1464`) and distinguishes
  length from stop-sequence termination (`mlx_lm/generate.py:1423`,
  `mlx_lm/generate.py:1425`, `mlx_lm/generate.py:1430`,
  `mlx_lm/generate.py:1431`). This is sufficient to derive per-request token
  IDs/counts and stop reasons without parsing text.
- The response dataclasses contain no native timestamp field
  (`mlx_lm/generate.py:1012`, `mlx_lm/generate.py:1237`). The required hook is
  nevertheless synchronous: the server itself consumes prompt and generation
  responses by UID immediately after `batch_generator.next()`
  (`mlx_lm/server.py:851`, `mlx_lm/server.py:853`, `mlx_lm/server.py:858`,
  `mlx_lm/server.py:882`). The probe follows the existing JouleWise
  `stream_generate` adapter idiom: it takes a monotonic timestamp when each
  `next()` result returns, emits one event per UID, and records the shared
  return timestamp honestly for responses from the same scheduler step.
- The high-level `BatchResponse` exposes only texts, aggregate `BatchStats`,
  and optional caches (`mlx_lm/generate.py:1872`,
  `mlx_lm/generate.py:1882`, `mlx_lm/generate.py:1884`). Although
  `batch_generate` internally groups tokens by UID
  (`mlx_lm/generate.py:1930`, `mlx_lm/generate.py:1931`,
  `mlx_lm/generate.py:1946`), it discards token IDs and finish reasons from its
  return (`mlx_lm/generate.py:1952`, `mlx_lm/generate.py:1963`). Therefore the
  high-level convenience function alone is
  `unsupported_for_joulewise(event_observability)`; the feasibility candidate
  depends specifically on the lower-level `BatchGenerator.next()` surface.

### Static scope despite a continuous-capable primitive

`BatchGenerator` is documented as a continuous-batching component
(`mlx_lm/generate.py:1486`, `mlx_lm/generate.py:1488`). The probe does not test
that scheduler mode. It freezes a static cohort by inserting all B requests
once before the first `next()`, setting both prompt and completion capacity to
B, never admitting another request, and draining the cohort to completion.
This mirrors the one-shot structure of `batch_generate`
(`mlx_lm/generate.py:1917`, `mlx_lm/generate.py:1930`,
`mlx_lm/generate.py:1933`) while retaining lower-level observation.

## Live probe and expected artifact

The model is the local mirror named by
`configs/examples/mac_mlx_local.json`:

`/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit`

At source-review time that directory and its `config.json` were present and
the mirror occupied approximately 839 MiB. The delegated worktree's `.venv`
was absent; run the command from a checkout where `.venv/bin/python` is the
pinned repo venv. The harness treats either a missing model or missing/mismatched
venv as structured `runtime_unavailable` evidence and does not fetch anything.

Required semantic pass (small B=2 confirmation):

```bash
.venv/bin/python scripts/axi_sb_static_batch_spike.py \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --batch-size 2 \
  --max-tokens 8 \
  --timeout-seconds 180 \
  > /tmp/axi-sb-b2.jsonl
```

Check that every output line is JSON and inspect the final outcome:

```bash
.venv/bin/python -c 'import json,sys; rows=[json.loads(x) for x in sys.stdin if x.strip()]; print(json.dumps(rows[-1],sort_keys=True)); assert rows[-1]["event"]=="probe_outcome"' < /tmp/axi-sb-b2.jsonl
```

Optional memory-fit ladder, still a feasibility probe and not an energy run:

```bash
for b in 2 4 8 16; do
  .venv/bin/python scripts/axi_sb_static_batch_spike.py \
    --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
    --batch-size "$b" --max-tokens 8 --timeout-seconds 180 \
    > "/tmp/axi-sb-b${b}.jsonl"
done
```

Each successful point emits a separate `memory_fit_observation` containing
the tested B, `fit`, peak MLX memory when available, and
`range_established:false`. The lead may summarize the largest tested fitting B
and first tested failing B as the memory-fit interval; it must not use that
field to alter `supported` or either `unsupported_for_joulewise(...)` code.

## Current evidence and verdict

Attached live probe outputs (lead-run 2026-07-16, Metal live, repo venv):
`docs/process_traces/2026-07-16-axi-sb-live-probes/axi-sb-b2.jsonl`
(SHA-256 `ba632327dd16940b42d017600f7c7864a2dc8c8ee7a81a2cf072af249ee9f612`)
and `.../axi-sb-b4.jsonl`
(SHA-256 `e0e5804dacc1270ee94561988314274fcda1b4159e3e2b2cb436ea448616951b`),
with the closeout-procedure checks recorded in that directory's README:
configured == realized B on every model call (prefill `[B,prompt]`, decode
`[B,1]`), `insert_call_count` == 1, B distinct `request_id`s each with output
token IDs + SHA-256, counts, `length` stop reasons, per-token timestamps, and
all four phase hooks. The earlier no-Metal sandbox smoke
(`runtime_unavailable(runtime_import_failed)`) remains degradation evidence
only.

Current verdict: **`supported`**.

Lead closeout procedure:

1. Attach or durably reference the exact JSONL output and record its SHA-256.
2. Confirm the final `probe_outcome` agrees with the preceding
   `batch_observation`; double-check configured and realized B,
   `insert_call_count`, runtime UID count,
   observed leading batch dimensions, per-request counts/hashes/stop reasons,
   timestamps, and phase hooks.
3. Replace only the verdict and memory-fit fields supported by those outputs.
4. Mint the Mac C5-2.2 registry leg only for `supported`. This document does
   not mint it.

## Negative-verdict filing rule (Hailo idiom)

If the live result is negative, retain this dated feasibility document as an
applicability finding instead of implementing a backend path. Record the exact
structured code, the attached evidence, per-question answers, and any optional
reproduction step; leave the Mac C5-2.2 leg absent. This mirrors the Hailo
filing shape: explicit questions, verdict vocabulary, dated current verdict,
recorded evidence, per-question answers, and a scope consequence. A negative
result does not become an energy claim and does not schedule a quiet-Mac
campaign.
