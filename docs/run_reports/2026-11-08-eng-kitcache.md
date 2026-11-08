# eng-kitcache handoff

Branch: `perf/2026-11-08-eng-kitcache`, based on
`origin/align/2026-11-08-v4-r11@05b6d04cb`.

The implementation, complete input-key contract, equality evidence, synthetic
before/after timings, file list and limitations are in
[the performance report](../perf/2026-11-08-eng-kitcache.md).

Code commit: `cefbf2373` (`perf(align): cache v4 kit bytes and batch historical reads`).
This report and the timing samples are committed separately on the same branch.

Commands and final results (Python 3.13.18, unittest only):

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_kitcache` | 17 passed, 9.819 s |
| `python3.13 -B -m unittest tests.align.test_v4_kit` | 116 passed, 4.096 s |
| `python3.13 -B -m unittest tests.align.test_v4_registration` | 20 passed, 3.532 s |
| `python3.13 -B -m unittest tests.align.test_w1_kit_r10` | 30 passed, 13.596 s |
| `python3.13 -B -m unittest tests.align.test_v4_executed_closure` | 2 passed, 4.357 s |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_v4_kit.py scripts/benchmark_align_v4_kitcache.py` | passed |
| `python3.13 -B scripts/align_v4_kit.py --no-cache` | regenerated; only two provenance digests changed |
| `python3.13 -B scripts/align_v4_kit.py --check` | expected exit 1, pending R0/R1; no generated drift |
| `python3.13 -B scripts/benchmark_align_v4_kitcache.py` | exact pending/filled output equality; same pending refusal; five-sample timing medians recorded |
| `git diff --check` | passed |

The five targeted modules cover 185 tests. Synthetic static arm components
went from 1.316 s to 0.196 s; the 221-mutation loop went from 23.678 s to
2.376 s. On tiny fixtures, complete generation-key hashing costs more than
the batched uncached rebuild, and receipt cache hits regress by 18 ms;
these limitations are retained in the report rather than counted as wins.

The initial failing-first cache run had three failures and four errors; the
Git replacement and readiness-snapshot regressions separately failed before
their fixes. A strict source-census test fixture also needed both synthetic
code directories.
One cache/closure invocation briefly overlapped by mistake; all subsequent
test invocations were sequential. No full suite was run. Total test runtime
was well under the brief's approximately 20-minute budget.

No sealed outcomes, real restricted directory, prohibited external user path
or model weights were accessed. Git used only repository code objects through
the allowed store/alternates. No network or measurement campaign ran. The existing
8-worker job was not inspected or controlled. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json` and `tests/test_gen_state.py` are untouched;
no kernel task was registered, as required by the brief.

No scientific question is open in this slice. Timing generalization to real
arm hosts remains uncertain; the report explicitly separates static synthetic
component timings from native validation. No MLX code was changed or executed.
The lead must review/cherry-pick the local commits and satisfy the existing
exact-candidate receipt and native W1 gates outside this sandbox. No push.
