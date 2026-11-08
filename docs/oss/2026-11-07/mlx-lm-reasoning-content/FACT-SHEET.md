# FACT SHEET: mlx-lm server, `reasoning` is not mapped back to `reasoning_content` (JouleWise OSS item C)

Prepared 2026-11-07 by an agent (Opus 5.5), read-only. Nothing here was executed: no upstream code was built, installed, imported or tested. Sources were read from git objects of a `--no-checkout` clone and from public GitHub pages. These are facts for Ed to restate in his own words. Nothing in this file is upstream text. mlx-lm forbids AI-written issues, PR descriptions, commit messages and replies (CONTRIBUTING.md, "AI Usage Policy"; AGENTS.md).

Statically reviewed 2026-11-07 by a second agent (Fable 5.1), same read-only rules. Every file:line below was re-read at the pin and found correct; additions from the review are marked "(review)". See §10.

## Pins

| What | Value |
|---|---|
| Upstream repo | https://github.com/ml-explore/mlx-lm |
| Pinned commit (patch base) | `56230fa02b8ff8330daf26dc95c28480423ed5fe` (main, 2026-11-05, "Add fused Metal kernel for DSA sparse prefill (#2027)") |
| Release named in the plan | v0.32.2 = `93e6d4a6447b3080861985947f0820e76fcb957d` (2026-10-16) |
| `process_message_content` at v0.32.2 vs pin | Byte-identical (diffed). `02-fix.patch` applies to v0.32.2 at offset -15. `01-test.patch` applies only to the pin, because the test imports differ at v0.32.2. |
| vLLM precedent read at | `vllm-project/vllm` `d1879210a4b10773d22a2a659152beca0d35d007` (2026-11-08 +0800) |
| Local read-only clone | `/private/tmp/jwoss-ro/mlx-lm-reasoning-content/src` (no checkout) |

## 1. The problem

- `mlx_lm.server` returns the model's thinking under the key `reasoning`, both in `choices[0].message` (non-streaming) and in `choices[0].delta` (streaming).
- When a request arrives, the server does not read `reasoning` on assistant messages. It passes messages to the chat template with their keys unchanged. The only normalisations are: `content` lists to strings, `None` content to `""`, string tool-call arguments to dicts (`process_message_content`), and http image URLs to data URLs (`_inline_image_urls`, `server.py:158-168`).
- Chat templates that show past thinking read `message.reasoning_content`. In mlx-lm itself, `mlx_lm/chat_templates/deepseek_v32.py:171` reads only `reasoning_content`. The plan says the Qwen3.5/3.6/3.8 HF templates do the same. That claim was not re-checked here: reading HF files was outside this kit's allowed sources.
- Result: a client that sends back the assistant message exactly as the server returned it (the usual agent loop) sends `reasoning`, and the template renders that turn without its thinking. The server does not accept its own output key as input.
- Possible second effect (not measured yet): the turn-2 prompt no longer contains the tokens the model generated in turn 1, so the stored prompt-cache entry for turn 1 is not a prefix of turn 2. Qwen3.5's linear layers use `ArraysCache`, which cannot be trimmed, so the server falls back to a shorter cache entry and prefills the rest again (mechanism in §3). Whether a client-side rename fixes this depends on whether the template re-renders the tool call exactly as the model wrote it. Only Ed's live run (`repro_server.py`) can settle this. **No number exists yet.** The "119 bytes per turn" figure in older JouleWise notes came from JouleWise's own `MlxEndpoint` and must not be cited.

## 2. Minimal repro

- **No weights, no network** (`repro_unit.py`). Pass one assistant message, in the shape the server returns, through `mlx_lm.server.process_message_content`. Expected on v0.32.2 and on the pin: no `reasoning_content` key, exit code 1.
- **Tokenizer files only** (`repro_render.py`). Build the turn-2 prompt the way `_tokenize` does, for `mlx-community/Qwen3.5-0.8B-4bit`, in two modes: "echo" (returned message unchanged) and "rename" (`reasoning` renamed to `reasoning_content`). Expected, not verified: the reasoning text is missing from the echo prompt and present in the rename prompt.
- **Live server** (`repro_server.py`, standard library only; Ed downloads the weights). Run one tool-call chain against stock `mlx_lm.server` at temperature 0 and record `usage.prompt_tokens_details.cached_tokens` per request. Do this in echo mode and rename mode, restarting the server in between. Thinking stays on (no `chat_template_kwargs`), so the result does not mix in the separate `enable_thinking=false` drift (QwenLM/Qwen3#1826, cited from the plan).
- Plan gate: if echo falls back and rename extends the cache, Ed writes the issue. If both fall back, the issue rests on the lost thinking alone and makes no cache claim.

## 3. Root cause (file:line at pin `56230fa`)

| Step | Location |
|---|---|
| Output key is `reasoning` | `mlx_lm/server.py:1526-1527` (`choice[key_name]["reasoning"] = reasoning_text`). The same function serves streaming deltas (`server.py:1641-1648`). At v0.32.2: `server.py:1511`. |
| Request messages go through unchanged | `mlx_lm/server.py:1733-1754` `handle_chat_completions` passes `body["messages"]` as is |
| The one normalisation step skips `reasoning` | `mlx_lm/server.py:212-259` `process_message_content`, loop at `:236-258`. It handles `content` and `tool_calls[].function.arguments` only. At v0.32.2: `server.py:197-244`. |
| Template call | `mlx_lm/server.py:655-695` (`_tokenize`: `process_message_content` then `tokenizer.apply_chat_template(messages, ...)`) |
| In-repo template that reads only `reasoning_content` | `mlx_lm/chat_templates/deepseek_v32.py:171` (read), `:265-272` (rendered after the last user turn), `:300` (dropped before it) |
| Cache lookup | `mlx_lm/models/cache.py:1652-1672` `LRUPromptCache.fetch_nearest_cache`. A longer entry is used only if `can_trim_prompt_cache` (`:1661`); otherwise it falls back to the longest stored strict prefix (`:1668-1670`). |
| Hybrid cache cannot be trimmed | `mlx_lm/models/qwen3_5.py:347-348` (`ArraysCache` for linear layers); `ArraysCache` (`cache.py:596`) inherits `_BaseCache.is_trimmable() -> False` (`cache.py:164-165`) |
| Cache stored after generation | `server.py:1003-1008` (batched, key `r.all_tokens[:]`) and `server.py:1154-1157` (single, key `cache_key`, which starts as `prompt[:]` at `:1085` and grows by `cache_key.append(gen.token)` at `:1142`). Key = prompt + generated tokens. (review: `:1085` and `:1142` added) |
| No checkpoints inside a tool chain | `server.py:715-718`: segment checkpoints (system, user) are saved only when the last message is `user`. A turn that ends in `tool` stores only its full entry. |

## 4. Upstream history (verified on GitHub pages, 2026-11-07)

- **PR #711** "Improve reasoning and tool call parsing in server" (awni; merged 2026-01-05) brought in the `reasoning` output key. Review thread, 2026-01-03:
  - kernelpool asked whether clients must still send `reasoning_content`, since "a lot of chat templates still rely on reasoning_content".
  - awni replied: "The input `messages` accept `reasoning_content` in the `assistant` role (which is passed directly to the chat template. We could remap that if needed." He also wrote: "I wouldn't have designed it that way ... but that's what the downstream models and upstream tools expect."
  - So the asymmetry is known and deliberate, and the maintainer has said a remap is possible.
- **Issue #704** "GLM 4.7 Preserved Thinking ?" (closed 2025-12-29). awni's server example (2026-01-18) reads `data["choices"][0]["message"]["reasoning"]` and sends it back as `"reasoning_content"`. The maintainer position is that the client renames the key.
- **Issue #903** "Caching doesn't seem to be working for Qwen3.5" (open, since 2026-02-17). awni: "the prompt cache won't match exactly since the second request drops the reasoning tokens." awni proposed saving the cache just before the reasoning output. At the pin this is the thinking-tail segment (`server.py:745-759`), which applies only when the last message is `user` (`:717`). It covers clients that drop reasoning between user turns, not tool chains where the template re-renders it.
- **PR #1841** (hesamat; closed by its author 2026-09-06, not merged, no maintainer comment): a model-specific normalisation of missing reasoning history, for K2/IFM only.
- **PR #1904** (merged 2026-10-01, `caed194`): a +2/-1 change in the same function (`process_message_content`: parse tool-call arguments only when they are a string) plus one test (that test uses the weight-loading `TestServer` harness). This is a recent precedent for a small change there.
- A search of mlx-lm issues and PRs for `reasoning_content` on 2026-11-07 found no open issue or PR on this mapping. (review, same day: the search returns five hits, #1439, #1050, #711, #704, #161; the only open one is #1050 "Nemotron-Cascade-2: thinking mode infinite loop on Apple Silicon", which is unrelated.)
- (review) The #711, #704 and #903 quotes above were re-read on the GitHub pages on 2026-11-07 and match. In #903, the "tool args can shift" report is from spicyneuron (2026-03-09), with a Claude Code Grep call whose JSON keys were reordered between requests; awni's cache-before-reasoning proposal is dated 2026-02-17.

## 5. Precedent elsewhere

- vLLM `vllm/renderers/chat_utils/chat_message.py:655-660` (at `d1879210a`): for assistant messages, `reasoning` is copied to both `result_msg["reasoning"]` and `result_msg["reasoning_content"]`, with the comment "keep compatibility". Tests are in `tests/renderers/chat_utils/test_assistant.py:22-51`: `test_assistant_reasoning_is_mirrored_to_reasoning_content`, `test_assistant_without_reasoning_sets_neither_field` and `test_non_assistant_reasoning_is_not_mirrored`.
- Two more claims come from the plan and were not re-checked: llama.cpp accepts `reasoning_content` inbound, and froggeric's template PR #88 independently reports the mismatch.

## 6. Proposed fix (`02-fix.patch`, 6 added lines, 1 file)

In `process_message_content`, inside the per-message loop, after the tool-call block:

```python
        # Chat templates read "reasoning_content", but responses use "reasoning".
        reasoning = message.get("reasoning")
        if message.get("role") == "assistant" and isinstance(reasoning, str):
            if message.get("reasoning_content") is None:
                message["reasoning_content"] = reasoning
```

- Only assistant messages change. A user or tool message that carries `reasoning` is left alone (same rule as vLLM).
- Copy only. `reasoning` stays, so a template that reads `reasoning` sees no change.
- A non-null `reasoning_content` from the client is never overwritten. A missing or `null` one counts as absent.
- Only string `reasoning` is copied. vLLM also accepts a `prompt_embeds` dict there; mlx-lm has no such input.
- The output format does not change, and clients that already rename keep working.
- The function runs only when the tokenizer has a chat template (`server.py:653`). The no-template path (`convert_chat`) never used reasoning.
- Design choice for Ed: `message.setdefault("reasoning_content", reasoning)` is one line shorter. It does not fill an explicit `null`, so the last assertion of test 1 (`other`) would then fail.

## 7. The test (`01-test.patch`, in `tests/test_server.py`)

- New class `TestProcessMessageContent`, placed with the other weight-free classes (after `TestToolCallFormatter`, before `TestServer`). It uses no `DummyModelProvider`, no weights and no network.
- `test_reasoning_is_copied_to_reasoning_content`: an assistant message in the shape the server returns (`content: None`, `reasoning`, one tool call), plus one with `reasoning_content: None`. On the pin it **fails** with `AssertionError: None != 'Call f.'`. With the fix it passes.
- `test_other_messages_are_not_changed`: a user message with `reasoning`, an assistant message without reasoning, and an assistant message whose `reasoning_content` is already set. It passes both before and after the fix and guards against overreach.
- One import is added: `process_message_content` from `mlx_lm.server`, placed at the end of the import list (isort order).
- Style was checked by hand only: every added line is 88 characters or fewer (black default), and the files were checked with `ast.parse`. black, isort and ruff were not run. Ed runs pre-commit before pushing (CONTRIBUTING.md); RUN-ME step 5 has the exact commands. (review: `uv`/`uvx` are not installed on the Air, so the `uvx` form from CONTRIBUTING.md does not work there; RUN-ME step 5 now installs `pre-commit` into the venv instead.)
- (review) Both patches were re-applied with `git apply` to plain-text copies of the pinned files in a scratch directory and applied cleanly; the `#` preamble lines are ignored by `git apply`. The diffstat is exactly 29 + 6 = 35 added lines, no deletions, no trailing whitespace. Hand-traced against the pinned function: test 1 reaches `assertEqual(None, "Call f.")` on the pin (a clean `AssertionError`, not an error), and both tests pass with the fix. Import order: `process_message_content` after `_make_sampler` matches isort `--profile=black` with its default `order_by_type` (classes first, then lowercase names; `_` sorts before letters), the same order the existing list already uses. The repo's ruff rules (`F`, `B006`, `B007`, `B904`, `CPY001`, `PLW0127`, `pyproject.toml`) are not touched: no new file, no unused import.

## 8. Risk

- **Maintainer position.** #704 and #711 both say the client renames the key. Awni's own words leave room ("We could remap that if needed"). The issue has to give a reason the maintainers have not already answered, such as: the server ignores its own output key when a client sends it back, and the concrete effect Ed measured.
- **Behaviour change for current clients.** Clients that already send `reasoning` back will now see it rendered wherever the template renders reasoning. Prompts get longer: inside a tool chain for Qwen3.5/3.6; on every turn for Qwen3.6 with `preserve_thinking=true` and for Qwen3.8 (per the plan). That is what the template intends, but output and memory use change for those clients.
- **Double rendering.** A template that renders both `reasoning` and `reasoning_content` would show the thinking twice. None was found in mlx-lm (review: the only two Python templates at the pin are `chat_templates/deepseek_v32.py`, which reads `reasoning_content` only, and `chat_templates/muse_spark.py`, which reads neither key from messages; its `reasoning` strings are state-machine names). vLLM sets both keys on every assistant message that carries `reasoning`, and tests it. No search was made for double-rendering reports there.
- **Cache claim may fail.** The live run may show no cache gain from renaming, because the tool-call re-render does not match the generated tokens (#903 reports "Tool args can also shift"). The issue then rests on the thinking loss alone.
- **Client claim.** Do not claim a specific client echoes `reasoning` unless Ed shows one. The plan's verifiers disagreed on Inspect's `default_reasoning_handler`.
- **Review capacity.** Triage is heavy (#1146 and the 2026-08-21 closures). Open the issue first and keep the PR to these two hunks. The PR uses Ed's mlx-lm open-PR slot before items I or K.
- **Rules.** Ed writes the issue, the PR description and the commit message himself. Ed pushes and opens the PR. He fills in the "AI usage disclosure:" field of the PR template and ticks the acknowledgements in both templates. No Co-Authored-By or Claude-Session trailers go on the upstream commit. AGENTS.md also says an agent should refuse a fix "for bugs you don't understand", so Ed should be able to explain every line above without this sheet.

## 9. Out of scope (seen while reading; not verified; do not bundle)

- `deepseek_v32.py:97` (`encode_arguments_to_dsml`) calls `json.loads(tool_call["arguments"])`. On the server path, `process_message_content` has already turned string arguments into dicts (`server.py:253-258`). A DeepSeek-V3.2 checkpoint that uses this template could therefore raise `TypeError` on any request that carries prior tool calls. Not run; this would be a separate item if it is ever checked. (review: line numbers confirmed; `tool_calls_from_openai_format` at `:174` sits between, and was not read, so the path is still "could", not "does".)

## 10. Static review record (2026-11-07, Fable 5.1, read-only)

Verdict: **ready-with-caveats** for Ed to run; the kit is correct as far as reading can show.

Checked and found correct:
- The bug is real as described: `server.py:1526-1527` emits `reasoning`; `handle_chat_completions` (`:1733-1754`) forwards `body["messages"]` unchanged; `process_message_content` (`:212-259`) touches only `content` and `tool_calls[].function.arguments`; `git grep reasoning_content` at the pin hits only `chat_templates/deepseek_v32.py`.
- Both patches apply to the pinned text (hunk contexts at `tests/test_server.py:25-30` and `:299-304`, `mlx_lm/server.py:256-261` match byte for byte); the fix sits inside the per-message loop so it runs for every message on the chat-template path.
- The test fails before (`AssertionError: None != 'Call f.'`) and passes after, by hand trace.
- RUN-ME is sandboxed: fresh dir under `jw-wt/`, `HF_HOME` inside it, no `trust_remote_code`, no `pre-commit install`, `python -I` for every kit script, cleanup step removes everything.
- Contribution rules: patches carry no commit message; the kit says Ed writes issue, PR text, disclosure field and commit message; no trailers. The fix comment is one line, as AGENTS.md asks.

Corrected by the review (all in RUN-ME.md and this sheet, no patch changed):
- `uvx` is not installed on the Air; step 5 now installs `pre-commit` (or the three pinned tools) into the venv.
- Added the `.pre-commit-config.yaml` row, the `git apply` preamble note, the weight-free-class evidence, the `trust_remote_code` safety note for 6a/6b, the v0.32.2 `cached_tokens` line, and the single-path cache-key lines (`:1085`, `:1142`).
- Added the #1050 search result and the re-verification of the #711/#704/#903 quotes.

Caveats that remain (unchanged from the kit, still true):
- Nothing has been run. The three scripts can still have runtime mismatches (transformers 5.x tokenizer behaviour, HF repo name, template rendering position).
- The cache effect is unmeasured; the HF Qwen3.5 template behaviour is from the plan, not re-read.
- Acceptance risk is moderate to high given #704 and #711.

## Static review

Reviewer verdict (independent read-only static review, 2026-11-07): **ready-with-caveats**. Nothing upstream was executed, built, installed or imported; the kit has not been run (status UNRUN).

Review text as relayed to the lead by the workflow. The relay cut the text off partway through, so it ends mid-sentence; any corrections the reviewer made are already in the kit files above.

```text
VERDICT: ready-with-caveats

Static review of the mlx-lm `reasoning` -> `reasoning_content` kit at upstream pin `56230fa02b8ff8330daf26dc95c28480423ed5fe`. Read-only rules held: upstream read only via `git show`/`git grep` on the existing `--no-checkout` clone at `/private/tmp/jwoss-ro/mlx-lm-reasoning-content/src` plus WebFetch of github.com pages; nothing upstream was installed, imported or executed. The only "execution" was `git apply` and `python3 -I -c ast.parse` on plain-text copies of the two pinned files in the scratchpad (since deleted); no model weights, no pip.

CHECKS (all passed)
- Bug is real: `mlx_lm/server.py:1526-1527` emits `choice[key_name]["reasoning"]`; `handle_chat_completions` (`:1733-1754`) forwards `body["messages"]` unchanged; `process_message_content` (`:212-259`, loop `:236-258`) normalises only `content` and `tool_calls[].function.arguments`; `git grep reasoning_content` at the pin hits only `chat_templates/deepseek_v32.py` (`:171`, `:265-272`, `:300`). `muse_spark.py` (the only other Python template) reads neither key.
- Patches apply: hunk contexts match byte for byte (`tests/test_server.py:25-30`, `:299-304`; `mlx_lm/server.py:256-261`). Both applied cleanly with `git apply`, `#` preamble included. 35 added lines, no deletions, none >88 chars, no trailing whitespace, patched copies `ast.parse` clean. Fix is inside the per-message loop so it covers every assistant message on the chat-template path; copy-only, assistant-only, never overwrites non-null.
- Test: hand-traced on the pinned function, test 1 reaches `assertEqual(None, "Call f.")` on the pin (clean AssertionError), both tests pass with the fix. isort order (`process_message_content` after `_make_sampler`) is correct for `--profile=black` default `order_by_type`. ruff rules (`F`, `B006`, `B007`, `B904`, `CPY001`, `PLW0127`) untouched.
- `process_message_content` is byte-identical at v0.32.2 (`:197-244`); v0.32.2 emits `reasoning` at `:1511` and reports `cached_tokens` at `:1495-1496`, so the 6b measurement works on stock.
- Cache mechanism claims verified: `ArraysCache` (`cache.py:596`) has no `is_trimmable` override -> `_BaseCache` False (`:164-165`); `fetch_nearest_cache` (`:1652-1672`) falls back to `result.shorter`; `qwen3_5.py:347-348`; no segment checkpoints when last message is not `user` (`server.py:717`); single-path cache key `prompt[:]` at `:1085` grows via `cache_key.append(gen.token)` at `:1142`.
- Upstream history re-read on GitHub: #711 (awni, merged 2026-01-05; kernelpool question and awni's "We could remap that if needed" / "I wouldn't have designed it that way" quotes confirmed), #704 (closed 2025-12-29; awni's 2026-01-18 client example renames to `reasoning_content`), #903 (open since 2026-02-17; quote confirmed; "tool args shift" is spicyneuron 2026-03-09). Search for `reasoning_content` returns 5 hits; only open one is #1050 (unrelated Nemotron loop). `caed194` = #1904 (2026-10-01) confirmed in git log.
- Sandbox safety: `mlx_lm.server -
[relayed excerpt ends here]
```
