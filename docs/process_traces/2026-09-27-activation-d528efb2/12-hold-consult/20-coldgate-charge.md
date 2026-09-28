# Cold gate HOLD-BY-CONSTRUCTION-01: how the 25G83 claim hold is closed by construction

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**The consult charge** (facts and questions — yours too): `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/12-hold-consult/00-consult-charge.md`.
**Seats:** Sol 6.0 xhigh `docs/process_traces/2026-09-27-activation-d528efb2/12-hold-consult/11-sol.md` (350eb695c879472b…), Astra 6 high `docs/process_traces/2026-09-27-activation-d528efb2/12-hold-consult/12-astra.md` (0dca2e493a5fe093…). The Opus hold refuter's cure sketch is a third input: `docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/hold-refuter-2-opus.md` (B-1 cure, S-1..S-4) with probes `probe_fix.py` etc. in the same directory.
**Candidate:** `feat/2026-09-27-d138-25g83-issuance` at `8458f797` (read-only worktree `/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2`). Its records at `f3c1bb64` (issuing record + D-185) are being revised.
**Rulings in force:** design ruling `docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/21-coldgate-fable-ruling.md` and addendum A1 `docs/process_traces/2026-09-27-activation-d528efb2/11-d138-design/31-addendum-ruling.md`.

**Rule, as an implementation spec for ONE fix round (fix round 3) plus its gates:**
1. The design that closes H1 by construction (epoch-keyed or otherwise), where it is enforced, what a non-claim caller is and how it is authorised, and how the cap plan's non-claim captures stay possible. Resolve seat disagreements; verify contested code facts yourself.
2. The exact changes (files, functions) and the tests: a RED-then-GREEN counterfactual for each known route (round 1 ×2, round 2 B-1, S-1..S-4), and the census test that fails on an unknown route. The fix seat's exhaustive WRITE_SCOPE.
3. The other open questions: the promotion tool's deleted-citation and bare-H1 acceptance (fix now, or lane); the four GREEN R7-freeze mutants (equivalent under R-1, or a test gap to close now); the independent replay's item (vi) (restate it).
4. The stop rule for this round: under what outcome the transaction stops for good and returns to the owner (e.g. a third found route), rather than a fourth round.
5. The gate sequence to merge from here.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. `/opt/homebrew/bin/python3 -B`; macOS has no `timeout` (`perl -e 'alarm N; exec @ARGV' …`); kill any process you start by PID. No capture, no powermetrics, never read the laptop battery.
- Modify NO file in any repository except the ruling file below. Scratch under `/tmp/cg-holdc-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/12-hold-consult/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 60 minutes. First line `RULING: HOLD-BY-CONSTRUCTION-01 ISSUED`. Plain language. End with a 3-line plain summary.
