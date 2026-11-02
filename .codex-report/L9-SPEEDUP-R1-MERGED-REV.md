VERDICT: ACCEPT

# L9-SPEEDUP-R1 (PR #620): merged-tree suite and adversarial pool review

Second independent reviewer. Scope: (1) the whole suite on the merged tree (gate row 2), and (2) an
adversarial concurrency and robustness review of the two process pools. Another reviewer covers
normalizer soundness, cache-key correctness and the synthetic proof run. I used synthetic data only
and read no restricted directory.

**Why ACCEPT, and what still blocks the merge.** No finding meets the REJECT bar. None can change a
number, admit something serial would refuse, hang a real run, or weaken fail-closed behaviour.
At `fd7d91b1f`, finding 1 was a failure this PR introduced, and it turned PR CI red: shard 12
failed, and fail-fast cancelled the other 11 shards. **It is fixed in `1f96b8bd9`**, which the lead
pushed and which changes only `configs/gates/hazard_refusals.json` (+3 lines). That module passes on
origin/main merged with `1f96b8bd9` (see Trees and Job 1). PR CI has not yet run the rest of the
suite, so the merge should still wait for a full green CI run on `1f96b8bd9`.

## Trees

| | sha |
|---|---|
| origin/main at review time | `f644dcd40948babb8cb3435cf3fdfb1ad4823b36` |
| PR head reviewed (`lane/2026-11-01-l9-speedup-r1`) | `fd7d91b1ff13a77deaf478418fdf0eda2c1eaf8b` |
| merged tree, the full-suite tree and this branch's base (`git merge --no-ff fd7d91b1f` onto origin/main, clean, no conflicts) | `8d14e654ea91bd3ef7b831d70a0f77ebf2f0fb25` |
| lane fix pushed by the lead (census only: `configs/gates/hazard_refusals.json` +3 lines; `git diff fd7d91b1f 1f96b8bd9` touches nothing else) | `1f96b8bd96ccbd55b07b4e7f0b5f668ae22ced3c` |
| origin/main merged with `1f96b8bd9` (`--no-ff`, clean; `git diff 8d14e654e e1e045b31` is that json file only) | `e1e045b31c344f706bfdcc19b8ad2ad992fbfaf0` |
| PR base | `2fdc0929d` (origin/main has changed no file this PR touches since then) |

This report is committed on top of `8d14e654e`, on branch `review/2026-11-01-l9-speedup-r1-merged-tree`.

## Job 1: whole suite on the merged tree

**Method.** I ran every module returned by `scripts/shard_tests.py:discover_test_modules()`
(467 modules), one process per module and at most 4 at a time. Each module ran the CI way:
`python -c "sys.path.insert(0,'scripts'); import shard_tests; raise SystemExit(shard_tests.run_units([<module>],1,1))"`.
`run_units` puts ROOT and `tests/` on `sys.path`, so `tests.test_mlx_runtime_detokenizer` imports
(`Ran 8 tests ... OK`). Environment: `TMPDIR=/private/tmp/jwr1rev-merged-tmp`, `JW_B5_SYNTHETIC_ONLY=1`,
and a fresh `JOULEWISE_CUSTODY_PARENT` per module under that TMPDIR. Python 3.14.6, macOS, M4 Air.

**First full pass (merged tree):** 467 modules, `tests=11779 failures=2 errors=18 skipped=141`.
463 modules OK and 4 FAILED:

```
tests.flags.test_flags_collect       | Ran 59 tests in 24.416s  | FAILED (errors=3)
tests.hazards.test_refusal_allowlist | Ran 23 tests in 21.996s  | FAILED (failures=2, skipped=1)
tests.test_night_agent_install       | Ran 85 tests in 755.514s | FAILED (errors=1)
tests.test_v5_block4_replay          | Ran 14 tests in 0.954s   | FAILED (errors=14)
```

**Classification.** I reran each failure on a clean origin/main worktree at `f644dcd40`, and re-ran
some on the merged tree:

| module | merged tree | clean main | merged rerun | class |
|---|---|---|---|---|
| `tests.hazards.test_refusal_allowlist` | `FAILED (failures=2, skipped=1)` | `Ran 23 tests in 20.637s` / `OK (skipped=1)` | on `e1e045b31` (origin/main + `1f96b8bd9`): `Ran 23 tests in 12.317s` / `OK (skipped=1)` | introduced at `fd7d91b1f` (finding 1; also failed PR CI run 41389315285, shard 12); **fixed in `1f96b8bd9`** |
| `tests.flags.test_flags_collect` | `FAILED (errors=3)` `ArmReadinessError: untracked pack directory: b'__pycache__'` | `Ran 59 tests in 44.669s` / `OK` | `Ran 59 tests in 47.136s` / `OK` | local environment artifact, not the PR |
| `tests.test_v5_block4_replay` | `FAILED (errors=14)`, same `__pycache__` error | `Ran 14 tests in 87.384s` / `OK (skipped=6)` | `Ran 14 tests in 102.879s` / `OK (skipped=6)` | local environment artifact, not the PR |
| `tests.test_night_agent_install` | `FAILED (errors=1)` `test_hung_grandchild_cannot_write_clock_into_next_cell` (`os.killpg` in `fixture_process`) | `Ran 85 tests in 664.003s` / `OK` | `Ran 85 tests in 650.322s` / `OK` | flaky (process-group timing under load), not the PR |

About the `__pycache__` artifact: an earlier module in my one-process-per-module order imported
`.py` files under `configs/campaigns/<pack>/`. That left ignored `__pycache__/` directories inside
committed packs, and `committed_pack_tree_sha256` then refuses those packs. After I deleted those
ignored directories, both modules pass on the merged tree. They also pass on clean main, and PR CI
did not report them. This PR touches nothing under `configs/`.

**Corrected totals.** After classification, the only failure on the merged tree `8d14e654e` is
`tests.hazards.test_refusal_allowlist` (2 failures), and it is fixed in `1f96b8bd9`. As the lead
asked, I reran only that module on origin/main merged with `1f96b8bd9` (`e1e045b31`). Its tail:

```
Ran 23 tests in 12.317s
OK (skipped=1)
SHARD SUMMARY index=1/1 modules=1 tests=23 failures=0 errors=0 skipped=1 result=PASS
```

Every other module is OK. The fix changes only that json file, so the other 466 modules' results
carry over.

PR test modules on the merged tree:

```
tests.b5_analysis.test_member_pool             | Ran 10 tests in 36.030s  | OK
tests.b5_analysis.test_parallel_steps          | Ran 10 tests in 128.975s | OK
tests.b5_analysis.test_run_caches              | Ran 13 tests in 89.774s  | OK
tests.b5_analysis.test_shared_physics_cache    | Ran 10 tests in 248.178s | OK
tests.b5_analysis.test_deadline_observer       | Ran 17 tests in 75.174s  | OK
tests.b5_analysis.test_frozen_files            | Ran 3 tests in 0.501s    | OK
tests.test_whole_window_analysis_clamp_flag    | Ran 14 tests in 92.237s  | OK
```

`python3 scripts/repin.py --check` on the merged tree: `PASS 16 pin families current`.

The appendix lists all 467 per-module tails.

**Process incident (my error; disclosed in full).** My first suite launcher had a broken throttle.
zsh's `jobs -r` inside a `cat | while read` pipeline always counted 0, so roughly all 467 modules
started at once for about 8 minutes (about 20:39 to 20:47 PST; load average peaked near 247). Pid
19107 was running at the time. I killed only processes in my own tree, identified by parent chain
and by a cwd under `/private/tmp/jwr1rev-merged*`. I never signalled 19107, and it was still
running afterwards. I discarded every result from that pass and reran the whole suite with a strict
4-lane Python throttle; all numbers above come from the rerun. **If pid 19107 is a real-data
analysis run, check it for `calibration_wall_deadline_fired` or other timing-sensitive refusals in
that window.** The 120 s wall deadline is host-dependent, and the overload could have tripped it.

## Job 2: adversarial review of the pools

Code read: `joulewise/b5_analysis/parallel.py`, `joulewise/analysis_member_pool.py`,
`joulewise/analysis_run_cache.py`, and the diff of `dry_run.py`, `scripts/run_b5_analysis.py` and
`whole_window.py` against `2fdc0929d`.

I wrote targeted tests and mutants outside the repo, in a scratch directory with
`adv_workers.py` and `test_adv_pool.py`. Nothing was committed anywhere. They ran against the
merged tree with the env vars above, with at most 4 test processes counting the suite lanes. Each
result below names the test that showed it.

### Spawn-context safety: OK

Probe: `test_spawn_environment`. A real `parallel.dispatch` ran a child program that reports its
environment. The driver was inside `without_backup_roots()` (with `JOULEWISE_BACKUP_ROOTS` set
beforehand), `relocated_custody(...)`, a `V2AuthenticationReadSession`,
`shared_instrument_calibration_physics_cache({})` and `analysis_run_caches({}, workers=4)`.

The spawned child:

- **Environment variables.** It inherits them as they were when the pool was spawned.
  - `JOULEWISE_BACKUP_ROOTS` is absent (correct: the pool is created inside `without_backup_roots`).
  - `TMPDIR`, `JW_B5_SYNTHETIC_ONLY` and `JOULEWISE_CUSTODY_PARENT` are inherited.
- **Working directory and `sys.path`.** cwd is the driver's cwd. `sys.path` is the driver's.
- **`__main__`.** It is not re-imported in any harmful way. The driver script guards on
  `__name__=='__main__'`, which is what spawn needs.
- **Run caches.** They are active in the worker with `workers=1`, so `member_map` is inert there
  (`member_map_inert: true`, `pool: None`). There are no nested pools.
- **Contextvars.** None are inherited. The window-lineage relocations come through as `{}` and no
  V2 session is active. The PR handles this correctly:
  - The physics store is re-established explicitly in `run_child` and `run_member`.
  - The member pool's read census is carried explicitly: a fresh session per task, records
    replayed into the caller's session by `consume`.
  - The relocation contextvar is set only by tests and never by the driver.
  - Child programs of steps 1, 2 and 4 do not run inside a session when run serially either
    (`StepState.invoke` opens none).

### Determinism of result order and counters: OK

- `test_workers_exceed_items_and_order` uses descending sleeps, so tasks complete in reverse order.
  Results still come back in task order, and the logs are named `0041`, `0042` and `0043` from
  `first_counter + i`.
- The driver advances `r._counter` before dispatch. `_stop_at` resets it to `base + stop + 1`, and
  `discard_after` removes the logs, outputs and pre-created empty directories of later tasks. This
  matches the serial run, which the PR's own `test_parallel_steps` checks for stop-at-refusal.
- Physics merges into the driver store run in task-index order, seeds first, and are add-only
  (`_merge` never overwrites).

### Worker crash or kill: fails closed, fast, no hang

| case | test | result |
|---|---|---|
| `os._exit` in a step-dispatch worker | `test_worker_hard_exit_fails_fast` | `BrokenProcessPool` after 0.24 s; no leftover children |
| external SIGKILL of a busy dispatch worker | `test_external_sigkill_of_a_busy_worker` | `BrokenProcessPool` after 2.56 s (2.5 s of that was the kill delay); no leftovers |
| worker crash inside `step_2` through `dry_run.run` | `test_worker_crash_inside_step_2_is_a_tooling_refusal` | run exit 2; step 2 recorded as `unclassified_refusal` (`"unclassified refusal at step 2"`, exit 2). The exception reaches the step loop's `except Exception` (`BrokenProcessPool` is a `RuntimeError`) |
| member-pool worker dies on one member | `test_crash_is_recomputed_serially` | that member comes back `ok=False`; the caller recomputes it serially at its own position; values equal serial (`[0,10,20,30,40]`); the broken pool is shut down and reset (`caches.pool=None`); no leaked processes |

Neither pool has a timeout on `future.result()`. A worker that deadlocks would hang the run. The
serial path has the same exposure, since it calls the same code in-process, so this is not a
regression. A crash or kill is detected immediately.

### Shutdown on refusal, KeyboardInterrupt and leaks

| case | test | result |
|---|---|---|
| normal completion, `dispatch` | `test_workers_exceed_items_and_order` | `pool.shutdown(wait=True)`; no children left |
| normal completion, member pool | `test_workers_exceed_items` | shut down when `analysis_run_caches` exits; no children left |
| refusal or exception inside `dispatch` | `test_worker_hard_exit_fails_fast` | `except BaseException: shutdown(wait=True, cancel_futures=True); raise` |
| SIGINT to the driver only, during `dispatch` (12 s tasks) | `test_sigint_driver_only_dispatch` | the driver waits for the running tasks, then exits (8.3 s); 0 orphans |
| SIGINT to the process group, member pool | `test_sigint_group_member_pool` | exits in 1.1 s; 0 orphans |
| SIGTERM to the driver, during `dispatch` | `test_sigterm_driver_dispatch` | **3 orphan workers survive, finish their tasks and write their outputs after the driver has died** (finding 3) |
| SIGKILL to the driver, member pool | `test_sigkill_driver_member_pool` | **3 orphans alive 30 s later.** In my first attempt, 4 orphans (3 workers and the resource tracker) sat idle for 15 minutes until I killed them (finding 3) |

Behaviour change under SIGINT: in a serial run, a SIGINT that lands inside a child program is
caught by `StepRunner.run` (`except BaseException`), and a refused record is still written. In the
parallel path, a `KeyboardInterrupt` raised while the driver waits on a future propagates out of
`run()`, and no record is written. Both outcomes are fail-closed (no record, nothing admitted).

### Memory at default workers

- `default_workers()` is `min(8, cpu-2)`, which is 8 on this 10-core host.
- `test_worker_rss`: a spawned worker reaches maxrss 49.7 MiB after importing `joulewise.cli`,
  `whole_window`, `reduce` and `scripts.extract_detection_floors`. That is about 0.4 GiB for 8
  workers before any per-task working set.
- The step pool is per-step and shut down after each step. The member pool lives from first use
  until the end of the run. The most that can coexist is 8 member workers plus 2 step-4 workers,
  and only if the member pool is first used before step 4.
- Each task carries a full snapshot of the run physics store. Those are floats keyed per
  calibration, so the snapshots are small.
- The author's real-shape synthetic runs used the default of 8 on this same 16 GB-class machine.
- No concern.

### workers > number of items: OK

- `dispatch` caps the pool at `min(workers, len(tasks))`. With 3 tasks and 8 workers it used 3
  worker processes.
- The member pool's `ProcessPoolExecutor(max_workers=workers)` spawns workers on demand. With 2
  calls and 8 workers it started 2 processes.
- `JOULEWISE_B5_ANALYSIS_WORKERS` set to a huge value is therefore bounded by the number of
  concurrent tasks.

### Is `--workers 1` the pre-PR serial path? Partly (finding 6)

Diff of `run()`, the step functions and `_prepare` against `2fdc0929d`:

- **Same as pre-PR at `workers=1`:**
  - `_parallel()` is false, so steps 1, 2 and 4 run their original loops. The only change is
    `jobs=list(s.kept_bundles())`, an in-memory generator over `s.kept`, so making it eager is
    equivalent.
  - `member_map` returns `None`. `consume(None, compute)` then calls exactly the original
    `rederive(path, authenticated_fiducial_bound_s=..., _instrument_calibration_physics_cache=physics_cache_for(physics_cache, _metadata))`.
  - The step loop's added `or run_caches.worker_observer_unavailable` is always false.
- **Different from pre-PR:** `run()` still enters `analysis_run_caches(physics_store, workers=1)`.
  The stage-1 and stage-4a caches are therefore active at `--workers 1`: the environment-admission
  and clock-evidence memos, the run physics store in isolated replay contexts and in `cli reduce`,
  and NEG-8 `reduce_bundle`.

`--workers 1` therefore isolates the pools but not the caches, and no switch turns the caches off.
The r1s and r4s proof runs cover equality at `workers=1`.

### Deadline-observer plumbing: fails closed, never cached

- **Step pool.**
  - `run_child` counts firings with a fresh `observe_wall_deadline()` in the worker.
  - `collect()` merges physics only when `firings == 0`.
  - `_account_deadlines` adds the firings to `s.deadline`. `run()` sees `deadline.firings` change
    and records `calibration_wall_deadline_fired`.
  - `firings=None` raises `calibration_deadline_observer_unavailable`.
  - The PR's `test_parallel_steps` covers this with a real `JumpingClock` firing.
- **Member pool.**
  - `test_firing_counts_and_is_not_merged`: a worker reports `firings=1` with a physics entry. The
    run observer reaches `firings == 3` for 3 tasks, and the run store stays `{'p': {}}` (nothing
    merged).
  - `test_clean_physics_merges`: with no firing, the entry merges.
  - `test_blind_worker_marks_unavailable`: `firings=None` sets `worker_observer_unavailable`, which
    `run()` turns into `calibration_deadline_observer_unavailable` for the step. The flag is never
    reset, so the refusal is sticky (fail-closed).
  - A crashed member task (`ok=False`) is recomputed in the driver under the driver's own observer.
- **Inside a worker's own store.** The reducer stores a fit only after every check passes
  (`reduce.py:1593`). A deadline-hit fit returns invalid before reaching the store, so it never
  lands in the worker store either. A later task's snapshot from the same worker cannot carry one
  back to the driver.

## Findings

1. **[HIGH for merge at `fd7d91b1f`; FIXED in `1f96b8bd9`; does not meet the REJECT bar] An
   introduced failure in `tests.hazards.test_refusal_allowlist`.**
   - Merged tree: `FAILED (failures=2, skipped=1)`. Clean main: `OK (skipped=1)`. PR CI run
     41389315285 shard 12: `MODULE FAIL tests.hazards.test_refusal_allowlist tests=23 failures=2`.
     Fail-fast then cancelled shards 1 to 11, so most of the suite never ran in the PR's CI.
   - (a) `census.differences` reports an unlisted raise site:
     `joulewise/cli.py _strict_uncertainty_evidence_problems raise _StrictClockEvidenceMemoHit`
     (line 1404, guard `a81bb345d0096d58`).
   - (b) `scope_problems` reports that `cli.py`, `environment_admission.py` and `whole_window.py`
     depend on `analysis_run_cache.py`, and `whole_window.py` depends on `analysis_member_pool.py`.
     Neither new module is scanned or listed in `not_scanned`.
   - Failure scenario: the hazard-path refusal census no longer covers code on the hazard path, so
     a future refusal site added in these modules would go uncounted. The PR cannot merge while CI
     is red.
   - Status: **fixed in `1f96b8bd9`**. That commit adds both modules to the census as `analysis`
     and lists the raise as an `INTERNAL` entry with the same guard `a81bb345d0096d58`. On
     `e1e045b31` the module passes: `Ran 23 tests in 12.317s` / `OK (skipped=1)`.
   - Remaining before merge: a full green CI run on `1f96b8bd9`. On `fd7d91b1f`, fail-fast stopped
     11 shards before they ran.

2. **[MEDIUM, conservative direction] Deadline firings and observer-unavailability are counted
   from tasks that a serial run would never have started.**
   - In `_step_1_parallel`, `_step_2_parallel` and `_step_4_parallel`, `_account_deadlines(s, state)`
     folds every task's `firings` and `unavailable`, including tasks after the stop index.
     `run()` then replaces all of the step's records with one `calibration_wall_deadline_fired`
     record (window `null`).
   - Shown for step 1 (`test_firing_in_a_task_serial_would_not_run` against
     `SerialCounterpart.test_serial_step1_same_inputs`). Bundle 0 (alpha) fails strict validation,
     and bundle 1 (beta), which runs only in parallel mode, reports a firing:
     - parallel: `{"status":"tooling_refusal","refusal":"calibration_wall_deadline_fired","window":null}`
     - serial: `{"status":"tooling_refusal","refusal":"kept_bundle_strict_validation_failed","window":"alpha"}`
   - Worst real scenario: in step 4, alpha's extraction classifies as an `outcome_class` refusal
     (a registered outcome; the run exits 3), while beta's extraction, run concurrently, hits the
     host-dependent 120 s wall deadline. The parallel run records a tooling refusal (exit 2) where
     serial records the registered outcome.
   - Why it is not REJECT: it never admits anything serial would refuse. It needs a host-dependent
     firing, and policy already treats any firing as "rerun". The cost is a lost run plus a record
     that differs from serial, which breaks the PR's "same record for every N" claim in this corner.
   - Fix: in the three `_step_*_parallel` functions, account only `results[:stop+1]` (or
     `results[:i]` on a rehash refusal). Optionally do the same for physics merges.

3. **[MEDIUM-LOW, operational] Orphaned workers when the driver dies by SIGTERM or SIGKILL.**
   - Shown above. `ProcessPoolExecutor` workers block on the call queue indefinitely after their
     parent dies; I saw idle orphans still alive after 15 minutes. Workers busy at the time finish
     their tasks.
   - Failure scenario: an operator `kill`s a real run during step 2. Up to 8 orphan workers keep
     running `reduce`, write `rereduced/...` outputs and `logs/` files into the dead run's restricted
     custody, and then stay resident. Persistent member-pool workers, with their memos, stay
     resident until killed by hand.
   - No admission impact, because a dead run writes no record. But custody changes after death, and
     a later run on a busy host competes with the orphans.
   - Fix (either or both):
     - A worker initializer that exits when `multiprocessing.parent_process().sentinel` becomes
       ready.
     - A driver SIGTERM handler that raises `SystemExit`, so the existing `finally` shutdowns run.

4. **[LOW] The member pool's workers keep the stdout/stderr file descriptors of whichever step
   created them.**
   - The pool is spawned lazily inside `StepRunner.run`'s `dup2` window, so for the rest of the run
     its workers write fd-level output into that earlier step's `logs/NNNN-*.std{out,err}.log`.
   - `test_inherited_stderr_of_persistent_pool`: output from a call made while step B's log was
     fd 2 landed in step A's log, and step B's log stayed empty.
   - Failure scenario: a numpy or Python warning raised in a step-9 member derivation is appended
     to an already-finished step-5 log. Step 9's own stderr log misses it. Logs are outside the
     record and outside `rehash`, so no decision changes, but restricted log bytes change after
     their step has closed.
   - Fix: a pool initializer that `dup2`s the driver's original fd 1/2 (or `/dev/null`) into the
     worker, or creating the pool eagerly at run start, outside any `StepRunner.run`.

5. **[LOW / info] No timeout on pool futures.**
   - A deadlocked worker hangs the run, which is the same exposure as serial (no regression).
   - A crash or kill is detected in under 3 s, and the step fails closed (`unclassified_refusal`,
     exit 2), or the member is recomputed serially.
   - A driver-only SIGINT during dispatch waits for the running children to finish their tasks.
     Under a group SIGINT this is immediate.

6. **[INFO] `--workers 1` is serial pools, not the pre-PR path.**
   - The run caches are active at every N.
   - The "a runner that overrides `StepRunner.run` stays serial" gate (`_parallel`) covers steps 1,
     2 and 4 only. The stage-4b member pool turns on whenever `workers > 1`, whatever the runner.
   - The PR report's wording ("`--workers 1` is the unchanged serial code path") should be read as
     covering the pools only.

7. **[INFO] Step-4 `s.path` ordering.** `_step_4_parallel` calls `s.path()` for both packs before
   any child runs. Serial resolves the beta path only after alpha has run and been registered. If
   the beta path were refused, the record would differ (no alpha output). The names are constants
   (`mint/extraction-{alpha,beta}.json`), so this cannot happen in practice. Step 2 handles the same
   case explicitly by falling back to serial.

## Appendix: per-module tails (merged tree `8d14e654e`, first full pass)

Format: `module | Ran line | result line`. The four FAILED lines are classified above.

```
tests.b5_analysis.test_analysed_windows_index | Ran 5 tests in 6.020s | OK (skipped=1)
tests.b5_analysis.test_archive | Ran 26 tests in 2.373s | OK
tests.b5_analysis.test_attempt_record | Ran 33 tests in 4.619s | OK
tests.b5_analysis.test_bracket | Ran 48 tests in 293.750s | OK
tests.b5_analysis.test_census_path_token | Ran 6 tests in 34.960s | OK
tests.b5_analysis.test_chain_fixture | Ran 2 tests in 1.411s | OK (skipped=1)
tests.b5_analysis.test_claim_gate_kept_quads | Ran 31 tests in 1.718s | OK
tests.b5_analysis.test_claim_replay | Ran 23 tests in 53.974s | OK
tests.b5_analysis.test_context | Ran 43 tests in 62.380s | OK
tests.b5_analysis.test_deadline_observer | Ran 17 tests in 75.174s | OK
tests.b5_analysis.test_deadline_tripwire | Ran 7 tests in 137.486s | OK
tests.b5_analysis.test_disclosures | Ran 62 tests in 5.955s | OK
tests.b5_analysis.test_dry_run | Ran 57 tests in 232.037s | OK (skipped=3)
tests.b5_analysis.test_fill_adapter | Ran 11 tests in 0.565s | OK
tests.b5_analysis.test_finalization_block5 | Ran 75 tests in 82.914s | OK
tests.b5_analysis.test_fixture_shapes | Ran 23 tests in 264.478s | OK
tests.b5_analysis.test_floor_kept_units | Ran 53 tests in 48.897s | OK (skipped=1)
tests.b5_analysis.test_frozen_files | Ran 3 tests in 0.501s | OK
tests.b5_analysis.test_gamma_flags | Ran 7 tests in 5.588s | OK
tests.b5_analysis.test_issuer | Ran 31 tests in 144.242s | OK
tests.b5_analysis.test_joined_probes | Ran 0 tests in 0.000s | OK (skipped=1)
tests.b5_analysis.test_kept_units | Ran 47 tests in 14.308s | OK
tests.b5_analysis.test_launch_lineage | Ran 4 tests in 51.440s | OK
tests.b5_analysis.test_member_pool | Ran 10 tests in 36.030s | OK
tests.b5_analysis.test_mint_kept_units | Ran 87 tests in 105.942s | OK (skipped=2)
tests.b5_analysis.test_neg8_parity | Ran 3 tests in 0.784s | OK
tests.b5_analysis.test_neg8_predicate | Ran 6 tests in 0.330s | OK
tests.b5_analysis.test_parallel_steps | Ran 10 tests in 128.975s | OK
tests.b5_analysis.test_release_equality | Ran 10 tests in 1.153s | OK (skipped=1)
tests.b5_analysis.test_removed_member_preparation | Ran 11 tests in 3.304s | OK
tests.b5_analysis.test_reported_cell | Ran 16 tests in 0.066s | OK
tests.b5_analysis.test_row_selection_context | Ran 7 tests in 48.985s | OK
tests.b5_analysis.test_run_caches | Ran 13 tests in 89.774s | OK
tests.b5_analysis.test_runtime_identity_cells | Ran 12 tests in 1.458s | OK
tests.b5_analysis.test_s10_chain_defects | Ran 34 tests in 4.244s | OK
tests.b5_analysis.test_sensitivity | Ran 36 tests in 190.065s | OK
tests.b5_analysis.test_sensitivity_guard | Ran 12 tests in 32.361s | OK
tests.b5_analysis.test_shared_physics_cache | Ran 10 tests in 248.178s | OK
tests.b5_analysis.test_sibling_pinset | Ran 24 tests in 2.292s | OK
tests.b5_analysis.test_sources_replay | Ran 36 tests in 1105.498s | OK
tests.b5_analysis.test_step4_exit_classes | Ran 26 tests in 0.010s | OK
tests.b5_analysis.test_step4_member_codes | Ran 6 tests in 0.863s | OK
tests.b5_analysis.test_step4_reason_table | Ran 8 tests in 4.834s | OK
tests.b5_analysis.test_tripwires | Ran 7 tests in 52.596s | OK
tests.b5_analysis.test_validator_context | Ran 47 tests in 182.364s | OK
tests.b5_analysis.test_windows | Ran 23 tests in 4.529s | OK
tests.external.test_km003c_monitor | Ran 13 tests in 0.491s | OK (skipped=1)
tests.external.test_km003c_parse | Ran 43 tests in 0.242s | OK
tests.flags.test_flags_catalog | Ran 6 tests in 0.010s | OK
tests.flags.test_flags_collect | Ran 59 tests in 24.416s | FAILED (errors=3)
tests.flags.test_flags_core | Ran 20 tests in 34.177s | OK
tests.flags.test_flags_exclusions | Ran 34 tests in 0.103s | OK
tests.flags.test_flags_fx_regressions | Ran 5 tests in 0.263s | OK
tests.flags.test_flags_identity_pins | Ran 6 tests in 1.148s | OK
tests.flags.test_flags_import_graph | Ran 3 tests in 0.184s | OK
tests.flags.test_flags_review_regressions | Ran 16 tests in 0.008s | OK
tests.flags.test_flags_schema | Ran 10 tests in 0.002s | OK
tests.flags.test_flags_sink | Ran 9 tests in 0.179s | OK
tests.hazards.test_arm | Ran 23 tests in 6.049s | OK
tests.hazards.test_arm_dwell_clean_run | Ran 4 tests in 0.050s | OK
tests.hazards.test_arm_identity | Ran 7 tests in 2.521s | OK
tests.hazards.test_battery | Ran 64 tests in 1.299s | OK (skipped=1)
tests.hazards.test_clock | Ran 37 tests in 0.114s | OK (skipped=1)
tests.hazards.test_contention | Ran 48 tests in 0.396s | OK (skipped=3)
tests.hazards.test_disk | Ran 8 tests in 0.001s | OK
tests.hazards.test_import_graph | Ran 6 tests in 0.912s | OK
tests.hazards.test_instrument | Ran 20 tests in 6.006s | OK
tests.hazards.test_monitor | Ran 34 tests in 16.539s | OK (skipped=1)
tests.hazards.test_monitor_p2 | Ran 6 tests in 0.030s | OK
tests.hazards.test_refusal_allowlist | Ran 23 tests in 21.996s | FAILED (failures=2, skipped=1)
tests.hazards.test_smc | Ran 12 tests in 0.001s | OK (skipped=2)
tests.hazards.test_thermal | Ran 7 tests in 0.001s | OK (skipped=1)
tests.independent_recompute.test_archives | Ran 14 tests in 13.044s | OK
tests.independent_recompute.test_auditfix | Ran 14 tests in 14.742s | OK
tests.independent_recompute.test_comparator | Ran 28 tests in 7.902s | OK
tests.independent_recompute.test_comparator_meter | Ran 13 tests in 3.288s | OK
tests.independent_recompute.test_examples | Ran 30 tests in 0.179s | OK
tests.independent_recompute.test_hygiene | Ran 6 tests in 0.705s | OK
tests.independent_recompute.test_input_gate | Ran 45 tests in 6.811s | OK
tests.independent_recompute.test_meter | Ran 9 tests in 0.582s | OK
tests.independent_recompute.test_meter_fit | Ran 5 tests in 46.738s | OK
tests.independent_recompute.test_rc_cmp10 | Ran 31 tests in 19.966s | OK
tests.independent_recompute.test_rc_cmp11 | Ran 13 tests in 12.435s | OK
tests.independent_recompute.test_rc_cmp7 | Ran 21 tests in 102.266s | OK
tests.independent_recompute.test_rc_cmp8 | Ran 27 tests in 23.843s | OK
tests.independent_recompute.test_rc_cmp9 | Ran 32 tests in 194.176s | OK
tests.independent_recompute.test_reconcile | Ran 12 tests in 3.848s | OK (skipped=3)
tests.independent_recompute.test_rehearsals | Ran 6 tests in 0.000s | OK (skipped=6)
tests.independent_recompute.test_review_fixes | Ran 38 tests in 9.493s | OK
tests.independent_recompute.test_review_probes_meter | Ran 3 tests in 16.799s | OK
tests.independent_recompute.test_round3 | Ran 30 tests in 28.980s | OK (skipped=9)
tests.independent_recompute.test_structural_rules | Ran 29 tests in 6.029s | OK
tests.test_2k_amplification | Ran 13 tests in 0.271s | OK
tests.test_acc_25g83_rev5 | Ran 13 tests in 37.390s | OK
tests.test_acc_25g83_rev6 | Ran 27 tests in 122.875s | OK
tests.test_adapters_powermetrics | Ran 3 tests in 3.206s | OK
tests.test_admit_model_panel_entry | Ran 4 tests in 0.001s | OK (skipped=4)
tests.test_agent_census_concurrency | Ran 3 tests in 14.965s | OK
tests.test_agent_identity | Ran 13 tests in 0.445s | OK
tests.test_aggregate | Ran 28 tests in 0.048s | OK
tests.test_analysis_claims | Ran 65 tests in 3.460s | OK
tests.test_analysis_engine | Ran 13 tests in 0.061s | OK
tests.test_analysis_engine_evidence_roots | Ran 3 tests in 46.390s | OK
tests.test_analysis_engine_v2_binding | Ran 9 tests in 78.345s | OK
tests.test_analysis_finalizer | Ran 18 tests in 46.698s | OK
tests.test_analysis_inputs | Ran 28 tests in 254.331s | OK (skipped=1)
tests.test_analysis_integration | Ran 116 tests in 137.148s | OK
tests.test_analysis_manifest | Ran 27 tests in 4.257s | OK
tests.test_analysis_manifest_v2 | Ran 5 tests in 0.002s | OK
tests.test_analysis_manifest_v3 | Ran 19 tests in 1.371s | OK
tests.test_analysis_multiplicity | Ran 25 tests in 1.489s | OK
tests.test_analysis_ratio | Ran 2 tests in 0.001s | OK
tests.test_analysis_ratio_integration | Ran 11 tests in 0.030s | OK
tests.test_arm_census | Ran 20 tests in 0.136s | OK
tests.test_arm_readiness | Ran 75 tests in 70.363s | OK
tests.test_arm_readiness_dry_run | Ran 12 tests in 142.805s | OK
tests.test_arm_readiness_evidence | Ran 19 tests in 47.307s | OK
tests.test_arm_readiness_evidence_author | Ran 24 tests in 267.640s | OK
tests.test_arm_readiness_evidence_packauth | Ran 27 tests in 104.823s | OK
tests.test_arm_readiness_evidence_t0 | Ran 81 tests in 1065.594s | OK
tests.test_arm_readiness_integration | Ran 13 tests in 405.778s | OK
tests.test_arm_readiness_lifecycle | Ran 70 tests in 235.539s | OK (skipped=1)
tests.test_arm_readiness_pack_digest | Ran 6 tests in 3.584s | OK
tests.test_arm_readiness_registry | Ran 6 tests in 22.350s | OK
tests.test_arm_readiness_schemas | Ran 51 tests in 0.865s | OK
tests.test_arm_retry | Ran 36 tests in 0.115s | OK
tests.test_audit_amplification | Ran 8 tests in 6.719s | OK
tests.test_audit_bundle_validation | Ran 22 tests in 9.395s | OK
tests.test_audit_cli_examples | Ran 12 tests in 0.379s | OK
tests.test_audit_clock | Ran 3 tests in 0.000s | OK
tests.test_audit_powermetrics_parser | Ran 4 tests in 0.001s | OK
tests.test_audit_reduce_degenerate | Ran 4 tests in 1.440s | OK
tests.test_audit_report | Ran 2 tests in 0.000s | OK
tests.test_audit_schema_edges | Ran 13 tests in 0.004s | OK
tests.test_authentication_io | Ran 22 tests in 1.727s | OK
tests.test_axi_analysis_manifest | Ran 23 tests in 0.240s | OK
tests.test_axi_burst_reduce | Ran 15 tests in 0.771s | OK
tests.test_axi_controller_events | Ran 7 tests in 1.559s | OK
tests.test_axi_mock_spec | Ran 11 tests in 10.644s | OK
tests.test_axi_output_identity | Ran 13 tests in 0.087s | OK
tests.test_axi_request_validation | Ran 12 tests in 0.135s | OK
tests.test_axi_schemas | Ran 17 tests in 0.008s | OK (skipped=2)
tests.test_b5_chain | Ran 25 tests in 23.761s | OK
tests.test_b5_chain_prune2 | Ran 44 tests in 37.277s | OK
tests.test_b5_chain_static_check | Ran 6 tests in 6.883s | OK
tests.test_b5_driver | Ran 41 tests in 51.257s | OK
tests.test_b5_driver_lineage_real | Ran 6 tests in 3.022s | OK
tests.test_b5_driver_p2 | Ran 46 tests in 63.379s | OK
tests.test_b5_driver_p3 | Ran 30 tests in 54.823s | OK
tests.test_b5_plan | Ran 25 tests in 7.362s | OK
tests.test_b5_seal_landing | Ran 9 tests in 3.807s | OK
tests.test_battery_float | Ran 114 tests in 166.381s | OK
tests.test_battery_float_consumers | Ran 18 tests in 49.481s | OK
tests.test_battery_float_sweep | Ran 5 tests in 4.633s | OK
tests.test_bench_replay_entrypoint | Ran 2 tests in 0.004s | OK
tests.test_bench_replay_start_drift | Ran 9 tests in 0.002s | OK
tests.test_benchmark_import | Ran 26 tests in 0.071s | OK (skipped=2)
tests.test_benchmark_import_math | Ran 10 tests in 0.233s | OK (skipped=1)
tests.test_bracket_binding_cli | Ran 19 tests in 36.078s | OK
tests.test_bridge | Ran 62 tests in 63.797s | OK
tests.test_build_capstone | Ran 2 tests in 0.000s | OK
tests.test_bundle | Ran 74 tests in 13.195s | OK
tests.test_bundle_read | Ran 82 tests in 27.709s | OK
tests.test_calibration_bracketing | Ran 95 tests in 12.314s | OK (skipped=1)
tests.test_calibration_cadence_report | Ran 9 tests in 3.710s | OK
tests.test_calibration_custody_store | Ran 7 tests in 0.425s | OK
tests.test_calibration_custody_worker | Ran 12 tests in 1.285s | OK
tests.test_calibration_dispositions | Ran 14 tests in 0.682s | OK
tests.test_calibration_exits | Ran 48 tests in 944.202s | OK
tests.test_calibration_ledger | Ran 95 tests in 12.120s | OK (skipped=1)
tests.test_calibration_ledger_custody | Ran 62 tests in 80.846s | OK
tests.test_calibration_ledger_historical_custody_report | Ran 12 tests in 14.018s | OK
tests.test_calibration_live_three_window | Ran 23 tests in 4.330s | OK (skipped=3)
tests.test_calibration_writer_crash_matrix | Ran 20 tests in 558.800s | OK
tests.test_campaign_generator_core | Ran 8 tests in 7.232s | OK
tests.test_cap_replay_harness | Ran 13 tests in 46.946s | OK
tests.test_capture_pipeline_era | Ran 10 tests in 2.416s | OK
tests.test_capture_t0_anchor_positive_control | Ran 10 tests in 101.816s | OK
tests.test_capture_t0_anchor_positive_control_g10 | Ran 3 tests in 30.727s | OK
tests.test_capture_t0_step | Ran 34 tests in 62.745s | OK
tests.test_check_gate_ledger | Ran 42 tests in 5.329s | OK
tests.test_check_paper_replay_fence | Ran 12 tests in 0.134s | OK
tests.test_check_window_provenance | Ran 44 tests in 68.077s | OK
tests.test_ci_docs_only | Ran 12 tests in 4.926s | OK
tests.test_claim_side_bound | Ran 26 tests in 0.038s | OK
tests.test_claims_index_lint | Ran 30 tests in 3.342s | OK
tests.test_claims_lint | Ran 30 tests in 3.063s | OK
tests.test_claude_bridge_mcp | Ran 16 tests in 5.925s | OK
tests.test_cli | Ran 11 tests in 2.701s | OK
tests.test_cli_run | Ran 98 tests in 53.312s | OK
tests.test_clock | Ran 3 tests in 0.002s | OK
tests.test_clock_reference | Ran 26 tests in 0.006s | OK
tests.test_codex_app_bridge | Ran 3 tests in 0.688s | OK
tests.test_codex_bridge_observer | Ran 9 tests in 7.663s | OK
tests.test_codex_mcp_server | Ran 34 tests in 11.230s | OK
tests.test_coldgate_charter_v3 | Ran 3 tests in 0.001s | OK
tests.test_coldgate_receipt | Ran 7 tests in 0.009s | OK
tests.test_collector_analysis_manifest_id | Ran 16 tests in 76.985s | OK
tests.test_controller | Ran 74 tests in 67.621s | OK
tests.test_controller_battery_float | Ran 13 tests in 5.386s | OK
tests.test_controller_g2b_attachment | Ran 23 tests in 1182.699s | OK
tests.test_controller_hazard_flags | Ran 58 tests in 315.591s | OK
tests.test_controller_retry_backoff | Ran 9 tests in 7.688s | OK
tests.test_corecaptured_loop | Ran 5 tests in 0.002s | OK
tests.test_corpus_strict_validation | Ran 3 tests in 0.299s | OK (skipped=1)
tests.test_custody_durability | Ran 5 tests in 0.029s | OK
tests.test_custody_isolation_guard | Ran 6 tests in 1.222s | OK
tests.test_custody_mode_inventory | Ran 7 tests in 111.974s | OK
tests.test_d078_reason_registry | Ran 14 tests in 0.141s | OK
tests.test_d117_contrast_v5_pack | Ran 48 tests in 48.164s | OK
tests.test_d117_decode_contrast_plan | Ran 25 tests in 45.499s | OK (skipped=1)
tests.test_d117_fixture_transport | Ran 7 tests in 1.633s | OK
tests.test_d117_floor_qwen25_1p5b_plan | Ran 22 tests in 15.461s | OK
tests.test_d117_floor_qwen25_7b_plan | Ran 20 tests in 22.644s | OK
tests.test_d117_floor_qwen3_v5_generate | Ran 22 tests in 34.329s | OK
tests.test_d117_gamma_d139a2_families | Ran 14 tests in 2.171s | OK
tests.test_d117_v3_family | Ran 5 tests in 26.680s | OK
tests.test_d138_rev6_issuance | Ran 5 tests in 6.625s | OK
tests.test_d165_dominance_closeout | Ran 59 tests in 18.443s | OK
tests.test_d165_rationale_census | Ran 10 tests in 16.145s | OK
tests.test_decisive_reference_resolution | Ran 1 test in 0.092s | OK
tests.test_dependence_sensitivity | Ran 29 tests in 6.151s | OK
tests.test_derive_estate_anchors | Ran 6 tests in 5.115s | OK
tests.test_detection_floor | Ran 131 tests in 6.076s | OK (skipped=1)
tests.test_determinism_gate | Ran 40 tests in 33.987s | OK (skipped=1)
tests.test_digest_pin_census | Ran 22 tests in 54.506s | OK
tests.test_docs_freshness | Ran 31 tests in 1.046s | OK
tests.test_doctor | Ran 9 tests in 0.009s | OK
tests.test_dominance_closeout | Ran 3 tests in 2.687s | OK
tests.test_emit_floor_mint_pinset | Ran 9 tests in 3.513s | OK (skipped=1)
tests.test_env_locks | Ran 3 tests in 0.001s | OK (skipped=1)
tests.test_envelope_gate | Ran 27 tests in 18.348s | OK
tests.test_environment | Ran 32 tests in 0.054s | OK
tests.test_environment_admission | Ran 2 tests in 0.335s | OK
tests.test_epoch_continuation | Ran 68 tests in 91.594s | OK
tests.test_epoch_continuation_stale_pin | Ran 6 tests in 9.704s | OK
tests.test_epoch_equivalence_check | Ran 29 tests in 20.632s | OK
tests.test_evidence_arm_sequence | Ran 1 test in 7.383s | OK
tests.test_evidence_night | Ran 168 tests in 557.021s | OK
tests.test_experiment | Ran 39 tests in 11.930s | OK
tests.test_family_marker | Ran 29 tests in 9.159s | OK
tests.test_finalize_analysis_manifest | Ran 13 tests in 41.927s | OK
tests.test_fixture_orphan_census | Ran 14 tests in 0.325s | OK
tests.test_floor_extraction | Ran 145 tests in 18.438s | OK (skipped=2)
tests.test_floor_mint_estimator | Ran 38 tests in 23.989s | OK
tests.test_floor_mint_pinsets_schema | Ran 2 tests in 0.001s | OK
tests.test_g10_clock_step_control | Ran 54 tests in 0.676s | OK (skipped=1)
tests.test_g2a_calibration_attachment | Ran 10 tests in 27.909s | OK
tests.test_gamma_unit_roster_guard | Ran 1 test in 0.446s | OK
tests.test_gate_prune_integration | Ran 7 tests in 1.901s | OK
tests.test_gate_sensibility_rounding | Ran 13 tests in 0.012s | OK
tests.test_gen_derivation_night | Ran 50 tests in 30.751s | OK
tests.test_gen_evidence_night | Ran 10 tests in 8.239s | OK
tests.test_gen_g2_phase_d | Ran 19 tests in 26.465s | OK
tests.test_gen_g2a_window | Ran 16 tests in 12.277s | OK
tests.test_gen_state | Ran 44 tests in 3.599s | OK
tests.test_generate_g2a_probe_inputs | Ran 30 tests in 1.863s | OK (skipped=1)
tests.test_generate_matrix | Ran 18 tests in 3.585s | OK
tests.test_generator_head_pin_relation | Ran 11 tests in 48.139s | OK
tests.test_gensuite | Ran 25 tests in 12.493s | OK
tests.test_git_fixture_hygiene | Ran 7 tests in 0.023s | OK
tests.test_git_fixture_maintenance | Ran 5 tests in 20.829s | OK
tests.test_harvest_b5_p2harv | Ran 48 tests in 88.024s | OK (skipped=4)
tests.test_harvest_b5_p3harv | Ran 48 tests in 47.772s | OK
tests.test_harvest_b5_rehearsal_compare | Ran 1 test in 0.000s | OK (skipped=1)
tests.test_harvest_b5_sources | Ran 55 tests in 1.784s | OK
tests.test_harvest_b5_trigger_scope | Ran 28 tests in 219.617s | OK
tests.test_harvest_b5_window | Ran 208 tests in 599.546s | OK (skipped=24)
tests.test_harvest_g2a_window | Ran 63 tests in 116.916s | OK
tests.test_harvest_v5_g2b_window | Ran 28 tests in 15.080s | OK
tests.test_harvest_v5_qualification | Ran 9 tests in 7.748s | OK
tests.test_harvest_window | Ran 37 tests in 24.116s | OK
tests.test_hazard_neg8_mint_verdicts | Ran 14 tests in 6.581s | OK
tests.test_hazard_whole_window_verdict | Ran 20 tests in 32.442s | OK
tests.test_identity_pins | Ran 42 tests in 16.505s | OK
tests.test_idle_admission | Ran 32 tests in 4.275s | OK
tests.test_idle_dependence | Ran 15 tests in 0.047s | OK
tests.test_install_magistrate_watchdog | Ran 10 tests in 7.980s | OK
tests.test_install_night_agent | Ran 67 tests in 95.095s | OK
tests.test_interfaces | Ran 5 tests in 0.047s | OK
tests.test_issue_calibration_acceptance_generation | Ran 156 tests in 347.474s | OK
tests.test_issue_dg071_dg075_statistics | Ran 32 tests in 3.995s | OK (skipped=1)
tests.test_issue_g2a_prefill_prompt_pin | Ran 31 tests in 12.040s | OK
tests.test_issue_p8_pin_delta | Ran 5 tests in 1.953s | OK
tests.test_issuer_corpus_root | Ran 15 tests in 19.087s | OK
tests.test_kernel_clock | Ran 4 tests in 0.001s | OK
tests.test_kv_size | Ran 14 tests in 0.012s | OK
tests.test_land_window_records | Ran 1 test in 1.290s | OK
tests.test_launch_context_no_qos_override | Ran 1 test in 0.011s | OK
tests.test_launch_window | Ran 39 tests in 1222.069s | OK
tests.test_launch_window_realization_recheck | Ran 20 tests in 12.881s | OK
tests.test_launcher_argv_regression | Ran 3 tests in 0.004s | OK
tests.test_live_hw_optin | Ran 4 tests in 0.191s | OK
tests.test_load_transition_alignment | Ran 13 tests in 0.427s | OK
tests.test_magistrate_watchdog | Ran 155 tests in 2.870s | OK
tests.test_magistrate_watchdog_b6 | Ran 9 tests in 0.082s | OK
tests.test_magistrate_watchdog_cli | Ran 7 tests in 12.512s | OK
tests.test_magistrate_watchdog_span | Ran 24 tests in 0.101s | OK
tests.test_magistrate_watchdog_yield | Ran 20 tests in 6.776s | OK
tests.test_measurement_liveness | Ran 32 tests in 0.313s | OK
tests.test_microdelta_generate_configs | Ran 4 tests in 0.064s | OK
tests.test_midcampaign_cure_generation_docs | Ran 2 tests in 0.001s | OK
tests.test_mint_analysis_admission | Ran 8 tests in 14.362s | OK
tests.test_mint_floor_artifact | Ran 42 tests in 8.606s | OK
tests.test_mint_floor_artifact_generalized | Ran 84 tests in 93.468s | OK (skipped=2)
tests.test_mint_floor_artifact_generalized_d165 | Ran 2 tests in 3.154s | OK
tests.test_mint_floor_v2_config_set | Ran 9 tests in 8.114s | OK (skipped=1)
tests.test_mint_policy_resolver_guard | Ran 1 test in 0.039s | OK
tests.test_mlx_runtime | Ran 43 tests in 0.030s | OK
tests.test_mlx_runtime_detokenizer | Ran 8 tests in 0.015s | OK
tests.test_mock_adapters | Ran 57 tests in 0.185s | OK
tests.test_model_panel | Ran 10 tests in 0.005s | OK
tests.test_modularity | Ran 10 tests in 0.567s | OK
tests.test_neg8_corpus_cap | Ran 19 tests in 90.038s | OK
tests.test_neg8_survivors | Ran 89 tests in 156.411s | OK
tests.test_network_time_off | Ran 15 tests in 0.564s | OK
tests.test_night_agent_install | Ran 85 tests in 755.514s | FAILED (errors=1)
tests.test_night_gate | Ran 112 tests in 1.739s | OK
tests.test_night_kinds | Ran 15 tests in 123.713s | OK
tests.test_night_plan_writer | Ran 10 tests in 0.020s | OK
tests.test_node_client | Ran 20 tests in 7.226s | OK
tests.test_node_worker | Ran 34 tests in 2.764s | OK
tests.test_node_worker_subprocess | Ran 1 test in 3.021s | OK
tests.test_nvidia_node_integration | Ran 12 tests in 14.775s | OK
tests.test_nvidia_smi | Ran 16 tests in 0.043s | OK
tests.test_p2038_production_path | Ran 8 tests in 421.481s | OK
tests.test_p2_ctl_auxiliary | Ran 2 tests in 1.476s | OK
tests.test_p2_ctl_calibration | Ran 17 tests in 79.228s | OK
tests.test_p2_ctl_cli | Ran 8 tests in 2.412s | OK
tests.test_p2_ctl_guard_probe | Ran 8 tests in 46.746s | OK
tests.test_package_bundle_pack | Ran 19 tests in 4.202s | OK
tests.test_paper_anchor_correction_quantified | Ran 12 tests in 0.148s | OK
tests.test_paper_build | Ran 5 tests in 0.301s | OK (skipped=2)
tests.test_paper_comparison_contract | Ran 14 tests in 0.003s | OK
tests.test_paper_comparison_placements | Ran 21 tests in 21.883s | OK
tests.test_paper_custody | Ran 33 tests in 72.333s | OK
tests.test_paper_excursion_decomposition | Ran 13 tests in 0.134s | OK
tests.test_paper_first_use_ledger | Ran 11 tests in 2.937s | OK
tests.test_paper_rendering | Ran 6 tests in 3.933s | OK
tests.test_paper_rendering_v5 | Ran 7 tests in 7.785s | OK
tests.test_paper_renumber_refs | Ran 3 tests in 0.344s | OK
tests.test_paper_replay_fence | Ran 11 tests in 0.293s | OK (skipped=1)
tests.test_paper_reported_energy | Ran 30 tests in 6.685s | OK
tests.test_paper_round7_artifacts | Ran 69 tests in 10.437s | OK (skipped=1)
tests.test_paper_successor_migration | Ran 10 tests in 0.679s | OK
tests.test_paper_terms_lint | Ran 16 tests in 1.861s | OK
tests.test_partial_record_enclosure | Ran 14 tests in 11.857s | OK
tests.test_phase_share | Ran 13 tests in 0.011s | OK
tests.test_pipeline_smoke_tail | Ran 4 tests in 8.677s | OK (skipped=1)
tests.test_powermetrics | Ran 61 tests in 17.241s | OK
tests.test_powermetrics_fiducial | Ran 76 tests in 150.263s | OK
tests.test_preflight | Ran 9 tests in 1.233s | OK
tests.test_preregistration_chain_digest | Ran 8 tests in 0.020s | OK
tests.test_prewindow_check | Ran 13 tests in 14.979s | OK
tests.test_promote_calibration_candidate | Ran 12 tests in 2.572s | OK
tests.test_publication_privacy | Ran 8 tests in 0.122s | OK
tests.test_quick_suite | Ran 15 tests in 0.431s | OK
tests.test_quiet_admission | Ran 12 tests in 0.065s | OK
tests.test_quiet_guard | Ran 87 tests in 2.813s | OK
tests.test_quiet_guard_process | Ran 20 tests in 0.002s | OK (skipped=1)
tests.test_quiet_predicate_campaign | Ran 167 tests in 19.580s | OK (skipped=4)
tests.test_r4_acceptance_oracle | Ran 10 tests in 3.900s | OK
tests.test_reason_code_partition | Ran 3 tests in 14.002s | OK
tests.test_reauthor_clean | Ran 21 tests in 44.926s | OK
tests.test_receipt_histsem | Ran 74 tests in 2630.699s | OK (skipped=1)
tests.test_receipt_oracle | Ran 3 tests in 0.422s | OK
tests.test_receipt_provenance_analyzer | Ran 8 tests in 0.633s | OK
tests.test_reduce | Ran 132 tests in 471.662s | OK
tests.test_rehearse_t0_unattended | Ran 8 tests in 5.888s | OK
tests.test_reissue_calibration_acceptance | Ran 6 tests in 0.114s | OK
tests.test_render_results_fills | Ran 24 tests in 0.804s | OK
tests.test_render_results_fills_live | Ran 4 tests in 0.879s | OK
tests.test_repin | Ran 47 tests in 52.301s | OK
tests.test_report | Ran 16 tests in 2.881s | OK (skipped=9)
tests.test_reserve_calibration_hazard | Ran 18 tests in 118.170s | OK
tests.test_results_fill_adapter | Ran 6 tests in 0.142s | OK
tests.test_results_prose_template | Ran 16 tests in 4.872s | OK
tests.test_rev6_custody_plan_id | Ran 9 tests in 16.001s | OK (skipped=1)
tests.test_rev6_prior_start_plan_id | Ran 3 tests in 0.230s | OK
tests.test_revision6_seal | Ran 3 tests in 0.988s | OK
tests.test_revision_five_b_readers | Ran 2 tests in 0.007s | OK
tests.test_rpt001_report_slice | Ran 23 tests in 5.937s | OK (skipped=3)
tests.test_rpt002_related_work | Ran 9 tests in 0.004s | OK
tests.test_run_campaign | Ran 267 tests in 322.106s | OK (skipped=1)
tests.test_run_campaign_hazard_flags | Ran 46 tests in 19.074s | OK
tests.test_run_campaign_max_blocks | Ran 22 tests in 4.646s | OK
tests.test_run_campaign_p2_rc | Ran 35 tests in 33.764s | OK
tests.test_run_d165_closeout_from_custody | Ran 35 tests in 205.589s | OK
tests.test_run_night | Ran 292 tests in 149.197s | OK
tests.test_run_night_probe_cadence | Ran 6 tests in 1.798s | OK
tests.test_run_night_probe_worker_cadence | Ran 1 test in 0.437s | OK
tests.test_s0_blocked_enumeration | Ran 1 test in 4.612s | OK
tests.test_s0_line_audit_guard | Ran 5 tests in 2.426s | OK
tests.test_salvage_dangler | Ran 24 tests in 0.157s | OK (skipped=1)
tests.test_sample_quiet_predicate_evidence | Ran 96 tests in 38.485s | OK (skipped=1)
tests.test_sampler_teardown | Ran 10 tests in 0.156s | OK
tests.test_scheduler_gates | Ran 40 tests in 3.256s | OK
tests.test_schemas | Ran 42 tests in 0.159s | OK (skipped=1)
tests.test_scored_ownership_forgery | Ran 10 tests in 4.870s | OK (skipped=4)
tests.test_scored_packer | Ran 41 tests in 20.486s | OK
tests.test_scored_packer_fuzz | Ran 6 tests in 0.000s | OK (skipped=6)
tests.test_scored_packer_stress | Ran 3 tests in 25.638s | OK (skipped=2)
tests.test_scored_reduce | Ran 64 tests in 121.766s | OK (skipped=1)
tests.test_scored_registration | Ran 3 tests in 0.002s | OK
tests.test_scored_roster_checker | Ran 24 tests in 5.344s | OK
tests.test_sealed_bundle_compatibility | Ran 4 tests in 1.085s | OK
tests.test_select_g2a_prefill_length | Ran 8 tests in 0.063s | OK
tests.test_select_outcome_branches | Ran 5 tests in 0.305s | OK
tests.test_shard_split | Ran 33 tests in 0.826s | OK
tests.test_shard_tests | Ran 6 tests in 2.048s | OK
tests.test_single_count_discipline_census | Ran 6 tests in 25.043s | OK
tests.test_single_count_discipline_matrix | Ran 12 tests in 10.298s | OK
tests.test_size_b5_window | Ran 14 tests in 1.900s | OK
tests.test_ssh_transport | Ran 8 tests in 0.001s | OK
tests.test_suite | Ran 26 tests in 0.037s | OK
tests.test_suite_control_parity | Ran 2 tests in 0.003s | OK
tests.test_summarize_g2a_prefill_probe | Ran 19 tests in 1.751s | OK (skipped=1)
tests.test_supersession_cross_consumer | Ran 15 tests in 0.093s | OK
tests.test_t0_anchor_positive_control | Ran 33 tests in 195.781s | OK
tests.test_t0_rehearsal | Ran 35 tests in 32.737s | OK
tests.test_uncertainty_evidence | Ran 58 tests in 52.450s | OK
tests.test_uncertainty_p2029 | Ran 27 tests in 8.537s | OK
tests.test_v5_arm_abort | Ran 17 tests in 7.984s | OK
tests.test_v5_block4_clock | Ran 10 tests in 5.386s | OK
tests.test_v5_block4_composed | Ran 2 tests in 1.716s | OK
tests.test_v5_block4_replay | Ran 14 tests in 0.954s | FAILED (errors=14)
tests.test_v5_block4_x1 | Ran 13 tests in 11.386s | OK
tests.test_v5_block4_x10 | Ran 16 tests in 1.298s | OK
tests.test_v5_block4_x12a | Ran 32 tests in 7.549s | OK
tests.test_v5_block4_x12b | Ran 11 tests in 70.720s | OK
tests.test_v5_block4_x16 | Ran 8 tests in 1.575s | OK
tests.test_v5_block4_x2 | Ran 15 tests in 37.802s | OK
tests.test_v5_block4_x4 | Ran 7 tests in 9.651s | OK
tests.test_v5_block4_x6 | Ran 15 tests in 14.641s | OK
tests.test_v5_block4_x7 | Ran 33 tests in 8.460s | OK
tests.test_v5_block4_x9 | Ran 9 tests in 58.786s | OK
tests.test_v5_pack_regen | Ran 7 tests in 3.033s | OK
tests.test_v5_pack_rehearsal | Ran 15 tests in 9.179s | OK
tests.test_v5_qualification_plan | Ran 54 tests in 21.798s | OK
tests.test_v5_s1_desk_closeout | Ran 7 tests in 8.710s | OK
tests.test_v5_s1_qualification | Ran 23 tests in 22.767s | OK
tests.test_validate_gate_packet | Ran 35 tests in 3.384s | OK
tests.test_validate_powermetrics_fiducial | Ran 13 tests in 55.422s | OK
tests.test_validate_powermetrics_fiducial_derivation_only | Ran 27 tests in 379.404s | OK
tests.test_validate_powermetrics_fiducial_hazard | Ran 11 tests in 303.379s | OK
tests.test_validate_powermetrics_fiducial_p2_vpf | Ran 15 tests in 338.257s | OK
tests.test_vllm_runtime | Ran 11 tests in 0.046s | OK
tests.test_whole_window | Ran 26 tests in 2.174s | OK
tests.test_whole_window_analysis_clamp_flag | Ran 14 tests in 92.237s | OK
tests.test_whole_window_inverted_corner_clamp | Ran 34 tests in 119.269s | OK
tests.test_whole_window_parallel_strict | Ran 8 tests in 0.344s | OK
tests.test_whole_window_selection | Ran 57 tests in 199.149s | OK
tests.test_window_duration_margins | Ran 42 tests in 15.521s | OK
tests.test_window_env_allowlist | Ran 4 tests in 0.019s | OK
tests.test_window_lineage | Ran 52 tests in 102.082s | OK
tests.test_window_lineage_idempotent | Ran 5 tests in 2.604s | OK
tests.test_window_status_guard | Ran 11 tests in 3.399s | OK
tests.test_workload_profile | Ran 7 tests in 0.003s | OK
tests.test_workload_sizing | Ran 8 tests in 0.001s | OK
tests.test_workloads | Ran 17 tests in 0.029s | OK
tests.test_write_b5_identity_pins | Ran 17 tests in 0.275s | OK (skipped=1)
tests.test_write_derivation_night_inputs | Ran 16 tests in 8.102s | OK
tests.test_zero_capture_facts | Ran 5 tests in 0.013s | OK
tests.twins.test_engine_twin | Ran 12 tests in 0.113s | OK
tests.twins.test_engine_twin_comparison | Ran 14 tests in 0.574s | OK
tests.twins.test_harvest_twin | Ran 16 tests in 0.002s | OK
tests.twins.test_harvest_twin_comparison | Ran 7 tests in 6.146s | OK
```
