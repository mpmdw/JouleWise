# Interp × energy tamper detection — 2026-11-07

**Delivery branch:** `interp/2026-11-07-tamper-detection`, already checked out
and clean at intake, based on integrated head `3c8ce8a5a`. Local commit only;
no push. The delivery commit includes this report. All new evidence is
**SYNTHETIC / UNCALIBRATED**. No physical validation or registration is claimed.

## Intake and authority

The explicit user brief selects desk work on ranked ideas 10,11,13 and
overrides routine coordination-state updates, kernel registration and the
canonical full-suite requirement. Read the design study/checks, repository
AGENTS/CLAUDE conventions, M0, targeted stop/status/workspace/queue regions,
source-of-truth map, analysis-plan contract and D-009/D-050/D-053/D-062/D-067
authority. No active stop card was present. This was a single-agent task;
no delegation, external consult or scientific authority decision was made.
No decision-log policy was changed.

No network, download, model weights, real measurements, collectors or Block-5
analysis pipeline was used. Absolute study paths in repository text were not
followed. No sealed directory or external study-data path was opened, searched
or listed. The existing blinded analysis job was not inspected or controlled.
Only this task's own synthetic demo process was interrupted, by its tool
session ID, during the performance investigation below.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` remain unchanged. No kernel tasks were registered.
Coordination notes are confined to this report; advisor-visible scientific
state has not changed, so `PROJECT_STATUS.md` was not edited.

## What changed

- [Threat model](../research/interp-energy/TAMPER-THREAT-MODEL.md): observer
  trust, non-adaptive/timing-masked/adaptive actors, ALIGN E2 relationship,
  signed energy anomalies, CPU gap, work-versus-intent limits, realistic rig
  floors, timing comparator, surgical bounds, fixed-token versus behaviour
  channels, artifact-format blinding, and later native/instrument gates.
- [Detector](../../joulewise/interp_energy/tamper_detection.py): 18 scenarios
  including sham; merged surgery/rank-one/LoRA, dense zero/outlier hypotheses,
  structural pruning, fixed-k identity, precision swap, idle padding and an
  adaptive feature-matching counterexample; unmerged adapters, hidden GPU/CPU
  edits, matched logged compute, tool-wait overlap, precomputed deltas and
  behaviour shortening. Reuses behaviour count/context energy, lock-in noise
  generation/ABBA contrasts and existing independent-pair power planning.
  It does not implement a second edit or replay engine.
- [Challenge planning](../../joulewise/interp_energy/tamper_challenge.py):
  exact binomial weak-effect sample sizes with multiplicity, known-SD TOST
  sensitivity with pair/copy/session/systematic terms, and separate synthetic
  analyst roster/curator key with opaque IDs and a canonical roster digest.
- [CLI](../../scripts/interp_energy/tamper_detection.py): stdlib-only
  `--design-only`, NumPy `--mode replay` / `--mode episode`; JSON to stdout,
  with no file readers, model loading, native backends or capture switches.
- Two new unittest modules, lazy package discovery and README API links.

This list is the complete file scope together with this report:
`docs/research/interp-energy/TAMPER-THREAT-MODEL.md`, the two package modules,
the CLI, `tests/interp_energy/test_tamper_challenge.py`,
`tests/interp_energy/test_tamper_detection.py`,
`joulewise/interp_energy/__init__.py`, `joulewise/interp_energy/README.md`,
and this report.

## Numerical findings and limits

Three copies cannot establish above-chance forced-choice detection: even
3/3 successes gives p=.125. For p0=.50 versus p1=.60, power .80 and
family alpha .05 across 17 searched classes, exact sizing gives **325
independent copies per class**, critical count **188**, size .00273221 and
power .802397. Replays do not increase that binary n. Eight pair observations
per artifact, distinct matched shams, and 200 s per pair imply **4911.11
acquisition hours before overhead**. This broad challenge is banked and
unaffordable as a half-night rider. A smaller study must prospectively narrow
its family/target, rather than silently weaken the question or top up outcomes.

The ±2.7 J equivalence sensitivity includes a .5 J assumed systematic bound,
.3 J copy SD and 4.7 J session SD. With 325 copies × 8 repeats and alpha/17,
ideal balanced-session power at zero is 0 at 16 sessions, .668 at 64 and
.987 at 128. This is a known-SD planning model, not achieved coverage; actual
session weights, copy dependence and unknown variances need another analysis.

Final CLI demonstrations used seed 17, 325 synthetic copies/scenario and the
default noise settings. Selected descriptive rates:

| Scenario | Replay joint flag / forced choice | Episode joint flag / forced choice |
|---|---|---|
| Sham | .009 / .523 | .040 / .517 |
| Surgical Astra-scale scenario | .006 / .489 | .015 / .520 |
| Plain precision swap | 1 / 1 | 1 / 1 |
| Precision + idle padding | 1 / 1 | 1 / 1 |
| Adaptive matched-feature counterexample | .012 / .508 | .022 / .477 |
| GPU work within tool wait | 1 / 1 | .532 / .954 |
| CPU-only 40 J DC dose | .034 / .840 | .012 / .535 |
| Behaviour shortening, counts accounted | .003 / .505 | .015 / .511 |

The timing flag rate for the idle-padded swap was .009 replay / .025 episode,
versus 1 for the plain swap. These are one stress realization, **not**
independent-binomial confidence statements or live sensitivities. Copy/sham
pairs share a session offset, while calibration has a separate offset.
Chronological correlations remain. The adaptive counterexample is stipulated
observational equivalence, not an experimentally demonstrated attack.
The noise surrogate's bounded colored segments do not establish a continuous
long-range spectrum or lock-in gain. DC ratios/SDs, timing noise, padding watts,
precision savings and all edit effect sizes are explicit assumptions.

## Verification

Commands below ran only targeted modules; no full suite or pytest was run.
Numerical commands used `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1`. Test execution stayed far below the 20-minute budget.
Python 3.13.18 lacks NumPy here. `/opt/homebrew/bin/python3` is Python 3.14
with an existing NumPy installation; nothing was installed.

| Command | Final result |
|---|---|
| `python3.13 -B -m unittest tests.interp_energy.test_tamper_challenge` | 9 passed |
| `python3.13 -B -m unittest tests.interp_energy.test_tamper_detection` | 6 passed, 5 NumPy tests skipped |
| `python3 -B -m unittest tests.interp_energy.test_tamper_detection` | All 11 passed, numerical tests executed |
| `python3 -B -m unittest tests.interp_energy.test_integration` | 4 passed, including all lazy namespace imports without optional dependencies |
| `python3 -B -m unittest tests.interp_energy.test_behaviour_channel` | 25 passed |
| `python3 -B -m unittest tests.interp_energy.test_lockin` | 12 passed |
| `python3 -B -m unittest tests.interp_energy.test_power` | 9 passed |
| `python3.13 -B -m compileall -q joulewise tests scripts/interp_energy` | Passed |
| `python3.13 -B scripts/interp_energy/tamper_detection.py --design-only` | Passed; stdlib-only power report |
| `python3 -B scripts/interp_energy/tamper_detection.py --mode replay --seed 17` | Passed; full default-sized JSON parsed successfully |
| `python3 -B scripts/interp_energy/tamper_detection.py --mode episode --seed 17` | Passed; full default-sized JSON parsed successfully |
| `git diff --check` | Passed |

Tests check exact binomial tails against direct combinatorics, minimum-n
sizing, multiplicity, inability of three copies to reject chance, roster/key
separation and pairing, session/systematic floors, signed detection, iid null
error, CPU/timing masking cases, behaviour accounting, dose response,
reproducibility and lazy imports. No MLX module was executed.

Initial failure: an exact float equality in the new binomial-tail test compared
.12500000000000006 to .125. Changed the assertion to approximate equality;
the direct-combinatorics oracle and production calculation were retained.
The final module passes.

Performance correction: the first broad demonstration exposed quadratic
per-burst window work in the reused long-trace simulator. Interrupted only
that own demo (exit 130); its partial output is superseded. The new module now
requests bounded 256-block segments from the unchanged shared simulator and
retains a whole-realization session shift. Full-sized replay and episode demos
then completed quickly and were parsed as JSON. Matched shams explicitly share
the test session offset, preventing an irrelevant between-session shift from
driving forced-choice preference. Final tests/demos ran after those corrections.

Process deviation: the behaviour-channel regression command yielded with a
live tool session, and the lock-in module was launched before that session
was polled. They may have briefly overlapped, contrary to the one-module-at-a-
time instruction. Both completed successfully; subsequent test launches waited
for prior test completion. No claim of strict sequential execution is made.

## Remaining work / next exact step

No missing user ruling blocks this desk delivery. It makes no settled policy
change and authorizes no measurement. The lead should first review the threat
model's scope and choose a feasible, prospectively frozen dose/equivalence
question rather than the full 17-family weak-classification challenge.

Before native collection, validate Python 3.11 and Python 3.13 with NumPy;
Python 3.14 numerical success is not CI-version verification. On an authorized
Metal-capable non-measurement machine, run individually, without downloads:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

These reused tiny native tests remain **unrun here** and validate software only.
The lead must still resolve ASTRA replay-count/timing-boundary differences,
confirm artifact-format blinding and stored edit survival, specify a connected
session/prompt roster and cluster inference, verify timing-masked arms and
padding budget, and obtain S1 rail/DC validity plus actual dose/noise/variance
estimates in a later clean quiet window. Native artifact creation, session
allocation, measurement collection, model-specific effect calibration and the
clustered challenge reducer are **not implemented** by this synthetic package.
