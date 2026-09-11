SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

DELTA RE-AUDIT of fix round 4 for lane NIGHT-INTERPRETER-PIN-01, branch fix/2026-09-11-night-interpreter-pin at HEAD 6dddb545 (one commit over 3b99a1a0, which re-audit 04 judged MERGEABLE AFTER FIXES with the single finding R1). Read-only: no tracked file may change; temp files only under /tmp. Read /Users/edr/code/JouleWise-wt-bk-3dab9c89/docs/process_traces/2026-09-11-activation-3dab9c89/04-delta-reaudit-interp-pin.md (finding R1 and Part B evidence), then 'git diff 3b99a1a0..HEAD'.

Round 4 (lead bench fix): render() in scripts/install_night_agent.sh substitutes template tokens in ONE pass with re.sub over the pattern r"com\.joulewise\.night|@@[A-Z_]+@@" and a dict lookup (unknown tokens are left as-is), so inserted values are never rescanned; a regression test renders with an interpreter symlink named 'python @@MODE@@ & pinned' and asserts argv[0] equality in both plists (it fails without the fix — the lead verified by stashing the installer change).

Judge, with commands + output:
1. Is the single-pass substitution byte-for-byte equivalent to the old sequential replace for every fixture plist the tests render today (diff the rendered outputs at 3b99a1a0 vs HEAD for at least the two-pins-matching case and the deadman case)? Any token in configs/launchd/com.joulewise.night.plist.template that the regex misses (grep -o '@@[^@]*@@' and compare with the replacements dict)? The label 'com.joulewise.night' also prefixes the deadman label — does the alternation order matter?
2. Re-run re-audit 04's R1 reproducer (/tmp/night-pin-reaudit-render-regression.py, if still present; otherwise author the equivalent) at HEAD: expected PASS.
3. Same-signature statement: is round 4's defect class (rescanned substitution) the same class as any earlier round's? State it explicitly.
4. Run python3 -m unittest tests.test_install_night_agent tests.test_run_night (expected 109) and /bin/zsh -n scripts/install_night_agent.sh.
5. Fresh-eyes on the one commit: anything a reviewer would object to (the 'import re' placement, regex escaping inside a zsh heredoc — is the heredoc quoted so backslashes survive? prove by extracting the rendered python source and compiling it).

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: MERGEABLE | MERGEABLE AFTER FIXES | BLOCKED and the claude-codex-report/v1 envelope.
