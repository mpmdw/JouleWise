# Cold Fable 5.1 final pass (gate-ledger row 7): PR #432, merge candidate c5088b87

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Your working tree** is `/Users/edr/code/JouleWise-wt-harvest-fp-3ba66eeb`, detached at the exact merge candidate `c5088b871dac4a3e75773f645c6293ffde1568b9` (parent `97082508` = origin/main).

**The change.** It is the harvest of derivation window W1 (`d079-epoch-25g83-derivation-w1-20260927`, epoch 25G83, Registration Revision 5), one commit of two files:
- `configs/calibration/calibration_ledger_head.json`: pin 176/`0f7609ae…` → 226/`bd7aee7ab969e58d4c08992a3af0b0a1fed88cc9a911a65d1200ed0220a46693`.
- A new file, `configs/calibration/battery_float_verdicts/d079-epoch-25g83-derivation-w1-20260927.json`, with `battery=pass`.

It was produced by the governed tools under `docs/phase_2/derivation_night_runbook.md` §2.0–§2.2a in the W1 measurement root, `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1` (HEAD c5088b87; ledger `runs/calibration_observation_ledger.jsonl`, sha256 `b03be938…c63f`). The night custody root is `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927`.

**Evidence already gathered** (read it and verify what you need; do not trust it):
- The operator record, items 4–11: `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/00-activation-record.md`. Raw tool outputs are in `10-w1-harvest/`.
- Row 1 + execution lens, Sol 6.0: `20-harvest-gate/11-sol-audit-report.md` (AUDIT: PASS). It re-derived the pin and verdict byte-exact and read all 24 ioreg files. F1/F2 are pre-existing validator gaps in `joulewise/battery_float.py`, a frozen file.
- Contract lens + counter-review, Opus 5.5: `20-harvest-gate/12-opus-contract-lens.md` (CONTRACT LENS: PASS; S1–S3 should-fix, all about notices, merge method and W2 material, none about the commit's bytes).

**Rule on:**
1. MERGE or DO-NOT-MERGE this exact candidate to `main`. The merge method is a merge commit.
2. Is the battery verdict right? Re-verify it yourself, read-only: run the §2.2a (vii) `check --session-ids` command from the measurement root, read at least three slots' `raw/battery_float.{pre,post}.ioreg` directly, and check that each slot's `probe_error`/`passed` fields in `instrument_evidence.json` are false/true. Sol's F1 says the validator does not check them.
3. Does Sol's F1 (the validator ignores recorded `probe_error`/`passed`) block this merge? Or is it a lane that must land, or be covered by a manual harvest check, before the next harvest?
4. Does the operator's ordering departure (slot-disposition lines read before step iii; an early refused cadence call) affect the science?
5. Anything that should block using `main` with pin 226 as W2's measurement head.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground.
- Modify NO file in any repository, measurement root, ledger or custody root. Scratch goes under `/tmp/fp-harvest-3ba66eeb/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/20-harvest-gate/22-fable-finalpass-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 30 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `VERDICT: MERGE` or `VERDICT: DO-NOT-MERGE`. Findings are tiered BLOCKER / SHOULD-FIX / NIT. End with a 3-line plain summary.
