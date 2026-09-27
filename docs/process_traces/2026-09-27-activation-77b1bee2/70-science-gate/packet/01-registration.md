# 01 — Registration and arm provenance

Primary source: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`). Whole-file committed digest also appears in candidate `derivation_notes.preregistration`.

Runbook item 1: `docs/phase_2/derivation_night_runbook.md` (sha256 `4bc879fe0d49665c697dd4d6692e0e8aa4953b355a7e45a49f07e0a93887e13b`), lines 3123–3126. Its three-night wording is adapted to Revision 5’s two actual sessions, W1 and W2; W3 was not opened.

Revision 5 exact lines 600–647 (including the separator blank line) and A-R5b exact lines 648–664 follow verbatim.

```text
# Revision 5 (2026-09-25; sealed 2026-09-25 at PR-L merge 9b750bf3)

**STATUS:** Revision 4 was drafted, never sealed, and is held at fallback tag `acc-v4-fallback` = `ea10e3c8`. Revision 5 is prospective: no W1 capture may be armed until the literal launch-context placeholders below are replaced with verified values and this whole text's digest is pinned in the arm material. The issuer refuses candidate preparation while any placeholder remains.

**Authority:** council ACCEPTANCE-25G83-02 under D-184 **Addendum (Ed, 2026-09-24 ≈04:40 PDT)**, as finally ruled by `docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md` §5 R4, R5, R9, R10, R17. This revision amends Revision 2's `## What replaces it`, `## On PASS`, and `## On FAIL` sections, Revision 1's “Stopping.” and dry-run outputs under “Blindness.”, and drops Revision 1's “Screen challenge.” as an issuance veto for this epoch. Wherever Revision 2 names r6 as the acceptance in force, read `d079_calibration_acceptance_v2_n17_r7`; r6 and r7 operatives are identical. Revision 3's chain digest in force remains unchanged.

## Registered epoch and operating condition

The six identity fields are `os_build` = `25G83`, `hardware_model: Mac15,9`, `power_policy: ac_high_power`, `sampling_interval_ms: 100`, `estimator_revision: joint_loss_sublevel_interval_branch_v2`, and `pulse_protocol_id: powermetrics_pulse_fiducial_v3`. The pinned operating condition is captures launched by a launchd agent with `ProcessType=Interactive`, template at commit 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87, template digests e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8 and 1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd. The first digest is the sha256 of configs/launchd/com.joulewise.night.plist.template (shared by the night and dead-man labels) and the second of configs/launchd/com.joulewise.night-probe.plist.template, both read at that commit. Each window's rendered-plist digests are plan-specific and are recorded in that window's arm evidence and probe receipt by the installer; they are not part of this text. Sealing replaces these three literals after PR #412 lands on main and before W1's arm notice: the commit is the one GitHub reports as PR #412's merge commit (`gh pr view 412 --json mergeCommit`); each digest is `git show <that commit>:<template path> | shasum -a 256`. The placeholder count (`grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:'` on this file) must be 0 before the arm-notice digest is taken; seal the literal tokens without backticks; at the seal, replace the header parenthetical "sealing pending PR-L pins" with "sealed <YYYY-MM-DD> at PR-L merge <first 8 hex of the commit>" (amendment A-R5a-1, `docs/decision_log.md`). Launch context sets the sampler cadence; this condition is part of the registered experiment.

## Sample, stops and blindness

W1 and W2 are derivation-kind windows of 12 declared slots each, at least 6 h apart; each has a 600 s settle and 600 s slot start-to-start cadence. W1 is derivation window one. At W1 harvest, the pin-free cadence report reads raw plists before any B value is read; if the median of the per-capture median native frame lengths is above 150 ms, stop: no W2, return to council. Then the count-only dry run runs before any B value is read. If it reports fewer than 6 valid of 12, stop: no W2, return to council. W2 then runs. W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid, and is another 12-slot window. Every valid resolved member is retained. Retained n ≥ 12 is the issuance floor; 12/13 order-statistic coverage, the floored S and t(0.995,11) support it. The earlier 0.245 s yield reason no longer applies. No B-based exclusion or outcome-driven top-up is permitted. B values are read only after the terminal session. Rules are fixed here before capture. The dry run may report valid count and “median native frame length,” alongside the existing counts, states and exclusion mechanisms; it reports no B value, screen or comparison.

Revision 2's equivalence look is NOT taken for this epoch. Reason: the r7 envelope's ceiling is its July corpus maximum at ≈120 ms frames; B grows with frame length; a 12-draw look cannot distinguish a +6 % regime from an identical one. W1 is derivation window one. There is no PASS continuation branch or FAIL branch for this epoch.

## Disclosed design inputs

The eleven valid 2026-09-19 n1/n2 B values, seen before this revision and disposed as diagnostics under `D-126-disposition-25G83-v3-2026-09-25`, are (seconds), in capture order: `0.041133514338919874`, `0.04200278099548145`, `0.172710636067422`, `0.03255031906139217`; `0.04103035733376445`, `0.04337273381948624`, `0.028250396657612444`, `0.035576770468514644`, `0.03487995875720681`, `0.13333095801710004`, `0.036897960254235855`. They are never members of the new registration.

The observed native-frame distributions, in the ruling's I/SH/D order (context; files; intervals; median; p95; maximum; fraction >0.25 s; fraction >0.1833 s), are:

| Context | Files | Intervals | Median | p95 | Maximum | >0.25 s | >0.1833 s |
|---|---:|---:|---:|---:|---:|---:|---:|
| I, session C | 21 | 6155 | 131.6 ms | 134.8 ms | 140.8 ms | 0 | 0 |
| I, session 2 | 12 | 3510 | 131.6 ms | 134.8 ms | 143.9 ms | 0 | 0 |
| SH, session C | 18 | 5496 | 121.2 ms | 125.2 ms | 134.1 ms | 0 | 0 |
| D, session 2, display ON | 3 | 703 | 243.3 ms | 278.6 ms | 296.4 ms | 43.5 % | 83.2 % |
| D, n1 night 09-19 | 30 | 10308 | 247.9 ms | 274.1 ms | 353.3 ms | 46.4 % | 82.9 % |

## Issuance arithmetic and barriers

The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch: on an identical instrument it would falsely refuse 16.3 % of the time. Count retained B > 0.075 s. Two or more mark the candidate `excursion_limited`, requiring the estimator lane before a phase-split claim. Any member B > 0.25 s refuses issuance with the `PLATEAU_INSET_S` mechanism named; 0.25 s is that protocol's plateau inset. No B value is excluded. S = max(corpus range quantized to 1e-6 s, 0.010818 s); C = max(predecessor C, successor Q99, S). If C = S, record `zero_headroom` and proceed with issuance; drift above S is refused by the operative bracket.

The physical barriers are pulse interiors, SNR, detection of all 59 pulses, edge coverage, anchor feasibility, pre/post brackets, settle and slot cadence, blindness, and verified Interactive launch context. Calendar-day spacing, n ≥ 19, the predecessor screen challenge, and strict S < C are not physical barriers for this epoch.

## Stale-number audit from record 37, re-keyed to 25G83/v3 at ≈132 ms

| Historical number | Role | Revision 5 disposition | Reason |
|---|---|---|---|
| 0.032898493715362 s | r7 preflight level screen | Replace as operative with new corpus maximum quantized to 1e-15 s; retain count above r7 as diagnostic. | The 132 ms operating condition changes B; r7's 120 ms maximum is not this epoch's screen. |
| 0.009724 s | r7 bracket screen | Replace with S = max(new quantized range, 0.010818 s). | The successor corpus sets its own range; the D-125 floor remains. |
| 0.010164834757777545 s (≈0.010165 s) | predecessor drift ceiling | Retain as predecessor-C input, then C = max(predecessor C, new Q99, S). | D-125 lineage monotonicity forbids lowering the ceiling. |
| 0.010818 s | D-125 genesis S floor | Retain. | It is independent of r7 cadence. |
| `calibration_bracket_max_drift_s` 0.010 s | production policy | Retain as policy until atomic G2-a re-freeze reconciles it with S and C. | It is a separate, conservative bound, not the new S or C. |

The historical r7 maximum-plus-range 0.04262208300415633 s remains diagnostic only. The simulation of W1 → futility → W2 → count-only W3, with all valid members retained and no equivalence branch, is `docs/calibration/acc_25g83_rev5_simulation.md`; its finite-sample bounds are a desk check, not a release criterion.

# Revision 5 — Amendment A-R5b (2026-09-25): battery float (directive #421)

Revision 5 above is sealed; not one word of it is edited here. This amendment adds one outcome-independent, mechanism-named exclusion decided from instrument state alone, and the rules that follow from it. It authorizes no window and licenses no measurement.

**Predicate.** A battery-float observation is one run of `/usr/sbin/ioreg -r -c AppleSmartBattery` whose raw standard output is retained. It PASSES when exactly one AppleSmartBattery object is present and, read only from that object's top-level property lines, `ExternalConnected = Yes`, `IsCharging = No`, `|InstantAmperage| ≤ 200 mA`, and the object's `UpdateTime` is no more than 180 s before the observation's wall time. A printed integer at or above 2^63 is read as that value minus 2^64 (two's complement; example: `18446744073709551458` reads −158 mA). A missing, duplicated, malformed or unreadable property, a failed or timed-out probe, a stale `UpdateTime`, or more than one object is not a pass. `Amperage` is recorded but never substituted for `InstantAmperage`. Each observation also records `Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `CurrentCapacity`, `AppleRawCurrentCapacity`, `AppleRawMaxCapacity` and `UpdateTime`.

**Admission.** A window is admitted only if the predicate passes at the arm check, again immediately before publication, and again at t0 inside the night gate's C3 row (refusal code `night_refused_battery_float`; probe failures are `night_probe_error`). A t0 or arm refusal with zero capture is a machine-state refusal under D-182: it licenses one new-plan successor on D-182's terms and is never a same-plan retry and never waived.

**Per-slot evidence.** Every derivation slot whose capture writer reaches its custody directory records one observation before the capture's first clock stamp is taken and one after its last clock stamp is taken, so that neither observation falls inside the interval the clock anchor is computed from and neither overlaps the sampler's life. The raw bytes are retained under the slot's custody as `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`; their SHA-256 digests, the verbatim property lines and the parsed values are recorded under the key `battery_float` in the hashed `instrument_evidence.json`. A failing or absent observation does not change the writer's exit path. The registered protocol, chain digest, sampler set, estimator-code pins and the estimator's clock-stamp inputs are unchanged.

**Window verdict.** Before the cadence report, before the count-only dry run and before any B value is read, every slot of the window that has a finalized ledger row, whatever its disposition, is checked from its raw bytes alone: both observations must be present, authenticated against the recorded digests, re-parsed, and must pass the predicate. One slot failing the predicate makes the whole window `battery_float_confounded`; one slot with a missing, stale, unparseable or unauthenticated observation makes it `battery_float_evidence_missing`. Either verdict is final for that window. A declared slot the window never reached (`window_exhausted`) carries no obligation.

**Consequences.** A window with either verdict is retained and disclosed. None of its slots is a member; none counts toward the "fewer than 6 valid of 12" stop, the 150 ms cadence stop (its cadence report is produced as a diagnostic only), n, or W3's trigger; its B values are not read before issuance is decided and are diagnostics afterwards. The issuer computes the verdict itself from raw bytes for every derivation-kind session it is asked to consider or that would otherwise refuse issuance under addendum A-7; the operator names the excluded sessions separately and issuance refuses unless the two sets are equal, so no clean window can be declared confounded and no confounded window can be omitted. The harvest record, the candidate's derivation notes and the next arm notice name the window, the failing slots, the raw digests and the reasons.

**Replacement.** A window with either verdict is replaced by one fresh window of the same kind under the unchanged protocol. The replacement takes the replaced window's place in the W1/W2/W3 sequence, faces that window's stops afresh, and keeps this revision's spacing of at least 6 h to its neighbours. At most one replacement window is permitted per epoch; any further window with either verdict stops the epoch and returns it to council. Replacement is admissible because the verdict is decided from instrument state alone, before any B value or disposition is read, so it cannot select on outcome. No other top-up is permitted.

**Disclosure.** Two observations bound a slot's endpoints only. `AppleRawCurrentCapacity` is updated by the gauge in steps, not continuously: on 2026-09-25 it held at 7516 mAh through about 4.5 min of 0.58–0.74 A charging (about 45 mAh), then stepped to 7591 mAh, its full-charge capacity, when charging ended. Its difference across a slot is recorded as a diagnostic and does not bound the net charge in between. A charging excursion that begins and ends between a slot's two observations is not detectable by this rule and is disclosed as a limitation. The 200 mA bound is a screen of thermal state for powermetrics-only windows; it is not an energy bound for a wall-meter window, and no wall-meter window is claim-bearing until WALL-METER-GAIN-01 registers a bound on the battery's net energy over the capture, from the wall side or by excluding the battery path by design.
```

### W1 arm

- W1 arm record: `docs/process_traces/2026-09-26-activation-22784e38/00-activation-record.md` (sha256 `fa4032bc38470ab0d02c5edfc0fbd8387d95b2a3f97787bf59239b6f7d8a981c`), items 2–3, 15–16.
- Arm evidence directory: `docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/`.
- Final desk output: `docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/step2.out` (sha256 `87164bc62c0e4acf94f3c44e7f2938b963442980080c9edb9bf19c89c2afc993`).
- Notice body: `docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/attempt-000001/notice-body.txt` (sha256 `6259ccad997682e22b1bb0adcb88fac88243513f877cb4d179c4b0701423befa`).
- Desk-input paste lines (verbatim from `step2.out`):

```text
stale identity fields vs /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json: os_build
IDENTITY_EPOCH_JSON=/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/identity-epoch.json sha256=b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607
T1_BINDINGS_JSON=/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/t1-bindings.json sha256=8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98
```

### W2 arm

- W2 arm record: `docs/process_traces/2026-09-27-activation-3ba66eeb/00-activation-record.md` (sha256 `8efdc046143f93f02f44b4b0e20b9ad2fdb440fade72f74299048fabd686d394`), items 24–27.
- Arm evidence directory: `docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/`.
- Final desk output: `docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/step2.out` (sha256 `0f3373c8c96e17cec16bd592c06a43c638980c773333cbf1f1ca72356533ee49`).
- Notice body: `docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/attempt-000001/notice-body.txt` (sha256 `ed96f17946981c6f35633fa2eb642a14e4c7e8184b7bfe5c7e13d709a8dbc78a`).
- Desk-input paste lines (verbatim from `step2.out`):

```text
stale identity fields vs /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json: os_build
IDENTITY_EPOCH_JSON=/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927/identity-epoch.json sha256=b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607
T1_BINDINGS_JSON=/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927/t1-bindings.json sha256=8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98
```

