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

## Round 2

Branch remains `feat/2026-11-11-sm-current-pointer`, as the round-2 brief directs.
Base: `e74eef7a3`. This section supersedes the manual workflow above.
The working tree was clean. No push, PR, network, model weights or host access.

### Built and decisions

- Replaced the old script/test with `scripts/gen_current.py` and
  `tests/test_gen_current.py`. No compatibility entry point remains.
- `render(text)` validates every source block and deterministically renders the
  highest numbered item carrying one. Numeric part precedes the letter suffix.
  A newer blockless item changes no generated byte. No wall clock is read.
- `generate(source, output)` renders before an atomic same-directory replace.
  `check(source, output)` returns 0 agreement, 1 drift, 2 invalid input/file.
  Invalid generated JSON/schema is exit 2; valid noncanonical/stale JSON is drift.
  Duplicate JSON keys are also refused. Drift names `python3 scripts/gen_state.py`.
- Kept the closed wait vocabulary and epoch plausibility checks. Added
  `ruling_recorded`. Strict time ordering is `t0 < latest_end <= deadline`.
  Bounds include 2026-01-01 and 2030-01-01 UTC because the brief refuses values
  outside that interval. Offset conversion has the two required known-value tests.
- `wait: none` generates a wait object with nullable deadline/refusal fields.
  A source block is distinguishable from the no-pointer document. An armed
  declaration still requires a deadline, including with `none`, to satisfy
  the explicit armed deadline inequality. No further armed/none prohibition.
- Exact unindented fences declare pointers. Quoted/indented fences are ignored
  examples; other fenced examples suppress heading/pointer recognition until
  their matching close. The rule and tests state this choice. A pointer's own
  closing fence must be exact. Errors name the RUN_STATE line and reason.
- Times use Python datetime precision (microseconds). Whole seconds render as
  integer epochs; supplied fractional seconds can render as numeric fractions.
- Committed output is the no-pointer document: every field except schema is
  null. No RUN_STATE item currently carries a declaration.
- Updated `POINTER_RULE.md` with the PLAN 5.1 example and the generated format.
  Updated the canonical tool/module rows. Renamed the timings entry with one
  alphabetical text insertion, 0.131 seconds; no JSON reserialization.

### Status publisher and generated page

Publisher: `scripts/window_status.sh`. The output path is at lines 32-33 and
shell redirection at line 94 recreates `WINDOW_STATUS.md` after liveness passes.
A freeze sentinel suppresses Git operations, not that write. Its tests are
`tests/test_window_status_guard.py`; they use synthetic custody and stub Git.

Searches of scripts, configs, tools and `.github` found no launchd template,
installer or automated caller invoking this publisher. It remains procedurally
wired in `docs/process/MAGISTRATE_WATCHDOG.md:10`,
`docs/process/NIGHT_HANDBACK.md:29` and `docs/contracts/window_liveness.md:739`.
It is also in the sealed inventory. No installed-host state was examined.
Thus it is not established as dead code. Restored `WINDOW_STATUS.md` unchanged
from `565c5efef^`; do not retire its file while retaining those procedures.
The publisher and its tests were not edited or run against live paths.
Corrected the liveness contract's retirement assertion and restored the phase-2
campaign doc's original status-file references. AGENTS step 2 stays unchanged;
no claim is made that the kernel's authority string has changed.

`docs/site/readme.html` is generated from README.md by the DocPage mapping in
`scripts/build_site.py:159`; regeneration is `python3 scripts/build_site.py`.
Reverted round 1's hand edit, as the brief permits. No site build or publication.
WINDOW_STATUS, the generated HTML and the phase-2 doc were each byte-compared
with `565c5efef^` and match exactly.

### Verification

Modules ran separately. No full suite, worker pool or measurement pipeline.

| Command | Result |
|---|---|
| `python3.13 -B scripts/gen_current.py` | PASS; generated present no-pointer document |
| `python3.13 -B -m unittest tests.test_gen_current` | Initially 3 test-expectation failures (two line numbers and an unordered expected-winner set); corrected. Then 44 PASS, 0.122 s; final 46 PASS, 0.131 s after fence/whitespace cases |
| `python3.13 -B -m unittest tests.test_gen_state` | PASS, 44 tests, 6.086 s |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | PASS, 14 tests, 2 skipped, 0.298 s |
| `python3.13 -B -m unittest tests.test_window_status_guard` | PASS, 11 tests, 6.745 s; synthetic paths only |
| `python3.13 -B /private/tmp/sm-current-pointer-r2-mutants.py` | PASS, 12/12 mutants killed; changed module objects only, never repository source |
| `python3.13 -m compileall -q joulewise tests scripts` | PASS |
| `python3.13 -B scripts/gen_current.py --check` | PASS, 0 |
| `python3.13 -B scripts/gen_current.py --show` | PASS, one no-pointer line |
| `python3.13 -B scripts/gen_state.py --check` | PASS, 0; pointer integration still pending |
| `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` | Exit 2; sandbox denies `ps`, no census established |
| `git diff --check` | PASS |

The 12 mutations cover newest/oldest selection, partial arms, unknown waits,
arm equality, deadline equality, duplicate keys, second blocks, misplaced blocks,
epoch endpoints, drift inversion, canonical ordering and null text acceptance.
The temporary runner's SHA-256 is
`56d65f03423c963c9baa60b96ef6cdc9d2b158909515907c644c5242a77c5681`.
Its temporary path is an optional audit receipt, not a required deliverable;
the permanent regression cases are in the new test module.
No gate here changes or validates a measurement number.

### Lead integration and limits

Do not infer CI wiring from the standalone checks. The seat did not edit
`scripts/gen_state.py` or `tests/test_gen_state.py`. Exact proposed lead edits
in `gen_state.py:main` (line numbers at this base):

1. Add `import gen_current` with the imports, after `import tempfile`.
2. At line 839, after the existing check loop, replace
   `return 1 if drift else 0` with
   `return max(1 if drift else 0, gen_current.check_default())`.
   This preserves both generators' error codes and checks both even on drift.
3. At line 848, after all generated-region writes, replace `return 0` with
   `return gen_current.generate_default()`.
   Leave the `--stdout` early return alone.

The default hooks are tested against a temporary ROOT. Lead adds the import
and one return-call line in each mode, then runs the three acceptance modules
again. The generated source is the final RUN_STATE file, after kernel writes.
The canonical CI check will cover CURRENT only after these lead edits land.

PROVISIONAL: two live census tests skipped because `ps` is denied, and the
standalone census also returned observation error. The lead must run
`python3.13 -B -m unittest tests.test_fixture_orphan_census` and
`python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` outside this
sandbox. Fixture cleanup cannot be independently certified here.
Python 3.11 remains for CI; local checks used 3.13. No MLX/native hardware tests
apply to this declaration generator. No observable is evaluated.

Read the approved lane PLAN, audit section 8, and arm-stack source on both
`origin/main` and `origin/align/2026-11-08-v4-r11` without checkout. Main's legacy
courier/hold records differ from W1's delivery receipts, named holds and outcome
faults. This generator consumes neither generation's night records, so its
input contract is identical on both. No real custody or forbidden ref was opened.

RUN_STATE.md, TASK_QUEUE.md, the state kernel, gen_state.py, test_gen_state.py,
existing production modules and publisher code remain unchanged. Round-1 names
and commands above are historical evidence only. No unresolved implementation
question remains; umbrella wiring and native census observation belong to lead.
Next exact step: apply the three gen_state integration edits above, run the
acceptance modules, obtain the cold lane review, then decide on a PR.

Round-2 commit subject: `Generate current pointer from RUN_STATE declarations`.
Local-only, intentionally not pushed under the brief.
