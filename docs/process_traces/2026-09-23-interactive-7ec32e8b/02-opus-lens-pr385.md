# 02 — Opus 5.5 lens (contract + execution) on PR #385 (branch diff, read-only)

Launched by the interactive Fable session at ~02:35 PDT 2026-09-23 as an Agent-tool subagent (model opus, general-purpose, read-only brief: contract, execution, risk, overbuild). 115k tokens, 35 tool uses, 4.8 min. Report verbatim:

```
Verdict: MERGEABLE WITH FIXES. The code is correct and the tests pass. The fixes are three stale doc lines and one doctrine conflict that sits outside the diff.

Should-fix
1. Doctrine conflict outside the diff, which can stop the next activation. The memory file fable-model-pin.md says "confirm the system prompt says Fable 5.1; if not, stop and tell Ed", and says never to spawn a magistrate on a non-Fable model. CLAUDE.local.md rule 11 still says "Ed's direct is Fable, as MAGISTRATE". An Opus magistrate loads both. The only counter-signal is the new line in docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:21, and it says "may run on Opus", which is weaker. Update the memory and rule 11, or have that line explicitly override the stop-if-not-Fable rule.
2. docs/process/MAGISTRATE_WATCHDOG.md:309 tells the operator to look for a resident with "--model fable --effort high". An Opus resident would not match that manual check. The watchdog code tracks the resident by PID and start token, so only the doc is wrong.
3. CLAUDE.md:9 says "The tracked .mcp.json starts codex mcp-server." It now starts npx -y @openai/codex@0.153.3 mcp-server.

Nits
- "removed from CLI 0.154 onward" appears in SKILL.md, CLAUDE.md and the check-codex-mcp.mjs comment. Only 0.153.3 and 0.156.1 were observed (record §6). "Absent in 0.156.1" is what the evidence supports.
- check-codex-mcp.mjs:241 prints "PASS: codex-cli 0.156.1", but the MCP server it tests is 0.153.3. The evidence line is misleading.
- CLAUDE.md still calls the MCP route "Primary Path", while Sol 6.0 runs only on the exec route.

Execution
- (a) .mcp.json and expectedCodexArgs match byte for byte, and the command is npx in both. I parsed both and compared them; I did not run the bridge check.
- (b) The census pattern still matches. Live pgrep -lf "[c]odex|[c]laude|[t]3" hit all three npx layers of the cold-Fable session's server: npm exec @openai/codex@0.153.3 mcp-server (49593), node …/_npx/…/.bin/codex mcp-server (49614) and the vendor codex binary (49629). arm_census builds its hits from the same pattern, and the watchdog finds its own children by ancestry, so the extra npm layer stays inside the owned tree.
- (c) The tests pass: 212 across codex_app_bridge, claude_bridge_mcp, magistrate_watchdog, night_gate, arm_census and prewindow_check, plus 158 across codex_bridge_observer, bridge and quiet_guard. No test hardcodes the watchdog's "fable" flag.

Risk
- Live activation (7a0f14bd, 39211): its Codex MCP children (39227 and 39231) are still running the old in-memory binaries. If they die, a reconnect runs codex mcp-server, which is 0.156.1 on disk and fails. Canonical .mcp.json is already broken for the same reason, so merging this PR repairs it rather than causing it.
- Next activation: it gets Opus only after the canonical checkout fast-forwards; launchd runs the watchdog from canonical every 300 s.
- npx -y depends on npm resolution at each launch. I did not test it offline.
- Nothing here is irreversible.

Overbuild: none.

Same-signature: none of these findings repeats a class from prior rounds.
```

## Disposition (interactive Fable, author)

Should-fix 1: memory `fable-model-pin.md` amended, `CLAUDE.local.md` rule 11 carries a dated amendment, and the relaunch-prompt line now explicitly supersedes the stop-unless-Fable rule. Should-fix 2 and 3: fixed. Nits: "absent in 0.154.0, 0.155.0 and 0.156.1 (checked 2026-09-23)" is what was actually observed (npx probes of 0.154.0 and 0.155.0 printed the generic CLI help, i.e. no such subcommand), so that wording is used; the version PASS line was already cured by the Fable final pass; "Primary Path" renamed. All in commit cfc343c9. The `npx -y` offline dependency is accepted and noted for the magistrate (the npx cache holds 0.153.3 after the first run).
