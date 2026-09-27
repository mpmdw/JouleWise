# Cold Fable 5.1 final pass (gate-ledger row 7): PR #434, merge candidate 722f7bd1

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-harvest-fp-77b1bee2`, detached at the exact merge candidate `722f7bd161f1a1d0ae2ef624f7f29aac3e347d82`. Its parent is `a71a5e79`; `origin/main` is `670756f3`, which adds only the test-only #433 on top of that. The integration tree, the merge into main, is `/Users/edr/code/JouleWise-wt-harvest-integ-77b1bee2` @ `2a4416c4`.

**The change.** It is the harvest of derivation window W2 (`d079-epoch-25g83-derivation-w2-20260927`, epoch 25G83, Registration Revision 5), one commit of two files:
- `configs/calibration/calibration_ledger_head.json`: pin 226/`bd7aee7a…6693` → 276/`476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737`.
- A new file, `configs/calibration/battery_float_verdicts/d079-epoch-25g83-derivation-w2-20260927.json`, with `battery=pass` (sha256 `51f49618…46ec`).

It was produced by the governed tools under `docs/phase_2/derivation_night_runbook.md` §2.0–§2.2a in the W2 measurement root, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2` (HEAD 722f7bd1, python `.venv/bin/python`, ledger `runs/calibration_observation_ledger.jsonl`, sha256 `23f72c37…1c7d`). The night custody root is `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927`. The pre-registration sha256 is `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`.

**Evidence already gathered** (read it and verify what you need; do not trust it). It is all under `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-77b1bee2/`:
- The operator record, items 2 and 4–10: `00-activation-record.md`. Raw tool outputs are in `10-w2-harvest/`.
- Row 1 + execution lens, Sol 6.0: `20-harvest-gate/11-sol-audit-report.md` (AUDIT: PASS, 0 findings).
- Contract lens + counter-review, Opus 5.5: `20-harvest-gate/12-opus-contract-lens.md` (CONTRACT LENS: PASS; 3 should-fix, 4 nits; dispositions in record item 10).
- The W1 precedent final pass, for comparison: `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/20-harvest-gate/22-fable-finalpass-ruling.md`.

**Rule on:**
1. MERGE or DO-NOT-MERGE this exact candidate to `main`. The merge method is a merge commit.
2. Is the battery verdict right? Re-verify it yourself, read-only:
   - Run the §2.2a (vii) `check` from the measurement root, naming W1 and W2 (`--session-ids <W1> --session-ids <W2>`).
   - Read at least three slots' `raw/battery_float.{pre,post}.ioreg` directly.
   - Check that each of those slots' `probe_error`/`passed` fields are false/true.
3. The registration consequence. W1 and W2 each have 6/12 valid, so n = 12, exactly Revision 5's floor, and the contract lens says W3 is **not permitted**. Is that reading of the registration right? What must be settled, and by whom, before `prepare-candidate` runs? The contract lens's S3 list is in its report. Is REV5-POST-W3-SHORTFALL-01 (what happens if issuance refuses after W2) a precondition for `prepare-candidate`?
4. Anything that should block merging, or that the owner notice (record item 10, correction email) got wrong.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`.
- Modify NO file in any repository, measurement root, ledger or custody root. Scratch goes under `/tmp/fp-harvest-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-77b1bee2/20-harvest-gate/22-fable-finalpass-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 30 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `VERDICT: MERGE` or `VERDICT: DO-NOT-MERGE`. Findings are tiered BLOCKER / SHOULD-FIX / NIT. End with a 3-line plain summary.
