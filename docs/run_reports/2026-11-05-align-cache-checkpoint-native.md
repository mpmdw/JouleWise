# ALIGN checkpoint native follow-up — 2026-11-05

Branch: `lane/2026-11-05-align-cache-checkpoint`; starting head `46eaf3b79`.
This follow-up supersedes the earlier report's dependency-availability finding.
**Current evidence:** the PR #657 review reports the original native gate passed
4/4 and the benchmark passed on mlx 0.31.2 / mlx-lm 0.31.3. Restored logits were
bitwise equal at boundaries 512 and 73 for both families/dtypes. That is supplied
review evidence, not a native result from this sandbox. The revised 2048-token
path and native context test still require a lead rerun. See [Fix round](#fix-round).

Items 1–4 and their verification/open-question sections below preserve the
historical follow-up's blocked attempts. Current conclusions, config provenance
and latency interpretation are superseded by the fix round. The original
report's self-reported intake slip remains disclosed; custody is not described
as unqualifiedly clean.

## Authority and safety

Continued the user's explicit four-item lane brief. Read repository instructions,
Mission M0, generated stop card (NONE), queue/do-not-do list, workspace/status
pointers, D-009, the existing cache design/report and pilot protocol. Initial
tree was clean. The explicit brief overrides historical queue ordering and the
normal coordination-state/full-suite close-out requirements.

No network, real measurement data, block-5 analysis, production model weights,
tokenizer or quiet-window experiment was accessed. Absolute study paths in
repository prose were treated as text. Only clone-local sources/configs and
the explicitly supplied `/private/tmp/jwsol/venv-mlx` installation were used.
The venv was not modified (commands set `PYTHONDONTWRITEBYTECODE=1`). No agent
was delegated, integration installed, commit pushed, or coordination state edited.

## Item 1 — native gate and installed-source audit

The supplied interpreter reports **mlx 0.31.2 / mlx-lm 0.31.3**. Inspected its
`qwen3_next.py`, `qwen3_5.py`, `gated_delta.py`, `cache.py`, and MLX API stubs.
Qwen3.8's supplied config is outer `qwen3_5`, nested `qwen3_5_text`; the native
`qwen3_5.Model` wrapper constructs its text model without a vision tower.
Both classes use three `ArraysCache` layers per full-attention `KVCache` at
interval four. Recurrent state is `[B, Hv, Dv, Dk]`, explicitly float32 in
`gated_delta_update`; convolution history follows activation dtype. Corrected
the formula's shape docstring (byte arithmetic is unchanged).

The previous tiny test never called `model.eval()`. MLX modules start in training
mode; both model classes pass `use_kernel=not self.training`. The new reusable
gate explicitly enters inference mode and requires a working Metal device.

`scripts/align_cache_checkpoint_native.py` builds four-layer random models from
the installed classes, float32/bf16, with Next MoE and Qwen3.5 dense MLPs.
It synthesizes consecutive turn rewrites of exactly **143, 257, 560 tokens**,
with seven consumed output tokens per turn, repeated restoration and a pristine
independent prefix to check snapshot ownership. No pilot token fixture is read.
It checks runtime payload/dtypes, offsets, finite logits, repeat determinism and
bitwise equality including signed-zero bits via uint8 views.

Two prefix lengths are used: 512 and 73. Fresh references re-prefill every token
with the same prefix/suffix chunk schedule. At prefix 512 that is also ordinary
512-token full prefill. Prefix 73 checks a partial checkpoint boundary. A separate
single-call full prefill reports its actual maximum error; it does **not** get
an invented tolerance or count as bitwise evidence. Changing GEMM/recurrence
chunk shapes is a different computation schedule even with deterministic
kernels. Nondeterminism or a matched-schedule mismatch fails the gate; neither
is silently converted into an allclose pass.

Execution results:

- Existing unittest: 1 attempted, **ERROR** at `mlx.nn` import, before any model
  or logits, with `[metal::load_device] No Metal device available`.
- Selecting `mx.cpu` also fails at the same decorator import; disabling compile
  additionally does not help. These were preflight attempts, not CPU evidence.
- New driver: exit **1**, same Metal error at device preflight; peak process RSS
  **34,258,944 bytes** (32.67 MiB), before any tiny model. `mx.metal.is_available()`
  says True here and is insufficient as a usable-device test.

No sandbox escape, permission bypass or venv change was attempted. The native
model paths are source-audited but **not execution-validated** in this sandbox.

Reproduce in a Metal-visible session, without starting any production workload:

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /private/tmp/jwsol/venv-mlx/bin/python -B scripts/align_cache_checkpoint_native.py
```

The driver uses 384 MiB MLX memory and 32 MiB allocator-cache guidelines, tiny
fixed dimensions and a 900 MiB process peak-RSS guard between evaluated stages.
MLX's memory setting is explicitly a **guideline**, not a hard RSS cap. Cases
are sequential. Production-config models are never instantiated.

## Item 2 — supplied-config sizing

Retained a byte-identical `.hf-next/config.json` copy at
`tests/align/fixtures/qwen3_next_config.json` (22,138 bytes), SHA-256
`f5a5422b8e3d47733f0073ff22dec1dc4a7832fec5fc1cf36eba31ace03cf0c4`.
User identifies the source as mlx-community; no upstream revision was verified
without network. Qwen3.8's supplied config still matches the earlier fixture
hash `8f80874ac3ad8fa386d3f6dc0ea85377f703376e009a03dee0360e08e289a25d`.

For Next: 36 recurrent / 12 full-attention layers, Hk=16, Hv=32, Dk=Dv=128,
convolution kernel=4. bf16 history + fp32 recurrence gives:

- Convolution: **49,152 B/layer**; recurrence: **2,097,152 B/layer**.
- Recurrent arrays: **77,266,944 B**; twelve logical u64 offsets: **96 B**.
- One checkpoint: **77,267,040 B = 73.6875916 MiB**.
- Two retained: **154,534,080 B = 147.3751831 MiB**.
- fp32 convolution sensitivity: **79,036,512 B/checkpoint**.

Updated the design's conditional Next row to supplied-config evidence and added
a fixture-backed regression. Qwen3.8 remains **153,944,192 B/checkpoint**,
**293.6252441 MiB/two**. These are payload estimates, not measured residency.
Neither weights' quantization nor config precision proves cache dtype; the
Metal-blocked native runtime dtype check remains outstanding.

## Item 3 — resource probe, attempt and extrapolation

Added `--benchmark` and MLX-free `--estimate-only` modes to the native driver.
The benchmark measures synchronous `_snapshot`/`_restore`, three warmups then
25 samples, with suffix mutation outside timing. It excludes duplicate snapshot
no-ops and reports operation-local active MLX memory, raw wall times, allocator
cache and process peak RSS. It never constructs a model from a real config.

Benchmark execution: **exit 1**, same Metal initialization error, before any
timed operation. Peak process RSS at failure was **36,634,624 B (34.94 MiB)**.
This is measured failed-preflight resource use, **not** tiny-model or copy cost.
No native wall time, allocated snapshot memory or timing extrapolation is
available. The long seven-worker job was not inspected or modified.

Config-only estimate mode: **PASS**, four family/dtype rows, timing fields null.
bf16-history projections (all state recurrence float32):

| Quantity | Next | Qwen3.8 / qwen3_5 |
|---|---:|---:|
| Tiny copied recurrent arrays | 26,880 B | 39,744 B |
| Real copied recurrent arrays | 77,266,944 B | 153,944,064 B |
| Real/tiny byte ratio | 2,874.5143 | 3,873.3913 |
| Three snapshot array sets during replacement | 231,800,832 B | 461,832,192 B |
| Four sets including active recurrence, conservative allowance | 309,067,776 B | 615,776,256 B |

Two-retained payload is listed under item 2. Three/four-set figures exclude
weights, KV, offsets, Python/allocator overhead and kernel workspace; they are
not RSS bounds. Real-layer counts are 12× and 16× the three-linear-layer tiny
models, so fixed object overhead also scales differently from array bytes.
Future timing output includes `tiny_median_ms × real_state_bytes / tiny_state_bytes`
as an explicit byte-proportional scenario, not a prediction or confidence bound.
Under the current blocker it correctly reports no timing numbers.

## Item 4 — suite integration and final review

Replaced the original optional one-family test with four native tests covering
both installed model families and both dtypes. Each runs aligned and partial
boundaries and all three rewrites through the same gate as the executable.
Missing native packages skip; installed-but-unusable Metal fails class setup.
Added three stdlib probe tests for real-config routing, memory projections with
no unmeasured times, and an estimate-only CLI guarded against any MLX import.
Updated the design document to the current gate; removed obsolete unavailable-
dependency wording and prospective, unmeasured allclose tolerances.

Final diff review: eight paths changed across the four items:

- `scripts/align_cache_checkpoint_native.py`: reusable native gate and benchmark.
- `tests/align/test_cache_checkpoint_native.py`: optional native suite integration.
- `tests/align/test_cache_checkpoint_probe.py`: offline probe/config checks.
- `tests/align/test_cache_checkpoint.py`: supplied Next sizing regression.
- `tests/align/fixtures/qwen3_next_config.json`: byte-identical supplied config.
- `joulewise/align/apple/prompt_cache.py`: shape docstring correction only.
- `docs/align/hybrid_cache_checkpoints.md`: current design/evidence limitations.
- This report: coordination handoff and execution evidence.

One local commit per brief item; none pushed:

1. `fd3cd207b` — two-family native gate and Metal blocker.
2. `58a436a13` — Next supplied-config payload calculation.
3. `fdb3ddf03` — resource probe and explicit payload projections.
4. `ALIGN: integrate optional two-family native checkpoint tests` — this final
   suite-integration/report commit; its hash is in the final handoff.

## Verification

Modules were run individually; no full-suite discovery, pipeline or real-data
replay. Final successful selection: **14 tests passed** with the supplied
interpreter (11 mechanics + 3 probe). The four numerical tests did **not** run:
class setup failed before a model was created. The bare interpreter separately
confirmed the missing-dependency skip behavior. Test execution was well below
the 20-minute budget (selected tests and failed preflights total seconds).

For the commands below, `$MLXPY` denotes exactly
`/private/tmp/jwsol/venv-mlx/bin/python`, not a changed venv. Native commands
also set `PYTHONDONTWRITEBYTECODE=1`, `HF_HUB_OFFLINE=1`,
`TRANSFORMERS_OFFLINE=1`, and a scratch `HF_HOME` under `/private/tmp`.

| Command | Final result |
|---|---|
| `PYTHONPATH=. $MLXPY -B -m unittest tests.align.test_cache_checkpoint` | 11 PASS, 0.011 s |
| `PYTHONPATH=. $MLXPY -B -m unittest tests.align.test_cache_checkpoint_probe` | 3 PASS, 0.122 s |
| `PYTHONPATH=. $MLXPY -B -m unittest tests.align.test_cache_checkpoint_native` | ERROR at class setup, 0 tests run, 0.146 s; Metal unavailable |
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint_native` | 4 SKIP; packages absent in this interpreter |
| `PYTHONPATH=. python3.13 -B scripts/align_cache_checkpoint_native.py --estimate-only` | PASS; four config rows, timing null |
| `PYTHONPATH=. $MLXPY -B scripts/align_cache_checkpoint_native.py` | Exit 1; Metal preflight error, no logits |
| `PYTHONPATH=. $MLXPY -B scripts/align_cache_checkpoint_native.py --benchmark` | Exit 1; Metal preflight error, no copy samples |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_cache_checkpoint_native.py` | PASS |
| `git diff --check` | PASS after removing an extra doc EOF blank line |
| `git diff --exit-code 46eaf3b79 -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | PASS; no protected path changes |

Earlier authoring checks (not additional native evidence):

- `python3.13 -B -m py_compile scripts/align_cache_checkpoint_native.py`: PASS.
- `python3.13 -B -m unittest tests.align.test_cache_checkpoint`: 11 PASS (0.008 s).
- `PYTHONPATH=. python3.13 -B scripts/align_cache_checkpoint_native.py --estimate-only`:
  PASS, four config-only rows. Initial invocation without `PYTHONPATH=.` failed
  to resolve `joulewise`; the documented command above corrects the invocation.
- Supplied interpreter, same driver with `--benchmark`: exit 1, Metal blocked.
- `git diff --check`: PASS.
- Native commands above: blocked/error, not passed or skipped numerical gates.

## Open questions and next exact step

1. **Blocking environment:** why is a Metal device inaccessible to this session
   despite installed MLX? No device-permission bypass is authorized here. Run
   the exact pinned unittest command above from a permitted Metal-visible
   session, followed by the driver with `--benchmark`. Keep the tiny-model
   limits and sequential execution. Fix and rerun any constructor, numerical
   or resource failure; the native path has not yet been execution-validated.
2. **Unmeasured:** restored/full max abs error, kernel determinism, actual
   runtime cache dtype/shape, copy latency and model-loaded peak memory. None
   is inferred from config arithmetic or the failed preflight RSS.
3. **Scope of eventual evidence:** partial-boundary equality is checked against
   a full matched-schedule re-prefill. The one-shot diagnostic cannot establish
   universal equality across schedules, and synthetic rewrites do not validate
   the production chat templates or production quantized weights.
4. **Provenance:** both configs are the user-provided clone-local bytes; upstream
   revision identity has not been independently authenticated without network.

Item 2 is complete and item 4 is integrated with skip/setup behavior checked.
Items 1 and 3 are implemented/attempted but remain **blocked**, rather than
claimed complete. Production readiness remains PROVISIONAL.

## Fix round

Executed the user's PR #657 fix brief from clean head `15360a0a0` on new local
branch `lane/2026-11-05-align-cache-checkpoint-fix-657`. Read
`/private/tmp/jwsol/rev-657.json` first: two HIGH, one MEDIUM, five LOW, no
refuted notes or BLOCKER findings. The lead's explicit checkpoint-limit ruling
governs the implementation. No network, measurement data, production weights,
analysis pipeline, quiet-window work or full test suite was used. No agents
were spawned. Commits are local; nothing was pushed. Coordination-state files
and `tests/test_gen_state.py` are unchanged from intake.

Authority gap: `git show origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN.md`
and its Amendment 1 counterpart failed because that ref is absent from this
clone. No matching local ref or reachable file history was found. An async
request for the commit SHA was sent; no reply was received before handoff.
The brief supplies Amendment 1's scope: W1 is **Qwen3.8-27B only**, Next dropped,
Flash-Next later. None of the retained Next tests authorizes it for W1. Exact
B7 reconciliation remains a disclosed LOW disposition below; this report does
not claim to have read the unavailable council texts.

Finding numbering follows the supplied review's order (H1, H2, M1, L1–L5).

| Finding | Fix / disposition | Regression evidence |
|---|---|---|
| H1 — automatically enabled checkpointing | `574322339`: new `EpisodeSpec.hybrid_checkpoint_limit`, default 0; None omitted from spec and execution policy, effective zero. Explicit values enter execution policy and therefore the governed runtime identity hash. Endpoint uses the resolved limit; no implicit enablement. `3c5dea047` updates legacy fixture tests to request omission explicitly. Fix per model before its first measured window and keep fixed for the whole series. | New limit/spec/identity and default-constructor tests failed before the fix, then passed. The existing governed digest test also checks omission versus 0 and distinct hashes for 0/1/2. |
| H2 — identity/runtime family mismatch | `7df9efd02` plus H1's shared resolver: identity and endpoint both call `hybrid_checkpoint_policy(config, limit)`. No identity policy means runtime limit zero even for a hybrid cache. Added nested `qwen3_5_moe_text` and the complete review-retained 122B config fixture. | Real 122B routing failed before the allowlist fix (0 versus expected 2), then passed. Endpoint tests compare identity policy, actual cache limit, snapshot creation, native fed IDs and closed-history render calls for enabled, zero, None and unknown configs. |
| M1 — unwired/default-stream manual prefill, mismatched chunks | `8bf648e94`: manual forwards and snapshot run inside `wired_limit(model, [generation_stream]), mx.stream(generation_stream)` using pinned native 2048-token chunks, with `mx.clear_cache()` after each evaluated chunk. Policy identity records 2048. | Synthetic context regression failed before the fix, then passed with exact forward/clear order for chunks 2048 and 73. New MLX-native context test is written, import-gated and **not executed here**. Native driver/reference chunk size now matches 2048. |
| L1 — stale native/config/test/custody claims | Evidence documentation group (this fix-round documentation commit): current status is separated from historical blocked attempts. Both reports and design now record review-supplied 4/4 native PASS, benchmark PASS, revision-verified config hashes and current local counts. PR-body replacement below carries the same qualifications and both intake slips. | Compared all three fixture byte strings with review-retained configs offline; SHA-256 values below. No fabricated text-only behavior test. External-source import safety is covered by the red/green regression in `3c5dea047`. |
| L2 — arrays described as deep-copied bytes; invalid latency scaling | `86e779797`: describe independent Python containers retaining immutable MLX array storage; remove byte-proportional timing multiplication, including when actual timing input exists. Payload accounting remains logical retention, distinct from allocation. | New probe test failed with fabricated production timing projections before the fix, then passed with null timing and explicit reference-retention semantics. |
| L3 — extra full-history render/encode inside setup | H1 removes this work entirely for the default zero/None and unsupported configs; endpoint regression explicitly checks render call counts. **Remaining LOW deferred:** enabled mode still performs the second render/encode. R1 must measure its context-length cost before enabled measured use. A constant-suffix optimization needs actual-template evidence and is not guessed here. | Enabled/disabled endpoint regression passes. No overhead measurement was performed or inferred. |
| L4 — same metadata key with setup versus post-snapshot values | `581408773`: setup-time count/bytes/retained-bytes remain unchanged in generation provenance; distinct `*_after_prefill` fields report the later state, including turns without a new snapshot. | New integrated endpoint test failed before the fix (setup 0 versus provenance 1), then passed; it checks all three payload/count fields across two turns. |
| L5 — B7 names, boundary and test filename differ | **LOW deferred for lead reconciliation with the actual council texts.** Existing snapshot is before the mutable assistant preamble because thinking tags can disappear next turn; the next prompt's LCP still gates restore. The implementation retains `cache_checkpoint_restore_count`, `cache_prefill_tokens_saved` and `test_cache_checkpoint.py`; no claim is made that these meet B7's names. | No contract fields or amendment were invented without the missing source. Lead should decide the exact `cache_refed_tokens` meaning and record the boundary amendment / desk compatibility mapping. |

The code behavior groups each have observed pre-fix failures and post-fix passes.
L1 is a documentation correction; L3 and L5 explicitly retain uncompleted LOW
work. No native pass from the pre-fix review is counted as a pass of this code.

Changed paths: the three Apple runtime files `endpoint.py`, `prompt_cache.py`,
`workload.py`; `scripts/align_cache_checkpoint_native.py`; five test modules
(`test_cache_checkpoint`, `test_cache_checkpoint_native`,
`test_cache_checkpoint_probe`, `test_pilot3_cache`, `test_pilot4`); the 122B config
fixture; `docs/align/hybrid_cache_checkpoints.md`; and these two run reports.
The final test refinement pins the complete 122B fixture hash and checks render
call counts for the disabled and fail-closed paths.

### Evidence, provenance and custody

The supplied review reports original native tests **4/4 PASS** with mlx 0.31.2 /
mlx-lm 0.31.3: restored versus full matched-schedule logits bitwise equal at
boundaries 512 and 73, both families and dtypes. It also reports benchmark PASS,
zero extra active array bytes per snapshot/restore, and retained-memory results
consistent with the saved payload staying live. Those results supersede the
historical claims of an unexecuted original gate, but do not validate the new
2048-token path/context, arbitrary schedules, quantized production trajectories,
production templates or energy measurements. Tiny benchmark timing is not
scaled into production latency.

The review verified upstream revision provenance; this offline fix round
independently confirmed byte equality with its retained config files:

| Fixture | Review-verified source revision | SHA-256 |
|---|---|---|
| `qwen3_next_config.json` | mlx-community/Qwen3-Next-80B-A3B-Thinking-4bit @ `9a2b4634` | `f5a5422b8e3d47733f0073ff22dec1dc4a7832fec5fc1cf36eba31ace03cf0c4` |
| `qwen38_config.json` | mlx-community/Qwen3.8-27B-8bit @ `815b83c0` | `8f80874ac3ad8fa386d3f6dc0ea85377f703376e009a03dee0360e08e289a25d` |
| `qwen35_122b_config.json` | mlx-community/Qwen3.5-122B-A10B-4bit @ `e9c67b08` | `fc1c3921b5146143cda7a5feed445cc31c8929cc3f164f967ec6340b448086eb` |

The original implementation report's manifest/header intake slip remains
disclosed. This fix round also had a verification slip: initially importing
`tests.align.test_pilot4` evaluated its existing `Path(kit.SHADE_CACHE).is_dir()`
decorator for `/Users/edr/.cache/joulewise/shade`, outside the clone. This was an
out-of-scope stat attempt; the optional test skipped and no contents were read.
The source test now requires explicit `JW_ALIGN_REAL_SHADE_TEST=1` before it
even checks existence. A subprocess regression traps external-home stats and
imports the module with that opt-in absent: it failed on the old decorator and
passes now. Do not describe custody as unqualifiedly clean.

### Final local verification

Modules ran one at a time using unittest; no parallel test processes or full
discovery. Latest complete module outcomes: **122 passed, 6 skipped, 128 selected**.
Five skips are MLX-native tests because packages are absent in `python3.13`;
one is the explicitly opt-in external SHADE source test. Observed aggregate
test time, including authoring failures and reruns, was under four minutes,
within the 20-minute budget. CPU/synthetic passes are not hardware evidence.

| Command | Latest result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint` | 16 PASS, 0.011 s |
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint_probe` | 5 PASS, 0.331 s |
| `python3.13 -B -m unittest tests.align.test_cache_checkpoint_native` | 5 SKIP, 0.000 s |
| `python3.13 -B -m unittest tests.align.test_pilot3_cache` | 12 PASS, 1.449 s |
| `python3.13 -B -m unittest tests.align.test_pilot4` | 17 PASS, 1 SKIP, 16.062 s |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 PASS, 25.349 s |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 PASS, 104.000 s |
| `python3.13 -B -m unittest tests.test_mlx_runtime` | 43 PASS, 0.018 s |
| `PYTHONPATH=tests python3.13 -B -m unittest tests.test_mlx_runtime_detokenizer` | 8 PASS, 0.006 s |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_cache_checkpoint_native.py` | PASS |
| `git diff --check` | PASS |
| `git diff --exit-code 15360a0a0 -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json tests/test_gen_state.py` | PASS, no protected changes |

Earlier red checks were intentional new regressions for H1, H2, M1, L2 and L4,
plus the external-stat import guard. Integration initially failed the two legacy
identity expectations that now explicitly request `hybrid_checkpoint_limit=None`;
both full modules were rerun successfully after correction. No unresolved local
test failure is being hidden by the skip count.

### PR body replacement (local draft; no network publication)

Impact: checkpointing is now an explicit series policy. EpisodeSpec defaults
`hybrid_checkpoint_limit` to 0, preserving rebuild-only execution. An explicit
positive value is hashed into execution policy and must be fixed per model
before its first measured window for the entire series. Enabling it changes the
computation schedule and token trajectory of **every hybrid turn**, including
turn zero and turns without a restore; it cannot be turned on after W1 while
claiming exact W1 seed replays.

The endpoint and identity share one policy resolver, including the real 122B
config's `qwen3_5_moe_text`; a hybrid cache without an identity policy cannot
enable checkpoints. Manual prefill uses native wired-limit/generation-stream
contexts, native 2048-token chunks and per-chunk allocator cleanup. Setup and
post-prefill checkpoint observations have distinct names. MLX snapshots retain
immutable array storage through independent containers; production latency is
not extrapolated from payload bytes.

Validation: 122 local tests pass, 6 skip across nine individually run modules;
compile and protected-file checks pass. The supplied review reports the
**pre-fix** native gate passed 4/4 and its benchmark passed; current revised
native tests need a Metal-visible lead rerun. Config hashes were revision-verified
by the review and byte-matched offline here. Both the original manifest intake
slip and this fix round's optional-test external-path stat attempt are disclosed.
Two LOW follow-ups remain: R1 rendering-overhead measurement for enabled use,
and exact B7 reconciliation after the absent council commit is supplied.
Amendment 1's W1 remains Qwen3.8-27B only. Production readiness is PROVISIONAL.

### Next exact steps / NEEDS_RULING

1. Supply the council branch's commit SHA available in the shared object store.
   **Question:** what exact B7 field semantics and boundary amendment apply?
   Options considered: invent compatibility aliases now, or read the binding
   text and have the lead adopt the mapping/amendment. Recommendation: the
   latter. Blocked work: LOW L5 field/test-name reconciliation and a claim of
   conformance to the complete council documents.
2. Lead runs the following outside this sandbox, with the pinned packages and
   Metal available. This is tiny random-model verification, not permission to
   start a production or quiet-Mac measurement while agents remain active:

   ```sh
   PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
     /private/tmp/jwsol/venv-mlx/bin/python -B -m unittest tests.align.test_cache_checkpoint_native
   PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
     /private/tmp/jwsol/venv-mlx/bin/python -B scripts/align_cache_checkpoint_native.py --benchmark
   ```

   Required native cases: `test_qwen3_next_float32`, `test_qwen3_next_bfloat16`,
   `test_qwen3_5_float32`, `test_qwen3_5_bfloat16` (2048 and 73 boundaries), and
   `test_manual_prefill_native_stream_wiring_and_chunks` (2048 + 73 chunk split).
3. Before enabled measured use, R1 measures the extra closed-history rendering
   overhead and validates the intended production template/schedule. Keep the
   limit fixed for that model's whole measured series. Default-zero use does
   not incur the second render. Lead reconciles L5 and replaces the live PR body
   from the local draft after review; this session made no network write.
