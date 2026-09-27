# Cold gate REV5-REFUSAL-BRANCH-01: the pre-written answer to "what if `prepare-candidate` refuses after W2?"

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Working tree:** `/Users/edr/code/JouleWise-wt-refusal-cg-77b1bee2`, detached at `origin/main` (`670756f3`). The registration is `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, and its sha256 must be `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`; verify it first. Read its Revision 1 "Stopping." text, Revision 5 in full (especially "Sample, stops and blindness", the issuance floor and the outcome set), and amendment A-R5b.

**Situation (verify what you need; do not trust it).** Epoch 25G83's two derivation windows are captured and harvested:
- W1 is `d079-epoch-25g83-derivation-w1-20260927`: 6/12 valid, battery pass.
- W2 is `d079-epoch-25g83-derivation-w2-20260927`: 6/12 valid, battery pass.
- The count-only dry run names both and reports `admissible for prepare-candidate: yes`.

A cold final pass ([ruling](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-77b1bee2/20-harvest-gate/22-fable-finalpass-ruling.md), §4) found three things:
- W3 is **not permitted** (fewer than 12 valid is the only trigger).
- Retained n = 12 is exactly the floor, so zero margin.
- One value-dependent, incurable refusal cause remains: any member B above 0.25 s (`PLATEAU_INSET_S`).

It ruled that the answer to "what happens on refusal" must be written and ratified by the owner or a cold gate **before** `prepare-candidate` runs, because Revision 5 does not restate Revision 1's "any further capture is Ed's written ruling" sentence.

Measurement roots (read-only), with the issuer at `scripts/issue_calibration_acceptance_generation.py`:
- `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1`
- `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`

**Do not open any measured B value, ledger row value or capture evidence value.** This ruling must stay outcome-blind.

**The proposed statement** (sent to the owner as a recommendation at ≈12:15 PDT, Gmail `1a0e446264f8b791`; the owner may override it):
- (a) On refusal, derivation under Revision 5 ends for this epoch; there is no further capture under it.
- (b) The 24 W1/W2 captures become disclosed diagnostics and are never members of a later registration. Re-using them alongside new captures would be a top-up under another name. This is the same treatment the eleven 2026-09-19 captures received.
- (c) Any successor registration is authorized by the owner or the council, and its text is sealed before its first capture.

**Rule on:**
1. Is each of (a), (b) and (c) consistent with the registration text as sealed? Where the text is silent, is the proposed fill outcome-independent and the most conservative one? Quote the text you rely on.
2. Is anything missing? For example: is refusal the only non-issue outcome? Do "excursion_limited" or "zero_headroom" issuance need a pre-written consequence too? What about a non-value refusal that is curable (missing bytes, wrong arguments), which the final pass says is re-run after the cure?
3. Replacement text: give the exact statement to record, as a numbered list, suitable to be pasted verbatim into the prepare record.
4. Does anything here need the owner rather than a cold gate? The rules let either ratify; say so if you think the owner must.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`.
- Modify NO file in any repository, measurement root, ledger or custody root. Scratch goes under `/tmp/cg-refusal-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-77b1bee2/40-refusal-branch/21-coldgate-fable-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 25 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `RULING: RATIFY`, `RULING: RATIFY-AMENDED` or `RULING: REJECT`. End with a 3-line plain summary for the owner.
