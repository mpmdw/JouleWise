# ALIGN R0 desk checks

Status: **fail**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 92.053 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| smc | host | fail | 61.664 |

## smc (host)

```json
{
  "argv": [
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python",
    "-B",
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/scripts/align_smc_enumerate.py",
    "--output",
    "/Users/edr/night-align/r0-v4-20261108T0140Z/smc",
    "--gpu-step",
    "--idle-seconds",
    "300",
    "--idle-max-seconds",
    "1200",
    "--load-seconds",
    "900",
    "--recovery-seconds",
    "600"
  ],
  "check": "smc",
  "check_seconds": 61.66350070782937,
  "exit_code": 3,
  "note": "Idle plus load-step selection; R1 still owns thermal-control qualification.",
  "selection_status": "PROVISIONAL",
  "smc_source_commit": "58525031a",
  "smc_step_budget": {
    "capture_seconds": 2700,
    "journal_bytes_estimate": 143202600,
    "journal_bytes_per_slot_estimate": 53038,
    "journal_estimate_note": "Measured 95,467,641 bytes /1,800 slots, rounded up; verify after enumeration.",
    "profile": {
      "idle_max_seconds": 1200,
      "idle_seconds": 300,
      "load_seconds": 900,
      "recovery_seconds": 600
    },
    "sample_period_seconds": 1,
    "timeout_seconds": 3300
  },
  "status": "fail",
  "stderr": "R0 refused/failed: NotQuiet: outside-tree CPU contention or unmeasured host CPU: {'interval': {'monotonic_ns': [2086251946842020, 2086282633041979], 'monotonic_raw_ns': [2086251946841437, 2086282633041291], 'wall_ns': [1794101914963058500, 1794101945649258500]}, 'error': None, 'elapsed_s': 30.686199959, 'clean': False, 'max_outside': {'pid': 415, 'command': 'WindowServer', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.08375100219100116}, 'outside_over_limit': [{'pid': 415, 'command': 'WindowServer', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.08375100219100116}, {'pid': 676, 'command': 'ControlCenter', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.05702889254251698}], 'exited_over_limit': [], 'outside_listed': [{'pid': 415, 'command': 'WindowServer', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.08375100219100116}, {'pid': 676, 'command': 'ControlCenter', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.05702889254251698}, {'pid': 438, 'command': 'airportd', 'start': 'Wed Oct 14 15:08:39 2026', 'cpu_s_per_s': 0.01792336622765412}, {'pid': 635, 'command': 'sysmond', 'start': 'Wed Oct 14 15:08:46 2026', 'cpu_s_per_s': 0.011079899122550899}, {'pid': 389, 'command': 'locationd', 'start': 'Wed Oct 14 15:08:38 2026', 'cpu_s_per_s': 0.009776381578715715}, {'pid': 1, 'command': 'launchd', 'start': 'Wed Oct 14 15:07:52 2026', 'cpu_s_per_s': 0.009776381578693486}, {'pid': 612, 'command': 'com.apple.Driver', 'start': 'Wed Oct 14 15:08:46 2026', 'cpu_s_per_s': 0.005865828947239802}], 'outside_total_cpu_s_per_s': 0.22387913815260388, 'outside_process_count': 725, 'tree_cpu_s_per_s': 0.05507361622677355, 'tree_process_count': 3, 'kernel_task_cpu_s_per_s': None, 'kernel_task_included': True, 'host_busy_cpu_s_per_s': 0.35195034185276924, 'host_idle_cpu_s_per_s': 15.628550457939912, 'host_ticks': {'busy_ticks': 1080, 'idle_ticks': 47958, 'cpus': 16, 'ticks_per_s': 100.0, 'elapsed_s': 30.686147208}, 'host_error': None, 'outside_aggregate_cpu_s_per_s': 0.2968767256259957, 'unattributed_cpu_s_per_s': 0.07299758747339183, 'unattributed_resolution_cpu_s_per_s': 0.5047872226272269, 'aggregate_limit_s_per_s': None, 'aggregate_over_limit': False, 'unaccounted': [{'pid': 43953, 'command': 'ps', 'start': 'Sat Nov 7 17:38:34 2026', 'reason': 'exited'}], 'raw': [{'name': 'ps.txt', 'sha256': '58b0d0e2b49aefc377ad1d6277a2186bdde804955e73ba1dc6d17932c9be347d', 'size': 49493, 'path': None}, {'name': 'ps.txt', 'sha256': '70a5f34f07d348e546922ef067cc8338a4653ec89cffe6de3d17b7c0a0192de0', 'size': 49493, 'path': None}], 'cpu_limit_s_per_s': 0.05, 'aggregate_cpu_limit_s_per_s': None, 'aggregate_above_0_05': True, 'regressed_counters': [], 'long_interval': False}\n",
  "stdout": "",
  "step_ruling": "docs/align/r0_step_test_ruling.md",
  "timeout_seconds": 3300
}
```
