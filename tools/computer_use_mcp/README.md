# Local macOS computer-use MCP

A Python 3.13 stdlib-only, local **stdio** MCP server for the occasional GUI
step in an authorized Claude Code session. Screenshots are MCP JPEG image
content, so Claude sees them without another API key. No network, packages,
model weights, clipboard access, or third-party input tools are used.

## Registration

Run this yourself in the intended Claude environment (registration is not
performed by this repository change):

```sh
claude mcp add computer-use -- python3.13 /path/to/joulewise/tools/computer_use_mcp/server.py
```

Alternatively, add the following to your own project MCP configuration. The
repository's `.mcp.json` is deliberately unchanged.

```json
{
  "mcpServers": {
    "computer-use": {
      "command": "python3.13",
      "args": ["/absolute/path/to/joulewise/tools/computer_use_mcp/server.py"],
      "env": {"JW_CU_REDACT": "1"}
    }
  }
}
```

The helper `cu_input.swift` compiles on its first needed operation using
`swiftc` from PATH, into `~/Library/Caches/joulewise-cu/cu_input-<source-hash>`.
Apple's Command Line Tools must already be installed. Missing `swiftc` or a
failed build produces a tool error. Compilation needs no Accessibility grant.
Only the executable is cached; safety checks and allowlist decisions run anew.

## One-time macOS grants

Use **System Settings → Privacy & Security → Screen Recording** (called
**Screen & System Audio Recording** on some versions) and **Accessibility**.
Grant both to the responsible process that runs Claude: typically Terminal
for an interactive CLI, or the LaunchAgent's executable for an unattended
magistrate. macOS attributes TCC permissions through the process chain; the
displayed identity can also involve the interpreter/helper. Confirm the
actual entries on the target Mac, and restart the affected processes if
macOS requests it. Rebuilding/replacing the helper may require rechecking
the attribution. A helper's existence alone does not establish a grant.

**macOS requires a human GUI click to grant these permissions. `tccutil`
cannot grant them**; it resets grants. This server never requests a grant or
tries to bypass TCC. When unarmed, `permissions_status` uses only
`CGPreflightScreenCaptureAccess()` and `AXIsProcessTrusted()` for permission
checks and never triggers a permission prompt. Capture and input refuse when
their preflight permission is absent. Inspect the actual grant through the same launch path
that will run the magistrate.

A headless `claude -p` process can drive an existing, unlocked, logged-in GUI
session when launched in that user's GUI bootstrap context and granted
permissions. It cannot create a login session, unlock the Mac, or guarantee
control of protected system/secure-input dialogs. Test the LaunchAgent route
outside measurement windows before relying on it.

## Safety model

- All operational tools, including `screenshot`, `frontmost_app`, and `wait`,
  check `/bin/launchctl print gui/<uid>` explicitly and also `print system`
  for **any loaded label starting `com.joulewise.night`**, even if it has no
  running PID. This covers GUI LaunchAgents when the caller is in SSH or a
  Background session, and system jobs. An unreadable GUI or system domain
  refuses the operation; an empty caller-relative `launchctl list` cannot
  bypass the check. They also refuse if a configured host-link marker
  contains a future epoch. The error names the observed cause.
  A missing marker means no marker gate; an invalid
  or unreadable marker, unavailable launchctl, or malformed launchctl output
  fails closed.
- `permissions_status` checks armed state before any helper use. When armed,
  it returns `armed: true`, the refusal reason, and both permissions as
  **`unknown (armed; not compiled)`**. It neither compiles nor invokes a
  cached helper in that case. An unreadable guard returns an MCP error with
  no compilation. Only an unarmed check may compile and report permission
  booleans with `armed: false`. Input checks armed state again after first-use
  compilation and foreground discovery; screenshots recheck immediately
  before capture. There is no OS transaction combining these probes with
  GUI events. Never arm a night concurrently with GUI operations.
- `allowlist.json` initially allows **System Settings and Finder**, matched
  by bundle id: `com.apple.systempreferences`, `com.apple.Settings`, and
  `com.apple.finder`. Display names appear only in the `_comments` mapping;
  localized names and apps spoofing a display name do not control access.
  Every operation except screenshot, permissions preflight, and `open_app`
  requires an allowlisted foreground app. `open_app` requires an allowlisted
  target bundle id and can recover focus from any foreground app (or no app),
  while still refusing armed state. It invokes `open -b`, without a shell.
  Edit this local configuration deliberately; it is reread on each check.
  **Terminal is excluded by default. Adding `com.apple.Terminal` allows
  `type_text` into Terminal to execute arbitrary shell commands**, outside
  the caller's shell-tool permission checks. Screenshots can observe other
  apps; review the screen for sensitive content before authorizing capture.
- `key` refuses `cmd+tab`, `cmd+shift+tab`, `cmd+space`, `ctrl+up`,
  `ctrl+down`, and `cmd+opt+esc`, including modifier aliases/reordering and
  extra modifiers. The Swift helper repeats this check before posting.
  Before each click, the helper's `CGWindowList` query must identify the
  topmost visible window at the point as a normal (layer 0) window with the
  allowed foreground bundle id and PID. Unknown ownership, another app,
  the Dock, desktop, menu bar, and status items refuse the click. Swift
  rechecks focus and ownership before each mouse-down, including both
  halves of a double-click. Menus/overlays at other layers are also refused.
- The allowlist reduces accidents; it is not a sandbox. An allowed app can
  itself launch programs, change settings, or expose other powerful actions.
  Move, drag, and scroll retain foreground gating without click ownership
  hit-testing. Use them only over the authorized app. The check-to-post race
  remains; neither window ownership nor armed state is an OS transaction.
- Each tool call appends a durable `before` record to
  `~/Library/Logs/joulewise-cu/actions.jsonl` **before any probe or operation**.
  A further `execute` record contains the discovered foreground app before
  an operation, and `after` records its result or refusal. Entries include
  UTC timestamp, call id, tool, arguments, foreground app, phase, and result.
  Foreground is `null` before discovery, in dry run, and when no app could be
  observed. A failed initial/execute log prevents execution. A failed result
  log warns that an action may already have happened: inspect before retrying.
  The server opens the log with append-only flags, refuses log symlinks, and
  never truncates or rotates it. This is an audit log, not tamper-proof storage
  against the owning local user.
  Unexpected tool exceptions also return `isError` and attempt an `after`
  record; the server remains available for the next call. If logging itself
  is unavailable, a durable `after` record cannot be guaranteed.
- `JW_CU_REDACT=1` replaces all `type_text` arguments in every log phase with
  `[REDACTED]`, including invalid requests. Text is still typed. Screenshot
  bytes are never logged; temporary image files are removed after the call.
  Other tool arguments and results remain visible in the log.
- `JW_CU_DRY_RUN` validates and logs intent/result only whenever it is set
  to anything except the empty string or exactly `0`. Values such as `true`,
  `yes`, `01`, `false`, or whitespace all mean **DRY RUN**; unset, empty, or
  exactly `0` enables live mode. Dry run performs **no
  subprocesses, compilation, probes, capture, input, app launch, or sleeping**.
  Its response explicitly says safety/permissions were not evaluated. It is
  neither a safety attestation nor a live action, even during an armed span.
- Input tools (`click`, `move`, `drag`, `scroll`, `type_text`, `key`, and
  `open_app`) share a sliding limit of five **tool actions** per second per
  server process. Excess calls fail rather than queue. A drag/text action can
  generate several native events. Reservations remain charged through action
  completion so slow operations cannot expire their own budget before posting.
  Run one server per controller; this is not
  a system-wide event limiter.

Host-link marker settings are in the same `allowlist.json` file:

```json
{
  "apps": ["com.apple.systempreferences", "com.apple.Settings", "com.apple.finder"],
  "armed_marker_paths": ["~/Library/Logs/jw-hostlink/armed_until"],
  "respect_remote_armed": true
}
```

`armed_marker_paths` is a nonempty list of absolute paths or `~/` paths
relative to the server user's home. Every configured marker is checked;
missing files are allowed, malformed or unreadable files refuse. On the
Air, the host-link monitor writes this marker to **mirror the MBP's armed
state**: a future value on the Air means the MBP is armed. The conservative
default `respect_remote_armed: true` refuses GUI work on the Air too.
Explicitly setting it to `false` opts out of all configured remote-marker
checks; it never disables local GUI/system launchd label checks. Omitted
settings retain the marker path and conservative default shown above.

These gates prevent this tool from acting during an observed armed span.
They do **not** authorize starting Claude during an armed night: the agent
process itself is load. Do not start or continue an agent during a quiet
measurement window. This is operations tooling, with no measurement/data
pipeline integration.

## Tools and coordinates

| Tool | Arguments / result |
| --- | --- |
| `permissions_status` | No arguments; armed status and permission booleans, or unknown while armed |
| `screenshot` | No arguments; main-display JPEG, long edge ≤1280, plus mapping metadata |
| `click` | `x`, `y`; optional `button`: `left`/`right`, `count`: 1/2 |
| `move` | `x`, `y` |
| `drag` | `x`, `y`, `to_x`, `to_y`; optional `duration`: 0.1–5 seconds (default 0.5) |
| `scroll` | Integer `dy`, optional integer `dx`, each within ±5000 pixels; positive up/left |
| `type_text` | `text`: up to 10,000 Unicode characters |
| `key` | `combo`, e.g. `shift+tab`, `ctrl+alt+delete`, `cmd+a`; launcher/switcher combos refused |
| `open_app` | `name`: exact allowlisted **bundle id**, e.g. `com.apple.systempreferences` |
| `frontmost_app` | No arguments; app display name, bundle identifier and PID |
| `wait` | `seconds`: 0–10 |

Input coordinates are **absolute Quartz screen points**, with the main
display's origin at the top left. Screenshots deliberately capture only the
main display (`screencapture -x -m`), avoiding mixed-monitor Retina ambiguity.
The helper can address any active display in absolute points. Use the returned
main-display bounds, and recapture after display configuration changes.

The returned `scale_factor`/`scale_x` is **JPEG pixels per screen point**;
`scale_y` is separate to account for integer resizing of the image height.
Convert a target at JPEG pixel `(u,v)` using:

```text
screen_x = screen_bounds_points.x + u / scale_x
screen_y = screen_bounds_points.y + v / scale_y
```

For example, a 2880×1800 Retina capture represents 1440×900 points; a
1280×800 JPEG has `scale_x = scale_y = 1280/1440`. Its center `(640,400)`
maps to `(720,450)` screen points. `capture_pixels_per_point` reports the
original Retina backing ratio (2 in this example), and `resize_scale` reports
the image resize ratio (1280/2880). Do not multiply by 2 again.

Keyboard shortcuts use ANSI physical key positions; named navigation and
function keys are supported. Use `type_text` for layout-independent Unicode
text. Secure input and some privileged dialogs may reject synthetic events;
an `ok` response means events were posted, not that the UI accepted them.
Verify the visible result before proceeding.

## Magistrate workflow

1. Outside all armed/quiet windows, arrange the one-time grants and an
   unlocked logged-in GUI session. Leave an allowed app foregrounded.
2. Register the MCP server and check Claude's tool permissions for the
   intended interactive or `claude -p` launch path. Explicitly authorize only
   the needed computer-use tools; follow local Claude policy rather than
   bypassing its tool permission checks.
3. Instruct the magistrate to call `permissions_status`, then `screenshot`,
   identify the control, convert image coordinates to points, make one
   action, and inspect a new screenshot. Use `open_app` for allowlisted app
   navigation and short `wait` calls where needed.
4. On a foreground-app refusal, `open_app` may restore focus to an already
   allowlisted bundle id. On an armed-night or missing-grant refusal, stop
   GUI work and report the cause. Do not disarm a night, broaden the
   allowlist, or repeatedly retry to get past a gate. Hand a grant/secure-dialog
   step back to the operator when macOS requires a physical click.

Example task text for an already authorized, unarmed magistrate session:

> Use computer-use permissions_status, then open_app with name
> com.apple.systempreferences and take a screenshot. Find the requested
> setting, convert image pixels with the
> returned scale mapping, perform the authorized toggle, and recapture to
> verify it. Stop on any safety refusal or missing permission.

## Protocol and offline checks

The transport is newline-delimited UTF-8 JSON-RPC 2.0 over stdin/stdout (not
LSP `Content-Length` framing). It implements initialization/version
negotiation, the initialized notification, `tools/list`, `tools/call`, `ping`,
and notification handling. The declared protocol baseline is `2025-11-25`,
with `2025-06-18`, `2025-03-26`, and `2024-11-05` compatibility. Unsupported
versions receive the declared baseline for the client to accept or disconnect.
Notifications get no response. Tool failures use `content` and `isError`;
successful screenshot content includes
`{"type":"image","data":"<base64>","mimeType":"image/jpeg"}`. No diagnostics
or startup banners go to stdout. Calls are serialized; cancellation cannot
undo posted events and is consumed after the current bounded call completes.

```sh
python3.13 -B -m unittest tests.tools.test_computer_use_mcp
python3.13 -B -m unittest tests.tools.test_computer_use_mcp_mutations
```

Tests use temporary homes and a fake executor, including for `swiftc`,
`screencapture`, `sips`, and `launchctl`; they never touch the real screen,
permissions, logs, or helper cache. They exercise dry run too. The mutation
module checks 22 adapted review mutants plus nine round-two mutants by
changing Python source in memory and rerunning the functional tests; it
never changes the checked-out implementation. Swift posting guards have
source checks only in this suite. Native helper
compilation, real screenshots, coordinate/input behavior, TCC attribution and
LaunchAgent/headless operation require a separate, unarmed macOS GUI smoke.
