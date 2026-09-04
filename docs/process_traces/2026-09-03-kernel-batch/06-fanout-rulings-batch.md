# Fan-out rulings kernel batch, 2026-09-04

## Authority and scope

This bookkeeping seat installs the dispositions in the magistrate's
`docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md` at upstream
commit `9c9ddc90f4f837fb8d81ae0fb96947ee3fa14de8`. The source reports remain on
their named fan-out branches pending their own gauntlets; this batch changes
only the protected live-state registry, its generated queue projection, the
focused state tests, and this trace.

The required `git fetch origin` could not write the linked worktree's
`FETCH_HEAD` because the Git administrative directory is outside the writable
sandbox. The worktree was clean, with local `origin/main` at `9c9ddc90` and
the bookkeeping head at `0f80c98a`; the authorized files had no content drift
between those commits except that the magistrate ruling file existed only at
the upstream commit. This batch therefore used the locally known upstream
ruling bytes and records the base limitation for the lead.

## Installed dispositions

| Row | Kernel action | Evidence and interpretation |
|---|---|---|
| `FLOOR-WORKLOAD-SIZING-01` | Retired by supersession | D-166 replaced the synthetic workload and fixed the `_v5` decode and prefill sizing rules. |
| `P1-008` | Retired and replaced by `ED-DATES-01` | The Phase-1 row seat found that acceptance criteria and hardware scheduling are owned elsewhere; only authoritative final-report and colloquium dates remain missing. |
| `P2-027` | Retired | The p2-rows seat found publication and external re-reduction are optional owner-directed dissemination, not a completion gate. |
| `P2-035` | Retired | The proposed variance study remains an unpromoted research candidate without a paper consumer or ruled forced-path measurement semantics. |
| `P2-047A` and dependent `P2-047B` | Retired | The controller already buffers in-window records, leaving no distinct buffered treatment; the seat explicitly recommended retiring the dependent physical execution too. `P2-010` and `P2-046B`, the two unrelated physical rows, remain live. |
| `P2-050` | Retired | Later fail-closed work absorbed the ruled items; the unadjudicated trace expansion is not retained as an umbrella task. |
| `PHASE-SHARE-ESTIMAND-01` | Closed as a measured null | Branch `feat/2026-09-04-fan-PHASE-SHARE-ESTIMAND-01` at `14a27380` reports width ratios of `1.0` for scalar prefill share and normalized asymmetry across all ten retained a10 members. The coupled curve removes impossible total-energy combinations but does not narrow either scalar estimand and remains diagnostic/non-claim-bearing. |
| `PREWINDOW-REGEX-01` | Closed complete | Branch `feat/2026-09-04-fan-PREWINDOW-REGEX-01` at `6b86b270` confirms the ruled `codex|claude|t3|mcp-server` pattern was already merged and adds a discriminating regression. Its dependent `EDQ-L9-3-CAPTURE-01` edge is satisfied while the external capture row becomes queued. |
| `QUIET-GUARD-01` | Reconciled, remains open | D-114 and PR #107 limit the row to commit 1: host-wide lease, census, and refuse-at-arm, installed inactive. The obsolete `T3-CHAR-PAIR-01` live-promotion dependency and all commits 2-4 wording are removed. Magistrate option A is explicit: closure requires inactive installation observed on Ed's host, after the required gauntlet. |

## New external input

`ED-DATES-01` asks only for the authoritative final-report and colloquium
dates. It does not reopen evaluator acceptance, Mac-only scope, NVIDIA intent,
borrow scheduling, or any hardware-verification question formerly bundled
into `P1-008`.

## Executed evidence

- `python3 -m unittest tests.test_gen_state tests.test_docs_freshness` exited
  0 on the final authorized edits: `Ran 65 tests in 23.461s`, `OK`.
- `python3 scripts/gen_state.py --check` exited 1 solely because the generated
  `RUN_STATE.md` region differs. That file is outside this delegated seat's
  exhaustive write scope.
- `python3 scripts/gen_state.py --check --run-state
  /tmp/fanout-run-state-fragment.md --queue TASK_QUEUE.md` exited 0 after the
  current kernel's run-state fragment was rendered to the temporary path. This
  proves the canonical kernel and authorized queue projection agree.
- `git diff --check` exited 0.
- The deliberate live-ID tripwire is 135: 143 prior rows minus nine terminal
  rows plus `ED-DATES-01`.
