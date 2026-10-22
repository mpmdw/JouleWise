# SUMMARY
- IN PROGRESS: implementation and synthetic results are saved; CI fixture correction awaits rerun.
- Implemented lazy HF Qwen3-MoE, Qwen2-MoE and Mixtral gate capture with phase tags.
- Implemented all exact public statistics signatures and grouped randomization.
- Added Holm-adjusted tests, grouped-bootstrap effects and held-out classifier AUCs.
- Compared routing, logged counts and combined features on identical task folds.
- Added multi-turn topic-affinity worlds, matched and independent-noise nulls.
- Added optional tiny random HF integration with no downloads.
- Draft PR #520 runs existing CI while managed runtime startup remains pending.

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
- TopicWorld(...); expected_topic_statistics(num_experts: int, top_k: int, fraction: float) -> dict[str, float]
- topic_episodes(side_fraction: float, *, design: TopicWorld | None = None, seed: int = 0,
  independent_noise: bool = False) -> tuple[Episode, ...]
- python3 -m joulewise.align.moe.stage_a EPISODES.jsonl --n-bootstrap N [--confidence C] [--n-perm N] [--seed S]

# TESTS RUN
Local execution is blocked by managed environment startup; exec_command reports
"No usable execution environment is available." No local counts, extras install,
or extra-dependent test success is claimed.

Existing CI via draft PR #520 at b1015ffc0713f752a137532f000df8b957b7a155:
- Build, installed-wheel, and fences: passed.
- python3 scripts/quick_suite.py --tier quick --workers 4:
  212 modules, 1 module failure; the inventory compared align.* against tests.align.*.
- tests.test_shard_tests: 4 tests, 1 failure, 0 skips.
- Ordinary/exclusive test jobs were skipped after that quick-tier failure.
- Minimal registry exception applied at 7f89688922d5750539cec72cb1649ae9d908a097:
  add "align." to the existing module-name prefix normalization in tests/test_shard_tests.py.
  This covers the three new test modules and the spine's existing test_records.
- At 2a170db68740f2abe567776b93bca5a6ecf14b17: quick tier passed.
  New stats module: 10 passed. New Stage A module: 14 tests, 1 fixture-oracle failure.
  Hook module: 6 skipped, reason "tiny HF MoE integration needs optional torch and transformers".
  Spine records: 4 passed. Other shards were cancelled after Stage A's failed oracle.
- Correcting the deterministic oracle and guaranteeing repeated selections in the
  optional tiny-model fixture; final evidence will replace this checkpoint.

# END-TO-END
Observed in CI at 2a170db68740f2abe567776b93bca5a6ecf14b17:
- 12 task groups, 24 episodes, 144 turns, 120 tool calls.
- 23,176 prefill tokens and 34,494 decode tokens; 32 experts, top-4, four layers.
- Sabotage changes the topic of 40% of decode tokens in expectation.
- RouterLog -> episode_stats -> grouped permutation -> Holm -> grouped bootstrap ->
  task-held-out routing/metadata/combined classifiers -> Mann-Whitney AUC/gain.
- AUC metadata 0.5, routing 1.0, combined 1.0; added AUC 0.5 [0.5, 0.5].
- Decode reuse effect 0.1359071076578115 [0.13118738132590682, 0.14117669025037116],
  containing analytic target 0.14 = .4^2*(1-4/32).
- Decode load effect 0.9648177222877435 [0.9501019886896048, 0.983076392559291].
- Decode entropy effect -0.1011543498323929 [-0.10440648355007826, -0.09856993805219644].
- All four decode Holm p-values 0.005859375 (exact 4096 arrangements).
- Paired zero-shift control: all AUCs 0.5, AUC gain 0, all Holm p-values 1.
- Independent-noise zero-shift control: routing/combined AUC 0.5902777777777778;
  added AUC 0.09027777777777779 [-0.026562499999999985, 0.26388888888888884];
  all Holm p-values 1. The interval includes zero.
- Counts-only positive control, shared JSONL CLI, and full 48/128/top-8 shape passed.
- Tiny real HF models skipped: optional torch/transformers absent.
- The nominal-f finite-CV oracle was the sole Stage A test failure (13/14 passed).
  It compared a finite topic draw with its population expectation. Replaced with
  balanced exposure whose entropy/load expectations are exact, without changing
  the random world or its reported analysis numbers. Awaiting rerun.

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
- Managed runtime unavailable: local required discovery, canonical suite, optional
  dependency installation, and tiny-model execution remain pending.
- Awaiting green CI after correcting the load-calibration fixture; current observed numbers are above.
- Lead-owned independent twin/review and merge gates are not claimed by this build lane.
- Compiled/fused/distributed HF capture requires separate coverage validation.
- Recorder host synchronization must not be interpreted as Stage B energy evidence.

# NEEDS_RULING
none
