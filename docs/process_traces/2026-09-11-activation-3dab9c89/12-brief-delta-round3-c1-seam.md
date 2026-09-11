SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

BOUNDED DELTA CHECK of fix round 3 for lane NIGHT-C1-REGISTRATION-DOCS-01 (PR #322), branch fix/2026-09-11-c1-registration-seam at HEAD 7fc058b9 (one commit over dc93749c; changes ONE paragraph, docs/phase_2/derivation_night_runbook.md §0.5 ~lines 503–512). Read-only; temp files only under /tmp. Read /Users/edr/code/JouleWise-wt-bk-3dab9c89/docs/process_traces/2026-09-11-activation-3dab9c89/09-delta-round2-c1-seam.md findings S1 and S3, then 'git diff dc93749c..HEAD'.

Judge with commands + output:
1. S1 CURED? Every factual claim in the new paragraph must be supported by primary evidence: the JSON file configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json (numerator, denominator, threshold, comparison, exact_equality_policy, per_component, all_must_pass), configs/campaigns/d117_contrast_v5/generate_configs.py::dominance_criterion_registration, docs/decision_log.md D-165 and D-166 entries, joulewise/night_gate.py:34–40 and :1300–1328. Quote each claim and its evidence line. Any unsupported or wrong claim is a SHOULD_FIX with the corrected sentence dictated verbatim.
2. S3 CURED? First-use census of the paragraph: list every term of art it uses (e.g. 'floor', 'energy component', 'dominance sentence', 'receipt class', 'C1') and for each say where the runbook builds or glosses it BEFORE this paragraph (line), or that the paragraph glosses it inline, or FLAG it. Judge 'floor' against the runbook's own earlier definition (grep -n -i 'floor' | head).
3. Does the paragraph still read as one clear explanation a reader could replicate the check from (the writing standard), or has accuracy made it opaque? If opaque, dictate a shorter accurate version.
4. python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate (expected 98); python3 scripts/gen_derivation_night.py --check; git diff --check dc93749c..HEAD.
5. Same-signature statement: round 3 re-cures the SAME class as round 2's S1 (misdescription of the registered criterion). If your answer to (1) is not fully CURED, say so in one line at the top — the lead's next move is then a consult, not a fourth round.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: MERGEABLE | MERGEABLE AFTER FIXES | BLOCKED and the claude-codex-report/v1 envelope.
