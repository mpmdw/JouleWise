# Fact sheet: llama.cpp converter drops QSA for `indexed_attention` (qwen4_exp)

Plan item B (`docs/research-audits/2026-11-07/oss-contributions.md` section 4.B, JouleWise branch `origin/research/2026-11-07-oss-contributions`).
Facts only, for Ed to restate in his own words. Nothing here is upstream-ready prose, and nothing has been posted.

**Status: UNRUN.** Everything below comes from reading source (git objects of a `--no-checkout` clone, plus GitHub pages read with WebFetch). No llama.cpp, transformers or kit code has been executed, built, imported or tested. The patches were checked only with `git apply --cached` against a throwaway index of the pinned commit. The kit's own Python files were checked only with `ast.parse`.

## Pins

| What | Value |
|---|---|
| llama.cpp | `ggml-org/llama.cpp` master `f477f795cb071baf5b8af6488378366a72034ac4` (2026-11-08 01:29 +0100, "server : downgrade per-request proxy logs to trace (#31859)") |
| Blob `conversion/qwen4exp.py` at the pin | `8a55d678d74ae4e40559caf8638443c85d827516` |
| transformers (read through WebFetch only) | `configuration_qwen4_exp.py` at `c5bd76e` (main, 2026-11-06). History of that file: PR #48337 "Add Qwen4Exp model" (`fc5c5bd`, 2026-08-26) already rewrote `full_attention` to `qwen_sparse_attention` in `__post_init__`; PR #48974 "Remap indexers layer_type" (`e2d83fd`, 2026-09-22) renamed that to `indexed_attention` and added the legacy remap |

**Static review, 2026-11-07 (second agent, read-only).** Re-read every cited llama.cpp line at the pin; all `file:line` references in this sheet check out. Both patches re-applied cleanly on a throwaway index of `f477f795c` (alone and in each combination; stats match). The constructor and `set_gguf_parameters()` chain was traced again (`Qwen4ExpTextModel -> _Qwen35MRopeMixin -> _LinearAttentionVReorderBase -> Qwen3NextModel -> _QwenMtpMixin -> Qwen2MoeModel -> TextModel -> ModelBase`): every key the chain reads without a default is in the test fixture, and a directory with only `config.json` indexes zero tensors without raising (`base.py:245-321`). Corrections made in this pass are marked "(review)". Still nothing executed.
| Read-only clone | `/private/tmp/jwoss-ro/llama-cpp-qsa-convert/src` (depth 50, never checked out) |

All `file:line` references below are to the llama.cpp pin unless marked otherwise.

## 1. The problem

- When a Qwen3.8-Flash-Next (`qwen4_exp`) checkpoint labels its QSA layers `"indexed_attention"`, `convert_hf_to_gguf.py` writes compress ratio 0 for every trunk QSA layer. Only the appended MTP block keeps its ratio. No error or warning is printed.
- With ratio 0, the runtime runs those layers as plain dense attention. It also prints no warning.
- The official checkpoint uses `"full_attention"` (saved with `transformers_version` 5.8.0.dev0, per JouleWise's recorded config). Hugging Face transformers has never saved that name for this model: from the model's merge (PR #48337, 2026-08-26) it rewrote `full_attention` to `qwen_sparse_attention`, and since PR #48974 (2026-09-22) to `indexed_attention`. So the bug hits any checkpoint saved through transformers' `save_pretrained`: fine-tunes, merges, re-shards and tiny test models, under either name. (review: the old text named only `indexed_attention`.)
- Expected effect on output: the same as the reference while the visible context fits the QSA selection budget, then a silent divergence beyond about 2k tokens. The official config has `indexer_budget=2048` and `indexer_compress_ratio=4`; the plan gives the threshold as budget + ratio = 2052. This comes from reading source only. The plan's wording advice: say "diverges from the reference beyond about 2k tokens, with no warning". Do not call the output "garbage".

## 2. Minimal repro (config only; no weights, no tokenizer, no build)

- `make_tiny_qwen4exp.py OUT --layer-type indexed_attention` writes one `config.json`. It has 4 trunk layers (`linear_attention` x3, then one QSA layer, the official 1-in-4 pattern), 1 MTP block, `indexer_compress_ratio=2` and `indexer_budget=4`.
- `repro_compress_ratios.py LLAMA_CPP_DIR OUT` follows `convert_hf_to_gguf.py` `main()` (lines 245-311) up to `set_gguf_parameters()`. It then prints `layer_types`, `recurrent_layers` and `attention.compress_ratios` for each layer.
- Expected on the pin. Neither output has been observed.

  | Checkpoint | Ratios written (trunk 0-3, then MTP) | Repro exit |
  |---|---|---|
  | `full_attention` (the official name) | `[0, 0, 0, 2, 2]` | 0 |
  | `indexed_attention` (the name recent transformers saves) | `[0, 0, 0, 0, 2]` | 1 |

- The test's own fixture is smaller still: `layer_types=["linear_attention", X]` plus one MTP block. It expects `[0, 2, 2]`; on the pin, `X="indexed_attention"` gives `[0, 0, 2]`.

## 3. Root cause

### 3a. The converter line

`conversion/qwen4exp.py:85-91`, inside `Qwen4ExpTextModel.set_gguf_parameters()`:

```python
ratio = hp["indexer_compress_ratio"]
layer_types = hp["layer_types"]
# the MTP block is a full-attention QSA layer too
self.gguf_writer.add_attention_compress_ratios(
    [ratio if layer_types[i] == "full_attention" else 0 for i in range(n_layer)]   # line 89
    + [ratio] * (self.block_count - n_layer)
)
```

- Line 89 tests for the literal string `"full_attention"`. Any other name for a QSA layer gets 0.
- The same class and its parents decide "attention vs. linear" with the opposite test, `== "linear_attention"`:
  - `conversion/qwen.py:415`: `recurrent = [t == "linear_attention" for t in layer_types]`, which becomes `attention.recurrent_layers`.
  - `conversion/qwen4exp.py:194`: `_merge_shared_input` uses `layer_types[bid] == "linear_attention"`.
- So an `indexed_attention` layer is written as an attention layer (`recurrent_layers` = false) with all of its indexer tensors, but with compress ratio 0. The GGUF loads without complaint.
- Searching the pinned tree for `indexed_attention` finds 0 hits.
- Precedents in the same directory that accept transformers' renamed layer types:
  - `conversion/nemotron.py:435-436`: `_SSM_LAYER_TYPES = {"mamba", "linear_attention"}` and `_ATTN_LAYER_TYPES = {"attention", "full_attention"}`.
  - `conversion/hy_v4.py:82`: `sparse = {"sparse_attention", "deepseek_sparse_attention"}`, with an unknown-value raise at lines 94-96.

### 3b. Why checkpoints carry `indexed_attention` (transformers, read with WebFetch)

- In `src/transformers/models/qwen4_exp/configuration_qwen4_exp.py` at `c5bd76e`, around line 180 (line numbers from WebFetch are approximate), `Qwen4ExpTextConfig.__post_init__` does this:
  - `elif "full_attention" in self.layer_types:` rewrites every `"full_attention"` to `"indexed_attention"`;
  - the in-code comment reads: "The real checkpoint contains "full_attention" entries for layers that are actually using an indexer";
  - with no `layer_types` given, the default pattern uses `"indexed_attention"` directly.
- `validate_architecture` (around line 189) raises on any layer type other than `linear_attention` and `indexed_attention`.
- `src/transformers/configuration_utils.py` (main as of 2026-11-07, around lines 100-106) defines `_LEGACY_LAYER_TYPE_REMAP`:
  - `"mamba": "linear_attention"`;
  - `"attention": "full_attention"`;
  - `"deepseek_sparse_attention": "indexed_attention"`;
  - `"qwen_sparse_attention": "indexed_attention"`, with the comment "QSA with block-compressed indexer keys (Qwen4-Exp)".

  `PreTrainedConfig.__post_init__` applies the remap.
- `save_pretrained` writes the new names. JouleWise saw this happen with transformers 5.22.1: the F1 audit, `docs/align/qwen4_exp_port/audit_mlx_vlm_numerical.md` on `origin/port/qwen4-exp-mlx`, around line 296.
- (review) History, from the file's commit list and the raw file at `fc5c5bd`: the initial "Add Qwen4Exp model" (PR #48337, 2026-08-26) already had the `__post_init__` rewrite, but to `qwen_sparse_attention` (default pattern `"linear_attention" if (i + 1) % interval_pattern else "qwen_sparse_attention"`; `validate_architecture` allowed `{linear_attention, qwen_sparse_attention}`). PR #48974 then renamed `qwen_sparse_attention` to `indexed_attention` everywhere and added the `_LEGACY_LAYER_TYPE_REMAP` entries. The PR page itself describes the change as remapping `deepseek_sparse_attention`, `qwen_sparse_attention` and similar names to one `indexed_attention`. A secondhand note on that page (a vllm-torchtpu commit message) says the rename shipped in transformers 5.18.0; the release that first contained `qwen4_exp` at all was not determined.
- Exposure today, per the plan (not re-checked): all 15 sampled Flash-Next derivatives on HF were saved with transformers 5.8-5.16, so none carries `indexed_attention` yet. (review) The plan's check should be repeated for `qwen_sparse_attention`: any of those 15 saved through a transformers that already contained PR #48337 would carry that name, which the pinned converter also zeroes. Every checkpoint re-saved from now on carries `indexed_attention`.

### 3c. A second trigger path (inference from source; not in the plan; only running settles it)

- `conversion/base.py:1696-1704`: `ModelBase.load_hparams` first tries `AutoConfig.from_pretrained(dir_model, trust_remote_code=False).to_dict()` (line 1699). It falls back to the raw `config.json` only if that raises.
- The pinned converter requirement is `transformers==4.57.6` (`requirements/requirements-convert_legacy_llama.txt:5`, `pyproject.toml:14`).
  - Inference: 4.57.6 has no `qwen4_exp`, so AutoConfig raises, the converter reads the raw `config.json`, and the official checkpoint converts correctly.
- If the converting environment has a transformers that registers `qwen4_exp`, AutoConfig rewrites `"full_attention"` (to `"qwen_sparse_attention"` before PR #48974, to `"indexed_attention"` after) before the converter sees it. In that case even the unmodified official checkpoint would convert with all trunk ratios 0.
- The repro prints the transformers version, whether it knows `qwen4_exp`, and whether the `layer_types` the converter saw differ from `config.json`. RUN-ME step 8 tests this path.

### 3d. Runtime consequences (`src/models/qwen4exp.cpp`, `src/llama-model.cpp`)

- `qwen4exp.cpp:62` reads `attention.compress_ratios` as an optional key.
- `qwen4exp.cpp:64-79` derives a single `indexer_kpool` from the nonzero entries. Zeros are skipped (`if (r == 0) continue;`), and validation (ratio > 1, divides the budget) runs only on nonzero values. A zeroed GGUF therefore loads without error.
- `qwen4exp.cpp:152-159` takes the layer kinds from `attention.recurrent_layers`, so `indexed_attention` layers are still attention layers.
- `qwen4exp.cpp:261-273` creates the indexer tensors (`index_q_proj`, `index_k_proj`, `index_q_norm`, `index_k_norm`) as required for every non-recurrent layer. They are converted and loaded, but unused.
- `llama-model.cpp:3318-3323` allocates the indexer cache for every non-recurrent trunk layer whenever `indexer_head_size > 0`. That memory is allocated but unused.
- `qwen4exp.cpp:478-481` builds the k-pool input only if `indexer_kpool > 0`.
  - With the MTP block exported, `kpool` comes from the MTP entry, so the input is built.
  - With `--no-mtp`, every entry is 0, so `kpool` is 0 and no k-pool input is built.
- `qwen4exp.cpp:1018-1021`: `const bool qsa = inp_kpool != nullptr && hparams.dsv4_compress_ratios[il] > 0;` and `sel = qsa ? build_qsa_sel(...) : nullptr`. Lines 1064-1070 then take the dense `build_attn(...)` path whenever `sel` is null.
- Net: the trunk QSA layers run dense attention silently. The MTP block (draft head) still runs QSA.

## 4. Proposed fix: two options, and the design is Ed's choice

llama.cpp `AGENTS.md:42`: "Agents: before writing code, make sure the contributor owns the design choices and can defend them without you." Both patches are references. Ed may prefer to type the 1-2 lines himself.

| | Option (a): `02-fix-option-a.patch` | Option (b): `02-fix-option-b.patch` |
|---|---|---|
| Change | line 89: `== "full_attention"` becomes `!= "linear_attention"`, plus a one-line comment above the existing MTP comment (review: `AGENTS.md:77-79` wants comments concise; Ed may prefer to fold both into one line) | class constant `_QSA_LAYER_TYPES = {"full_attention", "indexed_attention", "qwen_sparse_attention"}`; line 89 tests membership; `ValueError` on any name outside that set plus `linear_attention` |
| Size | +2 / -1 | +7 / -1 in the converter, +4 in the test (`test_unknown_layer_type`) |
| Consistency | Same predicate as `recurrent_layers` (`qwen.py:415`) and `_merge_shared_input` (`qwen4exp.py:194`). `compress_ratios` becomes the exact complement of `recurrent_layers`, which is what the runtime assumes (`qwen4exp.cpp:261` gives every non-recurrent layer an indexer). | Mirrors transformers' QSA names and the `nemotron.py:435-436` and `hy_v4.py:82,94-96` precedents. Fails loudly on a name it does not know. |
| Unknown future name | Treated as QSA without a message. That matches how `recurrent_layers` already treats it. | The conversion stops with an error naming the value. |
| Plan's lean | | (b) (plan section 4.B) |
| llama.cpp guidance | `AGENTS.md:20`: "a simpler change that does 90% of the job is often preferable to a complex one that does 100%" | `skills/code-review/SKILL.md:85` asks for a hard error rather than "a silent default fallback". That line is about required hparams; applying it to unknown values is an analogy. |

- Both options produce identical GGUF metadata for the official checkpoint, whose layer types are `full_attention` and `linear_attention`.
- Neither option touches C++. GGUFs already converted from re-saved checkpoints stay wrong until they are re-converted.
- Note: transformers' own `validate_architecture` accepts only `linear_attention` and `indexed_attention` for Qwen4-Exp, so a checkpoint that loads in transformers cannot carry any third name.

## 5. The test

- `01-test.patch` adds `tests/test_conversion_qwen4exp.py` (59 lines). A plain copy with a kit banner on top is `test_conversion_qwen4exp.py`.
- It follows the pattern of `tests/test_conversion_fp8.py`:
  - module docstring with the run command (lines 1-8);
  - a temp dir with `config.json`;
  - the model class built with `hparams=...` (lines 48-68).
- What it does:
  1. Builds `Qwen4ExpTextModel` from a 2-layer + 1-MTP synthetic config.
  2. Calls `set_gguf_parameters()`.
  3. Reads `gguf_writer.kv_data[0]["qwen4exp.attention.compress_ratios"]`.
  4. Checks the result in three subtests: `full_attention`, `indexed_attention` and `qwen_sparse_attention`.
- Passing `hparams` directly skips `load_hparams`, so the result does not depend on which transformers is installed. Importing `conversion.base` still needs `transformers` and `torch` installed (`base.py:20,23`).
- Expected on the pin: 2 subtest failures, `indexed_attention` and `qwen_sparse_attention`, each `[0, 0, 2] != [0, 2, 2]`. `full_attention` passes. After option (a) or (b), everything passes. Option (b) adds `test_unknown_layer_type`.
- Placement:
  - `skills/code-review/SKILL.md:215-216` asks for tests in an existing file where possible.
  - The only conversion test file is FP8-specific: docstring line 1 "Test FP8 conversion", class `TestFP8Conversion`.
  - So the kit adds a new file. The alternative is to paste the method into `test_conversion_fp8.py`. Ed's call.
- CI wiring:
  - `tests/CMakeLists.txt` registers no Python tests, and `test_conversion_fp8.py` is not registered either.
  - The Python CI that will see the new file: `python-lint.yml` (flake8 with `flake8-no-print`; the test has no `print`) and `python-type-check.yml` (`ty==0.0.88`, Python 3.11).
- The kit files are ASCII only, with no added line over 125 characters (`.flake8` max-line-length 125).

## 6. Risk

- **Behavior change.** Only checkpoints whose `layer_types` hold names other than `full_attention` and `linear_attention` are affected. Official-checkpoint output is unchanged under both options.
- **Overlapping open PR.** #27836 ("qwen4exp : add NextN/MTP draft head ...", opened 2026-08-27, label "conversion"; (review) still open as a Draft, last commits 2026-08-27), read through its GitHub Files page:
  - it rewrites the same lines (`conversion/qwen4exp.py` around lines 88-90);
  - it keeps `== "full_attention"` and changes the MTP tail to `[0] * (...)`;
  - so it does not fix this bug, and it will conflict textually with either option.
- **Other qwen4exp PRs.** 26 open PRs match `qwen4exp`. #30316 does not touch the converter. Titles suggest #30815 and #28699 are runtime-only, but their diffs were not checked.
- **Duplicates.** An issue/PR search for `indexed_attention` returns only #30306 (Dory support, unrelated). There the string appears in a pasted transformers error message.
- **Contributor rules** (`CONTRIBUTING.md`):
  - line 35: "Bug-fix PRs must include a reproducible issue and a regression test that fails before your change and passes after."
  - lines 38-40, new contributor: "Limit your open PRs to 1" and "Do not submit trivial fixes". The change is 1-7 lines but changes behavior, so the issue should show the effect.
  - lines 21-25: disclose AI use; Ed writes all posts.
  - `.github/pull_request_template.md:14`: `AI usage disclosure: YES / NO`.
  - `AGENTS.md:96`: commit trailer `Assisted-by: <assistant name>`, never `Co-authored-by`.
  - `AGENTS.md:50,99`: AI-written PR descriptions, commit messages and replies are prohibited, as is agent-run push or PR creation.
  - Code owner of `/conversion/`: @CISC (`CODEOWNERS:38`). (review) The new test file falls under `/tests/`, owned by @ggerganov (`CODEOWNERS:92`), so the PR gets two code-owner reviewers. Pasting the test into `tests/test_conversion_fp8.py` instead does not change that.
  - Issue template: "Bug (misc.)" (`019-bug-misc.yml`). Module "Python/Bash scripts"; required fields "Name and Version" and "Problem description & steps to reproduce".
- **Ed's open llama.cpp PRs.** Not checked here (the plan's check was rate-limited). RUN-ME step 0 checks.
- **Prior art elsewhere** (plan, not re-checked): vLLM accepts both names (`vllm/config/model.py:119-125`, `_QSA_LAYER_TYPES`; vLLM #59756 is an issue, closed 2026-10-04). SGLang handles the new name.

## 7. What only running will settle

1. That the test fails on the pin exactly as predicted (2 subtest failures, `[0, 0, 2]`) and passes after each option.
2. That the repro prints `[0, 0, 0, 0, 2]` for the `indexed_attention` config and `[0, 0, 0, 2, 2]` for `full_attention`.
3. The second trigger path (3c): whether a transformers that knows `qwen4_exp` makes even the official `config.json` convert with zeroed ratios. Also whether `AutoConfig` accepts the tiny config at all (otherwise use `--from-config` with a real `config.json`).
4. The runtime claim (3d): that a zeroed GGUF loads and runs dense attention with no warning, and that the unused k-pool input causes no error. This needs a real converted GGUF. `llama-debug --tensor-filter 'indexer_k_raw|kq_mask_qsa'` on the trunk should show those nodes only with correct ratios.
5. Whether any published Flash-Next GGUF on HF already has zeroed trunk ratios. Check `qwen4exp.attention.compress_ratios` in the HF GGUF metadata viewer, or with `gguf_dump.py --json --json-array` on a local file.
6. The `flake8` and `ty` results on the two touched files.
7. (review) The repro's exact log lines. Reading `base.py:1880-1914`: `rope_parameters.rope_type == "default"` (present in both the tiny and the official config) matches no branch and logs `Unknown RoPE type: default` at WARNING, so expect that line next to the AutoConfig fallback warning. It is upstream behavior for every Qwen3.5-family config and not part of this bug.
8. (review) Whether `AutoConfig` under a transformers that knows `qwen4_exp` accepts the tiny config; `Qwen4ExpTextConfig.validate_architecture` may demand more than the keys the tiny config sets.

## Static review

Reviewer verdict (independent read-only static review, 2026-11-07): **ready-with-caveats**. Nothing upstream was executed, built, installed or imported; the kit has not been run (status UNRUN).

Review text as relayed to the lead by the workflow. The relay cut the text off partway through, so it ends mid-sentence; any corrections the reviewer made are already in the kit files above.

```text
VERDICT: ready-with-caveats

Pin re-read: ggml-org/llama.cpp f477f795cb071baf5b8af6488378366a72034ac4 (read-only clone /private/tmp/jwoss-ro/llama-cpp-qsa-convert/src; `git show`/`git grep`/`git apply --cached` on a throwaway index only; transformers via WebFetch of raw.githubusercontent.com). Nothing upstream executed, imported or installed.

WHAT CHECKED OUT
- Bug is real. conversion/qwen4exp.py:89 tests `layer_types[i] == "full_attention"`; qwen.py:415 (`recurrent_layers`) and qwen4exp.py:194 use `== "linear_attention"`. Runtime lines all match the sheet: qwen4exp.cpp:62 (optional key), :64-79 (zeros skipped), :261-273 (indexer tensors for every non-recurrent layer), :478-481, :1018-1021 (`qsa = inp_kpool && ratio > 0`), :1064-1070 dense fallback; llama-model.cpp:3318-3323. transformers main configuration_utils.py has `_LEGACY_LAYER_TYPE_REMAP` with `"qwen_sparse_attention": "indexed_attention"` and configuration_qwen4_exp.py rewrites `full_attention` -> `indexed_attention` in `__post_init__`, `validate_architecture` allows only `{linear_attention, indexed_attention}`.
- Patches apply. Re-applied 01+a, 01+b and a-alone on a fresh index of the pin: qwen4exp.py +2/-1 (a), +7/-1 (b); test 59 / 63 lines. Hunk contexts match lines 35-41 and 84-92 exactly.
- Test fails-before / passes-after. Traced the full MRO (Qwen4ExpTextModel -> _Qwen35MRopeMixin -> _LinearAttentionVReorderBase -> Qwen3NextModel -> _QwenMtpMixin -> Qwen2MoeModel -> TextModel -> ModelBase). Every key read without a default (num_hidden_layers, mtp_num_hidden_layers, linear_*, head_dim, hc_*, indexer_*, layer_types, ple_layer_ids) is in the fixture; config.json-only dir indexes zero tensors without raising (base.py:245-321); `kv_data[0][key].value` is the raw list (gguf_writer.py:282,326). Predicted [0,0,2] vs [0,2,2] for indexed/qwen_sparse on the pin, [0,2,2] after either fix; option (b)'s `assertRaisesRegex(ValueError, "sliding_attention")` matches the raise. Test file 122-char max, ASCII, no print(); flake8/ty paths fine (ty.toml does not exclude tests/).
- Repro script: mirrors convert_hf_to_gguf.py:245-311; `get_model_class` map has both Qwen4Exp arch names (conversion/__init__.py:289-290); real-config PLE path raises the "PLE constant ... missing" ValueError the script catches; RUN-ME step 8's JouleWise path (origin/lane/2026-11-06-qwen4exp-quality-ref real-provenance.json, ["checkpoint"]["config"]) exists and holds the official config (48 layers, full_attention/linear_attention, ratio 4, budget 2048, ple [2], mtp 1, transformers_version 5.8.0.dev0).
- Contribution rules cited correctly (CONTRIBUTING.md:35,38-40; AGENTS.md:20,42,50,96,99; PR template:14; CODEOWNERS:38; SKILL.md:85,215-216). RUN-ME is sandbox-safe: venv-only installs, no weights, git stash/pop is sound, `mpmdw` matches the login in JouleWise's LICENSE/repo URL.

CORRECTIONS APPLIED (files under /private/tmp/jwoss-ro/llama-cpp-qsa-convert/kit/, SHA256SUMS regenerated and verified)
1. FACT-SHEET.md (pins row, s
[relayed excerpt ends here]
```
