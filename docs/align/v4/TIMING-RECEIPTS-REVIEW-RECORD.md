# Timing receipts: review record

2026-11-08. This is the review record for the timing-receipts lane (W1 integration item 6). The lane
has no two-seat agreement report, so this file names what was built, who reviewed it, the verdicts and the
shas, in place of one. It makes no claim beyond what those documents say.

## Rule that controls (Ed, 2026-11-08)

`docs/perf/SPEED-TOOLBOX.md` (on `main`), section "Timing receipts: markers only":

- A timing receipt is one appended line at a phase boundary: phase name, `time.monotonic_ns()` and
  wall-clock time. That is all.
- **No computation inside a window.** The ledger, durations and attribution are computed afterwards, off
  the MBP, by `joulewise.align.window_timing`.
- Append to journals that are already open. Create no new files, threads or processes. No extra fsync
  inside measured segments. Tens of markers per window, never at sample rate.
- Within-member phases are already stamped by the episode code; markers are added only where the reader
  reports a gap.

The registered estimand, blinding, preregistration, custody digests and batch-1 measured episodes are
unchanged by this lane.

## Build, reviews and verdicts

| Step | Seat | Object | Verdict |
|---|---|---|---|
| Build | Sol 6.1 (commits authored `Codex`) | `origin/perf/2026-11-08-timing-receipts`, build `3c9c47a4e`, verification note `0db040044`, run report `5fc873136` | built; recorded as pending delta review, STRICT re-registration and native validation (`docs/perf/TIMING-RECEIPTS-IMPL.md`) |
| Cold review | Claude Opus 5.5 (cross-family) | `origin/perf/2026-11-08-timing-receipts-opus-review` @ `53740ab65`, `docs/perf/timing-receipts-opus-review.md`, reviewing `5fc873136` | **HOLD**: three HIGH findings (below), two MEDIUM, LOWs; failing-first witnesses in `tests/align/test_timing_receipts_opus_witnesses.py` |
| Fix | Sol 6.1 (commits authored `Codex`) | `origin/receipts-fix`: `ed9fd3ca1` (receipt ordering, journal ownership, synthetic timing attribution), `bec6c8ae3` (verification, receipt inventory, native handoff); run report `bcd4fd3c2` on `perf/2026-11-08-timing-receipts` | the three HIGH findings corrected |
| Delta re-review | Sol 6.1 | `origin/perf/2026-11-08-timing-receipts-rereview` @ `9c4758dc9`, review commit `aba58bdf0`, `docs/perf/timing-receipts-rereview-sol.md`, reviewing `bec6c8ae3` against the v4 head `03253edca` (scratch merge `4c937e0be`) | **ADMIT_WITH_FIXES**: two manual merge resolutions (keep `joulewise/timing_receipts.py` in the closure; keep both the `v4_installer_handoff` span and the `pilot.install` call) and one MEDIUM, a stale receipt-test fixture (series-binding gate) |

The three Opus HIGH findings:

1. Every ALIGN member bundle failed `validate_bundle` (markers written ahead of buffered events, and a
   trailing `timing_boundary` after `run_finalized`), so the harvest marked every W1 member strict-invalid.
2. The driver wrote into the child chain's stage journal, creating it before any chain ran and leaking
   markers into desk records.
3. The branch failed existing CI gates, on its own head and on the v4 merge.

## Integration on the v4 line

- `560e4c87f` merges the receipts-fix head (it includes `bcd4fd3c2`) into the v4 line.
- `bb460ed89` regenerates the dynamic trace (`timing_receipts` is in the closure) and the receipt template.
- `f03a7ee38` merges that integration (plan item 6) into the R22 part 1 line.
- `e36b096fe` restores the timing-receipts measurement-core pins that the merge had left stale.

## What was and was not reviewed

- Both reviews and the build used synthetic data only. No measurement, custody or restricted record was read.
- The original build got an Opus cross-family review. The fix delta got a Sol re-review only; there is no
  separate Opus read of the fix delta. The Opus review's "re-review scope after fixes" lists the deltas a
  later reviewer should read, and the Sol re-review follows it.
- No agreement report exists for this lane. STRICT re-registration and the native/full-desk gates still
  apply before capture, as both the implementation note and the re-review state.
