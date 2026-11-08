# Permanent external SSD for ALIGN v4 and v5 — feasibility study

2026-11-08. Sol seat 1, branch `align/2026-11-08-ssd-permanent-sol1`.
**DRAFT / PROVISIONAL. No hardware qualification or amendment adoption.**
This is a prospective replacement proposal for the operating recommendation in
[the earlier study](SSD-ALWAYS-ATTACHED-STUDY.md), which remains historical.
The proposed rule is [DRAFT-AMENDMENT-permanent-ssd.md](DRAFT-AMENDMENT-permanent-ssd.md).

Ed's task ruling of 2026-11-07, about 23:10 PST, makes permanent attachment
the target, including buying a drive rather than returning the borrowed one.
The current device is a WD SN7100 2 TB in an OWC Express 1M2 USB4 enclosure.
The other binding change is meter capture **and DC-in analysis in every
measurement**: KM003C between the wall brick and MagSafe cable. V4's
registered residual stays GPU-rail energy; DC-in is secondary/print-only.
A separately qualified, registered DC endpoint is primary in v5. Therefore
the old amendment A1's DC/whole-machine exception cannot survive: it would
ban the drive from every window. Permanent attachment needs qualification
at both boundaries, rather than an assertion that the GPU cannot see it.

The brief says tonight's R0/R1 are drive-free, W1 is unregistered, and Ed is
present for first connection on Sunday 2026-11-08. Those are supplied planning
facts, not observations made in this clone. No data paths were followed.
Authority also read from the local `origin/main` Git object: RUN_STATE
210/212 (meter and v4/v5 split), 213 (dedicated MBP) and 214/R12 (v4-lean).
No remote freshness is asserted.

## 1. Recommendation and decision order

Prefer **B**, mounted with no external I/O, if it passes both the existing
GPU/operational tests and the new DC stability tests below. If B fails,
test **B-unmount**; if that fails, test **B-cut**. B-cut offers the strongest
electrical isolation but needs different, verified switching hardware.
**A**, including backups between members of a window, is rejected for this
proposal. A window includes idle baselines, warmup, gates, holds, references,
member gaps and teardown, through finalize. Unowned time still contributes
to whole-member DC energy.

All accepted modes require **zero Ed actions per normal window**. Only the
magistrate changes mount/power state, between finalized windows. No mode may
silently replace another after registration. If none passes, hold permanent
adoption and improve the hardware/protocol; recurring manual unplugging is
not the recommended automated-loop solution. Today's arm rule remains until
an amendment is adopted and its implementation qualified.

R12 cadence remains: close at terminal completion, commit the record, perform
short mechanical triage, recover the quiet start state and arm again. Desk/
analysis/review runs off the MBP; desk gating remains after W1 and after a
code/config change. The on-MBP magistrate is idle during capture. SSD
offload and mode preparation fit only between windows. The 30–45 min
turnaround target is conditional: measure offload + transitions + Q + arm
time. Thermal cooldown can overlap Q after the last access, but Q cannot
overlap offload. If the measured Q exceeds 30 min, disclose the longer
cycle rather than shortening it to meet a calendar target. R12's unchanged
300 s member idle/scaffold/gates and 6–8 count-only calibration-window rule
are unaffected by this proposal.

## 2. A constant configuration can consume watts, but cannot wander by joules

The bus-powered drive's planning range is **1–8 W**, inherited from the old
study's anecdotal enclosure reports, not a measurement or purchase guarantee.
At 234.5 s that is 234.5–1,876 J; at 1,800 s it is 1.8–14.4 kJ. This input
ultimately comes from the adapter/battery path. KM003C sees the adapter's DC
delivery, including the bus load when supplied there; charging or battery
assistance can redistribute it in time. It is not AC wall energy, and is not
automatically total machine consumption without battery accounting.

A large, repeatable offset is admissible as part of the declared serving
configuration. Its gross joules remain reported. It is **not** evidence of
hidden model work. Let `c_mode` be the measured candidate-minus-absent mean
DC power, reported separately at idle and identical-work decode, with its
interval and battery state. For a span of length `T`, a constant adds
`c_mode*T`. An energy-fit intercept alone does not remove this when durations
vary. Baseline subtraction removes it only when baseline and measured span
share the same state and the registered subtraction actually covers `T`.
Do not add a duration regressor, subtract a guessed 5 W, or change v4's GPU
model to make a drive pass. The current diagnostic DC fit uses per-member
idle subtraction; v5 must freeze its own scope and baseline before fitting.

The dangerous part is `e(T) = integral(delta_P(t) - c_mode) dt`, including
settling, sleep/wake transitions, drift and host work. No external reads or
writes are permitted in the qualified state. An unmounted NVMe can still
consume power and change state. APST/ASPM behavior through this bridge is
unknown. A marker or a quiet average is not proof of a stable state.

### Proposed DC stability budget, requiring prospective lead/cold adoption

Use the tighter **about 2 J same-position/replay-referenced SD** as the
planning resolution, not the historical **19–58 J regression residual SDs**.
These are historical rail/design scales, not measured KM003C precision or a
v5 noise estimate. The replay pair-difference SD of 2.97 J is a different
quantity. R11 leaves the U3 numerical energy bar PENDING; this proposal
neither installs a U3 constant nor substitutes for v5 metrology.

Define `sigma_star = min(2 J, qualified endpoint replay SD)` once an endpoint
has such an estimate. Until then, the 2 J calculation is a design target,
not evidence that DC can resolve it. Proposed QDC requires, separately at
idle and decode and for every registered span length:

- A 90% equivalence interval for **uncancelled mean error** inside
  `±0.05*sigma_star`: initially **±0.10 J**. This is error after the frozen
  offset/baseline treatment, not a ±0.10 J limit on gross drive energy.
- A one-sided 95% upper confidence bound on added SD at most
  `0.30*sigma_star`: initially **0.60 J**. A t interval on a mean is not this
  bound. Under an independently additive noise model this means at most
  9% added variance, or `sqrt(1.09)-1 = 4.4%` total SD inflation. Independence
  must be checked; otherwise bound total residual SD inflation directly at
  4.4%, with block-aware uncertainty, and show no compensating covariance.
- No unmodeled state steps, monotone within-window drift, or relation of
  residual error to condition, work duration, preceding offload or time
  since access. Bound early/late mean changes by the same 0.10 J budget.
  Missing coverage or insufficient precision is INCONCLUSIVE, never PASS.

These are proposed engineering tolerances, not previously registered facts.
Relative to 19–58 J, 0.60 J would be only 3.2–1.0% added SD, but using
`0.30*19 = 5.7 J` would already exceed the approximately 2 J replay scale.
That larger budget is unsuitable for the monitor+energy squeeze.

| Span T | Allowed coherent mean error / T | Allowed added energy SD / T |
|---|---:|---:|
| 120 s screening segment | 0.833 mW | 5.000 mW |
| 234.5 s historical 30B planning episode | 0.426 mW | 2.559 mW |
| 1,200 s illustrative member | 0.083 mW | 0.500 mW |
| 1,800 s member cap | 0.056 mW | 0.333 mW |

These divisions describe coherent span-average changes, not independent
sample noise limits. Use the actual baseline/episode/member integration
operator, including baseline-estimation uncertainty and serial covariance;
do not divide a 1 Hz power SD by the square root of sample count. A 5 W
state excursion lasting one second contributes 5 J, already too large.
Short guarded segments alone cannot certify long-member stability.

For **v4**, require QDC for the proposed permanent-configuration exception
while retaining DC's secondary label; a DC failure does not retrospectively
change a member's GPU eligibility. Show both raw DC and baseline-treated
diagnostics and mark unavailable DC explicitly. For **v5**, requalify at the
frozen primary endpoint's resolution, baseline, duration range, battery
policy and meter uncertainty; if those are tighter, tighten this budget.
Passing the SSD test is necessary, not sufficient, for a primary DC claim.

## 3. Ranked modes: what each channel sees and what can fail

Apple's GPU model and SMC PSTR/PDTR have no established exclusive component
boundary here. Measure their responses separately. `PSTR - CPU - GPU - ANE`
is an unassigned diagnostic residual, not an SSD or DRAM power meter.

| Rank / mode | GPU rail | PSTR / PDTR | KM003C DC-in | Magistrate hooks / Ed per window |
|---|---|---|---|---|
| 1 — **B**, attached, mounted, no I/O | No direct GPU workload intended; host controller, fabric, daemon and thermal effects still need Q1 | May show persistent bus/host offset and state steps; quantify both keys, no assumed watt-for-watt accounting | Full delivered bus/host offset and variability, with battery caveat | Validate device/mount and preparation, finish offload, freeze access, settle, arm; resume I/O only after finalize. **0** |
| 2 — **B-unmount**, attached, all its volumes unmounted | Same indirect paths; unmounting does not disable the controller | Bridge/NVMe can remain powered; sleeping draw and transitions unknown | Nonzero attached-but-unmounted offset until measured otherwise | Resolve allowlisted whole disk, `diskutil unmountDisk <resolved-disk>` before pre-arm; verify no child mounts; settle; `diskutil mountDisk <resolved-disk>` only after finalize. **0** |
| 3 — **B-cut**, cable stays attached, downstream VBUS off | Host/hub baseline remains; cutting downstream power may alter host link state | Hub/host load remains even with SSD off; do not assume equal to no hub | No SSD bus draw only after true cut/no backfeed is proven; hub and host still count | Flush, unmount, command the exact qualified hub port off using `uhubctl`; verify cut, settle, arm; after finalize power on, enumerate identity, mount, validate, offload. **0** |
| 4 — **A**, external writes during windows | Write/daemon/thermal effects may depend on arm and work length | Write/wake bursts, APFS/GC and host work | Direct additional, potentially condition-correlated energy; member-gap backups count too | Could route writes, but **not authorized**; Q2/Q3 bound means only and do not license variability |

B risks Spotlight (`mds`, `mdworker`), `fseventsd`, Time Machine (`backupd`),
APFS housekeeping, SMART/health polling, trim/garbage collection and unexpected
reads. Disable indexing, exclude Time Machine, retain the fsevents marker,
and observe behavior; configuration flags do not prove silence. Keep models,
tokenizers, code, logs, both window copies, custody and TMPDIR internal.

B-unmount reduces filesystem wakeups but can fail because a process holds
the disk open, a child APFS volume remains mounted, or Disk Arbitration
remounts it. A remount failure after finalize preserves the internal evidence
and holds the next arm; do not fall through to writing into an empty mount
directory. Never force-unmount an active writer as a normal remedy.

B-cut requires **true per-port VBUS switching**, not logical USB disable.
The supplied task says `uhubctl` can work on macOS with the few hubs that
really cut VBUS; this has not been independently verified offline. Such hubs
are generally USB 3.x rather than USB4; that is acceptable for offload.
Qualify the hub, port, permissions, command, restart behavior, absence of
backfeed and actual electrical off state with independent port-voltage/power
evidence. A successful command, extinguished LED or absent mount is not
enough. Bind upstream/downstream hub topology; some ports share a switch.
The meter/logger, MagSafe supply and other measurement devices must not lose
power or data when the SSD port switches. Do not introduce hub PD charging
or another supply into the Mac around KM003C.

For B-cut, electrically absent enumeration during a window is expected; the
same enrolled drive must return after finalize. Unexpected power-on, a hub
reset, another device on that port, or inability to prove the intended off
state is a fault. B and B-unmount still risk cable drops, thermal throttling
and unknown tunnelled NVMe power-state behavior. No mode gets an assumed
APST/ASPM setting from the SSD's bare-drive specification.

## 4. Qualification: extend the existing kit, do not reinterpret its PASS

Read [the corrected executing reviews](../reviews/2026-11-06-ssd-qualification-executing-reviews.md)
and [the original statistical/boundary review](../reviews/sol-burn-ssd-review.md).
Reuse `ssd_qualification.py`, its fixed-work decoder, journals, rail
extraction and physical-block inference. Their current CLI knows only
attached/detached and quiet/write, not B-unmount, B-cut or QDC. Its result
`B` presently means Q1+Q5, **not** permanent-SSD/DC authorization. The old
mounted-volume waiter and `RouteGuard` cannot observe the new modes safely.
This docs-only change implements none of the required extensions.

### Sunday design and the one-time absent reference

Nothing is captured while an agent or the current blinded analysis job is
running. The lead schedules a separate clean measurement session after that
job ends; Sunday is a proposed opportunity, not permission to interrupt it.
Ed is needed once for device enrollment and physical absence comparisons,
not for production-window transitions.

1. Before first connection, capture the physically absent idle and fixed-work
   decode reference with KM003C already in its permanent logging topology.
   Record adapter, battery, cable/port, fan/power policy and ambient/thermal
   state. If a hub is proposed, measure both no-drive/no-hub and no-drive/
   final-hub baselines; the latter isolates the downstream drive effect.
   The former exposes the total configuration change relative to tonight.
2. Enroll the exact drive, enclosure, firmware, cable, port and volume; verify
   preparation and ordinary offload/remount behavior. Do not format a borrowed
   drive without Ed's separate data/erase authority. Keep all captures internal.
3. Compare physically absent against **each candidate that could be adopted**
   at idle and identical-work decode, using five alternating physical blocks,
   `candidate / absent / candidate / absent / candidate`. The existing kit
   calls these `attached / detached / attached / detached / attached`;
   "attached" here does not mean write-mode A. Ed's repeated disconnects and
   reconnects belong to this one-time qualification session, before series
   freeze. Finish with the chosen device attached permanently.
4. If Ed can provide only one insertion and no repeated physical absence,
   the comparison is a useful offset description but cannot establish the
   existing Q1 equivalence interval: time and presence are confounded.
   Return INCONCLUSIVE. Repeated segments within that one block do not fix
   it. Automated B-cut repetitions can test electrical-off versus on with a
   fixed hub, but are not silently relabelled physical absence.
5. Compare the modes head-to-head as well, using blocked, counterbalanced
   order and the final topology. A different hub/cable requires its own
   absent and total-configuration comparison. A not-yet-owned B-cut hub
   remains an untested fallback; do not claim all modes qualified Sunday.

For each candidate retain six idle pairs and six fixed-work decode pairs
per physical block, 120 s nominal segments and 60 s gaps. In the extended
**no-I/O** schedule, replace legacy write slots by quiet repeats; retain
their positions and block labels. Move write-pattern/2 × 1.11 GB teardown
stress **before** each candidate's quiet settling period, never between its
deciding spans. This tests worst preceding offload without making B behave
like A. Q2/Q3 are not evaluated from repurposed slots. Separately running
the original write challenge is diagnostic only and adds time.

Use `Q = max(30 min, 2 * measured last-access-to-stable-state time)` before
deciding spans. It includes mount/unmount or power switching and recovery
of host thermal/idle state, not merely drive sleep. If no stable plateau is
observed, the mode has no valid Q and cannot pass. Challenge repeated short
turnarounds after a realistic maximum offload, varying earlier dwell lengths
to expose autonomous wake timers. Extend quiet plateaus through the longest
planned member, baseline and early/late window positions. A separate
window-length soak is necessary if shorter tests cannot bound slow changes.

### Capture and analysis

- One continuous powermetrics capture at the existing 10 Hz setting, SMC
  PSTR/PDTR/B0AC/B0AV plus R1 thermal keys at 1 Hz, metadata-daemon CPU,
  clock/thermal state, mount/device/power-state events and internal journals.
- The **existing KM003C reader/parser/supervision and custody hashes**, with
  continuous coverage before the first baseline through the last span.
  Use the authenticated clock mapping; integrate identical spans in every
  condition. Never splice a restart gap. Meter absence, sample gaps, unknown
  battery contribution or unresolved alignment prevents a deciding QDC PASS.
  Preserve v4's separate rail/DC availability semantics.
- Fixed prompt/token work loaded from the internal disk. Use the kit's 30B
  fixed decode for continuity, then D's registered development/replay work
  and the budget/thermal bridge in §5. Do not spend held-out seeds or fit a
  residual from variable work to conceal a drive transition.
- Estimate idle/decode mean offsets in each channel. Inspect within-span
  fluctuations, integrated errors for the duration grid, early/late drift,
  preceding-offload dependence and between-block state variation. Report
  gross DC, baseline-treated DC, and the battery observations separately.

Q1 uses **physical-block means**, intercept + linear time drift + presence,
with `df = blocks - 3`: five blocks give two residual df. Retain missing-
block accounting, the half-of-fullest retained-count guard, common time
basis, and fail-closed thermal evidence. Inspect nonlinear drift; an invalid
linear-drift model is not repaired by counting more 1 Hz samples. For a
combined four-state design (absent/B/B-unmount/B-cut), there are five fitted
coefficients including drift, so even five blocks would leave zero df.
Freeze a sufficiently replicated, full-rank design before collecting it.

| Gate | Required result for any chosen permanent mode |
|---|---|
| Existing **Q1**, GPU presence during decode | 90% interval entirely within ±0.25% of decode GPU power, about ±62.5 mW at 25 W. Point outside is FAIL; overlap is INCONCLUSIVE |
| Existing **Q5**, operational | Arm start/end PASS; zero unexpected device losses; zero attached metadata-daemon intervals above 0.05 CPU-s/s; zero idle battery-float violations at the existing 200 mA rule; absolute slow-temperature presence offset ≤0.5 °C; missing evidence fails. Intended unmount/off is verified by mode-aware evidence, not counted as loss |
| New **QDC**, §2 | Offset measured, intended power state stable, no external I/O, mean-error equivalence and one-sided variability bound both PASS at every relevant duration/load; no missing deciding evidence |
| Automation/bridge | Full no-human finalize → offload → state transition → quiet pre-arm cycle, complete event coverage, identity return and §5 checks PASS |

Q5 alone misses brief battery excursions if only segment means are used;
retain per-second battery/current and existing hazards for QDC. Show PDTR
and KM003C agreement/disagreement rather than treating SMC as the calibrated
reference. Freeze battery availability/correction and meter uncertainty in
the deciding analysis before viewing outcomes.

For QDC, predeclare a block-aware variance/SD procedure and its coverage
checks, not just a mean t test. Compare residual variance with absent controls
and bound the increase; if additive independence is not defensible, use the
total-SD/covariance condition in §2. Keep block-level shocks and serial
dependence, offset-estimation uncertainty and baseline covariance. Few blocks
may be unable to bound a 0.60 J increment on top of host/meter noise. The
existing kit supplies no such inference. Prespecify extension block counts,
stopping and simultaneous handling of modes/durations before reading the
qualification results; do not shop modes or loosen margins after a failure.
Estimate the diagnostic offset on prespecified reference records and judge
uncancelled error on separate challenge blocks, or use a prospectively
validated predictive procedure that accounts for estimating that offset.
Do not re-center each test block/span to zero or fit away its drift. The
production endpoint's own baseline operation must be reproduced exactly;
a diagnostic offset correction cannot silently become a production one.

### Measurement-MBP time bill

The latency synthesis, `docs/perf/2026-11-08-latency-synthesis.md` at Git
object `55029b860`, records **24,600 s = 6.833 h**, 125 segments for the
original five-block kit. The file may need `git show` on this clone. Three
blocks lose residual df; 30 s gaps are not an adopted speedup.

| Scope | Nominal MBP capture time, before transfer/native retries |
|---|---:|
| Original five-block kit, one candidate, 600 s settles | 6.833 h |
| Revised no-I/O five-block schedule, Q=1,800 s instead of 600 s | **8.500 h per candidate** |
| B and B-unmount, independently qualified against absence | **17.000 h** |
| B, B-unmount and B-cut, independently qualified | **25.500 h** |
| Initial absent reference/enrollment and automation exercises | Reserve **1–2 h**, planning allowance |
| R1-to-final-configuration bridge (§5) | Reserve **4–8 h**, planning allowance; full R1 rerun can cost more |

Thus reserve **13.5–18.5 h** for one candidate's base schedule plus setup/bridge,
or **30.5–35.5 h** for three, before any additional long plateaus or stronger
DC precision requirements. These are not upper bounds or promised Sunday
completion. Testing all three can extend beyond Sunday; schedule Ed's
physical transitions explicitly before freeze or leave later modes pending.
For one candidate the nominal schedule is
`5 * [1,800 + 24*(120+60)] = 30,600 s`; measured fixed-decode duration `d`
adds `60*(d-120)` seconds, and Q>1,800 adds `5*(Q-1,800)`. Decode/model-load
overhead, offload stress, physical handling and extended plateaus are extra.
Two healthy automated turnarounds cost at least two Q intervals (one hour
at the minimum); budget them within setup only if they actually fit.
No approximately 6.8 h plan alone proves long-window DC stability.
The total needed for a statistically decisive QDC result is not yet known;
reference/challenge replication and meter/host noise can increase this bill.

## 5. Boundary after drive-free R1, before unregistered W1

**The drive can join prospectively before W1; tonight's R1 bytes remain valid
evidence for the drive-free configuration. Its configuration-sensitive
outputs do not automatically become valid settings for the attached series.**
Record an R1-SSD bridge addendum binding the original R0/R1 digests, final
device/mode/topology, measured checks and resulting settings. No retroactive
R1 rewrite. No W1 registration/arm until that bridge is admitted. The old
requirement to attach before R1 is superseded only by an adopted amendment
with this bridge, not by this study's existence.

- Recheck internal-only model/stack/cache identity and a benign development
  decode/replay, token identity, active clock and throughput. Hardware changes
  do not by themselves erase R0's semantic evidence; new contention, timing,
  power or memory behavior can invalidate its transfer assumptions.
- Repeat the 30-min idle soak in the final mode and relevant D/30B load and
  recovery steps, retaining the model-free full-inventory thermal classifier.
  Verify sensor picks, noise/bands, soak references, thermal pressure, fan
  policy, power mode and the adopted High Power/cooler decision. Recheck
  t_decline, decode rate, N_chunk, G1/H recovery and G_turn. A sensor/policy
  change needing full R1 evidence requires that rerun before freeze.
- Re-exercise all three gated D planning runs and native X-G needed for the
  budget proof, with the relevant predecessor heat. Recompute G0 waits/caps,
  treating censored/unobserved waits under the existing rules; contrast caps
  retain R11's separate proof on every path. Check duty/turn opportunity,
  I_D, load/tail costs, B_D, T_dead and the 1(f)/L1 fit, W1 span/window ceiling
  and disk law from final-mode measurements. Q1/Q5 PASS alone proves none of
  these. Any signed R10 exception must be re-derived, not copied blindly.
- Recheck U5/replay/thermal transfer, U4 reference construction, battery float,
  charging/assist and adapter headroom, meter coverage/clock/uncertainty,
  quiet-start recovery and automated offload dwell. A new 1–8 W supply load
  can change charging or thermal behavior even when GPU Q1 passes.
- If unchanged settings meet every owning criterion, retain them with a
  digest-bound bridge receipt. If not, obtain replacement measurements and
  freeze corrected settings **before W1**, rerunning the affected R1 gates
  or full R1 when transfer cannot be established. The 4–8 h allowance is not
  a waiver of this work. It grants no new W1/D1 tuning permission, U3 energy
  constant, U5 waiver or change to held-out cohorts.

After freeze, exact drive, enclosure, firmware, cable/port, hub if any,
placement and mode stay fixed through the entire registered v4 series
(including any authorized extension/test windows). Planned B-unmount or
B-cut transitions at the registered lifecycle points are part of that fixed
mode; an unplanned removal, replacement, return, failure or mode switch is
an **SSD configuration break**. Preserve the affected window and cease new
arms; mark its configuration continuity unavailable from last proven-good
state (whole window if timing/coverage is unknown). The series cannot pool
post-break calibration/test data under the old configuration. Requalify and
obtain a prospective new segment/series ruling; repeat affected thermal,
budget and DC gates and rebuild reference/calibration evidence. Printing U4
on both sides alone does not repair the break. No silent rollback to absent.

## 6. Arm and kit changes required after adoption

Replace the blanket external-volume refusal with an allowlist of **one
physical device/enclosure**, one explicitly bound APFS log-volume UUID,
and the qualified mode. UUID/name
alone is insufficient: bind available drive/enclosure serial, model,
capacity, firmware, container/volume UUID, cable and stable port topology.
`diskN` is resolved afresh, not an identity. If reliable physical identity
cannot be established, qualification remains pending.

The magistrate must finalize internally, verify offload by UUID plus device
identity, complete both required copies, then prepare B/B-unmount/B-cut and
observe Q. Resolve/verify identity again before each destructive state
transition; no erase or format is part of these hooks. A transition error
holds pre-arm with an internal fault record. No in-window remount, health
probe, directory stat that wakes the disk, or power toggle is a repair.

Extend `external_volume.py` and `align_ssd_qualification.py` mode semantics;
wire the magistrate, session prepare/install and v4 kit readiness to the
same receipt. Retain default `off` and all unrelated pending registration
gates until adoption. The current mount-only census misses unmounted disks
and cannot distinguish B-cut from a cable loss; require mode-aware physical
census plus a qualified full-span event audit. Its overhead must itself be
included in qualification, using passive observation during windows.

Every per-window internal manifest must bind amendment/config/qualification/
bridge/code digests; exact device identity and topology; chosen mode; actual
mount state of every child volume; port power state (`on`, proven `off`, or
`unknown`); transition timestamps/results; last I/O and Q completion; arm
and finalize censuses; meter/logger identity, stream hashes/coverage and
battery observations; event-audit coverage and every deviation. B-cut links
the pre-cut identity receipt to the fixed port and post-power-on return
receipt; expected nonenumeration alone cannot attest cable continuity.

Refuse extra external storage devices/mounts, network/disk-image mounts, unreadable
census, wrong state or identity, missing qualification, insufficient internal
free space, missing audit readiness, or an incomplete prior-window event audit.
Complete active preparation/identity probes, `mdutil`/`tmutil` checks and
flushes before Q; arm uses bound preparation receipts plus passive current
state evidence so its checks cannot wake a qualified sleeping drive.
For B-unmount/off, test the volume's
preparation while mounted between windows; do not wake/mount it to check
Spotlight during pre-arm. Check actual state, not just command exit status.
Do not newly enumerate/probe measurement hardware during a live window.
The already qualified KM003C/logger is not a storage-device exception and
does not consume the SSD allowlist entry.

## 7. Purchase requirements and remaining unknowns

Buy before final qualification if the borrowed 2 TB drive cannot remain.
Returning it after W1 is a configuration break, regardless of buying an
identical model. Require **4 TB usable-class capacity**: v5 raw data is
about 1–1.2 TB per copy, two copies about 2–2.4 TB before pilots, models,
manifests, filesystem reserve and growth. Confirm the real retention bill;
4 TB is a minimum planning specification, not unlimited capacity. Two copies
on one SSD are one failure domain; preserve the required independently
verified second-copy policy. Keep peak per-window space internal (current
kit's ≥80 decimal GB arm floor plus actual sizing/other obligations).

Require a fanless enclosure with passive cooling away from MBP intake and
exhaust, stable macOS mounting, clear device/firmware identity, no forced
background software, predictable sleep/wake and low, **repeatable** idle
power. Require sustained offload throughput, retention/endurance and
reliability sufficient for the full series, and an explicit macOS/bridge
power-state compatibility test/return opportunity. A low bare-NVMe sleep
specification does not specify enclosure+host draw. Fix cable length/port,
placement (at least the old study's 30 cm separation), firmware and thermal
arrangement at enrollment. Prefer no fan, RGB/controller polling or vendor
daemon that wakes periodically.

If B-cut is needed, buy a hub whose **individual downstream port actually
cuts VBUS on macOS**, with independent switching, no backfeed/PD bypass,
stable addressability and adequate downstream SSD startup power. USB 3.x
offload speeds are acceptable; USB4 is not a requirement. Qualify the entire
drive/enclosure/hub/cable combination. No product recommendation or current
compatibility claim is made without network access or hardware evidence.

Unknown until measured: actual idle/decode offsets; plateau/wake/GC timing;
unmount's power benefit; tunnelled APST/ASPM; host/GPU/SMC coupling; meter and
battery precision at the proposed sub-joule budget; long-span serial drift;
true hub cut behavior; remount reliability; offload/settle time; R1-setting
transfer; and whether a 4 TB replacement has the same power behavior as the
borrowed 2 TB unit. Permanence is the operational objective, not a measured
scientific qualification. Lead/cold review must adopt the proposed budget
and inference, implement the hooks, then run the native gates in a clean
session. All native USB, KM003C, SMC, powermetrics and MLX/decode checks remain
unperformed here; tiny/synthetic software tests cannot establish these facts.
