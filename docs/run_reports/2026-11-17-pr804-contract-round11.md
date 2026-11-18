# PR #804 round 11 contract binding

[PR #804](https://github.com/mpmdw/JouleWise/pull/804) is step 2 of the cluster
merge order. Its previous head was `5755eef52`. The branch was rebased onto
`4a4d12930`, the head of [PR #811](https://github.com/mpmdw/JouleWise/pull/811).
RUN_STATE item 399 records the adopted decisions.

GitHub reported merge conflicts against the advanced `main`. The PR now
targets the #811 branch at the pinned contract head so Actions can test the
step-2 tree. Retarget #804 to `main` after #811 lands.

## Verification

| Tree | Scenario passes | Scenario xfails | Scenario failures |
|---|---:|---:|---:|
| #811 baseline | 1 | 74 | 0 |
| Rebased #804 before binding | 1 | 67 | 7 |
| #804 with the binding | 8 | 67 | 0 |

The separate source-inventory test passes. A-08, E-02, E-07, I-02, I-06, K-05
and N-06 run against the real offload CLI, offload library, encryption and
publication code. The fixture supplies CloudDocs command responses, a
dataless observation and a synthetic clock. A-12 remains the main pointer
expected failure. The mixed-port scenarios await the other production ports.

The #804 regressions exercise the evidence JSON, read-only validation,
stranded-span copying, legacy marker migration, rollback and future timestamps,
source and descriptor binding, publication recovery, and retained originals
and ciphertext. Termination tests use simulated child process handles. The
Python 3.13 focused run finished with 180 tests and 67 expected failures.
An OS signal guard refused any attempt to send a real signal. The canonical sharded run is on
GitHub Actions. This software evidence leaves native GUI-domain qualification
PROVISIONAL. The new head requires independent delta admission before merge.

The first hosted run exposed the child fixture's reliance on the unittest
loader's import name. The fixture now resolves its module from the repository
path. Discovery rooted at `tests/contract` verified the subprocess import and
passed all enabled scenarios. The first run also reported three deadline
failures in the calibration custody tests, whose code is outside this diff.

## NEEDS_SPEC

- **I-01.** Section 3.2 says an upload that never confirms returns 8 with
  `.ok.unconfirmed`. The established #804 behavior returns 5 with no marker
  when CloudDocs never reports the upload idle. It returns 8 with the
  unconfirmed record when upload reaches idle and the eviction/download
  verification cannot confirm. Confirm which failure the scenario intends.
  The production distinction is preserved pending that ruling.

## Next observable

Check the final head's GitHub Actions result. A failed check holds the PR.
Once the hosted run and independent delta admission are recorded, the lead
can consider #804 after #811 in the stated merge order.
