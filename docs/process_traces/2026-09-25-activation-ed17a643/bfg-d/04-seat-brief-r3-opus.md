# BFG-D round 3 — implementation seat brief (Opus 5.5; Codex unavailable since ≈15:40 PDT, 401)

You are the implementation seat for PR BFG-D on branch `feat/2026-09-25-bfg-d` in this worktree. Two earlier Sol seats left UNVERIFIED work committed at `7e1c5463` (round 1) and `cee37ea9` (round 2; its final report was lost when Codex auth failed). Treat all of it as a draft by an unknown author.

Read, in order, and follow exactly (later overrides earlier):
1. `01-seat-brief.md` (original brief; its WRITE_SCOPE line is superseded by the list below)
2. `00-final-texts-v1.1-source.md` §5 — the ONE source of truth (cold ruling)
3. `03-lead-rulings-r1.md` — lead rulings R1–R5
4. `02-seat-report-r1.md` — round 1's report (orientation only)

WRITE SCOPE (exhaustive): `joulewise/battery_float.py`, `joulewise/night_gate.py`, `joulewise/arm_retry.py`, `joulewise/evidence_night.py`, `joulewise/night_agent_install.py`, `joulewise/arm_readiness_evidence_t0.py`, `scripts/validate_powermetrics_fiducial.py`, `scripts/issue_calibration_acceptance_generation.py`, `scripts/calibration_cadence_report.py`, `scripts/issue_epoch_continuation.py`, `docs/process/NIGHT_HANDBACK.md` and `docs/phase_2/derivation_night_runbook.md` (ARM-RETRY-POLICY v1 block only), `tests/**`, and this directory for your report. Anything else: stop and report NEEDS_SCOPE. FORBIDDEN (pinned; test 5 proves unchanged): `joulewise/calibration_bracketing.py`, `joulewise/adapters/powermetrics.py`, `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/reduce.py`, `protocol_v3.json`, `scripts/night_chains/**`, `configs/**`.

WORK:
- Audit the draft against every §5.3 BFG-D item (1–7), every §5.5 clause (validator + issuer contract 1–6) and R1–R5; fix what is wrong; finish what is missing. §5.6 tests 1–11 must ALL exist and pass at the named production call sites (3, 5, 6, 8 and 9 were missing after round 1; verify round 2's state yourself).
- Never weaken, delete or loosen a pre-existing assertion. The only permitted edits to existing expected values add the new battery field or probe (R1); list each one with before and after in your report.
- Run to completion, in the foreground, and paste the final `Ran N tests … OK/FAILED` line for each of: `tests.test_battery_float`, `tests.test_night_gate`, `tests.test_arm_retry`, `tests.test_evidence_night`, the night_agent_install tests, the arm_readiness_evidence_t0 tests, `tests.test_validate_powermetrics_fiducial_derivation_only` plus any other validate_powermetrics_fiducial module, `tests.test_issue_calibration_acceptance_generation`, `tests.test_calibration_cadence_report`, the issue_epoch_continuation tests, `tests.test_acc_25g83_rev5` and `tests.test_preregistration_chain_digest`. Find the exact module names with `ls tests | grep -E '...'`. Slow modules are expected; never interrupt one.
- Pin proof: `git diff --stat c6814dd8 -- <each forbidden path>` must be empty; paste it.
- Do NOT run full test discovery; the lead runs it.
- Never run launchctl, powermetrics, sudo, the installer or model inference. You may run `ioreg -r -c AppleSmartBattery` (read-only).
- Work in ONE foreground session. Start no background tasks, subagents or watchers; if you end before your report file exists, that is a protocol failure.
- Commit in logical commits on this branch. Each message starts "BFG-D:" and ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- Write your report to `05-seat-report-r3.md` in this directory and commit it. It must contain the §5.3/§5.5/§5.6 → file:line → test table, the list of expected-value edits, the test tails, the pin proof, and any finding you think the ruling got wrong (with evidence; implement as ruled regardless unless it is impossible).
