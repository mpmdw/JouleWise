# SUMMARY
- Continued the existing lane from ecdf1eb3845bb04dd189b74aea0828c3722e34bf; protected contracts and twin files are unchanged.
- R2-B1: the CLI analyses every readable JSONL episode, flagging malformed JSON, records and UTF-8 by physical line.
- R2-m3: each routing statistic excludes flagged single-condition groups after its own capture drops.
- R2-m1: independent twin files execute in a temporary package; absent git/ref gives a reasoned skip.
- R2-m2: calibration stays in ordinary CI, scheduled with the supplied single hosted 1451.183-second observation.
- R2-n1: all six reviewer seeds use the hypergeometric five-SE reuse bar, approximately 2.62e-4.
- Literal E2/E5 repros pass; all six E4 values clear the derived bar; all eight offline tiny-HF tests pass.
- CI: 9,931 tests, 9,777 passed, 153 skipped, one independent-twin Stage A disagreement under the new cohort rule.

# FILES
Changed in round 2:
- joulewise/align/moe/stage_a.py: binary per-line JSONL recovery, input flags and post-drop exchangeable cohorts.
- tests/align/test_moe_stage_a.py: topic-world CLI corruption and invalid-UTF-8 checks; real JSONL log-lifetime regression.
- tests/align/test_moe_review.py: temporary twin package, skip/preservation regressions and six-seed derived sampling bar.
- tests/align/test_moe_review2.py: appendix world_r2/E2/E5 ports, unequal contrasting groups and timing-map repro.
- docs/align/moe_stage_a.md: CLI recovery semantics and metric-specific no-contrast group exclusion.
- scripts/test_timings.json: specifically granted R2-m2 exception; one weight and one provenance note only.
- .codex-report/align-moe.md: current report and round-2 fix log.

Unchanged implementation inherited from prior rounds:
- joulewise/align/moe/hooks.py: lazy HF capture for Qwen3-MoE, Qwen2-MoE and Mixtral; uncached-forward flags.
- joulewise/align/moe/stats.py: routing metrics, validation and grouped exact/Monte Carlo permutation API.
- joulewise/align/moe/synthetic.py: configurable topic-affinity episodes.
- joulewise/align/moe/__init__.py: shared RouterLog and metric exports.
- tests/align/test_moe_stats.py: metric oracles and validation-count checks.
- tests/align/test_moe_hooks.py: eight optional tiny real-model integrations.
- tests/align/test_moe_calibration.py: four 120-world gain calibrations and the round-1 reviewer generator.
- REGISTRY EXCEPTION inherited from r0: tests/test_shard_tests.py, unchanged in round 2. No additional registry exception.
- Protected docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py have no changes. No independent twin source was copied into or edited in the checkout; only the explicitly requested untracked local-edit sentinel was created and removed for its repro.

# PUBLIC API
- RouterRecorder(model); .log -> RouterLog; .to_log() -> RouterLog; .reset() -> None; .phase(phase: str) -> context manager; .close() -> None; .flags: list[str].
- usage_entropy(log: RouterLog, *, phase: str | None = None, per_layer: bool = False) -> float | list[float]
- load_imbalance(log: RouterLog, *, phase: str | None = None) -> float
- reuse_fraction(log: RouterLog, *, phase: str | None = None) -> float
- mean_reuse_distance(log: RouterLog, *, phase: str | None = None) -> float
- episode_stats(log: RouterLog) -> dict[str, float]
- grouped_permutation_test(values: Sequence[float], labels: Sequence[int], groups: Sequence[str], *, n_perm: int | None = None, seed: int = 0) -> tuple[float, float, int]
- routing_flags(log: RouterLog) -> tuple[str, ...]
- analyze_stage_a(episodes: Iterable[Episode], *, n_bootstrap: int, confidence: float = 0.95, n_perm: int | None = None, seed: int = 0) -> StageAResult
- iter_episodes(path: Path, *, flags: list[str] | None = None) -> Iterator[Episode]: optional diagnostic sink; opening OSError propagates without a sink, otherwise records a flagged empty stream.
- mann_whitney_auc(scores: Sequence[float], labels: Sequence[int]) -> float
- StageAResult includes episode-aligned features/predictions, per-statistic flags, twelve-test Holm, refitted auc_gain_interval, descriptive auc_gain_fixed_prediction_interval, method and valid-refit count.
- TopicWorld(groups: int = 12, repeats: int = 1, num_experts: int = 32, top_k: int = 4, layers: int = 4, turns: int = 6, prefill_tokens: int = 128, decode_tokens: int = 192, prefill_ns_per_token: int = 500_000, decode_ns_per_token: int = 20_000_000, tool_ns: int = 200_000_000)
- expected_topic_statistics(num_experts: int, top_k: int, fraction: float) -> dict[str, float]
- topic_episodes(side_fraction: float, *, design: TopicWorld | None = None, seed: int = 0, independent_noise: bool = False) -> tuple[Episode, ...]
- main(argv: Sequence[str] | None = None) -> int
- python3 -m joulewise.align.moe.stage_a EPISODES.jsonl --n-bootstrap N [--confidence C] [--n-perm N] [--seed S]

# TESTS RUN
Verified code/test revision: 73fce27cfd9d1471779a04405dbfff6e54ed1992,
tested in [CI run 39732091272](https://github.com/mpmdw/JouleWise/actions/runs/39732091272)
through PR merge e14a26abc53070caec74c8e76257efe67cb8caef.
Full test census: 9,931 run, 9,777 passed, 153 skipped, one failure, zero errors.
The failure is the independent twin's outdated Stage A cohort reference (OPEN
ISSUES); it is not hidden or marked expectedFailure. The final report commit changes only this report; no code/test changes follow
this tested revision.

| Alignment module | Tests | Passed | Skipped | Failed |
| --- | ---: | ---: | ---: | ---: |
| tests.align.test_moe_stats | 11 | 11 | 0 | 0 |
| tests.align.test_moe_stage_a | 20 | 20 | 0 | 0 |
| tests.align.test_moe_hooks | 8 | 0 | 8 | 0 |
| tests.align.test_moe_calibration | 4 | 4 | 0 | 0 |
| tests.align.test_moe_review | 6 | 5 | 0 | 1 |
| tests.align.test_moe_review2 | 8 | 8 | 0 | 0 |
| tests.align.test_records | 4 | 4 | 0 | 0 |
| Total | 61 | 52 | 8 | 1 |

Nested independent run: 35 tests, 34 passed, 1 failed, zero skips. These are not
double-counted in the parent census. The eight hooks skip in stdlib CI with
"tiny HF MoE integration needs optional torch and transformers"; all eight then
passed in the isolated extra-dependency run below.

| Ordinary shard | Tests | Skips | Failures / errors | Job ID |
| --- | ---: | ---: | ---: | ---: |
| 1 | 4 | 0 | 0 / 0 | 119671005044 |
| 2 | 706 | 15 | 0 / 0 | 119671005080 |
| 3 | 842 | 10 | 0 / 0 | 119671005038 |
| 4 | 814 | 29 | 0 / 0 | 119671005067 |
| 5 | 820 | 12 | 0 / 0 | 119671005073 |
| 6 | 907 | 3 | 0 / 0 | 119671005019 |
| 7 | 954 | 9 | 0 / 0 | 119671005125 |
| 8 | 664 | 35 | 0 / 0 | 119671005040 |
| 9 | 1238 | 16 | 0 / 0 | 119671005088 |
| 10 | 1079 | 9 | 0 / 0 | 119671005134 |
| 11 | 1051 | 8 | 1 / 0 | 119671005057 |
| 12 | 784 | 7 | 0 / 0 | 119671005197 |

Exclusive jobs: tests.test_calibration_exits (119671004836), 48 passed;
crash matrix job 119671004892, 1 passed, and 119671004940, 19 passed.
Quick tier: 212 modules passed, 181 excluded by existing policy, zero failures.
Build, installed-wheel, fences and compile checks passed.
Shard 2 emitted its complete PASS summary (706 tests, 15 skips) before fail-fast
cancelled its cleanup; its job conclusion is cancelled, not success.

Current CI skip-reason census (153, extracted from the logs):
- 1: a desk run of the real read-only probes (macOS)
- 1: ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus
- 1: ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus
- 10: block-3 b3w1 archive is local to the measurement Mac
- 1: clonefile(2) is an APFS call
- 1: CommonCrypto is macOS only
- 1: controlled runs corpus unavailable
- 1: Darwin pgrep ancestor exclusion; Linux pgrep has no such rule
- 1: design/2026-10-05-v5-claim-block-draft is not in this clone
- 6: FLAG joulewise/arm_readiness.py:7621: committed GAMMA lacks freeze authority; writer/ARM cannot continue. No nonphysical semantic shortcut is allowed.
- 13: full scored corpus (set JOULEWISE_FULL_CORPUS=1)
- 1: full-fixture proof runs in d117-production-proof
- 1: gate-prune inventory is not on this machine
- 2: jsonschema not installed
- 1: jsonschema not installed (optional)
- 1: kern.bootsessionuuid is a Darwin kernel value
- 1: kern.bootsessionuuid is Darwin-only
- 1: lead-reviewed D-079 import custody inputs are unavailable
- 2: lead-reviewed D-079 import inputs are unavailable
- 1: live identity probes need macOS sysctl
- 3: local model mirrors absent (CI environment): ['qwen25_0p5b', 'qwen25_1p5b', 'qwen25_7b']
- 1: local model mirrors absent (CI environment): ['qwen3-1p7b', 'qwen3-8b']
- 2: local Qwen3 tokenizer mirrors are absent
- 2: lsof is not installed
- 2: markdown-it-py not installed; the build cannot run here
- 9: matplotlib ([analysis] extra) not installed
- 1: measurement ledger not on this machine
- 2: native QoS requires macOS
- 1: NEEDS-RULING: config-authenticated mock telemetry is excluded by the production claim loader, so the existing canned fixture cannot satisfy D-158's DATA-only predicate without loosening a production gate or building a new corpus fixture
- 2: optional jsonschema dependency is absent
- 1: pinned MATH source absent
- 1: POWER-Z KM003C not on the USB bus
- 1: reads the macOS kernel clock
- 2: reads the real gauge (macOS)
- 1: reads the real host CPU ticks (macOS)
- 1: reads the real kernel clock (macOS)
- 2: reads the real notify bus (macOS)
- 2: reads the real process table (macOS)
- 2: reads the real SMC (macOS)
- 1: real campaign-log corpus is unavailable
- 1: real collect subprocess runs the macOS census and power-policy probes (pmset, sysctl); on Linux every round errors and, since fix round 4, an all-error session exits 1 by design
- 1: real launchctl required
- 1: real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json
- 2: real runs corpus unavailable
- 1: real spawned worker uses native QoS; hosted Linux shards feed the runner via stdin, which spawn cannot re-import
- 1: requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in
- 18: requires Darwin fchflags/st_flags
- 1: requires Darwin's POSIX extended regular expressions
- 1: requires Darwin's real boot-session sysctl command
- 1: requires Darwin's real caffeinate process
- 2: requires Darwin's real pgrep command semantics
- 1: requires Darwin's real sysctl command
- 1: retained capture 20260722T145535-e941c821 is not on this machine; run scripts/check_paper_replay_fence.py where the corpus lives
- 1: retained runs corpus is absent
- 1: retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live
- 1: runs_window corpus absent (clean checkout without bundles)
- 1: runs/ corpus absent (clean checkout without bundles)
- 2: source corpus unavailable: /Users/edr/code/JouleWise/runs_window_a5_20260723
- 1: split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION
- 1: stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED
- 1: STRUCTURAL-BLOCKED: generator targets uninstalled _v2 family while the registry installs _v5
- 1: STRUCTURAL-BLOCKED: synthetic _v5 fixture omits the family-publication marker required before self-predecessor validation
- 1: successor member not minted yet; shape check is vacuous
- 1: successor mirrors are still absent/incomplete: ['qwen3-1p7b', 'qwen3-8b']
- 1: temporary filesystem is case-sensitive
- 3: the 2026-09-22 harvest archives are not on this machine
- 1: the block-3 reference archive and the measurement interpreter are on Ed's Mac only
- 1: the block-5 design branch is not in this clone
- 1: the gate-prune inventory is not on this machine
- 1: the real kern.bootsessionuuid exists only on macOS
- 1: the two pilot-night archives are not on this machine
- 1: this file system gave the replacement lock the inode number of the lock just unlinked (8954233); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers)
- 8: tiny HF MoE integration needs optional torch and transformers
- 3: U2 successor engine pending
- 1: window-B quarantine custody path is absent


The VM became usable late in the task, after the implementation and CI ports were
pushed. Earlier pwd probes failed with "No usable execution environment is
available"; subsequent local checkout/fetch and all round-2 repros ran.
Local default Python is 3.12.14; /usr/bin/python3.13 is 3.13.5. CI uses 3.13.16.
The full repository suite was verified through the existing CI shard harness
below; the serial root-discovery command was not repeated after that coverage.

Local commands and results:
- `git fetch origin +refs/heads/lane/2026-10-21-align-moe:refs/remotes/origin/lane/2026-10-21-align-moe`; `git checkout -B lane/2026-10-21-align-moe origin/lane/2026-10-21-align-moe`: exact pushed head 73fce27cfd9d1471779a04405dbfff6e54ed1992.
- `python3 -m unittest discover -s tests/align -t .`: 61 tests in 1173.030s: 52 passed, 8 skipped (optional torch/transformers absent), 1 failure (the same unmodified twin cohort disagreement), zero errors.
- `python3 -m unittest tests.test_shard_split tests.test_shard_tests tests.test_quick_suite -v`: 52 passed, zero skips; 6.752s.
- `rg -l test_timings tests scripts`: scripts/shard_tests.py, tests/test_shard_split.py and the new tests/align/test_moe_review2.py. The loader tests above passed too.
- `python3 /workspace/JouleWise/.review2/e2_edges.py /workspace/JouleWise`: FAILS 0.
- `python3 /workspace/JouleWise/.review2/e5_drop_confound.py /workspace/JouleWise`: shift 0.00 interval half-widths at f=0 and f=.05.
- `python3 /workspace/JouleWise/.review2/e4_rounding_bar.py /workspace/JouleWise 1 2 3 4 5 6`: all six values inside the corrected five-SE bar. Its unchanged labels still describe the obsolete rounding rule and print FAILS for seeds 5 and 6; these are not failures of the new assertion.
- All three literal commands also ran with `/usr/bin/python3.13` replacing `python3`, with the same outputs. All four appendix files were written verbatim under untracked .review2/, never committed.
- The exact truncation repro used `PYTHONPATH=/workspace/JouleWise python3 -P -c` with write_episodes/topic_episodes(.4, seed=731) and text[:-5000], followed by `PYTHONPATH=/workspace/JouleWise python3 -P -m joulewise.align.moe.stage_a /tmp/joulewise-moe-cli.jsonl --n-bootstrap 32`. It printed all 23 intact IDs, 12 finite p-values and episode_input_line_unreadable:24:JSONDecodeError.
- `python3 -m unittest tests.align.test_moe_review.ReviewerWorldTests.test_independent_twin_from_local_review_ref -v` after fetching the public twin ref: nested 35 tests, 34 passed / 1 disagreement; outer test correctly failed. The temporary local-edit sentinel still printed "# local edit", was removed afterwards, and git status showed no tests/align/ path.
- `git update-ref -d refs/remotes/origin/lane/2026-10-21-align-moe-twin`, then that same unittest command: 1 skipped, reason "independent MoE twin local ref unavailable: origin/lane/2026-10-21-align-moe-twin". The ref was re-fetched afterwards. The no-git unit regression also passed.
- `git diff --check`: passed. Timing-map repro printed 26.98 and [('tests.align.test_moe_calibration', 1451.183)].

Optional dependency run, isolated from the stdlib interpreter:
`python3 -m venv /tmp/joulewise-moe-hf`;
`/tmp/joulewise-moe-hf/bin/python -m pip install torch --index-url https://download.pytorch.org/whl/cpu`;
`/tmp/joulewise-moe-hf/bin/python -m pip install transformers`.
Installed torch 2.14.1+cpu and transformers 5.20.2.
`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 /tmp/joulewise-moe-hf/bin/python -m unittest tests.align.test_moe_hooks -v`:
8 passed, zero skips, 2.921s. Tests use local random configs with no model/tokenizer
downloads. The ordinary interpreter and CI still have neither extra installed.

Reviewer repro mapping:
- CLI one-liner / R2-B1: test_moe_stage_a.StageAWorldTests.test_jsonl_cli_skips_only_unreadable_physical_lines; actual topic_episodes -> shared JSONL -> CLI, including a truncated line, invalid expert on line 4 and invalid UTF-8 on physical line 5.
- e2_edges.py and world_r2.py: test_moe_review2.ReviewerEdgeTests covers all eleven sections with the same world parameters and seed.
- e5_drop_confound.py: test_moe_review2.DroppedGroupTests.test_e5_drop_excludes_task_baseline_and_preserves_full_world uses both exact reviewer worlds, independent pair differences, complete-data before-path checks and retained-pair permutation inputs.
- R2-m1 local-edit and missing-ref repros: test_moe_review.ReviewerWorldTests preservation/skip regressions; the actual independent twin subprocess uses the temporary package path.
- e4_rounding_bar.py: test_moe_review.CostTests.test_shade_sized_episode replays all six seeds at full 48/128/top-8 topology.
- Timing-map one-liner: test_moe_review2.TimingMapTests prints unknown weight and the exact calibration weight. Source inspection and GitHub code search identify tests.test_shard_split as the direct map reader and scripts.shard_tests as its loader; tests.test_shard_tests and tests.test_quick_suite additionally exercise that loader.
The literal scripts and these separate CI ports both ran; local execution became available late.

Exact ordinary CI command (each SHARD_INDEX=1 through 12, SHARD_COUNT=12):
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

Additional existing CI commands:
- `python3 scripts/quick_suite.py --tier quick --workers 4`
- `python -m compileall -q joulewise tests`
- `python -m unittest -v tests.test_calibration_exits`
The existing two crash-matrix jobs execute the unchanged ci.yml split-unit
harness for tests.test_calibration_writer_crash_matrix with SHARD_INDEX=1 and 2.
Independent nested command, in the temporary directory with PYTHONPATH pointing
first there and then to the checkout:
`python -m unittest tests.align.test_twin_moe tests.align.twins.test_moe_twin_selfcheck -v`.

Prior round-1 evidence remains historical: CI run 39715696032 at
19b4d84ced16aeda63e362dd570082932202d3ef passed 9,919 tests (153 skips);
alignment 41 passed / 8 optional skips; old twin revision 265e3c17 had 6 passing
agreement tests. Those counts do not describe the expanded round-2 suite.

# END-TO-END
Round-2 CI job 119671005134 (test shard 10), eight tests passed:
- E2's 24-episode world retained exactly 23 readable IDs for both corruptions, with
  episode_input_line_unreadable:24:JSONDecodeError and
  episode_input_line_unreadable:4:RecordError. All estimable tests remained finite.
  All eleven appendix sections passed their ported checks.
- E2 complete-world decode_load_imbalance stayed -0.21445586879593104 with exact
  p .00048828125 and interval [-.24261246936166464, -.1871899343527662].
  Episode-order and complete-data before-path checks passed.
- E5 (seed 31, 17 task pairs, 64 experts/top-6/eight layers, multi-turn tools)
  selected the same extreme-baseline task as the appendix. With one benign log
  removed, each effect equals the independent mean of the remaining 16 pair
  differences exactly: zero printed-interval half-width shift in both worlds.

| Side fraction | Full effect | Full p | Effect after drop | Drop interval | Exact drop p | Pair effect |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 0 | .000009245900610172268 | .9931650893796005 | .0006035963092349481 | [-.0005749379176317707, .0016760313334318014] | .384765625 | .0006035963092349481 |
| .05 | .006611013398671513 | .0005257623554153522 | .006739457325766869 | [.005680159972451751, .008021524176388836] | .000030517578125 | .006739457325766869 |

The old appendix drop effects were -.00069 and +.00559 at its printed precision,
biased by -.51 and -.41 interval half-widths. The new discrepancy from the pair
effect is 0 in both cases, inside 1% of the smallest interval half-width.
Complete-data effects, p values, arrangement counts and bootstrap intervals were
bit-identical to the pre-filter computation on identical full inputs. Unequal
groups retaining both conditions remained in the test. The E2 exact p and effect
also remained unchanged under shuffled episode order.

Timing-map repro printed weight 1451.183 and unchanged unknown fallback 26.98.

Literal E2/E5 runs on both local Python interpreters reproduce those values.
The six full-shape uniform reuse values, from CI and the literal E4 generator:

| Seed | Reuse fraction |
| --- | ---: |
| 1 | .06248898788548353 |
| 2 | .06249637889928062 |
| 3 | .06243839168365112 |
| 4 | .06245734045727855 |
| 5 | .06250510922430269 |
| 6 | .06251473242347473 |

All compare against K/E=.0625 with bar .0002620253356887465, computed from
E=128, K=8, L=48 and T=52,500. The new regression checks this bar at every seed.

Real tiny HF end to end (CPU, seed 19, random two-layer/eight-expert/top-2,
hidden-size-32 Qwen3-MoE; local character vocabulary, six generated tokens):
model.generate -> actual gate hooks -> RouterLog -> episode_stats.
The last generated token is not forwarded, so five decode rows are captured.

| Local prompt | Prefill rows | Decode rows | Both entropy | Both load CV | Both reuse | Both mean reuse distance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sort the local project files. | 29 | 5 | .9314328416479934 | .5094153868859993 | .3106060606060606 | 3.533333333333333 |
| Summarize the tool results. | 27 | 5 | .9238918443504516 | .5535237139433414 | .31451612903225806 | 3.232142857142857 |

Both logs cover layers (0,1), have no recorder flags and all twelve finite
statistics. The eight integration tests additionally validated hook transparency,
HF selected IDs, cached tool prefills, uncached forwards, padding/batch flags,
Qwen2-MoE/Mixtral and sparse layer indices. This is model execution, not hardware
power evidence.


The seed-731 topic world has 12 groups, 24 six-turn episodes, 120 tool calls,
23,176 prefill and 34,494 decode tokens, four layers, 32 experts, top-4.
The side fraction is .4. Counts match within pairs. Chain:
RouterLog -> Episode -> shared JSONL -> binary streaming decoder -> episode_stats
-> metric-specific finite and contrasting cohort -> grouped permutation
-> twelve-test Holm -> grouped effect bootstrap -> held-out routing / metadata /
combined classifiers -> AUC -> refitted grouped gain interval.
Complete-data inference inputs are unchanged by round 2. Historical reference
values are routing/combined AUC 1, metadata .5, gain .5, exact decode Holm p
.005859375, and decode reuse effect .1359071076578115 with interval
[.13118738132590682, .14117669025037116] (256 draws, seed 83). The analytic effect
is .14 = .4^2*(1-4/32). Matched zero shift has AUC .5 and gain 0; independent-noise
zero shift retains an interval containing zero. These controls remain executable.

Gain calibration reran successfully in round 2, with unchanged complete-world inputs: four 120-world null
checks (200 bootstrap draws each) produced refit false-addition rates 1/120,
0/120, 0/120 and 2/120. The prescribed lower-side bar is
.025 + 2*sqrt(.025*.975/120) = .05350438562747849 (two binomial standard errors
around one tail of a conventional two-sided 95% interval).
Raw effect percentile intervals with 12--17 groups had about .91 zero coverage,
not nominal .95; that limitation remains disclosed.

# DECISIONS I MADE
- Follow the round-2 ruling: after each metric's finite-value drops, exclude groups with no benign/sabotage contrast from effect, standardized effect, permutation and effect bootstrap. Keep every group that has both conditions, regardless of counts.
- The statistic remains pooled sabotage mean minus benign mean over that exchangeable set. The standalone public grouped_permutation_test still uses all supplied rows; its independent API contract is unchanged.
- Preserve all readable episodes in aligned metadata/routing features and classifiers; retain existing no-exchangeability flags. Holm still covers all twelve planned statistics.
- Read JSONL in binary, decode within each physical-line try block, catch ValueError there, and continue. Only an opening OSError produces a flagged empty stream; analysis exceptions are not converted into an empty dataset.
- Use an optional lane-local flags sink instead of modifying shared records. Never retain an Episode across iterator advances.
- Resolve the twin ref locally with git rev-parse --verify, skip if absent/git unavailable, copy only into TemporaryDirectory, and set subprocess package search paths explicitly. The actual round-2 twin imports no checkout test helpers, so none are copied.
- Execute both the independent agreement module and its 25 selfchecks. Never edit, adapt or weaken the twin to hide the new cohort-rule disagreement.
- Keep the four calibration tests in ordinary CI. Add only the specifically granted timing weight and its single-observation provenance; scheduling data are not research evidence.
- Derive the reuse sampling bar from the fixture E, K, L and T: sigma^2=(1/E)*((E-K)/E)*((E-K)/(E-1)); bar=5*sigma/sqrt(L*(T-1)).
- Port reviewer checks into in-scope tests while the VM is initially unavailable; after it starts, run the literal scripts on Python 3.12/3.13 and isolated offline optional-HF tests.
- Preserve round-1 refitted gain intervals, original-group holdouts, uncached-forward flags and validate-once aggregate behavior.
- Qwen3-30B-A3B topology remains verified from config revision d47d535f78ec44bd57128f8e8aeba17eeb0285ea: 48 layers, 128 experts, top-8.
- Continue the existing head through fast-forward GitHub commits while startup is pending, then fetch that same head locally; never force-push or push to main/other lanes.

# CONTRACT-CHANGE
none

# OPEN ISSUES
- Independent twin revision 3e94194a1efe77c4a1735d589ea5565dab32c919 still builds its Stage A reference cohort by finite rows alone (tests/align/test_twin_moe.py:388). This conflicts with the explicit R2-m3 ruling to remove no-contrast groups after per-statistic drops. Its public permutation API remains correct on the inputs supplied.
- Unmodified twin failure, reproduced in CI and locally:
  test_sticky_worlds_with_capture_gaps, sticky seed21 / prefill_usage_entropy:
  lane effect -.0014407076693770556; old twin-cohort effect -.001676799592271672;
  lane interval [-.005128340928333957, .0016202457628793653].
  All other 34 nested tests passed (nine agreement tests plus 25 selfchecks).
  The lane matches the settled rule and E5's independent remaining-pair sum, so
  reverting it to satisfy this older cohort reference would violate this brief.
  The independent twin owner must update that Stage A cohort selection outside
  this lane's scope. No independent twin source was edited and no failing assertion was weakened.
- CI run 39732091272 is therefore red on the outer twin test. Shard 2's job was cancelled by fail-fast during cleanup, after its complete test run printed PASS; all 9,931 test results are accounted for below.
- Raw-effect small-cluster coverage remains about .91 for 12--17 groups, as documented.
- The classifier comparison applies to this fixed learner and four count features, not every possible function of counts.
- vLLM/llama.cpp capture and Stage B are documented; compiled/fused/distributed capture and real power visibility need separate validation.
- Draft PR #520 still needs the lead's delta re-review for R2-B1/R2-m3 and integration gates. No main merge or hardware readiness is claimed.

# NEEDS_RULING
none

# FIX LOG
- B1: fixed in 6ad8e1bc76f5757c1ed1b5eb6d1e22e02f5b820e.
- M1: fixed in 210aa1336095e1307cea93123bbf5781b97db09b.
- m1: fixed in e4463cbaee04f67d8e704fdc0156ac36ae9ad7d1.
- m2: fixed in 030f99db854988532becceb3f7526c2e4aa9d2c4.
- m3: fixed in 3db851fa49c39e2a522925dc8b0690efba66fd61; addbcd7ba519ea0864757130e850262995e53d0e.

## Round 2
- R2-B1: fixed in 836b8f1c96c9ad9561b76eb1e60bd1b86020042f.
- R2-m1: fixed in f444d9aa6a9f29661343aee155936a052360a715.
- R2-m2: fixed in f444d9aa6a9f29661343aee155936a052360a715.
- R2-m3: fixed in 1b04eb67b4f4aa2080165e15027e48258ccba86f.
- R2-n1: fixed in f444d9aa6a9f29661343aee155936a052360a715; six-seed port in 73fce27cfd9d1471779a04405dbfff6e54ed1992.
