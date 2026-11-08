# fix-finalize handoff — 2026-11-08

Local branch: `fix-finalize`, based on
`origin/perf/2026-11-08-eng-finalize` at `fdcc73d74`.
Authority: the user's fix-finalize brief and Opus review
`f551a6749:docs/perf/2026-11-08-opus-review-finalize-prearm.md`.
Mission M0 intake found no active stop card. This is the explicitly assigned
agent engineering task, not an instruction to resume queue or quiet-machine
work. The user's standing rules override full-suite and coordination-write
instructions. No kernel task was registered; RUN_STATE, TASK_QUEUE,
state_kernel and test_gen_state were not edited.

## Findings and disposition

- **F-L1 fixed.** One initial stable-snapshot attempt plus at most three
  retries, with 10/20/30 ms backoffs. Reacquire identities and restart the
  digest each time. Persistent identity changes raise `OSError` naming the
  path. No failing attempt caches a digest. Ordinary read errors, missing
  files and interruption propagate immediately. The same policy covers
  uncached admission hashing; no admission digest comes from terminal cache.
- **F-L2 fixed.** Native Darwin `statfs` must identify APFS; unknown platforms,
  detection errors and every other filesystem disable timestamp reuse.
  Check link and target devices. Observed mtime/ctime aligned to a microsecond
  or coarser also disable reuse, conservatively including accidental APFS
  alignment. Non-APFS streaming/parallel hashing still works and re-reads
  every inventory. A native probe of this clone returned `apfs`; other
  filesystem types/errors/precision were exercised with synthetic seams,
  not real mounted exFAT/HFS volumes.
- **F-L3 documented, cancellation deferred.** Worker cleanup still joins
  in-flight whole-file reads before returning. Cooperative interruption is
  a separate change; this patch does not abandon readers for faster exits.
- **F-L4 documented and tested.** An unrelated thread does not inherit the
  invocation's ContextVar cache. No global/thread-inherited cache was added.
- **F-M1 confirmed with a qualification.** The pinned R1/v4 desk calls
  `harvest_b6_session.py` → `joulewise/b5/harvest.py`. Member assessment
  supports a process pool and overlaps verdict production. The pinned desk
  argv actually omits `--workers`, so assessment defaults to one. Archive
  inventories/copy verification remain serial regardless of that setting.
  A separate synthetic-only experiment shows remaining parallel inventory
  headroom: 64 MiB, three fresh inventory reads plus an APFS clone, median
  0.168175 s serial vs 0.092528 s with four workers (1.82×, 45.0% reduction).
  All 36 measured inventories matched the oracle. These are warm, tiny,
  competing-load timings, not a production saving estimate. Real session
  argv, GB-scale performance, compression/offload/second-copy time and the
  share of turnaround spent hashing remain unknown.

## Files

- `joulewise/file_hashes.py`: retry policy, APFS/precision gate, lifecycle docs.
- `tests/test_finalize_hashes.py`: transient/persistent/open/read/post-read
  races, no-retry errors/interrupts, named error rows, filesystem detection
  failures, non-APFS/coarse timestamp refusal, link-volume policy and thread
  isolation; existing cache-count fixtures explicitly model eligible reuse.
- `docs/perf/2026-11-08-eng-finalize.md`: current race/cache behavior and
  corrected v4 performance framing; historical benchmark retained as dated.
- `docs/perf/eng-finalize-port-to-v4-lane.md`: unapplied port scope, pinned
  call-chain evidence, headroom and native handoff steps.
- `scripts/benchmark_v4_archive_inventory.py`: synthetic-only experiment,
  extracting three functions from the pinned Git object rather than running
  or importing any lane harvest pipeline. Takes no data-path argument.
- `docs/perf/2026-11-08-fix-finalize-v4-inventory.synthetic.json`: raw synthetic
  results, per-repeat timings and pinned harvest source digest.
- This report.

## Verification

Each unittest process selected only one module; no test modules ran in
parallel. All unittest commands used Python 3.13 and `TMPDIR=/private/tmp`.

| Command (after environment prefix) | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_finalize_hashes` | 23 passed, 0.455 s on final hash-module run |
| `python3.13 -B -m unittest tests.test_harvest_window` | 39 passed, final rerun 47.995 s (initial 36.857 s) |
| `python3.13 -B -m unittest tests.test_run_night.NightDriverTests tests.test_run_night.CourierDeliveryBoundaryTests` | 151 passed, final rerun 59.274 s (initial 62.534 s) |
| `python3.13 -B scripts/benchmark_v4_archive_inventory.py` | synthetic equality true, 36 measured inventories; raw output linked above |
| In-memory `compile(...)` of the three changed Python files | passed; no source execution |
| `git diff --check` | passed |

The first 22-test run passed before the additional precision test. After
tightening the precision guard, one positive cache-count fixture failed
because a native APFS timestamp happened to align to a microsecond. That
correctly made the file ineligible for reuse. Positive caching fixtures now
explicitly model eligibility; separate tests verify both fine APFS acceptance
and every coarse timestamp rejection. The final 23-test run passed.

No full suite, Block-5 analysis pipeline, measurement data, model download,
MLX execution, network, integration install, push or lane application was
performed. Tests and benchmarks created only synthetic temporary files.
Total targeted unittest time remains well below the user's 20-minute limit.

## Local commits

- `cf2db8c67` — `fix: retry unstable finalize hashes and gate cache reuse on APFS`
- The following handoff commit — `docs: record unapplied v4 finalize port and synthetic headroom`

The two-commit range changes only the seven files listed above. No push or
lane cherry-pick was performed. Git inferred the local committer identity
from the host; repository/global identity settings were not changed.

## Next exact step / limits

Lead: review the local commits, then choose a permitted post-R1 desk gap for
a **separate** port using the port note. Run the lane's native
`tests.test_run_night` including `HazardPackPrimitiveTests` outside this
sandbox. That process-group class was not run here. Run
`tests.test_finalize_hashes` on the lane and `tests.test_harvest_window` if
that tool is also ported, one module per process. No MLX-specific code/test
changed and no weights are required for these checks.

Before claiming a large turnaround saving, profile the authorized closed v4
path's actual phases; preserve independent destination re-reads and source
mutation checks. No scientific or naming ruling is needed for this patch.
The unresolved performance questions above do not block the local fixes.
