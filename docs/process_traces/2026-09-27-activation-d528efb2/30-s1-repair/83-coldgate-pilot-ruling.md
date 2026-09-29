ADDENDUM: S1-REPAIR-ROUTE-01-A1 ISSUED

# Cold gate S1-REPAIR-ROUTE-01-A1 — why the T5 pilot failed, and how T5 closes

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one session, no subagents. Session 2026-09-28 06:03 to 06:34 PDT by the host clock (31 minutes of the 60-minute budget). Python was `/opt/homebrew/bin/python3 -B`, always with the guard directory on `PYTHONPATH`. Scratch is `/tmp/cg-s1pilot-d528efb2/`. This file is the only repository file I wrote.

**Verdict in one paragraph.** The T5 pilot failed because the ruling in force counted only one of the two ways in which production code treats a test bundle more leniently than a real one. The switch it ruled (exemption parity) turns off the first way. All six refusals in the pilot come through the second way, which sits in a different function and which the switch never touches: I ran the pilot test with the switch and without it and got the same six reasons both times. None of the six bears on what the test is about. The route is to extend the same declared, test-only switch to the second way, by test ID, and to put the two reference bundles back into the hand-written form they had on main, bound and paired. I executed that route: the pilot test turns green, six further T5 test IDs turn green (42 of the 57 T5 outcomes in total), and both planted defects (a charging battery pair, an unbound config) turn the test red at the battery gate. The remaining 15 T5 test IDs are not one class; they are re-classed in §5. Round 3 may proceed now for every other class. The builder is not extended inside S1, and nothing is split out of S1.

## 0. Contamination disclosure and deviations

**Loaded by the harness without my choosing, before my first turn:** the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md` of the worktree I was started in, and the memory index `MEMORY.md` (one-line pointers, several of them naming loop context: checkpoints, directives, model assignments, and a one-line paraphrase of directive #421), plus lists of skills, agent types and tools, the git status and five commit subjects. I used none of it for any ruling below. Two exceptions, stated openly: the global file's writing standard (build each term before first use) is followed in this text; and for directive #421 I used only the wording given in the charge.

**Not opened by me:** `RUN_STATE.md`, `TASK_QUEUE.md`, any `CLAUDE*.md`, `AGENTS.md`, any memory file, any skill file, the decision log, the activation record, the pilot brief (`80-pilot-brief.txt`), any seat brief or seat report other than the pilot report.

**Read by me:** the charge; the ruling in force in full; the pilot report and its diff; both triage files; the guard's source; the code named under Executed evidence.

**Deviation 1: I ran inside the pilot worktree, without editing it.** My probes import the code of `/Users/edr/code/JouleWise-wt-s1-pilot-d528efb2` and change behaviour only in memory, inside the probe's own process. I edited no file there. At the start and at the end its head was `601a06c5`, `git status --short` listed the same four modified files, and the SHA-256 of `git diff` was `61a093e1…4ccb4a` both times, equal to the recorded `81-pilot-scratch.diff`.

**Deviation 2: my runs of many tests are not the suite's runs.** Probes 4 and 5 replace the test class's corpus builder by a copy of a corpus I built once, and apply the second switch to the whole process instead of per test ID. They are evidence for the route. They are not acceptance of any test.

**Deviation 3: one command failed for a shell reason and was repeated.** zsh did not split a variable holding the interpreter and its flag; six commands printed "no such file". No Python ran. I repeated them with the interpreter written out.

**The laptop battery was never read.** The guard's log held 61 lines before my first run and 61 after my last. No process of mine was running at the end. Two processes matching my scratch path exist (`zsh /tmp/d528-wait.sh …`); they belong to whoever launched me and I did not touch them.

## 1. Terms used in this addendum

Terms of the ruling in force (its §1) keep their meaning. The ones this text leans on, restated, and the new ones:

- **Bundle.** One run's directory (`config.json`, `metadata.json`, `events.jsonl`, the summary, raw telemetry).
- **The gate.** The battery check `authenticate_window_members` in `joulewise/bundle_read.py`.
- **Physical config.** A `config.json` whose SHA-256 equals `metadata.config_sha256` and that names a telemetry backend other than `mock`.
- **The builder.** `produce_strict_bundle` in `tests/bfgs_fixtures.py`: it runs the production controller on replayed telemetry with a fake clock and writes a bundle with a physical config and a battery pair.
- **Whole-window verdict row.** One line in `campaign_log.jsonl` that the campaign runner writes after a window: it records, for the whole set of bundles, whether the machine was idle enough (CPU admission per member), whether the power adapter stayed the same (adapter continuity), and whether two reference runs at the start and end of the window agree (the NEG-8 bracket). A reader does not trust the row; it recomputes the row from the members' own files and refuses on any difference.
- **Reference bundles.** The two bundles of a window, one at the start and one at the end, whose energies the NEG-8 bracket compares.
- **Exemption, first form.** The property `CustodyTelemetryIdentity.production_predicate_exempt` (`joulewise/whole_window.py:996`): true when the config is not bound or is mock. Five uses, in four functions. This is the only form the ruling in force knew.
- **Exemption, second form.** The function `_current_strict_summary(summary, bundle_path)` (`joulewise/whole_window.py:3554`). It answers "is this a current, non-mock measurement?": true only when the summary's reducer version is `0.5.2` or `0.6.2` **and** the bundle is not mock. Where it answers false for every member, the reader skips the recomputation described above and uses the older, shorter check. Fourteen call sites in eleven functions, all in `joulewise/whole_window.py` (§4.2).
- **Parity** (ruling in force). The test-only switch `exemption_parity(test_id)` that turns the first form to "exempt" for one named test. **Second switch:** the extension ruled in §4 that also makes the second form answer false, for one named test.
- **The pilot test.** `tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader`. **Its subject:** a bundle from the real controller whose config leaves the model unpinned is read by the loader with matching config identity (it asserts six model keys, `inclusion_status == "included"`, and no `config_hash_mismatch`).
- **Stand-in.** A replacement of production code inside a test.
- **Planted defect.** A deliberate fault added to prove a test turns RED when it should.

## 2. Executed evidence (this session, all in the foreground)

Probe scripts and outputs are under `/tmp/cg-s1pilot-d528efb2/` (`probe1.py` … `probe5.py`, `p4_on.tsv`, `p5.tsv`); the lead copies them into the trace directory. SHA-256 prefixes: probe1 `f6db72ef`, probe2 `8c890437`, probe3 `1b083448`, probe3b `f06cc5de`, probe4 `4f042cb2`, probe5 `a43b41bd`, p4_on `fa0455e3`, p5 `3d28d64d`.

| # | Probe | Result |
|---|---|---|
| Z1 | The pilot's command V6, unchanged | `Ran 1 test in 126.833s`, `AssertionError: 'excluded' != 'included'`. The pilot's RED reproduces. |
| Z2 | `probe2.py`: the class corpus built once by the test's own `setUpClass` and kept; the loader called exactly as the test calls it, with the test's own two stand-ins from `setUp`; once with parity, once without | **With parity:** excluded, six reasons, exactly those the charge lists. **Without parity:** excluded, the same six. Parity changes nothing for this test. |
| Z3 | Same, with the second form forced to answer false | With or without parity: excluded, **one** reason left, `whole_window_verdict_conflict`. Five of the six reasons vanish. |
| Z4 | Same as Z2, with a recorder around each step of the recomputation | `current_environment_refusals`: 32 calls, each returning `environment_admission_failed` and `environment_admission_missing`. `evaluate_cpu_idle_admission`: 32 calls, each `decision: failed`, `sample_count: 0`, conditions `cpu_baseline_telemetry_missing`, `gpu_idle_admission_unknown`. `evaluate_adapter_wattage_continuity`: 1 call, `decision: failed`, `adapter_wattage_unknown`, 64 observations of 64 unknown. `_derived_neg8_decision`: 1 call, returned `(None, "provenance")`. `_current_core_rederivation_reasons` returned all six reasons. |
| Z5 | The stored verdict row and one produced bundle, printed | Row: `idle_admission_core` holds `adapter_wattage_continuity`, `conditions`, `members`, `neg8_bracket`, `policy_sha256`, `schema_version` and **no** `instrument_calibration_bracket`; its `neg8_bracket` holds only `decision`, `policy`, `schema_version`. Bundle: `metadata.environment_admission` is `null`; reducer `0.5.2`; backend labels all `powermetrics`; real identity bound, labels agree; its own summary records `cadence_ratio_unrecorded`, `clock_anchor_unresolved`, `clock_bound_unrecorded`, `environment_admission_failed`, `environment_admission_missing`. |
| Z6 | `probe3.py`, route R1: second form off, produced reference bundles kept | excluded, `whole_window_verdict_conflict`. The NEG-8 recomputation returned `failed`; the row says `passed`. Both produced reference bundles have `gross_energy_j` 0.7754668970251918 and **no** anchor-shift envelope. |
| Z7 | `probe3b.py`, route R2: second form off; the two reference bundles rewritten as on main (gross 1.0, envelope 0.99 to 1.01), plus the label `measurement_quality.telemetry_source = "powermetrics"`, a physical config (`rebind_config`) and a passing pair (`write_passing_pair`) | **included, no reason; all 30 registered bundles included; the gate answered `pass` for all 30.** NEG-8 recomputation returned `passed`. Without the label (first attempt, `probe3.py`) one reason remained, `bundle_strict_invalid`: a bound config whose labels do not all agree. |
| Z8 | R2 with the ruled parity only (second form left on) | excluded, the same six reasons. The reference repair alone does not cure. |
| Z9 | R2 with the second switch but **without** the first | included, no reason. This test does not need the first form at all. |
| Z10 | Planted defect 1: R2, charging pair written on the target member | `WindowBatteryRefusal … battery_float_confounded (pre IsCharging is not No, pre InstantAmperage exceeds 200 mA)`. |
| Z11 | Planted defect 2: R2, one byte appended to the target's `config.json` | `WindowBatteryRefusal … battery_float_evidence_missing (pair not bound (config.json digest does not match metadata.config_sha256))`. |
| Z12 | `probe4.py`: all 22 T5 test IDs (the 57 outcomes), each run by `unittest` with its own `setUp`, corpus of Z7, second switch on | 6 IDs GREEN, 16 RED. Table in §5.1. |
| Z13 | `probe5.py`: 9 of the 16 RED IDs again, with the test module's verdict installer wrapped so that every pair of reference directories it writes gets the form of Z7 | 1 more GREEN (`test_valid_replacement…_with_production_telemetry_identity`), 8 RED. |
| Z14 | The pilot's V2 to V5 (the T2 pilot and the bind+pair pilot, each GREEN, each with the charging pair planted) | All four reproduce: `OK`, `battery_float_confounded` (1 member), `OK`, `battery_float_confounded` (3 members). Two more of mine: the T2 test **without** its ID on the list fails at once; the T2 test with its ID granted but the switch replaced by a no-op fails with `all_cells_extractable` false. So the T2 green rests on the switch, as ruled. |
| Z15 | Syntax-tree walk of ten production files for every branch on the bundle's identity; `grep` over `joulewise` and `scripts` for the two function names of the second form | §4.2 and §6. The second form is called from `joulewise/whole_window.py` only. |
| Z16 | Read `joulewise/whole_window.py:5308-5355` | The result of validating a verdict row is kept per session object, not per process. A result computed with a switch on cannot leak into a later test. |

**NOT EXECUTED by me:** the helper of §4.3 as written (I executed the two patches it wraps, not the helper); any test of §4.5; the full suite; any T5 test on main; the seven GREEN IDs **without** the second switch in my harness, except the pilot test (Z8); the census of sibling tests of §4.4 rule 9; the T4 rule on any test; the T1 rule on any test; whether the seven candidates of sub-class M in §5.1 really have the mock refusal as their subject (I judged by name and by the error text, and did not read the seven tests).

## 3. Ruling 1 — why T5 fails

### 3.1 The mechanism

```
load_analysis_inputs(manifest, runs_root, floor)            joulewise/analysis_engine/inputs.py
 │
 ├─ A. the gate, on every member                             real in every test; no switch reaches it
 │
 ├─ B. per bundle, _read_bundle                              strict validation, label agreement,
 │                                                           mock barrier: real in every test
 │
 └─ C. once per window, whole_window_refusal_reasons         inputs.py:3357
        reads the verdict row from campaign_log.jsonl
        recomputes it in _current_core_rederivation_reasons  whole_window.py:4388-4398
           asks the SECOND FORM about each member
           ├─ no member is current and non-mock  →  stop here, short check only
           └─ any member is current and non-mock →  recompute environment admission,
                                                    CPU admission, adapter continuity,
                                                    calibration bracket, NEG-8 point drift
        every refusal found in C is attached to EVERY bundle of the window  (inputs.py:3363-3370)
```

Every element of the drawing: A is the battery gate. B is the per-bundle reading. C is the window-level verdict check. The fork inside C is the second form. The last line is why one refusal in C excludes all 30 bundles at once.

**Worked example, with the numbers of Z2 to Z7.** The pilot test's window has 32 members: 30 registered bundles and 2 reference bundles.

1. On main the 30 bundles came from the controller on the `mock` backend. The second form answered false 32 times. C took the left branch. The hand-written verdict row was accepted as written. The test was green.
2. S1 refuses mock bundles on claim paths, so round 2 rebuilt the corpus with the builder: physical config, reducer `0.5.2`. Now the second form answers true. C takes the right branch and recomputes the row from the members. The members carry no environment admission (`null`), no idle records (0 samples), no adapter wattage (64 of 64 unknown). The recomputed row says "failed" three times; the hand-written row says "admitted", "stable", "passed". Six reasons, attached to all 30 bundles.
3. Parity switches the first form. The first form is not in C. Same six reasons (Z2).
4. With the second form switched to false, C takes the left branch again, as on main. One reason is left (Z3), and it has a different cause, item 5.
5. Round 2 had also replaced the two hand-written reference bundles (energy 1.0 J, envelope 0.99 to 1.01 J) by produced bundles. Those have energy 0.775 J and no envelope. The short check cannot read a reference without an envelope and answers `failed`; the row says `passed` (Z6).
6. With the references back in main's form, labelled, bound and paired, the short check answers `passed` and the test is green with all 30 bundles included and the gate at `pass` 30 times (Z7).

### 3.2 The six reasons, one by one

| Reason | Where it is raised | What was compared (executed, Z4 and Z5) | Kind |
|---|---|---|---|
| `environment_admission_missing` | `whole_window.py:4456`, from `current_environment_refusals` | the member's `metadata.environment_admission` is `null` | an **honest refusal of the produced bundle**, reached only through the second form |
| `environment_admission_failed` | same call | same | same |
| `cpu_admission_core_failed` | `whole_window.py:4497` | recomputed: `failed`, 0 samples; stored, hand-written: `{"decision": "admitted"}` | the produced bundle has no idle records **and** the row is hand-written; reached only through the second form |
| `adapter_continuity_failed` | `whole_window.py:4514` | recomputed: `failed`, wattage unknown 64 times; stored, hand-written: `stable` | same |
| `whole_window_verdict_provenance_invalid` | `whole_window.py:5748` (recomputation returned `provenance`); by reading also `:5715` (a current row must carry four point-drift fields; the hand-written bracket has none of them) | the hand-written row has the old shape | a refusal of the **test's hand-written row**; reached only through the second form |
| `whole_window_verdict_conflict` | by reading `whole_window.py:4551` (the row has no calibration bracket); by execution `:5803` on the short path (NEG-8 recomputed `failed`, stored `passed`) | the first cause goes with the second form; the second cause is the round-2 reference bundles | second form, **and** a side effect of round 2 |

### 3.3 The three questions of the charge

- **Exemption-gated checks that parity should cover.** All six are behind an exemption. None is behind the form parity switches. The closed list of the ruling in force is not short of entries; it is short of a whole form.
- **Honest refusals of the produced bundle.** Environment admission (two reasons), and the recomputed side of CPU admission and adapter continuity. The builder produces a bundle; it does not produce a window. It has no environment admission, no idle records, no adapter wattage, and the verdict row next to it is written by the test.
- **The test's own subject.** None of the six. The subject is config identity (§1).

**One fact the triage could not see.** On main this test already stipulated a production identity, but only inside `joulewise.analysis_engine.inputs` (its own `mock.patch` of `custody_telemetry_identity` there, unchanged by S1). `whole_window` kept reading the real, mock identity. So on main the same bundle was "production" to one module and "mock" to the other. A recorder around the real function sees only the second.

## 4. Ruling 2 — the T5 route

### 4.1 The four routes of the charge, judged

| Route | #421: claim paths gated? | #421: evidence a real window could produce? | Risk of another same-signature round | Ruling |
|---|---|---|---|---|
| **Extend the closed list** by the second form, by test ID | Yes. No production file changes. | No, by the letter; the same answer the ruling in force gave for the first form (its §3.3), now for a larger set of checks. See §4.6. | **Low to moderate, and measured:** 7 of 22 IDs green by execution, both planted defects red, the rest sorted by cause (§5.1). What remains open is a third form; §6 bounds it. | **Adopted**, with the reference bundles restored (§4.3, §4.4). |
| **Extend the builder** until a produced window passes the recomputation | Yes | Yes | **High.** Z4 and Z5 name at least five things nobody has built: environment admission, idle records, adapter wattage, a clock anchor, and a verdict row written by the production runner in the current shape. The replay keyword of the ruling in force (its §5.2, class T5) addresses one of five. | **Not inside S1.** The keyword task is **withdrawn**. The five items go to the lane CLAIM-CHAIN-CANARY-01. |
| **Re-class into refusal assertions** | Yes | Yes | Low | **Refused for tests whose subject is positive** (the loader includes; the analysis computes): asserting the refusal would delete what they test. **Adopted only** where the subject is the refusal itself (sub-class M, §5.1), which is class T3 as already ruled. |
| **Split the 57 rows into a lane** | Yes | Yes (nothing passes) | — | **Refused.** It would merge S1 with the analysis loader's positive path untested, when 42 of the 57 outcomes have an executed repair. |

### 4.2 The closed list of the second form

By syntax tree (Z15). One patch of `_current_strict_summary` switches all of them, because `_row_references_current_strict_member` calls it.

| Function in `joulewise/whole_window.py` | Line at `601a06c5` |
|---|---|
| `AuthenticatedConsumptionSession._prepare` | 776 |
| `_manifest_members` | 3504 |
| `_reference_energy_evidence` | 3650 |
| `mint_neg8_drift_bound_artifact` | 3843 |
| `_derived_neg8_decision` | 4144 |
| `_manifest_bundle_paths` | 4273, 4276 |
| `_current_core_rederivation_reasons` | 4392 |
| `_validate_row_uncached` | 5681, 5690 |
| `_row_references_current_strict_member` | 5872 |
| `whole_window_refusal_reasons` | 6046, 6052 |
| `whole_window_drift_allowances` | 6230 |

### 4.3 Ruled text

In `tests/bfgs_fixtures.py`, the helper of the ruling in force (its §3.3) becomes:

```python
# Closed list, second form: every function of joulewise/whole_window.py
# that asks whether a member is a current, non-mock measurement.
PARITY_SECOND_FORM_SWITCHED_OFF = (
    "AuthenticatedConsumptionSession._prepare",
    "_manifest_members",
    "_reference_energy_evidence",
    "mint_neg8_drift_bound_artifact",
    "_derived_neg8_decision",
    "_manifest_bundle_paths",
    "_current_core_rederivation_reasons",
    "_validate_row_uncached",
    "_row_references_current_strict_member",
    "whole_window_refusal_reasons",
    "whole_window_drift_allowances",
)

# Closed list of test IDs granted the second switch.  A subset of
# PARITY_TEST_IDS.  Written by the lead; a seat never adds to it.
PARITY_SECOND_FORM_TEST_IDS: frozenset[str] = frozenset({
})


@contextlib.contextmanager
def exemption_parity(test_id: str):
    """For one named test, treat every bundle as main treated it.

    First form, for every granted ID: every bundle counts as exempt.
    Second form, only for IDs on the second list: no bundle counts as a
    current, non-mock measurement.  The battery gate, the bundle's config
    binding, the mock barrier and strict validation are untouched: none of
    them reads either form.
    """
    if test_id not in PARITY_TEST_IDS:
        raise AssertionError(f"exemption parity not granted to {test_id}")
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(
            whole_window.CustodyTelemetryIdentity,
            "production_predicate_exempt",
            property(lambda self: True),
        ))
        if test_id in PARITY_SECOND_FORM_TEST_IDS:
            stack.enter_context(patch.object(
                whole_window, "_current_strict_summary",
                lambda *args, **kwargs: False,
            ))
        yield
```

In `tests/test_analysis_integration.py`, `install_passing_analysis_whole_window` writes each of its two reference directories as on main and then, in this order: adds `"measurement_quality": {"telemetry_source": "powermetrics"}` to the summary; writes a schema-valid `config.json` with the directory's `run_id` (template: `tests/fixtures/d078_r01/config.json`, as in the T2 pilot); writes `metadata.json` with `run_id` and `adapters.telemetry.name = "powermetrics"`; calls `rebind_config`; calls `write_passing_pair`. The two loops of `setUpClass` that replaced the reference directories by produced bundles (round 2, the last hunk of `setUpClass`) are removed. The energies 1.0, 0.99, 1.01 stay byte-identical. This is class T2's fixture form; it writes no admission evidence.

### 4.4 Rules, added to rules 1 to 6 of the ruling in force

7. **The second switch is granted by test ID, and only where main ran without those checks.** The lead's recorder, on main's tree only, wraps `_current_strict_summary` and logs its answer per bundle. An ID is granted only if the answer was false for every bundle the test read on main.
8. **Never the test's own subject.** Refused to a test whose own source, or a fixture method of its class that it calls, names a function of §4.2, or asserts a reason that only the right-hand branch of §3.1 can raise, or whose subject is the verdict row under current evidence. `test_authenticated_v2_whole_window_source_reaches_claim_consumption` is refused by this rule.
9. **Every switched-off check keeps a test that runs it switched on.** Before the switch lands, the lead lists green tests on the candidate that reach `_current_core_rederivation_reasons` past its early return: at least one that asserts a refusal and at least one that asserts acceptance. If no accepting test exists, the pull-request description says so in the sentence of §8, and the canary lane owns the gap. The lead does not invent one.
10. **The first form is not granted where it is not needed.** The pilot test passes without it (Z9). The helper applies it to every granted ID because that is the ruled text and it is harmless there (the test's own stand-in already stipulates a non-exempt identity inside `inputs.py`). No T2 test receives the second switch unless rule 7 grants it.
11. **No third switch on anyone's authority but a cold gate's.** A refusal that survives both switches is returned by test ID with the name of the refusing check.

### 4.5 Tests owed with the second switch

| Id | Input | Must observe | Planted defect that must turn it RED |
|---|---|---|---|
| H-19 | the scenario of Z7 under `exemption_parity` with an ID on both lists | gate `pass` for every member; every registered bundle `included`; no reason | the second `patch.object` removed: the six reasons of §3.2 |
| H-20 | an ID on the first list only | inside the block, `whole_window._current_strict_summary` is the original function | the `if test_id in …` line removed |
| H-21 | H-19 with the charging pair on one member | `WindowBatteryRefusal`, `battery_float_confounded` (executed, Z10) | none; pins that neither switch reaches the gate |
| H-22 | H-19 with one byte appended to one member's config | `WindowBatteryRefusal`, `battery_float_evidence_missing` (executed, Z11) | the gate fix of the ruling in force, §4.2, reverted in a scratch copy |
| sweep 2 | walk the syntax trees of every tracked `*.py` under `joulewise/` and `scripts/`; collect the enclosing function of every call named `_current_strict_summary` or `_row_references_current_strict_member` | the set equals `PARITY_SECOND_FORM_SWITCHED_OFF`, and every call is in `joulewise/whole_window.py` | a twelfth caller added in a scratch copy is reported |

Under `tests/`, the name `_current_strict_summary` may appear in helper H, in its own test module, and in the two files that name it today (`tests/test_whole_window_selection.py`, `tests/test_whole_window.py`); nowhere new. I checked today's files on the candidate, not on main; the lead confirms against main.

### 4.6 #421, stated plainly

**"No claim path un-gated."** Met. The route changes no production file. Every claim path keeps the gate and every check it has.

**"No test may pass on evidence a real window could not produce."** By the letter, **not met**, exactly as for the first form. Under both switches a test passes while these checks are off: environment admission, CPU admission, adapter continuity, the calibration bracket and NEG-8 point drift, all at window level. A real window that lacked them would be refused. They were equally off for the same tests on main, because main's corpus was mock.

The ruling in force read the directive as governing what production accepts, and said that reading is the owner's to overturn. I keep that reading and I widen what rests on it. The owner should decide knowing the size:

| | First form only (ruling in force) | Both forms (this addendum) |
|---|---|---|
| Places switched off | 5, in 4 functions | 5 + 14, in 4 + 11 functions |
| Tests affected | the T2 tests (33 outcomes in the triage) | those, plus up to 7 T5a test IDs (42 outcomes) |
| If the owner holds the letter | route: extend the builder | the same, and the five unbuilt items of §4.1 are the work list; S1 stays on HOLD meanwhile |

## 5. Ruling 3 — the 57 rows, the other classes, the stop conditions

### 5.1 T5 is four kinds of test, not one

The 57 outcomes are 22 test IDs (two IDs carry 25 and 12 sub-test outcomes). Under the route (Z12, Z13):

| Sub-class | Test IDs | Outcomes | What I observed | Rule |
|---|---|---|---|---|
| **T5a**, positive tests on the class corpus | 7: the pilot test; and the variants `…_with_production_telemetry_identity` of `complete_strict_current_bundle_set…` (25), `incomplete_pair_is_listed…` (12), `unregistered_matching_topup…`, `private_stochastic_seam…`, `named_strata_manifest…`, `valid_replacement_fills_original_slot…` | 42 | GREEN | Builder corpus stays; references per §4.3; both switches by ID under rules 7 and 8; assertions byte-identical. |
| **M**, candidates for a mock-refusal subject | 7: the five variants of the rows above **without** `_with_production_telemetry_identity` (`complete_strict…`, `unregistered_matching_topup…`, `private_stochastic_seam…`, `named_strata_manifest…`, `valid_replacement…`) and both `test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal…` | 7 | RED: `5 != 0`, `False is not true`, a list difference, `unexpectedly None`. On the candidate two of them fail with `'mock_telemetry_claim_ineligible' not found`. | The lead reads each. Where the subject is the refusal of mock bundles: class **T3** as ruled (R-list, sibling). Otherwise T6. |
| **F**, a member directory with no bundle form | 4: `test_cli_output_separation…`, `test_claim_output_separation…`, `test_attribution_limited_floor…`, `test_real_controller_pinned_model…` | 4 | RED at the gate: `missing required artifact: metadata.json` for `a10:cell-1-r0`, `runs:cell-1-r0`, `runs:attribution-cond-2m-short_short-r0` | Class **T4** first (give the members bundle form, bound and paired), then T5a. |
| **R**, residue | 4: `test_incomplete_pair_is_listed…` and `test_replacement_with_changed_rep_tag…` (RED at the gate for `mock-model-r1-short_short`, cause not established by me); `test_authenticated_v2_whole_window_source…` (refused by rule 8); `test_production_request_factory_reaches_predeclared_transport` (`unexpectedly None`, cause not established) | 4 | RED | **T6**, `NEEDS_RULING`, by test ID. |

42 + 7 + 4 + 4 = 57.

### 5.2 Round 3 proceeds for the other classes

| Class | Outcomes in the triage | May proceed? | Basis |
|---|---|---|---|
| NEW | 3 | **Yes**, now | ruling in force §4.3 |
| bind + pair | 37 | **Yes**, now. Accepted as a class of its own: bind first, then the pair, no switch, assertions byte-identical. | pilot held, re-executed by me (Z14) |
| T2 | 33 | **Yes**, now | pilot held, re-executed by me, and shown to rest on the switch (Z14) |
| T1 | 3 | **Yes, after one bench check.** The floor row `test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence` fails with `environment_admission_missing`, a reason of the first form, though its class says no bundle was exempt on main. The lead applies the pair alone at the bench. If it stays RED it is T6. | not executed by me |
| Paper pins | 23 | **Yes**, at step R3-7 as ruled | unchanged |
| T5a | 42 | **After pilots P-1 and P-2** (§5.3) | Z7, Z12, Z13 |
| F | 4 | **After pilot P-3** | T4 has never been piloted: the pilot substituted bind + pair for it |
| M, R, and the 5 T6 rows of the triage | 7 + 4 + 5 | per ID, as ruled above | — |

Seat H3 starts now, with §4.3 and §4.5 added to its task and the replay keyword removed from it. Its write scope is unchanged; the change to `install_passing_analysis_whole_window` belongs to seat A's file and seat A's scope. Seats A and B start after H3's commit, as ordered in the ruling in force (its §5.4), on every class marked "Yes". Seat A touches no T5 or F test ID until the lead has filed the pilots.

### 5.3 The pilots still owed, and who runs them

**The lead, at the bench, in scratch, nothing committed. Not a seat.** The pilot of the ruling in force was built by a seat; its claims reproduce (Z1, Z14), so nothing is lost, but the step exists so that the lead sees the class rule work with its own hands before it briefs anyone.

| Pilot | Test | Must observe |
|---|---|---|
| P-1 | the pilot test, on the real test file, with the helper of §4.3 and its ID on both lists | GREEN; RED with `battery_float_confounded` under the charging pair; RED with the six reasons of §3.2 when its ID is taken off the second list |
| P-2 | `test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact_with_production_telemetry_identity` (25 outcomes) | GREEN; RED under the charging pair |
| P-3 | `test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink` (runs in about 1 s) by the T4 rule, then as T5a | GREEN; RED under the charging pair |

### 5.4 Revised stop conditions

Conditions 1 to 4 and 7 of the ruling in force stand, with two amendments. Condition 5 is met and closed (the gate fix turned 44 IDs, under 50, by the lead's record; not re-measured by me). Condition 6 fired and is discharged by this addendum.

- **Condition 1, amended.** "…switched off by anything other than `exemption_parity`" now covers both forms of §4.3 and nothing else.
- **Condition 2, amended.** The cap stays at **10** outcomes still failing after R3-6. Outcomes that the triage record marked `NEEDS_RULING` **before** any seat started (sub-class R, the T6 rows, and any M row the lead finds is not T3) are not counted: they go to the per-ID gate in any case. The cap counts surprises.
- **Condition 6a, new.** P-1 or P-2 fails: return to a cold gate before seat A touches any T5 ID. P-3 fails: the four F IDs join the residue; no cold gate is needed for that alone.
- **Condition 8, new.** A refusal survives both switches on more than **3** test IDs and comes from one and the same check: return to a cold gate. That would be a third form.
- **Condition 9, new.** `PARITY_SECOND_FORM_TEST_IDS` holds more than **11** IDs (the 7 of T5a and the 4 of F): return to a cold gate. The second switch is for the integration corpus and is not to spread.

Round 3 remains the last repair round. The lead starts no round 4 on its own authority.

## 6. Ruling 4 — what the pilot shows wrong in the ruling in force

1. **§3.3, the closed list, was built from one name.** It listed the five uses of `production_predicate_exempt` and called them "exactly" what parity switches off. Production code branches on the bundle's identity in more ways. My census of ten files (Z15), which the lead repeats over all of `joulewise/` and `scripts/` and files with the triage record:

   | Kind | Where | Places | Effect on a physical test bundle |
   |---|---|---|---|
   | first form | `inputs.py`, `floor_extraction.py`, `run_campaign.py` | 5 | checks switch **on**; parity switches them off |
   | second form | `whole_window.py` | 14 | checks switch **on**; the second switch |
   | label agreement (a bound config whose three backend labels differ is strictly invalid) | `inputs.py:1939`, `:2856`; `floor_extraction.py:2022`; `run_campaign.py:2845`, `:5372`; three calls of `_custody_strict_invalid` in `whole_window.py` | 8 | **adds** a refusal; met by agreeing labels (Z7's first attempt shows it biting) |
   | mock barrier | `inputs.py:1943`, `:2889`; `floor_extraction.py:2028` | 3 | adds a refusal to mock bundles only |
   | decided when the bundle is **produced** | `reduce.py` (6), `controller.py` (4), `cli.py` (2), `adapters` (2), `idle_dependence.py` (1), `run_campaign.py:4172` (1) | 16 | recorded in the bundle's own files; no switch at reading time can change it |

   The last row is where a third form would come from. It did not stop any of the seven GREEN IDs.
2. **§3.2 rated parity's risk "Low … the switch restores main's checks by construction".** It restores the checks behind one property. The sentence "a refusal that survives it has, by definition, a different cause" was true and unhelpful: the different cause was a second form of the same thing.
3. **§5.2, class T5, is wrong twice.** It expected the surviving refusal to be "recorded in the produced bundle's own summary" and ruled a replay keyword for it. The surviving refusals come from the window's verdict row. The keyword would not have cured one of the six reasons. It is withdrawn.
4. **§5.1, the triage recorder, could not see this.** It records one form, around one function. It cannot see the second form, and it cannot see a test's own stand-in for the identity inside one module (§3.3 above). The class T5 it produced mixes four kinds of test (§5.1 above). The lead adds the recorder of rule 7.
5. **Round 2's replacement of the reference bundles by produced bundles was a mistake** (it sits in `setUpClass`, from A3's step R2-3). Produced bundles carry no anchor-shift envelope, so the NEG-8 recomputation fails on them whatever else is done (Z6). §4.3 undoes it.
6. **§5.4, step R3-3, was not followed in two ways.** A seat ran it, and T4 was not piloted. The first is recorded by the lead and I find no harm in it. The second is cured by P-3.
7. **§8, the sentence for the pull-request description, is out of date.** It becomes: "N tests run claim-path code under exemption parity: the battery gate and the bundle identity are real, and the five checks behind the first exemption form are off, as they were for the same fixtures on main. M of them also run with the window-level recomputation off (environment admission, CPU admission, adapter continuity, calibration bracket, NEG-8 point drift), as it was off for the same tests on main. No test yet runs the whole claim chain on fully produced evidence; the first real window after merge is the first end-to-end exercise." N and M are the sizes of the two lists.
8. **§3.3, rule 3, the refusal vocabulary,** must also hold every reason the right-hand branch of §3.1 can raise, for IDs that ask for the second switch. Rule 8 above says so.

**What stands, unchanged.** The route (parity, not the builder, not a split). The gate fix of §4 and its tests. Rules 1 to 6. Classes T1, T2, T3, T4, T6. The order R3-0 to R3-7. The hard cap on rounds. The lanes, with the five items of §4.1 added to CLAIM-CHAIN-CANARY-01.

## 7. Corrections to the charge's facts

1. **"The prototype's parity closed list has 4 entries"** suggests the list is short of entries. It is complete for its form: four functions, five places. What is missing is the second form, eleven functions, fourteen places.
2. **"57 T5 rows"** are 22 test IDs.
3. **The charge offers "adapter continuity" and "whole-window verdict provenance" as gaps in the builder's evidence.** Half of each is the test's hand-written verdict row, not the builder.

## 8. Plain summary

1. The pilot failed because the code has two separate ways of going easy on test bundles and the ruled switch covered only one; all six refusals come through the other one, none of them concerns what the test checks, and the battery check itself passed on all 30 bundles.
2. The cure is to extend the same declared, test-only switch to the second way, test by test, and to restore two reference bundles that the last round had replaced; I ran it, 42 of the 57 failing outcomes turn green, and a charging battery or a tampered config still turns the test red, while the other 15 are sorted into classes that already have rules or go to a ruling one by one.
3. The rest of round 3 may start now; the owner should know that this widens what rests on reading directive #421 as a rule for production code rather than for test fixtures (19 places switched off in tests instead of 5), and that holding the directive to the letter means building five kinds of evidence first, with S1 on hold meanwhile.
