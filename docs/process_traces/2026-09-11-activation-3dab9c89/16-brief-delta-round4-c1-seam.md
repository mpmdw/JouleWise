SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

BOUNDED DELTA CHECK of fix round 4 for lane NIGHT-C1-REGISTRATION-DOCS-01 (PR #322), branch fix/2026-09-11-c1-registration-seam at HEAD 66963ace (one commit over 7fc058b9; ONE paragraph of docs/phase_2/derivation_night_runbook.md §0.5 replaced with the text of consult record 15 §Q4). Read-only; temp files only under /tmp. Read /Users/edr/code/JouleWise-wt-bk-3dab9c89/docs/process_traces/2026-09-11-activation-3dab9c89/12-delta-round3-c1-seam.md (S3) and 15-opus-consult-pr322-paragraph.md (Q2 fact-check, Q3 census, Q4 text), then 'git diff 7fc058b9..HEAD'.

Judge with commands + output:
1. Is the committed paragraph byte-identical to consult 15 §Q4's text (diff them)? If not, list the differences.
2. Independently re-verify the paragraph's factual claims against primary evidence (joulewise/night_gate.py:30–42 and :1295–1330 — read_text UTF-8 then sha256; class table :536–543; pack identity fields :128–131; scripts/run_night.py:295; docs/decision_log.md D-165 and D-166 entries; §Terms 'Registration' at runbook :150–155; §1.1 for DIAGNOSTIC_NO_PACK; the 'twelve calibration captures' claim against the runbook's own slot count and configs/calibration/preregistration_d079_epoch_25g83_rev1.md). Any wrong or unsupported claim is a SHOULD_FIX with the corrected sentence dictated verbatim.
3. First-use test on the paragraph in the file's context: every term of art built earlier (line) or glossed inline; 'the file named at the top of this section' must actually be named at the top of §0.5 (quote the line). FLAG any failure.
4. python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate (expected 98); python3 scripts/gen_derivation_night.py --check; git diff --check 7fc058b9..HEAD; no line in the new paragraph longer than 79 columns.
5. Same-signature statement in ONE line at the top of your prose: is the first-use class (S3 of rounds 2 and 3) now CURED or does it survive? If it survives, say so plainly — the lead will not run a fifth round.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: MERGEABLE | MERGEABLE AFTER FIXES | BLOCKED and the claude-codex-report/v1 envelope.
