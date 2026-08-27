# T26 stream S5 — test-reliability batch (2026-08-26/27)

Four kernel rows plus one unregistered CI flake, worked as one stream on branch
`fix/ci-reliability-batch` and landing as PR #203. This file is the custody
record: what was reproduced, what was cured, what was verified, and — where a
link in a causal chain is inferred rather than observed — which link.

Bench for every local command below:
`/Users/edr/code/JouleWise/.venv/bin/python` (CPython 3.13.1, pytest 9.1.1),
worktree `/Users/edr/code/JouleWise-wt-s5-ci-reliability`, macOS arm64,
git 2.50.1, `mlx` installed (`mlx/core.cpython-313-darwin.so`).

Row dispositions land in the same PR as the code: A85, A88 and A89 are removed
from `docs/process/state_kernel.json` and written into the TASK_QUEUE completed
table; A86 stays live with a rewritten `status_note`. Until that PR merges, the
rows are still live on `main` — a statement here that a row "closes" is a
statement about this PR, not about any earlier commit.

---

## A85 — MLX-ACID-SIGABRT-01 (CURED HERE)

### Reproduced

With the four `@unittest.skip("CRASH-BLOCKED: ...")` decorators removed:

```
$ .venv/bin/python -m pytest tests/test_arm_readiness_evidence_t0.py -k acid
collected 34 items / 30 deselected / 4 selected
tests/test_arm_readiness_evidence_t0.py FFatal Python error: Aborted
  File "joulewise/adapters/mlx_runtime.py", line 1159 in _mlx_metal_memory
  File "joulewise/adapters/mlx_runtime.py", line 772 in _memory_snapshot
  File "joulewise/adapters/mlx_runtime.py", line 162 in prepare
  File "joulewise/identity_pins.py", line 1269 in _runtime_probe_metadata
  ...
exit 134
```

Each of the four run **alone** fails and does not abort — one `pytest -k
<name>` invocation per test, four separate interpreters, `1 failed, 33
deselected` each time. Those failures are A84 / FIXTURE-MODERNIZATION-01
(fixture R1 schemas), not this row. The abort needs a *prior* test in the same
interpreter.

### Root cause

`mlx.core` is a nanobind C-extension. Running its native initializer twice in
one interpreter calls `abort()`, and no Python code can catch that. Isolating
the second import — run the first ACID test, then re-import `mlx.core` in the
same interpreter — prints the diagnostic that pytest's `Fatal Python error`
banner swallows:

```
RuntimeWarning: nanobind: type 'Device' was already registered!
RuntimeWarning: nanobind: type 'DeviceType' was already registered!
Critical nanobind error: refusing to add duplicate key "cpu" to enumeration
"mlx.core.DeviceType"!            -> abort()
```

The second execution happens because the test helper `author_environment`
injected its synthetic `mlx_lm` with
`mock.patch.dict(sys.modules, {"mlx_lm": ...})`. `patch.dict.__exit__` restores
by `in_dict.clear(); in_dict.update(snapshot)`, where the snapshot was taken on
entry. `mlx` and `mlx.core` are imported **lazily inside** that context by
`mlx_runtime._mlx_metal_memory`, so they are not in the snapshot and are
**evicted** from `sys.modules` on exit. The next test's
`importlib.import_module("mlx.core")` then re-executes the already-loaded
shared object.

### Cure

Code-side on both halves — the row's fence forbids containing a process-level
abort with a skip marker.

- **Adapter** (`joulewise/adapters/mlx_runtime.py`): `_resolve_mlx_core()`
  keeps a module-scope reference to the loaded extension and serves it when
  `sys.modules` no longer has one, so no eviction can trigger a second native
  initialization. Three rules make that reference safe:
  - `sys.modules` stays authoritative while it holds an entry, so a test
    stand-in still answers for as long as it is installed;
  - only a **genuine extension** is remembered (`_is_loaded_extension` checks
    for `importlib.machinery.ExtensionFileLoader`), so a `ModuleType` stand-in
    cannot outlive its own `finally` block and silently supply memory numbers
    to real evidence — and, symmetrically, a real extension imported by
    *another* component (`mlx_lm.load()` runs before the memory snapshot) is
    remembered too, which a "only what I imported myself" rule would have
    missed;
  - a `None` value under `"mlx.core"` is Python's blocked-import sentinel and
    still raises, so a caller forcing the unavailable path still gets
    `mlx_core_not_found`.
- **Test helper** (`tests/test_arm_readiness_evidence_t0.py`):
  `author_environment` patches and restores the single `mlx_lm` key instead of
  snapshotting and rebuilding all of `sys.modules`.

### Acceptance

| acceptance evidence | status |
| --- | --- |
| the abort no longer kills the interpreter under pytest at the four ACID tests | with the skips temporarily removed the run reaches a normal summary: exit 1, `3 failed, 1 skipped, 32 deselected` (the skip is the Darwin boot-session `skipTest` when the sysctl is unavailable in the sandbox), no abort. Pre-fix the same command was exit 134. Pinned deterministically by the five regressions below |
| the four CRASH-BLOCKED skips narrowed to their remaining structural cause (A84) with reason strings updated | all four now read `STRUCTURAL-BLOCKED: fixture R1 schemas require FIXTURE-MODERNIZATION-01 (A84)` and stay skipped. `STRUCTURAL-BLOCKED:` is the canonical prefix in `tests/test_s0_blocked_enumeration.py`'s census, whose counts move 17/4 → 21/0 |
| full-suite pytest collection completes with zero deselection | `pytest --collect-only -q` → `4006 tests collected`, no collection error |

This row was never sufficient for the four ACID tests; A84 is what they still
need. No A84 fixture work was undertaken here.

### Regressions (each red before its fix, green after)

| test | red-before |
| --- | --- |
| `test_arm_readiness_evidence_t0.py::…::test_mlx_metal_memory_reuses_cached_core_after_module_eviction` | `AssertionError: 2 != 1` (extension initialised twice) |
| `test_arm_readiness_evidence_t0.py::…::test_author_environment_preserves_modules_imported_inside_context` | `KeyError: '_joulewise_author_environment_sentinel_…'` |
| `test_mlx_runtime.py::MlxCoreResolutionTests::test_sys_modules_standin_never_enters_the_extension_cache` | `AssertionError: <module 'mlx.core'> is not None` |
| `test_mlx_runtime.py::MlxCoreResolutionTests::test_blocked_import_sentinel_is_honoured_over_the_cache` | `AssertionError: None is not <module 'mlx.core' (ExtensionFileLoader …)>` |
| `test_mlx_runtime.py::MlxCoreResolutionTests::test_extension_imported_by_another_component_is_remembered` | `AssertionError: None is not <module 'mlx.core' (ExtensionFileLoader …)>` |

### Residual risk, recorded not fixed

The remembered reference lives in the adapter module's own global. A
hypothetical `importlib.reload(joulewise.adapters.mlx_runtime)` would reset it
and re-arm the fatal re-import. Nothing in `joulewise/`, `scripts/` or `tests/`
reloads any module (`grep -rn "importlib.reload"` → no matches), so no
reachable path was found; a process-stable holder module would close it if one
ever appears.

---

## A86 — CALEXITS-EVIDENCE-BYTES-01 (NOT REPRODUCIBLE AT THIS BENCH; STAYS LIVE)

`test_logical_producer_delay_preserves_exact_evidence_bytes` **passes** here,
repeatedly, at branch head, inside a full-module run, and at the exact commit
the row names as the pristine-main reproduction (`74794af`):

```
$ .venv/bin/python -m pytest tests/test_calibration_exits.py \
      -k preserves_exact_evidence_bytes -q       # branch head, 3 consecutive runs
1 passed, 45 deselected, 4 subtests passed in 37.48s
1 passed, 45 deselected, 4 subtests passed in 37.56s
1 passed, 45 deselected, 4 subtests passed in 37.29s

$ .venv/bin/python -m pytest tests/test_calibration_exits.py -q     # whole module
46 passed, 208 subtests passed in 399.24s (0:06:39)

$ git worktree add --detach <tmp> 74794af && cd <tmp>
$ .venv/bin/python -m pytest tests/test_calibration_exits.py \
      -k preserves_exact_evidence_bytes -q
1 passed, 33 deselected, 4 subtests passed in 37.68s
```

The test compares two independently-captured witness runs byte-for-byte. Each
capture builds a fresh `TemporaryDirectory` with a random suffix, so **any**
temp-path bytes reaching `instrument_evidence.json`, `events.jsonl`,
`raw/powermetrics.plist` or `power_trace.csv` would make the comparison fail on
every run, not intermittently. Passing four artifacts across five invocations
is positive evidence that no such leak is present on this bench at either
commit.

The row stays live with a rewritten `status_note`. It is NOT closed and NOT
declared cured: the honest state is that the reported deterministic failure
does not reproduce here, so there is nothing to cure red-before/green-after,
and a speculative "hardening" change would be exactly the tolerance-widening
the row forbids. What would settle it: the original failing output — the
byte-inequality message emits `delayed_sha256`, `baseline_sha256` and the name
of the artifact that differed.

---

## A88 — CALEXITS-FOURTH-SHAPE-01 (CURED ON MAIN BEFORE THIS STREAM; CLOSED HERE ON VERIFICATION)

The row was written against run **32739939880**; the cure landed as `ddb1f633`
("Admit the fourth pack-cleanup terminal shape; classify the absent pack
child") on 2026-08-24, after the row text was authored, and the row was never
closed.

Custody: `evidence/calexits-fourth-shape-run32739939880-attempt1-py3.11.txt`
(the failing job) and `...-py3.14.txt` (the passing sibling), extracted from
the preserved attempt-1 archive `fourth-shape-run32739939880-attempt1.zip`,
sha256 `f60638ebcea81bf5584a722604760a6e617ff6df70c1251222e0e2c486d8108c`.

What the 3.11 job shows:

```
test_forced_auto_maintenance_mutation_reproduces_cleanup_race ... FAIL
RACE_EXERCISED=0 NO_RACE_PRE_WRITE=0 TRACE_INCOMPLETE=0
...
  File ".../tests/test_calibration_exits.py", line 2339, in
    test_forced_auto_maintenance_mutation_reproduces_cleanup_race
    self.assertTrue(pack_evidence.complete, mutation_events[-20:])
AssertionError: False is not true : (...)
```

All three classification counters are zero: the test died on the very first
attempt, before classifying anything. The dumped event tail shows the detached
`git maintenance` process entering the `loose-objects` region, spawning only
`git prune-packed --quiet` (exit 0), and exiting 0 — **no `git pack-objects`
child was ever spawned**. That is the absent-pack-child shape. The 3.14 job of
the same run passed with `RACE_EXERCISED=1`, which is why the shape reads as
intermittent rather than as a broken predicate.

The landed cure covers exactly this: `_classify_pack_cleanup` branches on
`evidence.pack_child_absent` first and returns `NO_PACK_CHILD`
(`tests/test_calibration_exits.py:452-458`); the mutation test guards the
completeness assertion with `if not pack_evidence.pack_child_absent:`
(line ~2732); and a raised cleanup errno still outranks an absent child so it
cannot mask a real shape-A race.

The five modelled terminal shapes each carry a deterministic
`_synthetic_pack_topology` regression:

| shape | regression |
| --- | --- |
| A — cleanup errno raised | `test_pack_classifier_shape_a_cleanup_errno_is_race_exercised` |
| B — complete write-pack region | `test_pack_classifier_shape_b_complete_write_is_no_race_pre_write` |
| C — pack child killed in prepare-pack | `test_pack_classifier_shape_c_prepare_kill_is_race_exercised` |
| D — pack child killed in repository setup | `test_pack_classifier_shape_d_repository_setup_kill_is_race_exercised` |
| E — pack child never spawned | `test_pack_classifier_shape_e_absent_pack_child_is_no_pack_child` |
| — absent child must not mask a real errno | `test_absent_pack_child_never_masks_a_raised_cleanup_errno` |

`_synthetic_pack_topology` raises `"synthetic topology terminal shapes are
mutually exclusive"` if asked to build two at once. That establishes mutual
exclusion **among the modelled shapes**; it is not a proof that no sixth
topology exists. A sixth would classify `TRACE_INCOMPLETE` and fail loudly
rather than pass silently, which is the property that matters for soundness.

Hosted evidence for the row's "passes repeatedly on hosted runners across both
interpreters" clause is under A89 below — the two cures landed 32 minutes apart
and share the same run population.

---

## A89 — PLANTEST-RGLOB-RACE-01 (CURED ON MAIN BEFORE THIS STREAM; CLOSED HERE ON VERIFICATION)

Cured by `a28b55bf` ("Prune the git object store from checkout_inventory's
walk") on 2026-08-24, also after the row text was authored.

`checkout_inventory` no longer uses `Path.rglob`; it uses
`os.walk(topdown=True, onerror=<re-raise>)` and prunes `.git` and
`__pycache__` from `dirnames` before descending, so the loose-object fan-out
directory that vanished in run 32745254371 is never scandir-ed at all.
Exactness is preserved deliberately rather than traded for tolerance: a real,
non-excluded directory vanishing mid-walk still raises.

Three deterministic regressions ship with it, driven by
`_VanishingDirectoryHarness`, which patches `os.scandir` to pause the walking
thread at a chosen directory while a worker thread `rmtree`s it:

- `test_git_object_store_is_never_walked_and_cannot_toll_the_inventory` —
  cites the hosted provenance verbatim and asserts the hook never even fires
  (not firing is the green result: pruning removes the race window);
- `test_inventory_raises_when_a_real_directory_vanishes_mid_walk` — a blanket
  `FileNotFoundError` catch or a non-raising `onerror` would silently drop
  files, so tolerance is explicitly forbidden;
- `test_inventory_matches_the_rglob_semantics_it_replaces` — symlinks,
  dangling links, empty directories.

Bench verification, three consecutive runs:

```
$ .venv/bin/python -m pytest tests/test_d117_decode_contrast_plan.py -q
24 passed, 1 skipped, 24 subtests passed in 17.70s
24 passed, 1 skipped, 24 subtests passed in 17.17s
24 passed, 1 skipped, 24 subtests passed in 17.74s
```

### Hosted evidence for both A88 and A89

Both rows' acceptance asks for repeated green hosted runs, not a bench result.
Counting the `main` runs whose head commit is a descendant of **both** cures
(`git merge-base --is-ancestor` against each run's `headSha`):

```
runs on descendants of both cures: 36 ; success: 31
```

The five failures are not these tests:

- four are `test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set` —
  the live-ID oracle drifting against the kernel during 2026-08-26/27
  bookkeeping (runs 33028190855, 33027985566, 33027825819, 33026950658);
- one is run 32813091203, the identity-pins teardown race cured in this same
  PR — see below.

So across 36 hosted runs on both interpreters since the cures landed, neither
the mutation race nor the inventory race recurred.

---

## Unregistered flake — identity-pins teardown race (CURED HERE)

Not a kernel row. Diagnosed alongside A89 because the stream card asked whether
it is the same family. It is.

**Two hosted occurrences, not one:**

| run | job | date | interpreter | error |
| --- | --- | --- | --- | --- |
| 32813091203 | 97696108102 | 2026-08-25 | 3.11 | `OSError: [Errno 39] Directory not empty: '.git'` |
| 32974766555 attempt 1 | 98196695324 | 2026-08-26 | 3.14 | `OSError: [Errno 39] Directory not empty: '/tmp/tmpxbynrw01/.git/info'` |

Both in `ProjectionLifecycleTests` teardown, at `self.temporary.cleanup()`.
Custody: `evidence/identity-pins-teardown-run32974766555-attempt1-job98196695324.txt`.

### What is observed, and what is inferred

**Observed, at this bench.** `init_git` in `tests/test_identity_pins.py` ran
`git init -q` and set only `user.name`/`user.email`. Under that configuration
Git's own Trace2 event stream shows every fixture commit spawning a **detached**
maintenance child; with the four controls set it spawns none:

```
controls absent   children=[['git', 'maintenance', 'run', '--auto', '--quiet', '--detach']]
controls present  children=[]
```

A detached child outlives the test body by construction, so it can still be
running when `TemporaryDirectory.cleanup()` starts unlinking the repository.
That is the whole hazard, and it is now asserted directly by
`test_fixture_commits_start_no_detached_maintenance_process`, which fails with
the child's argv in the message if any control is removed.

**Inferred, not observed.** That the specific writer inside that child is
`git gc`'s `update-server-info` writing `.git/info/refs` is the natural reading
of an ENOTEMPTY on `.git/info`, but the preserved logs record the symptom, not
the process chain. The cure does not depend on which file the child writes: it
removes the concurrent writer entirely.

### Cure

`init_git` applies the same four-key hygiene tuple the calibration-exits
fixture uses (`maintenance.auto=false`, `gc.auto=0`,
`maintenance.autoDetach=false`, `gc.autoDetach=false`) immediately after `git
init`. Removing the writer, not tolerating the failure — no retries, no
`ignore_errors`, no widened errno allowlist.

Same family as A89 and as the calibration-exits mutation race: a background git
process mutating a fixture tree that another thread is walking or removing.
`EVIDENCE-AUTHOR-GIT-TEARDOWN-01` (closed 2026-08-22) is the same class again.

### Scope note

This hygiene is **not** yet repo-wide. There are 27 `git init` call sites in 21 test modules across
`tests/`, and the controls appear in four files:
`tests/test_arm_readiness_lifecycle.py`, `tests/test_calibration_exits.py`,
`tests/test_receipt_histsem.py`, and now `tests/test_identity_pins.py`. The
remaining sites (`tests/test_bundle.py:203`, `tests/test_calibration_ledger.py:144`,
`tests/test_d117_decode_contrast_plan.py:305`, and others) still initialise Git
without them. Sweeping them was deliberately left out of this PR — it would
collide with the other T26 streams' files — and is proposed as a kernel row in
the stream report rather than registered here.
