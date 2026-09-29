# Cold gate NTP-ENFORCE-DESIGN-01-A1: may N1 take a second fix round on the same defect?

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Why this gate is mandatory.** The orchestration rules require a cold gate before any second fix round on the same defect. The N1 delta re-audit says the execution lens's blocker F1 survives the first fix round in a new form (D1). The next round would be the second on F1. The rules add: if two consecutive rounds fail with the same signature, the next spend is a consult, not round three. So this ruling also sets what happens if round 2 fails.

**Ruling in force:** NTP-ENFORCE-DESIGN-01, `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/71-ntp-design/21-coldgate-fable-ruling.md`. The relevant parts are §4.3 (ON is restored on every exit path) and §4.5 (where harvest happens inside the chain).

**The record, all in the same directory (`…/71-ntp-design/`):**
- 30: the N1 brief.
- 31: the N1 report.
- 32: the execution lens (Astra). This is where F1 comes from: "the driver runs the query and ON while a surviving descendant of the capture may still run".
- 33: the contract lens (Opus).
- 34 and 35: the brief and report for fix round 1.
- **36: the delta re-audit (Astra), verdict FINDINGS.** Its findings:
  - **D1, BLOCKER.** F1 survives for descendants that run in separate process groups. Production quiet-evidence code starts its recorder and collector children with `start_new_session=True`. It repairs and cleans them up only later, after the driver's query and ON. The check at `scripts/run_night.py:1006` proves only that the original process group is gone.
  - **D2, SHOULD-FIX, introduced by fix round 1.** Suppose OFF is refused and the immediate ON also fails. Recovery then meets an empty start claim and returns `marker_invalid`. It does not retry ON and it keeps the marker. The pre-fix revision instead restored and removed the marker.
  - **D3, NIT.** The contract lens's finding N1 survives: the category regex backtracks, so a second `timed[...]` token inside the message can supply the witness.
  - **D4, NIT.** The saved F1 regression errors on the old revision for an incidental reason: the ON mock returns `None`.
  - Every other original finding is marked fixed, each with an executed regression.

  The auditor's probes and logs are in `/tmp/ntp-n1delta-d528efb2/`. Of these, `probes_killpg.py`, `probes-killpg-new.log`, `off_failure_regression.py` and `off-regression-*.log` bear on D1 and D2.

**The candidate:**
- worktree `/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2`;
- branch `feat/2026-09-28-ntp-n1`;
- head `3ad82b43`;
- the base of fix round 1 is `e7371399`;
- the fix diff is `git diff e7371399 3ad82b43`.

**Rule on:**
1. **Is D1 real, and is it the same defect as F1?** Verify it by execution in scratch. For example, reproduce the separately grouped sleeper against the driver and against recovery. Check the claim about `start_new_session=True` in the production capture code, and name the exact call sites.
2. **The cure's shape for D1.** Say what counts as proof that no capturing descendant can still be running before the query and before ON, in both the driver and recovery. Candidate forms to judge:
   - (a) a durable registry of every process group and ID the capture chain creates, which the proof then covers;
   - (b) requiring the chain itself to reap its separately grouped children, with a durable marker, before it writes `chain.exited`;
   - (c) a process-table sweep: every process whose ancestry or command matches the chain, including processes adopted by launchd;
   - (d) moving the query and ON after the quiet-evidence cleanup;
   - any combination of these, or something better.

   Name the call sites that must change. Name the counterfactual inputs that the regressions must use, meaning the production call path with a real separately grouped child, not a mock of today's artefact. Judge each form on whether it closes the whole class, not only the one route that was found.
3. **D2's cure.** The OFF-refusal branches need an explicit, durable "Popen never ran" state that recovery understands. The cure must keep the immediate ON attempt and F2's refusal of unknown identities. Confirm or amend.
4. **D3 and D4.** Fix them in round 2 or defer them. If deferred, say where.
5. **May fix round 2 proceed, and with what stop conditions?** In particular: what the delta re-audit after round 2 must execute, and what happens if D1's signature survives again. Is it a consult, a redesign charge, or owner escalation? Whether ruling §4.3 or §4.5 needs amending.

**Protocol.**
- Run as one non-interactive session, foreground only, with `/opt/homebrew/bin/python3 -B`.
- Run tests only with `PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard`.
- Never read the laptop battery.
- Never run real `systemsetup` or `sntp` commands, and never query the system log live.
- Probe processes must be harmless sleepers that you kill yourself.
- Modify NO repository file except the ruling below.
- Scratch space: `/tmp/cg-ntpfix2-d528efb2/`. Make a scratch copy of the candidate for probes; do not edit the candidate worktree.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/71-ntp-design/38-coldgate-fix2-ruling.md`.
- Budget: 60 minutes.
- First line: `ADDENDUM: NTP-ENFORCE-DESIGN-01-A1 ISSUED`.
- Write in plain language, and define each term at first use.
- End with a 3-line plain summary.
