SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

DELTA RE-AUDIT of fix round 2 for lane NIGHT-C1-REGISTRATION-DOCS-01 (PR #322), branch fix/2026-09-11-c1-registration-seam at HEAD dc93749c (one commit over 1f8c1174). Read-only; temp files only under /tmp. Read /Users/edr/code/JouleWise-wt-bk-3dab9c89/docs/process_traces/2026-09-11-activation-3dab9c89/07-opus-counter-review-pr322.md (findings B1, S1, S2 with dictated cures; N1–N4 were not taken), then 'git diff 1f8c1174..HEAD'.

Judge with commands + output:
1. B1 CURED? grep -n '\$H:' docs/phase_2/derivation_night_runbook.md must be empty; execute both braced commands (§1.5 blob id, §2.5 re-hash) in /bin/zsh against this worktree with MEASUREMENT_ROOT=$PWD and H=$(git rev-parse HEAD): the blob id and the digest must be non-empty and the digest must NOT be e3b0c442… (sha256 of empty input). Also: does zsh treat "${H}:path" correctly inside the runbook's fenced zsh blocks as written (quote the exact lines)?
2. Regression test tests/test_night_gate.py::RegistrationSeamTests::test_runbook_never_writes_unbraced_dollar_h_before_a_colon: run it; then show it FAILS against 1f8c1174's runbook (git show 1f8c1174:docs/phase_2/derivation_night_runbook.md > /tmp/rb.md and apply the same regex) and name the two offending lines. Does the regex r"\$H:" also catch "$H:" inside inline code and prose, and could it false-positive on any legitimate use (e.g. a sentence about the defect)? State whether the parenthetical the lead added at §2.5 avoids the literal.
3. S1 CURED? Read the new §0.5 sentence (about the dominance criterion, D-165's falsifier, file named for D-166): verify each factual claim against joulewise/night_gate.py (D166_REGISTRATION_PATH / SHA256, the registration builder) and docs/decision_log.md D-165/D-166 entries, and against the JSON file's content (ratio_id, threshold). Any claim not supported by primary evidence is a finding. First-use test: every term in the new sentence is glossed or built before use in the file.
4. S2 CURED? Read the arm-record item 1 cell: does it now unambiguously name the frozen CALIBRATION plan (`$CALIBRATION_PLAN`, §0.2) and distinguish it from night_plan.json; does `$CALIBRATION_PLAN` exist as a variable in the runbook (grep) or is it a name the lead invented? If invented, that is a SHOULD_FIX with the correct variable name dictated.
5. Same-signature statement: round 2's classes (zsh expansion defect in a doc command; two misdescriptions) versus round 1's (a first-use gloss) — same or different? Any surviving class?
6. python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate (expected 98) and python3 scripts/gen_derivation_night.py --check.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: MERGEABLE | MERGEABLE AFTER FIXES | BLOCKED and the claude-codex-report/v1 envelope.
