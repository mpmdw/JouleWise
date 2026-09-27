# Cold gate BFGS-S1-SCOPE-01, erratum ruling (Fable 5.1, cold judge): SF-1 to SF-6 and N-1 to N-3 against amendments 36–41

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one foreground session, no subagents, no background tasks. Worktree `JouleWise-wt-s1cg-92472459`, detached at `24b79db349706c9945ce42789b1be862a4400edc` (`git rev-parse HEAD`; `git status --short` empty at start and after the last probe). The charge is the file `30-erratum/00-charge.md`, committed at `8e2719e0` (commit present, subject read). Base tree: `git archive 1417c0c4 | tar -x -C /tmp/s1err/base`. Session 2026-09-26. No `sudo`, `launchctl`, `powermetrics`, installer, inference or live `ioreg`. Only this file was written to a repository path; every probe and scratch copy lives under `/tmp/s1err/`. No repository file was edited.

Vocabulary, defined once and used throughout:

- **Bundle**: one directory holding one measured run (its `config.json`, `metadata.json`, the event log `events.jsonl`, the power trace, raw instrument files).
- **S1**: the pull request that records two battery readings around every measured run and makes the bundle reader refuse bundles that lack them.
- **The pair**: those two readings, one before the measured span (`pre`) and one after (`post`), stored under the `battery_float` key of `metadata.json`, with the raw instrument output kept at `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`. A pair **passes** when both readings show the battery floating: neither charging nor discharging into the measurement.
- **The span**: the interval the pair must enclose. Its start is the monotonic-clock stamp on the event "stage `idle_baseline` started"; its end is the stamp on the event "stage `idle_drift_sentinel` completed". The `pre` reading must finish before the start and the `post` reading must begin after the end.
- **The reader**: `joulewise/bundle_read.py::BundleReader`. Its method `metadata()` is the gate: it admits a bundle in one of three states and raises otherwise.
- **The three admitted states**: (i) the bundle carries a pair that passes; (ii) the bundle carries no `battery_float` key and its digest is in the historical set, in which case it is labelled `unobserved_historical` (battery state was never recorded); (iii) the bundle is a simulated run (backend `mock`), labelled `not_applicable`.
- **The MOCK marker**: the exact value `{"pre": null, "post": null, "not_applicable": "mock"}` that the S1 controller writes under the `battery_float` key of a simulated run.
- **The historical set**: the committed file `configs/battery_float/historical_bundles.json`, a closed list of digests of bundles measured before the battery check existed. Its bytes are pinned by the constant `HISTORICAL_BUNDLE_SET_SHA256` in `bundle_read.py`.
- **Complete-bundle digest** and **tree digest**: two SHA-256 folds over the same inventory of a bundle directory (every regular file's relative path, byte hash and size). They differ only in how the inventory rows are serialised before hashing, so neither can be computed from the other without the files.
- **Prospective bundle**: a bundle with no pair that is not in the historical set and is not a simulated run. The reader refuses it with the message `battery_float_evidence_missing: prospective bundle`.
- **Status** versus **custody**: a *status* is a statement about the battery evidence (`pass`, `battery_float_confounded` meaning the readings show charging or discharging, `battery_float_evidence_missing` meaning a reading is absent or unusable, `not_applicable`, `unobserved_historical`). A *custody failure* (exception class `battery_float.CustodyFailure`, with subclass `CustodyUnreadable`) means recorded bytes are absent, altered or unreadable; it is never a status and it stops the whole computation.
- **The window gate**: `bundle_read.authenticate_window_members(members)`, which classifies every bundle of a measurement window before any energy is read, and refuses the whole window if any member is not acceptable. The exception it raises for status refusals is `WindowBatteryRefusal`.
- **The guard**: the test file `tests/test_battery_float_consumers.py`, which parses every production module that imports `joulewise.battery_float` and fails on any call that could forge a battery verdict, including any `dataclasses.replace(...)` call not on an exact allowlist.
- **WRITE_SCOPE**: the exhaustive list of paths a seat (a delegated model session) may edit.
- **Fix round, round 2, round F**: three successive work rounds on the S1 branch. The fix round repairs S1's own production code; round 2 wires the window gate into eight consumer modules; round F repairs test fixtures in other test files.

## 0. Contamination disclosure

Loaded by the harness without my choosing, before my first action: the user's global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers, including checkpoint titles; one of them states that S0 merged as pull request 429, which the charge also states). A system reminder supplied the git status and five recent commit subjects, and the tool and skill listings. None of these lines states a position on any of the nine findings. I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `CLAUDE.local.md`, no `AGENTS.md`, no decision log and no skill file. The base-tree extraction under `/tmp/s1err/base` contains copies of such files; one `ls | head -5` printed the names `AGENTS.md` and `CLAUDE.md`; their contents were not read. My whole-tree digest scans read every tracked base file mechanically for 64-character hex strings and printed only file names and counts.

Read by me: the erratum charge; the original charge; the ruling under review in full; the refuter's report in full; the Astra execution seat's report in full; text 7, text 8, text 12, §E and §F of Final texts v1.1; amendments 24, 25, 26 (both versions) and 31 (erratum version) and finding R-5 of the earlier erratum. I did not read the triage report, the seat brief or the seat report. Code read: `joulewise/bundle_read.py:180-470`, `joulewise/battery_float.py:55-85, 1020-1065`, `joulewise/interfaces.py:420-445`, the S1 diff of `joulewise/controller.py` and `tests/test_controller.py`, and the fixture constructors named under Executed evidence. I used one file the refuter produced, `/tmp/opusref-alldigests.json` (its map of on-disk bundle to complete digest), and then recomputed all 1402 of its values myself (X10).

## 1. Executed evidence (this session; every probe in the foreground)

All probes ran with `PYTHONDONTWRITEBYTECODE=1` and `TMPDIR=/tmp`. Scripts: `/tmp/s1err/probe_sf.py`, `/tmp/s1err/tree_sweep.py`; the rest were inline. "Head" is the real worktree at `24b79db3`. "Scratch" is `/tmp/s1err/head`, a `git archive` copy of head in which I applied a trial implementation of amendments 37 and 42 to `bundle_read.py` to learn what they break; nothing in it is proposed as the seat's code.

| # | Probe | Observed |
|---|---|---|
| X1 | **SF-1.** A simulated run built by the head controller (`run_benchmark` on the test suite's MOCK config), its `metadata.run_id` and `metadata.config_sha256` overwritten with a frozen legacy identity as `tests/test_cli_run.py:500-507` does; `bundle_read._historical_bundles` patched to return the production set plus the bundle's own complete digest | The controller wrote the MOCK marker. With the key present and the set patched: **refused**, `config.json digest does not match metadata.config_sha256`. With the key deleted, the digest recomputed and the set patched: **admitted**, `unobserved_historical`. With the key deleted and no patch: refused. `_historical_bundles()` returns a bare `frozenset` of 13. |
| X2 | **SF-1, second shape.** A non-simulated run (backend `powermetrics`, injected battery runner answering with the committed floating capture), then the same identity overwrite, as `tests/test_audit_amplification.py:154-161` does | Before the overwrite the reader returns `pass`. After it: refused, `battery_float_evidence_missing: pre evidence missing: session identity mismatch; post evidence missing: session identity mismatch`. The pair binds the run id, so rewriting the run id breaks the pair. With the key deleted and the set patched (raw battery files kept or deleted, both tried): admitted `unobserved_historical`; no strict-validation problem names a battery file. |
| X3 | **SF-3.** Two copies of the tracked fixture `tests/fixtures/d078_r01`, one byte appended to each `power_trace.csv` (so neither digest is in the set), passed to the window gate as members A and B | Each alone at the reader: `BundleReadError`, `battery_float_evidence_missing: prospective bundle`. Through the gate: **`CustodyUnreadable`** (a `CustodyFailure` subclass) with message `A: battery_float_evidence_missing: prospective bundle`; **B is not named**. A window of a charging-pair member `c1` followed by prospective `A` raises the same `CustodyUnreadable` naming only `A`: the confounded member is hidden. A window of `c1` alone raises `WindowBatteryRefusal` correctly. |
| X4 | **SF-4.** A passing non-simulated bundle, then `raw/battery_float.post.ioreg` deleted (a real custody failure, no patching), passed to the gate as `member-7` after one good member | `CustodyFailure('custody failure: custody/post expected b42eb919… observed absent')`. The label `member-7` is absent from the message; the exception has no notes and no `window_member` attribute. Python here is 3.14.7; `pyproject.toml` declares `requires-python = ">=3.11"`, so `BaseException.add_note` is available. |
| X5 | **SF-5.** One run per backend (`wall_meter`, `nvidia_smi`, `jetson_rails`, `powermetrics`) through the head controller with the test suite's registry (which supplies the mock telemetry adapter) and the injected battery runner | Every one carries `stage_started` then `stage_completed` for `idle_drift_sentinel`, completion metadata `{"status": "unavailable", "monotonic_ns": <int>}`. `authenticate_bundle` → `pass`; reader → `pass`. With the two events removed from the `wall_meter` bundle's `events.jsonl`: `authenticate_bundle` → `battery_float_evidence_missing`, reason `bundle span unavailable`; the reader refuses with that text. A simulated run carries no such events. Strict validation of the `wall_meter` bundle returns one problem, `raw-to-trace: no verifier registered for production backend wall_meter`, which does not concern the battery. |
| X6 | **SF-5, who reads the stage.** `Grep idle_drift_sentinel` over `joulewise/**` and `scripts/**` at head; `grep def measure_post_run_idle` | Eight hits: seven in `controller.py`, one in `battery_float.py:1054` (the span-end lookup). The only adapter that implements the real sentinel measurement is `joulewise/adapters/powermetrics.py:1021`. `battery_float.py` is S0 code that S1 may not edit. |
| X7 | **SF-6.** A marker-carrying bundle whose `config.json` is rewritten to backend `powermetrics` with `metadata.config_sha256` re-bound | Head reader: `battery_float_evidence_missing: invalid record`. `tests/test_bundle_read.py:246` asserts `"invalid record"` for exactly this shape. Head baseline: `python3 -m unittest tests.test_bundle_read tests.test_bfgs_window_consumers` → `Ran 100 tests`, `OK`. |
| X8 | **Trial of amendments 37 and 42 on the scratch copy** (typed refusal class, gate continues over status refusals, custody labelled, `_digest_bound_mock_config` never raises) | Same two suites: exactly **one** real failure, `test_explicit_mock_not_applicable_refuses_nonmock_config` (`"invalid record" does not match "battery_float_evidence_missing: not_applicable not bound"`). A second failure is a scratch artefact (the pin test asks git for `1417c0c4`, absent from the scratch repository). The probes of X1–X4 rerun on scratch: window [A, B] → `WindowBatteryRefusal` naming **both**; window [c1, A] → names both with their own statuses; the deleted-raw-file member → the same `CustodyFailure` object with note `window member: member-7` and attribute `window_member == "member-7"`. The guard's scanner (`tests.test_battery_float_consumers.violations`) on the patched `bundle_read.py`: `[]`. |
| X9 | **SF-2.** `tests/test_window_duration_margins.py` at head, then with its `_make_bundle` changed to backend `mock` plus a bound `config_sha256` (remedy R2 applied to a fixture that is `powermetrics` at base) | Head: `Ran 35`, `errors=24`. After R2: the reader admits the bundle as `not_applicable`; `failures=9, errors=6`. **Nine of the 24 turn green on a fixture whose backend was changed; fifteen stay red** because the consumer's own replay refuses (`raw_to_trace_replay_failed: … authoritative raw/powermetrics.plist is unavailable`). |
| X10 | **N-1, N-2: the reverse sweep, rerun in full.** Complete digest and tree digest of all 1402 bundle directories under `/Users/edr/code/JouleWise/runs*`, intersected with every 64-hex string in every tracked file at `1417c0c4` (10 577 distinct strings) | 1402 of 1402 of my complete digests equal the refuter's map. Committed files citing an on-disk bundle's **complete** digest: `df-ph-decode-floor-mint1.json` (50 bundles), and three prose documents (`docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md` 51, `docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md` 40, `docs/legacy/strategy/…/prop-param-scaling-energy.md` 12). Citing an on-disk bundle's **tree** digest: `analysis/rpt001-v2/input_manifest.json` (6), `analysis/rpt001-v2/artifact_manifest.json` (the same 6; it also declares the tree identity), and three prose documents. Wall time 16 s on ten processes. |
| X11 | **N-1: counts at base.** JSON walk of `df-ph-decode-floor-mint1.json` and `analysis/rpt001-v2/input_manifest.json`; intersection with the 13-entry set | The floor file holds 50 distinct values under `bundle_sha256` and the same 50 under `bundle_sha256s`; `c2851728…` is among them. The manifest holds six under `bundle_tree_sha256` and declares `{"algorithm": "sha256", "version": "joulewise.bundle-tree.nul-v1"}`. The three groups (13 fixtures, 50, 6) are pairwise disjoint: **69 distinct digests**. All 13 fixture entries are under `tests/fixtures/`. |
| X12 | **The paper registry, traced** (the ruling under review left this NOT EXECUTED). `docs/paper/results-fill-registry.md` at base, every line carrying a 64-hex string | 20 distinct digests, none a bundle digest of either kind. Ten claim rows (DG-135 to DG-144) pin the committed file `docs/process_traces/2026-08-09-prefill-phase-proof/results.json` (sha256 `e93c1d9c…d8b1`, recomputed equal). That file lists **100 bundles**, each by the SHA-256 of six of its files (`events.jsonl`, `metadata.json`, `outputs/tokens.jsonl`, `power_trace.csv`, `raw/powermetrics.plist`, `summary_metrics.json`), never by a whole-bundle digest. 50 are the floor file's 50. The other **50 are the 7B-model runs** under `runs_window_7bfloor_20260729`: all 50 are on disk, the six pinned files of all 50 hash to the committed values, their complete digests are cited by **no** committed file, and the head reader refuses all 50 as `prospective bundle`. A bundle there has 24 files, so six file digests do not fix its identity. |

**NOT EXECUTED.** No full-suite run (V2, V3). The count of distinct complete digests cited only by prose (the refuter's "41") was not re-derived; X10 gives per-file counts. Strict validation of a `wall_meter` bundle at base, for comparison with X5, was not run. Whether any production caller of the window gate exists today was not swept (round 2 creates them). The R3 remedy was tried on two fixture shapes I built (X1, X2), not on every round-F test. I did not reproduce the refuter's B-E2 by its own method (a patched raise); X4 replaces it with an unpatched failure.

## 2. Rulings

### SF-1 — UPHELD. Remedy R3 of amendment 38 cannot work as written.

X1 reproduces it: the reader looks in the historical set only when the `battery_float` key is absent, and every bundle the head controller builds has the key. X2 adds a second shape the refuter did not name: a non-simulated legacy-identity fixture carries a real pair, and the identity overwrite breaks that pair's binding to the run id, so remedy R1 (write a passing pair) cannot serve it either. A fixture that carries a frozen legacy identity models a run from before the battery check; such a run has no key and no raw battery files. Deleting both makes the fixture say what it models, and then the patched set admits it (X1, X2).

I adopt the refuter's replacement with three changes: the helper also deletes the two raw battery files; the patch target and its return type are named (this is N-3's second half); the label `unobserved_historical` is asserted on the reader attribute. **Text change:** amendment 38, remedy R3 and constraint F-6, as restated in §4.

### SF-2 — UPHELD, with the premise corrected.

The refuter's premise was that a retargeted fixture keeps "every assertion green". X9 shows that on the refuter's own example this is only partly so: nine of 24 tests turn green and fifteen stay red because the consumer replays the raw powermetrics file. The finding stands on the nine: a test that passes on a simulated-backend fixture after passing at base on a powermetrics fixture no longer tests what it tested, and constraint F-4 (no assertion weakened) cannot see that, because no assertion changed. The limit is cheap and mechanical. **Text change:** amendment 38, remedy R2, as restated in §4.

### SF-3 — UPHELD. The mechanism is changed from a message prefix to an exception class.

X3 reproduces it, and adds that a confounded member ahead of a prospective one is hidden. S1 did not invent this behaviour. Amendment 26, as the earlier erratum restated it, contains two sentences that contradict each other for this case: one requires `WindowBatteryRefusal` to name **every** member whose status is `battery_float_evidence_missing`; the other says "a `BundleReadError` raised while classifying a member … is re-raised … as `CustodyUnreadable`". The reader delivers the refusals of text 8 (`prospective bundle`, `invalid record`) as `BundleReadError`, so S1, following the second sentence to the letter, turned a status into custody. The second sentence's own examples (an unparseable `metadata.json`, a missing or malformed `events.jsonl`) show it was written for unreadable containers. The defect is in the ruled text, and amendment 42 repairs it.

The refuter proposed to tell the two cases apart by whether the message begins with `battery_float_evidence_missing:`. I reject that mechanism: it makes the wording of a message a control input, so a later edit to a message silently moves a refusal from status to custody. The reader instead raises a subclass of `BundleReadError` for a battery status refusal, and the gate branches on the class. X8 shows this shape works, keeps the guard clean, and breaks no S1 test other than SF-6's. I also drop the refuter's "`bundle_sha256` … or `None` if that raises": the reader has already computed the digest before it refuses, so the refusal carries that value and no exception is swallowed. **Text change:** new amendment 42 (§4); amendment 26's conversion sentence is narrowed by it.

### SF-4 — UPHELD, extended to both custody paths.

X4 reproduces it with a real failure. Text 12 requires the refusal to name the member. Round 2's consumers must not import `battery_float` (amendment 36's round-2 rule), so they cannot catch the exception to add the name; the gate must. Re-raising the same object keeps the class, the message and the failure list that S0's tests pin. I extend the refuter's text so that the `CustodyUnreadable` the gate itself constructs carries the same attribute, and so that the test checks the formatted traceback, which is where a reader of a failed run will look. **Text change:** amendment 42 (§4); one sentence added to amendment 36's round-2 rule.

### SF-5 — UPHELD. The stage is ratified, because S0's merged code leaves no other span end.

X5 and X6 reproduce it. The reasoning that forces the ratification: text 7 requires every non-simulated run to be bracketed ("a Mac `wall_meter` run is bracketed"); `battery_float.authenticate_bundle`, merged in S0 and byte-identical in S1, takes the span's end only from the completion event of stage `idle_drift_sentinel` (amendment 31); that stage runs a real measurement only on the powermetrics adapter (X6). Without the two events, every `wall_meter`, `nvidia_smi` and `jetson_rails` run would be refused as `bundle span unavailable` (X5, stage removed). S1's choice is therefore the only one inside its scope that satisfies text 7, and it is physically sound: the `post` reading starts after the measured run has ended. It still changes the event log of production runs with no ruled text behind it, which the original charge forbade. Amendment 43 supplies the text. I change the refuter's wording in two places: the condition is on the resolved telemetry **adapter**, which is what the code tests, and the test must not assert that strict validation is clean, because X5 shows a `wall_meter` bundle already carries an unrelated strict problem. **Text change:** new amendment 43 (§4).

### SF-6 — UPHELD.

X7 and X8 reproduce it: the test is green at head and is the single S1 test that amendment 37 turns red. Two neighbouring assertions would stay green only by accident, because the old message survives inside the new detail string; they are tightened to the ruled prefix. I also add one sentence defining "bound" in the message `not_applicable not bound`, since the message is raised for a config whose digest does match but whose backend is not `mock`. **Text change:** amendment 37 as restated in §4.

### N-1 — UPHELD. The included sources are named; the count is exact.

Amendment 40's rule "an artifact that pins bundles as inputs of a number" asks the seat for a judgment, and two seats could judge differently. The set is closed at `1417c0c4`, so its sources can be listed. X10 and X11 confirm the three groups and that they are disjoint. X10 also shows why naming is needed for determinism: two committed manifests carry the same six tree digests, and the set forbids a digest appearing twice, so the entry's `source` must be fixed by rule. "At least 69" becomes "exactly 69". X12 closes the item the ruling under review left untraced (the paper registry): it pins no bundle digest of either kind. **Text change:** amendment 40 as restated in §4.

### N-2 — UPHELD, as a report the seat runs, never as an input to the set.

The forward scan looks under key names, so a citation under an unexpected key would be missed. The reverse sweep starts from the bundles and cannot miss a citation of a bundle that is on disk. X10 is that sweep; it takes 16 s. It must not decide the set's contents: the set has to be rebuildable from git alone, and the corpus is not in git. **Text change:** amendment 40 as restated in §4 (the `--witness` clause).

### N-3 — UPHELD, both halves.

After amendment 39 a bundle with no key that is not in the set is hashed twice, once per fold. X10 measured both folds over 1402 bundles at 16 s in total, so the cost is about a hundredth of a second per bundle and is accepted; the two folds cannot share one pass because `complete_bundle_sha256` lives in `detection_floor.py`, outside S1's scope. The second half (the patch target's return type) is ruled under SF-1. **Text change:** amendment 39 as restated in §4.

## 3. One finding outside the refuter's list (flagged; not ruled)

**Fifty runs that the paper's registry relies on stay refused after every amendment here.** X12: ten claim rows of the paper pin a committed results file that lists 100 runs by the hashes of six files each. Fifty of those runs (the 1.5B model) enter the set through the detection-floor file. The other fifty (the 7B model, measured 2026-07-29, before any battery reading existed) are named by no whole-bundle digest in any committed file, so text 8 cannot enumerate them, and the reader labels them `prospective bundle`, which is false in the same way it was false for the six RPT001 runs. Nothing unsafe follows: a refusal releases no number. But any replay of those claim rows through the reader is red until a cold gate decides how they are admitted (for example a committed manifest of their complete digests, authenticated against the six pinned file hashes). I do not rule it, because the charge does not pose it and it widens the set. It belongs to the historical-battery lane, and amendment 40 now requires the builder to list these 50 by name so the omission is visible.

## 4. Amendments 36 to 43, restated in full (each self-contained; S1's next brief quotes these)

### Amendment 36 (amends text 4 and amendment 25's guard; adds one path to S1's WRITE_SCOPE)

36. **Guard rows for the controller.** `tests/test_battery_float_consumers.py` joins S1's WRITE_SCOPE for this amendment only. `REPLACE_CALL_ALLOWLIST` gains exactly these four rows, each with the existing value `REPLACE_REASON`, and the comment above the table is extended with the four replaced types in order (`RuntimeEvent`; `BenchmarkConfig`; `SamplingConfig`; `BenchmarkConfig`):

```python
("joulewise/controller.py", "_Execution._axi_request_events",
 "replace(event, metadata=metadata)"): REPLACE_REASON,
("joulewise/controller.py", "cooldown_gate",
 "replace(config, run_id=run_id if run_id is not None else config.run_id, sampling=replace(config.sampling, idle_seconds=selected.subwindow_s))"): REPLACE_REASON,
("joulewise/controller.py", "cooldown_gate",
 "replace(config.sampling, idle_seconds=selected.subwindow_s)"): REPLACE_REASON,
("joulewise/controller.py", "run_experiment",
 "replace(config, run_id=f'{experiment_id}__r{rep}')"): REPLACE_REASON,
```

The count assertion `len(REPLACE_CALL_ALLOWLIST) == 9` becomes `== 13`. No existing row, assertion or self-test is removed or loosened. Three tests are added:

- **(i) Forgery self-test on the real file.** Read `joulewise/controller.py`; assert the line `    verdict = battery_float.authenticate_capture(root)\n` occurs exactly once; assert `violations("joulewise/controller.py", source) == []`; insert `    verdict = replace(verdict, status='pass')\n` immediately after that line and assert the result is exactly `[("joulewise/controller.py", <that line's number + 1>, "dataclasses.replace")]`. Then append a new function whose body is the `run_experiment` row's call text and assert it is flagged (a row's text in another function is not covered).
- **(ii) Type test.** Import `RuntimeEvent` (`joulewise.interfaces`), `BenchmarkConfig` and `SamplingConfig` (`joulewise.schemas`); assert each is a dataclass, none is or subclasses `battery_float.PairVerdict`, and no `dataclasses.fields(cls)` type string contains `PairVerdict`.
- **(iii) Provenance test.** For every row of `REPLACE_CALL_ALLOWLIST` (all 13), assert the same (path, qualified name, call text) is found when the scanner is run over that path's source in `git archive 1417c0c4`, with one `battery_float` import line prepended so the scanner records sites; `skipTest` when the commit is absent from the clone, as the existing pre-seam test does. A row can therefore only cover a call that existed, in the same function with the same text, before S1 wrote a line.

RED/GREEN: `test_no_consumer_references_a_verdict_primitive` and `test_replace_call_allowlist_is_exact_and_only_covers_older_types` are RED at `24b79db3` and GREEN after; (i) is RED if any of the four rows is widened to a path-level exemption. A bench rerun of the guard needs git metadata: without it the second test compares against an empty table.

**Round 2 rule.** A module imports `battery_float` only where a ruled text requires a call into it (text 10 for `calibration_bracketing.py`; text 9 for `scored_reduce.py`). The eight text-12 consumers call `bundle_read.authenticate_window_members` and do **not** import `battery_float`. **They do not catch `CustodyFailure`, by that name or through `except Exception`; the window gate labels it with the member (amendment 42), so a consumer needs no handler to name the member.** When a required import exposes a pre-existing replace call, round 2 adds its exact row under conditions (ii) and (iii), states the replaced type with the file and line that proves it, updates the count, and lists the row in its report for the refuter. One such row is predicted (`calibration_bracketing.py::_candidate_from_observation`); its replaced type is NOT EXECUTED. A replace call that fails (iii) is new code and gets no row without a cold gate.

### Amendment 37 (amends text 8, state (iii) and the prospective sentence; S1's existing scope)

37. **Refusal label when the config does not bind.** In this amendment a bundle's MOCK marker is **bound** when both hold: the bytes of `config.json` hash to `metadata.config_sha256`, and the re-validated config's telemetry backend is `mock`. `BundleReader._digest_bound_mock_config` never raises. It reports not-bound, with a detail string, when `config.json` is missing or unreadable (`config.json cannot be read: <reason>`), when its bytes do not hash to `metadata.config_sha256` (`config.json digest does not match metadata.config_sha256`), or when it does not re-validate (the validator's message); it reports not-bound with an **empty** detail when the digest matches and the backend is simply not `mock`; it reports bound only when the digest matches and the backend is `mock`. The reader then raises, for a bundle with **no** `battery_float` key: `battery_float_evidence_missing: prospective bundle (<detail>)`; for a bundle whose key is exactly the MOCK marker: `battery_float_evidence_missing: not_applicable not bound (<detail>)`. In both, ` (<detail>)` is omitted when the detail is empty. A `battery_float` key holding anything other than a pair or the exact MOCK marker (for example `null`, or a marker with another value) is still `battery_float_evidence_missing: invalid record`. No bundle is admitted by this change; only the text of refusals moves. These refusals are raised as `BatteryStatusRefusal` (amendment 42).

Tests in `tests/test_bundle_read.py`:
- new: a copy of a non-simulated bundle with no key whose `metadata.config_sha256` is altered, and one whose `config.json` is deleted, each raise a message matching `^battery_float_evidence_missing: prospective bundle \(` (RED at `24b79db3`, which raises the bare config message);
- new: a marker-carrying bundle with an altered `config_sha256` raises a message matching `^battery_float_evidence_missing: not_applicable not bound \(`;
- **rewritten:** `test_explicit_mock_not_applicable_refuses_nonmock_config` asserts the full message `battery_float_evidence_missing: not_applicable not bound` in place of `invalid record`. This is the ruled expectation, not a weakening: the bundle is still refused, and the new text names the actual fault;
- **tightened:** the second assertion of `test_key_absent_mock_is_not_applicable_only_with_digest_bound_config` (`"config.json digest"` at head) asserts `^battery_float_evidence_missing: prospective bundle \(config\.json digest does not match`.

### Amendment 38 (adds to §E, S1; binds round F)

38. **Fixture round.** S1's WRITE_SCOPE gains, for round F only:

```text
tests/bfgs_bundle_fixture.py        (new; the one shared helper)
tests/test_analysis_integration.py
tests/test_floor_extraction.py
tests/test_whole_window_selection.py
tests/test_window_duration_margins.py
tests/test_run_campaign.py
tests/test_audit_amplification.py
tests/test_cli.py
tests/test_cli_run.py
tests/test_p2038_production_path.py
tests/test_package_bundle_pack.py
tests/test_partial_record_enclosure.py
tests/test_phase_share.py
tests/test_powermetrics.py
```

`tests/test_rpt001_report_slice.py` is **not** granted: its failure is a production refusal and must go green with no edit once amendments 39 and 40 land; if it does not, that is a finding to return. After round 2's full-suite rerun, the magistrate may add further paths **by name**, only files under `tests/`, only under the constraints below. Round F edits no file outside `tests/`.

Constraints, each checked by the refuter:

- **F-1 Three remedies, no other.**
  - **(R1) A passing pair written the way production writes it.** For a bundle produced by running the controller, inject `battery_runner` from `tests/battery_float_fixture.py`. For a hand-built bundle or calibration capture, the shared helper calls the real `battery_float.observe` through that runner, writes the two raw files at `raw/battery_float.<pre|post>.ioreg`, and writes the two span events (stage `idle_baseline` started, stage `idle_drift_sentinel` completed, each with an integer `monotonic_ns`) so that they fall between the two readings, before any manifest or evidence digest is sealed.
  - **(R2) A digest-bound MOCK config:** `config.json` bytes that hash to `metadata.config_sha256`, with backend `mock`. **R2 is available only to a fixture whose `config.json` backend is already `mock` when the same constructor is run at `1417c0c4`. A fixture whose backend at base is anything else, or that has no readable `config.json` at base, keeps its backend and takes R1, or R3 under R3's own conditions.**
  - **(R3) For a fixture that models a bundle measured before the battery check.** The fixtures that qualify are those that overwrite `metadata.run_id` and `metadata.config_sha256` with a frozen legacy identity, and test-mutated copies of a tracked historical fixture; the round-F brief lists them by test name. The shared helper (a) deletes the `battery_float` key from `metadata.json` and deletes `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg` if present, because a run from before the check has none of the three; (b) after the test's last mutation of the bundle, computes `complete_bundle_sha256` of the bundle; (c) patches `joulewise.bundle_read._historical_bundles` with `unittest.mock.patch` so that it returns `HistoricalBundleSet(complete=<production complete set> | {<that digest>}, tree=<production tree set>)` (the type is defined in amendment 39); (d) asserts the patched `complete` set has exactly one more member than production and the `tree` set is unchanged. Every R3 test asserts `reader.battery_float_status == "unobserved_historical"`. R3 is never used for a bundle that models a new measurement. R1 is not available to a fixture that overwrites the run id after the pair is written: the pair binds the run id and the overwrite breaks it.
- **F-2 No production seam.** No production module gains a parameter, environment variable, flag or branch for tests. R3 is a `unittest.mock` patch inside the helper.
- **F-3 Nothing else is patched.** No test patches `BundleReader.metadata`, `BundleReader._battery_verdict`, `_digest_bound_mock_config`, `authenticate_window_members`, or any `battery_float.authenticate_*`. `_historical_bundles` is patched only by the shared helper, for R3. `HISTORICAL_BUNDLE_SET_SHA256` is patched only by the reader's own pin test.
- **F-4 No assertion weakened.** No assertion is deleted, loosened, skipped or wrapped. Where text 8 supersedes an expectation, the test is rewritten to the ruled expectation and shown RED against `1417c0c4` behaviour and GREEN at head. The round's report lists every such test with old and new expectation and the ruled sentence that forces it.
- **F-5 Refusals are named.** A test that expects a battery refusal asserts the reason text (`prospective bundle`, `battery_float_confounded`, …), not merely that something raised.
- **F-6 The gate still bites through the fixture.** For each touched module, one counterfactual is run and reported. For R1 tests: the helper's raw reading swapped for `tests/fixtures/battery_float/charging-synthetic-from-real.ioreg` turns that module's R1 tests RED at the reader or the attachment. For R3 tests: with the patch removed, the test fails with a message beginning `battery_float_evidence_missing: prospective bundle`.
- **F-7 Partition reported.** The report gives, per test, the fixture's backend at base, which remedy it took and why. The triage partition is re-derived from the post-round-2 log, not copied.

**Outside round F.** The four AXI cases fail identically at base and are not S1's. The paper supply-map case is a source-hash receipt that goes stale whenever `bundle_read.py` changes; `configs/paper_supply/supply_map.json` is granted to S1 for **one final commit**, regenerated only by its committed generator after the last production change, and only if the resulting diff changes digest values of files S1 edited and nothing else; the seat pastes the generator command and the diff. (Generator NOT TRACED; if the diff touches anything else, the seat stops and returns it.)

### Amendment 39 (amends text 8, state (ii) and "Set enumeration"; S1's existing scope: `bundle_read.py`, the builder, the set file, `tests/test_bundle_read.py`)

39. **Tree-digest entries.** The historical set holds entries of two kinds, distinguished by their key set:

```text
{"complete_bundle_sha256": <64 hex>, "run_id": <str>, "source": <committed path>}
{"bundle_tree_sha256": <64 hex>, "tree_identity": "joulewise.bundle-tree.nul-v1",
 "run_id": <str>, "source": <committed path>}
```

Entries are sorted by (kind, digest). The reader rejects the file on any other key set, on a `tree_identity` other than that string, or on a digest appearing twice. A tree entry is enumerated only from a committed manifest that itself declares `bundle_tree_identity == {"algorithm": "sha256", "version": "joulewise.bundle-tree.nul-v1"}` and that amendment 40 names as an included source. `analysis/rpt001-v1/` declares no identity and uses a retired fold; its values are not enumerated.

**The loaded set.** `bundle_read._historical_bundles()` returns `HistoricalBundleSet`, a `typing.NamedTuple` with two fields, `complete: frozenset[str]` and `tree: frozenset[str]`. It is a `NamedTuple` and not a dataclass so that no `dataclasses.replace` call is ever needed on it in a module the guard scans. This function is the single place the reader obtains the set, and the one target remedy R3 patches.

Reader order for a bundle with **no** `battery_float` key, each step reached only if the one before did not decide:

1. compute `complete_bundle_sha256(path)` (symlinks and special files fail closed, as today); if it is in `complete`, the bundle is `unobserved_historical`;
2. compute the tree digest: for every regular file, (relative POSIX path, `sha256_authentication_input`, size by `lstat`), folded by `publication_privacy.tree_sha256` imported inside the function body; if it is in `tree`, the bundle is `unobserved_historical`;
3. state (iii) under amendment 37;
4. `battery_float_evidence_missing: prospective bundle`.

**Cost, stated.** A bundle that reaches step 2 has its files read and hashed twice, once per fold. The two folds cannot share one pass because `complete_bundle_sha256` is in `detection_floor.py`, outside S1's scope. Measured over 1402 real bundles, both folds together took 16 s on ten processes; this is accepted. A bundle that carries a pair, or that step 1 admits, is hashed once.

The verdict comes from `unobserved_historical_verdict("bundle", bundle_sha256=<the complete digest from step 1>)` in both cases, so text 9's and amendment 24's meaning of `bundle_sha256` is unchanged. `FROZEN_LEGACY_BUNDLE_IDENTITIES` still plays no part. The set's bytes and `HISTORICAL_BUNDLE_SET_SHA256` change inside S1; `battery_float.py`, `reduce.py`, `bundle.py` and S1's pin list stay byte-identical.

Tests in `tests/test_bundle_read.py`: a fixture bundle whose tree digest is a tree-kind entry is admitted `unobserved_historical` (RED at `24b79db3`); the same bundle with one byte appended to `power_trace.csv` is `prospective bundle`; the reader's tree digest equals `scripts/make_figures.bundle_tree_sha256` on the same directory; a set file with a tree entry naming another `tree_identity` is rejected; a set file with one digest in two entries is rejected. When the controlled corpus is present, `tests/test_rpt001_report_slice.py::test_full_route_census_emits_only_void_artifacts` is GREEN unedited.

### Amendment 40 (amends text 8, "Set enumeration"; binds the builder and the report S1 files before its pin is final)

40. **Enumeration by content, inclusion by named source, and two checks.**

**Scan.** The builder (`scripts/build_battery_float_historical_bundles.py`) reads every tracked file at `1417c0c4` (`git ls-tree -r`) and decides by **content**, never by path name:

- JSON and JSONL are parsed and walked by key; every 64-hex string at or under a key whose name contains `bundle` and one of `sha256`, `digest`, `tree` is a **candidate**, recorded with its key name, its file, and the nearest `bundle_id` / `run_id` in the same object.
- Every other text file is scanned by line for the same key pattern, and Markdown tables are scanned by column header, so a digest in a table cell is attributed to its column.
- Each (key name, producing schema) pair is classified **once, by reading the code that writes it**, as one of: `complete` (written from `complete_bundle_sha256`), `tree_nul_v1`, `tree_legacy`, `file_digest`, `not_a_bundle`. The classification table is a constant in the builder; each row cites the producing `file:line`. An unclassified pair makes the builder exit non-zero.

**Inclusion.** The set is closed at `1417c0c4`, so its sources are named here and held in the builder as the constant `INCLUDED_SOURCES`. An entry is written for a candidate only if its source is one of these three:

| Source | Key | Kind | Count |
|---|---|---|---|
| `df-ph-decode-floor-mint1.json` (the committed detection-floor artifact, schema `joulewise.detection_floor_artifact.v2`) | `bundle_sha256` (the same 50 values also appear under `bundle_sha256s`) | complete | 50 |
| `analysis/rpt001-v2/input_manifest.json` | `bundle_tree_sha256` | tree | 6 |
| tracked fixture bundles under `tests/fixtures/` and `docs/process_traces/`, found by directory walk and hashed from committed bytes, as the builder does today | — | complete | 13 |

The three groups are disjoint, so the set holds **exactly 69 entries**. `analysis/rpt001-v2/artifact_manifest.json` carries the same six tree digests; the entry's `source` is `input_manifest.json` and the second citation is listed as a duplicate. Every other candidate the scan finds is **listed, not included**, with its key, file, class and a reason, on stderr, with counts per key and per file; nothing is dropped silently. A candidate classed `complete` or `tree_nul_v1` whose source is not one of the three is listed with the reason `source not named by amendment 40` and named in the seat's report; it enters the set only by a cold gate. A digest needs no bundle on disk to be included: the set is a list of citations.

**Two checks, run by the seat and pasted into its report; neither decides the set's contents.**

- *Forward check.* The builder's output equals the committed file byte for byte, and the entry count is 69. A different count is a finding the seat returns; it does not explain it away.
- *Reverse check (the completeness witness).* The builder accepts `--witness <run root> …`. In that mode it computes the complete digest and the tree digest of every bundle directory under the given roots, intersects them with **every** 64-hex string in every tracked file at `1417c0c4` (not only strings under bundle-named keys), and prints each hit with the citing file, marked `included` or `listed`. It writes nothing. The expected result at `1417c0c4` over `/Users/edr/code/JouleWise/runs*` (1402 bundles) is: complete digests cited by `df-ph-decode-floor-mint1.json` (50, included) and by three prose documents (listed); tree digests cited by the two `analysis/rpt001-v2/` manifests (6, included once) and by three prose documents (listed). Any hit in a file that is neither an included source nor prose is a finding to return. A mismatch between an included entry and the recomputed digest of the bundle it names is a finding to return.

**Named in the listed-not-included output** (so the omissions are visible): the digest `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9` (amendment 41); the twelve tree values of `analysis/rpt001-v1/` (`tree_legacy`); and the 100 bundles of `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`, which the paper registry pins and which are identified there only by six per-file hashes each (`file_digest`). Fifty of those 100 are in the set through the floor file. The other fifty, the 7B-model runs of `runs_window_7bfloor_20260729`, are in the set through nothing and stay `prospective` until a cold gate rules on them.

On-disk bundles cited by no committed artifact stay `prospective` and remain the historical-battery lane's population, admitted only by cold gate, as text 8 already says.

Tests in `tests/test_bundle_read.py`: the builder's output equals the committed file; the set has 69 entries, 63 complete and 6 tree; `c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf` (bundle `p2015-df-ph-decode-abs-r03`) is a complete-kind entry whose `source` is `df-ph-decode-floor-mint1.json` (RED at `24b79db3`); a candidate from a source outside `INCLUDED_SOURCES` is not written. The refuter re-runs the builder and checks every classification row against its cited line.

### Amendment 41 (amends text 8, "Set enumeration")

41. **`PINNED_BUNDLE_SHA256` is a file digest.** The words "`PINNED_BUNDLE_SHA256`" are struck from text 8's list of citation classes. The builder's classification table (amendment 40) carries the row `PINNED_BUNDLE_SHA256` in `scripts/issue_dg071_dg075_statistics.py` → `file_digest`, citing `:537-539`; the digest `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9` is the SHA-256 of one file, `power_trace.csv` of bundle `p2015-df-ph-decode-abs-r03`, and appears in the listed-not-included output with that reason. The bundle that contains the file enters the set on its own citation, `c2851728…86bf` in the floor file. **Round 2 note:** that script reads `power_trace.csv` by path without the bundle reader, so the battery gate does not reach it; text 12's sweep (any direct read of `power_trace.csv`) must report it, and its allowlist row, if granted, is class `historical` with this amendment as the reason.

### Amendment 42 (new; amends amendment 26 and text 12; S1's existing scope: `joulewise/bundle_read.py`, `tests/test_bundle_read.py`, `tests/test_bfgs_window_consumers.py`)

42. **Status refusals are not custody; every refused member is named; custody carries the member's label.**

**(a) A typed refusal.** `bundle_read.py` gains `class BatteryStatusRefusal(BundleReadError)` with attributes `status: str`, `reasons: tuple[str, ...]` and `bundle_sha256: str | None`, and message `"<status>: <reasons joined by '; '>"`. The reader raises it, and nothing else, for every battery refusal that is a statement about evidence: `prospective bundle`, `not_applicable not bound`, `invalid record` and `not_reached` (each with status `battery_float_evidence_missing`), and, in `metadata()`, any verdict that `authenticate_bundle` returned with a status other than `pass`. `bundle_sha256` is the complete digest the reader computed before refusing (`None` only for `not_reached`, where none is computed); the reader does not hash again and does not suppress an exception from the digest function. Because it subclasses `BundleReadError` and its message is unchanged, every existing caller of `metadata()` behaves as before. Every other `BundleReadError` (an unparseable or non-object `metadata.json`, a missing or malformed `events.jsonl`, an unreadable or mis-pinned historical set file) stays a plain `BundleReadError`. The branch is on the exception's class, never on the text of its message.

**(b) The window gate.** In `authenticate_window_members`, for each member in order:

1. `BatteryStatusRefusal` → append the refused entry `{label, status, reasons: list, bundle_sha256}` taken from the exception, and **continue with the next member**;
2. any other `BundleReadError` → raise `battery_float.CustodyUnreadable("<label>: <error text>")` with attribute `window_member = label`, as amendment 26 rules for unreadable containers;
3. `battery_float.CustodyFailure` (including `CustodyUnreadable` raised inside `authenticate_bundle`) → call `exc.add_note(f"window member: {label}")`, set `exc.window_member = label`, and re-raise **the same object**, so its class, message and `failures` list are unchanged;
4. a returned verdict whose status is `battery_float_confounded`, `battery_float_evidence_missing` or `not_applicable` → append the refused entry, as today.

After the loop, if any entry was refused, raise `WindowBatteryRefusal` naming every one. Custody therefore still stops the computation at once and is never listed as a status; a status is never reported as custody. Amendment 26's sentence "a `BundleReadError` raised while classifying a member … is re-raised … as `CustodyUnreadable`" now applies to case 2 only. Consumers never catch `CustodyFailure`.

Tests in `tests/test_bfgs_window_consumers.py` (production call site: `authenticate_window_members`, called by the eight text-12 consumers from round 2 on):
- a window of two prospective members raises `WindowBatteryRefusal` whose `members` name both, each with status `battery_float_evidence_missing` and its own complete digest (RED at `24b79db3`: `CustodyUnreadable` naming the first only);
- a window of a charging-pair member followed by a prospective member names both, the first as `battery_float_confounded` (RED at `24b79db3`: the confounded member is hidden);
- a passing non-simulated member whose `raw/battery_float.post.ioreg` is deleted after finalization, placed second in a window, raises an exception for which `type(exc) is CustodyFailure`, `exc.window_member` is the member's label, `exc.__notes__` contains `window member: <label>`, `"".join(traceback.format_exception(exc))` contains the label, and `exc.failures` equals the list raised by `authenticate_bundle` on the same bundle (RED at `24b79db3`: no label anywhere);
- the existing `test_unreadable_second_metadata_is_custody` stays green and additionally asserts `window_member == "second"`;
- in `tests/test_bundle_read.py`: each of the four refusals in (a) is an instance of both `BatteryStatusRefusal` and `BundleReadError`; an unparseable `metadata.json` raises a `BundleReadError` that is **not** a `BatteryStatusRefusal`.

The guard must stay green on `bundle_read.py` with no new allowlist row (a trial implementation produced no violation).

### Amendment 43 (new; amends text 7 and amendment 31; S1's existing scope: `joulewise/controller.py`, `tests/test_controller.py`)

43. **The span's end marker on backends without a drift measurement.** The forcing facts: the pair must enclose a span whose end is the completion event of stage `idle_drift_sentinel` (amendment 31; read by `battery_float.authenticate_bundle`, which S1 may not edit); that stage performs a real post-run idle measurement only when the resolved telemetry adapter implements `IdleDriftEvidenceProvider`, which today is the powermetrics adapter alone; text 7 requires every non-simulated run to be bracketed. Therefore: when the config's telemetry backend is not `mock` and the resolved telemetry adapter is **not** an `IdleDriftEvidenceProvider`, `_stage_idle_drift_sentinel` emits `stage_started` and then `stage_completed` for `idle_drift_sentinel`, with completion metadata exactly `{"status": "unavailable", "monotonic_ns": <int>}`, and performs no measurement, no sleep and no adapter call. `"unavailable"` states that no drift measurement exists for this run; the event is a time marker and carries no evidence about idle drift. When the backend is `mock`, no such event is written, as at base. When the adapter is an `IdleDriftEvidenceProvider`, the stage runs as at base and its completion metadata gains only the `monotonic_ns` field. No reader other than `authenticate_bundle` may treat the marker's presence as evidence that a drift measurement ran; any later consumer of drift evidence must check `status`.

Tests in `tests/test_controller.py` (production call site: `_Execution.execute`):
- a run with backend `wall_meter`, the mock telemetry adapter supplied through the registry, and an injected battery runner writes exactly one `stage_started` and one `stage_completed` for `idle_drift_sentinel`, the latter with exactly the two metadata keys above; `battery_float.authenticate_bundle` rates the bundle `pass`; `BundleReader.metadata()` returns with `battery_float_status == "pass"`; no strict-validation problem of the bundle contains `battery_float` (the test does not assert that strict validation is otherwise clean: a `wall_meter` bundle already reports `no verifier registered for production backend wall_meter`);
- the same bundle with the two events removed from `events.jsonl` is refused with `battery_float_evidence_missing: bundle span unavailable`;
- a simulated run writes no `idle_drift_sentinel` event.

## 5. The S1 fix-round order

| Step | Round | Amendments | Scope | Ends with |
|---|---|---|---|---|
| 1 | **Fix round**, before round 2 | 36, 37, 39, 40, 41, 42, 43 | S1's existing WRITE_SCOPE plus `tests/test_battery_float_consumers.py` (amendment 36 only) | the builder's forward check and reverse check pasted in the report; a new `HISTORICAL_BUNDLE_SET_SHA256`; the S1 module suite and the guard suite green |
| 2 | **Round 2**, as already briefed | amendment 36's round-2 rule; amendment 41's round-2 note; amendment 42's contract is what the eight consumers call | S1's existing WRITE_SCOPE | the eight consumers wired; a full-suite rerun and a fresh failure index |
| 3 | **Round F** | 38 | the fourteen paths of amendment 38, plus any test path the magistrate adds by name | the full suite green except the four AXI cases that fail at base; the F-6 counterfactuals and the F-7 partition in the report |
| 4 | Last commit | the supply-map receipt clause of amendment 38 | `configs/paper_supply/supply_map.json` only, conditionally | the generator command and the diff pasted |

Why this order. Amendments 42 and 43 go in the fix round because round 2's consumers are written against the gate's contract, and round F's remedy R1 writes the span events amendment 43 defines. Amendment 39 precedes round F because R3 patches the type it defines. Amendment 38 waits for round 2 because round 2 adds refusals to the same test files.

## 6. Disposition and what is kept intact

| Finding | Ruling | Lands in |
|---|---|---|
| SF-1 | UPHELD; R3 rewritten (delete key and raw files, patch the named function) | amendment 38, round F |
| SF-2 | UPHELD, premise corrected (9 of 24 go green, not all); R2 limited to fixtures that are `mock` at base | amendment 38, round F |
| SF-3 | UPHELD; mechanism is an exception class, not a message prefix | amendment 42, fix round |
| SF-4 | UPHELD; extended to both custody paths | amendment 42, fix round |
| SF-5 | UPHELD; the stage is ratified with its forcing reason | amendment 43, fix round |
| SF-6 | UPHELD; one test rewritten, one tightened, "bound" defined | amendment 37, fix round |
| N-1 | UPHELD; three named sources, exactly 69 entries | amendment 40, fix round |
| N-2 | UPHELD; a `--witness` report that never writes the set | amendment 40, fix round |
| N-3 | UPHELD; cost stated, patch target typed | amendments 39 and 38 |

**Kept intact.** Custody is never a status: amendment 42 removes the one place where a status was reported as custody and adds none where custody becomes a status; a custody failure still stops the window at the member where it occurs. Authentication precedes every exclusion decision: the gate classifies every member before any energy is read and excludes none; it refuses the whole window. `joulewise/battery_float.py` is untouched by every amendment (amendment 43 exists because it may not be touched); `joulewise/reduce.py`, `joulewise/bundle.py` and S1's pin list stay byte-identical. No ruled text is reinterpreted beyond amendments 36 to 43.

**Flagged, not ruled:** the fifty 7B-model runs of §3; and, carried from the ruling under review, the `raw_summary()` read in `scripts/make_figures.py::gate_inputs` and the sixteen skipped tests of the full-suite run.

## 7. Plain summary for Ed (5 lines)

1. **All nine of the reviewer's findings are upheld**, each reproduced against the real code; none lets a run with a charging battery or damaged files reach a number. Two of the reviewer's proposed fixes were changed in mechanism, and one of its premises was only partly true (item 3).
2. **The window check** (the step that vets every run in a measurement window before any energy is read) was reporting "this run has no battery readings" as if files had been damaged, and stopped at the first bad run, hiding the rest, including a run whose readings showed charging. It now lists every bad run with its real reason, and genuine file damage carries the name of the run it was found in. The earlier ruled text contradicted itself here; the code had followed it literally.
3. **Test-fixture repair rules** (for the 87 failing tests, all pretend runs with no battery readings) are tightened: the shortcut for "pretend old run" fixtures could not work as written and is rewritten; and a fixture built on real power-meter data may not be switched to a simulated backend, which made 9 of 24 tests in one file pass while testing something else.
4. **Two unapproved behaviours are now written down:** runs on instruments other than the Mac's built-in power counter get a time-marker event in their log so the two battery readings can be shown to enclose the run (the marker measures nothing and says so); and the list of admitted pre-battery-check runs is fixed at exactly 69 entries from three named sources, with a 16-second cross-check against all 1402 runs on disk.
5. **New, outside the reviewer's list, and not decided here:** 50 runs of the larger (7B) model that ten of the paper's figures rely on are identified in the repository only by hashes of six of their 24 files, so they cannot be put on the admitted list and are refused as if newly measured. Nothing unsafe follows, but replaying those figures through the reader stays blocked until a separate ruling says how to admit them.
