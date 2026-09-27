# BFG-S S2 (quiet-night collector brackets and the night summary): cold Fable final pass (gate row 7; also row 10 for the post-lens commits)

You are a COLD reviewer: a fresh session with no loop context. Your working tree is the exact merge candidate `d3f904d6` on branch `feat/2026-09-26-bfgs-s2-qpe-collector`, based on main `1417c0c4`. Main has since moved to `97a48451` by a bookkeeping-only merge (README, RUN_STATE, TASK_QUEUE, state kernel, one gen_state test pin); the integration tree `11c2f89d` = candidate + `97a48451` is under a full-suite replay. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md or the decision log. **Contamination disclosure first.**

**The change.** `git diff 1417c0c4 d3f904d6` touches `scripts/sample_quiet_predicate_evidence.py`, `joulewise/quiet_predicate_campaign.py`, `joulewise/night_kinds.py` and five test files. S2 is the second of the battery-float gate's PRs (S0 merged; S1 in progress in parallel). It adds one battery pre/post pair per quiet-night collector envelope, the `journal_rows` witness, atomic record writes, the custody-first night summary that blanks a night on any non-pass, the executor's custody line, and flips the quiet-predicate night kind's `battery_brackets` fence to True.

**Rulings that govern, newest first where they conflict** (absolute paths):
1. BFGS-SAMESIG-01 erratum §8, amendments 44–46: `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/70-consult-samesig/30-erratum/21-coldgate-fable-erratum-ruling.md` (and its base ruling `../21-coldgate-fable-ruling.md`).
2. QPE-SHAPE3-NIGHT-BLANK-01 erratum §5 (amendment 35 restated, T6-f..v) and §3 B-6 (X-1): `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-e6f06c96/10-qpe-shape3/30-erratum/21-coldgate-fable-erratum-ruling.md`.
3. Addendum-3 erratum §3–§4, amendments 32, 33, 34 (30 as merged context): `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/20-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md`.
4. Addendum 2 §5, amendment 20 (collector clause): `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/40-addendum2/21-coldgate-fable-addendum2-ruling.md`.
5. Final texts v1.1 §4 texts 5, 6, 15 (S2 clause), §E, §F T5/T6: `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md`.
6. The seat brief and the lead's fix contract: `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/30-bfgs-s2/10-seat-brief.txt`, `30-fix1/10-fix-contract.txt`, `50-fix2/10-fix-brief.txt`.

**Review trail** (under `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/30-bfgs-s2/`): `11-seat-report.md` (round 1, `fcf9cfd9`); `20-lenses/11-sol-execution-lens.md` and `12-opus-contract-lens.md` (round-1 lenses); `30-fix1/11-seat-report.md` (fix 1, `6c73caf4`); `40-delta1/11-sol-execution-delta.md` and `12-opus-contract-delta.md`; `50-fix2/11-seat-report.md` (fix 2, `d3f904d6`, test-only); `60-delta2/11-sol-execution-delta.md` (clean). Lead bench commits: `4ea4b26b` (sweep assertion admits `quiet_pre`/`quiet_post`; S1 makes the mirror edit for `bundle_*`, and at integration the line becomes `set(battery_float.PHASES)`) and `a0e8e47f` (revert of fix item F7, upheld by amendment 46). The bench ran V1 unsandboxed at `d3f904d6`: 493 tests OK (the real-collector subprocess test needs `/bin/ps`, which the seats' sandbox denies).

**Magistrate's dispositions** (you may overrule any):
- Round-1 Sol B1 (a completed envelope with `end_stamp`, `post` and `journal_rows` stripped reads as an honest unfinished record): NO CHANGE, the residual amendment 35's restating ruling accepts by name.
- Round-1 Sol B2 and delta-1 B2 (authentication-to-routing binding): same signature twice → consult → SAMESIG option (a), amendments 44–45.
- Opus N-1: a historical envelope (no `battery_float` key) with a missing `rounds.jsonl` raises `CustodyUnreadable("rounds.jsonl unreadable: …")` and writes no summary (fail closed), rather than being excluded "as today" under text 6. The texts point both ways; the magistrate chose fail-closed. **Rule on this.**
- Fix-2 coverage pins for behaviour already correct at base are baseline-green; only changed-behaviour rows were required RED-first.
- Opus N-3..N-5 closed in fix 1; D-3's read-before-authentication order is recorded by amendment 44.

**Questions.**
- **Q1.** Is the candidate a faithful, complete implementation of the governing texts for S2's scope, with every T-row the rulings assign to S2 present, through the named production call site? Probe by execution in /tmp (real `collect`, `pilot_summary`, `summarize`, `execute`).
- **Q2.** Can any honest night now be refused, blanked or recorded under a wrong reason that the rulings do not intend? Include the refusal path, a timeout kill, a collector crash before any write, `record_attestation`, the replay recorder, and the two historical pilot nights (intended: `BATTERY_FLOAT_EVIDENCE_MISSING`).
- **Q3.** Can a charging-confounded or custody-failed envelope reach a published number or a non-blanked summary?
- **Q4.** Fresh review (row 10) of the bench commits `4ea4b26b` and `a0e8e47f` and the test-only fix 2.
- **Q5.** Do you accept each disposition above (rule N-1 explicitly)?
- **Q6.** Anything design-level that should stop S2 from merging before S1 (the fence flip makes a quiet-predicate night armable once S2 merges; text 15 allows that).

**Verdict.** MERGE, FIX-FIRST (with exact changes) or REFUSE. A refusal is a stop.

**Protocol.** A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Edit no repository file; scratch under `/tmp`. Write your verdict with the Write tool to `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/30-bfgs-s2/90-gate/21-fable-final-pass.md`. Ending before that file exists is a protocol failure. Budget: 45 minutes.
