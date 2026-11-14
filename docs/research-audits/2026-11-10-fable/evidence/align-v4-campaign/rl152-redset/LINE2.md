# RL-152 §2.2 / item 317 line 2: red-set evidence for kit c76344c5 at b4b6aeb19

Taken 2026-11-14 14:3x PST by the laptop lead (Opus 5.5).

- Base: CI `ci` run 43600776368 on `fe907d0d3` (PR #781, CI-only): failure, 12 red tests (`base-red.txt`).
- Head: CI `ci` run 43602828989 on `8bd31ae5a` (PR #775 head): failure, 12 red tests (`head-red.txt`).
  `git diff b4b6aeb19 8bd31ae5a` over the kit's 37 frozen paths is empty, so this run is a full-suite run
  on bytes equal to `b4b6aeb19` on every frozen path.
- The two red sets are identical test for test (`class-diff.txt` empty): test_r1_followup (1 ERROR),
  test_smoke_delta_sol1/2, test_timing_receipts, test_v4_dynamic_closure, test_v4_executed_closure,
  test_w1_prequal (3), test_w1bm_sol1/2, hazards.test_refusal_allowlist.
- Each red module passes at #777's head `ae340d3da`: CI `ci` run 43601158271 on `ae340d3da`: success
  (full suite), plus targeted local runs in `pass-at-777-head/` (rc 0).
- Meter driver blobs are identical at `fe907d0d3`, `b4b6aeb19`, `ae340d3da` and `8bd31ae5a`:
  `joulewise/b5/driver.py` ff4fd76a, `scripts/km003c_monitor.py` 7d6acc98.
- Kit `cl-dev-01.json` at `589748f15`: sha256 c76344c50aebc271cef5711ecb4f9b05482e8b5593a57afa16e973dfe1dc66d7.
