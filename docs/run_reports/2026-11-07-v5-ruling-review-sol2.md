# v5 ruling review — Sol2 run record

Recorded on the workspace date, 2026-11-07; the supplied brief and source draft
are dated 2026-11-08. Task: `v5-ruling-review`. Seat: **sol2**.

## Result and changed files

**SIGN_WITH_CHANGES.** Delivered the independent review at
[`ruling-review-sol2.md`](../align/squeeze/v5-design/ruling-review-sol2.md).
This run report and that review are the only intended changes. The ruling
itself, coordination state, source code, tests and historical evidence remain
untouched.

The supplied review branch was already provisioned and clean at intake:
`align/2026-11-08-v5design-ruling-review-sol2`, based on
`18f35ae066270cc44de52830a97f6004d4eee6ec`. No alternate branch was substituted.
The user explicitly authorizes a local commit; no push is authorized or made.

## Intake, scope, and evidence

Read repository AGENTS/CLAUDE conventions, Mission M0, targeted restart/stop-card
and queue/do-not-do-yet sections, source-of-truth map, orchestration, D-050 and
analysis-plan policy. No active stop card was present. The explicit docs-only
review takes precedence over stale next-work pointers. Per the binding brief,
RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json and tests/test_gen_state.py
were not edited and no kernel task was registered.

Used `git show <ref>:<path>` for the draft, all six seats' targeted relevant
sections, both judges, AGREEMENT-FINAL, main items 210/212/213, and PR #703's
tripwire-directions document. Immutable commits and line evidence are in the
review's source table. The draft SHA-256 is
`6d3e9605cb6b5209e36d84cd52021010d524ff8bcfb92abac2357c820e72c887`;
the agreement SHA-256 is
`75734be4601bb87c403a6ef1d212a53f8b6b33a0648afd5ee7e4dcde74a539c8`.
Cached-ref freshness was not checked against a remote. Git object access through
the allowed shared alternate was used only as normal Git repository access.

No agent was spawned or consulted. This is one independent Sol seat, not an
agreement or a self-attestation of two reviews. No model/effort override was
requested or inferred. The session identifier is not exposed by this interface;
none is invented. Lead disposition and rework time remain pending.

## Verification and catches

`python3.13 -B -` with an inline stdlib-only script **passed**. The script used
literal planning counts and arithmetic, with no project imports or file/data
loads. Assertions checked the 1,980-member sum, 768-hour base-case reserve,
704 necessary calibration/test software reruns, and a concrete seven-date
whole-window-loss example. Additional output reproduced all timing scenarios,
calendar spans, storage proxies, local scoring time and a clearly hypothetical
independent-attrition calculation. Numeric outputs and formulas are quoted in
the review, so no ephemeral script is required to interpret the findings.

`git diff --cached --check` **passed**. A separate `python3.13 -B -`
documentation/scope check **passed**: all 12 pinned source objects exist, the
handoff link resolves, and the staged paths are exactly the two authorized
Markdown deliverables. The final diff was read by this seat before commit;
the lead's independent disposition is still pending.

| Check | Finding affecting a number or claim |
|---|---|
| R11/D09 clause comparison | The draft adds a main-utility conjunction to the primary escape event. |
| Calibration roster/loss arithmetic | 44/pair cannot survive one ordinary loss among seven calibration dates while retaining 39. |
| Software-rerun census | 88+280+336=704, not the inherited 694. |
| Calendar arithmetic | Dec 7 leaves 84 days; reserved 1,200-s test phase needs 43.60 productive 16-hour days before batch overhead, beyond its 41-day tail. |
| Multiplicity contract comparison | Fixed sequence is statistically valid under specified conditions but differs from the local Holm requirement. |
| Comparator/blinding review | S access, assigned subset, actual-invocation replay, adaptive feedback and sealed local scoring require explicit freeze terms. |

No full/sharded/unit suite or compileall was run: only two Markdown files were
authored, and the brief forbids the full suite while an unrelated blinded job
runs. No MLX/native test, hardware measurement, pipeline, real measurement load,
job/process inspection, model download, network service or external integration
was invoked. No outside study path or real restricted directory was opened,
listed, searched or followed. No weights were accessed.

## Handoff, uncertainty, and commit

The lead must reconcile the primary event, calibration-loss plan, fair S/subset
contract, full ordered-decision power, and a measured phase-level capacity
schedule before signing. Development model selection and optional desktop
replication remain prospective decisions; no scientific recommendation was
installed by this review. The local-monitor arm is defensible as descriptive
transfer scoring with sealed outputs, and does not supply a second actor model.

All performance/capability/model-index figures are supplied documentary premises.
The capacity, runtimes, helper headroom, signal resolution, attrition and API
conditions are unmeasured here. Arithmetic is not native validation. G3–G10
hardware gates and the G12 complete-decision OC remain outside this sandbox,
under a clean lead-controlled lane after the current blinded job is protected.

Next: lead dispositions this seat and the independent companion seat, revises
the exact candidate, and writes the required agreement report. This run did
not produce or substitute that companion review.

Local commit message: `docs(align v5): adversarial Sol2 review of lead ruling`.
The resulting commit ID is returned in the session handoff; it is not embedded
in its own hashed contents.
