# Cold gate BFGS-S1-R2-01: ruling (Fable 5.1, cold judge) on S1 round 2's blockers

Candidate: `feat/2026-09-26-bfgs-s1-bundles` @ `49d77c74` (round 2 `21213be7` + fix round 2). Base `1417c0c4`.
Charge: `80-coldgate-r2/00-charge.md`, committed at `18546911`. Session: one foreground session, no subagents, no background tasks. No repository file edited; `git status --short` in the working tree was empty at the end (E12).

---

## 0. Contamination disclosure

The charge told me not to read `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md`, `AGENTS.md`, the decision log, or memory and skill files. I opened none of them. **However, the harness that started this session placed three of them in my context before the charge arrived:** the owner's global `CLAUDE.md` (a writing standard and a pointer to orchestration doctrine), the project `CLAUDE.md` (notes on the Codex bridge), and the index file `MEMORY.md` (about 110 one-line summaries of earlier sessions, including checkpoint lines that name this lane, pull-request numbers, and standing directives of the owner). I did not open any file those lines point to.

What this exposure could bias, and what I did about it:

- The index mentions that gates should be "sensible on science grounds" and that docs and tests get light gates. I did not use either as authority. Every ruling below rests on the ruled texts named in the packet, the code at `49d77c74`, and probes I ran.
- The index names the state of other lanes and pull requests. None of it bears on the six questions, and none is cited.
- The global writing standard asks that every term be defined at first use. The charge asks the same of the summary for Ed. I followed it throughout; it changes wording, not rulings.

I read, from the packet: the round-2 brief and seat report, the lens charge, both lens reports, the fix-2 brief and seat report, Final texts v1.1 (texts 7 to 12, §E, §F), amendments 20 to 28, amendment 26 as re-issued and amendment 31, amendments 36 to 43, and amendments 47 and 48. I did not read the lens logs, the seat logs, or any earlier cold-gate ruling beyond the sections that state those texts.

---

## 1. Terms used in this ruling

Each term is defined here once and used in this sense only.

- **Bundle.** The directory one measured run leaves behind. It holds, among others, `metadata.json` (what ran), `summary_metrics.json` (the reduced numbers, energy included), `power_trace.csv` (the power samples), and `events.jsonl` (the stage log).
- **Battery pair.** Two readings of the laptop battery's state, one taken before the measured span and one after. If either shows current flowing into or out of the battery, the wall-side and rail-side energy of that run cannot be trusted, because part of the power went to or came from the battery.
- **Verdict.** The object `PairVerdict` that the battery checker returns for one bundle. Its `status` is one of `pass`, `battery_float_confounded` (a reading shows charging or discharging), `battery_float_evidence_missing` (a reading is absent or unusable), `not_applicable` (a simulated run), `unobserved_historical` (a run measured before the check existed and listed in the committed set of 69 such runs).
- **Custody failure.** The exception `CustodyFailure` (and its subclass `CustodyUnreadable`): a file the evidence depends on is missing, unreadable, or does not hash to its recorded digest. It is never a status. It stops the whole computation.
- **The gate.** The function `bundle_read.authenticate_window_members(members)`. It takes a list of (label, bundle path), classifies every one, and either returns all verdicts or raises: `WindowBatteryRefusal` naming every member whose status refuses, or a custody failure labelled with the member it was found in.
- **Window.** One collection session: all the runs a campaign made under one runs directory and one campaign policy, selected or not.
- **Consumer.** One of the eight modules text 12 names, which turn bundles into claimed numbers.
- **Supersession record.** A row of type `campaign_occurrence_supersession` in a window's campaign log. It is written by `run_campaign --record-supersession` when one bundle id was collected twice. It names the selected occurrence, the superseded ones, and `quarantine.path`: the directory the superseded run's bundle was moved to. Production requires that directory to lie outside the runs directory (`run_campaign.py:6110-6111`, `whole_window.py:2821-2822`) and records the SHA-256 of three of its files.
- **Quarantined bundle.** The bundle at a supersession record's `quarantine.path`.
- **Placement.** In the scored campaign, one scheduled execution of one block of test items, keyed `(block_id, attempt)`. The roster (the executed schedule) records for each an **observation status**: `completed`, `cut_off` (it started and was stopped), or `not_started`. These three are the whole vocabulary (`scored_packer.py:237, :402`).
- **Capture window.** The reducer's input record that carries one placement's measured energy and the digest of the bundle it came from.
- **The sweep.** The test `tests/test_bfgs_consumer_sweep.py`. It parses every tracked Python file under `joulewise/` and `scripts/` and lists every place that reads a bundle's files without the gate. Each listed place must have a named row in the test's **allowlist** or the test fails.
- **Counterfactual.** For a test row: the specific wrong implementation under which the row must fail. A row that passes under its counterfactual tests nothing.

---

## 2. Executed evidence (this session, all in the foreground, working tree `49d77c74`)

| Id | Command or probe | Result (exact tail) |
|---|---|---|
| E1 | `PYTHONPATH=. python3 /tmp/bfgs_execution_probe.py` (the Sol lens's probe, re-run at `49d77c74`; `git diff --stat 21213be7 49d77c74` shows fix round 2 touched only the builder and two test files) | `campaign_helper ['pass'] quarantine_included False` / `ruled_set [('superseded', 'battery_float_confounded')]` / `sweep_mutant assigned []` / `sweep_mutant read_before_gate []` / `sweep_real_paper [] allowlist_rows []` |
| E2 | `/tmp/cg_r2/b2.py`: the reducer on fixture `_terminal_night(width=2, kind="ceiling_violation")`, placement `('large:decode:1:0', 0)`, class voided, status `cut_off`, no capture window | `pass PairVerdict, windowless -> refused battery_evidence_unbound` / `confounded PairVerdict, windowless -> refused battery_evidence_unbound` / `marker == roster status -> REDUCTION PRODUCED dict` / `marker != roster status -> refused battery_evidence_unbound` |
| E3 | `/tmp/cg_r2/gates.py`: every gate call in the eight consumers with its enclosing function, and the count of the word `quarantine` per module | 20 gate calls. `quarantine` occurs only in `whole_window.py` (9) and `run_campaign.py` (9); 0 in the other six. No gate call's member list reads a quarantine path. |
| E4 | `/tmp/cg_r2/q1.py`: the gate given a second member that is a missing directory, a symlink to a passing bundle, a regular file, a passing real directory | `missing directory -> CustodyUnreadable … missing required artifact: metadata.json | member: superseded:missing directory` / `symlink … -> CustodyUnreadable raw path traverses a symlink` / `regular file -> CustodyUnreadable … Not a directory` / `passing real directory -> returned {'selected': 'pass', …: 'pass'}` |
| E5 | `/tmp/cg_r2/q1_disk.py`: every supersession record in `/Users/edr/code/JouleWise/runs*/campaign_log.jsonl`, selected and quarantined bundle classified by the gate | `records 7`; all seven quarantine directories exist; in all seven, selected and quarantined are both `battery_float_evidence_missing: prospective bundle` |
| E6 | `python3 /tmp/opus_sweep2.py` (the Opus lens's widened detector) | `53 candidates; 23 not in allowlist` |
| E7 | `/tmp/cg_r2/sweep49.py . -v` (my prototype of the detector ruled in amendment 51; SHA-256 prefix `8e0d3bcdde3214e2`) | `sites 126 distinct rows (path,function,operation,file) 120 functions 89` |
| E8 | `/tmp/cg_r2/sweep49_cases.py`: the prototype on ten mutant sources and three gated sources, and on named real sites | all ten mutants `REPORTED` (K1 to K10, listed in amendment 51); all three gated sources `silent`; `current rows 65 | still reported 64`; the one not reported is the amendment-41 row, which moves to `main` (`('main', 'direct:issue_artifacts', 'power_trace.csv', 760)`); `prototype functions not in current allowlist: 37` |
| E9 | `/tmp/cg_r2/handlers.py`: handlers in the eight consumers whose caught types include `Exception`, `BaseException`, `RuntimeError`, `BundleReadError` or nothing | 49 at head (58 at base). `RuntimeError`: 19. `BaseException`: 15, of which 12 contain a bare `raise`. `BundleReadError`: 15. `Exception`: 0 at head. Ancestry printed: `CustodyFailure ['RuntimeError', 'Exception', …]`, `WindowBatteryRefusal ['RuntimeError', 'Exception', …]` |
| E10 | `/tmp/cg_r2/r47.py`: the builder's `build(root, names)` on three one-file trees holding `bundle_tree_sha256: ` + 64 `a` | `other.md -> entries 0 listed [...]` / `other.toml -> ValueError unclassified candidate pair` / `broken.json -> ValueError unclassified candidate pair: key=bundle_tree_sha256 schema=broken.json file=broken.json`, after stderr `unparseable broken.json: JSONDecodeError` |
| E11 | `python3 scripts/build_battery_float_historical_bundles.py --check` | `forward check: byte-identical entries=69` |
| E12 | `git diff --quiet 1417c0c4 HEAD -- <path>` for `joulewise/battery_float.py`, `reduce.py`, `bundle.py`, the three paper scripts, `tests/test_calibration_bracketing.py`, `tests/test_calibration_ledger.py`, `tests/receipt_corpus.py`, `configs/calibration`, `configs/campaigns`, `scored_packer.py`; `git ls-files | grep -c historical_captures.json`; a grep for any `battery_float` import line in the eight consumers; `git status --short` | every path `identical`; `0`; no import line; empty status. `battery_float.py` SHA-256 begins `4b4d7bb20625`. |
| E13 | `python3 -m unittest tests.test_bfgs_consumer_sweep tests.test_bfgs_window_consumers tests.test_scored_reduce.BatteryEvidenceReduceTests` | `Ran 23 tests in 30.305s` / `OK` |

Read, not run (each is marked where it is used): `run_campaign.py:5435-5509` and `:5849-5856` (a window with two present copies of one bundle id resolves `ambiguous` and is not eligible); `run_campaign.py:7933-7970` (the closing analysis of the speculative-decoding campaign); `whole_window.py:3895-3909`; `inputs.py:3128-3140` and `:1735-1757`; `calibration_bracketing.py:2331-2346`; `paper_prefill_resolvability_projection.py:181-197`; `issue_dg071_dg075_statistics.py:530-540, :742-762`.

---

## 3. Rulings at a glance

| Question | Finding | Ruling | Text |
|---|---|---|---|
| Q1 | Sol F1 | **UPHELD.** The quarantined bundle is a window member. Four more call sites have the same omission. | amendment 49 |
| Q2 | Opus B-2 | **UPHELD.** The marker is admitted for no status. Every started placement owes a verdict. | amendment 50 |
| Q3 | Sol F2, Opus B-1 | **UPHELD**, both. The detector is re-specified; the allowlist gains a fourth class that the sweep checks mechanically. | amendment 51 |
| Q4 | Opus S-1 | **UPHELD** as a breach. Raised from SHOULD-FIX to a required item of fix round 3. | amendment 52 |
| Q4 | Opus S-2 | **UPHELD. Remove** the collection-time gate. One closing analysis that relied on it gets its own gate. | amendment 53 |
| Q5 | flag R47-4 | **The classification rule governs.** The test row's expected result is corrected. | amendment 54 |
| Q6 | Opus S-3, S-4, S-5, N-1 to N-9 | **CONFIRMED** as test fixes with no text change, with three exceptions that the amendments above already rule (§9). | none |

Nothing is rejected. One detail of a lens report is corrected: the third line of the Sol probe (`aggregate_selected_mean 42.0`) does not show the campaign's verdict path releasing a number. It shows `aggregate_experiment` run on a list of one named bundle, which under amendment 49 (f) is that function's whole set. The defect F1 names is in the campaign helper, and lines one and two of the probe show it.

---

## 4. Q1: the quarantined bundle

### 4.1 What is asked

When one bundle id is collected twice, the operator moves the first run's bundle out of the runs directory and records a supersession. Text 12 defines a window's members as "every finalized bundle of the window, `FAILED` included, and every attempt the attempt ledger records, selected or superseded". The campaign's helper `_authenticate_whole_window_members` builds its list from the selected paths and from each bundle id's `present_paths`. Is the moved bundle a member, and if so how is it authenticated?

### 4.2 Evidence

- E1: with a charging-pair bundle at the quarantine path, the helper returns `['pass']` and the quarantine path is not in its result.
- Read, not run: `present_paths` is the list of copies of a bundle id found **inside** the runs directory (`whole_window.py:2426-2448`). A supersession is valid only when that list is exactly the one canonical path (`whole_window.py:2811-2813`), and a window where it holds two paths resolves `ambiguous` and is dropped (`run_campaign.py:5445-5448, :5852-5854`). So in every window that reaches the helper, `present_paths` holds the selected bundle and nothing else. The helper's clause for superseded runs can never add a member in production.
- The existing test `test_campaign_helper_includes_superseded_ordinary_and_axi_attempts` builds a resolution with two `present_paths`. That is the shape production refuses. The test pins a case that cannot occur and leaves the real one unpinned.
- E4: the gate, given a path that is missing, a symlink, or a regular file, already raises `CustodyUnreadable` carrying the member's label. No new custody code is needed.
- E5: seven supersession records exist on disk across six windows. In all seven both bundles are already refused as `prospective bundle` (measured before the check, and not among the 69 listed runs). Adding the quarantined bundle to the member list therefore changes the outcome of no window that exists today.

### 4.3 Ruling

**The quarantined bundle is a window member.** The reason is physical. The superseded run occupied time inside the window. A battery that was charging during it was charging in the window, and charging does not start and stop at the boundary between two runs. Text 12 already says "selected or superseded"; the supersession record is the ledger that records the superseded run.

**Other call sites with the same omission** (E3, and read):

| Call site | Member list today | Omits |
|---|---|---|
| `scripts/run_campaign.py::_authenticate_whole_window_members` (`:6197`) | selected paths, `present_paths`, sibling attempts under the attempt root | quarantined bundles (E1) |
| `joulewise/whole_window.py::_derived_neg8_decision` (`:3907`) | `ordinary_present_bundle_paths` per member id, sibling attempts | quarantined bundles (read) |
| `joulewise/analysis_engine/inputs.py::load_analysis_inputs` (`:3140`) | registered entries, sibling attempts | quarantined bundles (read; the module holds no reference to a quarantine path) |
| `scripts/run_campaign.py::run_axi_spec_campaign`, closing analysis (`:7933-7970`) | no gate call of its own; one gate per **selected** run through `evaluate_member` | every run the attempt ledger marks not eligible (read) |

The fourth row matters for Q4 as well: that closing analysis writes a whole-window verdict row and its only battery check is the collection-time gate that amendment 53 removes.

---

## 5. Q2: the scored reducer and placements without a capture window

### 5.1 Evidence

E2 reproduces the Opus probe exactly. For a placement that started, was stopped, and has no capture window:

- a genuine verdict, passing or confounded, is refused as `battery_evidence_unbound`, because `scored_reduce.py:133` requires a capture window for every verdict;
- the marker `{"no_bundle": "cut_off"}` is accepted, because `:128` checks only that no window exists and that the marker repeats the roster's status.

So the only evidence the reducer accepts for such a placement is a statement that there is no evidence. A run that was stopped while the battery was charging cannot refuse the reduction.

### 5.2 Ruling

Text 9 admits the marker "for a placement the roster records as having finalized no bundle". **The roster records no such thing.** Its three statuses say whether a block ran and whether it was stopped. A block that ran (`completed` or `cut_off`) went through the controller, and the controller writes a bundle for every run, failed runs included (text 7). `not_started` placements are outside the key set. So no placement in the key set meets text 9's condition, and **the marker is admitted for no status**.

One real case remains: a run whose process was killed before it wrote a bundle. The roster cannot tell that case from any other stopped run, so the reducer cannot excuse it. Its placement has no verdict to supply, and the reduction refuses with `battery_evidence_missing`. That is the outcome text 9 already accepts for a stopped run on a charging battery; what it costs a campaign is the question of the existing lane SCORED-CEILING-BATTERY-01, where it is recorded.

---

## 6. Q3: what the sweep must detect

### 6.1 Evidence

- E1 and the Opus mutants: a read through a variable, through a module constant, through `open_authentication_input`, or placed before the gate is not reported by the detector at `49d77c74`.
- The detector treats any call of the form `x.metadata()` as the gate, whatever `x` is (`test_bfgs_consumer_sweep.py:125-129`).
- The detector meets amendment 41's witness only through a clause that names one script, one function and one variable (`:139-144`).
- E6: the Opus detector finds 23 functions neither gated nor listed.
- E7, E8: a detector built to the rule of amendment 51 reports all ten mutants, stays silent on the three gated sources, reports 64 of today's 65 rows, and reports 120 rows over 89 functions in total, 37 of them functions with no row today.

### 6.2 Ruling

Both findings are upheld. The detector is re-specified in amendment 51 so that it follows the **path**, not the spelling of one call. The allowlist rule is tightened in two ways: each row names the file it reads, and a fourth class, `behind_gate`, replaces the use of `strict_validation` for "my caller already ran the gate", with the claim checked by the sweep itself.

I found, as the Opus lens did, no site that releases a claimed number ahead of a gate. I did not trace all 120 rows (§10).

---

## 7. Q4: the broad handler, and the gate at collection time

### 7.1 S-1

`inputs.py:1751` is `except (OSError, RuntimeError, TypeError, ValueError)`. It exists at base (one occurrence at `1417c0c4`, one at head). Round 2 made the gate reachable inside its `try` body. `CustodyFailure` and `WindowBatteryRefusal` both descend from `RuntimeError` (E9), so both are caught and replaced by the string `whole_window_verdict_provenance_invalid`.

**This is a breach.** Amendment 42 says "Consumers never catch `CustodyFailure`", without qualification. The round-2 brief's constraint says no consumer converts a custody failure into a reason. Amendment 36's round-2 rule names two ways of catching ("by that name or through `except Exception`"); I read those as the two the author thought of, and the rule's purpose covers any handler whose type is an ancestor of the exception. The outcome is still a refusal, so no number escapes. What is lost is the class of the failure and the name of the member, which is exactly what amendment 42 was written to keep.

### 7.2 S-2

`evaluate_member` runs while the campaign is still collecting. Text 12 scopes `run_campaign.py` to "its final analysis and whole-window verdict". The gate there is unruled behaviour, and it has three costs: the campaign stops at the first bad run and the night's remaining runs are never made; the bad run's provenance row is not written, so the record of what happened is lost; only the first bad run is named. A rule that stops a night is a separate ruled change (text 5 says so for the quiet-envelope collector, and the reason is the same here).

**Remove it.** The final analysis keeps its gate (`:8928`). The closing analysis of the speculative-decoding campaign gets its own (amendment 49 (e)).

---

## 8. Q5: R47-4

E10 confirms the seat's report. Amendment 47's classification rule makes a digest under a bundle-named key, in a file that is neither documentation nor parsed data and has no row in the classification table, stop the builder. Its test row R47-4 expects the same input to return a listed candidate.

**The classification rule governs.** Its stated reason applies with full force to a `.json` file that fails to parse: such a file "may be a citation source that nobody has classified", for example a manifest truncated by an interrupted write. Listing its digest as harmless would hide exactly the case the rule exists for. The row's expected result was my predecessor's error, not the rule's.

---

## 9. Q6: the remaining findings

Confirmed as test fixes for fix round 3, with no text change:

| Finding | What the fix round does |
|---|---|
| S-3, behavioural pins | One behavioural test per consumer at its production call site (the rows of amendments 49, 52 and 53 supply most). The import matcher also matches `from joulewise import battery_float`. Window-level outputs are asserted to show `unobserved_historical` for each consumer that writes one. |
| S-4 | A test **without** `_allow_unissued_fixture` in which discovery classifies an endpoint `pass` and the re-run sees `unobserved_historical`; expected `calibration_battery_float_disagreement`. Counterfactual: the equality clause at `calibration_bracketing.py:2341-2343` deleted (the Opus mutant T10-M1, which survives today). Read, not run. |
| S-5 | The pin test asserts every path of FT §E's excluded list, `joulewise/battery_float.py`, and the absence of `configs/battery_float/historical_captures.json`. All are byte-identical today (E12). |
| N-1, N-3, N-4 | Comment line number; the amendment-41 row's reason cites amendment 41; the self-test anchors at `1417c0c4` with `skipTest` when the commit is absent. |
| N-2 | Pin both constants to their sources and pin the `window_end_s == cutoff` case. If S1 is rebased before merge, both constants are re-derived, as text 10 already requires ("set at the S1 merge base"). |
| N-6 | Recorded in the pull request's body. No schema change is ruled. |
| N-8 | Pin the simulated-run behaviour directly. The dropped prompt-realization assertion returns in round F on a fixture that is not simulated. |
| N-9 | Information for the lead. No action in S1. |

Three exceptions, ruled above and not left to the seat:

- **S-3's member-set bullet** ("either widen them or obtain a ruling"): ruled by amendment 49 (f).
- **S-3's handler check** and **N-5** (handlers that round 2 narrowed without need): ruled by amendment 52.
- **N-7** (one-member gates inside helpers): they may stay, or be replaced by `behind_gate` rows under amendment 51, at the seat's choice, except the one in `evaluate_member`, which amendment 53 removes.

---

## 10. Amendments 49 to 54 (exact text; the fix-round brief quotes these)

Every test row names its production call site and the counterfactual under which it must fail. All new tests go in files already in S1's WRITE_SCOPE. No path is added to it.

### Amendment 49 (amends text 12, the `members` sentence; S1's existing scope: `scripts/run_campaign.py`, `joulewise/whole_window.py`, `joulewise/analysis_engine/inputs.py`, `tests/test_bfgs_window_consumers.py`)

49. **Window members include every quarantined bundle, and two kinds of consumer are told apart.**

**(a) Two kinds.** A **window consumer** is a function that works out a window's membership itself, from the campaign's manifests and logs. A **set consumer** is a function that is handed a list of bundles by name (the cells of a spec, the entries of a manifest, a list of member ids). The window consumers are exactly:

```text
scripts/run_campaign.py::_authenticate_whole_window_members   (whole-window verdict)
scripts/run_campaign.py::run_campaign                         (final analysis)
scripts/run_campaign.py::run_axi_spec_campaign                (closing analysis)
joulewise/whole_window.py::_derived_neg8_decision
joulewise/analysis_engine/inputs.py::load_analysis_inputs
```

Every other gate call in the eight consumers is a set consumer's.

**(b) The member list of a window consumer** is the union of:

1. every selected bundle path;
2. every copy of a member's bundle id present inside the runs directory (`present_paths`, or `ordinary_present_bundle_paths`);
3. for every selected bundle under `axi_attempt_bundles/<name>/`, every directory under that attempt root that holds `metadata.json`;
4. **for every valid supersession record of the window whose `bundle_id` is one of the window's member ids, the directory `Path(record["quarantine"]["path"])`.**

"Valid" means the record passes `validate_occurrence_supersession_entry`, which the three resolvers already call. `run_campaign` (final analysis) has no item 4: a supersession is recorded only after collection, by a separate command.

**(c) How the quarantined bundle is authenticated.**

- The path is passed **as recorded**, without `resolve()`. Resolving would follow a symlink and hide it.
- Its label is `superseded:<bundle_id>:<recorded path>`.
- It is passed to the gate **in the same call** as the other members, so that one refusal names every refused member.
- The consumer makes no check of its own before the call and catches nothing after it. A path that is missing, is not a directory, or is a symlink makes the gate raise `CustodyUnreadable` labelled with the member (executed, E4). A quarantined bundle is never skipped because it is absent: the record says it exists, so its absence is a custody failure.
- Its status is judged exactly as any member's. A quarantined bundle measured before the battery check and not among the 69 listed runs is `prospective bundle` and refuses the window. No exemption is granted here; admission of such a bundle is by cold gate, as text 8 says for every other.

**(d) `_derived_neg8_decision` and `load_analysis_inputs`** obtain the records through `supersession_entry_validation_results(runs_root, log_path)`, which both modules already import or define, and add item 4 for each record it reports valid.

**(e) The closing analysis of `run_axi_spec_campaign`** calls the gate once, over **every** value of `finalized_bundles` (selected and not), each labelled with the physical id the function already builds (`<entry>__a<ordinal>__<run_id>`), before `_idle_admission_core_evaluation` is called.

**(f) A set consumer** authenticates every bundle in the list it was handed, `FAILED` members included, and enumerates nothing else. The superseded runs of the window are the duty of the window's verdict. This is the reading of text 12's first sentence ("a set of bundles whose numbers are claimed") for a consumer that never sees a window. Residual, stated: `aggregate_experiment` binds no window verdict, so nothing shows it a superseded run. Its list is the repetitions of one experiment, where no supersession exists.

**Forcing fact for the record.** Seven supersession records exist on disk today. In all seven the selected and the quarantined bundle are both already refused as `prospective bundle` (E5). This amendment changes the outcome of no existing window.

**Test rows for amendment 49.** Fixtures: `WindowMembersTests.pair_bundle` builds a bundle with a passing pair, or with `charging=True` a charging pair.

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R49-1 | `_authenticate_whole_window_members` | the production shape: one selected bundle inside the runs directory, passing; `present_paths` holding that one path; a supersession whose quarantine path, outside the runs directory, holds a charging-pair bundle | `WindowBatteryRefusal` whose `members` is one entry, label beginning `superseded:`, status `battery_float_confounded` | the code at `49d77c74`, which returns one `pass` (E1) |
| R49-2 | same | as R49-1 with a passing quarantined bundle | two verdicts returned, both `pass`, one under the `superseded:` label | a rule that refuses whenever a supersession exists |
| R49-3 | same | as R49-2 with the quarantine directory deleted after the record is built | `type(exc) is CustodyUnreadable`; `exc.window_member` is the `superseded:` label | a helper that skips a quarantine path that is not a directory |
| R49-4 | same | the quarantine path is a symlink to a passing bundle | `CustodyUnreadable` | a helper that calls `resolve()` on the path |
| R49-5 | same | selected bundle prospective, quarantined bundle charging | one `WindowBatteryRefusal` naming **both** | two gate calls, one per kind of member |
| R49-6 | `run_whole_window_verdict` | a runs directory with a campaign log holding a supersession record written by `_run_record_supersession_locked`, quarantined bundle charging | the refusal propagates; **no verdict row is appended to the log** | the code at `49d77c74` |
| R49-7 | `load_analysis_inputs` | a manifest whose one ordinary member has a valid supersession, quarantined bundle charging | `WindowBatteryRefusal` naming the `superseded:` label | the code at `49d77c74` |
| R49-8 | `_derived_neg8_decision` | same shape | same | the code at `49d77c74` |
| R49-9 | `run_axi_spec_campaign`, closing analysis | two finalized attempts of one entry: attempt 1 not eligible with a charging pair, attempt 2 selected and passing | `WindowBatteryRefusal` naming attempt 1's physical id; no whole-window verdict row written | a gate over selected runs only |

The existing test with two `present_paths` stays (it pins item 2) and its docstring says that it is not the supersession case.

### Amendment 50 (amends text 9, the sentences on the entry, the marker and the refusals; S1's existing scope: `joulewise/scored_reduce.py`, `tests/test_scored_reduce.py`)

50. **Every started placement owes a verdict; the marker is admitted for no status.**

**(a) The entry.** For every key in the key set (every placement whose status is `completed` or `cut_off`), the entry is a `PairVerdict` of kind `bundle` whose `bundle_sha256` is 64 hexadecimal characters.

**(b) Binding.**
- Where a capture window exists for the key, `bundle_sha256` must equal that window's `bundle_sha256`.
- Where none exists, `bundle_sha256` must differ from every capture window's `bundle_sha256` and from every other entry's `bundle_sha256`.
- A failure of either is `battery_evidence_unbound`.

**(c) The marker.** An entry of the form `{"no_bundle": <anything>}` is refused with `battery_evidence_unbound`, for every status. The form stays recognised so that it is refused under that code and not as a malformed input. It can be admitted later only by a cold gate that names the roster field recording that a placement finalized no bundle. No such field exists (`scored_packer.py:237, :402`).

**(d) Order, and which code is reported.** Shape, duplicates and the two key-set checks first, as today. Then binding for every entry. Then status for every entry: if any entry is `battery_float_confounded` the code is `battery_float_confounded`; otherwise, if any is not `pass`, the code is `battery_float_evidence_missing`. The refusal's detail lists **every** key whose status is not `pass`, with its status, in placement order. All of this precedes `_check_window`, as text 9 rules.

**(e) Outcome for each (placement status × evidence form).**

| Roster status | Capture window | Evidence supplied | Outcome |
|---|---|---|---|
| `not_started` | any | none | accepted (the key is outside the key set) |
| `not_started` | any | any entry | `battery_evidence_unbound` |
| `completed` or `cut_off` | any | none | `battery_evidence_missing` |
| `completed` or `cut_off` | any | the marker, any value | `battery_evidence_unbound` |
| `completed` or `cut_off` | any | anything that is not a bundle-kind verdict with a 64-hex digest | `battery_evidence_input` |
| `completed` or `cut_off` | exists | verdict whose digest differs from the window's | `battery_evidence_unbound` |
| `completed` or `cut_off` | none | verdict whose digest equals a window's or another entry's | `battery_evidence_unbound` |
| `completed` or `cut_off` | either | bound verdict, `pass` | accepted |
| `completed` or `cut_off` | either | bound verdict, `battery_float_confounded` | `battery_float_confounded` |
| `completed` or `cut_off` | either | bound verdict, `battery_float_evidence_missing`, `unobserved_historical` or `not_applicable` | `battery_float_evidence_missing` |

The placement's class (live, terminal, voided) changes no row.

**(f) Two consequences, stated.**
- A run killed before it wrote a bundle has no verdict to supply, so the reduction refuses with `battery_evidence_missing`. This is recorded under lane SCORED-CEILING-BATTERY-01 as a campaign-cost question.
- **Residual.** For a placement without a capture window the reducer has nothing to check the digest against. Rule (b) stops one verdict from being used for two placements; it cannot show that the verdict belongs to this placement's bundle. That binding is the duty of the harvest step that produces the evidence. The ruling that lands the real producer must either give the reducer the harvest's list of member digests keyed by placement, or say why not. Until then `reduce` has no production caller (text 9).

**(g) The fixture producer** in `tests/test_scored_reduce.py` supplies, for a started placement without a window, a verdict whose digest is `sha256(repr((block_id, attempt, "no-window")))`.

**Test rows for amendment 50.** Production call site for all: `scored_reduce.reduce`. Fixture: `_terminal_night(width=2, kind="ceiling_violation")`; placement V = `('large:decode:1:0', 0)` (voided, `cut_off`, no window).

| Row | Input | Expected code | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R50-1 | V carries a charging verdict with a fresh digest | `battery_float_confounded` | the code at `49d77c74`, which refuses `battery_evidence_unbound` (E2) |
| R50-2 | V carries a passing verdict with a fresh digest | the reduction returns | the code at `49d77c74` |
| R50-3 | V carries `{"no_bundle": "cut_off"}` | `battery_evidence_unbound` | the code at `49d77c74`, which returns a reduction (E2) |
| R50-4 | a voided `completed` placement carries `{"no_bundle": "completed"}` | `battery_evidence_unbound` | the code at `49d77c74` |
| R50-5 | V carries a passing verdict whose digest is another placement's window digest | `battery_evidence_unbound` | a rule that accepts any 64-hex digest where no window exists |
| R50-6 | two placements without windows carry one digest | `battery_evidence_unbound` | same |
| R50-7 | an earlier placement carries `battery_float_evidence_missing`, a later one a charging verdict | `battery_float_confounded`; the detail names both keys | a rule that reports the first non-pass entry in order |
| R50-8 | the fixture producer's output for the fixture night | it holds no marker; the key set equals text 9's expression | the producer at `49d77c74`, which emits five markers |

`test_complete_placement_universe_and_no_bundle_vocabulary` is rewritten to R50-8. Its assertion `set(markers) <= {"completed", "cut_off"}` is removed because this amendment supersedes the sentence it pinned; the report names it under F-4's form (old expectation, new expectation, ruled sentence).

### Amendment 51 (amends text 12, the sweep sentence and the allowlist sentence; replaces amendment 26's clause "the sweep matches the function name and `BundleReader.metadata()`"; S1's existing scope: `tests/test_bfgs_consumer_sweep.py`)

51. **The sweep follows the path, checks the order of the gate, and checks its own `behind_gate` rows.**

**(a) Terms.**
- A **watched name** is one of `summary_metrics.json`, `metadata.json`, `power_trace.csv`.
- A **watched constant** is a string constant that equals a watched name or ends with `/` followed by one.
- A **module constant** is a name assigned at the top level of any tracked file under `joulewise/` or `scripts/` from a path expression (below). Module constants are collected over all those files first and matched by name, so a constant imported from another module is recognised.
- A **path expression** is any of: a watched constant; a name that is a module constant or a path name of the function; an attribute whose name is an upper-case module constant; a `/` operation either of whose sides is a path expression; a tuple, list or set literal any of whose elements is a path expression; a call to a **path builder** any of whose arguments, or whose receiver, is a path expression.
- The **path builders** are `Path`, `PurePath`, `PurePosixPath`, `join`, `joinpath`, `str`, `fspath`, `with_name`, `with_suffix`, `resolve`, `absolute`, `expanduser`, `parent`, `glob`, `rglob`, `iterdir`. They return a path, never a file's content.
- A **path name** of a function is a name bound in that function (by assignment, annotated assignment, `:=`, a `for` target, or a comprehension target) from a path expression. Binding is repeated until no new name is added. A name bound from any other call is **not** a path name: it holds content, not a path.
- The **non-reading calls** are a constant list in the test of callee names that cannot return a file's content (`is_file`, `exists`, `is_dir`, `is_symlink`, `relative_to`, `as_posix`, `lstat`, `stat`, `unlink`, `rename`, `mkdir`, `write_text`, `write_bytes`, `append`, `add`, `print`, `add_argument`, the built-in container and string functions, and exception constructors). The seat may extend the list only with names of that kind; the refuter checks each entry.

**(b) A read site** is, inside one function (nested functions and methods are swept separately and inherit nothing):
1. any call of `raw_metadata`, `raw_config`, `raw_summary` or `raw_artifact_bytes` on any receiver; or
2. any call that is neither a path builder, nor a non-reading call, nor a gate call, and whose receiver or any argument (positional or keyword) is a path expression; or
3. any assignment of a path expression to an attribute or a subscript (`self.trace = bundle / "power_trace.csv"`), reported as operation `store:<target text>`, because the read then happens in another function through a value the sweep cannot follow.

Under item 2, handing a path to a helper (`read_support_intervals(bundle / "power_trace.csv")`) is a read site **in the caller**, where the watched name enters. The helper, which sees only a parameter, is not reported.

**(c) A gate call** is:
- a call of `authenticate_window_members`, by bare name or as an attribute, in a module that imports that name from `joulewise.bundle_read` or imports that module, or in `joulewise/bundle_read.py` itself; or
- a call `X.metadata()` where `X` is a call of `BundleReader`, a name bound in the function from a call of `BundleReader`, a parameter whose annotation names `BundleReader`, or `self` inside the class `BundleReader`.

No other `.metadata()` call is a gate.

**(d) A read site is gated** only if some gate call of the same function (i) comes before it in source order (line, then column) and (ii) **dominates** it: every `if`, `for`, `while`, `match`, `except`, `else`, `finally` branch, conditional expression, or right-hand operand of `and`/`or` that encloses the gate call also encloses the read site. The body of a `try` and the body of a `with` do not count as branches. A read site that is not gated is **reported** as `(path, qualified function, operation, watched name, line)`.

**(e) The site-specific clause for `scripts/issue_dg071_dg075_statistics.py` is deleted.** Under (b) the script is reported at `main`, operation `direct:issue_artifacts`, watched name `power_trace.csv` (executed, E8), which is where the pinned path is named and handed to the reader. That report is the witness amendment 41's round-2 note requires. Its row is class `historical` and its reason cites amendment 41.

**(f) The allowlist.** The key is `(path, qualified function, operation, watched name)`; for the four tolerant accessors the watched name is `-`. The set of reported keys must **equal** the set of allowlist keys. Each row carries a class and a reason, and a `behind_gate` row carries a third field.

| Class | A row may carry it only if | The reason must state |
|---|---|---|
| `strict_validation` | every value the function returns or writes is a digest, a boolean, an identity string, or a list of problem strings | what is validated |
| `non_claim` | (i) no field the function reads from the file is an energy, power, current, charge or voltage value or is computed from one; **or** (ii) nothing the function returns or writes is consumed by a claim artifact | which of (i), (ii); for (i) the fields read; for (ii) where the output goes |
| `historical` | the function reads energy values from bundles measured before the battery check, and cannot be pointed at a later bundle: it pins what it reads by digest in committed code, or reads only a corpus that a committed artifact names | the pin or the corpus |
| `behind_gate` | the function is reached only after a gate, in one of the two forms below | nothing beyond the third field |

A **claim artifact** is a file a paper number is taken from or licensed by: a floor artifact, a whole-window verdict row, an analysis output, a fill of the paper's results registry, a figure.

**`behind_gate`, two forms, both checked by the sweep:**
- **Callers form.** Third field `callers`: a tuple of `path::qualified function`. The sweep asserts that every call of the helper's name (bare or as an attribute) in any tracked file under `joulewise/` or `scripts/` lies in a listed function, and that in each listed function either a gate call comes before and dominates that call, or the listed function itself has a `behind_gate` row. A chain that returns to a function already visited fails.
- **Consumers form**, for a function that runs during collection and whose result is used only later. Third field `consumers`: a tuple of (`path::qualified function`, name of the consuming call). The sweep asserts that in each named function a gate call comes before and dominates **every** call of the named consuming function.

**(g) Which sites may be exempted and which must be gated.**
1. A read site inside one of the eight consumer modules whose function returns, or passes on, a value from the file that includes an energy, power, current, charge or voltage value is **gated in the function or `behind_gate`**. It may carry no other class. `floor_extraction._read_summary` is such a site (it returns the parsed summary): its row is `behind_gate`, callers form.
2. The rows of `joulewise/whole_window.py` that today carry `strict_validation` with the reason "called behind the window gate" are re-classed: `behind_gate` where the function returns content, `strict_validation` where it returns only digests, booleans, identities or problems.
3. `scripts/run_campaign.py::evaluate_member` carries `behind_gate`, consumers form, with `consumers = (("scripts/run_campaign.py::run_campaign", "classify_campaign_members"), ("scripts/run_campaign.py::run_axi_spec_campaign", "_idle_admission_core_evaluation"))`.
4. `historical` is held by the eight rows that hold it at `49d77c74` (two in `envelope_gate.py`, five in `make_figures.py`, one in `issue_dg071_dg075_statistics.py`), re-keyed to the new key form, each checked by the refuter against the class's condition. A reported site in one of those same three files may take `historical` on the same ground. **Any other new `historical` row needs a cold gate.**
5. `scripts/paper_prefill_resolvability_projection.py::scan_corpora` (four reported sites, E8) is `non_claim` under (i). I read `read_support_intervals` (`:181-197`): it reads `timestamp_s`, `interval_start_s` and `interval_end_s` and nothing else. The seat states the fields read by `read_model` and `recorded_label` in their rows; if either reads an energy value the site is returned to the lead.
6. Every other reported site is classed by the seat under the table's conditions, and **the refuter checks every row**, as text 12 already requires. A site that fits no class is gated, or returned.

**(h) What the sweep cannot see, stated.** A read that never names the file: a loop over a directory listing, a copy of a whole directory, a digest of a whole bundle. A path that reaches a function inside an object the sweep did not see stored. Calls are matched by name, so two helpers of one name are treated as one.

**Test rows for amendment 51.** Each self-test calls the test module's `sweep_source` on a source string as file `joulewise/zz_new.py`; R51-14 onward run the sweep over the tracked tree. Sources K1 to K10 and G1 to G3 are those of `/tmp/cg_r2/sweep49_cases.py`, reproduced here in words.

| Row | Source | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R51-1 (K1) | the read `(b / "power_trace.csv").read_bytes()` | reported | none (pins the case that works today) |
| R51-2 (K2) | the path assigned to a name, then `name.read_bytes()` | reported | the detector at `49d77c74` (E1: `assigned []`) |
| R51-3 (K3) | the watched name in a module constant | reported | the detector at `49d77c74` |
| R51-4 (K4) | `open_authentication_input(b / "power_trace.csv", …)` | reported | the detector at `49d77c74` |
| R51-5 (K5) | `event.metadata()` on a parameter of no declared type, then a read | reported | a rule that takes any `.metadata()` call as the gate |
| R51-6 (K6) | the read first, the gate after it | reported | a rule that accepts a gate anywhere in the function (E1: `read_before_gate []`) |
| R51-7 (K7) | the gate inside `if b.is_dir():`, the read after the `if` | reported | a rule that checks order and not dominance |
| R51-8 (K8) | the path handed to a helper | reported as `direct:helper` | a rule with a fixed list of read functions |
| R51-9 (K9) | `for name, field in (("config.json","c"), ("metadata.json","m")):` then `(b / name).read_bytes()` | reported, watched name `metadata.json` | a rule that binds names only by assignment |
| R51-10 (K10) | a local function named `authenticate_window_members`, not imported from the reader module, called before a read | reported | a rule that matches the gate by name alone |
| R51-11 (G1 to G3) | the gate first then the read; `BundleReader(b).metadata()` then `raw_summary()`; gate and read inside the same `if` | not reported | a rule that reports every read |
| R51-12 | a store to an attribute: `self.trace = b / "power_trace.csv"` | reported as `store:self.trace` | a rule without item (b) 3. **NOT EXECUTED in my prototype.** |
| R51-13 | `joulewise/cli.py` from `git show 1417c0c4:` | the `raw_metadata` read at line 423 is reported; `skipTest` if the commit is absent | the anchor `b859317c` |
| R51-14 | the tracked tree | reported keys equal allowlist keys; every class is one of the four; every reason is non-empty | an allowlist row removed, or a row added for a site that does not exist |
| R51-15 | the tracked tree with the amendment-41 row removed | the sweep fails naming `scripts/issue_dg071_dg075_statistics.py`, `main` | the site-specific clause kept |
| R51-16 | a `behind_gate` row, callers form, and a new call of the helper added in an unlisted function | the sweep fails naming the unlisted caller | a `behind_gate` row that is not checked |
| R51-17 | the consumers-form row of `evaluate_member`, with the gate at `run_campaign` (final analysis) deleted | the sweep fails | a row that is not checked. This kills the Opus mutant M5, which survives every test today. |

**Size, measured on my prototype (E7), so the seat can tell a wrong implementation from a right one:** 120 rows over 89 functions at `49d77c74`, without item (b) 3. A count far from this is a finding to return, not to explain away. The prototype is scratch, not authority; the text above is.

### Amendment 52 (amends amendment 36's round-2 rule, third sentence; S1's existing scope: `joulewise/bundle_read.py`, the eight consumer modules, `tests/test_bfgs_window_consumers.py`, `tests/test_bfgs_consumer_sweep.py`)

52. **No handler in a consumer can swallow the gate's exceptions.**

**(a)** Amendment 36's sentence "They do not catch `CustodyFailure`, by that name or through `except Exception`" is replaced by: "No handler in the eight consumer modules changes, replaces or discards a `CustodyFailure` or a `WindowBatteryRefusal`, whatever exception type the handler names."

**(b)** `joulewise/bundle_read.py` gains the module constant `GATE_EXCEPTIONS = (WindowBatteryRefusal, battery_float.CustodyFailure)`. The consumers import it from `bundle_read`. They still do not import `battery_float`.

**(c)** A **broad handler** is one whose caught types include `RuntimeError`, `Exception` or `BaseException`, or that names no type. In the eight consumer modules, every `try` statement that has a broad handler has, **before** it, the handler

```python
except GATE_EXCEPTIONS:
    raise
```

whose body is that one statement. This is not a catch within the meaning of (a): the same object leaves, unchanged. The one exception: a broad handler whose own last statement is a bare `raise` (the lock-release handlers) needs no such clause.

**(d)** Every handler that round 2 narrowed from `except Exception` to a tuple of types returns to the types it caught at `1417c0c4`, with the clause of (c) before it. The narrowing made exception classes outside the tuple crash where base produced a structured refusal (Opus N-5); with (c) in place it is not needed.

**(e)** Handlers that name `BundleReadError` are untouched. A battery refusal raised by `BundleReader.metadata()` is a `BundleReadError` to its callers by amendment 42 (a), which ruled that "every existing caller of `metadata()` behaves as before".

**(f)** If the guard suite (`tests/test_battery_float_consumers.py`) goes red on (b) or (c), the seat stops and returns NEEDS_RULING. No guard row is granted here. NOT EXECUTED by me.

**Test rows for amendment 52.**

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R52-1 | `inputs.bind_floor_artifact_evidence` | a salvage component one of whose members has its `raw/battery_float.post.ioreg` deleted after finalization | `type(exc) is CustodyFailure`; `exc.window_member` is the member's label | the code at `49d77c74`, which returns the problem string `whole_window_verdict_provenance_invalid` |
| R52-2 | same | the member carries a charging pair | `WindowBatteryRefusal` naming the member | the code at `49d77c74` |
| R52-3 | same | the component's validation raises a `RuntimeError` that is not a gate exception | the problem string, as at base | a fix that removes `RuntimeError` from the handler's tuple |
| R52-4 | the eight modules, by syntax tree | the tracked files | every `try` with a broad handler has the clause of (c) before it, or the handler ends in a bare `raise` | the Opus mutants M4b (the gate in `mint_floor_artifact._strict_bundle` wrapped and re-raised as `MintError`) and M4c (`except RuntimeError` around the gate in `extract_cells`), both of which survive today |
| R52-5 | the eight modules, by syntax tree | the tracked files, plus the source `from joulewise import battery_float` inserted in `aggregate.py` | the import test fails | the matcher at `49d77c74` (the Opus mutant M7, which survives) |

Size, measured (E9): 19 handlers name `RuntimeError` and 15 name `BaseException`, of which 12 already re-raise. About 22 `try` statements gain the clause.

### Amendment 53 (amends text 12's scope sentence for `run_campaign.py`; S1's existing scope: `scripts/run_campaign.py`, `tests/test_bfgs_window_consumers.py`)

53. **No gate during collection.**

**(a)** The gate call in `evaluate_member` (`run_campaign.py:2801-2802`) is removed. `evaluate_member` decides nothing about battery state and refuses nothing on it.

**(b)** The gate of `run_campaign`'s final analysis (`:8928`) stays where it is: after the collection loop, before `classify_campaign_members`, over every evaluated member whose bundle directory exists.

**(c)** The closing analysis of `run_axi_spec_campaign` is gated by amendment 49 (e).

**(d)** Collection therefore runs to its end whatever the battery readings show, every run's provenance row is written, and the refusal at the closing analysis names every refused run. A rule that stops a night early on a battery reading, if ever wanted, is a separate ruled change.

**(e) Flagged for the lead, not ruled.** Text 12 refuses `not_applicable`, so the final analysis of a campaign made only of simulated runs raises. With the collection-time gate removed this happens after collection, and names every run, where at `49d77c74` it happens at the first run. Tests that drive a simulated campaign through its final analysis will meet that refusal in round F. Whether the final analysis of an all-simulated campaign should refuse is text 12's existing ruling; I leave it as it stands.

**Test rows for amendment 53.**

| Row | Production call site | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|---|
| R53-1 | `run_campaign` | three members; the second carries a charging pair; the third has no battery record and is not among the listed runs | all three runs are collected and all three provenance rows are written; then `WindowBatteryRefusal` naming the second as `battery_float_confounded` and the third as `battery_float_evidence_missing` | the code at `49d77c74`, which raises at the second member, names one, and writes no row for it |
| R53-2 | `run_campaign` | as R53-1 | no campaign verdict row is written | the final-analysis gate deleted (the Opus mutant M5) |
| R53-3 | `evaluate_member` | a bundle directory with a charging pair | returns a `MemberEvaluation`; raises nothing | the code at `49d77c74` |

### Amendment 54 (amends amendment 47, test row R47-4; S1's existing scope: `tests/test_bundle_read.py`)

54. **R47-4 follows the classification rule.** Amendment 47's text is unchanged. Its test row R47-4 is replaced by the two rows below. The builder at `49d77c74` already behaves as they require (E10); only the build-level test is owed.

| Row | Input | Expected | Must fail (RED) under this counterfactual |
|---|---|---|---|
| R47-4 | `broken.json` that fails to parse and holds the line `bundle_tree_sha256: ` followed by 64 `a` characters, with no classification row | stderr names the file as `unparseable broken.json`; then `ValueError` matching `unclassified candidate pair`, naming the key `bundle_tree_sha256` and the file `broken.json` | (1) the `continue` of `b859317c`, which skips the file and returns `([], [])`; (2) a rule that classes a candidate in an unparseable `.json` file as `quoted` |
| R47-4b | `broken.json` that fails to parse and holds 64 `a` characters on a line with no key token | stderr names the file as unparseable; `build` returns no entry and no listed candidate; nothing is raised | a rule that raises on every unparseable `.json` file |

The seat's existing scan-level test (`_candidates` yields the candidate and names the file) stays.

---

## 11. Kept intact

- **Custody is never a status.** Amendment 49 adds a member and no status: a quarantined bundle that cannot be read raises through the gate's existing custody path (E4). Amendment 52 removes the one place found where a custody failure became a reason string. Amendment 50 adds no status to the reducer; its codes are text 9's.
- **Authentication precedes every exclusion decision.** Amendment 53 moves no exclusion ahead of authentication: `evaluate_member` excludes nothing on battery grounds, and both closing analyses gate before they classify. Amendment 50 checks every entry before any window is interpreted.
- **`joulewise/battery_float.py` is byte-identical** to `1417c0c4` (E12, SHA-256 prefix `4b4d7bb20625`). No amendment here touches it. `GATE_EXCEPTIONS` lives in `bundle_read.py`.
- **FT §E's excluded list is byte-identical** (E12), and no amendment here names a path on it. `scripts/paper_prefill_resolvability_projection.py` and `joulewise/scored_packer.py` are also unchanged from base and stay so: the first gets an allowlist row, not an edit; the second is why the marker cannot be admitted.
- **The eight consumers do not import `battery_float`** (E12), and amendment 52 (b) is written so that they need not.
- **The historical set's 69 entries, bytes and pin are unchanged** (E11).

---

## 12. Not executed

- The full S1 module suite (V1, 416 tests, about 26 minutes per the seat) and V2, V3. I ran 23 focused tests (E13).
- Any code written to amendments 49, 50, 52 or 53. I ruled from probes of the code as it stands.
- The closing analysis of `run_axi_spec_campaign`, `_derived_neg8_decision` and `load_analysis_inputs` with a supersession present. Their omission is established by reading (§4.3), not by a run.
- Item (b) 3 of amendment 51 (stores to attributes), and both `behind_gate` checks. My prototype implements (a), (b) 1 and 2, (c) and (d).
- A classification of the 120 reported rows. I inspected `floor_extraction._read_summary`, `read_support_intervals`, the amendment-41 site, `evaluate_member` and the supersession readers. The rest is the seat's work and the refuter's check.
- The guard suite under amendment 52 (f).
- The Opus lens's mutants. I rely on its report for which survive, and say so at each row that cites one.
- Whether the gate refuses a symlink in a **parent** component of a member's path. E4 tested a symlink as the member's own directory.
- The 200-night differential test of the scored reducer, which the Sol lens reported as interrupted.

---

## 13. Probes written in this session

| File | Purpose |
|---|---|
| `/tmp/cg_r2/gates.py` | E3 |
| `/tmp/cg_r2/b2.py` | E2 |
| `/tmp/cg_r2/q1.py` | E4 |
| `/tmp/cg_r2/q1_disk.py` | E5 |
| `/tmp/cg_r2/handlers.py` | E9 |
| `/tmp/cg_r2/r47.py` | E10 |
| `/tmp/cg_r2/sweep49.py` | E7: prototype detector for amendment 51 |
| `/tmp/cg_r2/sweep49_cases.py`, `/tmp/cg_r2/sweep49.out` | E8, and the full list of reported rows |

Re-run from the lenses' scratch: `/tmp/bfgs_execution_probe.py` (E1), `/tmp/opus_sweep2.py` (E6).

---

## 14. The S1 order of remaining work

| Step | Round | Contents | Ends with |
|---|---|---|---|
| 1 | **Fix round 3** (one seat, S1's existing WRITE_SCOPE, no path added) | In this order, because each later item inventories the code the earlier ones change: **(i)** amendment 54 (two test rows); **(ii)** amendment 50 (reducer and its fixture producer); **(iii)** amendments 53 and 49 together (the gates of `run_campaign.py`, then the member lists of the three resolvers); **(iv)** amendment 52 (`GATE_EXCEPTIONS`, the pass-through clause, the handlers restored to their base types); **(v)** amendment 51 (the detector, the re-keyed allowlist, the classification of every reported row), last among production-facing work; **(vi)** the test fixes of §9 (S-3, S-4, S-5, N-1 to N-4, N-8). | every row R47-4 to R53-3 shown RED under its counterfactual and GREEN after; V1 and V2 green; the builder's forward check `byte-identical entries=69`; the count of reported sweep rows stated; the allowlist listed in the report with class and reason per row |
| 2 | **Delta lenses on fix round 3** | two lenses with distinct methods, as for round 2. The contract lens checks **every allowlist row** against amendment 51 (f) and (g), and re-runs the Opus mutants M4b, M4c, M5, M5d, M7 and T10-M1, all of which must now be killed. | findings, or none |
| 3 | **Round F** | amendment 38, unchanged: the fourteen test files, remedies R1 to R3. Two notes from this ruling: fixtures that drive a simulated campaign through its final analysis meet the refusal of amendment 53 (e); fixtures of the scored reducer use amendment 50 (g). | the full suite green except the four cases that fail at base; the F-6 counterfactuals and the F-7 partition |
| 4 | **Last commit** | the supply-map receipt clause of amendment 38 | the generator command and the diff pasted |

Early returns, as before: a text here that conflicts with the code, or a guard that goes red under amendment 52, is returned as NEEDS_RULING with the independent work finished first.

---

## 15. Plain summary for Ed (5 lines)

1. **Both reviewers' blockers are real and all are upheld; none lets a wrong number out today.** The work under review ("S1 round 2") wires a battery check into every program that turns measured runs into claimed energy numbers: a run counts only if readings taken before and after it show the laptop battery neither charging nor discharging.
2. **A re-done run's first attempt was escaping the check ("amendment 49", the new rule for which runs belong to a measurement session).** When a run is repeated, the first attempt's folder is moved aside and recorded; the check never looked there, so a first attempt made while charging left the session looking clean. It is now checked with the rest, in four programs. All seven such folders on disk are already refused for another reason, so no existing result changes.
3. **The scoring program accepted "there is no evidence" in place of evidence ("amendment 50").** For a test block that started and was stopped, it rejected a real battery result and accepted a note saying no run folder existed, for every block that had in fact run. The note is now refused always, because the schedule file records nothing that could justify it; every block that ran must bring its battery result.
4. **The automatic search for unchecked file reads was blind to the ordinary way of writing one ("amendment 51").** It missed a file path held in a variable, and accepted a check placed after the read. It now follows the path, requires the check to come first, and verifies by itself any exemption that says "my caller already checked". I built a trial version: it catches all ten test cases and lists 120 places to classify, against 65 today.
5. **Three smaller rulings.** A program that caught a "files damaged" error and replaced it with a vague message must now let it through unchanged ("amendment 52"); the battery check no longer stops a night of collection at the first bad run, and instead refuses at the end, naming every bad run ("amendment 53"); and where a rule and its own test row contradicted each other, the stricter rule stands and the test row is corrected ("amendment 54"). Next: one fix round, a review of it, then the repair of older test fixtures.
