# Permanent external SSD for ALIGN v4 and v5: feasibility study

2026-11-08 brief; independent Sol seat 2. **DRAFT / PROVISIONAL. No hardware qualification or adoption is claimed.**
Companion: [draft amendment](DRAFT-AMENDMENT-permanent-ssd.md). The earlier
[study](SSD-ALWAYS-ATTACHED-STUDY.md) and [amendment](DRAFT-AMENDMENT-external-log-volume.md)
are retained as historical proposals; neither licenses permanent operation.

## 1. Decision and authority

Ed's 2026-11-07 permanent-drive ruling removes routine human plug/eject from
the intended research loop. Recommend **B first, B-unmount second, B-cut third;
reject A**. Qualify and freeze one mode before W1. Once adopted, the exact SSD,
enclosure, cable, port/topology and mode stay for the entire v4 series. A later
v5 series needs its own DC endpoint qualification, even with the same storage.
Failure to qualify is a hold on adoption, not a plan for Ed to unplug every window.

The initial candidate is the borrowed WD Black SN7100 2 TB in an OWC Express
1M2 USB4 enclosure. If it cannot remain through the series, purchase the final
drive **before** qualification/W1; replacing a qualified borrowed drive is a
configuration change. First connection is planned for **Sunday 2026-11-08**, with
Ed present. R0/R1 tonight are drive-absent; W1 is not registered (brief facts,
not independently observed machine state).

Binding source order:

- Ed's task brief supplies permanence and meter-everywhere. RUN_STATE items
  210 and 212 R11-3 retain v4's GPU-rail residual and require actual meter
  samples, clock coverage, custody and battery-flow checks. v4 DC is secondary,
  print-only; a qualified DC endpoint is primary in v5.
- RUN_STATE 213 and 214 R12 require back-to-back windows, terminal completion
  rather than reservation to the ceiling, short mechanical triage, and desk
  work off the MBP. The 300 s member idle and G0/G1/hold policies stay. Offload
  cannot overlap a measuring window on the MBP.
- The [SSD executing reviews](../reviews/2026-11-06-ssd-qualification-executing-reviews.md)
  and [burn review](../reviews/sol-burn-ssd-review.md) govern reuse of the kit:
  physical-block inference, missing-evidence refusal, and no variance claim
  from Q3's mean-effect interval. See [protocol v4](../pilot_protocol_v4.md),
  [R1 contract](../r1_runtime_contract.md) and [KM003C integration](../squeeze/KM003C-ALIGN.md).
- Source snapshots read from local Git: `origin/main` at `3809bdd14` (items
  210–214); latency synthesis at `55029b860`,
  `docs/perf/2026-11-08-latency-synthesis.md`; final design at `6eb1ff5be`,
  `docs/align/council-2026-11-05/FINAL-DESIGN.md`. D-018 requires named channel
  boundaries; D-043 requires supersession closure when a proposal is adopted.
  No remote freshness or sealed measurement result is asserted.

## 2. What an admissible constant means in DC

The path is **wall brick → KM003C → MagSafe cable → MBP → bus-powered SSD**.
The meter measures DC supplied through MagSafe, including the drive's load;
brick AC losses are outside the boundary. Battery charging/assist buffers that
input, so DC input is not automatically instantaneous total machine power.
No second power supply may bypass the meter without a new boundary definition.

The old amendment A1's absolute DC/whole-machine exception is incompatible with
this path. Replace it with a **qualified configuration constant**, not a claim
that the drive is invisible. The earlier 1–8 W range is an unverified planning
range for enclosure plus drive, not a measurement here. NVMe bare-drive sleep
specifications do not establish USB4 enclosure sleep draw.

For load stratum L, define the matched candidate-minus-absent DC power offset
`p_L` from qualification blocks. Record idle and decode offsets separately and
test their difference; a load-dependent offset cannot be called one constant
without an explicitly qualified model. Let `T` be the actual registered energy
span, and define the unexplained configuration contribution as

`r(T) = integral(configuration power increment over T) - p_L * T`.

This is an experimental contrast inferred with matched controls, uncertainty,
clock/battery checks and block drift terms, not an assertion that KM003C alone
isolates SSD watts. Include host-controller and thermal consequences. Offset
estimation error, drift and power-state transitions belong in the bound on r.

**Constant watts are not constant joules.** Even a perfectly steady 5 W adds
1,172.5 J over 234.5 s, 9,000 J over 1,800 s, and 1,500 J for a 300 s duration
difference. A regression intercept does not remove `p*T` when T varies. Gross
v5 energy legitimately includes this duration cost for the machine as configured.
Report raw gross DC energy. Do not subtract a fitted SSD offset after seeing
outcomes, transfer GPU coefficients to DC, or label a storage-equipped result
as bare-MBP energy. If v5 registers a trusted fixed baseline/duration term,
qualify it and freeze it before calibration/test; retain raw gross alongside it.
The current v4 per-member idle subtraction is only diagnostic and cancels the
offset only under demonstrated stationarity and adequate baseline precision.

### Proposed DC stability budget (QDC, not an installed threshold)

Use the supplied **~2 J replay-referenced residual SD** as the conservative
design reference, not the 19–58 J regression residuals of the older GPU study.
Neither figure establishes the MBP's DC residual SD; that must be measured.
Propose, for each load and registered integration length:

- Absolute systematic unexplained energy: **≤ 0.05 × 2 J = 0.10 J**;
  require the entire block-aware 90% equivalence interval within ±0.10 J.
- Added random energy SD: **≤ 0.30 × 2 J = 0.60 J**;
  require a one-sided **95% upper confidence bound**, not the sample SD alone.
- No unmodelled state transition, reconnect, I/O or missing evidence anywhere
  in the protected interval. A mean near zero does not excuse cancelling steps.

For a coherent error throughout an integration, these translate to:

| Span T | Mean power error corresponding to 0.10 J | Power SD corresponding to 0.60 J |
|---|---:|---:|
| 120 s kit segment | 0.833 mW | 5.000 mW |
| 234.5 s historical 30B episode | 0.426 mW | 2.559 mW |
| 1,200 s span | 0.083 mW | 0.500 mW |
| 1,800 s span | 0.056 mW | 0.333 mW |

The budget applies per scored energy span, not once to an entire 12–16 h window.
The drive must nevertheless remain in its qualified state for that whole window.
Do not divide sampled power SD by sqrt(sample count): correlated wakeups and
slow drift must be integrated over real spans. Under independence, 0.6 J added
to 2 J increases SD by `sqrt(1.09)-1 = 4.4%`; dependence can make that calculation
wrong, so also report end-to-end replay residuals and load/history dependence.

For comparison, using 19–58 J would allow 0.95–2.90 J mean error and
5.70–17.40 J added SD (24–74 mW at 234.5 s for the SD bar). Those margins are
too loose for the proposed replay target. A 1 W state step lasting 1 s is 1 J;
a 4 W step lasting 1 s is 4 J. A 5 W plateau drifting by only 0.01% over 1,800 s
already produces 0.9 J. Large constant draw can be admissible; tiny instability
can fail. Meter/battery uncertainty may make QDC INCONCLUSIVE at this scale.

These fractions are prospective design proposals requiring lead scientific
adoption. v4 should use the strict screen now to avoid qualifying a mode that
immediately blocks v5. A Q1/Q5 PASS with QDC FAIL/INCONCLUSIVE is **not** joint
qualification. Any v4-only adoption despite that needs an explicit narrower
ruling and DC limitation; it cannot license v5 primary energy claims.

## 3. Ranked modes and their observable consequences

All production modes keep models, runs, both in-window copies, custody, monitor
journals and TMPDIR on the internal disk. No SSD reads, writes, hashing, sync,
TRIM request, SMART query or periodic volume probe in a protected interval.
No writes alone is insufficient: metadata reads can wake the device too.

| Rank / mode | GPU rail | PSTR / PDTR; KM003C DC-in | Automation and failure modes |
|---|---|---|---|
| **1: B — attached, mounted, no window I/O** | No direct GPU work is intended; host work, heat and shared-fabric effects remain empirical Q1 questions. | PSTR/PDTR offsets and transitions are empirical, not a published accounting identity. KM003C includes bus draw after battery buffering; stable sleep/idle draw must meet QDC. | Magistrate finishes offload, verifies identity/APFS/ownership, Spotlight disabled, Time Machine exclusion and fsevents settings, then waits the measured settle interval. Spotlight, fseventsd, backupd, APFS maintenance or another reader can wake the device despite settings. A drop/unmount is a fault. **Ed: zero actions/window.** |
| **2: B-unmount — cable connected, all volumes unmounted** | Same indirect paths as B; unmount does not establish electrical isolation. | Controller/bridge/NVMe may remain powered or change states; neither zero power nor reduced variance follows from unmount. KM003C still includes any draw. Measure against absent. | Resolve identity to the current whole disk, run `diskutil unmountDisk <resolved disk>` before pre-arm, verify every child volume absent and physical device still present. After finalize, `diskutil mountDisk <resolved disk>` and verify the expected UUIDs before offload. Busy handles, remount by another service, failure to mount, prompts or wrong disk identity refuse the next arm. No force-unmount. **Ed: zero actions/window.** |
| **3: B-cut — attached to a qualified switchable hub, SSD VBUS off** | SSD-side activity should cease, but the hub/host controller and switching transients remain configuration effects requiring Q1. | SSD power is zero only if VBUS truly drops and there is no backfeed. Hub draw remains in KM003C when bus-powered; PSTR/PDTR treatment still measured. A self-powered hub changes the whole-system boundary. | Flush/offload, unmount safely, then `uhubctl` selects the pinned hub and port to cut power before pre-arm. Verify physical VBUS removal, not just a logical-disable bit. Restore only after finalize, wait for enumeration, mount and verify identity. Unsupported hub, ganged power, reset restoring ON, leakage/backfeed, phantom enumeration and mount failure all fail closed. **Ed: zero actions/window after initial wiring.** |
| **4: A — any writes during the window, including between members** | DMA, daemon work and heat can alter rails; small average effect does not bound variance. | Write/wake/sleep bursts are directly material to DC; bytes and duration can correlate with arm or prior member. | No adoption. Q2/Q3 test mean effects only; they do not establish the required variability bound. External backup/direct routing stays disabled. |

For B-unmount, prevent automatic remount and qualify that prevention on this
macOS build. `diskutil unmountDisk` is not `eject`, disconnect or power-off.
Check all APFS children, not just `/Volumes/JW-EXT`. APST/ASPM support and state
residency of a tunnelled third-party NVMe are **unknown**; elapsed time or an
LED is not proof of sleep.

For B-cut, the task supplies `uhubctl` on macOS as a possible mechanism; no
compatibility was verified offline. Very few hubs truly switch VBUS. Require
macOS-supported per-port electrical power switching, qualified off-state
current/VBUS and no backfeed. Such practical candidates are USB 3.x rather
than USB4, which is adequate for between-window offload. Verify the actual
enclosure's USB 3.x fallback and transfer rate. Keep the hub, its upstream
link and any power supply fixed even when the SSD is off. Never switch a port
carrying the KM003C logger, MagSafe supply or another acquisition dependency.
Firmware/hub supply changes are requalification events.

## 4. Revised qualification: one setup campaign, then no human windows

**Hardware work is [QUIET-MAC], outside this seat and the active blinded job.**
The lead schedules it with nothing armed and all agent/job contention cleared.
Ed's Sunday presence authorizes the setup opportunity, not measurements during
the current job. No measurement commands were run for this document.

### 4.1 Reuse the kit without inheriting its missing capabilities

Reuse `joulewise/align/apple/ssd_qualification.py`,
`scripts/align_ssd_qualification.py`, `scripts/align_ssd_fixed_decode.py` and
the external-volume preparation/checking code. Existing extraction, block-mean
Q1 and Q5 are useful. The existing executable **does not** acquire/evaluate
KM003C, model unmounted/power-cut states, or authorize permanence. Its
`strongest_option_allowed=B` is a legacy GPU-only result.

Retain a five-physical-block comparison for **each** candidate:
**candidate → physically absent → candidate → physically absent → candidate**.
Use actual timestamps, six idle and six decode pairs/block, 120 s planned
segments, 60 s gaps, 600 s block settle: **125 slots, 24,600 s = 6.833 h**.
Presence inference uses five block means with intercept, linear drift and
presence, **2 residual df**. Three blocks have zero df. More segments within
three blocks do not repair it. R12/latency synthesis rejects qualification
shortcuts; neither 30 s gaps nor three blocks authorize a mode.

The old runner writes externally in its write-labelled slots, bursts after
them, and interprets mount absence as physical absence. Therefore it must not
be run unchanged for this design. A reviewed mode-aware runner must preserve
the timing/replication, replace those slots with explicitly labelled quiet
replicates for the no-I/O candidate, and disable external writes/bursts within
candidate blocks. Do not mislabel their results Q2/Q3. Write-pattern diagnostics
may be collected separately as non-adopting A evidence. Between blocks, test
real offload/fsync/unmount/cut/mount transitions, then wait for the qualified
state; 600 s is a minimum, not proof that a slow transition has finished.

Ed does the repeated physical absent/present interventions during this **one
pre-series qualification campaign on Sunday**, then leaves the final setup
connected. Permanent means no routine intervention after that boundary, not
that a single absent observation can supply a confidence interval. If Ed can
only supply one absent block, report a descriptive offset and INCONCLUSIVE
presence qualification. Obtain the needed controls before first permanent use.
For B-cut, measure both truly absent storage and the selected hub+SSD-off
topology; keep the final hub in the control topology when estimating the
incremental SSD effect, and separately disclose/measure hub-only versus bare
MBP. Do not silently use a direct-USB4 control for a hub-based configuration.

### 4.2 Capture and inference

- One continuous internal powermetrics capture for GPU/CPU/ANE/thermal;
  internal 1 Hz SMC PSTR, PDTR, B0AC/B0AV, qualified fast/slow temperatures,
  fans and observed power mode. Never infer KM003C joules from PSTR/PDTR.
- Add one existing KM003C reader, started before the first baseline and kept
  through the last segment/tail. Retain raw streams, clock anchors/fits,
  supervision/restarts, hashes and battery-flow evidence. Reuse existing
  reader/parser and authenticated integration seams; do not create a competing
  logger. R1's separate launch route still needs explicit native confirmation.
- Capture physical-device and mount/power events, metadata-daemon CPU and
  non-waking device-I/O evidence. Qualify observer overhead. Settings alone
  do not prove no access. Do not run `fs_usage`/SMART repeatedly in production
  without qualifying that observation cost and wake behaviour.
- For idle and fixed-work decode, report GPU, PSTR, PDTR and KM003C presence
  offsets with uncertainty, last-access-to-plateau latency, state changes,
  start/end and block scatter. Use the internal-model fixed decode (historical
  kit: 4,096 tokens); also validate the final D model/load and holds. No weights
  are downloaded or placed on the SSD for window use.
- Preserve the Q1 missing-block/retained-count guards, one time basis, finite
  S_slow requirement and nonlinear-drift inspection. A missing block cannot
  silently disappear. Device controls must be independent at the block level.

**GPU/operational gate:** Q1's entire 90% interval for quiet-decode presence
power lies within ±0.25% of reference GPU power (~62.5 mW at 25 W). Q5 requires
arm PASS at both ends, zero unexpected device losses, zero metadata-daemon
contention intervals above 0.05 CPU-s/s, complete thermal evidence with
|S_slow presence offset| ≤0.5 °C, and the existing idle |B0AC|≤200 mA check.
Also retain the current R11 battery/charging rules (InstantAmperage, ≥99% SoC,
top-up/OBC evidence); Q5's older battery threshold is not a replacement.
For unmount/cut, planned state changes between protected intervals are not
device losses; mode-specific identity/event proof replaces the mounted check.

**New DC gate QDC:** use §2's mean and added-SD bounds, separately at idle and
decode and over the actual endpoint's lengths. Report measured p_L; do not
require it near zero. Estimate energy errors after only the prospectively
specified constant/duration and drift terms. A block-aware variance-components
or matched-control analysis must give an upper bound on added variability,
including control/offset-estimation uncertainty. Never report
`sqrt(max(s_mode²-s_absent²,0))` alone as an upper bound. If source separation is
unidentifiable, a conservative bound on total unexplained matched energy is
acceptable; if it exceeds the budget, QDC cannot PASS.

Freeze the inference method and its distribution/dependence assumptions before
capture; validate it synthetically before implementing admission. A Gaussian
independent-block residual SD with just 2 df has a 95% upper bound about
**4.42 × observed SD**. Thus an observed 0.6 J is nowhere near sufficient;
the corresponding observed SD would need to be about 0.136 J. This example
is not a method for dependent segment residuals. Extra physical blocks or
long-span controls may be necessary; the 6.8 h design guarantees neither DC
precision nor a PASS. No post-hoc looser margin or preferred load selection.

Short-segment success does not establish a 1,800 s endpoint or a whole window's
power-state residency. Include repeated actual-span idle/decode/hold probes,
with absent controls at those spans in the Sunday campaign. Then run a full
maximum-window endurance rehearsal of the **selected** mode, including real
offload→quiet entry, first/late replays and finalize→restore/offload. Missing
long-span controls leave v5 primary transfer unqualified. Unexpected I/O, state
change, battery confounding, meter gap/restart through a span or unresolved
clock uncertainty prevents QDC PASS; missing DC must never become zero joules.

### 4.3 MBP time and cadence cost

| Component | Planned occupied MBP time |
|---|---:|
| One candidate's existing five-block shape | 6.833 h |
| All B, B-unmount, B-cut comparisons | 20.500 h |
| Selected-mode endurance at 59,520 s maximum window | 16.533 h |
| One candidate + endurance | 23.367 h minimum |
| Three candidates + selected-mode endurance | 37.033 h minimum |
| Full selected-configuration R1 repeat if needed | about 18.71 h with one OS-batch encounter, before retries/brackets/harvest |

Those totals exclude longer-than-planned decode, physical handling, additional
settling, endpoint-length absent controls, extra blocks for precision, hub-only
controls and failure retries. Add those measured durations explicitly; there
is no defensible guaranteed completion time yet. All three base comparisons
already consume nearly a day, not a 30–45 min turnaround. A single 6.83 h
comparison costs about 0.58 of an R12 ~11.8 h window cycle. Full three-mode
screening + endurance + the illustrative R1 repeat is **about 55.75 h plus
those extras**. Prefer a prospectively ranked B-first/fallback campaign over
automatically buying all three comparisons; unavailable modes stay unqualified.
If all modes must be compared, reserve the full campaign with Ed, including
the repeated absent controls, rather than promising a short Sunday visit.

In production, end offload before the qualified settle interval begins.
Initially retain the old floor `Q = max(30 min, 2 × measured worst
last-access-to-stable-state latency)`, measured for the chosen mode. Mount/
cut/restore transitions count as access. Demonstrate residency for the entire
maximum window. The floor is not a sleep guarantee. R12's 30–45 min target
may be exceeded by offload+Q; overlap Q with cooling only where the measured
physics permits, never overlap offload with a measuring window.

## 5. Joining after absent-drive R1, before W1

**Possible, conditionally; not automatic transfer.** Absent-drive R0/R1 retain
their valid observations for that configuration. Preserve their bytes, outputs
and provenance. Installing the SSD does not retroactively invalidate them,
but they do not thereby qualify a different machine configuration. Amend the
old requirement “attach before R1” to an explicit pre-W1 boundary plus transfer
qualification. W1 remains blocked until it is resolved and registered.

Recheck in the exact adopted mode, stack and physical setup:

1. Internal-only model/cache/log paths, model/quantization/tokenizer/runtime
   identity, sensor inventory/classification and observed power mode. Changed
   topology or sensors can require new R0 classification; no manual substitute.
2. R1 30-min idle soak, reference stability, fast/slow noise and bands S5,
   temperature response/recovery S1–S4/S7, fan behaviour and power/battery flow.
   A Q5 ≤0.5 °C offset alone does not establish thermal transfer.
3. 30B and D step throughput, I_D, tail, sustained-decode decline/S8/S9,
   B_D/T_dead feasibility and completed-turn opportunity. D's slowest rate,
   member budget and R11 contrast-cap arithmetic must still fit, including
   worst allowed waits. No silent budget enlargement or cap reduction.
4. Gated D_bank/D_spam replay pair and X-G with matched predecessor history:
   G0 waits/censoring, W1/D/contrast caps, G1/H recovery, S6 duty/thermal tuning,
   High Power/cooler adoption if used, and the complete final-policy proof.
5. Meter samples/clock/coverage/custody/battery behaviour plus Q1/Q5/QDC;
   native unmount/cut/remount and no-I/O observation. W1 still supplies its
   own reference/U checks and the initial post-W1 desk gate under R12.

**Default recommendation: repeat the full R1 in the selected configuration.**
A lead-approved smaller transfer qualification must name every reused output,
its evidence and original bound; Q1/Q5 alone cannot discharge items 2–4.
Recompute dependent slots/caps and regenerate kit/receipts before W1 where
measurements change; new code/config still needs the exact-candidate gates.
No absent/present pooling of energy or a cross-boundary model-window. A v5
baseline/scorer is separately registered with the permanent configuration.

After adoption, removal, device failure/replacement, unexpected remount or
power-state change has the named consequence **CONFIGURATION_BREAK / REQUALIFY**:
keep raw data, mark the affected window ineligible for qualified calibration/
claims, stop further measurement arms, close that configuration segment, and
require requalification and a prospective series-boundary ruling before
resuming. Do not quietly switch modes or continue the same calibration pool.
For registered v4, the lead must disposition affected W1/fit/calibration/test
sets and any required restart before use; existing clean pre-break windows
are preserved, not automatically pooled into a successor series. This proposed
series-admission rule is not an unapproved new X1–X8 member exclusion.

## 6. Magistrate and kit changes required before adoption

Replace mounted-volume-only refusal with an allowlist of **one physical storage
device in one qualified mode**, while continuing to refuse unrelated external,
network and disk-image volumes. KM003C is an acquisition instrument, not an
extra allowed storage device. UUID alone is insufficient; record drive serial/
model/capacity/firmware where exposed, enclosure/bridge identity/firmware,
APFS container and volume UUIDs, cable/port and hub topology. Missing hardware
serial needs an explicit reviewed alternative identity binding, not a claim
that a volume label identifies the drive. Resolve ephemeral diskN each time.

Pre-arm: finalize prior evidence; verify destination identity and copies;
offload; flush; apply B/B-unmount/B-cut; wait Q and normal cooling/battery/display
dwells; verify census/mode, all internal paths, and actual meter readiness.
Journal every transition internally. Failure refuses the arm. After proven
terminal finalize/hash, restore power/mount if needed, re-identify, offload and
begin the next quiet transition. Crash recovery must prove no window/driver
is alive before restoration; never remount/power-cycle under an uncertain run.
Use bounded timeouts and one documented recovery attempt, then hold for the
lead. No prompts, sudo questions or physical switching in the routine path.

Every window manifest must bind:

- amendment/config/qualification digests and mode; exact physical identity
  and topology; pre-arm/post-finalize identity observations;
- mounted UUID set/state, mount point, current resolved device node, last I/O,
  quiet-start timestamp and measured settling requirement;
- port power state/evidence and times; for B/B-unmount label VBUS on, including
  any unobserved detail; for B-cut bind the pre-cut identity to the powered-off
  port and continuous off-state evidence. Do not wake it to read its serial;
- all in-window mount/device/power/I/O events with full-span coverage, meter
  stream hashes/clock/battery availability, faults and terminal disposition.

The current mounted-volume census and stat-only RouteGuard cannot establish
this. Unmounted hardware, a power-cut device's prior identity and full-span
events need reviewed implementation and tests. Polling `/Volumes` misses
transient changes and says nothing about VBUS. Idle magistrate activity is
also contention: use a qualified lightweight collector, no agent turn during
the window. Qualification, configuration and event-schema changes must be
bound through kit prepare/install/arm and both ordinary/failed-close paths.

## 7. Purchase requirements and remaining uncertainty

If purchasing, choose **4 TB**: v5 raw data is estimated at ~1–1.2 TB per copy,
so two copies alone are ~2–2.4 TB before model/offload retention, filesystem
overhead and working headroom. A 2 TB drive is not a two-copy v5 solution.
Two copies on one enclosure share a failure domain; retain the separately
verified independent second-copy/custody policy. Size usable capacity and
internal staging headroom, not merely advertised TB. B does not expand the
internal space available to a live window; require space for both internal
copies and finalize before every arm.

Specify measured stable idle/sleep power, bounded settle/resume time, no
autonomous LED/fan/controller cycling, exposed persistent identity, reliable
flush/unmount/remount, macOS APFS compatibility, adequate passive heat removal
and **no fan**. Sustained offload bandwidth must fit the turnaround budget;
USB 3.x is acceptable if measured adequate. USB4 maximum throughput is less
valuable than stable power. For B-cut, require verified per-port VBUS control
on macOS, no ganged switching/backfeed and compatible enclosure fallback.
Keep the supply/meter boundary explicit. No product recommendation or current
compatibility claim is made without network access and hardware tests.

Unknown until measured: actual enclosure/host/hub power in each mode; APST/
ASPM and sleep residency; daemon/maintenance wakeups; remount and crash recovery
reliability; meter uncertainty and clock coverage at subjoule budgets; battery
buffering; DC replay SD; mode/load/history dependence; R1 thermal/throughput
transfer; offload speed/settle time; and how many independent blocks yield a
decisive QDC interval. **Permanence is the operating requirement; qualification
determines which automatic mode can meet it.**
