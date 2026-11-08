# 2026-11-07 — fixed-token forced-decode desk implementation

## Scope and authority

User-assigned Stage 0 DESK work for the interp × energy direction, specifically
the teacher-forced replay primitive. Read the design study and the relevant
two-channel/cache critiques in its companion checks file, repo instructions,
Mission M0, targeted restart/queue sections, orchestration guidance and D-009 /
D-013. No active stop card was present. This explicit user assignment selects
this bounded research tooling work ahead of ordinary queue work; the user's
coordination-state ownership overrides normal kernel/handoff updates.

Initial checkout was already the requested clean branch
`interp/2026-11-07-forced-decode`, based on `3edb715df`. Implementation commit:
`500035210` (`Add fixed-token decode replay with lazy MLX backend and synthetic reference`).
This report is delivered in a subsequent documentation commit on that branch.
Commits are local; nothing was pushed. No delegated agents or external consults.

No network, downloads, real model weights, measurement data, telemetry or
block-5 analysis pipeline were used. No external study paths were followed.
Tests use only tiny in-memory models and temporary synthetic files. No full or
quick suite was run, and the existing analysis job was not inspected or touched.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are unchanged; no kernel task was registered.

## Delivered files and behavior

- `joulewise/interp_energy/__init__.py`: dependency-free package import.
- `joulewise/interp_energy/forced_decode.py`: replay API, lazy MLX and NumPy
  backends, token validation, identity helpers and buffered JSONL output.
- `joulewise/interp_energy/reference.py`: a tiny pure-NumPy causal attention
  model with real growing key/value state and reproducible synthetic weights.
- `scripts/interp_energy/forced_decode.py`: local-only native CLI and a
  synthetic NumPy `--dry-run`; accepts exact prompt/continuation token files,
  or raw prompt text. Output files use exclusive creation.
- `joulewise/interp_energy/README.md`: API/CLI usage, schema/hash conventions,
  cache boundary, instrumentation limits and native handoff instructions.
- `tests/interp_energy/__init__.py`, `test_forced_decode.py`,
  `test_reference.py`, `test_forced_decode_mlx.py`: stdlib loop/provenance tests,
  numerical/CLI tests, and gated native tests using a tiny initialized llama.
- This run report.

Replay prefills `prompt[:-1]` in a fixed chunk policy, then feeds only the last
prompt token followed by preceding forced tokens, one ID per model call. It
uses a new model-default cache for every replay; MLX delegates cache creation
to `make_prompt_cache`, including any model-specific cache implementation.
No sampling, logits processors, argmax feedback, EOS stopping, cache trimming or
cache reuse occurs. The last forced token is scored/emitted, and is not yet
cached, matching the normal generation boundary described by the repo's
`spike_mlx_prompt_cache.py`.

The model is put into inference mode and parameters are materialized before
timing. Each token has monotonic-nanosecond forward start/completion and
diagnostic completion, context/input/forced IDs, argmax agreement, full-vocabulary
normalized forced-token log-probability, top-k token IDs/log-probabilities and
top-k membership. MLX completion explicitly evaluates logits and every cache
state. A header, token rows and a completion footer share weights, prompt,
fixed-sequence and replay-policy SHA-256 identities. The policy captures cache
types, chunk size, backend/runtime versions and diagnostic top-k configuration.

The CLI hashes a sorted safetensors file manifest and retains per-file hashes
and sizes. It records a separate config hash. The API marks its supplied current
weight digest as caller-asserted. Native loading accepts only an existing local
directory, sets offline flags and requests a local-only tokenizer. A fake-loader
test verifies those arguments and raw-prompt encoding without executing MLX.

## Verification

Modules were run individually and sequentially, all on synthetic inputs. Total
test execution across the session was seconds, well below the user's limit.
Final relevant results:

| Command | Result |
| --- | --- |
| `python3.13 -B -m unittest tests.interp_energy.test_forced_decode -v` | 14 passed; 0.332 s |
| `python3 -B -m unittest tests.interp_energy.test_reference -v` | 9 passed; 1.570 s; Python 3.14.6 with NumPy |
| `python3.13 -B -m unittest tests.interp_energy.test_reference -v` | 9 skipped: NumPy absent in Python 3.13 |
| `python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v` | 4 skipped: MLX/MLX-LM absent |
| Python 3.13 `compile(source, path, 'exec')` over the eight added Python files | Passed; no bytecode writes |
| `git diff --cached --check` | Passed before implementation commit |

The stdlib import test launches Python with `-S` and verifies that neither
package import loads NumPy, MLX or mlx-lm. Numerical tests compare cached token
scores to independent full-context causal forwards, verify exact repeated
reference scores, edit weights while preserving input IDs, exercise stable
normalization for extreme logits, and check output-file immutability/refusals.
No existing runtime/adapter code was modified. The canonical full suite was
intentionally omitted under the user's blinded-job instruction.

## Uncertainty and exact next step

**Native support remains PROVISIONAL.** Outside this sandbox, in an authorized
software-only session with a functioning Metal device and mlx-lm installed,
the lead should run:

```sh
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
```

Those four tests check greedy `generate_step` parity, non-greedy forced scores
against full forwards, exact A/A diagnostic repetition, repeatable tied top-k
selection, non-finite refusals and actual KV offsets/fresh caches. They use a
tiny model configuration and download nothing. Native execution and local-model
loading were not validated here. Hybrid Qwen3.5 caches specifically remain an
additional later compatibility check; passing a tiny llama fixture would not
establish that gate.

The replay loop is synchronous and instrumented. Diagnostic kernels, sorting,
host transfers and Python bookkeeping add work between forwards, even though
forward timestamps exclude diagnostics and all JSON/file output occurs later.
Whole-loop energy therefore includes that overhead and does not reproduce
normal mlx-lm asynchronous pipeline timing. The lead must assess overhead and
A/A behavior before using it for a switching-channel bound. Tied top-k boundary
membership is backend-defined; use the same backend/version across arms.

File-manifest identity authenticates on-disk artifacts, not later in-memory
mutations or topology/dtype equivalence. An in-process edit caller must supply
the digest of its current weights under one consistent convention. Experimental
validity, real-model gates, energy claims, pairing/order and measurement windows
remain lead-owned. No unresolved naming or scope question blocks this desk
implementation; native execution and later instrument validation remain open.
