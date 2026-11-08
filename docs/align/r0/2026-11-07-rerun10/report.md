# ALIGN R0 desk checks

Status: **fail**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 987.167 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| smc | host | fail | 956.777 |

## smc (host)

```json
{
  "argv": [
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python",
    "-B",
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/scripts/align_smc_enumerate.py",
    "--output",
    "/Users/edr/night-align/r0-v4-20261108T0224Z/smc",
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
  "check_seconds": 956.7773645839188,
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
  "stderr": "R0 refused/failed: NotQuiet: outside-tree CPU contention or unmeasured host CPU: {'interval': {'monotonic_ns': [2090006586680937, 2090042473813708], 'monotonic_raw_ns': [2090006586680104, 2090042473812770], 'wall_ns': [1794105669602898000, 1794105705490030500]}, 'error': None, 'elapsed_s': 35.887132771, 'clean': False, 'max_outside': {'pid': 794, 'command': 'routined', 'start': 'Wed Oct 14 15:08:49 2026', 'cpu_s_per_s': 0.05210781290142887}, 'outside_over_limit': [{'pid': 794, 'command': 'routined', 'start': 'Wed Oct 14 15:08:49 2026', 'cpu_s_per_s': 0.05210781290142887}], 'exited_over_limit': [], 'outside_listed': [{'pid': 794, 'command': 'routined', 'start': 'Wed Oct 14 15:08:49 2026', 'cpu_s_per_s': 0.05210781290142887}, {'pid': 1, 'command': 'launchd', 'start': 'Wed Oct 14 15:07:52 2026', 'cpu_s_per_s': 0.005015725306027989}], 'outside_total_cpu_s_per_s': 0.08721789004359072, 'outside_process_count': 730, 'tree_cpu_s_per_s': 0.08582463301411788, 'tree_process_count': 4, 'kernel_task_cpu_s_per_s': None, 'kernel_task_included': True, 'host_busy_cpu_s_per_s': 0.2658335206939969, 'host_idle_cpu_s_per_s': 15.6953237805137, 'host_ticks': {'busy_ticks': 954, 'idle_ticks': 56326, 'cpus': 16, 'ticks_per_s': 100.0, 'elapsed_s': 35.887122042}, 'host_error': None, 'outside_aggregate_cpu_s_per_s': 0.18000888767987902, 'unattributed_cpu_s_per_s': 0.0927909976362883, 'unattributed_resolution_cpu_s_per_s': 0.4333029441564181, 'aggregate_limit_s_per_s': None, 'aggregate_over_limit': False, 'unaccounted': [{'pid': 51860, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51861, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51862, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51863, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51864, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51865, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51866, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51867, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51868, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 51869, 'command': 'contactsd', 'start': 'Sat Nov 7 18:40:32 2026', 'reason': 'exited'}, {'pid': 52128, 'command': 'ps', 'start': 'Sat Nov 7 18:41:09 2026', 'reason': 'exited'}], 'raw': [{'name': 'ps.txt', 'sha256': '743a0ac3764b0ad903baff2773609a9b966f226c3b6faefa8c49080b098a17fa', 'size': 50173, 'path': None}, {'name': 'ps.txt', 'sha256': '4814741face65d17effc54b498a9a161ad862f6b6f5a7ad8c902b47ef04b8a7e', 'size': 49901, 'path': None}], 'cpu_limit_s_per_s': 0.05, 'aggregate_cpu_limit_s_per_s': None, 'aggregate_above_0_05': True, 'regressed_counters': [], 'long_interval': False}\n",
  "stdout": "",
  "step_ruling": "docs/align/r0_step_test_ruling.md",
  "timeout_seconds": 3300
}
```
