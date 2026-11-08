# DRAFT AMENDMENT: permanent SSD configuration for ALIGN

2026-11-08, Sol seat 1. **DRAFT / NOT IN FORCE. Hardware evidence absent.**
This proposes a replacement for the adoption terms of
[DRAFT-AMENDMENT-external-log-volume.md](DRAFT-AMENDMENT-external-log-volume.md),
which remains historical, using Ed's 2026-11-07 permanent-drive and
meter-everywhere rulings. Supporting design, equations, costs and unknowns:
[SSD-PERMANENT-STUDY.md](SSD-PERMANENT-STUDY.md).

Adoption requires the lead/cold science disposition of these prospective
criteria, passing native qualification for the exact chosen mode, an
admitted R1-to-SSD bridge, qualified implementation/event coverage, and Ed's
confirmation of the final hardware's whole-series availability. Ed's wish
for permanence supplies direction; it does not assert a qualification PASS.
This document neither arms W1 nor changes any checked-in configuration.

## A1. Scope and DC boundary — replaces the old A1 carve-out

Every ALIGN measurement captures KM003C DC input between wall brick and
MagSafe and analyzes it alongside rails. Permanent attachment is allowed
only as the **qualified constant configuration** described here. There is
no blanket exception excluding DC/whole-machine windows from this policy.
Other studies do not inherit permission automatically; their own registered
boundary and resolution must qualify the same configuration.

V4 retains its GPU-rail primary residual and its secondary/print-only DC
analysis. V5's DC endpoint can be primary only after separate metrology,
baseline, battery, fitting, calibration and threshold registration. Raw DC
includes the drive/hub/host input contribution. Keep gross energy and
measured mode-minus-absent offsets visible; do not call DC input AC wall
energy or assume it equals total consumption during battery activity.

No primary GPU estimator, X1–X8 exclusion, U1–U6 rule, contrast threshold or
held-out cohort changes through this draft. R11's pending U3 bar remains
pending. The prospective configuration fault below is a new admission/
continuity rule requiring review and implementation, not an already
registered member exclusion or an assertion that old X4 covers everything.

## A2. Exact hardware and a single frozen operating mode

Permit exactly one enrolled physical storage device/enclosure with its
qualified APFS log volume. Bind serial/model/capacity/firmware where
observable, volume/container UUID, cable, port/topology, placement and hub
identity/port if used. UUID, mount name and a transient `diskN` alone are
insufficient. Unverifiable identity is a refusal, not a wildcard.

Freeze one of these modes for the whole v4 series:

1. **B:** attached and mounted; no external reads or writes from quiet-period
   start through window finalize. Indexing disabled, Time Machine excluded,
   ownership enabled and `.fseventsd/no_log` present; observed daemon/I/O
   behavior must also pass qualification.
2. **B-unmount:** attached and powered; the magistrate resolves the enrolled
   whole disk and runs `diskutil unmountDisk` before pre-arm, verifies all
   child volumes unmounted, and runs `diskutil mountDisk` after finalize.
   Unmount is not electrical off. Validate preparation between windows.
3. **B-cut:** attached through the exact qualified hub; flush/unmount before
   pre-arm, cut only the designated downstream port with qualified `uhubctl`
   control, independently verify true VBUS off/no backfeed, then settle.
   After finalize, power on, verify returning physical/volume identity,
   mount and validate. Hub/host power remains part of the configuration.

Rank B first if it meets the DC budget, then B-unmount, then B-cut. Each
accepted mode has zero normal Ed actions per window. Mount/power transitions
at these lifecycle points are part of the fixed mode, not mode changes.
**A/direct writes and A-lite/member-gap backups are not authorized.** Existing
Q2/Q3 mean-effect tests cannot authorize them.

## A3. All window storage remains internal; between-window state machine

Keep code, model/tokenizer loads, runs, both window copies, custody, thermal
sidecars, monitor/meter streams and TMPDIR on the internal disk. Offload and
compression/hash work on the measurement Mac happen only between finalized
windows, never alongside the next capture. Preserve the existing independent
second-copy requirement and internal free-space/sizing gates.

The magistrate's automated sequence is:

`finalize internally → verify enrolled identity → mount/power on as needed →`
`offload and verify required copies → flush/close writers → prepare frozen`
`mode → verify actual state → quiet dwell → pre-arm/arm → capture → finalize`.

Use `Q = max(30 min, 2 * measured last-access-to-stable-state time)`. Q follows
the last I/O **or** mount/power transition and includes host thermal/idle
recovery. No stable plateau means no qualification. Neither command exit 0
nor a fixed 600 s remount wait substitutes for verified state/recovery.
Avoid writes into an empty mount directory after a failed mount. A stuck
unmount, failed remount, offload verification error or unexpected identity
holds the next arm, preserving internal evidence. No routine force-unmount,
in-window repair or silent fallback to another mode.

R12 remains in force: windows end at terminal completion; short mechanical
triage gates the next arm from a committed record and recovered quiet state.
Desk work stays off the MBP, with desk gating after W1 and any code/config
change. The magistrate stays idle during capture. Offload + transitions + Q
must be measured against the 30–45 min turnaround target; a longer necessary
Q lengthens the cycle. Do not shorten member idle, scaffold or thermal gates
to recover that time. R12's 6–8 count-only calibration-window rule is unchanged.

## A4. Qualification required at both energy boundaries

Compare true physical absence with every candidate intended for adoption,
at idle and identical-work decode, during a one-time enrollment/qualification
session with Ed present Sunday 2026-11-08 if the machine is free. Retain the
corrected five physical blocks and block-mean drift analysis. Five blocks
give two residual df; three give zero. A single absent→present transition
cannot certify equivalence. Physical switches during qualification precede
the permanent freeze; normal windows require none.

Reuse the existing kit/extraction/custody as specified in study §4, extended
for mode-aware no-I/O blocks, KM003C and longer-span stability. Move stress
offloads before Q, not between deciding quiet spans. Preserve Q1's balance,
missing-block and time-basis guards, and Q5's missing-evidence failures.

- **GPU Q1:** decode presence-effect 90% interval inside ±0.25% of decode GPU
  power (about ±62.5 mW at 25 W).
- **Q5:** arm checks PASS; zero unexpected device losses or metadata-daemon
  segments above 0.05 CPU-s/s; existing idle battery-float criterion at
  200 mA; slow-temperature offset ≤0.5 °C; complete deciding evidence.
  Expected unmount/off is evaluated through mode-aware identity/state proof.
- **New QDC:** stable intended power state, zero external I/O, measured idle
  and decode offsets with uncertainty, and the following mean/variability
  bounds for the actual endpoint operator and every relevant duration.

Proposed `sigma_star = min(2 J, qualified endpoint replay SD)`. Before an
endpoint SD is qualified, 2 J is a planning target, not a DC precision claim.
Require a 90% interval for uncancelled mean error within
`±0.05*sigma_star` (**±0.10 J** at 2 J), and a one-sided 95% upper bound on
added SD ≤`0.30*sigma_star` (**0.60 J**). Require the same mean-error bound
for early/late drift. The offset itself need not be small; `c*T` must be
reported and treated by the frozen baseline/model, not assumed absorbed by
an intercept. Under independently additive noise the SD budget permits at
most 4.4% total SD inflation; without that assumption, bound total residual
SD inflation directly by 4.4% and rule out compensating covariance.

At 234.5 s the mean/SD energy budgets correspond to coherent power changes
of 0.426/2.559 mW; at 1,800 s, 0.056/0.333 mW. Use integrated errors with
serial and baseline covariance, not white-noise extrapolation from 1 Hz SD.
The historical 19–58 J regression residuals cannot justify a looser budget
when replay-referenced effects are about 2 J. This is a proposed SSD
tolerance, not U3 or a v5 detection threshold.

Freeze block-aware variance inference, coverage checks, mode/duration
multiplicity, extension/stopping rules and battery/meter uncertainty handling
before reading results. A mean interval is insufficient. Coverage gaps,
unknown battery contribution, uncertain clock alignment, nonlinear drift,
state steps or insufficient precision cannot PASS. The legacy evaluator's
`B` result does not establish QDC. The original 6.833 h schedule is a base
cost; 30-min settles make the proposed no-I/O schedule **8.5 h per candidate**
before longer decode, setup, long plateaus, bridge or precision extensions.
Use separate prespecified offset-reference and challenge records, or a
validated predictive treatment of offset uncertainty. No test-block/span
re-centering or fitted drift removal may manufacture a stability PASS.
Reproduce the actual production baseline; a diagnostic correction is not
authority to change it. The total time to resolve QDC remains unknown.

All required gates must PASS before this exception can be adopted. For v4,
QDC is a configuration-adoption gate while DC remains secondary; it does
not change historical rail eligibility. V5 must separately repeat/extend
qualification at its registered primary DC scope/resolution, including
battery accounting and meter uncertainty. No missing native evidence is
replaced by a synthetic test.

## A5. Drive-free R0/R1 and the pre-W1 bridge

Tonight's drive-free R0/R1 outputs are preserved under that identity. W1 is
not registered, so the final drive may join before W1 **only after** a
digest-bound R1-SSD bridge is admitted. This replaces the old amendment's
requirement to attach before R1 without declaring all R1 settings portable.

Recheck the final mode's 30-min soak, sensor classification/noise/bands,
thermal reference, power/fan/High Power policy, D/30B load and recovery,
clock/throughput, t_decline, N_chunk, G_turn and G1/H duty. Re-exercise the
three gated D planning runs and X-G with the relevant predecessor heat;
rederive D/contrast G0 caps, all budget/receipt proofs, I_D/B_D/T_dead,
tails, turn opportunity, W1 sizing/free space, U5/replay/reference transfer,
battery float/headroom and DC continuity. Study §5 identifies the owning
R11 rules; do not relax them. Token/stack/R0 semantics may transfer only
with verified identity and unchanged assumptions.

Retain a setting only when the final configuration meets its owning
criterion. Changed settings require replacement measured evidence and
prospective freeze before W1; rerun affected or full R1 when needed. Preserve
the original record and label the bridge/new settings separately. This
amendment grants no additional post-W1 tuning right and no U3/U5 waiver.

## A6. Arm refusal, per-window manifest and events

Replace external-volume refusal only for the single qualified identity in
the frozen mode. Retain refusals for other storage devices, network or disk-
image mounts, unreadable census, extra child mounts, missing qualification/
bridge receipts, insufficient internal space, wrong mode/state or identity.
The already qualified KM003C/logger does not consume the storage allowlist.
Integrate the same mode-aware checks at magistrate pre-arm, session prepare/
install and kit readiness. The existing mount-only census is insufficient.

Finish active identity/preparation probes, `mdutil`/`tmutil` checks and
flushes before Q. Arm consumes their bound receipts and passive current
state, rather than waking the drive to repeat those checks. Require event-
audit readiness and complete prior-window audit coverage before the next arm.

Before quiet dwell, B proves enrolled device + prepared mount; B-unmount
proves enrolled powered device + no child mounts; B-cut binds pre-cut
identity to the fixed hub port and proves the downstream supply off. After
finalize it must prove the same device returns. Qualify passive full-span
device/mount/power-event evidence and its coverage/overhead. No repeated
SMART/directory probes that wake the SSD during measurement. Nonenumeration
alone cannot distinguish a correct power cut from an accidental disconnect.

Store internally with each window: amendment/config/code/qualification/
bridge digests; enrolled identity and observed identity; port/cable/hub
topology; mode; every child mount state; port power (`on`, proven `off`,
`unknown`); transition receipts/times; last I/O/Q completion; start/end
censuses and event-audit coverage; meter identity, streams/hashes/coverage
and battery state. Do not equate a mount UUID with physical continuity.

Unexpected disconnect, drive failure, remount, I/O, port power change,
identity mismatch or missing event coverage records an
**`ssd.configuration_break` (proposed name)** and safely stops further
collection at the existing lifecycle boundary without altering captured
bytes. Preserve the window and original rail/DC outputs; configuration
continuity is unavailable from last proven-good time, or for the whole
window if timing is unknown. Do not silently map the new fault into an
existing exclusion. Lead adjudication/registered consequence is required
before data are pooled or the next arm is released.

## A7. Series commitment, faults and disclosure

The exact device/enclosure/firmware/port/cable/hub/placement/mode remains for
the entire registered v4 series, including authorized extensions and tests.
Borrowed-drive return, replacement by an identical model, unplanned removal,
failure or a mode change is a configuration break. No post-break pooling
with old calibration, no model-window spanning the break, and no automatic
rollback to absent mode. Hold new arms; requalify and obtain a prospective
new segment/series ruling, redoing affected thermal/budget/DC gates and
reference/calibration evidence. Separate U4 prints alone do not restore
comparability. `status: off` is a between-series safety reset, not permission
to continue an attached series drive-free.

Report the hardware/mode, transition/arm verdicts, Q1/Q5/QDC results and
uncertainty, GPU/PSTR/PDTR/KM003C offsets, gross and baseline-treated DC,
battery availability and all faults. Label the unassigned PSTR residual as
potentially including storage/host bus power with undocumented SMC accounting.
The claim is about this complete serving configuration; do not compare an
absent series and an attached series as if their DC hardware were identical.

## A8. Implementation and adoption remain owed

No runtime code, config, hazard catalog or registered protocol is changed
here. Extend the external-volume module/CLI, SSD qualification runner and
evaluator, magistrate hooks, v4 kit/session and manifest/audit paths. Native
qualification must include failed unmount/remount, unexpected wake/drop,
wrong identity/extra volume, hub command success without real VBUS cut,
restart recovery and missing audit/meter coverage, with internal evidence
preserved and next arm held. Keep current defaults off until adoption.

The lead reviews both independent seats, dispositions the proposed numeric
budget and fault consequences through the owning science/registration gates,
and arranges clean-machine hardware work after active jobs/agents exit.
If buying, select the final **4 TB**, fanless, predictable-power drive/
enclosure combination before qualification; study §7 states requirements,
not product claims. No drive/hub, DC precision, APST/ASPM or R1 transfer has
been qualified by this document.
