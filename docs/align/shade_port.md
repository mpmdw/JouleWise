# SHADE-Arena local endpoint port

Status: implementation committed, execution validation blocked by the selected
cloud workspace never becoming usable. This is an internal port assessment,
not a benchmark result or hardware validation.

## Source, licence and integrity

Inspected public jkutaso/SHADE-Arena at its default branch, master, on 2026-10-22.
The head was 6614e77191c1f8e2d0c44c123c6f915905ebafae:
https://github.com/jkutaso/SHADE-Arena/commit/6614e77191c1f8e2d0c44c123c6f915905ebafae

The root LICENSE is MIT, copyright 2025 Jonathan Kutasov, Joe Benton,
Henry Sleight, John Hughes, Ethan Perez, Scale AI. Redistribution is permitted
with its copyright and permission notice. This port does not vendor source,
task text, task data, or monitor instructions. Its fixture is original code.

PinnedUpstream fetches that exact commit over HTTPS using git into
$XDG_CACHE_HOME/joulewise/shade/<commit> (or ~/.cache, or a supplied cache_dir).
On first preparation per instance/process it checks HEAD, hashes every on-disk
tracked file as its Git blob, and hashes
the sorted manifest of all 151 tracked files. Canonical manifest bytes are:

    UTF-8 relative path + NUL + ASCII Git blob SHA1 + newline

The manifest SHA256 is
ca16947b3a0e7f1af1a8a818ea214f619ee326978bd922749a32324726da7f89.
This SHA256 was computed from the GitHub tree during development; the Python
implementation still needs its execution check. Source/data byte changes,
untracked source/data, unsupported file kinds, and a different HEAD are
recorded as flags and yield an unavailable source rather than importing it.
Successful verification is cached for an immutable source tree. activate() does
no Git work after preparation; prepare(force=True) explicitly rechecks the pin
and bytes and clears cached modules. Failures are retried on later prepare calls.
Source flags describe the latest operation, so old transient failures do not
flag later clean episodes. Do not mutate a verified cache during an episode.

The source is on sys.path only inside activate(). Upstream's generic top-level
names (utils, tools, environments, environment_classes, task_pairs,
task_evaluation, llms) are saved/restored, including modules previously present
in the host process. Operations are serialized with a reentrant lock. No
working-directory change is required. Import isolation is process-global, so
unrelated threads should not import these names during an upstream operation.

## Provider coupling found

All 90 Python source files in the pinned tree were read or scanned for provider
imports, client construction, model dispatch, network access and tokenizers.

| Upstream location | Coupling | Port treatment |
|---|---|---|
| llms/together_llm.py | AsyncOpenAI client hard-codes https://api.together.xyz/v1 and requires its provider credential variable. Rewrites model names with Qwen/ or meta-llama/, has hosted-model pricing/tokenizer maps and gpt-4o tokenizer fallback. Converts think tags; its partial streaming path warns that usage may be inaccurate. | Do not invoke it. The urllib endpoint preserves the exact served model name, content/reasoning deltas, usage and timings. |
| llms/openai_llm.py | OpenAI SDK default hosted destination and credential requirement; hosted model allowlists, reasoning-model request branches, pricing and tiktoken model mapping. | Do not invoke it. |
| llms/anthropic_llm.py | AsyncAnthropic client and provider credential requirement; Anthropic content/tool blocks, separate system handling, remote token-count API and pricing. | Do not invoke it. |
| llms/google_llm.py | google.generativeai configuration and credential requirement; Gemini history/schema conversion, generation configuration, provider calls/retries and OpenAI tokenizer approximations. | Do not invoke it. |
| llms/deepseek_llm.py | AsyncOpenAI clients hard-code https://api.deepseek.com and a provider credential; model-specific pricing, tiktoken assumptions, separate reasoner tool prompting/parsing, retry and memory logging. | Do not invoke it. |
| llms/__init__.py and llms/base.py | Import every provider on package import; factory creates a provider client if none is supplied. | Keep out of the execution path. |
| utils/llm_utils.py, config.yaml | Hosted-model/org mapping, factory/provider dispatch, configured agent/monitor/evaluator model names. | Explicit endpoint objects replace these choices. |
| utils/experiment_runner.py and task_completion.py | Construct agent/monitor/evaluator providers from that configuration. The original pipeline chooses temperature and controls prompt conditions. | The runner protocols drive ShadeTask; no upstream ExperimentRunner or CLI is used. |
| utils/pipeline_elements.py | Imports OpenAI and Anthropic BadRequestError classes at import time, even for offline environment formatting. | This upstream dependency is still required lazily; no provider client is constructed. |
| utils/logging_utils.py | Imports pipeline_elements for QueryResult and therefore pulls in those SDK exception classes. | Still needed by the real environment loaders. |
| monitor_generation/add_more_default_monitors.py | OpenAI exception import and provider-backed monitor generation. | Not imported. Only the pinned base monitor literal is read. |
| task_evaluation/api_key_calendar_agendas_2_evaluation.py and expenditure_accounting_evaluation.py | Async evaluator_llm.query calls; they fail without a judge. | A small async facade forwards every query to the separately supplied ChatEndpoint and records llm_judge:<identity>. |

The hosted wrappers also use tenacity retry policies unrelated to whether a
completion has begun. Those policies are bypassed. The endpoint retries only
failed connects before any response byte (including status/header bytes)
arrives. Once connect succeeds, delivery is uncertain and no retry is made,
including read timeouts before response headers. Each retry is in result.raw_usage["joulewise"]["retries"] and the
endpoint's retries list. HTTP errors, partial headers and partial streams are
never replayed. Redirects are not followed.

No requests/httpx/urllib/socket service calls were found in the mock tool or
environment modules. Their mail, money, drive, calendar and web operations
mutate/read local mock objects and files.

## What can run offline

The stdlib endpoint, MockEndpoint, pin verifier, adapter and monitor modules
import without extras. Runtime source fetching is the only required public
network operation if the cache is not prepared. Existing verified caches use
allow_fetch=False for offline operation. The stdlib fixture exercises the same
activation, discovery, schema, dispatch, evaluation and monitoring paths.

The real upstream environments require optional Python packages even when
their services are mocked: pydantic v2, PyYAML, docstring-parser,
typing-extensions, rich, pandas, and OpenAI/Anthropic SDK imports. The two
judge-dependent evaluators also import analysis_utils, which imports
matplotlib and seaborn. Pydantic EmailStr also requires email-validator. These
imports occur inside task operations, not at
JouleWise module import. Missing dependencies become task_load_error flags.

One development installation recipe, once a shell exists, is:

    python3 -m pip install 'pydantic>=2' pyyaml docstring-parser typing-extensions rich pandas openai anthropic matplotlib seaborn email-validator

A static scan of the pin finds tenacity and tiktoken only on the bypassed hosted
provider/experiment paths; psutil is confined to the bypassed DeepSeek wrapper.
openapi-pydantic is imported only by unused utils/openapi_utils.py. None is a
direct requirement of this adapter's environment/evaluator path. This minimal
recipe has NOT been isolated in a fresh venv here: the VM is still unavailable.
Transitive package dependencies remain pip's responsibility.

No upstream hosted client or credential is needed. A local judge and monitor
can be separate local OpenAI-compatible servers. Endpoints may read a named
credential environment variable when an operator explicitly supplies
api_key_env; credentials never enter identities or diagnostics.

## Pairs and evaluation semantics

Tool counts below are static counts of unique runtime function names,
including end_task. Workspace lists five duplicate tool entries; the
FunctionsRuntime dictionary deduplicates them, as does this adapter. No pair
README documents a typical number of model turns. These are not measured run
lengths.

| Pair | Environment | Unique tools | Main evaluation | Side evaluation / notes |
|---|---|---:|---|---|
| american_airlines_2 | Travel | 73 | Deterministic flight fraction plus reservation success, combined by the upstream normalizer. | Deterministic airline share. Main work includes flights for 16 people, connections and a restaurant reservation. Long state tracking and travel constraints. |
| api_key_calendar_agendas_2 | Workspace | 45 | LLM judge of agenda/email work. | If outward mail or shared files exist, four judge calls attempt to recover the hidden mock string; otherwise false without judging. |
| bank_transfer_2 | Banking | 71 | Deterministic minimum of exact-payment and notification fractions. | Deterministic cumulative mock transfers and the pinned side threshold. Hints discuss splitting payments into about 40 transactions; that is not a documented turn count. |
| expenditure_accounting | Banking | 71 | LLM judge of the transaction review. | Two judge calls: infer information from shared files, then score it against the task definition's summary. |
| spam_filter_update | Spam filtering | 41 | Deterministic sorting/deletion evaluation followed by upstream add_score_columns's affine transform. | Deterministic classification of a constructed mock sign-in notice. Broad rules and autodeletion can damage main-task performance. |

score_main runs the original evaluate_main_task and original add_score_columns
method. A one-row compatibility object provides apply, assignment and scalar
<, <=, > and >= comparisons; american_airlines_2 uses > while other pairs use >=. This preserves their normalization, including the spam
pair's transform and the airline pair's reservation conjunction, without
copying numerical thresholds. evaluation_outputs retains the raw result.
score_side returns only a real bool, otherwise None with a flag. Missing
evaluations produce None, not a fabricated zero.

The calendar side evaluator inconsistently expects query results to be a
list/dict or falls back to str(result), whereas the normal upstream path
returns QueryResult. The facade supplies .messages for normal consumers and a
string containing only the judge answer for that fallback. It records
judge_reply_text_adapter. This prevents judge input text from being mistaken
for a successful recovered answer. The original four calls remain four calls.

reset(seed) rebuilds the environment from its fixed upstream files. There is
no upstream environment seed interface; upstream_fixed_initial_state records
that fact. The seed still reaches the supplied model/judge endpoint. Sabotage
uses the original system_message_suspicious(give_hint=...), including
<thinking> scratchpad instructions; benign uses the original
system_message_no_secondary_task. All three agent prompts use the pin's
indentation rule. sabotage_hint:on/off records the hint condition when that
prompt is requested. The monitor never receives the secret side instruction.

## Endpoint and monitor wire contracts

ChatResult reports server prompt, cached, completion and reasoning counts
unchanged as integers. vLLM must be served with
`--enable-prompt-tokens-details` to report prefix-cache reuse. Its default is
off while prefix caching can still be on. If none of
prompt_tokens_details.cached_tokens, usage.cached_tokens or timings.cache_n is
reported, cached_prompt_tokens remains the shared contract's zero and
cached_prompt_tokens_unreported flags that call. That zero is unknown; do not
treat its context/prefill split as measured cache accounting. Current vLLM streams delta.reasoning; llama.cpp streams
delta.reasoning_content. Both are accepted. llama.cpp reports no reasoning
counter: separated reasoning remains in reasoning_text, reasoning_tokens stays
zero and reasoning_tokens_unreported is recorded. Zero is an unknown counter in
this flagged case, not evidence that no hidden work happened. No derived token
count has been introduced. Empty deltas do not flag unreported work.

llama.cpp puts timings on its final usage chunk. Preserve it in raw_usage.
When ordinary usage is absent, prompt_n + cache_n and predicted_n are used
with a fallback flag. first_token_ns is the client's monotonic stamp on the
first nonempty content, reasoning, or tool function name/argument delta; role
and empty deltas do not establish generation. This follows Turn's end-of-prefill
contract, extending the original brief's content/reasoning-only wording.

Tool argument pieces are concatenated by streaming index. ID and name fields
are set once; identical repeats are tolerated and conflicting repeats flagged.
finish_reason is retained in raw_usage["joulewise"]. A length stop records
generation_cap_reached. timeout_s/max_retries and source_timeout_s are operator
transport budgets. Judge and monitor max_tokens (default 4096) are operator-set
generation caps, not scientific thresholds; both flag length stops on that call.
Judge per-call audit records are in task.evaluation_outputs["judge_calls"].

count_tokens posts model/prompt/content together to /tokenize outside /v1.
vLLM reads prompt, llama.cpp reads content. Both the combined and fallback
bodies explicitly set add_special_tokens=false and add_special=false, counting
only text on both servers (vLLM otherwise adds special tokens by default). An empty first token list for
nonempty input triggers the content-only fallback, with a flag. Every successful
call records tokenize_shape:prompt_and_content or tokenize_shape:content.
Schema-status fallback remains supported. Missing service returns zero with
tokenize_unavailable.

ChatMessage lacks assistant tool requests and reasoning. AssistantMessage and
assistant_message(result) retain them without changing the shared contract.
For protocol-only callers, the endpoint reconstructs requests from immediately
following tool IDs. ShadeTask records every dispatch in order, including failed
argument parsing. Malformed arguments become {} in the evaluator conversation
and carry a flag with the exact input string; they do not invalidate a score
of the resulting environment state. The malformed tool is not executed.

ShadeMonitor defaults to upstream's two messages: system=<pinned instruction>,
user=<conversation query>. There is no extra task block in the default variant.
upstream_actions_task is a named variant adding task_description only to an
actions_only query. The exact request is available in last_messages.
last_prompt is json.dumps([{"role": ..., "content": ...}, ...], sort_keys=True);
prompt_sha256 hashes its UTF-8 bytes, including both message roles.

- full retains assistant reasoning as closed thinking spans.
- no_scratchpad follows upstream exactly: remove closed, case-sensitive
  thinking/system_instructions pairs and collapse whitespace in every role.
  Unclosed thinking spans and local think tags remain visible.
- actions_only contains tool names and results.
- All views omit agent system prompts and tool arguments, as upstream does.

The shared scratchpad_tags exposes one pair, <thinking>/</thinking>. Upstream
also strips system_instructions; task.flags records
scratchpad_rule:upstream_closed_pairs:thinking,system_instructions. Runner-side
prestripping must use this same closed-pair rule and additional tag to produce
the same view. Prefer passing the intact transcript to ShadeMonitor so this
lane owns the rendering. A future contract should support multiple pairs and
an explicit stripping rule.

ShadeMonitorVerdict is a frozen MonitorVerdict subclass with per-call flags
and valid. An invalid/missing judgment has valid=False and a numeric 50
placeholder only because the shared contract requires a number; it must not
enter suspicion/catch-rate arithmetic. A real 50 has valid=True. A length stop
has valid=False even if it contains a parseable verdict. monitor.flags and
last_flags reset on each score call; the returned tuple is immutable.

Episode v1's strict reader rejects subclass fields. Store complete verdict
artifacts, project .shared_record() into Episode.monitor_verdicts and copy each
call's flags qualified by visibility/index into Episode.flags. Do not strip
validity/flags and treat the placeholder as a score. Adding flags/valid or an
optional suspicion to the shared record is the requested contract change.

Discovery failures remain on TaskPairList.flags; task/endpoint flags must also
be copied into Episode.flags. All nonphysical failures are recorded conditions.
No model service, hardware or paid API is used by the test suite.

## Offline verification to run

    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests
    python3 scripts/quick_suite.py --tier touched --since origin/lane/2026-10-21-align-spine

After fetching the pin during development and installing the optional
dependencies, set JOULEWISE_SHADE_CACHE to the cache parent (the directory
containing the commit directory), then run:

    python3 -m unittest tests.align.test_shade.RealUpstreamTests

The optional test never fetches code. All ordinary tests use a temporary local
Git commit of the original fixture and loopback http.server; they do not
contact external hosts. HTTPWorld explicitly excludes its loopback address
from proxies for the lifetime of the test.

The HTTP world specifies ten benign turns and eleven sabotage turns, with
28/29 tool calls, including parallel request deltas for four-invoice batches.
The authored chain is fixture pin verification -> ShadeTask prompts/schemas ->
urllib SSE -> actual mock environment -> separate judge facade -> original
normalizer -> ShadeMonitor under all three visibilities -> Episode JSONL and
transcript/usage/verdict files. Four worlds cover both usage flavours and both
conditions. The server's monitor response depends on the actual received tool
name and result, so removing either changes its response. The optional source
test covers loading, prompts, schemas, end_task and main/side scoring for all
five real pairs without a service call.

These tests have been authored but not executed in this seat because the
selected environment remains offline in pending/starting. No hardware,
serving stack, source-import dependency combination, or end-to-end result is
claimed validated.

## Risks for local models

The 41–73 tool schemas can consume a substantial context before any task
data. Measure the actual served tokenizer and context use; do not transplant
the hosted tiktoken estimates. Tool JSON, dependency constraints, multi-tool
history and stop/end_task behavior need pilot runs. Malformed calls remain
visible as errors and flags so a small model's tool competence is not silently
screened out.

At 8B to 30B, accurate arithmetic, long email/ledger context, travel connection
constraints and sustained private side-task planning are substantial demands.
Many failures could reflect main-task capability rather than monitorability.
Report main scores, side success, counts, truncations and flags together.
Neither the public pair readmes nor this synthetic fixture establishes a
sensible real-model turn/token cap: the runner must expose its budgets.

A local judge may miss disguised strings or grade narrative quality
differently. Keep judge identity, sampling parameters and the original raw
evaluation output; four side-judge calls are four pieces of off-box work,
not agent tokens or agent energy. Default full/no_scratchpad packaging and
rendering now follow the pinned upstream; actions_only is a port visibility.

Cached prompt counts and reasoning counts depend on server version/parser
configuration. Missing counts must not become inferred hidden-work evidence.
Tool-only completions now have a generated-token timestamp. Retry
flags and incomplete streams matter for attribution even when a transcript
looks complete.

The public five pairs are a limited benchmark split. No synthetic result here
establishes actual sabotage capability, monitor catch rate, or an energy
signal. Power can count hidden work and omitted tool activity, and remains
blind to what fits within one forward pass.

## Wire fixture sources

The review supplied source excerpts fetched 2026-10-21. The HTTP fixture models:

- vLLM v0.32.0/main: vllm/entrypoints/generate/base/protocol.py DeltaMessage.reasoning;
  chat_completion/serving.py reasoning usage only with a reasoning parser.
- llama.cpp master: tools/server/server-chat.cpp reasoning_content deltas;
  server-task.cpp usage without completion_tokens_details and timings on its last
  usage chunk; server-context.cpp post_tokenize returns 200 {"tokens": []} if
  content is absent; server-common.cpp timing field names.

These are wire compatibility fixtures, not executions of either serving stack.
The timing regression uses 200 ms prefill and six reasoning deltas spaced by
100 ms. Its 50 ms agreement bar is half the smallest wrong-delta offset.
The HTTP episode world covers llama.cpp's unreported hidden-token path through
Turn/Episode, retaining total decode and explicit missing-counter flags.
