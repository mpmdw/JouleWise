# PR #811 Tier 2 audit repair

The lead requested the repair of the Astra 6.2 BLOCK on `4a4d12930` and
the rebase of PR #804 from `f4195f98d`. Both original worktrees matched
their remote PR heads. RUN_STATE item 399 owns this software lane.

| Finding | Commit | Regression and disposition |
|---|---|---|
| HIGH 1, publication sync | `5506488bb`, `8581ffd56` | PASS. The sync-order test checks the error type, digest and errno for both writers. The retry test exercises identical and different bytes before and after temporary-link cleanup. E-02 exercises the late marker fault on #804. A-11 awaits #800. |
| HIGH 2, worker boundary | `8581ffd56` | PASS. The worker test requires both checkpoint channels and rejects a native clock call even if worker code catches the error. The pinned #807 supervisor delivered the passive worker checkpoint and recorded its cleanup signal in the synthetic PID namespace. |
| HIGH 3, collection | `8581ffd56` | PASS. The main collector checks the loaded case IDs against the contract. The regression rejects an empty or partial member even when another member supplies all IDs. |
| MED, APFS aliases | `5506488bb` | PASS. Case and Unicode aliases both report Busy for the same inode until the publisher reconciles it. The test preserves an unrelated temporary file. |
| MED, close roots | `8581ffd56` | PASS. The close argument test requires fixture campaign and work roots and the fixture fence path. |
| MED, desk-only gate | `8581ffd56` | PASS. X-18 ran against the pinned #799 desk lister with #800 absent. It accepted a clean local Git list and refused a warned list. |
| MED, preflight witness | `8581ffd56` | PASS for the false-positive regression. The audit's ENOENT witness now fails both X-13 assertions. The positive preflight check awaits #800. |
| LOW, A-12 scope | `8581ffd56` | PASS. An argparse exit is a real test error. The specific duplicate-pointer acceptance remains an expected failure. |
| I-01 ruling | `8581ffd56` | I-01 requires exit 5 and no marker if upload never reaches idle. I-02 requires exit 8 and an unconfirmed marker when upload reaches idle but verification fails. I-07 preserves the coupled scheduling regression. |

Python 3.13 cluster discovery ran 77 scenarios with 1 pass and 76 expected
failures. Six collector and boundary checks and 16 durable tests passed.
The owner seams absent at step 1 account for 75 expected failures and A-12
accounts for one. The separate pinned member witnesses used synthetic inputs.
The full sharded verification runs on hosted CI. Local broad discovery
includes tests that can open restricted inputs or signal processes.

The next gate is the final-head CI result and independent delta review on
both stacked PRs. Native qualification remains PROVISIONAL.
