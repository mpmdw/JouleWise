# Successor-paper survival map

This map treats `docs/paper/draft-v1.md` as a frozen 672-line source. It is an
audit ledger, not a substitution script. The successor is written in
`docs/paper/draft-v2-skeleton.md`; no instruction here authorizes an edit to
the frozen draft or to retained evidence.

The three dispositions are literal:

- **KEEP VERBATIM** means copy the frozen bytes in the stated range.
- **KEEP WITH NAMED EDITS** means copy everything except the exact
  quote-to-replacement pairs listed here. No nearby wording is silently
  repaired.
- **REWRITE** means do not seed prose from the frozen range. The paragraph for
  that range fixes what the new text must build, its order, and the result-fill
  registry rows it may consume.

In this map, a registry row identifier can be a conventional placement row
such as `DS-25`, an identity row such as `V5-ID-001`, or an exact-token key such
as `R_1p7B_decode_abs`. The successor renders a value slot as
`[FILL:<registry-row-id>]` only while its named supplier is still pending. A
`STOP_FILL` row instead carries that row's exact omission sentence immediately
beside the marker; no generic “do not fill” note substitutes for it.

## Preamble and title — frozen lines 1–8 — REWRITE

Build one protocol-first title before any outcome is known, then disclose that
the optional subtitle *attribution-limited* is allowed only if every required
authenticated, evaluable independent-edge ratio \(R\) and every required
authenticated, evaluable comparative shared-error ratio \(R_{cm}\) is at least
2. A missing,
unauthenticated, or zero-denominator required ratio selects neither outcome A
nor B, stops branch-dependent filling, and forbids the subtitle. Do not
preserve the two-title device, `_v4`, or a null-outcome title. Consume no
campaign result row; title identity comes from `V5-ID-001`, `V5-ID-002`, and
the D-165 branch rule.

## Abstract — frozen lines 9–12 — REWRITE

Write this only after the campaign and the post-campaign transfer fiducial are
known. In order, build the physical boundary-assignment problem, the in-window
pulse calibration, the point-only and boundary-moved component bounds, the
twofold ratios \(R\) and \(R_{cm}\), the selected outcome branch, the fixed
Qwen3 demonstration as an application of the rule rather than a scaling
study, the retained 37-of-50 short-prefill refusal, and the one-machine scope.
A missing, unauthenticated, or zero-denominator required ratio selects neither
outcome branch and stops filling rather than becoming an outcome-B shortfall.
Consume the eight independent-edge ratio keys, the four comparative
`R_cm_*_cmp` keys, `DS-25`–`DS-33`, `PG-01`, `PG-02`, `PG-04`–`PG-08`, and
`DG-067`–`DG-069`; render every `STOP_FILL` placement with its exact omission.

## 1. Introduction — frozen lines 13–32 — REWRITE

Build from physical reality before vocabulary: power is averaged over time
records; a software phase edge can split one such record; moving that edge
moves energy between prompt processing and token generation without changing
request energy. Then introduce the corrected clock mapping, define a cell,
define the resolution bound, build \(R\) and \(R_{cm}\) at a summary level only
after their inputs exist, state `RQ-ATTRIBUTION-DOMINANCE`, and separate the
fixed Qwen3-8B-versus-Qwen3-1.7B demonstration from any scaling claim. End with
the retained short-prefill question and scope. Consume `V5-ID-001`,
`V5-ID-002`, `V5-WL-001`–`V5-WL-005`, `V5-G2A-001`, the ratio keys, and
`DG-067`–`DG-069`; do not consume a directional result row before Section 6.

## 2. In-window calibration method — frozen lines 33–42 — KEEP WITH NAMED EDITS

Everything else in this range survives. Apply these five edits only.

1. Frozen quote:

   > JouleWise assigns each *powermetrics* sampling interval to prompt processing (*prefill*) or token generation (*decode*) using phase boundaries emitted by the runtime, then integrates the CPU, GPU, and neural-engine interval-average power inside each phase.

   Replacement:

   > Prompt processing (*prefill*) reads the prompt through the first output token; token generation (*decode*) emits later output tokens. A phase boundary is the runtime-recorded time separating those phases. JouleWise assigns each *powermetrics* sampling record to a phase using that boundary. A record contains the CPU, GPU, and neural-engine average power over one shared start-to-end interval; the calculation clips that interval to the phase and multiplies each channel's average power by the clipped time.

2. Frozen quote (the whole line-37 paragraph):

   > Figure 1 names the mechanism. Its horizontal time axis, vertical power axis, pale grid, and gray step rectangles show interval-average samples; the dashed trace is idealized underlying power. The lower gray bars name prefill and decode. The black vertical line is the runtime-recorded boundary, the blue band is its calibrated timing bound, and the hatched sliver is the energy that changes phase if the true boundary lies at a band edge. Double-headed arrows name one sampler interval and the power step; the blue callout arrow identifies the sliver. The legend and four notes name the marks, the high-power prefill and lower-power decode regimes, the blended sample at the boundary, and the unchanged request total.

   Replacement:

   > Figure 1 shows interval-average power around the recorded boundary between prompt processing and token generation, with the allowed boundary positions marked as a band. The hatched area is the energy reassigned between phases when the boundary moves across that band; the request total does not change.

## Bracketed pulse-train algorithm — frozen lines 43–62 — KEEP WITH NAMED EDITS

Everything else in this range survives. Apply these two edits only.

1. Frozen quote:

   > This calibrates edge placement under commanded GPU pulses and then transports that bound to sustained mixed inference load. That load-regime transfer is an applicability assumption, not a result: the pre/post bracket tests change across a window, but it does not test whether the pulse-derived bound transfers to inference.

   Replacement:

   > Commanded GPU pulses calibrate edge placement, but applying that bound to sustained mixed inference is an assumption. The before-and-after bracket tests for change across the measurement window; it does not test whether the pulse-derived bound applies to inference.

2. Frozen quote 1:

   > Figure 2 maps that bracket onto one complete measurement window. The gray horizontal arrow across the top points in the direction of session time. Blue-outlined boxes at the two ends are the pre-window and post-window calibration pulse trains; the blue bracket joining them says that the timing bound is measured on both sides of the science work and that the operative bound uses the larger capture plus a measured, never-zero allowance for change between them. The gray admission-gate box is the immediate pre-measurement check: its accompanying note names quiet state, power policy, thermal pressure, clock anchoring, and calibration freshness, and says that a failed check refuses the stage. The three small gray bars in the opening reference box, the single bar in the midpoint box, and the three bars in the closing reference box are fixed-workload reference runs used to measure drift. Between them, the two large white science-stage boxes contain small gray run bars grouped into A/B/B/A blocks—condition A, condition B, condition B, condition A. Box widths are illustrative rather than elapsed-time measurements, and the figure contains no measured data.

   Frozen quote 2:

   > The pale lower inset expands one A/B/B/A block. Its black vertical axis is measured value and its horizontal slot sequence runs from slot 1 through slot 4. A dashed sloping gray line, identified by a short gray leader, represents steady drift. Four circles lie on that line: white A circles occupy slots 1 and 4, while blue B circles occupy slots 2 and 3. The dashed blue vertical line marks the common average position in time. The two blue brackets below the circles show that the mean time of the two B runs and the mean time of the two A runs both land on that line. The right-hand notes state the consequence: steady linear drift subtracts from \((B_1+B_2-A_1-A_2)/2\), whose positive sign means B used more energy; curvature does not cancel and remains covered by the reference-derived whole-window drift allowance. Counterbalancing therefore reduces common linear drift but never replaces the measured allowance.

   Replacement for both paragraphs:

   > Figure 2 orders the before-and-after pulse calibrations, entry check, reference runs, and science blocks within one measurement window. Each science block uses A/B/B/A order—condition A, condition B, condition B, condition A—and names the four measured energies \(A_1,B_1,B_2,A_2\) in that order. Its block difference is \((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy than condition A. Matching the average run time of the two A members to that of the two B members cancels steady linear drift, while curvature remains covered by the separately measured whole-window allowance.

3. Frozen quote:

   > Appendix A.3 defines the pulse accepted region, clock-anchor feasible set, objectives, ranges, and every refusal constraint formally.

   Replacement:

   > Appendix A.3 formally defines the complete sets of pulse-edge positions and clock mappings that satisfy every fixed constraint, along with objectives, ranges, and refusal conditions.

4. Frozen quote:

   > For each commanded pulse, the detector estimates resting GPU power from samples outside every pulse margin and pulse height from samples wholly inside its plateau.

   Replacement:

   > For each commanded pulse, the detector estimates resting GPU power from samples outside the fixed time margin around every pulse and pulse height from samples wholly inside its flat high-power portion, called the plateau.

5. Frozen quote:

   > The clock anchor uses five wall-clock readings, each bracketed by monotonic-clock readings, together with every whole-second label embedded in the native power records.

   Replacement:

   > The clock anchor uses five wall-clock readings, each bracketed by readings from a monotonic clock—a counter that advances but is never corrected to civil time—together with every whole-second label embedded in the native power records.

## One diagnostic reconstruction — frozen lines 63–83 — KEEP WITH NAMED EDITS

Everything else in this range survives. Apply this non-reader-facing edit only.

- Frozen quote:

  > `while fresh _v4 captures byte-retain v3.`

  Replacement:

  > `while fresh _v5 captures byte-retain v3.`

This range consumes diagnostic rows `DG-002`–`DG-042`; none is a `_v5`
campaign result.

## 3. Instrument characterization — frozen lines 84–100 — REWRITE

Separate current characterization from pilot evidence. First state each
question in physical words, then state its calculation, threshold, sample
unit, and refusal. Explain that the 40-point linear slope reaches its endpoint
limits analytically by the signs of its fixed weights rather than enumerating
\(2^{40}\) combinations; the separate nonlinear component calculation refuses
exact enumeration above 16 observations. State that five identical-condition
blocks demonstrate only containment of those five blocks, not population
coverage. Consume `DS-02`, `DS-03`, `DS-05`, and `DS-06` only if an
authenticated characterization report exists; otherwise print the registry
refusal and no number. `DS-04` and `DS-07` are retired future-work rows and
must not be revived; `DS-01` is the separate phase-cell hold.

## Most probative diagnostic-era observations — frozen lines 101–108 — REWRITE

Label the material as pilot evidence under the retired calculation before any
number appears. In order, report the three complete unguarded point bounds
`DG-044`–`DG-046`, the three complete unguarded corner-re-evaluated bounds
`DG-047`–`DG-049`, and the three ratios `DG-050`–`DG-052`; state that they are
10.92, 5.92, and 7.02 and are not `_v5` outcomes. Then report the timing range
and member basis from `DG-053`–`DG-056`. Treat `DG-059`–`DG-062` as the
current 9.724-ms bracket screen in its named renderings; retain `DG-063` as the
retired 10.818-ms screen; distinguish the superseded and current corpus counts
in `DG-064` and `DG-065`; and keep `DG-066` as the separate historical
short-prefill diagnostic population. These are distinct registry roles, not a
single sensitivity series. Delete the old positive-width predicate as an
outcome criterion; if its artifact label is mentioned, call it an older
diagnostic label and state that it does not select the paper's result.

## 4. The resolution bound and how it is composed — frozen lines 109–114 — REWRITE

Begin with one physical record-clipping example in joules that shows why point
repeatability alone is insufficient, then name the two components: the absolute
component measures spread inside one model arm, and the comparative component
measures A/B/B/A block differences between arms. Define every symbol before its
first formula, define a resolution bound as the largest false difference the
cell permits, and state why the cell uses the larger component rather than their
sum. Introduce no campaign number here. This range consumes no fill row.

## A reproducible construction — frozen lines 115–190 — REWRITE

Build the method in this order: (1) clipping interval-average records to a
phase; (2) turning an allowed edge range into an energy interval; (3) the
absolute point-only formula; (4) the comparative A/B/B/A point-only formula;
(5) full corner re-evaluation of the same formula; (6) the independent-edge
ratio \(R\), its chosen twofold threshold, exact-equality passage, and
zero-denominator refusal; (7) the comparative shared/local replay and ratio
\(R_{cm}\), including why absolute \(R_{cm}\) is `not_applicable`; (8) the
small-sample multiplier, built from the 10-unit reference and \(n-1\) residual
degrees of freedom, and one-per-component whole-window allowance, built as the
maximum of named reference-run excursion and issued repeatability bound; and
(9) the cell maximum. Only after those safeguards and the two claim gates may
the text give A, evaluable-shortfall B, or the separate refusal disposition.
Give a real-number worked example for every mechanism, including the pilot
ratios and the retained replay fixture. Consume `DG-044`–`DG-052` and every
`R_*` and `R_cm_*` exact-token key. The old line-185 any-exceedance falsifier
and line-198 `fixed-p256` are not survivors.

## Two gates for a claim — frozen lines 191–211 — REWRITE

After the resolution calculation is complete, build Holm's fixed family of two
directional comparisons using token generation and the G2-a-selected prompt
length; state the ten block differences, Student-\(t\) statistic, two-sided
zero-mean null, and tail probability before Holm uses either probability.
Retain the missing comparison's stricter first slot rather than shrinking the
family. Then separate evidence exclusion, the magnitude gate against the final
cell floor, and the direction gate from the named measurement and decision
intervals and adjusted test. Work each gate with numbers and state that failure
to clear the floor means unresolved, not zero. Require Figure 3 here: its visual
elements are the evidence-exclusion path, magnitude path, direction path, both
intervals, both Holm thresholds, each stop, and all three close-out outcomes.
Consume `V5-G2A-001`, `DS-25`–`DS-33`, and `PG-01`, `PG-02`, `PG-04`–`PG-08`.
The line-210 zero-point fixture label is not a ratio result and must not survive
as one.

## 5. Collection stops when required evidence fails — frozen lines 212–215 — KEEP VERBATIM

## Measured admission rules — frozen lines 216–226 — KEEP VERBATIM

## Counterbalanced order — frozen lines 227–230 — KEEP VERBATIM

## Every input and every refusal remains visible — frozen lines 231–238 — KEEP WITH NAMED EDITS

Everything else in this range survives. Apply this edit only.

- Frozen quote:

  > The repository provides internal consistency and tamper evidence, not third-party provenance. It assumes a single trusted operator and no same-user program attempting to alter evidence; a known interval between checking a floor-specification path and authorizing it could let such a program alter the authorization record, although a precommitted fingerprint prevents the swap from altering a published number.

  Replacement:

  > The repository is tamper-evident for the operator's own benefit—a way to catch mistakes—not tamper-proof against another program or person. It assumes a single trusted operator, so its gates defend against error and post-hoc choice rather than an adversary; they provide internal consistency, not third-party provenance.

## 6. Demonstration results — frozen lines 239–240 — REWRITE

Open with the paper's three answer sets in this order: the boundary-doubling
result, the fixed Qwen3 pair as a demonstration of the rule, and the retained
short-prefill negative. State once that the pair is not a scaling experiment.
Consume the ratio keys, `DS-09`–`DS-33`, `PG-01`, `PG-02`,
`PG-04`–`PG-08`, and `DG-067`–`DG-077`, subject to each row's fill status.

## Results — frozen lines 241–244 — REWRITE

After data, write the null or exclusion row first. Then report the ratio table
component by component. Select outcome B only when every required ratio is
authenticated and evaluable and at least one is below 2. A missing,
unauthenticated, or zero-denominator required ratio selects neither branch,
stops filling, and prints its refusal reason; it is not an exclusion that may be
folded into B. Only then report the model-direction gates. Consume all eight
`R_*` keys, all four comparative `R_cm_*_cmp` keys, the four absolute
`R_cm_*_abs` not-applicable keys, and `DS-25`–`DS-33` plus `PG-01`, `PG-02`,
`PG-04`–`PG-08`, rendering every `STOP_FILL` placement with its exact omission
sentence.

## Printed negative result: short prompt processing is not resolvable — frozen lines 245–257 — REWRITE

Build the overlap rule from record supports before the 37-of-50 count: clip
each record's time interval to prompt processing and count records with
positive overlap; fewer than three refuses the phase. Then state that 37 of 50
retained short-prompt phases had two overlaps and 13 had three, without naming
the superseded Qwen2.5 pair as the successor demonstration. In the worked
bundle, state that the retained records tile without a meaningful pause;
record width and start-to-start spacing describe the same record-period
distribution apart from endpoint convention, so duration divided by a nominal
period cannot replace the overlap count. Require a diagram showing the record
supports, the prefill interval, and the marked two- and three-overlap counts.
Consume `DG-067`–`DG-077`; render `DG-071` and `DG-075` with their exact
registered omission sentences until their path- and SHA-pinned statistic
artifacts issue.

## Demonstration fixed before collection — frozen lines 258–265 — REWRITE

Name condition A as Qwen3-1.7B and condition B as Qwen3-8B only after the
fixed pair is identified. Then build the A/B/B/A difference and positive-sign
meaning, the real eight-prompt token-generation arm, the shared tokenizer and
chat-template fingerprints, reasoning mode off, greedy choice, forced 512
output tokens, the selected prefill length, ten blocks, and the unchanged
two-comparison Holm family. Consume `V5-ID-001`, `V5-ID-002`,
`V5-WL-001`–`V5-WL-005`, `V5-G2A-001`, and `DS-25`/`PG-01` only where
the result itself is later stated.

## Why 256 prompt tokens were selected — frozen lines 266–291 — REWRITE

Retitle this subsection so it says the selected prompt length is not yet stated
and carries the exact `V5-G2A-001` omission sentence beside that marker.
Build the G2-a rule before the selected rung: test 512, 1024, 2048, and 4096
in that order with at least five Qwen3-1.7B probes per rung; a rung passes only
when every small-model probe overlaps at least five records; five is a chosen
two-record safety margin above the reducer minimum of three. Give the worked
passing counts 5/6/7/5/8 and failing counts 5/6/4/7/8. Explain that Qwen3-8B is
probed to reveal whether the larger model changes resolvability but does not
select the rung. The shortest passing rung is selected; if none passes, collect
at 4096 and distinguish a reducer refusal below three from a calculable count
of three or four that misses the fixed-before-collection five-record design
floor. Then build fresh Tables 2 and 3 from the registry rather than preserving
the old 256-token projection. Consume `V5-G2A-001`, `V5-WL-005`, `DS-09`–
`DS-33`, `PG-01`, `PG-02`, and `PG-04`–`PG-08`, rendering G2-a and prompt-pin
holds with their exact registered omissions; never consume retired sizing rows
`DG-078`–`DG-097` as successor results.

## 7. Discussion and limitations — frozen lines 292–295 — REWRITE

Write this after the campaign and transfer fiducial. Start with the selected
ratio branch, or state the separate no-branch refusal that stops filling; then
say exactly what the fixed Qwen3 demonstration does and does not show, and
finally state whether the post-campaign gap fiducial supports or weakens transfer
of the pulse-derived edge bound. Consume the ratio keys and the future
transfer-fiducial result only after it issues; consume no superseded `_v4` row.

## What the finding changes — frozen lines 296–305 — REWRITE

Explain the practical consequence only for cells satisfying the all-ratios
rule: more repeats reduce point scatter but do not remove a boundary
contribution that at least doubled the point-only component. Report pilot
ratios separately from `_v5` ratios, explain why the fixed model pair is a
decision-rule demonstration rather than a scaling curve, and preserve
component-specific failures or exclusions. Consume `DG-050`–`DG-052`, the
`_v5` ratio keys, and `DS-25`–`DS-33`/`PG-01`–`PG-08` where fillable.

## Further limitations — frozen lines 306–311 — REWRITE

Order limitations by threat to the headline: pulse-to-inference transfer;
one machine and one software/counter boundary; internal counter joules without
an external gain check; dependence among ten blocks in one window; absence of
independent floor re-reduction; and trusted-operator rather than adversarial
provenance. For each, state what physical uncertainty remains and what evidence
would close it. Consume `DS-34` only for release status.

## Future work — frozen lines 312–319 — REWRITE

Lead with the inserted approximately 500-ms gap fiducial because it tests the
headline transfer assumption. Then name external-meter gain checking and
another-machine replication. Keep characterization and other research-bank
questions explicitly outside this paper's answer set. Use `_v5` consistently;
consume no campaign result row.

## 8. Related work — frozen lines 320–321 — KEEP VERBATIM

## From counter gain to counter time — frozen lines 322–327 — KEEP WITH NAMED EDITS

Everything else survives. Apply these three edits only.

1. Frozen quote:

   > Khan et al.'s *RAPL in Action* and Jay et al. own the gain axis: how accurately a software counter reports the magnitude of energy use [5] [6].

   Replacement:

   > Running Average Power Limit (RAPL) is a processor-exposed energy counter. Khan et al.'s *RAPL in Action* and Jay et al. own the gain axis: how accurately a software counter reports the magnitude of energy use [5] [6].

2. Frozen quote:

   > Across RAPL and NVML, they show that counter-update behavior and requested sampling frequency can materially change an energy reading; on one evaluated GPU, very frequent polling severely underestimated integrated power, with agreement recovering only at a much longer interval [23].

   Replacement:

   > Across RAPL and the NVIDIA Management Library (NVML) software power counter, they show that counter-update behavior and requested sampling frequency can materially change an energy reading; on one evaluated GPU, very frequent polling severely underestimated integrated power, with agreement recovering only at a much longer interval [23].

3. Delete this frozen sentence without replacement because Section 7 owns the
   limitation:

> The calibration uses commanded GPU pulses under a lighter CPU regime, however, and this capstone does not test whether its timing bound transfers unchanged to sustained mixed inference load (Section 7).

## LLM energy measurement — frozen lines 328–333 — KEEP VERBATIM

## Benchmark and metrology lineage — frozen lines 334–345 — KEEP VERBATIM

## 9. Evidence and code availability — frozen lines 346–353 — REWRITE

After release, name the repository revision, evidence archive, and fingerprint
manifest first. Then explain independent re-reduction in physical order: start
from released primary bytes and the fixed manifest, reconstruct every admitted
member and timing width, compare the complete set with the floor artifact, and
refuse before analysis if any member or width differs. State the present
limitation plainly if that consumer is still absent. Consume `DS-34`; no
placeholder may be replaced from prose or a nearby path.

## 10. Conclusion — frozen lines 354–359 — REWRITE

Write this last. In order, give the selected exact ratio branch sentence or the
separate no-branch refusal, the fixed Qwen3 demonstration decision without
scaling language, the retained 37-of-50 negative, the transfer-fiducial
condition on the headline, and the one-machine/counter boundary. Consume the
ratio keys, `DS-25`–`DS-33`, `PG-01`, `PG-02`, `PG-04`–`PG-08`, and
`DG-067`–`DG-069` only where authenticated and fillable; use exact omission
sentences for `STOP_FILL` rows.

## 11. References — frozen lines 360–393 — REWRITE

Build the bibliography from citations that survive the newly written paper,
remove orphan entries, verify every retained locator against its source, add
only sources actually used to build a mechanism or comparison, and renumber
after prose is final. This section consumes no result-fill row.

## Appendix A. Reproducing this work — frozen lines 394–399 — KEEP VERBATIM

## A.1 What a reader needs — frozen lines 400–405 — KEEP VERBATIM

## A.2 Scientific artifacts and their bindings — frozen lines 406–416 — KEEP VERBATIM

## A.3 Formal calibration algorithms — frozen lines 417–422 — KEEP VERBATIM

## A.3.1 The objects the algorithms operate on — frozen lines 423–451 — KEEP VERBATIM

## A.3.2 The capture procedure — frozen lines 452–468 — KEEP VERBATIM

## A.3.3 The clock-anchor estimator — frozen lines 469–558 — KEEP VERBATIM

## A.3.4 Placing the trace on the wall clock, trimming warm-ups, and authenticating the schedule — frozen lines 559–568 — KEEP VERBATIM

## A.3.5 The pulse-fit (accepted-region) algorithm — frozen lines 569–641 — KEEP WITH NAMED EDITS

Everything else survives verbatim. Apply these two edits only.

- Frozen quote:

  > `#### A.3.5 The pulse-fit (accepted-region) algorithm`

  Replacement:

  > `#### A.3.5 The pulse-fit algorithm`

- Frozen quote:

  > `**The accepted region.** The fitted point is not the output. Define the **loss limit**`

  Replacement:

  > `**The set of acceptable edge pairs.** The fitted point is not the output. Define the **loss limit**`

## A.3.6 The calibration bound B_fiducial and validity — frozen lines 642–653 — KEEP WITH NAMED EDITS

Everything else survives. Apply this edit only.

- Frozen quote:

  > Because the bound is the sample maximum over 59 draws from it, it is a "95/95" bound: with at least 95 % confidence it exceeds at least 95 % of that distribution (the probability that all 59 draws fall below the 95th percentile is 0.95⁵⁹ ≈ 0.048, so 1 − 0.95⁵⁹ ≥ 0.95). It is not a deterministic out-of-sample guarantee.

  Replacement:

  > The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions from 59 commanded pulses in one capture; the clock-anchor allowance is then added. Because those pulses share one capture and independence across pulse order and between onset and offset errors has not been shown, this value is an observed sample maximum, not a “95/95” population-coverage bound. It is not a deterministic out-of-sample guarantee.

## A.3.7 The work budget and the 120 s work clock — frozen lines 654–659 — KEEP VERBATIM

## A.4 Executable verification order — frozen lines 660–663 — KEEP VERBATIM

## A.5 Interpreting a refusal — frozen lines 664–669 — KEEP VERBATIM

## A.6 Release locators — frozen lines 670–672 — REWRITE

After the release checklist issues, print the repository revision, archive
locator, and fingerprint-manifest locator, and state which evidence-dependent
commands are now independently runnable. Until then, retain an explicit
release refusal keyed to `DS-34`; do not predict future issuance.

## Mandatory defect and survivor census

These frozen-draft sites must not survive outside frozen-quote evidence:

- **Retired headline falsifier:** line 21 (“does not exceed”), line 185 (the
  exact linear corner maximum versus guarded point value), and line 356
  (“contributes more than repeatability”). All are replaced by the complete
  unguarded full-corner ratio \(R\), the twofold threshold, and the mandatory
  comparative \(R_{cm}\) check.
- **Retired fixed prompt arm:** line 198 `fixed-p256`; line 260 “256-token
  prefill arm”; and the entire line-266–272 “Why 256 prompt tokens” rationale.
  D-166's four-rung G2-a rule replaces them.
- **False sampler mechanism:** line 256 says record spacing is longer because
  the sampler pauses. Retained evidence shows records tile without a meaningful
  pause; width and start spacing describe the same record-period distribution
  apart from endpoint convention.
- **`_v4` hits:** lines **2, 7, 80, 164, 294, 314, 356, and 358**. Line 314
  contains two occurrences. No successor prose may retain one.
- **`Qwen2.5` hits:** lines **247 and 260**. Line 247 remains historical
  evidence but is rewritten without using the superseded pair as the
  successor demonstration; line 260 becomes the fixed Qwen3 pair.
- **Related retired size labels:** `1.5B`/`7B` result-bearing hits at lines
  **247, 260, 268, 280–283, 289–290, and 356**. The 256-token
  characterization level at line 94, SHA-256, and the \(4096\times4096\)
  pulse matrix are not prompt-arm survivors.

## Audit-ledger rule

At fill time, use `structural-edits.md`, `retensing-plan.md`,
`fill-checklist.md`, and `results-fill-registry.md` only to audit the fresh
successor prose. They may prove that a required concept, branch, token, or
refusal is present; they must not mechanically generate sentences. Before any
result paragraph is accepted, check every registry slot against its current
status, every branch against the authenticated predicate, and every frozen
defect above against a concept-keyed search rather than a spelling-only search.
