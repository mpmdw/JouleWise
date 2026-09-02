# Fresh pass (Sol 253) — magistrate disposition, cures, re-issue (2026-09-02)

Report: file 35 (envelope 5141 bytes, `findings`, `complete`; BLOCKER 0 /
SHOULD-FIX 1 / NIT 1). F1, F3, F4, F6 clean; F4's replay matched file 34's
2 / 2 / 1 / 1 exactly; the committed artifact replayed byte-identical at
`b6b4013b`, the commit two above the one containing it.

## Dispositions

- **SF1 (should-fix) — ACCEPTED.** `test_producer_commit_is_the_scripts_last_commit_not_head`
  built each scratch history as producer-commit → one empty HEAD commit, so
  a `git rev-parse HEAD^` producer records the right commit by accident of
  fixture shape. Sol names it the same fixture-construction class as M1,
  narrower. Cure (bench, commit `6b6deb2f`): each history is now root
  (empty) → producer → a commit touching `unrelated.txt` → a later empty
  commit that differs by date between the two repositories; the test
  asserts the recorded commit equals the producer commit and differs from
  BOTH `HEAD` and `HEAD^`. A HEAD, HEAD^ or unscoped `git log -1`
  implementation now all record the wrong commit (replayed below). The
  comment in the test names the counterfactuals.
- **N1 (nit) — ACCEPTED.** "shows as a mismatch between the two" compared a
  64-hex SHA-256 with a 40-hex commit id. The provenance text (constant →
  JSON `method.provenance`, Markdown, docstring, golden literal) now says
  the recorded producer SHA-256 must equal the SHA-256 of the script as
  committed at the producer commit (`git show <producer commit>:<script
  path>`), and an uncommitted edit shows as the two hashes differing.
- Sol's F1 edge analysis (renames without `--follow`; a lower-level API
  caller pairing script bytes from one worktree with history from another;
  a historical checkout recording its own last touch; a dirty tracked
  script detectable only by the `git show` comparison above) — recorded,
  none taken as a code change: the CLI binds `repository_root` and the
  script to one checkout, the artifact is issued from a committed script
  by rule, and the N1 prose now gives the reader the exact comparison that
  detects the dirty case.

## Escalation-trigger statement (magistrate's call, written for Ed)

SF1 is the second finding against the same test in consecutive rounds (M1 in
the cold gate, SF1 in this pass). The rule-11 cold-gate trigger is "any
second fix round on the SAME DEFECT". M1's defect — the test asserted a
property the producer did not have — was closed in round 4: the producer
has the property and the HEAD implementation fails the test. SF1 is a
different defect — the test's discriminating power was incomplete (one
more wrong implementation passed) — and it is closed by a fixture history
with three shape properties, each of which now kills a named wrong
implementation. The magistrate applies the delta-3 cold gate's own ruling
(file 32 Q1; file 33 Q1: a residual narrowed by a cure is not a recurrence
of the defect the cure closed) rather than reinterpreting it, and did the
cure at the bench under the bench-vs-session threshold (six fixture lines).
If the next pass finds a third survivor of this class the standing trigger
fires and the next spend is a consult, not a fix. Ed sees this paragraph
in the batch email.

## Executed evidence (this session; `TMPDIR=<scratchpad>/tmpbench4`)

Focused module at `6b6deb2f`: `Ran 27 tests in 0.533s OK`.

Mutant replay (`mut5-<name>` copies, one-commit `git init`, single-site
replacement, focused module):

```
base      : Ran 27 tests  OK
head      : FAILED (failures=1)  test_producer_commit_is_the_scripts_last_commit_not_head   [git rev-parse HEAD]
headp     : FAILED (failures=1)  test_producer_commit_is_the_scripts_last_commit_not_head   [git rev-parse HEAD^  — Sol 253's survivor]
nopath    : FAILED (failures=1)  test_producer_commit_is_the_scripts_last_commit_not_head   [git log -1 --format=%H, no pathspec]
cap400    : FAILED (failures=2)  test_differential_against_independent_reference, test_retained_bundle_values_of_record
```

Re-issue at `6b6deb2f`, twice, into `<scratchpad>/reissue-h` and `reissue-i`:

```
9a4fdddeb8939ce363a93be617352781dba5bfb39bc7a3b1aa8130c9d691c3c7  dg071-dg075-statistics.json  (both)
041a045e088379ccaf47f8b147efe6c73f17f8f579cd3c1dff3db0143f24927b  dg071-dg075-statistics.md    (both)
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
```

Diff against `ebd947a0`'s artifact: `producer.git_commit` (`70147173` →
`6b6deb2f`), `producer.script_sha256`, and the last sentence of the
provenance paragraph in both files. Values of record UNCHANGED.

Replay at the commit containing the artifact (appended after that commit):

```
$ git rev-parse --short HEAD
2eea71fe                      (the commit that adds the re-issued artifact)
$ python3 scripts/issue_dg071_dg075_statistics.py --repository-root . --out <scratchpad>/reissue-j/dg071-dg075-statistics.json
$ cmp reissue-j/…json docs/paper/round7/…json && cmp reissue-j/…md docs/paper/round7/…md && echo BYTE-IDENTICAL
BYTE-IDENTICAL-AT-2eea71fe
```
