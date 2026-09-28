RULING: S1-REPAIR-ROUTE-01 ISSUED

# Cold gate S1-REPAIR-ROUTE-01 — how the S1 repair closes after two same-signature rounds

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one session, no subagents. Session 2026-09-27 23:44 to 2026-09-28 00:14 PDT by the host clock (30 minutes of the 60-minute budget). Python was `/opt/homebrew/bin/python3 -B`. Scratch is under `/tmp/cg-s1route-d528efb2/`. No file in any repository was modified; this file is the only repository file written. At the end of the session `git status --short` printed nothing on the candidate worktree (head still `5283d7d0`) and on my own worktree, and no process of mine was running.

**Verdict in one paragraph.** The repair continues on S1's branch for one last round, by a different route. Opus's diagnosis is right and I re-executed it: the remaining failures are one cause, not a hundred. A test bundle that is made to look real enough to carry battery evidence is, from that moment, held to every other check a real bundle owes, and the old test bundles skipped those checks through a fixture exemption that lives in production code. The route is **exemption parity**: the battery gate and the bundle's identity are always real, and the other checks are switched off only through one declared test-only switch, only for tests that are about something else. The gate property Opus reports is real (executed, five variants), it is a fault in S1's gate, and S1 fixes it before merge with the exact text in §4, which I executed. S1 is neither split nor abandoned.

## 0. Contamination disclosure and deviations

**Loaded by the harness without my choosing, before my first turn:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md` of the worktree I was started in, the memory index `MEMORY.md` (one-line pointers, several naming loop context such as checkpoints, directives and model assignments), a list of skills and agent types, the git status and five commit subjects. I used none of it for any ruling below. One exception is stated openly: the global file's writing standard (define each term at first use) matches what I would do anyway, and this text follows it.

**Not opened by me:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file, the decision log, the activation record, addenda A1 and A2.

**Read by me:** both charges; the three seats in full; the ruling S1-REGRESSION-01 and its addendum A3 in full; the findings sections of the round-2 reports of seats A and B; the guard's source; Opus's five probe scripts in full; the code named under Executed evidence. I read the three seats **before** forming my view, so my view is not blind to theirs. Every seat claim I rely on is marked as re-executed by me, confirmed by my reading, or taken from the seat.

**Deviation 1: one command ran in the background for about two minutes.** The protocol forbids background tasks. My run of ten test modules exceeded the harness's 600-second limit and the harness moved it to the background on its own. I killed it by PID (Python `65079`, its shell `65075`) and used none of its output. Every result below comes from later foreground runs.

**Deviation 2: my scratch tree is not a git repository.** It is a `git archive` export of `5283d7d0` limited to `joulewise scripts tests configs docs/contracts pyproject.toml`. Some tests need git and fail there for that reason alone. I therefore never report a module as green or red in absolute terms; I report only the **difference** between the export and a copy of it carrying my trial edit.

**Deviation 3: two of my probes are Opus's scripts.** I re-ran `probe3.py` and `probe5.py`, read in full first, with the import path changed to my own export. They are the seat's design, executed by me.

**The laptop battery was never read.** Every Python command ran with the guard on `PYTHONPATH`. The guard's log held 61 lines before my first run and 61 after my last; I only counted its lines and never wrote to it.

## 1. Terms used in this ruling

Terms defined in the ruling's §1 and in A3's §1 keep their meaning. The ones this text leans on, restated so it can be read alone, and the new ones:

- **S1.** The pull request that makes every reader of a measurement bundle check the bundle's battery evidence first. **Candidate:** the branch `fix/2026-09-27-s1-regress` at `5283d7d0`, which is S1 plus every repair so far.
- **Bundle.** One run's directory: `config.json`, `metadata.json`, `events.jsonl`, the power trace, the summary, raw telemetry under `raw/`.
- **Battery pair.** Two recorded readings of the laptop battery, before and after the measured span, each with the raw `ioreg` bytes and their digest.
- **The gate.** The function `authenticate_window_members` in `joulewise/bundle_read.py` and the per-bundle check `BundleReader._battery_verdict` it rests on. It answers with one status per bundle: `pass`, `battery_float_confounded` (charging), `battery_float_evidence_missing` (no usable pair), `unobserved_historical` (bytes on a closed list of 69 old bundles), `not_applicable` (mock; refused on every claim path).
- **Claim path.** Any code path whose output a paper number can be taken from.
- **Bound config.** A `config.json` whose SHA-256 equals `metadata.config_sha256`. **Mock config:** a bound config that names the synthetic `mock` telemetry backend. **Physical config:** a bound config that names any other backend.
- **Exempt bundle.** A bundle for which production code computes `production_predicate_exempt = True` (`joulewise/whole_window.py:995-999`). That happens exactly when the config is not bound, or is a mock config. The code's own comment calls this "fixture/non-production evidence".
- **Exemption-gated check.** A production check that first asks whether the bundle is exempt and, if so, reports nothing. There are five such places, in four functions (§3.3).
- **The coupling.** To carry a pair, a test bundle must get a physical config. Getting a physical config ends its exemption. So the act of adding battery evidence switches on every exemption-gated check the bundle used to skip.
- **Exemption parity** (short: **parity**). A test-only switch that makes every bundle count as exempt for the duration of one named test, and changes nothing else. "Parity" because the test then sees exactly the checks it saw on main.
- **Strict validation.** `validate_bundle(path, strict=True)` in `joulewise/cli.py`; an empty list means valid. It re-derives the power trace from raw telemetry.
- **Mock barrier.** Three inline statements that add the reason `mock_telemetry_claim_ineligible` when a bundle has a mock config (`joulewise/analysis_engine/inputs.py:1943-1944`, `:2889-2890`; `joulewise/floor_extraction.py:2028-2029`). It is a second refusal of mock bundles, behind the gate.
- **Helper H.** The test file `tests/bfgs_fixtures.py`. `rebind_config` gives a bundle a physical config with agreeing backend labels; `write_passing_pair` writes a pair from committed real `ioreg` bytes; `produce_strict_bundle` (**the builder**) runs the production controller on replayed telemetry.
- **Evidence-forward repair.** The fixture gets what the gate demands; the test's assertions stay byte-identical. **R-list:** the list, by test ID, of every test whose assertion changes, each approved.
- **Planted defect.** A deliberate fault put into a scratch copy of the code to prove a test turns RED when it should.
- **Seat.** One delegated model session with an exhaustive list of files it may write. **Lead:** the session that runs the loop and works "at the bench", that is, directly.

## 2. Executed evidence (this session, all in the foreground unless marked)

`tree` = my export of `5283d7d0`; `patched` = a copy of `tree` with the text of §4.2 applied. Both under `/tmp/cg-s1route-d528efb2/`.

| # | Probe | Result |
|---|---|---|
| Y1 | `shasum -a 256` of the three seat files; `git rev-parse HEAD` and `git status --short` on the candidate, at start and end | Sol `b36ff016…`, Astra `3f365007…`, Opus `a3ca1e07…`, as charged. Candidate `5283d7d01353…`, clean both times. |
| Y2 | My script `gp1.py`: one bundle from the builder, copied six times; five copies altered; each given to the gate, to `BundleReader.metadata()`, to `custody_telemetry_identity` and to strict validation | **Untouched:** gate `pass`, not exempt, strict `[]`. **Config deleted:** gate `pass`, exempt. **Config rebound to mock, pair kept:** gate `pass`, exempt, mock. **One byte appended to the config:** gate `pass`, exempt. **Config changed to mock, digest not updated:** gate `pass`, exempt. **Config replaced by `not json`:** gate `pass`, exempt. In all five, `BundleReader.metadata()` also answers `pass`. Strict validation reports problems in all five. |
| Y3 | Read `joulewise/bundle_read.py:466-507` and `joulewise/battery_float.py:1026-1068` | When metadata holds a pair, `_battery_verdict` returns `authenticate_bundle(path)` at once (`:483-487`). `authenticate_bundle` reads `metadata.json`, `events.jsonl` and the raw battery files. **It never opens `config.json`.** The config is read only on the branch for bundles with no pair (`:488-507`). |
| Y4 | Read `joulewise/controller.py:2115-2131` | The production controller writes the mock marker `{"pre": null, "post": null, "not_applicable": "mock"}` whenever the backend is mock, and a pair otherwise. **No production writer produces a pair under a mock config or a bundle without `config.json`.** |
| Y5 | `grep` over six consumers for the gate, strict validation, the identity function and the mock barrier | `joulewise/aggregate.py` and `scripts/extract_detection_floors.py` call the gate and **nothing else of these**. This agrees with the ruling's E10. |
| Y6 | `grep -rn production_predicate_exempt joulewise scripts tests` | One definition (`whole_window.py:996`) and five uses: `analysis_engine/inputs.py:205`, `floor_extraction.py:1903`, `scripts/run_campaign.py:4559`, `:6615`, `:6623`. **No use under `tests/`.** Enclosing functions in §3.3 (found by the nearest preceding `def`, not by syntax tree). |
| Y7 | Opus's `probe3.py` on `tree`: the scenario of `test_full_coverage_has_no_membership_refusal`, main's hand-built members, three ways | **No config (main's shape):** gate refuses, `battery_float_evidence_missing`. **Rebound and paired:** gate `pass` for all three; all three excluded with exactly `anchor_fallback_member_unusable` and `environment_admission_missing`. **Rebound and paired, exemption forced true:** gate `pass`; `all_cells_extractable True`; no member excluded; no reason. |
| Y8 | Opus's `probe5.py` on `tree`: the two neg8-derivation tests with `write_passing_pair` added to their members | `Ran 2 tests in 0.522s`, `OK`. |
| Y9 | The text of §4.2 applied to `patched`; `gp1.py` repeated there | Untouched bundle: `pass`. **All five altered bundles: `WindowBatteryRefusal`, status `battery_float_evidence_missing`**, with the reasons of the table in §4.2. `BundleReader.metadata()` raises `BatteryStatusRefusal` for all five. File digests in §4.2. |
| Y10 | Seven test modules run on `tree` and on `patched`; the sets of failing test names compared | `tests.test_bfgs_fixtures` (15 tests): green on `patched`. `tests.test_bundle_read` (118), `tests.test_battery_float_consumers` (21), `tests.test_aggregate` (29), `tests.test_bfgs_publication_privacy` (1): **same set on both**. `tests.test_bfgs_window_consumers` (41): **three tests fail on `patched` only** (§4.3). `tests.test_scored_reduce`: killed by my 120-second alarm on both; no result. |
| Y11 | Read `tests/test_bfgs_window_consumers.py:31-37` and `:404-409` | S1's own fixture `pair_bundle` builds its bundle from `configs/examples/mock_local.json` and changes the backend only when called with `real=True`. `test_passing_pair_returns_verdict` calls it without. **S1's own test of the status `pass` runs on a mock config.** |
| Y12 | Read `joulewise/analysis_engine/inputs.py:1936-1946`, `:2884-2892` | The mock barrier is inline in both places; there is no function to call. |

**NOT EXECUTED by me:** any full suite or whole-suite count; the exact number of remaining outcomes (I use the seats' figures: 64 integration outcomes in 29 test IDs, 7 campaign IDs, 25 floor outcomes); parity on any test of the integration or campaign modules; parity on the golden report; the sibling test of §5.3; the parity helper as a context manager (I executed the patch it wraps, Y7, not the helper); tests G-5 and G-6 of §4.4; the repair of the three tests of §4.3; four battery modules under the trial fix (`test_battery_float`, `test_battery_float_sweep`, `test_bfgs_consumer_sweep`, `test_bfgs_calibration_bracketing`) and everything outside the seven modules of Y10; the census of direct tests in §3.4 rule 5; the builder extension of §5.2 class T5.

## 3. Ruling 1 — the route

### 3.1 The diagnosis: Opus's coupling, confirmed

Sol and Astra describe what each later check needs, correctly and from reading. Opus explains why those checks appeared at all, and proves it by execution. I re-executed the proof (Y7) and the discriminator (Y8).

**Worked example (Y7).** Three hand-built floor members, each with summary value 40.0, as on main.

1. As on main, with no `config.json`: the members are exempt. On main the extractor admitted them. On the candidate the gate refuses them: no pair.
2. Given a physical config and a pair: the gate answers `pass`, three times. The members are no longer exempt. The extractor now runs two checks it skipped before and excludes all three, for `anchor_fallback_member_unusable` and `environment_admission_missing`.
3. The same bundles as in 2, with the exemption switched back on: the gate still answers `pass`; all three are admitted; the values are unchanged.

So the battery gate is satisfied in step 2, and everything that still fails in step 2 is a check that main never ran on these fixtures. That is the whole of the "same signature".

**The discriminator (Y8).** A test whose bundles were *not* exempt on main already met those checks on main. Such a test needs the pair and nothing else. Two of seat A's seven campaign IDs are of this kind and are green with a pair alone.

### 3.2 The seats' routes, judged

| Route | Soundness | Risk of a third same-signature round | Ruling |
|---|---|---|---|
| (a) the builder produces claim-ready bundles end to end | Highest: every check runs for real | **High.** Executed probes (Opus probe1; seat B's trial) show at least three layers nobody has built: environment admission on a real clock (about 11 s per bundle), sampler timing that satisfies the cadence and clock checks, and campaign-level idle admission. Each layer is a discovery round. Hand-set summary values cannot survive, so numeric assertions move as well. | **Not the route.** Kept as a lane (§9), and as one bounded task for class T5 (§5.2). |
| (b) a committed corpus, generated once | As (a); the corpus must first be generated, so it inherits (a)'s risk | High until (a) has succeeded once | **Not the route.** |
| (c) re-scope: assert the refusal, move the subject to a sibling | Sound where the test's subject is the refusal | Moderate: inner logic is inline (Y12) | **Adopted for one class only** (T3, tests whose subject is the refusal of mock bundles), as already ruled in the ruling's §3.4. |
| (d) split S1 | **Leaves claim paths un-gated** | — | **Refused** (§7). |
| (e) exemption parity | See §3.3 | **Low.** The switch restores main's checks by construction. A refusal that survives it has, by definition, a different cause. | **The route.** |
| (e′) pairs on bundles without a config | **Unsound.** No real window lacks `config.json`; and the gate fix of §4 refuses such bundles. | — | **Refused.** |

Sol's and Astra's central advice, "prove one complete case before migrating many", is adopted as the pilot of §5.3.

### 3.3 Is parity sound under directive #421? Stated plainly

The charge's test has two halves.

**"No claim path may be left un-gated."** Parity changes no production file. Every claim path keeps its gate call and every check it has today, and gains the fix of §4. **This half is met.**

**"No route may let a test pass on evidence a real window could not produce."** Read to the letter, **parity does not meet this half**: under parity, claim-path code admits a fixture that has no environment admission, and a real window without environment admission would be refused. I say so openly, and I rule that the letter is the wrong reading, for three reasons.

1. **The letter is met by nothing that exists.** Main's suite does not meet it (its fixtures were exempt, which is the same switch, thrown inside production code). Helper H's pairs on hand-built bundles, ruled in the ruling's §3.4, do not meet it. Only routes (a) and (b) would, and they are the routes with the high risk of a third round.
2. **What #421 protects is the truth of numbers.** No number leaves a test. The harm a test can do is false assurance: a green test that seems to say "this check works" while the check is off. Rules 1 to 6 below are aimed at exactly that harm.
3. **Parity makes production stricter than it is on main.** Today the exemption is reachable in production by any bundle whose config is unbound. With the fix of §4, a bundle on a claim path that answers `pass` has a physical config, so it is never exempt. The fixture exemption stops being something a claim bundle can reach through the status `pass`, and the switch moves to where test switches belong: test code.

**This reading is mine to rule and the owner's to overturn.** If the owner holds that #421 binds test fixtures to the letter, the route is (a) then (b), my estimate is four to six seat-rounds, and S1 stays on HOLD meanwhile.

**The closed list: what parity switches off.** Exactly the five uses of `production_predicate_exempt` (Y6), in four functions:

| File | Function | Line at `5283d7d0` | What the exemption skips there |
|---|---|---|---|
| `joulewise/analysis_engine/inputs.py` | `anchor_fallback_member_unusable` | 205 | whether a member without a resolved clock anchor is usable |
| `joulewise/floor_extraction.py` | `_cpu_admission_bundle_reasons` | 1903 | environment and CPU admission of a floor member |
| `scripts/run_campaign.py` | `_current_member_environment_refusals` | 4559 | environment admission of a campaign member |
| `scripts/run_campaign.py` | `_member_readiness_reasons` | 6615, 6623 | the reason `reducer_wire_unknown`; the post-run environment check |

**The mechanism: one switch, not four stand-ins.** Opus proposes replacing the functions by stand-ins. I rule the single switch Opus used in its own probe, for two reasons. `_member_readiness_reasons` computes many reasons and consults the exemption inline; replacing the whole function would switch off more than main skipped. And one switch is equal to main's behaviour at every place by construction, so no stand-in can drift from the function it replaces.

**Ruled text, added to `tests/bfgs_fixtures.py`** (with `import contextlib` and `from joulewise import whole_window` among its imports):

```python
# Closed list: the only places where exemption parity changes behaviour.
PARITY_SWITCHED_OFF = (
    ("joulewise/analysis_engine/inputs.py", "anchor_fallback_member_unusable"),
    ("joulewise/floor_extraction.py", "_cpu_admission_bundle_reasons"),
    ("scripts/run_campaign.py", "_current_member_environment_refusals"),
    ("scripts/run_campaign.py", "_member_readiness_reasons"),
)

# Closed list of test IDs granted parity.  Written by the lead from the
# triage record; a seat never adds to it.
PARITY_TEST_IDS: frozenset[str] = frozenset({
})


@contextlib.contextmanager
def exemption_parity(test_id: str):
    """For one named test, treat every bundle as exempt, as main treated it.

    The battery gate, the bundle's config binding, the mock barrier and
    strict validation are untouched: none of them reads the exemption.
    """
    if test_id not in PARITY_TEST_IDS:
        raise AssertionError(f"exemption parity not granted to {test_id}")
    with patch.object(
        whole_window.CustodyTelemetryIdentity,
        "production_predicate_exempt",
        property(lambda self: True),
    ):
        yield
```

A test uses it as `with exemption_parity(self.id()):` around its body.

**The rules.**

1. **Battery code is never stubbed.** Parity touches one property. Every name banned by the ruling's check 2 stays banned. In a parity test the gate runs for real on every bundle.
2. **The bundle's identity is always real.** Every bundle a parity test sends down a claim path has a physical config, agreeing backend labels, and a pair written by the controller or by helper H. After §4 the gate enforces the first of these itself.
3. **Never the test's own subject.** Parity is refused to a test whose subject is an exemption-gated check. The test is mechanical, run by the lead: a test is refused parity if its own source, or the source of a fixture method of its class that it calls, contains a string literal from the **refusal vocabulary**, or calls one of the four functions by name. The refusal vocabulary is every string the four functions can return on their non-exempt branch, including what `environment_admission_refusals` and `post_run_environment_refusals` return. The lead derives it from the syntax trees and files it with the triage record. Members I have seen: `anchor_fallback_member_unusable`, `environment_admission_missing`, `environment_admission_failed`, `reducer_wire_unknown`.
4. **By test ID only.** No class-wide, module-wide or `setUp`-level use. The helper raises for an ID not on the list.
5. **Every switched-off check keeps a test that runs it switched on.** Before parity lands, the lead lists, for each of the five places, at least one green test on the candidate that reaches its non-exempt branch and asserts its refusal. If a place has none, a direct test is owed first, written by seat H3.
6. **No production file changes for parity.** If parity seems to need one, the seat returns `NEEDS_RULING`.

**The sweep test that pins the list.** In `tests/test_bfgs_consumer_sweep.py`, test `test_exemption_parity_closed_list`: it walks the syntax trees of every tracked `*.py` under `joulewise/` and `scripts/`, collects the (file, enclosing function) of every attribute access named `production_predicate_exempt`, removes the definition itself (`joulewise/whole_window.py`, `CustodyTelemetryIdentity.production_predicate_exempt`), and asserts that the set **equals** `set(PARITY_SWITCHED_OFF)`. A second assertion, over `tests/`: the name `production_predicate_exempt` appears in `tests/bfgs_fixtures.py` and in that file's own test module, and in no other test file. If the syntax tree gives an enclosing name that differs from my table (Y6 used the nearest `def`), seat H3 reports it and the lead corrects the name; the five places must not change.

**Helper H's own tests, each with the planted defect that must turn it RED:**

| Id | Input | Must observe | Planted defect |
|---|---|---|---|
| H-15 | the scenario of Y7, step 3, under `exemption_parity` with a granted ID | gate `pass` for every member; all admitted; the summary values unchanged | the `patch.object` removed (the members are then excluded) |
| H-16 | `exemption_parity("tests.not_granted.X.test_y")` | `AssertionError` before the body runs | the ID check removed |
| H-17 | under parity, a member with the charging pair | refusal, `battery_float_confounded` | none; pins that parity does not reach the gate |
| H-18 | under parity, a member whose config is unbound (one byte appended) | refusal, `battery_float_evidence_missing` (needs §4) | the fix of §4 reverted in a scratch copy |
| sweep | the sweep test above | equal to the closed list | self-test: a sixth use added in a scratch copy of `joulewise/aggregate.py` is reported |

## 4. Ruling 2 — the gate property

### 4.1 It is real, and it is a fault in S1's gate

**Executed (Y2), five variants, all `pass`.** The cause is one line of control flow (Y3): when metadata holds a pair, the gate authenticates the pair and returns, and never looks at the config. The config decides the status only for bundles with no pair.

**Why it is a fault and not a curiosity.**

1. **It contradicts S1's own rule.** S1 refuses mock bundles on every claim path. A mock-config bundle that carries a pair answers `pass`. The ruling's test T12a-6 pins the mirror case (a physical config carrying the mock marker is refused); this case was never tested, and S1's own test of `pass` runs on a mock config (Y11), so the suite could not see it.
2. **In two consumers nothing stands behind the gate.** The experiment aggregate, which the figures script calls, and the floor extractor script call the gate and neither strict validation nor the mock barrier (Y5; the ruling's E10 lists more).
3. **Whether the telemetry was synthetic bears on whether a number is true.** Under #421 that makes the check mandatory.
4. **Parity rests on it.** Rule 2 of §3.3 says every fixture that passes the gate has a physical config. Without the fix that is a promise kept by reviewers; with it, production code keeps it.

**How severe.** No production writer produces such a bundle (Y4). It takes an edit, a loss or a corruption of `config.json` after the run. S1 is not merged, so no measured number has passed through this. It is a fail-open path for damaged or edited bundles. **It is fixed in S1 before merge. It does not go to a lane.**

### 4.2 Ruled text, exact, executed (Y9)

File `joulewise/bundle_read.py`. Base SHA-256 `623821106148e38692e3e1c5c3f786e709ccca315662daa80bc73ce3e737ea0c`; result `c4039f224de5d6df39cddb306c8fff9d3e217e8cd722e1bcd460595a975ad519`. The unified diff is kept at `/tmp/cg-s1route-d528efb2/gate-fix.diff` (SHA-256 `3061bcc64b1fd0e2514dde37122040e4c5505cb644fe56784d85237abe5a5b25`); the lead copies it into the trace directory.

Hunks 1 and 2: in `_battery_verdict`, both statements `return battery_float.authenticate_bundle(self._path)` (`:482` and `:487`) become:

```python
            return self._pair_verdict_under_bound_config(
                raw, battery_float.authenticate_bundle(self._path))
```

Hunk 3: a new method, inserted directly before `def _digest_bound_mock_config`:

```python
    def _pair_verdict_under_bound_config(
        self, metadata: dict[str, Any], verdict: battery_float.PairVerdict,
    ) -> battery_float.PairVerdict:
        # A pair is battery evidence only for the run its config describes:
        # ``pass`` requires config.json bytes that hash to
        # metadata.config_sha256 and name a physical telemetry backend.
        if verdict.status != "pass":
            return verdict
        mock, detail = self._digest_bound_mock_config(metadata)
        if mock:
            reason = "pair recorded under a mock config"
        elif detail:
            reason = f"pair not bound ({detail})"
        else:
            return verdict
        raise BatteryStatusRefusal(
            "battery_float_evidence_missing", (reason,), verdict.bundle_sha256)
```

**Why each choice.**

- **The pair is authenticated first, the config second.** A tampered raw battery file still raises `CustodyFailure`, exactly as today. The fix can only turn a `pass` into a refusal.
- **Only `pass` is touched.** A charging pair stays `battery_float_confounded` whatever the config. The fix hides no other status.
- **A pair under a mock config is `battery_float_evidence_missing`, not `not_applicable`.** The controller never writes that combination (Y4), so the record contradicts itself. As `not_applicable` it could enter one of the two flows that admit an all-mock window (text 12a); as missing evidence it is refused everywhere.
- **It reuses `_digest_bound_mock_config`,** the function that already decides the mock status, so "bound" and "mock" mean the same on both branches.

**What the text does, executed (Y9):**

| Bundle | Before | After |
|---|---|---|
| untouched | `pass` | `pass` |
| config deleted | `pass` | refused: `pair not bound (config.json cannot be read: …)` |
| config rebound to mock, pair kept | `pass` | refused: `pair recorded under a mock config` |
| one byte appended to the config | `pass` | refused: `pair not bound (config.json digest does not match metadata.config_sha256)` |
| config changed to mock, digest not updated | `pass` | refused: same reason as the row above |
| config replaced by `not json` | `pass` | refused: same reason |

### 4.3 What the fix costs: measured in part

In seven modules (Y10) the fix turns **three** tests, all in `tests.test_bfgs_window_consumers`, class `WindowMembersTests`: `test_passing_pair_returns_verdict`, `test_recorded_member_digests_precede_status_refusals`, `test_aggregate_authenticates_failed_member_before_numbers`. All three build their passing bundle on a mock config (Y11). They are repaired evidence-forward: the bundle that is meant to pass is built with `real=True`. Assertions stay byte-identical. If `real=True` does not yield a bound config, the fixture binds it; NOT EXECUTED by me.

**The rest of the suite is not measured.** The repairs of rounds 1 and 2 used helper H, whose `rebind_config` refuses a mock backend, so I expect few further turns; that is inference. Step R3-1 (§5.4) measures it before any seat starts.

### 4.4 Tests owed with the fix

In `tests/test_bfgs_window_consumers.py`. Bundles come from `produce_strict_bundle`.

| Id | Input | Must observe | Planted defect that must turn it RED |
|---|---|---|---|
| G-1 | an untouched produced bundle | gate `pass`; `BundleReader.metadata()` returns | the new method made to raise always |
| G-2 | `config.json` deleted | `WindowBatteryRefusal`, status `battery_float_evidence_missing`, reason begins `pair not bound (config.json cannot be read` | hunk 2 reverted |
| G-3 | config rebound to mock, pair kept; once with the default, once with `admit_mock_window=True` | refused both times, reason `pair recorded under a mock config` | the `if mock:` branch removed |
| G-4 | one byte appended to the config | refused, reason `pair not bound (config.json digest does not match metadata.config_sha256)` | the `elif detail:` branch removed |
| G-5 | the charging pair, config deleted | status `battery_float_confounded` | the first `if` of the method removed |
| G-6 | one raw battery byte flipped, config deleted | `CustodyFailure` | the config check moved before `authenticate_bundle` |
| G-7 | the bundles of G-2, G-3, G-4 given to `BundleReader(path).metadata()` | `BatteryStatusRefusal` each time | hunk 2 reverted |

G-1 to G-4 and G-7 state what I executed. G-5 and G-6 follow from my reading of the text and are NOT EXECUTED.

## 5. Ruling 3 — triage, seats, order, stop conditions

### 5.1 Who classifies, and how

**The lead classifies, at the bench, by script. Seats do not classify.** For each failing test ID of the round-3 inventory (step R3-1), the lead runs the test **on main's tree** with a recorder wrapped around `custody_telemetry_identity` that returns the real result unchanged and logs, per bundle path, whether the bundle was exempt. The recorder runs on main only, never on the candidate, and never inside a committed test, so check 2 is not touched. The output is one table, filed in the trace directory, with one row per test ID: class, the bundles seen, exempt or not, whether the test replaced the strict validator on main, and the result of rule 3 of §3.3.

### 5.2 The classes

| Class | Mark on main | Repair | Assertions |
|---|---|---|---|
| **T1** | no bundle the test read was exempt | the pair alone (`write_passing_pair`) | byte-identical |
| **T2** | every bundle was exempt, and the test replaced the strict validator itself or never reached it | main's fixture, then `rebind_config`, then `write_passing_pair`, then `exemption_parity`. **Not the builder:** produced bundles carry their own honest refusals (seat B's trial: cadence, clock bound) and cannot hold hand-set values. | byte-identical |
| **T3** | the test's subject is the refusal of mock bundles on a claim path | the ruling's §3.4, second form, on a mock corpus the test builds for itself; sibling per §5.3 | R-list |
| **T4** | the gate refuses a floor root that holds no bundle (14 of seat A's integration IDs) | first build the member bundles under each floor root in main's fixture form, rebound and paired; then derive the floor records from them; then as T1 or T2 | byte-identical; pins move only under A3's leaf-diff rule |
| **T5** | every bundle was exempt, and the test ran the **real** strict validator on main (the mock corpus of the integration module) | the round-2 corpus from the builder stays, and parity is added. If a refusal remains that is recorded in the produced bundle's own summary, seat H3 has **one** bounded task: `produce_strict_bundle` gains a keyword, default unchanged, that replays enough samples at the configured rate for the reducer's own cadence and clock checks to pass. No check is touched and no summary is edited. | byte-identical where the assertion does not name a number that came from mock telemetry; otherwise `NEEDS_RULING` |
| **T6** | rule 3 of §3.3 refuses parity (the subject is an exemption-gated check), or some bundles were exempt and others not | none under this ruling: `NEEDS_RULING`, counted under the cap | — |

**Where the remaining risk sits.** T1, T2 and T4 rest on executed evidence (Y7, Y8). **T5 does not**: nobody has shown that a produced bundle can pass the reducer's cadence and clock checks. By seat A's table T5 is at most about 13 integration IDs and one campaign ID. It is bounded by the pilot and by stop condition 3.

**The golden report** (A3 §5.5 item 3) is class T2: the five golden members are rebound and paired, the extractor runs under parity, and the report is regenerated under A3's leaf-diff rule, which stands unchanged. The test that compares the golden gets parity by ID. NOT EXECUTED for the golden itself.

### 5.3 The sibling for the mock barrier (seat A's F3)

A3 told seat A to call "the barrier's own function". There is none (Y12). After §4, a mock bundle cannot pass the gate on any claim path, so the barrier cannot be reached through a public entry with an honest mock bundle.

**Ruled.** The sibling builds a bundle that passes the gate (physical config, pair), and replaces `custody_telemetry_identity` **in the consumer's module** by a function that returns the real identity with `config_backend_class` set to `"mock"`. It asserts that the reason `mock_telemetry_claim_ineligible` appears. This is the **one permitted exception** to check 2's ban on new patches of `custody_telemetry_identity`. It is granted by test ID, and only in this direction: the stand-in makes a real bundle look mock and can only add a refusal. Planted defect: the barrier's two lines removed in a scratch copy turn the sibling RED. One sibling per barrier site (three sites). NOT EXECUTED by me. If it cannot be built without a production edit, the seat returns; the lead then retires the sibling for that site and records the reason ("after the gate fix the gate carries the mock refusal; the barrier stays in place, unchanged, as a second line").

### 5.4 Order, seats and scopes

Every seat works in its own linked worktree. Scopes are exhaustive.

| Step | Who | What | Output, and the gate to the next step |
|---|---|---|---|
| R3-0 | lead, bench | The three hunks of §4.2 as one commit on the candidate | The result digest of §4.2; the six rows of §4.2 reproduce |
| R3-1 | lead | The full suite on that head merged with main's head, in the integration tree | **The round-3 inventory**: every failing outcome by test ID. It replaces "about 100". It also measures what the gate fix turned. Stop condition 5. |
| R3-2 | lead, bench | The triage of §5.1; the refusal vocabulary; the census of rule 5 | The triage table; the contents of `PARITY_TEST_IDS` |
| R3-3 | lead, bench, in scratch, nothing committed | **The pilot:** one test of each of T2, T4 and T5 repaired by its class rule | Each green, with the planted defect "charging pair" turning it RED. Stop condition 6. |
| R3-4 | seat **H3** | `exemption_parity`, the two lists, H-15 to H-18, the sweep test, G-1 to G-7, the three tests of §4.3, any direct test owed under rule 5, and the T5 keyword if the pilot needed it. WRITE_SCOPE: `tests/bfgs_fixtures.py`, `tests/test_bfgs_fixtures.py`, `tests/test_bfgs_consumer_sweep.py`, `tests/test_bfgs_window_consumers.py`. | One commit; the lead runs every planted defect. The lead, not the seat, fills `PARITY_TEST_IDS`. |
| R3-5 | seats **A** and **B**, in parallel | A: the integration and campaign IDs by class, and the siblings of §5.3 for `inputs.py`. WRITE_SCOPE: `tests/test_analysis_integration.py`, `tests/test_run_campaign.py`, `tests/test_pipeline_smoke_tail.py`. B: the floor outcomes by class, the golden report, and the sibling for `floor_extraction.py`. WRITE_SCOPE: `tests/test_floor_extraction.py`, `tests/fixtures/d117_postcollection_trust/extraction_report.json`. | Reports: per test ID the class applied and the result; the R-list; every `NEEDS_RULING` with the test ID and the refusing check's name |
| R3-6 | lead, bench | The cherry-picks, linear; A3's step R2-4 (the one literal of A3 §5.4); every check of §8 | The step-4 head |
| R3-7 | lead | A3's step R2-5: the repin as the last commit, then the full suite on the head merged with main | Gate G-2 of the ruling |

Any outcome the fix turned in a module outside the scopes above is repaired by the lead at the bench, evidence-forward, in a file the ruling's §6 already grants.

**Every brief carries:** the seat stop rules (i) to (v) already in force; rules 1 to 6 of §3.3; the class table; and this sentence: "A test that still fails after its class rule is returned with its ID and the name of the refusing check. You add no stand-in, you add no ID to the parity list, and you write no admission evidence by hand."

### 5.5 Stop conditions and the hard cap

**Round 3 is the last repair round. The lead starts no round 4 on its own authority.**

Before any seat starts, the lead returns to a cold gate if:

5. the gate fix turned more than **50** test IDs that were green on `5283d7d0` (R3-1): the cost I measured in part was wrong;
6. any pilot fails (R3-3): the class rule does not do what this ruling says.

After R3-6, the lead returns to a cold gate if:

1. any test needs a production check switched off by anything other than `exemption_parity`, or any stand-in that the same test did not already have on main;
2. more than **10** outcomes of the round-3 inventory still fail, the paper supply-map pin outcomes aside;
3. more than **3** test IDs are refused by one and the same check that is neither the gate nor on the closed list;
4. any assertion changed outside the R-list;
7. any production path outside the seven of check 3 is needed.

If none holds, the lead repairs what remains at the bench under the rulings given and proceeds to R3-7.

**What returns to the cold gate:** the residue by test ID, each with its class and the refusing check, and the triage table. That gate rules per ID. It does not reopen the route.

## 6. Ruling 4 — A3: what was wrong, what stands

**Wrong.**

1. **§4.1 named the wrong cause.** It said the suite lacked a shared way to build a real-shaped bundle. The cause is the coupling (§3.1). A builder of single bundles cannot supply campaign or floor evidence, so A3's stop condition 3 was bound to fire. (Opus 1; Sol F2; Astra F2. Confirmed by Y7.)
2. **§4.1 ordered a broad migration on an acceptance that proved too little.** H-8 showed gate `pass` and strict validation `[]`. It did not show that any claim path admits the bundle. My own note there said so, and I commissioned the migration anyway. That was the error.
3. **§5.5 item 3 could not be met as written.** Produced members cannot hold the golden's hand-set values; rebound members without parity are excluded. The leaf-diff rule itself stands; the way to meet it is §5.2.
4. **§5.3 demanded a function that does not exist** (Y12). Replaced by §5.3 above.
5. **"The predicate is not replaced" is amended.** A check may be switched off through `exemption_parity` and through nothing else. The first half of that sentence stands: no admission evidence is written by hand, and no summary flag is edited.
6. **A3 missed the gate property.** Its probes X8 and X12 tested good bundles only.
7. **§8 said the method for 70 to 95 outcomes was "ruled; builder exists and was executed".** The builder was executed; the method was not.

**One seat claim I do not adopt in full.** Opus writes that "not written by hand" draws the wrong line. Half right. The line is now: battery evidence is never faked; the bundle's identity is always a physical config; a test's own subject is never switched off; admission evidence is still never written by hand.

**Stands, unchanged.** The stop conditions of §8, which fired as designed. The current-time runner (§4.2). The validator fix (§5.5, the production text and the seven tests). The rulings on the pins (§5.2, §5.4), on text 10a (§5.6), on the phase-share digest (§5.7), on the spoofed legacy identities (§5.9) and on the controller tests (§5.10). The scope grants. The checks. The builder itself, for tests that need a strictly valid bundle: class T5 and the 17 integration IDs it already turned green.

## 7. Ruling 5 — split or abandon?

**Neither.**

- **Do not split.** Any split lands a main on which some claim consumers check the battery and others do not. That leaves a claim path un-gated, which #421 forbids. Sol and Astra name the one form that would not: disable every unfinished consumer. That trades the repair for lost function and costs a review of its own. Refused.
- **Do not abandon.** Two rounds and this consult found two faults in S1's own code: the validator omission (A3 §5.5), which failed closed, and the gate property (§4), which failed open for edited or damaged bundles. Both are small and both have exact, executed text. Nothing found shows the gate refusing a bundle it should accept. The cost that remains is in the test suite, and it has one cause.
- **Do not merge `5283d7d0`.** HOLD stands until gate G-2 of the ruling is green on a head that carries §4.
- **What would reopen this.** Only an owner decision that #421 binds test fixtures to the letter (§3.3). Then the route changes to (a) and (b); the answer to "split or abandon" does not.

## 8. What changes in the checks

| Check | Change |
|---|---|
| 1, assertion census | No new R-list entry by this ruling except class T3 and the siblings of §5.3. The three tests of §4.3 change fixture arguments only. |
| 2, banned patterns | Added: the name `production_predicate_exempt` anywhere under `tests/` outside helper H and its own test module; `exemption_parity(` in `setUp`, `setUpClass` or at module level. Excepted, by test ID: the siblings of §5.3. |
| 3, production diff | **Unchanged: seven paths.** `joulewise/bundle_read.py` is already among them. |
| 5, planted defects | Rows added: G-1 to G-7; H-15 to H-18; the sweep self-test; the barrier lines removed (§5.3); for one parity test of each of seats A and B chosen by the lead, the passing pair swapped for the charging pair. |
| 9, path fence | Unchanged: every file of §5.4 is already inside it. |
| G-5, pull-request description | Add: "A battery pair yields `pass` only under a `config.json` that is digest-bound and names a physical backend." And: "N tests run claim-path code under exemption parity: the battery gate and the bundle identity are real, and the five exemption-gated checks are off, as they were for the same fixtures on main. No test yet runs the whole claim chain on fully produced evidence; the first real window after merge is the first end-to-end exercise." N is the size of `PARITY_TEST_IDS`. |

## 9. Lanes; none enters this repair

1. **CLAIM-CHAIN-CANARY-01.** One test that runs a fully produced window through the whole claim chain with no switch. Main never had one. It is route (a) for a single window, and the right home for the three unbuilt layers. Not a merge condition: every gap it could find fails closed.
2. **PROD-EXEMPT-RETIRE-01.** After §4, a bundle that answers `pass` is never exempt. Whether an `unobserved_historical` bundle can still be exempt, and whether the exemption should leave production code altogether now that tests carry their own switch, needs its own ruling.
3. A3's three lanes stand.

## 10. Corrections to the charge's and the seats' facts

1. **"≈100 remaining outcomes"** is not a measured figure. The seats report 64 integration outcomes (29 IDs), 7 campaign IDs and 25 floor outcomes; no full suite exists on `5283d7d0`. Step R3-1 produces the count.
2. **Opus names `floor_extraction.py:1903` "environment admission".** The enclosing function is `_cpu_admission_bundle_reasons`; it returns environment admission reasons among others.
3. **Opus's closed list is given "for example" with three names.** There are four functions and five places (Y6).
4. **Opus's option R2 (i)** (a mock bundle carrying a pair reaches the barrier) cannot be used once §4 lands; §5.3 replaces it.
5. **Sol and Astra ran no test**, as both state. Their tables of what each check needs are from reading, and I did not verify them line by line.

## 11. Plain summary

1. The remaining failures have one cause: giving a test bundle battery evidence also makes it answer for every other check a real measurement owes, so the last round keeps the battery check and the bundle's identity fully real and switches the other checks off only through one declared test-only switch, only for tests that are about something else, with the list of affected checks pinned by a test.
2. The battery gate had a real hole, now shown by execution: a bundle carrying battery readings passed even with its configuration file deleted, altered or marked as synthetic; S1 fixes this before merge with about twenty lines that I ran, and three of S1's own tests must be corrected because they relied on the hole.
3. S1 is neither split nor abandoned; one final round runs under a hard cap (the lead first measures the full suite and proves one test of each kind, and returns to a cold gate if more than 10 failures survive), and the owner may overturn my reading that the directive governs what production accepts rather than what test fixtures contain.
