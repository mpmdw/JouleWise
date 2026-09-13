# Refuter brief — NIGHT-CENSUS-CHATGPT-APP-01 install (branch fix/2026-09-13-night-census-desktop-apps, HEAD cda6b727), EXECUTION + FIRST-USE lens (Astra high; workspace-write for temp dirs, WRITE_SCOPE [])

SESSION_MODE: delegated
WRITE_SCOPE: []

You are in a detached review worktree at HEAD `cda6b727` (base main `27957b60`; diff = `git diff 27957b60..HEAD`: two docs files + one test). Read-only on tracked files; temp dirs allowed; never touch `/Users/edr/code/JouleWise` (its `.venv/bin/python3` may be used read-only), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. No network.

The ruling being installed (read-only): `/Users/edr/code/JouleWise-wt-bk-24b9d3dd/docs/process_traces/2026-09-13-activation-24b9d3dd/05-coldgate-packet-night-census-chatgpt/10-coldgate-fable-ruling.md`, the pairing refuter `12-…md` (amendments A1–A3 with exact replacement text) and the synthesis `13-…md` beside it.

Try to BREAK the install:
1. Fidelity: the installed runbook paragraph equals refuter 12's A2 + A3 text byte-for-byte (allowing only line re-wrapping); the NIGHT_HANDBACK sentence equals A1's text; the test equals ruling 10's test verbatim. Diff them mechanically (normalise whitespace) and paste any difference.
2. Placement: the runbook paragraph sits as a new paragraph directly after the §0.6 opening paragraph (the one beginning "`[QUIET-MAC]` nights are agent-free.") and before "Before the arm census"; quote the three surrounding lines.
3. First-use test on the installed prose, in the documents where it lands: every term of art in the new text (agent runtime, census, plan span, t0, helper process, refuses the night, arm) is defined at or before its first use in THAT document, or glossed inline. Give the defining line number for each, or name the term that fails.
4. Truth on this machine: run `/usr/bin/pgrep -lf "codex|claude|t3"` and show (a) at least one ChatGPT helper line, (b) that the top-level `/Applications/ChatGPT.app/Contents/MacOS/ChatGPT` process does NOT appear (grep it separately with `pgrep -lf ChatGPT.app/Contents/MacOS/ChatGPT`), confirming the paragraph's parenthetical claim.
5. Tests: `python3 -m unittest tests.test_night_gate` (paste the tail); then the mutation: in a temp copy of the module + `joulewise/night_gate.py` under /tmp, narrow the literal to `"codex mcp-server|codex exec|claude|t3"` and show the new test FAILS; restore. `python3 -m unittest tests.test_docs_freshness` (the runbook is a reader-facing doc). `git diff --check 27957b60..HEAD`. `git status --short` empty.
6. Anything else: a sentence that is true on one checkout and false on the one the operator uses (the 09-15 clone stays at 27957b60 without this text — does any installed sentence claim otherwise?).

Report (claude-codex-report/v1, genre review) as your FINAL MESSAGE, severity-tiered with file:line, pasted evidence, and "what the lead should double-check". Under 8000 bytes.
