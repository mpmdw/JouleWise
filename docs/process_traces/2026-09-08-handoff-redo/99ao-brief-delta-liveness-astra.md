# Delta re-audit — WINDOW-STATUS-GUARD-CENSUS-01 fix round (gpt-6-astra, medium, genre review, READ-ONLY)
Branch fix/2026-09-08-window-status-liveness, head e9579dc2; the fix round is `git diff a2cfb644 e9579dc2`. The Opus contract
review it answers is at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99s-ref-liveness-opus-contract-review.md
and the brief with the magistrate's rulings at
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ah-brief-fix-liveness-astra.md. Audit:
1. R1: is UNKNOWN now the outcome for rc 0 + empty output, and does UNKNOWN refuse publication (not merely warn)? Cite
   the assertion in the regression and state the counterfactual.
2. R2: trace `_complete_chain_start` in scripts/run_night.py: (a) is the first marker write complete (pid, pgid,
   epoch) and closed before `observe_identity` is called; (b) is the replacement atomic on the same filesystem and
   fsynced (read `_write_json`); (c) if the driver dies between the two writes, what does the dead-man path and the
   census each do with a marker lacking `start_time` — refuse (correct) or classify DEAD/LIVE (defect); (d) can the
   O_EXCL claim ever be re-taken by a second driver while the temporary file exists? (e) is there any window in
   which `chain.started` is EMPTY or partially written that the census could read? Cite lines.
3. R3: is `test_r7_real_campaign_log_writer_rows_are_complete` byte-identical to HEAD~2 (a2cfb644~1)? Run
   `git diff a2cfb644~1 e9579dc2 -- tests/test_run_campaign.py` and report whether the restored function differs.
4. R5/R6: does the exit-2 path release the campaign lock and remove the registry entry on every RuntimeError origin
   (lock acquired, publish failed), and does re-reconciliation append zero new diagnostics on an unchanged registry?
5. Any NEW defect introduced by this round (fix rounds introduce defects). Name file:line.
Verdict keys per genre review; severity per finding; ≤ 800 words; no edits; header < 8192 bytes.
