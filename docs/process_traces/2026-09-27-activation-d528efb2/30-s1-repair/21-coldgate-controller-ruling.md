RULING: S1-REGRESSION-01-A2 ISSUED

# Cold gate S1-REGRESSION-01-A2 — the controller test that contradicts text 12a

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one session, no subagents. Session 2026-09-27, 19:13 to about 19:40 PDT by the host clock. Python was `/opt/homebrew/bin/python3 -B`. Scratch is under `/tmp/cg-s1ctl-d528efb2/`. No file in any repository was modified; this file is the only file written. Seat P's worktree printed nothing for `git status --short` before and after my work.

**Verdict in one paragraph.** Seat P admitted exactly what text 12a allows and nothing more. The failing test exercises the experiment manifest aggregate, which is the second of 12a's two admitted flows. Its assertion is stale. `tests/test_controller.py` is granted for one class, with exact text given in §5. The old refusal assertion is kept, not deleted: it moves to the strict call form of the same aggregate, and a new test pins that a real experiment measured while the battery was charging is still refused through the controller. No production byte changes.

## 0. Contamination disclosure and one protocol deviation

**Loaded by the harness without my choosing, before my first turn:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md` of the worktree I was started in, the memory index `MEMORY.md` (one-line pointers, several naming loop context such as checkpoints, directives and model assignments), a list of skills and agent types, the git status and five commit subjects. I used none of it for any ruling below. One exception is stated openly: the global file's writing standard (define each term at first use) matches what I would do anyway, and this text follows it.

**Not opened by me:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file, the decision log, the consult seats, seat P's brief, seat H's brief and report. My scratch exports (E1) contain copies of the first four because `git archive` exports the whole tree; I did not open them.

**Read by me:** the charge; the ruling (`21-…`) and addendum A1 (`31-…`), both in full; seat P's report in full; the code and tests named under Executed evidence. I read seat P's report before forming my view, so my view is not blind to it. Every claim of seat P that I rely on was re-executed by me.

**Protocol deviation, stated plainly.** One of my commands (a run of two whole test modules on three trees) exceeded the harness's 600-second limit, and the harness moved it to the background without my asking. The protocol forbids background tasks. I stopped it by PID within seconds of noticing: the shell loop (PID 60034), the Python test process (PID 85407), and one fake-powermetrics helper process that an earlier timed-out test run had left orphaned (PID 85023). A process listing afterwards showed nothing of mine running. I rely on that run only for the two facts in E9, both of which I re-executed in the foreground.

**The laptop battery was never read.** Every test command ran under a guard of my own (E2) that raises before any `ioreg` process can start. The guard logged attempts; each one was blocked.

## 1. Terms used in this ruling

Terms defined in the ruling's §1 and the addendum's §1 keep their meaning. The ones this text leans on, restated so it can be read alone:

- **S1.** The pull request that makes every reader of a measurement bundle check the bundle's battery evidence first. Head `c7593edb`. **Seat P's head** is `db4eadf6`, one commit on top of it.
- **Bundle.** One run's directory (`config.json`, `metadata.json`, `events.jsonl`, the power trace, the summary).
- **Battery pair.** Two recorded readings of the laptop battery, before and after the measured span. **Charging pair:** a pair that shows the battery taking charge, so the meter's energy cannot be attributed to the workload alone.
- **The window gate.** The function `authenticate_window_members` in `joulewise/bundle_read.py`. It takes a set of bundles (a **window**) and either returns one verdict per member or raises `WindowBatteryRefusal`, an exception that lists every refused member with its status.
- **Statuses used here.** `not_applicable`: the bundle's digest-bound config names the synthetic `mock` telemetry backend, so no physical energy was measured. `battery_float_confounded`: the pair shows charging. `pass`: the pair is authentic and the battery was at float (neither charging nor discharging).
- **Mock window.** A window with at least one member that owes a verdict, where every such member is `not_applicable`.
- **The keyword.** The parameter `admit_mock_window` of the window gate, added by text 12a. Default `False` (strict: any `not_applicable` member refuses the window). With `True`, a mock window is returned instead of refused; every other window behaves as under the default.
- **Experiment.** One call of `run_experiment` in `joulewise/controller.py`: it runs the same config `repetitions` times, one bundle per repetition. **Experiment manifest:** the file `runs_root/experiments/<experiment_id>.json` that lists those bundles. **Aggregate block:** the manifest's key `aggregate`, a summary computed by `aggregate_experiment` in `joulewise/aggregate.py`; it carries `battery_float_members`, a map from each member's name to its status.
- **Strict call form.** A call of `aggregate_experiment(runs_root, manifest)` with no keyword. This is how the figures script `scripts/make_figures.py` calls it.
- **Runner.** The function the controller calls to obtain the raw battery reading. `run_benchmark` takes it as the parameter `battery_runner`; when none is given, the controller starts the real `/usr/sbin/ioreg`.
- **R-list.** The list, by test ID, of every test whose assertion is changed (not just its fixture), each approved by the lead. **Assertion census:** the ruling's check 1, which compares the assertions of each test on main and on the candidate.

## 2. Executed evidence (this session)

| # | Probe | Result |
|---|---|---|
| E1 | `git rev-parse HEAD` and `git status --short` on seat P's worktree; `git diff --stat c7593edb HEAD`; `git archive` of `db4eadf6` and of `c7593edb` into scratch (`tree-db4`, `tree-c75`) | Head `db4eadf692708b54a389e863ab384cf8477fd2bd`, clean. Eight files changed: the five production files and the three test files of seat P's scope. **`tests/test_controller.py` is unchanged by seat P** (`git diff c7593edb db4eadf6 -- tests/test_controller.py` prints 0 lines). All tests below ran in the scratch exports, never in a repository. |
| E2 | My guard, `/tmp/cg-s1ctl-d528efb2/guard/sitecustomize.py`, on `PYTHONPATH` for every test command | It wraps `subprocess.Popen.__init__`; if the command line contains `ioreg` it writes one log line and raises. It supplies no bytes and changes no return value. |
| E3 | Read `tests/test_controller.py:3286-3295` at `db4eadf6` | The test calls `run_experiment(make_suite_config("suite-mock-refusal", repetitions=2), …)` and expects `WindowBatteryRefusal` with one member of status `not_applicable`. The suite fixture config names the `mock` backend. |
| E4 | Read `joulewise/controller.py:2965-3014` at `db4eadf6` | After each repetition the controller appends the member, writes the manifest (`:3002`), and calls `aggregate_experiment(runs_root, manifest, admit_mock_window=True)` (`:3004`). An exception is recorded under `aggregate_error` and re-raised (`:3005-3012`). **This is the call site text 12a (c) item 2 names by file and line.** |
| E5 | Read `joulewise/aggregate.py:92-160` at `db4eadf6` | The keyword defaults to `False` (`:93`), is forwarded to the whole-set gate call (`:106-111`) and to `_read_member` (`:113`, `:148`, `:159-160`). The block carries `battery_float_members` (`:128-130`). Matches 12a (c) item 2 word for word. |
| E6 | Read `joulewise/bundle_read.py:282-360` at `db4eadf6` | The gate raises unless all four hold: the keyword is `True`; at least one verdict exists; every verdict is among the refused rows (`len(refused) == len(verdicts)`); every verdict is `not_applicable` (`:353-359`). A member refused through the exception path (`:328-331`) is in `refused` but not in `verdicts`, so the lengths differ and the window refuses. Custody exceptions are raised inside the loop (`:332-343`), before the admission test. Matches 12a (a) and (b). |
| E7 | `grep -rn admit_mock_window joulewise scripts` at `db4eadf6` | Literal `True` at exactly two places: `joulewise/controller.py:3004` and `scripts/run_campaign.py:9032`. Everything else is the parameter and its forwarding inside `aggregate.py` and `bundle_read.py`. **Equal to the closed list of 12a (c).** The paired-entry gate at `run_campaign.py:7848` does not pass it. |
| E8 | The test, run alone with its neighbour, on both exports | At `c7593edb`: 2 tests, `OK`. At `db4eadf6`: `FAIL: test_mock_experiment_refuses_at_aggregation … AssertionError: WindowBatteryRefusal not raised` at `tests/test_controller.py:3288`; the neighbour passes. **Seat P's flag F1 is re-executed and holds.** |
| E9 | The whole class `SuiteControllerTests` at `db4eadf6`; then the three tests that showed as failures in the cut run, by ID, on both exports | Class: 8 tests, 1 failure (the flagged test). The other two failures are `HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` (`tests/test_controller.py:1812`) and `HappyPathTests.test_powermetrics_thermal_coverage_is_continuous_across_admission_handoff` (`:2033`). **Both fail identically on `c7593edb` and on `db4eadf6`** (`RunStatus.FAILED != RunStatus.SUCCEEDED`), and my guard logged 8 blocked `ioreg` attempts for the two runs. So they are not caused by seat P; they fail because my guard blocked the real battery probe they start. See §7. |
| E10 | `git log -S test_mock_experiment_refuses_at_aggregation`; `git diff e7c8bcc6...c7593edb -- tests/test_controller.py` | The flagged test was **added by S1** (commit `cbfa9dc3`); it does not exist on main. In the same commit S1 changed the neighbouring test `test_run_experiment_suite_uses_repetition_order_seed`: it wrapped the `run_experiment` call in `patch("joulewise.controller.aggregate_experiment", return_value={})` with the comment "mock bundles cannot enter a claim-bearing aggregate window under the battery gate". On main that test runs the real aggregate. |
| E11 | The replacement text of §5, applied to a scratch copy (`proto`) of the `db4eadf6` export; run as four tests, as the whole class, and the new charging test alone in a fresh process | Whole class: `Ran 10 tests … OK`. Charging test alone: `OK`. Zero `ioreg` attempts logged. By script over the syntax tree, the restored neighbour test is **byte-identical to main's** (`e7c8bcc6`). Resulting file SHA-256 `5a572df43b7b0151a5778834523953dd2f773fdcd33ba4f3efc24bcbca9a5d15`, from a base file of `ae2f108ec506e05fe88009eb0d3c6aadddb1ae5afb947fdf653e24baa4626b88`. |
| E12 | Four planted defects in the scratch copy's production files, one at a time, each reverted and the file compared byte-for-byte with the export afterwards | See the table in §5.3. Every replacement test went RED under at least one defect, and each defect turned a different test RED. |
| E13 | A first draft of the charging test, which fed the charging bytes by `patch("joulewise.battery_float.subprocess.run", …)` | **Rejected by execution.** It passed when it ran after other tests and errored when it ran first, and then broke every later test in the class (`BundleError: metadata.json must be written before the summary`). That patch replaces `subprocess.run` for the whole process, not for the battery probe alone. The text of §5 injects the runner through the controller's own `battery_runner` parameter instead, and passes in both orders. |
| E14 | `grep` over the added lines of the replacement | No `admit_mock_window`, no `battery_float.observe(`, no `raw/battery_float.` (addendum check 2, last item and (k)). |
| E15 | `grep` for readers of `["aggregate"]` and `battery_float_members` under `joulewise/` and `scripts/`; read `scripts/mint_floor_artifact_generalized.py:988-989`, `:1908` | The only two hits on `["aggregate"]` outside the writer read a different document (a floor "pinset"), not an experiment manifest. I found no production reader of an experiment manifest's aggregate block by this search. |

**NOT EXECUTED by me:** any full suite; the whole of `tests.test_controller` or `tests.test_reduce` to completion (the module pair did not finish in 400 seconds per tree; see §0); the three `test_reduce` failures seat P left untriaged; the campaign completion flow at `run_campaign.py:9032` beyond the `grep` of E7; seat P's tests T12a-1 to T12a-11 (taken from seat P's V1, which reports 56 tests `OK`); the addendum's check 2 (l) with its wrapper; whether a reader of the experiment manifest's aggregate block exists outside `joulewise/` and `scripts/`, or reads the key by a form my `grep` does not match.

## 3. Ruling 1 — the flow is admitted, and seat P did not over-admit

**The flow.** The test calls `run_experiment`. After the first repetition the controller calls the aggregate at `controller.py:3004` with the keyword `True` (E4). The window at that moment holds one bundle whose bound config names `mock`, so it is a mock window, and the gate returns (E6). The aggregate block is written with that member shown as `not_applicable` (E5). Text 12a (c) item 2 names this call site by file and line, and 12a (d) names "the experiment manifest's aggregate block" as one of the two things an admitted mock window may produce. **The test's flow is the second admitted flow, as ruled.**

**Seat P's diff against the text.** I compared each clause of 12a with the code:

| Clause of 12a | Code at `db4eadf6` | Holds? |
|---|---|---|
| (a) mock window = at least one obligated member, all `not_applicable` | `bundle_read.py:353-358`; members with no `idle_baseline` start are skipped at `:315-326` and so are in neither list | Yes |
| (b) default is strict; with `True` any other window refuses and names every refused member | default `False` at `:284`; the refusal carries the whole `refused` list (`:359`) | Yes |
| (b) custody exceptions propagate in every case | raised inside the loop, before the admission test (`:332-343`) | Yes |
| (c) exactly two call sites pass `True` | E7 | Yes |
| (c) item 2: the keyword is forwarded to the whole-set call and to `_read_member` | `aggregate.py:110`, `:113`, `:160` | Yes |
| (c) `make_figures.py` stays strict | it passes nothing; the default is `False` | Yes |

**So ruling 3 of the charge is empty: there is no correction to seat P's production diff, and no production seat is named.**

**Why the test was right when written and is stale now.** S1 wrote this test at a time when its gate had one behaviour for every caller (E10). The test pinned that behaviour at the controller. The ruling then found that behaviour stricter than text 12 and amended it with 12a. The test pins the behaviour 12a replaced.

## 4. Ruling 2 — the grant

**GRANTED, for this repair only:** `tests/test_controller.py`, limited to the class `SuiteControllerTests` and within it to exactly these four edits. Every other byte of the file stays identical to `c7593edb`.

1. `test_mock_experiment_refuses_at_aggregation` is rewritten (R-list entry; §5.2, second function).
2. `test_mock_experiment_aggregate_shows_every_member_not_applicable` is added (first function).
3. `test_charging_experiment_refuses_at_aggregation` is added (third function).
4. `test_run_experiment_suite_uses_repetition_order_seed` is restored to main's bytes (§5.1).

**"Split, never delete": where each piece of the old test goes.**

| What the old test covered | Where it lives after this ruling |
|---|---|
| A mock experiment run through the controller reaches the aggregate and the gate sees its members | Edit 2: the same run now completes, and the manifest shows both members as `not_applicable`. |
| A window of mock bundles is refused, by exception type and by status | Edit 1: the **same test name, the same exception type, the same status literal `{"not_applicable"}`**. The call under `assertRaises` changes from `run_experiment` to the strict call form of `aggregate_experiment` on the manifest that experiment just wrote. This is the call the figures script makes, which 12a keeps strict. The member count changes from 1 to 2 because the experiment now finishes both repetitions, and an assertion on the member labels is added. |
| The controller's aggregate call can still refuse, and the refusal leaves the manifest with `aggregate_error` and no `aggregate` | Edit 3: a non-mock experiment whose battery pair shows charging is refused at the controller's own call (the one that passes `True`), with status `battery_float_confounded`. This is the case the keyword must never admit. |

**Why edit 4 is in the grant although that test is green.** Its patch and its comment were S1's workaround for the behaviour 12a removed (E10). Left in place, the comment tells a reader something that is no longer the reason for anything, and the patch hides the real aggregate from a test that ran it on main. Restoring main's bytes removes one hunk from S1's difference against main; the assertions are untouched. It costs nothing to review because the target is main's own text.

**Who carries it: the lead, at the bench, as one commit on seat P's branch on top of `db4eadf6`, before step 2's merge of P and H.** The text is exact and was executed by me (E11, E12), so applying it is mechanical, and briefing a seat would cost more than the work. No seat's WRITE_SCOPE changes: seat P's stays the eight paths of the ruling's step 1, and seats A to D do not receive this file. Seats A to D start from the step-2 head and must find `SuiteControllerTests` green there.

**Acceptance, all four required.**

- (i) After the edit, `shasum -a 256 tests/test_controller.py` prints `5a572df43b7b0151a5778834523953dd2f773fdcd33ba4f3efc24bcbca9a5d15`. If the lead's file differs only in whitespace from the text of §5, the lead records the digest obtained and the `git diff`; any other difference stops the edit.
- (ii) `python3 -B -m unittest tests.test_controller.SuiteControllerTests` prints `Ran 10 tests` and `OK`, with the runner guarded so the real probe cannot start.
- (iii) `git diff c7593edb HEAD -- tests/test_controller.py` shows hunks inside `SuiteControllerTests` only.
- (iv) The planted defects D1 to D4 of §5.3 each turn the named test RED in a scratch worktree, after the landing is committed.

**Stop rule.** If the text does not apply, or a test of the class is not green, or a defect does not turn its test RED, the lead stops and returns to a cold gate with the output. The text is not adjusted at the bench.

## 5. The exact text

### 5.1 Edit 4: restore the neighbour to main's bytes

Replace the first eight lines of the body of `test_run_experiment_suite_uses_repetition_order_seed` (the two comment lines, the `with patch(…)` line and the indented call) with main's five lines. The rest of the function is unchanged.

```python
    def test_run_experiment_suite_uses_repetition_order_seed(self) -> None:
        manifest_path, results = run_experiment(
            make_suite_config("suite-experiment", repetitions=2),
            self.runs_root,
            self.clock,
        )
        self.assertTrue(manifest_path.is_file())
```

Check: the function equals the one printed by `git show e7c8bcc6:tests/test_controller.py`.

### 5.2 Edits 1 to 3: replace the flagged test with these three functions

They stand where the old test stood, at the end of the class, followed by two blank lines and the file's existing `if __name__ == "__main__":` block.

```python
    def test_mock_experiment_aggregate_shows_every_member_not_applicable(self) -> None:
        manifest_path, results = run_experiment(
            make_suite_config("suite-mock-admitted", repetitions=2),
            self.runs_root, self.clock,
        )
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(len(results), 2)
        self.assertNotIn("aggregate_error", manifest)
        self.assertEqual(manifest["aggregate"]["members_total"], 2)
        self.assertEqual(manifest["aggregate"]["battery_float_members"],
                         {path.name: "not_applicable" for path, _ in results})

    def test_mock_experiment_refuses_at_aggregation(self) -> None:
        from joulewise.aggregate import aggregate_experiment
        from joulewise.bundle_read import WindowBatteryRefusal
        manifest_path, results = run_experiment(
            make_suite_config("suite-mock-refusal", repetitions=2),
            self.runs_root, self.clock,
        )
        manifest = json.loads(manifest_path.read_text())
        with self.assertRaises(WindowBatteryRefusal) as caught:
            aggregate_experiment(self.runs_root, manifest)
        self.assertEqual(len(caught.exception.members), 2)
        self.assertEqual({row["label"] for row in caught.exception.members},
                         {path.name for path, _ in results})
        self.assertEqual({row["status"] for row in caught.exception.members},
                         {"not_applicable"})

    def test_charging_experiment_refuses_at_aggregation(self) -> None:
        from joulewise.bundle_read import WindowBatteryRefusal
        payload = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        payload["run_id"] = "charging-experiment"
        payload["hardware_target"]["telemetry_backend"] = "wall_meter"
        payload["workload_profile"]["repetitions"] = 2
        charging = (
            REPO_ROOT / "tests/fixtures/battery_float/charging-synthetic-from-real.ioreg"
        ).read_bytes()
        calls = []

        def runner(argv):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, charging, b"")

        def member_run(*args, **kwargs):
            return run_benchmark(*args, battery_runner=runner, **kwargs)

        with patch("joulewise.controller.run_benchmark", side_effect=member_run):
            with self.assertRaises(WindowBatteryRefusal) as caught:
                run_experiment(
                    BenchmarkConfig.from_mapping(payload), self.runs_root,
                    FakeClock(1790373526), registry=BatteryBracketTests.Registry(),
                )
        self.assertEqual(len(calls), 2)
        self.assertEqual([row["label"] for row in caught.exception.members],
                         ["charging-experiment__r1"])
        self.assertEqual({row["status"] for row in caught.exception.members},
                         {"battery_float_confounded"})
        manifest = json.loads(
            (self.runs_root / "experiments" / "charging-experiment.json").read_text())
        self.assertNotIn("aggregate", manifest)
        self.assertEqual(manifest["aggregate_error"]["error_type"], "WindowBatteryRefusal")
```

**How the charging test works, step by step, so it can be rebuilt from this text.**

1. The config names the backend `wall_meter`, so the controller owes a battery pair and does not write the mock marker (`controller.py:2119-2122`).
2. The registry `BatteryBracketTests.Registry` (already in this file, written by S1) hands the controller the synthetic telemetry adapter, so no meter hardware is needed.
3. `run_experiment` has no parameter for the runner. The test replaces the name `run_benchmark` inside the controller module by a wrapper that calls the real `run_benchmark` with `battery_runner=runner` added. The runner returns the bytes of the repository's charging fixture and records each call. Nothing else in the process is replaced (contrast E13).
4. The controller probes twice for repetition 1 (before and after the span), writes the pair, and finishes the bundle. `len(calls) == 2` shows that repetition 2 never started.
5. The controller calls the aggregate with the keyword `True`. The one member's verdict is `battery_float_confounded`, so the window is not a mock window and the gate raises.
6. The controller records the error in the manifest and re-raises (`controller.py:3005-3012`). The test reads the manifest and finds `aggregate_error` and no `aggregate`.

### 5.3 Planted defects (executed by me in scratch, E12; the lead repeats them as acceptance (iv))

| Id | Defect planted in production | Test that went RED | Observed |
|---|---|---|---|
| D1 | `bundle_read.py:353-358` reduced to `if refused and not admit_mock_window:` (the keyword admits any window) | `test_charging_experiment_refuses_at_aggregation` | `WindowBatteryRefusal not raised` |
| D2 | the keyword's default in `aggregate_experiment` flipped to `True` | `test_mock_experiment_refuses_at_aggregation` | `WindowBatteryRefusal not raised` |
| D3 | the keyword removed at `controller.py:3004` (S1's behaviour at `c7593edb`) | `test_mock_experiment_aggregate_shows_every_member_not_applicable`, and with it the rewritten refusal test and the restored neighbour | 3 errors, each the refusal raised out of `run_experiment` |
| D4 | `battery_float_members` dropped from the aggregate block (`aggregate.py:128-130`) | `test_mock_experiment_aggregate_shows_every_member_not_applicable` | `KeyError: 'battery_float_members'` |

Under D1 the two mock tests stay green and under D2 the charging test stays green, so each refusal test guards a different edge of the keyword.

## 6. Ruling 4 — what changes in the ruling and the addendum

**No clause of text 12a or text 10a changes. No production path, no seat, no order and no other granted path changes.** These bookkeeping clauses change, each by one entry:

| Where | Change |
|---|---|
| Ruling §6, grant list | Add `tests/test_controller.py   (class SuiteControllerTests only; the four edits of S1-REGRESSION-01-A2 §4; carried by the lead)`. |
| Addendum §6, modification 2 | `tests/test_controller.py` stays a file that **no repair seat** may write. The sentence gains: "except the lead's one commit under S1-REGRESSION-01-A2". |
| Addendum check 9 (path fence) | The set of 50 becomes a set of **51**: add `tests/test_controller.py`. The three-dot form for the whole of S1 is unchanged, because that path is already among the 27 (addendum A13). |
| Check 1 (assertion census) | `tests/test_controller.py` joins the files walked. Its R-list has **one** entry, `tests.test_controller.SuiteControllerTests.test_mock_experiment_refuses_at_aggregation` (literal `1` becomes `2`; the label assertion is added; the call under `assertRaises` changes). The two added tests are new test IDs. The restored neighbour must show zero difference against main. Every other test of the file must show zero difference against `c7593edb`. |
| Check 2 (banned patterns) | Unchanged. For the record: the replacement contains no banned pattern (E14); it removes one patch of `aggregate_experiment`; its one new patch replaces `joulewise.controller.run_benchmark` by a wrapper around the real function in order to pass the production parameter `battery_runner`. The pair in the charging test is written by the controller, on a config that names `wall_meter`, so check 2 (k) and the mock-pair count of check 2 (l) are not touched. |
| Check 5 (planted defects) | Add the row "controller aggregate: D1 to D4 of S1-REGRESSION-01-A2 §5.3". |
| Ruling step 2 (lead, bench) | Before merging P and H, the lead lands the commit of §4 and runs acceptance (i) to (iv). |
| G-5, pull-request description | Add one sentence: "A mock experiment's manifest carries an aggregate block with every member marked `not_applicable`; the same aggregate called without the keyword, as the figures script calls it, refuses." |

Check 3 (the production diff) is unchanged: this ruling adds no production path. Check 7 (a)'s phrase "their files are untouched" names the fence files (`tests/test_bundle_read.py` and the tripwire), not `tests/test_controller.py`.

## 7. One finding outside the charge, returned to the lead

**Two tests in `tests/test_controller.py` start the real battery probe.** `HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` (`:1812`) and `HappyPathTests.test_powermetrics_thermal_coverage_is_continuous_across_admission_handoff` (`:2033`) failed under my guard on `c7593edb` and on `db4eadf6` alike, with 8 blocked `ioreg` attempts logged (E9). Without a guard they read the battery of the laptop that runs them, and pass only if it happens to be at float.

- This is **not** caused by seat P and does not bear on rulings 1 to 3.
- It bears on the ruling's check 6 (hermeticity), which requires every module that reaches the controller's reduce stage to stay green with the real probe replaced by a function that raises. These two tests will be red under that check, and the file is granted to no seat.
- **I do not grant their repair here.** I did not read the two tests' bodies or execute a repair, and a grant without executed text would be the kind of inference the ruling's §6 forbids. The likely repair is evidence-forward (inject a runner that returns the float fixture; assertions byte-identical), but that is a statement of expectation, not a ruling.
- The lead confirms the finding at step 2 with check 6 and brings the two test IDs to an addendum. Until then, anyone running `tests.test_controller` whole does so under a guard.

## 8. Corrections to the charge's facts

1. The charge says the file "is in no seat's scope". True, and stronger: the addendum's §6 names it among files no repair seat may write. This ruling keeps that and gives the edit to the lead.
2. The charge offers "a mixed window still refusing" as the example of where refusal coverage moves. A mixed window cannot be built through `run_experiment`, because every repetition shares one config, and the keyword may not appear in this file (addendum check 2, last item). Mixed windows stay covered at the gate by seat P's T12a-1, T12a-2 and T12a-10. At the controller, the refusal is covered by the two forms of §4: the strict call form on a mock experiment, and a charging real experiment.
3. Seat P's report gives `head_end` as `c7593edb`; the landing was committed afterwards as `db4eadf6` (E1). No conflict, recorded for the reader.

## 9. Plain summary

1. Seat P built exactly what was ruled: a synthetic experiment's summary block now goes through with every run marked "not applicable", and everything a paper number can come from still refuses; the one failing controller test was written for the older, stricter behaviour and is out of date.
2. The controller test file is opened for one class only, with exact text that I ran: the old refusal check is kept under the same name against the strict call the figures script uses, a new check shows the synthetic experiment's summary, another shows that a real experiment measured while the battery was charging is still refused, and one neighbouring test returns to the main branch's wording; the lead applies it as a single commit and no production code changes.
3. Separately, two other tests in that file read the real laptop battery when run; that is not seat P's doing, it will trip the planned isolation check, and it needs its own short ruling before anyone repairs it.
