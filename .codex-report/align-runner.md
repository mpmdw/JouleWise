# Alignment runner lane

## SUMMARY

- Completed the protocol-driven agent loop, factory registry, resumable randomized matrices and run/tamper CLI.
- Retained endpoint, tool, scoring, monitor, sampler and interrupt outcomes as flags.
- Preserved measured work through pure turn/tool/scratchpad tamper transforms.
- Added the configurable inbox agent and timing/token-driven synthetic GPU sensor.
- Fixed the matrix factory-loop parse error and setup-interruption handling.
- Executed all 42 align tests in CI: 38 lane tests plus 4 records tests, zero failures or skips.
- The 20-episode matrix produced 250 turns, 230 calls, 291200 prefill tokens, 43120 decode tokens and 1840 hidden tokens; energy checks and byte-identical recovery passed.
- Whole-repository CI remains red on an unchanged courier timing assertion outside this lane; the draft PR and exact limitation are recorded below.
- Protected contracts are unchanged; the only registry exception is the align prefix in tests/test_shard_tests.py. No hardware was used.

## FILES

- joulewise/align/runner.py: episode lifecycle, transcript views, identities, factories, randomized matrix, durable JSONL and recovery.
- joulewise/align/tamper.py: pure marking transforms and seeded evaluation-set selection.
- joulewise/align/mock_world.py: virtual clock, inbox task/tools, scripted endpoint, tokenizer/monitor and synthetic power model/sensor.
- joulewise/align/__main__.py: run and tamper CLI.
- tests/align/test_runner.py: 13 executed lifecycle, timing, token, visibility, mapping and failure tests; shared world constructor.
- tests/align/test_runner_matrix.py: 9 executed matrix, recovery, interruption and CLI tests; stderr end-to-end evidence.
- tests/align/test_mock_world.py: 9 executed world/sensor tests, including independent energy arithmetic and text blindness.
- tests/align/test_tamper.py: 7 executed production-episode transform tests.
- docs/align/runner.md: matrix format, factories, transcript encoding, recovery, tampering and synthetic assumptions/checks.
- .codex-report/align-runner.md: this report.
- Registry exception: tests/test_shard_tests.py adds only "align." to its module-prefix normalization. CI run 39710432431, quick job 119600881005, identified the exact tests.align.* versus align.* census mismatch. No timing weights, scheduler logic or other registries changed.
- docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py remain unchanged.

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

Executed code/test revision: 9e7f5231b1522e2d27622b9bc20e255ebd2e315e.
Executor: GitHub Actions, Python 3.13.16, draft [PR #533](https://github.com/mpmdw/JouleWise/pull/533)
into lane/2026-10-21-align-spine. The selected VM never exposed a usable
executor; repeated pwd attempts, including the final check, failed before a
process could start. No local Python, pip-extra, or hardware execution is claimed.

[CI run 39711261800](https://github.com/mpmdw/JouleWise/actions/runs/39711261800)
completed with overall conclusion failure. Every align module passed:

| Module | Tests | Failures | Errors | Skips | Job |
| --- | ---: | ---: | ---: | ---: | --- |
| tests.align.test_runner | 13 | 0 | 0 | 0 | test (3.13, 5), 119605144392 |
| tests.align.test_runner_matrix | 9 | 0 | 0 | 0 | test (3.13, 4), 119605144527 |
| tests.align.test_mock_world | 9 | 0 | 0 | 0 | test (3.13, 9), 119605144430 |
| tests.align.test_tamper | 7 | 0 | 0 | 0 | test (3.13, 3), 119605144409 |
| tests.align.test_records | 4 | 0 | 0 | 0 | test (3.13, 8), 119605144402 |
| Total | 42 | 0 | 0 | 0 | 38 lane + 4 spine |

No new test requires an extra, and no extra was installed from this seat.
There is no separate extra-dependent lane run to report. Repository optional
dependency skips are listed below.

Exact prerequisite commands included:

```sh
python3 scripts/quick_suite.py --tier quick --workers 4
python -m compileall -q joulewise tests
python -m unittest -v tests.test_calibration_exits
```

The quick tier passed 212 modules, excluded 179 by its configured selection,
and reported zero failed modules. Build, installed-wheel and fences passed.
Calibration-exits passed 48 tests with zero skips. Both writer-crash exclusive
units passed (1 and 19 tests, zero skips).

The ordinary shards used SHARD_COUNT=12 and SHARD_INDEX=1 through 12, with
this exact unchanged inline command from .github/workflows/ci.yml:

```sh
python - <<'PY'
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, "scripts")
import shard_tests

overlay = json.loads(Path("scripts/test_timings.json").read_text())
exclusive = frozenset(overlay["exclusive_modules"])
discovered = shard_tests.discover_test_modules()
assert exclusive <= set(discovered), (exclusive, discovered)
timings = shard_tests.load_timing_map()
ordinary = tuple(module for module in discovered if module not in exclusive)

# UNIT-atomic, not module-atomic. Modules in split_modules (today
# test_reduce and test_controller_g2b_attachment, each audited for
# per-test independence) are spread across shards at test
# granularity, so no single module floors the shard time. This edits no test file and
# skips nothing: expand_units emits one unit per declared heavy
# test plus ONE remainder unit holding every other test in that
# module, and verify_split_declaration fails the build closed if
# a declared id no longer exists.
splits = {
    module: declaration
    for module, declaration in shard_tests.load_split_declarations().items()
    if module in set(ordinary)
}
unknown = shard_tests.conservative_unknown_weight()
units, weights = shard_tests.expand_units(
    ordinary, timings, splits, unknown_weight=unknown
)
count = int(os.environ["SHARD_COUNT"])
partitions = shard_tests.partition_modules(
    units, weights, count, unknown_weight=unknown
)
totals = shard_tests.partition_totals(
    partitions, weights, unknown_weight=unknown
)
print("ORDINARY SHARD ESTIMATES", ",".join(f"{value:.3f}" for value in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], count, index))
PY
```

Completed shard tails (a printed PASS tail can still have a cancelled job
when fail-fast reaches its cleanup):

| Job | Tests | Failures | Errors | Skips | Job conclusion |
| --- | ---: | ---: | ---: | ---: | --- |
| [calibration-writer-crash-matrix-exclusive (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144340) | 1 | 0 | 0 | 0 | success |
| [test (3.13, 6)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144382) | 596 | 0 | 0 | 9 | success |
| [test (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144390) | 479 | 0 | 0 | 11 | success |
| [test (3.13, 5)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144392) | 918 | 0 | 0 | 10 | success |
| [test (3.13, 1)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144397) | 600 | 0 | 0 | 3 | success |
| [test (3.13, 8)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144402) | 819 | 0 | 0 | 13 | success |
| [test (3.13, 3)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144409) | 764 | 0 | 0 | 5 | success |
| [test (3.13, 9)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144430) | 916 | 0 | 0 | 9 | success |
| [calibration-writer-crash-matrix-exclusive (3.13, 2)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144450) | 19 | 0 | 0 | 0 | success |
| [test (3.13, 11)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144481) | 828 | 0 | 0 | 5 | success |
| [test (3.13, 4)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144527) | 839 | 1 | 0 | 9 | failure |
| [test (3.13, 12)](https://github.com/mpmdw/JouleWise/actions/runs/39711261800/job/119605144555) | 917 | 0 | 0 | 5 | cancelled |

Shards 7 and 10 were cancelled without final shard summaries. Their partial
logs are retained by the run; no whole-suite test count or whole-suite pass is
claimed. Shard 12 printed a complete PASS tail but its job was cancelled.

The overall failure is tests.test_v5_s1_qualification.QualificationSubsetTests.
test_delivered_courier_journal_assembles_with_observed_exit_and_timeout,
subtest still_running=True. Its unchanged helper at tests/test_run_night.py:6572
asserted elapsed < 5 seconds; observed elapsed was 30.206560553999907 seconds.
The call is at tests/test_v5_s1_qualification.py:132. This is outside WRITE_SCOPE,
is not a registry failure, and was left unchanged. All nine matrix tests had
already passed in that same shard.

Earlier [run 39710432431](https://github.com/mpmdw/JouleWise/actions/runs/39710432431)
passed build, installed-wheel and fences, then failed its quick census test:
4 tests, 1 failure, 0 errors/skips in tests.test_shard_tests. Its quick summary
was 212 modules with 1 failed module. The allowed prefix addition fixed it;
the next run's quick tier passed. Dependent align shards did not execute in
that first run.

The direct local commands below remain unexecuted because no VM process
could start; their align modules were instead executed by the CI command above:

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests
python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5
```

<details>
<summary>Repository skip reasons observed in the CI job logs</summary>

The lane's 42 tests skipped none. The following are the exact distinct reasons
printed by repository tests, including partial cancelled jobs. Counts refer to
printed skip lines (136 lines), not a claimed complete suite total.

- 1 printed skip line(s): 'a desk run of the real read-only probes (macOS)'
- 1 printed skip line(s): 'ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus'
- 1 printed skip line(s): 'ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus'
- 10 printed skip line(s): 'block-3 b3w1 archive is local to the measurement Mac'
- 1 printed skip line(s): 'clonefile(2) is an APFS call'
- 1 printed skip line(s): 'CommonCrypto is macOS only'
- 1 printed skip line(s): 'controlled runs corpus unavailable'
- 1 printed skip line(s): 'Darwin pgrep ancestor exclusion; Linux pgrep has no such rule'
- 1 printed skip line(s): 'design/2026-10-05-v5-claim-block-draft is not in this clone'
- 6 printed skip line(s): 'FLAG joulewise/arm_readiness.py:7621: committed GAMMA lacks freeze authority; writer/ARM cannot continue. No nonphysical semantic shortcut is allowed.'
- 5 printed skip line(s): 'full scored corpus (set JOULEWISE_FULL_CORPUS=1)'
- 1 printed skip line(s): 'full-fixture proof runs in d117-production-proof'
- 1 printed skip line(s): 'gate-prune inventory is not on this machine'
- 1 printed skip line(s): 'jsonschema not installed (optional)'
- 2 printed skip line(s): 'jsonschema not installed'
- 1 printed skip line(s): 'kern.bootsessionuuid is a Darwin kernel value'
- 1 printed skip line(s): 'kern.bootsessionuuid is Darwin-only'
- 1 printed skip line(s): 'lead-reviewed D-079 import custody inputs are unavailable'
- 2 printed skip line(s): 'lead-reviewed D-079 import inputs are unavailable'
- 1 printed skip line(s): 'live identity probes need macOS sysctl'
- 2 printed skip line(s): 'local Qwen3 tokenizer mirrors are absent'
- 2 printed skip line(s): 'lsof is not installed'
- 2 printed skip line(s): 'markdown-it-py not installed; the build cannot run here'
- 9 printed skip line(s): 'matplotlib ([analysis] extra) not installed'
- 1 printed skip line(s): 'measurement ledger not on this machine'
- 2 printed skip line(s): 'native QoS requires macOS'
- 2 printed skip line(s): 'optional jsonschema dependency is absent'
- 1 printed skip line(s): 'pinned MATH source absent'
- 1 printed skip line(s): 'POWER-Z KM003C not on the USB bus'
- 1 printed skip line(s): 'reads the macOS kernel clock'
- 2 printed skip line(s): 'reads the real gauge (macOS)'
- 1 printed skip line(s): 'reads the real host CPU ticks (macOS)'
- 1 printed skip line(s): 'reads the real kernel clock (macOS)'
- 2 printed skip line(s): 'reads the real notify bus (macOS)'
- 2 printed skip line(s): 'reads the real process table (macOS)'
- 2 printed skip line(s): 'reads the real SMC (macOS)'
- 1 printed skip line(s): 'real campaign-log corpus is unavailable'
- 1 printed skip line(s): 'real collect subprocess runs the macOS census and power-policy probes (pmset, sysctl); on Linux every round errors and, since fix round 4, an all-error session exits 1 by design'
- 1 printed skip line(s): 'real launchctl required'
- 1 printed skip line(s): 'real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json'
- 2 printed skip line(s): 'real runs corpus unavailable'
- 1 printed skip line(s): 'real spawned worker uses native QoS; hosted Linux shards feed the runner via stdin, which spawn cannot re-import'
- 1 printed skip line(s): 'requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in'
- 18 printed skip line(s): 'requires Darwin fchflags/st_flags'
- 1 printed skip line(s): 'retained capture 20260722T145535-e941c821 is not on this machine; run scripts/check_paper_replay_fence.py where the corpus lives'
- 1 printed skip line(s): 'retained runs corpus is absent'
- 1 printed skip line(s): 'retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live'
- 1 printed skip line(s): 'runs_window corpus absent (clean checkout without bundles)'
- 1 printed skip line(s): 'runs/ corpus absent (clean checkout without bundles)'
- 2 printed skip line(s): 'source corpus unavailable: /Users/edr/code/JouleWise/runs_window_a5_20260723'
- 1 printed skip line(s): 'split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION'
- 1 printed skip line(s): 'stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED'
- 1 printed skip line(s): 'STRUCTURAL-BLOCKED: generator targets uninstalled _v2 family while the registry installs _v5'
- 1 printed skip line(s): 'STRUCTURAL-BLOCKED: synthetic _v5 fixture omits the family-publication marker required before self-predecessor validation'
- 1 printed skip line(s): 'successor member not minted yet; shape check is vacuous'
- 1 printed skip line(s): 'temporary filesystem is case-sensitive'
- 3 printed skip line(s): 'the 2026-09-22 harvest archives are not on this machine'
- 1 printed skip line(s): 'the block-5 design branch is not in this clone'
- 1 printed skip line(s): 'the gate-prune inventory is not on this machine'
- 1 printed skip line(s): 'the real kern.bootsessionuuid exists only on macOS'
- 1 printed skip line(s): 'the two pilot-night archives are not on this machine'
- 1 printed skip line(s): 'this file system gave the replacement lock the inode number of the lock just unlinked (4522132); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers)'
- 3 printed skip line(s): 'U2 successor engine pending'
- 1 printed skip line(s): 'window-B quarantine custody path is absent'
- 3 printed skip line(s): "local model mirrors absent (CI environment): ['qwen25_0p5b', 'qwen25_1p5b', 'qwen25_7b']"
- 1 printed skip line(s): "local model mirrors absent (CI environment): ['qwen3-1p7b', 'qwen3-8b']"
- 1 printed skip line(s): "NEEDS-RULING: config-authenticated mock telemetry is excluded by the production claim loader, so the existing canned fixture cannot satisfy D-158's DATA-only predicate without loosening a production gate or building a new corpus fixture"
- 1 printed skip line(s): "requires Darwin's POSIX extended regular expressions"
- 1 printed skip line(s): "requires Darwin's real boot-session sysctl command"
- 1 printed skip line(s): "requires Darwin's real caffeinate process"
- 2 printed skip line(s): "requires Darwin's real pgrep command semantics"
- 1 printed skip line(s): "requires Darwin's real sysctl command"
- 1 printed skip line(s): "successor mirrors are still absent/incomplete: ['qwen3-1p7b', 'qwen3-8b']"

</details>

## END-TO-END

Executed test_twenty_worlds_tamper_and_jsonl_round_trips in job 119605144527:
2 task pairs x 2 conditions x 5 seeds through run_matrix -> run_episode ->
task tools -> three monitor views -> SyntheticPowerSampler -> episode and
transcript JSONL -> read_episodes. Independent token-draw reconstruction
checked every turn's cached context, prefill, decode and hidden work.

The emitted ALIGN_RUNNER_END_TO_END record reported:

- Episodes: 20; turns: 250; tool calls: 230.
- Prefill tokens: 291200; decode tokens: 43120; hidden tokens: 1840.
- Each of the ten sabotage episodes, covering both pairs and seeds 0..4,
  had exactly 184 hidden tokens at turn 6: 120 reasoning + 64 scratchpad.
  Every benign episode had zero hidden tokens.
- Sampled gross energy: 205559.04426718 J.
- Independently summed gross energy: 205559.04426718 J.
- Maximum per-episode energy disagreement: 1.8189894035458565e-12 J.
  The test uses the brief's 1e-6 relative agreement rule when no uncertainty
  exists; contiguous 100 ms averaging/sample boxes with trailing coverage
  conserve excess energy. Idle is added only over the episode interval.
- Four transformed datasets (delete turns, drop calls, hide scratchpad and
  seeded random deletion) were written and read back. Trace JSON and physical
  token/work totals stayed identical; logged counts changed as asserted.
- The matrix test's full-coverage/noiseless energy configuration is a
  conservation check. Separate executed mock-world tests exercised the default
  100 ms cadence, 25 ms averaging, 0.5 W noise and 0.1 W quantum, idle tool waits,
  cached-context energy, hidden decode work and blindness to changed text.

Executed test_simulated_kills_reproduce_both_files tested four kill boundaries:
before episode append, after episode append, partial episode line and partial
transcript line. Every resumed 20-episode episode/transcript file matched the
uninterrupted file byte for byte. Recovery flags/quarantined bytes were checked.
Executed CLI tests launched the real run and tamper module commands. Setup
interrupt and endpoint interrupt tests retained records and stopped scheduling.

These are synthetic results. No rented GPU, real benchmark, power instrument,
model download, paid API or live hardware result is claimed.

## DECISIONS I MADE

- Resumed the pushed runner branch at a5a25d7a5f69ea749e1012aff3fd1011f2c3a798.
  Read its report and the three protected governing files before writes.
- The bounded user brief selects this lane; the repository intake has no active
  stop card. Delegated WRITE_SCOPE takes precedence over generic bookkeeping.
- Used the explicitly authorized GitHub connector/CI fallback while the VM
  remained unusable. All commits target only lane/2026-10-21-align-runner.
  No force push, main push, other-branch push or merge occurred.
- Fixed the malformed monitor/sampler dispatch with explicit branches.
  CI found the separate census mismatch; only its allowed name-prefix entry
  changed, after that executed failure.
- Factories receive (config, FactoryContext); trusted imports register plugins.
  Optional clock and matrix_id keywords support deterministic synthetic runs
  while ordinary protocol implementations need no other lane imports.
- Endpoint usage supplies cached context, uncached prefill and total decode.
  records.py wins: hidden work is inside decode. Invalid counts/timestamps are
  flagged and normalized only to retain valid records.
- Missing scratchpad tokenizer counts are flagged. Lane-local runner metadata
  stores known counts and accounted indices; hide_scratchpad is idempotent
  for runner-produced records and never invents missing counts.
- Named assistant call messages carry call ID/name/JSON arguments, followed
  by tool results, because ChatMessage has no tool-call array. Separate
  reasoning_text uses jw_reasoning tags. Monitor views strip private natural
  text or retain only actions/results as requested.
- Sampling brackets agent work; model Turn times exclude separately timed
  tool waits. Sampling stops before scoring and monitors. Foreign traces
  require a real matching ClockMapping and are otherwise omitted with a flag.
- IDs hash task pair, condition, endpoint identity, seed and matrix ID.
  Recorded order_seed randomizes matrix order reproducibly. Valid committed
  IDs, including flagged records, skip; deliberate retries need a new identity.
- Transcript fsync precedes episode fsync; the episode is the commit marker.
  Quarantine malformed/partial bytes and record recovery flags in run.json
  so replay preserves primary-file bytes.
- Ctrl-C during setup writes an empty interrupted record without model calls;
  a loop interrupt retains completed work. The matrix stops after saving it.
- Synthetic coefficients, workload sizes, sensor cadence, noise and quantum
  are configurable assumptions. Tool waits draw idle power. The full-coverage
  energy test and default duty-shaped sensor test exercise separate stated
  configurations through the real runner.
- Kept the PR draft and reported the unchanged out-of-scope timing failure.
  No independent review, cold final pass, main integration or merge approval
  is asserted by this lane.
- The final report-only commit uses [skip ci]: no code/test byte changes follow
  the executed revision. This avoids repeating the whole suite for evidence
  prose. The failed repository run and pending lead gates remain explicit.

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

- Whole-repository CI is not green: the unchanged courier fixture failure
  above triggered fail-fast cancellations. A repair would require authority
  over tests/test_run_night.py (the elapsed-time assertion) and possibly its
  caller tests/test_v5_s1_qualification.py, neither in this lane's scope.
  No such repair was attempted or hidden.
- The managed VM remained unusable. Direct local discovery, canonical-suite
  and touched-tier commands are unexecuted; executed CI evidence is above.
- Draft PR #533 retains pending lead-owned review, integration and merge gates;
  gate-ledger therefore remains red. No merge is requested or performed here.
- Real endpoint adapters must honor the documented local tool-message encoding.
  InboxTask turns and ScriptConfig turns must agree when configured.
  Cross-lane/live hardware validation remains for the lead's authorized run.

## NEEDS_RULING

none for the completed runner lane.
