# Astra operations audit round 10 for PR #804 and PR #807

Mission M0 selected CLOSE-OFFLOAD-01 on the agent lane. The lead assigned
findings 2, 7, 8 and 10 to Builder B. The starting heads were `ccfe442b6`
for PR #804 and `297129cae` for PR #807. The previous retarget report
records the RL-174 D acceptance and live gates.

| Finding | Repair and regression |
| --- | --- |
| 2 | Controller-owned close compares the exact standing fence purpose, PID and deadline under the desk fence lock. It still runs the runner census and applies other configured fences. The regression covers the standing fence, lock contention, mismatched and short leases, and the live-runner and census-error results. |
| 7 | A previously verified cloud object is downloaded and streamed through the shared digest and size calculation. The low-space regression rejects same-size corrupt bytes, then reclaims with a valid SSD receipt while stage temp directory creation would fail with ENOSPC. |
| 8 | Both branches recover a publisher-named same-inode temp under the plan lock and sync the marker directory. The regression covers lock contention and preserves unrelated links. PR #807 also covers recovery of its interrupted retirement receipt. |
| 10 | The private MBP config's `raw_retention_paths` array applies to rotation, catch-up, and interrupted retirements. The regressions cover an older designated OUT across checks and the surviving files in an interrupted retirement. |

The regression tests failed against the starting heads. A baseline replay
also let the old config accept the new allowlist key to verify that the old
selector deleted both the designated older OUT and the surviving files
from an interrupted retirement.

Local verification used the relevant offload, fixture census and state
modules with process-signaling integration cases excluded. The local
harness intercepted attempts to send process signals. Hosted CI provides
the canonical sharded suite. The PR bodies record the current heads and
the audit regression names. Testing used synthetic source and control
files, synthetic provider observations and no measurement-host access.

The controller handoff is in the close runbook and the private standing-item
draft. PR #807 stays PROVISIONAL pending the lead's RL-174 D blind check,
native GUI production-key round trip, RL-171 close-interval floor recheck
and standing-item issue. The lead owns the merge decisions.
