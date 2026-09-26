# Exhibit 30: magistrate synthesis and proposals (Opus 5.5, activation ed17a643, 14:50 PDT 09-25)

This exhibit states the magistrate's arguments. It carries no authority.

## Physical picture

The machine is an M3 Max MacBook Pro running on AC. Ed raised its charge limit today from 80 % to 100 %.

- At 80 % the battery sat above its limit, and the charger carried no charging current.
- At 100 % the battery charges after any dip. Reads from 12:30 to 14:38 were 1.7–3.9 A, then 0.9–1.1 A at 99 %, with "finishing charge".
- Charging dissipates heat in the pack and charger. It raises the enclosure and SoC temperature, and with it the SoC's leakage power.
- powermetrics measures on-SoC rails (cpu/gpu/ane). Charging current does **not** pass through those rails, so the direct energy error in a powermetrics number is not I×V of the charge current. The error is the thermal path: leakage rises with temperature.
- A wall meter would count the charge power directly: 200 mA at 12.95 V ≈ 2.6 W, i.e. 1.24 kJ per 480 s capture.
- So the 200 mA bound is a gross screen for powermetrics-only windows. It is not an energy-error bound for wall-meter windows.

## Where the two blind seats agree (Sol 6.0 xhigh; Astra 6 high)

- **A1.** One shared parser over raw `ioreg -r -c AppleSmartBattery`, with unsigned-64 two's complement (n ≥ 2^63 → n − 2^64). It fails closed on missing, duplicate, malformed or nested-lookalike fields.
- **A2.** t0 refusal inside existing row C3 (not a new C6), next to the AC check at `night_gate.py:1488`, with a new reason code. A probe failure keeps `night_probe_error`. Arm: `evidence_night.check` plus a fresh read immediately before `publish_install`'s `os.replace`. A t0 battery refusal joins `arm_retry.ZERO_CAPTURE_MACHINE_REFUSALS`, so it is covered by D-182's one-successor route and is never a same-plan retry.
- **A3.** Do NOT add `battery` to `SAMPLERS`. `joulewise/adapters/powermetrics.py` is in `ESTIMATOR_CODE_PATHS`, and the change would move a pinned estimator-code digest and the captured stream.
- **A4.** Per-slot before/after ioreg brackets in the derivation writer (`validate_powermetrics_fiducial.py`: before sampler start, after teardown, including error paths). The raw bytes go in `raw/`, and they are hashed into `instrument_evidence.json` and the manifest artifacts. The registered shell chain is unchanged.
- **A5.** One authenticating consumer re-parses the raw bytes rather than trusting a stored boolean. It evaluates **all** slots of the window, including ordinary-invalid ones, before any B value is read: in `registration_dry_run`, in `_prepare_candidate` before `_select_members`, and in the lower calibration candidate loader. One failing or missing bracket makes the whole window `battery_float_confounded` / `battery_float_evidence_missing`.
- **A6.** Other window kinds need the same brackets and consumers before they run: quiet-predicate envelopes, controller/scored bundles, and the scored reducer's `capture_windows` boundary, which today authenticates nothing behind `bundle_sha256`.
- **A7.** No during-slot polling in the first cut. The controller's measured interval is deliberately quiescent. An ioreg subprocess inside the derivation slot would add CPU pulses to a pulse-energy measurement, and observer impact is uncharacterized. Brackets cannot prove "no charging in between"; that limit is disclosed.
- **A8.** Registration: `protocol_v3.json` does not change. The whole-window exclusion **does** change Revision 5's membership rule ("every valid resolved member is retained"), so a prospective addendum is needed before W1.

## Where they split

- **S1.** Sol wants two PRs (admission first, then recording plus consumers). Astra wants one vertical PR and says a t0-only PR must not close the lane.
- **S2.** After a captured window is confounded: Astra says halt and return to council unless a replacement rule is installed before capture. Sol wants the addendum to name the count handling and the "no top-up" consequence.

## Magistrate proposals

- **P1 (split by window kind, not by layer).** PR **BFG-D** covers A1, A2, A4 and A5: admission plus derivation/calibration recording and consumers. It is everything W1/W2 need and must merge before W1 arms. PR **BFG-S** covers A6: quiet envelopes, controller/scored bundles, scored reducer and bundle reader. It must merge before any non-derivation window arms. Rationale: every window that runs is fully covered, W1 is not held for code it never exercises, and neither PR alone is labelled as closing the lane.
- **P2 (addendum A-R5b, prospective, before W1).** Proposed text: "Battery float (directive #421). Each derivation window is admitted only if, at arm, immediately before publication and at t0, `ioreg` shows ExternalConnected = Yes, IsCharging = No and |InstantAmperage| ≤ 200 mA. Every slot records raw before/after ioreg brackets. If any slot's bracket is missing, unparseable or fails that predicate, the whole window is battery-confounded. It is checked before any B value is read, its slots are not members, it does not count toward W1/W2's valid-slot stops, and it is retained and disclosed. A confounded window is replaced once by a fresh window under the same protocol, at least 6 h after the previous window, because the confound is decided from instrument state alone and before any B is read, so replacement cannot select on outcome. A second consecutive confounded window stops the epoch and returns to council." The seal PR #418 merges as ruled, and A-R5b goes on top as its own labelled amendment with a new digest pinned in the W1 notice.
- **P3 (threshold).** Keep ≤ 200 mA as #421 fixes it for powermetrics-only windows, where it is a gross screen of thermal state and the existing settle and thermal gates stay in force. Before any wall-meter window, a tighter bound is sized to that instrument by lane WALL-METER-GAIN-01. #421 says in-doubt items are mandatory, so this stays a registered obligation, not a discretion.
- **P4 (W1 frozen calibration plan; W1 arm-scripts report F1).** Keep n1's `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json`, byte-pinned in the notice. W1 re-runs the same registered derivation (same pulse protocol v3, same writer) under the launch-context cure. Nothing in Revision 5 or rulings v2.1 names a different plan, and changing it would add a second difference from n1/n2.
- **P5 (sequencing).** #418 merges (row 9 replay is running) → BFG-D full gate → A-R5b registration PR (full gate) → W1 arm under NIGHT_HANDBACK, with the procedural battery gate in the arm scripts as well. BFG-S runs in parallel and does not block W1.
