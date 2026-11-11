Completed all three groups: mandatory DC-in gating with a 600-second outage bound, production HostLock preflight, and recorded power/NTP restoration across terminal and dead-man paths.

- Local commits: `19a862dc8`, `95ffa51c8`; clean tree on the requested branch, unpushed.
- Changed six runtime/smoke files, seven test files, and the [handoff report](docs/run_reports/2026-11-10-w1-reliability-r2.md).
- Verification: 288 focused tests passed, including 18 new cases. Compilation and diff checks passed; full suite omitted as instructed.

No implementation questions remain. Hardware behavior is **PROVISIONAL**: the lead must complete STRICT re-registration and native unplug, kill, dead-man, and read-back checks before W1 arms.