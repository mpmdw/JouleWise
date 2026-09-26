# Exhibit 00 — the binding directive and the finding behind it

## Issue #421 (author mpmdw = Ed; label directive; BINDING body, verbatim)

# BINDING TEXT (Ed, 2026-09-25): battery float is MANDATORY for every measurement window; anything germane to the verity of the science is mandatory

**Ed's words:** "make it binding obviously anything germane to the verity of the science is mandatory"

**1. The battery gate, for every measurement window** (W1/W2, calibration, evidence and claim-bearing windows; not only W1):
- **At arm and immediately before publication/t0**, read `ioreg -r -c AppleSmartBattery` and require:
  - `ExternalConnected = Yes`;
  - `IsCharging = No`;
  - |InstantAmperage| ≤ 200 mA (two's complement handled).
- **Log** the raw values to the stage and the arm record.
- **Failure postpones the arm.** It is never waived.
- **Harvest check:** if any slot records `is_charging = true`, or its battery current exceeds the bound, the window is confounded and not used for any claim or acceptance. The arm notice and the harvest record say so.
- **The code-level t0 gate (BATTERY-FLOAT-GATE-01)** remains a full-gate lane and should land promptly. Until it does, the procedural check above is mandatory.

**2. The general principle, binding on all roles.** A check, disclosure or gate that bears on whether a measured or claimed number is TRUE is mandatory. It is not at the magistrate's discretion and not traded against schedule. Examples: instrument state, machine quietness, clock anchoring, calibration binding, contamination, and the statistical adequacy of a claim rule. Discretion applies only to things that cannot change a number (ceremony, docs, bookkeeping; see #415). When in doubt, treat the item as germane.

**Context:** issue #420. Ed changed the charge setting from an 80 % cap to 100 % on 2026-09-25, and the battery charged all afternoon. Charging adds heat (SoC temperature and leakage) and invalidates wall-meter readings.


## Issue #420 (author mpmdw, filed by interactive seat 4b; a finding, verbatim)

**Finding for the W1 arm (interactive seat 4b, 2026-09-25):** battery charge state is recorded but not gated.

- Ed changed the charge setting from an 80 % cap (used for most of the project, including the July data) to 100 %. At ≈12:30–12:50 PDT today the battery was charging at 2.7–3.9 A (82 % → 96 %).
- The harness records `is_charging` and `battery_state` (`joulewise/environment.py:215`, `:878`), but no admission or t0 check refuses on them.
- **Risks:**
  - charging during a window adds heat, which raises SoC temperature and leakage;
  - a battery supplying the load makes wall-meter readings meaningless (one 09-23 observation at 100 %: −439 mA while on AC).
- **Evidence in progress:** a read-only logger (`/tmp/4b-osaudit/battery.jsonl`, every 30 s, until ≈15:30 PDT) will show whether the battery floats at ≈ 0 mA once full.

**Recommended minimum for W1 (the magistrate's call):**
1. At arm and at t0, read `ioreg -r -c AppleSmartBattery`.
2. Require `IsCharging = No` and |InstantAmperage| ≤ 200 mA.
3. Record the values in the arm record; postpone if they fail.

A proper t0 gate, BATTERY-FLOAT-GATE-01, is a full-gate lane.

