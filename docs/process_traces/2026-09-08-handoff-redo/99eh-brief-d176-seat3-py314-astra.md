WRITE_SCOPE: ["tests/test_launch_window.py"]

# D-176 seat 3 — Python 3.14 argparse color probe breaks three launch-window tests (gpt-6-astra, medium, genre implementation)
Worktree feat/2026-09-08-d176-seat3-consumer (uncommitted seat-3 work in the tree; keep it). The lead's bench on
Python 3.14.7 fails 8 subcases of three tests in tests/test_launch_window.py
(PackNightGoRefusalHandlerTests.test_cli_uses_one_json_handler_for_both_exception_families,
test_cli_then_callee_go_mutation_is_detected_by_the_real_callee, test_each_required_cli_flag_omission_refuses_before_consumption)
with: scripts/launch_window.py:41 _parser → argparse.ArgumentParser.__init__ → _set_color → can_colorize() →
"TypeError: 'Mock' object cannot be interpreted as an integer" — Python 3.14's argparse probes the stream for color
support and these tests patch sys.stdout/stderr (or the stream's fileno) with a Mock. CI runs 3.11 and 3.14, so the
fix must be test-side and version-agnostic: in those tests set the environment so the probe short-circuits
(`PYTHON_COLORS=0` and/or `NO_COLOR=1` via mock.patch.dict(os.environ, ...)) or give the patched streams a real
`isatty()` returning False and an int `fileno`; do NOT change scripts/launch_window.py. Verify by running
`python3 -B -m unittest tests.test_launch_window` (the bench Python is 3.14.7; if your sandbox has a different
Python, say so and reason about 3.14's argparse._set_color/can_colorize by reading the stdlib source). Acceptance:
tests.test_launch_window rc 0 to a log; git diff --check; no commit; header < 8192 bytes; report the mechanism.
