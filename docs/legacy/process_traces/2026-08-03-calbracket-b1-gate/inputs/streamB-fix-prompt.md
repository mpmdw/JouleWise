OBJECTIVE: Fix round 1 for commit 8383113 on impl/cal-bracket-d079 — close the independent audit's two blockers and one should-fix, exactly and narrowly. The audit report is at /private/tmp/claude-501/-Users-edr-code-JouleWise/d20c28cd-936a-44c6-a611-2f286532743a/scratchpad/streamB-audit.md — read it in full first. One commit. Structural shapes that passed audit are UNTOUCHED.

AUTHORITY: D-109 R1/R2 in /Users/edr/code/JouleWise/docs/decision_log.md (absolute path; main is ahead of this worktree); the audit findings B1/B2/S1 with their evidence lines.

FIXES:
B1 (blocker, R1.2/R1.4) — minted-consumption sessions bypass the ledger-snapshot refusal (whole_window.py:416, :490, :508; secondary verifier permits a missing session at :4584). Fix: minted-semantics sessions MUST also load the canonical ledger snapshot and refuse on pending/rollback/stale-head/head-mismatch exactly like non-minted paths; the secondary verifier must refuse a missing session rather than permit it. Regression: the audit's probe shape — a snapshot containing calibration_ledger_pending must make a minted session REFUSE (red pre-fix).

B2 (blocker, R2.3/R2.6) — content-bearing `abandoned` receipts are accepted as classifiable (validate_powermetrics_fiducial.py:372, calibration_ledger.py:303, :715, calibration_bracketing.py:884) though the R2 prior-set schema cannot represent `abandoned`. Fix per R2.6: `abandoned` is an UNRESOLVED class — a new abandoned observation (content-bearing or not) causes trigger evaluation to REFUSE until dispositioned; it never silently passes and never counts as classifiable. Align the finalization path so an abandoned receipt with content hashes is representable as unresolved evidence, not dropped. Regression: the audit's probe — a new content-bearing abandoned observation beside an otherwise valid bracket must produce refusal, not status=passed (red pre-fix).

S1 (should-fix, 4 regressions made genuinely defect-shaped):
- Cross-root expander test must exercise the PRODUCTION caller path (not the low-level evaluator directly) so restoring caller-root directory enumeration fails it (tests/test_calibration_bracketing.py:540).
- Prior-set test must discriminate: construct the case where treating a known holdout as "new" CHANGES the outcome (e.g. crosses a trigger threshold) (tests/test_calibration_bracketing.py:623).
- 38-total test must distinguish total-counting from post-cutoff-counting: 19 prior + 19 new distinct valids must TRIGGER under total counting and NOT under a defective post-cutoff count (tests/test_calibration_bracketing.py:643).
- Fork test must isolate a true sibling fork (same predecessor, different content, distinct sequence handling) so removing ONLY predecessor/fork checking fails it while sequence/duplicate checks alone do not catch it (tests/test_calibration_ledger.py:156).

Do NOT touch anything else. One commit citing the audit findings. VERIFICATION: python3 -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_whole_window_selection tests.test_reduce (green) + demonstrate each new/changed regression is red pre-fix (run against parent via in-memory mutant or git-show where cheap) + full suite (python3 -m unittest discover -s tests) with EXACT counts reported.

WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","joulewise/whole_window.py","scripts/validate_powermetrics_fiducial.py","tests/test_calibration_ledger.py","tests/test_calibration_bracketing.py","tests/test_whole_window_selection.py"]
EARLY_RETURN: NEEDS_SCOPE, NEEDS_RULING (e.g. if B1's minted-session snapshot requirement conflicts with a frozen minted-consumption contract — do not silently weaken either).
