# Claude Code → native Codex pet bridge

Date: 2026-07-18  
Lane: `[AGENT]`  
Task: `CODEX-BRIDGE-PET`

## Outcome

Claude Code's actual audited fallback, `scripts/codex-bridge`, can now run its
real Sol turn inside a dedicated Codex desktop task. The native pet therefore
sees the same running local conversation as the app UI instead of relying on a
parallel marker file.

The change does not alter routing policy: the model remains `gpt-5.6-sol`,
`high` remains the safe fallback and ordinary-task default, `xhigh` remains
trigger-only for hard individual work, and `ultra` remains reserved for Sol
sessions that must spawn subagents.

## Corrected root cause

Recent `.codex-bridge/invocation_manifest.jsonl` rows and a live Claude review
showed that Claude Code was invoking `scripts/codex-bridge`, which launched
standalone `codex exec` processes. Those processes were real and consumed plan
usage, but the Codex desktop pet did not react.

The first attempted diagnosis treated
`~/.codex/claude-spawned/index.jsonl` as the pet's input. Inspection of the
installed Codex desktop app disproved that assumption: the pet derives its
running state from app-server-owned local conversations. Neither standalone
`codex exec` nor the project MCP server becomes a running conversation in the
desktop app merely by writing observer events.

The Codex desktop app does expose a user-owned IPC router and a versioned
thread-follower operation. A follower turn runs on an app-owned conversation,
which gives the pet genuine state and keeps the result available to the script
caller.

## Implementation

- Added `scripts/codex-app-bridge.mjs`, a narrow desktop thread-follower client.
  It uses the configured app-owned bridge thread, passes the selected model,
  effort, cwd, approvals, and read-only/workspace-write sandbox to the turn,
  and captures `task_complete.last_agent_message` from the app-owned rollout.
- Updated `scripts/codex-bridge` so `new` and `review` use that native route
  when the ignored local `.codex-bridge/app-host-thread-id` exists. Machines
  without that local bootstrap retain the standalone CLI route;
  `CODEX_APP_BRIDGE=off` selects it explicitly.
- App turns are serialized with an ownership lock. Wrapper termination sends
  `thread-follower-interrupt-turn`, preventing the app conversation and pet
  from remaining falsely busy.
- The existing `.codex-bridge/` prompt, response, log, status, manifest, and
  observer artifacts remain intact. Manifest rows now distinguish
  `desktop-thread-follower` from `cli-bridge`.
- Removed the provisional MCP observer proxy after confirming that its JSONL
  events could not drive the native pet. Documentation now separates external
  diagnostics from the pet's app-conversation state.

The local bridge host created during this run is Codex app thread
`019f77a6-3612-7332-9f5e-be9fbde56be5`. Its id is machine-local runtime state,
not a tracked repository setting. After a Codex desktop restart, open the
"Bootstrap Claude bridge host" task once if the app has not restored it; the
bridge fails with that explicit recovery instruction instead of silently
falling back to an invisible standalone process.

## Live proof

The real wrapper command ran a read-only `gpt-5.6-sol` turn at `high` effort
through the desktop route. The helper reported:

- app thread: `019f77a6-3612-7332-9f5e-be9fbde56be5`
- turn: `019f77a9-2827-7de1-accf-ac2eda21927e`
- final token: `JOULEWISE_NATIVE_PET_BRIDGE_OK`
- manifest transport: `desktop-thread-follower`
- result: `OK`

The Codex app's own thread reader independently returned that turn as
`completed`, including its commentary, final bridge envelope, and eight-second
read-only smoke command. This proves that the script's actual Sol work was an
app-owned local conversation—the state the pet consumes.

## Verification

- `python3 -W error::ResourceWarning -m unittest tests.test_codex_app_bridge`
  — 2 tests, OK with normal user-level Unix-socket access. Covers the exact
  desktop request fields, answer capture, termination interrupt, and lock
  cleanup. The restricted test sandbox cannot bind Unix sockets, so these
  tests skip there rather than producing a false failure.
- `python3 -W error::ResourceWarning -m unittest
  tests.test_codex_bridge_observer` — 3 tests, OK.
- `bash -n scripts/codex-bridge` — OK.
- `node --check scripts/codex-app-bridge.mjs` — OK.
- Live native route smoke described above — OK.
- `scripts/check-codex-mcp.mjs` — all installed-runtime checks PASS with Codex
  CLI 0.144.0, Claude Code 2.1.214, and Node.js 23.7.0. The restricted first
  attempt could not write Codex's user state DB; the normal user-level rerun
  passed.
- `python3 scripts/gen_state.py --check` — OK.
- `git diff --check` — OK.
- `python3 -m unittest discover -s tests` — 1,722 tests in 378.294s, OK
  (15 skipped, including the two restricted-sandbox Unix-socket fixtures that
  passed in the focused user-level run).

## Workspace safety

The work was implemented on the already-dirty `impl/env-guard-cooldown`
branch. Path-disjoint environment-guard implementation, tests, generated site
pages, and untracked `node_modules/` were preserved. No quiet-machine
measurement, commit, push, merge, or deployment was performed.
