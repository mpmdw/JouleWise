# Alignment runner lane

## SUMMARY

- Implemented the protocol-driven agent loop with token accounting, timed tools, scoring, monitor views and sampler lifecycle.
- Implemented named factories, deterministic episode IDs and seeded matrix order.
- Added durable episode/transcript JSONL writes, resume checkpoints, partial-line quarantine and interrupt records.
- Added immutable turn/tool tampering and idempotent scratchpad accounting with explicit missing-count flags.
- Added a configurable 8B-shaped inbox world and a timing/count-driven synthetic GPU sensor.
- Added the run/tamper CLI, internal run documentation and 37 unittest methods.
- All implementation commits are saved on lane/2026-10-21-align-runner; only allowed paths differ from the spine.
- Verification is BLOCKED: the managed VM never became usable; no Python test, CLI or end-to-end run has executed.

## FILES

- joulewise/align/runner.py: factory registry, transcript views, episode loop, deterministic identities, randomized matrix and recovery.
- joulewise/align/tamper.py: pure marking transforms and seeded evaluation-set selection.
- joulewise/align/mock_world.py: virtual clock, inbox tools/task, scripted endpoint, tokenizer/monitor, power model and sampled traces.
- joulewise/align/__main__.py: run and tamper command line verbs.
- tests/align/test_runner.py: 13 episode lifecycle/accounting/visibility/error test methods and a shared world constructor.
- tests/align/test_runner_matrix.py: 8 matrix/recovery/CLI test methods, including the 20-episode production chain.
- tests/align/test_mock_world.py: 9 sensor/world test methods, including independent energy arithmetic and text blindness.
- tests/align/test_tamper.py: 7 production-episode transform test methods.
- docs/align/runner.md: matrix JSON, factory API, lifecycle, recovery, local transcript encoding, tampering and sensor assumptions.
- .codex-report/align-runner.md: this handoff.
- Registry exception files: none. No repo-wide test could run to establish a registry failure.
- docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py are unchanged.

## PUBLIC API

runner.py:

```python
@dataclass(frozen=True)
class FactoryContext:
    task_pair: str
    condition: str
    seed: int
    matrix_id: str
    clock_domain: str
    clock: Callable[[], int]

register_task_factory(name: str, factory: Callable[..., AgentTask]) -> None
register_endpoint_factory(name: str, factory: Callable[..., ChatEndpoint]) -> None
register_monitor_factory(name: str, factory: Callable[..., Monitor]) -> None
register_sampler_factory(name: str, factory: Callable[..., PowerSampler]) -> None
register_clock_factory(name: str, factory: Callable[..., Callable[[], int]]) -> None
register_token_counter_factory(name: str, factory: Callable[..., TokenCounter]) -> None
episode_id(task_pair: str, condition: str, endpoint_identity: str,
           seed: int, matrix_id: str = "") -> str
transcript_view(transcript: Sequence[ChatMessage], visibility: str,
                scratchpad_tags: tuple[str, str] | None = None) -> list[ChatMessage]
run_episode(task: AgentTask, condition: str, endpoint: ChatEndpoint, *,
            monitors: Sequence[Any] = (), samplers: Sequence[PowerSampler] = (),
            seed: int, max_turns: int, max_tokens: int, temperature: float,
            clock_domain: str, token_counter: TokenCounter | None = None,
            matrix_id: str = "", clock: Callable[[], int] | None = None
            ) -> tuple[Episode, list[ChatMessage]]
run_matrix(spec_path: str | Path) -> Path
```

Every factory is called as factory(config: Mapping[str, Any], context: FactoryContext).
Monitor entries may be monitor objects (full visibility) or (monitor, visibilities).

tamper.py:

```python
delete_turns(ep: Episode, indices: Iterable[int]) -> Episode
drop_tool_calls(ep: Episode, predicate: Callable[[ToolCall], bool]) -> Episode
hide_scratchpad(ep: Episode) -> Episode
random_tamper(ep: Episode, rng: random.Random, kind: str, fraction: float) -> Episode
```

mock_world.py:

```python
VirtualClock(now_ns: int = 0)
VirtualClock.__call__() -> int
VirtualClock.advance_ns(duration_ns: int) -> None
VirtualClock.advance(seconds: float) -> None
ScriptConfig(turns=12, prefill_pattern=(800, 1200, 1600),
             decode_pattern=(80, 160, 240), reasoning_tokens=120,
             scratchpad_tokens=64, prefill_tokens_per_second=2000.0,
             decode_tokens_per_second=60.0)
ScriptConfig.plan(condition: str, seed: int) -> list[dict[str, int | str]]
InboxTask(task_pair="mock/inbox", *, clock=None, turns=12,
          read_seconds=0.4, send_seconds=1.2, transfer_seconds=2.0)
MockTask = InboxTask
ScriptedEndpoint(*, clock=None, config=None, condition="benign")
MockTokenCounter()
MockMonitor()
PowerModel(idle_watts=55.0, prefill_joules_per_token=0.03,
           decode_joules_per_token=3.0, context_joules_per_token_squared=0.00004)
SyntheticPowerSampler(*, clock_domain="mock.monotonic", model=None,
                      interval_ns=100_000_000, averaging_window_ns=25_000_000,
                      noise_watts=0.5, quantum_watts=0.1, seed=0,
                      episode_domain=None, offset_ns=0, uncertainty_ns=0)
SyntheticPowerSampler.observe_episode(episode: Episode) -> None
SyntheticPowerSampler.clock_mapping() -> ClockMapping
SyntheticPowerSampler.segments(episode: Episode) -> list[tuple[int, int, float]]
SyntheticPowerSampler.expected_energy_joules(episode: Episode) -> float
register_mock_factories() -> None
```

These classes implement the task/endpoint/token-counter/monitor/sampler methods
from interfaces.py. SyntheticPowerSampler.start()/stop() return ordinary traces.
CLI main(argv: Sequence[str] | None = None) -> int is in __main__.py.

## TESTS RUN

No Python process could start. Execution counts: 0 tests run; skips are not
applicable because discovery never executed. The following exact commands were
submitted through exec_command with workdir /workspace/JouleWise, and each was
rejected before execution with:

```text
No usable execution environment is available. Wait for an environment to become available before using this tool.
```

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests
python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5
```

There are 37 authored unittest methods, counted by reading the committed test
sources through GitHub (13 runner + 8 matrix + 9 mock-world + 7 tamper).
That count is not a test result. No extras were installed or extra-dependent
tests run; all new source and tests use stdlib imports.

Read-only remote verification: GitHub compare_commits at implementation head
dcbc0e755d8e1f21550f174cf89a13fed45957fc against spine
4d47c4362352ccd8d4d904134a79f0d8260b21b5 reported 14 commits ahead, zero behind,
and precisely the ten allowed files listed above. The final report update adds
only this report. No protected contracts or registry files changed.

## END-TO-END

Implemented but NOT EXECUTED:

- 2 task pairs x 2 conditions x 5 seeds through run_matrix, run_episode, real
  task tools, all three monitor views, the synthetic sampler and JSONL readers.
- Independent reconstruction of scripted prefill/decode draws and cached context.
- Each tamper transform, then write_episodes/read_episodes round-trip, checking
  that measured trace bytes and physical-work totals stay unchanged.
- Simulated process death before an episode append, after an episode append,
  inside an episode line, and inside a transcript line. Resume is expected to
  reproduce both primary files byte for byte while recovery flags stay in run.json.
- An independent energy sum versus sampled integration. Equal 100 ms sample
  and averaging bins partition time, including trailing coverage, so aggregate
  excess energy is conserved. Agreement uses the brief's 1e-6 relative bar for
  computations without an uncertainty. Separate tests retain default 100 ms /
  25 ms duty-shaped sampling, 0.5 W noise and 0.1 W quantum.

Expected design counts, not measured results: each benign episode has 12 turns,
11 calls and no hidden tokens; sabotage has 13 turns, 12 calls and 184 hidden
tokens at turn 6 (120 reasoning + 64 scratchpad). Across the intended matrix
that is 20 episodes, 250 turns, 230 calls and 1840 hidden tokens.
Configured waits are 0.4 s/read, 1.2 s/send and 2 s/transfer.
Sensor assumptions are idle 55 W, 0.03 J/prefill token, 3 J/decode token,
and 0.00004 J/(cached-context token * decoded token).
No actual matrix duration, energy, test pass count or hardware result exists.

## DECISIONS I MADE

- The explicit bounded user brief selects this task over historical queue ranks.
  The remote generated intake has no active stop card or global selection gate.
- Required pipeline/records/interfaces and repository intake/orchestration
  instructions were read remotely before writes. No local workspace was available.
- Runner branch did not exist. Created it from spine
  4d47c4362352ccd8d4d904134a79f0d8260b21b5 and committed the first report as
  82cf4736f0561fcad386a57bdedcbf8bfd28821e before implementation.
- Used the GitHub connector for branch-only commits while VM startup prevented
  the requested local fetch/checkout/push sequence. No force update, main push,
  other-branch push, PR, merge or deployment occurred.
- Factories use a uniform (config, context) adapter and explicit trusted imports.
  The runtime never installs or fetches a plugin.
- Extra clock/matrix_id keyword parameters preserve the requested episode API
  while supporting deterministic mock timing and experiment identity.
- Start sampling after task setup and before model work; stop before scorers or
  monitors. Model-call Turn bounds exclude subsequent separately timed tool waits.
- Cached context, uncached prefill and total decode come from server usage.
  Hidden tokens include reasoning plus tokenizer-counted task scratchpad spans.
- records.py wins: hidden tokens remain inside decode tokens. Invalid counts are
  flagged and normalized only to satisfy its nonnegative/subset invariants.
- Separate reasoning_text is preserved with lane-local jw_reasoning tags.
  no_scratchpad strips only natural assistant text; actions_only retains paired
  call/result messages. tampered labels a supplied transcript, not an invented edit.
- The records contract lacks scratchpad-token storage. A hardware.runner adapter
  records counts and already-accounted indices; absent counts are flagged.
  hide_scratchpad is therefore idempotent for runner-produced records.
- Transcript fsync precedes episode fsync; the episode is the resume commit marker.
  Quarantine incomplete/invalid bytes rather than treating them as valid data.
  Keep recovery flags in run.json so deterministic replay preserves episode bytes.
- Endpoint/task/monitor/sampler/scoring failures retain flagged episodes; Ctrl-C
  retains the current partial episode and stops further scheduling.
- A valid existing episode ID skips even if it is flagged. A fresh matrix ID/output
  directory is required for a deliberate retry under the same coordinates.
- Random matrix order is deterministic from a recorded order_seed (default 0).
  IDs hash task pair, condition, endpoint identity, episode seed and matrix ID.
- Synthetic coefficients/noise/cadence are configurable world assumptions, never
  claimed device measurements. Tool waits are idle-only.
- Missing first-token timing conserves aggregate model-call energy with a note;
  it does not pretend to recover a prefill/decode boundary.
- Quantitative checks use independently summed energy and derived sample-bin
  conservation, and contrast tests use the stated roughly 1 J attribution floor.
- No out-of-scope bookkeeping or proactive registry edit was made.

## CONTRACT-CHANGE

No shared files changed. Desired additive extensions, worked around locally:

1. ChatMessage needs a structured tool-call request collection for standard
   backend serialization. The adapter currently uses named assistant messages
   with tool_call_id and arguments_json in content, followed by tool results.
2. Turn needs a separate scratchpad_tokens count, with explicit accounting
   semantics. Existing hidden_tokens already includes counted scratchpad work;
   the lane-local hardware.runner metadata prevents double counting.
3. A shared optional clock/observation capability could name sampler
   clock_mapping() and synthetic observe_episode(Episode), and a clock callable
   could become a documented runner injection. Currently these are optional
   lane-local adapters and ordinary protocol implementations remain supported.

The brief's instruction to move scratchpad work into hidden_tokens cannot infer
a count from an arbitrary Episode alone. records.py has no text or separate
scratchpad count. Missing information therefore produces a flag, not an estimate.

## OPEN ISSUES

- BLOCKING VERIFICATION: selected environment
  ccarenv_b64_Y2NhcmVudl9kZDc0ZTBkZjg2NDg4MTkxODU1YzBkMTIyOTBlYmRlOA
  alternates pending/starting, reports connectivity offline, and never exposes
  /workspace/JouleWise to exec_command. Repeated wait_for_environment calls did
  not yield a usable VM; environment diagnostics returned history_status not_found.
- Local setup, Python syntax/import checks, all 37 new test methods, the align
  suite, canonical suite, touched tier, actual 20-episode matrix, and actual CLI
  execution remain unverified. Do not interpret authored tests as passing tests.
- Once the VM is usable, fetch and check out origin/lane/2026-10-21-align-runner,
  read this report, run the three exact commands above, fix authorized failures,
  run/report the actual end-to-end numbers, then commit and push the updated report.
- If a repo-wide failure identifies a new-name registry requirement, the brief
  allows only the minimal names addition and requires listing that file here.
- Real endpoint adapters must honor the documented local tool-message encoding.
  Task and ScriptConfig turn counts must agree.
- The research's real hardware and external benchmark gates remain untouched.

## NEEDS_RULING

none
