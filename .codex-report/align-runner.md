# Alignment runner lane — fix round 1

## SUMMARY

- Fixed endpoint clock brackets, separated reasoning history, and retained model work for null content/non-text tools.
- Gave matrices stable planned cells, distinct task-config variants, safe factory failures, and linked retry attempts.
- Skipped unknown matrix conditions and unavailable tampered monitor views with explicit flags.
- Marked scratchpad transforms that change no tokens with tamper.hide_scratchpad.noop.
- Replaced Episode-driven mock power with an independent endpoint/task ledger.
- Propagated named sampler flags, including the configurable synthetic supply-limit scenario.
- Required serving budgets; recorded the compatible greedy-temperature fallback and its flag.
- Verification is running in CI; local execution remains unavailable. No final pass count is claimed yet.
- Shared contracts remain unchanged; the scratchpad baseline question remains for the lead.

## FILES

- joulewise/align/runner.py: episode loop/history/timing, structured power flags, planned cells, factory failures, retries and recovery.
- joulewise/align/tamper.py: flags a hidden-scratchpad application that moves no tokens.
- joulewise/align/mock_world.py: independent ModelWork/ToolWork/WorkLedger, sampler wiring, supply_limit and stated context coefficient.
- tests/align/test_runner.py: lifecycle regressions, endpoint clocks/history/content, monitor availability and notes shapes.
- tests/align/test_runner_matrix.py: production 20-cell matrix, recovery, factories/variants/retries/budgets/supply flags and cwd-stable CLI.
- tests/align/test_mock_world.py: ledger conservation, isolated hidden-work contrast, unchanged sensor truth after Episode mutation.
- tests/align/test_tamper.py: complete noop flag tuples, effective transforms and repeated-transform behavior.
- tests/align/test_runner_review.py: verbatim appendix fixtures, archived baseline/current probes, permitted retry variant, scratchpad readings and both discovery contexts.
- docs/align/runner.md: matrix/factory/identity/recovery/history/flags/mock procedures.
- .codex-report/align-runner.md: this report.
- joulewise/align/__main__.py is unchanged this round; its run/tamper CLI remains tested.
- No registry file changed this round. The previous lane's minimal tests/test_shard_tests.py align-prefix exception remains inherited.
- docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py are unchanged.

## PUBLIC API

All original callable names and keywords remain compatible:

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

FactoryContext and the uniform factory(config, context) signature are unchanged.
New matrix fields: optional endpoint identity and retry_flags. max_turns/max_tokens
are now required for scheduling; missing values produce matrix flags and no work.
Omitted temperature remains greedy with a flag and recorded effective settings.

The mock task/endpoint/token counter/monitor/clock/model APIs and all registered
mock.* names/config keys remain. New public ledger types:

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

SyntheticPowerSampler.start/stop use the independent ledger. Direct mock
components share their clock (VirtualClock.ledger), or the sampler receives an
explicit ledger. The circular observe_episode hook is removed. Factories handle
the wiring. The shared PowerSampler protocol is unchanged.

## TESTS RUN

Execution revision: 55c5e8a60001fd9bf6dfc0b03892bb5ceb87238a.
[CI run 39722106903](https://github.com/mpmdw/JouleWise/actions/runs/39722106903)
passed build, installed-wheel, fences and the quick tier (212 modules, 180
excluded, zero failed modules). Align shards are running/queued; their counts
and the two direct discovery/probe outputs remain pending. The quick command
was `python3 scripts/quick_suite.py --tier quick --workers 4`.
The VM has never started a Python process. No extra was installed.

## END-TO-END

Pending the independent review harness and the production matrix test in CI.
No newly measured end-to-end numbers are claimed at this checkpoint. The
harness executes archived 52999e6a2 probes before current code, prints the six
scratchpad readings, and runs both required align discovery contexts.

## DECISIONS I MADE

- Continued the pushed lane at 52999e6a2a7e165901dcfe813cc7ae68157c59ea; read its report and the three protected governing files first.
- Read AGENTS.md and the targeted intake/playbook/orchestration. No stop card was active; this bounded WRITE_SCOPE owns the work.
- The managed VM never exposed a process executor. Used connected GitHub commits/ref updates and the existing draft PR's CI; no force push, main push, other-branch push or merge.
- Baseline execution uses a local git archive of exactly 52999e6a2 inside CI, before current-code probes. The five supplied sources are unchanged; the additional retry copy changes only the explicitly permitted retry_flags field. No .review1 directory is committed.
- Endpoint stamps must be inside each measured call bracket. Foreign/invalid stamps fall back to that bracket with unknown first-token time. Earlier-domain stamps use clock.endpoint_outside_call; clock.endpoint_out_of_order is no longer added.
- The endpoint history strips separated jw_reasoning spans by default; archived/scored/full-view text retains them. Task scratchpad spans remain in endpoint history.
- Model work enters a provisional Turn before content parsing/tool execution. Null content and serializable fallbacks retain it.
- Planned cells use a sanitized task-spec digest and a declared endpoint identity or factory occurrence slot. Distinct task configs run; identical specs dedupe with a visible diagnostic. Explicit matrix IDs keep prior task variants stable.
- Runtime endpoint/model identities remain separate from planned cells. Factory failures use safe planned names, preserve actual task_pair when construction reaches the task, and link to the same cell as successful retries. Raw config is never written.
- Resume skips complete planned cells before factory calls. Failed factories retry automatically without repeating an unchanged failure diagnostic. Other retry_flags are opt-in; old attempts remain linked and flagged.
- Unknown matrix conditions schedule no cells and remain visible in run.json. The direct run_episode API retains its records-contract fallback and condition.unknown/raw requested-condition metadata; callers must inspect its flags.
- Serving max_turns/max_tokens are required. Greedy temperature=0.0 is retained for compatible matrices with a default flag and recorded value; explicit zero and fallback zero are tested for identical episode/transcript bytes.
- No-op scratchpad hiding stays at the current contract baseline and is explicitly flagged, including random/CLI paths. The baseline question is recorded below without stopping other work.
- run_episode cannot supply a tampered monitor transcript and skips that requested view with a flag. transcript_view still accepts an explicitly supplied tampered view.
- Power-note flags are power.<channel>.<original text>, deduplicated. Other notes use power.notes; notes never drop traces or reject data.
- Mock power reads the independent endpoint/task ledger. Synthetic supply_limit marks supply.battery_assist without inventing a different energy model.
- Synthetic parameters remain configurable assumptions. The context coefficient adds 1 J/decode token at 25000 cached positions; hidden-only energy contrasts hold visible work/context/timing fixed.
- The 1 J synthetic effect-size bar cites the M3 attribution limit and does not claim a GPU limit. No-uncertainty energy comparisons retain 1e-6 relative.
- No extra was installed; no test calls a network, real model service or hardware.

## CONTRACT-CHANGE

No shared contract file changed. Desired additive changes, worked around locally:

1. ChatMessage could expose native separated reasoning and a tool-call collection;
   the current runner strips archived reasoning from backend history and uses
   named call messages.
2. Turn could expose scratchpad_tokens with explicit visibility accounting.
   Current hardware.runner metadata supplies counts/already-hidden indices.
3. An optional ClockMapping capability and injected clock could be documented
   cross-lane. No Episode observation capability is requested now that the mock
   uses an independent source.

## OPEN ISSUES

- The selected VM remains pending/offline with no process executor. Connected GitHub/CI is the execution fallback; tests remain in flight.
- Scratchpad baseline ruling below remains lead-owned. Evaluation builders must exclude tamper.hide_scratchpad.noop as an ineffective manipulation.
- New planned identities apply to this runner's matrix output. Pre-fix output directories without planned-cell metadata need separate migration/review before mixing revisions; no live hardware corpus exists in this seat.
- PR #533 remains a draft; independent final-head review, integration/live gates and merge belong to the lead. No hardware validation or scientific claim is made.

## NEEDS_RULING

RUN-R1-05: Should an untampered record count scratchpad tokens as hidden, as now
and as records.Turn describes, or as visible so hide_scratchpad moves them?
Recommendation: keep the shared contract's hidden baseline unless the lead
prospectively changes the analysis convention. The interim noop flag lets
evaluation builders exclude unchanged rows.

The six requested hidden/visible baseline readings will be inserted after the independent world runs.

## FIX LOG

- RUN-R1-01 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — validate every endpoint call bracket, with ahead/behind regressions.
- RUN-R1-02 fixed 0ddf49ae00690d3bab7ffc1777e9b34c8b39f371 — strip separated reasoning from endpoint history; retain archival/full-view spans and record policy.
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
