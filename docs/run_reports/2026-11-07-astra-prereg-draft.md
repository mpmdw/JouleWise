# ASTRA-2CH preregistration draft — 2026-11-07

Status: desk deliverable complete; **DRAFT, NOT REGISTERED**, no live validation.
Task: `astra-prereg`. Branch: `interp/2026-11-07-astra-prereg`, already checked
out and clean at intake; starting HEAD `3edb715df`. This report does not
register a kernel task, authorize collection, or change project coordination.

## Intake and scope

Read the interp × energy design study and relevant companion checks, then
local AGENTS/CLAUDE, Mission M0, the generated stop/restart pointers, targeted
Current Project Status / Known Workspace State, Current Queue and
Do-Not-Do-Yet sections, the source-of-truth map, and orchestration conventions.
The generated stop card says NONE. The generated lane heads concern other
work; explicit user direction selects this bounded desk task under M0. The
current branch/status, not historical workspace prose, supplies the working
tree state. Registration examples read were the BYTES known-bytes draft,
block 6, difficulty v2, and targeted block-5 registration/analysis sections;
measurement/analysis contracts and D-078 supply the relevant soundness rules.

The user's task explicitly overrides coordination bookkeeping and the full
suite: no edits to RUN_STATE.md, TASK_QUEUE.md, state_kernel.json, or
tests/test_gen_state.py; no kernel task registered. No code or empty package
was added because this brief's deliverables are two Markdown drafts. No
external skill files or services were accessed. No subagents or cross-model
consults were launched; this draft still needs the lead's review and any
independent registration review the lead requires.

## Changes and reasoning

- [Registration draft](../registrations/astra_2ch_v0_draft.md): proposed P/F/T
  blocks; 40 problems and four free-running arms (base-on, edited-on,
  base-off, base-on/8k); 12 edited-reference replay clusters with ABBA/BAAB
  and A/A′; whole-MLP bf16-zero sensitivity control; synthetic GEMM and
  ≥1 GB ring-GEMV ladder. Declares estimands, boundaries, exclusions,
  custody, stopping, deviations, and seven open decision/evidence slots.
- [Analysis draft](../analysis/astra_2ch/ANALYSIS-PLAN-v0-draft.md): EPC as
  total joules divided by total successes; problem-level uncertainty with
  explicit zero-success/infinite outcomes; equal-reference replay contrast,
  conservative systematic propagation, local floor gates, ±0.1% DC TOST,
  and wider absolute-magnitude confidence bounds when equivalence is not
  established. Includes registry rows, instrument classes, and an independent
  token/context calibration plan.
- This run report is the third added file. No existing files were changed.

The study's noise figures are labelled transferred planning anchors, not
ASTRA calibration. KM003C DC plus signed battery assist is authoritative
for small whole-machine effects; fine rail precision cannot substitute for
DC. DC-only response is consistent with either off-rail energy or rail
insensitivity, not proof of Apple's implementation. No detection does not
mean equivalence. A replay bound describes the mean contrast on the selected
references, not a universal per-weight or per-sequence limit.

F-EPC is a primary **estimation** target, without a superiority test in this
small pilot. The sole proposed confirmatory test is T-DC equivalence
(Holm m=1, TOST alpha=.05, widened 90% interval; also print 95% bounds).
Secondary comparisons remain descriptive. These are draft choices for lead
review, not newly adopted project policy. The analysis also explains why
subtracting T directly from free-running F is not an exact causal channel
decomposition: procedure and reference distributions differ.

## Verification

- `python3 -B - <<'PY' ... PY` — focused, standard-library static check of
  the two requested drafts: **PASS**. Checked DRAFT/NOT REGISTERED status,
  trailing whitespace/newlines, all eight local Markdown links, valid
  A-1…A-7 references and all seven registration decision rows, one F0–F3 arm
  each, D−1 decode convention, the sole TOST family/margin, the four non-null
  P contrasts, and the synthetic interval arithmetic (−0.068%, +0.072%,
  absolute bound 0.072%). Only these documents and their in-repository link
  destinations were inspected by that check. This is document QA, not a
  test of a reducer or native measurement pipeline.
- The first version of that temporary checker incorrectly required each
  document to spell out all seven slot IDs individually. The analysis plan
  refers to the inclusive A-1 through A-7 range. Corrected the checker to
  validate the actual slot/reference convention; the drafts did not need a
  change for that failed assertion. A later table checker initially assumed
  too few columns for the four-column arm table; corrected it to compare
  each table's rows against its own header. Final checks passed, including
  whitespace, local links, fences and table structure across all three files.
- `git diff --check` and final staged whitespace/scope review: **PASS**.
  Only the two drafts and this report are in the delivery.
- No unittest module or compileall was run: no Python code changed. The
  full suite was expressly prohibited while the existing 8-worker blinded
  job runs. Static checks completed in under a second of command runtime.
- No network, downloads, model weights, real measurement inputs, hardware
  captures, Block 5 analysis pipeline, or real restricted directories were
  accessed. No existing process/job was stopped or changed. No push.

Commit: the local documentation commit containing this report and both
drafts, message `docs: draft ASTRA-2CH preregistration and analysis plan`.
Its hash is reported in the final handoff; it is intentionally not
self-referenced inside the commit.

## Open questions, uncertainty, and exact next step

Lead: review the proposed estimand/test distinction, edited-reference
selection, cap scoring rule, sparse-success interval treatment, null-bias
gate, and local calibration design; disposition the seven open slots in
registration §8. Ed owns permission to obtain the base/edit artifacts and
Mac windows/priorities. Lead owns source/license/hash verification, runtime
compatibility, acceptance thresholds and final registration/seal. The
native DC precision and total runtime remain unknown; a 12-reference design
may yield only a substantially wider bound than ±0.1%. The study's runtime
estimate must be redone including all A/A′ quads, controls and admission
overheads. No independent literature/provenance check was attempted under
the no-network rule, so source novelty and artifact claims remain as reported
by the study, not newly verified facts.

Outside this sandbox and only after authorization, the lead must run native
MLX checks for dense hybrid load, actual bf16 edit changes/hashes, A/A′
deterministic outputs, forced-token identity, KV **and recurrent** resets,
single-token decode counts, swap/compile behavior, kernel/residency and
meter/clock/battery cases. A disjoint software smoke precedes scored work.
Local noise/admission calibration and energy collection require a separate
clean, lead-controlled quiet window with no active agents. This task adds no
MLX tests; there is no invented native test command to report as passing.

Next exact step: lead desk-review of the two drafts and disposition of
OPEN[A-1]…OPEN[A-7]; then prospectively pin the approved design and native
validation kit. Keep this version labelled DRAFT until those gates close.
