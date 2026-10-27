# Tier E (last resort): the method and diagnostic paper with the automation pipeline

<!-- Use only when the primary-block release itself slips past about 20 November. Decided by date, not by any
result. This version reports no new energy result. It keeps §2 (related work), §3 (method), §4 (design), §6.1 to
§6.4 (BYTES design), §7 (automation) and §8 (limitations) of ../paper1.md, and replaces the title, abstract,
§1.3, §5, §6.5 and §9. The historical diagnostics come from the merged methods draft
(docs/paper/draft-v2-skeleton.md) and are bound by their existing registry rows. -->

# Dividing a Laptop's Inference Energy Between Phases: A Pre-registered Method, Its Historical Diagnostics, and the Automated Pipeline That Runs It

## Abstract (replaces)

Language-model inference has two phases, prefill and decode, and a laptop's own power sampler reports the
processor's average power over records of roughly a tenth of a second that do not line up with the boundary
between them. We specify how such records can be divided between the phases and how every source of timing
uncertainty enters the result: in-session GPU-pulse calibration, a rate-aware clock mapping, an attribution floor,
a detection floor with timing-widened corners, a dominance ratio that asks whether timing or repeatability limits
the measurement, and a drift allowance from reference requests. We demonstrate the calculations on synthetic
inputs and on historical captures from one Apple M3 Max laptop, where {{FILL: DX-012 | historical fitted onsets later than their commands}} of 59
fitted pulse onsets occurred after their commands and a three-record minimum refused {{FILL: DG-067 | historical short prefill phases with two records}} of
{{FILL: DG-068 | historical population size}} short prefill phases. We describe two pre-registered, blinded measurement campaigns built on the method, a
two-model phase-energy study with a replication and a test of whether decode energy per token follows bytes read,
resident size or decode time, both collected and awaiting release. Finally we describe the agent-driven pipeline
that designed, collected and audited them, its integrity controls and its failures. This paper reports no new
model-energy comparison.

## §1.3, Contributions (replaces)

1. The phase-attribution method with explicit limits (Section 3), demonstrated on synthetic inputs and historical
   captures (Appendix B).
2. Two registered, blinded experimental designs, collected to their registered ends, whose every output sentence
   was fixed before data (Sections 4 and 6.1 to 6.4).
3. An account of research run by AI agents, with its controls and failures (Section 7).

## §5 (replaces the section)

### 5. Status of the registered campaigns

The primary block, the replication block and BYTES were collected under their registrations
({{FILL: P1-E-STRUCT | per campaign and pack: sessions attempted and counting, cause families, kept-unit counts; structure only}}). Their energies remain blinded and have been read by no person or agent. The release
of each follows its registered conditions: the blind dry run, the release event and the independent
recomputation's agreement for Part 1; the stage-1 commitment and stage-2 release for BYTES. Every number they will
print, and every sentence under each outcome, is fixed in the registrations; the results sections of the full
paper are written as templates bound to those fields and will be released as a companion paper.

### 5.1 Historical diagnostics

{{FILL: P1-E-HIST | the historical edge-excursion and record-support results of the merged methods draft (Section 4 of docs/paper/draft-v2-skeleton.md), bound to registry rows DX-001/003/010-013 and DG-067-069/072/073/135-144, reproduced with their existing caveats: diagnostic-era captures, energies voided for claims, one capture, dependent edges}}

### 5.2 Synthetic demonstrations

The worked synthetic examples of Section 3 (overlap, first-kind bound, reported-energy interval, floors and the
dominance ratio), the two-block shared-sign fixture and the partial-record enclosure of the merged methods draft
are reproducible from the repository without any raw capture.

## §6.5 (replaces)

BYTES is reported as a registered design (Tier D, branch D.1 wording).

## §9, Conclusion (replaces)

A laptop's own power sampler can divide inference energy between phases only within limits the measurement must
report. We specified those limits, showed on historical captures why they bite, registered two experiments that
measure them under blinding and independent recomputation, and described an agent-driven pipeline whose mechanical
controls, more than any agent's judgment, protected those experiments. Their results will follow.
