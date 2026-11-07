# Sol burn review: SSD-always-attached study and implementation

Date: 2026-11-06
Scope: `docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md`, `joulewise/align/apple/external_volume.py`,
`joulewise/align/apple/ssd_qualification.py`, both SSD scripts, and their synthetic tests. No hardware or experiment
paths were accessed. All execution used repository tests and temporary directories.

## Verdict

**Option B remains a plausible hypothesis, not a hardware-qualified result. Option A/A-lite are not statistically
licensed by this protocol as written.** The implementation is commendably fail-closed at the volume boundary, but the
original Q1 interval pseudoreplicated segments within a physical attach/detach block. This review fixes that defect by
making the physical block the unit of analysis and changing the default from A-D-A to A-D-A-D-A. A three-block run now
returns Q1 INCONCLUSIVE rather than a spurious interval.

The physics argument should be stated as a measurement hypothesis. The code establishes that ALIGN asks powermetrics
for the `gpu_power` sampler (`joulewise/adapters/powermetrics.py:57-58`), and the study establishes that the SSD is
bus-powered (`docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md:13-14`). Neither fact proves the undocumented boundary of
Apple's modeled GPU rail or the attribution semantics of SMC PSTR/PDTR. The revised study no longer says that enclosure
or USB4-host power can appear *only* in PSTR/PDTR.

## Findings

### F1 — Critical, fixed: Q1 used the wrong independent unit

The treatment changes only when the drive is physically attached or detached, but the old code fit every quiet segment
as an independent row and computed its standard error from segment residuals. Merely replacing the residual degrees of
freedom with `blocks - 1` did not repair that pseudoreplication: the standard error still shrank with the number of
segments. With A-D-A there are three block means and three fitted coefficients (intercept, time, presence), hence
**3 - 3 = 0 residual df**, not 2.

The corrected `presence_offset` first averages within each physical block, fits those means, and uses `blocks - 3` df
(`joulewise/align/apple/ssd_qualification.py:326-374`). The default five blocks therefore have 2 df. The default plan now
uses A-D-A-D-A (`joulewise/align/apple/ssd_qualification.py:82-116`), and a synthetic regression proves that A-D-A is
INCONCLUSIVE (`tests/align/test_ssd_qualification.py`). This is a fail-closed behavioral correction; write-pair analysis
and extraction bytes are unchanged.

Caveat: even five alternating blocks identify presence only conditional on the specified linear time trend. Inspect the
reported block residuals; an obvious nonlinear drift invalidates the interval rather than becoming evidence for a
presence effect.

### F2 — High: Q3 does not test its stated variance/MDE claim

`paired_write_effect` computes the sample of paired `write - quiet` differences, then `_interval` constructs a t
interval for their **mean** (`joulewise/align/apple/ssd_qualification.py:256-297`). `evaluate` judges that mean against
`0.30 * s_r / T` (`joulewise/align/apple/ssd_qualification.py:371-428`). This can bound a systematic mean write effect.
It does **not** bound the additional variance, standard deviation, or MDE inflation claimed in the study. A distribution
with mean zero and arbitrarily large write-induced scatter can have a mean interval centered at zero; with enough pairs,
that mean interval can eventually pass while the scatter remains large.

The existing noisy-world test only demonstrates that five particular finite samples do not pass; it does not prove the
criterion controls variance (`tests/align/test_ssd_qualification.py`). Before A/A-lite can be authorized, add a
pre-registered variability estimand and a one-sided confidence bound (for example, a block-aware bound on the SD or RMS
of paired effects). Until then, interpret Q3 only as a mean-effect test and do not cite `sqrt(1.09)` or 4.4% MDE growth.
This limitation does not block B because B performs no in-window writes.

### F3 — Medium: “Q1-Q5” skips Q4

The verdict contains Q1, Q2, Q3, and Q5; there is no Q4 in code or the decision table
(`joulewise/align/apple/ssd_qualification.py:396-428`; `docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md:364-381`). That may be
a reserved label, but neither document says so. Rename the protocol “Q1-Q3 and Q5,” explicitly reserve Q4, or use Q4
for the missing write-variability criterion. As-is, “evaluate (Q1-Q5)” overstates coverage.

### F4 — High: rail-boundary claims exceeded the evidence

Powermetrics reports energy fields named `gpu_energy`, `cpu_energy`, and `ane_energy`; `segment_power` integrates those
fields (`joulewise/align/apple/ssd_qualification.py:201-229`). This is sufficient to define the study's observable. It
is not a component-level schematic. Similarly, PSTR and PDTR are SMC observations in this project, not cited,
publicly-defined accounting boundaries. Therefore:

* External enclosure power is ultimately supplied through the Mac's electrical path, but the fraction and timing seen
  in PSTR or PDTR must be measured.
* The enclosure's NAND/bridge work is not GPU computation, but host-controller work, thermal coupling, scheduling, and
  shared-fabric effects could alter a modeled rail.
* `PSTR - CPU - GPU - ANE` is a useful diagnostic residual, not proof that its terms are mutually exclusive physical
  rails.

The study now labels those statements as empirical questions (`docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md:25-33,
105-119,129-134`). The cited 1-8 W enclosure range is explicitly anecdotal in the source text
(`docs/align/v4/SSD-ALWAYS-ATTACHED-STUDY.md:439-449`); it is suitable for planning and thermal placement, not a verdict.

### F5 — Medium: expected-precision prose was internally inconsistent

Under the old three-block plan, there were 16 attached idle pairs (8 in each of two attached blocks) and 12 attached
decode pairs (6 in each), matching the prose. Under the corrected five-block default there are 18 attached idle and 18
attached decode pairs (6 pairs in each of three attached blocks). If pair differences were independent with SD 3 mW,
the nominal 90% t half-width is approximately `t(0.95,17) * 3 / sqrt(18) = 1.23 mW`. At SD 28 mW it is approximately
11.5 mW. These are planning calculations only; serial and block dependence can make them optimistic. Q1 precision must
be calculated from five physical block means, not segment noise.

### F6 — Low: external-volume safeguards are conservative, with one evidence limitation

The census fails closed on unparsed or unreadable mounts and treats network/disk-image mounts as external
(`joulewise/align/apple/external_volume.py:179-233`). The arm check requires the sole allowlisted external UUID and
checks APFS, writability, mount point, Spotlight, Time Machine exclusion, and the fsevents marker
(`joulewise/align/apple/external_volume.py:258-328`). Routing keeps custody and TMPDIR internal and falls back internally
on refusal (`joulewise/align/apple/external_volume.py:334-366`). `RouteGuard` is sticky after a device change and fsyncs
one internal loss record (`joulewise/align/apple/external_volume.py:369-430`). Synthetic tests cover these behaviors.

However, `.fseventsd/no_log` existence and `mdutil`/`tmutil` output are configuration evidence, not proof that no daemon
will run. Q5 correctly requires observed daemon CPU to be zero above its threshold; retain that runtime check.

## Qualification recommendations

1. Use the corrected five-block default. Never treat a three-block Q1 result as decisive.
2. Retain Q1's equivalence-test rule: PASS only when the entire 90% interval is inside the margin; point-outside-margin
   FAIL and overlap INCONCLUSIVE are implemented correctly (`joulewise/align/apple/ssd_qualification.py:256-276`).
3. State explicitly that 90% confidence intervals implement two one-sided 5% equivalence tests. They are not 95%
   estimation intervals.
4. Make physical blocks—not segments—the replication unit for every presence claim. Treat write/quiet pairs as paired
   experimental units, and report block-stratified effects to expose heterogeneity.
5. Add the missing variability criterion before licensing A/A-lite. Do not loosen a margin after observing data.
6. Record PSTR/PDTR as diagnostic channels, but decide on the directly observed GPU-rail estimand and operational Q5;
   do not use subtraction identities as component physics.
7. Keep all real-hardware conclusions PROVISIONAL until an authorized quiet-machine run exists. This repository contains
   no such data.

## Synthetic verification and equivalence boundary

The focused tests exercise only temporary files and generated rows. Existing extraction, writer cadence, routing, and
happy-path verdict shapes remain covered. The deliberate non-equivalence is limited to Q1/default scheduling: five
physical blocks replace three, and three-block presence evidence is now INCONCLUSIVE. No real bundle or analysis output
was read or rewritten.
