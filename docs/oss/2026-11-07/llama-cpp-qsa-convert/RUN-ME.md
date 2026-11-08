# RUN-ME: llama.cpp `indexed_attention` converter kit (item B)

Everything here is **UNRUN**: no agent has executed, built, imported or tested any of it. Ed runs it when he chooses to execute upstream code. The whole first stage (repro, failing test, fix, passing test) needs **no C++ build, no weights and no tokenizer**. It needs only a Python venv with llama.cpp's converter requirements.

Pin: `ggml-org/llama.cpp` `f477f795cb071baf5b8af6488378366a72034ac4`. The background is in `FACT-SHEET.md`.

## Kit files

| File | What it is |
|---|---|
| `FACT-SHEET.md` | problem, repro, root cause with `file:line`, fix options, test, risk |
| `make_tiny_qwen4exp.py` | standard-library generator for a config-only Qwen4-Exp checkpoint (`config.json` only) |
| `repro_compress_ratios.py` | imports *your* llama.cpp checkout and prints the `compress_ratios` the converter would write; exit 1 = bug |
| `01-test.patch` | adds `tests/test_conversion_qwen4exp.py` (fails on the pin) |
| `02-fix-option-a.patch` | minimal fix: `!= "linear_attention"` (+2/-1); apply after 01 |
| `02-fix-option-b.patch` | alternative fix: explicit name set plus a raise on unknown names, and one more test (+11/-1); apply after 01, *instead of* (a) |
| `test_conversion_qwen4exp.py` | the same test as plain text, with a kit banner (delete the banner if you copy it by hand) |
| `SHA256SUMS` | checksums of all of the above |

## 0. Before anything (no code runs)

```sh
# keep ~ clean: work under jw-wt; /private/tmp is wiped on reboot, so copy the kit first
mkdir -p ~/code/CapstoneProject/jw-wt/oss-llamacpp-qsa && cd ~/code/CapstoneProject/jw-wt/oss-llamacpp-qsa
cp -R /private/tmp/jwoss-ro/llama-cpp-qsa-convert/kit ./kit
(cd kit && shasum -a 256 -c SHA256SUMS)

# one-open-PR rule for new contributors: confirm you have no open llama.cpp PR
# (mpmdw = the GitHub login in JouleWise's LICENSE and repo URL; change it if you contribute from another account)
gh search prs --repo ggml-org/llama.cpp --author mpmdw --state open
# re-check for duplicates filed since 2026-11-07
gh search issues --repo ggml-org/llama.cpp "indexed_attention"
gh search prs --repo ggml-org/llama.cpp "qwen4exp compress_ratios"
```

## 1. Pinned clone

```sh
git clone https://github.com/ggml-org/llama.cpp llama.cpp
git -C llama.cpp checkout --detach f477f795cb071baf5b8af6488378366a72034ac4
git -C llama.cpp log -1 --format='%H %s'    # expect f477f795... server : downgrade per-request proxy logs to trace (#31859)
```

## 2. Read before running (this is the upstream code that will execute)

- What pip will install:
  - `llama.cpp/requirements/requirements-convert_hf_to_gguf.txt` pulls in torch 2.11.0 (with a pytorch.org extra index) and `-r requirements-convert_legacy_llama.txt`;
  - that file adds transformers 4.57.6, numpy, sentencepiece, protobuf and the PyPI `gguf` package (unused, because the checkout's `gguf-py/` is put first on `sys.path`).
- What the test and the repro import:
  - `conversion/__init__.py`;
  - `conversion/base.py` (imports transformers `AutoConfig`, torch, numpy and `gguf-py`);
  - `conversion/qwen4exp.py`, `conversion/qwen.py`, `conversion/qwen3vl.py`, `conversion/qwenvl.py`;
  - `gguf-py/gguf/__init__.py` and the modules it imports.
- The repro also calls `ModelBase.load_hparams`, as `convert_hf_to_gguf.py` does. That runs `load_all_models()`, which imports every `conversion/*.py` module.
- The kit scripts: `kit/make_tiny_qwen4exp.py` (standard library only) and `kit/repro_compress_ratios.py`.
- The key lines:
  - `conversion/qwen4exp.py:85-91` (the bug);
  - `conversion/qwen.py:411-417` (`recurrent_layers`);
  - `conversion/base.py:1696-1704` (AutoConfig first, then `config.json`).

## 3. Fresh venv (Python 3.11 = CI's version)

```sh
python3.11 -m venv .venv-convert
. .venv-convert/bin/activate
python -m pip install -r llama.cpp/requirements/requirements-convert_hf_to_gguf.txt
python -c "import transformers, torch; print(transformers.__version__, torch.__version__)"   # expect 4.57.6 2.11.0
```

## 4. Repro (config only)

```sh
python3 -I kit/make_tiny_qwen4exp.py q4x/legacy  --layer-type full_attention
python3 -I kit/make_tiny_qwen4exp.py q4x/resaved --layer-type indexed_attention
python kit/repro_compress_ratios.py llama.cpp q4x/legacy;  echo "exit=$?"
python kit/repro_compress_ratios.py llama.cpp q4x/resaved; echo "exit=$?"
```

Expected (predicted, never observed):

- **`legacy`**:
  - ratios column `0 0 0 2 2`, then `OK`, then `exit=0`;
  - converter WARNINGs: "Failed to load model config ... Trying to load config.json instead" (expected with transformers 4.57.6, which does not know `qwen4_exp`) and, from `conversion/base.py:1914`, "Unknown RoPE type: default" (the tiny config copies the official `rope_type: default`; upstream behavior, unrelated to this bug). Both appear for `resaved` too.
- **`resaved`**:
  - ratios `0 0 0 0 2`, then `BUG: trunk attention layers [3] ...`, then `exit=1`;
  - layer 3 shows `recurrent False` and `compress_ratio 0`.

Keep this output: it is the issue's repro evidence. Write the issue yourself.

## 5. Failing test

```sh
cd llama.cpp
git apply --check ../kit/01-test.patch && git apply ../kit/01-test.patch
python -m unittest discover -s tests -p 'test_conversion_qwen4exp.py' -v; echo "exit=$?"
```

Expected on the pin:

- `FAILED (failures=2)`;
- the failing subtests are `layer_type='indexed_attention'` and `layer_type='qwen_sparse_attention'`, each `AssertionError: Lists differ: [0, 0, 2] != [0, 2, 2]`;
- `layer_type='full_attention'` passes;
- `exit=1`.

## 6. Apply ONE fix, then the passing test

```sh
git apply --check ../kit/02-fix-option-a.patch && git apply ../kit/02-fix-option-a.patch   # or 02-fix-option-b.patch
python -m unittest discover -s tests -p 'test_conversion_qwen4exp.py' -v; echo "exit=$?"
python ../kit/repro_compress_ratios.py . ../q4x/resaved; echo "exit=$?"
```

Expected:

- the unit test reports `OK` (1 test with option (a); 2 tests with option (b)) and `exit=0`;
- the repro shows ratios `0 0 0 2 2` and `exit=0`.

The design choice is yours (FACT-SHEET section 4). If you prefer, type the change by hand instead of applying the patch.

## 7. Nearby regression tests and CI-equivalent checks

```sh
python -m unittest discover -s tests -p 'test_conversion_fp8.py' -v      # existing converter tests (Qwen2Moe, Qwen3Next, ...)
python ../kit/repro_compress_ratios.py . ../q4x/legacy; echo "exit=$?"   # official name still gives 0 0 0 2 2
git diff --check
python -m pip install flake8 flake8-no-print ty==0.0.88                  # CI: python-lint.yml, python-type-check.yml
flake8 conversion/qwen4exp.py tests/test_conversion_qwen4exp.py
ty check --exit-zero-on-warning conversion/qwen4exp.py tests/test_conversion_qwen4exp.py
```

`ty` in CI runs on the whole repo with `requirements/requirements-all.txt`. Run on two files without those requirements, it may warn about unresolved imports.

## 8. Optional: the second trigger path (transformers that knows qwen4_exp; FACT-SHEET section 3c)

Use a separate venv, so the pinned one stays clean. Run against the **unfixed** converter (`git stash` first and `git stash pop` after; the untracked test file stays put).

```sh
cd ..
python3.11 -m venv .venv-tf5 && . .venv-tf5/bin/activate
python -m pip install -r llama.cpp/requirements/requirements-convert_hf_to_gguf.txt
python -m pip install -U 'transformers>=5.18'            # overrides the 4.57.6 pin in this venv only; 5.18.0 is the secondhand first release with "indexed_attention" (FACT-SHEET 3b); JouleWise used 5.22.1
python -c "import transformers; print(transformers.__version__)"
git -C llama.cpp stash
python kit/repro_compress_ratios.py llama.cpp q4x/legacy; echo "exit=$?"
```

- **If AutoConfig accepts the tiny config,** expect `knows qwen4_exp: True`, `layer_types rewritten by AutoConfig: True`, and `exit=1` even though `config.json` says `full_attention`. The "converter saw" column shows `indexed_attention` (or `qwen_sparse_attention` with a transformers between 5.1x and 5.18).
- **If AutoConfig rejects the tiny config,** the converter logs the fallback WARNING. Repeat with a real `config.json` (config only, never weights):

```sh
# a) from JouleWise's recorded official config, or b) download just config.json from the HF repo
git -C ~/code/CapstoneProject/jw-wt/handoff show origin/lane/2026-11-06-qwen4exp-quality-ref:docs/run_reports/2026-11-05-flashnext-gold-parity/real-provenance.json \
  | python3 -I -c 'import json,sys; json.dump(json.load(sys.stdin)["checkpoint"]["config"], sys.stdout, indent=2)' > q4x/official-config.json
python3 -I kit/make_tiny_qwen4exp.py q4x/real-legacy  --layer-type full_attention    --from-config q4x/official-config.json
python3 -I kit/make_tiny_qwen4exp.py q4x/real-resaved --layer-type indexed_attention --from-config q4x/official-config.json
python kit/repro_compress_ratios.py llama.cpp q4x/real-legacy;  echo "exit=$?"
```

The real config has `ple_layer_ids`, so the repro prints a note that it stopped at the PLE step. The ratios are still printed: 48 trunk entries plus 1 MTP entry, with 12 QSA layers at 4 when correct and 0 under the bug.

Afterwards:

```sh
git -C llama.cpp stash pop
deactivate
. .venv-convert/bin/activate
```

## 9. Optional: runtime confirmation (needs a real Flash-Next GGUF; not needed for the issue or PR)

- **Metadata.** Run `python llama.cpp/gguf-py/gguf/scripts/gguf_dump.py --json --json-array FILE.gguf` and look at `qwen4exp.attention.compress_ratios`. Alternatively, open a published Flash-Next GGUF in the HF GGUF metadata viewer, which needs no download.
- **Graph.** Build (`cmake -B build && cmake --build build --target llama-debug -j`), then run `build/bin/llama-debug -m FILE.gguf -p hello -n 1 --verbose --tensor-filter 'indexer_k_raw|kq_mask_qsa'`. With correct ratios, the trunk QSA layers should show these nodes; with zeroed ratios, none should appear.
- **Logits (optional, about 0.5 day).** Compare logits of `indexed_attention` against `full_attention` past about 2.1k tokens.

## 10. Upstream sequence (all text written by Ed)

1. File the issue first, using template "Bug (misc.)", module "Python/Bash scripts". Include the step 4 output and the pinned sha.
2. About a day later, open one PR (branch from current `master`; rebase the patch if needed). The PR template line is `AI usage disclosure: YES - ...` in your own words. The commit trailer is `Assisted-by: <assistant name>`, never `Co-authored-by`. Do not use JouleWise's Co-Authored-By or Claude-Session trailers. Code owners who will be requested: @CISC for `/conversion/` and @ggerganov for `/tests/` (`CODEOWNERS:38,92`). In the issue and PR, name both affected layer-type spellings (`indexed_attention` now, `qwen_sparse_attention` for transformers between the model's merge and PR #48974): it is why the test covers three names.
3. Watch for #27836: it edits the same lines. Rebase if it lands first.
