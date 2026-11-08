# Sol registration seat 1: desk handoff, 2026-11-07

**Branch:** `align/2026-11-07-sol-v4-registration-seat1` (already present,
clean at intake). **Base:** `be3cc8b680cde290299aeb8d198de73993fe38b2`.
Independent desk draft only; no registration, arm, configuration fill,
coordination-state edit, merge, push or external message.

## Delivery

`docs/align/squeeze/sol/v4-registration-seat1.md` contains:

- Executive recommendation, source pins and a prioritized owner/lane/cost/gate/
  confidence matrix.
- Proposed exact protocol clauses for chair rulings 4, 5, 6, 9, 11, 15, 17,
  18 and 20, WP19 and twelve grouped implementation/registration concerns.
- Per-item code/kit changes and discriminating acceptance tests; public
  deviation alternatives for selected scope choices.
- A fresh independent Fable + Opus registration-gate checklist and explicit
  boundaries on the monitor/energy squeeze claim.

The findings are reconciled with current repository authority: R0-L2 settled
the slow pick, R10 implemented part of the budget path, Q4/Q6 are affirmative,
and W1's same-trajectory replay is now ordinal 17. The R10 lane deliberately
preserves old contrast admission without a receipt; that requires a lead
supersession if the proposed unconditional protection is adopted. No report
recommendation here is installed as policy.

## Intake and source boundary

Mission M0: read repository AGENTS/CLAUDE guidance, targeted stop-card/current
status/workspace and queue/do-not-do-yet text, playbook M0, orchestration,
source map and targeted D-170 authority. Active stop card was NONE. This
explicit user-assigned desk brief overrides ordinary queue selection; the
user expressly prohibited kernel/task registration and coordination writes.
Those restrictions were honored. No subagent or cross-model consult was
launched; the requested fresh blind Fable/Opus gate is a future lead action.

Read the specified agenda/explainer and locally available integrated,
literature, W1-prearm and research-program Git sources; additionally checked
the governing R10 implementation lane and the protocol-cited prior OC source.
Did not inspect other registration seats' branches. Full source hashes are in
the deliverable. No `git fetch` was attempted: binding no-network instruction
took precedence. Ref freshness beyond the local snapshot is unknown.

All reads stayed in this clone or Git's allowed object-store access. Absolute
data-root references were text only. No real restricted directory, measurement
data root, sealed measurement file or analysis pipeline was opened/run. No
model weights were accessed/downloaded, and no MLX/Metal or native telemetry
operation ran. The existing long analysis job was not inspected or touched.

## Actual verification

This was a documentation-only change. No unittest module, full test suite,
compileall, R1/W1 pipeline or hardware qualification was run. The current
main-based checkout does not contain `tests/align`; relevant modules belong
to the pinned integration lane. Historical tests cited in the audit are
attributed evidence, not tests run by this seat. The checks below took seconds,
not a measurement window, and used Python 3.13 stdlib only.

1. `git status --short --branch` — clean at intake, exact requested branch;
   final intended changes are only the two Markdown files listed below.
2. `python3.13 -B -` (citation/coverage checker supplied on stdin) — PASS:
   58 explicit `path:line[-line] @ commit` citations resolve via `git show`,
   each line span is valid; all nine required R headings, A0–A11 and eleven
   blind-gate checklist items are present, and both NEEDS_RULING blocks remain.
   This validates references/coverage, not the scientific truth of each claim.
   Initial checker assertions mistakenly expected at least 65 citations and
   twelve checklist items; corrected the checker to the actual intended
   coverage. Those failures were checker expectations, not source/test failures.
3. `python3.13 -B -` (synthetic carrier/rank probe supplied on stdin) — PASS:
   executed the stdlib-only `v4_estimands.py` source retrieved with
   `git show e901eb2a4:joulewise/align/apple/v4_estimands.py` in an isolated
   namespace. No runtime/hardware/data modules were imported. With 21
   synthetic carriers scoring `i+H` at H=0 and H=128, its same-H comparator
   returned detection `1/21` at both doses. Holding other carriers at H=0
   instead returned `1/21` then `1`. This confirms the report's helper concern
   in that constructed world; use in a final desk was not established.
   The same probe verified `(19*(39+1)+19)//20 == 38` and `1/40 == .025`.
4. `git diff --cached --check` — required before commit; PASS on the final
   staged two-file artifact. Final diff reviewed by this seat; no source,
   protocol, kit or coordination file included.

For reproducibility, the synthetic probe's essential calculation was:

```python
rows = [dict(pair='synthetic', window=f'w{i//7}', carrier=f'c{i}',
             h=h, score=float(i+h))
        for h in (0, 128) for i in range(21)]
result = benign_carrier_curve(rows, bootstrap_replicates=0)
assert result['pairs']['synthetic']['curve'] == [(0, 1/21), (128, 1/21)]
fixed = [sum(i+h > max(j for j in range(21) if j != i)
             for i in range(21))/21 for h in (0, 128)]
assert fixed == [1/21, 1.0]
```

## Files and local commit

Only these paths are committed:

- `docs/align/squeeze/sol/v4-registration-seat1.md`
- `docs/run_reports/2026-11-07-sol-v4-registration-seat1.md`

One local commit: `docs(align): draft Sol seat 1 v4 registration repair and blind gate`.
The final response records its hash; this report avoids a self-referential
commit pin. No push. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, and `tests/test_gen_state.py` are untouched.

## Open decisions and exact next step

Lead should first disposition U3's numeric derivation, U6/OC and its acceptance
consequence, unconditional no-receipt contrast protection, duty qualification
after R10, and the seed-tag/R1-identity tradeoff. Then implement the bounded
lanes, acquire qualification through authorized lead channels, freeze the
candidate manifest and convene the independent Fable + Opus gate before W1.

Uncertainty remains explicit: no new native evidence; no pilot data-derived
U3 coefficients; no demonstrated full U-set false-fail target; no locked-test
power/sample-size decision; no proof that X-G bounds every Y runtime; no
measured R1-to-W1 scheduler offset; no guarantee the adaptive squeeze holds.
Proposed 1,800-s top-up timing, offload freshness, U6 interval details and
stronger admission consequences require lead review. They are recommendations,
not assertions of existing chair authority.

Native lead work outside this sandbox includes D/X/Y token identity, cache
refeed accounting, battery/OBC/volume checks, scheduler/tail measurement,
High Power restoration and external-DC synchronization/real injection. MLX
tests should use tiny synthetic models, be gated on importability in ordinary
CI, and be run with Metal by the lead in a clean authorized environment.
