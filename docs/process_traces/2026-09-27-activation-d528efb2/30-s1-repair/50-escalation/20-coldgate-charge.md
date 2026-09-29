# Cold gate S1-REPAIR-ROUTE-01: how the S1 repair closes after two same-signature rounds

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**The consult charge** the three blind seats answered: `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/50-escalation/00-consult-charge.md` (read whole; its facts and questions are yours).
**Seats** (same directory): Sol 6.0 xhigh `11-sol.md` (b36ff016ab25b002…), Astra 6 high `12-astra.md` (3f3650077f5b6ce8…), Opus 5.5 `13-opus.md` (a3ca1e07e037a244…; probes in `/tmp/s1route-d528efb2/opus/`). Opus diagnoses one coupling (binding a non-mock config switches off `production_predicate_exempt`, `whole_window.py:989-999`) and proposes "exemption parity" + triage, and reports a gate property: a bundle carrying a pair passes even when its config is deleted or rebound to mock (`bundle_read.py:483-487`).
**Candidate:** `fix/2026-09-27-s1-regress` at `5283d7d0` (read-only worktree `/Users/edr/code/JouleWise-wt-s1-step2-d528efb2`). Tests only under `PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard`.

**Rule on:**
1. The route (from the seats' options or your own), judged first on soundness under owner directive #421 (no route may let a test pass on evidence a real window could not produce, and no claim path may be left un-gated), then on the risk of a third same-signature round. If you adopt a test-only mechanism that stubs production checks (e.g. "exemption parity"), rule the exact closed list, the rule that it never stubs battery code or the test's own subject, and the sweep test that pins the list.
2. The gate property Opus reports (pair present, config deleted or rebound to mock → gate `pass`): verify by execution. If real, is it a production defect S1 must fix before merge, and with what exact text and tests?
3. The triage: how every remaining outcome is classified, who classifies it, and the seats, scopes and order of the next round, with its stop conditions (a hard cap; what returns to a cold gate).
4. What in A3 was wrong (the seats name several), and what stands.
5. Whether S1 should instead be split or abandoned (ruling §8), stated plainly.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. `/opt/homebrew/bin/python3 -B`; macOS has no `timeout` (`perl -e 'alarm N; exec @ARGV' …`); kill any process you start by PID. Never read the laptop battery.
- Modify NO file in any repository except the ruling file below. Scratch under `/tmp/cg-s1route-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/50-escalation/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 60 minutes. First line `RULING: S1-REPAIR-ROUTE-01 ISSUED`. Plain language. End with a 3-line plain summary.
