# BY-P6 phase A, part 1: conflict resolution

Base/worktree HEAD: `5453160dd24498e17895ac8dbd24d3ca7874922a`.
In-progress merge: `9149ef58c4debec0682409e801addd1cf8c41bd5`
(`origin/lane/2026-10-22-bytes-twin-parity`, including reviewed PR #574).
No repository index mutation, commit, fetch, or further merge was performed.
The index intentionally remains unmerged until the lead stages the resolutions.
The BAT-2 ruling file is absent from this intermediate worktree; §4 was read
with `git show origin/lane/2026-10-22-battery-assist-audit:docs/process_traces/2026-10-22-forward/BAT-RULING.md`,
alongside the lead's explicit combined-semantics instruction.

## Conflict table

| File / original hunk | Pass-1 side | #574 side | Resolution and authority |
| --- | --- | --- | --- |
| `joulewise/bytes_analysis.py`, `_decode_battery_marker` | Current-only marker; `None` if the window has no B0AC; second-valued delay | Integer-nanosecond delay/window; false for a window without current | Keep the current-only nullable marker and integer-nanosecond boundaries. BAT-2 §4 / BAT-3 fix 1 and the lead's 20:20 PDT combined-semantics ruling require both. |
| `joulewise/bytes_analysis.py`, failed-energy marker loop near 994 | Call marker once; skip unknown windows; completion only over evaluated streams | `_battery_delay_ns`; skip windows with no polls | Compute integer delay, call marker once, skip when it returns `None`, and aggregate assistance/completeness over evaluated streams. BAT-2 §4 controls which polls count; #574 controls integer window arithmetic. |
| `joulewise/bytes_analysis.py`, pass-mean reason near 1420 | Deduplicate causes without pass labels | Preserve each actual pass ID/cause; keep the common blinded-stage string unchanged | Keep #574's per-pass reason assembly. The lead expressly requires #574's per-pass reasons and unchanged blinded-stage text. BAT-2 unknown-marker causes continue through those reasons. |
| `tests/fixtures/bytes/campaign.py`, function signature | Existing instant/delayed battery options | Adds reference assistance, late starts and stream-shape options | Keep the superset signature and both sides' fixture bodies. Required to exercise the battery fixtures and #574's native-parser stream-shape campaigns together. |

## Adjacent automatic-merge repairs

- A successful primary energy join still passed display seconds to the now
  nanosecond-valued marker helper. It now passes `_battery_delay_ns(stream)`.
- The independently implemented twin now returns an unknown marker when no
  current reading exists, distinguishes selected-stream and fallback causes,
  and aggregates only evaluated marker streams. The public Boolean meter flag
  remains the flag-presence projection; the separate nullable marker determines
  whether counts and the description line can be evaluated.
- Twin fallback completion is false when no mapped stream has an evaluated
  marker, matching the primary archive record. Selected energy streams retain
  their own completion disclosure even when current is missing.
- Regression expectations now apply #574's per-pass reason rule. New tests
  exercise missing B0AC on successful and failed native joins, and the twin's
  corresponding independent paths. The native-parser agreement oracle now
  follows the current-reading rule rather than using raw poll count.
  The primary integer-edge worked example now expects `None`, rather than
  `False`, for its empty marker window, as the combined BAT-2 ruling requires.
- #574's native sample decoding and clock-fit point handling remain intact;
  the twin continues to implement parsing and arithmetic without production
  imports. Native parser/join shape checks are part of the named agreement suite.
- The merged output-field inventory lacked the four copies of the pass-1
  lane's `withheld_path_checked`. They receive a specific custody-metadata
  exemption, citing the existing primary exact-path test. Canonical missing
  statuses, counts and flags remain compared. No stale inventory entries exist.

## Decisions I made

Applied the combined ruling mechanically: B0AC determines evaluation and sign;
integer nanoseconds determine window membership; pass-specific causes remain
pass-specific. No thresholds or agreement bars were added or changed. No energy,
fit, or estimator arithmetic was changed beyond the reviewed merge's integer
window behavior. The marker/description changes implement the lead's explicit
resolution authority and introduce no new choice of which data count.

## Deferred by the phase instruction

The lead stages and commits part 1 before any origin/main merge. Phase-A step 4
checks belong on the tree after part 2. The final B2 estimator pin, coverage
reproduction/adoption, registration edits and slot/order work (steps 6–8) await
phase B as directed. Any working source digest reported with this part is
diagnostic only and must not be adopted as the B2 pin.

Verification outcomes and per-campaign counts are recorded beside this file
after the named suites complete. All temporary fixtures and scratch repositories
use `/private/tmp/by-p6/part1-20261023`; only authorized scratch logs/reports and
the seven explicitly listed source/test/map files are written in this worktree.

The registered agreement module retains the exact union of 16 campaign labels
from the merge parents. `agreement_battery_variants.py` additionally runs both
CLIs, at the existing bars, on pass-1's instant-publication fixture with its
missing idle voltage and its delayed-publication fixture without reference
assistance. These two diagnostic variants do not change the registered campaign
mapping, coverage inventory, or estimator arithmetic.

## Final verification
Named run: **250 tests**, with four initial failures: the older reason substring, two inventory checks caused by the four missing custody metadata entries, and the empty-window Boolean expectation. The corrected runs passed: incomplete-window agreement (1 test), output coverage (6 tests), and MeterWorkedExamples (6 tests). The native marker-path class also passed (16 tests), and the exact custody-path test passed (1 test).
No unresolved failures and no pgrep-only failures. The full repository suite and forbidden cold-pass FullRoundTests were not run. No measurement was performed.
| Module | Tests in the named run | Final disposition |
| --- | ---: | --- |
| `tests.test_bytes_agreement` | 39 | Passed after corrected assertion rerun |
| `tests.test_bytes_coverage_map` | 6 | Passed after 6-test inventory rerun |
| `tests.test_bytes_twin` | 87 | Passed |
| `tests.test_bytes_analysis` | 103 | Passed after 6-test meter-class rerun |
| `tests.test_battery_float_sweep` | 5 | Passed |
| `tests.b6.test_bytes_packs` | 10 | Passed |

All 16 registered agreement campaigns and both additional pass-1 battery variants have **0 fields above the bar**. The marker_incomplete row below uses its corrected rerun; all other registered rows use the named run. Under-bar differences remain unclassified, as registered.
| Campaign | Compared | Under the bar | Above the bar |
| --- | ---: | ---: | ---: |
| `bytes` | 416077 | 7262 | 0 |
| `defects` | 356117 | 6601 | 0 |
| `edge_locked` | 346417 | 6213 | 0 |
| `marker_incomplete` | 20540 | 2436 | 0 |
| `late_start` | 220743 | 5837 | 0 |
| `empty_payload_n` | 416077 | 7358 | 0 |
| `replayed_batch` | 416077 | 7266 | 0 |
| `replayed_tail` | 416077 | 7285 | 0 |
| `first_batch_tail_replayed` | 416077 | 7297 | 0 |
| `minimum` | 336000 | 6928 | 0 |
| `resident` | 346417 | 6242 | 0 |
| `time` | 346417 | 6415 | 0 |
| `polls_only` | 20448 | 2534 | 0 |
| `header_closed` | 20448 | 2425 | 0 |
| `invalid_anchor` | 345937 | 6373 | 0 |
| `withheld` | 286518 | 5926 | 0 |
| `battery_instant` | 417517 | 7224 | 0 |
| `battery_delayed` | 416077 | 7324 | 0 |

Check tails: `part1-audit.log` records PASS for all 250 covered tests with corrected reruns; `part1-static.log` records PASS; `git diff --check` exits 0. Raw original and rerun logs are retained. An initial focused command used the nonexistent class name `NativeMarkerPathTests`; the correct `MarkerPathAgreementTests` passed all 16 tests.

## SHA, slots, and handoff
Working `joulewise/bytes_analysis.py` SHA-256: `42c637d69fdf5ac4237d02a7d1ce22b6ae6beff11215fba90518e48741c21d9b`. This is **diagnostic only**, not the adopted B2 agreeing pin. B2 400-campaign coverage reproduction/adoption, slot census and order edits remain deferred to phase B (steps 6–8). Phase-A step-4 checks remain for part 2 after origin/main is integrated.

The lead next stages the seven modified source/test/map paths and commits the existing part-1 merge. Only after that commit does part 2 merge origin/main. The branch HEAD and MERGE_HEAD have not changed during this session.

## Files changed by this session
- `joulewise/bytes_analysis.py`
- `scripts/bytes_twin.py`
- `tests/fixtures/bytes/campaign.py`
- `tests/fixtures/bytes/output_coverage.json`
- `tests/test_bytes_agreement.py`
- `tests/test_bytes_twin.py`
- `tests/test_bytes_analysis.py`
- `.scratch-SLOTS/p6/`: resolution record, immutable initial snapshots/hashes, replay scripts, logs, campaign counts and final audit. Baseline file copies are under `/private/tmp/by-p6/part1-20261023/baseline/`.
