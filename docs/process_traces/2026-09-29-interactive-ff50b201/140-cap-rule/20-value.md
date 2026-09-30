# CAP-RULE-25G83-1: the value (session ff50b201, 2026-09-30)

Recorded replay after pre-registration commit 4d03d848 (run-info: 10-replay/run-info.txt; output 10-replay/replay.jsonl, 100 captures, 0 failed, no B or bound field).

- Sizing set R2a: 88 captures, 65 with a need; **N_max = 170,965**.
- Check set R2b: 12 captures, 8 with a need; largest 132,137 (below N_max; the check set cannot lower the cap).
- **R3: Cap = 10 × N_max rounded up to the next 10,000 = 1,710,000** (production cap today 165,000).
- **R5:** 45 s + 1,710,000 × 35 µs = 104.85 s ≤ 120 s: PASS (largest admissible 2,142,857).
- **R7 range:** median frames 113.3–254.3 ms; all inside 100–150 ms.
- Captures whose need exceeds the old cap: 8 (the 8 W1/W2 cap stops).
- R6 guard tests and the cap line land with the cap change; P8 (pin-delta of R7) follows.
