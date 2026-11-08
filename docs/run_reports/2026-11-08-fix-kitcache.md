# fix-kitcache: Opus review applied

Branch: `fix-kitcache`, starting at `origin/perf/2026-11-08-eng-kitcache@27d4aa40f`.
Implementation commit: `d0cc5b7c20032958779a61b320bd9849bdb1407b` (`fix(align): remove kit and receipt decision caches`).
This report and the raw timing samples are a separate documentation commit.

## Authority and intake

User-directed, engineering-only review fix; it takes precedence over the unrelated
restart queue. Mission M0 completed: no active stop card or global gate; workspace
initially clean. No kernel task was registered. The user explicitly reserves
coordination state, overriding the normal state/kernel close-out instructions.
No measurement, registration judgment, estimand, threshold or roster changed.

Review read from
`origin/perf/2026-11-08-opus-review-kitcache@bf1d248c0:docs/perf/2026-11-08-opus-review-kitcache.md`.
The task's lead disposition owns the fixes. Speed rules read using
`git show origin/main:docs/perf/SPEED-TOOLBOX.md`: measure first, batch only
unmeasured software work, never cache decisions, prove byte equality.
No new consult or agent delegation was used. This is the fix of the supplied
cold review, not a new scientific ruling or live admission.

## Finding dispositions

- **HIGH-1 fixed:** deleted the receipt cache, its key/load/store/path helpers,
  `_committed_oids`, `_has_git_replacements`, metadata-only batch mode and the
  `cache` argument. Every successful validation compares all 223 working and
  committed bindings afresh. Working drift still refuses before Git I/O.
- **MED-1 fixed:** deleted the generation cache, complete-code census, concurrent
  key construction, publication logic, `cache` argument and `--no-cache` CLI flag.
  Every normal generation and `--check` executes the builders and their refusals.
  Existing cache files are ignored; this change does not delete user files.
- **MED-2 fixed:** fixture alternates use
  `git rev-parse --path-format=absolute --git-common-dir` plus `/objects`.
  The benchmark shares that fixture. A new synthetic linked-worktree regression
  exercises a `.git` file and verifies filled sizing can read the objects.
- **LOW-1 reverted:** the generation source scan is gone, including its new
  symlinked-directory and unreadable-code refusals. No retained protection
  required that scan.
- **LOW-2 reverted:** generated destinations again use `Path(output_root) / path`,
  restoring the legacy output symlink behavior for both generate and check.
  A synthetic symlink regression proves both paths reach the expected result.
  The receipt `_local` helper itself is byte-identical to the v4-r11 baseline:
  its pre-existing traversal/prohibited-name/symlink guard protects reads of
  receipt-supplied paths from redirection outside the intended tree. It remains.
- **LOW-3 retained and disclosed:** working-file faults precede Git faults;
  strict batch parsing reports non-blob/ambiguous/submodule requests as
  `commit unreadable` rather than the legacy missing-artifact message.
  These are the retained batching/ordering changes, not new admission decisions.
  Pending refusal text and all 221 single-working-file mutation messages match
  the legacy baseline exactly. This is not an exhaustive proof of all possible
  multi-fault message orderings.
- **LOW-4 resolved by deletion:** no generation key/publication path remains,
  so there is no ABA cache publication race.

Batched `_git_batch`/`_git_blobs`, ten-spec historical reads, invocation-local
`ContextVar` deduplication and working-bytes-first ordering remain. No persistent
or process-wide decision memo remains. Unchanged-output writes are still skipped.
Obsolete cache-only tests were removed or rewritten around fresh validation.
The three Opus witnesses were imported byte-for-byte from the review branch
(blob `07193c99a2b613ea53ce0353837d6368acdc7c37`). All three failed before the
fix (2.043 s); all three pass afterward.

## Before/after benchmark

Python 3.13.18; five in-process samples per ordinary row, one complete mutation
loop per implementation. The before run used the original benchmark and code;
the after run uses the cache-free benchmark. Both load the legacy v4-r11
functions from Git in the same interpreter, with the current generator digest
normalized equally. Raw samples, source hashes and exact refs are in the
[timing JSON](../perf/2026-11-08-fix-kitcache-timings.json).

Seconds; before default means a warm cache where that cache existed.
`same path` means the original benchmark did not provide a separate uncached row.

| Component | Before default | Before uncached | Fixed, always fresh | Legacy before / after |
|---|---:|---:|---:|---:|
| Pending generate | 0.083 | 0.053 | 0.049 | 1.180 / 1.864 |
| Filled generate + sizing | 0.085 | 0.054 | 0.047 | 1.053 / 2.446 |
| Pending --check | 0.052 | same path | 0.068 | 1.075 / 1.635 |
| Receipt, 223 bindings | 0.139 | 0.119 | 0.217 | 0.119 / 0.129 |
| Synthetic static arm components | 0.201 | same path | 0.239 | 1.293 / 2.359 |
| 221 working-file mutations (one run) | 3.733 | same path | 5.286 | 27.164 / 36.185 |

Pending and filled default generation improved from 0.083/0.085 s to
0.049/0.047 s. The fixed paths remain close to the pre-fix uncached builders.
Pending check, receipt validation, static-arm components and the mutation loop
were slower in this after run; those regressions are retained in the table.
In particular, receipt validation went from 0.139 s warm / 0.119 s uncached to
0.217 s, with fixed samples spanning 0.096–0.304 s. No isolated receipt
speedup is claimed. The after mutation loop remains 6.8x faster than its legacy
comparison (5.286 vs 36.185 s), preserving the working-first benefit.

The existing long job was neither inspected nor controlled. Host load was
uncontrolled: even legacy filled generation changed from 1.053 to 2.446 s.
These sequential synthetic timing samples cannot establish causal differences
of a few milliseconds or predict native-arm savings. No new fresh-process CLI
performance comparison was made; the review's small lazy-import saving from a
generation cache is deliberately relinquished by the lead's deletion decision.
The static arm row substitutes synthetic receipt validation for readiness and
excludes host probes, battery, disk, U3/WP19 and all live gates. It is not an arm.

Both benchmark runs passed pending/filled complete file-dictionary equality,
pending written-byte equality and the same pending refusal against v4-r11. The after
benchmark also explicitly compares the filled written bytes and all 221
mutation refusal messages. Successful receipt validation returns the same
receipt value. The independent legacy `git show` reader tests also pass.

## Verification

Each unittest module ran in a separate process, sequentially:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_kitcache_opus_witnesses` | 3 passed, 2.010 s |
| `python3.13 -B -m unittest tests.align.test_v4_kitcache` | 16 passed, 11.735 s |
| `python3.13 -B -m unittest tests.align.test_v4_kit` | 116 passed, 7.347 s |
| `python3.13 -B -m unittest tests.align.test_v4_registration` | 20 passed, 8.245 s |
| `python3.13 -B -m unittest tests.align.test_w1_kit_r10` | 30 passed, 33.877 s |
| `python3.13 -B -m unittest tests.align.test_v4_executed_closure` | 2 passed, 7.935 s |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_v4_kit.py scripts/benchmark_align_v4_kitcache.py` | Passed |
| `python3.13 -B scripts/align_v4_kit.py` | Regenerated; only two provenance digests changed |
| `python3.13 -B scripts/align_v4_kit.py --check` | Expected exit 1 on existing R0/R1 placeholders, after byte equality; no generated drift |
| `python3.13 -B scripts/benchmark_align_v4_kitcache.py --rounds 5` | Both before/after runs passed their equality assertions; samples retained |
| `git diff --check` | Passed |

187 final targeted tests passed (71.149 s reported test time); including the
failing-first witnesses, about 73.2 s. No full suite ran, per the binding brief.
No native MLX code changed or ran, so this slice adds no MLX test requirement.
Compilation briefly overlapped benchmark startup; unittest processes did not
overlap. The timings are explicitly not quiet-machine measurements.

## Files and handoff

Changed implementation/tooling: `scripts/align_v4_kit.py`,
`joulewise/align/apple/v4_registration.py`,
`scripts/benchmark_align_v4_kitcache.py`.
Changed tests: `tests/align/test_v4_kitcache.py` and the imported
`tests/align/test_v4_kitcache_opus_witnesses.py`.
Generated changes: `configs/campaigns/align_v4/plan_tree.json` generator SHA and
`configs/campaigns/align_v4/registration/identity_pins.json` dependent tree SHA.
Documentation: this report and its timing JSON. Scientific input/config bytes
and the receipt template are unchanged.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are untouched; no kernel task or advisor-visible
status update was made. No network, weights, measurement campaign, Block-5
pipeline, sealed outcomes or real restricted directory were accessed. Git read
only repository code/config objects through the allowed store/alternates.
No push, merge, external publish or change to the running job occurred.

No blocking question or new scientific ruling is open. Remaining uncertainty
is timing generalization and native readiness, which this synthetic run does
not validate. Next exact step: lead reviews/cherry-picks the local fix and
report commits, rebinds the exact candidate receipt, and performs the existing
native W1/registration gates outside this sandbox before any real arm.
