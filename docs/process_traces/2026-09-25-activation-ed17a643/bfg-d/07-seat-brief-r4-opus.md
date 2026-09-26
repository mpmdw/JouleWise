# BFG-D round 4: implementation seat brief (Opus 5.5; Codex still down)

You are the implementation seat for PR BFG-D on branch `feat/2026-09-25-bfg-d` in this worktree. HEAD is `ab431280`: round 3, completed by an earlier Opus seat (its report is `05-seat-report-r3.md`), plus the lead's N-1 bench change. Treat that work as reviewed-in-progress, not final.

**Your task:** implement cold gate HARVEST-VERDICT-FINAL-01 as finally ruled by its addendum. The ONE source is `06-harvest-final-obligations-v1.1-source.md`, §4 ("Harvest-verdict final obligations v1.1", §4.1–§4.11), in this directory. Implement §4.10 items 1–11 exactly. Where §4 gives a name (exception class, function, subcommand, flag, refusal text, record field, file path, constant), use it verbatim. §4 supersedes the earlier BFG texts wherever they differ. Everything else in `00-final-texts-v1.1-source.md` §5 still stands and must stay green.

**WRITE SCOPE (exhaustive):**
- everything round 3 had: `joulewise/battery_float.py`, `joulewise/night_gate.py`, `joulewise/arm_retry.py`, `joulewise/evidence_night.py`, `joulewise/night_agent_install.py`, `joulewise/arm_readiness_evidence_t0.py`, `scripts/validate_powermetrics_fiducial.py`, `scripts/issue_calibration_acceptance_generation.py`, `scripts/calibration_cadence_report.py`, `scripts/issue_epoch_continuation.py`, `tests/**`;
- plus `docs/decision_log.md` (append A-R5b-1 exactly as §4.8 gives it, below the A-R5b entry if present, otherwise at the end; it is a verbatim install);
- plus `docs/phase_2/derivation_night_runbook.md` (§4.9 block as new §2.2a, the §2.1 row and the §2.3 sentence, plus the existing ARM-RETRY-POLICY block);
- plus `docs/process/NIGHT_HANDBACK.md` (the §4.7 per-window notice line in the template, plus the existing policy block);
- plus this directory, for your report.

Anything else: stop and report NEEDS_SCOPE. `joulewise/authentication_io.py` is read-only; reuse it, never edit it. FORBIDDEN (pinned): `joulewise/calibration_bracketing.py`, `joulewise/adapters/powermetrics.py`, `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/reduce.py`, `protocol_v3.json`, `scripts/night_chains/**`, `configs/**`. The one exception: the tracked disposition registry is read to compute its digest, never edited.

**Rules:**
- Never weaken, delete or loosen a pre-existing assertion. List every expected-value edit with before/after.
- Every test named in §4.10 must exist and pass at the production call site named there.
- Run each touched module to completion in the foreground and paste its `Ran N … OK` line. Include at least: `tests.test_battery_float`, `tests.test_issue_calibration_acceptance_generation`, `tests.test_calibration_cadence_report`, `tests.test_epoch_continuation`, `tests.test_acc_25g83_rev5`, `tests.test_preregistration_chain_digest`, `tests.test_validate_powermetrics_fiducial_derivation_only`, `tests.test_night_gate`, `tests.test_evidence_night`, `tests.test_docs_freshness`, `tests.test_gen_state`. Never interrupt a slow module.
- Pin proof: paste `git diff --stat c6814dd8 -- <forbidden paths>` and confirm it is empty.
- Do NOT run full test discovery. No launchctl, powermetrics, sudo, installer or model inference. `ioreg` (read-only) is allowed.
- Work in ONE foreground session. Start no background tasks, subagents or watchers. Ending before your report exists is a protocol failure.
- Commit logically on this branch. Messages start "BFG-D:" and end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- Report to `08-seat-report-r4.md` in this directory and commit it. It must contain a table mapping each §4.10 item and test to file:line and result, the expected-value edits, the test tails, the pin proof, and any finding you believe §4 got wrong (with evidence; implement as ruled regardless unless impossible).
