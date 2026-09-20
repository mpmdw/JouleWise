# Record 15 — fresh-eyes delta re-audit of fix round 4 (`d11ab811`), CENSUS-SELF-MATCH-01, 2026-09-20 ≈05:25 PDT

Auditor: Opus 5 subagent (read-only; experiments in a /tmp copy). Verbatim report:

VERDICT: PASS — round 4 (d11ab811) cures the hosted-shard failure; no blockers, no should-fix. Two nits, no action required.

1. [confirmatory] CI feeds the test program on stdin: `.github/workflows/ci.yml:179` `python - <<'PY'` → `run_units(...)` at ci.yml:227. Measured in the /tmp copy: `MAIN FILE: <stdin> SPEC: None`. Fork never consults `__main__`, so the `_fixup_main_from_path` path is gone. Causality proven by control below (spawn under stdin reproduces the exact hosted traceback locally).
2. [pass] Fork picklability/importability: `_overlap_worker` is module-level (tests/test_agent_census_concurrency.py:35); under fork nothing is pickled or re-imported — target, argv, barrier and pipe are inherited. Nothing in the worker needs `__main__`.
3. [pass] Fork/thread safety: threads at fork = 1 (instrumented run: `THREADS AT FORK: 1 ['MainThread']`). I ran the real hosted packer (SHARD_COUNT=6): `tests.test_agent_census_concurrency` is the FIRST of 42 units in shard 5, so no earlier module can leave threads. No `-W error`, `PYTHONWARNINGS`, `filterwarnings` or `simplefilter` in shard_tests.py / CI / pyproject; no `tests/__init__.py`. `TextTestRunner` sets `simplefilter('default')`, so a fork DeprecationWarning would print, never fail.
4. [pass] Context consistency: Barrier (:122), Pipe (:127), Process (:128) all come from the one `context` object at :121.
5. [pass] Hosted precedent: tests/test_bridge.py:426,489 already use `get_context("fork")` with no skip guard and pass on the hosted Linux shards today.
6. [nit] On Darwin `get_all_start_methods()` includes "fork", so macOS also flips spawn→fork. Bench 3/3 OK and the child only barrier-waits + exec's pgrep; a narrower predicate (spawn unless `__main__.__file__` is unusable) would keep macOS on its safer default.
7. [nit] Residual Linux-runner surface: `/usr/bin/pgrep` exists on ubuntu-latest and `-lf` output parses identically (OSError → skipTest, so absence is fail-safe); timing budget is ample (bench 13.7 s, unmeasured→21.834 s weight, 30-min job timeout), but a >10 s hiccup at `communicate(timeout=10)` (:43) / `barrier.wait(timeout=20)` (:39) / `reader.poll(30)` (:136) becomes a hard FAIL, not a skip.
8. [same-signature] The class "native test not portable to the hosted runner" was ALREADY documented in-repo: tests/test_sample_quiet_predicate_evidence.py:783 skips with "hosted Linux shards feed the runner via stdin, which spawn cannot re-import". Round 3 re-committed a known defect class. Remaining spawn uses in that module are Darwin-skipped or never start a real Process (:763 uses a Mock). No other module at risk. Darwin skip at :170 ("requires Darwin POSIX_SPAWN_START_SUSPENDED") is accurate — flag 0x0080 has no Linux equivalent.

EXECUTED TAILS (all from /tmp/cfx, a copy of the worktree at d11ab811; nothing under /Users/edr/code touched)

(a) module at bench: `python -B -m unittest tests.test_agent_census_concurrency -v`
  test_owned_agent_markers_are_still_listed ... ok
  test_stopped_peer_is_excluded_after_exec ... ok
  test_synchronized_peer_censuses_do_not_match ... ok
  Ran 3 tests in 13.735s / OK

(b) exact CI shape (program on stdin, stdout redirected to a file = block-buffered):
  MAIN FILE: <stdin> SPEC: None
  THREADS AT START: 1 ['MainThread']
  MODULE START tests.test_agent_census_concurrency
  Ran 3 tests in 13.678s / OK
  MODULE PASS tests.test_agent_census_concurrency tests=3 failures=0 errors=0 skipped=0 seconds=13.678
  SHARD SUMMARY index=5/6 modules=1 tests=3 failures=0 errors=0 skipped=0 result=PASS   (EXIT=0; no duplicated output from the forked children)

(c) spawn control under the same stdin shape (pre-fix behaviour):
  File ".../multiprocessing/spawn.py", line 297, in _fixup_main_from_path
  FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/cfx/<stdin>'
  SPAWN CONTROL exitcode: 1

(d) hosted packer: shard 5 units=42, first = tests.test_agent_census_concurrency.

Commit scope verified: d11ab811 touches only tests/test_agent_census_concurrency.py, 6 insertions / 1 deletion, one hunk.

## Magistrate disposition (05:27 PDT)
PASS accepted; nits 6–7 registered, no change (macOS fork is safe here: one thread, exec-only child; the hard-fail timeouts are the intended behaviour for a regression that must not pass vacuously). Item 8 is a lesson for briefs: the seat wrote a `spawn`-context worker although `tests/test_sample_quiet_predicate_evidence.py:783` already records that the hosted shards feed the runner on stdin — briefs for native tests should name that precedent, and the lead's replay (macOS, file-based main) cannot see it. Merge proceeds on a green second hosted pass (record 12 §6).
