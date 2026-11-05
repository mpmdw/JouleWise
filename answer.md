# Qwen4 gold streaming handoff

Implemented on `lane/2026-11-05-qwen4exp-gold-stream`, based on
`f48da184b63de7eca7f6158a02ef8e5b6de1c3de` (the checked-out PR #667 head).
Implementation commit: **`78fe672a1`**. A following documentation commit contains
this handoff and the dated run report. Nothing was pushed.

## What was built

- `scripts/run_qwen4_gold_stream.py` and `joulewise/align/qwen4_gold/stream.py`:
  pinned HF metadata/downloads, complete-shard LFS SHA256 checks, disk guards,
  unit-major scheduling, durable lifecycle/chain manifest, exclusive driver
  lock, source/runtime/adapter fingerprints, and restart validation.
- `stream_ple.py`: exact official Transformers 5.22.1 hashing through its own
  `forward`, bounded extraction of raw PLE row bytes into `.npy`, and one sparse
  checkpoint shim for both backends. Missing rows raise.
- `stream_convert.py`: optional per-unit canonical maxfit fragments, using the
  canonical converter helpers and quantization policy; per-tensor progress,
  complete bf16 PLE export with recoverable append spans, and SHA256 manifests.
- Minimal runner/worker additions reuse the harness's existing reference
  `output.npy` traces and real input snapshots. These already contain every
  residual stream. Workers remain serial and offline; all stream-run HF paths
  are under `--work` and Xet is disabled.
- Twenty focused unittest tests and an appended laptop run plan in
  [gold_parity.md](docs/align/qwen4_exp_port/gold_parity.md).

The index excludes **333 vision tensors and 31 MTP tensors** from computation.
All 131 physical files still contain needed text weights, so these exclusions
do not eliminate whole-file downloads.

## Blocking disk-policy ruling

**NEEDS_RULING:** may the laptop run use `--shared-shards restage`?

The requested default, `--shared-shards retain`, keeps originals through their
last user. Official meta tensor shapes and the supplied index prove a lower
bound of **24.110 GiB staged at layer 8**, excluding MTP and headers. Alongside
the 25 GiB free reserve, this cannot fit approximately 40 GB free disk. The
default driver refuses that plan before downloading weight shards.

Options considered:

1. Keep originals: provide substantially more disk and raise the staging cap.
2. **Recommended:** approve the explicit `restage` exception. Authenticate a
   full source, retain only a byte-exact current-unit view, delete the original,
   and download it again for later units. This is implemented and tested; it
   is not silently enabled.

Blocked work is the native laptop run under the literal whole-shard policy.
Restaging should need roughly 9 GiB staging plus about 3 GiB short-prompt
evidence, with enforced guards, but **that real-weight peak has not been
measured**. Expect about 360 GB downloads with retention or about 460 GB with
restaging; pinned HF metadata produces the exact plan.

## Verification

All commands were offline; numerical tests used two threads. Final results:

| Command | Result |
|---|---|
| `/private/tmp/jwsol/venv-ref/bin/python -B -m unittest tests.test_qwen4_gold_stream` | **20 tests OK, 2 native-only skips**, 57.667 s |
| `/private/tmp/jwsol/venv-ref/bin/python -B -m unittest tests.test_qwen4_gold_parity` | **20 tests OK**, 0.693 s |
| `python3.13 -B -m unittest tests.test_qwen4_gold_stream` | **20 tests OK, 17 optional-dependency skips** |
| Targeted `compileall`, CLI `--help`, `git diff --check` | Passed |

Tests cover download/delete order, original shared retention, restaging byte
equality, free-space/staging refusal, partial downloads, kills around subset
commit/deletion, interrupted units/cases and PLE extraction, sparse/full PLE
lookup equality, SHA corruption refusal, complete-table conversion resume,
and multiple PLE parts sharing one source file.

The end-to-end test runs real official tiny reference workers, interrupts and
resumes them, then compares all four layers and endpoints in fp32/bf16 against
an independently loaded full tiny model. Its candidate is an explicit
**trace-copy test double**, so it establishes reference/coordinator behavior,
not MLX parity. Total targeted test time across development was about nine
minutes. The full test suite and Block-5 pipeline were never run.

## Exact native commands

The canonical branch was already available locally at
`65763077aec03235d149517f6c97a7cda987a74c`. No network fetch was attempted under
the standing no-network rule, and the branch was not merged. Its model SHA256
is `f4ec75d16f0af0517b63e202abeef704c9a775e9111949ab003250d51d982c37`;
converter SHA256 is
`18eed9d2843e7f981dc22f8c8de3daa52e766bee23af29af88a81541192e965f`.

First run native tests outside this sandbox:

```bash
GOLD_CANONICAL=/private/tmp/jw-gold-canonical-65763077
mkdir -p "$GOLD_CANONICAL"
git show 65763077aec03235d149517f6c97a7cda987a74c:joulewise/align/models/qwen4_exp.py > "$GOLD_CANONICAL/qwen4_exp.py"
git show 65763077aec03235d149517f6c97a7cda987a74c:scripts/align_convert_qwen4_exp.py > "$GOLD_CANONICAL/canonical_converter.py"

JW_GOLD_CANONICAL_MODULE="$GOLD_CANONICAL/qwen4_exp.py" \
JW_GOLD_CANONICAL_CONVERTER="$GOLD_CANONICAL/canonical_converter.py" \
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 \
/private/tmp/jwsol/venv-both/bin/python -B -m unittest tests.test_qwen4_gold_stream
```

The two previously skipped tests are
`OfficialTinyPLETests.test_native_mlx_sparse_gather` and
`NativeConversionTests.test_maxfit_uses_canonical_quantization_and_resumes_per_tensor`.
The combined native venv needs Transformers 5.22.1, Torch, NumPy, safetensors,
MLX 0.31.2 and mlx-lm 0.31.3.

After approving restaging, set `GOLD_ADAPTER` to the lead's canonical gold/v1
adapter. The canonical model file itself is not a gold adapter. Then:

```bash
GOLD_ADAPTER="${GOLD_ADAPTER:?export the canonical gold/v1 adapter path}"
GOLD_WORK="$PWD/runs/qwen4-gold-stream-20261105"

env -u HF_HUB_OFFLINE -u TRANSFORMERS_OFFLINE \
/private/tmp/jwsol/venv-ref/bin/python -B scripts/run_qwen4_gold_stream.py \
  --work "$GOLD_WORK" \
  --ref-python /private/tmp/jwsol/venv-ref/bin/python \
  --mlx-python /private/tmp/jwsol/venv-mlx/bin/python \
  --mlx-module "$GOLD_ADAPTER" \
  --adapter-dependency "$GOLD_CANONICAL/qwen4_exp.py" \
  --shared-shards restage --min-free-gb 25 --max-staging-gb 12 \
  --max-gb 12 --timeout 3600 --resume
```

Add `--plan-only` first for pinned metadata and exact estimates; remove that
flag to start. Add dependency flags for any other imported adapter sources.
The command uses the fixed built-in 9/8-token prompts; choose an explicit
`--prompts-json` before starting if desired. Repeat the same actual command to
resume. Do not change budgets, source code, adapter, prompts or environments
within a run.

Optional conversion must be chosen at the initial invocation by adding:

```bash
  --convert-out /absolute/lead/chosen/Dropbox-or-external-volume/qwen4-maxfit \
  --canonical-converter "$GOLD_CANONICAL/canonical_converter.py" \
  --canonical-module "$GOLD_CANONICAL/qwen4_exp.py"
```

## Unverified work and risks

- **No native MLX execution or real-weight parity was run.** No GOAL item 5
  PASS is asserted. The lead must supply/verify the actual canonical adapter.
- Live HF API/download behavior was mocked; its installed API signatures were
  inspected. Real transfer throughput, disk peak, worker RSS/Metal allocation
  and numerical results require the native run.
- Whole maxfit output needs roughly 210 GB, including the full approximately
  102 GB PLE table. A Dropbox folder on the same SSD does not supply capacity
  automatically. Guards stop when space is insufficient. There is no cloud
  upload or automatic eviction.
- Conversion writes unit fragments with `complete_model: false`, not an
  assembled canonical model. Dense MLX quantization is native-test pending;
  full-table bf16 copying/resume is tested on CPU fixtures. Full-model
  assembly/loading validation remains a later step.
- Short-prompt parity does not validate long QSA pruning, decode/cache,
  generation quality, or the separate GOAL item 11 Mac validation.

The exact next step is the shared-shard ruling, followed by the combined native
tests, adapter verification and the metadata preflight. The lead reviews and
pushes; no coordination-state files or kernel tasks were changed.
