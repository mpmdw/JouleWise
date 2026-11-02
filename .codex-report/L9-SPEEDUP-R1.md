STATUS: DONE (synthetic only; frozen set byte-identical). Stages 1-2: every recorded digest identical
to r0. Stage 4 (lead ruling 2026-11-01): identical to r0 after normalizing `validator_source_sha256`
and the digests derived from it; 5.7x faster than r0 with default workers.

# L9-SPEEDUP-R1: make the block-5 analysis runner fast without changing a byte

Lane `lane/2026-11-01-l9-speedup-r1`, based on `2fdc0929d` (tag `b5/analysis`). Synthetic data only:
the restored S10 chain (`tests.b5_analysis.fixtures_s10.chain_fixture()`) driven through
`tests.b5_analysis.joined_s10.JoinedHarness`. No real index, no restricted directory was read.

## What changed

### Stage 1 (`33b71d014`): run-scoped calibration-refit cache and content-keyed memos

- `joulewise/cli.py` `reduce` now passes the run's instrument-calibration physics store
  (`_instrument_calibration_physics_cache`), with the partition chosen from the bundle metadata
  exactly as validate-bundle (`_strict_problems`) chooses it. Outside an analysis run (no shared
  store) the call is unchanged and does no extra read. The reducer still consults an entry only
  after its own artifact/plist/events hash checks and never stores a wall-deadline-hit fit.
- New `joulewise/analysis_run_cache.py`: process-scoped run caches, entered once per driver run
  (and once per worker). It makes the run store visible to the cli strict-validation and reduce
  sites that run inside a fresh `contextvars.Context()` (the paper-custody indexed replays at
  `paper_custody.py:579`/`:723` and the reported-energy issuer at
  `paper_reported_energy_issuer.py:276`), which previously refitted every bundle in 9b/10/11. This
  is done from cli, **without editing paper_custody.py or whole_window.py** (see "Skipped").
- Content-keyed memos, active only inside a run. Key = sha256 of every authenticated byte string
  read plus every scalar input; the authenticated reads still happen on every call; exceptions are
  never cached; a hit returns the first computed value (deep-copied where mutable):
  - `environment_admission._window_thermal_pressure_refusals` (plist parse + exact-rational anchor
    LP + second parse; called for every member in every whole-window validation);
  - `cli._strict_uncertainty_evidence_problems` clock-evidence re-derivation.
- `tests/b5_analysis/test_shared_physics_cache.py`: the cold/warm expectation now reflects that
  `reduce` also uses the run cache (1 refit, was 3).

### Stage 2 (`a4f352257`): deterministic spawn pool for steps 1, 2 and 4

- New `joulewise/b5_analysis/parallel.py`; `dry_run.step_1/step_2/step_4` dispatch their
  independent child programs (validate-bundle per bundle, reduce per bundle, the two
  extract-detection-floors packs) to a spawned `ProcessPoolExecutor`.
- Log counters are assigned before dispatch (task i gets the counter it had serially). Primary
  context check, re-authentication of earlier outputs, registration, refusal classification and
  the stop at the first refusal all stay serial in the driver, in serial order. When a serial run
  would have stopped at task k, the files of every later task (logs, outputs, pre-created empty
  directories) are removed and the counter reset to the serial value.
- Physics: seed tasks (first bundle of each distinct calibration lacking a fit) run first; every
  later task is shipped the merged run store; each worker keeps its own store and memos for the
  step; worker fits merge back only from tasks whose deadline did not fire.
- Wall deadline: each worker runs the same `observe_wall_deadline` observer; its firings are
  added to the driver's observer, so the step is recorded as `calibration_wall_deadline_fired`
  (fail closed). A worker without an observer fails the step as
  `calibration_deadline_observer_unavailable`.
- Worker count: `scripts/run_b5_analysis.py --workers N` / `run(..., workers=N)`, else
  `JOULEWISE_B5_ANALYSIS_WORKERS`, else `min(8, cpu_count - 2)`. `--workers 1` is the unchanged
  serial code path; so is any runner that overrides `StepRunner.run` (test doubles, profilers).
  Invalid `--workers` is `analysis_arguments_invalid` (`step 0 - tooling_refusal`).

### Stage 3: not taken (lead: out of scope, not authentication-equivalent) — see below.

### Stage 4 (lead ruling 2026-11-01: `whole_window.py` / `paper_custody.py` may change; code identity may change)

- **4a (`85f0e0de2`, test `b859ee692`).** `whole_window._reference_energy_evidence_detail` (the NEG-8
  reference-energy re-derivation) now passes the run's calibration store to `reduce_bundle` through
  `analysis_run_cache.run_reduce_physics_kwargs`, with the same keying as cli (calibration artifact
  sha256 + exact metadata-bound partition, read only after the reducer's own hash checks; a
  deadline-hit fit is never stored; outside a run unchanged with no extra read). No other refit in
  `whole_window.py` / `paper_custody.py` lacked the cache (`strict_validate_bundles`' in-process path
  goes through cli, covered in stage 1); `calibration_bracketing`'s stored-evidence refit is frozen.
  `paper_custody.py` is not edited, so step 9b's claim-evidence receipt keeps its digest.
- **4b (`41d7efa30`).** Post-4a profile of step 5: `AuthenticatedConsumptionSession._prepare`'s
  per-member operative re-derivation (`_rederive_operative_summary`) was 63% of the step.
  `joulewise/analysis_member_pool.py` runs the dominated members' re-derivations in an ordered,
  persistent spawn pool (driver process only, workers > 1; created on first use, shut down with the
  run) and the session's loop consumes each outcome at its own serial position:
  - read census: when the caller is inside a `V2AuthenticationReadSession`, each task runs in its
    own fresh session in the worker and returns its records (identity, sha256, grammar, read count,
    first-read order); consumption registers them into the caller's session through the session's
    own first-digest/grammar enforcement, in member order, read-count times, so the session ends
    exactly as the serial loop leaves it, and a byte changed since the session first read it is
    refused as a serial read would refuse it (tested, including on real S10 members);
  - a task that raised is recomputed by the caller at its own position, so the serial code decides
    every failure;
  - the warm run store is shipped; worker fits merge back only from tasks whose deadline did not
    fire; worker firings are added to the run's observer (step fails closed as
    `calibration_wall_deadline_fired`); a worker without an observer makes the driver refuse the step
    as `calibration_deadline_observer_unavailable`;
  - `--workers 1` (and every process other than a run's driver, including stage-2 workers) keeps
    the old serial loop; the session's own `rederive` selection is shipped by reference to
    `whole_window._member_operative_summary` (the selection AST test now pins that).
- **Normalizer** (`docs/process_traces/2026-11-01-l9-speedup-r1/normalized_compare.py`, `1ee4ec682`):
  prints every differing file and field before normalization (pairing content-addressed files that
  were renamed), replaces each `validator_source_sha256` / `binder_source_sha256` value by a
  placeholder, recomputes every file's digest bottom-up to a fixpoint (values, substrings and
  content-addressed names), and requires the two trees to be identical; anything else is FAIL. A
  negative check (one changed digit in claim-verdicts) fails as it must.

## Proof

Four full synthetic blind dry runs over one restored S10 chain (restored once, read-only; its
22,950-file sha256 manifest is identical before and after all four runs), each via the joined
harness with fixed commit dates, so the scratch anchor `dc59ed529` is the same in all four:

- **r0**: `2fdc0929d` (base), serial, `profdriver.py ... none` (the profiling agent's driver).
- **r1d**: `a4f352257` (code identical to this head), **default workers** (8 on this 10-core host).
- **r1s**: `a4f352257`, `workers=1` (the serial path).
- **r1x**: `a4f352257`, `workers=6` (exploratory, run while r0 was running).

The r1 runs use a copy of the driver without the `TimedRunner` subclass (a runner that overrides
`StepRunner.run` deliberately keeps the serial path), passing `workers` to `dry_run.run`.

### Digest comparison: identical

| | r0 | r1d (default) | r1s (`--workers 1`) | r1x (6) |
|---|---|---|---|---|
| `B5-BLIND-DRY-RUN-RECORD.json` sha256 | `416f576d4df6...8fbea9` | same | same | same |

`416f576d4df6348730dd971cecd78d9bb9233e0aa2cbe4050e3557f4908fbea9` for all four: the record files
are byte-identical, so there is no differing field at all (the record's `analysis_commit` is the
harness scratch anchor, not the code commit). Beyond the record: all 449 recorded outputs (name and
sha256) equal, 18,487 census rows equal, the 449 non-log files under `restricted/` byte-identical,
the 1,088 restricted log names identical, and every log byte-identical after replacing the
custody/TMPDIR path (265 logs quote that path; 0 differ after normalisation). r0's record differs
from the profiling agent's `7046c366...` only because that run's chain lived at another path.

### Wall time per step (seconds, same host, M4 Air 4P+6E cores, attempt C and other runs sharing it)

| step | r0 | r1d default | r1s workers=1 | r1x workers=6 |
|---|---:|---:|---:|---:|
| 0 | 6 | 9 | 10 | 8 |
| 1 | 134 | 43 | 219 | 45 |
| 2 | 1581 | 21 | 65 | 23 |
| 3 | 1 | 0 | 1 | 0 |
| 3b | 225 | 240 | 242 | 273 |
| 4 | 664 | 219 | 420 | 285 |
| 5 | 7191 | 4522 | 4983 | 5043 |
| 8 | 402 | 261 | 282 | 279 |
| 6 | 398 | 257 | 334 | 277 |
| 9 | 957 | 572 | 658 | 683 |
| 9b | 3002 | 730 | 832 | 832 |
| 10 | 2806 | 614 | 720 | 714 |
| 11 | 3848 | 2108 | 2752 | 2794 |
| **total** | **21215** | **9596** | **11519** | **11255** |

2.2x overall at default workers (1.8x serial). Load differed between runs (r0, r1s and r1x
overlapped each other and attempt C; r1d overlapped r0's last two hours), so small per-step
differences are noise; the profiling agent's quieter serial baseline was ~26,000 s. Most of the
gain is stage 1 (r1s); stage 2 adds steps 1, 2 and 4.

### Tests (stages 1-2, at `a4f352257`)

- `tests/b5_analysis` whole package: `Ran 1056 tests` / `OK (skipped=10)` (skips are the S10
  real-program classes, which need `JW_B5_S10_REAL_PROGRAMS=1`).
- `tests.b5_analysis.test_frozen_files`: OK (part of the package run; at stages 1-2 the frozen set,
  `whole_window.py` and `paper_custody.py` were untouched vs `2fdc0929d`).
- Related top-level modules (cli, cli_run, environment(_admission), capture_pipeline_era,
  gate_sensibility_rounding, reduce, controller, reason_code_partition, custody_mode_inventory,
  paper_custody, whole_window_analysis_clamp_flag, whole_window_parallel_strict,
  validate_powermetrics_fiducial): `Ran 450 tests` / `OK`.
- `python3 scripts/repin.py --check`: `PASS 16 pin families current`.
- New: `tests/b5_analysis/test_run_caches.py` (store visible in a fresh context; inert outside a
  run; a deadline hit in an isolated context is never stored; memo keys are exact and need the same
  bytes; reads still happen on a hit; exceptions never memoized; a hit is a copy) and
  `tests/b5_analysis/test_parallel_steps.py` (worker-count resolution and `--workers` flag;
  steps 1 and 2 with workers 1 vs N on extracted committed S10 members give the same records,
  registered digests, custody tree, file bytes and log counter, including a stop at a refusing
  bundle; a wall-deadline firing in a spawned worker is counted by the driver observer and nothing
  that worker fitted reaches the run store; through `dry_run.run` it is recorded as
  `tooling_refusal calibration_wall_deadline_fired`; a worker without an observer refuses with
  `calibration_deadline_observer_unavailable`).

### Tests (stage 4, at this head)

- `tests/b5_analysis` whole package: `Ran 1068 tests` / `OK (skipped=10)`.
- `tests.b5_analysis.test_frozen_files`: OK; the frozen set (and `paper_custody.py`) is unchanged
  vs `2fdc0929d`.
- 27 whole-window/mint/floor/analysis-engine/paper/cli/reduce/environment test modules
  (`tests/test_{whole_window*,mint_floor*,floor_mint*,floor_extraction,neg8*,paper_reported*,
  analysis_engine*,window_duration_margins,paper_custody,cli*,reduce,environment_admission,
  capture_pipeline_era,reason_code_partition,custody_mode_inventory}`): `Ran 962 tests` /
  `OK (skipped=5)`, at `41d7efa30`.
- `python3 scripts/repin.py --check`: `PASS 16 pin families current`.
- New/updated: `test_run_caches.ReferenceEnergyRefitTests` (one shared fit, identical result,
  including in an isolated context; a deadline hit is never stored);
  `tests/b5_analysis/test_member_pool.py` (inert outside a run, with one worker or one call;
  values and the V2 session's records identical to serial, including order, counts, grammar and
  parse flags; a raising task recomputed by the caller; a byte changed since the session's first
  read refused at consumption; on real S10 members the pooled operative summaries, session census
  and run store equal serial; a real wall deadline in a member worker reaches the observer and is
  not stored; the driver refuses a step whose member pool could not observe with
  `calibration_deadline_observer_unavailable`); `test_whole_window_analysis_clamp_flag` (the one
  `rederive` selection is the only function shipped to the pool); `test_deadline_observer`
  (the NEG-8 energy site now shares the run cache: one fit).

### Stage 4 proof

Two more full synthetic runs at `41d7efa30` (code identical to this head; later commits touch tests
and the normalizer only), same chain (manifest unchanged after every run), against the same r0
custody `/private/tmp/jwspeedtmp/cust-r0-yRVf2V`:

- **r4d** default workers (8), **r4s** `workers=1`: both records sha256
  `20c2010ab763a008865dbf4015ab1ac9c02a896596a79a251f65e500780addf8`, byte-identical to each other
  (all 449 outputs, 18,487 census rows, all restricted files equal).
- **Normalized comparison r0 vs r4d and r0 vs r4s: PASS**, with the same pre-normalization diff list:

| file (before normalization) | differing fields |
|---|---|
| reported-energy **receipt**, alpha and beta (`restricted/custody/<sha>.json`, content-addressed so renamed) | `$.validator_source_sha256` only |
| reported-energy **inventory**, alpha and beta (`restricted/custody/<sha>.json`, renamed) | `$.files[6].path`, `$.files[6].sha256` (the receipt binding) |
| `restricted/supply-census/reported-energy-alpha.json`, `-beta.json` | `$.inventory.{path,expected_sha256}`, `$.receipt.{path,expected_sha256}` |
| `B5-BLIND-DRY-RUN-RECORD.json` | step 10 alpha/beta `outputs[5..6].name/sha256` (receipt, inventory) and `outputs[7].sha256` (role census) |

All other 1,531 files (the other 446 recorded outputs, and all 1,088 restricted logs after
replacing the custody root and TMPDIR) are byte-identical before normalization; after normalization
all 1,538 are identical. The change is `module:joulewise.whole_window` in the reported-energy
validator source census; 9b's receipt is unchanged.

| step | r0 | stages 1-2 default | stage 4 default (r4d) | stage 4 workers=1 (r4s) |
|---|---:|---:|---:|---:|
| 0 | 6 | 9 | 8 | 8 |
| 1 | 134 | 43 | 34 | 150 |
| 2 | 1581 | 21 | 17 | 46 |
| 3 | 1 | 0 | 0 | 1 |
| 3b | 225 | 240 | 207 | 172 |
| 4 | 664 | 219 | 154 | 241 |
| 5 | 7191 | 4522 | 1153 | 2383 |
| 8 | 402 | 261 | 86 | 125 |
| 6 | 398 | 257 | 131 | 155 |
| 9 | 957 | 572 | 296 | 360 |
| 9b | 3002 | 730 | 384 | 468 |
| 10 | 2806 | 614 | 339 | 415 |
| 11 | 3848 | 2108 | 942 | 1346 |
| **total** | **21215** | **9596** | **3751** | **5872** |

5.7x faster than r0 with default workers (3.6x serial). The remaining serial time is mostly the
frozen reducer's own anchor LP and plist parsing inside each member, 3b's bracket evaluation
(frozen `calibration_bracketing` refit) and step 11's sensitivity passes.

## Skipped, and what needs a ruling

1. **Anchor-LP / plist-parse memo inside the reducer and fiducial (frozen).** The remaining
   `derive_powermetrics_anchor_v3` and `_powermetrics_documents` calls from `reduce.py`,
   `powermetrics_fiducial.py` and `calibration_bracketing.py` are only reachable by editing or
   patching frozen files. Skipped. (The memos above cover the calls made from non-frozen code.)
2. **Edits to `whole_window.py` / `paper_custody.py`:** ruled in by the lead (2026-11-01) and done
   as stage 4 above. Not done: `paper_custody.py` needed no edit (its replays already reach the run
   store through cli); member-parallelism beyond the session's operative re-derivation (other
   per-member loops in `_validate_row_uncached`, now a small share) is left serial.
3. **Stage 3, sharing one prepared consumption session across mint components:** not taken; the
   lead ruled it out of scope (not authentication-equivalent). In `scripts/mint_floor_artifact.py` the two sessions a component builds are not built
   from identical inputs: `_authenticated_consumption_summaries` passes `calibration_bracket_binding`
   and the drift-allowance session does not, and the common-mode session is built in
   `floor_mint_estimator.py` (censused). Sharing would need a ruling that a session's cached row
   validation is valid for a consumer with a different binding. Possible saving: up to about half of
   step 5's validations.
4. **Coarser parallel units.** Not taken: the two `sensitivity_pass` calls in step 11 and the
   per-pack bracket evaluation in 3b take authenticated `ArchiveContext`/`ArchiveHandle` objects
   (closures, read censuses that feed the record) that cannot cross a process boundary without
   re-authenticating in the worker and losing the parent's census. Step 10's two packs and step
   5's emit/mint components mutate the run state or run inside a V2 read session. The step-10
   issuer also reads `paper_reported_energy.verify_registration_ordering`, which the joined harness
   patches in the driver process only, so a worker version could not be proved on the synthetic
   chain.

## Risks

- **Cross-context cache sharing.** The isolated replay contexts now see the run's physics store
  (through cli only). An entry is a verified fit keyed by the calibration artifact's sha256 and the
  exact metadata bound, read only after the reducer's own hash checks; that is the same trust the
  main context already gave it. The read-session isolation those contexts exist for is unchanged.
- **Memo correctness rests on the key covering every input.** Both memo keys were derived by
  reading the function bodies (all metadata fields consulted after the reads are in the key). A
  later edit that makes either function read a new input must extend the key; the tests pin the
  byte-sensitivity but not future inputs.
- **`joulewise/environment_admission.py` is in the sealed inventory.** It now differs from it
  (`repin.py --check` lists it among the files differing from the sealed inventory, as `cli.py` and
  `whole_window.py` already did at base). It only matters for collection from this tree.
- **Memory.** With 8 workers each worker imports joulewise and holds its own store/memos; peak
  observed was well within 24 GB, but a smaller host should pass `--workers`.
- **Worker failure** (a crashed worker or pickling error) is not retried: the pool is shut down,
  the exception reaches `dry_run.run`, and the step is recorded as a refusal (fail closed, exit 2).
  The completed workers' logs stay in restricted custody (the counter was advanced before dispatch,
  so the driver's failure log cannot collide with them). Repeat in a new custody root, if needed
  with `--workers 1`.
- **Stage 4 member pool.** A worker's reads happen in the worker at nearly the same time as the
  serial loop's would; with the session merge, any change since the session's first read of a file
  is refused, but a file the session had not read before is bound by the worker's read, not the
  driver's (as with stage 2's per-bundle children). The pool only runs in the driver process with
  workers > 1 and is shut down with the run.
- **Code identity.** Stage 4 changes `validator_source_sha256` in the step-10 receipts, so a
  release run must use the same analysis commit as its dry run (as before).
- Timings were measured on a shared, loaded laptop (attempt C running throughout); runs were niced.
