# Permanent external SSD: cross-family agreement and recommended lead ruling

2026-11-08. Opus 5.5 cold reviewer, branch `align/2026-11-08-ssd-permanent-agreement` (cut from `-sol1` @ `b29aae8e0`).
**Advisory to the lead. Nothing here is adopted, measured or wired.** Seats reviewed: Sol-1
(`align/2026-11-08-ssd-permanent-sol1`, docs `ec20d5422`) and Sol-2 (`-sol2`, docs `57f224549`), both cut from
`align/2026-11-08-v4-r11` @ `c3796bf49`; each has `SSD-PERMANENT-STUDY.md` and `DRAFT-AMENDMENT-permanent-ssd.md`.
Authority: `origin/main:RUN_STATE.md` @ `c07b388e9` items 181 (magistrate owns measurement), 210 (KM003C path), 212 R11-3
(v4 residual stays GPU, DC secondary; DC primary in v5), 213 (back-to-back windows, 30-45 min turnaround), 214 R12 and
215 (cadence, R1 deadline >= 67,371 s), plus Ed 2026-11-07 ~23:10: permanent drive "at nearly any cost".
No restricted path, sealed result or hardware was touched. *(verify)* marks unmeasured or unchecked facts.

## 0. Bottom line

The seats agree on almost everything structural, and both are right that writes during windows are out and the old
DC carve-out cannot survive meter-everywhere. They share one blocking flaw: the proposed DC gate (QDC: +/-0.10 J mean,
<= 0.60 J added SD) is roughly 15-250x tighter than any feasible five-block design can resolve, so it can only ever return
INCONCLUSIVE, and both seats make that a hold on permanence. That defeats Ed's ruling. Under true permanence the drive
is a constant part of the machine for the whole series, so the question is not "is presence equivalent to absence"
but "does the drive's state ever change inside a window". That is answered cheaply and directly by device-side
evidence (I/O counters, enumeration identity, Disk Arbitration events) checked every window, with DC-in as
corroboration. Recommended: **B-unmount first** (not B), a **~6.5 h MBP / ~45 min Ed** one-time qualification after
R1 ends, a lean R1 bridge instead of a full R1 repeat, and the borrowed drive for v4 with a purchased 4 TB drive
joining at the v4/v5 boundary.

## 1. Where the seats agree and disagree

| Topic | Sol-1 | Sol-2 | Resolution (reason) |
|---|---|---|---|
| Mode order | B > B-unmount > B-cut; A rejected | Same | **Both overruled on B vs B-unmount** (H-1): B-unmount > B > B-cut; A rejected (agreed). |
| Ed actions per window | Zero | Zero | Agreed. |
| DC criterion | sigma* = min(2 J, endpoint SD); +/-0.10 J 90% equivalence on mean error; 95% UCB added SD <= 0.60 J; early/late drift same bound | Fixed 2 J reference; same 0.10 / 0.60 J; adds `r(T)=integral - p_L*T` framing | **Both replaced** (B-1): event-based stability plus descriptive offset; numeric DC equivalence deferred to v5 metrology, scaled to the DC endpoint's own SD. `min()` in Sol-1 is the wrong direction (L-2). |
| Constant watts vs joules (`p*T` with varying T) | Yes | Yes, with 300 s = 1,500 J example | Agreed and correct; a v5 endpoint must subtract same-configuration idle, not rely on an intercept. |
| Qualification shape | 5 physical blocks per candidate, Q = 1,800 s settles: 8.5 h each; 13.5-18.5 h one mode incl. setup + bridge; 30.5-35.5 h three | Kit as is, 600 s settles: 6.833 h each; + 16.533 h endurance window: 23.37 h one, 37.03 h three; + full R1 repeat ~55.75 h | **Neither** (H-3): presence equivalence is moot under permanence. One plug-in, ~6.5 h automated characterization + bridge. Arithmetic in both checks out (L-1). |
| Endurance | Separate window-length soak "if needed" | Mandatory 59,520 s rehearsal | **W1 is the endurance test**, with the per-window checks below; a failure costs one window (counted as a loss), not a dedicated 16.5 h run every time. |
| R1 -> W1 | Bridge addendum, 4-8 h; retain settings that still meet their owning criteria | Default full R1 repeat (~18.71 h) | **Sol-1's bridge, leaner (~2.5 h)** (M-1): the drive sits outside the chassis; R1's own bands decide transfer; rerun only the step that fails. |
| Configuration break | Preserve, stop arms, pool nothing across; new segment ruling | Window ineligible, stop arms, requalify | **Agreed in substance; simplified**: an SSD event makes the window a whole-window loss under R12 B3 (W1: repeat W1); hold next arm for lead. |
| Arm rule | Allowlist one physical device in one mode; mode-aware census; passive in-window evidence | Same; adds D-043 supersession closure | Agreed; Sol-2's D-043 closure adopted. Concrete text in §3.4; mechanism named (M-3). |
| Purchase | 4 TB, fanless, predictable power; no product | Same | Agreed on 4 TB; **made actionable** in §3.5 (bridge class matters more than drive brand, M-4). |
| Q1 GPU presence gate | Keep (+/-0.25%) | Keep | **Demote to descriptive** (H-3); R12's "no SSD-qualification shortcuts" addressed in §3.1. |

## 2. Cold-review findings (both seats unless named)

**B-1 BLOCKER: QDC cannot pass, and failing it blocks permanence.** Both gates are an equivalence interval on a
five-block alternating design (intercept + drift + presence, 2 df). For blocks at t = 0..4 with presence 1,0,1,0,1 the
presence SE is 0.913 sigma_b, so the 90% half-width is 2.92 x 0.913 x sigma_b = 2.67 sigma_b. The required half-width
at a 120 s span is 0.833 mW (0.10 J / 120 s) and at 1,800 s 0.056 mW. Even an optimistic sigma_b = 5 mW between-block
SD of whole-machine DC-in means (display asleep; daemons, battery float and meter noise all land here) gives 13 mW:
16x too wide at 120 s, 240x at 1,800 s, so 250-57,000x more blocks. The SD bound is worse (Sol-2's own 4.42x factor).
Failure scenario: Sunday spends 7-37 MBP hours, QDC returns INCONCLUSIVE as it must, both amendments then "hold the
permanent exception", and Ed is back to manual plug/eject. Second defect: the 2 J figure is the **GPU-rail
replay-referenced** residual SD; the DC endpoint's residual SD is unmeasured and almost surely larger (it carries CPU,
fans, battery and the drive). Scaling a DC tolerance to a GPU SD is a category error. Fix: §3.2.

**H-1 HIGH: B (mounted) ranked above B-unmount.** A mounted volume is reachable by any process (`mds`/`mdworker`,
`fseventsd`, `backupd`, Finder/QuickLook, a stray `stat` or shell cwd, our own tooling). With a sleep timer active, one
access wakes the drive and holds it awake for the timeout: a ~3-5 W step *(verify; old study's anecdotes)* for ~10 min
(pmset `disksleep` default *(verify on the MBP)*) is ~1.8-3 kJ, far beyond any DC tolerance and invisible to the
mount-table census. "Indexing off" settings reduce, but cannot prove, silence. An unmounted volume has no filesystem
consumers at all, and the cost is two `diskutil` calls between windows. B's only advantage, no mount/unmount cycle,
is outweighed. Bonus: the current mount-only arm rule already passes under B-unmount; only the device census is new.

**H-2 HIGH: Sunday's plan collides with R1.** R0 re-run 11 had a 04:30 PST 11-08 deadline (item 211); R1 arms after it
and needs >= 67,371 s (item 215), so R1 occupies the MBP until about 23:00 Sunday at the earliest. Both seats speak of a
Sunday campaign "if the machine is free"; neither says it isn't. Fix: Ed's single physical step happens at R1's terminal
completion (Sunday late evening, else Monday morning); Sunday daytime builds and reviews the hooks on the Air.

**H-3 HIGH: Presence equivalence is the wrong question, at a disproportionate price.** Q1 and the five-block
absent/present design guard comparability between drive-present and drive-absent windows. Under permanence there are
none inside a series: every W1/D/calibration/test window has the same drive in the same state, so a constant offset is
part of the machine and cancels in every within-series contrast. What can bias v4/v5 is a state change correlated with
arm or position, which presence equivalence does not detect (it averages over blocks) and per-window device evidence
does. The repeated physical absences also need Ed for 4 replugs per candidate over 7-8.5 h each, the opposite of the
goal. Comparability to drive-free history (R0/R1) is a transfer question, handled by the bridge (§3.3).

**M-1 MED: Sol-2's default full R1 repeat (~18.71 h).** The drive is outside the chassis at >= 30 cm; the plausible
in-chassis effect is the USB4/USB host link (old study: 0.1-0.5 W, a guess). R1's own soak and step bands are the
right yardstick; rerun a step only if it misses its band. Sol-1's bridge is right; its 4-8 h allowance is generous.

**M-2 MED: Re-enumeration and automount are named but not prevented.** USB4 link retrain, cable bump, controller reset
or a reboot re-enumerates the drive under a new `diskN`; Disk Arbitration then **auto-mounts** it, Spotlight/fsck may
run, and the drive wakes mid-window. Fix: `/etc/fstab` entries `UUID=<volume-uuid> none apfs rw,noauto` for every
volume in the container (one-time, `sudo vifs`, Ed types the password) so nothing automounts; the magistrate mounts
explicitly with `diskutil mount <UUID>` *(verify both on this macOS build, §3.2 step 2)*. Also unflagged by both: macOS
**accessory security** on Apple-silicon laptops can hold a re-enumerated USB/Thunderbolt accessory until the user
unlocks the Mac; with the screen locked and Ed away the drive would not come back. Set "Allow accessories to connect"
to a non-prompting value once *(verify the option names)*, and test with a locked-screen replug. This also weighs
against B-cut, which re-enumerates the drive every window.

**M-3 MED: No concrete in-window evidence mechanism.** Both require a "qualified passive full-span collector" and
leave it unspecified. Zero-overhead, zero-wake mechanisms exist: (a) the IOBlockStorageDriver `Statistics` counters
(bytes and operations read/written) read from the IORegistry (`ioreg -r -c IOBlockStorageDriver -w0`), which never
touch the device; snapshot at unmount, pre-arm and post-finalize; (b) the device's IORegistry entry ID (changes on any
re-enumeration); (c) after finalize, `log show` over the window for Disk Arbitration/IOKit appear, disappear and mount
events. Nothing runs during the window.

**M-4 MED: Purchase spec omits the dominant power consumer, the bridge.** Old-study anecdotes put the OWC USB4
(ASM2464PD) enclosure at 4.5-6 W awake, 1-1.5 W with the drive asleep *(verify)*, i.e. the bridge dominates. A USB 3.2
Gen 2 (10 Gb/s) bridge typically draws much less and its USB suspend states are mature on macOS *(verify on Sunday's
borrowed-drive data vs the purchased one)*. At ~0.8-1 GB/s a 26.4 GB D-window copy takes under a minute, so USB4 speed
buys nothing for a 30-45 min turnaround. Also: behind any USB bridge an NVMe drive gets no host memory buffer, so a
DRAM-less drive (the SN7100 is one) can slow sharply on 20-50 GB sustained writes; prefer an on-drive-DRAM TLC drive.

**M-5 MED: Fault consequence lacks a registered count rule.** "Stop, requalify, lead rules a new segment" is right but
leaves the window's status to post-hoc judgement. Prereg fidelity wants it prospective and blind: an SSD event makes
the window a whole-window loss under R12 B3 (min 6, cap 8 already absorbs losses); W1 is repeated.

**L-1 LOW (arithmetic, verified):** 24,600 s = 5 x (600 + 24 x 180); 30,600 s = 5 x (1,800 + 4,320); 16.533 h =
59,520 s; 23.367 = 6.833 + 16.533; 37.033 = 20.5 + 16.533; 55.75 = 37.033 + 18.71; chi-square 2 df 95% SD UCB factor
sqrt(2/0.1026) = 4.415; coherent-power tables (0.10 J / T, 0.60 J / T) all correct.
**L-2 LOW (Sol-1):** `sigma* = min(2 J, endpoint SD)` tightens the drive budget when the DC endpoint is *noisier*;
it should scale with the endpoint's own SD.
**L-3 LOW:** `diskutil unmountDisk` on the APFS physical store vs the synthesized container disk: verify which node
unmounts all volumes, and check every volume in `diskutil apfs list` (both seats say "all children"; name the node).
**L-4 LOW:** mount after an unclean disconnect can trigger `fsck_apfs`, and APFS may issue trim on mount; both are I/O
between windows, so Q must start at observed I/O quiescence (counters stable), not at the `mount` exit code.
**Agreed physics (no finding):** KM003C sees drive power via the Mac's port (plus conversion loss), not AC; battery
float can time-shift it; PSTR/PDTR are not component meters; A's bursts correlate with arm via `member_s`; a dock or
hub sourcing USB-PD to the Mac would bypass the KM003C.

## 3. Recommended lead ruling (proposed "SSD-P1")

### 3.1 Mode order and what is dropped

**B-unmount** (adopt) > **B** (fallback only if unmount/mount automation fails its test) > **B-cut** (contingency only
if the unmounted drive's power is unstable; requires buying a hub) ; **A rejected**. One mode frozen per series.
Q1 presence equivalence, the five-block absent/present runner and QDC are **dropped as adoption gates**; GPU/PSTR/PDTR/DC
offsets are reported descriptively. This does not reverse R12's rejection of "SSD-qualification shortcuts": that
rejected shortening the presence-equivalence test while it was still the right question. Permanence removes the
question (H-3); the series-homogeneity guarantee replaces it. Blinding and prereg fidelity are untouched (§3.4 rules
are written into the registration text before W1; nothing reads outcomes).

### 3.2 The one-time qualification (after R1's terminal completion; ~6.5 h MBP, ~45 min Ed)

Prerequisite (Air, Sunday by day, off the MBP): build and review the B-unmount hooks, census and per-window checks
(§3.4) with unit tests; two seats review (Sol + Opus); the magistrate installs them. No MBP time.

1. **Absent reference, automated, 30 min.** Right after R1 finalizes: display asleep, magistrate idle, KM003C + rails +
   SMC captured at idle. This, R1's own soak and step 4 give a descriptive absent/present offset.
2. **Ed at the Mac, ~45 min.** Plug the drive into the fixed port, fixed cable, >= 30 cm placement away from intake and
   exhaust. Approve the accessory; set accessory security to non-prompting. One-time admin: `fstab` `noauto` entries
   for every volume UUID; `mdutil -i off`; `tmutil addexclusion`; `.fseventsd/no_log`; `.metadata_never_index`; check
   `pmset -g` (`sleep 0` on AC; record `disksleep`). Enroll identity (model, serial, firmware, bridge VID/PID,
   container and volume UUIDs, port location ID). Show the borrowed drive's contents before any erase (Ed's 11-06 rule).
   **Replug test:** Ed unplugs and replugs once with the screen locked; PASS if the device returns, nothing automounts
   within 5 min, and identity re-resolves under the new `diskN`. Ed is then done.
3. **Automation cycles, automated, ~2.5 h.** Three cycles of: `mount` by UUID -> offload stress (one D-sized 26.4 GB
   copy, hash-verified) -> flush -> `unmountDisk` -> wait for counter quiescence -> settle. From cycle 1 measure L =
   last I/O to DC-in plateau (60 s median within 0.1 W of the final 30 min median). Set Q = max(30 min, 2L). One
   negative test: hold a file open on the volume; `unmountDisk` must fail, the hook must log the dissenter, retry 3x and
   refuse (no force).
4. **Plateau and wake-step test, automated, ~2 h.** Unmounted idle for 2 h with full capture, then one forced wake
   (mount, read 1 GB, unmount). Measure the wake step size S in DC-in.
5. **R1 bridge, automated, ~2.5 h** (§3.3).

**PASS (all required):** P1 three of three cycles complete with no human action and no force, each unmount verified
for every container volume with the device still present, each mount verified by UUID, every offload hash-verified;
P2 replug test passes; P3 a plateau exists and Q <= 60 min (a longer Q is accepted and disclosed, not a failure; no
plateau is a failure); P4 over the 2 h plateau: zero change in the I/O counters and entry ID, zero Disk Arbitration
events, and no DC-in step >= S/2 lasting >= 5 min that is not explained by a logged contention episode (R0-L3 flags);
P5 the bridge passes. **Fail handling:** P1/P2 are software or settings: fix and repeat step 3/2 (only P2 needs Ed).
P3/P4 failing on DC with zero I/O: v4 may proceed (GPU primary; DC secondary disclosed with the measured drift); fix
before v5 (B-cut or the low-power enclosure). P4 with I/O or events: hold and diagnose. No margin is loosened after
seeing the data; these thresholds are frozen by this ruling.

### 3.3 What changes for R1 and W1

R1 tonight stays drive-free and immutable. W1 registration waits for SSD-P1's PASS. The **bridge** binds R0/R1 digests
to the enrolled configuration: a 30 min idle soak and one D load/recovery step with KM003C live, compared against
R1's own bands (noise, reference temperature, recovery, decode throughput) and battery float; plus a meter
samples/clock/custody check (item 212 R11-3). Inside its band, the R1 setting is kept by a digest-bound receipt;
outside, rerun that R1 step in the final configuration and refreeze before W1. No budget or cap is re-derived unless
its input moved. Registration text gains: the configuration (device, mode, Q), the per-window checks and the SSD-event
rule. **W1 is the first endurance test** under those checks. Old "attach before R1" is superseded; record under D-043
(annotate FINAL-DESIGN's physical setup, item 181 runbooks, the old study/amendment as historical).

### 3.4 Arm-rule text (replaces "refuse while any external volume is mounted", effective at adoption)

> **ARM-SSD.** The magistrate arms only if the physical storage census shows exactly one external storage device,
> the enrolled one (identity per the enrollment receipt), present with **every** container volume unmounted; no other
> external, network or disk-image volume mounted; its IORegistry entry ID and I/O counters equal those recorded at
> its last verified unmount; and at least Q seconds since that unmount's counter quiescence. A census read failure, a
> missing or extra device, any mounted volume of it, an identity or entry-ID mismatch, or a counter change refuses the
> arm. The KM003C and its logger are instruments, not storage. At post-finalize, before remounting, the magistrate
> re-reads entry ID and counters and queries the unified log for the window's span; any change or device event marks
> the window **SSD_EVENT**: it counts as a whole-window loss under R12 B3 (W1 is repeated), the next arm holds for the
> lead, and a second SSD_EVENT in a series requires requalification. Between windows: finalize -> remount by UUID ->
> offload and verify -> unmount -> Q, all bounded by timeouts, one retry, then hold; never force-unmount, never
> remount while a run may be alive, never write to an empty mount point. Zero Ed actions per window.

An absent drive after adoption is a configuration break, not a return to the old rule. Implementation: extend
`joulewise/align/apple/external_volume.py` with the B-unmount mode, physical census, counters and log query; wire
magistrate pre-arm, session prepare and kit readiness to one receipt; manifest fields as both seats list.

### 3.5 Hardware and purchase

**v4 runs on the borrowed SN7100/OWC** if Ed's friend agrees to leave it for the v4 series (~2-3 weeks; v4 needs
roughly 0.3 TB per copy). The purchased drive joins at the **v4/v5 boundary**, where v5 requalifies its DC endpoint
anyway, so the purchase is off W1's critical path. If the borrowed drive cannot stay through v4, buy now with fast
delivery and run §3.2 on the purchased unit before W1; a mid-series swap is a configuration break.

**Purchase recommendation (availability and prices need checking; product names are examples of widely known classes):**
- **Capacity 4 TB** (v5 raw ~1-1.2 TB per copy; two copies ~2-2.4 TB plus models and headroom). 2 TB is not enough.
- **Drive:** M.2 2280 NVMe, **TLC with on-board DRAM**, not QLC, not DRAM-less/HMB; e.g. WD Black SN850X 4 TB or
  Samsung 990 Pro 4 TB class. Gen 4 is plenty.
- **Enclosure:** fanless aluminium, **USB-C, USB 3.2 Gen 2 (10 Gb/s)**, Realtek RTL9210B-class bridge (or equivalent
  with UAS on macOS), no fan, no RGB, no vendor software, serial visible in `system_profiler SPUSBDataType`; with a
  short certified 10 Gb/s USB-C to USB-C cable. Rationale M-4: lower, steadier bridge power; speed is not a constraint.
  A USB4 enclosure like the borrowed OWC is acceptable if Ed prefers, but expect several watts more and more heat.
- **Do not buy a hub now.** Only if P3/P4 fail: a hub with genuine per-port VBUS switching supported by `uhubctl` on
  macOS (check its compatibility list), no upstream USB-PD to the Mac, fixed in the topology.
- Never use a powered dock or hub that charges the Mac: it bypasses the KM003C.

### 3.6 What the seats' drafts become

Base the amendment on Sol-1's A2/A3/A6 state machine and manifest plus Sol-2's A1 (D-043, power path) and A3 (`p*T`);
replace mode order, A4/QDC, R1 repeat, endurance and purchase text with §3.1-3.5. Keep the five-block kit only if the
v5 design asks for a presence contrast, else retire it in `CANONICAL.md`. Flash-Next tests on the drive are
between-window I/O and must end before Q starts.
