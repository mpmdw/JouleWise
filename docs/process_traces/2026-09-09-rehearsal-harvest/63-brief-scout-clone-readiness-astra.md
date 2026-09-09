SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Scout — CLONE-READINESS-01 preparation plan (gpt-6-astra, high, genre scout, read-only)

Worktree: this one, detached at main 7ca2908f. Read first: docs/process_traces/2026-09-08-handoff-redo/99co-magistrate-note-clone-readiness-plan.md (plan + amendment), the kernel row /tasks/CLONE-READINESS-01 in docs/process/state_kernel.json (goal, acceptance, status_note, fences), the second D-176 cold gate ruling under docs/process_traces/2026-09-08-handoff-redo/99ey-coldgate-packet-d176-second-gate/, docs/process/NIGHT_HANDBACK.md §Standing rules, scripts/install_night_agent.sh (the pin checks), joulewise/night_plan_writer.py (the v2 plan fields), and the G2-a first-window plan draft under docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/ (its NEEDS_RULING inputs).
Deliver a preparation plan the magistrate can execute WITHOUT Ed for the agent-side part and hand to Ed for the hardware part:
1. The exact clone recipe for the un-inventoried rehearsal clone `JouleWise-rehearsal-<date>-<sha>`: which head qualifies as "inventory-bearing" today (name the sha and the file(s) that make it inventory-bearing), the `git clone`/`git worktree` form 99co requires, the directory location rule, what "un-inventoried" excludes (runs/, custody, ledger files) and how to prove it (a listing/hash command), and what must NOT be copied. Quote 99co/99ey lines for each requirement.
2. The exact checks the night installer performs against that clone (`install_night_agent.sh` pin checks: repo_head vs driver checkout HEAD, measurement_head vs measurement_root HEAD, courier binary pin) and a dry-run command sequence that validates a v2 plan against the clone without installing anything (render-only / --check flags if they exist; quote the script).
3. Which G2-a inputs (PLAN_ID, NIGHT_ROOT, T0, WINDOW_MAX_S) remain NEEDS_RULING and what the 99cd draft proposes for each; list every fence that must be satisfied before a DIAGNOSTIC_NO_PACK plan is armed (item 4 stage-1 email, 99ey clone cut, D-175 conditions, powermode record per cold gate 44 Q3 / lane POWERMODE-PREFLIGHT-RECORD-01).
4. The Ed-hardware part: exactly what the production v5 re-cut needs from Ed (sudo? the measurement checkout of record /Users/edr/JouleWise-measurement-20260813? the calibration ledger restore/authenticate per the kernel note) and what can be pre-staged by the agent.
Read-only; no edits; no test suite. Report claude-codex-report/v1, genre scout, header < 8192 bytes (verdict = {counts, findings} only); body = the plan with quoted authorities and command tails (use `--help`/`--check` probes where scripts offer them).
