# A309 BFGD-VERDICT-MERGE-LIVENESS-01 — cold Fable final pass (gate row 7)

You are a COLD reviewer: a fresh session with no loop context. Your working tree is the exact merge candidate `58bfd3b0`, branch `fix/2026-09-26-bfgd-verdict-merge-liveness`: the fix plus bench NITs, with main `6a463e87` merged in. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md or the decision log.

**The change.** `git diff 6a463e87 58bfd3b0` touches `joulewise/battery_float.py` `load_committed_verdict` and `tests/test_battery_float.py`. It closes the Opus row-6 dissent M-1 on BFG-D. An honest harvest battery-float verdict that reaches main through a `--no-ff` merge was refused, which fails closed but is a permanent liveness trap for calibration issuance. The dictated closure is `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-8e43cfa7/10-liveness/ex-01-dictated-closure-M1.md`.

**Evidence** (under `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/70-a309-gate/`):
- `10-sol-execution-lens.md`: adversarial git histories. One SHOULD-FIX, F1: a rewrite-then-restore across two merges loads. The loaded bytes equal the honest adding commit's.
- `11-opus-contract-lens.md`: PASS, with two NITs, both fixed at the bench in `67231358`.
- **Magistrate's proposed disposition of Sol F1:** no truth impact, because the loaded verdict is byte-identical to the honest harvest commit. The dictated text is kept.

**Questions you must answer.**
- **Q1.** Is the candidate a faithful, complete implementation of the dictated closure, and does any history let a verdict whose final bytes differ from an honest harvest commit authenticate? Probe by execution in /tmp.
- **Q2.** Do you accept the F1 disposition?
- **Q3 (ordering).** The later ruling BFGS-DESIGN-01 Final texts v1.1 text 3 freezes `load_committed_verdict` (and nine other functions) "before S4", with "no exception granted", through a source-digest pin installed by PR S0. It is at `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md` §4 text 3. That judge struck an exception for this M-1 edit only because the M-1 ruling was absent from its packet (see its ruling 50/10 E20). The magistrate's resolution is to merge A309 BEFORE S0, so that S0 pins the post-M-1 bytes. The Revision-5 epoch has not issued, and W1 has not run, so the whole epoch sees one version. Is this consistent with both rulings' purpose (text 3's rationale: the issuer recomputes with main's code and must not disagree mid-epoch)? If not, say what must happen instead.

**Verdict.** MERGE, FIX-FIRST (with exact changes) or REFUSE. A refusal is a stop.

**Protocol.**
- A single non-interactive session: no background tasks, no subagents, every probe in the foreground.
- Write your verdict with the Write tool to `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/70-a309-gate/21-fable-final-pass.md`. Ending before that file exists is a protocol failure.
- Budget: 40 minutes.
