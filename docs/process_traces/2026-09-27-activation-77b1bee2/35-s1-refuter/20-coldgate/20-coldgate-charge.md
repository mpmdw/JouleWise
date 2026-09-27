# Cold gate S1-A3-ROUTE-01: do the S1 refuter's two A3 BLOCKERs block S1's merge, and what closes them?

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Candidate:** `/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2`, detached at `4aefdd12`. This is BFG-S stream S1 (branch `feat/2026-09-26-bfgs-s1-bundles`) merged with main `b69c39eb`. The S1 base is `1417c0c4`; `git diff 1417c0c4 4aefdd12` shows S1's changes together with main's since then. Use `git diff $(git merge-base 204424e6 b69c39eb) 204424e6` for S1's own changes.

**The rulings that define the pass**, all under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-3ba66eeb/`:
- `30-sweepclass-samesig/21-coldgate-fable-ruling.md`: amendment 61 (c), the stop rule A1–A5 and its findings table.
- `30-sweepclass-samesig/31-coldgate-fable-erratum-ruling.md`: amendment 66, especially 66 (a) row 1c (the non-blocking treatment of a pre-existing route) and 66 (b) (A3 as replaced). F1 there is the cooldown-anchor finding and lane BFGS-COOLDOWN-ANCHOR-01.
- `60-s1-fix3/21-coldgate-fable-ruling.md` (S1-FIX3-RETURNS-01): "No production code is ruled inside S1"; §5.4, the limit whose trace became the refuter's reading task 3; lane BFGS-RAWCAPTURE-01.

**The refuter's report:** `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/11-refuter-report.md`, ending `S1 REFUTER: A3 FAILS`. It gives two BLOCKERs of class (1), A3:
- **F1:** a charging bundle's idle baseline becomes a cooldown anchor that decides a later campaign's verdict. This happens on main too. The refuter says 66 (a) row 1c cannot exempt it, because S1 added lines in `evaluate_member` (`scripts/run_campaign.py:2811`) and `campaign_cooldown_before_member` (`:4221`), which are on the route.
- **F2:** a calibration capture whose own battery pair is missing still yields a numeric bound through `reduce._verify_instrument_calibration` (`joulewise/reduce.py:1171`) into whole-window preparation (`joulewise/whole_window.py:788`). The attachment gate (`controller.py:448`) is the only check. The refuter says S1 changed that function, so row 1c does not apply.

The same pass found A1, A2 and A5 holding, 119 allowlist keys, no class (4) forms, and all three reading tasks clean.

**Rule on:**
1. **F1.** Verify by execution or by reading. Which S1-added lines lie in those functions, and do they lie on the anchor route itself or elsewhere in the function? Under 66 (a) as written, does row 1c apply? Is F1 an S1 merge blocker, or a pre-existing lane item (BFGS-COOLDOWN-ANCHOR-01) that does not block?
2. **F2.** The same questions. Is the missing capture-pair recheck at reduction pre-existing on main? Did S1's change to `whole_window.py:788`'s function touch the route? Blocker, or lane BFGS-RAWCAPTURE-01?
3. **If either blocks:** what is the smallest closure? Must it be production code? The returns ruling said none is ruled inside S1. Does closing it inside S1 need its own ruling of the code, and a further refuter pass under the 61 (c) table ("unless the fix changes production code other than as ruled")? Or is the right move to land the lane first (BFGS-COOLDOWN-ANCHOR-01 / BFGS-RAWCAPTURE-01) and then merge S1 on top? Give an ordered plan.
4. **The same-signature check (rule 11).** Is this the same defect class as the SWEEPCLASS rounds? If so, say what the structural consult should decide.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3`, never `.venv`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`. Kill any process you start by PID.
- Modify NO file in any repository. Scratch goes under `/tmp/cg-s1a3-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/20-coldgate/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 35 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `RULING: S1 MERGE BLOCKED` or `RULING: S1 MERGE NOT BLOCKED`. End with a 3-line plain summary.
