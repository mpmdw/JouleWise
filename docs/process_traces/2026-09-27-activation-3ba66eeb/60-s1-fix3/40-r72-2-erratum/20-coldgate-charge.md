# Cold gate S1-R72-2-ERRATUM-01: one test row's stated counterfactual

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-r722-1c3b3ac9`, detached @ `00b0dc68` (the S1 branch after seat round 3b, committed unchanged by the lead).

**Authority:** the ruling S1-FIX3-RETURNS-01 at `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/60-s1-fix3/21-coldgate-fable-ruling.md`, amendment 72 and its row table (§4, row R72-2 at about line 179).

**The return** (seat report `…/60-s1-fix3/31-seat-report-round3b.md`, flag R72-2 and §Residual risk). Row R72-2 says the counterfactual is "a function without the test of `_MEASURAND_FIELDS`, which returns a license for an attempt that holds energy." The seat's executed probe shows:
- the tree's failed-attempt fixture already carries measurand bytes;
- with the `_MEASURAND_FIELDS` test removed, `_inspect_preworkload_abort` still refuses `gross_energy_j`, through an independent check on unknown non-null failed-summary fields.
So the row goes RED on its exact refusal message when the `_MEASURAND_FIELDS` test is removed, but the stated outcome (a license is returned) cannot occur. The seat asks: accept refusal-message RED, or amend the counterfactual to remove both guards.

**Rule, with executed evidence:**
- Reproduce the seat's probe on this tree (foreground, scratch under `/tmp/cg_r722/`). Quote the lines of both guards.
- Issue exact replacement text for row R72-2's counterfactual column (and its test column if needed). The row must still kill the defect it exists for: an energy-class value on a salvaged attempt reaching a license. Say whether one guard or both must be removed for the RED, and what message or outcome the RED is pinned to.
- State the seat's next step as test-only work in `tests/test_bfgs_consumer_sweep.py` (and, only if unavoidable, `tests/test_salvage_dangler.py`). No production code.
- This is an erratum of one row. Do not reopen any other amendment. Under the ruled stop rule, the next gate after the seat applies this is one refuter pass on the merge candidate.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every probe in the foreground.
- Edit no repository file. Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/60-s1-fix3/40-r72-2-erratum/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- **Budget: 20 minutes, hard.** Mark anything not run as NOT EXECUTED.
- End with a 3-line plain summary for Ed (technical, no project grounding; gloss every internal id).
