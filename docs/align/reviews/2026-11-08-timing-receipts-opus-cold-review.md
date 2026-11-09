# Timing receipts: Opus cold review of the fix delta

2026-11-08. Reviewer: Claude Opus 5.5 (cross-family; Sol 6.1 built the fix). Target: the timing-receipts fix delta
(`origin/receipts-fix`, `ed9fd3ca1` and `bec6c8ae3`, integrated on the v4 line by `560e4c87f`), read after the
Sol re-review `aba58bdf0` (ADMIT_WITH_FIXES). It follows the original Opus review (`53740ab65`, HOLD) and checks
that the three HIGH findings of that review are closed.

**Record status.** The reviewer's report was not committed to a branch. The lead relayed the verdict and the
findings in a message and asked that they be summarised here. This file is that summary, not the reviewer's own
text; it adds no finding and no verdict of its own. Findings are cited by the reviewer's own labels.

## Verdict: ADMIT-WITH-FIXES

- The three HIGH findings of the first Opus review are closed (member bundles validate; the driver no longer
  writes into the chain's stage journal; the CI gates pass).
- Capture bytes are unchanged by the fix delta.
- Four items need a fix before the delta is relied on (MEDIUM-1, MEDIUM-2 and the LOW items below).

## Findings and the lead's rulings

| Id | Where | Finding | Ruling |
|---|---|---|---|
| MEDIUM-1 | `joulewise/b5/chain.py` ~937-969 | `settle()` ran `"$PY" -B -c "$B5_SETTLE_PY"`, which imports `joulewise` outside a try block. An import failure exits rc=1 in about 0.07 s and the chain (`set -u`, return code unchecked) silently skips the registered 60 s settle. Even when it works, the import adds about 0.14 s of wall time and a process teardown right before the stage. | The settle never depends on a package import: an unconditional `/bin/sleep` for the registered duration, with two tiny marker writes around it from an inline stdlib-only writer (os/time/json only, every marker operation in try/except), and `(( $? == 0 )) \|\| note settle_marker_failed` for the marker writes only. A test: an empty `PYTHONPATH` or broken package still sleeps the full duration. |
| MEDIUM-2 | `scripts/align_v4_session.py` `_install_timing` (~775-792) and `_arm_and_install` (~1007-1016) | About 12-16 buffered marker JSON rows went to stdout after install returned, inside the quiet/display dwell. | No stdout. Persist the pre-stamp rows in the arm-record write that `pre_dwell` already makes, and the post-stamp rows (`v4_arm_checks` end, `v4_installer_handoff`) in the existing `dwell.json` rewrite in `_arm_and_install`'s `finally`. Fix the code comment. This also removes LOW-4 (a `ValueError` on closed stdout masking install's result). |
| LOW-1 | `scripts/run_night.py` ~1098-1262 | A refused launch closed `chain_launch_barrier` with status `complete`. | Record `refused`. |
| LOW-2 | `scripts/run_night.py` ~2546-2591 | `_timing_journal` yielded rows that both callers discarded, so arm-only markers and markers with no `night.log` were lost. | Retain them where the docstring says they are retained: spill to a file in the session. |
| LOW-3 | `joulewise/hazards/arm.py` ~277-285 | The `hazard_clean_dwell` end marker landed between the dwell end and the closing clock sample / boot reads. | Move it after the closing samples. |
| LOW-4 | install timing `finally` | A `ValueError` on a closed stdout could mask install's result. | Removed by the MEDIUM-2 ruling. |
| LOW-5 | `docs/align/v4/dynamic_closure_trace.json` | The trace regeneration dropped the `timing_receipts_delta` scenario. | Restore it. |
| LOW-6 | `joulewise/timing_receipts.py` docstring | It says writers never flush, but the driver and settle appends do. | Correct it. |

The chain text changes with MEDIUM-1, so the STRICT re-registration noted in `docs/align/v4/MERGE-NOTES.md` is needed.

## Fix commit

The fixes for every row above are on `align/2026-11-08-v4-r11` in commit `f455366162ffab6bcf7ecc4b5039f3b7d37f0c15`. The review covered the delta
before those fixes; it did not review the fix commit. That commit changes `joulewise/b5/chain.py`, a number-bearing
path, and has no review of its own.

## Related reports for the build and fix commits

- Build `3c9c47a4e` and fix `ed9fd3ca1` / `bec6c8ae3` (Sol 6.1, authored `Codex`).
- Original Opus cold review of the build, HOLD (three HIGH): `docs/perf/timing-receipts-opus-review.md`, sha256
  `57f14e798377d510cfb4a3f6273f1ed48826eb0551c62da1be33bb76481b7d8b`, branch
  `perf/2026-11-08-timing-receipts-opus-review` @ `53740ab65`.
- Sol delta re-review of the fix, ADMIT_WITH_FIXES: `docs/perf/timing-receipts-rereview-sol.md`, sha256
  `17a710e751b8762f8d4bb6f810b75fb16b325198a1c9a18fb2fd6528f4b0e690`, branch
  `perf/2026-11-08-timing-receipts-rereview` @ `9c4758dc9` (review commit `aba58bdf0`).
- This Opus cold review of the fix delta: ADMIT-WITH-FIXES (above).
