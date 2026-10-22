# SUMMARY
- Fixed B1: each routing statistic filters non-finite captures before all inference, naming dropped IDs/counts.
- Fixed M1: AUC-gain intervals refit classifiers per group-bootstrap draw, keeping original task copies together.
- Four 120-world null checks passed: false-addition rates 0.00833, 0, 0, 0.01667 against the derived 0.05350 bar.
- Flagged uncached re-forwards; cached multi-token tool prefills remain unflagged; disclosed roughly 91% effect-interval coverage.
- Streamed JSONL feature extraction and validated once; 52,500-token stats improved from 57.62s to 20.23s on the same CI inputs.
- CI: 9,919 tests, zero failures/errors, 153 skips; alignment: 41 passed, 8 optional skips; nested twin: 6 passed.
- The managed VM stayed offline; literal local probe/discovery commands and optional HF execution remain blocked.
- All changes are saved on the lane; protected contracts and the inherited registry exception are unchanged.

# FILES
- joulewise/align/moe/hooks.py: lazy HF router capture; uncached re-forward diagnostics.
- joulewise/align/moe/stats.py: exact public metrics/permutation APIs; aggregate validates once.
- joulewise/align/moe/stage_a.py: per-statistic finite cohorts, twelve-test Holm family, effects, refitted gain intervals, streaming JSONL.
- joulewise/align/moe/synthetic.py: existing configurable topic-affinity worlds, unchanged this round.
- joulewise/align/moe/__init__.py: existing shared RouterLog/stat exports, unchanged this round.
- tests/align/test_moe_stats.py: metric oracles, validation count and unit-specific agreement comment.
- tests/align/test_moe_stage_a.py: shifted/null/count controls, missing/empty captures, streaming lifetime and original bootstrap group identities.
- tests/align/test_moe_hooks.py: eight optional tiny-model integrations, including uncached generation and cached tool-result prefill.
- tests/align/test_moe_calibration.py: four 120-world calibration checks and the independent reviewer generator.
- tests/align/test_moe_review.py: reviewer r3 cases, independent twin invocation, old/new production-scale cost paths.
- docs/align/moe_stage_a.md: capture/backends, inference methods and small-group coverage disclosure.
- .codex-report/align-moe.md: this report.
- REGISTRY EXCEPTION inherited from r0: tests/test_shard_tests.py. Unchanged in this round; no new registry exception.
- Protected docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py are unchanged.

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
- analyze_stage_a(episodes: Iterable[Episode], *, n_bootstrap: int, confidence: float = 0.95, n_perm: int | None = None, seed: int = 0) -> StageAResult
- iter_episodes(path: Path) -> Iterator[Episode]: lane-local streaming adapter over shared from_json.
- mann_whitney_auc(scores: Sequence[float], labels: Sequence[int]) -> float
- StageAResult.auc_gain_interval: refitted group-bootstrap percentile interval;
  auc_gain_fixed_prediction_interval: descriptive fixed-score interval;
  auc_gain_interval_method: method name; n_auc_gain_bootstrap_valid: finite refit count.
- TopicWorld(groups: int = 12, repeats: int = 1, num_experts: int = 32, top_k: int = 4, layers: int = 4, turns: int = 6, prefill_tokens: int = 128, decode_tokens: int = 192, prefill_ns_per_token: int = 500_000, decode_ns_per_token: int = 20_000_000, tool_ns: int = 200_000_000)
- expected_topic_statistics(num_experts: int, top_k: int, fraction: float) -> dict[str, float];
  topic_episodes(side_fraction: float, *, design: TopicWorld | None = None, seed: int = 0, independent_noise: bool = False) -> tuple[Episode, ...].
- python3 -m joulewise.align.moe.stage_a EPISODES.jsonl --n-bootstrap N [--confidence C] [--n-perm N] [--seed S]

# TESTS RUN
Verified code/test revision: 19b4d84ced16aeda63e362dd570082932202d3ef.
[CI run 39715696032](https://github.com/mpmdw/JouleWise/actions/runs/39715696032)
completed successfully: all 20 jobs passed, Python 3.13.16 on Linux, no model extras.
The final report commit changes no code or tests relative to that revision.

| Module | Tests | Passed | Skipped |
| --- | ---: | ---: | ---: |
| tests.align.test_moe_stats | 11 | 11 | 0 |
| tests.align.test_moe_stage_a | 18 | 18 | 0 |
| tests.align.test_moe_hooks | 8 | 0 | 8 |
| tests.align.test_moe_calibration | 4 | 4 | 0 |
| tests.align.test_moe_review | 4 | 4 | 0 |
| tests.align.test_records | 4 | 4 | 0 |
| Alignment total | 49 | 41 | 8 |

The review module also ran `python -m unittest tests.align.test_twin_moe -v`
as a subprocess: 6 passed, zero skips. Those nested tests are additional evidence,
not added twice to the parent matrix count. Twin revision:
265e3c170fbba16a8752e3495061f5d2f8dfaa4a. Its three requested files were read with
`git show origin/lane/2026-10-21-align-moe-twin:<path>` from CI's full-history
checkout and written to the requested untracked test paths. No test fetched
network data or committed those files.

All eight hooks skipped with "tiny HF MoE integration needs optional torch and transformers".
No torch/transformers installation or extra-dependent run was possible: the
managed VM never admitted an exec command. No optional model execution is claimed.
The two added hook regressions cover uncached generate and a cached multi-token
tool-result prefill and skip cleanly with the same dependency guard.


Executed quick command: `python3 scripts/quick_suite.py --tier quick --workers 4`:
212 modules passed, 180 excluded by the existing policy; excluded modules remained
covered by ordinary/exclusive jobs. Executed compile command:
`python -m compileall -q joulewise tests`: passed.

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


| Ordinary shard | Tests | Skips | Failures / errors | Job ID |
| --- | ---: | ---: | ---: | ---: |
| 1 | 589 | 25 | 0 / 0 | 119618859459 |
| 2 | 840 | 10 | 0 / 0 | 119618859577 |
| 3 | 497 | 7 | 0 / 0 | 119618859484 |
| 4 | 762 | 13 | 0 / 0 | 119618859530 |
| 5 | 751 | 10 | 0 / 0 | 119618859518 |
| 6 | 619 | 7 | 0 / 0 | 119618859526 |
| 7 | 757 | 14 | 0 / 0 | 119618859464 |
| 8 | 792 | 19 | 0 / 0 | 119618859598 |
| 9 | 863 | 7 | 0 / 0 | 119618859476 |
| 10 | 1263 | 27 | 0 / 0 | 119618859478 |
| 11 | 896 | 10 | 0 / 0 | 119618859581 |
| 12 | 1222 | 4 | 0 / 0 | 119618859475 |
| Calibration exits exclusive | 48 | 0 | 0 / 0 | 119618859317 |
| Crash matrix exclusive 1 | 1 | 0 | 0 / 0 | 119618859352 |
| Crash matrix exclusive 2 | 19 | 0 | 0 / 0 | 119618859360 |

Full matrix total: 9,919 tests, 9,766 passed, 153 skipped, zero failures/errors.
Quick-tier repetitions and nested twin tests are not added to that total.

Complete skip-reason census (153), from the final matrix logs:
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
- 1: this file system gave the replacement lock the inode number of the lock just unlinked (4522201); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers)
- 8: tiny HF MoE integration needs optional torch and transformers
- 3: U2 successor engine pending
- 1: window-B quarantine custody path is absent

Local commands below were blocked by "No usable execution environment is available";
they are NOT recorded as executed:
```sh
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-moe
git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-moe origin/lane/2026-10-21-align-moe
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers
python3 /workspace/JouleWise/.review1/r3_stage_a.py /workspace/JouleWise
python3 /workspace/JouleWise/.review1/r10_gain_interval.py /workspace/JouleWise 120
python3 /workspace/JouleWise/.review1/r4_null_calibration.py /workspace/JouleWise 120
python3 /workspace/JouleWise/.review1/r9_hooks_nocache.py /workspace/JouleWise
python3 /workspace/JouleWise/.review1/r6_hooks_dispatch.py /workspace/JouleWise
python3 /workspace/JouleWise/.review1/r11_cost.py /workspace/JouleWise
python3 /workspace/JouleWise/.review1/r1_stats_ground_truth.py /workspace/JouleWise
```
The B1 one-liner and literal .review1 file creation likewise could not run in the
unavailable VM. Executed CI ports are identified explicitly: missing/empty captures
in test_moe_stage_a and reviewer r3 in test_moe_review; r10/r4 worlds and expanded
refit/fixed rate columns in test_moe_calibration; r11 and r1 section-6 old/new cost
paths in test_moe_review. Standalone metric ground truth additionally passed the
independent twin. This is CI evidence, not a claim that the literal VM scripts ran.


# END-TO-END
The unchanged seed-731 topic world has 12 groups, 24 episodes, 144 turns, 120 tools,
23,176 prefill and 34,494 decode tokens; four layers, 32 experts, top-4.
The side-task topic receives 40% of sabotage decode tokens in expectation.
Counts remain matched within pairs. The real chain was
RouterLog -> Episode -> episode_stats -> finite metric cohort -> within-group
permutation -> twelve-test Holm -> grouped effect bootstrap -> task-held-out
routing/metadata/combined classifiers -> AUC -> refitted grouped gain bootstrap.
Shared Episode JSONL write/decode and the streaming CLI also passed.

With 256 bootstrap draws and seed 83, routing/combined AUC remain 1.0, metadata
0.5, gain 0.5 with refitted interval [0.5, 0.5]. All four decode Holm p-values
remain 0.005859375 (exact 4,096 arrangements). Decode reuse effect remains
0.1359071076578115 [0.13118738132590682, 0.14117669025037116], containing the
analytic 0.14 = .4^2*(1-4/32). Decode load remains
0.9648177222877435 [0.9501019886896048, 0.983076392559291].
All complete-log raw statistics and point AUCs are unchanged by this round.

The paired zero-shift control has all AUCs 0.5 and gain 0. The independent-noise
zero-shift control has unchanged gain 0.09027777777777779, but its main interval
moves from fixed-score [-0.026562499999999985, 0.26388888888888884] to refitted
[-0.2336805555555555, 0.30312500000000003]: endpoint changes -0.2071180555555555
and +0.039236111111111194. Both contain zero; all Holm p-values are 1.
The counts-only positive control retains metadata AUC 1.0. The verified full
48-layer/128-expert/top-8 shape and deterministic balanced-affinity oracle passed.

M1 calibration used 120 worlds per condition, 200 bootstrap draws per world,
the exact r10/r4 generator parameters, and the same seeded worlds for old
fixed-score versus new refitted intervals. Lane seeds are 5000+s, reviewer seeds
1000+s, analysis seed s. The lower-side acceptance bar is
.025 + 2*sqrt(.025*.975/120) = 0.05350438562747849, derived from two binomial
standard errors around the lower side of a conventional two-sided 95% interval.

| Null world | Fixed lower>0 | Refit lower>0 | Fixed upper<0 | Refit upper<0 | Zero in effect CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| lane12 | 0.058333 | 0.008333 | 0.141667 | 0.000000 | 0.913194 |
| lane17 | 0.058333 | 0.000000 | 0.150000 | 0.000000 | 0.905556 |
| reviewA | 0.166667 | 0.000000 | 0.083333 | 0.000000 | 0.911111 |
| reviewB | 0.058333 | 0.016667 | 0.083333 | 0.000000 | 0.747917 |

False additions after refitting are 1, 0, 0, and 2 of 120; the bar admits at most
6 of 120. Every world passes. Upper-side rates have no acceptance bar, as directed.
For the same 120 reviewer-A worlds, fixed lower exclusion falls from 20/120 to
0/120; reviewer B falls from 7/120 to 2/120. The lead's recorded reviewer outputs
used 150 worlds, so their .147/.053 fixed rates are not the same census as the
.167/.058 first-120 rates above. Point AUCs were not changed by refitting intervals.

| Null world | Gain mean | Across-world SD | Refit interval implied SD | Routing AUC | Metadata AUC | Combined AUC | Raw p<.05 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lane12 | -0.027373 | 0.149301 | 0.163195 | 0.472627 | 0.500000 | 0.472627 | 0.038889 |
| lane17 | -0.011267 | 0.093970 | 0.100768 | 0.488733 | 0.500000 | 0.488733 | 0.040278 |
| reviewA | 0.023746 | 0.078035 | 0.094312 | 0.488689 | 0.456546 | 0.480291 | 0.048611 |
| reviewB | -0.007886 | 0.059606 | 0.070244 | 0.615686 | 0.646965 | 0.639079 | 0.205556 |

Implied SD is width/(2*Phi^-1(.975)), the r10 normal-reference column.
For lane12/lane17 it changes from the recorded fixed-score .099/.058 to
.163/.101; across-world SD stays .149/.094. Raw-effect interval coverage remains
0.9131944444444444 and 0.9055555555555556: about .91, not .95, with 12--17 groups.
Raw effects' bootstrap method was retained; the disclosure and fixed-seed test
comment were corrected. Reviewer B has genuine count differences and raw routing
statistics carry finite-length effects, so coverage of zero there is descriptive,
not calibration about a true zero effect. Only gain false additions are barred.

B1's independent reviewer world has 68 multi-turn episodes, 8 layers, 64 experts,
top-6, side-topic fraction .25 and sabotage count ratio 1.3. Complete-world gain
stays 0.3866782006920415; fixed interval [0.26892301038062283, 0.510402249134948] becomes
refitted [0.2740484429065744, 0.576319204152249], endpoint changes +0.005125432525951545 and
+0.065916955017301 (400 draws, seed 3).

Missing rev-11-1-benign-1 previously gave 12/12 NaN effects and p-values; now
all twelve are finite. Empty decode on rev-11-1-sabotage-1 previously gave four
NaN decode tests; now none. Each affected test names its dropped ID and count 1.
The twelve-test Holm family remains intact. Bootstrap draws are made from each
finite metric cohort, never selected for happening to avoid a bad task group.
The lane's missing-log regression also compares every effect, p, standardized
effect and interval with an explicit finite-cohort analysis.

After-values below use 100 draws and seed 3. The before values for missing-log
effects/p-values were NaN, so arithmetic before/after deltas are undefined.
The delta column instead states the change from the complete capture, for
review of which measured values moved.

| Missing-log metric | Effect after fix | Delta from complete | p after fix | Holm after fix | Interval |
| --- | ---: | ---: | ---: | ---: | --- |
| prefill_usage_entropy | -0.00028674921630272995 | -0.0000015374834227011437 | 0.4942166140904311 | 1 | [-0.0009349931889062245, 0.0005493051852632095] |
| prefill_load_imbalance | 0.0038500246083311073 | 0.00003489333205969206 | 0.20452155625657203 | 1 | [-0.0023246754587570068, 0.009426608717403024] |
| prefill_reuse_fraction | -0.00017673292715271224 | 0.00006262894727029401 | 0.907465825446898 | 1 | [-0.0024488088142825782, 0.002800828204718727] |
| prefill_mean_reuse_distance | -0.007488027771421551 | 0.00137085607924178 | 0.8485804416403786 | 1 | [-0.08769524513236839, 0.05226729991219849] |
| decode_usage_entropy | 0.00822934729554112 | 0.00006617635999956427 | 0.0005257623554153522 | 0.006309148264984227 | [0.005891324567008075, 0.010602931327241322] |
| decode_load_imbalance | -0.11923286820475806 | -0.00013717576227703643 | 0.0005257623554153522 | 0.006309148264984227 | [-0.1328238961811576, -0.10461218279221109] |
| decode_reuse_fraction | -0.016784267863484328 | 0.0003631535057489199 | 0.0005257623554153522 | 0.006309148264984227 | [-0.021931980183624328, -0.012519274435634371] |
| decode_mean_reuse_distance | 0.24923163165021656 | 0.00972411753781327 | 0.10830704521556257 | 0.6498422712933755 | [0.023882856151886536, 0.5020591228785161] |
| both_usage_entropy | 0.007452786940648098 | -0.000009354955722439169 | 0.0005257623554153522 | 0.006309148264984227 | [0.006569856047821391, 0.008335012577874511] |
| both_load_imbalance | -0.06381805241756502 | 0.00007047277287762499 | 0.0005257623554153522 | 0.006309148264984227 | [-0.07065084414484717, -0.05708297854834864] |
| both_reuse_fraction | -0.005152064787562667 | 0.0001308843291219306 | 0.0010515247108307045 | 0.007360672975814931 | [-0.007107122688772458, -0.002716248098479148] |
| both_mean_reuse_distance | 0.025510802733824774 | 0.0009257667419527819 | 0.34279705573080965 | 1 | [-0.01978726073830773, 0.06120555510294766] |

| Empty-decode metric | Effect after fix | Delta from complete | p after fix | Holm after fix | Interval |
| --- | ---: | ---: | ---: | ---: | --- |
| prefill_usage_entropy | -0.0002852117328800288 | 0 | 0.46635120925341744 | 1 | [-0.000926948980158207, 0.0005229795491963029] |
| prefill_load_imbalance | 0.0038151312762714153 | 0 | 0.19400630914826497 | 0.9700315457413249 | [-0.0022133948193477845, 0.009359591291167684] |
| prefill_reuse_fraction | -0.00023936187442300625 | 0 | 0.8732912723449001 | 1 | [-0.0024714490819840837, 0.0026332987463619584] |
| prefill_mean_reuse_distance | -0.008858883850663331 | 0 | 0.8012618296529969 | 1 | [-0.08851696507477141, 0.05016003540950442] |
| decode_usage_entropy | 0.007993670960536357 | -0.00016949997500519988 | 0.0005257623554153522 | 0.006309148264984227 | [0.005579245730519572, 0.010175549586028456] |
| decode_load_imbalance | -0.1187635094459573 | 0.00033218299652372496 | 0.0005257623554153522 | 0.006309148264984227 | [-0.13254696047189882, -0.10354452321930693] |
| decode_reuse_fraction | -0.01754462463493715 | -0.0003972032657039021 | 0.0005257623554153522 | 0.006309148264984227 | [-0.022147159292044007, -0.013646947719627137] |
| decode_mean_reuse_distance | 0.23237316007501632 | -0.007134354037386964 | 0.14668769716088328 | 0.8801261829652998 | [0.009463524674851728, 0.4907933470171602] |
| both_usage_entropy | 0.007249741513685528 | -0.0002124003826850093 | 0.0005257623554153522 | 0.006309148264984227 | [0.006246935443945731, 0.00832293658982737] |
| both_load_imbalance | -0.06217243726238664 | 0.001716087928056012 | 0.0005257623554153522 | 0.006309148264984227 | [-0.07065084414484717, -0.05342184170948705] |
| both_reuse_fraction | -0.005239422305396393 | 0.00004352681128820448 | 0.0005257623554153522 | 0.006309148264984227 | [-0.007237087590283511, -0.0028385986065618853] |
| both_mean_reuse_distance | 0.018294700622976244 | -0.006290335368895748 | 0.5094637223974764 | 1 | [-0.023095784858623247, 0.0510884265176128] |

m3 before/after cost used the same CI inputs and unchanged validating public
metric arithmetic; the before path reconstructs r0's twelve-call aggregate
comprehension, and the after path is production episode_stats. These are paired
CI measurements, not comparisons between the reviewer's Mac and CI hardware.

| Shape | Before seconds | After seconds | Change |
| --- | ---: | ---: | ---: |
| r11: 10,000 tokens x 48 x top-8 | 10.799911144 | 3.625220240 | -7.174690904 (66.4% lower) |
| r1 section 6: 52,500 tokens x 48 x top-8 | 57.622601816 | 20.228703469 | -37.393898347 (64.9% lower) |

Single validation took 0.683171915s on the 10k-token log. Memory remained
54,321,120 bytes, 5,432.112 bytes/token (about 5.3 KiB/token); the shared log
format did not change. The twelve-fold validation repetition is removed,
and the CLI no longer accumulates the episode logs. A weak-reference iterator
regression proves a log is released before the next episode is requested.
Numerical old/new aggregate agreement and all six twin tests passed.

# DECISIONS I MADE
- Filter finite rows separately per metric before effects, permutation and bootstrap; retain all episode-aligned features.
- Keep Holm family all 12 planned tests and flag excluded IDs/count plus one-condition groups.
- Refit metadata and combined classifiers for every cluster draw; hold all copies of each original task group together.
- Fixed-score AUC/gain intervals are labelled descriptive and cannot substantiate added routing separation.
- Use conventional 95% refit percentile gain interval, assess only false lower bound above zero against lead's derived bar.
- Use 120 worlds per null, bootstrap budget 200, same seeded worlds/parameters as reviewers; print upper rates with no bar.
- Retain raw-effect percentile intervals and disclose roughly 91% zero coverage for 12--17 groups.
- Preserve actual uncached repeated forwards; add uncached_reforward flag; cached multi-token tool prefill is ordinary prefill.
- CLI lane-local iter_episodes uses shared from_json; analyze_stage_a consumes iterable and retains only scalar features.
- Validate once per episode_stats aggregate; public metrics continue independent validation.
- No new registry exception; preserve previous tests/test_shard_tests.py change.
- Use existing CI through draft PR #520 while runtime offline; no local execution or optional-model claim.
- Published Qwen3-30B-A3B topology remains verified at config revision d47d535f78ec44bd57128f8e8aeba17eeb0285ea: 48 layers, 128 experts, top-8.
- No shared-record/protocol changes and no main-branch push. Continued the exact existing lane head 384d37995 through GitHub commits because the managed VM remained unusable.

# CONTRACT-CHANGE
none

# OPEN ISSUES
- The managed environment stayed offline in pending/starting. exec_command returned "No usable execution environment is available." Local checkout/fetch, literal .review1 script creation/execution, the exact local discovery commands, and optional-package installation/execution could not run. CI execution and in-scope reviewer-case ports are distinguished above; no local or HF execution is claimed.
- Effect percentile intervals with 12--17 groups retain roughly 91% empirical zero coverage despite nominal 95%; documented rather than silently relabelled.
- The AUC comparison is for this learner and these four count features, not universal conditional independence from every function of counts.
- vLLM and llama.cpp capture are documented, as requested. Compiled/fused/distributed HF capture and Stage B power visibility need separate validation.
- Recorder host synchronization is instrumentation overhead, not Stage B evidence.
- Draft PR #520 remains a build handoff. The separate gate-ledger run 39715696010 failed because rows 1--5 are NOT-RUN; this is not merge readiness. Lead-owned delta review and main integration are not claimed.

# NEEDS_RULING
none

# FIX LOG
- B1: fixed in 6ad8e1bc76f5757c1ed1b5eb6d1e22e02f5b820e.
- M1: fixed in 210aa1336095e1307cea93123bbf5781b97db09b.
- m1: fixed in e4463cbaee04f67d8e704fdc0156ac36ae9ad7d1.
- m2: fixed in 030f99db854988532becceb3f7526c2e4aa9d2c4.
- m3: fixed in 3db851fa49c39e2a522925dc8b0690efba66fd61; addbcd7ba519ea0864757130e850262995e53d0e.
