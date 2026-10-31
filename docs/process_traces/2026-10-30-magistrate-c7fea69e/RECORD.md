# Magistrate activation c7fea69e (Opus 5.5, headless, 2026-10-30 from 19:17 PDT)

No pending watchdog notices. No unread mail from Ed at launch. Open directives unchanged (#587 and the standing older ones).

## KB night attempt 2: chain ran, the capture stage failed on a code defect
- `/Users/edr/night-bytes-stream-test/attempt-2/custody/night/result.json`: verdict GO, chain exit 0, 18:50:00 to 19:03:50 PDT, 21 censuses, no census hits.
- Stages (`night/chain-stages.jsonl`): reserve rc 0; pre calibration capture rc 0; pre screen rc 0; calibration verdict rc 0; **known-bytes rc 2 after 81 s**; post calibration capture rc 0; session status rc 0.
- `runs_bytes_stream_test/capture/STAGE.json`: `status incomplete`, `call_count 0`, error `TypeError: ones(): incompatible function arguments ... Invoked with types: tuple`. The scan completed sizes 2**14 to 2**30 (17 sizes, 51 scan receipts, 17 pilots); the next size, 2**31 B, raised. No SCAN.json, no knee, no palindrome call.
- Cause. MLX 0.31.2 axes are signed 32-bit. `scripts/bytes_stream_test.py stream()` allocated `mx.ones((byte_count,), uint8)`; for 2**31 B that is one axis of 2**31 elements, and MLX raises TypeError, not MemoryError. `run_stage` treats only MemoryError as an allocation stop, so the stage ended `incomplete`. Reading rule §1 registers 22 sizes up to 2**35 B, so every live run would have hit this. The synthetic chain did not: the capture tests' fake `ones` returned `shape[0]` and enforced no axis limit.
- Desk steps (README, item 152): session copied once to `/Users/edr/night-archive/bytes-stream-test/attempt-2`; `bytes_stream_harvest.py` wrote `/Users/edr/night-bytes-stream-test/attempt-2-INPUT.json` with `records 0`, `scan null` and the stage diagnostic; `scan` and `read` not run (no SCAN_RECEIPTS.json). Night agents uninstalled (`install_night_agent.sh --uninstall`, rc 0); `com.joulewise.night*` gone from launchctl and LaunchAgents.
- Not an outcome of the test (no measured call ran), so a fixed attempt 3 is neither a retry into acceptance nor an unchanged retry.

## Fix: payloads of 2**31 B and more as whole 2**30-byte rows
- Lane branch `codex/2026-10-30-kb-shape` (bytes-stream-test clone; worktree `/Users/edr/code/jw-wt/kb-shape`), commit `79de7be49` on `9d45a2ea6`. Lead-written (Opus 5.5).
- `payload_shape(byte_count)`: flat below 2**31 B; otherwise `(byte_count // 2**30, 2**30)`, refusing a count that is not whole rows (every registered scan size is a power of two). `bytes_per_read` unchanged.
- Hardware evidence, lead, on this Mac with the measurement venv (MLX 0.31.2):
  - flat `mx.ones((2**31,), uint8)`: TypeError (reproduced);
  - 2-D payloads: `mx.sum` exact mod 2**32 at 2**30, 2**31, 3*2**30 B;
  - the patched `stream()` at 2**30, 2**31, 2**33, 2**35 B: 364, 384, 400, 400 GB/s. The M3 Max's memory bandwidth is 400 GB/s, so every byte is read once.
- Tests: new `test_payload_above_mlx_axis_limit_is_whole_rows`; the capture fake now raises TypeError on an axis above 2**31 - 1 and returns the element count. `tests.test_bytes_stream_test` passes. `test_bytes_stream_capture` + `test_bytes_mac_kit`: 14 tests, two fail only because a linked worktree is not an ordinary clone (`prepare must run from its own ordinary clone`); on the unpatched ordinary clone one of the same two fails (pre-existing).
- Sol 6.1 high executing review (`codex-run-v3`, local; report `~/night-archive/seats-c7fea69e/kb-shape-review.md`): **ADMIT, no findings.** It showed exact equality of every receipt, stage, harvest and reader field between the parent's flat payload and the patched shapes on 96 synthetic calls. From MLX 0.31.2's reduce source, the contiguous all-axis reduction uses 64-bit offsets and reads each byte once at all 22 scan sizes. The new tests fail against the parent. Every knee the rule can accept (K from 2**18 to 2**29) gives legal shapes. Its sandbox had no Metal device, so the lead's hardware run stands as the bandwidth evidence. Twelve orphaned synthetic test sleepers (from the lead's and Sol's runs) were terminated by the lead.
- Not yet on the measurement branch. `codex/2026-10-30-kb-capture` and `/Users/edr/code/bytes-stream-test` stay at `9d45a2ea6` until the knee question below is settled. The fix's cold passes go with any rule change, as one bundle.

## Desk rule-9 replay: the admitted knee rule refuses on every real scan
Before re-arming, the lead ran the whole §1 scan through the real `run_stage` with real MLX. Only the energy capture was stubbed, and the run was set to stop at the first palindrome call. Script: `~/night-archive/seats-c7fea69e/kb-knee-council/scans/rehearsal_run.py`. The scans, archived under `.../kb-knee-council/scans/`:

| Scan | Conditions | `knee_scan` reason |
|---|---|---|
| desk-contended | during the Sol review's suites | `64 K > s_max` (isolated above pair at 2**29) |
| desk-clean-1 | quiet Mac | `cache arm pairs not both resolved` (candidate K 2**28) |
| desk-clean-2 | quiet Mac | `64 K > s_max` (DRAM pair 2**33 above by noise) |
| desk-clean-3 | quiet Mac | `cache arm pairs not both resolved` (candidate K 2**26) |

- 4 of 4 refusals. Cache is resolved on every clean scan: the pairs at 2**24 and 2**25 (8→16 and 16→32 MB) have marginal throughput 565-1146 GB/s, against DRAM about 395-408 GB/s.
- The 2**26 pair (32→64 MB) reads below DRAM in all three clean scans (152, 184, 197 GB/s).
- Pairs from 2**27 to 2**28 vary between scans (302-922 GB/s), and these isolated late above pairs move the candidate K. Step 5 counts them by design (the false-knee guard).
- An attempt 3 under the unchanged rule would most likely end `knee not found` and spend the one registered session. So no re-arm tonight.

## Council on the knee rule (two blind seats)
- Brief `~/night-archive/seats-c7fea69e/kb-knee-council/BRIEF.md`: is the 32-64 MB behaviour physical; replay the admitted rule; any proposed change as exact text, replayed on every scan plus an adversarial no-cache synthetic scan that must refuse; the cheaper alternatives (more calls, a finer grid); or keep the rule and accept `knee not found`.
- Sol 6.1 xhigh, local `codex-run-v3`: report `.../kb-knee-council/sol-report.md`.
- Fable 5.1 high, `claude -p` from the kb-shape worktree: report `.../kb-knee-council/fable-report.md`.
- The lead writes the ruling. Any rule change gets a cold Fable and Opus pass (blind, executing) together with the shape fix before attempt 3 is prepared.

## Mail
- Ed, Gmail `1a18fe945ccd99c4` (thread `1a174cad9022cac9`): attempt 2 outcome, the fix, the desk refusals, and the council; no question; a NO keeps the unchanged rule.

## Council round 1 (20:06-20:26) and the lead's ruling
- **Sol 6.1 xhigh: MORE-DATA** (`kb-knee-council/sol-report.md`, scratch `sol-scratch/`).
  - Replay: 5 of 5 refusals (four desk scans, plus attempt 2's partial live scan rebuilt from its 51 receipts).
  - MLX 0.31.2's contiguous all-reduce switches launch geometry above 64 MiB (128 to 4096 first-pass threadgroups). So the fast 64→128 MiB pair need not mean cache.
  - It built and rejected the obvious repair (K from the two arm pairs). On a DRAM-only Gaussian-noise witness built from clean-3's spreads, that repair accepts a false K = 64 MiB where the admitted rule refuses.
  - Its proposal: a ~51 s timing diagnostic across the branch.
- **Fable 5.1 high: CHANGE** (`kb-knee-council/fable-report.md`).
  - It names three refusal routes: (a) the rebound pair; (b) plateau wobble against a threshold 0.5% above the single top pair (clean-2's 2**33 pair cleared it by 0.04 GB/s); (c) the 4 MiB arm increment, too small to resolve.
  - Its proposal: step 5 becomes the first cache-to-DRAM transition plus a derived straddle check. Replay: 4 of 5 refused, finding K = 2**26 only on clean-1. 0 false knees in 40,000 DRAM-only draws at 1× and 2× the observed noise; about 1 in 4,000 for both rules at 0.5×.
  - NEEDS_RULING: adopt; a DRAM reference envelope; printing late pairs.
- **Diagnostic (lead, quiet Mac, 3 runs; `kb-knee-council/diag/`, table `DIAG-TABLE.txt`):**
  - 32→45 MiB: 330-370 GB/s.
  - 45→64 MiB: about 140 GB/s, tight, in all 3 runs.
  - 64 MiB → 64 MiB + 1 B: about +30 µs on the clean run; the other two runs were noisy.
  - 90→128 MiB: about 600 GB/s.
  - So the slow/fast pattern at 64 MiB is largely the launch-geometry switch. And the cache arms (≤ 16 MiB, small launch) and S (≥ 4 GiB, large launch) do not run the same GPU work, contrary to §1's premise.
- **Ruling (lead):**
  1. No attempt 3 under the admitted rule.
  2. Fable's step-5 text is not adopted as written: it still refuses 2 of 3 quiet scans on route (c), and its straddle signature sits on the geometry branch.
  3. Design round 2, two blind seats (Sol xhigh, Fable high). Charge: whether the geometry difference between the arms can change a printed quantity, and the smallest design that removes it; a knee rule that handles routes a-c and refuses DRAM-only nulls; the cost. Brief `kb-knee-council/round2/BRIEF.md`.
  - The seats disagreed on a science question. A cold judge was not convened, because the diagnostic changed the question both positions answered; round 2 takes it up.
