# Local macOS computer-use MCP — 2026-11-11

Implemented operations tooling on `ops/2026-11-11-computer-use-mcp`, starting
at `origin/main` / `84ad2c5beea5f823723e6f6f83ccf8caabf9e476` with a clean
worktree. Implementation commit: **`6d628733b`**, `feat(ops): add guarded macOS
computer-use MCP server`. This report is committed separately. No push,
registration, external integration, network access, GUI automation, or real
measurement/data access was performed.

## Delivered

- `tools/computer_use_mcp/server.py`: Python stdlib-only newline-delimited
  JSON-RPC 2.0 stdio MCP implementation, initialize/version negotiation,
  initialized/cancelled notifications, tool schemas/list/calls, ping, protocol
  errors, bounded frames, and EOF shutdown. Declared protocol baseline:
  `2025-11-25`, with older revisions listed in the README.
- `tools/computer_use_mcp/cu_input.swift`: lazy compiled native CGEvent
  mouse movement, left/right/double click, drag, pixel scroll, key combos,
  and UTF-16 Unicode typing. It also reports the foreground application,
  display point bounds, and preflight-only permission booleans. There is no
  permission-request API. The source-addressed helper cache lives under
  `~/Library/Caches/joulewise-cu/`; missing swiftc gives a clear error.
- `tools/computer_use_mcp/allowlist.json`: System Settings, Finder, Terminal.
  Configuration and armed-state decisions are freshly checked, not cached.
- `tools/computer_use_mcp/README.md`: CLI and project configuration examples,
  one-time GUI grants, TCC attribution caveats, safety behavior, tools,
  Retina coordinate examples, and the headless magistrate workflow.
- `tests/tools/__init__.py` and
  `tests/tools/test_computer_use_mcp.py`: 32 synthetic-only unittest cases.
- `scripts/test_timings.json`: exactly one inserted module line, local
  observed scheduling weight **0.121 seconds**. This is the 32-test local
  observation, not a hosted median, speedup claim, or hardware evidence.

Screenshots use `/usr/sbin/screencapture -x -m`, convert/downscale with
`/usr/bin/sips`, and return base64 JPEG as MCP image content, maximum long
edge 1280 pixels. Point bounds and actual capture/resized dimensions produce
per-axis image-to-screen factors, including Retina 2x and resize rounding.
Capture is deliberately main-display-only. Temporary captures are cleaned
up on normal completion and handled errors; image bytes are never logged.

All operational tools except `permissions_status` refuse loaded launchd
labels beginning `com.joulewise.night` or a future `armed_until` epoch.
Unobservable/malformed guard state fails closed. Screenshot and permission
preflight are exempt from the foreground allowlist; other tools require it,
and app launches also validate their target. Input and screenshot rechecks
cover first-use helper compilation and other preflight delay.

Audit logging appends/fsyncs intent before any external probe, then resolved
foreground/execution intent and result. Log failure prevents an unlogged
operation; result-log failure explicitly warns against blind retry. Initial
foreground is null until discovered. `JW_CU_REDACT=1` redacts type_text
arguments even on invalid calls. `JW_CU_DRY_RUN=1` logs only, with no probes,
compiler, capture, input, app launch, or sleep; it explicitly does not attest
that safety/permission checks passed. Five input actions per sliding second
are enforced per server process, with reservations retained through
completion so a slow operation cannot expire its budget before posting.

## Verification

`python3.13 -B -m unittest tests.tools.test_computer_use_mcp`

**PASS: 32 tests in 0.121 seconds**, final test run. Earlier incremental
runs also passed. Aggregate targeted test time was under two seconds, well
below the brief's 20-minute limit. Every test uses a temporary synthetic
home and fake subprocess executor, including fake swiftc, screencapture,
sips, launchctl, helper, and app-launch boundaries. Some cases explicitly
exercise dry run; action-path cases use the fake executor without dry run
to prove the real gate and dispatch code. Screenshot payload bytes in the
fixtures are synthetic placeholders, not native JPEG evidence.

Coverage includes protocol round-trip/lifecycle/notifications/errors/frame
limits; every advertised schema and argument validation; both armed refusal
paths across every operational tool; failed/malformed guard observations;
allowlist exemptions, reload and launch-target checks; dry-run no-execution;
durable log-before-probe/execute, append preservation, redaction and log
failure; rate-limit boundaries and slow-operation accounting; helper-cache
and missing-compiler behavior; missing grants; image-content shape,
temporary cleanup, Retina/non-Retina/negative-origin/rounding mappings.

A separate `python3.13 -B` inline check compiled the three added Python
sources in memory, checked every server import against
`sys.stdlib_module_names`, parsed both JSON files, and proved the timing
file byte-identical to `origin/main` after removing the single added line.
**PASS.** `git diff --cached --check`: **PASS** before implementation commit.
An installed Apple SDK header was consulted read-only to confirm the
null-display-array behavior of `CGGetDisplaysWithPoint`; no native program
was compiled or executed.

The full suite was intentionally **not run**, per the brief's concurrent
analysis-job constraint and targeted-module-only instruction. No study code
or coordination state was changed. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, `tests/test_gen_state.py`, and `.mcp.json`
are unchanged; the brief assigns coordination ownership to the lead.

## Sandbox limits and next exact step

**No real screen and no Accessibility were tested in this sandbox.** The
Swift helper was not compiled by a real swiftc, no native events were
posted, no real screenshots were taken, and real permission/launchd status
was not queried. Native Swift API/type correctness, real sips/JPEG output,
Screen Recording and Accessibility attribution, Retina pointing, localized
app names, and GUI behavior remain **UNVERIFIED**. Offline protocol tests
are not an external MCP conformance certification; no network lookup or
live Claude registration was attempted.

The lead's next exact step is a native smoke **after the current job ends,
outside any armed/quiet window**, in the intended logged-in GUI launch
context:

1. Register using the documented `claude mcp add` command and call
   `permissions_status`, exercising first-use real compilation and checking
   that preflight does not prompt. Resolve any native build issue first.
2. Grant Screen Recording and Accessibility with the required physical GUI
   clicks for the responsible Terminal/LaunchAgent chain, restart when macOS
   requires it, and confirm preflight in that same launch context.
3. Capture a real screenshot; verify JPEG decoding, maximum 1280-pixel long
   edge, actual Retina backing ratio and image-to-point mapping. In a
   harmless scratch view of an allowlisted app, smoke each input operation
   and visually confirm it. Test the intended `claude -p` LaunchAgent path
   separately; no login/unlock/secure-dialog capability is claimed.
4. Check a non-allowlisted foreground refusal, actual local audit records,
   redaction and rate limiting without changing real measurement state.
   Armed-state behavior already has synthetic coverage; do not arm a real
   night just to test this server while an agent is active.

There are no outstanding implementation rulings. Operational limits remain:
guards and GUI events are separate OS operations (no atomic cross-service
lock); do not arm concurrently. `launchctl list` covers the server's
bootstrap context, so it must match the measurement LaunchAgents' context.
Dry run makes no safety claim. Rate limiting is per server process, and
event-post success does not establish UI acceptance. Protected dialogs may
still require operator input. The agent itself remains prohibited load in
an armed measurement span even though this server refuses its action tools.
