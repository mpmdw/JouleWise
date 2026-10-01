## RUN_STATE top block: Revision 6 measurement block 1 (windows C1, C2, C3), written 2026-09-30 by the orchestrator

Authority: orchestrator rulings, `docs/process_traces/2026-09-29-interactive-ff50b201/00-session-record.md` items 51-52; plan `160-block-runner-plan.md`; commands `170-c1-arm-recipe.md` (run its sections exactly, unedited). This block is live only while Ed has removed STOP; you are the operator, not a designer.

**Each activation, in this order (a quiet relaunch with nothing to do writes nothing, commits nothing, emails nothing):**
1. Write the heartbeat first. Read directives and Ed's unread mail (`from:claude2.glaring610@passmail.net is:unread`, all threads). Any NO or stop: halt (below). Check `standdown.request`, STOP, `ops/stop*`.
2. Find the newest window plan under `/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-*`. If its t0 is still ahead, or `now <= t0 + 9300 s`, or `night/result.json` or `night/courier.sent` is missing: do nothing, exit (recipe section 6 has the terminal test).
3. Terminal: run recipe section 6 for that window (pin advance, battery verdict, pin-and-verdict commit, `harvest_window.py`). Read `next_window.verdict` from `harvest.json`; the command exits 0 for every decision.
4. Land it: records commit, light-tier PR (Tier: light, Impact all No citing ruling 52(3), rows 1/4/5 "N/A (light tier)", row 2 "N/A (docs only)", row 3 the head sha), wait for CI green on the head, `gh pr merge --merge` (never squash). No lens, no cold gate, no suite run. Touch only the pin, the verdict, and the records `scripts/land_window_records.py` lands (default `docs/process_traces/rev6-windows/<session>/`).
5. Decide on the verdict alone:
   - `NEXT_WINDOW`: run recipe section 7, then sections 1, 3, 4, 5 with `LEAD_S=5400` and the prior-window values. The one email of the activation is this window's arm notice (arming is the change of state; `retry_allowed` needs its message and thread ids). Then exit well before the new t0 - 8 min.
   - any other verdict, any refusal, any null session, any stop flag, any missing record: halt.
6. Before every step re-read STOP and `standdown.request`; on a request, make work durable and exit.

**Forbidden (each one is a halt, not a workaround):**
- No code, config or plan edits; no edits to the recipe scripts; no new tests; never touch `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`.
- No per-window cold gate, lens, council or suite; no process, doctrine or registration amendments; no reinterpreting a verdict or stop flag.
- Never arm on anything but `NEXT_WINDOW`; never arm if a plan span is active, a night agent is loaded, the prior window's pin commit is not on main, or step2 of the recipe reports GAP 1.
- Never arm a fifth session (Revision 6 allows 3 counting windows plus 1 replacement); the registration's own count rule governs, not this brief.
- Never read a measured value (no B, no slot disposition, no chain-log slot lines); harvest output only.
- No `git fetch`, `pull` or `checkout` in `/Users/edr/code/JouleWise` while any plan is armed or a window is running; work in the measurement clone or a worktree. No sudo, powermetrics or launchctl beyond what the recipe scripts run. No branch deletion.
- Never leave any agent, child or background job alive past t0 - 8 min of an armed window.

**Recipe section 8 GAP 1-3 are fixed (PR #447).** If the gate still refuses the registration, harvest still prints a HEAD refusal after the pin/verdict commit, or any recipe step prints `REFUSED:`, stop and email; do not repair. Bench scripts are at `/Users/edr/night-plan-staging/r6-bench` (built from recipe section 2; run them unedited). Before t0 - 8 min of a window you armed, check the process list (`ps -A -o comm=`) for anything check 8 flags other than yourself; the ChatGPT desktop app's Codex helpers are flagged, and if it is open, halt and email Ed instead of arming.

**Halt means:** make state durable (commit on a worktree branch, update this block), email Ed once (what stopped, the session id, the verdict or refusal text, the exact next command you did NOT run), and exit. A halt is never retried by you; two failures with the same signature go to Ed as a consult.

**The block ends** when a harvest says `CLOSE_AND_DERIVE`, or at any halt or STOP. At `CLOSE_AND_DERIVE`: land that window's records (steps 3-4), do not arm, email Ed that the block is complete with the window list (session ids, valid and counted totals from `harvest.json`), and stop. Candidate derivation, the R9 campaign record, cold science gate and the #416 audit are the orchestrator's, never yours.
