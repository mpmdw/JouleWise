WRITE_SCOPE: ["tests/test_run_night.py","tests/test_night_gate.py"]

# D-176 census cure — night-driver test fixtures vs the launcher-identity check (gpt-6-astra, medium, genre implementation)
Worktree int/2026-09-08-d176-seats-2-3 at 93870527 with the UNCOMMITTED census cure in the tree (report
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fj-seat-d176-census-cure-final-astra-report.md; keep every edit). The lead's bench on the full named list plus
tests.test_run_night shows ONE error: tests/test_run_night.py ~:2168
test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule → night_gate._pack_rehearsal_roots →
arm_readiness._authenticate_launcher_identity raises "measurement_root: launcher is not the planned clone" because the
fixture plans a synthetic measurement_root. Correct the fixture the same way the census seat corrected
tests/test_launch_window.py ~:907 (the plan's measurement_root IS the running checkout,
Path(arm_readiness.__file__).resolve().parents[1], with its runs/ present or the census skipping the null locator) —
do NOT weaken or bypass the identity check; keep every sibling-child/DISJOINT assertion; add the counter-case in this
module if absent (a plan naming another checkout refuses "launcher is not the planned clone" at the gate). Sweep
tests/test_run_night.py and tests/test_night_gate.py for any other fixture with the same shape and correct it.
Acceptance (rc-gated; named modules ONLY, never discover/shard): tests.test_run_night tests.test_night_gate; git diff
--check; no commit; header < 8192 bytes; report each corrected fixture with before/after.
