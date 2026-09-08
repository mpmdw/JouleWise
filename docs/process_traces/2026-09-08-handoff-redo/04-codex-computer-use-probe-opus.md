# Codex computer-use probe through the bridge layers (Opus agent, 2026-09-08 ~01:00 PDT)

Ed's directive (memory `astra-computer-use-directive`): GPT models lead on computer use; Astra may be invoked
for GUI-bearing machine prep only once the bridge (a) exposes Codex's computer-use tool and (b) reports each
computer action in an auditable transcript. This probe checked both, on all three layers, with gpt-6-astra.
Probe artifacts: scratchpad `cu-probe/` (raw-probe.jsonl, wrapper-probe.{md,log,codex-observer.jsonl,status},
session-tool-inventory.md). No repo file was touched by the probe; no GUI click or keystroke was issued.

## Headline

Computer use IS exposed to gpt-6-astra on all three layers. The tool is MCP server `cua_repl`, tool `js`
(model-facing `mcp__cua_repl.js` and `mcp__cua_repl.js_reset`): a JS REPL whose `cua` API has
`getScreenshot()`, `getAXStateAndScreenshot()`, `click()`, `typeText()`, `getApp()`. It is supplied by the
`unified-computer-use@openai-bundled` plugin enabled in `~/.codex/config.toml`; `codex features list` shows
`computer_use stable true`.

NO screenshot was captured on any layer: every app-binding attempt was refused. Capability PRESENT and CALLABLE
is verified; capability ABLE TO SEE OR DRIVE THE SCREEN is not. Do not claim the latter.

| Layer | CU tool present | Screenshot executed | Action reporting | Blocker | Minimal change |
|---|---|---|---|---|---|
| A. raw `codex exec --json` | yes (`cua_repl/js`) | no: 1 `cua.getState()` completed, 3 app bindings failed | FULL: `--json` stream carries `mcp_tool_call` items with verbatim `code` and result | per-app CU grant missing; Terminal + Codex app hard-denied | none |
| B. `codex-run-v3` | yes (same) | no (same 4 calls) | WEAK in wrapper artifacts (`.log` has only `mcp: cua_repl/js started/completed/failed`, no args/results; observer JSONL has no tool events); FULL only in the Codex rollout `~/.codex/sessions/Y/M/D/rollout-*-<session_id>.jsonl` | same | emit the rollout path in the `FINISHED` observer event (~3 lines) |
| C. project MCP server (`.mcp.json`) | yes (`mcp__cua_repl.js`) | not attempted (read-only probe) | WEAK: `mcp__codex__codex` returns only the final message; full record only in the rollout (`session_meta.source="mcp"`) | same | harvest rollout by threadId |

## Evidence (verbatim)

Tool invoked (layer A): `{"type":"item.completed","item":{"id":"item_2","type":"mcp_tool_call","server":"cua_repl","tool":"js","arguments":{"code":"await cua.getState();","title":"Inspect enabled computer-use surfaces"},"status":"completed"}}`
Result carried the Computer Use system card (full `cua` TypeScript API) and a live app inventory (Wispr Flow,
ChatGPT, Terminal, Spotify, Finder, System Settings, Firefox, ProtonVPN, VS Code, Discord; `"browsers":[]`).

Three binding attempts, all `"status":"failed"`:
- `Computer Use is not allowed to use the app 'com.openai.codex' for safety reasons.`
- `Computer Use is not allowed to use the app 'com.apple.Terminal' for safety reasons.`
- `Computer Use was not approved to use Finder`
Model's closing lines: `CU_AVAILABLE: yes` / `CU_EXECUTED: yes` / `REPORTING: … captured zero screenshots and performed no clicks or typing.`

Wrapper (layer B): the sole `codex exec` call at `~/.local/bin/codex-run-v3:839` passes only `-m`, `-c
model_reasoning_effort`, `-c service_tier`, `-C`, `-s`, `-o`; no `--no-plugins`, `--ignore-user-config`,
`features.*` or `mcp_servers.*` override, so the user config (and its plugins) loads in full. `-s workspace-write`
governs model-issued shell commands, not the `cua_repl` MCP server process. Wrapper run reproduced layer A exactly.

MCP server (layer C): session `01a08007-2305-7290-bfca-0728a11747b3` (gpt-6-astra) listed `mcp__cua_repl.js`
among its tools and executed one `cua.getState()`. `.mcp.json`'s `-c mcp_servers.claude.enabled=false` disables
only the reverse Claude bridge, not plugins.

## Blockers, precisely

1. Per-app Computer Use approval is not granted. "was not approved to use Finder" is a Codex-side per-app
   grant, not a macOS TCC error. Non-interactive `codex exec` runs with `approval: never` and cannot answer an
   approval elicitation, so the grant must PRE-EXIST (granted from the Codex desktop app's approval flow).
2. Terminal and the Codex/ChatGPT app are hard-blocked "for safety reasons": no grant lifts this. A session
   cannot screenshot its own terminal or the Codex app.
3. macOS Screen Recording / Accessibility status for
   `/Users/edr/.codex/computer-use/Codex Computer Use.app/Contents/SharedSupport/SkyComputerUseClient.app` is
   UNKNOWN: no capture call was reached, so no TCC error text exists.

## Governance gaps found

- `WRITE_SCOPE` enforcement is built from `git status`/`git diff` of `$CDIR`; a GUI action changes no tracked
  path and is INVISIBLE to WRITE_SCOPE, exit-77 and the evidence bundle. Any seat permitted computer use needs an
  explicit computer-use scope clause in its brief; exit-77 will not catch a violation.
- Under `codex-run-v3` the auditable action record lives only in the Codex rollout; the wrapper should surface
  its path.

## What Ed must do to convert "present" into "exercised" (Ed-hands; prediction, not observation)

1. In the Codex desktop app, grant Computer Use for one harmless test app (Spotify, System Settings, or Wispr
   Flow; Terminal and ChatGPT are permanently refused).
2. If the capture then fails with a TCC error, grant Screen Recording and Accessibility in System Settings →
   Privacy & Security to the `Codex Computer Use.app` / `SkyComputerUseClient.app` binary.
3. Re-run the raw probe (`scratchpad/cu-probe/prompt.txt`) against the granted app.
