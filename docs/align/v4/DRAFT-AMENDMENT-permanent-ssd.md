# DRAFT AMENDMENT: permanent SSD in ALIGN v4 and v5

2026-11-08 brief; independent Sol seat 2. **DRAFT, NOT IN FORCE.**
Qualification rationale, numerical derivation and time bill:
[SSD-PERMANENT-STUDY](SSD-PERMANENT-STUDY.md). No measurement, arm permission,
new registered constant or successful software integration is asserted here.

## A1. Scope, channel and adoption

This proposal replaces the old
[external-log-volume draft](DRAFT-AMENDMENT-external-log-volume.md)'s A1 DC
carve-out, A3 pre-R1-only boundary, mounted-only A2/A6 logic and A8 GPU-only
qualification **on adoption**. The old files remain historical drafts.
Meter-everywhere makes “any DC/whole-machine measurement keeps the old rule
without exception” unsuitable: a permanent bus-powered SSD contributes to
every KM003C capture.

The configuration may include one permanently connected SSD, qualified and
operated under A2–A8. **v4's registered residual remains GPU-rail energy**;
KM003C DC-in remains secondary/print-only under RUN_STATE 210/212 R11-3.
This amendment does not promote a v4 DC fit, replace U3, change U1–U6, or
change X1–X8. v5's primary DC endpoint requires its own frozen integration,
baseline/duration, battery, uncertainty and calibration/scorer contract.

The power path is wall brick → KM003C → MagSafe → MBP → bus-powered storage.
KM003C includes supplied SSD power, excludes brick AC loss and can differ
from machine consumption during battery charge/assist. PSTR/PDTR are observed
diagnostics, not substitutes for the meter or guaranteed component boundaries.

Adoption requires a lead-selected mode and exact device, completed Q1/Q5/QDC
and native automation qualification, the owning scientific/registration gates
and Ed's acceptance of the permanent configuration. Ed has already ruled
permanence as the objective; no per-window physical confirmation is required.
Until adoption and wiring, the existing arm rule remains in force. A legacy
kit `B` verdict alone cannot authorize this exception.

At adoption, the lead closes supersession under D-043: annotate old live-rule
surfaces (FINAL-DESIGN physical setup/lever clauses, item 181/external-volume
runbooks and affected kit/registration contracts), bind the new rule/digests,
and install the event/admission consequences prospectively. This docs-only
proposal does not modify coordination state or frozen evidence.

## A2. Qualified configuration and allowlist

The arm admits at most **one physical external storage device**, only in its
frozen qualified mode. Pin drive model/serial/capacity/firmware where exposed,
enclosure/bridge identity, container/volume UUIDs, cable/port/topology and
placement. Missing serial requires a reviewed alternative; a UUID/name alone
does not prove hardware identity. Resolve diskN from identity at each arm.
All unapproved external, network and disk-image mounts still refuse; the
KM003C instrument is not a storage mount. Missing/ambiguous census refuses.

Modes in preference order; exactly one is frozen for a series:

1. **B:** attached, powered, mounted, no reads/writes during the protected
   interval. APFS, ownership on, writable for between-window offload, expected
   mount point/UUIDs, Spotlight disabled, Time Machine excluded and fsevents
   suppression settings verified. Runtime quietness is also required.
2. **B-unmount:** attached/powered, every child volume unmounted by
   `diskutil unmountDisk <identity-resolved whole disk>` before pre-arm.
   Physical presence remains verified; prevent/observe automatic remount.
   Restore with `diskutil mountDisk` only after A6 finalize, then verify UUIDs.
   No force-unmount and no assumption that unmount removes bus power.
3. **B-cut:** permanently wired to the pinned hub; safely unmount, then use
   qualified `uhubctl` per-port control before pre-arm. Prove actual VBUS off,
   no backfeed and no unwanted ganged-port effect. Bind the prior observed
   device identity to that port while it is off. The fixed hub remains part
   of the measured machine. USB 3.x speed is acceptable; macOS electrical
   switching support and enclosure fallback must be tested on actual hardware.

**A/direct and A-lite/backup writes anywhere inside a window are not adopted.**
Never switch modes as an automatic recovery during a series. A firmware,
enclosure, hub, cable/port or physical-layout change also requires review and
requalification; an equivalent product name is insufficient.

## A3. DC power as a configuration constant

Measure idle/decode candidate-minus-physically-absent offset `p_L` and its
uncertainty with independent physical blocks. The qualified state must remain
stable through the longest window, without I/O, reconnects or state changes.
APST/ASPM behaviour over USB4 and a nominal sleep LED are not evidence of this.

For each actual endpoint span T, bound unexplained energy
`r(T) = integral(configuration power increment) - p_L*T`, including offset
uncertainty, within-window drift, host/thermal effects and battery/clock
uncertainty. Proposed QDC uses the ~2 J replay reference:

- **Mean error:** entire block-aware 90% interval within **±0.10 J**.
- **Added SD:** one-sided **95% upper bound ≤0.60 J**, for idle and decode
  and the endpoint lengths actually used; sample SD or Q3 mean PASS is insufficient.
- No unexplained transitions, I/O or gaps in required state/meter evidence.

These are proposed qualification constants, requiring scientific adoption;
they are not imported into v4's registered estimator. At 234.5 s the budgets
are 0.426 mW mean error / 2.559 mW power SD; at 1,800 s, 0.056 / 0.333 mW for
coherent errors. The historical 19–58 J regression SD is not the qualification
scale for the tighter replay endpoint. DC repeatability at ~2 J is unproven.

A constant draw may be several watts; it need not equal zero. Raw gross DC
energy includes `p_L*T`, including extra duration. Do not remove it with an
intercept or an outcome-fitted subtraction. Any v5 fixed trusted baseline or
duration model is separately qualified and registered; raw gross stays visible.
v4 diagnostic idle subtraction is not evidence that the offset cancels in v5.
Battery/meter uncertainty that cannot resolve the budget gives INCONCLUSIVE.

## A4. Qualification and R1-to-W1 boundary

Before first permanent use, run the study §4 protocol in a clean lead-controlled
[QUIET-MAC] campaign with Ed present Sunday 2026-11-08 for the physical controls.
Compare physically absent against each candidate at idle and fixed decode;
use five physical blocks per comparison with the existing 600 s settle,
six idle/six decode pairs, 120 s segments and 60 s gaps. Each is **6.833 h
planned** and retains 2 residual df; three blocks have zero df. Do not shorten
it for turnaround. All three comparisons cost 20.5 h before extensions.
Adapt the old write/presence runner explicitly for quiet/unmounted/off modes;
an unmounted drive is not a physically absent control.

Retain Q1's GPU presence-equivalence bar (90% interval within ±0.25% reference
decode power), Q5's operational/battery/thermal checks, missing-block/count
guards and nonlinear-drift review. Planned unmount/cut between protected
intervals is distinguished from an unexpected loss. Preserve the newer R11
battery rules in addition to Q5's older check. Add actual KM003C continuous
capture, clock/custody/battery coverage, matched long-span controls and QDC.
No missing channel is zero energy. **PASS requires Q1 AND Q5 AND QDC PASS**.
FAIL/INCONCLUSIVE blocks permanent qualification; do not loosen margins.

Add selected-mode maximum-window endurance (~16.533 h at 59,520 s), repeated
endpoint-length idle/decode/hold probes and restore/offload tests. Thus one
comparison plus endurance is **23.367 h minimum**; all three plus endurance
are **37.033 h minimum**, excluding long controls, handling, settling and
precision-driven extensions. The existing evaluator has no QDC or off-state
support. Review and validate the new method/automation before using it to arm.

R0/R1 tonight without storage remain immutable, valid **for that configuration**.
The SSD may join **before unregistered W1**, but only at a documented boundary
and after qualification/transfer. Recheck sensor/stack identity, idle soak and
S1–S9, 30B/D throughput, I_D/tail, B_D/T_dead, G0 waits/caps including the
contrast cap, G1/H recovery, duty/High Power/cooler choices and replay history
under the exact final mode. Q1/Q5 alone do not validate these outputs.

Default: repeat full R1 (~18.71 h allowing one OS-batch encounter, plus retries/
brackets/harvest). A smaller lead-approved transfer must identify each reused
output and demonstrate its bound still holds. Regenerate affected slots,
caps, kit and receipts before W1; do not silently enlarge a budget or change a
thermal setting. The new configuration has its own W1 reference/bridge prints.
No model-window spans absent/present configurations. v5 requalifies its primary
DC endpoint before fit/calibration/test, with the selected permanent hardware.

## A5. Protected interval and paths

From quiet-period start through terminal finalize, every run/model/log path,
both in-window copies, custody and TMPDIR stay internal. No SSD access,
offload, backup, hash/compress, maintenance probe or background indexing.
Check actual access/state, not just disabled-service settings. Require enough
internal capacity for the complete window and finalize; permanence does not
move live writes off internal storage.

Before pre-arm, finish offload and flush, apply the qualified mount/power
state, then wait `Q = max(30 min, 2 × measured worst last-access-to-stable-state
latency)` plus any longer observed requirement. Verify actual settled state.
Transitions and maintenance triggered by unmount/power switching count toward
settling. Q may overlap ordinary cooling only after I/O ends; no offload
overlaps a measurement. A measured long Q can exceed R12's 30–45 min target.

## A6. Magistrate lifecycle

The following must be implemented and tested before adoption; not available
merely by adding a JSON mode to the current unknown-key-refusing config:

1. After previous terminal completion, finalize/hash and commit the evidence
   record; prove the driver stopped. Offload to the identity-verified SSD and
   verify copies. Never restore power/mount while run termination is uncertain.
2. Apply A2's frozen mode with bounded timeouts and journaled commands/results.
   Recover once only under a documented safe policy outside a window; on
   failure, hold/refuse rather than ask Ed to plug/eject. Remount failure cannot
   silently become “continue without SSD”.
3. Complete Q, cooling, charging/battery and display dwell. Validate physical
   device plus mount/power census, internal routing, qualification digests and
   actual meter samples/clock/custody/battery evidence at prepare/install/arm.
4. During measurement, the magistrate stays idle. A qualified lightweight
   event/I/O collector provides full-span evidence without waking storage.
   Mounted-volume polling/stat alone is insufficient; no in-window diskutil,
   SMART scan or agent turn is implied.
5. After proven terminal finalize, restore B-unmount/B-cut to its verified
   offload state, complete offload, then start the next quiet transition.
   Mechanical triage gates the next arm under R12; first post-W1 and any
   code/config change retain full desk gating. Desk work stays off the MBP.

Normal operation requires **zero Ed actions per window**. Initial connection,
safe device preparation, permissions and exceptional failed-hardware replacement
remain setup/service actions. No new hardware action is authorized by this draft.

## A7. Manifests and failure consequence

Each per-window manifest records amendment/mode/config/qualification digests;
physical device/enclosure identity; container/volume UUIDs; cable/port/hub
topology; resolved disk identifier; mount state and mounted child UUIDs;
port power state and proof; last access, quiet-start and settled timestamps;
full-span event/I/O coverage; meter hashes/clock/battery status; restoration
results and terminal disposition. In B-cut use pre-cut identity plus bound
port/off-state continuity; do not query a powered-off drive to identify it.

Unexpected disconnect, removal, power-on/off, remount, different identity,
unexplained state transition or missing required state evidence triggers
**CONFIGURATION_BREAK / REQUALIFY** (proposed internal journal event
`ssd.configuration_break`). Preserve raw data and record timing/reason. Mark
the affected window ineligible for qualified calibration/claims, stop subsequent
measurement arms, and close the configuration segment. Restore/recover only
after proven stop. The lead rules a new boundary, requalifies/re-registers
affected dependencies and dispositions any required W1/calibration/test restart;
no silent mode switch or pooling across the break. Prior clean data remain
preserved with their original configuration identity.

This is a prospective whole-window/series-admission consequence, not permission
to invent an X9 exclusion or retroactively delete members. The adopted event
catalog and admission rule must be explicit before the first qualified window.
The old draft's “continue and exclude overlapping members/600 s” does not
establish DC stationarity or restore a permanent configuration.

## A8. Disclosure, purchase and unresolved gates

Print the mode/identity, qualification intervals and limitations, GPU/PSTR/PDTR/
KM003C presence offsets, power-state variability, actual meter availability and
any break. Label PSTR minus modeled rails as a diagnostic including possible
storage/host contributions, never as a disjoint-rail accounting proof. v4 DC
stays secondary; failed qualification cannot be relabelled primary evidence.

If buying, require **4 TB** usable capacity planning for ~1–1.2 TB raw per v5
copy (two copies ~2–2.4 TB before retained models/headroom), stable low idle/
sleep draw, exposed durable identity, reliable flush/resume/mount, macOS/APFS
support, passive cooling and **no fan**. Require measured offload bandwidth
and power behaviour rather than a product brand. For B-cut, additionally
require genuine macOS-controllable per-port VBUS switching, no backfeed/ganged
cut and compatible USB 3.x fallback. Two copies on one drive do not replace
the independent verified second-copy policy. No network/product verification
was performed.

Open native gates: DC precision at the proposed budgets; state/daemon/I/O
residency over a whole window; hub electrical control and resets; safe remount/
crash recovery; battery/clock/custody coverage; R1 transfer and actual hours for
enough independent blocks. If no mode passes, hold the permanent exception
and return the scientific/configuration decision to the lead. Routine manual
unplugging and unqualified in-window writes are not fallbacks under this draft.
