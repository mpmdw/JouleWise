# T26 stream S5 — test-reliability batch (2026-08-26)

Four kernel rows plus one unregistered CI flake, worked as one stream on branch
`fix/ci-reliability-batch`. This file is the custody record: what was reproduced,
what was cured, and what the evidence is.

Bench for every local command below:
`/Users/edr/code/JouleWise/.venv/bin/python` (CPython 3.13.1, pytest 9.1.1),
worktree `/Users/edr/code/JouleWise-wt-s5-ci-reliability`, macOS arm64,
`mlx` installed (`mlx/core.cpython-313-darwin.so`).

---

## A85 — MLX-ACID-SIGABRT-01 (CURED)

**Reproduced at the bench.** With the four `@unittest.skip("CRASH-BLOCKED: ...")`
decorators removed from `tests/test_arm_readiness_evidence_t0.py`:

```
$ .venv/bin/python -m pytest tests/test_arm_readiness_evidence_t0.py -k acid
collected 34 items / 30 deselected / 4 selected
tests/test_arm_readiness_evidence_t0.py FFatal Python error: Aborted
  File "joulewise/adapters/mlx_runtime.py", line 1159 in _mlx_metal_memory
  File "joulewise/adapters/mlx_runtime.py", line 772 in _memory_snapshot
  File "joulewise/adapters/mlx_runtime.py", line 162 in prepare
  File "joulewise/identity_pins.py", line 1269 in _runtime_probe_metadata
  ...
```

Each of the four tests run **in isolation** fails (that is A84 /
FIXTURE-MODERNIZATION-01) but does **not** abort. The abort needs a prior test in
the same interpreter.

**Root cause.** `mlx.core` is a nanobind C-extension; executing its module init
twice in one interpreter is fatal by construction. Isolating the abort by
running the first ACID test and then re-importing `mlx.core` in the same
interpreter prints the native diagnostic that pytest's `Fatal Python error`
banner hides:

```
RuntimeWarning: nanobind: type 'Device' was already registered!
RuntimeWarning: nanobind: type 'DeviceType' was already registered!
Critical nanobind error: refusing to add duplicate key "cpu" to enumeration
"mlx.core.DeviceType"!            -> abort()
```

The second execution happens because the test helper `author_environment`
injected the synthetic `mlx_lm` module with
`mock.patch.dict(sys.modules, {"mlx_lm": ...})`. `patch.dict.__exit__` restores
by `in_dict.clear(); in_dict.update(snapshot)`, where the snapshot was taken on
entry. `mlx` and `mlx.core` are imported **lazily inside** that context by
`mlx_runtime._mlx_metal_memory`, so they are not in the snapshot and are
**evicted** from `sys.modules` on exit. The next test's
`importlib.import_module("mlx.core")` then re-executes the already-loaded
shared object.

The cure is code-side on both halves — see the PR diff and `FIX-1`/`FIX-2` in
the branch history. The four ACID tests **stay skipped**: they remain
structurally blocked on A84 fixture R1 schemas, and their skip reasons were
narrowed to say only that.

---

## A86 — CALEXITS-EVIDENCE-BYTES-01 (NOT REPRODUCIBLE AT THIS BENCH)

`test_logical_producer_delay_preserves_exact_evidence_bytes` **passes** here,
repeatedly, both at branch head and at the exact commit the row names as the
pristine-main reproduction (`74794af`):

```
$ .venv/bin/python -m pytest tests/test_calibration_exits.py \
      -k preserves_exact_evidence_bytes -q       # branch head, 3 consecutive runs
1 passed, 45 deselected, 4 subtests passed in 37.48s
1 passed, 45 deselected, 4 subtests passed in 37.56s
1 passed, 45 deselected, 4 subtests passed in 37.29s

$ git worktree add --detach <tmp> 74794af && cd <tmp>
$ .venv/bin/python -m pytest tests/test_calibration_exits.py \
      -k preserves_exact_evidence_bytes -q
1 passed, 33 deselected, 4 subtests passed in 37.68s
```

The test compares two independently-captured witness runs byte-for-byte. Each
capture builds a fresh `TemporaryDirectory` with a random suffix, so **any**
temp-path bytes reaching `instrument_evidence.json`, `events.jsonl`,
`raw/powermetrics.plist` or `power_trace.csv` would make the comparison fail on
every run, not intermittently. It passing four times for four artifacts each is
positive evidence that no such leak is present on this bench at either commit.

The row stays open with an updated `status_note`. It is NOT closed and NOT
declared cured: the honest state is that the reported deterministic failure does
not reproduce here, so there is nothing to cure red-before/green-after, and a
speculative "hardening" change would be exactly the tolerance-widening the row
forbids. What would settle it: the original failing output (delayed_sha256 /
baseline_sha256 and the differing artifact name), which the byte-inequality
message emits.

---

## A88 — CALEXITS-FOURTH-SHAPE-01 (ALREADY CURED ON MAIN; ROW CLOSED)

The row was written against run **32739939880**; the cure landed as
`ddb1f633` ("Admit the fourth pack-cleanup terminal shape; classify the absent
pack child") on 2026-08-24, after the row text was authored, and was never
closed.

Custody: `evidence/calexits-fourth-shape-run32739939880-attempt1-py3.11.txt`
(the failing job) and `...-py3.14.txt` (the passing sibling), extracted from the
preserved attempt-1 archive
`fourth-shape-run32739939880-attempt1.zip`,
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
child was ever spawned**. That is the "absent pack child" terminal shape.

The landed cure covers exactly this: `_classify_pack_cleanup` now branches on
`evidence.pack_child_absent` first and returns `NO_PACK_CHILD`
(`tests/test_calibration_exits.py:452-458`), the mutation test guards the
completeness assertion with `if not pack_evidence.pack_child_absent:`
(line ~2732), and the taxonomy has one deterministic synthetic-topology
regression per shape:

| shape | regression |
| --- | --- |
| A — cleanup errno raised | `test_pack_classifier_shape_a_cleanup_errno_is_race_exercised` |
| B — complete write-pack region | `test_pack_classifier_shape_b_complete_write_is_no_race_pre_write` |
| C — pack child killed in prepare-pack | `test_pack_classifier_shape_c_prepare_kill_is_race_exercised` |
| D — pack child killed in repository setup | `test_pack_classifier_shape_d_repository_setup_kill_is_race_exercised` |
| E — pack child never spawned | `test_pack_classifier_shape_e_absent_pack_child_is_no_pack_child` |
| — absent child must not mask a real errno | `test_absent_pack_child_never_masks_a_raised_cleanup_errno` |

`_synthetic_pack_topology` refuses to build two shapes at once
(`"synthetic topology terminal shapes are mutually exclusive"`), so the taxonomy
is exhaustive-by-construction rather than grown one flake at a time — which is
what the row's acceptance summary asked for.

---

## A89 — PLANTEST-RGLOB-RACE-01 (ALREADY CURED ON MAIN; ROW CLOSED)

Cured by `a28b55bf` ("Prune the git object store from checkout_inventory's
walk") on 2026-08-24, also after the row text was authored.

`checkout_inventory` no longer uses `Path.rglob`; it uses `os.walk(topdown=True,
onerror=<re-raise>)` and prunes `.git` and `__pycache__` from `dirnames` before
descending, so the loose-object fan-out directory that vanished in run
32745254371 is never scandir-ed at all. Exactness is preserved: a real
(non-excluded) directory vanishing mid-walk still raises.

Three deterministic regressions ship with it, driven by
`_VanishingDirectoryHarness`, which patches `os.scandir` to pause the walking
thread at a chosen directory while a worker thread `rmtree`s it:

- `test_git_object_store_is_never_walked_and_cannot_toll_the_inventory` —
  cites the hosted provenance verbatim and asserts the hook never even fires;
- `test_inventory_raises_when_a_real_directory_vanishes_mid_walk` — a blanket
  `FileNotFoundError` catch or a non-raising `onerror` would silently drop
  files, so tolerance is explicitly forbidden;
- `test_inventory_matches_the_rglob_semantics_it_replaces` — symlinks, dangling
  links, empty directories.

Bench verification, three consecutive runs:

```
$ .venv/bin/python -m pytest tests/test_d117_decode_contrast_plan.py -q
24 passed, 1 skipped, 24 subtests passed in 17.70s
24 passed, 1 skipped, 24 subtests passed in 17.17s
24 passed, 1 skipped, 24 subtests passed in 17.74s
```

---

## Unregistered flake — identity-pins teardown race (CURED HERE)

Not a kernel row. Diagnosed alongside A89 because the stream card asked whether
it is the same family. **It is.**

Hosted occurrence: run 32974766555 attempt 1, job 98196695324,
`test (3.14, 4)`, Python 3.14.7, ubuntu-latest, git 2.55.0. Custody:
`evidence/identity-pins-teardown-run32974766555-attempt1-job98196695324.txt`.

```
ERROR: test_nonconforming_committed_receipt_name_refuses_never_passes
       (test_identity_pins.ProjectionLifecycleTests...)
    self.temporary.cleanup()
  ...
    _rmtree_safe_fd_step(stack, onexc)
OSError: [Errno 39] Directory not empty: '/tmp/tmpxbynrw01/.git/info'
```

`init_git` in `tests/test_identity_pins.py` ran `git init -q` and set only
`user.name`/`user.email`. Every other git-backed fixture in this repo
(`tests/test_arm_readiness_lifecycle.py:443-452`,
`tests/test_calibration_exits.py:85-92`, `tests/test_receipt_histsem.py:545`)
also disables git's automatic maintenance; this one did not. `git commit`
triggers `git maintenance run --auto`, whose gc task detaches and calls
`update-server-info`, which writes `.git/info/refs`. A detached maintenance
process outliving the test body can create that file while
`TemporaryDirectory.cleanup()` is emptying `.git/info` — rmtree drains the
directory, then `rmdir` fails ENOTEMPTY.

Same family as A89 and as the calibration-exits mutation race: **a background
git process mutating a fixture tree that another thread is walking or
removing.** The cure is the same shape as the repo's existing convention —
remove the concurrent writer, not tolerate it — and it is carried in this PR
with a regression that reads the four config keys back out of a fixture
repository.

The remaining sites are proposed as a kernel row rather than swept here; see the
stream report.
