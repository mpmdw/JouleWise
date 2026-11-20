# sm-analysis-hygiene — 2026-11-11

Built Q12's analysis-identity checks and advisory checkout provenance for the lean
release verdict. Work is local on `test/2026-11-11-sm-analysis-hygiene`, based on
`origin/main` at `711467824395b689216ab24481d8f6e0a1d36ab4`. Nothing was pushed.

## Four values, before changes

| Notion | Observed value | Source and limit |
|---|---|---|
| (a) Frozen-files constant | `b13a510dc15b5e280309f7dd6b280426bf44afc6` | `tests/b5_analysis/test_frozen_files.py:B5_ANALYSIS_COMMIT`. Unchanged. |
| (b) Peeled r4 tag | `ab1e0098dbd0ab839c8f278088221aa8aa4de8d2` | `git rev-parse b5/analysis-r4^{commit}`. Unchanged. |
| (c) Committed record's `analysis_commit` | **Unavailable** | No tracked `B5-BLIND-DRY-RUN-RECORD.json` or `B5-RELEASE-RECORD.json` was found. No `analysis_commit` field was found in configs. `seal_pins.json` has only `schema`, erratum epochs, `sealed`, and `pins` at its top level. |
| (d) Runbook's `--pinned-commit` | **Parameterized**, not a literal commit | `RELEASE-RUNBOOK-lean.md` sets `PINNED=<record analysis_commit>` and passes `--pinned-commit "$PINNED"`. DLE-5 separately names r4 as `ab1e0098d`. CANONICAL names the release tool, without a literal pinned commit. |

The four are not proven equal. The test does not pretend otherwise. The actual
record and the argument used for the historical release remain unverified.
`verify_digests` reads the caller's custody record and compares its
`analysis_commit` with the argument. It reads seal digests from
`<pinned>:configs/analysis/b5/seal_pins.json`; that file does not pin an analysis
commit or the custody record's digest. No custody path was followed.

Git proves that (a) is an ancestor of (b): `merge-base --is-ancestor A B` exits 0.
Using all 388 paths returned by `test_frozen_files.frozen_digests()`,
`git diff --quiet A B -- <paths>` exits 1. The exact changed set is
`joulewise/b5/harvest.py` and `joulewise/calibration_bracketing.py`. It equals the
existing `EVOLVED_ON_MAIN` set. The same quiet diff on the other 386 paths exits
0. These are the qualified invariants the new test asserts. The old frozen-byte
tests still verify the original pins and rebound working-tree bytes.

## Changes and decisions

- Added `tests/b5_analysis/test_analysis_commit_agreement.py`. It checks the
  qualified ancestry/byte relation, DLE-5's tag identity, and the runbook's record
  binding. Missing tags/history produce an explicit skip. Missing committed
  records also produce an explicit skip, not a successful identity claim.
- The AST fence checks every Python file under `tests/b5_analysis/`, including
  helpers, for string literals beginning with `origin/`. There is no allowlist.
  Synthetic probes cover lane and other remote refs, tags, and comments. This
  fence is scoped to B5 analysis tests, not every unrelated test in the repo.
- Added `checkout_head` and `checkout_relation` to verdict records from
  `scripts/release_b5.py`. The existing `release_checkout` field is retained.
  Ancestry is observed using `git merge-base --is-ancestor`, including equality.
  This also prevents equal but unavailable object IDs from claiming equality.
- The four relations are `equals_pinned`, `descends_from_pinned`, `unrelated`,
  and `unknown`. `unrelated` includes a checkout behind the pin. Malformed IDs,
  missing objects, Git errors, and OS errors yield `unknown`. If checkout
  validation refuses before returning HEAD, the new fields remain null/unknown.
- The observation changes no comparison, refusal, or exit code. Synthetic
  verdict tests exercise all four relations with existing exits 0, 1, and 2.
  A separate synthetic record test executes the real digest verifier's matching
  and mismatching commit paths. These fixtures are not historical evidence.
- Added one CANONICAL tool-map row and exactly one alphabetically inserted
  timing-map line. The first measured module duration was 8.689 seconds.

Read audit sections 6 and 8 and the lane plan. Inspected `run_night.py`, the
watchdog, and the B5 driver on both required refs with `git show`. Main lacks
the W1 line's `courier.delivery.json`, `chain_exit_nonzero:<rc>`, and expanded
watchdog states. This seat adds no night-record reader and changes no arm-stack
file. The release metadata depends only on Git history.

## Verification

All unittest modules ran sequentially. No module exceeded three minutes.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_analysis_commit_agreement` | Initial: 13 tests, 8.689 s, OK; one skip for the absent committed record. |
| `python3.13 -B -m unittest -v tests.b5_analysis.test_analysis_commit_agreement` | Final: 13 tests, 10.767 s, OK; same explicit skip. |
| `python3.13 -B -m unittest tests.b5_analysis.test_frozen_files` | 4 tests, 2.618 s, OK. |
| `python3.13 -B -m unittest tests.b5_analysis.test_release_equality` | 10 tests, 13.813 s, OK; joined real-program S10 class skips by its existing opt-in gate. |
| `python3.13 -B -m unittest tests.independent_recompute.test_release_b5` | 31 tests, 47.690 s, OK. |
| `python3.13 -B -m unittest tests.independent_recompute.test_release_trace_20261107` | 11 tests, 15.815 s, OK. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | 14 tests, 0.788 s, OK; two live process checks skip because the sandbox denies `ps`. |
| `python3.13 -B -m unittest tests.test_gen_state` | 44 tests, 12.867 s, OK. |
| `python3.13 -m compileall -q joulewise tests scripts` | Exit 0. |
| `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` | Exit 2: `PermissionError: [Errno 1] Operation not permitted: 'ps'`. No rows/count could be observed. This is not a clean census. |
| `python3.13 -B scripts/repin.py --check` | Baseline and post-change: exit 0, all 16 pin families current. Both emit the same existing sealed-inventory warning. No digest/pin failure from the new fields. |
| `git diff --check` | Exit 0. The timing-map edit was also checked to be exactly one added line, with all other bytes unchanged. |

No release test module was skipped for time. The S10 opt-in class restores about
8 GB and takes hours; it stayed disabled. The full suite was not run, as directed.
The baseline pin check warned about existing sealed-inventory drift. No pin was
rewritten. The registry contains no target for `scripts/release_b5.py`.

A bounded `python3.13 -B -` inline mutation harness compiled ten in-memory
variants of the release script and ran five focused unittest methods per
variant. All ten were killed by assertion failures, with no errors or skips.
Mutations reversed ancestry, inverted equality and both Git status branches,
mapped invalid IDs/OS errors/Git errors to success, mislabeled descendants,
removed HEAD assignment, and gave refused checkouts a success relation. The
harness used only disposable synthetic Git repositories. It changed no file.

## Open questions and limits

The lead should confirm whether (a) is intentionally the frozen-byte anchor and
r4 the execution commit, or request a separately reviewed identity migration.
Recommendation: retain the established distinction and its two explicit
exceptions. Do not replace the constant just to make the values equal.

The lead must identify a permitted committed structure-only record/pointer before
the actual historical `analysis_commit` can be verified. The new optional record
test will compare that field to r4 if a named record is later committed. It never
opens real custody or a results ref. The runbook's placeholder cannot establish
which argument a past invocation actually used.

No measurements, analysis pipeline, real restricted data, RESULTS.md, held-out
data, remote host, network service, or model weights were accessed. Coordination
state, tags, and existing `joulewise/` files were not edited. No MLX code changed;
no native MLX run is required for this change. A live fixture census remains a
lead-side check outside this sandbox. Independent review and full CI remain
lead-owned.

Changed files: this report, CANONICAL.md, scripts/release_b5.py,
scripts/test_timings.json, and the new agreement test module. The local commit
hash is supplied in the final handoff.

Next exact step: the lead reviews the qualified anchor/r4 invariant and supplies
the permitted record-field evidence. Then run the live fixture census outside
the sandbox and complete the normal review/CI gates before any merge.
