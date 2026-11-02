VERDICT: ACCEPT

# L9-SPEEDUP-R1: cold review (lens: executes the code) by Fable 5.1

PR #620, head `fd7d91b1ff13a77deaf478418fdf0eda2c1eaf8b` (`lane/2026-11-01-l9-speedup-r1`), base
`2fdc0929d` (tag `b5/analysis`). Reviewer did not write any of this code. Worktree
`/private/tmp/jwr1rev-fable` (detached at the head) for the proof run; a second detached worktree
`/private/tmp/jwr1rev-fable-mut` for code mutants. Synthetic data only (`JW_B5_SYNTHETIC_ONLY=1`,
`TMPDIR=/private/tmp/jwr1rev-fable-tmp`, `JOULEWISE_CUSTODY_PARENT=/private/tmp/jwr1rev-fable-tmp/custparent`,
Python 3.13.18). No real-data root was read, listed or touched; pid 19107 was never signalled; the
proof run used `workers=3`.

ACCEPT because no defect was found that changes a number, an admit/refuse decision, or weakens
custody or fail-closed behaviour. The findings below are Low/Info: test-strength gaps (the shipped
code is correct, but the suite would not catch three plausible regressions), one latent
pre-existing cross-partition behaviour that the pooled path handles differently only on inputs the
capture pipeline never produces, and documentation points.

## 1. Normalizer soundness (`docs/process_traces/2026-11-01-l9-speedup-r1/normalized_compare.py`)

Read in full. What it does, checked against the code rather than the docstring:

- Loads exactly `dry-run/B5-BLIND-DRY-RUN-RECORD.json` and every file under `dry-run/restricted/`
  (logs only with `--logs`). The r0 custody tree contains nothing else (`find` on
  `cust-r0-yRVf2V`: 1538 files = record + restricted), so every recorded output is loaded.
- Replaces values only under the two keys in `SOURCE_IDENTITY_KEYS`
  (`validator_source_sha256`, `binder_source_sha256`), by text substitution, then verifies the
  substitution was exact by re-parsing and comparing with a structural `strip_identity` of the
  document (`identity_normalized_bytes`, line 127). A 64-hex value that occurs both under an
  identity key and elsewhere in the same document therefore aborts with `SystemExit`, not a PASS.
- Recomputes digests bottom-up to a fixpoint: only digests of *loaded files* are in `mapping`
  (line 134-135); any other 64-hex string (bundle digests, census row digests, index digest) is left
  alone, so a change in one of those remains a difference. It does not blanket-replace sha256s.
- Any remaining byte difference or name-set difference after normalization is FAIL (exit 1).

Mutants (copies of `/private/tmp/jwspeedtmp/cust-r0-yRVf2V` under `/private/tmp/jwr1rev-fable-tmp/mut/`,
built by `mkmut.py`, each compared against r0 with the normalizer, no `--logs`):

| mutant | perturbation | verdict | what the script printed |
|---|---|---|---|
| M1 | one digit of a float in `restricted/outputs/83d2…-projection-alpha.json` (`$.cells[0].attribution_floor.minimum_j`) | FAIL | `STILL DIFFERS: … $.cells[0].attribution_floor.minimum_j` |
| M2 | record `steps[7].status` (step 5) `ok` -> `refused` | FAIL | `STILL DIFFERS: B5-BLIND-DRY-RUN-RECORD.json $.steps[7].status` |
| M3 | one member dropped from `kept-units/16f5…-alpha.json` `$.cells.df-ph-decode-qwen3-1p7b.dropped` | FAIL | `… dropped[len]` |
| M4 | an extra file `restricted/custody/000…0.json` on the candidate side only | FAIL | `name only on one side` |
| M5 | `validator_source_sha256` changed in one receipt (gamma claim-evidence) **without** propagating derived digests | FAIL | 4 names only on one side; record `steps[11].outputs[3..5]` and `supply-census/claim-evidence-gamma.json` still differ |
| M6 | the author's legit r4d tree **plus** `"status":"PASS"` -> `"FAIL"` inside the alpha reported-energy receipt (the file whose identity hash legitimately differs) | FAIL | record `steps[13].outputs[5..7]`, `supply-census/reported-energy-beta.json` still differ |
| M7 | one hex digit of `input_census[0].sha256` in the record (a bundle digest, not a file digest) | FAIL | `STILL DIFFERS: … $.input_census[0].sha256` |
| M8 | unmodified copy of r0 (control) | PASS | |
| r0 vs r4d | author's stage-4 run | PASS | `450 normalized files; 443 were byte-identical before normalization` |

Conclusion: the normalizer cannot hide a numeric, status, membership, file-set, or non-identity
digest change, and an identity change that is not consistently propagated also fails. The only thing
it hides is a consistent change of the two named identity hashes and digests mechanically derived
from them, which is the lead's ruling.

## 2. Independent proof run (workers=3)

Chain `/private/tmp/jwspeed-r0/.scratch-s10f/tmp/chain` manifest (22,950 files):

```
$ (cd …/chain && find . -type f | sort | xargs shasum -a 256) > chain-manifest-before.txt
$ shasum -a 256 chain-manifest-before.txt
2f452dbe9212ee1fee513661d24ec57b20e4b5b42482d4553f5e59443198f8e0
```

Command:

```
TMPDIR=/private/tmp/jwr1rev-fable-tmp JOULEWISE_CUSTODY_PARENT=/private/tmp/jwr1rev-fable-tmp/custparent \
JW_B5_SYNTHETIC_ONLY=1 python3.13 <scratchpad>/drv/r1driver.py run /private/tmp/jwr1rev-fable \
  /private/tmp/jwspeed-r0/.scratch-s10f/tmp/chain /private/tmp/jwr1rev-fable-tmp/custparent/cust/run \
  /private/tmp/jwr1rev-fable-tmp/out none workers=3
```

(The driver was read first: it sets `JW_B5_S10_REAL_PROGRAMS=1`, copies the chain's
`window-index.json` into a scratch repository through `JoinedHarness`, asserts no real-custody path
in the index, pins commit dates so the scratch anchor is identical across runs, and calls
`dry_run.run(..., _runner=None, workers=3)` with the plain `StepRunner`, so the pools are used.)

Result: exit code 0, every step `ok`, wall 7249 s (host shared with the live attempt-C run, the
whole `tests/b5_analysis` suite and the mutant harness for most of that time, so timings are
upper bounds; the point of this run is the bytes, not the speed).

```
$ tail -3 /private/tmp/jwr1rev-fable-tmp/run.log
step 10 alpha ok
step 10 beta ok
step 11 - ok
$ tail -1 /private/tmp/jwr1rev-fable-tmp/out/events.jsonl
{"kind": "done", "code": 0, "wall": 7249.137478113174, ...}
```

Per-step wall time (s), from `events.jsonl`:

| step | 0 | 1 | 2 | 3 | 3b | 4 | 5 | 8 | 6 | 9 | 9b | 10 | 11 | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| this run, workers=3, loaded host | 74 | 180 | 47 | 1 | 449 | 258 | 2251 | 180 | 238 | 588 | 709 | 596 | 1658 | 7230 |
| author r0 (base, serial) | 6 | 134 | 1581 | 1 | 225 | 664 | 7191 | 402 | 398 | 957 | 3002 | 2806 | 3848 | 21215 |

Record digest:

```
$ shasum -a 256 .../cust/run/dry-run/B5-BLIND-DRY-RUN-RECORD.json  (mine)
20c2010ab763a008865dbf4015ab1ac9c02a896596a79a251f65e500780addf8
$ shasum -a 256 /private/tmp/jwspeedtmp/cust-r4d-2H9VSH/run/dry-run/B5-BLIND-DRY-RUN-RECORD.json
20c2010ab763a008865dbf4015ab1ac9c02a896596a79a251f65e500780addf8
$ shasum -a 256 /private/tmp/jwspeedtmp/cust-r4s-oQB4n1/run/dry-run/B5-BLIND-DRY-RUN-RECORD.json
20c2010ab763a008865dbf4015ab1ac9c02a896596a79a251f65e500780addf8
$ shasum -a 256 /private/tmp/jwspeedtmp/cust-r0-yRVf2V/run/dry-run/B5-BLIND-DRY-RUN-RECORD.json
416f576d4df6348730dd971cecd78d9bb9233e0aa2cbe4050e3557f4908fbea9
```

My record is byte-identical to the author's stage-4 records at default workers (r4d) and
`workers=1` (r4s), so workers=1, 3 and 8 all agree. Against r4d, `diff -rq` of `restricted/`
excluding logs: 0 differences (449 recorded outputs + census files); the 1,088 log names are
identical.

Normalizer, r0 (base) vs this run:

```
$ python3.13 normalized_compare.py /private/tmp/jwspeedtmp/cust-r0-yRVf2V/run /private/tmp/jwr1rev-fable-tmp/custparent/cust/run
files 450 450
record sha256 416f576d4df6...8fbea9 20c2010ab763...0addf8
== before normalization: differing files and fields
  only in baseline : restricted/custody/{0a9ff2e1…, b0b7419e…, e4aee4d5…, f01d6516…}.json
  only in candidate: restricted/custody/{173872b2…, e82351fe…, f49712ca…, ff062a07…}.json
  differs: B5-BLIND-DRY-RUN-RECORD.json            (steps[12..13].outputs[5..7] name/sha256)
  differs: restricted/supply-census/reported-energy-alpha.json   ($.inventory.{path,expected_sha256}, $.receipt.{path,expected_sha256})
  differs: restricted/supply-census/reported-energy-beta.json    (same four fields)
== content-addressed files present on both sides under different names (paired after normalization)
  … 2 receipts: field $.validator_source_sha256 only; 2 inventories: field $.files[6].{path,sha256} only
== after normalization
  450 normalized files; 443 were byte-identical before normalization
VERDICT: PASS (identical after normalizing source-identity hashes and their derived digests)

$ python3.13 normalized_compare.py <r0> <mine> --logs --tmp /private/tmp/jwspeedtmp/r0tmp /private/tmp/jwr1rev-fable-tmp
files 1538 1538
  1538 normalized files; 1531 were byte-identical before normalization
VERDICT: PASS (identical after normalizing source-identity hashes and their derived digests)
```

The pre-normalization diff list (every `differs:`, `only in`, `<->` and `field` line) is
line-for-line identical to the author's `/private/tmp/jwspeedtmp/norm-r0-r4d.txt`: the only leaf
field that differs is `$.validator_source_sha256` in the alpha/beta reported-energy receipts;
everything else is the receipt digest propagating into the inventory binding, the supply census
and the step-10 record rows. With `--logs`, 0 logs differ after replacing the custody root and
TMPDIR.

Chain manifest after the run:

```
$ shasum -a 256 chain-manifest-before.txt chain-manifest-after.txt
2f452dbe9212ee1fee513661d24ec57b20e4b5b42482d4553f5e59443198f8e0  chain-manifest-before.txt
2f452dbe9212ee1fee513661d24ec57b20e4b5b42482d4553f5e59443198f8e0  chain-manifest-after.txt
$ cmp chain-manifest-before.txt chain-manifest-after.txt && echo MANIFEST_IDENTICAL
MANIFEST_IDENTICAL
```

## 3. Cache and memo correctness

Files read in full: `joulewise/analysis_run_cache.py`, the memo hunks of
`joulewise/environment_admission.py` and `joulewise/cli.py`, the 4a hunk of `joulewise/whole_window.py`,
`_RunPhysicsCacheView`/`physics_cache_for`/`_effective_bound_partition` (whole_window 7600-7710), and the
reducer's cache consult/store (`reduce.py` 1527-1594, frozen, unchanged).

- **Physics store.** Key = calibration artifact sha256 inside a partition keyed by the exact
  `float.hex()` of the bundle's metadata `b_fiducial_s`. The reducer consults the entry only when
  `strict_physics`, after the artifact/raw/events hash and staleness checks, and stores only
  `max(metadata b_fiducial, fresh.b_fiducial_s)` after a verified fit; a deadline-hit fit returns
  invalid before the store line, so nothing is cached (tests `test_a_deadline_hit_*_is_never_stored`
  confirm; mutants D1/D5 below are equivalent mutants for exactly this reason).
- **Thermal-scan memo** (`_window_thermal_pressure_refusals`). Key = sha256(idle plist bytes),
  sha256(measured plist bytes), admission start/end, measured window start/end, presence flags,
  clock-anchor method, clock-stamp rows. I traced every value the scan reads after the two
  authenticated reads (lines 395-445): `parse_powermetrics_records(raw)`, `clock_anchor.method`,
  `clock_stamps`, `anchor["first_sample_end_point_epoch_s"]` (derived), and the two window scalars.
  Nothing outside the key feeds the result. Both `read_authentication_input` calls happen before
  the memo lookup (reads still registered on a hit; `test_reads_still_happen_on_a_hit`). The
  refusal tuple for a caught `(OSError, KeyError, TypeError, ValueError)` raised *after* the key is
  computed is memoized; those are deterministic parse/anchor failures of the keyed bytes (no I/O
  happens after the reads), so this is sound. An exception from the reads themselves happens
  before the key exists and is not memoized.
- **Clock-evidence memo** (`_strict_uncertainty_evidence_problems`). Key = sha256(raw plist),
  `anchor_method`, `stamp_rows`. The derivation uses `stamps` (from `stamp_rows`), `raw_records`
  (from the bytes) and `anchor_method` (dispatch, including the frozen `CLOCK_METHOD` replay); the
  structural fallback uses the same. `problems` accumulated before the memo are unaffected; the
  memoized `expected` is deep-copied in and out.
- **Run scope.** `_ACTIVE` is a process global set/restored by `analysis_run_caches`; worker
  processes enter their own; the member pool is shut down in the `finally`. Stage-2 workers run
  `cli.main` under `analysis_run_caches(workers=1)` so no nested pools. Nothing is keyed by path or
  mtime. Outside a run every memo returns `None` and `run_reduce_physics_kwargs` returns `{}`
  without reading (mutants C3, E4 killed).
- **Isolated replay contexts.** `cli._strict_problems` now imports
  `analysis_run_cache.physics_cache_for_call` under the name `physics_cache_for`; inside the driver's
  context (shared store set) it is byte-for-byte the old function; only in a fresh
  `contextvars.Context()` with no shared store does it fall back to the run store. The replays run
  outside the custody read session (`paper_custody._indexed_replay` docstring), so the extra
  `BundleReader.raw_metadata()` read in `run_reduce_physics_kwargs` does not enter any recorded
  census (and `VerifiedDigest.read_count` is not serialized into receipts; the r0-vs-r4 proof shows
  no census diffs).

Code mutants (applied one at a time in `/private/tmp/jwr1rev-fable-mut`, test run, `git checkout`
revert; harness `/private/tmp/jwr1rev-fable-tmp/codemut/mutants.py`, results `results.jsonl`):

| id | mutant | tests run | result |
|---|---|---|---|
| C1 | thermal memo key drops `admission_end_s` | `test_run_caches.ThermalScanMemoTests` | **SURVIVED** (3 tests OK) |
| C2 | clock-evidence memo key drops `anchor_method` | `test_run_caches.StrictClockEvidenceMemoTests` | **SURVIVED** (2 tests OK) |
| C3 | `memo()` returns a module-level table outside a run | `RunPhysicsStoreTests`, `ThermalScanMemoTests` | KILLED (`AssertionError: {} is not None`) |
| C5 | `physics_cache_for_call` ignores the metadata partition | `RunPhysicsStoreTests` | KILLED |
| C7 | add `RuntimeError` to the thermal scan's caught tuple | `ThermalScanMemoTests` | SURVIVED, equivalent: `_thermal_pressure_intervals_refusals` is called outside the `try`, so the test's `RuntimeError` never reaches that tuple |
| E4 | `run_reduce_physics_kwargs` active outside a run | `RunPhysicsStoreTests` | KILLED |

## 4. Pool correctness and fail-closed behaviour

Files read in full: `joulewise/b5_analysis/parallel.py`, `joulewise/analysis_member_pool.py`, the
`dry_run.py` hunks (`_parallel`, `_dispatch`, `_account_deadlines`, `_stop_at`, `_step_{1,2,4}_parallel`,
`run`), `StepRunner.run`, `RunState.{path,register,read,rehash,invoke,record}`, the serial
`step_2`/`step_4` bodies, `V2AuthenticationReadSession` (`_register`, `read`, `read_nofollow*`,
`ingest`), `observe_wall_deadline`, `_prepare` around the member loop, `_reference_energy_evidence_detail`
call sites, `_validator_source_sha256`.

- **Ordering and counters.** `_dispatch` advances `r._counter` by `len(tasks)` before dispatch;
  task i gets `first_counter + i`; results are consumed in task order; `_stop_at` resets the counter
  to `base+stop+1`, which equals the serial counter in both the "child k failed" and the
  "`require_primary_context`/`rehash` refused before child k" cases (serial raises before
  `runner.run` increments). Seed-first scheduling only changes which worker fits first; result
  order is by index. Step-2 pre-creates output directories through `s.path` (as serial would per
  task) and `_stop_at` removes the ones no surviving task needs. Step 4's program writes only
  `--out` (`extract_detection_floors.py:253` is the only mkdir/write), so `discard_after` leaves
  the tree as serial. Serial vs parallel classification code was compared line by line for steps
  1, 2, 4: identical decisions (`exception -> exit 2 code None`, `exit 0 without output -> 2`,
  `require_rereduction_matches_stored` refusal unlinks and records `exc.code`, step-4
  `classify_step4_exit` branch for branch).
- **Exceptions.** A child exception is captured by `StepRunner.run` in the worker
  (`escaped=True`) and classified exactly as serial. A worker-process failure (`future.result()`
  raising) shuts the pool down and re-raises out of `_dispatch` before the step's `try`, so the run
  loop's `except Exception` records the step as exit 2 (fail closed). In the member pool a lost
  worker (`BrokenProcessPool`) yields `MemberOutcome(ok=False, firings=0)` for every pending member,
  the pool is discarded, and each member is recomputed serially under the driver's own observer.
- **Deadline propagation.** Each worker runs `observe_wall_deadline()`; `firings` is returned in
  the result. `dispatch.collect` adds firings, flags `None` as unavailable, and merges physics only
  for a clean result; `_account_deadlines` runs in `finally` of every parallel step, adds to
  `s.deadline` and raises `OBSERVER_UNAVAILABLE`. The run loop then replaces the step's records
  with `calibration_wall_deadline_fired` / `calibration_deadline_observer_unavailable`, also when
  `run_caches.worker_observer_unavailable` was set by the member pool. Mutants D2, D3, D10, D11 all
  killed: the tests depend on the worker's *real* observer (D11 returned `firings=0` from the real
  worker and the step-closed test failed).
- **Pool shutdown.** Step pool: shut down with `wait=True` on both the normal and exception
  paths. Member pool: lives in `caches.pool`, shut down with `cancel_futures=True` when
  `analysis_run_caches` exits (end of run) or on a broken pool. Pending member futures after a
  refusal keep computing until then; they are pure (`reduce_bundle` is output-free), so this is
  waste, not a custody effect.
- **Read census (the author's stated 4b risk).** In the serial loop a member's reads register
  (identity, digest, grammar) into the caller's `V2AuthenticationReadSession` atomically with the
  read. Pooled, the worker reads inside its own fresh session, computes the value from exactly
  those bytes, and returns `(identity, sha256, grammar, read_count)` in first-read order; `consume`
  registers them through the same `_register` (first-digest and grammar enforcement, read_count
  times) at the member's serial position. The invariant that matters, "the digest in the census is
  the digest of the bytes the derivation consumed", holds in both; a byte changed since the
  session's first read is refused by `_register` exactly as a serial read would be (mutants D4,
  D12, E1 killed; test `test_a_byte_changed_since_the_first_read_is_refused_at_consumption`). The
  difference is that the driver trusts the digest reported by its own spawned child rather than
  computing it; this is already the trust model of the pre-existing `strict_validate_bundles`
  spawn pool in `whole_window.py`, whose workers' reads are not registered at all. 4b is therefore
  stricter than existing accepted practice, and I do not consider it a weakening. (Also checked:
  `strict_parse_succeeded` is a pure function of the grammar at first registration, so it is
  reproduced; `_lock` is an `RLock`, so `consume` holding it while calling `_register` is fine;
  `V2AuthenticationInputError` is a `RuntimeError` not in `_prepare`'s except tuple, so it
  propagates identically in both paths.)
- **Environment inheritance.** `multiprocessing.get_context('spawn')` on POSIX launches the child
  with the parent's current `os.environ`, `sys.path` and cwd in the preparation data, so
  `JW_B5_SYNTHETIC_ONLY`, `JW_B5_S10_REAL_PROGRAMS`, `TMPDIR`, `JOULEWISE_CUSTODY_PARENT` reach the
  workers. (Observed in the proof run: workers wrote their logs into my custody root, so cwd/env
  were right.)
- **Gate.** `_parallel` requires `type(r).run is StepRunner.run`; a profiling or test runner that
  overrides `run` stays serial, and `--workers 1` is the untouched serial code path.

| id | mutant | tests run | result |
|---|---|---|---|
| D1 | step pool merges fits from a worker whose deadline fired | `test_a_wall_deadline_in_a_worker_fails_the_step_closed` | SURVIVED, equivalent: a deadline-hit fit is never stored by the reducer, so the worker's snapshot is empty; the exclusion is belt-and-braces |
| D2 | step pool ignores a worker without an observer | `test_a_worker_without_an_observer_refuses` | KILLED |
| D3 | driver drops worker firings | `test_a_wall_deadline…`, `test_driver_records_a_worker_firing_as_calibration_wall_deadline` | KILLED (2 failures) |
| D4 | `consume` skips read-census registration | `test_member_pool.MemberPoolTests` | KILLED (3 failures) |
| D5 | member pool merges fits from a firing worker | `RealMemberTests.test_a_real_wall_deadline…` | SURVIVED, equivalent (as D1) |
| D6 | step pool assigns log counters in reverse order | `test_step_2_workers_1_and_n_are_identical` | **SURVIVED** |
| D7 | `_stop_at` keeps later tasks' files | `test_step_2_stop_at_a_refusal_leaves_serial_custody` | KILLED |
| D8 | member worker reports a raising task as `ok` | `MemberPoolTests` | KILLED |
| D10 | run loop ignores `worker_observer_unavailable` | `DriverObserverTests` | KILLED |
| D11 | step worker returns `firings=0` regardless of its observer | `test_a_wall_deadline…` | KILLED |
| D12 | `consume` registers each record once, not `read_count` times | `MemberPoolTests` | KILLED (2 failures) |
| E1 | member worker runs without a read session | `MemberPoolTests` | KILLED (3 failures) |

## 5. Frozen set

```
$ python3.13 - (intersect git diff --name-only 2fdc0929d fd7d91b1f with tests.b5_analysis.test_frozen_files.frozen_digests())
frozen count 388
changed & frozen: []
whole_window in frozen? False
```

`git diff 2fdc0929d fd7d91b1f --stat`: 16 files, 2268 insertions, 49 deletions; the only
`joulewise/` files are `analysis_member_pool.py`, `analysis_run_cache.py`, `b5_analysis/dry_run.py`,
`b5_analysis/parallel.py`, `cli.py`, `environment_admission.py`, `whole_window.py`, plus
`scripts/run_b5_analysis.py`, tests, the report and the normalizer. `paper_custody.py` and
`reduce.py` are untouched.

## Tests at the head (`/private/tmp/jwr1rev-fable`, unmodified, Python 3.13.18, `JOULEWISE_B5_ANALYSIS_WORKERS=2`)

```
$ python3.13 -m unittest tests.b5_analysis.test_frozen_files tests.b5_analysis.test_run_caches \
    tests.b5_analysis.test_parallel_steps tests.b5_analysis.test_member_pool \
    tests.b5_analysis.test_deadline_observer tests.b5_analysis.test_shared_physics_cache \
    tests.test_whole_window_analysis_clamp_flag
Ran 77 tests in 708.577s
OK

$ python3.13 -m unittest discover -s tests/b5_analysis -t .      (clean second worktree, same head)
Ran 1068 tests in 3135.020s
OK (skipped=10)
S3_PARITY_ROWS 12 PASS
S3_PIN4_NEUTRALITY 3 PASS
```

(Skips are the S10 real-program classes gated on `JW_B5_S10_REAL_PROGRAMS=1`.)

## Findings

1. **Low - test gap: memo keys' scalar inputs are untested.** Mutants C1 (drop `admission_end_s`
   from the thermal-scan key) and C2 (drop `anchor_method` from the clock-evidence key) survive
   `test_run_caches`; the memo tests only vary the raw bytes. Failure scenario: a future edit drops
   or reorders a scalar in `_thermal_scan_memo_key`; two members with identical plists but a
   different final-admission `end_s` (or a different anchor method with identical stamps) would
   share one memoized refusal tuple, changing an admit/refuse decision for the second member, and
   the suite would stay green. The shipped keys are complete (traced above). Suggested fix: a test
   that scans the same member twice with one scalar changed and asserts a miss for each scalar.
2. **Low - test gap: log-counter-to-task mapping is unpinned.** Mutant D6 (reverse counter
   assignment in `dispatch.make`) survives `test_step_2_workers_1_and_n_are_identical` because the
   test compares the tree (same set of log names) and non-log file bytes, not log contents per
   counter. Failure scenario: a regression that permutes counters leaves restricted logs whose
   names point at the wrong bundle; recorded outputs are unaffected (logs are not recorded outputs,
   and the author's proof compared all 1,088 logs byte-identically), but a custody reader would be
   misled. Suggested fix: compare `logs/*.stdout.log` bytes serial vs pooled in the test.
3. **Low - pre-existing cross-partition local cache, handled differently by the pooled path.**
   In `AuthenticatedConsumptionSession._prepare` the serial loop passes one call-local
   `physics_cache: dict[str, float]` (keyed by artifact sha256 only, no partition) to every member's
   strict validation and re-derivation (`whole_window.py` 1795, 1833, 1922); `_RunPhysicsCacheView.get`
   consults that local dict *before* the partitioned run store. The pooled worker
   (`_member_operative_summary`) uses `physics_cache_for_call({}, metadata)`, i.e. an empty local
   dict, so it reads the run store's partition for the member's own `b_fiducial_s`. Failure
   scenario: two members of one collection share a calibration artifact but carry different
   metadata `b_fiducial_s` (within the reducer's tolerance); serial (base and `--workers 1`) hands
   the second member the first member's `max(b_first, fresh)`, the pooled path refits and returns
   `max(b_second, fresh)`; the operative summary, and so a number, could differ between workers=1
   and workers>1. Why Low: the controller copies `b_fiducial_s` from the artifact
   (`controller.py:809`), so all members of one artifact share one partition unless metadata was
   edited by hand; on the synthetic chain the three artifacts each have exactly one value
   (checked: 708 bundles, 3 artifacts, 1 distinct `b_fiducial_s` each); and when it does differ the
   pooled value is the one the J2 partition design intends, the serial one being the latent bug.
   The PR's docstring claim "the serial loop's call-local dict holds only entries that are also in
   the run store" is true but does not imply equivalence, because the local dict is unpartitioned.
   Suggested disposition: defer to a lane that either partitions the local dict or asserts one
   partition per artifact per collection.
4. **Info - normalizer is broader than the PR's claim.** `SOURCE_IDENTITY_KEYS` also blanks
   `binder_source_sha256` (`paper_custody._floor_binder_source_sha256`, an `inspect.getsource`
   digest). The PR claims only `validator_source_sha256` changed, which the pre-normalization diff
   list confirms for r0 vs r4d/r4s and for my run; but a future reader running the script on a
   tree where the binder source changed would see PASS with the change visible only in the
   pre-normalization list. Suggested: print which identity keys actually differed and require the
   caller to name them (`--allow-identity validator_source_sha256`).
5. **Info - replay contexts now share state through an import alias.** `cli._strict_problems`
   imports `analysis_run_cache.physics_cache_for_call as physics_cache_for`; a reader of
   `paper_custody._indexed_replay` ("outside the custody read session") cannot see that its strict
   validations and reduces now consult the run's verified-fit store. Behaviourally sound (the store
   only short-circuits a hash-checked, deterministic refit), but worth a sentence in
   `_indexed_replay`'s docstring or in `analysis_run_cache`'s module docstring naming the three
   call sites.
6. **Info - refused-run custody differs from serial on a worker crash.** If a step-pool worker
   process dies, `dispatch` re-raises after `shutdown(wait=True)`; in-flight children finish
   writing their logs, `_stop_at` is not called, and the run loop records exit 2 with a failure log
   at counter `base+len(tasks)+1`. The run is refused (fail closed), but the restricted logs of
   children a serial run would never have started remain. Acceptable; noted for custody readers.
7. **Info - `consume` labels.** Records re-registered by `consume` carry the label
   `member derivation input <identity>`; a `V2AuthenticationInputError` raised there quotes that
   label instead of the serial read's label. Labels appear only in exception text (restricted
   stderr log of a refused step), never in a recorded output or refusal token (`RunnerResult.token`
   parses `error: <token>` lines only).

## Disposition summary

No High or Medium findings. Findings 1-3 are Low and do not change any output of the shipped
head; 4-7 are Info. Recommend ACCEPT, with findings 1-3 dispositioned to a named follow-up lane.

---

# Delta review: `1f96b8bd9` and `5f9f6cb749c538d3c4e0ce20dc5cdd576c6a45d0` (on top of fd7d91b1f)

DELTA VERDICT: ACCEPT

Reviewed cold in a third detached worktree `/private/tmp/jwr1rev-fable-delta` at `5f9f6cb74`
(`git log fd7d91b1f..origin/lane/2026-11-01-l9-speedup-r1` lists exactly these two commits).
Synthetic only; no full rerun (the synthetic chain never stops at a refusal, so the fix cannot change
its outputs; the proof above already covers the no-stop path).

## `1f96b8bd9` — `configs/gates/hazard_refusals.json` only

- `joulewise/analysis_member_pool.py` and `joulewise/analysis_run_cache.py` added to
  `scan.not_scanned` with reason `analysis` (the same reason as `analysis_engine/*`,
  `analysis_manifest*.py`). Checked against the code: both modules are inert outside
  `analysis_run_caches()`; their only raises are `TypeError`s on constructor arguments reachable
  solely from the block-5 driver and its workers. Appropriate.
- One `INTERNAL` site for `cli._strict_uncertainty_evidence_problems` raising
  `_StrictClockEvidenceMemoHit`. Checked: the raise is caught by `except _StrictClockEvidenceMemoHit`
  in the same function, which then runs the same `clock_anchor != expected` comparison on the
  memoized (deep-copied) evidence; the memo table is `None` outside a run, so the raise is
  unreachable during collection. The `protects` text is accurate. Guard digest is verified by the
  test itself.

```
$ python3.13 -m unittest tests.hazards.test_refusal_allowlist tests.b5_analysis.test_parallel_steps   (at 5f9f6cb74)
Ran 34 tests in 152.927s
OK (skipped=1)
$ python3.13 -m tests.hazards.refusal_census | tail -5
 "stale": [],
 "miscounted": [],
 "guard_changed": [],
 "scope_gaps": []
```

## `5f9f6cb74` — count worker deadline observations only for consumed tasks

The bug (merged-tree finding, MEDIUM) is real in fd7d91b1f: `_account_deadlines(s, state)` used
`dispatch`'s `WorkerDeadlineState`, which `collect()` aggregates over **every** pooled task. A task
after the refusal stop, which a serial run never starts, could add firings (step record replaced by
`calibration_wall_deadline_fired`, exit 2 instead of the serial exit 3 outcome) or an `unavailable`
flag (`calibration_deadline_observer_unavailable`). Confirmed by running the path check below against
fd7d91b1f: 13 subtests fail there, including step 4 (`22 != 4`, `21 != 3`, post-stop `None`
refusing).

### `consumed` on every path

Serial semantics to match: task i's firings reach the driver observer iff the serial loop
*started* task i, i.e. every earlier task passed and the `require_primary_context`/`rehash` before
task i passed; the stopping task itself counts (it ran), and the run loop's deadline check then
overrides its record, so the stopping task's own firing must be included.

`consumed` is set to `i+1` after the re-authentication block and before any decision on task i, in
all three functions, and the `finally` passes `results[:consumed]`:

| path | serial tasks started | `consumed` | correct |
|---|---|---|---|
| normal completion of n tasks | 0..n-1 | n (last iteration) | yes |
| refusal / exception / missing output / rereduction mismatch / step-4 non-ok record at task i | 0..i | i+1 (set before the decision) | yes |
| `require_primary_context`/`rehash` refuses before task i (i>=1) | 0..i-1 | i (left from iteration i-1; the `raise` happens before `consumed=i+1`) | yes |
| `require_primary_context`/`rehash` refuses before the pool (top of function) | none | `_dispatch` not reached, `finally` not entered | yes (serial raises at its first `invoke`) |
| `_dispatch` raises (worker process lost) | n/a | `finally` not entered; `_account_deadlines` never runs | acceptable: the run loop records the step exit 2 (tooling), fail closed, same as pre-fix |
| step 2 `s.path` refusal before the pool | n/a | returns `None`, serial fallback | yes |
| an `AnalysisRefusal` from `s.register` / `s.record` inside iteration i | 0..i | i+1 | yes (serial ran task i before registering) |

`_account_deadlines` itself: `sum(res.firings or 0 ...)` then `any(res.firings is None ...)` over the
consumed slice; a `None` among consumed still refuses `OBSERVER_UNAVAILABLE`, a `None` after the stop
no longer does. The `state` returned by `dispatch` is now ignored by all three callers (`_`).

Path check (`/private/tmp/jwr1rev-fable-tmp/delta/delta_paths.py`, mocked `_dispatch` returning
canned `ChildResult`s, `_stop_at`, `require_primary_context`, `require_rereduction_matches_stored`,
`_step_4_classify`; real `_step_{1,2,4}_parallel` and `_account_deadlines`), 9 subtests per function:
normal completion; refusal at 0; refusal at 1; rehash failure before task 1; before task 2; post-stop
`None` does not refuse; `None` at the stop task refuses; `None` before a rehash failure refuses;
exception before the loop counts nothing. Results: fd7d91b1f `FAILED (failures=3)` (13 failing
subtests across all three functions); 5f9f6cb74 `Ran 3 tests … OK`.

### Other post-stop effects

Checked everything a post-stop task can touch:

- Its logs, its output file and the empty output directories are removed by `_stop_at`/`discard_after`
  (tested at the PR level, mutant D7). `dispatch` returns only after `pool.shutdown(wait=True)`, so no
  child is still writing when `_stop_at` runs.
- It is never registered (`s.register` happens only in the consumed loop) and never recorded.
- `r._counter` is reset to the serial value.
- Its worker-process memos and physics are process-local and gone with the step pool.
- **Physics merge in `dispatch.collect()`**: a post-stop task with `firings == 0` still has its
  worker store merged into `s.physics_store`. Assessment: this cannot change a record or an exit
  code. The merged entries are verified fits (the frozen reducer stores an entry only after its
  artifact/plist/events hash checks and a successful fit), deterministic in the calibration bytes
  and the metadata partition, so they are what any later refit would compute; and after a stopping
  step the run loop sets `stopped=True` and every later step is `not_run`, so the store is never
  consulted again in that run (nothing after the step loop reads it). The only residue is state a
  serial run would not hold, for a run that is already refused. Info; a one-line comment in
  `collect()` or merging only `results[:consumed]` from the callers (keeping the seed merge, which
  the scheduling relies on) would make the equivalence explicit.
- The regression test uses `late_firing_worker`/`late_blind_worker` keyed on `GOOD[2]`'s path in
  `task.argv`, so the firing/blind task is exactly the post-stop one; `assertSameRun` compares
  records, registered digests, tree, files and counter with serial, and `firings == 0`.

### Mutants of the fix (applied in the delta worktree, run against the author's regression test
and my path check, reverted with `git checkout`)

| id | mutant | author's suite | path check |
|---|---|---|---|
| MU1 | step 2 `consumed=len(results)` (revert) | KILLED (`test_observations_after_the_stop_do_not_count`) | KILLED |
| MU2 | step 2 `consumed=i` (stop task excluded) | KILLED | KILLED (normal completion, refusal at 0/1) |
| MU3 | step 1 `consumed=len(results)` (fix absent in step 1) | **SURVIVED** | KILLED |
| MU4 | step 4 `consumed=len(results)` (fix absent in step 4) | **SURVIVED** | KILLED |
| MU5 | `_account_deadlines` ignores a `None` observer | KILLED (`test_a_worker_without_an_observer_refuses`) | KILLED |
| MU6 | `_account_deadlines` drops firings | KILLED (`test_a_wall_deadline_in_a_worker_fails_the_step_closed`) | KILLED |

### Delta findings

D1. **Low – test gap: the regression test covers step 2 only.** MU3 and MU4 (the fix missing in
    `_step_1_parallel` / `_step_4_parallel`) pass the whole `test_parallel_steps` module. Failure
    scenario: a later refactor of step 4's loop drops `consumed=i+1` and the original MEDIUM bug
    returns for exactly the step (4, alpha exit 3 with beta firing) the finding was about, with a
    green suite. The shipped fix is present and correct in all three functions (table above).
    Suggested fix for L9-SPEEDUP-FOLLOWUP: adopt the mocked-dispatch path check (9 paths × 3
    functions, 0.05 s) as `tests/b5_analysis/test_parallel_deadline_accounting.py`, or extend the
    regression test to steps 1 and 4.
D2. **Info – post-stop physics merge** (see above): harmless to records and exit codes because the
    run stops; document or restrict to consumed tasks.
D3. **Info – `WorkerDeadlineState`/`state` is now dead for the callers**; `dispatch` still builds and
    returns it. Harmless; could be removed or kept for the member pool's symmetry.

Both delta commits: ACCEPT. The PR-level verdict stands.

### Appendix: the path check used above

```python
"""Path-by-path check of `consumed` in _step_{1,2,4}_parallel with a mocked pool (synthetic, no bundles)."""
import sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, sys.argv.pop(1) if len(sys.argv) > 1 else '.')
from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.parallel import ChildResult, WorkerDeadlineState
from joulewise.b5_analysis.deadline_observer import DeadlineObserver, OBSERVER_UNAVAILABLE
from joulewise.b5_analysis.windows import AnalysisRefusal

class Fake:
    def __init__(self, root, exits, firings, rehash_fail_at=None):
        self.restricted = root; self.contexts = None; self.deadline = DeadlineObserver()
        self.exits, self.firings, self.rehash_fail_at = exits, firings, rehash_fail_at
        self.rehash_calls = 0; self.index_path = 'idx'; self.specs = {'alpha': {}, 'beta': {}}; self.stops = []
    def rehash(self):
        self.rehash_calls += 1           # call 1 is the pre-dispatch rehash; call k+1 precedes task k
        if self.rehash_fail_at is not None and self.rehash_calls - 1 == self.rehash_fail_at:
            raise AnalysisRefusal('step_input_digest_mismatch')
    def path(self, rel):
        p = self.restricted / rel; p.parent.mkdir(parents=True, exist_ok=True); return p
    def register(self, role, path): return {'name': role, 'sha256': '0' * 64}
    def read(self, role): return {}
    def record(self, step, window=None, exit_status=0, code=None, outputs=(), **kw):
        return SimpleNamespace(step=step, window=window, status='ok' if exit_status == 0 else 'refused', exit_status=exit_status)
    def dispatch(self, s, r, tasks):
        logs = self.restricted / 'logs'; logs.mkdir(exist_ok=True); results = []
        for i, (prog, argv, step, window) in enumerate(tasks):
            out, err = logs / f'{i}.out', logs / f'{i}.err'; out.write_text(''); err.write_text('')
            if self.exits[i] == 0 and '--output' in argv: Path(argv[argv.index('--output') + 1]).write_text('{}')
            if self.exits[i] == 0 and '--out' in argv: Path(argv[argv.index('--out') + 1]).write_text('{}')
            results.append(ChildResult(self.exits[i], str(out), str(err), False, self.firings[i], {}))
        r._counter = len(tasks)
        state = WorkerDeadlineState()   # as dispatch.collect() aggregates over ALL tasks (pre-fix interface)
        for res in results:
            if res.firings is None: state.unavailable = True
            elif res.firings: state.firings += res.firings
        return 0, results, state

def run(fn, exits, firings, rehash_fail_at=None):
    with tempfile.TemporaryDirectory(prefix='delta-paths-') as tmp:
        s = Fake(Path(tmp), exits, firings, rehash_fail_at); r = SimpleNamespace(_counter=0)
        jobs = [('alpha', f'run{i}', f'/nonexistent/bundle{i}') for i in range(len(exits))]
        with mock.patch.object(d, '_dispatch', s.dispatch), mock.patch.object(d, 'require_primary_context', lambda c: None), \
             mock.patch.object(d, '_stop_at', lambda *a, **k: s.stops.append(a[3])), \
             mock.patch.object(d, 'require_rereduction_matches_stored', lambda b, o: None), \
             mock.patch.object(d, '_step_4_classify', lambda s_, pack, result, outputs, code, exit_status: s_.record('4', window=pack, exit_status=exit_status)):
            try:
                out = fn(s, r, ('alpha', 'beta')) if fn is d._step_4_parallel else fn(s, r, jobs)
            except AnalysisRefusal as exc: out = exc.code
        return out, s.deadline.firings

class Paths(unittest.TestCase):
    def check(self, fn, n):
        name = fn.__name__
        with self.subTest(fn=name, path='normal completion'):
            out, f = run(fn, [0]*n, [1, 0, 2][:n]); self.assertEqual(f, sum([1, 0, 2][:n])); self.assertNotIsInstance(out, str)
        with self.subTest(fn=name, path='refusal at 0: only task 0 counts'):
            out, f = run(fn, [2] + [0]*(n-1), [4, 9, 9][:n]); self.assertEqual(f, 4)
        with self.subTest(fn=name, path='refusal at 1: tasks 0..1 count'):
            out, f = run(fn, [0, 2, 0][:n], [1, 5, 7][:n]); self.assertEqual(f, 6 if n > 1 else 1)
        with self.subTest(fn=name, path='rehash fails before task 1: only task 0 counts, refusal propagates'):
            out, f = run(fn, [0]*n, [3, 9, 9][:n], rehash_fail_at=1); self.assertEqual(out, 'step_input_digest_mismatch'); self.assertEqual(f, 3)
        if n > 2:
            with self.subTest(fn=name, path='rehash fails before task 2: tasks 0..1 count'):
                out, f = run(fn, [0]*n, [1, 1, 9], rehash_fail_at=2); self.assertEqual(out, 'step_input_digest_mismatch'); self.assertEqual(f, 2)
        with self.subTest(fn=name, path='post-stop observer None does not refuse'):
            out, f = run(fn, [2] + [0]*(n-1), [0] + [None]*(n-1)); self.assertNotEqual(out, OBSERVER_UNAVAILABLE); self.assertEqual(f, 0)
        with self.subTest(fn=name, path='observer None at the stop task refuses'):
            out, f = run(fn, [2] + [0]*(n-1), [None] + [0]*(n-1)); self.assertEqual(out, OBSERVER_UNAVAILABLE)
        with self.subTest(fn=name, path='observer None before a rehash failure refuses'):
            out, f = run(fn, [0]*n, [None] + [0]*(n-1), rehash_fail_at=1); self.assertEqual(out, OBSERVER_UNAVAILABLE)
        with self.subTest(fn=name, path='exception before the loop: nothing counted, propagates'):
            with tempfile.TemporaryDirectory() as tmp:
                s = Fake(Path(tmp), [0]*n, [5]*n); r = SimpleNamespace(_counter=0)
                def boom(*a): raise RuntimeError('pool failed')
                with mock.patch.object(d, '_dispatch', boom), mock.patch.object(d, 'require_primary_context', lambda c: None):
                    with self.assertRaises(RuntimeError):
                        fn(s, r, ('alpha', 'beta') if fn is d._step_4_parallel else [('alpha', 'x', '/nonexistent')]*n)
                self.assertEqual(s.deadline.firings, 0)
    def test_step_1(self): self.check(d._step_1_parallel, 3)
    def test_step_2(self): self.check(d._step_2_parallel, 3)
    def test_step_4(self): self.check(d._step_4_parallel, 2)

if __name__ == '__main__':
    unittest.main(argv=sys.argv[:1])
```
