# ALIGN reviewer2 desk handoff — 2026-11-07

**Status:** DRAFT review for the lead; no scientific ruling, registration,
collection, or claim gate was performed. Work branch:
`align/2026-11-07-reviewer2`, already selected and clean at intake, starting at
`fdb1e0409784096b1bfffbeea92d4e3d09a02ce0`. No push.

## Deliverable and findings

Added [REVIEWER2](../align/squeeze/REVIEWER2.md): three simulated reviewer
perspectives authored in this single Codex session. They are not independent
peer reviews. The document contains 13 objections, eight prioritized P0
recommendations, two P1 extensions, resource estimates, eight adaptive attack
families, a joint-evasion endpoint and explicit discussion limits.

The central objection is that accounted, benign-looking computation can still
implement sabotage. Passing v4's omission assay does not establish an adaptive
squeeze. The proposed addition tests successful sabotage missed by both
detectors, at a fixed combined benign false-alarm budget, with useful-task
performance and attack capability reported alongside it.

Other material findings:

- Separate v4 GPU-rail evidence from a new independently acquired DC-meter
  assay; it needs its own battery/coverage/boundary qualification and calibration.
- Reconcile ER's generic calibration, v4's leave-trajectory-out/rank procedure
  and the research page's sample-maximum explanation. At `m=39`, v4's stated
  5% rank formula selects rank 38, whereas a maximum would give rank 39 and a
  different marginal rate under the required exchangeability assumptions.
- Preserve settled authority: STATE item 204 already approves Q4 and Q6
  registration grade. Earlier audit questions and v4's default-off text are
  stale on that point. This review does not reopen the rulings.
- Mixed omission/cover attacks, equal-compute sabotage, counter provenance,
  monitor leakage, few independent windows and deliberate exclusions are
  central evaluation risks. Suggested costs make the adaptive study materially
  larger than one positive-control night.

## Files and commit scope

Only these two new documentation files belong to this change:

- `docs/align/squeeze/REVIEWER2.md`
- `docs/run_reports/2026-11-07-align-reviewer2.md`

The local commit message is `docs(align): add hostile reviewer2 squeeze review`.
Its hash is provided in the final handoff. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json` and `tests/test_gen_state.py` are untouched;
no coordination task was registered. No advisor-visible status was changed.

## Inputs and verification

M0 intake used repository instructions, targeted restart/queue/stop-card
sections, the playbook, orchestration and relevant contracts/decision-log
pointers. No active stop card or global work-selection gate was present in the
read projection. The direct user brief selects this desk review; older queue
work was not started. The review's source table pins its evidence:

- v4 / residual specification: `e901eb2a4`;
- chair ruling: `5ea21c17f`;
- literature audit: `16e1db623`;
- W1 pre-arm audit: `53a230598`;
- research-program audit: `7f74dd2a9`;
- agenda, research page, lead directions and contracts: starting head
  `fdb1e0409`.

No fetch was run: the explicit no-network rule overrides the brief's request
to fetch first. All requested refs were already available locally. Nothing in
this report verifies that they are the latest upstream versions, or that the
historical pre-arm findings remain unfixed on a later candidate.

Checks performed for this documentation-only change:

| Command / check | Result and purpose |
|---|---|
| `python3.13 -B - <<'PY' … PY` (inline standard-library document check) | PASS: all 12 pinned source links resolve using local `git cat-file -e <commit>:<path>`; no external link requests. Verified all 13 objection labels and eight P0 entries. |
| Same inline check, arithmetic | PASS: `ceil(.95*(39+1))=38`; maximum-threshold 90% upper bounds at 21/39; zero-event 95% bounds at 29/59/299; 59 member-hours for 59 episodes × two pairs × 1,800 s. |
| `git diff --cached --check` | PASS for both staged new documentation files. |
| Manual final diff/source review | Completed: scope, settled Q6/R10 treatment, distinction between omissions/injections/sabotage, proposed rather than adopted changes, and rate-assumption caveats. Corrected a draft sentence that could have implied low attack capability establishes detector coverage. |

No unit tests, compileall or full suite were needed: no executable code or test
changed. The user's full-suite prohibition was respected. No measurement,
analysis pipeline, model load/download, native MLX check, network operation or
access to real restricted data occurred. The long blinded job was not inspected
or controlled. No fixture was launched; the global fixture/process census was
not run for this desk-only change to avoid unnecessary machine inspection.

No subagents or external consults were used. The documentation checks exposed
no claim-bearing measured result and conferred no measurement authority.

## Open questions, limits and next step

The lead must adjudicate the threat/privilege boundary, count provenance,
independent collector topology, acceptable combined FPR/joint-evasion/utility
targets, and affordable attack/replication scope. Cost ranges are planning
judgments; capability, native runtime cost, hardware availability and independent
collector feasibility have not been tested. External literature was read through
the pinned repo audit and requires primary-source rechecking before submission.

No new native tests are introduced by this change. If the lead adopts the
proposals, their implementation must be qualified outside this sandbox: actual
MLX hidden-compute injections and cache/seed accounting; native gated replay
identity; DC/battery/clock/coverage checks; trusted acquisition; full-model
capability and monitor visibility; then the prospectively frozen physical
adaptive evaluation in a clean no-agent session. This report claims none of
those results.

**Next exact step:** the lead reads REVIEWER2 and writes an accept/reject/defer
disposition for P0-1 through P0-8 against the actual v4 candidate, then decides
which squeeze addendum to prepare before its claim-bearing collection. Review
and merge remain lead-owned; this session only commits the desk draft locally.
