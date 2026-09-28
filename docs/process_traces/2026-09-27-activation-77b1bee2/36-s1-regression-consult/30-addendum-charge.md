# Cold addendum S1-REGRESSION-01-A1: the paired refuter's SF-1 to SF-4

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**The facts** (verify them):
- The cold ruling **S1-REGRESSION-01** is at `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/36-s1-regression-consult/21-coldgate-fable-ruling.md` (sha256 `47868818218d961b09ea5b26b792bd3bfcecf4c1f406c3551dbf09b367a81647`). It decides how BFG-S stream S1 (head `c7593edb`, worktree `/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96`) repairs its full-suite regression: rule 12a (keyword `admit_mock_window`), text 10a (backup-root resolver), the G9 bench repin, a scope grant by exact path, and an ordered plan of seats and lead checks.
- The paired Opus refuter is at `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/36-s1-regression-consult/22-opus-refuter.md` (sha256 `cfbb01d02b1c741a1d1cc05a1b8a11489dba27722a21c531ccac8f6da13866fd`). It says **REFUTER: CONCUR**, 0 BLOCKER, with four SHOULD-FIX items that amend the ruling, plus three NITs:
  - **SF-1:** ban a battery pair on a mock-config fixture (check 2; helper H refuses it with a counterfactual self-test; the reader-side admission goes to a lane).
  - **SF-2:** rule `run_campaign.py:7848`, the AXI completion gate: add it to 12a (c) with a T12a-8 AXI row, or record why it is claim-bearing.
  - **SF-3:** 12a (d) is already met: `claim_readiness_for` returns `ready_for_analysis` for mock campaigns per main's documented contract. The refuter prefers keeping main's semantics.
  - **SF-4:** a fence limiting the repair diff's test paths, because check 7's commit-to-commit fence cannot see the repair.
- Main is `e7c8bcc6` (any clean checkout, e.g. `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2`, read-only).

**Rule on:**
1. Each of SF-1 to SF-4: adopt, adopt modified, or reject — verifying each against the code at S1's head and at main (cite file:line). For every adoption, give the **exact amended text** (replacement for the ruling's clause, or an added clause), and any added defect-shaped test with its counterfactual.
2. The three NITs: which, if any, change the plan.
3. Whether the ruling's plan order, seats, WRITE_SCOPE grants or lead checks change as a result; restate only what changes.
4. Anything in the refuter's analysis you find wrong.

This addendum amends only S1-REGRESSION-01's repair plan. It does not re-open the HOLD, the void MERGE verdict, or any other ruling.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3`, never `.venv`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`. Kill any process you start by PID.
- Modify NO file in any repository except the ruling file below. Scratch goes under `/tmp/cg-s1add-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/36-s1-regression-consult/31-addendum-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 35 minutes. The first line is `ADDENDUM: S1-REGRESSION-01-A1 ISSUED` (or `ADDENDUM: REFUSED — <reason>`). End with a 3-line plain summary.
