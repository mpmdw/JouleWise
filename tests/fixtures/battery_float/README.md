# Battery ioreg fixtures

`float.ioreg` is one read-only `/usr/sbin/ioreg -r -c AppleSmartBattery`
capture from this Mac on 2026-09-25 while at float. Its `UpdateTime` is
1790373525; tests supply an observation wall time relative to that value.

The other files preserve the real output bytes except for the exact edits below:

- `charging-synthetic-from-real.ioreg`: top-level `IsCharging = No` → `Yes`;
  top-level `InstantAmperage = 0` → `739`. This charging case is synthetic.
- `stale-synthetic-from-real.ioreg`: top-level `UpdateTime = 1790373525` → `1`.
- `malformed-synthetic-from-real.ioreg`: top-level `InstantAmperage = 0` → `broken`.

No nested property is rewritten.
