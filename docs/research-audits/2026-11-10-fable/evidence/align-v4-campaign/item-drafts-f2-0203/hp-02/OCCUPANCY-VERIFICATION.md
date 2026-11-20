Delivered the [clocked integration fixture](/Volumes/JW-EXT/scratch/d-hp02-full-occupancy-spec/hp02-occupancy-fixture.zip), [freeze addendum](/Volumes/JW-EXT/scratch/d-hp02-full-occupancy-spec/FREEZE-ADDENDUM.md), and [verification record and builder handoff](/Volumes/JW-EXT/scratch/d-hp02-full-occupancy-spec/FINAL-MESSAGE.md).

**All three spans cede at the invented Friday noon.** The s01 launcher plan passes at 16,650 seconds. After the 300-second dwell, the runner reaches the soak decision at 12:05 and waits 4,200 seconds until 13:15. The earlier 4,500-second witness remains correct for a hypothetical soak entry at noon. At 12:45, a completed s01 mock took **17,244 seconds of work**, demonstrating that the plan can understate occupancy by 594 seconds.

| Span | Existing fence | Noon occupancy through clearance | Noon headroom | 14:00 occupancy through clearance | 14:00 headroom |
|---|---:|---:|---:|---:|---:|
| s01 | 18,110 s | 20,420 s | −2,310 s | 17,020 s | +1,090 s |
| s02 | 20,810 s | 23,120 s | −2,310 s | 19,720 s | +1,090 s |
| s03 | 23,510 s | 25,820 s | −2,310 s | 22,420 s | +1,090 s |

The afternoon timing decision is eligible under the invented setup, restore and clearance bounds. For every roster, a last counted start at 23:59:58 or 23:59:59 passed. A start at 00:00:00 ceded.

**Verification passed from the unpacked delivery:** 1,764 clock cases, 43 runner traces, 11 dated pairs and all 60 original vector IDs, with zero native-command attempts. The [successor regression](/Volumes/JW-EXT/scratch/d-hp02-full-occupancy-spec/fixtures/successor_regression.py) produced the intended red against the plan-only control, with 27 false permissions in 54 decisions. The composed reference passed all 54. Regression SHA-256 is `f28df8c505128d360de4345cb16fec4a7d1f7575fcda451b627c72c3decf3aab`.

**Head and CI.** Seat-only delivery at frozen pin `dd206025abb30fd5c07515cd4b34b3e653174810`. No new commit, PR or CI run. The supplied worktree’s Git metadata was inaccessible; source identity was verified against the pinned public Git blobs.

**NEEDS_SPEC and ownership.** The timing finding requires no new frozen-pin or paper ruling. Opus retains line-2 applicability, queue admission and dates, the positive no-prior-look attestation, freeze acceptance and actual issue. All three items remain unissued.