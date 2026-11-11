# Computer-use MCP round 2 — 2026-11-11

Implemented the requested Fable review fixes on the existing requested branch
`ops/2026-11-11-computer-use-mcp`, starting clean at `59527a1b2`.
Implementation commit: **`ce1713f10`** (`fix(ops): harden computer-use MCP
after Fable review`). This report is committed separately. No push,
registration, network, model downloads, real launchd queries, native helper
compilation, screen capture, input events, or study-data access occurred.
All subprocess boundaries exercised by tests used fakes and temporary homes.
No agents were delegated work. The explicit brief selected this bounded
operations task; no kernel tasks or coordination state were written.

## Changes and acceptance

| Item | Delivered behavior and verification |
| --- | --- |
| F1 | Explicit `launchctl print gui/<uid>` and `print system`; both domains must be readable with a recognizable services section. Missing, duplicate, truncated, or malformed sections/rows refuse. Prefix checks include non-running services. Fakes cover GUI-domain errors/timeouts, system-domain errors/labels, and callers in SSH/Background whose relative `list` hides the GUI jobs. The system domain is always checked as the conservative choice. |
| F2 | `permissions_status` checks armed state before helper use. A positive armed observation returns `armed: true`, reason, and both permission fields as `unknown (armed; not compiled)`. Neither cold nor warm helpers are invoked while armed. Unknown guard state returns an MCP error without compilation; unarmed state may compile and return booleans. |
| F3 | Removed Terminal from defaults; explicit `com.apple.Terminal` opt-in still works, with the arbitrary-shell warning in README. Python and Swift block launcher/switcher key combinations, aliases, reordered modifiers and extra modifiers. A Swift `CGWindowList` query identifies the topmost visible window at click coordinates. Python requires its PID/bundle to match the allowed frontmost app and its layer to be 0. Swift repeats focus/owner checks before each mouse-down, including double-clicks. Unknown ownership, Dock, status items, other apps, desktop and nonzero-layer overlays refuse. Fake helper responses test accepted/refused owners; native guards have source checks only. |
| F4 | Allowlist entries and foreground matching use `com.apple.systempreferences`, `com.apple.Settings`, and `com.apple.finder`; display names are `_comments` metadata. Tests accept localized names and reject display-name spoofing. `open_app` retains its `name` argument, whose value is now a bundle id, and calls `open -b`. |
| F6 | Tool boundary catches unexpected `Exception` subclasses, attempts an `after` error record, and returns MCP `isError`. This includes probe, execution, result-shape/serialization, completion-clock and log failures. A stdio test verifies a subsequent tool call and ping after an unexpected error. If the log itself fails, an error is returned but a durable after record cannot be guaranteed. |
| F7 | Any `JW_CU_DRY_RUN` value other than unset, empty, or exactly `0` is dry run, including ambiguous `false`, `01`, and whitespace. Tests prove no probes, compilation, input or sleeping. |
| F9 | An allowlisted `open_app` target can recover focus from an unallowlisted app or absent foreground without probing the foreground. Armed checks, repeated target validation, permission preflight and rate limits remain. A cold-compile rearm fake proves no app opens after that rearm. |
| Host semantics | Configurable nonempty `armed_marker_paths` list, with absolute or `~/` paths. Every selected marker is checked; defaults preserve `~/Library/Logs/jw-hostlink/armed_until`. `respect_remote_armed` is a strict boolean defaulting true. False opts out of remote-marker checks only; GUI/system label gates always remain. README explains that the Air marker mirrors MBP armed state. Tests cover path replacement, multiple/missing markers, future marker, config reload, invalid config, and opt-out without disabling local labels. |

Files changed:

- `tools/computer_use_mcp/server.py`
- `tools/computer_use_mcp/cu_input.swift`
- `tools/computer_use_mcp/allowlist.json`
- `tools/computer_use_mcp/README.md`
- `tests/tools/test_computer_use_mcp.py` (32 existing cases retained/adapted;
  23 added; 55 total)
- `tests/tools/test_computer_use_mcp_mutations.py` (new)
- `scripts/test_timings.json` (one inserted module line only)
- This report.

## Verification

Commands were run sequentially, one targeted module at a time:

```sh
python3.13 -B -m unittest tests.tools.test_computer_use_mcp
python3.13 -B -m unittest tests.tools.test_computer_use_mcp_mutations
git diff --check
```

- Baseline before edits: **32 tests PASS**, 0.154 seconds.
- Final functional run: **55 tests PASS**, 0.273 seconds.
- Final mutation run: **1 wrapper test PASS**, 10.155 seconds: **31/31
  mutants caught, zero survivors**. Each variant runs all 55 functional
  tests (1,705 internal test invocations per mutation-module run). The
  checked-out implementation is never mutated; source changes exist only
  in memory. The review published descriptions rather than its runner, so
  the module reconstructs 22 adapted review mutants and adds nine round-two
  mutants. The original pre-input armed-recheck mutant now removes the
  redundant post-discovery checks together; removing just one still refuses
  through the remaining checks. Swift source assertions are not a native
  Swift mutation run.
- First mutation run also passed, 11.308 seconds. That observed local
  duration is the new timing entry; it is not a hosted median or throughput
  claim. Existing timing entries, including the original functional-module
  timing, were preserved. A byte comparison against `59527a1b2` proved that
  removing the one inserted line restores the entire original file exactly.
- An offline `python3.13 -B` inline check compiled all three changed Python
  sources in memory, checked imports against the stdlib (plus the local
  tests import), parsed the two JSON files, verified the timing-file byte
  comparison, and verified protected paths unchanged: **PASS**.
- Whitespace checks: **PASS**, including staged implementation review.
- An intermediate migration run had one obsolete test expecting the old
  launchctl error text; the new domain-specific error was correct. The
  expectation was updated and all subsequent functional runs passed.

Aggregate targeted test runtime was under one minute, below the brief's
20-minute limit. The full/quick/sharded suites and analysis pipelines were
not run, per the explicit concurrent-job restriction. `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py`,
and `.mcp.json` are unchanged. No real armed marker or custody was inspected.

## Uncertainty, residual limits, and next exact step

No implementation question remains unresolved. Native behavior is still
**UNVERIFIED**, including the new Swift API/type correctness, actual
`launchctl print` formatting on each target macOS version, window layering,
Screen Recording restrictions on window metadata, and real SSH/Background
GUI access. Unexpected native formats fail closed and may need compatible
parser changes after an unarmed inspection. F8 helper-build trust and F10
typing pacing were not requested in round 2 and remain as reviewed.

The allowlist remains an accident guard, not a sandbox: allowed apps can
perform powerful actions. Move/drag/scroll retain foreground gating without
the new click-owner hit test. Strict click gating also refuses app menus
or overlays on nonzero layers; this is deliberate conservative behavior.
The check-to-post race and epoch clock-skew limitations remain. Never arm
concurrently with GUI use or interpret these fixtures as live validation.

Lead's next exact step, **after the concurrent job ends and outside every
armed/quiet window**, is a native smoke in the intended GUI and headless
launch paths:

1. Build the updated Swift helper and validate the explicit GUI/system
   domain parser against real unarmed `launchctl print` output. Test the
   same-user SSH/Background route; an unreadable GUI domain must refuse.
2. Confirm unarmed preflight/TCC attribution without prompting. Use only
   synthetic markers/fixtures for armed tests; do not arm a real night while
   an agent is running. Confirm the Air's configured marker meaning before
   changing the conservative `respect_remote_armed` default.
3. Smoke an allowed normal-window click, wrong-app/desktop/Dock/status-item
   refusal, double-click recheck, blocked shortcut aliases, and `open_app`
   recovery by bundle id from a stray focus change. Inspect the audit log.
   Also complete the original screenshot/Retina/input/TCC smoke; no native
   evidence was produced here.
