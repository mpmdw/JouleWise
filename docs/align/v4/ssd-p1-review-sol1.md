# SSD-P1 agreement review — Sol seat 1

2026-11-08 task date. Branch `align/2026-11-08-ssd-p1-review-sol1`.
**Verdict: SIGN_WITH_CHANGES. Advisory only; SSD-P1 is not adopted or qualified.**

Support permanent attachment, automatic B-unmount as the first candidate,
internal storage throughout each window, and zero routine Ed actions. Do not
sign the current admission/evidence language. Constant hardware does not prove
constant power, the shortened bridge does not establish every reused R1 output,
and R12's count rule does not itself authorize a new exclusion. These are
repairable without restoring the proposed subjoule QDC gate or requiring Ed
to unplug between windows.

## Evidence and authority

Reviewed `SSD-PERMANENT-AGREEMENT.md` at `58fb53c30`, both seats' study and
amendment Git objects on `origin/align/2026-11-08-ssd-permanent-sol{1,2}`,
and local `origin/main:RUN_STATE.md` at
`c07b388e90d9f085e6428a1e0d96b0361ff417f0`, items 181, 210, 212–215
(211 for the scheduling claim). Also checked:

- [Protocol v4, ruling 20](../pilot_protocol_v4.md),
  [R1 runtime contract](../r1_runtime_contract.md), and
  [KM003C channel/fit contract](../squeeze/KM003C-ALIGN.md).
- `55029b860:docs/perf/2026-11-08-latency-synthesis.md`, table item 22 and
  §2; `6eb1ff5be:docs/align/council-2026-11-05/FINAL-DESIGN.md`;
  [D-018/D-043](../../decision_log.md).
- [Block-mean inference](../../../joulewise/align/apple/ssd_qualification.py)
  and [current volume census](../../../joulewise/align/apple/external_volume.py).

Git refs are local snapshots, not a network freshness claim. No hardware,
measurement files, sealed outcomes or out-of-clone user paths were inspected.
macOS/product statements below distinguish general knowledge from validation.

## Findings requiring changes

### H1 — HIGH: permanence and event silence do not establish endpoint stability

Agreement H-3/§§3.1–3.2 overstates what replaces Q1/QDC. A fixed device can
have autonomous controller/flash activity, bridge/link power changes, thermal
effects or battery-mediated input changes without host read/write increments
or a mount/re-enumeration event. Workload-dependent host effects can recur
with identical device identity. Thus device evidence does not answer whether
the drive's **power state ever changes** inside a window.

P4 is an operational screen, not an energy-error bound. With S = 4 W, a
4 W excursion lasting 60 s contributes 240 J but misses the five-minute rule.
A coherent 20 mW difference over 1,800 s contributes 36 J without approaching
the 0.1 W plateau tolerance. These are synthetic counterexamples, not observed
SSD behavior. P4 also needs a defined outcome when S is unresolvable, zero or
confounded by mount/host/battery effects. One observed wake amplitude is not a
lower bound on every future state transition.

**Required disposition:** explicitly adopt a storage-equipped configuration
for the whole v4 series. Absence equivalence may be retired as a different
scientific question, with no claim of bare-MBP or historical equivalence.
Keep GPU calibration, reference-state/thermal rules, negative controls and
configuration-matched fits intact; qualify their operation in the final mode.
The primary variable remains GPU energy, but the apparatus qualification loses
a guarantee unless this transfer is demonstrated. A constant watt contribution
does not cancel from unequal-duration energy totals: it contributes p*T.
Trusted baseline subtraction cancels it only under its stationarity and
baseline-precision assumptions; a residual intercept alone does not.

For v4 DC, preserve gross and baseline-treated diagnostics, flags, coverage,
clock, custody and battery evidence. It is reasonable to remove the proposed
±0.10/0.60 J **v4 adoption** veto because DC is secondary; label remaining
instability and avoid an SSD-negligibility claim. For v5, make a separately
qualified primary DC endpoint an explicit outstanding hard gate: final
baseline/integration operator, actual duration/load/history range, repeated
replays, uncertainty, battery handling, calibration and held-out operating
characteristics. Endpoint SD is relevant but cannot be the sole adjustable
tolerance: a noisier device must not qualify merely by inflating its own budget.
Neither a two-hour idle screen nor a clean W1 alone establishes that gate.

R12 item 214 explicitly rejected SSD shortcuts; the synthesis says three
blocks lose residual df. Dropping the contrast altogether is a new prospective
design/admission ruling, not a statistical cure for lost df. Name that
supersession and its replacement evidence, and close the losing surfaces under
D-043. SSD-P1 currently describes the change as if R12 were unaffected.

### H2 — HIGH: one soak plus one D step cannot establish the stated R1 bridge

Agreement §3.3 retains every setting whose input did not move, but does not
observe enough inputs to decide that. A 30-minute soak and one D load/recovery
step do not reproduce the matched-predecessor D-bank/D-spam replay checks,
X-G/contrast-cap proof, designed start states, G0 waits/censoring, duty/turn
opportunity, or any relevant 30B and adopted power-mode evidence. External
placement at 30 cm does not remove supply headroom, charging, host-link or
thermal-transfer uncertainty. The original Sol-1 bridge explicitly covered
these dependencies; §3.3 is materially smaller, not just faster.

**Required disposition:** retain a bounded bridge rather than automatically
repeating all R1. Make a table of every reused output, original criterion,
configuration sensitivity, new observation or justified invariant, and all
dependent slots/caps/kit receipts. Cover sensor picks/noise/reference bands,
S6/S7 recovery, S8/S9 decline/chunking, throughput, B_D/I_D/T_dead, matched
replay and X-G budget paths, and meter/battery behavior where applicable.
Unobserved is not unchanged. Rerun the affected step and dependent proofs when
transfer is unresolved; use full R1 where a smaller proof is unavailable.
Do not promise a 2.5-hour bridge before this map is executable. Preserve the
drive-free R0/R1 bytes and freeze the final receipts before W1.

### H3 — HIGH: ARM-SSD needs qualified evidence and an unavailable outcome

The enrolled-device/all-volumes-unmounted/Q structure is sound. The current
implementation is mount-based and has no qualified counter/entry-ID/log
receipt; the proposed mechanism is not yet production evidence.

IORegistry cumulative counters are useful for host data I/O, subject to the
actual driver exporting them. They do not cover all management commands or
autonomous device activity. A registry ID describes an object lifetime, not
every link retrain or power transition; choose the device/media/driver nodes
explicitly and bind their ancestry to the enrolled physical device. Default
unified logs are not a proven exhaustive, retained audit. Empty query output
cannot imply no event. Protocol v4 ruling 20 already requires native audit
qualification and treats missing/unqualified coverage as unavailable.

**Required disposition:** before adoption, validate device-specific counters,
their width/reset/monotonic behavior, node mapping, boot identity and the exact
log predicate, privileges, time bounds and retention over the maximum window.
Demonstrate detection of reads/writes, transient mount/unmount, removal and
return, and changed driver/media identity. Include missing fields, malformed
output, truncated/failed log queries and ambiguous coverage as unavailable;
hold the next arm and apply the prospectively registered window disposition.
Filter events to the enrolled device and disallowed storage, not every Disk
Arbitration event on the Mac. Bind raw evidence and code/config digests.

Record the baseline snapshot **after verified unmount and counter quiescence**,
then require unchanged identity/counters through Q, pre-arm and post-finalize.
The current text compares against counters at unmount while allowing them to
settle afterward. Define the protected span through terminal record and query
it before restoration. A restart must prove the run is dead before mounting.
Qualify the exact census/snapshot commands for wake effects; IORegistry reads
usually retrieve kernel properties, but an unconditional "never touches the
device" claim is not established here. Post-finalize log extraction avoids a
new in-window polling process; the OS logging facility still runs. Replace
"zero-overhead, zero-wake" with this bounded, validated claim.

### H4 — HIGH: R12 B3 does not automatically absorb SSD_EVENT losses

Agreement M-5/ARM-SSD treats minimum 6/cap 8 as an existing authorization to
drop an entire window and repeat W1. Item 215 requires prospective order and
roles, final eligibility, both-pair predicates, cap accounting, failure outcome
and simulation of selection/exchangeability. It explicitly says count alone
does not satisfy R13/R14. Six to eight windows cannot guarantee recovery from
arbitrary whole-window losses; calibration and test windows have different
roles. Event likelihood may depend on member load/duration/history even when
the event rule never reads alarm scores. Blinding alone does not prove
exchangeability after this selection.

**Required disposition:** register SSD_EVENT as a new infrastructure continuity
rule with exact event and unavailable-evidence predicates; which fit,
calibration, test and W1 records are affected; whether failed attempts consume
each cap; fixed replacement roles/order; and the insufficient-count outcome.
Include this loss mechanism in the required selection simulation. Retain all
raw records and report attrition. Define when an identical configuration may
resume versus when a new segment/requalification is required. Replacement,
mode/topology change or unresolved identity needs that ruling on the first
occurrence; a blanket "second event requires requalification" cannot license
one configuration change. No automatic pooling across such a break.

### M1 — MED: QDC arithmetic supports a precision concern, not impossibility

The five-block calculation in B-1 is correct **for a presence coefficient**
with equally spaced blocks, independent homoscedastic Gaussian block errors,
and intercept + linear time + presence. With X rows (1, i, 1[i even]),
`(X'X)^-1[p,p] = 5/6`, df = 2, and t(0.95,2) = 2.919986. Therefore
SE = 0.912871*s_b and the 90% half-width is 2.665570*s_b. The χ² two-df
95% upper SD factor is 4.415396, giving an observed-SD limit of 0.135888 J
for a 0.60 J bound under that model.

| Span | ±0.10 J in mean power | Half-width at assumed s_b = 5 mW | Ratio to 0.10 J | Largest observed s_b permitting zero-effect mean PASS |
|---|---:|---:|---:|---:|
| 120 s | 0.833333 mW | 1.599342 J | 15.993 | 0.312629 mW |
| 1,800 s | 0.055556 mW | 23.990130 J | 239.901 | 0.020842 mW |

There is no mathematical lower bound making five-block PASS impossible.
A positive-noise synthetic example with residuals
`5e-6 W * [1,-2,0,2,-1]` orthogonal to X, mean `10 + .001*i` W, has
s_b = 0.011180 mW. At 1,800 s its zero-effect mean half-width is 0.053644 J
and total-residual SD upper bound 0.088858 J: both below the proposed numbers.
This refutes "can only ever return INCONCLUSIVE"; it proves nothing about
native achievable precision or identifiability of **added** SSD variance.

The 5 mW assumption is unverified, and the drafts explicitly call 2 J a GPU
planning scale, not measured DC precision. Their QDC targets uncancelled
error after a prospective baseline/offset operator, not necessarily the raw
presence coefficient. Its inference must be specified before applying this
SE calculation. Added-variance separation needs controls/covariance assumptions;
the χ² example alone does not supply it. A nonzero estimate can also yield a
FAIL rather than INCONCLUSIVE.

The "250–57,000x more blocks" squares current half-width ratios while keeping
the two-df t multiplier fixed. That is not a sample-size derivation. Under an
ideal large balanced independent-block design and s_b = 5 mW, a normal
zero-effect half-width calculation gives roughly 390 and 87,660 **total**
blocks (about 78x and 17,532x five blocks). Neither calculation is a powered
design or a native recommendation. Replace the BLOCKER with: precision is
unestablished and likely costly under the illustrative noise assumption.

### M2 — MED: qualification time and R1 timing are overstated as known

The numbered plan totals **7.5 automated MBP hours**, plus **0.75 h Ed/MBP**
= **8.25 occupied hours**, not 6.5 h: 0.5 + 2.5 + 2 + 2.5 automated.
This excludes the forced wake's duration/tail, failure retries and any bridge
extension. Three cycles already require three hours of settling alone if
Q = 60 min; accepting Q > 60 makes the 2.5-hour cycle allowance impossible.
Overlap needs explicit compatible intervals and cannot be presumed from this
sequential plan. Forty-five minutes of Ed is an allowance, not a demonstrated
upper bound on privileges, approval and replug setup.

H-2 also confuses a required **deadline allowance** with minimum run duration.
Item 215's 67,371 s protects a worst-case batch encounter; item 214 also
recognizes early terminal completion. Neither R0's deadline nor R1's allowance
establishes a 23:00 earliest finish. Keep "after authenticated R1 terminal
completion, scheduled by the magistrate" (item 181); do not touch a running job.
Installation/native qualification does occupy the MBP even if preparation is
on the Air. The automatic no-Ed sequence remains feasible in principle, but
offload/hash + transitions + Q + pre-arm must be measured against 30–45 min.

### M3 — MED: P1–P5 and fallback rules are not a deterministic PASS contract

- P3 both requires Q ≤ 60 min and accepts longer Q. "All required" P3/P4
  then has a v4 override on DC failure, including potentially no plateau.
  Write separate v4 mandatory operational/GPU-transfer gates, descriptive DC
  results, and pending v5 DC gates. Give each failure/unavailable case a result.
- Estimate Q from all relevant cycles and final operating conditions, not
  cycle 1 alone. Define sustained plateau, finite observation horizon and
  measurement uncertainty; freeze Q before its independent validation cycles.
  L and S estimated from the same record cannot themselves validate the
  future-state guarantee. R0-L3 contention flags are disclosures, not a causal
  explanation automatically excusing a coincident DC step.
- The busy-handle negative test says three retries; ARM-SSD says one. Use one
  specified bounded policy and timeout, no force. P1/P2 failures can be hardware,
  firmware, ownership or missing serial/UUID exposure, not merely fixable settings.
- B is listed as a fallback but ARM-SSD prohibits any mounted volume. B-cut
  removes the enrolled device from the live storage census. Both need their
  own qualified, frozen mode predicates and prospective adoption before use;
  neither is a silent runtime fallback. An unqualified alternative holds.
- W1 can serve as the first full-length endurance attempt if explicitly
  commissioned and prospectively governed, after observer/transfer qualification.
  It is not a substitute for those prerequisites or proof of v5 metrology.

### M4 — MED: retain the purchase class, qualify the performance claims

Four TB, TLC with on-drive DRAM, fanless 10 Gb/s USB-C/UAS, no unnecessary hub,
and no charging dock bypassing KM003C are reasonable requirements/preferences.
Capacity arithmetic is correct given the unverified 1–1.2 TB/copy forecast.
Two directories on one SSD are not independent copies; preserve the separate
custody/second-copy and internal window-staging/free-space requirements.

RTL9210B-class does not certify low, stable native power, reliable firmware,
UAS negotiation, identity exposure, suspend/resume or APFS handling. Test the
exact enclosure/drive/cable under sustained copy + destination rehash + flush
and remount cycles, including warm/full-drive behavior. At the assumed
0.8–1 GB/s, one 26.4 GB copy takes 26–33 s; this is not the full verified
two-copy offload time. DRAM does not alone determine sustained writes; SLC
cache, free space, firmware and temperature matter. The universal "behind any
USB bridge ... no HMB" is overbroad: a PCIe-tunneled USB4/Thunderbolt topology
differs from a USB mass-storage bridge; actual host-driver HMB support is
unverified. SN850X/990 Pro and bridge wattages remain examples/estimates, not
checked SKU specifications, availability or a purchase guarantee.

Keep buying a switched hub contingent on demonstrated need. Qualification
must prove macOS command support, actual per-port VBUS removal/no backfeed,
fixed topology and logger/meter independence; command success is insufficient.
Never add a charging path around KM003C. Confirm borrowed-unit availability
for the **whole series once**, or qualify the purchased unit before W1. A
boundary swap requires final-unit qualification and new configuration receipts.

### L1 — LOW: the criticism of min() has its direction reversed

Sol-1's `min(2 J, endpoint SD)` remains 2 J when the endpoint is noisier;
it tightens when the endpoint is quieter. Agreement L-2 says the opposite.
Choosing an absolute cap versus a relative endpoint budget is a prospective
design decision, not an algebra error or license to use max() automatically.

## macOS and device fact audit

No network or native probes were used. **Verified-general** means established
general mechanism only; **unverified-native** applies to this MBP/build/stack.
The agreement's own `(verify)` annotations are not validation evidence.

| Claim | Status and limit |
|---|---|
| fstab UUID `noauto` | **Verified-general:** UUID entries/noauto are a conventional macOS Disk Arbitration automount control. **Unverified-native:** the exact APFS syntax and every-volume coverage here, locked replug/reboot behavior, and explicit `diskutil mount <UUID>` under the unattended account. It is an automount preference, not access control preventing explicit mounts, new UUIDs or all management I/O. |
| Accessory approval while locked | **Verified-general:** Apple-silicon Mac laptops have USB/Thunderbolt accessory approval controls; reconnect while locked can need authorization depending on settings/history. **Unverified-native:** current policy, exact UI names, managed restrictions and whether this enrolled unit prompts. One locked-screen replug is useful evidence, not proof for reboot/new firmware/every reset. |
| pmset disksleep/default 10 min | **Verified-general:** disksleep is a configurable disk-idle policy; unmount is not power-off. **Unverified:** this machine's profiles/defaults and whether this USB4 bridge obeys the timer. No verified basis for "one access holds it awake ten minutes"; controller/bridge timers can differ. No pmset command was run. |
| USB4 re-enumeration and diskN | **Verified-general:** removal/reconnection or controller reset can recreate registry/media objects and change diskN, so resolve persistent identity each time. **Unverified/overbroad:** every link retrain necessarily re-enumerates or automounts, every power-state transition changes the chosen registry ID, or fstab prevents all activity. |
| IOBlockStorageDriver Statistics | **Verified-general:** block-storage drivers can expose cumulative data-I/O statistics in IORegistry. **Unverified-native:** keys, units, node coverage, lifetime/reset behavior and non-waking reads for this stack. Stable counters do not establish zero autonomous energy or every management command. |
| Unified-log event completeness | **Repo-verified requirement, not implementation proof:** protocol v4 ruling 20 requires a daytime qualification and marks absent/unqualified audit unavailable. **Unverified-native:** exhaustive relevant events and full-window retention/query coverage. Empty output is not a clean certificate. |
| UAS/RTL9210B and serial display | **Verified-general:** UAS is a USB storage transport, not a power-state guarantee. **Unverified-native:** actual negotiated transport/firmware, suspend behavior, NVMe identity versus enclosure serial, and exposure through `SPUSBDataType` (USB4/Thunderbolt may use a different tree). |

## Disposition for the lead

Sign the **direction** after H1–H4 and M1–M4 are reflected in the next SSD-P1
text and implementation acceptance list. Do not adopt the current PASS claim.
The smallest credible plan keeps B-unmount first; explicitly supersedes
Q1/five-block adoption for a declared storage-equipped v4 estimand; preserves
qualified GPU/R1 transfer and full-span event evidence; makes DC descriptive
for v4 and independently gates v5; and prospectively registers SSD losses and
cap behavior under amended R12. It keeps the drive connected permanently and
requires no scheduled human action per window. Fault recovery may hold for
the magistrate/lead rather than silently changing the mode.

The next exact step is a lead disposition and revised ruling/bridge-output
map, followed by reviewed hooks and synthetic fault tests. Native approval,
unmount/replug/audit/maximum-span and KM003C/SMC/MLX qualification remain for a
clean agent-free measurement session after the current job. This review
authorizes no measurement or adoption. The accompanying
[run report](../../run_reports/2026-11-08-ssd-p1-review-sol1.md) records checks
and remaining uncertainty.
