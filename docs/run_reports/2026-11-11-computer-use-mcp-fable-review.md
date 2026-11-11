# Computer-use MCP — Fable 5.2 cold review (2026-11-11)

Target: `origin/ops/2026-11-11-computer-use-mcp` @ `436e421ff`
(`tools/computer_use_mcp/`, `tests/tools/test_computer_use_mcp.py`,
`docs/run_reports/2026-11-11-computer-use-mcp.md`). Reviewer: Claude Fable 5.2,
cold seat, on the Air. No real screen capture or input was driven.

## Verdict: ADMIT-WITH-FIXES

The code is careful and the gates that exist are well tested (22/22 safety
mutations caught). Nothing here blocks merging it as ops tooling or using it
interactively from Terminal on a GUI session. **F1 and F2 must be fixed before
the server is registered for the headless magistrate on the measurement Mac**,
and F3 must be stated in the README, because the allowlist is weaker than its
description suggests.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 1 | Unit tests `python3.13 -B -m unittest tests.tools.test_computer_use_mcp` | PASS, 32 tests |
| 2 | Mutation testing, 22 safety-gate mutants | 22 caught, 0 survived (list below) |
| 3 | Armed refusal: `com.joulewise.night` prefix match | PASS (prefix, any PID state; `org.x.com.joulewise.night` not matched) |
| 4 | Armed refusal: `armed_until` future epoch | PASS (float, finite, `> now`) |
| 5 | Fail closed: launchctl error / timeout / malformed header or row | PASS |
| 6 | Fail closed: empty, non-numeric, nan/inf, unreadable marker | PASS (missing file = no marker gate, per brief) |
| 7 | Fail closed: launchctl run outside the GUI domain | **FAIL OPEN, see F1** (reasoned, not run natively) |
| 8 | No load during an armed span | **FAIL, see F2** (`permissions_status` compiles Swift while armed; reproduced with the fake executor) |
| 9 | Allowlist enforced on frontmost app, rechecked before input | PASS as coded; **weak as a boundary, see F3–F5** |
| 10 | `open_app` target allowlisted, no shell, exact string | PASS |
| 11 | Log before execute; append-only; symlink refused; fsync | PASS (`O_APPEND\|O_NOFOLLOW`, 0600; log failure blocks execution) |
| 12 | Dry run executes nothing | PASS (no subprocess, compile or sleep); only the exact value `1` enables it (F7) |
| 13 | Rate limit 5 input actions per second | PASS (sliding window, slot held to completion) |
| 14 | No `CGRequestScreenCaptureAccess` / prompting API | PASS (0 occurrences; preflight gates run before `screencapture` and before any event post, in both server and helper) |
| 15 | MCP initialize / tools/list / tools/call / errors / image content | PASS (live stdio round-trip with `permissions_status` and a dry-run `click`) |
| 16 | Helper compile: no shell, no argument injection, hash-addressed cache | PASS (argv is a fixed operation name, arguments go as JSON on stdin, `cu_input-<sha256[:24]>` so a source change recompiles); minor F8 |
| 17 | Retina coordinate mapping | PASS on review (points from `CGDisplayBounds`, pixels from the capture, per-axis JPEG-pixels-per-point; main display only); not verified natively |
| 18 | README: TCC grants honest, registration without repo `.mcp.json` | PASS (`.mcp.json` unchanged on the branch; says a GUI click is required and `tccutil` cannot grant) |
| 19 | Real `launchctl list` on the Air parses under the strict row parser | PASS (495 lines, 0 rejected rows) |
| 20 | Native screenshot, input, TCC attribution, LaunchAgent path | NOT VERIFIED (Terminal has no grants; by instruction nothing was driven) |

Mutants, all caught: night-label refusal removed; prefix narrowed to the exact
label; future-epoch check removed; invalid marker, unreadable marker,
malformed launchctl header and malformed launchctl row each made to fail open;
first frontmost check removed; pre-input frontmost recheck removed; pre-input
armed recheck removed; pre-capture armed recheck removed; armed check skipped
for `wait`/`frontmost_app`; dry run made live; `before` log dropped; `execute`
log dropped; `O_APPEND` replaced with `O_TRUNC`; rate limit 5→6; rate limit
not applied; Screen Recording gate removed; Accessibility gate removed;
`open_app` target check removed; redaction disabled.

## Findings

**F1 (must fix before magistrate use) — the launchd label check is
domain-relative and fails open outside the GUI session.** `check_armed` runs
bare `/bin/launchctl list`, which lists the caller's own launchd domain. The
night agents are user LaunchAgents (`~/Library/LaunchAgents`, per
`tests/test_install_night_agent.py`), so they live in `gui/<uid>`. A server
started from an SSH session, or from anything in the Background session, gets
a well-formed list without them, and the label gate passes silently. Only the
`armed_until` marker would then stand between the magistrate and an armed
night. The README mentions the context dependence, but the code should not
depend on it. Fix: query `launchctl print gui/<uid>` explicitly (and refuse if
it cannot be read), or refuse unless `launchctl managername` is `Aqua`. This
is reasoned from launchd behaviour; it was not reproduced, because this
review session is itself in the Aqua domain.

**F2 (must fix before magistrate use) — `permissions_status` can compile the
Swift helper during an armed night.** It is exempt from the armed check and
calls `helper()`, which runs `swiftc` (120 s timeout) when the cache is empty
or the source hash changed. Reproduced with the fake executor: armed label
loaded, `permissions_status` succeeds and `swiftc` is invoked. A compile is
exactly the kind of load the brief says this server must never cause. Fix:
never compile while armed (use an existing cached binary or refuse), or
prebuild at registration time.

**F3 (document; consider hardening) — the allowlist gates the frontmost app,
not the target of the event.** Three consequences:
- A click or scroll goes to whatever is under the pointer: the Dock, the menu
  bar, or a visible window of a non-allowlisted app. One click can launch or
  act on any app.
- `key` accepts `cmd+tab` and `cmd+space` from an allowlisted app. Spotlight
  is an overlay, so the frontmost app likely stays allowlisted while
  `type_text` plus `return` launches anything. The next call is refused, but
  the launch has happened.
- Terminal is on the default allowlist, so `type_text` is arbitrary shell
  execution that bypasses Claude Code's own Bash permission rules, including
  commands that would disarm or disturb a night.
The allowlist is a speed bump against accidents, not a sandbox, and the README
should say so. Options: drop Terminal from the default, refuse app-switching
combos, hit-test the window owner under the pointer in the helper.

**F4 (should fix) — apps are matched by localized display name.** The name is
locale-dependent and any app can call itself "Terminal". The helper already
returns `bundle_id`; match on `com.apple.systempreferences`,
`com.apple.finder`, `com.apple.Terminal`.

**F5 (residual) — check-to-post race.** The last frontmost check and the event
post are separate processes. Moving the frontmost and armed-marker recheck
into the helper, immediately before posting, would shrink the window to
microseconds. It cannot be closed entirely; the README is honest about that.

**F6 (hardening) — unexpected exception types escape `call()`.** Only
`ToolError`, `OSError` and `ValueError` are caught. Anything else kills the
server with a `before` record and no `after` record. That is fail closed, but
a catch-all that logs and returns `isError` is better for a headless caller.

**F7 (low) — `JW_CU_DRY_RUN` is live for any value other than `1`.**
`true`, `yes` and `01` all execute for real. Accept common truthy values or
refuse unknown ones.

**F8 (low) — helper build trust.** `swiftc` is resolved from `PATH` (prefer
`/usr/bin/swiftc`), and an existing cache file is trusted by name without
checking the permissions of a pre-existing cache directory. Same-user only.
Old binaries are never pruned.

**F9 (usability) — a stray focus change strands the session.** Once a
non-allowlisted app is frontmost, every tool but `screenshot` refuses,
including `open_app` back to an allowlisted app. Recovery then needs a
physical step. Allowing `open_app` to an allowlisted target from any
frontmost app would keep this remote-recoverable.

**F10 (native smoke) — `type_text` posts up to 500 events with no delay
between 20-unit chunks,** which can drop characters. Typed text is logged in
clear unless `JW_CU_REDACT=1` (as the brief specified; the README snippet sets
it).

**F11 (note) — clock skew.** A clock that runs ahead opens the marker gate
early. That is inherent to an epoch marker and is why the label check (F1)
has to be robust.

Protocol notes, no action needed: an unknown tool returns an `isError` result
rather than JSON-RPC `-32602`; `tools/*` before `notifications/initialized`
returns `-32000`. Both are acceptable to Claude Code.

## Observations on this Mac

- `~/Library/Logs/jw-hostlink/armed_until` on the Air currently holds a future
  epoch, so every live tool except `permissions_status` would refuse here
  right now. The gate works; a native smoke of screenshot or input on the Air
  needs that marker expired first.
- Live `permissions_status` returned `accessibility=false`,
  `screen_recording=false` with no prompt, matching the orchestrator's smoke.
