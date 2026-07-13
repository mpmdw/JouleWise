# 2026-07-12 adaptive Claude Code ↔ Sol/Fable bridge

## Outcome

The JouleWise agent bridge is now usable in both directions:

- Claude Code starts or continues full `gpt-5.6-sol` sessions through the
  project Codex MCP server. `high` is the fallback and normal individual-task
  default; Claude selects `xhigh` only for named hard-task triggers and
  `ultra` only when Sol itself must spawn subagents.
- A top-level Codex session can ask Claude Fable for one bounded, read-only
  peer judgment through the sole reverse MCP tool, `consult_fable`.

The bridge has a hard one-hop boundary. The Claude-facing Codex server starts
with `mcp_servers.claude.enabled=false`, so a Claude-originated Sol session
cannot discover the reverse server. The reverse adapter launches Fable with an
empty MCP registry, disabled slash commands, no session persistence, plan
permission mode, and only `Read`, `Grep`, and `Glob`.

This was user-directed `[AGENT]` process/tooling work. It did not start a
`[QUIET-MAC]` measurement, change research evidence, or alter advisor-visible
claims.

## Effort policy found and reconciled

The existing personal Claude policy was found in `~/.claude/CLAUDE.md` and
`~/.claude/skills/codex-delegation/SKILL.md`. It already reserved `ultra` for
Sol sessions that spawn subagents, but still said individual work used xhigh by
default. The user's newer instruction superseded that wording. Both personal
files and all tracked JouleWise Claude entry points now use:

- `high`: normal individual work, including bounded/mechanical tasks,
  docs/config, straightforward implementation, named FIX rounds, and ordinary
  focused review;
- `xhigh`: design-bearing, cross-contract/multi-component, non-local
  root-cause, adversarial/integration-review, or otherwise judgment-dense work
  where an incorrect answer is materially costly;
- `ultra`: only when the Sol session itself must spawn subagents.

When high versus xhigh is uncertain, the policy says to start high and escalate
only when an xhigh trigger actually appears. `~/.codex/config.toml` already
used `gpt-5.6-sol` / `high`; no Codex personal-config change was needed.

## Bridge architecture

### Claude Code → Sol

- `.mcp.json` starts `codex mcp-server` pinned to `gpt-5.6-sol`, `high`
  fallback effort, and `mcp_servers.claude.enabled=false`.
- The tracked Claude agent, `/codex` command, and project Codex skill classify
  task difficulty, pass the model and selected effort explicitly, set the
  narrowest sandbox, retain `on-request` approvals, and attach
  `BRIDGE_ORIGIN: claude` / `BRIDGE_HOPS_REMAINING: 0`.
- `codex-reply` remains the continuation path. Substantial D-050/D-064 work
  still uses `codex-run-v3` when available.
- `scripts/codex-bridge` now pins/records model and effort for new, resumed,
  and review calls. Its fallback is `high`, with deliberate environment
  overrides for xhigh or ultra.

### Top-level Codex → Fable

- `.codex/config.toml` registers `scripts/claude-bridge-mcp.mjs` as the project
  `claude` MCP server and exposes only `consult_fable`.
- `.agents/skills/claude-consult/SKILL.md` gives Codex the invocation and
  adjudication contract.
- The adapter rejects calls without `BRIDGE_ORIGIN: codex` and
  `BRIDGE_HOPS_REMAINING: 0`, invokes Claude without a shell, pins Fable/high,
  and bounds output and runtime.
- Only this single tool is preapproved for non-interactive Codex use. The
  Fable response is advice; the calling Codex session remains lead.

An initial `claude mcp serve` design was rejected after live testing. Its MCP
schema exposed `Agent`, but its serving context had an empty subagent registry;
both the default `general-purpose` and an explicitly injected `fable-consult`
profile failed with “Agent type ... not found.” A direct no-tools registry
check proved the custom profile itself was valid. No echoed token after either
failed tool call was accepted as evidence. The purpose-built adapter uses
Claude Code's supported non-interactive model entry point instead.

## Files changed

- Agent bridge/config: `.mcp.json`, `.codex/config.toml`,
  `scripts/claude-bridge-mcp.mjs`, `scripts/codex-bridge`,
  `scripts/check-codex-mcp.mjs`.
- Claude/Codex discovery surfaces: `.claude/agents/codex.md`,
  `.claude/commands/codex.md`, `.claude/skills/codex/SKILL.md`,
  `.agents/skills/claude-consult/SKILL.md`, `.gitignore`.
- Policy/process: `AGENTS.md`, `CLAUDE.md`, `RUN_STATE.md`, `TASK_QUEUE.md`,
  and this report.
- Focused regressions: `tests/test_claude_bridge_mcp.py`.
- Personal Claude policy (outside Git): `~/.claude/CLAUDE.md` and
  `~/.claude/skills/codex-delegation/SKILL.md`.

## Verification

Installed runtime and protocol checker:

```text
codex-cli 0.144.0
Claude Code 2.1.207
Node.js v23.7.0

PASS: Claude -> Sol MCP exposes full-session start and continuation controls
PASS: Claude -> Sol defaults to gpt-5.6-sol with high fallback effort
PASS: Claude-originated Sol sessions disable the reverse Claude server
PASS: Sol -> Fable MCP exposes only the guarded consult_fable tool
PASS: reverse bridge preapproves only consult_fable and enforces read-only one-hop policy
```

Static and focused checks:

```text
node --check scripts/claude-bridge-mcp.mjs
node --check scripts/check-codex-mcp.mjs
bash -n scripts/codex-bridge
git diff --check

python3 -m unittest tests.test_claude_bridge_mcp
Ran 4 tests in 0.271s
OK

python3 scripts/gen_state.py --check
exit 0
```

The audited CLI fallback was exercised with `/bin/echo` for `new`,
`resume --last`, and `review`. Every launch used `gpt-5.6-sol` / `high`,
disabled the reverse Claude server, and recorded the same model and effort in
its ephemeral manifest.

Live Claude Code `/codex` acceptance:

```text
token: JOULEWISE_SOL_HIGH_GUARDED_OK
thread: 019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26
source: mcp
model: gpt-5.6-sol
effort: high
sandbox: read-only
approval-policy: on-request
reverse Claude server: disabled
```

Live top-level Sol → Fable acceptance:

```text
token: JOULEWISE_FABLE_MCP_OK
Codex thread: 019f5a26-d8a6-7993-b48d-8131d88748b9
Codex model/effort: gpt-5.6-sol / high
Codex sandbox: read-only
MCP server/tool: claude / consult_fable
actual Fable tool result: JOULEWISE_FABLE_MCP_OK
```

The current canonical suite is not green for an unrelated concurrent
working-tree reason:

```text
Ran 1317 tests in 125.398s
FAILED (failures=1, errors=1, skipped=12)
```

Both failures are in `tests/test_gen_state.py`: concurrent separately owned
edits removed `P2-028` from `docs/process/state_kernel.json`, while the existing
fidelity tests still require that ID and mutate it in an invalid-kernel case.
The bridge did not edit either file. The generated-state check itself passes,
and all bridge-specific tests pass. Those separately owned state changes were
preserved for their owner to adjudicate.

## Process trace and boundaries

- Active stop card at intake: none. Mission M0 and orchestration rules were
  followed; no quiet-machine task was run.
- OpenAI docs skill: confirmed trusted project MCP configuration under
  `.codex/config.toml`, tool allowlists, and per-tool approval modes. Claude's
  official subagent documentation informed the rejected custom-agent probe;
  installed-runtime behavior determined the final adapter.
- No collaboration subagents were spawned for implementation. The only model
  sessions were bounded no-edit bridge acceptance calls described above.
- Main advanced concurrently from `0e7616a` to `99b8640`/`origin/main` during
  this work. Separately owned changes to `docs/process/state_kernel.json` and
  `docs/run_reports/2026-07-13-restart-merge-deploy.md` were preserved.
- No commit, push, PR, merge, deployment, destructive Git action, or site
  regeneration was requested or performed by this bridge work.

## Next exact step

In Claude Code, use `/codex <task>`; Claude will choose high/xhigh/ultra by the
recorded triggers, keep the thread id, and use `codex-reply` for continuation.
From a top-level Codex task, request the `claude-consult` skill when a bounded
independent Fable judgment would materially help. Do not use the reverse path
from a Claude-originated Sol session.
