# Review r2 of PR #500 (fix/2026-10-16-watchdog-b6-bindings, head ed665952e)

Reviewer: Opus 5.5. I am an independent, executing reviewer and did not author the PR. Date: 2026-10-17.
Base reviewed against: the r1 review /Users/edr/night-archive/watchdog-b6/REVIEW-pr500.md. Its MAJOR-1 was found on 42ebf400c.
Nothing was edited, committed, pushed, installed or loaded. No launchd job and nothing under /Users/edr/night-custody was written.
The harness and its outputs are in /private/tmp/wdrev-harness/: replay_b6.py, failclosed_b6.py, fc_sequence.py, equiv.py, realstate.py, and the out_*/eq_*/allplans_* files.
Each run set TMPDIR to a fresh /private/tmp/wdrev.XXXX directory and set JW_B5_SYNTHETIC_ONLY=1.

## Verdict: REQUEST-CHANGES (test-only; the production fix is correct)

The production change does what MAJOR-1 asked. Executed on a real block-6 plan shape in a `night-b6/sessions/<id>/custody/` layout that the storage scan does not reach:
- a magistrate already running gets REQUEST at exactly t0-180, SIGTERM at t0-90 and SIGKILL at t0-60;
- the results are identical under python3.13 and python3.14;
- on 11,762 decisions over all 392 parseable on-disk v2/v5 plans, scanned-plan behaviour matches main exactly.

The head is still red in CI:
- `tests.test_night_agent_install` fails, because the new de-duplication changes the fence string that test asserts;
- CI shard 1 failed and shards 2-12 were cancelled.

An uncommitted one-line fix for that test appeared in the PR worktree at 07:07:34 during this review. Another session wrote it, not me. With it, the module passes (below). Commit it, get CI green, and this becomes APPROVE-WITH-NITS.

## Findings

### BLOCKER-1: `tests.test_night_agent_install` fails on ed665952e (CI red)

CI (`gh pr view 500 --json statusCheckRollup`):
- `test (3.13, 1)` FAILURE, `test (3.13, 2..12)` CANCELLED;
- gate-ledger FAILURE;
- build, quick, installed-wheel, fences and changes pass.

Shard 1 log:
```
FAIL: test_child_mask_after_signal_is_empty (test_night_agent_install.RecordPollTests.test_child_mask_after_signal_is_empty)
AssertionError: 'inst[26 chars]ight-agent-test; installed_plan:prior-install-night-agent-test' != 'inst[26 chars]ight-agent-test'
```

Local reproduction on a clean `git archive ed665952e` tree:
`PYTHONPATH=/private/tmp/wdrev-head python3.13 -B -P -m unittest tests.test_night_agent_install` gives `Ran 85 tests ... FAILED (failures=503, errors=18)`.
- All 503 subtest failures are the same duplicate-string assertion: 301 of `installed_plan:install-night-agent-test`, 202 of the `prior-` variant.
- The 18 errors come from the export not being a git repository (`git rev-parse HEAD` exits 128). They do not come from the PR.

Cause: `_installed_agent_plans` now de-duplicates by (plan_id, resolved plan path), so `installed_agent_fence` returns `installed_plan:X` once instead of once per label. That is the seat's intended decision 2. tests/test_night_agent_install.py:895 still expects `"; ".join([...] * len(LABELS))`.

The worktree now carries an uncommitted edit, `git -C /Users/edr/code/JouleWise-wt-watchdog-b6 diff`, mtime 07:07:34, written by another session:
```
-        self.assertEqual("; ".join(["installed_plan:" + expected_plan] * len(LABELS))
-                         if expected_plan else None, fence)
+        # Both plists name one plan; the fence lists each (plan id, plan path) once.
+        self.assertEqual("installed_plan:" + expected_plan if expected_plan else None, fence)
```
With that edit, the run over 7 modules gives `Ran 376 tests in 1054.399s OK`:
`PYTHONPATH=$W python3.13 -B -P -m unittest tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog tests.test_install_night_agent tests.test_night_agent_install tests.test_fixture_orphan_census tests.test_b5_plan tests.test_evidence_night`

The seat's report does not list test_night_agent_install among the modules it ran. That is how this escaped.

### MINOR-1: Some plist or plan contents raise exceptions that escape `load_plans`, so a running session is never stood down

Three exceptions get through, because `_installed_agent_plans` catches `(OSError, ValueError, OverflowError, TypeError, KeyError, IndexError, PlanError, InvalidFileException, ExpatError)` and `load_plans` catches `(OSError, ValueError, OverflowError)`:
- `AttributeError`, raised inside plistlib by a malformed `<date>`;
- `RecursionError`, raised by a deeply nested binary plist;
- `RecursionError`, raised by a deeply nested plan JSON.

Command: `failclosed_b6.py <head> <sim> plist_bad_date plist_deep_binary plan_deep_json_recursion`. Python 3.13 and 3.14 give the same result:
```
{"case": "plist_bad_date", "t-t0": -170, "load_plans_EXC": "AttributeError: 'NoneType' object has no attribute 'groupdict'", "no_owner": "EXC AttributeError ...", "owner": "EXC AttributeError ..."}
{"case": "plist_deep_binary", ... "load_plans_EXC": "RecursionError: maximum recursion depth exceeded" ...}
{"case": "plan_deep_json_recursion", ... (3.14) "RecursionError: Stack overflow (used 16352 kB) while decoding a JSON array ..."}
```
The resident sequence (`fc_sequence.py ... plist_bad_date`) ends with `{"case": "plist_bad_date", "t-t0": -600, "STEP_EXC": "AttributeError: ..."}`.

Effect:
- `decide()` and `ResidentSupervisor.step()` raise, so no launch happens: the tick crashes.
- A session that is already running is never sent REQUEST, TERM or KILL. The forked supervisor exits through its `except BaseException` and `os._exit(0)` (magistrate_watchdog.py:3063).

This was already true on main for the same inputs. `decide` raised there too, and main's resident stayed in NETWORK_UNCERTAIN, also never standing down.

The cases are not reachable from the installer, whose template has no `<date>` element, or from the plan writer. The t0 census remains the backstop.

Fix in one line: catch `Exception` per plist inside `_installed_agent_plans`. The scanned path already wraps `json.loads` in `except Exception` (line 750).

### NIT-1: An installed plan that cannot be read and has no readable sibling drains on the generic timers

With no readable plan, t0 is unknown, so the drain falls back to STOP_COOPERATIVE_S = 540 s, then TERM, then 60 s grace, then KILL.

Command: `fc_sequence.py ... plan_missing`, with the drain starting at t0-600:
```
t0-600 HOLD_UNSAFE request; t0-60 SIGTERM; t0 SIGKILL
```
If such a fault appears less than 600 s before the real t0, the session is still alive at t0. This cannot be avoided without a readable t0. Main handles a torn scanned plan the same way. Recorded for information only.

When one plist is readable, the drain uses that plan's deadlines exactly. For both `torn_night_valid_deadman` and `night_and_deadman_name_different_plans`:
```
t0-600 HOLD_UNSAFE request; t0-90 SIGTERM; t0-60 SIGKILL
```

### NIT-2: Two intended behaviour changes to record in the PR body

1. A torn installed plist now also drains a running resident. Before, it held launches only and the resident stayed ACTIVE. This is the safe direction. The cost: a stale night plist whose plan has been moved keeps every magistrate off until the plist is removed.
2. A local STOP file during an installed-only span now reports FENCED or STANDDOWN_* instead of STOPPED. This matches the scanned-plan precedence; neither state launches.

## Checks requested

1. **Named test modules on the head.** The worktree was clean at that point (cwd = worktree):
   `python3.13 -B -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_b6 tests.test_magistrate_watchdog_span tests.test_magistrate_watchdog_yield tests.test_night_gate tests.test_night_plan_writer tests.hazards.test_refusal_allowlist`
   gives `Ran 352 tests in 21.260s OK`. Python 3.14.7 gives the same: `Ran 352 tests in 21.581s OK`.
   The seat's regression claim holds. With head's tests run on the 5f4620d71 watchdog source, `tests.test_magistrate_watchdog_b6` gives `Ran 8 tests ... FAILED (failures=14)`: all 8 methods fail, by assertion.

2. **MAJOR-1 scenario.** `replay_b6.py`:
   - Setup: the real MT plan, all path strings rewritten into `<sim>/night-b6/sessions/b6-alpha-s01-20261017T0000Z/`. The night and dead-man plists are copied with `--plan` rewritten into `<sim>/home/Library/LaunchAgents`, beside a magistrate plist, and HOME is set to `<sim>/home` (the `Path.home()` seam).
   - What the watchdog sees: `glob_plans: []`, then `load_plans: ["SMOKE-d117_floor_qwen3-1p7b_v5-20261016T2114Z"], errors: []`.
   - Fresh state at each time point, live owner:

     | t | decide | after actor | standdown.request | signal |
     |---|---|---|---|---|
     | t0-600 | ACTIVE | ACTIVE | no | none |
     | t0-181 | ACTIVE | ACTIVE | no | none |
     | t0-180 | STANDDOWN_REQUEST | STANDDOWN_REQUESTED | yes | none |
     | t0-91 | STANDDOWN_REQUEST | STANDDOWN_REQUESTED | yes | none |
     | t0-90 | STANDDOWN_TERM | STANDDOWN_TERM | yes | SIGTERM |
     | t0-61 | STANDDOWN_TERM | STANDDOWN_TERM | yes | SIGTERM |
     | t0-60 | STANDDOWN_KILL | FENCED | (cleared) | SIGKILL |
     | t0+60 (chain.started) | STANDDOWN_KILL | FENCED | | SIGKILL |
     | completion+60, courier.sent | ACTIVE | ACTIVE | | none |

   - Without an owner: LAUNCHING until t0-181, then FENCED from t0-180 through t0+60, then LAUNCHING after completion.
   - `fenced_checkouts` now includes the plan's measurement checkout, which closes r1 MINOR-1.
   - One resident stepped every 10 s, ignoring SIGTERM:
     ```
     -590 ACTIVE; -180 STANDDOWN_REQUESTED request=true; -90 STANDDOWN_TERM [SIGTERM]; -60 FENCED [SIGTERM, SIGKILL] owner_alive=false
     ```
   - Python 3.13 and 3.14 outputs are identical after path normalisation.
   - Contrast on base 5f4620d71: every owner row stays ACTIVE with no request and no signal (MAJOR-1 reproduced).
   - Main cannot parse the plan (`bindings must name exactly the fourteen launch bindings`).

3. **Fail-closed cases** (`failclosed_b6.py`, at t0-600 and t0-170, without and with an owner).
   - These cases all give `HOLD_UNSAFE launch=False`; with an owner, the drain writes `standdown.request`:
     - plan missing, chmod 000, not JSON, a JSON list, rejected by the validator, future-authored, not UTF-8, a directory;
     - `--plan` given twice, `--plan` last, a relative plan path, a NUL in the path;
     - plist garbage, bad XML, no ProgramArguments, ProgramArguments a dict, top-level array, bad integer;
     - plist is a directory, plist is a dangling symlink, LaunchAgents is a dangling symlink, LaunchAgents is a file.

     That is the safe direction: no launch, and a running session is drained.
   - Night and dead-man plists naming different plans: both are loaded and the result is HOLD_UNSAFE. The drain then follows the plan deadlines (TERM at t0-90, KILL at t0-60).
   - The same plan_id at two paths: both are kept and the result is HOLD_UNSAFE (plan conflict).
   - The magistrate plist alone is ignored (`plans: []`, LAUNCHING).
   - Exceptions not caught: see MINOR-1. `json.JSONDecodeError` and `UnicodeDecodeError` are ValueErrors and are caught. `InvalidFileException` and `ExpatError` are caught.

4. **Real Mac state, read only.** `realstate.py` with `Storage('/Users/edr/night-custody/magistrate', dry_run=True)`, same result under 3.13 and 3.14:
   - LaunchAgents joulewise entries are `com.joulewise.b6mt.after.plist`, `com.joulewise.b6mt.quiet.plist` and `com.joulewise.magistrate.plist`.
   - `_installed_agent_plans: []`, `installed_agent_fence: None`, `load_plans errors: []`, `would_write: []`.
   - `load_plans` returns the 26 historic scanned plans under /Users/edr/night-custody, all past. It returns no installed plans.
   - Only the `com.joulewise.night` and `com.joulewise.night.deadman` labels are read, so the magistrate and b6mt plists are never parsed as night plists.
   - The lane's `joulewise/b6/driver_lane.py` installs exactly these two labels, with `launch_lead_s` = 420 s. The resident polls every 10 s, so it sees an installed plan before t0-180.

5. **v2 and block-5 v5 parity with main.**
   - Decisions: `equiv.py` covered all 394 on-disk plans; 392 parsed (381 v2, 11 v5) and 2 were refused identically on both sides. It ran decide plus the next actor at t0-600, t0-170, t0-70, t0+60 and completion+60, with night states none, started and done_sent, without and with an owner. Main d79e03549 against head: `rows 11762 11762 differing 0`.
   - Validator: `allplans.py` over 458 plans changes only the 4 block-6 machine-test plans (refused to ok), as in r1.
   - Main's own watchdog tests run on head code: `FAILED (failures=9, errors=5)`, as expected.
     - Failures: only the installed-only expectations the PR deliberately changed (`installed_plan:` reason, STOP precedence, torn-plist drain).
     - Errors: the main version of test_night_plan_writer, which lacks the lead's `list_directory` mock, plus four CLI tests that need a git checkout.

6. **No silly numbers.** The production diff adds no numeric constant; `git diff 5f4620d71 ed665952e -- scripts/magistrate_watchdog.py | grep '^+' | grep '[0-9]'` is empty.
   - REQUEST, TERM and KILL stay at 180, 90 and 60 s, with their derivation in LEAD-MARGIN-01.
   - The test offsets (600, 170, 70, +60, +1 s) are sample points chosen to fall on either side of those leads. They are not tolerances.
   - The capture_screen strings in the fixture are not read by the watchdog.
   - The four allowlist rows are census-computed counts and hashes.

## What I ran

All commands used absolute paths and `git -C`. Main, base and head trees came from `git archive` into /private/tmp (wdrev-main, wdrev-base, wdrev-head, and wdrev-mixed = head with main's tests). Later module runs used `python -B -P` so that cwd could not shadow PYTHONPATH.

- The test modules listed above, under /opt/homebrew/bin/python3.13 (3.13.1) and /opt/homebrew/opt/python@3.14/bin/python3.14 (3.14.7).
- `replay_b6.py` on head (3.13 and 3.14), base and main.
- `failclosed_b6.py`: 30 cases on head under 3.13, a subset under 3.14, and the uncaught cases on main.
- `fc_sequence.py`: different plans, torn sibling, plan missing, bad date.
- `equiv.py` and `allplans.py`, main against head.
- `realstate.py` (read only).
- `gh pr view 500` and `gh run view 39038153339 --log-failed`.

A process-hygiene note: one early run of mine (`-m unittest` without `-P`, cwd = the canonical checkout) imported canonical main code. I stopped it and discarded its result. Afterwards `git -C /Users/edr/code/JouleWise status` showed only the two pre-existing untracked files.

## Addendum: head 8d3fbdc94 (lead's test-only commit) and the fence-string de-duplication

**What 8d3fbdc94 changes.** `git -C $W diff ed665952e 8d3fbdc94` touches tests/test_night_agent_install.py only, 2 lines. They are byte-identical to the uncommitted edit that BLOCKER-1 above describes.

**Test run.** I ran the 7-module set with that content in the worktree: tests.test_magistrate_watchdog_cli, test_install_magistrate_watchdog, test_install_night_agent, test_night_agent_install, test_fixture_orphan_census, test_b5_plan and test_evidence_night. Result: `Ran 376 tests in 1054.399s OK`. The worktree is now clean at 8d3fbdc94.

**CI.** When this addendum was written, CI on 8d3fbdc94 was still running. Shown so far: build and changes SUCCESS. gate-ledger FAILURE, because ledger rows are not yet filled.

**BLOCKER-1 status.** BLOCKER-1 is resolved once the 12 test shards pass.

### The de-duplication is correct

The de-duplication key is (plan_id, resolved `--plan` path). The night and dead-man plists normally name the same plan file. That is one plan, so naming it once is the right output.

The string never collapses distinct plans:
- the same plan_id at two different paths stays listed twice;
- `load_plans` then reports that pair as a plan conflict, giving HOLD_UNSAFE (executed above, case `night_and_deadman_same_id_different_paths`).

Both plists are still validated before de-duplication. A torn dead-man plist therefore cannot hide behind a valid night plist (cases `torn_night_valid_deadman` and `test_readable_installed_sibling_keeps_deadlines_when_other_plist_is_torn`).

### Nothing consumes the per-plist count

Search command: `git grep -nE "installed_agent_fence\(|installed_plan:"` over scripts/, joulewise/, tools/ and *.sh/*.zsh, at 8d3fbdc94, d79e03549 (main) and lane/2026-10-16-b6-round2.

- **At 8d3fbdc94.** The only production occurrence is the definition (scripts/magistrate_watchdog.py:844-849). `decide()` and `_launch_fence` no longer call it. Every decision now goes through `load_plans`, whose reasons are "plan span active and census empty", "plan span active at launch boundary" and STANDDOWN_*. `installed_agent_fence` is now called only by tests:
  - test_magistrate_watchdog.py:2861 and others;
  - test_magistrate_watchdog_b6.py:151;
  - test_night_agent_install.py:871.
- **On main.** The string was used only as a Decision reason in `decide()` and `_launch_fence`, written to state.json and events.jsonl as free text. Nothing parses it or counts its parts.
- **On the lane.** No reference outside its watchdog copy.
- **On disk.** `/Users/edr/night-custody/magistrate/events.jsonl` has 0 lines containing `installed_plan`.

So the change of count, from one per plist to one per plan, affects no decision and no consumer. Only the four test assertions depended on it, and they are now updated.

### NIT-3 (new)

`installed_agent_fence()` no longer has a production caller. Two options:
- delete it and point those tests at `load_plans`;
- or keep it as a test or diagnostic helper and say so in its docstring.

docs/process/MAGISTRATE_WATCHDOG.md:35 and :116-119 still describe the installed-only path as "`FENCED` with `adopt=False`" and the fence reason as `installed_plan:<plan_id>`. That is now wrong: installed plans get STANDDOWN_* with `adopt=True`, using the common reasons. The doc needs a one-paragraph update. This is light tier and does not block the merge.

### Verdict on 8d3fbdc94

APPROVE-WITH-NITS once CI is green on 8d3fbdc94. Still open, none of them merge blockers:
- MINOR-1: catch `Exception` per plist;
- NIT-1 and NIT-2;
- NIT-3: the doc and the dead helper.

## Delta review: head 374509f83 (6d014015b and 374509f83 on top of 8d3fbdc94)

**Verdict: APPROVE-WITH-NITS, once the CI shards are green.** At the time of writing:
- CI shows build, changes, fences and installed-wheel SUCCESS;
- quick and the test shards are pending;
- gate-ledger shows FAILURE until the ledger rows are filled.

### What I executed

1. **The new test passes on the head and fails on 8d3fbdc94.**
   - Head:
     `PYTHONPATH=$W python3.1x -B -P -m unittest tests.test_magistrate_watchdog_b6.InstalledBlockSixTests.test_installed_plist_content_faults_hold_and_drain`
     gives `Ran 1 test OK` under both python3.13 and python3.14.
   - The same test against the 8d3fbdc94 watchdog: I used a `git archive 374509f83` tree with `scripts/magistrate_watchdog.py` taken from 8d3fbdc94. It gives `ERROR ... (body='bad_date') AttributeError: 'NoneType' object has no attribute 'groupdict'` and `FAILED (errors=1)` on both interpreters.

2. **MINOR-1 is closed.** I re-ran `failclosed_b6.py` on the head under 3.13 and 3.14, at t0-170. All three formerly escaping cases now give the same outcome: `HOLD_UNSAFE launch=False`, and with an owner, `HOLD_UNSAFE req=True`. The error strings carried in the snapshot:
   - `plist_bad_date`: "'NoneType' object has no attribute 'groupdict'";
   - `plist_deep_binary`: "maximum recursion depth exceeded";
   - `plan_deep_json_recursion`, a 200,000-deep plan JSON named by a plist: "maximum recursion depth exceeded while decoding a JSON array" (3.14: "Stack overflow ... while decoding a JSON array").

   So the plan path reached through a plist is covered: the plan's `json.loads` sits inside the widened `try`.

   Running the resident sequence (`fc_sequence.py ... plist_bad_date`): the resident survives and drains. It gives `t0-600 HOLD_UNSAFE request`, then `t0-60 SIGTERM`, then `t0 SIGKILL`. Those are the generic 540/600 s timers, because no t0 is readable (NIT-1, which you deferred to a named lane).

   Controls are unchanged: `valid_pair` gives FENCED / STANDDOWN_REQUEST, and `plan_missing` gives HOLD_UNSAFE.

3. **The scanned path.** `fuzz_from_mapping.py` took three real plans (block-6 MT, b5 v5, v2) and substituted 12 values into every field and nested field. The values were None, [], {}, "x", 1, -1, 1.5, True, NaN, inf, 10**400 and "0.1": 2,436 mutations in all. None of them raised outside the scanned path's `(PlanError, ValueError, OverflowError)`. Its `json.loads` was already under `except Exception`.

4. **Test modules.** Head 374509f83, clean worktree. I ran 7 modules: `tests.test_magistrate_watchdog`, `_b6`, `_span`, `_yield`, `tests.test_night_gate`, `tests.test_night_plan_writer` and `tests.hazards.test_refusal_allowlist`.
   - `Ran 353 tests OK` on python3.13 (27.5 s) and on python3.14 (29.0 s).
   - `python3.13 -m tests.hazards.refusal_census` exits 0, with no unlisted, miscounted, guard-changed or scope-gap rows.
   - I did not re-run test_night_agent_install. It is unchanged since 8d3fbdc94, where it passed locally, and its assertions do not depend on the except clause. CI will cover it.

### Does `except Exception` swallow too much?

- **Interrupts and exits are not swallowed.** `KeyboardInterrupt`, `SystemExit` and `GeneratorExit` derive from BaseException, not Exception, so they still propagate.
- **What it does catch.** `RecursionError` and `MemoryError` are Exception subclasses, so they become HOLD_UNSAFE plus a drain. That is the safe direction.
- **Masking a real bug.** A code bug inside the try (in from_mapping, deadman_epoch or the argv parsing) would now give HOLD_UNSAFE plus a drain on the generic timers, with the exception text in the state.json reason, instead of crashing the tick and the resident. Before this change, such a crash meant no stand-down at all. So for the agent-alive hazard the change is strictly better.
- **What it costs.** A bug like that would hold magistrate launches until someone reads the reason. That costs magistrate time, not data. The existing valid-plan tests (test_magistrate_watchdog_b6, the decide-phase tests) would go red on such a bug, so it would not land silently.

### Is the documentation accurate?

docs/process/MAGISTRATE_WATCHDOG.md now matches the code.
- The `FENCED` bullet and decide-order steps 2-5 describe the actual behaviour: one plan set from the scan plus both plists; STANDDOWN_* with adopt=True; a torn plist giving HOLD_UNSAFE that also drains, with a readable sibling keeping its deadlines; and STOP during an installed span reporting the span's state.
- `installed_agent_fence` is now documented as a test helper that `decide()` no longer calls. That is true: its only callers are in tests.
- The `t0 - 8/6/5 min` wording elsewhere in the doc is stale. The doc's own erratum note at lines 60-66 already says to read 180/90/60 s, matching the constants at magistrate_watchdog.py:96-98. No action is needed in this PR.

### The four allowlist rows

They are census-computed. The guards moved because the `except` line is part of each guard's context. Reclassifying them BASELINE to INTERNAL, with a protects line, is consistent with the r2 rows. `refusal_census` exits 0.

### NIT-4: the new test's "deep" case does not exercise RecursionError

`plistlib.loads` of 5000-deep nested `<array>` XML parses fine: `parsed ok, type list` under python3.13, because the XML plist reader is not recursive. The case then fails on `document["ProgramArguments"]` with a TypeError, which 8d3fbdc94 already caught. That subtest passed on 8d3fbdc94, so only `bad_date` guards the change.

A recursion case needs a deep binary plist (the `deep_binary_plist(200000)` builder in failclosed_b6.py) or a deeply nested plan JSON named by a valid plist. This is optional; behaviour is correct as executed above.

### Open items

- NIT-1 (deferred to a named lane);
- NIT-4;
- confirm the CI shards are green on 374509f83.
