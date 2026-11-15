# Line 2 for cl-dev-03.v1.1 (pin 2d347f721), final: CI run 43664825578

Items-1115 builder, Sun 15 Nov 2026 15:03 PST (`date`). Completes `/Volumes/JW-EXT/scratch/dev03-line2/LINE2-dev03.md` (Sat 20:00, INCOMPLETE).

- Run: `ci` 43664825578 on PR #788 head `9cbb365a6957c3737617d8604ba6d06071ab018c` (frozen-path diff against `2d347f721` over the kit's 38 paths: empty).
- Status: completed 2026-11-15T04:47:37Z (Sat 14 Nov 20:47:37 PST); conclusion **failure**. Test shards red: 2, 3, 5, 6, 7, 8, 9, 11, 12; green: 1, 4, 10. Every non-test job success.
- Shard 11 was slow, not stalled: `tests.test_bytes_analysis` ran 9,106.8 s and passed (MODULE PASS, 112 tests). Its one red is `align.test_v4_dynamic_closure ... test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace` (failures=1), the twelfth base red.
- Red set: re-derived from every failed job's log (`gh run view --log --job`), FAIL/ERROR ids: 12 tests, `line2-dev03-red-9cbb365a6.txt`.
- Base: `ci` 43600776368 on `fe907d0d3`, conclusion failure, re-derived the same way: 12 tests, `line2-base-red-fe907d0d3.txt`.
- **The two sets are equal, test for test. No added red.** (`diff` empty.)
- Part 3 (each red passes at #777 head `ae340d3da`, CI 43601158271) and part 4 (the recorded diff) and D2 (`test_kit_v11` 30 tests, 0 skipped, shard 7) stand as in the item.
