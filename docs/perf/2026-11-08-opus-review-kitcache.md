# Opus cold review: ALIGN v4 kit cache

Branch reviewed: `origin/perf/2026-11-08-eng-kitcache` at `27d4aa40f`, built by Sol 6.1 on
`origin/align/2026-11-08-v4-r11` (`05b6d04cb`). Reviewer: Opus 5.5. This is a cold,
cross-family review: the diff, the perf report, the timing JSON and the run report were read,
and the code paths were traced by hand.

## Verdict: ADMIT_WITH_FIXES

Keep the batching, the per-invocation deduplication and the reordered receipt checks. Together
they produce all of the measured speedup.

Remove the receipt cache before merging (HIGH-1). It sits on the admission path that `--check`
runs, it can be forged locally, and it is slower than not caching.

Also remove the generation cache, or make it opt-in (MED-1). It can hide a refusal raised by the
code that is actually running. It saves about 0.2 s, only for a fresh-process normal regeneration,
and never on an arm.

Fix the test fixture so it works in a Git worktree (MED-2).

Once those changes are made, the branch meets the three required properties:

- byte-identical `--check`;
- no refusal is ever served from a cache;
- engineering only.

The two-tier receipt work can then land without cache interactions.

## Findings

### HIGH-1: `--check` consults the receipt cache, and a cache hit can admit a drifted commit

**Where.** `joulewise/align/apple/v4_registration.py:359` sets the default
`validate_receipt(..., cache=True)`. The hit path is at `:403-415`.

**The path.** The admission path takes this default:

1. `kit.generate(check=True)` (`scripts/align_v4_kit.py:1782`) calls `require_w1_ready`.
2. `require_w1_ready` calls `require_registration(root)` (`:1329`).
3. `require_registration` calls `validate_receipt(receipt, root)` (`v4_registration.py:436`).

`scripts/align_v4_session.py:47,432` runs that `--check` in `prepare` and in `install`. The
second call in a session is therefore a cache hit.

**What a hit skips.** It skips the committed-bytes comparison, which is the step that binds the
reviewed bytes to the receipt commit. The comparison is replaced by a JSON file under `build/`.
That file's integrity field is a plain SHA-256 of its own payload, which anyone can recompute.
It is not an authenticator.

The perf report says "`--check` always bypasses the generation cache". That is true. It does not
bypass the receipt cache, so the admission gate is not cache-independent.

**Soundness without forgery.** The key covers the full receipt, freshly read blob OIDs,
validator and kit digests, and Python. Replacement refs force a miss. Git OIDs are content
addresses. I found no stale-hit path that does not involve a planted entry.

**Benefit.** None. On the Air, a warm hit takes 0.078 s and an uncached run takes 0.065 s, a
regression. Sol measured the same regression: 0.135 s against 0.109 s.

**Two-tier compatibility.** On a hit, the function returns early (`return receipt` at `:415`).
Any amendment-row or deviation-log check added after the committed loop would be skipped on a
hit. An amendment-tier path also legitimately has working bytes that differ from the committed
blob. That breaks the cache's single `value == bindings` model.

**Witnesses** (both fail on `27d4aa40f` and pass on `05b6d04cb`), in
`tests/align/test_v4_kitcache_opus_witnesses.py`:

- `test_require_registration_validates_receipt_without_cache`
- `test_planted_cache_entry_cannot_turn_commit_drift_into_admission`

The second test sets up a working file that matches the receipt but not the commit. With
`cache=False` it is refused with "digest drift". After one planted entry, the default call
admits it.

**Fix.** Delete the receipt cache: `_has_git_replacements`, `_committed_oids`, the `cache`
parameter and the `_cache_*` use in `validate_receipt`.

Keep the following:

- working-bytes-first ordering, which is where the 221-mutation speedup comes from;
- the stricter `_git_batch` parse;
- the shared `_git_blobs`.

If the team ever wants a receipt memo, cache only the pure, content-addressed map
`oid -> sha256(blob)` and let every comparison run in line. Never cache a decision or return
early.

### MED-1: the generation cache keys on the code on disk, not the code that is running

**Where.** `scripts/align_v4_kit.py:1693-1722` builds the key. `:1724-1754` is the hit path.

**The problem.** The key hashes every `.py` file under `joulewise/` and `scripts/` on disk. What
actually builds the output is the code already imported. A long-lived process whose checkout
changes underneath it, or any in-process patch, gets a warm hit. In that case the running
builder never executes, and a refusal it would raise is hidden.

**Impact.** Admission still fails closed, because `--check` rebuilds without this cache
(`:1769`). The impact is therefore stale written kit bytes plus a later drift refusal, not a
silent change to the science.

**Witness.** `test_warm_output_root_still_runs_the_builders_refusals` patches
`check_window_reference_roles` to refuse. On a warm output root, `generate()` returns the cached
files and does not raise. It fails on `27d4aa40f` and passes on `05b6d04cb`.

**Benefit.** In process, a warm hit is slower than the batched rebuild:

| Kit | Warm cache | Batched rebuild |
|---|---:|---:|
| Pending | 0.055 s | 0.037 s |
| Filled | 0.050 s | 0.029 s |

From a fresh CLI process, a warm hit takes 0.47 s and `--no-cache` takes 0.65 s, because a hit
skips the lazy imports. The cache never runs on the arm path.

**Fix.** Delete the cache. Otherwise, make `--cache` opt-in and rebuild from the exact bytes
that were digested, which also closes LOW-4.

### MED-2: the test fixture and the benchmark break inside a Git worktree

**Where.** `tests/align/test_v4_kitcache.py:50` writes `kit.ROOT/.git/objects` as the alternate.
In a worktree, `.git` is a file, not a directory.

**Effect.**
`tests.align.test_v4_kitcache.GenerationCacheTests.test_filled_synthetic_plan_and_sizing_are_byte_identical_when_cached`
errors here with "v4 kit historical source object missing". `scripts/benchmark_align_v4_kitcache.py`
fails the same way. Worktrees under `jw-wt/` are this repo's standard layout. I ran the benchmark
from Sol's full clone instead.

**Fix.** Use `git rev-parse --path-format=absolute --git-common-dir` and append `/objects`.

### LOW findings

- **LOW-1:** a new refusal in normal (non-check) generation. The code census refuses any
  symlinked directory, and any `.py` file it cannot read, anywhere under `joulewise/` or
  `scripts/` (`align_v4_kit.py:1712-1716`). This goes away with MED-1.
- **LOW-2:** the output path now goes through `_local(output_root, path)` (`:1773`). Symlinked
  components under the output root are now refused for both writing and `--check`; previously
  they were followed. This is hardening, but it changes what the kit refuses. Record it in the
  engineering log, or revert to `Path(output_root) / path`.
- **LOW-3:** the set of refusals is unchanged, but some messages and their order differ:
  - Working-file drift is now reported before Git faults. The perf report discloses this.
  - A tree, ambiguous or submodule spec now reports "commit unreadable" instead of "missing
    committed artifact" (`v4_registration.py:289`).
- **LOW-4:** an ABA race at the publication recheck (`align_v4_kit.py:1748`). If an input
  changes from A to B and back to A during a build, B-derived bytes are stored under key A. This
  is moot if MED-1 is fixed.
- **Write safety is OK:**
  - each entry is written to a same-directory `NamedTemporaryFile` and published with
    `os.replace`;
  - a load that fails its checksum is a miss;
  - concurrent writers publish identical content, so the last writer wins harmlessly;
  - the missing fsync and orphaned temporary files after SIGKILL are harmless.

## Required properties

| Property | Status on `27d4aa40f` | Status after the fixes |
|---|---|---|
| `--check` proves byte-identical regeneration | Holds for generation (fresh `build_files`, byte compare). Fails for the readiness gate, which uses the receipt cache (HIGH-1). | Holds |
| No refusal is served from a cache | Fails: a planted receipt entry (HIGH-1) and the loaded-code/disk-code mismatch (MED-1) | Holds |
| Engineering only | Output bytes equal the baseline on the pending and filled synthetic kits, and the pending refusal is identical (re-run here). Refusal surface changes: LOW-1 and LOW-2. | Holds, with LOW-2 logged |

## Is the cache key complete?

I traced every read in `_build_files`, `_identities`, `derive_sizing` and
`validate_align_v4_w1_plan.validate`.

- **Inputs.** The only working inputs are `inputs.json`, `r1_slots.json`, and `w1_plan.json` or
  its absence. The only Git inputs are the 10 historical specs. All are keyed. The validator is
  pure given its arguments.
- **Interpreter.** `sys.version` is in the key.
- **Packages.** A build loads no third-party module (checked from `sys.modules`), so package
  versions cannot affect the output.
- **Environment variables.** The kit reads none. Git environment variables can only change the
  source bytes, and those bytes are digested into the key.
- **Kit code.** Covered on disk, but not as loaded (MED-1).

## Measured savings

Measured on the M4 Air with Python 3.13.18, by running Sol's benchmark from the full clone. Each
figure is the median of 5 in-process runs.

| Component | Legacy | Branch (uncached) | Branch (warm) |
|---|---:|---:|---:|
| Pending generate | 0.757 s | 0.037 s | 0.055 s |
| Filled generate | 0.814 s | 0.029 s | 0.050 s |
| Pending `--check` | 0.478 s | 0.025 s | n/a (never cached) |
| Receipt, 223 bindings | 0.069 s | 0.065 s | 0.078 s |
| Synthetic static arm | 0.754 s | 0.120 s | n/a |
| 221 working-file mutations (1 run) | 13.57 s | 1.58 s | n/a |

Fresh-process CLI timings on the real repo, 5 runs each:

- `align_v4_kit.py --check`: 1.40–1.65 s on the baseline and 0.89–0.98 s on the branch, saving
  about 0.55 s per call;
- normal generation: 1.00–1.27 s on the baseline, 0.47 s with a warm cache and 0.63–0.68 s with
  `--no-cache`.

On the arm, a session runs `kit.generate(check=True)` twice, in `prepare` and `install`, so the
arm saves about 1.1–1.3 s on the Air. The MBP was not measured, to keep work off the measurement
Mac. Expect a similar saving of about 1 s. That is under 0.005% of the 26,940 s W1 span, so it
is negligible for the arm. The real payoff is test and CI time: about 12 s per run of the
receipt-mutation test on the Air, and about 21 s on Sol's host. All of that comes from batching
and reordering, none from the caches.

## Verification run here

Each test module ran in its own process with `python3.13 -B -m unittest`:

| Module | Result |
|---|---|
| `test_v4_kitcache` | 16 passed, 1 error (MED-2, worktree only) |
| `test_v4_kit` | 116 passed |
| `test_v4_registration` | 20 passed |
| `test_w1_kit_r10` | 30 passed |
| `test_v4_executed_closure` | 2 passed |
| `test_pilot4` | 18 passed, 1 skipped |
| `test_pilot3` | 7 passed, 1 skipped |
| New witnesses | 3 fail on `27d4aa40f`; 3 pass on `05b6d04cb` |

The benchmark's equality assertions (pending and filled bytes, pending refusal, receipt) all
passed. No model, study data, restricted directory or measurement host was touched.
