# Permanent external SSD: agreement and signable lead ruling SSD-P1

2026-11-08, revision 2. Opus 5.5 cold reviewer, branch `align/2026-11-08-ssd-permanent-agreement`.
**Advisory to the lead until signed. Nothing here is adopted, measured or wired.**
- Inputs: the Sol-1 and Sol-2 seats (`align/2026-11-08-ssd-permanent-sol1`, docs `ec20d5422`; `-sol2`, docs
  `57f224549`), both cut from `align/2026-11-08-v4-r11` @ `c3796bf49`.
- Reviews of revision 1 (`58fb53c30`), both SIGN_WITH_CHANGES: `align/2026-11-08-ssd-p1-review-sol1` @ `584141461`
  and `-sol2` @ `f5fbe0d5f`. Their findings are dispositioned in §2.
- Authority: `origin/main:RUN_STATE.md` @ `ae60ae22c`, items 181, 210, 212 R11-3, 213, 214 (R12), 215, 216 and
  217 (B3 is now **fixed 8 calibration windows**), plus Ed 2026-11-07 ~23:10: permanent drive "at nearly any cost".
- No restricted path, sealed result or hardware was touched. Every macOS or device mechanism named here is
  general knowledge, **unverified on this MBP** until the native gate in §4.4 that tests it.

## 0. The ruling in brief

1. **What changes:** v4 is declared a **storage-equipped configuration**. The borrowed SN7100/OWC is permanently
   attached in mode **B-unmount**.
2. **What it costs:** no bare-MBP or drive-free equivalence claim; absent/present GPU Q1 is retired as a different
   question. This is a scoped supersession of item 214's "no SSD-qualification shortcuts", which needs a one-line
   confirmation from Ed.
3. **GPU estimand unchanged:** every v4 GPU input (R1-S, W1, the 8 calibration windows, test) comes from that one
   configuration.
4. **DC-in:** stays secondary in v4. It gets an achievable idle stability check (DCS-1) that sets its label, not a
   veto. The v5 primary DC endpoint stays an open hard gate, qualified on the final hardware.
5. **Bridge:** R1 is re-run in full with the drive attached (**R1-S**). This re-derives every configuration-sensitive
   output and is also the full-length endurance run.
6. **Evidence:** I/O counters and logs are evidence of no host block I/O and of device continuity. They are never
   proof of zero wake or constant power.
7. **Outcomes:** ARM-SSD has PASS, REFUSE and UNAVAILABLE outcomes. SSD events are classified under fixed-8 B3 as
   IO, STATE, UNVERIFIED or a configuration break.
8. **Cost:** ~10.3-13.3 MBP h of qualification plus R1-S (15.6 h nominal, at least 18.7 h with one batch encounter).
   Ed spends ~45 min once, then zero actions per window.

## 1. Where the two design seats agree and disagree (from revision 1, resolutions updated)

| Topic | Sol-1 / Sol-2 | Resolution |
|---|---|---|
| Mode order | Both: B > B-unmount > B-cut; A rejected | **B-unmount > B > B-cut**; A rejected. Reviews concur (both "support B-unmount first"). |
| Ed per window | Both zero | Agreed. |
| DC criterion | Both: +/-0.10 J mean, <= 0.60 J added-SD UCB (QDC) as an adoption veto | Not a v4 veto (DC is secondary): DCS-1 sets the v4 DC label. A v5-specific QDC-type gate on the final hardware stays open (§4.5). |
| `p*T` | Both: constant watts are not constant joules | Agreed. Trusted baseline subtraction cancels `p*T` only under its stationarity/precision assumptions; an intercept never does. |
| Qualification shape | Sol-1 8.5 h/candidate; Sol-2 6.833 h + 16.5 h endurance | One mode, within-configuration gates G1-G6. R1-S doubles as endurance (§4.4). |
| R1 -> W1 | Sol-1 bridge 4-8 h; Sol-2 full R1 repeat | **Full R1-S** (§4.6). Revision 1's 2.5 h bridge is withdrawn. |
| Break / arm rule / D-043 | Both: allowlist one device; break holds arms; Sol-2 adds D-043 closure | Adopted, with explicit outcomes (§4.7, §4.8). |
| Purchase | Both: 4 TB, fanless | Kept with the class in §4.10; qualification, not chipset, certifies power. |

## 2. Disposition of every review finding

| Finding | Disposition |
|---|---|
| S1-H1 / S2-H2: permanence changes the population; silence does not certify stability; item 214 supersession must be explicit | **Accepted.** Declared storage-equipped v4 with no bare-MBP claim (§4.1). Item 214 is superseded explicitly and narrowly, with Ed's confirmation. GPU reference/thermal rules, negative controls and configuration-matched fits are untouched. DCS-1 added (§4.5). v5 DC is a named hard gate. |
| S2-H1 / S1-M1: the factors are right, "impossible" is wrong | **Accepted.** Restated as a precision concern: under an assumed 5 mW block SD the five-block design is ~16x (120 s) to ~240x (1,800 s) short of +/-0.10 J. No power at that resolution has been demonstrated, and a nonzero-noise passing example exists. The "250-57,000x blocks" heuristic is withdrawn. Q1 is retired as a question, not on power grounds. |
| S2-H3 / S1-H3: counters/logs are not zero-wake proof; ARM-SSD needs qualified evidence and UNAVAILABLE | **Accepted.** §4.3 states what each source can and cannot certify. The collectors are qualified with positive controls in G4. ARM-SSD has an UNAVAILABLE outcome. The baseline snapshot is taken after counter quiescence. "Zero-overhead, zero-wake" is withdrawn. |
| S1-H2 / S2-H4: the lean bridge is insufficient; Q5 is dropped | **Accepted.** R1-S re-derives all R1 outputs; only identity/semantic outputs transfer by digest (§4.6). The Q5 operational checks (daemon CPU, battery float + R11 battery rules, slow temperature) are kept in G6/ARM-SSD. |
| S1-H4 / S2-H5: SSD_EVENT vs amended B3; lost window vs break | **Accepted.** §4.8 sorts events into four classes against fixed-8 (item 217) and the zero-capture rule (item 216). It covers role-specific W1 and test handling and the no-pooling-across-break rule, and puts the loss mechanism in the attrition report and the pre-W1 simulation. |
| S1-M2 / S2-M1: inconsistent time bill; the 23:00 claim; contradictions in P3 | **Accepted.** §4.9 is a conditional bill that includes Q. R1 timing: the magistrate schedules after authenticated R1 terminal completion; no earliest finish is claimed. |
| S1-M3: P1-P5 not deterministic; retry mismatch; B and B-cut as silent fallbacks | **Accepted.** G1-G6 have PASS/FAIL/UNAVAILABLE outcomes and fallback rules F1-F3. There is one retry policy. Alternative modes require their own full qualification. |
| S1-M4 / S2-M2: purchase claims overreach | **Accepted.** Class kept as a preference. Chipset and DRAM certify nothing; the exact unit is qualified. The HMB claim is narrowed. An externally powered drive moves energy outside the KM003C boundary and must be disclosed. |
| S1-L1 / S2-L1: `min()` direction misdescribed | **Accepted; revision 1 L-2 was wrong.** `min(2 J, SD)` tightens only below 2 J. Choosing an absolute versus relative budget is a v5 design choice. |
| S2-H2 note: reviews must be "two Sol seats per Opus product", not "Sol + Opus" | **Accepted** (§4.4 step A). |
| Fact audits (fstab `noauto`, accessory approval, `disksleep`, re-enumeration, IORegistry counters, unified log, UAS/serial) | **Accepted as unverified-native.** Each is tested in G1/G2/G4 or treated as unknown. The "3-5 W for 10 min" wake is an anecdotal scenario only. |

## 3. Revision-1 findings that stand (abridged)

- **Mode (stands).** A mounted volume is reachable by any process, so wake-by-access is plausible and unbounded
  ahead of time. An unmounted one has no filesystem consumers. The current mount-only census already passes
  under B-unmount; what is new is the device census.
- **Automount (stands, scoped).** Re-enumeration can auto-mount. Mitigate with fstab UUID `noauto` entries; this
  is an automount preference, not access control. Test it in G2.
- **Accessory approval (stands).** A locked Mac can hold a reconnecting accessory, which also weighs against B-cut
  re-enumerating every window. Ed owns that setting.
- **Precision (restated).** QDC's resolution was never shown achievable at five blocks. It moves to v5 design.
- **Purchase (restated).** The bridge class likely dominates enclosure power, and USB4 speed buys no turnaround.

## 4. SSD-P1 (signable text)

### 4.1 Scope, claim and authority

- **Configuration.** v4 runs on one storage-equipped configuration from R1-S through every W1, calibration and
  test window. The binding record is the enrollment receipt (device, enclosure, firmware, cable, port, placement
  >= 30 cm from intake and exhaust, mode).
- **Claims.** No v4 claim is made about a bare MBP, and nothing is pooled with drive-free data. Drive-free R0/R1
  stay immutable as the record of their own configuration.
- **What is retired.** Absent/present GPU Q1, the five-block runner and QDC are retired as v4 adoption gates. R1
  vs R1-S is printed descriptively.
- **Item 214.** Its rejection of SSD-qualification shortcuts is superseded only for this purpose. That rejection
  guarded presence equivalence, which this configuration no longer asks.
- **Sign-off.** The lead rules; Ed confirms one line ("v4 is storage-equipped; no bare-MBP claim"), per item 181
  (research-plan changes are his). Adoption closes D-043 supersession: FINAL-DESIGN physical setup, the old study
  and amendment, item 187's kit and its runbooks.
- **v4 GPU estimand unchanged.** The registered residual stays GPU energy. All reference, thermal, negative-control
  and fit rules apply as written, with their inputs re-derived in R1-S.
- **v4 DC.** Gross and baseline-treated diagnostics, coverage, clock, custody and battery flags are kept. The label
  comes from DCS-1 (§4.5). No SSD-negligibility claim is made.
- **v5 DC primary: open hard gate.** Before any primary use, qualify on the final purchased hardware the frozen
  baseline/integration operator, duration/load/history range, repeated replays, battery handling, meter
  uncertainty, calibration and held-out operating characteristics. Neither DCS-1 nor clean v4 windows count toward
  it.

### 4.2 Mode and fallbacks

- **B-unmount is the only adopted mode.** All window I/O stays internal.
- **Between windows:** finalize, then mount by UUID, offload and verify, unmount, wait for quiescence, wait Q.
- **B (mounted, no I/O) and B-cut (switched hub)** are alternatives, not runtime fallbacks. Each needs its own G1-G6
  qualification and a prospective adoption before use.
- **A is rejected.**
- If the adopted mode fails in service, arms hold (§4.8). The mode is never silently switched.

### 4.3 What the device evidence can and cannot certify

| Source | Can certify, once qualified | Cannot certify |
|---|---|---|
| Block-storage `Statistics` counters on the enrolled media's driver node, bound to its physical ancestry | No host-issued block reads or writes through that node between two snapshots | Autonomous drive or bridge power-state changes, link power states, management commands, thermal change, zero wake |
| IORegistry entry IDs of the device, media and driver nodes | Object continuity: an observed change proves re-enumeration | Every reset or retrain; some may preserve a node |
| Unified-log query after finalize (predicate validated against induced events) | Corroboration of mount, unmount, appear and disappear events | Absence: an empty result is not a clean certificate |
| KM003C DC-in (+ SMC PSTR/PDTR) | Idle-state power stability to DCS-1's resolution | Load-time drive power, separate from host load |

- **Fail closed:** missing, malformed, reset, non-monotone or stale counters, unknown nodes, and failed or truncated
  log queries are **UNAVAILABLE**, never clean.
- **Wake effects:** reads use registry properties and the post-hoc log only, with no in-window poller. Whether a
  read wakes the device is itself tested in G4.

### 4.4 Qualification sequence and the gate contract

**A. On the Air, no MBP time.**
- Implement the B-unmount hooks, the physical census, the counter, entry-ID and log collectors, ARM-SSD and the
  manifest fields in `joulewise/align/apple/external_volume.py`, plus the magistrate wiring.
- Add synthetic fault tests: busy unmount, missing node, counter reset, empty or failed log, extra device, identity
  mismatch, remount refusal while a run may be alive.
- Two independent Sol seats review; the lead verifies; the magistrate installs.

**B. On the MBP.** The magistrate schedules this after authenticated R1 terminal completion, in a clean,
agent-free interval. Durations are in §4.9.

| Step | What happens |
|---|---|
| B0 | Install and dry-run the collectors, drive absent. |
| B1 | **Absent idle reference**, 2.0 h: display asleep, magistrate idle, KM003C + SMC + powermetrics. |
| B2 | **Ed, about 45 min**, detailed below. |
| B3 | **Cycles 1-3** (automated): mount by UUID, then a 26.4 GB copy, hash-verified, then flush, then `unmountDisk`. Then observe for 90 min. Cycles 1-2 set L, Q is frozen, cycle 3 validates it. Run the open-handle negative test once. |
| B4 | **Plateau** 2.0 h (DCS-1, matched to B1). Then a **positive control**: mount, read 1 GB, unmount. Then re-settle Q. |
| B5 | **R1-S** (§4.6), with ARM-SSD before it and its post-finalize checks after. |

Ed's step B2:
- Plug in at the fixed port, cable and placement, and approve the accessory. Set the accessory policy.
- `sudo vifs`: add a UUID `noauto` line for every exposed volume.
- `mdutil -i off`, `tmutil addexclusion`, `.fseventsd/no_log`, `.metadata_never_index`.
- Record the `pmset -g` AC profile (sleep must be 0).
- Enroll the identity. Show the contents of the borrowed drive before any erase.
- **Locked-screen replug** for G2.

**Gate contract.** Each gate returns PASS, FAIL or UNAVAILABLE; UNAVAILABLE counts as not passed. **Adoption
requires G1, G2, G3, G4 and G6 all PASS.** G5 sets the DC label; it is not a veto.

| Gate | PASS when (frozen now) |
|---|---|
| **G1 Automation** | Cycles 1-3 complete with no human action. Each mount is verified by every volume UUID. Each copy is hash-verified. After each unmount, every volume of the enrolled hardware is absent from the mount table and the device is present. Timeouts are 60 s for mount and 60 s for unmount. **One retry policy everywhere:** on busy, log the dissenter, wait 30 s, retry once, then REFUSE. Never force. The open-handle test yields REFUSE with the dissenter logged. |
| **G2 Reconnect** | After Ed's locked-screen replug: the device returns within 120 s, no volume mounts within 5 min, and identity re-resolves. The collectors record the entry-ID change and the appear event (positive control). |
| **G3 Settling** | L_i runs from the last counter increment to the start of the first 10 min span whose 60 s medians of DC-in stay within +/-50 mW of the following 20 min median, observed for up to 90 min. Q = max(30 min, 2 x max(L_1, L_2)), rounded up to 5 min, frozen before cycle 3. PASS if Q <= 90 min and L_3 <= Q/2. No plateau in 90 min is FAIL. Q above 45 min is PASS with a disclosed longer turnaround. |
| **G4 Evidence** | Counters are unchanged across the B4 plateau and the B3 settles. The positive control raises read counters by >= 1 GB and the log query returns its mount and unmount events. Snapshot reads cause no counter change and no DC step above 50 mW. Any missing or malformed field is UNAVAILABLE. |
| **G5 DCS-1** | §4.5: STABLE, UNSTABLE or UNAVAILABLE. |
| **G6 R1-S** | R1-S is admitted under the R1 runtime contract's own acceptance rules, and ARM-SSD pre-arm and post-finalize are clean over its whole span. This is the endurance evidence: at least 56,207 s in the qualified state. The Q5 operational checks are retained: metadata-daemon CPU, battery float, the R11 battery rules and slow temperature. |

**Fallbacks.**
- **F1:** a software fault in G1 or G4 is fixed and the gate rerun, with no Ed. A hardware fault in G1 or G2 (no
  exposed identity, unmount unreliable, policy cannot be met) holds adoption; the lead then rules B or B-cut
  qualification, or different hardware.
- **F2:** G3 FAIL or G5 UNSTABLE with a fix wanted means new hardware (low-power enclosure or B-cut hub) and a full
  requalification.
- **F3:** G6 failing for SSD reasons holds; failing for non-SSD reasons follows R1's own redo rules.
- No threshold is loosened after data are seen.

### 4.5 DC-in stability check DCS-1 (v4 label; achievable and meaningful)

**Design.**
- B1 (absent) and the B4 plateau (present, after Q) are each 2.0 h, in the same idle protocol: display asleep, no
  agents, same thermal start rule.
- Statistic per record: the 5 min medians m_k of DC-in power, with a robust linear trend.
- A 5 min block is unavailable if the meter has a gap or an R0-L3 contention flag falls in it. Flags mark data
  unavailable; they never excuse a step.
- More than 20% of blocks unavailable in either record gives UNAVAILABLE.

**STABLE requires all of:**
1. No adjacent-15-min-median step above max(50 mW, 1.5 x the largest such step in B1).
2. |trend| <= max(10 mW/h, 1.5 x |B1 trend|).
3. Detrended range of m_k <= max(100 mW, 1.5 x the B1 range).
4. G4's counters clean over the plateau.

Otherwise the result is UNSTABLE.

**Why it is achievable and what it bounds.** 5 min medians of whole-machine idle power resolve tens of mW. The
assumption is scatter well below 100 mW, unmeasured, which is why the thresholds carry the max(·, 1.5 x absent)
form. The check therefore detects any drive or bridge sleep/wake or state change of about 50 mW or more at idle,
which matters most: the anecdotal wake step is 1-5 W. A missed 50 mW state over an 1,800 s member is 90 J, the
same order as v4's regression residual scale (19-58 J, GPU). So STABLE means the drive adds no idle instability
resolvable beside v4 DC's own noise.

**Limits.** It does **not** bound sub-50 mW effects, load-time drive power, or the 2 J replay scale. That is v5's
gate (§4.1). R1-S's idle segments are printed with the same statistic, descriptively, as longer-span evidence.

**Labels.** STABLE: v4 DC prints are labelled "SSD configuration, idle-stable to DCS-1". UNSTABLE or
UNAVAILABLE: v4 proceeds (G1-G4 and G6 permitting) as **V4_DC_UNQUALIFIED**, with every DC print labelled and the
measured instability disclosed. This is deterministic, not a waiver.

### 4.6 R1 bridge: R1-S, a full R1 in the final configuration

**Transfer matrix.**

| R1 output | Configuration-sensitive? | Treatment |
|---|---|---|
| R0 semantics, model/stack/tokenizer/quantization identity, internal paths | No (bytes and identity) | Transfer by digest check at R1-S start |
| Sensor inventory/classification | Possibly (topology) | Re-derived in R1-S; a changed key set escalates to an R0 re-check |
| Soak reference R, S5 bands, S1-S4/S7 | Yes (host-link heat, supply) | Re-derived |
| 30B and D steps: rate, t_decline, S8/S9, B_D, I_D, T_dead, N_chunk, G_turn, tails | Yes | Re-derived |
| A-B-A legs (High Power adoption) | Yes | Re-derived |
| Gated D replays, X-G, U5, G0 waits/censoring, G1/H, S6 duty, contrast caps, L1/1(f) budget fit | Yes | Re-derived, with all dependent slots, caps, kit and receipts regenerated before W1 |
| Battery drain/float, meter coverage, clock, custody | Yes | Re-derived; the R11-3 meter checks apply |

**Running it.**
- R1-S uses the unchanged R1 driver and plan. Size `window_max_s` from items 215 and 216: at least 67,371 s with no
  redo, at least 96,427 s with a redo, plus bracket, close and harvest.
- The magistrate runs ARM-SSD before it and the post-finalize checks after it, without modifying the frozen R1 lane.

**Outputs.**
- R1-S is authoritative for W1.
- Drive-free R1 vs R1-S is printed per output, descriptively. One run each gives no inference.
- If R1 has **not** armed when SSD-P1 is signed, the magistrate may instead hold R1 until enrollment and run it once
  as R1-S, saving one R1. A running R1 is never touched.

### 4.7 ARM-SSD (replaces "refuse while any external volume is mounted", effective at adoption)

> **ARM-SSD.** Before every arm the magistrate builds a physical storage census from qualified collectors (§4.3).
> **PASS** requires all of: exactly one external storage device present, the enrolled one (identity per the
> receipt, nodes bound to its physical ancestry); every filesystem or LUN it exposes unmounted; no other external,
> network or disk-image mount; and its entry IDs and counters equal to the **quiet receipt**, the snapshot taken
> after verified unmount and counter quiescence. The quiet receipt must also be at least Q old.
> **REFUSE** on any mismatch: missing or extra device, a mounted volume, an identity or entry-ID change, or any
> counter change since the quiet receipt. Restarting Q needs a new verified unmount and quiescence; counters are
> never silently re-baselined.
> **UNAVAILABLE** when any required field is missing, malformed or unqualified, or the census cannot be read. It
> refuses the arm and holds for the magistrate.
> After terminal completion, and before any remount, the magistrate re-reads the nodes and counters and runs the
> validated log query over the protected span (quiet receipt through terminal record). It classifies the window
> per §4.8.
> **Between windows:** finalize, then remount by UUID (only once the run is proven dead), then offload and verify,
> then unmount, then the quiet receipt, then Q. All steps have the G1 timeouts and one retry, then hold. Never
> force-unmount; never write to an empty mount point.
> The KM003C and its logger are instruments, not storage. Zero Ed actions per window.

### 4.8 SSD events under fixed-8 B3 (items 216 and 217)

| Class | Trigger | Window consequence | Series consequence |
|---|---|---|---|
| **SSD_IO** | Counter change in the protected span, enrolled device continuous | Whole window **lost**: no member eligible; the counters cannot localize the I/O | Resume after the lead finds and removes the cause, in the same configuration |
| **SSD_STATE** | Entry-ID change or appear/disappear event; the same enrolled identity returns | Whole window lost | Diagnose first (also on the first occurrence). Resume only after verified restoration of the same configuration. |
| **SSD_UNVERIFIED** | Post-finalize evidence UNAVAILABLE | Whole window lost (conservative) | Hold until the collector is fixed and requalified |
| **CONFIG_BREAK** | Device missing or replaced, identity, firmware or topology changed, or mode changed | Window lost | Hold all arms. A prospective new-segment ruling is needed; no pooling or fit across the break. |

**Roles.**
- **Calibration:** a lost window that captured at least one member **consumes its slot** (item 216); one with zero
  captures does not. Fewer than 39 eligible per pair after 8 gives `insufficient_calibration` (item 217). There is
  no replacement window.
- **W1:** a lost W1 is repeated before any calibration window.
- **Test:** a lost test window is replaced by one appended window in the frozen order, at most one per cohort,
  pending the open test-shape ruling. This must be written into the test rule before W1.

**Selection and reporting.**
- Classification reads device evidence only, never scores or energy.
- SSD losses go into the attrition report, and the pre-W1 simulation adds a whole-window-loss stress case (one SSD
  loss per series) to the fixed-8 FPR check.

### 4.9 Time bill (conditional; Q in hours, 0.5 <= Q <= 1.5)

| Item | MBP hours |
|---|---|
| B0 install/dry-run | 0.25 |
| B1 absent reference | 2.0 |
| B2 Ed (MBP occupied) | 0.75 |
| B3 cycles: 2 x (0.35 copy/verify/transitions + 1.5 observe) + (0.35 + Q) | 4.05 + Q |
| B4 plateau 2.0 + positive control 0.25 + re-settle Q | 2.25 + Q |
| **Qualification subtotal** | **9.3 + 2Q = 10.3-12.3** (13.3 with one G1 rerun) |
| B5 R1-S | 15.61 nominal (no redo, no batch hit); at least 18.71 with one encounter; at least 26.8 with a redo; plus bracket/close/harvest |
| **Total before W1** | **about 26-31 h typical**; up to about 40 h with a redo and a rerun |

- **Ed:** about 45 min once. Add about 15 min only if G2 needs a second replug. Nothing per window.
- **Turnaround after adoption:** remount + offload + verify + unmount + Q + pre-arm, about Q + 0.4 h. With Q = 30 min
  that is about 0.9 h, above R12's 30-45 min target. Disclosed as a cadence cost, not hidden.
- **Cheaper path:** the R1-hold option in §4.6 removes about 16-19 h.

### 4.10 Hardware and purchase

**Which drive when.**
- Confirm **once** that the borrowed SN7100/OWC can stay for the whole v4 series. If yes, v4 runs on it and the
  purchased drive joins at the v4/v5 boundary. It then needs a full G1-G5 requalification and new receipts, plus
  v5's own DC gate.
- If the borrowed drive cannot stay, buy now and run §4.4 on the purchased unit before W1.

**Purchase class.** A preference; availability, prices and SKU details need checking.
- **4 TB.** v5 needs about 1-1.2 TB per copy (unverified forecast). Two directories on one drive are one failure
  domain; the independent second copy stays.
- **Drive:** TLC NVMe with on-board DRAM, not QLC, e.g. the WD Black SN850X or Samsung 990 Pro 4 TB class.
- **Enclosure:** fanless aluminium, bus-powered, USB-C 10 Gb/s, Realtek RTL9210B-class with UAS on macOS. No fan,
  no RGB, no vendor software. Use a short certified cable.

**Limits of the class.** Chipset, DRAM or "low power" claims **certify nothing**: G1-G5 on the exact drive,
enclosure and cable decide. Buy where a return is possible. HMB and sustained-write behaviour depend on the
transport and firmware. 26.4 GB at about 0.8 GB/s is about 33 s of transfer, before hash, flush, mount and Q.

**No hub, no charging dock.** Buy a B-cut hub only under F2. It must prove per-port VBUS removal, no backfeed,
autonomous recovery and logger independence. A dock or hub that charges the Mac bypasses the KM003C. An externally
powered drive moves its energy outside the KM003C boundary; that is disclosed, not hidden.

### 4.11 What the seats' drafts become

**Kept as the amendment's base:**
- Sol-1's A2/A3/A6 state machine and manifest.
- Sol-2's A1 (power path, D-043) and A3 (`p*T`).

**Replaced:**
- Mode order by §4.2.
- A4/QDC by §4.4-4.5, with the v5 gate in §4.1.
- The bridge and endurance by §4.6.
- The fault rules by §4.7-4.8.
- Purchase by §4.10.

**Retired.** The five-block kit stays only if the v5 design asks for a presence contrast; otherwise it is retired
in `CANONICAL.md` at adoption. Flash-Next tests on the drive count as between-window I/O and must end before the
quiet receipt.
