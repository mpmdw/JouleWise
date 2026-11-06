# Flash-Next (`qwen4_exp`) mlx-lm upstreamability audit

Date: 2026-11-06. Scope: the canonical model module, its artifact loader, and
tests in this checkout. This was a source/API audit with synthetic fixtures
only; it did not access any experiment or custody data.

## Verdict

**Closer, but not ready to submit as an mlx-lm model module.** The public model
surface now follows the expected native-module shape and is guarded by a
platform-independent contract test. Numerical behavior was deliberately not
changed. The remaining blocker is architectural: PLE weights are represented
as JouleWise external mmap files and configured with JouleWise runtime fields,
not as a normal mlx-lm checkpoint/model contract.

## Findings and changes

### 1. API conventions — repaired

`ModelArgs` previously required both `model_type` and `text_config`, even
though a native model module owns its model type. It now defaults to
`"qwen4_exp"`, gives `text_config` a safe `default_factory`, and accepts a
missing `model_type` in `from_dict` (`joulewise/align/models/qwen4_exp.py:254-280`).
This changes only the formerly failing/unsupported construction path; an
explicit happy-path value produces the same fields.

`Model` already had the important mlx-lm entry points: `__call__`, `layers`,
`make_cache`, `sanitize`, `quant_predicate`, and `cast_predicate`
(`joulewise/align/models/qwen4_exp.py:2095-2222`). It now also exposes
`head_dim` and `n_kv_heads` as read-only properties forwarding the canonical
text configuration (`joulewise/align/models/qwen4_exp.py:2105-2117`). These
are metadata-only accessors; they do not enter inference.

The module is not yet house-style-small: it contains converter profile policy,
compiled-decode lifecycle, custom serializable hybrid caches, mmap table I/O,
and performance dispatch. Those are justified for JouleWise, but an upstream
patch should split generic functionality into shared mlx-lm facilities or
present each extension separately rather than submit a 2,222-line model as one
review unit.

### 2. `model_file` hook — accurately scoped and tested

The converter writes `model_file="qwen4_exp.py"` and copies that file into the
artifact (`scripts/align_convert_qwen4_exp.py:578-587`). That metadata supports
ordinary remote-model loading, but it is **not** the trusted JouleWise load
path. `load_verified_model` first binds both manifest and module hashes, builds
the module from the verified source bytes, overrides `model_file` to `None`,
and supplies `(module.Model, module.ModelArgs)` via `get_model_classes`
(`scripts/align_convert_qwen4_exp.py:423-467`). Documentation and test wording
now distinguish those two paths instead of claiming every test uses the hook.

This is appropriate artifact hardening, not an upstream API. Once the model is
merged natively into mlx-lm, converted artifacts should select it by
`model_type="qwen4_exp"`; they should not ship executable `model_file` code.
Until then, ordinary loading remains a remote-code path, whereas the verified
loader's hash pins are the supported JouleWise path.

The converter's module pin was rebound to the measured SHA-256
`204c4589…` after the final model edit (`scripts/align_convert_qwen4_exp.py:51-54`).

### 3. Tests — useful parity suite, missing cheap upstream contract

The existing canonical suite is unusually strong numerically (fp32/bf16,
component isolation, cache/padding, quantization, long sparse prefill, and
tamper tests), but it requires MLX/Metal plus transformers. This Linux checkout
does not have `mlx_lm`, so it cannot honestly certify that native suite.

Added `tests/align/test_qwen4_exp_upstream_contract.py`, four stdlib-only tests
covering: the license marker, native `ModelArgs` defaults, the model generation
surface, and the exact distinction between artifact `model_file` metadata and
verified class injection (`tests/align/test_qwen4_exp_upstream_contract.py:1-66`).
These checks are intentionally structural and explicitly do not substitute for
the numerical suite.

Before submission, the native suite should be reorganized into small upstream
unit tests using random tiny configurations, with the JouleWise converter and
manifest-security cases retained here. The upstream patch needs direct tests
for native registry selection by `model_type`; a `model_file` artifact is not a
substitute for that path.

### 4. Licensing and provenance — marker repaired, confirmation still needed

The repository is MIT and requires preservation of its notice
(`LICENSE:1-13`). The model formerly had an informal `Copyright 2026
JouleWise` line that did not identify the copyright holder or license. It now
has `SPDX-License-Identifier: MIT` and the repository's named copyright holder
(`joulewise/align/models/qwen4_exp.py:1-3`). The module also records that it is
a convergence of two independent ports and that community PR #1788 was not
read or executed (`joulewise/align/models/qwen4_exp.py:6-21`).

That is adequate repository hygiene, not legal clearance. Before upstreaming,
the contributor should confirm mlx-lm's required contribution/license process
and preserve an auditable statement distinguishing architecture/reference
comparison from copied implementation. No license conclusion in this report
asserts rights over the upstream checkpoint weights.

### 5. Remaining upstream blockers

1. **PLE storage contract.** `ModelArgs.ngram_tables` points at sidecar files
   and `TextModel` performs host-side ID conversion and mmap gathers
   (`joulewise/align/models/qwen4_exp.py:255-268,1940-1953`). Upstream needs a
   supported checkpoint representation and loading policy, not a
   JouleWise-converter-only layout.
2. **JouleWise runtime knobs.** Sparse crossover thresholds and
   `compile_decode` live in checkpoint configuration
   (`joulewise/align/models/qwen4_exp.py:265-279`). Upstream should decide
   defaults internally or establish generic configuration keys.
3. **Unsupported standard feature.** `input_embeddings` is accepted by the
   signature but raises because PLE requires token IDs
   (`joulewise/align/models/qwen4_exp.py:1955-1959`). The limitation needs an
   upstream API decision and a focused test.
4. **Platform coupling.** The module imports `fcntl`, `mmap`, and `resource`
   (`joulewise/align/models/qwen4_exp.py:50-55`). mlx-lm targets Apple
   platforms, but these dependencies and resource-limit behavior still deserve
   explicit maintainer review rather than being hidden in a model file.
5. **Native-registration proof.** There is no test in this checkout that puts
   `qwen4_exp.py` in mlx-lm's own model registry and loads solely by
   `model_type`. That is the final API proof required before calling the port
   upstream-ready.

## Verification performed

- `python3 -m unittest -v tests.align.test_qwen4_exp_upstream_contract` — 4
  tests, 0 failures.
- `python3 -m unittest -v tests.align.test_qwen4_exp_canonical` — 36 tests
  discovered and all 36 skipped because MLX is unavailable; this is an
  environment check, not parity evidence.
- `python3 -m py_compile joulewise/align/models/qwen4_exp.py
  scripts/align_convert_qwen4_exp.py
  tests/align/test_qwen4_exp_upstream_contract.py` — pass.
- `sha256sum joulewise/align/models/qwen4_exp.py` — final measured digest is
  recorded in the converter pin.
- The Metal numerical suite was not run because `import mlx_lm` raises
  `ModuleNotFoundError` in this checkout. Historical results are not relabeled
  as verification from this run.
- `python3 -m unittest discover -s tests` was started as the repository-wide
  check, then interrupted after more than two minutes in the unrelated slow
  `tests/b5_analysis/test_analysis_work_counts.py` pulse-fitting workload; it
  produced no failure before interruption and is not claimed as a pass.
