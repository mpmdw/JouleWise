# Cold gate S1-REGRESSION-01: how S1 closes its full-suite regression

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**The facts** (verify them):
- BFG-S stream S1 is at head `c7593edb`, worktree `/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96`. It was cleared by a cold final pass that ran only targeted suites.
- **The full suite on its integration tree** (`/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2`, `42e2af3e`) gives **115 failures and 418 errors**, caused by S1 itself. Main `e7c8bcc6` is green.
- **The scout's 11 groups:** `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/62-regression-scout-report.md`, with the inventory `62-regression-inventory.jsonl`.
- **Three blind consult seats**, all in `36-s1-regression-consult/`: Sol (`11-sol-consult.md`), Astra (`12-astra-consult.md`) and Opus (`13-opus-consult.md`). All three say HOLD S1. They split on G2:
  - Sol keeps the strict refusal of `not_applicable` at window scope, with tests changed to expect it.
  - Opus proposes text "12a": an all-mock window returns verdicts, a mixed window refuses, and the config-bound `mock_telemetry_claim_ineligible` barrier still blocks claims. About 8 lines in `bundle_read.py`.
  - Astra proposes minimal ruled non-claim mock completion.
- **Opus also found** that the repair must edit files §E forbids S1 to write, which needs a named scope grant. It found that G6 blocks S3's `_v5` freeze (`arm_readiness_evidence.py:2446-2466`), and it raised should-fix items on campaign-completion shape, a mislabelled refusal and G10's real battery probe.
- **S1's ruling texts** are all under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/`: Final texts v1.1 at `2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md` (read text 12 and §E); the SWEEPCLASS and RETURNS rulings at `2026-09-27-activation-3ba66eeb/`; and the final pass at `2026-09-27-activation-77b1bee2/35-s1-refuter/51-fable-finalpass-ruling.md`.

**Rule on:**
1. **G2.** Strict refusal with the tests changed, rule 12a, or another rule? Check the text-12 contradiction Opus names by reading the code. Whatever you choose must keep every claim-bearing path strict and must not weaken the gate. If you choose 12a, give its exact text and its defect-shaped tests.
2. **G9.** Who repins the paper supply-map roles, when, and under what review? Are they synthetic `test_fixture_non_issuing` fixtures, as Opus says? Verify.
3. **Scope.** Grant, by exact path, the files the repair may edit beyond S1's ruled WRITE_SCOPE, or refuse the grant and say what follows.
4. **The repair plan.** Is it ordered? Give the steps, the seats and their WRITE_SCOPEs, the checks the lead must run (assertion counts against main, banned patterns, planted defects), and **the gate sequence, with a full suite of the exact head merged with current main before every refuter, cold gate and final pass**. Say which of Opus's should-fix items are in scope.
5. **Anything that should instead split or abandon S1.**

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3`, never `.venv`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`. Kill any process you start by PID.
- Modify NO file in any repository. Scratch goes under `/tmp/cg-s1reg-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/36-s1-regression-consult/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 40 minutes. The first line is `RULING: S1-REGRESSION-01 ISSUED`. End with a 3-line plain summary.
