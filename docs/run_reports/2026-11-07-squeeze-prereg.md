# squeeze-prereg desk handoff — 2026-11-07

Status: draft delivered for lead review; no registration, data access or live
qualification. Branch: `align/2026-11-07-squeeze-prereg` (already checked out at
intake). Base: `fdb1e0409784096b1bfffbeea92d4e3d09a02ce0`; initial tree clean.

## Intake and authority

Read repository AGENTS/CLAUDE conventions, Mission M0, targeted stop-card,
status/workspace and queue/do-not-do sections, the authority map, orchestration
roles/review/write rules, analysis-plan contract and D-043/D-062/D-078 context.
No stop card was active. Classified the brief as explicitly selected [AGENT]
research documentation; it does not select a machine-state measurement lane.
The user’s specific instruction forbids coordination-state changes, so no
RUN_STATE, TASK_QUEUE, kernel, generated state or status file was edited and no
task was registered. Handoff lives here as requested.

Read AGENDA and the Energy Tripwire page in this clone, plus protocol v4 and
energy_residual from local `origin/lane/2026-11-06-v4-r1-integrated`. Read the
literature, W1 pre-arm and research-program audit syntheses from their named
local research refs. The addendum records immutable full commit pins. Item
204 of the local RUN_STATE settles Q4/Q6 and supersedes the older audits’
open approval questions; Q6 was not reopened.

The brief asks for a fetch but also forbids network access. No fetch/network
request ran; all required refs were already available. Ref freshness beyond
these local snapshots is unverified. No external path named in source prose
was followed. No real restricted directory, sealed outcome, measurement bundle
or running job was inspected. Git object reads may use the allowed shared
alternate store. No model was downloaded or loaded.

## Deliverable and findings

Added `docs/registrations/align_v4_squeeze_addendum_DRAFT.md`:

- Non-adaptive, padding, smoothing, timing, tool-shifting and mixed strategies;
  bounded development feedback; a separate real-compute positive-control class.
- Explicit log-forgery permissions, trusted DC/battery/span boundary, detector
  views, independent execution truth, separate configuration/pair cohorts,
  seed roles, blinding and failure accounting.
- Energy/transcript solo and OR/AND estimands. Composite max/min rules have a
  common marginal false-alarm budget; literal OR/AND are also printed with
  their different bounds. No channel-independence assumption is used.
- Escape probability and surviving hidden-token mass; fixed sample/stopping
  proposals; multiplicity/dependence caveats; holds/fails/unresolved criteria;
  deviations and a lead/Ed decision table, with v4 section citations.

At m=39 the sample-max marginal bound is 2.5% per calibrated rule; literal
solo-alarm OR has a 5% union bound. The realized-tail 90% upper tolerance bound
is approximately 5.73%, so the draft does not promise a realized 2.5% FPR.
The paired composite rules differ from literal Boolean combinations and are
labelled explicitly.

The full proposed design has 1,398 eligible episode captures per configuration,
including 720 primary attacks (six families × two pairs × 60). At 1,800 s per
D member it reserves 699 science-member hours before scaffolding, probes or
invalid attempts. This is an illustrative precision-driven reservation, not
a feasible calendar or a power guarantee. No existing D-window capacity is
implicitly expanded. With zero escapes, the simultaneous two-sided 95%
12-cell Bonferroni upper endpoint is 0.0978; dependence may make the proposed
10% ceiling unresolved even then.

## Verification

Docs-only: no runtime, MLX code, test module or measurement configuration changed.
No unittest module, full suite, sharded suite, pipeline or compileall was run;
there is no executable change to exercise, and the user forbids the full suite
while the separate blinded job runs. Cheap, single-process checks only:

- `python3.13 -B -` with a standard-library inline document audit: passed source
  object/section existence, sample-table total, false-alarm arithmetic,
  zero-escape interval arithmetic, required scope/content markers, balanced
  Markdown fences and protected-path change checks. No data dependencies.
- `git diff --cached --check`: passed for both added Markdown files.
- Final staged diff read: the addendum and this report only; coordination state
  and all pre-existing files preserved.

The first ad hoc audit included an incorrect extra assertion that n=59 could
not clear the 0.10 zero-escape ceiling; its upper endpoint is about 0.09935.
Removed that unsupported minimal-n assertion and reran the audit. The draft
proposes n=60 and never claims it is the mathematical minimum; its arithmetic
was unchanged.

The author reviewed the final text. No independent reviewer or registration
cold gate ran; those remain lead-owned and are not represented as completed.
There was no delegated agent or external consult. The document checks found
no result-bearing code defect; they verified draft arithmetic and provenance.

## Open decisions and uncertainty

1. Ed/lead must choose full confirmatory capacity or a smaller feasibility
   design, and accept/change the proposed H=1,024 / escape≤0.10 criterion.
2. Freeze actual monitor identity/prompt/view, reported-log forgery rights,
   DC/battery/span semantics, score transforms, injection implementation and
   adaptation budget. Plausible padding can defeat both channels; a squeeze
   is a hypothesis, not an established consequence of metering.
3. The split-fit/calibration estimator is a proposed departure from v4’s
   per-session analysis. Its exchangeability assumptions, window dependence,
   cluster sensitivity and physical-PC uncertainty bar require scientific
   review; no finite-sample guarantee under arbitrary drift is claimed.
4. Resolve reserve-attempt authority against v4’s no-replacement policy, pin
   the admitted configuration/seed tag and complete the manifest/time cap.
   D and 30B results cannot be pooled to clear a gate.
5. Controlled injected work tests detection; it does not prove autonomous
   sabotage adds compute or that every form of hidden computation is caught.
   Injection-mode mixture results do not establish mode-wise robustness.

Native tests for this change: none were added because the change is prose.
Before executing the future study, the lead must run the owning protocol’s
R0/R1/W1 native qualifications outside this sandbox and validate real MLX
hidden-work execution/synchronization, identical visible PC replays, correct
tool/span ownership, trusted DC/clock/battery custody and monitor-input
separation. The implementation and native test commands do not yet exist for
this addendum; do not treat its arithmetic checks as MLX/hardware evidence.
No live gate can run from this active agent session.

Next exact step: review addendum §9’s owner/decision table, disposition its
proposals and capacity, then commission implementation/independent registration
review at the resulting frozen specification. This draft authorizes no arm.

## Commit

Local commit message: `docs(align): draft v4 monitor-energy squeeze preregistration`.
The commit contains only the two new Markdown files named above. No push,
merge or publication is authorized or performed.
