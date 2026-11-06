# ALIGN R0 desk checks

Status: **fail**. Selection data; no R1/hardware-control claim.
Complete R0: **False**. Evidence: live_desk.
Total wall duration: 20.788 seconds.

| Check | Model | Status | Wall seconds |
|---|---|---|---|
| host | host | pass | 0.322 |
| disk | host | diagnostic | 19.776 |
| host-identity | host | pass | 0.304 |
| model-load | D | fail | 0.253 |

## host (host)

```json
{
  "check": "host",
  "check_seconds": 0.3221592919435352,
  "note": "Read-only desk readiness; R1 lever adoption and arm readiness require their own gates.",
  "probes": {
    "physical_memory": {
      "status": "pass",
      "stdout": "137438953472\n"
    },
    "pmset_battery": {
      "status": "pass",
      "stdout": "Now drawing from 'AC Power'\n -InternalBattery-0 (id=23265379)\t100%; charged; 0:00 remaining present: true\n"
    },
    "pmset_custom": {
      "status": "pass",
      "stdout": "Battery Power:\n Sleep On Power Button 1\n powermode            0\n standby              1\n ttyskeepawake        1\n hibernatemode        3\n powernap             1\n hibernatefile        /var/vm/sleepimage\n displaysleep         5\n womp                 0\n networkoversleep     0\n sleep                0\n lessbright           1\n tcpkeepalive         1\n disksleep            10\nAC Power:\n Sleep On Power Button 1\n powermode            0\n standby              1\n ttyskeepawake        1\n hibernatemode        3\n powernap             1\n hibernatefile        /var/vm/sleepimage\n displaysleep         0\n womp                 1\n networkoversleep     0\n sleep                0\n tcpkeepalive         1\n disksleep            10\n"
    },
    "pmset_thermal": {
      "status": "pass",
      "stdout": "Note: No thermal warning level has been recorded\nNote: No performance warning level has been recorded\nNote: No CPU power status has been recorded\n"
    },
    "wired_limit": {
      "status": "pass",
      "stdout": "iogpu.wired_limit_mb: 0\n"
    }
  },
  "readiness": {
    "observed_lowpowermode": null,
    "observed_power_mode": "0",
    "on_ac": true,
    "power_mode_ok": true
  },
  "status": "pass"
}
```

## disk (host)

Free after present weights: 83629871104 bytes (R0 report-only; no free-space or offload gate).
W1 arm gate, evaluated separately after R0: ≥80000000000 bytes and configured offload hash matches.
SMC capture: 1800 s; journal estimate: 29491200 bytes.

| Model | Observed bytes | Design download bytes | Difference |
|---|---|---|---|
| D | 29531527104 | 29531521322 | 5782 |
Configured W1 offloads (not verified during R0): [].
W1 two copies: 37.4 GB; D windows two copies: 52.9 GB (rounded planning estimates). D and 30B anchor file hashes are in JSON.

## host-identity (host)

```json
{
  "check": "host-identity",
  "check_seconds": 0.30446658306755126,
  "expected_hw_model": "Mac15,9",
  "hw_memsize": 137438953472,
  "hw_model": "Mac15,9",
  "minimum_memory_bytes": 137438953472,
  "status": "pass"
}
```

## model-load (D)

```json
{
  "check": "model-load",
  "check_seconds": 0.2527303749229759,
  "error": "PackageNotFoundError: No package metadata was found for mlx",
  "model": "D",
  "status": "fail"
}
```
