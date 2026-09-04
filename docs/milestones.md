# Milestones And Calendar Map

Status: live sequence, with unresolved external dates named explicitly. The
state kernel (`docs/process/state_kernel.json`) owns whether a step is ready;
`RUN_STATE.md` owns the current restart point. This page records calendar
constraints and the dependency order without turning an estimate into a
promise.

## Known Date Constraints

| Constraint | Recorded state | Truth source |
|---|---|---|
| Local Mac authorization needed for privileged `powermetrics` sampling | Closed on 2026-07-06; the privileged sample and restricted permission rule were recorded. | Phase 1 exit checklist; `RUN_STATE.md` project history |
| Advisor meeting | On 2026-08-28, the meeting was moved one week later. No subsequent meeting outcome or replacement date is recorded in the repository. | `RUN_STATE.md`, T27c |
| Evaluator acceptance bar, colloquium date, and final report deadline | Not yet recorded. Task `P1-008` remains the owner; no repository document may infer these dates. | `docs/process/state_kernel.json`, task `P1-008` |

## Live `_v5` Campaign Sequence

The internal name `_v5` denotes the prospective Qwen3 campaign selected by
D-164 through D-167. A *prospective* campaign fixes its plan and decision rules
before the data they judge exist. None of the rows below asserts that a
claim-bearing result has been collected.

| Order | Milestone | Calendar rule and evidence |
|---|---|---|
| Infrastructure gate | Finish the unattended-night supervisor and pin each night plan to the dedicated measurement checkout. | These gates precede every real window; see `RUN_STATE.md` T31 and D-169/D-171. |
| Diagnostic probe | Run G2-a, the quiet-machine prompt-length probe. | It follows the infrastructure gate. Its date is selected through the governed night plan, not copied here; see state-kernel task `V5-G2A-PREFILL-PROBE-01`. |
| Desk day | Authenticate the G2-a selection, generate the three `_v5` packs, and prove them in a fresh checkout. | It starts only after G2-a and the decode-identity correction; see state-kernel task `V5-DESK-DAY-01`. |
| Shakedown and transaction | Prove the frozen pack on the measurement machine, then open the claim-bearing transaction under the authorization rule. | D-167 owns the order; state-kernel task `V5-TRANSACTION-01` owns the live gates. |
| Nightly collection and desk checks | Run the pre-registered campaign nights, handing each completed night to the G3 check before another arm. | D-167 and the transaction task own the sequence. The repository does not promise a completion date. |
| Issue and write | Produce governed floor and close-out artifacts, then fill only the paper statements those artifacts license. | D-078 bars all predecessor-corpus energy values from this step; the results-fill registry owns each fill. |

## Historical Phase Skeleton — Not A Live Schedule

The original five-phase table is retained only to explain the repository's
directory names. It no longer selects work or predicts dates; the live `_v5`
sequence above and the state kernel do.

| Historical phase | Original dependency | Present interpretation |
|---|---|---|
| 1: Approval, feasibility, measurement design | supervisor and device access | Method and access history; unresolved advisor/calendar input remains in `P1-008`. |
| 2: Harness, Mac slice, and baselines | Phase 1 readiness gate | The Mac instrument path exists; current measurement work is the `_v5` campaign. |
| 3: Disaggregation and interconnect sweep | Phase 2 readiness gate | Not a current paper-schedule promise. Any extension remains behind its live gate. |
| 4: Analysis | dataset frozen | Current desk analysis follows authenticated campaign artifacts. |
| 5: Presentation and submission | analysis gate | Dates remain unknown until `P1-008` records the evaluator calendar. |

## Scheduling Rules

- Quiet-machine measurement is never performed while an agent session is
  active. The state kernel's machine-state lane and current operator card must
  both authorize it.
- The diagnostic probe, desk day, shakedown, transaction, nightly checks,
  artifact issuance, and paper fills run in the order above. A later row never
  borrows an unmet gate from an earlier row.
- If G2-a cannot support a prefill arm, D-166 requires the registered refusal;
  the threshold is not lowered after seeing data. If the timing-dominance test
  fails, D-165 withdraws that sentence rather than changing the test.
- Session-record heartbeat: if more than fourteen days pass with neither a
  dated session record linked from `RUN_STATE.md` nor a recorded break here,
  the next session starts with a milestones and risk-register review. A session
  record may be a formal file under `docs/run_reports/` or the dated
  `RUN_STATE.md` block plus its linked `docs/process_traces/` record, matching
  the repository's current session-record convention.
