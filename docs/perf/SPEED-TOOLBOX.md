# Speed toolbox: levers for MBP utilization and pipeline throughput

Standing reference for every agent working on block cadence, measurement-MacBook-Pro (MBP) utilization or pipeline speed. Ed, 2026-11-07/08: "every part of the pipeline that takes 3-16 hours can be knocked down to 1-5 with some effort", "we built it for robustness not throughput", "add batching to the toolbox". Priority order and rules: RUN_STATE items 213-221.

## Rule zero: measure first
Profile before you optimize.
- **Measurement steps** are profiled post hoc from committed records with `joulewise.align.window_timing`, not live, because live instrumentation adds contention.
- **Software steps** are profiled directly with a profiler on synthetic inputs.

Estimates made from code alone have been 10× off. The finalize and pre-arm builds were estimated to save a lot and saved 2-3 min. Two caches turned out slower than no cache. Every claimed saving needs a measured before and after.

## Levers, roughly by MBP-hours returned
1. **Anti-idle.** The MBP must never wait on a missing prerequisite.
   - The next-2 readiness gate.
   - Critical-path look-ahead.
   - A native smoke before long blocks.
   - Guard replay before any guard gates a real run.
   - No hidden opt-in tests.
2. **Move work off the MBP.** It can go to the Air, the x86 desktop, or the cloud. Candidates:
   - the desk;
   - the harvest (the biggest single item, about 88-109 min per window);
   - analysis, reviews and kit regeneration;
   - compressed offload during cool-down.

   The MBP keeps only finalize, the light triage, cool-down, the pre-arm checks and the dwell.
3. **Turn fixed waits into conditions.** Cool-down and dwell end when the measured start-state band holds, with a floor and a ceiling. Each change needs evidence, and window-design changes need paired Sol and Opus builds before registration.
4. **Batching. Allowed only for UNMEASURED work.**
   - **Allowed:**
     - capability and no-bite screens;
     - attack-policy development;
     - model-ladder selection;
     - post-hoc local-monitor scoring of sealed transcripts;
     - synthetic test generation;
     - any inference whose energy is not an estimand.
   - **Forbidden** for every measured episode or member (R0, R1, W1, D, calibration, test, and v5 measured episodes). Batching shares power across episodes, breaks per-episode attribution and changes the energy per token. That makes it a different estimand, so measured episodes stay batch-1.
   - Batched work on the MBP runs only between windows and counts as MBP busy time.
   - Measure the aggregate tok/s at batch sizes 1/2/4/8 and the memory headroom (no swap) before relying on it.
   - Per-request energy attribution under batched serving is future research, not a shortcut.
5. **Parallelize and dedupe software.**
   - Bounded worker pools, batched git object reads (`git cat-file --batch`), streaming I/O, and hashing each file once.
   - Prove byte-identical output against the serial path, including refusals, ordering and floating-point summation order.
6. **Caching.** Only after measurement shows a win. Never cache a decision or a refusal: cache content digests (oid → sha256) at most. The key must cover the code as loaded, not only the code on disk. `--check` and admission paths never read caches. (Lesson from the kitcache review.)
7. **CI.** Shard by measured timings and run nothing twice. Every required test runs in the default CI, and none is lost (prove it with a test-id diff).
8. **Review-loop latency.**
   - The fixer starts on the first review that lands.
   - Opus and Sol seats run in parallel.
   - Witness tests go straight to the fixer.
   - Critical-path jobs get CPU priority on the Air (renice the others).

## Timing receipts: markers only (Ed, 2026-11-08)
A timing receipt is one appended line at a phase boundary: phase name, `time.monotonic_ns()` and wall-clock time. That is all.
- **No computation inside a window.** The ledger, durations and attribution are computed afterwards, off the MBP, by `joulewise.align.window_timing`.
- **Append to journals that are already open.** Use `chain-stages.jsonl` and `events.jsonl`. Create no new files, threads or processes.
- **No extra fsync inside measured segments.** Markers that fall inside a member are buffered and flushed with the existing stage-boundary sync. Turnaround markers (arm, cool-down, dwell, finalize, offload, push) sit outside measured time.
- **Keep the marker count to tens per window.** Never emit at sample rate. For scale, the powermetrics stream already writes 10 samples a second.
- **Within-member phases are already stamped** by the episode code (prefill, decode, tools, gates). Add markers only where the reader reports a gap.

## Never traded for speed
- Blinding and preregistration fidelity.
- Custody digests.
- The registered estimand.
- Batch-1 for measured episodes.
- The full-desk gate after W1 or after any code or config change.
- Paired builds for window design.
