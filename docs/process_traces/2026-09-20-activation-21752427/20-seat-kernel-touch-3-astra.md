```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"Kernel touch 3 complete.","workspace":{"base_requested":"741a1f66","base_mode":"exact","head_start":"741a1f66","head_end":"741a1f66","upstream_end":"741a1f66","branch":"bookkeeping/2026-09-20-kernel-touch-2-21752427"},"pathspec":["docs/process/state_kernel.json","TASK_QUEUE.md","RUN_STATE.md","tests/test_gen_state.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"inspection","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_state.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Change

Retired `EVIDENCE-INSTALLER-SPLIT-01` by removal and registered `EVIDENCE-NIGHT-ENTRY-01` at rank 256, following the retirement/successor convention found in history (for example, `b8fe1110`). Count remains **220**.

The successor is queued, `[AGENT]`, `p1_phase_gate`, with no dependencies. It records PR 1 preparation and lifecycle façade, sealed-byte preservation, the refusal inventory, required deliverables, and the 4–6 seat-hour estimate. PR 2 records later notice-to-install orchestration and watchdog census provenance.

Lane 257 and every unrelated task remain unchanged. Updated the expected ID and T38o report pointer; regenerated both regions. `updated` remains `2026-09-20`.

Executed checks:

```text
/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_state.py
(no output; exit 0)

/Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_state.py --check
(no output; exit 0)

PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_state -q
----------------------------------------------------------------------
Ran 44 tests in 2.245s

OK

Task count = 220; lane 257 and every unrelated task unchanged
RUN_STATE.md: bytes outside generated region unchanged
TASK_QUEUE.md: bytes outside generated region unchanged
Changed paths exactly match WRITE_SCOPE
```

`git diff --check`: exit 0.

`git diff --stat`:

```text
 RUN_STATE.md                   |  2 +-
 TASK_QUEUE.md                  |  4 ++--
 docs/process/state_kernel.json | 30 +++++++++++++++++-------------
 tests/test_gen_state.py        |  5 +++--
 4 files changed, 23 insertions(+), 18 deletions(-)
```

`git diff RUN_STATE.md | head -20`:

```diff
diff --git a/RUN_STATE.md b/RUN_STATE.md
index cf2607e9..7a53d1be 100644
--- a/RUN_STATE.md
+++ b/RUN_STATE.md
@@ -5347,7 +5347,7 @@ NONE — no global work-selection gate is active.
 
 ## Restart By Machine-State Lane
 
-Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-09-20). Latest report: [T38n — 2026-09-20: census self-match cure merged (PR #371); pilot night one aborted, harvested, uninstalled](docs/process_traces/2026-09-20-activation-21752427/12-diff-gate-census-self-match.md).
+Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-09-20). Latest report: [T38o — 2026-09-20: evidence-night entry point designed (consult 18); pre-arm supervisor clause corrected](docs/process_traces/2026-09-20-activation-21752427/19-ruling-supervisor-clause-and-entry-point-design.md).
 
 ### [ED-EXTERNAL]
 
```

Next exact step: lead review of the four-file diff. No blockers; no commits or pushes.

## Verification notes

This bookkeeping-only change used the requested focused suite and generator checks; the full application suite was not run. No network, launchctl, or writes outside the allowlist occurred.