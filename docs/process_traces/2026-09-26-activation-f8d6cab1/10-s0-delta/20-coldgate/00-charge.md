# Cold gate BFGS-DESIGN-01, addendum 3: custody of the quiet-envelope records (rule-11 trigger: a second fix round on the same defect class)

You are a COLD judge: a fresh session with no loop context. Your working tree is the S0 candidate `783a09be` (branch `feat/2026-09-26-bfgs-s0-helper-fence`). Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log, or memory or skill files. **Contamination disclosure first:** your ruling's opening lines list anything you loaded that was not in this packet.

**Why you are convened.**
- Round 3 closed a BLOCKER class: *a malformed or unreadable input masks a custody failure*. Appending a malformed line to `rounds.jsonl` had turned a recorded-digest mismatch from `CustodyFailure` into `pass`.
- The delta re-audit of rounds 3/3b now reports two more members of that class. Two consecutive rounds failing with the same signature are an escalation trigger, so the next step is this ruling, not a round-4 fix.
- The two lenses split on the same-signature question. The magistrate does not adjudicate a split that would need ruled text changed.

**Packet** (absolute paths):
- Authority, Final texts v1.1 §4 text 2 (order (a)–(f); custody "never a status … never an exclusion"): `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md`
- Addendum 2 (amendments 20–28; amendment 21 is the quiet span, and E1/E12 are the refusal-shape envelope): `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/40-addendum2/21-coldgate-fable-addendum2-ruling.md`
- The lead's round-3 fix contract (C1 is at issue: "Missing: zero rows"): `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/41-fix-contract-round3.md`
- The delta charge: `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/00-delta-charge.md`
- Sol execution lens (F1 and F2 are BLOCKERs; "same signature: yes"): `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/10-sol-execution-lens.md`
- Opus contract lens ("same signature: no"; S-1 and S-2 are SHOULD-FIX): `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/11-opus-contract-lens.md`
- Code: `joulewise/battery_float.py`, in `authenticate_quiet_session` (about lines 923–980), `authenticate_pair`, `authenticate_bundle` and `authenticate_capture`. Tests: `tests/test_battery_float.py` (`RoundThreeAuthenticationTests.quiet` builds the fixtures).

**The magistrate's reading, which you may reject.**
- **F2.** `session.json` is the *mutable* session journal, so the per-round digests in `rounds.jsonl` are the only digests recorded before finalization. In F2, a journal row records a raw digest that disagrees with the one `session.json` now states. `CustodyFailure` is raised. Deleting `rounds.jsonl` then gives `pass`, because C1 treats a missing journal as zero rows.
  - If a completed (non-refusal) collector envelope always writes a non-empty journal, then a missing journal means lost custody evidence and cannot be `pass`.
  - The refusal shape (E1/E12) writes an *empty* journal, never a missing one.
- **F1.** An unreadable or non-object `session.json` becomes `{}`, and an unreadable `metadata.json` or `instrument_evidence.json` is handled the same way in their wrappers. Text 2(a) then yields `evidence_missing`, and the journal cross-check is skipped. The effect is that deleting a raw file *and* corrupting the container turns a `CustodyFailure` into a status.
  - Opus reads this as ruled by text 2(a). Sol reads it as the same signature.
  - The magistrate's concern: some consumers treat `evidence_missing` as a per-member **exclusion** (for example, text 10's bracketing `continue`), whereas custody must refuse the whole computation and is "never an exclusion". So corrupting a record converts a refusal into a selection.

**Rule each question.** For each, give a decision, the exact text (numbered as amendments continuing from 28), the tests it obliges (defect-shaped, each naming the counterfactual input and the production call site), and reasons. Verify code claims with executed probes: run the Sol reproducer (copied to `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/10-sol-repro.py`; run it from the working tree root with `python3 <path>`), or rebuild it from `RoundThreeAuthenticationTests.quiet`.
- **Q1 (F2).** What is the status of a missing `rounds.jsonl` for (i) the exact refusal shape, (ii) a completed envelope with `end_stamp`, and (iii) any other shape? Is it custody, `evidence_missing` or `pass`? Check the collector (`scripts/sample_quiet_predicate_evidence.py`) for when it creates the journal, and say whether a present-but-empty journal for a completed envelope is acceptable.
- **Q2 (F1).** What is the status of an unreadable, non-JSON, duplicate-key or non-object mandatory container (`session.json` for quiet; `metadata.json` for bundle; `instrument_evidence.json` for capture)? Choose between `CustodyUnreadable` (a refusal of the whole computation) and `evidence_missing` under text 2(a). Distinguish a readable object whose pair fields are missing, which stays text 2(a). Consider the exclusion-versus-refusal effect on text-10 bracketing and on any other consumer that excludes.
- **Q3 (the same-signature sweep).** Name any other input S0 reads where absence or corruption downgrades custody. Rule on each, or state that there is none.
- **Q4 (S-1 and S-2, for confirmation only).** The magistrate intends to apply both in the next fix round:
  - S-1: the C7 pin hashes from the first decorator line and requires a single binding per name, and is regenerated from the base file.
  - S-2: the C8(ii) guard also flags `copy.replace` and `__replace__`.

  Object only if either conflicts with ruled text.

**Protocol.**
- A single non-interactive session: no background tasks, no subagents, every probe in the foreground. Do not edit repository files other than the ruling file.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/20-coldgate/10-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 40 minutes. Mark any probe you could not run as NOT EXECUTED.
