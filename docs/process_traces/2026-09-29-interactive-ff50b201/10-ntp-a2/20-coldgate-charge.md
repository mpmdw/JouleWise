# Cold gate NTP-ENFORCE-DESIGN-01-A2: the second delta re-audit of N1

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Why this gate is mandatory.** The orchestration rules require a cold gate before any second fix round on the same defect. Fix round 2b fixed E2: after a failed capture-absence proof, `result.json` and `refusal.json` disagreed. The contract lens now finds the same disagreement at another call site (its R3). A round to fix R3 would be the second fix round on E2.

**Ruling in force:** NTP-ENFORCE-DESIGN-01 (`…/71-ntp-design/21-coldgate-fable-ruling.md`), as amended by addendum A1 (`38-coldgate-fix2-ruling.md`). Read A1 in full.

**The record (all in `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/71-ntp-design/`):**
- 42: fix round 2 (Sol).
- 44: fix round 2b (an Opus writer outside the sandbox). It fixed E1–E3, which the lead found by running the live tests outside the sandbox (record 00, item 118).
- **45: executing delta re-audit (a fresh Opus instance, outside the sandbox): DELTA: PASS.**
  - All seven rows of A1 §7.3 pass, and D1 and N1 do not survive.
  - Three nits: NIT-1, the retry horizon (about 0.8 s with two or more registered groups, 1.8 s with one, 2.8 s with none; liveness only); NIT-2, a night path matches any command that merely starts with it, sibling worktrees included; NIT-3, the idle-night recorder's command line carries no capture signature, so only P2 sees it.
  - It also reports that a lead-run test census elsewhere ran real `sudo -n /usr/bin/powermetrics`, and that the P3 sweep matched those root-owned rows.
- **46: contract-lens delta re-audit (Astra): DELTA: FINDINGS, with no blocker and five should-fixes.**
  - **R1:** the never-launched claim is accepted when the `pid`/`pgid` keys are missing, not null.
  - **R2:** P2's inherited batch census treats an empty answer with exit 0 as proof.
  - **R3:** the E2 fix misses the refusal written by the clean-up step [K] (`night_probe_error`), so the records disagree again.
  - **R4:** the 5 s bound excludes the first pass.
  - **R5:** an earlier group refusal (C7) returns exit status 6, not the refusal status 3.
  - Its probes are in `46-probes/`, and its E1 judgment is "faithful to 'up to 5 s'".

**The candidate:** `/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2`, branch `feat/2026-09-28-ntp-n1`, head `36e8ba6e`. The detached audit copy is `/Users/edr/code/JouleWise-wt-ntp-n1delta2-d528efb2`.

**Rule on:**
1. **Is R3 the same defect as E2?** If so, may a fix round (2c) proceed, and with what exact scope? Verify R1–R5 by execution in scratch.
2. **Which of R1–R5, NIT-1 and NIT-2 are N1's to fix now, and which are registered limits or other lanes?** R2 and R5 are inherited behaviour that N1 now relies on. For each, say whether it can make a query or ON run beside a capture, or a record false, or whether it only costs a window.
3. **NIT-1: should the retry horizon be widened toward A1's 5 s, and how?** For example: start a pass while at least one full check timeout remains; abandon a pass whose check was starved; return the last complete pass's evidence. Weigh a lost window (a spurious refusal) against the bound.
4. **The stop conditions for 2c and its delta.** If a defect of the E2 kind recurs after 2c, what happens: a consult, a redesign, or the owner?
5. **After 2c and a clean delta, is N1 ready for the full gate** (the Opus counter-review, the cold Fable final pass, the PR with its gate ledger, merge)? Or does something else stand in the way, such as N5 or N3's scope?

**Protocol.**
- One non-interactive session, foreground only, with `/opt/homebrew/bin/python3 -B`.
- Run tests only with `PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard`.
- Never read the laptop battery.
- Never run real `systemsetup`, `sntp` or `powermetrics`; never query the system log live.
- Probe processes are harmless sleepers that you kill yourself.
- Modify NO repository file except the ruling below. Scratch space is `/tmp/cg-ntpfix2c-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/10-ntp-a2/21-coldgate-fable-ruling.md`.
- Budget: 60 minutes.
- First line: `ADDENDUM: NTP-ENFORCE-DESIGN-01-A2 ISSUED`.
- Plain language, with each term defined at first use. End with a 3-line plain summary.

**Re-convened 2026-09-29** (orchestrator session ff50b201) after the 09-28 owner pause stopped the first attempt with no output. Only the output path above changed from charge 47 (`…/71-ntp-design/47-coldgate-fix2c-charge.md`). Do not read `48-a2-contract-refuter-opus.md`; a paired refuter's findings are compared with your ruling afterwards.
