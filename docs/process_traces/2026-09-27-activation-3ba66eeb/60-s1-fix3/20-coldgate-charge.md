# Cold gate S1-FIX3-RETURNS-01: the fix-round-3 seat's returns (step 11)

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Write the contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-s1ret-3ba66eeb`, detached @ `8953c7a5`. That is the S1 branch after the fix-round-3 seat's partial work, committed unchanged. Its parent `315364b2` is the tree the rulings were written against.

**Authority, latest text wins:**
- SWEEPCLASS-SAMESIG-01: `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/21-coldgate-fable-ruling.md`. Amendments 61–65; §8.2 steps 1–12; stop rule 61 (c).
- Its erratum: `…/31-coldgate-fable-erratum-ruling.md` in the same directory. Amendments 66–71; delta steps 13–19; lane BFGS-COOLDOWN-ANCHOR-01.
- Both amend amendments 51 and 57–60. Their paths are cited inside the rulings.

**What the seat returned** (report: `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/60-s1-fix3/11-seat-report.md`; the three NEEDS_RULING tables are at its end). It implemented amendment 63 (a) and the narrowed sweep, then returned under step 11:
1. **Two watched reads fit no class.** Both are in `joulewise/salvage_dangler.py`: `_inspect_preworkload_abort` (reads `summary_metrics.json`) and `_telemetry_timestamp_bounds` (reads `power_trace.csv`). They feed a salvage license, and that license reaches `authorize_salvage_dangler_exclusion` → `run_campaign`.
2. **Twelve raw-capture members are outside `RAW_CAPTURE_READERS`, 11 of kind `energy` with no qualifying preceding gate:** `calibration_bracketing._load_calibration_candidate_unbounded`, three `cli.py` strict verifiers, `controller._load_instrument_calibration_attachment`, `reduce._verify_instrument_calibration`, three paper scripts, `validate_powermetrics_fiducial.main` / `rederive_artifact`, and `environment_admission._window_thermal_pressure_refusals` (thermal pressure; no ruled kind fits). Most read `raw/powermetrics*.plist` for the timing fiducial or calibration rather than for claim energy. Decide per member whether that makes them non-energy.
3. **The 64 (b) conflict on `evaluate_member`.** This is the cooldown-anchor route, already ruled by erratum amendment 66 (lane BFGS-COOLDOWN-ANCHOR-01). Confirm that the seat's executed probe matches it, and that 66 disposes of the item.

**Rule, with executed evidence:**
- For each item: its class or kind under the rulings, or a new exact text if none fits. Or rule it a tree finding under 61 (c) / 66, with a lane and an order relative to S1's merge and to the next scored campaign.
- Where a reading of the code decides the kind (energy versus timing or calibration), execute or quote the lines that show what value leaves the function.
- Give the complete, ordered list the seat applies next: steps 13–19 of the erratum plus your dispositions, as test-only work within fix round 3's WRITE_SCOPE. If you rule production code, say so explicitly and name the lane.
- Keep the stop rule finite. A deliberate-evasion form is never a finding (61 (b)).

**Keep intact:**
- custody is never a status;
- authentication precedes every exclusion decision;
- `joulewise/battery_float.py` and FT §E's excluded list stay byte-identical;
- the eight consumers do not import `battery_float`.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every probe in the foreground (split long ones).
- Edit no repository file. Scratch goes under `/tmp/cg_s1ret/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/60-s1-fix3/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- **Budget: 35 minutes, hard.** Mark anything not run as NOT EXECUTED.
- End with a 5-line plain summary for Ed (technical, no project grounding; gloss every internal id).
