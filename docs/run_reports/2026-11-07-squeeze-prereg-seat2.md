# Independent squeeze preregistration draft — seat 2

Date: 2026-11-07. Branch: `align/2026-11-07-squeeze-prereg-seat2`.
Starting HEAD: `be3cc8b680cde290299aeb8d198de73993fe38b2`.
Status: DESK DRAFT delivered for lead/Ed adjudication; no registration or
hardware validation. The requested branch already existed and was checked
out, with a clean worktree. No branch recreation was necessary.

## Delivered

[The addendum](../registrations/align_v4_squeeze_addendum_DRAFT_seat2.md)
defines the non-adaptive, padding, smoothing, timing, tool-shift, mixed and
physical-positive-control classes; paired joint detection and hidden-work
survival estimands; calibrated energy/transcript/OR/AND rules; independent
fit/calibration/test cohorts; sample sizes, seeds, blinding, stopping,
decision rules, deviations and an explicit lead/Ed decision table.

The draft makes several consequential distinctions:

- Separate 2.5% single-channel calibrations give a simple OR ceiling of 5%.
  A separately calibrated joint max/min score compares four rules at a
  common 2.5% marginal ceiling, without assuming channel independence.
- A calibration maximum has a rank guarantee only under exchangeability
  with the new benign score. Original leave-one-trajectory-out calibration
  and full-fit test scoring do not automatically meet that requirement.
  Independent fit/calibration/test scoring is a proposed V4 amendment.
- At m=39 the marginal bound is 2.5%, while the iid continuous-score 90%
  upper bound for the realized tail of a particular maximum is about 5.73%.
- Edited logs do not demonstrate physical hidden work. D-model injected
  compute is a gate; 30B controls must be calibrated and labelled separately.
- The 60-carrier candidate can clear a simultaneous 10% survival ceiling
  with zero escapes, but can have poor joint power. Its 1,118 core episodes
  and independence assumptions require a budget and science ruling. A
  conservative independent-window alternative needs at least 53 independent
  windows per cell in the zero-escape case; six windows cannot establish it.
- The squeeze is a hypothesis. A positive result has explicit dose,
  logging-contract, privilege, task, configuration and adaptive-budget limits.

## Intake, authority and independence

Read AGENTS.md, CLAUDE.md, AGENT_PLAN.md, Mission M0, the applicable
orchestration sections, generated stop/restart and queue intake sections,
Known Workspace State, relevant D-038/D-050/D-053/D-054/D-062 entries, and
the analysis-plan contract. No active stop card was present. This explicit
user-assigned documentation task outranked the ordinary generated restart
pointers. Queue/kernel changes were prohibited by the brief and were not
made; this report records intake instead.

Required substantive sources were the current agenda/research map and
existing local refs for V4 plus energy_residual, literature, W1 pre-arm gate,
and research-program audits. Their exact commits and relevant sections are
in the addendum's source table. Historical recommendations in the audits
were distinguished from Ed's later adaptive-squeeze direction.

No fetch was attempted: the brief's no-network rule took precedence over its
fetch request. All required named refs were available locally, but freshness
beyond those local objects was not verified. No content from branch
`align/2026-11-07-squeeze-prereg` was inspected. No peer was invoked and no
independent review or lead approval is claimed for this seat's draft.

No real restricted path or external /Users/edr path was deliberately opened,
listed or searched; allowed shared Git objects were accessed through Git.
Absolute data-path references in repository text were not followed. No
Block-5 pipeline, measurement data, model weights, quiet measurement,
process inspection/control, network access, push or deployment was used.
The running blinded analysis job was not inspected or controlled.

## Files changed

Only these two new documentation files:

- `docs/registrations/align_v4_squeeze_addendum_DRAFT_seat2.md`
- `docs/run_reports/2026-11-07-squeeze-prereg-seat2.md`

RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json,
tests/test_gen_state.py and all source/test files were left untouched. No
coordination task or registration was created.

## Verification

Documentation-only verification; no unittest module, compileall, full suite,
MLX import or native model execution was needed or run. This also respected
the running-job restriction and avoided unnecessary CPU load.

- `python3.13 -B - <<'PY' ... PY`: PASS (exit 0, under one second).
  Inline stdlib assertions checked ten numbered sections, required threat
  and outcome coverage, cohort totals, runtime-cap arithmetic, rank/FPR
  arithmetic, zero-survivor confidence bounds, minimum n and exact-binomial
  per-cell operating characteristics. Markdown links were checked against
  local files or `git cat-file -e <commit>:<path>`; no network resolution.
  The final run covered ten draft/report links. One intermediate checker
  failed because its whitespace regex matched blank lines; the corrected
  spaces/tabs-only check passed, without requiring a document change.
- Final staged `git diff --cached --check`: PASS.
- Final staged path review and content review: only the two listed Markdown
  files, with all new scientific choices marked as proposals. Arithmetic
  review corrected the minimum independent zero-escape n from 54 to 53 and
  called out the candidate's low-power limitation.

These are document consistency and arithmetic checks, not statistical-code,
monitor, injector, meter, MLX or live-hardware verification. The inline check
was ephemeral; no implementation tests were added for this reversible draft.

## Unresolved decisions and next exact step

The addendum's final table is the actionable ruling list. In particular,
the lead/Ed must choose logging permissions, adversary feedback/search budget,
DC boundaries, monitor and visible inputs, deployment-fit versus session
calibration, independent unit, affordable sample sizes, H*/survival/utility
margins, replacement authority and D-model positive controls. No current-head
readiness conclusion follows from the historical W1 audit.

Next: compare the two independent preregistration proposals, adjudicate those
choices, then commission a reconciled candidate and blind synthetic operating
characteristics before freezing any cohort. The lead retains final review,
registration, public deviation entries and all native/hardware gates.

Outside this sandbox, the eventual implementation needs native D-model MLX
injector checks (real execution and exact dose witnesses), public-log/monitor
leakage and truncation checks, externally metered envelope/battery/timing
qualification, seed/configuration identity, and installed parent instrument
and cold-registration gates. No native test module is named here because no
MLX code or tests were authored; its owners must supply the exact commands.

## Local commit handoff

This report and the draft are committed together with message
`docs(align): draft independent seat-2 squeeze preregistration`.
The resulting commit ID is supplied in the final handoff; it cannot be
embedded in its own committed report. No push is authorized or performed.
