# ALIGN R0 desk checks

Status: **fail**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 884.134 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| smc | host | fail | 853.725 |

## smc (host)

```json
{
  "argv": [
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python",
    "-B",
    "/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/scripts/align_smc_enumerate.py",
    "--output",
    "/Users/edr/night-align/r0-v4-20261108T0115Z/smc",
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
  "check_seconds": 853.7253174169455,
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
  "stderr": "R0 refused/failed: NotQuiet: outside-tree CPU contention or unmeasured host CPU: {'interval': {'monotonic_ns': [2085766770084958, 2085796888444270], 'monotonic_raw_ns': [2085766770084124, 2085796888443291], 'wall_ns': [1794101429786302000, 1794101459904661000]}, 'error': None, 'elapsed_s': 30.118359312, 'clean': False, 'max_outside': {'pid': 61967, 'command': 'frauddefensed', 'start': 'Tue Nov 3 15:38:52 2026', 'cpu_s_per_s': 0.09197048123721502}, 'outside_over_limit': [{'pid': 61967, 'command': 'frauddefensed', 'start': 'Tue Nov 3 15:38:52 2026', 'cpu_s_per_s': 0.09197048123721502}], 'exited_over_limit': [], 'outside_listed': [{'pid': 61967, 'command': 'frauddefensed', 'start': 'Tue Nov 3 15:38:52 2026', 'cpu_s_per_s': 0.09197048123721502}, {'pid': 663, 'command': 'cloudd', 'start': 'Wed Oct 14 15:08:47 2026', 'cpu_s_per_s': 0.02523377824559696}, {'pid': 838, 'command': 'networkservicepr', 'start': 'Wed Oct 14 15:08:50 2026', 'cpu_s_per_s': 0.010956772132954788}, {'pid': 1, 'command': 'launchd', 'start': 'Wed Oct 14 15:07:52 2026', 'cpu_s_per_s': 0.006640467959389873}], 'outside_total_cpu_s_per_s': 0.18095275189267304, 'outside_process_count': 735, 'tree_cpu_s_per_s': 0.08466596648191277, 'tree_process_count': 4, 'kernel_task_cpu_s_per_s': None, 'kernel_task_included': True, 'host_busy_cpu_s_per_s': 0.3512793984572717, 'host_idle_cpu_s_per_s': 15.620976501529036, 'host_ticks': {'busy_ticks': 1058, 'idle_ticks': 47048, 'cpus': 16, 'ticks_per_s': 100.0, 'elapsed_s': 30.118475625}, 'host_error': None, 'outside_aggregate_cpu_s_per_s': 0.2666134319753589, 'unattributed_cpu_s_per_s': 0.08566068008268587, 'unattributed_resolution_cpu_s_per_s': 0.5186204245329418, 'aggregate_limit_s_per_s': None, 'aggregate_over_limit': False, 'unaccounted': [{'pid': 42411, 'command': 'ps', 'start': 'Sat Nov 7 17:30:29 2026', 'reason': 'exited'}], 'raw': [{'name': 'ps.txt', 'sha256': '3c451ddd9dd2e8ea192a4f87a12180c16cc78b42520957a70ac3f1b897fa5b84', 'size': 49629, 'path': None}, {'name': 'ps.txt', 'sha256': '7b048e5c8155ddc8c08d3df014acb4ffae4910afd54ded6a3e3e1c7b3af86dc8', 'size': 50241, 'path': None}], 'cpu_limit_s_per_s': 0.05, 'aggregate_cpu_limit_s_per_s': None, 'aggregate_above_0_05': True, 'regressed_counters': [], 'long_interval': False}\n",
  "stdout": "",
  "step_ruling": "docs/align/r0_step_test_ruling.md",
  "timeout_seconds": 3300
}
```
