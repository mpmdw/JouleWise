**HOLD.** Three findings remain:

- HIGH: executed installer/startup code remains amendable.
- HIGH: G3 admits unlisted or unsupervised KM003C streams.
- MED: G1 accepts stale packets when later records use different paths.

Added [witnesses](tests/align/test_r11_delta3_sol2.py), [review](docs/align/squeeze/fanout/r11-delta3-review-sol2.md), and [verification report](docs/run_reports/2026-11-08-align-v4-r11-delta3-sol2.md).

Serial targeted tests: **361 baseline instances passed**, including one expected failure. New witnesses: 13 tests, seven passing controls and six intentionally failing methods. Compileall and whitespace checks passed. Native MLX and live hardware remain unverified.

Committed locally on `align/2026-11-08-v4-r11-delta3-sol2`:

- `6e3962cd6` — witnesses
- `48e11b925` — reports

Working tree clean; nothing pushed. Lead should resolve these findings with Sol1 before Stage B, including choosing the authoritative latest-record binding.