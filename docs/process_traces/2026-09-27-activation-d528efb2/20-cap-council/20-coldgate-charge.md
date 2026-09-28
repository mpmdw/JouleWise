# Cold gate CAP-COUNCIL-25G83-01: the 165,000-cell work cap at epoch 25G83

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md (except rows A331/A332), CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**The charge** the four blind seats answered: `docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/00-consult-charge.md` (read it whole; its facts and its seven questions are yours too).
**The four seats** (all in `docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/`): Sol 6.0 xhigh `11-sol.md` (ccefaad5baa7f926…), Astra 6 high `12-astra.md` (f059a50a5b4eebb4…), Opus 5.5 `13-opus.md` (6f3bf12c760f5971…), Fable 5.1 blind seat `14-fable.md` (8f13b894ab391a3d…). All four recommend route R with a fresh successor corpus; they differ on the sizing rule (bottom-up from measured maxima vs top-down), the covered frame range and its evidence, what happens outside the range, whether a formula replaces the constant, and the schedule.
Repository for verification (read-only): `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2` (main `e7c8bcc6` + records).

**Rule on:**
1. Route R or M (or other), with the closure condition for the H1 HOLD stated so a later reader can check it mechanically.
2. **The sizing rule, in full, as text to be pre-registered** before any value is computed: its inputs (cell counts and frame lengths only), the evidence it may be fitted to, the covered frame-length range, behaviour outside the range, whether the bound is a constant or a function of physics the capture supplies, and the acceptance test (e.g. ≥ 24 non-claim captures with zero cap stops). Resolve the seats' disagreements explicitly; verify their factual claims against code where they conflict (cite file:line).
3. **Re-issue membership:** fresh registered corpus, the same 12, or other; and whether the non-claim captures that test the new cap may also be the successor's corpus.
4. **Sequencing**, as an ordered list, relative to: the D-138 issuance of the current candidate `dbad7cc7` (being prepared now; not in question), the other estimator changes merge-staged under D-138, the three-family full-system audit Ed requires before any claim-bearing run (directive #416), the clock-step investigation (H4), and the windows.
5. **H4 clock steps:** the investigation that must precede claim-bearing windows, and whether the 5 ms span limit stands.
6. What this ruling needs from Ed, if anything (Ed reserves acceptance-artifact identity and publication; changes to the sealed registration need his approval).

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3 -B`, never `.venv`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`. Kill any process you start by PID. Run no capture, no powermetrics.
- Modify NO file in any repository except the ruling file below. Scratch goes under `/tmp/cg-cap-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 45 minutes. First line `RULING: CAP-COUNCIL-25G83-01 ISSUED` (or `RULING: REFUSED — <reason>`). Plain language; every term glossed at first use. End with a 3-line plain summary.
