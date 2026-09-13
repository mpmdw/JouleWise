# Exhibit D — governing text at 27957b60

## docs/contracts/pack_night_go_receipt.md lines 92–108
```
is its governed environment file, and the **chain** is the child execution
sequence. A **window** is the identified measurement run named in the pack and
launch context. **Launch realization** rechecks what actually launched; **L10**
is the later launch-to-claim verification ladder. The **courier** delivers the
completed run's results; the **dead-man** is the watchdog that stands down or
terminates a night when continued operation cannot be authorized.

The night driver (`scripts/run_night.py`) is the only GO producer. Its first act
remains the governed agent census, a process-list check for agent presence. Pack
preparation precedes ARM verification and does not receive premature measurement
GO. §10.3 fixes the sequence: first census, then pinned plan bytes/v3 parse,
pack/record preparation, driver-authored T-0 evidence and ARM, verification of
that exact new ARM path, C1–C5, separate GO, and the eight-flag launcher argv. After ARM verification, the driver authenticates the transaction
authorization, confirmation record, T-0 evidence, boot/clock evidence, quiet
census and no-retry state, asks the night gate to evaluate C1–C5, and only then produces
`joulewise.pack_night_go_receipt.v1`. The launch consumer is
`joulewise/arm_readiness.py::_consume_launch_capability`; the launcher is
```

## docs/process/NIGHT_HANDBACK.md lines 190–202
```
next plan.

## Executed — d079-epoch-25g83-derivation-n1-20260913 (2026-09-13)

The night fired and was REFUSED at the gate. Launchd started the driver at
02:56:02 PDT from the clone at H `f90cb8c0`; gate verdict `REFUSED`, reason
`night_refused_agent_present` (census `pgrep -lf codex|claude|t3` exit 0:
Ed's interactive `claude` session pid 24974 with its two Codex MCP servers,
and the ChatGPT desktop app's Codex helper); no chain started
(`chain_exit_code` null), no ledger session opened, nothing captured;
`launchd.night.err` EMPTY; results branch `night-results/20260913` at
`e2dd56d5`; courier email `1a09a3319d602a37`. Per §Next lane this refusal
kind is correct behaviour and the night is re-planned, never re-armed.
```

## docs/phase_2/derivation_night_runbook.md §0.6 lines 582–605
```
### 0.6 Census clean, and the night is agent-free

`[QUIET-MAC]` nights are agent-free. The magistrate exits before `t0 − 25
minutes`; that boundary is the closed start of the plan span, and the resident
supervisor's cooperative ladder enforces it: `standdown.request` at
`t0 − 25 min`, TERM no later than `t0 − 16 min`, KILL no later than
`t0 − 15 min` (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines", the boundary table).

Before the arm census, stop all own seats, delegated tasks and background jobs
using the activation's real task controls; record the task IDs and results and
invent none. Then inspect and classify by ancestry:

```zsh
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'
```

A no-match `grep` exit 1 is the expected outcome, not a failure to be
suppressed. "Own" means this activation and its attached descendants: prior
activations, interactive sessions, foreign seats, daemons, spares, resumed
twins and PID-1 orphans are **not** own. Foreign or unclassifiable processes
abort the arm; do not signal them. Never run the chain, the driver, a full
preflight or a calibration capture from the live activation as a quietness
test.

```

## docs/process/state_kernel.json lane NIGHT-CENSUS-CHATGPT-APP-01
```json
{
 "acceptance": {
  "evidence": [
   "docs/process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md F2: night census pgrep -lf over the codex, claude and t3 names matched the ChatGPT desktop app's 'Codex (Service)' helper (codex-sandbox in its argv) at t0 2026-09-13 02:56",
   "docs/process_traces/2026-09-12-activation-b58fb582/02-equivalence-night-arm-record.md step 4: the arm-time census classifies pgrep hits by ancestry (own vs foreign) but the t0 census in joulewise/night_gate.py does not"
  ],
  "pointer": {
   "json_pointer": "/tasks/NIGHT-CENSUS-CHATGPT-APP-01/acceptance",
   "label": "NIGHT-CENSUS-CHATGPT-APP-01 acceptance",
   "path": "docs/process/state_kernel.json"
  },
  "summary": "A written ruling (cold gate or Ed) decides whether the t0 agent census keeps refusing on the ChatGPT desktop app's Codex helper (operator quits the app before every plan span; runbook 0.6 and the notice template say so) or the pattern is narrowed to agent sessions and MCP servers with a defect-shaped regression that still refuses claude/codex/t3 agent processes; either way the decision is installed in code or runbook text, not left to the desk."
 },
 "authority": {
  "label": "2026-09-13 activation c5048879 harvest record F2 (magistrate registration; rule change needs a ruling)",
  "path": "docs/process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md"
 },
 "dependencies": [],
 "fallback": null,
 "fences": [],
 "flags": [],
 "goal": "Ruling-first: the night gate's t0 agent census (pgrep -lf over the codex, claude and t3 names) matches the ChatGPT desktop app's own Codex helper process, so the app must be quit for every armed night or the pattern must be narrowed under a ruling; decide, then install the decision (code + regression, or runbook/notice text).",
 "id": "NIGHT-CENSUS-CHATGPT-APP-01",
 "lane": "agent",
 "priority": "p2_next_slice",
 "rank": 192,
 "status": "queued",
 "status_note": "2026-09-13: registered from activation c5048879 after the equivalence night refused at t0 (agent present: Ed's interactive session AND the ChatGPT app helper). Blocked on a ruling; not started. Until ruled, every notice tells Ed to quit the ChatGPT app before the plan span.",
 "stop_card": null
}
```
