# 03 — Cold Fable 5.1 final pass on PR #385 (branch diff at df92dbd6, read-only, fresh instance)

Launched by the interactive Fable session at ~02:35 PDT 2026-09-23 with `claude -p --model fable --effort high --permission-mode plan --allowedTools Read,Glob,Grep,Bash`; prompt at the end of this file. Cost $2.00, 152 s, 13 turns. Verdict and cures verbatim:

```
**Verdict: APPROVE WITH CURES.** Nothing in the diff is false. Four lines invite misreads.

**(1) Rule 11 reading.** Sound. Rule 11 already places the turn-by-turn loop with the lieutenant and reserves adjudication for a cold Fable instance. The 2026-09-23 amendment in CLAUDE.local.md says the same. Ed's verbatim ruling in record §6 orders only the final pass and equal reverence. The Opus-runs-the-loop placement was Fable's judgment under Ed's delegation, so the prompt's attribution "(Ed, 2026-09-23 …)" slightly overclaims.

The line: "before any merge and before any arm, obtain a cold Fable verdict (`claude -p --model fable`, fresh worktree, no loop context) … a Fable final-pass refusal is a stop." That is **mandatory in text, advisory mechanically**. For merges the only hook is gate-ledger row 7, which the check marks advisory and which verifies evidence exists, not which model wrote it. For arms there is no hook at all. The watchdog enforces nothing here.

**(2) Two-model hazard.** Real but fail-loud in the worst case. CLI 0.153.3 rejects a 6.0 model request outright, per the bench note in record §6. The silent case is a caller omitting the model and getting 5.6 with no label in the MCP result. Visible only in the rollout JSONL session header under ~/.codex/sessions. The exec route is safe: the manifest records the session-header model, and the user config defaults to gpt-6-sol. One misread surface: the check script prints the current binary's version directly above the MCP-model PASS line.

**(3) Cures, exact:**
- `scripts/check-codex-mcp.mjs` line 242: label the version PASS as the exec-route CLI and print the pinned MCP CLI version beside it.
- Relaunch prompt line 21: attribute the Opus-loop placement to Fable under Ed's delegation. Name row 7 as the final-pass evidence row.
- Same line: the user config sets effort medium, so say "pass --effort high" for codex-run-v3.
- `SKILL.md` line 95: "removed … 0.154 onward, 2026-09-23" reads as a removal date. Write "(observed 2026-09-23)".
--- cost 2.00132025 turns 13 dur 152206
```

## Disposition (interactive Fable, author)

All four cures applied in commit 746caca5 (bridge-check version line labelled with both CLIs; topology line attributes the placement to Fable under Ed's delegation, names row 7, pins --effort high; 'observed' wording). The two kept findings (final pass mandatory in text but advisory mechanically; MCP two-model hazard fail-loud) are recorded for the magistrate as follow-up lanes.

## Prompt

```
COLD FABLE 5.1 FINAL PASS (read-only; you are a fresh instance with no loop context). Do not modify anything; only Read/Glob/Grep and read-only Bash. Review the change set: git -C /Users/edr/code/JouleWise-wt-sol6 diff origin/main (11 files). Context: Codex CLI updated to 0.156.1 which removed 'codex mcp-server'; exec route moves to gpt-6-sol; MCP route pinned to npx @openai/codex@0.153.3 with gpt-5.6-sol; magistrate watchdog launches --model opus (Ed's 2026-09-23 directive: Opus 5.5 runs the loop, Fable 5.1 does the final pass); relaunch prompt gains one topology line. Answer the design-level questions: (1) Is running the headless magistrate on Opus 5.5 with a cold Fable final pass a sound reading of rule 11 in /Users/edr/code/JouleWise/CLAUDE.local.md, and does the new prompt line make the final pass mechanically mandatory or merely advisory? Quote the line and say which. (2) Does pinning the MCP route to an old CLI create a silent two-model hazard (a seat believing it is on Sol 6.0 while on 5.6)? Where would that be visible? (3) Any line in the diff that is false or that a successor could misread. Verdict: APPROVE / APPROVE WITH CURES (list exact cures) / REFUSE, under 300 words.
```
