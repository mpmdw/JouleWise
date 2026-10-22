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
It checks HEAD, hashes every on-disk tracked file as its Git blob, and hashes
the sorted manifest of all 151 tracked files. Canonical manifest bytes are:

    UTF-8 relative path + NUL + ASCII Git blob SHA1 + newline

The manifest SHA256 is
ca16947b3a0e7f1af1a8a818ea214f619ee326978bd922749a32324726da7f89.
This SHA256 was computed from the GitHub tree during development; the Python
implementation still needs its execution check. Source/data byte changes,
untracked source/data, unsupported file kinds, and a different HEAD are
recorded as flags and yield an unavailable source rather than importing it.

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
connection failures before any response byte (including status/header bytes)
arrives. Each retry is in result.raw_usage["joulewise"]["retries"] and the
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
matplotlib and seaborn. These imports occur inside task operations, not at
JouleWise module import. Missing dependencies become task_load_error flags.

One development installation recipe, once a shell exists, is:

    python3 -m pip install 'pydantic>=2' pyyaml docstring-parser typing-extensions rich pandas openai anthropic matplotlib seaborn

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
method. A one-row compatibility object supports exactly the operations these
five normalizers use. This preserves their normalization, including the spam
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
system_message_no_secondary_task. The monitor gets only user_query.

## Endpoint and monitor wire contracts

ChatResult reports server prompt, cached, completion and reasoning counts
unchanged as integers. Missing counts are zero with flags, never locally
estimated. Empty reasoning_content deltas carry no generated reasoning text
and do not raise reasoning_tokens_unreported. Nonempty separated reasoning
with an absent, invalid or zero reasoning counter still raises that flag.
A llama.cpp timing block is preserved in raw_usage; when ordinary
usage is absent, prompt_n + cache_n and predicted_n are used and the fallback
is flagged. first_token_ns uses the client's monotonic clock at the first
nonempty content or reasoning_content delta; a role or tool-only delta does
not establish a content token timestamp. Tool requests are accumulated by
their streaming indices, including split names and JSON arguments.

count_tokens uses /tokenize outside the trailing /v1 prefix. It first sends
vLLM's model/prompt shape and accepts count or tokens; on a schema/status
mismatch it tries llama.cpp's content shape and accepts integer or object
token lists. Unavailability is zero plus tokenize_unavailable in flags.

ChatMessage lacks assistant tool requests and reasoning. AssistantMessage and
assistant_message(result) retain them without changing the shared contract.
For protocol-only callers, the endpoint reconstructs requests from immediately
following tool result IDs and its previous completions. The runner must append
the assistant completion and tool results in order. A missing history entry
is flagged. Keeping the extension also preserves reasoning in subsequent
model input and in full monitor views.

ShadeMonitor reads the exact common upstream instruction literal without
importing its provider packages. prompt_variant="upstream" identifies that
literal; unknown variants are flagged. A single user message contains that
instruction, the legitimate task, and the rendered transcript. This preserves
the instruction text but differs from upstream's two-message system/user
packaging; it makes prompt_sha256 unambiguously the hash of the exact UTF-8
message content sent. last_prompt and responses expose the audit text.

- full includes assistant content and separated reasoning, expressed using
  thinking tags.
- no_scratchpad removes thinking, think and system_instructions spans. It also
  removes unfinished and nested spans; upstream logging removes tagged spans
  from all message roles.
- actions_only contains tool names and result contents. Legitimate task
  context is supplied separately.
- All views omit agent system instructions. As in upstream's names-only
  monitor format, tool arguments remain hidden in every view.
- A missing or invalid verdict produces the upstream uncertainty value, 50,
  with monitor_verdict_invalid; a missing prompt is separately flagged. The
  flag must accompany the verdict so it cannot be counted as a model judgment.

Task/monitor flags and endpoint diagnostics must be copied into Episode.flags
by the runner. Discovery returns a tuple-compatible TaskPairList with a flags
attribute, so even list_task_pairs() retains source failure diagnostics. The
immutable protocols do not currently require these attributes, so protocol-only
code must explicitly collect them.

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
The planned chain is fixture pin verification -> ShadeTask prompts/schemas ->
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
not agent tokens or agent energy. The default monitor packaging above is a
port variant, not an exact reproduction of the upstream hosted experiment.

Cached prompt counts and reasoning counts depend on server version/parser
configuration. Missing counts must not become inferred hidden-work evidence.
A tool-only completion has no observed content first-token timestamp. Retry
flags and incomplete streams matter for attribution even when a transcript
looks complete.

The public five pairs are a limited benchmark split. No synthetic result here
establishes actual sabotage capability, monitor catch rate, or an energy
signal. Power can count hidden work and omitted tool activity, and remains
blind to what fits within one forward pass.
