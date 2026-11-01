# Alignment runner lane — fix round 2

## SUMMARY

- Retained raw endpoint usage and lifted returned/exception-carried diagnostics into Episode flags.
- Recovered unreported separated reasoning only with an explicit tokenizer, preserving its provenance flag.
- Replaced undeclared endpoint slots with public-config digests so reordered matrices retain both arms.
- Added noop labels to ineffective delete/drop transforms, including random and CLI paths.
- Gave task scorers reasoning-stripped endpoint history while preserving archive and monitor views.
- Replaced history-dependent nested test runs with direct current-code regressions.
- Made synthetic prompt/cache usage depend on received messages and explicit cache assumptions.
- All 71 stdlib tests and all five reviewer commands pass locally; discovery wall time fell from 91.349 s to 11.561 s.
- Protected contracts and shade-lane files remain unchanged; no hardware run is claimed.

## FILES

- joulewise/align/runner.py: endpoint diagnostics/raw usage, partial-failure retention, scorer view, config-derived cells and undeclared-pair flags.
- joulewise/align/tamper.py: effective/ineffective delete and drop labelling without altering selection or measured work.
- joulewise/align/mock_world.py: message-derived request counts, block cache, configurable transcript payload size and independent work ledger.
- tests/align/test_runner.py: lifecycle, usage/failure provenance, scorer and monitor regressions.
- tests/align/test_runner_matrix.py: 20-cell reconstruction, durable recovery, arm reorder/removal, factory failures and CLI noop.
- tests/align/test_runner_review.py: direct current-code agreement/recovery/edge checks replacing git archives and nested discovery.
- tests/align/test_mock_world.py: independent prompt/cache arithmetic, reasoning-feedback mutation and sensor-derived effect bars.
- tests/align/test_tamper.py: empty/repeated/small-fraction noop checks and unchanged physical work.
- docs/align/runner.md: format, procedures, migration, views, provenance and synthetic assumptions.
- .codex-report/align-runner.md: this report.
- Temporary tests/align/test_runner_round2_repro.py was used only for the explicitly authorized CI fallback and is deleted from the final tree.
- joulewise/align/__main__.py remains unchanged; its drop-without-name path is tested.
- No registry additions in Round 2. The inherited tests/test_shard_tests.py align-prefix exception is unchanged.
- docs/align/PIPELINE.md, joulewise/align/records.py, joulewise/align/interfaces.py and all shade files are unchanged.

## PUBLIC API

The runner/registry/transcript/tamper signatures remain unchanged:

```python
run_episode(task: AgentTask, condition: str, endpoint: ChatEndpoint, *,
            monitors: Sequence[Any] = (), samplers: Sequence[PowerSampler] = (),
            seed: int, max_turns: int, max_tokens: int, temperature: float,
            clock_domain: str, token_counter: TokenCounter | None = None,
            matrix_id: str = "", clock: Callable[[], int] | None = None
            ) -> tuple[Episode, list[ChatMessage]]
run_matrix(spec_path: str | Path) -> Path
episode_id(task_pair: str, condition: str, endpoint_identity: str,
           seed: int, matrix_id: str = "") -> str
transcript_view(transcript: Sequence[ChatMessage], visibility: str,
                scratchpad_tags: tuple[str, str] | None = None) -> list[ChatMessage]
register_task_factory(name: str, factory: Callable[..., AgentTask]) -> None
register_endpoint_factory(name: str, factory: Callable[..., ChatEndpoint]) -> None
register_monitor_factory(name: str, factory: Callable[..., Monitor]) -> None
register_sampler_factory(name: str, factory: Callable[..., PowerSampler]) -> None
register_clock_factory(name: str, factory: Callable[..., Callable[[], int]]) -> None
register_token_counter_factory(name: str, factory: Callable[..., TokenCounter]) -> None
delete_turns(ep: Episode, indices: Iterable[int]) -> Episode
drop_tool_calls(ep: Episode, predicate: Callable[[ToolCall], bool]) -> Episode
hide_scratchpad(ep: Episode) -> Episode
random_tamper(ep: Episode, rng: random.Random, kind: str, fraction: float) -> Episode
```

FactoryContext and factory(config, context) are unchanged. Existing mock class names,
factory names and constructor parameters remain available. Additive workload assumptions:

```python
ScriptConfig(..., message_overhead_tokens: int = 4, cache_block_tokens: int = 16)
InboxTask(..., observation_tokens: int = 800)
```

These are configurable synthetic assumptions. ScriptConfig.plan's generated-work
rows remain inspectable; prefill/context there are legacy nominal targets. Actual
prompt/context/prefill now come from received messages and matching cache prefixes.
The mock endpoint identity advances to mock/synthetic-8B/v2/<config digest>.
hardware.runner adds raw_usage, failed_requests and scoring_transcript_view.
No shared record or protocol changes.

Unchanged mock ledger and sensor APIs:

```python
ModelWork(start_ns: int, first_token_ns: int | None, end_ns: int,
          context_tokens: int, prefill_tokens: int, decode_tokens: int)
ToolWork(name: str, start_ns: int, end_ns: int)
WorkLedger(turns: list[ModelWork] = ..., tools: list[ToolWork] = ...)
SyntheticPowerSampler(*, clock_domain="mock.monotonic", model=None,
                      interval_ns=100_000_000, averaging_window_ns=25_000_000,
                      noise_watts=0.5, quantum_watts=0.1, seed=0,
                      episode_domain=None, offset_ns=0, uncertainty_ns=0,
                      clock: VirtualClock | None = None,
                      ledger: WorkLedger | None = None, supply_limit: bool = False)
SyntheticPowerSampler.sample_ledger(ledger: WorkLedger, *,
                                   start_ns: int, end_ns: int) -> tuple[PowerTrace, ...]
SyntheticPowerSampler.segments(episode: Episode | WorkLedger) -> list[tuple[int, int, float]]
SyntheticPowerSampler.expected_energy_joules(episode: Episode) -> float
```

```python
VirtualClock(now_ns: int = 0)
VirtualClock.advance(seconds: float) -> None
VirtualClock.advance_ns(duration_ns: int) -> None
ScriptedEndpoint(*, clock: VirtualClock | None = None,
                 config: ScriptConfig | None = None, condition: str = "benign")
MockTokenCounter.count_tokens(text: str) -> int
register_mock_factories() -> None
```

InboxTask/MockTask, ScriptedEndpoint, MockMonitor and SyntheticPowerSampler still
implement the corresponding shared protocols. PowerModel's configurable coefficients
and sampler defaults retain their documented assumptions.

## TESTS RUN

VM: Python 3.12.14, cwd=/workspace/JouleWise. Exact baseline commit:
ec4a3727090e639b54d2fc636a4762bd997c6483. Fixed code/test tree: d20735e9509c925a0c12a70ec530de9608eacf7c;
all production/test bytes in the final report commit are identical to this tree.
The temporary CI harness is absent. No project extra was installed; no
extra-dependent test exists in this lane, so no extra run is applicable.

Commands below were launched verbatim by /tmp/r2/measure.py. It records
perf_counter wall time plus stdout/stderr/return code under /tmp/r2. The initial
/usr/bin/time wrapper exited 127 before starting tests because that executable is
absent; Python timing then ran successfully. No test failure was concealed.

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.align.test_runner_review
python3 -I /tmp/r2/scripts/run_in.py /workspace/JouleWise /tmp/r2/scripts/r2_integration.py /tmp/r2/shade-6da/endpoints.py
python3 -I /tmp/r2/scripts/run_in.py /workspace/JouleWise /tmp/r2/scripts/r2_integration.py /tmp/r2/shade-5bb/endpoints.py
python3 -I /tmp/r2/scripts/run_in.py /workspace/JouleWise /tmp/r2/scripts/r2_episodes.py
python3 -I /tmp/r2/scripts/run_in.py /workspace/JouleWise /tmp/r2/scripts/r2_edges.py
python3 -I /tmp/r2/scripts/run_in.py /workspace/JouleWise /tmp/r2/scripts/r2_matrix.py /workspace/JouleWise
```

Discovery ran at both revisions; the focused review-module command ran on the
fixed revision. All five repro commands ran at both revisions in the listed order.
Every listed command returned 0. Baseline diagnostic lines reproduce the reported
bugs even though the existing ledger checks already report zero failures.

| Command | Baseline wall s | Fixed wall s | Fixed result |
| --- | ---: | ---: | --- |
| align discovery | 91.349124725 | 11.561278170 | 71 tests, 0 failures/errors/skips |
| focused review module | not separately timed on VM | 5.027511975 | 5 tests, 0 failures/errors/skips |
| integration-6da | 0.670052033 | 0.657235144 | all required printed conditions checked; exit 0 |
| integration-5bb | 0.749127296 | 0.673733859 | all required printed conditions checked; exit 0 |
| episodes | 3.053424989 | 2.988637806 | 970 checks, 0 failures |
| edges | 0.126777662 | 0.100532015 | all required printed conditions checked; exit 0 |
| matrix | 47.385953657 | 47.207214182 | 80 checks, 0 failures |

Baseline discovery: 57 tests, zero failures/errors/skips (unittest's internal
runtime 91.049 s). Fixed discovery: 71 tests, zero failures/errors/skips (internal
runtime 11.428 s). The same command's observed wall difference is
-79.787846555 s; this is a single operational timing observation, not a
controlled performance claim. Focused fixed-module internal runtime: 4.879 s.

| Module | Baseline tests | Fixed tests | Fixed failures/errors/skips |
| --- | ---: | ---: | --- |
| tests.align.test_runner | 19 | 23 | 0/0/0 |
| tests.align.test_runner_matrix | 16 | 19 | 0/0/0 |
| tests.align.test_runner_review | 1 | 5 | 0/0/0 |
| tests.align.test_mock_world | 10 | 11 | 0/0/0 |
| tests.align.test_tamper | 7 | 9 | 0/0/0 |
| tests.align.test_records | 4 | 4 | 0/0/0 |
| Total | 57 | 71 | 0/0/0 |

Before the VM became usable, [baseline CI run 39732883580](https://github.com/mpmdw/JouleWise/actions/runs/39732883580)
also executed all five repro commands at harness-only commit
a4dc89cd1e3b8f96f3f83c02fabc8bdd13a9731c. Its production files are identical to ec4a37270.
Python 3.13.16 repro wall times: integration-6da 0.862441311 s,
integration-5bb 0.885528057 s, episodes 4.217752268 s, edges 0.185321944 s,
matrix 59.701939575 s. The harness passed as one test in 65.857 s.
[Repro job 119675434895](https://github.com/mpmdw/JouleWise/actions/runs/39732883580/job/119675434895).

The inherited old review module's [CI job 119675434951](https://github.com/mpmdw/JouleWise/actions/runs/39732883580/job/119675434951)
took 157.049 s. Its nested root/outside-cwd discoveries took 54.341/54.179 s,
58 tests each, no failures/errors, one skip each: the temporary Round-2 harness's
explicit recursion guard avoided repeating the five repros inside those historical
children. Those 57 original tests all ran. This legacy behavior is removed from
the final tree. VM results above require no recursion guard or skips.

Final inspection: git diff --check passes; protected-file SHA-256 values match
the baseline; both /tmp shade files match git show at their exact pinned commits;
only allowlisted files differ. No final runner test invokes git, recursively
launches discovery or executes older implementation code. No whole-repository
suite was manually run; automatic PR CI owns it.

## END-TO-END

Power can count hidden tokens and unlogged tool calls; it is blind to reasoning
that fits inside a single forward pass. All results here are synthetic validation.

The independent world uses its endpoint/task ledgers as truth, a foreign-clock
20 ms cumulative-energy sensor with a 1 mJ quantum, mapped clocks, multi-turn
agent/tool episodes and all monitor views. The 16 direct episodes run through
run_episode, JSON round-trip and mapped-counter checks. The separate 20-cell
matrix runs CLI -> factories -> real run_matrix/run_episode -> traces/verdicts ->
JSONL -> CLI tamper -> JSONL readback -> resume, eight real SIGKILL trials and
SIGINT retention/retry. Its 970 episode checks and 80 matrix checks remain at
zero failures. The counter interpolation bar is the supplied physics derivation:
2 endpoints * 310 W * 0.020 s + 2 * 0.001 J = 12.402 J. Worst per-turn/episode
errors remain 2.34638612169897/0.7960930430926965 J.

Printed scientific/accounting changes from ec4a37270:

- Both integrated clean runs change 40 -> 160 hidden tokens per turn (+120); raw
  usage presence changes False -> True. Completed turn counts stay 4 and 7. HTTP
  500 retains 4 Turns for the returning adapter and 3 completed Turns plus partial
  diagnostics for the raising adapter; the required HTTP/empty/error flags appear.
- Independent unreported-usage case changes hidden 707 -> 3162 (+2455), equal to
  ledger truth. Context remains 0 versus truth 112112 and prefill remains 122491
  versus truth 10379; the missing-cache flag now discloses these unrecoverable
  counts, rather than inventing them.
- Reordered endpoints change ['think=1', 'think=1'] -> ['think=1', 'think=0']; both
  cells run once. The removal case retains both arms without an extra record.
- Unchanged random logs labelled as effective tampering change 16 -> 0, 2 -> 0
  and 12 -> 0 for the three affected small-fraction cases. The other two cases
  remain 0. Empty direct/CLI transforms explicitly name noop.
- Factory-failure record count stays 2, now both carrying matrix.task_pair_undeclared.
- Independent reported-usage direct summary is unchanged: 16 episodes, 357 turns,
  450 calls, 168310 prefill, 98849 decode, 44799 hidden, 2134.860034159 virtual s.
- Independent 20-cell matrix sums are unchanged: 360 turns, 454 calls, 170496
  prefill, 98668 decode, 45992 hidden. Its condition order is unchanged.

The shared inbox world also runs its real 2-pair x 2-condition x 5-seed matrix,
then four tamper datasets and JSONL readback. Tests independently reconstruct
received-message prompt sizes/cache blocks and generated draws, then compare
sensor energy against an independent count sum. Twelve direct commit boundaries
and four partial/commit failure cuts recover identical primary files. New message
history accounting intentionally changes this world's numbers:

| Shared inbox quantity | Before | After | Delta |
| --- | ---: | ---: | ---: |
| episodes | 20 | 20 | 0 |
| turns | 250 | 250 | 0 |
| tool_calls | 230 | 230 | 0 |
| prefill_tokens | 291200 | 243990 | -47210 |
| decode_tokens | 43120 | 43120 | 0 |
| hidden_tokens | 1840 | 1840 | 0 |
| sampled_gross_joules | 205559.04426718 | 199361.07726718 | -6197.96700000 |
| independent_gross_joules | 205559.04426718 | 199361.07726718 | -6197.96700000 |

Each sabotage record still has exactly 184 hidden tokens at turn 6; this is the
scripted 120 reasoning + 64 scratchpad tokens. Maximum per-episode conservation
error changes 1.8189894035458565e-12 -> 9.094947017729282e-13 J (floating-point noise);
both runs use the derived no-uncertainty 1e-6 relative agreement rule.
The isolated hidden-work contrast changes 603.2255999999998 -> 594.5113600000004 J,
a -8.71424 J change from corrected cached context. The configured 8192-position
context contrast stays 741.86752 J at printed precision. Effect-size checks now
use the mock sensor's 2*N*dt*(sigma + quantum/2) design bar, not the borrowed M3 bar.
In the shared inbox world, categorical scores, generated decode/hidden sums and
transform selections remain unchanged. Operational interruption positions vary with wall timing:
kill pre-resume line counts are [8,10,18,9,9,11,4,9] before and
[9,10,18,9,10,11,4,9] after; all eight recovered byte comparisons pass in both runs.
Default SIGINT retains 20 final records with one 19-turn interrupted attempt in
both runs. Retry SIGINT retains 21 records in both; the interrupted attempt changes
19 -> 0 turns and the pre-resume row count 10 -> 11 because the signal landed at
a different point. Both preserve one linked retry and add no repeated retry later.

Final outputs of all five supplied repro commands follow verbatim. The scripts'
legacy label 'adapter flags (raw_usage) dropped' prints the adapter's own flags;
its adjacent raw-usage/episode lines and ordinary JSON assertions establish that
they are now retained. Reserved-tag collision and late-trace lines are deliberately
unchanged; no archive-shape change was authorized in this round.

integration-6da

```text
INTEG clean: turns 4 Episode.flags ('endpoint.cached_prompt_tokens_unreported', 'endpoint.reasoning_tokens_unreported', 'usage.reasoning_uncounted')
INTEG adapter flags (raw_usage) dropped: ['cached_prompt_tokens_unreported', 'reasoning_tokens_unreported']
INTEG hidden per turn [160, 160, 160, 160] (reasoning 120 + scratchpad 40 = 160 per turn)
INTEG raw_usage present in Episode JSON: True
INTEG last request roles: ['system', 'user', 'assistant', 'assistant', 'tool', 'assistant', 'assistant', 'tool', 'assistant', 'assistant', 'tool']
INTEG assistant messages carrying tool-call JSON as content: 3 of 6 | example: {"role": "assistant", "content": "{\"id\": 0}", "name": "read_ticket", "tool_call_id": "call0", "tool_calls": [{"id": "call0", "type": "function", "function": {"name": "read_ticket", "arguments": "{\"
INTEG HTTP 500 on request 4: turns 4 Episode.flags ('endpoint.cached_prompt_tokens_unreported', 'endpoint.reasoning_tokens_unreported', 'usage.reasoning_uncounted', 'endpoint.http_error:500', 'endpoint.stream_missing_done', 'endpoint.missing_or_invalid_prompt_tokens', 'endpoint.missing_or_invalid_completion_tokens', 'endpoint.empty_result') | last turn tokens (0, 0) | adapter flags ['cached_prompt_tokens_unreported', 'http_error:500', 'missing_or_invalid_completion_tokens', 'missing_or_invalid_prompt_tokens', 'reasoning_tokens_unreported', 'stream_missing_done']
```

integration-5bb

```text
INTEG clean: turns 7 Episode.flags ('endpoint.cached_prompt_tokens_unreported', 'endpoint.reasoning_tokens_unreported', 'usage.reasoning_uncounted')
INTEG adapter flags (raw_usage) dropped: ['cached_prompt_tokens_unreported', 'reasoning_tokens_unreported']
INTEG hidden per turn [160, 160, 160, 160, 160, 160, 160] (reasoning 120 + scratchpad 40 = 160 per turn)
INTEG raw_usage present in Episode JSON: True
INTEG last request roles: ['system', 'user', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool']
INTEG assistant messages carrying tool-call JSON as content: 0 of 6 | example: {"role": "assistant", "content": "<thinking>note note note note note note note note note note note note note note note note note note note note note note note note note note note note note note note n
INTEG HTTP 500 on request 4: turns 3 Episode.flags ('endpoint.cached_prompt_tokens_unreported', 'endpoint.reasoning_tokens_unreported', 'usage.reasoning_uncounted', 'endpoint.error.EndpointRequestFailed', 'endpoint.http_error:500', 'endpoint.stream_missing_done', 'endpoint.missing_or_invalid_prompt_tokens', 'endpoint.missing_or_invalid_completion_tokens', 'endpoint.usage_unavailable', 'endpoint.empty_result') | last turn tokens (606, 203) | adapter flags ['cached_prompt_tokens_unreported', 'http_error:500', 'missing_or_invalid_completion_tokens', 'missing_or_invalid_prompt_tokens', 'reasoning_tokens_unreported', 'stream_missing_done', 'usage_unavailable']
```

episodes

```text
R2 SUMMARY {"calls": 450, "decode": 98849, "duration_s": 2134.860034159, "episodes": 16, "hidden": 44799, "max_total_energy_err_J": 0.7960930430926965, "max_turn_energy_err_J": 2.34638612169897, "prefill": 168310, "turns": 357}
---- edges
EDGE vllm-unreported: Episode.flags ('endpoint.reasoning_tokens_unreported', 'endpoint.cached_prompt_tokens_unreported', 'usage.reasoning_uncounted') | hidden recorded 3162 truth 3162 | context recorded 0 truth 112112 | prefill recorded 122491 truth 10379 | raw_usage kept anywhere: True
EDGE real monotonic stamps: turns 5 flags ('episode.max_turns',)
EDGE perf_counter stamps: turns 5 flags ('episode.max_turns',)
EDGE max_turns 0: 0 ('episode.max_turns',) traces 1 trace samples 1
EDGE max_turns 1: 1 ('episode.max_turns',)
EDGE no mapping: 0 ('clock.unmapped',)
EDGE no counter: hidden 2087 flags ('hidden_tokens.scratchpad_uncounted',) counts 0
EDGE thinking off: hidden 830 truth 830 flags ()
R2 CHECKS 970 failures 0
```

edges

```text
SLOT reorder: endpoints recorded ['think=1', 'think=0'] | thinking-off arm ran: True | run.json flags ['matrix.spec_changed']
ZERO-USAGE result: turns 2 last turn (0, 0) flags ('endpoint.http_error:500', 'endpoint.empty_result')
REASONING quoting </jw_reasoning>: visible in no_scratchpad view: True
CONTENT with '<jw_reasoning>': visible text hidden from no_scratchpad monitor: True | counted hidden: 0 flags ()
TIES: turns [(5000000000, 5000000000), (5000000000, 5000000000)] calls [(5000000000, 5000000000), (5000000000, 5000000000)] flags ()
LATE trace (all samples after episode end): attached 1 flags ()
DELETE nothing: ('tamper.delete_turns', 'tamper.delete_turns.noop') | DROP nothing: ('tamper.drop_tool_calls', 'tamper.drop_tool_calls.noop')
```

matrix

```text
MATRIX totals {'turns': 360, 'prefill_tokens': 170496, 'decode_tokens': 98668, 'hidden_tokens': 45992, 'tool_calls': 454}
MATRIX order conditions SbbSbSbSbSSSbSSSbbbb
RANDOM delete_turns fraction 0.02: labelled tampered (no noop flag) but log unchanged: 0 of 20
RANDOM delete_turns fraction 0.05: labelled tampered (no noop flag) but log unchanged: 0 of 20
RANDOM drop_tool_calls fraction 0.02: labelled tampered (no noop flag) but log unchanged: 0 of 20
RANDOM drop_tool_calls fraction 0.1: labelled tampered (no noop flag) but log unchanged: 0 of 20
RANDOM hide_scratchpad fraction 0.1: labelled tampered (no noop flag) but log unchanged: 0 of 20
KILL trial 0: 9 lines before resume; identical after resume: True
KILL trial 1: 10 lines before resume; identical after resume: True
KILL trial 2: 18 lines before resume; identical after resume: True
KILL trial 3: 9 lines before resume; identical after resume: True
KILL trial 4: 10 lines before resume; identical after resume: True
KILL trial 5: 11 lines before resume; identical after resume: True
KILL trial 6: 4 lines before resume; identical after resume: True
KILL trial 7: 9 lines before resume; identical after resume: True
KILL byte mismatches 0 of 8 (baseline run 3.7s)
SIGINT retry=False: rc 0; before resume 10 episodes, after 20; interrupted records 1 with turns [19]; retries 0
SIGINT retry=True: rc 0; before resume 11 episodes, after 21; interrupted records 1 with turns [0]; retries 1
SLOT after removing endpoint 0: records ['r2/vllm-sim/r2/qwen3-8b-like/think=1', 'r2/vllm-sim/r2/qwen3-8b-like/think=0'] run.json flags ['matrix.spec_changed'] | thinking-off episode present: True
FAIL-RECORD task_pair/endpoint/flags: [('r2.tickets', 'qwen3-8b-like-thinking', ('factory.error.TypeError', 'matrix.task_pair_undeclared')), ('r2.tickets', 'qwen3-8b-like-thinking', ('factory.error.TypeError', 'matrix.task_pair_undeclared'))]
R2 MATRIX CHECKS 80 failures 0
```

Baseline outputs from the exact ec4a37270 VM checkout are retained here too:

baseline integration-6da

```text
INTEG clean: turns 4 Episode.flags ()
INTEG adapter flags (raw_usage) dropped: ['cached_prompt_tokens_unreported', 'reasoning_tokens_unreported']
INTEG hidden per turn [40, 40, 40, 40] (reasoning 120 + scratchpad 40 = 160 per turn)
INTEG raw_usage present in Episode JSON: False
INTEG last request roles: ['system', 'user', 'assistant', 'assistant', 'tool', 'assistant', 'assistant', 'tool', 'assistant', 'assistant', 'tool']
INTEG assistant messages carrying tool-call JSON as content: 3 of 6 | example: {"role": "assistant", "content": "{\"id\": 0}", "name": "read_ticket", "tool_call_id": "call0", "tool_calls": [{"id": "call0", "type": "function", "function": {"name": "read_ticket", "arguments": "{\"
INTEG HTTP 500 on request 4: turns 4 Episode.flags () | last turn tokens (0, 0) | adapter flags ['cached_prompt_tokens_unreported', 'http_error:500', 'missing_or_invalid_completion_tokens', 'missing_or_invalid_prompt_tokens', 'reasoning_tokens_unreported', 'stream_missing_done']
```

baseline integration-5bb

```text
INTEG clean: turns 7 Episode.flags ()
INTEG adapter flags (raw_usage) dropped: ['cached_prompt_tokens_unreported', 'reasoning_tokens_unreported']
INTEG hidden per turn [40, 40, 40, 40, 40, 40, 40] (reasoning 120 + scratchpad 40 = 160 per turn)
INTEG raw_usage present in Episode JSON: False
INTEG last request roles: ['system', 'user', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool', 'assistant', 'tool']
INTEG assistant messages carrying tool-call JSON as content: 0 of 6 | example: {"role": "assistant", "content": "<thinking>note note note note note note note note note note note note note note note note note note note note note note note note note note note note note note note n
INTEG HTTP 500 on request 4: turns 3 Episode.flags ('endpoint.error.EndpointRequestFailed',) | last turn tokens (606, 203) | adapter flags ['cached_prompt_tokens_unreported', 'http_error:500', 'missing_or_invalid_completion_tokens', 'missing_or_invalid_prompt_tokens', 'reasoning_tokens_unreported', 'stream_missing_done', 'usage_unavailable']
```

baseline episodes

```text
R2 SUMMARY {"calls": 450, "decode": 98849, "duration_s": 2134.860034159, "episodes": 16, "hidden": 44799, "max_total_energy_err_J": 0.7960930430926965, "max_turn_energy_err_J": 2.34638612169897, "prefill": 168310, "turns": 357}
---- edges
EDGE vllm-unreported: Episode.flags () | hidden recorded 707 truth 3162 | context recorded 0 truth 112112 | prefill recorded 122491 truth 10379 | raw_usage kept anywhere: False
EDGE real monotonic stamps: turns 5 flags ('episode.max_turns',)
EDGE perf_counter stamps: turns 5 flags ('episode.max_turns',)
EDGE max_turns 0: 0 ('episode.max_turns',) traces 1 trace samples 1
EDGE max_turns 1: 1 ('episode.max_turns',)
EDGE no mapping: 0 ('clock.unmapped',)
EDGE no counter: hidden 2087 flags ('hidden_tokens.scratchpad_uncounted',) counts 0
EDGE thinking off: hidden 830 truth 830 flags ()
R2 CHECKS 970 failures 0
```

baseline edges

```text
SLOT reorder: endpoints recorded ['think=1', 'think=1'] | thinking-off arm ran: False | run.json flags ['matrix.spec_changed']
ZERO-USAGE result: turns 2 last turn (0, 0) flags ()
REASONING quoting </jw_reasoning>: visible in no_scratchpad view: True
CONTENT with '<jw_reasoning>': visible text hidden from no_scratchpad monitor: True | counted hidden: 0 flags ()
TIES: turns [(5000000000, 5000000000), (5000000000, 5000000000)] calls [(5000000000, 5000000000), (5000000000, 5000000000)] flags ()
LATE trace (all samples after episode end): attached 1 flags ()
DELETE nothing: ('tamper.delete_turns',) | DROP nothing: ('tamper.drop_tool_calls',)
```

baseline matrix

```text
MATRIX totals {'turns': 360, 'prefill_tokens': 170496, 'decode_tokens': 98668, 'hidden_tokens': 45992, 'tool_calls': 454}
MATRIX order conditions SbbSbSbSbSSSbSSSbbbb
RANDOM delete_turns fraction 0.02: labelled tampered (no noop flag) but log unchanged: 16 of 20
RANDOM delete_turns fraction 0.05: labelled tampered (no noop flag) but log unchanged: 2 of 20
RANDOM drop_tool_calls fraction 0.02: labelled tampered (no noop flag) but log unchanged: 12 of 20
RANDOM drop_tool_calls fraction 0.1: labelled tampered (no noop flag) but log unchanged: 0 of 20
RANDOM hide_scratchpad fraction 0.1: labelled tampered (no noop flag) but log unchanged: 0 of 20
KILL trial 0: 8 lines before resume; identical after resume: True
KILL trial 1: 10 lines before resume; identical after resume: True
KILL trial 2: 18 lines before resume; identical after resume: True
KILL trial 3: 9 lines before resume; identical after resume: True
KILL trial 4: 9 lines before resume; identical after resume: True
KILL trial 5: 11 lines before resume; identical after resume: True
KILL trial 6: 4 lines before resume; identical after resume: True
KILL trial 7: 9 lines before resume; identical after resume: True
KILL byte mismatches 0 of 8 (baseline run 3.6s)
SIGINT retry=False: rc 0; before resume 10 episodes, after 20; interrupted records 1 with turns [19]; retries 0
SIGINT retry=True: rc 0; before resume 10 episodes, after 21; interrupted records 1 with turns [19]; retries 1
SLOT after removing endpoint 0: records ['r2/vllm-sim/r2/qwen3-8b-like/think=1', 'r2/vllm-sim/r2/qwen3-8b-like/think=0'] run.json flags ['matrix.spec_changed'] | thinking-off episode present: True
FAIL-RECORD task_pair/endpoint/flags: [('r2.tickets', 'qwen3-8b-like-thinking', ('factory.error.TypeError',)), ('r2.tickets', 'qwen3-8b-like-thinking', ('factory.error.TypeError',))]
R2 MATRIX CHECKS 80 failures 0
```


## DECISIONS I MADE

- Continued ec4a3727090e639b54d2fc636a4762bd997c6483 and read its report before the protected plan/records/interfaces. Intake reported no active stop card; the brief's exhaustive WRITE_SCOPE controls writes.
- The VM initially reported starting/offline and exec_command was unavailable. Used the expressly authorized GitHub/PR #533 CI fallback for the baseline and saved fixes as remote commits. The VM became usable during the session; then ran the exact baseline and fixed commands locally on Python 3.12.14. No force update, other-branch push, main push or merge.
- Baseline CI commit a4dc89cd1e3b8f96f3f83c02fabc8bdd13a9731c changes only the temporary harness; its production files are byte-identical to ec4a37270. Baseline CI repros finished before publishing the prepared fixes. The supplied six scripts are unchanged; materialized in the CI temporary directory and later at /tmp/r2/scripts on the VM. Both pinned shade files are fetched as public code, never merged or edited.
- Raw usage is kept per request index. Exception flags and partial_result are optional capabilities read with getattr against ChatResult from interfaces.py; no endpoint implementation is imported.
- A returned zero-usage result remains a flagged Turn. A raised request retains its partial result in hardware.runner.failed_requests, without creating a completed Turn or executing incomplete tool calls. HTTP 500 therefore leaves four Turns with the old returning adapter, and three completed Turns plus failure diagnostics with the raising adapter.
- Nonempty unreported reasoning always adds usage.reasoning_uncounted. With token_counter it contributes a labelled local count; without one it contributes no estimated native reasoning tokens. Server-reported reasoning is never counted twice. Scratchpad accounting and the hidden<=decode contract clamp are unchanged.
- Task scoring uses endpoint_history, stripping separated reasoning and retaining task scratchpads and actions/results. Archive/full/no_scratchpad/actions_only monitor policies are unchanged.
- Undeclared endpoint keys use the credential-stripped component-spec digest; declared identities remain unchanged. Reordering/removing arms and credential-only edits preserve cells. Old undeclared slot-key directories retain their old records and append new config-key cells; use a fresh directory/matrix ID and review old attempts explicitly. No real-hardware data exists under those slot keys.
- Noop describes whether the invocation changed a logged flag (or hidden count for scratchpads). Selection remains round(fraction*eligible) with Python half-even rounding and no minimum-one rule. Flags remain cumulative.
- A failed undeclared task keeps its safe factory fallback pair and gains matrix.task_pair_undeclared; this is a flag, never a scheduling refusal.
- The requested archive format is retained. Native reasoning opt-in is deferred because ChatMessage has no native reasoning field; forwarding wrapper text would change backend content. The structured-message convention below is the proposed solution.
- ScriptedEndpoint counts actual received text, schema text and configured role envelopes; cached tokens are the matching previous request rounded down to configurable blocks. Initial context/tool observations carry their configurable payload in the transcript. Generated reasoning cannot silently remain in cache under the strip policy.
- Kept legacy ScriptConfig fields/constructor keys as nominal planning inputs while moving measured usage to the message path; tests independently reconstruct request usage instead of asserting nominal prefill draws.
- Synthetic effect-size bars now use 2*N*dt*(sigma+quantum/2), conservatively summing both traces' per-sample noise/quantum without averaging down. This is a design check, not a GPU confidence interval. No-uncertainty arithmetic retains the brief's 1e-6 relative agreement bar.
- Current-code assertions retain the old review checks through direct lifecycle, matrix, retry/duplicate/condition/credential and recovery tests. No final runner test invokes git, unittest discovery or an older implementation.
- No extra dependency was installed. Ordinary tests make no network calls; only the explicitly supplied integration repro binds a localhost fake server. Nothing contacts an external model, paid API or hardware.

## CONTRACT-CHANGE

No shared file changed. Proposed additive conventions, with runner-local adapters in this round:

1. Define raw_usage["joulewise"]["flags"] as diagnostic strings and optional request exceptions' flags/partial_result ChatResult consistently across endpoint adapters. Preserve raw usage and propagate endpoint.<flag> into Episode.flags.
2. Add structured assistant tool requests and a separated reasoning field to ChatMessage. Archive them without wrapper parsing; adapters serialize one assistant turn, scorers receive visible assistant content, and reasoning history policy remains explicit (default strip). This would also resolve reserved-tag collisions without changing this round's archive shape.
3. Add explicit scratchpad token/visibility accounting to Turn; hardware.runner supplies it locally now.
4. Document optional sampler clock_mapping() and injected clocks across lanes. No sampler Episode-observation capability is requested.

## OPEN ISSUES

- Code-head CI run 39738652279 is queued as of this report; local required checks above have passed. The final report-only commit uses [skip ci] to preserve that code-head run.
- Gate-ledger run 39738652118 fails the unchanged draft PR body because its lead-owned gates remain NOT-RUN. This is not a lane test failure or merge attestation.
- Unreported cache counts cannot be recovered from completion text; affected context/prefill values remain flagged.
- Slot-key output migration requires explicit review; old records are retained rather than reassigned.
- The unchanged wrapper representation has reserved-tag collision limitations, as printed by r2_edges.py; the structured-message proposal addresses them.
- PR #533 remains a draft; lead-owned review, merged-tree/cold/final-head/merge gates are not claimed here.
- Synthetic evidence does not establish real-hardware sensitivity.

## NEEDS_RULING

RUN-R2-01 / shade hidden-token convention: may separated reasoning that the server
did not count contribute tokenizer-derived hidden tokens? Implemented as directed:
count only when token_counter is supplied and always flag usage.reasoning_uncounted.
In the independent sabotage seed-3 world, including tokenizer-derived native reasoning gives 3162
hidden tokens versus 707 when those 2455 unreported reasoning tokens are excluded
(the scratchpad counter remains active under both readings). The integration
episodes give 160 versus 40 per completed turn: four-turn totals 640 versus 160
with shade 6da, seven-turn totals 1120 versus 280 with shade 5bb. The lead's ruling
can change analysis inclusion of this flagged estimate without rewriting raw usage.

RUN-R1-05 remains: should scratchpads be hidden at baseline, as records.Turn now
specifies, or visible so hide_scratchpad moves them? Kept the contract baseline.
The current inbox sabotage episode has 184 hidden tokens (120 native + 64
scratchpad); the visible-scratchpad reading has 120 and hiding moves 64. Under
the current baseline hiding moves zero and is flagged noop. Physical work is unchanged.

## FIX LOG

- RUN-R1-01 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — validate every endpoint call bracket, with ahead/behind regressions.
- RUN-R1-02 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — strip separated reasoning from endpoint history; retain archival/full-view spans and record policy; strengthened regression in 5a5d2d200c96fe183f82a78b9971b6ae81863ed9.
- RUN-R1-03 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — spec-derived planned cells, pre-factory resume, credential-free failure identities and linked retries.
- RUN-R1-04 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — run distinct task configs, preserve prior variant IDs, flag identical planned duplicates.
- RUN-R1-05 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — flag no-op scratchpad hiding; retain baseline question under NEEDS_RULING.
- RUN-R1-06 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — retain a model Turn before parsing; flag null content and encode non-text tool results.
- RUN-R1-07 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — skip unknown matrix conditions with a named matrix flag.
- RUN-R1-08 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — opt-in retry_flags retain/link old attempts; default behavior remains committed.
- RUN-R1-09 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — CLI subprocesses explicitly select repository cwd and PYTHONPATH.
- RUN-R1-10 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — sensor truth comes from the endpoint/task ledger, without observe_episode.
- RUN-R1-11 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — skip unavailable tampered monitor visibility with a named flag.
- RUN-S fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — propagate distinct named trace flags; add supply-limit matrix and plain-text-note regressions.
- N1 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — require serving limits; flag/record compatible greedy-temperature fallback.
- N2 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — adjacent 1 J derivations and an isolated hidden-token energy comparison.
- N3 noted 55c5e8a60001fd9bf6dfc0b03892bb5ceb87238a — the M3-derived synthetic bar is explicitly not a GPU instrument limit.
- N4 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — state the context coefficient's configurable 25000-token/1 J stress contrast.

### Round 2

- RUN-R2-01 fixed 10f5b3acf57dd273d30d305764bd7f48a74b1fa3 — retain raw usage, lift adapter/exception/partial flags, flag empty results and recover unreported reasoning only with an explicitly supplied tokenizer.
- RUN-R2-02 fixed 10f5b3acf57dd273d30d305764bd7f48a74b1fa3 — key undeclared endpoints by credential-stripped config digests; declared identities retain their behavior.
- RUN-R2-03 fixed 10f5b3acf57dd273d30d305764bd7f48a74b1fa3 — mark empty and repeated delete/drop transforms, including random and CLI paths, with noop flags.
- RUN-R2-04 fixed 8ddac274ae2a83d76e9624e032152418feaf515c — preserve the required archive shape and strip policy; document the structured reasoning/tool proposal and report both shade wire formats.
- RUN-R2-05 fixed 10f5b3acf57dd273d30d305764bd7f48a74b1fa3 — give task scorers endpoint_history while retaining all existing monitor views.
- RUN-R2-06 fixed 10f5b3acf57dd273d30d305764bd7f48a74b1fa3 — replace history/subprocess-discovery probes with direct current-code assertions, including twelve commit-boundary recoveries; temporary harness removed in d20735e9509c925a0c12a70ec530de9608eacf7c.
- RUN-R2-07 fixed 8ddac274ae2a83d76e9624e032152418feaf515c — derive mock prompt and block-cache usage from received messages; test reasoning feedback and independently reconstruct usage.
- RUN-R2-08 fixed 10f5b3acf57dd273d30d305764bd7f48a74b1fa3 — flag task-factory failures whose task_pair was undeclared, retaining and deduplicating the records.
