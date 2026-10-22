# align-residual lane report

## SUMMARY

- Implements A7's benign-only logged-work energy model and excess-energy detector.
- Uses scaled Householder QR and nonnegative Paule-Mandel extra-variance estimation.
- Preserves shared parameter covariance and independent turn/episode uncertainty.
- Provides task-pair-held-out thresholds and normal hidden-decode power boundaries.
- Shared-record adapter honors deleted turns and hidden-token semantics; problems are flags.
- Alignment checks: 21 pass with NumPy; 21 run with one optional-reference skip on stdlib only.
- Synthetic benign and zero-energy-control false positives are 5.3% at alpha 0.05.
- Near the 80% hidden-work boundary, detection is 81.3%; deletion agrees with theory.
- Documents provisional M3 Max/NVML examples; no hardware result is claimed.
- Full Python 3.13 CI passes: 9891 tests, 146 skips; local VM differences are recorded.

## FILES

- joulewise/align/energy_residual.py: exact required dataclasses/API, stdlib QR/WLS,
  variance estimation, predictions, residuals, grouped calibration, detection power,
  flagged output adapters and turn_rows_from_episode.
- tests/align/test_energy_residual.py: realistic 20-turn agent/trace fixtures,
  numerical/edge checks, shared-record adapter, optional lazy NumPy reference.
- tests/align/test_energy_residual_power.py: 512 independent coefficient-coverage
  worlds, grouped calibration, hidden-work/deletion power and zero-energy control.
- docs/align/energy_residual.md: model terms, uncertainty assumptions, quantile,
  power derivation, worked M3 Max and duty-sampled NVML examples, limitations.
- tests/test_shard_tests.py: sole registry exception; add only the align. namespace
  to the inventory's unittest module-name prefix normalization. No tests removed.
- .codex-report/align-residual.md: this report. No other files changed.

## PUBLIC API

Required frozen dataclasses retain exactly the specified constructor fields:

- TurnRow(episode_id: str, group: str, context_tokens: int, prefill_tokens: int,
  decode_tokens: int, duration_s: float, energy_j: float, energy_half_width_j: float)
- EnergyModel(names: tuple[str, ...], coef: tuple[float, ...],
  cov: tuple[tuple[float, ...], ...], sigma2_per_turn: float, n_turns: int)

Functions:

- design_row(r: TurnRow) -> list[float]
- fit_energy_model(rows: Sequence[TurnRow]) -> EnergyModel
- predict_episode(model: EnergyModel, rows: Sequence[TurnRow]) -> tuple[float, float]
- residual_score(model: EnergyModel, logged_rows: Sequence[TurnRow],
  measured_total_j: float, measured_half_width_j: float) -> float
- grouped_benign_threshold(benign: Mapping[str, tuple[Sequence[TurnRow], float,
  float]], *, alpha: float) -> float
- min_detectable_hidden_decode_tokens(model: EnergyModel,
  logged_rows: Sequence[TurnRow], *, alpha: float, power: float,
  measured_half_width_j: float) -> float
- turn_rows_from_episode(episode: Episode,
  turn_energy: Mapping[int, tuple[float, float]]) -> tuple[TurnRow, ...]

Private subclasses attach flags without changing required dataclass constructors
or numeric/sequence return behavior. Copy flags into Episode.flags before casting,
arithmetic, or ordinary JSON serialization.

## TESTS RUN

Local Python 3.12.14; NumPy 2.3.5 was already installed, so no package install was
needed. Every local test command below used PYTHONDONTWRITEBYTECODE=1.

- python3 -m unittest discover -s tests/align -t .
  First 20-test run: 2 failures, 0 errors/skips. A single iid 400-episode
  calibration draw gave threshold 1.490743 and false positives 72/1000,
  beyond the requested one-binomial-SE agreement bar. Conditional normal
  theory for that draw was 0.0627; the detector and power tests otherwise passed.
  A stratified Gaussian calibration fixture reduces this finite-tail Monte
  Carlo variability while keeping independent iid evaluation episodes.
  The 20-test rerun passed, with NumPy reference executed.
  Final 21-test run (512 fitting seeds, label-compatibility regression):
  21 passed, 0 failures/errors/skips, 23.767 s.
- python3 -S -m unittest discover -s tests/align -t .
  Initial 20-test run: passed, 1 skip, 23.064 s.
  Final 21-test run: passed, 1 skip, 23.986 s.
  Skip reason: "NumPy optional WLS reference absent". -S disables site packages;
  all mandatory production and synthetic paths still execute.
- python3 -m unittest tests.test_shard_tests
  4 passed, 0 failures/errors/skips, 7.905 s.
- python3 -S -m unittest tests.align.test_energy_residual.TestEnergyResidual.test_power_boundary_and_context
  1 passed, 0 failures/errors/skips, 0.020 s, after the zero-hidden-energy /
  requested-power-below-alpha edge fix. Conventional 0.05/0.8 outputs unchanged.
- python3 scripts/quick_suite.py --tier touched --since 4d47c4362352ccd8d4d904134a79f0d8260b21b5
  254 modules, 135 excluded, 7 failed modules, 754.316 s. Both detector
  modules passed. Failed modules: tests.test_b5_chain_prune2 (2 failures),
  tests.test_b5_driver_p2 (3 failures), tests.test_harvest_b5_p2harv (1 failure),
  tests.test_run_campaign_p2_rc (3 failures), tests.test_v5_block4_x12a (2 errors),
  tests.test_v5_block4_composed (1 error), tests.test_fixture_orphan_census
  (1 failure). These files and their production code are unchanged by this lane.
  Exclusions: 130 timing-threshold, 2 exclusive, 3 split and 5 A211 declarations
  (categories overlap). The runner reports module counts, not aggregate skips.
  Process-tree/orphan checks report surviving PIDs. Three closeout errors
  reported backup command failures; rsync was absent from the VM. Public Debian
  rsync 3.4.1/libpopt packages were subsequently extracted under /tmp for the
  canonical run, since apt installation lacks privileges and sudo is absent.
- python3 -m unittest discover -s tests
  The local Python 3.12.14 duplicate was interrupted (exit 130) only after the
  completed Python 3.13 full CI suite passed. It had emitted failures/errors in
  existing checks and no aggregate local unittest result; no local full-suite
  pass or final count is claimed. The complete successful repository result is
  the 9891-test CI run below. Local discovery found 9891 tests, 0 import errors.
  Exact local command, including temporary public rsync/libpopt and the
  documented worktree corpus override:

  ```bash
  PATH='/tmp/joulewise-align-residual-tools-53cthbxz/root/usr/bin':"$PATH" LD_LIBRARY_PATH='/tmp/joulewise-align-residual-tools-53cthbxz/root/usr/lib/x86_64-linux-gnu'${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH} R7F_CORPUS_ROOT=/workspace/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/align-residual-canonical.log 2>&1
  ```
- git diff --check
  Passed.

CI fallback during cloud startup: draft PR #525 against lane/2026-10-21-align-spine,
https://github.com/mpmdw/JouleWise/pull/525. Run 39704390856 at
fcb64dcdf478fa36fe8dc1a85a8826097075c257 passed state/documentation fences,
build and installed-wheel checks. Its exact test command was
python3 scripts/quick_suite.py --tier quick --workers 4:
212 modules, 177 excluded, 1 failing module. tests.test_shard_tests ran 4 tests,
1 failure, 0 errors/skips, because plain discovery's align.* names differed from
the runner's tests.align.* names. The permitted one-prefix inventory addition
now passes locally. Main CI test shards were skipped following that quick failure.
New detector modules had unknown timing weights and were excluded from quick.

### Completed full CI evidence

Python 3.13 CI run 39707410101 is SUCCESS at numerical code head
658bc6b08704d2b1adf048b1249e8259a08ca6ef:
https://github.com/mpmdw/JouleWise/actions/runs/39707410101
All 20 jobs passed, including fences, build, installed-wheel, quick, the 12
ordinary shards, calibration exits and both writer-crash-matrix partitions.
The 15 complete-suite test jobs ran 9891 tests, 0 failures, 0 errors, 146 skips.
This exactly matches the 9891 tests independently discovered locally.
Quick also passed: 212 modules, 177 excluded, 0 failures, 288.989 s.

| CI job | Tests | Skips |
| --- | ---: | ---: |
| calibration-writer-crash-matrix-exclusive (3.13, 2) | 19 | 0 |
| calibration-writer-crash-matrix-exclusive (3.13, 1) | 1 | 0 |
| calibration-exits-exclusive (3.13) | 48 | 0 |
| test (3.13, 5) | 818 | 5 |
| test (3.13, 2) | 504 | 6 |
| test (3.13, 7) | 921 | 11 |
| test (3.13, 9) | 922 | 20 |
| test (3.13, 8) | 836 | 8 |
| test (3.13, 1) | 563 | 3 |
| test (3.13, 10) | 1178 | 20 |
| test (3.13, 6) | 656 | 16 |
| test (3.13, 11) | 931 | 6 |
| test (3.13, 4) | 764 | 10 |
| test (3.13, 3) | 715 | 16 |
| test (3.13, 12) | 1015 | 25 |
| Total | 9891 | 146 |

Alignment module tails from that CI run:

```text
MODULE PASS tests.align.test_records tests=4 failures=0 errors=0 skipped=0 seconds=0.009
MODULE PASS tests.align.test_energy_residual tests=11 failures=0 errors=0 skipped=1 seconds=0.255
MODULE PASS tests.align.test_energy_residual_power tests=6 failures=0 errors=0 skipped=0 seconds=28.013
```

Exact ordinary-shard command (SHARD_COUNT=12; SHARD_INDEX=1 through 12):

```bash
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

Exact exclusive writer command (SHARD_INDEX=1 and 2):

```bash
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

Exact calibration-exits command:

```bash
python -m unittest -v tests.test_calibration_exits
```

The skip reasons below are unchanged repository conditions, not new lane rulings.
They include one optional NumPy-reference skip; all mandatory A7 paths ran.

| Count | Existing CI skip reason |
| ---: | --- |
| 1 | a desk run of the real read-only probes (macOS) |
| 1 | ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus |
| 1 | ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus |
| 10 | block-3 b3w1 archive is local to the measurement Mac |
| 1 | clonefile(2) is an APFS call |
| 1 | CommonCrypto is macOS only |
| 1 | controlled runs corpus unavailable |
| 1 | Darwin pgrep ancestor exclusion; Linux pgrep has no such rule |
| 1 | design/2026-10-05-v5-claim-block-draft is not in this clone |
| 6 | FLAG joulewise/arm_readiness.py:7621: committed GAMMA lacks freeze authority; writer/ARM cannot continue. No nonphysical semantic shortcut is allowed. |
| 13 | full scored corpus (set JOULEWISE_FULL_CORPUS=1) |
| 1 | full-fixture proof runs in d117-production-proof |
| 1 | gate-prune inventory is not on this machine |
| 1 | jsonschema not installed (optional) |
| 2 | jsonschema not installed |
| 1 | kern.bootsessionuuid is a Darwin kernel value |
| 1 | kern.bootsessionuuid is Darwin-only |
| 1 | lead-reviewed D-079 import custody inputs are unavailable |
| 2 | lead-reviewed D-079 import inputs are unavailable |
| 1 | live identity probes need macOS sysctl |
| 2 | local Qwen3 tokenizer mirrors are absent |
| 2 | lsof is not installed |
| 2 | markdown-it-py not installed; the build cannot run here |
| 9 | matplotlib ([analysis] extra) not installed |
| 1 | measurement ledger not on this machine |
| 2 | native QoS requires macOS |
| 1 | NumPy optional WLS reference absent |
| 2 | optional jsonschema dependency is absent |
| 1 | pinned MATH source absent |
| 1 | POWER-Z KM003C not on the USB bus |
| 1 | reads the macOS kernel clock |
| 2 | reads the real gauge (macOS) |
| 1 | reads the real host CPU ticks (macOS) |
| 1 | reads the real kernel clock (macOS) |
| 2 | reads the real notify bus (macOS) |
| 2 | reads the real process table (macOS) |
| 2 | reads the real SMC (macOS) |
| 1 | real campaign-log corpus is unavailable |
| 1 | real collect subprocess runs the macOS census and power-policy probes (pmset, sysctl); on Linux every round errors and, since fix round 4, an all-error session exits 1 by design |
| 1 | real launchctl required |
| 1 | real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json |
| 2 | real runs corpus unavailable |
| 1 | real spawned worker uses native QoS; hosted Linux shards feed the runner via stdin, which spawn cannot re-import |
| 1 | requires Darwin and explicit QG_LIVE_DARWIN=1 real-acquisition opt-in |
| 18 | requires Darwin fchflags/st_flags |
| 1 | retained capture 20260722T145535-e941c821 is not on this machine; run scripts/check_paper_replay_fence.py where the corpus lives |
| 1 | retained runs corpus is absent |
| 1 | retained XD/AQ corpora are not present; run the default R7F CLI where both corpora live |
| 1 | runs_window corpus absent (clean checkout without bundles) |
| 1 | runs/ corpus absent (clean checkout without bundles) |
| 2 | source corpus unavailable: /Users/edr/code/JouleWise/runs_window_a5_20260723 |
| 1 | split production proof requires a registered JOULEWISE_D117_PROOF_PARTITION |
| 1 | stopped-after-exec probe requires Darwin POSIX_SPAWN_START_SUSPENDED |
| 1 | STRUCTURAL-BLOCKED: generator targets uninstalled _v2 family while the registry installs _v5 |
| 1 | STRUCTURAL-BLOCKED: synthetic _v5 fixture omits the family-publication marker required before self-predecessor validation |
| 1 | successor member not minted yet; shape check is vacuous |
| 1 | temporary filesystem is case-sensitive |
| 3 | the 2026-09-22 harvest archives are not on this machine |
| 1 | the block-5 design branch is not in this clone |
| 1 | the gate-prune inventory is not on this machine |
| 1 | the real kern.bootsessionuuid exists only on macOS |
| 1 | the two pilot-night archives are not on this machine |
| 1 | this file system gave the replacement lock the inode number of the lock just unlinked (4522116); the reclaimer tells the two apart by device and inode number only, so here it cannot (known limit of scripts/run_campaign.py _hazard_reclaim_stale_campaign_lock; APFS on the measurement Mac does not reuse numbers) |
| 3 | U2 successor engine pending |
| 1 | window-B quarantine custody path is absent |
| 3 | local model mirrors absent (CI environment): ['qwen25_0p5b', 'qwen25_1p5b', 'qwen25_7b'] |
| 1 | local model mirrors absent (CI environment): ['qwen3-1p7b', 'qwen3-8b'] |
| 1 | NEEDS-RULING: config-authenticated mock telemetry is excluded by the production claim loader, so the existing canned fixture cannot satisfy D-158's DATA-only predicate without loosening a production gate or building a new corpus fixture |
| 1 | requires Darwin's POSIX extended regular expressions |
| 1 | requires Darwin's real boot-session sysctl command |
| 1 | requires Darwin's real caffeinate process |
| 2 | requires Darwin's real pgrep command semantics |
| 1 | requires Darwin's real sysctl command |
| 1 | successor mirrors are still absent/incomplete: ['qwen3-1p7b', 'qwen3-8b'] |
| 1 | the block-3 reference archive and the measurement interpreter are on Ed's Mac only |


## END-TO-END

All worlds use the real public functions, with shared Episode/Turn/ToolCall
records and an adapter to visible TurnRows. A 20-turn agent uses 10 tool calls,
128-1024 prefill tokens and 128-512 decode tokens per call, growing cached
contexts and multi-second turns. The known generating coefficients are:
(5 J/call, 0.005 J/prefill, 0.12 J/decode, 1e-5 J/context-decode,
4e-6 J/context-prefill). Extra turn sd is 6 J; turn measurement standard
uncertainties are 0.4/1.2/2.0 J, with a separate 1 J episode component.
Both context products materially contribute above the noise floor.

The counter world has 933 samples at 100 ms, 20 turns, 10 tool calls and
93.2 s duration. The real shared-record serialization/deserialization runs;
fixture counter differencing subtracts the known 20 W baseline and produces
turn energies, agreeing within 0.004 J (1% of the smallest printed 0.4 J
uncertainty). Those energies go through turn_rows_from_episode, real benign
fit/prediction/residual/power functions. With the 8000-turn benign training fit,
this example measures 2105.630906 J, predicts 2094.285173 J with sd 27.326170 J,
and has score denominator 27.344462 J and hidden-token boundary 297.066107.
Counter differencing is controlled fixture attribution, not A4/live validation.

512 independent iid fitting worlds each contain 24 episodes (480 turns).
Coverage within one fitted standard error, compared with normal nominal 0.6827:

| coefficient | mean printed SE | observed coverage |
| --- | ---: | ---: |
| call intercept | 1.05720 | 0.6758 |
| prefill | 0.00195089 | 0.6504 |
| decode | 0.00394253 | 0.6758 |
| context-decode | 2.81740e-7 | 0.6504 |
| context-prefill | 1.50855e-7 | 0.6680 |

Each coefficient also passes the mean-bias check. The simultaneous 95% coverage
bar is z_(1-.05/(2*5))*sqrt(p*(1-p)/512), approximately 0.053.

Calibration uses 400 benign episodes, 8 task pairs, and real leave-pair-out
refits. To stabilize a stringent one-SE test, total Gaussian errors are
stratified across a randomly permuted normal quantile grid. Conditional Gaussian
orthogonal turn errors remain; finite-grid marginals approximate the same known
Gaussian noise model. Evaluation uses 1000 independent iid episodes. Coefficient
coverage worlds remain iid throughout. No seed search or threshold tuning occurs.

The final 8000-turn model has sigma2=35.468970 J^2/turn. Its example coefficients
and printed parameter standard errors are:

| feature | coefficient | SE |
| --- | ---: | ---: |
| intercept | 5.06699565 | 0.259652 |
| prefill | 0.00405276942 | 0.000475043 |
| decode | 0.121532956 | 0.000961433 |
| context-decode | 9.86926779e-6 | 6.77780e-8 |
| context-prefill | 4.07052688e-6 | 3.63806e-8 |

Held-out benign threshold: 1.668333. Independent false positives: 53/1000=0.053,
within sqrt(.05*.95*(1/400+1/1000))=0.012894 of alpha=0.05. This iid calibration
uncertainty is conservative for stratified calibration.

| H / normal H_min | mean integer H | observed detection | conditional theory | normal approximation |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0.00 | 0.0530 | 0.0486 | 0.0476 |
| 0.5 | 160.10 | 0.3780 | 0.3683 | 0.3679 |
| 1 | 309.26 | 0.8130 | 0.8139 | 0.8158 |
| 1.5 | 459.06 | 0.9860 | 0.9833 | 0.9839 |
| 2 | 608.64 | 1.0000 | 0.9996 | 0.9996 |

Hidden decode is equally distributed across turns, preserves logged contexts,
extends wall time and retains the same visible decode counts. Both normal
approximation and exact conditional theory agree within the family-corrected
binomial bars; the table appears in test failure messages.

| early logged turns deleted | observed detection | conditional theory |
| --- | ---: | ---: |
| 1 | 0.6170 | 0.6108 |
| 2 | 0.9720 | 0.9729 |
| 4 | 1.0000 | 1.0000 |

Deletion leaves measured energy unchanged, verifies the integer visible-turn
count, and retains deleted-turn noise in theoretical power. The zero-cost
hidden-work control gives exactly the same 53/1000 decisions as benign work,
including at twice the normal token boundary. It cannot create extra energy
evidence from semantics or extended duration.

Worked planning examples in docs use alpha=0.05, power=0.8, the conventional
choices requested: M3 Max D=2.457641 J, H_min=12.221726 (ceil 13 tokens);
NVML 100 ms/25 ms duty D=56.603887 J, H_min=70.372071 (ceil 71).
With 25 independent sensor-phase repetitions, the conditional NVML example
gives 30.755995 (ceil 31). These are explicit assumptions, not hardware findings.

## DECISIONS I MADE

- The direct bounded brief governs selection; root AGENTS/M0, current stop card
  and queue cautions were read. No active stop card. No nested target AGENTS.
  Preserve all lead-owned state/docs outside the explicit lane allowlist.
- Read PIPELINE.md, records.py and interfaces.py before writes; all unchanged.
- Use stdlib QR instead of a required scientific library; NumPy is only a
  lazily imported, skipUnless-guarded test reference.
- Read half-widths as one standard uncertainty, exactly as requested.
- Use nonnegative Paule-Mandel Q=n-5, safeguarded Newton/bisection and
  sqrt(binary64 epsilon) relative moment convergence. The all-zero-h case
  reduces to OLS with residual sum of squares/(n-5).
- Scale columns by their largest magnitude, solve by Householder QR and map
  covariance back to original units. Never apply a second reduced-chi-square.
- At zero h use a variance-scale ULP to represent limiting weights without
  false QR rank loss; do not add this numerical device to prediction noise.
- Public feature order is fixed; label spellings are diagnostic and unrestricted.
- Preserve input rows; undefined analyses return recorded flags and NaNs.
  Nonpositive hidden energy returns infinity above the false-positive power;
  targets at or below that power require zero hidden tokens.
- Preserve exact public dataclass constructor fields through private flagged
  model/numeric/sequence subclasses; document flag persistence at the boundary.
- Sum design rows before the covariance quadratic form; count independent
  turn noise plus independent episode measurement error without duplicating
  shared baseline/clock components.
- Never use duration as a regressor.
- Use type-1 inverse empirical CDF, strict score > threshold and whole task-pair
  holdouts. Connect malformed mixed groups into a common holdout with a flag;
  empty logs cannot identify a calibration group.
- Follow records semantics: decode_tokens includes hidden_tokens. The adapter
  subtracts hidden counts, honors logged=False and leaves missing energy flagged.
- Hidden-decode power uses mean logged context and the normal threshold,
  with no added-call intercept and fixed denominator, exactly as specified.
- Requested power <= alpha requires no hidden tokens, even when hidden work
  costs no energy; above alpha a nonpositive per-token cost remains unreachable.
- Adopt stratified synthetic calibration to reduce finite-tail Monte Carlo
  variability without changing the one-binomial-SE assertion or production
  quantile/model. Keep independent evaluation and iid coefficient-coverage worlds.
- Expand fitting coverage from 128 to 512 worlds to resolve the marginal
  initial coverage more precisely; derive simultaneous bars from binomial SE.
- Only registry edit: add align. to tests/test_shard_tests.py's inventory
  normalization, after CI demonstrated this precise name-registration failure.
- NVML period/duty alone imply no accuracy; power-gap noise, phase diversity,
  quantization and repetitions in the example are explicit parameters.
- Preserve the approximately 1 J M3 attribution component across repetitions.
- Initial commits were saved via connected GitHub tools while the cloud
  environment cycled pending/starting. Draft PR #525 enabled CI in that interval;
  local work resumed its remote head when the environment became available.

## CONTRACT-CHANGE

No shared-contract modification. Desired future change: a typed diagnostics
field/result would preserve flags without numeric/sequence subclasses.
The local adapters honor the exact required constructor fields. Callers must
copy flags into Episode.flags before arithmetic/casting/ordinary JSON encoding.

The shared records reject malformed construction with RecordError, whereas the
brief generally calls for flags. That contract wins and remains unchanged;
this lane's analysis conditions are returned as flags.

## OPEN ISSUES

- Local Python 3.12 VM process/custody checks differ from the successful
  production Python 3.13 CI run; touched failures are recorded above. No
  out-of-scope production/test repair was attempted. The duplicate local full
  run was stopped after all 9891 CI tests completed successfully.
- PR #525 remains a draft. Its merge gate ledger deliberately records missing
  independent review, merged-tree/cold review and dispositions as NOT-RUN;
  a green test workflow is not represented as completed merge authority.
- Independent cross-model twin agreement belongs to the integration gate;
  NumPy linear algebra checks are not represented as that independent twin.
- Hardware results and linear/normal/independent-error assumptions need a pilot.
- Attached scalar/sequence flags require explicit persistence as documented.

## NEEDS_RULING

none
