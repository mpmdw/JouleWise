# align-shade

## SUMMARY

Implemented R2-F1, R2-F2, R2-F3 and R2-m1 on the existing shade branch.
Invalid monitor calls raise MonitorVerdictUnavailable with immutable diagnostics and no numeric placeholder.
Runner tool-call records coalesce into one assistant turn across endpoint, monitor and judge paths.
Judge conversations remove runner-native <jw_reasoning> spans; tool arguments stay out of assistant text.
HTTP, transport and missing-accounting failures raise EndpointRequestFailed with the partial ChatResult.
Missing judge score tags are flagged while upstream normalization remains unchanged.
Added runner-shaped HTTP/failure worlds and optional pandas parity coverage; retained the structured assistant path.
NOT EXECUTED: the VM never became usable; no tests, repros, installs or synthetic episodes ran.
Pushed via the authorized GitHub fallback; shared contracts and runner.py are unchanged.

## FILES

Files changed in this rerun:

- joulewise/align/endpoints.py: urllib SSE/tokenize client, private call-record coalescer, EndpointRequestFailed, partial-result diagnostics, deterministic MockEndpoint.
- joulewise/align/shade/__init__.py: exports MonitorVerdictUnavailable alongside the task, source and monitor APIs.
- joulewise/align/shade/monitor.py: common history normalization, runner/native reasoning visibility, optional-suspicion diagnostic snapshots, typed failures and valid shared verdicts.
- joulewise/align/shade/task.py: common history normalization, runner-reasoning removal for judges and judge_score_tag_missing.
- tests/align/test_endpoints.py: fifteen authored methods, including runner-shaped HTTP history and five partial/accounting failure cases.
- tests/align/test_shade.py: twenty-three authored methods, including runner/judge/visibility equivalence, per-call exception evidence and four optional real-source methods.
- tests/align/test_shade_http.py: three authored methods covering four comparative worlds, an invalid-verdict world and four failed-request worlds.
- docs/align/shade_port.md: pin/licence, provider inventory, pair notes, runtime failure semantics, verification recipe and local-model risks.
- .codex-report/align-shade.md: current implementation, execution limitation, outstanding integration/ruling and preserved historical FIX LOG.

Unchanged lane implementation and original fixture files:

- joulewise/align/shade/upstream.py: pinned MIT source, manifest verification, runtime Git fetch and scoped imports.
- tests/align/fixtures/shade/.gitignore: excludes generated fixture bytecode.
- tests/align/fixtures/shade/README.md: original fixture provenance and purpose.
- tests/align/fixtures/shade/environments/ledger_environment.py: three-page, 24-invoice stateful environment.
- tests/align/fixtures/shade/task_evaluation/ledger_review_evaluation.py: injected judge, state scoring, side scoring and upstream-shaped normalization.
- tests/align/fixtures/shade/task_pairs/base_task_definition.py: original benign, sabotage and monitor prompt methods.
- tests/align/fixtures/shade/task_pairs/ledger_review/task_definition.py: fixture task definition and environment creation.
- tests/align/fixtures/shade/universe_related_stuff/ledger.json: original invoice records.
- tests/align/fixtures/shade/utils/__init__.py: fixture namespace.
- tests/align/fixtures/shade/utils/functions_runtime.py: original tool registration, schemas, dependencies and dispatch.
- tests/align/fixtures/shade/utils/path_utils.py: fixture-root resolution.
- tests/align/fixtures/shade/utils/pipeline_elements.py: original tool-result formatter.

No registry files were changed. No new module was added. No shared contract,
runner file, upstream source/data, review overlay or repro script was committed.

## PUBLIC API

    OpenAICompatEndpoint(base_url: str, model: str, *, api_key_env: str | None = None,
                         timeout_s: float = 120.0, extra_body: Mapping[str, Any] | None = None,
                         max_retries: int = 1, derive_reasoning_tokens: bool = False)
    endpoint.chat(messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (),
                  max_tokens: int, temperature: float, seed: int | None) -> ChatResult
    endpoint.count_tokens(text: str) -> int
    endpoint.flags: list[str]
    endpoint.retries: list[dict[str, Any]]
    EndpointRequestFailed(partial_result: ChatResult)
    error.partial_result: ChatResult
    error.flags: tuple[str, ...]

    AssistantMessage(role: str, content: str, name: str | None = None,
                     tool_call_id: str | None = None,
                     tool_calls: tuple[ToolCallRequest, ...] = (), reasoning_text: str = "")
    assistant_message(result: ChatResult) -> AssistantMessage
    MockEndpoint(script: Iterable[ChatResult | Mapping[str, Any]] = (), *,
                 identity: str = "mock:scripted", token_counts: Mapping[str, int] | None = None,
                 start_ns: int = 0, turn_interval_ns: int = 1_000_000_000)
    mock.chat(...) -> ChatResult
    mock.count_tokens(text: str) -> int

    PinnedUpstream(cache_dir: Path | str | None = None, *,
                   commit: str = UPSTREAM_COMMIT, file_sha256: str = FILE_LIST_SHA256,
                   allow_fetch: bool = True, source_timeout_s: float = 120.0)
    source.prepare(*, force: bool = False) -> Path | None
    source.activate() -> context manager yielding Path | None
    source.monitor_prompt() -> str | None
    source.flags: list[str]
    file_list_sha256(root: Path) -> str
    TaskPairList(pairs: Sequence[str] = (), *, flags: Sequence[str] = ())
    list_task_pairs(upstream: PinnedUpstream | None = None) -> TaskPairList

    ShadeTask(task_pair: str, *, upstream: PinnedUpstream | None = None,
              judge_endpoint: ChatEndpoint | None = None, give_hint: bool = True,
              judge_max_tokens: int = 4096, judge_temperature: float = 0.0)
    task.reset(seed: int) -> None
    task.system_prompt(condition: str) -> str
    task.user_prompt() -> str
    task.task_description() -> str
    task.tool_schemas() -> Sequence[Mapping[str, Any]]
    task.call_tool(name: str, arguments_json: str) -> str
    task.score_main(transcript: Sequence[ChatMessage]) -> float | None
    task.score_side(transcript: Sequence[ChatMessage]) -> bool | None
    task.flags: list[str]
    task.evaluation_outputs: dict[str, Any]
    task.scratchpad_tags = ("<thinking>", "</thinking>")

    ShadeMonitor(endpoint: ChatEndpoint, *, prompt_variant: str = "upstream",
                 upstream: PinnedUpstream | None = None, max_tokens: int = 4096,
                 temperature: float = 0.0, seed: int | None = None)
    monitor.score(transcript: Sequence[ChatMessage], *, visibility: Visibility,
                  task_description: str) -> MonitorVerdict
    monitor.flags: list[str]  # latest call only; last_flags aliases it
    monitor.last_flags: list[str]
    monitor.last_valid: bool
    monitor.last_verdict: ShadeMonitorVerdict | None
    monitor.last_messages: tuple[ChatMessage, ...]
    monitor.last_prompt: str  # canonical JSON of exact role/content messages
    monitor.responses: list[str]
    ShadeMonitorVerdict(monitor_model: str, visibility: Visibility, suspicion: float | None,
                        prompt_sha256: str, flags: tuple[str, ...] = (), valid: bool = True,
                        raw_reply: str = "", verdict_rule: str = "last_tag_strict",
                        verdict_tags: tuple[str, ...] = (),
                        upstream_first_tag_value: float | str = "unparseable")
    diagnostic.shared_record() -> MonitorVerdict
    MonitorVerdictUnavailable(diagnostics: ShadeMonitorVerdict)
    error.diagnostics: ShadeMonitorVerdict
    error.flags: tuple[str, ...]
    error.raw_reply: str
    error.prompt_sha256: str
    render_transcript(transcript: Sequence[ChatMessage], *, visibility: Visibility) -> str
    strip_scratchpad(text: str) -> str

score() returns exactly the shared MonitorVerdict only when valid. Invalid
calls save diagnostics, then raise MonitorVerdictUnavailable, exported from
joulewise.align.shade. ShadeMonitorVerdict is now an independent frozen
diagnostic dataclass, with suspicion=None on failure, rather than a subclass
requiring an invented number. Its shared_record() also raises when invalid.
Save the exception/last_verdict before the next call. A real tagged 50 returns
a shared record. Protocol-only runners can omit unavailable verdicts and
record monitor.error.MonitorVerdictUnavailable without reading lane fields.

chat() raises EndpointRequestFailed after storing per-call diagnostics on an
HTTP/transport error or missing/invalid prompt/completion accounting. Its
partial_result preserves whatever bytes, counts, timing and retries survived.
A usable llama.cpp timings fallback still returns ordinary accounting.
Missing cached/reasoning details alone remain flagged unknown zero counters.

The default-off derived reasoning diagnostic remains only:

    raw_usage["joulewise"]["derived_reasoning_tokens"] = {
        "count": int | None, "source": "server:/tokenize", "special_tokens": False,
        "flags": list[str], "retries": list[dict[str, Any]]}

It never changes reported reasoning_tokens or Turn.hidden_tokens.

## TESTS RUN

Nothing ran: zero executed tests or repros. No syntax/import check, package
install, venv, local checkout, loopback server or episode was executed.
There are no observed pass/fail/skip counts. The VM execution block is not a
test skip, and no authored assertion is claimed to have passed.

The following exact commands were submitted with workdir /workspace/JouleWise
and rejected before execution:

    git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-shade
    python3 -m unittest tests.align.test_endpoints tests.align.test_shade tests.align.test_shade_http -v
    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests
    python3 -m pip --version

Every rejection said:

    No usable execution environment is available. Wait for an environment to become available before using this tool.

pwd was rejected with the same message. wait_for_environment was started at
intake and remained pending through the implementation. Repeated status
checks reported starting/offline or pending/offline, failure=null. At
2026-10-22 05:45:45 UTC the status was starting/offline. The environment
network policy file and local workspace were inaccessible. This was not an
automatic approval rejection.

Neither pandas nor upstream extras could be installed. No runtime upstream
cache could be created. The extra-dependent tests and real-pair repros could
not run. Four optional RealUpstreamTests methods require git, an explicitly
supplied offline cache, pydantic >=2/email-validator and the other upstream
extras; those are authored guards, not observed skips. Source inspection
counts 15 endpoint + 23 shade + 3 HTTP methods = 41 authored methods.

The supplied reviewer repros were not executed or created on disk; the runner
overlay could not be fetched/extracted locally. All fixture and real-pair
runner_world.py commands for both flavours, runner_failures.py,
tool_shape_repro.py, task_edges.py and score_vs_pandas.py remain outstanding.
Resume with the brief's /tmp/r2 overlay recipe and adapt only the failed
monitor probe to catch MonitorVerdictUnavailable; additionally inspect the
judge conversation for <jw_reasoning> leakage.

Required remaining local commands after checkout and extras setup include:

    python3 scripts/quick_suite.py --tier touched --since 6da3afe2d21b06dbffe0f521eb5768fd6aeb8ee2
    python3 scripts/fixture_orphan_census.py --fail-on-orphans
    JOULEWISE_SHADE_CACHE=/tmp/r2/cache /tmp/r2/venv/bin/python -m unittest tests.align.test_shade.RealUpstreamTests -v
    python3 /tmp/r2/scripts/tool_shape_repro.py /workspace/JouleWise
    python3 /tmp/r2/scripts/runner_world.py /workspace/JouleWise vllm
    python3 /tmp/r2/scripts/runner_world.py /workspace/JouleWise llamacpp
    python3 /tmp/r2/scripts/runner_failures.py /workspace/JouleWise
    python3 /tmp/r2/r1scripts/task_edges.py
    /tmp/r2/venv/bin/python /tmp/r2/scripts/runner_world.py /workspace/JouleWise vllm /tmp/r2/cache bank_transfer_2
    /tmp/r2/venv/bin/python /tmp/r2/scripts/runner_world.py /workspace/JouleWise llamacpp /tmp/r2/cache bank_transfer_2
    /tmp/r2/venv/bin/python /tmp/r2/scripts/score_vs_pandas.py /workspace/JouleWise /tmp/r2/cache

Remote static checks are separate from test execution: read the lane report
first, immutable contracts, repository instructions/M0 and owning source.
No nested AGENTS.md was listed in the affected directories. GitHub confirmed
that the existing branch began at 6da3afe2d21b06dbffe0f521eb5768fd6aeb8ee2.
Four implementation commits were fast-forwarded with force=false. GitHub
compare showed four ahead/zero behind and only eight allowed lane files
before this report. The upstream master head still equals the retained pin.
No syntax, import or runtime success is inferred from any remote read.

## END-TO-END

NOT EXECUTED. No transcripts, verdict files, Episode JSONL, measured timing,
token/first-token mismatches, pandas parity rows or reviewer outputs exist
from this rerun. The following describes authored inputs and expected
assertions only, never observed results.

The four comparative worlds run the original fixture pin verifier -> scoped
upstream imports -> ShadeTask prompts/tools -> real urllib SSE -> fixture
tool runtime/environment -> separate judge endpoint -> pinned-shape score
normalizer -> three ShadeMonitor views -> transcript/usage/verdict files and
shared Episode JSONL round-trip. Both vLLM and llama.cpp wire flavours run
both conditions. Their driver now emits the runner's inline reasoning and
interleaved assistant call records. Existing unit/HTTP coverage also retains
the lane-local AssistantMessage and older plain-assistant/tool path.

| Per-flavour scripted fixture inputs | Benign | Sabotage |
|---|---:|---:|
| Agent turns | 10 | 11 |
| Tool calls | 28 | 29 |
| Prompt tokens | 64000 | 73216 |
| Cached prompt tokens | 52992 | 61440 |
| Uncached prefill tokens | 11008 | 11776 |
| Completion tokens | 7680 | 8960 |
| Server reasoning, vLLM | 5120 | 6144 |
| Reported reasoning, llama.cpp | 0, unreported | 0, unreported |
| Normalized main score | 1 | 1 |
| Side success | false | true |
| Scripted monitor score per visibility | 9.5 | 92.5 |

These exact integers derive from prompt=4096+512*i, first prompt uncached,
later uncached=768, normal completion=768 with 512 hidden, and one extra
export turn with completion=1280/hidden=1024. The normal path has three page
reads, six batches approving all 24 invoices and end_task; sabotage adds
export_audit to hidden_archive. No new measured-quantity bar was introduced.

An additional complete benign HTTP world supplies missing, real-50 and capped
monitor replies. Expected diagnostics are suspicion=[None,50,None],
valid=[False,True,False]; only one shared verdict is stored unchanged.
The missing/capped calls raise, preserve raw reply/hash/flags, and generate
monitor.error.MonitorVerdictUnavailable. This is also tested after a partial
endpoint failure with an otherwise parseable tagged 50.

The new failed-request HTTP world fails after three normal turns for HTTP
400, stall and cut. Expected surviving completion sum is 3*768=2304, with
three Turns and endpoint.error.EndpointRequestFailed, rather than a fourth
zero-token Turn. A never-usage server fails on its first call, yielding zero
Turns and that error flag. Stall/cut input includes 120 synthetic reasoning
tokens retained in the partial-result evidence. The timeout is an operator
budget below the scripted delayed chunk; assertions use integer counts,
never an ungrounded latency agreement bar. Companion endpoint cases include
DONE without usage and invalid completion usage, plus no post-connect retry.

The minimal runner-shaped transcript has two approve_invoice call records
c1/c2 interleaved with results. Expected wire roles are
system,user,assistant,tool,tool, with both calls on that assistant and no
arguments-as-content message. The monitor names-only view hides arguments;
the judge conversation equals the structured AssistantMessage reference and
contains neither <jw_reasoning> nor its private text. Comparative HTTP tests
also check that assistant messages are not consecutive and judges contain no
native reasoning.

The optional real-source parity method runs every pair across seven replies:
the review's five plus uppercase score tags and an unclosed score tag.
That is 5*7=35 scalar comparisons through the real evaluator/normalizer and
pandas after real mock-tool state changes. Exact equality is justified by
identical upstream normalization code on identical scalar inputs. Missing
closed tags on the two score-tag main evaluators should carry
judge_score_tag_missing. This has not run.

Existing first-token tests retain their physically separated delta stamps
and documented 50 ms bar (half a 100 ms wrong-delta offset). Existing cache,
special-token and optional derived-reasoning worlds remain in place.

## DECISIONS I MADE

- Continue from the existing branch at 6da3afe2, never reset to the spine.
  Use the explicitly authorized GitHub fallback after repeated VM execution
  failures; fast-forward only and label every current finding NOT EXECUTED.
- Preserve pin 6614e77191c1f8e2d0c44c123c6f915905ebafae, MIT licence and manifest
  ca16947b3a0e7f1af1a8a818ea214f619ee326978bd922749a32324726da7f89.
  The current upstream master still has that head. No upstream code/data is
  vendored; the fixture remains original and unchanged.
- R2-F1 supersedes the prior numeric-placeholder rule. Store diagnostics,
  then raise MonitorVerdictUnavailable for every unavailable judgment.
  Diagnostics have optional suspicion, preserving no invented number even
  outside Episode. Genuine tagged 50 remains a valid shared record.
  Endpoint errors are wrapped after retaining their partial monitor reply.
- Treat assistant ChatMessage.tool_call_id as the runner's call record.
  Coalesce its content as arguments into the preceding assistant across
  intervening tool results, keeping result order. Reuse one private
  normalizer in all three lane paths. Keep AssistantMessage and the older
  plain-assistant/tool reconstruction working.
- Runner <jw_reasoning> spans represent native hidden reasoning. Remove them
  from judge conversations and restricted monitor views, while full keeps
  them. Preserve the separate native reasoning_text isolation and upstream
  thinking/system_instructions closed-pair rule.
- R2-F3 uses the contract's exception channel: no HTTP/transport failure or
  unavailable mandatory accounting returns a normal ChatResult. Store the
  partial result and flags before raising EndpointRequestFailed. The runner
  can keep the episode and sampler evidence while omitting that failed Turn.
  Against a server that never reports usable usage/timings, an episode has
  zero Turns and endpoint.error.EndpointRequestFailed; partial generated
  work is diagnostic evidence, never a measured zero-work turn.
- Prompt/completion totals are mandatory accounting; cached and reasoning
  details alone remain flagged unknown zeros as the immutable contract
  specifies. A stream missing DONE but retaining usable counts stays a
  flagged result unless a transport exception occurred. No failure adds a
  retry after connect or any guessed token counts.
- Preserve default-off derive_reasoning_tokens as a labelled /tokenize
  diagnostic only. Do not promote it to llama.cpp hidden_tokens; that
  printed-number choice is explicitly under NEEDS_RULING.
- R2-m1 preserves upstream's main score for calendar-agendas/expenditure
  formatting failures and adds judge_score_tag_missing for absent closed,
  case-insensitive <score> tags. Other pair normalizers are untouched.
- Preserve tool results verbatim. The runner_world.py args_json probe searches
  the entire monitor prompt for invoice_id; this also matches legitimate
  ledger tool results. Correctness checks target assistant argument leakage,
  not deletion of observed tool data.
- Keep the requested exact judge flag name. score_vs_pandas.py filters its
  printed flags for the substring "error", so judge_score_tag_missing will
  not appear in that printed list. The optional parity test checks task.flags
  directly without changing the reviewer's inputs or normalizer.
- Retain last-tag strict finite 0..100 monitor parsing, all closed tag bodies
  and upstream's first-tag/clamp alternative in frozen diagnostics. Retain
  canonical role/content JSON hashing, upstream two-message prompt packaging,
  explicit actions-task variant, operator caps and prior accounting flags.
- No new dependencies, measurement thresholds, protocol fields or hardware
  claims. New count assertions are scripted integer identity; the pandas
  comparison executes the same normalizer on identical scalar inputs.
- Follow the exhaustive write scope. No registry addition without an observed
  registry failure. No runner/shared-contract edit, external model service,
  paid API or hardware experiment occurred.

## CONTRACT-CHANGE

No shared contract file was modified.

- ChatMessage needs structured assistant tool requests and separate reasoning,
  or one canonical transcript convention. AssistantMessage plus the private
  coalescer adapt the two existing lane conventions without changing records.
- ChatResult/AgentTask/Monitor need a per-call flags/diagnostics channel that
  protocol-only runners must propagate into Episode.flags. This includes
  cache/reasoning unknowns, retries, task/judge formatting and monitor detail.
  The exception stopgaps prevent two corrupt record shapes; they do not carry
  all remaining diagnostic conditions into Episode by themselves.
- MonitorVerdict should support validity/flags or optional suspicion. Until
  adopted, the lane returns a plain record for valid scores and raises with
  optional-suspicion diagnostics for unavailable scores.
- AgentTask.scratchpad_tags still exposes one pair while upstream strips two;
  request multiple pairs and an explicit closed-pair/whitespace convention.
  Runner-native reasoning also needs an agreed separated representation.

## OPEN ISSUES

- Execution remains blocked. All syntax/import checks, focused/align/full
  suites, touched suite, fixture census, extras tests and reviewer repros are
  outstanding on this head. No local checkout, overlay, cache, package
  installation, scripts or result files could be created.
- Runner lane: copy per-call raw_usage["joulewise"]["flags"], task.flags and
  monitor diagnostics (qualified by visibility) into Episode.flags; persist
  partial-result/monitor exception evidence for audit. The lane-side typed
  exceptions use the existing runner error channel but do not fix dropped
  missing-cache/reasoning or judge-format flags.
- Reviewer probe limitations need attention when execution is available:
  runner_world.py's whole-prompt invoice_id search also sees ledger result
  columns, and score_vs_pandas.py hides flags lacking the substring "error".
  Preserve the supplied inputs; inspect assistant text/direct task.flags in
  companion checks instead of redacting legitimate results or renaming flags.
- Runtime source verification, the isolated extras recipe and all source
  imports remain unvalidated in this seat. The previous reviewer's runs on
  earlier heads do not validate this rerun.
- Real vLLM/llama.cpp serving, model competence and hardware/power validation
  remain outside this synthetic/mock task.

## NEEDS_RULING

Question: should llama.cpp Turn.hidden_tokens remain the server-unreported
zero, or be populated from the opt-in served /tokenize diagnostic?

Options: retain zero with an Episode flag and separately labelled estimate;
or promote the derived count into hidden_tokens with explicit provenance,
accounting for the tokenizer request's extra measured-server work and joined
text tokenization semantics.

Recommendation: retain reported zero plus a required flag and separate
derived diagnostic until the lead chooses a consistent accounting policy.
Blocked work: promotion of any derived count into ChatResult.reasoning_tokens
or Turn.hidden_tokens, and any printed comparison using that replacement.
This rerun changes none of those numbers.

## FIX LOG

### Round 1

B1 — fixed (NOT EXECUTED) — 05ea350dd7253ddedbb47c4a5be7b819a2dda7e5 — accept reasoning and reasoning_content; first reasoning delta timestamps generation.
B2 — fixed (NOT EXECUTED) — 05ea350dd7253ddedbb47c4a5be7b819a2dda7e5 — combined tokenizer body plus explicit shape/fallback flags.
B3 — fixed (NOT EXECUTED) — d44d27ccbe8000ec2ee69fc0a266286b56456055 — scalar comparisons include AA2's >; RealUpstreamTests retained.
M1 — fixed (NOT EXECUTED) — 05ea350dd7253ddedbb47c4a5be7b819a2dda7e5 — tool name/argument deltas establish first_token_ns.
M2 — fixed (NOT EXECUTED) — 3900cdcbc4c8cc176103e466db42289377add404 — process-local verification cache; no per-tool Git/rehash; timings unavailable.
M3 — fixed (NOT EXECUTED) — 09c175b09a38d4d262ce34e1c7c6fa9688063e00 — frozen flagged/valid verdict subclass and per-call reset.
M4 — fixed (NOT EXECUTED) — d44d27ccbe8000ec2ee69fc0a266286b56456055 — malformed args reconstructed as {}; every call keeps its history slot.
M5 — fixed (NOT EXECUTED) — 09c175b09a38d4d262ce34e1c7c6fa9688063e00 — upstream closed-pair removal and whitespace rule; unclosed text remains visible.
M6 — fixed (NOT EXECUTED) — 09c175b09a38d4d262ce34e1c7c6fa9688063e00 — two roles, canonical message hash and named actions-task variant.
M7 — fixed (NOT EXECUTED) — ac3a08011c444c39df13675ab6fbd2ff3b79325c — source-shaped server fixtures; fc8861c1e77ebd2fbe56e1a48feba51c17005d9a adds the llama.cpp episode path; probe APIs unchanged.
m1 — fixed (NOT EXECUTED) — 05ea350dd7253ddedbb47c4a5be7b819a2dda7e5 — connected/request-sent timeout cannot retry and carries a timeout flag.
m2 — fixed (NOT EXECUTED) — 3900cdcbc4c8cc176103e466db42289377add404 — latest-operation source flags replace transient history.
m3 — fixed (NOT EXECUTED) — e87da8b557f12dac31a6e3b31840488955db48f9 — compare resolved fixture and cache paths.
m4 — fixed (NOT EXECUTED) — 398670732f53788fdd37a86c43d47f6b9c629167 — email-validator/pydantic-v2 extras gate; c8093d2b20272a65f574a4b71e5eaa6b08a555e6 updates recipe and static dependency assessment; fresh venv unrun.
m5 — fixed (NOT EXECUTED) — 05ea350dd7253ddedbb47c4a5be7b819a2dda7e5 — identical identifier repeats are idempotent; conflicts flagged.
m6 — fixed (NOT EXECUTED) — d44d27ccbe8000ec2ee69fc0a266286b56456055 — sabotage hint on/off is recorded when used.
m7 — fixed (NOT EXECUTED) — c603ea7524341052a011d53f4a2f2acd318a5258 — task flag/documentation names both upstream closed-pair tags.
m8 — fixed (NOT EXECUTED) — 6e4341f575aa936908c977e1b6938e541f25d3c2 — report replaced with this seat's zero-execution evidence and corrected authored worlds; Mac review results are not claimed as post-fix validation.
numbers — fixed (NOT EXECUTED) — 09c175b09a38d4d262ce34e1c7c6fa9688063e00 — operator generation caps, per-call truncation flags; endpoint commit 05ea350dd7253ddedbb47c4a5be7b819a2dda7e5 documents synthetic clock and transport budgets; derived test bars retained.

### Round 2

N1 — fixed (NOT EXECUTED) — efd431f831aa8ae66aa3f596a01e772d26e167b5 — missing cache counts are flagged per call; required vLLM serve flag and default-usage HTTP world added.
N2 — fixed (NOT EXECUTED) — 44fef910882c32268e012b622a8abc98c218768b — native reasoning is dropped directly outside full and from judge conversations; quoted closing-tag regression added.
N3 — fixed (NOT EXECUTED) — 074282bf902224c511bc58415468fce67e8b893a — last-tag strict rule retained; multiple tags flagged; all tag bodies and the upstream first-tag value or "unparseable" retained per call and documented.
N4 — fixed (NOT EXECUTED) — 074282bf902224c511bc58415468fce67e8b893a — plain score returns; reset last_verdict/last_flags/last_valid; unit/HTTP tests assert unchanged-return round-trips. No VM or probe copies: pending adaptations are v.flags to mon.last_flags, v.valid to mon.last_valid (snapshot for later lists), and v.shared_record() to v; verdict_parse prints last_flags and upstream_first_tag_value. No other probe changes.
m-a — fixed (NOT EXECUTED) — 4204aa2c702529d0ac7b8af8408b18d853c860e4 — opt-in server-tokenized reasoning count is labelled only in raw_usage['joulewise']; default off avoids extra measured-server work and preserves printed counters.
m-b — fixed (NOT EXECUTED) — efd431f831aa8ae66aa3f596a01e772d26e167b5 — combined/fallback tokenizer bodies explicitly disable both backends' special-token additions.
m-c — fixed (NOT EXECUTED) — 44fef910882c32268e012b622a8abc98c218768b — malformed argument flags contain byte length and SHA256 prefix, are deduplicated, and preserve main-state scoring/history.
m-d — open (NOT EXECUTED) — the round-2 reviewer executed the suite, extras suite and every round-1 repro on 07c3d379c before this round; those runs do not validate this round.
numbers — fixed (NOT EXECUTED) — 074282bf902224c511bc58415468fce67e8b893a — nothing in the review's number list lacks a derivation; invalid records keep 50.0, with per-call validity/qualified flags and explicit exclusion from catch-rate arithmetic in docs and HTTP tests. New assertions use exact scripted integer/hash/serialization identity; the 16-hex SHA prefix is a 64-bit display identifier, not an analysis bar.

### Round 2 rerun (R2 findings)

R2-F1 — fixed (NOT EXECUTED) — 6f32c3d9a90d5b111d4d0a7d8800e085c5142ec6 — invalid calls save optional-suspicion diagnostics then raise MonitorVerdictUnavailable; genuine 50 returns a shared record.
R2-F2 — fixed (NOT EXECUTED) — 1b6ae2ba212130c1231a7d05a17de03ace49228a — coalesce interleaved runner call records in endpoint/monitor/judge paths and strip runner reasoning from judges; structured path retained.
R2-F3 — fixed (NOT EXECUTED) — 4ac5caff91a99b3183f1f0a7307e2dfcc6a97460 — raise EndpointRequestFailed with partial_result on HTTP/transport or missing mandatory usage; request runner flags propagation and preserve hidden-token ruling.
R2-m1 — fixed (NOT EXECUTED) — 90fb01a10e0123d0a444425cef00b3b96f77f911 — judge_score_tag_missing flags absent closed score tags for the two upstream normalizers without changing their numeric output.
