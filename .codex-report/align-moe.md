# SUMMARY
- FIX ROUND 1 IN PROGRESS: B1 and cost/capture fixes are checkpointed; calibration and verification pending.
- Implemented lazy HF Qwen3-MoE, Qwen2-MoE and Mixtral routing capture with phase tags.
- Verified Qwen3-30B-A3B config: 48 layers, 128 experts, top-8.
- Implemented all routing-statistics APIs, exact/Monte Carlo grouped tests and Holm correction.
- Added grouped-bootstrap effects and task-held-out routing/counts/combined AUC comparison.
- A 24-episode topic world gave routing AUC 1.0 versus counts AUC 0.5; null controls removed evidence.
- CI: 9,904 tests, zero failures/errors, 151 skips; alignment: 28 passed and 6 optional skips.
- Managed runtime never became usable; local commands, pip installation and extra-dependent execution remain unverified.
- All work is pushed to the MoE lane; three protected files are unchanged; one inventory exception is recorded.

# FILES
- joulewise/align/moe/__init__.py: shared RouterLog and stat exports.
- joulewise/align/moe/hooks.py: lazy model hooks, snapshots, phase override, capture flags.
- joulewise/align/moe/stats.py: entropy, load CV, reuse, distances, grouped permutation.
- joulewise/align/moe/stage_a.py: effects, intervals, Holm, held-out AUC comparison, JSONL CLI.
- joulewise/align/moe/synthetic.py: configurable token-level topic-affinity worlds.
- tests/align/test_moe_stats.py: numerical oracles and permutation controls.
- tests/align/test_moe_stage_a.py: real end-to-end shifted/null/count controls and JSONL.
- tests/align/test_moe_hooks.py: optional tiny random Qwen3/Qwen2/Mixtral integration.
- docs/align/moe_stage_a.md: topology source, capture, inference, backend paths, limitations.
- tests/test_shard_tests.py: REGISTRY EXCEPTION; add align. to namespace normalization.
- .codex-report/align-moe.md: this report.

# PUBLIC API
- RouterRecorder(model); .log -> RouterLog; .to_log() -> RouterLog; .reset() -> None;
  .phase(phase: str) -> context manager; .close() -> None; .flags: list[str].
- usage_entropy(log: RouterLog, *, phase: str | None = None, per_layer: bool = False) -> float | list[float]
- load_imbalance(log: RouterLog, *, phase: str | None = None) -> float
- reuse_fraction(log: RouterLog, *, phase: str | None = None) -> float
- mean_reuse_distance(log: RouterLog, *, phase: str | None = None) -> float
- episode_stats(log: RouterLog) -> dict[str, float]
- grouped_permutation_test(values: Sequence[float], labels: Sequence[int], groups: Sequence[str], *, n_perm: int | None = None, seed: int = 0) -> tuple[float, float, int]
- routing_flags(log: RouterLog) -> tuple[str, ...]
- analyze_stage_a(episodes: Sequence[Episode], *, n_bootstrap: int, confidence: float = 0.95,
  n_perm: int | None = None, seed: int = 0) -> StageAResult
- mann_whitney_auc(scores: Sequence[float], labels: Sequence[int]) -> float
- TopicWorld(groups: int = 12, repeats: int = 1, num_experts: int = 32, top_k: int = 4,
  layers: int = 4, turns: int = 6, prefill_tokens: int = 128, decode_tokens: int = 192,
  prefill_ns_per_token: int = 500_000, decode_ns_per_token: int = 20_000_000,
  tool_ns: int = 200_000_000)
- expected_topic_statistics(num_experts: int, top_k: int, fraction: float) -> dict[str, float]
- topic_episodes(side_fraction: float, *, design: TopicWorld | None = None, seed: int = 0,
  independent_noise: bool = False) -> tuple[Episode, ...]
- python3 -m joulewise.align.moe.stage_a EPISODES.jsonl --n-bootstrap N [--confidence C] [--n-perm N] [--seed S]

# TESTS RUN
Verified code revision: 9eaecf93f4d11a845d2febfc70d105d2108b0b90.
[CI run 39706857631](https://github.com/mpmdw/JouleWise/actions/runs/39706857631)
completed successfully: all 20 jobs passed. Python 3.13.16 on Linux, no model extras.
The final commit after this revision updates only this report and documentation;
the code/test tree is the verified revision's tree.

The complete ordinary/exclusive test matrix ran 9,904 tests: 9,753 passed,
151 skipped, zero failures and zero errors. Quick-tier repetitions are separate
from that total. The alignment subset is included in the matrix totals:

| Module | Tests | Passed | Skipped |
| --- | ---: | ---: | ---: |
| tests.align.test_moe_stats | 10 | 10 | 0 |
| tests.align.test_moe_stage_a | 14 | 14 | 0 |
| tests.align.test_moe_hooks | 6 | 0 | 6 |
| tests.align.test_records (unchanged spine) | 4 | 4 | 0 |

All six hook tests skipped with:
"tiny HF MoE integration needs optional torch and transformers".
No optional packages were installed by tests. No extra-dependency run is claimed:
the managed VM never became usable for exec_command or pip.

Exact quick command: `python3 scripts/quick_suite.py --tier quick --workers 4`.
Result: 212 modules passed, 178 excluded by the existing quick-tier policy, zero failures.
All excluded modules remained covered by ordinary/exclusive matrix jobs.

Exact compile command in ordinary jobs: `python -m compileall -q joulewise tests`: passed.

Exact ordinary test command from .github/workflows/ci.yml, executed from the
repository root with SHARD_COUNT=12 and SHARD_INDEX=1 through 12:

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

Exact calibration-exit command:
`python -m unittest -v tests.test_calibration_exits`: 48 passed, zero skips.

Exact crash-matrix command, SHARD_INDEX=1 and 2:

```sh
python - <<'PY'
import os
import sys

sys.path.insert(0, "scripts")
import shard_tests

module = "tests.test_calibration_writer_crash_matrix"
timings = shard_tests.load_timing_map()
splits = shard_tests.load_split_declarations()
unknown = shard_tests.conservative_unknown_weight()
# expand_units runs verify_split_declaration, which fails closed if
# the declared heavy test id no longer exists. That is the case a
# computed remainder would otherwise absorb in silence, handing one
# shard ~20 minutes of unaccounted work while the weights disagree.
units, weights = shard_tests.expand_units(
    (module,), timings, {module: splits[module]}, unknown_weight=unknown
)
partitions = shard_tests.partition_modules(
    units, weights, 2, unknown_weight=unknown
)
totals = shard_tests.partition_totals(
    partitions, weights, unknown_weight=unknown
)
print("CRASH-MATRIX SHARD ESTIMATES", ",".join(f"{v:.3f}" for v in totals))
index = int(os.environ["SHARD_INDEX"])
raise SystemExit(shard_tests.run_units(partitions[index - 1], 2, index))
PY
```

Per-job counts; the failure/error column is explicit:

| Job | Tests | Skips | Failures / errors | Job ID |
| --- | ---: | ---: | ---: | ---: |
| calibration-exits-exclusive (3.13) | 48 | 0 | 0 / 0 | 119589862480 |
| calibration-writer-crash-matrix-exclusive (3.13, 1) | 1 | 0 | 0 / 0 | 119589862499 |
| calibration-writer-crash-matrix-exclusive (3.13, 2) | 19 | 0 | 0 / 0 | 119589862554 |
| test (3.13, 12) | 1096 | 4 | 0 / 0 | 119589862574 |
| test (3.13, 1) | 565 | 10 | 0 / 0 | 119589862577 |
| test (3.13, 10) | 1286 | 24 | 0 / 0 | 119589862578 |
| test (3.13, 6) | 706 | 18 | 0 / 0 | 119589862579 |
| test (3.13, 4) | 785 | 9 | 0 / 0 | 119589862603 |
| test (3.13, 5) | 767 | 18 | 0 / 0 | 119589862611 |
| test (3.13, 2) | 626 | 7 | 0 / 0 | 119589862616 |
| test (3.13, 7) | 655 | 11 | 0 / 0 | 119589862627 |
| test (3.13, 8) | 804 | 11 | 0 / 0 | 119589862628 |
| test (3.13, 9) | 987 | 21 | 0 / 0 | 119589862639 |
| test (3.13, 11) | 949 | 6 | 0 / 0 | 119589862661 |
| test (3.13, 3) | 610 | 12 | 0 / 0 | 119589862700 |

Complete skip-reason census (151), copied from the final matrix logs.
These include inherited repository corpus, platform, and gate conditions:

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
- 1: this file system gave the replacement lock the inode number of the lock just unlinked (4522114); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers)
- 6: tiny HF MoE integration needs optional torch and transformers
- 3: U2 successor engine pending
- 1: window-B quarantine custody path is absent

Additional successful CI checks: build, installed-wheel smoke, state/pin/docs
fences, strict mock run/validate/reduce/revalidate. The fence's exact
`python -m unittest -v tests.test_docs_freshness` command passed 31 tests. Their repeated tests are not
added to the matrix total above.

Development failures and their dispositions:
- At b1015ffc0713f752a137532f000df8b957b7a155, quick tier had 1 failed module:
  tests.test_shard_tests, 4 tests with 1 failure. Its discovery inventory lacked
  align. namespace normalization. Applied the brief's registry exception to
  tests/test_shard_tests.py at 7f89688922d5750539cec72cb1649ae9d908a097.
- At 2a170db68740f2abe567776b93bca5a6ecf14b17, Stage A had 13/14 passes:
  the added nominal-f finite-count oracle made a deterministic check depend on
  one random draw landing inside a 95% sampling interval. Replaced that oracle
  with balanced exposure and an exact entropy/load law. The random-world data,
  estimator, thresholds and all printed world results remained identical.
- The corrected Stage A module passed 14/14 at the verified revision. Its three
  printed world summaries were bit-identical to the previous run.

Not executed locally because exec_command returned "No usable execution
environment is available"; environment status repeatedly cycled pending/starting:
```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests
python3 scripts/fixture_orphan_census.py --fail-on-orphans
```

The equivalent alignment/core tests ran through the existing CI shard runner
above. No local fixture processes or hardware measurements were started.

# END-TO-END
The main generative world used seed 731, 12 task groups and 24 episodes:
144 turns, 120 tool calls, 23,176 prefill tokens and 34,494 decode tokens.
It uses 32 experts, top-4 and four layers, with random main-topic selections and
layer-specific side-topic affinities. Sabotage switches 40% of decode tokens
in expectation; token/tool counts and prefill stay matched within pairs.

Real chain:
RouterLog -> Episode -> episode_stats -> within-task permutation ->
Holm across all 12 metrics -> whole-task bootstrap -> leave-task-out
routing/metadata/combined classifiers -> Mann-Whitney AUC and paired gain interval.
The same world also ran through shared Episode JSONL write/read and the CLI with
32 bootstrap resamples and seed 83.
Intervals below are 95%, 256 bootstrap resamples, seed 83; permutations are exact
over 4,096 arrangements.

| Result | Value | Interval |
| --- | ---: | --- |
| Metadata AUC | 0.5 | 0.5 to 0.5 |
| Routing AUC | 1.0 | 1.0 to 1.0 |
| Combined AUC | 1.0 | 1.0 to 1.0 |
| Added AUC | 0.5 | 0.5 to 0.5 |
| Decode load effect | 0.9648177222877435 | 0.9501019886896048 to 0.983076392559291 |
| Decode reuse effect | 0.1359071076578115 | 0.13118738132590682 to 0.14117669025037116 |
| Decode entropy effect | -0.1011543498323929 | -0.10440648355007826 to -0.09856993805219644 |
| Decode reuse-distance effect | -0.040791516025056485 | -0.04575411137490326 to -0.035552700316032304 |

All four decode Holm p-values are 0.005859375. The analytic expected reuse
increase is f^2(1-k/E) = .4^2(1-4/32) = .14, inside the observed interval.
Perfect separation gives degenerate bootstrap AUC intervals in this finite
control; these are conditional on its fitted folds, not real-model generalization
uncertainty. Reuse-distance first-use exclusion introduces finite-window effects.

Controls through the real analysis:
- Paired zero shift: all three AUCs 0.5, added AUC 0, all Holm p-values 1.
- Independent-noise zero shift: routing/combined AUC 0.5902777777777778,
  metadata AUC 0.5; gain 0.09027777777777779, interval
  [-0.026562499999999985, 0.26388888888888884] (128 resamples, seed 83).
  All Holm p-values 1; the gain interval includes zero.
- Counts-only positive control repeats benign decode work, updating router rows,
  token counts, context and timestamps consistently: metadata AUC 1.0.
- Balanced exposure: exact 2/5 side-topic fraction, 960 decode rows, four layers;
  entropy/load agree with the mixture law to the required 1e-6 relative bar;
  zero-shift balanced exposure has zero load CV and unit normalized entropy.
- Full verified shape: 48 layers, 128 experts, top-8, two-turn episodes with tools,
  through episode_stats with finite outputs.
- Missing router logs remain in the report; metadata analysis continues with flags.
- Tiny HF models/two prompts are implemented but skipped because dependencies
  were absent; there is no claim of observed real-model routing from this seat.

# DECISIONS I MADE
- Verified the published Qwen3-30B-A3B config at d47d535f78ec44bd57128f8e8aeba17eeb0285ea:
  48 layers, 128 experts, top-8, sparse step 1, no dense-only layer overrides.
- Discover actual HF sparse blocks by class, with their actual decoder indices.
- One sequence per RouterLog; inferred phases can be overridden for cached prefills.
- Preserve processed-forward token order; last sampled generation token can be unforwarded.
- Record capture limitations in recorder.flags, for propagation to Episode.flags.
- Phase filtering precedes adjacency/distances; RouterLog has no turn boundaries.
- Entropy/CV are averaged by layer; reuse distance pools recurrent selections.
- episode_stats keys are <phase>_<function_name>, 4 metrics x 3 phases.
- Missing/invalid routing yields NaN plus diagnostics; CLI emits JSON null and flags.
- Exact randomization uses extreme/arrangements; Monte Carlo uses (extreme+1)/(n+1).
- Monte Carlo budget >=1901 from SE(.05)<.005; smaller explicit budgets are increased.
- Exact integer sums of binary-rational inputs remove arbitrary floating tie tolerances.
- Holm family remains all twelve metrics even when a phase is missing.
- Bootstrap whole task groups, preserving within-group episodes; confidence/budget are exposed.
- Compare fixed standardized nearest-centroid classifiers on identical leave-task-out folds.
- Fit all preprocessing on training groups only; hidden decode tokens are removed from
  the visible-count baseline per Turn.hidden_tokens contract.
- Spine contains only records/interfaces/__init__, so local Mann-Whitney AUC is required.
- AUC bootstrap resamples fixed out-of-fold predictions; intervals are conditional on fits.
- Existing shared record validation remains authoritative; failed CLI file/record reads
  produce a flagged non-estimable report rather than silently dropping rows.
- Runtime startup forced GitHub API checkpoints and a draft PR to run existing CI.
- Used only the brief's registry exception for the discovery-namespace inventory fix.
- Replaced a nominal-probability confidence-coverage assertion with an exact balanced-
  exposure oracle: a single finite random topic draw need not be inside a 95% interval.
- Tiny-model generation length follows the pigeonhole bound so reuse distance is defined.
- The classifier comparison is specific to this learner/features; conditional, possibly
  degenerate control-world AUC intervals do not quantify real-model generalization.

# CONTRACT-CHANGE
none

# OPEN ISSUES
- Managed runtime never became usable. The exact local discovery commands,
  session-end live fixture census and optional pip/CPU-model run remain blocked.
  The CI evidence above is the executed stdlib verification, not a local run.
- HF hooks have source-level verification against transformers v4.57.6 and six
  optional integration tests, but no observed model execution in this seat.
- Draft PR #520 remains a build handoff. Independent twin comparison, executing
  review, current-main integration and merge gates remain lead-owned. The
  separate gate-ledger workflow intentionally has NOT-RUN review rows; no merge
  or final-head review approval is claimed.
- AUC intervals resample fixed out-of-fold scores. The comparison is specific to
  this fixed classifier and four metadata features; it does not establish
  independence from every possible function of counts.
- Compiled/fused/distributed HF capture needs separate coverage validation.
  vLLM and llama.cpp export paths are documented, as requested, rather than built.
- Host synchronization from hooks must not be interpreted as Stage B power evidence.

# NEEDS_RULING
none

# FIX LOG
- B1: fixed in 6ad8e1bc76f5757c1ed1b5eb6d1e22e02f5b820e; regressions in 10a8dea6be7c213e130bbdee1c87c45e2ee91b9b (execution pending).
- m2: fixed in 030f99db854988532becceb3f7526c2e4aa9d2c4 (execution pending).
- m3: fixed in 3db851fa49c39e2a522925dc8b0690efba66fd61 and addbcd7ba519ea0864757130e850262995e53d0e (timings/twin pending).
