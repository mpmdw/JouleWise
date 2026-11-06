# Keeping the external SSD attached to the measurement MacBook Pro: feasibility study (DRAFT)

Author: Opus 5.5 (laptop lead's delegate), 2026-11-06. Branch `lane/2026-11-06-ssd-always-attached`, cut from
`origin/lane/2026-11-05-align-pilot10-benign` @ `f3af22b94` (the merged ALIGN v4 kit). That lane holds
`joulewise/align/`, which has no pin, so the new code can live there. `origin/main` (magistrate, `launch_align_r0.py`,
night and custody tooling) was read but not changed. No hardware was touched. Nothing under `jw-b5-*`, `night-*`,
`night-custody`, `night-archive` or `restricted/` was opened.

Status: a study and a draft. Nothing here is in force. Today's rule still binds: no external volume is mounted during
R0, R1, W1 or the calibration windows (RUN_STATE item 181). Changing the rule needs the council and Ed; the draft
amendment is `DRAFT-AMENDMENT-external-log-volume.md`.

The drive: a borrowed WD_Black SN7100 2 TB (PCIe 4.0, DRAM-less) in an OWC Express 1M2 (USB4 40 Gb/s, bus-powered,
ASMedia ASM2464PD bridge). It arrives Saturday 2026-11-07.

---

## 0. Bottom line

**Recommendation: Option B, if the qualification passes. Not Option A.** B keeps the drive attached all the time but
writes nothing to it during a window. Logs go to the internal disk as today, and bundles move to the SSD between
windows. Until the amendment is adopted, Option C (attach by day only, today's rule) stays in force. C also stays in
force for any measurement at the DC or whole-machine boundary (BYTES-type), whatever happens here.

Why, in numbers:

1. **The estimand cannot see the drive directly.** ALIGN's residual, U3 and the contrast all integrate
   `powermetrics:gpu_power`, the GPU rail from IOReport's energy model (`pilot_analysis.py:192`). The enclosure draws
   VBUS power from the Mac's USB-C port: forum measurements put it at about 1-1.5 W asleep, 4.5-6 W idle and 7.5-8 W
   while writing. The external load is not GPU work, but neither Apple nor this repository supplies a public rail-boundary
   specification proving that every host-controller cost is excluded from `gpu_power`, or that SMC PSTR/PDTR attribute
   every VBUS watt in a particular way. The qualification must therefore measure GPU rail, PSTR, and PDTR rather than
   infer one from another. Plausible indirect paths include heat, shared-fabric contention, and OS daemon CPU work.
2. **The real write load is arm-independent during measured segments, by construction.** Bundles are 89 % raw
   powermetrics plists (mean 507 MB per pilot-v3 member). The plist streams to the internal `TMPDIR` at a fixed 10 Hz,
   about 512 kB/s, and is copied into the bundle only after the post-window dwell. Every arm-dependent byte (turns,
   transcript, events, episode: about 2.2 MB per member) is written after the episode returns
   (`workload.py:689-697`, `output_artifacts`). Inside an episode, the bundle tree gets only the 1 Hz thermal sidecar (fsync every 5 s)
   and two tiny logs. So the danger the brief names, "hidden-work arms write more bytes", does not occur inside
   turn-owned segments with today's writers. Under A it occurs between members, which is unowned time followed by
   300 s of idle and the G0 gate.
3. **A buys disk space; B buys the operational win.** A window writes 18.6 GB per copy (W1) to 26.4 GB per copy
   (D windows), so 37-53 GB for the two in-window copies. Free space on the MacBook Pro has run between 51 and 115 GB.
   The pressure, though, comes from retained data: model weights (the window models alone are 17.2 + 44.9 + 29.5 GB,
   plus about 130 GB of reserve and fallback weights) and retained pilot roots (about 19-38 GB each). Ed's 11-06
   retention ruling already moves those to the SSD. Once they are off, a window's own 37-53 GB fits, and B adds no
   write path during windows. A would also put the primary custody copy on a borrowed, removable device that can drop
   mid-window. B removes about 16 plug/eject actions from Ed over the series, and the risk of losing a whole 12-16 h
   window to a forgotten eject.
4. **The bars are tight but reachable.** On the 30B (the smallest s_r, 19 J per pair), an episode bias of
   ≤ 0.05·s_r is about 4 mW of GPU-rail power over a 234 s episode. The protocol (§6) resolves that at idle, where
   GPU-rail noise is a few mW. Under decode it resolves about ±14 mW (expected) against a 24 mW mean-effect bar. B
   needs only the presence and operational criteria (Q1, Q5); A also needs the write criteria (Q2, Q3) and a
   write-variability criterion still to be defined.

**What would change the recommendation.**
- Q1 or Q5 fails (presence moves decode GPU power by more than 0.25 %, the drive drops, or metadata daemons wake): C.
- Ed cannot lend the drive for the whole series: C. Removing the drive mid-series is a configuration break.
- The disk still binds after the offloads, Q2 and Q3 pass, and a write-variability criterion is added and passes: A-lite, which writes the backup copy to the SSD between
  members, as a separate lead ruling.

---

## 1. What the instrument measures during a window

| Channel | Source and cadence | Used for | Code |
|---|---|---|---|
| GPU rail energy | `powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal --format plist`, 10 Hz (`power_hz: 10.0` in every align config) | **The estimand.** Turn-owned GPU energy per turn; per-pair residual and score; U3; the W1 contrast d_t | `joulewise/adapters/powermetrics.py:58,1480-1497`; `pilot_analysis.py:192-212` |
| CPU and ANE rails | same stream | idle admission ("processor power"), prints | same |
| Thermal pressure | same stream (`thermal` sampler) | U1(a), X3 | same |
| SMC B0AC, B0AV, PDTR (DC-in), PSTR (system total), PPBR | `joulewise/hazards/smc.py`, 1 Hz | battery float and assist hazard; PSTR − (GPU + CPU + ANE) printed as the "unassigned power residual" (FINAL-DESIGN §2.4) | `smc.py:19-52`; `hazards/battery.py` |
| SMC T* / F* keys | 1 Hz sidecar `outputs/align_thermal.jsonl` | G0, G1, holds; U2; U5 | `joulewise/align/apple/thermal.py:104-118` |
| Process CPU | `ps` snapshots every 10 s in the window; 30 s intervals at arm | contention hazard (> 0.05 CPU-s/s outside the tree flags `contention.request_overlap`) | `joulewise/hazards/contention.py` |

**The residual and s_r.** The frozen sequence design `[1, P, D, (C+P)D + D²/2, CP + P²/2]` is fitted per model × pair ×
session on logged token counts (alternative desk `4d54cb47b`, calibration `7fbd95e31`). The per-pair residual scale
s_r is that fit's benign misfit. A score is residual/s_r, and the threshold is rank `⌈0.95(m+1)⌉`, the sample maximum
at m ≈ 20. Observed values:
- 30B: s_r 19-33 J (spam) and 45-58 J (bank) on episodes of about 2.7 kJ.
- 30B identical-work pair-difference SD: 2.97 J.
- Within-window drift: up to about 10 J.
- Contrast bars: 6 J and 10 J.
- U3 bar: 3·max(2.97 J, 0.0011·E).
- U4 point bar: ±0.25 % (FINAL-DESIGN §2.4-2.5).
- Projected D s_r: 110-1,440 J on 15-45 kJ episodes, at e_D ≈ 3.5 J/token (council 2026-11-06 CHAIR §C; fable-cold).
- MDE ≈ q·s_r/e: about 80-370 tokens for the 30B.

**The noise floor that matters is s_r, not the meter.** The instrument floor is about 2-30 tokens. Energy-model misfit
limits detection (fable-cold, MDE section).

---

## 2. The always-attached drive, channel by channel

### 2.1 Power facts (no official enclosure figure exists; treat these as ranges)

| Item | Figure | Source |
|---|---|---|
| SN7100 maximum | 4-4.5 W | Newegg spec, SmartHDD |
| SN7100 PS4 / L1.2 sleep | about 5 mW (spec); 0.03 W measured in one review | Newegg; Framework forum |
| SN7100 idle with L1 ASPM | about 1 W (one test bed) | ssdwiki |
| OWC Express 1M2 (ASM2464PD) on macOS USB4, idle, LED on | 4.5-6 W (wall-meter anecdotes) | MacRumors threads |
| same, writing | 7.5-8 W | MacRumors |
| same, drive asleep (LED off) | 1.0-1.5 W | MacRumors |
| Whether macOS enables APST/ASPM for a tunnelled third-party NVMe | unknown **(guess: partially)**; the qualification measures the drive's states in PSTR | — |

The figures in the table above are for **presence**. The enclosure is bus-powered, so its electrical input ultimately
comes through the Mac's adapter/battery power path. How the undocumented SMC PSTR and PDTR keys report that load, and
whether host-side work appears in a powermetrics modeled rail, are empirical questions in this protocol. A constant few watts, against a 140 W adapter that runs
D's decode at roughly 60-100 W whole-machine **(guess)**, does not threaten the battery float. It slightly raises the
odds of battery-assist seconds, which are DISCLOSE-only.

### 2.2 The SoC-side USB4 controller

On the M3 Max, the Thunderbolt/USB4 host and its PCIe tunnel involve host-side logic. No source cited here establishes
which powermetrics modeled domain, if any, receives that cost, nor that `PSTR - (CPU + GPU + ANE)` is a physically
exclusive rail. An active-link cost of **0.1-0.5 W is an unverified planning guess**, not a physics input to a verdict.

One possible path into the GPU rail is temperature; shared-resource and scheduling paths are also possible. A planning
calculation using GPU temperature sensitivity of about 0.1 W/°C **(unverified guess: leakage ~15 % of 25 W, doubling
per ~25 °C)** and +0.1-0.3 °C gives about 0.01-0.03 W, or 2-7 J over a 234 s episode. This is a sensitivity scenario,
not a measured enclosure effect.

That figure is a constant **presence offset**, the same in every arm. Three things absorb it:
- the per-session fit intercepts;
- the window-local thermal reference R, measured with the drive attached;
- G0, which releases each episode at the same start state.

It matters only across a configuration change, so it is bounded at the U4 point bar (Q1).

### 2.3 Power-state transitions caused by writes

This is the **variance and correlation** question. Under A, every write wakes the link and the drive (L1.2 to L0,
PS4 to PS0). The stated 10-100 ms, +2-6 W, and 0.02-0.6 J ranges are unverified planning guesses. The external-device
portion should primarily affect whole-system/input channels, but the protocol does not assume it appears **only** in
PSTR and PDTR; host work and thermal coupling can alter modeled rails.

The in-episode writers have fixed cadence: the thermal sidecar fsyncs every 5 s. Whether that cadence prevents this
enclosure/SSD combination from entering a low-power state is unknown and must be observed; it cannot be inferred from a
generic timer assumption.

Under B nothing writes, so the drive falls asleep a set time after the last access and stays asleep. The one
transition (−3 to −5 W in PSTR) must happen before the window, hence the quiet period in the amendment (A5).

### 2.4 CPU and I/O wakeups

The write path for the external drive costs the CPU about the same as the internal one: the bytes and the syscalls are
the same. Only the driver stack differs (IONVMe over a PCIe tunnel versus Apple's internal ANS). The CPU rail sees
milliwatts.

DMA for 1 kB/s (A, in-episode) or a 1 GB burst between members (A, post-member) does not compete with decode's
memory-bandwidth demand during episodes.

### 2.5 Thermal coupling of the enclosure itself

The enclosure runs warm at 5-8 W and sits on its cable outside the chassis. Placement is part of the physical setup:
at least 30 cm away, not near the intake or the exhaust, and fixed for the series (FINAL-DESIGN §3.1).

### 2.6 Background OS activity triggered by a mounted volume

This is the **real risk**. A mounted volume can wake several daemons:
- **Spotlight:** `mds`, `mds_stores`, `mdworker_shared` and the text importers on JSON/JSONL/CSV bundles.
- **fseventsd:** its on-volume log flushes. A runaway `fseventsd` has already delayed an arm on this Mac
  (RUN_STATE, C1 09-30).
- **Time Machine:** the "use this disk?" prompt, or `backupd`.
- **APFS:** a free-space trim at mount, and `fsck_apfs` after an unclean disconnect.
- **diskarbitrationd:** probes at mount.

Coverage today is partial:
- The R0 launcher SIGSTOPs only the per-user `corespotlightd` and `spotlightknowledged`.
- The root `mds` family runs freely.
- The contention hazard would flag any of these above 0.05 CPU-s/s and exclude the overlapping members. The cost is
  lost members, not biased ones.

Mitigation:
- Spotlight off by `mdutil -i off` (authoritative). `.metadata_never_index` is recorded but recent macOS may ignore
  it.
- `.fseventsd/no_log`.
- A Time Machine volume exclusion, plus `DoNotOfferNewDisksForBackup`.
- Ownership on.
- Mounted once, by day, outside windows.

The arm check refuses if any of these is missing (§7).

### 2.7 Summary

| Effect | Presence (constant offset) | Variance (adds to s_r) | Correlation with arms | Channel | Under B | Under A |
|---|---|---|---|---|---|---|
| Enclosure + SSD bus power | 1-8 W | state toggles | only if writes differ by arm | PSTR, PDTR, battery | constant asleep | constant awake (5 s fsync cadence) |
| SoC USB4 link power → heat → GPU leakage | ~0.01-0.03 W GPU **(guess)** | ≈ 0 | none (constant) | GPU via T | absorbed | absorbed |
| Write syscalls, DMA | — | mW | in-episode writes are fixed cadence | CPU | none | ≈ 0 |
| Post-member burst (raw copy, reduce, backup) | — | — | yes (bytes ∝ member_s) but **unowned**, before 300 s idle + G0 | all | none | A-lite/A only |
| Metadata daemons | — | possibly large | could correlate with write volume | CPU, fabric, GPU clocks | none if indexing is off | none if off; contention flags otherwise |
| Disconnect or remount mid-window | step | large | random | all | flag and exclude member | same, plus the write path falls back |

---

## 3. The write load, from the code

Measured from `configs/campaigns/align_pilot_v3/registration/sizing_evidence.json`: 24 pilot-v3 members, mean bundle
507 MB, mean member about 650 s.

| File (per member) | Mean bytes | Share | When written |
|---|---|---|---|
| `raw/powermetrics.plist` | 212.8 MB | 42.0 % | streamed to internal `TMPDIR` during the member; copied in after the dwell |
| `raw/powermetrics_idle.plist` | 157.0 MB | 30.9 % | 300 s idle at 10 Hz, so about 52 kB per sample; same path |
| `instrument_calibration/raw/powermetrics.plist` | 83.6 MB | 16.5 % | calibration capture; same path |
| `rich_telemetry*.jsonl` | 47.3 MB | 9.3 % | reduce, after the member |
| `outputs/align_turns.jsonl`, transcript, episode, `events.jsonl` | 2.2 MB | 0.4 % | **after the episode returns** (`workload.py:689-697`, `output_artifacts`) — the only arm-dependent bytes |
| everything else (traces, metadata, ioreg) | < 2 MB | — | before or after |
| `outputs/align_thermal.jsonl` (v4 sidecar) | about 0.4-1 kB/s **(estimate)** | — | **during the episode**, 1 Hz, fsync every 5 s |

Laws and per-member totals:
- Disk law: bytes = 186.75 MB + 512.4 kB/s × member_s (n = 24, residual SD 2.1 MB).
- 30B anchor (783 s): 588 MB.
- N (1,200 s): 802 MB.
- D (1,800 s): 1.11 GB.
- Backups: after every successful member, `run_campaign.py:11454-11462` runs `backup_runs.sh` (rsync of the runs
  root) between members.

Per window: W1 is 18.6 GB per copy and a D window 26.4 GB per copy (FINAL-DESIGN §2.3, §2.7), which is 37-53 GB for the
two in-window copies.

**Arm dependence.**
- Inside turn-owned segments: none. The only writers are fixed-cadence (the powermetrics stream to `TMPDIR`, the
  sidecar, the monitor journal in custody).
- Between members: yes. The bytes follow member_s. A contrast G member is planned 300 s longer than an S member, so
  about 154 MB more. Under B this never touches the SSD. Under A it is unowned time, followed by the next member's
  idle, idle admission and G0.

**Model weights.**
- The window models (17.2 GB 30B, 44.9 GB N, 29.5 GB D) stay internal under every option.
- `mlx_lm.load` reads safetensors lazily and materializes them into Metal buffers at `mx.eval(model.parameters())`
  (`r0_mlx.py:76`). Decode is not file-backed, so weights on the SSD would mean reads at load only.
- Load still sits inside each member: a fresh process per member, so 17-45 GB re-read at about 3 GB/s over USB4 with
  the enclosure at 7-8 W. That changes I_m (the member intercept R1 measures) and the load-heat transient. **Window
  models therefore stay internal.** Non-window weights belong on the SSD:
  - the 122B (69.6 GB);
  - Next-Instruct (44.9 GB);
  - D-4bit (16.1 GB);
  - Flash-Next sources.
- The qualification's fixed-decode load reads weights from internal only. Whether decode is file-backed is a
  protocol check (`fs_usage`/`iostat` shows no SSD reads during decode).

## 4. What fills the measurement Mac's disk

Free space recorded in RUN_STATE:
- 33 GB, then 115 GB after the 09-xx prune;
- 102 GB before pilot 10;
- 66 GB after pilot 9;
- 58 GB after pilot 8;
- 51 GB after pilot 7.

The "80 GB free after weights" arm floor (FINAL-DESIGN risk 11) is therefore binding today.

The weights add up as follows:
- window models: 91.6 GB;
- reserves and fallbacks on disk: about 130 GB (122B, Instruct, D-4bit when downloaded);
- Flash-Next: 111.5 GB at 4-bit, plus bf16 sources.

Retained pilot roots run about 19-38 GB each. So per-window logs (37-53 GB, transient) are what crosses the floor, but
retained weights and archives are what lower the floor. **Offload already addresses the latter**: the PR #665 runbook
and Ed's 11-06 retention ruling call for an SSD copy plus a server-confirmed iCloud copy, then local delete. With the
non-window weights and pilots 4-10 moved off, free space should reach about 200+ GB **(estimate)**. That is enough for
any window's 53 GB. Log volume during a window is then not the pressure, and A's main benefit disappears.

## 5. Options, ranked

### Option B (recommended): always attached, nothing written during windows

- All window paths stay internal: runs, backups, custody, `TMPDIR`. This is `log_mode: "internal"`.
- After the desk, bundles move to `JW-EXT` with the offload runbook, which then deletes locally once the SSD copy and
  the iCloud copy are verified.
- No SSD writes start within the quiet period before t0 (default 30 min; the qualification sets it from the measured
  sleep transition).

Risks:
1. **Presence offset.** Absorbed by intercepts, the window reference and G0. Bounded by Q1.
2. **The drive sleeps or wakes mid-window.** PSTR/PDTR are diagnostic candidates for the transition; GPU rail and
   daemon traces are checked too because the channel attribution is not established from public documentation.
   The mid-window presence check uses `stat` only, so it does not wake the drive.
3. **Disconnect mid-window.** Nothing is lost. A remount triggers trim, fsck and diskarbitration, so members
   overlapping the event are flagged and excluded, and the window continues.
4. **Sleep/wake between windows re-enumerates the device.** Some USB4 enclosures fail to remount after wake. The arm
   check then refuses (allowlisted volume absent), and Ed replugs: the same cost as C, but rarer.
5. **Borrowed hardware.** Returning the drive mid-series is a configuration break (amendment A3).
6. **Configuration identity.** The anchor K-session bridge to pilots 4-9 changes. That bridge is already print-only,
   because the new stand changes it anyway (FINAL-DESIGN risk 9).

### Option A-lite: attached; backup copies to the SSD between members only

- `log_mode: "backup"`. The primary bundle stays internal.
- `RouteGuard` sends the backups internal for the rest of the window if the volume drops.
- Halves the in-window internal footprint (18.6-26.4 GB saved).
- Adds a 0.6-1.1 GB burst per member in unowned time, a few seconds at USB4 speeds into the SN7100's SLC cache.
- Needs Q2 and Q3 too. Worth it only if the disk still binds after the offloads.

### Option A: attached; runs root on the SSD

- `log_mode: "direct"`. The primary custody copy sits on borrowed, removable hardware.
- In-episode writes (the sidecar) go over USB4.
- Saves 37-53 GB per window.
- **Not recommended.** Its only extra benefit over A-lite is space that the offloads already provide. Its extra risks:
  - a drop mid-member corrupts or splits the primary bundle;
  - the custody tooling (`harvest`, `check_runs_roots`) assumes one runs-root tree;
  - DC-boundary prints become drive-dependent.

### Option C (status quo): attach by day, eject and unplug before every window

- No measurement risk.
- Costs about 2 Ed actions per window (about 16 over the series) and a missed-eject refusal risk. A refused arm can
  cost a 12-16 h window slot.
- **Remains mandatory for BYTES-type DC-boundary work** (PDTR, KM003C, whole-machine), where the drive's 1-8 W is in
  the channel itself.

### Failure modes common to A and B, with handling

| Event | Detection | Handling |
|---|---|---|
| Enclosure disconnect mid-window | `RouteGuard` stat (device changed or unmounted); kernel log; PSTR step | journal `external_volume.lost`; writes internal for the rest of the window; members overlapping the event plus 600 s are flagged `external_volume.event` and excluded |
| USB4 low-power entry and exit | PSTR steps at fixed delays after the last access | quiet period before t0; under B nothing accesses the drive in the window |
| macOS sleep/wake between windows | arm check (absent or UUID mismatch) | refuse; Ed replugs; arm again |
| Spotlight/TM re-enabled by an OS update | arm check (mdutil, tmutil) | refuse |
| Second external device plugged | census | refuse (allowlist) |

---

## 6. Hardware qualification protocol (Saturday 11-07, by day, nothing armed, non-claim)

**Who and when.**
- Ed unplugs twice and replugs twice (A-D-A-D-A). The magistrate or lead runs everything else.
- Run it after the volume is prepared (`scripts/align_external_volume.py prepare-plan --device diskN`, shown to Ed
  before any erase) and before R1.
- R1 must then run in the configuration the verdict adopts, because R1's idle soak and step tests fill slots S1-S9
  under that configuration.
- It cannot ride inside R1: R1 has to be quiet, and D is blocked (R0 NLL failure, item 182). The 30B is also the
  binding cell (smallest s_r).

**Design (corrected default plan, 125 segments, about 6.8 h).**
- **Lead design decision (laptop lead, 2026-11-06):** adopt A-D-A-D-A with 6 idle and 6 decode pairs per block
  (125 segments, about 6.8 h, up from 87 segments and about 4.7 h). The lead verified Sol's pseudoreplication
  finding independently. In a 400-seed Monte Carlo (decode block shock SD 50 mW, segment SD 20 mW), the old
  segment-level fit on A-D-A gave a 90 % interval covering the truth 39-41 % of the time and PASSed a true 0.10 W
  presence effect (margin ±63 mW) 14.75 % of the time; the block-mean fit on A-D-A-D-A covered about 90 % and PASSed it
  1.0 % of the time. The CLI and `plan()` share the same defaults (`DEFAULT_BLOCKS`, `DEFAULT_IDLE_PAIRS`).
- `python3 scripts/align_ssd_qualification.py plan --out plan.json` gives five physical blocks:
  **attached → detached → attached → detached → attached**. The former three-block default was invalid
  for an uncertainty interval: after fitting intercept, linear drift, and presence to three block means it had zero
  residual degrees of freedom. Treating the repeated segments as independent presence assignments was pseudoreplication.
- Each block has:
  - a 600 s settle;
  - 6 idle pairs and 6 decode pairs of 120 s segments with 60 s gaps, in ABBA order (linear drift cancels within each
    load level).
- Pair conditions:
  - **Attached blocks: quiet vs write.** Write segments replay the window write pattern onto `JW-EXT`: the sidecar
    and monitor streams, plus a worst-case 52 kB at 10 Hz powermetrics-sized stream.
  - **Detached blocks: quiet vs write-to-internal.** This is the status-quo control, print only.
- After each write segment, a teardown burst (2 × 1.11 GB with fsync, one D member's bundle plus its backup) runs in
  the gap.
- **Decode** is fixed work: `scripts/align_ssd_fixed_decode.py --model <30B dir, internal>`, a greedy 4,096-token
  decode with no EOS stop, stamped around the decode only.
- A shorter three-block plan may still be used for debugging, but Q1 is mechanically INCONCLUSIVE and cannot authorize
  any always-attached option.

**Captures (all on the internal disk).**
- One continuous `sudo powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal --format plist`
  over the whole session, so a constant anchor offset cancels.
- From the runner:
  - SMC PSTR, PDTR, B0AC and B0AV at 1 Hz, plus `--smc-extra-key` for the S_slow (heatsink-class) key. If R1 has not
    classified it yet, use the R0 enumeration's candidate.
  - Metadata-daemon CPU per segment from `ps`.
  - Arm-check verdicts at start and end.
  - A presence check after every attached segment.
- Optional: `sudo fs_usage -w -f diskio` during two decode segments, to confirm no SSD reads during decode.

**What decides.** Mean GPU-rail power over each segment's steady core (5 s guards), from powermetrics `gpu_energy`
(`extract`). `evaluate` prints:

| Criterion | Estimate | Margin (30B, s_r,min = 19 J, T_ep = 234.5 s) | Why this margin |
|---|---|---|---|
| **Q1 presence (decode)** | attached − detached quiet decode GPU power; OLS on physical-block means with linear drift; df = blocks − 3 (2 by default) | ±0.25 % of decode power (≈ ±63 mW at 25 W) | the U4 point bar: presence must not move the cross-window frame. A constant offset within the series is absorbed anyway |
| **Q2 write effect (idle)** | paired write − quiet, attached blocks, idle | ±0.05·s_r,min/T_ep = **±4.1 mW** (D: ±5.1 mW) | per-episode bias ≤ 0.05 s_r shifts scores by ≤ 0.05 against thresholds of 2.5-7.1 s_r; the 30B MDE moves ≤ 1.5 tokens |
| **Q3 write effect (decode)** | same, under decode | ±0.30·s_r,min/T_ep = **±24 mW** (D: ±30 mW) | a bar on the **mean** in-episode write effect only. Q3 is a t interval on the mean of paired write − quiet differences, so it does not bound added variance and does not by itself bound s_r or MDE inflation; a variability criterion is needed before A/A-lite can be licensed. Matters only for A/A-lite: B does no in-window writes |
| **Q5 operational** | journal | all of: arm check PASS at start and end; 0 volume losses; 0 attached segments with metadata-daemon CPU > 0.05 CPU-s/s; 0 idle segments with \|B0AC\| > 200 mA; \|S_slow presence offset\| ≤ 0.5 °C (half the δ band) | missing evidence fails |

Each criterion is PASS, FAIL or INCONCLUSIVE:
- **PASS:** the 90 % interval lies inside the margin.
- **FAIL:** the point estimate is outside the margin.
- **INCONCLUSIVE:** otherwise.

`strongest_option_allowed` is mechanical:
- **B:** Q1 and Q5 PASS.
- **C:** anything else.
- **A / A-lite:** not available from `evaluate`. Q2 and Q3 bound only the mean write effect, so A/A-lite also need a
  write-variability criterion that does not exist yet. `write_criteria_pass_print_only` reports whether Q2 and Q3 both
  passed.

A FAIL or INCONCLUSIVE in Q2 or Q3 does not block B, because B writes nothing in windows.

Q1 returns INCONCLUSIVE (fail closed) when fewer than four blocks have usable quiet decode segments, when any block
kept fewer than half the quiet segments of the fullest block, a block with none counting as 0 (the equal-weight block-mean fit is then not valid), or
when the residual df is 0. All rows use one time basis: epoch stamps if every row has one, else the planned ordinal
clock. A missing S_slow reading in any quiet idle segment fails Q5.

**Expected precision (guesses, to be replaced by the data).**
- Idle: pair-difference SD about 3 mW, 18 attached-block pairs, so a nominal independent-pair 90 % half-width of
  about 1.2 mW against 4.1 mW.
- Decode: pair-difference SD about 0.11 % × 25 W ≈ 28 mW (the 30B identical-work pair SD as a fraction), 18
  attached-block pairs, so a nominal independent-pair half-width of about ±12 mW against 24 mW.
- Presence precision comes from five physical block means (df 2), not from the number of segments. It cannot be
  forecast from the segment pair SD without an assumption about block shocks.
- Planning simulation (lead, 400 seeds, no true presence effect, segment SD 20 mW): Q1 PASSes about 99 % of the
  time with block-to-block decode shocks of 5 mW SD, 88 % at 10 mW, 51 % at 20 mW, 25 % at 30 mW and 7.5 % at
  50 mW. A Q1 PASS therefore needs block-level decode power to repeat within roughly 10-20 mW (0.04-0.08 % of
  25 W); larger block scatter gives INCONCLUSIVE, which leaves Option C.
- If decode comes out INCONCLUSIVE, the extended plan or more decode pairs are the remedy; never a looser margin.

**Also recorded, print only.**
- PSTR and PDTR presence offset (expected +1 to +6 W) and the time from last access to the drive's low-power entry.
  This sets the amendment's quiet period.
- The internal-write control effects.
- Per-block nonlinearity of drift.
- Burst sizes and durations.

**Then.**
1. The record goes to `docs/align/v4/qualification/<date>/`: `plan.json`, journal, `rows.json`, `verdict.json` and a
   NOTE.
2. The council (window design council: Opus 5.5 xhigh, Sol 6.1 xhigh, Fable 5.1; Opus final) reads it with the draft
   amendment.
3. Ed decides adoption and confirms the drive can stay for the series.

## 7. Software prepared (default OFF, fail-closed)

| File | What it does |
|---|---|
| `joulewise/align/apple/external_volume.py` | Config validation: statuses `off` (default) / `qualification` / `active`; one upper-case UUID; mount point `/Volumes/<name>`; `log_mode` `internal` / `backup` / `direct`; unknown keys refuse.<br>Mount census from `/sbin/mount` + `diskutil info -plist`: network shares and disk images count as external; unreadable means refuse.<br>`arm_check`: `off` refuses any external volume, which is today's rule, now mechanical. Non-off refuses anything but the allowlisted UUID, and the allowlisted one unless it is APFS, external-physical, writable, ownership on, Spotlight indexing disabled (`mdutil -s`), Time Machine-excluded (`tmutil isexcluded`), with `.fseventsd/no_log` present, and at the configured mount point. `claim_eligible` only in `active`.<br>`route`: custody and `TMPDIR` are always internal; any refusal routes everything internal with the reason.<br>`RouteGuard`: a stat-only mid-window check; once the volume is lost, writes stay internal for the rest of the window; one fsynced journal line.<br>`prepare_plan`: prints only. Refuses disk0-disk3 and malformed identifiers; the erase line is commented out and gated on showing Ed the contents. |
| `scripts/align_external_volume.py` | CLI: `census`, `arm-check` (exit 0 PASS, 3 REFUSE), `route`, `prepare-plan` |
| `configs/align/v4/external_log_volume.json` | the committed config: `status: "off"` |
| `configs/align/v4/external_log_volume.qualification.example.json` | the Saturday template (placeholder UUID; fill from `diskutil info`) |
| `joulewise/align/apple/ssd_qualification.py` | `plan` (ABBA, block balance), `PatternWriter` (fixed cadence, no drift), `teardown_burst`, `extract` (overlap-weighted steady-core rail power using the existing powermetrics parser, unchanged), `presence_offset`, `paired_write_effect`, `evaluate` (Q1-Q3 and Q5, option; Q4 is not defined), `summarize_ops`, `run_session` (journal on internal, 1 Hz SMC through `joulewise.hazards.smc.Reader` unchanged, `ps`-based metadata-daemon CPU) |
| `scripts/align_ssd_qualification.py` | CLI: `plan`, `run`, `extract`, `evaluate`, `write-pattern` |
| `scripts/align_ssd_fixed_decode.py` | fixed-work greedy decode (mlx-lm `generate_step`, no EOS stop), JSON stamps |
| `tests/align/test_external_volume.py`, `tests/align/test_ssd_qualification.py` | 41 tests with fake runners and synthetic worlds; planted effects above each margin are caught; noisy data never PASS |

**Not wired yet.** Wiring needs the amendment:
- the magistrate's arm sequence;
- `launch_align_r0.py preflight` on main;
- the v4 session `prepare`, which would pass `route()`'s `runs_parent` and backups to `plan_inputs.build`.

One step is independent of the amendment: running `scripts/align_external_volume.py arm-check` with the committed
`off` config at every arm turns today's written rule ("no external volume mounted") into a mechanical refusal. The lead
could wire that now.

Pinned files are untouched: hazards, the b5 driver and harvest, powermetrics, `smc.py`, `run_campaign.py`.
`tests/hazards/test_refusal_allowlist` and `tests/align/test_measurement_core_boundary` pass.

## 8. Open questions for the council and Ed

1. Ed: can the borrowed drive stay attached for the whole v4 series (W1 through D3/N4, about 1-2 weeks)? If not, use C.
2. Council: are Q1-Q3's fractions (0.25 % U4 bar; 0.05 s_r bias; 0.3 s_r added SD) the right bars? They are scaled to
   the 30B, the cell with the smallest s_r.
3. Council: should the mechanical `off`-status arm check be wired now, independent of the amendment?
4. Lead: the offload runbook (PR #665) must target `JW-EXT` by UUID and finish before the quiet period. Its second
   copy stays the iCloud server-confirmed one. Data whose only second copy is on the borrowed drive is flagged before
   the drive is returned (memory: external SSD).

Sources (specifications):
- [Tom's Hardware SN7100 review](https://www.tomshardware.com/pc-components/ssds/wd-black-sn7100-ssd-review)
- [Newegg SN7100 2 TB spec](https://www.newegg.ca/Western-Digital-2TB-SN7100-NVMe/p/N82E16820250275)
- [ssdwiki SN7100](https://www.ssdwiki.com/m-2-pci-express/wd-black-sn7100/)
- [Framework forum, SN770/SN7100 idle](https://community.frame.work/t/sn770-sn7100-ssd-idle-power-draw/70086)
- [SmartHDD SN7100 2 TB](https://smarthdd.com/database/WD_BLACK-SN7100-2TB/7615M0WD)
- [MacRumors: OWC Express 1M2 vs Maiwo (idle 5.5-6 W, writes 7.5-8 W)](https://forums.macrumors.com/threads/owc-express-1m2-versus-maiwo-40gbps-m-2-nvme.2441898/page-2)
- [MacRumors: Thunderbolt/USB4 NVMe enclosures (ASM2464PD idle and sleep draw)](https://forums.macrumors.com/threads/thunderbolt-3-m-2-nvme-ssd-enclosures.2027925/page-85)

The enclosure figures are user wall-meter anecdotes, not OWC specifications. The qualification's PSTR and PDTR prints
replace them.
