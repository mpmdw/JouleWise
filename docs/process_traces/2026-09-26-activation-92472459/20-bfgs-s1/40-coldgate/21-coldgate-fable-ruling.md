# Cold gate BFGS-S1-SCOPE-01 ruling (Fable 5.1, cold judge): the S1 guard rows, fixture scope, the six retained RPT001 bundles, and one pinned digest

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, single foreground session, no subagents, no background tasks. Worktree `JouleWise-wt-s1cg-92472459`, detached at `24b79db349706c9945ce42789b1be862a4400edc` (`git rev-parse HEAD`; `git status --short` empty at start and at end). Base tree extracted with `git archive 1417c0c4 | tar -x -C /tmp/s1cg/base`. Session 2026-09-26. No `sudo`, `launchctl`, `powermetrics`, installer, inference or live `ioreg`. Only this file was written; scratch probes live under `/tmp/s1cg/`. No repository file was edited.

Vocabulary used throughout, defined once:

- **S1** is the pull request that puts a battery check around every measured run ("bundle": one directory holding one run's config, metadata, event log and power trace) and makes the bundle reader refuse bundles without that check.
- **The pair** is the two battery readings (one before the measured span, one after) that S1's controller now records in each bundle. A bundle "passes" when both readings show the battery floating (neither charging nor discharging into the measurement).
- **The historical set** is the committed file `configs/battery_float/historical_bundles.json`: a closed list of digests of bundles measured before the battery check existed. A bundle on that list is readable and is labelled `unobserved_historical` (battery state was never recorded). A bundle with no pair that is not on the list is refused as `prospective bundle`.
- **Complete-bundle digest** and **tree digest** are two different SHA-256 folds over the same inventory of a bundle directory (every regular file's relative path, byte hash and size). They differ only in how the inventory rows are serialised before hashing (E8).
- **The guard** is the test file `tests/test_battery_float_consumers.py`. It parses every production module that imports `joulewise.battery_float` and fails on any call that could forge a battery verdict, including any `dataclasses.replace(...)` call not on an exact allowlist.
- **WRITE_SCOPE** is the exhaustive list of paths a seat (a delegated model session) may edit.

## 0. Contamination disclosure

Loaded by the harness without my choosing: the global `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the auto-memory index `MEMORY.md` (one-line pointers, including loop-context titles and checkpoint names). A system reminder supplied the git status and five recent commit subjects, plus the tool and skill listings. I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `CLAUDE.local.md`, no `AGENTS.md`, no decision log, and no skill file. Two forbidden file **names** (`RUN_STATE.md`, `docs/council_log.md`) appeared in the output of one `git grep -l` file listing; their contents were not read, and every later sweep excluded them by name.

Read by me: this charge; the four authority rulings in full (Final texts v1.1, addendum 2, addendum 3, the erratum), which is more than the sections the charge names; the round-1b seat brief and seat report; the triage report; the failure index and the two triage logs (by `grep` only). I did not read the triage brief. When I checked the target directory after writing, a paired refuter report (`11-opus-contract-refuter.md`) and an execution-seat manifest had appeared beside this file; I opened neither. Code read is named under Executed evidence. I read, without modifying, seven measured bundles in the main checkout's untracked corpus (`/Users/edr/code/JouleWise/runs/` and `runs_window_a10_20260725/`).

## 1. Executed evidence (this session; every probe in the foreground)

All probes ran from the worktree root with `PYTHONDONTWRITEBYTECODE=1`. Probe scripts are `/tmp/s1cg/*.py`.

| # | Probe | Observed |
|---|---|---|
| E1 | The guard's own scanner (`tests.test_battery_float_consumers._Checker` / `violations`) run over every tracked `*.py` under `joulewise/` and `scripts/`, at head and in the base tree | **Head:** 10 modules import `battery_float` (the 8 at base plus `joulewise/bundle_read.py` and `joulewise/controller.py`); 13 replace sites against 9 allowlist rows; violations exactly `controller.py` lines 1983, 2566, 2569, 2966. **Base:** 8 importers, 9 sites, 9 rows, no violation. `bundle_read.py` contributes no replace site. **F1 reproduced.** |
| E2 | The four extra sites as the guard keys them (path, enclosing qualified name, `ast.unparse` of the call) | `_Execution._axi_request_events`: `replace(event, metadata=metadata)`; `cooldown_gate`: `replace(config, run_id=run_id if run_id is not None else config.run_id, sampling=replace(config.sampling, idle_seconds=selected.subwindow_s))`; `cooldown_gate`: `replace(config.sampling, idle_seconds=selected.subwindow_s)`; `run_experiment`: `replace(config, run_id=f'{experiment_id}__r{rep}')`. |
| E3 | What each replaced object is, by reading | `event` iterates `sorted(local, …)` where `local: list[RuntimeEvent]` (`controller.py:1837`); `config` is the parameter `config: BenchmarkConfig` of `cooldown_gate` (`:2540`) and of `run_experiment` (`:2875`); `config.sampling` is `BenchmarkConfig.sampling: SamplingConfig` (`schemas.py:1045`). `dataclasses.fields` of the three classes: `RuntimeEvent` (`interfaces.py:186`) has `timestamp_s, event_type, phase, message, metadata: dict[str, Any]`; `SamplingConfig` has three floats; `BenchmarkConfig` has 13 fields, one declared `compare=False`. None is, subclasses, or declares a field of type `PairVerdict`. |
| E4 | Where a battery verdict actually exists in `controller.py` | One binding: `verdict = battery_float.authenticate_capture(root)` at `:448`, used only for `verdict.status` and `verdict.reasons` at `:449-450`. No other name in the file holds a `PairVerdict`. |
| E5 | The four rows added in memory, then the scanner run on the real `controller.py` and on three mutations | Unmutated: no violation, four sites seen. One line `verdict = replace(verdict, status='pass')` inserted after the unique `:448` line: exactly one violation, `('joulewise/controller.py', 449, 'dataclasses.replace')`. The text of the `run_experiment` row pasted into a **different** function: flagged. So exact rows do not open the file. |
| E6 | Provenance of the four calls | `git show 64e39bb9:joulewise/controller.py` contains all four (count 4); they are also at base lines 1944, 2504, 2507, 2904. `class PairVerdict` does not exist at `64e39bb9` (count 0). The guard's existing reason string "predates PairVerdict (64e39bb9)" is true of all four. |
| E7 | Future exposure, simulated by prepending a `battery_float` import to each module S1 round 2 or the quiet-envelope PR (S2) will touch | `calibration_bracketing.py`: 1 site (`_candidate_from_observation`). `floor_extraction.py` 4, `scripts/mint_floor_artifact.py` 1, `scripts/run_campaign.py` 11, but only if those modules import `battery_float`, which no ruled text requires. Both S2 modules: 0. Every other round-2 module: 0. |
| E8 | The two digest definitions, read | `complete_bundle_sha256` (`detection_floor.py:558`) and the tree digest (`publication_privacy.tree_sha256:356`, version `joulewise.bundle-tree.nul-v1`, used by `scripts/make_figures.py:132`) both fold the sorted inventory of every regular file: relative path, byte SHA-256, size. Same input, different serialisation. |
| E9 | The six retained RPT001 bundles on disk, hashed read-only | For all six: tree digest **equals** the pin in committed `analysis/rpt001-v2/input_manifest.json`; no `battery_float` key; backend `powermetrics`; `config.json` bytes hash to `metadata.config_sha256`; `(run_id, config_sha256)` is in `bundle_read.FROZEN_LEGACY_BUNDLE_IDENTITIES`; the head reader raises `battery_float_evidence_missing: prospective bundle`. First event timestamp of `example-mac-mlx-local__r1`: 1783396949 (2026-07-07). Complete digests: r1 `9fa8c3f0…c3a6`, r2 `c88b919c…1ecb`, r3 `a1609960…91fa`, qwen35 r1 `598b6eef…7cb1`, r2 `120953ca…fa25`, r3 `a03e253f…8af5`. **The route refusal is reproduced at the reader.** |
| E10 | What the RPT001 route publishes | `analysis/rpt001-v2/dataset.csv` is one row: `status = voided`, "no measurement from this corpus is eligible for claim use or reproduced by the rpt001-v2 route". `claims_index.jsonl` names `emit_rpt001_void_placeholders`. The route reads the six bundles and emits no number. |
| E11 | The builder (`scripts/build_battery_float_historical_bundles.py`) read, and `build()` run without writing | It rebuilds the committed bytes exactly (sha256 `6cbdd1aa…1a53`). **Every one of the 13 entries comes from a directory walk of tracked fixture bundles.** Cited digests are collected only to print them as "unresolved"; none is ever added. Files are classed by **path name** (`"detection_floor" in path`, `"analysis_manifest" in path`, `"receipt" in path`, …). |
| E12 | Structured sweep of the base tree for 64-hex values under keys naming a bundle digest (JSON walked by key; text files by line), outside `docs/process_traces/`, `docs/legacy/`, `docs/reviews/`, `docs/site/` | 66 distinct digests, **0 in the historical set**: 50 under `bundle_sha256` in `df-ph-decode-floor-mint1.json` (repository root; schema `joulewise.detection_floor_artifact.v2`; 50 distinct `bundle_id`s); 6 + 6 under `bundle_tree_sha256` in `analysis/rpt001-v2/` and `analysis/rpt001-v1/` (the v1 values differ from v2 and v1 declares no `bundle_tree_identity`); 1 `validated_bundle_sha256` in a test golden; 3 that are not bundle identities. |
| E13 | Digest `69451609…06e9` | `scripts/issue_dg071_dg075_statistics.py:89-99, 537-539`: the constant is compared with `_sha256(actual_path.read_bytes())` where the path is `…/p2015-df-ph-decode-abs-r03/power_trace.csv`. On disk, `sha256(power_trace.csv)` **equals** the constant. It is the hash of one file. The parent bundle's complete digest is `c2851728…86bf`, which **is** cited by `df-ph-decode-floor-mint1.json` and is **not** in the historical set. |
| E14 | The config-digest refusal, on copies of a real retained bundle under `/tmp` | P1 unmodified copy: `battery_float_evidence_missing: prospective bundle`. P2 `metadata.config_sha256` altered: `config.json digest does not match metadata.config_sha256`. P3 `config.json` deleted: `config.json cannot be read: …`. P4 a mutated copy whose own complete digest is added to the set by patching `bundle_read._historical_bundles`: admitted, `unobserved_historical`. P5 the same without the patch: `prospective bundle`. |
| E15 | Where the refusing fixtures get their shape | `tests/test_cli_run.py:504` and `tests/test_audit_amplification.py:147,160` write `metadata["run_id"], metadata["config_sha256"] = <a frozen legacy identity>` over a synthetic `config.json`, and already patch `bundle_read._check_config_sha256` to tolerate the mismatch. The failure index holds 19 lines carrying `config.json digest does not match metadata.config_sha256` (`grep -c`). |
| E16 | A tree digest built through the reader's authenticated hashing call | Inventory hashed with `authentication_io.sha256_authentication_input`, sizes by `lstat`, folded by `publication_privacy.tree_sha256`: equals `make_figures.bundle_tree_sha256` on the same bundle. `publication_privacy.py` does not import `bundle_read`. |
| E17 | Triage logs, by `grep` | Head: `Ran 1052 tests`, `FAILED (failures=50, errors=37, skipped=16)`. Base rerun of the failing methods: `Ran 78`, `failures=4, errors=1`; the four failures are the AXI cases (`campaign start identity unavailable`), the error is RPT001's `git ls-files` in an archive without git metadata. |

**NOT EXECUTED:** no unit-test suite (V1, V2, V3) was rerun by me; E1 and E5 exercise the guard's scanner directly, and E17 relies on the triage seat's logs. The per-test partition of class B (47 / 11 / 10) was not re-derived; I verified the mechanism and representative fixtures only. Markdown tables that cite digests without a key on the same line were not swept (E12 is a lower bound). How `docs/paper/results-fill-registry.md` pins bundles was not traced. The generator of `configs/paper_supply/supply_map.json` was not traced. The replaced type at `calibration_bracketing.py::_candidate_from_observation` was not confirmed.

## 2. Q1: the guard

### Decision: option (a), four exact rows, with three mechanical conditions

The four calls copy a run-event record and two kinds of run configuration (E3). None can hold a battery verdict, all four predate the verdict type (E6), and the only verdict in the file is bound once and read twice (E4). The guard sees them now only because the ruled controller brackets add the import (E1). Adding four exact rows states a true fact about the file; E5 shows the file stays guarded afterwards.

### Options rejected, and the ones that would evade the guard

- **(b) explicit constructors: compliant but rejected.** Rewriting `replace(config, run_id=…)` as `BenchmarkConfig(schema_version=…, model=…, …)` must enumerate 13 fields, one of them excluded from comparison (E3). Any field added to the configuration later is silently reset to its default in every repetition's config and in the cooldown sub-window. That is a defect in the measurement path bought to silence a test, and it moves production lines no ruled text asks to move.
- **Evasions (any of these is a finding, not a fix):**
  1. a file-level exemption for `joulewise/controller.py`, or a row keyed on path or function alone, or on a pattern;
  2. reaching `battery_float` through `importlib`, `__import__` or `getattr` so the scanner's import test is false;
  3. a generic helper (`def with_changes(obj, **kw): return replace(obj, **kw)`) in a module that does not import `battery_float`, called from one that does;
  4. moving the battery probes out of `controller.py` into a new module so the controller stops importing `battery_float`: it removes from the guard's view the one module where a verdict is in scope, and texts 7 and 11 place those calls in the controller.

### Amendment 36 (amends text 4 and amendment 25's guard; adds one path to S1's WRITE_SCOPE in §E)

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
- **(iii) Provenance test.** For every row of `REPLACE_CALL_ALLOWLIST` (all 13), assert the same (path, qualified name, call text) is found when the scanner is run over that path's source in `git archive 1417c0c4`, with one `battery_float` import line prepended so the scanner records sites; `skipTest` when the commit is absent from the clone, as the existing pre-seam test does. A row can therefore only ever cover a call that existed, in the same function with the same text, before S1 wrote a line.

RED/GREEN: `test_no_consumer_references_a_verdict_primitive` and `test_replace_call_allowlist_is_exact_and_only_covers_older_types` are RED at `24b79db3` (E1) and GREEN after; (i) is RED if any of the four rows is widened to a path-level exemption.

**Round 2 rule.** A module imports `battery_float` only where a ruled text requires a call into it (text 10 for `calibration_bracketing.py`; text 9 for `scored_reduce.py`). The eight text-12 consumers call `bundle_read.authenticate_window_members` and do **not** import `battery_float`. When a required import exposes a pre-existing replace call, round 2 adds its exact row under conditions (ii) and (iii), states the replaced type with the file and line that proves it, updates the count, and lists the row in its report for the refuter. E7 predicts one such row (`calibration_bracketing.py::_candidate_from_observation`); its type is NOT EXECUTED here. A replace call that fails (iii) is new code and gets no row without a cold gate.

## 3. Q2: the fixtures

### 3.1 Is the config-digest refusal what text 8 requires? Yes for the refusal, no for its label

Text 8 admits a bundle in exactly three states: (i) it carries a pair that passes; (ii) it carries no pair and its complete-bundle digest is in the historical set; (iii) it is a simulated ("MOCK") run, decided "only from the `config.json` whose digest `metadata.config_sha256` binds and only when its telemetry backend is `mock`". Everything else raises.

S1's reader (`bundle_read.py::_battery_verdict`) tries (i), then (ii), and consults the config digest only on the way to (iii). E9 and E14-P1 confirm it on real bundles: a bundle whose config digest binds but whose backend is `powermetrics` is refused as `prospective bundle`, and the digest binding is never applied to a bundle that carries a pair or is in the set. **S1 has not read a digest binding into bundles the ruling did not bind.** Every class-A and class-B fixture I examined builds a bundle with no pair, outside the set, and either a non-MOCK backend or a `config_sha256` that does not match its `config.json` (E15); text 8 refuses each of them. **The refusals are ruled behaviour, not overreach.**

One class-C defect, of labelling (**C-1**): for a bundle with no pair whose config digest does not bind, the reader raises `config.json digest does not match metadata.config_sha256` (E14-P2) or `config.json cannot be read` (P3). Text 8 rules the message for that bundle: `battery_float_evidence_missing: prospective bundle`. The S1 message names a config fault as the reason for a refusal whose reason is missing battery evidence; 19 lines of the failure index carry it (E15). It returns to S1 under its existing scope.

A second class-C defect, of enumeration (**C-2**, the builder admits only fixtures), is ruled under Q3.

### Amendment 37 (amends text 8, state (iii) and the prospective sentence; S1's existing scope)

37. **Refusal label when the config does not bind.** `BundleReader._digest_bound_mock_config` returns `False`, and never raises, when `config.json` is missing, unreadable, does not hash to `metadata.config_sha256`, or does not re-validate; it returns `True` only when the digest binds and the backend is `mock`. It records the reason in a local detail string. The reader then raises: for a bundle with **no** `battery_float` key, `BundleReadError("battery_float_evidence_missing: prospective bundle (<detail>)")`, where `(<detail>)` is omitted when the config binds and the backend is simply not `mock`; for a bundle whose key is the `not_applicable` marker, `BundleReadError("battery_float_evidence_missing: not_applicable not bound (<detail>)")`. No bundle is admitted by this change; only the text of two refusals moves. T8 gains: the E14-P2 and P3 shapes raise a message matching `^battery_float_evidence_missing: prospective bundle \(` (RED at `24b79db3`); a marker-carrying MOCK bundle with an altered `config_sha256` raises `not_applicable not bound`.

### 3.2 Scope

The suite must be green at the commit that merges S1, so the fixture work lands **in the S1 pull request, on the S1 branch**, as its own round ("round F") with its own brief and commits. It runs **after round 2's production changes**, because round 2 wires the window check into eight consumers and will add refusals in the same five test files; one pass over the union is cheaper and leaves one diff to review.

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

`tests/test_rpt001_report_slice.py` is **not** granted: its failure is the production refusal ruled in §4 and must go green with no edit once amendments 39 and 40 land; if it does not, that is a finding to return. After round 2's V3 rerun, the magistrate may add further paths **by name**, only files under `tests/`, only under the constraints below (the precedent is §E's S3 sentence). Round F edits no file outside `tests/`.

Constraints, each checked by the refuter:

- **F-1 Three remedies, no other.** (R1) A passing pair written the way production writes it: for a bundle produced by running the controller, inject `battery_runner` from `tests/battery_float_fixture.py`; for a hand-built bundle or calibration capture, the shared helper calls the real `battery_float.observe` through that runner, writes the two raw files at `raw/battery_float.<pre|post>.ioreg`, and writes event stamps that bracket them, before any manifest or evidence digest is sealed. (R2) A digest-bound MOCK config: `config.json` bytes that hash to `metadata.config_sha256` with backend `mock`. (R3) For a fixture that **models a bundle measured before the battery check** (one carrying a frozen legacy identity, or a test-mutated copy of a tracked historical fixture): the helper patches `joulewise.bundle_read._historical_bundles` to return the production set plus the fixture's own complete-bundle digest, computed after the test's last mutation (E14-P4). R3 is never used for a bundle that models a new measurement.
- **F-2 No production seam.** No production module gains a parameter, environment variable, flag or branch for tests. R3 is a `unittest.mock` patch inside the helper.
- **F-3 Nothing else is patched.** No test patches `BundleReader.metadata`, `BundleReader._battery_verdict`, `_digest_bound_mock_config`, `authenticate_window_members`, or any `battery_float.authenticate_*`. `HISTORICAL_BUNDLE_SET_SHA256` is patched only by T8's own pin test.
- **F-4 No assertion weakened.** No assertion is deleted, loosened, skipped or wrapped. Where text 8 supersedes an expectation, the test is rewritten to the ruled expectation and shown RED against `1417c0c4` behaviour and GREEN at head. The round's report lists every such test with old and new expectation and the ruled sentence that forces it.
- **F-5 Refusals are named.** A test that expects a battery refusal asserts the reason text (`prospective bundle`, `battery_float_confounded`, …), not merely that something raised.
- **F-6 The gate still bites through the fixture.** For each touched module, one counterfactual is run and reported: the helper's raw reading swapped for `tests/fixtures/battery_float/charging-synthetic-from-real.ioreg` must turn that module's R1 tests RED at the reader or the attachment.
- **F-7 Partition reported.** The report gives, per test, which remedy it took and why; the triage partition (14 class A; 47 / 11 / 10 class B) is re-derived from the post-round-2 log, not copied.

**Class D is outside round F.** The four AXI cases fail identically at base (E17) and are not S1's. The paper supply-map case is a source-hash receipt that goes stale whenever `bundle_read.py` changes; `configs/paper_supply/supply_map.json` is granted to S1 for **one final commit**, regenerated only by its committed generator after the last production change, and only if the resulting diff changes digest values of files S1 edited and nothing else; the seat pastes the generator command and the diff. (Generator NOT TRACED here; if the diff touches anything else, the seat stops and returns it.)

## 4. Q3: the six retained RPT001 bundles, and what the miss implies

### 4.1 Decision: shape (c). Admit them, by the digest the committed manifest actually names

**The science.** The six bundles were measured on 2026-07-07 (E9), eleven weeks before any battery reading was recorded. Their battery state is unobserved. `unobserved_historical` says exactly that and claims nothing more; `prospective bundle` says they are new measurements that skipped the check, which is false. A committed manifest pins each of them by a digest over its full contents, and the on-disk bytes match all six pins (E9). They are the population text 8 was written to admit; they fell out only because text 8's enumeration says "complete_bundle_sha256 values" and this manifest names the other fold of the same inventory (E8).

**What admission does not do.** It releases no number: the RPT001 route publishes void placeholders only (E10). It upgrades nothing to `pass`: the scored reducer still refuses `unobserved_historical` (text 9), post-cutoff bracketing still needs two passing endpoints (text 10), and the paper's claim renderers stay blocked on the historical-battery lane's `battery_state` column (text 19). Option (b) would keep a production route red to protect numbers that the route does not emit.

**Why not option (a) as posed.** The complete-bundle digest cannot be derived "from committed bytes": the bundle bytes are not committed (`git ls-files runs` is empty). A builder that maps tree digest to complete digest must read an untracked corpus, so the set could no longer be rebuilt from git alone, which is the property the v1.1 ruling (M4) introduced the enumeration to secure. Under shape (c) the builder copies the tree digest out of the committed manifest and the **reader** computes the tree digest of the bundle in front of it. Both folds are SHA-256 over the same inventory, so the admission is exactly as strong.

### Amendment 39 (amends text 8, state (ii) and "Set enumeration"; S1's existing scope: `bundle_read.py`, the builder, the set file, `tests/test_bundle_read.py`)

39. **Tree-digest entries.** The historical set holds entries of two kinds, distinguished by their key set:

```text
{"complete_bundle_sha256": <64 hex>, "run_id": <str>, "source": <committed path>}
{"bundle_tree_sha256": <64 hex>, "tree_identity": "joulewise.bundle-tree.nul-v1",
 "run_id": <str>, "source": <committed path>}
```

Entries are sorted by (kind, digest). The reader rejects the file on any other key set, on a `tree_identity` other than that string, or on a digest appearing twice. A tree entry is enumerated only from a committed manifest that itself declares `bundle_tree_identity == {"algorithm": "sha256", "version": "joulewise.bundle-tree.nul-v1"}`; at the S1 merge base that is `analysis/rpt001-v2/input_manifest.json`, whose six `bundle_tree_sha256` values are admitted by this ruling. `analysis/rpt001-v1/` declares no identity and uses a retired fold; its values are not enumerated.

Reader order for a bundle with **no** `battery_float` key, each step reached only if the one before did not decide:

1. compute `complete_bundle_sha256(path)` (symlinks and special files fail closed, as today); if it is a complete-kind entry, the bundle is `unobserved_historical`;
2. compute the tree digest: for every regular file, (relative POSIX path, `sha256_authentication_input`, size by `lstat`), folded by `publication_privacy.tree_sha256` imported inside the function body; if it is a tree-kind entry, the bundle is `unobserved_historical`;
3. state (iii) under amendment 37;
4. `battery_float_evidence_missing: prospective bundle`.

The verdict comes from `unobserved_historical_verdict("bundle", bundle_sha256=<the complete digest from step 1>)` in both cases, so text 9's and amendment 24's meaning of `bundle_sha256` is unchanged. `FROZEN_LEGACY_BUNDLE_IDENTITIES` still plays no part. The set's bytes and `HISTORICAL_BUNDLE_SET_SHA256` change inside S1; `battery_float.py`, `reduce.py`, `bundle.py` and S1's pin list stay byte-identical. T8 gains: a fixture bundle whose tree digest is a tree-kind entry is admitted `unobserved_historical` (RED at `24b79db3`); the same bundle with one byte appended to `power_trace.csv` is `prospective bundle`; the reader's tree digest equals `scripts/make_figures.bundle_tree_sha256` on the same directory (E16); a set file with a tree entry naming another `tree_identity` is rejected. When the controlled corpus is present, `tests/test_rpt001_report_slice.py::test_full_route_census_emits_only_void_artifacts` is GREEN unedited.

### 4.2 The miss is not confined to RPT001: the builder enumerates nothing but fixtures (C-2)

Text 8 rules the set as "exactly the `complete_bundle_sha256` values named by committed artifacts … **plus** the tracked fixture bundles". The builder implements only the second half (E11). It collects cited digests solely to print them as "unresolved", and it finds almost none because it classes files by name: the committed detection-floor artifact is `df-ph-decode-floor-mint1.json`, which contains none of the substrings it looks for. That one file names **50** complete-bundle digests of real measured bundles, none in the set (E12); E13 confirms one of them against bytes on disk. The seat's "one unresolved citation" was a symptom of the narrow search, not a measure of the corpus.

So at `24b79db3` every real pre-check bundle behind a committed floor artifact is refused as `prospective`, which is false, and the pin `6cbdd1aa…` is not final. This is a class-C defect inside S1's existing scope.

### Amendment 40 (amends text 8, "Set enumeration"; binds the builder and a sweep S1 runs before its pin is final)

40. **Enumeration by content, and the sweep.** The builder reads every tracked file at `1417c0c4` (`git ls-tree -r`) and decides by **content**, never by path name:

- JSON and JSONL are parsed and walked by key; every 64-hex string at or under a key whose name contains `bundle` and one of `sha256`, `digest`, `tree` is a **candidate**, recorded with its key name, its file, and the nearest `bundle_id` / `run_id` in the same object.
- Every other text file is scanned by line for the same key pattern, **and** Markdown tables are scanned by column header, so a digest in a table cell is attributed to its column.
- Each (key name, producing schema) pair is classified **once, by reading the code that writes it**, as one of: `complete` (written from `complete_bundle_sha256`), `tree_nul_v1`, `tree_legacy`, `file_digest`, `not_a_bundle`. The classification table is a constant in the builder; each row cites the producing `file:line`. An unclassified pair makes the builder exit non-zero.
- **Included:** `complete` and `tree_nul_v1` candidates whose source file is an artifact that pins bundles as inputs of a number (detection-floor artifacts, analysis and report input manifests, window receipts, paper-registry pins), plus the tracked fixture bundles under `tests/fixtures/` and `docs/process_traces/` as today. **Listed, not included:** candidates cited only by prose records (`docs/process_traces/`, `docs/legacy/`, `docs/reviews/`, run reports), by test goldens, or classed `tree_legacy`, `file_digest` or `not_a_bundle`. The builder writes both lists to stderr with counts per key and per file; nothing is dropped silently.
- A digest needs no bundle on disk to be included: the set is a list of citations. Where the controlled corpus is present, the seat additionally recomputes every entry it can find and reports found / not found / mismatched; a mismatch is a finding to return.

Before the pin is final the S1 seat reports: the classification table; the included count by kind and by source file; the listed-not-included table; and how `docs/paper/results-fill-registry.md` pins its inputs (if it pins an artifact by digest and that artifact is committed, the artifact's member digests are enumerated from the artifact; if the artifact is not committed, the row is listed for the historical-battery lane). From this session's lower bound (E12) the set holds **at least 69 entries**: 13 fixtures, 50 complete digests from `df-ph-decode-floor-mint1.json`, 6 tree digests from `analysis/rpt001-v2/input_manifest.json`. A final count below 69 is explained entry by entry. The refuter re-runs the builder and checks every classification row against its cited line. T8 gains: the builder's output equals the committed file; `c285172881235ef1ed0e29731c412706604e8cd182182981a5ed44cc2df986bf` (bundle `p2015-df-ph-decode-abs-r03`) is a complete-kind entry whose `source` is `df-ph-decode-floor-mint1.json` (RED at `24b79db3`).

On-disk bundles cited by no committed artifact stay `prospective` and remain the historical-battery lane's population, admitted only by cold gate, as text 8 already says.

## 5. Q4: digest `69451609…06e9`

**Listed and excluded. Not a blocker.** It is the SHA-256 of one file, `power_trace.csv`, verified against the bytes on disk (E13). It is not a bundle identity of either kind and can never match a bundle the reader hashes. The bundle that contains the file enters the set on its own citation, `c2851728…86bf` in the floor artifact (amendment 40). Text 8's enumeration listed `PINNED_BUNDLE_SHA256` among its classes on the assumption that the constant was a complete-bundle digest; it is not.

### Amendment 41 (amends text 8, "Set enumeration")

41. **`PINNED_BUNDLE_SHA256` is a file digest.** The words "`PINNED_BUNDLE_SHA256`" are struck from text 8's list of citation classes. The builder's classification table (amendment 40) carries the row `PINNED_BUNDLE_SHA256` in `scripts/issue_dg071_dg075_statistics.py` → `file_digest`, citing `:537-539`; the digest `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9` appears in the listed-not-included output with that reason. **Round 2 note:** that script reads `power_trace.csv` by path without the bundle reader, so the battery gate does not reach it; text 12's sweep (any direct read of `power_trace.csv`) must report it, and its allowlist row, if granted, is class `historical` with this amendment as the reason.

## 6. Disposition

| Item | Ruling | Owner |
|---|---|---|
| F1 guard | Option (a): four exact rows, count 13, three added tests (amendment 36) | S1, guard file added to scope |
| Class A / B refusals | Ruled behaviour under text 8; **not** overreach | — |
| C-1 refusal label | Class C; amendment 37 | S1, existing scope |
| C-2 builder enumerates only fixtures | Class C; amendment 40; pin `6cbdd1aa…` not final | S1, existing scope |
| Fixture scope | Round F in the S1 PR after round 2; 13 test files + 1 helper; constraints F-1 to F-7 (amendment 38) | S1 round F |
| Class D | AXI: not S1's. Supply-map receipt: one final regenerated commit, conditional | lead / S1 last commit |
| RPT001 six | Admitted `unobserved_historical` by committed tree digest (amendment 39) | S1, existing scope |
| `69451609…` | File digest; listed, excluded (amendment 41) | S1 builder |

**Kept intact:** custody is never a status (no amendment here converts a read failure into an admission; amendment 37 changes refusal text only); `joulewise/battery_float.py`, `joulewise/reduce.py`, `joulewise/bundle.py` and S1's pin list are untouched by every amendment; no ruled text is reinterpreted beyond amendments 36 to 41.

**Order for the lead.** (1) One S1 fix round under existing scope plus the guard file: amendments 36, 37, 39, 40, 41, ending with the enumeration report and a new pin. (2) Round 2 as briefed, with amendment 36's round-2 rule. (3) V3 rerun, then round F under amendment 38. (4) The supply-map receipt commit last.

**Flagged, not ruled (outside the charge):**
- `scripts/make_figures.py::gate_inputs` reads `raw_summary()` after strict validation; round 2's sweep will need a row for it. The route emits void placeholders (E10), so class `historical` fits, but the row is the sweep's to grant.
- The two S2 modules expose no replace site (E7), so S2 should not need the guard file; if it does, it rebases on amendment 36's count.
- 16 tests were skipped in V3; I did not check which, and a skipped test proves nothing about the gate.

## 7. Plain summary for Ed (5 lines)

1. **The guard test** (a test that scans code for ways to fake a battery verdict) is red only because the run controller now imports the battery module, which exposes four old copy-with-changes calls on run configs and event records. None can touch a verdict. Ruled: list those four exact calls, and add a test proving a faked verdict inserted into the real controller file is still caught.
2. **The 87 failing tests** are test fixtures, not a bug in the new battery gate: they build pretend runs with no battery readings, and the gate refuses them exactly as ruled. One real flaw: some refusals are mislabelled as a config-file problem. The fixtures get fixed in the same pull request, after the remaining production work, under rules that forbid weakening any check.
3. **The six old report runs** (measured 7 July, before any battery reading existed) are admitted and labelled "battery state never observed". That is the true label, their bytes match the fingerprints already committed, and the report built from them publishes no number.
4. **A larger gap surfaced:** the list of admitted old runs was built from test fixtures only. At least 50 real runs named by a committed detection-floor file (the file recording the smallest energy difference the instrument can resolve) were left off and would have been refused as if new. The list must be rebuilt by reading file contents, not file names, before it is frozen.
5. **The unresolved fingerprint** is the hash of a single power-trace file, not of a run; it is recorded as excluded, and the run that contains the file gets onto the list through the detection-floor file.
