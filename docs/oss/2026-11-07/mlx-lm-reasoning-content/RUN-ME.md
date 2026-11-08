# RUN-ME: mlx-lm item C (`reasoning` -> `reasoning_content`)

**Status: UNRUN.** An agent wrote every file in this kit on 2026-11-07 and executed none of them. Only Ed runs them, after reading them. Nothing here posts anywhere.

**Static review (2026-11-07, second agent, Fable 5.1, read-only):** every file:line in FACT-SHEET.md was re-read from the git objects at the pin; both patches were applied with `git apply` to plain-text copies of the two pinned files in a scratch directory (not a checkout, nothing imported) and applied cleanly, including with the `#` preamble lines; the patched copies parse (`ast.parse`) and no added line exceeds 88 characters. The #711, #704 and #903 quotes were re-read on GitHub. Corrections made by the review are marked "(review)" below. Still unrun: every script and test.

Pinned upstream commit: `56230fa02b8ff8330daf26dc95c28480423ed5fe` (ml-explore/mlx-lm main, 2026-11-05).
Plan stock release: v0.32.2 (`93e6d4a6447b3080861985947f0820e76fcb957d`).

## 0. Read before running

| File | Why |
|---|---|
| `FACT-SHEET.md` | The facts, citations and risks |
| `01-test.patch`, `02-fix.patch` | 29 and 6 added lines, no deletions; check them yourself |
| `repro_unit.py` | Imports `mlx_lm.server.process_message_content`. No network. |
| `repro_render.py` | Downloads tokenizer and config files for one HF repo (no weights) |
| `repro_server.py` | Standard library only; talks to a local server over HTTP |
| Upstream `pyproject.toml` at the pin | `pip install -e .` runs the setuptools and setuptools-scm build backend and pulls `mlx>=0.32.3`, `transformers>=5.7.0`, numpy, sentencepiece, pillow, protobuf, pyyaml and jinja2 from PyPI. There is no `setup.py`. |
| Upstream `AGENTS.md`, `CONTRIBUTING.md`, `.github/*template*.md` | The rules for posting |
| Upstream `.pre-commit-config.yaml` at the pin | black 26.10.1, isort 9.0.1 (`--profile=black`), ruff 0.16.8 (`ruff-check`). CI runs these in `check_lint`, then the full test suite on a self-hosted Mac. (review) |

`git clone` runs no repo-provided hooks. Do not run `pre-commit install`.

Each patch starts with `#` comment lines before the `--- a/` header. `git apply` ignores leading text, so they apply as written; `git am` would not accept them, but Ed commits by hand anyway. (review)

Kit checksums (taken when the kit was written):

```sh
cd /private/tmp/jwoss-ro/mlx-lm-reasoning-content/kit && shasum -a 256 -c SHA256SUMS
```

## 1. Fresh dir, pinned clone, fresh venv (on the Air; outside $HOME top level)

```sh
export OSSC=/Users/edr/code/CapstoneProject/jw-wt/oss-c-mlxlm
export KIT=/private/tmp/jwoss-ro/mlx-lm-reasoning-content/kit
mkdir -p "$OSSC" && cd "$OSSC"
export HF_HOME="$OSSC/hf"           # keep downloads out of ~/.cache; delete with the dir

git clone --filter=blob:none https://github.com/ml-explore/mlx-lm mlx-lm
git -C mlx-lm checkout --detach 56230fa02b8ff8330daf26dc95c28480423ed5fe
git -C mlx-lm log -1 --format='%H %s'      # must print 56230fa0... Add fused Metal kernel ...

/opt/homebrew/bin/python3.13 -m venv .venv-main   # needs >=3.11; 3.13 is installed
. .venv-main/bin/activate
pip install -e ./mlx-lm requests          # not ".[test]": lm-eval/datasets are not needed here
python -c "import mlx_lm, mlx.core as mx; print(mlx_lm.__version__, mx.__version__)"
```

## 2. Repro with no weights (unpatched pin)

```sh
cd "$OSSC"
python -I "$KIT/repro_unit.py"; echo "exit=$?"
```
Expected: it prints `BUG: 'reasoning_content' is None ...` and `exit=1`.

## 3. Failing test

```sh
cd "$OSSC/mlx-lm"
git apply --check "$KIT/01-test.patch" && git apply "$KIT/01-test.patch"
python -m unittest -v tests.test_server.TestProcessMessageContent
```
Expected: 2 tests, 1 failure:
- `test_reasoning_is_copied_to_reasoning_content ... FAIL` with `AssertionError: None != 'Call f.'`
- `test_other_messages_are_not_changed ... ok`

Running the class by name skips `TestServer.setUpClass`, so no weights are loaded. Importing `tests.test_server` still imports `mlx.core`, `requests` and `mlx_lm.utils.load` at module level, which is why step 1 installs `requests`; `tests/__init__.py` exists at the pin, so the dotted name resolves. The only module-level data is the `TOOL_CALLS` dict (line 115). (review)

## 4. Apply the fix, test passes

```sh
cd "$OSSC/mlx-lm"
git apply --check "$KIT/02-fix.patch" && git apply "$KIT/02-fix.patch"
python -m unittest -v tests.test_server.TestProcessMessageContent      # expect: OK (2 tests)
cd "$OSSC" && python -I "$KIT/repro_unit.py"; echo "exit=$?"          # expect: FIXED, exit=0
git -C "$OSSC/mlx-lm" diff --stat                                        # expect: 2 files changed, 35 insertions(+)
```

## 5. Nearby regression tests (no weights)

These are the weight-free classes in `tests/test_server.py`. (review: confirmed by reading the pin. `load()` is called only inside `DummyModelProvider`, which only `TestServer*` classes construct; `TestModelSwapClearsCache` mocks `mlx_lm.server.load`; `TestGenerationThreadDeath` uses `FailingModelProvider`; `TestTextStateMachine` builds its tokenizer from a `SimpleNamespace`. `TestServerWithoutKVCacheQuantization` is left out on purpose: it constructs `DummyModelProvider`.)

```sh
cd "$OSSC/mlx-lm"
python -m unittest -v \
  tests.test_server.TestTextStateMachine tests.test_server.TestApplyStopWords \
  tests.test_server.TestHandleCompletion tests.test_server.TestToolCallFormatter \
  tests.test_server.TestProcessMessageContent tests.test_server.TestKeepalive \
  tests.test_server.TestLRUPromptCache tests.test_server.TestMakeSampler \
  tests.test_server.TestModelSwapClearsCache tests.test_server.TestGenerationThreadDeath
```
Expected: all OK.

Optional, at Ed's choice: run the full server suite, which downloads the CI test model `mlx-community/Qwen1.5-0.5B-Chat-4bit` into `$HF_HOME`. Upstream CI runs it on the PR anyway.
```sh
python -m unittest -v tests.test_server
```

Before pushing, check formatting. (review: `uv`, `uvx`, `pipx`, `pre-commit`, `black`, `isort` and `ruff` are not installed on the Air as of 2026-11-07, so CONTRIBUTING.md's `uvx pre-commit run --all` will not work as written. Use the venv instead.) `pre-commit` clones the three hook repos named in `.pre-commit-config.yaml` from GitHub into `~/.cache/pre-commit` and builds an isolated env for each; these are third-party formatters, not mlx-lm code. Set `PRE_COMMIT_HOME` to keep that cache inside `$OSSC` too.
```sh
cd "$OSSC/mlx-lm" && . "$OSSC/.venv-main/bin/activate"
export PRE_COMMIT_HOME="$OSSC/pre-commit-cache"
pip install pre-commit
pre-commit run --files mlx_lm/server.py tests/test_server.py
```
Expected: black, isort and ruff-check all `Passed`. If black or isort rewrites anything, keep their version and re-check `git diff`. Alternative without pre-commit, same pinned tool versions:
```sh
pip install black==26.10.1 isort==9.0.1 ruff==0.16.8
black --check mlx_lm/server.py tests/test_server.py
isort --profile=black --check-only mlx_lm/server.py tests/test_server.py
ruff check mlx_lm/server.py tests/test_server.py
```
(If `uv` is installed later, `uvx pre-commit run --files mlx_lm/server.py tests/test_server.py` does the same.)

## 6. Live evidence for the issue (the plan's first step; downloads weights)

### 6a. Rendered prompt, tokenizer files only (fast)

Run this twice: once on the unpatched pin and once on the patched tree. For the unpatched run, either run it before step 3, or run `git -C "$OSSC/mlx-lm" stash` first and `git -C "$OSSC/mlx-lm" stash pop` afterwards.
```sh
cd "$OSSC"
python -I "$KIT/repro_render.py" --tokenizer mlx-community/Qwen3.5-0.8B-4bit; echo "exit=$?"
```
Expected, not verified:
- Unpatched: `RESULT: BUG` (exit 1). Echo prompt without the reasoning text; rename prompt with it.
- Patched: `RESULT: FIXED` (exit 0). `token ids identical: True`.
- `RESULT: INCONCLUSIVE` (exit 2) means this template renders no reasoning at that position. Stop and re-check the template before writing anything.

Record the HF snapshot revision. It is the `snapshots/<sha>` folder under `$HF_HOME/hub/models--mlx-community--Qwen3.5-0.8B-4bit/`.

### 6b. Stock server, cached_tokens per turn (the plan's measurement on v0.32.2)

Use a second venv with the PyPI release, so the server is stock v0.32.2 and not the pin. (review: v0.32.2 reports `usage.prompt_tokens_details.cached_tokens` at `server.py:1495-1496`, so the `cached` column is populated on the stock release too.)
```sh
cd "$OSSC"
/opt/homebrew/bin/python3.13 -m venv .venv-0322 && . .venv-0322/bin/activate
pip install "mlx-lm==0.32.2"
python -I "$KIT/repro_unit.py"; echo "exit=$?"        # expect BUG, exit=1 (same code path)
```
Safety note (review): `mlx_lm.server` has `--trust-remote-code` as a `store_true` flag (pin `server.py:1953-1956`, default off), and `load_tokenizer` passes no `trust_remote_code` either (`utils.py:613-635`), so the `*.py` files that the HF download pattern fetches are stored but not executed in 6a or 6b. Do not add `--trust-remote-code`. The weights are downloaded by the server on first start; 6a's `repro_render.py` downloads only `*.json`, `*.py`, `*.txt`, `*.jsonl`, `*.jinja`, `tokenizer.model` and tiktoken files (`utils.py:619-628`), never `*.safetensors`. The HF repo name `mlx-community/Qwen3.5-0.8B-4bit` comes from the plan and was not checked against HF (outside the allowed sources); if the download 404s, pick another `mlx-community` Qwen3.5 4-bit repo and record its snapshot sha.

Terminal A (server; first run downloads the 0.8B 4-bit weights into `$HF_HOME`):
```sh
. "$OSSC/.venv-0322/bin/activate"; export HF_HOME="$OSSC/hf"
mlx_lm.server --model mlx-community/Qwen3.5-0.8B-4bit --port 8080
```
Terminal B:
```sh
python -I "$KIT/repro_server.py" --mode echo   --out "$OSSC/echo-0322.jsonl"
#   stop and restart the server in terminal A (empties the prompt cache)
python -I "$KIT/repro_server.py" --mode rename --out "$OSSC/rename-0322.jsonl"
```
Optional third run: the patched pin as the server, in echo mode. If the fix works, it should match the rename run.
```sh
. "$OSSC/.venv-main/bin/activate"; mlx_lm.server --model mlx-community/Qwen3.5-0.8B-4bit --port 8080
python -I "$KIT/repro_server.py" --mode echo --out "$OSSC/echo-patched.jsonl"
```
How to read it: from turn 2 on, compare `cached` with `prev_ctx` (previous prompt + completion).
- Echo flat and rename near `prev_ctx`: the cache claim holds. Use those numbers.
- Both flat: drop the cache claim; the issue rests on the lost thinking (6a).
- `WARNING: turn 1 cached_tokens>0`: the server was not restarted; run again.
- The 0.8B model may make no tool call at all (`NOTE:` line). Raise `--max-tokens` or change the prompt in the script.

## 7. Clean up

```sh
deactivate 2>/dev/null; rm -rf /Users/edr/code/CapstoneProject/jw-wt/oss-c-mlxlm
```
Keep the `*.jsonl` files first if you will cite them.

## 8. Not for the agent; Ed's own steps

Ed writes the issue (template ack line) and, after a maintainer replies, the PR. He writes the description, fills in the "AI usage disclosure:" field and writes the commit message himself. He pushes and opens the PR from his own fork. No Co-Authored-By or Claude-Session trailers go on the upstream commit.
