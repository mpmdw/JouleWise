# SSD-P1 adversarial review — Sol 2

**Verdict: SIGN_WITH_CHANGES. The present text is not an adoption receipt.**

2026-11-08 UTC; independent Sol seat 2 on
`align/2026-11-08-ssd-p1-review-sol2`. Reviewed agreement:
`58fb53c3054994b9aa6ffd6b5444e5e3d6ad421e`,
[SSD-PERMANENT-AGREEMENT.md](SSD-PERMANENT-AGREEMENT.md).
Authority is `git show origin/main:RUN_STATE.md` at
`c07b388e90d9f085e6428a1e0d96b0361ff417f0`, items 181, 210,
212–215. Both original seats' study/amendment pairs were inspected from
their respective `origin/align/2026-11-08-ssd-permanent-sol{1,2}` refs;
the working-tree copies are Sol 1's, not both seats' reports.

I support **B-unmount first**, internal-only window writes, automated
between-window offload, one frozen configuration per series, a bounded R1
transfer procedure rather than an unconditional full repeat, and buying a
4 TB device outside W1's critical path if the loan lasts. Zero human actions
per window is compatible with these choices. It does not require claiming
that unchanged block counters certify power stability.

The HIGH findings below must be dispositioned before adoption. This review
changes no rule, registration, kit, machine setting or measurement schedule.
No network, raw measurement files, native hardware commands or model weights were
used. Numerical examples below are synthetic, not MBP validation.

## Findings

### H1 — HIGH: the numerical factors are right; the impossibility claim and the gate being analyzed are not

Agreement lines 43–52 correctly analyze a **raw presence coefficient** for
equally spaced blocks with design columns `[1, t, z]`, `t=0..4`,
`z=(1,0,1,0,1)`. With observed residual block SD `s_b`:

```text
residual df = 5 - 3 = 2
[(X'X)^-1]presence,presence = 5/6
SE(presence) = 0.912870929 s_b
t(0.95, 2) = 2.919985580
90% CI half-width = 2.665569950 s_b
95% Gaussian SD upper bound = sqrt(2 / chi2(0.05,2)) s = 4.415396443 s
```

At `s_b=5 mW`, the mean half-width is 13.328 mW: **1.599 J at
120 s, 23.990 J at 1,800 s**, respectively 15.99 and 239.90 times
0.10 J. A zero-centered interval fits only if `s_b` is below approximately
**0.31263 mW / 0.020842 mW**, respectively. An SD upper bound of 0.60 J
with two df requires observed SD at most **0.135888 J** under that simple
Gaussian model. The practical precision objection is strong.

But two residual df do not impose a positive lower bound on the interval
width. A constructed nonzero-noise five-block example with `s_b=0.010 mW`
has a 1,800 s mean half-width of **0.047980 J** and even a conservative
total residual SD upper bound of **0.079477 J**: both pass. This establishes
mathematical possibility only. Neither this tiny scatter nor the agreement's
optimistic 5 mW assumption has been measured here. A large estimated effect
can also produce FAIL, rather than the asserted inevitable INCONCLUSIVE.

More fundamentally, both seats define QDC on **uncancelled energy after the
frozen baseline/offset operator**, including its uncertainty. Sol 1 explicitly
says this at study lines 99–106 and amendment A4; Sol 2 defines `r(T)` in
study §2. A CI for raw drive presence is not automatically that CI. A shared
power offset can cancel under a matched baseline, while an imperfect baseline
can add covariance and estimation error. The 4.415 factor bounds a simple
total Gaussian SD; it does not by itself estimate an added variance component
above noisy absent controls. Both seats already acknowledge insufficient
precision and the possibility of extension.

**Required change:** replace “can never pass / must be INCONCLUSIVE” with
“the proposed base design has no demonstrated power at the proposed DC
resolution.” Specify the actual endpoint operator before a power calculation.
Do not use this objection to discard GPU Q1: its approximate 62.5 mW margin
at 25 W is much wider than the 13.328 mW half-width in this same example.
The existing synthetic Q1 studies also show useful five-block power.

The proposed “250–57,000x more blocks” is a fixed-critical-value,
inverse-square heuristic, not a sample-size calculation: the critical value
falls as df rises, and correlation, controls and the endpoint operator matter.
Remove the literal requirement or label the assumptions.

### H2 — HIGH: permanence changes the comparison population; it does not establish cancellation or supersede R12

Agreement lines 67–73 and 126–130 substitute “same drive” for a statistical
stability guarantee. Fixed physical presence removes absent/present mixing
within the new series. It does not remove load-, duration-, temperature-,
position- or previous-offload-dependent effects. Even perfectly constant
power `p` adds `p*T` joules: 5 W over a 300 s duration difference is 1,500 J.
An energy intercept cannot absorb that generally. Host-controller/fabric
effects and altered thermal gates can affect GPU energy without SSD I/O.

The consequences differ by endpoint:

| Endpoint | Defensible scope of dropping a gate |
|---|---|
| v4 GPU primary | The measured rail remains GPU under item 212 R11-3. Final-configuration fit/calibration/test data can support a claim about that configured machine. Dropping Q1 gives up demonstrated drive-free equivalence and requires validated thermal/budget/replay transfer and the original eligibility gates. Presence alone does not prove exchangeability or unchanged sensitivity. |
| v4 DC secondary | A prospective v4-only waiver of the proposed 0.10/0.60 J QDC can be reasonable. Keep raw gross, baseline-treated diagnostics, battery/coverage flags and explicit limitations; do not describe SSD/DC stability as qualified. Missing DC remains missing and does not silently rewrite rail eligibility. |
| v5 DC primary | Descriptive offsets and counter silence cannot qualify the endpoint. Freeze scope, baseline or duration treatment, battery policy, clock/meter uncertainty, load/history dependence, calibration and held-out scoring before primary use. A gross configured-machine endpoint may legitimately include SSD energy; idle subtraction is a design choice, not a universal physical requirement. |

[KM003C-ALIGN.md](../squeeze/KM003C-ALIGN.md), especially its print-only
convention and open questions, confirms that v4's per-member idle subtraction
and separate DC fits are diagnostic. Its subtraction cancels a constant only
when the baseline and scored interval share that constant. It does not
qualify v5 or permit a post-hoc fitted SSD correction.

Item 214 explicitly rejects SSD-qualification shortcuts. The cited latency
synthesis, row 22 and §2, rejects three blocks for lost residual df; it does
not authorize deleting the contrast. The agreement's interpretation is a
**new scientific proposal**, not an already installed exception. Ed's
permanence objective authorizes pursuing the configuration, not an unstated
change of exclusion rules or endpoint claims. Item 181 reserves research-plan
changes to Ed and leaves scheduling to the magistrate.

**Required change:** explicitly seek a scoped pre-W1 supersession of item
214 and its owning qualification surfaces through the lead/Ed process. Either
retain GPU Q1, or replace it with a named, reviewed final-configuration
stability/transfer design and narrow the equivalence claim. State that the
v4-only QDC waiver supplies **no v5 primary qualification**. Close D-043
back-annotations when adopting, not in this advisory review.

Also correct §3.2's prerequisite “Sol + Opus”: Ed's present brief requires
two independent Sol seats reviewing each Opus product. An additional Opus
review does not replace the second Sol seat; the lead verifies the final result.

### H3 — HIGH: registry counters plus unified logs cannot certify zero wake or unchanged power

Agreement lines 89–94 call the proposed mechanism “zero-overhead,
zero-wake”; ARM-SSD then treats it as full-span state proof. Registry reads
normally inspect kernel properties without reading a mounted filesystem.
That makes them promising **boundary snapshots**, with no new in-window
poller. It does not establish the claimed completeness or native behavior.

An enclosure/SSD can autonomously change power state, temperature or link
state with unchanged logical block read/write counters. Management commands
and USB/bridge activity need not appear as block byte/operation increments.
An entry ID identifies an IORegistry object during its lifetime; a reset or
recovery need not recreate the particular object being sampled. Conversely,
a genuine detach/re-enumeration normally does create new objects. The exact
driver node and its relation to the enrolled physical device must be proven.

Unified logs are a diagnostic record, not a guaranteed durable journal of
every mount, transient reconnect or power transition. A successful `log show`
with zero matching rows is not proof of coverage: predicates, log levels,
privacy, retention and clock boundaries can omit relevant events. An
unobserved brief mount/unmount need not leave a changed final mount table.

The two-hour P4 screen also misses a 1 W, 1 s excursion (1 J), or a slow
10 mW drift over 1,800 s (18 J), despite their potential relevance to a small
DC endpoint. A mounting/read-induced wake is not a calibrated signature of
every autonomous power transition. If measured `S` is zero, negative,
unresolved or has substantial uncertainty, `S/2` is not a useful threshold.

**Required change:** describe the mechanism as evidence for block-I/O and
device continuity, with an explicit coverage limit. Bind the device to its
storage-service node and counter schema; require valid timestamps, monotone
counters, complete before/after records and fail-closed handling of missing,
reset, stale or unparsable observations. Qualify the registry query's native
behavior outside this sandbox. Validate log predicates against induced events
and bind events to the enrolled device's lineage; keep log silence
corroborative.
Any post-receipt I/O invalidates the quiet receipt; restarting Q requires
verified preparation, not silently overwriting counters. If full-span event
coverage is an adoption requirement, qualify an OS event journal or another coverage-bearing
mechanism; do not infer it from an empty retrospective query. Reuse existing
DC/SMC capture to investigate autonomous changes without adding SSD probes.
V5 still needs endpoint-length, load/history and early/late energy evidence.

### H4 — HIGH: the lean bridge and P1–P5 omit configuration-sensitive R1 and operational gates

Agreement §3.3's one D load/recovery step does not establish every output the
original R1 qualified. [r1_runtime_contract.md](../r1_runtime_contract.md)
records the 30B and D steps, S1–S9, designed start states, gated D/X-G runs,
planning turns, power policy and dependent budgets. Both original SSD seats'
§5 transfer inventories cover these dependencies. Moving the enclosure
30 cm away reduces an external heat path; it says nothing quantitative about
SoC host-link heat, supply headroom, battery flow or altered recovery waits.

Q5 is also not explicitly preserved in the new all-required P1–P5 list.
`ssd_qualification.operational()` currently checks metadata-daemon activity,
battery float and thermal offset as well as arm checks and losses. P3/P4
counter silence cannot replace those. “Compared against R1's own bands” does
not identify which evidence can retain each slot or how dependent caps are
recomputed. Newer R11 battery requirements must survive the older Q5 screen.

**Required change:** make P5 a transfer matrix: each reused R0/R1 output,
owning criterion, final-configuration evidence, dependent kit field and
failure action. Cover internal paths/stack/token identity, sensor inventory,
soak/noise, 30B/D rate and decline, recovery/G0/G1/H, predecessor heat, duty,
`I_D/B_D/T_dead/N_chunk`, contrast caps and power/battery/meter continuity.
Retain the applicable operational checks explicitly. Reuse settings when all
their criteria pass; repeat only affected work when dependency closure is
demonstrated, otherwise repeat the relevant R1 sequence. **2.5 h is an
estimate, not a waiver or an established bound.**

Using W1 as the first endurance opportunity can be a prospective engineering
choice; it risks losing W1 and cannot establish maximum-window reliability
in advance. Its programmed span is shorter than the D span/59,520 s ceiling.
W1 success alone must not be called a full-length endurance qualification.

### H5 — HIGH: SSD_EVENT needs the amended R12 eligibility contract and a configuration-break distinction

ARM-SSD's conservative pre-arm census and no-force/no-empty-mount-point
rules are sound. One enrolled physical device with all volumes unmounted is
stronger than a mounted-volume allowlist. Extend “every container volume” to
every filesystem/LUN exposed by the enrolled hardware; resolve identities
afresh rather than trusting `diskN` or a UUID alone. Ambiguous observation
must refuse the arm.

But agreement lines 103–105/184–186 assume “min 6, cap 8 already absorbs
losses.” Item **215 amends B3**: window roles/order, final eligibility,
both-pair predicates, cap accounting, failure outcome and simulation of
selection/exchangeability must be frozen before W1. Counts alone do not
satisfy R13/R14. The B3 calibration rule does not automatically define test
window replacements or W1 retry policy.

Failures can correlate with long/hot work or an offload-dependent power
state. Deleting the corresponding windows, or excusing a DC step because a
contention flag “explains” it, can select the score distribution. Moreover,
a failed drive replaced by another model is not merely one lost window in
the old calibration population. The new text drops the original seats'
explicit no-pooling-after-configuration-break protection.

**Required change:** register SSD_EVENT and observation-unavailable outcomes,
the protected interval, whole-window consequences, role-specific retries and
attempt accounting. Failed calibration attempts consume the registered hard
cap; do not count only successes or assume eligibility targets will be met.
Include the SSD loss mechanism in item 215's pre-W1 simulation/qualification.
Do not use a score/energy-dependent veto to clean the pool post hoc. A
transient event may resume only after verified restoration to the **same**
qualified configuration. Device/enclosure/firmware/topology/mode changes hold
new arms and require a prospective new-segment/series and pooling ruling.
The first event already requires diagnosis before resuming; “second event
requires requalification” cannot authorize an unverified first recovery.
Scheduling remains the magistrate's responsibility under item 181.

### M1 — MED: the time bill and P3/P4 pass semantics contradict the claimed all-required PASS

The listed automated steps sum to **0.5 + 2.5 + 2 + 2.5 = 7.5 MBP h**.
Including the sequential 45 min Ed setup gives **8.25 MBP h**, before the
wake/read, exceptional settle, reruns, brackets and harvest. The claimed
6.5 h is not obtained. Earlier seats' base 6.833/8.5 h and the 4.415 SD
factor check out; their larger totals were conditional minimum estimates.

P3 says `Q <= 60 min` is required and simultaneously accepts larger Q.
P1–P5 are “all required,” yet DC-only P3/P4 failures may proceed in v4.
`Q >= 30 min` also consumes most of the 30–45 min turnaround after offload;
`Q=60 min` cannot meet that target. Three full settles at Q=60 min already
exceed step 3's entire 2.5 h allowance. Counter quiescence needs a defined
observation duration and timeout. L should use the worst qualified cycle,
not only cycle 1, with a prospective response to later slower settling.

**Required change:** publish a conditional time bill, distinguish
`V4_OPERATIONAL_PASS / V4_DC_UNQUALIFIED / V5_DC_PASS`, and give P3/P4
unambiguous failure/waiver outcomes. Bound missing plateaus, unresolved S,
log/counter failures and retries. Reconcile the negative unmount test's
three retries with ARM-SSD's one retry. R0-L3 flags are disclosures, not a
blanket scientific waiver for DC excursions. Longer Q is an explicit cadence
tradeoff. The post-R1 timing recommendation is sensible; actual run status
and R1 completion were not observed, and item 215's 67,371 s is a subtotal
before its stated bracket/close/harvest additions.

### M2 — MED: the purchase class is reasonable; chipset and DRAM do not qualify power behavior

Accept 4 TB, TLC with on-board DRAM as a conservative purchase preference,
fanless enclosure, direct fixed port/cable, no hub initially and no charging
dock bypassing KM003C. At 0.8 GB/s, 26.4 GB takes about **33 s of transfer**;
flush, hash, mount and settling still belong in turnaround. USB4 bandwidth
is not needed for that nominal offload target.

The specific SN850X/990 Pro and RTL9210B-class examples have **not been
verified offline here** for current revisions, firmware, exposed identity,
4 TB compatibility, UAS, sustained speed or sleep behavior. A bridge family
does not guarantee lower/steadier power on this macOS/port/cable combination.
The universal “any USB bridge” HMB claim is too broad; common USB storage
bridges generally do not expose NVMe HMB, but exact transport matters.
DRAM-less slowdowns depend on capacity, SLC cache, fullness, workload and
firmware; 20–50 GB is not a demonstrated cliff. DRAM can itself cost power.

**Required change:** keep the spec as a preference, with actual-device
qualification and returnability as procurement criteria; label performance
and wattage predictions unverified. A B-cut hub must prove per-port physical
VBUS removal/no backfeed and autonomous recovery on macOS, and becomes a new
qualified topology. Bus-powered storage keeps its supply inside the stated
KM003C path. An externally powered SSD/hub can move SSD energy outside that
boundary even if it does not charge the Mac; disclose/redefine that boundary
rather than claiming the meter captures it.

### L1 — LOW: Sol 1's min() is misdescribed

Agreement line 110 says `min(2 J, endpoint SD)` tightens the allowance when
the DC endpoint is noisier. It yields **1, 2, 2 J** for endpoint SDs of
1, 2, 4 J: it tightens below 2 J and caps above it. The policy may be too
strict, but its direction is not as described. A DC endpoint needs its own
prospectively justified resolution; merely being noisier is not authority
to permit an arbitrarily larger SSD error or preserve a small-effect claim.

## macOS and mechanism fact audit

No web, local system-manual lookup or live MBP inspection was performed.
“General knowledge” below is not verification of this machine/build.

| Claim relied on | Status and limit | Native evidence owed before use |
|---|---|---|
| UUID entries in `/etc/fstab` with `noauto` suppress normal automatic mounts | **General knowledge; exact recipe UNVERIFIED.** Plausible macOS mechanism, not implemented/tested in the inspected repo. It is not a veto on explicit mounting, raw device probes or newly created, unenrolled volume UUIDs. | Verify the exact APFS volume UUID syntax using the enrolled hardware, normal reconnect and restart. Check every exposed volume; preserve/restore settings under the operator's procedure. |
| `diskutil mount <UUID>` and whole-device `unmountDisk` cover the intended APFS children | **General knowledge; exact APFS node/behavior UNVERIFIED.** The existing module models mounted volumes, not B-unmount. | Establish physical-store/container relationships, all-volume results, open-file refusal and identity after disk-number changes. |
| Locked-screen accessory approval can block unattended reconnection | **General knowledge; exact policy/option names UNVERIFIED.** Previously approved devices and policy states can behave differently; not every reconnect necessarily prompts. | Locked reconnect/restart test under the chosen policy. Do not assume globally allowing every accessory is necessary for an enrolled device. Ed owns that setting. |
| `pmset disksleep` defaults to about 10 min and governs the NVMe enclosure's wake residence | **UNVERIFIED on this MBP.** “10 min” is a common historical setting, not a universal default or proof of USB/NVMe firmware/APST behavior. | Record actual AC settings and observe last-I/O-to-settled behavior across cycles. The 3–5 W/10 min step is an anecdotal planning scenario. |
| USB4 retrain/reset always re-enumerates with a new `diskN`/entry ID | **UNVERIFIED and overstated.** Disconnect/reconnect can re-enumerate; some resets/retrains can preserve particular service identities. Disk numbering is not persistent identity. | Exercise reconnect/reset paths that can be tested safely, map registry nodes and log/counter responses; fail closed on ambiguity. |
| IOBlockStorageDriver counters establish no logical block I/O | **General mechanism plausible; schema, completeness and no-wake behavior UNVERIFIED on the selected stack.** Not proof of SSD power state. | Read-only snapshot qualification, correct parent/child association and induced-I/O positive controls. |
| Unified log silence establishes no mount/reconnect/wake over a window | **UNVERIFIED; insufficient as an exhaustive negative guarantee.** No inspected repo implementation provides such coverage. | Known-event detection/retention/clock/permission tests and explicit observation-unavailable outcomes; qualify a coverage-bearing journal if required. |

The repo verifies the current GPU Q1/Q5 algorithms and a default-off,
mounted-volume census through synthetic tests. It does **not** verify the
new registry/log collector, ARM-SSD wiring, locked-screen recipe or enclosure
power claims. The original study's forum wattages remain anecdotes.

## Required P1–P5 disposition before a signature becomes adoption

| Criterion | Review disposition |
|---|---|
| P1 — automated offload/mount/unmount | Keep. Verify all identities, volumes, hashes, internal free space, timeout/abort recovery and no live-run remount. Include the open-file negative test; never force. |
| P2 — locked reconnect/no automount | Keep as a native operational gate, including log/registry positive controls and actual policy/UUID behavior. Reconnect during a window is still a loss, not permission to continue measuring. |
| P3 — plateau/Q | Define plateau estimator, bounded observation, worst-cycle L, allowable Q and cadence consequence. State the explicit v4-only DC waiver instead of calling a failed P3 a universal PASS. |
| P4 — two-hour quiet screen | Keep as an operational screen with documented detection limits. No observed block I/O is useful; it is not zero-wake proof, a DC equivalence result or a maximum-window endurance result. |
| P5 — R1 bridge | Replace the one-step description with H4's dependency matrix and preserved operational gates. Retain settings only on their owning evidence. |

Before W1, also install H5's amended count/eligibility/series rules and
item 215's required simulation. Before v5 primary use, qualify the actual DC
endpoint with the final purchased hardware and full intended scope. Hardware
replacement at the v4/v5 boundary is sensible; it does not make v4's QDC
waiver evidence for v5.

## Verification and handoff

- Independent arithmetic using the repo OLS and t-quantile primitives plus
  analytic two-df chi-square: factors, thresholds, a nonzero-noise passing
  counterexample and time sums reproduced. No native precision inferred.
- `python3.13 -B -m unittest tests.align.test_ssd_qualification`:
  **26 tests, OK**, 0.353 s.
- `python3.13 -B -m unittest tests.align.test_external_volume`:
  **23 tests, OK**, 0.006 s. System calls in these tests are faked.
- Full suite and Block-5 pipeline were not run. No MLX/native storage tests
  were run; this review changes no code.

The lead's next exact step is to disposition H1–H5 and issue the scoped
SSD-P1 revision/authority change, then have the implementation and native
qualification reviewed before the magistrate schedules it after R1. The
independent second seat and final adjudication remain the lead's work. Native
tests above must run in a lead-controlled non-measuring interval, followed by
the normal quiet-machine preparation; never during the active blinded job.
