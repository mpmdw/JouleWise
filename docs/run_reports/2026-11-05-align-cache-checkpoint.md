# ALIGN hybrid cache checkpoint implementation — 2026-11-05

Current status: **opt-in, rebuild-only by default; fixes and current evidence
are recorded in [Fix round](2026-11-05-align-cache-checkpoint-native.md#fix-round)**.
The review reports the original native gate passed 4/4 and both supplied config
hashes match pinned upstream revisions. This fix round does not rerun native
tests. No production readiness or energy savings claim is made.

The sections below preserve the original implementation run's historical
evidence, counts and limitations. They are superseded by the linked fix round
where they describe current defaults, native status, provenance or copy cost.
The self-reported **intake slip** below remains part of the custody record;
no unqualified claim of a clean custody audit is made.

Branch: `lane/2026-11-05-align-cache-checkpoint`.
Base: `c9a0a39437614176bf4e14ff1565a6e4537328fb`.
Implementation commit: `0ba413d40` (`ALIGN: checkpoint and restore hybrid prompt caches at turn boundaries`).
This report is committed separately after that implementation commit.

## Authority and intake

Executed the user's bounded `[AGENT]` implementation brief ahead of historical
queue pointers. Read the repository instructions, Mission M0, generated stop
card (NONE), relevant status/workspace sections, queue and do-not-do-yet list,
source-of-truth map, ALIGN cache protocol and pinned dependency references.
The initial tree was clean and detached at the requested base. No agent was
delegated work. No commit was pushed.

The user's standing rules supersede the ordinary state-update/full-suite
checklist: `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`
and `tests/test_gen_state.py` were not edited; no task was registered. The
full suite was not run. No network, quiet-window collection, production-model
load or block-5 analysis pipeline was used.

**Intake slip:** while looking for offline model-config/cache API references,
I read a short excerpt of the clone-local `configs/bytes/bytes_manifest.json`
and its Next header record before recognizing the former's runtime-derived
cache metadata. This was not a block-5/raw-run read, but it exceeded the brief's
broader instruction against reading real measurement-derived data. I stopped
that inspection and did not use those runtime shapes or values as sizing or
exactness evidence. No referenced absolute model/data path was followed.

## Changes and design

- `joulewise/align/apple/prompt_cache.py`: default two-checkpoint ring for the
  exact `ArraysCache`/non-rotating `KVCache` mixture; deep-copy entire recurrent
  cache objects, save KV offsets, restore the newest compatible checkpoint and
  invalidate overwritten branches. Unknown layouts retain whole-cache fallback.
  Config-shape sizing and actual payload accounting are included.
- `joulewise/align/apple/endpoint.py`: choose the closed-history token-prefix
  boundary before the mutable assistant preamble; arrange the measured boundary
  prefill and attach checkpoint observations to per-turn generation records.
- `joulewise/adapters/mlx_runtime.py`: optional prefill hook inside the existing
  prefill phase; retain counts for the entire fed delta even when the hook
  prefills part of it before native streaming.
- `joulewise/align/apple/workload.py`: hybrid configs gain a fixed checkpoint
  policy identity. Non-hybrid policy bytes stay unchanged. Energy-model terms,
  exclusions, predictors and stopping rules are unchanged.
- `tests/align/test_cache_checkpoint.py`: synthetic causal recurrence and
  endpoint integration; deep-copy isolation, repeated restores, selection,
  eviction, fallback, offsets, byte/token accounting and identity checks.
- `tests/align/test_cache_checkpoint_native.py`: optional tiny random mlx-lm
  Qwen3-Next numerical/shape gate, without weights, tokenizer or data access.
- `tests/align/fixtures/prompt_cache_c9a0a394.py`: untouched base cache source
  as a compatibility oracle. Its Git blob matches the base source exactly:
  `69b1e6fe66d8211ed13aa2e3415e285d1be7e15d`.
- `tests/align/fixtures/qwen38_config.json`: byte-identical copy of the
  user-provided `.hf-qwen38/config.json`.
- `docs/align/hybrid_cache_checkpoints.md`: full design, observations, sizing,
  exactness gate, offline-source limitations and next validation command.
- This report contains coordination handoff in place of lead-owned state edits.

The closed-history boundary is a candidate: arbitrary templates cannot be
promised stable from one render alone. Correctness always requires the actual
next token LCP. If a template rewrites before the newest candidate, an older
matching checkpoint is restored; if none remains, the full rebuild is explicit.
No recurrent state is paired with independently rewound KV state. At least one
prompt token remains for native generation.

The member's `generation` record logs `cache_prefill_tokens_saved`,
`cache_checkpoint_restore_count` and `cache_checkpoint_restore_bytes`, plus
boundary/restore offsets, policy, ring limit/count, latest/retained payload bytes
and available config-derived sizing. These remain observations only.

## Memory and evidence limits

Assuming batch one, bf16 convolution history and fp32 recurrent state:

| Model | Bytes per checkpoint | MiB | Evidence |
|---|---:|---:|---|
| Qwen3.8-27B | 153,944,192 | 146.8126 | Computed from clone-provided config: 48 linear/16 full layers, Hk=16, Hv=48, Dk=Dv=128, kernel=4 |
| Qwen3-Next-80B-A3B | 77,267,040 | 73.6876 | **Conditional arithmetic only**, assuming 36 linear/12 full layers, Hk=16, Hv=32, Dk=Dv=128, kernel=4; published config unavailable |

The Qwen3.8 fixture SHA-256 is
`8f80874ac3ad8fa386d3f6dc0ea85377f703376e009a03dee0360e08e289a25d`.
The Next estimate is not claimed to satisfy the requested published-config
verification. An asynchronous request for clone-local offline sources/config
was unanswered at handoff; no network or external home-directory lookup was
used to fill the gap.

Two retained snapshots cost about 293.6252 MiB for Qwen3.8 and, under the
unverified assumptions, 147.3752 MiB for Next. These are logical payloads,
including eight bytes per KV offset, not resident-memory measurements. No KV
tensors are copied. Active recurrent state, Python/allocator overhead and the
temporary additional snapshot during replacement are extra.

`mlx_lm` was unavailable to both `python3.13` (3.13.18) and default `python3`
(3.14.6); no vendored mlx-lm implementation was found. References actually
read were `env/mac-measurement-lock.txt` (mlx 0.31.2/mlx-lm 0.31.3), the existing
adapter and persistence spike, and `docs/align/pilot_protocol_v2.md`. Neither
pin was changed. Upstream source compatibility and deep-copy behavior could
not be audited against an installed package.

The native unittest requires bitwise restored/fresh logits for demonstrated
deterministic matched schedules; it separately compares one-shot full prefill
with `atol=rtol=1e-5` for float32 and `0.015625` for bf16 because chunk boundaries
can change reduction order. It prints actual differences when executed. Here
it **skipped**, so there is no native logit, dtype/shape or resource-use result.
The tiny model is intended to remain far below 1 GB, not a measured memory bound.
Production Next-Thinking/Qwen3.8 template behavior also remains a live gate.

## Verification

Individually selected unittest modules; no full-suite discovery. Final selected
module results total **111 passed, 2 skipped** (113 selected tests). The skips
include the entire new native numerical gate and one existing optional pilot-4
test. Aggregate final module wall time was about 145 seconds, comfortably under
the requested 20-minute test budget, with brief focused reruns during authoring.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint` | 10 passed |
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint_native` | 1 skipped: pinned native packages absent |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 passed |
| `python3.13 -B -m unittest tests.align.test_pilot4` | 17 passed, 1 skipped |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 passed |
| `python3.13 -B -m unittest tests.test_mlx_runtime` | 43 passed |
| `PYTHONPATH=tests python3.13 -B -m unittest tests.test_mlx_runtime_detokenizer` | 8 passed |
| `python3.13 -B -m compileall -q joulewise tests` | Passed |
| `git diff --check` | Passed |
| `git diff --exit-code -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | No changes |

The detokenizer command without `PYTHONPATH=tests` initially failed to import
its pre-existing top-level `test_mlx_runtime` helper; the command above resolves
that harness path and passes. Test scaffolding errors encountered during
authoring were corrected before the listed final passes.

## Next exact step / open questions

1. Put an offline installation/source of **mlx 0.31.2 + mlx-lm 0.31.3** and the
   published Next `config.json` inside the clone. Audit the actual cache/model
   APIs and run `python3.13 -B -m unittest tests.align.test_cache_checkpoint_native`.
   Fix any API, shape or numerical failure; retain the printed numerical evidence.
2. Authenticate the Next config and replace its conditional sizing row with
   `checkpoint_size_from_config` output. Verify actual cache dtypes as part of
   the native gate; config precision alone is not runtime evidence.
3. Lead reviews the boundary behavior on the intended Next-Thinking/Qwen3.8
   templates and performs any production rehearsal in a clean lead-controlled
   machine-state lane. This agent session did not start that work.

Numerical exactness, upstream compatibility, actual peak memory and a verified
published-config Next size remain open. These limitations are not waived by
the passing synthetic tests or the local commits.
