# eng-finalize → R1/v4: proposed port only

No lane, measurement checkout, registration, installed job or rendered plist
was changed. This note compares Git objects only:

- eng-finalize base: `fdcc73d743d40d9b18ff1a56d81bb70302e3893c`.
- R1/v4: `origin/lane/2026-11-06-v4-r1-integrated`, pinned here at
  `e901eb2a480d51377a494be9d797733dfcd0220b`.
- Opus review: `origin/perf/2026-11-08-opus-review-finalize-prearm`,
  `f551a6749cc17b8f2e70f40b1b52ad3fb1fdba93`, finding F-M1.

## Applicable terminal-inventory changes

Port `joulewise/file_hashes.py` including the F-L1 stable-snapshot retries and
F-L2 APFS/precision reuse gate. In the lane's `scripts/run_night.py`, port
only the corresponding eng-finalize hunks:

1. Streaming `_sha256_path` for fresh admission reads; never use terminal
   cache entries for gate inputs.
2. `_artifact_entry`/`_artifact_list`: bounded, ordered hashing of the
   existing result inventory, preserving traversal order, literal diagnostics,
   missing-file behavior and disclosure filters.
3. One `hash_scope` around each CLI terminal run/rehearse/dead-man dispatch,
   spanning result and durable records before/after courier. Changed files
   must invalidate; every later invocation must authenticate afresh.
4. Optional `--hash-workers` choices 1/2/4/8 with default 1. Leave installed
   argv/plists alone unless a separate lane change explicitly changes them.

On the pinned lane the relevant symbols are `_artifact_entry` (1439),
`_artifact_list` (1453), `_durable_record` (1523), result inventory (2142),
reporting durable records (2374–2386), dead-man records (5065 onward), and
`_main` (5703). Re-locate by symbol after lane movement. Retain the lane's
powermode close, lock handling, receipt rules and R1 additions. Copying the
whole eng-finalize `run_night.py` would lose lane changes.

The review found the original patch applied cleanly, but that is not a gate
for a future port at a different head. Do not port while R1 is armed (the
review cites RUN_STATE 216). The lead must establish the permitted desk gap.
This session did not inspect live job state.

`scripts/harvest_window.py` is outside the v4 desk call chain below. Its
optimization can remain on eng-finalize; it gives no saving to these v4
archives. This branch alone saves **zero** on the unmodified lane. After a
port, terminal-inventory savings depend on the bytes actually in `night/`
and `night/evidence/`, not the much larger runs trees. Their live size/runtime
was not read or measured here.

## F-M1: the large-copy path and what “already parallel” means

The pinned code confirms the review's route:

| Code at the pinned R1 head | Evidence |
|---|---|
| `scripts/align_pilot_session.py:269`, `desk` | At 311–314 builds argv for `scripts/harvest_b6_session.py` with `--non-claim`; session archive/private/export roots are passed explicitly. |
| `scripts/harvest_b6_session.py:15,34,46` | Imports `joulewise.b5.harvest`; accepts `--workers` (default 1); calls `harvest(..., seams=Seams(workers=args.workers), prepare_desk=True)`. |
| `joulewise/b5/harvest.py:2342,3795,4076,5516` | Member assessment supports `ProcessPoolExecutor` through `Seams.workers`. |
| `joulewise/b5/harvest.py:7894` | With `prepare_desk`, verdict production and early member assessment overlap before archiving. |
| `joulewise/b5/harvest.py:3969,1625` | `archive_inputs` calls `archive_sources`: source inventory → clone → independent destination inventory, for each source. |
| `joulewise/b5/harvest.py:1592,1606,7624` | `tree_inventory` hashes files serially; `clone_tree` uses macOS `cp -c -pR` with byte-copy fallback; `sources_unchanged` re-hashes sources. |

Thus “already parallel” is true of supported member assessment and verdict
overlap. **It is not evidence of parallel archive hashing or copying.** The
pinned `desk` argv omits `--workers`, so member assessment actually defaults
to **one**, unless a different operator invocation supplies it. The review
does not establish which argv a real session used, and this session did not
read session records. Passing a worker count through that caller is another
possible future change, with unmeasured benefit.

There are three full inventory reads around an ordinary archive copy
(source, destination, final source recheck), and `prepare_desk` additionally
inventories the runs root before/after verdict writing (5413,5485). Those
before/after checks detect writes and must remain fresh. Do not reuse a
terminal digest across these authentication boundaries. Hashing files within
each fresh inventory is a plausible independent speedup; `Seams.workers`
currently does not control it.

Compression has a separate cost. At the same head,
`joulewise/desk_compress.py:292–329` processes files serially; each zstd
invocation already uses `-T0`, with source hashing, decompressed digest
verification, fsync and publication before original removal. More parallel
compressors could oversubscribe the machine. No compression, offload or
second-location confirmation was benchmarked or changed here.

## Synthetic headroom, not a production estimate

Reproduce in an authorized agent desk session, never in a quiet window:

```sh
TMPDIR=/private/tmp python3.13 -B scripts/benchmark_v4_archive_inventory.py
```

The script extracts only `sha256_file`, `tree_inventory` and `clone_tree`
from the pinned lane's Git object. It never imports or invokes harvest,
analysis or compression, and accepts no input-data path. Sixteen generated
4 MiB files (64 MiB) plus a literal symlink model source inventory → clone →
destination inventory → source recheck. Each candidate pass has fresh hashes;
all inventories must equal the lane oracle. Three repeats, local APFS,
uncontrolled warm cache and competing machine load; no GB-scale evidence.

Raw output: [synthetic inventory timings](2026-11-08-fix-finalize-v4-inventory.synthetic.json).

| Mode | Median three-read + clone total, s | Relative to lane serial |
|---|---:|---:|
| Pinned lane serial | 0.168175 | 1.00× |
| Candidate fresh streams, 1 worker | 0.181473 | 0.93× |
| Candidate fresh streams, 2 workers | 0.111305 | 1.51× |
| Candidate fresh streams, 4 workers | 0.092528 | 1.82× |

Four workers saved **0.075648 s (45.0%)** on this tiny archive skeleton.
All 36 measured inventories matched the oracle. This demonstrates remaining
parallel hash headroom despite the existing member pool. It does not show
that real archives or turnaround get 1.82× faster: media throughput, large-file
distribution, compression, second-location copying, verification and network
transport can dominate. No evidence supports a 10–30 minute saving from
eng-finalize. Production seconds saved are **unknown**. If this isolated
stage's 45.0% reduction transferred, the total saving would be 0.450 times
the fraction of turnaround spent in that stage; that fraction is unmeasured.

## Lead's next steps and checks

After the permitted R1 close, prepare a separate lane port and run, one module
per process, `tests.test_finalize_hashes`, `tests.test_run_night` (including
`HazardPackPrimitiveTests`) and `tests.test_harvest_window` if that tool is
also ported. Run native process-group cases outside this sandbox; no MLX
execution or model weights are needed for this patch.

Before choosing archive work, time a closed, authorized v4 session's phases:
verdict/member assessment, source inventories, clone/copy, independent
destination inventory, source recheck, compression, second-location copy and
confirmation. Count `night/` and evidence separately from runs/archive bytes.
Only then choose a hash worker count or a separate archive optimization. Keep
all destination re-reads, mutation refusals and custody/deletion gates.
