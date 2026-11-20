# Computer-use MCP round 3 — 2026-11-11

Implemented Fable delta findings D1–D3 on the requested existing branch
`ops/2026-11-11-computer-use-mcp`, starting clean at `48b392612`.
The delta section of `2026-11-11-computer-use-mcp-fable-review.md` was the
first file read. Mission M0 intake found no active stop card; the explicit
brief selected this bounded operations task over the normal queue. No
kernel task was registered and no coordination state was written.

## Changes

- **D1:** Python applies the existing click ownership check to both drag
  endpoints, passes the expected foreground PID/bundle to Swift, and
  rechecks armed state after window inspection. Swift checks both endpoints
  before pointer movement and again immediately before mouse-down. Both
  use the existing normal-window check, including Dock/status-item
  refusals. A validated drag with Euclidean distance strictly below 3
  screen points becomes a single left click at its start before logging
  or any probes. Every audit phase identifies it as `click`; no drag
  operation is sent to the helper. Invalid requests retain their original
  intent/refusal records. Distances of exactly 3 points remain drags.
- **D2:** Labels must match `[A-Za-z0-9._-]+`; quoted labels and every other
  character refuse. Night-prefix matching is case-insensitive in both
  launchd domains. The services closing line must have exactly the
  indentation of its opening line. A stray brace at another indentation
  remains inside the section and fails row validation, so it cannot hide
  later labels. Tests cover all three open review rows, additional invalid
  label characters, and valid labels/space-indented blocks.
- **D3:** README states that `respect_remote_armed` must stay `true` on
  the MBP and its local marker must remain configured: that marker records
  the MBP's own armed state, and `false` skips it as well as remote markers.
  README also describes the new drag behavior and remaining move/scroll
  limits.
- Added seven Python source mutants: removal of all drag hit-tests,
  removal of the end check, removal of short-drag conversion, conversion at
  the wrong threshold, missing label validation, case-sensitive prefix
  matching, and ignored closing indentation. Updated the two existing
  prefix-mutant anchors for the new case normalization.

Files changed:

- `tools/computer_use_mcp/server.py`
- `tools/computer_use_mcp/cu_input.swift`
- `tools/computer_use_mcp/README.md`
- `tests/tools/test_computer_use_mcp.py`
- `tests/tools/test_computer_use_mcp_mutations.py`
- This report.

Existing test modules were extended, so `scripts/test_timings.json` needed
no insertion and remains byte-identical to the starting commit. No timing
file was re-serialized.

## Verification

Targeted modules ran sequentially with Python 3.13:

```sh
python3.13 -B -m unittest tests.tools.test_computer_use_mcp
python3.13 -B -m unittest tests.tools.test_computer_use_mcp_mutations
git diff --check
```

- Baseline: **56 functional tests PASS** (0.402 s); **31/31 mutants killed**
  by the existing mutation wrapper (16.311 s).
- Regression-first check: the new tests exposed the requested defects on
  the original implementation (68 tests, 49 failed subtests/assertions).
- Final functional run: **69 tests PASS** (0.292 s), retaining all 56
  original test cases and adding 13. Coverage includes endpoint ownership,
  unknown ownership, the armed recheck, expected native identity, short
  drag execution/logging/refusal/dry run, the exact threshold, invalid
  requests, and the parser cases above.
- Final mutation run: **one wrapper test PASS** (16.389 s), **38/38 mutants
  killed, zero survivors**, including `drag hit-tests removed`. Each mutant
  ran all 69 functional tests, totaling 2,622 internal test invocations.
  Mutants exist only in memory; checked-out source is never mutated.
- An inline `python3.13 -B` check compiled the three changed Python files
  in memory, parsed the allowlist and timing JSON, compared timing bytes
  with `git show 48b392612:scripts/test_timings.json`, and verified protected
  paths unchanged: **PASS**. Whitespace check: **PASS**.

Aggregate targeted test runtime was under one minute. The concurrent
analysis job was left untouched. No full/quick/sharded suite, analysis
pipeline, model download, network call, real launchd query, native helper
compilation, screen capture, or real input occurred. Tests used fake
subprocesses and temporary homes only. No study-data or real restricted
directory was accessed. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, `tests/test_gen_state.py`, and `.mcp.json`
are unchanged. No subagents or external consults were launched. The change
is recorded in one local commit titled
`fix(ops): hit-test drags and harden launchctl parsing`; no push.

## Uncertainty and next exact step

No implementation question is unresolved. Native behavior remains
**UNVERIFIED**: Swift guards have source assertions, not native execution
or a native mutation run. Python 3.11 was not run here. The stricter parser
was exercised only against synthetic fixtures and the pre-existing native
row fixture; actual formatting on target macOS versions may still need
compatibility changes and will refuse if unrecognized.

Drag intermediate points are not hit-tested, and the check-to-post race
remains. Move/scroll behavior and the other residual findings from the
delta review are unchanged. These tests supply no live hardware evidence
and change no measurement or claim-bearing number. The checks caught
operations safety defects only; no scientific gate was run or closed.

After the concurrent job ends, the lead's next step is a native build and
smoke outside every armed/quiet window: allow a normal-window drag; refuse
Dock, menu-bar extras, other-app and unknown-window targets at each
endpoint; verify short drags generate one click and `click` audit records;
verify the actual unarmed GUI/system launchctl format still parses. Keep
the MBP marker setting true. Use only synthetic fixtures for armed-state
tests. Final independent review and native validation remain with the lead.
