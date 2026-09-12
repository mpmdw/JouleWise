SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

DELTA RE-AUDIT of fix round 5 for lane NIGHT-INTERPRETER-PIN-01 (PR #321), branch fix/2026-09-11-night-interpreter-pin at HEAD e46f06c8 (one commit over 6dddb545, which re-audit 08 judged MERGEABLE and Opus counter-review 06 judged MERGEABLE AFTER FIXES with F1/F3/F4 should-fix; F2 was declined by the lead — untestable on macOS because the old plutil path was absolute, the string tripwire plus ubuntu CI are the guards; N1–N7 not taken). Read-only; temp files only under /tmp. Read /Users/edr/code/JouleWise-wt-bk-3dab9c89/docs/process_traces/2026-09-11-activation-3dab9c89/06-opus-counter-review-pr321.md (F1, F3, F4 and their dictated cures), then 'git diff 6dddb545..HEAD'.

Judge with commands + output:
1. F1 CURED? docs/contracts/pack_night_go_receipt.md: the §7.1 cell again reads ':39–75,132–141' (verify those ranges against 'git show d3cab2d4c2937886a25659756374483c7a8dc578:scripts/install_night_agent.sh'); the one dated sentence added after the preamble names ':91–122' and ':182–220' — verify both ranges at HEAD (NightPlan validation heredoc; render() through its closing brace). No other cell changed.
2. F3 CURED? tests/test_install_night_agent.py::InstallNightAgentTests::test_default_derivation_refuses_when_measurement_root_cannot_be_read: run it verbosely; confirm each of the four subTests exercises a DIFFERENT failure path of the installer's derivation line (instrument or reason from the code: json KeyError, JSONDecodeError, empty string, env: python3 not found) and that the asserted stderr is the installer's exact single line. Does the 'no-python3-on-path' case really have no python3 (PATH = one empty directory; the installer's other calls are absolute /usr/bin/... — do any of them need PATH?) and does it fail at the derivation rather than earlier?
3. F4 CURED? docs/phase_2/derivation_night_runbook.md: '--render-only DIR' is glossed at its first (only) use; the gloss matches NIGHT_HANDBACK.md's wording; the sentence still reads correctly.
4. Same-signature statement: round 5's classes (provenance of a baseline table; missing coverage; a doc gloss carried into a second file without its parenthetical) versus rounds 1–4 (whole-driver parsing under old python; doc/uninstall inconsistencies; macOS-only bootstrap; rescanned substitution). Same or different? Any surviving class?
5. python3 -m unittest tests.test_install_night_agent tests.test_run_night (expected 110); /bin/zsh -n scripts/install_night_agent.sh; git diff --check 6dddb545..HEAD.
6. Fresh-eyes on the whole unit as a merge candidate at HEAD (git diff origin/main..HEAD): anything a reviewer who has not seen rounds 1–5 would object to. Keep to material points.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: MERGEABLE | MERGEABLE AFTER FIXES | BLOCKED and the claude-codex-report/v1 envelope.
