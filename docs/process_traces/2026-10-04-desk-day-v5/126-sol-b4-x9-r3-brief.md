# Block-4 lane X9 round 3 (Sol 6.1 high): a read-only offset check before the G10 inputs are prepared, and the X4 placement fixture

Worktree: /Users/edr/code/JouleWise-wt-dd5-x9 (branch `lane/2026-10-05-b4-x9`, rounds 1-2 committed). Scratch /tmp/dd5-x9/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal.

1. **`preflight` subcommand** for `scripts/ed_session/capture_t0_anchor_positive_control.py`.
   - Why: G10 needs fresh real T-0 author inputs, captured within the T-0 span before the control (600-3600 s). If the offset is still below 20 ms when the inputs are ready, the inputs perish while the operator waits. So the lead must check the offset band before preparing the inputs, not only inside `run`.
   - Behaviour: the subcommand runs the same fixed R0 collector and agreement computation as `run`'s preflight. Reuse the function; do not duplicate it. It prints one canonical JSON object: `status` (`PASS`, `g10_preflight_offset_too_small` or `g10_preflight_offset_too_large`), `midpoint_s`, `bound_s`, the collector's rc, and the boot id. With `--output <new path>`, it writes the full raw record create-once.
   - It needs no OUTSIDE confirmation and writes nothing into any custody root. It never runs an ON or OFF; prove that with an injected runner that records argv. Exit 0 on PASS, 3 on too small, 4 on too large, 2 on any error.
   - `run`'s own preflight still runs and stays authoritative.
2. **`tests/test_v5_block4_x4.py`**: the original `a1`-placement custody test (round-2 flag F2). Adapt it to the `a2` expiry → G10 → `s1` placement with an equivalent negative, without weakening it.

Tests: kill-tests for the subcommand (too small, too large, error, no ON or OFF argv, create-once output). Run `tests.test_v5_block4_x9 tests.test_v5_block4_x4 tests.test_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 tests.test_v5_block4_x1`. Finish in this turn.

WRITE_SCOPE: ["scripts/ed_session/capture_t0_anchor_positive_control.py", "tests/test_v5_block4_x9.py", "tests/test_v5_block4_x4.py", "tests/test_capture_t0_anchor_positive_control.py"]
