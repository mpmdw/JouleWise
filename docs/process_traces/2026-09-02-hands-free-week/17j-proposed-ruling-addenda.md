# Proposed addenda to MAGISTRATE-RULING-UNATTENDED-STAGE1 (object of Q6; not installed)

**R-6 addendum (proposed).** The night plan's stale check binds the MEASUREMENT checkout of record (D-171 item 5), not the driver checkout: plan schema `joulewise.night_plan.v2` carries `measurement_root` and `measurement_head`; `night_plan_stale` fires when the measurement checkout's HEAD differs from `measurement_head`; the driver checkout's HEAD is recorded in the census row and never refuses. v1 plans are retired fail-closed (`night_plan_malformed`). The installer checks both pins at install and none at uninstall.

**R-7 addendum (proposed).** The magistrate fast-forwards the measurement checkout deliberately before each arm; ordinary daytime work in the driver checkout no longer invalidates an armed night.

**R-9 addendum (proposed).** The stand-down DEADLINE and FORCE are owned by the launchd supervisor `com.joulewise.magistrate` (request file at t0 − 25 min; SIGTERM t0 − 16 min; SIGKILL t0 − 15 min by process-tree walk of the recorded session only; census verification after); the session's cooperative exit remains the preferred path and the only one that emails at stand-down; forced stand-downs are reported by the next session's first email. Arming stays outside the supervisor's charter.
