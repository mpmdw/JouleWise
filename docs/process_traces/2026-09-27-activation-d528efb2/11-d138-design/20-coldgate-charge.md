# Cold gate D138-25G83-DESIGN-01: the design of the D-138 issuing transaction for the epoch-25G83 calibration

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.** This is the D-144 co-design ruling: independent designs → a cold ruling that becomes the implementation spec.

**The charge the design seats answered:** `docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/00-design-charge.md` (read whole; its facts and questions 1–7 are yours).
**Three designs:**
- Sol 6.0 xhigh (the scout, which also mapped precedent and pins): `docs/process_traces/2026-09-27-activation-d528efb2/10-d138-scout/report.md` (e0d64bc2eb048352…), Q6 is its design, Q7 its open questions; pin census `docs/process_traces/2026-09-27-activation-d528efb2/10-d138-scout/pin_inventory.tsv`.
- Astra 6 high: `docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/12-astra.md` (ecf0c2c5551f4ec5…).
- Opus 5.5: `docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/13-opus.md` (55375160a1f01891…).
**Settled since the charge:** Ed approved the identity `d079_calibration_acceptance_v2_n12_25g83_r1` (path `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json`) and publication once every gate passes (Gmail 17:57 PDT 09-27; record `docs/process_traces/2026-09-27-activation-d528efb2/00-activation-record.md` item 17).
**Pending, not yours:** cold science addendum SCI-25G83-CANDIDATE-01-A2 on a new fact (macOS network time was ON during W1/W2; `docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/00-charge.md`). It may add a disclosure D8 or stop issuance. Design so D8 text can be inserted without redesign; do not rule on the science.
Code: read-only checkout `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2` (main `e7c8bcc6`).

**Rule, as an implementation spec a seat can follow without further questions:**
1. **Loader repair:** the exact design (functions, where the shared disposition authentication lives, what pins it, how the candidate's disposing decision ids bind), with the defect-shaped tests and their counterfactuals. Resolve disagreements among the three designs explicitly; verify contested code facts yourself (cite file:line; you may reproduce the in-memory probe).
2. **Issued bytes:** the exact field-by-field transform from candidate to issued artifact, the seals recomputed and by which production function, what must stay byte-identical, deterministic serialization; and whether a tool (script) or a hand transform produces them (a tool the reviewers can re-run is preferred unless you rule otherwise).
3. **Pin swap:** the must-change list (use the scout's census and check it), what stays, how R7-specific consumers are frozen to R7.
4. **Disclosures and HOLD:** where D1–D7 (+ D8 if A2 adds it) and H1 live; the meaning of `claim_eligible`; whether H1 is enforced in code in THIS PR or procedurally with a lane (say which and why).
5. **WRITE_SCOPE** for the one implementation seat, by exact path, and what the lead does at the bench instead.
6. **Verification and gate sequence** for the PR: pre-issue re-hash list, independent replay, full suite on the head merged with main, lenses/refuters, cold final pass, post-merge checks (A1 B1).
7. Anything that should stop or reorder the transaction.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3 -B`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`. Kill any process you start by PID. Run no capture or powermetrics.
- Modify NO file in any repository except the ruling file below. Scratch under `/tmp/cg-d138design-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 50 minutes. First line `RULING: D138-25G83-DESIGN-01 ISSUED` (or `RULING: REFUSED — <reason>`). Plain language; every term glossed at first use. End with a 3-line plain summary.
