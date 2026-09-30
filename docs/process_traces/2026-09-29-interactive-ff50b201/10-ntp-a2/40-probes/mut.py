import subprocess, sys, shutil
M = sys.argv[1]
muts = {
 "R3": ("scripts/run_night.py", "        if cleanup_only:\n            return (None if cleanup_proven else", "        if False:\n            return (None if cleanup_proven else",
        ["tests.test_run_night.CaptureRefusalRecordTests.test_R3_A_early_cleanup_leaves_verdict_to_failed_proof"]),
 "R1": ("joulewise/network_time_window.py", '            and "pid" in started and "pgid" in started\n', "",
        ["tests.test_network_time_window.WindowTests.test_R1_recovery_rejects_missing_identity_keys",
         "tests.test_network_time_window.WindowTests.test_R1_recovery_rejects_missing_pid_with_launch_error",
         "tests.test_run_night.NightDriverTests.test_R1_driver_rejects_incomplete_nonlaunch_claims",
         "tests.test_run_night.NightDriverTests.test_R1_deadman_rejects_incomplete_nonlaunch_claims"]),
 "R2": ("scripts/run_night.py", '    if result.returncode == 0 and not lines:\n        return {pgid: (False, ["census_ambiguous: exit 0 with no lines"])\n                for pgid in chunk}\n', "",
        ["tests.test_run_night.NightDriverTests.test_R2_empty_successful_batch_is_not_capture_proof"]),
}
for name, (f, old, new, tests) in muts.items():
    p = f"{M}/{f}"; orig = open(p).read()
    assert orig.count(old) == 1, (name, orig.count(old))
    open(p, "w").write(orig.replace(old, new))
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=M, capture_output=True, text=True)
    open(p, "w").write(orig)
    tail = [l for l in r.stderr.splitlines() if l.startswith(("AssertionError", "Ran ", "FAILED", "OK", "ERROR:", "FAIL:")) or "Error:" in l]
    print(f"== deletion {name}: exit={r.returncode}"); print("\n".join(tail))
# sanity: unmutated copy passes the same tests
alltests = [t for v in muts.values() for t in v[3]]
r = subprocess.run([sys.executable, "-B", "-m", "unittest", *alltests], cwd=M, capture_output=True, text=True)
print("== unmutated control:", r.returncode, r.stderr.strip().splitlines()[-1])
