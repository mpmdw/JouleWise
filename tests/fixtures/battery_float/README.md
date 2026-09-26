# Battery ioreg fixtures

`float.ioreg` is one read-only `/usr/sbin/ioreg -r -c AppleSmartBattery`
capture from this Mac on 2026-09-25 while at float. Its `UpdateTime` is
1790373525; tests supply an observation wall time relative to that value.

`float-2026-09-25-2047.ioreg` is the real capture ex-03 of cold ruling
BFG-D-PARSER-ESC-01 (the same bytes as
`docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/17-real-ioreg-capture-2026-09-25-2050.txt`):
one read-only `/usr/sbin/ioreg -r -c AppleSmartBattery` at float, 17337 bytes,
64 LF-terminated lines, no CR, sha256
`582475270c35c51cc05c2020f500d8c7dfba3eb9a6436a0186cb5ce18a851631`. Its
`UpdateTime` is 1790394405. `tests/battery_float_corpus.py` builds the
ruling's grammar corpus from it.

The other files preserve the real output bytes except for the exact edits below:

- `charging-synthetic-from-real.ioreg`: top-level `IsCharging = No` → `Yes`;
  top-level `InstantAmperage = 0` → `739`. This charging case is synthetic.
- `stale-synthetic-from-real.ioreg`: top-level `UpdateTime = 1790373525` → `1`.
- `malformed-synthetic-from-real.ioreg`: top-level `InstantAmperage = 0` → `broken`.

No nested property is rewritten.
