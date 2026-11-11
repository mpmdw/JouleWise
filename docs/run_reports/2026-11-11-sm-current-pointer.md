# sm-current-pointer — 2026-11-11

Branch: `feat/2026-11-11-sm-current-pointer`.
Commit subject: `Add checked current pointer and retire stale status document`.
No push or PR. The working tree was clean at intake.

## Built

- `docs/process/CURRENT.json`: schema v1, item 261, owner lead, null arm/wait.
- `scripts/current_pointer.py`: check, bump and one-line show. Standard library.
- `tests/test_current_pointer.py`: 27 tests, with synthetic temporary files and
  one repository check selecting only RUN_STATE heading numbers and letters.
- `docs/process/POINTER_RULE.md`: Q7 rule and synthetic item-249 example, 58 lines.

The checker rejects unknown keys, duplicate JSON keys, malformed JSON, invalid
timestamps, non-integer epochs, implausible epochs, invalid waits and stale item
numbers. Epoch bounds are exclusive: 2026-01-01 UTC through 2030-01-01 UTC.
An arm needs a non-none observable and deadline >= latest end >= t0.
`chain_exited` is refused; use `result_json_exists` for pre-chain refusals too.

Bump edits only the two top-level value tokens. Tests compare every output byte
against the expected source, including CRLF, whitespace, escapes, key order and
replacements of different lengths.
An omitted optional suffix tracks the integer only. A supplied suffix must match
the highest heading's letter. Bump preserves it and refuses a stale suffix;
the lead must correct or remove it manually. It never infers an arm from prose.

## Other files touched

- `AGENTS.md`: minimal intake replacement with CANONICAL, top item and CURRENT.
- `CANONICAL.md`: rows for pointer/rule, tool and regression module.
- `WINDOW_STATUS.md`: deleted.
- `CLAIMS_STATUS.md`, `docs/contracts/window_liveness.md`,
  `docs/phase_2/splitwise_decode_campaign.md`: retired-status reference fixes.
- `docs/site/readme.html`: only the stale status link changed, byte-checked
  against HEAD. No site rebuild or publication.
- `scripts/test_timings.json`: one alphabetical inserted line, 0.169 seconds
  from the first local module run. No reserialization.
- This report. No coordination-state or existing production Python edits.

## Verification

Modules ran separately, without the full suite or concurrent test workers.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_current_pointer` | PASS, 27 tests, 0.169 s initially, 0.655 s in the final run |
| `python3.13 -B -m unittest tests.test_gen_state` | PASS, 44 tests, 3.135 s |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | PASS, 14 tests, 2 skipped, 0.169 s |
| `python3.13 -B -m unittest tests.test_window_status_guard` | PASS, 11 tests, 2.235 s |
| `python3.13 -B -m unittest tests.test_bridge` | PASS, 62 tests, 63.017 s |
| `python3.13 -m compileall -q scripts/current_pointer.py tests/test_current_pointer.py` | PASS |
| `python3.13 -m compileall -q joulewise tests scripts` | PASS |
| `python3.13 -B scripts/current_pointer.py bump` | PASS; seeded number/timestamp only |
| `python3.13 -B scripts/current_pointer.py check` | PASS, item 261 |
| `python3.13 -B scripts/current_pointer.py show` | PASS, one line |
| `git diff --check` | PASS |

The bridge module pins canonical enforcement snippets in AGENTS; those bytes
still pass. No test pins the edited intake text or the real retired status file.
The window-status module tests synthetic writer behavior and was preserved.
The only AGENTS reference in test_docs_freshness is site_capsule/AGENTS.md;
it does not depend on the edited intake and was not run.

Read the required audit sections and lane plan from the specified refs.
Inspected run_night.py, magistrate_watchdog.py and b5/driver.py on both
origin/main and origin/align/2026-11-08-v4-r11. The latter has delivery receipts,
named holds and nonzero-exit faults. This pointer declares waits and reads no
night record, so it does not depend on either generation's receipt vocabulary.
No custody, results branches, records refs, measurement pipeline, network, SSH,
model downloads or host probes were used by the new code.

## Limits and lead follow-up

The checker validates a declaration; it does not evaluate its observable or
establish live host state. No hardware or MLX tests apply to this tool.
Python 3.13 ran locally; Python 3.11 remains for CI.
The live orphan census and live CLI smoke skipped because the sandbox denies ps.
PROVISIONAL: the lead must run that module outside the sandbox. Its orphan
cleanup also relies on ps, so this run cannot independently prove fixture cleanup.

Historical process traces, decision-log entries and the generated historical
run-state page retain old status mentions. The legacy window_status.sh writer
and its safety tests remain untouched under the no-writer-change rule. Running
that legacy writer can recreate the retired document; the lead owns retiring it.

RUN_STATE.md, TASK_QUEUE.md, state_kernel.json and test_gen_state.py are unchanged.
The kernel still says `AUTHORITATIVE_WORK_SELECTION_STATE`; its demotion and any
generated queue/header changes belong to the lead, as the lane plan specifies.
Next: lead reviews the local commit, fills the real arm/wait if appropriate,
runs the native census check, and schedules the cold lane review before a PR.
