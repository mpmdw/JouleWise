# CI on the tree of H_claim: run 37745108000 (2026-10-08)

## What this record is

**CI** is the set of checks GitHub runs on a pushed commit (the workflow `ci` in `.github/workflows/ci.yml`).
**H_claim** is the last commit that changes anything a block-5 measurement window reads:
`a64000884ef5bb4b76415835f02f39803f6eb620`. This record states which CI run stands for H_claim and why it may,
since the run was made on another commit.

## The fact

H_claim is a merge commit: its second parent is `3ff380b74ff3f549ba7038a241c485e15e46638f`, the head of the lane
`lane/2026-10-07-ci-linux-fixes`, which carried the test-side fixes that made the Linux jobs pass. The merge brought nothing
of its own: the two commits hold the same files. Git names the whole set of files of a commit by one hash, the
commit's **tree**; two commits with the same tree hash have byte-identical files.

| Commit | Tree (`git rev-parse <commit>^{tree}`) |
|---|---|
| `3ff380b74ff3f549ba7038a241c485e15e46638f` (the lane's head, the commit CI ran on) | `96178f01902ad751d5e62e6ad01e6fb83af44611` |
| `a64000884ef5bb4b76415835f02f39803f6eb620` (H_claim) | `96178f01902ad751d5e62e6ad01e6fb83af44611` |

CI run `37745108000` (https://github.com/mpmdw/JouleWise/actions/runs/37745108000) ran on the lane's head, triggered by the
lane's own draft pull request (event `pull_request`), from 2026-10-08T07:42:32Z to 2026-10-08T08:09:07Z (UTC). Its conclusion is
`success`, and every one of its 20 jobs completed with `success`:

| Job | Conclusion |
|---|---|
| `build` | success |
| `calibration-exits-exclusive (3.13)` | success |
| `calibration-writer-crash-matrix-exclusive (3.13, 1)` | success |
| `calibration-writer-crash-matrix-exclusive (3.13, 2)` | success |
| `changes` | success |
| `fences` | success |
| `installed-wheel` | success |
| `quick` | success |
| `test (3.13, 1)` | success |
| `test (3.13, 10)` | success |
| `test (3.13, 11)` | success |
| `test (3.13, 12)` | success |
| `test (3.13, 2)` | success |
| `test (3.13, 3)` | success |
| `test (3.13, 4)` | success |
| `test (3.13, 5)` | success |
| `test (3.13, 6)` | success |
| `test (3.13, 7)` | success |
| `test (3.13, 8)` | success |
| `test (3.13, 9)` | success |

The jobs named `test (3.13, n)` are the twelve parts of the ordinary test suite; the three jobs with `exclusive`
in their name run the two test modules that must not run beside anything else. All of them run on GitHub's Linux
runners.

Both tree hashes were computed by command when this record was written, and the job table was written by a script
from `gh run view 37745108000 --repo mpmdw/JouleWise --json …`; nothing in the two tables was typed.

## What this run does not cover

The seal commit and the record commit come after H_claim. The seal commit changes only the three seal documents
under `configs/campaigns/v5_claim_25g83/` (the sealed inventory, the registration and the analysis plan), and the
record commit changes only documents, records and tests. The registration (section 12, step 4) requires CI to
pass at the record commit, which is the head of pull request #489. That run is named in the pull request's ledger,
row 3, by the record commit's own hash; it does not exist yet when this record is written.

Before the lane's fixes the branch had never had a full Linux run: on 2026-10-07 the job `quick` failed on Linux
with two tests whose defects were in the tests themselves, and every later job was skipped. The lane cured those
with commits confined to seven files under `tests/`. One further candidate change of the lane, to
`scripts/run_campaign.py` (commit `9271df94f`: it hardens the reclaiming of a stale lock file against a file
system that reuses inode numbers, which the Linux runner does and the Mac's volume does not), was not taken for
block 5 and is not in H_claim.
